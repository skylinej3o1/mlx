# Qwen3.8 MXFORGE research index

Status: **LATEST POINTER**

Updated: 2026-08-29 evening ET.

## Flash-Next resume order

Read these in order when resuming Flash-Next work:

1. `QWEN38_FLASH_NEXT_CONDITIONAL_MEMORY.md` — released architecture, PLE/QSA/GDN memory hierarchy and original SSD-tier thesis.
2. `QWEN38_FLASH_NEXT_DAY1_APPLE_QUANTS.md` — release-day Apple quant/runtime field evidence.
3. `QWEN38_FLASH_NEXT_LATE_DAY1_RERUN.md` — late day-one corrections and rerun evidence.
4. `QWEN38_FLASH_NEXT_DAY2_RUNTIME_DELTA.md` — M1 Ultra/tarruda anchor, AtomicChat quant audit, oMLX 0.6.3 MTP, revised 2x-M1 forecast.
5. `QWEN38_FLASH_NEXT_AUG28_FIELD_DELTA.md` — exact direct Metal QSA, cold SSD-PLE batching, llama.cpp native MTP, PLE rollback correctness, mixed-length batching, `ngram-mod`, distributed-MTP warning, and adjacent 5070 Ti adaptive-KV evidence.
6. `QWEN38_FLASH_NEXT_AUG28_LATE_DELTA.md` — batched depth-1 MTP under concurrency, layer-streamed Flash-Next imatrix calibration at ~21 GB active memory, stricter SSD-PLE cold rerun, and exact no-thinking/prefix-cache API reconstruction.
7. **`QWEN38_AUG29_EVENING_DUAL_TRACK_DELTA.md` — CURRENT DUAL-TRACK ADDENDUM.** M1/M2 FP16 leaf recast, concurrent-`pread` SSD PLE, 64GB QSA long-context memory fixes, PLE-residency model-swap bug, current Flash-Next DFlash incompatibility, and fresh scored/unqualified 27B challenge receipts.

## Qwen3.8-27B tuning resume

For the active Q8 verifier project, read:

1. `QWEN38_27B_AUG28_TUNING_REFRESH.md` — ecosystem scan mapped onto the post-P69B12 project state.
2. `QWEN38_27B_LAYR_MTP_CHALLENGE_MINING_AUG28.md` — mechanism-level mining of the Layr frontier and producer-side sidecar lessons.
3. `QWEN38_27B_5070TI_MEMORY_HIERARCHY_AUG29.md` — RTX 5070 Ti serving plan: jrell asymmetric quant + Bee KVarN/MTP + adaptive-KV overflow + Tameru/RAG/web.
4. **`QWEN38_AUG29_EVENING_DUAL_TRACK_DELTA.md`** — fresh negative controls for narrow-QMV and producer-rewrite fusions, plus corrections separating scored rejections from timeout/infrastructure failures.

The authoritative local experiment state remains:

- `experiments/p51-q8-verifier/STATUS.md` on branch `project51-q8-verifier`.

At the Aug-28 evening scan, GitHub `project51-q8-verifier` was at `5d6325f8747f8634061d1ea2e9bedf57a1010588`, with P69B12 promoted and P69B13 next. Always re-read STATUS and re-check the branch head before resuming experiments.

## Current highest-leverage takeaways

### Flash-Next

- M1/M2-specific BF16-leaf -> FP16 recast is now a first-class performance lane: reported M1 Ultra gains were about +5% novel TG, +14% rewrite TG and +60% PP without increasing model storage width; it is not bit-identical and belongs to a production-quality profile rather than an exact-numerics ruler.
- SSD PLE is increasingly an active runtime-optimization surface rather than a fixed tax. Concurrent `pread()` reportedly exposed ~11x random-read IOPS on M4 Max NVMe and cut a 40K cold Flash-Next TTFT from ~217s to ~6.5s while also improving decode.
- the old ~43K ceiling on a 64GB Mac was substantially caused by QSA mask routing and full-prefix snapshotting pathologies; the fixed path reached ~96K cleanly on M4 Pro 64GB. Full 262K on 64GB still requires real QSA KV quantization.
- PLE residency decisions must use stable capacity and be observable; a model-swap admission bug could silently force resident PLE to SSD and cut reported M1 Ultra decode from ~35 to ~14 tok/s.
- oMLX DFlash is **not currently a real Flash-Next (`qwen4_exp`) path**; count native MTP and context/ngram drafting instead.
- direct exact QSA, layer-streamed quant calibration, batched MTP, rollback correctness, and prompt-cache reconstruction remain important.
- **distributed Flash-Next MTP remains the unresolved two-M1 risk.** None of the Aug-29 findings removes the Thunderbolt verifier/state problem.
- revised two-M1 confidence is mildly higher because M1 compute and SSD-PLE paths improved: ~400-550 tok/s at normal 20-30K PP is increasingly credible; 40-50+ TG still depends on competent distributed MTP.

### Qwen3.8-27B

- keep P69B13 constrained to the already-measured GDN/projection/downstream-tail remainder; no reprofile/reopen merely because an external challenge explores a similar surface.
- do **not** generalize wide QMV geometry to narrow attention K/V: Layr #1478 kept parity but scored 3.6353 vs 3.7291 frontier.
- do **not** replace an efficient compiled flat elementwise producer with a barrier-heavy custom row kernel merely to emit xsums: both FA `o_proj` (#1476, 3.6490) and GDN postnorm `out_proj` (#1477, 3.6469) were parity-clean but materially slower than the 3.7291 frontier.
- refined sidecar rule: producer-side auxiliary-data fusion is attractive only when it rides an already-required/good producer without materially changing launch geometry.
- prior positive evidence from the promoted residual/RMSNorm xsums producer remains valid; the new failures define where the pattern stops working.
- PR #1470's trained hybrid MTP head is **unqualified**, not a scored negative: its official run timed out after three hours despite promising local M3 Max acceptance results.
- PR #1472's one-pass M=6/7/8 QMV is also **unqualified**, not a scored negative: the benchmark failed during workspace preparation.
- PR #1481 broad compiled-shapeless elementwise fusion was cancelled before scoring and is not benchmark evidence.
- current finished-P69 Q8 M1 target remains roughly 20.0-20.3 tok/s central; this sweep improves candidate-selection discipline rather than revealing a new guaranteed throughput step.

Current research branch: `mxforge-research-20260826`.

When resuming from another chat, read this index first, then the relevant current delta before updating forecasts or selecting implementation work.
