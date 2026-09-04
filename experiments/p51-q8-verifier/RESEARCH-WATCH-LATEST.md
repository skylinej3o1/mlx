# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct
   targets from older watch-note prose when the target file has a newer calibration date.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-04-1550.md`

   **The 15:50 note is authoritative for current promotion level, topology preference, cache policy,
   safe MTP concurrency and qualification order.**

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
   - `RESEARCH-WATCH-2026-09-04-0915.md` — llama.cpp 0.4.0 packaging baseline, parallel-MTP
     isolation gate, Apple SSD-expert-streaming backfill and MTP-head quant A/B;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — fresh PP-vs-TP structural evidence, production
     coding-agent cache-granularity failure, CUDA link/toolchain preflight and DS4-agent compaction.

5. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer
  ownership, recurrent rollback, MTP/verification and slot isolation, QSA/PLE placement and
  residency, sparse long-context prefill, compiled decode, cache/state lifecycle, optional
  SSD-streaming controls, and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — sustained distributed decode, PP-vs-TP,
  Metal shard mapping, command-buffer/OS behavior, AProjQ4, speculation policy, multi-session bubble
  fill and agent-shell lifecycle/context behavior.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel
  work, ANE prefill economics, workload-aware cache/session granularity and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit
  fit, native MTP/DFlash, MTP-head quantization, Blackwell verify kernels/stability, exact CUDA
  build/runtime provenance, context headroom and coding/tool throughput.

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

**The 15:50 pass moves no row.** Fresh evidence changes topology confidence, cache policy and
qualification hygiene, not the calibrated exact-rig performance distribution.

Important qualifiers remain:

- Flash keeps its short/medium B1, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`;
- M1 27B ANE-assisted PP is a separate approximate lane, not P69 exact work;
- 5070 Ti targets require a fully resident target; a spilled configuration is disqualified;
- DS4 remains conservative until an exact sustained 0731 dual-M1 TG receipt exists.

---

# Current newest evidence delta — 2026-09-04 15:50 ET

Freshness boundary: `205d81a5bd0109d80948c3727d53e0d4f119365f` /
2026-09-04 13:22:48 UTC.

## Fresh / material

### DS4 #861 strengthens PP2/layer ownership over TP2

Fresh post-rebase two-node Strix-Halo/TB5 evidence compares pipeline over TCP against TP over the
lower-latency NHI path on the same hosts:

- ~4–5K prefill: **242 PP vs 166 TP**;
- 1024-token short-context decode: **15.08 vs 13.86**;
- 128-token decode around 4–5K context: **14.01 vs 12.93**.

This is not an M1 rate ruler. It is strong topology/mechanism evidence: on two nodes, one activation
handoff can beat many TP gate exchanges even when the TP wire is faster. Keep **PP2/layer ownership
primary, TP2 control** for both DS4 and Flash. Multi-session pipeline filling remains the preferred
aggregate-throughput direction.

### oMLX #3443 turns cache block size into a workload-adaptive requirement

Fresh real coding-agent traffic on M3 Ultra256 with hybrid GDN/ArraysCache models, including
Flash-Next, reports:

- 51.7K requests / 88M prompt tokens;
- median prompt **1,514 tokens**;
- automatic block enlargement to **4096**;
- 32,542 boundary-unavailable skips vs 1,325 stores;
- only **3.9%** successful store rate.

The cache is effective when a full boundary exists, so the failure is granularity versus workload,
not a broken cache. A >=64 GB RAM heuristic can actually choose coarser granularity on the larger
machine.

For Hermes/coding-agent qualification, record prompt-length distribution, attempted/successful
stores, boundary-unavailable skips, cached-token ratio, exact-prefix hit rate, cold/hot wall time,
boundary-capture overhead and serialization continuity. Prefer an exposed/workload-selected or
adaptive block size over a RAM-derived constant.

### llama.cpp #28403 adds a CUDA build/link/runtime preflight

A fresh qwen4exp SOFT_MAX crash on RTX PRO 4500 Blackwell was resolved with **no source change**:
CUDA 13.3 compiled the binary, but it had silently linked CUDA 12 runtime libraries. Explicit
`CUDAToolkit_ROOT`/compiler/architecture produced CUDA-13 links and removed the failure on the same
commit/model/driver.

Before any exact 5070-Ti stability/performance run, record driver/toolkit/SM/build flags and inspect
the actual linked `cudart`, `cublas` and `cublasLt` majors. Fail the benchmark on unintended
linkage. Then run the existing ubatch 256/512 + neutral/code/tool prompt-shape matrix. This does not
supersede #28377; not every similar CUDA failure is a linkage mismatch.

### DS4 #973 separates agent-shell compaction from model context

Fresh M1 Ultra128 report: `ds4-agent -c 32768` compacted a large tool read around ~1.8K old context,
rebuilt to ~1.96K, then reported context full. Treat this as agent/tool-result compaction behavior,
not a DS4 engine/KV context ceiling.

