# External runtime watch — 2026-09-16 12:46 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-16 11:07:39 UTC` through the user-request cutoff `2026-09-16 16:46:32 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, merge-only activity, or a later merge of older measurements. Several DS4 commits merged during this window but had September 15 author/measurement timestamps; those were screened as older evidence and do not refresh the boundary.

## Executive result

No exact active-topology receipt appeared for any canonical target. **No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max64: **25 tok/s / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max64/TB4: **15 tok/s / 180 tok/s cold PP**.

This window is highly useful for the implementation plan even without a target-moving receipt:

1. **vLLM #57171** turns the previous GLM-5.3-Flash PP warning into a constructive stage-boundary recipe: materialize deferred mHC `hc_post` on the sending stage, transmit only the residual streams, and let the receiving stage execute standalone `hc_pre`. The same PR found a second failure where PP left the MTP drafter embedding unavailable, producing **zero accepted drafts while target output still remained correct**.
2. **oMLX #3702 / `b45fb7e5` / `65c65e38`** fixes dynamic multi-request Lightning-MTP handoff. Rebuilding committed history now uses ordinary prefill semantics, and a late join hands the current committed frontier to standard batching instead of replaying the existing request's history.
3. **oMLX #3703** catches another Qwen4/Flash-Next MTP concurrency failure: the vendored linear `ArraysCache` lacked batch conversion, so parking MTP or admitting a second request could kill the engine loop. Warm singleton cache state must not be restamped with padding during conversion.
4. **vLLM #57170** shows that profile/admission workspace geometry must come from the active sparse backend rather than a dense worst case. One GLM-5.3-Flash configuration dropped a profile allocation from **4.25 GiB to 1.00 GiB**, increasing available KV capacity by **43%**.
5. **vLLM #57180** distinguishes the cache **proof horizon** from the reusable-token horizon. A lookup may need to inspect one speculative unit farther to prove an earlier committed recurrent checkpoint safe, while still returning no more reusable tokens than the caller allows.
6. **mlx-serve `dcb0ede5`** fixed a Qwen3.8-Flash-Next batch crash above ten surviving streams: a repack view buffer budgeted one handle per row even though a row could store up to three. After the fix, 32 streams were reported decoding together at **185 tok/s aggregate on M4 Max**. This is concurrency evidence only, not a B1 target signal.
7. **DS4 fresh Qwen Metal batching integration** adds native batched MTP with request-local recurrence/cache/n-gram state, exact-sampling fallback, stale-snapshot clearing and benchmark-validity guards. The strongest fresh lesson is that speculative policy is a **batch-cycle economics** decision and that failed/truncated streams must not silently count as throughput.
8. **llama.cpp `2f3fd025`** gives MTP output-producing and no-output/catch-up phases separate graph-result arenas so the two topologies do not evict and recapture each other's graphs. The published 4–5% RTX5090 measurement predates this window, so only the fresh graph-identity mechanism is promoted here.
9. **vLLM #57163** shows runtime lifecycle operations can silently destroy quant side state: `sleep(level=2)` zeroed FP8 KV scales because the scales had changed registration class and therefore escaped the buffer snapshot. Reloaded weights alone were not sufficient to restore correctness.
10. **vLLM #57206 / #57202** sharpen QSA/indexer routing: prefill selector eligibility depends on chunk request multiplicity/start geometry, and decode launch partitions should be bounded by work actually available rather than maximum configured geometry.

Fresh HF/community screening surfaced newly indexed M3 Ultra/M3 Max/5070Ti benchmark pages, but none had a source-time-qualified new measurement in this window on the exact active hardware/quant/runtime target. They are not promoted and do not move the planning distribution.

---

## Promoted PP design evidence — vLLM #57171: canonicalize deferred mHC state at the stage boundary

Source PR created: `2026-09-16 12:37:32 UTC`.

The previous watch captured vLLM #57121, which correctly rejected GLM-5.3-Flash PP because the stage handoff dropped deferred mHC `post` / `comb` state. #57171 proposes and validates a more useful solution.

Each token carries four mHC residual streams. A normal same-stage transition runs the fused operation:

`hc_post(previous layer) -> hc_pre(next layer)`.

At a PP cut there is no next local layer to consume the deferred representation. The new design therefore:

1. executes the pending `hc_post` on the **sending** stage;
2. sends only the resulting residual streams, shaped `[tokens, residual_streams, hidden]`;
3. initializes `residual/post/comb` as absent on the receiving stage;
4. lets the receiver's first layer execute standalone `hc_pre`;
5. under sequence parallelism, flattens/all-gathers/reshapes the residual streams at the boundary.

