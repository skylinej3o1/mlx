# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1753.md`

   **The 17:53 note is authoritative for actual-resolved MTP block/depth benchmark provenance, post-baseline explicit depth sweeps, QSA low-bit indexer-cache backfill and speculative external-cache group/lifecycle ownership. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1510.md` — oMLX #3494 stock-runtime attribution correction, physical recurrent-checkpoint materialization/nullness, restored-boundary finite-state/logit certification, persistent request-slot ownership, state-index stride, overlapped-step happens-before and PP+MTP distributed-state certification;
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

**The 17:53 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-07 17:53 ET

Starting freshness boundary: `9211221b8d998ff8cfbf67882db4e61c22596d6b` / **2026-09-07 19:24:38 UTC**.

## FRESH / material

### rMLX #540 — actual MTP block/depth is benchmark provenance

A post-boundary MTP change showed that an explicitly requested block could previously be silently narrowed to the checkpoint declaration while the surrounding benchmark/gate still labeled the row with the requested value.

The checkpoint declaration is training/default provenance, not automatically a structural ceiling. A recursively chained MTP head may accept an explicitly deeper request up to the verify-forward ceiling, but depth profitability is an empirical whole-round question.

**Promotion:** record requested depth, checkpoint-declared depth and the engine-reported block actually executed. Reject a benchmark cell if the actual executed block does not match its label.

After the replay semantic baseline is frozen, certify the shipped/default depth first and only then sweep explicitly deeper blocks as separate A/B cells. Each cell carries per-position acceptance, tokens/round, partial/full-accept census, whole-round phase costs, TG/wall and correctness evidence.

Tape/refold remains an orthogonal post-baseline rollback optimization and must be compared at the same resolved depth as replay.

## BACKFILL / useful pre-boundary

### vLLM #54890 — QSA FP8 indexer cache

Flash-Next QSA gained an FP8 E4M3 indexer-cache path with dedicated reference coverage. Treat this as mechanism evidence that QSA/indexer side-cache precision can be optimized separately from the main KV/state path.

**Promotion after exact QSA semantics are frozen:** low-bit QSA/indexer-cache A/B with selected-set/tie/order/frontier-logit correctness plus route/footprint provenance.

### vLLM #52771 — speculative offload lookup/publication needs explicit group and lifecycle ownership

The MTP/EAGLE offload path could erase a valid reusable boundary when the wrong group population was treated as speculative and the mandatory volatile-tail drop consumed the only match. The fix also preserves the rule that a volatile draft tail is withheld while rejection can rewrite it, then becomes publishable when the request finishes.

**Promotion:** external/SSD cache qualification records target/recurrent/attention/draft group identity, stable-vs-volatile lifecycle, actual restored tokens/bytes and warm wall time. Successful stores alone are not evidence of useful reuse.

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

Keep the 15:10 bring-up order, with these incremental changes:

- after exact QSA selected-set/tie/order certification, permit a **separate low-bit QSA/indexer-cache A/B**;
- persistent external/SSD cache qualification includes explicit speculative-group ownership and finish-time stable-tail publication;
- after pre-verify snapshot/commit/replay correctness is frozen, certify **default MTP depth with actual-block provenance**;
- then sweep explicitly deeper MTP blocks as independent cells; requested depth never substitutes for actual executed depth;
- tape/refold A/B uses the same actual resolved depth as its replay control;
- deeper MTP is promoted only if correctness holds and whole-round TG/wall improves.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the Qwen resident baseline and Tiel Q4/Q5 partial-expert-offload plan using 64 GB host RAM. For speculative Qwen rows, actual executed block/depth now joins realized placement/backend, VRAM/context headroom and real coding-agent wall time as mandatory provenance.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External serving findings do not rewrite frozen P69 evidence.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as topology/mechanism evidence until sustained current-head exact dual-M1 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- A benchmark cell is defined by what the engine actually executed, not merely what the CLI requested.
- Checkpoint-declared MTP depth is training/default provenance, not automatically a structural or performance optimum.
- Deeper speculative depth is an explicit correctness + whole-round A/B dimension.
- QSA/indexer cache precision is a separate state surface and is optimized only after deterministic semantic certification.
- Speculative cache/offload state carries explicit group ownership and lifecycle; volatile tails become reusable only after stability.
- The 15:10 oMLX #3494 attribution correction remains authoritative.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for replay correctness.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
