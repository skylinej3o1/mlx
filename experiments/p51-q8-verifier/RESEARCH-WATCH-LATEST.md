# Project 51 / Relay — LATEST research watch, 2026-10-22 09:20 EDT

**PREVIOUS strict cutoff:** **2026-10-21 23:32:14 UTC**, prior verified head `28987a547ef366ae4e768cf4164d9e04d8bd5fcb`.
**NEW strict cutoff:** **2026-10-22 13:20:53 UTC** (09:20:53 EDT). Only updates *after* this timestamp count as fresh next pass.
**Complete deltas:** [`RESEARCH-WATCH-2026-10-22-0920.md`](./RESEARCH-WATCH-2026-10-22-0920.md); previous evening [19:32](./RESEARCH-WATCH-2026-10-21-1932.md).

## Current conclusion

**M1 Max 64GB state/memory correctness outranks another speculative quant port this pass.** A real Strata Metal QSA allocation/snapshot defect and physical oMLX M1Max64 kernel/prefix benches are powerful mechanism evidence but NOT new owner ds4 measured speeds; DS4 KVarN K4V3 at262K still unimplemented and projected~61–62GiB before OS margin.

- **UPDATED earlier Strata #3564 OPEN:** M5Max128 512K IQ3S **unused extra QSA arena12,416MiB** freed plus Metal session SAVE/RESTORE repair, parked switch2306→54ms; do not assume paperniuk DS4 duplicates it, Metal checkpoint geometry not CUDA portable. https://github.com/Niko1221/Strata/pull/3564
- **UPDATED older oMLX #4496 DRAFT:** physically exact **M1Max32c64GB**, dense Qwen3.8-27B DFlash2 decode **23.8→33.7@67K,17.6→24.2@133K**, 35B MoE 17K75.9→93.2 and67K48.4→54.7 (confounds settings). Real M1 verify QMV/MMA and attention-shape ideas, not FlashNext IQ3_S TG. https://github.com/jundot/omlx/pull/4496
- **NEW oMLX #4762 OPEN:** actual M1Max64 Qwen3.6-35B protected **836-token** system-prefix cache, **~15→32 req/min four workers**, 100% post-warm prefix restores, 0.82s median TTFT vs2.03; not decode gain, nonidentical no-cache outputs around bf16 chunk boundaries. https://github.com/jundot/omlx/pull/4762
- **NEW Mirai uzu #1004 MERGED:** unifies trellis tape bit-identically, **M5Max XS27B +11.4% decode**, XS 4K PP time×0.805, **NOT pre-M5** (#899 still open future). https://github.com/trymirai/uzu/pull/1004 . RECOVERED Mirai S for Strata quality challenger to Gyro-L and DASLab on owner Linux (pinned older patch, recommended96–128GB host). https://huggingface.co/trymirai/Qwen3.8-Flash-Next-S-strata-experimental
- **NEW TensorFold #1176 OPEN:** RTX5090 **dense27B** INT8 activation W4A8 prompt TTFT35.7K **~10.7→7.85s**,109.8K **43.5→34.7**, prompt arithmetic/logits change. Stacked, not owner card. https://github.com/ashhart/TensorFold/pull/1176
- **NEW TensorFold #1195 OPEN:** GB10 persistent PLE worker reduces per-gather microbench ~8–30x but only 2.1% MTP c4 round and negligible c1 served speed; no Mac carryover. https://github.com/ashhart/TensorFold/pull/1195
- **UPDATED older upstream DS4 #1238 OPEN:** M5Max QFN Q2 bit-exact Metal decode **48→54–56 tok/s @2–32K**, PP worse at14K+, no M1 IQ3S proof. https://github.com/antirez/ds4/pull/1238
- **NEW Strata #3711/#3686 OPEN:** warm host page reuse host memcpy synthetic ~5–7→17–18 GB/s, not device TG; and canceled Metal prompt no longer blocks next request for minutes on M4Pro, relevant to agents. https://github.com/Niko1221/Strata/pull/3711 https://github.com/Niko1221/Strata/pull/3686
- **NEW TRT-LLM release v1.4.0rc1; UPDATED #20714:** Rubin ES SM107 PrimTS FlashNext QSA core/indexer +5.3% served req/s (32K), no 5070Ti/M1 speed transfer. https://github.com/NVIDIA/TensorRT-LLM/pull/20714
- **Source controls:** older Locals M2Max27B 8-agent 78 aggregate TG vs stock25 does NOT imply per-stream78 or M1 performance. https://github.com/Generated-Computers/Locals
- **No latest general replacement or production conversion** for original GSQ-RCO / native full 262K single-M1 K4V3, no new dual-M1 source-equivalent QSA/GDN/MTP/PLE handoff or 262K filled 3–5 agents. Releases hold: Strata0.2.2, oMLX0.7.2, Splash1.4.0, TensorFold1.1.2, paperniuk DS4 beta2.

**Numerical targets and confidence unchanged:** owner two **M1Max64 TB4** FlashNext IQ3S>=40TG/425 genuinely cold PP **128K physically occupied**, >=35TG/400PP native262K, AA-like xhigh>=38, 3–5 independently retained sessions; separate **5070Ti16+64GB Linux**, **RX6800 gfx1030 16+32**. No additional machine purchase. Next source interval starts after **2026-10-22 13:20:53 UTC**.
