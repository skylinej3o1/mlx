# Project 51 / Relay — research watch 2026-10-17 20:40 EDT

**PREVIOUS STRICT CUTOFF:** **2026-10-17 19:05:57 UTC**.
**NEW STRICT CUTOFF:** **2026-10-18 00:40:26 UTC** (user asked at Oct17 20:40:26 EDT).
**Method and scope:** Read `RESEARCH-STATE.md`, `RESEARCH-TARGETS.md`, and `RESEARCH-WATCH-LATEST.md` before live research. Authenticated GitHub PR/issue metadata and author measurements from Strata, oMLX, Splash, TensorFold, mlx-vlm and Basalt; first-party NVIDIA and community model cards plus Reddit. **NEW** = PR/issue created within this strict window (not necessarily merged); **UPDATE** = pre-existing source meaningfully advanced by cutoff; **RECOVERED OLDER** = a previously overlooked older release relevant to today's request. Some web pages are live and may have been edited after cutoff; release dates and source status at retrieval are explicitly separated. Benchmarks in PRs and model cards are not run on owner's gear. Respect exact active context and source-quant/runtime/OS details. Research only, no executable code, model source, frozen verifier or numerical targets changed.

## Executive finding: NEW-to-our-watch NVIDIA Flash-Next quantization is NOT NEWLY RELEASED in this cutoff

### RECOVERED OLDER, **official NVIDIA Qwen3.8-Flash-Next-FP4-Local** (QAD)

- First-party checkpoint https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local card **release date 2026-10-05**, subsequently discussed Oct15 at https://www.reddit.com/r/LocalLLaMA/comments/1x6vqft/fp4_qad_quant_of_qwen38flashnext_from_nvidia/ . **Not a new Oct17-evening release**. Repo approximately **96 GiB weights / ~102 GB** on disk; distinct from NVIDIA's **older** https://huggingface.co/nvidia/Qwen3.8-Flash-Next-NVFP4 (**~133GB**) released Aug31. It is not the same as an unrelated community GPTQ-Strata checkpoint.
- It is **quantization-aware distilled (QAD)**, not merely post-training quantization. BF16 teacher logits and hidden-state targets, end-of-thinking/end-of-response loss; ModelOpt/Quatrain training **2,500 trunk updates + 1,500 joint updates** including n-gram/PLE tables, frozen attention. Routed experts QAD **NVFP4 E2M1 + E4M3 block scales**; decoder attention **MXFP8**; MTP experts **NVFP4** with BF16 activations, parts of vision NVFP4/MXFP8 and critical norms kept FP32/BF16. The checkpoint also uses novel losslessly compressed NVFP4 scales unsupported in upstream stock vLLM at card date; validated using **custom local-inference-lab/B12X vLLM containers** on **RTX PRO6000 Blackwell 96GB (one card; PLE offload)** or **DGX Spark 121GB UMA**. NVIDIA describes 262K native context and optional extended context; do **not** claim 1M quality from a KV-capacity statement.
- Vendor-published BF16 versus QAD: **GPQA Diamond 92.2%→91.5%**, **ToolEvalBench 89.4%→88.7%** (0.7 percentage-point absolute each). Strong *vendor* retention on those protocols, **not** same-bench comparison to Swift1.5 IQ3_S, nor evidence long Pi repo tasks and native low/xhigh quality. Separate older NVIDIA NVFP4 posttraining card compares against FP8 on different benchmarks and claims GPQA91.5, TerminalBench2.1 82.9; not comparable to QAD BF16 pair.
- **Owner 5070Ti16 + host64GB native headless Linux:** Blackwell CUDA FP4 ISA itself is present, **but 96GiB checkpoint is larger than 64GB RAM+16GB VRAM nominal aggregate**, before OS, KV, expert cache and model overhead. No validated Strata GGUF/FP4 conversion preserving QAD training, tool quality and high-precision islands, and stock local vLLM B12X requires incompatible memory/PLE/residency plan. Target **research-source-quality oracle / upstream derivation candidate**, not a downloadable drop-in daily driver; do not download ~102GB as if it will run at 90+TG on owner hardware. More efficient distilled 3–4bpw original/bounded-precision hybrid could be transformative **only after original learned weights + scales map to supported kernels and actual AA/code long-agent comparisons pass**.

### NEW-to-this-window source consumer NVFP4/GPTQ lane, distinct model

