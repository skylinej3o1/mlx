# Latest external runtime watch

## Active scope

Research remains centered on the hardware and execution lanes we actually own or are actively building:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**;
- **Qwen3.8-27B — one M1 Max 64 GB**;
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**;
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**;
- **Blazer / custom ~5.x-BPW execution work** when evidence is portable to those machines.

**Do not maintain a dedicated future M5 / M5 Ultra purchase lane.** Stronger Apple evidence is retained only when it teaches something portable about the active M1 lanes: kernels, memory ownership, cache/state precision, speculative execution, load transients, workspace lifetime, positional-state correctness or cluster/runtime design.

---

## Read order for every new research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md` — authoritative for TG/PP target identity; context is part of target identity.
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0111.md` — newest complete delta: Blackwell NVFP4-KV physical execution identity, screened rebase/rediscovery noise, no target changes.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-2022.md` — QSA bounded-workspace/allocator-lifetime evidence, DFlash per-layer normalization correctness, Qwen4Exp YaRN execution consistency.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md` — exact expert-offload read overlap, logical-vs-physical padded-token metadata, JIT specialization discipline, screened V4.1 Apple fast path.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md` — PP+MTP stage ownership, stage-local draft dependencies, pointer freshness and acceptance parity.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md` — dual-node Flash load transient, Tahoe/TB control transport, exact expert-offload capacity, Metal expert-tail geometry, grouped state writes and rollback correctness.
8. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` — BACKFILL / mechanism candidate only.
9. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` — portable mixed-precision/PLE/context-shape mechanisms only; stronger-hardware rates are transfer evidence.
10. Retain the 2026-09-10 and 2026-09-09 deltas/mining notes for the previously recorded TP2/PP ownership, recurrent rollback, QSA/MTP, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates the later dated deltas, this watch/mining chain remains part of canonical working context.

---

# Freshness discipline

The latest complete external-search pass covers substantive sources strictly after `2026-09-12 00:22:42 UTC` through:

**Hard source-freshness boundary for the next complete external search: `2026-09-12 05:11:02 UTC`.**

Source-specific mining and repository-only commits do not independently advance the global boundary. Evidence timestamp = substantive source timestamp, not rediscovery, crawler or rebase time.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | planning objective | **400 tok/s** | ~55-60% |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | ~55-60% | **110 tok/s native/exact-runtime** | ~60% |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | ~60-65% | **250 tok/s** | ~55-60% |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | ~60-65% | **180 tok/s** | ~60% |

Flash interpretation remains explicit: **40 TG sustained at ~128K active context** is the headline objective; a short-context 40 that collapses near 128K does not satisfy it. **400 PP** is cold-prefill. Neither is an exact measured dual-M1 receipt yet.

No canonical target moved in the 01:11 ET pass.

---

# Newest directly relevant evidence — 2026-09-12 01:11 ET

## Consumer-Blackwell NVFP4 KV execution geometry — vLLM #56550

**FRESH NEW / BLACKWELL MECHANISM TRANSFER. Not an exact RTX5070Ti16 speed receipt.**

PR #56550 was created inside this search window. It enables NVFP4 KV on SM120 consumer Blackwell through FlashInfer and makes the physical route agree across HND KV layout, linear/unswizzled V block-scale writes, the backend dtype gate, attention block-size/layout plumbing and SWA/main-cache block geometry.

Validation used RTX 5090 + Qwen3.8-27B-QUASAR-NVFP4 + TP2 + DFlash: the engine started, KV was actually allocated as NVFP4, CUDA graphs captured and end-to-end chat produced correct output. The evidence is explicitly from a combined SM120 stack and supplies no portable standalone TG/PP rate.

**Promote for the RTX 5070 Ti lane:** `KV precision` alone is not execution identity. Record requested dtype, physically allocated dtype, attention backend, KV layout, scale representation/write order, main/SWA block sizes, kernel divisibility/geometry, graph-capture route and actually executed route.

KV provenance becomes:

`requested -> configured -> backend-admitted -> physically allocated/layout-resolved -> graph-captured -> executed`.

A command-line low-bit KV setting therefore does not prove the measured path used the intended physical format. No target moves.

## Fresh-screen negative results

- No exact new dual-M1 Flash-Next receipt.
- No exact new M1 Max64 Qwen3.8-27B receipt.
- No fresh canonical RTX5070Ti16 target-topology receipt.
- No exact new dual-M1 DS4-0731 receipt; `antirez/ds4` had no post-boundary commit/issue activity.
- oMLX post-boundary activity was dominated by UI/i18n work; older runtime PRs were not reclassified as fresh because a fork or search index moved.
- vLLM #56177 resurfaced after a rebase. Its strong shared device-side expert-pool numbers are older evidence, not a fresh measurement.
- vLLM #56509 later-V4.1 SM120 geometry and #56323 DSv4 DFlash warmup/JIT activity did not add fresh target evidence in this window.
- screened llama.cpp activity did not provide a new Metal/Qwen target-lane result before the request cutoff.
- community/Hugging Face searches resurfaced useful 5070 Ti 27B measurements, but their underlying measurement/post times were older or not proven post-boundary; crawl time was not used as freshness.

---

# Important retained evidence

## QSA bounded workspace and allocator lifetime

vLLM #56500/#56457: a long-context QSA path can obey a per-allocation byte cap while allocator-retained memory still grows through a monotonic ladder of differently sized workspaces. A 254K Flash-Next cold prefill on 2x unified-memory GB10 failed exactly where the retained-allocation model predicted ~14 GB/rank. Prefer bounded reusable workspace or a small deliberate bucket set; record live tensors, allocator-reserved bytes and post-warmup allocation count separately.

## DFlash semantic-axis correctness

vLLM #56431: stacked per-layer K normalization was accidentally treated as one vector, moving GSM8K 0.487 -> 0.859 and acceptance 0.011 -> 0.459 after correction. Fused/stacked draft ops must preserve semantic axes, layer-to-parameter-row mapping and independent acceptance/task-quality validation.

## Qwen4Exp YaRN execution consistency

oMLX #3594: positional extension beyond native 262,144 must be installed and shared consistently by main attention, QSA/indexer and MTP. Configured context/rope metadata does not prove the fused/eager route actually executes the intended transform. Current ~128K objective remains inside native horizon.

## Exact expert offload / parallel read arrival

`jundot/omlx#3589`: immutable expert reads may arrive in parallel while cache ownership/LRU/state mutation remains deterministic and serial. Keep exact expert offload as emergency capacity lane, not primary dual-M1 architecture.

