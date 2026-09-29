# Project 51 primary-lane research watch — 2026-09-29 02:21 ET

**Freshness boundary entering this pass:** **2026-09-29 02:19:04 UTC**.  
**User cutoff:** **2026-09-29 06:21:54 UTC**.

## Decision

**Durable STATE update; no TARGETS change.**

This pass materially strengthens:
- Flash-Next mixed-precision protected-island allocation;
- heterogeneous stage-local layer parallelism;
- Swift 1.5 effective solved-task throughput;
- long-context/concurrent Flash capability;
- phase-specific collective and speculative-metadata reuse rules.

It does **not** provide a reproducible new exact 2x-M1-Max/TB4 Flash receipt, an exact-user-5070Ti Strata ladder, or direct source-paired Flash IQ3_S long-context quality evidence. Canonical physical TG/PP targets remain unchanged.

## Strict-window findings

### NEW — deferred vLLM delayed-mHC seam fusion

Source: https://github.com/vllm-project/vllm/commit/0af34418e99b972029b53130c9a9665b4e692536  
Timestamp: **2026-09-29 02:19:10 UTC**.

This landed six seconds after the prior cutoff and therefore belongs to this pass. On ROCm/gfx950 DSv4.1, vLLM routes a delayed hyperconnection seam through a fused post/pre/RMSNorm AITER path with explicit numerical tests across token counts and seam variants.

P51 interpretation:
- another independent example that HC/recurrent seam fusion can remove dependent operations while preserving a bounded numerical contract;
- cross-model/hardware only, no numerical transfer to Apple7.

### NEW — mlx-serve Flash-Next `mid48` protected-island A/B

Source: https://github.com/ddalcu/mlx-serve/commit/65b9c2e0be4ca3ccbdbb5b186d6e5992681c4a14  
Timestamp: **2026-09-29 03:18:26 UTC**.

M5 Ultra / 256 GB / `--mtp --mtp-typical 0.2`.

The repack keeps 8-bit only on:
- lm_head / embeddings;
- hyper-connections;
- router gate;
- GDN in_proj_a / in_proj_b;
- attention k/v;
- indexer;
- PLE;
- MTP head.

It moves other non-expert q/o/GDN-body/shared-expert projections from 8 -> 4 bit. Pack size **75.30 -> 73.86 GB**.

Measured:
- S=1 forward **-11.2%**;
- S=4 verify forward **-4.9%**;
- MMLU-Pro-400: **346** vs 340 / 338 control repeats;
- 4-stream decode: **39.0 TG/request** vs 39.1 / 38.9 controls — effectively no E2E gain.

Reason for missing E2E gain: joined verify kernels accept 8-bit weights only, so mid48's new 4-bit projections fall back to per-request verification. A 4-bit verifyQMM probe gained ~4.8% at four streams but was not bit-exact and was not promoted.

Critical all-4-bit control:
- S=1 forward **-14.7%**;
- **12.8% more output tokens**;
- 7 answers hit the 8,192-token cap.

P51 consequence:
- protect HC/router/recurrent-control/indexer/PLE/MTP islands;
- quant allocation and verifier-kernel support are one optimization problem;
- do not interpret short-benchmark parity as unchanged reasoning-token behavior.

### NEW — Strata 0.1.21 heterogeneous layer split

Sources:
- https://github.com/Niko1221/Strata/commit/f1b1d961537fd66d37fee68a60015701375b7b5a
- https://github.com/Niko1221/Strata/blob/main/docs/MULTI_GPU.md
- https://github.com/Niko1221/Strata/blob/main/bench/results/2026-09-29-layer-split/README.md

Release timestamp: **2026-09-29 04:14:43 UTC**.

Physical rig:
- Ryzen 9 9950X3D / 62 GB / Windows 11;
- RTX 5080 16 GB x16;
- RTX 3090 24 GB on x4 Gen4 (~6 GB/s);
- Coder GSQ-RCO IQ1_M, 32K, int8 KV, spec4.