The argument for equivalence is strong: the fused op is defined as the same `hc_post` followed by `hc_pre`; the PP cut only removes one fusion opportunity per boundary.

Validation on PP=4 showed coherent output and a 50-problem GSM8K sample of 0.98 both with and without MTP. The fused-vs-split mHC comparison was bit-identical for token counts above 32 and within the documented small BF16-rounding difference below that threshold.

### Second bug: a correct target can hide a dead drafter

With PP enabled, MTP drafted 604+ tokens and accepted **zero** before the fix, yet final target outputs remained correct because verification still worked.

Root cause was weight provenance:
- the drafter needs the target `model.embed_tokens.weight`;
- the MTP loader dropped that weight;
- target-embedding sharing does not work the same way on non-owner PP stages;
- the target embedding on the final stage can be a `PPMissingLayer`.

The fix gives non-first PP drafter ranks their own embedding and explicitly loads the target embedding into it. Afterward mean acceptance length was reported at **2.45–2.81**, with per-position acceptance **0.85 / 0.60** on free-form text and **0.95 / 0.86** on the GSM8K probe. Single-stream 256-token generation on the test PP4 system moved roughly **5.7 s -> 3.3 s** with MTP.

Hardware was four CMP 170HX / GA100 devices plus an out-of-tree sparse-attention backend, so those rates are not Apple transfer receipts.

### Promoted rules for our dual-M1 bridge

- Prefer a **canonical boundary representation** over shipping every deferred implementation artifact when the transformation can be completed exactly on the sender.
- For Flash PP, compare two designs explicitly: propagate deferred HC side state versus materialize `post` before the cut and send only residual streams. Measure numerical equivalence, TB4 bytes/cycle and stage latency.
- Every MTP/drafter parameter has a stage-local provenance chain: `checkpoint/source -> loader -> rank owner -> alias/copy -> armed execution`.
- **Zero acceptance with correct final text is an artifact/weight-route alarm**, not merely evidence that the drafter is weak. Verify weights and stage residency before tuning depth or kernels.

---

## Promoted direct Apple runtime evidence — oMLX #3702: dynamic join must hand off committed state, not replay history

Fresh commits:
- `b45fb7e5a127355c0769d0b7c828849db17492e7` at `2026-09-16 15:29:53 UTC`;
- `65c65e38e0aff6001d09a8ecd234edd6d8780fa1` at `2026-09-16 16:14:12 UTC`.

Two related state-transition mistakes were fixed.

### Committed cache reconstruction must use ordinary prefill semantics

`_reconcile_mtp_to_standard` previously replayed committed history through the MTP-managed backbone wrapper. That wrapper creates speculative rollback snapshots even though the history being reconstructed is already committed.

The fix rebuilds through ordinary model forward/prefill, then compares the resulting cache against an independently ordinary-prefilled cache for Qwen and Qwen VLM families.

Rule: **state purpose determines execution route**. Reconstructing committed standard state must use committed/standard semantics even when the same model is capable of speculation.

### A late join must not replay existing rows

The later commit changes the active-batch join path. Instead of rebuilding prior requests, the drained MTP batch feeds each request's last committed main token into standard decode and then admits the new row.

New tests deliberately fail if the old full-history reconciliation path is called during a late join. They also cover unequal acceptance, three-row joins, staggered completion, exact next-token/logprob state and terminal cache history.

### Transfer to our scheduler

For dynamic batch membership, certify:
- pre-join request cache/frontier identity;
- one authoritative handoff token/state per existing row;
- no O(prompt/history) replay for rows whose committed frontier is already materialized;
- new rows receive only their own priming work;
- late join / cancellation / staggered finish cannot change an existing row's accepted prefix.

This is directly relevant if our MTP implementation ever batches request rows locally before or after the PP traversal.

---

## Promoted Flash-Next cache-conversion correctness — oMLX #3703

Source PR created: `2026-09-16 16:35:41 UTC`.

This is the last high-value source-time-qualified item found before the requested cutoff.

Qwen4-Exp uses a heterogeneous cache stack: vendored linear `ArraysCache` objects plus QSA KV caches. Lightning MTP's singleton rebuild passes caches through mlx-lm's generic batch converter. The QSA cache already supplied its own `to_batch`, but the vendored linear cache did not.

Consequences at concurrency >= 2:
- MTP parking could fail to restore calibration/standard state;
- a second request joining an MTP singleton could fail to restore committed batch cache;
- the engine loop could terminate and require model reload.

