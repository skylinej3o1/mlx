
# Project 51 research watch — 2026-09-30 06:55 ET

Freshness boundary entering: **2026-09-30 08:40:26 UTC**  
Cutoff: **2026-09-30 10:55:22 UTC**

## Decision

Durable STATE and TARGETS changes, but **no numerical target movement**.

Operational changes:
- qualify new Strata runs on **0.1.28+**;
- the old 1,058-1,100 MiB manual reserve is a 0.1.27 workaround/control, not the normal 0.1.28+ setup;
- keep RTX-50/sm_120 qualification on CUDA 13.x;
- add served-vs-fused GDN arithmetic parity to Apple source-equivalence/MTP certification.

## NEW — Strata 0.1.28

Release: https://github.com/Niko1221/Strata/releases/tag/v0.1.28  
Main commit: bbaaabb4643bb7873d4cef9d48b5dcf96e6cbff4  
Created 09:18:54 UTC; published 09:45:28 UTC.

0.1.27 sized the expert cache before allocating its enlarged CJK MTP head. That consumed the nominal reserve after
cache sizing. 0.1.28 accounts for the draft head first, so the configured reserve remains available; the cache holds
a few percent fewer experts by design. Issue #199's release check reports a 12-GB test card moving from 210 to
379 MiB free.

New --draft-vocab en keeps the older English/code subset, saves about **110 MiB VRAM** and is reported 1-2% faster
for English, but Chinese/Japanese/Korean get almost no useful drafts. Keep the multilingual draft for AA and
multilingual certification; use the English subset only as a labeled performance/capacity arm.

0.1.28 also fixes:
- cancelled-prompt state poisoning the next request;
- /status authentication and explicit-empty-key handling;
- installed-model --host/--api-key propagation;
- tool arguments being truncated by literal closing-tag text;
- misleading engine-exit diagnostics.

Release qualification says fixed-cache output is byte-identical to 0.1.27 across Q2_0/IQ3_XXS/IQ3_S/Coder and
includes 8K/16K/32K needles. This is correctness/stability evidence, not a new exact-card PP/TG A/B.

Sources:
- https://github.com/Niko1221/Strata/issues/199
- https://github.com/Niko1221/Strata/issues/217
- https://github.com/Niko1221/Strata/issues/210

## UPDATE — first-request stall family is not fully closed

Issue #217 was closed because the original report had exhausted VRAM and a stale stage label. A strict-window
follow-up at 10:26:26 UTC, still on **0.1.27**, reports a different Windows machine stalling with up to
**1,668 MiB free**, one live thread in nvcuda64.dll, GPU 100% utilized and ~0-1% memory bandwidth.

Source: https://github.com/Niko1221/Strata/issues/217

Do not claim 0.1.28 has eliminated the entire stall family until the exact-box >=8 h soak includes repeated cold
long prompts and cancellation/retry cycles.

## NEW — exact RTX 5070 Ti + 62-GB Linux host receipt, with a CUDA-12.8 PLE failure

Issue #224: https://github.com/Niko1221/Strata/issues/224  
Created 09:30:06 UTC.

Configuration:
- RTX **5070 Ti 16 GB**, sm_120;
- **62 GB RAM** Linux;
- IQ3_XXS native pack;
- INT8 KV, 32,768 resident cells;
- 65,536 configured context;
- MTP spec4;
- 1,100-MiB reserve; **634 MiB free after load**;
- Strata 0.1.27 self-built with **CUDA 12.8**.

Prompts around 1.7K+ fault in batched PLE postops; CUDA_LAUNCH_BLOCKING=1 localizes the first error to
native_ple_postops_batch. With **STRATA_PLE_BATCH=0**, all tested prompts succeed, including **11,105 tokens**
in two chunks. Reported fallback PP ranges 546-1,320 depending on prompt size.

Classification:
- real exact-GPU / near-exact-host-class execution evidence;
- not a production PP anchor because it uses a fallback kernel;
- not 262K host-fit proof because only 65K was configured and 11K filled;
- CUDA 12.8 was already outside the qualified sm_120 lane, so reproduce on CUDA 13.x before treating this as a
  current generic Strata defect.

