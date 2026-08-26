# Qwen3.8-Flash-Next conditional memory / SSD-tier research note

Status: **CORE / architecture research lead**

Updated: 2026-08-26

## Why this matters

Qwen has officially announced `Qwen3.8-Flash-Next` as an **upcoming release and preview of the Qwen4 architecture**:

- https://huggingface.co/Qwen/Qwen3.8-Flash-Next

A now-edited ModelScope preview, repeated in the NVIDIA DGX Spark forum, described the model as roughly:

- 125B main-model parameters
- +51B N-gram embedding parameters
- ~6B parameters active per token

Forum thread:

- https://forums.developer.nvidia.com/t/qwen3-8-flash-next/381228

Treat those exact `125B + 51B / 6B active` numbers as **preview / not-yet-certified** until the released config and checkpoint can be inspected. The official Hugging Face countdown currently confirms the Qwen4-preview status but not those sizes.

The important architectural lead is the possibility that the extra 51B are not ordinary compute weights, but a large sparse conditional-memory table analogous to DeepSeek's Engram / Deep Sparse Embedding work.

## Primary architectural precedent: Engram / DSE

Paper:

- https://arxiv.org/abs/2601.07372
- https://aclanthology.org/2026.acl-long.226.pdf

Key properties:

- classic N-gram-style embedding lookup modernized as conditional memory;
- deterministic addressing rather than learned expert routing;
- bigram/trigram hash mappings in the demonstrated system;
- only activated lookup rows need to move per token;
- total table capacity can therefore be much larger than the working set.

Most important systems result:

The paper inserted a **100B-parameter DSE table entirely in host DRAM** and asynchronously prefetched the required rows while preceding transformer compute ran. Reported throughput penalty was only:

- 1.9% on a 4B dense backbone;
- 2.8% on an 8B dense backbone.

The paper explicitly states that effective communication volume scales with **activated slots rather than total embedding-table size**.

It then proposes a multi-level hierarchy exploiting Zipfian N-gram frequency:

```text
HBM / unified-memory hot rows
        ↓
CPU / system DRAM
        ↓
NVMe SSD cold tail
```

The SSD tier is a proposed optimization in this primary paper, not the measured 1.9-2.8% experiment; that experiment used host DRAM.

## Stronger SSD precedent: TF-Engram

Paper:

- https://arxiv.org/abs/2607.07388

`TF-Engram` explicitly stores large phrase-memory tables across a **GPU -> DRAM -> SSD hierarchy** and uses predictive prefetching to hide external-memory latency. It is not evidence for Qwen3.8-Flash-Next specifically, and its model-scale evaluation uses Qwen3-0.6B, but it materially strengthens the feasibility of SSD-backed phrase memory as a systems primitive.

## Capacity math if the preview 51B figure is real

Approximate storage for a 51B-parameter N-gram table:

| Representation | Decimal GB | GiB |
|---|---:|---:|
| FP16/BF16 | 102.0 | ~95.0 |
| Q8 | 51.0 | ~47.5 |
| Q6 ideal | 38.25 | ~35.6 |
| Q4 ideal | 25.5 | ~23.7 |

This is unusually SSD-friendly capacity. Even an ideal-Q4 copy of the entire rumored table is only ~23.7 GiB.

By contrast, if the main body is truly 125B parameters, ideal Q4 alone is ~58.2 GiB. Therefore the **main backbone, not the N-gram table, is likely the harder single-M1-Max capacity problem**.

## MXFORGE design hypothesis

Do **not** require the whole conditional-memory table to be resident.

Preferred experiment topology:

```text
full conditional-memory table
        ↓
internal NVMe SSD (authoritative backing)
        ↓
mmap / page cache
        ↓
explicit hot-row cache in unified memory
        ↓
lookup consumer layers
```

Initial hot-cache sweep:

- 1 GiB
- 2 GiB
- 4 GiB
- 8 GiB

Do not assume the optimum hot fraction from total-table size. Measure the real coding-agent access distribution.

## Why prefill is especially favorable

For a known prompt, all token IDs are known before model execution. If lookup addresses are deterministic, MXFORGE can in principle:

1. compute every N-gram lookup address for the prompt;
2. deduplicate addresses;
3. sort/coalesce SSD ranges;
4. prefetch required pages before or while prompt chunks execute;
5. keep high-frequency rows resident for later turns.

This is materially easier than predicting ordinary MoE expert selection.

Decode is less deterministic because each next token is not known until sampled, but immediately after token selection the N-gram addresses become known. If the memory lookup occurs after enough early-layer compute, that interval can be used as a prefetch window.

## Coding-agent locality hypothesis

Code/tool traffic should be tested separately from prose because it may have exceptionally strong N-gram locality:

- language syntax;
- JSON / XML / tool envelopes;
- Git and shell commands;
- repeated repository identifiers;
- common programming idioms;
- repeated agent scaffolding.

The hypothesis is not that most of the 51B table becomes resident. The desired outcome is:

> **most table capacity stays on SSD while most actual accesses hit RAM/page cache.**

Those are compatible because phrase frequencies are strongly non-uniform.

## Measurements required when weights land

First inspect:

- exact model parameter count;
- exact active-parameter count;
- names/shapes/dtypes of N-gram tensors;
- N-gram orders;
- hash/addressing scheme;
- number of tables / lookup heads;
- rows fetched per token;
- embedding row width;
- layers that consume conditional memory;
- whether tables are separable checkpoint tensors;
- whether runtime quantization of those tables is supported;
- context and multimodal memory overhead.

Then benchmark:

- table representation: FP16/Q8/Q6/Q4 if supported;
- SSD-only backing + 1/2/4/8 GiB hot cache;
- demand misses/token;
- hit rate by tier;
- bytes read/token;
- page-fault / read latency;
- prefetch hit rate;
- prefill throughput and TTFT;
- decode tok/s;
- memory pressure / swapouts;
- SSD write amplification (ideally near-zero because the table is read-only);
- complete coding-agent task time.

## Two-M1-Max implication

If the preview 125B main-body figure is correct, two 64GB M1 Max machines become more attractive than one for quality-preserving target execution:

```text
M1 Max #1         M1 Max #2
    \                /
     \ main backbone/
      TP / PP / custom
           |
  conditional memory
  hot: RAM / UM
  cold: SSD
```

The key point is that the extra conditional-memory capacity should **not automatically be counted as resident model weight** when judging fit.

## Promotion rule

Promote the SSD-tier design only after the released checkpoint proves that Flash-Next really exposes a sparse deterministic N-gram/conditional-memory structure compatible with offload.

Until then:

- Qwen4-preview status: **confirmed**;
- exact 125B + 51B / 6B-active configuration: **preview / unconfirmed**;
- Engram host-memory offload viability: **primary-paper measured**;
- NVMe hierarchy: **primary-paper proposed + TF-Engram separately demonstrated**;
- M1 Max performance: **unknown; benchmark locally**.
