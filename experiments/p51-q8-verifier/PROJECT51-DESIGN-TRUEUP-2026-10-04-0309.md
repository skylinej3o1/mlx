# Project 51 design/source true-up — 2026-10-04 03:09 ET

**This is not a comprehensive strict-window research pass.**
The formal search hard boundary remains **2026-10-04 00:51:42 UTC**.
This note persists the targeted source audits and design recalculation performed after that boundary so the next
strict search can classify them as KNOWN rather than rediscover them.

## Executive change

Project 51's dual-M1 Flash-Next production lane is now centered on the public **ISTA-DASLab IQ3_S** artifact rather
than on a hypothetical custom 3.4-3.6-bpw artifact.

New production goal:
- **DASLab IQ3_S**
- **2x M1 Max 64 GB over TB4**
- **native 262,144 context**
- **>=35 TG sustained**
- **>=400 cold PP**
- xhigh-only production quality certification.

Performance goal:
- **~128K active context**
- **>=40 TG**
- **>=425 cold PP**.

Stretch:
- **>=40 TG at native262K**.

The old 40-TG / 400-PP @128K target remains useful as historical context, but the production success criterion is now
the full-native-context 35/400 goal because the user's real coding/Playwright sessions can reach ~262K+.

## Source A — paperniuk/ds4 M1 Flash-Next fork

Repository:
https://github.com/paperniuk/ds4/tree/m1-flash-next

This is a credible primary-source M1-Max receipt and a major implementation donor.

### Exact measured M1 Max 64-GB anchors

M1 Max, 32-core GPU, 64 GB:

Q2_0:
- ~4K: 35.5-37.7 plain / **44-45 TG with MTP**, ~355 PP;
- 128K: 36.0 plain / **43.4 MTP**, ~345 PP;
- 256K: 32.9 plain / **37.4 MTP**, ~290-320 PP;
- one chat grown to ~398K: ~35 MTP TG, ~292 PP.

IQ3_XXS:
- ~35 MTP TG short;
- ~34.2 around 128K;
- ~31.7 around 259K.

IQ3_S:
- **~26 TG plain / ~32-34 TG with MTP at short context** on the same M1 Max;
- currently memory-limited to a small window on a single 64-GB Mac, so there is no physical 128/262K IQ3_S
  one-M1 receipt yet.

### Why the speedup is credible

The fork implements exactly the classes of M1 work Project 51 had been hypothesizing:
- Apple7 mixed-IQ matvec kernels;
- 2/3-row expert kernels that read weights once for MTP verification;
- long-context QSA/indexer/top-k/attention kernels on pre-M5 Apple GPUs;
- prompt expert tail/remainder tiles;
- overlap of n-gram SSD reads with layer-0 compute;
- faster sampler;
- prompt/cold-cache anchors for agent resume.

One especially useful measured mechanism:
- long-context indexer/attention work moved plain decode at ~128K from **23.8 -> 33.8 TG** with byte-identical output.

This materially lowers the software-risk prior behind Project 51. The old ~25-27 target-only / ~39-41 mature-system
model was too pessimistic because important M1-specific long-context kernels have now been demonstrated physically.

### IQ3_S quality shorthand

For engineering planning, **DASLab IQ3_S may be treated as conventional-Q5-class task quality at ~3.5-bpw
transformer economics**.

This is only a shorthand:
- it is not numerical/source equivalence;
- it is not permission to skip xhigh agent certification;
- near-tie logits, very long trajectories, tool loops, multilingual edge cases and replay/state equivalence remain
  explicit gates.

IQ3_S remains the quality-first production artifact. IQ3_XXS is a speed/capacity control, not the preferred
production quant.

## IQ3_S memory recalculation

The ds4 fork's launcher uses:
- IQ3_S base: **~55.2 GiB** with MTP/vision planning;
- context slope: **~33 KiB/token**;
- explicit extra reserve: ~2 GiB.

Its formula puts native262K around:
- 55.2 GiB base
- + ~8.69 GiB context/state
- + 2 GiB reserve
- = **~65.9 GiB total planned memory**.

