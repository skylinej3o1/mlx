# Runtime TG / PP Targets and Planning Confidence

Calibrated: **2026-09-04 06:40 ET**  
Target-definition correction: **2026-09-10 ET**  
Latest strategy true-up: **2026-09-28 11:57 ET**

This is the canonical planning-target file for the recurring model/hardware lanes:

1. Qwen3.8-Flash-Next on the planned **2x M1 Max 64 GB / Thunderbolt 4** cluster.
2. Qwen3.8-27B on **one M1 Max 64 GB**, with the user's **RTX 5070 Ti 16 GB + 64 GB host** kept as a separate dense-CUDA lane.
3. Qwen3.8-Flash-Next on the user's **RTX 5070 Ti 16 GB + 64 GB Windows host using Strata**.
4. DeepSeek-V4-Flash-0731 / DS4 on the same **2x M1 Max 64 GB / Thunderbolt 4** cluster.

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
- **Resident-agent capacity is not the same as one-shot context fit.** A 128K agent counts as resident only if its complete continuation state can remain retained/resumable for the next turn without a full re-prefill. Budget attention KV, recurrent/GDN state, QSA/indexer state, draft/MTP state and any retained checkpoint/state image separately from the active request. TensorFold's 64-GB 27B result is the cautionary receipt: ~140K one-shot fits, but DFlash2 conversations above roughly 100K could no longer retain their checkpoint and re-prefilled on the next turn.
- **Prefix reuse is not automatically physical prefix sharing.** A pinned system-prefix checkpoint (for example Strata 0.1.20) can eliminate repeated prefill for new chats while still using one live branch/arena at a time. Project 51 may count a common 30-60K prefix only once across several simultaneously resident agents **only after** the runtime implements refcounted/read-only shared attention+recurrent/QSA state and proves independent private-suffix continuation/rollback. Logical cache hits alone do not earn multi-agent memory-capacity credit.
- A target can move only when new direct physical evidence or a materially stronger mechanism case
  changes the planning distribution. Mechanism transfer alone should normally change the test plan,
  not silently become a measured rate.
- **Context is part of target identity.** A short/medium-context rate must never silently substitute
  for the ~128K Flash headline target.
- **CUDA->Apple handoff is a separate qualification target, not cold PP credit.** TensorFold #77 now proves on
  Qwen3.8-27B that CUDA `conv` / recurrent `rec` / attention `kv` state maps 1:1 into MLX cache tensors after only
  batch-dimension/layout changes. The Project-51 bridge succeeds only when the imported continuation diverges from a
  Mac-native prefill **no earlier than the Mac's own allowed chunk-plan control**, needles/agent replay pass, and the
  producer state is exported at a committed safe frontier. Qualify at **32K first, then 96K/128K**. Fast producer
  prefill earns no bridge credit if its numerical drift exceeds the consumer's own execution-plan tolerance.

### 2026-09-23 first-principles floor / center recalibration

This is a **derived engineering scenario model**, not a new benchmark and not a target change. It was rebuilt from the measured single-M1 long-context anchor instead of reasoning backward from the 40-TG goal.

Starting point:
- modern tuned M1 Max / Flash-Next / ~4.27-bpw target-only measurements are ~23.3 TG at 117.8K and ~20.5 TG at 148.5K, implying roughly **~22-23 TG around 128K**;
- that stack is already substantially optimized, so ordinary target-only kernel headroom should not be assumed to be enormous.

If the current xhigh quant hypothesis succeeds:
- a source-like **~3.4-3.6 average transformer BPW** artifact that maps efficiently to Apple7 is estimated at roughly **~25-27 target-only TG @ ~128K**;
- this estimate assumes only part of target-forward time scales with routed-expert bytes, so it does **not** convert the BPW reduction linearly into TG.

Required uplift to hit 40:
- 25 TG needs **1.60x** effective speculative/distributed acceleration;
- 26 TG needs **1.54x**;
- 27 TG needs **1.48x**.

