# Latest external runtime watch

## Active scope

Research is currently centered on the hardware and execution lanes we actually own or are actively building:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**;
- **Qwen3.8-27B — one M1 Max 64 GB**;
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**;
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**;
- **Blazer / custom ~5.x-BPW execution work** when evidence is portable to those machines.

**Do not maintain a dedicated future M5 / M5 Ultra purchase lane yet.** Stronger-Apple-hardware evidence may still be retained when it directly teaches us something portable about kernels, memory ownership, cache/state precision, speculative execution, load transients, or cluster/runtime design. It must not create a separate target, shopping roadmap, or ongoing search obligation.

Historical dated watches remain archival evidence. Where an older watch labels M5/M5-Ultra or large-Apple-UMA work as a future lane, this scope statement supersedes that planning interpretation.

---

## Read order for every new research pass

1. Read the durable canonical research state:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical target file:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP target identity. Context is part of target identity.**

3. Read the newest complete external-search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md`

   Use it for the directly relevant two-node Flash TP2 load-transient evidence, Tahoe/TB control transport, exact expert-offload capacity evidence, Metal routed-expert tail geometry, grouped compact-state insertion, rollback correctness and exact-target screening. Its V4.1/M5-class material is **transfer-only archival evidence**, not an active future-hardware lane.

4. Retain the newest source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md`

   This mines MoBA only for a portable execution idea: preserve Qwen's learned selected-block IDs, invert query->block work into block->query groups for wide prefill, then merge partial results with online softmax. It is **BACKFILL / MECHANISM / FUTURE KERNEL CANDIDATE**, not a model replacement and not target evidence.

5. Retain the preceding source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md`

   This remains useful for Flash mixed-precision shape, PLE placement, context/content-shape benchmarking and long-context runtime mechanisms. Treat M5-specific rates as transfer evidence only.

6. Retain preceding complete deltas when they contain mechanisms relevant to the active hardware lanes. Do **not** continue mining stronger future Apple hardware merely to build a future purchase case.

7. Retain the 2026-09-10 deltas for TP2 control topology, shared-round-skeleton gates, workload-shaped cache blocks, task wall-clock, sink-truth telemetry, custom-kernel ABI, bit-exact-vs-tolerance methodology, QSA/MTP shapes, two-Mac synchronization, the corrected r/oMLX Flash thread, oQ5e robustness, MTPLX speed-vs-reliability and PLE residency.

8. Retain the 2026-09-09 deltas for DS4 selective projection/quant shape, full-machine residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram mechanisms, quantized-FA capability, routed-MoE geometry, RTX5070Ti capacity evidence, Atlas ownership, replay boundaries and soak attribution.

9. Retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / mechanism research**, not fresh target evidence.

10. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

Because `RESEARCH-STATE.md` predates the later dated deltas, the watch/mining chain remains part of canonical working context.

---

# Freshness discipline

The latest complete external-search pass covers sources strictly after `2026-09-11 10:39:19 UTC` through:

**Hard source-freshness boundary for the next complete external search: 2026-09-11 17:48:40 UTC.**

Source-specific mining and repository-only commits do not independently advance the global boundary. Future searches should prioritize exact/current hardware lanes first, then portable mechanisms. Do not spend search budget on future-M5 purchase tracking unless the user explicitly reopens that scope.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Flash interpretation remains explicit:

- **40 TG sustained at ~128K active context** is the headline dual-M1 Flash objective;
- 40 only at short context while collapsing near 128K does **not** satisfy it;
- **400 PP** is the cold-prefill objective;
- 40 @ ~128K remains a planning target/hypothesis, not an exact measured dual-M1 receipt.

No canonical target moved in the 13:48 pass or in this scope correction.

---

# Newest directly relevant evidence — 2026-09-11 13:48 ET pass

## Dual-node Flash TP2 load transient

Merged `jundot/omlx#3578`, commit `f37f7c5b80122e5a55bfa29b39425f7406f9686c`.

Progressive sharding retained references to unsharded layer arrays beside newly materialized shards, allowing up to **~1.5x layer-weight residency during initial load**. On a **2-node Qwen3.8-Flash-Next-REAP-288 TP2** load, explicit reference deletion / GC / MLX cache clear reduced sharding-phase peak allocation by **~4.2 GiB**.

Promotion:

- load/transform/sharding/first-eval peaks are distinct from steady-state model residency;
- on 64-GB nodes, steady-state fit does not prove load-time fit;
- release source/intermediate representations before materializing the next ownership form.

This is load-memory evidence, not PP2-vs-TP2 speed evidence.

## Tahoe / Thunderbolt control-plane transport

`jundot/omlx#3577` reports a macOS/TB control-path failure mode where the runtime used to open the rank-control socket can matter independently of the data-plane collective path. The revised route tries direct TCP first and retains bounded proxy fallback semantics.

Promotion: bring-up provenance distinguishes **control-plane route** from data-plane transport and records executable, direct/proxy route, auth and deadline outcome. No stronger-Mac/TB numeric rate transfers to M1/TB4.

## Exact MoE expert offload

Merged commit `6df0d8d6499e86fa8610d8193b3d5b9b6bbc9093` streams non-resident experts from the original safetensors checkpoint under exact routing.

Project stance: expert streaming is an emergency **capacity** lane, not the preferred dual-M1 Flash speed architecture. Prefer keeping routed experts resident when feasible and treating sparse PLE/n-gram placement separately.

