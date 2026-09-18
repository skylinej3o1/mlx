# External runtime watch — 2026-09-18 11:03 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-18 13:32:09 UTC` through `2026-09-18 15:03:36 UTC`.

PRs, issues, comments/reviews, and default-branch commits were explicitly screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Current Qwen3.8-Flash-Next Hugging Face/community surfaces were also searched. Evidence time means substantive measurement/investigation time, not crawler, merge, label, bot or rebase timestamps.

## Executive result

**No exact dual-M1-Max/TB4 Q5 receipt appeared. Numeric targets and planning confidence stay unchanged.**

Flash-Next remains:
- canonical quant lane: **Q5-class / eventual ~5.x BPW**
- target topology: **2x M1 Max 64 GB / TB4**
- headline target: **40 TG sustained at ~128K**
- cold PP target: **400 PP**
- planning confidence: **~55% for 40 TG @128K**, **~65-70% for 400 PP**

The most important change in this pass is a **correction**, not a new target receipt: the prior DS4 claim that the optimized M1 path halved prefill at chunk128 was invalid because the base binary did not actually honor the CLI chunk value. Once effective settings are matched, the optimized M1 path is faster.

## NEW — corrected DS4 #1056 M1 Max 64 GB resident A/B

Substantive comment: **2026-09-18 14:41:39 UTC**.

Hardware/model:
- Apple **M1 Max 64 GB**
- Qwen3.8-Flash-Next **Q2**
- Metal
- resident mode for the main A/B
- base `8db1d1d`
- candidate `04c0867`
- temp 0, no-think
- ABBA/BAAB, four observations per ordinary cell, two for deep/streaming cells.

### Measurement correction

The earlier base test passed `--prefill-chunk 128`, but upstream `ds4_engine_generate_argmax` actually reads `DS4_QWEN4_PREFILL_CHUNK` and otherwise defaults to 8192.

Control on the same base binary / long prompt:
- requested chunk128, env unset → actually 8192: **267.5 PP**
- effective chunk128 forced through env: **125.7 PP**

Therefore the previously recorded roughly 282→136 PP “regression” was an **8192-vs-128 configuration mismatch**.

With effective chunk128 pinned in both arms:
- base → candidate: **127.5 -> 136.6 PP (+7%)**.

The negative throughput finding is retracted.

### Corrected resident performance — chunk2048

5,760-token prompt:
- ordinary PP: **274.4 -> 288.0 (+5%)**
- ordinary TG: **24.96 -> 28.57 (+14%)**
- MTP TG: **27.24 -> 31.75 (+17%)**
- MTP PP: **273.5 -> 259.0 (-5.3%)**
- MTP acceptance: **72.2% -> 79.1%**

17,408-token prompt:
- ordinary PP: **271.4 -> 285.0 (+5%)**
- ordinary TG: **23.39 -> 26.80 (+15%)**
- MTP TG: **24.76 -> 28.41 (+15%)**
- MTP PP: **272.6 -> 265.9 (-2.5%)**
- MTP acceptance: **59.5% -> 70.8%**

Reported decode ranges do not overlap in these cells.

Classification: **new exact M1 Max physical A/B, exact model family, low-bit Q2 and medium context. Strong M1 runtime evidence, but not target-Q5/128K proof.**

### Corrected numerical interpretation

Unchunked 5,760-token prefill:
- base @8192 and candidate @8192 are **bit-identical**.

Chunked vs unchunked max logit delta:
- candidate chunk2048: **0.424518**
- candidate chunk128: **0.424518**
- base chunk2048: **0.594551**
- base chunk128: **1.132671**.

Thus the candidate's chunk128 and chunk2048 paths are internally identical and closer to the unchunked reference than base, but **a residual ~0.4245 difference between chunked and unchunked remains open**.

Project 51 action:
1. benchmark manifests record the **effective runtime-resolved setting**, not only requested CLI flags;
2. chunk-size performance A/Bs are invalid unless both arms prove the same effective chunk;
3. chunked-vs-unchunked logit/cache-state parity remains a correctness gate even after throughput is fixed.

Target impact: **no numeric or confidence move**. The corrected data removes a false negative and strengthens medium-context M1 headroom, but does not close the Q5/128K/TB4 gap.

## NEW — oMLX #3738: Flash-Next dev4 64 GB memory regression

Issue created **2026-09-18 13:54:03 UTC**.

Setup:
- M4 Max 64 GB
- oMLX **0.7.0.dev4**
- Qwen3.8-Flash-Next-oQ4e
- 25% resident experts
- MoE SSD offload
- n-gram SSD offload
- context benchmark targeting 16K, Max Context prefill priority.

Observed:
- during a 4,096-token prefill, process memory reaches **53.9 GB**
- hard watermark is **53.2 GB**
- Metal cap ceiling **56.0 GB**
- request aborts and model is eventually evicted.

Reporter states:
- same behavior occurs with a GBP-DE **oQ5e** Flash artifact;
- dev2 ran slowly but did not show the same runaway memory behavior.

No root cause/fix existed by cutoff.

Classification: **new same-model-family Apple 64 GB runtime-regression evidence, not target-topology evidence.**

Project 51 action:
- pin exact oMLX/MLX/runtime SHA in fit/performance receipts;
- run a prefill-memory staircase before accepting a runtime upgrade;
- distinguish model intrinsic fit from a version-specific memory-manager/transient regression;
- do not lower Q5 target confidence from this issue unless the behavior reproduces on the chosen Project 51 runtime.

## NEW — oMLX #3737: dev4 27B MTP/ANE regression

Issue created **2026-09-18 13:47:22 UTC**.

Setup:
- M4 Max 64 GB
- Qwen3.8-27B-4bit + VLM MTP drafter
- oMLX dev1 vs dev4
- same benchmark/config.

