# External runtime watch — 2026-09-09 09:41 ET

Starting canonical head: `1f5e7fa881be71772f9ddd30ebe5a7fd49e7b3ca`

Starting hard source-freshness cutoff: **2026-09-09 10:36:27 UTC**.

Canonical target blob at start: `e91ed103bd85ff1db36d1d1d61675d02b1b3d3fb`.

## Executive summary

This pass found **fresh speculative-accounting/provenance evidence in rMLX** and **fresh backend-capability / routed-MoE launch-shape evidence in llama.cpp**. It found **no fresh exact target-lane performance receipt** for dual-M1 Flash-Next, single-M1 Qwen3.8-27B, the fully-resident Q3_K_XL RTX 5070 Ti lane, or dual-M1 DS4-0731.

Therefore:

- **no canonical TG / PP target moves**;
- **P69 remains untouched and isolated**;
- strengthen benchmark provenance from `requested/configured/armed/executed` to include **compiled capability** explicitly;
- keep speculative work-accounting fields under the same single-source discipline as round width, rollback targets and acceptance;
- keep routed-MoE tile/launch geometry driven by the actual active expert shape rather than generic dense defaults, but transfer no AMD/CUDA rate to Apple targets.

---

## FRESH — rMLX #552: one speculative record assembly and one provenance seam

Commit:

`0b2a15232124bd961c8423e2ba539a7b7e027b33`

Timestamp: **2026-09-09 13:21:09 UTC**.

Title: `spec(refactor): one record assembly, one seed emit, one resident-KV report (#552)`.

This continues the #549/#550 consolidation from the previous watch. The nine per-loop `RoundStats` constructions are replaced by a single `RoundTotals` mapping through `round_common::log_request_record`; sidecar loops share one seed/bonus emit path, and the seven verifier-resident-KV reports share one producer.

Important correctness/provenance properties:

- the **phase-charge decision remains at each round loop's own call site**, beside the rollback semantics it controls;
- `RoundTotals` is destructured when converted to the persistent record, so adding a field without mapping it becomes a compile-time failure rather than a silently omitted measurement;
- the gate explicitly refuses a `charged:` decision written somewhere that cannot be held to the loop that performed the rollback;
- `elapsed_ns` is now tested against the actual clock read rather than an unrelated phase counter;
- decode TPS is driven with a non-empty rate window rather than a fixture that could only return `None`;
- the seed-EOS early-exit path deliberately remains outside the resident-KV report and the source states that this exit/report rule is not yet mechanically enforced.

### Promotion

For our speculative certification, extend the existing single-source rule:

1. one authoritative round width / rollback target / phase-charge decision;
2. one authoritative proposal/acceptance accounting walk;
3. **one authoritative request-record mapping** for draft, accept, phase, timing and resident-KV fields;
4. the charge token must remain attributable to the exact loop that ordered rollback — do not centralize the decision merely to deduplicate syntax;
5. a record field is not certified merely because it exists: drive it with a non-vacuous fixture that can distinguish the intended source from a plausible wrong source;
6. early-exit paths need an explicit record/report contract so a later report insertion cannot silently change the population represented by telemetry.

This is mechanism/provenance evidence only. It moves no target rate.

---

## FRESH — llama.cpp #28079: quantized Flash Attention has a compiled-capability state

Commit:

`5a4d0fecae272c9caf0b32eb384fa6a58dddb560`

Timestamp: **2026-09-09 10:50:08 UTC**.

Title: `CUDA: replace GGML_FA_ALL_QUANTS with GGML_FA_QUANTS, more control over what is compiled (#28079)`.

The change makes the set of quantized Flash-Attention combinations compiled into a build explicitly configurable and adds a runtime fallback warning for an uncompiled combination.

The relevant precursor evidence is issue #28633, created before this pass's cutoff, so its measured numbers remain **KNOWN/context rather than FRESH**: on RTX 3090 / Qwen3.8-27B, requesting Q4_0 KV + Flash Attention from a build that lacked the corresponding quantized-FA support could execute a fallback path and produce a very large long-prompt PP collapse; recompiling with the required quantized FA support restored the intended GPU path.

### Promotion

Our benchmark route provenance is now explicitly:

`requested -> configured -> compiled -> armed/admitted -> executed`

where applicable.

For any custom QSA/FA/quant kernel cell, record:

- exact build / kernel-set hash;
- whether the requested dtype/quant/width combination was compiled;
- admission decision and fallback reason;
- the backend/kernel that actually executed.

A fallback cell cannot define the performance of the intended route simply because the CLI/config requested it. Prefer fail-closed behavior for certification; if production permits fallback, make it visible and separately labelled.

This is CUDA mechanism evidence only. It moves neither the Apple targets nor the canonical fully-resident RTX 5070 Ti Q3_K_XL target.

---

