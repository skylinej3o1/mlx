# External runtime research watch — 2026-09-10 14:14 ET

## Scope and freshness

This delta continues from the prior hard source-freshness boundary:

**2026-09-10 13:23:11 UTC**

Search covered oMLX, rMLX, llama.cpp, vLLM, DeepSeek official release material, DS4, and exact-rig searches for the four canonical target lanes.

**Hard source-freshness boundary for the next external search: 2026-09-10 18:22:16 UTC.**

Evidence classes below distinguish genuinely post-boundary material from refreshed/rebased older work. A repository refresh or rediscovery does not make an older benchmark fresh.

---

# Executive result

There is useful post-cutoff evidence, but **no canonical TG/PP target moves**.

The highest-leverage new result for day-to-day local-agent experience is not a raw decode record: it is a Qwen3.8-27B cache-granularity A/B showing that workload-shaped paged-cache blocks can cut TTFT and whole-agent wall time dramatically while decode changes only slightly. This strengthens the standing view that once TG is interactive, cache reuse, incremental append and TTFT can matter more to subjective UX than another small decode gain.

Other post-cutoff evidence strengthens speculative telemetry truth, packaged-kernel ABI provenance, target-vs-draft fast-prefill eligibility, hybrid attention/recurrent cache transfer semantics, UVA buffer lifetime discipline, and exact-small-M kernel selection. DeepSeek's official V4.1 Flash release also makes the future sparse/offload architecture thesis more concrete, but it does not redefine the current DS4-0731 lane.

---

# FRESH / oMLX #3557 — cache block size must follow request shape, not model geometry alone

PR: `jundot/omlx#3557`

- created/updated: **2026-09-10 14:21:12 UTC**
- head: `ce0a6da4e2d888bcf66e148d678e5fbf86acdc55`
- title: `feat(cache): allow overriding resolved paged cache block size`

Exact test cell:

- Apple M3 Max 64 GB;
- `Qwen3.8-27B-oQ4e-mtp`;
- native MTP depth 3;
- FP16 KV;
- 20 agentic coding tasks = 4 tasks x 5 repetitions;
- both arms on commit `94530d8d`;
- block size is the only intended variable.

The existing `qwen3_5`/ArraysCache heuristic resolves a 4096-token page because of model geometry. The Pi coding-agent system prompt is about 3.6K tokens and early turns are about 3.9-4.1K total, so the stable prefix can sit below one complete page. Because reusable prefixes are whole-block based, the stable system prompt repeatedly misses materialization and the scheduler reports `boundary_snapshot_unavailable`.

Measured **4096 -> 512** block size:

| metric | 4096 | 512 | delta |
|---|---:|---:|---:|
| prefix-cache hit rate | 59.8% | 88.7% | +28.9 pp |
| tokens re-prefilled / attempt | 13,892 | 4,957 | -64.3% |
| TTFT | 18.35 s | 5.92 s | -67.7% |
| decode | 45.65 tok/s | 44.02 tok/s | -3.6% |
| full suite wall | 2512.6 s | 1546.2 s | **-38.5%** |

Per-task medians improve 36-52%.

Important qualification: the author could not directly retrieve `prefill_tokens_per_second`, so this is **not** evidence that 512-token blocks make the prefill kernel itself faster. It is evidence that better prefix materialization/reuse can overwhelm the boundary-snapshot overhead in this workload. The TTFT improvement tracks the reduction in tokens that actually need re-prefill; decode remains nearly flat.

Implementation adds `OMLX_PAGED_CACHE_BLOCK_SIZE` as an opt-in final override after geometry heuristics. Invalid/non-power-of-two values fail soft to the default; defaults are unchanged when unset.

## Promotion

For local coding-agent qualification, block/page size becomes a workload parameter:

- record stable-prefix length distribution and turn-length distribution;
- sweep page sizes against representative agent traffic, not synthetic one-shot prompts only;
- record hit rate, reusable-prefix tokens, tokens re-prefilled, TTFT and end-to-end task wall separately from decode TG;
- do not assume the largest prefill-efficient page is the best serving page;
- small recurring decode or boundary overhead can be an excellent trade if it removes repeated cold work.

For the dual-M1 Flash plan, add a representative page-size A/B such as 256/512/1024/2048/4096 once cache/replay correctness is stable. This is **M3-Max / 27B transfer evidence**, not an M1 numeric target receipt.

---

# FRESH / rMLX #555 — one authoritative speculative round event; report sink truth, not nearby proxies

Commit: `7d5ebefd63895aeadfcde2632e02172f7323edfa`