The proposed fix adds batch conversion to the cache class itself. A fresh cache receives the batch left-padding stamp; a **warm singleton is returned untouched** because it represents one running unpadded row. Tests found that stamping warm running state caused token mismatches.

### Promoted rules

- Every heterogeneous cache family participating in batching must define its own conversion/merge/split semantics; a central converter's type table is not sufficient evidence.
- **Fresh-cache conversion and warm-running-cache conversion are different state transitions.** Never mutate padding/ownership metadata merely because a generic conversion function was entered.
- Cache conversion belongs in the same qualification matrix as trim/rollback/prefix restore: cold, warm, late join, split, merge, park, resume and staggered finish.

---

## Promoted capacity evidence — vLLM #57170: profile geometry must come from the executed backend

Source PR created: `2026-09-16 12:33:38 UTC`.

A profile-run temporary for MLA prefill was always sized from dense MLA geometry even when the runtime used a sparse MLA backend that could never generate that many projected rows.

Measured GLM-5.3-Flash configuration:
- dense-profile allocation: **69,632 rows / 4.25 GiB**;
- sparse backend reachable cap: **16,384 rows / 1.00 GiB**.

A memory snapshot attributed 4.250 GiB of the roughly 4.5 GiB profile peak to that one temporary.

End-to-end capacity effect on the tested 4x GA100 PP4 setup:
- peak activation per GPU: **4.52–4.60 -> 1.29–1.35 GiB**;
- available KV cache on rank 0: **9.84 -> 13.09 GiB**;
- GPU KV capacity: **770,703 -> 1,102,315 tokens (+43%)**;
- GSM8K and MTP acceptance unchanged.

### Transfer to our 128K Flash qualification

Our memory ruler must distinguish:

`configured maximum geometry -> executed backend reachable geometry -> profile/warmup allocation -> settled live allocation`.

A profile-only impossible dense shape can steal enough unified memory to invalidate a 128K admission result even when steady-state sparse execution would fit. Profile and warmup transients are therefore first-class physical-capacity evidence, not bookkeeping noise.

---

## Promoted prefix-cache rule — vLLM #57180: proof horizon is not reusable horizon

Source PR created: `2026-09-16 13:41:59 UTC`.

With MTP/EAGLE and Mamba/recurrent state, prefix lookup may intentionally drop a speculative hash/checkpoint unit. The old coordinator also capped the search at the final reusable-token limit, so the two restrictions compounded.

Example from the PR:
- prompt length: 16,000;
- hash width: 16;
- old search could stop at 15,968;
- safe saved recurrent checkpoint existed at 15,984.

Allowing lookup to inspect through 16,000 gives enough **proof margin** for the later speculative drop to land on the safe 15,984 checkpoint, while the returned reusable hit still obeys the caller's original reuse limit.

Real Qwen3.5-0.8B reproduction:
- repeated 16K prompt cached tokens: **15,120 -> 15,984**;
- prompt recomputed: **880 -> 16**;
- cold/warm token IDs equal for all 6/6 comparisons.

This is a cache-correctness/recompute result, not a serving-throughput claim.

### Promoted rule

Maintain separate variables for:
- **proof/search horizon** — how far metadata may be inspected to establish safety;
- **reusable/commit horizon** — how many tokens may actually be adopted.

Registration and lookup must also use the same global speculation/drop contract. Per-group draft flags cannot silently disagree with scheduler-wide commit semantics.

---

## Promoted Apple batching correctness — mlx-serve `dcb0ede5`: logical rows undercounted physical sidecar handles

Source commit: `dcb0ede51dc5db3b291a7f9c5b52168a6b1f8a05`.
Source timestamp: `2026-09-16 13:58:00 UTC`.

Qwen3.8-Flash-Next batched decode crashed once more than ten streams survived a repack. The state-repack view buffer reserved **one handle per row** but could store up to **three handles per row**. At 11+ streams the buffer overran and the server segfaulted.

The release note reports 32 streams decoding together after the fix at **185 tok/s aggregate on M4 Max**.

That number is a concurrency aggregate, not B1 sustained TG and not a target-moving receipt.

### Promoted rule

Logical row count is not enough for scratch sizing. For each batched state family record:

`rows x max physical handles/views per row x bytes/handle + alignment/padding`.

Qualify the actual multiplicity at B1/B2/B4 and at a high-concurrency stress cell. This is the sidecar analogue of the existing physical billing-width rule.

