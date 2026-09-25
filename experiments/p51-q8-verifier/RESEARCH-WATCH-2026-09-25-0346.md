# Project 51 primary-lane research watch — 2026-09-25 03:46 ET

**Freshness boundary checked:** prior hard boundary **2026-09-25 00:45:51 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-25 07:46:32 UTC**.

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

This pass adds strong regime-specific evidence:
1. target-only routed-expert fusion can materially help Flash-Next while providing essentially no MTP gain;
2. prompt/history lookup transfers well from M5 Ultra to M4 Max on copy/edit workloads while remaining neutral elsewhere;
3. 4-bit KV is primarily a capacity/headroom lever at low concurrency, not automatically a B1 speed lever;
4. warm-prefix memory accounting can double-bill already-restored rows and reject a ~198K agent turn despite most state being resident.

## Findings

### NEW — oMLX #3912: one-token Flash routed experts collapse five dependent launches to two, +6-8% target-only decode, zero measurable MTP gain

Source: https://github.com/jundot/omlx/pull/3912  
Created **2026-09-25 00:51:38 UTC**.

Qwen3.8-Flash-Next target-only routed-expert decode after the fused router previously performs five dependent operations per MoE layer:
1. gate+up gather QMM,
2. SwiGLU,
3. down gather QMM,
4. multiply by router score,
5. sum across 10 selected experts.

Across 48 MoE layers, #3912 reproduces the same arithmetic in two launches:
- gate+up + SwiGLU epilogue;
- down + weighted sum.

M5 Max 128 GB, Qwen3.8-Flash-Next-oQ4e-mtp, PLE SSD offload, Lightning MTP **off**:

| prompt | baseline | fused | gain |
|---:|---:|---:|---:|
| 4,174 | 54.9 TG | **58.6** | **+6.1%** |
| 14,592 | 53.7 | **56.8** | **+8.2%** |

All 20/20 paired runs were faster at both points. Peak resident memory was essentially unchanged (~52.2-53.4 GiB), TTFT unchanged, and real-model greedy logits/completions were bit-identical.

With Lightning MTP **on**, target verification uses multi-row kernels and keeps the composed path. The new fused decode kernel executes only ~60-170 times per 128-token request instead of 6,192 times and showed **no measurable throughput improvement**.

**Classification:** NEW exact-family stronger-Apple target-only evidence.

**P51 consequence:** maintain separate **S=1 target-only** and **S=2-8 verifier** optimization ledgers. A large target-only win does not automatically lower verifier target-forward-equivalent cost. Conversely, an Apple7 S=1 kernel can still improve the 24-27 TG fallback without helping the 40-TG speculative path.

The mechanism is strongly relevant to Apple7 because it removes dependent launches, but no M1 percentage is transferred.

### UPDATE — mlx-serve #523: prompt lookup transfers to M4 Max and is flat when no useful repetition exists

Source: https://github.com/ddalcu/mlx-serve/pull/523  
PR closed/merged in this window.

M4 Max 128 GB, Flash-Next mixed 4/8-bit, exact acceptance, greedy:

| task | base | lookup |
|---|---:|---:|
| copy ~1.8K-token file | 110 / 104 | **133 / 146** |
| rename one function, return file | 105 / 103 | **136 / 145** |
| new code | 99 / 89 | 92 / 98 |
| prose | 77 / 77 | 74 / 78 |

Qwen3.8-27B 4-bit on the same M4 Max:
- copy/edit workloads improve roughly **~50%**;
- new code/prose remain essentially flat;
- lookup lands ~**98%** of copy-task drafts;
- exact-copy outputs are byte-identical in every arm.

A fresh M5 Ultra profile also shows PLE gather itself is only ~0.305 ms of a 29-33 ms MTP round there (~1%), so moving the already-hot 32-GB n-gram table onto GPU would not be the largest bottleneck on that machine.

At four concurrent streams, experimental wider fused verify hardware raises aggregate throughput roughly **+8%**, but can reduce single-stream sampled performance 5-7%, suggesting the gate should depend on row count rather than chip identity.

**Classification:** UPDATE / stronger Apple workload-selective speculation evidence.

**P51 consequence:** history/prompt lookup is now demonstrated across both M5 Ultra and M4 Max. Keep it as a third adaptive arm for agent workflows, not part of the generic 40-TG denominator. Selection policy should be **mechanism x row-count x current measured cost**, not merely hardware family.

### NEW — mlx-serve #528: SSD-restored warm rows can be double-billed by admission and destroy a valid 198K warm turn

Source: https://github.com/ddalcu/mlx-serve/issues/528  
Created **2026-09-25 06:29:40 UTC**.

M3 Ultra 96 GB, Qwen3.8-Flash-Next full-512 3.3-BPW, MTP, 262K context.

A ~197,945-token agent turn restores:
- **193,961 tokens from SSD**;
- corresponding MTP head state.

Only ~4K tokens are actually new. Nevertheless the prefill estimator bills ~9.2 GB as though the **whole 197,945-token prompt** needs fresh KV, evicts ~9.5 GB of hot-cache entries, then rejects the request with `PrefillDoesNotFit`.

The likely source-side cause in the report:
- RAM checkout marks restored buffers as owned/donatable;
- disk restore leaves `checked_out=false`;
- admission therefore credits zero restored rows even though the rows were already restored into the request's own target cache;
- live available memory already excludes those buffers, so the same memory is counted twice.

