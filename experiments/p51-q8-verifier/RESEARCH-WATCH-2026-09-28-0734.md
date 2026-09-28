# Project 51 primary-lane research watch — 2026-09-28 07:34 ET

**Freshness boundary entering this pass:** **2026-09-28 10:51:31 UTC**.  
**User cutoff:** **2026-09-28 11:34:46 UTC**.

Strict boundary preserved. Older exact-rig evidence recovered during this pass is labeled **RECOVERED CURRENT** rather than NEW.

## Decision

**Canonical dual-M1 targets unchanged. RTX 5070 Ti dense-27B targets are recalibrated.**

Keep dual-M1 Flash-Next at **40 TG @ genuinely filled ~128K / 400 cold PP / ~70% >=40 confidence**.

For the RTX 5070 Ti dense Qwen3.8-27B lane, the old blanket **120 TG / 250 PP** row is no longer an adequate target identity. The direct CUDA-v2 receipt recovered below makes context a required part of that lane's target:
- short/<=8K: **120 TG working target**
- ~16K: **110 TG**
- ~64K: **95 TG**
- ~128K: **90 TG**
- cold PP: **~1,900 PP @ 24–32K**, **~1,500 PP @ ~128K**

---

## RECOVERED CURRENT — exact RTX 5070 Ti CUDA-v2 receipt was missed in prior passes and forces a PP true-up

Source: feveromo/recipes-qwen3.8-27b-5070ti, commit f24951565fc1196ba7d1f137cee560dcd8f822c2, committed **2026-09-27 20:16:20 UTC**. It predates this hard window and is therefore RECOVERED CURRENT.

Exact hardware/config:
- **RTX 5070 Ti 16 GB / GB203 / sm_120**
- Ryzen 7 9800X3D / 32 GB DDR5-6000
- llama.cpp build 11191 plus pinned custom CUDA-v2 patch
- Huihui Qwen3.8-27B abliterated **GSQ-RCO IQ3_S + embedded MTP**
- target + draft KV **Q4_0**
- MTP max 3
- reasoning **xhigh**, normal production sampler also tested
- context **131,072**
- one stream, fully GPU-resident target

Measured long-context ladder:
- short: **130.0–131.6 TG** greedy; **129.5 TG** sampled
- 15,694 prompt: **104.7 TG / 2,030 PP** greedy; **111.7 TG sampled**
- 62,494 prompt: **98.0 TG / 1,814 PP** greedy; **96.0 TG sampled**
- 92,914 prompt: **94.8 TG / 1,696 PP**
- 128,794 prompt: **91.3 TG / 1,576 PP**, 81.7 s prefill

At 128K the server loaded at 14,804 MiB and peaked at 14,926 MiB; whole-card peak with a light desktop was 15,074 MiB. Four planted values across a 119,457-token prompt were recalled exactly; an append-only follow-up reused 119,645 cached tokens.

### Why v2 is faster

The patch is highly specific, but its mechanisms overlap several P51 themes:
- 2–4-column quantized matvec decodes each weight block once and reuses it across verify columns;
- fused reduced-vocabulary MTP head (**16,384 ranked rows + context rows**) eliminates repeated 248K-row draft lm-head scans;
- fused MTP catch-up collapses several draft graphs into one;
- Gumbel-coupled sampling preserves the target distribution while increasing draft/target agreement;
- Q4_0 attention gets a specialized MMA path for small query width;
- prompt attention uses INT8 QK MMA for large batches;
- norm/residual/GDN/conv glue is fused;
- GDN prompt kernels are reported ~3.5x faster locally;
- launches per short decode cycle fall roughly **2,420 -> 1,090**.

Target-v1 numerical checks are unusually good for a custom path: v2 verify/prefill KLD versus v1 is below v1's own ubatch-size noise, and coupled-sampling tests validate the target distribution. This still does **not** certify the abliterated IQ3_S checkpoint to Project-51 AA~40 quality.

### Target effect

The old exact-rig PP anchors in TARGETS were 191–219 PP. Those were not a production ceiling; they were a stale runtime path. Keeping a 250-PP mature target after direct **1.6K–2.0K PP** production-style receipts would violate the project's target-change rules.

TARGETS is therefore updated this pass to a **context-aware 5070-Ti ladder**, while preserving the old anchors as historical pre-v2 baseline.

---

## NEW — Strata 0.1.14 speed matrix confirms >900 PP at 128K even on the weaker RTX 5070 12 GB

Commit 24c3551848cd426173b5686ba3c40af87a59c4ed at **2026-09-28 11:07:35 UTC**.

Hardware: RTX 5070 12 GB / Ryzen 5 7600 / 64 GB DDR5, engine 0.1.14, 256 generated tokens, MTP/spec4, 8-bit KV above 4K and KV streaming from 64K.

