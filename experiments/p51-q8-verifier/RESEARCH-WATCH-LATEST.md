# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-0655.md`

   **The 06:55 note is authoritative for recurrent tape/refold MTP optimization, cold long-prefill -> first-spec-cycle handoff, multi-step MTP cache restore, content-addressed distributed model identity, explicit recurrent-layer manifests and graph/compile route provenance. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-2333.md` — physical recurrent-block concurrency corroboration, MLX lazy-phase materialization, request-row metadata ownership, real-consumer cache publication, offload-slot ownership and agent qualification;
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

**The 06:55 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-07 06:55 ET

Starting freshness boundary: `377501fa9c7bec9662803c926d97f6aad3e0c1c5` / **2026-09-07 03:42:29 UTC**.

## FRESH / material

### rMLX `0cec5a187fb2716d5f45c4bd105b572b6da0aa6e` — recurrent tape/refold removes the second full-model replay on partial MTP rounds

Partial speculative acceptance previously rebuilt recurrent state by restoring the pre-round snapshot and replaying the accepted prefix through the full layer stack, causing another model-weight read. The new path tapes causal recurrent inputs during the original round and refolds only the accepted prefix through the recurrence kernel.

Real recurrent-stack tests report exact agreement with the replay it replaced at every accepted length for both one-verify-forward and forward-per-token draft geometry.

**Promotion:** after Flash replay correctness is frozen, test recurrent tape/refold before deeper drafting. Measure whole-round wall time, acceptance, refold cost, weight traffic and semantic equivalence.

### oMLX #3494 — cold long-prefill -> first MTP verify cycle can collapse under eager-dispatch contention

On M3 Ultra / Flash-Next, the first MTP cycle after >=16K prefill intermittently accepted 0/6 under eager dispatch. The reported collapses occurred on first long-prefill requests under contention; quiet and short-context cases were healthy. Root cause remains unproven.

**Promotion:** certify a distinct cold engine -> short warmup -> first long prefill -> first MTP-cycle seam under quiet and contended conditions, including explicit state materialization before speculative step 1.

### LMCache #4984 — multi-step cached restore requires a separate MTP-on gate

After a base hybrid-layout fix, no-MTP long cached restores were reported bit-identical, including multi-chunk and 258K cases. The same base with MTP on was 0/10 identical when the retrieve crossed more than one scheduler step; single-step retrieves were fine.

**Promotion:** external/session-cache qualification requires completed-store proof, no-MTP multi-step restore equivalence, then MTP-on multi-step restore equivalence. Single-step success is insufficient.

### Mesh-LLM #1680 — distributed model identity must be content/revision-addressed

Identical local GGUF bytes on two nodes failed split eligibility because synthetic identity included file mtime. Matching mtimes made the nodes agree. The reported M4+M5 rate is not dual-M1 evidence.

**Promotion:** distributed startup identity derives from content digest / canonical revision plus tokenizer/runtime identity; path and mtime never define semantic model identity.

### llama.cpp `9a7570587ce908b0073a0458877205b80627f393` — explicit recurrent-layer manifests are now conversion metadata

The converter now emits explicit recurrent-layer metadata instead of relying only on a uniform full-attention interval. A non-uniform Qwen3.8-27B test reported zero layer-type mismatches after the fix. Real-MTP padding still needs an exact check.

**Promotion:** conversion/startup certification compares explicit recurrent/full-attention manifests against runtime interpretation and tests MTP-padded metadata.

### vLLM #55272 — graph/compile/eager route is benchmark provenance

The NVIDIA Flash-Next path removed model-level torch.compile/custom-op wrappers. The PR also reports a large temporary n-gram-table autotune memory peak under the prior route and mixed/noisy throughput changes after removal.

**Promotion:** benchmark receipts stamp graph/compile/eager route and dependency revision; results across execution-route changes are not silently combined.

### ds4 PR #990 UPDATE — Metal Flash port remains a mechanism-mining control, not a target ruler

A single M5 Pro 64 GB Q2+Q8-PLE configuration reports 30-33 TG and 58-73 PP, plus sparse-path equivalence testing below its selection budget. It has no MTP and no serialized recurrent/PLE session state and is proven on only one M5 Pro host.

**Classification:** alternative-runtime / other-hardware mechanism evidence only. It does not calibrate dual-M1 targets.

Useful mining surfaces: QSA pooled selection, PLE row-store/no-cache access, 64 GB residency strategy, GDN gate details and sparse-path equivalence tests.

---

# Focused follow-up status

- **vLLM #55533 / #55617:** no post-cutoff result; prior physical recurrent-block concurrency corroboration remains standing evidence but is not double-counted as fresh.
- **oMLX #3462 / #3464:** no fresh target-rate result surfaced.
- **llama.cpp #25187 / #28425 / #28433 / #28448:** no fresh target-rate result surfaced.
- **Tiel Coder:** no fresh exact RTX 5070 Ti result.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Current high-level order:

1. historical pinned llama control;
2. corrected-GDN semantic baseline + reference frontier/state certification;
3. explicit recurrent/full-attention layer-manifest identity + distributed content-addressed model identity;
4. exact PP2/layer-owned baseline; TP2 control;
5. ordinary no-spec recurrent rollback / growing-session correctness;
6. typed cache/state-grid identity + unequal-grid restore;
7. no-MTP batch-composition invariance at concurrency 1/2/3/4, including actual scheduled occupancy;
8. cold-first request + PLE/state epoch ownership;
9. QSA selected-set/tie/order oracle;
10. real-agent cache capture + canonical reusable boundary + async-store follower tests;
11. **multi-step session/cache restore: no-MTP first, then MTP-on**;
12. realistic-depth profiler + explicit MLX carry materialization;
13. QSA horizon / route / footprint accounting + PLE residency;
14. chunk-faithful MTP reconcile;
15. pre-verify snapshot / commit / replay with temporary drafts excluded from persistent history;
16. **cold long-prefill -> first MTP-cycle handoff under quiet and contention**;
17. MTP off/on physical recurrent-capacity accounting;
18. per-slot draft context + adversarial multi-slot isolation + sampler-law certification;
19. **recurrent tape/refold candidate after replay correctness is frozen**;
20. full-vector/frontier/session fingerprints; approximate FP16 lane only after exact freeze;
21. compiled B2/B4, combine passing mechanisms, long prefill while other sessions decode.

Safe serving remains profitable singleton MTP + plain concurrent work until multi-slot state isolation, physical-capacity behavior and multi-step MTP restore are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct state. Configured, admitted or queued slots alone do not count.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Keep the Qwen resident control and Tiel Q4/Q5 partial-expert-offload plan. Preserve realized backend/placement, offload-slot ownership, whole-round speculative economics and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External serving findings do not rewrite frozen P69 evidence.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as topology/mechanism evidence until sustained current-head exact dual-M1 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- Partial speculative acceptance should not imply a second full model replay when recurrent inputs can be refolded safely.
- A cold long-prefill -> first speculative cycle is a distinct correctness phase and is tested under contention.
- Single-step cache/session restore does not certify multi-step MTP restore.
- Distributed model identity is content/revision identity, never mtime identity.
- Recurrent/full-attention layer layout is explicit model metadata and part of runtime identity.
- Graph/compile/eager route is benchmark provenance.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
