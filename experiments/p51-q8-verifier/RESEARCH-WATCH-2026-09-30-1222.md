# Project 51 research watch — 2026-09-30 12:22 ET

Freshness boundary entering: **2026-09-30 10:55:22 UTC**  
Cutoff: **2026-09-30 16:22:36 UTC**

## Decision

Durable STATE and TARGETS changes, but **no numerical target movement**.

Operational changes:
- qualify new Strata production runs on **0.1.29+**;
- qualify new stable Apple comparisons on **oMLX 0.7.0**;
- add Windows host-registration/pin policy to the 64-GB admission gate;
- add rapid stream-abort -> immediate retry to the Strata agent soak;
- add exact-M1 mixed-width matrix routing to the Apple optimization queue;
- keep source-equivalence/state certification separate from throughput and MTP acceptance.

## NEW — Strata 0.1.29

Release: https://github.com/Niko1221/Strata/releases/tag/v0.1.29  
Commit: `d6708a4aae15b4860000d54c8af9e84d684bce09`  
Created 12:01:53 UTC; published 12:18:09 UTC.

0.1.29 adds:
- sampled-token selection split across the GPU, with same-seed token parity against 0.1.28;
- QSA verify-window block-score reuse;
- prompt-path GDN recurrence software pipelining;
- AVX2 expert-row prefetch;
- correctness fixes for bf16 NaNs, q8 split-GEMV barriers, failed KV-stream residency masking and verify-table bounds;
- immediate engine exit on CUDA prompt faults;
- a warning for RTX-50 builds using CUDA <13;
- RAM-aware 262K setup accounting instead of a fixed 90-GB rule.

Published sampling result on an RTX 5070 / Q2_0:
- top-k 20: about +4%;
- top-k 40: +15-20%;
- top-k 64: +38-42%;
- greedy: unchanged.

The release reports fixed-cache byte identity against 0.1.28 on Q2_0/IQ3_XXS/IQ3_S/Coder, including prompt-path
internal state. Its 64K server qualification includes a 58,700-token retrieval, prompt reuse, tool call,
cancelled-long-prompt recovery and sampled answer.

Classification: production-baseline promotion, **not a generic TG multiplier** and not an exact 5070-Ti IQ3_XXS A/B.

## NEW — 0.1.29 long-prompt stall remains real

Issue #251: https://github.com/Niko1221/Strata/issues/251  
Created 15:12:10 UTC.

Configuration:
- Strata 0.1.29;
- IQ3_XXS, 131,072 configured context;
- RTX 4070 Ti SUPER 16 GB;
- CUDA 13.0.2;
- 128 GB RAM / Linux;
- AVX2 CPU.

A ~13.2K prompt repeatedly stalls with the verify window at position 139. The report shows all 24 expert jobs done,
all seven workers sleeping, GPU/host at layer 48, no swap, and ~7.4 GB host RAM available; the 60-s watchdog then
kills the engine. Model load left 439 MiB VRAM free.

Classification: direct 0.1.29 stability evidence on a different 16-GB NVIDIA card. It keeps the exact-box >=8 h soak
and repeated cold-long-prompt gate mandatory. **No TG/PP or fit-prior movement.**

## NEW — Windows 63-GB host registration can poison later CUDA allocation

Issue #243: https://github.com/Niko1221/Strata/issues/243  
Created 13:58:29 UTC.

Windows 11 / RTX 4090 24 GB / 63.3 GB RAM / IQ3_XXS / 131K context:
- whole-arena `cudaHostRegister` fails;
- 36 slices / 28 GiB are then registered;
- every subsequent `cudaMalloc` fails, including a 1-MB buffer when allocation order is changed;
- external counters still showed about 19 GiB free VRAM plus substantial free RAM/commit.

The reporter's 8-GiB registration cap reaches READY in 51 s and serves at 40-44 tok/s with a 70% expert-cache hit
rate on that machine.

Classification: **NEW host-admission failure mode**, not an exact 5070-Ti receipt and not 262K proof. Add bounded
Windows pinning as a qualification control; the conditional ~90% 262K/64-GB fit prior remains unchanged.

