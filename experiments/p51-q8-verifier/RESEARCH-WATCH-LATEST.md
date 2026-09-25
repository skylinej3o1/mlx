# Project 51 primary-lane research watch — 2026-09-25 06:37 ET

**Freshness boundary checked:** prior hard boundary **2026-09-25 08:33:40 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-25 10:37:58 UTC**.

## Decision

**No canonical TG/PP, xhigh-quality, architecture, or planning-confidence change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

No exact dual-M1/TB4 Flash-Next S=2-8 verifier receipt appeared, no direct Apple7 PP2 overlap measurement appeared, and no new precisely timestamped source-vs-quant xhigh behavioral certification appeared.

Two fresh llama.cpp merges are relevant as enabling infrastructure, but neither is a production-style Project 51 throughput receipt.

## Findings

### NEW — llama.cpp #24364: model-driven activation precision becomes part of FP4 quant identity

Source: https://github.com/ggml-org/llama.cpp/commit/e9f824d8c0f011662a742c9d15d4aa18a41e32c0
Committed **2026-09-25 08:36:35 UTC**.

The merge adds `llama_prec_policy` and per-tensor activation-precision metadata for NVFP4/MXFP4 paths. In particular:
- converted checkpoints can mark individual NVFP4 tensors as unable to use A4 when their source quantization is `W4A16_NVFP4`;
- Blackwell native W4A4 is selected only for FP4 weights that are permitted to consume Q4 activations;
- marked W4A16 tensors route through a higher-precision W4A8-style path instead;
- `GGML_CUDA_MMQ_PREC=q4|q8|auto` provides an explicit override for experiments.

This is primarily **consumer-Blackwell / RTX-5070-Ti-relevant infrastructure**, not Apple evidence. It formalizes a point already important to P51: a nominal weight format such as NVFP4 is not a complete runtime identity when selected layers require higher activation precision.

**Classification:** NEW adjacent 5070-Ti quant/runtime infrastructure.

**P51 consequence:** future NVFP4/MXFP4 receipts must record both weight precision and effective activation policy. Do not compare `NVFP4` results while silently mixing W4A4 and W4A8/W4A16-designated layers. For the phase-disaggregated 27B prefiller lane, preserve checkpoint-provided per-layer precision metadata before testing global `q4` overrides.

There is **no end-to-end Qwen3.8 benchmark in this merge**, so it earns no TG/PP credit for either the 5070-Ti or M1 targets.

### NEW / enabling only — llama.cpp #29095: Metal FWHT now supports widths 1024-8192

Source: https://github.com/ggml-org/llama.cpp/commit/e351231c4f4cdd89c88e696c46d0eb718c9e0ab5
Committed **2026-09-25 09:15:33 UTC**.

The Metal backend previously covered FWHT widths 64-512 with one row per simdgroup. The new threadgroup kernel extends the operation to **1024, 2048, 4096 and 8192** for both F32 and F16 sources:
- 256 threads per threadgroup;
- sub-simdgroup butterflies remain shuffle-based;
- larger intra-threadgroup butterflies use threadgroup memory;
- the widest 8192 path allocates **32 KB** of threadgroup memory;
- device memory-limit checks reject unsupported widths rather than allowing a nil pipeline.

Validation reported on **M5 Pro**:
- `MUL_MAT_HADAMARD`: **26/26**;
- `MUL_MAT`: **1265/1265**.

**Classification:** NEW Apple Metal primitive / transfer evidence, not a Flash-Next benchmark.

**P51 consequence:** this removes an upstream Metal capability gap for wide Hadamard-transform quantization schemes and is worth mining if the heterogeneous-quant search adopts transformed FP4/ternary-style weights. It does **not** imply an M1 speedup: the validation hardware is M5 Pro, there is no Qwen3.8 A/B, and Project 51's production Flash path is MLX/PP2 rather than this llama.cpp kernel.

Do not add this to the 40-TG numerator unless an Apple7 real-model A/B shows that the transform path both engages and improves end-to-end verifier/decode cost.

### LOWER PRIORITY — llama.cpp #29329 splits Metal FA kernels by dtype

Source: https://github.com/ggml-org/llama.cpp/commit/5a75f14c0f0fd643e3629b48b297cb44a7361f94
Committed **2026-09-25 09:11:00 UTC**.

The Metal flash-attention kernel library is split into per-dtype libraries. This is useful code-size/build organization and can reduce unnecessary specialization loading, but this merge provides no Project 51-relevant end-to-end speed receipt.

**Classification:** NEW maintenance/build infrastructure; no planning effect.

### NON-QUALIFYING fresh commits

vLLM had three commits inside the strict window, but they were logging configuration, CI sharding, and a type annotation. None changes Qwen3.8 inference economics or correctness.

## Required-surface / community scan

Strict-window issue/PR/commit screening found no qualifying post-boundary performance or correctness update on:
- **antirez/ds4**
- **jundot/omlx**
- **ddalcu/mlx-serve**
- **incoai/splash**
- **paperniuk/splash**
- **youssofal/MTPLX**
- **localai-org/apex-quant**
- **IST-DASLab/GSQ**.

Public/Hugging Face/Reddit searches surfaced the already-known M1 Splash report, MTPLX 2.12.0 material, ISTA-DASLab NVFP4 prefiller, Flash-Next GSQ-RCO, and recent stronger-Apple oMLX posts. None exposed a substantive timestamp inside **08:33:40-10:37:58 UTC** that would justify promotion as NEW in this delta.

## Canonical planning state after this pass

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target.
- RTX 5070 Ti 27B: **120 TG** mature target.

`RESEARCH-STATE.md` and `RESEARCH-TARGETS.md` require no change from this pass. The activation-precision rule is recorded here but does not yet alter a canonical target or deployed configuration.

## New hard boundary

**2026-09-25 10:37:58 UTC**
