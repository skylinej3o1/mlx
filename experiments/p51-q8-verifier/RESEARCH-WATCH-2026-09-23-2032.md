# Project 51 primary-lane research watch — 2026-09-23 20:32 ET

**Freshness boundary checked:** prior hard boundary **2026-09-23 20:42:43 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 00:32:47 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No new exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared. No new DASLab / GSQ-RCO xhigh behavioral-quality result appeared.

The strongest fresh evidence is:

1. an independent second Strix-Halo validation of the same Qwen3.8-Flash-Next Q4 runtime, including deterministic logits, session recovery, tool use, official quality scores and a measured MTP uplift from ~20.6 TG target-only to ~29.4 TG on the coding workload;
2. a concrete DFlash/NIXL bug and fix showing that target and draft KV transfer geometry must be computed per region, not inherited from the target model's global attention topology;
3. real-weight speculative-verification-front sharding data showing a small but repeatable gain at some concurrency/quant combinations rather than a universal multiplier;
4. Apple/Metal evidence that dispatch/fusion economics are strongly hardware-topology dependent and that verify-width resource qualification must include threadgroup-memory safety.

These improve mechanism confidence and implementation specificity. They do not move the 40/400 forecast.

## Findings

### UPDATE / independent exact-family validation — DS4 #1070, Qwen3.8-Flash-Next on Strix Halo

Source: https://github.com/antirez/ds4/pull/1070  
Fresh independent validation comment: 2026-09-23 21:06:56 UTC.

A second user independently reproduced the Qwen3.8-Flash-Next **Q4** path on a separate Ryzen AI Max+ 395 / Radeon 8060S Strix Halo, 128 GB unified memory, ROCm 10 / HIP 7.15.

Configuration:
- Qwen3.8-Flash-Next-Q4.gguf;
- resident model weights ~69.73 GB;
- n-grams disk-only;
- CPU governor performance, GPU perf level high.

Independent correctness:
- isolated Qwen4 ROCm kernels: PASS;
- production full-output oracle across Q2/Q4 and T=33/2049/8193: PASS 6/6;
- n-gram tests: PASS;
- injected disk-read failure recovery across prefill/decode/MTP: exact recovery;
- repeated 8K prefill frontier logits: **0 / 248,320 differing logits** across every repeat pairing;
- repeated greedy server requests: byte-identical;
- session checkpoint/restore/rewind/resample: PASS;
- native tool-call round trip: correct arguments and final answer.

Independent Q4 quality references essentially reproduced the PR's own official continuation scores:
- Short/default NLL **0.290386**, API top-1 **92.08%**;
- Short/quality NLL **0.290357**, API top-1 **92.06%**;
- Long/default NLL **0.124453**, API top-1 **97.13%**;
- Long/quality NLL **0.125177**, API top-1 **97.52%**.

Independent speed:
- prefill @8192: **580.26 tok/s** vs PR 579;
- ordinary decode @2048: **20.59 tok/s** vs PR 20.2;
- MTP coding test: **29.35 tok/s** vs PR 29.8.

That coding-test MTP arm is about **1.43x** the independent target-only decode rate, but it is a workload-specific rate rather than a 128K steady-state multiplier. The same reporter measured meaningfully lower rates under default Ubuntu power settings, so power/governor state belongs in benchmark identity.

**Classification:** UPDATE / strong exact-model-family, cross-hardware transfer evidence.

**P51 consequence:** this materially strengthens confidence that the Flash-Next runtime mechanisms, disk-backed n-grams, recurrent state, restoration and native MTP can coexist correctly on another unified-memory consumer system. The MTP uplift is directionally supportive of the speculative thesis, but it is short-context/AMD and must not be transferred numerically to M1 @128K.

**Target impact:** none.

### NEW — vLLM #58470 / #58471: DFlash KV transfer geometry must be per-region, not inherited from an MLA target

Sources:
- https://github.com/vllm-project/vllm/issues/58470
- https://github.com/vllm-project/vllm/pull/58471

Exact reported deployment:
- target GLM-5.3 MLA FP8;
- draft DFlash2, GQA with 8 KV heads, k=4;
- prefill attention TP1 feeding decode TP8;
- 2 x 8 H200, NIXL over UCX/InfiniBand.

The target's model-wide MLA transfer mapping treats KV as replicated. That is correct for the MLA target but wrong for the GQA draft, whose KV is head-sharded across decode TP ranks.

On main:
- correct draft geometry is rejected by handshake;
- if only the size check is relaxed, every decode rank reads draft head 0;
- target output can still remain correct because the target verifies drafted tokens, but draft acceptance falls because 7/8 ranks attend to the wrong draft head.

