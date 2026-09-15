# External runtime watch — 2026-09-14 23:44 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-14 22:42:15 UTC` through the user-request cutoff `2026-09-15 03:44:23 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, comment-only activity, or a later merge of already-known measurements.

**New hard source-freshness boundary for the next complete external search: `2026-09-15 03:44:23 UTC`.**

The prior cutoff-edge item, vLLM #56908 (created `2026-09-14 22:49:17 UTC`), was examined first in this pass.

---

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured internal GDN/projection/downstream-tail evidence.**

---

# Fresh evidence

## mlx-serve #431 — semantic media-boundary bug destroyed highest SSD hybrid restore

Source PR #431 created `2026-09-15 01:11:43 UTC`, merged `2026-09-15 02:30:16 UTC` as commit `1bf485297cc63e53d7cc2f96a75c845bed407545`.

**FRESH DIRECT APPLE / QWEN3.8-FLASH-NEXT PREFIX-CACHE + LONG-CONTEXT STATE EVIDENCE.**

On a hybrid Qwen3.8-Flash-Next path, a byte-identical text-only conversation at roughly 73K tokens restored almost none of its useful SSD prefix after restart:

- before: **16,384 / 73,398 tokens restored**, **34.2 s** wall;
- RAM-tier control on the same request matched about **73,293** tokens in ~2.0 s;
- the same low-checkpoint cap recurred on mid-session disk restores from roughly 61K through 229K prompt lengths.

The disk tier's ranking algorithm itself was not the defect. `firstMediaPlaceholder` scanned raw token ids for image/audio/video placeholder ids even when the request contained no media. Those ids are ordinary vocabulary entries too. This text conversation happened to contain `248056` (`image_token_id`) at position 18,338, so the scheduler invented a media boundary there.

That false boundary became the hybrid disk lookup's hard `limit`. The donor covering the full prefix had checkpoints starting at 49,152 and therefore had no checkpoint at or below the false 18,338 limit; it was rejected. A stale entry with a 16,384 checkpoint won instead.

The fix conditions placeholder interpretation on actual media state (`vision_embeddings != null`), so raw token equality alone cannot create a modality boundary. The same corrected value also keys checkpoint inheritance/thinning.

Live after the fix, same conversation/flags:

- **73,293 / 73,375 tokens restored**;
- wall **1.6 s**;
- mid-session restores also reached deep checkpoints rather than collapsing to 16,384.

The disk-tier ranking contract was additionally pinned across a fresh restart: choose the **highest restorable checkpoint** at or below the valid semantic match boundary.

**Project consequence:** a raw token value is not sufficient proof of semantic modality state. Prefix-cache identity for Flash must carry the modality-presence side channel that gives placeholder ids meaning. Our long-context ruler should include text-only prompts containing special/placeholder token ids by coincidence and prove that restart restore chooses the highest semantically and physically restorable committed recurrent checkpoint. This is directly relevant to long agent histories and SSD-backed QSA/GDN/PLE state.

## mlx-serve #432 — exact shortlist top-k/top-p avoids full-vocabulary Metal ranking

Source PR #432 created `2026-09-15 01:30:40 UTC`, merged `2026-09-15 02:54:36 UTC` as commit `ff3d7574faf9300aeec7f09600cc7227b69856f5`.

**FRESH DIRECT APPLE / FLASH-NEXT SAMPLED-DECODE MECHANISM EVIDENCE.**

The old sampled path ranked the full vocabulary every token. On the pinned MLX Metal backend, `Partition` and `ArgPartition` currently route to the same multi-block merge sort, so `mlx_topk` / `mlx_argpartition` do **not** imply a cheap physical partial-selection path.

The replacement constructs an exact bounded shortlist by ranking chunk maxima and only the candidate chunks that can contain the top-m values. It preserves the sampler's rank contract:

- descending value order;
- deterministic ties by lowest original column id;
- candidate layout in ascending original-column order before the stable rank;
- top-p mass computed as an exclusive scan over the ordering;
- f32 accumulation for the nucleus even when logits are bf16.

That last item matters: the old bf16 cumsum dropped **148 of 3,720** nucleus columns on one 248,320-wide probe row.