At **128K prompt depth**:
- Q2_0: **1,208 PP / 67.2 TG**
- IQ2_XS: **1,071 PP / 59.8 TG**
- IQ3_XXS: **1,015 PP / 45.8 TG**
- IQ3_S: **931 PP / 40.5 TG**

At 32K the same rows are about **1,070–1,308 PP**.

Decode comparisons across old/new prompt paths are not clean speed A/Bs because prompt-path rounding can change text and speculative acceptance. A same-machine 4K back-to-back reports 0.1.14 at 88.5 TG versus 0.1.12 at 85.7 TG for Q2_0, so the engine itself is not showing a large decode regression.

### P51 consequence

For the planned 5070-Ti prefill -> M1 decode experiment, CUDA prefill compute is now very unlikely to be the 400-PP bottleneck. The hard problems are **canonical state export, transfer, visibility, recurrent/QSA identity and TB4 overlap**, not raw CUDA prompt throughput.

---

## RECOVERED CURRENT + NEW — Strata eagerly loads CUDA kernels before VRAM is consumed; 0.1.15 code lands

Mechanism commit 660996051e965dd8db71df188cdf6de021b6bbf2 at **10:49:25 UTC** was missed by the previous pass and is RECOVERED CURRENT.

IQ3_XXS at 64K/128K could fail mid-prompt with `out of memory: cudaFuncSetAttribute`: CUDA lazily loaded an MMQ kernel only after the expert cache and prompt buffers had consumed nearly all VRAM.

Fix:
- set `CUDA_MODULE_LOADING=EAGER` before the CUDA context is created unless the user already set it;
- load kernel code before expert-cache sizing;
- cost ~**30 MB VRAM**, about ~20–23 fewer resident experts on the measured 12-GB card.

Engine-version commit de1916658200b9bca8fdb24d4ce6352017593bc0 landed **11:17:58 UTC** and makes setup require 0.1.15.

Strict-boundary note: the GitHub **v0.1.15 release was published at 11:34:55 UTC, nine seconds after this pass's cutoff**, so the release publication itself is excluded. The code commits are in-window.

### P51 rule

Lazy code/module residency is part of VRAM admission. Preload or reserve kernel/module memory **before** filling an expert/KV cache to the last few MiB.

---

## UPDATE — Strata sampler parity bug: non-greedy penalties are applied twice

Issue #53 was opened 20 seconds before the prior cutoff but edited after it; it is fully in-scope now. Current Strata source at the 0.1.15 code point still shows the reported behavior.

In the sampled path:
1. candidate selection stores `apply_penalties(logit, history_count, p)` into `sel_logit`;
2. after top-k/min-p/top-p, `scaled(i)` applies `apply_penalties(sel_logit[i] * inv_t, ...)` **again**.

So repetition/frequency/presence penalties are double-applied for non-greedy sampling when history and non-neutral penalties are active. The greedy path applies them once.

The project's own host parity fixture reproduces the same two-pass semantics, so **implementation-vs-self-reference parity is insufficient**.

Minimal reported example with presence penalty 1.5 and T=0.7 changes a repeated token's probability from about **10.5% single-pass -> 2.55% two-pass**.

### P51 consequence

Add an independently derived **sampler semantics oracle** to AA/runtime certification:
- repetition/frequency/presence penalties
- temperature ordering
- top-k/top-p/min-p ordering
- greedy vs sampled
- target-only vs speculative
- compare against the chosen canonical sampler, not a host port of the same implementation.

This bug does **not** affect our neutral-penalty benchmark rows, and it does not by itself imply general model-quality degradation.

---

## NEW — vLLM Qwen4Exp HC down+SiLU fusion independently confirms a small-row crossover

PR #58957 merged at **2026-09-28 10:51:38 UTC**, only seven seconds after the prior hard boundary.

On GB300, fused BF16 hyper-connection down projection + SiLU wins for decode batches up to 48 tokens:
- M=1: **5.86 -> 4.16 us (1.41x)**
- M=16: **10.02 -> 5.66 us (1.77x)**
- M=48: **9.76 -> 6.94 us (1.41x)**
- M=64: **9.50 -> 11.14 us (0.85x)** — it loses.

Qwen3.8-Flash-Next TP4+MTP3 8K/1K E2E TPOT improves about **2–4% at concurrency 1–16**, nearly flat at c=64.

This is GB300 CUDA evidence, not Apple or 5070-Ti numeric credit.

### P51 consequence

It independently reinforces the dispatch rule already emerging from Apple: **fusions need a measured row/concurrency cutoff**. Do not assume a kernel that wins at S=2–8 should own prefill or wide batches.

---

## UPDATE — vLLM #52244 gives a precise write-side rule for hybrid GDN prefix-cache + MTP

Updated in this window.

Observed failure on Qwen3.5 hybrid GDN+attention with MTP: a replay can land **one hash unit before** the prompt tail, while the producer cached recurrent state only at the prompt's own tail boundary. Intersecting attention and GDN cache groups then collapses the usable hit to a previous page or zero.

