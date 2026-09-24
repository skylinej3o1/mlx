# Project 51 primary-lane research watch — 2026-09-24 16:14 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 17:23:35 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 20:14:25 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

No exact dual-M1/TB4 Flash-Next S=2-8 verifier receipt appeared, no direct Apple7 PP2 overlap measurement appeared, and no new precisely timestamped DASLab/ByteShape source-vs-quant xhigh behavioral certification appeared.

This pass nevertheless adds strong implementation evidence in three areas:

1. **Exact Flash-Next prefill:** oMLX #3903 raises M5 Max prefill **24-32%** by stacking GDN, HyperConnection, MoE, QSA, PLE, and chunking changes without changing the core model math.
2. **Workload-selective speculation:** mlx-serve #523 uses prompt/context lookup to replace some MTP chains and reports **+17%** across an 11-task agent set and **+31-48%** on copy/edit workloads.
3. **Warm-agent state:** production verification of #3901 shows exact tail-boundary MTP history restore raises accepted tokens/cycle from roughly **2.34-2.47 to 3.62-3.92**, but also exposes a restart/orphan-chain case where memory-only MTP history never self-rebuilds.

## Findings

### NEW — oMLX #3903: exact Flash-Next prefill rises 24-32% from stacked architecture-specific work

Source: https://github.com/jundot/omlx/pull/3903  
Merged commit: **3e2bdb1fea55** at **2026-09-24 18:43:24 UTC**.

M5 Max 128 GB, Qwen3.8-Flash-Next-oQ4e-mtp, Lightning MTP, PLE SSD offload:

| Prompt | Main PP | PR PP | Gain |
|---:|---:|---:|---:|
| 4K | 1,579 | **1,952** | **+23.6%** |
| 16K | 1,522 | **2,007** | **+31.9%** |
| 16K paged | 1,507 | **1,975** | **+31.0%** |
| 64K | 1,326 | **1,716** | **+29.4%** |
| 64K paged | 1,321 | **1,729** | **+30.9%** |

The implementation stacks several independent prefill changes:
- **GDN:** fused conv/norm prework plus gated norm;
- **HyperConnection:** fewer passes over the 10,240-wide residual stream;
- **MoE:** native weighted-sum now supports Flash-Next top-k=10;
- **QSA:** plain causal attention for early rows, sorted native top-k output, query tiles 256 -> 1024;
- **PLE:** vectorized n-gram lookup;
- **chunking:** 2048 first chunk then 8192-token chunks on large NAX hosts, with paged-cache geometry following.

Validation:
- fused GDN prefill final logits and all 122 cache arrays bitwise equal to stock on the checked real-model chunked prefill;
- fused HC write/norm bitwise equal;
- post-prefill argmax equal on all four 4K/16K probes;
- reported PR-vs-main KL 0.005-0.014, within the scale of main-vs-main chunking variation reported in the PR.

Peak memory at 16K/64K rises by roughly **~3 GiB** because of 8192-token chunks.

**Classification:** NEW exact-family stronger-Apple PP evidence.

**P51 consequence:** the 400-PP thesis is increasingly an **implementation problem rather than a Flash architectural impossibility**. GDN recurrence, HC, QSA, MoE and PLE each leave prefill headroom that can stack. But M5 Max percentages do not transfer to M1, and the +3-GiB chunk-memory tax matters on 64-GB nodes. P51 should benchmark chunk width as a joint **PP / peak-memory / state-correctness** parameter.

**Target impact:** none. The missing measurement is still balanced half-model M1 stage PP under the final quant and PP2 topology.

### NEW — mlx-serve #523: prompt lookup can replace some MTP rounds on agent/copy workloads

Source: https://github.com/ddalcu/mlx-serve/pull/523  
Created **2026-09-24 17:30:44 UTC**.

When recently committed tokens plus t1 match an earlier span in the prompt/output, the runtime can verify the earlier continuation instead of running an MTP chain. The gate compares expected tokens-per-cost against the MTP chain it would replace.

M5 Ultra 256 GB, Qwen3.8-Flash-Next mixed-4/8bit, bf16 KV:

- 11 agent-style tasks, greedy, token-weighted: **185.6 -> 216.5 TG (+16.6%)**
- repeat/return edited file: **197-214 -> 278-311 TG (+31-48%)**
- unified diff / JSON tool payload / prose / new code: **roughly flat (0.96-1.02x)**
- 32K decode three-round cell: **95.2 -> 100.3 TG**
- broad greedy/sampled cells otherwise overlap.

At four concurrent copy-heavy streams:
- lookup on: **172.9 / 178.3 aggregate**
- off: **165.2 / 165.5**
- only **~1.06x**, because lookup currently fires mainly on solo rows (15-18% of tokens) versus ~83% at B1.

The same comment exposes a planner issue: at 98-99% draft acceptance, grouped width-2 can be priced faster than plain decode but still not selected because the planner compares against an optimistic plain lower bound; width-4 may never collect samples when its predicted latency exceeds the fixed latency cap.

Maintainer review explicitly notes that lookup cost constants are currently fit to **M5 Ultra + Flash-Next** and should instead read measured per-chip/model round cost before any default enablement.

**Classification:** NEW exact-family Apple speculative mechanism evidence.

