# External runtime watch — 2026-09-18 17:34 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-18 16:27:22 UTC` through `2026-09-18 21:34:45 UTC`.

PRs, issues, comments/reviews, and default-branch commits were explicitly screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Fresh Qwen3.8-Flash-Next Hugging Face/community/web surfaces were also searched. Evidence time means substantive source/measurement time, not crawler, merge, label, bot, or rebase timestamps.

A major **RECOVERED OLDER EVIDENCE** item was surfaced during this pass. Its repository/measurements date to **2026-09-08**, so it is not called new merely because it was discovered now.

## Executive result

**No exact dual-M1-Max/TB4 Q5 receipt appeared, so the numeric targets stay fixed. Planning confidence rises because of a newly recovered exact-M1, near-target-precision long-context receipt.**

Flash-Next remains:
- canonical quant lane: **Q5-class / eventual ~5.x BPW**
- target topology: **2x M1 Max 64 GB / TB4**
- headline target: **40 TG sustained at ~128K**
- cold PP target: **400 PP**

Updated planning confidence:
- **40 TG @ ~128K: ~65%** (from ~55%)
- **400 cold PP: ~75%** (from ~65-70%)

The confidence move is driven by a public, raw-data-backed M1 Max 64 GB receipt at **4.27 bpw** with modern indexed QSA/direct PLE and **MTP off**, not by stronger-chip extrapolation.

## RECOVERED OLDER EVIDENCE — modern M1 Max 64 GB / 4.27-bpw / ~118K receipt

Source:
- repository: `kadirbalalan/qwen38-mac-fast`
- repository commit: `feeb3d57bf340f027f55eb56760c736cd80c4326`
- commit date: **2026-09-08 09:17:30 UTC**
- runtime fork commit: `535e1f69d4bdf9c9aa51619636595d155ff02ccf`
- raw JSON checked into `benchmarks/raw/`.

Exact setup:
- Apple **M1 Max 64 GB**
- Qwen3.8-Flash-Next
- AtomicChat **AD-4.27bpw-Q4_K_M-M64**, 33 shards, ~94.5 GB download
- Q8_0 K / Q8_0 V
- Flash Attention ON
- Metal indexed QSA with Q8-aware selected-row gather/dequant
- direct PLE: `--lazy-mode on-direct`
- one slot
- batch / ubatch: 512 / 256
- prompt cache RAM: 0
- **MTP OFF**
- n-gram sidecar OFF
- Q8 vision projector kept off Metal
- Metal wired limit 57,344 MiB.

Controlled sweep, each with **384 generated tokens**:

| Actual prompt | PP | TG |
|---:|---:|---:|
| 84,984 | **208.84** | **23.80** |
| 93,212 | **206.87** | **23.79** |
| 101,396 | **205.27** | **23.47** |
| 109,580 | **202.46** | **23.28** |
| 117,764 | **203.18** (`on-direct`) | **23.31** |
| 148,476 stress | **152.03** | **20.51** |

The raw 117,764-token JSON records 384 generated tokens, 596.10 s total wall, ~56.98 GiB system-wide wired memory after the run and ~11.37 GB swap after. The 148,476 stress run reaches ~58.09 GiB system-wide wired and ~11.57 GB swap.

Q8 KV controlled A/B around 77K:
- F16/F16: **209.78 PP / 24.01 TG**
- Q8/Q8: **211.00 PP / 23.92 TG**
- system-wide wired memory drops by roughly **1.0 GiB** with Q8 KV.

The repository separately preserves a 39-generation real Pi coding session, but its mixed-workload task TG varies materially with request shape/page residency; the controlled JSON sweep is the correct context-scaling anchor.

Classification: **recovered exact target-generation hardware / exact model family / near-target precision / modern long-context physical receipt. Not exact Q5, not dual-M1/TB4.**

### Project 51 interpretation

This is materially stronger than the previous M1 Q2/IQ1 anchors:
- it is **4.27 bpw**, much closer to the Q5-class goal;
- it uses modern indexed QSA and direct PLE;
- it reaches the actual neighborhood of the headline context target;
- it generates 384 output tokens rather than a tiny capacity smoke;
- MTP is **off**, so the low-20s decode rate is the target-only physical path.

It cannot be doubled:
- Q5-class will be heavier than 4.27 bpw;
- the machine is under substantial memory pressure and uses swap;
- PP2 over TB4 introduces stage balance and activation handoff costs;
- B1 decode cannot achieve ideal 2x PP scaling without useful multi-row/speculative overlap;
- this is a custom llama.cpp fork.

But it removes a major uncertainty: a current M1 Max path can sustain about **23 TG at ~118K** and about **20.5 TG at ~148K** near the intended precision class before MTP. That is why 40@128K moves to about **65%**, not because of a simple 2x extrapolation.

