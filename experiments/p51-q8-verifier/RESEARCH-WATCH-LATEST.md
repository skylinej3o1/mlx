# Latest external runtime watch

## Active scope

Research remains centered on:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**
- **Qwen3.8-27B — one M1 Max 64 GB**
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**
- **Blazer / custom ~5.x-BPW execution work** where evidence transfers cleanly

Do not maintain a dedicated future M5/M5-Ultra lane unless explicitly reopened. Stronger-Apple evidence remains transfer/mechanism evidence unless it reproduces an active topology.

---

## Read order for the next research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-2115-ADDENDUM.md` — targeted mlx-serve Flash-Next backfill: direct Apple QSA gather/select/history receipts, adaptive MTP and coarse-head rerank, M5 1M community receipt, fresh missed-window grouped-MTP commit, and distributed-MTP PP2 implementation hypothesis. **Does not advance freshness boundary.**
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-2057.md` — newest complete delta: generated-prefix MTP history, SDPA transient capacity, distributed-MTP constraint, coherent multi-slot prompt cache, expert-major offload prefill, live-length gather geometry, sampler-support-aligned drafting, dummy-draft KV poisoning, M1 long-context correctness, QSA top-k/request lifecycle, recovered #3614/#28213/#28699.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1533.md` — TB routable-address discovery, executed PP ownership, live memory admission, lazy-send/collective ordering, internal prefill checkpoints, DCP interleave mapping, EPLB warmup isolation.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1237.md` — live-context-bounded sparse work, DFlash2 per-layer causality, DSpark candidate-pruned proposal head, MTP retained-history offload coverage, parallel JIT warmup, multimodal pre-prefill TTFT.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-0343.md` — dual-Mac failed-runtime recovery, exact rendered-context budgeting, SM120 physical-stride correctness, compiled speculative drafter evidence, producer-side norm/quant fusion.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-2300.md` — fused RMS/GDN verifier recurrence, expert-offload I/O/speculation economics, direct TB/RDMA cluster failure modes, shared physical host-cache ownership, speculative JIT warmup cardinality, draft-architecture provenance.
9. Older 2026-09-12 / 2026-09-11 / 2026-09-10 / 2026-09-09 notes remain retained for QSA/MTP, offload, PP/TP, recurrent rollback, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest **complete** pass covers substantive sources strictly after `2026-09-13 19:33:05 UTC` through `2026-09-14 00:57:57 UTC`.

The 21:15 ET file is a targeted addendum/backfill. It includes one missed source that was actually inside the prior complete window and several older mlx-serve sources surfaced later. It is not a complete post-boundary scan.

**Hard source-freshness boundary for the next complete external search remains `2026-09-14 00:57:57 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase, comment-only activity or merge-only churn. Resurfaced older evidence stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C from external evidence.**

Recent mlx-serve evidence changes the **confidence calibration**, not the target: 40 tok/s @ ~128K should now be treated as a credible success floor for a fully tuned implementation rather than an assumed ceiling. 50+ is an increasingly plausible stretch, but must not become canonical without exact dual-M1 measurement.

---

# Newest addendum — mlx-serve Flash-Next

## Fresh missed-window: mlx-serve #412 / `6d3cb6d...`

Source time `2026-09-13T22:11:47Z`, inside the prior complete-search window but missed because mlx-serve was not yet part of the regular sweep.

Flash-Next now shares draft + one row-axis verify forward across concurrent requests while preserving independent KV, recurrent state and rollback offsets. Reported 4-stream gains over legacy per-request MTP: **+30.1% @4K, +26.8% @16K, +18.9% @64K**; two streams about +27%. Single-stream byte parity retained.

**Transfer:** independent speculative state can coexist with shared verify compute. This strengthens our PP2 design hypothesis that stage-local state should remain local while the authoritative proposal/accept path is minimized.

## Direct Apple QSA decode gather — `96578478...`

QSA selected ~2K rows but old decode still built a full-context mask and ran full-KV SDPA. Gathering only selected K/V rows produced locked-serial KV8 results:

- 32K **40.8 -> 51.3 tok/s**
- 64K **32.9 -> 48.7**
- 128K **23.5 -> 46.1**
- 256K **14.6 -> 40.9**

This is direct Apple confirmation that **selection must remain sparse through the actual K/V read and attention execution**.

## Direct Apple QSA prefill gather — `7d012036...`

