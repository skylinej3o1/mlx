# Runtime TG / PP Targets and Planning Confidence

Calibrated: **2026-09-04 06:40 ET**  
Target-definition correction: **2026-09-10 ET**  
Latest strategy true-up: **2026-10-04 13:00 ET**

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
- **Resident-agent capacity is not the same as one-shot context fit.** A 128K agent counts as resident only if its complete continuation state can remain retained/resumable for the next turn without a full re-prefill. Budget attention KV, recurrent/GDN state, QSA/indexer state, draft/MTP state and any retained checkpoint/state image separately from the active request. TensorFold's 64-GB 27B result is the cautionary receipt: ~140K one-shot fits, but DFlash2 conversations above roughly 100K could no longer retain their checkpoint and re-prefilled on the next turn. TensorFold #155 adds a stricter gate: **checkpoint-capture refusal under memory pressure must spill durably or fail/report loudly**; silently dropping a refused boundary checkpoint and cold-prefilling the next turn does not count as retained state. The maintainer confirms this still applies to 0.6.0 and asks that spill use a bounded asynchronous writer plus a resume-vs-fresh token-SHA test, so Project 51 should require the same properties.
- **Prefix reuse is not automatically physical prefix sharing.** A pinned system-prefix checkpoint (for example Strata 0.1.20) can eliminate repeated prefill for new chats while still using one live branch/arena at a time. Project 51 may count a common 30-60K prefix only once across several simultaneously resident agents **only after** the runtime implements refcounted/read-only shared attention+recurrent/QSA state and proves independent private-suffix continuation/rollback. Logical cache hits alone do not earn multi-agent memory-capacity credit. TensorFold #169 makes this test concrete: Flash-Next CUDA reuses a completed conversation but currently does not checkpoint a shared ~30.7K system/tools block for a *new* conversation, while its 27B path does. Add a new-conversation/common-system-prefix reuse test to resident-agent certification.
- **Advertised context is not retained-agent capacity.** On a real 64-GB M5 Pro, TensorFold 0.6.0 can advertise 65,536 Flash-Next tokens yet refuse ~50-65K prompts either immediately after a tiny request or only after minutes of prefill. For 64-GB Apple qualification, test the window edge as the first request, after a tiny request, after a retained turn, and through final prefill completion; all paths must agree on admission and retention.
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

**Implementation feasibility update (TensorFold 0.4.0):** pre-M5 Metal now serves Flash-Next checkpoints with
per-module MLX affine **2/3/4/5/6/8-bit mixed formats**, and 5/6/8-bit rows use row-exact matrix-unit kernels rather
than forcing a slow generic path. This materially lowers implementation risk for P51's protected high-precision
islands, but it is not an exact M1-Max/dual-M1 throughput receipt and therefore does **not** raise the 40-TG
probability by itself.

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

# 1a. Swift 1.5 Flash-Next — alternate effective-task-throughput lane

Swift 1.5 Flash-Next is now a **first-class alternate checkpoint for the main dual-M1 Flash lane**.
It does **not** change the physical 40-TG / 400-PP targets because the architecture and per-token runtime
are essentially the same. Its value proposition is a large reduction in reasoning-token demand at xhigh.

Paired BF16 xhigh evidence at 262K context:
- GPQA-D: **89.80 -> 89.60**, mean thinking tokens **17,683 -> 7,823 (-55.8%)**;
- MMLU-Pro: **87.75 -> 87.20**, mean thinking tokens **-57.0%**;
- AIME 2026: **98.67 -> 96.67**, mean thinking tokens **-31.3%**;
- HMMT: **98.00 -> 97.33**, mean thinking tokens **-35.1%**;
- LiveCodeBench v6: **88.40 -> 90.39**, mean thinking tokens **-44.8%**;
- Terminal-Bench 2.1: **67.64 -> 69.66**, but mean total generated tokens **+11.9%**.

The important conclusion is **not** “Swift is always 1.8x faster.” Token savings are workload-dependent,
and Terminal-Bench is a counterexample on mean output length. For Project 51, report Swift beside base Flash
with:
- physical TG / PP;
- solved-task wall time;
- generated reasoning/output tokens;
- tokens per solve;
- tool-call / trajectory length;
- AA/tool/long-context pass/fail;
- MTP acceptance and rollback behavior.

Independent xhigh Aider evidence is directionally strong: one paired community run reports base Flash at
**90.7% retry pass, 17,646 tokens/case, 1,542 s/case** and Swift Flash at **86.9%, 6,991 tokens/case,
608 s/case**. In paired n=107, 99 cases agree, 2 are Swift gains and 6 losses (McNemar p~0.29). Treat
that as task-efficiency evidence, not equivalence certification.

Strata also provides a useful same-runtime speed check: at 4K / IQ2_XS it reports roughly **465 PP /
78.7 TG for Swift** versus **467 / 78.3 for base**, supporting the assumption that most of Swift's wall-time
advantage comes from fewer generated tokens rather than a materially faster forward pass.

### Swift-Flash promotion gate

Base Flash remains the canonical quality/control checkpoint until Swift passes the full P51 suite at xhigh:
1. source-vs-Swift hard reasoning/coding/tool trajectories;
2. filled 128K+ semantic continuity and recurrent/QSA stability;
3. repeated agent trajectories and long-horizon recovery from mistakes;
4. MTP acceptance / rollback / thinking-parser behavior;
5. compact-quant certification on the actual deployment artifact.

The current Swift-specific GSQ-RCO compact releases are:
- IQ3_XXS: **75.97 GB**;
- IQ2_XS: **68.15 GB**;
- Q2_0: **66.55 GB**.

Their published Swift-specific KLD refinement is predominantly 512-token and explicitly does not establish
long-context quality. Therefore **do not inherit the base Flash IQ3_XXS/IQ3_S AA priors automatically**.
The chosen Swift compact quant needs its own AA and 128K+ qualification.

For planning only, when a paired workload preserves quality and reduces generated tokens by fraction `r`,
the useful-work rate can be expressed as **physical TG / (1-r)**. Keep this derived task metric out of
physical TG tables.

---

# 1b. Persistent canonical agent-root image — cross-runtime target

This is a **TTFT/state-reuse target, not a cold-PP target**. The first production artifact should be
dense Qwen3.8-27B because its stable Pi/Hermes system+tools prefix is large enough to matter and the
complete hybrid state is already well understood. Flash-Next follows after the denser state contract is
proven.

## Initial root-image target

| Gate | Initial target | Stretch |
|---|---:|---:|
| invariant root depth | **20K-40K tokens** | **64K+** |
| survives server/runtime restart | **required** | — |
| restore-to-ready on same runtime | **<5 s** | **<2 s** |
| suffix work after restore | **only new/private suffix** | — |
| target + speculative state | **complete and compatible** | — |
| mismatch behavior | **hard miss / re-prefill** | — |

Why this is worth a separate target: at the single-M1 native working PP target of ~110 tok/s, cold
materialization of a 20K invariant root costs roughly **182 s** and 40K costs roughly **364 s**. A valid
persistent root turns that repeated cost into state I/O plus a tiny landing suffix. Do not report that
as a higher PP number; report **root restore latency**, **restored tokens**, **replayed tokens** and
**real-task -> first-token latency** separately.

### Evidence and qualification contract

- patched llama.cpp on Qwen3.8-Flash-Next: 5,892-token cold prompt ~19.1 s; patched hybrid
  checkpoint restore ~153 ms and next request only 4 tokens / ~508 ms;
- TensorFold Qwen3.8-27B: 35,583-token conversation spills 2.2-2.4 GiB in ~0.18-0.19 s,
  reloads in ~0.24 s and answers in ~2.3 s versus 26.2 s cold, byte-identical;
- NInfer Qwen3.8-27B: a 6.9K complete session is ~416 MiB, saves in ~0.24 s and restores in
  ~0.12 s, including paged target+MTP KV, GDN state, MTP tail hidden, checkpoints and prefix identity.

These are **same-runtime persistence** results. They do not prove CUDA->MLX portability.

Additional Tier-1 RAM evidence now exists on Strata IQ3_S: a shared-core snapshot implementation passed **30
A->B->A returns across ~2K / 40K / 120K contexts**, including streamed KV, exact expected answers/state and stable
retained payload. At 51,133 cached tokens, a return after another conversation takes **1.237 s** and a checkpoint
return **0.566 s**. This materially raises confidence in the *correctness/feasibility* of parked full hybrid state,
but it does not change the Apple restore-latency target because the timing is from RTX 4090 / host RAM, not M1.

A root is valid only when all identity components match: model/weights, quant, tokenizer, chat template,
system/tools/extensions, reasoning/preserve-thinking behavior, KV/recurrent geometry, speculative
configuration, state-schema version and committed frontier. Target KV without recurrent/checkpoint/draft
state does not count.

### Promotion sequence

1. same-runtime M1 dense-27B root at **20K-40K**, exact continuation and restart survival;
2. include MTP/draft state and verify acceptance/trajectory parity after restore;
3. qualify **32K CUDA -> Apple** canonical-state export/import;
4. extend the portable image to **96K/128K**;
5. only then implement/credit **one physical immutable shared root + COW/private suffixes**.

A forkable persistent image normally creates a private materialized copy for each agent. It saves compute
and TTFT but **must not be counted as shared resident-agent memory capacity** until the runtime actually
implements refcounted/read-only shared attention+recurrent/QSA root state.

---

# 2. Qwen3.8-27B — M1 Max 64 GB

The certified P69 exact-verifier campaign remains separate. P69B12 stays frozen/promoted and
P69B13 remains next from existing profiling only. The targets below are production-runtime planning
numbers and do not alter P69 certification.

## Swift 1.5 alternate-checkpoint lane — effective task throughput

Swift 1.5 Qwen3.8-27B is now a **first-class alternate checkpoint candidate**, but it does not change
the physical 25-TG / 110-PP hardware targets. Its value proposition is fewer reasoning/output tokens
for a solved task.

