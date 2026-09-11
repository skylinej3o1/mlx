# External runtime watch — 2026-09-11 06:39 ET

Search window: strictly after **2026-09-11 04:26:56 UTC** through **2026-09-11 10:39:19 UTC**.

This is a complete fresh-search delta. The intervening `RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` remains a source-specific mining note and is retained separately in the read chain.

## Executive result

**No canonical TG / PP target moves.**

The pass found useful Apple-kernel, speculative-state and future-V4.1 evidence, but no new exact target-topology receipt for:

- Qwen3.8-Flash-Next on **2x M1 Max 64 GB / TB4**;
- Qwen3.8-27B on **one M1 Max 64 GB**;
- the canonical fully-resident Q3_K_XL/native-MTP **RTX 5070 Ti 16 GB** speed lane;
- DeepSeek-V4-Flash-0731 on **2x M1 Max 64 GB / TB4**.

Canonical targets therefore remain:

| Model / hardware | Working TG | Working cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max 64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** |
| Qwen3.8-27B — M1 Max 64 | **25 tok/s** | **110 tok/s** |
| Qwen3.8-27B — RTX 5070 Ti 16 GB | **120 tok/s** | **250 tok/s** |
| DS4-0731 — 2x M1 Max 64 / TB4 | **15 tok/s** | **180 tok/s** |

The Flash 40 TG denominator is explicitly ~128K active context. Short-context 40 TG does not satisfy the headline objective.

---

# FRESH evidence

## 1. oMLX #3548 — M5 INT8-activation prefill can read the checkpoint's existing Q4/Q5 packed weights directly

Commit:

`83a641d2820c79383fb53ffb717eb7cf0a89e967`

Timestamp:

**2026-09-11 04:57:55 UTC**

Hardware / measured cell:

- MacBook Pro **M5 Pro 48 GB**;
- Qwen3.8-27B-oQ4e-mtp;
- `pp4096`;
- affine Q4/Q5 GS64 weight path;
- activation quantization INT8;
- prefill only.

Measured:

- **391.8 -> 518.5 tok/s prefill** (`+32.3%`);
- Q4 GEMM reaches **42 TOP/s** against a measured **44.21 TOP/s** ceiling.

Mechanism:

- eligible prompt-processing matmuls route through M5 tensor units as INT8 x INT8 -> INT32;
- packed Q4/Q5 weights are decoded directly into fragment registers;
- affine correction lands at GS64 boundaries;
- no second repacked weight copy is needed;
- the original checkpoint weight stream remains usable by decode;
- activation quantization is shared/amortized across projections where possible.

Important limitation:

- this changes numerics;
- it is off by default / opt-in;
- the PR explicitly says full real-workload accuracy has **not** yet been measured;
- brief agentic testing only reported no obvious degradation;
- it is M5-specific and does not numerically transfer to M1.

### Promotion

Treat **activation representation** as part of prefill execution identity, separate from stored-weight BPW.

For future M5-class / Blazer work, keep a candidate lane where:

> packed Q4/Q5 checkpoint weights stay canonical, while prefill activations are dynamically lowered to a tensor-unit-friendly format.

Certification must separately include:

- weight format;
- activation format;
- activation quantization cost / sharing factor;
- routed tensor families;
- prompt shape / chunk size;
- task-quality and logit drift;
- cold PP and task wall-clock.

Do **not** infer a current M1 target gain. M1 has no equivalent M5 tensor-unit path here.

---

## 2. oMLX #3563 — staged recurrent-checkpoint storage needs namespace lifetime, not just file lifetime

Commit:

`779ef216f11c4f1ff6c226dd48be452ca4d8499b`

Timestamp:

**2026-09-11 05:02:35 UTC**

Bug:

- `take_staged_file` moved a promoted boundary snapshot out and removed its request directory;
- a writer could already have created that directory and be about to write the next staging file;
- `rmdir` between those two steps caused the queued write to fail with `ENOENT`;
- the pending marker was released despite no file behind it;
- `commit_gdn_checkpoint` then returned false and the split-GDN store rejected the placeholder block one boundary early.

Fix:

- do not remove the request directory during staged-file promotion;
- request cleanup owns directory removal after all staged writers are done.

### Promotion

Our persistent GDN / recurrent checkpoint design needs an explicit lifetime hierarchy:

**request namespace -> staging generation -> file/object -> published boundary**.

A published/moved file does not imply the namespace is quiescent. Qualification should prove:

- queued writers retain the namespace until completion;
- pending/commit markers cannot outlive the physical object they promise;
- promotion and cleanup cannot race a future generation;
- cancellation/unload drains or invalidates staged generations before namespace reclamation.

This strengthens existing snapshot / boundary-generation ownership rules.

---

## 3. llama.cpp #28164 — Metal fusion became a first-class executable contract; one indexing bug silently cost ~5% TG

Commit:

`a2878d30df0130dde503a7d9ba30d3d21bd71b9f`

Timestamp:

**2026-09-11 09:41:54 UTC**

Key changes:

1. one single-source Metal fusion pattern table is consumed by both graph optimization/packing and compute encoding;
2. structural checks happen before allocation, full buffer-placement checks at compute time;
3. a bug passed a relative rather than absolute output index to fusion validation;
4. the bug silently disabled norm/MUL fusion and caused roughly a **5% token-generation regression**;
5. GDN followed by recurrent-state cache copy can fuse so GDN writes state snapshots directly into the cache target and the trailing copy is elided;
6. a generic fusion-stats API records which fusion patterns actually fire;
7. CI now compares fusion counts against a committed Metal backend baseline, with fusion-disabled as a zero-count control and fused/unfused numerical comparison.

### Promotion

Add an explicit **fusion provenance/census** layer to performance identity:

**declared pattern -> graph-packed adjacency -> eligibility check -> encoder match -> executed fusion count**.

Do not infer a fused route from source code or graph intent alone.

For P69/Blazer/Flash bring-up, record the actual fusion census for the benchmark cell. A silent lost fusion can be a multi-percent regression without any model-level correctness failure.

For recurrent state specifically, investigate direct producer-to-owner writes:

> GDN/recurrent kernel -> authoritative state/cache destination

instead of:

> GDN output -> transient snapshot -> copy/scatter -> authoritative destination.

But direct-write fusion must preserve ownership, rollback and consumer ordering; the llama implementation's pattern-specific validator is a useful design model.

---

## 4. llama.cpp #28692 — narrow quantized GEMV can waste most SIMD lanes; row splitting fixes the execution shape, not the bits

Commit:

`aac810230f9ef0cf73a47c56e46e87d0988be348`

Timestamp:

**2026-09-11 09:30:20 UTC**

Affected Metal IQ kernels:

- IQ1_S
- IQ1_M
- IQ2_XXS
- IQ2_XS
- IQ2_S
- IQ3_S

Mechanism:

- each thread owns one 32-element chunk;
- for `ne00 < 1024`, rows can contain fewer than 32 chunks, leaving part of the SIMD group idle;
- when the narrow chunk count divides 32, threads now split the output rows so those otherwise-idle lanes perform useful row work;
- wide-matrix path remains unchanged;
- K-quants have the same broad idle-thread problem but a different lane mapping and are explicitly left for separate work.

### Promotion — direct Blazer relevance

A quant recipe is not complete until its **small-width lane utilization** is certified.

For our eventual ~5.x-BPW execution format, explicitly measure:

- B1 GEMV / QMV narrow-K shapes;
- MTP verifier small-M shapes;
- routed expert shapes;
- QSA / sparse selected-row projections;
- lane occupancy / row splitting / tile geometry.

The fact that K-quants need separate treatment is important: a nominally attractive Q5/Q6 recipe can lose to another format if its Metal lane mapping strands SIMD work at the model's exact widths.

This reinforces the standing rule: **BPW and kernel layout must be co-designed.**

---

## 5. vLLM #55864 — shared KV should be represented as absent inputs, not dummy tensors

Commit:

`fbf51c70269bb0d8333e14c5788e628e33c72f5d`

Timestamp:

**2026-09-11 06:07:52 UTC**

Mechanism:

- a Gemma MTP layer reuses target K/V via KV sharing;
- the old API still manufactured dummy K/V tensors merely to satisfy a call signature;
- the backend now accepts `key=None`, `value=None` for the sharing layer;
- DCP prefill explicitly refuses this configuration where the backend does not support it.

### Promotion

When state is shared/owned elsewhere, encode that fact **semantically**, not by materializing dummy stand-ins.

For our PP2/MTP state interfaces:

- owner state and reader state should be explicit;
- absent producer data should be `None`/no-buffer, not a fake tensor;
- backend capability gates must distinguish decode, prefill, DCP/PP and speculative widths;
- unsupported combinations fail closed rather than silently allocating or copying redundant state.

This is especially relevant if future Qwen/DeepSeek-family architectures share sparse/KV state across layers.

---

