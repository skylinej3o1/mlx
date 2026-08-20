# MXFORGE benchmark reporting format

Reference inspiration: https://github.com/julianmb/q38rocm

The `q38rocm` project does an unusually good job of presenting inference work as a sequence of understandable tables instead of isolated headline TPS numbers. MXFORGE should use a similarly consistent reporting structure while keeping our stricter paired-certification methodology.

This file is the default reporting template for Qwen3.8, DeepSeek V4, future MoE work, and cross-hardware comparisons.

## 1. Optimization-stage table

Show cumulative whole-stack progress from a fixed baseline. Do not add overlapping percentage wins from isolated microbenchmarks.

| Stage | Context / precision | Plain decode | Effective speculative decode | PP / TTFT | Peak memory | Delta vs baseline | Certification |
|---|---|---:|---:|---:|---:|---:|---|
| Baseline | | | | | | 1.00x | |
| + optimization A | | | | | | | |
| + optimization B | | | | | | | |
| Current champion | | | | | | | |

Notes:

- Report target-only decode separately from effective emitted TPS with MTP/DFlash/DSpark.
- If a stage changes quant, KV precision, or model weights, state that explicitly; it is not a pure runtime comparison anymore.
- Include context length because verifier and attention economics can change materially with context.
- Prefer 10 paired runs for champion certification where practical.

## 2. Workload-specific speculative table

Speculation is content-dependent. Code, structured output, prose, and reasoning should not be collapsed into one number.

| Workload | Plain decode | Speculative decode | Draft mode / depth | Accepted tokens / verify | Acceptance distribution | Speedup |
|---|---:|---:|---|---:|---|---:|
| Code generation | | | | | | |
| Code edit / copy-heavy | | | | | | |
| Structured JSON / tools | | | | | | |
| Technical prose | | | | | | |
| Reasoning / math | | | | | | |

For comparisons between MTP, DFlash2, DSpark, and lookup drafting, replay identical prompts. Do not compare different live-agent windows and attribute all drift to the drafter.

## 3. Context-scaling table

Every champion should publish the curve, not just the shortest prompt.

| Context | Cold PP tok/s | Warm-prefix delta PP | Plain decode tok/s | Effective speculative tok/s | KV mode | Cache memory | Peak memory | Prefix hit rate |
|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 2K | | | | | | | | |
| 8K | | | | | | | | |
| 32K | | | | | | | | |
| 64K | | | | | | | | |
| 96K | | | | | | | | |
| 128K | | | | | | | | |

For Apple agent tests, add cached tokens and newly-prefilled tokens per request. Large logical context should not imply a full cold prefill every turn.

## 4. Hardware / topology comparison table

Use this when comparing M1/M2/M3/M4/M5, single-node vs two-node, TP vs PP, or Apple vs CUDA/ROCm.

| Hardware / topology | Model / quant | Context | PP tok/s | Plain decode | Effective decode | Interconnect | Peak memory / node | Notes |
|---|---|---:|---:|---:|---:|---|---:|---|
| | | | | | | | | |

For distributed runs, also log:

- local compute time
- collective / network time
- idle or pipeline bubble time
- bytes transferred per emitted token
- verifier communication cost for M=2..8
- node-specific memory headroom

## 5. Memory / context budget table

Particularly important for 64 GB Apple machines and the 16 GB RTX 5070 Ti.

| Configuration | Weight residency | KV @ target context | Runtime / workspace | OS / desktop reserve | Remaining headroom | Max validated context |
|---|---:|---:|---:|---:|---:|---:|
| | | | | | | |

A kernel or layout optimization that raises TPS but increases transient prefill memory enough to reduce usable context is not an unconditional win. Report both.

## 6. Quality / fidelity table

Speed is not sufficient when quantization, KV compression, or altered support-model weights are involved.

| Configuration | Weight bpw | KV mode | PPL / KLD | Task score(s) | Tail metric | Output exactness | Notes |
|---|---:|---|---:|---|---:|---|---|
| | | | | | | | |

For lossless speculative decoding, explicitly state that target verification preserves the target model's emitted token sequence. If quantization changed, losslessness applies only relative to that quantized target.

## 7. Agentic time-to-action table

For the product/appliance use case, raw TPS is not the whole objective.

| Scenario | Logical context | Cold-prefill events | Prefix hit rate | PP time | Generation time | Tool time | Compaction time | Total task time | Success |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| | | | | | | | | | |

This is the table that should eventually decide whether an MXFORGE configuration is actually better for coding agents.

## Presentation rules

1. Put the current champion and baseline in every relevant table.
2. Keep externally reported numbers visually separate from MXFORGE-reproduced numbers.
3. Label measured, estimated, and speculative values explicitly.
4. Prefer absolute tok/s and milliseconds plus the ratio; do not publish only percentages.
5. State model hash, quant hash, commit, MLX/runtime version, macOS/driver version, hardware, power mode, prompt set, output length, and context.
6. Preserve failed configurations and regressions in the report; they prevent rediscovery.
7. Use the same table shape across experiments so improvements are visible at a glance.

The goal is the clarity of `q38rocm`'s presentation combined with MXFORGE's paired-run and whole-stack certification discipline.