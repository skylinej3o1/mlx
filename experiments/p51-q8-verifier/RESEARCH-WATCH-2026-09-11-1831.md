# External runtime watch — 2026-09-11 18:31 ET

Search window: **strictly after 2026-09-11 18:30:00 UTC through 2026-09-11 22:31:55 UTC**.

Scope remains limited to the hardware/execution lanes we actually own or are building:

- Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4;
- Qwen3.8-27B — one M1 Max 64 GB;
- Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM;
- DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4;
- Blazer / custom ~5.x-BPW execution work where evidence is portable.

Stronger Apple hardware is retained only when it teaches a mechanism directly relevant to those lanes. It does not create a future-M5 purchase lane.

Evidence discipline is unchanged: source timestamp controls freshness; exact-target receipts, transfer/mechanism evidence, experimental A/Bs and planning targets remain separate; component gains do not become TG/PP multipliers without target-topology reproduction.

## Executive result

**No canonical target moves.** No fresh exact receipt appeared for:

- 2x M1 Max64/TB4 Flash-Next;
- one M1 Max64 Qwen3.8-27B;
- RTX5070Ti16 fully-resident Q3_K_XL/native-MTP;
- 2x M1 Max64/TB4 DS4-0731.

The strongest fresh result is `jundot/omlx#3589`, an **open** Flash-Next expert-offload PR showing that exact miss handling can be made much less latency-bound by overlapping positional reads while preserving serial cache-state mutation. This materially improves the emergency capacity/offload lane, but it does **not** change the primary dual-M1 strategy: keep routed experts resident when feasible and spend offload complexity first on naturally sparse PLE/n-gram state.

Two fresh merged vLLM changes add portable correctness/runtime lessons: DFlash/DSpark speculative attention metadata must distinguish physical padded execution from logical query counts, and dynamic per-request shapes should not be baked into JIT specialization keys when the kernel math does not need specialization.

---

# FRESH — oMLX #3589: parallel exact expert-miss reads

PR: `jundot/omlx#3589`  
Created: **2026-09-11 19:34:09 UTC**  
State at cutoff: **open, non-draft, unmerged**.

Classification: **FRESH / EXACT MODEL-FAMILY / STRONGER-APPLE TRANSFER / CAPACITY-OFFLOAD A/B**.

The existing exact expert-offload path performed each cache miss as a serial synchronous memmap copy on the compute thread. #3589 changes the miss path into two phases:

1. classify all misses for the call without mutating cache state, then issue bounded parallel `os.pread` reads using read-only shard descriptors;
2. preserve the original serial install order for slot writes, LRU victims, hit/miss counters, resident-byte accounting and cache maps.

This is an important design separation: **I/O arrival may be parallel while ownership/state mutation remains serialized and deterministic**.

Physical A/B supplied by the PR:

- Apple M5 Pro 64 GB;
- `Vontra/Qwen3.8-Flash-Next-MLX-oQ2-MTP`;
- 48 routed layers, 512 experts/layer, top-10, about 1.84 MB/expert;
- PLE mmap;
- MTP off;
- greedy;
- identical prompts before/after.

| residency | cell | serial | parallel pread |
|---:|---|---:|---:|
| 25% | 3461-token TTFT | 183 s | **18.7 s** |
| 25% | decode after prompt | 4.4 tok/s | **17.7 tok/s** |
| 25% | 122-token warm decode | 2.3 tok/s | **16.2 tok/s** |
| 68.8% | 3461-token TTFT | 30.1 s | **4.5 s** |
| 68.8% | decode after prompt | 13.6 tok/s | **19.7 tok/s** |
| 68.8% | 122-token warm decode | **23.9 tok/s** | 22.4 tok/s |

Generated text was identical to the serial baseline and loaded size was unchanged; the PR reports 33.9 GB at 68.8% residency.

## Interpretation

The low-residency results show that the old path was often **I/O-latency bound rather than storage-bandwidth bound**. Parallel positional reads recover very large fractions of TTFT and decode throughput without changing routing or numerical output.

The 68.8% warm-decode row is equally important: once miss pressure is low, extra read-pipeline machinery is not automatically a win. Do not treat the large low-residency ratios as universal model-level multipliers.

