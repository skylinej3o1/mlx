# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical target file:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP target identity. Context is part of target identity.**

3. Read the newest complete external-search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-0639.md`

   This is authoritative for the latest post-cutoff pass: oMLX M5 INT8-activation prefill, recurrent-checkpoint namespace lifetime, llama.cpp Metal fusion execution/census and narrow-IQ lane utilization, vLLM shared-KV / PCP-spec / DeepSeek-V4.1 runtime contracts, exact-target screening, and the newly surfaced Apple V4.1 future-hardware lane.

4. Read the newest source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md`

   This mines Moonshot AI's **MoBA: Mixture of Block Attention for Long-Context LLMs** for a portable QSA execution idea: keep Qwen's learned selected-block set fixed, invert the sparse query->block relation into block->query work groups, run blockwise attention, and combine per-query partial results with online softmax. It is **BACKFILL / MECHANISM / FUTURE KERNEL CANDIDATE**, not a model-replacement proposal and not an exact target receipt.

5. Retain the preceding source-specific mining note:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md`

   This mines the mlx-serve Qwen3.8-Flash-Next 1M-context release and mixed 4/8-bit pack. It is **TRANSFER / MECHANISM / USER-DEVELOPER RECEIPT**, not an exact dual-M1 receipt and not a complete external-search pass.

6. Retain the immediately previous complete delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-0026.md`

   It remains authoritative for oMLX #3553 M3-Ultra machine-exclusive A/B and content-shape evidence, M5 long-context equal-acceptance decomposition, rMLX #558, heterogeneous-PP completion ownership, ragged sparse MTP routing, deferred-free capacity semantics and cluster recovery.

7. Retain the 2026-09-10 dated deltas for TP2 control topology, shared-round-skeleton gates, workload-shaped caching, sink-truth telemetry, custom-kernel ABI, bit-exact-vs-tolerance methodology, QSA/MTP shapes, reliable Metal synchronization, the under-mined r/oMLX Flash thread, oQ5e robustness, MTPLX speed-vs-reliability and PLE residency.

8. Retain the 2026-09-09 deltas for DS4 selective projection/quant-shape behavior, full-machine-residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram work, compiled quantized-FA capability, routed-MoE tile geometry, RTX5070Ti capacity evidence, Atlas ownership, replay boundaries and concurrency/soak attribution.

9. Retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / future serving research**, not fresh target evidence.

10. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, newer dated deltas remain part of the evidence chain.

---

# Freshness discipline

The latest **complete external search pass** covers sources strictly after the previous boundary `2026-09-11 04:26:56 UTC` through:

**Hard source-freshness boundary for the next complete external search: 2026-09-11 10:39:19 UTC.**

The MoBA note and mlx-serve 1M note are source-specific mining/backfill and deliberately do **not** advance this boundary. Repository-only commits and source-specific mining must never create a source-search gap.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Flash interpretation remains explicit:

- **40 tok/s sustained at ~128K active context** is the headline dual-M1 Flash objective;
- short/medium TG ladders are bring-up calibration only;
- the old September 4 ~128K 20/25/30/35 ladder is historical evidence calibration, not the target;
- reaching 40 only at short context while collapsing near 128K does **not** meet the goal;
- **400 tok/s** remains the realistic cold-prefill objective;
- 40 @ ~128K is a planning target / hypothesis, not an exact measured dual-M1/TB4 receipt.

**The 06:39 complete pass and subsequent source-specific mining moved no target.**

---

# Newest fresh evidence — 2026-09-11 06:39 ET pass

## FRESH — oMLX #3548: M5 INT8-activation prefill over existing Q4/Q5 packed weights

Commit `83a641d2820c79383fb53ffb717eb7cf0a89e967`, **04:57:55 UTC**.

On MacBook Pro M5 Pro 48 GB, Qwen3.8-27B-oQ4e-mtp at pp4096:

- **391.8 -> 518.5 tok/s prefill**;
- Q4 GEMM **42 TOP/s** against a measured **44.21 TOP/s** ceiling.

