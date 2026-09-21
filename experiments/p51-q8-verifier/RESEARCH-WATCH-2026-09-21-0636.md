# Project 51 external runtime watch — 2026-09-21 06:36 ET

**Hard freshness window:** strictly after **2026-09-20 19:37:24 UTC** through the user's message cutoff **2026-09-21 10:36:04 UTC**.

## Decision

**No numeric TG/PP or quality-floor change.**

- production quality floor remains **>=38 AA-class**, with **39-40 preferred**;
- headline remains **40 TG @ ~128K / 400 genuinely cold PP**;
- no new exact 2x M1 Max 64 GB / TB4 / ~128K / P51 mixed-quant + MTP physical receipt appeared.

This window materially strengthens three design areas:

1. **MTP/verifier runtime:** current oMLX recovered Qwen3.8-Flash-Next oQ4e MTP to 116-117 tok/s on M3 Ultra with ~90-92% acceptance.
2. **Speculative-state correctness:** dummy draft writes can silently poison a prefix cache, and recurrent state must travel with KV across disaggregated/pipeline boundaries.
3. **Quant allocation:** recovered direct Qwen3.8-Flash-Next GSQ/RCO evidence shows a 3.00-bpw transformer allocation retaining 99.4% of BF16 on its AIME/GPQA/LiveCodeBench task average while preserving BF16/F32 sensitive islands.

## NEW — oMLX #3791: recover Qwen Lightning MTP throughput

Source: https://github.com/jundot/omlx/pull/3791  
Created **2026-09-21 08:49:50 UTC**; merged **09:35:11 UTC**.

After an mlx-vlm change, the short-block MoE path materialized strided fused gate/up views during multi-token draft-head history folds, copying about **900 MiB** of expert weights/quant tensors. Target verification also bypassed existing fused gate/up and router top-k paths.

The fix reuses fused gate/up for short-block and verification paths, restores fused router top-k where eligible, and parallelizes independent token rows in the hyper-connection up projection while keeping each row's arithmetic/reduction order.

Qwen3.8-Flash-Next-oQ4e-mtp, **M3 Ultra**, greedy, one request, cache disabled, 1024 generated tokens:

| runtime | TG |
|---|---:|
| dev2 | 108.78 |
| main before fix | 94.34 |
| gate/up + HC | 114.32 |
| + fused router | **116.42-117.13** |

MTP acceptance stayed around **90-92%** without repeated parking.

The fused router changes expert ordering/normalization rounding, so final generated text differs from pre-fusion main, although router-enabled runs were internally repeatable.

### Project 51 consequence

- Verifier/draft short-block execution deserves its own fused-path audit; a target-only kernel win can disappear if verify bypasses it.
- Count materialization/copies in MTP history-fold and verify paths; a hidden ~GB-class copy per cycle can dominate.
- Router fusion is a **quality identity** as well as a speed identity: if arithmetic/order changes, rerun the >=38 behavior suite and MTP acceptance panel rather than demanding bit identity to an unfused path.
- This materially strengthens the **short-context upside case**, but it is M3 Ultra evidence and does not change the 40@128K dual-M1 probability.

## NEW — mlx-serve commit f66634e: KV8 attention can beat BF16 at long context

Source: https://github.com/ddalcu/mlx-serve/commit/f66634e3d266e30e1417c658ff255f2b4060270c  
Commit **2026-09-20 20:21:43 UTC**.

mlx-serve added a head-dim-256 KV8/KV4 attention path using Apple's `matmul2d` tensor op: 32-token pages dequantize into threadgroup memory, online softmax, split-KV partials.

On **Qwen3.8-27B / M4 Max / KV8 / MTP**:

- 16K: **45 -> 55 tok/s**
- 32K: **37 -> 51 tok/s**
- KV8 became faster than BF16 KV at 32K on that tested path.

The same change also fixes multi-request long-context admission that could individually fit each request but collectively overrun Metal memory, adds an OS reserve, narrows long-prefill chunks under contention, and allows decode ticks between chunks.

### Project 51 consequence

This is not Flash-Next/M1 evidence, but it strengthens the existing **Q8 KV is not necessarily a speed sacrifice** hypothesis. Keep Q8 as the quality-first KV baseline and optimize the dequant/attention kernel before lowering KV precision. At B1/B2/B4, admission must bill **aggregate live/reserved state**, not each request in isolation.

