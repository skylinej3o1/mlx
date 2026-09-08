# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0843.md`

   **The 08:43 note is authoritative for the landed oMLX distributed request-safety integration, rMLX bounded speculative capture / commit-scoped conditioning result, hybrid recurrent+MTP mixed-phase ordering bug, deterministic-QSA TopK monitor, speculative backend-context placement cleanup and the DGX-Spark n=1/2/3 MTP depth backfill. It moves no performance target.**

4. The immediately previous deltas remain essential:

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

**The 08:43 pass moves no row.** It adds no sustained physical receipt from an exact target rig.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-08 08:43 ET

Starting freshness boundary: `51a5b0ed65657ac4d0ea337ce81d2cc5abf0afe0` / **2026-09-08 06:47:16 UTC**.

## FRESH / distributed lifecycle lands

### oMLX #3258 / `94530d8d49541ede9e99ef04a4431ee4953117a6`

Merged to main at **06:57:56 UTC**. The request-scoped cancellation, drain confirmation, orphan-generator reaping, cancellation-before-batch-mutation fencing, rank-aware cache maintenance, persisted prompt snapshots, peer-local unloaded-cache clearing, rank acknowledgements, synchronized prompt-cache plans and request/response identity surfaces captured in the 02:38 review are now landed mainline behavior.

The current merged pipeline path explicitly documents that **MTP is inactive on distributed serving** (`n_confirmed == 0`). Cluster request-safety therefore does not imply PP+MTP support.

**Promotion:** use #3258 as the current lifecycle reference, but retain exact dual-M1 cancellation/cache/restart/slot-reuse certification and record distributed-MTP active/inactive as realized provenance.

## FRESH / Apple speculative capture + conditioning

### rMLX #545 / `c86e45dbf9c6eaefbafa050df567382f8dec7915`

Merged at **10:45:40 UTC**.

DFlash2 now bounds verifier hidden capture **during chunked prefill** to the exact drafter-readable tail instead of materializing the full prompt and trimming afterward. On the shipped DFlash2 pair at a **16K prompt**, this reduced **Metal peak by ~600 MB**, reproduced twice per arm.

DFlash1/DFlash2 also carry row-wise conditioning projection across rounds and project only the rows the round actually committed. A shared identity-checked `committed_rows` becomes the single producer of the accepted capture prefix used by state updates and accounting.

Fresh-vs-carried projection is not byte-identical in all cases because dispatch-height rounding can move a few bf16 ULPs and occasionally a near-tie draft proposal; the PR qualifies this with model-level answer equivalence rather than pretending the numerical path is unchanged.

**Promotion:** capture horizon is semantic provenance; bound capture at production time; one committed frontier drives all derived state; compare carried projection to a fresh reference; record realistic-context peak Metal memory; and do not promote trip-count reduction to speed without wall/TG A/B.

## FRESH / mixed-phase recurrent + MTP correctness

### vLLM #55894

A fresh RTX PRO 6000 Blackwell Nemotron hybrid Mamba2+attention+MoE MTP report isolates silent corruption when the independently selected drafter backend lowers the global batch-reorder threshold from the recurrent target's required `1+k` to 1. Continuing prefill can then remain ahead of speculative decode rows; the recurrent builder positionally treats those decode rows as prefill and writes the wrong state slots.

Controls report 0/400 with MTP off, 0/400 when the global threshold is forced to `1+k`, and 0/400 when the drafter backend is pinned to a compatible route, versus repeated corruption in the production arm.

**Promotion:** stateful decode-before-prefill ordering is a correctness invariant. B2/B3/B4 certification adds staggered admission where a short request's **first speculative decode** shares a physical batch with another request's continuing chunked prefill. Record realized target/drafter backends and each scheduler threshold; do not let a permissive backend weaken a stateful backend's required ordering.

## FRESH / QSA deterministic route monitor

### vLLM #55872

Open PR adds an opt-in deterministic FlashInfer TopK backend for tied sparse-attention selection. It does not change the default and currently makes no performance/quality claim. Fresh #54521 discussion points at it for live validation.

A companion client parity collector reinforces provenance discipline: endpoint-observed prompt logprobs/token IDs can be canonicalized while unobserved server launch/runtime config remains unresolved rather than guessed.

**Promotion:** keep deterministic TopK as a separately named route pending live E2E validation; separate observed evidence from user-supplied/unresolved runtime configuration.

## FRESH / speculative placement hygiene

### llama.cpp #28390 / `415e909d84334a7b1f582229c166aa98be6c4678`

Merged at **12:44:33 UTC**. A single-device speculative drafter could create an unused Meta backend context when the target used tensor split, consuming unnecessary VRAM. The merged change avoids that wrapper.

**Promotion:** requested split/device flags do not define realized placement. Record actual target/drafter backend contexts and peak VRAM/context headroom. No rate claim or target movement.

## BACKFILL / MTP depth economics

### Ling single-DGX-Spark n=1/2/3 sweep

Underlying runs are described as **2026-08-22**, so this is backfill despite the new Reddit post.

