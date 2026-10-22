# Project 51 / Relay — LATEST research watch, 2026-10-22 13:12 EDT

**PREVIOUS verified head:** f08c2a09e71a82db92093c3ef55c945d1bfe4a31, strict cutoff **2026-10-22 14:44:00 UTC (10:44 EDT)**.
**NEW strict cutoff:** **2026-10-22 17:12:40 UTC (13:12:40 EDT)**. Begin next scan strictly after this time.
**Full primary-source report:** [RESEARCH-WATCH-2026-10-22-1312.md](./RESEARCH-WATCH-2026-10-22-1312.md). Prior reports: [10:44](./RESEARCH-WATCH-2026-10-22-1044.md) and [09:20](./RESEARCH-WATCH-2026-10-22-0920.md).

## New/updated evidence; no owner hardware tested

- **NEW unscored model candidate Sage-A1.5**: paper submitted Oct20 and released/discussed Oct21 **before** this watch (RECOVERED, not post-cutoff invention). Qwen3.6-35B-A3B family; official 21.7GB Q4_K_M text GGUF, MLX oQ4e-MTP variants. Publisher SWE-Pro61.2 (base Qwen3.6 49.5); independent xhigh AA not established. M5Max128GB/oMLX community 64K PP2529/TG105.8 and128K1644/80.9, process peak24.9GB; NOT M1. One-M164GB coding/research worker trial is justified with full tool/final-output QA and retained contexts, not FlashNext target replacement.
- **NEW Strata #3742 OPEN**: one box 4xRTX4090 QFN IQ3_XXS ~110K state stage-parallel capture **880→268ms per100K**, not token generation or two TB4 Macs, no CUDA→Metal layout evidence.
- **NEW Strata #3747 OPEN**: RX6700XT12 gfx1031 +62GiB Linux IQ2_XS RX6000 package and source smoke at occupied90.3K ~591PP/34.5TG when aligned, with memory-clock/run-order confounds; owner's RX6800 gfx1030 16GB+32GB still unsupported physically.
- **UPDATED old #3671/#3672 OPEN**: 2xRX7900XTX24 one host, QFN IQ3_S custom split/tuning 16K PP980→2392/TG53→78; 128K only configured, capped reasoning cases without final responses; not user RX6800.
- **NEW Splash #556 OPEN** M5Pro real dense/MoE DFlash restored-state comparator: 24/24 same proposal/retained lengths but final-hidden L2 0.044-0.057 and selector can change verify row count; stronger Relay parity gate, not speed. **NEW #555** target-distribution numerical proposal reference (no runtime TG); #551-554 training DRAFT unserved.
- Strata #3741 MCP final-answer round-cap correctness only; upstream ds4 #1252 ROCm test-link only. Older TensorFold #1200 updated without new credit. No owner GSQ-IQ3S native262K M1 / KVarN K4V3 / 3–5 long-agent / exact CUDA→Metal Relay demonstration; no verified significant new shipped pre-M5 Metal runtime.
- **Frozen goals:** physical 2xM1Max64/32GPU each via TB4, Qwen3.8-Flash-Next original general DASLab GSQ IQ3_S at occupied128K >=40 TG/425 genuinely cold PP, occupied262K >=35TG/400PP, source-like AA xhigh>=38, 3–5 independent retained sessions; separate 5070Ti16+64GB Linux; separate RX6800 gfx1030 16GB+32GB DDR4. No numerical confidence or hardware buy update.

**Next steps:** physical DS4 M1 buffer/memory map; physical M1 exact 27B verification+prefix A/B; Sage single-M1 Q4/oQ4e with solved-task+retained-state trial; exact CUDA quant challenger eval; RX6800 source/build/admission; native state-equivalence before Relay.