## NEW — vLLM #56734: dummy speculative steps can poison cached draft KV

Source: https://github.com/vllm-project/vllm/pull/56734  
Merged **2026-09-21 01:06:25 UTC**.

Idle/padding draft steps could compute slot mappings through stale persistent block-table rows and write drafter K/V into cache blocks belonging to previous requests. Those blocks could already be registered in prefix cache.

Observed failure: per-request MTP acceptance latched to exactly zero until prefix-cache reset; poisoned drafter rows could contain NaNs while target KV remained clean.

The fix marks dummy mappings PAD and guards the mapping kernel so padding rows never dereference stale block tables.

### Project 51 consequence

A sudden MTP-acceptance collapse is not automatically draft-model weakness. The verifier harness must distinguish:

- draft quality loss;
- target/verify numerical mismatch;
- **draft-cache corruption / stale slot ownership**.

Dummy, padding, warmup, cancelled and auxiliary-agent rows must be write-inert for target/draft KV and recurrent/QSA checkpoints unless they own an explicit live slot.

## NEW MERGE — vLLM #51052: recurrent state must travel with attention KV

Source: https://github.com/vllm-project/vllm/pull/51052  
Merged **2026-09-20 21:30:34 UTC**.

vLLM's MoRIIO READ path now transfers packed recurrent conv/SSM state alongside attention KV for hybrid models. Decode otherwise starts from an empty recurrent state even when attention KV was successfully restored.

Notable contract:

- recurrent groups remain distinct rather than flattened;
- conv + SSM reads complete before forward;
- producer exports `h(N-1)`; decoder recomputes the last prompt token to derive `h(N)`;
- unsupported speculative/heterogeneous layouts fail closed.

Real-weight accuracy and long-context AgentX serving were validated on AMD multi-node hardware. Hardware rates do not transfer to P51.

### Project 51 consequence

This reinforces the PP2/warm-session state model: **KV hit alone is insufficient**. A checkpoint identity includes target KV + recurrent/GDN/QSA state and the exact replay boundary. For cross-stage restore, publish the state at a replayable committed boundary and deliberately recompute the landing token if that is the state contract.

## NEW — Splash #88: Apple9 Q4/MoE decode nearly doubles on M3 Max, with an important rejected optimization

Source: https://github.com/incoai/splash/pull/88  
Created **2026-09-21 08:25:14 UTC**.

Splash adds Apple9-specific bfloat simdgroup-matrix Q4 decode and four-SIMD-group MoE tiles. On **M3 Max 40-core**:

- Qwen3.8-27B aggregate short-context decode: **1.930x (+93.0%)**
- 35B: **1.367x (+36.7%)**

Prefill was essentially flat.

A proposed Apple10 split-K default was **withdrawn** because it reproducibly changed speculative acceptance/output on prompt-specific cases. Disabling only split-K restored main outputs/acceptance in all tested device/model/prompt combinations.

### Project 51 consequence

No numeric transfer to M1/Apple7. Mechanism lessons:

- use BF16/FP32-safe operand/accumulation where FP16 range is unsafe;
- tune MoE/Q4 tiles by actual Apple family/core count;
- any split-K/reassociation optimization is admitted only after **MTP acceptance + behavioral quality** checks;
- preserve rollback toggles for arithmetic-changing kernels.

This strongly supports our existing M1 BF16->FP16 experiment being **selective**, not a blanket conversion.

## RECOVERED OLDER DIRECT FLASH QUANT EVIDENCE — ISTA-DASLab GSQ/RCO

Source: https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF

This release predates the strict watch window and is intentionally classified as **RECOVERED OLDER EVIDENCE**.

DASLab has a direct Qwen3.8-Flash-Next GSQ/RCO release, not merely the 27B model. RCO performs budget-constrained per-tensor quant-type allocation after GSQ candidate generation.

### Quality result

Their strongest released transformer allocation is **IQ3_XXS / 3.00 bpw**:

| model | AIME25 | GPQA-D | LiveCodeBench v6 | task avg |
|---|---:|---:|---:|---:|
| BF16 | 100.00 | 91.92 | 87.43 | 93.12 |
| GSQ/RCO 3.00 bpw | **100.00** | **91.41** | **86.29** | **92.57** |

That is **99.4% of BF16 task average**. It is **not an AA score** and therefore does not certify Project 51's >=38 requirement.

The release has no MTP-head result, so it also does not certify speculative acceptance.

