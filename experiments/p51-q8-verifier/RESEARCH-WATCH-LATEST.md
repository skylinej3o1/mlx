# Project 51 primary-lane research watch — 2026-09-23 12:30 ET

**Freshness boundary checked:** prior hard boundary **2026-09-23 13:53:27 UTC**. This pass covers substantive evidence through the user cutoff **2026-09-23 16:30:12 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No new exact 2x M1 Max / TB4 Flash-Next throughput receipt appeared, and no new DASLab / GSQ-RCO xhigh behavioral result appeared.

The useful deltas are operational/correctness-oriented:

1. vLLM #58368 demonstrates that hybrid Mamba/GDN + MTP prefix reuse can lose the prompt-tail recurrent checkpoint and collapse a valid 1,536-token reuse to **zero**. This strengthens the rule that a cache hit includes the correct recurrent checkpoint boundary, not merely matching token hashes/KV blocks.
2. llama.cpp #29322 shows `--sleep-idle-seconds` can keep prompt-cache RAM allocated during sleep and then discard the cache on wake, forcing a full re-prefill. This directly affects Project 51's planned agent sleep/wake/prewarm design.
3. llama.cpp #29324 shows token-count cache budgets are badly misleading for hybrid/recurrent models because fixed recurrent state dominates short entries: about **~640 MiB private-memory growth per ~1.2K-token prompt** in the reported Qwen3.8-27B setup. P51 cache budgets must be byte/state aware.
4. SGLang opened #40925 and #40929 for DSA-indexer and MTP KV-cache sharding. They are potentially relevant to state partitioning, but the PRs currently contain no accuracy/performance evidence and get no architectural promotion beyond "watch."
5. llama.cpp merged missing Metal f32 x BF16 matrix-vector variants needed by BF16 depthwise 1D convolution. It fixes a real Metal compatibility hole, but the code is guarded by native-BF16 support and therefore gives no direct M1-Max performance credit.

Keep:
- Flash-Next xhigh production quant search: **~3.0 / 3.2 / 3.4 / 3.6 average transformer BPW**;
- likely source-like xhigh region: **~3.3-3.6**, center hypothesis **~3.4-3.5**;
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**;
- planning confidence for >=40 TG: **~70%**;
- 50/500 remains stretch/headline territory.

---

## NEW — vLLM #58368: MTP prompt-tail cache reuse requires the recurrent checkpoint at the shifted boundary

Source:
https://github.com/vllm-project/vllm/pull/58368

Created **2026-09-23 14:10:53 UTC**, still open at this cutoff.

Affected regime:
- hybrid Mamba/GDN models;
- MTP enabled;
- prefix caching enabled;
- aligned recurrent-cache mode;
- hash block size smaller than the recurrent/Mamba block size.

Concrete example from the PR:
- `hash_block_size = 64`;
- prompt A length = **1,600 tokens**;
- prompt B begins with A;
- MTP prefix lookup intentionally drops the final 64-token matched block, so the reusable boundary should be **1,536**;
- scheduler ends a prefill chunk at 1,536 to compute recurrent state there;
- regression saves the recurrent state at 1,600 instead of 1,536;
- result: prompt B reuses **0 tokens instead of 1,536**.

The bug came from using the wrong semantic flag: checkpoint-tail storage depended on `use_eagle`, while the scheduler's actual boundary-shift condition is represented by `drop_eagle_checkpoint_block`.

### P51 consequence

Promote a more precise cache-identity rule:

> a reusable prefix is `token-prefix identity + exact recurrent/QSA checkpoint boundary + state schema`, not token hashes alone.

For every warm-prefix entry, record:
- logical matched token length;
- actual replay/resume boundary;
- recurrent checkpoint token index;
- QSA/indexer checkpoint token index;
- draft/MTP checkpoint boundary;
- hash-block and recurrent-block geometry;
- model/runtime/quant identity.

A checkpoint stored at the wrong boundary invalidates the hit even if the prefix token hashes match.

Add a regression fixture with non-aligned prompt lengths around every block boundary and require the restored continuation to match a no-cache reference.

---

## NEW — llama.cpp #29322: sleep holds prompt-cache RAM, then wake discards the cache

