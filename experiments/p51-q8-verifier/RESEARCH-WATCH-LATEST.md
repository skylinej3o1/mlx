# Project 51 / Relay — research watch 2026-10-18 14:56 EDT

**PREVIOUS STRICT CUTOFF:** **2026-10-18 13:24:10 UTC**.
**NEW STRICT CUTOFF:** **2026-10-18 18:56:22 UTC** (user request October 18, 14:56:22 EDT).
**Basis and procedure:** Read canonical `RESEARCH-STATE.md`, `RESEARCH-WATCH-LATEST.md`, `RESEARCH-TARGETS.md` before search; inspected authenticated GitHub PR metadata and primary full-body receipts plus first-party researcher repo README/CHANGELOG, official NVIDIA card, and Terminal-RSI author page. **NEW** means created inside this strict interval; **UPDATE** means previously observed evidence materially advanced within it; **RECOVERED OLDER** means older pre-cutoff work previously unlogged. A newly opened docs PR is not newly built code; upstream OPEN != merged; an author's vendor vs independent numbers, M1 vs M5, single vs multi GPU, short context vs native262K, configured vs filled, request count vs concurrent solved-task count remain distinct. Some live repo documentation may include later edits; claims are source snapshots rather than as-of-time independent execution. **No experiments run on owner's hardware, no code/model/quant/verifier changes.**

## Top-level conclusion

**Biggest update: fully served NVIDIA QAD FP4-Local checkpoint on ONE DGX Spark 128GB with TensorFold's Zig CUDA engine, documented today in primary receipts.** This is stronger than the previous source-parser-only watch, but **does not move the owner single RTX5070Ti16 +64GB headless Linux fit, throughput or AA quality forecast**. **Exact M1Max64** Strata Metal measurements now give Q2_0/IQ3_XXS/IQ3_S speed at only 32K configured context. Reliability changes in tool-call parsing, vision-prefix caching and memory / sampling require separate agent quality gates.

## 1. NEW today: NVIDIA QAD FP4-Local actually served on GB10, not merely parsed

**Primary repo:** https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold and its primary README/CHANGELOG.
**Independent author lab account:** https://mia-ai.net/models/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold
**NEW TensorFold #1042 OPEN docs PR (created 2026-10-18 18:37:30Z):** https://github.com/ashhart/TensorFold/pull/1042
**Checkpoint:** https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local pinned `b9ce18a6887e18c089fdea8509a33e63429a3300`. First-party NVIDIA release **Oct5**—NOT a new checkpoint release or a community GPTQ quant.

