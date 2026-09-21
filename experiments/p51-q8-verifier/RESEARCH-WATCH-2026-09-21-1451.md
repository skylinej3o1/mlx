# Project 51 research watch — 2026-09-21 14:51 ET

**Freshness boundary checked:** previous hard boundary **2026-09-21 17:23:50 UTC**. Search ran through the user's cutoff **2026-09-21 18:51:47 UTC**.

## Decision

**No numeric TG/PP, quality-floor, or confidence change.**

This pass finally surfaced a **materially cluster-relevant recovered analogue**: a production-verified 2-node Qwen3.8-Flash-Next deployment that sustains ~41-42 tok/s single-stream at the model's native 262K context with speculative decoding. It is not Apple/TB4 evidence, so it does not justify changing Project 51's probabilities, but it is stronger support for the two-node/full-context/40-TG systems thesis than the single-node Apple or multi-GPU receipts alone.

Two additional recovered items sharpen the cluster design: exact-family recurrent-state retention under agentic prefix reuse, and a node-local pipeline-placement pattern that deliberately moves only pipeline activations across node boundaries.

## RECOVERED — 2x DGX Spark full Flash-Next at native 262K

Source: https://huggingface.co/pocharlies/Qwen3.8-Flash-Next
Recipe date: **2026-08-27**. This is **recovered older evidence**, not an exact-window measurement.

Deployment:
- `RadixArk/Qwen3.8-Flash-Next-NVFP4`;
- full 125B MoE / ~6B active + 51B n-gram PLE + MTP;
- **2x NVIDIA DGX Spark (GB10), 128 GB each**;
- **TP=2**;
- direct **200G RoCEv2** DAC between nodes;
- SGLang;
- native **262,144-token** context;
- NEXTN MTP, 3 speculative steps; reported sustained accept length ~2.3.

30-minute soak:

| metric | reported value |
|---|---:|
| single-stream decode | **~41-42 tok/s** |
| 8-stream aggregate | **153 tok/s avg** (139-166) |
| speculative accept length | **~2.3** sustained |
| context | **262,144** |

The recipe also reports a cold 72K single-prompt prefill around ~2.5K tok/s and large prefix-friendly concurrent prefill rates in the several-thousand-tok/s range.

### Why this matters to P51

This is a direct physical proof that the exact Flash-Next family, including native MTP and full 256K context, can live across **two separate machines** and sustain the neighborhood of our **40-TG headline**.

It removes one uncertainty: distributed full-model Flash-Next does not inherently collapse below 40 merely because the model is split across machines.

### Why it does NOT transfer numerically

- Fabric is **200G RoCEv2**, far faster than TB4.
- It uses **TP=2**, while P51 deliberately wants **PP2** so only stage activations cross TB4.
- GB10/SGLang/NVFP4 CUDA kernels and Apple7/Metal/MLX have very different execution characteristics.
- Their resident per-rank model geometry and PLE handling differ from P51's mixed-precision PP2 design.

Therefore the receipt strengthens the **architecture plausibility**, not the numerical forecast. Keep 40@128K confidence unchanged pending exact M1/TB4 PP2 measurements.

## RECOVERED — vLLM #57253 exact Flash recurrent-state retention

Source: https://github.com/vllm-project/vllm/pull/57253
Created 2026-09-16; active again in this window, but measurements predate the boundary.

Workload:
- `Qwen3.8-Flash-Next-FP8`;
- 4xB200 / TP4;
- 256K AgentX replay workload;
- concurrency 128, 900 s;
- equal KV capacity across all arms.

At equal KV capacity:

| metric | current main | retirement skipped | boundary-protect fix |
|---|---:|---:|---:|
| steady-state prefix hit | 49.81% | 75.24% | **77.48%** |
| request throughput | 1.16/s | 1.82/s | **1.89/s** |
| input throughput | 92,834/s | 137,924/s | **143,366/s** |
| mean TTFT | 2,986 ms | 1,384 ms | **1,335 ms** |
| mean ITL | 63.51 ms | 38.98 ms | **36.32 ms** |