Source:
https://github.com/ggml-org/llama.cpp/issues/29322

Created **2026-09-23 16:17:18 UTC**.

Reported setup:
- Qwen3.8-27B hybrid GDN model;
- RTX 5090 32 GB / Windows;
- `--cache-ram` plus `--sleep-idle-seconds`.

Observed lifecycle:
1. entering sleep destroys model/context/speculative state but leaves `prompt_cache` allocated;
2. wake reloads the model and constructs a new prompt cache;
3. the old cache entries are therefore discarded **after consuming host RAM throughout sleep**.

Minimal behavioral receipt:
- before sleep, repeated prompts process only **4 tokens** after cache restore;
- after wake, the same prompts re-process **3,974** and **3,624 tokens**.

The reporter notes that for ~100K agent sessions, a wake can therefore add a full re-prefill on top of model reload.

### P51 consequence

The P51 agent sleep/wake plan must explicitly distinguish:

- **model residency state**;
- **prompt/warm-state persistence**;
- **host/SSD cache residency**;
- **post-wake validity**.

A process reporting "cache retained in memory" is insufficient. The acceptance test is a post-wake cache hit that restores the full typed Flash state manifest and reproduces the reference continuation.

Required wake benchmark:
1. establish a long warm session;
2. verify warm-hit token count / TTFT;
3. enter the real sleep state;
4. measure resident host/SSD bytes while asleep;
5. wake;
6. verify the same prefix hit survives;
7. measure wake->ready and task->TTFT separately.

If a runtime cannot preserve logical cache entries across model unload/reload, P51 should own persistence outside the runtime rather than relying on its in-process cache.

---

## NEW — llama.cpp #29324: recurrent prompt-cache entries need byte-based budgets, not token-count budgets

Source:
https://github.com/ggml-org/llama.cpp/issues/29324

Created **2026-09-23 16:19:20 UTC**.

Reported setup:
- Qwen3.8-27B hybrid GDN;
- RTX 5090 32 GB;
- 96 GB host RAM;
- unified KV / Q8 K+V;
- `--cache-ram -1`.

Implementation issue:
- `-1` removes the byte limit but leaves the total token cap at `n_ctx`;
- hybrid/recurrent saved states have a large fixed per-entry cost independent of prompt length;
- token count is therefore a poor predictor of memory use.

Measured with 100 distinct ~1.2K-token prompts:
- `--cache-ram -1`: roughly **+640 MiB per new prompt**, linear;
- 10 prompts: **+6.2 GiB**;
- 20: **+12.5 GiB**;
- 30: **+18.7 GiB**;
- 40: **+25.0 GiB**;
- stopped at 44: **+27.5 GiB**, still growing;
- explicit 24,576-MiB cache budget: growth plateaued around **+23.4 GiB**.

Reporter estimates recurrent state around **~300 MiB per saved state**, with checkpointing adding comparable fixed cost.

### P51 consequence

Warm-agent cache capacity must be planned in **bytes per complete state bundle**, not token count.

Required telemetry per entry:
- token count;
- target KV bytes;
- QSA/indexer bytes;
- recurrent/GDN bytes;
- checkpoint history bytes;
- draft/MTP bytes;
- PLE/history sidecar bytes;
- metadata/schema overhead;
- total host / SSD resident bytes.

Eviction should be governed primarily by total bytes and value/reuse policy, with token count only secondary.

This is especially important if many small independent agent sessions are retained: short prompts are not cheap merely because they contain few tokens.

---

## NEW / WATCH ONLY — SGLang #40925 and #40929 open cache-sharding work for DSA indexer and MTP

Sources:
- https://github.com/sgl-project/sglang/pull/40925
- https://github.com/sgl-project/sglang/pull/40929

Created:
- #40925: **2026-09-23 14:26:58 UTC**;
- #40929: **2026-09-23 14:55:54 UTC**.

Titles:
- "Support kv cache sharding for DSA indexer"
- "Support kv cache sharding for MTP"

At this cutoff both PR descriptions are still empty templates:
- no mechanism explanation;
- no accuracy result;
- no speed result;
- CI is not green.

