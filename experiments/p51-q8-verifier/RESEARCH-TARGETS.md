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
- **Agent wake/prewarm** is also separate: a lightweight Slack/Telegram/iMessage wake signal may pre-materialize the invariant system/tools/skills/repo prefix and certified recurrent/QSA state before the real task arrives. Measure wake->ready and real-task->TTFT independently; the 400-PP ruler remains genuinely cold.
- A target can move only when new direct physical evidence or a materially stronger mechanism case
  changes the planning distribution. Mechanism transfer alone should normally change the test plan,
  not silently become a measured rate.
- **Context is part of target identity.** A short/medium-context rate must never silently substitute
  for the ~128K Flash headline target.

## 2026-09-10 target-definition correction

The original 2026-09-04 normalization file accidentally made the Flash executive **40 tok/s** row
look like a short/medium-context target while also placing a lower probability ladder under the
~128K subsection. Subsequent project discussion clarified that the intended headline system goal is:

> **Qwen3.8-Flash-Next, quality-preserving mixed dynamic-4-bit deployment with an initial
> ~4.6-4.9 effective-BPW hot-trunk search band, PP2 on 2x M1 Max 64 GB over TB4, ~128K active
> context: ~40 tok/s sustained TG, with ~400 tok/s realistic cold PP.**

This correction is **not** an evidence-driven downgrade and then re-upgrade. No negative exact-target
measurement forced 40 -> 30. It restores the intended denominator for the existing goal.

The 40 @ ~128K number remains a **planning target / hypothesis**, not a measured dual-M1 receipt.

### 2026-09-20 quality floor — preserve >=38 AA-class behavior

The user explicitly prioritizes retaining model intelligence over the last few tok/s.

Current source reference (Artificial Analysis v4.3.2):
https://artificialanalysis.ai/models/qwen3-8-flash-next

- source Qwen3.8-Flash-Next Intelligence Index: **40**;
- production P51 quant hard floor: **>=38 AA-class behavior**;
- preferred production band: **39-40**;
- below 38: **experimental speed quant only**, not the default agent model.

This makes the quant search **lexicographic**:

1. satisfy the >=38 quality/capability floor across coding, agentic/tool, long-context and stateful behavior;
2. preserve MTP acceptance/correction behavior and QSA/recurrent correctness;
3. only then maximize sustained M1 TG / minimize hot bytes and microseconds.

The current ~4.6-4.9 hot-trunk BPW band remains a **search region, not a requirement**. If a slightly heavier quant is needed to stay >=38, quality wins. APEX-inspired ~4.3-4.6 arms remain valuable experiments, but cannot be promoted solely from perplexity or throughput.

Certification should preferably include the actual comparable AA evaluation. Until that is practical, the frozen P51 proxy suite must be calibrated against source/Optimized/oQ5e behavior and include hard coding, tool use, long-context retrieval, QSA/indexer stability, recurrent-state replay and MTP acceptance. **A guessed "38+" is not certification.**

This is a **quality-target change only**. It does not change the 40 TG @ ~128K / 400 cold-PP planning targets or their current confidence ladder.

### 2026-09-20 quant-identity correction — flat Q4 vs dynamic Q4

Project 51 should no longer describe the intended Flash lane as "basically Q5" or identify it by one whole-file BPW.

Current public MLX bracketing references:

- **MTPLX Bare Speed:** flat Q4 for every MoE expert/dense matrix, 64-weight groups; 16-bit GDN/recurrent/norm/QSA-indexer/MTP islands; ~74 GB resident weights with the n-gram sidecar on SSD.
- **MTPLX Optimized Speed:** dynamic Q4 with the **QSA projections promoted to Q8** plus the same 16-bit sensitive islands. This is the higher-quality recommended sibling, but it is not a literal uniform Q5 quant.
- **APEX / Myric Flash evidence:** heterogeneous allocation can push selected expert classes lower while protecting small sensitive paths, but the published Flash APEX artifact omits the MTP head and uses GGUF formats whose M1 kernel economics do not transfer automatically.

The deployment objective remains an **initial ~4.6-4.9 effective-BPW hot compute trunk**, with PLE/ngram and MTP precision accounted separately. APEX-inspired ~4.3-4.6 arms are now explicit experiments, not promoted targets.

The optimizer's objective is **behavioral quality and MTP acceptance per M1 hot byte / microsecond saved**, not minimum file size. The first baseline experiment is to make the MTPLX 16-bit BF16 islands/compute path M1-FP16-friendly while keeping the quantized tensors unchanged.