Block-index gather instead of dense full-cache masked QSA prefill reported:

- 32K **589 -> 699 tok/s**
- 128K **395 -> 654**
- 256K **267 -> 551**

Also separates n-gram/PLE boot warm state from steady-state prefill.

## QSA select + fused score sheet — `680e5a56...`

M5 Max long-context cells after exact top-k threadgroup splitting + fused score path:

- 162K: serial **50.3 -> 52.8**, MTP **54.8 -> 60.3**, prefill **1393 -> 1413**.
- 361K: serial **47.7 -> 49.6**, MTP **57.7 -> 59.0**.
- 805K: serial **39.5 -> 46.6**, MTP **53.5 -> 57.8**, prefill **930 -> 960**.

Promote exact top-k, score fusion and live shape/threadgroup policy as real Apple Flash hotspots.

## QSA history / recurrent checkpoint ownership — `e0a42640...` + `290b84c3...`

mlx-serve reduces full raw QSA history to a short raw-key ring plus pooled authoritative history and stops cloning growing QSA history into every SSM checkpoint.

Reported consequences include:

- ~**3.2 GB** raw-key saving at 1M;
- 256K history file **960 MB -> 192 MB**;
- warm ladder to 1M: **37.7 tok/s**, peak MLX active **108.8 GB**;
- separate M5 validation: 1M prefill **509 tok/s**, **49 tok/s @128K** after cool-down.

**Promote:** shared append-only QSA history and checkpoint-local recurrent leftovers are separate ownership classes. Never snapshot the whole long-history tensor into every recurrent checkpoint.

## MTP economics / proposal head — `862bddff...` + `58fcfbdf...`

mlx-serve combines adaptive speculation based on measured serial/spec prices with a coarse quantized proposal head + exact shortlist rescoring, deferred PLE gather, and projecting only the MTP rows actually consumed.

This is independent confirmation of several current project principles:

- proposal precision/work can differ from target verifier precision;
- full-vocab draft projection can dominate a draft step and should be avoided;
- PLE/lazy-graph waits should be overlapped/deferred;
- MTP should switch off when long-context verifier economics become negative and switch back on when profitable.

## GDN state ownership — `fa76a4b5...`

A 3-row GDN conv tail was a view into the whole 4096-token prefill chunk, pinning ~3 GB. Owning just the required tail cut peak ~2.5 GB with unchanged prefill speed and materially reduced the admission bill.

**Promote:** recurrent tails must own only the minimal retained rows; views into large prefill tensors are part of memory provenance.

---

# mlx-serve release/community calibration

## v26.9.2 release (source 2026-09-09; timestamp retained)

Reported Qwen3.8-Flash-Next changes include cheaper speculative rounds, shortlist drafting instead of full-vocab work, faster long prompts, adaptive MTP, SSD prefix cache and per-request long-prompt width. The M4 Max benchmark table records Flash-Next MTP **83 -> 93 tok/s** from 26.9.1 to 26.9.2; release notes describe roughly +30% at 64K/128K from the broader optimization bundle.

## Reddit 1M community receipt (source 2026-09-09/10; timestamp retained)

Co-creator report on M5 Max 128GB, mixed dense8/expert4, KV8, MTP, 1 concurrency:

- ~117 GB peak at 1M;
- prefill ~1700-1800 tok/s initially and near ~1000 toward 1M;
- generation 100+ <=16K, 80+ <=256K, ~60 @500K, ~40 @1M;
- coding ~75 tok/s at 1M in the original post.

A follow-up states current main subsequently raised the 1M tail **~40 -> ~67 tok/s (+67%)**, but the exact commit responsible for the entire delta has not been isolated. Treat that number as a community/current-main receipt, not a controlled implementation A/B.

**Consequence:** this strongly raises confidence in Apple Flash long-context headroom, but single-M5 avoids our TB4/PP2 synchronization cost. Keep the dual-M1 canonical target unchanged.

---

# Distributed Lightning-MTP: current planning interpretation

The oMLX #3653 blocker is real: stock distributed MTP remains rejected. Current evidence nevertheless supports treating it as an **engineering/certification blocker, not a known architectural impossibility**.

Working PP2 hypothesis:

1. keep backbone / QSA / GDN / PLE state stage-local;
2. one authoritative sampling/verification-control rank;
3. one normal PP traversal for the whole verifier row block, **not one traversal per drafted token**;
4. authoritative rank determines accepted-prefix length / sampled continuation;
5. tiny commit/control synchronization back to the other stage;
6. both stages commit/rollback KV + recurrent + QSA/indexer + PLE + MTP history to the same boundary;
7. prefix-cache sidecars persist that same boundary identity;
8. cancellation/errors synchronize the same commit decision before releasing state.

Prove distributed MTP correctness relatively early; its transport/state topology determines which P69/QSA paths are actually hot.

Do not store conversational confidence percentages as measured evidence.

---

# Current Flash-Next optimization stack

Treat these as largely orthogonal and potentially stackable:

1. **QSA/indexer:** compact selected-K/V decode + prefill, live-span launch geometry, exact/deterministic top-k, fused score path, short raw-key ring + pooled history, owner-local state.
2. **MTP/P69 economics:** distributed-MTP correctness, one verifier traversal/round, coarse proposal head + exact rerank, consumed-row-only projection, GDN verifier fusion/prework, PLE defer, adaptive depth/speculation.
3. **PP2/MoE/runtime:** actual layer ownership/balance, TB4 transport/collective order, transient-aware admission, minimal recurrent-tail ownership, allocator lifecycle, prefix-cache/SSD correctness and recovery.

---

# Prior complete-watch critical evidence still active

- oMLX #3647: generated-prefix MTP history must travel with backbone cache state.
- oMLX #3651: 2x64 GB context capacity must include route-specific SDPA transient.
- oMLX #3653: ordinary PP compatibility does not imply distributed MTP is enabled.
- oMLX #3655: distributed prompt cache can use coherent count-based LRU while byte eviction stays disabled.
- vLLM #56720: launch geometry should scale with live compressed-KV gather length.
- vLLM #56724: probabilistic draft support must align with target top-k/top-p support.
- vLLM #56734: dummy speculative steps must be write-side-effect-free on persistent drafter state.
- llama.cpp #28805: ~128K Flash correctness must be tested semantically/repeatedly, not inferred from successful generation.
- recovered oMLX #3614: dual-64GB Q4-class capacity plausibility does not remove the distributed-MTP blocker.
- recovered llama.cpp #28213/#28699: compact QSA gather + incremental/owner-local indexer state remain high-value transfer evidence.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Highest-priority gates now include:

1. distributed-Lightning-MTP correctness/topology proof;
2. compact QSA selected-K/V execution on decode **and** prefill;
3. exact top-k / score-sheet / launch-shape census;
4. minimal authoritative QSA history + recurrent checkpoint ownership;
5. prefix-cache bundle identity across backbone/QSA/GDN/PLE/MTP state;
6. route-specific prefill transient capacity;
7. repeated 64K/~96K/~128K semantic correctness;
8. TB4 transport, actual stage ownership, live admission ceiling, lazy collective ordering and failure/reload certification.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement and no external reorder. **P69B12 frozen/promoted; P69B13 next.** mlx-serve independently supports proposal-head rerank / consumed-row-only projection / verifier-economics principles, but does not alter P69 sequencing.

## RTX5070Ti16

No target movement. Existing SM120 physical-stride/executed-route gates remain.

## DS4-0731 dual M1

No target movement. Apple long-context state/cache ownership lessons transfer; later-V4.1/ROCm throughput percentages do not.

---

# Standing rules added/reinforced

- Fits in aggregate RAM != runnable target stack; feature mutexes/distributed capability gates are feasibility dimensions.
- Distributed MTP is a distinct execution topology and must be certified separately from ordinary PP.
- QSA selection is not an optimization unless downstream K/V read + attention remain sparse.
- Shared append-only indexer history and checkpoint-local recurrent leftovers need separate ownership.
- Recurrent tails must not retain whole prefill chunks through views.
- Prefix-cache correctness is multi-state committed-boundary correctness, not backbone-KV correctness alone.
- Dummy/warmup/padding speculative work must be write-side-effect-free.
- Proposal precision/work and target verifier precision/work are independent optimization dimensions.
- Adaptive speculation should compare realized accepted tokens against measured verifier-cycle cost.
- Semantic long-context correctness needs repeated probes near the operating boundary.
- Merge/crawl time does not refresh older evidence.
- Requested/configured/planned remains distinct from built/available/contracted/admitted/executed.
- Component/kernel gains do not move canonical targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
