# Project 51 / Relay — LATEST research watch, October 24 2026, 02:33 EDT

**Previous verified branch HEAD:** `c1f37c91ad092e9b64bf8b4155350e42e4de4649`.
**Previous strict UTC cutoff:** **2026-10-24 02:39:58Z**.
**NEW strict UTC cutoff:** **2026-10-24 06:33:34Z** (October 24, 02:33:34 EDT). Next scan starts strictly AFTER this instant.
**Full report:** [RESEARCH-WATCH-2026-10-24-0233.md](./RESEARCH-WATCH-2026-10-24-0233.md); previous [RESEARCH-WATCH-2026-10-23-2239.md](./RESEARCH-WATCH-2026-10-23-2239.md).

## High-signal strict delta
- **AUTHORITATIVE HARDWARE CORRECTION:** RX6800 non-XT gfx1030 16GB dedicated VRAM plus **16GB DDR4 host**, not 32GB. Keep at16GB DDR4 for first dense27B GSQ IQ3_XXS (9.73GiB, embedded MTP) actual physical VRAM/host fit. QuarkStar #8 remains an OLD UNRESOLVED discrete-VRAM/GTT problem (RX6800XT ~10TG), no new q36 commit. Start llama.cpp ROCm/HIP gfx1030; no exact-owner 40+TG proof, no hardware purchase.
- **NEW Hipfire v0.4.3 RELEASED05:24Z:** new split MQ3/MQ2 FlashNext tiers, gfx1201-only R9700 optimizations and new MoE quant; 16K prefill 1957→18545 Qwen3.6 A3B is mixed new engine/default and quant on R9700, **not RX6800 gfx1030**, not original DASLab model or Mac.
- **NEW Strata #3926 issue** physical **RX6900XT gfx1030+64GB host** Qwen3.6 MoE opt-in dense MMQ PP4K1379→2301(+67%), PP16K1091→1599(+47%), decode unchanged; #3924 OPEN rocBLAS5.2.0 same card short QFN Coder IQ1_M prefill GPU-timeline +12–18%, **11/12** cross-configuration answers identical. Not owner RX6800 or dense27B.
- **NEW Strata #3919 OPEN** RX7900XTX gfx1100 QFN IQ3_S adaptive KV ring 128K-tier decode53.28→66.03 (+23.9%), 64K controlled no-op, MTP acceptance dependent, no Metal effect.
- **UPDATED OLD oMLX #4772** real M1Max64 oQ4e Qwen3.6 MoE protected group64 instead of128 plain decode85–86→94–95 (~10%), MTP up to101 and16K decode69.6→78, KL slight improvement, **not original DASLab FlashNext**. **NEW oMLX #4810 OPEN** M3Ultra/M5Max concurrency MTP backoff +2.8%/+11.3% at8 clients *MTP-on*, MTP-off still faster; no owner M1.
- **NEW TF #1228 OPEN** GB10 small2B CUDA cancelled-prefill saved 6016/10752 tokens and exact replay; no repeat-run speed or original FlashNext on owner. **NEW llama.cpp #31075 OPEN** M3Ultra Metal dense27B Q4_0 34.05→34.97 (+2.7%) only.
- **NEW Strata #3922 CLOSED UNMERGED** RTX4090 GBNF 50/50 valid JSON,30/30 parsed tools, grammar disables MTP and six-slot aggregate -18.6%. **NEW Basalt #41** nullable string schema anyOf paths only2/5 correctly delivered vs5/5 type-union control. Tool/task correctness gates matter more than syntactic success. No new native KVarN4/Q4_0 source-original parity.
- No new physically verified original-general source QFN IQ3_S **actually occupied 128K/262K** meets primary goals, no **CUDA5070Ti→MetalM1** complete persistent frontier, no verified Qwen4 dense27B quant.

**Frozen targets/confidence:** 2 separate M1Max64/32GPU via TB4, ISTA-DASLab Qwen3.8-Flash-Next general GSQ IQ3_S actually occupied128K ≥40 sustained B1TG/425 truly coldPP and native262K ≥35/400; xhigh AA-like≥38 and 3–5 independently durable/resumable agents. RTX5070Ti16+64GB DDR5 Linux separate; Radeon RX6800 nonXT16 VRAM + **16GB DDR4 host** separate. No numerical/probability changes or third M1.

**Next:** physical owner-card RAM/VRAM admission and full agent solve rate; M1 source-matched KVarN/Q4/FP16 indexer+MTP at true occupied128/262K; independent stored agents under compaction/cancellation; complete full QSA/GDN/PLE/MTP CUDA→Metal Relay with measured TB4 bytes and semantics.
