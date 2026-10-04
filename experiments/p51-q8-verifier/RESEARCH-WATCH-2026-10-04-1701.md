# Project 51 research watch — 2026-10-04 17:01 ET

Freshness boundary entering: **2026-10-04 18:00:16 UTC**
Cutoff: **2026-10-04 21:01:52 UTC**

## Decision

**No headline TG/PP target movement and no Flash fit/admission/stability-prior movement.**

This pass materially changes implementation priority in two places:

1. **Dense-27B fleet:** promote a one-time **RTX 5070 Ti cold-prefill -> M1 Max ownership handoff** to a formal
   Project-51 lane. The 5070 processes the initial large prefix, exports complete continuation state once, the M1
   imports it and becomes the sole session owner. Continuous cross-node decode/disaggregation remains out of scope.
2. **RX6800 producer:** exact gfx1030 evidence plus a near-chip IQ3_S prompt-kernel result materially strengthens the
   RX6800 cold-prefill experiment. It is now a high-priority producer lane, but receives no numeric PP credit until
   exact RX6800 + target IQ3_S is measured.

The strict hard boundary advances to **2026-10-04 21:01:52 UTC**.

## NEW — Strata #815/#816: exact RX 6800 / 64-GB Windows regression receipt

PR:
https://github.com/Niko1221/Strata/pull/815

Issue:
https://github.com/Niko1221/Strata/issues/816

Created **2026-10-04 18:51 UTC**.

Exact hardware:
- RX 6800 16 GB / gfx1030;
- Ryzen 7 5700X3D;
- 64 GB DDR4-3200;
- Windows 11;
- ROCm 10.2.0a;
- Flash-Next at 128K.

0.1.39 regressed decode versus 0.1.38 by roughly 12-22% depending workload. Disabling the new shared-expert
second stream with `STRATA_SH_STREAM=0` not only removes the regression but beats 0.1.38 in the measured rows.

Representative IQ2_XS:
- 0.1.38 English / Ukrainian / code: ~50-55 / 41-42 / 56-57 TG;
- 0.1.39 default: ~42-43 / 32-33 / 49-50;
- 0.1.39 + SH_STREAM=0: ~54-57 / 43-44 / 60-63.

IQ3_XXS + Cyrillic draft vocab on the fixed configuration:
- ~49 English / 55 Ukrainian / 52 code TG.

Prompt at ~30K remains ~311 PP in these arms.

Project-51:
- exact gfx1030 is now demonstrably viable on current Strata;
- default 0.1.39 is a bad RX6800 comparator unless the HIP shared-expert fork is disabled/fixed;
- no IQ3_S target-number transfer yet.

## NEW — Strata #826: HIP shared-expert stream regression root-caused

PR:
https://github.com/Niko1221/Strata/pull/826

Created **2026-10-04 19:55:51 UTC**.

The shared expert was forked onto a second stream by default. That overlap helps CUDA but the cross-stream event cost
can exceed the shared-expert work on HIP.

R9700 / gfx1201 / 48K prompt:
- stock 0.1.39: **43.4 TG median**;
- fork off by default: **62.9 TG**;
- forcing SH_STREAM=1 reproduces ~43.5;
- forcing SH_STREAM=0 reproduces ~63.0;
- 4/4 greedy output checks identical.

Project-51:
- HIP defaults must be backend-specific;
- exact RX6800 qualification uses SH_STREAM=0 or a build containing the fix;
- no CUDA transfer.

## NEW — Strata #835: RDNA2 prompt path can nearly double with FP16-output GEMMs

PR:
https://github.com/Niko1221/Strata/pull/835

Created **2026-10-04 20:47:24 UTC**.

One RX 6900 XT / gfx1030 / IQ3_S:
- 9.4K: **439 -> 744 PP** (+69%);
- 34.7K: **466 -> 915 PP** (+96%);
- 105.8K: **461 -> 926 PP** (+101%);
- decode unchanged ~44-48 TG.

Two RX6900XT layer split:
- 8.3K: 444 -> 833 PP;
- 33.6K: 707 -> 1,356 PP.

The change exploits rocBLAS's much faster FP16-in/FP16-out kernels on gfx103x. Reported teacher-forced comparisons
move closer to the higher-precision reference on the tested corpus; 15/15 needle recall passes in both arms.

Limits:
- RX6900XT is same gfx1030 family but not exact RX6800;
- exact target artifact / exact Linux RX6800 is unmeasured;
- prefill arithmetic changes, so full Project-51 quality/state equivalence remains required.

Project-51:
**RX6800 cold prefill is now a high-priority experiment rather than a speculative side lane.**
Do not assign a numeric RX6800 PP target until the exact card is tested.

## NEW — Strata #832: exact 5070 Ti + 64-GB Windows Flash IQ3_S through 164K

PR:
https://github.com/Niko1221/Strata/pull/832

Created **2026-10-04 20:30:40 UTC**.

