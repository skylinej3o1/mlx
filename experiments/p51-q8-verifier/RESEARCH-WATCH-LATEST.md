# External runtime watch — 2026-09-18 05:21 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-18 03:56:56 UTC` through `2026-09-18 09:21:44 UTC`.

PRs, issues, comments/reviews, and default-branch commits were explicitly screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Current Qwen3.8-Flash-Next Hugging Face/oMLX/community surfaces were also searched. Evidence time means the substantive measurement or investigation timestamp, not crawler, merge, rebase, label, or generic review-bot time.

## Executive result

**No exact active-topology dual-M1/TB4 Q5 receipt appeared. The canonical numeric targets do not move.**

Flash-Next remains:
- canonical quant lane: **Q5-class / eventual ~5.x BPW**
- hardware/topology: **2x M1 Max 64 GB / TB4**
- headline target: **40 tok/s sustained TG at ~128K active context**
- cold PP target: **400 tok/s**

The evidence picture does improve enough to durably recalibrate confidence:
- **40 TG @ ~128K:** about **55% engineering confidence**
- **400 cold PP:** about **65-70% engineering confidence**

Those are planning estimates, not statistical probabilities.

The strongest additions are:
1. **NEW substantive M1 evidence in the strict window:** DS4 #1068 received a detailed M1 Max 64 GB resident-mode A/B that reaches **31.71 TG MTP at 5.8K** and **28.76 TG MTP at ~17.4K**, with **~254-270 PP** at the correct chunk size. The same comment exposes a severe chunk-size-dependent PP regression.
2. **NEW exact Qwen3.8-Flash-Next offload evidence:** vLLM #57497 keeps the full PLE n-gram table off GPU on one MI300X, remains bit-identical against device-resident PLE, recalls 105K/209K needles, and cuts a 16K TTFT **3.5 -> 1.9 s** using asynchronous start/finalize prefetch.
3. **NEW interactive-serving finding:** oMLX #3726 fixes prefill-admission starvation; a request with only 1,161 uncached tokens had waited ~50 s. Controlled first-token latency fell **8.86 -> 0.73 s** without MTP and **7.28 -> 1.16 s** with MTP.
4. **NEW hidden-state warning:** vLLM #57493 shows identical greedy requests producing different decode logprobs/text depending on prior filler traffic even with prefix caching off and max_num_seqs=1.

## NEW / RECOVERED — DS4 #1068 gives a stronger exact-M1 Flash calibration

PR #1068 itself predates this window, so its original table is **recovered older evidence**, not relabeled new.

Exact original setup:
- MacBook Pro M1 Max 64 GB
- macOS 25.5
- Metal
- DS4 `8db1d1d`
- `Qwen3.8-Flash-Next-Q2.gguf`
- 137.10 GiB on disk
- **41.72 GiB resident**
- n-gram table disk-only
- prefill chunk 2048.

Original measured sweep:
- 2K: **288.41 PP / 24.15 TG**
- 4K: **274.97 / 24.41**
- 8K: **274.78 / 24.45**
- 12K: **275.57 / 24.46**
- 16K: **273.95 / 24.26**

A real 32,113-token prompt:
- **271.94 PP**
- **22.76 TG**

Built-in MTP:
- **33.19 TG** on highly predictable output
- **28.91 TG** on prose
- about 3% PP cost.

Classification: **exact M1-generation and exact Flash-Next family, but Q2 rather than the canonical Q5 lane. Strong silicon/runtime calibration, not direct target proof.**

### NEW strict-window #1068 comment: resident-mode optimized A/B

At **2026-09-18 04:29:47 UTC**, a new physical M1 Max 64 GB A/B was posted. Base was current DS4 main `8db1d1d`; the candidate was the Qwen Metal optimization branch. Both were separately built from matching worktrees.

Selected results:

5,760-token prompt:
- ordinary decode: **21.91 -> 26.63 TG (+22%)**
- MTP: **28.20 -> 31.71 TG (+12%)**
- prefill: ~274 -> ~271 PP ordinary; ~268 -> ~262 PP MTP.