## NEW — Linux multi-GPU shows the opposite pinning tradeoff

Issue #253: https://github.com/Niko1221/Strata/issues/253  
Created 15:26:56 UTC.

Linux / RTX 4090 + RTX 3060 / Q2_0 / 32K:
- stock 8-GiB host-registration cap: 32K prefill **664.9 tok/s**;
- Linux-only unrestricted registration patch: **2,109.8 tok/s**;
- ~28K prompt wall time: 42.674 s -> 13.359 s;
- representative expert-copy wait falls from roughly 2-2.6 s/chunk to 34-40 ms.

A 4090-only control at explicit 2048-token chunks reaches 2,814.4 tok/s.

Classification: platform/topology architecture signal. Do not make the Windows 8-GiB cap universal.

## NEW — Strata 0.1.29 request-finalization race matters for agents

Issue #266: https://github.com/Niko1221/Strata/issues/266  
Created 16:20:53 UTC, inside the strict cutoff by ~103 seconds.

A cancelled/aborted request can finalize after the next request has acquired the service FIFO, clear the new
request's status fields, and trigger `KeyError: 'tail'` / client `RemoteDisconnected`. The reporter's request-ID
ownership guard passes five local abort-after-three-chunks -> immediate-retry rounds with no exception.

Classification: agent/API correctness gate. Add rapid cancellation/retry handoffs to the soak. No physical target
movement.

## NEW — oMLX 0.7.0 stable

Release: https://github.com/jundot/omlx/releases/tag/v0.7.0  
Created 15:20:17 UTC; published 15:24:27 UTC.

For Project 51, 0.7.0 promotes to stable a large body of work already seen during RC/dev:
- faster Flash-Next prefill/decode/MTP;
- exact single-request Lightning-MTP verify rows;
- rebuilt memory admission;
- exact prefix reuse for split-GDN SpecPrefill;
- the served-equivalent fused GDN norm fix from PR #4122;
- an M1-Max native decode-attention correctness fix;
- better large-quant load behavior by releasing n-gram shards during load.

Classification: **NEW stable-baseline event**, but most underlying mechanisms are KNOWN from pre-release work.
No exact dual-M1-Max filled-128K receipt appears, so Apple TG/PP targets do not move.

## UPDATE — oMLX shared MTP parking at high concurrency

PR #4112: https://github.com/jundot/omlx/pull/4112  
Updated 12:37:31 UTC.

M5 Ultra / Qwen3.8-Flash-Next oQ5e-mtp / 8 requests:
- 272.6 -> 280.6 aggregate tok/s across all waves;
- after first wave: 272.3 -> **286.2 (+5%)**;
- MTP off: 293.4;
- 4-request and 1-request rates essentially unchanged;
- at 2 requests MTP still wins, ~205 vs 172.

Target verify/acceptance/cache are unchanged and single-request replies are byte-identical. M5-only concurrency
evidence; no M1 transfer.

## NEW — TensorFold pre-M5 Flash-Next mixed-width matrix route

PR #149: https://github.com/ashhart/TensorFold/pull/149  
Created 16:07:30 UTC.

Problem: on M1-M4, mixed Flash-Next checkpoints can send 5/6/8-bit dense projections through a row-at-a-time path
rather than the existing matrix-unit backend.

Opt-in `TF_FLASH_DENSE=matrix` routes those dense linears through the matrix backend. Tests say a 16-row window is
bit-identical to 16 one-row steps and remains within 2% of MLX quantized matmul.

M3 Ultra / Qwen3.8-Flash-Next oQ4e-mtp:
- one stream: 83-111 -> **89-130 tok/s**;
- N=4: 121-126 -> **140-168 tok/s**;
- 6.8K prefill: 1,148 -> 1,175 tok/s.

Classification: strong mechanism evidence for the exact M1 test plan, **not numerical M1-Max transfer**.

## UPDATE — TensorFold host-RAM prompt-state tier

PR #106: https://github.com/ashhart/TensorFold/pull/106  
Updated 14:45:56 UTC; closed, not merged.

