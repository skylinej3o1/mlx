# Project 51 — Ranked Discovery Scratchpad — October 31, 2026, 07:45 EDT

**Last maintained:** October 31, 2026. **Strict hard cutoff:** 2026-10-31T11:45:10Z. [Detailed dated watch](./RESEARCH-WATCH-2026-10-31-0745.md), [identical LATEST](./RESEARCH-WATCH-LATEST.md). Previous cutoff 2026-10-30T20:16:33Z. Score = 3F+2N+3E+2A+I (0–3 inputs), a triage heuristic not probability. New MERGE of old PR does not date its older physical benchmark anew. Safety and correctness findings override scores.

## Fixed objective / device budget

Original **ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO IQ3_S**, transformer54.8GB and 28.8GB separately SSD-mappable ngram; two separate M1 Max 32GPU 64GB. True128K coldPP>=425 TG>=40 and262K PP>=400 TG>=35, 3–5 correct durable tool-using xhigh coding agents and source AA-like>=38. oQ5e/BF16 quality reference, oQ4e speed comparator; custom 3.0/3.2/3.4/3.6 transformer BPW candidates, PLE+MTP precision budget separately. Also RTX5070Ti16GB Linux+64GB DDR5, RX6800 nonXT gfx1030 16GB VRAM **ONLY16GB HOST RAM**, GTX1080 8GB. No matched owner long-agent run or numerical target promotion; HIGH approval before machine tests.

## Ranked 12 active leads

