# External Qwen runtime watch — 2026-08-31

This note records external runtime/quantization evidence relevant to the P51/P69 exact-Q8 verifier work and the separate Qwen3.8-Flash-Next dual-Mac research plan.

These are upstream PR descriptions and community field reports, not measurements produced by this repository. Do not turn them into local performance claims without reproduction.

## Executive delta

- Qwen3.8-27B Layr-Labs MTP challenge frontier remains `3.7291100105909`; no new promoted result changes the P69 direction.
- Qwen3.8-Flash-Next runtime evidence improved materially again, especially for long-context MTP, warm agent turns, and M1-class hardware.
- The strongest new M1-specific field report shows a single M1 Max 64 GB running Flash-Next with SSD-streamed tensors/ngrams/MTP, custom sparse attention, and dynamic MTP at roughly 22 decode tok/s with MTP, while reporting roughly 150 prefill tok/s at 256K context.
- This strengthens the case that the eventual dual-M1 Flash-Next bottleneck is implementation/distribution quality rather than an obvious single-node compute wall. Distributed MTP is still unmeasured and remains the major uncertainty.

## Flash-Next: exact long-context MTP verification

Upstream oMLX PR #3320 (`perf(qwen4): flatten exact long-context MTP decode`) routes batch-one Qwen4 Lightning-MTP verify windows through bounded direct selected-block QSA above a measured crossover while preserving exact target verification.

Reported M3 Ultra 256 GB fixed-depth-5 results:

| Context | Decode-only |
|---:|---:|
| 10K | 85.6 tok/s |
| 50K | 74.4 tok/s |
| 100K | 71.8 tok/s |
| 150K | 70.9 tok/s |

The prior 150K path was about 59.4 tok/s, making the reported 150K improvement +19.3%. The direct-QSA verify path itself stayed near 71–73 tok/s from 20K through 150K, which is the important architectural result: verifier cost need not grow badly with context when the selected-block path is bounded correctly.

The same PR reports adaptive MTP at 220K around 53.15 tok/s with ~99% draft acceptance versus 26.37 tok/s MTP-off, with deterministic output-hash parity in its stated check.

Source: https://github.com/jundot/omlx/pull/3320

## Flash-Next: cached-drafter priming

Upstream oMLX PR #3328 (`perf(qwen4): prime verified MTP drafter from cached suffix`) addresses a warm-agent seam: the target backbone can restore a huge prefix while the memory-only MTP drafter lacks history.

Reported deterministic 100K restart case:

- 98,304 target prompt tokens restored from prefix cache;
- 1,668 exact suffix tokens used to prime the drafter;
- 97.6% draft acceptance;
- 5.32 committed tokens/target cycle;
- 60.35 tok/s decode;
- exact output hash matched the unmodified target result.

This is directly relevant to persistent-agent/Tameru-style compaction and restoration: large target-prefix reuse does not have to imply a long MTP cold-start penalty.

Source: https://github.com/jundot/omlx/pull/3328

## Flash-Next: latent Metal keepwarm for agent-turn gaps

New upstream oMLX PR #3330 (`perf(runtime): add opt-in latent Metal keepwarm`) adds a default-off bounded GPU pulse between cached turns. It does not mutate model weights, KV state, prompt state, sampling state, or SSD cache state.

Reported M3 Ultra 256 GB / Flash-Next oQ4e-MTP 220K agent-tool conversation results include:

- keepwarm OFF model TTFT after 5/15/60-second gaps: about 1.84 / 1.76 / 1.76 s;
- keepwarm ON repeated-turn model TTFT median: about 1.45 s;
- keepwarm ON after a 60-second gap: about 0.85 s model TTFT (visible-stream TTFT remained higher at 1.83 s in that run);
- B1 repeated decode median: 55.56 -> 58.79 tok/s;
- cold 4K prefill: 887.01 OFF vs 885.31 ON tok/s, effectively neutral;
- no cache repopulation after explicit hot/L0 clear in the stated validation.

This is not a throughput-transforming kernel change, but it is highly relevant to interactive coding-agent latency once cache restore and MTP priming are already good.

Source: https://github.com/jundot/omlx/pull/3330

## Flash-Next: M1 Max 64 GB field result

A fresh LocalLLaMA field report is unusually relevant because it is on the exact Apple generation/memory class of interest: M1 Max 64 GB.

Reported configuration:

