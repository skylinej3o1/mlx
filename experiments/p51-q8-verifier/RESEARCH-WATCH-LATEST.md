# Latest external runtime watch

## Active scope

Research remains centered on the hardware and execution lanes we actually own or are actively building:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**;
- **Qwen3.8-27B — one M1 Max 64 GB**;
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**;
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**;
- **Blazer / custom ~5.x-BPW execution work** when evidence is portable to those machines.

**Do not maintain a dedicated future M5 / M5 Ultra purchase lane.** Stronger-hardware evidence is retained only when it teaches something portable about the active lanes: kernels, memory ownership, cache/state precision, speculative execution, load transients, workspace lifetime, physical geometry, positional-state correctness or cluster/runtime design.

---

## Read order for every new research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md` — authoritative for TG/PP target identity; context is part of target identity.
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0313.md` — newest complete delta: M1-targeted Qwen3.8-27B DFlash2 FP16 candidate, Flash-Next proposal-head precision A/B, speculative-verifier peak profiling, shared-expert physical padding/fusion, fresh screening.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0111.md` — Blackwell NVFP4-KV physical execution identity and screened rebase/rediscovery noise.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-2022.md` — QSA bounded-workspace/allocator-lifetime evidence, DFlash per-layer normalization correctness, Qwen4Exp YaRN execution consistency.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md` — exact expert-offload read overlap, logical-vs-physical padded-token metadata, JIT specialization discipline, screened V4.1 Apple fast path.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md` — PP+MTP stage ownership, stage-local draft dependencies, pointer freshness and acceptance parity.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md` — dual-node Flash load transient, Tahoe/TB control transport, exact expert-offload capacity, Metal expert-tail geometry, grouped state writes and rollback correctness.
9. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` — BACKFILL / mechanism candidate only.
10. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` — portable mixed-precision/PLE/context-shape mechanisms only; stronger-hardware rates are transfer evidence.
11. Retain the 2026-09-10 and 2026-09-09 deltas/mining notes for the previously recorded TP2/PP ownership, recurrent rollback, QSA/MTP, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates the later dated deltas, this watch/mining chain remains part of canonical working context.

---

# Freshness discipline

The latest complete external-search pass covers substantive sources strictly after `2026-09-12 05:11:02 UTC` through the current request. One older user-supplied checkpoint was separately admitted as a **BACKFILL / experiment candidate**, not mislabeled as fresh evidence.

**Hard source-freshness boundary for the next complete external search: `2026-09-12 07:13:21 UTC`.**

Evidence timestamp = substantive source timestamp, not rediscovery, crawler, rebase or comment time.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | planning objective | **400 tok/s** | ~55-60% |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | ~55-60% | **110 tok/s native/exact-runtime** | ~60% |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | ~60-65% | **250 tok/s** | ~55-60% |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | ~60-65% | **180 tok/s** | ~60% |

Flash interpretation remains explicit: **40 TG sustained at ~128K active context** is the headline objective; short-context 40 that collapses near 128K does not satisfy it. **400 PP** is cold-prefill. Neither is an exact measured dual-M1 receipt yet.

No canonical target moved in the 03:13 ET pass.

---

# Newest directly relevant evidence — 2026-09-12 03:13 ET

## M1-targeted Qwen3.8-27B DFlash2 FP16 drafter

`deepsweet/Qwen3.8-27B-DFlash2-FP16`

**BACKFILL / USER-SUPPLIED EXPERIMENTAL CANDIDATE. Not a fresh receipt and not target evidence.**

This is the ~2B Qwen3.8-27B DFlash2 drafter converted from the stock BF16 checkpoint to FP16. Its card explicitly targets M1/M2 Apple Silicon and points M3+ users back to the BF16 original. That makes it directly worth testing on our single M1 Max64 lane, but there is no direct Qwen3.8/M1 measurement yet.

Promote a matched three-arm experiment:

1. plain Qwen3.8-27B;
2. stock BF16 `z-lab/Qwen3.8-27B-DFlash2`;
3. FP16 `deepsweet/Qwen3.8-27B-DFlash2-FP16`.

Start at **4K / 16K / 32K**; extend to **64K / 128K** only if FP16 remains profitable. Record target TG/E2E, TTFT/PP, acceptance rate and mean acceptance length, draft latency, peak/resident memory, actual draft dtype/route and task quality. Faster proposal generation alone is insufficient if acceptance falls.

Older `jundot/omlx#880` M1/M2-oriented Qwen3.6 evidence supports the FP16-drafter mechanism at short/medium context but is transfer evidence only; do not project its percentage gain onto Qwen3.8.

**P69 remains untouched.**

## Flash-Next proposal-head precision separation — vLLM #56577

**FRESH / STRONGER-HARDWARE FLASH MECHANISM TRANSFER.**

