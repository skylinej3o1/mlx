# Runtime Research Watch — 2026-09-02 09:45 ET

Scope: fresh delta after `RESEARCH-WATCH-2026-09-02-0530.md`, with canonical-state-first classification. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B, and DeepSeek-V4-Flash/DS4, especially 2x M1 Max 64 GB / TB4 and 3-4-agent serving economics.

This pass does **not** change the certified exact-Q8 verifier state. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling data only**.

## Executive delta

1. **NEW — oMLX #3359 is the strongest new 64-GB-class capacity/headroom lead.** It adds exact-routing SSD expert streaming for Qwen3.8-Flash-Next and DeepSeek V4. A separate M5 Pro 64 GB validation ran Flash-Next oQ2-MTP at only ~32.7 GB resident and 25-28 tok/s warm after correctness fixes. The PR's best development run reaches 40.36 tok/s with 32.23/34.09 GiB loaded/peak memory, but the PR body does not name that development machine, so the absolute result is **not** an M1 calibration.
2. **NEW/IMPORTANT CAUTION — exact native-demand SSD routing is not free on Apple Silicon.** Follow-up measurements on the M5 Pro found ~217 us/layer total route turnaround versus ~67 us for a plain gather. The incremental host round-trip is about 150 us/layer, implying roughly **7 ms extra per 48-layer decode step** even when the expert is already resident. This makes streaming a capacity/headroom track, not the preferred hot path when full residency is available.
3. **NEW — streamed PLE prefill needs explicit prefaulting.** The same follow-up found Qwen4-Exp PLE mmap gathers touching 16,368 random rows for a 1023-token prompt; page-cache eviction produced 3.6-10 s bimodal prefill. Parallel page prefaulting stabilized seven runs to 3.57-3.89 s. This reinforces the existing rule: do not put synchronous random mmap faults on the inference thread.
4. **UPDATE — llama.cpp #28213 got an independent long-context confirmation.** On a very different multi-GPU host, a 65.7K prompt measured 15.5 -> 19.6 tok/s (+26%) at ~60K with gathered selected-K/V and no short-context regression at 2K. More importantly, the tester identifies full-context `build_qsa_top_k` selection as the next context-scaling bottleneck after attention is made O(top-k).
5. **NEW sibling implementation — llama.cpp #28244.** It also gathers only QSA-selected cells, but gates the path until cache depth is >=4x the selected width. RTX PRO 6000 / UD-Q4_K_XL / q8 KV: 4K stays 103.4 tok/s while 50K rises 73.2 -> 78.9 tok/s (~+8%). Unlike #28213's reported short-context -4% on the same reporter's comparison, this guarded path avoids the 4K tax. At depth it is not bit-identical to master because the reduction order changes, so exactness policy matters.
6. **NEW upstream-maturity lead — llama.cpp #28243.** A new draft PR adds dedicated Qwen3.8-Flash-Next MTP support and shared MTP modules, reusing `embed_tokens` to save RAM/disk. The PR claims 1.3-2x faster MTP but currently publishes no hardware/benchmark table, so it is a tracking lead rather than forecast evidence.
7. **NO CHANGE — exact dual-M1 evidence.** llama.cpp #27993 has no new comments; DS4 #922 has no new comments; DS4 #861 has no new distributed-serving comments. There is still no sustained dual-M1 Flash-Next TG receipt and no sustained 0731 dual-M1 TG receipt.
8. **NO CHANGE — MTP requalification cautions.** oMLX #3370 has no maintainer response to the temp>0 acceptance-collapse report; #3320 has no fresh requalification result. `ARahim3/mlx-dspark` has no new code push after 2026-09-01 10:54 UTC.

Net: **do not move the B1 or B2-B4 forecast bands.** The new evidence improves confidence that a 64-GB-class node can trade SSD bandwidth for substantial workstation/agent headroom, but it simultaneously shows why our mature 2x M1 Max design should prefer a resident hot execution path whenever possible.

## NEW — oMLX #3359 exact-routing SSD expert streaming

Source: https://github.com/jundot/omlx/pull/3359

The PR adds an opt-in streamed-MoE runtime with:

- `soft_reap` pinned-hot-expert residency or `cache_only` zero-pinned residency;
- route-frequency or LRU expert caches;
- prompt scratch banks that can be lent to decode-cache capacity;
- Apple Metal I/O with direct publication into proven-idle exact-format slots;
- native-demand callbacks at MLX evaluation boundaries;
- learned hot-list persistence and telemetry;
- Qwen4-Exp awareness: 48 backbone MoE layers streamed, shared experts + separate MTP expert remain resident, and the large PLE remains SSD mmap-backed.

### PR headline development result — hardware not named in body

Qwen3.8-Flash-Next oQ2-MTP, `cache_only`, zero pinned routed experts:

