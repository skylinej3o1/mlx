# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-09-1402.md`

   **The 14:02 note is authoritative for fresh Qwen3.8-Flash-Next UVA PLE offload / Engram-parallel evidence, NVFP4 DSpark packed gathered top-k projection evidence, Flash-Next backend dispatch-limit qualification, and the post-13:57:01 UTC no-target-move screening pass.**

4. Retain the immediately previous runtime deltas:

   - `RESEARCH-WATCH-2026-09-09-0941.md` — rMLX #552 request-record provenance, quantized-FA compiled-capability provenance, routed-MoE active-expert tile geometry;
   - `RESEARCH-WATCH-2026-09-09-0628.md` — exact RTX5070Ti IQ4_XS 256K capacity lane, Atlas concurrent-MTP ownership/counter regression, rMLX #549/#550 round/acceptance invariants, oMLX #3520/#3539, vLLM mixed-concurrency/tail-ring/soak attribution;
   - retain 2026-09-08 and older dated deltas for the remaining QSA, GDN/projection, recurrent rollback, cache lifecycle, concurrency and provenance evidence.

5. Also retain:

   `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md`

   as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

6. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

7. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 14:02 pass moves no row.** Cross-hardware PLE and packed-gather gains are mechanism evidence until reproduced on the exact target topology.

---

# Current newest evidence delta — 2026-09-09 14:02 ET

Starting canonical head: `e4a832db893151f0694e5230de0dddce355b2d8f`.

Starting hard source-freshness boundary: **2026-09-09 13:57:01 UTC**.

The `e4a832db...` cross-model KV/state-transfer note is an intervening **BACKFILL** from a 2026-08-04 paper and is not counted as post-cutoff source evidence.

## FRESH / vLLM #54371 — Qwen3.8-Flash-Next PLE placement and Engram parallelism

`3116c5d06bfe76501b3dd6b5434bfc7f3274f5e7` at **2026-09-09 14:32:34 UTC** adds pinned-host/UVA PLE offload and separates PLE/Engram sharding from the ordinary TP/DP model topology.

The measured Qwen3.8-Flash-Next-FP8 cells use 8K C2 prefill and C64 / 1024-token / MTP3 decode. TP4/DP1 prefill is **33,544.13 tok/s resident vs 33,322.61 offloaded**; raw decode is **2,261.37 vs 2,245.84**, while acceptance differs. The PR's acceptance-normalized comparison characterizes the offload delta as about **+1.84% TP4 and +2.86% DP2**, effectively flat at single-run precision.

**Promotion:** PLE is a separately placeable/shardable sparse lookup plane. On dual M1, measure resident vs file-backed placement, selected rows/bytes, page-cache/fault state, overlap, replication/sharding, consuming-stage locality and actual TB4 traffic. Do not transfer NVIDIA rates numerically.

## FRESH / vLLM #55713 — packed NVFP4 gathered top-k projection

`83fe99399ec0603b32393a14324b65c67ad04af2` at **2026-09-09 17:33:46 UTC** makes DSpark's selected-row Markov correction operate directly on retained packed NVFP4 W2 rows/scales: gather packed rows -> local group dequant -> small dot -> scatter.

The reported Nemotron 3.5 Lightning A/B is roughly **3-4% faster** with top-k 512 enabled in both T=0 and T=1 cells, with batch-size and CUDA-graph parity coverage.

**Promotion:** add packed selected-row quantized kernels to the portable 5.x-bit / Blazer candidate set. Quant packing should be co-designed for sparse gathers as well as dense QMV/GEMV and MTP small-M work.

## FRESH / llama.cpp #28592 — Flash-Next backend dispatch limit

`22397c31a00e78f55ae556c41fc78b717c5911bd` at **2026-09-09 14:54:15 UTC** changes Vulkan FILL dispatch to a 2D grid because Qwen3.8-Flash-Next could exceed Intel `maxComputeWorkGroupCount`.

**Promotion:** long-context/large-state qualification includes actual backend grid/dispatch limits; do not extrapolate route viability from small shapes alone. No Apple rate implication.

## SCREENED / no target move

- oMLX main: no post-cutoff main commit.
- rMLX: no post-cutoff commit.
- antirez/ds4: no post-cutoff commit.
- TurboQuant-MLX: no post-cutoff commit.
- vLLM #56037: no new substantive post-cutoff comment.
- broad exact-rig searches: no timestamp-qualified new exact dual-M1 Flash/DS4, single-M1 mature 27B, or fully-resident Q3_K_XL RTX5070Ti receipt.
- interesting web-discovered quantized/mmap PLE artifacts were not promoted as FRESH without a substantive post-cutoff timestamp.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. PLE physical-placement and actual selected-row traffic identity;
2. PLE replication/sharding topology independent of PP layer ownership;
3. cold/warm page-cache behavior for file-backed PLE;
4. proof that PLE placement creates no accidental dense/repeated TB4 traffic;
5. packed selected-row quantized projection kernels alongside dense QMV/GEMV candidates;
6. backend dispatch/grid-limit qualification at real large-state shapes.

All existing distributed/MTP/recurrent/QSA correctness and provenance gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot state isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Keep fully-resident Q3_K_XL/native-MTP as the speed lane and IQ4_XS host-backed hot/cold-KV as the separate long-context capacity lane.

## Dual-M1 DS4-0731

No target movement. The new DSpark path is portable sparse-quant kernel evidence only.

---

# Standing decisions strengthened this pass

- PLE/n-gram tables are a distinct sparse lookup plane, not ordinary streamed weights.
- Total parameter count is not per-token bandwidth when a large component is selected-row lookup.
- Offload economics are determined by selected-row traffic, locality, overlap and wall time, not full table size.
- PLE sharding topology is not automatically the same as PP/TP/DP topology.
- Sparse selected-row consumers should avoid dense dequantization where packed gathers are viable.
- The custom 5.x-bit quant objective includes sparse-gather kernel cost, not only dense GEMV/QMV quality/speed.
- Cross-hardware mechanism evidence does not move exact-target rates.
- No canonical target movement this pass.
- P69 remains isolated.
