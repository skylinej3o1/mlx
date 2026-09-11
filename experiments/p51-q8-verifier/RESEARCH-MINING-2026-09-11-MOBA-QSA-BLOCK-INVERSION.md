# Source-specific mining — MoBA for QSA execution design

Date: **2026-09-11 ET**  
Classification: **BACKFILL / MECHANISM / FUTURE KERNEL CANDIDATE**  
Does **not** advance the global external-search freshness boundary.  
Does **not** move any canonical TG / PP target.  
Does **not** interrupt P69B13.

## Primary source

- Enzhe Lu et al., **“MoBA: Mixture of Block Attention for Long-Context LLMs”**, arXiv:2502.13189v1, 2025-02-18.
- Moonshot AI / Tsinghua University / Zhejiang Lab-Zhejiang University.
- Official implementation: `MoonshotAI/MoBA`.
- The paper states that MoBA was deployed for Kimi long-context requests.

This note separates two very different ideas:

1. **MoBA as a trained attention architecture** — not a drop-in replacement for current Qwen3.8-Flash-Next QSA.
2. **MoBA's execution organization** — potentially portable to Qwen while keeping Qwen's existing QSA-selected block set fixed.

The second item is the useful one for this project.

---

# What MoBA actually does

MoBA partitions historical KV into blocks and routes each query to a small subset of those blocks.

For block `i`, the paper scores relevance with a query dot the mean-pooled key representation for that block, then takes top-k blocks subject to causality. The current block is always included and is evaluated causally.

The important implementation detail is **not** merely “top-k sparse attention.” The paper explicitly reorganizes the sparse relation for computation:

1. determine query -> KV-block assignments;
2. reorder/group query rows by the KV blocks they selected;
3. execute attention block-by-block with variable-length FlashAttention;
4. keep current-block causal attention separate from historical-block attention;
5. restore query ordering;
6. combine partial block results using **online softmax**.

In other words, instead of materializing a private gathered-KV tensor independently for every query row, the backend can turn

`query -> selected blocks`

into

`selected block -> all query rows that need it`.

That execution transformation is the main portable lesson for Qwen QSA.

---

# Paper evidence worth retaining

## Training/scaling setup

For the smaller scaling-law experiments:

- block size: **512**;
- top-k: **3**;
- at 8K sequence length this gives up to **81.25% attention sparsity**;
- MoBA and full-attention models show extremely similar LM-loss scaling.

For the 1M-context Llama-3.1-8B experiment:

- continual pretraining progresses 128K -> 256K -> 512K -> 1M;
- MoBA is activated for another **100B tokens**;
- block size: **4096**;
- top-k: **12**;
- the last **3** layers remain full attention while the other **29** use MoBA.

This is strong evidence that the architecture can preserve long-context quality after training, but it is also the reason we must not call MoBA a drop-in runtime transformation for current Qwen weights.

## Quality

At 128K on RULER:

- MoBA: **0.7818**;
- full attention: **0.7849**.

The paper also reports comparable results across a broad benchmark table and satisfactory Needle-in-a-Haystack performance through 1M.

Important qualification: in the downstream evaluation the paper uses **MoBA for prefill only and switches back to full attention for generation**.

Therefore the paper itself should not be used as evidence that sparse MoBA-style decode is always quality-neutral.

## Performance

The paper's headline speedups are **attention-layer computation**, not whole-model throughput:

- up to **6.5x** attention-forward speedup at 1M-token prefill;
- about **16x** lower attention computation time at 10M in its fixed-sparsity scaling experiment.

Do not transfer these numbers to end-to-end Qwen PP.

The portable conclusion is only that the query/block inversion plus blockwise varlen-attention organization scales much better than full attention when the selected-block relation is sufficiently sparse and query rows share historical blocks.

---

# What is NOT portable to Qwen3.8-Flash-Next without training

Do **not**:

- replace Qwen QSA's learned selector with MoBA's mean-pooled-K gate;
- change QSA block selection/top-k semantics merely because MoBA's gate worked after training;
- infer that Qwen can remove/replace QSA layers with MoBA layers;
- infer MoBA's quality numbers for untrained Qwen substitutions;
- apply the 6.5x or 16x headline attention speedups as whole-model or Apple multipliers.

Current Qwen weights were trained around QSA/GDN/PLE/MTP semantics. Selection identity remains part of correctness.

---

# Portable candidate: QSA inverted-block wide-prefill backend

## Core hypothesis

Hold the **existing Qwen QSA selector and selected block IDs exactly fixed**.

Only change the execution organization after selection:

### Current gathered-style mental model

For each query row:

`q_j -> selected blocks {b1, b2, ...} -> gather selected K/V -> attention`

Neighboring query rows often select many of the same historical blocks, so the same K/V block can be fetched/materialized repeatedly.

### MoBA-style inverted execution

Build the inverse incidence relation:

`block b -> {query rows that selected b}`

Then:

1. sort/bucket `(query, block)` edges by block id;
2. load each selected historical K/V block once per useful execution tile;
3. run its assigned query rows against that block;
4. maintain per-query online-softmax state `(m, l, acc)` across blocks;
5. separately handle Qwen's causal/current-tail requirement exactly as the official QSA path requires;
6. restore output rows to original query order.

If the exact same selected K/V rows and exact attention semantics are preserved, this can be an **execution-backend experiment**, not a model change.

---

