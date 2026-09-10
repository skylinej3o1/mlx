# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest genuinely fresh search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-0601.md`

   **The 06:01 note is authoritative for fresh M5-Max Flash-Next cold-prefill/PLE-overlap evidence, two-Mac Metal fast-sync correctness, execution-shape-specific Flash decode/MTP/QSA work, K-only sparse-indexer memory, equal-total-token graph-address correctness, replay-boundary retention and benchmark-window provenance.**

4. Retain the source-correction/backfill delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-0016.md`

   **The 00:16 note fully incorporates the previously under-mined r/oMLX Flash-Next thread: realistic 120K/150K harness receipts, oQ5e memory/robustness evidence, MTPLX speed-versus-reliability evidence, 64-GB-class viability, conditional PLE/N-gram residency, runtime-engine deltas, and tokens-to-solution/task-wall-clock consequences. It is BACKFILL / USER RECEIPT / TRANSFER evidence and moves no target.**

5. Retain the immediately previous fresh runtime deltas:

   - `RESEARCH-WATCH-2026-09-09-2034.md` — DS4 selective-projection Q4 phase/shape behavior, fused sparse-index score/top-k/attend contracts, quant-format matrix-shape cliffs, direct-visible versus staged-copy control traffic, Blazer co-design implications;
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

# Freshness discipline

The 00:16 ET Reddit incorporation was a BACKFILL / SOURCE-CORRECTION and did not advance the prior boundary. The 06:01 ET pass is the next genuinely fresh search and covers sources after **2026-09-10 00:38:49 UTC**.

**Hard source-freshness boundary for the next external search: 2026-09-10 10:07:43 UTC.**

This is the end-of-search boundary, not the later repository-write timestamp. Future passes must search strictly after this source boundary; repository-only commits must never create a source-search gap.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 06:01 pass moves no row.**

Important Flash interpretation from the canonical target file:

- **40 tok/s** remains the B1 short/medium working target;
- the separate ~128K ladder remains the recorded **20 / 25 / 30 / 35 tok/s** confidence ladder;
- **400 tok/s** remains the realistic cold-prefill working target.

The fresh M5-Max 128K cold-prefill receipt strengthens the mechanism case for 400 PP, but it is not an M1-Max numeric transfer.

---

# Current newest fresh evidence — 2026-09-10 06:01 ET

## FRESH / oMLX #3534 — cold Flash-Next PP and SSD-PLE overlap

M5 Max 128 GB / `Qwen3.8-Flash-Next-oQ4e-mtp` / SSD PLE / MTP off:

- app-admin cold exact-N 16K: **1,165 -> 1,554 PP**;
- 64K: **1,219 -> 1,433 PP**;
- 128K: **1,243 -> 1,390 PP**;
- generation remains essentially unchanged at ~51 TG / ~46.5 TG for 64K / 128K.

Per-2048-token chunk work falls from ~1,817 -> 1,536 ms, with hyperconnection cost 250 -> 144 ms and PLE cost 248 -> 35 ms via compact selected-row upload plus lookahead gathering of the next PLE chunk while current GPU work executes.

**Promotion:** selected-row PLE compaction/overlap and hyperconnection PP work are first-class Flash seams. This is direct Apple/exact-model transfer evidence, not a dual-M1 rate receipt.

## FRESH / oMLX cluster — reliable Metal synchronization is a hard gate

Two-Mac TCP Ring / DS4-0731 stalled twice during 64K prefill with MLX fast Metal synchronization. Changing only `MLX_METAL_FAST_SYNCH=0` completed the same 65,536-token prompt + 128-token decode.

**Promotion:** default cluster bring-up to the reliable sync path, record the flag in provenance, and certify repeated long-context progress before measuring rates. Hardware generation was not established, so this is not an exact dual-M1 receipt.

## FRESH / oMLX #3553 — Flash decode/MTP optimization depends on exact row/context shape

M5 Max draft work on the exact Flash model shows:

- selected-KV gathered QSA decode: MTP gains up to **+6.8%** at a reported 134K rung;
- verify GDN fusion must preserve precise recurrent numerics; a tiny exp mismatch can fork output hundreds of tokens later;
- grouped quantized projections can help 2..8 verify rows while losing **1.6-2.4%** on single-row decode;
- keeping a parked MTP head primed can restore profitable long-context re-entry;
- 2..15-row gathered QSA at long context gives **+4.6% at 82K code**, with head-cycle time 3.4 -> 1.8 ms;
- prompt-lookup n-gram drafts (-10 to -20%), a proposed block-sparse prefill kernel (3.6x slower), and an MMA GDN prefill recurrence rewrite were measured negative/low-leverage.

**Promotion:** certify n=1 decode, 2..8 verify rows, 2..15 committed-head folds and large-M prefill as separate execution cells. Do not generalize a kernel win across phases.

## FRESH / llama.cpp #28330 — indexer cache memory is semantically K-only

The sparse indexer does not consume a V cache, so llama.cpp removes the unused allocation.

**Promotion:** memory/context accounting must inventory actual consumed QSA/indexer state rather than mechanically price K+V.

## FRESH / vLLM #56237 — capture identity includes row layout and buffer address

Two flattened speculative layouts can have the same total graph-token count while requiring different compressed sparse-indexer metadata. A captured graph retained an old address and consumed uncompressed context lengths after a layout transition `[2,2] -> [1,1,1,1]`. A stable-buffer ownership fix restores correct replay; the associated adaptive DS4 GSM8K result rises from severely broken accuracy to the fixed-K/no-spec range.

**Promotion:** same token count is not graph identity. Capture provenance includes row partition, query width, compression layout and backing-buffer identity.

## FRESH / vLLM #54713 — keep multiple valid replay boundaries

Block-aligned hybrid speculative prompts can require one boundary for an exact resend and another for a longer sibling. Retaining only the higher one can collapse exact-replay cache reuse.

**Promotion:** cache certification must cover exact resend, sibling append and MTP/recurrent restoration at aligned boundaries.

## FRESH / rMLX #554 — preserve rate provenance under host jitter

A client/engine rate cross-check was flaky under load because its wall-clock decode window was too short. rMLX keeps the 10% agreement band and widens the plain measurement window instead of relaxing the provenance rule.

**Promotion:** use sufficiently long decode windows and retain strict client/engine agreement; host jitter is not grounds to widen the acceptable identity band.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. reliable Metal sync as initial cluster baseline and provenance;
2. repeated 64K+ distributed completion before rate promotion;
3. selected-row PLE compaction + asynchronous next-chunk gather;
4. profile hyperconnection PP separately from PLE and attention;
5. separate n=1 / verify 2..8 / narrow-fold 2..15 / large-M prefill kernel cells;
6. captured QSA metadata identity includes actual row layout and buffer ownership;
7. semantic K-only indexer memory accounting where appropriate;
8. multiple replay boundaries for exact resend and sibling extension;
9. long-output recurrent parity after fused-kernel changes;
10. retain the 00:16 Q5/MTPLX/PLE-residency/task-efficiency backfill and all prior ownership/concurrency/quant/soak gates.

Safe serving remains **profitable singleton MTP + plain concurrent work** until concurrency/state-isolation gates are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. **P69B12 frozen/promoted; P69B13 remains next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the speed lane; host-backed/streamed long-context configurations remain a separate capacity lane.

## Dual-M1 DS4-0731

No target movement. The new two-Mac synchronization result changes the correctness gate, not the rate.

---

# Standing decisions strengthened

- Cold PP remains a large optimization surface even with SSD-backed PLE.
- PLE selected-row work should be compacted and overlapped rather than serialized.
- Distributed synchronization mode is part of benchmark identity.
- Flash kernels are phase/row/context specific.
- Same total token count does not prove captured graph-layout equivalence.
- Sparse indexer memory follows actual state consumption.
- Cache replay has more than one useful boundary under hybrid speculation.
- Recurrent numerical correctness must survive long downstream generation.
- Benchmark rate identity should be made robust with longer windows, not looser agreement bands.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**
