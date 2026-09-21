# Project 51 focused DASLab / Flash-Next quant pass — 2026-09-21 08:18 ET

**Freshness boundary checked:** current branch began this pass at **2026-09-21 12:03:30 UTC**. Focused search ran through the user's cutoff **2026-09-21 12:18:58 UTC**.

## Decision

**No numeric TG/PP or quality-confidence change.**

The DASLab Flash-Next release is stronger evidence for Project 51's **heterogeneous tensor-role strategy and optimizer design**, but it is **not** evidence that a 3.00-bpw Flash build satisfies P51's >=38 AA-class production floor.

The most important correction to the earlier positive read is that the released GSQ-RCO Flash quant is **calibrated/evaluated primarily at xhigh reasoning effort**, and DASLab now explicitly acknowledges substantial degradation can occur at **medium reasoning effort**. That makes the release a powerful allocation prior rather than a production-quality certificate.

## Direct ISTA-DASLab Flash-Next release

Source: https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF

Flash-Next is treated as a 512-expert MoE across 48 layers, with 10 experts active per token. DASLab says **95% of searchable weight mass lives in the routed experts**. Their RCO search covers 352 groups: 304 dense/control tensors plus 48 fused routed-expert matrices, one per layer.

The search uses separate candidate ladders for the huge routed-expert bank and the dense/control path.

### Released operating points

| variant | transformer bpw | resident weight shard | fixed PLE/ngram shard | total |
|---|---:|---:|---:|---:|
| Q2_0 | 2.40 | 37.6 GB | 28.8 GB IQ4_NL | 66.4 GB |
| IQ2_XS | 2.50 | 39.2 GB | 28.8 GB IQ4_NL | 68.0 GB |
| IQ3_XXS | **3.00** | **47.0 GB** | **28.8 GB IQ4_NL** | **75.8 GB** |

The PLE/ngram table is 51.2B parameters and is **excluded from the RCO search**. All three evaluated builds use the same IQ4_NL table at about 4.5 bpw.

Only shard 1 is intended to be resident; shard 2 can stay mmap-backed on SSD.

## Quality evidence: impressive, but narrower than P51 needs

Reported xhigh-oriented results:

| build | AIME25 | GPQA-D | LiveCodeBench v6 | task avg |
|---|---:|---:|---:|---:|
| BF16 | 100.00 | 91.92 | 87.43 | 93.12 |
| GSQ-RCO IQ3_XXS 3.00 bpw | **100.00** | **91.41** | **86.29** | **92.57** |

That is **99.4% of BF16 task average**.

Their five-task zero-shot average is also effectively at parity: 77.23 for IQ3_XXS versus 76.94 BF16.

This is strong evidence that an aggressively heterogeneous Flash quant can preserve selected reasoning/coding benchmarks. It is **not AA**, not agent/tool-state evaluation, and not a deep-context recurrent/QSA certification.

## Critical caveat: reasoning-effort dependence

The current model card explicitly says the quants are primarily optimized for **xhigh reasoning effort** and warns that lower reasoning effort can show larger quantization-induced degradation.

A detailed community report using **medium** reasoning effort observed substantial behavior degradation versus the official Alibaba service, including poor performance on a Three.js voxel coding task. DASLab's maintainer responded that this makes sense because optimization used xhigh reasoning traces and confirmed that medium can degrade noticeably more. A second user independently reported significant medium-effort degradation. DASLab says future releases should maintain acceptable medium-mode behavior.

Sources:
- https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/discussions/14
- https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/discussions/18

### P51 consequence

**Reasoning effort becomes part of quant identity/certification.**

P51 must certify at least:
- medium;
- xhigh;
- thinking-off/non-reasoning where relevant;
- long agentic/tool loops where token-budget economics matter.

A quant that looks source-equivalent only after spending 20-60K reasoning tokens does not automatically satisfy our always-ready coding-agent objective.

## Exact IQ3_XXS tensor-allocation structure

Source allocation commit:
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/commit/fb6d8664256ad762f679204ebd14ab6d907fc82d

The released 3.00-bpw first shard contains 1,223 tensors with this type histogram:

- BF16: 484
- F32: 292
- Q6_K: 71
- IQ4_XS: 67
- IQ4_NL: 58
- Q4_K: 45
- Q2_0: 38
- IQ3_S: 82
- IQ3_XXS: 12
- IQ2_S: 20
- IQ2_XS: 20
- IQ2_XXS: 18
- Q5_K: 15
- F16: 1

The role pattern is much more important than the literal GGUF types:

- output head: Q5_K;
- hyperconnection projection/injection tensors: **BF16**;
- HC norms: **F32**;
- recurrent/SSM scalars, conv state and norms: commonly **F32/BF16**;
- QSA indexer K/Q projections: **BF16**, indexer norms F32;
- full-attention projections: commonly Q4-Q6 class;
- shared experts: generally materially higher precision than routed experts;
- routed gate/up expert mass: frequently ~IQ2-class;
- routed expert down matrices: commonly Q2_0 / IQ4_NL because the 640-row shape prevents many 256-element K/I formats.

This independently validates the P51 protected-island thesis: spend precision on HC/recurrent/QSA/control paths and harvest bandwidth from the giant routed expert bank.

## Format cost matters as much as bits

DASLab's own 55-prompt llama.cpp performance panel gives an unusually useful warning:

