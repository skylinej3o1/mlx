# Project 51 — Seeded Discovery Scratchpad (October 30 07:22 EDT)

Verified cutoff **2026-10-30T11:22:56Z**. Immutable evidence [2026-10-30-0722 watch](./RESEARCH-WATCH-2026-10-30-0722.md), identical [LATEST](./RESEARCH-WATCH-LATEST.md). Five scores F,N,E,A,I each0..3, priority heuristic **3F + 2N + 3E + 2A + I** /33 (no probabilistic interpretation). Safety/cross-client correctness overrides rank.

## Fixed objective and hardware

**ORIGINAL ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO IQ3_S**, custom heterogeneous3.0/3.2/3.4/3.6 BPW (aim source-like xhigh ~3.3–3.6), separate PLE/ngram/MTP/HC/GDN/QSA, frozen **oQ5e/BF16 quality** comparator and **oQ4e speed** fallback; two distinct **M1Max32GPU 64GB**, original actually occupied128K TG>=40 coldPP>=425 /262K TG>=35 coldPP>=400, 3–5 independently restorable correct xhigh tool-agents + AA-like>=38. Owner RTX5070Ti16/CoreUltra7265F64GiB DDR5 Linux, RX6800nonXT gfx1030 16GB VRAM/**ONLY16GB HOST DDR4**, GTX1080 8GB Pascal. Never transfer other quant/model/SoC measurements to owner as evidence.

## Top 12 source-seeded leads

| Priority + ID; F,N,E,A,I / total | Primary seed and exact status | Next falsifier / human-HIGH gate |
|---|---|---|
| **SAFETY RS-24**,2,3,3,3,0 /27 | [Basalt #121](https://github.com/jesdga95/basalt/issues/121) optimized CUDA low-bit wrong RTX5070Ti Win MSVC; still OPEN | Actual owner Linux original-source per-tensor MMQ/MMVQ and decode-once parity vs independent FP64; make sure both original quant tensors and actual compiler differ; do not assume Linux affected. |
| **SAFETY RS-25**,2,3,3,3,0 /27 | [Basalt #130](https://github.com/jesdga95/basalt/issues/130), new OPEN [#155](https://github.com/jesdga95/basalt/pull/155) T1..8 fix still spec4/spec8 output different from prompt folding, OPEN [#157](https://github.com/jesdga95/basalt/pull/157) prompt GEMM width fix | Test same original source+tokens T1/3/5/8 and short prefill boundary, reference logit rows and actual early state; don't mistake window-rounding fix for entire whole-response determinism. |
| **SAFETY RS-26**,2,3,2,3,0 /24 | [Basalt #139](https://github.com/jesdga95/basalt/issues/139) two5070Ti 1500-request expert loan token0; still OPEN | Live per-expert index and cached payload parity, long soak+rollback sentinel, avoid "100% MTP" success claim when garbage produced; single owner5070Ti distinct. |
| **HIGH RS-31**,2,3,3,3,0 /27 | **FRESH MERGED [oMLX #4971](https://github.com/jundot/omlx/pull/4971)** long session M3Ultra QFN oQ4e, peak185.3→153GiB MTP off/177→158.2 on; 44GiB bank growth issue | Exact M1 source IQ3S memory when joins/finishes/MTP ragged rollback, 1/2/4 active +3–5 parked; per-layer temporary pool, OS wired, output-class and full coding results. |
| **HIGH RS-32**,2,3,2,3,0 /24 | **FRESH OPEN [oMLX #4970](https://github.com/jundot/omlx/pull/4970)** GDN sidecar partial-prefix SSD write amplification: ~49MiB each regardless tail; 58GB/1209 files/day | Distinguish 256-token/twice-seen partial admission from full first sight + existing durable; checkpoint durability, cold next turn and SSD TBW vs agent cache hit. |
| **HIGH RS-33**,2,3,2,3,0 /24 | **FRESH OPEN RFC [vLLM #64725](https://github.com/vllm-project/vllm/issues/64725)** LeapQuant 16-token replay INT8 GDN; QFN MI355 TP2 state57.9→25.7MB, decode-step1.08–1.13x, no MTP | Repeat against *per-window BF16* and FP32 exact original reference at true128/262K, 16token fold + NaN/race/flush and all xhigh tool-judge gates; native Metal not written, speculative disabled. |
| **HIGH RS-34**,2,3,2,3,0 /24 | **FRESH OPEN [Basalt #149](https://github.com/jesdga95/basalt/pull/149)** streamed checkpoint write/read under low RAM: 100K reread17.8sec→~1s restored on 5080 | Owner5070Ti64GiB actual low RAM/pressure store under 1GB peak, 122K/262K byte-exact restore, crash corrupt file, committed tool turn; compares REFUSED disk restore not normal fast restore. |
| **HIGH RS-35**,1,3,2,2,0 /20 | **FRESH [TensorFold #1661](https://github.com/ashhart/TensorFold/issues/1661)** actual QFN 261K gfx1151/192GB HIP inexact, MTP71.28 TG serial34.20, coldPP1489 | Quality/layer parity data at 261K, compare model4bit vs source GSQ and 192GB vs owner16GB host, no transfer to M1/6800 or source xhigh. |
| **HIGH RS-36**,1,2,2,3,0 /21 | **UPDATED OLD [TensorFold 2-Mac Qwen27 #1437](https://github.com/ashhart/TensorFold/pull/1437)** greedy single slot, no drafter/grammar/cache; older M4 Pro pair receipt pre-rebase, no M1 | True owner two M1Max over TB4 actual decode/PP and link failure only with separate approved 27B test; source QFN cannot reuse stack as-is for independent 3–5 agents. |
| **HIGH RS-17**,2,2,3,3,0 /25 | [M1Max64 adaptive c4 #4935](https://github.com/jundot/omlx/issues/4935), different Qwen3.6 oQ4e; [new open #4977](https://github.com/jundot/omlx/pull/4977) M3Ultra Qwen3.6 dense +57% c16 | Exact original IQ3S/no spec/adaptive/fixed MTP, agent complete tool quality, per-request fairness and memory; 16 active client scale NOT owner64GB certification. |
| **HIGH RS-20**,2,2,2,3,0 /22 | [oMLX correct forward #4930](https://github.com/jundot/omlx/pull/4930), [Hadamard QFN loader #4864](https://github.com/jundot/omlx/pull/4864) updated, [OptiQ wrong norm #4960](https://github.com/jundot/omlx/issues/4960) fresh different Qwen3.5 | Freeze source transformer/QSA/HC/PLE+MTP tensor-map and norm/basis conventions; matched bytes and xhigh coding judge instead of speed or greedy agreement only; account for +1 gamma and rotated states. |
| **HIGH RS-27**,2,2,3,3,0 /25 | [Strata original IQ3S dual/single6900 gfx1030 #4602](https://github.com/Niko1221/Strata/pull/4602), **FRESH adjacent [#4696](https://github.com/Niko1221/Strata/issues/4696)** 6700XT gfx1031 Win source DIFFERENT IQ3XXS F16 prefill16K +91% | Physical RX6800 nonXT only16GB HOST RAM feasibility first; source original fit not established, cannot extrapolate 64/128GB windows/ROCm packages from other devices. |

## Top 3 future deep dives (falsifiers, not authorization)

1. **RS-24+25+34 5070Ti safety/persistence**: trace Basalt #121 after Oct30 code status and exact actual Linux compiler ISA parity; #155 k_mid8 vs residual spec4/8 prompt folding; #157 cuBLASLt width algorithm; run identical frozen QFN source short/deep logs if HIGH-approved; #149 restore state hash from 100K under actual OS pressure and token history/latest acknowledgment.
2. **RS-31+32+33 native agent memory**: compare oMLX #4916→#4936→#4954→#4971 batch banks, sidecar ~49MB per unique short prefix #4970, ReplaySSM/LeapQuant source GDN resident checkpoint 57.9→25.7MB on MI355; split nominal/peak/persisted memory, true 128K/262K each QFN source M1 and 3–5 independently restorable tool/coder tasks; paper BF16-per-window nonlossy baseline and MTP impossible currently.
3. **RS-35+36+27 hardware transfer**: TensorFold 261K HIP gfx1151 192GB user wants full context, evaluate exact quant/inexact policy and lack of source fidelity; two-Mac 27B greedy-only and pre-rebase M4 receipt; AMD RX6700XT official Windows gfx1031 confirmed but not owner Linux RX6800 16GB host.

## Negative controls and scope debt

- No verified new source-original ISTA QFN GSQ-RCO IQ3S ShapeLearn/ByteShape same-release tensor map; ISTA DeepSeek V4.1 recent activity != QFN; separate source Coder pruned October17 != original source, Reddit Oct24 Coder8GB != original.
- No original QFN on two M1Max64 at actually occupied128/262K with frozen code/tool quality, no native Metal K4V3 with MTP/durable state, no multihost QFN Metal Relay with same-state correctness.
- No exact RX6800 nonXT16GBVRAM/**only16GB HOST** original GSQ IQ3S long-context stable serving, do not propose speed upgrade until fit+OS verified.
- 261K HIP is DIFFERENT 192GB unified GPU/MLX4 quant and `numerics=inexact`; cannot port into 5070Ti or M1 budget.
- TensorFold two-Mac 27B pair is 4bit dense and only greedy1 no prompt cache/grammar/drafter; old M4 pair acceptance pre-rebase; loopback correctness no network test.
- 62–78x M1 tile_qmm [#1590](https://github.com/ashhart/TensorFold/pull/1590) **OLD-created Oct29 09:53** LFM2 previously pathological kernel, NOT source QFN M1 78× speed.
- Recurrent-state low-rank quant is not KV main/indexer compression; GPT agent quality source oracle remains oQ5e/BF16 and no approval for unsafe lossy route biased or FP8 prefill.
- Same hardware repeatable first token and active/parked memory must be tracked, not Python response code saying200, cached tokens, or optimistic reference file.
- System controls: no seed-run automation, no unapproved model download/benchmark, no CI or setup change. **PROPOSED→HIGH-APPROVED→RUNNING→RESULTS→AWAITING-HIGH-REVIEW**.

**NEXT STRICT FRESHNESS BOUNDARY: 2026-10-30T11:22:56Z.**
