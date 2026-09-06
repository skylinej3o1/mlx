# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct targets from older watch-note prose.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0658.md`

   **The 06:58 note is authoritative for actual MTP scheduler occupancy, canonical recurrent/attention first-repeat cache boundaries, distributed-MTP control requirements, realistic long-context Apple Flash attribution and actual CUDA backend-placement provenance. It moves no performance target.**

4. The immediately previous delta remains essential:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0243.md`

   It remains authoritative for whole-round speculative economics, marginal multi-position verify cost and QSA selected-set/order determinism.

5. The 19:43, 15:12 and 12:00 deltas remain important for speculative-checkpoint provenance, verifier-only equivalence, first-repeat cache qualification, real-agent cache-capture efficacy, MTP-head/vocabulary ordering, reusable scratch, ordinary recurrent rollback and persistent identity:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1943.md`
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1512.md`
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1200.md`

6. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain dated deltas newer than that point when reconstructing the evidence chain. The recent sequence is:

   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode correction / hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS, Blackwell ubatch and cache granularity;
   - `RESEARCH-WATCH-2026-09-04-0915.md` — v0.4.0-era baseline, parallel-MTP isolation, SSD-expert streaming and MTP-head quant;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — PP-vs-TP structural evidence, production cache-granularity failure and CUDA provenance;
   - `RESEARCH-WATCH-2026-09-04-1840.md` — stable v0.4.0 pin, modality-agnostic KV reuse, DS4 tool-observation correction and MTP draft-cache VRAM;
   - `RESEARCH-WATCH-2026-09-04-1930.md` — Flash MTP commit semantics, concurrent-PLE state isolation, Apple recurrent kernels and decoupled cache geometry;
   - `RESEARCH-WATCH-2026-09-05-0400.md` — neighboring-row QSA gather reuse, Metal `MUL_MAT` width exactness and DS4 fixed-work PP;
   - `RESEARCH-WATCH-2026-09-05-0500.md` — production-layout invariance correction, low-level runtime provenance and Strix-Halo AProjQ4 smoke;
   - `RESEARCH-WATCH-2026-09-05-1200.md` — recurrent multi-turn rollback, per-slot draft context, AProjQ4 PP semantics, M1/M2 FP16 activation lane and persistent-state identity;
   - `RESEARCH-WATCH-2026-09-05-1512.md` — real-agent cache-capture efficacy, 27B FR-Spec correction, ds4 reusable scratch, allocator identity and TG-log provenance;
   - `RESEARCH-WATCH-2026-09-05-1943.md` — speculative-loader provenance, greedy answer equivalence and first-repeat MTP cache-boundary backfill;
   - `RESEARCH-WATCH-2026-09-06-0243.md` — whole-round MTP decomposition, marginal verify-position cost, QSA order determinism and M5 TensorOps approximate-lane backfill;
   - `RESEARCH-WATCH-2026-09-06-0658.md` — MTP scheduler occupancy, canonical hybrid cache boundary, distributed-MTP regression controls, corrected M5 long-context attribution and CUDA backend-placement provenance.

7. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 06:58 pass moves no row.** It adds no sustained physical receipt from the four target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and hardware-specific approximate matrix routes remain separate from exact-runtime evidence.
- 5070 targets require full residency and measured net VRAM/context headroom.
- DS4 remains conservative until exact sustained 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-06 06:58 ET

Starting freshness boundary: `4fcc8631aed3bde6e2e757c281d586c1c5a4c200` / **2026-09-06 06:51:53 UTC**.

## FRESH / material

### llama.cpp #28484 — distributed draft-MTP can regress while acceptance and plain decode stay healthy

On Qwen3.8-27B UD-IQ4_XS split across RTX A2000 12 GB + RTX 3080 10 GB over 2.5 GbE RPC, updating `bb4caa7` -> `6a1a922` changed:

- MTP depth-2 TG **27–32 -> 21.3 tok/s**;
- no-MTP dense decode stayed ~17–18 / **17.5 tok/s**;
- acceptance stayed healthy at **0.737–0.832** and mean accepted length **1.74–1.83**;
- a separate 31B dense control stayed **17.66 tok/s**.

The newer build also increased graph/compute reserve enough to disturb a previously loadable 98K-context split.

**Promotion:** distributed/TB4 speculative certification must retain a same-topology no-spec control and record speculative TG/E2E wall, acceptance, per-round transport/sync, graph reserve and draft/target context allocation. Acceptance alone is not a performance oracle.

This is distributed CUDA/RPC evidence, not a dual-M1 rate ruler.

## BACKFILL + FRESH UPDATE / material

### vLLM #53504 — canonical hybrid cache boundary is now a first-repeat requirement

Qwen3.8-27B-FP8, dual RTX 5090 TP2, MTP2, 1,600-token hybrid block unit:

