# Project 51 external runtime watch — 2026-09-21 08:03 ET

**Hard freshness window:** strictly after **2026-09-21 10:36:04 UTC** through the user's message cutoff **2026-09-21 12:03:30 UTC**.

## Decision

**No numeric TG/PP or quality-floor change.**

- production quality floor remains **>=38 AA-class**, with **39-40 preferred**;
- headline remains **40 TG @ ~128K / 400 genuinely cold PP**;
- planning confidence remains unchanged at **~65% for >=40 TG @ ~128K** and **~70% for >=400 cold PP**;
- no new exact 2x M1 Max 64 GB / TB4 / ~128K / Project-51 mixed-quant + MTP physical receipt appeared.

This short window adds meaningful architecture/correctness evidence in four areas:

1. **Sparse-prefill canonicalization debt:** a fast sparse turn can leave no reusable canonical prefix; bounded idle-time dense recovery can repay that debt.
2. **Failure cleanup:** request-scoped numerical mutations such as a RoPE offset wrapper must be removed before requeue ownership is cleared.
3. **Cache sizing:** profile the same sampler/logits path that warmup and serving will actually use before assigning the rest of memory to KV/recurrent state.
4. **Prefix-planner CPU cost:** once prefix pages are durable, do not rescan them or repeat shared residency/materialization work once per cache group.

## NEW — oMLX #3793: bounded idle-time canonical-state recovery after sparse prefill

Source: https://github.com/jundot/omlx/pull/3793  
Created **2026-09-21 11:04:15 UTC**. Draft/open at cutoff.

SpecPrefill can answer a request from a sparse subset of the conversation while leaving no cache state that the normal prefix cache considers independently restorable. On hybrid models, non-sliceable recurrent layers only carry valid state at captured block boundaries. The consequence is **canonicalization debt**: later turns can repeatedly recompute a suffix even though the prior turn itself was fast.

The draft adds scheduler-owned dense rereads that run only during engine-level slack. They publish ordinary canonical cache state at whole block boundaries through the normal serving/cache path.

Important correctness contract:

- canonical committed tokens may advance only to an **independently restorable** boundary;
- a successful store is not enough: the serving cache itself must read the boundary back successfully under a throwaway identity;
- model/cache identity, exact boundary state and hybrid recurrent snapshot availability are rechecked at publish time;
- partial blocks are not published as smaller wins;
- cancellation/reset/unload/error paths release the synthetic recovery request without turning it into foreground work.

Important scheduling contract:

- background recovery uses bounded, cancellable slices;
- admission is based on **machine-level slack**, not merely one scheduler queue looking idle;
- the recovery budget is **process-global** across engines sharing the accelerator;
- execution-slice size controls collision severity, while the budget controls collision frequency.

One controlled seven-turn synthetic coding session, with the sparse route forced on every foreground turn:

| arm | cumulative foreground | final reusable prefix | final debt |
|---|---:|---:|---:|
| SpecPrefill only | 228.38 s | 0 | 43,065 tokens |
| + background recovery | **79.06 s** | **36,864 tokens** | 2,105 tokens |

That is a **65.4% foreground reduction on one workload**, not a universal speed claim.

Slice measurements also show why recovery must be interruptibility-aware: a 4,096-token slice produced a 15.08 s observed maximum TTFT; smaller 1024/512/256 slices cut the traced uninterruptible unit to roughly 4.66/2.39/1.25 s respectively, with non-monotonic observed maxima.

### Project 51 consequence

This is directly relevant to rewindable always-ready sessions.

A fast sparse/QSA prefill path is not complete merely because it answers the current turn correctly. P51 needs to track **canonical-state debt** separately from foreground completion and optionally repay it during idle periods so the next task can restore a normal committed prefix.

Adopt these design rules:

- committed prefix length advances only after an explicit restorable-state verification;
- publish hybrid state only at versioned committed boundaries that include KV + recurrent/GDN/QSA state;
- background canonicalization is bounded, cancellable, low-priority and globally budgeted across live engines;
- re-evaluate foreground admission between slices;
- sleep/rewind should preserve already-published canonical state even if an unfinished recovery job is discarded.

Do **not** import the 65.4% number into P51 performance planning. It is a single oMLX workload and an open draft.

## NEW — oMLX #3792: stale SpecPrefill RoPE wrapper can leak across requests after OOM requeue

Source: https://github.com/jundot/omlx/pull/3792  
Created **2026-09-21 10:50:42 UTC**. Open at cutoff.

