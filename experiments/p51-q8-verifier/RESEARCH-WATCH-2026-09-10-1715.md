# External runtime research watch — 2026-09-10 17:15 ET

## Scope and freshness

This delta continues from the prior hard source-freshness boundary:

**2026-09-10 18:22:16 UTC**

Search covered oMLX, rMLX, llama.cpp, vLLM, antirez/ds4, and exact-rig searches for the four canonical target lanes.

**Hard source-freshness boundary for the next external search: 2026-09-10 21:24:31 UTC.**

Evidence timestamps, not rediscovery time or a repository/PR `updated_at` alone, determine freshness. Rebased, force-pushed or newly summarized older benchmarks remain UPDATE/BACKFILL unless their run provenance establishes a post-boundary measurement.

---

# Executive result

There is material post-cutoff mechanism and serving evidence, but **no canonical TG/PP target movement**.

The strongest new items are:

1. rMLX #556 defines and mutation-checks the interface/oracle for collapsing seven speculative round loops before engine code is migrated;
2. oMLX #3468 was force-pushed into a much narrower SSD expert-streaming implementation with one streamability predicate, conversion before giant MoE materialization, fail-clean semantics and focused regressions;
3. oMLX #3063 now preserves the operator-requested distributed prompt-cache slot count across plan-time and measured-headroom retuning, so a conservative first pass cannot permanently pin later cache capacity.

The oMLX #3468 benchmark body remains **UPDATE/BACKFILL / capacity-lane evidence**, not fresh target evidence: the PR's post-cutoff implementation history is clear, but a post-cutoff timestamp for the benchmark executions was not established.

No new post-cutoff exact 2x M1 Max64/TB4 Flash-Next or DS4-0731 rate receipt was found, nor a new canonical one-M1-Max64 27B or fully-resident RTX5070Ti16 speed receipt.

---

# FRESH / rMLX #556 — define the shared round skeleton and mutation oracle before migrating code

Commit: `64a5dc1e228f6e33f347c41bfa0d75a87fc9e8d5`

Timestamp: **2026-09-10 19:40:19 UTC**

Title: `spec(design): the round skeleton's interface, its oracle and its mutation list (#556)`

This is explicitly **proposal/docs/tests, not migrated engine code**.

`docs/SPEC_ROUND_SKELETON.md` defines a drafter interface around prefill, block selection, propose, verify, rollback and condition, plus the migration order, observables and a mutation table. The point is to collapse seven highly duplicated round loops without erasing the places where their semantics genuinely differ.

Important pinned distinctions include:

- which early exit reports/skips verifier resident-KV telemetry;
- where an empty proposal chain is refused;
- whether the round's charge decision is decided locally or forwarded from its entry/configuration;
- which basis defines verifier rollback/offset reporting;
- emission outcome and stop ownership;
- conditioning-buffer/projection meaning;
- what `prefill_ns` includes for each drafter family;
- requested/default block versus the block the round actually ran.

The design uses source-reading and mutation checks for facts that ordinary output equivalence cannot see. Examples include moving the resident-KV report across an exit, disabling the empty-chain guard, hoisting/lowering the round report, rebinding a charge token, or satisfying a scanner only through a comment/phantom needle.

The recorded duplication baseline is **2032 matched lines summed across 21 loop pairs over 2326 total loop-body lines**. Each migration chunk is required to report the debt again, and duplication only counts as removed when a body is actually deleted.

## Promotion

For our speculative engine work:

- define owner/edge/exemption semantics before shared-control-flow refactors;
- mutation-check every source/provenance gate against the defect it claims to catch;
- shared skeletons may unify mechanics but must not erase drafter-specific exit, charge, conditioning or block semantics;
- keep **design/proposed → implemented → compiled → armed → executed** distinct;
- the block/rate/telemetry a benchmark reports must be what the round actually executed, not what the caller requested or inferred.

Mechanism/provenance only. No target movement.

---

# FRESH / oMLX #3468 — narrowed SSD expert-streaming implementation is now a focused capacity/offload lane

PR: `jundot/omlx#3468`

Current title: `feat: MoE expert streaming from SSD (dense resident, experts demand-loaded)`

Current head: `626feab03d3885b728c2c990e3f4252ed5d48784`

The PR was force-pushed/narrowed after the cutoff. Its current post-cutoff history is:

- `dc93f89f90aa5f0415fb01eed14ee5f9d382ee95` — **20:08:20 UTC** — narrow to the streaming patch, DeepSeek-V4 spill, MTP spill-miss path, engine fail-clean, scheduler LRU guard, settings/loading/monitoring and focused regressions;
- `db1ee5f0725f81a4a7512102afe10fc09413ad47` — **20:08:34 UTC** — include the Metal synchronization helper required by the scheduler guard;
- `b6b16b7a1892e50b6ca03b6dcf17d1767104ce21` — **20:08:54 UTC** — drop the 7.6K-line experiment suite from the minimal PR, retaining 83 focused tests;
- `626feab03d3885b728c2c990e3f4252ed5d48784` — **21:07:08 UTC** — audit cleanup/dead-code removal; 83 focused tests pass.

The narrowed implementation keeps several useful architectural rules:

### One authoritative streamability predicate

The loader and forcing/conversion path use the same structural `expert_streaming_estimate` decision. This closes a dangerous split-brain case where one layer of the runtime could decide streaming was required while another declined lazy loading and materialized the full multi-hundred-GB expert banks.

### Convert before materialization

When streaming is supported, the checkpoint is loaded lazily and the expert banks are replaced by the streaming representation **before** `materialize_lazy_state`. Only after the MoE banks have been removed does normal materialization proceed for dense weights/state.

For giant MoE artifacts this ordering is a correctness/capacity invariant, not merely an optimization.

### Fail clean if requested streaming cannot be established

If conversion/backing creation fails, model load fails rather than continuing with all expert banks resident and risking OOM/SIGKILL.

### Projection ownership is explicit

The normal gate+up fusion is skipped while expert streaming is active because the streaming path owns that projection layout. Independent optimizations must not silently stack when they both assume ownership of the same tensors/layout.

### Route/cache health becomes execution provenance

The streaming path records request-level LRU hit/miss/eviction/capacity and context-fallback information and persists the learned expert-pin profile before teardown.

## UPDATE / BACKFILL — benchmark body, not fresh execution evidence

The current PR description reports a common **M4 Pro 48 GB / 4-GiB expert budget / 2K prompt / 96 decode tokens / single request / MTP off** comparison:

| model | prefill | decode | process peak |
|---|---:|---:|---:|
| Qwen3.8-Flash-Next-JANG_4M | 56.6 tok/s | 2.42 tok/s | 10.64 GiB |
| DeepSeek-V4-Flash-0731-JANG | 20.6 tok/s | 2.53 tok/s | 12.78 GiB |
| GLM-5.3-Flash-JANG-MTP | 35.0 tok/s | 1.75 tok/s | 14.77 GiB |

DeepSeek TTFT is reported as 107.5 s cold-page-cache versus 89.6 s warm.

These cells are useful as **capacity/offload transfer evidence**, but this pass did not establish that the benchmark runs themselves occurred after the hard cutoff. The minimal PR also deliberately excludes benchmark/result artifacts from its current code diff. Therefore do not label these numbers FRESH and do not move any canonical target from them.

The performance shape also reinforces the existing architectural distinction: streaming routed expert banks can buy fit at a severe per-token cost, whereas Flash-Next's PLE/n-gram table remains a structurally better SSD-offload target because it uses small indexed reads rather than repeatedly feeding active expert weights.

## Promotion

- one authoritative streamability/placement predicate;
- lazy load + offload conversion must occur before any eager whole-model materialization;
- requested offload fails closed if backing creation fails;
- runtime provenance includes resident/streamed route, cache hit/miss/eviction and fallback state;
- tensor-layout owners must declare incompatible fusions/transforms;
- classify expert streaming as a **capacity/offload lane** until exact target-topology evidence says otherwise;
- do not numerically transfer the M4-Pro benchmark body to the M1 cluster.

---

# UPDATE / oMLX #3063 — preserve requested prompt-cache capacity across repeated distributed retuning

PR: `jundot/omlx#3063`

Title: `fix(cluster): tier distributed prompt-cache slots by headroom`

Head: `3d57f07be6e804033433425cdfb061649a97688f`

Post-cutoff review/update timestamp: **2026-09-10 20:42:07 UTC**.

The key revision is that `ExecutionSettings` now stores `requested_prompt_cache_size` separately from the currently resolved/clamped `prompt_cache_size`.

This matters because cluster activation can tune more than once:

1. an initial planning pass can see tight estimated headroom and clamp an intended four-slot cache to one;
2. a later measured placement can show ample real headroom;
3. if the second pass clamps from the already-clamped value, it can never restore two/four slots;
4. the revised path clamps each pass from the preserved operator/profile request instead.

The explicit regression covers **planned 3 GiB headroom → 1 slot**, then **measured 20 GiB → 4 slots**, then a headroom collapse back to **1 slot**.

The distributed coherence rule remains important:

- count-based LRU can stay in lockstep when ranks observe the same insert/fetch event stream;
- rank-local **byte-budget eviction remains disabled**, because unequal PP stages can cross byte thresholds on different requests and retain different prefixes, causing token-offset divergence before collectives;
- slot count bounds the number of retained prefixes, not their actual byte footprint; memory pressure is still governed elsewhere.

