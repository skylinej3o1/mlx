# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-09-1752.md`

   **The 17:52 note is authoritative for fresh full-machine-residency benchmark provenance, PP speculative broadcast operand-lifetime/device-happens-before evidence, rMLX single-source recurrent rollback/state construction, shared-KV read-only ownership, and the post-18:04:46 UTC no-target-move screening pass.**

4. Retain the immediately previous runtime deltas:

   - `RESEARCH-WATCH-2026-09-09-1402.md` — Qwen3.8-Flash-Next UVA PLE offload / Engram parallelism, NVFP4 packed gathered top-k projection, Flash-Next backend dispatch-limit qualification;
   - `RESEARCH-WATCH-2026-09-09-0941.md` — rMLX #552 request-record provenance, quantized-FA compiled-capability provenance, routed-MoE active-expert tile geometry;
   - `RESEARCH-WATCH-2026-09-09-0628.md` — exact RTX5070Ti IQ4_XS 256K capacity lane, Atlas concurrent-MTP ownership/counter regression, rMLX #549/#550 round/acceptance invariants, oMLX #3520/#3539 and vLLM mixed-concurrency/tail-ring/soak attribution;
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

**The 17:52 pass moves no row.** The new evidence materially strengthens qualification and benchmark provenance, but it is not an exact canonical target-lane rate receipt.

---

# Current newest evidence delta — 2026-09-09 17:52 ET

Starting canonical head: `1db04e8db706aaa281a82cf29805bd86af8ae574`.

Starting hard source-freshness boundary: **2026-09-09 18:04:46 UTC**.

## FRESH / oMLX #3520 — full-machine residency is benchmark provenance

Comment `5606588580` at **2026-09-09 18:12:36 UTC** reports M3 Ultra 512GB production validation on `Qwen3.8-Flash-Next-oQ4e-mtp` with gathered/fused/eager paths.

Full-machine-exclusive single-stream runs report about **74–90 tok/s through 16K–64K**, while merely leaving two sibling engines idle but resident reduces the same 16K workload to roughly **46–62 tok/s**. Controlled c2/c4 × 4K/16K A/Bs also put batched MTP **14–27% below plain batching** in aggregate.

**Promotion:** record every resident engine/process, keepwarm/preload activity and relevant memory residency as part of the benchmark cell. Batched MTP must beat an equal-residency plain-batching control before promotion. M3 Ultra rates do not transfer numerically to dual M1.

## FRESH / vLLM #55745 — PP draft broadcast source lifetime

`e8064a96d02db70ebc1ca922bc9aba967a654483` at **2026-09-09 19:55:56 UTC** fixes the PP speculative-draft broadcast by recording `input_batch.idx_mapping` on the broadcast stream. Recording only the derived `send` tensor was insufficient because the indexing source remains asynchronously consumed.

**Promotion:** PP/MTP qualification must prove producer -> collective/broadcast -> consumer device-stream happens-before and retain every asynchronously consumed mapping/index/control operand until the consumer completes. Host scope or successful collective issue is not proof.

## FRESH / rMLX #553 — one recurrent rollback/refold/state seam

`85690ce5208822024e9fa4a71f51b34e7576e66a` at **2026-09-09 20:50:08 UTC** centralizes round emission, rollback/refold-or-disarm, recurrent stack construction and actual rollback-arm reporting.

**Promotion:** one authoritative low-level mutation seam for recurrent rollback/refold/state construction; draft drivers retain semantic ownership and telemetry, but do not duplicate the state mutation machinery. Record which arm actually executed.

## FRESH / vLLM #55887 — shared-KV reader must not mutate owner state

`dcd544486b7f4672b3c2e60ea289f19d86cf355c` at **2026-09-09 21:51:34 UTC** adds AITER shared-KV prefill/extend support and explicitly validates that the shared layer reads the target cache without changing it, across prefill/extend/mixed shapes and cache layouts/dtypes.

**Promotion:** shared QSA/KV/state provenance identifies owner versus reader; reader paths need read-only/byte-stability checks and mixed-phase qualification. Sharing storage is not ownership transfer.

## UPDATE / exact-rig search

A fresh discussion update exists on a previously known **M1 Max 32GB** Qwen3.8-27B baseline, but its measurement predates this cutoff and does not match the canonical 64GB lane. No exact target receipt is promoted from it.

## SCREENED / no target move

- no new post-cutoff exact dual-M1 Max64/TB4 Flash-Next receipt;
- no new one-M1 Max64 Qwen3.8-27B receipt;
- no new fully-resident Q3_K_XL/native-MTP RTX5070Ti16 speed-lane receipt;
- no new dual-M1 Max64/TB4 DS4-0731 receipt;
- oMLX #3539 and vLLM #56037 have no new substantive post-cutoff result;
- antirez/ds4 and TurboQuant-MLX have no post-cutoff target-lane rate evidence.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. resident-engine-set / keepwarm / memory-residency provenance;
2. equal-residency plain-batching controls for every concurrent-MTP throughput claim;
3. lifetime of every PP speculative mapping/index/control operand through device consumer completion;
4. explicit producer -> collective -> consumer stream happens-before;
5. one recurrent rollback/refold/state-stack producer with executed-arm reporting;
6. shared-state owner/reader identity and read-only/byte-stability checks;
7. all prior PLE, QSA, packed-gather, boundary-materialization, B2 interleaving, mixed-concurrency and long-soak gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until per-slot state isolation, physical recurrent capacity, distributed PP+MTP ownership and equal-residency throughput benefit are all certified.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Keep fully-resident Q3_K_XL/native-MTP as the speed lane; host-backed long-context configurations remain separate capacity evidence.

## Dual-M1 DS4-0731

No target movement.

---

# Standing decisions strengthened this pass

- What else is resident on the machine is part of a benchmark cell.
- Idle resident engines are not equivalent to absent engines.
- Batched speculative throughput claims require equal-residency plain-batching controls.
- Derived-output lifetime does not prove source/index operand lifetime under asynchronous execution.
- PP correctness requires device-stream happens-before, not merely host ownership or successful broadcast issue.
- Recurrent rollback/refold/state mutation should have one authoritative low-level seam.
- Shared-state readers must prove they do not mutate owner state.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**
