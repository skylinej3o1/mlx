# Project 51 — Seeded Discovery Scratchpad: Oct 29 17:15 EDT

**Last reconciled request cutoff:** **2026-10-29T21:15:12Z**, paired [immutable watch](./RESEARCH-WATCH-2026-10-29-1715.md) and exact identical [LATEST](./RESEARCH-WATCH-LATEST.md). Triage **3F+2N+3E+2A+I** (Fit, Novelty, Evidence, Actionability, independent confirmation 0–3 each; heuristic, NOT quality/performance score). **Safety > score**. Human HIGH approval required before any proposed model/hardware test, CI mutations, sync or automated tuner.

## Objective and machine constraints

Source **ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO IQ3_S** custom mixed transformer3.0/3.2/3.4/3.6bpw with **oQ5e/BF16 oracle**, **oQ4e speed fallback**, separate PLE/ngram+MTP+QSA/GDN/HC precision. Two SEPARATE M1Max32GPU/64GiB native Metal true128K TG>=40 coldPP>=425 and true262K TG>=35 coldPP>=400, 3–5 correct long-lived coding/tool xhigh agents with parked state and AA-like>=38. Owner RTX5070Ti16GB+CoreUltra7265F+64GB DDR5 Linux Basalt and RX6800 NONXT gfx1030 16GB VRAM **ONLY16GB HOST RAM** (not 128GB). Hardware reports on different GPUs never upgrade numerical goals.

## Ranked active leads (12 max)