17,408-token prompt:
- ordinary decode: **22.92 -> 24.81 TG (+8%)**
- MTP: **24.81 -> 28.76 TG (+16%)**
- prefill: ~268 -> ~270 PP ordinary; ~259 -> ~253 PP MTP.

Reported decode ranges did not overlap in any tested cell. MTP acceptance counters reproduced the branch's expected counts.

Classification: **new exact M1 hardware A/B, low-bit/non-target quant, medium-context rather than 128K.**

### Important negative result: chunk 128 can halve resident PP

On the 5,760-token prompt with resident weights:
- `--prefill-chunk 128`: **282 -> 136 PP**, about a 52% loss
- `--prefill-chunk 2048`: prefill stays roughly flat around 270 PP.

The regression bisected to the #1047 streaming-foundation commit even though resident mode was being used. Decode remained improved.

Project 51 action:
- prefill chunk is **performance topology**, not a cosmetic knob;
- M1 bring-up must sweep 128 / 512 / 1024 / 2048, and larger only when memory allows;
- do not certify an optimization from one chunk width.

This new exact M1 evidence is the main reason the durable PP target confidence is now **65-70% for 400 PP**, while the numeric target remains 400.

## NEW — vLLM #57497: Qwen4Exp PLE CPU offload + asynchronous prefetch

PR #57497 was created **2026-09-18 05:04:02 UTC**.

Exact evaluated model/hardware:
- `Qwen/Qwen3.8-Flash-Next-FP8`
- **1x MI300X**
- max model length 262,144
- PLE table in pinned host memory through UVA
- 120 GiB CPU KV tier.

Purpose:
- keep the official FP8 PLE n-gram table (~**51 GiB**) entirely off GPU;
- support the bf16 table path (~**102 GiB**) for NVFP4 artifacts;
- start the next PLE layer lookup on a side stream, then join/copy only when that layer consumes it;
- keep lookup start/finalize behind custom ops so compilation does not materialize a full bf16 copy of the table.

Correctness:
- 50/50 PLE tests pass;
- offload vs device top-8 logprobs **bit-identical, max diff 0.0**;
- exact needle recall at **105K and 209K**;
- simple arithmetic prompt correct.

Capacity/performance:
- GPU KV pool: **1.57M tokens**, about **6.0x 262K**
- 16K TTFT: **3.5 s synchronous -> 1.9 s asynchronous**
- single-stream decode: about **77-84 TG**.

Classification: **new exact same-model-family offload receipt, wrong hardware/runtime for direct M1 transfer. Strong architecture evidence.**

Project 51 action:
- SSD PLE on M1 should use the same conceptual split phase: **launch gather early -> continue useful work -> join only at consumption**;
- compile boundaries must not accidentally materialize offloaded PLE state;
- correctness gate compares offload/resident logprobs or tensor outputs, not only final text.

Target impact: no numeric move. Confidence in the chosen offload architecture rises.

## NEW — vLLM #57491: sparse n-gram offload can be effectively free when hidden

PR #57491 was created **2026-09-18 04:43:22 UTC** for DeepSeek-V4.1-Flash on ROCm.

On MI355X TP4, moving Engram tables from device to pinned host memory:
- available KV memory: **107.8 -> 154.38 GiB (+43.2%)**
- KV capacity: **4,325,113 -> 6,194,599 tokens (+43.2%)**
- max concurrency @ 33,792: **127.99x -> 183.32x**.

Serving, 4096 input / 512 output, C8:
- base mean TPOT: **11.35 +/- 0.02 ms**
- offload: **11.35 +/- 0.02 ms**
- output throughput: **620.64 vs 621.10 tok/s** in paired measurement, statistically flat.

Micro-shape:
- 1 token / 18 rows: UVA **9.3 us**, HBM **10.7 us**
- 1024 tokens / 18,432 rows: UVA **89.0 us**, HBM **10.3 us**
- background prefetch is intended to hide the wider-prefill delta.

A strict-window follow-up cross-check at 8x MI355X reported GSM8K parity between base/offload arms within sampling error.

Classification: **new exact non-target sparse-table offload evidence.**