Correctness coverage includes 248,320-wide rows, all-equal/tie-heavy rows, rank-3 `[B,L,V]` blocks matching stochastic MTP verification shape, byte-identical filtered logits for the shortlist route, identical sampled token under matched keys, and 2,531 passing tests.

A live M4 Max / Qwen3.8-Flash-Next mixed-4/8-bit / no-MTP / 256-token A/B against a **pre-rank baseline** reported:

- `top_p=0.95 + top_k=20` filter cost: **1.13 -> 0.51 ms/token**;
- absolute decode: **60.5 -> 64.0 tok/s**;
- greedy control moved **65.0 -> 66.1 tok/s** between boots.

Important qualification: the author explicitly marks a fresh A/B against the immediate `bdcf5a1d` rank-correct baseline as pending. Pure top-p remains full-rank by design, and our canonical greedy ruler returns before either filter.

**Project consequence:** high-level sampler API names are not physical execution identity. For sampled agent workloads, record the physical selection implementation, sampler route census, ms/token, tie policy, accumulator precision and whether top-k actually executes as a partial selection or a full sort. Keep this separate from the canonical greedy TG ruler. Do not book the 60.5 -> 64.0 absolute delta as a clean current-stack gain until the fresh paired A/B lands.

## oMLX #3669 — Apple SDPA launch geometry can silently exceed device limits

Source PR #3669 created `2026-09-15 00:43:10 UTC`.

**FRESH DIRECT APPLE / QWEN3.8-FLASH-NEXT KERNEL-ADMISSION CORRECTNESS EVIDENCE.**

The investigation used `Qwen3.8-Flash-Next-oQ5e-mtp` on an **M2 Ultra 192 GB**, testing oMLX 0.7.0.dev2 behavior. The primary PR concerns a tool-call envelope being silently discarded by API logic; that part is agent-quality plumbing rather than an inference optimization.

During the investigation, however, a separate GPU defect was isolated: some `decode_fast` SDPA kernels could launch thread groups larger than certain Apple GPU generations permit. Metal could silently skip those launches and leave stale/uninitialized output rather than producing a clean high-level failure. The repo's own fp32 decode tests failed on the affected M2-class geometry. The proposed fix adopts MLX-style residency/launch checks, and the `decode_fast` fp32 `d=128` tests pass on the affected g14d device where pristine dev2 fails.

The report also notes a separate long-context stall around ~90K cached tokens on oMLX 0.6.4; that remains under investigation and is **not** explained or fixed by this PR.

**Project consequence:** compiled/selected/armed is still weaker than valid execution. Our Metal route provenance must include per-device threadgroup/residency limits and a launch-validity gate, especially for specialized QSA/SDPA kernels transferred from newer Apple GPUs to M1 Max. Poison/sentinel output tests should prove the kernel actually executed rather than silently preserving stale memory. The ~90K stall is an open signal only and does not move any target or mechanism assumption.

## vLLM #56926 — serializing offloaded Engram lookups can reduce compute interference

Source PR #56926 created `2026-09-15 01:34:05 UTC`.

**FRESH DISTRIBUTED/OFFLOAD SCHEDULING TRANSFER.**

Two CPU-offloaded DeepSeek-V4.1 Engram lookups previously ran on separate CUDA streams while decoder GEMMs ran concurrently. The streams competed for resources. The PR gives both lookups one shared stream while retaining a separate completion event per layer, so consuming the first result does not wait for the second lookup to finish.

Scoped GB200 harness: four MXFP8 compute GEMMs alongside two production UVA lookups, 8,192 tokens, TP4 rank-0 shard, ~22.89 GiB table per Engram layer.

| Measured time | Two lookup streams | One shared stream |
|---|---:|---:|
| compute finished | 3.528 ms | 0.697 ms |
| everything finished | 3.549 ms | 3.033 ms |

Compute alone was 0.283 ms. Across two 60-pair runs, paired median savings were about **2.83 ms** to compute completion and **0.50 ms** to all-work completion. Compute improved in every pair; total completion improved in 54/60 and 50/60 pairs. Exact lookup/GEMM output comparisons passed. No full decoder, collectives or E2E serving result is claimed.

