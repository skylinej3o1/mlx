# Runtime Research Watch — 2026-09-02 23:20 ET

Scope: fresh external delta after `RESEARCH-WATCH-2026-09-02-1630.md`, following the canonical-state-first protocol. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DS4 distributed serving, and the planned 2x M1 Max 64 GB / TB4 Hermes system.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **NEW independent Apple persistent-cache receipt — llama.cpp #28092.** On M5 Max 128 GB / Metal / Qwen3.8-Flash-Next (~90 GB), a 33K-token hybrid state including recurrent GDN state plus speculative draft state survived a full process restart. Cold prefill was 39.2 s, restart without disk cache 39.7 s, and restart with `--cache-disk` **0.09 s**. Disk cost was roughly **900 MiB per 33K-token prompt**. This independently confirms the oMLX #3330/#3328 conclusion that cold logical agents need not replay their full histories after process/model lifecycle events.
2. **NEW pre-M5 Metal performance bundle — DS4 #954.** The PR explicitly targets M1–M4 resident Metal paths and is physically measured on M3 Ultra / DeepSeek-V4-Flash-0731. Greedy decode moves 42.49–43.93 -> **46.14 tok/s** (+5.0–8.6%); prefill gains ~1.3% at 2K and ~4.0–4.4% at 4K–8K; first-token latency 28.1 -> **24.3 ms**. Output is reported bit-identical. This is portable pre-M5 Apple evidence, but it is DS4/DeepSeek rather than Qwen Flash-Next and therefore does not directly move the dual-M1 forecast.
3. **NEW pipeline-shard correctness/performance lead — DS4 #957 / #845.** A known two-host Apple-Silicon pipeline case using `--layers` mapped a shard as ~156 disjoint Metal buffers and measured **10.01 -> 0.13 tok/s (~77x slowdown)** versus the same host/binary without the fragmented mapping; network telemetry was effectively zero, so the collapse was local compute/mapping. New PR #957 coalesces adjacent/overlapping tensor spans before creating Metal buffers. **No post-fix throughput receipt has been posted yet.** For our eventual PP2 bring-up, require a mapping-log gate proving coalesced/overlapping shard mapping before trusting any throughput result.
4. **UPDATE — llama.cpp #28243 now has real but contradictory Flash-Next MTP measurements.** On RTX 5090 + 5060 Ti, UD-IQ4_XS + shared Q4_K_M MTP at 65K measured 36.4 tok/s no-draft -> **45.3 average**, 48–54 in code sections, with acceptance 0.767 / mean len 2.53. On 2x RTX A6000 with UD-Q3_K_XL, both shared and standalone draft heads fell to ~0.32–0.39 acceptance and **never beat the 41–42.5 tok/s baseline**, despite the same standalone head previously reporting 82–95% acceptance on #27836. This strengthens the existing rule: MTP must be qualified by exact quant, workload, sampling, hardware and branch; do not make it mandatory for Hermes.
5. **RECOVERED + UPDATE — llama.cpp #28136 direct PLE reads.** The older PR reports real-world Qwen3.8-Flash-Next prefill on GB10 improving roughly **300 -> 750–800 tok/s** by replacing lazy `mmap` PLE access with direct reads; fresh comments identify the test model as Unsloth UD-Q4_K_XL and stress that realistic text touches far more PLE rows than repeated-token microbench prompts. This is not Apple evidence, but reinforces our existing PLE rule: benchmark real code/agent prompts and avoid synchronous random mmap fault behavior on the inference thread.
6. **NEW cross-model Apple memory caution — oMLX #3394.** On M5 Max 64 GB / Qwen3.8-27B, an older source revision completes 128K while a newer source build rejects the same run at 114,688 tokens, even with the head-dim-256 memory-bounded route forced. This is not Flash-Next evidence, but reinforces that context limits are runtime/admission/transient dependent rather than derivable from static KV bytes alone.
7. **UPDATE correctness caution — oMLX #3181.** A fresh M3 Ultra 512 GB report shows a community `Qwen3.8-Flash-Next-MLX-oQ8-MTP` conversion still collapsing to constant `!` output even after the RMSNorm-dialect canonicalization path runs. The failure is independent of MTP and prefix cache. Treat arbitrary community MLX conversions as unqualified until deterministic output/parity gates pass; prefer known oMLX-native/qualified checkpoint lineages for performance bring-up.
8. **NEW instrumentation lead — oMLX #3391.** A new scheduler PR times previously invisible prefill-side boundary snapshot capture on hybrid GDN models. The motivating report saw ~5–6 s block-crossing premiums while existing SSD-store timers only showed milliseconds. This PR instruments rather than fixes the cost; track the first physical attribution result because cold/warm Hermes session economics depend on recurrent-state snapshot overhead.
9. **UPDATE — DS4 #861 rebased current main.** On 2x gfx1151 / TB5 pipeline split, current measured PP is ~250 tok/s at 6K and 274 at 23K, decode ~14–15.5 tok/s, and B2 partial batching gives +3–14% aggregate depending prompt shape. Kernel POCs place single-session decode near the DRAM wall; forcing high iGPU clocks adds ~6–10%. Routed-MoE row batching remains the next proposed multi-session gain. No direct M1-Max forecast change.
10. **NO CHANGE — exact dual-M1 receipts.** llama.cpp #27993 still has no new sustained 2x M1 Max Flash-Next TG result; DS4 #922 still has no sustained dual-M1 0731 TG result. Layr has no new submission after #1481 and `ARahim3/mlx-dspark` still reports last push 2026-09-01 10:54 UTC.