This is materially less demanding than the earlier Q5-ish design, where a ~21-22-TG target-only base would have needed roughly **~1.8-1.9x** effective acceleration.

Current scenario interpretation:
- **physical fallback / speculation contributes almost nothing:** ~24-27 TG;
- **practical mature-system downside with at least modest speculation:** ~30-32 TG;
- **central planning region:** ~39-41 TG;
- **headline target:** 40 TG;
- **stretch:** ~50 TG.

The central mechanism remains verifier economics:
- measured Flash depth-5 verification cost: **~2.3 target-forward equivalents** on stronger Apple hardware;
- proposed MoE-union + GDN/chunked verification goal: **~1.5x**;
- ~2.4 useful accepted tokens / 1.5x verify cost gives ~1.6x effective uplift, approximately enough to turn a 25-TG target-only system into the 40-TG headline result.

PP2 does not magically double B1 causal decode. Its throughput value is primarily the ability to overlap **multi-row speculative verification** across stages. The new Metal batching-risk watch therefore makes Apple7 B2/B4 verifier efficiency a first-order acceptance gate.

Cold-PP derived scenario:
- exact modern single-M1 long-context PP is roughly ~200 tok/s in the tuned lane;
- useful long-prompt PP2 overlap plus modest lower-bit/fusion gains yields a current **~370-390 PP center**;
- **~320-340 PP** is the mature downside region;
- **400 cold PP** remains the success target.

**Probability/target effect:** none numerically. Keep the existing **~70% planning confidence for >=40 TG** and the 40/400 targets. This section clarifies the floor/center and what must be true for the target to land.

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

Historical note: the ~4.6-4.9 hot-trunk band was the quality-first search region at this point. **This is superseded by the 2026-09-23 xhigh-only specialization below**, which moves the active search toward ~3.0-3.6 average transformer BPW while requiring source-like xhigh behavior. Quality still wins over speed.

Certification should preferably include the actual comparable AA evaluation. Until that is practical, the frozen P51 proxy suite must be calibrated against source/Optimized/oQ5e behavior and include hard coding, tool use, long-context retrieval, QSA/indexer stability, recurrent-state replay and MTP acceptance. **A guessed "38+" is not certification.**

This is a **quality-target change only**. It does not change the 40 TG @ ~128K / 400 cold-PP planning targets or their current confidence ladder.

### 2026-09-23 xhigh-only production specialization

The user's actual local Flash-Next operating policy is now explicit: **drive the production model at xhigh reasoning**. Project 51 therefore optimizes for the intended production distribution rather than requiring one aggressive quant to preserve medium/xhigh/thinking-off equally.

This changes the **quant search policy**, not the headline TG/PP target:

- desired production quality: **source-like ~AA40-class behavior at xhigh**;
- >=38 remains a hard rejection floor, not the desired endpoint;
- start the first serious custom allocation around **~3.5 average transformer BPW**;
- search approximately **3.0 / 3.2 / 3.4 / 3.6** heterogeneous arms;
- current engineering hypothesis for the source-like xhigh frontier: **~3.3-3.6 average transformer BPW**, center ~3.4-3.5;
- preserve higher precision in QSA/indexer, recurrent/GDN-sensitive tensors, norms, router/shared experts, output/head and MTP-sensitive paths;
- compress the routed expert bank first;
- PLE/ngram and MTP/draft precision remain separately reported identities.

The DASLab 3.00-bpw Flash result is especially relevant because its calibration and published hard-reasoning evidence are xhigh-oriented. Its medium-effort degradation is still an important warning about calibration-domain specialization, but medium parity is no longer a production admission criterion for the xhigh-only artifact.

**Certification rule:** repeated paired source-vs-quant xhigh trajectories must cover hard reasoning, coding, tool use, long-context retrieval, multi-turn agent state, thinking-token distribution and MTP acceptance. One-run benchmark parity, KLD, perplexity or teacher-logit similarity is insufficient.

**Performance target effect:** none numerically. Keep **40 TG @ ~128K** (~70% planning confidence) and **400 cold PP** as the working dual-M1 goals. Lower BPW earns speed credit only after source-like xhigh behavior is demonstrated.

