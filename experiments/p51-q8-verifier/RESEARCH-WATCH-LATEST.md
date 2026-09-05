# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct
   targets from older watch-note prose when the target file has a newer calibration date.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-0500.md`

   **The 05:00 note is authoritative for current promotion level, production-layout numerical
   invariance probes, GPU-runtime provenance and the newest AProjQ4 cross-backend smoke evidence.**

4. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain the dated
   deltas newer than that consolidation point when reconstructing the evidence chain:

   - `RESEARCH-WATCH-2026-09-03-1330.md` — broader machine-specific backfill;
   - `RESEARCH-WATCH-2026-09-03-1530.md` — Blackwell verify / M1 serving-memory findings;
   - `RESEARCH-WATCH-2026-09-03-1725.md` — DS4 AProjQ4 + request-adaptive DSpark policy;
   - `RESEARCH-WATCH-2026-09-03-1950.md` — original Flash sparse-QSA M5 measurements;
   - `RESEARCH-WATCH-2026-09-03-2205.md` — GSQ-RCO / MTP-imatrix leads;
   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode reproduction correction,
     #28349 downgrade and hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS diagnostic,
     Blackwell ubatch stability and short-turn cache granularity;
   - `RESEARCH-WATCH-2026-09-04-0915.md` — 0.4.0-era packaging baseline, parallel-MTP isolation
     gate, Apple SSD-expert-streaming backfill and MTP-head quant A/B;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — PP-vs-TP structural evidence, production coding-agent
     cache-granularity failure, CUDA link/runtime preflight and first #973 classification;
   - `RESEARCH-WATCH-2026-09-04-1840.md` — stable v0.4.0 pin correction, modality-agnostic KV reuse,
     DS4 tool-observation correction, MTP draft-cache VRAM economics and CUDA-graph co-residence;
   - `RESEARCH-WATCH-2026-09-04-1930.md` — Flash MTP depth/commit evidence, concurrent-PLE state
     isolation, Apple exact recurrent-kernel mining and decoupled cache geometry;
   - `RESEARCH-WATCH-2026-09-05-0400.md` — QSA neighboring-row gather reuse, Metal `MUL_MAT`
     verifier-width exactness and DS4 fixed-work PP methodology;
   - `RESEARCH-WATCH-2026-09-05-0500.md` — production-layout invariance correction, low-level
     runtime stability provenance and Strix-Halo Vision AProjQ4 smoke validation.

5. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer
  ownership, recurrent rollback, MTP verification/commit semantics, target-op batch-width exactness,
  production-layout quant probes, slot isolation, QSA/PLE placement and residency, sparse
  long-context prefill, compiled decode, cache/state lifecycle and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — sustained distributed decode, PP-vs-TP,
  Metal shard mapping, command-buffer/OS behavior, AProjQ4, speculation policy, fixed-work PP,
  multi-session bubble fill, tool-result behavior, compaction and exact prefix/session reuse.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel
  work, ANE prefill economics, GDN kernel evolution, target-op batch-width behavior, production
  quant-layout fidelity, cache/session granularity and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit
  fit, native MTP/DFlash, MTP-head and draft-cache quantization, Blackwell verify kernels/stability,
  exact CUDA build/runtime/driver provenance, net VRAM/context headroom and coding/tool throughput.

Other machines promote only when they expose a mechanism likely to transfer into one of those four
hardware lanes.

---

# Canonical target calibration — unchanged

Full threshold ladders and assumptions live in `RESEARCH-TARGETS.md`.

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 05:00 pass moves no row.** The new findings correct attribution and strengthen stability /
benchmark provenance but do not provide a new sustained receipt from any target rig.

Important qualifiers remain:

- Flash keeps its short/medium B1, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`;
- M1 27B ANE-assisted PP is a separate approximate lane, not P69 exact work;
- 5070 Ti targets require a fully resident target and measured net VRAM headroom;
- DS4 remains conservative until an exact sustained 0731 dual-M1 TG receipt exists.

---

# Current newest evidence delta — 2026-09-05 05:00 ET

Starting freshness boundary: `755e3e9cac65e7e9970a027b44f76c0e827eaa88` /
2026-09-05 08:03:24 UTC.

## Fresh / material

### vLLM #54521 — withdraw the synthetic blockwise-FP8 M-invariance row

Post-cutoff correction at 08:40:57 UTC: the earlier blockwise-FP8 row used the wrong scale layout
for the production SM120 kernel and is withdrawn. Per-channel FP8 remained identical across tested M
widths; BF16 cuBLAS retained a 1-ulp M-dependent difference. A production-layout GB10 blockwise rerun
is pending.

**Policy:** isolated quant-kernel exactness/invariance probes must reproduce production tensor and
scale layouts/strides before being used for attribution. Do not treat the withdrawn row as evidence.

### vLLM #55425 — low-level Intel runtime update removes the observed 160K MTP2 crash in a 3-run retest