Published xhigh BF16 comparisons report workload-dependent **mean-token reductions of roughly 16-54%**
with broadly similar aggregate quality, including higher LiveCodeBench with ~24.5% fewer mean tokens
and higher Terminal-Bench with ~16% fewer. Treat the headline 58.5% figure as a workload/median result,
not a universal multiplier.

For planning only, if a task preserves quality while reducing generated tokens by fraction `r`, define:

**effective base-Qwen work rate = physical TG / (1-r)**

Examples at a 25-TG physical engine:
- 24.5% fewer tokens -> **~33 TG-equivalent** task work;
- 40% fewer -> **~42 TG-equivalent**;
- 50% fewer -> **~50 TG-equivalent**.

These are **not physical throughput claims** and must never appear in TG benchmark tables.

Promotion requires paired base-vs-Swift xhigh runs on the P51 AA suite with:
- solved-task wall time;
- generated reasoning/output tokens;
- tool-call count / trajectory length;
- long-context semantic continuity;
- MTP/DFlash acceptance and rollback behavior;
- repeated agent trajectories.

Base Qwen3.8-27B remains the control until Swift meets the same production AA/tool/long-context floor.
Swift-specific GSQ-RCO **IQ3_S+MTP (~12.12 GB)** is the preferred first low-bit capacity artifact, but
its existing short-context distribution tests are only an allocation prior; it still needs full P51
certification.

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

### 2026-09-29 Strata 0.1.26 PP matrix true-up

The same weaker **RTX 5070 12 GB / Ryzen 5 7600 / 64 GB Windows** calibration box, using the same code-agent
prompts and setup defaults, now measures:

- IQ3_XXS: **1,745 / 1,609 / 1,602 PP** at 32K / 64K / 128K;
- IQ3_S: **1,624 / 1,640 / 1,443 PP** at 32K / 64K / 128K.

Those 12-GB cells are now retained as weaker-card calibration, not the 5070-Ti PP center.



### 2026-10-04 13:00 ET 5070 context-ladder / VRAM-safety true-up

**No numeric target or planning-confidence movement.**

New measured 5070-Ti performance anchor (Linux / 96-GB host / IQ3_S / calibrated):
- ~100 TG at 2K-8K;
- ~96-100 TG through 32K-131K;
- ~3.1K PP at 131K.

This complements the existing ~257.6K Windows anchor (~43-53.5 TG after tuning). Neither proves the user's exact
64-GB host admission or final xhigh agent wall-clock.

**Important correction to the previous pass:** the 1M slowdown in #781 is now attributed to an oversized explicit
expert cache/WDDM sysmem fallback, not proven intrinsic max-context cost. Project 51 still configures **262144** by
default because that is the production requirement, but larger caps are not rejected on principle.

5070-Ti admission/configuration rules:
- expert-cache auto first;
- streamed INT8 KV / ~32K resident remains the first 64-GB Windows arm;
- measure free VRAM after allocations are physically touched;
- treat near-zero VRAM headroom or WDDM paging as failed admission even if startup succeeds;
- #796 unified VRAM planner is a high-priority A/B after baseline but earns no admission credit until exact Windows
  5070-Ti/64-GB validation;
- calibrate pool workers/spec/min-p/pcie-frac/profile only after the memory plan is safe.

Production priors remain:
- IQ3_S/native262K physical fit **~97%**;
- Windows 16-GB/64-GB full-context admission **~90%**;
- 8 h / 24 h zero-stall **~75% / ~55%**.

