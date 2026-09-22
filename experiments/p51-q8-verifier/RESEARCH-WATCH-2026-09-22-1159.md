# Project 51 primary-lane research watch — 2026-09-22 11:59 ET

**Freshness boundary checked:** previous hard boundary **2026-09-22 10:43:09 UTC**. Search ran through the user's cutoff **2026-09-22 15:59:04 UTC**.

## Decision

**No numeric target or confidence change.**

The strongest new evidence is not a new raw TG record. It closes important pieces of the **warm-agent / speculative-state lifecycle** and gives us a much better recipe for the newly-interesting **DASLab/low-bit + DFlash2 on M1** experiment.

## NEW — oMLX #3835 merges reusable prefix-tail blocks

Source: https://github.com/jundot/omlx/pull/3835
Main commit in-window: `8288884d9b4f` at **2026-09-22 14:58:02 UTC**.

Problem: paged caches traditionally publish full 2K/4K blocks. A fully warm multi-turn conversation therefore re-prefills up to `block_size-1` tokens every request, especially around chat-template generation markers.

#3835 stores one short terminal-tail snapshot just before the generation prompt, hashes it in its own domain with parent lineage, persists the metadata through SSD reconstruction, and re-lays the next request from the prior full-block grid so the cache geometry does not drift.

Physical validation:
- Qwen3.6-35B-A3B, 13.4K prompt: **1,174 -> 37 re-prefilled tokens**;
- TTFT: **0.83 -> 0.42 s**;
- 10-turn 100K-164K conversations with Lightning MTP on Qwen3.8-27B, Qwen3.8-Flash-Next and DeepSeek-V4.1 reused the previous prompt minus the generation prompt;
- deleting tail blocks to force a partial hit recovered on the next turn;
- `--no-cache` replay returned the same answers.

The PR explicitly notes that changing chunk boundaries can slightly perturb greedy output even when restored state is exact. This reinforces our existing rule that cache correctness and full cold-path token identity are related but not identical tests.

### P51 consequence

For a coding agent, full-block prefix reuse is not enough. Add **generation-boundary tail snapshots** to the canonical warm-session design. The reusable prefix identity becomes:

`full-block lineage + terminal-tail lineage + message/generation boundary + recurrent/QSA state version + draft-state lineage`.

## NEW — oMLX #3840/#3842 repair hybrid draft-cache reuse

Sources:
- https://github.com/jundot/omlx/pull/3840
- https://github.com/jundot/omlx/pull/3842

Both were created inside this window.

Two different bugs had combined to make SpecPrefill's hybrid-GDN draft cache effectively useless:

1. `score_tokens()` read logical sequence position from `cache[0]`. On Qwen hybrid models layer 0 can be recurrent `ArraysCache`, which has no `offset`; restored state was therefore silently treated as position 0 and re-prefilled.
2. draft `store_cache()` did not receive recurrent boundary snapshots. Stored blocks therefore contained placeholders for recurrent layers, and cache walk-back correctly rejected every nominal hit as stale/unsafe.

#3840 resolves logical offset from the actual attention-layer cache and fails closed when state exists but no trustworthy position can be derived.

#3842 captures recurrent state at a reachable draft-prefill boundary and publishes it with the draft cache.

Reported runtime on a **27B target + 0.8B hybrid GDN draft**:
- baseline: **0 draft-cache hits**;
- treatment: **23 hits / 27 scorings**;
- representative warm suffix-only scorings: roughly **0.3-0.8 s** instead of multi-second full scoring;
- treatment total: **38.7 s actual vs 140.4 s baseline-equivalent** on the fitted per-prompt comparison;
- no partial-prefix rejections or scoring failures in the treatment.

The authors are explicit that these are prompt-fit comparisons between stochastic trajectories, not a fixed-seed end-to-end speedup claim.

### P51 consequence

This is almost a direct implementation proof of our existing architecture claim:

> **restoring target KV without restoring usable speculative/recurrent state is incomplete.**

For P51, target prefix, recurrent/QSA checkpoint and DFlash/MTP draft state each need an independently reachable committed boundary before the coordinator intersects them.

## RECOVERED — direct M1 DFlash2 failure mode and successful workaround

Source: https://huggingface.co/incoai/Qwen3.8-27B-DFlash2/discussions/3

This predates the current hard boundary (Aug 19) and is classified as **RECOVERED OLDER EVIDENCE**, but it directly qualifies the DFlash2-on-M1 idea raised in the preceding conversation.

