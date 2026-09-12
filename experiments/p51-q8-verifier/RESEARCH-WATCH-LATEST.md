# Latest external runtime watch

## Active scope

Research remains centered on the hardware and execution lanes we actually own or are actively building:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**;
- **Qwen3.8-27B — one M1 Max 64 GB**;
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**;
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**;
- **Blazer / custom ~5.x-BPW execution work** when evidence is portable to those machines.

**Do not maintain a dedicated future M5 / M5 Ultra purchase lane.** Stronger-hardware evidence is retained only when it teaches something portable about active M1/5070Ti lanes: kernels, memory ownership, cache/state precision, speculative execution, load transients, workspace lifetime, physical geometry, positional/state correctness or cluster/runtime design.

---

## Read order for every new research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md` — authoritative for TG/PP target identity; context is part of target identity.
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1103.md` — newest complete delta: V4.1 CED bounded-replay Apple prefill, fresh ds4 V4.1 Metal support, device-authoritative speculative metadata, fresh screening.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0313.md` — M1-targeted Qwen3.8-27B DFlash2 FP16 candidate, Flash-Next proposal-head precision A/B, speculative-verifier peak profiling, shared-expert physical padding/fusion.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0111.md` — Blackwell NVFP4-KV physical execution identity and screened rebase/rediscovery noise.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-2022.md` — QSA bounded-workspace/allocator-lifetime evidence, DFlash per-layer normalization correctness, Qwen4Exp YaRN consistency.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md` — exact expert-offload read overlap, logical-vs-physical padded-token metadata, JIT specialization discipline.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md` — PP+MTP stage ownership, stage-local draft dependencies, pointer freshness and acceptance parity.
9. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md` — dual-node Flash load transient, Tahoe/TB control transport, exact expert-offload capacity, Metal expert-tail geometry, grouped state writes and rollback correctness.
10. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` — BACKFILL / mechanism candidate only.
11. `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` — portable mixed-precision/PLE/context-shape mechanisms only; stronger-hardware rates are transfer evidence.
12. Retain the 2026-09-10 and 2026-09-09 deltas/mining notes for TP2/PP ownership, recurrent rollback, QSA/MTP, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch/mining chain remains part of canonical working context.

---

# Freshness discipline

The latest complete search covers substantive sources strictly after `2026-09-12 07:13:21 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-12 15:03:42 UTC`.**

Evidence timestamp = substantive source timestamp, not rediscovery, crawler, rebase or merge-only noise. A PR created before a boundary may be retained as a post-boundary integration signal only when labeled accurately; its older measurements do not become fresh.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | planning objective | **400 tok/s** | ~55-60% |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | ~55-60% | **110 tok/s native/exact-runtime** | ~60% |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | ~60-65% | **250 tok/s** | ~55-60% |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | ~60-65% | **180 tok/s** | ~60% |

Flash interpretation remains explicit: **40 TG sustained at ~128K active context** is the headline objective; a short-context 40 that collapses near 128K does not satisfy it. **400 PP** is cold-prefill. Neither is an exact measured dual-M1 receipt yet.

No canonical target moved in the 11:03 ET pass.

---

# Newest directly relevant evidence — 2026-09-12 11:03 ET

## oMLX #3607 — CED prefill with bounded SWA replay

**FRESH NEW / APPLE PREFILL-ARCHITECTURE TRANSFER. Not exact DS4-0731 and not an active dual-M1 receipt.**

PR #3607 was created and merged inside the window. For DeepSeek V4.1 prefill, decoder-half layers 21–39 forward attention + MoE only over the trailing sliding-window tokens, while full-context global decoder KV is obtained by projecting the encoder-final hidden state through the midpoint CSA2 layer. Chunked prefill invalidates/rebuilds the stale decoder window; decode and DSpark verify blocks remain outside the CED path. Follow-up commits preserve state through reload/cache planning and expose the per-model toggle.

Reported Apple A/B:

- M3 Ultra 512 GB;
- `DeepSeek-V4.1-Flash-oQ4e-mtp`;
- ~21.4K cold prefill;
- **50.19 s / ~430 tok/s -> 30.55 s / ~700 tok/s**, roughly **+63% prefill throughput**;
- stated DSpark acceptance stayed in the same ~71–73% range because decode/speculation itself was not changed.

Promote the mechanism, not the percentage. Split-phase optimization identity now includes:

1. encoder/decoder phase ownership;
2. full-context state/KV source;
3. bounded trailing-forward scope;
4. replay/reconstruction window;
5. chunk-boundary stale-state invalidation;
6. replay source/state boundary;
7. chunked-vs-single parity;
8. decode/speculative inclusion or exclusion;
9. reload/cache-planner persistence;
10. actual executed route.