- **NEW Strata issue #2956**, author **RTX5060Ti 16GB** on Windows10, Ryzen5 5600, **96GB host RAM**, community pack **Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata**, engine 0.1.45, `--expert-cache 2048`, `--kv q4_0`, `--max-context 524288`, adaptive and MTP. Normal CPU/GPU run gives **26.1TG short**, **627 PP16K**, **635 PP32K**; a CPU/power-limited eco run 15.6TG. Human/coding task success **not tested**. Separate needle suite 3/3 at 32K,128K,~261K,~518K; ~518K prompt read **~862–863s**, reported decode18–19TG for needle. This is physically demonstrated *one-shot high-context retrieval* on a 16GB GPU, but **96GB RAM** and a more aggressively compressed KV/quant path. Do **not** count as an exact owner64GB admission or retained 3–5-agent win. Author says loaded model+ KV consumes about **63.3GiB +3.38GiB** in host setup; limited headroom on owner's64GB. Client cache reuse in short 14.6K agent suite 68.8%, no end-to-end solved tasks, no real 520K Pi.
- **NEW #2964**, RTX5090 +128GB host on same community GPTQ NVFP4 Strata pack, opt-in `STRATA_ADAPT_FETCH=2` admits fetched experts directly into VRAM cache. A/B **16.00±0.24→15.16±0.10 ms/verify round** (-5.3%), decode **151.9→159.2 TG** (+4.8%), short ~45 prompt/600 output, default disabled, incompatibilities with async/pipeline/batch/layer split; **not** official NVIDIA QAD and not owner16GB evidence. #2963 pinned sliced fallback: Windows RTX5090 48GiB resident expert copy 32K TTFT9.93→6.74s, auto-pinned original6.67s. Different WDDM/128GB case, not Linux native owner's free performance.
- **NEW #2995** *two RTX5070Ti 16GB GPUs* with this NVFP4 GPTQ pack, 4K cold prefill **2718 PP** opt-in scaled peer host-sums vs P2P1383 PP, and ~84K prompt **2638 PP**. Corrects **missing per-expert NVFP4 scaling** on peer path; previously refused/NaN for >=20K. This is **2 GPUs**, not one owner5070Ti16. Source opening at **2026-10-18 00:27:29Z** is within cutoff. No task-quality comparison or 3–5 agents; opt-in and unmerged. Source: https://github.com/Niko1221/Strata/pull/2995 .
- Two separate quant streams create a useful future experiment: original IQ3_S Swift daily driver vs community GPTQ Strata if 64GB fit solved vs **official QAD FP4-Local** only if a verified conversion/streaming engine makes it viable. Do not merge their benchmarks/quality results or call community GPTQ "NVIDIA QAD".

## Other NEW hardware and agent developments (Oct17 19:05Z–Oct18 00:40Z)

### Correct tool-output identity and memory under pressure

- **#2952 OPEN** Chat Completions can pair simultaneous `read_file(a)` and `read_file(b)` results in wrong order if client sends B then A. Proposed Python converter keeps `tool_call_id` until ordered by preceding assistant calls; same-function calls included. Complete unique-ID sets only; ambiguous histories retain original order. 384 tests passed/1 skip; **no GPU live task run**. Direct agent correctness priority: add out-of-order and duplicate function-name fixture to Pi/Playwright corpus.
- **#2962 OPEN** Strata conversation-cache pressure policy frees retained KV first, then least-recently-used parked dialog, then idle batch checkpoints when free physical RAM drops below floor. Uses `malloc_trim` to address *previous* Linux glibc bug #2934, but destructive eviction means agents re-prefill, so not a standalone answer to guaranteed resident 3–5 agent requirement. RTX5090/128GB/Windows GPTQ pack synthetic pressure 9.76→11.9GB available, two dialogs dropped, newest retained restored133ms; Linux allocator 256MiB unit test, not production Linux 64GB multiagent soak. Pair with proposed disk snapshots #2915 / prefix-rotation #2930 and RAM-pressure missing restores #2923. An under-memory condition must be reported, not silently credited as live caching.
- **#2989 OPEN** 2×RTX5090 Swift1.5 IQ3_S agent screenshot prefill alongside 4 decode sessions; longest decode pause ~**6.0s→0.1s**, sessions' in-prefill TG ~5→34–37, at slight extra incoming prompt TTFT ~6.4→7.4s. Explicit `STRATA_PIPED_CONCURRENT=1` multi-stage opt-in, not single5070/owner concurrent result. Useful multi-agent architecture case, no target revision.
- **#2985 OPEN** multi-stage `STRATA_PIPED_MTP` 4×RTX3090, four streams: code total203→270TG for N=2, prose209→216, depends draft acceptance and 4-GPU layer split; not owner singleGPU or dual M1.
- **#2986 OPEN**, two RTX5060Ti16 **native headless Ubuntu Server** +128GB RAM on Swift? **original Flash IQ3_S**, 262K *configured*: short chat93.6TG, agent90.4, 16K PP2002, with experimental speed projection ON; no true262K fill or quality gate. Example of headless native CUDA throughput, not direct owner speed prediction.
- **#2993 OPEN** one RTX4070 12GB + Ryzen9800X3D Windows Strata0.1.45 original IQ3_S: short chat66.1, agent69.7,16K PP1794, but only 16K filled and speed projection ON; different GPU, not owner.
- **#2965 OPEN** layer8–33 **experimental speed/projection vector changes outputs/refusal behavior** and lacks Swift1.5 support; candidate is neither QAD quant nor safe performance-only optimization. Do NOT enable in quality baseline.
- **#2959 OPEN** optional `strata_prefix` partial-message rendering could yield spurious HTTP400; patch ignores only optional bad heads without weakening real malformed request validation. Useful static system-prefix caching correctness.
- **#2960 NEW** on **RX7900XTX Windows HIP** reports 2/10 startups with GPU KV-streaming *zero block reads* past resident32768 and wrong long-text responses despite normal prefill rate; all-resident32768→131072 avoids it in 6 starts. Not RX6800 evidence but serious zero-block-read + answer-quality silent-failure regression gate, check long-context retrieval and block-read telemetry on owner card.
- **#2948 NEW** on 2×R9700 Linux: 0.1.45 auto two-stage pipelining with all experts GPU resident hurts decode~25% (at some long context higher); different hardware, reason not to auto-enable pipeline flags blindly.