VLM MTP TG, dev1 -> dev4:
- 1K: **44.2 -> 35.4**
- 4K: **41.2 -> 32.4**
- 16K: **42.9 -> 25.4**.

Acceptance stays essentially unchanged:
- 62.1/59.4/74.9% -> 62.8/57.1/75.5%.

That points toward verify-round/runtime cost rather than poorer drafting.

At 16K with the drafter loaded:
- ANE banks are released for headroom;
- reported freed amount: **11.94 GB**
- PP: **302 -> 239**
- with MTP off, banks remain and PP returns to ~302.

One unload then leaves **16.45 GB active** after emergency reclaim failure until server restart.

Classification: **new exact oMLX runtime regression for the 27B lane.**

Project 51 action:
27B qualification records:
- runtime version/SHA,
- MTP verify cost separately from acceptance,
- ANE-bank residency/release events,
- post-unload active memory.

No 27B hardware target moves from a software regression.

## NEW — vLLM #57569: auto-calibration can be unstable

PR created **2026-09-18 14:02:50 UTC** to calibrate DMA-vs-Triton KV-load cutoffs at handler initialization.

A30 initial measurements show the concept can select hardware-specific cutoffs with roughly **~20 ms actual measurement overhead**, aside from first Triton/JIT cost.

But a GB10 cross-check at **14:20 UTC** finds repeated identical calibration calls can choose very different thresholds.

Examples across seven consecutive calls:

16 KiB:
- 5-rep calibration picks **32, 16, 256, 32, 16, 64, 256**
- 25-rep calibration narrows somewhat to **16, 32, 16, 16, 16, 16, 16**.

64 KiB remains unstable even at 25 reps:
- **128, 256, 128, 32, 32, 32, 128**.

The DMA arm is reported stable to ~2%; Triton median latency at N=16 can move from roughly 0.037 to 0.25 ms, about **6x**, and the selection algorithm amplifies one noisy crossover.

Classification: **new exact auto-tuning methodology evidence, non-target hardware.**

Project 51 rule:
automatic threshold tuning cannot promote from a single sweep. Require:
- a meaningful winning margin / hysteresis,
- repeated independent sweeps or consensus,
- raw spread persisted in artifacts,
- fail-closed/default behavior when the surface is unstable.

This is directly relevant to future autonomous Mac tuning loops.

## NEW — vLLM #57575: sparse-prefill transients must be reserved before KV sizing

Draft PR created **2026-09-18 14:35:22 UTC** for GLM sparse MLA.

Reported 4,096-token prefill transient buffers:
- padded query: **288 MiB**
- FlashMLA output: **256 MiB**
- compact mixed-batch output: **128 MiB**
- plus ~2 MiB internal statistics tensors.

Startup profiling had skipped attention, so these allocations were not included before KV sizing and could appear later at runtime.

The draft reserves the large buffers through the workspace manager before KV sizing. However:
- GPU tests were not run because dependency setup hit HTTP 429;
- no physical reproduction/performance/eval receipt exists yet.

Classification: **new mechanism evidence / unvalidated draft**, not performance evidence.

Project 51 action:
representative sparse-prefill workspace must be part of fit admission before allocating cache. Existing post-admission fit rules are strengthened to explicitly include the largest planned prefill chunk.

## Strict-window negative/no-promotion findings

- vLLM #57560 still has no serving/accuracy A/B for the ROCm FlyDSL GDN prefill backend at the cutoff.
- vLLM #57578 is a GLM NoPE sparse-MLA compatibility bug on GB10, not Flash-Next evidence.
- DS4 #1085 proposes ternary PTQ for DeepSeek V4.1 and extrapolates possible streaming gains; no V4.1 ternary quant or benchmark exists yet, so no Project 51 target change.
- llama.cpp strict-window commits contain no new Flash-Next Apple performance receipt.
- mlx-serve had no new strict-window Flash measurement after the #438/#460 evidence already recorded.
- Fresh Hugging Face/community search found no exact **dual-M1 Max / TB4 / Q5** receipt. A current Reddit thread contains a roughly 20 TG / 200 PP M1 Max 64 GB user claim, but without a sufficiently specified recipe to improve upon the exact M1 receipts already in the repo.

## Target / confidence decision

**No change.**

Flash-Next dual M1 Max:
- **40 TG @ ~128K: ~55%**
- **400 cold PP: ~65-70%**

TG ladder:
- >=30: ~85-90%
- >=35: ~70-75%
- >=40: ~55%
- >=45: ~30-35%
- >=50: ~15-20%.

PP ladder:
- >=250: ~97%
- >=300: ~90%
- >=350: ~80%
- >=400: ~65-70%
- >=450: ~45-50%
- >=500: ~30-35%
- >=600: ~12-15%
- >=700: ~5%.

The corrected DS4 result improves confidence in the **quality of the M1 optimization path**, but because it is Q2 and medium-context it is not enough to raise the 40@128K Q5 forecast above the current mid-50s.

## New/strengthened qualification rules

1. **Requested setting != effective setting:** benchmark manifests must capture runtime-resolved chunk size, backend, cache/offload policy and acceleration state.
2. **Matched effective configuration before A/B:** a benchmark is invalid if the arms silently resolve different settings.
3. **Chunked/un-chunked numerical gate:** self-consistency across chunk widths is necessary but not sufficient; compare to an unchunked/reference path where feasible.
4. **Runtime upgrade memory staircase:** rerun fit/prefill peak tests on every oMLX/MLX version change.
5. **Autotune stability gate:** threshold learners need margin, repeated consensus and raw variance artifacts.
6. **Largest-prefill workspace in fit admission:** reserve/price sparse transient buffers before cache sizing.

## Hard freshness boundary

`2026-09-18 15:03:36 UTC`
