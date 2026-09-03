# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-0400.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-03 04:00 ET

This was a narrow ~20-minute freshness pass after the 03:40 delta and is intentionally recorded as **NO MATERIAL DELTA**. It advances the search/audit boundary to **2026-09-03 07:38 UTC** without manufacturing a new project result from unrelated upstream activity.

Checks:

- **NO CHANGE — oMLX:** no new PR/issue/main-branch update after the boundary that changes tracked Flash-Next/Qwen3.8 conclusions.
- **NO CHANGE — exact dual-M1:** llama.cpp #27993 and DS4 #922 still have no sustained 2x M1 Max Flash-Next/0731 TG receipt.
- **NO CHANGE — PP2 mapping fix:** DS4 #957 still has no post-fix Apple throughput result.
- **NO CHANGE — MTP/checkpoint:** llama.cpp #28243 and #28302 have no new follow-up after the Apple results already recorded at 03:40.
- **NO CHANGE — Layr / mlx-dspark:** no new Layr submission; mlx-dspark still reports last code push at 2026-09-01 10:54 UTC.
- **BROADER SWEEP:** web/Reddit/Hugging Face mainly resurfaced already-known single-M1 64 GB Flash-Next evidence and existing oMLX benchmarks. No new dual-M1 calibration appeared.
- Fresh llama.cpp SYCL/CUDA/HIP activity after the boundary is unrelated to Apple Metal / Flash-Next / exact-verifier work and is intentionally not promoted.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged**. There is still no exact dual-M1 Flash-Next TG calibration.

Hermes policy remains: 3-4 logical agents, 2-3 active compute slots, session-aware hot ownership, staleness-aware eviction, rewind-capable recurrent checkpoints under a byte budget, durable SSD exact-terminal fallback, asymmetric resident PP2, and speculative depth enabled only after identity + wall-clock qualification.

The user's mature-system target of roughly **400+ tok/s cold prefill plus excellent prompt/prefix caching** remains sensible and unproven on dual M1 Max.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
