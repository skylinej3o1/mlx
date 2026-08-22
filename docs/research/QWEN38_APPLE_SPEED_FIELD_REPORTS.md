# Qwen3.8-27B Apple Silicon speed field reports — 2026-08-22

Status: **FIELD EVIDENCE / supports Q8 + speculation + heterogeneous-prefill branches**

Primary user-supplied thread:

- https://www.reddit.com/r/LocalLLM/comments/1vv2tw5/people_running_qwen_38_27b_on_apple_silicon_whats/

Purpose: preserve fresh Apple Silicon Qwen3.8-27B performance observations while keeping them clearly separate from MXFORGE-certified measurements. The thread mixes machines, runtimes, quants, contexts, background load, and speculative methods, so it is useful as a hypothesis generator rather than a benchmark table.

## High-value observations

### M2 Ultra 64GB — Q8 unexpectedly faster than Q4

A poster reports using Unsloth Studio with `unsloth/Qwen3.8-27B-UD-Q8_K_XL.gguf` on an M2 Ultra 64GB Mac Studio and obtaining:

- Q8_K_XL: **34.9 tok/s**
- a lighter Q4 rerun: **27.1 tok/s**

The poster explicitly notes this was not an optimized MLX setup and that normal desktop workloads were running in the background.

Do not interpret this as proof that Q8 is universally faster than Q4. It is nevertheless highly relevant to the existing MXFORGE Q8-detour hypothesis: byte-aligned / execution-friendly quant formats can outperform smaller quants when dequantization, packing, verifier shape, or runtime kernels dominate enough of the decode path.

MXFORGE action: keep Q8 as an execution substrate to certify, not merely a quality control. Any local comparison must hold runtime, context, MTP/speculation, sampling, prompt, and background load constant.

### M5 Max 128GB — Q8_0 + MTP long-context stability

A thread participant reports llama.cpp + MTP + Q8_0 on an M5 Max 128GB at approximately **28–30 tok/s** from roughly **10K through 262,144 context**, with occasional short-context peaks near 40 tok/s.

This is field evidence, not a controlled benchmark, but the shape matters: Q8-class decode can remain practically strong at very long context when the runtime/speculative path is favorable. This strengthens the requirement that MXFORGE certify 30K/64K/100K+ rather than infer real-agent performance from tiny tuner prompts.

### M3 Ultra 60c / 96GB — oQ5e + Lightning MTP + ANE prefill

A participant posts oMLX results for `Qwen3.8-27B-oQ5e-mtp` with Lightning MTP, Qwen ANE prompt processing, and speculative prefill using `Qwen3.5-0.8B-MLX-4bit`:

- pp1024/tg128: **310.1 pp tok/s**, **43.7 tg tok/s**, TTFT 3.302 s, peak 27.70 GB
- pp4096/tg128: **369.3 pp tok/s**, **42.7 tg tok/s**, TTFT 11.09 s, peak 28.94 GB
- continuous batching 4x: aggregate **110.0 tg tok/s**

This is newer/faster hardware than the M1 target and must not be transferred numerically. Architecturally it reinforces that prompt processing and decode are separate optimization planes and that ANE-assisted prefill can coexist with Lightning MTP.

### M4 Pro 48GB — DFlash2 field point

A poster reports **24 tok/s** on M4 Pro 48GB with 4-bit MLX + oMLX + DFlash2.

This aligns with prior mlx-dspark/DFlash2 evidence but does not by itself establish a new performance frontier because prompt, context, draft settings, acceptance, and model build are unspecified.

### M1 Pro — ordinary baseline

A participant reports roughly **10–14 tok/s** on M1 Pro, with a transient 17 tok/s peak. Useful only as a broad sanity check; hardware is below the MXFORGE M1 Max target.

## What this thread changes for MXFORGE

It does **not** change the current Qwen branch order, but it increases confidence in three existing hypotheses:

1. **Q8 deserves a real execution-oriented branch.** Smaller bpw is not guaranteed to be faster once quant/dequant and speculative-verification kernels enter the picture.
2. **Speculation and quantization must be co-designed.** The winning quant can change when MTP/DFlash2 is enabled.
3. **Long-context certification is mandatory.** A useful agent model should be judged at ~30K and beyond, not only at 1K/4K.

The thread also reinforces the existing two-plane optimization strategy:

- decode: quant layout + MTP/DFlash2/DSpark + verifier kernels;
- prefill: ANE/GPU/CPU heterogeneous execution + prefix-cache reuse.

## Reproduction rule

When MXFORGE compares Q6/Q8/Q4 locally, use paired identical prompts and log:

- exact model/quant and effective bpw
- runtime commit/build
- context length and KV precision
- MTP/speculation method and depth
- acceptance / committed tokens per verify
- target-only and effective speculative tok/s
- verifier latency
- PP tok/s and TTFT
- steady/peak memory
- thermals / background load

Do not promote any Reddit number to a project result until reproduced on the M1 Max target hardware.
