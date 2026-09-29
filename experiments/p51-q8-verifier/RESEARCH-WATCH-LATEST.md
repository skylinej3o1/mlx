# Project 51 primary-lane research watch — 2026-09-29 06:01 ET

**Freshness boundary entering this pass:** **2026-09-29 06:21:54 UTC**.  
**User cutoff:** **2026-09-29 10:01:02 UTC**.

## Decision

**Durable STATE + TARGETS update.**

This pass makes two planning changes:
1. add **Swift 1.5 Flash-Next** as a first-class alternate checkpoint lane measured by effective solved-task throughput, not physical TG;
2. keep the Strata IQ3_S ~32K cold-PP target at **1,200 PP** but raise its planning confidence **~80% -> ~90%** after a direct weaker-card RTX 5070 12-GB receipt clears that level.

Canonical physical targets otherwise remain unchanged:
- dual-M1 Flash-Next: **40 TG sustained @ genuine ~128K / 400 cold PP / ~70% >=40 TG**;
- single-M1 dense27B: **25 TG / ~110 PP**;
- RTX 5070 Ti dense CUDA-v2 TG/PP ladder unchanged;
- Strata IQ3_XXS and long-context IQ3_S centers unchanged;
- IQ3_S AA>=40 planning prior unchanged at **~80%**.

## Strict-window findings

### NEW — Strata 0.1.22 prompt path materially raises PP

Release:
https://github.com/Niko1221/Strata/commit/6a772da1bd667e71a295a8288b149034c417ad11  
Timestamp: **2026-09-29 09:04:51 UTC**.

Key measured constituent changes on the RTX 5070 12-GB calibration class:

#### IQ3_S 32K — asynchronous expert issuer

Source:
https://github.com/Niko1221/Strata/commit/cf68b004c25f3ec60997d780422ce92e0e959f23  
Timestamp: **06:41:08 UTC**.

- IQ3_S 32K prompt: **1,143 -> 1,213 PP**.
- Unpinned-expert copy wait falls **15.2% -> 7.5%**.
- 20K residual dumps / continuations remain byte-identical to 0.1.21.
- The commit reports roughly **+16% prompt TG** for IQ3_S / IQ3_XXS in the broader Phase-C path.

This is the decisive target-calibration receipt: a weaker RTX 5070 12 GB physically clears the P51 user's RTX 5070 Ti **1,200-PP @32K IQ3_S** target.

#### Q2_0 32K — tensor-core QSA prompt attention

Source:
https://github.com/Niko1221/Strata/commit/dce4598fdf79779e2437b4071195001fe5524705  
Timestamp: **07:48:42 UTC**.

- QSA prompt-attention time: **5,216 -> 1,318 ms**.
- 32K prompt: **1,386 -> 1,646 PP (+18.8%)**.
- Synthetic parity against FP64: relative error **~3.2e-6** versus **~2.5e-6** for the old FP32 kernel.
- Needles 8K / 16K / 32K × five depths: **15/15** under both paths.

The path uses FP16 MMA with FP32 accumulation and is intentionally **not bitwise**. The model can amplify tiny summation-order changes even when the kernel error remains FP32-level.

P51 rule:
- this is a prompt-only approximate/numerical lane;
- it does not alter exact verifier certification;
- require full-state/logit/trajectory gates before using an approximate prompt kernel as a source-equivalent production path.

#### Q2_0 128K — combined branch

Source:
https://github.com/Niko1221/Strata/commit/e0fb57d00dbe6277a47d19d5b99a6af3510b7445  
Timestamp: **08:33:39 UTC**.

- 0.1.21: **1,144 PP**.
- combined branch: **1,596 PP (+39.5%)**.
- TTFT: **115.7 -> 83.4 s**.
- KV staging: **1.331 s of 81.3 s (~1.6%)**.

This shows substantial common prompt-path headroom at long context, but it is Q2_0. Do not substitute it numerically for IQ3_S or IQ3_XXS.

#### Other exact prompt-path work

- GDN recurrence split over independent value columns:
  https://github.com/Niko1221/Strata/commit/66f4341e6c50c5436037e4a1bc47f5ff9fb2cd47
  - Q2_0 32K GDN **5,118 -> 4,264 ms**;
  - prompt **1,258 -> 1,308 PP**;
  - 4K/20K continuation byte-identical.

- Prompt MTP grouping removes host synchronization per draft group:
  https://github.com/Niko1221/Strata/commit/f0bbe978ec4fab037dda7cb7288ff8fcd604025b
  - draft-layer share **1,091 -> 905 ms** on Q2_0 32K.

- Lent expert-cache refill batches copies and waits once:
  https://github.com/Niko1221/Strata/commit/581765a7c2abb6c2e70cabf9f8035117413d694a
  - 1,782 slots on RTX 5070: **162 -> 96 ms**;
  - 4K/32K outputs identical.