## FRESH — llama.cpp #28552: routed-MoE MMQ tiling should follow active expert width

Commit:

`d4abd573f6a360201799072384ceec6170fdb60c`

Timestamp: **2026-09-09 11:25:54 UTC**.

Title: `CUDA: size routed MoE MMQ N-tiles from typical expert width on RDNA3 (#28552)`.

The host-side path now selects the quantized MMQ N tile against `ncols_opt`, i.e. the typical routed-expert output width, rather than relying on a generic dense-oriented shape assumption.

### Promotion

For our Apple routed-MoE profiling/mining:

- derive candidate tile geometry from the **actual active expert N/K/M shape** and verify-width population;
- do not assume the dense-path optimum transfers to routed experts;
- profile stage-local routed projections separately from dense/shared-expert projections;
- retain exact-M1 measurement as the only basis for Apple numeric promotion.

No numeric transfer from RDNA3/CUDA and no target move.

---

## SCREENED / no target change

### oMLX

- No post-cutoff main commit.
- #3539 recurrent-boundary materialization failure has no fresh comment beyond the previous watch.
- #3520's latest M3-Ultra QSA reproduction remains the previous watch's evidence.
- #3534 Flash-Next prefill optimization and #3533 ragged fused-MTP measurements predate the cutoff and remain **KNOWN**, not fresh.

### Atlas

Latest relevant main commit remains `fdc912b108ccf7f83dc5283e75b44148f87e15a5` at 2026-09-09 02:34:17 UTC, already captured in the 06:28 watch. No post-cutoff Atlas commit.

### TurboQuant-MLX / Rapid-MLX / NInfer / antirez-ds4

- TurboQuant-MLX: no post-cutoff commit.
- Rapid-MLX: no post-cutoff target evidence.
- NInfer latest screened commit is pre-cutoff.
- antirez/ds4: no post-cutoff main commit.

### llama.cpp issue timestamp trap

Issue #28648 shows a post-cutoff `updated_at`, but its substantive body was created **2026-09-09 09:35:30 UTC**, before the cutoff, and no material post-cutoff comment was retrievable. Treating `updated_at` alone as fresh evidence would violate the evidence-timestamp rule. Screened only.

### vLLM / exact-rig search

Post-cutoff vLLM main activity did not provide a stronger exact target-lane rate. Fresh web/exact-rig searches found no new post-cutoff receipt for:

- 2x M1 Max 64 GB / TB4 Flash-Next;
- 2x M1 Max 64 GB / TB4 DS4-0731;
- one M1 Max 64 GB mature Qwen3.8-27B native/exact-runtime lane;
- RTX 5070 Ti 16 GB **fully-resident Q3_K_XL/native-MTP** speed lane.

Recovered M1-Max and RTX receipts in search remain pre-cutoff/known calibration and do not move targets.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2 / layer ownership primary, TP2 control**.

Add/strengthen the following certification items:

1. compiled-capability identity for every custom quantized QSA/FA/kernel route;
2. `requested/configured/compiled/armed-or-admitted/executed` provenance;
3. one authoritative speculative request-record mapping, with non-vacuous source tests for timing/rate/phase/KV fields;
4. early speculative exits have an explicit telemetry-population contract;
5. routed-MoE tile geometry is profiled from real active expert shapes, not copied from dense defaults.

All previous 06:28 gates remain in force: request/state ownership, device happens-before, mixed-phase ordering, one committed frontier, boundary materialization/restart reuse, round-width/rollback/phase-charge consistency, proposal+bonus acceptance shape, B2 admission interleaving, QSA route identity, dense-vs-gathered equivalence separation, long-soak robustness, stage-local state and no accidental dense TB4 materialization.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next only from existing measured high-leverage GDN/projection/downstream-tail profiling.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Keep:

- canonical speed lane = fully-resident Q3_K_XL/native MTP;
- separate IQ4_XS host-backed long-context capacity lane from the 06:28 watch.

The fresh quantized-FA build change strengthens route/build provenance but is not a new 5070 Ti speed receipt.

## Dual-M1 DS4-0731

No target movement.

---

# Standing decisions strengthened this pass

- Evidence freshness follows the timestamp of the substantive evidence, not a later issue `updated_at`.
- A requested backend feature is not a benchmark fact until its compiled capability and actual execution route are known.
- Build capability is a first-class provenance dimension for quantized attention/custom-kernel cells.
- Speculative telemetry is part of correctness: phase, timing, rate and resident-KV mappings need one producer and discriminating tests.
- Deduplicating a semantic decision away from the loop that owns its rollback can reduce auditability; centralize mapping, not ownership meaning.
- Routed-MoE launch geometry should reflect the active expert shape and must be measured on the target backend.
- Cross-runtime/cross-hardware mechanisms do not move target rates without exact target-lane reproduction.
- No canonical target movement this pass.
- P69 remains isolated.
