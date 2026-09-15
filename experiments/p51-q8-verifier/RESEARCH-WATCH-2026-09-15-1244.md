# External runtime watch — 2026-09-15 12:44 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-15 11:34:26 UTC` through the user-request cutoff `2026-09-15 16:44:45 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, comment-only activity, or a later merge of already-known measurements.

## Executive result

No exact active-topology receipt appeared for any canonical target. No target moves.

This was nevertheless a strong Apple / hybrid-runtime pass. The highest-value fresh items are:

1. **oMLX #3685** — direct M4 Max 64 GB / Qwen3.8-27B / 68K-context evidence that a live-memory-dependent SDPA route can change greedy output. Route selection is therefore correctness identity, not merely a memory heuristic.
2. **vLLM #57039** — direct Qwen3.8-Flash-Next GDN prefill evidence that two hidden per-layer copies can be removed; one gated-norm component falls 185 -> 114 us at T=8192 with exact output equivalence.
3. **llama.cpp #28948** — fresh Metal implementation surface for compound MoE routing/reduction and SSM/GDN-adjacent fusions, with broad correctness coverage; performance numbers are still pending.
4. **vLLM #57000** — the 11-second cutoff-edge item from the prior watch: hybrid recurrent-state admission can wedge by billing hundreds of logical null blocks instead of the handful of physical blocks that can actually exist.
5. **mlx-serve #438** — fresh Apple Flash-Next HC/GDN prefill fusion implementation and tests. Its quoted performance cells are prior-arm measurements, not fresh measurements of this head, so they remain supporting evidence only.

Additional promoted transfer: vLLM #57001 rank-aligned collective profiling, #57007 causal-conv product precision, and #57021 GEMM+collective fusion economics.

## Promoted — oMLX #3685: SDPA route is deterministic correctness identity

Source created: `2026-09-15 16:29:40 UTC`.

Direct Apple setup:
- Mac Studio M4 Max 64 GB.
- `Qwen3.8-27B-oQ4e-mtp` architecture: 48 GatedDeltaNet + 16 attention layers, head_dim=256.
- 68,034-token prompt, max output 32, temperature 0, top_k=1.
- oMLX cache disabled; MTP and ANE prefill disabled for the reproduction.

The SDPA256 path chose between an unfused full-score-matrix route and a bounded/fused online-softmax route from *live process headroom on each call*. Those two routes use different floating-point reduction orders. The same byte-identical request therefore could take different arithmetic routes depending only on process history.

Measured first-route headroom for the same request varied **14.8 / 21.6 / 22.7 GB** across processes. The dynamic hard limit also moved **42.1 -> 43.5 GB** inside one run.

Four pre-fix runs of the identical request produced different route/partition histories and multiple distinct replies. Pinning the bounded route removed the divergence.

The fix makes the route a pure function of stable request/model geometry:
- parameter bytes,
- projected cache bytes at the current `kv_len`,
- measured fixed recurrent state,
- configured hot-cache budget,
- stable physical cap rather than transient process usage.

A subtle but important implementation finding: a naïve parameter walker missed private submodules such as `_language_model`, pricing the 27B model at only ~1 GB. Physical budgeting must walk the actual private execution tree, not assume the public module iterator captures all owned weights.

Validation on the patch alone:
- 10/10 identical runs: 5 fresh processes + 5 after a small preceding request.
- same partition: `16 x 4096, 2497`.
- same route point: bounded from chunk 8.
- same first-token logits hash and same reply.
- peak MLX memory fell **30.35 -> 28.39 GB (-6.5%)** because the bounded route does not materialize the full fp32 score matrix.
- no clean speedup claim; TTFT ranges overlap.

### Promoted rule

A route that changes reduction order / arithmetic is **execution and correctness identity**. It must not be selected from incidental allocator/process history if deterministic greedy equivalence is part of the ruler.