On one Radeon R9700 32 GB + 62-GiB host:
- host-state tier expands the 27B window from 32,768 to 126,553 tokens, or 221,382 with FP8 KV;
- eight 24K conversations round-robin: repeat-turn TTFT 12.21 s -> **0.39 s**;
- 103.9K cold prefill: 1,348 tok/s.

It has not served on NVIDIA. Architecture/capacity evidence only.

## NEW — vLLM long-context speculative verify attention bottleneck

PR #59448: https://github.com/vllm-project/vllm/pull/59448  
Created 14:52:37 UTC; updated 16:21:59 UTC.

On AMD Strix Halo / Qwen3.8-27B W4A16 / MTP k=3, q_len=4 verify was excluded from split-KV 3D attention, leaving
a handful of programs to walk the entire KV history.

Kernel q_len=4 A/B:
- 4K: 2.959 -> 0.572 ms (5.2x);
- 16K: 9.011 -> 0.731 ms (12.3x);
- 32K: 72.199 -> 2.773 ms (26.0x);
- 65K: 262.769 -> 5.392 ms (48.7x).

End-to-end decode improves +34% at 4K, +82% at 16K and +70% at 32K, but 32K is still slower than the same stack
without speculation. Some greedy outputs differ because the reduction order changes.

Classification: mechanism and **source-equivalence warning**, not a Project-51 speed transfer.

## UPDATE — SGLang PP x speculative recurrent-state correctness

PR #40001: https://github.com/sgl-project/sglang/pull/40001  
Updated 15:29:53 UTC.

On hybrid GDN/KDA/Mamba targets, accepted recurrent state was not committed on every PP stage and, with >2 stages,
accept results could pair with the wrong in-flight micro-batch. The PR reports GLM-5.3 PP2+MTP GSM8K moving
0.745 -> 0.990 after the fix while acceptance length had looked normal before; Qwen3.8-Flash-Next PP4+MTP changes
from a crash to 0.965 / AL 3.02.

Classification: strong independent evidence that MTP acceptance is not a correctness proof. Stable recurrent-state
rows/commit ordering remain a first-class Project-51 gate.

## NEW / low-transfer — MLX

Strict-window MLX commits:
- `ac8be42c1c3668d8adc80931d7eda94e4a033def` at 12:43:24 UTC: EOF/EINTR handling in ParallelFileReader;
- `9c3d35571ac450a8ecf5c17b4d0e3fac52c08bc8` at 13:29:59 UTC: slice-bound clamping with array indexing.

No direct Project-51 performance or quality receipt.

## KNOWN / strict-window negative — DASLab and other watched sources

DASLab HF history:
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/commits/main

Latest Flash-Next model commit remains `ed59f92`, outside the strict window. No new checkpoint, RCO allocation,
source-paired 262K quality result or benchmark.

Other latest commits observed:
- TurboQuant-MLX: `a6945a0`, 2026-09-19;
- MoEspresso: `6b96f27`, 2026-09-24;
- mlx-serve: `933566c`, 2026-09-30 00:50:34 UTC;
- Ishizuki: `459ee00`, 2026-09-26.

No strict-window update from those sources.

llama.cpp strict-window commits were unrelated training-KV/batch API work; no new Qwen3.8 MTP target receipt.

## Canonical target state

RTX 5070 Ti / Strata IQ3_XXS:
- qualified baseline becomes **0.1.29+**;
- TG centers unchanged;
- cold PP unchanged: **32K 3,000 / 64K 2,900 / 128K 2,750 / 262K 2,500**;
- compressed-streaming conditional 262K/64-GB fit prior **~90% unchanged**;
- IQ3_XXS AA>=38 **~85%**;
- IQ3_XXS AA>=40 **~65%**;
- IQ3_S AA>=40 **~80%**;
- K6/V4 long-horizon quality **~60-70%**.

Apple:
- stable comparison baseline becomes **oMLX 0.7.0**;
- no TG/PP center movement;
- exact-M1 mixed-width matrix routing becomes a test, not target credit;
- TurboQuant remains M1-M4 compressed-KV priority.

## New hard boundary

**2026-09-30 16:22:36 UTC**
