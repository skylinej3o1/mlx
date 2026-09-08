# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1048.md`

   **The 10:48 note is authoritative for the landed Apple IQ3 small-width SIMD-utilization A/B, landed recurrent checkpoint-retention / warm-rewind fix, DFlash2 cumulative-OOB attribution correction, and recovered same-day M1-Max Qwen3.8-27B baseline. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0843.md` — landed oMLX distributed request-safety integration, rMLX bounded speculative capture / commit-scoped conditioning, hybrid recurrent+MTP mixed-phase ordering bug, deterministic-QSA TopK monitor, speculative backend-context placement cleanup and DGX-Spark n=1/2/3 MTP-depth backfill;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0238.md` — M5-Max Flash-Next Q4_K routed-expert double-buffer/chunk-width A/B, cross-request MTP carry/hidden-state ownership failure, distributed cancellation/cache-agreement lifecycle review, depth-sensitive QSA `top_k` provenance and ParoQuant/DFlash2 rollback-hook qualification;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-2157.md` — Apple grammar-constrained MTP serving A/B, merged prefill/decode fairness enforcement, distributed sampler-backend ownership/fallback evidence, HC-prefill microbench-vs-E2E correction and Apple MTP-drafter loader CI hardening;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1919.md` — M3-Ultra ds4 Flash-Next prefill-structure A/B: block-history GDN convolution, repeated-work elimination, wider routed-down tiling and retained negative candidates;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1753.md` — actual-resolved MTP block/depth provenance, post-baseline explicit depth sweeps, QSA low-bit indexer-cache backfill and speculative external-cache group/lifecycle ownership;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-1510.md` — oMLX #3494 stock-runtime attribution correction, physical recurrent-checkpoint materialization/nullness, restored-boundary finite-state/logit certification, persistent request-slot ownership, state-index stride, overlapped-step happens-before and PP+MTP distributed-state certification;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-07-0655.md` — recurrent tape/refold MTP candidate, multi-step MTP cache restore, content-addressed distributed model identity, explicit recurrent-layer manifests and graph/compile route provenance. **Its stock-oMLX #3494 attribution is superseded by the 15:10 correction.**
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

**The 10:48 pass moves no row.** It adds no sustained physical receipt from an exact target topology strong enough to alter a planning distribution.

---

# Current newest evidence delta — 2026-09-08 10:48 ET

Starting freshness boundary: `fa13bcae0ba0d285dd8611543a7993fb6ff641f2` / **2026-09-08 12:53:53 UTC**.

## FRESH / Apple small-width Metal utilization

### llama.cpp #28086 / `88ada91c18cd026388be742838d9f27fc12673bc`

Merged at **12:54:42 UTC**.

`IQ3_XXS` with `ne00=512` had only 16 32-element chunks for 32 SIMD threads, leaving half the lanes idle. The landed split path assigns multiple threads per chunk and divides output rows between them.

On an M5 24 GB with Tiel-Coder-35B-A3B MTP `UD-IQ3_XXS`, a fixed 13-generation coding-agent replay improved **24.66 -> 22.59 s/rep (-8.4%)** and **65.6 -> 73.9 tok/s**, while perplexity stayed 3.3969. Kernel latency fell roughly 29-37% across the reported multi-row verify heights.

**Promotion:** profile actual lane utilization at exact matrix widths; vary expert IDs to avoid unrealistic hot-weight benchmarks; transfer row/chunk splitting only where the target quant/shape proves the same idle-lane regime; require wall/TG + equivalence beyond microbench. No numeric transfer from M5/Tiel/IQ3 to M1 Flash Q4/Q2.

## FRESH / recurrent checkpoint retention and rewind economics

### llama.cpp #28302 / `5d806aa2575e01e126651fd69ab1ab6cefff861d`

Merged at **13:01:03 UTC**.

Checkpoint spacing eviction was running before the checkpoint list was full. With default `checkpoint_min_step=8192`, short conversational prompts could lose the useful near-frontier recurrent checkpoint and later edits/branches/retries/reopens had to re-prefill much more history.

Measured examples:

- M5 Qwen3.5-9B edit rewind: **702 -> 26 prompt tokens**, **1459 -> 229 ms**;
- M1 Pro ordering control: **704 / 3355 ms -> 26 / 264 ms -> 704 / 3323 ms**;
- M5 Tiel coding-agent replay: warm reprocessed tokens **2436 -> 1776**, wall **18.25 -> 17.12 s (-6.2%)**.

Retaining useful checkpoints costs memory: reported checkpoint sizes are ~50 MiB for Qwen3.5-9B and ~74 MiB for Tiel, with ~596 MiB highest observed live-checkpoint usage in the agent replay.

**Promotion:** branch/edit/retry/compaction/reopen are explicit recurrent-session cells; record warm `prompt_n`, prompt wall, frontier identity, live checkpoint count and bytes; recent mathematically useful frontiers cannot be silently deleted by generic spacing policy; duplicate positions supersede rather than accumulate. This is warm reuse, not cold-PP target evidence.

## UPDATE / DFlash2 OOB attribution correction

### vLLM #55279

Fresh investigation reports upstream A100 runs reaching 21K-22K speculative verification steps cleanly, but those runs did **not** execute the community split-KV Triton patch used by the failing deployment. A CMP-unlocker driver memory-map issue is also a plausible Xid-31 confound for the reporter's hardware.

