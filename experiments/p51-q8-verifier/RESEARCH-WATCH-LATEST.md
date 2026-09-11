# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence definitions:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP target identity. Context is part of the target identity.**

3. Read the newest genuinely fresh/update search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-0026.md`

   **The 00:26 note is authoritative for fresh oMLX #3553 M3-Ultra machine-exclusive A/B and content-shape evidence, the stronger long-context M5 equal-acceptance / bit-exact decomposition, rMLX #558 population-relation gate hardening, vLLM heterogeneous-PP completion ownership, MTP ragged sparse-attention routing, deferred-free capacity semantics, and oMLX cluster-pairing recovery.**

4. Retain the immediately previous fresh search deltas:

   - `RESEARCH-WATCH-2026-09-10-1928.md` — concrete qwen4_exp TP2 control strategy, rMLX semantic-population charge/sampling gates, vLLM per-stream/capture split-K workspace ownership, forward-progress watchdog backfill;
   - `RESEARCH-WATCH-2026-09-10-1715.md` — rMLX shared-round-skeleton mutation gates, narrowed #3468 SSD expert-streaming classification, prompt-cache requested/planned/measured/effective semantics;
   - `RESEARCH-WATCH-2026-09-10-1414.md` — workload-shaped cache blocks, agent TTFT/task wall, sink-truth telemetry, packaged custom-kernel ABI, fast-prefill arming, UVA lifetime and hybrid distributed mapping;
   - `RESEARCH-WATCH-2026-09-10-0911.md` — bit-exact-vs-tolerance cycle decomposition, equal-acceptance methodology, quantized MTP-head evidence and conversion/quant-block requirements;
   - `RESEARCH-WATCH-2026-09-10-0601.md` — M5 Flash cold-prefill/PLE overlap, reliable two-Mac Metal synchronization, QSA/MTP shape work and graph-address/replay-boundary retention;
   - `RESEARCH-WATCH-2026-09-10-0016.md` — BACKFILL / SOURCE-CORRECTION for the under-mined r/oMLX Flash thread: 120K/150K harness receipts, oQ5e memory/robustness, MTPLX speed-vs-reliability, 64-GB viability, PLE/N-gram residency and task-wall consequences.

5. Retain the 2026-09-09 deltas for DS4 selective projection/quant-shape behavior, full-machine-residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram work, quantized-FA compiled capability, routed-MoE tile geometry, RTX5070Ti capacity evidence, Atlas concurrency ownership, oMLX replay boundaries and vLLM concurrency/soak attribution.

6. Also retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

7. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

8. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Freshness discipline

The latest completed external search covers sources strictly after **2026-09-10 23:28:08 UTC** through the end of the current search.

**Hard source-freshness boundary for the next external search: 2026-09-11 04:26:56 UTC.**

This is the end-of-search boundary, not a repository-write timestamp. Future passes must search strictly after this source boundary; repository-only commits must never create a source-search gap. Refreshed/rebased metadata does not make older benchmark execution fresh.

---

# Canonical target calibration — unchanged this pass

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Important Flash interpretation from the canonical target file:

- **40 tok/s sustained at ~128K active context** is the headline dual-M1 Flash working target;
- short/medium 30/35/40/45/50 is secondary bring-up calibration only;
- the old September 4 ~128K 20/25/30/35 ladder is historical evidence calibration, not the target;
- reaching ~40 only at short context while collapsing near 128K does **not** meet the system goal;
- **400 tok/s** remains the realistic cold-prefill target;
- 40 @ ~128K is a **planning target / hypothesis**, not a measured exact dual-M1/TB4 receipt.

The 00:26 search pass moves **no target**. Fresh Apple transfer evidence strengthens the long-context mechanism case but remains cross-hardware.

---

# Current newest incorporated evidence — 2026-09-11 00:26 ET

## FRESH / MATERIAL UPDATE — oMLX #3553 long-context decode levers and new Apple A/Bs

PR head `a04d2408183c130d24a968ed74732260eb55d0be`.

Two post-cutoff physical comments are fresh:

- **2026-09-11 02:46:46 UTC:** M3 Ultra 512 GB, machine-exclusive, all sibling engines stopped, physical tree-switch/restart between arms, 120 total requests. Decode medians main -> PR: 164.1 -> 164.5 @1K, 86.5 -> 86.9 @16K, 82.2 -> 82.8 @32K, **80.6 -> 81.5 @64K**. Baseline already includes #3520 + #3534, so #3553 is incremental rather than claiming the older gathered-QSA gain again.
- **2026-09-11 03:39:11 UTC:** same machine-exclusive methodology across prose/code/CJK-shaped prompts. Absolute long-context throughput varies materially by content shape, and 16K code is the one negative #3553 cell (**83.9 -> 80.1, -4.5%**) despite positive prose long-context cells.

The PR's M5 Max 128 GB body is an UPDATE / transfer record rather than fresh exact-target evidence. At pinned depth 3 the portable signal is the **equal-acceptance / bit-exact cycle decomposition**, not the raw client-TG delta on forked continuations:

- 16K: ~1.2% equal-acceptance bit-exact throughput gain;
- 65K: ~6.0%;
- **136K: ~10.0%**;
- 210K: ~14.1%.

Portable levers: fused GDN verify rows, grouped quantized verify projections, narrow gathered-QSA windows for MTP-head folds and parked-head priming. Tolerance-level selected-KV/indexer kernels are kept separate because near-tie route changes can alter acceptance and continuation.

A critical recurrent-exactness result: a precise-vs-fast exponential difference at one BF16 gate input shifted GDN recurrent state by an FP32 ulp and could fork greedy output much later. Math-library/compiler semantics therefore belong in recurrent-kernel provenance.

**Promotions:**

1. separate client TG from equal-work/equal-acceptance cycle cost when an optimization can change the continuation;
2. certify actual MTP verify-row widths, not only single-row decode;
3. grouped projections are verify-row candidates, not automatically B1 wins;
4. preserve/prime MTP-head state across parked standard decode;
5. include code, prose and multilingual/CJK-shaped workloads in long-context qualification;
6. keep resident sibling engines / keepwarm state in benchmark provenance;
7. carry measured negatives forward to avoid duplicate low-leverage exploration unless M1 profiling shows a different bottleneck.

This strengthens the plausibility of maintaining high TG near ~128K but **does not numerically transfer M5/M3 rates to M1 Max**.

## FRESH / rMLX #558 — cross-population invariants catch a lost loop that counts alone miss

`3ded8892c5f07918dd8a43aa09972fb744766cc4`, **2026-09-11 01:27:34 UTC**.

A bodiless trait declaration could cause the scanner to consume the following function body, losing a round loop while a newly added entry kept the total census looking plausible. The fix terminates bodiless declarations correctly and requires every forwarding entry to have a forwarded loop to enter.

**Promotion:** provenance gates need relational invariants across entries/routes/loops, not only matching counts. A `lost X + gained Y` defect can preserve the total.

## FRESH / vLLM #56033 — heterogeneous PP completion includes no-op consumer stages

`ce08bb5b3463fd423be90d5f22c2b41142834bf6`, **2026-09-11 02:57:19 UTC**.

For producer/consumer PP sizes that differ, a consumer stage with no overlapping layer still owns a completion dependency. The producer now retains KV until every consumer PP stage, including no-op pulls, finishes.

**Promotion:** PP lifetime/release accounting follows topology participants, not only stages that transferred bytes.

## FRESH / vLLM #55239 — ragged sparse attention can cover MTP verify rows

`828f4f19b4d8ea6a97a047409a90b563d166002f`, **2026-09-11 01:13:14 UTC**.

The GLM-5.3-Flash sparse Triton route now admits multi-token speculative verification because the kernel indexes metadata per query token. Tests cover 2-row and 6-row MTP verification.

**Promotion:** QSA/sparse-attention eligibility should be derived from actual per-query-row capability; verify width must not silently force a dense fallback when the sparse kernel supports it.

## FRESH / vLLM #49675 — deferred free is not immediately reusable capacity

`84030bbe3d74d99bad477a3d2e37a973ccd8865c`, **2026-09-11 00:40:10 UTC**.

Under overlapping batches/PP, in-flight output can fence KV blocks. Preempting that request cannot satisfy an immediate allocation and can trigger a zero-progress cascade. The scheduler now checks whether the victim's blocks can actually be returned before using it as an allocation victim.

**Promotion:** logical retirement/preemption and physically reusable memory/state are separate facts.

## FRESH / oMLX #3565 — cluster pairing recovery

`48951154c06c5db408ee40ad6533c3a65ab061e7`, **2026-09-11 03:27:20 UTC**.

Pairing sessions persist across joiner restart; cancellation retires the local generation even while remote cleanup is pending; delayed responses cannot resurrect the retired join.

Operationally useful for eventual two-Mac serving, but **no throughput implication**.

---

# Screened / no target movement

- llama.cpp main: no inspected commit after the starting cutoff.
- antirez/ds4 main: no post-cutoff main commit.
- no new exact 2x M1 Max64/TB4 Flash-Next sustained TG/PP receipt;
- no new canonical one-M1-Max64 Qwen3.8-27B target receipt after the cutoff;
- no new fully-resident Q3_K_XL/native-MTP RTX5070Ti16 canonical speed receipt after the cutoff;
- no new exact 2x M1 Max64/TB4 DS4-0731 sustained decode receipt;
- broad web results that were older, undated or merely crawled today were not promoted as fresh evidence.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as concrete control.

Add/strengthen:

1. headline target remains **40 TG @ ~128K active context**;
2. selected-K/V gathered QSA should cover B1 decode, target verify rows and narrow MTP-head committed folds when legal;
3. GDN verify-row kernels require precise reference-math semantics plus recurrent-state and long-continuation certification;
4. grouped quantized projections are tested specifically at verify-row widths;
5. parked MTP-head state should remain primed through plain-decode intervals;
6. client TG and equal-acceptance cycle cost stay separate when route tolerance can fork text;
7. long-context matrix includes code/prose/multilingual-CJK content shapes;
8. no-op PP stages still participate in completion/lifetime accounting;
9. deferred release is not reusable capacity until its fence completes;
10. machine-residency/sibling-engine state remains benchmark provenance;
11. all prior concurrent-state/workspace/rollback/cache-boundary/forward-progress/long-soak gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until simultaneous B2/B3/B4 state/workspace isolation is certified.

## Future Blazer / ~5.x BPW

Add exact verify-row geometry, quant-signature grouping, sparse selected-row/narrow-fold compatibility and math-implementation identity to the execution descriptor. Optimize quality + difficult-tail robustness + acceptance + equal-work cycle cost + TG + PP + memory + usable context + PP balance, not BPW alone.

## Single M1 Max64 Qwen3.8-27B

No target movement. **P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed IQ4_XS remains a separate capacity lane.

## Dual-M1 DS4-0731

No target movement. No fresh exact dual-M1 rate receipt.

---

# Standing decisions strengthened

- 40 TG @ ~128K remains the actual Flash headline objective.
- Context and content shape are part of performance-cell identity.
- Client TG on a changed continuation is not a pure kernel multiplier.
- Recurrent exactness includes precise-vs-fast math semantics.
- Sparse attention must qualify the actual MTP verify/narrow-window shapes.
- PP completion counts no-op participants that own a lifetime dependency.
- Deferred release is not reusable capacity until completion is physically established.
- Provenance gates need cross-population relations, not only census totals.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**