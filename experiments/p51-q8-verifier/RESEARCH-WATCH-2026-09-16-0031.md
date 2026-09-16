# External runtime watch — 2026-09-16 00:31 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-16 00:15:16 UTC` through the user-request cutoff `2026-09-16 04:31:59 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, merge-only activity, or a later merge of older measurements.

## Executive result

No exact active-topology receipt appeared for any canonical target. **No target moves.**

This window is nevertheless high value because it produced two direct Apple / Flash-Next execution-path findings and several strong speculative/QSA correctness transfers:

1. **mlx-serve `b7b2c775`** — TurboQuant KV was removed after direct Flash-Next / M4 Max measurement showed it was **14% slower than affine at 4K and roughly one-third slower at 16K**. The stored low-bit format had no fused downstream consumer, so every token dequantized and un-rotated the whole cache.
2. **mlx-serve `0b54c43b` / merged #438** — HC/GDN prefill fusion accidentally specialized Metal kernels on prompt width. A novel 700-token width paid three new pipeline compilations and moved **957 ms repeated -> 1060 ms novel**, turning the optimization into a regression below ~1K. Making width a scalar input restored novel lengths to **958–961 ms**.
3. **vLLM #57109** — exact sparse-indexer top-k has a strong context/row-width crossover. A new GVR2 backend loses on short rows but wins increasingly from 32K through 1M; it also prewarms all row-count variants before serving. This directly reinforces our QSA route-ladder and first-use compilation rules.
4. **vLLM #57110** — DSpark incorrectly inherited EAGLE's trailing prefix-cache block drop even though only the hidden-state scheduling contract is shared. The same fix also separates logical target block geometry from heterogeneous physical draft/target page sizes.
5. **vLLM #57108** — a broken serialized-FP8 checkpoint served at **560 tok/s with green health checks while GSM8K strict-match was 0.0** because required per-layer scales were silently treated as loaded. This is a strong artifact-certification warning: boot + throughput do not prove quantized checkpoint integrity.
6. **vLLM #57107 / #57102 / #57097** — volatile serving dimensions can cause unnecessary compile variants; duplicate derived metadata can cost ~0.20 ms/step; and fusing three QSA prepare kernels into one can cut the local stage substantially while producing no resolved E2E throughput change. These sharpen where launch/JIT work belongs in our ruler.
7. **vLLM #57092 / #57094** — batch-wide FP8 scale scope and graph-padding rows can make one request's numerics depend on unrelated co-batched requests or let an inactive NaN poison an entire batch. Quant scale scope and dummy-row numerical inertness are execution identity.
8. **llama.cpp #28976** — fresh M5 Max WebGPU evidence gives another independent GDN+copy fusion receipt, including Qwen3.8-27B Q4, but this is transfer evidence only and does not reopen P69 or move the Apple target.

No fresh source-time-qualified exact dual-M1 Flash receipt, one-M1-Max64 Qwen3.8-27B canonical-quant receipt, controlled RTX5070Ti16 target receipt, or dual-M1 DS4-0731 receipt appeared.

## Promoted direct Apple evidence — TurboQuant KV can lose when no fused consumer exists

Source commit: `ddalcu/mlx-serve b7b2c775593eaa98657c3d4012819752c5917c1e`.
Source timestamp: `2026-09-16 01:08:50 UTC`.

mlx-serve removed its `turbo2` / `turbo4` KV-cache schemes entirely.

Direct measured reason on **Qwen3.8-Flash-Next / M4 Max**:
- TurboQuant KV was **14% slower than affine at 4K**;
- roughly **one-third slower at 16K**;
- no fused hot path consumed the TurboQuant representation;
- therefore each token dequantized and un-rotated the whole cache before use.

The runtime now exposes only the cache schemes whose physical execution path is actually supported.

### Promoted rule for our Flash lane

A nominally smaller/faster storage format is not an optimization unless the hot consumer actually stays in that format.

For every KV/QSA precision experiment record:

`configured scheme -> stored physical representation -> consumer admitted route -> dequant/rotation scope -> bytes read/token -> executed kernel`.

If a cache format forces full-history decode/reformat work each token, its lower residency can be overwhelmed by the conversion cost. Do not keep a precision lane merely because it reduces bytes at rest.

This also strengthens the existing rule that configured precision is weaker evidence than physical packing + executed kernel admission.

## Promoted direct Apple evidence — volatile prompt width must not become a Metal template key