This is a **target-definition refinement, not a TG/PP probability change**.

### 2026-09-18 recovered Q5-class target-lane evidence

A previously missed 2026-09-15 oMLX community session is directly on the intended **Q5-class** Flash lane: `Qwen3.8-Flash-Next-Uncensored-oQ5e-mtp` on M5 Max 40-core / 128 GB, oMLX 0.7.0.dev2. The public benchmark recipe has MTP, DFlash, speculative prefill, ANE prefill and TurboQuant KV disabled. It reports **1,203 PP / 47.3 TG at 131,072 tokens** and **1,236 PP / 47.4 TG at 200,000 tokens**, with 91.4 / 97.4 GB MLX-active peaks. This is stronger-Apple transfer evidence, not dual-M1 proof, but it removes the stale assumption that the headline Flash lane was Q6/Q8 and materially strengthens the case that Q5-class target-only execution itself can remain above 40 tok/s deep into long context.

The same artifact's model card reports **5.72 bpw effective**, 128.54 GB on disk, with the PLE table SSD-offloaded on a 128 GB Mac; a real **250,073-token** request completed at **1,165 PP** and about **30 TG** with Lightning MTP + TurboQuant KV4, while the full native 262,144-token window fit. The sibling oQ6e build is listed at 150.5 GB on disk / about 101 GiB resident with MTP off and does **not** keep the full 262K window on 128 GB (about 131K limit). This is why **Q5-class remains the canonical Flash quality/capacity lane**: it is the highest published oQe level in this family that preserves the full-context fit on a 128 GB Apple machine.

These receipts raise qualitative confidence in the 40@128K architecture target but do not change the numeric target or assign a new exact-target probability; M1-generation silicon, TB4 partitioning, per-node working-set balance and distributed correctness remain unmeasured.
The September 10 r/oMLX backfill adds useful stronger-Apple long-context transfer receipts (including
30+ tok/s-class 120K-150K harness use and a separate warm ~40 tok/s report), but those do not become
exact M1-Max/TB4 evidence.

---

## Executive working targets

| Model / hardware lane | Working TG target | Confidence / status | Working cold PP target | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~65%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

Interpretation: these are the numbers to optimize toward in planning and experiment selection. They
are deliberately not the 90%-confidence floors and not the low-probability stretch ceilings.

---

# 1. Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4

## Quant design identity — custom mixed deployment lane

Project 51 no longer treats one whole-file BPW value as the Flash quant identity.

- **Quality/certification comparator:** oQ5e / high-quality 5-bit-class builds.
- **Aggressive speed comparator:** oQ4e.
- **Public MLX bracketing endpoints:** MTPLX **Bare = flat Q4 trunk**; MTPLX **Optimized = dynamic Q4 with Q8 QSA**. Neither should be mislabeled as a uniform Q5.
- **Intended deployment-design lane:** begin conservatively around **4.6-4.9 effective BPW on the hot compute trunk**, with tensor-role-aware allocation. Direct Flash-Next GSQ/RCO evidence now justifies **RCO-inspired ~3.0-4.6 experimental allocation arms** where M1/MLX kernels are actually efficient; these are research arms, not production targets. The production winner is whichever allocation satisfies the >=38 quality floor and MTP/state gates at the best M1 hot-byte/microsecond cost.
- **Optimization objective:** quality/tool-state/long-context/MTP acceptance per **M1 hot byte and microsecond saved**, not whole-file BPW. **Allocation method should combine APEX-style perturbation evidence with GSQ/RCO-style exact-budget optimization**, while adding M1 runtime cost and P51 behavioral/MTP losses to the objective.
- **PLE/ngram table precision + placement:** reported separately; SSD/offloaded PLE bits should not inflate the decode-bandwidth label. **However, PLE precision is part of the long-context MTP/quality gate, not a free capacity knob**: community Flash-Next evidence shows a possible deep-context acceptance penalty when the n-gram table is aggressively quantized, so Q4/Q6/Q8/source PLE arms must be tested through 128K before promotion.
- **MTP precision:** reported separately and kept relatively high until acceptance/quality evidence proves lower precision safe.
- Sensitive QSA/indexer, GDN, hyperconnection, routing/shared-expert and head tensors may receive Q6/Q8-class precision even when the routed expert mass is lower.

