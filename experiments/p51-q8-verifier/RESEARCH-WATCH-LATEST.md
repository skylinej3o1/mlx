# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1813.md`

   **The 18:13 note is authoritative for the corrected extension-built oMLX #3520 long-context QSA matrix and width-dependent routing, fresh independent indexed split-K numerical/performance evidence, Affine4 long-context capacity evidence, and fresh DSv4/DSpark draft-loader/native-depth provenance. Its corrected #3520 matrix supersedes the quantitative #3520 figures in the 14:38 note. It moves no performance target.**

4. Retain the immediately previous deltas:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1438.md` — gathered-QSA mechanism promotion, short-prompt MTP paged-boundary admission fix and device-upload happens-before correction. **Its #3520 benchmark percentages are superseded by the 18:13 correction; the remaining findings stand.**
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1048.md` — landed Apple IQ3 small-width SIMD-utilization A/B, recurrent checkpoint-retention / warm-rewind fix, DFlash2 cumulative-OOB attribution correction and recovered M1-Max Qwen3.8-27B baseline;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0843.md` — landed oMLX distributed request-safety integration, rMLX bounded speculative capture / commit-scoped conditioning, hybrid recurrent+MTP mixed-phase ordering bug, deterministic-QSA TopK monitor, speculative backend-context placement cleanup and DGX-Spark MTP-depth backfill;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0238.md` — M5-Max Flash Q4_K routed-expert double-buffer/chunk-width A/B, cross-request MTP state ownership, distributed lifecycle review, QSA `top_k` provenance and ParoQuant/DFlash2 rollback-hook qualification;
   - retain the 2026-09-07, 2026-09-06 and 2026-09-05 watch deltas for GDN/projection structure, actual MTP depth, recurrent rollback/state geometry, QSA tie/order, scheduler occupancy, whole-round speculative economics, cache lifecycle, sampler ownership, request-row ownership and benchmark-provenance gates.

5. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain the dated deltas newer than that point when reconstructing the evidence chain.

6. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 18:13 pass moves no row.** No fresh sustained exact target-topology receipt was strong enough to change a planning distribution.

---

# Current newest evidence delta — 2026-09-08 18:13 ET

Starting freshness boundary: `5452dffc758ba3230ed627e514d06beaeec87d71` / **2026-09-08 18:47:28 UTC**.

## UPDATE / CORRECTION — oMLX #3520

The mechanism survives, but an earlier server chain is explicitly withdrawn because the native sparse-attention extension was not built and the fallback route overstated the branch by up to ~20 percentage points at 229K.

Current M5-Max 128GB / High-Power / Flash-Next-oQ4e-mtp comparison (`main` `b908f563` -> branch `9e19561b`), with native extensions built in both arms:

- **serial:** +7.5% @63K, +17.7% @134K, +28.1% @229K;
- **adaptive sampled MTP:** +8.5%, +25.4%, +36.1%;
- **adaptive greedy MTP:** +14.6%, +28.7%, +32.4%.

These replace the #3520 percentages in the 14:38 watch.

The revised branch also shows that QSA routing is strongly width-dependent on M5/NAX:

- selected-KV gather switches between token-major amortized copy and stored-layout take by query width/context;
- native indexer-score gate ~32 rows;
- native top-k gate ~8 rows;
- native sparse-GQA attention gate ~24 rows;
- ordinary MTP verify widths of 4–8 rows can be much faster on gathered SDPA than on the native sparse kernel.

**Promotion:** record extension/build availability, query/verify width, context, selected gather form, each native/fallback kernel route and fallback reason. A custom/native route is not presumed faster merely because it exists.

## FRESH — indexed split-K numerical/performance evidence

Independent M5-Max comment on #3520 reports an indexed split-K selected-KV attention path:

- isolated M=3 attention ~2.8x at 16K -> ~11x at 128K versus gather;
- M=1 crossover around 32–64K;
- end-to-end decode +11% @16K, +21% @32K, +42% @64K, digest-identical to the gather baseline.

A mathematically cleaner reduction still shifted a chosen-token logprob by ~0.06 at 16K and flipped a real verify transaction. Matching the deployed native arithmetic path was required for digest equality.

**Promotion:** custom sparse kernels require real-checkpoint transaction-level equivalence at the exact verify width and deployed MLX build; build hash, admission and silent fallback are benchmark provenance.

## UPDATE / optional long-context capacity lane — oMLX #3499 Affine4

M5 Pro 48GiB Qwen3.8-27B evidence includes:

- 150K: 291.9 PP / 12.3 TG;
- 200K: 250.0 PP / 11.8 TG;
- logical attention KV at 200K: 12.21 -> 3.71 GiB (-69.6%);
- separate Affine4 MTP probe: 16.9 -> 36.1 TG with Lightning MTP, 84/97 considered drafts accepted;
- a fresh third-party cherry-pick reports fitting 256K Qwen3.8-27B context, but without a controlled rate/quality receipt.

Affine4 is lossy and chunk-sensitive; keep it a separate optional capacity route pending exact quality/equivalence and MTP/restore certification. It does not alter the native/exact-runtime target.

## FRESH — DSv4 / DSpark loader provenance

