# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest genuinely fresh/update search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-1414.md`

   **The 14:14 note is authoritative for workload-shaped cache-block sizing and agent TTFT/task-wall evidence, rMLX single-producer round telemetry/sink truth, packaged custom-kernel ABI provenance, per-step fast-prefill target/draft eligibility, UVA buffer-generation lifetime, hybrid attention-vs-recurrent distributed state mapping, small-M shape-aware dispatch, the official DeepSeek V4.1 Flash architecture update, and the refreshed Affine4 long-context backfill.**

4. Retain the immediately previous search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-0911.md`

   **The 09:11 note remains authoritative for the completed oMLX #3553 Flash-Next bit-exact-vs-tolerance benchmark decomposition, equal-acceptance cycle-cost methodology, independently quantized MTP-head evidence, V4.1 streamed conversion/quant-block requirements, and its exact-target screening result.**

5. Retain the 06:01 and 00:16 deltas:

   - `RESEARCH-WATCH-2026-09-10-0601.md` — M5-Max Flash-Next cold-prefill/PLE-overlap, two-Mac reliable Metal synchronization, execution-shape-specific decode/MTP/QSA work, K-only sparse-indexer memory, graph-address identity, replay-boundary retention and benchmark-window provenance;
   - `RESEARCH-WATCH-2026-09-10-0016.md` — BACKFILL / SOURCE-CORRECTION for the previously under-mined r/oMLX Flash-Next thread: realistic 120K/150K harness receipts, oQ5e memory/robustness, MTPLX speed-versus-reliability, 64-GB-class viability, PLE/N-gram residency and task-wall consequences.

6. Retain the 2026-09-09 deltas for DS4 selective projection/quant-shape behavior, full-machine-residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram work, quantized-FA compiled capability, routed-MoE tile geometry, RTX5070Ti capacity evidence, Atlas concurrency ownership, oMLX replay boundaries and vLLM concurrency/soak attribution.

7. Also retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

8. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

9. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Freshness discipline

The latest completed external search covers sources strictly after the prior boundary **2026-09-10 13:23:11 UTC** through the end of the current search.

**Hard source-freshness boundary for the next external search: 2026-09-10 18:22:16 UTC.**

This is the end-of-search boundary, not the later repository-write timestamp. Future passes must search strictly after this source boundary; repository-only commits must never create a source-search gap. Refreshed/rebased metadata does not make older benchmark evidence fresh.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 14:14 pass moves no row.**

Important Flash interpretation from the canonical target file:

- **40 tok/s** remains the B1 short/medium working target;
- the separate ~128K ladder remains **20 / 25 / 30 / 35 tok/s**;
- **400 tok/s** remains the realistic cold-prefill working target.

No new exact dual-M1/TB4 rate receipt was found this pass.

---

# Current newest incorporated evidence — 2026-09-10 14:14 ET

## FRESH / oMLX #3557 — cache block size is a workload parameter

M3 Max 64 GB / Qwen3.8-27B-oQ4e-mtp / native MTP3 / FP16 KV / 20 coding-agent tasks, same build with only paged-cache block size changed **4096 -> 512**:

- prefix hit rate **59.8% -> 88.7%**;
- tokens re-prefilled / attempt **13,892 -> 4,957 (-64.3%)**;
- TTFT **18.35 s -> 5.92 s (-67.7%)**;
- decode **45.65 -> 44.02 tok/s (-3.6%)**;
- full suite wall **2512.6 -> 1546.2 s (-38.5%)**.

The existing 4096 geometry-derived page is a poor fit for a stable ~3.6K system prompt and ~3.9-4.1K early turns because the reusable prefix may never complete a whole page. This is reuse/granularity evidence, **not a direct prefill-kernel speed measurement**.

**Promotion:** once serving is correct, sweep block/page size against representative agent traffic. Record stable-prefix length, cache-hit rate, re-prefilled tokens, TTFT, decode and end-to-end task wall separately. A small decode tax can be an excellent trade for much less repeated prompt work.

## FRESH / rMLX #555 — one authoritative per-round event and sink-derived telemetry

Commit `7d5ebefd63895aeadfcde2632e02172f7323edfa`, **15:27:28 UTC**.

Seven speculative loops now report through one `RoundReport`/`log_round` seam. The work exposed incorrect proxy-derived telemetry: `refolded` must come from actual recurrent refold work, and `n_committed` must be what the sink actually emitted after budget/stop clipping. Missing facts are omitted rather than written as zero; duplicate round events are removed; empty/missing-field comparisons fail closed and coverage is reported per cell.

**Promotion:** a telemetry field naming an action must come from the actual side effect/sink, not nearby control-flow arithmetic. Event target + field schema + reader copy are provenance.

## FRESH / oMLX #3558 — packaged Python/native-kernel ABI is execution identity

Commit `b6f64a86b0f18d0055c625c1a3f67916d3240447`, **15:26:24 UTC**.

The Mac app now refuses a custom-kernel build whose CPython implementation/cache tag/version/extension suffix differs from the bundled donor runtime, and validates the staged `_ext*.so` files after copy to catch stale artifacts.

**Promotion:** compiled capability provenance includes runtime-loader ABI and staged extension identity. A build-time import does not prove the packaged app can load/execute the kernel.

## FRESH / vLLM #56145 — fast-prefill target/draft topology and per-step arming

Commit `e6cb56337b49e606f55fde1870adbbb051e23f9f`, **17:36:04 UTC**.

KV-sharing fast prefill is defined over a contiguous suffix of eligible **target** layers; speculative draft layers can register after the target and share KV but must not extend/break that target suffix. The helper can decline the fast path per step for no-prefill, full-graph capture, multiple microbatches or missing logits-index metadata.

**Promotion:** configured fast-prefill is not armed/executed fast-prefill. Record target-vs-draft topology and per-step arm/fallback reason.

## FRESH / vLLM #55819 — UVA-backed writes require explicit slot lifetime

Commit `2e0ee66cab1e7a0fd2ccfb0992a0e4b5e940196d`, **14:27:16 UTC**.

UVA-backed state writes can avoid an extra H2D copy, but buffer-pool reuse/growth must retire prior GPU readers first.

**Promotion:** direct-visible/UVA-like control buffers require backing-storage + slot/generation identity and explicit reader-lifetime synchronization.

## FRESH / vLLM #55531 — hybrid distributed state mapping is cache-group aware

Commit `7cdd9304ae2e46572f220741bf86e0b3c2da569c`, **18:12:15 UTC**.

Hybrid attention + recurrent/Mamba state under distributed context parallelism now requires compatible local/remote sharding; attention prefix-block mapping is applied to attention cache groups rather than blindly to recurrent-state groups.

**Promotion:** QSA/KV blocks and GDN/recurrent state keep distinct ownership/transfer schemas. Peer sharding/interleave compatibility is part of the handshake and executed provenance.

## FRESH / llama.cpp #28457 — small-M dispatch must depend on M as well as N/K

Commit `6788edb4f325c1cb4210997eb79edcab2e27aeaa`, **17:20:18 UTC**.

Vulkan Qwen work changes small-vs-medium tile selection from N-only to M+N, permits split-K at small M when appropriate and adds an eligible m=1 operand-swap path, with boundary tests around M and width transitions.

**Promotion for Blazer:** mechanism only, but Q5/Q6/custom mixed-bit dispatch should key on actual M/N/K + quant format + verify width. Keep n=1 decode and small-M MTP verification separate.

## FRESH / OFFICIAL — DeepSeek V4.1 Flash architecture

DeepSeek's 2026-09-10 release identifies V4.1 Flash as a **552B MoE** using a new asymmetric **Causal-Encoder-Decoder**, with **8B active input** and **16B active output**, and native multimodality. DeepSeek states KV-cache HBM demand is **1/4** and SSD demand **1/8** of the prior generation and reports **437x** smaller KV than its first generation.

**Promotion:** this strengthens the future sparse-active-bandwidth/offload thesis, but it does not prove M1 fit and does not redefine DS4-0731. Keep V4.1 as a separate future architecture lane until a real quant/offload/runtime artifact establishes placement and traffic.

## UPDATE / BACKFILL — oMLX #3499 Affine4 long-context KV

The PR was refreshed after the cutoff, but underlying implementation/benchmark work carries earlier author dates/rebases, so the numeric cells are preserved as **UPDATE/BACKFILL rather than fresh target evidence**.

Current reported M5 Pro 48-GB / Qwen3.8-27B Affine4 cells include **291.9 PP / 12.3 TG at 150K** and **250.0 PP / 11.8 TG at 200K**; logical attention KV at 200K is reported **12.21 GiB native -> 3.71 GiB Affine4 (-69.6%)**. A separate 8K MTP control reports 16.9 TG off -> 36.1 TG on with 84/97 considered drafts accepted, and a 28,903-token thinking/MTP run supplies endurance evidence. Compression is lossy and general quality equivalence is not established.

**Promotion:** Affine4 is a long-context capacity/control candidate. Compare task quality, teacher-forced drift, acceptance by depth, memory, PP/TTFT, TG and task wall against native/TQ controls before adoption.

---

# Screened / no target movement

- oMLX #3553 has a post-cutoff metadata update but the same `a04d2408...` head/material benchmark evidence already incorporated in the 09:11 watch; do not double-count it.
- No new post-cutoff exact receipt for 2x M1 Max64/TB4 Flash-Next.
- No new post-cutoff exact receipt for 2x M1 Max64/TB4 DS4-0731.
- No new post-cutoff one-M1-Max64 canonical mature Qwen3.8-27B target cell.
- No new post-cutoff RTX5070Ti16 fully-resident Q3_K_XL/native-MTP canonical speed cell.
- Search surfaced older M1-Max64 27B and RTX community receipts, but they predate this boundary and are not fresh evidence.
- No post-cutoff `antirez/ds4` main change supplied stronger exact target evidence.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. workload-shaped cache/page-size sweep after replay correctness is stable;
2. stable-prefix length, hit rate, re-prefill tokens, TTFT and task wall as serving metrics;
3. packaged custom-kernel ABI + staged extension identity in compiled/executed provenance;
4. target-vs-draft topology and per-step fast-path arm reason;
5. type-specific attention-block versus recurrent-state transfer;
6. generation/lifetime ownership for direct-visible/UVA-like control buffers;
7. M/N/K/quant/verify-width-aware small-M dispatch;
8. all prior reliable-sync, selected-row PLE overlap, graph-layout, recurrent, concurrency, soak and equal-acceptance speculative gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until concurrency/state-isolation gates are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. #3557 is strong workload/cache transfer evidence on M3 Max 64 GB, not an M1 numeric receipt.

**P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the speed lane; older Q2/Q3/Q4 and host-backed/long-context results remain separate evidence cells.

## Dual-M1 DS4-0731

No target movement. V4.1 is a distinct future architecture lane, not an updated DS4-0731 rate receipt.

## Future Blazer / 5.x-bit

Add workload-shaped cache granularity, M/N/K/quant/verify-width-aware dispatch, independently tunable MTP-head precision, packaged ABI/runtime-loaded-kernel provenance, cache-group-aware distributed ownership, and task-wall/quality certification alongside raw rate.

---

# Standing decisions strengthened

- Cache reuse granularity is a serving/workload parameter, not only model geometry.
- TTFT and end-to-end task wall are first-class once TG is interactive.
- Telemetry must report actual sink side effects, not proxy arithmetic.
- Missing telemetry is absent, not zero; empty comparisons cannot pass.
- Packaged loader ABI belongs in compiled/executed custom-kernel identity.
- Fast-path configuration and per-step arming are separate provenance states.
- Attention/KV blocks and recurrent state require type-specific distributed transfer semantics.
- Direct-visible/UVA state needs explicit buffer-generation lifetime.
- Small-M kernel selection must use actual M plus N/K and quant geometry.
- DeepSeek V4.1 strengthens sparse/offload direction but does not establish M1 fit.
- Refreshed/rebased metadata does not make older benchmarks fresh.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
