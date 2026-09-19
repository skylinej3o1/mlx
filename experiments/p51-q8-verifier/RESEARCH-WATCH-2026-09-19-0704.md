# External runtime watch — 2026-09-19 07:04 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-19 07:51:54 UTC` through `2026-09-19 11:04:27 UTC`.

PRs, issues, comments/reviews, and default-branch commits were screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Fresh Qwen3.8-Flash-Next Hugging Face/community/web surfaces were also searched. Evidence time means substantive source/measurement time, not crawler, merge, label, bot or rebase timestamps.

## Executive result

**No exact dual-M1-Max/TB4 custom-Q5-class receipt appeared. Numeric targets and planning confidence stay unchanged.**

Current Flash-Next plan:
- **40 TG sustained @ ~128K: ~60%**
- **400 cold PP: ~70%**
- deployment design: **custom ~4.6-4.9 hot-trunk BPW**
- oQ5e: quality/certification comparator
- oQ4e: aggressive speed comparator
- PLE and MTP precision tracked separately.

The most important change in this window is upstream code evidence: llama.cpp merged new Metal fusion machinery whose **qwen4exp fusion baseline explicitly activates on the exact graph family used by Flash-Next**. This is genuine post-Kadir work, but no direct Flash-Next performance A/B has been published yet.

## NEW — upstream qwen4exp-active Metal MoE / SSM fusion landed

llama.cpp PR #28948 merged as commit:

`5b59b83f4e2101ea173d4f853a0522d9971f48c6`

at **2026-09-19 10:14:44 UTC**.

It adds:
- top-k MoE routing fusion
- MoE weighted-reduction fusion
- RMS_NORM + SCALE fusion
- SSM_CONV + SiLU fusion
- function-constant specialization for runtime variants
- safer/pattern-driven fusion dependency tracking
- cross-device Metal-copy synchronization fixes.

Critically, the merged Metal fusion baseline explicitly contains `qwen4exp` entries for:
- `MUL+ADD`
- `RMS_NORM+SCALE`
- `SOFT_MAX+ARGSORT+GET_ROWS+SUM_ROWS+CLAMP+DIV`
- `SSM_CONV+UNARY`
- plus existing GDN/HC-style patterns.

Therefore this is **direct architectural applicability**, not merely “similar model” inspiration.

### Published performance — related Apple models, not Flash-Next

M2 Ultra:
- Qwen3.5-MoE 35B Q4: **90.26 -> 104.87 TG (+16%)**
- Qwen3.5-MoE 35B Q8: **83.50 -> 96.62 (+16%)**
- Qwen3.5 dense 27B Q4: **26.04 -> 27.31 (+5%)**
- Qwen3.5 dense 27B Q8: **21.88 -> 22.79 (+4%)**.

M5 Max:
- Qwen3.5-MoE 35B Q4: **104.70 -> 117.75 TG (+12%)**
- Qwen3.5-MoE 35B Q8: **95.44 -> 106.73 (+12%)**
- Qwen3.5 dense 27B Q4: **25.57 -> 26.60 (+4%)**
- Qwen3.5 dense 27B Q8: **18.58 -> 19.13 (+3%)**.

Prefill gains are typically smaller, roughly 0–7% in the reported tables.

Classification: **new exact upstream Metal implementation evidence with qwen4exp graph applicability; performance measurements are transfer evidence from related models/hardware.**

### Project 51 interpretation

This patch post-dates Kadir's frozen September 8 runtime.

It gives us a concrete reason to believe some additional single-node headroom exists after his benchmark, but the exact percentage is unknown because:
- no Qwen3.8-Flash-Next A/B was posted;
- Kadir already carried substantial custom Qwen4Exp Metal work;
- conceptual overlap with his custom HC/QSA/MoE paths may exist.

Therefore:
- **do not add +12–16% to Kadir**
- retain the existing **~5–15% likely single-node target-only headroom**, with the new merge supporting the upper end of that range
- create a future controlled ruler: **Kadir frozen runtime -> current/upstream fusion backport**, same artifact, prompt, context, PLE state and QSA path.

No 40-TG probability change until that physical A/B exists.

## NEW — upstream qwen4exp HC Metal support landed

llama.cpp PR #29000 merged as commit:

`59fc5a1ca3842241dd53617ae2ae030c1a015061`

at **2026-09-19 08:27:31 UTC**.

It adds Metal support for:
- gated qwen4exp `hc_pre` with per-element sigmoid gate and scale
- identity qwen4exp `hc_post` where each stream keeps its own residual.

No performance measurements were published.

Classification: **new direct qwen4exp backend-coverage evidence, not speed evidence.**

Kadir already had custom qwen4exp HC work, so this is primarily relevant to making modern upstream a viable clean baseline rather than proving additional speed by itself.

## NEW — severe same-family runtime regression on vLLM

vLLM #57680, created **2026-09-19 09:01:17 UTC**.

Setup:
- Qwen3.6-35B-A3B-FP8
- 1x H100 NVL
- no speculation
- same advertised attention/MoE/cudagraph configuration
- vLLM 0.26.0 vs 0.29.0.