# Why this is especially relevant to Apple / dual-M1

The potential gain is not “more sparsity”; QSA already supplies sparsity.

The potential gain is **KV reuse across query rows** during wide prefill:

- fewer repeated K/V block reads;
- less repeated gathered-KV materialization;
- better cache/local-memory reuse;
- an execution shape that may map better to wide prefill than the few-row gathered decode kernel;
- possible reduction in unified-memory bandwidth pressure on M1 Max.

This complements existing evidence rather than replacing it:

- oMLX #3520: selected-row gather form depends strongly on query width and context;
- oMLX #3553: narrow decode/verify should consume indexed K/V directly instead of materializing gathers;
- MoBA suggests a distinct **wide-prefill** backend where shared selected blocks become the unit of work.

The likely design split is therefore:

- **B1 decode / MTP small-M:** indexed selected-K/V direct kernel;
- **wide prefill:** candidate inverted block->query backend;
- retain existing gathered/copy paths as controls because crossover depends on `(context, query rows, selected-block overlap)`.

---

# Required first measurement: selection-overlap topology

Do not write the kernel before measuring whether Qwen's real QSA selections provide enough reuse.

Instrument representative QSA prefill chunks and record, per layer/head/chunk:

- query rows `M`;
- selected blocks per query;
- number of unique selected historical blocks;
- total query-block edges;
- **reuse factor = edges / unique selected blocks**;
- block popularity histogram;
- Jaccard / overlap of selected blocks across adjacent query rows;
- overlap versus query-row distance;
- selected-block run length / temporal locality;
- current-tail fraction versus historical-block fraction;
- distribution by content shape: code, prose, CJK/multilingual, tools/agent transcripts.

A block-inverted backend is attractive only if enough query rows share selected blocks to amortize bucketing and online-softmax bookkeeping.

---

# Proposed A/B matrix if overlap is promising

Compare against the exact current QSA selected-block set.

## Query widths

- 16
- 32
- 64
- 128
- 256
- 512
- 1024
- 2048

## Context

- 16K
- 32K
- 64K
- 128K
- 256K where practical

## Arms

1. current token-major/copy gathered path;
2. current stored-layout selected-row path where legal;
3. inverted block->query backend;
4. optional hybrid dispatcher chosen from measured crossover.

## Record

- kernel wall time;
- total QSA-layer wall time;
- cold PP;
- K/V bytes read or best available proxy;
- selected-row materialization bytes;
- bucketing/sort cost;
- online-softmax merge cost;
- temporary memory;
- fusion/execution census;
- exact selected-block identity;
- output/logit parity;
- whole-model cold PP, not only attention microbenchmarks.

Do not claim a win from an attention-only microbenchmark if whole-model PP does not improve.

---

# Correctness gates

For the execution-only experiment:

1. **Selector frozen:** identical selected block IDs versus the control for every query/head/layer.
2. **Causality identical:** current-tail/current-block masking must match QSA semantics exactly.
3. **KV identity:** backend consumes the same K/V values in the same logical token order.
4. **Online-softmax equivalence:** compare against the canonical selected-K/V attention result; use precise accumulation semantics where needed.
5. **No hidden route changes:** selection/indexer precision, QSA route, block geometry and kernel-set identity are benchmark provenance.
6. **Long continuation:** if any tolerance-level math remains, separate bit-exact cycle cost from continuation-dependent client TG using the existing #3553 methodology.
7. **PP2 ownership:** stage-local K/V remains stage-local; this optimization must not create dense/repeated TB4 traffic.

---

# Relation to PP2 / Thunderbolt

This idea should not change the current PP2 topology thesis.

Under PP2/layer ownership:

- each Mac owns the QSA state for its assigned layers;
- block inversion is local to that stage;
- only stage-boundary activations should cross TB4 in the normal path;
- no new cross-node selected-KV exchange should be introduced.

Therefore its expected value is primarily reduced **local unified-memory traffic / materialization**, not reduced full-KV TB4 transfer.

---

# Relation to Blazer

This adds another reason that quant format cannot be designed independently from sparse-attention execution.

For a future 5.x-BPW Flash stack, selected K/V / projections should be evaluated against both:

- narrow indexed direct-consume kernels;
- wide block-inverted prefill kernels.

A packing/layout that is ideal for B1 QMV but expensive to load/dequant once per shared block may be suboptimal overall.

Blazer execution identity therefore should eventually include:

- selected-block K/V pack layout;
- dequant granularity versus QSA block geometry;
- ability to reuse a decoded block across multiple assigned query rows;
- online-softmax accumulation precision;
- query/block bucketing representation.

---

# Current project consequence

Add one future Flash candidate:

> **QSA wide-prefill inverted-block backend:** keep Qwen's learned selected-block set fixed, transpose the sparse query/block relation, evaluate each historical block for all assigned query rows, and merge with online softmax.

Priority order:

1. instrument real QSA selection-overlap/reuse first;
2. prototype only if reuse is high enough;
3. compare whole-model cold PP at ~128K, not just a kernel microbenchmark;
4. preserve current gathered paths as measured controls;
5. do **not** interrupt P69B13 for this work.

No canonical target changes.

The dual-M1 Flash headline remains:

- **40 TG @ ~128K active context**;
- **400 tok/s cold PP**.

Global external-search cutoff remains **2026-09-11 10:39:19 UTC** because this is source-specific backfill/mining, not a new complete freshness pass.