- spec-on repeat shape: **cold / full re-prefill / hit**;
- unmodified current main reproduced **24.9 / 2.83 / 0.61 s**;
- no-spec control reproduced **3.47 / 0.28 / 0.29 s**.

Mechanism: MTP/EAGLE reduces an 11,910-token prompt’s reusable hybrid boundary to **9,600**. The first request materializes recurrent state at 9,600 but default sparse retention keeps the unshifted 11,200 boundary, so FullAttention has 9,600 and recurrent groups do not. Request 2 therefore reconciles to zero, then learns the 9,600 junction; request 3 hits.

A 1,600-token retention-interval workaround gave **2.52 s cold then 0.55 s on all repeats**, but occupancy/eviction pressure remains unmeasured.

**Promotion:** recurrent and attention state must share one canonical MTP-adjusted reusable boundary. Record full prompt, adjusted boundary, retained boundaries by state family, first/second repeat hits, growing-session reused/fresh tokens and occupancy pressure. Any semantic change must preserve verifier-only greedy equivalence.

### vLLM #55533 — actual speculative scheduler occupancy is a multi-agent promotion gate

Qwen3.8-27B-class hybrid, RTX 4090 D, 48 GDN +16 attention layers, MTP k=1:

| batch | no spec | MTP | mean accepted len / seq / iteration |
|---:|---:|---:|---:|
| 1 | 56.4 | **72.0** | 0.86 |
| 3 | 150.6 | **203.7** | 0.84 |
| 4 | **195.4** | 157.8 | -0.03 |
| 8 | **367.1** | 197.0 | -0.38 |
| 20 | **649.0** | 210.9 | -0.73 |

At batch 8, each decode iteration schedules only **3 of 8** sequences, distribution `[2,2,2]`; the remainder rotate in later. A smaller 24-GDN-layer sibling does not show the collapse up to batch 20, pointing at recurrent-state/speculative-slot budget accounting.

**Promotion:** configured concurrency is not measured concurrency. For parallel 1/2/3/4 plus stress above 4, record active requests, actually scheduled sequences, token distribution per sequence, target/draft slots, recurrent-state memory, cache admission and aggregate emitted tokens/iteration.

This strengthens the safe default: profitable singleton MTP + plain concurrent work until multi-slot state residency and slot isolation are proven on target hardware/runtime.

### mlx-serve #366 — corrected M5 Flash profile says realistic long-context attention is first-order

Keep only the reporter’s **final corrected interpretation**.

Direct model-level measurement remains:

- M5 Max 128 GB, MLX 0.32.2, 4-bit Flash-Next;
- 65K source-code prompt, prefix cache disabled;
- Flash prefill **1,329 tok/s**;
- dense 27B controls 604 / 651 tok/s.

At realistic context depth, a representative 4,096-token chunk around 32K key length measured:

- SDPA: **1,112 ms / 36%**;
- MoE GEMMs: 665 ms / 22%;
- MoE scaffolding: 271 ms / 9%;
- GDN projections: 232 ms / 8%;
- conv1d: 89 ms / 3%;
- attention projections: 64 ms / 2%;
- 2,433 ms accounted vs 3,060 ms actual.

Across the 65K work estimate, total work was **1,026 TFLOP / 49.3 s = 20.8 TFLOP/s**, about **42%** of the reporter’s measured ~50 TFLOP/s 4-bit GEMM ceiling. Attention represented about **62% of total FLOPs**. Individual SDPA/MoE kernels were roughly 27–38 TFLOP/s.

Earlier claims that the path was unsorted, 95.7% MoE-bound, or only 16% utilized were explicitly retracted. Prefill already sorts experts, and an actual 4,096 -> 8,192 runtime chunk A/B moved PP only **0–1%**.

**Promotion:** profile Flash PP at realistic key depth and keep QSA/attention first-order for long context. Separate attention/QSA, MoE, GDN and launch/host time. Do not promote the initial “19x unsorted MoE” hypothesis.

M5 is transfer evidence only; the dual-M1 target remains unchanged.

### vLLM #54521 / open PR #55122 — QSA deterministic kernel contract is sharper; model-level proof pending

PR #55122 proposes deterministic `persistent_topk` output in ascending index order, removes atomic arrival-order output assignment on relevant paths and removes the candidate-buffer failure mode that could alter the selected set.

Standalone sm121 harness: **177/177** deterministic/reference-equal cases; stock kernel reproduced its own exact output **0/177** on those test inputs.

Reported cost is roughly 1.3–3x per top-k call. Model-level +1.5% decode-step at 32K and +2% TTFT at 8K are estimates; inspected end-to-end A/B was still pending.

Fresh scoping also confirms Flash-Next’s vLLM MoE path uses `FusedTopKRouter` / CUDA `topk_softmax`, not the separate `grouped_topk` fallback; do not conflate #55514 with this QSA issue.

**Promotion:** retain set/order/canonical-logit gates and add position-resolved teacher-forced logprob spread, top-1 agreement, top-k overlap and first-divergent-position tests in serial and concurrent modes around the selection boundary.