For PP, a single M1 already sustains roughly **203 PP at ~118K** near target precision. A balanced dual-stage long-prefill pipeline plus the known modern prefill headroom makes **400 PP materially more plausible**, so confidence moves to about **75%**.

## NEW — vLLM #57616: plain native MTP was silently disabling prefix cache

PR created **2026-09-18 19:22:59 UTC**.

Exact evaluated setup:
- DGX Spark / GB10
- Qwen3.8-Flash-Next NVFP4
- MTP k=3
- align mode
- prefix caching on
- piecewise CUDA graphs
- 262K context
- disk-backed PLE in the decode benchmark.

Mechanism:
- native/plain MTP shares target KV and has **no separate draft KV group**;
- the cache coordinator saw “no draft group identified” and conservatively marked **all groups as EAGLE**;
- replay-boundary arithmetic then produced only boundary 0, so `cache_blocks()` inserted nothing;
- repeated byte-identical prompts therefore had zero cache hits.

Measured:
- nightly, no workaround: prefix hits **0**, repeat 4,137-token TTFT **3.6 s every time**
- broad workaround: **6400/12778 = 50.1%** hits, TTFT **3.6 -> 1.6 s**
- targeted fix: same **50.1%** hit rate and **3.6 -> 1.6 s**, while retaining the trailing-block pollution guard
- MTP acceptance remains **44.5%**
- 8-category decode median remains about **38.9 TG** with the disk-backed PLE setup.

Classification: **new exact same-model-family native-MTP/cache evidence; wrong hardware for target performance transfer.**

Project 51 rule:
Native model-owned MTP should be modeled as speculation over **target state** unless an actual separate draft state exists. EAGLE/DFlash/draft-model cache fallbacks must not be applied merely because “speculation is enabled.”

Prefix-cache qualification must include:
- plain native MTP
- separate-draft speculation
- MTP on/off
- repeated prompt TTFT/hit counters
- trailing-block state correctness.

## NEW — vLLM #57608: token-indexed PLE must stage after draft proposal

Issue created **2026-09-18 18:40:05 UTC**.

Setup:
- DGX Spark GB10
- Qwen3.8-Flash-Next NVFP4
- MTP k=3
- disk-backed n-gram PLE
- FULL_DECODE_ONLY vs PIECEWISE graphs.

Problem:
`prepare_inputs` runs before MTP draft proposal. Verify input includes the newly proposed draft tokens, so PLE rows staged at `prepare_inputs` are missing the draft tail.

Measured:
- correct in-forward/piecewise PLE staging acceptance: **44.5%**
- too-early pre-`execute_model` staging: **34.6%**
- visible output-quality regression accompanies the acceptance loss
- piecewise correct execution costs about **7% decode throughput** versus FULL_DECODE_ONLY on this setup.

Classification: **new exact same-model-family PLE/MTP state evidence; non-Apple hardware.**

Project 51 rule:
Any token-indexed side data used by verify—PLE rows, token-dependent QSA side state, etc.—must be staged against the **final verify token sequence after draft proposal**. Draft proposal -> verify is an explicit state/preparation frontier.

Do not “optimize” host I/O by staging from target-only input IDs if speculation will append IDs later.

## NEW — vLLM #57605: lookahead can corrupt recurrent state at page boundaries

PR created **2026-09-18 18:01:04 UTC**, rebased again before cutoff.

Failure:
- Mamba/GDN align mode
- prefix caching
- lookahead/speculative capacity
- prefill chunk ends exactly on a state-page boundary.

Two corruption modes:
1. no next page materialized, so a state write targets a recycled stale block;
2. lookahead-inflated padding displaces the actual running-state column with a null slot, and the next chunk chains from null state.

Physical reproduction:
- 4-node Arm / Thor SM110 cluster
- GLM-5.3-Flash
- NVFP4
- MTP
- prefix caching
- chunked prefill.

Before:
- boundary-ending chunks produce deterministic **0% spec-decode acceptance** from first decode step.

After:
- full prompt-size ladder remains coherent;
- **22-turn conversation / 360K prompt tokens** remains coherent;
- reported mean acceptance length ~**3**.

Classification: **new recurrent-state boundary correctness evidence; model/hardware differ, mechanism strongly transfers.**

Project 51 action:
Add page-aligned recurrent-state fixtures with lookahead enabled. Verify:
- next-page block is physically materialized before boundary write;
- null padding cannot displace running state;
- worker running-state column equals scheduler/block-table identity;
- multi-turn acceptance does not collapse after exact page boundaries.

## NEW — llama.cpp #29092: fused GDN leaks recurrent state across requests

Issue created **2026-09-18 17:37:58 UTC**.