For our Apple rulers, record:
`request geometry -> projected physical bytes -> stable cap -> selected arithmetic route -> chunk partition -> output hash`.

Live allocator state may still reject/slow a request for safety, but should not silently choose a numerically different route for the same qualified request.

The PR also leaves a useful open issue: adaptive prefill throttling can still alter the chunk partition from live memory. On recurrent/GDN models, partition boundaries can change reduction/state-update arithmetic. **Prefill partition is therefore semantic identity too**, not merely a scheduler detail.

## Promoted — vLLM #57039: eliminate hidden GDN prefill copies

Source created: `2026-09-15 16:25:54 UTC`.

Direct model path: Qwen3-Next / Qwen3.5 / **Qwen3.8-Flash-Next** GatedDeltaNet prefill.
Hardware measurement: B300 TP1, Qwen3.8-Flash-Next-FP8.

Two copies were paid per GDN layer during FlashInfer chunk prefill:
1. the chunk kernel returned a fresh tensor that was copied into preallocated `core_attn_out`;
2. reshaping a strided `z` slice for gated RMSNorm silently materialized a clone.

The patch writes the chunk kernel directly into the destination buffer and reformulates grouped RMSNorm so `z` remains a view.

Scoped component at T=8192:
- gated norm **185 -> 114 us/layer**.
- max absolute output difference: **0.0**.

Serving cells are modest but directionally consistent:
- 8192-in/1024-out C1 TTFT 238.5 -> 236.6 ms; decode essentially flat.
- C8 TTFT 1153.7 -> 1131.7 ms, aggregate output 774.9 -> 783.4 tok/s.
- 2048-in/128-out C32 TTFT 558.8 -> 541.9 ms, output 1263.3 -> 1275.3 tok/s.
- GSM8K strict exact match: 96.82% before and after.

### Transfer to our Flash implementation

CUDA/B300 and <=8K are not our active topology, so this does not calibrate 40/400. Promote the mechanism:
- audit every `reshape`, slice and layout conversion on the hot GDN/HC path for **physical clone/materialization**, not API-level view intent;
- let producer kernels write directly into the consumer-owned/persistent destination when lifetime permits;
- count per-layer bytes copied, copy kernels, and allocator transients in the PP ruler.

Small per-layer copy wins can compound across the many recurrent layers even when one request-level A/B looks modest.

## Promoted — vLLM #57000: physical recurrent-state admission, not logical span

Source created: `2026-09-15 11:34:37 UTC`, eleven seconds after the previous cutoff.

Hybrid Mamba-align requests resumed after an external KV partial hit could be admitted using the full logical sequence block count even though most recurrent-state positions were represented by null placeholders.

Concrete Kimi-K3 example at 759,544 tokens, recurrent block size 1536:
- logical accounting per Mamba group: **495 blocks**;
- physical requirement: at most **9 blocks** = running state + checkpoint + 7 speculative blocks;
- three Mamba groups plus one MLA group were billed **1546 required blocks**.

The request then remained deferred forever despite HBM/KV usage around 1.2%, and could wedge following requests.

### Promoted rule

For hybrid/recurrent state, admission must price the allocator's **bounded physical ownership model**, not logical token-span placeholders.

This applies especially after prefix/SSD restore, checkpoint transitions and speculative-state allocation. The same physical rule used by allocation must be used by preflight/admission; otherwise a system can reject or deadlock a request that physically fits.

Add to our long-context admission ruler:
`logical span`, `physical live state blocks`, `checkpoint blocks`, `speculative blocks`, `null/virtual blocks`, and the final allocator bill.

## Promoted implementation surface — llama.cpp #28948: Metal MoE/GDN fusion stack

Source created: `2026-09-15 12:24:09 UTC`; active work continued in this window.

Fresh Metal backend fusions include:
- SOFT_MAX + ARGSORT + GET_ROWS for top-k MoE routing, with optional norm/scale;
- MoE weighted reduction fusion;
- RMS_NORM + SCALE;
- SSM_CONV + SiLU;
- Metal function constants for runtime variants.

