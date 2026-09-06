# External runtime research watch — 2026-09-06 02:43 ET

Starting branch checkpoint: `6a338ab826e620a7d45407b04cb303cb353f0180`

Starting hard freshness cutoff: **2026-09-05 23:49:49 UTC**.

Classification rule:

- **FRESH** = created, updated, commented or committed strictly after the cutoff;
- **BACKFILL** = older evidence newly surfaced and material to experiment design;
- **KNOWN / NO CHANGE** = already represented or unchanged after the cutoff.

---

# Result

This pass found **two fresh material runtime/certification results**:

1. rMLX #518 directly decomposes Qwen3.8-27B MTP round cost, removes a verifier-head re-read and identifies accepted-prefix replay plus multi-row verify cost as the dominant remaining speculative bottlenecks;
2. vLLM #54521 isolates a QSA correctness seam where the selected top-k **set is correct but the emitted order is nondeterministic**, and that raw order feeds floating accumulation.

A useful M5-Max ds4 TensorOps result was also backfilled as a separate approximate/non-exact Apple lane.

No new sustained physical receipt surfaced from any of the four target rigs. `RESEARCH-TARGETS.md` therefore remains unchanged.

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

---

# FRESH / material

## 1. rMLX `fd33c684a8b4deefb78df2c9ae46e69b5856a02a` / #518 — speculative-round economics become a first-class optimization surface

Fresh commit time: **2026-09-06 02:39:56 UTC**.

On a quiet host, block 3, 86 rounds, 4-bit Qwen3.8-27B verifier plus MTP sidecar, charged diagnostic timing reports:

| round class | n | round ms | draft | verify | walk | rollback | other |
|---|---:|---:|---:|---:|---:|---:|---:|
| replayed / partial accept | 34 | 76.68 | 4.16 | 40.47 | 0.000 | **31.99** | 0.055 |
| full accept | 52 | 46.09 | 4.18 | 41.81 | 0.000 | **0.027** | 0.066 |

### What this establishes

- On a partial-accept round, the loop restores the pre-round state and **re-runs the accepted prefix through the whole verifier stack**. That is effectively a second full verifier weight read.
- The recurrent-state snapshot itself is not the expensive operation. Snapshot, emission, truncation and bookkeeping together measured about **0.06 ms**.
- The verify graph already had the block logits available, but the acceptance walk had been re-deriving the quantized LM head one position at a time. Reading the verifier argmax once from the already-built block result produced a measured **+1.96% decode** on this pair, with ABBA/BAAB placement, binary identity checks and identical output digests.
- With like-for-like timing, the material residual is the accepted-prefix replay: about **12.7 ms/round averaged at block 3**, not an unexplained snapshot cost.

### The second ceiling: verifying an additional position is unexpectedly expensive

The same work measures the marginal cost of one extra verified position at roughly one quarter of a plain decode step:

| model | plain step | marginal verify / extra position | fraction |
|---|---:|---:|---:|
| Qwen3.8-27B 4-bit GDN hybrid | 30.77 ms | 7.27 ms | **0.236x** |
| Gemma4 E4B MXFP8 full attention | 11.90 ms | 2.88 ms | **0.242x** |

A simple bandwidth roofline would suggest roughly 0.04x. The similar fraction on recurrent and full-attention architectures argues against GDN recurrence as the sole cause; a quantized multi-row / kernel-dispatch effect is now the leading test candidate.

Removing replay alone therefore projects only to about **1.56x**, not the prior 2.2x aspiration for this loop.

For the Qwen3.8 pair, block-2 -> block-3 round growth was decomposed as roughly:

- +7.27 ms verify;
- +6.24 ms replay;
- +2.03 ms draft.

The deeper-block penalty is therefore split between verify geometry and replay rather than being a replay-only problem.

### Fresh #496 follow-up sharpens draft-side costs

The corrected speculative accounting is:

`tokens_per_round = 1 + accept_rate * (block - 1)`.

For the measured Qwen3.8-27B MXFP8/MTP pair:

- block 2: acceptance 0.877, 1.88 tokens/round, measured 1.36x speedup, implied step cost **1.38x plain**;
- block 3: acceptance 0.728, 2.46 tokens/round, measured 1.23x speedup, implied step cost **2.00x plain**.

Three additional depth-scaling costs were identified in the MTP drafter path:

1. full 248,320-vocab LM-head materialization per drafted token — about **1.3 GB per draft token** on the cited 4-bit checkpoint;
2. one host synchronization / read-back per drafted token;
3. one trailing sidecar step per round.

### Promotion to our experiment order

Before treating deeper MTP or aggressive draft-vocabulary trimming as the next lever, profile and attack the whole speculative round in this order:

1. accepted-prefix rollback/replay — eliminate a second verifier weight read if the architecture permits exact state selection/delayed commit;
2. verifier-head reuse — never re-derive per-position logits when the verify block already produced the needed result;
3. quantify **M=1 vs M=2/3/... quantized verify cost** on the target runtime/hardware;
4. remove avoidable per-draft full-head reads and host synchronizations;
5. then re-optimize block depth and compare full-head quantization vs FR-Spec/vocab trimming.

New required speculative metrics:

- partial/replayed-round fraction;
- rollback/replay ms;
- marginal verify ms per added position;
- full-head bytes read per round;
- host synchronizations per round;
- acceptance, accepted tokens/cycle, true drafting share, TG and E2E wall;
- peak memory/context headroom.

**Instrumentation warning:** the new charged phase-split forces otherwise-lazy work so timing is attributable. That changes scheduling. Charged diagnostic rows must be marked and excluded from ordinary champion/performance tables; use them for attribution, not final rate claims.

This is strong mechanism and measured runtime evidence, but not an exact M1-Max or RTX5070Ti rate receipt.

---

## 2. vLLM #54521 fresh follow-up — QSA selected-block order is a correctness invariant when accumulation is order-sensitive

Issue activity is fresh after the cutoff and materially changes the diagnosis.

Earlier discussion associated greedy nondeterminism with crossing `indexer_budget`. A fresh independent GB10 reproduction found divergence even at **582 prompt tokens**, below one third of a 2,048 budget, and it persisted with MTP disabled. The budget threshold is therefore not a sufficient explanation.

A later controlled kernel test isolates a stronger mechanism on the real QSA geometry:

- `columns = 65,536`;
- `k = 512`;
- 10 identical calls with narrow-range indexer logits;
- when `visible > k`, `persistent_topk` returns the **correct set** of selected indices but in a **run-varying order**.

Representative results at `visible=1024`:

| rows | exact order identical | selected set identical |
|---:|---:|---:|
| 1 | **1/10** | **10/10** |
| 4 | **1/10** | **10/10** |
| 32 | **1/10** | **10/10** |
| 64 | **1/10** | **10/10** |
| 128 | **1/10** | **10/10** |
| 512 | **1/10** | **10/10** |

At `visible=480` (< k), both order and set were 10/10 stable.

The existing kernel correctness tests can miss this because they compare selected sets / sorted indices. The raw unsorted output is then consumed by QSA expansion and sparse-attention accumulation. If the same blocks are accumulated in a different order, floating-point reduction order changes; near-tied logits can therefore flip even though the top-k **set** is mathematically correct.