Fresh substantive commit: `0b54c43b664dd91d5b0c85acbf550590905b1fb0` in mlx-serve PR #438.
Source timestamp: `2026-09-16 01:16:49 UTC`.
Merged to main in `ea540c5560c2dbf4db36a649edb0a17a4ecab34a` at `02:40:30 UTC`.

HC/GDN prefill fusion initially used prompt/chunk width `S/M` as a Metal template value. That meant a novel prompt width compiled **three fresh Metal pipelines**.

M4 Max, 700-token prefill:
- repeated/already-compiled width: **957 ms**;
- novel width with template specialization: **1060 ms**;
- after moving width to a 0-dim runtime scalar input: novel widths **958–961 ms**.

Only the genuinely discrete sigmoid-table switch remains templated.

The merge also fixed an experiment-isolation bug: `MLX_SERVE_GDN_DECODE_FUSED=0` accidentally disabled a prefill norm/gate arm too, so a decode A/B could carry a hidden prefill regression. Decode and prefill gates are now independent and env gates are latched.

### Promoted rules

- Serving dimensions that vary per request/chunk belong in **runtime inputs**, not specialization/template keys, unless the specialization gain has been proven larger than compile churn.
- Warm repeated-rung benchmarks can hide shape-first-use JIT tax. Include **novel-width** cells in the qualification ladder.
- Compile-key cardinality is part of execution identity: record how many pipeline/kernel variants a workload can create over the qualified context/batch/depth range.
- A/B switches must be orthogonal. A decode kill switch must not silently change prefill behavior, and vice versa.
- Environment/config reads used by hot-path routing should be resolved/latching outside the repeated inner path.

This is directly relevant to our planned Metal HC/GDN/QSA work and should be enforced from the first implementation, not cleaned up after steady-state tuning.

## Promoted sparse-indexer transfer — vLLM #57109: exact top-k has a row-width crossover

Source created: `2026-09-16 03:35:34 UTC`.

vLLM adds FlashInfer GVR2 as an exact sparse-indexer decode top-k backend. The useful evidence is not that one backend is universally fastest; it is that backend choice changes sharply with **valid row length, row width, batch and top-k**.

GB300, FP32 indexer logits, exact selected values checked against masked `torch.topk`:

### Top-k 512, DeepSeek-V4.1-Flash-like shape

| row / valid | batch | cooperative | persistent | DeepSelect | GVR2 |
|---|---:|---:|---:|---:|---:|
| 32K / 4K | 8 | **9.2 us** | 15.5 | 10.4 | 11.4 |
| 32K / 32K | 8 | 14.4 | 23.7 | 15.5 | **12.1** |
| 32K / 32K | 64 | 18.6 | 16.5 | 16.5 | **13.8** |
| 64K / 64K | 8 | 16.4 | 27.7 | 19.6 | **12.4** |
| 64K / 64K | 256 | n/a | 61.6 | 34.9 | **29.5** |

### Top-k 2048, uncompressed 128K-style shape

| valid length | batch | cooperative | persistent | DeepSelect | GVR2 |
|---:|---:|---:|---:|---:|---:|
| 8K | 8 | **9.3 us** | 16.5 | 12.4 | 14.4 |
| 32K | 64 | 22.6 | 20.6 | 30.8 | **16.5** |
| 128K | 64 | 35.6 | 53.4 | 50.3 | **24.4** |
| 1M | 64 | 140.4 | 325.8 | 155.8 | **84.1** |

The new backend therefore deliberately stays out of short-row cells.

A second useful part is compilation discipline. The kernel variant depends on row count, so startup warms every relevant row count up to the configured `max_num_seqs * (1 + speculative_tokens)`. On 4x GB300 DeepSeek-V4.1-Flash, all GVR2 compiles occurred during startup warmup and **zero** occurred during subsequent serving.

No E2E throughput claim is made.

### Transfer to our QSA/indexer ladder

- Sparse selector backend is a **geometry-dependent route**, not a model-global choice.
- Route on actual valid span / selected K / query rows / physical layout / device generation.
- Benchmark selector latency at short, target (~128K) and very-long spans; do not infer the 128K winner from 4K.
- If a kernel's compiled variant depends on verifier width, batch or row count, prewarm the complete qualified set or remove the volatile dimension from the compile key.
- Exact top-k qualification must still include deterministic tie order, not only value-multiset equality.

This composes directly with the previous mlx-serve QSA gather-vs-mask crossover finding.

