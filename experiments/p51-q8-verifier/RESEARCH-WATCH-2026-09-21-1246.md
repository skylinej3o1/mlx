# Project 51 research watch — 2026-09-21 12:46 ET

**Freshness boundary checked:** previous hard boundary **2026-09-21 12:18:58 UTC**. Search ran through the user's cutoff **2026-09-21 16:46:31 UTC**.

## Decision

**No numeric target or confidence change.**

The highest-value additions are:
- Splash's newly surfaced native-Q8 Qwen3.8-27B measurements, which give Project 51 a much clearer model-specific speculative-runtime blueprint but still do not run on M1/Apple7;
- a fresh Splash agentic-behavior report showing that identical weights plus much higher tok/s can still produce dramatically worse multi-turn trajectories;
- fresh oMLX evidence that warm prefix restoration can preserve TTFT while silently losing MTP decode acceleration;
- a new batched-DFlash/small-M verify-kernel path showing large multi-request gains without moving B1.

These findings change the **P69->P70 experiment plan and certification gates**, not the canonical Flash or 27B target numbers.

## RECOVERED / newly surfaced — Splash native-Q8 Qwen3.8-27B

Community publication:
https://www.reddit.com/r/LocalLLaMA/comments/1wmbbf9/splash_engine_qwen3827b_in_native_8bit_at_3755/

Implementation provenance:
https://github.com/npanj/splash/tree/q8
Q8 implementation commit: 5ce51ee76529195d4ddfb5d8ffdcdffd172a75c0 (2026-09-20 05:36:58 UTC)

Because the implementation commit predates the prior freshness boundary and the Reddit result exposes only a Sep-21 publication date rather than a reliable exact post time, this is recorded as **recovered mechanism evidence**, not as an exact-window timestamped code change.

### Reported hardware and results

- M5 Pro, 64 GB unified memory.
- Qwen3.8-27B native 8-bit target, ~27 GB.
- Splash fork adds native group-64 Q8 tiled Metal kernels and Q8 package/schema support.
- Five short task prompts at temperature 0:
  - native Q8 Splash-HQ: **36.9 TG average**;
  - same 8-bit base weights under MTPLX: **26.5 TG average**;
  - compressed-Q8 Splash arm: **36.5 TG average**;
  - peak reported Splash-HQ prompt: **54.8 TG** on the math case.
- Long-session telemetry reaches **190,016 tokens**. Representative deep-context decode samples include 27.1 @34.6K, 30.1 @83.4K, 24.8 @106K, 33.3 @180K, 31.9 @187.6K, 21.1 @188.5K and 32.0 @190K; cache-hit samples can spike higher.

### Interpretation

This is strong evidence that native Q8 can remain attractive under speculative decoding because the objective is not minimum bytes alone: target quality can improve draft acceptance enough to offset some additional memory traffic.

However, the post's broad zero-quantization-degradation / reasoning-cliff language is **not a quality certificate**. The detailed reasoning example is narrow, and Project 51 still requires source-equivalence/agentic evaluation.

### M1 transfer limit

Current Splash device validation requires Apple GPU family >=9 (M3-or-newer). The Q8 path uses newer Metal tensor/matmul machinery and is not an M1/Apple7 binary we can simply enable by removing a guard.

Therefore:
- do **not** transfer 36.9 or 54.8 numerically to M1;
- do **not** change the single-M1 27B target from 25 TG;
- do use Splash as an architecture/mechanism reference.

### Project 51 action

Keep P69B13 next in the certified exact-verifier chain. Then create a separate **P70-SPLASH-MECHANISMS** campaign:

1. measure full speculative cycle time, accepted tokens/cycle and depth distribution;
2. measure CPU/dispatch/materialization gaps versus GPU-active verifier time;
3. measure hot weight bytes per accepted token;
4. only if the dominant loss is in verifier execution, prototype one Apple7-specific persistent/small-M Q8 kernel on a dominant projection;
5. promote nothing without exact-output/behavior and MTP acceptance checks.

A crude application of Splash's same-weight +39% runtime delta to the current exact M1 verifier's ~19.55 TG would land near ~27 TG, which is a **sanity-check hypothesis only**, not evidence.

