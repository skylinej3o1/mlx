# External runtime research watch — 2026-09-05 19:43 ET

Starting branch checkpoint: `d3e7de243bf604558e508a9a44ce5b2c0116da16`

Starting hard freshness cutoff: **2026-09-05 19:18:28 UTC**.

Classification rule for this pass:

- **FRESH** = created, updated, commented or committed strictly after the cutoff;
- **BACKFILL** = older than the cutoff but newly surfaced and materially changes a test or interpretation;
- **KNOWN / NO CHANGE** = already represented in the research state or no post-cutoff movement.

---

# Result

This pass found **one fresh material speculative-decoding/certification result** and **one useful pre-cutoff Flash cache backfill**. It found **no new sustained physical receipt from any of the four target rigs**, so `RESEARCH-TARGETS.md` remains unchanged.

Canonical centers therefore remain:

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

---

# FRESH / material

## rMLX `7bc69130c275de3540dcfa1d39e9b71676ce3549` / #515 — speculative provenance and answer-equivalence must be first-class gates

Fresh commit time: **2026-09-05 20:18:01 UTC**, about one hour after the starting cutoff.

The commit adds Qwen3.5-family PPL work, but the material part for this project is its Qwen3.8-27B speculative-decoding audit.

### 1. A published Qwen3.8-27B DFlash checkpoint had been only partially consumed by the loader

The reported Qwen3.8 DFlash 2 checkpoint contains a candidate selector and per-layer dynamic convolutions that the runtime did not implement. The old loader nevertheless accepted the checkpoint, silently ignored unsupported weight families, built an earlier DFlash architecture and emitted benchmark rows under the published checkpoint's name.

The reviewed fix changes this from a warning to **fail closed**: the supported Qwen3.6 drafter consumes all 91 tensors and loads; the Qwen3.8 checkpoint leaves **23 unread tensors** and is refused.

**Promotion:** any external MTP/DFlash/EAGLE-style drafter adopted into the 27B lane must prove checkpoint provenance and complete tensor consumption. A benchmark row named after a checkpoint is not sufficient evidence that the checkpoint architecture was actually executed.

### 2. Greedy DFlash output diverged from its own no-drafter verifier

On the same verifier, the DFlash arm reportedly diverged from the verifier-only temperature-0 answer at the **fourth token**, while the MTP sidecar stayed byte-identical for 160 tokens.

Because greedy speculative acceptance should only emit verifier argmax tokens, this is a strong sign of a **round-loop / verification-loop correctness failure**, not merely lower drafter quality.

**Promotion:** add strict answer-equivalence to speculative certification. For deterministic/greedy runs, compare the full generated sequence against the same verifier with speculation disabled. Acceptance rate, apparent quality and TG are not enough.

### 3. First 4-bit Qwen3.8-27B MTP measurements show quantization changes the speculation optimum

Across six MTP cells against a published affine-4-bit verifier and 4-bit sidecar, block 2 reportedly paid on code and 4K prompts and only barely on prose; block 3 paid on code alone. The 4-bit pair produced about **1.19x** block-2 speedup versus **1.36x** for the prior MXFP8 pair, with acceptance falling from **0.877 to 0.730**.

The report also notes a residual of roughly one-third to two-fifths of a speculative round that a faster verifier does not remove.

**Consequence for the RTX 5070 Ti lane:** preserve the existing full-head-quantization-first ordering, but add two mandatory gates before promotion:

1. checkpoint/tensor-consumption provenance;
2. deterministic verifier-only answer equivalence.

Continue reporting acceptance, accepted tokens/cycle, true drafting share, TG, E2E wall and peak memory. Do not transfer the reported rate or optimum to the 5070 Ti: this is runtime/speculation evidence, not an exact-card receipt.

---

# BACKFILL / material

## `wtdcode/vllm-backport` `4995d9c7a42018246ead0624ee4d120a3149956d` — MTP can make the *first* repeated prefix miss even when the cache works on the second repeat

Commit time: **2026-09-05 17:43:37 UTC**, so this is older than the hard cutoff and is classified only as backfill.

Physical report:

- Qwen3.8-Flash-Next-AWQ;
- TP4 A6000;
- MTP 3;
- cache block 1024;
- 13.4K-token repeated prompt.

Under sparse recurrent-boundary retention, the implementation retained the Mamba replay boundary at `num_prompt_tokens - 1`. With EAGLE/MTP enabled, the full-attention cache lookup pruned the last matching block by one block. The recurrent and full-attention sides therefore landed exactly one block apart, so their intersection was empty on the **first repeat**. A shared-prefix junction appeared only after another request, allowing the second repeat to hit.

