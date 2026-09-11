# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence definitions:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP target identity. Context is part of the target identity.**

3. Read the newest genuinely fresh complete search delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-0026.md`

   This remains authoritative for the latest full post-cutoff pass: oMLX #3553 M3-Ultra machine-exclusive A/B and content-shape evidence, M5 long-context equal-acceptance decomposition, rMLX #558 gate hardening, vLLM heterogeneous-PP completion ownership, MTP ragged sparse routing, deferred-free capacity semantics and oMLX cluster recovery.

4. Then read the newest **source-specific mining note**:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md`

   This note mines the mlx-serve Qwen3.8-Flash-Next 1M-context release and its mixed 4/8-bit model pack. It is **TRANSFER / MECHANISM / USER-DEVELOPER RECEIPT**, not an exact dual-M1 receipt and not a complete external-search pass.

5. Retain the immediately previous dated deltas:

   - `RESEARCH-WATCH-2026-09-10-1928.md` — qwen4_exp TP2 control strategy, rMLX semantic-population gates, vLLM workspace ownership;
   - `RESEARCH-WATCH-2026-09-10-1715.md` — shared-round-skeleton mutation gates, narrowed #3468 SSD streaming classification;
   - `RESEARCH-WATCH-2026-09-10-1414.md` — workload-shaped cache blocks, task wall-clock, sink-truth telemetry, packaged custom-kernel ABI, UVA lifetime;
   - `RESEARCH-WATCH-2026-09-10-0911.md` — bit-exact-vs-tolerance cycle decomposition, equal-acceptance methodology, quantized MTP-head evidence;
   - `RESEARCH-WATCH-2026-09-10-0601.md` — Flash cold-prefill/PLE overlap, two-Mac Metal synchronization, QSA/MTP shape work;
   - `RESEARCH-WATCH-2026-09-10-0016.md` — BACKFILL / SOURCE-CORRECTION for the under-mined r/oMLX Flash thread: 120K/150K harness receipts, oQ5e robustness, MTPLX speed-vs-reliability, 64-GB viability and PLE residency.

6. Retain the 2026-09-09 deltas for DS4 selective projection/quant-shape behavior, full-machine-residency provenance, PP speculative ownership, recurrent rollback, UVA PLE/Engram work, quantized-FA compiled capability, routed-MoE tile geometry, RTX5070Ti capacity evidence, Atlas concurrency ownership, replay boundaries and concurrency/soak attribution.

7. Also retain `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md` as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

8. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

9. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Freshness discipline

The latest **complete external search pass** ended at:

**Hard source-freshness boundary for the next external search: 2026-09-11 04:26:56 UTC.**

The mlx-serve 1M note was a **source-specific mining/update**, so it deliberately does **not** advance this global boundary. Future full passes must still search strictly after `2026-09-11 04:26:56 UTC` across all watched lanes.

Repository-only commits and source-specific mining must never create a source-search gap.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Flash interpretation remains explicit:

- **40 tok/s sustained at ~128K active context** is the headline dual-M1 Flash objective;
- short/medium TG ladders are bring-up calibration only;
- the old September 4 ~128K 20/25/30/35 ladder is historical evidence calibration, not the target;
- 40 only at short context while collapsing near 128K does **not** meet the goal;
- **400 tok/s** remains the realistic cold-prefill objective;
- 40 @ ~128K is a planning target / hypothesis, not a measured exact dual-M1/TB4 receipt.

The mlx-serve 1M evidence strengthens the architecture case but **moves no exact-target number**.

---

# Newest source-specific incorporation — mlx-serve 1M Flash-Next

Primary note:

`RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md`

Primary public sources:

- Reddit release thread: `r/LocalLLaMA` — Qwen3.8-Flash-Next on mlx-serve, 1M context;
- `ddalcu/mlx-serve`;
- `ddalcu/Qwen3.8-Flash-Next-MLX-Serve-mixed-4-8bit` model card.

## Transfer receipt

The release author reports on **M5 Max 128 GB**, 8-bit KV and one-concurrency serving:

- ~**40 tok/s prose at ~1M context**;
- ~**75 tok/s coding at ~1M context**;
- temperature 1.0 deep-context work rather than only short greedy microbenchmarks;
- ~117 GB peak memory at full 1M.

The same thread reports an approximate context curve of 100+ TG through ~16K, 80+ through ~256K, ~60 around 500K and ~40 around 1M, with prefill ~1700-1800 early and near ~1000 approaching 1M.

These are **stronger-Apple transfer receipts only**. They do not numerically transfer to M1 Max/TB4.

## Mixed-precision pack — important Blazer implication

The published pack is roughly **75 GB resident before KV** and assigns:

- routed experts (~121B parameters): **4-bit**;
- attention, GDN, hyper-connections, QSA indexer, shared experts and LM head: **8-bit**;
- routers, inject gates, norms, convs and SSM state: **BF16**;
- MTP head: same policy as trunk;
- n-gram table: separate **4-bit** sparse lookup plane.

