# Project 51 primary-lane research watch — 2026-09-29 08:58 ET

**Freshness boundary entering this pass:** **2026-09-29 10:01:02 UTC**.  
**User cutoff:** **2026-09-29 12:57:59 UTC**.

## Decision

**Durable STATE + TARGETS update.**

The main target change is now justified by a complete physical matrix rather than extrapolation:

### Strata cold-PP true-up

On the weaker RTX 5070 12 GB, engine 0.1.22 physically measures:

| Quant | 32K PP | 64K PP | 128K PP |
|---|---:|---:|---:|
| IQ3_XXS | **1,555** | **1,449** | **1,386** |
| IQ3_S | **1,499** | **1,285** | **1,245** |

The P51 RTX 5070 Ti planning centers therefore move conservatively to:

| Quant | 32K PP target | 64K PP target | 128K PP target |
|---|---:|---:|---:|
| IQ3_XXS | **1,500** | **1,400** | **1,300** |
| IQ3_S | **1,450** | **1,250** | **1,200** |

Physical TG targets, AA priors and dual-M1 Flash targets do **not** move.

## Strict-window findings

### NEW — full Strata 0.1.22 prompt matrix

Source:
https://github.com/Niko1221/Strata/commit/cd97dafa303f8842df8d72ec1464f1158d9cd77d  
Timestamp: **2026-09-29 11:38:54 UTC**.

Hardware / settings:
- RTX 5070 12 GB, PCIe 5 x16;
- Ryzen 5 7600;
- 64 GB DDR5-5200;
- Windows 10;
- MTP spec4;
- greedy;
- INT8 KV above 4K;
- KV streaming from 64K;
- one code-agent prompt per cell.

Measured prompt matrix:

| Quant | 32K | 64K | 128K |
|---|---:|---:|---:|
| Q2_0 | 1,844 | 1,836 | 1,682 |
| IQ2_XS | 1,799 | 1,611 | 1,495 |
| IQ3_XXS | **1,555** | **1,449** | **1,386** |
| IQ3_S | **1,499** | **1,285** | **1,245** |
| Coder | 1,871 | 1,938 | 1,779 |

The IQ3 rows are the target-moving evidence. They physically clear the previous P51 PP centers on a weaker 12-GB 5070.

The same matrix's decode rows are not used to move P51 TG targets because:
- the user's 5070 Ti has materially more VRAM;
- existing exact-user decode receipts are stronger;
- each cell is one generated continuation and MTP acceptance varies with text.

### NEW — Strata 0.1.24 QSA-selection prompt acceleration

Sources:
- https://github.com/Niko1221/Strata/commit/731899f6a1ae5c69704fa920eb2819a3b47d2784
- https://github.com/Niko1221/Strata/commit/3ce2523c2823687de5372be3af58534f56cbf286

Timestamps: **11:40:49 / 11:53:04 UTC**.

RTX 5070 / Q2_0:
- 32K prompt: **1,742 -> 1,797 PP**;
- 128K prompt: **1,608 -> 1,843 PP (+14.6%)**;
- QSA-select portion at 128K: **14.6 -> 4.2 s**;
- TTFT at 128K: **82.7 -> 72.3 s**.

Mechanism:
- block scores as tensor-core GEMM using 3x-TF32;
- per-query top-k keys held/read once in registers;
- register top-k returns the exact same selected ids;
- block-score arithmetic is **not bitwise** to the old path.

Quality gates:
- 8K/16K/32K needles × five depths: **15/15** both;
- 16K continuation: **32/32 identical**;
- 32K top-1 same, **KL ~0.03**.

P51 interpretation:
- exact selection IDs are not sufficient for exact model equivalence if score arithmetic changes;
- keep this as an approximate prompt-only path with trajectory/quality certification separate from exact verifier work;
- do **not** add 0.1.24's extra Q2 gain to the new IQ3 PP targets until a same-quant matrix lands.

### NEW — oMLX greedy MTP verifier must reproduce sampler numerics

Source:
https://github.com/jundot/omlx/commit/263752597a0e1b51264ac51280d12635b192abb4  
Timestamp: **2026-09-29 10:29:40 UTC**.

Serial MLX greedy decode samples from:
`logits - logsumexp(logits)`
in the logits dtype, then argmaxes the rounded log-probabilities.

Lightning MTP verify instead used raw-logit argmax.

For nearby bf16 logits, subtracting logsumexp can round two values to the same log-probability; the serial sampler then chooses the lower token id while raw-logit argmax chooses the higher original logit.

oMLX now uses the serial log-probability path for greedy verify.

P51 exact-verifier rule:
- exactness means **same numerical sampler pipeline**, not merely the same unnormalized logits;
- P69B13 fixtures must include near-ties where bf16 normalization changes the argmax tie.

### NEW — oMLX quantized kernel-choice exactness

Same commit.

MLX 0.32.2's one-row qmv_fast K alignment depends on weight bits:
- **512** at 4/5 bit;
- **256** at 6/8 bit.