On an **M1 Max 32 GB**, the then-current oMLX/dflash-mlx profile used quantized draft weights with FP16 activations (`w4a16`) because M1/M2 emulate BF16. The reporter/diagnostic reproduction found:
- draft hidden state non-finite under FP16;
- logits all NaN;
- acceptance **0%**;
- DFlash2 dramatically slower than plain decode.

Controls:
- BF16 draft: finite and accepted useful tokens;
- quantized draft with **FP32 activations (`w4a32`)**: finite and matched BF16-like acceptance across the reported prompts.

After switching the quantized draft to FP32 activations, the reporter says DFlash2 reached about **25 TG**, slightly faster than their plain ~19.6-TG path. BF16 also worked but was slower on M1 because it is emulated.

### P51 consequence

For the second-M1 DASLab+DFlash2 sweep, do **not** start with FP16 draft arithmetic simply because the chip prefers FP16 elsewhere. Start with:

1. BF16/reference draft if the runtime supports it;
2. quantized draft + FP32 activations;
3. only then an FP16-activation arm after a finite-state oracle passes.

Every arm must record draft hidden finite %, logit finite %, per-position acceptance, accepted tokens/pass, draft time and target verify time.

This recovered result makes 'DFlash2 can help an M1' much more credible, but it is not a modern DASLab/M1 benchmark and therefore does not move the 25-TG target probability.

## DFlash2 + low-bit target status

Official llama.cpp DFlash2 support is already target/draft-quant independent enough to serve a Q4 target with BF16/Q8/Q4 drafts; on M5 Pro the published Qwen3.8-27B study reports **10.42 AR -> 18.43-19.31 TG DFlash2**, acceptance length ~4.9-5.1.

Public IQ3_S packages also explicitly pair a low-bit target with an external DFlash2 draft, proving the topology is practical in llama.cpp. Current web/community search also surfaced GSQ-RCO IQ3_S + DFlash2 use on discrete GPUs, but no timestamped exact M1/DASLab result clean enough to promote as a target anchor.

So our proposed experiment remains valid:

`DASLab IQ3_S / IQ3_XXS target` + `external DFlash2 draft` + `Apple7 precision gate` + `n_max sweep`.

## UPDATE — vLLM #58114 now has end-to-end PLE metadata results

Source: https://github.com/vllm-project/vllm/pull/58114

Previously we only had builder microbenchmarks. The PR now reports Qwen3.8-Flash-Next-FP8 / TP4 / MTP3 on one 4xGB200 node:

| concurrency | output TG change | TPOT change | TTFT change |
|---|---:|---:|---:|
| C1 | **-1.52%** | +2.07% | -2.47% |
| C8 | **+4.96%** | -4.70% | -4.48% |

while the metadata builder itself is ~32-48% faster.

This is valuable precisely because it prevents over-crediting the microbench. The same metadata optimization can be useful at C8 and neutral/negative for B1.

### P51 consequence

PLE/QSA metadata optimizations must be measured at **B1 and B2/B4 separately**. Do not transfer a builder percentage into decode TG.

## Splash scheduler work — useful design ideas, no performance credit yet

Splash opened #106-#110 to:
- bound decode selection to the actual max batch width of four;
- remove selected prefill candidates in one pass;
- reuse scheduler planning buffers;
- reuse validated cache probes between admission and activation;
- use page fingerprints to accelerate shared-prefix comparison.

All preserve correctness semantics and all explicitly require benchmarking. No end-to-end receipt existed by the cutoff, so P51 gives them **zero forecast credit** for now.

## Other primary-lane checks

- **2x M1 Max / TB4 Flash:** no new exact receipt, PP2 implementation result or Apple7 full-Flash timing.
- **single-M1 Flash:** no new full-512-expert M1 receipt and no Apple dynamic-expert-cache implementation.
- **M1 27B:** no new modern exact-hardware record beyond Splash #95; recovered DFlash2 evidence changes the experiment recipe, not the target.
- **5070 Ti 27B:** no new Harish/DASLab same-card frontier result; the sm_120 IQ_S compiler gate from the prior watch remains mandatory.
- llama.cpp #27861 expert-cache PR was touched in-window, but no new benchmark/comment/review measurement appeared in the public PR streams we checked.
- DS4 #952 remained active but added no new exact M1-Max measurement in this window.

## Target / confidence impact

Unchanged:
- dual-M1 Flash-Next: **40 TG @ ~128K**, **400 cold PP**, >=38 AA-class; ~70% planning confidence for >=40 TG;
- single-M1 27B: **25 TG**, ~65% confidence for >=25;
- RTX 5070-Ti 27B: **120 TG mature optimized target**.

## New hard boundary

**2026-09-22 15:59:04 UTC**
