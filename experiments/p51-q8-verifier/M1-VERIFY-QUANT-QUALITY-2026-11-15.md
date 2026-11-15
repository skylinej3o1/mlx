# M1 verify kernels and quality-per-byte frontier — Nov 15 2026, 10:49 EST

## Status and scope

Research-only evidence card. Window 2026-11-15T14:32:00Z→15:49:00Z minute-resolution. [Full dated watch](./RESEARCH-WATCH-2026-11-15-1049.md). No owner device action and no replacement of original ISTA-DASLab GSQ-RCO IQ3_XXS minimum.

## 1. Fresh source: oMLX 6/8-bit M1 verification qmv

[PR #5304](https://github.com/jundot/omlx/pull/5304) created 14:39:22Z OPEN. Source says `m1_verify_qmv` was already specialized for 4/5 bit; adding 6/8-bit eligibility for 2–4-row verification. 16 weights/lane produce respectively 3 or 4 packed words, aligned; 5-row route remains MMA. Projections fewer than 1024 output columns excluded. Source device: **M1 Ultra**, not 2021 M1 Max. Local per projection over four shapes, fp16/bf16: 6-bit gain 0 to36% at2 rows,21–61% at3,9–48% at4; 8bit 0–13% at2,14–42% at3,20–57% at4. Per-call values are **best of 15** on a busy system.

End-to-end measured only **Qwen3-4B-Instruct-2507-6bit**, MLX0.32.4, fresh `--no-cache` server, 256 new token streaming, 8 rounds; branch A already includes #5276, B adds #5304. Aggregate concurrent throughput bf16 two123.5→160.5 (+30%), three138.4→184.9 (+34%), four144.3→204.1 (+41%); fp16 two137.4→174.3 (+27%), three147.6→205.6 (+39%), four150.5→213.6 (+42%). Outputs hashes match except cold-start A empty response in one cell. Per-projection fp16 max difference ~4e-3 vs stock; NOT bit-identical. No multi-row MTP verification or DFlash result, no RAM/TTFT or coding task quality on QFN/dense27B, no M1Max exact test.

**Owner implication:** High-quality dense27B Q5/Q6/Q8 may benefit if the same path applies, but app-level PP/TG of original GSQ QFN cannot be extrapolated. Only a controlled on-device test could establish gain, provided quality and correct tool calls pass.

## 2. Updated old source: oMLX M1 MMA verify attention

[PR #5300](https://github.com/jundot/omlx/pull/5300) created 12:47Z before strict cutoff; [14:42Z CI comment](https://github.com/jundot/omlx/pull/5300#issuecomment-6896277908) fixes hook-leak test. The already-described kernel applies during armed verify only, 3–8 rows, `KVCache` plain, width128, fp16/bf16; M1Ultra median9 interleaved runs. Four-query attention: 4096 keys6.58→3.04ms;16K keys25.85→9.67ms. Whole 4B forward ratio only0.94/0.87 at4096 keys rows4/8;0.89/0.84 at8192, with no end2end MTP token-per-second benchmark. Reordered fp32 summations can diverge greedy text, even when oracle tolerances pass. Source QFN QSA and physical128–262K unknown. Not eligible for performance projection without quality control.

## 3. Fresh dense 27B on M5 Pro, not old M1

[Kapitsa PR #1276](https://github.com/nace-ai/kapitsa/pull/1276) created 14:58Z OPEN: `NI_QMT_MIN`17 vs64 for 27B plainMLX4 on M5Pro48GB. 26,45,63-row cache-turn prefills 208–301→150–173ms; no cold4K prefill gain (5076–5091 vs5082ms), decode 17.6–17.9 unchanged. Controlled random prompts and 192-record 0 top1 flip with tiny KL; not actual coding task and **M5 silicon matrix path not available M1**. This supports a *turn-size* benchmarking methodology only.

## 4. Older mixed-precision quantization research newly surfaced

[llama.cpp #15550](https://github.com/ggml-org/llama.cpp/pull/15550), original 2025, OPEN. Chooses per-tensor quant formats by sampled dequantization error weighted with importance matrix, prunes Pareto-dominated choices then solves bit budget through Lagrangian selection. Authors report 93% of 238 evaluations/34 models meet or improve KLD versus standard quant, at an extra 5–10x quantization time and with resumable state. **Not QFN exact model.** KLD is a proxy; no BF16 distribution, long-context coding task, PLE split and MTP quality matched to ISTA original GSQ.
 
Question: can a future original-QFN-specific allocation move more bits to sensitive QSA/GDN/expert regions, preserve PLE and MTP, and deliver IQ3_S coding quality at XXS resident bytes? This is a *falsifiable research hypothesis*, not a recommendation to replace source quants. First identify GGUF tensor coverage, expert/tensor support and stable PLE provenance. Without BF16 KL/top1/tool/task A/B, HOLD.

## 5. Agent correctness is the governing score

[Kapitsa #1231](https://github.com/nace-ai/kapitsa/issues/1231) reports 27B:kquant Pi v1.5.2 loops on M4Pro48. New 14:48Z comment requests effort-level logs; unresolved, cannot attribute to quant or engine. [Strata #6032](https://github.com/Niko1221/Strata/pull/6032) open parser-recovery PR addresses malformed tool call envelopes and JSON but no live model test, new 15:00Z Linux keepawake CI issue. Need same full coding task suite: pass rate, tool JSON typed validity, persistent stream restarts, dead loops and time-to-correct-finish.

## 6. Verification gate for hardware tests (requires separate HIGH)

Fix model source hash+per-tensor quant origin, tokenizer/template, occupied128K and259K, drafts MTP ON vs DFlash2 ON with identical task, 1/2/4 agent streams, per-task correct outputs and wall clock, tool-call semantic/JSON validation, BF16 KL top1 and memory. Record cold JIT, warm prefill, numerical drift and concurrency rather than only best tok/s. No experiments performed in this research update.