Dual-M1 remains:
- production: IQ3_S/native262144/**>=35 TG / >=400 cold PP**;
- performance: IQ3_S/~128K/**>=40 TG / >=425 cold PP**;
- stretch: IQ3_S/native262144/**>=40 TG**.


### 2026-10-04 11:18 ET protocol/configuration correction

**No numeric target or planning-confidence movement.**

Canonical Strata protocol correction:
- **0.1.39 / 6f32ec0 DOES include native stateless /v1/responses**, implemented earlier by 0ad8f70 (#451);
- PR #759 closing unmerged does not remove that support;
- current Codex qualification is incomplete because #782 shows Codex 0.160.0 additional_tools input is rejected.

5070-Ti configuration gate:
- pool-worker count is now a mandatory calibration dimension, not a default to trust;
- production default remains **262144** because it is the required context; #780/#799 correct the prior inference that larger configured caps are intrinsically slow when VRAM residency is healthy;
- #783 becomes a later exact-sm_120 fusion A/B after the clean 0.1.39 baseline, with no pre-credit.

Production priors stay:
- IQ3_S/native262K physical fit **~97%**;
- Windows 16-GB/64-GB full-context admission **~90%**;
- 8 h / 24 h zero-stall **~75% / ~55%**.

Dual-M1 remains:
- production: IQ3_S/native262144/**>=35 TG / >=400 cold PP**;
- performance: IQ3_S/~128K/**>=40 TG / >=425 cold PP**;
- stretch: IQ3_S/native262144/**>=40 TG**.


### 2026-10-04 10:31 ET exact-5070 native262K performance anchor / protocol correction

**No dual-M1 target movement and no fit/admission/stability-prior movement.**

Windows/5070-Ti planning remains:
- IQ3_S/native262K physical fit: **~97%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**.

New direct performance anchor:
> **RTX 5070 Ti 16 GB / Windows / DASLab IQ3_S / 262144 / streamed INT8 KV / 96-GB host** has now been reported
> above **40 TG** at a 257.6K prompt after calibration, with single runs spanning roughly **43-53.5 TG**.

This is the exact target GPU and quant but **not** the target host-memory capacity. It demonstrates GPU/runtime
capability; it does not prove the user's 64-GB box will admit and sustain the same configuration.

Exact-box tuning order:
- frozen-residency quality baseline first;
- then pool workers, spec4/spec6, spec-min-p and pcie-frac sweep;
- learned profile as an independent arm;
- repeated cold/warm xhigh agent runs with wall-clock and retry accounting.

Do not copy #775's settings blindly. The host/CPU differ and its cells are single-run observations.

Software identity:
- treat **0.1.39 / commit 6f32ec0** as the next current-engine qualification candidate when BUILD.json confirms it;
- retain 0.1.38 as the regression comparator;
- native /v1/responses **is present in 0.1.39** via older commit 0ad8f70/#451; current Codex compatibility still has the #782 additional_tools gap.

RX6800:
- #778 materially reduces gfx1030 bring-up risk by fixing current-main compilation and showing adjacent RX6950XT
  execution;
- no bridge/PP target credit until exact RX6800 + target artifact + speculation-OFF prefill and state-equivalence tests.

Dual-M1 remains:
- production: IQ3_S/native262144/**>=35 TG / >=400 cold PP**;
- performance: IQ3_S/~128K/**>=40 TG / >=425 cold PP**;
- stretch: IQ3_S/native262144/**>=40 TG**.


### 2026-10-04 08:27 ET exact 16GB/64GB fit / agent-protocol true-up

One planning prior moves; production TG/PP targets do not.

**Windows/Strata lane:**
- IQ3_S/native262K **physical fit: ~95% -> ~97%**;
- Windows 16-GB/64-GB full-context admission: **~90% unchanged**;
- 8 h / 24 h zero-stall: **~75% / ~55% unchanged**;
- automatic containment: **~85% unchanged**.

Why physical fit moves:
Strata #757 is a direct IQ3_S/262144 receipt on the same broad memory class—16-GB GPU + 64-GB host—with a 250K cold
prompt, ~15.7/16-GB VRAM peak, >=6.17-GiB host MemAvailable, no swap growth and 15/15 needles. GPU compute and OS are
different from the target box, so **no TG/PP transfer** and **no Windows-admission raise**.

**5070-Ti configuration remains:**
- streamed INT8 KV;
- ~32K resident cells first;
- fine auto:16384-class prefill chunking;
- measure RAM commit, WDDM/shared memory, hard faults, VRAM reserve and late transients.

The #757 control strengthens this streamed-KV choice: when its 262K KV allocation was kept non-streamed, the expert
cache shrank materially and decode fell ~13-17% versus the 131K-cap arm.

**Agent qualification adds:**
- Responses/Codex protocol lane with ~100K tools/skills prefixes and subagent workflows;
- log native tool calls separately from JSON recovery, retry-assisted calls and synthesized calls;
- server-synthesized tool calls receive zero native-model quality credit.

**Dual-M1 numeric targets remain unchanged:**
- production: IQ3_S/native262144/**>=35 TG / >=400 cold PP**;
- performance: IQ3_S/~128K/**>=40 TG / >=425 cold PP**;
- stretch: IQ3_S/native262144/**>=40 TG**.

Strata #761's 2.04x four-way pipeline A/B changes the implementation checklist, not the M1 numeric prior:
asynchronous stage handoff and explicit stage-wait telemetry are required before judging balanced-pipeline PP.


### 2026-10-04 07:00 ET strict-pass qualification true-up

**No numeric target or planning-confidence change.**

Production baseline remains:
> **DASLab IQ3_S / 2x M1 Max 64 GB / native262144 / >=35 TG / >=400 cold PP / source-like xhigh agent behavior.**

Performance target remains:
> **IQ3_S / ~128K / >=40 TG / >=425 cold PP.**

Stretch remains:
> **IQ3_S / native262144 / >=40 TG.**

Model-challenger order changes:
1. **Build/qualify Swift 1.5 Flash-Next IQ3_S** using the ISTA IQ3_S allocation as the reproducible starting point,
   then apply/verify Swift-specific GSQ refinement;
2. existing Swift GSQ-RCO IQ3_XXS becomes the immediately available lower-precision control;
3. no Swift tier can inherit Swift-BF16 coding/Terminal gains without quant-level xhigh task evidence.

Quality-gate clarification:
- streamed **INT8 KV remains the first Windows long-context baseline**;
- long-context FP16-vs-INT8 teacher-forced KL can remain tiny while greedy trajectories fork at near ties;
- certification therefore uses task success, tool behavior, retrieval and repeated xhigh trajectories, not token
  identity to FP16.

RX producer clarification:
- nearby gfx1031 evidence is not gfx1030 certification;
- exact RX6800/gfx1030 cold prefill must prove QSA/PLE/prompt-kernel coverage before state-export/import gets bridge
  credit.

Admission/operability clarification:
- Windows exact-box logging adds **commit-capacity headroom**;
- disk continuation persistence is a later qualified feature, not part of initial cold-fit certification;
- cross-request repetition and reasoning->tool boundary behavior are explicit agent correctness gates.


### 2026-10-04 03:53 ET Swift 1.5 challenger / task-normalized throughput true-up

**No change to the DASLab IQ3_S production target. Model-selection metrics expand.**

Production baseline remains:
> **DASLab IQ3_S / 2x M1 Max 64 GB / native262144 / >=35 TG / >=400 cold PP / source-like xhigh behavior.**

New challenger:
> **Swift 1.5 GSQ-RCO IQ3_XXS**, pending quant-level long-agent qualification.

Underlying Swift 1.5 BF16 is especially relevant to Project 51:
- GPQA-D essentially flat at xhigh while mean thinking tokens fall ~56%;
- LiveCodeBench improves ~2 points with ~45% fewer mean thinking tokens;
- Terminal-Bench improves ~2 points;
- but IFBench and AIME regress, so it is not globally superior.

The compact bucket currently has **IQ3_XXS / IQ2_XS / Q2_0**, not IQ3_S. IQ3_XXS has promising short-context KLD
against Swift BF16, but no quant-level long-agent task receipt. Therefore it cannot inherit the BF16 benchmarks by
assumption.

Add a first-class KPI alongside TG/PP:
> **time-to-correct-agent-result / total task wall-clock**

Report reasoning-token count, tool count, retries and success together with raw TG/PP. This prevents a token-efficient
Swift model from being undervalued merely because its decoder TG is lower—or overvalued because the BF16 model thinks
less while the quant loses capability.

Swift promotion requires coding/Terminal/SWE-bench-style/Playwright/deep-context/repeated-xhigh qualification plus
single/dual-M1 memory and speed measurements.


### 2026-10-04 03:09 ET dual-M1 Flash-Next target recalibration

**This section supersedes the September dual-M1 Flash target center. It is based on targeted source audits, not a
new comprehensive search pass; the strict search hard boundary remains 2026-10-04 00:51:42 UTC.**

New physical anchor:
- paperniuk/ds4 / M1 Max 64 GB / Qwen3.8-Flash-Next;
- Q2_0: ~43.4 MTP TG @128K and ~37.4 @256K;
- IQ3_XXS: ~34.2 @128K and ~31.7 around259K;
- **IQ3_S: ~32-34 MTP TG at short context**;
- tuned long-context QSA/indexer work has already demonstrated a 23.8 -> 33.8 TG plain-decode jump at ~128K.

This is sufficiently stronger than the old ~22-23-TG M1 long-context anchor to move the canonical dual-M1 planning
distribution.

#### Canonical production artifact

**DASLab IQ3_S** is now the first production artifact for the 2x M1 Max lane.

IQ3_S may be used as a **Q5-class task-quality planning shorthand at ~3.5-bpw transformer economics**, but this does
not imply source equivalence. Production still requires source-like xhigh coding/tool/long-context/state behavior.

#### Canonical dual-M1 goals

| IQ3_S / 2x M1 Max 64 GB | Initial bring-up | Mature realistic | Success target | Stretch |
| --- | ---: | ---: | ---: | ---: |
| TG @ ~128K | 25-28 | **34-38** | **40** | 45+ |
| TG @ native262K | 23-26 | **31-35** | **35** | **40** |
| cold PP @ ~128K | 330-380 | **420-460** | **425+** | 500 |
| cold PP @ native262K | 330-380 | **390-430** | **400** | 450+ |

Canonical production definition:
> **IQ3_S / native262144 / >=35 TG / >=400 cold PP / source-like xhigh behavior.**

Performance definition:
> **IQ3_S / ~128K / >=40 TG / >=425 cold PP.**

Stretch:
> **IQ3_S / native262144 / >=40 TG.**

Planning confidence:
- fit cleanly across two 64-GB M1 Maxes: **>=90%**;
- >=400 cold PP @262K: **~80%**;
- >=35 TG @262K: **~70-75%**;
- >=40 TG @128K: **~70-75%**;
- >=40 TG @262K: **~45-55%**.

These are engineering planning priors.

#### Memory basis

paperniuk/ds4 plans IQ3_S approximately as:
- 55.2 GiB base;
- ~33 KiB per context token;
- +2 GiB reserve.

At native262K this is **~65.9 GiB**, only slightly above a single 64-GB Mac and trivial across 128 GB aggregate.
The large n-gram/PLE table can stay on SSD.

Therefore the dual-M1 problem is now primarily **latency/topology**, not aggregate fit.

#### Architecture competition

Do not lock PP2/pipeline as the only architecture.

Qualify three arms:
1. balanced contiguous layer pipeline;
2. asymmetric decode split after one-time post-prefill state migration;
3. **almost-local IQ3_S with shallow routed-expert SSD spill**.

For arm 3, the approximate bytes that must leave Mac A at resident budgets of 54/56/58 GiB are **11.9 / 9.9 /
7.9 GiB** respectively. Slipstream makes this mechanism credible, but its M5-Pro rates do not transfer to M1.

The winning architecture is the one that meets the native262K 35/400 production goal with the best xhigh quality and
operational reliability—not the one with the prettiest microbenchmark.

#### Custom-engine scope

Do not rebuild generic Flash-Next M1 execution from zero.

Start from paperniuk/ds4 and add only the missing Project-51 work:
- Qwen Flash distributed/asymmetric execution;
- exact IQ3_S memory/residency control;
- shallow expert spill experiment;
- additional multi-row verifier work only where profiling still shows headroom;
- copy-from-context proposals for repo/file edits;
- resident-agent/session correctness;
- dual-M1 scheduling.

Historical September 40 TG / 400 PP @128K remains in this file for provenance but is superseded as the sole production
goal by the native262K 35/400 definition above.


### 2026-10-03 20:51 ET exact-5070 PP / copy-draft / agent-admission true-up

**No numeric target movement. Exact-box PP and agent-serving qualification get new arms.**

Primary Windows stays Strata 0.1.38, IQ3_S/native262K fit ~95%, Windows admission ~90%, 8 h / 24 h zero-stall
~75% / ~55%, automatic #481 containment ~85%, with INT8 streamed KV and ~32K resident cells first.

**5070-Ti prefill:** add a #693-equivalent `--prefill auto:16384` fine/equal-chunk arm. Same-GPU IQ3_XXS evidence
shows ~21-35% higher PP from 32-100K and ~3.1-3.4K PP absolute. Do not transfer that rate to IQ3_S; measure
16/32/64/128/200/~250K on the exact quant and log chosen chunk / expert loans / transient VRAM.

**#646:** root-cause fixes for the sm_120 crash and source-gate drift are plausible, and a 24-GB Ada partial-residency
test now gets +5-16% decode. Still exclude the branch from 5070-Ti certification until an independent 16-GB sm_120
partial-residency retest plus exact IQ3_S gate succeeds.

**Agent-serving profile:** enable `fit_max_tokens=true` for clients that send large static max-token allowances;
keep explicit reasoning budget and log the fitted effective cap.

**Custom M1 27B:** generic target remains **25 TG / 110 cold PP**. Add context-copy proposals as a later,
workload-specific accelerator after base verifier/state correctness. Copy-heavy rewrite TG never substitutes for the
generic TG target.


### 2026-10-03 15:42 ET 16GB-baseline / RX-prefill / persistence true-up

**No numeric target movement. Configuration and qualification rules sharpen.**

Primary Windows exact-box qualification:
- Strata **0.1.38**;
- native 262144, 204800 first fallback;
- **INT8 streamed KV with ~32768 resident cells first**;
- preserve real post-load VRAM reserve;
- #646 resident-verify optimization branch excluded until its non-resident sm_120 crash and IQ3_S exactness issues
  are fixed.

The exact RTX5060Ti16/64GB #620 receipt is the reason this is now a requirement: full 131K resident INT8 KV can
consume the head's startup allocation, while `--kv-resident 32768` succeeds.

Single-M1 Qwen3.8-27B stays **25 TG / 110 cold PP**. TensorFold #323's M2-Max GDN tuning yields only ~0.8-2.2%
full-model gain, reinforcing that bespoke work should stay focused on the multi-row long-context verifier and
state/cache lifecycle.

RX6800 producer qualification starts **prefill-only / spec off** because Strata #649 shows an unresolved gfx1030
speculative-verify hang. The producer earns credit only from cold target-only PP + full-state export/import parity;
decode/spec can be qualified later.

Conversation parking remains OFF in the initial production baseline. Strata #668 session-file restore is a separate
future persistence arm; qualify 128K/200K/~250K restart restore before promotion.

Agent-state gate adds: at max_tokens/EOT inside a speculative window, live committed state must contain exactly the
API-visible outputs (#652).


### 2026-10-03 07:53 ET resident-state / reasoning-accounting true-up

**No numeric target movement. Qualification rules tighten.**

- Reasoning-budget continuation telemetry does **not** count as trusted PP/context accounting until segment aggregation
  preserves the original input/cache counts and aggregates continuation output/timing exactly.
- Resident-agent admission must include **checkpoint-slot count and bytes**, not just active context.
- Parking/terminal snapshots must **not duplicate paged KV**. Store only state not already durably represented by the
  page pool plus stable references/metadata; restore must still pass fresh-vs-resumed equivalence.
- High/xhigh keeps an explicit reasoning budget and now requires a **non-empty final answer after budget rollover**
  soak case.
- Draft-vocabulary tuning is workload-weighted. For the QA/coding lane, protect code/tool/CJK tail coverage instead
  of minimizing vocabulary size blindly.

Primary Windows 262144/204800 fallback, single-M1 **25 TG / 110 cold PP**, DASLab IQ3_S-MTP artifact priority,
RX6800 prefill experiment, PLE ladder and hardware-purchase decision remain unchanged.


### 2026-10-03 07:00 ET M1-27B/PLE/RX producer true-up

**No numeric target movement. The implementation baseline and artifact identities get sharper.**

Primary Windows remains Strata 0.1.38 with:
- IQ3_S/native262K physical fit ~95%;
- Windows full-context admission ~90%;
- 8 h / 24 h zero-stall ~75% / ~55%;
- #481 automatic containment ~85%;
- 204800 as the first fallback if native262K qualification fails.

**PLE correction:** FP8 remains the practical production-fidelity candidate, but new direct #586 evidence shows it
is **not source-equivalent to BF16**. BF16 is the exact source-value control; stock IQ4_NL remains the capacity/default
baseline. Production PLE choice must be made by labeled quality/agent evaluation, not KL alone.

**Single-M1 Qwen3.8-27B:** retain **25 TG / 110 cold PP**. Build the custom lane on current upstream MLX:
- include merged #4596 before measuring attention;
- include/cherry-pick #4598 if available before writing replacement affine Q4/Q5/Q6/Q8 gather-QMV;
- bespoke work focuses on long-context multi-row GQA verify, MTP scheduling, state/cache lifecycle and quant mapping.

**Primary M1/RX artifact:** DASLab **IQ3_S-MTP integrated (~12.1 GB)**. Target-only IQ3_S is the serial control;
IQ3_XXS-MTP is the speed/capacity control; ByteShape remains the alternate quality-allocation family.

**RX6800 producer:** TensorFold ROCm Qwen3.8-27B (#100) and ROCm GGUF (#144) are implementation mines. Their R9700 /
Strix numbers do not transfer to gfx1030. Bridge credit still requires exact RX6800 PP plus full-state HIP->M1 import.

**Dense-27B KV:** INT8/Q8 is the first compressed long-context control; more aggressive KV follows only after
continuation and agent-quality gates.


### 2026-10-02 23:26 ET single-M1 27B / RX-prefill strategy true-up

**No numeric target changes. Two experimental lanes become explicit priorities.**

Current primary baseline moves to **Strata 0.1.38**. Windows Flash-Next physical-fit/admission/stability priors stay
unchanged.

For **Qwen3.8-27B on one M1 Max 64 GB**, keep the existing **25 TG / 110 cold-PP** working targets. Recovered MTPLX
#506 does not justify a numeric raise because its +30-39% long-context improvement is an estimate on M3 Max, but it
identifies the exact kernel seam our custom engine should attack: pre-M5 multi-row GQA verification must traverse the
long KV once per verify block, not once per drafted row. The custom-engine benchmark contract now includes
16/32/64/96/128K, q=2/3/4 plus wider DFlash-style blocks, dispatch/fallback counters, verify-cycle time, acceptance,
and serial-equivalence checks.

Candidate order for the custom M1 27B engine:
1. **DASLab GSQ-RCO IQ3_S (3.50 bpw / 11.8 GB)** — quality-first;
2. **ByteShape ~3.8-bpw quality arm**;
3. **DASLab IQ3_XXS (3.00 bpw / 10.1 GB)** and ByteShape ~3.2-bpw — speed/context arms.
Q5/Q6/Q8 remain controls, not presumed production winners.

For the user's **RX 6800 16 GB + Linux host**, add a formal **dense-27B cold-prefill-producer** experiment.
Same-architecture Strata evidence reaches ~330-339 PP on RX6900XT-class gfx1030 Flash-Next, and llama.cpp has a
dual-RDNA2 Qwen3.8-27B Q4_K_M fresh-prompt result around 230 PP. These are not single-RX6800/DASLab measurements, so
the canonical RX secondary-lane PP estimate does not move.

RX->M1 bridge credit requires:
- single-card RX6800 PP receipt on the exact low-bit 27B artifact;
- full conv/recurrent/KV state export at a committed frontier;
- exact tokenizer/model identity;
- M1 import;
- continuation equivalence versus Mac-native prefill;
- transfer time included in TTFT.


### 2026-10-02 20:20 ET Apple TurboQuant/transient-memory true-up

**No numeric primary-Windows target movement. Apple capacity qualification gets a stricter rule.**

oMLX #3436 demonstrates real QSA TurboQuant on a 64-GB M4 Pro: an ~84.8K request peaks around 55.8 GB before
post-prefill conversion and falls to ~49.2 GB afterward. An attempted quantize-during-prefill implementation still did
**not** raise the practical context ceiling. Therefore Project 51 grants **no max-context credit from KV compression
arithmetic alone**; the exact runtime must show a lower cold-prefill transient peak.

oMLX #3437 also corrects its own earlier single-64GB ~200K+ estimate: streamed-expert Flash-Next oQ2 on one M4 Pro
hits a measured ~121-122K wall from chunked-prefill transient memory and uses a 120K production setting. This is not
the dual-M1/TB4 topology, so the Project-51 two-node target does not move. It does mean the dual-node 200K+ hypothesis
must be proven by a true two-node cold 128K/200K/262K admission ladder, not inferred from resident-weight + KV bytes.

Strata #563's hot expert-cache VRAM release/refill remains **off** in the certified baseline because a refill while
another Windows application still holds VRAM can trigger WDDM shared-memory spill and ~10-17 TG decode. It may be
qualified later as a workstation-sharing feature.


### 2026-10-02 19:25 ET fidelity/parser true-up

**No numeric runtime target or fit-prior movement. PLE and agent-correctness qualification priorities change.**

Current exact-box baseline stays **Strata 0.1.37** with:
- physical fit/admission ~95%;
- Windows full-context admission ~90%;
- 8 h / 24 h zero-stall ~75% / ~55%;
- #481-style automatic containment/no-manual-service-restart ~85%.

**PLE ladder changes:** stock IQ4_NL remains the compatibility baseline, but checkpoint-native **FP8 PLE becomes the
preferred production-fidelity candidate**, with BF16 PLE retained as the source-of-record control. Strata #464 now
reports independent FP8-vs-BF16 answer-level KL around 0.00087 on an adjacent 0.1.37/RTX5090 lane while stock IQ4_NL
can be much farther from BF16 at individual positions. Exact IQ3_S long-agent A/B is still required before promotion.

**Deterministic AA runs must freeze residency.** Strata #463 and new #550 both show timing races around adaptive expert
residency can fork arithmetic/state. Keep `--adapt-swaps 0`, fixed expert cache, `--pcie-frac 0` for strict gates,
and qualify adaptive residency only afterward.

**Agent-production gate expands:** Strata #537 plus vLLM #59821 require explicit tests for quoted/generated
`</think>`, quoted tool markup inside reasoning, genuine implicit-end calls, incomplete current calls, malformed
historical calls and normal tool loops. Passing raw runtime soak is not sufficient for autonomous QA-agent signoff.

**Custom sm_120 builds:** Strata #542 makes CUDA runtime/header compatibility and sane GPU-property logging a mandatory
pre-benchmark check. A build reporting impossible shared-memory capacity is invalid evidence.

Conversation parking remains OFF in the initial production baseline: official-v0.1.37 Windows data shows it can work
at ~58K, but #528 remains unresolved near ~100K and adjacent runtimes continue to find restore-state corruption.


### 2026-10-02 16:03 ET Strata 0.1.37 recovery/agent-production true-up

**Current exact-box baseline becomes Strata 0.1.37. Fit and zero-stall priors stay fixed; recovery semantics improve.**

0.1.37 ships the #481 server-side safety net: a silent or STOP-unresponsive engine is killed, the active request
errors, and the next request restarts the engine. The shipped default silence threshold is **300 s** (with long-prompt
allowances), so the former "<60 s built-in recovery" line is no longer an honest description of the current release.

Current planning state:
- IQ3_S/native262K physical fit: **~95%**;
- Windows full-context admission: **~90%**;
- 8 h zero-stall: **~75%**;
- 24 h zero-stall: **~55%**;
- #481-style **automatic containment/no-manual-service-restart: ~85%**;
- sub-60 s recovery: **not yet qualified**; requires a lower `engine_silence_s` production setting plus a real soak.

This ~85% is an engineering prior based on the implemented kill/restart path plus unit/HTTP fake-engine tests. There is
not yet a live 0.1.37 recurrence showing recovery from the exact #481 failure.

**Production configuration change:** leave `--conversation-cache-mib` / conversation parking OFF until #528 is
fixed. A Windows RTX5090/IQ3_XXS report shows restored ~100K conversations at ~18-31 TG versus ~87-116 TG with ordinary
prompt reuse. This does not prohibit prefix reuse; it only disqualifies parking/restore for the initial baseline.

**High/xhigh configuration change:** set `reasoning_budget_tokens` explicitly. #530 shows high/xhigh can otherwise
consume max_tokens entirely in reasoning and return empty content. No universal budget number is promoted yet.

If screenshot-driven QA is included, require #529-equivalent Anthropic tool_result image handling in addition to the
existing #510/#525 tool-call gates.


### 2026-10-02 15:02 ET Strata 0.1.36 baseline true-up

**Current exact-box baseline becomes Strata 0.1.36. Numeric planning priors and TG/PP centers do not move.**

The 0.1.36 release was missed by the immediately preceding watch pass. It preserves the default native-IQ prompt path
while adding RTX-50-class cluster decode kernels whose QSA selection and greedy argmax parity tests are bitwise through
262,144. This is favorable for the RTX 5070 Ti lane but remains subphase evidence until a controlled IQ3_S full-request
ladder lands.

Do **not** enable `STRATA_PF_FUSED=1` for source-certification runs. On the published exact RTX 5070 IQ3_S A/B it is
approximately neutral/slower (-0.2% at 4K, -1.4% at 32K) and uses different arithmetic; one greedy arm diverged after
a 31-token common prefix. Treat it as a separate experimental speed/quality arm.

The promised #481 lost-step recovery is not listed in the 0.1.36 release commit and has no new soak receipt.
Therefore keep:
- physical fit/admission ~95%;
- Windows full-context admission ~90%;
- 8 h zero-stall ~75%;
- 24 h zero-stall ~55%;
- current-release <60 s built-in recovery ~55%.

Add Strata #525's reasoning-to-tool-call boundary to the agentic production gate; it does not change the raw
runtime/fit priors.


### 2026-10-02 12:59 ET IQ3_S native262K fit/admission true-up

**Physical-fit/admission prior rises from ~90% to ~95%. Mature TG/PP centers remain unchanged.**

Recovered Strata #406 supplies the previously missing memory-shape receipt: a Windows user reports
**64 GB RAM + 16 GB VRAM + IQ3_S** working at manually configured 256K context with only a slight performance hit.
The original Linux/64-GB IQ3_S reporter also ran full native context with >6 GB free. Since 0.1.33, setup preserves an
explicit 262,144 request instead of forcing 128K.

This still is not the user's exact RTX 5070 Ti. Exact certification requires a real ~250K IQ3_S cold prompt on that
machine. But together with #469 (IQ3_S ~250K on 11-GB VRAM), #31 (exact 5070 Ti/~63-GB Windows/native262K on
IQ3_XXS) and #200 (exact 5070 Ti 257,466-token cold prompt on IQ3_XXS), the remaining physical-fit uncertainty is now
small enough for a **~95%** planning prior.

Windows 16-GB/64-GB full-context admission confidence rises from **~85% to ~90%**.

Stability does **not** inherit those numbers. #481 remains open on 0.1.35; its next-release automatic-restart fix is
promising but not yet released-and-soaked. Keep the current 8 h / 24 h zero-stall priors at **~75% / ~55%** and
current-release <60 s recovery at **~55%**.

PR #500's original +69-78% decode headline is now explicitly excluded from planning centers after an independent
RX 7900 XTX / IQ3_S test measured approximately **-2.3% decode / -0.6% 32K prefill**. Treat it as an exact-box A/B
candidate only.


### 2026-10-02 05:52 ET IQ3_S native262K fit/stability true-up

**Mature TG/PP centers unchanged.**

Strata #469 runs IQ3_S + native262K on an **RTX 2080 Ti 11 GB** with engine RSS roughly **52.3-52.9 GiB** through a
real 250K prompt. The host has 128 GB, so this is not the exact 64-GB proof, but it demonstrates a full native working
set below 53 GiB process RSS on a GPU with 5 GB less VRAM than the target 5070 Ti.

Combined with Strata v0.1.35's Windows low-RAM fix, the exact-box
**5070-Ti 16 GB + 64 GB + IQ3_S + native262K physical-fit/admission prior becomes ~90%**.

Do not confuse fit with production stability. Strata #481 reports repeated permanent deadlocks on a
**5060 Ti 16 GB + 64 GB Windows** coding-agent box under heavy-prefix prompts and long reasoning streams, with no
watchdog recovery. Exact-box qualification therefore requires agentic long-reasoning soak and an external supervisor.

Current production-readiness priors:
- 8 h zero-stall soak: **~75%**;
- 24 h zero-stall soak: **~55%**;
- Windows 16-GB/64-GB admission: **~85%**;
- built-in restart/recovery under 60 s: **~55%**.

Current exact-box baseline: **Strata v0.1.36**.

Fidelity qualification gains a new control: Strata #464 can stream the checkpoint's original **BF16 PLE** with little
measured PP cost. IQ4_NL-vs-BF16 changes 14.6% of measured routing entries and all probed first-window logits, so run
BF16 PLE as a source-of-record AA/agent control before making strong near-source claims about IQ3_S.

If MTP startup is VRAM-fragmentation limited, Strata #474 establishes the English draft vocabulary (~133 MiB head)
as a code-lane emergency lever versus the default CJK head (~348 MiB).

### 2026-10-02 exact-5070-Ti/runtime strategy true-up

**No numeric target change.** New same-GPU evidence expands the physical bracket rather than moving the mature centers.

Strict-window Strata PRs #439/#452/#453 use an exact **RTX 5070 Ti 16 GB** but a weak host
(PCIe 3.0 x16, Ryzen 5900XT, DDR4-2133). On IQ3_XXS they place current 8K-32K prompt processing around
**about 1.6-1.9K PP** depending on the independent optimization arm, with #453 showing roughly **46-60 TG** in its
8K/16K MTP samples. These are a weak-host floor region, not the user's DDR5/new-platform target.

Keep the canonical IQ3_XXS PP centers **3,000 / 2,900 / 2,750 / 2,500** because the stronger exact-card evidence
already includes about 3.0K around 60K and **2,668 PP at a real 257,466-token cold prompt**. The new evidence explains
why same-GPU results spread so widely: prompt expert streaming, host/link bandwidth, QSA attention path and MTP prompt
work are first-order variables.

IQ3_S receives a stronger runtime anchor, not an exact-box target change: Strata #440 serves a real
**261,669-261,670-token** IQ3_S prompt on one RTX 5090 / 96-GB host and passes 9/9 needle cases. Exact
**5070-Ti 16-GB + 64-GB-host IQ3_S** admission remains the missing proof.

Current exact-box baseline: **Strata v0.1.34**. An explicit 262,144 context is now preserved by setup on 64-GB PCs;
it is warned rather than forcibly reduced.

### 2026-09-30 exact RTX 5070 Ti filled-context PP true-up

Strata issue #200 finally provides a genuine near-native-context measurement on the target GPU class:
- RTX **5070 Ti 16 GB**, IQ3_XXS native pack, streamed INT8 KV, 32K resident window, MTP spec4;
- **257,466 tokens read from zero in 96.5 s = 2,668 PP** at a configured 262,144 context;
- issue #199 on the same GPU/model path measures two ~60K cold prompts at **2,993 / 3,000 PP** with a
  1,058-MiB manual reserve on 0.1.27. That reserve was the workaround for 0.1.27's draft-head accounting bug;
  **0.1.28+ reserves the draft head before expert-cache sizing**, so the configured reserve remains free without
  carrying the 1,058-MiB workaround forward blindly.

The old 1.5K-class 5070-Ti PP centers are therefore retired. New production-planning centers, with a deliberate
Windows/64-GB-host haircut versus the Linux/93-GB physical receipts:

| Context | IQ3_XXS cold PP target | Evidence status |
|---|---:|---|
| ~32K | **3,000 tok/s** | extrapolated slightly downward from exact ~60K ~3.0K PP |
| ~64K | **2,900 tok/s** | exact-card ~60K anchor ≈3.0K |
| ~128K | **2,750 tok/s** | interpolation between ~60K and filled-257K exact-card receipts |
| ~262K | **2,500 tok/s** | exact-card 257,466-token cold receipt = 2,668 PP |

IQ3_S centers remain **1,550 / 1,550 / 1,350 PP** at 32K/64K/128K until an exact-card IQ3_S ladder lands;
do not transfer the IQ3_XXS uplift numerically without measurement.

The exact-card 151K–257K outputs were **95–118 TG**, but they were list-style answers with favorable draft acceptance.
They establish an optimistic full-context receipt, **not** a generic TG center, so the TG ladder remains unchanged.

### 2026-09-29 full Strata 0.1.22 PP matrix true-up

The complete 0.1.22 prompt matrix on the weaker **RTX 5070 12 GB / Ryzen 5 7600 / 64 GB** now gives:
- IQ3_XXS: **1,555 / 1,449 / 1,386 PP** at 32K / 64K / 128K;
- IQ3_S: **1,499 / 1,285 / 1,245 PP** at 32K / 64K / 128K.

Because every measured row clears the previous P51 5070-Ti center on weaker GPU hardware, the mature PP
targets are raised conservatively to:
- IQ3_XXS: **1,500 / 1,400 / 1,300 PP**;
- IQ3_S: **1,450 / 1,250 / 1,200 PP**.

These are still planning centers, not exact-user receipts. CPU/expert-residency differences can matter, and the
published matrix is one code-agent prompt per cell. Strata 0.1.24 subsequently improves the common long-prompt
QSA-selection path further (Q2_0 128K **1,608 -> 1,843 PP**), but no same-quant 0.1.24 IQ3 matrix exists yet, so
that extra gain is **not** baked into the raised IQ3 targets.

### 2026-09-29 Strata 0.1.22 prompt-path update

The weaker **RTX 5070 12 GB** calibration box now physically clears the IQ3_S 32K PP target during the
0.1.22 prompt work:

- IQ3_S 32K: **1,143 -> 1,213 PP** from the asynchronous expert-stream issuer;
- Q2_0 32K: **1,386 -> 1,646 PP** with the tensor-core QSA prompt-attention path;
- Q2_0 128K: **1,144 -> 1,596 PP** on the combined branch, with KV staging only **1.331 s of 81.3 s**.

The Q2_0 rows prove substantial headroom in the common prompt path, but they are not substituted for IQ3
measurements. The direct IQ3_S 32K receipt is enough to raise confidence in **>=1,200 PP @32K** on the
user's stronger 5070 Ti; it is not enough to raise the 64K/128K IQ3_S centers or any IQ3_XXS center without
a final same-quant long-context matrix.

## IQ3_XXS — balanced production target

| Active context | Mature TG target | TG planning confidence | Mature cold PP target | PP planning confidence |
|---|---:|---:|---:|---:|
| <=8K | **100 TG** | **~75%** | — | — |
| ~32K | **95 TG** | **~75%** | **1,650 PP** | **~90%** |
| ~64K | **90 TG** | **~80%** | **1,550 PP** | **~90%** |
| ~128K | **78 TG** | **~85%** | **1,500 PP** | **~90%** |

Interpretation:
- 64K has the strongest repeated same-card decode support;
- 128K now has a direct **RTX 5070 Ti / IQ3_XXS / Strata 0.1.24 physical anchor at 79.7 TG**, so the 78-TG center is
  no longer primarily an extrapolation. Confidence rises to ~85%, but the center stays conservative because the
  receipt is one machine/workload and speculative acceptance is text/language dependent;
- PP targets are conservative relative to the 12-GB card because 16 GB should hold more experts resident, but an
  exact-card Strata PP ladder has not yet been published.

**Stretch, not canonical:** **90 TG @ ~128K** for IQ3_XXS. Planning confidence **~35–40%** until an
exact-card 128K receipt exists.

## IQ3_S — quality-first target

| Active context | Mature TG target | TG planning confidence | Mature cold PP target | PP planning confidence |
|---|---:|---:|---:|---:|
| <=8K | **85 TG** | **~65%** | — | — |
| ~32K | **78 TG** | **~65%** | **1,550 PP** | **~90%** |
| ~64K | **70 TG** | **~60%** | **1,550 PP** | **~90%** |
| ~128K | **60 TG** | **~55%** | **1,350 PP** | **~85%** |

This lane deliberately sacrifices throughput for quant headroom. Do not raise it from IQ3_XXS speed
receipts without a same-checkpoint physical run.

## Sampling / penalty throughput convention

The TG tables above are **neutral/no-penalty throughput targets** unless a row explicitly says otherwise.
Strata 0.1.19 fixed speculative penalty history so every verified token now sees the same repetition/presence/frequency
history as serial decoding. Correct non-neutral penalties reduce throughput by **~1-11%** in Strata's release testing
because more drafts are rejected. For a production agent configuration that enables penalties, budget this discount
until an exact RTX 5070 Ti 0.1.19+ ladder exists; do not treat it as a kernel regression.

### Draft-vocabulary / candidate-space gate

A speculative lane is not qualified merely because its draft head loads and verifies correctly. Strata issue #137
shows that a compact draft vocabulary can silently exclude the output language: the bundled 40,525-token subset had
only **27 CJK-bearing tokens**, and Chinese-output decode rose **76.8 -> 87.7 TG (+14%)** when the full native head
was used.

Production qualification therefore requires:
- candidate-space coverage for the expected languages and structured/code token domains;
- coverage measured over **actual target-output token occurrences/kinds**, not prompt language alone;
- acceptance broken down by language/domain, not only aggregate acceptance;
- **domain-aware compact expansion first**, preserving the resident expert cache where possible;
- a full-head or fail-open fallback when the compact subset still cannot represent the target distribution;
- verifier-width tuning only **after** candidate coverage is known healthy.

A second RTX 5070 Ti reproduction is the reason for preferring expansion over the full head: expanding the shipped
40,525-id subset to **106,285 ids** for CJK raised English->Chinese translation from **68.1 -> 99.0 TG** while
keeping the expert-cache slot count unchanged; the full 322.1-MiB head was slightly slower and displaced 76 expert
slots.

Do not diagnose low acceptance as an S/kernel/model-quality problem until draft-vocabulary coverage is ruled out.

### MTP draft-asset integrity gate

Strata #327 demonstrates that a mirror/proxy can ignore HTTP Range requests and silently populate MTP tensor files
with the wrong shard bytes while sizes and locally-generated hashes still look valid. Before any acceptance/TG
qualification:
- verify ranged downloads were actually served as HTTP 206 with the expected byte interval, or extract from a
  fully verified source file;
- pin source revision and authoritative tensor byte ranges/hashes;
- sanity-check draft norms/scales for finite, plausible values;
- record offered-draft count separately from accepted-draft count.

A run with `0 accepted of 0 offered` is not evidence of poor acceptance. Draft-vocabulary coverage, draft-asset
integrity and target-arithmetic parity must all pass before changing S or blaming the model.

### Fused-GDN served-arithmetic exactness gate

oMLX PR #4122 demonstrates on an M1 Max that the fused speculative GDN norm can differ by one BF16/FP16 ULP from
the served graph when the float32 exponential implementation differs. For Apple AA/source-equivalence/MTP
certification, require the fused verifier's norm path to match the served arithmetic; close float32 agreement alone
is insufficient.

### Verifier-width / native-expert exactness gate

Strata 0.1.30 adds an explicit width-invariant native i-quant expert mode for issue #152:
`STRATA_IQ_MT_MIN=1`. It uses the multi-token arithmetic from width 1 upward, so a token's target-model expert rows
round the same regardless of the speculative verify window; `native_expert_parity` checks this bit-for-bit.

**AA/source-equivalence/MTP-certification runs must enable `STRATA_IQ_MT_MIN=1`.** The maintainer reports roughly
1-3% decode cost on IQ3_S/AVX-512; IQ3_XXS was about +3% in that test and other arms were within noise. The old
`STRATA_NO_IQ512=1 STRATA_NO_IQ256=1 STRATA_NO_IQ4NL=1` combination remains a conservative fallback/control.

Throughput runs on the default faster width-dependent path remain useful physical measurements, but do not count
them as proof of plain-vs-MTP target arithmetic equivalence.

For **distributed/head/output-row GEMM splits**, arithmetic identity must also include the reduction schedule.
Strata #204 shows that cuBLAS can choose a different split-K for a half-width projection than for the full-shape
projection, changing bits despite algebraically identical GEMMs. A split path must pin a reference-equivalent
algorithm/reduction order or be separately source-certified; same operands and same mathematical result are not
enough.

### Runtime tensor-kind / file-interpretation gate

Before source-equivalence certification, record and assert the actual GGUF tensor kind and byte count for critical
PLE/GDN/QSA tensors against the runtime kernel's expected representation. Strata #303 shows why: an artifact with an
F32 `ple_conv1d.weight` can be raw-cast into an F16 kernel and produce garbage while synthetic F16 parity tests stay
green. The canonical ISTA-DASLab IQ3_XXS allocation explicitly stores `blk.1.ple_conv1d.weight` as F16, so that exact
bug does **not** affect the target artifact; the gate protects future checkpoints/conversions.

## Stability / admission targets

**Qualified Strata baseline: 0.1.31+ for new production tests.** 0.1.31 keeps fixed-cache output
byte-identical to 0.1.30 on the release quants and lands the fixes we were waiting for: request-status cleanup is
ownership-scoped (#266), watchdog exit releases GPU waits before termination (#267), Linux multi-GPU returns to
full-arena pinning (#253), tagged installs are pinned to their own engine/model/dependency revisions, and Windows
gets opt-in `STRATA_ARENA_PIN_GIB=auto` bounded by the shared-memory budget (#243). It also adds the experimental
GGUF-in-place/file-tier path that can run a ~111-GB UD-Q4_K_XL artifact on a 12-GB RTX 5070 + 64-GB host at roughly
7-8.5 tok/s.

0.1.31 is **the qualification baseline, not a completed safety certification**. Keep the exact-box >=8 h soak with
repeated cold long prompts, rapid abort/immediate-retry and concurrent-session handoffs, watchdog/device recovery,
and Windows 64-GB admission/pin-budget checks. The known implementation fixes landing does not replace reproducing
them on the user's exact RTX 5070 Ti + 64-GB configuration. Keep `STRATA_IQ_MT_MIN=1` for certified source/MTP
arithmetic and a qualified CUDA 13.x build on sm_120.

| Production gate | Target | Planning confidence now |
|---|---:|---:|
| sustained single-slot soak | **8 h, zero stalls/watchdogs** | **~75%** |
| extended soak | **24 h, zero stalls/watchdogs** | **~55%** |
| Windows 16-GB/64-GB auto admission | **boots first try, no expert-cache OOM** | **~90%** |
| error recovery with healthy RAM headroom | **restart <60 s** | **~55%** |

### 64-GB-host low-RAM fallback

Strata 0.1.26 can mmap the expert file instead of pinning the entire expert corpus in committed RAM. This is a
**fit/admission fallback**, especially for tight IQ3_S + Windows headroom on a 64-GB host, not the canonical
performance configuration. A published Coder example drops committed memory from roughly **36 -> 13 GB** with the
same answers; small GPUs can become much slower because more experts arrive from SSD.

Do not mix low-RAM-mode measurements into the main TG/PP tables unless the row is explicitly labeled.

Why the stability confidence moved:
- exact 5070-Ti 0.1.14: ~3.5 h / three HE+ sweeps, **zero stalls**;
- another 16-GB Blackwell / 64-GB host reported a few sustained hours with **zero stalls**;
- the remaining admission issue (#60) is a distinct boot-time cache-sizing/fragmentation problem, not recurrence
  of the verify-window NVIDIA-driver-lock deadlock.

## Long-context KV precision lanes

**INT8 K/V remains the quality baseline.**

### Maximum-context target — IQ3_XXS 3.00 bpw + native 262K on 64-GB host

This is now an explicit Project-51 target for the RTX 5070 Ti lane:

- **weights:** DASLab GSQ-RCO **IQ3_XXS, 3.00 transformer bpw**;
- **context:** genuine/native **262,144**, not allocation-only;
- **GPU:** RTX 5070 Ti 16 GB;
- **host:** 64 GB RAM;
- **KV:** Flash/QSA-aware compressed + streamed full-attention KV;
- **protected state:** QSA/indexer **structure** (pending-ring lineage, block/page positions, spare/dead row,
  logical->physical mapping and checkpoint frontier), GDN/recurrent state and MTP/draft state stay exact unless
  separately certified. The normalized **compressed QSA index-key rows** may enter a qualified lower-precision
  storage lane; they are not the same thing as structural indexer state.

Why this is now substantially stronger than a fit estimate:
- Strata issue #200 physically runs **IQ3_XXS on the exact RTX 5070 Ti 16 GB at 257,466 prompt tokens** under a
  262,144-token window with streamed INT8 KV;
- pinned K/V is **1.55 GiB @128K / 3.09 GiB @262K**;
- on the 93-GB Linux host, system RAM available after load is still roughly **44 / 43 GB** at 128K / 262K,
  which implies the steady loaded footprint is far below 93 GB;
- Strata still models IQ3_XXS at **60 GB normal RAM / 42.9 GB expert arena**, and its setup script conservatively
  caps IQ3_XXS at 128K on <90-GB hosts;
- the remaining uncertainty is therefore the **64-GB host's peak simultaneous load/staging + OS headroom**, not
  whether 16-GB VRAM or the Flash state machine can execute genuine 262K.

### Historical TurboQuant candidate ladder — superseded 2026-10-01

This K6/V4 ladder is retained for format/memory history, but it is **no longer the active production candidate**. Current TurboQuant source automatically promotes symmetric Turbo K to Q8 when GQA >= 6; Flash-Next is 12:1. The active Project-51 custom path therefore protects K: built-in K8V4 control, then Q8/INT8-K + Turbo4-V as an optional parity bridge, then **Q8/INT8-K + Turbo3-V** as the capacity candidate. Symmetric/compressed K remains a research arm.

The earlier first custom candidate was **K6/V4**, not symmetric Q6.

The currently audited generic TurboQuant-MLX storage format has:
- 6-bit indices packed **5 per uint32** -> **6.4 physical bpv** before scales;
- one FP16 scale per 64 values -> ~**0.25 bpv** scale overhead;
- K6 therefore ~**6.65 bpv**;
- V4 ~**4.25 bpv**;
- equal-sized K/V -> **~5.45 bpv average storage**.

First-order fit estimate versus Strata's ~8.25-bpv INT8+scale representation:
- **K6/V6:** ~6.65 bpv -> roughly **~2.9 GB @262K**; probably too conservative to create comfortable host margin;
- **K6/V4:** ~5.45 bpv -> roughly **~2.4 GB @262K**; preferred first custom target;
- **K4/V4:** ~4.25 bpv -> roughly **~1.9 GB @262K**; aggressive quality arm.

These are **format-level Strata estimates**, not measured K6/V4 Flash receipts. For geometry context, a separate
llama.cpp Flash-Next implementation physically measures **q8_0 3.19 GiB / q4_0 1.69 GiB / TBQ3 1.15 GiB @256K**,
which brackets the same order of magnitude and confirms that only 12 full-attention layers dominate KV storage.

### Implementation status — proven in Flash llama.cpp research, still missing in Strata

**Correction:** compressed Qwen3.8-Flash-Next KV is not hypothetical. Two public llama.cpp research trees have
implemented TurboQuant/TBQ-style KV for `qwen4exp` while retaining the hybrid sparse-attention model path.

Strongest physical capacity anchor:
- Qwen3.8-Flash-Next **UD-IQ3_XXS**;
- RTX **A5000 16 GB** / 128-GB host;
- `-c 262144`;
- only **12/48** layers hold full-attention KV;
- q8_0 KV **3.19 GiB**, q4_0 **1.69 GiB**, TBQ3 **1.15 GiB** at 256K;
- TBQ3 leaves **51 MoE-cache slots** versus 29 for q8_0 and reports ~**14.5 GiB** peak GPU use.

This means the **16-GB VRAM side of IQ3-class Flash @ native context is physically demonstrated** with compressed KV.
It does **not** prove a 64-GB host fit because that run had 128 GB system RAM.

A second independent Flash fork measures Turbo3 K+V at essentially the same decode speed as q8_0 and about **341 MiB
less GPU memory** in a 131K-class setup; a later short quality check reports roughly **+2.56% PPL vs q8_0**.

What is still missing:
- **Strata** does not yet expose a compressed+streamed TurboQuant Flash KV path;
- **TurboQuant-MLX** intentionally skips Flash's `_AttnCache` because replacing it generically drops QSA indexer state;
- no public implementation yet matches P51's active **Q8/INT8-K + Turbo3-V + Strata streaming + exact QSA/indexer preservation**
  on the user's Windows 5070 Ti box.

P51 implementation should therefore **port/mine proven qwen4exp TBQ plumbing**, not invent the concept from zero:
1. preserve QSA/indexer **structural state** separately and exactly; optionally qualify the normalized compressed
   index-key store as FP8 after the BF16 control passes;
2. compress only the actual full-attention K/V payload;
3. keep host KV compressed at rest;
4. gather only needed/resident cells;
5. dequantize into bounded register/shared scratch in the attention path;
6. never materialize a second full 262K fp16 cache;
7. own Hadamard/rotation exactly once — existing Flash TBQ work found double-rotation to be a real integration hazard.

### QSA compressed-index storage lane

SGLang now provides direct Qwen3.8-Flash-Next evidence that the **normalized compressed QSA index-key cache** can be
stored in **FP8 e4m3** while leaving the pending raw-key ring BF16, the norm/group-mean/RoPE compute path high
precision and the main attention KV unchanged.

On a B300 Qwen3.8-Flash-Next-FP8 xhigh evaluation, BF16-indexer -> FP8-indexer:
- GSM8K: **97.80 -> 97.65**;
- AIME26 pass@1: **98.33 -> 99.17**;
- GPQA-D pass@1: **92.11 -> 91.98**;
- GPQA majority@8: **93.18 -> 92.93**.

For the current compressed-QSA geometry (1 index KV head, 128 dim, ratio 4, 12 QSA layers), the stored-key budget is
about **768 B/token BF16 vs 384 B/token FP8**, roughly **96 MiB saved at 262K**. This is useful margin, not the main
host-RAM lever.

Important boundary:
- structural indexer state remains exact;
- FP8 applies only to the normalized compressed key rows / matching scoring query;
- SGLang currently gates this path to **SM90/SM100**, so the user's **sm_120 RTX 5070 Ti earns no direct memory or
  speed credit** until a Blackwell implementation is qualified.

### Quality priors for the 262K lane

Planning priors, not measured P51 results:
- **physical fit, conditional on a correct Strata compressed-streaming implementation:** ~**90%**;
- **GPU/VRAM + genuine native-context execution:** now directly proven on the **exact RTX 5070 Ti 16 GB** with
  IQ3_XXS + streamed INT8 KV at a 257,466-token prompt;
- **legacy K6/V4 source-like long-horizon quality prior:** ~**60-70%** until Flash-specific 128K/262K evidence exists; this is historical context, **not** the active production candidate;
- **end-to-end production readiness today:** lower than fit probability because the required path is not yet in Strata
  and the 64-GB host margin remains the unresolved part.

Broader TurboQuant evidence argues for caution:
- production-oriented 2026 evaluations prefer 4-bit/no-QJL modes over 3-bit at very long context;
- architecture-specific sweeps find K sensitivity varies materially, with examples ranging from K6/V4 to K8/V4;
- therefore **do not assume K6/V4 passes AA40** simply because the memory arithmetic works.

### Existing implemented controls

**INT8 K/V** remains the source-quality control.

**K8V4** remains the best currently implemented Strata capacity control before whole-cache Q4:
- K stays INT8, preserving the attention-score path;
- V uses Hadamard-rotated Q4_0;
- Strata reports **816 B/cell vs 1,056 B/cell for INT8 (~23% less KV)**;
- on RTX 3090 / Coder at ~198K, the published arm reports **99 TG vs 85 TG INT8**, the same needle result, and
  **2-5% slower prefill**.

K8V4 is not the final 262K solution because it currently **does not support Strata KV streaming**. Full Q4 K/V
remains a lower-precision extreme/capacity arm.

### Apple runtime baseline and pre-M5 mixed-width matrix gate

**Qualified Apple runtime baseline: oMLX 0.7.0** for new stable-baseline comparisons. The release promotes exact
single-request Lightning-MTP verify, the served-equivalent fused GDN norm, rebuilt memory admission, and an M1-Max
native decode-attention correctness fix. It does not provide a new exact dual-M1-Max filled-128K TG/PP receipt.

TensorFold PR #149 and the 0.6.0 release make two pre-M5 Flash-Next bottlenecks concrete: mixed 5/6/8-bit dense
projections can miss the matrix-unit path, and deep sparse-QSA prefill can regress badly if the non-NAX path keeps an
old gather floor/kernel. Add exact-M1-Max A/Bs for the mixed-width matrix backend at S=1 and MTP verify widths,
requiring serial/verify arithmetic equivalence before any speed credit.

Also qualify Apple prefill in **two regimes**: a genuinely cold long prompt and a deep suffix after a retained
60K+ prefix (target shape: ~60K -> 96K/100K). mlx-serve #658 on M3 Ultra measures ~1,190 tok/s cold at 60K but only
~570 tok/s on the 60K->99K suffix while oMLX 0.7.0 remains ~1,190 tok/s on the same box. Treat the diagnosis and M3
numbers as mechanism evidence only; the M1 target does not move.

### Apple long-context MTP / PLE residency qualification

The headline Flash target remains **B1**. Multi-agent serving is a separate gate:
- oMLX #4141 shows that at ~100K, batched Lightning-MTP can win at B1 yet lose badly at B2/B4/B8 because ragged
  rollback physically rolls the whole retained K/V + QSA indexer bank each verify cycle. Count speculative batching
  only when it improves aggregate throughput at the target context after rollback/state-commit costs.
- Capacity-limited Macs with PLE offload must report **cold-PLE/fresh** and **warm-PLE/replay** TG separately.
  oMLX #4140 on M3 Ultra 96 GB measures fresh requests around 62-65 tok/s initially versus ~80 tok/s immediate
  replays, strongly correlated with page-ins in that experiment. PLE warmth is therefore part of benchmark state.

For the M1 lane, B2/B4/B8 qualification must record PLE residency/page-in state, rollback bytes/time, MTP acceptance
and aggregate throughput. A warm singleton MTP win does not promote multi-agent speculation.

Long-prefill qualification must also measure **Metal command-buffer duration versus current state depth**. oMLX #4149
shows a shallow-optimal fixed 1,024-token chunk can survive ~124K yet hit the watchdog deep in a ~245K pipeline run;
depth-aware shrinking avoids the failure without paying the shallow 512-token penalty everywhere. The exact budget is
hardware-specific, so transfer the adaptive rule, not the M5 numeric threshold.

### M1-M4 compressed-KV hardware boundary

oMLX PR #3582 explicitly treats Affine4/Affine8 as an M5-oriented path. On M1-M4 its portable path is a
correctness/capacity fallback and TurboQuant remains the recommended compressed format. Project 51 therefore keeps
TurboQuant-style KV as the dual-M1 priority; M5 Affine 100K/200K capacity receipts do not transfer numerically.

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

### Post-compression recovery control — Victoria

Victoria is **not** folded into the DASLab source-fidelity priors. It is a separate capability-per-byte control:
44% of experts are pruned (512 -> 288), then the compressed model is retrained at 4-bit with quantization-aware
distillation and a final-model draft head.

Published anchors:
- NVFP4 Terminal-Bench 2.1 **70.04% avg@3**, HumanEval **97.0%**;
- GGUF Q4_K_M Terminal-Bench **75.28% (67/89)** vs original Flash-Next **88.76% (79/89)** = **84.8% retained** on
  that one agent benchmark; HumanEval **93.2% avg@5**;
- B300 decode 134.7 tok/s without MTP, 269.3 with the unretrained pruned head, 279.6 with the retrained head;
- M3 Max 128 GB: ~26.8-27.8 -> 34.3-38.0 tok/s with the GGUF draft head, 70.4% acceptance.

After the frozen BF16/Q8/Q6/Q5/Q4/IQ3_S/IQ3_XXS fidelity ladder, run Victoria through the **same** AA, retrieval,
agent/tool, multilingual and long-trajectory suite, but report two axes separately:
1. **source fidelity** versus original Flash-Next;
2. **absolute useful capability per resident byte / per joule / per dollar**.

Do not use Victoria's results to raise the IQ3_XXS AA priors. A future experimental lane may combine sensitivity-aware
pruning/allocation, GSQ/RCO, post-quant QAD and a retrained draft head, but it has no canonical target yet.

## Promotion order

1. Reproduce the **0.1.31+ zero-stall soak** on the user's exact box for >=8 h, including repeated cold long-prompt starts, rapid stream-abort/immediate-retry plus concurrent-session handoffs, and watchdog/device-recovery checks; #266/#267 fixes have landed but remain exact-box qualification items.
2. Resolve or bound the **16-GB/64-GB Windows admission-margin** issue, including whole-arena/sliced `cudaHostRegister` behavior and a bounded-pin control inspired by issue #243; do not transfer the cap to Linux without measurement.
3. Complete a frozen exact-card Strata ladder at 32K / 64K / 128K for IQ3_XXS, then IQ3_S. The
   **79.7-TG IQ3_XXS @128K** report is now a direct anchor, but not a full controlled ladder.
4. Validate draft-vocabulary/language coverage **and draft-asset integrity** (source revision, byte ranges/hashes, finite tensor sanity, offered-vs-accepted counts), then record acceptance by workload before tuning verifier width.
5. Require width-invariant native-expert arithmetic for source-equivalence / AA / MTP certification; on Strata 0.1.31+ enable `STRATA_IQ_MT_MIN=1` and record it with every certified run.
6. Run the AA suite with INT8 K/V as the default quality baseline; test **K8V4** as the currently implemented
   capacity control.
7. If stock INT8/K8V4 still needs more KV margin, port/mine the existing qwen4exp TurboQuant plumbing and qualify the Strata Flash-aware lane in this order:
   **INT8 K/V fidelity control -> K8V4 built-in control -> optional Q8/INT8-K + Turbo4-V parity bridge -> Q8/INT8-K + Turbo3-V capacity candidate -> compressed-K research arms**, preserving QSA structural/recurrent/MTP state exactly and proving rotation ownership.
8. Add the optional **FP8 compressed-QSA-key** lane only after BF16-indexer parity; keep the pending ring, spare/dead key,
   block/page positions and checkpoint frontier exact.
9. For every S>1/MTP sparse path, plan **one union working set across all verify rows before mutation/eviction**.
   Independent per-row residency is a correctness failure even if each row is individually valid.
10. The exact 5070-Ti/native-context execution gate is now passed on a 93-GB host. Issue #224 additionally
    proves a **62-GB Linux host** can load IQ3_XXS and execute an 11,105-token prompt at a 65K configuration when its
    CUDA-12.8 batched-PLE path is disabled; that is partial admission evidence, not a 262K receipt. Finish the
    **64-GB-host** qualification: cold boot/load peak, steady physical RAM, staging overlap, compressed-host-KV bytes,
    32K resident window, repeated 257K cold prefills, and clean recovery under memory pressure on CUDA 13.x.
11. Run the 262K semantic gate separately: needles/MRCR, xhigh AA, long agent/tool trajectories and MTP acceptance.
    The 29K->257K retrieval decline in issue #200 proves that “it fits” is not the same as “it retains semantics.”
12. On the Apple lane, A/B TensorFold-style mixed-width dense matrix routing on the exact M1 Max at S=1 and verify widths, measure prefill both cold and as a ~60K->96K/100K retained-prefix suffix, verify advertised-window admission/retention as first request/after a tiny request/after a retained turn, benchmark B1/B2/B4/B8 with cold-vs-warm PLE state, and sweep prefill chunk size versus state depth/command-buffer duration; require bit/arithmetic equivalence, no deep-QSA/admission/watchdog collapse, and a real aggregate MTP win after rollback costs.
13. For long-context MTP changes, separately certify verify-attention reduction order and accepted recurrent-state commit/pairing; vLLM #59448 and SGLang #40001 show that speed/acceptance alone can hide trajectory or accuracy changes.
14. Freeze the pure-PTQ AA ladder first; then add **Victoria** as a separate post-compression-recovery control and report source fidelity separately from absolute capability-per-byte.
15. Only after those pass, optimize 262K throughput and resident-window size; do not retreat to IQ2_XS solely because
    stock Strata's current setup script caps IQ3_XXS at 128K.

---

# 3c. Qwen3.8-Flash-Next — RX 6800 16 GB + 64 GB DDR4 (secondary lane)

This is a **secondary planning lane**, not a canonical Project-51 target.

A post-boundary update to Strata PR #311 gives the first strong same-architecture anchor: RX 6900 XT 16 GB
(gfx1030) + 63 GB host RAM + Swift 1.5 IQ3_XXS at a genuinely full 131,072-token context sustains **38-42 tok/s**
with the default 15 CPU workers. Prefill is **246 tok/s at ~2K** and **330-339 tok/s** with auto 8K chunks; decode
after 16K reaches 45.5 tok/s. The PR is still open and gfx1030 remains experimental.

For the user's RX 6800 16 GB + 64 GB DDR4, plan around:
- **~28-36 tok/s** short-to-128K decode;
- **~27-34 tok/s** at genuinely filled ~128K;
- **~220-300 tok/s** cold prefill order-of-magnitude.

A new exact-card receipt now anchors the short-context floor: Strata PR #376 reports an **RX 6800** at
**28.1-28.3 tok/s decode** when HIP kernels are correctly compiled with release optimization. The same build folder,
after a failed first configure poisoned the cached HIP flags and left kernels at `-O0`, ran only 0.24-0.27 tok/s.
That receipt is Windows/HIP SDK 7.2, Strata 0.1.30 + the Windows HIP work, expert cache 2048, and does **not** publish a
filled-128K denominator.

Therefore the **~28 tok/s lower edge is now exact-GPU physical evidence**, while the upper short-context bound,
filled-128K **~27-34 tok/s**, and **~220-300 PP** remain transferred/inferred from the RX 6900 XT gfx1030 receipt.
The user's exact Ryzen/Linux configuration and canonical DASLab checkpoint still need direct measurement.

Promotion gate: merged/validated gfx1030 support, exact RX 6800 **64K/128K filled-context TG+PP**, MTP acceptance,
release-build flag verification, and an AA/quality smoke test. Until then this remains a useful background-agent node,
not a headline system target.

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

Cross-cutting systems priority: **persistent canonical agent-root images** now sit ahead of incremental
cold-PP tuning for invariant system/tool prefixes. They do not change the hardware ranking below because
restore latency and cold PP are separate metrics.

Persistent-root correctness now additionally requires:
- **domain separation:** an exact system/tool root carrying terminal recurrent/GDN state must not enter ordinary
  partial-prefix matching as if it were a generic token/KV block;
- **bounded tail lineage:** retain only the explicitly required edited-turn/private-suffix generations rather than
  accumulating one full recurrent/QSA tail per turn;
- **admission credit for owned restored state:** a prefix already restored into owned cache slots is not billed again
  as if every token were a fresh allocation;
- **durable backing before eviction credit:** a GPU page counts as reclaimable only when its host/disk backing and
  transfer ownership are already reserved.

Strata PR #189 now provides a strong mechanism receipt: IQ3_S snapshot/restore parity across INT8 streamed/ring and
K8V4 cases plus a 30-cycle soak reaching **119,987-token** prompts. It strengthens the state-image design but is not
a throughput or exact-user-hardware result.

Restore/import frontiers are now explicitly **monotonic commitments**: SGLang #41450 shows that a cache tree can grow
while a restore is pending, causing a later lookup to match more tokens than the consumer was promised. P51 must clamp
every restore/import to the committed frontier established at admission/export; a fresher lookup may discover more
state, but it cannot silently extend the transaction already in flight.

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

**Long-context batching gate:** do not assume shared weights make B2/B4 aggregate throughput exceed B1. An M1 Ultra
Qwen3.8-27B/oQ4e/TQ8 run at ~20K context measured **21.7 TG solo but only ~11.2 TG aggregate for two concurrent
MTP-off rows**, while short-context two-way reached **28.9 aggregate**. This is cross-hardware dense-model evidence,
so it does not move the dual-M1 Flash ladder numerically, but it makes a context ladder mandatory.

Before promoting any B2-B4 target, measure B1/B2/B4 at minimum **16K / 32K / 64K / ~128K active context**, record
per-step bytes/effective bandwidth/kernel path, and reject a scheduler optimization that raises short-context
aggregate TG while collapsing at long context.

Also treat speculative decoding itself as cohort-dependent. oMLX Qwen3.8-Flash-Next on M5 Ultra reports **B8 aggregate
272 TG with shared MTP vs 293 TG with MTP off**; the runtime spends 81.5 ms on an 8-request depth-3 verify versus
23.9 ms on a normal 8-row step. The scheduler must be allowed to park MTP immediately on a clear loss and retain that
verdict across a stable cohort instead of repeatedly relearning it after joins/finishes.

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