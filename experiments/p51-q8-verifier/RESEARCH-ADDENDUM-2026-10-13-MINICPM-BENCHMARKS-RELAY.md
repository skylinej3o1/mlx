# User-supplied MiniCPM-V 4.7 benchmarks and Relay prefill/decode reminder
Recorded: 2026-10-13 02:46 EDT, as a **user-supplied benchmark-image interpretation**, not a new freshness scan.
Previous formal research hard boundary remains **2026-10-13 06:13:56 UTC**, in `RESEARCH-WATCH-LATEST.md`.
Sources: screenshots supplied by user from the OpenBMB MiniCPM-V 4.7 announcement, OpenBMB's official checkpoint comparison chart; upstream https://github.com/OpenBMB/MiniCPM-V and https://github.com/jundot/omlx/pull/4496 .

## 1. General/agent benchmark table — important, do NOT omit in later summaries

Score columns in official image: MiniCPM-V4.7 **35B-A3B**, Qwen3.6 **35B-A3B**, Qwen3.6 **27B**, Qwen3.8 **27B**, Gemma-4 **31B**. **All instruct-mode, public reports plus vendor local evaluations with official checkpoints.** Not a common evaluator, decoding, prompt/cost/quant or xhigh apples-to-apples test.

| Category / test | MiniCPM 35B-A3B | Qwen3.6 35B-A3B | Qwen3.6 27B | Qwen3.8 27B | Gemma4 31B |
|---|---:|---:|---:|---:|---:|
| Knowledge CMMLU | 90.21 | 89.34 | 89.52 | 87.66 | 79.76 |
| Knowledge MMLU-Pro | 83.45 | 84.11 | 84.52 | 82.40 | 84.43 |
| Knowledge SuperGPQA | 61.23 | 63.37 | 63.71 | 60.41 | 62.23 |
| Instruction IFBench | 47.67 | 35.33 | 44.67 | 43.67 | 54.33 |
| Math AIME26@avg16 | 76.46 | 74.17 | 80.42 | 76.04 | 76.88 |
| Coding LiveCodeBench-v6 | 56.57 | 54.29 | 59.05 | 63.62 | 71.24 |
| Tool call BFCL-v4 | 60.06 | 60.20 | 60.66 | 63.72 | 61.96 |
| Agent tool task τ²-Bench | **84.65** | 79.65 | 79.70 | 66.90 | 67.35 |

**Interpretation:** MiniCPM τ² **84.65 vs Qwen3.8-27B 66.90** is +17.75 points, but BFCL **60.06 vs 63.72** and coding **56.57 vs 63.62** favor Qwen3.8. Strong candidate for *tool-agent/multimodal specialist* test, not proven winner for complex coding; test exact same harness/versions and xhigh-or-tool settings.

## 2. Vision benchmark table (same vendor graphic, 4x and 16x visual compression)

Rows show MiniCPM **4x / 16x**, then Qwen3.6 35B-A3B, Qwen3.6 27B, Qwen3.8 27B and Gemma4 31B. Baseline competitor compression fixed at 4x,4x,4x,9x respectively. Higher is better except MMHal-Hallrate (lower better). Publish full provenance and correct names before benchmarking.

| Metric | MiniCPM 4x | MiniCPM 16x | Qwen3.6 A3B | Qwen3.6 27B | Qwen3.8 27B | Gemma4 31B |
|---|---:|---:|---:|---:|---:|---:|
| MMBench | 91.72 | 90.87 | 86.76 | 85.11 | 85.91 | 89.63 |
| MMStar | 80.67 | 80.13 | 76.00 | 74.40 | 75.13 | 76.47 |
| MMT-Bench | 75.47 | 75.12 | 72.53 | 73.58 | 72.82 | 75.73 |
| SimpleVQA | 54.14 | 51.41 | 54.40 | 52.75 | 50.81 | 52.24 |
| MMMU | 80.22 | 80.00 | 77.44 | 78.44 | 76.00 | 75.33 |
| MathVista | 88.00 | 87.30 | 84.40 | 84.40 | 84.40 | 78.50 |
| MMMU-Pro | 69.71 | 67.66 | 69.88 | 69.97 | 69.74 | 64.02 |
| MathVerse_MINI | 86.45 | 84.80 | 82.74 | 81.88 | 84.37 | 75.58 |
| MathVision | 74.24 | 72.93 | 74.24 | 75.03 | 78.22 | 69.28 |
| OCRBench | 91.20 | 90.40 | 86.00 | 86.80 | 83.90 | 85.40 |
| OCRBench_v2 | 68.47 | 65.67 | 66.50 | 65.49 | 63.95 | 54.14 |
| OmniDocBench_v1.6 | 94.24 | 93.25 | 80.17 | 82.14 | 80.36 | 79.17 |
| CharXiv_Reasoning | 75.60 | 69.20 | 67.50 | 68.50 | 70.70 | 65.00 |
| CCOCR | 81.14 | 78.29 | 82.33 | 82.34 | 82.49 | 76.91 |
| TextVQA_VAL | 84.99 | 81.72 | 83.98 | 81.31 | 79.60 | 81.21 |
| BLINK | 70.33 | 68.12 | 66.91 | 66.65 | 67.81 | 69.33 |
| MMSI-Bench | 16.00 | 15.20 | 10.70 | 9.00 | 10.90 | 18.70 |
| Hallusion-Bench | 63.83 | 64.42 | 62.06 | 62.35 | 60.98 | 61.65 |
| MMHal-Score | 4.72 | 4.67 | 4.96 | 3.17 | 5.03 | 4.18 |
| MMHal-Hallrate (lower better) | 21.88 | 22.92 | 25.00 | 21.88 | 21.88 | 27.08 |
| RefCOCO | 90.93 | 89.61 | 90.97 | 90.91 | 88.77 | 81.47 |
| ScreenSpot | 86.99 | 85.01 | 92.94 | 90.73 | 93.31 | 83.75 |
| MM-IFEval | 65.41 | 64.62 | 62.85 | 65.77 | 68.03 | 69.59 |
| Video-MME without subtitles | 76.40 | 74.70 | 75.70 | 70.20 | 73.40 | 74.10 |
| LongVideoBench | 68.90 | 67.60 | 63.10 | 67.70 | 60.90 | 60.70 |
| MotionBench | 68.12 | 68.02 | 67.87 | 69.11 | 65.11 | 62.67 |