Median decode:
- c=1: **148.3 -> 41.4 TG**
- c=12: **1295.0 -> 362.3 aggregate TG**
- ITL: **6.68 -> 23.88 ms**.

Prompt length from ~120 through ~12K does not change the regression materially.

CPU profiler:
- `aten::copy_` calls: **10,139 -> 6,137**
- mean per call: **109.5 -> 563.1 us**
- total CPU-side copy wait: **1.099 -> 3.455 s**.

The reporter interprets this as GPU-completion wait rather than extra copy/dispatch work.

0.29 also alternates request-by-request between approximately **41.4 and 60.8 TG**, while older releases are stable to ~1%.

Classification: **new non-Apple hybrid-Qwen runtime-regression evidence.**

Project 51 action:
- dependency/runtime SHA remains benchmark identity;
- preserve raw repeated-run distributions;
- if measurements form two stable modes, report both modes rather than hiding them behind one median;
- selected backend names are insufficient proof that two runtime releases execute with equivalent cost.

This reinforces existing rules; it does not move target confidence.

## NEW — agent reasoning replay can amplify a target-model failure

oMLX #3758, created **2026-09-19 09:02:03 UTC**.

DeepSeek-V4.1-Flash-oQ4e-mtp in a long agentic session enters a stochastic reasoning loop. One captured loop:
- **40,583 generated tokens**
- **7,003 MTP cycles**
- **5.80 tokens/cycle**
- **99.4% MTP acceptance**.

The high acceptance is not an MTP error: the target itself predicts the repetitive trajectory.

The serving/client path then replays the enormous historical `reasoning_content` back into later prompts. A matched probe showed adding about 200 tokens of historical reasoning increased rendered prompt tokens from **42 to 382**, almost the same as placing that text in ordinary content.

Compaction removes the contaminated turns and temporarily restores behavior; later loops can poison history again.

Classification: **new agent-serving transfer evidence, not Flash performance evidence.**

Project 51 action:
- do not replay unlimited private reasoning into future agent turns;
- cap/strip reasoning history unless explicitly required by the target format;
- treat high MTP acceptance as a performance/correctness signal, **not a semantic-health guarantee**;
- add runaway/repeated-ngram termination guards to long autonomous-agent qualification.

## STRICT-WINDOW negative findings

- No new exact 2x M1 Max / TB4 Qwen3.8-Flash-Next performance receipt.
- No direct Qwen3.8-Flash-Next benchmark was attached to the newly merged llama.cpp Metal fusion patch.
- No new DS4 or mlx-serve default-branch commit in the strict window that changes the Flash target.
- llama.cpp #29110, the high-value Metal small-row MTP verify PR from the prior watch, received no new physical M1 result in this window.
- oMLX #3755, the deep-context dev4 Flash regression from the prior watch, received no new diagnosis/fix before cutoff.
- Fresh HF/community searching surfaced no new exact dual-M1 Apple quant receipt.

## RECOVERED / corroborating quant evidence — not new-window target evidence

Fresh community searching surfaced additional examples supporting the component-wise quant accounting already adopted:

- A current ExLlamaV3 4.05-whole-BPW build explicitly uses **6-bit lm_head, 8-bit MTP and 6-bit PLE**, demonstrating again that headline BPW can hide much higher precision in non-trunk components.
- Baekpica's Q5 SSD-PLE artifact explicitly reports **resident backbone effective BPW = 6.0659** while keeping the 51.2B PLE table separately at **BF16 on SSD**. It is a DGX Spark / ds4 artifact, not Apple evidence.
- That same older campaign reports extensive Q5-backbone optimization and ~28–30 TG MTP decode on DGX Spark; these values are not transferred to M1.

These reinforce the Project 51 accounting convention but do not change the custom **4.6-4.9 hot-trunk** design target.

## Target / confidence decision

**No change.**

Flash-Next dual-M1 Max:
- **40 TG @ ~128K: ~60%**
- **400 cold PP: ~70%**.

The new qwen4exp-active upstream Metal fusions improve our confidence that Kadir's September 8 runtime is not the final software ceiling, but absent a direct Flash A/B they are not sufficient to numerically move the forecast.

## New/strengthened qualification rules

1. **Post-Kadir upstream ruler:** benchmark Kadir frozen runtime versus current/upstream qwen4exp fusion stack under identical model/context/QSA/PLE conditions.
2. **Fusion applicability != transferable speedup:** direct graph-pattern coverage is stronger than generic transfer evidence, but still requires physical model-level A/B before percentage credit.
3. **Preserve multimodal runtime distributions:** alternating fast/slow execution modes must be reported explicitly.
4. **Reasoning-history hygiene:** private/internal reasoning is not automatically safe or useful conversation history for autonomous agents.
5. Existing component-wise quant, effective-setting, chunk-parity, MTP-state, distributed-geometry, deep-context and state-isolation gates remain.

## Hard freshness boundary

`2026-09-19 11:04:27 UTC`
