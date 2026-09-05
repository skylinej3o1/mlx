# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct targets from older watch-note prose.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1512.md`

   **The 15:12 note is authoritative for current agent-turn cache-capture efficacy, Qwen3.8-27B MTP-head/vocabulary experiment ordering, ds4 reusable-scratch transfer, allocator-identity monitoring and benchmark-TG provenance.**

4. The immediately previous delta remains important for ordinary recurrent rollback, per-slot MTP context sizing, DS4 fresh-prefill semantics, M1/M2 FP16 activation experimentation and persistent-cache identity:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1200.md`

5. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain dated deltas newer than that point when reconstructing the evidence chain. The most recent relevant sequence is:

   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode correction / hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS, Blackwell ubatch and cache granularity;
   - `RESEARCH-WATCH-2026-09-04-0915.md` — v0.4.0-era baseline, parallel-MTP isolation, SSD-expert streaming and MTP-head quant;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — PP-vs-TP structural evidence, production cache-granularity failure and CUDA provenance;
   - `RESEARCH-WATCH-2026-09-04-1840.md` — stable v0.4.0 pin, modality-agnostic KV reuse, DS4 tool-observation correction and MTP draft-cache VRAM;
   - `RESEARCH-WATCH-2026-09-04-1930.md` — Flash MTP commit semantics, concurrent-PLE state isolation, Apple recurrent kernels and decoupled cache geometry;
   - `RESEARCH-WATCH-2026-09-05-0400.md` — neighboring-row QSA gather reuse, Metal `MUL_MAT` width exactness and DS4 fixed-work PP;
   - `RESEARCH-WATCH-2026-09-05-0500.md` — production-layout invariance correction, low-level runtime provenance and Strix-Halo AProjQ4 smoke;
   - `RESEARCH-WATCH-2026-09-05-1200.md` — recurrent multi-turn rollback, per-slot draft context, chunk-size-dependent AProjQ4 PP, M1/M2 FP16 activation lane and persistent-state identity;
   - `RESEARCH-WATCH-2026-09-05-1512.md` — real-agent cache-capture efficacy, independent 27B FR-Spec correction, exact ds4 CUDA scratch-reuse receipt, allocator-identity watch and TG-log provenance.

6. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 15:12 pass moves no row.** It changes serving certification and experiment ordering, but adds no sustained physical receipt from the four target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 remains a separate approximate serving lane; it does not alter P69 or exact-runtime targets.
- 5070 targets require full residency and measured net VRAM/context headroom.
- DS4 remains conservative until exact sustained 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-05 15:12 ET

Starting freshness boundary: `10523b862796ac4d53a034305e1d307075fd45b8` / 2026-09-05 16:04:52 UTC.

## Fresh / material

### oMLX #3462 — effective prefix reuse is now a first-class agent metric

A physical M3-Ultra/Flash-Next long-running coding-agent report measured a **68% cache-store skip rate** under the 2,048-token ArraysCache boundary rule. Average prompts/completions were about 99,246 / 535 tokens. Prompts grew 94K -> 148K while reusable prefix stayed fixed at 12,288 tokens, causing about 80K repeated prefill tokens per turn.

MTP can compound exact-boundary misses because scheduler steps advance by multiple tokens. Do not lower the 2,048 prefill step casually: it is tied to recurrent-state materialization correctness.

**Promotion:** add an agent-turn cache-capture efficacy gate recording successful stores/skips, reusable-prefix frontier, reused/fresh tokens, warm TTFT/wall, completion length and MTP stride. `Cache enabled` or raw hit count is not sufficient.

### llama.cpp #25187 fresh Qwen3.8-27B follow-up — full-head quality can beat aggressive FR-Spec trimming

An independent Qwen3.8-27B 192K-context comparison reports the 32K FR-Spec draft vocabulary at about 60.6-60.8% long-context acceptance and 104.5-105.6 TG, versus **70.9% / 112.6 TG** for a cross-file full Q5_K head. Internal IQ4_XS full head was 68.1% / 109.7. The 32K trim could still win about 5% wall time on some short interactive prompts.

**Promotion for RTX5070Ti:** test full-head MTP quantization before aggressive 32K trimming. Judge speculation by acceptance, accepted tokens/cycle, TG, E2E wall and memory, not draft-head kernel time alone. FR-Spec stays a memory/workload-specific candidate. Different hardware; no 5070 target move.

### ds4 `b42682f` / `9ab7053` — exact reusable-scratch decode win on DGX Spark

Fully resident Flash-0731 Q2, no speculation, three interleaved medians after warmup:

| Context | Before | After | Gain |
|---|---:|---:|---:|
| 2K | 17.90 | 19.25 | +7.5% |
| 4K | 15.23 | 16.22 | +6.5% |
| 8K | 15.01 | 15.97 | +6.4% |

Prefill stayed essentially unchanged. Full prefill/post-decode logits and the 100-case continuation score were unchanged. The change reuses aligned Q8 scratch instead of repeated CUDA pool allocation.

**Transfer:** inspect Metal projection/QMV decode for equivalent per-step scratch allocation or temporary construction. Promote only via exact M1 A/B; this CUDA/GB10 result is not an M1 ruler.

### llama.cpp #28448 — dynamic graph allocation identity becomes a monitored correctness seam

A new sparse-MoE report shows `ggml_gallocr` can reuse a stale same-size allocation plan when the logical tensor at a graph position changes. Two physical sparse-MoE reproductions were reported, including a CPU-only Gemma control and a Qwen3-MoE case, with silent incoherent output rather than a crash.

**Policy:** monitor rather than block. If Qwen4Exp dynamically changes decode topology/expert graph identity, add a route-change/full-logit oracle versus forced reallocation/reference. Do not infer Apple impact without a relevant reproduction.

### oMLX #3464 — benchmark log line can omit computed TG

`[benchmark-pp-result]` currently logs PP/TTFT/E2E/cached tokens but not the already-computed generation TPS. Missing TG in that line must not be reverse-engineered into a measured rate. Promotion receipts require explicit TG and generated-token denominator/structured result.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG receipt or completed long-context exact result surfaced.
- **Dual-M1 DS4-0731:** fresh ds4 evidence is other hardware; no new sustained generated-token denominator on 2x M1 Max64/TB4 surfaced.
- **RTX 5070 Ti 27B:** no new exact-card TG/PP receipt surfaced; FR-Spec evidence changes test ordering only.
- **M1 Max64 27B:** no new exact single-M1-Max serving receipt surfaced.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Qualification order now explicitly includes:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent partial-prefix rollback / growing-session gate;
3. **growing coding-agent cache-capture efficacy** with short completions and long reused prefixes;
4. PLE residency/page-cache/direct-read A/B;
5. sparse-QSA wide-prefill and neighboring-row reuse;
6. QSA known-horizon reservation and recurrent-checkpoint budgeting;
7. pooled session restore / persistent identity gates;
8. MTP recurrent commit plus **per-slot draft-context sizing** and slot isolation;
9. activation-FP16 approximate lane only after exact baseline freeze;
10. compiled/multi-agent/long-prefill-during-decode stress.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

PP2/layer ownership remains primary; TP2 remains control; AProjQ4 remains the primary projection candidate. Keep cold/full PP separate from incremental-agent PP.

Add a profile check for per-step Metal scratch/temp allocation in projection/QMV decode. The DGX Spark result is mechanism transfer only.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

P69 remains separate: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

FR-Spec/full-head evidence is not an M1 receipt. If an external MTP head is later adopted, test head quantization/acceptance before aggressive vocabulary trimming.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Preserve full residency first-order.

Updated speculative order:

1. native/full-head MTP baseline;
2. full-head head-quantization A/B with memory/context headroom recorded;
3. Blackwell ubatch/prompt-shape and small-N verifier stability;
4. then 32K FR-Spec or other vocab trim as memory/workload-specific alternative;
5. compare acceptance, accepted tokens/cycle, true drafting share, TG, E2E wall and peak memory.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing decisions strengthened this pass

- **Cache enabled != cache effective:** require reusable-prefix frontier advancement and bounded fresh-prefill work in real agent sessions.
- Short-output recurrent agents are an adversarial cache workload; MTP stride must be included in the cache-capture test.
- Draft-head compute savings are not the objective function; acceptance/verification work can dominate E2E speculation.
- Prefer full-head MTP quantization before aggressive vocabulary trimming on the 5070 Ti unless memory pressure forces the latter.
- Per-step scratch/allocation lifecycle is a decode profiling candidate; the current exact receipt is CUDA-only.
- Dynamic graph allocation identity is a correctness watch item, not yet a Qwen4Exp/Apple blocker.
- Every promoted benchmark receipt requires an explicit TG source and denominator.
- All 12:00 decisions remain active: ordinary recurrent rollback is distinct from MTP rollback; draft context is per slot; PP semantics record fresh increment size; persistent state carries tokenizer/model/runtime identity; approximate FP16 activation lanes remain separate from exact-runtime evidence.
- Stronger/different hardware and non-bit-exact mechanisms do not move exact-machine targets by themselves.
- P69 exact verifier work remains isolated from external serving/runtime research.
