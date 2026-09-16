# External runtime watch — 2026-09-15 20:15 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-15 18:32:30 UTC` through the user-request cutoff `2026-09-16 00:15:16 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, merge-only activity, or comment-only activity unless that comment itself contains a new measurement.

## Executive result

No exact active-topology receipt appeared for any canonical target. **No target moves.**

The strongest fresh item is unusually relevant to the Flash lane:

1. **mlx-serve #439** — direct M4 Max / Qwen3.8-Flash-Next mixed-4/8 evidence that the MTP QSA verify-gather has a real context/KV-layout crossover. On dense KV, copying the fixed ~14K-row verify union loses to the in-place mask path below roughly 32K keys. Because the two arithmetic routes are not bit-identical, raw decode tok/s can be distorted by acceptance/content forks; verifier round cost is the honest A/B metric.
2. **vLLM #57057** — Qwen3.8 at 262K on MI355X shows a clean capacity crossover for 4-bit KV: slightly slower than FP8 at low concurrency, then better before eviction and dramatically better once FP8 hits its KV-capacity wall. This is a capacity/quality alternative lane, not a reason to replace our preferred quality configuration.
3. **vLLM #57078** — sparse-prefill local work can be cut by consuming dense top-k indices directly instead of packing dense-to-ragged and by tiling inverse RoPE; the latter is 2.2–3.1x faster in the scoped MI355X kernel microbench.
4. **vLLM #57079** — an incorrectly gated fast MoE backend plus a disabled compiled activation path roughly doubled DS4-family decode on MI325 at 32K. The transfer is about physical route/capability admission, not an Apple DS4 receipt.
5. **vLLM #57042 fresh on-GPU comment** — independent gfx1100 validation confirms reduction-order dependence and adds a new chunk-seam result: merely changing tensor/chunk geometry can change 2-stage FP32 all-reduce bits even without switching algorithms.
6. **llama.cpp #28972** — speculative graph metadata capacity itself can overflow as max draft depth grows; dynamic/adaptive speculative depth must size scheduler graph structures, not only model buffers.

Fresh vLLM #57081/#57086 and ds4-dfm-rs #47 were inspected as additional transfer/supporting evidence. No fresh exact dual-M1 Flash, one-M1-Max64 27B canonical-quant, controlled RTX5070Ti16 target, or dual-M1 DS4-0731 receipt appeared.

## Promoted — mlx-serve #439: QSA verify gather has a context/KV-scheme crossover

Source PR created: `2026-09-15 22:39:30 UTC`.
Fresh corrective commit after review: `2026-09-16 00:14:14 UTC`.

Direct Apple/model setup:
- Apple M4 Max.
- Qwen3.8-Flash-Next mixed 4/8-bit.
- dense KV.
- 128 output tokens, temperature 0.
- MTP fixed depth 6, verify width S=7.
- two reps per MTP cell.

The verify-gather copies a roughly fixed 14K-row union. At moderate context on dense KV, that copy can cost more than leaving KV in place and applying the mask path. The patch therefore changes the gather floor from one universal value to a per-KV-scheme gate: **32768 for dense KV**, with quantized KV retaining 16384 as an explicitly unmeasured carry-forward.

Fresh cells:

| prompt | prefill before/after | decode before/after | verify-round cost before/after |
|---:|---:|---:|---:|
| 17K | 748 / 750 tok/s | 45.2,45.1 / 45.1,55.7 | **66.0 ms -> 62.1–64.5 ms** |
| 34K | 737 / 735 | 46.9,47.2 / 46.3,46.7 | 68.0 -> 68.8 ms |

The 55.7 tok/s 17K rep is **not** a clean throughput win: the mask path is not bit-identical to the gather path, and that rep followed a different greedy trajectory with acceptance around 2.46 tokens/round versus 1.91. The scoped round cost is therefore the honest mechanism measurement.

Serial no-MTP curve, included to show the dip is speculative rather than ordinary decode:

| context | decode | prefill |
|---:|---:|---:|
| 1K | 56.0 | 750 |
| 2K | 54.0 | 801 |
| 4K | 52.5 | 830 |
| 8K | 51.8 | 787 |
| 16K | 51.4 | 764 |
| 32K | 50.8 | 747 |

Full suite: 2552 passed, 0 failed.

