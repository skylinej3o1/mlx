# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical target file:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP target identity. Context is part of target identity.**

3. Read the newest complete external-search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md`

   This is authoritative for the latest fresh pass: merged oMLX DeepSeek V4.1 Apple measurements, dual-node Flash TP2 load-transient evidence, Tahoe/TB control transport, exact expert-offload capacity evidence, Metal routed-expert tail geometry, grouped compact-state insertion, Affine8 long-context KV transfer and exact-target screening.

4. Retain the newest source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md`

   This mines MoBA only for a portable **execution** idea: preserve Qwen's learned selected-block IDs, invert query->block work into block->query groups for wide prefill, then merge partial results with online softmax. It is **BACKFILL / MECHANISM / FUTURE KERNEL CANDIDATE**, not a model replacement and not target evidence.

5. Retain the preceding source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md`

   This mines the mlx-serve Qwen3.8-Flash-Next 1M release and asymmetric mixed-precision pack. It is **TRANSFER / MECHANISM / USER-DEVELOPER RECEIPT**, not an exact dual-M1 receipt.

6. Retain the preceding complete deltas:

   - `RESEARCH-WATCH-2026-09-11-0639.md` — M5 A8 prefill, recurrent-checkpoint namespace lifetime, Metal fusion census/direct GDN state write, narrow-IQ lane utilization, shared-KV / PCP-spec / V4.1 runtime contracts and future-Apple backfill;
   - `RESEARCH-WATCH-2026-09-11-0026.md` — oMLX #3553 machine-exclusive A/B, M5 long-context equal-acceptance decomposition, rMLX gate hardening, heterogeneous-PP completion, ragged sparse MTP routing, deferred-free capacity and cluster recovery.

7. Retain the 2026-09-10 deltas for TP2 control topology, shared-round-skeleton gates, workload-shaped cache blocks, task wall-clock, sink-truth telemetry, custom-kernel ABI, bit-exact-vs-tolerance methodology, QSA/MTP shapes, two-Mac synchronization, the corrected r/oMLX Flash thread, oQ5e robustness, MTPLX speed-vs-reliability and PLE residency.

8. Retain the 2026-09-09 deltas for DS4 selective projection/quant shape, full-machine residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram work, quantized-FA capability, routed-MoE geometry, RTX5070Ti capacity evidence, Atlas ownership, replay boundaries and soak attribution.

9. Retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / future serving research**, not fresh target evidence.

10. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

Because `RESEARCH-STATE.md` predates the later dated deltas, the watch/mining chain remains part of canonical working context.

---

# Freshness discipline

The latest complete external-search pass covers sources strictly after `2026-09-11 10:39:19 UTC` through:

**Hard source-freshness boundary for the next complete external search: 2026-09-11 17:48:40 UTC.**

The MoBA and mlx-serve mining notes are source-specific and do not independently advance the global boundary. Repository-only commits must never create a search gap.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Flash interpretation is explicit:

- **40 TG sustained at ~128K active context** is the headline dual-M1 Flash objective;
- 40 only at short context while collapsing near 128K does **not** satisfy it;
- **400 PP** is the cold-prefill objective;
- 40 @ ~128K remains a planning target/hypothesis, not an exact measured dual-M1 receipt.

**The 13:48 complete pass moves no canonical target.**

---

# Newest fresh evidence — 2026-09-11 13:48 ET pass

## DeepSeek V4.1 Flash on Apple — new future-large-UMA lane

Merged `jundot/omlx#3574`, commit `f79b785485b36f81dcd669de86c1175f0507f851`.

M3 Ultra 512 GiB, DeepSeek-V4.1-Flash-oQ4e, code_python, temperature 1, prefix cache off, up-to-2K chunks, 128 generated tokens:

### Engram RAM