## BACKFILL / known provenance trap

### llama.cpp #28455 — `-fa on` is not proof that CUDA FlashAttention executed

A freshly closed maintainer comment calls the behavior a known issue. With default `GGML_CUDA_FA_ALL_QUANTS=OFF`, unsupported q4_1/q5_0/q5_1 KV FA combinations can silently schedule attention on CPU while `llama-bench` still reports `fa=1`.

The detailed RTX 4080 table is user-reported; representative server numbers were q5_1 default **38.4 PP / 6.5 TG**, q8_0 default **1,348 / 30.1**, and q5_1 with `GGML_CUDA_FA_ALL_QUANTS=ON` **1,162 / 38.5**.

**Promotion:** actual operator/backend placement belongs in benchmark provenance. If the 5070/Tiel/Qwen lane uses q4_1/q5 KV, assert compiled FA support and GPU execution before comparing rates.

---

# Focused follow-up status

- **oMLX #3462:** no post-cutoff comments/fix surfaced; real-agent cache-capture gate remains active.
- **oMLX #3464:** no post-cutoff comments/fix surfaced; explicit TG provenance remains active.
- **jundot/omlx main:** no material post-cutoff update surfaced.
- **rMLX main:** no post-cutoff commits surfaced; 02:43 whole-round MTP evidence remains current.
- **antirez/ds4 main:** no post-cutoff commit surfaced.
- **MLX #4409:** no post-cutoff comment/result surfaced.
- **llama.cpp #28425/#28433/#28448/#25187:** no newer result displaced their standing gates.
- **Tiel Coder:** no fresh targeted receipt surfaced.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG receipt or completed new exact-rig cold-PP result.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact-card TG/PP receipt.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max serving receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Current order:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent rollback / growing-session correctness;
3. real-agent cache capture plus **canonical recurrent/attention reusable-boundary** check;
4. first-repeat, second-repeat and growing-session reuse with MTP on/off;
5. QSA set/order determinism plus position-resolved behavioral regression;
6. realistic-depth long-context profiler: QSA/attention vs MoE vs GDN vs host/launch;
7. PLE residency/page-cache/direct-read and QSA known-horizon/residency work;
8. MTP recurrent commit/replay plus per-slot draft-context sizing;
9. **scheduled-sequence occupancy** at parallel 1/2/3/4 and stress above 4;
10. concurrent pure-prefill / adversarial MTP slot-isolation;
11. whole-round MTP replay/verify/head/sync/transport accounting;
12. activation-FP16 approximate lane only after exact freeze;
13. compiled multi-agent / long-prefill-while-decode combinations.

Canonical center remains **40 TG / 400 cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel control lane

No target change and no Tiel rate claim.

1. Preserve the known resident Qwen baseline.
2. Tiel practical A/B remains Q4/Q5 partial expert offload using 64 GB host RAM, not 3-bit by default.
3. Stamp actual backend/operator placement in every row.
4. If quantized KV is used, assert CUDA FA support and GPU execution.
5. Measure whole-round MTP economics and actual scheduled-sequence occupancy under batching.
6. Full-head MTP-head quantization before aggressive FR-Spec trimming.
7. Judge practical quality/useful-work-per-hour plus TG/PP/VRAM/context headroom.

Canonical Qwen center remains **120 TG / 250 cold PP**.

## Single M1 Max64 Qwen3.8-27B

P69 remains separate: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External serving work does not change that sequence.

Canonical center remains **25 TG / 110 native cold PP**.

## Dual-M1 DS4-0731

No fresh exact-rig result. Existing Metal/TB transport, scratch/temp, rollback and session-state transfer candidates remain in force.

Canonical center remains **15 TG / 180 cold PP**.

---

# Standing decisions strengthened this pass

- **Configured concurrency is not measured concurrency.** Record what the scheduler actually admits each iteration.
- MTP multi-agent promotion requires target/draft recurrent-state budget accounting, not only acceptance and aggregate TG.
- **Acceptance can remain healthy while speculative throughput regresses.** Keep a same-topology no-spec control and round/transport accounting.
- Hybrid cache reuse needs one canonical MTP-adjusted boundary across recurrent and attention state; certify first repeat explicitly.
- Preserve verifier-only greedy equivalence when changing EAGLE/MTP cache semantics.
- Long-context attribution must use realistic key depth; shallow component profiles can invert the apparent bottleneck.
- Requested flags are not treatment proof: stamp effective runtime chunk, actual backend and operator placement.
- QSA promotion requires kernel determinism plus position-resolved/end-to-end behavioral equivalence.
- Previous gates remain active: ordinary recurrent rollback, cache frontier/effectiveness, persistent runtime identity, checkpoint/tensor completeness, per-slot draft context, concurrent state isolation, whole-round MTP economics and explicit TG generated-token provenance.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
