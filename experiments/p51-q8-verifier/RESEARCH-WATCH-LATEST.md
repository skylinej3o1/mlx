# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-2157.md`

   **The 21:57 note is authoritative for the fresh Apple grammar-constrained MTP serving A/B, merged prefill/decode fairness enforcement, distributed sampler-backend ownership/fallback evidence, HC-prefill microbench-vs-E2E correction and Apple MTP-drafter loader CI hardening. It moves no performance target.**

4. The immediately previous deltas remain essential:

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

**The 21:57 pass moves no row.** It adds no sustained physical receipt from an exact target rig.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-07 21:57 ET

Starting freshness boundary: `e6357f532ed226b1073a78799b84760d0f25b751` / **2026-09-07 23:21:27 UTC**.

## FRESH / material

### oMLX #3504 — grammar-constrained MTP serving A/B

A fresh 611-request Apple structured-output A/B on `qwen3.8-27b-oQ6e-mtp` showed that grammar state can be snapshotted/rewound through speculative verify while maintaining an independent grammar oracle and still producing a material MTP speed win.

Key measured results:

- MTP actually drafted on 611/611 enabled requests;
- 0/601 non-truncated MTP-on corpus outputs were off-grammar, with all 1202 deliberate mutants rejected;
- streaming raw-byte sample: 0/50 off-grammar, all 100 mutants rejected;
- parse/schema-valid rate was essentially unchanged versus MTP off;
- paired corpus wall ratio ~**1.283x**;
- streaming decode sample **25.6 -> 47.9 tok/s**;
- median acceptance ~0.85 and ~2.58 emitted tokens/cycle.

**Promotion:** grammar/parser state is speculative state. Production structured-output MTP must prove snapshot/restore/rewind semantics, actual MTP engagement, independent grammar validity with mutation controls, parse/truncation parity, acceptance/tokens-per-cycle and wall/decode against MTP off. Do not assume grammar lowers acceptance; measure the actual schema/tool workload.

This is Apple transfer evidence, not an exact M1-Max target receipt.

### Ollama #18302 — distributed sampler placement / fallback

A fresh 2x-TITAN RTX tensor-split Qwen3.8-27B MTP A/B found that requesting backend sampling when logits were sharded forced a rejected backend path and CPU fallback. Removing the unsupported request improved end-to-end decode **27.67 -> 35.14 tok/s (+27%)** with the answer unchanged.

**Promotion:** distributed MTP records sampler owner/backend, complete-vs-sharded logits, reduction support and actual fallback. PP2 keeps explicit last-stage/complete-logit sampling ownership; TP2 control fails optimized qualification if a supposedly accelerated sampler silently falls back.

This is topology/mechanism evidence only.

## UPDATE / material status

### oMLX #3487 — merged prefill/decode fairness enforcement

Merged 2026-09-08 00:55:01 UTC. The scheduler now rechecks fairness before every in-flight prefill chunk, rotates deferred work for fair progress, charges non-embedding external prefill to decode debt and uses the same gate for new admission.

**Promotion:** long-prefill-while-decode qualification reports per-request latency/progress as well as aggregate throughput and proves prefill cannot monopolize successive chunks after debt closes the gate.

### oMLX #3492 — HC-prefill RMSNorm microbench does not yet produce E2E PP

A fresh generalization commit broadens the fused RMSNorm kernel eligibility, but the current PR evidence remains cautionary: a roughly 3.4-3.5x isolated norm speedup corresponds to only ~0.2% difference in restart-per-sample 100K end-to-end TTFT (255.06 vs 254.56 s), not a significant whole-request win.

**Promotion consequence:** keep the 19:19 block-history GDN/repeated-work candidate ahead of standalone HC-prefill norm fusion. Component microbench ratios do not enter PP forecasts without production-style wall A/B.

### vllm-mlx #752 — MTP drafter-loader regression coverage added to Apple CI

Fresh Apple-CI commit exercises registered-drafter loader regressions. Existing 64K continuous-batching / 128K MTP qualification predates this cutoff and remains KNOWN rather than fresh.

**Promotion:** target/drafter identity, metadata source and compatibility are part of the runtime identity gate; malformed/incompatible combinations fail before serving starts.

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

- target/drafter metadata and compatibility join the persistent runtime identity gate;
- after ordinary sampler-law certification and singleton replay correctness, add a grammar-constrained structured-output MTP state oracle with independent grammar/mutation controls and actual-engagement provenance;
- row-wise batched grammar+MTP remains unqualified until separately proven;
- distributed sampler provenance is mandatory, especially on the TP2 control;
- long prefill while other sessions decode now includes per-chunk fairness/debt enforcement and per-request latency/progress;
- retain the 19:19 prefill candidate ordering: block-history GDN/repeated-work elimination before broad repacking; standalone HC-prefill norm fusion remains lower priority until exact-rig E2E evidence appears.

For MTP, actual-resolved block/depth remains mandatory provenance. Default depth is certified first; deeper depths are separate correctness + whole-round A/B cells. Tape/refold remains orthogonal and post-replay-baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. The fresh tensor-split sampler result is distributed topology evidence only and does not alter the single-card resident target. Preserve realized placement/backend, sampler path, VRAM/context headroom and real coding-agent wall-time provenance.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External production-serving A/Bs do not rewrite frozen verifier evidence.

## Dual-M1 DS4-0731

No target movement and no fresh exact sustained current-head dual-M1 generated-token receipt.

---

# Standing decisions strengthened this pass

- Structured-output grammar state is speculative state and is checkpointed/rewound with the emitted frontier.
- Constrained decoding may improve speculative acceptance on some workloads; measure rather than assume direction.
- MTP-enabled configuration is not proof of MTP execution; actual draft/verify engagement is mandatory provenance.
- Distributed sampling lives where complete logits exist or uses an explicitly supported reduction path.
- Silent sampler fallback is a failed optimized cell even if correctness survives.
- Prefill/decode fairness is a serving correctness property, not merely a throughput knob.
- Aggregate concurrency claims include per-request progress/latency under concurrent long prefill.
- Isolated component microbench speedups do not become PP gains without production-style wall A/B.
- Controlled negative experiments remain first-class mining evidence.
- A benchmark cell is defined by what the engine actually executed, not merely what the CLI requested.
- QSA/indexer cache precision remains a separate state surface optimized only after deterministic semantic certification.
- Speculative cache/offload state carries explicit group ownership and lifecycle.
- The 15:10 oMLX #3494 attribution correction remains authoritative.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for replay correctness.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