For Flash-Next this creates a concrete research question: can any expensive later phase derive authoritative global state from a full-context boundary while forwarding only a bounded local tail? Treat as a hypothesis until demonstrated on Qwen3.8-Flash-Next.

## antirez/ds4 `bd66c402` — DeepSeek V4.1 Flash support for Metal

**FRESH NEW / APPLE MODEL-LINEAGE IMPLEMENTATION TRANSFER. Not DS4-0731 target evidence.**

Commit `bd66c402070042bf0a79ad6ece8242de4c93680c` landed at `2026-09-12 09:47:54 UTC` and adds substantial V4.1-specific Metal support: graph/preload tests, Engram support, Metal execution and prefill tests, CLI/GGUF plumbing, TP and command-memory/cancellation coverage.

At this commit the docs state:

- V4.1 text/vision use their own graph/GGUF/tokenizer and are not interchangeable with Flash-0731 weights or DSpark files;
- Q2 has ~152 GiB main weights plus 189 GiB Engram tables kept on disk and read on demand;
- one 128 GB Mac uses SSD streaming;
- two 128 GB Macs can run resident TP/RDMA at ~81 GiB main weights/rank;
- full residency has been tested on an M3 Ultra 512 GB;
- V4.1 DSpark is not implemented in this ds4 path.

Retain as source-level transfer for Engram-on-disk ownership, resident-vs-streamed expert capacity, TP/RDMA ownership, V4.1 graph separation, command-memory lifetime and prefill batching. It does **not** move our 0731 two-M1-64 target.

## vLLM #56562 — device-authoritative speculative/indexer metadata

**POST-BOUNDARY MERGE / MECHANISM TRANSFER. The PR predates the prior boundary; its benchmark numbers are not reclassified as fresh measurements.**

Merged at `2026-09-12 14:20:04 UTC`. It replaces per-step PyTorch metadata chains with Triton writes into existing buffers for DSV4.1 token/request and indexer metadata.

The durable lesson is correctness/provenance: under DSpark adaptive verification, CPU-side request boundaries can be stale, so metadata must derive from the authoritative **device** query boundaries. Graph replay was explicitly tested with changed device boundaries and stale CPU boundaries.

Promote metadata provenance:

`logical request state -> authoritative device/stage boundary -> derived token/request/indexer metadata -> graph-captured metadata route -> executed draft/verifier route`.

This extends our logical-vs-physical shape and pointer-freshness rules and should be checked explicitly when Flash PP2/MTP metadata crosses stages.

---

# Fresh-screen results / non-promotions

- **vLLM:** no newly created post-boundary Qwen3.8-Flash-Next or Qwen3.8-27B exact receipt on active M1/5070Ti topologies. #56562 is retained as current-runtime metadata provenance, not a newly fresh benchmark. Prior #56577/#56572/#56568/#56550 and earlier QSA/DFlash items remain prior-pass evidence.
- **oMLX:** #3607 is the substantive new Apple inference change. No new exact M1 Max64 Qwen3.8-27B or dual-M1 Flash-Next performance receipt was found.
- **antirez/ds4:** fresh V4.1 Metal support landed, but no fresh 0731 dual-M1-64 performance receipt.
- **llama.cpp:** post-boundary commits were screened through cutoff; no new Metal/Qwen3.8/DS4 active-lane throughput or correctness receipt was found.
- **Community/HF/Reddit:** searches resurfaced older M1/M2 DFlash2 and Flash-Next evidence but no source-time post-boundary exact active-lane result strong enough to promote. Crawl time does not reset evidence time.

---

# Important retained evidence

## DFlash2 / speculative precision

- `deepsweet/Qwen3.8-27B-DFlash2-FP16` remains an M1/M2-targeted **experiment candidate**, not a target receipt. Compare plain vs stock BF16 DFlash2 vs FP16 DFlash2 under matched cells.
- vLLM #56577 separates target-verifier precision from proposal-head precision: on stronger hardware, a private FP8 proposal head materially improved Flash-Next speculative throughput while the target head remained BF16. Promote the precision-plane separation and memory/acceptance accounting, not its percentage to Metal.
- vLLM #56431 proves stacked draft operations must preserve per-layer semantic axes; acceptance and task quality can collapse while code still runs.

## Memory and physical execution identity

- vLLM #56572: admission profiling must cover maximum reachable speculative-verifier rows/temporaries, not only smaller startup shapes.
- vLLM #56500/#56457: bounded per-allocation size does not prevent allocator-retained workspace growth; record live bytes, reserved bytes and post-warmup allocation count.
- vLLM #56550: requested KV dtype is not physical execution identity; record allocated dtype, backend, layout, scale encoding/write order, block geometry, graph capture and executed route.
- vLLM #56568: shared/routed expert logical shape may differ from physical padded kernel shape; record padding, scale semantics, fused/fallback route and memory cost.
- oMLX #3578: load/transform/sharding/first-eval transients remain distinct from steady-state residency.

