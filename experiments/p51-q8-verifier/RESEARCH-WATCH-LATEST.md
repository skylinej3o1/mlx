# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest genuinely fresh/update search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-1715.md`

   **The 17:15 note is authoritative for rMLX #556's mutation-checked shared-round-skeleton design, the force-pushed/narrowed oMLX #3468 SSD expert-streaming implementation and its capacity-only benchmark classification, and oMLX #3063's requested/planned/measured/effective distributed prompt-cache retuning semantics.**

4. Retain the immediately previous search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-1414.md`

   **The 14:14 note remains authoritative for workload-shaped cache-block sizing and agent TTFT/task-wall evidence, rMLX single-producer round telemetry/sink truth, packaged custom-kernel ABI provenance, per-step fast-prefill target/draft eligibility, UVA buffer-generation lifetime, hybrid attention-vs-recurrent distributed state mapping, small-M shape-aware dispatch, the official DeepSeek V4.1 Flash architecture update, and the refreshed Affine4 long-context backfill.**

5. Retain the 09:11, 06:01 and 00:16 deltas:

   - `RESEARCH-WATCH-2026-09-10-0911.md` — completed oMLX #3553 Flash bit-exact-vs-tolerance benchmark decomposition, equal-acceptance cycle-cost methodology, independently quantized MTP-head evidence, V4.1 streamed conversion/quant-block requirements;
   - `RESEARCH-WATCH-2026-09-10-0601.md` — M5-Max Flash cold-prefill/PLE-overlap, two-Mac reliable Metal synchronization, execution-shape-specific decode/MTP/QSA work, K-only sparse-indexer memory, graph-address identity, replay-boundary retention and benchmark-window provenance;
   - `RESEARCH-WATCH-2026-09-10-0016.md` — BACKFILL / SOURCE-CORRECTION for the previously under-mined r/oMLX Flash thread: realistic 120K/150K harness receipts, oQ5e memory/robustness, MTPLX speed-versus-reliability, 64-GB-class viability, PLE/N-gram residency and task-wall consequences.

6. Retain the 2026-09-09 deltas for DS4 selective projection/quant-shape behavior, full-machine-residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram work, quantized-FA compiled capability, routed-MoE tile geometry, RTX5070Ti capacity evidence, Atlas concurrency ownership, oMLX replay boundaries and vLLM concurrency/soak attribution.

7. Also retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

8. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

9. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Freshness discipline

The latest completed external search covers sources strictly after the prior boundary **2026-09-10 18:22:16 UTC** through the end of the current search.

**Hard source-freshness boundary for the next external search: 2026-09-10 21:24:31 UTC.**

This is the end-of-search boundary, not the later repository-write timestamp. Future passes must search strictly after this source boundary; repository-only commits must never create a source-search gap. Refreshed/rebased/force-pushed metadata does not make older benchmark execution fresh.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 17:15 pass moves no row.**

Important Flash interpretation from the canonical target file:

- **40 tok/s** remains the B1 short/medium working target;
- the separate ~128K ladder remains **20 / 25 / 30 / 35 tok/s**;
- **400 tok/s** remains the realistic cold-prefill working target.

No new exact dual-M1/TB4 rate receipt was found this pass.

---

# Current newest incorporated evidence — 2026-09-10 17:15 ET

## FRESH / rMLX #556 — pin the shared round skeleton's semantics before engine migration

Commit `64a5dc1e228f6e33f347c41bfa0d75a87fc9e8d5`, **19:40:19 UTC**.

This is deliberately **design/docs/tests, not implemented engine migration**. The proposed common round loop defines the drafter interface, migration order, observables and mutation table before seven speculative loop bodies are collapsed.

The important lesson is that deduplicating control flow must preserve facts that ordinary output equivalence cannot see: resident-KV report exit, empty-chain refusal point, charge-decision ownership, rollback/offset basis, emission outcome, conditioning/projection meaning, prefill timing scope and the block actually executed. Source readers are mutation-checked against moved reports/guards, charge rebinding, edge reordering and comment/phantom scanner matches.

**Promotion:** define owner/edge/exemption semantics before shared-control-flow refactors; mutation-check the gate against the defect; preserve **design → implemented → compiled → armed → executed**; report the block/telemetry the round actually ran.

## FRESH / oMLX #3468 — focused SSD expert-streaming implementation

Current head `626feab03d3885b728c2c990e3f4252ed5d48784`.

Fresh post-cutoff history:

- `dc93f89f90aa5f0415fb01eed14ee5f9d382ee95` — **20:08:20 UTC** — narrowed streaming implementation with fail-clean, per-model top-k/spill invalidation;
- `db1ee5f0725f81a4a7512102afe10fc09413ad47` — **20:08:34 UTC** — required Metal-sync helper;
- `b6b16b7a1892e50b6ca03b6dcf17d1767104ce21` — **20:08:54 UTC** — removes the broad experiment suite, retains 83 focused regressions;
- `626feab03d3885b728c2c990e3f4252ed5d48784` — **21:07:08 UTC** — audit/dead-code cleanup; 83 focused tests pass.

The useful architectural rules are:

- one structural streamability predicate shared across forcing/loading/conversion;
- lazy load and replace giant expert banks with streaming backing **before** `materialize_lazy_state`;
- requested streaming fails closed if backing/conversion cannot be established rather than proceeding into full-bank OOM;
- streaming owns its projection layout, so normal gate+up fusion is not silently stacked on top;
- request-level LRU hit/miss/eviction/capacity and fallback state become executed-route telemetry.

### UPDATE / BACKFILL benchmark body

The PR description reports M4 Pro 48-GB / 4-GiB expert budget / 2K prompt / 96 decode / single-request / MTP-off cells:

- Flash-Next: **56.6 PP / 2.42 TG**;
- DS4-0731: **20.6 PP / 2.53 TG**;
- GLM-5.3: **35.0 PP / 1.75 TG**.

This pass did **not** establish post-cutoff execution timestamps for those benchmark runs; the narrowed PR explicitly excludes benchmark/result artifacts from its current code diff. Therefore these are **capacity/offload transfer evidence, not fresh target receipts**.

**Promotion:** treat routed-expert SSD streaming as a capacity lane. For Flash-Next, PLE/n-gram SSD offload remains structurally preferable when feasible because it serves small indexed reads rather than repeatedly feeding active expert weights.

## UPDATE / oMLX #3063 — requested cache capacity survives repeated cluster retuning

Post-cutoff update **20:42:07 UTC**.

`ExecutionSettings` now preserves `requested_prompt_cache_size` separately from the currently clamped slot count. An initial tight-headroom plan can resolve to one slot, then measured placement can restore two/four slots rather than clamping again from one forever. The explicit regression covers **3 GiB planned → 1 slot; 20 GiB measured → 4 slots; headroom collapse → 1 slot**.

Count-based LRU remains the cross-rank coherence mechanism; byte-budget eviction stays disabled because unequal PP stages can cross rank-local byte thresholds at different requests and retain different prefixes.

**Promotion:** cluster capacity provenance is **requested → planned → measured-headroom-retuned → effective**. Repeated tuning resolves from durable requested intent, not the previous clamp. Cache capacity and cache-coherence policy are separate facts.

---

# Screened / no target movement

- oMLX main has no new post-cutoff main commit with stronger target-lane evidence; current fresh oMLX evidence is in PR updates above.
- oMLX #3536 has post-cutoff review/metadata activity, but its substantive tensorized MTP acceptance work/benchmarks do not establish a new post-cutoff execution cell; preserve as UPDATE/KNOWN.
- rMLX #555 is pre-cutoff for this pass and already incorporated by the 14:14 watch; #556 is the new item.
- focused vLLM MTP/KV results nearest the boundary predate 18:22:16 UTC; later changes supplied no stronger exact Apple/hybrid target evidence.
- llama.cpp's Qwen Vulkan small-M item belongs to the prior watch; later generic backend activity supplied no exact Qwen target receipt.
- antirez/ds4 supplied no new post-cutoff exact 2x-M1-Max64/TB4 DS4-0731 rate receipt.
- exact-rig searches supplied no new timestamped post-cutoff 2x-M1 Flash receipt, one-M1 canonical 27B receipt or RTX5070Ti16 fully-resident canonical speed receipt. Older/undated/crawled-today records are not fresh evidence.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. mutation-checked drafter-specific exit/charge/conditioning/block semantics before speculative-loop collapse;
2. one authoritative streamability/placement predicate;
3. offload conversion before giant-bank materialization and fail-closed backing creation;
4. PLE/n-gram SSD offload primary, routed-expert streaming a separate capacity control;
5. resident/streamed route + cache hit/miss/eviction/fallback state in executed provenance;
6. projection-layout ownership so streaming/fusion/custom-quant transforms cannot silently conflict;
7. preserve `requested → planned → measured → effective` cache-slot state across repeated cluster tuning;
8. rank-synchronized prompt-cache eviction remains count-based, not rank-local byte-threshold based;
9. retain all prior reliable-sync, selected-row PLE overlap, cache-page-size, graph-layout, recurrent ownership, concurrency, soak and equal-acceptance speculative gates.

Safe serving remains **profitable singleton MTP + plain concurrent work** until concurrency/state-isolation gates are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. The new material is design/offload/cluster-serving transfer evidence, not a new M1 numeric receipt.

**P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; offload/host-backed variants stay separate capacity cells.

## Dual-M1 DS4-0731

No target movement. #3468 makes SSD expert-streaming capacity more concrete, but its M4-Pro benchmark body is not a dual-M1 receipt.

## Future Blazer / 5.x-bit

Add component-level residency/offload ownership to execution provenance. Custom quant/fusion/streaming paths must declare which tensor layout they own and which transforms are mutually exclusive. Preserve actual executed block/route/cache-state identity alongside quant/group/kernel identity.

---

# Standing decisions strengthened

- Shared speculative control flow needs a mutation-checked semantic interface before deduplication.
- Design/proposal evidence is not executed-engine evidence.
- The reported round/block/telemetry must come from what actually executed.
- Offload support should have one authoritative capability/placement predicate.
- Giant expert banks must be converted to streaming form before eager materialization.
- Requested offload fails closed if its backing cannot be established.
- Routed-expert SSD streaming is a capacity lane unless exact target evidence proves favorable economics.
- PLE/n-gram offload remains structurally preferable for Flash-Next when feasible.
- Cache tuning provenance is **requested → planned → measured → effective**.
- Repeated retuning clamps from requested intent, not a previous clamp.
- Distributed prompt-cache coherence cannot depend on unequal rank-local byte thresholds.
- Refreshed/rebased/force-pushed metadata does not make older benchmark execution fresh.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
