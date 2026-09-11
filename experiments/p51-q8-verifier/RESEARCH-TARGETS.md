# Runtime TG / PP Targets and Planning Confidence

Calibrated: **2026-09-04 06:40 ET**  
Target-definition correction: **2026-09-10 ET**

This is the canonical planning-target file for the three recurring model families:

1. Qwen3.8-Flash-Next on the planned **2x M1 Max 64 GB / Thunderbolt 4** cluster.
2. Qwen3.8-27B on **one M1 Max 64 GB**, with the user's **RTX 5070 Ti 16 GB + 64 GB host** kept as a separate hardware lane.
3. DeepSeek-V4-Flash-0731 / DS4 on the same **2x M1 Max 64 GB / Thunderbolt 4** cluster.

These probabilities are **engineering planning confidence**, not statistical confidence intervals.
They answer: *after the currently known high-leverage runtime work is implemented and qualified,
how likely is the mature system to sustain at least this rate on the named hardware?*

Definitions:

- **TG** = sustained generation/decode throughput. For Flash-Next, the headline working target in this
  file is explicitly a **~128K active-context B1** target. For other rows, and for Flash secondary
  calibration ladders, the context regime is stated locally.
- **PP** = cold prompt-processing/prefill throughput for a realistic uncached agent/document prompt,
  with prefix reuse disabled for the measurement. Tiny `pp512` microbenchmarks are not used as
  production PP rulers.
- For cluster PP, long enough prompts are assumed to permit useful chunk/pipeline overlap.
- Prefix/session reuse is a separate latency objective and should not be folded into cold PP.
- A target can move only when new direct physical evidence or a materially stronger mechanism case
  changes the planning distribution. Mechanism transfer alone should normally change the test plan,
  not silently become a measured rate.
- **Context is part of target identity.** A short/medium-context rate must never silently substitute
  for the ~128K Flash headline target.

## 2026-09-10 target-definition correction

The original 2026-09-04 normalization file accidentally made the Flash executive **40 tok/s** row
look like a short/medium-context target while also placing a lower probability ladder under the
~128K subsection. Subsequent project discussion clarified that the intended headline system goal is:

> **Qwen3.8-Flash-Next, quality-preserving Q5-class / eventual ~5.x-BPW weights, PP2 on 2x M1 Max
> 64 GB over TB4, ~128K active context: ~40 tok/s sustained TG, with ~400 tok/s realistic cold PP.**

This correction is **not** an evidence-driven downgrade and then re-upgrade. No negative exact-target
measurement forced 40 -> 30. It restores the intended denominator for the existing goal.

The 40 @ ~128K number remains a **planning target / hypothesis**, not a measured dual-M1 receipt.
The September 10 r/oMLX backfill adds useful stronger-Apple long-context transfer receipts (including
30+ tok/s-class 120K-150K harness use and a separate warm ~40 tok/s report), but those do not become
exact M1-Max/TB4 evidence.

---

## Executive working targets

| Model / hardware lane | Working TG target | Confidence / status | Working cold PP target | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Interpretation: these are the numbers to optimize toward in planning and experiment selection. They
are deliberately not the 90%-confidence floors and not the low-probability stretch ceilings.

---

# 1. Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4

## TG — headline target is B1 at ~128K active context

**Working target: 40 tok/s sustained TG at approximately 128K active context.**

This is the real interactive-system objective. Reaching ~40 tok/s only at tiny or short/medium
context while collapsing to ~20 tok/s near 128K does **not** count as meeting the headline goal.

Useful success interpretation for the mature system:

| ~128K sustained B1 TG | Interpretation |
|---:|---|
| <25 tok/s | material miss / architecture or implementation problem |
| 25-30 tok/s | partial success, useful but below the intended experience |
| 30-35 tok/s | excellent practical result |
| 35-40 tok/s | strong success |
| **>=40 tok/s** | **headline target met; validates the main dual-M1 Flash thesis** |