## Logical vs physical padded execution shape

vLLM #56181: physical graph/DP padding must be reflected consistently in attention metadata, slot/cache mapping and draft population. Requested logical tokens are not necessarily executed physical tokens.

## Dynamic request shape vs structural JIT specialization

vLLM #56153: layout/head/packing/tile/precision may be structural compile identity; high-cardinality token/batch/table lengths normally belong at runtime. Benchmark first compile, first new shape, warmed steady state and realistic shape churn separately.

## PP + MTP ownership

vLLM #46994: drafter stage, hidden-state producer/consumer, draft transport, stage-local embeddings/projections and QSA/indexer/spec-buffer pointer freshness are explicit. Final-output correctness does not prove speculative correctness because rejection can hide corrupt drafts.

## Dual-node Flash load transient

oMLX #3578 reduced sharding-phase peak allocation by about 4.2 GiB on a two-node Flash TP2 load by releasing superseded parameter trees. Load/transform/sharding/first-eval peaks remain distinct from steady-state residency.

## Transport / routed-tail / rollback

Keep control-plane route provenance separate from collective data-plane provenance; routed-expert occupancy/tail geometry is kernel identity; grouped narrow-state writes require ownership proof; rollback participants are preflighted before mutation and incompatible speculative state remains committed-only/clone-per-cycle as appropriate.

---

# Current consequences by active lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Required evidence includes:

1. load/transform/sharding/first-eval and steady-state memory separately;
2. live vs allocator-reserved workspace memory;
3. bounded QSA workspace reuse with no monotonic context-shape allocation ladder;
4. disjoint top-k scratch and physical workspace/ubatch ownership;
5. physical draft-head stage, hidden-state producer/consumer and explicit draft transport;
6. stage-local embedding/projection ownership;
7. QSA/indexer/spec buffer source and pointer freshness;
8. logical vs physically padded execution rows/tokens;
9. per-layer draft normalization mapping and dtype;
10. final-output parity, speculative acceptance parity and task-quality checks separately;
11. PP1-vs-PP2 acceptance under matched cells;
12. request-namespace and checkpoint-file lifetime separation;
13. expert occupancy/tail-tile geometry;
14. PLE as its own sparse placement plane;
15. code/prose/CJK/tool/low-acceptance long-context cells;
16. positional-transform provenance only if testing beyond native 262,144;
17. profitable singleton MTP + plain concurrent work remains the safe serving default until physical B2/B3/B4 recurrent/spec-state and workspace isolation are certified.

## Blazer / ~5.x BPW

Execution identity includes per-tensor stored precision, activation precision by phase, KV/state class precision, routed/shared experts, QSA/indexer precision, recurrent/control precision, MTP-head precision, packing/group/tile/lane geometry, routed occupancy/tails, load transients and workspace lifetime. Benchmark reserved bytes, live bytes and allocation count alongside TG/PP/task wall-clock.

## Qwen3.8-27B M1 / P69

No target movement. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

DFlash2 adds a correctness requirement only: fused/stacked draft normalization must preserve the per-layer axis.

## RTX5070Ti16

No target movement. Fully resident canonical speed lane remains distinct from host-backed capacity experiments. Certification now also requires KV physical-format provenance: allocated dtype, backend, layout, scale ordering, block geometry, graph capture and executed route.

## DS4-0731 dual M1

No target movement. Later V4.1 GPU/Apple evidence remains mechanism transfer unless it reproduces DS4 topology/runtime directly.

---

# Standing rules

- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Benchmark cell = actual executed route, not requested flags.
- Route provenance ladder: requested -> configured -> compiled -> armed/admitted -> executed.
- Memory provenance includes live tensors, allocator-retained workspace and load/materialization transients.
- Physical KV format provenance includes allocated dtype, backend, layout, scale encoding/order and block/kernel geometry.
- B2/B3/B4 require physically simultaneous independent requests with correct persistent state; configured/admitted/queued slots do not count.
- Final-output correctness is not sufficient speculative correctness.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **Do not actively track future M5/M5 Ultra purchase performance unless the user explicitly reopens that scope.**