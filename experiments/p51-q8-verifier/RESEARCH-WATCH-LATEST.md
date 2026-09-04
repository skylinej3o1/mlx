# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct
   targets from older watch-note prose when the target file has a newer calibration date.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-04-0915.md`

   **The 09:15 note is authoritative for current promotion level, safe MTP concurrency policy and
   qualification order.**

4. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain the dated
   deltas newer than that consolidation point when reconstructing the evidence chain:

   - `RESEARCH-WATCH-2026-09-03-1330.md` — broader machine-specific backfill;
   - `RESEARCH-WATCH-2026-09-03-1530.md` — Blackwell verify / M1 serving-memory findings;
   - `RESEARCH-WATCH-2026-09-03-1725.md` — DS4 AProjQ4 + request-adaptive DSpark policy;
   - `RESEARCH-WATCH-2026-09-03-1950.md` — original Flash sparse-QSA M5 measurements;
   - `RESEARCH-WATCH-2026-09-03-2205.md` — GSQ-RCO / MTP-imatrix leads;
   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode reproduction correction,
     #28349 downgrade and hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS diagnostic,
     Blackwell ubatch stability and short-turn cache granularity;
   - `RESEARCH-WATCH-2026-09-04-0915.md` — llama.cpp 0.4.0 packaging baseline, parallel-MTP
     isolation gate, Apple SSD-expert-streaming backfill and concrete MTP-head quant A/B.

5. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans remain narrow:

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer
  ownership, recurrent rollback, MTP/verification and slot isolation, QSA/PLE placement and
  residency, sparse long-context prefill, compiled decode, cache/state lifecycle, optional
  SSD-streaming controls, and multi-agent pipeline filling.
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

**The 09:15 pass does not move any row.** It changes packaging and correctness policy, not the
calibrated performance distribution.

Important qualifiers remain:

- Flash keeps its B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`;
- M1 27B ANE-assisted PP is a separate approximate lane, not P69 exact work;
- 5070 Ti targets require a fully resident target; a spilled configuration is disqualified;
- DS4 remains deliberately conservative until an exact sustained 0731 TG receipt exists.

---

# Current newest evidence delta — 2026-09-04 09:15 ET

Freshness boundary: branch checkpoint `9f24f1eabadfcad661174bc4b4bd8c126386858d` /
2026-09-04 10:43:57 UTC.

## Fresh / material

### llama.cpp 0.4.0 version bump merged

llama.cpp #28386 was created and merged after the cutoff. Its version notes collect initial
Qwen3.8-Flash-Next support, lazy/on-demand tensor reading, sparse FA infrastructure, Qwen4Exp
recurrent rollback, Qwen4Exp graph/indexer work, Apple RDMA RPC transport, RPC event/async APIs,
KV-cell state tracking, n-gram lookup and DFlash2 into one 0.4.0-era baseline.

The version notes still call Flash-Next optimization incomplete, so this is not throughput evidence.
At check time the version bump was merged but a stable GitHub `v0.4.0` release/tag was not yet
visible. For a turnkey community recipe, qualify and pin one exact 0.4.0-era build rather than
silently mixing moving-master patches.

## New-to-repo backfill / material correctness

### Parallel qwen4exp MTP requires a slot-isolation gate

llama.cpp #28286 reports plausible **cross-slot content contamination** under
`draft-mtp + --parallel > 1` with Qwen3.8-Flash-Next: one concurrent request can drift into another
slot's code/prose while still producing valid-looking text. Graph disable did not remove the
reported failure; `--parallel 1` did not reproduce it, and trivial repetitive prompts could pass.

This was reported on another backend/build and does not prove the current 0.4.0 baseline is still
affected. It does prove that casual smoke tests are insufficient.

**Safe default until the real dual-M1 gate passes: one active MTP lane at a time.** Other concurrent
work may use plain target batching, PP pipeline filling and queued/arbitrated requests. Parallel MTP
must pass distinct high-entropy prompts, temp-0 and real sampling, repeated parallel-2/4 runs,
join/leave/cancel/cache-restore cases and explicit cross-slot attribution checks before promotion.

### Recurrent rollback is a mechanism, not a parallel-safety certificate

Merged llama.cpp #28123 fixes qwen4exp recurrent rollback planes for GDN/PLE convolution history
and showed large single-slot RTX PRO 6000 speculative gains. Absolute rates do not transfer to M1.
The current policy is to A/B recurrent rollback + singleton MTP on the M1 pair, while treating
multi-slot isolation as a separate correctness problem.

## New-to-repo backfill / portable Apple mechanism

### oMLX SSD expert streaming is a useful secondary capacity lane

oMLX #3359 implements exact-routing SSD expert streaming with bounded resident expert banks,
route-frequency/LRU caches, direct Metal I/O and native-demand callbacks. An independent M5 Pro
64 GB reviewer run after correctness fixes reported Flash-Next oQ2 MTP around 32.7 GB resident and
25-28 tok/s warm. More important for architecture selection, native-demand turnaround measured
about 150 us/layer, implying roughly a 7 ms/step host-mediated floor across 48 layers even when the
needed expert rows are resident.