Exact broad target box:
- RTX 5070 Ti 16 GB;
- 64 GB host RAM;
- Windows 11;
- DASLab Flash-Next GSQ-RCO IQ3_S;
- max context 262144;
- Q4_0 KV, 32768 resident;
- MTP spec4, min-p .70;
- 0.1.39 release.

Measured medians:
- ~5.2K: **3,012 PP / 75.8 TG**;
- ~41.4K: **3,487 PP / 74.7 TG**;
- ~131.2K: **3,523 PP / 82.8 TG**;
- ~164.1K: **3,442 PP / 79.6 TG**.

Important classification:
- this is **Flash-Next**, not dense 27B;
- it proves strong exact-box Flash prefill through 164K;
- it does **not** transfer 3.5K PP to the dense-27B session-launcher lane;
- it does not prove a filled ~250K prompt on the target 64-GB Windows box.

No fit/admission/stability prior moves.

## RECOVERED OLDER EVIDENCE — exact RTX 5070 Ti dense-27B CUDA v3

Source:
https://github.com/feveromo/recipes-qwen3.8-27b-5070ti

Verified **2026-09-28**; absent from the current canonical v2 summary.

Exact RTX 5070 Ti / Qwen3.8-27B GSQ-RCO IQ3_S + embedded MTP, custom llama.cpp v3:
- real agent sessions: **147.2 TG / 2,177 PP**;
- 15.7K: **109.6 TG / 2,200 PP**;
- 62.5K: **99.7 TG / 1,949 PP**;
- 92.9K: **100.2 TG / 1,814 PP**;
- 128.8K: **93.2 TG / 1,680 PP**;
- peak VRAM at 128K ~14.53 GiB.

This supersedes v2 as the best same-card dense-27B physical receipt, but **does not move the mature target ladder**:
the existing targets already sit below these receipts to allow source-like quant / workload variance.

It strongly supports using the 5070 as a dense-27B cold-prefix producer.

## NEW — Splash #301: retained hybrid checkpoint makes shared-prefix 27B reuse cheap

Issue:
https://github.com/incoai/splash/issues/301

Created **2026-10-04 19:45:04 UTC**.

M5 Pro 64 GB, Qwen3.8-27B fine-tune + DFlash2, int8 KV:
- two conversations share ~19K system-prefix tokens;
- current 1.2.0 re-prefills conversation B: **39.6 s TTFT**;
- keeping the last 4,096-token prefill checkpoint lets B reuse 16,384 tokens: **6.3 s TTFT**;
- reply text identical in all reported A/B runs;
- retained checkpoint cost: ~187 MiB.

This is not CUDA->Metal portability, but it is direct evidence that the 27B Mac runtime already treats useful
continuation state as a retainable composite object rather than "KV only."

### Project-51 dense-27B fleet topology promoted

Initial implementation rule:
> **Transfer ownership, not computation.**

1. 5070 loads the exact destination checkpoint/quant/runtime identity.
2. 5070 performs **cold initial prefill only**.
3. Freeze at a committed token frontier.
4. Export canonical continuation state:
   - attention KV;
   - GDN recurrent + convolution state;
   - position/RoPE/context metadata;
   - tokenizer/template/model/quant/config fingerprint;
   - committed token frontier.
5. One bulk transfer to one M1 Max.
6. M1 imports and verifies the frontier, then becomes the **sole authoritative session owner**.
7. 5070 discards that session and can launch another agent.

Phase 1 deliberately does **not** require transferring MTP/DFlash draft state. Reconstruct it locally if cheap;
transfer it only if measurement shows reconstruction is material.

Identity rule:
- Swift->Swift only;
- ThinkingCap->ThinkingCap only;
- base->base only;
- no cross-post-train state reuse even when architecture shapes match.

Qualification order:
- 32K exact model/quant CUDA->Apple;
- compare local-M1-prefill vs transferred state next-token/logit/trajectory;
- then 96K / 128K;
- measure export + network + import wall time against M1-local cold prefill;
- only then consider later "send a giant append back to 5070" ownership migration.

Continuous token-by-token cross-node decode is explicitly **not** the first architecture.

## UPDATE — Strata #783: partial-residency follow-up is mildly positive, original gate stays open

New comments inside the window:
- 2x RTX5060Ti / partial residency / IQ2_XS: mean decode ~**+3.7%**, prefill flat; limited parity spot-check clean.
- single RTX4090 / IQ2_XS: **+1.9% code / +3.9% reasoning / +4.7% agent** short-context decode.

These weaken the idea that #783 is broadly unsafe, but they do **not** close the earlier 2x3090 Swift-IQ3_XXS
end-to-end divergence case. Exact 5070/IQ3_S qualification still required before speed credit.

## UPDATE — Strata #711: streamed K8V4 becomes a real long-context candidate

PR:
https://github.com/Niko1221/Strata/pull/711

Updated in-window.

