# Project 51 / Relay — LATEST research watch, 2026-10-22 10:44 EDT

**PREVIOUS cutoff:** 2026-10-22 **13:20:53 UTC** (09:20:53 EDT); previously verified branch head `599a91b9a058ada365250b2190ce75ede3b7cc2a`.
**NEW strict cutoff:** **2026-10-22 14:44:00 UTC** (10:44:00 EDT). Next scan begins *after*, and must distinguish genuinely newly created PRs from updates to older PRs.
**Complete source audit:** [`RESEARCH-WATCH-2026-10-22-1044.md`](./RESEARCH-WATCH-2026-10-22-1044.md) ; prior [09:20](./RESEARCH-WATCH-2026-10-22-0920.md) and older chained watches.

## Newest developments — no owner hardware directly run

- **UPDATE draft Strata #3322:** official QFN DFlash2 opt-in CUDA target + Q8/Q4 drafter and target-only controls; **OLDER** RTX4070TiSUPER16 Oct20 at 8K cfg: 27-token code decode MTP38.46 vs DFlashQ8 block7 **50.86 (+32%)**, longer 2425-token only55.31→56.77 (+2.6%). Requires proper model agreement; remains **DRAFT**, no populated128/262K or owner5070Ti, not default. https://github.com/Niko1221/Strata/pull/3322
- **UPDATE Strata #3717:** RTX5060Ti16+128GB host general IQ3_S Strata0.2.2 measured cold4K **1529PP**,16K **1836PP**, short **56.7TG**, 12/12 sanity; **three 512-token capped performance requests had no final answer**. Different card, 2× host RAM vs owner5070Ti64, no long-context quality. https://github.com/Niko1221/Strata/pull/3717
- **NEW Strata #3735:** RX7900XTX24+63GB Windows Swift IQ3S/XXS/IQ2XS actual tool samples and 4K/32K/100K needle 9/9 on successful starts; **two Swift bad starts scored 0/9 needles, excluded after server reset**. Serious cold-start/corrupt-session QA warning. Not owner's separate gfx1030 RX6800+32GB. https://github.com/Niko1221/Strata/pull/3735
- **CLOSED UNMERGED Strata #3329 at13:47Z:** planned Linux gfx1030/gfx1031 `rx6900` engine feed package NOT confirmed shipped; owner RX6800 Linux source build remains the known reliable avenue. https://github.com/Niko1221/Strata/pull/3329
- **NEW Splash #550:** 552 captured DFlash cycles + offline selector correctness and replay tests differentiate proposal vs selector errors; no new trained draft or speedup; relevant diagnostic for future agent acceptance. https://github.com/incoai/splash/pull/550
- **NEW TensorFold #1200:** M5Ultra256 QFN MLX6+MTP later-image chat shared state resumes: **0→6050 cached** on third turn, TTFT **2.78→1.12s**, same-frame cache-off reply parity. Numerics differ versus old shifted-frame. No owner M1 or physical shared branch memory measurement. https://github.com/ashhart/TensorFold/pull/1200
- **UPDATE older oMLX #4745:** M5Ultra256 DeepSeek V4.1 SSD Engram warm-row reuse PP at50/131/262K **+18/+19/+15%** without altered generated hash, avoiding repeated sparse reads; *not Qwen4Exp PLE or user's M1*. Mechanism audit only. https://github.com/jundot/omlx/pull/4745
- **UPDATE older TensorFold #1009 DRAFT:** Qwen3.6 MoE Metal M4Pro64 native67.4TG vs mlx-lm85.6; cold65K 481.2s vs135.2s; functional MoE port is not automatically optimized. https://github.com/ashhart/TensorFold/pull/1009
- **Nothing shipped** in scanned interval for Mirai uzu/lalamo, Basalt Gyro-L, Locals, paperniuk ds4, oMLX, Splash, Strata or TensorFold. No new full owner-system M1Max64 QFN GSQ-IQ3S 262K fit, native K4V3 or TB4 distributed checkpoint/handoff.

**FROZEN:** owner **2× M1Max64 32c TB4** QFN full general GSQ IQ3S >=40TG + genuinely cold425PP at actually occupied128K, >=35TG/400PP 262K, AA-like xhigh>=38, 3–5 retained agents; **RTX5070Ti16+64GB Linux** quant challenger Gyro-L vs Mirai S vs DASLab/Swift; separate **RX6800 gfx1030 16GB+32GB**. No justified changes to numbers, planning confidence or buy/no-buy. Next strict interval starts **after 2026-10-22 14:44:00 UTC**.