### 2026-09-20 quant-identity correction — flat Q4 vs dynamic Q4

Project 51 should no longer describe the intended Flash lane as "basically Q5" or identify it by one whole-file BPW.

Current public MLX bracketing references:

- **MTPLX Bare Speed:** flat Q4 for every MoE expert/dense matrix, 64-weight groups; 16-bit GDN/recurrent/norm/QSA-indexer/MTP islands; ~74 GB resident weights with the n-gram sidecar on SSD.
- **MTPLX Optimized Speed:** dynamic Q4 with the **QSA projections promoted to Q8** plus the same 16-bit sensitive islands. This is the higher-quality recommended sibling, but it is not a literal uniform Q5 quant.
- **APEX / Myric Flash evidence:** heterogeneous allocation can push selected expert classes lower while protecting small sensitive paths, but the published Flash APEX artifact omits the MTP head and uses GGUF formats whose M1 kernel economics do not transfer automatically.

Historical 2026-09-20 objective: **~4.6-4.9 effective-BPW hot compute trunk**, with PLE/ngram and MTP precision accounted separately. **Superseded for the active production search by the 2026-09-23 xhigh-only policy**: start near ~3.5 average transformer BPW and search ~3.0/3.2/3.4/3.6, promoting only source-like xhigh behavior.

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
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s @ ~128K active context** | **~70% planning confidence for >=40** | **400 tok/s** | **~70%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~65%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 <=8K / 110 ~16K / 95 ~64K / 90 ~128K tok/s** | **~75-90% by context; direct same-GPU-class v2 ladder** | **1,900 @24-32K / 1,500 @~128K tok/s** | **~80-85%** |
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
- **Intended deployment-design lane:** production is now **xhigh-specialized**. Begin the first serious custom build around **~3.5 average transformer BPW** and search approximately **3.0/3.2/3.4/3.6** heterogeneous allocations where M1/MLX kernels are efficient. The current engineering hypothesis for source-like xhigh behavior is **~3.3-3.6 average BPW**. This is a search region, not certification. The production winner is the lowest-cost allocation that remains source-like on repeated xhigh hard-reasoning/coding/tool/long-context/agent trajectories and passes MTP/state gates.
- **Optimization objective:** quality/tool-state/long-context/MTP acceptance per **M1 hot byte and microsecond saved**, not whole-file BPW. **Allocation method should combine APEX-style perturbation evidence with GSQ/RCO-style exact-budget optimization**, while adding M1 runtime cost and P51 behavioral/MTP losses to the objective.
- **PLE/ngram table precision + placement:** reported separately; SSD/offloaded PLE bits should not inflate the decode-bandwidth label. **However, PLE precision is part of the long-context MTP/quality gate, not a free capacity knob**: community Flash-Next evidence shows a possible deep-context acceptance penalty when the n-gram table is aggressively quantized, so Q4/Q6/Q8/source PLE arms must be tested through 128K before promotion.
- **MTP precision:** reported separately and kept relatively high until acceptance/quality evidence proves lower precision safe.
- Sensitive QSA/indexer, GDN, hyperconnection, routing/shared-expert and head tensors may receive Q6/Q8-class precision even when the routed expert mass is lower.

The frozen quality gate is behavioral: **source-like ~AA40-class behavior at xhigh is the production objective; >=38 is the hard rejection floor, not the desired endpoint**. A custom quant must retain essentially source/oQ5e/Optimized capability on Project 51's hard coding, long-context, tool/state, QSA/recurrent-stability and MTP-acceptance fixtures. Direct Flash GSQ/RCO evidence shows that very low nominal transformer BPW can preserve several reasoning/coding benchmarks, but **that does not substitute for AA-class and agentic certification**. A faster quant that materially changes routing/state behavior or falls below the quality floor does not qualify merely because average perplexity or a narrow task average is close.

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

This is the user's practical speed lane. **Context is now part of this target's identity.** A single
context-free TG or PP number is no longer an adequate ruler for this card.

