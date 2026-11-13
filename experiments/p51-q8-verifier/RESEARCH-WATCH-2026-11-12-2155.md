# Project 51 strict research watch — 2026-11-12 21:55 EST

Previous strict cutoff 2026-11-12T16:15:53Z; new strict cutoff 2026-11-13T02:55:44Z. GitHub primary source issue sweep of Kapitsa, Basalt, Splash, oMLX and Strata, plus public web spot-check. FRESH = created after cutoff; UPDATED = older issue updated after cutoff. Not an exhaustive HF quant inventory or Qwen model release audit. No hardware experiments, installs, code, CI or config changes.

## CRITICAL CORRECTION — Basalt #334 earlier alarm INVALIDATED
[Basalt #334](https://github.com/jesdga95/basalt/issues/334) **UPDATED** Nov13 01:20Z. Original 14/24 Basalt vs 0/12 Strata output-ceiling disparity was **invalid**: unequal output ceilings (400–900 vs ~4700 tokens). Matched retest Basalt **15/24** vs Strata **13/24** finish:length; empty final **10/24** vs **12/24**, p=0.77. No evidence of Basalt-specific regression. Keep tool turn-completion as general acceptance test, remove engine-specific red flag.

## HIGH FRESH — Kapitsa DFlash2 verify numerical drift on M1 Max
[Kapitsa #1234](https://github.com/nace-ai/kapitsa/issues/1234) created Nov12 18:38Z. Ornith1.5-35B-A3B and Qwen3.6-35B-A3B plain vs drafted T=0 output differs on all 3 prompts each; each arm repeatable. M1Max32 teacher-forced step vs verify 8 windows*24 rows: Ornith top1 agreement **0.9896**, KL mean **6.99e-4**, max abs logit diff **2.38**, 2 flips; dense Qwen3.5 4B 1.000 top1, KL7.30e-7. M4Pro reproduced; quality impact unknown, no direct QFN GSQ result. Correctness and agent-task gate mandatory before claiming lossless draft.

## HIGH FRESH — Strata GSQ IQ3S vs Unsloth UD-IQ4XS + Q8 PLE field report
[Strata #5881](https://github.com/Niko1221/Strata/issues/5881), Nov12 18:55Z. 2xRTX3090 24GB, Strata local engine0.1.59.1, ISTA/DASLab QFN GSQ IQ3_S with standalone Q8_0 PLE, 64GB host RAM, complex tuned split. Cold 25.7K prefill ~910→2120–2330 tok/s (2.2–2.4x); decode ~100–110 tok/s, real chat median ~101–102. Small MMLU GSQ IQ3S vs Unsloth UD-IQ4XS statistically tied, Unsloth math arm NOT run, no coding-agent head-to-head; PLE difference confounds inference. Not directly comparable to 5070Ti or single M1.

## HIGH FRESH — Basalt RTX5070Ti16 + 64GB RAM startup issue
[Basalt #339](https://github.com/jesdga95/basalt/issues/339), Nov12 18:05Z. RTX5070Ti16 + RTX5060Ti16, Ryzen9800X3D, 64GB RAM, official NVFP4-DQ8 QFN pack, Basalt0.3.2 524K with vision dynamic. Default 2048MiB RAM reserve OOM-killed after RAM copy 2/2; 5120 reserve starts but all requests stall 30s RAM guard. Basalt0.2.1 reportedly serves 170–260K same host. Not owner's single GPU GSQ IQ3S true32K spec1; still warn transient RAM and startup guard.

## MEDIUM FRESH — Splash microkernel optimization limited end-to-end
[Splash #759](https://github.com/incoai/splash/issues/759) M5Pro preparation packing four tasks yields ~4.86% held-out component GPU time reduction, whole model tok/s +0.14% only, no TTFT gain. [#760](https://github.com/incoai/splash/issues/760) static 3-dispatch ~43–46% component GPU time reduction vs 8 dispatch on held-out synthetic; whole-model throughput unmeasured. No M1/QFN gain established.

## MEDIUM FRESH — Radeon RX6800 long-context Strata reliability
[Strata #5892](https://github.com/Niko1221/Strata/issues/5892) Nov13 01:01Z, RX6800 16GB gfx1030 +62GB RAM QFN IQ3XXS 256K, engine0.1.59, five prompt-read no-progress self-kills and one verify timeout under real 32K–137K agent prompts, silent respawn and full re-prefill. Relevant to owner's secondary RX6800 machine, not proof same behavior with different CPU/RAM/driver.

## LOW FRESH — Kapitsa dense27B Q5 KQuant Pi looping anecdote
[Kapitsa #1231](https://github.com/nace-ai/kapitsa/issues/1231) single unquantified user report of Pi1.5.2 infinite looping on M4Pro48 with 27B KQuant0.2.35. No reproducible controls, cannot attribute to quant.

## Qwen4 and Relay
No verified official downloadable Qwen4 Flash-Next/27B/35B model in this spot-check. Flash-Next posttraining Qwen4/4.5 hypothesis remains speculation. Relay CUDA→Metal KV+recurrent state transfer unproven; original GSQ XXS historical 128K PP278/TG34.2, 259K PP258/TG31.7, quality floor XXS, preferred IQ3S. Keep frozen Basalt first run pristine original GSQ IQ3S, true32K INT8KV one slot spec1 no draft, parity + tool quality, HIGH owner approval before actual hardware actions.

NEXT STRICT CUTOFF: 2026-11-13T02:55:44Z.
