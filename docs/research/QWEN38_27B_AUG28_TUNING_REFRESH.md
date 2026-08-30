# Qwen3.8-27B tuning refresh — Aug 28, 2026

Status: **FRESH EXTERNAL SCAN / directly relevant to `project51-q8-verifier` after P69B12**

Updated: 2026-08-28 evening ET.

## Local project checkpoint used for this refresh

The current GitHub `project51-q8-verifier` branch is at:

- commit `5d6325f8747f8634061d1ea2e9bedf57a1010588`;
- P69B12 B/A piggyback promoted;
- current raw absolute 29,297-token TG record remains P69B11 at ~19.5551 tok/s, with P69B12's one-off absolute run essentially tied within cross-session noise;
- next series is P69B13;
- do not rerun P69B7 profiling;
- do not reopen P69B8, P69B9, P69B10-C, or P69B12-A.

P69B13 must still select from the already-measured remaining high-leverage GDN/projection/downstream-tail structure. This external scan is a source of implementation ideas and future side lanes, not permission to discard that measurement discipline.

## Executive delta

1. **A live Qwen3.8-27B native-MTP optimization challenge now exists on Apple Silicon and matches our target geometry almost exactly.** Layr Labs' `qwen3.8-27b-mtp-v1` uses the official 27B geometry, an MLX 4-bit affine/group-64 backbone, and the official 15-tensor BF16 MTP head. The editable surface includes the MLX kernels, target runtime, draft schedule/depth (0..8), speculative apparatus, and even MTP head weights. This is now the highest-value external repository to mine for independent verifier/kernel ideas.
2. **Upstream MLX independently identified and fixed the same GQA K/V-reuse bottleneck that P60/P61 attacked.** Issue #4076/#4077 reports that `sdpa_vector_2pass_1` reread K/V once per query head instead of once per KV-head group. Reassigning SIMD work to reuse K/V across query heads produced 1.14-1.27x kernel speedups at 32K and ~9% end-to-end gains on tested models. This strongly validates P61 HEADPAIR/HPT2's architectural direction. Before any future attention reopening, compare the upstream implementation against our exact GQA6/M4 specialization.
3. **Native MTP and context-derived n-gram speculation already compose in llama.cpp on Qwen3.8-27B.** A current llama.cpp issue explicitly reports `--spec-type draft-mtp,ngram-mod` working on the 27B target. Adding an external DFlash draft simultaneously is currently broken at initialization because the MTP context is incorrectly requested from the non-MTP draft model. For MXFORGE, MTP+ngram is therefore the cheapest future speculation side lane to measure before adding a second draft model.
4. **DFlash2 is now a serious alternative-speculation reference for 27B, but it does not displace P69 single-stream verifier work.** A public L4 24GB deployment runs Qwen3.8-27B UD-Q4_K_XL with a ~1.14 GiB DFlash2 Q4_K_M draft over a 226K window, reporting ~33 tok/s seven-workload average in its same-harness comparison and workload-dependent accepted lengths around 2.6-3.6. The important lesson is adaptive economics and GPU-side sampling, not a direct Apple speed prediction.
5. **M5 Cider W8A8 demonstrates a large prefill lane, not an exact Q8 verifier replacement.** Qwen3.8-27B-8bit prefill reportedly improves ~1.3-1.53x with ~5.8GB lower long-context peak memory, but the path changes arithmetic: ~2.16% higher WikiText perplexity and only 19/22 exact deterministic sequences. It conflicts with P51's exact-trajectory discipline and should stay out of P69B13.
6. **The external ecosystem increasingly confirms that verifier arithmetic order is a first-class correctness/performance variable.** The Layr challenge explicitly scores against target fidelity; llama.cpp and other 27B work continue to report MTP/output divergence when block verification takes a different reduction path. This reinforces the P53/P60 lesson: a faster kernel that changes the speculative trajectory is not automatically a valid structural promotion.

## 1. Layr Labs Qwen3.8-27B native-MTP challenge

Source:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge

Current live track:

- `qwen3.8-27b-mtp-v1`;
- reference backbone: MLX 4-bit affine, group size 64;
- official Qwen3.8-27B source;
- official 15-tensor BF16 MTP head;
- 64 layers;
- hidden size 5120;
- 24 query heads;
- 4 KV heads;
- head dim 256;
- vocab 248320;
- same four-layer hybrid repeat as the Qwen3.8 family.

