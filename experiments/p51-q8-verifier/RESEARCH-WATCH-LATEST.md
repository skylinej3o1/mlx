# Project 51 primary-lane research watch — 2026-09-23 06:19 ET

**Freshness boundary checked:** prior hard boundary approximately **2026-09-23 07:55 UTC**. This pass covers substantive evidence through the user cutoff **2026-09-23 10:19:31 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

The strongest fresh evidence is implementation-side rather than a new target-topology receipt:

1. oMLX opened a new MCDMA pipeline-transport series that moves stage activations, sampled tokens and optionally remote-prefill KV outside the ordinary ring, but it has **not** yet been validated on real ConnectX hardware or against a live vLLM producer.
2. vLLM opened a Qwen4Exp PLE fix that stops decode/MTP preprocessing from scanning the configured maximum token workspace on every step; outputs are designed to be bit-identical, but end-to-end ROCm numbers are still pending.
3. SGLang opened two useful Qwen3.8-27B DFlash2 correctness PRs proving that quantized target heads and quantized drafts can retain essentially identical acceptance when loader/module-name contracts are correct.
4. A newly surfaced oMLX M1-Max result shows 5.8-6.2% decode improvement on Qwen3.5/3.6 35B-A3B by automatically engaging the existing fused FP16 GDN prework path. This is exact-chip / same-GDN-family evidence, **not Flash-Next throughput evidence**.

No new exact 2x M1 Max / TB4 Flash-Next decode receipt appeared. No new DASLab / GSQ-RCO xhigh behavioral result appeared. Keep:

- production quant search: **~3.0 / 3.2 / 3.4 / 3.6**, center hypothesis **~3.4-3.5**, likely source-like xhigh region **~3.3-3.6 average transformer BPW**;
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**;
- planning confidence for >=40 TG: **~70%**;
- 50/500 remains stretch/headline territory.

---

## NEW — oMLX #3869 / #3870: direct stage-edge transport and remote prefill plumbing

Sources:
- https://github.com/jundot/omlx/pull/3869
- https://github.com/jundot/omlx/pull/3870

#3869 was created **2026-09-23 08:15 UTC**. It adds an MCDMA-backed stage edge for Mac<->CUDA pipeline deployments. The receiver verifies the link before launch, all ranks vote on whether the edge is usable, and a failed link falls back to the ordinary MLX ring. Integration tests verify bit-exact activation transfer, shape/dtype checks, and failure-on-link-drop rather than hanging.

#3870 was created **2026-09-23 10:11 UTC** and generalizes the design:

- every pipeline edge can independently use MCDMA;
- sampled tokens can ride the next activation request, removing the ordinary ring all-sum from the steady decode step when all edges are live;
- long prompts can optionally be remotely prefilled by a vLLM server and have only the missing KV pages handed back;
- large received frames can be copied into MLX from Metal-visible buffers, avoiding an extra CPU copy.

Important qualification: the PR explicitly says it has **not yet been run on ConnectX hardware or inside live vLLM**. Current evidence is unit/integration/stand-in transport correctness, not a production throughput receipt.

### P51 consequence

This strongly reinforces our **stage-boundary-activations-only** communication design, but receives **zero numeric TG/PP forecast credit** until hardware measurements exist.

Durable transport rules:

- probe every stage edge independently;
- make transport choice per edge, not globally;
- fail closed / fall back cleanly on link loss;
- sampled-token/control traffic should piggyback on already-required pipeline messages where possible;
- remote prefill must prove cache-layout identity before injecting state;
- do not infer PP speedup from transport microbenchmarks alone.

For dual M1 / TB4 specifically, MCDMA itself is not our transport. The transferable idea is the **message contract and edge ownership**, not the RDMA mechanism.

---

## NEW — vLLM #58325: Qwen4Exp PLE preprocessing should scale with actual tokens, not configured maximum

Source:
https://github.com/vllm-project/vllm/pull/58325

Created **2026-09-23 10:14 UTC**.

On the AMD Qwen4Exp path, the persistent PLE workspace is sized to
`[max_num_reqs, max_num_batched_tokens]`. Before this PR, n-gram shift / EOS-segment / hash preprocessing ran over the full configured second dimension even when a decode step contained only one token per request or a small MTP verify width.

