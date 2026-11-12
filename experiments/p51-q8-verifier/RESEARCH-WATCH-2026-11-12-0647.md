# Project 51 strict research watch — November 12 2026 06:47 EST

**Previous cutoff:** 2026-11-12T03:49:45Z. **New strict cutoff:** 2026-11-12T11:47:29Z. Sources below are FRESH or UPDATED inside window unless explicitly labeled older. Primary GitHub issues; not an exhaustive Hugging Face or release scan. No owner hardware work, downloads, tests, installs or inference-code changes.

## HIGH — FRESH Basalt MACaQ format incompatibility
[Basalt issue #333](https://github.com/jesdga95/basalt/issues/333) analyzes Huawei MACaQ source and Basalt converter. MACaQ-R is a code-only refinement of existing Q4_K/Q5_K/Q6_K GGUF and **should** convert unchanged, **untested**. Full MACaQ MoE uses per-linear/per-expert pre_scale D1 and Hadamard64 on activation; Basalt's converter does not honor those metadata/tensors, may silently convert and serve **incorrect logits**. Require explicit rejection until native transform is supported, then BF16 reference parity, KLD and agent-task acceptance. Full Flash-Next MACaQ currently ~125GB recipe with Q8 PLE, no sub4-bit IQ3XXS/S. No Flash-Next MACaQ or MACaQ-R published in issue. This is a format warning, not MACaQ quality validation.

## HIGH — UPDATED OLD Kapitsa Bolt LiLiCorr correctness issue appears fixed
[Kapitsa issue #1150](https://github.com/nace-ai/kapitsa/issues/1150), created Nov10 and updated/closed Nov12. Earlier Kapitsa0.2.31/0.2.33 with Bolt74B+LiLiCorr produced off-topic 0/8 with draft, 11/12 without. **Important resolution:** reporter tested Kapitsa **0.2.35-rc1** on same M5 Ultra/macOS27.0.1 and got **8/8 in each of 11 legs**, including default drafter. One first-start anomalous result was not reproduced. Issue CLOSED; don't present as still unresolved. Not a QFN/M1 direct benchmark; retain regression gate for speculative decoding correctness.

## MEDIUM — FRESH oMLX multiagent long-context MTP
[oMLX #5186](https://github.com/jundot/omlx/issues/5186), Nov12 08:21Z. Experimental deferred ragged rollback realignment opt-in OMLX_DEFER_REALIGN=1 for concurrent native MTP requests, Qwen3.8-27B oQ8 on **M5 Max**, paired 24.7K+100.7K contexts **30.6→40.8 TG**, 78.1K+100.3K **28.9→42.1 TG**; paired needle recall 8/8 and 16 tests. Proposal/open, not M1 Max, not QFN, no demonstrated general agent throughput; strong signal for HaikuSwarm multi-session scheduling.

## MEDIUM — FRESH Splash dispatch overhead proposals
[Splash #754](https://github.com/incoai/splash/issues/754) eliminate draft-attention layout-copy dispatch while preserving BF16 reduction order. [Splash #755](https://github.com/incoai/splash/issues/755) reduce command-graph parameter/literal-binding allocations. Both proposals, no verified M1 Max gains.

## Retained baseline / priority
Last watch: Kapitsa M1Max dense27B ANE PP1.40–1.76x experimental with changed greedy outputs; Ornith1.5-35B-A3B M1Max 101–103 TG no draft, up to198 TG favorable speculative but divergent text; Q5 KQuant catalog no M1 benchmark; Basalt Windows long-agent hang #325 unrelated to frozen owner first test; QFN original GSQXXS historical DS4 at 128K PP278/TG34.2 and 259K PP258/TG31.7. No new verified official downloadable Qwen4 Flash-Next or 27B in this GitHub-focused scan. Keep Qwen4/4.5 Flash-Next post-training refresh **speculation**, not roadmap.

**Owner setup:** two independent 2021 M1Max64; RTX5070Ti16+64GB. Quality floor original GSQ IQ3XXS, IQ3S preferred. Frozen Basalt first run original GSQ IQ3S, true32K, INT8KV, one slot, spec1 no draft, parity and coding tool quality; HIGH approval before hardware actions. Relay CUDA prefill→Metal decode requires KV/recurrent state parity and measured transient VRAM. No silent quant/engine swaps.

**NEXT STRICT CUTOFF 2026-11-12T11:47:29Z.**