Project 51 implication:
Sparse table residency should be treated independently from dense model residency. If the access can be launched early and hidden, a very large table can be moved out of the scarce compute-memory tier without paying an output-throughput tax.

Do not transfer the +43.2% capacity number to Apple; memory architecture and storage tier differ.

## NEW — oMLX #3726: raw PP does not guarantee interactive TTFT

PR #3726 was created **2026-09-18 05:09:06 UTC** and merged as `ca32d928ca561af4921a6724de89adee9d70c7b3` at 05:18 UTC.

Failure:
- decode active;
- existing chunked prefills always got the first prefill opportunity;
- those chunks accrued decode debt;
- admission gate reclosed before new waiting requests could enter.

Observed production symptom:
- a classifier request hit cache and had only **1,161 tokens** left to prefill;
- it still waited about **50 seconds** for admission;
- request cancelled around 60 seconds after HTTP entry.

Controlled Qwen3.5 9B test, concurrent 16K prefill + decode + later short request:

MTP OFF:
- first token **8.86 -> 0.73 s**
- completion **12.11 -> 1.18 s**

MTP ON:
- first token **7.28 -> 1.16 s**
- completion **10.65 -> 1.16 s**.

The fix alternates the first prefill opportunity between waiting requests and already-running prefills while keeping memory/concurrency/decode-debt guards.

Classification: **new exact oMLX scheduler result; different model, highly transferable serving behavior.**

Project 51 action:
Every user-facing PP receipt now needs separate timing for:
1. request arrival -> admission,
2. admission -> first prefill execution,
3. model prefill PP,
4. first-token wall time.

A system can have excellent PP and still feel unusably slow if stage 1/2 starves under concurrent decode.

## NEW — vLLM #57493: prior requests can perturb greedy decode with cache disabled

Issue #57493 was created **2026-09-18 04:57:06 UTC**.

Setup:
- Qwen3-8B bf16
- Ryzen AI Max+ 395 / Radeon 8060S, gfx1151
- ROCm attention backend
- `max_num_seqs=1`
- eager execution
- prefix caching **disabled**
- same greedy probe repeated after filler prompts of different lengths.

ROCm attention over 20 trials:
- prefill-driven logprob[0]: **1 distinct value**
- decode logprob[5]: **4 distinct values**
- completions: **2 distinct outputs**, 14 vs 6 occurrences.

Triton attention:
- logprob[0]: **1**
- logprob[5]: **1**
- completion: **1**, 20/20 identical.

Classification: **new non-target kernel/state correctness receipt.**

Project 51 action:
A fixed greedy probe must be replayed after variable unrelated filler traffic, not only from a fresh process. Compare token logprobs/hash as well as text. This test applies even with prefix cache disabled and B1 scheduling, because stale scratch/kernel state can create cross-request dependence outside the explicit cache.

## NEW — DS4/V4.1 distributed prefill warning

DS4 issue #1078, created **2026-09-18 07:29:44 UTC**:
- 2x DGX Spark
- DeepSeek-V4.1-Flash Q2
- tensor parallel over RDMA
- reported decode **18-20 TG**
- prefill roughly **400 PP**.

A tool-use prompt shows a long apparent freeze:
- prompt start at 09:16:36;
- first logged prefill progress at 32,768 / 56,603 tokens only at 09:17:54;
- total prompt wall **157.9 s**, average **358.4 PP**.

No root cause is established yet. Do not convert the progress gap into a kernel conclusion.

Classification: **new exact non-target distributed serving symptom.**

Project 51 implication:
Distributed prefill qualification should include per-chunk timestamps and “time before first progress” rather than trusting only final average PP.

## NEW — vLLM #57521: a plausible prefill fusion regressed TTFT

Issue #57521, created **2026-09-18 07:34:33 UTC**, reports A-B-A testing of a DeepSeek-V4 context-WKV stacking optimization on:
- 2x DGX Spark / GB10
- TP2 over RoCE
- DeepSeek-V4-Flash-0731 NVFP4
- DSpark k=5.