This modestly strengthens the proposition that ~64-GB Linux can at least load/run IQ3_XXS; the conditional
**~90% 262K/64-GB fit prior stays unchanged**.

## NEW — Strata long-prefill optimization work

PR #203: https://github.com/Niko1221/Strata/pull/203

The current mid-prompt checkpoint copy reportedly idles the GPU about **370 ms/checkpoint**. At a default 16K
checkpoint interval, seven checkpoints at 128K imply ~2.6 s of potential idle time arithmetically. The async
pinned-staging PR has no single-GPU 128K wall-clock A/B yet; maintainer explicitly requested one. **No PP target
movement.**

PR #216: https://github.com/Niko1221/Strata/pull/216

Layer-split state is being carved by owned QSA/GDN layers instead of whole-model state, and prompt loans become
per-stage. A helper-rank prompt-offload experiment was rejected after measuring **38.1 -> 83.4 s** on a 23,420-token
prompt, conflicting with MMQ and exposing a pinned-buffer race. Useful distributed-state evidence; no single-GPU
target transfer.

## NEW — oMLX M1 Max GDN exactness regression

PR #4122: https://github.com/jundot/omlx/pull/4122  
Created 09:25:28 UTC.

On M1 Max 64 GB, the fused speculative verifier can use a different float32 exponential than the served SiLU graph,
changing the final FP16/BF16 norm by **one ULP**. New regression tests fail on unchanged main and pass with the fix;
a real Qwen3.6-35B-A3B checkpoint matched **1,950** decode norm checks after selecting served-equivalent arithmetic.

P51 rule: source-equivalence/MTP certification requires **served-vs-fused GDN arithmetic parity**, not merely close
float32 results or similar text.

## NEW — oMLX compiled TurboQuant quantizer: small and workload-dependent

PR #4121: https://github.com/jundot/omlx/pull/4121  
Created 09:20:17 UTC.

M1 Max 64 GB, Qwen3.6-35B-A3B, TurboQuant 3-bit KV:
- ~462 tokens: 69.30 -> 70.40 TG (+1.6%)
- ~1,998: 67.14 -> 68.31 (+1.7%)
- ~8,142: 61.50 -> 62.24 (+1.2%)
- nightly at ~18.5K: 67.99 -> 66.43 (-2.3%)

Cache states/responses matched. Opt-in/default-off. Worth benchmarking, not a generic multiplier.

## UPDATE — oMLX Affine KV hardware boundary

PR #3582: https://github.com/jundot/omlx/pull/3582  
Strict-window update 08:52:06 UTC.

The author explicitly recommends Affine4/Affine8 for M5, while **TurboQuant remains the compressed-KV recommendation
for M1-M4**. The portable Affine path is a correctness/capacity fallback. Do not transfer M5 100K/200K capacity
receipts into the dual-M1 plan.

## UPDATE — context-copy drafting

PR #4104: https://github.com/jundot/omlx/pull/4104

Existing Qwen3.8-Flash-Next M5 Ultra measurements show file-edit +30.5% and Grill +19.8%, ordinary coding chat flat,
with greedy output exactness. A strict-window comment adds sampled speculative-copy evidence on GLM-5.3-Flash,
explicitly **not Qwen**. Keep this as a workload-specific edit/repetition arm; do not transfer GLM sampled gains.

## NEW — SGLang architecture signals

Merged PR #40227: https://github.com/sgl-project/sglang/pull/40227  
Commit 8055ccd2cd36964541b36b817e40f5a758e31746 at 09:19:02 UTC.

It exposes GDN/KDA prefill hooks, checkpoint/prefix routing and auxiliary recurrent-state accounting. No GPU
performance/accuracy run was performed. This supports the P51 rule that recurrent auxiliary state must be accounted
separately from attention KV.

PR #41880: https://github.com/sgl-project/sglang/pull/41880  
Created 10:53:29 UTC.

