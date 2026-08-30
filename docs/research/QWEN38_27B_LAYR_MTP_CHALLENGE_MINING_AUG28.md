# Qwen3.8-27B Layr MTP challenge mining — Aug 28, 2026

Status: **HIGH-SIGNAL EXTERNAL MECHANISM AUDIT / P69 implementation intelligence**

Updated: 2026-08-28 evening ET.

Companion to `QWEN38_27B_AUG28_TUNING_REFRESH.md`.

This note mines the public Layr Labs `qwen3.8-27b-mtp-v1` submission history for mechanisms that transfer conceptually to MXFORGE's exact Q8 verifier campaign. It deliberately separates **officially promoted evidence** from locally positive but officially rejected probes.

## Executive result

The single most relevant public mechanism is the officially promoted **producer-side xsums fusion** at Layr PR #1197 / commit `0863b06ac16e26e48fc06e97444095b00feb66d4`.

That change removes standalone per-QMV activation chunk-sum fill dispatches by making an already-required fused residual+RMSNorm producer emit the exact side table consumed by the following quantized matvec. The official submission was merged. The promoted lineage is reported at score ~`3.7291100105909`, although subsequent source-identical reruns demonstrate substantial benchmark variance; the mechanism should be valued for its causal structure and merge result, not the final decimal score.

The closest follow-up, PR #1474, attempted to extend the same idea to `mlp.down` by fusing **SwiGLU output + xsums production**. It was closed unmerged. Therefore the general producer-side metadata-fusion pattern is validated, but this specific SwiGLU/down implementation is **negative evidence** and must not be copied blindly.

For P69B13, the right action is:

> inspect the already-measured remaining projection/downstream-tail seams for a standalone auxiliary-data/materialization step whose exact arithmetic can be emitted by an already-required producer, while preserving the producer's launch geometry and the consumer's arithmetic verbatim.

Do not force the exact Layr `xsums` mechanism onto our Q8 path unless our current MLX/oMLX verifier actually has an analogous standalone table/fill.

## 1. Promoted mechanism: residual/RMSNorm producer emits QMV xsums

Source:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1197

Official status:

- PR #1197: **merged**;
- head / merge commit: `0863b06ac16e26e48fc06e97444095b00feb66d4`;
- parent score reported at submission: ~3.71960;
- later public challenge records identify `0863b06` as the ~3.72911 promoted frontier.

### Measured structure

The challenge's affine-4/group-64 wide QMV path uses a precomputed activation chunk-sum table at verifier widths M>=4. Before the promoted change, each eligible QMV launched a separate `xsums` fill kernel.

One verify round was reported to contain 257 wide QMV calls:

| Path | Calls/round |
|---|---:|
| GDN in projection | 48 |
| GDN out projection | 48 |
| full-attention QKV | 16 |
| full-attention out | 16 |
| MLP gate/up | 64 |
| MLP down | 64 |
| lm_head | 1 |

127 of those inputs were already being produced by a fused residual+RMSNorm kernel:

- ~47 GDN entry norms;
- 16 attention QKV entry norms;
- 64 post-attention norms feeding MLP gate/up.

The promoted change made that producer also write the exact chunk-sum table, deleting the 127 standalone fill dispatches.

The submitter measured the old fill at roughly 4-6 us/launch and estimated 508-762 us of removable work in a ~68.4 ms round, before the producer-epilogue cost. The official merge is the important evidence that this style of producer-side sidecar fusion can survive the challenge's hidden exact-token/performance gate.

### Exactness lesson

The first algebraically equivalent attempt was discarded because it recomputed sums with a different reduction expression.

The promoted version instead copied the standalone fill kernel's load and accumulation chain essentially verbatim into the producer epilogue, after the producer had written the exact BF16 activation bytes.

This is directly aligned with MXFORGE's strongest P53/P69 lesson:

> preserve the actual floating-point path, not merely the mathematical formula.

### P69 relevance

P69B11 and P69B12 already exploit the same broader principle from another direction:

- P69B11 bundles QKV + Z projections in one dispatch while retaining their independent arithmetic;
- P69B12 uses otherwise-idle SIMD capacity in that dispatch for the tiny B/A projections.

The Layr result adds a second pattern:

> **producer epilogue computes exact metadata/side work needed by the next projection, deleting an entire standalone dispatch.**

Before P69B13 implementation, inspect whether the measured remaining GDN/projection/downstream tail contains any exact analog:

- input-summary / affine auxiliary table generation;
- activation materialization followed immediately by a summary/gather/copy;
- layout/index side data computed in a standalone kernel after a producer already traverses the same bytes;
- small downstream projection work that can ride an existing producer without changing its critical launch geometry.

## 2. Negative evidence: SwiGLU -> down-projection xsums extension

Source:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1474

Official status:

- PR #1474: **closed, not merged**.

Mechanism:

- replace the ordinary SwiGLU elementwise producer with a custom Metal kernel;
- compute exact `(gate * sigmoid(gate)) * up` output;
- in the same launch, produce the chunk-sum table required by `mlp.down`;
- intended to delete another 64 standalone fills per verify round.

The submitter estimated an optimistic upper bound around +0.48% from the previously measured per-fill payoff.

It did **not** promote.