| context | PP MTP OFF -> ON | TG OFF | TG MTP ON | peak MLX / RSS GiB |
|---:|---:|---:|---:|---:|
| 4K | 457.99 -> 452.15 | 20.23 | 32.06 | 404.04 / 403.16 |
| 16K | 459.12 -> 454.77 | 20.00 | 34.72 | 404.52 / 403.19 |
| 32K | 452.19 -> 447.73 | 19.80 | 31.51 | 404.54 / 403.22 |
| 64K | 439.39 -> 435.56 | 19.67 | 39.66 | 404.56 / 403.25 |

### Engram SSD

| context | PP MTP OFF -> ON | TG OFF | TG MTP ON | peak MLX / RSS GiB |
|---:|---:|---:|---:|---:|
| 4K | 458.62 -> 452.48 | 19.96 | 34.45 | 289.60 / 295.05 |
| 16K | 441.40 -> 436.41 | 19.83 | 35.42 | 290.08 / 306.39 |
| 32K | 443.11 -> 442.52 | 19.75 | 34.14 | 290.09 / 315.37 |
| 64K | 429.41 -> 431.74 | 19.58 | 36.00 | 290.12 / 329.09 |

Important interpretation:

- real Apple V4.1 oQ4e PP is already roughly **430-460 tok/s** through 64K on M3 Ultra512;
- DSpark/Lightning MTP is roughly **32-40 TG** in these bounded sampled cells;
- SSD Engram removes roughly **114 GiB active MLX** at the 64K row while PP is nearly flat there;
- RSS growth shows that active MLX is not the complete residency story;
- no M5 Ultra numerical extrapolation is promoted from this receipt.

Track V4.1 large-Apple separately from DS4-0731. It is a future-hardware lane, not a canonical target row yet.

## Dual-node Flash TP2 load transient

Merged `jundot/omlx#3578`, commit `f37f7c5b80122e5a55bfa29b39425f7406f9686c`.

Progressive sharding retained references to unsharded layer arrays beside newly materialized shards, allowing up to **~1.5x layer-weight residency during initial load**. On a **2-node Qwen3.8-Flash-Next-REAP-288 TP2** load, explicit reference deletion / GC / MLX cache clear reduced sharding-phase peak allocation by **~4.2 GiB**.

Promotion:

- load/transform/sharding/first-eval peaks are distinct from steady-state model residency;
- on 64-GB nodes, steady-state fit does not prove load-time fit;
- release source/intermediate representations before materializing the next ownership form.

This is load-memory evidence, not PP2-vs-TP2 speed evidence.

## Tahoe / Thunderbolt control-plane transport

`jundot/omlx#3577` reports that `/usr/bin/python3` on macOS 26 Tahoe may fail outbound control sockets over TB bridge interfaces in noninteractive/background execution while the active venv Python works. The revised route tries direct TCP first and keeps bounded proxy fallback semantics.

Promotion: benchmark/bring-up provenance must distinguish **control-plane route** from the data-plane collective route and record executable, direct/proxy route, auth and deadline outcome.

No M4/TB5 numeric transfer to M1/TB4.

## Exact MoE expert offload

Merged commit `6df0d8d6499e86fa8610d8193b3d5b9b6bbc9093` streams non-resident experts from the original safetensors checkpoint under exact routing.

Representative Gemma-4-26B-A4B 4-bit rows show the capacity/latency tradeoff clearly: 100% residency ~14.20 GB / 122.5 TG / 0.30 s TTFT versus 25% ~4.57 GB / 40.1 TG / 9.6 s TTFT and 12.5% ~2.96 GB / 29.3 TG / 18.1 s TTFT.

Project stance: expert streaming is an emergency capacity lane, not the preferred dual-M1 Flash speed architecture. Prefer keeping routed experts resident when feasible and treating sparse PLE/n-gram placement separately.

## Metal routed-expert tail geometry

llama.cpp commit `5bda51bfbc62e64193221e639f6ad4e08767d760` skips the empty upper half of an NR1=32 `mul_mm_id` token tile when an expert receives <=16 rows in its last tile. Tests explicitly cover 1/15/16/17/32-row tails and the perf harness redraws expert IDs between iterations.

