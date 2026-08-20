# Geodesia-KV: adaptive mixed-precision KV research note

Source: https://github.com/geodesia-ai/geodesia-kv

Status: **promoted research lead; not yet an MXFORGE implementation**.

## Why it matters

Geodesia-KV treats KV precision as a dynamic allocation problem rather than a single model-wide setting. It divides cache state into 64-token blocks and assigns each block a precision level from a monotonic ladder such as `{16, 8, 4, 2, centroid}` using causal attention mass and estimated reconstruction error. Blocks can demote as they become less valuable, but do not promote again, so the design does not require keeping a dense fallback copy resident.

The implementation also includes a fused CUDA attention kernel that consumes heterogeneous packed KV directly and dequantizes inside online-softmax attention. The useful MXFORGE lesson is broader than the exact CUDA codec:

> **KV precision can be a context-, block-, and workload-dependent runtime policy rather than a static global knob.**

This fits the existing MXFORGE adaptive-runtime thesis: target quant, drafter, verification width, cache precision, context policy, topology, and memory residency can be selected together from measured hardware economics.

## Claims to treat cautiously

The project describes itself as retaining all tokens with "no information loss." MXFORGE should interpret this narrowly as **no token-position eviction**. Quantizing KV to 2-bit or a centroid representation is numerically lossy even if a runtime bound is maintained on attention-output error.

The current published evidence is also not directly transferable to our targets:

- validation is on Qwen2.5-3B, Qwen3-8B, and Qwen3-30B-A3B rather than Qwen3.8-27B;
- benchmark contexts are much shorter than our desired long-agent regimes;
- the shipping implementation is CUDA/vLLM, not Metal/MLX;
- Qwen3.8-27B has hybrid GDN/recurrent state, so ordinary attention KV is only part of the long-context state;
- DeepSeek V4 Flash uses MLA-style compressed state rather than ordinary GQA KV, so the existing kernel is not a DS4 drop-in;
- the vLLM integration recommends eager execution for dynamic cache management, which may conflict with graph-capture optimizations that matter for decode speed.

Therefore the source is an architecture and experiment lead, not evidence that MXFORGE will obtain the project's headline memory reduction or preserve identical downstream behavior.

## Qwen3.8-27B experiment path

Do not interrupt the current MTP/verifier work. Once the decode/speculative baseline is stable:

1. **Establish references**
   - Q8 KV quality/default where it fits.
   - Uniform Q6/Q5/Q4 cache controls if supported.
   - Measure memory, decode latency, long-context quality, and prefix behavior.

2. **Instrument block importance**
   - collect attention mass / salience for attention layers;
   - estimate per-block K/V quantization distortion;
   - keep GDN/recurrent state accounted separately rather than pretending it is ordinary KV.

3. **Prototype a monotonic precision ladder**
   - recent / protected blocks: Q8 or higher;
   - warm high-salience history: Q6/Q8;
   - cool history: Q4;
   - cold history: Q2 or another aggressive representation only if quality permits;
   - protect sinks, recent tokens, tool instructions, and other empirically sensitive anchors.

4. **Build a Metal-native mixed-bit attention path**
   - consume packed blocks directly;
   - dequantize inside attention rather than materializing a dense cache;
   - specialize around M1 SIMD/threadgroup behavior;
   - measure graph/dispatch cost as carefully as memory savings.

5. **Integrate with the adaptive scheduler**
   Candidate inputs:
   - current context length;
   - free/wired unified memory;
   - resident KV bits/value distribution;
   - block importance / estimated distortion;
   - workload class;
   - drafter residency and verification width;
   - expected output reserve.

   The scheduler should compress only when the expected memory/context benefit exceeds the latency and quality cost.

6. **Re-certify speculation**
   Any KV representation change can alter target latency and potentially numerical outputs. Re-sweep MTP/DFlash/DSpark/lookup policy and M=2..8 verification after the cache path changes.

## DeepSeek V4 Flash interpretation

Do not port the ordinary mixed-K/V CUDA kernel directly. Instead investigate whether the same **importance-weighted variable-rate principle** can apply to DS4's MLA/compressed cache state.

Possible long-term questions:

- can older MLA latent blocks be stored at lower precision while preserving recent/salient state at higher precision?
- can precision change without forcing full context reconstruction?
- can TP/PP KV migration transform both layout and precision in one pass?
- can cache compression postpone a topology/drafter transition enough to repay its conversion cost?

These belong after the current TP verifier, small-MTP, DSpark, PP, and migration baselines are individually measured.

## Certification requirements

Do not promote a mixed-precision cache based on perplexity or memory savings alone. Report:

- resident bits/value distribution over time;
- actual unified-memory savings and transient peaks;
- decode and verification tok/s at multiple context bands;
- prefill and cache-conversion cost;
- long-code editing correctness;
- multi-needle retrieval;
- instruction retention;
- multi-turn agent state;
- tool-call validity;
- reasoning/coding regression suites;
- tail-sensitive distribution metrics where available;
- prefix-cache continuity;
- any interaction with graph capture / dispatch count.

## Priority

**High-value later branch, below the current MTP-head / reduced-vocabulary drafter / verifier-hot-path work.**

The immediate thing to preserve is the architectural insight: **static uniform KV precision is not necessarily the endpoint.**