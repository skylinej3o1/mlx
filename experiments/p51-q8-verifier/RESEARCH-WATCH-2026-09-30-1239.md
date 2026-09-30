# Project 51 research watch — 2026-09-30 12:39 ET

Freshness boundary entering: **2026-09-30 16:22:36 UTC**  
Cutoff: **2026-09-30 16:39:54 UTC**

## Decision

One durable correction to STATE; **no canonical numerical target movement** and no TARGETS-file change.

The user's RX 6800 question also triggered a recovered-current AMD evidence pass. That evidence is recorded as a
secondary low-confidence planning lane, not as a promoted Project-51 target.

## UPDATE — vLLM #59448 32K MTP result corrected upward

Issue #59054 comment at 16:38:43 UTC:
https://github.com/vllm-project/vllm/issues/59054#issuecomment-5915559599

The previous 32K serving comparison included the first slow decode steps immediately after a long prefill and only
averaged 64 generated tokens. A corrected steady-state run uses 160 generated tokens, skips the first five steps,
keeps the same seed/machine, and uses FULL_AND_PIECEWISE graphs.

At 32K on gfx1151 / Qwen3.8-27B / MTP k=3:
- stock gate: 581 ms/step, 3.2 tokens/step, **~5.5 tok/s**;
- 3D verify + masked-segment guards: 162 ms/step, 3.3 tokens/step, **~20.5 tok/s**;
- no speculation: 92 ms/step, **10.9 tok/s**.

So the fixed verify path makes MTP **~1.9x faster than no-spec** at 32K on this box. PIECEWISE graphs reproduce
essentially the same 163-ms step time.

Classification: **UPDATE / correction**. Retire the earlier statement that MTP remained slower than no-spec after
the kernel fix. Transfer the mechanism only; do not transfer 20.5 tok/s to Project-51 NVIDIA/Apple hardware.

## NEW / low-transfer — vLLM CI only

Commit `d2fb35f66e6ce9fbd0e32c6129b130ad90c1754c` at 16:24:08 UTC removes a duplicate ROCm CI run.
No Project-51 performance/quality effect.

## NEW / irrelevant — TensorFold and SGLang issue activity

TensorFold issue #153 was created at 16:36:26 UTC asking about vision-model support. No benchmark or architecture
evidence.

An old SGLang OLMoE TP issue was touched at 16:37:38 UTC; unrelated to Flash-Next.

## RECOVERED CURRENT — RX 6800 / RDNA2 Strata-style feasibility

Upstream Strata's documented HIP backend remains a Linux **gfx1100 RX 7900 XT/XTX** lane. It does not currently
claim RDNA2 gfx1030 support.

Community evidence:
- Strata issue #259: RX 6700 XT / gfx1031 / 12 GB / community port / IQ3_XXS. Short prompts serve coherently with
  MTP at **6-10 tok/s**, but ~1K+ prompts currently fail in multi-chunk prefill with `routed id out of range`.
- Tuned upstream-style gfx1100 evidence on RX 7900 XTX + 64 GB host reaches **55-59 tok/s** output on 4K-9K fresh
  IQ3_XXS requests, with first-use/warm prefill from ~448 to ~967 tok/s.
- RDNA4 16-GB transfer controls: RX 9070 ~23 tok/s decode / ~238 prefill on a 4,445-token prompt; RX 9060 XT IQ1_M
  ~27-31 decode and ~540-753 prefill.

Planning inference for RX 6800 16 GB + 64 GB DDR4, assuming a fixed/tuned Linux RDNA2 port:
- <=32K: **~12-18 tok/s**;
- ~64K: **~10-15 tok/s**;
- ~128K: **~8-12 tok/s**;
- cold PP: **~150-350 tok/s** order-of-magnitude.

Current minimally tuned/community path should be expected nearer **~8-14 tok/s** short-context and is not yet
long-prompt reliable. 64 GB primarily buys resident CPU-expert/cache feasibility; it does not transform RDNA2 GPU
throughput. Exact Ryzen model remains unspecified, so CPU-offload uncertainty stays material.

Classification: **RECOVERED CURRENT / planning inference**, not a measured RX 6800 Strata result and not a canonical target.

## Strict-window negative scan

From **16:22:36 -> 16:39:54 UTC**:
- no new Strata commit/release;
- no new oMLX commit/release;
- no new MLX commit;
- no new relevant llama.cpp Flash-Next/MTP commit;
- no DASLab Flash-Next checkpoint/RCO update;
- no TurboQuant-MLX, MoEspresso, mlx-serve or Ishizuki update affecting Project 51;
- no exact RX 6800 Strata benchmark appeared.

## Canonical target state

Unchanged from the 16:22:36 UTC watch:
- RTX 5070 Ti IQ3_XXS PP: **3,000 / 2,900 / 2,750 / 2,500** at 32K/64K/128K/262K;
- conditional 262K/64-GB fit prior: **~90%**;
- IQ3_XXS AA>=38 **~85%**, AA>=40 **~65%**;
- IQ3_S AA>=40 **~80%**;
- K6/V4 long-horizon quality **~60-70%**;
- dual-M1 Flash target remains **~40 TG @128K / ~400 PP**.

Secondary AMD planning lane is not promoted into TARGETS.

## New hard boundary

**2026-09-30 16:39:54 UTC**
