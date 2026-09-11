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

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md`

   Use it for the fresh exact expert-offload I/O-overlap evidence, DFlash/DSpark logical-vs-physical padded-token correctness, dynamic-shape JIT specialization discipline, and the screened DeepSeek V4.1 stronger-Apple fast-path work. It moves no canonical target.

4. Retain the preceding complete delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md`

   Use it for PP+MTP physical-stage ownership/correctness, stage-local draft dependencies, pointer freshness, speculative acceptance parity, and the closure of the duplicate oMLX expert-streaming lane.

5. Retain the preceding complete delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md`

   Use it for the directly relevant two-node Flash TP2 load-transient evidence, Tahoe/TB control transport, exact expert-offload capacity evidence, Metal routed-expert tail geometry, grouped compact-state insertion, rollback correctness and exact-target screening. Its V4.1/M5-class material is **transfer-only archival evidence**, not an active future-hardware lane.

6. Retain the newest source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md`

   This mines MoBA only for a portable execution idea: preserve Qwen's learned selected-block IDs, invert query->block work into block->query groups for wide prefill, then merge partial results with online softmax. It is **BACKFILL / MECHANISM / FUTURE KERNEL CANDIDATE**, not a model replacement and not target evidence.

7. Retain the preceding source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md`

   This remains useful for Flash mixed-precision shape, PLE placement, context/content-shape benchmarking and long-context runtime mechanisms. Treat M5-specific rates as transfer evidence only.

8. Retain preceding complete deltas when they contain mechanisms relevant to the active hardware lanes. Do **not** continue mining stronger future Apple hardware merely to build a future purchase case.

9. Retain the 2026-09-10 deltas for TP2 control topology, shared-round-skeleton gates, workload-shaped cache blocks, task wall-clock, sink-truth telemetry, custom-kernel ABI, bit-exact-vs-tolerance methodology, QSA/MTP shapes, two-Mac synchronization, the corrected r/oMLX Flash thread, oQ5e robustness, MTPLX speed-vs-reliability and PLE residency.

10. Retain the 2026-09-09 deltas for DS4 selective projection/quant shape, full-machine residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram mechanisms, quantized-FA capability, routed-MoE geometry, RTX5070Ti capacity evidence, Atlas ownership, replay boundaries and soak attribution.

11. Retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / mechanism research**, not fresh target evidence. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

Because `RESEARCH-STATE.md` predates the later dated deltas, the watch/mining chain remains part of canonical working context.

---

# Freshness discipline

The latest complete external-search pass covers sources strictly after `2026-09-11 18:30:00 UTC` through:

**Hard source-freshness boundary for the next complete external search: 2026-09-11 22:31:55 UTC.**

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

No canonical target moved in the 18:31 ET pass.

---

# Newest directly relevant evidence — 2026-09-11 18:31 ET pass

## oMLX #3589 — parallel exact expert-miss reads

Open, non-draft PR `jundot/omlx#3589` changes exact MoE expert offload from serial synchronous memmap reads on the compute thread to a two-phase path:

1. classify misses without cache mutation and issue bounded parallel `os.pread` reads;
2. preserve the original serial install order for slot writes, LRU victims, hit/miss counters, maps and resident-byte accounting.

The key transferable design rule is:

> **I/O arrival may be parallel while cache ownership/state mutation remains deterministic and serial.**

Physical A/B on M5 Pro 64 GB with `Vontra/Qwen3.8-Flash-Next-MLX-oQ2-MTP`, PLE mmap, MTP off, greedy:

| residency | cell | serial | parallel pread |
|---:|---|---:|---:|
| 25% | 3461-token TTFT | 183 s | **18.7 s** |
| 25% | decode after prompt | 4.4 tok/s | **17.7 tok/s** |
| 25% | 122-token warm decode | 2.3 tok/s | **16.2 tok/s** |
| 68.8% | 3461-token TTFT | 30.1 s | **4.5 s** |
| 68.8% | decode after prompt | 13.6 tok/s | **19.7 tok/s** |
| 68.8% | 122-token warm decode | **23.9 tok/s** | 22.4 tok/s |

Generated text was identical to the serial baseline; loaded size was unchanged. The low-residency results show the old path was often I/O-latency bound, not bandwidth bound. The high-residency warm row also shows the machinery is not automatically a win once misses are rare.

Promotion for any capacity-constrained Flash experiment:

- exact router decisions remain authoritative;
- parallelize immutable reads, not ownership mutation;
- bound workers and in-flight bytes;
- record residency, miss rate, bytes/ops, TTFT, task wall-clock and TG;
- include high-residency/warm regression cells;
- schedule-ahead prefetch remains a candidate, not a promoted result.

This improves the emergency capacity/offload lane but **does not displace resident routed experts or PP2/layer ownership as the primary dual-M1 Flash architecture**.

## vLLM #56181 — logical vs physical padded-token metadata