Why 40 remains the goal rather than a measured claim:

- single-M1 Flash-Next target-only work is around ~10-13 tok/s in the known tuned lane;
- native MTP has reached roughly ~18-22 tok/s on one M1 Max depending on context/configuration;
- PP2/layer ownership can reduce per-node target work without requiring a chatty TP collective;
- selected-KV/QSA, request-adaptive verify width, compiled low-occupancy decode, better cache/state
  lifecycle and stage-local recurrent state remain real seams;
- stronger-Apple transfer evidence now includes real 120K-150K harness usage in the 30+ tok/s class
  and a separate warm-session ~40 tok/s report, strengthening plausibility without proving the exact
  two-M1 target lane;
- there is still no sustained exact physical 2x-M1 Flash TG receipt at ~128K, so this remains an
  engineering target rather than a measured result.

### Historical September 4 ~128K confidence ladder — retained for provenance, not target definition

The original normalization captured this evidence-confidence ladder:

| Mature B1 TG | Historical confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

Retain it as a record of the **2026-09-04 evidence calibration**. It must not be read as saying the
project target is 30 tok/s. The later clarification restored the intended **40 tok/s @ ~128K** goal,
and exact-target confidence for that goal should be recalibrated only when stronger evidence warrants it.

### Short/medium B1 — secondary calibration only

| Mature B1 TG | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

This ladder remains useful for bring-up and regression diagnosis, but it is **not** the headline Flash
target. A mature system that reaches 40 here but misses badly at ~128K has not completed the goal.

## Cold PP — realistic long agent/document prompts

| Mature cold PP | Confidence |
|---|---:|
| >=250 tok/s | ~95% |
| >=300 tok/s | ~85% |
| >=350 tok/s | ~70% |
| **>=400 tok/s** | **~55-60%** |
| >=450 tok/s | ~40% |
| >=500 tok/s | ~25% |
| >=600 tok/s | ~10% |

**Working target: 400 tok/s cold PP.**

Rationale:

- reproducible single-M1 Flash-Next prefill has been roughly ~150-180+ tok/s in older custom
  llama.cpp configurations;
- sufficiently long prompts can pipeline chunks across a balanced PP2 split, so cluster PP has a
  much stronger scaling case than B1 decode;
- gathered-QSA prefill and sparse selected-K/V are structurally favorable;
- the ~27 GiB PLE/n-gram table can make PP vary dramatically depending on residency/page-cache
  state, so this target assumes an explicitly qualified PLE policy rather than accidental warm
  page cache;
- stronger-hardware 800-900+ tok/s gathered-prefill receipts show substantial implementation
  headroom but are not numerically transferred to M1.

Qualification rule: every Flash PP result must record PLE lazy/resident mode, page-cache condition,
competing I/O, stage placement, prompt length, prefill chunking and actual TB4 traffic.

---

# 2. Qwen3.8-27B — M1 Max 64 GB

The certified P69 exact-verifier campaign remains separate. P69B12 stays frozen/promoted and
P69B13 remains next from existing profiling only. The targets below are production-runtime planning
numbers and do not alter P69 certification.

## TG

| Mature B1 TG | Confidence |
|---|---:|
| >=20 tok/s | ~95% |
| >=22 tok/s | ~80% |
| **>=25 tok/s** | **~55-60%** |
| >=28 tok/s | ~30% |
| >=30 tok/s | ~15% |

**Working target: 25 tok/s.**

Anchors:

- the frozen exact-Q8 P69 ruler is already about **19.55 tok/s** at ~29K context;
- practical 4-bit M1 Max serving receipts sit around high teens B1 and fall with context;
- a separate DFlash 4-bit receipt has reached ~23.5 tok/s at 32K;
- there is still plausible headroom in verifier/projection/GDN scheduling, but 30 tok/s should remain
  a stretch until direct M1 evidence moves it.

