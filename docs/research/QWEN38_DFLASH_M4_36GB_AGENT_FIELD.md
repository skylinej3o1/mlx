# Qwen3.8-27B DFlash2 on M4 Max 36GB — agent-workload field result

Date logged: 2026-08-23
Last updated: 2026-08-24

## Sources

- Reddit field report: https://www.reddit.com/r/LocalLLM/comments/1vwdssa/qwen3827b_dflash_on_a_36gb_m4_max_surprisingly/
- DFlash2 drafter: https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2
- oMLX M4 Max 32-core / 36GB Q4 + quantized DFlash2 reference: https://omlx.ai/benchmarks/performance/5allyvr2
- oMLX M4 Max 40-core Q8 target + Q4 DFlash2 reference: https://omlx.ai/benchmarks/performance/6zatli6n
- Q4 DFlash2 GGUF acceptance reference: https://huggingface.co/incoai/Qwen3.8-27B-DFlash2-GGUF/blob/main/README.md

## Reported setup

- MacBook Pro M4 Max, 36GB unified memory
- Qwen3.8-27B-MLX-4bit
- oMLX
- DFlash2
  - draft quantization: 4-bit
  - activation: 16-bit
  - group size: 64
  - verify: adaptive
  - draft window: 2048
- DeepSeek Harness Minimal
- concurrency 1

## Reported same-workload result

| Configuration | Model time | Result |
|---|---:|---|
| Qwen + DSH Minimal, no DFlash | ~133 s | Correct |
| DFlash2 | ~48 s | Correct |
| DFlash2 + Q4 draft | ~42 s | Correct |

The Q4-draft result is ~3.17x lower model-side task time than the no-DFlash baseline on this single reported coding-agent workload. Individual turns reportedly reached ~35–50 tok/s versus ~10–20 tok/s before DFlash.

The report also states zero throttled pages and no increase in swapouts after the Q4 DFlash run. Treat `memory_pressure`'s reported 82% free percentage as a pressure/availability indicator, not literal unused physical RAM.

## Why this matters for MXFORGE

This is more useful than a short synthetic TG headline because it measures a complete coding-agent task that created files, used tools and ran tests successfully. It reinforces the project objective of optimizing time-to-completed-task rather than raw token throughput alone.

The strongest architectural signal is that **draft precision is itself a runtime knob**. Quantizing the DFlash2 drafter to Q4 improved both residency and task time in the reported workload. That suggests a hardware-local search over target quant x drafter quant x verification policy rather than treating the drafter checkpoint as fixed.

The particularly attractive MXFORGE configuration is now:

```text
Qwen3.8-27B Q8 target
        |
        | authoritative logits / lossless verification
        v
Q4 DFlash2 drafter
        |
        v
MXFORGE multi-row Q8 verifier
```

The Q4 drafter can remain low precision because target verification is authoritative. Draft precision primarily changes drafter cost, memory, and acceptance behavior; it does not redefine the target model's accepted-token distribution when verification is implemented losslessly.

## New Q8-target evidence

A fresh oMLX community submission demonstrates that DFlash2 remains effective with an **8-bit Qwen3.8 target** rather than only a 4-bit target. The reported M4 Max 40-core run uses a Q8 target with a Q4/FP16/GS64 DFlash2 drafter and reports roughly:

- 38.0 tok/s at ~1K
- 31.9 tok/s at ~4K

This is not an M1 result and is not a controlled comparison against the MXFORGE stack, but it removes an important uncertainty: a low-bit DFlash2 drafter can productively run ahead of a high-quality Q8 target.

The Q4 DFlash2 GGUF evaluation also reports an acceptance length around 5.39 in its test, versus roughly 5.28 BF16 and 5.13 Q8. Treat those values as checkpoint/runtime-specific evidence, not a guaranteed M1 acceptance rate, but they argue against assuming that Q4 draft quantization necessarily harms acceptance.

## Current MXFORGE Q8 anchor

The live Q8 tuning branch has advanced beyond the earlier ~18.5 tok/s checkpoint.

Current formal certified 29,297-token ruler after P69 SG2R4 promotion:

- target: Qwen3.8-27B-oQ8e-fp16-mtp
- M1 Max 32-core GPU / 64GB
- prompt: 29,297 tokens
- completion: 512
- fixed D3 / verifier M4
- mean decode: **19.0746 tok/s**
- median decode: 19.0741 tok/s
- mean backbone/cycle: 141.8324 ms
- cycles: 186
- acceptance: 325/442 = 73.5%
- deterministic output hash preserved