Timestamp: **2026-09-10 15:27:28 UTC**

Title: `spec(refactor): one per-round event over the union of what seven loops reported (#555)`

Seven speculative loops now close through one `RoundReport`, one `log_round`, and one shared target. The union of real fields is available to every loop; facts a loop does not have are absent rather than emitted as fake zeroes.

The refactor exposed several telemetry errors that are directly relevant to our verifier certification:

1. `refolded` had been inferred from verifier offsets, which can claim a refold for non-recurrent stacks. It now comes from the actual rollback/refold operation and ultimately whether recurrent layers were actually refolded.
2. `n_committed` could describe the candidate list handed to the emitter rather than what reached the visible sink when remaining budget or a stop token clipped a round. `emit_round_tokens` now returns the actual emitted count.
3. `condition_rows` now reflects the one persistent verifier conditioning row (`h_cond`) rather than an incorrect no-conditioning assumption.
4. DFlash 2 previously emitted two events for one physical round, inflating one capture from 3862 real rounds to 4423 event lines; the shared seam removes the duplicate producer.
5. capture comparison now fails closed when a requested field appears nowhere, reports coverage per cell, and pins the reader's target/field schema rather than allowing an empty stream to look like a pass.
6. overrun/error records are shaped so they cannot accidentally be classified as a second normal round event.

## Promotion

- one authoritative per-round event producer;
- a telemetry field that names an action must come from the actual action/sink result, not a nearby arithmetic proxy;
- `committed` means actually emitted/visible/retained after budget/stop clipping;
- missing-field and empty-stream comparisons fail closed;
- coverage is per benchmark cell, not globally inferred from one cell;
- event target, field schema and reader copy are part of provenance.

Mechanism/provenance only; no target movement.

---

# FRESH / oMLX #3558 — packaged custom-kernel ABI is part of compiled/executed identity

Commit: `b6f64a86b0f18d0055c625c1a3f67916d3240447`

Timestamp: **2026-09-10 15:26:24 UTC**

Title: `fix(mac): reject custom kernels with the wrong bundled Python ABI (#3558)`

A Mac app build can compile/test a native extension under a different CPython from the interpreter actually bundled in the donor app. A `cpython-313` extension can therefore pass a build-time import and still be unloadable by a packaged `cpython-311` app.

The build now compares:

- implementation;
- `cache_tag`;
- Python major/minor;
- extension suffix;

before compiling, and then inspects the staged `_ext*.so` files after copy so stale native artifacts are also rejected.

## Promotion

Extend the compiled-capability provenance ladder to include **runtime-loader ABI and staged extension identity**. A source-tree or build-time import does not prove the shipped runtime can execute the custom kernel.

For our Apple custom kernels, record at minimum:

`source/build SHA -> compiled kernel set -> extension ABI/suffix -> staged artifact -> runtime load -> actual dispatched kernel`.

No rate transfer.

---

# FRESH / vLLM #56145 — fast-prefill eligibility is target/draft topology plus per-step arming

Commit: `e6cb56337b49e606f55fde1870adbbb051e23f9f`

Timestamp: **2026-09-10 17:36:04 UTC**

Title: `[Core] MRV2 support for fast-prefill (#56145)`

KV-sharing fast prefill applies to a contiguous suffix of eligible **target** layers. Speculator draft layers can register after the target and can themselves share KV; they must be excluded from the eligibility walk rather than extending or breaking the target suffix.

The new helper also makes fast-prefill a per-step armed state. It declines the fast path when, among other cases:

- there is no prefill;
- the step is a FULL CUDA-graph capture;
- the batch is split into more than one microbatch;
- required logits-index metadata is absent.

Tests explicitly guard against silently running the other model runner.

## Promotion

- `configured fast-prefill` is not `armed fast-prefill`;
- target and draft layer topology are separate execution identities;
- log the per-step arm/fallback reason;
- missing metadata must fall back deliberately rather than pretending the requested fast path executed.

Cross-runtime mechanism only; no Apple numeric transfer.

---

# FRESH / vLLM #55819 — UVA-backed state writes are profitable only with explicit slot lifetime

Commit: `2e0ee66cab1e7a0fd2ccfb0992a0e4b5e940196d`

Timestamp: **2026-09-10 14:27:16 UTC**

Title: `[Perf] Use UVA-backed contents for MRV2 apply_write (#55819)`

For UVA-backed targets, staged write contents can remain in pinned CPU/UVA storage rather than paying an extra asynchronous host-to-device copy. The buffer pool grows in powers of two and round-robins slots.

