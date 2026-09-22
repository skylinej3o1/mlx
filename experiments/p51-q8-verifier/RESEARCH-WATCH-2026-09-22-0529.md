# Project 51 primary-lane research watch — 2026-09-22 05:29 ET

**Freshness boundary checked:** previous hard boundary **2026-09-22 06:05:53 UTC**. Search ran through the user's cutoff **2026-09-22 09:29:14 UTC**.

## Decision

**One planning-confidence change:** single-M1 Qwen3.8-27B mature **>=25 TG** rises from **~55-60% to ~65%**; >=22 TG rises from ~80% to ~90%. Working targets themselves do not change.

No numeric change to dual-M1 Flash, 5070-Ti 27B, or cold-PP targets.

## NEW — exact Apple7/M1 Max Splash result

Source: incoai/splash issue #95, created **2026-09-22 07:40:26 UTC**; branch commit `paperniuk/splash@8b76480b0e9a`, authored **07:30:16 UTC**.

Hardware/model:
- Apple M1 Max, 32-core GPU, 64 GB;
- macOS 26.6.2 / Xcode 27;
- `incoai/Qwen3.8-27B-Splash`, Q4 package;
- Apple GPU family 7.

Important result: every Splash startup capability check except the hard-coded family>=9 gate already passes on M1 Max — Metal 4, placement-sparse support, 32 KiB threadgroup memory, 1024 threads/threadgroup, and working-set requirement. The reporter says the model needs **no new kernel implementations** to run correctly; it needs an Apple7-specific policy.

Measured policy from `tune-kernels`:
- prefill plain/residual N128: 4 -> 8 simdgroups, **+22-32% per-layer GPU gain**;
- one-lane decode eligible projections: Split64 x8/full-grid, **+20-53% per-layer GPU gain**;
- fused-up prefill and vocabulary projection retain their old choices.

End-to-end one-request HTTP, reasoning off:

| | Untuned Apple7 | Tuned Apple7 |
|---|---:|---:|
| prompt A decode | 23.2 | **25.7 TG** |
| prompt B decode | 14.0 | **15.4 TG** |
| prompt C decode | 23.7 | **25.8 TG** |
| three-prompt mean | 20.3 | **22.3 TG** |
| 7,244-token cold prefill | ~34 PP | **~49 PP** |
| 7,244-token TTFT | 211.6 s | **146.6 s** |

The tuned policy's greedy output was byte-identical to the untuned Apple7 build across the reporter's three single-request and three-concurrent-request checks.

### Critical correctness finding

Simply letting Apple7 inherit Apple9's `LinearTile::Simdgroup` decode tile is **wrong**. The isolated sgmatrix test passes 672 cases, yet the real 27B model emits obvious greedy-text corruption and falls to 8.6-9.8 TG, consistent with destroyed DFlash acceptance. Multi-lane M24 candidates also fail tuning parity.

Durable P51 rule: **real-model parity is a promotion gate for Apple7 kernel policy. Kernel-unit correctness is necessary but not sufficient.**

### P70 consequence

This changes our implementation order substantially:

1. reproduce `8b76480b0e9a` on our M1 Max runner;
2. freeze its correct Apple7 policy as a new comparison arm;
3. instrument DFlash acceptance / cycle costs / per-projection timing;
4. only then decide whether a custom persistent/small-M Q8 verifier kernel is still necessary.

Yesterday we treated Apple7 Splash as likely requiring a custom backend. This exact M1 result shows that much of the current Q4 runtime can execute correctly with **policy changes alone**.

That is a real reduction in engineering risk for the 27B lane and transferable mechanism evidence for Flash, but it does not prove full Flash-Next or PP2/TB4.

## Target change — single-M1 Qwen3.8-27B

Previous ladder:
- >=22 TG ~80%;
- >=25 TG ~55-60%.

New ladder:
- **>=22 TG ~90%**;
- **>=25 TG ~65%**;
- >=28 TG ~30% unchanged;
- >=30 TG ~15% unchanged.