## 6. vLLM #56107 — context partitioning + speculative decode requires preserving global position/state identity

Commit:

`980c16c8e4c66dce0bc4d355e4ec7fa2ae7b5141`

Timestamp:

**2026-09-11 05:07:53 UTC**

Adds prefill-context-parallel support for:

- single-module MTP;
- replicated DSpark.

Important mechanics:

- local partitions copy the already-materialized GPU `positions` instead of reconstructing them from lagging CPU request state;
- local hidden states are restored to the global layout before sampling;
- draft hidden states preserve the pre-partition representation needed by the speculator;
- auxiliary hidden states are restored too;
- sparse indexer slot mapping treats replicated MTP draft decode differently from PCP-expanded prefill;
- only supported speculative families/topologies are admitted.

### Promotion

For our PP/TP controls, distinguish:

**global request state -> partition-local execution state -> restored global sampling/spec state**.

Never recompute a global cursor from a host-side mirror merely because the local execution shard can derive a plausible value. After rejection/rollback, host and device request cursors can legitimately differ transiently.

This strengthens our existing device-truth / route-provenance / recurrent-ownership requirements.

---

## 7. vLLM #56214 — native DeepSeek-V4.1 support lands; cross-layer compressed state and query quantization are now concrete runtime contracts

Commit:

`e77daef89e18e08321ae7b8b24827eedd5fe8673`

Timestamp:

**2026-09-11 09:11:19 UTC**

This is **future-architecture / transfer evidence**, not a DS4-0731 target receipt.

Useful runtime evidence includes:

- native DeepSeek-V4.1 model support;
- compressor state with a dedicated circular/ring cache beside paged MLA and SWA groups;
- compressor metadata maps each real token explicitly into its ring slot while padding stays PAD;
- fused query RMSNorm + MXFP8 quantization is tested bitwise against the separate native quantizer, including graph replay;
- attention and indexer projections may consume the same pre-quantized query representation only when their consumer-kernel contract matches;
- retained/irrelevant scale metadata is explicitly guarded so dequantized paths do not accidentally reapply it.

### Promotion

For future V4.1 / Qwen4-like work, add state classes explicitly rather than flattening them into one generic KV concept:

- paged global attention state;
- cross-layer shared compressor/index state;
- bounded ring/replay state;
- recurrent state;
- speculative sidecar state.

Likewise, activation/query quantization can be shared across multiple consumers only when **consumer kernel identity and quantization key match**.

No current Qwen or DS4 target changes.

---

# BACKFILL / newly surfaced future Apple lane — DeepSeek-V4.1 MLX

These sources are useful and newly incorporated here, but their original repo/source activity predates this pass's hard boundary or lacks a reliable post-boundary publication timestamp. Treat them as **BACKFILL / TRANSFER**, not fresh target evidence.

## PipeNetwork/deepseek-v41-mlx

Public runtime description reports:

- DeepSeek-V4.1-Flash as **754.6B total parameters**;
- 40 layers × 384 routed experts;
- cross-layer KV/cache sharing where **layers 2/8/14/20 own compressor/index state and four owners serve all 40 layers**;
- layer 20's state serves layers 21-39;
- two Engram tables total **196.6B parameters**;
- mixed Apple build:
  - **427 GB**: mixed 4/8-bit with Engram 4-bit, aimed at 512-GB Macs;
  - **477 GB**: mixed 4/8-bit with Engram 6-bit, aimed at 1-TB machines.

Reported divergence ladder:

| recipe | tf mean | free@39 | cos@39 |
|---|---:|---:|---:|
| 8-bit | 0.0084 | 0.1243 | 0.9910 |
| 6-bit | 0.0177 | 0.1393 | 0.9886 |
| mixed 4/8, Engram native | 0.0335 | 0.1948 | 0.9800 |
| mixed 4/8, Engram 6-bit | 0.0335 | 0.1945 | 0.9801 |
| mixed 4/8, Engram 4-bit | 0.0342 | 0.2090 | 0.9775 |
| uniform 4-bit + Engram 4-bit | 0.0579 | 0.2714 | 0.9634 |

The runtime author therefore reports uniform 4-bit as **dominated** by the mixed recipe: only ~3 GB smaller but materially worse free-running drift.

Operationally important 512-GB result:

- the 477-GB Engram-6 build does **not** fit operationally on a 512-GiB machine despite the nominal file size;
- first/lazy materialization can transiently require roughly 2x build size and macOS compresses dirty MLX buffers rather than treating them as evictable page cache;
- the 427-GB Engram-4 build is the intended 512-GB tier.

