# Project 51 / Relay — research watch 2026-10-19 10:38 EDT

**PREVIOUS STRICT CUTOFF:** **2026-10-19 11:13:49 UTC**.
**NEW STRICT CUTOFF:** **2026-10-19 14:38:35 UTC** (user message Oct 19 10:38:35 EDT).
**Method:** Read `RESEARCH-STATE.md`, `RESEARCH-TARGETS.md`, and `RESEARCH-WATCH-LATEST.md` before searching; inspected authenticated GitHub PR/issue creation times and bodies, Agens Engine primary README/CHANGELOG and dated commits, and independent web discovery. NEW=created/published within this strict UTC interval, UPDATE=materially changed within, KNOWN=already cited, RECOVERED OLDER=prior-cutoff source newly incorporated. Source PRs OPEN unless explicitly merged. Earlier experimental numerical claims on other GPUs remain non-transferable to owner's native headless Linux. No actual owner hardware test, model/code/verifier changes or target ladder adjustment.

## Priority A: RECOVERED OLDER within Oct 19 — Volundr v1.3.0 released 2026-10-19 09:19:42Z, before previous strict cutoff

**Sources:** https://github.com/BlockWayz/agens-engine ; https://github.com/BlockWayz/agens-engine/blob/main/CHANGELOG.md ; commit `8ebc3366da77deb270cf7d44feb8bdd670d80e71`.

- **RECOVERED OLDER (missed in previous watch, not newly released in this delta):** release **1.3.0** supports **MTP under tensor parallelism (`--tp 2/4`)**; greedy output equals undrafted for 13 textual and 26 vision-tested prompts, author sampling distribution checks. Earlier 1.2 expressly disabled MTP+TP; this is a real change, but **two physical 16GB GPUs were still not tested**; vendor dual 16GiB cap experiments use 48GB GPUs constrained to budget. No cross-vendor AMD+CUDA or CUDA→Metal multi-node variant.
- **Vision + MTP in all 16/24/48 GiB profiles** using shared temporary workspace. Vendor `16gb` on a physical **48GB GPU held to 16GiB**, mixed2/3/4bit Volundr32B, observed max actual context **217,092 tokens images+MTP**, **237,572 text+MTP**, **225,284 with images and no MTP**; image+MTP 219K document+follow-up+two images author reports **16.75GB decimal device memory within 16GiB cap**. Note the **model's initial document length may exceed remaining active context if images/outputs included**; distinguish configured max from actual admitted session budget. Team's card states `--mtp` 16gb one conversation, cannot assume >=3 concurrently.
- `--budget-gib` now uses **GPU-resident KV when all fit** and host-tiered KV otherwise. Shipped budget profiles still tier KV, so 16GiB profile isn't suddenly fully resident. Single non-TP profile's stored KV can use **~24GB pinned host** at262K.
- Still no team-authored **physical RTX5070Ti 16GB sm120** test, no official ROCm or MLX engine; SM120 CUDA kernels *built, not hardware validated*. Existing 16GiB 2.82bpw quant **GPQA Diamond73.7 vs BF16 v1 80.3**, 4/13 long high-thinking 110K document tests looped/not completed (earlier source); `--think-guard` is mitigation not healed underlying quality. Vendor short greedy speed ≈140.7TG code with MTP in 1.2 is **not exact owner's expected speed**. First user-run experiment separate from Qwen Flash Swift primary with 16GiB true device admission+driver, tool/screenshot, thinking loops, solve/hour.

## Priority B: NEW Strata request-depth KV ring #3168 on Radeon RX7900XTX — *generate only*

**Source:** https://github.com/Niko1221/Strata/pull/3168 (NEW OPEN created 13:37:49Z), and https://github.com/Niko1221/Strata/issues/3166 (NEW 13:01:52Z).