Post-cutoff update at 08:17:30 UTC: Qwen3.8-27B GPTQ INT4 + BF16 MTP2 on Arc Pro B70 had previously
failed on repetition 3 under Intel compute-runtime 26.27 with Xe CCS/BCS reset. Under runtime
26.31.39395.13, XPU Graph still enabled, three consecutive 160K + 128-token requests all completed
(246.50 s, 245.49 s, 244.59 s). The reporter does not yet call it definitively fixed.

**Policy:** GPU driver / compute-runtime version is part of every stability receipt. This reinforces
RTX-5070 certification provenance but is not a CUDA throughput ruler.

### DS4 #929 — Vision AProjQ4 fully-resident Strix Halo smoke pass

Post-cutoff ROCm report at 08:25:22 UTC: the 78.62-GiB Vision-Exp AProjQ4 artifact ran fully resident
on Ryzen AI Max+ 395 / Radeon 8060S, correctly identified/count a kitten in the reported smoke case,
showed no crash/NaN/loop failure, and generated at **17.69-17.80 tok/s**. Reported image-turn
processing was 95.52 tok/s and follow-up processing 43.94 tok/s.

No AProjQ8 control was run. Treat this as cross-backend operational support for AProjQ4, not a
quality-equivalence claim and not a dual-M1 rate ruler.

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** no post-boundary sustained exact 2x M1 Max64/TB4 TG receipt or completed
  long-context exact result surfaced; llama.cpp #28243 had no post-cutoff comment.
- **Dual-M1 DS4-0731:** no post-boundary sustained generated-token denominator surfaced; #952 had no
  post-cutoff comment.
- **M1 Max64 Qwen3.8-27B:** no post-boundary exact serving receipt surfaced; MLX #4409 remains
  pre-cutoff for this pass.
- **RTX 5070 Ti 27B:** no post-boundary exact 5070-Ti throughput receipt surfaced in the watched
  llama.cpp/Blackwell search.
- **oMLX:** no focused Qwen3.8/MTP/cache issue hit after the cutoff.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Qualification order:

1. pin/certify llama.cpp `v0.4.0` / exact tagged commit on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. PLE residency/page-cache/direct-read A/B;
4. sparse-QSA wide-prefill A/B;
5. QSA neighboring-row selected-block reuse A/B after sparse-QSA passes;
6. pooled QSA-prefix retention / rollback correctness;
7. Metal `MUL_MAT` batch-width invariance across actual quant types and planned verify widths;
8. reproduce **production quant tensor/scale layouts and strides** in isolated invariance probes;
9. singleton MTP depth/acceptance with pre-verify snapshot + exact recurrent commit/replay;
10. mismatched-length concurrent pure-prefill state-isolation gate;
11. adversarial parallel-MTP slot isolation, then MTP concurrency >1;
12. compiled-decode B2/B4;
13. exact cache/session reuse and multi-agent stress.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

No target/topology change. Keep PP2/layer ownership primary, TP2 control, AProjQ4 primary candidate,
request-adaptive speculation, mapping/OS/command-buffer/residency diagnostics, fixed-work PP,
tool-observation, compaction and exact-session gates. The fresh Strix Halo Vision smoke pass does not
replace the required exact dual-M1 AProjQ8/Q4 comparison.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No target change. If batched verification is used, inherit the Metal matmul-width gate and require
production quant-layout fidelity in isolated exactness probes. P69 remains separate and unchanged:
**P69B12 frozen/promoted; P69B13 next from existing profiling only**.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Keep linked CUDA-runtime provenance, **driver/runtime version**, ubatch/prompt-shape
stability, fully resident Q3_K_XL + native MTP, draft-cache net-memory A/B, DFlash control, small-N
verify, MTP-head quant and GSQ-RCO.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing architecture / certification decisions

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stable llama.cpp `v0.4.0` remains the reproducible first baseline candidate; it does not imply
  optimized Flash throughput.
- Stage-local recurrent/GDN/QSA/expert state is preferred when residency permits.
- QSA neighboring-row selected-block reuse remains an experimental Apple prefill lane, not forecast
  input.
- MTP exactness includes target-op batch-width numerical invariance plus recurrent snapshot/commit
  correctness and long greedy continuation.
- **Quant-kernel invariance tests must mirror production layout/strides.**
- Concurrent pure-prefill remains a dedicated Flash correctness gate before concurrent MTP.
- PP comparisons require actual `prefill_tokens`, context frontier, generation coupling, build and
  model identity.
- **GPU driver / compute-runtime version is part of benchmark identity and stability certification.**
- Physical cache-page size and prefix-match granularity should remain independently selectable.
- Prefix/session reuse remains separate from cold PP.
- DS4 #973 remains tool-observation-path first, compaction second.
- On 16-GB NVIDIA, nominally smaller draft KV can consume more total VRAM; net residency decides.
- Stronger/different hardware mechanisms do not move exact-machine targets by themselves.
- P69 exact verifier work remains isolated from external serving/runtime research.

The detailed rationale, confidence ladders and target-change rules remain centralized in
`RESEARCH-TARGETS.md`.