The next proposed step in the PR is schedule-aware prefetch: prefill can know the distinct expert set for a chunk before installation, while decode has measured LRU-to-optimal hit-rate headroom. That is a candidate, not a promoted result.

## Project consequence

For any future capacity-constrained Flash experiment:

- preserve exact router decisions;
- split miss handling into **parallel immutable reads** and **serial deterministic publication/state mutation**;
- bound worker count and in-flight bytes explicitly;
- record residency fraction, miss rate, bytes/read operations, TTFT, task wall-clock and TG;
- benchmark high-residency warm decode separately so offload plumbing does not regress the easy case;
- if chunk-ahead prefetch is attempted, prove that prefetched data is advisory only and cannot mutate routing/cache ownership ahead of the committed execution order.

This improves the capacity lane but does not displace resident experts or PP2/layer ownership as the primary dual-M1 Flash architecture.

---

# FRESH — vLLM #56181: DFlash/DSpark padded-token metadata correctness

Merged commit: `9dcf6bf344caa7793bae0b45a7896d3f8e03a01a`  
Merged: **2026-09-11 21:33:53 UTC**.

Classification: **FRESH / SPECULATIVE-DECODE CORRECTNESS TRANSFER / NOT TARGET SPEED EVIDENCE**.

Failure mode: with DP > 1, synchronization can add physical padding tokens. DFlash/DSpark attention metadata could then disagree about token population: `query_start_loc_cpu` represented logical query tokens while `num_tokens` represented the padded execution shape. FlashInfer could fail because the actual query tensor row count no longer matched the attention indptr terminal count.

The fix centralizes a uniform attention-metadata builder:

- under FULL CUDA graph execution, use the padded physical token/request count from the batch descriptor;
- otherwise use the actual logical query count;
- reuse the contract for DFlash/DSpark proposal and the later single-draft decode steps used by MTP/EAGLE.

Relevant benchmark cells in the PR include:

- Qwen3.8-27B + Qwen3.8-27B-DFlash2, DP1: acceptance length ~3.92 -> 3.89 and acceptance rate 41.65% -> 41.29%, with throughput essentially unchanged;
- Qwen3-Coder DFlash DP2: **crash -> successful serving** after metadata correction;
- DeepSeek-V4-Flash MTP and DSpark cells remained within small acceptance deltas.

Absolute GPU rates are not portable to our hardware and do not move targets.

## Project consequence

Extend route/state provenance with explicit distinction between:

- logical request rows/tokens;
- physical padded rows/tokens actually executed;
- graph/capture execution shape;
- attention metadata shape;
- slot/cache mapping shape;
- speculative draft population.

For Flash PP2/batching qualification, **requested row count is not execution row count**. Any padding introduced by synchronization, batching or compiled graph buckets must propagate consistently through QSA/indexer/cache/spec metadata. Final output alone is not a sufficient proof because rejection or masking can hide speculative corruption.

---

# FRESH — vLLM #56153: dynamic shapes should not poison the JIT cache key

Merged commit: `2d75e586fcaf88231f7a75f482dc8bfb5ad9da10`  
Merged: **2026-09-11 21:34:17 UTC**.

Classification: **FRESH / DSV4 INDEXER KERNEL MECHANISM / PORTABLE COMPILE-LIFECYCLE EVIDENCE**.

A DSV4 indexer quant-cache gather kernel treated four runtime values as Triton compile-time constants:

- total tokens;
- batch count;
- block-table width;
- block count.

The first two vary frequently in serving. Because they entered the compile-cache identity, new prompt/shape cells could trigger fresh kernel compiles; the PR reports **several seconds of cold latency** in local-serving situations. The patch leaves true structural constants specialized while moving shape/batch values to runtime arguments. Kernel math/output are unchanged.

## Project consequence

For QSA/indexer/Blazer/custom Metal kernels, explicitly divide kernel identity into:

**Structural specialization** — layout, head dimension, packing, tile geometry, precision, algorithm choice.

**Runtime shape** — token count, batch count, request padding, table length/block count where the math does not require specialization.

Do not casually promote high-cardinality request-shape values into compiled-kernel identity. Benchmark:

1. first-ever compile;
2. first request for a new runtime shape;
3. warmed steady state;
4. shape churn across realistic agent traffic.