**Project consequence:** overlap is not automatically free. For Apple PLE/Engram/SSD reads running beside Metal compute, explicitly compare parallel versus intentionally serialized scheduling and record critical-path compute finish, all-work finish, storage bandwidth, GPU occupancy and subsequent wait time. Preserve independent readiness events even when producers share a serialized resource. This complements the earlier small-Engram-read and command-buffer wait findings.

## vLLM #56929 — fuse post-gather reordering, padding removal and quantization

Source PR #56929 created `2026-09-15 02:04:09 UTC`.

**FRESH DISTRIBUTED DATA-MOVEMENT + QUANTIZATION TRANSFER.**

DeepSeek-V4.1 Engram TP gathering produced rank-major rows, while the replicated `wkv` projection consumes token-major input. The old non-SP path materialized a BF16 reorder clone and then quantized it. At 8,192 tokens x width 6,144, the intermediate alone is **96 MiB**.

The new path gathers once along the transport-friendly dimension, then a fused kernel:

- reorders rank-major -> token-major;
- removes padded heads;
- quantizes directly to MXFP8 + scales;
- hands the resulting `QuantizedActivation` directly to `wkv`, avoiding another activation-quantization pass.

There is still exactly one all-gather. Two-GPU all-gather correctness and bitwise FP8/scales were tested, including graph replay.

Scoped GB200 operation timings, excluding all-gather/lookup/GEMM:

| Tokens | Old reorder + quantize | Fused | Speedup |
|---:|---:|---:|---:|
| 1 | 2.176 us | 2.016 us | 1.08x |
| 128 | 7.360 | 2.560 | 2.88x |
| 1,024 | 23.392 | 7.648 | 3.06x |
| 8,192 | 143.935 | 52.544 | 2.74x |
| 8,192, padded-head case | 247.008 | 50.432 | 4.90x |

For the 8,192 x 6,144 case the net saving is **91.4 us (63.5%)**, eliminating about **192 MiB** of standalone BF16 read/write traffic.

**Project consequence:** extend the prior "collapse before transport" rule through the consumer boundary: transport/gather only once, then perform layout conversion, padding trim and quantization in one producer-to-consumer handoff whenever the next kernel accepts the compact representation. For TB4 PP2, inventory every transferred state for post-receive clones, transposes, padding removal and requantization. Record physical bytes moved both over TB4 and locally after receipt.

## vLLM #56932 — sparse decode decomposition must be bounded by physical page-table capacity

Source PR #56932 created `2026-09-15 02:57:22 UTC`.

**FRESH SPARSE-ATTENTION WORK-DECOMPOSITION TRANSFER.**

MiniMax-M3 small-batch sparse decode exposed too little parallel work inside a page and could schedule splits beyond the page-table's physical capacity. The patch splits pages for more parallelism, bounds split count using CPU-visible table capacity, skips empty slices on device, and only takes a direct single-page path when the physical table is actually one column wide.

RTX 5090 / SM120 operator matrix: 72 cases spanning shapes and BF16/FP8 KV modes, CUDA Graph timing, 256-column preallocated page table.

Repeated geomean speedups:

- BF16 KV: **~1.097x**;
- FP8 scalar: **~1.285x**;
- FP8 per-token/head: **~1.376x**;
- all 72 cases: **~1.247x**;
- worst case remained ~0.99x; max relative RMS error against dense reference 0.3269%.

The author explicitly notes that production metadata slices page-table **rows**, not columns: short logical context does not imply a physically one-column table. These are operator numbers, not serving/model throughput.

**Project consequence:** QSA work decomposition must use physical metadata capacity as well as live logical context. Add page/block-table width, padded capacity, empty-slice count and scratch/LSE clearing semantics to sparse execution identity. A live-span optimization is insufficient if the underlying physical metadata remains padded to a larger capacity. Benchmark occupancy/parallelism using the actual padded shapes our M1 path will carry.

## vLLM #56935 — mega sparse attention shows fusion admission depends on live/padded geometry

Source PR #56935 created `2026-09-15 03:21:41 UTC`, updated before the cutoff at `03:41:41 UTC`.

**FRESH SPARSE-ATTENTION FUSION / LAYOUT TRANSFER.**