Root cause: state retirement treated an old recurrent checkpoint as irrelevant once the *current request* had advanced past it, even though a *future request* sharing the prefix needed exactly that registered boundary to resume. Under pressure the pool reclaimed it, forcing long prefix recomputation.

### P51 rule

State lifecycle has at least two notions of liveness:
- needed by the active request's next forward;
- needed by a future cache consumer.

A recurrent/QSA/MTP checkpoint that is cache-published remains live under the second notion even after it is dead under the first. Cluster sleep/rewind/agent sessions must not recycle such state merely because the producer has decoded beyond it.

## RECOVERED — vLLM #51548 node-local pipeline placement

Source: https://github.com/vllm-project/vllm/pull/51548

The proposed layout lets **pipeline parallelism define the node boundary**: pipeline stages are placed node-locally and only PP activations cross nodes, while DP/EP communication stays within a node. It explicitly supports DP=1 as well as MoE deployments.

This is very close to P51's rationale for **PP2 across the two M1s instead of cross-node TP**. There are no benchmark results in the PR, so it is design corroboration only.

## Exact-window findings

- `antirez/ds4`: no new commit, but PR #1070 (older body, active in-window) adds Qwen3.8-Flash-Next on Strix Halo with resident Q2/Q4, disk PLE and built-in MTP. Q4 MTP-off is ~19.7-19.9 TG through 32K and prefill ~405-466 TG depending history. Useful cross-platform support, not cluster evidence.
- `vllm-project/vllm`: only one merged commit in-window (`#57937`, redundant PLE offload env removal). Several old PRs were active; #57253 and #51548 are the cluster-relevant recovered items above. A new async NIXL-pull PR #57987 explicitly has **no end-to-end or performance acceptance yet**, so it is not evidence.
- `jundot/omlx`: no commits. #3793 received more canonical-recovery work but its core evidence was already captured before this boundary. No new cluster TG receipt.
- `ggml-org/llama.cpp`: one Metal mask-bounds fix; no new Flash performance receipt. The wide-query FA PR #28439 remains M5-only tuning and does not affect token generation in its own end-to-end tests.
- `incoai/splash`: merged previously reviewed Apple9 batch/prefill PRs; their measurements predate this boundary and remain single-node M3/M5 evidence.
- `ddalcu/mlx-serve`: no runtime commit; one Codex tool-history fix was active at the cutoff.
- Kadir, MTPLX, APEX, ik_llama and AutoRound: no qualifying commit in-window.
- Targeted web/Hugging Face/Reddit search found **no new 2x M1 Max/TB4 Flash-Next receipt** after the hard boundary.

## Other recovered caution — Qwen3.8-27B TurboQuant KV + MTP

vLLM #52475 reports an older RTX5090 reproduction where Qwen3.8-27B with MTP K3 is clean with FP8 KV but silently repetition-collapses on ~8K prompts with TurboQuant 3/4-bit KV; TurboQuant without MTP is clean. This reinforces P51's existing rule that KV precision and speculative acceptance/correctness are a joint identity. It adds no Flash-cluster target change.

## Target / confidence impact

Unchanged:
- Flash production quality floor: **>=38 AA-class**, preferred 39-40.
- Flash headline: **40 TG @ ~128K active context**.
- Flash cold PP: **400**.
- Current 40-TG confidence ladder unchanged.
- Single-M1 27B target: **25 TG**.
- 5070 Ti and DS4 targets unchanged.

Cluster interpretation after this pass:

> We now have a direct **two-machine exact-family receipt above 40 tok/s at native 262K**, but on TP2/200G/GB10. It strengthens the distributed Flash thesis while leaving the decisive question exactly where it was: can PP2 + Apple7 kernels + MTP keep both M1 stages occupied enough over TB4?

## New hard boundary

**2026-09-21 18:51:47 UTC**
