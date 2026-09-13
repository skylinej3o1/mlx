# External runtime research watch — 2026-09-13 15:33 ET

## Search window

This complete pass covers substantive sources strictly after `2026-09-13 16:37:16 UTC` through the user-request cutoff `2026-09-13 19:33:05 UTC`.

Evidence timestamp means the substantive source timestamp, not crawl time, rediscovery, rebase, comment-only activity, or merge-only churn.

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | 40 tok/s @ ~128K active context | 400 tok/s | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | 25 tok/s | 110 tok/s native/exact-runtime | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | 120 tok/s | 250 tok/s | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | 15 tok/s | 180 tok/s | unchanged |

**P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. External evidence below does not reopen P69B8/B9/B10-C.**

---

## 1. oMLX #3637 — Thunderbolt discovery must advertise routable addresses, not infer them from multicast source

**FRESH NEW / DIRECT DUAL-MAC TB4 BRING-UP EVIDENCE.**

Cluster-v2 multicast discovery can discover a peer Mac yet still fail to learn the actual Thunderbolt IPv4 path. The wire protocol previously carried only `(node_id, http_port)` in WASSUP, so the receiver learned only the datagram source. On direct Thunderbolt this can be IPv6 link-local; after the process-local scope zone is stripped, the stored bare `fe80::` address is not dialable. Static TB IPv4 and self-assigned APIPA `169.254.x.x` addresses therefore remained invisible until typed manually.

The proposed fix adds an optional address inventory to WASSUP. Crucially, advertised addresses become **probe candidates, not trusted peer addresses**. The receiver probes the candidate and accepts it only if the returned `node_id` matches. Bare IPv6 link-local, loopback, multicast and unspecified addresses are excluded; IPv4 APIPA is deliberately retained because it is legitimate on macOS Thunderbolt. The inventory is cached for 30 s so discovery bursts do not repeatedly invoke interface enumeration.

Validation: 154 discovery/pairing tests plus 137 pairing/UI tests passed. Physical two-Mac hotplug/renumbering validation is still pending.

**Promote for Flash-Next/DS4 PP2 bring-up:**

- transport discovery identity includes **advertised address inventory + verification**, not packet-source inference alone;
- APIPA must remain eligible for Thunderbolt and be verified rather than range-banned;
- distinguish discovered peer, routable candidate, probe-verified endpoint and selected data interface;
- certify both static TB IPv4 and self-assigned `169.254/16`, both directions, plus hotplug renumbering.

## 2. oMLX #3638 — planned PP ownership is not executed ownership unless the model-specific loader honors it

**FRESH NEW / HIGH-VALUE PP2 OWNERSHIP-CORRECTNESS EVIDENCE.**

A GLM-5.2 cluster could plan unequal layer ownership such as 26/52 or 41/37, but the model's class-local `pipeline()` method silently recomputed an even split. A 78-layer model therefore loaded 39/39 even when the planner approved 26/52, and the mismatch was caught only after a full ~432.7 GB load cycle.

The generic pipeline patch was not sufficient because the architecture overrode the generic method. The proposed compatibility shim marks the **actual model-specific method** as assignment-aware, applies the approved layer range, and also updates `num_layers`, which the model uses for cache sizing and iteration. The native even-split behavior is retained outside the distributed-worker compatibility context.

Tests cover the reported 26/52 case, the second rank, odd 79-layer/3-rank assignments, contract detection and local-path preservation; cluster regression reported 1381 passed / 2 skipped.

**Promote:** requested/planned PP assignment -> patched/contracted loader -> actual loaded layer range -> cache-range ownership -> executed stage must be one certification chain. A planner receipt alone is not execution evidence, and post-load mismatch detection is too late for multi-hundred-GB models.

## 3. oMLX #3643 — rank prefill admission must use the live settled memory ceiling, not a load-transient snapshot

**FRESH NEW / DIRECT LARGE-MODEL APPLE CAPACITY EVIDENCE.**

A distributed rank's prefill guard sampled dynamic free-memory capacity once, seconds after weights landed, and froze that transient minimum for the engine lifetime. The field case measured a **49.7 GiB** frozen ceiling while the host settled to **112.1 GiB** 11 seconds later; a 68.3 GiB stage slice was then rejected forever even though the settled machine could admit it. Across a three-Mac 198.6 GB deployment, planner and guard disagreed by roughly 60 GB.

