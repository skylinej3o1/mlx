# Project 51 research watch — 2026-09-30 19:19 ET

Freshness boundary entering: **2026-09-30 20:42:47 UTC**  
Cutoff: **2026-09-30 23:19:38 UTC**

## Decision

Durable STATE and TARGETS changes; **no canonical numerical target movement**.

New test-plan consequences:
- TensorFold **0.6.0** is now the current experimental TensorFold baseline;
- Apple prefill certification must include **deep suffix prefill after a retained 60K+ prefix**, not only a cold prompt;
- source-equivalence must assert critical GGUF tensor kinds/byte counts against kernel expectations;
- refused checkpoint spill must be asynchronous/bounded and prove resume-vs-fresh token identity.

## NEW — TensorFold 0.6.0

Release: https://github.com/ashhart/TensorFold/releases/tag/v0.6.0  
Commit: `c4646171139ee8a3c38103eaa1699dad226ec12b`  
Created 21:30:58 UTC; published 21:31:05 UTC.

Relevant release evidence:
- RTX 40 / sm_89 support;
- one RTX 4090 / Qwen3.8-27B DFlash2 receipt at 40,182 tokens: 2.4-2.6k tok/s prompt fill from 2K-32K and 64-86
  tok/s decode, with drafted==serial and resume/resend==fresh;
- Flash-Next prompts can fill inside decode rounds under parallel serving, reducing head-of-line TTFT;
- an 18.7K Flash-Next resend is reported 8.3 s -> 0.08 s via retained prompt state;
- CUDA prompt arithmetic defaults to bf16; on the 27B the release reports KL 0.0031 vs fp32, compared with 0.0624
  for FP8 prompt rows;
- pre-M5 copy windows widen and concurrent Flash-Next rounds use matrix units; one M3 Ultra edit reports 190->233
  tok/s;
- Flash-Next NVFP4 CUDA: +4.9-7.1% decode and +15-16% 2K-16K prefill, bit-identical.

Classification: **NEW experimental-runtime baseline/mechanism evidence**. No exact dual-M1-Max filled-128K result, so
no Apple TG/PP target movement.

## NEW — mlx-serve deep-context Flash-Next prefill collapse on pre-M5 Mac

Issue #658 created 21:28:15 UTC:
https://github.com/ddalcu/mlx-serve/issues/658

Same M3 Ultra 512-GB box, same-day comparison:
- cold ~60K prefill: mlx-serve ~1,190 tok/s, oMLX ~1,230;
- 60K -> 99K suffix after retained prefix: mlx-serve **~570 tok/s**, oMLX **~1,190 tok/s**;
- decode at 99K: mlx-serve 56-67, oMLX ~64 tok/s;
- short decode remains competitive/faster on mlx-serve.

The reporter suspects mlx-serve's pre-M5 non-NAX QSA path / 8,192 gather floor; that diagnosis is not yet
maintainer-confirmed.

Classification: **NEW Apple deep-prefill mechanism warning**. P51 now tests cold and retained-prefix suffix prefill
separately. M3 Ultra numbers do not transfer to M1.

## UPDATE — TensorFold #155 persists in 0.6.0

Maintainer comment at 21:34:38 UTC confirms boundary-capture refusal is still silently skipped in 0.6.0 and spill
only sees evictions.

Requested upstream fix requirements:
1. one refusal-reason log per request;
2. bounded asynchronous writer so multi-GB spill does not block decode rounds;
3. a test proving refused capture -> disk spill -> next-turn resume has the same token SHA as fresh prefill.

Classification: **UPDATE / resident-agent certification gate strengthened**.

## NEW — Strata RTX 4090 IQ3_XXS real-request throughput

Issues #307/#308, created 22:33-22:40 UTC:
https://github.com/Niko1221/Strata/issues/307

RTX 4090 24 GB + i9-13900K + 64 GB DDR5, native Windows, 128K configured context, INT8 KV, MTP:
- IQ2_XS: 106.1 tok/s whole request, ~115 peak, 95.5% expert-cache hit;
- IQ3_XXS: **98.1 tok/s whole request**, ~120 peak, 91.9% expert-cache hit;
- IQ3_XXS generated 11,485 tokens in 118 s.

Classification: **NEW 24-GB consumer throughput/cache receipt**. Prompt depth is unspecified; configured 128K is not
filled 128K, so no long-context TG transfer to the 5070 Ti target.