**Planning interpretation:** MiniCPM 4x leads on OmniDocBench and OCRBench; surprisingly strong 16x retention in some tasks but CharXiv, TextVQA and ScreenSpot decline; **ScreenSpot Qwen3.8 27B 93.31 vs MiniCPM 86.99** is a warning for precise GUI clicks/coordinates, even though τ² favors MiniCPM. Routing by *task-specific tests* (OCR vs GUI grounding vs multi-turn tool use), not aggregate leaderboard. MiniCPM 4x/16x refers **visual tokens**, not direct 4x/16x wall-clock performance or 4x/16x runtime RAM savings. Video scores are model-side, but local mlx-serve PR #834 only implements image input and returns HTTP400 for video.

## 3. Relay clarification — CUDA prefill is the intended complement to M1 decode

The **architectural goal** is `RTX 5070 Ti CUDA prefill (PP) -> precise portable model+session state transfer -> independent M1 Max / MLX Metal decode (TG)`, keeping two Macs free for independent stateful coding agents. The new oMLX #4496 strengthens the *decode endpoint*: author reports Qwen3.8-27B DFlash2 block8 greedy decode M1 Max64G at 17K=40.4 TG, 67K=33.7, 133K=24.2. For Qwen3.6-35B-A3B MTP3 reported 17K=93.2, 34K=81.3, 67K=54.7. **They are one Mac, greedy, author tests, not production xhigh or our exact Swift quant.** Baseline switches speculative scheme for Qwen3.8, so gains cannot be assigned only to kernels.

Critical: fast Strata *Flash-Next* prefill on 5070 Ti does **not** automatically transfer to dense Qwen3.8-27B, Qwen3.6-35B-A3B or MiniCPM-V 4.7. CUDA prefill and MLX decode must be the **same checkpoint architecture, compatible weights/quantization/numerics**, identical token/media preprocessing and rotary positions, with complete and properly mapped attention KV, GDN recurrent/conv, QSA/indexer, hyperconnections, draft/MTP ownership and committed frontier. Verify exact state oracle and output distribution; no shortcut by copying KV tensors alone. Need compatible CUDA *dense or VLM model* prefill engine, not simply repurposing Flash Strata.

User's critical point: **Relay solves prefill bottleneck**. The M1 Max decode rates are end-goal for agent continuations; slow Mac cold PP can be bypassed if (and only if) CUDA→Metal prefill state transfer correctness, throughput and total wall-time break-even are demonstrated. Stage practical independent Mac agent serving first; then harness-level expert checkpoint, followed by Relay. Include state transfer/warmup/setup, resident memory and latency in strict cost model:
`TTFT_relay = CUDA_prep + CUDA_prefill + state_serialize + network_transfer + MLX_import + verifier_setup + first_decode`,
compare with `TTFT_local = MLX_local_prefill + first_decode`. Do not substitute theoretical 40Gbps Thunderbolt line rate or GGUF size for measured transport or checkpoint volume. For repeat turns, retained prefix state may be cheaper than repeated relay handoff. For two independent Mac agents, relay may need replicated target-state copies; never count KV-prefix shared resident across Macs absent explicit transport+ownership.

**Priority:** Compare actual per-Mac 27B sampled-quality decode, warm/cold PP, 128K context, tool errors and memory. Prototype serialized CUDA→Metal state for a minimal matching model and verify no numerical drift before offering fleet-scale Relay throughput. Do not shift canonical P51 target numbers without exact hardware tests. No new hardware buy recommended.
