# External runtime watch — 2026-09-18 12:27 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-18 15:03:36 UTC` through `2026-09-18 16:27:22 UTC`.

PRs, issues, comments/reviews, and default-branch commits were explicitly screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Fresh Qwen3.8-Flash-Next Hugging Face/community surfaces were also searched. Evidence time means substantive measurement/investigation time, not crawler, merge, label, bot or rebase timestamps.

## Executive result

**No exact dual-M1-Max/TB4 Q5 receipt appeared. Numeric Flash targets and planning confidence do not move.**

Flash-Next remains:
- canonical quant lane: **Q5-class / eventual ~5.x BPW**
- target topology: **2x M1 Max 64 GB / TB4**
- headline target: **40 TG sustained at ~128K**
- cold PP target: **400 PP**
- planning confidence: **~55% for 40 TG @128K**, **~65-70% for 400 PP**

This window is primarily useful for **tuning/control-plane correctness**, not for recalibrating Flash throughput. The strongest findings are:
1. shape-bucketed kernel tuning can be silently frozen at compile-time dummy shapes and erase most of the intended gain;
2. rank-local autotune-cache divergence can hang distributed tuning collectives;
3. recurrent checkpoints can become visible after a producer is preempted before the state was actually computed;
4. target and speculative/draft compute-buffer reserve must be treated as separate memory identities.

## NEW — vLLM #57586: runtime shape must drive tuned-kernel dispatch

PR created **2026-09-18 15:57:42 UTC**.

Problem:
- `VLLM_BATCH_INVARIANT=1` routes linears through tuned persistent Triton matmuls;
- config tables are keyed by architecture, N/K and an **M bucket**;
- on the default `torch.compile` path, config lookup runs while Dynamo traces with a dummy M;
- the selected BLOCK_M / BLOCK_N / warp / stage configuration becomes frozen in the graph;
- small-M decode can therefore run with a large-M configuration despite having a carefully tuned small-M table.

On RTX PRO 6000 Blackwell / SM120 the PR reports the frozen config is **3-6x slower per GEMM** than the intended M<=8 configuration.

Switching batch-invariant mode to breakable CUDA graphs means lookup occurs at graph-capture time with the real capture M.

Decode-heavy latency, BI=1 main -> BI=1 corrected:
- Qwen3-1.7B: **1.4305 -> 0.5211 s (-63.6%)**
- Qwen3-4B: **2.3578 -> 0.9797 (-58.4%)**
- Qwen3-8B: **3.4567 -> 1.5818 (-54.2%)**

BI overhead versus BI=0 changes:
- 1.7B: **2.95x -> 1.07x**
- 4B: **2.52x -> 1.05x**
- 8B: **2.28x -> 1.04x**.

Prefill-heavy latency also improves substantially:
- 1.7B: **0.4674 -> 0.2590**
- 4B: **0.8095 -> 0.5024**
- 8B: **1.2641 -> 0.8254**.

TP2 Qwen3-8B shows no expected win because the SM120 table lacks those per-rank shapes; measured change is -1.3%, effectively neutral.

Correctness:
- batch-invariance tests pass;
- TP2 bitwise probe: **0 / 1536 mismatches** across the reported comparisons.

Classification: **new exact Blackwell shape-dispatch evidence; not Flash/M1 evidence.**

### Project 51 action

For every shape-sensitive autotuned path:
- log the runtime-effective M/N/K and selected config ID;
- prove those values are not frozen during compile/tracing from a dummy shape;
- compare selected config at trace time, capture time and steady-state runtime;
- reject a tuning result if the optimized table exists but the runtime never actually consults the real request shape.

This is especially relevant to the RTX 5070 Ti lane and to future compiled multi-row verifier/decode kernels.

## NEW — vLLM #57579: distributed autotune caches must agree across ranks

PR created **2026-09-18 15:16:26 UTC**.

Observed mechanism:
- on FlashInfer 0.6.x, rank 0 can report an autotune **cache hit** while peers enter **Tuning**;
- peers then block on tuning collectives that rank 0 never enters;
- one cause is dual persisted filenames (`autotune_config.json` vs `autotune_configs.json`);
- another is rank-local in-memory AutoTuner state.

Proposed behavior:
- before synchronized tuning, every rank loads the same persisted payload or all miss together;
- rank-local hits are cleared if the group is going to miss;
- both cache filename aliases are written.

Validation at cutoff:
- isolated CPU helper tests pass;
- full pytest was not run in the author's environment;
- no physical multi-rank reproduction/fix receipt is posted yet.

Classification: **new distributed autotune mechanism evidence; not performance evidence.**

### Project 51 action

Before any dual-Mac experiment that depends on learned/tuned runtime state:
- hash the tuning cache/config on both Macs;
- require identical cache epoch/config IDs before execution;
- if one node has a warm hit and the other does not, force a group-wide deterministic choice: all-load or all-retune;
- include tuning-cache identity in the result metadata alongside `Mac1 SHA == Mac2 SHA == result SHA`.

A distributed run is not reproducible if only the source code SHA agrees while rank-local learned tuning state differs.

## NEW — vLLM #57580: uncomputed recurrent checkpoints can leak through preemption

Issue created **2026-09-18 15:28:07 UTC**.

CPU scheduler/cache-metadata reproduction:
- Mamba align cache mode
- prefix caching enabled
- 16-token blocks
- priority preemption.

Priority case:
- request `low` has only **32 completed tokens**;
- it is withdrawn before executing the next boundary;
- a later consumer nevertheless gets a **48-token prefix/state hit**;
- state refcount moves **0 -> 1** and allocation succeeds.