The same commit also fixed `top_p=0`, which previously produced an empty nucleus and random-vocabulary sampling instead of greedy selection. Sampling-edge tests remain part of execution correctness, especially when comparing speculative and non-speculative paths.

---

## Promoted DS4 runtime update — fresh Qwen3.8 Metal batched MTP integration

Fresh author-time-qualified DS4 changes in this window include:
- `8e608a66e07aea0645ee3651755758465bd20f63` at `12:46:28 UTC`;
- `d1620ba061328caa7a6a81c434b09aa5fc4224f8` at `13:02:09 UTC`;
- `ab38bc6b7af916901e6160afc7d1445e13445a2a` at `13:17:25 UTC`;
- documentation/QA update `8db1d1d155cb0400a86a86b9c62d0defb3a6148b` at `13:17:26 UTC`.

The implementation now allows Qwen3.8 Metal session batching with MTP while keeping session-local recurrence, attention cache and n-gram history. Important safety behavior in the fresh integration:
- exact sampled requests can remain on ordinary batches;
- stale verification snapshots are cleared after ordinary batched progress;
- logical context/output limits are enforced independently of physical allocation room;
- speculative timing estimates are reset when batch width changes;
- speculative batches above the supported width, images and steering fall back to ordered execution;
- QA explicitly tests row isolation, reordered companions, mixed ordinary/MTP cycles, failed reads, snapshot recovery, cancellation, prefix reuse and short output limits.

A second fresh commit hardens the concurrency benchmark so failed/truncated streams cannot be counted as successful throughput. It now requires a valid terminal reason, valid completion-token usage, a completed `[DONE]` stream and all requested jobs to finish; failed grid cells propagate a nonzero exit status.

### What was deliberately NOT promoted from the same merge wave

A number of highly interesting Qwen batch-kernel measurements landed on main during this window but have September 15 or early-September-16 author/measurement timestamps. Examples include grouped MoE specialization, batched predictor work, row-wise recurrent/attention kernels and various C=16 throughput observations.

Those remain useful older transfer evidence but **do not refresh this window's measurement timestamp** and therefore do not move any target here.

### Promoted rules

- Speculative policy is a **whole-cycle economics** problem: compare accepted tokens per cycle against the measured plain/spec cycle cost at the current batch width.
- A policy's cost model becomes stale when batch width/topology changes; reset or re-learn it.
- Benchmark validity is binary: incomplete/failed/truncated streams do not become slower successful samples.
- Batched correctness requires companion/reordering isolation tests, not only aggregate output plausibility.

---

## Promoted graph/JIT identity transfer — llama.cpp `2f3fd025`: MTP phases need separate graph arenas

Fresh merge commit timestamp: `2026-09-16 16:16:54 UTC`.

MTP alternates between topologically different work:
- output-producing draft/decode batches;
- no-output prefill/catch-up batches.

llama.cpp previously stored both in one previous-graph arena. The shapes repeatedly replaced one another's cache identity, causing recurring graph capture instead of stable reuse.

The fix keeps separate graph-result arenas keyed by whether outputs are produced and tracks which arena is currently valid. Scheduler/memory resets invalidate both.

The PR includes an RTX5090 Qwen3.6 MTP3 measurement around +4–5%, but that benchmark predates this watch window, so it is **not** promoted as fresh performance evidence.

### Transfer to Metal

Even without CUDA graphs, the same identity rule applies to Metal/JIT caches:

`semantic phase + output contract + row/depth geometry + kernel route` is part of compile/cache identity.

Draft, verify, catch-up and ordinary decode should not accidentally ping-pong one specialization slot when their graph/topology differs.

---

## Promoted lifecycle correctness — vLLM #57163: quant side state can disappear across sleep/reload

Source PR created: `2026-09-16 11:11:32 UTC`.

`CompressedTensorsKVCacheMethod` rebound calibrated `_q_scale/_k_scale/_v_scale` values from buffers into parameters. `sleep(level=2)` only snapshots named buffers before discarding the allocation, so those scales were omitted and returned as zero after a weights-only reload.

Observed failure included NaN logprobs and wrong tokens. On one characterized checkpoint all 96 affected scales returned as zero before the fix; after restoring the buffer registration invariant, 36/36 rounds were bit-exact against the never-slept control. The PR also notes that a tiny ~4.657e-09 injected scale perturbation could flip a greedy decision, so approximate restoration is not an adequate certificate.

### Promoted rule

Lifecycle identity includes registration/ownership metadata, not only tensor names and values. For any sleep/offload/reload/checkpoint path, census all persistent side state:

`weight / scale / zero-point / recurrent state / cache sidecar -> registration class -> saved by lifecycle operation? -> restored bit-exact?`.

This matters for future model reloads and runner orchestration even if our first dual-M1 campaign keeps both processes resident.

---

## Scoped QSA/indexer updates — vLLM #57206 and #57202

### #57206 — prefill selector eligibility is chunk-local

Created `2026-09-16 16:39:26 UTC`, seven minutes before cutoff.

The new prefill DeepSelect path is eligible only for specific chunk geometry: one request in the indexer chunk, supported alignment/device, and no incompatible context parallelism. Multi-request chunks fall back, although a multi-request batch can still benefit if the planner splits requests into independent chunks.

The PR quotes strong earlier GB200 kernel profiles, but explicitly labels them earlier validation and not fresh standalone E2E measurements. We therefore promote the routing rule, not the old speed numbers.

Rule: QSA/indexer route identity includes **request multiplicity within the chunk, causal row start/end, CP mode, alignment and selected-K**, not just total context length.

Tie qualification still needs deterministic membership/order where our runtime promises it; matching selected scores alone is weaker evidence.

### #57202 — launch partitions should be bounded by work available

Created `2026-09-16 16:01:51 UTC` as a draft. It caps score/top-k producer counts from already CPU-visible page/block bounds instead of instantiating maximum launch geometry for short contexts. No new GPU/performance run accompanies the publication, so this is a test-plan transfer only.

Rule: derive launch topology from **available work**, not configured maxima, when the bound is already known without device synchronization.

---

## Screened but not target-moving

### vLLM #57162 — ROCm sampler failure on Flash-Next

Created `2026-09-16 11:08:27 UTC`, just after the previous boundary. AITER's top-k/top-p sampler segfaulted on MI300X/gfx942 even with eager execution; falling back to native sampling restored serving and produced normal GSM8K results. Useful backend-admission evidence, but it does not transfer directly to our Metal target.

### Fresh HF/community pages

Search surfaced current-index pages for:
- M3 Ultra oQ6e/oQ8e Flash-Next packs;
- Rapid-MLX Flash-Next 4-bit;
- M3 Max low-bit Flash packs;
- RTX5070Ti Flash-Next/EXL3 community benchmarks;
- older DS4-0731 oMLX comparisons.

Several contain useful numbers, including long-context Apple and 5070Ti receipts, but the measurement/source timestamps are older or not independently qualified inside this exact window. Crawler freshness is not measurement freshness. None is promoted here.

---

## Implementation consequences for the dual-M1 Flash campaign

The new findings strengthen the first-pass implementation checklist:

1. **PP stage interface:** enumerate all deferred HC/mixer state and test sender-side canonicalization before deciding what crosses TB4.
2. **MTP weight provenance:** certify drafter embeddings/projections on the actual rank that executes them; do not infer from target-model ownership.
3. **Dynamic MTP state transitions:** test late join, park/resume, split/merge, cancellation and staggered finish without replaying committed history.
4. **Cache conversion:** every heterogeneous cache class gets cold/warm batch-conversion and rollback tests.
5. **Memory admission:** profile/warmup workspace follows actual backend reachable geometry; record transient and settled allocator peaks separately.
6. **Prefix proof vs reuse:** keep proof/search margin distinct from accepted reusable prefix.
7. **Scratch billing:** multiply logical rows by physical sidecar/view multiplicity.
8. **Compile/graph identity:** draft/verify/catch-up/ordinary phases retain separate stable identities where topology differs.
9. **Benchmark validity:** failed or incomplete runs are excluded by failing the cell, never by quietly counting fewer tokens.
10. **Lifecycle side state:** if sleep/reload/offload enters the runner workflow, certify scales and sidecars bit-exact across the transition.

These rules change how we build and certify the system, but they do not justify changing the planning targets before exact dual-M1 measurements exist.

## Planning interpretation

For Flash-Next dual M1 Max64/TB4:
- `<30 tok/s @ ~128K`: important failure;
- `30–34`: below desired mature system;
- `35–39`: decent but keep tuning;
- `40–45`: realistic core success range;
- `45–50`: good stretch;
- `50–60`: upside only if the major mechanisms stack; not promised and not canonical.

No evidence in this window justifies moving the **40 @ ~128K / 400 cold PP** planning target.

## New hard source-freshness boundary

`2026-09-16 16:46:32 UTC`

The next complete pass must evaluate substantive source/measurement activity **strictly after** this timestamp. Crawler time, merge-only time and rediscovery of older measurements do not qualify.