Reported same-prompt sequence:

| | first | second | third |
|---|---:|---:|---:|
| before | 12.21 s | 9.81 s / hits 0 | 1.23 s / hits 12,288 |
| after retaining shifted boundary | 13.51 s | 1.15 s / hits 12,288 | 1.14 s / hits 12,288 |

This is a downstream/backport implementation on NVIDIA hardware, not Apple/MLX evidence, and it does not move a target.

**Promotion to Flash qualification:** our cache test must explicitly distinguish:

- first repeated prompt;
- second repeated prompt;
- growing-agent prefix reuse;
- MTP on/off;
- recurrent-boundary and attention-prefix intersection.

A system that only begins reusing a prefix on the *second* repeat is not cache-correct/effective enough for the turnkey agent box. This sharpens, rather than replaces, the oMLX #3462 reusable-frontier gate from the 15:12 pass.

---

# Focused follow-up status

## oMLX

- #3462 (Flash real-agent boundary-capture starvation): still open, **0 comments**, no post-cutoff maintainer change surfaced.
- #3464 (benchmark log omits `gen_tps`): still open, **0 comments**, no post-cutoff change surfaced.
- `jundot/omlx` main has **no commits after 2026-09-05 19:18:28 UTC** in the checked window.

## llama.cpp

- #28425 ordinary recurrent partial rollback: no post-cutoff update surfaced.
- #28433 aggregate-vs-per-sequence MTP draft context sizing: no post-cutoff update surfaced.
- #28448 dynamic graph allocator identity: no post-cutoff maintainer update surfaced; latest issue activity remains pre-cutoff.
- #25187 FR-Spec/full-head follow-up: latest activity remains pre-cutoff.
- the only checked upstream llama.cpp commit after the cutoff was unrelated repository/issue-template maintenance; no new Flash/Qwen runtime receipt surfaced.

## ds4 / MLX / vLLM

- `antirez/ds4` main: **no commits after the cutoff**.
- `ml-explore/mlx` main: **no commits after the cutoff**.
- MLX #4409 packed `gated_delta_seq`: still open; latest activity remains pre-cutoff and no new M1 result surfaced.
- vLLM #55375 Qwen4Exp fused-PLE state-index stride fix remains merged; no fresh post-cutoff material surfaced in this pass.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash-Next:** no fresh sustained exact 2x M1 Max64/TB4 TG or cold-PP receipt; no completed new long-context exact-rig rate.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on the exact dual-M1/TB4 topology.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact-card TG/PP receipt.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1 serving receipt.

---

# Current consequences

## Flash-Next / dual M1

Keep the existing bootstrap and qualification order. Strengthen the cache section so the first repeat is a required hit/effectiveness check, not merely the second repeat or a later warmed session. Continue treating `cache enabled != cache effective` as a first-class rule.

Canonical center remains **40 TG / 400 cold PP**.

## Qwen3.8-27B / RTX 5070 Ti

The speculative lane now requires **loader/checkpoint provenance** and **greedy answer equivalence** in addition to the existing acceptance / accepted-tokens-per-cycle / true-drafting-share / TG / wall / memory metrics.

Canonical center remains **120 TG / 250 cold PP**.

## Qwen3.8-27B / M1 and P69

No P69 experiment order change. **P69B12 remains frozen/promoted; P69B13 remains next from existing profiling only.** Do not import this external speculative evidence into P69 exact verifier optimization.

## DS4

No lane change. The existing Metal scratch/temp-allocation transfer candidate remains; no new exact dual-M1 evidence surfaced.

---

# Standing decisions strengthened by this pass

- A named checkpoint is not evidence that its full architecture ran: speculative loader provenance must prove all required tensors/weight families were consumed or fail closed.
- Greedy speculative decoding must be byte/token-equivalent to the same verifier with speculation disabled; coherent output and acceptance are insufficient.
- Quantization can change the optimal speculative block depth and acceptance materially; re-measure the full loop after changing verifier or drafter quantization.
- Flash prefix-cache qualification must include the **first repeat**, not only later warmed repeats, and must verify recurrent-state boundaries intersect the attention-side reusable prefix under MTP.
- `cache enabled != cache effective` remains the governing agent-serving rule.
- No rate/target moves without exact physical evidence from the target topology or an exceptionally strong explicit justification.
- P69 remains isolated.
