# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct
   targets from older watch-note prose when the target file has a newer calibration date.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-04-1840.md`

   **The 18:40 note is authoritative for current promotion level, topology preference, cache/session
   policy, DS4-agent diagnosis and 5070 qualification order.**

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
   - `RESEARCH-WATCH-2026-09-04-0915.md` — 0.4.0-era packaging baseline, parallel-MTP isolation
     gate, Apple SSD-expert-streaming backfill and MTP-head quant A/B;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — PP-vs-TP structural evidence, production coding-agent
     cache-granularity failure, CUDA link/runtime preflight and first #973 classification;
   - `RESEARCH-WATCH-2026-09-04-1840.md` — stable v0.4.0 pin correction, modality-agnostic KV reuse,
     DS4 tool-observation correction, MTP draft-cache VRAM economics and CUDA-graph co-residence.

5. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer
  ownership, recurrent rollback, MTP/verification and slot isolation, QSA/PLE placement and
  residency, sparse long-context prefill, compiled decode, cache/state lifecycle, exact session
  reuse, optional SSD-streaming controls, and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — sustained distributed decode, PP-vs-TP,
  Metal shard mapping, command-buffer/OS behavior, AProjQ4, speculation policy, multi-session bubble
  fill, agent-shell tool-result behavior, compaction and exact prefix reuse.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel
  work, ANE prefill economics, workload-aware cache/session granularity and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit
  fit, native MTP/DFlash, MTP-head and draft-cache quantization, Blackwell verify kernels/stability,
  exact CUDA build/runtime provenance, net VRAM/context headroom and coding/tool throughput.

Other machines promote only when they expose a mechanism likely to transfer into one of those four
hardware lanes.

---

# Canonical target calibration — unchanged

Full threshold ladders and assumptions live in `RESEARCH-TARGETS.md`.

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 18:40 pass moves no row.** It changes reproducibility, agent/session policy and exact-5070
qualification hygiene, not the calibrated exact-rig performance distribution.

Important qualifiers remain:

- Flash keeps its short/medium B1, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`;
- M1 27B ANE-assisted PP is a separate approximate lane, not P69 exact work;
- 5070 Ti targets require a fully resident target and **measured net VRAM headroom**;
- DS4 remains conservative until an exact sustained 0731 dual-M1 TG receipt exists.

---

# Current newest evidence delta — 2026-09-04 18:40 ET

Freshness boundary: `621bcd5352c1ef7430fecf3cf8f1715f1c83ac97` /
2026-09-04 19:59:18 UTC.

## Fresh / material

### DS4 #977 — exact KV reuse across text → image → appended-image turns

Fresh Apple Metal validation reports:

- first image appended: **18,073 / 18,435 prompt tokens reused**;
- second image appended: **18,807 / 19,079 reused**.

This is not dual-M1 rate evidence. It strengthens a serving decision: exact compatible
prefix/session state is a **first-class agent latency path**, including modality transitions, and is
separate from cold PP. Conditioning must be validated and changed/moved/removed image state must
rewind before the affected span.

### llama.cpp #28404 — co-resident Blackwell process + CUDA-graph interaction isolated

Fresh post-cutoff completion of a 2x2 experiment on dual RTX 5060 Ti / sm_120 found fatal CUDA errors
only in the **dual co-resident server + CUDA graphs ON** cell. Single-server graphs-on was stable;
dual graphs-off and single graphs-off were stable. `GGML_CUDA_DISABLE_GRAPHS=1` removed the fatal
errors there with no measurable cost above the two-block noise floor.

Mechanism transfer only. Keep graphs enabled for the normal single-5070 lane unless exact evidence
says otherwise. If future serving uses multiple co-resident CUDA processes/devices, add a graphs
on/off stress gate.

### llama.cpp #28378 — MTP draft-cache quantization can worsen net VRAM

Fresh independent corroboration says the same counterintuitive effect is observed and adds that
DFlash did not show it in that user's check.

The PR's Qwen3.8-27B / 16-GB example at 64K context reports:

- draft KV unquantized: CUDA compute buffer **126.77 MiB**, total GPU use ~**15,573 MiB**;
- q8 draft K/V: CUDA compute buffer **374.03 MiB**, total GPU use ~**15,711 MiB**.

Absolute figures do not transfer to the exact 5070 Ti unless reproduced. The policy does: never
assume `-ctkd/-ctvd` creates free headroom. Measure **net VRAM, workspace, acceptance, TG and maximum
healthy context**, and include DFlash as a draft-memory control.

## Backfill / correction

### DS4 #969 refines the #973 “1.9K context full” diagnosis

Pre-cutoff PR #969 says DeepSeek text-only tool observations could fail without a loaded vision
encoder because the multimodal append path required vision for every tool/user append. The failed
tool-result commit could then fall into spurious compaction ending in `context full after
compaction`.

That matches #973 closely. Corrected classification:

> **tool-observation path first; compaction second; not a model-context ceiling unless a post-fix
> physical reproduction proves otherwise.**

