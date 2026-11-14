# Project 51 research watch — November 14, 2026, 12:33 EST

Prior strict cutoff 2026-11-13T17:44:04Z. New cutoff 2026-11-14T17:33:51Z. Targeted GitHub issue updates and Qwen official release search. Research-only; no hardware experiments or inference-code edits. Issues marked UPDATED may predate cutoff.

## Priority 1 — M1 Max DFlash2 concurrency counterexample (UPDATED)
[oMLX #4935](https://github.com/jundot/omlx/issues/4935), updated Nov14 13:14Z. M1Max32GPU64GB, Qwen3.6-35B-A3B oQ4e, 8K prompts, 512 output, oMLX0.7.3rc1: aggregate tok/s 1/2/4 requests: no spec 86/105-106/123-124; DFlash2 adaptive 68-72/95-105/112-123; DFlash2 fixed 62-63/48/56-59; fixed MTP depth3 78/74-75/72-74. 24/24 valid tool-call JSON across arms on main retest. DFlash2 not automatically faster; fixed verify concurrency trap. Different model/engine/quant from Paperniuk DS4 QFN; cannot extrapolate direct.

## Priority 2 — RDNA2 expert PCIe calibration (UPDATED)
[Strata #4007](https://github.com/Niko1221/Strata/issues/4007), updated Nov14 15:40Z. RX6900XT gfx103x QFN IQ3S, Windows i9-10900K PCIe3 x16: default 35.4/35.5 @4K, 37.1/34.8 @32K versus refined 42.6/42.5 and43.8/44.0. Linux Ryzen5600X PCIe4 x8 smaller ~1-2% gains. Tunable GPU expert share from 0.35 to 0.20. Not measured on user's RX6800; user secondary 16GB host RAM remains limiting.

## Priority 3 — cache handoff support (FRESH)
[oMLX #5264](https://github.com/jundot/omlx/issues/5264), updated Nov14 17:16Z; PR #5265 live additive SSD cache rescan for out-of-band blocks.
[oMLX #5266](https://github.com/jundot/omlx/issues/5266), updated Nov14 14:21Z; PR #5267 opt-in prefix block hash chain for verifying receiver cache handoff. Neither is cross-runtime CUDA→Metal KV + recurrent-state parity; proposals not proven merged.

## Priority 4 — Anthropic tool adapter (FRESH)
[Strata #5952](https://github.com/Niko1221/Strata/issues/5952), updated Nov14 14:32Z: Claude Code tool_addition blocks within system messages silently dropped from Anthropic-compatible conversion; local reproduction 0.2.13.1 and 0.2.12; static main check unverified. Not model IQ3S quality; agent tool coverage failure.

## Other followups
[Kapitsa #1234](https://github.com/nace-ai/kapitsa/issues/1234), updated Nov14 04:25Z: DFlash2 T0 greedy drift vs plain on 35B MoE; M1Max32 Ornith teacher-forced top1 agreement 98.96%, 2 flips; quality consequence unknown. Retain parity gate.
[Kapitsa #1194](https://github.com/nace-ai/kapitsa/issues/1194), updated Nov14 02:48Z: M1Max32 27B 4bit opt-in ANE split 4K prefill 129-134→225-236 tok/s (1.7-1.76x); 16K 124→173 (1.4x), decode unchanged, numeric 0.77-0.89% and 2/2 greedy wording changes. Not quality-cleared.
[Basalt #339](https://github.com/jesdga95/basalt/issues/339), updated Nov14 11:11Z: 5070Ti+5060Ti 64GB host QFN official NVFP4-DQ8 0.3.2 OOM or 30sec RAM guard; not owner's frozen single 5070Ti original GSQ IQ3S test.
[Splash #768](https://github.com/incoai/splash/issues/768): M5 user claims Bonsai-2 27B ternary ~50 tok/s versus Qwen3.6-35B-A3B ~150; unverified user report, model mismatch.
Paperniuk [DS4](https://github.com/paperniuk/ds4/tree/m1-flash-next) most recent commit remains 9da1288 Nov12 21:28Z; [Splash M1](https://github.com/paperniuk/splash) latest d61103e Nov12 11:20Z. No new DFlash2 vs MTP at 128K M1Max64 in targeted check.

## Qwen4 release status
Official [QwenCloud changelog](https://docs.qwencloud.com/changelog/models) confirms qwen4-max-preview Nov11 Token Plan only; no verified Qwen4-Flash or Qwen4-27B open weights. Distinguish cloud preview from local model availability. No new original GSQ quant release established in this targeted scan.

## Owner priorities / frozen controls
Two independent M1Max64 32GPU; RTX5070Ti16 64GB RAM; secondary RX6800 16VRAM 16GB RAM. Original GSQ IQ3XXS minimum, IQ3S preferred. 128K-262K; quality/tool correctness above speed. Frozen first Basalt experiment original GSQ IQ3S true32K INT8KV 1 slot spec1 NO DRAFT. Relay CUDA→Metal KV/recurrent state unverified. HaikuSwarm Molt context budget. No experiments, model downloads, CI, or code edits authorized.

NEXT CUTOFF 2026-11-14T17:33:51Z.