## Metal routed-expert tail geometry

llama.cpp commit `5bda51bfbc62e64193221e639f6ad4e08767d760` skips the empty upper half of an NR1=32 `mul_mm_id` token tile when an expert receives <=16 rows in its last tile. Tests explicitly cover 1/15/16/17/32-row tails.

Promotion: Blazer/MoE kernel identity includes routed token occupancy and tail-tile utilization, not only `(M,N,K,bits,group size)`.

## Grouped small state writes

vLLM commit `1e1060f9988fa188fd243c093610889594ba18fd` reinforces a portable candidate: group same-shaped narrow state/cache writes across layers where ownership/lifetime permits. Treat its reported kernel-level gain only as mechanism evidence.

## Rollback correctness

Fresh GLM-5.3 Lightning-MTP work reiterates a critical rule: preflight every recurrent/sparse rollback participant before mutating any state; clamp accepted length when necessary; keep incompatible speculative head state committed-only and clone per cycle. This is architectural transfer, not a target receipt.

---

# Stronger-hardware evidence policy

Evidence from M3/M4/M5-class Apple hardware is still allowed in the repository when it answers a question we are actively solving on M1, such as:

- exact tensor/phase shape behavior;
- kernel lane/tile utilization;
- QSA selected-row execution structure;
- MTP acceptance/cycle accounting;
- recurrent rollback ownership;
- PLE/Engram sparse-residency mechanisms;
- load/materialization transients;
- cache/state precision tradeoffs;
- control/data-plane cluster correctness.

But it should be classified **TRANSFER / MECHANISM**, not promoted into a future-purchase lane. Do not maintain M5 Max/M5 Ultra target rates, expected configurations, purchase assumptions, or dedicated future-hardware watch sections unless requested later.

---

# Source-specific mining retained

## MoBA -> QSA block-inversion candidate

Do not transplant MoBA's trained selector. Keep only the execution candidate:

> freeze Qwen's existing selected-block IDs -> invert query/block edges -> process historical blocks for all assigned query rows -> merge per-query partials with online softmax.

Instrument reuse first. Promote only if whole-model **cold PP @ ~128K** improves enough to amortize bucketing/merge. Narrow B1/MTP stays on direct indexed selected-K/V paths.

## mlx-serve 1M Flash

Keep only conclusions portable to the active project:

- Q4-ish routed experts + higher-precision control/state/shared/QSA/MTP is a first-class Blazer candidate family;
- n-gram/PLE is a separate sparse lookup plane with resident/SSD/hybrid/stage-local policies;
- context **and content shape** are benchmark identity;
- warm prefix/recurrent-checkpoint operation stays separate from cold PP.

---

# Screened / no target movement

No fresh exact receipt was found for:

- 2x M1 Max64/TB4 Flash-Next;
- one M1 Max64 Qwen3.8-27B;
- RTX5070Ti16 fully-resident Q3_K_XL/native-MTP canonical speed lane;
- 2x M1 Max64/TB4 DS4-0731.

Rediscovered older web/HF/Reddit material is not fresh merely because it was crawled today.

---

# Current consequences by active lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control.

Add/retain:

1. load-time source/transform/sharding/first-eval peaks in admission telemetry;
2. explicit release of superseded parameter trees before next representation materializes;
3. control-plane route/executable/auth/deadline provenance distinct from data-plane transport;
4. actual fusion census;
5. exact recurrent-state producer/destination ownership;
6. request-namespace lifetime independent of checkpoint-file lifetime;
7. device/global cursor truth through partitioning and rejection;
8. expert occupancy/tail-tile geometry;
9. grouped narrow-state writes only with ownership/lifetime proof;
10. PLE placement as a separately measured sparse plane;
11. code/prose/CJK/tool/low-acceptance long-context cells;
12. profitable singleton MTP + plain concurrent work remains the safe default until physical B2/B3/B4 recurrent/spec-state and workspace isolation are certified.

## Blazer / ~5.x BPW

Execution identity includes:

- per-tensor stored precision;
- activation precision by phase;
- KV/state precision by state class;
- routed/shared expert distinction;
- QSA/indexer precision;
- recurrent/control precision;
- MTP-head precision;
- packing/group and exact tile/lane geometry;
- routed expert occupancy/tail utilization;
- load/materialization transient memory;
- task success, difficult-tail robustness, MTP acceptance, task wall-clock, TG/PP, memory/context and PP balance.

The destination remains a quality-preserving ~5.x-BPW operating point, not a nominal bit-rate contest.

## Qwen3.8-27B M1 Max64 / P69

No target movement. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

## RTX5070Ti16

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed IQ4_XS remains separate capacity evidence.

## DS4-0731 dual M1

No target movement. Evidence from later DeepSeek architectures is mechanism transfer only unless it reproduces the DS4 topology/runtime question directly.

---

# Standing rules

- Evidence timestamp = substantive source timestamp, not rediscovery time.
- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Benchmark cell = actual executed route, not requested flags.
- Route provenance ladder remains requested -> configured -> compiled -> armed/admitted -> executed.
- B2/B3/B4 require physically simultaneous independent requests with correct persistent state; configured/admitted/queued slots do not count.
- Safe serving remains profitable singleton MTP + plain concurrent work until per-slot recurrent/spec state isolation, physical recurrent capacity, PP+MTP ownership and concurrent-state semantics are certified.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **Do not actively track future M5/M5 Ultra purchase performance until the user reopens that scope.**