The DS4-agent shell gate must cover text-only tool results with/without vision, large tool payloads,
repeated post-compaction tools and continuation after summary rebuild.

### oMLX #3439 supplies the explicit cache-block knob implied by #3443

Pre-cutoff implementation backfill: explicit ArraysCache block-size override, independent of
prefill step size. This confirms the practical route for the existing policy: sweep 64/128/256/etc
against real short-turn traffic instead of deriving cache granularity from system RAM.

### Stable llama.cpp `v0.4.0` exists — search-lag correction

GitHub shows stable **`v0.4.0`**, published **2026-09-04 19:56:47 UTC**, targeting
`427291b5b34cd914a31b3fd3b61a68f6184f4b9f`. That is ~2.5 minutes before the previous cutoff, so
this is a correction to the 15:50 note rather than fresh evidence.

Use the stable tag/exact commit as the first reproducible community baseline candidate. The release
itself still calls Qwen3.8-Flash-Next support initial and says optimization work is pending, so the
tag does **not** promote throughput claims.

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** no new sustained exact TG or completed long-context exact follow-up surfaced.
- **Dual-M1 DS4-0731:** no sustained generated-token denominator beyond existing evidence surfaced.
- **RTX 5070 Ti 27B:** direct repo remains `pushed_at=2026-08-20T19:16:50Z`.
- **Apple 27B:** `mlx-dspark` remains `pushed_at=2026-09-01T10:54:45Z`; Layr remains
  `pushed_at=2026-08-29T07:05:19Z`.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Qualification order:

1. pin/certify **llama.cpp `v0.4.0` / exact tagged commit** on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. PLE residency/page-cache/direct-read policy A/B;
4. sparse-QSA wide-prefill A/B;
5. pooled QSA-prefix retention / rollback correctness;
6. recurrent rollback + **singleton MTP** A/B;
7. adversarial parallel-MTP slot-isolation gate before MTP concurrency >1;
8. compiled-decode B2/B4 end-to-end A/B;
9. workload-derived cache granularity + exact prefix/session reuse;
10. SSD expert streaming only as secondary capacity/control lane;
11. combine passing mechanisms, then multi-agent long-prefill-during-decode stress.

Safe serving posture remains: profitable singleton MTP lane + plain concurrent work until slot
isolation is physically certified.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

Keep:

- **PP2/layer ownership primary; TP2 control**;
- AProjQ4 primary serving candidate, AProjQ8 control;
- request/workload-adaptive speculation;
- Metal mapping + OS build + command-buffer completion + GPU-busy + residency diagnostic gate;
- separate agent-shell qualification for tool observation, compaction and exact session reuse.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

Canonical center remains **25 TG / 110 native cold PP**. Cache block size remains workload-selected;
ANE-assisted PP remains a separate approximate lane with hidden-bank admission accounting.

P69 remains separate and unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling
only**.

## RTX 5070 Ti16 Qwen3.8-27B

Current qualification order:

1. CUDA build/link/runtime provenance preflight;
2. ubatch 256/512 + neutral/code/tool prompt-shape stability matrix;
3. fully resident Q3_K_XL + native MTP speed lane;
4. **MTP draft-cache memory A/B: unquantized vs q8; measure net VRAM/workspace/max context**;
5. DFlash draft-memory/speed control;
6. small-N Blackwell verify A/B;
7. BF16/Q6_K/Q4_K-imatrix MTP-head A/B;
8. GSQ-RCO context/quality controls;
9. if multiple co-resident CUDA server processes are ever used, CUDA-graphs on/off stress.

Canonical center remains **120 TG / 250 PP**.

---

# Standing architecture decisions

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stable llama.cpp `v0.4.0` is now available as a reproducible baseline candidate; its release
  status does not imply optimized Flash throughput.
- Stage-local recurrent/GDN/QSA/expert state is preferred over per-token TB4 or host-mediated state
  exchange when residency permits.
- Multi-agent throughput is separate from B1 TG; independent requests can fill pipeline bubbles.
- MTP concurrency is correctness-gated, not merely throughput-gated.
- **Cache granularity is workload geometry.** Do not derive it from RAM size alone.
- Prefix/session reuse is a separate latency objective and must not be counted as cold PP.
- DS4 #973 should be debugged through the **tool-observation path before compaction**.
- On 16-GB NVIDIA, **nominally smaller draft KV can consume more total VRAM**; net residency and
  maximum healthy context decide promotion.
- CUDA benchmark provenance includes the actually linked runtime libraries; co-resident process
  configurations get their own graph-stability gate.
- Stronger-chip percentages and microbenchmarks do not move exact-machine targets by themselves.
- The eventual community recipe should fail visibly on correctness, paging/residency, cross-slot
  leakage, lifecycle, cache starvation, tool-observation failure or compaction corruption.

The detailed rationale, confidence ladders and target-change rules remain centralized in
`RESEARCH-TARGETS.md`.
