# External runtime research watch — 2026-09-10 19:28 ET

## Scope and freshness

This delta continues from the prior hard source-freshness boundary:

**2026-09-10 21:24:31 UTC**

Search covered oMLX, rMLX, llama.cpp, vLLM, antirez/ds4, and exact-rig web/GitHub searches for the four canonical target lanes.

**Hard source-freshness boundary for the next external search: 2026-09-10 23:28:08 UTC.**

Evidence timestamps, not rediscovery time, crawl time, PR `updated_at`, or a rebased committer timestamp alone, determine freshness.

---

# Executive result

This is a **material architecture / qualification pass with no canonical TG/PP target movement**.

The strongest new item for the dual-M1 Flash project is oMLX #3566: a fresh, model-family-specific distributed tensor-parallel strategy for `qwen4_exp` / `qwen4_exp_text`, the architecture lineage oMLX uses for Flash-Next. It concretely shards GDN, recurrent, attention and MoE structures across ranks and therefore gives us a real TP2 control implementation to compare against PP2. It is still strategy/unit-test evidence rather than a real two-Mac throughput receipt.

rMLX #557 strengthens the speculative-refactor gate model by moving charge/sampling provenance onto the semantic populations that will survive the shared-loop migration and by closing scanner fail-open holes. vLLM #56098 independently reinforces that scratch/workspace state is stream-owned execution state under concurrency and graph capture.

No new exact dual-M1/TB4 Flash or DS4 rate receipt appeared. No new canonical single-M1-Max64 27B or fully-resident RTX5070Ti16 speed receipt appeared. Targets remain unchanged.

---

# FRESH / oMLX #3566 — `qwen4_exp` distributed TP strategy becomes a concrete TP2 control lane

PR: `jundot/omlx#3566`

Created: **2026-09-10 22:08:36 UTC**

Head commit: `5dcadc1b177df5b87830620cbce5e2e11ed4fb53`

Commit timestamp: **2026-09-10 22:08:26 UTC**

Title: `feat(cluster): add Qwen4 / qwen4_exp distributed tensor-parallel strategy`

The implementation adds a dedicated `QWEN4_EXP` tensor strategy for the hybrid linear/full-attention architecture rather than incorrectly reusing `qwen3_next` assumptions.

The fresh strategy explicitly shards:

- GatedDeltaNet `in_proj_qkv` by contiguous Q/K/V channel ranges;
- `in_proj_z`, `in_proj_b`, `in_proj_a` as column-parallel projections;
- depthwise `conv1d` weights/biases, including rank-local `groups` adjustment;
- recurrent decay/timestep vectors `A_log` and `dt_bias` across value-head ownership;
- GDN `out_proj` as row-parallel with cross-rank reduction;
- full-attention `q_proj`, `k_proj`, `v_proj`, `o_proj`;
- MoE `switch_mlp` and `shared_expert` paths;
- planner divisibility constraints for linear-attention key/value dimensions;
- nested `text_config` architecture resolution.

Reported validation is **tests, not a physical cluster receipt**:

- 47 focused planner/tensor-strategy/tensor-parallel tests pass;
- 1279 `cluster or tensor` tests pass, 13 skipped.

## Promotion

For the Flash-Next program:

- TP2 is no longer merely a conceptual control; use #3566 as a concrete reference strategy to compare with PP2;
- keep **strategy/configured → materialized shards → collective topology → armed → executed** distinct;
- record rank ownership for GDN Q/K/V/Z/B/A, conv groups, recurrent `A_log`/`dt_bias`, full-attention heads and MoE experts;
- verify divisibility and local tensor shapes on the exact checkpoint, not only architecture-name matching;
- cross-rank reductions on `out_proj`/attention/MoE are the traffic we must measure directly against PP2's stage-boundary traffic;
- PP2 remains primary because #3566 supplies no physical two-Mac rate, no TB4 bytes/token receipt, and no evidence that TP2 beats PP2 for Flash-Next.

This **reinforces the value of keeping TP2 as a control lane** while leaving the PP2 target untouched.

---

