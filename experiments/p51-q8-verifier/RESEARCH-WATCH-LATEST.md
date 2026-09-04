# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct
   model targets from older watch-note prose when the target file has a newer calibration date.

3. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-04-0625.md`

4. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, also read every
   dated `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   evidence chain. In particular retain:

   - `RESEARCH-WATCH-2026-09-03-1330.md` — broader machine-specific backfill;
   - `RESEARCH-WATCH-2026-09-03-1530.md` — Blackwell verify / M1 serving-memory findings;
   - `RESEARCH-WATCH-2026-09-03-1725.md` — DS4 AProjQ4 + request-adaptive DSpark policy;
   - `RESEARCH-WATCH-2026-09-03-1950.md` — original Flash sparse-QSA M5 measurements;
   - `RESEARCH-WATCH-2026-09-03-2205.md` — GSQ-RCO / MTP-imatrix leads;
   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode reproduction correction,
     #28349 downgrade and hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS diagnostic,
     Blackwell ubatch stability and short-turn cache granularity.

5. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans remain narrow:

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer
  ownership, MTP/verification, QSA/PLE placement and residency, sparse long-context prefill,
  compiled-decode experiments, cache/state lifecycle and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — distributed decode, PP-vs-TP, Metal shard
  mapping, command-buffer/OS behavior, sparse-attention/activation economics, speculation policy,
  multi-session bubble fill and portable pre-M5 Metal work.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel
  work, ANE prefill economics, cache/session granularity and serving-memory/admission behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit
  fit, native MTP/DFlash, MTP-head quantization, Blackwell verify kernels/stability, context
  headroom and coding/tool throughput.

Other machines should be promoted only when they expose a mechanism likely to transfer into one of
those four hardware lanes.

---

# Canonical target calibration — 2026-09-04 06:40 ET

These are mature-system engineering probabilities, not statistical confidence intervals. Full
threshold ladders and assumptions live in `RESEARCH-TARGETS.md`.

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Important qualifiers:

- Flash retains its previous B1 TG ladder and ~128K ladder; the new work formalizes the **PP
  probability ladder** around the prior 400+ design target.
- M1 27B PP above is the native/exact-runtime planning lane. Experimental ANE-assisted PP has a
  separate ladder because the demonstrated ANE path uses approximate INT8 work; it must not be
  called P69/exact merely because one benchmark preserved top-1.
- 5070 Ti targets assume a **fully resident Q3-class target**. Spilled higher-bit configurations do
  not count as target candidates.
- DS4 remains intentionally conservative: the exact-hardware pre-0731 decode anchor is only
  ~10-13 tok/s, while current 0731 has exact distributed PP evidence but no sustained TG receipt.

The target recalibration is a planning normalization across all three model families. It does not
claim that the 06:25 search pass itself produced new exact Flash/DS4 TG measurements.

---

# Current newest evidence delta — 2026-09-04 06:25 ET

Freshness boundary: branch checkpoint `7672162d1ae45a90a6a10fe6d1457bdcd7cf8057` /
2026-09-04 05:21:00 UTC.

Material findings:

- **Flash PLE residency:** llama.cpp #28355 confirms the ~27 GiB
  `per_layer_token_embd` / n-gram table can be lazy under `--lazy-mode auto`; `--no-mmap` alone
  does not force it resident. Reported prefill fell roughly **2400 -> 1000 tok/s** after page-cache
  eviction from competing activity. Every Flash PP measurement must record PLE placement/lazy mode
  and page-cache condition.
- **DS4 mapping is necessary but not sufficient:** fresh #845 two-M3-Ultra evidence on macOS 27
  Beta 8 remained around **0.16 tok/s** even after locally reducing ~156 Metal shard buffers to 4.
  GPU busy time was tiny versus wall time, with stable residency and negligible wire traffic.
  Distributed qualification must therefore record OS build and command-buffer completion behavior
  in addition to map coalescing.
- **Blackwell stability:** llama.cpp #28377 reports prompt/content-dependent qwen4exp
  `cublasGemmEx` prefill failures on GB10 at ubatch 512; ubatch 256 passed the reporter's sweep and
  failing HumanEval-shaped prompt. Add prompt-shape + ubatch fuzzing to the 5070-Ti promotion gate;
  do not transfer the GB10 failure rate or speed numerically.
- **Short-turn state granularity:** oMLX #3430 shows 2048-token whole-block cache commits can miss
  reusable short turns; smaller 256/128/64 blocks reduce repeat latency at higher cold boundary
  cost. Exact assistant serialization also changes reusable-prefix length.
- **Lifecycle:** oMLX #3431 shows a stop command can report success while process/port/Metal memory
  remain live. Stop/reload qualification must verify actual resource release.

No fresh sustained physical 2x-M1 Flash-Next TG or DS4-0731 TG surfaced. #922 remains the exact
0731 cluster PP anchor at ~152 tok/s for 34,384 tokens with no generated-token denominator. The
direct 5070-Ti repo remains the primary speed ruler.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Bring-up order:

1. plain exact PP2/layer-owned baseline;
2. PLE residency policy A/B: lazy/page-cache vs stage-local resident/direct-read/quantized;
3. sparse-QSA experimental A/B;
4. compiled-decode A/B using real end-to-end B1/B2 serving metrics;
5. short-turn cache granularity / exact replay A/B;
6. combine only passing mechanisms, then test long-prefill-arriving-while-other-agents-decode.

PP2/layer ownership remains primary; TP2 remains a falsification/control benchmark. The canonical
working center is **40 TG / 400 PP**.

## Dual-M1 DS4-0731

Keep:

- PP2/layer ownership primary;
- TP2 control;
- current-head AProjQ4 primary serving candidate with AProjQ8 control;
- request/workload-adaptive speculation.

Mandatory diagnostic gate before interpreting TG/PP:

1. sane/coalesced Metal shard mapping;
2. macOS build and command-buffer completion/wait behavior;
3. GPU-busy fraction and wired residency;
4. same-host non-distributed control;
5. only then PP bubbles/interconnect and multi-session filling.

Canonical working center: **15 TG / 180 PP**.

## Single M1 Max 64 GB Qwen3.8-27B

Canonical working center: **25 TG / 110 native PP**. The optional ANE-assisted PP lane is separate
and quality/memory-gated. Hidden compiled ANE banks remain first-order admission memory; record full
system/process high-water, not only MLX-active memory.

P69 remains separate and unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling
only**.

## RTX 5070 Ti 16 GB Qwen3.8-27B

Canonical working center: **120 TG / 250 PP**.

Keep:

- speed lane = Q3_K_XL + native MTP + small-N Blackwell verify work;
- context/quality lane = GSQ-RCO controls;
- prompt-shape/ubatch stability matrix before speed promotion;
- fit is first-order: a quant/runtime that spills is disqualified regardless of nominal quality.

---

# Standing architecture decisions

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stage-local recurrent/GDN/QSA state is preferred over per-token TB4 state exchange.
- Multi-agent throughput must be measured separately from B1 TG; independent requests may fill
  bubbles even when one dependent stream cannot.
- Speculation is workload/acceptance/sampling dependent; do not assume MTP everywhere.
- Prefix/session reuse is a separate latency objective and must not be counted as cold PP.
- Stronger-chip percentages and microbenchmarks do not move exact-machine targets by themselves.

The detailed rationale, confidence ladders and target-change rules are now centralized in
`RESEARCH-TARGETS.md`.