A steady-state kernel win that repeatedly recompiles on normal request-shape changes can lose badly in task wall-clock/TTFT.

---

# FRESH BUT SCREENED — oMLX #3590 DeepSeek V4.1 fast path

PR: `jundot/omlx#3590`  
Created: **2026-09-11 21:33:25 UTC**  
State at cutoff: **open, unmerged**.

M3 Ultra results in the PR report stock V4.1 around 15.5 tok/s decode / 337 tok/s ~2K prefill and the proposed default stack around 26.5-27.2 / 490-500 with Engram stub; mmap + hot cache is around 25.5 / 481. B8 aggregate decode is reported near 79.5 tok/s.

This is **later-architecture stronger-Apple transfer only**. It is not DS4-0731 evidence and does not create a V4.1/future-hardware lane.

Portable notes worth retaining:

- preserve shared cache/pool identity when converting singleton caches to batched forms;
- append-only state needs explicit semantics rather than assuming every cache advances a common processed cursor;
- wired-memory policy can dominate large-UMA execution if the working set is otherwise forced into thrash;
- batch aggregate throughput and independent-singleton equivalence require separate correctness tests — the PR itself notes batch-vs-independent B1 is not yet bit-exact.

No target movement.

---

# Screened / recovered older / non-portable items

- `jundot/omlx#3583` was created before this freshness window; later update activity does not make its earlier format-metadata body fresh.
- oMLX ANE-bank accounting #3425 is valuable but already belongs to the existing hidden-resident-memory evidence chain; its body predates this pass.
- llama.cpp activity after the boundary did not add a fresh Apple Metal / exact-target receipt. Generic CI/build and non-target backend work was screened out.
- `antirez/ds4` had no commit or issue activity in the search window.
- A web search rediscovered an M1-Max Qwen3.8-27B benchmark and an M4-Pro Flash deployment; their substantive publication/update dates precede this window, so they are **RECOVERED OLDER EVIDENCE**, not fresh evidence.
- Same-day community multi-GPU Qwen3.8-27B reports are different GPU/topology/quant lanes and do not supersede the RTX5070Ti16 canonical receipt set.

---

# Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** |

No probability/confidence calibration changes in this pass.

---

# Current consequences

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Add/retain:

- load/materialization/first-eval transient telemetry;
- explicit control-plane vs data-plane provenance;
- physical draft-head stage and explicit draft-token transport;
- recurrent/QSA/indexer/spec-state ownership and pointer freshness;
- logical rows/tokens vs physical padded execution rows/tokens;
- graph-bucket/compiled-shape identity;
- final-output parity separate from draft-acceptance parity;
- PP1-vs-PP2 acceptance parity;
- kernel compile-cache cardinality and cold-vs-warm timing;
- expert occupancy/tail geometry;
- PLE as a separate sparse placement plane;
- if expert offload is used, parallel immutable reads + serial deterministic cache mutation, with high-residency regression cells;
- code/prose/CJK/tool/low-acceptance long-context cells.

Safe serving remains profitable singleton MTP + plain concurrent work until physical per-slot recurrent/spec state and workspace isolation are certified.

## Blazer / ~5.x BPW

Add compiled-kernel specialization identity to the existing execution identity: distinguish structural specialization from high-cardinality runtime shape. Cold compile, shape-churn wall-clock and warmed kernel rate are separate benchmark cells.

## Qwen3.8-27B M1 Max64 / P69

No change. **P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

## RTX5070Ti16

No change. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane. No fresh exact-rig receipt appeared.

## DS4-0731 dual M1

No change. DSV4/V4.1 GPU or newer-architecture work is mechanism transfer unless it reproduces the DS4-0731 topology/runtime question directly.

---

# Standing rules

- Evidence timestamp = substantive source timestamp, not rediscovery time.
- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Benchmark cell = actual executed route, not requested flags.
- Route provenance ladder remains requested -> configured -> compiled -> armed/admitted -> executed.
- Logical work shape and physical padded/compiled execution shape are both part of provenance.
- Final-output correctness is not sufficient speculative correctness; rejection can mask corrupt drafts.
- B2/B3/B4 require physically simultaneous independent requests with correct persistent state.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **Do not actively track future M5/M5 Ultra purchase performance until the user reopens that scope.**