The correctness contract is the important transfer: a slot cannot be reused/grown until all GPU readers of the prior generation are retired. Tests exercise multiple inflight slots and repeated growth/shrink cycles.

## Promotion

For tiny recurrent/control-state traffic, direct-visible/UVA-style storage is a valid candidate, but benchmark identity must include backing storage, slot/generation identity and reader-lifetime synchronization. Logical payload equality alone does not prove safe reuse.

No Apple rate transfer.

---

# FRESH / vLLM #55531 — hybrid distributed state transfer must be cache-group aware

Commit: `7cdd9304ae2e46572f220741bf86e0b3c2da569c`

Timestamp: **2026-09-10 18:12:15 UTC**

Title: `[KV Connector] Support symmetric DCP disagg for hybrid mamba models (#55531)`

The change lifts a blanket restriction for hybrid attention + recurrent/Mamba state under disaggregated context parallelism, but only with compatible local/remote sharding. Importantly, attention prefix-caching block mapping is applied to attention-type cache groups, not blindly to recurrent-state groups.

## Promotion

- distributed cache/state handshakes must certify peer sharding compatibility;
- cache transfer logic is group-type aware: attention blocks and recurrent state do not inherit the same mapping rules merely because both are called cache;
- auto-derived interleave/sharding belongs in executed provenance, with an explicit override taking precedence.

This directly reinforces the dual-M1 requirement to keep QSA/KV ownership and GDN/recurrent ownership distinct. No TB4 rate transfer.

---

# FRESH / llama.cpp #28457 — small-M routing must key on M as well as N/K

Commit: `6788edb4f325c1cb4210997eb79edcab2e27aeaa`

Timestamp: **2026-09-10 17:20:18 UTC**

Title: `vulkan: small M matrix optimizations for qwen (#28457)`

The Vulkan path changes small-vs-medium tile selection from an N-only heuristic to an M+N decision, permits split-K at small M when occupancy warrants it, and adds a special eligible `m=1` operand-swap route. Boundary tests cover widths around 7/8/9, 127/128, 511/512 and M around 31/32, including quantized Q8_0.

## Promotion for Blazer / Apple kernel mining

The numeric Vulkan win does not transfer, but the shape rule does: Q5/Q6/custom mixed-bit matmul/QMV dispatch must be keyed by actual **M/N/K + quant format + verify width**, not a dense-path N-only default. Keep n=1 decode and small-M MTP verify separate in tuning.

---

# FRESH / OFFICIAL — DeepSeek V4.1 Flash makes the future sparse/offload thesis more concrete

Official DeepSeek release date: **2026-09-10**.

DeepSeek states that V4.1 Flash is:

- a **552B** MoE model;
- a new asymmetric **Causal-Encoder-Decoder** architecture;
- **8B active on input** and **16B active on output**;
- the smallest model in the new architecture family;
- natively multimodal.

DeepSeek also states that, versus the prior generation, the new architecture reduces KV-cache HBM demand to **1/4** and SSD demand to **1/8**, and reports a **437x** KV-cache reduction relative to its first generation.

## Promotion

This is direct official architecture evidence for the direction we have been designing around: total parameter count can rise while active compute and long-context state become much more aggressively bounded/offloadable.

It does **not** prove V4.1 Flash fits, runs well, or is desirable on one/dual M1 Max 64 GB. At 552B total it is a separate future lane until a real quant/offload/runtime artifact establishes placement and active traffic. It does not redefine DS4-0731.

---

# UPDATE / BACKFILL — oMLX #3499 Affine4 KV cache long-context record

PR `jundot/omlx#3499` was refreshed post-cutoff and currently reports a much fuller long-context Affine4 record. However, much of the underlying implementation/benchmark work carries earlier author dates and was later rebased/recommitted; the post-cutoff refresh itself is not sufficient to make every numeric cell fresh. Therefore preserve the useful evidence as **UPDATE/BACKFILL**, not as a new target-rate receipt.

Current reported Apple M5 Pro 48-GB / Qwen3.8-27B Affine4 cells include:

- 150K: 291.9 PP / 12.3 TG, active MLX peak 20.71 GiB;
- 200K: 250.0 PP / 11.8 TG, active MLX peak 21.81 GiB;
- logical attention KV at 200K: 12.21 GiB native -> 3.71 GiB Affine4, or 69.6% less;
- short 8K single-pass decode is similar across native BF16 / TQ4 / Affine4;
- a separate 8K Affine4 MTP control reports 16.9 TG off -> 36.1 TG on, with 84/97 considered drafts accepted;
- a thinking-enabled MTP run generated 28,903 tokens as endurance evidence.