## Cold PP — native/exact-runtime planning lane

| Mature native PP | Confidence |
|---|---:|
| >=85 tok/s | ~95% |
| >=100 tok/s | ~80% |
| **>=110 tok/s** | **~60%** |
| >=125 tok/s | ~35% |
| >=140 tok/s | ~15% |

**Working native/exact-runtime PP target: 110 tok/s.**

Recovered direct M1-Max evidence provides a useful calibration: `mlx-community/Qwen3.8-27B-4bit`
on M1 Max 64 GB measured **84.6 tok/s** standard-GPU prefill at 2,048 tokens. An experimental
40% ANE / 60% GPU path measured **112.2 tok/s**, but that path uses approximate INT8 ANE work and
is therefore not an exact-runtime replacement merely because the tested top-1 token matched.

### Optional ANE-assisted production lane

If approximation/quality and memory gates are accepted, use a separate PP ladder:

| Mature ANE-assisted PP | Confidence |
|---|---:|
| >=110 tok/s | ~85% |
| >=125 tok/s | ~60% |
| >=140 tok/s | ~35% |
| >=160 tok/s | ~15% |

Do **not** merge this ladder into P69 or call it exact. ANE admission must include hidden compiled-bank
memory; process RSS/MLX-active alone is insufficient.

Source anchor: Blaizzy/mlx-vlm #1943, M1 Max 64 GB, Qwen3.8-27B-4bit, 2,048-token prefill,
84.6 -> 112.2 tok/s with hybrid ANE/GPU.

---

# 3. Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM

This is the user's practical speed lane. The target model must remain fully resident; a nominally
higher-quality quant that spills is not a valid performance candidate.

## TG

| Mature mixed coding/agent TG | Confidence |
|---|---:|
| >=100 tok/s | ~95% |
| >=110 tok/s | ~85-90% |
| **>=120 tok/s** | **~60-65%** |
| >=130 tok/s | ~35% |
| >=140 tok/s | ~15% |

**Working target: 120 tok/s mixed agent TG.**

Direct exact-rig anchors already include:

- Q3_K_XL + native MTP around **113.27 tok/s** at 32K in an earlier server sweep;
- **116.89 tok/s** at 24K / q8 KV / MTP depth 4;
- ~97.2 tok/s mean across a later cache-busted 8K four-workload A/B;
- individual code/HTML lanes around 110-122 tok/s and tool-shaped outputs above 120 tok/s;
- larger IQ4_XS configurations spill badly and therefore do not define the speed target.

The ~120 center target assumes modest gains from current Blackwell small-N verify work and adaptive
MTP policy, not a transfer of RTX PRO 6000 absolute rates.

## Cold PP — 24K-32K server-class ruler

| Mature cold PP | Confidence |
|---|---:|
| >=200 tok/s | ~95% |
| >=225 tok/s | ~80% |
| **>=250 tok/s** | **~55-60%** |
| >=300 tok/s | ~25% |
| >=350 tok/s | ~10% |

**Working target: 250 tok/s cold PP at agent-sized context.**

Direct rig anchors:

- 24K, q8 KV, native MTP depth 4: **219.1 tok/s PP / 116.89 tok/s TG**;
- 32K, q8 KV, native MTP depth 4: **191.0 tok/s PP / 113.27 tok/s TG**;
- plain fully-resident Q3_K_XL `llama-bench pp512` can exceed 1,900 tok/s, proving the short-batch
  matrix path is not the production PP ruler; realistic server context is the relevant target.

Promotion gate: first pass the Blackwell prompt-shape/ubatch stability matrix (ubatch 256/512,
neutral + code/tool prompts, MTP off/on). A faster but prompt-fragile build does not count.

---

# 4. DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4

## TG

| Mature B1 TG | Confidence |
|---|---:|
| >=10 tok/s | ~95% |
| >=12 tok/s | ~85% |
| **>=15 tok/s** | **~60-65%** |
| >=18 tok/s | ~35% |
| >=20 tok/s | ~20% |
| >=25 tok/s | ~5% |