### NEW — Strata decode-regression scare does not reproduce

Issue:
https://github.com/Niko1221/Strata/issues/119

A user reported 0.1.13 roughly 50% faster than 0.1.21. The maintainer ran both released engines on the same RTX 5070 / Q2_0 / same config:

- 0.1.13: **73.1 / 76.2 TG**
- 0.1.21: **73.8 / 74.3 TG**

The engine-level regression was not reproduced. First-request expert-cache adaptation and text-dependent speculative acceptance can move observed TG substantially.

P51 interpretation:
- 0.1.22 is prompt-side progress, not a reason to reset the existing decode targets.

### NEW — llama.cpp Metal FWHT optimization

Source:
https://github.com/ggml-org/llama.cpp/commit/18bbc46b4697e8623e6f0a8d22e789d387b91617  
Timestamp: **2026-09-29 07:29:51 UTC**.

The 512-wide FWHT now uses the 256-thread threadgroup kernel rather than the one-simdgroup path.

P51 interpretation:
- useful implementation support for Hadamard/rotated low-bit quantization;
- no Qwen end-to-end physical receipt is published, so this does not move Apple TG targets.

### NEW — vLLM recurrent/KDA prefill checkpoints

Source:
https://github.com/vllm-project/vllm/commit/3e2a7e74a556623ddee3a327299d7bf04055501e  
Timestamp: **2026-09-29 09:14:30 UTC**.

GLM-5.3 FlashKDA now exports both convolution and recurrent state at aligned prefill checkpoint boundaries. Tests restore those states and verify that suffix execution reproduces uninterrupted prefill, including cases with speculative rows.

P51 rule strengthened:
- a reusable hybrid prefix requires a materialized recurrent checkpoint at a valid aligned boundary;
- KV alone is insufficient;
- speculative rows must not corrupt the non-spec checkpoint ordering/state identity.

This is cross-model/hardware correctness evidence only.

### NEW / low-priority — vLLM fast-start weight cache gains PP support

Source:
https://github.com/vllm-project/vllm/commit/af5b4857e1353c01fd6bf41bc3cb9f84dc82dd89  
Timestamp: **2026-09-29 09:37:43 UTC**.

The weight-cache daemon now keys and places cached weight shards by DP × PP × TP rank rather than rejecting pipeline parallelism.

P51 interpretation:
- corroborates the general rule that persistent/cached artifacts in PP must include **stage identity** in their cache key;
- startup/weight-cache feature only; no inference target movement.

## RECOVERED CURRENT — Swift 1.5 Flash-Next

Primary source:
https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GGUF

The official comparison uses:
- BF16;
- **xhigh** thinking;
- 262,144 context for the seeded benchmark suite;
- MTP disabled;
- temperature 1 / top-p .95 / top-k 20;
- five seeds for seeded benchmarks.

Paired base Flash -> Swift 1.5 Flash:

| Benchmark | Base | Swift | Mean thinking/output-token effect |
|---|---:|---:|---:|
| GPQA-D | **89.80** | 89.60 | **-55.8% thinking** |
| MMLU-Pro | **87.75** | 87.20 | **-57.0% thinking** |
| C-Eval | 93.27 | **93.60** | **-44.1% thinking** |
| IFBench | **73.20** | 70.13 | **-46.9% thinking** |
| AIME 2026 | **98.67** | 96.67 | **-31.3% thinking** |
| HMMT | **98.00** | 97.33 | **-35.1% thinking** |
| ERQA | **70.80** | 69.30 | **-55.7% thinking** |
| LiveCodeBench v6 | 88.40 | **90.39** | **-44.8% thinking** |
| Terminal-Bench 2.1 | 67.64 | **69.66** | **+11.9% mean total output** |

Important:
- xhigh is the strongest relative Swift setting; lower reasoning levels lose materially more GPQA quality;
- the token reduction is strongly workload-dependent;
- Terminal-Bench is an explicit counterexample to any claim that Swift always emits fewer total tokens.

P51 consequence:
- Swift Flash becomes a **first-class alternate main-Flash checkpoint**;
- physical dual-M1 TG / PP numbers do not change;
- base Flash remains the quality/control checkpoint until Swift passes the full P51 xhigh AA/tool/128K+/MTP suite.

### Independent xhigh agentic corroboration — Aider

Source:
https://www.reddit.com/r/LocalLLaMA/comments/1wsvr71/qwen38_flashnext_vs_swift_15_flashnext_aider/

Reported paired run:
- base Flash: **90.7% retry pass**, **17,646 tokens/case**, **1,542 s/case**;
- Swift Flash: **86.9% retry pass**, **6,991 tokens/case**, **608 s/case**;
- paired n=107: 99 agreements, 2 Swift gains, 6 losses; McNemar exact p approximately 0.29.