Why the move is deliberately modest: two prompts physically clear 25 TG on the exact target machine, but the third is only 15.4 TG and the three-prompt mean is 22.3. Content-dependent DFlash acceptance remains the limiting variable. The 25-TG working target is therefore more credible, not yet routine.

Cold PP stays **110 TG target / ~60% confidence**. Splash's 49-PP 7K result is direct but reflects a currently weak Apple7 prefill path; existing native MLX M1 evidence around 85-100 PP remains a better baseline for the broader mature-runtime target.

## RECOVERED — dynamic expert residency is already directly tested on Flash-Next

Source: llama.cpp PR #27861, created 2026-08-28. It predates this boundary and is recorded as recovered older evidence because it directly answers the expert-swapping question raised immediately before this watch.

On Qwen3.8-Flash-Next UD-Q4_K_XL, 512 experts / top-10 routing, a 54K-record mixed routing trace found:
- weak transferable static skew: a learned top-32 list covers only ~10% out of sample (uniform ~6.2%);
- strong temporal locality: simulated **LRU-64 ~67%**, **LRU-128 ~81%**.

The PR dynamically caches recently used host-offloaded experts in accelerator memory. One 2x3090 setup with 28 expert layers host-resident reports **18.4 -> 24.2 TG (+31%)** using 48 slots/layer, about 4.1 GiB VRAM. Other community arms show that short-window admission gates can reduce upload churn dramatically and that speculative small-batch support requires careful duplicate-slot / synchronization handling.

### P51 consequence

Add **dynamic expert residency** as a research branch, especially for full Flash on a single 64-GB M1:
- preserve all 512 experts instead of REAP-pruning them;
- keep critical/shared/sensitive tensors resident;
- maintain a stage-local hot routed-expert pool;
- use recency + short-term frequency + measured behavioral importance for admission;
- record hit rate **and** bytes promoted, evictions, upload yield, residency pressure, MTP acceptance and behavioral parity;
- for dual-M1 PP2, expert caches remain stage-local so expert traffic never crosses TB4.

No target probability is moved from this GPU/PCIe evidence; Apple unified memory + SSD promotion has different costs.

## Other exact-window checks

- **Splash #91 merged** at 06:08 UTC: optional BF16 target KV; already captured in the prior watch, no new target effect.
- **Splash #79 merged** at 07:03 UTC: mixed greedy/sampling telemetry only; no arithmetic/scheduling speed change.
- **Splash #43** validates model-free Apple8/M2 admission but has no real-model generation result. #95 supersedes it for our M1 question.
- **vLLM #58114** directly targets Qwen3.8 PLE metadata construction. GB200 microbenchmarks cut builder time ~32-48%, but end-to-end validation is blocked by an extension mismatch; do not transfer to M1 or claim serving TG.
- **vLLM #47842** removes one Qwen GDN reshape/copy kernel on ROCm; serving gain is only ~0.4-0.8% on 8x MI355X. Mechanism is generic launch cleanup, no M1 forecast impact.
- **llama.cpp #28243** remains the Qwen3.8-Flash-Next shared-MTP PR with a broad 1.3-2x claim, but no new exact M1/TB4 measurement was attached in this window.
- Kadir, MTPLX, APEX, AutoRound, Harish 5070-Ti and the existing 5070-Ti same-card projects had no qualifying new commit/receipt in-window.
- Targeted web/community search found no newer **2x M1 Max/TB4 Flash** receipt and no newer exact **5070 Ti** result that displaces the current frontier.

## Dual-M1 Flash interpretation

No forecast change. The most important transfer is qualitative:

> Apple7 is no longer merely 'maybe capable of a Splash-like path.' We now have direct M1 evidence that the existing model-specific runtime works correctly with a measured Apple7 policy and no new kernel implementation.

That removes one implementation-risk term from P70. It does **not** establish the memory/PLE/full-Flash/PP2/TB4 denominator, so the headline remains **40 TG @ ~128K / 400 cold PP / ~70% confidence for >=40 TG**.

## New hard boundary

**2026-09-22 09:29:14 UTC**
