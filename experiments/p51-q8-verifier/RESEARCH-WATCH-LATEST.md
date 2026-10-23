# Project 51 / Relay — LATEST research watch, 2026-10-23 16:32 EDT

**Verified starting branch HEAD:** `b80bd231ad9a7d22f448c5e583a0ccd375afedb7`
**Previous strict cutoff:** 2026-10-23 17:47:07 UTC.
**NEW STRICT UTC CUTOFF:** **2026-10-23 20:32:52 UTC** (16:32:52 EDT). Next scan strictly AFTER this instant.
**Full report:** [RESEARCH-WATCH-2026-10-23-1632.md](./RESEARCH-WATCH-2026-10-23-1632.md). Prior [13:47](./RESEARCH-WATCH-2026-10-23-1347.md), [13:45](./RESEARCH-WATCH-2026-10-23-1345.md), [07:19](./RESEARCH-WATCH-2026-10-23-0719.md).

## Highest-value new evidence

- **NEW Strata #3876 OPEN** reduces Gyro-M GGUF Metal-wrapped VA from ~91.97 to37.57GB by omitting 54GB file-backed PLE table; physical **128GB Apple Silicon** 2K PP728→1245, short TG70.9→84.6; **NOT 54GB resident RAM freed or verified 64GB M1**. Related old #3299 trellis Metal kernels tested on **M5Max128** Gyro-M versus source IQ3S coding task8.1 vs7.4 min and shared mapped weights2 engines1.28× aggregate, neither M1 agent fit nor original general IQ3S replacement.
- **UPDATED OLD Strata #3541 OPEN DRAFT** physical **M5Max128 QFN GSQ IQ3S** Metal actual-window state park28,785 tokens RAM798MB49ms/restore41ms, disk679MB save161ms/restore after process restart103ms, identical95/95 reply; only solo, no M1Max64/full128K or Metal batching. **UPDATED #3341** separate CUDA4080Super snapshot1,962 tokens266MB disk across restart, reused1962+17 new; neither merged/Metal cross-tested.
- **MERGED llama.cpp #30965 at17:49Z** removes redundant QSA-only kq_mask compute allocation, measured CUDA scratch **~2GiB at ubatch4096 /4GiB at8192** each device+host graph; does **not** shrink model weights/KV or automatically reclaim on paperniuk DS4 M1. Audit exact user's scratch.
- **NEW TensorFold #1219** dense27B DFlash2 **GB10** better attention row+K/V L2 locality, physical32,706-token prompt **TTFT140–144→101s (-29%)**, c1 ~37.3→31.3ms/token, four-stream per stream124–132→79ms; **18/18 hashes plus 8/8 FP8 exact**; different CUDA GPU/architecture.
- **UPDATED oMLX #4773 OPEN** physical **M1Max64/32GPU** dense27B oQ4e+FP16 DFlash2 4bit: short code solo BF16->FP32 **38.0→50.6 TG** and **3 concurrent each10.9–15.2→13.2–17.3TG**, acceptance90–91%. Different model and short active streams, not three retained 128K GSQ IQ3S agents or merged M1 #4496.
- **NEW Strata #3882** HIP RDNA4 DFlash2 now serves solo but author's A/B **INVALID and withdrawn**, no speed claim or RX6800 gfx1030 parity. **UPDATED older #3699** Sage Q4_K_M RTX5080+64GB example only after manual BF16 SSM graft, not official untouched checkpoint/model quality. oMLX #3676 nonmonotone PLE expert resident-fit estimator theoretical, not physical owner 64GB admission.
- **NEW oMLX #4798/#4799** thinking parser/response-admission correctness, oMLX #4797 keepalive model identity, no throughput; **NEW Strata #3878** external5090 regression 5–7% PP slower, decode similar. No new DASLab source-like occupied128/262K qualified benchmark, no native K4V3 single M1 fit, and no actual CUDA→Metal Relay.

**FROZEN planning:** 2×M1Max64 32GPU separate, original general DASLab QFN GSQ IQ3S **occupied128K≥40 sustained B1 TG /425 genuinely coldPP**, native occupied262K≥35/400, AA-like source xhigh≥38 and 3–5 independent retained/restarted coding agents. One Linux RTX5070Ti16+64DDR5 and one RX6800 NON-XT gfx1030 16+32DDR4; no third Mac and no purchase/confidence changes.

**Next physical experiments:** exact M1 DS4 buffer accounting and Q8 vs K4V3 native262K; M1 3–5 session cache+disk restoration and full coding tasks, FP16 DFlash dense27B and Gyro fit independently; correct-card CUDA and smaller AMD checks; full source-equivalent 5070Ti→Metal QSA/GDN/PLE/MTP committed frontier with TB4 transfer/validation.