- `STRATA_KV_RING_ADAPT` (opt-in) sets ring `clamp(round_page(prompt+max_new),32768,cap)`. Uses `--kv-resident` as cap and selects before arena + CUDA/HIP graph capture. Interleaved Radeon7900XTX24GiB gfx1100, ROCm10.2, QFN IQ3_S, 256 output-token trials: 1K130.8→130.6TG (-0.2%),32K74.2→83.8(+12.9%),128K77→81.9(+6.4%). Client first-token/prefill neutral; limited 3–5 pairs and only 256 outputs. Earlier flat enlarged ring32768→49152 at 1K **MTP140.3→84.0TG (-40%)**, while MTP-off36.7→37.8; inconsistent draft resource competition. Adaptive ring preserves shallow allocation.
- **Not integrated with `--serve`** conversations; author explicitly says requires per-conversation create hook. No physical RX6800 gfx1030 or RTX5070Ti16 result and not robust long-agent suite. Track before promoting in multiagent project.

## Priority C: NEW exact Pi and 5070Ti screenshot-agent correctness repairs

- https://github.com/Niko1221/Strata/pull/3167 **NEW OPEN 13:17:34Z**: serve aliases **`thinking_token_budget`**, **`thinking_budget`**, **`thinking_budget_tokens`** to `reasoning_budget_tokens` on OpenAI/Anthropic/Responses endpoints, native field wins. Previously silently ignored; now value validation catches invalid and real budget applied. Four focus and 341 server tests passed using mock engine, **no GPU run**. This may materially influence coding-agent thinking length and solve metrics even with identical model; include API budget/test harness parity in benchmark.
- https://github.com/Niko1221/Strata/issues/3171 **NEW 14:34:16Z** + https://github.com/Niko1221/Strata/pull/3174 **NEW OPEN 14:37:51Z**: 5070Ti16 **Windows Strata0.1.44.1** + `vram_elastic: true` & elastic GPU vision: images returned by Read/MCP tool fail with internal AttributeError but wrongly report 400 malformed, because vision encoder was never started; ordinary user-sent images succeed. Two-line `_vision_up()` fix author-reproduced success on exact model of card. **No Linux sm120 reproduction**, but high priority owner Py/Playwright screenshot agent test; mitigation disable elastic vision until fixed. Current patch does not improve cases where internal exceptions erroneously get 400.
- https://github.com/jundot/omlx/pull/4663 **NEW OPEN 14:00:29Z**: opted-in cluster eviction of non-pinned, competing local models on exact peer where structured InsufficientMemoryError occurs; 1,569 cluster tests pass, **does not make multiagent caches resident**, no M1 physical test. Safer failure attribution than automatic arbitrary eviction.
- No new direct KVMem (source last merge10:33Z before cutoff), NInfer direct5070Ti fork/new Linux benchmarks, or Adaptive V2 full attended CUDA-to-Metal transfer in strict window. Earlier NInfer GSQ-RCO Swift S physical Windows5070Ti16 128K~91.9–97.8TG +177MiB slack remains RELEVANT **KNOWN older** but not NEW.

## Priority D: NEW merged ModelOpt support, different model / Apple GPU