On MI355X/gfx950, a Qwen3.8 hyperconnection hc_mix kernel reports **1.73-2.38x kernel-only speedup** for M=1..16.
Transfer the mechanism only: hyperconnection mixing is a decode-time small-M, weight-read-bound target. Do not
transfer AMD speed numbers to NVIDIA/Apple.

## NEW — vLLM per-token NVFP4 MoE merge carries an explicit accuracy warning

PR #50030: https://github.com/vllm-project/vllm/pull/50030  
Merged commit 0103a9b96fde27d26a464bf2c30b4d977b2a134f at 10:42:03 UTC.

GSM8K examples:
- Qwen3-30B-A3B: 94.09% BF16 -> 93.56% NVFP4
- Nemotron-3-Nano: 23.20% -> 17.59%
- Nemotron-3-Super: 93.78% -> 94.24%

The PR explicitly says runtime validation does not establish accuracy parity. This is broader support for P51's
low-bit quality discipline, not direct DASLab/5070-Ti evidence.

## UPDATE — llama.cpp Qwen3.8 MTP still WIP

PR #28243: https://github.com/ggml-org/llama.cpp/pull/28243

Strict-window report: RTX 4080 FE 16 GB + RTX 5060 Ti 16 GB at 128K, q4/q5 weights, **18-19 TG without MTP** and
**16-21 TG with MTP**. Different topology and no stable speedup; no target credit.

## NEW / low-transfer — TensorFold and MLX

TensorFold main has no strict-window commit, but:
- PR #133 adds an operator-settable CUDA startup reserve; no live server run with it.
- PR #134 makes GLM-5.3-Flash DFlash2 sliding-attention/ring state constant with context; GLM-specific/kernel-only.

Sources:
- https://github.com/ashhart/TensorFold/pull/133
- https://github.com/ashhart/TensorFold/pull/134

MLX commit 91c83d19bf022d7bc3e906582435f69fdc77ec63 fixes cooperative-tensor builds on macOS 27; no direct P51 performance
receipt.

## KNOWN — no strict-window DASLab release

HF commit history:
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/commits/main

The latest model commit is still ed59f92, about a day old at cutoff. The collection-page "updated" badge is not
commit-level freshness evidence. No new strict-window checkpoint, RCO allocation, source-paired 262K quality result
or benchmark.

## SAME-DAY CURRENT — Reddit/community

A current LocalLLaMA post reports a 12-GB RTX 5070-Ti laptop + 64-GB host around **1,500 PP at 32K** and **51 TG
around 43K** with IQ3_XXS/Strata. Reddit exposes the calendar day but not an auditable strict sub-day timestamp.
Different GPU memory class; supporting evidence only and already consistent with the prior same-day consumer-system
classification. **No target movement.**

## Strict-window negative scan

From **08:40:26 -> 10:55:22 UTC**:
- no new DASLab HF commit;
- no TurboQuant-MLX commit;
- no MoEspresso commit;
- no Ishizuki commit;
- no mlx-serve main commit;
- no TensorFold main commit;
- no new sustained filled-128K dual-M1/TB4 receipt;
- no Strata K6/V4 compressed+streamed implementation;
- no exact 64-GB-host + filled-257K IQ3_XXS receipt.

## Canonical target state

RTX 5070 Ti / Strata IQ3_XXS:
- TG centers unchanged; 95-118 full-context list-generation remains favorable-workload evidence only.
- cold PP: **32K 3,000 / 64K 2,900 / 128K 2,750 / 262K 2,500**
- compressed-streaming conditional 262K/64-GB fit prior: **~90% unchanged**
- IQ3_XXS AA>=38 **~85%**
- IQ3_XXS AA>=40 **~65%**
- IQ3_S AA>=40 **~80%**
- K6/V4 long-horizon quality **~60-70%**

Apple:
- no TG/PP center movement;
- add GDN served-arithmetic exactness gate;
- TurboQuant remains M1-M4 compressed-KV priority;
- compiled TQ quantization stays workload-gated.

## New hard boundary

**2026-09-30 10:55:22 UTC**