Example from the PR: with `max_num_batched_tokens=16384`, an ordinary decode step still preprocesses 16,384 columns.

The fix slices the workspace to `[:num_reqs, :num_tokens]`. The author argues downstream indexes are already bounded by `num_tokens`, so outputs should remain bit-identical and only never-read columns stop being touched.

### Evidence level

- unit-test plan: bit-identical sliced vs full-width reference across ragged MTP, graph padding and single-request shapes;
- persistent memory footprint unchanged;
- **ROCm E2E Flash-Next throughput and accuracy measurements are still TODO**.

### P51 consequence

Add a durable rule:

> every PLE/QSA/indexer preprocessing loop must be bounded by **actual live rows/tokens**, not the configured maximum workspace or context.

This belongs in the verifier profile because the error gets especially wasteful for B1 decode and small MTP widths.

No target credit until end-to-end measurements land.

---

## NEW — SGLang #40883: packed target lm_head works with NEXTN / DFlash2 when the quant method is used correctly

Source:
https://github.com/sgl-project/sglang/pull/40883

Created **2026-09-23 08:38 UTC**.

The target can serve a pack-quantized `lm_head` through its quant method, but the speculative paths previously assumed `.weight` exists and refused to start.

Qwen3.8-27B validation, RTX 6000 Ada, TP1:

| target head | spec path | result | GSM8K/200 | mean accept length |
|---|---|---|---:|---:|
| BF16 | NEXTN | serves | 0.970 | 3.629 |
| BF16 | DFlash2 | serves | 0.970 | 6.035 |
| W8A16 packed | NEXTN | old main fails | - | - |
| W8A16 packed | DFlash2 | old main fails | - | - |
| W8A16 packed | NEXTN, PR | serves | 0.965 | 3.629 |
| W8A16 packed | DFlash2, PR | serves | 0.970 | 6.035 |

### P51 consequence

The output/head should remain a protected tensor class in the quality-first allocator, but **protected does not necessarily mean BF16 forever**. A Q8/W8-style head can be a legitimate experimental arm if paired source-vs-quant xhigh/agent tests remain source-like and MTP acceptance is unchanged.

Do not change the current production precision policy yet; this is 27B/Ada evidence, not Flash/M1 evidence.

---

## NEW — SGLang #40884: quantized DFlash2 draft can preserve acceptance if module-name / tensor-loader contracts are correct

Source:
https://github.com/sgl-project/sglang/pull/40884

Created **2026-09-23 08:38 UTC**.

The important bug was silent: draft modules were constructed under names that did not match checkpoint quantization rules. Ignore patterns for q/k/v therefore failed, fused layers were built quantized, BF16 checkpoint tensors were silently dropped, and the draft could reach warmup with effectively invalid/uninitialized state.

The PR makes the draft build under checkpoint names and **refuses tensors that the instantiated module cannot actually consume** rather than silently discarding them.

Qwen3.8-27B, RTX 6000 Ada:

| draft | result | GSM8K/200 | accept length |
|---|---|---:|---:|
| BF16 DFlash2, main | serves | 0.970 | 6.035 |
| BF16 DFlash2, PR | serves | 0.970 | 6.035 |
| W8A16 draft, main | device-side assert in warmup | - | - |
| W8A16 draft, PR | serves | 0.970 | **6.031** |

The quantized draft keeps q/k/v, selector, convolution kernels and norms at higher precision in the published recipe.

### P51 consequence

Strengthen the Apple7 DFlash2 gate:

1. verify every draft tensor is consumed by the intended module;
2. reject unexpected dense-vs-packed / packed-vs-dense mismatches;
3. record protected draft submodules explicitly;
4. only after load-identity passes should finite-hidden/logit checks and acceptance tests be trusted.

The existing M1 `w4a32` finite-state rule remains valid; this is an additional **loader identity** gate.

---

## RECOVERED OLDER EVIDENCE — oMLX #3853: exact M1 Max FP16 GDN decode fusion

Source:
https://github.com/jundot/omlx/pull/3853

