# Qwen3.8-Flash-Next conditional memory / SSD-tier research note

Status: **CORE / released architecture / high-leverage MXFORGE lead**

Updated: 2026-08-26 after official weight release

## Release status

The August 26 release confirms the previously previewed numbers and makes the storage/offload thesis substantially stronger.

Primary sources:

- https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- https://qwen.ai/blog?id=qwen3.8-flash-next
- https://huggingface.co/docs/transformers/model_doc/qwen4_exp
- https://www.lmsys.org/blog/2026-08-26-qwen-flash-next/
- https://github.com/QwenLM/Qwen3.8-Flash-Next

Confirmed language-model topology:

- 125B main-model parameters;
- 6B activated per token;
- +51B / 51.2B N-gram PLE parameters;
- +4B one-layer MTP module;
- hidden size 2560;
- 48 decoder layers;
- 36 Gated DeltaNet layers + 12 Qwen Sparse Attention layers;
- 512 routed experts, top-10 routed + one shared expert;
- MoE intermediate size 640;
- native 262,144 context, extensible to 1M with YaRN;
- QSA compression ratio 4, selecting 512 blocks / 2048 logical tokens per full-attention layer.

The Hugging Face BF16 checkpoint is about 360 GB, consistent with roughly 180B total parameters across the main model, PLE and MTP.

## The PLE is exactly the kind of memory we hoped it was

The official config places a single Per-Layer Embedding (PLE) memory at configured layer ID 2, near the start of the decoder.

Exact released PLE structure:

- `ngram_size = 3`;
- 8 bigram hash heads using `(x[t-1], x[t])`;
- 8 trigram hash heads using `(x[t-2], x[t-1], x[t])`;
- 16 selected embedding rows per token total;
- each row contributes 160 values;
- concatenated PLE vector width = 2560;
- total PLE parameters = 51.2B;
- BF16 table footprint = about 95.4 GiB;
- fixed read-only model weights, not KV cache or mutable attention state.

SGLang documents two small request-local PLE states: the recent token IDs needed for hashing and a short-convolution history. The target model uses PLE during prefill, decode and target verification; the one-layer MTP draft disables PLE.

This is materially better for speculative decoding than having the draft repeatedly touch the giant table.

## Production proof: sparse host-memory offload already works

The strongest day-0 result comes from SGLang's implementation for the actual released model.

SGLang keeps each rank's vocabulary-parallel PLE table shard in **pinned host memory** and gathers only the 16 selected rows into a small BF16 GPU buffer. A dedicated CUDA stream overlaps the gather with the first decoder block.

On H200, TP4, MTP-213:

- target-model GPU weight footprint: 83.91 -> 60.45 GiB per GPU;
- PLE offload freed 23.46 GiB/GPU;
- allocated KV capacity: 1.84M -> 3.28M tokens (+78.54%);
- matched throughput at concurrency 1/2/4: effectively unchanged, -0.07% geometric mean;
- four fixed prompts matched exactly in output token IDs;
- first-case chosen-token logprob trace also matched exactly.

Therefore these points are now **measured on Qwen3.8-Flash-Next itself**, not merely inferred from Engram:

1. the PLE can live entirely outside accelerator memory;
2. only sparse selected rows need to cross the slow-memory boundary;
3. asynchronous prefetch can hide essentially all of the transfer cost in a tuned implementation;
4. offload preserves model math / output exactness.

## Raw transfer volume is tiny; latency is the real problem

Per token, PLE logically retrieves:

- 16 rows;
- 160 BF16 values/row;
- 2560 BF16 values total;
- about 5 KiB of useful embedding payload per token.

At 20 tok/s this is only about 100 KiB/s of useful data. Even at 150 tok/s it is under 1 MiB/s.

So SSD feasibility is not fundamentally a sequential-bandwidth problem. It is a **random-latency, page-granularity, cache-hit and prefetch-timing problem**.

