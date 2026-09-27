# Project 51 primary-lane research watch — 2026-09-27 13:04 ET

**Freshness boundary:** canonical boundary entering this pass was **2026-09-27 13:12:54 UTC**. This watch covers qualifying evidence strictly after that boundary through the user cutoff **2026-09-27 17:04:18 UTC**.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- central TG region **~39-41**, mature downside **~30-32**, target-only fallback **~24-27**
- single-M1 27B: **25 TG canonical target**
- 5070 Ti + Strata Flash lane: experimental until exact-hardware TG/PP and AA~40 certification.

This interval strengthens a systems conclusion: realized local-LLM speed is increasingly limited by **synchronization, launch topology, state materialization and residency headroom**, not only the nominal FLOP/bandwidth roofline.

## NEW — mlx-serve #584: async-eval ladder buys ~3-6% on Flash batched decode, but only after host PLE materialization

Source: https://github.com/ddalcu/mlx-serve/pull/584  
Merged **2026-09-27 16:53:00 UTC**, commit `42b34e2c7d2d4f6a41e6c0fbf731abb00e7dd31d`.

Qwen3.8-Flash-Next batched decode now asynchronously evaluates `{h, mlp_out}` every fourth layer. The correctness trap is important: on the CPU PLE arm the deferred PLE embedding is initially a **zero-filled MLX leaf** whose host gather is filled later. An early async eval before `flushDeferredPle` therefore consumes zeros. The patched path fills the leaf before the first ladder boundary when ids are host data, and skips the ladder when ids are still lazy.

Removing the early materialization changed **128/128 logits** in the regression.

M5 Max 128 GB / mixed4-8bit / CPU PLE / MTP off, same-binary A/B:
- prose x2: **43.6 -> 46.2 TG**
- prose x4: **31.2 -> 32.1 TG**
- ~8.5K x2: **41.0 -> 43.4 TG**
- serial: unchanged around ~61 TG.

**P51 consequence:** async/lazy evaluation can recover several percent without changing arithmetic, but host-produced leaves/recurrent state must have an explicit materialization/visibility boundary before any early GPU eval. This belongs in our verifier, PLE staging and heterogeneous-prefill state protocol.

## NEW — mlx-serve #580: fused QSA at S=1 helps batched long-context decode, not a lone stream

Source: https://github.com/ddalcu/mlx-serve/pull/580  
Merged **2026-09-27 16:52:49 UTC**, commit `185bfe2cf7352c85c905c17bc0c5d53c7e8c0ee1`.

Past the QSA gather threshold, each S=1 row in a multi-stream batch previously launched a dependent chain: index expansion -> gather -> subset dequant -> masked SDPA. The fused split-K sparse kernel already matched S=1 within two bf16 ulps, so the batched floor is now lowered to S=1 only when `n >= 2`; solo decode retains the old path.

M5 Max / Q8 KV:
- four streams, ~11.9K: **37.3 -> 34.9 ms/step**
- four streams, ~47.6K: **~3.0-3.1 ms/step saved**
- four streams, ~95.5K: **~3.1-3.6 ms/step saved**
- two streams, ~47.6K: **~0.8-1.4 ms/step saved**
- one stream: neutral at ~12K and ~95K; fused path can be 0.05-0.2 ms slower solo.

Dense bf16 S=1 parity was subsequently added at 9K and 40K and stayed within the two-ulp bar.

**P51 consequence:** dispatch policy needs the tuple **GPU generation x quant/KV format x tensor geometry x S x KV depth x active concurrency**. A path that loses at solo S=1 can win materially when N independent S=1 rows share one fused launch.

## NEW — Strata v0.1.9: nominal free VRAM can become a hard stall

Source: https://github.com/Niko1221/Strata/commit/0680ab633f69deb23ac6c4691737386d459a9843  
Committed **2026-09-27 14:23:07 UTC**.

Strata's adaptive expert cache was sized from free VRAM **before** the native output head (~0.44-0.52 GB) and later buffers were allocated. On IQ3_S at 128K this left only **30 MiB** free; the driver paged GPU memory and the first verify window stalled indefinitely while monitoring showed GPU '100%' at ~45 W.

Fix: load the head first, then size the expert cache around everything already resident.

Afterward:
- **480-626 MiB VRAM remains free** with everything loaded;
- Q2_0 32K expert slots shrink ~8% (**4,167 -> 3,848**);
- same greedy prompts measured **78-79 TG median vs 71.7** on engine 0.1.8;
- startup warns below **256 MiB** and recommends additional reserve.

**5070-Ti consequence:** do not chase the maximum expert-cache count. For the user's 16-GB card, reserve hundreds of MiB after *all* fixed heads/graphs/workspaces are loaded and measure actual free VRAM under the 128K verify path. A slightly smaller hot-expert cache can be substantially faster than triggering CUDA paging.

## QUALITY EXCLUSION — Strata experimental speed projection

Commit `9e599c076e2f74a83b8576c5e171f7e99e635062` adds an optional control-vector/refusal-direction projection. It is **off by default**, costs only 0.2-0.4% per token, and reports mean teacher-forced KL **0.063** over 2,557 tokens.

This is behavior modification rather than an inference optimization. **Do not enable it in AA~40/source-like certification or baseline speed tests.**

## Reddit thread — 'The Silent Bottleneck'

Provided URL: https://www.reddit.com/r/LocalLLM/comments/1wra2ph/the_silent_bottlenec/

Reddit refused direct retrieval in this environment and the fresh post was not yet indexed by the search backends, so this watch does **not** attribute any exact claims, numbers or quotations to it.

The broad framing nevertheless has substantial independent support **today**:
1. vLLM #58684: a tiny blocking D2H metadata read made async sparse/MTP decode slower; removing it cut TPOT up to **38%**.
2. mlx-serve #584: lazy host-state timing changed correctness and async scheduling recovered several percent.
3. mlx-serve #580: a chain of small QSA kernels loses to one fused launch under batched S=1, even though solo S=1 does not benefit.
4. Strata v0.1.9: 30 MiB nominal VRAM headroom caused driver paging and a full verify stall.

Therefore the **general thesis is valid** if it is 'the real bottleneck can be synchronization/memory plumbing/residency rather than headline FLOPs or bandwidth.' It would be **too strong** if interpreted as one universal bottleneck or as evidence for a specific M1 speedup without exact Apple7 measurements.

## Other strict-window activity

- vLLM had unrelated ROCm DeepSeek-V4.1 multi-stream and pooling work after the current boundary; no direct Apple/P51 target credit.
- oMLX, Splash, MTPLX, Ishizuki, DS4, DASLab/GSQ and ModelOpt had no new qualifying primary-lane receipt in this strict interval.
- Strata also added service/UI reliability changes; no additional planning-grade throughput receipt beyond the v0.1.9 residency fix above.

## Canonical planning effect

**Targets unchanged.** Add three durable rules:
- never infer forward progress from utilization alone;
- keep explicit post-load VRAM headroom;
- treat host sync/materialization and kernel-count/launch topology as first-class terms in the cost model.

`RESEARCH-STATE.md` is updated with #584, #580, the Strata v0.1.9 reserve rule, and the quality exclusion. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 17:04:18 UTC**
