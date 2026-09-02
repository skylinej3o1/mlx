# Runtime Research Watch — 2026-09-02 16:30 ET

Scope: fresh external delta after `RESEARCH-WATCH-2026-09-02-1520.md`, following the canonical-state-first protocol. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DS4 distributed serving, and the planned 2x M1 Max 64 GB / TB4 Hermes system.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **UPDATE — oMLX #3330 now proves exact session rehydration across model unload/reload.** A fresh M3 Ultra / Qwen3.8-Flash-Next-oQ4e-MTP live gate persisted the newest exact terminal to SSD before unload. After reload, a 5,039-token prompt restored 5,035 tokens from `ssd-exact-terminal` and processed only a 4-token suffix. This materially strengthens the Hermes design: a logical agent can become cold/unloadable without forcing a full-history reprefill when it returns.
2. **NEW production-track transition — DS4 #952 supersedes #621 for AProjQ4.** #621 remains the development archive; #952 contains the focused production-ready AProjQ4 support. It preserves the same measured Metal result: 2.14 GiB smaller model, final-head three-repetition paired median Q4/Q8 decode ratio 1.155, Q4 winning 32/32 frontiers through 65K, and Metal prefill effectively tied. This remains a lossy/future capacity track, not admissible exact-Q8 P69 evidence.
3. **NEW exact Apple capacity receipt — M3 Max 64 GB / AtomicChat 4.27-bpw Flash-Next.** A fresh user report on a 14-inch M3 Max 40c / 64 GB / 512 GB SSD ran the 4.27-bpw AtomicChat build with llama.cpp at 128K context and raised GPU wired memory to 60,512 MB. Reported prompt processing was ~300 tok/s; generation started above 20 tok/s and fell to ~12 tok/s at 128K. Memory pressure frequently entered amber and the user reports the machine was not practically usable for other work while the model was loaded. This is single-node SSD-streaming evidence, not M1 or dual-node evidence.
4. **FRESH ANECDOTE — near-400 PP / 36 TG at max context on an oMLX MTP setup.** A new comment in a 128-GB M5 Max full-262K Flash-Next thread reports prompt processing "close to 400" and ~36 tok/s generation at maximum context with oMLX Lightning MTP. Hardware/configuration details are not fully restated in the comment, so treat it as a community lead only; do not use it as a calibrated forecast input.
5. **NEW cross-model memory-control lead — oMLX #3384 / #3381.** On M3 Ultra / GLM-5.3-Flash, lowering prefill chunk width 2048 -> 1024 cut peak process memory by 13.87 GB and removed long-prompt livelock at an 8.8% prefill-throughput cost. The new draft PR exposes a per-model prefill-step override. This is not direct Qwen4 evidence: current qwen3.5/qwen4 scheduling can impose a 4096 floor on >=64-GB machines without NAX/native sparse-QSA conditions. Portable lesson: prompt chunk width is a legitimate peak-memory/admission knob, but Flash-Next must be tested against its own gathered-QSA/floor path.
6. **NO CHANGE — exact dual-M1 calibration.** llama.cpp #27993 still has no new sustained 2x M1 Max Flash-Next TG result; DS4 #922 still has no sustained dual-M1 0731 TG result.
7. **NO CHANGE — speculative/kernel watch.** llama.cpp #28243 still has no benchmark/hardware/acceptance table; oMLX #3382 has no follow-up to the 2.3x verify-cost decomposition; #3370 still has no maintainer resolution for temp>0 acceptance collapse; #3320 has no fresh requalification result.
8. **NO CHANGE — Layr / mlx-dspark.** No submission newer than Layr #1481; `ARahim3/mlx-dspark` still reports last push 2026-09-01 10:54 UTC.

## Hermes consequence

The strongest change is not raw speed; it is **session lifecycle confidence**. The desired server policy can now be more explicit:

- 3-4 logical/persistent agents;
- only 2-3 active compute slots when economically appropriate;
- exact resident hot state for recent agents;
- durable SSD exact-terminal/paged fallback for cold agents;
- unload/reload allowed under workstation or memory pressure;
- restore the longest exact terminal and process only the changed suffix;
- keep model/runtime memory accounting separate from advertised context limits.

The new M3 Max 64-GB report is also a useful negative control for workstation mode: squeezing Flash-Next onto one 64-GB node by SSD streaming works, but it consumes essentially the whole machine. Our 2x64-GB design should use the second node and asymmetric resident PP specifically to avoid that operating point.

## Forecast consequence

Short/medium B1, ~128K B1, and mature B2-B4 aggregate probability bands remain **unchanged**. The M5 anecdote and M3 single-node receipt are cross-hardware/runtime evidence and do not replace the missing exact dual-M1 calibration.

The user's mature-system target of roughly **400+ tok/s cold prefill plus excellent prompt/prefix caching** remains sensible. The unload/reload exact-terminal result strengthens the caching side of that target substantially.

External evidence does **not** modify the certified P69 checkpoint; **P69B13 remains next using existing profiling data only**.

## Sources

- oMLX #3330: https://github.com/jundot/omlx/pull/3330
- DS4 #952: https://github.com/antirez/ds4/pull/952
- oMLX #3381: https://github.com/jundot/omlx/issues/3381
- oMLX #3384: https://github.com/jundot/omlx/pull/3384
- Fresh M3 Max 64-GB report: https://www.reddit.com/r/LocalLLM/comments/1w53inj/running_qwen38_flash_on_64gb_macbook/
- Full-context M5 Max thread / fresh oMLX comment: https://www.reddit.com/r/LocalLLM/comments/1w0e23p/running_qwen38flashnext_at_full_262k_context_on_a/