For Qwen4Exp/MTP, the target verifier keeps its BF16 vocabulary head while proposal projection uses a private rowwise-E4M3 copy. On two DGX Spark GB10 nodes, TP2/MTP4 with `nvidia/Qwen3.8-Flash-Next-NVFP4`, the A/B reported:

- default FlashInfer GDN: **63.075 -> 71.2475 tok/s (+12.96%)**;
- explicit Triton GDN: **62.148 -> 72.359 tok/s (+16.43%)**;
- an earlier token-capture run: **63.130 -> 69.317 tok/s (+9.80%)**, acceptance **0.7823 -> 0.7781**.

The private proposal copy added about **318 MB/rank** and modestly reduced effective KV capacity. Single-run quality results were mixed rather than a no-regression proof.

**Promote:** target-verifier precision and drafter/proposal-head precision are separate execution-identity dimensions. Record proposal activation scaling, private derived-weight lifetime/memory, resulting KV-capacity change, acceptance and task quality. This supports mixed precision conceptually; it is not evidence that FP8 is the right Metal format and does not move the M1 target.

## Speculative-verifier peak profiling — vLLM #56572

**FRESH / MEMORY-ADMISSION + PROFILING TRANSFER.**

An intermittent Gemma4 MTP OOM involved another **1.33 GiB** logits soft-cap allocation. More generally, startup profiling covered up to **1,024 logits rows** while runtime speculative verification reached **2,721 rows**. The patch removes an avoidable full-vocabulary temporary and profiles the real verification/sampling/rejection route before sizing KV capacity.

**Promote:** capacity proof includes a distinct **spec-verifier peak-shape phase**. Track maximum physical verifier rows, full-vocabulary temporary lifetime, actual sampling/rejection path, TP projection/sharding/communication buffers where applicable, and startup-profile shape versus maximum reachable runtime shape. A smaller startup shape is not proof of runtime capacity.

## Shared-expert physical padding / fusion — vLLM #56568

**FRESH / LATER-DEEPSEEK GPU MECHANISM TRANSFER. Not DS4-0731 target evidence.**

DeepSeek-V4.1-Flash routed experts used a physically padded 2560 intermediate while its 2304-wide shared expert retained checkpoint geometry, forcing all 40 layers to a serial shared-MLP path. Zero-padding the shared expert with unit scales enabled native MegaMoE fusion.

On 8x B200 TP8/EP the fresh implementation A/B reported:

- batch 1: **96.3 -> 107.1 tok/s (+11.2%)**;
- batch 16: **715.0 -> 814.6 (+13.9%)**;
- batch 64: **1212.3 -> 1397.3 (+15.3%)**.

The fused path added about **1.87 GiB/rank** model-load memory. This is later-architecture CUDA transfer evidence only.

**Promote:** MoE execution identity distinguishes logical checkpoint shape from physical routed/shared-expert padded shape, padded-lane scale semantics, actual fused/fallback route, padding memory cost and tail/tile occupancy. A logically compatible shared expert can silently prevent the intended fused route.

## Resolved KV dtype observability — vLLM #56571

Small but useful provenance reinforcement: logging `auto` is not sufficient; benchmark records should capture the **resolved physical KV dtype**. No target impact.

## Fresh-screen negatives

- `jundot/omlx` main: no post-boundary commits; no fresh exact M1/Qwen3.8 receipt.
- `antirez/ds4`: no post-boundary commits; no fresh DS4-0731 receipt.
- screened llama.cpp activity after the boundary was SYCL/RPC/server maintenance rather than new Metal/Qwen active-lane measurement.
- no exact new dual-M1 Flash-Next receipt;
- no exact new M1 Max64 Qwen3.8-27B receipt;
- no canonical RTX5070Ti16 target-topology receipt;
- no exact new dual-M1 DS4-0731 receipt.

---

# Important retained evidence

## Consumer-Blackwell NVFP4 KV physical identity

vLLM #56550: requested low-bit KV does not prove physical execution. Record physically allocated dtype, backend, HND/layout, V-scale representation/write order, main/SWA block geometry, graph-capture route and actual executed route.

## QSA bounded workspace and allocator lifetime

vLLM #56500/#56457: a per-allocation cap can coexist with allocator-retained growth through a ladder of differently sized workspaces. Prefer bounded reusable workspace/buckets; record live tensors, allocator-reserved bytes and post-warmup allocation count separately.

## DFlash semantic-axis correctness

vLLM #56431: stacked per-layer K normalization accidentally collapsed its layer axis, destroying acceptance/quality. Fused/stacked draft ops must preserve layer-to-parameter-row mapping and semantic axes.

## Qwen4Exp YaRN execution consistency

oMLX #3594: context extension beyond native 262,144 must be installed and shared consistently by main attention, QSA/indexer and MTP. Configured metadata does not prove the selected route executes it. Current ~128K objective remains inside native horizon.