## Promoted speculative/cache correctness — vLLM #57110: shared hidden-state path does not imply shared cache-tail semantics

Source created: `2026-09-16 03:37:54 UTC`.

DSpark intentionally uses part of EAGLE's hidden-state scheduling path because it consumes target hidden states. That shared predicate accidentally caused it to inherit **EAGLE's trailing prefix-cache block drop** too.

For EAGLE that drop is required because the trailing draft-cache block is volatile. DSpark's block-parallel drafting does not have that contract. The inherited behavior therefore:
- discarded an otherwise reusable final prefix block;
- moved Mamba cache position back one block;
- reduced prefix hits and forced repeated prefill.

The same PR also separates target logical block geometry from heterogeneous physical cache pages:
- target-only config defines logical attention/Mamba block sizing;
- DSpark/target page sizes remain heterogeneous rather than padded to the largest group;
- page-size buckets occupy disjoint backing ranges;
- bucketed physical bytes/block feed admission, capacity and worker configuration consistently.

### Promoted rules

- Reusing a scheduler/control path does **not** authorize inheriting its cache commit/drop semantics. Cache-tail rules are speculation-family-specific state contracts.
- Logical token/block granularity and physical page/billing width are separate identities.
- Draft/verifier auxiliary state may have different physical page geometry from target KV; admission must bill the actual heterogeneous allocation rather than widening every group to a peer's maximum.
- Prefix reuse must certify the committed boundary for every state family: KV, recurrent/Mamba/GDN, QSA/indexer and draft state.

No throughput target moves from this CPU-tested correctness PR.

## Promoted artifact-certification rule — vLLM #57108: a fast healthy server can still have a broken quantized checkpoint

Source created: `2026-09-16 03:29:20 UTC`.

vLLM's opt-in strict weight tracker effectively exempted entire quantized modules if their quant method defined a post-load hook. That made genuinely missing serialized quant parameters invisible.

Real motivating checkpoint: 274B DeepSeek-V4-Flash-FP8 on 8x MI300X.
- 43 `attn.wo_a.weight_scale_inv` tensors, one per layer, were absent from the shards despite being registered by the index.
- Before the fix the server booted normally, health was green and throughput was **560 tok/s**.
- Yet GSM8K strict-match was **0.0000** and flexible-extract 0.0136; outputs were garbage.
- With strict tracking fixed, the loader fails closed and names exactly the 43 missing scales.
- Correctly configuring that projection as unquantized/BF16 then boots cleanly; a 50-sample GSM8K check reported 1.0 and the serving run completed 64/64 requests.

### Promoted rules for our conversion/benchmark gate

- Successful load, green health and high throughput are **not artifact correctness evidence**.
- For every mixed-quant checkpoint, prove that each physically required weight, scale, zero-point and side tensor was either loaded from a named source or intentionally synthesized by a qualified post-load rule.
- A generic `post_process_weights` hook must never imply every parameter in that module is optional.
- Artifact completeness belongs before performance benchmarking. If the model is computing quickly with uninitialized or wrong-scale data, the speed number is invalid regardless of output latency.

This is especially relevant when we build/modify Flash and 27B mixed-precision packs.

## Promoted JIT/spec-control transfer — vLLM #57107

Source created: `2026-09-16 03:19:30 UTC`.

Triton's compile cache specialized acceptance-estimator integer arguments on properties such as `== 1` and divisibility by 16. Runtime `num_reqs` / `num_tokens` changes therefore created multiple compiled variants and serving stalls.

Across a sweep from 1 through 256:
- `_accumulate_kernel`: **14 -> 9** compiled variants;
- `_local_max_sumexp_kernel`: **3 -> 1**;
- `_predict_kernel`: **3 -> 1**.

Correctness tests passed; no E2E latency claim is provided.

### Transfer

The lesson matches the direct Metal width result in this same window: volatile serving geometry must not silently explode compile-key cardinality. For Lightning MTP, inventory compile specialization across **B, K/depth, verifier rows and context bucket** and distinguish intentional finite specialization from accidental JIT churn.

## Promoted launch/metadata transfer — vLLM #57102

Source created: `2026-09-16 03:01:36 UTC`.

A DeepSeek-V4.1 speculative trace was rebuilding the same token-to-request mapping once per KV cache group even when query boundaries and padding were identical.

Sharing it only within one `build_attn_metadata()` call changed:
- target mapping launches: **6 -> 1**;
- draft mapping launches: **3 -> 1**;
- total target launches: 30 -> 25;
- total draft launches: 12 -> 10.