The prefill-OOM requeue path cleared the request bookkeeping id but did not actually remove the shared model's SpecPrefill RoPE wrapper. Because later cleanup was guarded by the id that had just been cleared, the stale offset wrapper could survive into unrelated subsequent requests.

After an earlier crash fix, this failure became quieter: the next sparse prefill could tolerate/peel the wrapper, but ordinary requests arriving before that could still run through the stale position offset.

The proposed fix calls the same RoPE cleanup used by normal completion **before** dropping ownership.

### Project 51 consequence

Generalize this beyond RoPE:

> Any request-scoped mutation of shared model/runtime state must be reverted while ownership is still provable, before requeue/preemption/OOM/cancellation clears the owner token.

Apply this to:

- QSA/indexer temporary offsets or masks;
- speculative verify/draft patches;
- graph-replay row mappings;
- recurrent checkpoint staging;
- PP2 stage-local request metadata;
- any temporary kernel/backend mode switched for one request.

A failure path that merely clears metadata without undoing the underlying numerical mutation is unsafe.

## NEW — vLLM #57926: profile the real sampler/warmup peak before sizing KV

Source: https://github.com/vllm-project/vllm/pull/57926  
Created **2026-09-21 10:43:04 UTC**. Open at cutoff.

MRv2 profiling used dummy requests with no sampling parameters, so the sampler skipped FP32 logits upcast, bias, penalties and bad-word work. KV capacity was then sized against an unrealistically cheap peak. The later kernel warmup used realistic sampling parameters **after KV allocation** and could OOM.

On one L4 24 GB example:

- profiled peak activation changed **0.55 -> 0.80 GiB**;
- KV capacity fell about **1.3%**;
- a configuration that OOMed in warmup at 0.98 memory utilization started successfully after profiling the real sampler path.

### Project 51 consequence

P51's memory admission/profile pass must exercise the same feature set that real wake + serve can activate **before** assigning the remaining memory to KV, recurrent checkpoints, MTP buffers and PP2 workspaces.

The profile identity should include at minimum:

- actual sampling/logit-processing mode;
- MTP verify width and rollback buffers;
- QSA/indexer workspace;
- selected cache dtype;
- grammar/tool-schema path when enabled;
- PP2 stage buffers;
- recurrent checkpoint staging.

Warmup cannot be the first time a larger serving path appears after cache sizing.

## NEW — vLLM #57930: repeated prefix scans can dominate scheduler CPU

Source: https://github.com/vllm-project/vllm/pull/57930  
Created **2026-09-21 11:24:53 UTC**. Open at cutoff.

HiSparse materialization was rescanning the entire already-computed prefix on every call and repeating shared materialization/residency operations once per resident cache group.

The patch:

- starts scanning from the already-ready/importing prefix cursor;
- executes shared operations only once from the first resident manager;
- preserves holes, pending writes, spill budgets and publication ordering.

On one B300 Scale-SWE deployment with 20 resident groups, planner + residency CPU time fell from roughly **110-134 ms/step to 2.7-2.9 ms/step** in the measured phases. A focused 512-page CPU microbenchmark fell from **512.01 to 6.63 us/request**. Live throughput changed by roughly 2.1x between the final original/fixed phases, but those windows were not fixed-context capacity benchmarks and carried instrumentation plus other runtime patches.

### Project 51 consequence

For long-lived P51 sessions, prefix residency bookkeeping must be **incremental**:

- keep monotonic durable/importing cursors;
- never rescan a known-durable 128K prefix on each turn;
- deduplicate shared materialization across target/draft/cache groups;
- separate per-group geometry from shared prefix ownership.

At B1 this may be modest; at B2-B4, multiple live agents and restore/recovery work can make host scheduler latency visible enough to stall otherwise-idle M1 stages.

## NEW DRAFT — vLLM #57939: full imported prompt replay can remain graph-decode-shaped

Source: https://github.com/vllm-project/vllm/pull/57939  
Created **2026-09-21 12:01:01 UTC**, less than three minutes before cutoff. Draft/open.

After a complete P/D prefix import, vLLM still replays the final prompt token to produce logits. The logical request is prefill, but the actual work is a one-token replay. Treating that replay as generic prefill can disqualify the whole mixed batch from a FULL graph.

The draft records successful full-prompt imports and allows the final one-token replay to be graph-decode-shaped only under strict conditions. Partial imports, failures, preemption, speculative/multi-token replay and other ambiguous cases retain normal classification.

