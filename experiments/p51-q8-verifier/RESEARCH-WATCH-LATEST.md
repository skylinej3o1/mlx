# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-2333.md`

   **The 23:33 note is authoritative for physical recurrent-block concurrency corroboration, MLX lazy-phase materialization, request-row metadata ownership, real-consumer cache publication, offload slot ownership, strict benchmark identity vs near-tie diagnosis, and large-schema parallel-tool agent qualification. It moves no performance target.**

4. The immediately previous deltas remain essential:

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

**The 23:33 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-06 23:33 ET

Starting freshness boundary: `d2ca23f5082b0a2dfede97fe480c8ddbe26cc1b7` / **2026-09-06 23:55:24 UTC**.

## FRESH / material

### vLLM #55533 / WIP #55617 UPDATE — recurrent-block capacity strongly corroborates the MTP concurrency cap

An independent 48 GB Qwen3.8-27B experiment pinned physical recurrent/KV capacity and observed scheduled width track block count almost exactly:

- 22–28 blocks -> 3 requests;
- 29–35 -> 4;
- 36 -> 5;
- 43 -> 6;
- 57 -> all 8.

This is strong corroboration, not yet the original reporter's decisive MTP-on/off proof and not a merged fix.

**Promotion:** B2-B4 certification records physical state blocks, per-request footprint, speculative reserve, configured slots, actually scheduled sequences, emitted tokens/sequence/iteration, aggregate TG and TTFT. Configured or queued slots do not count as active concurrency.

### rMLX #532 / `e14a1d5c...` — MLX speculative sub-phase clocks require explicit carry materialization

Charged profiling found lazy carry work crossing timing boundaries and materially contaminating attribution. Corrected drafter over-attribution was roughly 10% DFlash2, 58% MTP sidecar and 8% Gemma4 assistant on the reported host.

**Promotion:** draft/verify/rollback/capture timings are inadmissible for optimization ordering unless all state carried across each measured boundary is proven materialized.

### vLLM #55637 — request-row metadata is typed concurrent state

Fresh sparse-attention debugging shows producer/consumer request-row cardinality disagreement can map an invalid logical request onto another valid KV row instead of immediately crashing.

**Promotion:** bound request-row and block-column indices at both producer and consumer seams; impossible request IDs fail closed and never alias another request. Include graph warmup and request arrival/retirement transitions.

### rMLX #533 / `3b18eb9a...` — cache publication requires a real concurrent consumer

Bookkeeping publication order alone does not prove a newly stored prefix is usable. The strengthened race drives a follower through the seam and checks restored content / next-token behavior.

**Promotion:** async-cache certification requires store ordering, concurrent follower consumption, semantic/state identity and one canonical telemetry record per logical request.

### vLLM #54975 / `1f778486...` — offload buffers require persistent slot ownership

Circular prefetch wraparound could refill a static slot belonging to another logical owner. The fix preserves ownership class across prefetch steps.

**Promotion:** Tiel expert offload, PLE offload and SSD/host-resident paths record a logical-owner -> physical-slot invariant. This is transfer evidence, not target-rig speed evidence.

### rMLX #531 / `2275ab878...` — strict benchmark identity and near-tie diagnosis are separate layers

A near-tie arithmetic divergence can change greedy output without proving state corruption.

**Promotion:** keep whole-completion identity as a strict greedy benchmark-admission gate, but diagnose failures with first divergent frontier, top-two margin and full-vector/state evidence before labeling corruption.

### llama.cpp #28522 — large-schema parallel-tool qualification added to agent readiness

A fresh multi-Qwen report describes malformed parallel tool calls and a hang on a ~48-optional-parameter tool schema; smaller schemas work and MTP-off did not fix it. A contributor could not reproduce from the schema alone, so mechanism remains unproven.

**Promotion:** qualify large optional schemas, compiled grammar field coverage, parallel tool calls, duplicate/missing keys, timeout/hang behavior and an MTP-off control. Treat as runtime/tool-grammar evidence, not model-quality evidence.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Current order:

1. historical pinned llama control;
2. corrected-GDN semantic baseline + reference frontier/state certification;
3. exact PP2/layer-owned baseline; TP2 control;
4. ordinary no-spec recurrent rollback / growing-session correctness;
5. typed cache/state-grid identity + unequal-grid restore;
6. **plain no-MTP batch-composition invariance at concurrency 1/2/3/4, including request-row cardinality/bounds and actual scheduled occupancy**;
7. cache-layout/handler + model/tokenizer/runtime/GDN identity;
8. cold-first request + PLE/state epoch ownership;
9. QSA selected-set/tie/order oracle;
10. **large-schema + parallel-tool-call agent correctness gate**;
11. real-agent cache capture + canonical recurrent/attention reusable boundary;
12. **async store -> real concurrent follower usability**, forced eviction/pause progress;
13. warm-slot PP + Metal interior-mask-skip proof;
14. realistic-depth profiler + long-context small-N route/version matrix;
15. **charged-phase profiler with explicit MLX carry-materialization proof**;
16. QSA known-horizon reservation + route/footprint accounting;
17. PLE residency/page-cache/direct-read with explicit slot ownership;
18. chunk-faithful MTP reconcile;
19. pre-verify snapshot / commit / replay with temporary drafts excluded from persistent history;
20. **MTP off/on physical recurrent-capacity accounting: total blocks, per-request blocks, speculative reserve and actually scheduled sequences**;
21. per-slot draft context + adversarial multi-slot isolation;
22. production sampler-law certification;
23. strict greedy benchmark identity + near-tie diagnostic classifier;
24. full-vector frontier/state fingerprints;
25. file/memory session byte identity + semantic restore equivalence;
26. concurrent pure-prefill isolation;
27. M1/M2 activation-FP16 approximate lane after exact freeze;
28. compiled B2/B4; combine passing mechanisms; long prefill while other sessions decode.

Safe serving remains profitable singleton MTP + plain concurrent work until multi-slot state isolation and physical-capacity behavior are proven.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct state. Configured, admitted or queued slots alone do not count.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the Qwen resident baseline; test Tiel Q4/Q5 partial expert offload with 64 GB host RAM. Add explicit offload-slot ownership, realized placement/backend provenance and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External serving findings do not silently rewrite frozen evidence.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as mechanism/certification evidence until sustained current-head exact dual-M1 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- Physical recurrent-state capacity is part of concurrency, not merely a memory statistic.
- Configured/admitted slots do not count without simultaneous scheduling and independent correct state.
- MLX sub-phase clocks require explicit lazy-carry materialization.
- Request-row metadata carries typed ownership and is bounded at producer and consumer seams.
- Invalid request IDs fail closed; they never alias another valid request.
- Cache publication is not proven until a real concurrent follower consumes it correctly.
- Static offload buffers require persistent logical slot ownership across wraparound.
- Strict greedy benchmark identity and semantic near-tie classification are different evidence layers.
- Agent readiness includes large-schema grammar compilation, parallel tool semantics and hang guards.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
