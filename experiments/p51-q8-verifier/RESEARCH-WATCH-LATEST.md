# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct targets from older watch-note prose.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0243.md`

   **The 02:43 note is authoritative for whole-round speculative economics, QSA selected-set/order determinism and the resulting Flash/5070 experiment ordering. It moves no performance target.**

4. The immediately previous delta remains essential:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1943.md`

   It remains authoritative for speculative-checkpoint provenance, greedy verifier-only answer equivalence and first-repeat MTP prefix-cache qualification.

5. The 15:12 and 12:00 deltas remain important for real-agent cache-capture efficacy, MTP-head/vocabulary ordering, reusable-scratch transfer, ordinary recurrent rollback, per-slot MTP context sizing and persistent-cache identity:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1512.md`
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1200.md`

6. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain dated deltas newer than that point when reconstructing the evidence chain. The recent sequence is:

   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode correction / hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS, Blackwell ubatch and cache granularity;
   - `RESEARCH-WATCH-2026-09-04-0915.md` — v0.4.0-era baseline, parallel-MTP isolation, SSD-expert streaming and MTP-head quant;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — PP-vs-TP structural evidence, production cache-granularity failure and CUDA provenance;
   - `RESEARCH-WATCH-2026-09-04-1840.md` — stable v0.4.0 pin, modality-agnostic KV reuse, DS4 tool-observation correction and MTP draft-cache VRAM;
   - `RESEARCH-WATCH-2026-09-04-1930.md` — Flash MTP commit semantics, concurrent-PLE state isolation, Apple recurrent kernels and decoupled cache geometry;
   - `RESEARCH-WATCH-2026-09-05-0400.md` — neighboring-row QSA gather reuse, Metal `MUL_MAT` width exactness and DS4 fixed-work PP;
   - `RESEARCH-WATCH-2026-09-05-0500.md` — production-layout invariance correction, low-level runtime provenance and Strix-Halo AProjQ4 smoke;
   - `RESEARCH-WATCH-2026-09-05-1200.md` — recurrent multi-turn rollback, per-slot draft context, chunk-size-dependent AProjQ4 PP, M1/M2 FP16 activation lane and persistent-state identity;
   - `RESEARCH-WATCH-2026-09-05-1512.md` — real-agent cache-capture efficacy, independent 27B FR-Spec correction, exact ds4 CUDA scratch-reuse receipt, allocator-identity watch and TG-log provenance;
   - `RESEARCH-WATCH-2026-09-05-1943.md` — speculative-loader provenance, greedy answer equivalence, 4-bit MTP behavior and first-repeat MTP cache-boundary backfill;
   - `RESEARCH-WATCH-2026-09-06-0243.md` — whole-round MTP decomposition, marginal multi-position verify cost, QSA order determinism and M5 TensorOps approximate-lane backfill.

7. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 02:43 pass moves no row.** It adds no sustained physical receipt from the four target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and hardware-specific approximate matrix routes remain separate from exact-runtime evidence.
- 5070 targets require full residency and measured net VRAM/context headroom.
- DS4 remains conservative until exact sustained 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-06 02:43 ET

Starting freshness boundary: `6a338ab826e620a7d45407b04cb303cb353f0180` / **2026-09-05 23:49:49 UTC**.

## FRESH / material

### rMLX `fd33c684a8b4deefb78df2c9ae46e69b5856a02a` / #518 — optimize the speculative round, not just the drafter

A charged diagnostic run on a 4-bit Qwen3.8-27B verifier + MTP sidecar decomposed 86 block-3 rounds:

| round class | n | round ms | draft | verify | rollback | other |
|---|---:|---:|---:|---:|---:|---:|
| partial/replayed | 34 | 76.68 | 4.16 | 40.47 | **31.99** | 0.055 |
| full accept | 52 | 46.09 | 4.18 | 41.81 | **0.027** | 0.066 |

The material findings are:

- partial-accept rollback re-runs the accepted prefix through the full verifier stack, effectively paying another verifier weight read;
- recurrent snapshot/bookkeeping itself is only about **0.06 ms**;
- the acceptance walk had been re-deriving the quantized LM head position by position instead of consuming the block result; reusing the block argmax produced a measured **+1.96% decode** on this pair with output identity preserved;
- one extra verified position costs about **0.236x of a plain step** on the 27B GDN hybrid and **0.242x** on an MXFP8 full-attention model, far above the ~0.04x roofline intuition;
- removing replay alone therefore projects to about **1.56x**, not the old 2.2x aspiration;
- block-2 -> block-3 round growth was roughly +7.27 ms verify, +6.24 ms replay and +2.03 ms draft.

Fresh #496 analysis also identifies depth-scaling draft costs: a full 248,320-vocab head read per drafted token (~1.3 GB on the cited 4-bit checkpoint), one host sync per drafted token, and a trailing sidecar step.

**Promotion:** before deeper MTP or aggressive vocab trimming, measure/attack accepted-prefix replay, verify M=1 vs M>1 kernel economics, redundant full-head reads and host synchronizations. Add replay fraction/ms, marginal verify-position ms, head bytes and sync count to the speculative receipt.

**Instrumentation rule:** charged phase timing forces evaluations and changes scheduling. Charged rows are diagnostic only and must not enter ordinary champion tables.

This is measured runtime evidence, not an exact M1-Max or 5070 rate receipt.

### vLLM #54521 — correct top-k set can still be numerically wrong downstream if emitted order is nondeterministic

Fresh GB10 investigation corrected the earlier `indexer_budget` diagnosis. Greedy divergence was reproduced below the budget and with MTP disabled.

The decisive isolated test used the real QSA geometry (`columns=65,536`, `k=512`) and found that when `visible > k`, ten identical `persistent_topk` calls returned:

- the **same selected set 10/10**;
- but the **same exact order only 1/10** across row counts 1 through 512.

At `visible=480 < k`, both set and order were 10/10 stable.

Existing tests can miss this because they compare sets/sorted values. QSA consumes the raw selected order in sparse-attention accumulation, so changing block order changes floating-point reduction order and can perturb near-tied logits.

**Promotion to Flash QSA:** require selected-set equality, selected-order determinism, canonical-order logit equivalence, prefill/decode separation, MTP on/off, serial/concurrent scheduling and narrow-range/near-tie indexer-score stress. Structurally valid indices/no duplicates are not sufficient.

If selection order is not semantically meaningful, normalize it before an order-sensitive floating accumulation.

This is NVIDIA/GB10 evidence, not an Apple bug or a target-rate ruler.

## BACKFILL / separate approximate lane

### M5-Max ds4 Metal TensorOps can be faster in agent work while remaining non-exact

The previously reproduced TensorOps route has real long-prompt numerical drift (worst RMS about 1.386, max-abs about 7.27, with first-token greedy flips in long cases). A pre-registered 15-task x 3-sweep route A/B nevertheless found:

- T/R wall ratios **0.900, 0.768, 0.690**; pooled **0.786**;
- T 43/45 task-run passes vs R 38/45;
- the pre-registered “route buys with no measured agent-task break” screen fired.

The lower-level drift remains. Therefore agent-task parity cannot substitute for a logit/greedy equivalence gate. Stamp the exact Metal route and keep hardware-specific approximate paths separate from exact-runtime evidence. Do not transfer this M5 result to M1 Max.

## FRESH / monitor only

### llama.cpp `971595d6697f53b215d02a8381f8b5af142a4d86`

More M2-Max FA-vector tuning for Q4_0/Q4_1/Q5_0/Q5_1 landed upstream. The inspected PR contains no rate receipt or M1 mapping, so monitor only.

---

# Focused follow-up status

- **oMLX #3462:** still open, 0 comments; no fix or maintainer response surfaced.
- **oMLX #3464:** still open, 0 comments; no logging fix surfaced.
- **jundot/omlx main:** no commits after the cutoff.
- **llama.cpp #28425:** unchanged; ordinary no-spec recurrent rollback gate remains active.
- **llama.cpp #28433:** unchanged; per-slot MTP draft-context sizing gate remains active.
- **llama.cpp #28448:** unchanged; allocator identity remains monitored, not an Apple/Flash blocker.
- **llama.cpp #25187:** no fresh activity; full-head quantization before aggressive FR-Spec remains active.
- **antirez/ds4 main:** no commits after the cutoff.
- **ml-explore/mlx main:** only a fresh CUDA completion-worker fix surfaced; no Apple/M1 runtime receipt.
- **MLX #4409:** still open; no fresh M1 result surfaced.
- **wtdcode/vllm-backport:** no commits after the cutoff.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG receipt or new exact-rig cold-PP result.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **RTX 5070 Ti 27B:** no fresh exact-card TG/PP receipt.
- **M1 Max64 27B:** no fresh exact single-M1-Max serving receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Qualification now explicitly includes:

1. ordinary no-spec recurrent rollback correctness;
2. real-agent cache-capture frontier + first-repeat/second-repeat effectiveness;
3. selected-QSA **set + order determinism**, canonical-order logits and near-tie stress;
4. PLE/QSA residency, page-cache and known-horizon controls;
5. MTP recurrent commit/replay correctness and per-slot draft context;
6. speculative-round replay/verify/head/sync economics;
7. only then deeper MTP / compiled multi-agent combinations.

Canonical center remains **40 TG / 400 cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

Preserve full residency first. Updated speculative order:

1. native/full-head baseline with checkpoint completeness + greedy verifier-only equivalence;
2. measure replay fraction/cost, marginal verify-position cost, head bytes and host syncs;
3. eliminate avoidable replay/head/sync overhead if reproduced;
4. full-head MTP-head quantization A/B with memory/context headroom;
5. only then aggressive FR-Spec/vocab trimming or deeper draft depth;
6. judge by acceptance, accepted tokens/cycle, true drafting share, TG, E2E wall and peak VRAM.

Canonical center remains **120 TG / 250 cold PP**.

## Single M1 Max64 Qwen3.8-27B

P69 remains separate: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

Canonical center remains **25 TG / 110 native cold PP**.

## Dual-M1 DS4-0731

No exact-rig update. Metal scratch/temp allocation remains a transfer candidate. M5 TensorOps remains a separate approximate hardware lane.

Canonical center remains **15 TG / 180 cold PP**.

---

# Standing decisions strengthened this pass

- Optimize speculative decoding as a **whole-round system**, not a drafter-only kernel.
- Partial-accept recurrent replay can cost another full verifier read; measure replay fraction and milliseconds.
- Measure M=1 vs M>1 verifier geometry on the actual target kernel/runtime; roofline assumptions are not receipts.
- Full-head bytes and host synchronization count are first-class speculative metrics.
- Charged/forced diagnostic timing must be excluded from ordinary benchmark leaderboards.
- Sparse-QSA correctness requires deterministic accumulation behavior, not merely the right selected set.
- Near-tie score distributions belong in QSA certification.
- Hardware-specific approximate matrix routes must be labeled/quality-certified separately from exact-runtime evidence.
- Previous gates remain active: cache effectiveness/frontier, first-repeat reuse, ordinary recurrent rollback, per-slot MTP context, concurrent state isolation, persistent runtime identity, checkpoint/tensor completeness, greedy verifier-only equivalence and explicit TG denominator/provenance.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
