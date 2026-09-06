# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0956.md`

   **The 09:56 note is authoritative for eviction/pause progress correctness, chunk-faithful MTP reconciliation, QSA known-horizon reservation, route-aware long-context memory accounting, immediate-follow-up cache-store freshness and the ds4 Qwen3.8 Flash-Next mechanism-mining lane. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0658.md` — actual MTP scheduler occupancy, canonical recurrent/attention first-repeat cache boundaries, realistic-depth Apple Flash attribution and CUDA backend-placement provenance;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0243.md` — whole-round speculative economics, marginal multi-position verify cost and QSA selected-set/order determinism;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1943.md` — speculative-checkpoint provenance, greedy verifier-only equivalence and first-repeat MTP cache backfill;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1512.md` — real-agent cache-capture efficacy, MTP-head/vocabulary ordering, reusable scratch and TG-log provenance;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1200.md` — ordinary recurrent rollback, per-slot MTP context sizing, AProjQ4 PP semantics, M1/M2 FP16 activation lane and persistent runtime identity.

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

**The 09:56 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-06 09:56 ET

Starting freshness boundary: `b67893dc685847fa4a2508ef074a6cff82790984` / **2026-09-06 11:07:17 UTC**.

## BACKFILL / material

### antirez/ds4 PR #991 — Qwen3.8 Flash-Next Metal runtime is now a serious mechanism-mining/control lane

Open PR #991 adds Qwen3.8-Flash-Next / `qwen4_exp` Metal support, external PLE, optional MTP, optimized kernels, correctness checks and benchmarks through 262K.

The corrected M3 Ultra 512 GiB candidate reports:

- **896/896** recorded full-vocabulary FP32 decode vectors byte-identical to the original numerical reference through 262K;
- all recorded frontier top predictions and greedy continuations matching;
- fresh-8K prefill **1149.37 -> 1201.06 tok/s (+4.50%)**;
- total decode **45.59 -> 47.24 tok/s (+3.62%)**;
- 262K combined-median decode **42.425 -> 43.735 tok/s (+3.09%)**.

An earlier MTP-focused candidate measured roughly +5–6% across three short prompts, but later long-context work found numerical drift in that implementation. Treat those MTP rows as mechanism evidence; the corrected candidate's MTP regression smoke is smaller and less repeated.

**Promotion:** mine two-token HC/GDN geometry, expert input reuse, predictor batching/submission reduction and the 262K correctness harness. Do not transfer M3 Ultra rates or percentages to M1 Max.

## FRESH / material

### oMLX — eviction/pause progress is part of cache correctness

Commit `9a544e37f22c493fe281e5d1284c3cadaf44dedb` fixes a scheduler path where a prefill request paused after its cache had advanced, then resumed from stale logical counters and fed already-prefilled tokens again.

Failure consequences include duplicated KV spans, boundary snapshots behind the true prefix and later prefix hits restoring semantically corrupted state.

**Promotion:** add a forced eviction/pause oracle. Compare logical consumed tokens, cache offsets, boundary frontier and resumed logits/state against an uninterrupted chunked control; then store/reuse the session and prove later prefix-hit equivalence.

### oMLX — MTP reconcile must reproduce ordinary prefill chunk geometry

Commit `e69d707359eb2f682beacc1802b7dee5b35b4c02` fixes MTP fallback reconciliation that could rebuild a 13–30K history in one forward rather than the normal prefill chunk sequence.

On a measured GLM5.3-Flash case, one-shot reconstruction diverged from a 512-token-chunk cache beginning around layer 7. The fix pins the ordinary generator step; a 1,300-token test expects `[512, 512, 276]`.

**Promotion:** record original/reconcile chunk sequences and compare recurrent/QSA/KV state plus target logits across QSA route boundaries. Token-count equality is not enough.

### oMLX #3455 — reserve QSA/indexer capacity against the known final horizon

Fresh merged work shows a Qwen3.8-Flash-Next-oQ4e-mtp ~205K prompt on an M-series 128 GB machine crossing a QSA growth boundary and jumping process footprint by about **12.25 GB**, allocating capacity 393,216 despite a 262,144 model maximum.

The fix reserves the known final prefill horizon once and covers restored-prefix cases.

**Promotion:** move known-horizon reservation earlier. Record logical horizon, reserved/realized capacity, realloc count/bytes and physical-footprint deltas.

### oMLX Qwen4-exp long-context memory accounting — price the route actually executed

Fresh commits including `a0a16857301a39eae8ba9c98577063d2ff47b1b5`, `58df5bd5e3f75ac25cb5a16697c73374a0a9eded` and `d90d6fcbaa725bb03023f85c339868ab9151a0d6` correct masked SDPA256 pricing, route attribution and retained-vs-reclaimed allocator accounting.

Reported validation includes cold ~180K multimodal prefill, a ~190K cached continuation and a restored-prefix dense-mask replay that had previously been rejected by over-predicting another ~26.7 GB.

**Promotion:** record predicted route and **actual execution route** (gathered/dense-mask, bounded/unfused), physical footprint, MLX active/model resident memory, retained pool bytes, reclaimed bytes and per-chunk transient prediction.

### oMLX — immediate agent follow-ups can race async cache storage

Commit `8827f0956f09ef31b1817aac3598b65ffe330e08` replaces a fixed prompt-length wait floor with restorable-overlap logic. A sub-4K follow-up could otherwise arrive before the preceding `store_cache` finished and re-prefill every turn.

**Promotion:** real-agent cache qualification includes an immediate-follow-up cell that records in-flight-store status, common/restorable overlap, wait/skip decision, reused/fresh tokens and TTFT versus a settled control.

### oMLX — prefix cache storage/reuse must fail closed for unreconstructible cache layouts

Fresh commits `2f6aa9a2c157b3dc13e0b85caec24ef434ce69b3` and `b2cb698ffc5989bca92ac9930f6aad2d9c34040b` prevent unknown cache subclasses from being structurally downgraded to plain KV representation and losing semantic state.

**Promotion:** cache class/handler identity and round-trip preservation join model/tokenizer/runtime identity. Test both partial and exact hits; fail closed on unknown layouts.

## UPDATE / prior evidence downgraded

### llama.cpp #28484 — distributed MTP regression no longer reproducible

The reporter now says the previously reported 25–30% MTP regression cannot be reproduced, with no driver/Windows update, although TG remains below the historical value.

Downgrade the regression claim. Retain the measurement discipline it motivated: same-topology no-spec control, speculative wall/TG, acceptance, graph reserve, transport/sync and draft/target context allocation.

## FRESH / first-repeat control strengthened

### vLLM #53504 — another hybrid gets zero MTP prefix hits until no-drop diagnostic

A Qwen3.6-35B-A3B hybrid reproduction reports default MTP cache hits **0 / 72,992 queried tokens**, while no-spec begins hitting from request two. `disable_eagle_block_drop=true` restores the no-spec total hit count in that run without changing acceptance.

Use no-drop as a diagnostic A/B, not a presumed universal fix. The canonical requirement remains one reusable boundary shared by recurrent and attention state, with verifier-only greedy equivalence preserved.

## Supporting / separate lanes

- Fresh oMLX ANE fixes make compiled-bank reserve/release accounting more truthful and include a non-target ~65K Qwen27 prefill report around 397 tok/s. Keep this strictly in the approximate ANE lane; do not use it as an M1 native target ruler.
- llama.cpp PR #28475 fixes CUDA MMID/MMF racecheck findings. Keep deterministic repeated-logit/race-clean execution in Qwen/Tiel CUDA qualification; no rate transfer.
- rMLX `285a51abbbd7b0ce9cb6e8888dcd4a3125fb1319` strengthens published-benchmark provenance/harness refusal logic; no new model rate.

---

# Focused follow-up status

- **oMLX #3462:** no fresh comments; real-agent cache-capture gate remains active, strengthened by pause/resume and async-store cases.
- **oMLX #3464:** no fresh comments; explicit generated-token/TG provenance remains active.
- **llama.cpp #28425:** unchanged; ordinary no-spec recurrent rollback remains active.
- **llama.cpp #28433:** unchanged; per-slot MTP draft-context sizing remains active.
- **llama.cpp #28448:** unchanged; allocator identity remains monitored.
- **llama.cpp #25187:** unchanged; full-head quantization before aggressive FR-Spec remains active.
- **MLX #4409:** no new result.
- **Tiel Coder:** no fresh exact 5070 Ti result.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or new exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max serving receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Current order:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent rollback / growing-session correctness;
3. cache-layout/handler round-trip + model/tokenizer/runtime identity;
4. real-agent cache capture with one canonical recurrent/attention reusable boundary; MTP on/off;
5. **immediate short-follow-up async-store race**;
6. **forced eviction/pause progress oracle**;
7. QSA selected-set/order + position-resolved behavioral regression;
8. realistic-depth QSA/attention vs MoE/GDN/host profiler;
9. **known-horizon QSA reservation** and capacity/physical-footprint metrics;
10. PLE residency/page-cache/direct-read;
11. **MTP reconcile using ordinary prefill chunk geometry**, including short-tail invariant;
12. MTP commit/replay + per-slot draft context;
13. scheduled-sequence occupancy at parallel 1/2/3/4 plus stress;
14. concurrent pure-prefill state isolation;
15. adversarial parallel-MTP slot isolation;
16. M1/M2 activation-FP16 approximate lane after exact freeze;
17. compiled B2/B4;
18. combine passing mechanisms, then long prefill while other sessions decode.

Use ds4 #991 as an explicit Flash **alternative-runtime/mechanism-mining control**, not as target evidence.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve Qwen's known resident baseline; test Tiel Q4/Q5 partial expert offload rather than defaulting to 3-bit. Record actual CUDA backend placement, MMID/MMF correctness, whole-round MTP economics, full-head quant, peak VRAM/context and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. ANE evidence remains approximate-lane only.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as topology/mechanism control until a sustained exact 0731 generated-token denominator exists.

---

# Standing decisions strengthened this pass

- Cache correctness includes semantic cache-class/handler round-trip, not token hashes alone.
- Pause/resume must preserve logical progress, physical cache progress and boundary-snapshot frontier.
- Reconcile/rollback must preserve the effective prefill geometry that built recurrent/QSA state.
- Long-context memory accounting distinguishes resident/retained bytes from reclaimed/reallocatable bytes.
- Record the **route actually executed**, not only the route predicted/configured.
- Known final context horizon is a legitimate capacity-management input.
- Immediate agent follow-ups belong in cache qualification.
- Cross-runtime/higher-chip gains remain mechanism candidates until target-hardware reproduction.
- llama.cpp #28484 is downgraded; retain controls, not the causal claim.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