Best 5080+3090 K=26:
- **2,039 PP @16K**
- **2,357 PP @28K**
- **83.8 TG story**
- **109.7 TG code**

0.1.20 5080-alone control:
- 2,045 / 2,005 PP;
- 83.2 / 88.2 TG.

The split pipeline therefore improves the 28K prompt substantially and keeps story decode level while improving code decode. A slower third 2080 Ti makes decode worse.

Correctness:
- one-GPU branch vs 0.1.20: **10/10 byte-identical**;
- same-GPU split hand-off: **10/10 byte-identical**;
- cross-GPU expert execution can round differently;
- all tested needles found and multi-stage conversation checkpoint reuse works.

P51 consequence:
- stage-local expert/state residency plus one handoff per verify window can work over weak links;
- once hot-expert residency saturates, **per-stage compute balance dominates**;
- a slow stage should not be added merely for capacity.

No transfer of the 18-20% prompt gain to M1/TB4.

### NEW — oMLX MiMo long-context attention stack (cross-model)

Sources:
- https://github.com/jundot/omlx/commit/3cd1c0ca62000328d7eca7663f67216ac525519f
- https://github.com/jundot/omlx/commit/07d88dbd4c3c000843f741d82314eb53b637bcac

Timestamps: **05:33:42 / 05:34:29 UTC**.

M5 Ultra / MiMo-V2.6-Flash:
- prefill chunk widening plus fused attention raises long-prompt PP;
- split-key long-context decode attention changes E2E decode:
  - 8K **108.6 -> 111.7 TG**
  - 64K **73.9 -> 88.4 TG**
  - 256K **40.2 -> 69.0 TG**

P51 interpretation:
- reinforces the existing rule that long-context attention/verify rows need a dedicated plan;
- cross-model/M5 evidence only.

### NEW — vLLM fused multi-step draft metadata reuse

Source: https://github.com/vllm-project/vllm/commit/35d6fb3187d0a5a70c43ee5b0c3e923a7cb96226  
Timestamp: **2026-09-29 06:06:47 UTC**.

FlashInfer TRTLLM-gen fused draft steps reuse the step-1 decode metadata while sequence lengths advance in place and block tables stay fixed.

P51 rule:
- speculative metadata can remain persistent inside a verify cycle where its invariants are explicit;
- do not mechanically rebuild unchanged decode/block metadata every draft step.

No direct target-hardware speed receipt.

### NEW — SGLang phase-specific PCIe-IPC all-reduce

Source: https://github.com/sgl-project/sglang/commit/c7be3e935b5034006cd6ae7977b41e2459b4126c  
Timestamp: **2026-09-29 06:08:44 UTC**.

On one switch-free 8x sm120 PCIe host, hidden 6144 bf16, FlashInfer PCIe-IPC beats NCCL dramatically for small/decode reductions. In TP8 at 8K:

| transport/workspace | TTFT | TPOT | output TG |
|---|---:|---:|---:|
| NCCL only | 1910 ms | 21.14 ms | 35.02 |
| PCIe-IPC, prefill-sized | 3176 ms | 13.64 ms | 38.43 |
| PCIe-IPC, decode-sized | **1849 ms** | **13.62 ms** | **48.05** |

At 128K/C4, prefill-sized workspace regressed TPOT by ~45%; limiting the optimized workspace to decode-sized rows removed that regression.

P51 rule:
- communication kernel/workspace selection is **phase + row-shape specific**;
- never size a decode collective path from the largest prefill geometry just because it can run it.

### OUTSIDE CUTOFF — vLLM Rust-frontend commit

vLLM `e05095c9` landed at **2026-09-29 06:23:54 UTC**, two minutes after the user cutoff. It is intentionally deferred to the next pass.

## SAME-DAY CURRENT — exact-chip M1 Max ~27-TG lead

Source: https://www.reddit.com/r/LocalLLaMA/comments/1wrqql8/qwen38flashnext_125b_at_1215_toks_on_a_2021_32gb/

