# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct
   targets from older watch-note prose when the target file has a newer calibration date.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-0400.md`

   **The 04:00 note is authoritative for current promotion level, Flash QSA-selection reuse,
   Metal-MTP numerical exactness gates and DS4 PP benchmark hygiene.**

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
     verifier-width exactness and DS4 fixed-work PP methodology.

5. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer
  ownership, recurrent rollback, MTP verification/commit semantics, target-op batch-width exactness,
  slot isolation, QSA/PLE placement and residency, sparse long-context prefill, compiled decode,
  cache/state lifecycle, exact session reuse and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — sustained distributed decode, PP-vs-TP,
  Metal shard mapping, command-buffer/OS behavior, AProjQ4, speculation policy, fixed-work PP
  methodology, multi-session bubble fill, agent-shell tool-result behavior, compaction and exact
  prefix reuse.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel
  work, ANE prefill economics, GDN kernel evolution, target-op batch-width behavior,
  workload-aware cache/session granularity and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit
  fit, native MTP/DFlash, MTP-head and draft-cache quantization, Blackwell verify kernels/stability,
  exact CUDA build/runtime provenance, net VRAM/context headroom and coding/tool throughput.

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

**The 04:00 pass moves no row.** The new findings improve prefill mechanism selection and exactness /
benchmark gates but do not provide a new sustained receipt from any target rig.

Important qualifiers remain:

- Flash keeps its short/medium B1, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`;
- M1 27B ANE-assisted PP is a separate approximate lane, not P69 exact work;
- 5070 Ti targets require a fully resident target and measured net VRAM headroom;
- DS4 remains conservative until an exact sustained 0731 dual-M1 TG receipt exists.

---

# Current newest evidence delta — 2026-09-05 04:00 ET

Starting freshness boundary: `e74f3dc6683be61e1084fde59e294228351410e4` /
2026-09-04 23:35:16 UTC.

## Fresh / material

### vLLM #55430 — QSA tile-union prefill makes neighboring-selection reuse concrete

Fresh Qwen3.8-Flash-Next work on SM121 exploits high overlap among neighboring QSA query-row selected
blocks. A row tile forms a union of selected blocks, gathers each block once, and retains per-row
semantics through membership masks in online softmax.

Reported end-to-end gains on GB10 / TP1 are modest but consistent in the measured cells:

- 7.5K TTFT about **2.8% faster**;
- 29K TTFT about **1.7% faster**;
- two concurrent ~8K requests about **2.2% faster**;
- concurrent ~30K + ~8K about **1.6% faster**.

This is not an Apple throughput ruler. It promotes an experiment: after sparse-QSA itself passes on
the M1 cluster, test shared neighboring-row selected-block gather work, with request-aware boundaries
and serial-reference correctness.

### llama.cpp #28243 — Metal MTP exactness problem isolates to verifier-width `MUL_MAT` paths

Fresh diagnosis reports tested Metal Flash Attention as batch-invariant but several `MUL_MAT`
formats as batch-width dependent: q6_K first differs at width 4; q8_0, iq4_nl and f16 at width 2.
Wider fallback paths can differ more.

That matters directly to speculative verification because target AR runs width 1 while MTP verifies
roughly `n_max + 1` positions together. The verifier can therefore select another numerical matmul
kernel even when recurrent rollback/commit is otherwise correct.

The corrected M5-Pro matrix withdraws the earlier large speed claim. The reported greedy-exact
speculative cell was slower than baseline; the only modestly faster tested cell was not greedy-exact.

**Policy change:** MTP certification now includes target-op batch-width numerical invariance across
the actual quant formats and verify widths, plus long greedy continuation comparison. Recurrent
state correctness alone is insufficient.

### DS4 #952 — PP attribution requires actual prefill-work accounting

Fresh follow-up rejects the earlier prompt-file-length explanation for a PP discrepancy and exposes a
more general benchmark trap: the displayed context frontier can differ from the number of new tokens
actually prefetched. The reported harness examples include 16K context with 8K fresh prefill, 32K
with 16K and 64K with 32K.