K8V4 can now use `--kv-resident` streaming. On RTX4090/31-GB-host/IQ2_XS/262K:
- streamed K8V4 frees enough VRAM for 1,745 more expert slots than non-streamed K8V4;
- prompt-cache restores at 114,688 and 229,376 tokens decode normally;
- q4_0 and K8V4 performance are workload-shaped and single-run.

Project-51:
- keep INT8 as the frozen exact-box baseline;
- add streamed K8V4 as a later quality/capacity A/B, not a default.

## NEW — Strata #812: Codex MCP namespace compatibility fix

PR:
https://github.com/Niko1221/Strata/pull/812

Created **2026-10-04 18:34:10 UTC**.

Codex sends namespaced MCP tools; Qwen often emits the flattened double-underscore spelling. The adapter did not map
that spelling back to the namespace, so Codex rejected the call as unsupported.

The PR registers both names and reports real Codex 0.160.0 -> Strata IQ3_S MCP web-search success after the fix.

Project-51:
- add namespaced-MCP spelling to the Codex protocol gate;
- Responses support is still not "fully Codex compatible" until #782 additional_tools and the other lifecycle cases pass.

## UPDATE — Strata #525 parser rescue becomes explicit/default-off adaptation

An in-window review update moves stranded-tool-call rescue behind named `format_fixes`, default OFF, with observable
adaptation logging. This is the right Project-51 doctrine:
- fail loud by default;
- parser adaptations are explicit;
- adaptation-assisted success is reported separately from native model success.

## NEW — Strata #833: low-RAM Windows file-tier prefill work

PR:
https://github.com/Niko1221/Strata/pull/833

Created **2026-10-04 20:38:32 UTC**.

RTX5070Ti + RTX3060 / 32GB Windows / Swift Flash IQ3_XXS / 47.6K:
- 0.1.39 with 18-GiB resident budget: ~1,261 PP;
- batched reads + closed mapped view: **~1,669 PP**;
- helper-cache arm: ~1,665-1,787 PP.

Useful mechanism for memory-starved Windows hosts; user's 64-GB primary box is less file-tier bound.
No direct target movement.

## NEW — Strata #834: 512K IQ2_XS stretch receipt on 4090 + 32 GB

PR:
https://github.com/Niko1221/Strata/pull/834

Created **2026-10-04 20:43:09 UTC**.

One RTX4090 24GB + 32GB host, Flash IQ2_XS, experimental YaRN 2x:
- 476,820-token prompt: **3,411 PP / 122 TG at depth**;
- planted recall correct at all tested sizes;
- RAM headroom setting is critical.

This is useful long-context systems evidence only:
- outside trained 262K;
- IQ2_XS;
- different GPU;
- one planted recall fact;
- no Project-51 numeric transfer.

## NEW — Splash #300: zero-allocation prompt-lookup drafter

PR:
https://github.com/incoai/splash/pull/300

Created **2026-10-04 18:23:11 UTC**.

Standalone prompt-history lookup engine reports ~49 ns query latency on Apple Silicon and zero decode-time heap
allocations. It is not yet a full-model served speed receipt.

Project-51:
- useful later mechanism for copy/repetition-heavy coding;
- no generic TG credit.

## NEW — oMLX #4249: M1 Max 64-GB Lightning-MTP settings bug

Issue:
https://github.com/jundot/omlx/issues/4249

Created **2026-10-04 19:52:47 UTC**.

Fresh oMLX 0.7.0 on M1 Max 64GB can reject enabling Lightning MTP on Qwen3.8-27B / Swift 1.5 27B until TurboQuant KV
is toggled once. This is a settings/UI dependency bug, not evidence that Lightning MTP requires TurboQuant.

Project-51:
- verify effective runtime config from logs, not UI state alone.

## CURRENT PUBLIC ARTIFACT CHECK

No official/public **Swift Flash GSQ-RCO IQ3_S** found at cutoff.
No official/public **ThinkingCap Qwen3.8-27B GSQ-RCO IQ3_S** found at cutoff.
Swift 1.5 Qwen3.8-27B GSQ-RCO IQ3_S+MTP remains available and is the first dense alternate-checkpoint artifact.

A same-day third-party "Heretic" Swift 1.5 IQ3_S exists, but its exact publication timestamp was not established
inside this strict window; classify it as current third-party availability, **not NEW**.

## KNOWN / NO CHANGE

- Flash production baseline remains DASLab GSQ-RCO IQ3_S.
- Swift Flash IQ3_S remains the highest-priority Flash challenger to build/qualify.
- 5070-Ti Flash physical fit remains ~97%.
- Windows 16-GB/64-GB full-context admission remains ~90%.
- 8 h / 24 h zero-stall remains ~75% / ~55%.
- Dual-M1 Flash production remains native262K >=35 TG / >=400 cold PP.
- Dual-M1 Flash performance remains ~128K >=40 TG / >=425 cold PP.
- Dense-27B RTX5070 mature ladder is unchanged numerically; v3 strengthens its physical anchor.