The fix creates a separate draft TP mapping from the draft's own KV-head count and applies it only to draft SPLIT regions.

End-to-end, P TP1 -> D TP8:
- NIXL transferred phase: **accept length 3.221**, accept rate **0.555**;
- local-prefill ground truth: **3.253**, accept rate **0.563**;
- difference in accept length: ~1%;
- external prefix-cache hit rate: 100% steady-state;
- failed transfers: 0.

Per-position acceptance over NIXL was 0.792 / 0.606 / 0.467 / 0.356 for positions 0-3.

**Classification:** NEW exact speculative-state transport evidence, non-P51 hardware/model.

**P51 consequence:** transfer/cache ownership must be keyed by **state region identity**, not merely by the target model's global topology. Under PP2 or any future disaggregated P51 path, target KV/QSA/GDN/MTP/draft state may have different sharding or replication semantics. A single model-wide mapping is unsafe.

Also note the diagnostic trap: target output can look fine while draft state is wrong because verification masks the correctness failure as an **acceptance-performance regression**. P51 validation must therefore inspect acceptance by position and state geometry, not final text alone.

### UPDATE — SGLang #40820: real-weight sharding of the speculative verification front gives small, shape-dependent gains

Source: https://github.com/sgl-project/sglang/pull/40820  
Fresh substantive commit: d8e6c4b97abe at 2026-09-23 21:38:39 UTC.

The PR shards Kimi-K3's latent down-projection at the **speculative verification front** across TP8 instead of recomputing the full projection on every rank. Each request verifies eight token positions per step; two requests verify sixteen.

Real-weight B300 TP8/DCP8, 61,440 input / 1,024 output tokens, 95% prefix-cache hits, simulated acceptance fixed at 5.5:

| checkpoint | conc | baseline | candidate | change |
|---|---:|---:|---:|---:|
| NVFP4 | 1 | 343.42 | 348.59 | **+1.51%** |
| NVFP4 | 2 | 571.52 | 588.97 | **+3.05%** |
| MXFP4 | 1 | 379.64 | 379.22 | **-0.11%** |
| MXFP4 | 2 | 622.58 | 627.80 | **+0.84%** |

The authors explicitly call MXFP4 inconclusive; run-to-run/acceptance variation is of the same order as the apparent gain.

**Classification:** UPDATE / cross-hardware verifier-front mechanism evidence.

**P51 consequence:** distributing/sharding work specifically at the verifier front is viable, but the gain is workload-, concurrency- and kernel-stack-dependent. Do not treat "move verifier work across ranks/stages" as an automatic large multiplier. Instrument each front component and require real-weight A/Bs.

### UPDATE — SGLang #40961: eliminating one verify-side scatter is a few-percent win at low concurrency

Source: https://github.com/sgl-project/sglang/pull/40961

The PR fuses DSV4 target-verify SWA cache writes into the existing QK norm/RoPE kernel and removes the standalone scatter launch.

8K/1K workload:
- C1 total throughput: **2977.08 -> 3075.55 tok/s (+3.31%)**;
- C4: **7546.37 -> 7738.55 (+2.55%)**;
- C16: **14234.90 -> 14331.06 (+0.68%)**.

Median TPOT/ITL also improve modestly.

**Classification:** UPDATE / verifier-dispatch transfer evidence.

**P51 consequence:** supports the current strategy of deleting standalone verifier launches and folding state writes into already-paid kernels. It also shows the expected diminishing system gain as other work dominates.

### NEW — mlx-serve #514: Apple dispatch price and fusion payoff are topology-specific

Source: https://github.com/ddalcu/mlx-serve/issues/514

On an M5 Ultra 256 GB / Flash-Next mixed 4/8-bit setup, a dependent dispatch probe estimates approximately **3.1 us per chained dispatch**, versus ~1.5-1.7 us previously measured on M4 Max.

Baseline forward:
- **13.42 ms / forward**;
- ~4,243 MLX ops;
- ~75 tok/s forward-only, ~79 tok/s through server.

Disabling selected fusions:
- HC fused off: **+2.57 ms (+19%)**;
- MoE gate/up fused off: **+1.47 ms (+11%)**;
- router fused off: **+0.73 ms (+5%)**;
- MoE down/reduce fused off: **+0.73 ms (+5%)**;
- GDN decode fused off: **+0.69 ms (+5%)**.

A follow-up source build estimates ~1,430 actual kernels/token and ~99 command buffers/forward, with the GPU 99.3% busy; the cost is not simply a host-idle bubble.