A review found two hot-path bugs in the first patch version: the default/no-env floor was not memoized, causing repeated environment scans per verify layer, and TurboQuant could be classified as quantized at block-selection time but as dense at gather time, paying a selector whose result was then discarded. The fresh `00:14:14 UTC` commit fixes both by caching the no-env answer and keying both sites consistently on affine-quant triples.

### Promoted rules

- **QSA gather vs mask is a measured geometry decision**, not a universal optimization. Gate by actual KV representation, selected-row union, live K/V span, and backend/device crossover.
- If alternative verify routes are not numerically identical, raw TG is partly a content/acceptance metric. Compare **ms/verifier-cycle, BPC, accepted tokens/cycle and output hash** separately.
- The gate that decides to build/select sparse blocks and the consumer that decides to gather them must derive `quantized/dense` from one authoritative physical representation. Never pay selection work that the downstream route then rejects.
- Environment/config lookups on a per-layer verifier path must be warmed/cached; configuration resolution itself can become measurable launch-path overhead.
- The M4 dense-KV ~32K crossover is direct evidence for that machine/config only. It is **not** an M1 threshold, a quantized-KV threshold, or 128K calibration.

This is directly relevant to our Flash implementation and should be included in the initial QSA route ladder rather than added only after the first performance plateau.

## Promoted capacity transfer — vLLM #57057: 4-bit KV changes the long-context concurrency wall

Source created: `2026-09-15 18:40:09 UTC`.

Fresh Qwen3.8/MI355X 262K-request data compares UltraQuant 4-bit KV against FP8 KV. The 4-bit format roughly halves KV storage, but the important result is a **crossover**, not a universal speedup.

Qwen3.8 TP8:

| concurrency | UQ4 tok/s | KV8 tok/s | delta | UQ4 peak KV | KV8 peak KV |
|---:|---:|---:|---:|---:|---:|
| 8 | 193.9 | 199.4 | -2.7% | 8.2% | 14.1% |
| 16 | 280.2 | 288.0 | -2.7% | 17.4% | 32.0% |
| 32 | 374.0 | 363.1 | +3.0% | 35.1% | 66.3% |
| 36 | 398.9 | 299.6 | +33.1% | 39.7% | 82.4% |
| 38 | 414.6 | 225.4 | +84.0% | 44.2% | **100.0%** |
| 42 | 430.7 | 114.7 | +275% | 45.4% | 99.9% |

Qwen3.6-27B TP2 shows the same shape more mildly: UQ loses ~1–2% at low concurrency, crosses around C34, and is +9% at C42 while using roughly half the KV capacity.

Quality cells are not identical: reported GPQA-Diamond is 92.9% UQ4 vs 94.4% KV8 on Qwen3.8 and 85.4% vs 87.4% on Qwen3.6-27B. The authors call this sampling noise, but for our ruler it remains a measured quality difference until a stronger equivalence bar exists. Benchmark bases also differ somewhat, so absolute throughput is indicative rather than target-grade.

### Transfer

- KV precision is a **capacity/latency/quality trade**, not merely a bytes-per-token setting.
- Measure low-concurrency kernel cost separately from the high-concurrency eviction/preemption wall.
- A lower-precision cache may legitimately lose B1 while winning the serving Pareto once the higher-precision cache approaches physical capacity.
- Keep KV4 as an optional capacity/emergency lane for our work unless quality is explicitly requalified; it does not change the preferred Q6/Q8-quality target lane.

No canonical target moves from this.

## Promoted sparse-prefill transfer — vLLM #57078: keep selector output in a consumer-native form

Source created: `2026-09-15 21:17:57 UTC`.

DeepSeek-V4 sparse MLA prefill on one MI355X adds two local-compute changes:
1. tile inverse GPT-J RoPE by eight rows for the production T>=256 shape;
2. let the Triton sparse-attention fallback consume dense top-k indices + per-row lengths directly instead of packing them into a ragged representation first.

Inverse-RoPE microbench:
- T256: 12.83 -> 5.55 us (**2.31x**).
- T1024: 45.90 -> 20.59 us (**2.23x**).
- T8192: 571.90 -> 186.56 us (**3.07x**).

Dense-to-ragged packing eliminated:
- 256x512: 13.05 us.
- 1024x1024: 16.78 us.
- 8192x2048: 85.84 us.

Dense-top-k output matched the existing packed-ragged path exactly for tested widths 5/70/256. TP8 E2E results are still pending, so no request-level speedup is booked.

