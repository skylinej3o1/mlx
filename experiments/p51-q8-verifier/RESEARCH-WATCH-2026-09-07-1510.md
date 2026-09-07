# External runtime research watch — 2026-09-07 15:10 ET

Starting freshness boundary: `6d9161e180d04667c3f2eea4360cf05520704154` / **2026-09-07 11:17:04 UTC**.

## Classification

**Material certification / state-identity update. No performance target moves.**

This pass adds one correction to the immediately previous watch, two fresh hybrid-cache / recurrent-state findings, two post-cutoff PP+MTP ordering/ownership updates, and two older but high-value Flash-specific backfills.

No fresh sustained exact receipt was found for the target dual-M1 Flash topology, dual-M1 DS4-0731, single-M1-Max Qwen3.8-27B, RTX 5070 Ti Qwen3.8-27B, or RTX 5070 Ti Tiel Coder.

---

# UPDATE / CORRECTION

## oMLX #3494 — previous cold-prefill race attribution was too broad

The previous 06:55 watch treated the reported first-long-prefill MTP collapse as an oMLX eager-dispatch / prefill-to-speculation handoff race candidate.

The reporter subsequently found a deterministic mechanism and then corrected the attribution: the problematic `patched_extend` / `_ADOPT_QUEUE` / `drop_ctx()` hook comes from the reporter's own open **PR #3265 batched-verify patch**, not stock oMLX main, v0.6.4, or PR #3469.

Mechanism in that experimental path:

- prompt priming correctly folds the prompt into the MTP head;
- the experimental hook removes the primed context and queues it for adoption;
- the queue consumer is reachable only on the batched-verify path;
- when that consumer is not eligible, the first MTP cycles begin cold / position-misaligned and the adaptive controller can park before recovery.

Stock oMLX was independently reported to preserve full prompt priming on first MTP activation.

**Correction:** do not carry a standing claim that stock oMLX has a cold-long-prefill first-cycle race. Keep the test only as an experimental-batched-verify / custom-hook certification case.

**Promotion:** any optimization that transfers ownership of primed recurrent/speculative state must prove that every producer handoff has an eligible consumer on all control-flow arms. A queue is not ownership unless its consumer is reachable.

---

# FRESH / material

## vLLM #55766 — deterministic bad GDN checkpoint can poison a later prefix-cache restore with NaN logits

Qwen3.8-27B BF16, TP2 on 2x H100, vLLM 0.28.0, prefix caching, hybrid GDN+attention, align-mode recurrent cache.

A two-request reproducer shows a block-aligned prefix hit can restore a bad recurrent checkpoint when the previous prefill ended a small even number of tokens past the aligned boundary. The later request returns all-NaN logits from its first generation step and can emit repeated token-id 0 until max tokens. Retrying the identical request fails identically until the cache turns over.

Important controls:

- per-request cache salt -> clean;
- prepending tokens so the reusable prefix shifts -> clean;
- appending tokens while preserving the same hit -> still fails;
- a short post-restore prefill is clean; the failure requires enough fresh prefill after the restored boundary.

The issue has no engine fix yet and does not establish the root cause, but the carrier is strongly tied to the restored hybrid-state boundary rather than ordinary sampling.

**Promotion:** cache/session certification now includes, at every reusable recurrent boundary:

1. physical state existence / materialization;
2. finite state and finite logits immediately after restore;
3. exact/reference frontier or full-vector/state fingerprint where available;
4. a continuation long enough to cross at least one full fresh block after the restored boundary;
5. retry behavior after the first failed restore so a poisoned cache entry cannot masquerade as a transient model error.

A cache hit plus coherent text is not sufficient evidence.

## LMCache #5004 — unmaterialized recurrent boundaries must be represented as null, never as reusable state

PR #5004 fixes the multi-step MTP restore corruption family from #4984.

With MTP, vLLM can merge a prompt's final full aligned block and tail into one prefill step. In that shape **no recurrent state is physically written at the intermediate full-block boundary**. vLLM's own block list represents that slot as null and moves the speculative scratch block onward, but LMCache's request tracker previously retained the moved block in the old slot and later restored it as if it were a valid recurrent checkpoint.

The fix detects a moved block ID, clears the old slot to null, and allows a cache hit to advance only through chunks for which all required object groups physically exist.

Direct validation on 2x RTX 5090, vLLM 0.28.0, Qwen3.5-0.8B hybrid, align mode:

- MTP on, before: output differs, hit 2240;
- MTP on, after: output identical, hit 1680;
- MTP off: output identical, hit 2176 before and after.

