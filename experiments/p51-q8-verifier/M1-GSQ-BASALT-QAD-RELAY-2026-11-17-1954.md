# Project 51 technical focus — Nov 17, 2026, 19:54 EST

[Full strict watch](./RESEARCH-WATCH-2026-11-17-1954.md). Evidence window 2026-11-17T13:50:06Z→2026-11-18T00:54:00Z. Documentation/research only, no owner GPU/CI, downloads or model changes.

## 1. M1 source quant format is the critical speed gate

New Paperniuk [#69](https://github.com/paperniuk/splash/pull/69) and [#70](https://github.com/paperniuk/splash/pull/70) OPEN on Apple7 M1 Splash1.6.1 fork, not upstream1.7 port: **dense Qwen3.8-27B MLX affine4** 32GPU M1Max32GB, #70 B1 decode GPU step -4.74%, #69 -1.19%. #70 shifted greedy transcript in five of eight. Nov17 22:30 reviewer M2Max gets dense MLX4 improvement but **GGUF IQ3_XXS output projection +2.0% slower B1 and +2.3% B2; Q8_0 +5.4% slower B1**. #67/#68/#71 CLOSED UNMERGED. Therefore do not claim original QFN ISTA GSQ IQ3_XXS improves. Historical genuine physical128K PP278/TG34.2, 259K PP258/TG31.7 near57GiB M1Max64 unchanged; forecast unchanged. Needed: restrict affine optimization to affine-only so it does not slow GSQ mixed quant; source GGUF long-context logits and complete tools/agent checks require HIGH approval.

## 2. 5070 Ti Basalt first-run frozen source and NVIDIA QAD are NOT substitutes

[Basalt #412](https://github.com/jesdga95/basalt/pull/412) on RTX5070Ti16 Windows with **112GiB host RAM** and self-converted ISTA IQ3_S default community drafting: PP16K3752,65K4303 and weighted TG135.9; 38.2GiB pinned host expert copy. Owner has64GB host and frozen **original pristine GSQ IQ3_S historic v2 Basalt package, exact source/PLE SHA, physical32K, slot1, INT8KV, spec1 NO DRAFT**, CPU-double and actual coding-agent tool validation. No replacement of that setup.

Fresh [NVIDIA QFN NVFP4-QAD](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-NVFP4-QAD) with merged [Basalt converter #406](https://github.com/jesdga95/basalt/pull/406): author 122.6GiB converted pack, 100-step distillation, PPL3.3022→3.1547 (-4.5%) but BF16 KL0.0620→0.0831 (+34%) and top1 91.70→90.64%. Not a better original quant just because PPL improves; no completed-agent proof or owner single64GB residency. #411 other5090 loader A/B shows no universal startup speed gain, and #414 4-GPU scheduling is not one-card improvement.

## 3. CUDA helper still not original Splash GGUF and Relay remains harder

oMLX helper does partial early-layer CUDA prefill for native MLX weights. GSQ-RCO IQ3_XXS/S is original GGUF on **external Splash engine**. [oMLX #5369](https://github.com/jundot/omlx/pull/5369) achieves ~6% true128K cold TTFT gain on OTHER M5Pro dense27B MLX8, no GSQ/M1/5070Ti. [#5384](https://github.com/jundot/omlx/pull/5384) SSD NVFP4 PLE path for a converted98GiB QFN specifically refuses CUDA helper; that native model exceeds M1Max64. Complete Relay still requires exact attention KV/indexer, GDN recurrence, PLE, MTP draft, prefix/tokenizer/sampling state transferred to Metal; cannot claim working. Research helper first, keep full Relay strategic option.

## 4. Multi-agent quality and cache identity

[Splash #781](https://github.com/incoai/splash/pull/781) backport eight-agent p95 TTFT19.787→1.291s, but trusted coding checks17/24 both and aggregate rate a bit lower. [#706](https://github.com/incoai/splash/issues/706) new analysis of 180K GSQ cache misses implicates client-mutated image/tool/prompt history around 15K, not all engine eviction. HaikuSwarm Molt must journal immutable rendered prompt/image/tool hashes, runtime exact cached state, idempotent retries and proof of action completion. [Strata #6171](https://github.com/Niko1221/Strata/issues/6171) other patched runtime warm+route-prior premature end behavior 10/137 is a correctness warning, not independent global backend ranking. Optimize correct completed coding tasks per hour, not PPL/TG/TTFT alone.

## 5. Qwen4 and two-Mac expectations

No verified official Qwen4 compact Flash/27B/~35B-A3B weights or size. Qwen4-Max Nov16 cloud is previous state; llama.cpp qwen4exp labels denote QFN engine family, not fresh Qwen4 model. Two 2021 M1Max64 are separate 64GB domains, and earlier dual M5Ultra256GB split-prefill replicated-decode cannot be extrapolated. No actual new owner throughput; no 3–5 simultaneously reliable agent demonstration. Separate HIGH approval for any hardware tests, runtime/model installations, config or source changes.