The frozen quality gate is behavioral and now has an explicit production floor: **>=38 AA-class behavior, preferably 39-40**. A custom quant must retain essentially source/oQ5e/Optimized capability on Project 51's hard coding, long-context, tool/state, QSA/recurrent-stability and MTP-acceptance fixtures. Direct Flash GSQ/RCO evidence shows that very low nominal transformer BPW can preserve several reasoning/coding benchmarks, but **that does not substitute for AA-class and agentic certification**. A faster quant that materially changes routing/state behavior or falls below the quality floor does not qualify merely because average perplexity or a narrow task average is close.

**Canonical performance targets remain 40 TG @ ~128K / 400 cold PP.** A custom quant may create stretch headroom beyond these numbers, but no higher numeric target is promoted until physical target-topology evidence exists.


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

- recovered exact-M1 low-bit evidence now shows the **full Flash-Next model on one M1 Max 64 GB** sustaining about **21 tok/s at 128K** with PLE mmap/SSD backing and about **24 tok/s on code with an MTP sidecar**. This materially strengthens the M1 silicon/runtime plausibility of the dual-node thesis, but the weights are Q2/IQ1-class rather than the canonical Q5-class, so the number is not doubled or transferred into the target forecast;

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

### Current September 21 ~128K engineering-confidence ladder

These are engineering planning estimates, not statistical probabilities. They incorporate the exact-Q5 stronger-Apple long-context receipt plus the recovered and newly strengthened exact-M1 low-bit receipts, while retaining a large discount for the still-unmeasured Q5 + PP2 + TB4 combination.

| Mature B1 TG @ ~128K | Current confidence |
|---:|---:|
| >=30 tok/s | ~95% |
| >=35 tok/s | ~85% |
| **>=40 tok/s** | **~70%** |
| >=45 tok/s | ~45% |
| >=50 tok/s | ~25% |

The confidence ladder includes a strong recovered modern **M1 Max 64 GB** physical receipt: AtomicChat's **4.27 whole-file BPW** artifact, Q8 KV, indexed QSA, direct PLE and **MTP off** sustains **23.31 TG at 117,764 prompt tokens** (384 generated) and **20.51 TG at 148,476**. The 4.27 label must not be treated as near-Q5 hot-trunk precision: the giant high-precision PLE table inflates whole-file BPW while much of the compute trunk is far more aggressively quantized. The receipt therefore proves a modern exact-M1 low-20s physical floor for an aggressive mixed quant, not for the intended 4.6-4.9 hot-trunk deployment lane. The pinned fork is also already substantially tuned. The 40-TG thesis still depends on higher-quality hot-trunk execution plus MTP/multi-row pipeline occupancy across the second M1. Recovered Splash evidence validates on **M3-or-newer Apple Silicon** that an aggressively model-specialized runtime can make **multi-row speculative verification** the dominant source of effective-TG gains, with fixed 8-row target verification, a trained draft path, Q8 paged-KV verification, and shape-specialized decode kernels. Splash currently requires M3+ and has an open M2/Apple-family-8 backend request, so its exact kernels are not direct M1 evidence; the M1-specific basis remains Project 51's own 27B verifier campaigns. Combined with Project 51's own 27B experience—where the meaningful gains also came primarily from MTP/verify-side tuning rather than ordinary B1 target decode—and llama.cpp #29110's +37% MTP-depth-2 gain with almost no n_max=1 movement, Splash previously justified the move to about 65% for 40 TG. The recovered DGPP two-Spark NVFP4 campaign now supplies materially stronger exact-family long-context evidence: after exact QSA-selection work, pass time is 29.55 ms at 129,560 tokens and 31.36 ms at 260,062 with 1.85-1.92 committed tokens/pass and exact response parity, implying roughly 63-65 TG and 59-61 TG respectively. Because this remains GB10/TP/RoCE rather than M1/PP2/TB4, only a modest additional planning credit is taken: **~70% for >=40 TG, ~45% for >=45, and ~25% for >=50**. The 144-TG Splash headline itself is not transferred numerically. Post-Kadir upstream llama.cpp now also contains qwen4exp-active Metal MoE routing/reduction, RMS_NORM+SCALE and SSM_CONV+SiLU fusion patterns plus newer qwen4exp HC backend support. These changes post-date the frozen September 8 runtime and justify preserving some incremental single-node headroom, but because no direct Flash-Next A/B exists and Kadir already carried custom overlapping Metal work, they do **not** raise the 40-TG probability.

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
|---:|---:|
| >=250 tok/s | ~98% |
| >=300 tok/s | ~95% |
| >=350 tok/s | ~85% |
| **>=400 tok/s** | **~70%** |
| >=450 tok/s | ~50% |
| >=500 tok/s | ~30-35% |
| >=600 tok/s | ~12-15% |
| >=700 tok/s | ~5% |

