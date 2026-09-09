# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-09-0941.md`

   **The 09:41 note is authoritative for the fresh rMLX #552 speculative-record/provenance consolidation, llama.cpp quantized-Flash-Attention compiled-capability provenance, routed-MoE active-expert tile-shape mechanism, and the post-10:36:27 UTC no-target-move screening pass. It moves no canonical performance target.**

4. Retain the immediately previous delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-09-0628.md`

   **The 06:28 note remains authoritative for the exact RTX5070Ti IQ4_XS 256K hot/cold-KV capacity runtime, Atlas concurrency-only MTP ownership/counter regression, rMLX #549/#550 single-source speculative round/acceptance invariants, the M3-Ultra #3520 reproduction and dense-vs-gathered non-equivalence, oMLX recurrent-boundary materialization failure, and vLLM mixed-concurrency/tail-ring/long-soak fault attribution.**

5. Retain the 2026-09-08 deltas in order as needed:

   - `RESEARCH-WATCH-2026-09-08-1813.md` — corrected extension-built oMLX #3520 matrix, width-dependent QSA routing, indexed split-K evidence, Affine4 capacity lane and DSv4/DSpark drafter-depth provenance;
   - `RESEARCH-WATCH-2026-09-08-1438.md` — gathered-QSA mechanism, MTP paged-boundary admission and upload happens-before;
   - `RESEARCH-WATCH-2026-09-08-1048.md` — Apple IQ3 small-width SIMD A/B, recurrent checkpoint retention, cumulative-OOB attribution and recovered M1-Max 27B baseline;
   - `RESEARCH-WATCH-2026-09-08-0843.md` — distributed lifecycle, bounded verifier capture, mixed-phase recurrent/MTP ordering, QSA monitor and backend-context provenance;
   - older dated deltas remain part of the evidence chain for rollback, cache lifecycle, concurrency, sampler ownership and benchmark provenance.

6. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain dated deltas newer than that point when reconstructing the evidence chain.

7. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 09:41 pass moves no row.** The RTX 5070 Ti speed target remains the fully-resident Q3_K_XL/native-MTP lane; the 06:28 IQ4_XS host-backed 256K result remains a separate long-context capacity lane.

---

# Current newest evidence delta — 2026-09-09 09:41 ET

Starting canonical head: `1f5e7fa881be71772f9ddd30ebe5a7fd49e7b3ca`.

Starting hard freshness boundary: **2026-09-09 10:36:27 UTC**.

## FRESH / rMLX #552 — one speculative request-record mapping

`0b2a15232124bd961c8423e2ba539a7b7e027b33` at **2026-09-09 13:21:09 UTC** centralizes speculative request-record construction, seed/bonus emission and verifier-resident-KV reporting.

The phase-charge decision intentionally stays at the round loop that owns rollback; the shared mapping destructures `RoundTotals` so an unmapped new field becomes a compile failure. Timing/rate fields gain non-vacuous source tests, and a new gate refuses charge decisions that cannot be tied to the loop that ordered them.

**Promotion:** one authoritative request-record mapping for draft/accept/phase/timing/KV fields; keep semantic ownership decisions attributable to their loop; drive every telemetry field with a fixture capable of distinguishing the intended source from a plausible wrong one; explicitly certify early-exit telemetry population.

## FRESH / llama.cpp #28079 — compiled quantized-FA capability is provenance

`5a4d0fecae272c9caf0b32eb384fa6a58dddb560` at **2026-09-09 10:50:08 UTC** replaces the broad all-quant Flash-Attention build switch with configurable quantized-FA combinations and adds runtime warning/fallback for an uncompiled combination.

The relevant Qwen3.8-27B fallback measurement predates this cutoff, so it remains **KNOWN/context**, not fresh. Its mechanism is still load-bearing: requesting FA with a KV quant combination absent from the build can benchmark a fallback path rather than the intended kernel.

**Promotion:** route provenance is now explicitly `requested -> configured -> compiled -> armed/admitted -> executed`. Record build/kernel-set hash, compiled dtype/quant/width capability, admission/fallback reason and actual executed backend. A fallback path never defines the intended cell merely because the flag requested it.

## FRESH / llama.cpp #28552 — routed-MoE N tiles follow active expert width

`d4abd573f6a360201799072384ceec6170fdb60c` at **2026-09-09 11:25:54 UTC** chooses routed-MoE quantized-MMQ N tiling from host-side typical expert width rather than a generic dense shape assumption.

**Promotion:** Apple routed-MoE kernel mining should derive candidate tile geometry from real active-expert M/N/K and verify-width shapes, profile routed vs dense/shared projections separately, and require exact-M1 measurement before numeric promotion.

## SCREENED / no target move

- oMLX main: no post-cutoff main commit; #3539 has no fresh material comment; #3520's latest reproduction remains in the 06:28 note.
- Atlas: no post-cutoff commit; `fdc912b...` remains the previous watch's evidence.
- TurboQuant-MLX, Rapid-MLX, NInfer and antirez/ds4: no post-cutoff target evidence.
- llama.cpp issue #28648 had a post-cutoff `updated_at` but a pre-cutoff substantive body and no retrievable material post-cutoff comment; **updated_at alone is not fresh evidence**.
- vLLM post-cutoff main activity produced no stronger exact target-lane rate.
- exact-rig searches found no new post-cutoff dual-M1 Flash/DS4, single-M1 mature 27B, or fully-resident Q3_K_XL RTX5070Ti receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. compiled-capability identity for every quantized QSA/FA/custom-kernel cell;
2. `requested/configured/compiled/armed-or-admitted/executed` provenance;
3. one authoritative speculative request-record mapping with discriminating tests for phase/timing/rate/KV fields;
4. an explicit telemetry-population contract for early speculative exits;
5. routed-MoE tile geometry derived from measured active-expert shape rather than dense defaults.

All 06:28 gates remain: distributed identity/lifecycle, stage-local recurrent/QSA state, mixed-phase ordering, one committed frontier, proposal+bonus acceptance shape, B2 admission interleaving, actual boundary materialization/restart reuse, device happens-before, dense-vs-gathered equivalence separation, custom route/build/admission provenance, mixed-long/short and equal-short stress, long soak, and no accidental dense TB4 materialization.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot state isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Keep fully-resident Q3_K_XL/native-MTP as the speed lane and IQ4_XS host-backed hot/cold-KV as the separate long-context capacity lane.

## Dual-M1 DS4-0731

No target movement.

---

# Standing decisions strengthened this pass

- Evidence freshness follows the timestamp of substantive evidence, not a later issue `updated_at`.
- Requested/configured is insufficient: compiled capability and actual executed route are benchmark facts.
- Build/kernel-set identity is first-class provenance for quantized attention and custom-kernel cells.
- Speculative telemetry is part of correctness and needs one authoritative mapping plus non-vacuous source tests.
- Centralize record mapping without obscuring which loop owns the semantic decision/rollback.
- Routed-MoE launch geometry follows the active expert shape and is target-backend-specific.
- Cross-runtime/cross-hardware mechanisms do not move target rates without exact target-lane reproduction.
- No canonical target movement this pass.
- P69 remains isolated.