This is direct evidence for that CUDA/LMCache configuration and **mechanism-transfer evidence** for our Apple Flash cache design.

**Promotion:** checkpoint *existence* is typed state. If a recurrent boundary was not physically materialized, encode it as null/unavailable and stop the reusable frontier before it. Never infer validity from block identity, sequence position, or a neighboring speculative scratch allocation.

## vLLM #53613 UPDATE — overlapping steps require an explicit happens-before edge before state mutation

Updated post-cutoff on 2026-09-07.

Under async scheduling or another `max_concurrent_batches > 1` shape, the current step can begin `_update_states` while the previous step's speculative postprocess is still using persistent block tables, staged recurrent metadata, and accepted-token buffers.

The proposed fix waits on the previous accepted-token/postprocess event **before any mutation** of those shared structures.

Field evidence is hardware/runtime-specific, but substantial:

- 2x RTX 3090 TP2 hybrid GDN+MTP4: stock crash at 10,873 generated tokens; another partial fix alone at 8,446; ordering fix clean through 42,769 generated tokens / 80 turns;
- direct GB10 probes show the prior postprocess still unlanded when next-step mutation starts in >99% of steady-state steps on the affected decode backend;
- throughput A/B was too noisy to resolve a small cost, so this remains correctness/ordering evidence rather than a speed claim.

**Promotion:** overlapping serving must prove an explicit happens-before relationship for every shared recurrent/speculative metadata buffer before request arrival, retirement, compaction, block-table rewrite, or state-index mutation.

## vLLM #46994 UPDATE — PP+MTP exposes multiple independent distributed-state failure classes

Updated post-cutoff on 2026-09-07.

The V2 PP+MTP work now documents five separate failure classes rather than one generic "PP speculation" bug:

1. missing MTP draft-model PP interface support;
2. sampled-token collective width mismatch causing a PP hang;
3. draft tokens not relayed to non-last PP ranks, so verifier inputs differ across stages;
4. stale sparse-attention top-k buffer ownership after model-head sharing, depressing acceptance from ~27-33% to 84.4% after dynamic ownership was restored in the reported GLM-5.2 TP4/PP2 run;
5. missing last-stage draft projection on Qwen3.5/3.6, producing near-random drafts.

Cross-model Qwen3.5/3.6 PP2 validation reports high K1/K2/K3 acceptance after the fixes, but this is not Qwen3.8-Flash-Next QSA and is **mechanism-transfer evidence only** for our target.

**Promotion:** PP+MTP is certified as one distributed state machine, not as "PP passes" plus "MTP passes." Every PP stage must prove identical collective shape/op ordering, explicit relay of draft tokens to every consumer, live ownership of sparse-attention/indexer buffers, and correct last-stage draft-head/projection semantics.

---

# BACKFILL / high-value Flash-specific evidence

## vLLM #55506 — persistent request-slot identity, not ephemeral batch-row identity

This predates the current cutoff but is directly relevant to the dual-M1 PP2 appliance.

Flash-Next + PP>=2 + MTP + prefix cache failed sharply when concurrency crossed **2 -> 3**. The speculative context had captured batch-ordered recurrent block tables, but under PP a rank can consume them after the transient batch mapping has changed.

Using an ephemeral batch row to index persistent recurrent/speculative state caused repeated-token loops, NaN-derived token 1023, and acceptance collapse. Reindexing the tables by persistent request slot eliminated the reported failures.

Reported validation on PP4 / MTP4:

- before: 16/48 looped requests;
- after: 0/56;
- acceptance recovered from ~2.80 accepted tokens/step to ~4.90-5.00;
- long-context needle checks remained exact.

**Promotion:** every persistent recurrent/speculative state object is owned by a persistent request/session slot, never by a transient batch row. Explicitly test the 2 -> 3 transition, unequal prompt lengths, arrivals/retirements, and slot compaction.

## vLLM #55467 — PLE state-index vectors can be strided views

This also predates the current cutoff.

With MTP configured, the Mamba block table has multiple columns per request. Selecting column 0 yields a **strided** state-index view. The Flash-Next PLE short-conv kernel indexed it as if contiguous, so prefill rows after row 0 could write into request 0's speculative checkpoint slots.

The fix honors the actual state-index stride.

Reported GB10 simultaneous-prefill validation:

- stock: 30-50% of cells contained a corrupted request;
- fixed: 0/20 corrupted cells across c=2, c=3 and c=5.

