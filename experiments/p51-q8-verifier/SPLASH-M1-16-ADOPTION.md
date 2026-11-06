# Splash 1.6.0-m1 — 2021 M1 Max adoption safety and new Flint alternative

Source update at 2026-11-06T17:40:53Z; [strict watch](./RESEARCH-WATCH-2026-11-06-1240.md). Documentation ONLY: no approval for install/run/download/model replacement.

## Official release and physical numbers

[Paperniuk unofficial fork 1.6.0-m1](https://github.com/paperniuk/splash/releases/tag/1.6.0-m1) published **2026-11-06T14:39:26Z**. M1/M2 port of upstream Splash1.6 memory policy plus native Flint heads, gate/up fused and hyper-connection norm, ANE short prefill tune. Upstream official Splash M3+; M1 fork maintained independently. New source requires tests before adoption.

[Release's M1Max64 400-token greedy ABBA](https://github.com/paperniuk/splash/releases/tag/1.6.0-m1): source QFN **Q2_0** one-lane79.1→78.7 TG, two-lane **AGGREGATE**98.4→97.6 TG, cold16.7K PP426→428; Qwen3.8-27B MLX4bit 54.7 one /60.4 agg and PP201, UD-Q5_K_M 46.7 /53.8 and PP186. **Not owner original GSQ IQ3_XXS/S** and unreported actual deep decode context. Do not present as production-quality or per-agent 97.6 TG.

**Existing Flint40B-A2.5B** in [new native M1 fork](https://github.com/paperniuk/splash/pull/40), Unsloth Flint UD-Q4_K_XL and DFlash2 on M1Max: **77TG one lane /94TG aggregate2 lanes /822PP at16K**, context256K *supported/configured, NOT physically 256K occupied decode proven*, unverified relative xHigh coding quality and tool output correctness. Excellent secondary-worker candidate after owner HIGH, not floor replacement.

## Current red blocker

[Issue #51](https://github.com/paperniuk/splash/issues/51) **FRESH created16:22Z**: 1.6.0-m1 with one MoE Unsloth IQ1S GPU family8 hangs when warm final-prefill tail 17–32 rows, leads watchdog30sec and HTTP503; **independent exact M1Max24GPU/64GB** release-hash matched pure MLX4bit MoE+DFlash2 **input7 new rows pass3/3, input23 rows hang2/2**; 1.5.0-m1 same23 row finishes0.55s. Issue independent comment **17:34:37Z**, within watch window. Root cause likely small tail scheduling or kernel dispatch but NOT demonstrated; mixed quant sole explanation ruled out. Not shown on owner's32GPU unit yet, do not claim all M1 models broken. Priority fix plus hardware-approved A/B tiny prompts and multi-turn agent actual executed tools before adopting. **Do not install or auto-update owner Macs**.

## Preexisting source IQ3S M1Ultra deep benchmark (rediscovered Nov6, published Nov4)

[Issue #47](https://github.com/paperniuk/splash/issues/47) M1Ultra48GPU128GB original GSQ IQ3S, source both shards byte exact DFlash2, SSD PLE resident2GB: actually 1K51TG/672PP;16K36.5/718;64K34.6/643;131K35.7/627;192K34.0/625, 2 repetitions with wide variance. 262K selftest times out at120sec. M1Ultra has twice system memory and more GPU/bandwidth than owner M1Max; cannot infer target 128/262K IQ3S one64GB all resident. Shows PLE can stream without measurable slowdown **on that 128GB host**.

## Explicit gated test design (PROPOSED ONLY)

1. Verify precise model source, checksum, metadata, GGUF experts and original PLE IQ4NL, desired GSQ IQ3XXS and eventually IQ3S. No Q2 substitution permitted for acceptance.
2. Tiny new-row cold/warm 1/7/16/23/31/32/33/64/128, all API dialects, thinking on/off, tools and xHigh multi-turn. Crash/hang/HTTP503 is fail even if TG appears better.
3. Actually fill 16K→64K→128K→262K where memory admits. Report resident/wired/compressed/free/swap, SSD read, KV spill/restore, Apple GPU time; PLE source formatting.
4. Compare correctness and executed tool artifacts on identical frozen heldout tasks with original Paperniuk DS4, not just speculative accepted tokens and headline output TPOT.
5. For multi-agent two independent Mac nodes vs one split pipeline, quantify both-done wall and fair small-turn TTFT, never multiply per-lane throughput. Any hardware/CI requires explicit HIGH approval.

**Owner physical source baseline HOLD:** original pristine IQ3XXS DS4 128K278PP/34.2TG and259K258PP/31.7TG. All original IQ3S high long targets unmeasured. No device action.