This is favorable for MXFORGE because token IDs deterministically define the lookup addresses.

## Checkpoint layout is promising but stock Transformers is not enough

The released config contains:

- `ngram_vocab_size_base = 20_000_000`;
- `ple_embed_dim = 2560`;
- `heads_per_ngram = 8`;
- `split_ngram_parts = 128`.

Transformers documentation explicitly says `split_ngram_parts` controls logical checkpoint shards for the giant PLE table, **but current Transformers concatenates those parts into one runtime embedding weight**.

That means:

- checkpoint separability: **confirmed**;
- stock HF runtime keeping the table SSD-backed: **no**;
- custom MXFORGE loader/runtime needed for true SSD-resident sparse lookup: **yes**.

The 128-way checkpoint split is nevertheless extremely convenient for building a non-concatenating loader.

## Capacity math

Approximate storage for the 51.2B PLE table:

| Representation | Decimal GB | GiB |
|---|---:|---:|
| BF16 | 102.4 | ~95.4 |
| Q8 | 51.2 | ~47.7 |
| Q6 ideal | 38.4 | ~35.8 |
| Q4 ideal | 25.6 | ~23.8 |

Main 125B body, idealized:

| Representation | GiB |
|---|---:|
| BF16 | ~232.8 |
| Q8 | ~116.4 |
| Q6 | ~87.3 |
| Q4 | ~58.2 |

The separate 4B MTP module is another ~7.45 GiB BF16 / ~1.86 GiB ideal Q4.

So a single 64GB M1 Max still does **not** comfortably fit a fully resident Q4 main body + Q4 MTP + runtime/KV/hot PLE cache. PLE SSD offload solves the extra 51B capacity problem, but not by itself the 125B main-model residency problem.

## The main model is itself unusually offload-friendly

The released config strongly suggests that most of the 125B body is the routed expert pool.

For a standard SwiGLU expert with three `2560 x 640` matrices:

- ~4.915M parameters/expert;
- x512 experts;
- x48 layers;
- ~120.8B routed-expert parameters.

This is a derived estimate from the config, not an official parameter decomposition, but it is consistent with the advertised 125B total and 6B active-per-token figure.

If correct, roughly 97% of the nominal main body is routed-expert capacity while only 10/512 routed experts are selected per layer for a token.

That makes Flash-Next an unusually strong candidate for combining:

1. sparse PLE offload;
2. hot/cold MoE expert residency;
3. DwarfStar / FreeToken-style expert prefetch and retention;
4. MTP speculative decoding;
5. QSA long-context sparsity.

In other words, **both giant sources of parameter count are sparse-access structures**.

## MXFORGE M1 hierarchy hypothesis

Apple Silicon has unified memory, so there is no separate large CPU-DRAM tier analogous to an H200 server. The natural hierarchy becomes:

```text
M1 unified memory
  - dense/core weights
  - hot routed experts
  - hot PLE rows/pages
  - KV / GDN / QSA state
        |
        v
macOS page cache / explicit caches
        |
        v
internal NVMe SSD
  - cold PLE table
  - cold routed experts
```

The PLE table can be treated as read-only SSD backing with sparse promotion. MoE experts can use a separate retention/prefetch policy driven by router behavior.

The research question is no longer whether 51B PLE offload is architecturally legitimate. It is:

> **Can NVMe latency be hidden nearly as well as SGLang hides pinned-host latency, using deterministic PLE addressing, page/cache locality and overlap with layer-0 compute?**

## Prefill is especially favorable

For a known prompt, all token IDs are available in advance, therefore every PLE hash lookup is knowable before execution.

MXFORGE can in principle:

1. hash the entire prompt;
2. enumerate the exact 16 PLE row IDs/token;
3. deduplicate rows/pages;
4. sort/coalesce disk requests;
5. prefetch pages before or during prompt chunks;
6. retain frequently reused coding/tool N-grams for later turns.

