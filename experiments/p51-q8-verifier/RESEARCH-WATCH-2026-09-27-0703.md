# Project 51 primary-lane research watch — 2026-09-27 07:03 ET

**Strict freshness boundary:** prior hard boundary **2026-09-27 10:23:44 UTC**. Strict-window scan runs through **2026-09-27 11:03:54 UTC**. No qualifying primary-lane commit landed in that interval; one SGLang diffusion change was unrelated.

This watch also intentionally consolidates **RECOVERED CURRENT / SECONDARY-LANE** evidence from Strata, ISTA-DASLab and TensorFold that became materially relevant in the immediately preceding discussion.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- central TG region **~39-41**, mature downside **~30-32**, target-only fallback **~24-27**
- single-M1 27B: **25 TG canonical target**
- RTX 5070 Ti dense-27B: **120 TG mature target / 250 cold PP baseline target**
- Flash production quant search **3.0-3.6 BPW**, source-like xhigh region still a hypothesis pending AA certification.

## RECOVERED CURRENT — Strata is a serious complete Flash-Next runtime on commodity NVIDIA

Sources:
- https://github.com/Niko1221/Strata
- https://github.com/Niko1221/Strata/blob/main/docs/DETAILS.md
- https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/

Measured setup: **RTX 5070 12 GB / Ryzen 5 7600 / 64 GB DDR5 / Windows**, one code-agent prompt per length, 256 generated tokens, MTP enabled.

At **128K context**:

| quant | TG | PP |
|---|---:|---:|
| Q2_0 | **65.1** | **543** |
| IQ2_XS | **52.0** | **472** |
| IQ3_XXS | **44.8** | **414** |
| IQ3_S | **42.2** | **378** |

Short-context output is ~95 / 78 / 66 / 54 TG respectively.

Architecture:
- GPU: attention + DeltaNet mixers + hyper/gated-residual work + routers/shared experts + output head + MTP + hot routed-expert cache.
- RAM: all **24,576 routed experts**; CPU computes misses concurrently with GPU-resident experts.
- SSD: **28.8-GB n-gram/PLE table**, sparsely read.
- speculation: native MTP up to depth 3, typically **2.4-3.2 committed tokens/pass**.
- prompt lookup: up to 5-token drafts only when measured acceptance/cost says it pays.

### KV streaming is a MoE residency lever

At >=64K Strata moves the colder portion of KV to system RAM and keeps the attention-hot portion in VRAM. Q2_0 at 262K moves **50.9 -> 62.6 TG** while GPU-resident experts rise **1,589 -> 3,872**.

Interpretation: on a VRAM-starved MoE system, retaining every KV byte on GPU can be slower than moving cold KV to RAM if the reclaimed VRAM holds materially more hot experts.

### Prompt-copy / agent editing

Strata's current prompt lookup is reported **6-11% faster on code edits**, with other text unchanged. The controller gates lookup on its measured speculative surplus.

**P51 rule:** copy/lookup drafting should be opportunistic and measured, not a permanent decoder mode. Report novel-generation TG separately from edit-effective throughput.

### Q4 KV is not our AA-quality default

Strata's optional Hadamard-rotated Q4_0 KV:
- halves KV memory;
- about **+4% TG at 128K**;
- but long-document perplexity worsens **8-12%**; needle tests still pass.

For AA~40 work, leave this as a throughput arm. Higher-precision KV remains the default until our long-context reasoning/tool/agent suite certifies otherwise.

## RECOVERED CURRENT — ISTA-DASLab quant quality

Sources:
- https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF
- https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF

### Flash-Next IQ3_XXS

Official GSQ-RCO **3.00 transformer BPW** results:
- task average **92.57 vs BF16 93.12 = 99.4%**
- AIME25 **100.00 vs 100.00**
- GPQA-D **91.41 vs 91.92**
- LiveCodeBench v6 **86.29 vs 87.43**.

This is good enough to promote **3.0 BPW Flash IQ3_XXS to an AA~40 candidate arm**, but not to certify it.