Correctness coverage reported:
- Metal backend ops: **15,755 / 15,755** passed.
- FA vector-slice tests: **240 / 240**.
- fusion baseline: **228 ok, 0 failed**.

Detailed performance benchmarks are explicitly pending, so there is **no speed claim to book**.

### Transfer

This maps closely onto our Flash/P69-derived hot-path census. Add explicit Apple experiments for:
1. route selection + top-k gather fusion;
2. expert weighted reduction fusion;
3. RMSNorm/scale fusion;
4. conv/activation fusion.

Per standing rule, fusion is admitted only after exact reduction/rounding boundaries and physical route equivalence are enumerated. Do not assume the compound fusion is automatically faster after other bottlenecks move.

## Promoted implementation surface — mlx-serve #438: HC + GDN prefill fusion

Source PR created: `2026-09-15 13:18:49 UTC`.

Fresh implementation rebased from current main fuses Qwen4/Flash-Next HC residual-write/normalization/mixing plus GDN convolution/normalization/gates during prefill. Local M5 Max 128 GB ReleaseFast build and `zig build test` passed: **2558 passed, 171 skipped, 0 failed**.

The PR quotes prior-arm measurements from #408:
- M4 Max 128 GB mixed-4/8 Flash-Next: 16K **723 -> 744 tok/s**, 32K **728 -> 747**.
- M5 Max 128 GB cold 64K mean **1749.5 -> 1849.5 tok/s**.

Those measurements predate this fresh head, so they are **supporting historical evidence only**. The new PR explicitly says fresh-head full-model A/B is pending.

Promote the implementation path and its compiled-reference parity, not the old percentages as new evidence.

## Promoted measurement rule — vLLM #57001: align ranks inside the profiler

Source created: `2026-09-15 11:59:31 UTC`.

Profiling one identical AllGather on four ranks without a post-profiler-start barrier produced reported durations of:
- 30.418 ms,
- 4.137 ms,
- 0.036 ms,
- 3.842 ms.

That is an ~850x apparent spread caused primarily by rank arrival/profiler startup jitter. With a barrier immediately before the profiled call, the same ranks measured 0.034 / 0.105 / 0.204 / 0.236 ms; per-rank compute remained 0.064-0.070 ms.

### Promoted rule

Collective duration includes **arrival skew + peer waiting + transport/work** unless ranks are aligned. Our TB4 PP/MTP profiler must synchronize/quiesce ranks after profiler setup and immediately before isolated collective measurements, while separately retaining end-to-end arrival skew as a serving metric.

Do not interpret the fastest/slowest rank's raw collective span as link cost without this calibration.

## Promoted correctness transfer — vLLM #57007: FP32 accumulation does not imply FP32 products

Source created: `2026-09-15 12:40:38 UTC`.

The causal-convolution prefill/update kernel multiplied BF16/FP16 operands before adding into an FP32 accumulator. Bits lost in the product could not be recovered by the accumulator.

Synthetic Qwen-27B MXFP4 replay:
- **5417 / 10240** convolution outputs differed from the independent FP32-product path before the fix;
- after widening operands before multiplication, all 10240 matched that comparison;
- first-layer recurrent-state relative difference improved roughly **1.81e-3 -> 2.38e-4**.

No task-quality or throughput claim.

### Promoted rule

Precision identity includes **operand precision at multiplication**, not only accumulator/output dtype. For GDN/conv/recurrent equivalence tests, record input cast, product dtype, accumulation dtype and final cast separately. This is relevant when comparing Apple kernels or fusions that appear to advertise the same FP32 accumulator.

## Promoted transfer — vLLM #57021: fuse producer compute with collective when shape warrants it

Source created: `2026-09-15 14:37:15 UTC`.