Interpretation:
- strong evidence for useful task-seconds reduction;
- not proof of exact quality equivalence;
- score task wall-time / tokens-per-solve separately from physical TG.

### Same-runtime physical check

Strata's Swift documentation reports at 4K / IQ2_XS roughly:
- Swift: **465 PP / 78.7 TG**
- base: **467 PP / 78.3 TG**

Thus Swift's main throughput advantage is fewer generated reasoning tokens, not a materially faster per-token architecture.

### Compact Swift Flash GSQ-RCO packs

Current Swift-specific compact releases:
- IQ3_XXS: **75.97 GB**
- IQ2_XS: **68.15 GB**
- Q2_0 experimental: **66.55 GB**

Their Swift-specific quant refinement/KLD work is predominantly at **512 tokens** and explicitly does not establish long-context parity. Standard Swift GGUFs publish longer-context distribution measurements, but that is not a substitute for certification of the compact GSQ-RCO artifacts.

P51 gate:
- do not inherit the base Flash low-bit AA priors automatically;
- certify the actual Swift deployment quant at xhigh, 128K+, tools, recurrent/QSA state stability, MTP acceptance and repeated-agent trajectories.

## RECOVERED CURRENT — newer-Apple public Flash fork, not M1

A separate public Mac report uses an **M5 Pro 64 GB**, not M1 Max. It reports approximately:
- **367 PP @4K**
- **27.6 TG** with depth-3 MTP
- **18-18.6 TG** target-only
- **~20.6 TG** at ~29K real-chat context
- gathered sparse attention roughly +19% @62K and +50% @130K
- Metal MoE fusion roughly +5-9%

P51 interpretation:
- useful mechanism evidence for sparse attention / MTP / Metal fusion;
- does **not** upgrade the previous exact-chip M1-Max ~27-TG anecdote into a receipt;
- no M1 target movement.

## SAME-DAY CURRENT — exact M1-Max ~27-TG lead remains unpublished

The previous MoEspresso-thread claim of **~27 TG on M1 Max 32-core** still has no public fork/config/context/acceptance denominator in this strict window.

P51 treatment:
- retain as high-priority follow-up only;
- do not move single-M1 or dual-M1 Flash confidence.

## Outside cutoff

Strata issue #57 received an update at **2026-09-29 10:01:06 UTC**, four seconds after this pass's cutoff. Any new content in that update belongs to the next pass.

## Strict-window negative scan

- **TensorFold:** no post-boundary commit after 0.3.6.2.
- **Ishizuki:** no post-boundary commit.
- **oMLX:** no P51-relevant Qwen3.8 Flash/27B performance change in-window.
- **mlx-serve:** no post-boundary commit after the already-promoted mid48 work.
- **Exact 2x M1 Max / TB4 Flash:** no new reproducible physical receipt.
- **Exact user's RTX 5070 Ti / Strata:** no final 32K/64K/128K 0.1.22 IQ3_XXS/IQ3_S matrix and no new 8h/24h soak receipt.
- **DASLab:** no newer official Flash IQ3_S source-paired 32K/64K/128K/262K quality result found.
- **Exact M1-Max ~27-TG lead:** still unpublished.

## Durable target changes

### Swift 1.5 Flash effective-task-throughput lane

Added to `RESEARCH-TARGETS.md` as a separate alternate Flash checkpoint lane.

Do not change:
- physical **40 TG @ genuine ~128K** target;
- physical **400 cold PP** target;
- base-Flash AA control.

Track Swift with:
- physical TG / PP;
- solved-task wall time;
- output/reasoning tokens;
- tokens per solve;
- tool trajectory length;
- long-context/tool/AA quality;
- MTP acceptance/rollback.

### Strata IQ3_S ~32K PP confidence

Target stays:
- **1,200 PP @ ~32K**

Planning confidence:
- **~80% -> ~90%**

Reason:
- direct **1,213 PP** IQ3_S 32K receipt on the weaker RTX 5070 12 GB.

No change to:
- IQ3_S 64K / 128K PP centers or confidences;
- IQ3_XXS PP ladder;
- any Strata TG target;
- AA priors.

## Canonical planning state after this pass

- Dual-M1 Flash-Next: **40 TG sustained @ genuine ~128K / 400 cold PP / ~70% >=40 TG**.
- Single-M1 dense27B: **25 TG / ~110 PP**.
- Persistent root-image target unchanged.
- Swift dense27B lane retained.
- **Swift Flash lane added.**
- RTX 5070 Ti dense CUDA-v2 ladder unchanged.
- Strata IQ3_S 32K: **1,200 PP / ~90% confidence**.
- Strata remaining IQ3 PP/TG rows unchanged.
- IQ3_XXS AA>=38: **~85%**.
- IQ3_XXS AA>=40: **~65%**.
- IQ3_S AA>=40: **~80%**.

## New hard boundary

**2026-09-29 10:01:02 UTC**