Why not certified: a current Hugging Face community test reports meaningful qualitative degradation in some real workflow / voxel-modeling tasks for the official Flash IQ3_XXS. DASLab replied that the result was unexpected and needs investigation. This is exactly why P51's AA bar requires source-vs-quant xhigh reasoning/coding/tool/long-context/semantic-continuity testing, not only aggregate benchmark parity.

### Dense 27B IQ3_S

DASLab's **3.50-BPW IQ3_S / 11.8 GB** is the cleaner quality reference:
- AIME25 **100.00 = BF16**
- LiveCodeBench v6 **85.71 = BF16**
- GPQA-D **89.39 vs 89.90**
- task average **91.70 vs 91.87 = 99.8%**.

DASLab describes this arm as **task-lossless**. This strongly supports keeping the P51 27B source-like-quality center around **~3.4-3.6 BPW**.

## 5070 Ti practical Flash lane

The measured Strata card is a **5070 12 GB**, weaker and smaller than the user's **5070 Ti 16 GB**. More VRAM matters because Strata uses it as expert-cache capacity; its own cross-GPU estimates are explicitly **±20%**.

Therefore:
- promote **5070 Ti + Strata + DASLab IQ3_S/IQ3_XXS** to a first-class experimental serving lane;
- do **not** replace measured 5070 numbers with projected 5070-Ti numbers in canonical evidence;
- certify AA~40 first, then benchmark exact 4K/32K/64K/128K TG+PP, VRAM expert count, CPU miss share and RAM headroom on the real rig.

If IQ3_S or IQ3_XXS clears AA~40 on the user's suite, the 5070 Ti may be a better practical Flash-Next server than the proposed CUDA-prefill -> M1-decode composition; the heterogeneous lane remains valuable for dense 27B and as a systems experiment.

## RECOVERED CURRENT — TensorFold / DFlash2 Apple-Silicon direction

Sources:
- https://tensorfold.dev/
- https://github.com/z-lab/dflash

TensorFold currently reports **Qwen3.8-27B 120-124 TG on M5 Max 128 GB with DFlash2**, versus **27 TG without drafts** in the stated workload.

Classification: **stronger-generation Apple evidence only**. No planning-grade M1 Max TensorFold receipt was found, so the result gets **zero direct M1 target credit**.

The mechanism is relevant. Official DFlash guidance for **quantized Qwen3.8-27B on MLX** recommends **block size <=5**, because stock MLX quantized matmul loses efficiency at larger verify width. That independently agrees with Ishizuki/Splash/oMLX/P51 findings: optimal S is tensor-shape/GPU/quant-specific, and simply drafting wider is not a free win.

### M1 27B follow-up priorities

Mine/test conceptually:
1. tensor-specific S=2-8 crossover policy;
2. custom Apple7 few-row quantized verify;
3. DFlash2 / native-MTP mechanism selection by measured surplus;
4. prompt-copy for edit-heavy agent output;
5. recurrent-only partial-accept rollback;
6. whole-chunk GDN prefill;
7. host-read overlap.

## Strict-window scan

No qualifying Project-51 performance/correctness change appeared after **10:23:44 UTC** through **11:03:54 UTC** in DS4, vLLM, oMLX, mlx-serve, llama.cpp, Splash, MTPLX, SGLang, Ishizuki or Strata. SGLang had one unrelated diffusion commit.

## Canonical planning effect

**Targets unchanged.** What changes is lane priority:

- **Practical Flash serving:** benchmark the user's 5070 Ti with Strata + DASLab IQ3_S/IQ3_XXS.
- **Flash AA-quality:** IQ3_XXS 3.0 BPW is a candidate, not certified; preserve the 3.3-3.6 source-like planning band until our suite says otherwise.
- **Dense M1 27B research:** DASLab IQ3_S 3.5 BPW becomes a high-quality reference arm; pursue TensorFold/DFlash2-inspired verifier and copy/recurrent-prefill work.
- **Heterogeneous CUDA prefill -> M1 decode:** still valid, but may be unnecessary for practical Flash if Strata on the 5070 Ti clears quality and throughput requirements.

`RESEARCH-STATE.md` is updated with these durable conclusions. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 11:03:54 UTC**