A verifier that used K%512 for every width could execute a different arithmetic kernel from the serial one-row path.

This mismatch is latent for the currently served Qwen3.8-Flash-Next shapes, but directly matters to P51's heterogeneous mixed-bit search.

P51 rule:
- quant format alone is not enough for row-exact identity;
- **serial kernel-choice predicate** is part of verifier identity.

### NEW — oMLX late-join state handoff eliminates 111K replay

Source:
https://github.com/jundot/omlx/commit/65515c3c9c3b6d884b3a4cb828ae6e4c86e84e3c  
Timestamp: **2026-09-29 10:09:26 UTC**.

A shared Lightning batch could finish one row, leave a singleton state, then have a pending request join. The old reconciliation path rebuilt the singleton by replaying its entire history.

Observed production failure:
- survivor history: **~111K tokens**;
- replay: **~2 minutes**;
- joining request TTFT: **122 s**;
- process memory: **88 -> 116 GB**;
- PLE page cache was evicted.

The surviving row is already at a drained MTP frontier. oMLX now hands that state off with at most one forward instead of replaying it.

P51 rule:
- at a drained/materialized committed frontier, **handoff live state**;
- do not reconstruct known-good state from token history unless no direct handoff exists.

### UPDATE — Strata shared multi-conversation snapshot core

Issue:
https://github.com/Niko1221/Strata/issues/57

The RAM shared-core branch now includes:
- QSA KV + host/streaming maps;
- indexer state including the **per-sequence spare key `idx_dead`**;
- GDN / PLE state;
- MTP state;
- checkpoints;
- exact token/image/steering identity;
- used-page sizing;
- Linux + Windows physical-memory admission;
- whole-image validation before writes where possible;
- explicit fatal/fail-closed handling for mid-transfer failure.

Important audit correction:
the original snapshot omitted `idx_dead`, and the original fingerprint omitted it. Fixtures with the same opening tokens could mask the problem. A distinct-spare-key regression is now present.

This is unusually good corroboration for P51's state contract: latent/indexer spare rows are real continuation state even when normal happy-path fixtures do not expose them.

### UPDATE — physical ~120K parked-conversation soak

Same shared-core work; Linux / RTX 4090 / IQ3_S.

Passed:
- **30 returns**;
- contexts ~2,026 / 39,985 / **119,987 tokens**;
- streamed KV;
- expected known-answer outputs;
- exact baseline output/state parity;
- stable retained payload per context.

At 51,133 cached tokens:
- A -> B -> A: full prefix reused, 22 new tokens processed in **1.237 s**;
- checkpoint return: seven new tokens in **0.566 s**.

Interpretation:
- direct proof that ~120K full hybrid conversation state can be repeatedly parked/restored in host RAM;
- same-runtime RTX evidence, **not** Apple restore timing;
- does not yet prove restart persistence.

### UPDATE — Strata NVMe tier converging onto one snapshot format

PR:
https://github.com/Niko1221/Strata/pull/52

The existing simple NVMe implementation already demonstrated:
- whole-session snapshots;
- exact state validation;
- restart promotion;
- a test where only 13 new tokens were processed in ~350 ms after restart;
- round-robin long (~110K) conversations.

The author now has the simple NVMe cache working against the #57 shared snapshot API and is developing a **delta-based cache** to avoid rewriting entire snapshots every turn and to reduce duplicate storage for forks.

P51 treatment:
- unified RAM + NVMe snapshot format is the correct architectural direction;
- delta persistence remains work-in-progress until bounded staging, atomic durability, identity and corruption/failure tests are published.

### NEW — SGLang snapshot bootstrap transaction pattern

Sources:
- https://github.com/sgl-project/sglang/commit/7bcfcf5aa0e511058fb1fe021c9b17ad99d993c4
- https://github.com/sgl-project/sglang/commit/8b3a4cad8be68a23f480b4c4ee07189150931d86
- https://github.com/sgl-project/sglang/commit/8d1643b21ea43ab86d9575302075fd1b951ab313
- https://github.com/sgl-project/sglang/commit/4a4e1ce0140cacc52e2903bc8403ad762f6c68c7

Timestamps: **10:56:32 -> 12:07:37 UTC**.

A booting router/rank:
1. subscribes to live events before snapshot fetch;
2. buffers incoming batches while pending;
3. fetches a sibling snapshot;
4. vets it before it may touch the tree;
5. applies the snapshot through the single writer;
6. proves sequence/watermark continuity;
7. releases held deltas after the splice.

P51 consequence:
this is very strong cross-runtime support for the CUDA->Apple/full-state handoff transaction:
- begin receiving deltas before snapshot;
- validate whole image before mutation;
- mutate through one state owner;
- prove frontier continuity;
- then expose/release subsequent work.

### SAME-DAY CURRENT — M3 Ultra full-262K Flash report

Source:
https://www.reddit.com/r/MacStudio/comments/1wt6w03/qwen38_flash_next_q4_at_full_262k_context_on_a/