The kernel keeps the checkpoint's packed affine Q4/Q5 weights canonical, decodes them directly into fragments, and changes the **activation** execution representation to INT8 for eligible prompt-processing matmuls. It is opt-in because activation quantization changes numerics; broad task-quality validation is not yet reported.

**Promotion:** activation precision is a first-class phase/execution property independent of stored-weight BPW. This is an M5/future-Blazer mechanism, not an M1 numeric multiplier.

## FRESH — oMLX #3563: recurrent checkpoint namespace lifetime

Commit `779ef216f11c4f1ff6c226dd48be452ca4d8499b`, **05:02:35 UTC**.

Promoting a staged boundary could remove the request directory while the next writer had already entered its mkdir -> write interval, producing ENOENT and a missing GDN checkpoint. Cleanup now owns final namespace removal.

**Promotion:** persistent state lifetime is:

**request namespace -> staging generation -> physical object -> published boundary**.

A moved/published file does not prove the namespace is quiescent.

## FRESH — llama.cpp #28164: Metal fusion provenance and direct GDN state writes

Commit `a2878d30df0130dde503a7d9ba30d3d21bd71b9f`, **09:41:54 UTC**.

A relative-vs-absolute output-index bug silently disabled a norm/MUL fusion and caused about a **5% TG regression**. The new single-source fusion table drives optimizer and encoder, exposes per-pattern execution counts, and CI pins the actual fusion census. It also adds a GDN + cache-copy fusion that writes recurrent snapshots directly into the destination cache and elides the trailing copy.

**Promotion:** benchmark identity gains:

**declared fusion -> packed adjacency -> eligibility -> encoder match -> executed fusion count**.

Record the actual fusion census; enabled source code is not proof that a fusion executed.

## FRESH — llama.cpp #28692: narrow IQ Metal widths strand SIMD lanes

Commit `aac810230f9ef0cf73a47c56e46e87d0988be348`, **09:30:20 UTC**.

IQ1/IQ2/IQ3 `mul_mv` kernels with `ne00 < 1024` could leave large parts of a SIMD group idle because each lane owned one 32-element chunk. The new split path distributes rows across otherwise-idle lanes. K-quants need separate treatment because their lane mapping differs.

**Promotion:** Blazer must optimize precision **and** exact lane/tile geometry. Explicitly qualify B1 GEMV/QMV, MTP small-M, routed-expert and sparse selected-row widths; nominal BPW does not determine runtime ordering.

## FRESH — vLLM #55864: shared KV is semantically absent, not a dummy tensor

Commit `fbf51c70269bb0d8333e14c5788e628e33c72f5d`, **06:07:52 UTC**.

A KV-sharing MTP layer now calls attention with `K=None, V=None` rather than allocating fake K/V buffers. Unsupported DCP-prefill sharing fails closed.

**Promotion:** encode owner / reader / absent state explicitly; never fabricate dummy storage merely to satisfy a generic interface.

## FRESH — vLLM #56107: PCP + speculative decode preserves global/device state identity

Commit `980c16c8e4c66dce0bc4d355e4ec7fa2ae7b5141`, **05:07:53 UTC**.

Single-module MTP and replicated DSpark now work with prefill context partitioning. The implementation copies already-materialized GPU positions instead of rebuilding them from potentially lagging CPU request state, restores local hidden state to global layout before sampling, and preserves the pre-partition hidden representation needed by the speculator.

**Promotion:** distinguish **global request state -> partition-local execution state -> restored global sampling/spec state**; device truth remains authoritative through rollback/rejection.

## FRESH / FUTURE ARCHITECTURE — vLLM #56214: DeepSeek-V4.1 runtime contracts

Commit `e77daef89e18e08321ae7b8b24827eedd5fe8673`, **09:11:19 UTC**.

V4.1 support makes several architecture concepts concrete in runtime code:

- compressor state has a dedicated circular/ring cache beside paged MLA/SWA groups;
- token-to-ring mappings are explicit;
- fused query RMSNorm + MXFP8 quantization is tested bitwise against the separate quantizer including graph replay;
- pre-quantized query representations may be shared by attention/indexer projections only when the consumer kernel/quantization contract matches.