The editable surface is unusually broad:

- model execution/runtime;
- MLX Metal kernels;
- speculative drafting code;
- per-round draft depth and schedule, including adaptive 0..8;
- MTP head weights themselves.

The challenge's own published baseline note says the unmodified MTP tree is roughly 0.994x serial on its scoring ruler. That is useful independent confirmation of the same phenomenon P51 found early: native MTP is not automatically profitable unless verifier cost and acceptance economics are jointly optimized.

### Action for P51/P69

Do not change P69B13 merely because this challenge exists. Instead:

1. periodically inspect its accepted/high-scoring submissions and diffs;
2. classify any winning changes into:
   - projection/QMM;
   - GDN/recurrent;
   - attention/KV reuse;
   - LM head/sampling;
   - MTP schedule/head;
   - graph/dispatch/materialization removal;
3. only transfer a candidate into P69 if it maps to a currently measured residual seam and can preserve our frozen arithmetic/trajectory contract.

This repository is now probably the best external source for 27B-specific Apple verifier ideas because the geometry and objective are so close to ours.

## 2. Upstream MLX GQA K/V reuse validates P60/P61

Sources:
- https://github.com/ml-explore/mlx/issues/4076
- https://github.com/ml-explore/mlx/pull/4077

Upstream diagnosis:

`sdpa_vector_2pass_1` assigned one SIMD group per query head, causing every query head in a GQA group to stream the same K/V bytes independently. The issue reports effective bandwidth collapsing on high-GQA shapes even when DRAM bandwidth was available.

The fix reorganizes work so one SIMD group handles a token subchunk and computes several query heads from registers, reducing repeated K/V loads while leaving the second pass unchanged.

Reported evidence at 32K:

- kernel-level improvement: ~1.14-1.27x;
- Qwen3-30B-A3B end-to-end: +9.5%;
- Qwen2.5-3B end-to-end: +9.2%.

### Relationship to our P60/P61

Our certified 27B verifier specialization independently reached the same architectural principle under a harder geometry:

- verifier q_len/M = 4;
- GQA = 6;
- head_dim = 256;
- exact native 256-block two-pass topology retained;
- HEADPAIR HPT2 reuses K/V across adjacent query heads at the same verifier row;
- frozen 186-cycle / 325-of-442 trajectory preserved.

Therefore this upstream work is **validation, not a reason to reopen attention immediately**.

Before any future attention experiment, diff the upstream #4077 implementation against P61 and ask only whether it exposes a genuinely new reuse/layout trick that our M4/GQA6 path does not already exploit. Otherwise keep P61 closed.

## 3. Native MTP + `ngram-mod` already composes on 27B

Source:
- https://github.com/ggml-org/llama.cpp/issues/27839

The issue's environment explicitly states:

- target: Qwen3.8-27B UD-Q4_K_XL with MTP layers;
- `--spec-type draft-mtp,ngram-mod` works on the target;
- adding `draft-dflash` with an external non-MTP draft model currently fails at initialization because the runtime requests an MTP context from that external draft.

### MXFORGE implication

After the current structural P69 series, add a separate speculation-policy ruler:

```text
A. native MTP only
B. native MTP + ngram-mod
C. target-only + ngram-mod
```

Run it on at least two workloads:

1. the frozen 29.3K novel/coding ruler;
2. a copy/edit/patch-heavy agent ruler deliberately containing reusable source text.

Do not assume a gain on the current frozen ruler. Context-derived drafting pays according to output overlap, not model class.

This lane is attractive because it needs no extra learned draft model and can potentially accelerate agent edits that native MTP handles only moderately well.

## 4. DFlash2 is a real 27B alternative, but later

Sources:
- https://github.com/ggml-org/llama.cpp/pull/27342
- https://github.com/hanxiao/Qwen3.8-27B-UD-Q4_K_XL-L4

A public L4 24GB recipe demonstrates:

- Qwen3.8-27B UD-Q4_K_XL target;
- DFlash2 Q4_K_M draft around 1.14 GiB;
- context 226,048;
- `n-max 7`;
- seven-workload same-harness shipped average ~32.96 tok/s versus ~24.18 stock;
- workload accepted lengths roughly 2.65-3.60 in the 256-token tests;
- code ~32.57 tok/s in that same table;
- long summarization becomes much more favorable as generation continues.