# FRESH / rMLX #557 — provenance gates must follow semantic populations through refactors

Commit: `8fc0f043e479eb3215cc6333552f223cf9c62c7e`

Timestamp: **2026-09-10 22:54:32 UTC**

Title: `spec(gate): re-key the charge and sampling gates onto the populations the round skeleton needs (#557)`

This follows #556's shared-round-skeleton design and rewrites the gates so they remain meaningful before, during and after migration.

Key changes:

- charge provenance is tracked across three semantic populations: classic/forwarded round loops, entries that construct `RoundCfg`, and drafter rollbacks;
- the forwarded charge configuration is immutable in the shared loop (`&RoundCfg`), making whole-value mutation/reforwarding structurally impossible rather than trying to enumerate every mutation spelling;
- sampling provenance follows the same evolving population plus the two-model dispatch guard;
- entries must carry the request sampler into the configuration they hand to the shared loop;
- stochastic and normal verifier-draw constructions are checked distinctly;
- scanners strip comments and string bodies so commented-out or printed needles cannot satisfy a code invariant;
- ambiguous multiple `RoundCfg` parameters fail closed instead of silently choosing one;
- function-body extent and wrapped-call parsing were hardened against comment/formatting bypasses;
- portability was checked across BSD awk, gawk and mawk;
- fixture populations were expanded substantially and include mid-migration/end-state trees.

## Promotion

For our own source/provenance gates:

- define the **semantic population that owns a fact**, not a temporary syntax pattern that disappears during refactoring;
- gate both sides of a forwarded value: where it is decided and where it is consumed;
- prefer structural immutability/ownership constraints over regex attempts to enumerate every mutation form;
- scanners must read code rather than comments/strings and must fail closed on ambiguous ownership;
- every gate needs mutation fixtures across the current tree, intermediate migration tree and intended end state;
- a clean gate after refactor is evidence only if its population stayed anchored to the semantic owner.

Mechanism/provenance only. No target movement.

---

# FRESH / TRANSFER — vLLM #56098: concurrent streams need owned split-K workspace state

Commit: `9163190dda009a310d8c175d63860ac7c671ca90`

Timestamp: **2026-09-10 22:14:22 UTC**

Title: `[ROCm][Bugfix][Perf] Tune multi-stream shared experts use; wvSplitKrc fixes (#56098)`

The ROCm skinny/split-K path had static scratch tensors that were safe for one stream but could be aliased by concurrent streams. The fix makes workspace ownership explicit:

- pre-allocated per-device workspace pool;
- eight normal stream slots plus eight graph-capture-reserved slots;
- a stream reuses its own assigned slot;
- if normal slots are exhausted, fall back to a safe per-call zeroed workspace at added cost;
- graph-capture streams must use pre-warmed reserved storage rather than allocate/enqueue initialization inside capture;
- the implementation checks workspace capacity against actual M/N/K/split-K shard count;
- split-K depth selection is shape-dependent because extra K shards increase readback cost, and over-aggressive splitting can cost more than conservative splitting.

This is ROCm, not Apple, so **no numerical transfer**.

## Promotion

For PP2/MTP/concurrency certification:

- scratch/workspace memory is execution state and needs stream/request/generation ownership;
- graph capture needs separately certified pre-warmed storage identity;
- static process-global scratch is not concurrency-safe merely because values are temporary;
- resource exhaustion must have an explicit safe fallback whose performance cost is visible;
- verify-width/small-M/split-K decisions must include workspace pressure and concurrency state, not just arithmetic FLOPs.

This independently reinforces the existing rule that B2/B3/B4 certification must prove physical simultaneous execution with isolated per-slot state.

---

# UPDATE / BACKFILL — oMLX #3040: heartbeat health does not prove pipeline progress

PR: `jundot/omlx#3040`

Current head: `5956b0d8beda5dfb87942aabd2137f03630a8503`

The branch was refreshed/recommitted at **2026-09-10 23:08:53 UTC**, but the commit's author date is **2026-08-22**. Therefore the underlying observation is preserved as **UPDATE/BACKFILL**, not FRESH execution evidence.