**Promotion:** future architectures should model paged global state, cross-layer compressor/index state, bounded ring/replay state, recurrent state and speculative sidecars as distinct ownership classes.

This is not DS4-0731 target evidence.

---

# BACKFILL / future Apple lane — DeepSeek-V4.1 MLX

Newly surfaced Apple work is retained as **BACKFILL / TRANSFER**, not fresh exact-target evidence.

`PipeNetwork/deepseek-v41-mlx` describes a 754.6B V4.1 runtime with four cross-layer compressor/index owners (layers 2/8/14/20) serving all 40 layers and 196.6B Engram parameters. Published Apple-oriented mixed builds include:

- **427 GB** mixed 4/8-bit + Engram 4-bit for the 512-GB tier;
- **477 GB** mixed 4/8-bit + Engram 6-bit for 1-TB machines.

Its reported divergence ladder strongly favors mixed precision over uniform 4-bit: the uniform-4 build saves only about 3 GB versus the 427-GB mixed build while showing substantially worse free-running drift.

Operationally, the 477-GB build reportedly does **not** fit a 512-GiB machine despite nominal checkpoint size, because lazy first materialization can transiently approach ~2x build size and dirty MLX buffers interact poorly with macOS compression. The 427-GB build is the intended 512-GB tier.

**Promotion:** nominal file size below unified memory is not an admission proof. Price resident weights + first-eval transient + allocator/wired/compressed behavior + cache/context + scratch + sidecars.

A separate experimental ~239-GB 2-bit V4.1 MLX build reports up to ~9.5 tok/s on M3 Ultra 256 GB, but lacks broad reasoning/coding validation; keep it only as low-bit feasibility evidence.

---

# Source-specific MoBA mining — newest

`RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` is authoritative for the MoBA-derived execution candidate.

Paper facts retained there:

- MoBA routes queries to selected historical KV blocks and groups queries by assigned block for variable-length block attention;
- blockwise partial results are combined with **online softmax**;
- its 1M Llama experiment uses block size 4096 / top-k 12, leaves the final 3 layers full attention, and activates MoBA after long-context continued training;
- RULER@128K is **0.7818 MoBA vs 0.7849 full attention**;
- the paper uses MoBA for **prefill only** and full attention for generation in downstream evaluation;
- the reported **6.5x at 1M** and **16x at 10M** are attention-computation results, not whole-model PP multipliers.

### Portable project consequence

Do **not** graft MoBA's trained selector onto Qwen.

Instead retain one future execution-only candidate:

> **QSA wide-prefill inverted-block backend:** freeze Qwen's existing selected-block IDs, transpose query->block edges into block->query groups, evaluate each historical block for all assigned query rows, and merge partial outputs with online softmax.

Before writing the kernel, instrument real QSA selection overlap and record:

- total query-block edges;
- unique selected blocks;
- reuse factor = edges / unique blocks;
- block popularity / adjacent-row overlap;
- context and query-width dependence;
- code/prose/CJK/tool workload dependence.

Only prototype if reuse is sufficient to amortize bucketing and merge overhead. Whole-model **cold PP @ ~128K** is the promotion metric; attention-only speedup is insufficient.

This complements the existing shape split:

- narrow B1/MTP rows -> indexed selected-K/V direct consume;
- wide prefill -> candidate block-inverted backend;
- existing gathered/copy paths remain measured controls.

PP2 ownership is unchanged: inversion stays stage-local and must not create dense/repeated TB4 KV traffic.

---

# Source-specific mlx-serve 1M Flash note — retained

`RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` remains authoritative for the M5 Max128 Qwen3.8-Flash-Next 1M-context transfer receipt and its asymmetric mixed-precision pack.

Key standing consequences remain:

- Blazer search explicitly includes **Q4-ish routed experts + high-precision control/state/shared/QSA/MTP** as a first-class candidate family;
- n-gram/PLE is a separately managed sparse lookup plane with resident / SSD / hot-cold / stage-local policies;
- context **and content shape** are part of benchmark identity;
- warm prefix/recurrent-checkpoint operation stays distinct from cold PP.

