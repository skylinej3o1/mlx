# Ling-3.0-flash DSpark — model-specific speculation and heterogeneous sidecar

Status: **CORE / promoted research lead**

This note tracks the newly open-sourced `Ling-3.0-flash-dspark` draft model and its implications for MXFORGE. It is separate from the DeepSeek V4 sidecar work because Ling uses a different hybrid architecture (KDA + gated MLA + sparse MoE) and therefore has different state/rollback requirements during speculative verification.

## Primary announcement

User-supplied source:

- https://x.com/AntLingAGI/status/2090847436755648939

Ant Ling reports that `Ling-3.0-flash-dspark` is a DSpark draft model trained specifically for `Ling-3.0-flash`. Their announcement reports, on **4 NVIDIA Blackwell GPUs at batch 1**, across **1,000 requests**:

- **1,120 tok/s**
- **0.78 ms mean TPOT**
- **9.95 accept length**

Treat these as **vendor-reported datacenter results**, not a transferable MXFORGE speed prediction. The important signal is that a high-acceptance, model-specific DSpark now exists as an open checkpoint.

Primary checkpoint pointer reported by the llama.cpp integration:

- https://huggingface.co/inclusionAI/Ling-3.0-flash-dspark

The checkpoint page was too fresh to inspect reliably through the current web index at intake time. Do not infer its exact parameter count, VRAM footprint, precision, or target-component borrowing until the model card/files are inspected directly.

## Target model facts

Official `Ling-3.0-flash` materials describe a **124B-total / 5.1B-active** hybrid-linear MoE:

- 42 transformer layers
- 35 KDA + 7 gated MLA layers (5:1 pattern)
- 512 routed experts + 1 shared expert
- 8 routed experts active per token
- hidden size 2,560
- expert intermediate size 768
- vocabulary 157,184
- context training schedule up to 256K

The public target config also contains MTP-related fields, but current Apple conversion/runtime packages differ in which auxiliary speculation tensors they retain. Do not assume the existing MLX target conversion is already DSpark-ready.

## llama.cpp support — merged 2026-08-22

Primary implementation:

- https://github.com/ggml-org/llama.cpp/pull/27508

PR #27508, `model : support DSpark for bailingmoe3`, was merged on 2026-08-22. Two details matter for MXFORGE:

1. it adds DSpark speculative decoding for the Ling/BailingMoE3 architecture;
2. it explicitly adds **partial rollback for BailingMoE3 recurrent state**.

The second point is an important architectural lesson. Ling's KDA/recurrent state cannot be treated exactly like ordinary attention KV during rejected speculative branches. Any MLX/Metal port must make speculative commit/rollback semantics explicit and certify state restoration, not merely token acceptance.

The merged llama.cpp path uses a separate draft model and supports commands of the form:

```text
--spec-type draft-dspark
--spec-draft-model <Ling-3.0-flash-DSpark.gguf>
--spec-draft-n-max 8
```

The conversion path also requires the target model directory while converting the DSpark checkpoint, another signal that target/drafter packaging dependencies should be inspected before assuming a fully self-contained remote sidecar.

## DGX Spark evidence from the merged PR

The PR includes an 880-request `speed_bench.py` comparison on a single NVIDIA DGX Spark.

### Overall

| Mode | Decode | Mean latency | Acceptance |
|---|---:|---:|---:|
| target only | 44.20 tok/s | 15.364 s | n/a |
| DSpark | **55.73 tok/s** | **12.817 s** | 0.3895 |

That is about **+26.1% decode throughput overall** in this workload mix.

### Workload dependence

Selected categories:

| Workload | Target only | DSpark | Approx gain | DSpark acceptance |
|---|---:|---:|---:|---:|
| coding | 43.80 | **73.71** | **+68.3%** | 0.5773 |
| RAG | 44.58 | **65.94** | **+47.9%** | 0.4830 |
| multilingual | 43.68 | **65.95** | **+51.0%** | 0.4944 |
| math | 43.96 | **56.83** | **+29.3%** | 0.4241 |
| reasoning | 44.62 | **51.30** | **+15.0%** | 0.3636 |
| writing | 44.39 | **49.14** | **+10.7%** | 0.3248 |
| roleplay | 44.28 | **48.69** | **+10.0%** | 0.3415 |