## NEW — Splash #90: throughput can improve while agent behavior gets much worse

Source:
https://github.com/incoai/splash/issues/90
Created: **2026-09-21 15:55:42 UTC**

Setup:
- M5 Max, 36 GB;
- Splash 1.0.1 vs LM Studio;
- same Qwen3.6-35B-A3B weights;
- Claude Code through Anthropic Messages API;
- identical TypeScript implementation/test task in clean worktrees.

Reported results:

| engine/run | turns | wall clock | outcome |
|---|---:|---:|---|
| LM Studio | **60** | **4m38s** | completed, checks passed |
| Splash 1 | 110 | 34m09s | completed |
| Splash 2 | 113 | 40m00s | timeout |
| Splash 3 | 207+ | — | manually stopped |

At the same time Splash reported **232 TG**, ~3,400 PP, **91.8% prefix-cache hit rate**, ~1.0 s cached TTFT at an 82K prompt, and accepted longer context than the comparison engine.

The reporter checked matching quantization metadata/weights, identical harnessing, no engine failures/retries, no obvious chat-template difference in this client path and no severe memory pressure. The proposed cause — an approximate speculative/sampling path changing the target distribution — is **a hypothesis, not established root cause**.

### Durable rule

Runtime equivalence must be certified as a behavioral property, not inferred from checkpoint identity.

Project 51 evaluation must include:
- multi-turn coding-agent trajectories;
- tool-call sequence and argument correctness;
- turn count / completion success;
- outcome correctness;
- temperature-0 token parity where exactness is claimed;
- sampled-distribution tests when probability-preserving speculation is claimed.

A runtime can be much faster per token and still be slower or worse per completed agent task.

## NEW — oMLX warm-prefix MTP decode regression evidence

Source:
https://github.com/jundot/omlx/issues/3770

The issue itself predates this pass, but **new comments inside the exact window** materially narrow the mechanism.

### No-cache recovery

At 14:49 UTC, an M5 Max reproduction on current main after the known fixes reports:
- pre-#3719 production: **92.6 code / 59.1 prose TG**;
- dev4 pre-fix: **68.2 / 51.2**;
- current main + all fixes: **100.7 / 77.4**.

So the current no-cache path is not merely recovered; on that workload it exceeds the older production build.

### Warm-cache regression

At 15:17 UTC, an M3 Ultra reporter resolves an apparent disagreement:

| mode | dev3 | current main + fixes |
|---|---:|---:|
| no-cache decode | ~110 | **~119** |
| repeated-prompt cache-hit decode | **~168** | ~115 |

The claim is that dev3 restored some MTP-related warm state that current main no longer recovers, so prefix-cache hits no longer produce the same decode acceleration even though cold/no-cache decode is faster.

This is especially relevant to Project 51's agent control-plane design because our real workload is dominated by multi-turn warm sessions.

### Durable rule

Warm-session performance identity includes more than target prefix/KV restoration.

Benchmark separately:
- genuine cold;
- warm target prefix only;
- warm target prefix + recurrent/QSA state;
- warm target + draft/MTP state.

Record restored vs recomputed tokens/state and MTP tokens/cycle after wake/rewind. A restore path that improves TTFT but does not restore speculative decode acceleration is incomplete.

## NEW — oMLX #3797 batched DFlash + small-M verify kernels

Source:
https://github.com/jundot/omlx/pull/3797
Created: **2026-09-21 14:06:27 UTC**

M3 Ultra, Qwen3.8-27B:

| path | B=1 | B=2 | B=4 |
|---|---:|---:|---:|
| standard batching | 37.0 | 68.2 | 106.9 |
| old single-stream DFlash | 82.0 | — | 83.7 |
| batched DFlash2 block-4 | **84.5** | **119.9** | **160.7** |

Kernel-only Lightning-MTP comparison on oQ4e-mtp:
- B1: 82.4 -> 82.1;
- B2: 96.7 -> 122.5;
- B4: **112.0 -> 166.3**.