TTFT:
- 8K A1/B/A2: **2.502 / 2.589 / 2.512 s**
- 32K: **10.191 / 10.551 / 10.221 s**
- regression: roughly **+3.2-3.3%**.

Same-build A1<->A2 TTFT spread is only 0.3-0.4%, while decode throughput and acceptance fluctuate 6-7% between boots. The patch also reduces KV capacity about 1.5%.

Classification: **new exact non-target distributed regression and methodology evidence.**

Project 51 action:
For small PP changes, use A-B-A or mirrored interleaving and measure the metric's own same-build noise floor. Do not infer prefill wins from noisy decode/acceptance movement.

## Low-impact / negative scan results

- oMLX #3589 merged in-window, but its main Qwen Flash expert-offload measurements predate the hard boundary. It remains useful supporting evidence: parallel `pread` turns serial expert-miss I/O into a much faster pipeline, but is not relabeled new because of merge time.
- oMLX dev4 got a startup-failure issue (#3730) with no diagnostic detail by the cutoff; no Project 51 conclusion follows yet.
- mlx-serve #454, created just after the prior boundary, shows a Qwen3.8-27B DFlash2 drafter shape mismatch on M3 Max. It is a 27B speculative-path issue, not Flash-Next target evidence.
- llama.cpp strict-window commits/PRs contain no new exact Flash-Next M1/TB4 Q5 receipt. The relevant current Flash PR set is unchanged.
- Current HF/oMLX searches found no new exact dual-M1 Q5 benchmark in this window. Older M5 Q5 and M1 low-bit results remain the calibration anchors already recorded.
- vLLM #57514 has no measurements; it is not used as performance evidence.

## Target / confidence decision

### Flash-Next dual M1

**Keep 40 TG @ ~128K / 400 cold PP. Keep Q5-class as the canonical quant lane.**

Current planning-confidence ladder at ~128K:
- >=30 TG: **~85-90%**
- >=35 TG: **~70-75%**
- >=40 TG: **~55%**
- >=45 TG: **~30-35%**
- >=50 TG: **~15-20%**.

Cold PP:
- >=250: **~97%**
- >=300: **~90%**
- >=350: **~80%**
- >=400: **~65-70%**
- >=450: **~45-50%**
- >=500: **~30-35%**
- >=600: **~12-15%**
- >=700: **~5%**.

Why confidence moved:
- exact M1 low-bit execution is now supported by a better reproducible DS4 receipt around 24.4 TG / 275 PP through 16K, plus ~22.8 TG / 272 PP at 32K;
- the strict-window M1 optimization A/B reaches roughly 29-32 TG with MTP on medium contexts;
- the prior independent M1 PLE-last receipt remains about 21 TG at 128K;
- the exact-Q5 M5 receipt remains 47.3 TG / 1,203 PP at 128K without MTP;
- offload/prefetch evidence increasingly shows the PLE table can be taken off the scarce fast-memory tier without making it the steady-state bottleneck.

Why confidence does not move higher:
- no exact Q5 dual-M1/TB4 physical receipt;
- Q2/IQ1 bandwidth economics differ substantially from Q5;
- PP2/TB4 bubbles, stage balance and distributed recurrent/QSA/MTP state remain unmeasured on the target topology;
- chunking and scheduler policy can erase otherwise-good kernel speed.

## New/strengthened qualification rules

1. **Prefill chunk sweep:** chunk width is part of the benchmark identity; sweep 128/512/1024/2048 at minimum on M1.
2. **Admission latency decomposition:** request->admission and admission->first-prefill are reported separately from model PP.
3. **Async PLE split phase:** measure synchronous lookup against launch-early/join-late overlap; require output/logprob parity.
4. **Cross-request hidden-state probe:** repeat a fixed greedy/logprob probe after variable filler traffic even with prefix cache disabled.
5. **Distributed progress telemetry:** record first-progress delay and per-chunk wall times, not only average PP.
6. **Noise-floor A/B:** small PP/TTFT claims need mirrored/A-B-A runs and same-build drift measurement.

## Hard freshness boundary

`2026-09-18 09:21:44 UTC`