The stated risk is highly relevant to us: replacing a compiler-generated flat elementwise launch with a custom threadgroup-per-row kernel plus barriers can lose enough occupancy/launch efficiency to erase the saved downstream dispatch.

### P69 rule derived from this rejection

Do not conclude:

> "Fuse SwiGLU with whatever comes next."

Conclude:

> "Fuse downstream side work only when the producer launch geometry can remain at least as good as the incumbent, or when the removed work is large enough to dominate the producer rewrite cost."

This makes small custom producer rewrites less attractive than extending an already-custom/promoted producer epilogue.

## 3. Host-side sidecar handoff simplification: locally positive, officially rejected

Source:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1281

PR #1281 simplified an eight-entry weak-reference + `NSLock` lookup ring into a single serialized pending producer->consumer handoff.

Local paired result reported about:

- ~0.19% decode reduction;
- ~0.22% work-after-first-block reduction;
- exact rows/trajectory preserved.

Official status:

- **closed, not merged**.

Takeaway:

Host graph/bookkeeping costs are measurable once GPU kernels are heavily optimized, but tiny host-path wins remain vulnerable to benchmark noise and hardware transfer. This is a cleanup category, not a first P69B13 target.

## 4. Wide-QMV occupancy work: useful warning, not a direct M=4 port

PRs #1255/#1262 explored reducing rows-per-SIMDgroup from 4 to 2 in the challenge's M=2..9 affine4 wide-QMV kernel.

On M1 Ultra, the author reported:

- ~14.1% aggregate microbenchmark reduction across tested cells after a better estimator;
- large wins at several M>=6 cells;
- ~11% local end-to-end improvement on one setup;
- exact output elements in direct comparison.

However:

- results were strongly width- and shape-dependent;
- some small-width/wide-N cells regressed;
- M1 Ultra -> ranked M5 transfer was uncertain;
- associated ranked submissions did not establish a promoted successor to `0863b06`.

### Relevance to our fixed M=4 Q8 verifier

Do not import its `rows_per_simd=2` setting.

The useful lesson is methodological:

- measure occupancy/parallelism rather than assuming weight-pass minimization is optimal;
- a configuration that rereads more weights can still win if it produces enough independent threadgroups and lowers register pressure;
- width-specific kernel geometry needs same-hardware integrated certification.

Our P69B3 SG2R4/P69B11 geometry is already certified on the actual M1 Max and should not be perturbed without a measured residual pointing there.

## 5. Other challenge mechanisms worth watching, but not P69B13 pivots

### Proposal-only MTP `fc` M=1 QMV specialization

Recent PRs #1384/#1397 specialize the proposal head's M=1 K10240->N5120 affine4 QMV to one SIMDgroup producing eight output rows, removing duplicate activation streaming. Local directional results were large, but the relevant submissions were not established as a new promoted frontier in this audit.

Potential future MTP-head-only lane, not a current target-verifier structural candidate.

### Compiled fixed-shape proposal tail

PR #1250 used `MLX.compile` for a fixed-shape proposal/rerank graph and reported a small (~0.5%) local positive direction. It did not displace the frontier. This is a later host/graph-construction optimization category.

### DFlash2 proposal head

Recent PR #1445 combines a DFlash2 RTN4 proposal head with target-side fused/persistent kernels and reports strong local exact-token integration results. Official ranked outcome was not established as a promoted replacement during this scan.

Treat DFlash2 as a separate future speculation architecture, not as P69 work.

## 6. What the challenge says about our current P69 state

The challenge and P51 independently converge on several conclusions:

1. **Verifier cost, not draft-head cost, is often the dominant lever.**
2. **Dispatch/materialization deletion beats tiny epilogue micro-optimizations when it removes whole graph work.**
3. **Arithmetic order is part of the correctness contract.**
4. **Local kernel wins frequently fail integrated or cross-hardware transfer.**
5. **The best next candidates are structural producer/consumer combinations, not arbitrary kernel rewrites.**

That is almost exactly the evidence pattern from P69B5/P69B6/P69B8-P69B12.

## 7. Concrete P69B13 pre-implementation checklist

Without rerunning P69B7 profiling:

1. Re-read the existing P69B7/P69B10 remaining seam map.
2. For each still-open high-cost projection/downstream-tail seam, identify:
   - producer tensor;
   - immediate consumer;
   - standalone kernels between them;
   - whether producer already traverses the exact bytes needed by the standalone work;
   - whether the standalone work's arithmetic can be copied verbatim as an epilogue;
   - whether the producer's existing launch geometry can remain unchanged.
3. Rank highest any candidate that deletes a whole command buffer/materialization while preserving an already-certified producer kernel.
4. Deprioritize a candidate requiring replacement of a fast compiler-generated elementwise producer with a barrier-heavy custom launch unless projected savings are clearly larger than the rewrite risk.
5. Use the Layr accepted #1197 patch as an implementation-pattern reference only; promotion still requires our actual-weight exactness gates and controlled integrated A/B.

## Bottom line

The fresh external scan does **not** justify abandoning the recorded P69B13 queue.

It does sharpen what to look for:

> **an exact producer-side fusion that deletes downstream auxiliary/materialization work is now the freshest high-confidence structural pattern.**

The accepted Layr xsums fusion is strong positive evidence for that class. The rejected SwiGLU/down extension is equally valuable negative evidence about overengineering the producer itself.