The production candidate must remain fully resident on the 16-GB GPU. A nominally higher-quality
quant that spills is not a valid performance candidate. Quality certification remains separate from
runtime throughput: the strongest current physical receipt uses an abliterated GSQ-RCO IQ3_S build,
so its speed transfers much more cleanly than its behavioral quality.

## 2026-09-28 target true-up — same GPU class, current CUDA-v2 path

A missed 2026-09-27 physical receipt on an **RTX 5070 Ti 16 GB / GB203 / sm_120** invalidates the old
blanket **120 TG / 250 PP** planning row.

The measured system was a Ryzen 7 9800X3D / 32 GB DDR5-6000 host rather than the user's exact host,
but the target model was fully GPU-resident and the GPU/VRAM identity is exact. It ran Qwen3.8-27B
GSQ-RCO IQ3_S + embedded MTP, Q4_0 target/draft KV, batch 512 / ubatch 256, MTP depth <=3 and a pinned
llama.cpp CUDA-v2 patch. The production sampler and xhigh-capable serving configuration were exercised.

Direct measured ladder:

| Active prompt/context regime | Decode TG | Cold PP | Notes |
|---|---:|---:|---|
| short | **130.0-131.6** greedy / **129.5** sampled | — | 256-token short fixture |
| ~15.7K | **104.7** greedy / **111.7** sampled | **2,030** | production sampler also measured |
| ~62.5K | **98.0** greedy / **96.0** sampled | **1,814** | 512 generated tokens |
| ~92.9K | **94.8** | **1,696** | 512 generated tokens |
| ~128.8K | **91.3** | **1,576** | 128,794-token prompt; 81.7 s prefill |

At ~128K, llama-server peaked at about **14.93 GiB** and the whole card at about **15.07 GiB** with a
light desktop. A 119K ledger-recall test returned all four planted values exactly; an append-only
follow-up reused about 119.6K cached tokens.

This is not an upstream llama.cpp baseline. The pinned patch rewrites a large part of the Blackwell
hot path: multi-column quantized matvec, reduced-vocabulary MTP drafting, fused draft catch-up,
distribution-exact coupled sampling, small-query Q4 attention, INT8 prompt QK, fused decode glue and
faster prompt GDN/MMQ kernels. The numerical checks are strong for runtime correctness, but they do
**not** certify the checkpoint to the Project-51 AA~40 quality requirement.

### Working TG ladder

| Context | Mature TG target | Planning confidence |
|---|---:|---:|
| <=8K | **120 tok/s** | **~90%** |
| ~16K | **110 tok/s** | **~80%** |
| ~64K | **95 tok/s** | **~80-85%** |
| ~96K | **92 tok/s** | **~80-85%** |
| ~128K | **90 tok/s** | **~75-80%** |

These targets deliberately sit slightly below the corresponding physical receipts to leave room for
workload/acceptance variance and for a source-like production quant. **120 TG remains the short-context
working target; it is no longer a context-free mixed-agent target.**

## Cold PP ladder

The old **250 PP at 24K-32K** target is retired. It described an older server/runtime path whose direct
anchors were only 191-219 PP; it is not a hardware ceiling.

| Context | Mature cold PP target | Planning confidence | Current physical anchor |
|---|---:|---:|---:|
| ~24K-32K | **1,900 tok/s** | **~80%** | bracketed by 2,030 @15.7K and 1,814 @62.5K |
| ~64K | **1,750 tok/s** | **~80-85%** | 1,814 @62.5K |
| ~96K | **1,650 tok/s** | **~80-85%** | 1,696 @92.9K |
| ~128K | **1,500 tok/s** | **~80-85%** | 1,576 @128.8K |

The ~24K-32K target is an interpolation between adjacent physical receipts, not a claim that an exact
32K run measured 1,900 PP. The ~64K/~96K/~128K rows each have a nearby direct prompt measurement.

### Historical pre-v2 anchors retained

The older exact-card/server path measured:

- 24K, q8 KV, native MTP depth 4: **219.1 PP / 116.89 TG**;
- 32K, q8 KV, native MTP depth 4: **191.0 PP / 113.27 TG**;
- Q3_K_XL + native MTP around **113.27 TG** at 32K;
- a cache-busted 8K four-workload A/B around **97.2 TG mean**.

Those rows remain useful as evidence of how much the runtime path changed; they no longer define the
mature PP distribution.

### Promotion gates

The new speed ladder becomes a production lane only after:

1. the same patch or equivalent mechanisms reproduce on the user's 5070 Ti host;
2. neutral + code/tool + long-agent prompts pass the prompt-shape/ubatch stability matrix;
3. sampled and greedy semantics pass an independently derived sampler oracle;
4. the chosen source-like quant passes AA~40 reasoning/coding/tool/long-context gates;
5. long-context MTP acceptance, KV quality and tool behavior remain stable through ~128K.

A faster but prompt-fragile or behavior-changing build does not count.

---

# 3b. Qwen3.8-Flash-Next — Strata / RTX 5070 Ti 16 GB + 64 GB host

This is a separate runtime/model lane from the dense Qwen3.8-27B CUDA-v2 section above.

**Planning-confidence definition for this section:** the chance that a mature Strata build on the user's
exact RTX 5070 Ti 16 GB / 64 GB Windows rig can sustain at least the stated number under the named
context/quant regime **without reintroducing a known stability defect**. These are engineering planning
probabilities, not statistical intervals.

The primary production-quality candidates are:
- **IQ3_XXS** — balanced speed/quality lane; current best candidate for high-throughput agent use;
- **IQ3_S** — quality-first lane; slower but the preferred lane for source-like AA certification.

The pruned DASLab **Coder** is explicitly excluded from the primary target table because its xhigh SWE-bench
Verified retention is only ~91.3% of BF16 even though LiveCodeBench retention is ~98.7%. It remains a
specialized coding/capacity lane.

## 2026-09-28 physical anchors

Current measured Strata 0.1.14 on the weaker RTX 5070 12 GB / R5 7600 / 64 GB host:

| Quant | 32K PP / TG | 64K PP / TG | 128K PP / TG |
|---|---:|---:|---:|
| IQ3_XXS | **1,108 / 51.4** | **1,065 / 50.0** | **1,015 / 45.8** |
| IQ3_S | **1,070 / 48.2** | **1,070 / 48.8** | **931 / 40.5** |

Exact RTX 5070 Ti evidence is less matrix-like but materially stronger on decode:
- the 16-GB / Ryzen 9800X3D issue-31 box repeatedly showed healthy requests in the **50–90 TG** range;
- one long degenerate generation sustained roughly **105 TG** before the old stall;
- same-day code-generation reporting around **64K** is approximately **91 TG** on IQ3_XXS;
- after the 0.1.14 GPU-copy fix, that exact box completed **three HE+ sweeps / ~3.5 hours**
  with **zero stalls and zero watchdog trips**, where the old path froze every ~20–45 minutes.

The post-fix stability receipt materially raises confidence in Strata as a real production candidate.
It does not remove the separate Windows auto-admission/memory-fragmentation watch from issue #60.

## IQ3_XXS — balanced production target

| Active context | Mature TG target | TG planning confidence | Mature cold PP target | PP planning confidence |
|---|---:|---:|---:|---:|
| <=8K | **100 TG** | **~75%** | — | — |
| ~32K | **95 TG** | **~75%** | **1,300 PP** | **~85%** |
| ~64K | **90 TG** | **~80%** | **1,250 PP** | **~80%** |
| ~128K | **78 TG** | **~65%** | **1,150 PP** | **~75%** |

Interpretation:
- 64K has the strongest direct same-card decode support and is therefore the highest-confidence long-context TG row;
- 128K decode remains partly extrapolated from the exact-card healthy range plus the 12-GB context ladder;
- PP targets are conservative relative to the 12-GB card because 16 GB should hold more experts resident, but an
  exact-card Strata PP ladder has not yet been published.