The same report emphasizes two implementation lessons relevant beyond CUDA:

1. sampling/logit handling can dominate if a verifier copies the full 248,320-vocab row to the host for every verified position;
2. speculation depth must be workload-adaptive because acceptance changes radically across math, code, prose, chat and generation phase.

### P51 implication

Do not pivot from native MTP to DFlash2 during P69.

A later controlled A/B is worthwhile only after:

- the structural native verifier is stable;
- MTP+ngram has been measured;
- a suitable Apple DFlash2 runtime/draft is available without distorting memory pressure.

The main question is complete task time and memory, not whether DFlash2 can win on a different GPU/backend.

## 5. Cider W8A8: strong prefill, wrong contract for current P51

Source:
- https://github.com/jundot/omlx/discussions/3136

Reported M5 Max / Qwen3.8-27B-8bit prompt throughput:

| Prompt | MLX W8A16 | Cider W8A8 | Gain |
|---:|---:|---:|---:|
| 511 | 771 | 1003 | 1.30x |
| 1,975 | 796 | 1044 | 1.31x |
| 7,879 | 722 | 1106 | 1.53x |
| 31,471 | 494 | 756 | 1.53x |
| 62,935 | 415 | 579 | 1.39x |
| 96,031 | 343 | 458 | 1.34x |

Long-context peak memory fell by roughly 5.8 GB in the reported runs.

But this is a symmetric per-channel W8A8 path with activation quantization, not an exact replacement for MLX affine Q8/W8A16:

- WikiText PPL: 7.475 -> 7.637 (~+2.16%);
- exact deterministic generated sequence: 19/22;
- same first token: 21/22.

### P51 implication

Do not use this inside the exact P69 verifier path.

Possible future role:

- optional prompt-processing-only acceleration;
- separate quality-certified serving profile;
- M5-generation work where INT8 TensorOps are much more relevant than M1.

It is not a P69B13 candidate for the current M1/Q8 exact-trajectory project.

## 6. New decision rubric for P69B13

The external scan does **not** change the recorded P69B13 rule:

- select the next candidate from measured remaining high-leverage GDN/projection/downstream-tail structure;
- no new profiling rerun;
- no reopening P69B8/P69B9/P69B10-C/P69B12-A.

It adds two checks before implementing the next candidate:

### Check A — Layr challenge

Search current high-scoring Qwen3.8 MTP submissions for a 27B-specific implementation of the same seam. If one exists, use it as an implementation reference, not as promotion evidence.

### Check B — upstream MLX

If the candidate touches attention/KV or generic quantized small-M primitives, confirm whether upstream MLX has changed since our local fork. Reuse a proven upstream primitive only if its arithmetic/order can satisfy the frozen exactness contract.

## Recommended queue after the current P69 structural series

1. **Finish P69B13+ from measured structural remainder.** This remains the highest-confidence way to push the frozen 29.3K single-stream ruler beyond ~19.55 tok/s.
2. **Mine the Layr Qwen3.8 MTP challenge** for independent 27B-specific winners.
3. **MTP + ngram-mod A/B** on both novel-code and copy/edit agent workloads.
4. **Batched native MTP for 27B concurrency**, borrowing the same per-row rollback/always-advance ideas now being tested for Flash-Next in oMLX.
5. **DFlash2 vs native MTP** only as a separate speculation architecture experiment.
6. **Prefix-cache/API exactness and session affinity** for real agent serving.
7. **Optional non-exact prefill lanes such as Cider W8A8** only under a separate quality contract.

## Forecast impact

For the current frozen P69 single-stream exact verifier, the scan does not justify raising the immediate structural forecast dramatically. P69B13 is still likely to be an incremental win unless another bundle eliminates a full materialization/dispatch family.

The larger upside is now outside the narrow single-stream structural ruler:

- context-derived speculation can produce very large gains on copy/edit-heavy traffic;
- DFlash2 offers a distinct learned-draft economics point;
- batched MTP could materially improve 3-5-agent aggregate throughput;
- the Layr challenge may surface new 27B-specific kernel/schedule ideas faster than isolated local search.

The correct strategy is therefore:

> keep the P69 structural path disciplined, while opening separate measured lanes for speculation composition and concurrency rather than mixing them into the current exact verifier campaign.
