# Qwen3.8-27B: M4 Max external calibration and post-P69 implications

Status: **external field calibration / not a replacement for the frozen P69 ruler**

Updated: 2026-08-30 ET.

Primary field report:
- https://www.reddit.com/r/LocalLLaMA/comments/1w1qn9a/speeds_of_a_local_qwen3827b_on_an_m4_max_with_5/

Related reproducible benchmark/config repository:
- https://github.com/snagnever/macstudio-local-llm

## Why this matters

This is one of the more useful external Apple-Silicon calibrations for the active Qwen3.8-27B project because the benchmark includes several production-ish inference stacks, multiple context lengths, prefix-cache/edit scenarios, native MTP, DFlash2, and high-precision 8-bit/oQ8e targets on the same M4 Max.

It should **not** be compared directly to the P69 frozen ruler: hardware, prompts, sampling, runtime, quant layout, cache state and speculative policy differ. The value is as a ceiling/crossover calibration and as evidence for post-P69 experiment ordering.

## Headline 32K decode results on M4 Max 40-core

Approximate field results reported in the post:

| Runtime / target | Decode @ ~32K |
| --- | ---: |
| oMLX AWQ ~5 bpw, target-only | ~40.1 tok/s |
| oMLX oQ8e (~8.6-bit class) + native MTP | ~30.8 tok/s |
| mlx-dspark 8-bit target + DFlash2 | ~38.3 tok/s |
| MTPLX 4-bit + native MTP | ~45.2 tok/s |
| MTPLX 8-bit + native MTP | ~36.7 tok/s |

The oMLX benchmark configuration pins:

- `Jundot/Qwen3.8-27B-oQ8e-mtp` for the oQ8e arm;
- `Jundot/Qwen3.8-27B-oQ8e-fp16-mtp` for the FP16-scale oQ8e arm;
- MTP enabled;
- SpecPrefill disabled;
- ANE prefill disabled.

The DFlash2 arm pins:

- target: `mlx-community/Qwen3.8-27B-8bit`;
- drafter: `incoai/Qwen3.8-27B-DFlash2`;
- runtime: mlx-dspark;
- adaptive/automatic draft width.

## M4 -> M1 bandwidth-normalized calibration

The full M4 Max used in the field report is a 546 GB/s-class machine. A full M1 Max is about 400 GB/s.

A deliberately crude bandwidth-only normalization gives:

- oQ8e native-MTP: `30.8 * 400 / 546 ~= 22.6 tok/s`;
- 8-bit + DFlash2: `38.3 * 400 / 546 ~= 28.1 tok/s`;
- ~5-bpw target-only: `40.1 * 400 / 546 ~= 29.4 tok/s`.

These are **not forecasts**. M4 has newer GPU architecture, different kernels and different runtime behavior. They are useful as external upper-bound indicators for what a mature M1 stack might plausibly approach if the workload remains largely bandwidth-limited.

Against the current certified P69-family M1 Max result of roughly 19.55 tok/s at ~29.3K, the bandwidth-normalized oQ8e/MTP field result suggests the current stack is already a large fraction of an external mature-runtime reference, while leaving credible residual headroom.

## Revised exact-Q8 structural target view

This field calibration supports a modest upward confidence revision without changing the requirement for local measurement.

Approximate confidence for the frozen ~29.3K exact-Q8 ruler:

- >=20.0 tok/s: ~80-85%;
- >=20.5 tok/s: ~55-60%;
- >=21.0 tok/s: ~35-40%;
- >=21.5 tok/s: ~20%;
- ~22+ tok/s: ~10%, no longer physically absurd but still a stretch.

Interpretation:

- 20.0 is increasingly likely;
- 20.5 is a reasonable optimization target;
- low-21s should be treated as a serious stretch objective rather than fantasy;
- do not use the external M4 result to bypass P69's exactness/measurement gates.

## DFlash2 moves up the post-P69 queue

The strongest planning change is the 8-bit + DFlash2 result.

Reported context curve:

| Context | 8-bit + DFlash2 |
| ---: | ---: |
| ~32K | ~38.3 tok/s |
| ~64K | ~29.9 tok/s |
| ~128K | ~22.6 tok/s |
| ~256K | ~14.5 tok/s |

This is much stronger Apple-Silicon evidence than previously available that DFlash2 can materially outperform a native-MTP high-precision target on real workloads.

Preferred experiment order after the exact P69 structural series closes:

1. freeze the native-MTP champion;
2. A/B DFlash2 against that exact target/runtime;
3. A/B native MTP + `ngram-mod`/context-derived drafting;
4. compare task-weighted wall time on novel-code and copy/edit/patch-heavy agent workloads;
5. only then consider adaptive routing between speculative modes.

Do not interrupt P69 to chase DFlash2.

## Context-dependent speculation is now directly evidenced

The same field report shows materially different scaling by speculative strategy as context grows.

Approximate curves:

| Context | oQ8e native MTP | DFlash2 8-bit | MTPLX 4-bit MTP |
| ---: | ---: | ---: | ---: |
| ~32K | 30.8 | 38.3 | 45.2 |
| ~64K | 27.4 | 29.9 | 34.0 |
| ~128K | 21.2 | 22.6 | 23.7 |
| ~256K | 14.0 | 14.5 | 7.2 |

The aggressive native-MTP path that wins at short/medium context can become uneconomic at extreme context.

This validates a future policy layer such as:

- 0-32K: aggressive native MTP / DFlash competition;
- 32-64K: adaptive speculative depth;
- 64-128K: shallower speculation and continuous acceptance/cost measurement;
- 128K+: increasingly target-biased;
- near 256K: permit target-only or DFlash-like mode to beat expensive multi-token verification.

The correct crossover must be measured per runtime/quant/hardware rather than hard-coded from this M4 post.

## Weight-byte economics remain dominant

The ~5-bpw target-only arm reportedly reaches ~40.1 tok/s at ~32K, faster than the ~8.6-bit native-MTP arm despite having no speculative acceleration.

This is a strong reminder that speculative decoding cannot always repay nearly doubling target-weight traffic.

Longer-term product profile candidate:

- **QUALITY:** highly optimized exact/high-precision oQ8e native-MTP stack;
- **SPEED:** quality-certified ~5-bpw target optimized primarily for bytes moved per committed token.

Keep these as separate profiles rather than contaminating the exact-Q8 research ruler.

## Prefix-cache/edit behavior matters for agents

The field benchmark includes cold, repeat, append, middle-edit and tool-turn scenarios rather than only isolated decode.

Reported behavior at long context shows that runtimes differ materially in retained/reusable prefix state, especially after middle edits. That means nominal decode TPS is not sufficient for agent-runtime selection.

For coding agents, measure at minimum:

- exact repeat;
- append-only continuation;
- middle-of-context edit;
- tool-result insertion;
- cache-hit percentage;
- prefill wall time after each mutation;
- total task wall time, not only generation TPS.

This aligns with the broader MXFORGE policy: cache topology is an inference optimization in its own right.

## Current planning conclusion

This result does **not** change the immediate P69 candidate-selection discipline.

It does change the post-P69 priority stack:

1. finish exact native-MTP structural tuning;
2. DFlash2 becomes a high-priority A/B rather than a distant curiosity;
3. add context-aware speculative routing instead of assuming one verifier policy for 32K through 262K;
4. retain a possible ~5-bpw speed profile as a separate production lane;
5. evaluate cache/edit behavior as part of real agent throughput.

The external M4 result should be treated as a calibration ruler, not as a claim about achievable M1 throughput until reproduced locally.