A repeated 35B/200K comparison in the same PR shows materially better long-context decode with Affine4 than the compared TurboQuant4/native paths, but compression is lossy and different formats can follow different continuations. The author explicitly does not claim cross-format quality equivalence.

## Promotion

Treat Affine4 as a **long-context capacity/control candidate**, not a default quality lane. Any adoption into our 27B or future Flash qualification must compare:

- task quality / teacher-forced drift;
- MTP acceptance by depth;
- cache memory;
- PP/TTFT;
- sustained TG;
- task wall;
- output/chunk-size sensitivity;

against native BF16 and other compressed-KV controls.

No canonical target move from this refreshed PR.

---

# SCREENED / no target movement

## oMLX #3553

PR metadata updated after the prior cutoff, but the head remains `a04d2408183c130d24a968ed74732260eb55d0be` and the material benchmark decomposition is the same evidence incorporated by the 09:11 watch. Do not count the metadata refresh as a new measurement.

## Exact target lanes

No new post-cutoff exact receipt was found for:

- 2x M1 Max 64 GB / TB4 / Flash-Next;
- 2x M1 Max 64 GB / TB4 / DS4-0731;
- one M1 Max 64 GB / canonical mature Qwen3.8-27B target cell;
- RTX 5070 Ti 16 GB / fully-resident Q3_K_XL + native-MTP canonical speed cell.

A searchable M1-Max-64 Qwen3.8-27B DFlash artifact reports about 22.0-22.3 TG, but it was already indexed before this cutoff and is not fresh evidence for this pass. RTX community results surfaced by current search likewise trace to older runs already outside this freshness window.

No post-cutoff `antirez/ds4` main change supplied stronger exact target evidence.

---

# Consequences by canonical lane

## Dual-M1 Flash-Next

Keep **PP2 / layer ownership primary; TP2 control**.

Add/strengthen:

1. workload-shaped paged-cache block-size sweep after correctness is stable;
2. stable-prefix length, hit rate, re-prefill tokens, TTFT and task wall as serving metrics;
3. packaged custom-kernel ABI + staged extension identity in compiled/executed provenance;
4. target-vs-draft topology and per-step fast-path arm reason;
5. separate attention-block transfer from recurrent-state transfer;
6. explicit lifetime/generation ownership for direct-visible/UVA-like control buffers;
7. M/N/K/quant/verify-width-aware small-M dispatch;
8. all prior reliable-sync, selected-row PLE overlap, graph-layout, recurrent, concurrency, soak and equal-acceptance speculative gates remain.

The strongest practical implication from this pass: once decode is already interactive, reducing repeated prompt work can move perceived and whole-task performance much more than a small raw TG increase.

## Single M1 Max64 Qwen3.8-27B

No target movement. The new #3557 result is strong workload/cache transfer evidence on M3 Max 64 GB, not an M1 speed receipt.

**P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; older Q2/Q3/Q4 and host-backed long-context results remain separate evidence cells.

## Dual-M1 DS4-0731

No target movement. DeepSeek V4.1 Flash is a future architecture family with materially different active-compute/state design, not an updated DS4-0731 receipt.

## Future Blazer / 5.x-bit work

Add to the durable co-design checklist:

- page/cache granularity evaluated against actual agent traffic;
- M/N/K/quant/verify-width-aware dispatch;
- MTP-head precision independently tunable;
- packaged ABI/runtime-loaded kernel provenance;
- cache-group-aware distributed ownership;
- tolerance/quality/task-wall certification alongside raw rate.

---

# Standing decisions strengthened

- Cache reuse granularity is a serving/workload parameter, not only a model-geometry parameter.
- TTFT and task wall are first-class once TG is interactive.
- Telemetry must report actual side effects at the sink, not infer them from control-flow proxies.
- Missing telemetry is absent, not zero; an empty comparison cannot pass.
- Packaged loader ABI belongs in compiled/executed custom-kernel identity.
- Fast-path configuration and per-step arming are separate provenance states.
- Attention/KV blocks and recurrent state require type-specific distributed transfer semantics.
- Direct-visible/UVA control traffic needs explicit buffer-generation lifetime guarantees.
- Small-M kernel selection must use actual M as well as N/K and quant geometry.
- DeepSeek V4.1 strengthens the sparse/offload direction but does not establish M1 fit.
- Refreshed/rebased PR metadata does not make older benchmark evidence fresh.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**