## UPDATE — pruned Q2 quality is selectively degraded

Issue #298 comments, 21:41-22:24 UTC:
- HumanEval: **92.7% / 164 problems**, ~28.9 tok/s;
- GPQA-Diamond: **25% / only 20 questions**, ~30.9 tok/s;
- reporter's Qwen3.6-35B-A3B control: **35%** on the same tiny GPQA subset.

Classification: **UPDATE / quality caution**. The 8-GB pruning experiment may retain strong coding while damaging hard
reasoning; do not generalize it to unpruned DASLab GSQ-RCO quality.

## NEW — Strata #303 exposes a file-format interpretation hole; official DASLab target is clear

Issue #303 created 21:36:58 UTC:
https://github.com/Niko1221/Strata/issues/303

An Unsloth UD-IQ3_XXS artifact stores `blk.1.ple_conv1d.weight` as F32, but the tested Strata path raw-casts it into
an F16 convolution kernel. Output becomes garbage while synthetic F16 parity tests remain green.

RECOVERED CURRENT control:
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/commit/fb6d8664256ad762f679204ebd14ab6d907fc82d

The official ISTA-DASLab IQ3_XXS allocation explicitly lists `blk.1.ple_conv1d.weight: F16`. Published IQ2_XS/Q2_0
allocations likewise use F16 for that tensor. Therefore this exact F32/raw-F16 defect does **not** apply to our
canonical DASLab target.

Classification: **NEW runtime bug + RECOVERED CURRENT target-artifact exclusion**. Add tensor-kind assertions to
certification anyway.

## NEW / low-transfer — Strata Linux layer-split pinning and prompt-borrow evidence

Issue #306 created 21:37:24 UTC:
https://github.com/Niko1221/Strata/issues/306

On 2x V100 16GB / 62GB host / Linux, an older 0.1.24 manual port reports:
- 28K prefill: 932 tok/s one card -> 378 split with the universal 8-GiB pin cap -> 976 with full Linux arena pinning;
- no-MTP decode: ~29-31 -> 35.2 tok/s;
- prompt-borrow sizing/reservation mismatches under the patched split.

Classification: **NEW platform-policy evidence, low direct transfer**. It reinforces the existing rule that WDDM pin
caps must not be blindly applied to Linux and memlock must be measured.

## UPDATE — oMLX batch realignment remains correlated with rare short stops, causality unresolved

Issue #4036 updates 21:37-22:41 UTC:
https://github.com/jundot/omlx/issues/4036

A retained M1 Max / 0.7.0rc1-era agent corpus contains 1,038 row-realignment warnings; 7 of 10 <=10-token completions
on >=5K prompts occur within 5 seconds of a realign. But a targeted 40-iteration stress run produces 203 realigns
and zero short stops, and a real agent request with the same cached-prefix/small-suffix shape also completes normally.

Classification: **UPDATE / unresolved runtime-vs-model attribution warning**. Preserve suspicious early-stop traces in
P51 Apple agent tests; do not call the realign causal.

## Strict-window negative scan

Strata's latest main release remains **0.1.30**; 0.1.31 fixes discussed earlier are not released by this cutoff.

DASLab Flash-Next GSQ-RCO commit history still tops at `ed59f92`; no new checkpoint/allocation/benchmark appears
after the prior boundary:
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/commits/main

No Project-51-relevant strict-window update was found in TurboQuant-MLX, MoEspresso or Ishizuki. MLX core has no
relevant new Flash-Next commit in the window. SGLang's Flash-Next roadmap was touched but adds no new local-device
measurement; local 5090/Spark work remains a TODO.

## Canonical target state

Unchanged:
- RTX 5070 Ti IQ3_XXS cold PP: **3,000 / 2,900 / 2,750 / 2,500** at 32K/64K/128K/262K;
- conditional 262K/64-GB fit prior: **~90%**;
- IQ3_XXS AA>=38 **~85%**;
- IQ3_XXS AA>=40 **~65%**;
- IQ3_S AA>=40 **~80%**;
- K6/V4 long-horizon quality **~60-70%**;
- dual-M1 Flash target: **~40 TG @128K / ~400 PP**.

## New hard boundary

**2026-09-30 23:19:38 UTC**