Decode has less lookahead because the next token is unknown until sampled, but PLE is placed near the start of the model and SGLang already demonstrates overlapping its gather with the first decoder block. On M1 we need to determine whether an SSD/page-cache pipeline leaves enough overlap window.

## Coding-agent locality hypothesis

Code/tool traffic should be measured separately from prose because it may show unusually favorable N-gram locality:

- programming syntax;
- JSON/XML/tool envelopes;
- shell/Git commands;
- repeated repository names and paths;
- framework idioms;
- repeated agent scaffolding.

Desired outcome:

> **nearly all PLE capacity can remain SSD-backed while nearly all recurring accesses are served from unified-memory/page-cache hot state.**

## QSA / rolling-agent relevance

QSA itself is another major agentic lever:

- only 12/48 layers maintain growing attention K/V;
- 36/48 GDN layers use fixed-size recurrent state;
- QSA indexes roughly `L/4` compressed blocks but performs final sparse attention over only ~2K original K/V positions;
- the index is not a lossy replacement for the selected values: final attention reads original K/V entries.

Qwen also preserves historical thinking by default and explicitly frames this as beneficial for decision continuity and KV-cache utilization in agent scenarios.

This architecture therefore aligns unusually well with MXFORGE's rolling-agent work: stable prefix/KV continuity, external artifact memory, sparse long-context retrieval and conditional parameter memory can all reduce the need to treat the physical attention window as the agent's lifetime memory.

## First MXFORGE experiments

### A. PLE-only storage characterization

Sweep:

- full resident baseline;
- mmap/SSD backing with OS page cache;
- explicit 1/2/4/8 GiB hot cache;
- BF16/Q8/Q6/Q4 PLE representations if exact/quality-safe paths exist.

Measure:

- unique PLE rows/token;
- page working set;
- hit rate by tier;
- demand misses/token;
- bytes read/token;
- SSD read latency;
- prefetch hit rate;
- TTFT / prompt processing;
- decode tok/s;
- swapouts / memory pressure;
- SSD write amplification (should be near-zero for read-only weights).

### B. Expert-cache characterization

Measure routed-expert locality separately:

- experts touched/token;
- reuse distance;
- layer-specific hot sets;
- coding vs prose routing locality;
- cache size vs miss curve;
- prefetch accuracy using current-layer / prior-token router history.

### C. Combined heterogeneous-memory runtime

Only after A/B are characterized:

```text
core + hot experts + hot PLE -> unified memory
cold experts + cold PLE      -> SSD
MTP                           -> resident if beneficial
```

Evaluate complete coding-agent task time, not just tok/s.

## Two-M1-Max implication

Two 64GB M1 Max systems remain attractive because they give the main model much more comfortable residency while allowing PLE to stay external:

```text
M1 Max #1         M1 Max #2
    \                /
     \ main backbone/
      TP / PP / custom
           |
  PLE hot: UM/cache
  PLE cold: SSD
```

But the release makes a **single 64GB M1 more interesting than before** because a custom runtime may not need either the 51B PLE table or the full ~121B expert pool resident simultaneously.

## Evidence status

- Qwen4-preview status: **confirmed**;
- 125B main + 51B PLE + 4B MTP / 6B-active: **confirmed**;
- single PLE layer near decoder start: **confirmed**;
- 16 PLE rows/token, 8 bigram + 8 trigram heads: **confirmed by SGLang day-0 implementation**;
- whole PLE resident in host RAM instead of GPU: **measured on released model**;
- host-offload performance penalty: **~0.07% geometric mean in SGLang H200 TP4 test**;
- exact output preservation under host offload: **measured**;
- checkpoint PLE split into 128 logical parts: **confirmed config**;
- current Transformers concatenates PLE shards at runtime: **confirmed docs**;
- NVMe SSD as cold PLE tier on M1: **not yet measured**;
- custom expert streaming on M1: **not yet measured**;
- M1 performance: **unknown; benchmark locally**.