**Working target: 15 tok/s. Stretch target: 18-20 tok/s.**

Rationale:

- exact-hardware pre-0731 serial layer-PP measured roughly 10-13 tok/s decode;
- exact 0731 #922 proves long distributed execution but publishes no sustained TG denominator;
- AProjQ4 gives a real +15.5% decode result on M5 Max and saves ~2.14 GiB, making it the best current
  serving candidate, but the percentage is not transferred numerically to M1;
- DS4 #964's large GLM gains explicitly do not move DeepSeek-V4, so they remain mining evidence;
- mapping/OS/command-buffer pathologies can erase all apparent PP value if not gated first.

This is intentionally more conservative than the Flash target. DS4 is the architecture/control lane,
not the model for which we currently have the strongest M1 decode-upside case.

## Cold PP

| Mature cold PP | Confidence |
|---|---:|
| >=150 tok/s | ~95% |
| >=165 tok/s | ~80% |
| **>=180 tok/s** | **~60%** |
| >=200 tok/s | ~35% |
| >=225 tok/s | ~15% |
| >=250 tok/s | ~5% |

**Working target: 180 tok/s cold PP.**

Direct exact-hardware anchors are unusually strong here:

- pre-0731 2x M1 Max / TB4 long-prompt prefill: roughly **153.7-162.7 tok/s**;
- exact 0731 #922: **~152 tok/s** for a 34,384-token distributed prefill.

Thus >=150 is essentially the conservative floor when the runtime is healthy. The 180 target assumes
incremental implementation gains and current-head model/layout choices, not a hypothetical 2x scaleup.

Mandatory qualification before accepting a DS4 PP/TG number:

1. sane/coalesced Metal layer maps;
2. macOS build recorded;
3. command-buffer wait/completion and GPU-busy fraction recorded;
4. wired residency checked during decode;
5. same-host non-distributed control run;
6. only then attribute remaining loss to PP bubbles/TB4 and test multi-session filling.

---

# Current priority order implied by the targets

For pure interactive speed on the hardware already owned:

1. **RTX 5070 Ti + Qwen3.8-27B** — already closest to its mature target and most likely to exceed
   120 tok/s on favorable code/tool traffic.
2. **Dual-M1 Flash-Next** — highest upside among the Apple cluster lanes, but also the largest direct
   measurement gap; **40 TG @ ~128K / 400 PP** is the center system goal, not yet a physical receipt.
3. **Single-M1 Qwen3.8-27B** — useful exact/kernel optimization laboratory; ~25 TG is the realistic
   mature center, with PP strongly affected by whether approximate ANE assistance is allowed.
4. **Dual-M1 DS4-0731** — strongest exact cluster prefill anchor and best topology laboratory, but a
   conservative ~15 TG center until a physical current-head decode receipt changes the calibration.

For Hermes/multi-agent throughput, do not rank systems from B1 TG alone. Flash's B2-B4 aggregate
scheduler/pipeline target remains important and should be measured separately from single-request TG.

## Flash mature B2-B4 aggregate ladder — retained

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

---

# Target-change rules

Future research passes should update this file only when one of these occurs:

- direct sustained physical evidence on the exact target machine/topology;
- a same-generation hardware result closes a major unknown and has a defensible transfer mechanism;
- a required optimization is disproven or fails to reproduce;
- fit/admission changes make the assumed production configuration impossible;
- a new runtime path changes the actual work performed enough that the old target is no longer the
  same workload.

When updating, preserve both the old measurement anchors and the reason the probability moved.
Never convert microbenchmark speedups, stronger-chip percentages, or cache-hit latency into TG/PP
without an explicit wall-clock production-style measurement. Never change a context denominator
silently: short/medium, ~128K and 200K+ capacity cells are separate benchmark identities.