P69's key verifier improvement is directly relevant to DFlash integration: the SG2R4 Q8 M4 projection kernel shares Q8 weight loads across four verifier vectors, reducing the cost of multi-row target verification.

## M1 DFlash2 forecast

Forecast target: Q4 DFlash2 drafter -> P69-class Q8 target/verifier on the frozen ~29.3K coding ruler.

This is a planning forecast, not a measured result.

| Effective decode threshold | Estimated probability of reaching/exceeding |
|---|---:|
| 21 tok/s | ~90% |
| 23 tok/s | ~75% |
| 25 tok/s | ~55–60% |
| 27 tok/s | ~35% |
| 29 tok/s | ~18–20% |
| 30 tok/s | ~10–12% |
| 32 tok/s | ~5% |

Working midpoint / 50%-confidence target:

**~25.5 tok/s at ~29.3K with Q8 target quality.**

Operational bands:

- conservative successful integration: 21–23 tok/s
- expected tuned MXFORGE result: 24–27 tok/s
- strong result: 27–29 tok/s
- stretch / exceptional result: 30+ tok/s

Relative to the 19.0746 tok/s P69 ruler:

- 23 tok/s = +20.6%
- 25 tok/s = +31.1%
- 25.5 tok/s = +33.7%
- 27 tok/s = +41.5%
- 29 tok/s = +52.0%
- 30 tok/s = +57.3%

Do not multiply the M4 field-report ~3.17x task-time result by the P69 ruler. The forecast above is deliberately much more conservative because DFlash verification geometry, acceptance, long-context attention, and drafter overhead at ~29K remain unmeasured on M1.

## M1 Max experiment plan

The experiment to run is a paired replay on the frozen coding ruler plus a representative agent suite:

1. current P69/native-MTP champion as control;
2. DFlash2 default/high-precision drafter;
3. DFlash2 Q8/Q6/Q4 drafter where supported;
4. Q4/FP16/GS64 as a first high-priority recipe;
5. adaptive verify vs fixed verification widths;
6. draft-window sweep including 2048;
7. explicitly map DFlash verification row counts to existing M2..M8 MXFORGE verifier kernels;
8. retune shared-weight Q8 verification for the dominant DFlash row geometry rather than assuming native MTP's M4 optimum transfers unchanged;
9. record drafter time, target-verifier time, accepted tokens per verification, rejection depth, effective TG, peak memory, and complete task time;
10. repeat at ~4K, ~16K, frozen ~29.3K, and longer-context bands.

The most important comparison is not DFlash2 versus plain autoregressive decoding. It is:

**current tuned native MTP vs independently tuned DFlash2 on identical replayed workloads.**

## Integration hypothesis

There is a plausible source of genuine composability rather than headline-speedup multiplication:

- DFlash2 can increase useful candidate tokens per target verification;
- MXFORGE P51-P69 work reduces the cost of multi-row Q8 target verification.

Those two effects act on different terms of the speculative-decode cost equation and can therefore combine if DFlash's dominant verification geometry maps efficiently to the tuned Q8 kernels.

The main risk is geometry mismatch: native MTP currently favors fixed D3 / M4, while DFlash2 adaptive verification may naturally generate different row counts. Some verifier work should transfer directly; some will need DFlash-specific routing/kernel tuning.

## Corroborating Apple observations

oMLX community submissions on M4 Max 32-core / 36GB show Qwen3.8-27B 4-bit with quantized DFlash2 at roughly 33.5 tok/s @1K and 30.3 tok/s @4K in one configuration, versus roughly 21–22 tok/s for plain 4-bit runs on the same hardware class. A separate 64K DFlash + TurboQuant KV4 submission reports 14.3 tok/s. These are heterogeneous community runs, not a controlled A/B, but they support the claim that the Apple DFlash2 path is real.

The 32-core M4 Max and 32-core M1 Max also have unusually similar headline unified-memory bandwidth (roughly 410 GB/s vs 400 GB/s respectively), which makes the raw low-bit drafter path more portable than a generic M4-vs-M1 generation comparison might suggest. Do not infer equal end-to-end performance: GPU architecture, kernels, target verifier cost, context behavior, and memory residency still differ materially.

## Status

**CORE / high-priority speculative bakeoff.**

Promote Q4 DFlash2 -> Q8 target as a first-class M1 experiment once the current verifier checkpoint reaches a clean stopping point. Preserve the P69 native-MTP champion as the formal control. Do not claim the M4 ~3.17x task-time gain or the ~25.5 tok/s M1 forecast as a measured MXFORGE result until paired certification is complete.
