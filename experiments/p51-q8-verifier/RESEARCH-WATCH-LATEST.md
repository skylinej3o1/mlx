# Project 51 primary-lane research watch — 2026-09-23 15:03 ET

**Freshness boundary checked:** prior hard boundary **2026-09-23 16:30:12 UTC**. This pass covers substantive evidence through the user cutoff **2026-09-23 19:03:50 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No new exact 2x M1 Max / TB4 Flash-Next throughput receipt appeared, and no new DASLab / GSQ-RCO xhigh behavioral result appeared.

The most useful new evidence is about where the remaining risk actually sits:

1. A new Metal report shows potentially catastrophic long-context multi-sequence batching behavior on an M3 Ultra, including a case where two separate singleton processes substantially outperform one batched process. The report is **provisional**: it uses an older prebuilt, Qwen4Exp is not upstream-supported in that llama.cpp build, and the maintainer explicitly says the custom script does not account for some effects correctly. Still, it creates a mandatory P51 gate: verify-width B2/B4/B8 must be benchmarked at long context on Apple7 before PP2 overlap gets forecast credit.
2. SGLang #40947 makes Flash-Next PLE lookup substantially cheaper at the microkernel level by sharing one host table across TP ranks, but end-to-end throughput is effectively neutral. This is valuable negative evidence: PLE lookup collectives can look expensive in isolation without being a material system bottleneck.
3. vLLM #58413 demonstrates exact hybrid-state offload/replay on Qwen3.8-27B + MTP3 at 100K: external adoption rises **0 -> 99,008 tokens**, TTFT falls from about **11.7-12.3 s to 377 ms**, greedy continuation is byte-identical, and MTP accept length remains **2.601**. Correct per-group state geometry can make warm external restore work extremely well.
4. vLLM #58428 turns the KV-PP RFC into a concrete Phase-1 planning prototype: physical layer ownership is decoupled from logical KV planning, draft state stays rank-local, and PP4 unit tests report ~3.2x block-capacity expansion. Runtime communication is still unimplemented, so this is architecture evidence only.
5. A Blackwell Qwen3.8 hybrid/MTP report (#58422) shows a silent engine wedge with health still returning 200. Backend-specific, but operationally important: P51 liveness must include token-progress probes, not only process/HTTP health.
6. A CUDA Qwen4Exp report (#29326) claims ~20% long-context PP gain through a radix top-k path for the QSA indexer. It is not Apple evidence and is not yet a merged/controlled upstream result, but reinforces that indexer top-k remains a legitimate prefill optimization seam.

### Planning interpretation carried forward

The first-principles forecast completed after the previous watch is now the canonical interpretation of the unchanged 40/400 target:

- measured modern single-M1 4.27-bpw target-only anchor implies roughly **~22-23 TG around 128K**;
- if a source-like ~3.4-3.6-bpw P51 quant maps efficiently to Apple7, a reasonable design estimate is **~25-27 TG target-only**;
- therefore **40 TG requires ~1.48-1.60x effective speculative/distributed uplift**, materially less heroic than the old Q5-ish design;
- **physical fallback if speculation/PP2 contributes almost nothing:** ~24-27 TG;
- **practical mature-system downside with at least modest speculation:** ~30-32 TG;
- **current central planning region:** ~39-41 TG;
- **headline target:** 40 TG;
- **stretch:** 50 TG;
- cold-PP derived center remains roughly **370-390**, downside **320-340**, with **400** the success target.

These are derived engineering scenarios, not new measurements. They do **not** change the existing ~70% planning confidence for >=40 TG.

---

## NEW / PROVISIONAL — llama.cpp #29335: Metal long-context batched decode can collapse badly

Source:
https://github.com/ggml-org/llama.cpp/issues/29335

Created **2026-09-23 17:56:40 UTC**.

Reported hardware/runtime:
- Apple M3 Ultra, 512 GB;
- Unsloth prebuilt llama.cpp b10830, not current master;
- Qwen3.8-Flash-Next Q8_0;
- several unique long-context requests decoding inside one server batch.

Reported aggregate decode:

| Context | N=1 | N=2 | N=4 | N=8 |
|---:|---:|---:|---:|---:|
| 256 | 32.8 | 45 | 60 | 78 |
| 16K | 25.9 | 10.3 | 6.9 | 5.2 |
| 32K | 25.7 | 8.6 | 5.5 | — |

At 32K:
- one process, N=1: **25.7 TG**;
- one process, N=2 batch: **8.6 aggregate TG**;
- two independent N=1 processes: **39.4 aggregate TG**.

The reporter says the same qualitative cliff appears on GLM-5.3-Flash, suggesting a Metal batched-attention path rather than a Qwen-only issue.

### Critical qualification

The llama.cpp maintainer replied that:
- the custom script does not account for some effects correctly and can report incorrect numbers;
- `llama-batched-bench` should be used;
- these model architectures are not currently upstream-supported in llama.cpp.

Therefore the exact ratios are **not promoted as reliable measurements**.

### P51 consequence

The mechanism risk is still important because P51 depends on multi-row speculative verification and PP2 overlap.

Add an Apple7 verifier-width gate before any PP2 throughput projection is trusted:

- B1, B2, B4, B8 at 4K / 32K / 128K;
- same shared-prefix verification geometry used by the real MTP path;
- target-only and verify path separately;
- Metal GPU occupancy and per-stage idle%;
- one process batched vs multiple singleton-process control;
- same exact quant/kernel policy.

If long-context B2/B4 is slower than repeated B1 on M1, PP2 scheduling must avoid the pathological batching path or use a different kernel/row layout.

**Target effect:** none until reproduced on supported current code and P51's actual shared-prefix verify geometry.

---

## NEW / NEGATIVE SYSTEM EVIDENCE — SGLang #40947: faster PLE gather, neutral end-to-end performance

Source:
https://github.com/sgl-project/sglang/pull/40947

Created **2026-09-23 17:18:35 UTC**.

The PR adds an opt-in shared host-table backend for Qwen3.8-Flash-Next PLE offload:
- one complete ~47.68-GiB anonymous host table is shared by all TP ranks;
- each rank directly gathers its needed rows;
- the normal PLE lookup all-reduce is removed;
- checkpoint loaders still see rank-local partition views.

Accuracy:
- 370 tests passed, 4 skipped;
- 2,048 frozen-input logprobs exactly match baseline at TP1 and TP4;
- GSM8K results within run noise;
- all TP4 schedulers map the same inode/table.

Micro-level:
- shared PLE gather: **~2.2-3.6 µs**;
- repeated baseline capture: **~11.2 µs**;
- TP4 decode removes one collective per step: **98 -> 97 kernels**.

End-to-end:
- TP4 C1 decode: **107.200 -> 107.383 output TG (+0.17%)**;
- TP4 prefill-heavy: **211.621 -> 211.064 output TG (-0.26%)**;
- TP1 effectively unchanged;
- TP4 weight-load stages rise roughly **32 s -> 69 s**;
- KV capacity decreases ~0.098%.

### P51 consequence

This is strong negative evidence against prioritizing PLE lookup-collective elimination solely because the microkernel/collective looks expensive.

For P51:
- continue treating PLE as a placement/offload/correctness problem first;
- profile PLE in whole-server target and verify traces before spending engineering effort;
- do not translate a 3-5x gather microbenchmark improvement into TG/PP forecast credit.

The more important long-context seams remain verifier GDN/MoE cost, QSA/indexer geometry, Apple7 kernel dispatch, and PP2 occupancy.

---

## NEW — vLLM #58413: exact 100K hybrid-state offload restore with MTP

Source:
https://github.com/vllm-project/vllm/pull/58413

Created **2026-09-23 17:10:21 UTC**.

Affected topology:
- Qwen3.8-27B hybrid GDN;
- MTP3;
- `mamba_cache_mode=align`;
- external CPU/filesystem KV tiering;
- 8x H200 test deployment.

Before the fix, MTP shifted recurrent handoff boundaries onto a hash boundary that was not the global offload chunk boundary. The connector dropped the recurrent state, so every-group matching failed and external adoption was **zero**.

The fix gives align-mode recurrent groups their own hash-block-granular offload geometry rather than forcing the global full-attention chunk geometry.

100K end-to-end receipt:
- external adopted tokens: **0 -> 99,008**;
- recurrent state files: 0 -> 1/1/1;
- CPU->GPU load: **7.05 GB**;
- cold TTFT: **11.7-12.3 s**;
- CPU-tier warm TTFT: **377 ms**;
- filesystem-tier replay after reset: **375 ms**;
- roughly **31x** improvement versus the broken full-recompute path;
- cold full compute vs 99,008-token restored replay: **byte-identical 128-token greedy continuation**;
- MTP accept length: **2.601 vs 2.601**;
- non-MTP control still adopts 99,840 tokens.

### P51 consequence

This is strong exact-family transfer evidence for the warm-agent design:

- recurrent/QSA/full-attention state groups may require **different checkpoint/block geometry**;
- external persistence is viable if every group's semantic boundary is preserved;
- a shared global chunk size is not a sufficient cache identity;
- warm restore should be certified by actual adopted-token count + continuation parity + unchanged speculative acceptance.

It does not change cold PP or sustained TG targets, but materially de-risks the long-session sleep/wake objective.

---

## NEW — vLLM #58428: KV-PP planning prototype makes layer ownership explicit

Source:
https://github.com/vllm-project/vllm/pull/58428

Created **2026-09-23 18:44:28 UTC**.

This is Phase 1 of the earlier KV-PP / LayerSplit RFC.

Implemented:
- explicit `kv_pipeline_parallel_size`;
- immutable placement plan;
- contiguous balanced target-layer ownership by rank;
- **draft/EAGLE/MTP groups remain rank-local on every rank**;
- physical KV tensors are allocated only for owned target layers + local draft layers;
- scheduler retains a common logical block footprint;
- scratch budget = **2 x maximum target-layer bundle size** for future double-buffered transfers.

Unit-test example:
- PP4 planning yields about **~3.2x block-capacity expansion** after scratch reservation.

### Qualification

Runtime execution and communication are **not implemented yet**. There is no throughput receipt.

### P51 consequence

This converges strongly with our state-ownership design:
- target state belongs to the stage/layer owner;
- speculative/draft state can intentionally remain local/replicated;
- scheduler-visible logical cache identity can be decoupled from physical ownership;
- transfer scratch must be budgeted explicitly.

No TG/PP credit until Phase 2 provides runtime measurements.

---

## NEW / BACKEND-SPECIFIC — vLLM #58422 silent Qwen3.8 hybrid/MTP engine wedge

Source:
https://github.com/vllm-project/vllm/issues/58422

Created **2026-09-23 18:09:14 UTC**.

Reported configuration:
- Qwen3.8-27B hybrid GDN MoE;
- TP1;
- MTP4;
- NVFP4 KV;
- FlashInfer;
- RTX PRO 6000 Blackwell / SM120.

Failure signature:
- ~10 simultaneous requests;
- generation-token counter remains flat >60 s;
- requests remain "running";
- GPU utilization reports 100% but power is near idle;
- `/health` remains 200;
- no error/traceback;
- no self-recovery; restart required.

The same deployment also had separate illegal-memory-access crashes, so this is a backend/runtime instability report rather than evidence against the architecture.

### P51 consequence

Operational rule:
- HTTP/process health is insufficient for a long-running local agent server;
- add a **progress watchdog** keyed to generated-token/forward counters when requests are active;
- preserve a controlled restart/reload path that restores validated warm state.

No Apple7 performance implication.

---

## NEW / WEAK TRANSFER — llama.cpp #29326: QSA top-k radix path reportedly adds ~20% CUDA PP

Source:
https://github.com/ggml-org/llama.cpp/issues/29326

Created **2026-09-23 16:55:33 UTC**.

The report says the CUDA Qwen4Exp path was not compiling/dispatching the parallel radix top-k implementation used by the indexer. Enabling radix top-k for sufficiently wide/multi-row shapes reportedly improves Qwen3.8-Flash-Next prompt processing by about **20%**, with gains holding through ~148K context.

Qualification:
- Windows / SM75;
- user issue, not a controlled merged PR;
- no Apple measurement;
- no detailed A/B table in the issue.

### P51 consequence

This is weak but directionally consistent evidence that **QSA/indexer top-k can still be a meaningful prefill bottleneck**.

Keep top-k/indexer profiling in the cold-PP workstream, but do not transfer 20% to M1 or change the 400-PP target.

---

## Community / Hugging Face delta

Fresh searches after the hard boundary for:
- DASLab / GSQ-RCO xhigh evidence;
- new Flash-Next low-bit quality comparisons;
- new M1/M2/M3/M5 long-context Flash receipts;
- new 128K MTP/DFlash measurements.

No qualifying post-boundary community/HF result was found. Search results were older threads/releases already covered by Project 51.

No new DASLab GitHub commit/PR/issue appeared in-window.

---

## Checked with no qualifying fresh target evidence

- **DASLab GSQ/RCO:** no new commit/PR/issue or xhigh behavioral receipt in-window.
- **MTPLX:** no new commit/PR/issue.
- **EXL3:** no new commit/PR/issue.
- **PonyExl3:** no new commit/PR/issue.
- **mlx-serve:** no P51-relevant performance change; one UI-streaming issue only.
- **Splash:** no P51-relevant performance/correctness delta.
- **official Qwen3.8 repo:** no new commit/PR/issue.
- **MiaAI-Lab dual-DGX-Spark Flash:** no new delta.
- **flashnext-hybrid:** no new delta.
- **Weschera single-DGX-Spark Flash:** no new delta.
- **DS4:** no new qualifying performance/correctness receipt.
- no new exact **2x M1 Max/TB4 Flash-Next** TG or cold-PP receipt.
- no new exact **RTX 5070 Ti** result strong enough to move its target.

## Target / confidence impact

Numeric targets unchanged:

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

**2026-09-23 19:03:50 UTC**
