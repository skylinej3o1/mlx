# Project 51 primary-lane research watch — 2026-09-24 20:45 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 22:20:34 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-25 00:45:51 UTC**.

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

The strongest fresh conclusions are implementation rules:
1. **speculative rollback must be in-place and proportional to changed state, never a deep copy of the whole batch cache;**
2. **KV-group geometry can turn a one-layer drafter bucket into dozens of per-step metadata builders and erase speculative gains;**
3. **logit storage precision is a protected output-state choice: FP32 logits can recover near-tie top-1 fidelity at negligible decode cost;**
4. **expert offload should be modeled from measured route hit-rate curves and device bandwidth rather than residency percentage alone.**

## Findings

### NEW — oMLX #3909: whole-cache rollback can dominate batched MTP step time and explode the MLX pool

Source: https://github.com/jundot/omlx/pull/3909  
Created **2026-09-24 23:32:48 UTC**.

Text-only Qwen3.5/3.6/3.8 Lightning MTP lacked a per-row vector rollback path. Shared verify therefore fell back to `commit()`, which:
- deep-copied the **entire batch cache** once per distinct accepted length;
- extracted rows;
- merged rows back into the batch.

Because MLX keeps freed buffers pooled up to the configured cache limit, this was both a latency and memory-pressure problem.

Qwen3.8-27B oQ4, 64-GB M-series Mac, batch 2:
- active model memory stayed ~17 GB;
- MLX buffer pool grew **~300 MB/step on short answers** and **~1 GB/step around 2K tokens**;
- pool reached **30-40 GB** between clears;
- process memory hit the hard watermark and evaluation requests were aborted;
- batched step ~**110 ms**, while only ~**38 ms** was backbone compute.

The new vector rollback:
- rolls KV rows back in place;
- replays GDN rows from zero-copy pre-verify state in one masked chunk;
- periodically compacts shared left padding;
- keeps pending boundary emission safe.

After:
- pool max batch 2: **30-40 GB -> 3.6 GB**
- pressure events/aborts: **several/yes -> 0/0**
- 2-row batched step: **~110 -> ~62 ms**
- 4-row aggregate decode: **~90 TG** (single-stream MTP ~50)
- Qwen3.8-27B oQ6 batch 4 also ran clean: pool max **8.7 GB**, zero pressure events.

A second commit enables shared initial priming for text-only batches:
- batch 8 median step: **225 -> 192 ms**
- pool max: **~20 -> 12 GB**
- aggregate decode: **41 -> 49 TG**.

**Classification:** NEW exact-Qwen3.8 dense / Apple speculative-state evidence.

**P51 consequence:** verifier rollback must be **in-place, row-aware and bounded by changed state**. A logically correct rollback path can still destroy throughput and 64-GB viability if it deep-copies whole KV/recurrent caches. Add allocator-pool growth, bytes copied per rollback and padding-compaction cost to the M1 S=2-8 profiler.

### NEW — vLLM #58638: drafter KV grouping can erase speculative gains through metadata overhead

Source: https://github.com/vllm-project/vllm/issues/58638  
Created **2026-09-25 00:04:44 UTC**.

Hybrid target + speculative drafter layouts can create a tiny one-layer drafter KV bucket. Existing grouping picks the smallest bucket as group size, exploding the number of cache groups and therefore per-step block-table/metadata builds.

Qwen3.6-35B-A3B + DFlash example:
- target buckets: 30 GDN / 10 full-attn / 5 sliding / 1 drafter-full;
- main heuristic: group size 1 -> **46 groups**;
- one GDN metadata `build()` can cost ~900 us and is repeated per group.

Measured B300:
- main 46 groups: **460 TG c=1 / 4654 c=32**
- byte-aware group size, 17 groups: **733 / 6495**
- block-outermost packed layout, 5 groups: **746 / 7463**
- acceptance length **5.1-5.2** across the Qwen runs.

The memory trade is real:
- 46 groups: 7.42M KV capacity;
- 17 groups: 5.19M due to ~3.05 GiB/request worst-case full-attention padding;
- packed 5-group layout: 7.53M capacity with only 58 MiB padding, but backend support is limited.

**Classification:** NEW adjacent-Qwen hybrid-spec infrastructure evidence.

**P51 consequence:** target/draft state geometry is not just a capacity concern. **Group count itself can be a decode-time host/control cost.** P51 should avoid allowing a small draft-state class to force per-layer target grouping. Optimize group geometry against both bytes and metadata-build count, and include group count in cache/runtime identity.

No numeric transfer to Apple7.

### NEW — Splash #141: keep target and draft logits FP32 to preserve near-tie behavior at near-zero speed cost

Source: https://github.com/incoai/splash/pull/141  
Created **2026-09-24 22:45:43 UTC**.

Splash previously stored target and DFlash draft logits as BF16 even though projection accumulation was FP32. Around logits of 16-32, BF16 spacing is 0.125, so near ties can collapse.

Reference observation:
- llama.cpp compared with only its own logits rounded to BF16 agrees on top-1 with itself at only **99.06% for 27B** and **98.95% for 35B**.

The PR keeps the existing quantized weights / BF16 normalized input / FP32 accumulation, but stores the final vocabulary logits in FP32 and makes target sampling plus draft selection consume FP32.

Teacher-forced vs llama.cpp over 16,384 positions:
- 27B prefill M5: top-1 **98.91 -> 99.44%**, median KL **1.4e-4 -> 0.5e-4**
- 27B decode B1 M5: **98.79 -> 99.30%**
- 27B prefill M3: **98.75 -> 99.42%**
- 27B decode B1 M3: **98.82 -> 99.45%**
- 35B improves more modestly, e.g. M3 prefill **97.60 -> 98.14%**.

