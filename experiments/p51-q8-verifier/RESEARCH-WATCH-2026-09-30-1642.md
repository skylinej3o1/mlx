# Project 51 research watch — 2026-09-30 16:42 ET

Freshness boundary entering: **2026-09-30 16:39:54 UTC**  
Cutoff: **2026-09-30 20:42:47 UTC**

## Decision

Durable STATE and TARGETS changes; **no canonical numerical target movement**.

Operational changes:
- promote new Strata runs to **0.1.30+**;
- use **`STRATA_IQ_MT_MIN=1`** for Strata AA/source-equivalence/MTP certification;
- keep the stability gate open pending a 0.1.30 retest of the prompt-path hang and released fixes for the
  abort/retry ownership race, bounded verify-window exit and Windows pin-budget behavior;
- add **checkpoint-capture refusal** to resident-agent persistence tests.

## NEW — Strata 0.1.30

Release: https://github.com/Niko1221/Strata/releases/tag/v0.1.30  
Commit: `30ec18ec7094550fcc594fd948220d511d80464e`  
Created 17:34:50 UTC; published 17:50:57 UTC.

Relevant changes:
- 1K-4K prompts switch to 1,024-token streamed chunks: reported +17-28% prompt speed on the maintainer's RTX 5070;
- layer splits keep only per-card session state and lend only each card's own expert-cache tail to prefill;
- resident low-RAM mode copies the non-GPU expert complement into ordinary RAM;
- optional multi-conversation cache parks several conversations in RAM;
- AMD RDNA4 support lands;
- `STRATA_IQ_MT_MIN=1` makes native i-quant CPU expert arithmetic independent of verifier width;
- idle unload/load controls and shared expert arenas land;
- experimental >262K RoPE scaling is exposed.

Release qualification says fixed-cache output remains byte-identical to 0.1.29 on Q2_0/IQ3_XXS/IQ3_S/Coder and
the five release models pass a 64K real-use sequence including retrieval, follow-up reuse, tool call, cancellation
and sampled answer.

Classification: **NEW production-baseline promotion**. Short-prompt improvements do not change long-context PP rulers.

## NEW — width-invariant Strata expert arithmetic is now an explicit supported mode

Issue #152 closed at 20:17:06 UTC. Maintainer confirmation at 17:51:29 UTC:
`STRATA_IQ_MT_MIN=1` makes CPU experts use the multi-token kernels from width 1, so the same target-model expert
rows round the same regardless of drafting width. `native_expert_parity` checks width 1/2/4 bit-for-bit.

Reported speed effect:
- IQ3_S / AVX-512: roughly 1-3% slower;
- IQ3_XXS: about +3%;
- other arms: within noise.

Classification: **NEW certification mechanism**. This replaces the broad NO_IQ* workaround as the preferred exactness
lane. Default fast mode remains width-dependent.

## UPDATE — #251 was a prompt-path stall, not a verify-window stall

Issue #251 closed at 18:43:25 UTC after the maintainer clarified the stall report. The active stage was
`reading the prompt, from token 0`; the displayed verify window was stale state from the previous request.

The prompt path changed in 0.1.30. The maintainer asked for a 0.1.30 retest with a debugger stack if it persists.
No such retest exists inside this window.

Classification: **UPDATE / failure reclassification**, not a stability pass. Cold long-prompt starts remain in the soak.

## UPDATE — 0.1.31 is already targeted at the remaining safety races, but is not released in this window

Issue #266, 18:44:21 UTC: maintainer confirms the request-finalization ownership race and says 0.1.31 scopes status
cleanup by request id.

Issue #267, 18:44:25 UTC: maintainer explains the Windows device-loss mechanism as an unbounded final verify sync plus
GPU-side waits spinning on host-mapped flags after watchdog process exit. 0.1.31 is planned to bound the wait and
release all flags before exit.

Issue #243, 18:44:28 UTC: maintainer says 0.1.31 will cap sliced host registration below Windows' shared-GPU-memory
budget and honor `STRATA_ARENA_PIN_GIB`.

Classification: **UPDATE / planned fixes only**. Do not promote 0.1.31 until a release exists and is reproduced.

## UPDATE — 0.1.30 fixes the gfx1100 HIP verify failure

Issue #273: https://github.com/Niko1221/Strata/issues/273

The reporter's RX 7900 XTX / ROCm 7.1.52802 / Coder IQ1_M setup failed every 0.1.29 verify launch. On 0.1.30, the
same machine and pack serve successfully.

