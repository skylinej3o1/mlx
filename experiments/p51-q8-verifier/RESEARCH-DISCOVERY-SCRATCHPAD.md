# Project 51 — Ranked Discovery Scratchpad — November 5 2026 16:29 EST

**Strict watch:** [RESEARCH-WATCH-2026-11-05-1629.md](./RESEARCH-WATCH-2026-11-05-1629.md) · [LATEST](./RESEARCH-WATCH-LATEST.md) · [method v1.0](./RESEARCH-DISCOVERY-METHOD.md). Prior cutoff2026-11-05T17:51:18Z, new exact cutoff **2026-11-05T21:29:03Z**. Triage 3F+2N+3E+2A+I out of33 is source-priority heuristic, NOT measured confidence. Rank up to12 active leads, no transcript duplicates.

**Fixed floor:** Original GSQ QFN IQ3XXS min acceptable on one 2021M1Max32GPU64GB; physical DS4 actual128K278PP/34.2TG,259K258PP/31.7TG. Two independent M1Max64 original IQ3S truly filled128K >=425PP/40TG,262K>=400PP/35TG;3–5 independently correct xHigh coding agents AA-like>=38 UNMEASURED. First Linux RTX5070Ti16/64GB only original official GSQ IQ3S .basalt v2, one slot32K/int8KV/spec1 CPU-double and Codex correctness under HIGH. RX6800 nonXT16VRAM with ONLY16GB host RAM.

## Active ranked discoveries

