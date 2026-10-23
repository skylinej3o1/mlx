# Project 51 / Relay — latest research watch, 2026-10-23 13:47 EDT

**Canonical prior main watch** [RESEARCH-WATCH-2026-10-23-1345.md](./RESEARCH-WATCH-2026-10-23-1345.md) was concurrently committed as HEAD `4251f8007cf9f87721161e58b44e80037f84e970` with cutoff **2026-10-23 17:45:00 UTC** (13:45 EDT). Preserve that full report; no work was overwritten.
**NEW strict UTC cutoff:** **2026-10-23 17:47:07 UTC** (13:47:07 EDT); next search STRICTLY after this time. **Supplementary watch:** [RESEARCH-WATCH-2026-10-23-1347.md](./RESEARCH-WATCH-2026-10-23-1347.md). It advances the final two-minute delta and adds uncovered prior-window supporting evidence without double-counting the existing 13:45 report.

## Most important current state (main 13:45 report plus supplement)

- Strata #3869 CUDA DFlash2 now runs on 2×3090 split but averages **124.0 TG vs MTP126.2** across short requests; oMLX #4785 reports FlashNext DFlash2 attach/rollback failure on M3Ultra, needing safe recurrent frontier. **Neither is usable as CUDA→Metal Relay proof**.
- Remote CUDA layer-stage checkpoint Strata #1887 on 10GbE 16K later turns **TTFT12.83→0.38s** and worker fault handling, different vendor/state format. Hipfire #945 introduces bounded 16GiB host/8GiB disk session tier with correct private snapshots, not an RX6800 long-agent deployment.
- Strata #3060 staged RAM expert model on RTX3060+32GB reports **33.07→38.71 TG** over120 ShareGPT requests vs old adaptation, source IQ3XXS not owner 5070TiIQ3S; oMLX #4792 fixes SSD dirty block replacements, for durable agent/offload consistency.
- oMLX #4496 M1Max dense27B DFlash and verification kernels remain OPEN; separate M1Ultra35B updated results cannot be credited to M1Max64 original GSQ model.
- Supplemental **TensorFold #1080** RTX5090 dense27B at real75.6K TTFT **144.5→26.9s**, but 10/24 baseline greedy replies identical, not source parity; **NEW #1217** GB10 FlashNext GDN fusion bitwise full served gain~2–3% (not GPU kernel headline alone).
- **MERGED Basalt #23** bulk prefix matching; stacked #24/#25 private GDN and bigram draft-KV tail ownership/restore correctness, no owner speed and some negative parked timing. **MERGED llama.cpp #30804** generic CUDA graph TG+1–2%, and NEW draft trimmed-vocabulary #31037 +7.4% SYCL with graphs off, tool grammar #31040.
- **Date-only context** physical M1Max64 FlashNext-oQ4e-fp16-mtp oMLX public 64K row **PP233.6/TG8.0/peak49.5GB**, https://omlx.ai/benchmarks/performance/3xz7c2u3 ; posting UTC and true full-input occupancy not disclosed, not qualified strict-window/ISTA IQ3S result.
- No genuinely occupied native262K on owner's M1 Max general DASLab IQ3S, no 3–5 independent exact long agent sessions, no reliable source-equivalent CUDA→Metal transfer, no quantitatively justified goal/confidence change.

**Frozen planning hardware/targets:** 2× M1Max64 32GPU TB4 prospective, source original-general GSQ IQ3S occupied128K >=40 sustained B1 TG /425 truly cold PP; occupied262K >=35/400, source-like xhigh AA>=38, 3–5 independent restorable coding agents; one RTX5070Ti16+64GB Linux and one RX6800 nonXT gfx1030 16GB+32GB. No third Mac.

**Next experiment order:** actual M1 DS4 wired/Metal allocations + Q8/K4V3 at real 128/262K; physical M1 3–5 agent exact parent-root and token reuse/restore with tools, cold prefills, RAM admission; source-quality real M1 low-bit 27B/Flint/Sage; exact user's CUDA/AMD benchmarks; Relay QSA/GDN/PLE/MTP true transferred committed frontier and TB4 cost.