### Promotion

This is a strong future-M5-Ultra lesson:

> **nominal checkpoint size < unified memory is not a sufficient residency test.**

Admission must price:

- resident weights;
- first-eval/lazy-materialization transient;
- allocator/wired/compressed memory behavior;
- cache/context growth;
- runtime scratch;
- MTP/vision sidecars if enabled.

For Blazer, this independently reinforces asymmetric precision allocation: large bulk memory structures can take lower precision while control/shared/index/state paths remain higher precision.

A separate experimental 2-bit V4.1 MLX build reports up to **9.5 tok/s** on an M3 Ultra 256 GB in short text-only custom-runtime testing, but explicitly lacks broad reasoning/coding quality validation. Treat this only as a low-bit feasibility receipt, not a production target.

---

# SCREENED / no target movement

Fresh exact-rig/current-web screening found no post-cutoff stronger receipt for:

- dual M1 Max64 / TB4 Flash-Next;
- one M1 Max64 Qwen3.8-27B;
- RTX5070Ti16 fully-resident Q3_K_XL/native-MTP canonical speed lane;
- dual M1 Max64 / TB4 DS4-0731.

Returned exact-rig Reddit rows were older known August/September evidence, including the already-incorporated RTX5070Ti 256K capacity lane and older M1 Flash/DS4 receipts. Crawl/rediscovery time was not treated as freshness.

No fresh post-cutoff rMLX commit materially changed the speculative-state plan.

No fresh post-cutoff antirez/ds4 main commit materially changed the DS4 target lane.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control.

Add/strengthen:

1. benchmark provenance includes an actual **fusion census**, not just enabled flags;
2. consider direct recurrent-state producer -> authoritative cache/state writes where ownership/rollback order can be proven;
3. persistent boundary/checkpoint stores need request-namespace lifetime independent of individual staged files;
4. partition/global request cursors use device truth through rollback/speculation;
5. shared state should be represented as owned/shared/absent, not dummy materialization;
6. activation representation is part of phase execution identity, even though the new M5 A8 path is not portable to M1;
7. keep all existing QSA long-context, MTP equal-acceptance, content-shape, PLE residency, PP completion, deferred-free and B2/B3/B4 gates.

Headline objective remains **40 TG @ ~128K active context + 400 cold PP**.

## Future Blazer / ~5.x BPW

Add to the execution descriptor:

- narrow-width SIMD/lane utilization;
- per-format row-splitting strategy;
- executed fusion census;
- activation precision per phase;
- direct-state-write vs transient+copy form;
- first-eval transient memory.

Continue to evaluate at least:

1. Q5-dominant;
2. expert-aggressive Q4-ish bulk + high-precision control/state;
3. sensitivity-optimized mixed 5.x.

## Single M1 Max64 Qwen3.8-27B

No target movement. M5 A8 prefill is mechanism evidence only.

**P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed IQ4_XS stays a capacity lane.

## Dual-M1 DS4-0731

No target movement. V4.1 evidence is a separate future architecture lane.

## Future DeepSeek V4.1 / large-memory Apple

Track separately from DS4-0731:

- cross-layer compressor/KV ownership;
- ring/replay scratch semantics;
- Engram precision/residency;
- lazy-materialization peak memory;
- native MTP inclusion;
- 512-GB vs 1-TB quant tiers;
- eventual M5-Ultra exact receipts.

The new Apple ports make a 512-GB V4.1 lane concrete enough to watch, but there is not yet an M5 Ultra production-style TG/PP receipt.

---

# Standing decisions strengthened

- Context and content shape remain part of performance-cell identity.
- Fusion intent is not execution; record actual fusion counts.
- Quant BPW is not execution cost; exact width/lane mapping matters.
- Activation precision is independent from stored-weight precision.
- Shared/absent state should not be represented by dummy buffers.
- Device/global request position is authoritative through partitioning and speculative rollback.
- Persistent snapshot namespace lifetime outlives any individual promoted file.
- Nominal model file size below unified memory does not prove operational residency.
- Cross-layer state sharing is a trained/model contract unless explicitly proven otherwise; do not graft V4.1 sharing onto current Qwen weights by assumption.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No target moved in this pass.**
- **P69 remains isolated.**

---

# Freshness

**New hard source-freshness boundary for the next complete external search: 2026-09-11 10:39:19 UTC.**

This boundary is the end of this complete search, not the later repository-write timestamp. Repository-only commits or source-specific mining must never advance it.