Models:
- Qwen3.6-35B-A3B Q4_K_M
- **Qwen3.8-27B Q4_K_M**
- HIP/ROCm / gfx1151 Strix Halo.

With the fused Gated DeltaNet operation enabled, a reused server slot can carry the previous request's recurrent state into the next request.

Three-request deterministic probe:
- R1 contains synthetic document A and returns A correctly;
- R2 has a different document B but restored prefix checkpoint; output contains A's abstract and a verbatim A clause;
- R3 deliberately breaks the prefix so the runtime performs full `memory_seq_rm [0,end)` and reprocesses from position 0; output **still contains A**.

Control on the older tested build:
- moving layer 0 to CPU disables the fused GDN path;
- the leak disappears.

The reporter varied graph reuse, HIP graphs, context checkpoints, cache RAM, context shift, F16 KV, expert placement and slot settings; only fused-GDN disable clears the older-build repro.

29-document warm-runner observation:
- contamination accumulates;
- output eventually degrades into unterminated generation;
- ubatch changes onset rather than mechanism.

Cost of the workaround on qwen3.6:
- prompt latency per token: **0.89 -> 1.10-1.12 ms (+24%)**
- decode latency per token: **18.3 -> 23.0-23.7 ms (+26-29%)**.

Classification: **new serious non-Apple recurrent-state isolation evidence, including Qwen3.8-27B.**

### Project 51 action

Cross-request state isolation becomes a mandatory **privacy/correctness gate**:
- disjoint synthetic vocabularies/documents
- same server slot, repeated requests
- checkpoint restore path
- complete cache/state clear path
- cancellation/preemption path
- MTP on/off
- warm runner over many requests.

After a logical reset, hash/snapshot GDN/recurrent state and require zero dependence on prior-request content. A clean text response alone is not enough; use state/logit probes where possible.

## NEW — oMLX #3742: mlx-vlm upgrade halves Lightning-MTP acceptance

Issue created **2026-09-18 16:47:25 UTC**.

Model/hardware:
- Qwen3.6-35B-A3B-oQ6-mtp
- M3 Ultra 80 GPU / 512 GB
- pp16384 / tg128
- custom kernels rebuilt at every bisect point.

Bisected transition:
- parent `76d19fed`, mlx-vlm `78b96eb5`: mean TG **116.7**
- `a1663771`, mlx-vlm `3fb24e90`: **70.0**
- current dev4: **73.1**.

Telemetry:
- acceptance **72.5% -> 34.7%**
- tokens/cycle **2.48 -> 1.44**
- backbone/cycle **18.16 -> 18.47 ms**
- prefill unchanged around **2740-2757 PP**
- no distribution overlap: old minimum 102.2 > new maximum 77.0.

The commit changes speculative verify/rollback integration, including delegation of rollback to upstream mlx-vlm.

Classification: **new exact oMLX speculative-state regression, different Qwen model but highly relevant mechanism.**

Project 51 action:
MTP acceptance is not merely a workload statistic; a large acceptance discontinuity at unchanged target-cycle time can indicate **state rollback/verify correctness divergence**.

Runtime upgrades must replay frozen MTP acceptance/token-cycle fixtures before promotion.

## NEW — oMLX #3748: dev4 can fail to load a Flash-Next custom qwen4_exp pack

Issue created **2026-09-18 20:45:08 UTC**.

Model:
- `pipenetwork/Qwen3.8-Flash-Next-MLX-mixed-4_8bit`
- ~103.9 GB
- PLE mmap
- custom `qwen4_exp.py`.

Reported:
- dev2 loads/runs at approximately **20 TG**
- dev4 / mlx-vlm 0.7.1 calls `custom_model.ModelConfig.from_dict`
- the custom module has no `ModelConfig`
- VLM load fails; LLM fallback is blocked by the trust-remote-code gate; requests return 409.

This is separate from the dev4 memory regression already recorded.

Classification: **new same-model-family loader/version regression; not target performance evidence.**

Project 51 action:
Keep exact runtime dependency pins in all Flash manifests. “Same model + same command” is not a reproducible configuration if mlx-vlm/mlx-lm pins change underneath it.

## UPDATE — distributed autotune cache is rank-specific, not identical

vLLM #57635, created **2026-09-18 21:26:58 UTC**, provides a stronger field diagnosis than the earlier generic cache-sync proposal.

8x H100 / TP8+EP8 field report:
- rank 0's persisted FlashInfer file contains keys for `ep_rank=0`;
- on restart, rank 0 hits those keys while ranks 1-7 enter tuning collectives;
- 18 crash-loop restarts reproduce the hang over 8.5 hours;
- clearing only the autotune-cache directory changes the next start: all ranks retune for ~1 s, engine reaches READY in ~20 s;
- reported as **19 identical failures, then one success with one variable changed**.

