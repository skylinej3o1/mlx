# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0238.md`

   **The 02:38 note is authoritative for the fresh M5-Max Flash-Next Q4_K routed-expert double-buffer/chunk-width A/B, cross-request MTP carry/hidden-state ownership failure, distributed cancellation/cache-agreement lifecycle findings, depth-sensitive QSA `top_k` benchmark provenance and quant-layout-aware ParoQuant/DFlash2 rollback-hook qualification. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-2157.md` — Apple grammar-constrained MTP serving A/B, merged prefill/decode fairness enforcement, distributed sampler-backend ownership/fallback evidence, HC-prefill microbench-vs-E2E correction and Apple MTP-drafter loader CI hardening;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1919.md` — M3-Ultra ds4 Flash-Next prefill-structure A/B: block-history GDN convolution, repeated-work elimination, wider routed-down tiling and retained negative candidates;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1753.md` — actual-resolved MTP block/depth benchmark provenance, post-baseline explicit depth sweeps, QSA low-bit indexer-cache backfill and speculative external-cache group/lifecycle ownership;
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

**The 02:38 pass moves no row.** It adds no sustained physical receipt from an exact target rig.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-08 02:38 ET

Starting freshness boundary: `11996bac754e4818f702b75bd1a060ff010df022` / **2026-09-08 02:04:05 UTC**.

## FRESH / measured Flash prefill transfer evidence

### ds4 #991 / `a30ed072fc9dc77eeba65a4c4d1a6984cc44be74`

On **M5 Max 137 GB**, Qwen3.8 Flash-Next Q4_K routed experts gained about **+3.8%** in the report's contamination-controlled warm-pair analysis from a double-buffered TensorOps `mm_id` staging path. An isolation control with TensorOps but old staging was ~-0.9%, making the double buffering the useful mechanism rather than the API switch itself.

The higher-leverage result is the chunk sweep at a 16K frontier:

- Q2 path: best at **8192** tokens, ~1064 tok/s, ~+35% over the 1024-token convention;
- Q4 path: best at **4096**, ~1000 tok/s, ~2.2x the 1024 result;
- Q4 regressed sharply at 8192 (~537 tok/s).

**Promotion:** chunk width is now an explicit **per-quant/per-kernel/topology sweep**. Sweep it before judging routed-expert kernels, and choose PP2 cluster chunking jointly from stage balance, scratch/occupancy and actual TB4 bubbles/traffic. The M5 percentages do not transfer to M1.

## FRESH / speculative-state ownership

### Atlas #968 — cross-turn MTP carry / hidden rows lacked sufficient provenance

A model-global carry slot and shared hidden-row interval could be reused across requests while proving only prefix/range coverage, not which request/generation owned the state. The repair stamps carry/session identity and hidden intervals with generation ownership and separates "configured" from actually `armed` execution.

The PR explicitly leaves device ordering unproven: a host ownership stamp does not establish the capture/copy -> consumer happens-before relation.

**Promotion:** every cross-turn/cross-request speculative buffer carries owner identity + generation/epoch + valid range; coverage and provenance are separate predicates; common template prefixes are not generic request identity; host ownership and device happens-before are certified independently; composed foreign-write/foreign-read negative controls are mandatory.

## FRESH / distributed PP2 lifecycle

### oMLX #3258 — cancellation / cache-agreement integration review

A fresh restack looked substantially complete but maintainer review still found missing cancellation vote/drain/arm wiring, stale-cancel scoping, terminal response signaling, live/SSD cache maintenance, peer-local path resolution, request-ID propagation and prompt-cache agreement.

The reported repair order is: validate cancel epoch -> complete shared votes -> drain Metal work -> authenticated rank barrier -> arm exact epoch/UID set -> only then permit batch removal. Focused validation after restoration reports 335 passed / 3 skipped; no original two-Mac hardware rerun was available.

**Promotion:** distributed cancellation/cache maintenance are synchronized state-machine transitions. PP2 qualification adds cancellation during prefill/decode, all-request/watchdog cancellation, stale markers/worker restart, rank barrier before reuse, terminal response signaling, loaded/unloaded local+remote cache clear and post-lookup cross-stage prompt-cache agreement.

## FRESH / QSA benchmark provenance

### llama.cpp #28591 — depth-sensitive QSA `top_k`

A fresh benchmark-harness PR exposes `qwen4exp.attention.indexer.top_k` as model metadata in `llama-bench`. Its motivating Vulkan evidence reports the prefill difference for `top_k=1024` versus 2048 growing from about **8% near 29K** to **25% near 120K** context.

**Promotion:** actual indexer `top_k` / selection budget, context depth and realized metadata override become benchmark provenance. Sweep at realistic depths including the ~128K lane and pair speed with selected-set/tie/quality certification; short-context PP cannot establish long-context economics.

## FRESH / bounded Apple quantized-target correctness

### oMLX #3515 — ParoQuant DFlash2 target-op / rollback hooks

A fresh Qwen3.8-27B ParoQuant DFlash2 PR shows that loading and dimensional compatibility are insufficient. In an ablation with real nonzero rotations, suppressing all speculative-hook installation changed the next-token argmax after partial rejection, while correct hook installation preserved it. The PR reports related tests plus earlier M3-Max full-model greedy/forced-rejection/prefix/cancellation/reload validation but explicitly makes **no controlled serving-performance claim**.

**Promotion:** speculative compatibility binds the actual quantized module classes and realized hook/rewrite coverage, not just model dimensions. Forced-rejection rollback and unload/reload re-arming are mandatory. P69 remains isolated.

## UPDATE / screened

- vLLM #55557 has fresh fp8-QSA review corrections around V scaling/normalizer semantics and realistic test-memory construction, but its headline performance/capacity data predates this cutoff. **KNOWN/BACKFILL; no target movement.**
- oMLX #3508 reinforces that source-content identity is not sufficient cache identity when materialized representation geometry depends on transformation/request regime. Useful later multimodal cache rule only.
- rMLX: no post-cutoff PR update.
- Rapid-MLX: no post-cutoff Qwen3.8 update.
- NInfer: no post-cutoff Qwen3.8 issue update.
- TurboQuant-MLX: no post-cutoff commit.
- llama.cpp #28243 Flash-Next MTP had no post-cutoff commit in the inspected commit list; existing claims remain KNOWN.

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

Keep **PP2/layer ownership primary and TP2 as control**. Preserve the existing semantic/cache/MTP ordering, with these additions:

- after exact PP2 semantics/recurrent ownership/cold-PP harness, profile stage-local GDN/routed-MoE/projection/synchronization at realistic chunks;
- perform a **chunk-width sweep per quant/kernel path before kernel promotion**;
- retain the 19:19 block-history GDN/repeated-work candidate and add double-buffered routed-expert staging only where exact M1 profiling exposes the same barrier/load bottleneck;
- choose final PP2 chunking jointly from stage balance + scratch/occupancy + real TB4 bubbles/traffic;
- every persistent/speculative surface proves coverage **and provenance**: owner identity, generation/epoch, valid range, device happens-before and reset on cancellation/slot reuse/reload/restart;
- distributed cancellation/cache maintenance follows one cross-rank state machine with barrier/fencing before ownership release;
- prompt-cache hits require cross-stage boundary/owned-byte agreement after lookup;
- QSA/indexer `top_k`, depth and realized metadata/cache path are benchmark provenance;
- quantized target/draft qualification records actual speculative-hook coverage and forced-rejection rollback;
- retain 21:57 grammar-state, actual-MTP-engagement, sampler-owner/fallback and prefill/decode-fairness gates.

For MTP, actual-resolved block/depth remains mandatory provenance. Default depth is certified first; deeper depths are separate correctness + whole-round A/B cells. Tape/refold remains orthogonal and post-replay-baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt. Preserve realized placement/backend, sampler path, VRAM/context headroom and real coding-agent wall-time provenance.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C. External M3/M5/other-runtime evidence does not rewrite frozen verifier evidence.

## Dual-M1 DS4-0731

No target movement and no fresh exact sustained current-head dual-M1 generated-token receipt. ds4 #991 remains Flash-Next mining evidence, not DS4-0731 throughput evidence.

---

# Standing decisions strengthened this pass

- Chunk width is quant/kernel/topology-specific, not a universal serving constant.
- Kernel A/Bs explicitly control or label cold paging and heat-soak contamination.
- Double buffering promotes only when exact profiling proves exposed staging/barrier latency and scratch/occupancy is acceptable.
- Coverage and provenance are separate state predicates.
- Every cross-turn/cross-request speculative buffer carries owner identity + generation/epoch.
- Common prompt prefixes are not generic request identity unless reuse is justified by the exact mathematical dependency of the state.
- Configured/enabled and actually armed/executed are separate benchmark fields.
- Host ownership stamps do not establish device happens-before.
- Distributed cancellation is a synchronized state transition, not rank-zero bookkeeping.
- Cancellation acknowledgements are plan/epoch/worker scoped so stale all-request state cannot poison later targeted requests.
- Prompt-cache reuse in PP2 requires cross-stage boundary/owned-byte agreement after lookup.
- QSA/indexer selection width is long-context benchmark provenance and is paired with semantic selected-set/quality certification.
- Cache identity binds representation-shaping metadata, not only source content.
- Quantized target/draft compatibility includes realized module classes and speculative-hook coverage, not dimensions alone.
- Forced-rejection rollback and unload/reload re-arming are part of speculative compatibility.
- Structured-output grammar state remains speculative state and is checkpointed/rewound with the emitted frontier.
- Distributed sampling lives where complete logits exist or uses an explicitly supported reduction path.
- Silent sampler fallback remains a failed optimized cell even if correctness survives.
- Prefill/decode fairness remains a serving correctness property, not merely a throughput knob.
- Isolated component microbench speedups do not become PP gains without production-style wall A/B.
- Controlled negative experiments remain first-class mining evidence.
- A benchmark cell is defined by what the engine actually executed, not merely what the CLI requested.
- The 15:10 oMLX #3494 attribution correction remains authoritative.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for replay correctness.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