This is unusually clean evidence for the **adaptive speculation** thesis: one fixed DSpark policy can be excellent for coding/RAG while much less valuable for prose/roleplay. The scheduler should consume recent acceptance and workload class rather than force DSpark globally.

Do not compare the DGX Spark numbers directly with Ant Ling's 4-Blackwell 1,120 tok/s headline. They are different hardware, runtime, precision/topology and benchmark setups.

## Why this matters to the existing MXFORGE hardware

Ling is particularly interesting for the user's heterogeneous fleet because it is a sparse ~124B model rather than a dense 27B model.

Current community Apple target conversions already demonstrate capacity-feasible checkpoints such as:

- stock-ish MLX 4-bit: ~65.22 GiB weights
- oQ4: ~66.63 GiB weights
- oQ5: ~80.67 GiB weights
- oQ2: ~38.73 GiB weights

These are community conversions and must be quality/performance-certified independently. More importantly, current conversion notes explicitly say their ordinary causal-generation adapters omit or do not claim DSpark support.

For **2 x M1 Max 64GB**, that creates a plausible future target configuration:

```text
M1 Max #1 ----\
                +-- Ling-3.0-flash target (distributed) + state + verifier
M1 Max #2 ----/
        ^
        | minimal feature / candidate protocol
        v
RTX 5070 Ti 16GB
        +-- official Ling-3.0-flash-dspark, if its final residency fits
```

This is conceptually similar to the DS4 ThriftOps sidecar, but should be treated as a separate experiment because Ling's KDA recurrent state and BailingMoE3 rollback semantics differ from DeepSeek's target state.

### What is plausible now

- two Macs have ample aggregate capacity for a materially higher-quality Ling target than a single 64GB Mac;
- the 5070 can potentially make the model-specific drafter cheap and keep drafter residency off the Macs;
- coding is exactly the category where the merged llama.cpp benchmark reports the largest DSpark gain;
- Ling's low active parameter count means a large-MoE target may be a better fit for bandwidth-constrained hardware than a dense model of similar total weight size.

### What is **not** yet established

- that the official Ling DSpark checkpoint fits comfortably in 16GB VRAM;
- that it is self-contained enough for a remote 5070 sidecar without duplicating target components;
- that the required target feature packet is as small/simple as DS4's;
- that distributed M1 verification remains cheap enough at useful draft widths;
- that current MLX BailingMoE3 kernels support correct speculative recurrent-state rollback;
- that the community Apple quants preserve enough target quality for the intended agent workload.

## First MXFORGE experiment ladder

1. **Inspect the official DSpark checkpoint** — tensors, size, precision, target dependencies, conditioning features.
2. **Reproduce llama.cpp on a CUDA control** — target only vs DSpark, especially coding, using identical prompts.
3. **Measure draft-side residency on the 5070 Ti** — determine whether the official checkpoint fits with adequate workspace.
4. **Profile Ling target-only on Apple** — single-Mac capacity modes and two-Mac distributed target options; separate quant quality from topology performance.
5. **Specify recurrent-state rollback semantics** for KDA in MLX/Metal before enabling speculation.
6. **Build small-M verifier cost curves** on the distributed target; do not assume n-max=8 is optimal over Thunderbolt.
7. **Prototype 5070 sidecar only if the verifier economics work.**
8. **Add adaptive enable/disable policy** by workload/context/recent acceptance.
9. Later, test parent-conditioned/Micro-PCTree ideas only after linear DSpark is correct and the extra verification-node cost is known.

## Metrics

For every Ling speculative run log:

- target-only decode tok/s
- DSpark effective target-verified tok/s
- draft latency
- acceptance rate and accepted-length distribution
- rejection depth
- target verification latency by M
- KDA recurrent-state rollback/commit cost
- distributed wire/collective time
- target memory per Mac
- 5070 drafter VRAM
- context length and output reserve
- workload class
- correctness / replay equivalence

Primary optimization target remains:

> **minimum whole-system milliseconds per committed target-verified token.**

The new Ling release strengthens the broader MXFORGE thesis: model-specific drafters are becoming a normal part of open inference stacks, and the winning deployment can assign target capacity, drafting compute, and state verification to different pieces of hardware rather than requiring one monolithic box.