## Flash/MTP ownership and long context

- vLLM #46994: explicit drafter stage, hidden-state producer/consumer, draft transport, stage-local embed/proj and QSA/indexer/spec-buffer freshness.
- vLLM #56181: logical request rows/tokens and physically padded execution shape must remain consistent in attention/cache/draft metadata.
- vLLM #56153: structural JIT specialization and dynamic runtime shape are different execution identities; benchmark first compile/new shape/warm/churn separately.
- oMLX #3594: beyond native 262,144, positional scaling must be consistently installed across main attention, QSA/indexer and MTP. Current ~128K objective stays inside native horizon.
- `jundot/omlx#3589`: immutable exact-expert reads may arrive in parallel while cache ownership/LRU/state mutation stays deterministic; keep exact expert offload as emergency capacity lane rather than primary dual-M1 design.

---

# Current consequences by active lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Certification now includes:

1. load/transform/sharding/first-eval and steady-state memory separately;
2. live vs allocator-reserved workspace memory;
3. bounded QSA workspace reuse with no monotonic context-shape allocation ladder;
4. disjoint top-k scratch and workspace/ubatch ownership;
5. physical draft stage, hidden-state producer/consumer and explicit draft transport;
6. stage-local embedding/projection ownership;
7. QSA/indexer/spec-buffer source and pointer freshness;
8. logical vs physically padded execution rows/tokens;
9. per-layer draft normalization mapping/dtype;
10. proposal/draft-head precision separately from target-verifier precision;
11. private speculative-weight memory and KV-capacity tradeoff;
12. maximum physical spec-verifier row shape and temporary lifetime during admission;
13. **authoritative device/stage boundaries for speculative/indexer metadata**;
14. **split-phase full-context state source vs bounded local forward/replay scope where applicable**;
15. **chunked-vs-single parity for any bounded-replay optimization**;
16. final-output, acceptance and task-quality checks separately;
17. PP1-vs-PP2 acceptance under matched cells;
18. request namespace/checkpoint lifetime separation;
19. expert occupancy/tail and logical/physical padded geometry;
20. PLE as its own sparse placement plane;
21. code/prose/CJK/tool/low-acceptance long-context cells;
22. positional-transform provenance only beyond native 262,144;
23. singleton MTP + concurrent plain serving stays default until B2/B3/B4 recurrent/spec-state/workspace isolation is certified.

P69-derived verifier/kernel methods remain promising transfer candidates for Flash-Next, but **P69 itself is unchanged by this external-search pass**.

## Blazer / ~5.x BPW

Execution identity includes stored precision, activation precision by phase, KV/state precision, target-verifier vs drafter/proposal precision, private derived speculative weights, routed/shared expert logical and physical shape, padding/scale semantics, QSA/indexer precision, recurrent/control precision, packing/group/tile/lane geometry, occupancy/tails, load transients, workspace lifetime, spec-verifier peak shape, and authoritative state/metadata boundaries.

## Qwen3.8-27B M1 / P69

No target movement. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

DFlash2 remains a challenger to the tuned Lightning-MTP/P69 incumbent. Existing FP16 and W4/A32 draft experiments remain useful, but no fresh post-boundary receipt changes their expected ranking.

## RTX5070Ti16

No target movement. Fully resident canonical speed lane remains distinct from host-backed capacity experiments. Keep physical KV-format provenance and separate target/draft/proposal/verifier precision planes.

## DS4-0731 dual M1

No target movement. Fresh V4.1 evidence supplies two mechanism/source-code veins only:

- oMLX CED bounded-replay prefill;
- ds4 V4.1 Metal/Engram/streaming/TP implementation.

Neither reproduces 0731 on two 64 GB M1 Max machines.

---

# Standing rules

- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Benchmark cell = actual executed route, not requested flags.
- Route provenance: requested -> configured -> compiled -> armed/admitted -> executed.
- Context is part of target identity.
- Evidence timestamp is substantive source time, not crawl/search/rebase time.
- Requested/configured precision is not physical/executed precision.
- Memory provenance includes load/materialization transients, live tensors, allocator-retained workspace, private derived speculative weights and verifier temporaries.
- Physical execution identity includes layout, packing, padding, scale semantics, tile/tail occupancy and actual fused/fallback route.
- For split-phase/replay optimizations, record authoritative full-context state source, bounded local-forward scope, replay boundary and chunked-vs-single parity.
- For speculative metadata, record which device/stage boundary is authoritative and prove graph replay consumes fresh boundaries.
- B2/B3/B4 require physically simultaneous independent requests with correct persistent state; configured/admitted/queued slots do not count.
- Final-output correctness is not sufficient speculative correctness; acceptance rate/length and task quality remain independent checks.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **Do not actively track future M5/M5 Ultra purchase performance unless the user explicitly reopens that scope.**