**Promotion:** state-index tensors are not assumed contiguous. Either consume their stride exactly or materialize a contiguous copy and prove identity. Add simultaneous prefill c2/c3/c5 with MTP configured.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash-Next:** no fresh sustained exact 2x M1 Max 64 / TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max 64 / TB4.
- **Single M1 Max64 Qwen3.8-27B:** no fresh exact target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt.

Therefore `RESEARCH-TARGETS.md` remains untouched.

Canonical centers remain:

| Lane | TG | cold PP |
|---|---:|---:|
| Flash-Next 2x M1 Max64 / TB4 | **40** | **400** |
| Qwen3.8-27B M1 Max64 | **25** | **110 native/exact-runtime** |
| Qwen3.8-27B RTX 5070 Ti16 | **120** | **250** |
| DS4-0731 2x M1 Max64 / TB4 | **15** | **180** |

These are **planning targets**, not measurements.

---

# Dual-M1 Flash consequences / revised certification order

Keep PP2/layer ownership primary and TP2 as control.

1. historical pinned llama control;
2. corrected-GDN semantic baseline + explicit recurrent/full-attention layer manifest;
3. exact PP2/layer-owned baseline; TP2 control;
4. ordinary no-spec recurrent rollback / growing-session correctness;
5. typed cache/state-grid identity + unequal-grid restore;
6. plain no-MTP batch-composition invariance at c1/c2/c3/c4 with persistent request-slot ownership;
7. explicit state-index stride/materialization oracle, including simultaneous prefill c2/c3/c5;
8. model/tokenizer/runtime/GDN/content identity across both nodes;
9. cold-first request + PLE/state epoch ownership;
10. QSA selected-set/tie/order oracle;
11. large-schema + parallel-tool-call agent correctness;
12. real-agent cache capture + canonical reusable recurrent/attention boundary;
13. **physical checkpoint-existence/nullness oracle: reusable frontier advances only through materially written state**;
14. async store -> real concurrent follower usability and forced eviction/pause progress;
15. **restored-boundary finite-state / finite-logit gate + exact frontier/state fingerprint + one-full-fresh-block continuation**;
16. warm-slot PP + Metal interior-mask-skip proof;
17. realistic-depth profiler + long-context small-N route/version matrix;
18. charged-phase profiler with explicit MLX carry materialization;
19. QSA known-horizon reservation + route/footprint accounting;
20. PLE residency/page-cache/direct-read with explicit logical slot ownership;
21. chunk-faithful MTP reconcile;
22. **pre-verify snapshot / commit / replay semantic baseline** with temporary drafts excluded from persistent history;
23. **only after #22 is frozen: tape/refold candidate A/B versus replay**;
24. MTP off/on physical recurrent-capacity accounting;
25. **PP+MTP distributed-state gate: fixed collective widths/op counts, draft-token relay to every consumer, live sparse-buffer ownership, last-stage draft-head/projection semantics**;
26. **overlapped-step happens-before gate before any shared state mutation**;
27. per-slot draft context + adversarial multi-slot isolation, especially c2 -> c3;
28. production sampler-law certification;
29. strict greedy benchmark identity + near-tie diagnostic classifier;
30. full-vector frontier/state fingerprints;
31. file/memory session byte identity + semantic restore equivalence;
32. concurrent pure-prefill isolation;
33. M1/M2 activation-FP16 approximate lane after exact freeze;
34. compiled B2/B4; combine passing mechanisms; long prefill while other sessions decode.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot state isolation, physical recurrent capacity and PP+MTP distributed ownership are proven.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

---

# Other lanes

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the Qwen resident baseline. Tiel remains Q4/Q5 partial expert offload using 64 GB host RAM, with Q6 as an optional quality control. Record realized placement/backend provenance, offload-slot ownership, VRAM/context headroom and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next only from existing profiling.** External serving findings do not rewrite frozen verifier evidence.

## Dual-M1 DS4-0731

No target movement. Continue using DS4 as mechanism/certification evidence until sustained current-head exact dual-M1 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- A reusable recurrent boundary exists only if its state was physically materialized.
- Null/unmaterialized boundaries are first-class typed state and stop reuse.
- A cache hit is not a correctness proof; restored state and logits must be finite and semantically checked.
- Persistent recurrent/speculative state belongs to persistent request/session slots, never transient batch rows.
- State-index strides are semantic metadata; kernels may not assume contiguity.
- Overlapped scheduling requires explicit happens-before edges before shared-state mutation.
- PP+MTP is one distributed state machine and is certified jointly.
- Experimental/custom patch failures are not promoted to stock-runtime claims without provenance.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for the replay correctness oracle.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