A retry seconds later succeeds.

The report also identifies a neighboring RAM-hit case where the connection-side admission counted a hot entry as reclaimable before the incoming request pinned it, so the later scheduler could not actually reclaim the memory it had assumed.

**Classification:** NEW exact-family long-agent admission evidence.

**P51 consequence:** memory admission must be computed from **post-restore ownership and post-pin reality**, not pre-lookup reclaimability. Restored rows that are owned by the slot must be credited exactly once. Avoid destructive cache eviction until final admission is certain. For P51, the warm-state byte ledger must distinguish:
- resident and owned by this request;
- resident but shared/pinned;
- reclaimable;
- restorable but currently non-resident;
- new bytes still required.

### NEW — vLLM #57057: exact Flash-Next 4-bit KV preserves GPQA quality and delays the 262K concurrency eviction wall

Source: https://github.com/vllm-project/vllm/pull/57057  
Updated in-window.

UltraQuant 4-bit KV for D=256 attention was tested on Qwen3.8-Flash-Next at **262K-token requests** on MI355X.

GPQA-Diamond, multiple seeds:
- UltraQuant 4-bit KV: **93.27%**
- FP8 KV baseline: **92.42%**

The PR states the decode kernel itself is numerically exact and per-seed benchmark differences are sampling variance.

Throughput/capacity, TP8:
- C8: UQ **193.9** vs KV8 199.4 (-2.7%)
- C16: **280.2** vs 288.0 (-2.7%)
- C32: **374.0** vs 363.1 (+3.0%)
- C36: **398.9** vs 299.6 (+33%)
- C38: **414.6** vs 225.4 (+84%)
- C42: **430.7** vs 114.7 (+275%)

At C38 the FP8 KV cache hits 100% / eviction; UQ is only ~44% full.

**Classification:** NEW exact-family low-bit-KV capacity evidence, cross-hardware.

**P51 consequence:** 4-bit KV should primarily be modeled as a **capacity/headroom lever**, not assumed to improve B1 decode. At low concurrency it is slightly slower in this test; its payoff appears when reduced bytes avoid cache pressure/eviction. On 64-GB M1, that saved state memory could instead buy higher weight precision, larger context safety margin, or more resident expert/state capacity. Apple quality and unpack cost still require direct measurement.

### NEW / unresolved — oMLX #3917 reports a large Qwen3.8-27B context-capacity regression on M4 Max 64 GB after runtime/OS/quant changes

Source: https://github.com/jundot/omlx/issues/3917  
Created **2026-09-25 07:24:53 UTC**.

Reporter compares:
- older oMLX 0.6.4 / macOS 26.6 / Q4e: benchmark progresses to ~163,840 processed tokens before memory guard rejects the 262K target;
- oMLX 0.7.0rc1 / macOS 27 / Q6e: failure occurs around ~98,304 processed tokens, with observed attempts commonly ~70-90K.

The fresh log shows a prefill safety rejection when:
- current footprint ~39.81 GB;
- predicted KV+SDPA transient ~9.92 GB;
- required ~49.73 GB;
- Metal ceiling ~49.25 GB.

This is **confounded** by OS version, runtime version and a larger Q6 quant, and no root cause exists at cutoff.

**Classification:** NEW unresolved Apple memory-capacity report.

**P51 consequence:** no planning change. Context-capacity certification must use the exact final quant/runtime/macOS combination and distinguish **steady resident bytes from prefill transients and memory-guard policy**. A model that nominally fits 128K can still fail admission because of transient PP workspace.

### KNOWN / UPDATE — vLLM #58439 file-backed PLE remains compatible with the new persistent-prefetch-id fix

Fresh GB10 rebase validation after #58489:
- PLE suites: **76 passed**;
- checkpoint-mapped file-backed PLE and persistent prefetch-id storage coexist;
- no new performance numbers.

The substantive P51 conclusion is already durable: file-backed 47.7-GiB PLE is viable only with explicit page prefetch; cold GPU page faults alone can make a ~30K prefill 88 s versus ~1.6 s with CPU prefaulting.

### PUBLIC / QUANT SURFACES

- **ISTA-DASLab/GSQ Flash-Next:** no new precisely timestamped Flash-Next source-vs-quant behavioral certification in this interval.
- **ByteShape:** no new Flash-Next release or behavioral receipt found; current public Qwen3.8 work remains dense 27B.
- **DASLab 27B phase-disaggregated quantization:** Hugging Face reports the Qwen3.8-27B NVFP4 prefiller updated within the last several hours. It streams a separate 12.8-GiB NVFP4 prefill stack layer-by-layer while keeping an aggressive low-bit decode model resident, claiming ~50% recovery of accuracy lost to very-low-bit decode at close to zero resident-memory cost. The associated GitHub repository had **no commits in this strict interval**, so this is recorded as background, not NEW code evidence.
- **LocalLLaMA:** no new precisely timestamped M1/dual-M1 Flash-Next receipt. The 12-GB RTX 5070 custom engine remains the same-day background result: 65.1 TG / 543 PP at 128K on its lowest-bit path, with quality still not source-certified.

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

**2026-09-25 07:46:32 UTC**
