# Qwen3.8-27B DFlash2 on M4 Max 36GB — agent-workload field result

Date logged: 2026-08-23

## Source

- Reddit field report: https://www.reddit.com/r/LocalLLM/comments/1vwdssa/qwen3827b_dflash_on_a_36gb_m4_max_surprisingly/
- DFlash2 drafter: https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2

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

For M1 Max 64GB, do not transfer the M4 numbers directly. The experiment to run is a paired replay on the frozen coding ruler or a representative agent suite:

1. current native MTP champion/control;
2. DFlash2 FP16/default drafter;
3. DFlash2 Q8/Q6/Q4 drafter where supported;
4. adaptive verify vs fixed block settings;
5. draft window sweep (including 2048);
6. record target-verifier time, drafter time, acceptance/path length, effective TG, peak memory, and complete task time;
7. repeat at realistic ~30K and longer contexts.

Quality must be separated into target-weight quality and speculative behavior. DFlash verification is lossless with respect to the target model, but this field report uses a 4-bit target, so it does not answer whether a Q6/Q8 target plus a low-bit DFlash drafter is the best quality/speed point for MXFORGE.

## Corroborating Apple observations

oMLX community submissions on M4 Max 32-core / 36GB show Qwen3.8-27B 4-bit with quantized DFlash2 at roughly 33.5 tok/s @1K and 30.3 tok/s @4K in one configuration, versus roughly 21–22 tok/s for plain 4-bit runs on the same hardware class. A separate 64K DFlash + TurboQuant KV4 submission reports 14.3 tok/s. These are heterogeneous community runs, not a controlled A/B, but they support the claim that the Apple DFlash2 path is real.

## Status

**FIELD REPORT / high-value lead.** Promote to the Qwen3.8 speculative bakeoff. Do not claim the reported ~3.17x task-time gain on M1 until reproduced under paired replay.