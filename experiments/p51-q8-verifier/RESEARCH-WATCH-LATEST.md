# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1832.md`

   **The 18:32 note is authoritative for corrected GDN baseline semantics, typed recurrent/attention/draft cache geometry, warm unified-KV PP root-cause qualification, persistent-vs-draft state ownership, full-vector frontier validation, byte-faithful session snapshots and physically backed multi-agent recurrent-state capacity. It moves no performance target.**

4. The immediately previous deltas remain essential:

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

**The 18:32 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-06 18:32 ET

Starting freshness boundary: `d40aeef2c2a966ee2c2e238b2b9ec9b8d6d4683d` / **2026-09-06 16:58:15 UTC**.

## BACKFILL / baseline semantic prerequisite

### llama.cpp #28068 / `5fdfa6282936576d2f352d4b97f397a109f207a6` — corrected GDN normalization

Merged just before the previous pass cutoff and missed by that note.

llama.cpp changed GDN q/k normalization from a clamp-style denominator to the reference `rsqrt(sum(x^2)+eps)` form used by Qwen FlashQLA / corrected Transformers / FLA-backed runtimes. The affected architecture set includes **qwen4exp**.

**Promotion:** preserve the old pinned runtime as a historical control, but build the candidate semantic baseline with the corrected normalization. Certify reference frontier logits/state before treating any later speed work as valid. Do not compare pre-fix and post-fix rates as if the inference math were identical.

## FRESH / material

### vLLM #55600 / #55601 — recurrent-state restore must use the recurrent grid's own units

A hybrid prefix hit can seed recurrent state using a smaller attention/draft block size instead of `mamba_block_size`. Out-of-range indices crash; in-range wrong indices can silently restore another valid recurrent-state row, especially with multiple sequences.

**Promotion:** attention, recurrent, draft and QSA geometries are typed units. Add unequal-grid restore tests and multi-slot wrong-row oracles.

### llama.cpp #28495 UPDATE — warm unified-KV PP collapse localized to CUDA/HIP mask skipping

Controlled A/B ties the large repeated-request PP loss to unified KV and stale/interior shared-pool cells. CUDA/HIP FA skips tails but not all-`-INF` interior blocks. **Metal already has interior-block skipping.**

**Promotion:** keep warm-slot PP qualification but downgrade suspicion of this exact root cause on Metal. Explicitly prove the chosen native/custom PP2 path preserves interior masked-block skipping.

### ds4 `394865c5...` — persistent rolling support contains trusted target rows, not temporary drafts

Fresh DSpark state work keeps temporary draft rows outside persistent history and merges only trusted target captures into the logical rolling window. gfx1151 coding-rate gains are transfer evidence only.

**Promotion:** verifier commit/rollback owns persistent-state mutation. Draft rows require temporary lifetime and must disappear on rollback/capture gaps.

### ds4 `85a4f0e6...` — full-vector frontier identity catches hidden drift

Strict full-score/full-float32-vector validation caught numerical drift despite unchanged argmax IDs at all recorded frontiers.

**Promotion:** mechanism gates distinguish bit-identical, numerically drifted but behaviorally passing, and invalid-artifact states. Use full-vector/state fingerprints at selected frontiers.

### ds4 `c0a6119f...` — snapshot transport can corrupt the final byte

An in-memory `fmemopen` session snapshot could overwrite the final payload byte with its terminator. The fix reserves a separate byte and compares memory serialization against file serialization.

**Promotion:** add file-vs-memory byte identity, canonical length/hash, boundary-byte sentinels and semantic restore equivalence.

### vLLM #55580 UPDATE — configured sequences do not prove physically backed recurrent concurrency

A Qwen3.8-27B hybrid TP2 workload shows c32 aggregate throughput stepping from ~230 to ~301 tok/s when the shared state/KV block pool crosses a narrow capacity threshold, while c8 and single-stream are unchanged.

**Promotion:** the appliance concurrency certificate records actual recurrent rows/columns, cache blocks, draft reserve, admitted/scheduled sequences and restart-to-restart capacity variance. Mild-concurrency claims require proof that B2/B4 are physically backed, not merely configured.

### vLLM #55610 — cache compression requires a context-length throughput curve