Self-reported 96-GB M3 Ultra / Q4 Flash-Next:
- full 262K context;
- **55-60 TG decode**;
- **~667 cold PP**;
- cached turns reportedly **0.3-0.8 s**;
- ~90% GPU memory allocation and little room for normal desktop use.

P51 interpretation:
- useful stronger-Apple long-context transfer evidence;
- not exact M1 Max/TB4 evidence and does not move the 40-TG probability ladder.

## RECOVERED CURRENT — TensorFold 0.3.6.3

Release:
https://github.com/ashhart/TensorFold/commit/191188075bca56a7c71074a79375eb4c1cb22e1c  
Timestamp: **2026-09-29 04:51:55 UTC** — before this pass's strict window, so not NEW.

### Flash-Next NVFP4 CUDA

Published NVFP4 Flash checkpoints now:
- run as published on one CUDA GPU;
- drafted output equals serial output;
- resumed prompts equal fresh prompts;
- **84/84 concurrent streams equal their solo runs**.

On one DGX Spark, TensorFold reports Flash NVFP4 decode **1.13-1.52x vLLM** on the same checkpoint.

Limits:
- NVFP4 is currently one-rank only;
- two-rank NVFP4 refused;
- PLE-on-SSD refused;
- images refused until qualified.

P51 interpretation:
- strong exact-concurrency / ModelOpt-NVFP4 mechanism evidence;
- not an exact user's-5070Ti performance ladder.

### Decode-share during long prefills

On M3 Ultra, three incoming ~17K prompts previously stalled a running reply for up to **164 s**. Chunked interleaving with decode-share cuts the longest pause to **7 s**, while a request served alone is unchanged.

P51 consequence:
- agent UX needs a **latency-fairness / max-pause metric** in addition to cold PP and aggregate throughput;
- long prefill should not monopolize the engine when an interactive decode is active.

### Warm long conversations

Under an emulated 64-GB budget on M3 Ultra:
- one 27B conversation grows to **143K tokens**;
- resumed turns remain **38-46 s**;
- 0.3.6.2 had fallen back to full re-prefill beyond ~100K.

The fix:
- does not evict existing good checkpoints until a new checkpoint is known to fit;
- no longer retains an unnecessary copied stored prefix;
- reduces DFlash2 prompt taps from **114 KB/token -> 64 KB/token**.

This further reinforces P51's rule:
**allocated context != resident/resumable context**.

### M1-M4 prompt kernels

TensorFold 0.3.6.3 also adds M1-M4-specific Flash prompt work:
- one-expert-per-GPU-tile MoE scheduling;
- batched QSA block-score matmul;
- GQA scoring/tuned top-512 selection;
- same-bit behavior.

Reported M3 Ultra gains are only a few percent. Useful implementation evidence, not a new exact M1 Max E2E receipt.

## Low-priority strict-window findings

- llama.cpp `8019dc56`: collect all graph input tensors before PP graph copying so switching request shapes/modalities does not spuriously change scheduler graph composition and force bad re-reservation.
- oMLX `5ea8cfc1`: fixes causal masking in a decode fallback path.
- vLLM strict MiMo tool-calling/frontend changes are not material to current P51 performance targets.

## Strict-window negative scan

- **Exact M1 Max Flash-Next:** no newly published reproducible ~27-TG fork/settings/context receipt.
- **Exact dual M1 Max / TB4 Flash:** no new physical sustained 128K receipt.
- **DASLab Flash IQ3_S long-context source-paired quality:** no new official 32K/64K/128K/262K paired result found.
- **mlx-serve:** no post-boundary Flash commit.
- **Ishizuki:** no post-boundary commit.
- **Exact user's RTX 5070 Ti Strata:** no direct 0.1.22/0.1.24 matrix yet; targets are raised from a weaker-card lower-bound receipt.
- **Strata TG ladder:** no target-moving exact-user decode matrix in this pass.

## Durable target changes

### Strata IQ3_XXS cold PP

Previous:
- 32K **1,300**
- 64K **1,250**
- 128K **1,150**

New:
- 32K **1,500 PP / ~90%**
- 64K **1,400 PP / ~90%**
- 128K **1,300 PP / ~85%**

### Strata IQ3_S cold PP

Previous:
- 32K **1,200**
- 64K **1,150**
- 128K **1,050**

New:
- 32K **1,450 PP / ~90%**
- 64K **1,250 PP / ~85%**
- 128K **1,200 PP / ~85%**

### Not changed

- Dual-M1 Flash-Next: **40 TG sustained @ genuine ~128K / 400 cold PP / ~70% >=40 TG**.
- Single-M1 dense27B: **25 TG / ~110 PP**.
- Strata IQ3 TG targets unchanged.
- IQ3_XXS AA>=38: **~85%**.
- IQ3_XXS AA>=40: **~65%**.
- IQ3_S AA>=40: **~80%**.
- Swift Flash and dense Swift remain effective-task-throughput lanes, not physical TG multipliers.
- Persistent Apple root restore-latency target unchanged.

## New hard boundary

**2026-09-29 12:57:59 UTC**