---

# Screened / no target movement

No post-cutoff exact receipt was found for:

- 2x M1 Max64/TB4 Flash-Next;
- one M1 Max64 Qwen3.8-27B;
- RTX5070Ti16 fully-resident Q3_K_XL/native-MTP canonical speed lane;
- 2x M1 Max64/TB4 DS4-0731.

Exact-rig web/Reddit results were older known receipts or previously incorporated capacity evidence; rediscovery/crawl time was not treated as freshness.

No post-cutoff rMLX change materially moved the speculative-state plan. No post-cutoff antirez/ds4 main change materially moved the DS4 target lane.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control.

Qualification now also requires:

1. actual **fusion census** in benchmark provenance;
2. direct recurrent-state producer -> authoritative destination A/B where rollback/ordering remain provable;
3. request-namespace lifetime independent of staged checkpoint-file lifetime;
4. device/global cursor truth through partitioning, rejection and rollback;
5. explicit owner/reader/absent state instead of dummy materialization;
6. activation representation in phase execution identity;
7. QSA selection-overlap/reuse instrumentation before any inverted-block wide-prefill kernel work;
8. exact selected-block identity and online-softmax equivalence for any block-inverted backend;
9. all existing QSA long-context, equal-acceptance MTP, content-shape, PLE residency, PP completion, deferred-free, B2/B3/B4 and soak gates.

Headline objective remains **40 TG @ ~128K active context + 400 cold PP**.

Safe serving remains **profitable singleton MTP + plain concurrent work** until simultaneous recurrent/spec state and workspace isolation are certified.

## Future Blazer / ~5.x BPW

Execution identity now includes:

- per-tensor precision / routed-vs-shared expert class;
- QSA indexer, recurrent/control and MTP-head precision;
- pack/group geometry;
- exact narrow-width SIMD/lane utilization and row-splitting strategy;
- verify-row geometry;
- sparse selected-row/narrow-fold compatibility;
- selected-block K/V packing and dequant granularity for shared-block reuse;
- online-softmax accumulation precision for blockwise QSA;
- actual fusion census;
- activation precision per phase;
- direct-state-write vs transient+copy form;
- first-eval transient memory;
- math implementation identity.

Continue evaluating at least Q5-dominant, expert-aggressive Q4-ish bulk + high-precision control/state, and sensitivity-optimized mixed-5.x families.

## Single M1 Max64 Qwen3.8-27B

No target movement. M5 A8 prefill is mechanism evidence only.

**P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed IQ4_XS remains a separate capacity lane.

## Dual-M1 DS4-0731

No target movement. V4.1 stays a separate future-architecture lane.

## Future DeepSeek V4.1 / large-memory Apple

Track separately:

- cross-layer compressor/KV ownership;
- ring/replay scratch semantics;
- Engram precision/residency;
- lazy-materialization peak memory;
- MTP/vision sidecars;
- 512-GB vs 1-TB quant tiers;
- eventual M5-Ultra exact TG/PP receipts.

---

# Standing decisions strengthened

- **40 TG @ ~128K remains the actual Flash headline objective.**
- **400 PP remains the cold-prefill objective.**
- Fusion intent is not execution; record actual fusion counts.
- Quant BPW is not execution cost; exact width/lane mapping matters.
- Activation precision is independent from stored-weight precision.
- Shared/absent state should not be represented by dummy buffers.
- Device/global request position remains authoritative through partitioning and speculative rollback.
- Persistent checkpoint namespace lifetime outlives any individual promoted file.
- Nominal model size below unified memory does not prove operational residency.
- Cross-layer state sharing is a trained/model contract unless explicitly proven otherwise; do not graft V4.1 sharing onto current Qwen weights by assumption.
- **MoBA's selector is not a drop-in Qwen replacement; its query/block inversion is retained only as an execution candidate with Qwen selection frozen.**
- Measure QSA block-selection reuse before implementing an inverted-block kernel.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **The 06:39 complete pass plus subsequent source-specific mining moved no target.**
- **P69 remains isolated.**
