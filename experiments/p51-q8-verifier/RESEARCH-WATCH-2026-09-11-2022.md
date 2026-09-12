# External runtime research delta — 2026-09-11 20:22 ET

## Scope and freshness

This pass continues the active research lanes only:

- Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4;
- Qwen3.8-27B — one M1 Max 64 GB;
- Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM;
- DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4;
- portable Blazer / ~5.x-BPW kernel and runtime mechanisms.

The previous hard source-freshness boundary was `2026-09-11 22:31:55 UTC`. This pass screens substantive source activity after that boundary through `2026-09-12 00:22:42 UTC`.

Stronger Apple hardware remains **TRANSFER / MECHANISM only** unless it directly reproduces an active M1 topology. No future-M5 purchase lane is reopened.

---

# Executive result

**No canonical TG or cold-PP target moves. No P69 state moves.**

The strongest fresh evidence is about long-context QSA workspace lifetime and speculative-draft state correctness, not about exact target-topology speed:

1. QSA prefill storage must be bounded by a reusable workspace, not merely by a per-allocation byte cap; allocator-retained growth can dominate long-context memory even when each individual allocation is under budget.
2. DFlash/DSpark stacked per-layer normalization must preserve the layer axis; silently reusing one layer's scale can collapse both draft acceptance and task quality.
3. Long-context RoPE configuration is execution state, not metadata: main attention, QSA/indexer and MTP must share the same installed positional transform, and an incompatible fused/SpecPrefill route must fail closed or fall back explicitly.

---

# 1. vLLM #56500 / #56457 — bounded reusable QSA prefill workspace

## Classification

**FRESH UPDATE / TRANSFER / MECHANISM / directly relevant to Flash long-context memory stability.**

PR `vllm-project/vllm#56500` was substantively updated after the prior boundary. It addresses issue `#56457`, where Qwen4Exp QSA prefill allocated a logits tensor whose width grew with context length. A nominal per-allocation cap did not bound *retained allocator memory* because every chunk requested a new, slightly larger shape.

The original physical report is especially useful:

- model: Qwen3.8-Flash-Next-NVFP4 / Qwen4Exp;
- 2x DGX Spark GB10, unified memory, TP2;
- 254K-token cold prefill;
- failure at exactly 166,400 computed tokens;
- approximately 9-14 GB/rank disappeared outside the KV pool before the failure;
- the monotonic allocation series predicts about 14 GB/rank of retained blocks at that point;
- reducing the per-buffer limit to 64 MiB made the request shape saturate early and memory remain flat through the 254K prompt and eight concurrent 254K prompts.

`#56500` changes the storage policy rather than the QSA math: reserve a bounded logits workspace once, keep top-k scratch disjoint, and use compact views for each chunk. In its allocation probe:

| measurement | base | bounded workspace |
|---|---:|---:|
| reserved memory, first -> last step | 34 -> 1,370 MiB | 536 -> 536 MiB |
| extra device allocations after first step | 15 | 0 |
| peak live tensor memory | 171.90 MiB | 528.65 MiB |

The larger fixed live reservation is intentional; the win is eliminating context-shape-driven allocator growth. Real-kernel timings were effectively unchanged across the reported shapes, so this is primarily a storage-lifetime/correctness result rather than a kernel-speed claim.

## Promotion for our Flash-Next work

Add these as explicit long-context admission and benchmark dimensions:

- **logical workspace budget**;
- **live tensor bytes**;
- **allocator-reserved/retained bytes**;
- **number of new allocations after warm-up**;
- **workspace lane / ubatch ownership**;
- **scratch overlap proof**;
- first chunk, first new context bucket, long-context steady state and peak retained memory.

A per-operation `max_bytes` control is not sufficient if the allocator keeps a monotonic sequence of differently sized blocks. Prefer stable bounded storage with views or a deliberately coarse finite bucket set.

For our ~128K objective, this is a direct design warning even though the measured failure happened later and on different hardware. It does **not** justify changing the 400 tok/s cold-PP target.

---

# 2. vLLM #56431 — DFlash per-layer K-normalization axis

## Classification

**FRESH SUBSTANTIVE UPDATE / SPECULATIVE-CORRECTNESS TRANSFER.**

The DFlash path stacks per-layer K-normalization weights. The affected XPU kernel treated the 2-D weight `[num_layers, head_dim]` as a 1-D vector, so every draft layer used layer 0's normalization row.

The failure was not subtle in validation:

- before: GSM8K 0.487, acceptance rate 0.011, acceptance length 1.080;
- after per-layer normalization: GSM8K 0.859, acceptance rate 0.459, acceptance length 4.215.

