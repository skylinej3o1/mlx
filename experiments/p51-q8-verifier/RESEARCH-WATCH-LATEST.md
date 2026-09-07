# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1510.md`

   **The 15:10 note is authoritative for the oMLX #3494 attribution correction, physical recurrent-checkpoint materialization/nullness, restored-boundary finite-state/logit certification, persistent request-slot ownership, state-index stride handling, overlapped-step happens-before ordering, and PP+MTP distributed-state certification. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-0655.md` — recurrent tape/refold MTP optimization candidate, multi-step MTP cache restore, content-addressed distributed model identity, explicit recurrent-layer manifests and graph/compile route provenance. **Its stock-oMLX #3494 attribution is superseded by the 15:10 correction.**
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-2333.md` — physical recurrent-block concurrency, MLX lazy-phase materialization, request-row metadata ownership, real-consumer cache publication, offload-slot ownership and agent qualification;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1951.md` — MTP/recurrent capacity hypothesis, no-MTP batch-composition certification, version-qualified long-context small-N routing and greedy benchmark answer-equivalence;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1832.md` — corrected GDN baseline semantics, typed recurrent/attention/draft cache geometry, warm unified-KV PP qualification, persistent-vs-draft state ownership, full-vector frontier validation and byte-faithful session snapshots;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1245.md` — QSA tie-set correctness, PLE request/step epoch ownership, Apple batch-composition invariance, stochastic speculative-sampling certification, warm-slot PP and small-N routing;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0956.md` — eviction/pause progress, chunk-faithful MTP reconciliation, QSA known-horizon reservation, route-aware memory accounting, immediate-follow-up cache-store freshness and ds4 Flash mining;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0658.md` — actual MTP scheduler occupancy, canonical recurrent/attention first-repeat cache boundaries, realistic-depth Apple Flash attribution and CUDA backend-placement provenance;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0243.md` — whole-round speculative economics, marginal multi-position verify cost and QSA selected-set/order determinism;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1943.md` — speculative-checkpoint provenance, greedy verifier-only equivalence and first-repeat MTP cache backfill;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1512.md` — real-agent cache-capture efficacy, MTP-head/vocabulary ordering, reusable scratch and TG-log provenance;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1200.md` — ordinary recurrent rollback, per-slot MTP context sizing, AProjQ4 PP semantics, M1/M2 FP16 activation lane and persistent runtime identity.

5. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain the dated deltas newer than that point when reconstructing the evidence chain.

6. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 15:10 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-07 15:10 ET

Starting freshness boundary: `6d9161e180d04667c3f2eea4360cf05520704154` / **2026-09-07 11:17:04 UTC**.

## UPDATE / correction

### oMLX #3494 — do not attribute the cold-head failure to stock oMLX

The reporter traced the bad priming handoff to the reporter's own open batched-verify patch path, not stock oMLX main/v0.6.4 or PR #3469. The custom hook dropped a primed context into an adoption queue whose consumer was not reachable on every control-flow arm.

**Standing correction:** keep a custom/experimental primed-state handoff test, but do not carry a standing claim that stock oMLX has the reported first-long-prefill failure.

## FRESH / material

### vLLM #55766 — restored recurrent boundary can poison later generation

A Qwen3.8-27B TP2 prefix-cache reproducer reports a deterministic bad restored GDN checkpoint producing all-NaN logits on a later request. Cache salt or shifting the reusable boundary avoids the failure; preserving the same hit preserves it.

**Promotion:** a reusable recurrent boundary is certified only if its state physically exists, restored state/logits are finite, semantic/frontier evidence matches, and generation crosses at least one full fresh block after restore.

### LMCache #5004 — unmaterialized recurrent boundaries are null state

With MTP, a merged final full block + tail can leave no recurrent state physically written at an intermediate aligned boundary. LMCache previously retained a moved speculative block there and later restored it as a valid checkpoint. The fix clears the old slot to null and stops the reusable frontier unless every required object group physically exists.

Direct validation on the reported 2x RTX 5090 / Qwen3.5 hybrid configuration restores MTP-on output identity after the fix. Treat this as **mechanism-transfer evidence** for Apple Flash.

**Promotion:** physical checkpoint existence/materialization is typed state. Null/unwritten boundaries stop reuse.

### vLLM #53613 UPDATE — overlapping serving requires happens-before before mutation