| Lead / score | Verified receipt + transfer limit | Next falsifier |
|---|---|---|
| **SAFETY RS-64 / 27** | [Strata #4787](https://github.com/Niko1221/Strata/pull/4787) FRESH OPEN: physical gfx1100 Windows HIP host-pinned GPU alias overlaps stack, causing fluent wrong-prompt answers; 5/70 bad unpatched versus0/70 repaired on same source | Reproduce with own engine build and independent prompt/model SHA, memory-map alias and start canary; Windows HIP only, not Linux RX6800 |
| **SAFETY RS-65 / 27** | [vLLM #64855](https://github.com/vllm-project/vllm/issues/64855) FRESH OPEN: native padded sparse indexer ragged spec writes incorrect weights and causal bounds; 4/6 mismatched tokens ROCm MI355X | Mixed decode lens [2,1,2,1] vs flattened reference, masked top-k, cuda source inspection alone not a physical CUDA repro |
| **HIGH RS-66 / 27** | [oMLX #4898](https://github.com/jundot/omlx/pull/4898) FRESH MERGED M1Max64 6/8bit g64 verify MMA; Qwen3.6-35B-A3B +18–24% over short coding prompts, g128 control flat | Inspect original GSQ IQ3S per-tensor 6/8bit+group64 and actual 5–16 verifier rows; frozen oQ5e/BF16 xhigh/128K/262K agent quality |
| **HIGH RS-67 / 27** | [oMLX #4988](https://github.com/jundot/omlx/issues/4988), [merged gate fix](https://github.com/jundot/omlx/commit/e05b7b6fc986b49338061b05b09f43d25160b390): revised QFN oQ4e 8bit GDN out_proj silently disables 5bit-only fused decode, M3Ultra 64K decode61.2 old→50.6 new | Same checkpoint post-merge and actual fused-per-layer trace, separate 29% extra weight bytes from dispatch; source M1 Gold eval |
| **HIGH RS-56 / 26** | [oMLX #4985](https://github.com/jundot/omlx/pull/4985) FRESH MERGED per-rank Engram SSD flags on M5Max128+M1Max32 DeepSeek V4.1, 94.6GB SSD per rank, M1 RSS15.3GB, ~50TG | QFN PLE distributed flag expressly NOT implemented, source M1 pair model/plan/hash, safe rank residency and full tool-state correctness |
| **SAFETY RS-46 / 27** | [Strata #4730](https://github.com/Niko1221/Strata/issues/4730) prior M4Max IQ3S Metal QSA checkpoint four-row vs CUDA three-row serializer, 24K park fails 50.65s re-read | Backend-versioned snapshot geometry, 24K vs66K and original M1 actual agent last acknowledged tool message; never bypass validation |
| **SAFETY RS-68 / 25** | [Strata #4761](https://github.com/Niko1221/Strata/pull/4761), [#4762](https://github.com/Niko1221/Strata/pull/4762) new parser repair attempts CLOSED UNMERGED; existing quoted tool calls and truncated file content still deployment risks; [mlx-serve merged hardening](https://github.com/ddalcu/mlx-serve/commit/c86e4b29a8f8532c993a6c6322ee351d897e04a2) | Tool examples never execute, writes byte-exact, strict grammar returns HTTP400 if unenforceable, streaming full prose, long-lived cache fallback |
| **HIGH RS-69 / 24** | [TensorFold #1702](https://github.com/ashhart/TensorFold/pull/1702) FRESH MERGED FlashNext MTP wide norm byte-identical; CUDA sm120 RTX PRO6000 microkernel4.67→1.75us, HIP gfx1201 22.21→4.36us | Full model end-to-end and source quant quality required, not RTX5070Ti or RX6800 measured |
| **HIGH RS-70 / 24** | [TensorFold #1733](https://github.com/ashhart/TensorFold/pull/1733) FRESH MERGED opt-in GB10 FP4 solo prompt chunk 31.7K TTFT16.05→14.78s but arriving short request wait0.36→1.94s and +5.86GB scratch | Compare 1 vs3–5 concurrent agents, tail latency and active MTP, not original IQ3S target |
| **HIGH RS-48 / 23** | [Strata #4780](https://github.com/Niko1221/Strata/pull/4780) FRESH OPEN physical RX6900XT Windows gfx1030 original IQ3S, one9.7K prompt PP869 /400 gen TG68.5; configured262K only | Owner RX6800 nonXT 16GB HOST feasibility, independent complete256K and xhigh agent tasks; no overprojection |
| **HIGH RS-71 / 23** | [oMLX #4853](https://github.com/jundot/omlx/pull/4853) UPDATED OLD QFN M3Ultra/M5Max multiagent +10–22% proposal CLOSED UNMERGED | Identify which individual kernel commits actually landed, same oQ4e revision and matched source long tasks; no phantom deployment claim |
| **SAFETY RS-55 / 25** | Prior [Strata #4736](https://github.com/Niko1221/Strata/pull/4736) one 0/12 sanity on startup, fluent wrong answers; new #4787 offers class-specific root explanation | Mandatory per-fresh-process semantic canary, preserve failure, do not assume same root for all runtimes |

## Deprioritized / closed and negative evidence

- New TensorFold v1.2.0 [release commit](https://github.com/ashhart/TensorFold/commit/a388876f41e), includes many unrelated model families and a new opt-in FlashNext CUDA path; no original source M1 full xhigh run.
- Strata QFN Windows RX6900XT benchmark above uses one tuned run and context **configured**262K, not 262K occupied. Previous Linux RX6900XT report had **78.5GB host** vs owner RX6800 **16GB host**.
- Strata 0.2.9 GDN default speedups on Linux CUDA and **gfx12 HIP**, not owner gfx1030; no source target promotion.
- vLLM #64855 distinct from prior vLLM #64758 Kimi-K3 cross-request NaN spread and prior Basalt token0 expert cache corruption; three independent mechanisms.
- Official ISTA [main tree](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/main) remains ed59f92, no new source-original improved ByteShape/ShapeLearn quant, AREX2 different model.
- No user physical native two-M1 original source 128/262K, no full source-like quality/completed 3–5 xhigh coding agents, no standalone owner RTX5070Ti Linux or RX6800 nonXT 16GB host source 128K.

## Next three seeded source trails

1. **M1 mixed-precision source fit:** #4898 bits/group route → #4988 QFN GDN revised 8bit layout + source ISTA per-tensor allocation → actual M1 eligible layers/quality vs oQ5e/BF16 and peak memory. Numeric speed only after HIGH approval.
2. **Native agent correctness:** Windows HIP #3431/#4787 vs source CUDA/Metal model startup and #4730 Metal checkpoint, plus still-unmerged parser fix attempts. Demand byte-exact tool call and non-fluent-false startup gates, no exception merely because response HTTP200.
3. **Cross-request state and scheduling:** vLLM #64855 mixed draft-length causal/batch indexer, #64758 nonfinite contamination and TensorFold solo-chunk latency inversion; future bounded 1/2/4 active, 3–5 parked agent and long uptime fairness battery.

**NEXT STRICT BOUNDARY: 2026-10-31T11:45:10Z.** Research only; no model downloads, benchmark executions, hardware actions, CI jobs, or tuning mutation approvals.
