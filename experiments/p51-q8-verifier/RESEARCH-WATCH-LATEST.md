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
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-2300.md` — newest complete delta: fused RMS/GDN verifier recurrence, expert-offload I/O/speculation economics, direct TB/RDMA cluster failure modes, shared physical host-cache ownership, speculative JIT warmup cardinality, draft-architecture provenance.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1735.md` — live-context-bounded DSA work, fused/graph-capturable prefill metadata, draft-config provenance, direct Flash-Next cluster PLE failure, 64-GB capacity/recovered REAP evidence.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1257.md` — GDN kernel-image route admission, device-authored adaptive metadata, no-forward KV-store lifecycle, coordinated long-prefill cancellation, recovered Flash-Next SP evidence.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1103.md` — V4.1 CED bounded-replay Apple prefill, ds4 V4.1 Metal support, device-authoritative speculative metadata.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0313.md` — M1-targeted 27B DFlash2 FP16 candidate, proposal-head precision A/B, verifier-peak profiling, shared-expert padding/fusion.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0111.md` — Blackwell NVFP4-KV physical execution identity.
9. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-2022.md` — QSA bounded-workspace lifetime, DFlash per-layer normalization, YaRN consistency.
10. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md` — exact expert-offload read overlap, logical-vs-physical padded shape, JIT specialization.
11. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md` — PP+MTP ownership and pointer freshness.
12. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md` — dual-node load transient, TB control transport, Metal expert-tail geometry, rollback correctness.
13. `RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` and `RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` remain backfill/mechanism context only.
14. Older 2026-09-10 / 2026-09-09 notes remain retained for TP/PP, recurrent rollback, QSA/MTP, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-12 21:35:07 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-13 03:00:39 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase, comment-only activity or merge-only churn. Resurfaced older evidence stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved in the 23:00 ET pass. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C from external evidence.**

---

# Newest directly relevant evidence — 2026-09-12 23:00 ET

## oMLX #3626 — fused RMS/GDN verification recurrence

**FRESH NEW / DIRECTLY RELEVANT VERIFIER-MECHANISM CANDIDATE. Not an exact active-lane receipt.**

The opt-in Qwen4 path fuses RMS/scaling prework, full GDN recurrence, gated normalization and recurrent rollback snapshots into one dispatch with narrow B1/S3-4/BF16-projection/FP32-state admission.

A separately qualified composed source reported exact 18/18 fixed-length cells and median decode:

- 16K: **77.20 -> 78.09 tok/s**;
- 32K: **79.13 -> 81.00**;
- 64K: **75.70 -> 76.97**.

Only 16K passed the stated thermal gate; 32K/64K are diagnostic. The isolated PR head itself has CPU validation only and the PR does not establish an exact active-hardware/model identity for those throughput numbers.

**Promote:** normalization + recurrent update + rollback-state materialization can be one verifier ownership boundary only when cache advance and every rollback snapshot remain exact. This is a Flash transfer experiment and a conceptual 27B analogue, **not P69B13 evidence**.

## oMLX #3628 — expert-offload I/O and speculation economics

**FRESH NEW / STRONGER-APPLE V4.1 CAPACITY + I/O TRANSFER. Not DS4-0731 target evidence.**

Replacing Engram-style scattered-row access with contiguous expert-slab `preadv`, dedicated read workers, bounded in-flight payload and expert-boundary chunking changed synthetic cold M5 Max expert fetch from **0.23 -> 9.3 GB/s**, one-token per-MoE-layer read cost from **362 -> 9.1 ms**, and sorted 256-token prefill from **33 -> 568 token-layers/s**.

Real V4.1 oQ3e on a 128 GB M5 Max reported:

- 12.5% expert residency: 38.0 GiB Metal active, 49.6 GiB peak, **28 PP / 5.6 TG**, hit rate 0.69;
- 25%: 65.7 GiB active, 77.4 GiB peak, **25 PP / 4.2 TG**, hit rate 0.78.

The lower-residency arm was faster because extra free RAM became filesystem page cache. More importantly, a 5-token verification block touched roughly **4.6x** as many experts as one-token decode under these miss-bound conditions; speculative decode was estimated to lose badly despite higher tokens/step.

**Promote:** speculation profitability includes nonresident expert touches, misses, fetched bytes, resident fraction and page-cache state; acceptance/tokens-per-step alone is insufficient. Scattered Engram rows and contiguous expert slabs need separate I/O primitives and queues.

## oMLX #3620/#3621/#3625 — exact dual-Mac transport/reliability lessons

**FRESH NEW / DIRECTLY RELEVANT TOPOLOGY MECHANISM EVIDENCE. No TG/PP receipt.**

- **#3620:** packaged workers can leak app `PYTHONHOME/PYTHONPATH` into system-Python JACCL/socket helpers, crashing communicator bootstrap. Helper-process runtime/ABI/environment belongs in distributed execution identity.
- **#3621:** active direct Thunderbolt/RDMA links using macOS self-assigned `169.254/16` were rejected as unroutable, causing Wi-Fi fallback. Link-local Thunderbolt is valid; certify the actual selected interface/address/transport.
- **#3625:** heavy TB/RDMA prompt ingestion can delay SSH health probes beyond 5 seconds; the previous 3-second interval/two-failure policy could kill healthy ranks after roughly six seconds. Liveness-plane policy must tolerate dataplane collective stalls and be tested during long-prefill load.