| Priority / Lead / F,N,E,A,I / total | Seed | Best disconfirming next evidence |
|---|---|---|
| **SAFETY 0 RS-24** 2,3,3,3,0/**27** | [Basalt #121](https://github.com/jesdga95/basalt/issues/121), real 5070Ti low-bit unpack wrong on optimized Windows CUDA | Test owner's exact Linux compiler/flags and original IQ3S tensor map; MMQ AND MMVQ vs independent double, source QA tools, output parity; don't infer all OS affected. |
| **SAFETY 0 RS-25** 2,3,3,3,0/**27** | [Basalt #130](https://github.com/jesdga95/basalt/issues/130), sub160SM GDN width dependence; [#132](https://github.com/jesdga95/basalt/issues/132) dense GEMM width | Physically T1/3/5/8, profile on/off and timing-dependent spec; compare hidden GDN state and full logits with static expert placement; read docs disagreement, fix tests. |
| **SAFETY 0 RS-26** 2,3,2,3,0/**24** | [Basalt #139](https://github.com/jesdga95/basalt/issues/139), 2×5070Ti late token0 after expert loan; [main 159ac](https://github.com/jesdga95/basalt/commit/159ac3c197f7f58d70436041186d62cd8b671cd9) | Full soak across concurrent cold prompt + existing decode; reclaim/loan valid expert index, independent output sentinel. No proof merged commit fixes this specific bug. |
| **HIGH RS-27** 2,3,3,3,0/**27** | [Strata #4602](https://github.com/Niko1221/Strata/pull/4602), 7 fully measured arms, dual/single RX6900XT original IQ3S, gfx1030 | Owner RX6800 only16GB HOST vs reporter128GB: actual model + cache + PLE resident feasibility, ROCm detect, single 4/16/128K semantic xhigh eval, isolate switches rather than confounded arms. |
| **HIGH RS-28** 2,3,3,3,0/**27** | [oMLX merged #4954](https://github.com/jundot/omlx/pull/4954), QFN oQ4e eight 160–204K sessions M3Ultra | Original source IQ3S on M1Max64: measure finish/rollback pool spikes, correct tool-agent outcome, 1–4 active vs 3–5 parked, benchmark full wall and swap; MTP on 55→64 10min turns is not certified M1. |
| **HIGH RS-29** 2,3,2,3,0/**24** | [Basalt disk conversation commits](https://github.com/jesdga95/basalt/commit/93f1d2643524bb55d167a698fd528bedde3bcfcc), [Strata #3565](https://github.com/Niko1221/Strata/pull/3565) | Reversible exact latest GDN/QSA+indexer/MTP/PLE atomically persisted across tool turns and crashing, explicit session ID not SHA1(first question); actual resume latency, disk budget/FS correctness. |
| **HIGH RS-17** 2,3,3,3,0/**27** | [Physical M1Max64 adaptive MTP #4935](https://github.com/jundot/omlx/issues/4935) | Original IQ3S no-spec vs adaptive vs fixed plus full 3–5 agent completion; single no-spec faster than adaptive, fixed c4 ~58 vs plain123 on DIFFERENT Qwen3.6 quant. |
| **HIGH RS-11** 2,3,2,3,0/**24** | [Strata PLE RAM cache 8GB lost #4518](https://github.com/Niko1221/Strata/issues/4518) | Full source M1 unified PLE/weights/stream KV/park+in-flight peak accounting; no default always-pin PLE without agent revisit result. |
| **HIGH RS-20** 2,3,2,3,0/**24** | [oMLX calibrated actual forward #4930](https://github.com/jundot/omlx/pull/4930), [TensorFold dense mixer #1617](https://github.com/ashhart/TensorFold/issues/1617) | Source original model per tensor sensitivity and frozen multilingual/code/ref logit tools at matched true bytes; gfx1151 mix5 22% code gain but only56.1% greedy match, no oracle KL. |
| **HIGH RS-19** 2,3,2,3,0/**24** | [Basalt host KV #117](https://github.com/jesdga95/basalt/pull/117), current main and #114 | Owner5070Ti true131/262K deep cold/warm and1/2 agents after parity baseline; one5080 +4.7% decode/-3.8% cold read and hostRAM pin1.74GB, off with parallel. |
| **MED RS-30** 2,3,3,3,0/**27** | [Basalt FP8 prefill #129](https://github.com/jesdga95/basalt/pull/129) | +15.28% PP at131K RTX5080 but KL .02191→.02667; test conservative precision, actual xhigh code completion and BF16 KL before considering optional speed tradeoff. OPEN, not approved. |
| **MED RS-21** 2,3,2,2,0/**22** | [vLLM ROCm QSA MXFP4 #64123](https://github.com/vllm-project/vllm/pull/64123), [#64405](https://github.com/vllm-project/vllm/pull/64405), [FP8 #61529](https://github.com/vllm-project/vllm/pull/61529) | Hardware MI355X only, +51% token capacity no c1 gain, quality pending; source M1 and gfx1030 KVarN not implemented. |

## Next three seeded discovery trails

1. **RS-24/25/26 correctness**: inspect true Basalt low-bit unpack and verification-window code lineage; crosscheck llama.cpp identical GGUF output and newer Basalt repair commits; prioritize RTX5070Ti Linux exact vs Windows MSVC compiler behavior, GPU type-specific parity and reference-validity pitfalls (#119 no dump, #136 false fused arm, #133 aborted suite). Investigate independent developer confirmations with timestamps.
2. **RS-27/20 native AMD**: pull linked [Vop3p tuning notes](https://github.com/Vop3p/dual-6900xt-flash-next-tuning/blob/main/docs/linux-dual-6900xt.md) and source revision for each arm; measure RAM/PLE actual host and ROCm gfx1030 support vs owner's RX6800 **16GB host**; independent AMD hardware/creator time/size controls. Separate FP8/MTP precision from exact model.
3. **RS-28/29/17 agent persistence**: compare oMLX #4916→#4936→#4954 vs Basalt core conversation_store and Strata auto_sessions → analyze GDN/QSA/indexer, agent-tool history, longest-row finish, ragged rollback, crash after save; propose complete source M1 long-agents HIGH protocol and fail-safe semantics.

## Source graph additions and counterchecks

- **Physical 5070Ti optimized CUDA wrong byte alias** [Basalt #121](https://github.com/jesdga95/basalt/issues/121); **physical 5080 speculative T-width inconsistency** [#130](https://github.com/jesdga95/basalt/issues/130); **quant test invalid comparator** [#136](https://github.com/jesdga95/basalt/issues/136); **late expert relocation poisoned output** [#139](https://github.com/jesdga95/basalt/issues/139). Source compiler/pack/OS vary; do not merge conclusions into blanket unsupported.
- **Original model near owner RX6900XT** [Strata #4602](https://github.com/Niko1221/Strata/pull/4602) **fresh**, same gfx1030 but more CUs and **128GB host**; [#3073](https://github.com/Niko1221/Strata/pull/3073) created Oct18 newly updated on HIP simt2, do not redateless retitle.
- **Baseline exact original quant** [ISTA-DASLab original](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF); **different older coder pruned Oct17** [Coder](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF), do not conflate with benchmark. ByteShape/ShapeLearn source-like map still not verified new.
- **Native persistent state** [Basalt commit93f1](https://github.com/jesdga95/basalt/commit/93f1d2643524bb55d167a698fd528bedde3bcfcc) vs [oMLX batch inplace4954](https://github.com/jundot/omlx/pull/4954) and [llama.cpp GDN draft rollback31350](https://github.com/ggml-org/llama.cpp/pull/31350); confirmation limited to independent mechanisms, NOT same backend equivalence.
- **Fast yet lossy** [Basalt #129](https://github.com/jesdga95/basalt/pull/129) RTX5080 original IQ3S FP8 131K +15.28% PP KL degradation; [TensorFold #1617](https://github.com/ashhart/TensorFold/issues/1617) gfx1151 oQ4e mixer5 code +22% but greedy 56.1%, no source oracle.

## Negative and deprioritized / debt

1. **Numeric targets unchanged**: no owner source QFN IQ3S actual 128K/262K cold PP/TG, no M1 long-agent quality / multi-Mac transfer, no real KVarN K4V3 fused M1, no source AA-like38 evaluated.
2. **Original source quant search**: no confirmed new ISTA source optimized QFN ShapeLearn/ByteShape tensor-map publish or AREX-to-QFN quant in checked public HF and code; listing recency ≠ revision.
3. **RX6800 no standalone 16GB host original IQ3S evidence**: 2×6900XT+128GB may be physically infeasible on owner's host. Do not project PP/TG.
4. **GPU correction may be compiler-specific**: Basalt #121 Win/MSVC not yet Linux GCC + CUDA; no claim Linux CUDA broken until tested.
5. **Reasoning semantics**: fast output full of token0 with 100% MTP acceptance = failure, not performance. Need task completion, tool audit, output-class sentinel, judge calibration.
6. **Performance precision tradeoff**: +15% PP with mixed FP8 not oQ5e-quality by default; +22% code HIP mixer5 lacks BF16 KL and long xhigh tasks. Do not replace BF16 comparator.
7. **Parked state correctness**: original GDN+QSA+PLE+MTP source snapshots, atomic file writes, interrupted checkpoint and last acknowledged tool boundary no M1 proof.
8. **Safety**: previous cross-client SSE and argument-truncation risks persist, plus new parity no-ops. No autonomous mutation or new scheduler or hardware purchase approved.

**NEXT HARD BOUNDARY (read via LATEST before next turn): 2026-10-29T21:15:12Z.**
