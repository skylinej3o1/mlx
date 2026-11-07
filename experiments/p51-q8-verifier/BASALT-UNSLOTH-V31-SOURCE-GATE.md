# Project 51 — Basalt Unsloth Dynamic3.1 versus source GSQ: quality, distribution & owner-first PC blocker

## November 7 2026 07:18 EST — 28.8GB common PLE controls quality comparisons

[PLE artifact note](./QFN-CROSS-QUANT-PLE-SHARING-2026-11-07.md) · [strict watch](./RESEARCH-WATCH-2026-11-07-0718.md) cutoff 2026-11-07T12:18:52Z. FRESH [Strata #5479](https://github.com/Niko1221/Strata/pull/5479) original ISTA 2-shard source `per_layer_token_embd.weight` PLE shard2 and Unsloth v3.1 4-shard PLE shard4 IQ4NL payload have matching SHA; split.count/no metadata differs, draft loader exemption enables hardlink same28.8GB tensor across 2/3/4 model splits; one on-hardware Strata0.2.11 generation reported. This is **source PLE payload immutability**, not equal transformer/model quality, not an independently verified Apple Metal loader, and no saving of active KV or source IQ3S 64GB safe RAM; saves **disk and download bytes** per extra quant if loader supports. Original pristine GSQ IQ3S formerly official .basalt v2 still supply blocked absent older verified copy, unchanged user frozen first-PC requirement. Prior Basalt-source 100×512 WikiText2 BF16 KL (UD2XS .183 vs GSQXXS .240, UD3XXS .119 vs GSQS .150) not xHigh task success; compare exact common PLE, source BF16 oracle and long tool outcomes after HIGH, no auto Unsloth substitution. No source pack changes executed.

**Cutoff:** 2026-11-07T04:34:41Z. [Strict watch](./RESEARCH-WATCH-2026-11-06-2334.md) · [tensor fidelity](./QUANT-TENSOR-FIDELITY-2026-11-06.md) · [Basalt first PC](./BASALT-FIRST-PC-PLAN.md). **Research only. No authorization to download, convert, bench, install, CI or change owner model.**

## 1. Critical provenance: Basalt publisher has removed frozen official original-GSQ packs

[Basalt maintainer comment](https://github.com/jesdga95/basalt/issues/240) at2026-11-07T01:05:49Z and [commit658ef41e](https://github.com/jesdga95/basalt/commit/658ef41e7774e6a0e44ffaa9f0835d94374be06a) say official `jesdga/Qwen3.8-Flash-Next-Basalt` repository now ships **UD-IQ1_M** instead of GSQ Q2_0, **UD-IQ2_XS** instead of GSQ IQ3_XXS, **UD-IQ3_XXS** instead of GSQ IQ3_S. The three previous original GSQ *.basalt files **removed** from publisher's current distribution. Author says the source model is closer BF16 at comparable size. This is **new distribution and new measured comparison**, NOT novel Unsloth quant weights (Dynamic3.1 Nov4). Latest tagged Basalt **v0.3.0**, source main contains changes; no v0.3.1 tagged yet.

The original [ISTA-DASLab source GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) is independent and has NOT been declared removed. User's **immutable first-PC contract** is **pristine original ISTA GSQ IQ3_S from previously official .basalt v2**. It is **supply-blocked** if no preverified offline original pack exists; no user local inventory access and don't assume one exists. No replacement/quant/convert/test approved. Conversion of untouched original GGUF via official Basalt converter using suitable original vision/MTP/PLE sections, with verified SHA and byte-equivalent tensor checks, is a possible **future owner HIGH-approved** path, but creates a newly sourced pack not equal to old published SHA. This requires fresh approval to change the frozen artifact contract, even if model tensors match; do not silently replace by Unsloth.

## 2. Maintainer same-hardware direct KL/logit and speed comparison

[Primary issue 240 comment](https://github.com/jesdga95/basalt/issues/240) posted01:05Z, **100 chunks WikiText-2×512 each, BF16 full model reference, RTX5090 at400W + RTX5060Ti180W, INT8 KV**. Same existing official Basalt benchmark harness; a KL/PPL evaluation set **is not the imatrix used during quantization**. PPL ≠ KL closeness. Speed 1 cold stream, tok/s separately for prose/chat/structured; do NOT compare to separate 575W/one5090 experiment.

| Old source GSQ → new UD | Old size → UD GiB | Old KL → UD KL | old BF16 top1 → UD top1 | old prose/chat/structured → UD |
|---|---:|---:|---:|---:|
| Q2_0 → UD-IQ1_M | 65.6→67.1 | .433→.256 |78.24→83.19%|421/463/826→364/434/732|
| IQ3_XXS → UD-IQ2_XS|74.4→74.4|.240→.183|84.03→86.21%|374/427/698→345/396/641|
| IQ3_S → UD-IQ3_XXS|81.6→81.6|.150→.119|87.56→88.67%|344/405/662→342/399/658|

**Meaning:** at same packaged 74.4GiB/81.6GiB, UD v3.1 appears closer to BF16 **logits** than old GSQ source in this test; source IQ3S relative KL improvement ~20.7%, UD2 vs XXS ~23.8%. Three categories of output speed slightly/slower, not a free TG uplift. No individual high-stakes coding task success, true 128/262K, memory trace, external replication, M1 Apple7/Metal quant support, end-to-end Qwen PLE accuracy or exact per-tensor embedding breakdown provided in the comment. Publisher describes smarter but correctness not measured. Must not assume BF16 KL guarantee hard xHigh coding quality or that IK3 bit labels correspond quality ranks.

## 3. Native format fix: eliminate untracked one-tensor requant workaround

Before [issue267](https://github.com/jesdga95/basalt/issues/267) `UD-IQ2_XS` native `blk.4.ffn_down_exps` Q5_0 disabled the planned route-tail for all48 layers, causing4–8% of experts to cross PCIe. Contributor on OTHER RTX5060Ti saw65TG unmodified,84TG if Q5_0 requantized to IQ4NL,94TG original GSQXXS. **That modified GGUF is NOT an original UD quant**.

New source main [commit201e37e](https://github.com/jesdga95/basalt/commit/201e37e1a329d36bcfcaa6148a7adc6c2bb5bdd2) 22:56Z adds Q5_0 down native grouped decode and MMQ, as well as [K2/K3 expert code](https://github.com/jesdga95/basalt/commit/65a91428559), maintainer confirms original **unmodified** UD-IQ2XS now converts and runs optimized. No new post-fix physical same-box TG or 5070Ti result. Native support on CUDA engine main not native M1 Metal.

## 4. Source-level BF16 embedding question is related but separate

Earlier [Strata #5433](https://github.com/Niko1221/Strata/pull/5433) UD-IQ4XS compressed input embeddings IQ4XS 322MiB vs BF16 1212MiB, 244/4995 top1 flips KL.02602, +890.4MiB host under Radeon R9700 pinned map without VRAM. This does **not** establish original GSQ input embedding type or free Apple unified memory. For a fair IQ3XXS ↔ UD-IQ2XS and source IQ3S ↔ UD-IQ3XXS test, explicitly inventory `token_embd.weight`, BF16 PLE IQ4NL/SSD semantics, dense/MTP/vision, LoRA/merged tuning or other tensor differences. A "just use higher bits on input table" recommendation without artifact/oracle is a hypothesis.

## 5. First-PC immutability and future FAIR quality experiment (proposal only)

- **Gate A: provenance**: identify previously official GSQ IQ3_S `.basalt` v2 artifact SHA from publisher or previous owner copy. If unavailable, STOP rather than substitute Unsloth. Separately request HIGH approval before creating/repackaging an original ISTA GSQ IQ3_S .basalt v2 from unchanged source GGUF and compatible original MTP/vision sections.
- **Gate B: source sameness**: paired full model BF16 oracle logits (random/controlled samples, teacher forced code/docs/agent, 16K/32K/128K/262K actually OCCUPIED), expert formats, PLE ngram fidelity, sentence-level tool JSON, output refusal/truncation artifacts, identical thinking settings/MTP and draft acceptance, original vs new version hashes.
- **Gate C: task performance**: heldout multi-file coding fixes, unit tests passing on filesystem, tool execution completeness, xHigh long-session recovery and persistent agent state, both per-agent correctness and multiagent aggregate throughput. Compare same-bitrate **source original GSQ IQ3XXS vs UD-IQ2XS**, and **source original GSQ IQ3S vs UD-IQ3XXS**. Do not use final output token match alone; no benchmark contamination or cherry-pick.
- **Gate D: physical**: 2021 M1Max32GPU64 Native Metal long 128/262K residency/swap, true PP/TG and TTFT, SSD table reads, cold vs warm, 2 Mac independent vs pipelined rank; owner Linux RTX5070Ti16 original GSQ IQ3S first32K/int8KV/spec1 before introducing any UD competition. Difference in backend features or specialized bit formats is a real deployment dimension.
- **Gate E: switch policy**: no minimum quality floor relaxation, no model promotion until quality+operational acceptability proven. User may later choose to make Unsloth new official floor, but NO silent change through a repeated research scan.

**Status:** original first-PC package SUPPLY BLOCKED IF NO PRE-VERIFIED COPY, not observed hardware failure; original source quant remains available and user contract unchanged. No owner action conducted.