| build | prompt t/s | decode t/s | avg latency |
|---|---:|---:|---:|
| Q2_0 2.40 bpw | **367.49** | **93.79** | **6.70 s** |
| IQ2_XS 2.50 bpw | 108.19 | 70.30 | 12.68 s |

The files differ by only 1.6 GB. DASLab attributes the large speed difference to the quantization formats: IQ-style lookup-table decode costs can dominate, while simple Q2_0 maps better onto the runtime kernels.

These are **not M1 numbers**, and the card does not provide a transferable Apple hardware denominator.

### P51 consequence

Never optimize BPW in isolation.

Our allocator's cost term should be measured:
- M1 microseconds/token by tensor role + shape + candidate format;
- hot bytes actually fetched;
- verifier/MTP multi-row kernel cost;
- prefill cost;
- compile/materialization cost.

A 3.0-bpw allocation using slow low-bit formats can lose to a 4.x-bpw allocation with much better M1 kernels.

## MTP status

At this cutoff, the official ISTA-DASLab Flash-Next repo does **not** ship a dedicated MTP-integrated variant or report MTP acceptance.

This contrasts with DASLab's 27B GSQ-RCO release, where official `-mtp` builds exist and include the MTP head directly.

Community users have attached external Flash MTP heads/sidecars, but that does not certify the DASLab Flash allocation's target/draft agreement.

### P51 consequence

Treat target quant and MTP quant as separate identities.

The 99.4% task-average result says **nothing directly about**:
- MTP acceptance;
- acceptance by depth at 128K;
- tokens/cycle;
- target/draft disagreement;
- rollback/recurrent-state behavior.

P51 must optimize the MTP head independently and include acceptance loss in the allocation objective.

## PLE/ngram interpretation

DASLab fixes the 51.2B PLE/ngram table at IQ4_NL for all released variants and reports good benchmark behavior.

This does **not** overrule our PLE warning.

Why:
- the published quality panel is not a 128K MTP acceptance study;
- reasoning tasks do not isolate accumulated long-context PLE error;
- separate community evidence has shown a possible Q8-vs-IQ4_NL deep-context MTP reversal.

Therefore Project 51 should keep **Q8 PLE as the quality-first baseline** and A/B source/Q8/Q6/Q4 through 8K/32K/64K/128K.

## Independent 3.5-bpw reproduction

Source: https://huggingface.co/pfeifferj/Qwen3.8-Flash-Next-GSQ-RCO-GGUF

This is **not an ISTA-DASLab release**. It is an independent community reproduction using GSQ/RCO at a 3.5-bit target.

Main weights are 47.94 GB; the author provides either:
- 103.68 GB BF16 embedding/ngram shard, or
- 29.49 GB Q4_0 n-gram + Q8 token-embedding shard.

On a 2,000-question no-reasoning MMLU-Pro subset:
- GSQ-RCO 3.5-bit: 58.25%
- reconstructed BF16 reference: 55.40%

PPL was 3.1058 vs 3.0533 BF16; IFEval strict was tied 13/16, completed-correct 12/16 vs 13/16 due one truncated quant response; GSM8K was 8/8 both.

This is useful independent evidence that a higher-budget heterogeneous Flash allocation is viable, but it remains a narrow evaluation and does not certify AA/agentic quality.

## Project 51 plan update

### What changes

1. **GSQ/RCO becomes a first-class allocator template, not merely a research curiosity.**
   Build a candidate database per tensor/role, then solve a budgeted assignment problem rather than hand-selecting one global BPW.

2. **The giant routed-expert bank is the primary compression target.**
   DASLab says 95% of searchable weight mass is there. We should preserve expensive precision on control/state tensors and spend aggressive bits almost entirely on routed expert matrices first.

3. **M1 latency enters the optimizer directly.**
   Replace DASLab's pure size budget with a P51 objective/constraint that includes measured Apple cost:
   `quality loss + MTP acceptance loss + long-context/state loss`
   subject to or traded against
   `M1 us/token + hot bytes + resident bytes`.

4. **Do not literally port IQ3_XXS GGUF types into MLX.**
   The allocation pattern is the signal. Candidate formats should be whatever MLX/M1 executes efficiently.

5. **Keep the conservative production start, widen experimental arms.**
   Production search still begins around **4.6-4.9 hot-trunk effective BPW** / MTPLX-Optimized-class protection.
   Add structured **~4.3, ~4.0, ~3.5 and ~3.0** experimental allocations where M1 kernels are efficient.
   Promote only if they pass the >=38-class behavior gate.

6. **Add reasoning-effort robustness to certification.**
   Medium and xhigh must both be first-class rows. DASLab's result proves that calibration-distribution mismatch can hide inside an excellent headline benchmark.

7. **Keep PLE and MTP outside the trunk BPW number.**
   PLE precision and MTP precision remain separately optimized/certified.

### What does not change

- >=38 AA-class production floor;
- 39-40 preferred;
- 40 TG @ ~128K headline;
- 400 genuinely cold PP headline;
- current ~65% confidence for >=40 TG and ~70% for >=400 cold PP.

Net: DASLab raises confidence that **there exists a much better allocation frontier than flat Q4/Q5**, while the medium-effort failure prevents us from converting that into confidence that their 3.00-bpw model itself meets P51's quality floor.

## New hard boundary

**2026-09-21 12:18:58 UTC**