**P51 consequence:** this directly validates the existing P51 **history/self-speculation** branch for code-edit and tool-agent workloads. It should remain opportunistic and cost-gated, not part of the generic xhigh 40-TG denominator. The controller should choose among target-only, MTP, and history/prompt lookup using **measured landed tokens / measured current cost**, with hardware/model-specific cost tables.

### UPDATE — oMLX #3895/#3901 production verification: full MTP history restore recovers acceptance and has negligible steady-cycle tax

Source: https://github.com/jundot/omlx/issues/3895#issuecomment-5819959390  
Fresh comment: **2026-09-24 18:41:18 UTC**.

Production M3 Ultra / Flash-Next-oQ4e-mtp warm tail-hit telemetry:

| | Before #3901 | After #3901 |
|---|---:|---:|
| MTP primed | 7 | **1176** |
| tokens/cycle | 2.34-2.47 | **3.62-3.92** |
| acceptance | 71-74% | **97-100%** |

Per-cycle backbone cost after restore:
- warm restore **26.3 ms/cycle**
- natural path **26.2 ms/cycle**

The reconstruction itself costs ~12-50 ms once per request, around ~0.4 ms/cycle amortized over the observed ~35-cycle request.

This strengthens the prior conclusion: preserving draft/MTP state at the exact cache boundary is not just correctness—it materially changes speculative economics.

A new gap remains:
- MTP sidecar is memory-only;
- after server restart, a target prefix restored from SSD has no MTP sidecar;
- suffix-only priming does not satisfy the current capture condition;
- repeated warm hits therefore **never self-heal** that chain.

Suggested mitigations are either versioned sidecar persistence or a draft-head-only replay of the cached prefix to rebuild history.

**Classification:** UPDATE / exact-family warm-agent state evidence.

**P51 consequence:** persistent warm-agent state needs a **restart bootstrap contract**. A semantically valid target cache hit must not permanently strand the draft model in suffix-only history. If MTP state is not persisted, rebuild it deliberately once and publish a new compatible frontier.

### KNOWN/UPDATE — SGLang #40041 merged: target-verify PLE preparation fusion

Source: https://github.com/sgl-project/sglang/pull/40041  
Merged commit **b129504f0efd** at **2026-09-24 20:13:34 UTC**.

Substantive result was already durable:
- Qwen3.8 target verify PLE gate/convolution preparation fusion;
- about **2% E2E decode**;
- AIME26 **95%**;
- acceptance unchanged.

**Classification:** KNOWN/UPDATE (merge only). No new numeric conclusion.

### NEW / cross-family Metal — llama.cpp #29377: sparse-attention index placement improves long-context Metal PP, little TG

Source: https://github.com/ggml-org/llama.cpp/pull/29377  
Merged commit **cdc06426e70c** at **2026-09-24 19:44:36 UTC**.

DeepSeek-V4-Flash-Vision Q2 on Metal, moving sparse-FA indices to threadgroup/shared memory:

At 65,536 prompt tokens:
- PP **304.43 -> 348.12 tok/s (+14.4%)**
- 32-token TG **23.72 -> 23.90 (+0.8%)**

At 32,768:
- PP **360.07 -> 378.33 (+5.1%)**
- TG nearly flat.

**Classification:** NEW cross-family Apple prefill mechanism evidence.

**P51 consequence:** sparse-attention metadata movement can remain material to long-context PP while barely affecting decode. This supports profiling QSA index movement separately in the Apple7 PP path, but no percentage transfer to Flash-Next.

### UPDATE / caution — Splash #131 M2 Ultra failure at 64K

Source: https://github.com/incoai/splash/issues/131#issuecomment-5819563113

A user reports Qwen3.8-27B Splash on **M2 Ultra 128 GB**:
- 32K benchmark works;
- 64K PP/TG test triggers engine recovery / native transport stop.

No root cause was established by the cutoff.

**Classification:** UPDATE / unresolved reliability report.

**P51 consequence:** no performance inference. Apple-family kernel speedups require explicit **filled-context reliability qualification**, not only short/32K speed cells. Keep 64K/128K soak and recovery behavior in the Apple7 certification matrix.

### SCREENED — DS4 #1120 M5 shape specialization shows why microbench gains cannot be summed

M5 Max resident V4/GLM shape-specialized kernels show isolated wins of a few percent, but combined whole-model decode gains only:
- V4 Flash **~0.86-1.06%**
- GLM 5.3 Flash **~1.38-1.48%**

Some isolated kernels are even slower while whole-model routing still improves.

**P51 consequence:** maintain the current rule: only real-model A/B moves the performance ledger; do not sum isolated kernel percentages.

### Quant / community search

- **ISTA-DASLab/GSQ:** no in-window GitHub issue/PR/commit activity.
- **ByteShape:** no precisely timestamped new source-vs-quant Flash-Next behavioral receipt inside this strict interval.
- A same-day LocalLLaMA post reports a custom CUDA Flash-Next engine at 128K with low-bit GSQ/RCO-family quants and high throughput, and a same-day UkisAI Swift release reports large thinking-token reductions. The web surface exposes only "today", not a precise publication time, so neither is promoted into this strict delta. The Swift branch also deliberately changes reasoning behavior and is not source-like P51 evidence.
- No new exact dual-M1/TB4 receipt was found.

## Canonical planning state after this pass

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target; Apple7 + heterogeneous quant + verifier co-design remains an experimental upside lane.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 20:14:25 UTC**
