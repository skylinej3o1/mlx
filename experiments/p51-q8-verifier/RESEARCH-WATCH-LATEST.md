# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-1330.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-03 13:30 ET

This pass was performed canonical-state-first and also checked the older Aug-31 / Sep-1 formal chain before classifying recovered machine receipts. Older external measurements absent from the formal chain are explicitly labeled **NEW-TO-REPO BACKFILL** rather than newly published results.

Material deltas:

- **NEW-TO-REPO — M1 Max 64 GB / Qwen3.8-27B:** direct oMLX serving curves now anchor the hardware. A favorable no-MTP/no-DFlash 4-bit M1 Max 32c profile measured about **18.9 tok/s B1 at 1K, 17.9 at 8K, 15.1 at 32K, 13.3 at 64K, and 10.3 at 128K**, with **44.9 tok/s B4 aggregate** at short context. A separate 8-bit profile measured **10.9 B1 / 38.4 B4 aggregate**. Keep profiles separate because oMLX build/acceleration settings vary materially.
- **NEW-TO-REPO — RTX 5070 Ti 16 GB / Qwen3.8-27B:** a direct `UD-Q3_K_XL` native-MTP setup fits a 24K Q8-KV window. Controlled 8K cache-busted four-workload mean was **97.2 tok/s**; 24K agent tool-call generation was **111-115 tok/s**. The tested IQ4_XS 4-bit target spilled to ~0.4 tok/s, making fit/quant selection first-order on this card.
- **NEW-TO-REPO — RX 6800 16 GB / Qwen3.8-27B:** one real 32K Vulkan tool-chain task measured Q3_K_M at **~12.7 tok/s TG / ~129-130 PP** and UD-Q2_K_XL at **29.3 TG / 156 PP** with ~10.68 GB VRAM. Useful direct GPU evidence, but the one-task Q2 quality result requires reproduction.
- **NEW-TO-REPO — RTX 5070 Ti 16 GB + 64 GB host / Flash-Next:** Windows + llama.cpp b10718 + IQ4_XS + 128K + Q4 KV + Flash Attention + Auto-Fit/Lazy Mode reports **~17-18 tok/s real chat generation**. An independent Q8_0 same-GPU-class artifact reports **11.3 tok/s single-stream decode**. Quant/residency policy is part of the performance result.
- **NEW-TO-REPO — single M1 Max 64 GB / DS4-0731:** a patched llama.cpp / IQ3-XXS / 64K operator reached **90+ tok/s prefill and 7+ tok/s decode** after tuning; a second same-thread M1 Max / DS4 IQ2XXS point reports about **8-10 PP / 10 TG**. These improve single-node calibration only; exact 2x M1 0731 decode TG remains missing.
- **FRESH POST-10:30 — llama.cpp #28330:** Qwen4Exp indexer memory unnecessarily allocated a V-cache plane that is never used; the new PR removes that waste. This is promising capacity headroom for constrained Flash-Next machines, but no bytes-saved or end-to-end TG measurement is posted yet.
- **FRESH POST-10:30 — DS4 #861/#963:** refreshed two-Radeon-8060S/TB5 layer-pipeline numbers are **250-274 tok/s prefill, 15.5 tok/s short decode, ~14.3-14.4 tok/s over a 6,144-token thinking run**, with two-client batching **+3% to +14% aggregate**. Separately, #963 fixes DeepSeek text-tool observations being misreported as context overflow on M5 Max. These are topology/correctness evidence, not M1 receipts.
- **FRESH POST-10:30 — oMLX #3405:** fixes a fresh-install MLX 0.32.2 Qwen3.8-27B VLM `mx.repeat` compatibility regression; real 27B screenshot and Flash-Next image/tool validations pass. No raw-speed claim.
- **NO CHANGE — exact dual-M1 / Layr:** no sustained 2x M1 Max Flash-Next TG or 0731 TG appeared, and no Layr exact-challenge PR updated after the prior cutoff.

## Forecast consequence

Do **not** change the canonical dual-M1 Flash-Next B1 or B2-B4 confidence bands from this pass. The key missing measurement remains sustained Flash-Next TG on the real 2x M1 Max/TB4 topology.

Add machine-specific **27B serving priors** separately from P69:

- M1 Max 64 GB: favorable 4-bit oMLX baseline is high-teens B1 at short context, about 10 tok/s at 128K, with ~45 tok/s short-context B4 aggregate observed;
- RTX 5070 Ti 16 GB: the measured strong lane is a low-bit target + native MTP; the tested 4-bit file can spill catastrophically;
- RX 6800 16 GB: low-bit 27B is practical and can be fast, but the Q2 quality conclusion needs workload-specific reproduction.

For Flash-Next, the new 5070-Ti/64-GB-host receipt makes that user's discrete-GPU lane much better calibrated. For DS4-0731, the single-M1 backfill improves fallback calibration without supplying the still-missing two-node TG.

M1 Max 32 GB remains directly unmeasured for these new 27B/DS4 receipts; do not infer fit from MLX-active memory alone because the 64-GB oMLX 27B profiles report much larger process/system memory footprints.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