The fix re-reads the rank's `hard_limit` once per request, preserving the dynamic back-off if other applications later consume memory and falling back to the build-time value if the live read fails. Regression: 201 relevant prefill/inference/memory-guard tests passed.

**Promote:** capacity identity needs at least load/materialization transient, settled idle ceiling, live per-request ceiling and allocator/runtime usage. Do not certify a Flash-Next/DS4 capacity failure from a ceiling sampled during model-load transients.

## 4. oMLX #3644 — lazy PP forward must be materialized before a collective that depends on its stage send

**FRESH NEW / HIGH-VALUE PP2 EXECUTION-ORDER EVIDENCE.**

With `sampling_rank_only=true`, the same distributed deployment could run at ~18 tok/s when the flag was off yet hang forever when enabled, with collective sockets showing zero bytes. The worker built a full forward + LM-head graph lazily; its stage send depended on that graph, but the worker never sampled from the logits and therefore nothing forced evaluation. The token `all_sum` could be scheduled first: the worker blocked in the collective while rank zero waited on a stage receive that never occurred.

The proposed fix explicitly materializes the already-built worker logits before issuing the token collective. The optimized adapter-specific skip-logits path remains unchanged. A new event-order test pins `eval` before `all_sum`; 120 related tests passed. The exact physical two-machine Metal+CUDA topology has not yet been rerun.

**Promote:** PP2 correctness requires **dependency materialization ordering**, not merely matching collective order in source code. For each stage send/recv/collective, certify what lazy graph owns the send, what event evaluates it, and that no dependent collective can overtake it.

## 5. vLLM #56714 — internal recurrent prefill checkpoints can remove a redundant full-model replay

**FRESH NEW / STRONG LONG-CONTEXT PREFILL MECHANISM TRANSFER. Not Apple-topology evidence.**

Kimi-K3's Triton KDA backend adds 64-token-aligned internal recurrent-state checkpoints so a prefix-cache hit can resume from an internal state instead of performing an extra full-model prefill pass.

16x B200, TP8/DP2/EP16/DCP8, prefix caching enabled, paired A/B:

- random 8K c16: mean TTFT **3593.4 -> 3339.9 ms (-7.1%)**;
- random 32K c16: **10121.3 -> 8999.8 ms (-11.1%)**;
- 32K prefix + 2K suffix c1: **1662.5 -> 1343.2 ms (-19.2%)**;
- same c16: **8362.0 -> 7141.1 ms (-14.6%)**;
- 128K prefix + 2K suffix c1: **3656.0 -> 2790.1 ms (-23.7%)**;
- same c16: **28484.1 -> 19156.9 ms (-32.7%)**.

All 1472 completed requests succeeded. Single-token outputs differed in 6/704 paired outputs, with repeat-to-repeat differences also present, so this is performance/mechanism evidence rather than a bit-exact model-output receipt.

**Promote for Flash-Next:** recurrent/GDN/QSA prefix reuse should ask whether the runtime can checkpoint the authoritative internal state at aligned boundaries and resume only the suffix. The relevant identity includes checkpoint alignment, state precision, prefix-match boundary, speculative retained span and whether resume avoids a hidden full-model replay.

## 6. vLLM #56715 — DCP/PCP indexer gather mapping must include physical interleave

**FRESH NEW / INDEXER DISTRIBUTION-CORRECTNESS EVIDENCE.**

PCP index gathering assumed interleave=1. With DCP4/interleave64, token 1 could read the key belonging to token 64. The patch uses configured interleave when mapping gathered shards back to global token positions and keeps padded gathers in bounds.

Validation on current main: **72 ordering cases passed**, covering interleave 1/64, DCP2/4/8, short/boundary contexts and split request rows. Restoring the old arithmetic fails all 36 interleave64 cases.

**Promote for Flash-Next QSA/indexer work:** world size and logical shard count are insufficient execution identity. Record **physical token interleave, local->global mapping, padding extent and gather order**; a distributed indexer can be numerically wrong while all tensors have plausible shapes.

## 7. vLLM #56716 — kernel warmup must not contaminate expert-load statistics

**FRESH NEW / MOE-EPLB MEASUREMENT-CORRECTNESS EVIDENCE.**