The proposed DeepSeek-V4.1 FlashMLA mega-attention backend fuses Q normalization, RoPE, sparse attention, inverse RoPE and output FP8 cast in one launch, writing directly into the representation consumed by `wo_a`. It declares those producer/consumer capabilities explicitly so the generic framework can bypass redundant normalization/projection steps.

Additional physical-layout work:

- one caller-provided output buffer pair spans the step;
- prefill chunks and decode segment write disjoint token ranges;
- one downstream FP8 einsum consumes the whole N-token output;
- `wq_b` rows and `wo_a` columns are permuted once at load time into the kernel-native layout rather than shuffled every step;
- the mega backend uses a compact NVFP4 cache record where supported and rejects incompatible cache/backend combinations rather than silently falling back.

GB300 graph-mode decode microbenchmark, mega / split-KV microseconds:

- **64 live heads:** 29/29 at `s_q=1`, 29/31 at 32, 31/40 at 128, 53/72 at 256, 95/140 at 512 — up to ~**1.47x**;
- **16 live heads:** 31/29, 31/29, 33/33, 59/57, 107/108 — effectively a wash.

The decisive variable is **live heads relative to padded heads**, not merely batch size. Prefill is unmeasured. There is no E2E served-forward result or accuracy measurement on the mega path yet.

**Project consequence:** megafusion admission must be based on actual live:padded geometry and stage ownership, not a generic "fused is faster" rule or a batch-size threshold. For Apple QSA/Flash kernels, consider load-time weight permutation and direct consumer-native output, but benchmark M1-specific head/group padding under the exact PP2 split. Do not transfer the CUDA percentages.

---

# Screened but not promoted

## vLLM #56908

Created `2026-09-14 22:49:17 UTC`, the prior pass's cutoff-edge item. It makes MRV2 tolerate systems without pinned-memory/UVA support, especially WSL. No throughput or active-target mechanism receipt; screened and closed as a compatibility fallback rather than promoted into the Flash tuning sequence.

## Other fresh vLLM speculative/configuration fixes

#56928 derives offload namespace cache dtype from the worker-reported physical KV specs rather than a scheduler knob; #56930/#56933 prevent dense speculative drafters from inheriting target expert parallelism; #56936 avoids building a mismatched target/draft `VllmConfig` for Gemma4 MTP. These reinforce existing standing rules that configured dtype is weaker than executed/normalized dtype and that proposal/draft topology is distinct from target topology. They do not add a new target receipt or justify P69 sequencing changes.

## ds4 #1052

Fresh ROCm/Fedora link fix for `libamdhip64`; no active Apple/Flash/DS4 performance or correctness consequence for this project.

## llama.cpp #28919

Fresh SenseNova U1 model support only. No new Qwen3.8/Metal/long-context optimization after #28918 in the prior watch was found in this window.

## oMLX #3669 API half / #3668

The tool-call-envelope fix in #3669 is useful agent-quality plumbing but is not an inference optimization. #3668 corrects multiple-choice answer extraction. Neither moves runtime targets. Only #3669's independently discovered Apple SDPA launch-validity defect is promoted above.

## External HF / Reddit / community screen

The screen surfaced additional Apple and RTX Qwen3.8 reports, but the useful hits were older than this source-time window or lacked an exact substantive source timestamp. Under the standing freshness rule they do **not** advance the hard boundary, calibrate the active topology or move targets.

---

# Fresh-screen negatives

- No exact fresh **dual-M1 Flash-Next** TG/PP receipt.
- No exact fresh **M1 Max64 Qwen3.8-27B** target-topology receipt.
- No source-time-qualified fresh **RTX5070Ti16 Qwen3.8-27B** controlled receipt matching the canonical lane.
- No exact fresh **dual-M1 DS4-0731** receipt.
- No evidence justifies moving **40/400**, **25/110**, **120/250** or **15/180**.
- No evidence justifies reopening or reordering P69.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 control. Add/reinforce these work items:

1. **Semantic prefix-restore boundary gate:** text-only prompts containing special media-token ids must not acquire a modality boundary without actual media state. Cold-restart tests at 64K/~96K/~128K should prove highest-restorable committed checkpoint selection across KV + GDN/QSA/PLE state.
2. **M1 launch-validity gate:** every specialized Metal QSA/SDPA route must certify threadgroup/residency geometry on the actual M1 Max generation and prove execution with poison/sentinel output checks.
3. **Physical sparse metadata census:** record page/block-table capacity, padded columns/heads/groups, live span and empty work units. Optimize the physical work shape, not only the logical context length.
4. **Consumer-native PP handoff:** after TB4, fuse any reorder, padding trim, quantization and projection-input preparation that can avoid a high-precision temporary or a second pass. Record TB4 bytes plus local post-receive read/write traffic.
5. **Overlap-versus-interference A/B:** for PLE/Engram/SSD reads and Metal compute, benchmark parallel streams/queues against selective serialization. Track critical-path compute completion separately from all-work completion.
6. **Sampled-agent ruler separate from greedy:** sampler route census, physical top-k implementation, full-rank fallback, tie policy and ms/token belong in sampled workloads. The canonical greedy TG ruler remains sampler-filter-free.
7. **Fusion admission by live:padded geometry:** before enabling a large QSA/attention fusion, measure exact stage-local live heads/groups versus padded geometry. Consider load-time weight permutation if it removes repeated step-local shuffles.
8. Retain the prior persistent-state ownership/concurrency, collapse-before-TB4, workspace-view lifetime, long-context coalescing, sparse sentinel/tail, compact selected-K/V QSA, incremental indexer, transient-aware PP chunking, distributed MTP consensus/rollback and exact PP ownership gates.

The fresh evidence exposes **additional optimization seams**, but none is an exact dual-M1 calibration. The canonical **40 tok/s @ ~128K / 400 cold PP** remains the correct planning objective.

## Qwen3.8-27B M1 / P69

No target or sequence movement. **P69B12 remains frozen/promoted; P69B13 remains next.**

#432's sampler lesson applies if we benchmark stochastic agent workloads, but the canonical Q8/Q6 greedy rulers should not absorb it. #56929's general lesson about avoiding post-collective high-precision layout temporaries may matter only if/when a matching internal measured shape appears; it does not reopen P69 externally.

## RTX5070Ti16

No target movement. #56932 is native SM120 sparse-attention mechanism evidence, but it is MiniMax-M3 operator work rather than the canonical Qwen3.8-27B execution path. Retain the physical page-table/padded-shape lesson alongside the existing SM120 kernel-image/fallback, physical-stride and concurrent-long-prompt gates.

## DS4-0731 dual M1

No target movement. #56926/#56929/#56935 provide useful Engram/sparse scheduling and layout ideas, but all benchmark receipts are CUDA-side and not the active Apple topology. Keep them as mechanism-transfer candidates only.

---

# Standing rules added / reinforced

- **Raw token equality is not semantic modality state:** special/placeholder ids require the side-channel state that gives them meaning before they can constrain cache inheritance or restore.
- **Prefix restore chooses the highest valid committed state boundary:** shared-token length alone is weaker than the highest semantically and physically restorable recurrent checkpoint.
- **High-level MLX op names are not physical-cost identity:** `topk` / partition may execute as a full sort; record the actual backend route and route census.
- **Sampler exactness includes deterministic rank/ties and accumulation precision:** tie order and f32-vs-bf16 scan behavior can change the nucleus even when the headline sampling parameters are identical.
- **Async overlap can lose to controlled serialization:** measure resource interference and critical-path completion; preserve independent readiness even when producers share a stream/queue.
- **Fuse representation changes at the consumer boundary:** reorder + padding trim + quantization should avoid a materialized high-precision transient when the consumer accepts the compact representation.
- **Sparse work decomposition is bounded by physical metadata capacity:** logical live length does not imply compact page/block-table geometry.
- **Fusion admission depends on live:padded geometry:** a megakernel that wins at dense live-head utilization can be neutral or worse after sharding/padding.
- **Load-time layout work can replace repeated step-time shuffles:** pre-permute weights when a specialized route has a stable physical layout contract.
- **Kernel admission includes per-device launch validity:** compiled/selected/armed is not enough; threadgroup/residency limits and proof of actual execution belong in route provenance.
- **Community results without exact source time do not advance the hard freshness boundary or canonical targets.**
- Exact target receipts remain distinct from mechanism transfer, experimental A/Bs and planning targets.