A user in the MoEspresso thread reports progressing from ~7.5 TG to ~14 TG and then to **~27 TG on an M1 Max 32-core**, saying the final step required a kernel rewrite and effectively became a fork.

This is potentially very important because the chip class is exact, but it is **not yet a reproducible receipt**:
- fork not published;
- context depth unspecified;
- MTP/speculation settings unspecified;
- no acceptance/PP/command/config identity;
- no repeatable benchmark denominator.

P51 consequence: high-priority follow-up only. Do not move single-M1 Flash or dual-M1 40-TG confidence yet.

## SAME-DAY CURRENT — 4x R9700 high-concurrency Flash receipt

Source: https://www.reddit.com/r/LocalLLaMA/comments/1wsxgbo/first_few_days_of_qwen38flashnext_on_4x_r9700_its/

The current deployment reports:
- **150+ TG** single stream;
- **~100 TG each** with 3-5 concurrent streams;
- **10K+ PP**;
- ~7.8 GB total KV allocation, said to support roughly four 262,144-token sessions;
- ~31.5/32 GB used on each GPU.

Model: tcclaviger Qwen3.8-Flash-Next MXFP4/FP8 with PLE/ngram offload.

P51 interpretation:
- strong evidence for Flash-Next's aggregate multi-agent ceiling and relatively cheap sparse long-context state;
- not numerically transferable to M1/TB4 or one 5070 Ti.

## RECOVERED CURRENT — Swift 1.5 + HyperQwen ~630-task task-seconds result

Source: https://www.reddit.com/r/LocalLLaMA/comments/1wsqjku/swift_15_hyperqwen_37_less_task_completion_time/

Single RTX 3090 / HyperQwen comparison:

| model | avg task time | avg output tokens/task | decode TG |
|---|---:|---:|---:|
| base Qwen fast quant | **108.1 s** | **8,985** | **112.1** |
| Swift 1.0 | **66.2 s** | **5,245** | 105.9 |
| Swift 1.5 INT8-head | **72.2 s** | **5,751** | 104.0 |
| Swift 1.5 INT4-head | ~**68.2 s** | ~**5,669** | ~100+ |

The comparison is roughly 630 tasks. Swift is physically slower per generated token but completes the workload materially faster because it generates far fewer tokens.

P51 consequence:
- materially strengthens the already-promoted **effective solved-task throughput** lane;
- do not relabel task-seconds as TG;
- base Qwen remains the quality/control checkpoint.

## Strict-window negative scan

- **TensorFold:** no post-boundary commit after 0.3.6.2.
- **Ishizuki:** no post-boundary commit.
- **llama.cpp:** no P51-target runtime change before cutoff; the 06:18:58 Muse schema fix is unrelated.
- **DASLab:** no newer official Flash-Next IQ3_S source-paired 32K/64K/128K/262K quality result found.
- **Exact dual M1 Max / TB4:** no new reproducible Flash-Next physical receipt.
- **Exact user's RTX 5070 Ti / Strata:** no new single-card 32K/64K/128K ladder or 8h/24h soak receipt.
- **MoEspresso 27-TG M1 lead:** promising but not promotable until the fork/settings/benchmark identity are public.

## Canonical planning state

Unchanged:
- Dual-M1 Flash-Next: **40 TG sustained @ genuine ~128K / 400 cold PP / ~70% >=40 TG**.
- Single-M1 dense27B: **25 TG / ~110 PP**.
- Persistent root-image target unchanged.
- RTX 5070 Ti dense CUDA-v2 and Strata ladders unchanged.
- IQ3_XXS AA>=38: **~85%**.
- IQ3_XXS AA>=40: **~65%**.
- IQ3_S AA>=40: **~80%**.
- Swift remains a separate effective-task-throughput lane, not a physical TG target.

## Files intentionally not changed

- `RESEARCH-TARGETS.md`: no planning probability or physical target moved.

## New hard boundary

**2026-09-29 06:21:54 UTC**