Promotion: Blazer/MoE kernel identity includes routed token occupancy and tail-tile utilization, not only `(M,N,K,bits,group size)`.

## Group small cache insertion across speculative layers

vLLM commit `1e1060f9988fa188fd243c093610889594ba18fd` reports **4-6x kernel-level** improvement for small-batch grouped MLA cache insertion, including FP8 conversion.

Portable candidate: group same-shaped small state writes across layers where ownership/lifetime permits. Do not convert kernel-level gain to model TG.

## Fresh open Affine8 KV experiment

`jundot/omlx#3582` was created at 16:33:49 UTC and remains open in this pass.

M5 Pro48 / Qwen3.8-27B-oQ4e, speculation disabled:

- Affine8 uses about **50.8-51.5%** of native FP16 attention-cache bytes in the reported sweep;
- full-model 200K row: ~255-259 PP and ~9.3-9.4 decode TG depending generation length;
- active MLX ~24.46 GiB, sampled physical peak up to 36.13 GiB for the 4,096-token generation cell;
- 250K was gracefully rejected under that run's dynamic memory ceiling;
- the PR explicitly does not claim semantic/retrieval quality from numerical error alone.

Promotion: KV/state precision is an independent design axis from weight BPW and activation precision. Selection-critical indexer state may warrant a different precision policy from bulk K/V.

## GLM-5.3 MTP transfer

Fresh GLM-5.3 Lightning-MTP work reiterates a critical correctness rule: preflight every recurrent/sparse rollback participant before mutating any state; clamp accepted length when necessary; keep incompatible speculative head state committed-only and clone per cycle.

Adjacent M3 Ultra256 result: 24.9 TG MTP-off vs 44.1-47.6 TG MTP-on at a 4.2K warm prompt, ~95% acceptance. This is not a Qwen or DS target receipt.

---

# Source-specific mining retained

## MoBA -> QSA block-inversion candidate

Do not transplant MoBA's trained selector. Keep only the execution candidate:

> freeze Qwen's existing selected-block IDs -> invert query/block edges -> process historical blocks for all assigned query rows -> merge per-query partials with online softmax.

Instrument reuse first. Promote only if whole-model **cold PP @ ~128K** improves enough to amortize bucketing/merge. Narrow B1/MTP stays on direct indexed selected-K/V paths.

## mlx-serve 1M Flash

Keep the asymmetric mixed-precision and PLE-placement conclusions:

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

No rMLX commit after the previous hard cutoff materially changes the speculative-state plan. No post-cutoff antirez/ds4 main change moves the DS4 lane. mlx-serve has no post-cutoff main commit in this complete window.

Rediscovered older web/HF/Reddit material is not fresh merely because it was crawled today.

---

# Current consequences by lane

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
12. profitable singleton MTP + plain concurrent work remains the safe default until physical B2/B3/B4 recurrent/spec state and workspace isolation are certified.

## Future Blazer / ~5.x BPW

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

## DeepSeek V4.1 / future large Apple UMA

Track as a separate future lane. The M3 Ultra512 oQ4e receipt is now a real baseline. Do not infer M5 Ultra rates by memory-bandwidth ratios alone.

## Qwen3.8-27B M1 Max64 / P69

No target movement. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

## RTX5070Ti16

No target movement. Fully resident Q3_K_XL/native-MTP stays the canonical speed lane; host-backed IQ4_XS stays separate capacity evidence.

## DS4-0731 dual M1

No target movement. V4.1 is a separate architecture/model lane.

---

# Standing decisions

- **40 TG @ ~128K remains the actual dual-M1 Flash headline objective.**
- **400 PP remains the cold-prefill objective.**
- No target row moved in the 13:48 pass.
- M3 Ultra512 V4.1 is strong future-Apple evidence, not an M5 Ultra or DS4-0731 receipt.
- Steady-state model fit does not prove cluster load-time fit.
- Control-plane route provenance is separate from data-plane transport provenance.
- Blazer now explicitly spans stored weights + activations + runtime state precision + real routing/tile geometry.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **P69 remains isolated.**