### Allocation structure

The public allocation is unusually informative:

- `output.weight`: Q5_K;
- hyperconnection projection/injection tensors: **BF16**;
- HC/SSM/norm/scalar state tensors: commonly **F32/BF16**;
- QSA indexer K projection: **BF16** in shown indexed layers;
- dense/full-attention projections: generally **Q4-Q6 class**;
- routed expert gate/up: frequently **~IQ2-class**;
- expert down is constrained by the 640-row shape and uses Q2_0/IQ4_NL-class compatible formats;
- shared experts are materially higher than most routed expert mass;
- n-gram/PLE table is held separately at **IQ4_NL**, 28.8 GB.

This is remarkably aligned with the P51 thesis: protect the small recurrent/indexer/HC/control path and spend very few bits on the enormous routed-expert mass.

### Project 51 quant-search update

Promote **GSQ/RCO allocation as a first-class sensitivity prior beside APEX**.

The safe production search still starts from MTPLX Optimized / ~4.6-4.9 hot-trunk territory because:

- GGUF IQ2/IQ3 formats do not imply fast M1/MLX kernels;
- 3.00 bpw is not AA-certified;
- DASLab's released Flash build has no MTP-head certification;
- its PLE is IQ4_NL, while separate community evidence suggests aggressive PLE quantization may hurt deep-context MTP.

But add **RCO-inspired ~3.0-4.3 experimental allocation arms** where M1 kernels are actually efficient. The objective is no longer to hand-pick one BPW: solve a constrained allocation problem whose loss includes Project 51 behavior/quality, MTP acceptance, M1 microseconds and hot bytes.

## USER-SUPPLIED CURRENT EVIDENCE — M3 Ultra 113 tok/s mlx-serve

Source: https://www.reddit.com/r/oMLX/comments/1wlhyc6/flashnext_on_a_mac_studio_m3_ultra_256gb_113_toks/

The user surfaced this after the previous watch cutoff. Reddit exposes the publication day but not an exact timestamp, so it is **not classified as strict-window NEW evidence**.

Mac Studio **M3 Ultra 256 GB / 60-core**, mlx-serve 26.9.4, mixed 4/8 pack, MTP, max concurrency 1, greedy:

- think off: **113.1 tok/s** short-context decode;
- xhigh: **69.8-70.4 tok/s**;
- cold 64K prefill: **959.6 tok/s**;
- 258K request with 64K cached: **891.6 tok/s** prefill.

This independently converges with oMLX #3791's **116-117 tok/s** current M3 Ultra Flash MTP result despite a different runtime/quant path.

### Project 51 consequence

This strengthens the **upside tail**, not the headline probability. It shows that two distinct modern Apple runtimes can drive short-context Flash MTP far above the 40-TG target and that long-prompt prefill on a single stronger Apple memory system has large headroom. It still does not answer the critical missing cell: **xhigh / MTP decode at ~128K on exact M1/TB4 topology**.

## Screened / no target-changing evidence

- **vLLM #53080:** target/draft scheduling-budget separation is highly relevant conceptually, but its substantive implementation commit is August; not relabeled new.
- **vLLM #56926:** THP-packed host-table lookup evidence is useful for large host tables but substantive changes predate this window; latest activity is merge/rebase metadata.
- **vLLM #57865:** new retained-workspace/KV-sizing accounting reinforces live-memory admission, but has no P51-specific throughput receipt.
- **DS4:** no strict-window Project-51 implementation receipt.
- **oMLX:** #3791 recorded above; several other merges are VLM/DeepSeek/offload-specific.
- **mlx-serve:** f666 recorded above; no new exact Flash-Next M1/TB4 receipt.
- **llama.cpp:** no strict-window P51 Metal/M1 throughput receipt.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no activity.
- **MTPLX:** no post-boundary commit.
- **APEX:** no post-boundary commit.
- Current Reddit/Hugging Face scan found no new exact dual-M1/TB4 Flash receipt.

## Target impact

**No numeric change.**

Production remains:

- **>=38 AA-class behavior hard floor; 39-40 preferred**;
- **40 TG @ ~128K** headline;
- **400 genuinely cold PP** headline.

The GSQ/RCO result widens the **experimental allocation search space downward**, but it does not lower the production-quality standard or promote a 3-bit runtime target.

**New hard boundary: 2026-09-21 10:36:04 UTC.**