On a reported Qwen3.8-27B hybrid TP2 stack, k8v4 expands KV capacity ~37% but changes decode from only ~-3% at ~3K context to ~-31% at ~55K versus FP8.

**Promotion:** qualify compression at short/medium/long/~128K with TG, PP, TTFT, memory, concurrency and exact-quality/state gates.

### vLLM `6865e67...` — adaptive speculation calibration belongs after warmup

Adaptive verification is now suppressed during fixed kernel warmup and restored for later calibration/capture.

**Promotion:** if adaptive draft depth is introduced, warm/compile first and calibrate steady-state policy afterward. Keep cold-start metrics separate.

---

# Focused follow-up status

- **oMLX #3462 / #3464:** no post-cutoff comments; cache-capture efficacy and explicit TG provenance remain active.
- **llama.cpp #25187 / #28425 / #28433 / #28448:** no post-cutoff comments; standing full-head, rollback, slot-context and allocator-identity gates remain active.
- **llama.cpp #28495:** materially updated; exact root cause now CUDA/HIP unified-KV interior-mask handling, with Metal carrying the relevant skip capability.
- **MLX #4409:** no new exact target result surfaced.
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

1. preserve historical pinned llama runtime as control;
2. corrected-GDN semantic candidate + reference frontier-logit/state certification;
3. exact PP2/layer-owned baseline; TP2 control;
4. ordinary no-spec recurrent rollback / growing-session correctness;
5. typed cache/state grid identities + adversarial unequal-grid restore;
6. cache-layout/handler + model/tokenizer/runtime/GDN identity;
7. cold-first request + request/step epoch ownership;
8. QSA selected-set/tie/order oracle;
9. batch-composition invariance at concurrency 1/2/3/4, no-MTP first;
10. real-agent cache capture + canonical recurrent/attention reusable boundary;
11. immediate async-store race + forced eviction/pause progress;
12. warm-slot PP + explicit Metal interior-mask-skip proof;
13. realistic-depth QSA/attention vs MoE/GDN/host profiler;
14. known-horizon QSA reservation + route/footprint accounting;
15. PLE residency/page-cache/direct-read;
16. small-N vs wide-N route matrix;
17. chunk-faithful MTP reconcile;
18. pre-verify snapshot / commit / replay with temporary drafts excluded from persistent history;
19. per-slot draft context + physically backed recurrent capacity at parallel 1/2/3/4;
20. production sampler-law certification;
21. full-vector frontier/state fingerprints;
22. file/memory session byte identity + semantic restore equivalence;
23. concurrent pure-prefill isolation;
24. adversarial parallel-MTP slot isolation;
25. M1/M2 activation-FP16 approximate lane after exact freeze;
26. compiled B2/B4, combine passing mechanisms, then long prefill while other sessions decode.

Safe serving remains profitable singleton MTP + plain concurrent work until multi-slot state isolation, batch-composition invariance and physical-capacity gates pass.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the known Qwen resident baseline and test Tiel Q4/Q5 partial expert offload using 64 GB host RAM rather than defaulting to 3-bit. Include corrected GDN semantics, context-length compression curves, realized residency/backend placement and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. The external serving-runtime GDN correction does not silently rewrite frozen P69 evidence; test it later as an explicit new control if desired.

## Dual-M1 DS4-0731

No exact-rig target update. Fresh ds4 work is strong state/certification mechanism evidence, but measured rates in this delta are other hardware and do not transfer numerically to M1 Max.

---

# Standing decisions strengthened this pass

- Correct GDN math is part of baseline identity, not an optimization knob.
- Historical pins remain controls when semantic fixes require a new candidate baseline.
- Cache/state block sizes are typed units; heterogeneous grids must not share an unqualified index.
- Multi-slot restore must catch wrong-but-valid cross-row reads, not only crashes.
- Persistent speculative history contains verifier-authoritative target state, not temporary drafts.
- Full-vector identity catches drift that argmax equality can miss.
- Session serialization must be byte-faithful independently of model-state logic.
- #28495 is now a CUDA/HIP-specific mechanism; Metal keeps a regression gate at lower suspicion.
- Configured concurrency is not physical recurrent-state capacity.
- Cache compression is qualified over context length.
- Adaptive speculation calibration belongs after kernel warmup.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.