- llama.cpp fork;
- SSD streaming for model tensors;
- SSD streaming for n-gram/PLE data;
- SSD streaming for MTP;
- custom Q4 quant assembled by tensor-level performance/quality selection;
- custom Metal sparse attention with near-linear context degradation;
- Q4_0 MTP reported to retain the same acceptance as the tested Q8_0 MTP at half the RAM;
- dynamic MTP draft sizing, including disabling speculation when context makes it negative.

Reported performance:

- ~180 tok/s 4K prefill without MTP;
- ~170 tok/s 4K prefill with MTP in the original note, with a later edit reporting ~185–190 tok/s after another optimization;
- ~150 tok/s prefill at 256K context;
- decode rising from ~12.9 to ~22 tok/s with MTP (~70% gain).

This is a community field report, not a controlled reproduction. Still, it is the first strong direct evidence in this watch that one M1 Max can run Flash-Next at useful full-context rates despite only 64 GB RAM by combining selective residency, SSD streaming, sparse attention, and MTP.

Source: https://www.reddit.com/r/LocalLLaMA/comments/1w296bx/qwen38flashnext_optimised_for_macs/
Fork: https://github.com/mihailescu2m/llama.cpp

## Flash-Next: quantization should be architecture/workload aware

Two independent lines now point the same way.

1. oMLX HOBBIT work (#3325) reports workload-profiled hot/cold expert precision allocation. The published PR data show meaningful decode gains for small perplexity penalties and also show that expert hotness changes substantially by workload/domain. That argues against a uniform-bit quant for an agent-specialized build.

2. Community Flash-Next quant work is converging on per-layer/tensor assignment rather than blanket bpw. A recent AP-GGUF release explicitly uses per-layer tailored quantization and reports 20–30 GB savings versus common Q4 builds at a similar perplexity band.

For our eventual build, the design implication is to preserve precision preferentially in architecture-sensitive regions and coding-agent-hot experts rather than spending bits uniformly. This is a research direction, not yet a local checkpoint.

Sources:
- https://github.com/jundot/omlx/pull/3325
- https://www.reddit.com/r/LocalLLaMA/comments/1w1ou8x/qwen38_flash_quants/

## Flash-Next: M1/M2 BF16 activation recast remains high priority

Upstream oMLX PR #3277 reports that M1/M2 hardware benefits from recasting BF16 non-quantized activation-side tensors to FP16 because BF16 arithmetic is emulated there.

Reported M1 Ultra / Flash-Next oQ4e-MTP results:

- rewrite decode: 28.29 -> 32.26 tok/s (+14.0%);
- novel decode: 22.89 -> 24.07 tok/s (+5.2%);
- prefill: 313.2 -> 500.2 tok/s (+59.7%).

This is particularly relevant to M1 Max reproduction. It should be isolated as its own A/B before combining it with distributed inference or new quantization.

Source: https://github.com/jundot/omlx/pull/3277

## Qwen3.8-27B external state

The Layr-Labs `qwen-3.8-mtp-challenge` frontier remains:

`3.7291100105909`

The newest visible candidate (#1481) is an unmeasured compiled-elementwise-fusion proposal without an Apple-Silicon local timing receipt. There is no newly promoted external result that should change the P69B13 selection or reopen closed verifier seams.

Source: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1481

A separate quantization development is worth cataloging but does not alter the exact-Q8 verifier campaign: GSQ+RCO 2.5–3.0 bpw GGUFs use learned scalar grids plus per-tensor constrained precision assignment. The architecture-level lesson again supports non-uniform bit allocation for future compact deployments.

Source: https://www.reddit.com/r/LocalLLaMA/comments/1w13vse/release_sota_ggufs_for_qwen3827b_gsqrco_at_25_to/

## Decision impact

### P69 / 27B exact-Q8 verifier

No change.

- Keep the P69B12 promoted stack and exact-Q8 ruler intact.
- Continue to P69B13 from existing profiling/census data.
- Do not reopen the explicitly closed P69B8/P69B9/P69B10-C seams on the basis of external challenge submissions.

### Flash-Next dual-M1 research

Evidence priority now looks like:

1. reproduce the single-M1 Max 64 GB baseline with MTP + selective SSD residency;
2. isolate the M1/M2 FP16-activation recast;
3. establish distributed target-only scaling before adding distributed MTP;
4. port/bound direct-QSA verify so long-context speculation does not inherit general-mask scaling;
5. profile coding-agent expert/tensor hotness before choosing a final mixed-precision quant;
6. add cached-drafter priming and optional GPU keepwarm only after cache/distributed correctness is stable.

The single-M1 field result materially raises confidence that useful Flash-Next performance on this hardware class is feasible. It does **not** establish a two-node 40+ tok/s result; distributed scaling and MTP coordination remain the unknowns.
