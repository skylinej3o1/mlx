# Project 51 strict research watch — November 12 2026 11:15 EST

**Previous cutoff:** 2026-11-12T11:47:29Z. **New strict cutoff:** 2026-11-12T16:15:53Z. Distinguish FRESH issues from UPDATED older issues. GitHub primary source scan Kapitsa/Basalt/Splash/oMLX/Strata and public Qwen4 release search. No hardware tests, installs, downloads, CI or code changes.

## HIGH FRESH — Basalt Flash-Next IQ3_S agent tool-turn noncompletion
[Basalt #334](https://github.com/jesdga95/basalt/issues/334), created Nov12 12:35Z. Linux RTX5080 16GB, custom converted Qwen3.8-Flash-Next IQ3_S, Basalt v0.3.2 vs Strata0.1.59 same machine/prompts/weights (different converters), max-context262K, INT8 KV, Basalt default spec8. Basalt defaults: output ceiling hits **14/24**, empty assistant finals **10/24**, tasks passed **18/24**; reasoning capped8192: 12/24, 7/24,20/24; Strata: ceiling0/12, empty1/12, passed11/12. Tool calls valid but loop instead of finalizing; no evidence our original GSQ IQ3_S spec1 frozen run will fail. Add agent-turn close / bounded tools / final response acceptance, keep frozen first-run settings.

## HIGH UPDATED OLD — Splash long-context capacity bug FIXED in 1.6.1
[Splash #713](https://github.com/incoai/splash/issues/713) originally Nov7, updated/closed Nov12. On another Apple64GB QFN GSQ IQ3XXS, Splash1.6.0 auto expert floor caused capacity_exhausted >~30K; same reporter confirmed Splash1.6.1 default auto successfully completes ~201K and ~220K input with KV spill/restore. No M1 Max exact speed inference. Avoid repeating outdated 'still broken' claim.

## MEDIUM FRESH — Splash multi-session memory admission issue
[Splash #758](https://github.com/incoai/splash/issues/758) created Nov12 13:28Z. M5Pro64GB Splash1.6.1, 2–3 independent ~245K contexts. Second Start lane-state claims wait 12–34s due memory governor. Flint3 sessions stock31.6 TG combined vs patched/flags ~57.7–61.5, but model-specific. Qwen3.8-27B2 stock22.9 TG, local patch ~23–26.2, remains memory-bound. Not QFN, not M1, not merged. Supports HaikuSwarm admission/latency tests.

## MEDIUM FRESH — Strata Flash-Next vision UI screenshot benchmark
[Strata #5872](https://github.com/Niko1221/Strata/issues/5872), created Nov12 16:13Z (2min before cutoff), 2xRTX3090, QFN Gyro-M-TQ2_0, nonofficial engine build. 6144 picture tokens vs2048 improved 38-fact real UI score F16 33→34.5 at higher cost; Q8 projector36 real facts but worse dark probes; no monotonic F16/Q8/Q6/Q4 quality ranking. All 5 variants passed 9/9 light synthetic but missed 3–4px dark card shifts/baselines. Relevant to Playwright visual-agent QA, NOT text coding/our GPUs.

## UPDATED older — M1 Max ANE still opt-in, quality gate
[Kapitsa #1194](https://github.com/nace-ai/kapitsa/issues/1194) maintainers request matched greedy text or logit dump on two setups before default M1–M3 enable. Original 4K dense27B ANE prefill1.70–1.76x on M1Max32GB, 16K1.40x, wording changes 2/2. No new independent M1Max64 validation.

## Qwen4
Public Nov12 search: Qwen4-Max Preview still API-only temporary access; no verified official open Qwen4 Flash-Next/27B or 35B checkpoint. Qwen4/4.5 Flash-Next posttrained refresh is user hypothesis, not verified. No basis to reassign a Qwen4Exp architecture tag to a released model.

## Retained baseline
Two independent M1Max64; RTX5070Ti16+64GB. QFN original GSQ IQ3XXS quality floor, IQ3S preferred. Original XXS historical 128K PP278/TG34.2,259K PP258/TG31.7. Basalt first run frozen pristine original GSQ IQ3S pack true32K INT8KV one slot spec1 NO DRAFT with PLE/source numerical parity, tools and coding gates; HIGH approval before owner hardware actions. Relay CUDA prefill→Metal decode requires exact KV/recurrent-state compatibility, transient VRAM and fallback. Ornith35B M1Max short TG101–103 no-draft/up to198 favorable speculation unverified hard agent. Dense27B Q5KQuant, MACaQ still research.

**NEXT STRICT CUTOFF 2026-11-12T16:15:53Z.**