The eventual coding-agent recipe needs a separate shell gate for large tool results, compaction,
summary+tail reconstruction, continuation and repeated post-compaction tool calls.

### llama.cpp #28213 remains live after API churn

The selected-K/V gather branch was freshly rebased for a graph API change. No new Apple performance
result accompanied it, so promotion level stays experimental.

## New-to-repo backfill that changes the Flash A/B plan

- **oMLX #3428:** on M5, gathered QSA is a poor choice for tiny MTP verify/history widths but becomes
  useful for wider query batches; retaining completed pooled QSA index blocks across `trim()` avoids
  expensive full re-pooling. Portable policy: gather wide prefill, keep tiny verify rows on the
  cheap official path by default, and preserve immutable pooled-prefix state across rollback.
- **oMLX #3437:** M4 Pro64 mmap expert streaming can make Flash fit where full residency cannot, but
  single-request prefill declines with context and the measured ceiling was ~121–122K. Keep
  SSD/mmap expert streaming as a fallback/capacity lane; prefer resident stage-owned experts on the
  dual-M1 aggregate-128-GB deployment when possible.

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** no new sustained TG and no completed ~115K exact follow-up surfaced; #27993
  remains topology/correctness evidence only.
- **Dual-M1 DS4-0731:** #922 remains ~152 tok/s for 34,384-token prefill with no sustained generated
  denominator; no exact-M1 post-#957 physical throughput result surfaced.
- **RTX 5070 Ti 27B:** direct repo remains `pushed_at=2026-08-20T19:16:50Z`; no new exact single-card
  receipt displaced the current Q3_K_XL/native-MTP ruler.
- **Apple 27B:** `mlx-dspark` remains `pushed_at=2026-09-01T10:54:45Z`; Layr remains
  `pushed_at=2026-08-29T07:05:19Z`.
- **llama.cpp release surface:** the prior 0.4.0 version bump remains merged and fresh automated
  build releases continue, but a stable GitHub `v0.4.0` release/tag was still absent at this check.
  Pin an exact commit/build.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Current qualification order:

1. pin/certify one exact 0.4.0-era baseline on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 is control;
3. PLE residency/page-cache policy A/B;
4. sparse-QSA wide-prefill A/B;
5. pooled-QSA-prefix retention across trim; tiny MTP verify windows stay official-path by default;
6. recurrent rollback + **singleton MTP** A/B;
7. adversarial parallel-MTP slot-isolation gate before MTP concurrency >1;
8. compiled-decode B2/B4 end-to-end A/B;
9. **workload-derived cache granularity** using real prompt distribution + store/hit rates;
10. SSD expert streaming/direct I/O only as secondary capacity/control lane;
11. combine passing mechanisms, then long-prefill-arrives-during-decode multi-agent stress.

Safe serving posture remains: profitable singleton MTP lane + plain concurrent work until slot
isolation is physically certified.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

Keep:

- **PP2/layer ownership primary; TP2 control** — now with stronger cross-hardware structural support;
- AProjQ4 primary serving candidate, AProjQ8 control;
- request/workload-adaptive speculation;
- Metal mapping + OS build + command-buffer completion + GPU-busy + residency diagnostic gate.

If DS4 itself is the coding-agent shell, add a separate `ds4-agent` tool-result/compaction gate.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

Canonical center remains **25 TG / 110 native PP**. If ArraysCache is used, block granularity must
fit the real conversation-turn distribution and be judged by store/hit rates. ANE remains a
separate approximate lane.

P69 remains separate and unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling
only**.

## RTX 5070 Ti16 Qwen3.8-27B

Current qualification order:

1. **CUDA build/link/runtime provenance preflight**;
2. ubatch 256/512 + neutral/code/tool prompt-shape stability matrix;
3. fully resident Q3_K_XL + native MTP speed lane;
4. small-N Blackwell verify A/B;
5. BF16/Q6_K/Q4_K-imatrix MTP-head A/B for context headroom;
6. GSQ-RCO context/quality controls.

Canonical center remains **120 TG / 250 PP**.

---

# Standing architecture decisions

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stage-local recurrent/GDN/QSA/expert state is preferred over per-token TB4 or host-mediated state
  exchange when residency permits.
- Multi-agent throughput is separate from B1 TG; independent requests can fill pipeline bubbles.
- MTP concurrency is correctness-gated, not merely throughput-gated.
- **Cache granularity is workload geometry.** Do not derive it from RAM size alone.
- Prefix/session reuse is a separate latency objective and must not be counted as cold PP.
- CUDA benchmark provenance includes the **actually linked runtime libraries**, not just `nvcc` and
  driver banners.
- Stronger-chip percentages and microbenchmarks do not move exact-machine targets by themselves.
- For the eventual community recipe, pin a physically certified runtime/build and provide a
  self-test that fails visibly on correctness, paging/residency, cross-slot leakage, broken
  lifecycle, cache-store starvation or agent-shell compaction failure.

The detailed rationale, confidence ladders and target-change rules remain centralized in
`RESEARCH-TARGETS.md`.