The update reports **351 cluster tests passed**.

## Promotion

For cluster serving provenance, add a capacity-resolution ladder:

**requested → planned → measured-headroom-retuned → effective**.

Repeated admission/retune logic must resolve from durable requested intent, not the previous pass's already-clamped output. Cache capacity and cache-coherence policy are separate facts; byte-based eviction must not become rank-local on a synchronized PP cache.

This is particularly relevant to warm-prefix/multi-agent UX, but it is not a throughput target receipt.

---

# SCREENED / no target movement

- **oMLX main:** no new post-cutoff main commit with stronger target-lane evidence; fresh oMLX material this pass is in the PR updates above.
- **oMLX #3536:** post-cutoff review/metadata activity exists, but the substantive MTP tensorized-acceptance implementation/benchmarks predate or lack post-cutoff execution provenance. Preserve as UPDATE/KNOWN, not fresh rate evidence.
- **rMLX:** #556 is the only new post-cutoff main item found; #555 at 15:27 UTC was already incorporated by the 14:14 watch.
- **vLLM:** the closest relevant MTP/KV changes found in the focused scan were before 18:22:16 UTC. Later visible changes did not provide stronger exact hybrid/Apple target evidence.
- **llama.cpp:** the Qwen Vulkan small-M work from the prior watch is pre-cutoff here; later generic backend activity did not provide a new exact Qwen target receipt.
- **antirez/ds4:** no post-cutoff exact 2x-M1-Max64/TB4 DS4-0731 rate receipt or stronger mainline target evidence found.
- **exact-rig Flash search:** no new timestamped post-cutoff 2x M1 Max64/TB4 Flash-Next sustained TG/PP receipt found.
- **exact-rig M1 27B search:** surfaced older/undated community receipts only; crawled-today/rediscovered is not fresh evidence.
- **exact-rig RTX5070Ti16 search:** surfaced older fully-resident/MTP results already represented in the evidence chain; no new canonical speed cell.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. before collapsing speculative drivers, pin drafter-specific exit/charge/conditioning/block semantics and mutation-test the source gates;
2. keep PLE/n-gram SSD offload primary; treat routed-expert streaming as a separate capacity control unless exact evidence changes the economics;
3. require one authoritative streamability/placement predicate and fail closed if the chosen offload path cannot be established;
4. offload conversion must precede giant-bank materialization;
5. record resident/streamed route + cache hit/miss/eviction/fallback state in executed provenance;
6. declare projection-layout ownership so streaming/fusion/custom quant transforms cannot silently conflict;
7. preserve `requested → planned → measured → effective` cache-slot state across repeated cluster tuning;
8. keep rank-synchronized prompt-cache eviction count-based rather than rank-local byte-threshold based;
9. retain all prior reliable-sync, selected-row PLE overlap, cache-page-size, graph-layout, recurrent ownership, concurrency, soak and equal-acceptance speculative gates.

Safe serving remains **profitable singleton MTP + plain concurrent work** until concurrency/state-isolation gates are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. The new material is design/offload/cluster-serving transfer evidence, not a new M1 numeric receipt.

**P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; expert/host/offload configurations stay separate capacity cells.

## Dual-M1 DS4-0731

No target movement. #3468 makes an SSD expert-streaming capacity path more concrete, but its M4-Pro 2.53 tok/s body is not a dual-M1 receipt and should not redefine the existing DS4 lane.

## Future Blazer / 5.x-bit

Add component-level residency/offload ownership to execution provenance. A custom quant/fusion/streaming path must declare which tensor layout it owns and which transforms are mutually exclusive. Preserve actual executed block/route/cache-state identity alongside quant/group/kernel identity.

---

# Standing decisions strengthened

- Shared speculative control flow needs a mutation-checked semantic interface before code deduplication.
- Design/proposal evidence is not executed-engine evidence.
- The reported round/block/telemetry must come from what actually executed.
- Offload support should have one authoritative capability/placement predicate.
- Giant expert banks must be converted to the streaming representation before eager materialization.
- Requested offload must fail closed if its backing cannot be established.
- Routed-expert SSD streaming is a capacity lane unless exact target evidence proves favorable performance economics.
- PLE/n-gram offload remains structurally preferable for Flash-Next when feasible.
- Cache tuning provenance is **requested → planned → measured → effective**.
- Repeated retuning must clamp from requested intent, not a previous clamp.
- Distributed prompt-cache coherence cannot depend on unequal rank-local byte thresholds.
- Refreshed/rebased/force-pushed metadata does not make older benchmark executions fresh.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
