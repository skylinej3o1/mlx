# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest genuinely fresh/update search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-1928.md`

   **The 19:28 note is authoritative for the fresh oMLX #3566 `qwen4_exp` distributed TP strategy, rMLX #557 semantic-population charge/sampling gates, vLLM #56098 per-stream/capture split-K workspace ownership, the rebased oMLX #3040 forward-progress watchdog backfill, and this pass's exact-target screening result.**

4. Retain the immediately previous search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-1715.md`

   **The 17:15 note remains authoritative for rMLX #556's mutation-checked shared-round-skeleton design, the narrowed oMLX #3468 SSD expert-streaming implementation/capacity-only benchmark classification, and oMLX #3063 requested/planned/measured/effective prompt-cache retuning semantics.**

5. Retain the 14:14, 09:11, 06:01 and 00:16 deltas:

   - `RESEARCH-WATCH-2026-09-10-1414.md` — workload-shaped cache blocks and agent TTFT/task wall, sink-truth telemetry, packaged custom-kernel ABI, fast-prefill target/draft arming, UVA lifetime, hybrid distributed state mapping, small-M dispatch, V4.1 architecture and Affine4 backfill;
   - `RESEARCH-WATCH-2026-09-10-0911.md` — Flash bit-exact-vs-tolerance cycle decomposition, equal-acceptance methodology, quantized MTP-head evidence and V4.1 streamed conversion/quant-block requirements;
   - `RESEARCH-WATCH-2026-09-10-0601.md` — M5 Flash cold-prefill/PLE overlap, two-Mac reliable Metal synchronization, QSA/MTP shape work, graph-address identity and replay-boundary retention;
   - `RESEARCH-WATCH-2026-09-10-0016.md` — BACKFILL / SOURCE-CORRECTION for the under-mined r/oMLX Flash thread: realistic 120K/150K harness receipts, oQ5e memory/robustness, MTPLX speed-versus-reliability, 64-GB viability, PLE/N-gram residency and task-wall consequences.

6. Retain the 2026-09-09 deltas for DS4 selective projection/quant-shape behavior, full-machine-residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram work, quantized-FA compiled capability, routed-MoE tile geometry, RTX5070Ti capacity evidence, Atlas concurrency ownership, oMLX replay boundaries and vLLM concurrency/soak attribution.

7. Also retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

8. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

9. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Freshness discipline

The latest completed external search covers sources strictly after the prior boundary **2026-09-10 21:24:31 UTC** through the end of the current search.

**Hard source-freshness boundary for the next external search: 2026-09-10 23:28:08 UTC.**

This is the end-of-search boundary, not the later repository-write timestamp. Future passes must search strictly after this source boundary; repository-only commits must never create a source-search gap. Refreshed/rebased/force-pushed metadata does not make older benchmark execution fresh.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 19:28 pass moves no row.**

Important Flash interpretation from the canonical target file:

- **40 tok/s** remains the B1 short/medium working target;
- the separate ~128K ladder remains **20 / 25 / 30 / 35 tok/s**;
- **400 tok/s** remains the realistic cold-prefill working target.

No new exact dual-M1/TB4 rate receipt was found this pass.

---

# Current newest incorporated evidence — 2026-09-10 19:28 ET

## FRESH / oMLX #3566 — concrete `qwen4_exp` TP2 control topology

Created **22:08:36 UTC**, head `5dcadc1b177df5b87830620cbce5e2e11ed4fb53`.

Adds a dedicated distributed tensor strategy for `qwen4_exp` / `qwen4_exp_text`: separate GDN QKV/Z/B/A projection sharding, depthwise conv/group slicing, recurrent `A_log`/`dt_bias` value-head ownership, row-parallel GDN out-proj reduction, full-attention Q/K/V/O sharding, MoE switch/shared-expert sharding, and planner divisibility checks.

Validation is unit/cluster tests only: 47 focused tests and 1279 `cluster or tensor` tests pass (13 skipped). **No physical two-Mac rate receipt.**

**Promotion:** TP2 is now a concrete Flash-family control lane rather than a conceptual one. Compare its real collective bytes/waits against PP2 stage-boundary traffic on the exact checkpoint; keep strategy/configuration separate from materialized/executed shard provenance. PP2 remains primary until exact measurements say otherwise.

## FRESH / rMLX #557 — gates follow semantic ownership through the shared-loop migration

Commit `8fc0f043e479eb3215cc6333552f223cf9c62c7e`, **22:54:32 UTC**.

Charge/sampling gates now follow classic/forwarded loops, entries and rollback/dispatch owners across the migration rather than relying on temporary function signatures. The forwarded `RoundCfg` is immutable; scanners strip comments/strings, fail closed on ambiguous config ownership and carry mutation fixtures across current/mid-migration/end-state trees.

**Promotion:** provenance gates must follow semantic owners, gate both decision and consumption sides, prefer structural immutability over regex-only policing, and prove recall against migration-state mutations.

## FRESH / TRANSFER — vLLM #56098: split-K scratch is stream-owned execution state

Commit `9163190dda009a310d8c175d63860ac7c671ca90`, **22:14:22 UTC**.

ROCm shared-expert skinny GEMM now gives split-K scratch explicit per-stream slots plus separate graph-capture slots; normal exhaustion has a safe but slower per-call fallback, and graph capture requires pre-warmed reserved storage. Split-K depth also depends on actual shard/readback geometry rather than one global threshold.

**Promotion:** scratch/workspace buffers need stream/request/generation ownership and graph-capture identity. B2/B3/B4 cannot be certified with process-global shared scratch merely because that state is temporary.

## UPDATE / BACKFILL — oMLX #3040: heartbeat health != pipeline progress

Current branch was recommitted at **23:08:53 UTC**, but the commit author date is 2026-08-22, so this is not fresh execution evidence.

The observation describes a two-Mac TP2 deployment where two concurrent streams wedged mid-prefill while heartbeats/processes/SSH all looked healthy. The proposed watchdog keys on `batch_steps` progress while requests are in flight; idle quiescence is explicitly not a stall.

**Promotion:** cluster liveness and forward progress are separate facts. Add monotonic in-flight progress evidence to concurrent/long-prefill qualification and keep supervisor recovery distinct from proving the underlying collective bug fixed.

---

# Screened / no target movement

- No post-cutoff oMLX mainline rate receipt; #3566 is strategy/test evidence.
- No new post-cutoff exact 2x M1 Max64/TB4 Flash-Next rate receipt.
- No new post-cutoff exact 2x M1 Max64/TB4 DS4-0731 rate receipt.
- No new post-cutoff canonical one-M1-Max64 Qwen3.8-27B receipt.
- No new post-cutoff RTX5070Ti16 fully-resident Q3_K_XL/native-MTP canonical speed receipt.
- Exact-rig web results were older August or undated/crawled-today observations; crawl time does not make them fresh.
- Later visible vLLM/llama.cpp activity did not provide stronger exact Apple target evidence.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as a concrete control**.

Add/strengthen:

1. reproduce #3566's exact qwen4_exp shard topology for TP2 control;
2. measure collective bytes/waits for GDN out-proj, full attention and MoE reductions versus PP2 stage-boundary traffic;
3. verify exact checkpoint divisibility, conv groups and recurrent-head ownership;
4. track strategy → materialized shards → collective topology → armed → executed provenance;
5. give scratch/workspace state explicit per-concurrent-stream ownership and separate graph-capture storage;
6. add in-flight forward-progress monitoring to B2/B3 and long-prefill stress;
7. retain all prior reliable-sync, PLE overlap, cache-page-size, QSA/recurrent ownership, MTP equal-acceptance and soak gates.

Safe serving remains **profitable singleton MTP + plain concurrent work** until concurrency/state/workspace isolation is certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. No fresh exact M1 rate receipt.

**P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane.

## Dual-M1 DS4-0731

No target movement. No fresh exact dual-M1 receipt.

## Future Blazer / 5.x-bit

Add distributed-shard ownership and scratch/workspace slot identity to the execution descriptor. Mixed-bit kernels must be certified under the actual small-M/verify-width/concurrency workspace regime rather than single-stream microbenchmarks only.

---

# Standing decisions strengthened

- TP2 now has a concrete qwen4_exp reference strategy, but remains a control until physical two-Mac execution proves its economics.
- Distributed support is not one fact: strategy definition, materialized shard shapes, collectives, arming and execution are separate.
- Source/provenance gates must follow semantic ownership across refactors.
- Prefer structural immutability over regex-only mutation policing.
- Scratch/workspace memory is owned execution state under concurrency.
- Graph-capture scratch needs separately pre-warmed/owned storage.
- Heartbeat health does not prove collective forward progress.
- Exact simultaneous B2/B3/B4 certification remains mandatory.
- Refreshed/rebased metadata does not make older benchmark execution fresh.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
