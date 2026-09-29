# Project 51 primary-lane research watch — 2026-09-29 17:50 ET

**Freshness boundary entering this pass:** **2026-09-29 20:40:47 UTC**.  
**User cutoff:** **2026-09-29 21:50:01 UTC**.

## Decision

**Durable STATE + TARGETS update; no existing TG/PP center changes.**

The main planning change is architectural:

> **Primary maximum-context target: Qwen3.8-Flash-Next GSQ-RCO IQ3_XXS (3.00 transformer bpw) at genuine 262,144 context on the RTX 5070 Ti 16 GB + 64 GB host, using a Flash/QSA-aware compressed-streaming KV implementation.**

Do not drop the weights to IQ2_XS merely because stock Strata currently caps IQ3_XXS to 128K on <90-GB hosts.

The first custom KV candidate becomes **TurboQuant-style K6/V4**, with K8/V4 as the implemented control and K4/V4 as the aggressive arm.

## Strict-window findings

### NEW — vLLM preserves prompt-end recurrent checkpoint under sparse retention

Source:
https://github.com/vllm-project/vllm/commit/d882bddbeab6b4a0d5861dfcb171bf61ce2109d6  
Timestamp: **2026-09-29 21:00:16 UTC**.

Sparse Mamba checkpoint retention could treat the final partial prompt block as a transient boundary and evict it when retention_interval=0.

The fix explicitly recognizes the reusable prompt-end checkpoint and keeps it. A follower extending a 240-token prompt resumes from the 224-token checkpoint.

P51 rule:
- intermediate checkpoints may be sparsely retained;
- the **canonical materialized prompt-end frontier must be pinned independently**;
- do not let generic sparse-retention policy evict the exact state required for the next append-only turn.

### NEW — SGLang reuses one DFlash auxiliary-output buffer across decode graph sizes

Source:
https://github.com/sgl-project/sglang/commit/84523d67851171fa20f7c68d3d6dc6cbf20c4423  
Timestamp: **2026-09-29 21:24:51 UTC**.

DFlash target models capture auxiliary hidden states for the draft. Previously different decode CUDA-graph sizes could retain their own packed output buffers.

The new path:
- preallocates one decode-graph-owned auxiliary buffer;
- every graph size aliases its row slice;
- the draft consumes the target hidden state in the same step;
- the next target forward may then overwrite the buffer.

P51 interpretation:
- cycle-scoped target->draft auxiliary state can be **single-owner scratch** when its lifetime is formally bounded;
- do not multiply resident memory by verifier/graph variants unnecessarily;
- useful for long-context multi-agent capacity accounting, no direct target-hardware TG receipt.

### NEW — mlx-serve NAX canary/cache-lifetime hardening

Source:
https://github.com/ddalcu/mlx-serve/commit/ff7f359bd024687fe93640bac7ae16832a237640  
Timestamp: **2026-09-29 20:55:24 UTC**.

Two P51-relevant fixes:
1. per-shape Metal kernel configs were cached even though output shapes contain row count, so unique prompt sizes could grow the cache indefinitely;
2. a parity canary could consume an error latch raised by an earlier operation in the same forward.

Now:
- configs are constructed/freed per call where shape-dependent;
- canaries remember whether an error was already pending and drop only a latch they themselves raised.

P51 rule:
- correctness canaries must not hide unrelated forward failures;
- runtime shape caches need explicit bounded lifetime/admission rather than silently growing with prompt diversity.

### Low priority / no target effect

- llama.cpp GGUF overflow/bounds fixes in-window are general parser safety.
- vLLM sampler-warmup and frontend tool-grammar fixes do not affect the current P51 physical target.
- no Strata engine commit landed inside the strict window.

## RECOVERED CURRENT — TurboQuant-MLX Flash-Next audit

Repository:
https://github.com/manjunathshiva/turboquant-mlx

This is older than the strict window, but the previous P51 passes had not audited its Qwen3.8-Flash-Next KV behavior.

### Critical correction: TurboQuant KV is currently a no-op for Flash-Next

TurboQuant-MLX supports Qwen3.8-Flash-Next **weights**, including a published mixed TQ Flash build, but its generic KV conversion intentionally skips Flash's `_AttnCache`.

Reason:
- `_AttnCache` subclasses MLX `KVCache`;
- it also owns the QSA sparse-indexer cache;
- an earlier generic TurboQuant replacement discarded that extra state;
- decode then silently lost the proper sparse-selection behavior.

The project fixed this by converting only exact base `KVCache` objects and leaving subclasses unchanged.

The README explicitly states:

**`--kv-bits` has no effect on Qwen3.8-Flash-Next.**

P51 consequence:
- there is **no off-the-shelf TurboQuant Flash KV path today**;
- the P51 262K plan requires a Flash-aware cache implementation which compresses ordinary attention K/V while preserving QSA/indexer state exactly.

### TurboQuant supports 6-bit codebooks

The current MLX codebook implementation supports **1 through 8 bits**, computing Lloyd-Max tables for 5-8 bits on first use.

So K6/V4 is mechanically representable.

However the generic bit packer stores:
- floor(32 / bits) values per uint32;
- at 6 bits, that means **5 values / uint32 = 6.4 physical bits/value**, with two unused bits.

With group size 64:
- FP16 scale overhead ~= **0.25 bpv** per K or V lane;
- K6 ~= **6.65 bpv**;
- V4 ~= **4.25 bpv**;
- equal K/V K6/V4 ~= **5.45 effective storage bpv**.