## Exact expert offload / parallel read arrival

`jundot/omlx#3589`: immutable expert reads may arrive in parallel while cache ownership/LRU/state mutation remains deterministic and serial. Keep exact expert offload as emergency capacity lane, not primary dual-M1 architecture.

## Logical vs physical padded execution shape

vLLM #56181: physical graph/DP padding must be reflected consistently in attention metadata, slot/cache mapping and draft population. Requested logical tokens are not necessarily executed physical tokens.

## Dynamic request shape vs structural JIT specialization

vLLM #56153: layout/head/packing/tile/precision may be structural compile identity; high-cardinality token/batch/table lengths normally belong at runtime. Benchmark first compile, first new shape, warmed steady state and realistic shape churn separately.

## PP + MTP ownership

vLLM #46994: drafter stage, hidden-state producer/consumer, draft transport, stage-local embeddings/projections and QSA/indexer/spec-buffer pointer freshness are explicit. Rejection can hide corrupt drafts, so final-output correctness alone is insufficient.

## Dual-node Flash load transient

oMLX #3578 reduced sharding-phase peak allocation by about 4.2 GiB on a two-node Flash TP2 load by releasing superseded parameter trees. Load/transform/sharding/first-eval peaks remain distinct from steady-state residency.

---

# Current consequences by active lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Required evidence includes:

1. load/transform/sharding/first-eval and steady-state memory separately;
2. live versus allocator-reserved workspace memory;
3. bounded QSA workspace reuse with no monotonic context-shape allocation ladder;
4. disjoint top-k scratch and physical workspace/ubatch ownership;
5. physical draft-head stage, hidden-state producer/consumer and explicit draft transport;
6. stage-local embedding/projection ownership;
7. QSA/indexer/spec-buffer source and pointer freshness;
8. logical versus physically padded execution rows/tokens;
9. per-layer draft normalization mapping and dtype;
10. **proposal/draft head precision separately from target-verifier precision**;
11. **private derived speculative-weight memory and resulting KV-capacity tradeoff**;
12. **maximum physical spec-verifier row shape and temporary-buffer lifetime during admission**;
13. final-output parity, speculative acceptance parity and task-quality checks separately;
14. PP1-vs-PP2 acceptance under matched cells;
15. request-namespace and checkpoint-file lifetime separation;
16. expert occupancy/tail-tile and logical/physical padded geometry;
17. PLE as its own sparse placement plane;
18. code/prose/CJK/tool/low-acceptance long-context cells;
19. positional-transform provenance only if testing beyond native 262,144;
20. profitable singleton MTP + plain concurrent work remains the safe serving default until physical B2/B3/B4 recurrent/spec-state and workspace isolation are certified.

## Blazer / ~5.x BPW

Execution identity includes per-tensor stored precision, activation precision by phase, KV/state class precision, target-verifier precision, drafter/proposal precision, private derived speculative weights, routed/shared expert logical and physical padded geometry, padded-lane scale semantics, QSA/indexer precision, recurrent/control precision, packing/group/tile/lane geometry, occupancy/tails, load transients, workspace lifetime and spec-verifier peak shape. Benchmark reserved/live bytes, allocation count, TG/PP/task wall-clock and acceptance together.

## Qwen3.8-27B M1 / P69

No target movement. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

The FP16 DFlash2 checkpoint is an **external experiment candidate only**. Test plain vs stock BF16 DFlash2 vs FP16 DFlash2 under matched 4K/16K/32K cells before adopting it; extend longer only if profitable.

## RTX5070Ti16

No target movement. Fully resident canonical speed lane remains distinct from host-backed capacity experiments. Continue physical KV-format provenance from #56550. #56577 is speculative-precision transfer, not a 5070 Ti receipt.

## DS4-0731 dual M1

No target movement. #56568 reinforces logical-vs-physical routed/shared-expert geometry and fused-route provenance only. Later V4.1 CUDA/B200 rates are not DS4 evidence.

---

# Standing rules

- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Benchmark cell = actual executed route, not requested flags.
- Route provenance ladder: requested -> configured -> compiled -> armed/admitted -> executed.
- Context is part of target identity.
- Requested/configured precision is not physical/executed precision.
- Memory provenance includes load/materialization transients, live tensors, allocator-retained workspace, private derived speculative weights and verifier temporaries.
- Physical execution identity includes layout, packing, padding, scale semantics, tile/tail occupancy and actual fused/fallback route.
- B2/B3/B4 require physically simultaneous independent requests with correct persistent state; configured/admitted/queued slots do not count.
- Final-output correctness is not sufficient speculative correctness; record acceptance rate/length and task quality independently.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **Do not actively track future M5/M5 Ultra purchase performance unless the user explicitly reopens that scope.**