**Working target: 400 tok/s cold PP.**

Rationale:

- exact single-M1 evidence includes both the DS4 Q2 ~272-275 PP medium-context lane **and** the recovered Atomic mixed-quant long-context receipt at **208.84 PP @84,984**, **203.18 PP @117,764**, and **152.03 PP @148,476** with indexed QSA/direct PLE/Q8 KV. Its whole-file 4.27 BPW is not comparable to the intended hot-trunk precision, and its packed-QSA path is not parity-certified, so it is useful physical PP evidence but not a direct custom-quant ruler;
- sufficiently long prompts can pipeline chunks across a balanced PP2 split, so cluster PP has a
  much stronger scaling case than B1 decode;
- gathered-QSA prefill and sparse selected-K/V are structurally favorable;
- the ~27 GiB PLE/n-gram table can make PP vary dramatically depending on residency/page-cache
  state, so this target assumes an explicitly qualified PLE policy rather than accidental warm
  page cache;
- stronger-hardware prefill evidence now includes M5 Max mixed-4/8 HC+GDN fusion measurements of **1618 PP at ~16K**, **1850 at ~33K**, and a fusion-on plateau of **~1858-1873 PP through ~131K**. This reinforces architectural PP headroom but is not numerically transferred to M1;
- stronger-hardware 800-900+ tok/s gathered-prefill receipts remain supporting evidence from other runtimes/hardware classes, not direct M1 forecasts.

Qualification rule: every Flash PP result must record PLE lazy/resident mode, page-cache condition,
competing I/O, stage placement, prompt length, prefill chunking and actual TB4 traffic. Qualification
must also report **scheduler admission-to-first-prefill delay** separately from model PP/TTFT and sweep
prefill chunk size. Every receipt must verify the **effective runtime-resolved chunk width** rather than
trusting the requested CLI flag: DS4 #1056 exposed a case where base silently used 8192 despite
`--prefill-chunk 128`, invalidating an apparent regression. The same prompt must also be checked across
chunk widths at the **logit/cache-state level**: chunked execution can remain numerically different from
an unchunked reference even when final sampled text happens to agree.

---

# 2. Qwen3.8-27B — M1 Max 64 GB

The certified P69 exact-verifier campaign remains separate. P69B12 stays frozen/promoted and
P69B13 remains next from existing profiling only. The targets below are production-runtime planning
numbers and do not alter P69 certification.

## TG

| Mature B1 TG | Confidence |
|---|---:|
| >=20 tok/s | ~95% |
| >=22 tok/s | ~90% |
| **>=25 tok/s** | **~65%** |
| >=28 tok/s | ~30% |
| >=30 tok/s | ~15% |

**Working target: 25 tok/s.**

### 2026-09-22 direct Apple7 calibration

Splash #95 adds the first clean exact-hardware M1 Max 64 GB receipt from the model-specific Splash
runtime. On an M1 Max 32-core GPU, a measured Apple7 policy produces **25.7 / 15.4 / 25.8 tok/s**
across three short prompts (about **22.3 tok/s mean**) versus 23.2 / 14.0 / 23.7 untuned, with
byte-identical greedy output versus the untuned Apple7 path in the reporter's single-request and
three-concurrent-request A/B.

This is strong enough to raise the mature **>=22 TG** planning cell from ~80% to **~90%** and the
headline **>=25 TG** cell from ~55-60% to **~65%**. It does **not** justify moving >=28 or >=30:
one prompt remains heavily acceptance-limited at 15.4 TG, reasoning was off, the workload was short,
and the tested quant/runtime is not the frozen P69 identity. The same report measures only ~49 tok/s
cold PP on a 7,244-token prompt, so the separate 110-PP production target and confidence remain
unchanged; Apple7 prefill is explicitly the weak part of the current Splash policy.

The result also changes experiment ordering: reproduce the measured Apple7 policy before inventing
new kernels. Its failed Simdgroup experiment is a mandatory warning that isolated Metal kernel tests
can pass while full-model greedy output is wrong.

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