Raw-Metal dependent-dispatch floor:
- M5 Max serial encoder: ~0.81 us;
- M5 Ultra: ~1.48 us;
- concurrent + buffer barrier: ~1.10 vs ~1.80 us.

A persistent cross-grid barrier experiment works cheaply on M5 Max but becomes either incorrect or slower than a launch on M5 Ultra at larger threadgroup counts; the reporter suspects cross-die behavior but does not prove the cause.

**Classification:** NEW Apple transfer evidence, stronger-chip/multi-die, not M1.

**P51 consequence:** fusion remains high leverage, but dispatch/barrier economics are hardware-topology identity. Benchmark Apple7 directly. Do not assume a persistent-megakernel/barrier strategy that works on one Apple topology will scale to another.

### NEW — llama.cpp #29340: Metal verify/batch width can cross threadgroup-memory limits under quantized KV

Source: https://github.com/ggml-org/llama.cpp/pull/29340

Quantized FlashAttention with head sizes 512/512 or 576/512 and batches 20-31 can exceed the 32-KiB Metal threadgroup-memory limit. The concrete Q8_0, DK/DV 576/512, batch 24 case required **37,888 bytes**, causing a Metal validation abort.

The fix dequantizes KV to F16 before the non-vector kernel for those shapes, reducing threadgroup memory to **29,696 bytes**. Added regression cases fail without the fix and pass with validation; the full FA suite passes 4,956/4,956.

**Classification:** NEW Apple correctness/resource evidence; not a known Flash-Next head shape receipt.

**P51 consequence:** verify width is part of kernel-resource certification. B1/B2/B4/B8 is not sufficient as a universal shape list if later verifier designs use wider packed rows; every promoted kernel policy must check actual threadgroup-memory occupancy at all verify widths and KV formats.

### NEW / operational — oMLX #3883: recurrent sidecars can dominate persistent-cache bytes and evade generic cleanup

Source: https://github.com/jundot/omlx/issues/3883

On Qwen3.8-27B-oQ4e-fp16-mtp:
- total cache on disk: **28.60 GiB**;
- normal hex KV files: ~9.24 GB;
- GDN sidecars: **19.36 GB**.

The unloaded-model dashboard counted only the 9.2-GB hex KV portion, and the generic manual clear path left the 19.36-GB GDN sidecars behind.

**Classification:** NEW operational state-management evidence.

**P51 consequence:** strengthens the byte-budget rule: cache observability, eviction, purge, migration and sleep/wake tooling must enumerate every state class explicitly, including recurrent/GDN sidecars. "KV cache size" is not a complete storage metric.

### UPDATE / merged transfer evidence — SGLang #40794: DFlash support on Kimi-K3

Source: https://github.com/sgl-project/sglang/pull/40794  
Merged commit: 208f6f7501f7 at 2026-09-23 22:58:39 UTC.

On 8xB300 per role, K3 PD 1P1D, TP8/TP8, DFlash block size 8:
- GSM8K 5-shot: **95.7%**;
- average accept length: **4.99**;
- acceptance rate: **57%**.

This primarily demonstrates that the DFlash hidden-state capture contract can transfer to another architecture and that a public draft can be integrated cleanly. It is not Flash-Next/Apple evidence and DFlash pipeline parallelism remains unsupported in that implementation.

**P51 consequence:** useful supporting evidence for keeping external-draft speculation as a real branch, not a replacement for the native-MTP baseline.

## Checked surfaces / negative results

- **IST-DASLab/GSQ:** no issues, PRs or commits in-window.
- **oMLX:** no in-window performance commit for Flash-Next; #3883 is the relevant recurrent-sidecar operational finding.
- **mlx-serve:** no new PR/commit; #514 is the relevant new Apple runtime measurement.
- **llama.cpp:** no new exact M1 Flash-Next throughput receipt. #29340 is the relevant Metal resource/correctness item; merged #29339 only extends vision-target conversion for DFlash/DSpark.
- **vLLM:** many generic CI/frontend/ROCm changes were screened. #58470/#58471 is the material speculative-state transport result.
- **SGLang:** extensive activity screened; #40820, #40961 and merged #40794 are the material verifier/speculation items.
- **Community/Hugging Face/Reddit:** fresh search did not surface a controlled post-boundary source-vs-quant xhigh behavioral receipt or exact M1/TB4 Flash-Next throughput result. Older Reddit/HF threads remain useful context but are not new evidence for this window.

## Canonical planning state after this pass

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**, conditional on at least modest speculation benefit.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG**.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 00:32:47 UTC**
