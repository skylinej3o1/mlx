# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1438.md`

   **The 14:38 note is authoritative for the updated M5-Max Flash long-context gathered-QSA decode/target-verify A/B, the fresh short-prompt MTP paged-boundary admission fix, and the fresh device-upload happens-before correction. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1048.md` — landed Apple IQ3 small-width SIMD-utilization A/B, recurrent checkpoint-retention / warm-rewind fix, DFlash2 cumulative-OOB attribution correction and recovered M1-Max Qwen3.8-27B baseline;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0843.md` — landed oMLX distributed request-safety integration, rMLX bounded speculative capture / commit-scoped conditioning, hybrid recurrent+MTP mixed-phase ordering bug, deterministic-QSA TopK monitor, speculative backend-context placement cleanup and DGX-Spark n=1/2/3 MTP-depth backfill;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0238.md` — M5-Max Flash-Next Q4_K routed-expert double-buffer/chunk-width A/B, cross-request MTP carry/hidden-state ownership failure, distributed cancellation/cache-agreement lifecycle review, depth-sensitive QSA `top_k` provenance and ParoQuant/DFlash2 rollback-hook qualification;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-2157.md` — Apple grammar-constrained MTP serving A/B, merged prefill/decode fairness enforcement, distributed sampler-backend ownership/fallback evidence, HC-prefill microbench-vs-E2E correction and Apple MTP-drafter loader CI hardening;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1919.md` — M3-Ultra ds4 Flash-Next prefill-structure A/B: block-history GDN convolution, repeated-work elimination, wider routed-down tiling and retained negative candidates;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1753.md` — actual-resolved MTP block/depth provenance, post-baseline explicit depth sweeps, QSA low-bit indexer-cache backfill and speculative external-cache group/lifecycle ownership;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1510.md` — stock-oMLX #3494 attribution correction, recurrent checkpoint materialization/nullness, restored-boundary finite-state/logit certification, persistent request-slot ownership, state-index stride, overlapped-step happens-before and PP+MTP distributed-state certification;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-0655.md` — recurrent tape/refold MTP candidate, multi-step MTP cache restore, content-addressed distributed model identity, explicit recurrent-layer manifests and graph/compile route provenance. **Its #3494 attribution is superseded by the 15:10 correction.**
   - retain all 2026-09-06 and 2026-09-05 watch deltas for recurrent rollback, cache geometry, QSA tie/order, scheduler occupancy, whole-round speculative economics, warm-slot qualification, sampler ownership, request-row ownership and benchmark-provenance gates.

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

**The 14:38 pass moves no row.** It adds no fresh sustained physical receipt from an exact target topology.

---

# Current newest evidence delta — 2026-09-08 14:38 ET

Starting freshness boundary: `4331d0ec753ffb3456fe1bd817ebdfc1056143f6` / **2026-09-08 14:55:14 UTC**.

## UPDATE / strongest long-context Flash evidence

### oMLX #3520 — gathered QSA for backbone decode + Lightning-MTP target verify

The underlying branch commits predate this cutoff, but the PR was revised after it with a full M5-Max server benchmark matrix and crossover analysis. Classify **UPDATE**, not fresh commit.

On **M5 Max 128 GB / Qwen3.8-Flash-Next-oQ4e-mtp**, the branch:

- selects QSA K/V rows directly from the stored cache layout instead of transposing/copying the dense cache;
- carries a request-level text-only position proof into qualifying batch-one decode/verify steps;
- routes **target verify rows as well as backbone decode rows** through gathered QSA above the threshold;
- fails closed for multimodal/batched/unproven position semantics.

Per-QSA-layer selected-row gather cost is reported approximately context-flat (0.32 / 0.25 / 0.27 ms at 41K / 82K / 206K) versus the prior full-cache transpose+reshape (0.65 / 0.91 / 1.83 ms).

Controlled server deltas grow strongly with context:

- serial decode: **+8.3% @63K, +18.5% @134K, +29.6% @229K**;
- adaptive sampled MTP: **+8.2%, +25.7%, +27.0%** at those depths;
- adaptive greedy/deeper MTP: **+13.3%, +34.3%, +39.5%**.

The optimization crossover differs by regime: roughly 12K serial, 16K sampled MTP and 36–40K greedy/deeper MTP. An earlier eligibility route paid host syncs and lost ~14/8/5% at 4K/8K/16K, so short-context negative controls remain mandatory.

**Promotion:** "QSA enabled" is insufficient. Record the realized route of draft, target decode and target verify; prove selected-row gather does not hide dense-cache materialization; sweep threshold by workload/depth; keep QSA/selected-KV state stage-local under PP2. The M5 percentages do not numerically transfer to M1/TB4, so no target movement.

## FRESH / short-prompt MTP boundary publication

### oMLX #3525 / `6b21d06ad21aa668d834e0e2ef957dca0bd56d5e`

Fresh at **15:32:48 UTC**.

MTP paged-cache commit alignment was armed lazily only after the first snapshot attempt. For prompts shorter than a cache block, the first block boundary occurs during speculative decode before any prefill capture, so the MTP cycle could cross the 2048 boundary at offset 2047/2049; split-GDN snapshot storage then rejected the block and the answer remained uncached.

The fix arms boundary alignment at request admission.