On DeepSeek-V4.1 B200 TP4, fusing an MXFP8 output GEMM with sequence-parallel reduce-scatter cut the scoped quantization+GEMM+RS path at M=2048/4096/8192 by **39.1% / 32.6% / 28.8%**. Smaller shapes regressed and stay on the old path below M=1024.

E2E output throughput moved +2.0% at C16 and +5.9% at C964; C64 was inconsistent across nodes and is not a stable claim. Task-level accuracy is still pending and generated text differed between arms, so the feature remains opt-in.

### Transfer

NVLink reduce-scatter is not our TB4 PP transport, so this is not topology evidence. The transferable rule is to look for **producer-direct-to-transport / projection+communication fusion** only after measuring a shape crossover. Keep a fallback for small rows and require correctness on changed-input replay and output lifetime.

## Fresh but not promoted / timestamp discipline

- vLLM #57040 adds Qwen3.8-Flash-Next-FP8 MoE benchmark support and reports FlashInfer TRT-LLM remaining ~10-16% faster than tuned Triton on B300 TP1. Useful backend context, but it does not transfer cleanly to Metal/TB4 and does not change the active ruler.
- vLLM main merged #56969 and other older PRs during this window. Their substantive evidence predates this hard window; **merge time does not refresh evidence**.
- `Baekpica/ds4-dfm-rs` #45 is relevant resource-policy work, but it was created at `2026-09-15 01:24:38 UTC` and merged before the previous cutoff. It is not fresh evidence for this watch.
- Fresh oMLX i18n/UI work and unrelated llama.cpp Vulkan/WebGPU/embedding changes were inspected and not promoted.

## External HF/community screen

A current Hugging Face model card for `whm0627/Qwen3.8-Flash-Next-177B-A3B-fits64GB-PLElast-GGUF` reports an M1 Max 64 GB llama.cpp Metal run around **21 tok/s decode / 200 tok/s prefill**, with the author saying 128K keeps roughly the same decode speed and MTP code generation reaches ~24 tok/s. The card's benchmark commit history shows the benchmark was added roughly nine days ago, outside this watch window.

Therefore it is background calibration only and **does not advance the hard freshness boundary or move 40/400**.

No source-time-qualified fresh exact dual-M1 Flash receipt, one-M1-Max64 27B canonical-quant receipt, controlled RTX5070Ti16 target receipt, or dual-M1 DS4-0731 receipt appeared in this pass.

## Target status

Canonical targets remain unchanged:

- Qwen3.8-Flash-Next dual M1 Max64/TB4: **40 tok/s @ ~128K active context**, **400 tok/s cold PP**.
- Qwen3.8-27B one M1 Max64: **25 tok/s**, **110 tok/s native/exact-runtime cold PP**.
- Qwen3.8-27B RTX5070Ti16 + host RAM: **120 tok/s**, **250 tok/s cold PP**.
- DS4-0731 dual M1 Max64/TB4: **15 tok/s**, **180 tok/s cold PP**.

No P69 reorder/reopen.

## Planning impact

This pass strengthens the implementation plan more than target calibration.

Add/raise priority for:
1. deterministic arithmetic-route provenance from stable request geometry;
2. deterministic / explicitly certified prefill partitioning for recurrent state;
3. hidden view-to-copy/materialization accounting in HC/GDN prefill;
4. direct producer-to-destination buffers;
5. compound Metal MoE/GDN fusion experiments;
6. physical recurrent-state admission after cache restore / speculation;
7. rank-aligned collective microbenchmarks plus separately measured arrival skew;
8. operand-product precision in recurrent correctness bars;
9. shape-gated producer+communication fusion experiments.

The fresh evidence is encouraging for the 40/400 campaign because it exposes more concrete removable work on the hybrid path, but it is not an exact dual-M1 measurement and therefore does not justify moving the target.

## New hard freshness boundary

`2026-09-15 16:44:45 UTC`