FCFS control:
- `low` actually reaches **48 completed tokens**;
- consumer receives a legitimate 48-token hit;
- refcount **1 -> 2**.

Mechanism:
- checkpoint/hash is eagerly registered during allocation;
- same-pass priority withdrawal frees the producer block without retracting the registration;
- a later state lookup can acquire the never-computed checkpoint.

Limits:
- CPU metadata reproduction only;
- no model forward / GPU / MLX / actual state tensor corruption demonstrated;
- latest main/fix branches were not executed by the reporter.

Classification: **new recurrent-state scheduling evidence, strongly transferable to hybrid GDN state ownership.**

### Project 51 action

A recurrent/GDN/MTP checkpoint is publishable only after confirmed model execution crosses its frontier.

Qualification must distinguish:
- allocated checkpoint
- hash-registered checkpoint
- actually-computed checkpoint
- committed/visible checkpoint.

A successful refcount increment or cache lookup is not proof of computed state.

Add a priority/preemption fixture where an unexecuted boundary must remain invisible while earlier completed state remains reusable.

## NEW transfer evidence — llama.cpp #29086: target and draft reserve are separate memory identities

PR created **2026-09-18 15:22:37 UTC**, later closed.

Idea:
- reserve compute buffers for less than the full advertised context;
- allow allocator growth later if the conversation reaches deeper context.

Development-model result:
- roughly **6.5 GiB** freed;
- throughput improvement only about **1.5%** because the memory was largely host-side;
- explicitly characterized by the author as a memory knob rather than a speed optimization.

Critical negative:
- applying the reduced reserve to the **speculative draft context** cut decode from **26.8 TG -> 11.9 TG**;
- the PR therefore deliberately leaves the draft context fully reserved.

Classification: **new non-target memory-layout evidence; closed draft, no Flash target effect.**

### Project 51 action

Price and tune reserve separately for:
- target model
- MTP/verifier/draft state
- long-context QSA/KV
- transient prefill workspace.

Do not infer that reserve that appears idle on target-only execution is also safely reclaimable from the speculative side.

## NEW transfer evidence — vLLM #57585: recurrent-kernel shape-aware launch can help B1 without serving-throughput gain

PR created **2026-09-18 15:57:09 UTC** for GLM-5.3-Flash KDA on H20.

Kernel spec-verify improvements versus fixed launch configuration:
- roughly **+14-19%** at n_req 1-4 on the reported TP4/TP8 cells;
- smaller but positive gains at larger request counts.

E2E:
- single-request TP8 decode: **212 -> 223 TG (+5%)**
- 48-concurrency serving throughput: **unchanged within run-to-run variance**.

Kernel and state output are reported bit-identical across the sweep.

Classification: **new recurrent-kernel transfer evidence, not Qwen/Apple evidence.**

Project 51 implication:
single-request recurrent-kernel improvements can be real while aggregate serving throughput is unchanged. Keep B1 TG and B2-B4 aggregate goals separate and do not promote a Hermes/multi-agent optimization solely from a B1 microkernel win.

## Strict-window negative / no-promotion findings

- DS4 #1056 received only a note that another small bug was found; no new commit/measurement was posted before the cutoff, so the corrected M1 A/B from the prior watch remains the latest physical M1 evidence.
- oMLX #3737/#3738 had no substantive new diagnosis/fix in this window. The dev4 MTP/memory regressions remain open and version-specific.
- vLLM #57590 adds a rope-free sparse-MLA ROCm path for GLM-5.3-Flash, but all performance/accuracy cells are still TODO at cutoff.
- llama.cpp and mlx-serve default-branch activity produced no new Qwen3.8-Flash-Next Apple performance receipt.
- Fresh community/HF searching did not surface a new exact **dual M1 Max / TB4 / Q5** benchmark in this time window. Current search results mostly point to previously known single-Apple or stronger-hardware receipts.

## Target / confidence decision

**No change.**

Flash-Next dual M1 Max:
- **40 TG @ ~128K: ~55%**
- **400 cold PP: ~65-70%**

TG ladder:
- >=30: ~85-90%
- >=35: ~70-75%
- >=40: ~55%
- >=45: ~30-35%
- >=50: ~15-20%.

PP ladder:
- >=250: ~97%
- >=300: ~90%
- >=350: ~80%
- >=400: ~65-70%
- >=450: ~45-50%
- >=500: ~30-35%
- >=600: ~12-15%
- >=700: ~5%.

The window strengthens the **qualification/control plane**, not the physical Flash forecast. The next meaningful confidence move still needs target-quant Apple evidence at long context or exact dual-M1/TB4 execution.

## New/strengthened qualification rules

1. **Runtime shape, not trace shape:** persist real M/N/K and chosen kernel config; verify tuned decisions occur after real shape is known.
2. **Distributed autotune identity:** tuning-cache/config hashes must match across both Macs before a distributed run.
3. **Computed-before-published state:** recurrent checkpoints become cache-visible only after confirmed execution.
4. **Separate target/draft reserve:** memory reserve is role-specific; verifier/draft headroom cannot be reclaimed based on target-only behavior.
5. Existing gates remain: effective-setting verification, chunked/un-chunked numerical parity, runtime-version memory staircase, autotune stability/hysteresis, largest-prefill workspace admission, scheduler admission timing and cross-request determinism.

## Hard freshness boundary

`2026-09-18 16:27:22 UTC`
