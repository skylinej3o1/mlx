# Project 51 strict research watch — November 13, 2026 12:44 EST

Previous cutoff 2026-11-13T11:39:08Z. New cutoff 2026-11-13T17:44:04Z. GitHub issue/commit scan for paperniuk DS4/Splash, Strata, Kapitsa, oMLX, Basalt, Splash. FRESH vs UPDATED distinguish; no hardware work, downloads, CI or inference code changes.

## HIGH UPDATED — Strata M1 Max tile calibration
[Strata #4025](https://github.com/Niko1221/Strata/issues/4025), updated 2026-11-13T14:21Z. M1Max24GPU64GB, QFN Q2_0. Default M4/M5 tiles dense GEMV 33.1ms vs best 20.7ms on two-token window; opt-in PR #4019 --calibrate improves short decode +30–32%, 6K-context +26%, 4995/4995 quant_quality rows match with opt-out; perplexity 4.439→4.431. Not original GSQ XXS/S nor owner's M1Max32GPU; don't extrapolate.

## HIGH UPDATED — oMLX fused attention M1 fallback
[oMLX #5087](https://github.com/jundot/omlx/issues/5087), updated 2026-11-13T17:22Z. M1Ultra QFN Qwen4_exp fused attention attempts 1024 threads >896 M1 max; falls back to MLX, output works but loses fused optimization. Fix proposal cap group size, not validated speed gain.

## HIGH FRESH — Kapitsa M1 Ultra 35B DFlash2 acceptance
[Kapitsa #1254](https://github.com/nace-ai/kapitsa/issues/1254), updated 2026-11-13T15:48Z. M1Ultra128, 32K prompt, Kapitsa default 35B pack+DFlash2 ~139 tok/s vs mlx-community plain 4bit same drafter ~152; same cycle time ~25ms but accepted tok/cycle 3.48 vs3.78. Model/quant affects acceptance. Not QFN or M1Max; no general engine ranking.

## HIGH FRESH — Strata 5070Ti long-agent repetition/context clamp
[Strata #5924](https://github.com/Niko1221/Strata/issues/5924), updated 2026-11-13T15:05Z. Windows RTX5070Ti16, Flash-Next abliterated IQ2XS, 204800 configured but 65536 observed context in logs. fit_max_tokens clamps output room to ~221 at 65.3K input, answer budget exhausted, repetitive no-tool-call loops; app overrides config on restart. A user report, not original GSQ IQ3S; reinforces Molt context-headroom and tool-finish checks.

## Paperniuk fork check
[DS4 m1-flash-next](https://github.com/paperniuk/ds4/tree/m1-flash-next) last visible commit 2026-11-12T21:28:48Z, 9da1288 (mixed IQ3/Q2 SSD streaming). Prior Nov12 DFlash2 port and bit-exact batched verification remain key; no newer commits confirmed by midday cutoff. [paperniuk/splash](https://github.com/paperniuk/splash) most recent commit Nov12 11:20Z docs 1.6.1-m1. No new M1Max64 DFlash2 vs MTP benchmark observed. Prior upstream antirez/ds4 last Nov3.

## Other
[Splash #759](https://github.com/incoai/splash/issues/759), [#760](https://github.com/incoai/splash/issues/760) updated but production-shaped experiments still no qualified throughput gain. [Basalt #351](https://github.com/jesdga95/basalt/issues/351) ZRAM resident budget request, no impact on owner 64GB baseline.

## Retained
Owner two independent M1Max64 32GPU, desktop RTX5070Ti16+64GB, secondary RX6800. Original GSQ IQ3XXS quality floor, IQ3S preferred; 128K-262K context; frozen Basalt first test original GSQ IQ3S true32K INT8KV 1 slot spec1 no draft, PLE parity/agent quality. Relay CUDA→Metal KV/recurrent state handoff still unproven. Qwen4/4.5 Flash-Next refresh speculative; this scan not exhaustive model-release/quant inventory. No inference or hardware changes.

NEXT STRICT CUTOFF: 2026-11-13T17:44:04Z.