### Transfer to our QSA/indexer path

- The authoritative sparse selector representation should flow directly into the consumer when possible. Do not pay dense->ragged->consumer conversion purely because an older API expects it.
- Measure representation-conversion kernels as first-class QSA cost, especially at long prefill widths.
- Small row-wise transforms such as RoPE can become meaningfully access/launch-bound and benefit from multi-row cooperative tiling.

This composes with the existing rule to communicate/retain the smallest semantic state rather than producer-internal structure.

## Promoted backend-route transfer — vLLM #57079: capability gating can hide a 2x path

Source created: `2026-09-15 21:21:54 UTC`.

On MI325 at context 32768 / batch 1, the PR enables an AITER Triton MXFP4 MoE path that was incorrectly gated to gfx950 and restores a compiled `forward_native` path for `SiluAndMulWithClamp` that had been inadvertently disabled.

Reported decode:
- DS4-Pro TP4: **22.39 -> 46.49 -> 50.19 tok/s** (base -> MoE fast path -> both), 2.24x overall.
- DS4-Flash TP1: **32.72 -> 64.43 tok/s**, 1.97x overall.

This is ROCm/MI325, a different model/runtime and not our DS4-0731 Apple topology. Do not transfer the magnitude.

### Transfer

Promote the failure mode:
- `supported by architecture` and `actually admitted on this device/build` are separate execution facts.
- Capability guards, compile decorators and backend-family allowlists belong in route provenance.
- When a model unexpectedly lands on a generic path, audit **why the faster physical route did not arm** before writing a new kernel.

This reinforces our existing requested->configured->compiled->admitted->executed provenance chain.

## Promoted distributed correctness update — vLLM #57042 fresh on-GPU validation

Fresh substantive comment timestamp: `2026-09-15 18:56:22 UTC`.

The prior watch had only the PR author's CPU emulation. A new independent gfx1100 on-GPU harness validates the kernel ordering effect and adds a useful chunk-geometry result.

4 logical ranks, same upstream kernel:
- one-stage vs two-stage, identical 2048x5120 FP32 data: **31.28% of elements differ**; BF16 0 in this realistic-random test.
- two-stage 1664x5120 vs the same row prefix inside 2048x5120: **14.86% FP32 elements differ**; BF16 0.
- one-stage 1664 vs 2048 prefix control: 0 difference.
- applying the PR's fixed absolute rank order moved the measured FP32 differences to zero.

The new part is the **seam**: no collective algorithm switch is required. Merely changing total tensor/chunk geometry moves partition ownership boundaries and therefore rank accumulation order on the two-stage route.

### Transfer

- Chunk size / partition geometry can be arithmetic identity in a distributed reduction, not just a performance knob.
- When comparing PP/pre-fill chunk widths, certify whether any collective's partition ownership or reduction order changes with total row count.
- For our two-rank BF16 PP2 path this exact four-rank FP32 failure is **not an active blocker**. Retain it as a correctness/measurement rule, not evidence that our two-M1 path is unstable.

## Promoted speculative-resource rule — llama.cpp #28972

Source created: `2026-09-16 00:04:26 UTC`.

Speculative graphs grow with `--spec-draft-n-max`. A diagnosed case reaches:
- n_max=8: hash capacity 2053; nodes+leafs 2000 -> fits.
- n_max=9: nodes+leafs **2054** -> fixed scheduler hash capacity 2053 -> assert.

The patch grows the scheduler hash set and its per-tensor arrays before graph splitting, using allocator-like headroom instead of assuming init-time graph size remains sufficient. Full end-to-end n_max=9 was not rerun by the author because their AMD/Vulkan fork hits a separate earlier DSpark crash; treat this as a direct resource-contract fix with incomplete E2E validation.

### Transfer to adaptive Lightning MTP

- Max/adaptive speculative depth changes not only tensor rows but **graph metadata cardinality**: nodes, leaves, scheduler bookkeeping, capture slots and side arrays must be sized or growable for the qualified maximum.
- Our depth sweep should assert actual graph resource counts at D1..Dmax and fail cleanly before serving if a fixed-capacity table cannot hold the requested depth.

This complements the previous `selected K -> executed K` rule.

## Supporting / watch-only fresh items

