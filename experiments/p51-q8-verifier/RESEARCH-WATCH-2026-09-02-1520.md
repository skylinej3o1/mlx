# Runtime Research Watch — 2026-09-02 15:20 ET

Scope: fresh external delta after `RESEARCH-WATCH-2026-09-02-1350.md`, following the canonical-state-first protocol. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DeepSeek-V4/DS4 distributed serving, and especially the planned 2x M1 Max 64 GB / TB4 Hermes agent system.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **UPDATE — DS4 #621 AProjQ4 Metal decode win reproduces on the current head.** A fresh M5 Max 128 GB rerun at `6a20b13`, 226 commits after the older reference, again reports a 3-rep paired median Q4/Q8 decode ratio of **1.155** and Q4 winning **32/32** frontiers from 2K through 65K. Prefill remains effectively tied. This strengthens AProjQ4 as a future lossy/capacity track but does not affect exact-Q8 P69.
2. **RECOVERED OLDER EVIDENCE — quantized Flash-Next PLE/n-gram tables are a major independent memory lever.** `primitive-ai/Qwen3.8-Flash-Next-PLE-quant` reduces the 51.2B-parameter BF16 PLE table from **95.4 GB** to **49 GB FP8**, **32 GB INT4**, or **28.8 GB NVFP4-style** and serves it mmap-backed. On its RTX PRO 6000/vLLM setup, INT4/NVFP4 table throughput is roughly 5-6% below the in-RAM BF16 table while measured knowledge/tool-call quality remains in the same run-to-run band; an INT4-table configuration was validated end-to-end inside a 48 GB container. This source predates the 13:50 pass, so classify it as recovered rather than new.
3. **RECOVERED PLE+MTP interaction evidence — table quantization can preserve much more speculative benefit than raw BF16 NVMe streaming on the tested GPU stack.** The same project reports real-prompt single-stream MTP at **142.6 tok/s** with BF16 table in RAM, **129.6** with INT4 mmap table, **128.8** with NVFP4 mmap table, versus **77.5-82.3** with the BF16 table directly on NVMe. Do not transfer these absolute rates to Apple; the portable idea is to quantize the sparse table itself before accepting a large SSD/page-fault tax.
4. **UPDATE — llama.cpp #28244/#28213 relationship clarified, not a new performance result.** #28244 reuses the existing selected-cell mask rather than deriving one from per-cell bias, keeping the change localized to qwen4exp.cpp. Existing measured result remains 103.4 -> 103.4 tok/s at 4K and 73.2 -> 78.9 at 50K; no new Apple evidence.
5. **NO CHANGE — upstream llama.cpp Flash-Next MTP #28243.** Still draft, same head, still only the unqualified 1.3-2x claim with no published hardware/context/acceptance table.
6. **NO CHANGE — oMLX MTP/cache/streaming threads.** No fresh comments after the 13:50 pass on #3382 verify-cost decomposition, #3330 ExactResident/prompt-tail, or #3359 SSD expert streaming. The temp>0 #3370 question also remains unresolved.
7. **NO CHANGE — exact dual-M1 receipts.** llama.cpp #27993 still has no new comments and therefore no dual-M1 Flash-Next TG receipt. DS4 #922 still has no new comments and no sustained dual-M1 0731 TG receipt.
8. **NO CHANGE — DS4 #861 distributed serving.** No new post-13:50 batching result. Existing B4 ~13.2 tok/s partial-row-batching evidence remains the latest.
9. **NO CHANGE — Layr and mlx-dspark.** No new Layr submission after #1481; `ARahim3/mlx-dspark` still reports its last code push at 2026-09-01 10:54 UTC.

Net: **do not move the B1 or B2-B4 dual-M1 forecast bands.** The useful new/recovered information is about future capacity engineering: projection precision and PLE precision can be treated as separate knobs, and PLE quantization may be substantially preferable to leaving a huge BF16 table exposed to SSD/page-cache behavior.

## UPDATE — DS4 #621 current-head M5 Max reproduction

Source: https://github.com/antirez/ds4/pull/621#issuecomment-5514694380

Physical MacBook Pro M5 Max 128 GB, fully resident AProjQ4/AProjQ8 pair, PR head `6a20b13`:

- cold-start run, 3-rep paired decode median Q4/Q8: **1.155**;
- hot-start run: 1.147;
- Q4 wins: **32 / 32** context frontiers in every repetition;
- prefill Q4/Q8: 1.003 cold (reported range 0.980-1.027), 1.021 hot — effectively tied;
- representative decode:
  - 2,048: Q4 48.80 vs Q8 41.62 tok/s, ratio 1.173;
  - 65,536: ratio 1.129.

The reporter notes substantial within-session throughput drift that is not explained by die temperature. Cold single-rep ratios can look closer to ~1.19, while 3-rep paired medians settle around 1.155. This is useful methodology for any future long Apple A/B: interleave arms and avoid interpreting one cold sweep as the stable effect.

