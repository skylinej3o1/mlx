# Qwen3.8 MXFORGE research index

Status: **LATEST POINTER**

Updated: 2026-08-30 ET.

## Flash-Next resume order

Read these in order when resuming Flash-Next work:

1. `QWEN38_FLASH_NEXT_CONDITIONAL_MEMORY.md` — released architecture, PLE/QSA/GDN memory hierarchy and original SSD-tier thesis.
2. `QWEN38_FLASH_NEXT_DAY1_APPLE_QUANTS.md` — release-day Apple quant/runtime field evidence.
3. `QWEN38_FLASH_NEXT_LATE_DAY1_RERUN.md` — late day-one corrections and rerun evidence.
4. `QWEN38_FLASH_NEXT_DAY2_RUNTIME_DELTA.md` — M1 Ultra/tarruda anchor, AtomicChat quant audit, oMLX 0.6.3 MTP, revised 2x-M1 forecast.
5. `QWEN38_FLASH_NEXT_AUG28_FIELD_DELTA.md` — exact direct Metal QSA, cold SSD-PLE batching, llama.cpp native MTP, PLE rollback correctness, mixed-length batching, `ngram-mod`, distributed-MTP warning, and adjacent 5070 Ti adaptive-KV evidence.
6. `QWEN38_FLASH_NEXT_AUG28_LATE_DELTA.md` — batched depth-1 MTP under concurrency, layer-streamed Flash-Next imatrix calibration at ~21 GB active memory, stricter SSD-PLE cold rerun, and exact no-thinking/prefix-cache API reconstruction.
7. `QWEN38_AUG29_EVENING_DUAL_TRACK_DELTA.md` — M1/M2 FP16 leaf recast, concurrent-`pread` SSD PLE, 64GB QSA long-context memory fixes, PLE-residency model-swap bug, current Flash-Next DFlash incompatibility, and fresh scored/unqualified 27B challenge receipts.
8. `QWEN38_AUG30_MORNING_RUNTIME_DELTA.md` — context/history drafting promoted to an early two-M1 PP lane; M5 Metal long-context recovery; predecessor-index and QSA bookkeeping lessons; higher-bit affine MoE fast-path evidence; route-prep profiling; DFlash benchmark-hygiene warning; Flash-Next correctness follow-ups.
9. `QWEN38_AUG30_LATE_MORNING_DELTA.md` — predecessor-lookup head-to-head (#28011 vs #27992), dual-GB10 speed/correctness boundary, distributed PP speculative-transport pattern, local Codex metadata integration, effective-bpw bookkeeping.
10. **`QWEN38_AUG30_AFTERNOON_DELTA.md` — CURRENT FLASH-NEXT ADDENDUM.** Cache-integrated O(log n) predecessor lookup (#28040), large-QSA-TOP_K runtime evidence (#28032), single-96GB 165-170K field receipt, memory-rich/GPU-poor field receipt, E2Studio agent-efficiency comparison, and the missed-but-material 27B NVFP4-DFlash2 correctness fix (#28000).

## Qwen3.8-27B tuning resume

For the active Q8 verifier project, read:

1. `QWEN38_27B_AUG28_TUNING_REFRESH.md` — ecosystem scan mapped onto the post-P69B12 project state.
2. `QWEN38_27B_LAYR_MTP_CHALLENGE_MINING_AUG28.md` — mechanism-level mining of the Layr frontier and producer-side sidecar lessons.
3. `QWEN38_27B_5070TI_MEMORY_HIERARCHY_AUG29.md` — RTX 5070 Ti serving plan: jrell asymmetric quant + Bee KVarN/MTP + adaptive-KV overflow + Tameru/RAG/web.
4. `QWEN38_AUG29_EVENING_DUAL_TRACK_DELTA.md` — negative controls for narrow-QMV and producer-rewrite fusions, plus corrections separating scored rejections from timeout/infrastructure failures.
5. **`QWEN38_27B_M4MAX_EXTERNAL_CALIBRATION_AUG30.md` — CURRENT 27B EXTERNAL CALIBRATION.** M4 Max production-ish decode receipts across oQ8e native MTP, 8-bit+DFlash2, ~5-bpw target-only and MTPLX; conservative M4→M1 normalization; revised P69 confidence; DFlash2 priority bump; context-aware speculation; cache/edit-agent implications.
6. `QWEN38_AUG30_MORNING_RUNTIME_DELTA.md` — no new scored Layr frontier; DFlash effective-engine validation; context/history drafting as post-P69 serving lane.
7. `QWEN38_AUG30_LATE_MORNING_DELTA.md` — distributed PP+MTP transport evidence and quant-quality metadata rules.
8. **`QWEN38_AUG30_AFTERNOON_DELTA.md` — latest runtime qualification delta.** Layr still unchanged; adds merged llama.cpp #28000 showing that a broken NVFP4 DFlash2 scale path can silently collapse acceptance to ~0%, plus agent-efficiency evidence favoring medium reasoning.

The authoritative local experiment state remains:

- `experiments/p51-q8-verifier/STATUS.md` on branch `project51-q8-verifier`.

At the Aug-28 evening scan, GitHub `project51-q8-verifier` was at `5d6325f8747f8634061d1ea2e9bedf57a1010588`, with P69B12 promoted and P69B13 next. Always re-read STATUS and re-check the branch head before resuming experiments.

## Current highest-leverage takeaways

### Flash-Next

- **Context/history drafting remains an early distributed-serving lane.** Repeated code/edit workloads can gain heavily while novel prose falls back toward target-only behavior; this can potentially amortize a two-M1 PP boundary without first solving a distributed neural MTP head.
- **Predecessor lookup is converging on an upstream-worthy cache-integrated index.** #28040 moves O(log n) lookup into `llama_kv_cells`, removes parallel fallback structures, reports byte-identical multi-sequence and multimodal behavior, and improves RTX PRO 6000 generation 74.5→77.6 tok/s at 55K and 52.0→56.7 at 132K. If the same surface is first-order on Metal, prefer one authoritative position index over repeated scans or parallel side maps.
- **Profile the entire QSA selector pipeline, not only attention math.** Vulkan #28032 shows large-TOP_K/indexer work can be close to neutral at d0 yet become a first-order 16K-32K tax. On GB10, TG128 d32K improved 12.02→19.78 and PP512 d32K 390→521; these numbers do not transfer to Metal, but the bottleneck class does.
- **Microkernel speed is not the product metric.** Competing Vulkan TOP_K #28036 had faster isolated decode TOP_K in some cases but weaker whole-model/prefill behavior and was closed. Continue optimizing complete task/round cost.
- **PLE should remain a first-class pageable/compressed tier.** A fresh single RTX PRO 6000 field setup reports ~165-170K context, INT4 PLE, ~89GB VRAM plus ~33GB page cache, and 76-125 tok/s depending MTP acceptance. This is not an Apple forecast; it reinforces reserving fast memory for trunk/KV/state rather than insisting on full-precision PLE residency.
- **Memory contention is first-order even when the model fits.** A 256GB DDR4 + RTX3060 field setup reports Flash-Next ~12-15 tok/s at 65K but ~3-5 tok/s under competing memory-heavy workloads. Qualify the two-M1 service under realistic background load, not only a clean benchmark process.
- **Correctness qualification gates every performance promotion.** Retain long generation, ordered-marker/literal retrieval, tool-call continuation, long-output→short-prefill transition, prefix reuse, concurrent joins, speculative rollback and post-cancel health checks.
- **Distributed native MTP is risky but no longer architecturally mysterious.** External PP+TP work demonstrates compact proposal metadata transport, rank-local acceptance derivation, all-rank optimistic-output trimming and recurrent rollback. Use it as a state-machine reference, not an Apple speed claim.
- M1/M2 BF16-leaf→FP16 recast remains a production-performance lane: reported M1 Ultra gains ~+5% novel TG, +14% rewrite TG, +60% PP; not bit-identical.
- SSD PLE remains an active optimization surface: concurrent `pread()` on M4 Max exposed ~11x random-read IOPS and cut a reported 40K cold TTFT from ~217s to ~6.5s while improving decode.
- The old ~43K ceiling on a 64GB Mac was substantially runtime pathology; fixed QSA/snapshot paths reached ~96K on M4 Pro 64GB. Full 262K on 64GB still needs real QSA KV quantization.
- **Quant labels are insufficient quality metadata.** Record payload/effective bpw, tensor-family allocation, calibration, activation precision and MTP-head precision. `NVFP4` alone does not define quality; a well-allocated ~6.5 effective-bpw artifact is generally a high-confidence daily-driver class, but allocation still matters.
- Higher-bit quality quant no longer implies permanent generic affine fallback: oMLX has group-64 Q4/Q6/Q8 native block-list MoE machinery with real Q6 gains on another architecture. Port to Qwen4-exp remains future work.
- oMLX DFlash is not currently a real Flash-Next (`qwen4_exp`) path; native MTP and context/history drafting are the current relevant speculation lanes.
- **Agent serving should default to medium reasoning and treat xhigh as escalation.** E2Studio's 100-task Django subset reports Flash-Next 91 at both medium and xhigh, with medium the best request/point efficiency in the whole test; xhigh completed the same tasks while being chattier. Treat this as workload evidence, not universal model truth.
- Keep roughly 400-550 tok/s as the normal 20-30K PP target and roughly 40-50 tok/s as the mature central two-M1 TG band until local measurement. The new external evidence improves confidence in the memory hierarchy and long-context software-cleanup plan, not the raw two-M1 headline forecast.

### Qwen3.8-27B

- Keep P69B13 constrained to the already-measured GDN/projection/downstream-tail remainder; do not reprofile/reopen merely because an external runtime explores a similar surface.
- Do not generalize wide-QMV geometry to narrow attention K/V: Layr #1478 was parity-clean but materially slower than the 3.7291 frontier.
- Do not replace an efficient compiled flat producer with a barrier-heavy row kernel merely to emit xsums: FA `o_proj` (#1476) and GDN postnorm `out_proj` (#1477) were parity-clean regressions.
- Producer-side sidecars are attractive only when they ride an already-required/good producer without materially changing launch geometry.
- #1470 trained hybrid head and #1472 one-pass M=6/7/8 remain **unqualified**, not scored negatives; #1481 also did not establish a new scored frontier.
- **Layr remains unchanged at 3.7291100105909; no new submission exists beyond #1481.** No change to the active P69 plan.
- Current rough frozen-ruler confidence remains: >=20.0 ~80-85%, >=20.5 ~55-60%, >=21.0 ~35-40%, >=21.5 ~20%, ~22+ ~10%.
- DFlash2 remains high-priority post-P69, but #28000 adds a hard qualification requirement: a quantized DFlash2 drafter can appear enabled while missing projection scales and accepting essentially zero useful drafts. Verify effective engine, quant metadata, acceptance/accepted-per-round, target-only control and emitted-token fidelity.
- External M4 Max calibration still makes 20.5 and low-21s credible residual targets on the frozen M1 ruler, while remaining a calibration rather than an M1 prediction.
- Speculative policy should eventually be context-aware; measure 32K/64K/128K/256K crossover instead of fixing one depth everywhere.
- A quality-certified lower-bpw speed profile remains separate from the exact-Q8 ruler. Store effective bpw and protected tensor families in artifact metadata/naming.
- E2Studio's current local-agent subset reports the 27B family at 74-81, with medium reasoning as good or better in score/efficiency than xhigh. Include medium-reasoning task wall time as a first-class serving metric.

Current research branch: `mxforge-research-20260826`.

When resuming from another chat, read this index first, then the relevant current delta before updating forecasts or selecting implementation work.
