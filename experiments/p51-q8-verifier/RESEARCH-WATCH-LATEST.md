# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest genuinely fresh/update search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-0911.md`

   **The 09:11 note is authoritative for the completed oMLX #3553 Flash-Next bit-exact-vs-tolerance benchmark decomposition, equal-acceptance cycle-cost methodology, DeepSeek V4.1 Flash architecture/Engram implications, independently quantized MTP-head evidence, V4.1 quant-block/streamed-conversion requirements, and the current exact-target screening result.**

4. Retain the immediately previous genuinely fresh search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-0601.md`

   **The 06:01 note remains authoritative for M5-Max Flash-Next cold-prefill/PLE-overlap evidence, two-Mac Metal fast-sync correctness, initial execution-shape-specific Flash decode/MTP/QSA work, K-only sparse-indexer memory, equal-total-token graph-address correctness, replay-boundary retention and benchmark-window provenance.**

5. Retain the source-correction/backfill delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-10-0016.md`

   **The 00:16 note fully incorporates the previously under-mined r/oMLX Flash-Next thread: realistic 120K/150K harness receipts, oQ5e memory/robustness evidence, MTPLX speed-versus-reliability evidence, 64-GB-class viability, conditional PLE/N-gram residency, runtime-engine deltas, and tokens-to-solution/task-wall-clock consequences. It is BACKFILL / USER RECEIPT / TRANSFER evidence and moves no target.**

6. Retain the previous runtime deltas:

   - `RESEARCH-WATCH-2026-09-09-2034.md` — DS4 selective-projection Q4 phase/shape behavior, fused sparse-index score/top-k/attend contracts, quant-format matrix-shape cliffs, direct-visible versus staged-copy control traffic, Blazer co-design implications;
   - `RESEARCH-WATCH-2026-09-09-1752.md` — full-machine-residency benchmark provenance, PP speculative broadcast operand lifetime/device happens-before, rMLX single-source recurrent rollback/state construction, shared-KV read-only ownership;
   - `RESEARCH-WATCH-2026-09-09-1402.md` — Qwen3.8-Flash-Next UVA PLE offload / Engram parallelism, NVFP4 packed gathered top-k projection, backend dispatch-limit qualification;
   - `RESEARCH-WATCH-2026-09-09-0941.md` — rMLX request-record provenance, quantized-FA compiled-capability provenance, routed-MoE active-expert tile geometry;
   - `RESEARCH-WATCH-2026-09-09-0628.md` — exact RTX5070Ti IQ4_XS 256K capacity lane, Atlas concurrent-MTP ownership/counter regression, round/acceptance invariants, oMLX boundary materialization, vLLM mixed-concurrency/tail-ring/soak attribution;
   - retain 2026-09-08 and older dated deltas for remaining QSA, GDN/projection, recurrent rollback, cache lifecycle, concurrency and provenance evidence.

7. Also retain:

   `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md`

   as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

8. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

9. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Freshness discipline

The latest completed external search covers sources strictly after the prior boundary **2026-09-10 10:07:43 UTC** through the end of the current search.

**Hard source-freshness boundary for the next external search: 2026-09-10 13:23:11 UTC.**

This is the end-of-search boundary, not the later repository-write timestamp. Future passes must search strictly after this source boundary; repository-only commits must never create a source-search gap.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 09:11 pass moves no row.**

Important Flash interpretation from the canonical target file:

- **40 tok/s** remains the B1 short/medium working target;
- the separate ~128K ladder remains the recorded **20 / 25 / 30 / 35 tok/s** confidence ladder;
- **400 tok/s** remains the realistic cold-prefill working target.

No new exact dual-M1/TB4 receipt was found this pass.

---

# Current newest incorporated evidence — 2026-09-10 09:11 ET

## UPDATE / oMLX #3553 — completed Flash optimization decomposition

The post-cutoff update completes the benchmark analysis for M5 Max 128 GB / Flash-Next oQ4e / SSD PLE.

The important methodological result is that **wall-ms per speculative cycle and acceptance/continuation must be reported separately**. Tolerance-level QSA/indexer changes can flip near-tie routing, fork the greedy continuation and thereby alter acceptance and tokens/cycle without those changes being kernel speed.

Pinned depth-3 wall-cycle saving grows with context from roughly **1.2% at 16K** to **8.6% at 65K**, **12.8% at 136K** and **16.2% at 210K**.

A separate bit-exact/control-flow arm retains **57-100%** of the measured cycle saving across those cells, with equal-acceptance throughput gains of approximately **+1.2 / +6.0 / +10.0 / +14.1%** at 16K / 65K / 136K / 210K. The additional tolerance-level kernels add smaller incremental equal-acceptance gains while requiring a separate correctness lane.