This corrects the earlier idealized 5.0-bpv assumption.

### Revised memory estimate for the 262K target

Strata's own current admission arithmetic:
- IQ3_XXS normal RAM target: **60 GB**;
- expert arena: **42.9 GB**;
- INT8 streamed KV: ~**13.7 KB/token**;
- 262K INT8 KV: ~**3.6 GB**;
- setup effectively wants another ~1 GB of margin.

Simple stock total ~= **64.6 GB**.

First-order compressed-KV estimates, assuming comparable K/V geometry:

| KV candidate | Approx effective storage | Approx 262K host KV | Interpretation |
|---|---:|---:|---|
| Strata INT8 | ~8.25 bpv | **~3.6 GB** | quality baseline |
| TQ K6/V6 | ~6.65 bpv | **~2.9 GB** | likely too little extra margin |
| **TQ K6/V4** | **~5.45 bpv** | **~2.4 GB** | preferred first custom target |
| TQ K4/V4 | ~4.25 bpv | **~1.9 GB** | aggressive quality arm |

These are format-level planning estimates, not measured Flash memory traces.

K6/V4 therefore plausibly recovers roughly **~1.2 GB** versus Strata INT8. That gets the simple arithmetic below 64 GB, but still leaves little OS/runtime margin; P51 should combine it with bounded snapshot/checkpoint buffers, no expanded duplicate KV, and optionally mmap only the cold expert tail.

### Existing TurboQuant evidence argues for conservative precision

Current broader evidence is mixed:

- TurboQuant's original paper reports strong low-bit long-context results.
- Independent 2026 evaluations are more conservative and generally prefer **4-bit no-QJL/norm-corrected** modes over 3-bit at >=128K.
- Some reported 3-bit variants lose **15-25 points** on reasoning/code benchmarks at long context.
- A separate 8-model engineering reproduction finds architecture-specific sweet spots including **K6/V4**, **K6/V3**, and Qwen-family cases needing **K8/V4**.

Therefore:
- K6/V4 is a **research candidate**, not a source-equivalent assumption;
- K8/V4 stays the safer precision control;
- K4/V4 is the capacity stress arm;
- QSA/indexer/recurrent/MTP state stays protected.

### TurboQuant-MLX Flash weight result is not KV evidence

The same project has a Qwen3.8-Flash-Next mixed-weight TQ build around **52.0 GiB** fully resident on a 64-GB Mac and an n-gram offload mode that reduces active memory **52.01 -> 34.13 GiB** while preserving its logits in the reported check.

Useful conclusions:
- Flash has substantial removable/streamable memory outside the core active MoE path;
- aggressive memory engineering can preserve behavior.

Not allowed conclusion:
- this does **not** prove TurboQuant-compressed Flash KV, because Flash KV quantization is explicitly disabled there.

## 262K P51 target contract

The target now means all of the following simultaneously:

- GSQ-RCO IQ3_XXS **3.00 transformer bpw**;
- native **262,144** context;
- RTX 5070 Ti 16 GB;
- 64 GB host RAM;
- full host K/V stored compressed;
- no persistent full-fp16/fp32 expanded duplicate;
- initial ~32K resident GPU KV window;
- QSA/indexer state including spare/dead-row identity exact;
- GDN/recurrent state exact;
- MTP/draft state exact;
- checkpoint/root/frontier identity exact;
- long-context cache remains append-resumable.

Preferred experimental order:
1. INT8 @128K source-quality control;
2. K8/V4 control;
3. **K6/V4 custom Flash-aware path**;
4. K4/V4 capacity stress;
5. only then lower precision.

Planning priors:
- physical fit conditional on a correct implementation: **~75-80%**;
- K6/V4 source-like long-horizon quality: **~60-70%** prior;
- production readiness today: lower, because the required Flash/QSA compressed-streaming path does not yet exist.

## Strict-window negative scan

From **2026-09-29 20:40:47 -> 21:50:01 UTC**:

- **Strata:** no new engine commit; new Swift setup issues are packaging/startup bugs, not physical target evidence.
- **TensorFold:** no new commit after 0.4.0.
- **oMLX:** no strict-window commit.
- **Ishizuki:** no commit.
- **MoEspresso:** no commit/public M1-Max ~27-TG fork.
- **DASLab:** no new official source-paired Flash IQ3_S 128K/262K semantic-quality result found.
- **Exact user's 5070 Ti:** no 262K IQ3_XXS physical run yet.
- **TurboQuant-MLX:** no strict-window commit; findings above are RECOVERED CURRENT.

## Durable target changes

### Added

**IQ3_XXS 3.00 bpw + genuine 262K + compressed Flash-aware KV** becomes the preferred maximum-context target on the user's 5070 Ti / 64-GB host.

### No numeric TG/PP change

Existing speed centers stay:
- Strata IQ3_XXS 128K: **78 TG / ~85%**;
- IQ3_XXS PP: **1,650 / 1,550 / 1,500** at 32K / 64K / 128K;
- IQ3_S PP: **1,550 / 1,550 / 1,350**;
- dual-M1 Flash: **40 TG @ genuine ~128K / 400 PP / ~70% >=40 TG**.

No 262K IQ3_XXS TG/PP center is assigned until a physical run exists.

## New hard boundary

**2026-09-29 21:50:01 UTC**