A separate attempted fix (#53287) did not change the end-to-end nondeterminism. The fresh investigation also corrects an earlier suspicion: the cooperative-top-k exclusion on GB10 is intentional because that backend failed to launch on this hardware; simply removing the family gate is not a fix.

### Promotion to Flash QSA certification

For every selected-KV/QSA gather path — including future Metal implementations — test all of the following separately:

1. selected **set** equality versus a reference implementation;
2. selected **order** determinism over repeated identical runs;
3. candidate output/logits versus a canonical deterministic ordering (for example sorted indices if semantics allow);
4. prefill and decode separately;
5. MTP on and off;
6. serial and concurrent request scheduling;
7. adversarial narrow-range / near-tie indexer scores.

A result with valid indices, no duplicates and the correct selected set is **not sufficient** when downstream floating accumulation depends on order.

If selected-block order is not semantically meaningful, normalize it before order-sensitive accumulation rather than relying on incidental kernel emission order.

This is NVIDIA/GB10 evidence and does not imply an Apple bug. It changes our Flash correctness gate, not the 2x-M1 rate target.

---

# BACKFILL / separate approximate lane

## M5 Max ds4 Metal TensorOps — substantial agent speed win despite known numerical drift

A pre-cutoff M5-Max finding, with post-cutoff issue closure/activity, is useful as a policy backfill rather than a target-rig receipt.

The TensorOps route had already been independently reproduced as numerically divergent on long prompts:

- `metal-tensor-equivalence` worst RMS about **1.386** and worst max-abs about **7.27**;
- long memory/code prompts can flip the first greedy token;
- reference kernels restore bit-identical behavior in the cited controls.

A pre-registered 15-task x 3-sweep route A/B then compared the fast TensorOps route (T) with reference kernels (R), one binary and one treatment variable:

- paired wall ratios T/R: **0.900, 0.768, 0.690**;
- pooled wall ratio: **0.786** (reference roughly 1.27x slower);
- task-run passes: **T 43/45, R 38/45**;
- the pre-registered “route buys with no measured agent-task break” screen fired.

This does **not** restore exactness: the lower-level numerical-divergence gate still fails. It establishes that a materially faster approximate route can pass a finite agent suite while remaining non-bit-exact.

Policy:

- accelerated Metal numerical routes must stamp the exact route in every result;
- task-level parity cannot replace the logit/greedy equivalence gate;
- keep such paths in an explicitly approximate/quality-certified serving lane;
- do not transfer M5 TensorOps speed or quality conclusions to M1 Max.

---

# FRESH / monitor only

## llama.cpp `971595d6697f53b215d02a8381f8b5af142a4d86` — more M2-Max FA-vector tuning landed

Fresh upstream Metal commit adds tuned FA-vector table entries for Q4_0/Q4_1/Q5_0/Q5_1 across many shapes on M2 Max.

No benchmark receipt or M1 mapping is attached to the PR body inspected in this pass. Treat as implementation freshness / a future tuning table to inspect, not an M1 performance ruler.

---

# Focused follow-up status

- **oMLX #3462:** still open, 0 comments; no fix or maintainer response surfaced.
- **oMLX #3464:** still open, 0 comments; no logging fix surfaced.
- **jundot/omlx main:** no commits after the cutoff.
- **llama.cpp #28425:** unchanged; ordinary no-spec recurrent rollback gate remains active.
- **llama.cpp #28433:** unchanged; per-slot MTP draft-context sizing gate remains active.
- **llama.cpp #28448:** unchanged; allocator identity remains monitored, not an Apple/Flash blocker.
- **llama.cpp #25187:** no fresh activity; full-head quantization before aggressive FR-Spec trimming remains the 5070 ordering.
- **antirez/ds4 main:** no commits after the cutoff.
- **ml-explore/mlx main:** one fresh CUDA completion-worker fix only; no Apple/M1 runtime change relevant here.
- **MLX #4409:** still open; no new M1 receipt surfaced.
- **wtdcode/vllm-backport:** no commits after the cutoff.
- **Exact M1-Max / dual-M1 search:** no new exact target-rig result surfaced.
- **Exact RTX5070Ti Qwen3.8 search:** no new exact-card receipt surfaced.

---

# Updated consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Add/strengthen these gates before promoting sparse QSA or MTP performance:

1. ordinary no-spec recurrent rollback correctness;
2. real-agent cache-capture frontier + first-repeat/second-repeat effectiveness;
3. selected-QSA **set AND order determinism**, canonical-order logit equivalence, near-tie stress, prefill/decode split;
4. PLE residency/page-cache/direct-read and QSA known-horizon memory controls;
5. MTP snapshot/commit/replay correctness and per-slot draft context;
6. speculative round decomposition: replay fraction/cost, marginal verify-position cost, head reads and host syncs;
7. only then deeper MTP / compiled multi-agent combinations.

Canonical center remains **40 TG / 400 cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

Preserve full residency first. Updated speculative order:

1. native/full-head MTP baseline with checkpoint completeness + greedy verifier-only equivalence;
2. measure round-loop replay, marginal verify-position cost, head bytes and host synchronizations on the exact 5070 runtime;
3. eliminate avoidable replay/head/sync overhead if reproduced;
4. full-head MTP-head quantization A/B with memory/context headroom recorded;
5. only then aggressive FR-Spec/vocab trimming or deeper draft depth;
6. compare acceptance, accepted tokens/cycle, true drafting share, TG, E2E wall and peak VRAM.

Canonical center remains **120 TG / 250 cold PP**.

## Single M1 Max64 Qwen3.8-27B

External speculative evidence does not alter P69. **P69B12 remains frozen/promoted; P69B13 remains next from existing profiling only.**

Canonical center remains **25 TG / 110 native cold PP**.

## Dual-M1 DS4-0731

No exact-rig update. Metal scratch/temp allocation remains a transfer candidate. M5 TensorOps evidence belongs to a separate approximate hardware lane and does not move the M1 target.

Canonical center remains **15 TG / 180 cold PP**.

---

# Standing decisions strengthened this pass

- Optimize speculative decoding as a **whole round**, not as drafter kernel time alone.
- Partial-accept recurrent replay can cost a second verifier weight read; measure replay fraction and replay milliseconds explicitly.
- The marginal cost of M>1 verification must be measured on the target kernel/runtime; roofline assumptions are not sufficient.
- Do not re-read or re-materialize a full LM head per verify/draft position unless physically justified.
- Host synchronization count is a first-class speculative metric.
- Diagnostic timing that forces evaluation can change scheduling; charged rows must never compete with ordinary benchmark rows.
- Sparse-QSA correctness requires deterministic accumulation behavior, not merely a correct selected set.
- Near-tie score distributions belong in the QSA correctness suite.
- Hardware-specific approximate matrix routes must be labeled and quality-certified separately from exact-runtime evidence.
- All previous gates remain active: cache effectiveness/frontier, first-repeat reuse, ordinary recurrent rollback, per-slot MTP context, concurrent state isolation, persistent runtime identity, checkpoint/tensor completeness, greedy verifier-only equivalence and explicit TG denominator/provenance.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
