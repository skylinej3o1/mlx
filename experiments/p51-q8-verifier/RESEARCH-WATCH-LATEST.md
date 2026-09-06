# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-1245.md`

   **The 12:45 note is authoritative for QSA tie-set correctness, PLE request/step epoch ownership, Apple batch-composition invariance, stochastic speculative-sampling certification, warm-slot PP qualification and small-N decode/MTP kernel routing. It moves no performance target.**

4. The immediately previous deltas remain essential:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-06-0956.md` — eviction/pause progress, chunk-faithful MTP reconciliation, QSA known-horizon reservation, route-aware long-context memory accounting, immediate-follow-up cache-store freshness and ds4 Qwen3.8 Flash-Next mechanism mining;
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

**The 12:45 pass moves no row.** It adds no sustained physical receipt from the exact target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 and ANE-assisted routes remain separate approximate production lanes.
- 5070 targets require measured residency/backend placement and net VRAM/context headroom.
- DS4 remains conservative until exact sustained current-head 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-06 12:45 ET

Starting freshness boundary: `04aeef52051d6fdda7ac49d4a507be2aadc2a566` / **2026-09-06 14:14:07 UTC**.

## FRESH / material

### llama.cpp #28497 — QSA tie handling can change the selected set itself

Qwen4-exp QSA expands compressed-block scores to tied cell scores before top-k. CUDA CUB top-k can choose different cells from the tied boundary block across calls/devices. Real Qwen3.8-Flash-Next temperature-0 runs diverged above the selection boundary; stable radix-sort fallback restored repeatability.

**Promotion:** certify compressed-block set, expanded-cell set, tie-boundary membership, order and first-divergent position. Stable order alone is not sufficient.

### vLLM #54521 / #53899 — four independent correctness axes

Fresh position-resolved work separates:

1. QSA selected-set/order/tie determinism;
2. MoE finalize determinism;
3. external/async PLE request-step ownership;
4. batch-shape/concurrency invariance.

A PLE CPU-offload semaphore could leave every graphed forward consuming the **previous step's PLE output**. Fixing that plus QSA/MoE determinism made sequential runs bit-exact; concurrent larger shapes still diverged, proving concurrency is separate.

**Promotion:** use cold-first plus warm repeats, position-resolved logprobs/top-1, graph/compiled-path off/on where applicable, and sequential/concurrent cells. Same-prompt-twice after warmup is not a sufficient oracle.

### oMLX #3476 — exact M1 Max batch-composition divergence, not caused by MTP

On M1 Max 64 GB / 32 GPU cores, identical greedy requests were serially stable but changed output when overlapped. A small model without MTP reproduced it; a larger Qwen3.6 model produced recurring completion lengths of 67 / 72 / 102 tokens for the same prompt. Single-slot mode restored determinism.

**Promotion:** Apple serving certification includes identical + mixed prompts at concurrency 1/2/3/4, no-MTP first, with output/hash and position-resolved evidence where available.

### rMLX `79f01a37268335781f0395216dfc52c3e1f7c326` — greedy tests did not certify production sampling

Five sidecar speculative loops silently decoded greedily for `temperature > 0` because sampler configuration never reached the speculative loop.

**Promotion:** nonzero-temperature MTP certification resolves temperature/top-p/top-k, seed/RNG ownership and verifier distribution at accepted/rejected/rollback positions. Unsupported penalties/logit bias must fail closed or be explicitly declared.

### oMLX `8327920452bd4180407f8fd8c4100f0a4dafca67` — decode/MTP small-N routing differs from wide prefill

M1 Ultra GLM-5.3-Flash measurements show block MoE kernels can be 2–2.7x slower than plain gather-QMM over much of the small route-count region while wide prefill still favors the block path. A corrected server routing policy materially improved measured aggregate generation.

Qwen3.8-Flash-Next M5 evidence similarly shows tiny-row QSA verification can favor the official masked path while wider work favors gathered selected-K/V.

**Promotion:** benchmark actual route choice by effective row/route count for B1 decode, MTP widths, B2/B4 and prefill. Do not transfer a wide-prefill winner into decode by operator name alone.

### oMLX `2aab2ce3ce2f4254abd0c99a5ff64efb98215d3a` — resource state must be worker-local

SDPA headroom-provider state is now scoped to the actual engine worker rather than a shared registration one scheduler could replace or clear for another.

**Promotion:** resource/correctness state must explicitly belong to request, slot or engine-worker unless truly immutable/process-global.

### llama.cpp #28495 — first-request PP can hide a warm multi-slot collapse

On a Qwen3.8-27B ROCm system with two unified-KV slots, a ~100K prompt measured ~336 PP on request 1 and ~151–155 PP on later sequential requests, while a one-slot control stayed ~323 PP. Generation was unaffected and disabling spec did not remove it.

**Promotion:** cold PP qualification includes request 1 vs request 2+ at slot counts 1/2/3/4 before concurrency is added.

### llama.cpp #28506 — two RTX 5070 Ti fit depends on realized, not requested, tensor split

Qwen3.8-27B Q5_K_M at 190K/q8-KV/MTP3 on 2x RTX 5070 Ti demonstrates that per-tensor split rounding can bias realized allocation away from requested `-ts` and cause OOM. Equal split reportedly fits at ~14,642 MiB / 16,303 MiB per card without the vision encoder.

**Promotion:** if using multi-GPU placement, record requested and realized split/bytes/tensors. This is fit/provenance evidence, not a TG/PP receipt.

---

# Focused follow-up status

- **antirez/ds4 PR #991:** still open at the same inspected head; no post-cutoff update.
- **oMLX #3462 / #3464:** no post-cutoff comments; capture-efficacy and explicit-TG-provenance gates remain active.
- **vLLM #53504 / #55533:** no post-cutoff comments; canonical hybrid boundary and actual scheduled-sequence occupancy remain active.
- **MLX #4409:** no post-cutoff result.
- **llama.cpp #28425 / #28433 / #28448 / #25187:** no post-cutoff comments; standing rollback/context/allocator/MTP-head gates remain active.
- **llama.cpp #28484:** no newer result; retain downgraded/not-currently-reproducible status.
- **Tiel Coder:** no fresh exact RTX 5070 Ti receipt.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or new exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max target-model TG/PP receipt. #3476 is adjacent-model correctness evidence.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card TG/PP receipt. #28506 is two-card fit/provenance evidence only.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Current order:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent rollback / growing-session correctness;
3. cache-layout/handler round-trip + model/tokenizer/runtime identity;
4. cold-first request + request/step epoch ownership for async/external PLE/state;
5. QSA block/cell selected-set, tie-membership and order oracle;
6. batch-composition invariance at concurrency 1/2/3/4, identical + mixed prompts, no-MTP first;
7. real-agent cache capture with canonical recurrent/attention reusable boundary;
8. immediate async-store race + forced eviction/pause progress;
9. warm-slot PP request 1 vs request 2+ at slot counts 1/2/3/4;
10. realistic-depth QSA/attention vs MoE/GDN/host profiler;
11. QSA known-horizon reservation + capacity/footprint accounting;
12. PLE residency/page-cache/direct-read;
13. small-N versus wide-N kernel-route matrix for MoE/QSA decode/verify/prefill;
14. MTP reconcile using ordinary prefill chunk geometry;
15. MTP pre-verify snapshot / commit / replay + per-slot draft context;
16. production sampler-law certification for temperature/top-p/top-k, RNG and rollback positions;
17. actual scheduled-sequence occupancy at parallel 1/2/3/4 plus stress;
18. concurrent pure-prefill isolation;
19. adversarial parallel-MTP slot isolation;
20. M1/M2 activation-FP16 approximate lane after exact freeze;
21. compiled B2/B4; combine passing mechanisms; long prefill while other sessions decode.

Safe serving remains profitable singleton MTP + plain concurrent work until multi-slot state isolation, batch-composition invariance and occupancy pass.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve Qwen's known resident baseline; test Tiel Q4/Q5 partial expert offload with 64 GB host RAM rather than defaulting to 3-bit. Record actual CUDA backend placement, resident/offloaded bytes, whole-round MTP economics, MTP-head quant, peak VRAM/context and real coding-agent wall time. If multi-GPU is ever used, record realized split rather than trusting `-ts`.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. Production serving-concurrency findings do not alter the frozen exact verifier campaign unless intentionally brought under test.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as topology/mechanism control until sustained exact 0731 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- QSA correctness = selected set + tie membership + order.
- Cold-first request is a mandatory oracle for async/external state.
- External/async PLE and recurrent state need request/step epoch ownership.
- Batch composition is an independent semantic axis and has direct M1 Max evidence.
- Greedy equivalence does not certify stochastic speculative decoding.
- Warm multi-slot PP is separate from first-request PP.
- Decode/MTP small-N and prefill wide-N require separate kernel routing qualification.
- Resource/headroom state belongs to request/slot/worker, not mutable globals.
- Requested tensor split is not allocation provenance; record realized placement.
- Cross-runtime/higher-chip gains remain mechanism candidates until target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.