- Author Zig branch `zig-flashnext`, patch stack built against `db281878` and TensorFold native sm121 CUDA. Actual QAD checkpoint has **all 512 experts, ten routed per token**, NVFP4 with losslessly compressed CSF scales, MXFP8 attention/shared linear, separately quantized vision and MTP, SSD-streamed **~26.8GiB PLE**. A new CUDA FP4 support patch is actually integrated into recipe (as distinct from still-OPEN TensorFold upstream GLM-specific #1021/#1023 host-only prototypes). Vision on, draft MTP on, FP8 KV, parallel5; one DGX Spark 128GB (reported ~121GiB usable).
- **Author physical speed** on one GB10, *prose*: **46–55 TG** single request, **73.5 /90.3/106.4/132.7 TG aggregate** at 2/3/4/5 simultaneously; prose 5-way per stream ~27.7 TG. *Code*: single **67.9 TG**, five-way aggregate **149.7 TG**. Short-code output and prose are different acceptance regimes; don't add or multiply. First token after cached prefix ~195–266ms for one-five prose queries in the measured table.
- Fresh cold prefill (full lab's headline performance, single GB10) **~2,665PP at4K**, **~2,501PP at16K**, **~2,430PP at32K**, **~2,197PP at131K**; pairwise tile-on/off in a controlled section 4K **2,090→2,397PP (+14.7%)**,16K **2,174→2,474(+13.8%)**,32K **2,161→2,450(+13.4%)** from a new `TF_FLASHNEXT_PROMPT_EXPERT_TILE` on ≥1024-row prefill. Table contains two slightly different measurement procedures; don't treat sparkDash vs `bench_streams` rates as interchangeable.
- Fit is decisive: author says **~96GiB checkpoint on disk; ~81GiB loaded model memory with vision; ~85GiB actual idle system memory** and 98.6GiB peak under five100K prompts+six short. Startup calculated ~108GiB minimum free for full default scenario; default pool **~24.36GiB of sequence memory**, one262K FP8 KV ~4.37GiB; model's 262K request window configured. **One true 194,723-token needle** found at99.4s /1,959PP (older or alternate benchmark state), five 100K prompts plus six small replied without crash; no independently solved Pi agent corpus at 262K and no owner64GiB fit.
- Exactness: 7-prompt greedy and serial/drafted/concurrent token identity *within same engine*, teacher-forced match against prior Python engine **2,270/2,295 positions (~98.91% top1)**, toolcheck3/3 and image/vision smoke. These are **not** independent NVIDIA GPQA or AA replicated results. The original **91.5% GPQA /88.7% ToolEvalBench** remain NVIDIA vendor figures from previous watch.
- NEW #1042 is a **docs-only** recovery from earlier #952 merge; no fresh CUDA execution in that PR and no official TensorFold release gate established by it. Mia's independent patch stack and app *do* document served model. Watch stable upstream merge and isolate exact source revision.
- **Owner conclusion:** 5070Ti Blackwell sm120 supports FP4 arithmetic, but *81GiB loaded* exceeds 64GB host plus16GB GPU nominal physical capacity, without OS/KV overhead; can't assume usable because combined nominal ≈80GB (and GB≠GiB). Need streamed expert file tier / stricter quant or bigger RAM; both risk huge slowdown and model fidelity. Do NOT confuse this distilled model with Maximilian228 community GPTQ Strata. User hardware purchasing/probabilities unchanged.

## 2. NEW exact M1Max64 Strata source-grade performance, context explicitly only <=32K

**Strata #3067 NEW OPEN** created Oct18 **15:45:54Z** https://github.com/Niko1221/Strata/pull/3067
- Hardware Apple M1 Max 64GiB/32GPU, macOS Metal, Strata commit `38978a6d`, source GSQ-RCO FlashNext; short-chat TG **Q2_0 35.1**, **IQ3_XXS 32.0**, **IQ3_S 23.1**. Resident Q2_0 and IQ3_XXS `STRATA_METAL_STREAM=0`; IQ3_S streamed arena38GiB/share0.3. Fresh16K PP ~**380 /320 /290**, respectively.
- Six needles found at 16K and30K (depth10/50/90 for each). **Configured context32,768**; 32K benchmark and128K needle not run; speed-only plus needles, **no agent correctness/long-running tool campaign**. Faster Q2 quant could lose quality; Q2/XXS resident vs IQ3S streaming confounds quant-only speed comparisons.
- Strongest direct chip receipt in Strata this pass, **not** a revision of oMLX M1Max64 dense27B DFlash2 #4496 **24.2TG133K** (different model/runtime/ctx), and NOT a two-M1 FlashNext 40TG@128K receipt or oMLX comparative win. Need same checkpoint/source/effort/quality and 128K B1 side-by-side; M1 Mac code path sampler #3006 still gated.

## 3. NEW NVIDIA Blackwell sibling 16GB and exact multi-GPU calibration evidence

- **Strata #3068 NEW OPEN** Oct18 **16:03:37Z** https://github.com/Niko1221/Strata/pull/3068: RTX5080 16GB +60.2GB RAM **native Linux**, UD-IQ4_XS, FP8 PLE sidecar and `STRATA_HC_Q8=1`, int8 KV 128K configured. Short chat **72.9TG**, agent followup **69.7TG**, ~68.8% short-session cache reuse; 6/6 32K/128K needles passed, but PP highly unstable **323–998PP4K across work windows**, per-run true context not 128K resident Pi, single client only. Informal HC_Q8 +21% decode **n=1** not quality-controlled; **not owner5070Ti** and model UD-IQ4_XS not Swift IQ3_S. Useful to test HC_Q8 and high precision PLE independently on exact sm120.
- **#3076 NEW OPEN** Oct18 17:10:16Z https://github.com/Niko1221/Strata/pull/3076: **RTX5060Ti16+RTX4080Super16** on Windows, IQ2_XS, calibration changed pcie share0.55→0.90, spec-min-p0.5→0.7, prefill-pipe 0→3072 and run conditions; short chat45.2→80.4TG, PP16K705.7→1707.5, agent44.3→72.6. **Unpaired, two GPUs, different model/CPU, speed only**. Demonstrates calibration sensitivity, NOT owner single5070Ti expected delta or simultaneous client capacity. Freeze config before engine version A/B.
- **#3064 NEW OPEN** https://github.com/Niko1221/Strata/pull/3064 on AMD HIP GDN verify: split batched commit previously silently disabled, optimized LDS barriers and prefetch, author gfx1201 RDNA4 parity bench with gfx1030 asm branch. **No owner RX6800 gfx1030 physical long-agent speed**. Keep exact #2788 async-copy soak and #2941 k16v8 precision parity first.

## 4. Agent correctness and long-lived sessions

- **oMLX #4654 NEW OPEN** created Oct18 **15:54:19Z** https://github.com/jundot/omlx/pull/4654 : live Qwen3.5-9B MLX tool argument that **contains literal closing XML function/tool tags** causes streaming frontend to terminate tool envelope early and leak rest of tool argument as visible prose. Branch balances nested `<parameter>` tags in one shared scanner across streaming/non-stream/wrapperless parsers. Live model reproduced, 16,839 tests pass. Tool-call args already complete; symptom is **content leak/parser-boundary correctness**, not tool loss in that trace. Limits: malformed unclosed parameter and ambiguous literal close tags cannot be unambiguously recovered with same token ids. Not yet merged and not specifically M1 dense27B QFN.
- **MiaAI-Lab #70 NEW OPEN** created Oct18 **16:54:06Z** https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold/pull/70 : GB10 full QAD model with **7 screenshots**, repeated 19,588-token image chat, reusable visual rows keyed by features, second turn **0→19,581 token reuse; 9.13s→0.20s prefill**; changed screenshot forces full miss, resumed reply SHA equal to freshly computed. **Opt-in on one rank and paired patch**, not baseline cross-rank or M1. There is also an *older in this time window's watch?* #69 opened 12:15Z **before cutoff** (RECOVERED OLDER), **alternative patch named 0016** for xgrammar structured-output support with vendor FP4 QAD, hardmode ToolEval score86→88, structured6/12→10/12, no nonstructured speed change. #69 and #70 independently name patch 0016; **do not claim both patches already merged or composable**. They demonstrate controlled API and screen-agent reliability levers.
- **Source Terminal-RSI official author page** https://jyyang26.github.io/terminal-rsi/ still displays **"Code soon / Model soon"** as checked Oct18, **no downloadable Terminal-RSI-27B checkpoint or confirmed released training code**. Prior paper is **RECOVERED OLDER Oct15** and its context/evaluation/failure limits persist: final four-suite mean50.58% but strict long-horizon success5/46, 96K eval limit with32K summary; not a new Qwen3.8 dense27B local model or runtime improvement this pass.
- **Strata #3042 previous-window NEW but now relevance:** 503 refused batch admission counted as completed HTTP requests; genuine 3-5 agent success metric must use protected terminal tests, not request counts or draft accept. #2934 glibc park memory floor, #2930 boundary checkpoint, #2952 out-of-order Chat Completions tool results, oMLX #4637 multi-engine shared Metal queue remain critical prior watch items.

## Changes to project plan / acceptance gates (only source-backed)

1. **High confidence *format-engine proof*, not owner deployment:** NVIDIA QAD FP4-Local now **actually runnable** on GB10/128GB, proof ~81GiB model loaded, 24.36GiB KV pool, 1–5 concurrent. Track source format + SSD PLE and stable upstream path. Owner RTX5070Ti16+64GB remains Swift1.5 GSQ-RCO IQ3_S low default and Swift Q2_0 fast alternate; QAD cannot fit as currently deployed. No numerical owner TP or quality prediction.
2. **M1Max64×2**: compare physical Strata Flash Q2/XXS/IQ3S 32K with physical oMLX Flash and dense27B actual133K receipts (not same model). Request 32/64/128K resident source-like IQ3 and multiagent, sampler/effective sampling correctness and cache restoration. Existing Relay 40TG@128K, 400PP target unverified.
3. **Agent-suite quality**: XML close tags in file arguments, same tool name/out-of-order results, screenshot identity/reuse, held state, false HTTP503 "success", successful terminal verifier and tasks/hour; guarded cache roots under long static tool headers.
4. **Radeon RX6800 +32GB**: #3064 gfx1030 code path not a physical proof; prioritize #2788 async copy exact chip, #2941 k16v8 quality/VRAM and full fill admission; no 262K target change.
5. **No trained Terminal-RSI released** and no new owner-class complete CUDA→Metal transferred GDN/QSA/PLE committed-state frontier. No frozen verifier or experimental source modifications. No hardware purchase or numerical probability change.

**Next strict watch begins after 2026-10-18 18:56:22 UTC.**

## Primary links

- https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold
- https://mia-ai.net/models/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold
- https://github.com/ashhart/TensorFold/pull/1042
- https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local
- https://github.com/Niko1221/Strata/pull/3067
- https://github.com/Niko1221/Strata/pull/3068
- https://github.com/Niko1221/Strata/pull/3076
- https://github.com/Niko1221/Strata/pull/3064
- https://github.com/jundot/omlx/pull/4654
- https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold/pull/70
- https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold/pull/69
- https://jyyang26.github.io/terminal-rsi/