**Policy change:** every PP receipt must record context frontier, actual `prefill_tokens`, whether
generation ran in the same invocation, commit/build and model artifact. Comparative cold-PP A/Bs
should fix actual prompt-token work and isolate generation whenever practical.

This does not change the existing AProjQ4 decode promotion or the DS4 target.

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact dual-M1 TG result, completed long-context exact receipt
  or post-boundary M1-Max Flash follow-up surfaced.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator surfaced.
- **RTX 5070 Ti 27B:** direct repo remains `pushed_at=2026-08-20T19:16:50Z`.
- **Apple 27B:** `mlx-dspark` remains `pushed_at=2026-09-01T10:54:45Z`; Layr remains
  `pushed_at=2026-08-29T07:05:19Z`.
- **Core MLX GDN #4409:** useful but pre-boundary and already captured by the 19:30 note.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Qualification order:

1. pin/certify llama.cpp `v0.4.0` / exact tagged commit on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. PLE residency/page-cache/direct-read policy A/B;
4. sparse-QSA wide-prefill A/B;
5. **QSA neighboring-row selection/gather reuse A/B** after sparse-QSA passes;
6. pooled QSA-prefix retention / rollback correctness;
7. **Metal `MUL_MAT` batch-width invariance gate** across target quant types and planned verify widths;
8. singleton MTP depth/acceptance A/B with pre-verify snapshot + exact recurrent commit/replay;
9. multi-request pure-prefill state-isolation gate using deliberately different prompt lengths and
   serial references;
10. only then adversarial parallel-MTP slot isolation and MTP concurrency >1;
11. compiled-decode B2/B4;
12. workload-derived cache matching + exact prefix/session reuse;
13. combine passing mechanisms, then long-prefill-arrives-during-decode multi-agent stress.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

No target/topology change. Keep PP2/layer ownership primary; TP2 control; AProjQ4 primary candidate;
request-adaptive speculation; mapping/OS/command-buffer/residency diagnostics; tool-observation,
compaction and exact session gates.

For PP comparisons, record **both context frontier and actual fresh-prefill token count** and prefer
fixed-work A/Bs before attributing rate movement to a kernel or quant choice.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No target change. If this lane uses batched verifier execution, inherit the Metal matmul width gate.
P69 remains separate and unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling
only**.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Keep CUDA linked-runtime provenance, ubatch/prompt-shape stability, fully resident
Q3_K_XL + native MTP, draft-cache net-memory A/B, DFlash control, small-N verify, MTP-head quant and
GSQ-RCO. No new exact-5070 speed receipt surfaced.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing architecture decisions

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stable llama.cpp `v0.4.0` remains the reproducible first baseline candidate; it does not imply
  optimized Flash throughput.
- Stage-local recurrent/GDN/QSA/expert state is preferred when residency permits.
- **QSA neighboring-row selected-block reuse is an explicit experimental Apple prefill lane**, not a
  forecast input.
- **MTP exactness includes target-op batch-width numerical invariance.** Correct recurrent snapshot /
  commit semantics alone are not enough when verifier batching selects a different Metal matmul path.
- Coherent output is not exactness proof. Verify state, logits/greedy continuation, acceptance by
  position and serial-vs-batched behavior.
- Concurrent pure-prefill remains a dedicated Flash correctness gate before concurrent MTP.
- **PP TPS comparisons require explicit actual-work accounting:** `prefill_tokens`, context frontier,
  generation coupling, build and model identity.
- Physical cache-page size and prefix-match granularity should remain independently selectable.
- Prefix/session reuse remains separate from cold PP.
- DS4 #973 remains tool-observation-path first, compaction second.
- On 16-GB NVIDIA, nominally smaller draft KV can consume more total VRAM; net residency decides.
- CUDA benchmark provenance includes actually linked runtime libraries; co-resident process
  configurations get their own graph-stability gate.
- Stronger-chip percentages and microbenchmarks do not move exact-machine targets by themselves.
- P69 exact verifier work remains isolated from external serving/runtime research.

The detailed rationale, confidence ladders and target-change rules remain centralized in
`RESEARCH-TARGETS.md`.