Async/overlapped serving could mutate block tables and speculative/recurrent metadata while the previous step's speculative postprocess still consumed them. The proposed fix waits on the prior accepted-token/postprocess event before mutation.

**Promotion:** before arrivals, retirements, compaction, block-table rewrites or state-index changes, prove the previous consumer has completed.

### vLLM #46994 UPDATE — PP+MTP is one distributed state machine

The current PP+MTP work documents multiple independent failure classes: collective-width mismatch, missing draft-token relay to non-last PP ranks, stale sparse/indexer-buffer ownership and missing last-stage draft projection, in addition to model-interface support.

**Promotion:** certify PP+MTP jointly. Every rank proves collective shape/op order, every consumer receives the same draft tokens, sparse/indexer buffers retain live ownership, and the last-stage draft head/projection is semantically correct.

## BACKFILL / high-value Flash-specific

### vLLM #55506 — persistent request-slot identity beats transient batch-row identity

Flash-Next + PP>=2 + MTP + prefix cache failed at the 2 -> 3 concurrency transition when persistent recurrent/speculative state was indexed through a stale batch-row mapping. Reindexing by persistent request slot removed the reported loops and recovered acceptance.

**Promotion:** persistent state belongs to persistent request/session slots; explicitly test c1/c2/c3/c4, especially 2 -> 3, unequal prompts and arrivals/retirements.

### vLLM #55467 — state-index tensors may be strided views

The Flash-Next PLE path consumed a strided state-index view as if contiguous when MTP configured multiple columns per request, corrupting simultaneous prefill rows after row 0. The fix honors the actual stride.

**Promotion:** state-index stride is semantic metadata. Honor it or explicitly materialize a contiguous copy and prove identity. Test simultaneous prefill c2/c3/c5.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Current high-level order:

1. pinned historical llama control;
2. corrected-GDN semantic baseline + explicit recurrent/full-attention manifest;
3. exact PP2/layer-owned baseline; TP2 control;
4. ordinary no-spec recurrent rollback / growing-session correctness;
5. typed cache/state-grid identity + unequal-grid restore;
6. no-MTP c1/c2/c3/c4 with persistent request-slot ownership;
7. state-index stride/materialization oracle, including simultaneous prefill c2/c3/c5;
8. model/tokenizer/runtime/GDN/content identity across both nodes;
9. cold-first request + PLE/state epoch ownership;
10. QSA selected-set/tie/order oracle;
11. real-agent cache capture + canonical reusable boundary;
12. physical checkpoint-existence/nullness oracle;
13. async store -> real follower + eviction/pause progress;
14. restored-boundary finite-state/logit + frontier/state + one-full-fresh-block gate;
15. warm-slot PP + Metal interior-mask-skip proof;
16. realistic-depth + charged-phase profiler with MLX carry materialization;
17. QSA horizon / route / footprint + PLE residency;
18. chunk-faithful MTP reconcile;
19. **freeze pre-verify snapshot / commit / replay semantic baseline**;
20. **only after replay correctness freeze: tape/refold A/B**;
21. MTP off/on physical recurrent-capacity accounting;
22. PP+MTP distributed-state certification;
23. overlapped-step happens-before certification;
24. per-slot draft context + adversarial isolation, especially c2 -> c3;
25. sampler-law, strict benchmark identity and full-vector/state fingerprints;
26. session byte identity + semantic restore; concurrent pure-prefill isolation;
27. approximate M1/M2 FP16 lane only after exact freeze;
28. compiled B2/B4; combine passing mechanisms; long prefill while other sessions decode.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the Qwen resident baseline and Tiel Q4/Q5 partial-expert-offload plan using 64 GB host RAM. Record realized placement/backend provenance, offload-slot ownership, VRAM/context headroom and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External serving findings do not rewrite frozen P69 evidence.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as topology/mechanism evidence until sustained current-head exact dual-M1 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- A reusable recurrent boundary exists only if its state was physically materialized.
- Null/unmaterialized boundaries are first-class typed state and stop reuse.
- A cache hit is not a correctness proof; restored state and logits must be finite and semantically checked.
- Persistent recurrent/speculative state belongs to persistent request/session slots, never transient batch rows.
- State-index stride is semantic metadata; kernels may not assume contiguity.
- Overlapped scheduling requires explicit happens-before edges before shared-state mutation.
- PP+MTP is one distributed state machine and is certified jointly.
- Experimental/custom patch failures are not promoted to stock-runtime claims without provenance.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for the replay correctness oracle.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
