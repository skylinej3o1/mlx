# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest source-correction/backfill delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-0016.md`

   **The 00:16 note fully incorporates the previously under-mined r/oMLX Flash-Next thread: realistic 120K/150K harness receipts, oQ5e memory/robustness evidence, MTPLX speed-versus-reliability evidence, 64-GB-class viability, conditional PLE/N-gram residency, runtime-engine deltas, and tokens-to-solution/task-wall-clock consequences. It is BACKFILL / USER RECEIPT / TRANSFER evidence and moves no target.**

4. Read the newest genuinely fresh search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-09-2034.md`

   **The 20:34 note remains authoritative for the latest post-cutoff search evidence: DS4 selective-projection Q4 phase/shape behavior, fused sparse-index score/top-k/attend contracts, quant-format matrix-shape cliffs, direct-visible versus staged-copy control traffic, and resulting 5.x-bit / Blazer co-design implications.**

5. Retain the immediately previous runtime deltas:

   - `RESEARCH-WATCH-2026-09-09-1752.md` — full-machine-residency benchmark provenance, PP speculative broadcast operand lifetime/device happens-before, rMLX single-source recurrent rollback/state construction, shared-KV read-only ownership;
   - `RESEARCH-WATCH-2026-09-09-1402.md` — Qwen3.8-Flash-Next UVA PLE offload / Engram parallelism, NVFP4 packed gathered top-k projection, backend dispatch-limit qualification;
   - `RESEARCH-WATCH-2026-09-09-0941.md` — rMLX request-record provenance, quantized-FA compiled-capability provenance, routed-MoE active-expert tile geometry;
   - `RESEARCH-WATCH-2026-09-09-0628.md` — exact RTX5070Ti IQ4_XS 256K capacity lane, Atlas concurrent-MTP ownership/counter regression, round/acceptance invariants, oMLX boundary materialization, vLLM mixed-concurrency/tail-ring/soak attribution;
   - retain 2026-09-08 and older dated deltas for the remaining QSA, GDN/projection, recurrent rollback, cache lifecycle, concurrency and provenance evidence.

6. Also retain:

   `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md`

   as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

7. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

8. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Freshness discipline after the 2026-09-10 thread backfill

The 00:16 ET thread incorporation is a **BACKFILL / SOURCE-CORRECTION** commit, not a new internet freshness pass.

**Hard source-freshness boundary remains: 2026-09-10 00:38:49 UTC.**

The next external search must search strictly after that timestamp. Do **not** use the newer repository commit timestamp as the source cutoff, or material posted between 00:38:49 UTC and the backfill commit would be skipped.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 00:16 backfill moves no row.**

Important Flash interpretation from the canonical target file:

- **40 tok/s** remains the B1 short/medium working target;
- the separate ~128K ladder remains the recorded **20 / 25 / 30 / 35 tok/s** confidence ladder;
- **400 tok/s** remains the realistic cold-prefill working target.

The Reddit receipts strengthen long-context plausibility on newer Apple silicon but do not redefine 40 tok/s as an exact dual-M1 128K receipt or target.

---

# Current newest incorporated backfill — 2026-09-10 00:16 ET

Source: full user-supplied capture of the r/oMLX thread `Qwen3.8-Flash-Next-oQ4e-mtp with oMLX 0.6.4 is an absolute wonder !`.

## BACKFILL / USER RECEIPT — realistic Apple-silicon harness context

Promoted receipts include:

- M4 Max 128 GB / Jundot oQ4e-MTP / Pi / 120K configured context / low reasoning: **stable 30+ TG** in practical use;
- separate M4 Max 128 GB user after KV/PLE warmup: approximately **500 PP / 40 TG**, active-context denominator unspecified;
- M5 Max daily-driver user: **>30 TG up to ~150K**, memory pressure near ~200K, with no reported oMLX loops/tool-call errors in that workload.

These are useful long-context user receipts, not exact dual-M1 target-lane measurements.

## BACKFILL / USER RECEIPT — Q5 robustness/headroom

M5 Max 128 GB report under broadly similar conditions:

- oQ4e roughly **93 GB total-system memory**;
- oQ5e roughly **102-103 GB total-system memory**;
- normal prompts often indistinguishable;
- difficult constraint/stability tasks favored Q5 in the reported examples, including fewer constraint failures and no observed Q5 reasoning loops during that user's testing.

**Promotion:** treat oQ5e-class weights as the primary quality-shape candidate while retaining oQ4e as speed/control. Blazer certification must explicitly measure hard-constraint stability, loop/runaway rate and long-task completion, not only average chat quality.

## BACKFILL / USER RECEIPT — MTPLX speed/control versus reliability

Multiple M5/M2 users report large MTPLX TG gains, including roughly **50-100%** gains and a **70-75 TG** M5-Max report, but users also report loops/hallucinations and returning to slower oMLX for reliability.

**Promotion:** MTPLX is a frontier speed/control runtime to mine. Promotion requires same-weight/config behavioral parity, tool-call/state correctness, MTP acceptance and output/task certification.

## BACKFILL / USER RECEIPT — 64 GB viability, not exact M1 proof

One commenter reports **12-20 TG on a 64 GB Max**, but does not identify the Max generation; another commenter explicitly reports inability to get the setup running on M1 Max.

**Do not promote this to the exact M1 Max64 lane.**

## BACKFILL / USER RECEIPT — PLE residency/offload is conditional

A M5 Max 128 GB user reports that disabling SSD N-gram offload improves speed while still allowing ~128K context.

**Promotion:** target-topology qualification must A/B resident, SSD-backed, hot-resident/cold-SSD and PP-stage-local PLE policies. Record memory headroom, context ceiling, I/O/page-fault behavior and TB4 traffic.

## BACKFILL / TRANSFER — runtime and task-efficiency metrics

The thread also strengthens two methodological requirements:

- same-model GGUF-to-oMLX anecdotal jumps as large as **10-32 -> 35-70 TG** show that runtime/graph/kernel identity can dominate nominal quant labels;
- a reported slower DS4-family model sometimes reached similar answers with fewer tokens, reinforcing **tokens-to-solution / task wall-clock** as a first-class agent metric.

A newer M5 mlx-serve/NAX report of roughly **52 TG sustained across ~50K output tokens / ~1200 PP** remains a stronger-hardware/runtime ceiling receipt only.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. usable-context TG cells at 32K / 64K / ~128K / capacity edge;
2. cold versus warm KV/PLE state as mandatory provenance;
3. resident versus SSD-backed versus hybrid PLE policy A/B;
4. oQ5e-class primary quality-shape candidate; oQ4e speed/control;
5. MTPLX as speed-control implementation, never automatic production baseline;
6. loop/runaway, tool-call integrity, long-task completion and tokens-to-solution metrics;
7. context headroom and allocator stability in quant utility;
8. all previous quant-shape, QSA paired-backend, recurrent ownership, rollback, boundary-materialization, resident-engine, concurrency and soak gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until the existing concurrency/state-isolation gates are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. **P69B12 frozen/promoted; P69B13 remains next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the speed lane; host-backed long-context configurations remain a separate capacity lane.

## Dual-M1 DS4-0731

No target movement. Cross-model task-efficiency anecdotes affect the evaluation harness, not the exact hardware rate.

---

# Standing decisions strengthened

- Real agent usability must be measured at realistic active context.
- Warm KV/PLE state is benchmark provenance.
- PLE residency policy is hardware/memory/context dependent.
- Q5's probable value is difficult-tail robustness/headroom more than obvious normal-chat gains.
- MTPLX is a valuable speed-control implementation but requires correctness certification before adoption.
- Runtime implementation can dominate nominal BPW/model choice.
- Quant utility includes quality-tail robustness, TG, PP, MTP acceptance, memory, usable context and allocator stability.
- Agent evaluation includes tokens-to-solution / task wall-clock, not TG alone.
- The future custom 5.x-bit / Blazer project continues to co-design sensitivity, packing, group geometry, sparse gathers, MTP small-M kernels and PP stage balance.
- Cross-runtime/cross-hardware user receipts do not move exact target rates without target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