The commit describes a two-Mac TP2 deployment in which **two concurrent streams froze mid-prefill** inside a collective/Metal fence while heartbeat threads, processes and SSH all remained healthy. A watchdog instead keys on the inference progress counter: if `batch_steps` stops advancing while requests are actually in flight, it records `progress_stalled` and exits the rank so the supervisor can recover it. A frozen counter while idle is explicitly healthy and must not trigger.

## Promotion

- liveness/heartbeat/readiness and **forward progress** are separate cluster facts;
- multi-rank certification needs an in-flight progress watchdog or equivalent monotonic progress evidence;
- idle quiescence must not be mistaken for a stall;
- a supervisor restart path is operational recovery, not proof that the underlying collective bug is solved;
- retain the physical two-concurrent-stream cell in stress testing, but do not label this rebased August observation as fresh September throughput evidence.

---

# SCREENED / no target movement

- oMLX main still has no post-cutoff mainline commit supplying a stronger exact target rate; #3566 is an open PR with strategy/test evidence.
- oMLX #3468/#3063 were incorporated by the immediately previous 17:15 watch; no new target-grade rate receipt appeared after 21:24:31 UTC.
- rMLX #557 is the fresh post-cutoff item; it advances gate correctness, not engine performance.
- vLLM #56098 is useful concurrency/workspace transfer evidence; later visible CI/frontend changes are not relevant target evidence.
- llama.cpp post-cutoff visible activity supplied no new exact Apple/RTX target receipt.
- antirez/ds4 supplied no new post-cutoff exact 2x-M1-Max64/TB4 DS4-0731 rate receipt.
- exact-rig web searches for dual-M1 Flash, one-M1 27B, RTX5070Ti16 27B and dual-M1 DS4 surfaced older August or undated/crawled-today receipts only. Crawl time is not evidence time.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as a now-concrete control**.

Add/strengthen:

1. reproduce #3566's qwen4_exp shard ownership as the TP2 control topology;
2. measure per-token/per-step collective bytes and waits for GDN out-proj, full attention and MoE reductions versus PP2 stage-boundary traffic;
3. verify recurrent `A_log`/`dt_bias`, depthwise conv groups and Q/K/V head slicing on the exact Flash checkpoint;
4. keep strategy/configuration separate from physically materialized/executed shard provenance;
5. make scratch/workspace ownership explicit per physical concurrent stream/request and separately for graph capture;
6. add forward-progress evidence in addition to heartbeat/readiness during B2/B3 and long-prefill stress;
7. preserve all prior cache, reliable-sync, PLE overlap, QSA, recurrent-state, MTP equal-acceptance and soak gates.

Safe serving remains **profitable singleton MTP + plain concurrent work** until state/workspace/concurrency isolation is certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. No fresh exact M1 rate receipt.

**P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Exact-rig web search surfaced older August Q2/Q3/Q4 cells already outside the new-freshness window; fully resident Q3_K_XL/native-MTP remains the canonical speed lane.

## Dual-M1 DS4-0731

No target movement. No fresh exact dual-M1 receipt.

## Future Blazer / 5.x-bit

Add distributed-shard ownership and scratch/workspace slot identity to the full execution descriptor. Mixed-bit packing/kernel selection must be certified under the actual small-M/verify-width/concurrency workspace regime, not only single-stream microbenchmarks.

---

# Standing decisions strengthened

- TP2 for Flash-Next now has a concrete qwen4_exp reference strategy, but remains a control until real two-Mac execution proves its economics.
- Distributed model support is not one fact: strategy definition, materialized shard shapes, collectives, arming and execution are separate provenance layers.
- Provenance/source gates must follow semantic ownership across refactors, not temporary syntax.
- Prefer structural immutability over regex-only mutation policing.
- Scratch/workspace buffers are owned execution state under concurrency.
- Graph-capture scratch needs separately pre-warmed/owned storage.
- Heartbeat health does not prove forward progress through collectives.
- Exact simultaneous B2/B3/B4 certification remains mandatory before claiming concurrent speculative serving.
- Refreshed/rebased metadata does not make older benchmark execution fresh.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
