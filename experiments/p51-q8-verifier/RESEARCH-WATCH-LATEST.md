# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1919.md`

   **The 19:19 note is authoritative for the post-22:03 UTC ds4 Flash-Next prefill-structure A/B: block-history GDN convolution, reusable repeated-work elimination, wider routed-down tiling, retained negative candidates and their promotion order. It is M3 Ultra experimental/transfer evidence and moves no performance target.**

4. The immediately previous deltas remain essential:

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

**The 19:19 pass moves no row.** It adds no sustained physical receipt from an exact target rig.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-07 19:19 ET

Starting freshness boundary: `611b8bdf7c2ead7e67b66491debe7d9884c09464` / **2026-09-07 22:03:12 UTC**.

## FRESH / material experimental A/B

### antirez/ds4 #991 / `b85a6174da6d0ea3139b48194a2ca108097657b1` — Flash-Next structural prefill reuse

A post-boundary ds4 Flash-Next commit on **M3 Ultra 512 GB**, resident weights and **MTP off**, adds block-history GDN convolution and wider Q2_K routed-down tiling on top of an already-enabled Q8-unpack baseline.

The final controlled 8K cases improved about **+2.8 to +2.9%** over that enabled baseline, including prose, independent code and 8K append-after-8K-prefix shapes. The experiment used explicit off/on controls, alternating ABBA/BAAB repeats and bit-for-bit final-vocabulary comparisons. All 64 measured final vocabulary rows / 15,892,480 floats matched.

The negative experiments are equally useful for candidate ordering: broad IQ2 gate/up FP16 unpack was **-6.95%**, routed-input FP16 prepacking **-19.70%**, gate/up widening approximately neutral/negative, while the routed-down-only tile and block-history convolution were the retained components.

**Evidence class:** measured experimental A/B on M3 Ultra; **transfer/mechanism evidence only** for M1 Max / TB4. It is not an exact M1 PP receipt and must not be numerically transferred.

### Promotion for dual-M1 Flash prefill work

After exact PP2 semantic/state ownership and the cold-PP harness are frozen:

- profile stage-local GDN convolution and routed MoE attribution at realistic chunks;
- test block-history recurrence parallelization if the same repeated-work shape exists;
- test one-time quantized-weight unpack only when the exact M1 quant/layout repeats decode work and scratch fits;
- test wider routed-down tiles independently from gate/up widening;
- require append/live-prefix recurrent-state identity, scratch/residency accounting and explicit kill-switch controls;
- combine only passing mechanisms and measure end-to-end cluster cold PP with actual TB4 traffic/bubbles.

The portable result is the **candidate ordering and repeated-work shape**, not the M3 percentage.

## Screened non-promotions

- oMLX #3469's material M5 benchmark content predates the boundary; the post-boundary update was non-technical. **KNOWN.**
- Rapid-MLX #3156's M2-Max Qwen3.8-27B MTP-vs-plain numbers predate the boundary; its post-boundary event was a bot closure without resolution. **BACKFILL/KNOWN, not UPDATE.**
- NInfer #188's high Qwen3.8-27B DFlash2 numbers predate the boundary; fresh comments do not establish the exact RTX 5070 Ti lane. **KNOWN/BACKFILL.**
- targeted rMLX / llama.cpp / vLLM / exact-rig scans produced no new exact target receipt.

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

Keep PP2/layer ownership primary and TP2 as control. Preserve the 15:10 + 17:53 correctness/MTP ordering, with one prefill refinement:

- after exact PP2 semantics, recurrent ownership, QSA correctness and a trustworthy cold-PP harness, add a **stage-local prefill-structure A/B** for block-history GDN convolution / repeated quantized-weight work before broad repacking;
- exact stage-local recurrent/frontier identity and append behavior are mandatory;
- single-stage gains promote only after end-to-end cluster PP measures real stage balance and TB4 traffic.

For MTP, actual-resolved block/depth remains mandatory provenance. Default depth is certified first; deeper depths are separate correctness + whole-round A/B cells. Tape/refold remains orthogonal and post-replay-baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement or experiment-order change from this pass. Preserve the resident Qwen baseline and Tiel Q4/Q5 partial-expert-offload plan with realized placement/backend, VRAM/context headroom and real coding-agent wall-time provenance.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External M2/M3 serving A/Bs do not rewrite frozen P69 evidence.

## Dual-M1 DS4-0731

No exact-rig target update. ds4 #991 is Flash-Next Metal mining evidence, not a 0731 dual-M1 throughput receipt.

---

# Standing decisions strengthened this pass

- Controlled negative experiments are first-class mining evidence.
- Repeated-work elimination is promoted only when exact profiling proves the repetition exists in the chosen quant/layout/backend.
- Scratch used to save decode/unpack work is part of admission and residency accounting.
- Prefill optimizations must preserve recurrent history/frontier semantics in append as well as cold-prefix cases.
- Single-node prefill gains do not become PP2 cluster gains until TB4 bubbles/traffic and stage balance are measured.
- A benchmark cell is defined by what the engine actually executed, not merely what the CLI requested.
- QSA/indexer cache precision remains a separate state surface optimized only after deterministic semantic certification.
- Speculative cache/offload state carries explicit group ownership and lifecycle.
- The 15:10 oMLX #3494 attribution correction remains authoritative.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for replay correctness.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