The PR was created before the prior hard boundary (2026-09-22 20:43 UTC), so this is classified as **RECOVERED OLDER EVIDENCE**, not fresh creation. It was updated again inside this pass.

Hardware:
- Apple M1 Max 64 GB
- MLX 0.32.2
- Qwen3.5/3.6 35B-A3B
- B1/T1 greedy decode
- thinking/speculation off
- FP16 convolution/input, FP32 recurrent state

Whole-server A/B:

| mixed conversion | main TG | fused TG | gain |
|---|---:|---:|---:|
| 4-bit default | 73.79 | **78.33** | ~6.2% |
| 5-bit default | 59.75 | **63.32** | ~6.0% |
| 6-bit default | 57.97 | **61.35** | ~5.8% |

Complete 256-token response time falls about 4.8-5.9%.

Validation includes 2,268 real-weight numerical cases and 270 synthetic server rows; no new test failures relative to the same main baseline.

### Qualification

This is **exact M1 Max evidence**, but it is **not Flash-Next** and it does not cover speculative verification. Qwen4/Flash uses a separate BF16/normalization route.

### P51 consequence

This is useful exact-chip evidence that fused GDN prework remains worth pursuing on Apple7 and that a ~6% B1 gain is physically available on a nearby GDN architecture when the route is shape/precision-matched.

It does **not** justify increasing the 40-TG probability.

---

## NEW — llama.cpp #29305: cache source logits once, compare conversion candidates later

Source:
https://github.com/ggml-org/llama.cpp/pull/29305

Created **2026-09-23 10:07 UTC**.

The PR adds a conversion workflow that lets a source-model token/logit run be saved once and later reused to verify converted candidates, avoiding repeated execution of the huge reference model.

### P51 consequence

Adopt the concept in the quant-search harness:

- freeze source tokens/logits for a controlled prompt suite;
- reuse the source artifact across 3.0/3.2/3.4/3.6 candidate conversions;
- still run behavioral xhigh/agent evaluation separately.

This reduces quant-search cost, but **logit parity remains an allocator/correctness signal, not AA40 certification**.

---

## NEW / NEGATIVE TRANSFER — llama.cpp #29298 sparse-FA prefill changes DS4, not Qwen4Exp in the submitted benchmark

Source:
https://github.com/ggml-org/llama.cpp/pull/29298

Created **2026-09-23 08:03 UTC**.

DGX Spark, long-context pp2048:

DeepSeek-V4:
- @65K depth: **238.24 -> 293.35 PP (+23%)**
- @131K depth: **172.75 -> 244.46 PP (+42%)**
- TG essentially unchanged.

Qwen4Exp A3B IQ1_S:
- 0K / 16K / 32K / 65K PP and TG are essentially unchanged (~1.00x).

### P51 consequence

Do not transfer sparse-attention kernel gains across hybrid model families merely because both expose sparse attention. The selection geometry / batch gate that helps DSV4 prefill is not automatically useful to Qwen4Exp.

This is a useful negative result and supports model-specific kernel dispatch.

---

## Checked with no qualifying fresh target evidence

Between the hard boundary and cutoff:

- **MTPLX:** no new commit/PR/issue.
- **EXL3:** no new commit/PR/issue.
- **PonyExl3:** no new commit/PR/issue.
- **official Qwen3.8 repo:** no new commit/PR/issue.
- **MiaAI-Lab dual-DGX-Spark Flash repo:** no new commit/PR/issue.
- **flashnext-hybrid:** no new commit/PR/issue.
- **mlx-serve:** no new commit/PR/issue.
- **DS4:** no qualifying new item.
- no new exact **2x M1 Max/TB4 Flash-Next** TG or cold-PP receipt.
- no new **DASLab Flash xhigh quality** result.
- no new **5070 Ti** result strong enough to move its canonical target.

## Target / confidence impact

Unchanged:

- Flash-Next xhigh production quant: search ~3.0-3.6; likely source-like region ~3.3-3.6 (hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- **~70%** planning confidence for >=40 TG.
- single-M1 27B: **25 TG**.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-23 10:19:31 UTC**
