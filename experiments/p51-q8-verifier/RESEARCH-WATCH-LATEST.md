# Project 51 / Relay — LATEST research watch, October 25 2026, 10:23 EDT

**Previous verified branch HEAD at scan start:** `b9fd2da6bef0f7d279f2d1dff87cb5d51c6205f9`. **Previous strict UTC cutoff:** 2026-10-24 06:33:34Z. **NEW strict UTC cutoff:** **2026-10-25 14:23:55Z** (Oct25 10:23:55 EDT). Next scan starts strictly AFTER this time.
**Full dated report:** [RESEARCH-WATCH-2026-10-25-1023.md](./RESEARCH-WATCH-2026-10-25-1023.md).

## Main findings
1. **RECOVERED older BeeLlama implementation, not a new release:** Qwen3.8 FlashNext QSA + KVarN K4V3 + 1024-token precision tails + mirrored index-cache and PLE/GDN/MTP checkpoints already implemented in a llama.cpp fork; native high-performance Metal and exact full262K IQ3S on M1Max64 NOT proved. Compare BeeLlama Metal vs Paperniuk DS4 before porting.
2. **NEW oMLX #4496 MERGED Oct24 14:00Z:** physical M1Max64 dense Qwen3.8-27B DFlash2 long decode17K40.4/67K33.7/133K24.2TG on merged route, **not FlashNext**. **NEW #4830 OPEN:** physical M1Max dense27B 5-bit MMA verify +3% one stream/+4% three, no QFN source. **oMLX #4772 group64 ~10% claim WITHDRAWN**.
3. **NEW RX6700XT gfx1031 12GB +64GB host Strata QFN IQ2_XS #3989:** short median46.5TG; 4K587PP/39.3TG; 16K705PP/43.1TG (draft protocol21/21); **not owner RX6800 nonXT16VRAM+16DDR4** or occupied128K rate. **NEW exact RX6800 gfx1030 Linux no ROCm detected Strata #4072**, Windows same machine reportedly works—check HIP setup before predictions.
4. **NEW Strata #4068 opt-in exact recent/sink Q4 KV window:** RX9060XT Swift derivative bulk8.25→5.29 bit/cell, 128K1584→1016MiB, tail KL0.00959 int8 vs0.00663 precise-window vs0.01587 plain q4lm8v; not KVarN or M1 QFN.
5. **NEW Strata #4039:** RTX2060SUPER8GB QFN IQ3XXS fresh prefill 336→395 4K,371→460 16K,380→460 32K from scratch buffer alias; 6 greedy probes same, not owner. **#3976** warm32K CUDA 2GPU staged TTFT65→33.1sec; not heterogeneous Relay.
6. **NEW source results at CONFIGURED large contexts only:** Strata RTX3090 #4054 IQ3S 524K max, short87–99TG and 16KPP1675–1679; RTX5090 #4099 IQ3S262K max, short184TG/16KPP7008. No actually occupied512K or262K evidence or owner card equivalence. **Strata v0.2.6 Oct25 13:45Z** Qwen engine remains0.1.50, DeepSeek-only0.1.51.
7. **NEW oMLX #4839:** QFN `qwen4_exp` still lacks ANE prefill backend, M3Ultra256 user observes ~1020 coldPP at55K (~55sec TTFT). **vLLM #62914** actual Qwen3.5 TP1↔TP2 exact GDN state restored but TP1 200-problem GSM8K60→54 if reused from TP2: byte-exact restore ≠ numerical output parity. **No CUDA5070Ti→M1 P/D exact verified frontier**.
8. HF: **ThinkingCap GSQ-RCO IQ3S/XXS not verified**; existing standard IQ4_XS is too big for owner M1s. Existing Swift and original ISTA-GSQ RCO remain distinct.

**Frozen targets/confidence:** two M1Max64/32GPU independent via TB4; source-general ISTA QFN IQ3_S truly occupied128K >=40 B1 TG/425 truly coldPP and native262K>=35TG/400 coldPP, xhigh AA-like>=38, 3–5 separately durable resumable agents. Separate RTX5070Ti16+64 DDR5 Linux and RX6800 NONXT gfx1030 16VRAM+16DDR4. No revised probabilities, hardware purchase or promoted quant.

**Next:** memory census and true native Metal KVarN K4V3 QSA-indexer / PLE-GDN / MTP+tail safety and task solve-rate; verify RX6800 HIP gfx1030 driver and host admission; real full Relay committed-state transport and wall-time vs local.