These directly strengthen PP2/TB4 bring-up methodology without moving throughput targets.

## vLLM #56629 — shared physical HiSparse host pool across TP ranks

**FRESH MERGE / MEMORY-OWNERSHIP TRANSFER. Not Metal evidence.**

For single-node multiprocess TP, replicated MLA source KV is mapped to one mmap-backed pinned-host pool instead of one physical copy per TP rank. Rank 0 writes; peers wait on IPC events. Tests cover visibility, creator-only population, SIGKILL cleanup and exact round trips, but no production-sized model/performance run was performed.

**Promote:** logical per-rank state and physical backing are different dimensions. Replicated host-side state can share physical storage only with explicit producer/event ownership. PP2 remains primary; this does not make TP2 preferred.

## vLLM #56323 -> #56649/#56654 — DFlash/MTP JIT warmup cardinality blowup

**FRESH INTEGRATION CHURN / COMPILE-LIFECYCLE WARNING. Not a throughput result.**

#56323 merged explicit MRV2 sampler/DFlash/MTP JIT warmup. Follow-up CI evidence reports about **120 warmup keys per fresh engine**, with multi-engine lanes accumulating roughly **700-1,400 seconds** of compilation and timing out while tests otherwise progressed. #56654 proposes reverting the MRV2-specific migration; its targeted tests pass but no e2e serving/startup/first-request benchmark exists yet.

**Promote:** compile/prewarm key count and total wall time are part of execution identity. Benchmark fresh process, explicit prewarm cost, first real request, first new shape, warm steady state and realistic shape churn separately.

## vLLM #56641 — explicit draft architecture must survive MTP-family rewrites

**FRESH NEW / SPECULATIVE CONFIG-PROVENANCE CORRECTNESS.**

A Qwen-family DSpark checkpoint declaring `Qwen3DSparkModel` was being rewritten to a Qwen MTP architecture based on `model_type` alone, after which DSpark dispatch could fall through to an incompatible DeepSeek implementation. The proposed fix preserves the explicit DSpark architecture; config/dispatch tests pass, but end-to-end Qwen DSpark is not claimed.

**Promote:** explicit draft architecture is authoritative unless a conversion proves otherwise. `model_type`, MTP-like fields and target-family resemblance are not enough to rewrite the draft execution class. This reinforces target-vs-draft config separation for DFlash2/DSpark/Lightning experiments.

---

# Fresh-screen negatives

- `jundot/omlx` main: no post-boundary commits; the important Apple evidence above is in fresh open PRs.
- `antirez/ds4`: no in-window commits and no new exact dual-M1 0731 receipt.
- `llama.cpp`: in-window structured logging and Qwen3-Coder schema/parser work only; no active-lane Metal throughput/correctness receipt.
- vLLM MHC/DSv4 warmup migration activity was screened; no exact active M1/5070Ti target receipt.
- Web/HF/Reddit screening did not produce a source-time-qualified post-boundary exact active-lane result strong enough to promote. Crawl time does not reset evidence time.
- no new exact dual-M1 Flash-Next TG/PP receipt;
- no new exact M1 Max64 Qwen3.8-27B receipt;
- no canonical RTX5070Ti16 receipt;
- no exact new dual-M1 DS4-0731 receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Certification now explicitly includes:

1. JACCL/control-sidecar process environment and ABI;
2. selected physical network interface/address/transport, including valid TB/RDMA link-local;
3. heavy-prefill watchdog survival and liveness/dataplane decoupling;
4. verifier fusion ownership across normalization, recurrence and exact rollback snapshots;
5. compile/prewarm key count and total startup compilation wall time;
6. logical per-rank vs physical replicated host-state ownership;
7. existing live-context bounds, QSA workspace lifetime, proposal precision, draft config, spec-verifier peak shape, rank-local PLE loader path, PP/MTP pointer/state and long-context gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement. #3626 is conceptually aligned with our GDN verifier campaign but **does not become P69B13 evidence**, does not alter the frozen ruler, and does not reopen closed branches. It is a separate external mechanism candidate to revisit only after the existing P69 plan or independent reproduction under our ruler.

Draft architecture/config identity is further reinforced by #56641.

## RTX5070Ti16

No target movement. The JIT warmup cardinality evidence matters to CUDA startup/benchmark methodology; #56629/#56641 are transfer/correctness evidence, not 5070 Ti speed receipts.

## DS4-0731 dual M1

No target movement. #3628 is later-V4.1/M5 capacity evidence only, but strongly supports disabling speculation whenever verifier blocks multiply expert misses. #3620/#3621/#3625 are directly useful dual-Mac bring-up/reliability lessons.

---

# Standing rules added/reinforced

- Fused recurrent verification must certify cache advance **and every rollback snapshot**, not only final output.
- Speculation economics must include nonresident expert touches/misses/fetched bytes per verification step.
- Storage primitives must match physical access shape: scattered-row gather and contiguous slab reads are distinct lanes.
- Distributed execution identity includes helper-process environment/ABI, selected physical interface/address and liveness policy.
- Logical replicated state and physical backing are separate; physical deduplication requires explicit producer/consumer synchronization.
- JIT warmup cardinality and total compile wall time belong in benchmark identity.
- Explicit draft architecture beats family/model-type heuristics unless a conversion proves equivalence.
- Requested/configured route remains distinct from built/available/admitted/executed route.
- Final-output correctness does not certify speculative correctness; acceptance/task quality remain separate.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
