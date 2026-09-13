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
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1533.md` — newest complete delta: TB routable-address discovery, executed PP ownership, live memory admission, lazy-send/collective ordering, internal prefill checkpoints, DCP interleave mapping, EPLB warmup isolation.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1237.md` — live-context-bounded sparse work, DFlash2 per-layer causality, DSpark candidate-pruned proposal head, MTP retained-history offload coverage, parallel JIT warmup, multimodal pre-prefill TTFT.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-0343.md` — dual-Mac failed-runtime recovery, exact rendered-context budgeting, SM120 physical-stride correctness, compiled speculative drafter evidence, producer-side norm/quant fusion.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-2300.md` — fused RMS/GDN verifier recurrence, expert-offload I/O/speculation economics, direct TB/RDMA cluster failure modes, shared physical host-cache ownership, speculative JIT warmup cardinality, draft-architecture provenance.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1735.md` — live-context-bounded DSA work, fused/graph-capturable prefill metadata, draft-config provenance, direct Flash-Next cluster PLE failure, 64-GB capacity/recovered REAP evidence.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1257.md` — GDN kernel-image route admission, device-authored adaptive metadata, no-forward KV-store lifecycle, coordinated long-prefill cancellation, recovered Flash-Next SP evidence.
9. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1103.md` — V4.1 CED bounded-replay Apple prefill, ds4 V4.1 Metal support, device-authoritative speculative metadata.
10. Older 2026-09-12 / 2026-09-11 / 2026-09-10 / 2026-09-09 notes remain retained for QSA/MTP, offload, PP/TP, recurrent rollback, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-13 16:37:16 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-13 19:33:05 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase, comment-only activity or merge-only churn. Resurfaced older evidence stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved in the 15:33 ET pass. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C from external evidence.**

---

# Newest directly relevant evidence — 2026-09-13 15:33 ET

## oMLX #3637 — routable Thunderbolt address discovery

**FRESH NEW / DIRECT DUAL-MAC TB4 BRING-UP EVIDENCE.**

The multicast handshake previously learned only the packet source address, which on direct TB can be IPv6 link-local; after scope removal a bare `fe80::` is undialable, while static TB IPv4 or APIPA `169.254.x.x` remained invisible until manually entered.

The proposed WASSUP address inventory advertises dialable candidates, keeps APIPA eligible, and requires an HTTP probe whose returned `node_id` matches before the address enters the peer record. Validation reported 154 discovery/pairing tests plus 137 pairing/UI tests passing; physical two-Mac hotplug validation remains pending.

**Promote:** transport identity is discovered peer -> advertised candidate -> probe-verified endpoint -> selected physical interface, not datagram source alone.

## oMLX #3638 — planned layer split vs actually loaded layer split

**FRESH NEW / HIGH-VALUE PP2 OWNERSHIP-CORRECTNESS.**

A model-specific `pipeline()` override silently recomputed an even split and ignored an approved unequal plan. A 78-layer ~432.7 GB deployment could plan 26/52 yet actually load 39/39, only failing after the entire load. The compatibility shim now makes the architecture-specific loader honor the assignment and maintain its cache/loop layer count.

**Promote:** planner assignment is not execution evidence. Certify the actual method invoked, contract marker, loaded start/end layers, cache range and executed stage.

## oMLX #3643 — live per-request rank admission ceiling

**FRESH NEW / LARGE-MODEL APPLE CAPACITY EVIDENCE.**

A rank's dynamic prefill ceiling was frozen immediately after model load: the field case captured **49.7 GiB** during the transient while the settled host reached **112.1 GiB** 11 seconds later. The stale ceiling kept rejecting a 68.3 GiB stage and contributed to a three-Mac 198.6 GB activation failure.

The fix re-reads the hard limit once per request while retaining live back-off under later pressure and build-time fallback on read failure. 201 related tests passed.

**Promote:** load transient, settled idle ceiling and decision-time live ceiling are separate capacity identities.

## oMLX #3644 — lazy stage-send dependency can deadlock a later collective

**FRESH NEW / HIGH-VALUE PP2 EXECUTION-ORDER EVIDENCE.**

With `sampling_rank_only` enabled, an otherwise working pipeline (~18 tok/s with the flag off) could report ready and never emit a token. A worker's stage send depended on a lazy full-forward graph that nothing evaluated; the token all-sum could therefore run first, leaving the worker blocked in the collective while rank zero waited on the missing receive.

The fix explicitly materializes the worker forward before the all-sum; an event-order test pins `eval < all_sum`. The exact physical topology is not yet rerun.

**Promote:** collective source order is insufficient. Record the lazy dependency that owns each send, the event that materializes it, and prove downstream collectives cannot overtake it.

## vLLM #56714 — internal prefill checkpoints avoid hidden full replay

**FRESH NEW / STRONG LONG-CONTEXT PREFILL MECHANISM TRANSFER.**

Kimi-K3 Triton KDA adds 64-token-aligned internal recurrent-state checkpoints so prefix reuse can resume from an internal state instead of performing an extra full-model prefill pass.

16x B200 A/B mean TTFT reductions ranged from **7.1% at random 8K** to **32.7% at 128K prefix + 2K suffix / concurrency 16**; 128K+2K c1 improved **3656.0 -> 2790.1 ms (-23.7%)**. All 1472 requests completed. A few single-token outputs differed across A/B, with repeat-to-repeat differences also present, so this remains mechanism/performance evidence rather than bit-exact output evidence.

**Promote for Flash-Next:** recurrent/GDN/QSA prefix hits must disclose internal-state checkpoint alignment and whether a supposedly cached prefix still triggers a hidden full-model replay.

## vLLM #56715 — indexer DCP/PCP interleave is execution identity

**FRESH NEW / DISTRIBUTED INDEXER-CORRECTNESS.**

PCP gather arithmetic assumed interleave 1. At DCP4/interleave64, token 1 could read token 64's key. The corrected mapping passed **72 ordering cases** across interleave 1/64, DCP2/4/8 and boundary/split-row contexts; restoring old arithmetic failed all 36 interleave64 cases.

**Promote:** QSA/indexer identity includes physical token interleave, local/global mapping, padding and gather order.

## vLLM #56716 — warmup traffic must not enter expert-load statistics

**FRESH NEW / MOE-EPLB MEASUREMENT-CORRECTNESS.**

MRV2 kernel warmup invokes real model execution and could contaminate EPLB expert-load counters at startup and immediately after elastic rebalance. The proposed fix suppresses EPLB accounting during warmup and restores the prior state afterward.

**Promote:** expert popularity, ownership and rebalance decisions must be based on real request traffic, with warmup/profiling/synthetic batches excluded.

---

# Fresh-screen negatives / non-promoted current artifacts

- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No exact RTX5070Ti16 Qwen3.8-27B throughput receipt.
- No exact new dual-M1 DS4-0731 receipt.
- No new vLLM DFlash/MTP PR was created in this search window.
- `jundot/omlx` main had no in-window commit; current Apple evidence above is open-PR evidence.
- `antirez/ds4` had no in-window commit.
- `llama.cpp` had NextN/MTP metadata guarding and unrelated maintenance only; no new active-lane Metal/Qwen speed receipt.
- External web/HF screening returned previously known M1 DFlash W4/A16 -> W4/A32 evidence and older Flash-Next 64GB reports, but no new source-time-qualified active-topology receipt. Do not refresh those evidence dates.
- vLLM #56713 is useful ABI/transport-provider provenance but not active-lane performance evidence.
- vLLM #56718 (MLA LoRA correctness) and #56719 (OTel/fork tracing) do not affect active target calibration.
- oMLX #3636 is the UI-side complement to #3637; #3637 is the higher-value discovery mechanism.
- oMLX #3642 is distributed SSD snapshot teardown hygiene rather than throughput evidence.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Certification now explicitly includes:

1. static TB IPv4 + APIPA address advertisement and probe verification;
2. planned assignment -> architecture-specific loader contract -> actual loaded layer range;
3. load-transient vs settled/live memory ceiling;
4. lazy graph materialization before dependent sends/collectives;
5. aligned recurrent-state checkpoint/resume vs hidden full-prefix replay;
6. DCP/interleave global-order reconstruction in indexer/QSA paths;
7. warmup exclusion from MoE expert-load statistics;
8. existing live-span/workspace, PLE, verifier peak, failure/reload, ABI, watchdog, TB/RDMA and long-context gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement and no P69 ordering change. This pass is largely distributed/long-context methodology. **P69B12 frozen/promoted; P69B13 next.**

## RTX5070Ti16

No target movement and no exact 5070-Ti speed receipt. Existing SM120 stride and executed-route gates remain.

## DS4-0731 dual M1

No target movement. The oMLX cluster findings directly strengthen dual-Mac PP/TB/capacity methodology; #56714 is recurrent-state checkpoint mechanism transfer only.

---

# Standing rules added/reinforced

- Discovery source address is not transport identity; advertise candidates and probe-verify the endpoint.
- Planned PP ownership is not executed ownership until the actual architecture-specific loader and loaded ranges are verified.
- Admission ceilings are decision-time state; load-transient minima are not permanent capacity facts.
- Lazy graph dependencies must be materialized before collectives whose progress depends on their send/recv side effects.
- Prefix-cache hits must disclose whether internal recurrent state resumes directly or causes hidden full-model replay.
- Distributed indexer identity includes physical token interleave and local/global mapping.
- Warmup/profiling/synthetic requests must not contaminate expert-load statistics.
- Merge/crawl time does not refresh older evidence.
- Requested/configured/planned remains distinct from built/available/contracted/admitted/executed.
- Final-output correctness does not certify speculative/distributed state correctness.
- Component/kernel gains do not move canonical targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