## Hermes consequence

The strongest new architectural evidence is **independent confirmation of cold-session persistence**. Both oMLX and llama.cpp now physically demonstrate that hybrid Flash-Next state can survive unload/restart and avoid replaying a long prompt. The llama.cpp receipt additionally gives a first storage-order estimate: ~900 MiB for ~33K tokens in that particular M5 Max/Q8/draft configuration. Do not extrapolate it as a universal byte/token constant, but budget SSD cache storage explicitly when planning 3–4 logical agents.

For PP2 qualification, add one explicit startup gate inspired by DS4 #957/#845:

- inspect per-node Metal model-map diagnostics;
- reject fragmented per-tensor shard mappings before benchmarking;
- require coalesced/overlapping mappings plus resident-memory confirmation;
- only then interpret stage timing / TG / PP.

Speculation policy remains workload-adaptive. The new llama.cpp #28243 results show that even the same model family and draft machinery can range from a useful +25% class gain to a complete net loss depending on quant/hardware/branch.

## Forecast consequence

Short/medium B1, ~128K B1, and mature B2-B4 aggregate probability bands remain **unchanged**. None of the fresh measurements are the missing exact 2x M1 Max Flash-Next calibration.

The software-shape confidence improves: persistent cold state, exact lifecycle rehydration, and pre-M5 Metal optimization are all moving in the desired direction. The new PP shard-map issue is a bring-up hazard to test explicitly, not evidence that the proposed asymmetric resident PP2 architecture is wrong.

External evidence does **not** modify the certified P69 checkpoint; **P69B13 remains next using existing profiling data only**.

## Sources

- llama.cpp #28092 persistent prompt cache: https://github.com/ggml-org/llama.cpp/pull/28092
- DS4 #954 pre-M5 Metal bundle: https://github.com/antirez/ds4/pull/954
- DS4 #957 layer-map coalescing: https://github.com/antirez/ds4/pull/957
- DS4 #845 fragmented `--layers` mapping report: https://github.com/antirez/ds4/issues/845
- llama.cpp #28243 Flash-Next MTP: https://github.com/ggml-org/llama.cpp/pull/28243
- llama.cpp #28136 direct PLE reads: https://github.com/ggml-org/llama.cpp/pull/28136
- oMLX #3394 128K prefill regression: https://github.com/jundot/omlx/issues/3394
- oMLX #3181 Qwen4-exp norm/checkpoint compatibility: https://github.com/jundot/omlx/issues/3181
- oMLX #3391 prefill-boundary timing: https://github.com/jundot/omlx/pull/3391
- DS4 #861 distributed/batching work: https://github.com/antirez/ds4/pull/861
