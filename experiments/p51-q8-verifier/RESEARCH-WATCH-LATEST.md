# Project 51 / Relay — latest research watch 2026-10-23 07:19 EDT

**Previous verified canonical HEAD:** `54353c5a7f390fb50c5719f45e49d0ddf3da9ae0`
**Previous strict UTC cutoff:** 2026-10-23 04:54:15 UTC
**NEW STRICT UTC CUTOFF:** **2026-10-23 11:19:46 UTC (07:19:46 EDT)**. Next scan STRICTLY after; avoid including #945 Hipfire, which was created at 11:20:00Z beyond this boundary.
**Full primary-source report:** [RESEARCH-WATCH-2026-10-23-0719.md](./RESEARCH-WATCH-2026-10-23-0719.md). Prior [00:54](./RESEARCH-WATCH-2026-10-23-0054.md), [Oct22 20:23](./RESEARCH-WATCH-2026-10-22-2023.md), [Oct22 17:31](./RESEARCH-WATCH-2026-10-22-1731.md).

## Strongest newly created / merged evidence

- **MERGED oMLX #4776 (08:58Z)** reallocates tiny-bit oQ head/embedding budget into always-on dense layers with ≤70MB size variation: dense27B oQ2.5e chatKL**0.28→0.075**, HumanEval+**135→145**, base35B oQ4e KL**0.020→0.014**; a priority *quality* candidate for physically resident one-M1 dense/35B workers, **NOT FlashNext GSQ numeric target or xhigh solved-agent proof**.
- **MERGED oMLX #4763 (10:36Z)** Flint native text serving and oQ4e/6e validated 1,327 tests M4Max128; no owner M1Max inference; **raw logits differ between chunked and single-pass prefill**, must audit reliability before long sessions.
- **NEW oMLX #4782 (09:32Z) OPEN** serving prefix hit counters can falsely report success when all KV was evicted and prompt fully re-prefilled. 836 regression tests; no throughput change. Verify actual restored tokens/bytes, not counters, across 3–5 agents.
- **UPDATED OLD Strata #3231 (05:56Z) OPEN** M-series **128GB** Metal conversation parking: actual 5,323-token checkpoint save45.9ms/restore9.9ms, followup5323 reused/17 fresh, snapshot435.5MB (~82KB/token); cold greedy output matches test, but huge 128K multiagent memory and no owner64 demonstration.
- **NEW Strata #3806 (08:30Z) DRAFT** Gyro-L TQP5–7 trellis CPU/CUDA 32KPP1955.5/TG71.2 on CMP170HX, exact dequant; **NO Metal/HIP/SYCL or long-context coding xhigh**.
- **UPDATED OLD Strata #3185 (10:53Z) OPEN** 2-GPU RTX3090+V100 full-resident stage frees **21.71GiB** duplicated CPU expert arena commit, requires full 512-expert residency+no prompt borrowing; **NOT single RX6800+32GB or Mac DS4 memory recovery**.
- **NEW Strata #3800 (07:25Z) OPEN** schema-token masks across MTP draft steps: RTX4090 laptop IQ3S 20 agent reports first-pass valid **17/20→20/20**, avoiding 3 expensive CLI retries; Metal compile only.
- **NEW Strata #3819–#3821 ~10:48Z** GP100 4-GPU dedicated full VRAM: asynchronous commit removes waits (same output no reliable TG), long QSA 115K decode **51→52.5 (+2.9%)** parity, smaller prefill chunks improve short PP 10% **but change state and one response**. CUDA sm60 only; no owner speed.
- **NEW Mirai uzu #1009 (07:53Z)** M5Pro Qwen3.5 35B-M MoE int4 head/fused shared expert 78.2bf16→97.9 int4→112.5TG, different hardware, quant/behavior; pre-M5 not shown.
- **MERGED oMLX #4777** MiniMax M3.1 22.5→42 TG with DSpark on M3Ultra (different M1 capacity) and **MERGED Splash #539** Ornith122B DFlash2 (too large).
- **RECOVERED Swift1.5 FlashNext GSQ quant listing** now includes **IQ3_S 83.74GB** / IQ3_XXS75.97 / IQ2_XS68.15 / Q2_0 66.55, source checkpoint is Swift finetune not original general Qwen; timestamps not independently established and all full-shard sets exceed an individual 64GB M1's memory. Not a newly verified performance upgrade.

**Unchanged targets:** two separately housed 64GB/32GPU M1 Max, original Qwen3.8-Flash-Next ISTA-DASLab GSQ-RCO IQ3_S, physically occupied 128K ≥40 decode /425 genuinely cold PP, occupied native262K ≥35/400, source-like AA-like≥38, 3–5 independently resumable agents; single RTX5070Ti16+64 DDR5 Linux and single nonXT RX6800 gfx1030 16+32 DDR4, no third Mac. **None achieved/certified end-to-end**. No quant/hardware/prediction revisions.

**Next experiments:** physical single M1 real DS4 allocation and K4V3-Q8262K; actual 3–5 agent KV restored/admitted vs only reported hit, memory sharing and tool correctness, complete task throughput; merged oMLX dense27B low-bit/Flint/35B challenger M1 A/B; correct model-sized 5070Ti and smaller gfx1030; exact physical 5070Ti→M1 source-like recurrent/QSA state.