The new verify kernel handles 7..24 rows and 4/5-bit affine weights, dequantizing a K chunk once and multiplying it against every row.

### P51 relevance

This is not a B1 target improvement — B1 is effectively flat. It is strong evidence for future **concurrent-agent** serving:
- verify kernel shape should key on total rows = batch x speculative block;
- shared weight traversal matters;
- one independent speculative engine per request leaves large throughput on the table.

No numeric B1 target changes.

## NEW/confirmed — pre-M5 numerical portability: DS4 #1039

Source:
https://github.com/antirez/ds4/issues/1039
Fresh confirmation comment: **2026-09-21 16:06:16 UTC**

An M1 Ultra previously failed a model-free router numerical check while the same check passed on M5 Max. The unstable expression was a small-logit softplus implemented as log(1 + exp(x)); around x~-11.9, FP32 cancellation/rounding produced roughly a **0.5% router-probability error** in the reported case.

PR #1044 replaced the small-logit path with a log1p-style accurate approximation. The Sep-21 exact-window confirmation reports current main passing the full router test **3/3 on M1 Ultra**.

### P51 relevance

When we prototype Apple7-specific verifier/router kernels, use numerically stable elementary functions and compare to an accurate oracle. Works-on-M3/M5 is not enough to certify M1 arithmetic.

## MINOR — llama.cpp Flash prefill-copy optimization

Commit:
https://github.com/ggml-org/llama.cpp/commit/f4e276a2066a40cd200db17c1131826d6c0c7a94
Timestamp: **2026-09-21 16:00:51 UTC**

On Qwen3.8-Next-Flash IQ3_XXS / gfx1151, vectorizing contiguous conversion gives:
- pp2048: roughly **+1.26%**;
- tg128: roughly **+0.14%**;
- output bit-identical.

This is useful negative separation: a memory-copy optimization can matter to prefill while being essentially irrelevant to decode. Do not mix PP and TG optimization narratives.

## Checked with no qualifying target evidence in this window

- antirez/ds4: no new commits; #1039 only supplied the fresh M1 confirmation above.
- vllm-project/vllm: many commits/PR updates. The DeepSeek-V4 adaptive-verification merge happened in-window, but its performance data predate this cutoff, so merge time is not treated as new evidence. No exact M1/Flash target receipt.
- jundot/omlx: no branch commits in the interval; exact-window comments/PR #3797 are captured above.
- ddalcu/mlx-serve: only test/chore commits in the interval; no qualifying new Qwen TG/PP receipt.
- ggml-org/llama.cpp: the direct Flash prefill result above is the only material in-window model measurement; other commits were unrelated or tooling.
- incoai/splash: no commits in-window; new issue #90 is captured above.
- kadirbalalan/qwen38-mac-fast and visible kadirbalalan/llama.cpp fork: no commits in-window.
- youssofal/MTPLX: no commits in-window.
- localai-org/apex-quant: no commits in-window.
- ikawrakow/ik_llama.cpp: README/AUTHORS-only commits; no runtime/quant evidence.
- Intel AutoRound: one unrelated ARK compilation-memory change; no Qwen3.8/M1 evidence.
- ByteShape, Unsloth, Bartowski, EXL3, PrismML: checked current public surfaces; no substantive release/measurement with a qualifying evidence timestamp inside this 4h27m window.

## Target / confidence impact

Unchanged:
- Flash-Next production quality floor >=38 AA-class behavior; preferred 39-40.
- Flash headline: **40 TG @ ~128K**.
- Flash cold PP: **400**.
- Current Flash confidence ladder unchanged.
- Single-M1 Qwen3.8-27B working target: **25 TG**.
- 5070 Ti and DS4 targets unchanged.

What changed is the **next-work ordering**:
1. finish P69B13 from existing exact profiling;
2. instrument cycle/acceptance/dispatch/warm-state metrics;
3. branch P70 for Splash-style Apple7 experiments;
4. add multi-turn agentic behavioral equivalence to runtime promotion gates;
5. add warm-prefix speculative-decode restoration as a separate benchmark axis.

## New hard boundary

**2026-09-21 16:46:31 UTC**