### Implication

This is a strong requalification of the existing AProjQ4 architectural lead across a much newer code head. It remains **lossy/cross-quant evidence**, not exact-Q8 evidence, and it does not modify P69B13. For future Flash-Next/DS4 capacity tracks, however, selective projection quantization increasingly looks like a mature way to buy a few GiB plus decode speed rather than merely a size compromise.

## RECOVERED — quantized Flash-Next PLE/n-gram tables

Source: https://huggingface.co/primitive-ai/Qwen3.8-Flash-Next-PLE-quant

This source existed before the current pass and was missing from the formal watch chain, so classify it **RECOVERED OLDER EVIDENCE**.

The 51.2B-parameter PLE/n-gram table is published in several quantized sidecar formats:

| PLE table | Size |
|---|---:|
| BF16 reference | 95.4 GB |
| FP8 per-row | 49 GB |
| INT4 group-16 | 32 GB |
| NVFP4-style group-16 | 28.8 GB |

The implementation mmaps 128 shard files and dequantizes only the gathered rows, so anonymous host RAM scales with the working set rather than with the entire table.

### Measured GPU-stack evidence — not Apple

One RTX PRO 6000 Blackwell, 176 GB host RAM, local NVMe, mixed NVFP4/FP8 target, 8K in / 512 out, no prefix cache:

- BF16 table in RAM: ~84.4-84.5 tok/s B1, ~516.8-523.6 tok/s B32;
- INT4 mmap table: ~80.1-80.2 B1, ~483.6-487.9 B32;
- NVFP4 mmap table: ~80.1-80.3 B1, ~476.8-479.5 B32.

Reported knowledge scores remain approximately tied and the 200-item tool-call suite sits within its stated repeat spread. INT4 was also validated end-to-end inside a **48 GB container**, reporting ~79.4 tok/s B1 and ~486 tok/s B32 with sanity/tool-call gates passing.

### PLE + MTP interaction

On the project's real-prompt MTP comparison:

- no speculation: 91.2 tok/s;
- depth 3 with BF16 PLE in RAM: **142.6 tok/s**;
- depth 3 with INT4 mmap PLE: **129.6 tok/s**;
- depth 3 with NVFP4 mmap PLE: **128.8 tok/s**;
- depth 3 with BF16 PLE directly on NVMe: **77.5-82.3 tok/s**.

Again, these are **not Apple numbers**. The portable conclusion is architectural: if the huge sparse table must be offloaded, quantizing the table itself can reduce the active page working set enough to preserve much more speculative benefit than raw BF16 disk streaming.

### Implication for the dual-M1 Hermes plan

This gives us another future memory lever distinct from model/expert quantization:

1. keep the hot model execution path resident across PP2 when possible;
2. keep PLE as the first offload candidate because access is sparse;
3. if raw PLE footprint/page pressure is still too high, evaluate **PLE-only quantization** before resorting to broad expert streaming;
4. qualify quality separately because PLE quantization is lossy even when measured suites appear tied;
5. benchmark PLE precision against real agent/tool repetition, because that is where MTP and n-gram reuse matter most.

This could eventually help the four-agent/workstation-headroom target, but there is no M1-Max PLE-quant receipt here, so do not turn it into a RAM guarantee yet.

## llama.cpp / oMLX / distributed checks

### llama.cpp #28243 — no change

Still draft at the same head. No hardware benchmark table, context ladder, acceptance statistics, or Apple-specific result has appeared.

### llama.cpp #27993 — no change

No comments after 13:50 ET. Still no sustained 2x M1 Max Flash-Next decode result.

### DS4 #922 — no change

No comments after 13:50 ET. Still no sustained exact-0731 dual-M1 decode result.

### DS4 #861 — no change

No new batching measurement after the B4 partial-row result already recorded in the 13:50 delta.

### oMLX #3382 / #3330 / #3359 / #3370 — no material change

No post-13:50 result that changes the existing verify-cost, warm-agent-cache, SSD-expert-streaming, or temp>0-MTP conclusions.

### Layr / mlx-dspark — no change

- Layr: no new PR after #1481; best score remains `3.7291100105909`.
- mlx-dspark: repository metadata still shows last push at 2026-09-01 10:54 UTC.

## Forecast consequence

### Mature dual-M1 Flash-Next B1 — unchanged

| Target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

### ~128K active-context B1 — unchanged

| Target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate — unchanged

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

## Bottom line

No fresh receipt justifies moving the performance ladder. The pass does, however, sharpen the future memory/capacity strategy: **treat PLE precision independently from target-weight precision and expert residency**. A mature Hermes deployment may eventually use resident PP2 target weights, an aggressively memory-efficient PLE sidecar, exact resident/paged prompt state, and only selective SSD expert streaming when the workstation/agent budget requires it.
