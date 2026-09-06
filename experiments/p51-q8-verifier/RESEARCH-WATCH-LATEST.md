# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1951.md`

   **The 19:51 note is authoritative for physically backed MTP/recurrent concurrency accounting, no-MTP batch-composition certification, version-qualified long-context small-N routing and benchmark answer-equivalence requirements. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1832.md` — corrected GDN baseline semantics, typed recurrent/attention/draft cache geometry, warm unified-KV PP root-cause qualification, persistent-vs-draft state ownership, full-vector frontier validation, byte-faithful session snapshots and physically backed recurrent-state capacity;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1245.md` — QSA tie-set correctness, PLE request/step epoch ownership, Apple batch-composition invariance, stochastic speculative-sampling certification, warm-slot PP qualification and small-N decode/MTP kernel routing;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0956.md` — eviction/pause progress, chunk-faithful MTP reconciliation, QSA known-horizon reservation, route-aware long-context memory accounting, immediate-follow-up cache-store freshness and ds4 Flash mechanism mining;
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

**The 19:51 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-06 19:51 ET

Starting freshness boundary: `9804a511b1adfaa1726b1858fb7a58c101fccd1b` / **2026-09-06 22:41:15 UTC**.

## FRESH / material

### vLLM #55533 + WIP PR #55617 — MTP recurrent-state reserve may be the physical concurrency limiter

The fresh issue update and diagnostic PR now test a concrete mechanism: MTP reserves extra recurrent/mamba state blocks per sequence, increasing `per_req_blocks` and lowering `max_concurrency = num_blocks / num_blocks_per_request`.

The requested A/B is identical Qwen3.8-27B hybrid GDN workload with MTP on versus completely off, logging mamba mode, speculative blocks, per-request block count and computed concurrency.

**Status:** hypothesis under test, not yet proven. PR #55617 is diagnostic-only.

**Promotion:** B2-B4 certification records target recurrent rows, speculative reserve, total physical capacity, realized per-request footprint, actually scheduled sequences, emitted tokens/sequence/iteration, aggregate TG and TTFT. MTP off/on becomes a physical-capacity A/B, not only an acceptance/speed A/B.

### vLLM #53257 UPDATE — base batched decode remains nondeterministic without speculation

DeepSeek-V4 Flash temperature-0 concurrency tests remain nondeterministic after swapping MoE backend, sparse-attention backend, indexer-cache precision, graph mode and prefix caching. With speculative decoding completely disabled, the reported mean minority-output rate increased to **2.36%** across five 500-request concurrency-32 runs.

**Promotion:** no-MTP batch-composition invariance must pass before MTP is enabled. Treat per-step batch metadata/state ownership as an independent correctness surface. A speculative verifier can partially mask an underlying base-path defect by rejecting bad proposals.

### vLLM #55615 — long-context small-N route guards require dependency-version provenance

Fresh ROCm evidence shows a >64K sparse top-k fallback justified by old AITER 0.1.19 behavior remains active after AITER 0.1.21.post1 can run the shape faster. Operator delta is ~20-24% at 65K/131K but only ~1.1% of reported total decode TPOT.

**Promotion:** version-stamp kernel-route guards and re-evaluate long-context small-N routes at B1/MTP/B2/B4. Record operator share of TPOT before promoting work.

## BACKFILL / benchmark integrity

### rMLX `128932f3379baaf7e4923ddd24cbf50d1dd7b26e` — greedy speed rows require whole-answer equivalence

A speculative benchmark now refuses to file a greedy throughput row unless:

- the plain reference repeats itself;
- the speculative arm matches the whole plain completion run-by-run;
- sampler disposition is unambiguous.

Sampled runs are explicitly marked instead of being required to match independent draws token-for-token.

**Promotion:** greedy performance rows require semantic equivalence before recording; sampled rows require sampling-law certification and explicit labeling.

---

# Focused follow-up status

- **oMLX #3462 / #3464:** no post-cutoff activity surfaced.
- **llama.cpp #25187 / #28425 / #28433 / #28448:** no post-cutoff activity surfaced.
- **llama.cpp / oMLX / ds4 / rMLX:** no new post-cutoff relevant commit surfaced in this pass.
- **MLX #4409:** no new target-relevant result surfaced.
- **vLLM #55533:** materially updated; diagnostic PR #55617 active, no root-cause proof/fix yet.
- **vLLM #53257:** materially updated; no-spec concurrent base path still corrupts under the reported workload.
- **Tiel Coder:** no fresh exact RTX 5070 Ti result.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or new exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Current order:

1. historical pinned llama control;
2. corrected-GDN semantic baseline + reference frontier/state certification;
3. exact PP2/layer-owned baseline; TP2 control;
4. ordinary no-spec recurrent rollback / growing-session correctness;
5. typed cache/state-grid identity + unequal-grid restore;
6. **no-MTP batch-composition invariance at concurrency 1/2/3/4 before speculative testing**;
7. cache-layout/handler + model/tokenizer/runtime/GDN identity;
8. cold-first request + PLE/state epoch ownership;
9. QSA selected-set/tie/order oracle;
10. real-agent cache capture + canonical recurrent/attention reusable boundary;
11. immediate async-store race + forced eviction/pause progress;
12. warm-slot PP + Metal interior-mask-skip proof;
13. realistic-depth profiler + long-context small-N route/version matrix;
14. QSA known-horizon reservation + route/footprint accounting;
15. PLE residency/page-cache/direct-read;
16. chunk-faithful MTP reconcile;
17. pre-verify snapshot / commit / replay with temporary drafts excluded from persistent history;
18. **MTP off/on recurrent-capacity accounting: target rows + speculative rows + actually scheduled sequences**;
19. per-slot draft context + adversarial multi-slot isolation;
20. production sampler-law certification;
21. full-vector frontier/state fingerprints;
22. file/memory session byte identity + semantic restore equivalence;
23. concurrent pure-prefill isolation;
24. M1/M2 activation-FP16 approximate lane after exact freeze;
25. compiled B2/B4; combine passing mechanisms; long prefill while other sessions decode.

Mild concurrency remains a core upside hypothesis, but the production claim is now explicit:

> aggregate scaling is measured only over requests simultaneously physically scheduled with independent correct state; configured or queued slots do not count as active concurrency.

Safe serving remains profitable singleton MTP + plain concurrent work until multi-slot state isolation and physical-capacity behavior are proven.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the Qwen resident baseline; test Tiel Q4/Q5 partial expert offload with 64 GB host RAM. Keep realized placement, whole-round MTP economics, corrected GDN semantics, long-context behavior and real coding-agent wall time explicit.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External serving findings do not silently rewrite frozen evidence.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as mechanism/topology evidence until sustained current-head exact dual-M1 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- MTP can consume recurrent-state capacity as well as compute; measure both.
- Configured parallelism is not scheduled parallelism.
- Greedy batch-composition invariance must pass before speculation is credited with correctness.
- A speculative verifier may partially mask corruption in the underlying batched path.
- Per-step batch metadata/state ownership is first-class correctness state.
- Dependency-version route guards carry provenance and are re-qualified after upgrades.
- Long-context small-N optimization priority depends on share of total TPOT.
- Greedy speed rows require semantic equivalence to a repeatable plain reference before recording.
- Sampled performance requires sampling-law certification rather than token identity.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.