The diffs are non-trivial (#40925 ~768 additions; #40929 ~950 additions), so this is real implementation activity, but there is not enough evidence to infer semantics or performance safely.

### P51 consequence

Watch closely because this may become useful cross-framework evidence for:
- indexer/MTP state ownership;
- state sharding geometry;
- PP/disaggregated cache transfer.

Do **not** change P51 state ownership or PP2 design from the PR titles alone.

No target credit.

---

## UPDATE — llama.cpp #28741 merged: missing Metal f32 x BF16 depthwise-convolution path

Source:
https://github.com/ggml-org/llama.cpp/pull/28741
Merged commit in this window:
`9575389609d6f8437de0b205561a4824d217c409`

The fix adds missing Metal `f32 x bf16` matrix-vector variants used by BF16 depthwise 1D convolution. Before the fix, that convolution shape aborted because `ggml_conv_1d_dw` builds an F32 im2col and multiplies it by a BF16 kernel.

### P51 consequence

This is useful ecosystem correctness for hybrid/GDN models on newer Apple devices with native BF16 support.

However the implementation is guarded by `GGML_METAL_HAS_BF16`; devices without native BF16 support are unchanged. Therefore it gives **no direct M1-Max speed/correctness credit** to Project 51's Apple7 target.

It does reinforce why P51's M1 lane should prefer intentional FP16 protected-island compute rather than assuming BF16 kernel parity.

---

## NEW / SECONDARY — oMLX #3877 MiMo Lightning MTP reinforces speculative-state isolation and rollback

Source:
https://github.com/jundot/omlx/pull/3877

Although MiMo is not the primary P51 Flash target, this merged work is relevant to speculative-state engineering:

- isolates speculative head state with cache copies;
- retains predictor index;
- rolls rejected drafts back after sliding-window cache rotation;
- preserves MTP heads and calibration statistics through oQ conversion.

M3 Ultra / MiMo-V2.6-Flash-RL-oQ4e-mtp reported Lightning-MTP TG changes:
- 4K: **44.4 -> 49.3 (+11.0%)**;
- 16K: **41.6 -> 50.0 (+20.2%)**;
- 32K: **38.5 -> 46.0 (+19.5%)**.

But the author explicitly notes long-context greedy token IDs can differ across cache/batching conditions with MTP enabled, so this is not a clean equivalence proof.

### P51 consequence

No Flash target credit.

Durable general lesson already consistent with P51:
- speculative state must be isolated from target state;
- rejected branches must roll back every mutable cache/index;
- predictor/draft position is part of cache identity;
- oQ conversion must preserve MTP tensor identity and calibration.

---

## Community / Hugging Face delta

Explicit searches for fresh post-boundary:
- DASLab / GSQ-RCO xhigh updates;
- Flash-Next M1/M2/M3/M5 long-context measurements;
- new MTP/DFlash2 128K receipts.

No qualifying new result in the **13:53:27-16:30:12 UTC** window was found.

Search surfaced older material only, including:
- Halogen/Strix-Halo Flash measurements;
- Litwein REAP320/MTPLX artifacts;
- prior M5/M3/M1 community cards;
- older SSD-PLE / DGX-Spark experiments.

None is classified as NEW for this pass.

---

## Checked with no qualifying fresh target evidence

- **MTPLX:** no new commit/PR/issue in-window.
- **EXL3:** no new commit/PR/issue in-window.
- **PonyExl3:** no new commit/PR/issue in-window.
- **mlx-serve:** no P51-relevant fresh change.
- **official Qwen3.8 repo:** no new commit/PR/issue in-window.
- **MiaAI-Lab dual-DGX-Spark Flash:** no new commit/PR/issue in-window.
- **flashnext-hybrid:** no new commit/PR/issue in-window.
- **Weschera single-DGX-Spark Flash:** no new commit/PR/issue in-window.
- **DS4:** no qualifying new performance/correctness receipt.
- **DASLab / GSQ-RCO:** no new xhigh behavioral receipt.
- no new exact **2x M1 Max/TB4 Flash-Next** TG or cold-PP receipt.
- no new exact **RTX 5070 Ti** receipt strong enough to move its target.

## Target / confidence impact

Unchanged:

- Flash-Next xhigh production quant: search **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- single-M1 27B: **25 TG**.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-23 16:30:12 UTC**