**Promotion:**

- record wall-ms / verify cycle at equal acceptance;
- strict bit-exact lane versus tolerance-certified lane;
- never count continuation luck as kernel speed;
- tolerance QSA/indexer work needs teacher-forced NLL/logit/top-k/route drift plus task behavior;
- recurrent/GDN changes retain long-output parity;
- n=1, verify 2..8, narrow-fold 2..15 and large-M prefill remain distinct cells.

This is exact-model Apple transfer evidence on a stronger M5, not a dual-M1 numeric receipt.

## FRESH / vLLM #56228 — DeepSeek V4.1 Flash future architecture lane

Merged **2026-09-10 12:16:26 UTC**.

The implementation introduces first-class conditional Engram/n-gram memory with CPU/UVA-capable lookup and architecture-specific compressed-state handling. This strengthens the durable sparse/offload thesis but also demonstrates that V4.1 is a distinct architecture lane rather than a transparent DS4-0731 continuation.

**Promotion:** keep V4.1 as future architecture research until a runnable quant/offload artifact exists. Do not move the current DS4-0731 rate row from V4.1 architecture evidence alone.

## FRESH / vLLM #54574 — separate/quantized MTP LM head

Merged **2026-09-10 12:26:32 UTC**.

A separate W4A16 MTP LM head retains mean acceptance length very close to the shared/native-style external-MTP control in the reported cross-model accelerator test: roughly **4.31565 -> 4.28227**.

**Promotion for Blazer:** treat MTP-head precision as an independent quant variable. Sensitivity-map and certify the head separately and include draft-head quant/config identity in full execution provenance.

Different model/runtime/accelerator: transfer only, no Apple rate transfer.

## FRESH / llama.cpp #28696 — exact V4.1 quant metadata and streamed Engram conversion

Created **2026-09-10 10:23:42 UTC**, updated through at least **12:56:28 UTC** during the pass.

Key findings:

- V4.1 FP8 block geometry is `[32,32]`, not the inherited V4 `[128,128]`; the wrong inherited value can silently rescale dequantized weights.
- each of two Engram tables is reported as **384,006,168 x 256**;
- whole-table float32 dequant would require roughly **393 GB scratch per table**;
- conversion therefore streams row blocks into a disk-backed memmap;
- a full conversion on 121 GiB host RAM produced 1046 tensors and a **507.9 GB Q8_0** artifact with MXFP4 experts while adding under 8 GB peak host memory;
- the converted artifact still does **not** load in the inherited runtime because V4.1 lacks tensors that graph expects.

**Promotion:** exact quant block/group metadata is model identity; family defaults are unsafe. Giant conditional-memory components require streamed/offload-first conversion. Successful low-scratch conversion does not prove inference fit or speed.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. equal-acceptance wall-ms/cycle as a first-class speculative performance metric;
2. bit-exact and tolerance-level kernel lanes;
3. acceptance/continuation changes excluded from kernel-speed credit;
4. teacher-forced route/distribution drift for tolerance QSA/indexer changes;
5. long-output recurrent parity after GDN fusion;
6. n=1 / 2..8 verify / 2..15 narrow-fold / large-M prefill separate cells;
7. all 06:01 reliable-sync, PLE-overlap, graph-layout, cache-boundary and prior ownership/concurrency/soak gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until concurrency/state-isolation gates are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. **P69B12 frozen/promoted; P69B13 remains next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the speed lane; host-backed/mixed-GPU long-context configurations remain separate capacity lanes.

## Dual-M1 DS4-0731

No target movement. V4.1 is future architecture evidence, not an exact DS4-0731 benchmark receipt.

## Future custom 5.x-bit / Blazer

Add:

- independently quantized MTP head;
- exact per-artifact block/group metadata ingestion;
- streamed conversion for giant conditional-memory tables;
- bit-exact versus tolerance certification lanes;
- acceptance-by-depth and task-wall-clock in the objective.

---

# Standing decisions strengthened

- Kernel speed and speculative acceptance are separate observables.
- Equal-acceptance cycle cost is first-class for speculative optimization.
- Bit-exact improvements should be promoted independently of tolerance-level improvements.
- Tiny recurrent/indexer differences can fork long continuations.
- MTP-head precision need not equal backbone precision.
- Exact quant block/group metadata is part of model identity.
- Giant Engram/conditional-memory components should be streamed/offloaded rather than expanded whole.
- DeepSeek V4.1 Flash is a future architecture lane and does not redefine DS4-0731.
- Cross-runtime/cross-hardware evidence does not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