Metadata-builder host wall reduction is ~11–12% across B1/B16/B128. At B1:
- target: **1261.14 -> 1120.84 us**;
- draft: **484.71 -> 425.06 us**;
- combined saved per step: roughly **0.20 ms**.

GPU-side span also moved target 66.7 -> 58.0 us and draft 27.7 -> 24.1 us. Exact metadata comparisons passed.

### Transfer

- Repeated derived mapping/state metadata across groups can be shared when their request boundaries/padding identity is exact.
- Keep reuse lifetime narrow: same build/cycle only unless a stronger invalidation contract exists.
- Target and draft metadata lifetimes remain separate.
- On Apple, where host launch gaps matter, explicitly census duplicate mapping/index construction across QSA/GDN/MTP state families before adding more kernel work.

## Promoted scoped QSA fusion transfer — vLLM #57097

Source created: `2026-09-16 01:56:18 UTC`.

Fresh Qwen3.8-Flash-Next work fuses three decode prepare kernels into one:
1. main Q/K norm + RoPE + output gate;
2. K/V paged-cache write;
3. QSA pre-indexer work.

H20 microbench, current three-kernel stage vs fused launch:
- M=1 cold L2: **12.13 -> 6.58 us (1.84x)**;
- M=256 cold: **15.69 -> 9.19 us (1.71x)**;
- M=1024 cold: **24.34 -> 11.44 us (2.13x)**.

But the 8x H20 E2E serving A/B is unresolved/flat within run-to-run noise:
- C1: -1.5%;
- C4: +1.3%;
- C64: 0.0%.

Some outputs are bitwise identical, while main Q/K differ by up to one BF16 ULP because the fused kernel changes RMSNorm reduction order.

### Transfer

- Kernel-launch fusion can have a real local win and still be irrelevant to request throughput if the stage is not on the dominant critical path.
- Measure local stage marginal **and** E2E before promoting it in priority.
- Fusion changes reduction structure; maintain numerical/semantic gates rather than assuming equivalent algebra is bit-identical.

This is useful for our Metal QSA design but provides no target-grade magnitude.

## Promoted quant/determinism rule — vLLM #57092

Source created: `2026-09-16 00:32:23 UTC`.

With batch-invariant mode enabled, online FP8 MoE still used one dynamic activation scale across the entire co-batched activation tensor. One request's values therefore changed another request's quant scale and could flip greedy tokens.

Fresh reproducer before fix:
- request A alone vs A with B: first token flip at position 11;
- warm vs cold writer: flip at position 11.

After switching the invariant path to per-token activation scales and fixing the associated expert-scale stride bug, all compared rounds were identical. Kernel error against reference also improved in the tested shape.

### Promoted rule

Quantization **scale scope** is execution identity. A per-tensor scale over a multi-request batch creates cross-request numerical coupling even when model weights and individual prompts are unchanged. If we require deterministic equivalence across B1/Bn, activation/stat reductions must be scoped to the semantic request/token unit or the coupling must be explicitly accepted and measured.

## Promoted dummy-row rule — vLLM #57094

Source created: `2026-09-16 01:32:52 UTC`.

A CUDA-graph decode batch with three active sequences pads to four. The inactive row had `seq_len=0`; a decode-attention stage computed `0/0`, creating NaN. A later **batch-wide** FP8 dynamic-scale `amax` then propagated that NaN into every active request.

Fix makes the zero-length row produce finite zero output; three active rows then match the unpadded execution.

### Promoted rule

A dummy/padding row must be **numerically inert at every intermediate stage**, not merely ignored at the final output. Any later batch-wide statistic, quant scale, reduction or normalization can amplify poison from an inactive row into live requests. This extends our existing rule that dummy speculative paths must be write-side-effect-free.

## Supporting transfer — llama.cpp #28976: another GDN+copy fusion receipt

Source created: `2026-09-16 02:18:29 UTC`.

WebGPU adds fused `gated_delta_net + cpy`, using the same eligibility concept as CUDA/Metal. M5 Max measurements:
- Qwen3.8-27B Q4_K Medium tg128: **19.37 -> 20.63 tok/s (~7%)**;
- Qwen3.5 2B: ~3%;
- Qwen3.5 9B: ~4%.

A nine-prompt Qwen3.5-9B MTP set retained aggregate acceptance **0.926** while total wall moved **21.41 -> 20.85 s**.