Measured 64K-window sequence:
- prefill 98 tok/s @467 -> 426 @1.7K -> 560 @6.7K -> 541 @26.8K -> **856 @49K**;
- decode 17.7 @467 -> 27.5 @1.7K -> 46.0 @6.7K -> **60.5 @26.8K** -> 35.4 @49K;
- expert-cache hit 93.3-97.1%, 17.42 GiB of experts in 24-GB VRAM;
- OpenAI and Anthropic endpoints and a tool-call smoke test pass;
- prompts through 49,005 tokens served.

Classification: **UPDATE / AMD runtime recovery**, no RDNA2 numeric transfer.

## NEW — pruned Q2 on RTX 2060 8 GB: ~30 TG, ~150 PP, 128K

Issue #298 created 20:27:04 UTC:
https://github.com/Niko1221/Strata/issues/298

A community user pruned experts from the Q2 Flash-Next model to fit an RTX 2060 8 GiB and reports:
- ~30 tok/s decode;
- ~150 tok/s prefill;
- ~17.6 GiB resident system RAM;
- ~26.8-GiB PLE can remain on NVMe;
- context up to 128K.

The reporter explicitly says coding quality versus Qwen3.6-35B is still under test.

Classification: **NEW extreme-cost capacity/performance evidence; quality unknown**. No AA or canonical target credit.

## NEW — oMLX 0.7.0 restores full 256K context on one 64-GB Apple lane

Issue #3917 comment at 17:41:57 UTC:
https://github.com/jundot/omlx/issues/3917#issuecomment-5916532477

On an M4 Max 64-GB machine with Qwen3.8-27B oQ6e-mtp, the reporter says oMLX 0.7.0 plus the new aggressive memory
tier completes the full 256K context benchmark. The balanced tier spends long periods over its soft budget and makes
very little progress near ~222K.

Classification: **NEW current Apple capacity receipt**, but for 27B/M4 Max rather than Flash-Next/M1 Max. No dual-M1
headline target transfer.

## NEW — oMLX proposal to manage Splash / splash-m1

Issue #4132 created 18:15:54 UTC:
https://github.com/jundot/omlx/issues/4132

A contributor has a working oMLX integration that launches Splash as a managed backend for Qwen3.8-27B and
Qwen3.6-35B-A3B; `splash-m1` was tested on an M1 Max. This would keep oMLX lifecycle/dashboard/cache plumbing while
using Splash kernels.

Classification: **NEW integration mechanism**, but Splash here does not target Flash-Next, so no P51 Flash TG credit.

## NEW — TensorFold checkpoint refusal can silently destroy resident-agent resume state

Issue #155 created 16:46:14 UTC:
https://github.com/ashhart/TensorFold/issues/155

On M3 Ultra 512 GB / GLM-5.3-Flash, memory-pressure prefill can refuse boundary checkpoint captures before they enter
the store. The configured conversation-spill callback only runs on eviction, so refused captures are silently lost.
The request completes but the next turn has no RAM/SSD resume state and cold-prefills the entire conversation.

Reported examples:
- 88,784 tokens -> 231 s cold re-prefill;
- 91,661 -> 234 s;
- 178,694 -> 496 s.

Classification: **NEW resident-state correctness gate**. P51 must test checkpoint-capture refusal separately from
eviction and require durable spill or explicit failure/logging.

## UPDATE — TensorFold two-Spark TP2 startup regression is gone in 0.5.0

Issue #107 closed at 16:45:39 UTC: the reporter confirms TensorFold 0.5.0 no longer exhibits the two-node startup
hang seen in 0.3.6/0.3.7.

Classification: **UPDATE / Spark stability evidence**, no hardware-buy target movement.

## NEW / low-transfer — SGLang B200 TP1 Qwen3.8-Flash-Next NVFP4 cookbook run

Issue #41919 created 19:10:43 UTC. It contributes a pinned single-B200 TP1 benchmark set and a full 1,319-question
GSM8K greedy/no-thinking evaluation. This is useful as a datacenter reference, but the hardware/runtime/quant are too
different for consumer TG/PP transfer.

## Strict-window negative scan

DASLab Flash-Next GSQ-RCO commit history remains at `ed59f92`; no new checkpoint/allocation/benchmark landed after
the prior boundary. citeturn722447view0

No Project-51-relevant strict-window change was found in TurboQuant-MLX, MoEspresso, mlx-serve or Ishizuki. MLX
itself has no new commit in the window. llama.cpp's new changes are unrelated to the P51 Flash-Next target.

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

**2026-09-30 20:42:47 UTC**
