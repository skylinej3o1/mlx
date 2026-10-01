# Project 51 research watch — 2026-10-01 06:28 ET

Freshness boundary entering: **2026-10-01 03:57:17 UTC**  
Cutoff: **2026-10-01 10:28:50 UTC**

## Decision

Durable STATE and TARGETS changes. **Canonical 5070-Ti and dual-M1 numerical targets do not move.**

Material changes:
- promote Strata qualification baseline to **0.1.31+**;
- materially raise the secondary **RX 6800 / RDNA2** planning lane from the old 8-18-TG class to roughly
  **28-36 TG**, based on a same-architecture RX 6900 XT receipt;
- add explicit Apple long-context **batched-MTP rollback** and **cold-vs-warm PLE residency** gates;
- record a 1M-token exact-5070-Ti stretch receipt without promoting the native 262K production context.

## NEW — Strata 0.1.31

Release: https://github.com/Niko1221/Strata/releases/tag/v0.1.31  
Commit: `9259cad4cfa3543cd3b8decab5962672b968c649`  
Created 04:27:52 UTC; published 05:13:47 UTC.

Project-51 relevant changes:
- fixes the late request-finalizer/status race (#266);
- watchdog exit releases GPU waits before terminating (#267);
- Linux multi-GPU full-arena pinning restored; the 8-GiB cap is Windows-specific again (#253);
- `STRATA_ARENA_PIN_GIB=auto` adds an opt-in Windows shared-memory-aware cap (#243);
- tagged installs pin engine/model/dependency versions (#214);
- Windows GGUF expert loading roughly 2x faster;
- experimental file-tier/ram-budget path runs Unsloth UD-Q4_K_XL (~111 GB download) on RTX 5070 12 GB + 64 GB
  host at ~7-8.5 tok/s with a 40-GiB RAM budget.

Release qualification retains fixed-cache identity to 0.1.30 on Q2_0/IQ3_XXS/IQ3_S/Coder and repeats the 64K
retrieval/reuse/tool/cancel/sample server sequence.

Classification: **NEW baseline promotion**. Exact-box soak/admission gates remain.

## RECOVERED CURRENT / UPDATE — exact gfx1030 RX 6900 XT dramatically raises the RX 6800 prior

PR #311:
https://github.com/Niko1221/Strata/pull/311

The PR was created at 23:17:13 UTC, just before the previous hard boundary, then updated at 06:21:57 UTC. Do not call
the underlying receipt new.

Experimental gfx1030 setup:
- RX 6900 XT 16 GB;
- i7-13700KF;
- 63 GB RAM;
- NixOS / ROCm 7.2.3;
- Swift 1.5 IQ3_XXS;
- 131,072 context, 32K resident KV.

Measured:
- **38-42 tok/s decode with 15 CPU workers, including a full 131K context**;
- 35-37 with 8 workers; 26-28 with 24 workers;
- **246 PP at ~2K**;
- **330-339 PP** at auto 8K chunks around 8K/16K;
- 45.5 TG after a 16K prefill.

Classification: **RECOVERED CURRENT / major planning correction**. Revised RX 6800 + 64-GB DDR4 inference:
~28-36 TG short-to-128K, ~27-34 at filled 128K, ~220-300 PP. Moderate confidence; PR open, exact card/model differ.

## NEW — exact RTX 5070 Ti 16 GB reads ~1.04M tokens

Issue #348, created 07:26:05 UTC:
https://github.com/Niko1221/Strata/issues/348

RTX 5070 Ti 16 GB / Ryzen 7 7700 / 93 GB RAM / IQ3_XXS / INT8 streamed KV / 32K resident / MTP S=4 / YaRN x4:
- ~1.04M pinned KV: **12.38 GiB**;
- 1,037,660-token prompt: **626 s = 1,657 PP** from zero;
- retrieval: **8/10** at ~1.04M.

But YaRN changes behavior inside the trained range:
- ~156K unscaled prior: 8/10;
- ~156K YaRN x4: **6/10**.

Classification: **NEW stretch-context physical receipt**, not production-context promotion. Native unscaled 262K remains
the target; 93-GB host result does not establish 1M on the user's 64-GB host.

## NEW — oMLX long-context batched MTP rollback becomes O(context)

Issue #4141, created 07:22:08 UTC:
https://github.com/jundot/omlx/issues/4141

M5 Ultra / Flash-Next oQ4e / 100K shared prefix + 2K private/session:
- B1: MTP 115.5 vs standard 93.5;
- B2: 107.1 vs 124.1;
- B4: 123.2 vs 161.3;
- B8: 150.9 vs 228.3 aggregate.

At eight ~100K rows:
- verify attention ~33.1 ms;
- ragged rollback **110.3 ms** because whole K/V + QSA-indexer banks are physically rolled.

A singleton-only MTP switch recovers ~122.7 / 155.5 / 223.6 at B2/B4/B8.

Classification: **NEW Apple multi-agent qualification gate**. No B1 headline target movement.

## NEW — oMLX PLE SSD warmth materially changes observed decode

Issue #4140, created 06:54:30 UTC:
https://github.com/jundot/omlx/issues/4140

M3 Ultra 96 GB / oMLX 0.7.0 / Flash-Next oQ4e-mtp with PLE offload:
- fresh short requests initially **62.2-64.6 tok/s**;
- immediate identical replays **80.1-80.4 tok/s**;
- later warm replays ~80.5-80.8;
- request-level page-ins correlate extremely strongly with the slowdown in that experiment.

The report explicitly does not prove all page-ins are PLE decode reads.

Classification: **NEW benchmark-state confounder**. Apple TG must report cold-vs-warm PLE state and should instrument
page-ins/read stalls.

## NEW — Strata sm_86 short-prefill regression is architecture-specific

Issue #340, created 05:20:33 UTC:
https://github.com/Niko1221/Strata/issues/340

2x RTX A5000 / sm_86 / Coder IQ1_M:
- ~1.8K PP: 1,487 -> 883-973 from 0.1.28 to 0.1.30 (~-35 to -38%);
- ~14K: 2,143 -> 1,860-1,906;
- ~42K: ~-2%;
- decode unchanged around 71 tok/s.

Disabling the obvious 0.1.29/0.1.30 prompt optimizations does not recover the short-prompt loss.

Classification: **NEW architecture-specific regression evidence**. No sm_120 target change; reinforces exact-card A/B.

## NEW / low-transfer — 3x3090 IQ4 at 1M

Issue #359, created 09:26:52 UTC, reports >120 tok/s at short context and ~60 tok/s around 1M on 3x RTX 3090,
compared with ~20 tok/s in the reporter's llama.cpp setup. Protocol is too thin for target credit.

## UPDATE — pruned Q2 low-cost lane

Issue #298 receives further engineering claims:
- ~35 tok/s;
- estimated 400+ PP;
- reporter believes 6-GB VRAM may be possible at lower speed.

Quality remains the limiting unknown. Maintainer is willing to accept a pruning converter only as an experimental tool
with quality measurement against the full model.

## NEW / experimental — Strata NVFP4, INT8-KV rotation and larger prefill chunks

PR #353 (NVFP4 experts on 0.1.31):
- RTX 5090, 8K prefill: W4A8 **4,231 PP**, W4A4 **4,583 PP**;
- same decode;
- CPU/GPU NVFP4 expert arithmetic is tolerance-equal rather than bit-exact, and routing/timing can therefore cause
  run-to-run token divergence unless expert-cache ownership is fixed.

PR #293 (INT8 KV Hadamard rotation):
- local attention error improves;
- first-token KL improves for NVFP4 but **worsens for IQ2_XS**.
Rotation stays opt-in/model-specific.

PR #282 (32K prefill chunks):
- IQ2_XS 32K prefill +~15% on RTX 5090;
- NVFP4 3,535 -> 5,201 PP;
- chunk-count changes can alter summation order/tokens.

Classification: **NEW/UPDATE experimental mechanisms**, no canonical credit.

## NEW / datacenter mechanism — SGLang NEXTN optimization series

PR #41175 updated in-window. Full series on B200 x4 / TP4 / Flash-Next NVFP4:
- normal TPOT 4.1270 ms -> NEXTN 1.6936 ms;
- derived decode 242.3 -> 590.4 tok/s;
- AIME-style integration: 95.42% normal vs 95.00% NEXTN.

Performance uses simulated acceptance length 3.3, so this is mechanism evidence only.

## NEW from previous eight-second exclusion — vLLM FlashAttention KV-view bookkeeping

Issue #59534 was created 03:57:25 UTC, eight seconds after the prior cutoff. Local 8xH100 patch caches derived K/V
views and reports TTFT p50 -12 to -16% with no output change. Low direct transfer.

## Strict-window negative scan

DASLab Flash-Next GSQ-RCO main remains `ed59f92`; no new checkpoint/allocation/benchmark:
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/main

Strata latest release is now 0.1.31. TensorFold remains 0.6.0; oMLX remains 0.7.0. No material strict-window
TurboQuant-MLX, MoEspresso or Ishizuki release changes the canonical targets.

## Canonical target state

Unchanged:
- RTX 5070 Ti IQ3_XXS cold PP: **3,000 / 2,900 / 2,750 / 2,500** at 32K/64K/128K/262K;
- conditional 262K/64-GB fit prior: **~90%**;
- IQ3_XXS AA>=38 **~85%**;
- IQ3_XXS AA>=40 **~65%**;
- IQ3_S AA>=40 **~80%**;
- K6/V4 long-horizon quality **~60-70%**;
- dual-M1 Flash target: **~40 TG @128K / ~400 PP**.

Secondary lane revised:
- RX 6800 16 GB + 64 GB DDR4: **~28-36 TG**, **~220-300 PP** planning range, moderate confidence.

## New hard boundary

**2026-10-01 10:28:50 UTC**
