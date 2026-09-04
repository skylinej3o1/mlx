# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct
   targets from older watch-note prose when the target file has a newer calibration date.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-04-1930.md`

   **The 19:30 note is authoritative for current promotion level, Flash MTP/state-isolation gates,
   Apple recurrent/GDN kernel watch and cache-geometry policy.**

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
     isolation, Apple exact recurrent-kernel mining and decoupled cache geometry.

5. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer
  ownership, recurrent rollback, MTP verification/commit semantics and slot isolation, QSA/PLE
  placement and residency, sparse long-context prefill, compiled decode, cache/state lifecycle,
  exact session reuse and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — sustained distributed decode, PP-vs-TP,
  Metal shard mapping, command-buffer/OS behavior, AProjQ4, speculation policy, multi-session bubble
  fill, agent-shell tool-result behavior, compaction and exact prefix reuse.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel
  work, ANE prefill economics, GDN kernel evolution, workload-aware cache/session granularity and
  serving-memory behavior.
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

**The 19:30 pass moves no row.** The new results are stronger-chip, alternate-runtime or
cross-architecture mechanism/correctness evidence rather than exact sustained receipts from the
four target rigs.

Important qualifiers remain:

- Flash keeps its short/medium B1, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`;
- M1 27B ANE-assisted PP is a separate approximate lane, not P69 exact work;
- 5070 Ti targets require a fully resident target and measured net VRAM headroom;
- DS4 remains conservative until an exact sustained 0731 dual-M1 TG receipt exists.

---

# Current newest evidence delta — 2026-09-04 19:30 ET

Freshness boundary: `e8ddf943f3f034f0502afffbab798d1a259a7670` /
2026-09-04 22:42:14 UTC.

## Fresh / material

### MTPLX #457 — M3-Max Flash-Next MTP D3 reaches ~2.03x AR, but correct recurrent commit is mandatory

Fresh M3 Max128 / MLX0.32 / mlx-lm0.31.3 Qwen3.8-Flash-Next sweep, two runs:

- AR **36.27 / 36.28**;
- D1 **45.30 / 45.26** (~1.25x);
- D2 **58.42 / 58.73** (~1.61x);
- D3 **73.60 / 73.88** (~2.03x).

D3 acceptance was 0.961/0.922/0.882. The important correctness observation is that forcing the
wrong capture/commit path produced corrupted recurrent state, D3 acceptance ~0.214 and only 0.80x
while the quality gate still passed. Qwen4-Exp's verified-window commit needs the pre-verify GDN
snapshot/replay semantics.

**Transfer only, not an M1 rate ruler.** MTP promotion now requires recurrent-state validation and
acceptance shape, not merely coherent output or a quality gate.

### DS4 #964 — exact Apple-Metal recurrent prefill kernels show 16.6-26.0% gain on M3 Ultra

Fresh GLM-5.3-Flash M3-Ultra update reports PP gains from **+16.6% to +26.0%** across 512-16K
frontiers while decode stays within ~1% of the prior baseline. Reported frontier logits are
byte-identical on the measured suite.

The useful transfer mechanisms are token tiling, two-head indexed attention with preserved
reduction order, MoE tail culling, blocked immutable recurrent-state preparation and shared-load
recurrence-value packing. A balanced 8K recurrence-value A/B added another **~2.0%** exactly.

This elevates exact recurrent/GDN packing/tiling/shared-load work into a high-priority Apple kernel
mining family. It does not change the dual-M1 DS4 or Flash rate forecasts.

### local-inference-lab/vllm #646 — decouple physical cache pages from recurrent/prefix hit geometry

Fresh GLM-5.3-Flash DGX-Spark TP4 evidence separates 2048-token target pages from 256-token recurrent
blocks and a 256-token prefix-match unit. At a 33-GB KV budget it reports 791K -> 4.30M token
capacity while preserving 256-token prefix matching and broadly maintaining serving throughput.

This is cross-hardware/cross-model mechanism evidence. Promote the policy: **physical page size,
recurrent checkpoint size and prefix-match granularity are separate knobs**. Do not let a coarse
memory-efficient page silently force coarse agent prefix reuse.

### FreeToken #389 — dense FP8 projection path helps Qwen4-Exp on Ada, with a residency trap

Fresh 2x RTX6000-Ada TP2 Flash-Next A/B: load-time per-tensor FP8 W8A8 on dense attention/GDN
projections reports **89.8 -> 99.2 tok/s (+10.4%)** single stream, +2.5% aggregate at 8 concurrent,
TTFT parity and higher expert residency after a hidden parent-view retention bug was fixed.

This is not a 5070/27B ruler and numerics change. Keep it as a future Qwen4-Exp NVIDIA mechanism.
The memory lesson transfers: sliced tensors can keep large parent allocations alive even when the
visible child is small; explicit residency accounting must catch that.

## Fresh update / correctness transfer

### vLLM #55375 — concurrent pure-prefill PLE state indexing can cross-corrupt slots