Merged commit `9dcf6bf344caa7793bae0b45a7896d3f8e03a01a` fixes DFlash/DSpark speculative attention metadata under DP padding.

With DP > 1, synchronization may add physical padding tokens. The failing path mixed logical query-token counts with the padded execution token count, so attention metadata could disagree with the actual query tensor. The fix uses the padded physical count under FULL graph execution and the logical count otherwise, through a shared metadata builder used by DFlash/DSpark and later MTP/EAGLE single-draft steps.

Project promotion:

- distinguish **logical request rows/tokens** from **physical padded execution rows/tokens**;
- record graph/capture bucket shape;
- require attention metadata, slot/cache mapping and speculative draft population to describe the same physical execution shape;
- requested row count is not automatically executed row count;
- final-output parity is not sufficient speculative correctness because rejection/masking can hide bad drafts.

The PR contains a Qwen3.8-27B + DFlash2 cell with essentially unchanged acceptance/throughput and a DP2 DFlash cell that goes from crash to successful serving. Absolute GPU rates are not portable and move no target.

## vLLM #56153 — keep dynamic request shapes out of JIT identity

Merged commit `2d75e586fcaf88231f7a75f482dc8bfb5ad9da10` removes runtime token/batch/block counts from the compile-time specialization identity of a DSV4 indexer quant-cache gather kernel.

The old path marked total tokens, batch count, block-table width and block count as compile-time constants. High-cardinality request-shape changes could therefore create new compiled kernels; the PR reports several seconds of cold latency in local-serving situations. True structural constants such as layout, head dimension and tile geometry remain specialized; kernel math/output are unchanged.

Promotion for QSA/indexer/Blazer/custom kernels:

- **structural specialization:** layout, head dimension, packing, tile geometry, precision, algorithm choice;
- **runtime shape:** token count, batch count, request padding and table/block lengths unless the algorithm truly requires specialization.

Benchmark first-ever compile, first request for a new runtime shape, warmed steady state, and realistic shape churn separately. A faster steady-state kernel can still lose task wall-clock if normal request variation causes recompilation.

## oMLX #3590 — screened stronger-Apple V4.1 fast path

Open `jundot/omlx#3590` reports an M3 Ultra DeepSeek-V4.1 fast path around 26.5-27.2 tok/s decode / 490-500 tok/s ~2K prefill with Engram stub versus ~15.5 / ~337 on the stock path; mmap + hot cache is around 25.5 / 481, and B8 aggregate decode is reported near 79.5 tok/s.

This is **later-architecture stronger-Apple transfer only**, not DS4-0731 evidence and not a future-hardware planning lane.

Portable notes retained:

- preserve shared cache/pool identity when singleton caches become batched caches;
- append-only state needs explicit semantics rather than assuming one shared processed cursor;
- large-UMA wired-memory policy can dominate execution when the working set otherwise thrashes;
- aggregate batching speed and independent-singleton numerical equivalence require separate tests; the PR itself notes batch-vs-independent B1 is not yet bit-exact.

No target movement.

---

# Preceding directly relevant evidence retained — 14:30 ET pass

## vLLM #46994 — PP + MTP ownership/correctness

Merged `6fe67cbbf3e43da89bebf6ab0eeaca4ba6c75663` establishes that the speculative drafter has a real physical PP-stage owner, stage/rank heuristics can silently skip required draft work, tied/shared weights still need physical ownership on the executing stage, and stale sparse-indexer aliases can collapse acceptance while target rejection preserves apparently correct final output.

For dual-M1 Flash PP2, retain:

- physical draft-head stage;
- target hidden-state producer and draft consumer;
- explicit draft-token transport;
- stage-local embedding/projection ownership;
- QSA/indexer/spec buffer source and pointer freshness;
- final-output parity separate from draft-acceptance parity;
- PP1-vs-PP2 acceptance parity before interpreting TG differences;
- fail-closed semantics when a speculative participant is absent.

## oMLX #3359 — duplicate expert-streaming lane closed

The older draft SSD expert-streaming branch closed without merge after upstream expert offload landed. Do not double-count its historical benchmark body as fresh evidence.

---

# Preceding directly relevant evidence retained — 13:48 ET pass

## Dual-node Flash TP2 load transient

Merged `jundot/omlx#3578`, commit `f37f7c5b80122e5a55bfa29b39425f7406f9686c`, showed progressive sharding retaining both unsharded and sharded representations. Explicit cleanup reduced sharding-phase peak allocation by about **4.2 GiB** on a two-node Flash-Next TP2 load.

Load/transform/sharding/first-eval peaks remain separate admission phases from steady-state residency.

## Tahoe / Thunderbolt control plane

`jundot/omlx#3577` shows rank-control transport can fail independently of data-plane collectives. Record executable/runtime, direct/proxy path, auth and deadline outcome separately from collective-route provenance.

## Exact MoE expert offload