That is the key new fact:
**native262K IQ3_S is only slightly too large for one 64-GB M1 Max, not remotely too large for two.**

The ~26.8-28.8-GiB n-gram/PLE shard does not need to be resident; the M1 fork already reads the relevant rows from
SSD.

Across 2x64 GB, capacity is therefore easy. The problem is choosing the topology that preserves decode latency.

## Recalculated dual-M1 targets

These are derived engineering targets, not measured dual-M1 receipts.

| IQ3_S / 2x M1 Max 64 GB | Initial bring-up | Mature realistic | Project-51 target | Stretch |
| --- | ---: | ---: | ---: | ---: |
| TG @ ~128K | 25-28 | **34-38** | **40** | 45+ |
| TG @ 262K | 23-26 | **31-35** | **35** | **40** |
| cold PP @ ~128K | 330-380 | **420-460** | **425+** | 500 |
| cold PP @ 262K | 330-380 | **390-430** | **400** | 450+ |

Planning confidence:
- clean IQ3_S/native262K fit across two M1 Maxes: **>=90%**;
- >=400 cold PP at native262K: **~80%**;
- >=35 TG at native262K: **~70-75%**;
- >=40 TG at ~128K: **~70-75%**;
- >=40 TG at native262K: **~45-55%**.

These remain engineering priors, not statistical confidence intervals.

### Why these rates are now plausible

The single-M1 IQ3_S short MTP anchor is already ~32-34 TG.
IQ3_XXS loses only about 10% moving from short context to ~260K in this tuned engine.

A first interpolation therefore puts a hypothetical sufficiently large one-M1 IQ3_S around:
- roughly **31-33 TG @128K**;
- roughly **28.5-30.5 TG @262K**;

before using the second M1 as an optimization resource.

For cold PP:
- tuned one-M1 low-bit Flash is already roughly high-200s/low-300s at deep context;
- ds4's existing generic two-machine pipeline machinery has demonstrated strong long-prompt stage overlap on other
  models;
- **400 PP at native262K is therefore now a plausible engineering center rather than a speculative wish**.

Do not double-count the MTP gains: paperniuk/ds4 already includes 2/3-row verification and existing MTP uplift.

## Dual-M1 architecture bakeoff

Qwen3.8 Flash-Next distributed execution is **not implemented in the paperniuk fork yet** even though upstream ds4 has
general network TP/pipeline support for other models. Project 51 still owns this engineering.

Three topologies must be compared.

### A. Balanced layer pipeline

- split contiguous layer ranges roughly evenly;
- each Mac owns its local recurrent/QSA/KV state;
- hidden activations cross TB4 at one stage boundary;
- best for capacity and cold-prefill pipeline overlap.

Risk:
- autoregressive decode is serialized across the boundary;
- existing generic distributed ds4 controls show a material decode penalty in conventional pipeline mode.

Use as the simplest bring-up / capacity control.

### B. Asymmetric dual-M1 decode split

Possible design:
- balanced stage assignment during cold prefill;
- after prefill, migrate a subset of layer state once;
- skew decode ownership so Mac A holds most target layers and Mac B owns only a small tail + output/MTP.

Why it may work:
- Qwen hidden width is only ~2560, so BF16 inter-stage activations are only about 5 KiB/row;
- bandwidth is therefore not the fundamental TB4 problem;
- round-trip synchronization/bubble is the real cost;
- one-time post-prefill state migration may be cheap relative to a 128-262K cold prefill.

This is a Project-51 design hypothesis, not a measured receipt.

### C. Almost-local IQ3_S + shallow SSD expert spill

This topology became credible after the Slipstream audit below.

Goal:
- Mac A runs essentially the complete target forward locally, including full 262K state;
- only a shallow slice of routed-expert weights is absent from RAM and is predictively streamed;
- Mac B becomes a helper rather than a mandatory per-token target stage.

Using the ~65.9-GiB full IQ3_S/262K plan:

| Desired Mac-A resident budget | Approx. bytes that must leave Mac A |
| ---: | ---: |
| 54 GiB | **~11.9 GiB** |
| 56 GiB | **~9.9 GiB** |
| 58 GiB | **~7.9 GiB** |

Not all bytes are spillable; context/runtime state must remain local, so the removed bytes should come from the routed
expert bank.

This is a dramatically smaller streaming problem than Slipstream's measured larger-than-RAM model.

If shallow spill preserves >=35 TG, this may be preferable to putting the target critical path across TB4.

## Source B — Slipstream

Repository:
https://github.com/npanj/slipstream

Slipstream is **not** a Project-51 quality artifact. It is an implementation/mechanism donor.

It runs a ~95.5-GiB custom Qwen3.8-Flash-Next/Swift model on a **64-GB M5 Pro** using:
- SSD expert streaming;
- predictive expert read-ahead;
- prompt-lookup drafting + MTP;
- QSA kernels;
- Metal-mapped n-gram tables.

Reported M5-Pro telemetry:
- six-task benchmark average ~40.8 TG;
- 3,086 live agent requests;
- 32-64K: ~35.0 TG average;
- 64-96K: ~32.4;
- 96-130K: ~32.9;
- no obvious long-context decode collapse through the measured 130K regime.

Do **not** transfer these rates to M1 Max:
- hardware is M5 Pro;
- checkpoint/quant is different;
- Swift/plain V3 benchmark evidence is not comparable to DASLab IQ3_S's quality evidence.

### Durable Project-51 lessons from Slipstream

1. **Predictive SSD expert streaming is viable enough to test for a shallow IQ3_S spill.**
   Slipstream is solving a larger overflow problem than the ~8-12 GiB Project-51 shallow-spill case.

2. **Prompt/context-copy speculation is real and highly relevant to the user's workload.**
   Together with TensorFold #319, this gives independent support for:
   - copy proposal first;
   - then MTP;
   - then ordinary target fallback.

   This is particularly relevant to brownfield Playwright work where the model often rewrites fixtures, configs,
   tests and code already present in context.

3. **N-gram/PLE residency is not required.**
   Both the paperniuk fork and Slipstream independently show practical architectures where large auxiliary tables
   live outside the main resident weight set.

## Revised implementation priority

For the dual-M1 Flash-Next lane:

1. Reproduce paperniuk/ds4 on one M1 Max:
   - Q2 control;
   - IQ3_XXS 128/262K;
   - IQ3_S short-context;
   - exact speed/memory/thermal telemetry.

2. Port/load DASLab IQ3_S as the canonical production artifact.

3. Measure exact one-M1 IQ3_S memory components:
   - resident weights;
   - attention/QSA state;
   - recurrent/GDN state;
   - MTP state;
   - transients;
   - n-gram/PLE I/O;
   - available expert-cache/spill budget.

4. Run the three topology bakeoff:
   - balanced dual-M1 pipeline;
   - asymmetric decode split;
   - almost-local + shallow expert spill.

5. Promote the topology that best satisfies **35 TG / 400 PP at native262K** with source-like xhigh behavior.

6. Only after base correctness:
   - deeper multi-row verifier work;
   - copy-from-context proposals;
   - draft-vocab tuning;
   - resident-agent/persistence optimizations;
   - multi-agent scheduling.

## What is superseded

The September assumption that a source-like xhigh artifact would begin around only ~25-27 target-only TG @128K is
superseded by the new physical M1-Max kernel receipts.

The old Project-51 headline **40 TG / 400 PP @128K** is no longer the sole production definition.

New canonical goals:
- **production:** IQ3_S, native262K, >=35 TG, >=400 cold PP;
- **performance:** IQ3_S, ~128K, >=40 TG, >=425 cold PP;
- **stretch:** IQ3_S, native262K, >=40 TG.

The quality rule remains unchanged:
**speed never promotes a quant that fails the xhigh agent/coding/tool/long-context/state certification suite.**