**Stretch, not canonical:** **90 TG @ ~128K** for IQ3_XXS. Planning confidence **~35–40%** until an
exact-card 128K receipt exists.

## IQ3_S — quality-first target

| Active context | Mature TG target | TG planning confidence | Mature cold PP target | PP planning confidence |
|---|---:|---:|---:|---:|
| <=8K | **85 TG** | **~65%** | — | — |
| ~32K | **78 TG** | **~65%** | **1,200 PP** | **~80%** |
| ~64K | **70 TG** | **~60%** | **1,150 PP** | **~75%** |
| ~128K | **60 TG** | **~55%** | **1,050 PP** | **~70%** |

This lane deliberately sacrifices throughput for quant headroom. Do not raise it from IQ3_XXS speed
receipts without a same-checkpoint physical run.

## Sampling / penalty throughput convention

The TG tables above are **neutral/no-penalty throughput targets** unless a row explicitly says otherwise.
Strata 0.1.19 fixed speculative penalty history so every verified token now sees the same repetition/presence/frequency
history as serial decoding. Correct non-neutral penalties reduce throughput by **~1-11%** in Strata's release testing
because more drafts are rejected. For a production agent configuration that enables penalties, budget this discount
until an exact RTX 5070 Ti 0.1.19+ ladder exists; do not treat it as a kernel regression.

## Stability / admission targets

| Production gate | Target | Planning confidence now |
|---|---:|---:|
| sustained single-slot soak | **8 h, zero stalls/watchdogs** | **~90%** |
| extended soak | **24 h, zero stalls/watchdogs** | **~75%** |
| Windows 16-GB/64-GB auto admission | **boots first try, no expert-cache OOM** | **~70%** |
| error recovery with healthy RAM headroom | **restart <60 s** | **~80%** |

Why the stability confidence moved:
- exact 5070-Ti 0.1.14: ~3.5 h / three HE+ sweeps, **zero stalls**;
- another 16-GB Blackwell / 64-GB host reported a few sustained hours with **zero stalls**;
- the remaining admission issue (#60) is a distinct boot-time cache-sizing/fragmentation problem, not recurrence
  of the verify-window NVIDIA-driver-lock deadlock.

## Quality-certification targets

These are **planning probabilities for the custom Project-51 AA suite**, not measured AA scores:

| Quant | Quality objective | Planning confidence |
|---|---|---:|
| IQ3_XXS | **AA >=38** | **~85%** |
| IQ3_XXS | **AA >=40** | **~65%** |
| IQ3_S | **AA >=40** | **~80%** |

Rationale: DASLab's official 3.0-bpw Flash-Next IQ3_XXS task average is ~99.4% of BF16 on its published
suite, but Project-51 still requires source-vs-quant xhigh reasoning, coding, tools, long-context semantics,
thinking behavior and speculative-acceptance certification. IQ3_S gets a higher AA>=40 prior because it retains
more weight precision **and** DASLab now reports **82.0% SWE-bench Verified vs 82.8% BF16 (~99.0% retained)** on the
unpruned IQ3_S build. That materially strengthens the long-horizon agentic prior, but it is still not a Project-51
AA measurement and does not certify long-context/state/tool parity by itself.

## Promotion order

1. Reproduce the **0.1.14+ zero-stall soak** on the user's exact box for >=8 h.
2. Resolve or bound the **16-GB/64-GB Windows admission-margin** issue.
3. Run a frozen exact-card Strata ladder at 32K / 64K / 128K for IQ3_XXS, then IQ3_S.
4. Run the AA suite with INT8 KV as the default quality baseline; Q4 KV remains a capacity/speed arm.
5. Only after those pass, optimize toward the 128K stretch numbers.

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

1. **RTX 5070 Ti + Qwen3.8-27B** — now has a direct same-GPU-class long-context CUDA-v2 ladder:
   roughly 130 TG short, ~91 TG at 128K and 1.6K-2.0K cold PP across 16K-128K. The remaining work is
   source-like quant/AA qualification and reproduction on the user's host, not proving the raw GPU ceiling.
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