This is WebGPU, M5 Max and Q4, not our MLX/Metal M1 topology. Treat as independent mechanism support only. It does not reopen P69 or move any canonical target.

## Watch-only fresh items

### vLLM #57105 — Qwen3.8-Flash-Next QSA logits workspace reservation
Created `2026-09-16 03:09:05 UTC`. It reserves worst-case indexer-logits workspace up front so later shapes do not trigger fresh allocation/fragmentation. This is directly model-relevant but currently has no performance or allocator measurement in the PR body. Keep it on the watch list; if measured fragmentation/residency data appears, fold it into the QSA workspace ruler.

### vLLM #57104 — async KV load + MTP promotion deadlock
Created `2026-09-16 03:04:26 UTC`. Async-loaded requests were admitted without reserving future speculative lookahead slots. Under KV pressure, parked requests could fill the pool, then none could be promoted because promotion needs `1 + num_spec_tokens`; parked loads are non-preemptible and with zero RUNNING requests nothing can free space. The fix reserves promotion margin at admission. No benchmark result is posted yet, but retain the correctness rule: an offloaded/parked request must be admitted only if its required future promotion state is physically allocatable.

### oMLX
Main activity in-window is UI/i18n/benchmark-export work. New Qwen tool-call recovery work is agent/API correctness rather than inference performance. No new source-time-qualified active-lane runtime receipt was found.

### ds4-dfm-rs
Main merged the Ling support work after the boundary, but its substantive measurements predate this window and were already screened. Merge time does not refresh evidence. No fresh DS4-0731 target receipt appeared.

### llama.cpp
Other fresh work in the window is backend/build/support work without a stronger active-lane measurement than #28976.

## External / community screen

Fresh web/HF/community search produced no source-time-qualified new exact active-lane receipt inside this hard window.

Visible M1 Max Qwen3.8-27B benchmark pages remain August measurements and therefore background only. A current benchmark aggregator exposes RTX5070Ti rows, but the surfaced result lacks the source-time/provenance controls required for promotion into our RTX target lane. No canonical target uses those numbers.

## Target status

Canonical planning targets remain unchanged:

- Qwen3.8-Flash-Next dual M1 Max64/TB4: **40 tok/s @ ~128K active context**, **400 tok/s cold PP**.
- Qwen3.8-27B one M1 Max64: **25 tok/s**, **110 tok/s native/exact-runtime cold PP**.
- Qwen3.8-27B RTX5070Ti16 + host RAM: **120 tok/s**, **250 tok/s cold PP**.
- DS4-0731 dual M1 Max64/TB4: **15 tok/s**, **180 tok/s cold PP**.

No P69 reorder/reopen.

## Planning impact

Add or strengthen these items in the implementation/tuning ruler:

1. KV precision receipt must prove the downstream consumer actually consumes the stored physical format; reject low-bit schemes that full-cache dequantize/unrotate every token.
2. Volatile prompt/chunk width, batch and adaptive speculative dimensions should be runtime inputs unless bounded specialization is explicitly measured; record compile-key cardinality.
3. Add first-use **novel-shape** cells in addition to warm repeated-rung cells.
4. QSA selector/gather routes need context/valid-span crossover ladders; no universal backend assumption.
5. Prewarm every intentionally specialized selector/verifier row-count variant before timed serving.
6. Separate speculation-family cache semantics from shared scheduler/hidden-state mechanics; certify commit/drop boundaries per state family.
7. Bill heterogeneous draft/target cache page sizes physically rather than widening groups to a logical peer size.
8. Before benchmarking a converted quant checkpoint, assert required weight/scale/zero-point completeness; boot/health/TG are insufficient.
9. Record quant activation/stat **scope** (token/request/batch) as execution identity and include B1-vs-Bn deterministic probes where required.
10. Dummy/padded rows must stay finite/inert through all intermediates, especially before batch-wide quant/stat reductions.
11. Census duplicate target/draft/QSA metadata mapping work per verifier cycle and reuse only under exact boundary identity.
12. Keep kernel-fusion priority tied to measured critical-path/E2E gain; microbench speedup alone does not justify implementation order.
13. Admission for parked/offloaded state must include future MTP lookahead/promotion margin so the system cannot enter a zero-running, non-preemptible deadlock.

This pass adds useful implementation constraints and more evidence that the remaining gains are highly route- and geometry-dependent, but it does not provide exact dual-M1 calibration. **40/400 remains the correct canonical success floor.**

## New hard freshness boundary

`2026-09-16 04:31:59 UTC`