This does **not** prove generic Q4 has Q5/Q6 quality. It does prove that a serious high-quality Flash pack can allocate precision extremely asymmetrically.

### Blazer candidate family expanded

Do not constrain eventual ~5.x-BPW work to “mostly Q5 + selected Q6/Q8.” Maintain at least three candidate families:

1. **Q5-dominant** — bulk Q5, sensitive Q6/Q8/BF16, proven-insensitive Q4;
2. **expert-aggressive** — routed experts Q4-ish while control/state/shared/QSA/MTP tensors stay Q6/Q8/BF16;
3. **sensitivity-optimized mixed 5.x** — tensor/layer-specific Q4/Q5/Q6/Q8 from the representative coding/tool/reasoning corpus.

Judge candidates by task success + difficult-tail robustness + MTP acceptance + task wall-clock + TG/PP + memory/context + PP balance, not by nominal BPW alone.

## PLE / n-gram architecture strengthened

The model card stores the 51B n-gram table as a separate **32 GB 4-bit mmap-backed file**. Per token only 16 rows are fetched/dequantized and one 2560-vector is uploaded; the whole table is not resident.

Therefore treat n-gram/PLE as a separate sparse lookup plane with explicit policies:

- SSD/page-cache backed;
- fully resident when memory permits;
- hot-resident/cold-SSD hybrid;
- PP-stage-local ownership;
- explicit prefetch/coalescing only when profiling supports it.

This complements, rather than contradicts, earlier oMLX evidence that roomy 128-GB systems can be faster with resident PLE. Residency policy is hardware/memory-pressure dependent.

## Long-context system consequences

The mlx-serve result strengthens the existing thesis that Flash-Next long-context degradation is governed increasingly by QSA selection/gather, recurrent/state handling, MTP verification, cache/KV policy and memory pressure rather than dense attention over every historical token.

Keep separate long-context qualification cells for:

- code/editing/agent loops;
- English prose;
- multilingual/CJK;
- tool-call-heavy work;
- deliberately low-acceptance / novel-content controls.

Warm prefix-cache / recurrent-checkpoint operation must stay separate from cold PP.

The 1M example's prefix cache and SSM-checkpoint settings also reinforce the intended local-agent system design:

> **stable repo brain/prefix -> cached -> selectively append task-local context -> retain recurrent checkpoints -> avoid repeatedly cold-ingesting giant contexts.**

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control.

Standing additions now include:

1. headline target remains **40 TG @ ~128K active context**;
2. selected-K/V gathered QSA must cover B1, target verify rows and legal narrow MTP-head folds;
3. GDN/recurrent kernels require precise reference-math semantics plus long-continuation certification;
4. grouped quantized projections are verify-row candidates, not assumed B1 wins;
5. parked MTP-head state should remain primed through plain-decode intervals;
6. client TG and equal-acceptance cycle cost stay separate when route tolerance can fork text;
7. long-context matrix includes code/prose/multilingual-CJK/tool/low-acceptance shapes;
8. no-op PP stages still participate in completion/lifetime accounting;
9. deferred release is not reusable capacity until its fence completes;
10. resident sibling engines / keepwarm state remain benchmark provenance;
11. PLE residency policy is explicit and measured;
12. mixed-precision expert-vs-control variants are part of future quant certification;
13. all prior concurrent-state/workspace/rollback/cache-boundary/forward-progress/long-soak gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until simultaneous B2/B3/B4 recurrent/spec state and workspace isolation are certified.

## Future Blazer / ~5.x BPW

Execution identity now includes:

- per-tensor precision class;
- routed-vs-shared expert distinction;
- QSA indexer precision;
- recurrent/control precision;
- MTP-head precision;
- packing/group geometry;
- actual verify-row geometry;
- sparse selected-row/narrow-fold compatibility;
- math implementation identity.

The destination remains a quality-preserving ~5.x-BPW-class operating point, but **the route to it is now explicitly open to Q4-ish expert bulk with much higher-precision control/state tensors**.

## Single M1 Max64 Qwen3.8-27B

No target movement. **P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed IQ4_XS remains separate capacity evidence.

## Dual-M1 DS4-0731

No target movement. No fresh exact dual-M1 rate receipt from this source-specific update.

---

# Standing decisions

- **40 TG @ ~128K remains the actual Flash headline objective.**
- **400 PP remains the cold-prefill objective.**
- The mlx-serve 1M result is strong architectural validation, not exact dual-M1 proof.
- Blazer candidate search now explicitly includes **Q4-ish routed experts + high-precision control/state** as a first-class family.
- PLE/n-gram remains a separately managed sparse lookup plane, not assumed resident model bulk.
- Context **and content shape** are part of performance-cell identity.
- Client TG on a changed continuation is not a pure kernel multiplier.
- Recurrent exactness includes precise-vs-fast math semantics.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- The global hard source-search cutoff remains **2026-09-11 04:26:56 UTC**.
- **P69 remains isolated.**
