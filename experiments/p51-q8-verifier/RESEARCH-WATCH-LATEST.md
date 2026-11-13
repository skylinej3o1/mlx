# Project 51 strict research watch — 2026-11-13 06:39 EST

Previous cutoff 2026-11-13T02:55:44Z; new strict cutoff 2026-11-13T11:39:08Z. Primary GitHub issue sweep Kapitsa, Basalt, Splash, oMLX, Strata. FRESH and UPDATED distinctions. No hardware experiments, model downloads, code/CI/config changes. No exhaustive Hugging Face quant inventory or Qwen4 release verification in this pass.

## HIGH FRESH — Strata dual RTX5060Ti GSQ IQ3S at 200K configured
[Strata #5909](https://github.com/Niko1221/Strata/issues/5909), created 2026-11-13T07:52Z. Two RTX5060Ti16, ~63GB RAM, Strata engine0.1.59, original GSQ QFN IQ3S, DFlash2 spec6, KV INT8, configured204800, one slot. Short decode median79.5 TG; 4K PP838.4, TG66.4, TTFT4.92s; 16K PP1599.7, TG72.8, TTFT10.27s. 12/12 sanity checks passed including tools, but 6/9 performance requests hit 512-token reasoning+answer cap. Context 200K configured, NOT tested 200K actual. Different two-GPU topology from owner 5070Ti single GPU; no Relay measured.

## HIGH FRESH — Strata RTX5090 GSQ IQ3S 173.6 short / 222.9 agent decode
[Strata #5906](https://github.com/Niko1221/Strata/issues/5906), created 07:44Z. RTX5090 32GB, 64GB RAM, 262K configured, single slot, engine0.1.59, T=0 thinking off. Short decode173.6, agent followup decode222.9 tok/s; fresh16K PP6674.1, TTFT2.42s. Agent test only ~13.6K last turn, 64 output cap, 69.7% cache hit, no correctness test. Not a long-context agent quality proof or apples-to-apples 5070Ti.

## HIGH FRESH — M1 Ultra 35B concurrency activation precision tradeoff
[oMLX #5227](https://github.com/jundot/omlx/issues/5227), created 06:52Z. M1Ultra128GB Qwen3.6-35B-A3B, oMLX0.8.0rc1, MTP/draft off. Two concurrent requests vs solo sequential: 6-bit FP16 activations -4 to -9% short, 6-bit BF16 +11 to+18%, 4-bit BF16 +30 to+37%; long contexts worsen. But FP16 absolute solo 105–111 TG vs BF16 71–78 TG; FP16 concurrent aggregate ~100 vs BF16 ~85. BF16 concurrent greedy differs from solo, FP16 matched. Not M1Max, not QFN. Supports per-node scheduling tests and two independent nodes.

## MEDIUM FRESH — Basalt parallel scaling limited when experts in RAM
[Basalt #347](https://github.com/jesdga95/basalt/issues/347), created 07:29Z. RTX PRO6000 Blackwell96GB+253GB RAM QFN Q8_0 experts 70% VRAM/30% RAM. Concurrent 1=206.3 aggregate TG, 4=347.4, 8=434.4 (2.11x), per-request at8=54.3. GPU-window-only estimates overstated end-to-end. Not owner topology; useful for HaikuSwarm worker throughput vs latency.

## MEDIUM UPDATED — Splash Muse-style experiments did NOT translate
[Splash #759](https://github.com/incoai/splash/issues/759) and [#760](https://github.com/incoai/splash/issues/760) updated Nov13: real dense27B B1 whole-cycle GPU66.20ms, preparation0.034ms (~0.05%), gate/up38.7%. Previously -4.86% component prep time translated only +0.14% request tok/s. Synthetic static 3-dispatch -43–46% component time but production 27B/35B 12-variant screen no merge-ready gain; 18/56 non-regression,38 failures. No M1 throughput upgrade; draft PRs remain drafts.

## MEDIUM UPDATED — oMLX M1 Ultra/old Apple kernels
[oMLX #5087](https://github.com/jundot/omlx/issues/5087) describes Qwen4-named fused attention kernels falling back on M1 due 1024 threadgroup >896. Naming does not prove open Qwen4 release. [#5143](https://github.com/jundot/omlx/issues/5143) M1 Ultra MTP verify threadgroup limits. No confirmed fix in this scan.

## Retained Project 51
Two independent M1Max64, RTX5070Ti16+64GB desktop, secondary RX6800. GSQ IQ3XXS minimum, IQ3S preferred. Basalt first PC test frozen pristine original GSQ IQ3S, true32K, INT8KV, one slot, spec1 NO DRAFT, PLE numerical parity and agent task acceptance. Owner approval HIGH before tests. Relay CUDA prefill→Metal decode state format and recurrent-state parity unproven. No verified new official Qwen4/4.5 Flash-Next checkpoint in this scan; do not claim comprehensive release audit.

NEXT STRICT CUTOFF 2026-11-13T11:39:08Z.
