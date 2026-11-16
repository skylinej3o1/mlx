# November 16 Project 51 — Qwen4 launch, Relay helper0.1.5, M1 Max, dense27B fidelity

**Evidence interval:** 2026-11-15T17:52:37Z→2026-11-16T13:48:42Z. This document is a focused desk-research receipt, not permission to execute anything on owner machines. [Full strict watch](./RESEARCH-WATCH-2026-11-16-0848.md).

## 1. First-party Qwen4: what actually changed

[Alibaba Nov16 Qwen4-Max announcement](https://www.alibabacloud.com/en/press-room/alibaba-unveils-qwen4-max) and [QwenCloud dated release log](https://docs.qwencloud.com/changelog/models) confirm the production Qwen4-Max API and Nov11 preview separately. Model: 2.4T total sparse MoE, 71B activated per token, 1M context, native vision, reasoning/tools. Smaller-scale Qwen4 models **will be released as open weights** per written first-party commitment. Press announcement does **not name exact small models or dates**. Conference-reported Flash/Plus/27B tiers and 35B-A3B tester speculation are separate evidence categories; not an official parameter announcement. Claimed Work360 35% fewer tokens high effort /60% average task cost reduction are internal vendor eval. No official Qwen4-Flash or Qwen4-27B weight config/manifest/license at strict cutoff. Qwen3.8 Flash-Next architecture preview does not establish future Flash's total or posttrained-vs-new checkpoint.

For owner 2×2021 M1Max64: this **raises the probability of some compact open Qwen4**, but cannot justify buying hardware, reserving a given quant or changing inference targets without real tensor files, licence, maximum memory residency and coding-agent quality.

## 2. Relay-adjacent concrete progress

[oMLX helper #5316](https://github.com/jundot/omlx/pull/5316), MERGED Nov16 09:43Z, helper0.1.5. Primary actual M3Ultra host + DGXSpark helper, QFN oQ4e (not original GSQ GGUF). Three distinct fixes:

1. Host had cached 3D MRoPE position states; helper expected 2D text positions, causing prefix hits to run locally. Host now emits2D; helper accepts legacy3D.
2. Freed MLX allocations persisted in helper cache up to memory limit; cap at1GiB and clear per job. DGX Spark after3×99K requests free3.8→40GiB.
3. 3-bit expert gather used grid-z one block/route and failed above65,535; patch grid-x allows81,920 routes bit-equal.

99K PP v0.1.4 1,827→0.1.5 1,826, **flat**, and 25K2014→2000. Do not claim 10× prefill; 40GiB is *free memory* recovered, not 40GiB extra GPU VRAM or model residency. Higher memory headroom may make more useful work feasible but no tested improvement on owner 5070Ti16.

Prior oMLX CUDA helper #5163 already had Mac→CUDA partial layers; still open: 5070Ti16 selected-layer residency, full QSA KV/indexer and GDN recurrent state, PLE weights, MTP/draft continuation, correct sampling and actual TTFT end-to-end. [oMLX #5287](https://github.com/jundot/omlx/issues/5287) explains quadratic QSA append copies at high context; closing issue does not prove #5316 changed algorithm; inspect before forecasting. [oMLX #5288](https://github.com/jundot/omlx/issues/5288) Auto loaded47 helper layers but ran~31, fixed32 used ~16GiB less; doc/status update is not source-backed automatic fix. [TensorFold #3565](https://github.com/ashhart/TensorFold/pull/3565) source export/import is DeepSeek V4.1 draft host tests, not QFN product. [Splash #778](https://github.com/incoai/splash/pull/778) QFN RAM-only continuations store recurrent/draft/KV state with synthetic tests but no running engine path or cross-host handoff. These are promising mechanics, not Relay parity.

## 3. Old M1 current reality

[Paperniuk Splash #66](https://github.com/paperniuk/splash/pull/66), OPEN from Nov15 19:44Z, proposes self-calibrated pair for dense27B MLX4. Device M1Max 32GPU32GB (not 64GB source QFN); threshold769 rows after which pair becomes worthwhile; 1024-row TTFT4.704→4.067s,1536 6.891→5.768s,2016 9.082→7.543s, 14,096 cold67.75→57.16s. One short 480-row slightly worse, 17/19 responses same, both different greedy long outputs. Startup calibration ~71s after shaders compiled and additional278MB pair memory; max auto context 172,025→163,833 for this 32GB configuration. **Not shipped** and no comparable exact 64GB QFN GSQ 128/259K result.

[Paperniuk Splash #63](https://github.com/paperniuk/splash/issues/63#issuecomment-6909558187) Nov16 06:50Z new commenter >12h without the old ~24h decay after release1.6.1-m1.1. This is good early field feedback, not a fix proof or full24h soak. The issue remains OPEN. Paperniuk DS4 m1-flash-next has no strict-window commits. Historical pristine GSQXXS true physical128K PP278/TG34.2,259K PP258/TG31.7, near57GiB resident holds unchanged.

## 4. Dense27B same-bytes GPTQ 4bit and real coding-agent replay (REDISCOVERED OLD)

[mlx-community GPTQ Qwen3.8-27B](https://huggingface.co/mlx-community/Qwen3.8-27B-GPTQ-4bit) originally created around October26 (not Nov16 new weights); author sady4850, originally personal repo redirected. Same layout and model architecture as MLX standard4 group64, 497 language matrices GPTQ with bf16 Hessian calibrations119×2048; embedding and vision tower unchanged. No extra working set: ~15GB same size and same Splash speed.

Author compares BF16 reference using both GPU torch and Splash M1Pro. On **Splash same model/quant/KV and same 2K windows**: wiki KL baseline RTN0.0562 vs GPTQ0.0399; chat RTN0.1906 vs GPTQ0.1002; top1 flips chat13.13%→9.05%, wiki9.58→7.49%. 127 verify cycles23.05→23.00s. On same evaluation Unsloth UD-Q4KM16.5GB chatKL0.0831 but verify25.60s; GSQ dense27B IQ3_S11.8GB chatKL0.2121 verify29.40s. These are **not inter-model comparable quality rankings**, and KL is a proxy.

Independent contributor ghisguth M2Max Splash1.4 coder replay **78 turns physically32K–124K context** comparing separate Q4 checkpoints to Q8 reference; same tool calls+arguments plain31% GPTQ44%, same tool choice79→83%, argument similarity0.88→0.92, no broken calls. Q8 vs itself same exact calls82%, so there is stochastic/determinism baseline; **44% not a pass rate**, no vision, coding task success or controlled 128K owner M1 work. This is the highest-quality older found quant candidate for exact same memory. Its paper/weights are not a fresh Nov16 event. More robust quality-per-byte may permit 27B Q5 with headroom, but only live agent testing can establish.

## 5. DSpine and exact-vs-approximate verification

[vLLM #67094](https://github.com/vllm-project/vllm/pull/67094) OPEN from Nov11, updated in this strict window, includes real H10080 BF16 Qwen3.8-27B + Tencent five-layer DSpine b16, 15 draft tokens, concurrency8, xhigh, prefix-cache OFF. Acceptance per response vs pooled GSM8K6.927/5.902, HumanEval5.712/5.216, MBPP5.909/5.149, MTBench4.693/4.134 T0. It is a developer's real acceptance check, NOT a speed or correctness claim for 5070Ti16 solo, Apple7, Q5 or Basalt (its #360 request closed without implementation). [Splash #776](https://github.com/incoai/splash/pull/776) RFlash relaxed acceptance opt-in may change sampled output distributions, **cannot be a lossless agent baseline**; leave native MTP and DFlash2 original GSQ comparisons exact.

## 6. CPU IQ3 FAST and why safety blocks it

[Strata #6085](https://github.com/Niko1221/Strata/pull/6085) OPEN, on Ryzen9600X Zen5 AVX512 VBMI, in-register IQ3_S gate/up throughput18.1→58.6GB/s, XXS21.4→56.6GB/s, full QFN decode mean22.43→21.45ms/token (noise overlap). Independent commenter Nov16 13:39Z reproduced AVX2-only Ryzen5975WX SIGILL before main even with STRATA_IQ_FAST=0 because new translation-unit initializer executes unsupported AVX512. **Must fix dispatch before run or merge; user CoreUltra7 265F cannot be inferred compatible.** User frozen Basalt and CPU double-quality remain unchanged.

## 7. Agent/caching correctness

[oMLX #5312](https://github.com/jundot/omlx/pull/5312) MERGED: if max active requests2 but benchmarking8, waves counted as parallel and aggregate TG overreported 4× on one SmolLM2 test; actual benchmark needs admitted concurrency. [Strata #6034](https://github.com/Niko1221/Strata/pull/6034) OPEN disk spilled parked agent 751MiB serializer with independent HIP 19/22 restores and TTFT84.7→9.9s, but a new check finds stale budget accounting after corrupt spill is refused; no exact owner GPU source. [Splash #778](https://github.com/incoai/splash/pull/778) synthetic recurrent/draft RAM continuation for multi-agent lane suspension, not deployed. [Qwen Code history fix #15959](https://github.com/QwenLM/qwen-code/pull/15959) prior turn causal restoration remains Molt pattern.

## 8. Recommendations, NOT executed

Only desk research authorized: watch official Qwen4 HF configs, inspect CUDA helper0.1.5 QSA cache cost, monitor #63 full 24–48h and #66 API rollout, analyze GPTQ independent agent suite and compare to Nace KQuant. HIGH needed before any model download, owner device run, code modifications or software installation. Frozen Basalt first PC RTX5070Ti16+64GiB sourceGSQIQ3_S v2 true32K INT8KV spec1 no draft; owner RX6800 nonXT host16GiB. Two Macs separate 64GiB. No changes to target speeds.
