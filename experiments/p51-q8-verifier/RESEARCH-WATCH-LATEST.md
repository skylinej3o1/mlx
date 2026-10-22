# Project 51 / Relay — LATEST research watch 2026-10-22 17:31 EDT

**Prior verified HEAD:** `d6ace3473f28e7b7c68999ad4052bd15fe6c51ce`
**Prior strict cutoff:** **2026-10-22 19:36:43 UTC** (15:36:43 EDT).
**NEW strict cutoff:** **2026-10-22 21:31:34 UTC** (17:31:34 EDT). Start next research search strictly AFTER the new cutoff.

**Complete research:** [RESEARCH-WATCH-2026-10-22-1731.md](./RESEARCH-WATCH-2026-10-22-1731.md). Previous [15:36](./RESEARCH-WATCH-2026-10-22-1536.md), [13:12](./RESEARCH-WATCH-2026-10-22-1312.md), [10:44](./RESEARCH-WATCH-2026-10-22-1044.md), [09:20](./RESEARCH-WATCH-2026-10-22-0920.md).

## Priority results (source author / not tested on owner hardware)

- **NEW Strata #3763 OPEN** physical 2×RTX5070Ti16 on ONE Linux PCIe box fixes missing NVFP4 expert scales on peer prefill; finite logits had wrong recall without fix. Cold25K two needles pass, prefill21K **~2400→2700tok/s (+12.5%)**, author decode+27%; no single-card owner / CUDA→Metal GDN/QSA state parity or full128K.
- **NEW llama.cpp #30997 OPEN** fixes silent cache restore refusal when idle sessions hold unified KV cells: save+evict and retry, CPU tested **3126 reused/26 eval vs previously3152 fresh**. Priority for 3–5 truly retained agents.
- **UPDATED OLD Strata #1937 OPEN** disk-backed IQ3_XXS agent park across restart on 2×CMP50HX: 41.8K cold22.5-23.3s→2.6-2.9s restore and165.6K cold73.3→8.4s; exact only with adaptive swaps off, no Metal builds. Crucial durable retention mechanism, not native Apple delivery.
- **UPDATED OLD Strata #3678** RTX4070Ti12/64 RAM Ornith1.5-35B quant GQA KV: int8 ~26% of f16 bytes; physically180K int8 **475 coldPP/13.3TG**, fp8 same PP/12TG; Q4 had higher bytes than fp8 due encoding overhead. **Not QFN GSQ QSA/K4V3**. **UPDATED older llama.cpp #30683** RTX Pro6000 avoids copying cached shared-prefix 35B state,83→62ms; not true multiagent physically shared prefix.
- **UPDATED Splash #556** 540 real native DFlash CUDA cycles on Qwen3.8-27B training exports, no consistent acceptance/throughput benefit; pre-existing M5Pro restore drift remains.
- **RECOVERED Flint detail** launch Oct21; llama.cpp Flint Metal #30928 **MERGED Oct21 21:26Z**, official 22.9GB NVFP4 /26GB INT4, M4/M5-only special `rec` NOT M1, but ordinary Metal llama.cpp offers viable *unscored* one-M1 test. Publisher 54.9 TerminalBench2.1/74.2 SWE Verified BF16, not AA>=38, no physical M1 source-like rate. No new reliable QFN GSQ general IQ3S better quant or full native M1 occupied262K test.
- **FROZEN** physically occupied **128K** dual M1Max64 32 GPU core original general DASLab GSQ-RCO IQ3S >=40 sustained decode /425 truly cold PP; occupied **native262K** >=35/400, xhigh AA-like>=38, 3–5 independently retained agents. Separate RTX5070Ti16+64 DDR5 Linux and nonXT RX6800 gfx1030 16GB+32GB DDR4. No confidence shifts, no third Mac, no CUDA→Metal parity.

**Next:** M1 exact buffer map and 262K fit with Q8 vs K4V3; owner single-M1 source-like agents/cache admission/durable park and Flint/Sage controlled comparison; actual 5070Ti CUDA+RX6800 own GPU quant validation; physical Relay state export with complete QSA/GDN/PLE/MTP, transport and agent quality.
