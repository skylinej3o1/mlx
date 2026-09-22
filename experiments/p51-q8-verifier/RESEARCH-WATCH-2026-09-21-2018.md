# Project 51 primary-lane research watch — 2026-09-21 20:18 ET

**Freshness boundary checked:** branch was already advanced to **2026-09-21 21:48:06 UTC** before this pass. Search ran strictly through the user's cutoff **2026-09-22 00:18:59 UTC**.

## Scope

This pass intentionally returned to the three primary lanes:

1. **Qwen3.8-Flash-Next on 2x M1 Max 64 GB / TB4**, with single-M1 Flash as a secondary calibration lane;
2. **Qwen3.8-27B on one M1 Max 64 GB**;
3. **Qwen3.8-27B on the RTX 5070 Ti 16 GB + 64 GB host**.

Unrelated model/runtime activity was ignored unless it changed a mechanism directly needed by those lanes.

## Decision

**No numeric target or confidence change.**

No new exact M1/TB4 Flash performance receipt, single-M1 Flash record, single-M1 27B speed record, or 5070-Ti 27B record appeared after the current 21:48:06 UTC boundary.

The two material exact-window additions are correctness/runtime-state results that matter directly to our intended agent workload:

- vLLM #58021 turns the distributed cache-geometry bug from the previous pass into an explicit fail-closed coordinator/worker contract;
- mlx-serve #492/#493 shows that a long Qwen3.8-27B agent can silently jump back to an old conversation branch if partial prefix reuse adopts speculative hidden state from the wrong lineage.

## NEW — vLLM #58021: resolved hybrid cache geometry must be authoritative

Source: https://github.com/vllm-project/vllm/pull/58021
Created **2026-09-21 21:49:02 UTC**, inside this pass.

The previous watch recorded #58020: the scheduler can resolve a fine hybrid prefix-match/hash unit from all cache groups while a worker independently derives a much coarser unit from its local recurrent block geometry, silently dropping a valid checkpoint.

#58021 supplies the concrete repair:

- resolve scheduler/hash geometry **once** in EngineCore;
- store the resolved values in `KVCacheConfig` before workers initialize;
- make scheduler and every worker read the same published geometry;
- late workers/restarts adopt that published value rather than re-derive it;
- repeated adoption of the same value is allowed;
- conflicting geometry is an error;
- unresolved access **raises** instead of silently falling back to local block size.

Focused validation reports 12/12 new tests and mutation checks that fail when each piece of the contract is individually removed. It does not claim model-level performance or accuracy improvement.

### P51 consequence

For PP2 across two M1s, cache/checkpoint geometry becomes explicit **cluster configuration state**. A session/checkpoint identity must carry at least:

- target cache/hash geometry;
- recurrent/GDN checkpoint grid;
- QSA/indexer state geometry;
- draft/MTP geometry;
- PP2 partition/runtime schema version.

No stage may independently infer a geometry already resolved by the coordinator. Missing or conflicting geometry fails closed to recomputation.

## NEW — mlx-serve #492/#493: partial-prefix reuse must not adopt sibling MTP state

Sources:
- https://github.com/ddalcu/mlx-serve/issues/492
- https://github.com/ddalcu/mlx-serve/pull/493

#492 was created **2026-09-21 21:54:09 UTC**. Environment:

- M4 Max 64 GB;
- `ddalcu/Qwen3.8-27B-MLX-Serve-8bit`;
- MTP depth 6, PLD on, dense KV;
- long coding-agent tool loop at ~80K context;
- multiple hot-prefix-cache entries.

Observed failure: after a tool result, the cache matched a sibling branch and reused **79,353 / 79,969 tokens** (raw match 79,488). The model then ignored the current task/tool suffix and answered as though the root prompt were still a simple `hi`. The request still reported a healthy **32.5 tok/s decode**, so this was a silent semantic failure, not a throughput or crash signal.

#493, created **2026-09-21 22:21:26 UTC**, addresses two separate hazards:

1. **Branch-owned speculative state:** on any partial match, MTP/DFlash hidden state is discarded rather than adopted from the sibling cache entry. Speculative state belongs to the exact branch that created it.
2. **Message-boundary restore:** a partial token match is snapped backward to a safe chat-turn delimiter before replay, so the suffix is never resumed from the middle of a tool/message boundary.

The PR says it was tested on multi-turn coding-agent loops with 80K+ context across multiple cache entries. No controlled speed comparison is claimed.

### P51 consequence

Warm-agent identity is stricter than token-prefix identity:

`target prefix` + `branch lineage` + `message boundary` + `speculative-state lineage`.

A partial cross-branch target-prefix match may still be reusable after safe replay, but **draft/MTP hidden state must be exact-lineage only**. This belongs in the GitHub Actions correctness suite before we optimize warm-cache hit rate.

## Primary-lane performance sweep

### 2x M1 Max / TB4 Flash-Next

- No new exact physical 2x-M1/TB4 receipt.
- No new PP2 Apple implementation/measurement.
- No new Apple7 Splash backend.
- The current two-Spark/DGPP evidence and ~70% planning confidence for >=40 TG @~128K remain the latest distributed analogue, not a new Apple result.

### Single M1 Max 64 GB Flash-Next

- `mihailescu2m/llama.cpp`, `npanj/llama.cpp`, Kadir's `qwen38-mac-fast` and visible fork: **no commits in-window**.
- Web/community search surfaced only the already-known M1/M5 Flash reports; nothing newer with a trustworthy post/commit time inside this boundary.
- No new result changes the existing exact-M1 low-20s long-context physical floor or the separate MTP/headroom hypotheses.

### Qwen3.8-27B on M1 Max

- No new M1 Max performance commit/receipt.
- mlx-serve #492/#493 is the meaningful new result: it changes long-agent cache correctness, not the speed forecast.
- A llama.cpp long-context-decode-cliff issue for Qwen3.8-27B was active just after the prior boundary, but its actual measurements date to August and therefore are not treated as new evidence. Current 5070-Ti and Apple tuned stacks already demonstrate that such a cliff is not universal.

### Qwen3.8-27B on RTX 5070 Ti 16 GB

- `Harish4948/Qwen3.8-27B-One-RTX-5070-Ti`: **no commits/issues updated in-window**.
- IST-DASLab GSQ/RCO: no issue/PR activity in-window relevant to this lane.
- The frontier remains the published same-GPU setup: **51.3 TG @128K**, **24.6 TG @261K**, native MTP, KVarN-style low-bit KV/recent high-precision tail, peak ~14.77 GB VRAM. No newer same-card receipt displaced it.

## Checked but not promoted

- Splash #90 received no new substantive root-cause result in this interval.
- vLLM QSA/offload and pipeline-push work was active, but no Apple/TB4 or 5070-Ti performance measurement was attached.
- llama.cpp and DS4 had no in-window commit relevant to the primary lanes.
- oMLX had no in-window runtime commit on Qwen3.8 Flash/27B.
- ByteShape, Bartowski, Unsloth, AutoRound, APEX, GSQ/RCO and community/HF search produced no newly timestamped result that changes the current primary-lane frontier.

## Target / confidence impact

Unchanged:
- Flash-Next 2x M1 Max headline: **40 TG @ ~128K**, **400 cold PP**, production floor **>=38 AA-class**;
- current Flash >=40 @128K planning confidence: **~70%**;
- single-M1 Qwen3.8-27B working target: **25 TG**;
- RTX 5070 Ti Qwen3.8-27B working target: **120 TG** with the existing long-context feasibility receipts unchanged.

## New hard boundary

**2026-09-22 00:18:59 UTC**