The proposed fix persists per-rank files and loads them only if every rank's expected file exists.

This corrects an over-simple earlier Project 51 formulation: distributed tuning caches need not be byte-identical when the key includes rank/stage identity.

Durable rule:
- same source/runtime/topology manifest
- same tuning schema/epoch
- complete expected per-rank/per-stage cache set
- each rank loads only its role's cache
- group-wide all-hit or all-retune decision.

## 27B side finding — exact 2-bit Bonsai verify path on M4 Max

mlx-serve commit `bbf652a589d8b7dc2d7e8299581003c14a1bf229`, **2026-09-18 21:30:45 UTC**.

Prism Ternary-Bonsai-2-27B:
- M4 Max
- exact 2-bit GEMV
- MTP depth 2
- verify M=2..3 uses half2 storage widened to f32 FMA.

Reported:
- 3-row trunk forward: **35.4 -> 32.2 ms**
- at 4K: **38.3 -> 34.7 ms**
- S=2: **28.6 -> 24.8 ms**
- llmprobe 512/1K/2K decode: **73.5 TG vs 67.9**
- prefill: **271 PP vs 255**.

Classification: **new exact M4/ternary/short-context 27B transfer evidence; not an M1 target receipt.**

Keep it on the 27B extreme-compression watchlist; do not alter the M1 27B target from this result.

## Strict-window negative / no-promotion findings

- vLLM #57575 merged in this window, reserving sparse-prefill workspace before KV-cache sizing. The mechanism was already recorded in the previous watch; merge time does not make the old measurements new.
- vLLM #57603/#57604 add DeepSeek-V4.1 GPU overlap/staging optimizations; they are non-Apple transfer evidence and do not move the DS4 dual-M1 target.
- vLLM #57590 still had no completed performance/accuracy table for the new rope-free sparse-MLA ROCm backend at the relevant cutoff.
- DS4 default branch had no new substantive commit in the strict window. #1056 had no new benchmark beyond the corrected M1 A/B already recorded.
- Fresh HF/community searching found **no exact dual M1 Max / TB4 / Q5 physical receipt**.
- Current M4/M5 oMLX Q5 benchmark aggregators are useful stronger-chip context but do not supersede the recovered exact-M1 4.27-bpw receipt for M1 planning.

## Target / confidence decision

### Flash-Next dual M1 Max

**Keep numeric targets: 40 TG @ ~128K / 400 cold PP. Keep Q5-class as canonical quant.**

Updated TG planning ladder:
- >=30 TG: **~95%**
- >=35 TG: **~85%**
- >=40 TG: **~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20-25%**.

Updated PP ladder:
- >=250 PP: **~98%**
- >=300: **~95%**
- >=350: **~88%**
- >=400: **~75%**
- >=450: **~55-60%**
- >=500: **~40%**
- >=600: **~15-20%**
- >=700: **~5-8%**.

Why confidence moves:
- exact M1 Max / modern long-context / near-target precision now has a raw controlled anchor at **23.31 TG / 203.18 PP @117,764** with MTP off;
- the same physical path remains above **20 TG at 148K**;
- this removes much of the uncertainty around modern M1 indexed-QSA/direct-PLE viability near headline context.

Why confidence does not move higher:
- target quant is Q5-class, not 4.27 bpw;
- exact dual-M1/TB4 behavior is still unknown;
- the M1 long-context receipt uses substantial system swap;
- single-request PP2 decode depends on meaningful multi-row/MTP overlap rather than simple stage doubling;
- distributed recurrent/QSA/cache correctness remains a real qualification risk.

## New/strengthened qualification rules

1. **Near-target single-M1 ruler:** add a 4.x/5.x-bpw 96K/118K/128K/148K sweep with 384+ generated tokens before cluster tuning.
2. **Native-MTP cache semantics:** plain MTP shares target state unless an actual draft state/group exists.
3. **Post-draft token-indexed staging:** PLE/QSA side data for verify is prepared from final verify IDs.
4. **Page-boundary lookahead fixture:** exact state-page boundaries + speculation must preserve running-state ownership.
5. **Cross-request state privacy:** reused slots must prove zero recurrent-state leakage across users/requests.
6. **MTP acceptance as state-health metric:** frozen acceptance/token-cycle fixtures gate runtime upgrades.
7. **Rank-role-aware autotune manifest:** per-rank cache payloads may differ; schema/epoch/topology/completeness must agree.
8. Existing effective-setting, chunk-parity, memory-staircase, autotune-stability, workspace-admission and admission-latency gates remain.

## Hard freshness boundary

`2026-09-18 21:34:45 UTC`
