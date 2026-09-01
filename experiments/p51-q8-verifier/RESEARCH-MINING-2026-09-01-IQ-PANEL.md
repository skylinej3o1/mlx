# Research mining — large-batch quantized-weight panel reuse

Source thread:
https://www.reddit.com/r/LocalLLaMA/comments/1w3n506/avx2_speed_up_large_batch_size_prompt_processing/

This note records the portable optimization mechanism behind the reported AVX2 large-batch prompt-processing work. The useful lesson is not AVX2 specifically; it is a change in representation and reuse strategy when batch width is large enough to amortize quantized-weight decode/repack cost.

These are upstream/community implementation observations, not measurements produced by this repository. Do not convert them into MLX/Metal performance claims without profiling and reproduction.

## Core mechanism

For supported low-bit IQ weight formats, the patch avoids repeatedly decoding the same compact quantized weight rows for every activation/prompt row.

Instead it:

1. decodes a group of **8 consecutive quantized weight rows once**;
2. repacks them into an **8-row interleaved compute panel** (`block_iqp_x8`);
3. stores the decoded signed int8 values plus per-row floating factors, integer sub-block scales, and an optional bias correction in that panel;
4. reuses the panel across multiple Q8_K activation rows through GEMM/GEMV kernels;
5. falls back to the ordinary path below a measured batch-size crossover.

The explicit crossover in the inspected implementation is:

- `GGML_IQP_MIN_BATCH = 8` for ordinary `MUL_MAT`;
- `GGML_IQP_MIN_BATCH_ID = 8` per expert for `MUL_MAT_ID`.

That threshold is as important as the panel itself: the repack/decode has a fixed cost, so B1/small-batch decode should not pay it when there are too few activation rows to amortize it.

## Panel organization

The inspected `block_iqp_x8` representation contains, for eight interleaved weight rows:

- `dfac[8]`: floating super-block factors;
- `bias[8]`: optional VNNI unsigned-activation correction;
- interleaved integer sub-block scales;
- decoded/interleaved signed int8 quant values.

`iqp_decode_panel_8()` performs the decode/repack once for eight source rows. The downstream `iqp_gemm_8x8_q8_K` / `iqp_gemm_tile_4` family then consumes the same panel for multiple activation rows rather than re-decoding the compact IQ storage repeatedly.

Supported IQ formats in the inspected patch include:

- IQ2_XXS
- IQ2_XS
- IQ2_S
- IQ3_XXS
- IQ3_S
- IQ1_S
- IQ1_M
- IQ4_XS

The activation side is converted to Q8_K.

## MoE-specific relevance

The `MUL_MAT_ID` path is particularly interesting for MoE prompt processing.

For one selected expert, the implementation:

1. decodes that expert's weight rows into the 8-row panel once;
2. gathers/scatters the activation rows routed to that expert;
3. processes up to four activation rows at a time against the same panel;
4. writes through a temporary tile because expert outputs are scattered in destination space.

This is a useful general pattern for Flash-Next / MoE work: **route first, group enough rows by expert, then pay weight-unpack/repack cost once per expert tile rather than once per routed token.**

## Why this is portable beyond AVX2

AVX2/VNNI/GFNI are implementation details of the CPU kernel. The architecture-independent idea is:

> When quantized-weight decode cost is material, batch width changes the optimal weight representation. Keep compact storage for residency, but decode/repack a tile once into a compute-friendly panel and reuse it across enough activation rows to amortize the conversion.

A Metal/MLX equivalent would not necessarily look like `block_iqp_x8`. Candidate forms include:

- unpacking/reformatting low-bit expert blocks once per threadgroup/tile into threadgroup or other fast intermediate storage;
- reusing the unpacked panel across multiple prompt rows;
- grouping routed MoE rows by expert so the same expert block is consumed repeatedly before eviction;
- using different kernel paths for B1, MTP-width, and large-prefill geometries rather than forcing one representation on every shape.

This connects directly to the other Sep-1 lesson from QSA TOP_K routing: **shape-specific dispatch matters.** The fastest B1 kernel can be the wrong prefill kernel, and the best compact storage layout can be the wrong compute layout once several rows reuse the same weights.

## Possible relevance to current projects

### Qwen3.8-Flash-Next

High interest for prompt processing / expert-heavy batched work if profiling shows repeated low-bit expert unpack/dequant overhead.

Specific experiment to consider later:

- profile low-bit expert matmul at B=1, 2, 4, 8, 16, 32 and representative prefill ubatches;
- separate compact-weight decode/repack time from dot-product time;
- group rows by expert and measure whether a temporary compute panel amortizes at B>=N;
- find the actual Apple crossover rather than inheriting the CPU patch's threshold of 8.

### PP + MTP / context drafting

Potentially relevant but not automatically a win. MTP/context drafting creates multi-row verifier geometry, which may make panel reuse attractive if quant unpack is repeated per row. However verifier widths around 2–9 rows are exactly near the crossover region, so this must be measured. GPU kernels may already amortize unpack work internally.

### Qwen3.8-27B P69 exact-Q8 verifier

**No immediate campaign change.**

P69 is an exact-Q8 Metal verifier campaign with its own measured seams. Do not redirect P69B13 on the basis of this CPU IQ-panel work. Only revisit the concept if local profiling demonstrates repeated quantized-weight decode/repack overhead across verifier rows and an exact compute-panel representation can preserve the frozen arithmetic/trajectory requirements.

## Qualification rules if ported

Preserve the strongest ideas from the upstream implementation:

1. **Measured crossover gate.** Keep the old path below the batch width where repack pays for itself.
2. **A/B escape hatch.** The inspected implementation exposes `GGML_NO_IQ_PANEL` so the panel path can be disabled without rebuilding.
3. **Representation exactness check.** The debug verification path checks that panel reconstruction reproduces reference dequantization for supported IQ formats.
4. **End-to-end qualification.** A faster panel microbenchmark is insufficient; measure actual prefill / routed-expert / MTP verifier wall time.
5. **Separate B1 from prefill.** Do not allow a large-batch optimization to regress single-token decode.

## Decision

Record as a **future MXFORGE / Flash-Next batching candidate**, not a current P69 optimization.

Priority is conditional on profiling. The seam becomes high priority if low-bit expert/prompt matmuls show a meaningful fraction of time spent repeatedly decoding/repacking the same compact weight blocks across multiple activation rows.

The compact statement to carry forward is:

> **Store compact; compute repacked; amortize by batch; gate by geometry.**