**Promotion:** add short-prompt + long sampled MTP output cells where the first paged boundary occurs during decode. Exact block-aligned frontier publication is a request-admission invariant, with next-turn reuse, cancellation/retry and slot-reuse checks.

The broader PR also reinforces that reasoning/tool-call output is reusable only when exact next-turn rendered history preserves it; streamed, non-streamed and parser/tool-call paths must carry identical cacheability provenance.

## FRESH / device state-publication ordering

### NInfer / `b88c0f6fc7e999f13eb2fcf7fc9105ed79a91868`

Fresh at **16:35:48 UTC**.

A pageable H2D upload could return before the physical transfer completed, allowing a consumer on a non-blocking stream to run against incomplete state. NInfer now synchronizes completion before returning and separately documents that callers must order prior readers before overwriting the destination.

**Promotion:** certify two independent happens-before edges on every reusable state surface:

1. old reader → overwrite/upload;
2. upload/capture completion → new reader.

Owner/epoch/range metadata does not prove device completion. Use the correct MLX/Metal primitive on Apple; the portable requirement is ordering, not CUDA's exact API.

## SCREENED / no target movement

- NInfer also carries a target-only T=1 L2 weight-prefetch optimization measured ~+1.7–1.9% without speculation but ~0 under MTP; useful negative evidence that target-only kernel wins may vanish under speculative geometry.
- Rapid-MLX post-cutoff work is service-doctor/diagnostic tooling, not target performance evidence.
- llama.cpp `f3f1a8f...` changes lazy loading for integrated GPUs; not an Apple target receipt.
- antirez/ds4 `6289c...` is terminal UI presentation only.
- Atlas post-cutoff work is GLM-5.3/KDA, another model lane.
- vLLM same-day hybrid fault activity remains unresolved and does not supersede the prior attribution caution.
- no fresh exact dual-M1 Flash/DS4, M1-Max64 27B or RTX5070Ti receipt surfaced.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Current qualification/optimization order:

1. exact PP2 model/recurrent/QSA identity + landed distributed lifecycle;
2. cold-PP harness with real chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase first speculative decode joining another request's continuing chunked prefill;
4. speculative ownership / rollback / replay with one authoritative committed frontier;
5. bound verifier capture to the drafter-readable horizon;
6. **admission-time paged-boundary alignment**, including short-prompt/long-output first-boundary crossing;
7. recurrent checkpoint retention across branch/edit/retry/compaction/reopen with exact frontier/count/bytes;
8. rendered-history cacheability for preserved reasoning/tool calls, with stream/nonstream parity;
9. native/default MTP-depth whole-round baseline;
10. workload-separated deeper-depth A/Bs + segmented long-generation acceptance/TG;
11. **realized QSA route proof for backbone decode and target verify**;
12. selected-KV gather cost/traffic must scale with selected rows rather than dense context;
13. threshold sweep by serial / sampled MTP / greedy-deeper MTP with short-context negative controls;
14. stage-local GDN/routed-MoE/projection/sync profiling at realistic chunks, including active SIMD-lane utilization;
15. per-quant/per-kernel chunk-width sweep before promotion;
16. block-history/repeated-work candidate first; double-buffer or row-split only after matching M1 profiling;
17. combine passing mechanisms and rerun cluster cold PP, ~128K TG, append/live-prefix, branch/retry and real coding-agent wall cells.

For PP2 long context, selected K/V plus recurrent/QSA state remain stage-local. Turning sparse attention into dense TB4 traffic fails the intended economics.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured/admitted/batched/queued slots do not count; staggered mixed prefill/decode must remain correct.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt. Continue pinning actual source/kernel path, target/drafter placement, sampler path, driver/runtime state and VRAM/context headroom. The new NInfer synchronization lesson is correctness provenance, not a rate estimate.

## Dual-M1 DS4-0731

No target movement and no fresh exact sustained current-head generated-token receipt. Recurrent cache/boundary semantics transfer; Flash QSA measurements do not.

---

# Standing decisions strengthened this pass

- Record realized QSA routes for draft, target decode and target verify.
- A selected-KV path fails qualification if it secretly materializes/copies the dense cache.
- Selected-row cost/bytes are measured across context depth.
- Long-context route thresholds are workload/depth specific.
- Short-context negative controls are mandatory.
- Adaptive-MTP parking/depth behavior is part of whole-round economics.
- Acceptance is diagnostic; emitted tokens per wall-second is the objective.
- Route eligibility is request provenance with step-scoped realization and explicit reset.
- MTP paged-boundary alignment is armed at admission.
- Short-prompt/long-output cells expose lazy-initialization bugs hidden by long prefills.
- Generated reasoning/tool output is reusable only when next-turn rendered tokens prefix-match it.
- Streaming/non-streaming/parser paths carry the same cacheability provenance.
- Warm reuse is certified by exact stored/restored frontier identity.
- Old-reader→overwrite and upload-complete→new-reader are separate happens-before edges.
- Host owner/epoch/range metadata does not prove device completion.
- Target-only T=1 kernel gains do not transfer to MTP unless speculative execution hits the same geometry.
- Existing grammar-state, sampler-owner/fallback, fairness, cancellation/reuse/restart, request-slot ownership, quantized-hook, actual-MTP-depth and tape/refold gates remain active.
- Chunk width remains quant/kernel/topology specific.
- Cross-runtime/other-hardware gains remain mechanism evidence until exact target reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