An early unmatched B300 live window showed output throughput 1,402 -> 1,487 tok/s/decode GPU and a larger share of FULL-graph steps, but the author explicitly notes that the current-main revision lacks GPU/token/logprob parity validation.

### Project 51 consequence

For sleep -> wake and remote/SSD restored prefixes, classify work by **physical replay shape**, not only by semantic request phase. A certified one-token landing replay should be eligible for the same compiled path as ordinary decode if state identity and numerical parity are proven.

Keep this as an optimization hypothesis until parity is demonstrated; it does not change target planning.

## RECOVERED OLDER COMMUNITY EVIDENCE — halt95 W4A16 Merlin: PP2 + MTP + FP8 PLE at 261K

Source: https://huggingface.co/halt95/Qwen3.8-Flash-Next-W4A16-Merlin

This evidence predates the strict window and is classified as **RECOVERED OLDER EVIDENCE**.

The v2 serving shape is **TP2 x PP2 + expert parallel**, MTP K=3, on 4x RTX 3090. It keeps:

- routed experts INT4 g128;
- GDN qkv/z/out INT8 while selected recurrent tensors remain BF16;
- attention/indexer/shared expert/head paths BF16;
- the 51B PLE/ngram table in **FP8**, host-resident and pulled to GPUs;
- attention KV in FP8 with calibrated static scales.

Measured v2 single-stream rows at 4K / 32K / 131K / 261K prompt:

- thinking-on decode: **162 / 166 / 169 / 176 tok/s**;
- MTP tokens per step: **3.02 / 3.07 / 3.13 / 3.28**;
- prefill: **4,944 @10K / 5,282 @100K / 5,122 @261K**;
- cold TTFT: **0.91 / 6.19 / 24.77 / 50.68 s**.

The same card reports 4/4 250K needle checks and a small quality panel against a BF16 teacher, but this is **not AA certification** and NVIDIA throughput does not transfer to M1.

A concurrency bug in the v2 PP/MTP draft handoff is also instructive: an unidentified draft slot could be overwritten by the alternating PP microbatch, leaving an unmasked grammar row. v2.0.1 keyed draft snapshots by scheduler step and restored schema-valid output under the tested load cells.

### Project 51 consequence

This is useful qualitative support for two existing P51 choices:

1. **higher-precision PLE is a valid deep-context lane**: FP8 PLE can coexist with 261K MTP and >3 accepted tokens/step on a very different runtime/hardware stack;
2. **PP + speculative slot identity must be explicit**: draft state must be keyed to the scheduler step/request that consumed it, not to an anonymous reusable slot.

It does not resolve the Q8-vs-lower-bit PLE question on M1 and does not move the 40@128K probability.

## Screened / no target-changing evidence

- **antirez/ds4:** #1099 received activity, but it is API tools-streaming test coverage, not a P51 runtime receipt.
- **vLLM:** #57926/#57930/#57939 recorded above. #57891's level-2 frozen-weight CPU backup is relevant to generic sleep lifecycle but is explicitly untested and does not alter P51's retained-prefix design.
- **oMLX:** #3792/#3793 recorded above; no new Flash-Next TG receipt after the 10:36 boundary.
- **mlx-serve:** no post-boundary inference-runtime commit relevant to P51; visible PR activity was UI/image/general application work.
- **llama.cpp:** post-boundary merged commits were primarily SYCL/CUDA/CI/server maintenance. Open lazy-row, speculative-order and Metal FA work had activity but no new substantive commit timestamp in this window, so it is not relabeled NEW.
- **Splash:** no post-boundary commit/PR.
- **Kadir qwen38-mac-fast and visible fork:** no post-boundary commit.
- **MTPLX:** no post-boundary commit/PR.
- **APEX:** no post-boundary commit/PR.
- **Reddit/community:** no new exact dual-M1/TB4 Flash receipt surfaced in the strict window.
- **Hugging Face:** the halt95 W4A16 Merlin material is recorded as recovered older evidence, not strict-window new evidence.

## Target impact

**No numeric change.**

Production remains:

- **>=38 AA-class behavior hard floor; 39-40 preferred**;
- **40 TG @ ~128K** headline;
- **400 genuinely cold PP** headline;
- planning confidence unchanged at **~65% for >=40 TG @ ~128K** and **~70% for >=400 cold PP**.

The new work mainly tightens the state machine around sparse prefill, restore/wake and cache sizing. It makes the always-ready agent design more credible, but provides no exact M1/TB4 throughput denominator.

**New hard boundary: 2026-09-21 12:03:30 UTC.**