- https://github.com/jundot/omlx/pull/4661 **NEW and MERGED** created13:06:09Z, updated14:22:38Z. Fixes NVIDIA **ModelOpt two-level NVFP4 per-expert scaling** including stored MTP experts for a GLM5.3-Flash-FP4-Local **MLX repack**, using `weight_scale_2*2688` as global scale for oMLX QuantizedSwitchLinear. Validation M5Ultra256GB, MLX active model174.33GiB, 129 expert scale tensors matched; 15 specific tests, teacher-forced NLL checks. Branch overall tests180? 18,102 passed,12 failures present on main. **NOT** NVIDIA Qwen3.8-Flash-Next-FP4-Local serving on M1Max64 nor compressed scale compatibility across models; memory footprint alone excludes current 64GB single M1.
- https://github.com/ashhart/TensorFold/pull/1068 NEW OPEN12:13:14Z: isolated CUDA GeGLU/SwiGLU rounding kernels, 7.55M outputs exact within float64 rounding restrictions on GB10, **no actual model invocation or speed**. Don't count as 27B/Volundr CUDA boost.
- https://github.com/ashhart/TensorFold/pull/1066 **KNOWN in earlier cutoff** created10:45Z; updated14:08Z, Flash-family *different* GLM5.3-Flash M5Ultra tensor kernel 4.4–5.3% prefill, no M1 proof.
- https://github.com/Niko1221/Strata/pull/3163 and /3164 **NEW OPEN** 12:35Z: HIP QSA selection WMMA split and grid reorder physical gfx1151 Strix Halo; scorer kernel up to2x or27% faster but whole inference only about +1.8–1.9%; grid bit-identical, split2 sometimes changes selected blocks at 262K. **gfx1151 WMMA is not RX6800 gfx1030**, do not transfer.
- https://github.com/Niko1221/Strata/issues/3169 **NEW 13:58Z**: two RTX3090 24GiB +178GiB host QFN IQ3_XXS, 262K configured, short chat125.8TG, PP16K3273 and short synthetic 15K agent turns139.4TG, **no actual long262K fill, tool quality or streaming proof**. Separate multi-GPU/no purchase baseline.
- https://github.com/Niko1221/Strata/issues/3173 **NEW 14:36:15Z**: two MI50 gfx906 16GiB ROCm7.14 QFN IQ3_XXS, `--pipeline-windows 2` lifts **49.2→66.9TG** at short 1.6K prompt with 131K configured, not exact RX6800 physical or measured active128K; no independent quality. Platform v0.1.43.1, cannot build0.1.45, related issue #3172. Does not support user single RX6800 performance.
- https://github.com/Niko1221/Strata/issues/3170 NEW 14:24Z: Windows gfx1100 large-batched prompt intermittently kills Strata after 80 min despite dozens good requests; not gfx1030 owner, general stability gate.

## Project 51 decision

- **RTX5070Ti16 /64GB Intel265F native headless Linux**: keep QFN Swift1.5 IQ3_S low primary, dense27B NInfer Swift/ByteShape, KVMem and AdaptiveKV independent compare. Validate API thinking budgets and screenshot tool-return elastic vision, complete long 128/200/262K saved state and solve/hour; do NOT import measured ROCm gfx1100+12.9% or MI50 +36%. Volundr Engine1.3 qualifies for separate bounded **single** 16GB experimental trial and needs true board test.
- **M1Max64×2 TB4**: exact dense27B ruler oMLX #4496 M1Max64 DFlash2 24.2TG133K still not superseded; #4661 GLM ModelOpt import irrelevant to QAD QFN on M1; #4663 opt-in eviction isn't shared resident prefix. No 128K second Mac/PC handoff.
- **RX6800 gfx1030+32GB**: prior #3146 gfx1031 FP16 prompt speed gain source, no direct gfx1030; no current new exact-card physical speed. Separate HIP machine remains independent worker, not same-PC CUDA+HIP expert helper #3127.
- **No changed performance targets, source models, hardware purchase, M1 Linux transfers, frozen verifier or experimental code.** Future numerical ladder revision requires exact context+source quality+completed agent workload.

**NEXT STRICT WATCH begins after 2026-10-19 14:38:35 UTC.**

## Source receipts
- https://github.com/BlockWayz/agens-engine
- https://github.com/BlockWayz/agens-engine/blob/main/CHANGELOG.md
- https://github.com/Niko1221/Strata/pull/3168
- https://github.com/Niko1221/Strata/issues/3166
- https://github.com/Niko1221/Strata/pull/3167
- https://github.com/Niko1221/Strata/issues/3171
- https://github.com/Niko1221/Strata/pull/3174
- https://github.com/jundot/omlx/pull/4661
- https://github.com/jundot/omlx/pull/4663
- https://github.com/ashhart/TensorFold/pull/1068
- https://github.com/Niko1221/Strata/pull/3163
- https://github.com/Niko1221/Strata/pull/3164
- https://github.com/Niko1221/Strata/issues/3169
- https://github.com/Niko1221/Strata/issues/3173
- https://github.com/Niko1221/Strata/issues/3170