Post-cutoff update to a Qwen3.8-Flash-Next bug: with MTP3, the fused PLE short-convolution path
assumed a non-contiguous state-index view was contiguous. Later requests then read/wrote the wrong
cache slots, producing repetitive corrupted output.

The fix uses the actual state-index stride. Reported old-path regression cases mismatch 90.3% of
output elements; patched checks pass 5/5 minimal concurrent pairs, 20/20 eager, 20/20 compiled /
CUDA-graph and 35 PLE tests.

This is CUDA/vLLM, not proof of an MLX/llama.cpp bug. The **failure class transfers strongly**.
Before concurrent MTP is promoted on the dual-M1 server, run mismatched-length concurrent pure
prefills and compare PLE/GDN state, rollback and output against serial references.

## Updated upstream kernel work

### MLX #4409 — packed `gated_delta_seq` is a serious future Apple GDN candidate

Existing core-MLX PR updated post-cutoff. Eight value rows share a SIMD-group while preserving the
reported bit pattern. M5-Max validation reports 77/77 cross-build `mx.array_equal` output/final-state
cases and paired kernel speedups around **1.78-2.16x** over T512-2048 for the measured batch shapes;
a short/default-path probe reports roughly +7-24% in several B1 T<=16 cells.

This is not mainline exact-M1 serving evidence. Track upstream and test only after the serving
baseline is frozen. **Do not alter P69B13** from this external finding.

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** no new sustained exact TG, completed long-context exact follow-up or post-cutoff
  exact-M1 Flash receipt surfaced.
- **Dual-M1 DS4-0731:** no new exact sustained generated-token denominator surfaced.
- **RTX 5070 Ti 27B:** direct repo remains `pushed_at=2026-08-20T19:16:50Z`.
- **Apple 27B:** `mlx-dspark` remains `pushed_at=2026-09-01T10:54:45Z`; Layr remains
  `pushed_at=2026-08-29T07:05:19Z`.
- **oMLX:** no post-boundary focused issue/PR surfaced.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Qualification order:

1. pin/certify llama.cpp `v0.4.0` / exact tagged commit on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. PLE residency/page-cache/direct-read policy A/B;
4. sparse-QSA wide-prefill A/B;
5. pooled QSA-prefix retention / rollback correctness;
6. singleton MTP depth/acceptance A/B with **pre-verify snapshot + exact recurrent commit/replay**;
7. **multi-request pure-prefill state-isolation gate**: very different prompt lengths, serial
   references, PLE/GDN state-address correctness, rollback and verified-window commit;
8. only then adversarial parallel-MTP slot isolation and MTP concurrency >1;
9. compiled-decode B2/B4;
10. workload-derived cache matching, decoupling physical page geometry from prefix-match granularity
    where feasible;
11. combine passing mechanisms, then long-prefill-arrives-during-decode multi-agent stress.

Add exact recurrent/GDN packing, tiling and shared-load kernels to the **post-baseline** mining queue.
Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

No target/topology change. Keep PP2/layer ownership primary, TP2 control; AProjQ4 primary candidate;
request-adaptive speculation; mapping/OS/command-buffer/residency diagnostics; tool observation,
compaction and exact session gates. DS4 #964 is kernel-mechanism evidence only.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No target change. MLX #4409 is future serving/runtime kernel evidence. P69 remains separate and
unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Keep CUDA linked-runtime provenance, ubatch/prompt-shape stability, fully resident
Q3_K_XL + native MTP, draft-cache net-memory A/B, DFlash control, small-N verify, MTP-head quant and
GSQ-RCO. FreeToken #389 belongs to a future Qwen4-Exp GPU lane rather than current 27B calibration.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing architecture decisions

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stable llama.cpp `v0.4.0` remains the reproducible first baseline candidate; it does not imply
  optimized Flash throughput.
- Stage-local recurrent/GDN/QSA/expert state is preferred when residency permits.
- Multi-agent throughput is separate from B1 TG; independent requests can fill pipeline bubbles.
- MTP concurrency is correctness-gated.
- **Coherent output is not sufficient proof of correct MTP state.** Verify recurrent snapshots,
  verified-window commit/replay and acceptance-by-position.
- **Concurrent pure-prefill is a dedicated Flash correctness gate.** PLE/GDN slot state must match
  serial references under deliberately different request lengths/layouts.
- **GDN/recurrent Metal kernels remain a large bit-exact optimization surface.** Packing rows,
  sharing invariant loads, blocked state preparation and token tiling are prioritized mechanisms.
- **Physical cache-page size and prefix-match granularity should be independently selectable.**
- Prefix/session reuse remains separate from cold PP.
- DS4 #973 remains tool-observation-path first, compaction second.
- On 16-GB NVIDIA, nominally smaller draft KV can consume more total VRAM; net residency decides.
- CUDA benchmark provenance includes the actually linked runtime libraries; co-resident process
  configurations get their own graph-stability gate.
- Stronger-chip percentages and microbenchmarks do not move exact-machine targets by themselves.
- P69 exact verifier work remains isolated from external serving/runtime research.

The detailed rationale, confidence ladders and target-change rules remain centralized in
`RESEARCH-TARGETS.md`.