### vLLM #57081 — FP8 o-projection helps prefill more than aggregate decode
Created `2026-09-15 21:28:15 UTC`.
On MI355X DSV4.1-Flash TP4/DSpark C8, a native FP8 o-projection reduced TTFT p50 **566 -> 335 ms (-40.7%)** and ITL p50 5.2 -> 4.69 ms, while output tok/s/chip was 94.44 -> 92.9 (-1.6%, reported within run variance). The fast GEMM is also disabled during graph capture because that path segfaults on gfx950. Useful reminder to separate prefill benefit, decode throughput, and graph-compatibility; no active-target promotion.

### vLLM #57086 — overlap shared-output all-reduce with routed experts
Created `2026-09-15 22:35:02 UTC`. The upstream implementation is fresh, but its quoted ~4% critical-path/throughput numbers are explicitly historical and were not rebenchmarked on this adaptation. Keep the dependency idea — overlap communication with independent expert work using a deliberately low-resource collective — but do not book the historical percentages as fresh evidence.

### ds4-dfm-rs #47 — Ling YaRN 256K / recurrent kernel work
Created `2026-09-15 18:37:48 UTC`. Demonstrates a 262,144-token allocation/smoke on one GB10 and reports an 8K KDA BF16 decode-pair improvement. Ling-3.0 is not an active model lane and Metal is not qualified, so this remains hybrid-runtime background only.

## Fresh main-branch activity / timestamp discipline

- mlx-serve merged #434 at 19:18:07 UTC and #436 at 19:07:47 UTC. Their substantive measurements were already captured in earlier watches; merge time does not refresh them.
- vLLM and llama.cpp merged several older PRs during this window. Their underlying measurements predate the hard boundary; no evidence timestamp was advanced from those merges.
- oMLX exposed no new performance PR created after this window's boundary; #3685 remains the most recent relevant Apple performance/correctness item and was captured in the prior watch.

## External HF / community screen

Fresh web crawling surfaced several useful historical cards/discussions, but no source-time-qualified exact active-topology receipt inside this hard window.

Examples retained only as background calibration:
- an M1 Max 64 GB Flash-Next DS4 IQ2 discussion remains short-context and does not have MTP on that branch;
- a 5070 Ti 16 GB Qwen3.8-27B long-context runtime report is several days old and uses a different quant/runtime;
- dual-Strix and DGX/GX10 Flash cards are useful architectural context but not dual-M1 evidence.

Per standing methodology, crawler freshness and card modification time do not advance the hard evidence boundary.

## Target status

Canonical targets remain unchanged:

- Qwen3.8-Flash-Next dual M1 Max64/TB4: **40 tok/s @ ~128K active context**, **400 tok/s cold PP**.
- Qwen3.8-27B one M1 Max64: **25 tok/s**, **110 tok/s native/exact-runtime cold PP**.
- Qwen3.8-27B RTX5070Ti16 + host RAM: **120 tok/s**, **250 tok/s cold PP**.
- DS4-0731 dual M1 Max64/TB4: **15 tok/s**, **180 tok/s cold PP**.

No P69 reorder/reopen.

## Planning impact

Add or strengthen these rows in the implementation/tuning ruler:

1. QSA verify `mask vs gather` crossover by physical KV scheme and live context; measure verifier round cost separately from TG/acceptance.
2. One authoritative KV-representation predicate from selection gate through gather consumer; no paid-and-discarded selector.
3. Cache/warm configuration resolution used in per-layer verify hot paths.
4. Keep alternative QSA arithmetic-route identity in the output-hash/correctness receipt.
5. KV precision lane reports low-concurrency kernel cost, physical-capacity/eviction crossover, and quality separately.
6. Preserve sparse selector output in a consumer-native representation; measure dense/ragged packing explicitly.
7. Audit device/backend capability gates before assuming a fast physical route is unavailable.
8. Treat distributed chunk/partition geometry as possible reduction-order identity.
9. Size graph metadata/bookkeeping across D1..Dmax, not merely model tensors; adaptive depth requires scheduler-resource qualification too.
10. Preserve separate prefill/TTFT, decode/ITL and aggregate-throughput bars for precision fast paths whose benefits are phase-dependent.

This pass is positive for the eventual Flash tuning campaign because #439 gives us a concrete Apple QSA crossover to test from day one. It still provides **no exact dual-M1 128K calibration**, so 40/400 remains the correct canonical planning target.

## New hard freshness boundary

`2026-09-16 00:15:16 UTC`