### Splash / M1 Metal long context

- **#469 NEW OPEN** Splash extends the already-unmerged FlashNext 20-PR stacked patchset with **YaRN 4×**, fixes scaled QSA pooled-key rotation and grows QSA bitmap/window. Author on **M5 Pro64GB** streams `UD-IQ3_XXS` with 12GB resident expert cache and 2GB PLE cache; true 450K-token continuous grow 7/7 needles, prefill per step ~796–908 tok/s; planning 1,010,000 context is not a filled 1M prompt. No source-grade M1Max64 quality or pair/TB4. #470 OPEN further tests K320/640, permuted expert slots, PLE fully resident when cache>=table; stacked not merged.
- TensorFold #1005 previously NEW (strict cutoff last watch) M5Ultra256GB physical1M needle with >203GiB wired: no new target relevance. oMLX #4496 M1Max64 dense27B DFlash 24.2 TG133K remains OPEN, no M1 IQ3 3bit verifier or new M1 dualRelay.
- oMLX #4637 queue merge previous window remains recommended multi-model stability prerequisite, no current exact M1 Max receipt; no new model/quant that overturns it by cutoff.
- No newly validated Qwen4 production final checkpoint/GSQ-RCO 35B/ByteShape/Gyro-Signal + Swift combo, no CUDA→Metal complete QSA/GDN/PLE state transfer.

## Decisions / acceptance plan

1. **Quality:** Keep Swift1.5 GSQ-RCO IQ3_S original on **single RTX5070Ti16 +64GB native headless Linux** (Intel Ultra7 265F), low effort as provisional default. Evaluate community GPTQ NVFP4 (NOT NVIDIA QAD) only after actual host fit and solved-task parity, not because a 96GB host read a 520K needle. For NVIDIA QAD FP4-Local, first design exact-format ModelOpt-to-runnable engine plan and source-quality AA/tool/code tests: do **not** simply rename safetensors or presume a lossless GGUF mapping.
2. **True resident-agent readiness:** add tool_call_id reordering corpus, glibc release and park diagnostics, cache supersession rotation, concurrent 3–5 sessions and screenshots, require GDN/QSA+draft state hash, explicit reported refusal and successful return-turn TTFT (same resumed tokens).
3. **Version parity:** Pin 0.1.44.1 vs0.1.45 native headless Linux, set effective presence_penalty explicitly, log reason/effort & sampler, real 32/64/128/200/262K fill and output >=4K, no speed-projection/confounded behavior in base arm.
4. **RX6800:** exact gfx1030 32GB HIP K16V8 vs INT8 source-quality A/B, further #2788 async-copy stable soak, verify nonzero block reads past resident KV and no wrong retrieval.
5. **M1 Max64×2:** benchmark stable oMLX and DFlash #4496 first; investigate Splash #469 only if Apple7 kernel/PLE offload capability is proven, before 262K or beyond requests. Do not combine M5 YaRN claims with M1 context targets.
6. **No numerical performance ladder changes, hardware purchase or code merges.** The full watch and canonical research state are documentation updates only.

**Next strict cutoff starts after 2026-10-18 00:40:26 UTC.**

## Core source receipts

- https://huggingface.co/nvidia/Qwen3.8-Flash-Next-FP4-Local
- https://huggingface.co/nvidia/Qwen3.8-Flash-Next-NVFP4
- https://www.reddit.com/r/LocalLLaMA/comments/1x6vqft/fp4_qad_quant_of_qwen38flashnext_from_nvidia/
- https://github.com/Niko1221/Strata/issues/2956
- https://huggingface.co/Maximilian228/Qwen3.8-Flash-Next-NVFP4-GPTQ-Strata
- https://github.com/Niko1221/Strata/pull/2964
- https://github.com/Niko1221/Strata/pull/2963
- https://github.com/Niko1221/Strata/pull/2995
- https://github.com/Niko1221/Strata/pull/2952
- https://github.com/Niko1221/Strata/pull/2962
- https://github.com/Niko1221/Strata/pull/2989
- https://github.com/Niko1221/Strata/pull/2985
- https://github.com/Niko1221/Strata/pull/2986
- https://github.com/Niko1221/Strata/pull/2993
- https://github.com/Niko1221/Strata/pull/2965
- https://github.com/Niko1221/Strata/pull/2959
- https://github.com/Niko1221/Strata/issues/2960
- https://github.com/Niko1221/Strata/issues/2948
- https://github.com/incoai/splash/pull/469
- https://github.com/incoai/splash/pull/470
