# Project 51 external runtime watch — 2026-09-20 14:18 ET

**Hard freshness window:** strictly after **2026-09-20 15:28:44 UTC** through the user's message cutoff **2026-09-20 18:18:49 UTC**.

## Decision

**No TG/PP confidence change.** Keep **40 TG @ ~128K / 400 genuinely cold PP** on 2x M1 Max 64 GB / TB4.

**Quality target changed by explicit user decision:** production quant must preserve **>=38 Artificial-Analysis-class behavior**, with **39-40 preferred**. Current source Qwen3.8-Flash-Next is still **AA Intelligence Index 40 (#5/113)** on the current Artificial Analysis page. The quant search is now lexicographic: satisfy the quality floor first, then maximize M1 throughput. A faster candidate that falls below the 38-class acceptance floor remains an experimental speed quant, not the production lane.

Current source reference:
https://artificialanalysis.ai/models/qwen3-8-flash-next

Current AA v4.3.2 profile includes, among others, AutomationBench-AA **56%**, Terminal-Bench 4.0 **25%**, SciCode **51%**, HLE **38%**, and AA-LCR v1.1 **80%**. These benchmark values are source-model context, not claims about any local quant.

## NEW — vLLM #57813: unfinished work should retain the exact prefix chunks it will resume from

Source: https://github.com/vllm-project/vllm/pull/57813  
Created **2026-09-20 15:49:52 UTC**; implementation commit **15:37:20 UTC**.

CPU-offloaded chunks became normally evictable as soon as their store completed. During a paused/in-flight rollout or agent task, the request stops touching its own prefix and can therefore become the LRU victim even though it is exactly the state the request will need on resume.

The PR adds optional `pin_in_flight_chunks`:

- chunks referenced by unfinished requests are refcounted;
- eviction prefers everything else;
- pins release on request finalization;
- pinning is a preference rather than an absolute reservation, so a cache consisting entirely of in-flight chunks can still make progress.

**Project 51 consequence:** the sleep-preserved CPU/SSD tier should understand **request lifetime**, not just global LRU. A live coding-agent session or paused tool loop should preferentially retain its certified resume checkpoint/prefix while completed/background sessions are evicted first. Do not make the pin absolute: memory-pressure escape must remain possible.

## NEW — vLLM #57815: sparse-indexer batch shape can silently change the forward pass

Source: https://github.com/vllm-project/vllm/pull/57815  
Created **2026-09-20 16:16:29 UTC**; implementation commit **16:15:35 UTC**.

vLLM's sparse indexer cannot currently honor `VLLM_BATCH_INVARIANT=1`. Which top-k path/algorithm is used can depend on:

- row count;
- padded column count / longest sequence in the batch;
- occupancy/cooperative-launch fit;
- backend fallback thresholds.

That changes sparse **selection**, not merely reduction rounding. The PR explicitly references observed greedy nondeterminism on **Qwen3.8-Flash-Next** and DeepSeek-V4-Flash under changing concurrency.

The patch refuses the unsupported promise instead of silently claiming batch invariance.

**Project 51 >=38-quality gate:** certification must include the same prompt/session under **B1/B2/B4 and mixed-length concurrent batches**, checking QSA selected indices, greedy token identity/logit envelope, recurrent state and MTP acceptance. If batch shape changes indexer algorithm or padding geometry, either pin a batch-invariant path or treat topology/concurrency as part of runtime identity. Temperature 0 alone is not a determinism guarantee.

This is especially important for the custom quant search: a candidate cannot be blamed or credited for a quality change that is actually a batch-dependent QSA-selection change.

## NEW — vLLM #57817: GPU n-gram speculation is not automatically pipeline-parallel

Source: https://github.com/vllm-project/vllm/pull/57817  
Created **2026-09-20 17:04:09 UTC**; implementation commit **17:03:34 UTC**.

vLLM's `ngram_gpu` proposer keeps token/proposer state only on the last PP rank, but incremental state updates run on every rank. PP>1 therefore crashes/hangs today; the PR rejects the configuration before workers launch.

Making it functional requires transport of sampled tokens, draft tokens and per-request counts across PP ranks.

**Project 51 rule:** do **not** conflate this generic `ngram_gpu` speculative proposer with Flash-Next's PLE/n-gram embedding table. The latter can remain a stage-owned sparse sidecar. But if P51 adds n-gram self-speculation under PP2, its proposer state needs explicit ownership/transport or stage-local semantics; it cannot be assumed to work merely because target MTP state transport works.

## UPDATE — Splash #3 hardens a real SSD tier for KV + recurrent state

Source: https://github.com/incoai/splash/pull/3  
Original implementation predates this window; substantive validation/hardening commits continued through **2026-09-20 17:21:27 UTC**. Classified as **UPDATE**, not NEW architecture discovery.

The SSD tier stores cached KV pages **and recurrent state** under a bounded disk quota while sharing the same prefix tree/recency order as RAM. Current validation includes:

- partial writes/allocation failures;
- cancellation during real disk restore;
- shared restores;
- exhausted capacity;
- real-model 128K cold/cached paths and partial-prefix replay;
- 648 HTTP requests in main-vs-disabled comparisons.

Reported warm-throughput medians across tested cases ranged **-1.00% to +0.94%**, i.e. no demonstrated meaningful steady-state penalty in those runs.

**Project 51 consequence:** this strengthens the practical case for the new **sleep-idle** tier: CPU/SSD checkpoint retention can include recurrent state, not only plain KV. Still measure write amplification/high-water allocation and do not infer M1 NVMe restore latency from Splash's numbers.

## UPDATE — vLLM #57816: preemption/resume must reset offload-placement cursors

Source: https://github.com/vllm-project/vllm/pull/57816  
Created **2026-09-20 16:25:05 UTC**, but its implementation commit is **07:33:35 UTC**, before this watch boundary. Classified as **RECOVERED OLDER EVIDENCE**.

A resumed request represented as new placement data could append onto stale GPU block-table/cursor state and fail to offload the newly confirmed tail block.

**P51 rule:** after preemption/rewind/restart, placement/store cursors are session-versioned state. Reset/reconstruct them from the resumed checkpoint; never append new placement to stale cursor bookkeeping.

## Screened / no target-changing evidence

- **DS4:** no strict-window implementation commit. #1090/#952 updates are archived/review activity; their headline measurements predate this window.
- **oMLX:** no post-boundary implementation commit; #3776 remains the current direct Apple Flash verify-fusion evidence. #3003's DFlash observability work is August code despite a fresh metadata timestamp.
- **mlx-serve:** no strict-window Project-51 implementation commit.
- **llama.cpp:** no strict-window M1/Flash implementation receipt. #29181 was opened later but its main grouped-expert fusion commit predates the previous boundary; already treated as recovered evidence.
- **Splash:** #3 received new validation/hardening commits and is recorded as an UPDATE; no new target-topology TG receipt.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no activity.
- **MTPLX:** no post-boundary commit.
- **APEX:** no post-boundary commit.
- Current community search found a September 20 Strix Halo post comparing multiple Flash-Next quants, but the search result does not expose an exact publication time within this strict window and the hardware/backend is not M1. It is not promoted as cutoff-qualified evidence.
- Current Hugging Face/community pages continue to support heterogeneous 4-bit + protected-attention designs, but no newly timestamped exact M1/TB4 quality/throughput receipt appeared.
- No new exact **2x M1 Max 64 GB / TB4 / ~128K / P51 mixed quant + MTP** physical throughput receipt appeared.

## Target impact

**TG/PP: no numeric change.**

**Quality: explicit production floor added.**

Production Project 51 quant acceptance is now:

- **>=38 AA-class behavior: hard floor**;
- **39-40: preferred target band**;
- below 38: experimental speed lane only, regardless of TG;
- if the 40-TG headline requires falling below 38, preserve intelligence and accept a slower production rate instead.

The AA number itself must ultimately be established by an actual comparable evaluation or a validated proxy suite; an engineering guess that a quant is "probably 38+" is not certification.

**New hard boundary: 2026-09-20 18:18:49 UTC.**