A fresh 4x SM80 Vision-Exp DSv4 report with DSpark n=6 gives ~45 -> ~86 tok/s single-stream and ~138 -> ~229 aggregate. The portable finding is loader correctness:

- resolving `lm_head` from the outer VL wrapper returned `None`, silently leaving the draft head randomly initialized and acceptance near zero;
- Vision-Exp has `num_nextn_predict_layers=3`, so requested speculative depth must respect the exact checkpoint's native structure.

**Promotion:** explicitly bind/hash drafter head weights; record wrapper/inner-LM ownership, native MTP/NextN layer count and requested/resolved depth. Nonzero speculative execution is not proof of a valid drafter.

## BACKFILL / multi-session cache-group economics

vLLM #54661 shows a deployment where an EAGLE/DFlash sliding-window draft group dominated a shared prefix-cache pool despite not defining the useful target hit horizon. Per-group retention plus a constrained hit-min exemption recovered substantial multi-conversation capacity in a fork. Treat as mechanism evidence only: occupancy is recorded by semantic cache group, and any hit exemption must prove fresh-window recomputation and no stale draft state.

## SCREENED / no-change

- oMLX, rMLX, antirez/ds4, llama.cpp, Atlas, NInfer, vllm-mlx and TurboQuant-MLX: no post-cutoff main commit relevant to target rates.
- Rapid-MLX post-cutoff work is service/provider/audit work.
- oMLX #3372 closed as superseded by #3287; do not promote its title-level +18% prefill claim as fresh E2E evidence.
- vLLM post-cutoff main activity did not yield a stronger exact target receipt.
- no new controlled exact dual-M1 Flash/DS4, M1-Max64 27B or RTX5070Ti target-lane receipt surfaced.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Current ordering:

1. exact PP2 model/recurrent/QSA identity + distributed lifecycle;
2. cold PP with real chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase first speculative decode joining continuing chunked prefill;
4. speculative ownership / rollback / replay with one authoritative committed frontier;
5. bound verifier capture to the drafter-readable horizon;
6. admission-time paged-boundary alignment, including short-prompt first-boundary-during-decode;
7. recurrent checkpoint retention across branch/edit/retry/compaction/reopen;
8. rendered-history cacheability for preserved reasoning/tool calls, stream/nonstream parity;
9. native/default MTP whole-round baseline;
10. explicit drafter-head binding + native trained MTP/NextN count + requested/resolved depth;
11. workload-separated deeper-depth A/Bs + segmented long-generation acceptance/TG;
12. realized QSA route for draft, target decode and target verify;
13. extension/build/admission receipt before custom-route timing;
14. row/verify-width x context route matrix, including 1/2/4/8/16/24/32/64 rows;
15. selected-KV traffic/work accounting; no hidden dense materialization unless deliberately amortized and measured;
16. custom split-K only after exact-build real-checkpoint digest/equivalence;
17. serial / sampled-MTP / greedy-deeper threshold sweeps with short-context negative controls;
18. stage-local GDN/routed-MoE/projection/sync profiling + SIMD occupancy;
19. quant/kernel chunk-width sweep;
20. optional compressed-KV long-context lane only after quality/chunk-sensitivity/MTP/restore qualification;
21. multi-session cache occupancy by semantic group;
22. combine passing mechanisms, then rerun cluster cold PP, ~128K TG, append/live-prefix, branch/retry and coding-agent wall cells.

For PP2, selected K/V plus recurrent/QSA state remain stage-local. Sparse attention that turns into dense TB4 traffic fails the intended economics.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

> B2/B3/B4 means physically simultaneously scheduled independent requests with correct persistent state. Configured/admitted/batched/queued slots do not count; staggered mixed prefill/decode must remain correct.

## Single M1 Max64 Qwen3.8-27B

No target movement. Affine4 remains an optional long-context capacity route only.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt. Record actual kernel/source/build route, target/drafter placement, sampler path, driver/runtime identity and peak VRAM/context headroom; fallbacks must be visible.

## Dual-M1 DS4-0731

No target movement. Add explicit draft-head binding and native MTP/NextN-depth provenance. CUDA Vision-Exp rates do not transfer numerically to Apple text-0731.

---

# Standing decisions strengthened this pass

- Corrected production-route receipts supersede benchmark chains that exercised a different fallback path.
- Extension/build availability, admission and fallback identity are benchmark provenance.
- QSA/sparse routing depends on hardware + phase + query/verify width + context.
- Native custom kernels are not presumed faster at decode/MTP widths.
- Custom sparse-attention correctness is transaction-level and can depend on arithmetic-path identity.
- Verify width is a semantic and performance dimension.
- Drafter weights are explicitly bound/hashed; `spec enabled` is insufficient.
- Native trained MTP/NextN structure plus requested/resolved depth is mandatory provenance.
- Lossy KV compression is a separate capacity lane pending quality/chunk-sensitivity qualification.
- Cache capacity is measured by semantic group under multi-session load.
- Existing request ownership, device happens-before, mixed-phase recurrent ordering, grammar rollback, sampler ownership/fallback, fairness, cancellation/reuse/restart, quantized-hook, QSA selected-set/order and tape/refold gates remain active.
- Acceptance remains diagnostic; useful emitted tokens per wall-second is the objective.
- Cross-runtime/other-hardware gains remain mechanism evidence until exact target reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
