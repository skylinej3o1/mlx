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
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-2022.md` — newest complete delta: QSA bounded-workspace/allocator-lifetime evidence, DFlash per-layer normalization correctness, Qwen4Exp YaRN execution consistency, fresh source screening.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md` — exact expert-offload read overlap, logical-vs-physical padded-token metadata, JIT specialization discipline, screened V4.1 Apple fast path.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md` — PP+MTP stage ownership, stage-local draft dependencies, pointer freshness and acceptance parity.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md` — dual-node Flash load transient, Tahoe/TB control transport, exact expert-offload capacity, Metal expert-tail geometry, grouped state writes and rollback correctness.
7. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` — BACKFILL / mechanism candidate only.
8. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` — portable mixed-precision/PLE/context-shape mechanisms only; stronger-hardware rates are transfer evidence.
9. Retain the 2026-09-10 and 2026-09-09 deltas for the previously recorded TP2/PP ownership, recurrent rollback, QSA/MTP, cache/state, transport, ABI, precision and soak methodology.
10. Retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` and `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` as mechanism research, not fresh target evidence.

Because `RESEARCH-STATE.md` predates the later dated deltas, this watch/mining chain remains part of canonical working context.

---

# Freshness discipline

The latest complete external-search pass covers sources strictly after `2026-09-11 22:31:55 UTC` through:

**Hard source-freshness boundary for the next complete external search: `2026-09-12 00:22:42 UTC`.**

Source-specific mining and repository-only commits do not independently advance the global boundary. Evidence timestamp = substantive source timestamp, not rediscovery time.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | planning objective | **400 tok/s** | ~55-60% |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | ~55-60% | **110 tok/s native/exact-runtime** | ~60% |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | ~60-65% | **250 tok/s** | ~55-60% |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | ~60-65% | **180 tok/s** | ~60% |

Flash interpretation remains explicit: **40 TG sustained at ~128K active context** is the headline objective; a short-context 40 that collapses near 128K does not satisfy it. **400 PP** is cold-prefill. Neither is an exact measured dual-M1 receipt yet.

No canonical target moved in the 20:22 ET pass.

---

# Newest directly relevant evidence — 2026-09-11 20:22 ET

## QSA bounded workspace and allocator lifetime — vLLM #56500 / #56457

**TRANSFER / MECHANISM, directly relevant to Flash long-context memory stability.**

The Qwen4Exp QSA path could allocate a slightly larger logits tensor on every chunk as `max_seq_len` grew. A per-allocation byte cap did not cap allocator-retained memory because each old size remained cached.

The physical report on 2x unified-memory GB10 running Qwen3.8-Flash-Next is unusually diagnostic: a 254K cold prefill died at exactly 166,400 tokens, where the monotonic allocation sequence predicts about **14 GB/rank** of retained QSA buffers. A 64 MiB workaround caused allocation size to saturate and kept memory flat. The proposed reusable-workspace fix instead reserves bounded storage once and serves each chunk through compact views.

Allocation probe from #56500:

| measurement | base | bounded workspace |
|---|---:|---:|
| reserved memory, first -> last | 34 -> 1,370 MiB | 536 -> 536 MiB |
| new allocations after first step | 15 | 0 |
| peak live tensor memory | 171.90 MiB | 528.65 MiB |

Kernel timings were essentially unchanged. The portable lesson is storage lifetime, not GPU speed.

**Promote:** Flash/QSA admission telemetry distinguishes logical workspace budget, live tensor bytes and allocator-reserved/retained bytes. After warm-up, a long-context path should not create a monotonic ladder of new workspace sizes. Prefer one bounded reusable workspace or a small deliberate bucket set; keep top-k scratch disjoint and prove per-ubatch/workspace-lane ownership.

This does not move the 400 PP target.

## DFlash per-layer K normalization — vLLM #56431

**SPECULATIVE-CORRECTNESS TRANSFER.**

DFlash stacks K-normalization weights as `[num_layers, head_dim]`. An XPU path treated the weight as one vector and reused layer 0's normalization for every draft layer. The reported validation moved from GSM8K **0.487 / acceptance 0.011 / acceptance length 1.080** to **0.859 / 0.459 / 4.215** after preserving the layer axis.

**Promote:** any stacked/fused draft operation must retain semantic axes, not merely tensor byte size. Speculative execution identity records layer-to-parameter-row mapping, normalization source/dtype/shape and target-vs-draft ownership. Qualification includes acceptance length/rate and task quality, not only shape checks or final-output smoke tests.

The PR includes Qwen3.8-27B + DFlash2 testing, but its absolute accelerator rates are not target evidence.

## Qwen3.8-Flash-Next YaRN execution consistency — oMLX #3594

**FRESH / STRONGER-APPLE TRANSFER / LONG-CONTEXT CORRECTNESS.**

The pinned mlx-vlm Qwen4Exp MRoPE path ignored `text_config.rope_parameters`, so simply raising the context gate beyond the native **262,144** tokens could leave YaRN configured in metadata but not executed. The patch installs the positional transform into the shared attention rotary object used by main attention, QSA/indexer and MTP, explicitly falls back from a fused MRoPE route that cannot represent non-unit scaling, and records current SpecPrefill incompatibility rather than silently rebuilding plain frequencies.

A stronger-Apple field test reached 350K tokens with coherent generation and active MTP. Treat that only as mechanism validation.

**Promote for future >262K work:** positional extension provenance is `configured -> installed -> shared by attention/QSA/MTP -> fused/eager route capable -> executed`. Reject mixed positional regimes. Our ~128K objective remains inside the native horizon, so no target moves.

---

# Important retained evidence

## Exact expert offload / parallel read arrival

`jundot/omlx#3589`: immutable expert reads may arrive in parallel while cache ownership/LRU/state mutation remains deterministic and serial. Strong low-residency TTFT/TG improvement; high-residency warm regression proves the machinery is not universally beneficial. Keep this as the emergency capacity lane, not the primary dual-M1 architecture.

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

Keep **PP2/layer ownership primary**, TP2 as control. Required evidence now includes:

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
16. positional-transform provenance only if testing beyond the native 262,144-token horizon;
17. profitable singleton MTP + plain concurrent work remains the safe serving default until physical B2/B3/B4 recurrent/spec-state and workspace isolation are certified.

## Blazer / ~5.x BPW

Execution identity includes per-tensor stored precision, activation precision by phase, KV/state class precision, routed/shared experts, QSA/indexer precision, recurrent/control precision, MTP-head precision, packing/group/tile/lane geometry, routed occupancy/tails, load transients **and workspace lifetime**. Benchmark reserved bytes, live bytes and allocation count alongside TG/PP/task wall-clock.

## Qwen3.8-27B M1 / P69

No target movement. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

DFlash2 adds a correctness requirement only: fused/stacked draft normalization must preserve the per-layer axis.

## RTX5070Ti16

No target movement. Fully resident canonical speed lane remains distinct from host-backed capacity experiments.

## DS4-0731 dual M1

No target movement. Later V4.1 GPU/Apple evidence remains mechanism transfer unless it reproduces DS4 topology/runtime directly.

---

# Standing rules

- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Benchmark cell = actual executed route, not requested flags.
- Route provenance ladder: requested -> configured -> compiled -> armed/admitted -> executed.
- Memory provenance includes live tensors, allocator-retained workspace and load/materialization transients.
- B2/B3/B4 require physically simultaneous independent requests with correct persistent state; configured/admitted/queued slots do not count.
- Final-output correctness is not sufficient speculative correctness.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **Do not actively track future M5/M5 Ultra purchase performance unless the user explicitly reopens that scope.**