Merged `6df0d8d6499e86fa8610d8193b3d5b9b6bbc9093` provides the maintained exact capacity lane. Prefer resident routed experts when feasible; treat sparse PLE/n-gram placement separately.

## Metal routed-expert tail geometry

llama.cpp `5bda51bfbc62e64193221e639f6ad4e08767d760` reinforces routed token occupancy and tail-tile utilization as part of MoE kernel identity.

## Grouped small state writes and rollback correctness

Retain grouped narrow-state writes only where ownership/lifetime permits. Recurrent/sparse rollback participants must be preflighted before mutation; incompatible speculative state remains committed-only or clone-per-cycle as appropriate.

---

# Stronger-hardware evidence policy

Evidence from M3/M4/M5-class Apple hardware is allowed only when it answers an active M1 question, such as tensor/phase shape, kernel occupancy, QSA selected-row execution, MTP acceptance/cycle accounting, recurrent rollback ownership, PLE/Engram sparse-residency mechanisms, load transients, cache/state precision, compile lifecycle or cluster correctness.

Classify it **TRANSFER / MECHANISM**, not a future-purchase lane. Do not maintain M5 Max/M5 Ultra target rates, purchase assumptions or dedicated watch sections unless requested later.

---

# Source-specific mining retained

## MoBA -> QSA block-inversion candidate

Keep only the execution candidate:

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

Additional screening:

- `jundot/omlx#3583` was created before this freshness window; later update activity does not make its earlier format-metadata body fresh;
- oMLX ANE-bank accounting #3425 remains part of the older hidden-resident-memory chain, not fresh evidence here;
- llama.cpp post-boundary activity produced no new exact Apple Metal / target-hardware receipt;
- `antirez/ds4` had no commit or issue activity in this window;
- rediscovered M1-Max 27B and M4-Pro Flash benchmark pages substantively predate the window and remain **RECOVERED OLDER EVIDENCE**;
- same-day community multi-GPU 27B reports use different hardware/topologies/quants and do not supersede the RTX5070Ti16 canonical lane.

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
6. physical draft-head stage and explicit draft-token transport;
7. stage-local embedding/projection ownership for the drafter;
8. QSA/indexer/spec buffer source and pointer freshness through each cycle;
9. **logical rows/tokens vs physical padded execution rows/tokens**;
10. graph/capture bucket and compiled execution-shape identity;
11. final-output parity separate from speculative-acceptance parity;
12. PP1-vs-PP2 acceptance parity under identical cells;
13. compiled-kernel cache cardinality plus first-compile/new-shape/warm timing;
14. request-namespace lifetime independent of checkpoint-file lifetime;
15. device/global cursor truth through partitioning and rejection;
16. expert occupancy/tail-tile geometry;
17. grouped narrow-state writes only with ownership/lifetime proof;
18. PLE placement as a separately measured sparse plane;
19. if expert offload is required, parallel immutable reads + serial deterministic publication/cache mutation, with high-residency regression cells;
20. code/prose/CJK/tool/low-acceptance long-context cells;
21. profitable singleton MTP + plain concurrent work remains the safe default until physical B2/B3/B4 recurrent/spec-state and workspace isolation are certified.

## Blazer / ~5.x BPW

Execution identity includes per-tensor stored precision, activation precision by phase, KV/state precision by state class, routed/shared expert distinction, QSA/indexer precision, recurrent/control precision, MTP-head precision, packing/group and tile/lane geometry, routed-expert occupancy/tails, load transients, task success, difficult-tail robustness, MTP acceptance, task wall-clock, TG/PP and memory/context balance.

Add **compiled-kernel specialization identity**: distinguish structural specialization from high-cardinality runtime request shape. Cold compile, first-new-shape latency, shape-churn wall-clock and warmed kernel rate are separate benchmark cells.

The destination remains a quality-preserving ~5.x-BPW operating point, not a nominal bit-rate contest.

## Qwen3.8-27B M1 Max64 / P69

No target movement. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

## RTX5070Ti16

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed capacity experiments stay separate. No fresh exact-rig receipt appeared.

## DS4-0731 dual M1

No target movement. Later-architecture or GPU evidence is mechanism transfer only unless it reproduces the DS4-0731 topology/runtime question directly.

---

# Standing rules

- Evidence timestamp = substantive source timestamp, not rediscovery time.
- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Benchmark cell = actual executed route, not requested flags.
- Route provenance ladder remains requested -> configured -> compiled -> armed/admitted -> executed.
- **Logical work shape and physical padded/compiled execution shape are both part of provenance.**
- B2/B3/B4 require physically simultaneous independent requests with correct persistent state; configured/admitted/queued slots do not count.
- Safe serving remains profitable singleton MTP + plain concurrent work until per-slot recurrent/spec state isolation, physical recurrent capacity, PP+MTP ownership and concurrent-state semantics are certified.
- Final-output correctness is not sufficient speculative correctness; rejection can mask corrupt drafts.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **Do not actively track future M5/M5 Ultra purchase performance until the user reopens that scope.**
