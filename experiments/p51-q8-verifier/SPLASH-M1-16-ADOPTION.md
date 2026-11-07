# Splash 1.6.0-m1 — 2021 M1 Max adoption safety and new Flint alternative

## November 6 2026 23:34 EST — source patch endurance and upstream 1.6 prefix cache loss

[Strict watch](./RESEARCH-WATCH-2026-11-06-2334.md) cutoff 2026-11-07T04:34:41Z. Splash fork [PR #52](https://github.com/paperniuk/splash/pull/52) updated **22:54:35Z** with an extended real agent session on contributor's **Unsloth UD-IQ1_S** patched branch: **2.5h,200 requests, ACTUAL up to236K context**, main+two subagents, **27 requests with 17–32 final prefill rows**, zero engine failures or restarts. On prior M2Max source Q2_0/UDIQ1S thirty-request regression each passed, a stock release hung with28-tail; **PR OPEN, no new packaged tag** as of cutoff. Hardware for new extended run not explicitly exact owner2021M1Max32GPU, and successful finished coding tasks not externally audited. No owner install/test authorization; release adoption remains blocked for pristine original GSQXXS/3S until published patched M1 binary and owner HIGH-gated acceptance.

Separate [upstream Splash #706](https://github.com/incoai/splash/issues/706) **FRESH03:24Z** M5Max ohmypi 1.6.0 QFN agent input180830 cached179360 followed by input181614 cached **only14528** -> **164832 fewer prefix tokens reused**, repeated memory claims; downgrade1.5 report appears better. Author reports symptom, no confirmed root cause or independent repro, and not proof the M1 fork same path. **Add explicit prefix retention parity in 128/262K multiagent tests** and memory pressure/SSD read context. The upstream 1.6 broad 1.27× throughput M5 case is prior, not a guarantee of warm-turn reliability.

# Splash 1.6.0-m1 — 2021 M1 Max adoption blocker progress

**New checkpoint 2026-11-06T22:39:45Z**. [Strict watch](./RESEARCH-WATCH-2026-11-06-1739.md). All test cases below are **proposed** for owner, NOT authorized or run.

## Updated status, November 6 17:39 EST

- Original [Splash unofficial M1/M2 1.6.0-m1](https://github.com/paperniuk/splash/releases/tag/1.6.0-m1) release published **14:39Z**, source first report [#51](https://github.com/paperniuk/splash/issues/51) created16:22Z and **independent M1Max24GPU actual 23 new-row hang** already recorded in prior watch. New [#52](https://github.com/paperniuk/splash/pull/52) **created17:47:25Z, OPEN at cutoff**, patch restores per-segment instead of one fused `gguf_decode_mma_fused_m32` dispatch on Apple GPU family7/8 at prefill <=32 rows; specifically **17–32 final chunk problematic**.
- Fresh evidence **M2 Max** original **ISTA GSQ Q2_0** incremental new1052 tail28 hangs on stock 1.6.0-m1, succeeds2.3s patched. Both GSQ Q2_0 and **Unsloth UD-IQ1_S** 30/30 warm sequence pass at patched PR head, `gguf-projection` and `linear-plan` Metal tests with/without shader validation passed. PR author's confirmed UD IQ1S run20:19Z; proposed fix not merged/published as of request.
- Fresh [#51 21:49Z comment](https://github.com/paperniuk/splash/issues/51#issuecomment-6696652020) reports different **M1 Max64 Qwen3.8-27B Q8** using oMLX/Splash1.6.0-m1 first turn succeeds, next hangs, while native oMLX MTP succeeds. No evidence that this different bug is definitely same dispatch defect; independent release safety blocker.
- Earlier release **M1Max64 QFN Q2 78.7 tok/s one-lane, 97.6 two-lane AGGREGATE,16.7KPP428** still not source original GSQXXS/S. Earlier Flint40B UD-Q4_K_XL M1Max **77TG single,94TG two-lane AGGREGATE, PP82216K**, 256K context support **NOT actually occupied**. Flint remains optional SECONDARY after quality proof.
- Existing [Paperniuk Splash #47](https://github.com/paperniuk/splash/issues/47) original GSQ IQ3S 2022 **M1Ultra48GPU128GB** actually192KPP625/34TG and 262K boot selftest TIMEOUT is PRIOR REDISCOVERED evidence, **not owner32GPU64GB fit proof**.

## Blocker exit criteria (only proposed)

1. Fix merged to specific tagged M1 1.6 revision and binary SHA, independent **24/32GPU M1Max** as well as M2Max confirmation.
2. Cold and warm new added rows 1/7/16/17/23/28/31/32/33/64/128 and mixed quant and homogeneous MLX/Original source; no hung HTTP503 or silent failure; verify complete API tool JSON responses.
3. Native original **ISTA GSQ IQ3_XXS acceptance floor** hard xHigh agent tasks actual128/259K, compare previous physical Paperniuk DS4 **278/34.2** and**258/31.7**; before source IQ3_S high quality test, confirm 64GB memory swap and KV cache.
4. With two independent Macs, compare 2 agent lanes vs split one model; no x2 memory illusion or per-lane vs AGGREGATE throughput mistake.
5. No downloads/installs/builds/CI/hardware until separate HIGH approval. **Adoption blocked at cutoff, despite promising PR**.

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
