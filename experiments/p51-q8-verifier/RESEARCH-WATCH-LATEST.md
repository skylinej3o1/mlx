# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct targets from older watch-note prose.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1943.md`

   **The 19:43 note is authoritative for speculative-checkpoint provenance / greedy answer-equivalence gates and for the first-repeat MTP prefix-cache backfill. It moves no performance target.**

4. The immediately previous delta remains essential:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1512.md`

   It remains authoritative for real-agent cache-capture efficacy, Qwen3.8-27B MTP-head/vocabulary experiment ordering, ds4 reusable-scratch transfer, allocator-identity monitoring and benchmark-TG provenance.

5. The 12:00 delta remains important for ordinary recurrent rollback, per-slot MTP context sizing, DS4 fresh-prefill semantics, M1/M2 FP16 activation experimentation and persistent-cache identity:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1200.md`

6. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain dated deltas newer than that point when reconstructing the evidence chain. The most recent relevant sequence is:

   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode correction / hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS, Blackwell ubatch and cache granularity;
   - `RESEARCH-WATCH-2026-09-04-0915.md` — v0.4.0-era baseline, parallel-MTP isolation, SSD-expert streaming and MTP-head quant;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — PP-vs-TP structural evidence, production cache-granularity failure and CUDA provenance;
   - `RESEARCH-WATCH-2026-09-04-1840.md` — stable v0.4.0 pin, modality-agnostic KV reuse, DS4 tool-observation correction and MTP draft-cache VRAM;
   - `RESEARCH-WATCH-2026-09-04-1930.md` — Flash MTP commit semantics, concurrent-PLE state isolation, Apple recurrent kernels and decoupled cache geometry;
   - `RESEARCH-WATCH-2026-09-05-0400.md` — neighboring-row QSA gather reuse, Metal `MUL_MAT` width exactness and DS4 fixed-work PP;
   - `RESEARCH-WATCH-2026-09-05-0500.md` — production-layout invariance correction, low-level runtime provenance and Strix-Halo AProjQ4 smoke;
   - `RESEARCH-WATCH-2026-09-05-1200.md` — recurrent multi-turn rollback, per-slot draft context, chunk-size-dependent AProjQ4 PP, M1/M2 FP16 activation lane and persistent-state identity;
   - `RESEARCH-WATCH-2026-09-05-1512.md` — real-agent cache-capture efficacy, independent 27B FR-Spec correction, exact ds4 CUDA scratch-reuse receipt, allocator-identity watch and TG-log provenance;
   - `RESEARCH-WATCH-2026-09-05-1943.md` — speculative-loader provenance, greedy answer equivalence, 4-bit MTP-loop behavior and first-repeat MTP cache-boundary backfill.

7. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 19:43 pass moves no row.** It adds no sustained physical receipt from the four target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 remains a separate approximate serving lane; it does not alter P69 or exact-runtime targets.
- 5070 targets require full residency and measured net VRAM/context headroom.
- DS4 remains conservative until exact sustained 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-05 19:43 ET

Starting freshness boundary: `d3e7de243bf604558e508a9a44ce5b2c0116da16` / **2026-09-05 19:18:28 UTC**.

## FRESH / material

### rMLX `7bc69130c275de3540dcfa1d39e9b71676ce3549` / #515 — speculative provenance and deterministic answer equivalence

Fresh commit time: **2026-09-05 20:18:01 UTC**.

The material Qwen3.8-27B findings are:

- a published Qwen3.8 DFlash 2 checkpoint contained a candidate selector and per-layer dynamic convolutions the loader did not support; the old path silently ignored unsupported weight families and benchmarked an earlier DFlash architecture under the checkpoint name;
- the reviewed loader now fails closed: a supported Qwen3.6 drafter consumes all 91 tensors, while the Qwen3.8 checkpoint leaves **23 unread tensors** and is refused;
- on the same verifier, the DFlash temperature-0 arm diverged from its own no-drafter verifier answer at the **fourth token**, while the MTP sidecar remained byte-identical over 160 tokens;
- first reported 4-bit Qwen3.8 MTP cells produced about **1.19x** block-2 speedup versus **1.36x** for a prior MXFP8 pair, with acceptance **0.730 vs 0.877**; block-depth profitability also became more workload-dependent after quantization.

**Promotion for the 27B speculative lane:**

1. require checkpoint/tensor-consumption provenance and fail closed on unsupported weight families;
2. at deterministic/greedy settings, require full answer equivalence against the same verifier with speculation disabled;
3. continue measuring acceptance, accepted tokens/cycle, true drafting share, TG, E2E wall and memory after every verifier/drafter quantization change.

This is runtime/speculation evidence, not an exact 5070 Ti or M1 rate receipt.

## BACKFILL / material

### `wtdcode/vllm-backport` `4995d9c7a42018246ead0624ee4d120a3149956d` — MTP first-repeat prefix hits can fail despite later cache success

