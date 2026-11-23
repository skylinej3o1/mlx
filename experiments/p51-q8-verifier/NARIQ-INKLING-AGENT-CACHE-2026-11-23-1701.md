# Project 51 focused note — November 23, 2026 17:01 EST: Agent-state semantics, NariQ dense27B and PC realities

[Strict dated watch](./RESEARCH-WATCH-2026-11-23-1701.md). Window `2026-11-23T13:22:45Z`→`2026-11-23T22:01:00Z`. Research-only.

## Why this window matters

Three independent sources converge on **agent history fidelity** as a throughput limit distinct from kernel speed:

1. **Strata Inkling Metal** [#6914](https://github.com/Niko1221/Strata/pull/6914) + [#6827](https://github.com/Niko1221/Strata/pull/6827): on M5Pro48 SQ15, tools break exact prefix replay and Metal lacks native checkpoint. Both fixes are required for tool-turn 7,716/7,771-token reuse and 7.97→0.94s TTFT; 3-turn Cline agent 408.5→154.8/145.7s, same task outcome. Open, one slot, ~170MiB cached state. Fails to extrapolate to M1 until compiled/correct at occupied deep context.
2. **Splash upstream** [#808](https://github.com/incoai/splash/pull/808): supersede disposable earlier states; reply-resume rose ~29–36% to86–93% on M5Max SWE-bench sample, TTFT ~277/282→210/178ms; solved counts variable19/17 vs16/18, not a quality boost. Cache state is a resource with lifecycle, not just an LRU hit counter.
3. **oMLX SSD** [#5588](https://github.com/jundot/omlx/pull/5588): prevent in-flight obsolete SSD block writes from silently replacing newer state. Baseline regression fails eight injected races; patched 402 focused tests pass. For Molt, a successful restore must match exact prefix/cold output and file semantics, not merely a log of tokens cached.

## NariQ position (old November20 release newly documented)

[NariQ paper](https://arxiv.org/abs/2611.26157); [weights](https://huggingface.co/nari-labs/Qwen3.8-27B-NariQ-GGUF); [fork](https://github.com/nari-labs/nari-llama.cpp). NariQ is a **distinct dense27B**, trellis-code quant calibrated on agent traces, and developers report BF16 39.8% DeepSWE/62.6 Terminal2.1 vs3-bit 41.0%/63.8 in their own Claude Code benchmark; 113 DeepSWE tasks×3, 82 Terminal tasks×3. See detailed watch for 2.5 and2-bit. Developer source has M3Pro 3bit only3.8tok/s, no other M1 result, no optimized GeForce verification, no KV quant, no native MTP, ~30GB for262K, and no independent published replication. Keep candidate on radar; do not replace minimum pristine sparse original GSQ IQ3_XXS. NariQ vs GSQ KL in paper is **dense** comparison, not QFN.

## A matched-chip-name fallacy with actual 5070Ti

[Basalt merged #634](https://github.com/jesdga95/basalt/pull/634) publishes one RTX5070Ti16 **NVFP4 QFN** community-1 score: PP16K4739.7,PP64K5116.4, aggregate TG167.7, conversation124.7, structured186.5, prose128.0; Intel285K,127GiB,Windows,max-context66661 and draft active. The frozen own PC first trial is Intel265F,64GiB,Linux, historical pristine ISTA IQ3_S pack/PLE, physical32K INT8, `spec=1` NO DRAFT: no comparison or forecast transfer. [Basalt #629](https://github.com/jesdga95/basalt/pull/629) fixes structured repeated nonstring tool args but remains OPEN, hence must be an explicit correctness gate. [Basalt #632](https://github.com/jesdga95/basalt/pull/632) thinking-budget answer-header fix also OPEN.

## Metal and AMD hardware reality

[oMLX #5586](https://github.com/jundot/omlx/pull/5586) looped Mini BF16 fused control gives M3Ultra single-token 22.33→19.25ms without M1 test; [#5585](https://github.com/jundot/omlx/pull/5585) small-verify attention M3Ultra8K 8-row46.7→43ms, different kernel. [oMLX #5511](https://github.com/jundot/omlx/pull/5511) corrected M5Pro 96K Inkling FP8 KV trade: -25.7% PP, +23.0% decode, peak memory23.2→20.5GB, quant loses top1, not an automatic win for M1. [Strata #6879](https://github.com/Niko1221/Strata/pull/6879) HIP 1024 ring overwrite on newer Radeon gfx1201 quant breaks attention; not proven on one RX6800 gfx1030/16GB host. [#6885](https://github.com/Niko1221/Strata/pull/6885) fixes a specific **Hy4Flash** M1Max shader compile bug, not old-M1 Inkling. Best established M1 original QFN GSQ physically128K PP278/TG34.2 and259K PP258/TG31.7 remains historical. Spring central forecast unchanged.

## Decision gates

- Track **correct completed coding tasks/hour** over 16/32/64/128/259K physical context; include prefill, replay, failures, tool parser, 24hr memory, and crash restoration.
- Do not claim source code merge, benchmark or system change on owner's rigs.
- No full GSQ CUDA→Metal Relay, no new accepted M1 quality/throughput benchmark, no official downloadable Qwen4 Flash/27B manifest. Two independent resident M1Max64 agents remain the baseline architecture.