Perplexity is unchanged within ±0.003.

Cost:
- logits arena +**16 MB** for four lanes;
- most decode A/B cells are within noise;
- one 35B MLX B3-B4 case shows ~0.8-1.0% cost;
- greedy outputs and acceptance were identical in the speed tests.

**Classification:** NEW quality/precision-path evidence.

**P51 consequence:** protect **output precision**, not only output-head weights. P51 should retain FP32 accumulation and strongly prefer FP32 stored logits for target sampling and draft acceptance, particularly when the quant search is already pushing average BPW low. A few megabytes of logits state is a cheap quality hedge compared with raising large weight tensors.

### NEW — oMLX #3910/#3911: expert-offload residency should be modeled from route hit rate, not resident percentage

Sources:
- https://github.com/jundot/omlx/pull/3910
- https://github.com/jundot/omlx/issues/3911

#3910 exposes real expert-cache hit/miss counters. Example Qwen3.8-Flash-Next-4bit on M5 Max 128 GB at **50% expert residency**:
- 48 wrapped layers;
- **92,438 hits / 13,502 misses**
- hit rate **87.26%** after one cold request.

#3911 proposes a speed estimator:
- record routed expert IDs during decode;
- replay them through the same per-layer LRU policy at multiple residency fractions;
- combine misses/token with expert bytes and measured drive bandwidth;
- anchor with a measured compute floor.

Out-of-sample examples from the contributor's prior runtime:
- Qwen3-235B-A22B 4-bit, 45% experts: estimate **12.5 TG ±25%**, measured **11.7**
- Qwen3-30B-A3B 4-bit / M1 Pro 32 GB / 12-GB expert budget: estimate **14.7 (11.8-18.4)**, measured **14.5**
- same model / 20 GB: estimate **19.3**, measured **17.5**.

Contributor notes forthcoming fetch/compute overlap makes actual step cost closer to **max(compute, fetch)** than their current additive approximation.

**Classification:** NEW offload-modeling evidence.

**P51 consequence:** if the final 64-GB M1 Flash quant requires routed-expert spill, reason from **misses/token and overlappable fetch time**, not "X% of experts resident." High route locality can make 50% residency far better than a naive 50% bandwidth penalty. This remains a contingency/offload branch, not a planning credit for 40 TG.

### UPDATE — mlx-serve #523: hardware-calibrated history lookup retained; new comment is advisory only

Fresh maintainer/community discussion continues to recommend:
- resident n-gram/PLE where memory allows;
- GPU-side/fused PLE pre-verification work;
- concurrency testing.

No new controlled performance measurement beyond the already-recorded default-sampling lookup results.

**Classification:** UPDATE, no new numeric state.

### UPDATE — SGLang #40223: every MTP draft head's KV and recurrent state must be restored, with each pool's own indexing

Source: https://github.com/sgl-project/sglang/pull/40223  
Fresh activity through **2026-09-25 00:26 UTC**.

Inkling HiCache restore previously omitted separate MTP draft SWA/Mamba state or could restore later draft heads incompletely. Draft SWA buffers can also use **full-token IDs while target SWA uses separately allocated physical IDs**, so putting both through the target pool can copy the wrong rows.

The PR:
- discovers every separate draft KV, convolution and temporal state pool;
- preserves global MTP depth IDs;
- uses each pool's own indexing/ownership;
- schedules all draft state restoration before target completion;
- accounts for sidecar memory in fixed host budgets.

Validation:
- 64 GPU transfer cases;
- 4 end-to-end serving cases after device eviction;
- **768 host tokens restored, 0 device-cache tokens**;
- each produced **32 identical tokens with zero logprob difference** vs cold run.

No throughput claim.

**Classification:** UPDATE / cross-model warm-state correctness evidence.

**P51 consequence:** further strengthens the rule that target and each draft depth have **separate state ownership/indexing identities**. "Restore MTP state" is insufficiently specific; state must be restored per draft head/pool using that pool's geometry.

### LOWER PRIORITY — vLLM #58631/#58633: speculative host and padding overhead continues to be shaved

- #58631 removes **~3.5 us/step/rank** of pure host Torch dispatch from DFlash/DSpark paths; explicitly no E2E claim.
- #58633 parallelizes one DFlash graph-padding path from **39.84 -> 2.17 us** at a MI355X production shape, recovering up to ~34-36 us/step; still a kernel-level fraction of a multi-ms step.

These reinforce the speculative-control-plane thesis already made durable by SGLang #41166-#41175, but do not add a new planning conclusion.

## Quant / community search

- **ISTA-DASLab/GSQ:** no in-window GitHub issue/PR/commit activity.
- **ByteShape:** no new precisely timestamped Flash-Next source-vs-quant behavioral result in this strict interval.
- The same-day Strata / LocalLLaMA 12-GB RTX 5070 report is now mirrored with a calendar date and reports at 128K: Q2_0 **65.1 TG / 543 PP**, IQ2_XS **52.0 / 472**, IQ3_XXS **44.8 / 414**. The public sources still do not expose a publication time precise enough to prove it falls after the prior **22:20:34 UTC** boundary, so it is **not promoted as NEW in this watch**. It remains important background evidence that model-specific runtime design can radically outperform generic llama.cpp on the same low-bit Flash quant.
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

**2026-09-25 00:45:51 UTC**
