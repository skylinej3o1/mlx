# Qwen3.8-Flash-Next late day-one rerun

Status: **fresh field evidence / delta from earlier Aug 26 sweep**

Updated: 2026-08-27 ~01:00 ET.

## What changed since the earlier sweep

1. **Still no credible direct M1 Max Flash-Next benchmark found.** Searches across Reddit, Hugging Face and oMLX benchmark pages surfaced M3/M5/Strix/NVIDIA results, but no clean M1 Max result. Keep all 2x M1 Max throughput figures forecast-only.
2. **Apple native MTP evidence strengthened.** Vontra's uniform 6-bit MTP checkpoint now publishes a controlled 3x512-token oMLX test on an Apple M3 Studio: 20.6495 tok/s median without MTP vs 25.935 tok/s with 3 draft tokens, +25.6%, 73.55% acceptance, exact greedy-output parity.
3. **The SSD-PLE project now has audited Q5/Q6 main GGUF artifacts uploaded.** The published MQ-Q6 resident compute backbone is 97,660,877,400 bytes / 90.9538 GiB and uses a heterogeneous Q5/Q6/Q8/BF16/F32 recipe while keeping the 51.2B PLE as a BF16 SSD sidecar.
4. **An independent Unsloth user hit the exact GGUF layout issue expected for SSD PLE on Metal.** Their Q4_K_XL n-gram tensor was interleaved with Metal-allocated tensors, causing mmap to wire it into GPU memory; rearranging the quant internals allowed SSD offload. This strengthens the requirement that MXFORGE package PLE as an explicit sidecar rather than rely on conventional monolithic GGUF/MLX sharding.
5. **Q5 remains the most attractive serious target.** InferencerLabs' early fidelity ladder still shows a substantial jump from Q4.5 token agreement (91.65%) to Q5.5 (95.05%), then diminishing gains to Q6.5 (96.65%). Baekpica's architecture-aware recipe independently uses Q5_K for most routed expert gate/up tensors, Q6_K for edge/down-sensitive paths, and Q8_0 for MTP/always-active paths.
6. **Community runtime anecdotes remain strong but not certification-grade.** A 3090 + 128GB DDR5 user reports roughly 20 tok/s with Unsloth UD-Q4_K_XL using CPU MoE offload and llama.cpp PR #27742. This is useful evidence that the architecture remains practical on heterogeneous memory, not an Apple performance anchor.

## Key new sources

- Vontra 6-bit MTP MLX: https://huggingface.co/Vontra/Qwen3.8-Flash-Next-MLX-6bit-MTP
- Vontra oQ6 MTP MLX: https://huggingface.co/Vontra/Qwen3.8-Flash-Next-MLX-oQ6-MTP
- Baekpica SSD-PLE mixed quant: https://huggingface.co/Baekpica/Qwen3.8-Flash-Next-Mixed-Quant-SSD-PLE-GGUF
- Baekpica Q5/Q6 artifact commit: https://huggingface.co/Baekpica/Qwen3.8-Flash-Next-Mixed-Quant-SSD-PLE-GGUF/commit/d645b1199072fcef81c2a908a301455d12ca4fb3
- Unsloth SSD-layout report: https://www.reddit.com/r/unsloth/comments/1vz8zo6/unsloth_qwen38nextflash_quant_layout_issue_for/
- 3090 field run: https://www.reddit.com/r/Qwen_AI/comments/1vzfarq/%C3%A9poustouflant_qwen38flashnext_rtx_3090_128_ddr5/

## Current MXFORGE recommendation

Do not adopt a monolithic community quant as the final 2x M1 Max format.

Target:

```text
2x M1 Max 64GB

resident/distributed compute:
  bulk routed experts         Q5-class
  sensitive expert/down      Q6 where measured useful
  MTP / always-active        Q8 initially
  routers/GDN/QSA/HC/control protected as needed

external memory:
  PLE sidecar                BF16 first for exactness ruler
  PLE production             Q8 SSD after quality certification
  explicit bounded UM/page cache
```

The late-day-one evidence increases confidence in the architecture, not yet the exact M1 throughput number. The dominant unknowns remain 2-node synchronization efficiency and SSD PLE latency hiding on Apple Silicon.