| Priority/score | Source classification, exact seed | Next test / contradictory explanation |
|---|---|---|
| 1/30 RS-196 | PRIOR [QFN Unsloth3.1](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF) UD-IQ2XS75.8GB full/28.8GB PLE (~47GB weights), UD-IQ3XXS83.6GB; no independent original GSQ IQ3S-like xHigh quality. | Exact tensor format+hash, BF16/oQ5e oracle and heldout128/262K tools on M1 vs GSQ XXS/S, independent coding repetitions; quality floor hold. |
| 2/27 RS-213 | FRESH [Basalt0.3.0 release](https://github.com/jesdga95/basalt/releases/tag/v0.3.0)21:17Z multi-model preserves .basalt v2, **config migration breaking**; FRESH [Linux5080 original GSQ IQ3S #254](https://github.com/jesdga95/basalt/pull/254)16KPP4730/64KPP5045/192TG; prior Windows5080 #252 3976/4590/137. | Exact original IQ3S first Linux5070Ti when HIGH; benchmark flags/PCIe, source parity, tool semantics, config migration; do not infer OS causal performance. |
| 3/27 RS-215 | FRESH [Paperniuk Splash #49](https://github.com/paperniuk/splash/pull/49) M1Pro dense27B warm 72 prefill229→206s,128–255 new rows98→75s. Prior M1Max ANE crossover~388, so user transfer doubtful. | M1Max original QFN GSQXXS actual warm tool-turn 128–512-row crossover, ANE startup, deep128/262K and tool correctness; explicit HIGH. |
| 4/25 RS-214 | REDISCOVERED [Flint40B-A2.5B](https://huggingface.co/RecursiveSI/flint), [Q4K_M23.4GB](https://huggingface.co/ggml-org/Flint-GGUF), [mixed IQ3S16.5GiB](https://huggingface.co/minicx/flint-IQ3_S-mix-GGUF); FRESH [Strata Flint #5347](https://github.com/Niko1221/Strata/pull/5347) single RTX5060Ti 16GB claim pending review. | Potential M1 **secondary** coder at Q4, not source QFN replacement; validate n15 mini-suite vs contradictory PPL, actual262K and tool/QA on native Metal. |
| 5/25 RS-217 | FRESH [Strata #5345](https://github.com/Niko1221/Strata/pull/5345) new UD-IQ4XS-v31 16KPP2339 vs old2573, decode130 vs108 on heterogeneous Blackwell; **auto-tier K/PCIe settings explain apparent20% decode uplift**. | Matched placement K/PCIe, equal source/BF16 quality and useful long xHigh agent, no quant-speed claim. |
| 6/25 RS-216 | FRESH [Strata #5346](https://github.com/Niko1221/Strata/pull/5346) actual empty historical think block and dropped preserve_reasoning in multi-turn template, fallback fix OPEN and pack copy remains. | Serialized all3 API dialects, pack vs fallback, executed tools and agent quality; no GPU A/B. |
| 7/23 RS-218 | FRESH [Basalt DeepSeek BF16 gate](https://github.com/jesdga95/basalt/commit/6c9582e3f37a224477a0749d799507fd5907d07d) other model UD-IQ1M KL.278/top1 83.88 vs GSQ IQ2XXS .431/top1 79.97,100×512 on dual5090+5060Ti. | Source precision/calibration hypothesis only, ~242GiB pack can't fit; no user baseline substitution. |
| 8/22 RS-219 | REDISCOVERED [Ripple65B NVFP4 57.2GB](https://huggingface.co/ricursiveAI/Ripple-65B-Preview-NVFP4/tree/main); FRESH [llama.cpp support](https://github.com/ggml-org/llama.cpp/commit/fecdc81eec0922b229e7e6f4069cea603e10d6a7)18:55Z. | 57.2GB on64GB Mac leaves no working room; only dual real partition after hardware proof, publisher scores not direct QFN comparison. |
| 9/20 RS-220 | REDISCOVERED [Kimi-K3.1-Pro](https://huggingface.co/moonshotai/Kimi-K3.1-Pro),2.8T/104B active QAT MXFP4W/MXFP8A,1M, ~1.5TB. | Frontier method reference, no local fit; watch small variants. |
| 10/24 RS-209 | PRIOR [TensorFold1.2.3](https://github.com/ashhart/TensorFold/releases/tag/v1.2.3) M3Ultra simultaneous Flash Next MTP reply48→8sec, cache extra-mark fix rejected TTFT4.38→5.67; FRESH [short-first scheduler](https://github.com/ashhart/TensorFold/commit/91e4120b234804851fdf0cf1f58b073eac16403c) different27B Metal. | Real M1 QFN B1/B2/B4 mixed prefill/reply correct completed coding tasks, not just throughput. |
| 11/22 RS-221 | FRESH [antirez/ds4 #1321](https://github.com/antirez/ds4/pull/1321) M5Max DeepSeek expert hotlist steady19.8→26.2TG but6sec initial preseed; different model. | Count end-to-end startup/SSD wear and logits, no claim source QFN M1 gain. |
| 12/22 RS-206 | PRIOR actual source GSQ IQ3S cross-rank **two independent 2021 M1Max64** plus 128/262K retained GDN/QSA/PLE/MTP/agent state unproven; fused M1 1024>896 issue unresolved. | Physical rank split over TB4 with exact tool results and durable sessions after HIGH. |

## Deprioritized / negatives (max8)

- No fresh owner 2021 M1Max original GSQ IQ3XXS occupied128/262K long A/B or physically resident IQ3S one M1 at262K.
- No independent QFN UD3.1 IQ2XS equal-or-better than GSQ IQ3S full hard xHigh task-grade study; revised UD3.1 speed confounded by placement.
- No official Qwen4 released downloadable weights independently verified in strict window; qwen4exp means prior QFN architecture.
- Basalt DeepSeek UD1M~242GiB and Kimi~1.5TB beyond user fleet; Ripple NVFP457.2GB impractical single64GB.
- Flint custom mixed GGUF n15 coding score conflicts with smaller quant's perplexity; no production quality evidence.
- No user Linux5070Ti Basalt original IQ3S actual PP/TG or complete Codex tool correctness; other RTX5080 reports cannot replace.
- DeepSeek hotlist steady TG excludes~6sec seeding; M1Pro ANE gains unlikely to transfer to M1Max due crossover.
- No two equal M1Max true native long QFN distributed correct coding agent; RX6800nonXT ONLY16GB host unlike multiAMD analogues.

## Next 3 exploratory checks

1. Revision-hashed Unsloth QFN UD-IQ2XS transformer tensor map, source BF16/GSQ XXS/S actual equal-budget xHigh128/262K agent quality; probe native 2021 M1 g13 without owner execution.
2. Basalt0.3 original IQ3S v0.2.1 parity, Linux5080 #254 configs and repeated decoder context; proposed owner FIRST PC one 5070Ti original IQ3S v2 32K/int8KV/spec1 with CPU double/JSON tools only after HIGH.
3. M1Max short-tail ANE crossover vs M1Pro #49 and new Flint Q4K_M *separate secondary agent* as independent model fit/long QA research, never substitute QFN baseline.

**New source-map growth:** official Basalt0.3 release and DeepSeek BF16 pack; RecursiveSI Flint, ggml-org Flint GGUF, minicx mix, ricursiveAI Ripple NVFP4, moonshotai Kimi3.1 Pro. **Debt:** exact GGUF tensor indices/digests, M1 Metal Flint correctness, BF16 hard agents, true occupied vs configured context, OS wired+swap, long-lived checkpoint replay. **Next cutoff: 2026-11-05T21:29:03Z.** No HIGH approval or owner hardware/CI/model downloads.
