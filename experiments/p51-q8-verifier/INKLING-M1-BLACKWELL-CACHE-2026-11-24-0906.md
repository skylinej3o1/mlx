# Inkling PC/M1 and agent correctness — Nov24 09:06 EST

[Full watch](./RESEARCH-WATCH-2026-11-24-0906.md) carries strict cutoff, exact sources and all evidence. Separate candidate track only.

## Quant and platform decision

The Nov24 [5080 guide](https://www.reddit.com/r/LocalLLaMA/comments/1y46vxe/guide_inkling_2_mini_on_a_single_rtx_5080_16gb/) uses DQ8 19.7GB on 16GB VRAM plus CPU expert spill, INT8 KV, spec8 and custom branch. Native experts mostly preserved; MX8 19.6GB currently listed, preserves MXFP8 natively. Not interchangeable benchmark artifacts. Author 239K occupied 3275PP/132TG; 5.8K7505/218. 64GB DDR5-7200 285K vs owner64GB DDR5-4800 265F and 5070Ti16: CPU+RAM may dominate spill. No owner forecast promoted. IQ3_QT 10.5GB alternative lower-fidelity compression needs matched tasks. Keep first GSQ trial frozen.

M1: [Paperniuk #86](https://github.com/paperniuk/splash/pull/86) OPEN actual M1 Max32 Inkling DFlash2 chat, no long-context data. [#84](https://github.com/paperniuk/splash/issues/84) projected three-lane throughput gain from M2 Max projection kernels, +27.5% dense Q4_0 and +10% QFN Q2_0, not measured end-to-end/source GSQ. [#89](https://github.com/paperniuk/splash/pull/89) old Apple dispatch stability fix OPEN. 1.7.2 upstream not proof M1 fork ready.

## Critical correctness gates

[Basalt #658](https://github.com/jesdga95/basalt/issues/658) cancelled prefill poisons QFN UD cache; [Strata #7024](https://github.com/Niko1221/Strata/issues/7024) SWA ring overwritten at large Metal chunk; [#7020/#7021](https://github.com/Niko1221/Strata/issues/7020) concurrent prefill changes greedy writer outputs; [Splash #818](https://github.com/incoai/splash/issues/818) reply state capture refused under KV pressure even on1.7.2. Must validate cancelled/aborted requests do not publish incomplete state, exact replay and slot independence, long-lived session state admission. Warm cache hit is not evidence of correctness. No runtime changes or owner tests authorized.