No upstream vLLM root cause or fix is established.

**Promotion:** hash the actual speculative source/kernel path and pin device/driver/runtime memory-map provenance. Upstream-clean does not clear a community patch; patched-path failure does not indict upstream. Keep long cumulative-round stress after short semantic tests.

## BACKFILL / recovered M1-Max Qwen3.8-27B baseline

A same-day r/oMLX post predating this pass reports M1 Max Mac Studio, 24-core GPU / 32 GB, 512 prompt / 700 generation, 3 runs:

- MLX 4-bit: **81.76 prompt tok/s, 15.81 generation tok/s**, 16.39 GB peak;
- llama.cpp UD-Q4_K_M full Metal + FA: **99.61 ± 0.44 prompt tok/s, 9.69 ± 0.34 generation tok/s**.

A comment claims ~18-25 tok/s around 50K context with tuned MTPLX on another M1 Max 32 GB, but lacks enough controlled provenance and remains anecdotal.

**Classification:** BACKFILL/direct chip-family baseline, not exact M1 Max64 mature-runtime evidence. It is compatible with the existing 25 tok/s planning target and moves nothing.

## SCREENED / no-change

- oMLX: no post-cutoff main commit.
- antirez/ds4: no post-cutoff main commit.
- rMLX #547: CI/debt-report process work only.
- vllm-mlx: no post-cutoff commit.
- Avarok Atlas: no post-cutoff commit.
- no fresh exact dual-M1 Flash or DS4 sustained receipt;
- no fresh exact M1-Max64 27B mature-runtime receipt after the cutoff;
- no fresh exact RTX5070Ti 27B or Tiel-Coder receipt after the cutoff.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact target-configuration mature-runtime receipt after the cutoff.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt after the cutoff.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Current ordering:

1. exact PP2 model/recurrent/QSA identity + landed distributed lifecycle;
2. cold-PP harness with real chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase first-decode joining continuing chunked prefill;
4. speculative ownership / rollback / replay with one authoritative committed frontier;
5. bound verifier capture to the drafter-readable horizon;
6. recurrent checkpoint-retention qualification across branch/edit/retry/compaction/reopen, with warm `prompt_n` + wall + frontier identity + bytes;
7. default/native MTP depth whole-round baseline;
8. workload-separated deeper-depth A/Bs and segmented long-generation acceptance/TG;
9. stage-local GDN/routed-MoE/projection/sync profiling at realistic chunks, including exact active SIMD-lane utilization;
10. per-quant/per-kernel chunk-width sweep before promotion;
11. block-history/repeated-work candidate first; double-buffering or small-width row/chunk splitting only where exact M1 profiling proves the matching bottleneck;
12. combine only passing mechanisms and rerun cluster cold PP, append/live-prefix, branch/retry and real agent-wall cells.

Persistent gates from earlier watches remain active: distributed MTP is not yet certified; target/drafter backend and scheduler requirements are independent provenance; QSA selected-set/order and actual `top_k` are mandatory; grammar state, sampler owner/fallback, fairness, request-slot owner/epoch/range, device happens-before, cancellation/reuse/restart reset and quantized-hook coverage remain required; tape/refold stays post-replay-baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count; staggered mixed prefill/decode must also remain correct.

## Single M1 Max64 Qwen3.8-27B

No target movement. The recovered 24-core/32GB benchmark is baseline calibration only.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt. Pin actual target/drafter source/kernel paths, device placement, sampler path, driver/runtime state and peak VRAM/context headroom before using a stability or speed cell. The new Tiel IQ3 result is Apple transfer evidence only.

## Dual-M1 DS4-0731

No target movement and no fresh exact sustained current-head generated-token receipt. Checkpoint-retention semantics transfer to recurrent session reuse but do not constitute DS4 throughput evidence.

---

# Standing decisions strengthened this pass

- Warm recurrent reuse is certified by exact retained/restored frontier identity, not a generic cache-hit flag.
- Branch/edit/retry/compaction/reopen are first-class recurrent-cache cells.
- Reprocessed prompt tokens and warm prompt wall are mandatory session-reuse metrics.
- Recurrent checkpoint retention needs explicit count and byte accounting.
- Small matrix width can make SIMD occupancy a high-leverage bottleneck.
- Routed-kernel A/Bs vary expert IDs when fixed IDs would create unrealistic hot-weight reuse.
- Kernel gains require production-style wall/TG and equivalence before promotion.
- Cross-quant small-width fixes transfer only after exact shape/profile confirmation.
- Community-patched speculative paths are separate execution identities from upstream.
- Exact installed source/kernel hashes and driver/runtime state are failure provenance.
- Long cumulative-round stress remains necessary after short correctness tests.
- Acceptance length remains diagnostic; useful emitted tokens per wall-second remains the speculative objective.
- First-decode-during-continuing-prefill remains an explicit concurrency cell.
- Capture horizon, target/drafter backends, scheduler requirements, owner/epoch/range and device happens-before remain mandatory provenance.
- QSA selected-set/order determinism and actual `top_k` remain mandatory.
- A benchmark cell is defined by what the engine actually executed, not what was requested.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
