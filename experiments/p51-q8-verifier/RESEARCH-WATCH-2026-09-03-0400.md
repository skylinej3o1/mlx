# Runtime Research Watch — 2026-09-03 04:00 ET

Scope: narrow freshness pass after `RESEARCH-WATCH-2026-09-03-0340.md`, using **2026-09-03 07:38 UTC** as the hard search boundary. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DS4 distributed serving, and the planned 2x M1 Max 64 GB / TB4 Hermes system.

This is intentionally a **NO MATERIAL DELTA** checkpoint. The search window is only about twenty minutes. It is recorded to advance the audit/freshness boundary without relabeling unrelated upstream activity as a new project result.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Search result

1. **NO CHANGE — oMLX.** GitHub has no PR, issue, or main-branch commit updated after the 07:38 UTC boundary that changes the tracked Flash-Next/Qwen3.8 runtime state. No new physical Flash-Next Apple receipt appeared in the tracked oMLX threads.

2. **NO CHANGE — exact dual-M1 Flash-Next.** llama.cpp #27993 has no new comment/result after the boundary. There is still no sustained 2x M1 Max Flash-Next TG result and no completed long-context needle receipt.

3. **NO CHANGE — llama.cpp MTP/checkpoint threads.** #28243 has no new follow-up after the M5 Pro identity/performance caution recorded in the 03:40 delta. #28302 has no new maintainer/physical follow-up after the M1 Pro rewind-checkpoint receipt already recorded there.

4. **NO CHANGE — DS4 dual-node tracks.** DS4 has no repository commit or PR update after the boundary. #922 still has no sustained dual-M1 0731 TG result, and #957 still has no post-fix Apple throughput receipt for coalesced `--layers` Metal mappings.

5. **NO CHANGE — Layr / mlx-dspark.** Layr has no newly updated submission after the boundary. `ARahim3/mlx-dspark` still reports `pushed_at = 2026-09-01T10:54:45Z`; repository metadata activity is not a code update.

6. **IRRELEVANT FRESH UPSTREAM ACTIVITY — do not promote.** llama.cpp main did receive a fresh SYCL peer-to-peer-copy commit after the boundary, and several unrelated CUDA/HIP PRs were active. None provide Apple Metal, Flash-Next, dual-M1, or exact-verifier evidence, so they are intentionally excluded from project conclusions.

7. **BROADER WEB / REDDIT / HUGGING FACE SWEEP — no new dual-M1 receipt.** Fresh search mainly resurfaced already-known single-M1 64 GB Flash-Next reports and existing oMLX community benchmarks. No new post/search result provided a sustained 2x M1 Max Flash-Next decode measurement, new PP2 result, or stronger long-context dual-M1 calibration. A newly listed Qwen3.8-Max-0902 cloud snapshot is outside this local-runtime watch scope.

## Forecast consequence

**None.** Short/medium B1, ~128K B1, and mature B2-B4 aggregate probability bands remain unchanged because the missing calibration is still the same physical receipt: sustained Qwen3.8-Flash-Next execution on the exact 2x M1 Max 64 GB / TB4 topology.

Hermes architecture remains unchanged from the 03:40 delta:

- 3-4 logical persistent Flash-Next agents;
- normally 2-3 active compute slots;
- session-aware hot-state ownership and exact reuse;
- staleness-aware eviction;
- rewind-capable recurrent checkpoints under a byte budget;
- durable SSD exact-terminal/paged fallback;
- bounded cache persistence under pressure/unload;
- asymmetric resident PP2 with workstation headroom on the primary Mac;
- speculative depth only after identity + wall-clock qualification on the exact runtime/hardware/quant/workload.

The mature target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**. It remains a design target, not a dual-M1 measurement.

Canonical `RESEARCH-STATE.md` remains last consolidated at 2026-09-02 05:30 ET; this no-delta checkpoint does not justify reconsolidation.