Example before fix with 67-token hash unit / 1,072-token GDN page:
- 1,072-token prompt -> **0 cached tokens**
- 2,144 -> **0**
- 3,000 -> 1,072

The fix is write-side: make prefill stop at the position a replay can actually land on, publish recurrent state there, and avoid caching prompt-end states that no lookup can reach. Full attention publishes the deepest reachable tail as well.

### P51 consequence

This sharpens our boundary rule: **a state snapshot is useful only if the future lookup protocol can actually land on that exact position**. Export/cache planners should derive checkpoint positions from the consumer's replay/rewind rule, not just from producer chunk ends.

---

## UPDATE — vLLM host-file PLE gather makes the Flash-Next disk-backed working set concrete

PR #58815 updated in-window.

For Qwen3.8-Flash-Next's **47.7 GiB FP8 PLE**:
- measured access is about **17.6 rows/step**;
- roughly **1.6 MiB working set over 800 steps**;
- host-file gather deduplicates row ids, `POSIX_FADV_WILLNEED`s coalesced ranges, `preadv`s rows, and copies only the staged rows to device.

DGX Spark / local NVMe results:
- realistic c=1 staging is **0.38–0.39% of ITL**;
- c=16 staging is ~**7.3–7.6% of ITL**;
- cold 30K prompt TTFT **17.40 s vs 15.45 s warm**;
- 817/817 soak requests +177 long-prefix requests completed without error in the earlier mapped-view iteration;
- current path leaves no persistent worker mapping of the PLE files.

This is not discrete-5070-Ti evidence and not Apple numeric credit.

### P51 consequence

PLE capacity should be designed around the **active row working set**, not the 47.7-GiB logical table size. A bounded staged/file-backed PLE path remains very plausible if host gather is prefetched/deduplicated and does not accidentally force full residency.

---

## SAME-DAY CURRENT — independent 5070 Ti dense27B report corroborates the recovered v2 receipt, but original provenance is incomplete

A Sep-28 community benchmark aggregator reports the same class of patched RTX 5070 Ti / IQ3_S / Q4_0-KV path at **104.7 TG / 2,030 PP** around 15.7K and **91.3 TG / 1,576 PP** at a 128,794-token prompt. The numbers match the feveromo repository receipt above.

Because the aggregator does not expose a precise publication timestamp for that row and search did not independently recover a separate original source, classify it as **SAME-DAY CURRENT corroboration**, not a second strict-window receipt.

---

## Strict-window scan summary

From **10:51:31 -> 11:34:46 UTC**:
- **Strata:** new 0.1.14 speed matrix, 0.1.15 code/version commits, sampler-parity issue; promoted.
- **vLLM:** Qwen4Exp HC fusion merged; hybrid-GDN prefix-cache PR and host-file PLE PR updated; promoted as mechanism evidence.
- **oMLX:** #4047 fused MoE updated; useful but non-bit-exact/default-off, retained as watch item rather than canonical state change.
- **TensorFold:** no new merged M1/Flash performance commit in-window.
- **mlx-serve:** no new commit or qualifying issue update.
- **Ishizuki / MTPLX / Splash / upstream DFlash / llama.cpp:** no strict-window primary-lane commit.
- **DASLab / GSQ-RCO:** no new strict-window AA certification receipt.

---

## Project 51 actions promoted by this pass

1. **True-up the 5070-Ti target file**: retire 250 PP as a current mature target; use the context ladder in TARGETS.
2. **Port the CUDA-v2 mechanisms selectively** into the 5070-Ti research lane: multi-column qmv, reduced draft vocabulary, fused catch-up, small-query Q4 attention, prompt GDN kernels. Do not assume each transfers to Apple.
3. **5070-Ti -> M1 bridge priority rises**: raw CUDA prefill is now comfortably above the cluster's 400-PP objective; focus on canonical state handoff and overlap.
4. **Pre-reserve code/module VRAM** before expert/KV admission.
5. **Add independent sampler-semantics tests**; self-reference parity is not enough.
6. **Cache/export checkpoint positions derive from consumer landing positions**, including MTP/hash rewind.
7. **PLE staging budget from touched rows**, not full logical table.

---

## Canonical planning effect

**Dual-M1 Flash and single-M1 dense targets unchanged. RTX 5070-Ti dense targets changed.**

Dual-M1 Flash remains **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence**.

Single-M1 dense remains **25 TG / ~110 PP**.

RTX 5070 Ti dense27B now uses a context-aware ladder. The old 250-PP row is superseded by direct exact-card evidence around **1.6K–2.0K PP** across 16K–128K, while decode naturally falls from ~130 TG short to ~91 TG at 128K.

## New hard boundary

**2026-09-28 11:34:46 UTC**