Therefore:

- mine direct Metal publication and PLE prefaulting techniques;
- keep exact SSD expert streaming as a **one-Mac / fallback / capacity** control;
- do not replace resident stage-owned experts with host-mediated demand in the primary dual-M1
  topology when aggregate 128 GB residency can avoid that per-layer round trip.

## Backfill / concrete 5070 candidate

### MTP-head quantization A/B

llama.cpp #28351 now gives concrete head-only agreement numbers. Q4_K + imatrix is about 240 MB
with 0.7216 agreement in the reported table, Q6_K about 350 MB / 0.7233, and BF16 about 850 MB /
0.7239. There is no direct 5070-Ti end-to-end result.

After the existing ubatch/prompt-shape stability gate, test BF16 vs Q6_K vs Q4_K+imatrix MTP heads
on the exact 5070 Ti with identical target quant, sampled acceptance, TG, VRAM, maximum healthy
context and agent-quality checks.

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** #27993 remains correctness/topology only; no sustained TG or completed 115K
  follow-up surfaced.
- **Dual-M1 DS4-0731:** #922 remains ~152 tok/s at 34,384-token prefill with no sustained TG
  denominator; #957 still has no physical exact-M1 post-coalescing result.
- **RTX 5070 Ti 27B:** the direct test repo still has `pushed_at=2026-08-20T19:16:50Z`.
- **Apple 27B external frontier:** `mlx-dspark` still has `pushed_at=2026-09-01T10:54:45Z` and
  Layr's challenge repo still has `pushed_at=2026-08-29T07:05:19Z`.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Current qualification order:

1. **Pin/certify one 0.4.0-era baseline** on both Macs.
2. Plain exact PP2/layer-owned baseline: correctness, B1/B2/B4, cold PP, long context.
3. PLE residency policy A/B: lazy/page-cache vs stage-local resident/direct-read/quantized.
4. Sparse-QSA experimental A/B.
5. Recurrent rollback + **singleton MTP** A/B at temp 0 and intended agent sampling.
6. **Parallel-MTP slot-isolation gate before any `parallel > 1` MTP serving.**
7. Compiled-decode B2/B4 E2E A/B; do not restore the non-reproduced large B1 claim.
8. Short-turn cache granularity / exact replay A/B.
9. SSD-expert-streaming/direct-I/O as a secondary capacity/control lane.
10. Combine only passing mechanisms, then run long-prefill-arrives-while-other-agents-decode stress.

PP2/layer ownership remains primary; TP2 remains a falsification/control benchmark.

**Safe serving posture now: singleton profitable MTP lane + plain concurrent work until slot
isolation is physically certified.**

Canonical working center remains **40 TG / 400 PP**.

## Dual-M1 DS4-0731

No topology or target change. Keep:

- PP2/layer ownership primary;
- TP2 control;
- current-head AProjQ4 serving candidate with AProjQ8 control;
- request/workload-adaptive speculation.

Mandatory diagnostic order remains:

1. sane/coalesced Metal mappings;
2. macOS build and command-buffer completion/wait behavior;
3. GPU-busy fraction and wired residency;
4. same-host non-distributed control;
5. then PP bubbles/interconnect and multi-session filling.

Canonical working center remains **15 TG / 180 PP**.

## Single M1 Max 64 GB Qwen3.8-27B

Canonical working center remains **25 TG / 110 native PP**. The optional ANE-assisted PP lane is
separate and quality/memory-gated. Hidden compiled ANE banks remain first-order admission memory.

P69 remains separate and unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling
only**.

## RTX 5070 Ti 16 GB Qwen3.8-27B

Canonical working center remains **120 TG / 250 PP**.

Current qualification order:

1. ubatch 256/512 + neutral/code/tool prompt-shape stability matrix;
2. Q3_K_XL + native MTP speed lane;
3. small-N Blackwell verify A/B;
4. BF16/Q6_K/Q4_K-imatrix **MTP-head** A/B for context headroom;
5. GSQ-RCO stays the separate context/quality lane.

A head-quant change promotes only if it increases usable headroom without enough acceptance/quality
loss to erase the wall-time benefit.

---

# Standing architecture decisions

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stage-local recurrent/GDN/QSA/expert state is preferred over per-token TB4 or host-mediated state
  exchange when residency permits.
- Multi-agent throughput is separate from B1 TG; independent requests can fill pipeline bubbles.
- **MTP concurrency is now a correctness-gated feature, not merely a throughput option.**
- Speculation remains workload/acceptance/sampling dependent; do not assume MTP everywhere.
- Prefix/session reuse is a separate latency objective and must not be counted as cold PP.
- Stronger-chip percentages and microbenchmarks do not move exact-machine targets by themselves.
- For the eventual community recipe, pin a physically certified runtime/release and provide a
  self-test that fails visibly on correctness, paging/residency, cross-slot leakage or broken
  lifecycle behavior.

The detailed rationale, confidence ladders and target-change rules remain centralized in
`RESEARCH-TARGETS.md`.