MRV2 kernel warmup invokes real `execute_model`/sampling paths, causing dummy warmup batches to enter EPLB expert-load statistics. This happens at startup and after elastic-EP re-warm, immediately after rebalance. The proposed fix suppresses EPLB accounting around warmup and restores the previous flag afterward; the new test pins normal, exception and already-suppressed cases.

No GPU throughput result is claimed.

**Promote:** any Flash-Next MoE expert-load/routing study must separate **real request traffic from warmup/profiling/synthetic batches**. Expert popularity, ownership/rebalance and offload decisions are invalid if warmup samples pollute the measurement window.

---

## Fresh-screen negatives / non-promoted items

- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No exact RTX5070Ti16 Qwen3.8-27B throughput receipt.
- No exact new dual-M1 DS4-0731 receipt.
- No new DFlash/MTP PR was created in vLLM during this window.
- `jundot/omlx` main had no in-window commits; the Apple findings above are fresh open PR evidence.
- `antirez/ds4` had no in-window commit.
- `llama.cpp` had NextN/MTP metadata guarding and unrelated maintenance, but no new Metal/Qwen active-lane throughput receipt.
- Web/HF/community screening surfaced the previously known M1 DFlash W4/A16 failure -> W4/A32 recovery and older Flash-Next/64GB reports, but no source-time-qualified new active-topology receipt in this window. Do not refresh their evidence date.
- vLLM #56713 (ROCm RoCE userspace/kernel ABI mismatch) reinforces runtime ABI provenance, but is not directly active-lane evidence.
- vLLM #56718 is MLA LoRA correctness and #56719 is OTel/fork tracing lifecycle; neither changes active target calibration.
- oMLX #3636 complements #3637 by refusing undialable bare link-local IPv6 in the UI, but #3637 is the higher-value discovery-learning mechanism.
- oMLX #3642 improves distributed SSD snapshot reclamation on teardown; retain as lifecycle hygiene, not performance evidence.

---

## Current consequences by lane

### Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Add or reinforce:

1. advertise + probe-verify the actual TB4 IPv4/APIPA route;
2. planned assignment -> model-specific loader contract -> actual loaded ownership;
3. distinguish load-transient memory from settled/live per-request admission;
4. explicitly materialize lazy stage-send dependencies before downstream collectives;
5. evaluate aligned internal recurrent-state checkpoints to avoid hidden full-prefix replay;
6. include token interleave/global mapping in distributed QSA/indexer identity;
7. exclude warmup/synthetic requests from expert-load statistics;
8. retain existing live-span, workspace, PLE, verifier-peak, failure/reload, ABI, watchdog, TB/RDMA and long-context gates.

No target movement.

### Qwen3.8-27B M1 / P69

No target movement and **no P69 ordering change**. The new evidence is mostly distributed/long-context methodology. P69B12 remains frozen/promoted; P69B13 remains next only from internal measured evidence.

### RTX5070Ti16

No target movement. No exact 5070-Ti speed receipt appeared. Existing SM120 stride and route-certification gates remain; vLLM #56715/#56716 transfer only as distributed/indexer and measurement methodology where applicable.

### DS4-0731 dual M1

No target movement. #3637/#3638/#3643/#3644 are directly useful to dual-Mac PP reliability/capacity methodology. #56714 is recurrent-state checkpoint mechanism transfer from another architecture/hardware, not a DS4 receipt.

---

## Standing rules added/reinforced

- Discovery source address is not transport identity; advertise candidates and probe-verify the selected endpoint.
- Planned PP layer ownership is not executed ownership until the actual architecture-specific loader contract and loaded ranges are verified.
- Dynamic admission ceilings must be sampled at the decision point; load-transient minima are not permanent capacity facts.
- Lazy graph dependencies must be materialized before any collective whose progress depends on their send/recv side effects.
- Prefix-cache hits must disclose whether recurrent/internal state can resume directly or triggers hidden full-model replay.
- DCP/PCP/indexer identity includes physical interleave and local/global token mapping.
- Warmup/profiling traffic must not contaminate expert-load statistics or routing decisions.
- Merge/crawl time does not refresh older evidence.
- Requested/configured/planned route remains distinct from built/available/contracted/admitted/executed route.
- Final-output correctness does not certify speculative/distributed state correctness.
- Component/kernel gains do not move canonical targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