- cache / scratch: 288 / 32 experts per layer;
- decode bank: 320 / 512 rows after scratch lending;
- loaded / peak MLX memory: **32.230 / 34.092 GiB**;
- 901 prompt / 128 generated tokens;
- prompt processing: **362.306 tok/s**;
- token generation: **40.3625 tok/s**;
- fixed MTP depth 3;
- 100% acceptance in the forced trajectory;
- 2,553 JIT expert loads;
- 15.496 GB logical expert reads.

Across three matched direct-I/O runs, the PR reports mean 363.00 PP / 39.62 TG versus 353.23 / 32.62 for staged publication, a reported +21.47% TG improvement from removing the destination blit while preserving routing trajectory.

**Classification:** strong architecture evidence, but not M1-Max evidence. The PR does not identify the development machine for the 40.36 tok/s headline and uses oQ2 plus a forced high-acceptance MTP trajectory.

### Independent M5 Pro 64 GB validation

Source: https://github.com/jundot/omlx/pull/3359#issuecomment-5500837620

A contributor tested the branch on **M5 Pro 64 GB** with Qwen3.8 Flash Next oQ2-MTP (66 GiB checkpoint):

- ~32.7 GB measured resident;
- ~25-28 tok/s warm with MTP depth 3 after fixes.

The test also exposed two correctness/runtime bugs before those fixes were merged into the source branch:

1. `mx.synchronize()` could deadlock because the miss-path completion handler needed the GIL; a GIL-releasing synchronize path was added.
2. The native-demand fast path could read a stale slot map from the graph built one step earlier and diverge nondeterministically; resolving routes through the callback restored exact output at the same throughput in the tester's eager reference case.

The contributor also found the residency estimator counting a PLE that streaming had forced onto mmap, reporting ~52.6 GB estimated versus ~32.7 GB measured and falsely refusing admission on 64 GB hardware.

### Implication for our 2x M1 Max plan

This is meaningful because it demonstrates a **real 64-GB Apple node** running Flash-Next with roughly half of nominal unified memory occupied by the streamed runtime. It strengthens the idea that the primary M1 can preserve workstation/Hermes headroom if necessary.

But it does **not** imply that our dual-M1 production path should stream all experts. M5 Pro has newer GPU/Metal characteristics, the tested checkpoint is oQ2, and the follow-up route-latency measurement below gives a concrete reason to keep the hot execution path resident when two 64-GB machines together have enough physical memory.

## NEW — native-demand route turnaround has an Apple-Silicon floor

Source: https://github.com/onthehub97/omlx/pull/2

The follow-up was tested on the M5 Pro 64 GB branch and merged into the #3359 source branch.

Measured with every expert resident:

- native-demand route turnaround: **~217 us/layer**;
- plain gather control: **~67 us/layer**;
- GPU finish -> CPU observes completion: ~47 us;
- CPU signal -> next command buffer starts: ~106 us.

The author tested a dedicated polling thread, GPU-signalled shared event, busy second queue, and GPU-side spin-gate ideas. None removed the host round-trip. A running Apple GPU kernel did not reliably observe CPU stores quickly enough for a practical spin gate.

The important number is the **incremental ~150 us/layer** versus a plain gather. Across 48 layers that is roughly **7.2 ms/decode step** before SSD miss service itself.

### Durable design implication

For our pair:

- **resident experts remain the preferred hot path** when capacity permits;
- SSD expert streaming is a **capacity/workstation-headroom mode**, not a free speed optimization;
- if streaming is used, maximize cache hit rate and avoid unnecessary native-demand round trips;
- do not assume that "all experts happen to be cached" eliminates the callback cost.

This makes the eventual workstation-mode policy more concrete: first solve the asymmetric PP/resident allocation; use expert streaming selectively only if the primary's desired headroom or 3-4-agent state requires it.

## NEW — Qwen4-Exp PLE prefault removes streamed-prefill bimodality

Source: https://github.com/onthehub97/omlx/pull/2

With expert streaming enabled, Qwen4-Exp's PLE remained SSD mmap-backed. A 1023-token prompt touched **16,368 rows across 128 shards** through a random-access numpy gather. When those pages were not already cached, the inference thread blocked on synchronous SSD page faults and the GPU sat idle.

Before:

- same prompt could finish around 3.6 s when pages were hot;
- or take roughly 6-10 s after page-cache eviction.

After coalescing page ranges and prefaulting them on a 16-worker read pool:

- seven consecutive runs: **3.57-3.89 s**;
- gather itself: ~0.35-0.53 s.

The same follow-up replaces a 200-us polling wait that macOS timer coalescing could stretch toward a millisecond with a completion semaphore, pools 64-MB staging buffers, and allows bounded scratch-prefetch depth.

### Implication

This reinforces #3372 rather than replacing it: **SSD PLE can be viable, but random faults and host waits must be removed from the inference thread.** It is especially relevant if our M1 workstation mode SSD-backs PLE while keeping experts resident.

## UPDATE — llama.cpp #28213 confirms gathered-QSA win and exposes next bottleneck

Source: https://github.com/ggml-org/llama.cpp/pull/28213

A new independent test used Qwen3.8-Flash-Next UD-Q3_K_XL, q8 KV, no speculative decode, a 65,715-token prompt, and a very unusual 8-GPU PCIe-Gen1 system:

- gather OFF at ~60K: **15.5 tok/s**;
- gather ON: **19.6 tok/s**;
- delta: **+26%**;
- ~2K decode: **39.8 tok/s** in both modes.

The transferable result is not the absolute speed. Once attention itself is bounded to the selected ~2K cells, `build_qsa_top_k` still scores/selects over the full expanded context every token. On this machine it became the dominant remaining context-scaling term.

This validates an already-known seam in `RESEARCH-STATE.md`: **after selected-K/V gather, QSA/indexer top-k acceleration is the next long-context target.**

## NEW sibling — llama.cpp #28244 guards selected-cell gather by depth

Source: https://github.com/ggml-org/llama.cpp/pull/28244

This is a separate one-commit implementation of the same architectural shape. It only takes the compact selected-cell path when the cache is at least 4x deeper than the top-k width.

RTX PRO 6000, UD-Q4_K_XL, q8 KV, TG 1024:

| Path | 4K | 50K |
|---|---:|---:|
| master | 103.4 | 73.2 |
| #28244 | 103.4 | 78.9 |

So the deep-context gain is about +7.8% while short context is unchanged. A same-reporter comparison reported #28213 at 99.7 tok/s at 4K and 79.9 at 50K, i.e. slightly more depth gain but ~4% short-context cost in that implementation.

Caution: #28244 says depth outputs are not bit-identical to master because the flash-attention reduction order changes over the compact selected set. That is acceptable only as a lossy/numerically-different runtime track unless exact parity can be re-established.

## NEW tracking lead — llama.cpp #28243 dedicated Flash-Next MTP

Source: https://github.com/ggml-org/llama.cpp/pull/28243

Created 2026-09-02. Draft PR from Daniel Hanchen / Unsloth adds dedicated Qwen3.8-Flash-Next MTP support on top of the shared MTP infrastructure and reuses `embed_tokens` to reduce disk/RAM duplication.

The PR headline says **1.3-2x faster MTP**, but there is currently no benchmark table, machine, context, acceptance rate, or sampling configuration in the PR body and no comments.

**Classification:** NEW upstream-maturity lead, not performance evidence. Track for Apple support, memory behavior, and whether its acceptance/rejection semantics address the temp>0 concern in oMLX #3370.

## DS4 / distributed / exact-frontier checks

### DS4 #922 — no change

No comments since the 05:30 consolidation. Still no completion-token count or sustained dual-M1 0731 TG.

### llama.cpp #27993 — no change

No comments since the 05:30 consolidation. Still no dual-M1 Flash-Next throughput or posted result for the previously-started 115K/256K correctness run.

### DS4 #861 — no change

No new distributed-serving comments. Existing qualitative result remains: pipeline/layer split minimizes interconnect traffic versus chatty TP on Thunderbolt-class links, while multi-session distributed decode still needs row-batched/coalesced execution to become a true concurrent throughput path.

### DS4 #621 — active but no M1-topology delta

Fresh discussion is primarily GB10/CUDA quality and Q4/Q8 requalification. It does not change the Apple/TB4 architecture decision in this pass.

### DFlash2 / mlx-dspark

Repository metadata shows no new code push after 2026-09-01 10:54 UTC and no fresh issue activity in the current pass window.

## Forecast consequence

### Short/medium-context mature dual-M1 Flash-Next B1

**Unchanged:**

| Target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

### ~128K active-context B1

**Unchanged:**

| Target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate

**Unchanged:**

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

### What did change conceptually

The capacity ladder is stronger:

- a 64-GB-class Apple node can run Flash-Next with ~33 GB measured residency in a streamed oQ2 mode;
- therefore preserving meaningful workstation/Hermes headroom on the primary is increasingly plausible;
- however, streaming every routed expert introduces an Apple host-round-trip floor that is large enough to matter to decode;
- on our **2x 64-GB M1 Max pair**, use the extra physical RAM to keep the performance-critical execution path resident first, then selectively SSD-back PLE or colder expert capacity only when the workstation/agent memory budget requires it.

The user's desired **~400 tok/s prefill + strong prompt/prefix caching** remains a sensible mature-system target. This pass does not provide a dual-M1 400-PP measurement; the new streamed-M5-Pro data mainly tells us how to avoid I/O-induced prefill variance if SSD backing is used.

## Revised eventual bring-up emphasis

Keep the existing test ladder, with these additions before distributed tuning if any weight class is SSD-backed:

1. measure full-resident single-M1 baseline first;
2. separately A/B PLE-only SSD backing and routed-expert streaming;
3. record route callback count, expert-cache hit/miss rate, direct/staged I/O bytes, and per-token native-demand time;
4. force cold-page PLE tests, not only warm page-cache runs;
5. require exact greedy trajectory after cache evictions/refills;
6. only then combine SSD backing with PP2 and multi-agent scheduling.

PP2 remains primary; TP2 remains the controlled falsification benchmark. No external result changes P69B13 selection.