The PR also exercises a Qwen3.8-27B + DFlash2 serving cell, but those absolute XPU/GPU rates are not portable to our targets.

## Promotion

For DFlash/DSpark/MTP and any fused stacked draft operation, execution identity must include:

- layer axis and layer-to-parameter-row mapping;
- normalization weight source, dtype and shape;
- target vs drafter ownership of the state;
- acceptance length/rate and task-quality checks in addition to shape/output smoke tests.

A tensor having the right total size is not sufficient evidence that a batched/fused kernel preserved the semantic axis. This reinforces the standing rule that speculative correctness needs its own acceptance/quality qualification.

---

# 3. oMLX #3594 — Qwen3.8-Flash-Next YaRN execution consistency

## Classification

**FRESH / STRONGER-APPLE TRANSFER / LONG-CONTEXT CORRECTNESS.**

`jundot/omlx#3594` reports that the pinned mlx-vlm Qwen4Exp MRoPE path ignored `text_config.rope_parameters`, making Qwen's static YaRN extension recipe a silent no-op if a server simply lifted the context gate beyond the native 262,144-token horizon.

The patch installs the YaRN frequency table and attention scaling into the shared attention rotary object. That matters because the QSA indexer shares that rotary instance and the Qwen4Exp MTP path constructs through the same attention class. It also explicitly falls back from the fused Metal MRoPE path when the configured scaling cannot be represented by that kernel, and records SpecPrefill as incompatible with scaled Qwen4Exp RoPE in its current form.

The author field-validated coherent generation through 350K tokens on an M5 Max 128 GB with an oQ4e checkpoint and PLE on SSD. This is not an M1 target receipt and is outside our current ~128K objective.

## Promotion

Treat positional scaling as route provenance:

`configured -> installed -> shared by attention/QSA/MTP -> fused/eager route capable -> executed`.

For any future >262K experiment, reject a mixed positional regime where target attention, sparse index selection and the drafter see different RoPE frequencies/scales. A context-limit flag by itself is not proof that extension is active.

No current target moves because ~128K remains inside the native horizon.

---

# 4. Screened fresh activity

- vLLM merged `9d88ceb02694c6e3df182ec3c87201284f50e2c6` for BF16 KDA checkpoint state. This reinforces state-dtype provenance but adds no new active-lane target evidence.
- llama.cpp `82d6bb284d1ff1c6ef37f29a4c3b63d1a8b11806` is server subprocess refactoring and is not material to the active inference lanes.
- Updated DeepSeek-V4.1 PP/SP/state-relay PRs contain useful later-architecture GPU mechanics, but their current speed tables are code/configuration mixtures or measurements from frozen pre-rebase sources. They reinforce existing ownership/relay rules and are not DS4-0731 receipts.
- Rediscovered M1-Max Qwen3.8-27B community benchmarks from earlier in the week are not fresh merely because they surfaced in this pass.

No fresh exact receipt was found for:

- 2x M1 Max64/TB4 Flash-Next;
- one M1 Max64 Qwen3.8-27B;
- RTX5070Ti16 fully-resident canonical Qwen3.8-27B lane;
- 2x M1 Max64/TB4 DS4-0731.

---

# Active-lane consequences

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Add to the existing certification matrix:

- bounded QSA workspace with allocator-reserved vs live-memory telemetry;
- no monotonic context-shape allocation ladder after workspace warm-up;
- disjoint top-k scratch / per-ubatch workspace ownership;
- per-layer draft normalization provenance;
- acceptance + task-quality checks for every speculative fused route;
- positional-transform provenance if context testing ever crosses 262,144 tokens.

The headline target remains **40 TG sustained at ~128K active context / 400 cold PP**.

## Qwen3.8-27B M1 / RTX5070Ti

No target movement. DFlash2 evidence adds a correctness test requirement only: stacked draft-layer normalization must retain the layer axis and be checked through acceptance and task quality.

## DS4-0731 dual M1

No target movement. Later V4.1 PP/state-sharing work remains mechanism transfer only.

## Blazer / ~5.x BPW

Add workspace-lifetime identity to the existing execution identity: storage precision and kernel geometry are not enough if request-shape variation causes allocator growth. Benchmark reserved bytes, live bytes, allocation count and warm reuse alongside TG/PP/task wall-clock.

## P69

No change. **P69B12 remains frozen/promoted. P69B13 remains next only from the existing measured high-leverage GDN/projection/downstream-tail profile. Do not reopen P69B8/B9/B10-C.**

---

# Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s** |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** |

---

# Next freshness boundary

**`2026-09-12 00:22:42 UTC`**

Future complete searches should start strictly after this timestamp. Preserve source timestamps; do not promote rediscovery time into evidence freshness.