# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-0730.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-03 07:30 ET

This pass adds two fresh DS4 state-correctness results that are directly relevant to long-lived Hermes agents. It does **not** change the certified verifier state or dual-M1 throughput forecast bands.

Material deltas:

- **NEW — DS4 #960 cancellation-safe prompt frontier:** snapshots model-owned mutable state before decode so cancelled requests can restore raw KV/recurrent/indexer state exactly rather than merely trimming transcript tokens. M3 Ultra/Metal validation reproduced 607 full-logit vectors after full ring overwrite; an image/tool cancellation restored **1,272 tokens** and exact retry reused all 1,272 with zero suffix prefill. Snapshot capture averaged **2.717 ms** and ~22.39 MiB GPU backup tensors plus host state. Add cancellation/retry as an explicit hot transactional checkpoint layer for Hermes.
- **NEW — DS4 #961 multimodal conditioning provenance:** identical text tokens do not imply identical KV after image conditioning. Cache keys include image count/spans, final conditioning hashes and canonical token text. M3 Ultra/Metal restored a **1,044-token image-conditioned checkpoint across restart in 9.2 ms**; changed-image controls rebuilt. Future Hermes multimodal cache identity must include all non-text conditioning provenance.
- **STATUS UPDATE — oMLX #2595 generic MoE expert offload:** remains a useful capacity/reference mechanism but is currently open/out-of-sync with main (`mergeable=false`); the fresh activity is a rebase request, not a new performance receipt. No Flash-Next forecast change.
- **NEW but non-material — oMLX #3401/#3400:** quant-size UI estimation and GLM affine-quant loading issues; no current Flash-Next runtime consequence.
- **NO CHANGE — exact dual-M1:** llama.cpp #27993 and DS4 #922 still have no sustained 2x M1 Max Flash-Next/0731 TG receipt. DS4 #957 still has no post-fix Apple mapping throughput result. No new #28243/#28302/#861 measurement.
- **NO CHANGE — Layr / mlx-dspark / broader sweep:** no new Layr submission; mlx-dspark still reports last code push at 2026-09-01 10:54 UTC; web/Reddit/Hugging Face produced no new physical dual-M1 calibration.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged**. There is still no exact dual-M1 Flash-Next TG calibration.

Hermes policy now explicitly separates three state layers: (1) cheap resident transactional frontier checkpoint for cancellation/retry, (2) bounded rewind checkpoints for edits/branching/compaction, and (3) durable SSD exact-terminal/paged state for unload/restart/slot eviction. Cache identity must be conditioning-complete for multimodal turns.

The mature target remains 3-4 logical agents, 2-3 active compute slots, session-aware hot ownership, staleness-aware eviction, asymmetric resident PP2, and roughly **400+ tok/s cold prefill plus excellent prompt/session caching** as a design target rather than a dual-M1 measurement.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