Reported mean acceptance length rises **1.87 -> 2.39 -> 2.77**, while freeform throughput falls **38.7 -> 34.8 -> 33.6 tok/s** at 512 output tokens and **37.3 -> 33.6 -> 31.6** at 2048. Code stays roughly flat. The checkpoint reportedly has one native NextN layer, so n>1 autoregressively reuses the same drafter.

**Promotion:** acceptance length is diagnostic, not objective. Optimize useful emitted tokens / wall-second; qualify depth by workload; record native head count, requested/resolved n and how deeper proposals are formed; segment long-generation acceptance/TG over the output.

## SCREENED / no-change

- rMLX #546 is docs/process cleanup only.
- antirez/ds4 main has no post-cutoff main commit; prior #991 transfer evidence remains current.
- Avarok Atlas: no post-cutoff commit surfaced.
- vllm-mlx: no post-cutoff commit surfaced.
- vLLM #54521 has fresh validation-methodology discussion but no new proven end-to-end fix receipt.
- broad same-day searches found no new exact dual-M1 Flash/DS4, M1-Max64 27B or RTX5070Ti 27B rate receipt.

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

Keep **PP2/layer ownership primary and TP2 as control**.

Current ordering:

1. exact PP2 model/recurrent/QSA identity + landed distributed request lifecycle;
2. cold-PP harness with real chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase batch correctness: first decode joining continuing chunked prefill;
4. speculative ownership, rollback/replay and one authoritative committed frontier;
5. bound verifier capture to exact drafter-readable horizon; record realistic-context peak Metal;
6. default/native MTP depth whole-round baseline;
7. workload-separated deeper-depth A/Bs and segmented long-generation acceptance/TG;
8. stage-local GDN/routed-MoE/projection/sync profiling at realistic chunks;
9. per-quant/per-kernel chunk-width sweep before kernel promotion;
10. block-history/repeated-work candidate first, double-buffered routed-expert staging only where M1 profiling proves the same exposed barrier/load bottleneck;
11. combine only passing mechanisms and rerun cluster cold PP, append/live-prefix and agent-wall cells.

Persistent gates:

- current oMLX distributed serving has MTP inactive; PP+MTP remains separately uncertified;
- target and drafter backends plus scheduler requirements are independent provenance;
- stateful decode ordering cannot be weakened by a permissive backend;
- capture horizon, native MTP head count and realized depth are provenance;
- acceptance length cannot substitute for wall/TG;
- QSA selected-set + order determinism, actual `top_k`, context depth and realized route remain mandatory;
- grammar state, sampler owner/fallback, fairness, request-slot ownership, device happens-before, cancellation/reuse/restart resets and quantized-hook coverage remain mandatory;
- tape/refold stays post-replay-baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count. The 08:43 evidence adds that they must also remain correct under staggered mixed prefill/decode composition.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt. Preserve full residency, realized target/drafter contexts and sampler path, peak VRAM/context headroom, native/default MTP depth first, workload-specific deeper-depth whole-round A/Bs, mixed-phase recurrent/spec cells where applicable and real coding-agent wall/equivalence qualification.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C. External runtime evidence does not rewrite certified verifier results.

## Dual-M1 DS4-0731

No exact-rig update. rMLX #545 is general speculative-state transfer evidence, not DS4-0731 throughput evidence.

---

# Standing decisions strengthened this pass

- Acceptance length is diagnostic; useful emitted tokens per wall-second is the objective.
- MTP depth is workload-specific and evaluated as a whole round.
- Native trained MTP-head count and requested/resolved depth are benchmark provenance.
- Long-generation MTP qualification segments acceptance and TG over the output.
- Capture only verifier hidden history the drafter can mathematically read; capture horizon is model semantics.
- One authoritative committed frontier drives all derived speculative state.
- Incremental/carried projection requires a fresh-reference numerical/equivalence test on the real checkpoint.
- Reduced trip counts are not measured speedups.
- Realistic-context peak memory is a first-class speculative metric.
- Stateful decode-vs-prefill row ordering can be a correctness invariant.
- Target and drafter backend selection and scheduler requirements are independent realized provenance.
- First-decode-during-continuing-prefill is an explicit concurrency cell.
- Distributed request safety on main does not imply distributed MTP support.
- Requested device/split mode does not define actual backend-context allocation.
- Deterministic QSA TopK remains a separately named route pending end-to-end validation.
- Endpoint-observed evidence and unresolved/user-supplied runtime configuration remain distinct.
- Chunk width remains quant/kernel/topology-specific.
- Coverage and provenance remain separate state predicates.
- Every cross-request speculative buffer still carries owner identity + generation/epoch + valid range + explicit device happens-before.
- Structured-output grammar state remains speculative state and rewinds with the emitted frontier.
- Distributed sampling still lives where complete logits exist or uses an explicitly supported reduction path.
- Prefill/decode fairness remains serving correctness, not merely throughput.
- A benchmark cell is defined by what the engine actually executed, not merely what the CLI requested.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