Commit time **2026-09-05 17:43:37 UTC**, so this is explicitly backfill, not fresh.

Physical report: Qwen3.8-Flash-Next-AWQ, TP4 A6000, MTP3, block 1024, 13.4K-token repeated prompt.

With sparse recurrent-boundary retention, the recurrent replay boundary and the EAGLE/MTP-shifted full-attention cache boundary landed one block apart. The result was **zero cache hit on the first repeat**, with the second repeat finally succeeding after a shared-prefix junction existed.

Reported repeated-prompt sequence:

- before: 12.21 s | 9.81 s / hits 0 | 1.23 s / hits 12,288;
- after retaining the shifted boundary: 13.51 s | 1.15 s / hits 12,288 | 1.14 s / hits 12,288.

**Promotion to Flash qualification:** explicitly test first repeat, second repeat and growing-agent reuse with MTP on/off. Verify that recurrent-state retained boundaries intersect the attention-side reusable prefix. A cache that only becomes effective on the second repeat does not pass the turnkey-agent gate.

This strengthens the oMLX #3462 rule from the 15:12 pass: **cache enabled != cache effective**.

---

# Focused follow-up status

- **oMLX #3462:** still open, 0 comments; no post-cutoff maintainer change surfaced.
- **oMLX #3464:** still open, 0 comments; no post-cutoff change surfaced.
- **jundot/omlx main:** no commits after the cutoff in the checked window.
- **llama.cpp #28425:** no post-cutoff update surfaced.
- **llama.cpp #28433:** no post-cutoff update surfaced.
- **llama.cpp #28448:** no post-cutoff maintainer update surfaced; remains a monitored correctness seam, not an Apple/Flash blocker.
- **llama.cpp #25187:** latest material activity remains pre-cutoff.
- **llama.cpp main:** only unrelated repository/issue-template maintenance surfaced after the cutoff; no new Flash/Qwen rate receipt.
- **antirez/ds4 main:** no commits after the cutoff.
- **ml-explore/mlx main:** no commits after the cutoff.
- **MLX #4409:** still open; no fresh M1 result surfaced.
- **vLLM #55375:** remains merged; no fresh post-cutoff material surfaced in this pass.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG receipt or completed new exact-rig cold-PP result.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **RTX 5070 Ti 27B:** no fresh exact-card TG/PP receipt.
- **M1 Max64 27B:** no fresh exact single-M1-Max serving receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep the existing bootstrap/qualification order. Strengthen the cache gate:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent partial-prefix rollback / growing-session correctness;
3. growing coding-agent cache-capture efficacy with short completions and long reused prefixes;
4. **first-repeat / second-repeat cache effectiveness with MTP on/off and recurrent/attention boundary intersection**;
5. PLE residency/page-cache/direct-read A/B;
6. sparse-QSA wide-prefill and neighboring-row reuse;
7. QSA known-horizon reservation and recurrent-checkpoint budgeting;
8. pooled session restore / persistent identity gates;
9. MTP recurrent commit plus per-slot draft-context sizing and slot isolation;
10. activation-FP16 approximate lane only after exact baseline freeze;
11. compiled/multi-agent/long-prefill-during-decode stress.

Canonical center remains **40 TG / 400 cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Preserve full residency first-order and the full-head-quantization-before-aggressive-vocab-trim ordering.

Add two promotion gates to every external drafter experiment:

- **checkpoint completeness/provenance**;
- **greedy verifier-only answer equivalence**.

Canonical center remains **120 TG / 250 cold PP**.

## Single M1 Max64 Qwen3.8-27B

P69 remains separate: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. Do not contaminate P69 with external speculative work.

Canonical center remains **25 TG / 110 native cold PP**.

## Dual-M1 DS4-0731

No lane change. Metal scratch/temp-allocation lifecycle remains a transfer candidate; no exact dual-M1 update surfaced.

Canonical center remains **15 TG / 180 cold PP**.

---

# Standing decisions strengthened this pass

- A benchmark row named after a drafter checkpoint is not provenance; prove all required tensor families were consumed or fail closed.
- Greedy speculative decoding must be equivalent to the same verifier with speculation disabled; coherent output and acceptance are insufficient.
- Quantization can change speculative acceptance and optimal block depth materially; re-measure the full loop.
- Flash prefix-cache certification must include the **first repeat**, not merely a later warmed repeat.
- **Cache enabled != cache effective:** require advancing reusable-prefix frontier, bounded fresh-prefill work and recurrent/attention boundary compatibility under MTP.
- Existing gates remain active: ordinary recurrent rollback is separate from MTP rollback; draft context is per slot; concurrent pure-prefill state isolation is mandatory; persistent state carries tokenizer/model/runtime identity; explicit TG source + generated-token denominator are required for promoted receipts.
- Stronger/different hardware and non-bit-exact mechanisms do not move exact-machine targets by themselves.
- P69 remains isolated.
