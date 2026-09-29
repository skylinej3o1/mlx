# Project 51 primary-lane research watch — 2026-09-29 15:09 ET

**Freshness boundary entering this pass:** **2026-09-29 15:03:35 UTC**.  
**User cutoff:** **2026-09-29 19:09:40 UTC**.

## Decision

**Durable STATE + TARGETS update; no numeric TG/PP/AA-center change.**

This pass changes the production plan in three ways:
1. TensorFold 0.4.0 demonstrates that **pre-M5 Apple can actually serve row-exact per-module mixed 2-8-bit Flash checkpoints**, materially reducing implementation risk for the P51 protected-island quant design.
2. Strata's new **K8V4** mode becomes the preferred long-context capacity experiment before whole-cache Q4; INT8 remains the quality baseline.
3. The multilingual MTP fix is refined from "use the full head" to **domain-aware compact draft-vocabulary expansion first, full-head fail-open second**.

Canonical physical targets remain:
- dual-M1 Flash-Next: **40 TG sustained @ genuine ~128K / 400 cold PP / ~70% >=40 TG**;
- single-M1 dense27B: **25 TG / ~110 PP**;
- Strata IQ3_XXS ~128K: **78 TG / ~85%**;
- Strata PP ladders unchanged;
- AA priors unchanged.

## Strict-window findings

### NEW — TensorFold 0.4.0: pre-M5 mixed-bit execution is real

Source:
https://github.com/ashhart/TensorFold/commit/7a00336b2f6d1a1a3e0ba49d1ef5b4b82e927759  
Timestamp: **2026-09-29 17:03:00 UTC**.

TensorFold 0.4.0 adds on M1-M4:
- Flash-Next MLX affine **2/3/4/5/6/8-bit** support;
- per-module mixed checkpoint support;
- row-exact 5/6/8-bit kernels on the matrix units;
- existing 4-bit group-32 kernels retained for those modules;
- each module executes in its checkpoint's own format.

This is directly relevant to P51's proposed ~3.3-3.6 average-bpw artifact with protected high-precision islands.

Dense Qwen3.8-27B / M3 Ultra supporting measurements:
- oQ4e 8-row verify: **40.8 -> 31.9 ms**;
- new oQ-width kernels are reportedly within **1-5% of 4-bit** at every tested width;
- DFlash2 sampled code: **+14%**;
- chat: **+5-7%**;
- greedy code: level.

The runtime's drafted replies remain equal to its own serial reference. The 5/6-bit arithmetic path changes from older TensorFold releases, so cross-release token identity is not claimed.

P51 interpretation:
- a mixed-bit P51 artifact no longer requires assuming that protected 5/6/8-bit islands must fall onto a catastrophically slow generic Metal path;
- still cross-chip evidence: no transfer of M3-Ultra percentages to M1 Max;
- no 40-TG probability move without an exact M1/dual-M1 physical run.

### NEW — TensorFold 0.4.0 Flash-specific M1-M4 work

Same release.

Reported on M3 Ultra:
- Flash-Next drafted and serial execution **2-7% faster**;
- attention gate folded into merge;
- PLE + router fusion;
- chained drafts queued as built;
- multi-row 4-bit dots remove an integer-to-float conversion while preserving result bits.

Useful Apple7 mining evidence only.

### NEW — TensorFold stream admission becomes incremental

On a 64-GB Mac, dense 27B now serves **16 streams at 32K contexts**, compared with 4-9 in 0.3.x.

Mechanism:
- a stream reserves memory as it grows rather than its entire maximum reply;
- shared-round workspace is charged to the streams actually sharing it;
- when memory gets tight, retained prompts are evicted first, newest streams wait next, then a request fails explicitly.

P51 rule strengthened:
- multi-agent resident capacity should be priced from **current/incremental state + shared workspace**, not N × worst-case reply reservation;
- this is dense-27B capacity evidence, not Flash B2-B4 TG evidence.

### NEW — Strata 0.1.25 prompt fusions

Release:
https://github.com/Niko1221/Strata/commit/a4d791ea4467b3856dcf443fb4d6b88ebd0447a6  
Timestamp: **2026-09-29 17:12:10 UTC**.

Relevant exact prompt changes:

F-1:
https://github.com/Niko1221/Strata/commit/882bb6de757c492718d7f86b1b0a1e64536782d9
- removes an FP32 copy of hyper-connection normalized rows;
- next mixing kernel recomputes the required values in the same arithmetic order;
- reported **+1.1% @32K / +1.7% @128K**.

F-2:
https://github.com/Niko1221/Strata/commit/b04684515f6b886e11bd8dbb50a70dd584675e2a
- fuses a half's hyper-connection write with the next half's normalization;
- bit-identical;
- F-1 + F-2 together: **+4.0% @32K / +3.3% @128K** on the tested prompt path.

P51 interpretation:
- real common-path PP headroom;
- do not move IQ3 PP targets until a same-quant 0.1.25 matrix is published.

### NEW — Strata K8V4 hybrid KV

Source:
https://github.com/Niko1221/Strata/commit/2aa8f72c96431a8ea608ee7ed801d746d4ca498f  
Timestamp: **2026-09-29 16:09:42 UTC**.

Design:
- **K = INT8**, unrotated;
- **V = Hadamard-rotated Q4_0**;
- attention scores retain the INT8 K path;
- footprint **816 B/cell vs 1,056 B/cell for INT8**, ~23% less.

Measured RTX 3090 / Coder IQ1_M:
- around 118.75K: decode **82-97 TG** versus INT8 **75 TG** (acceptance varies);
- prefill around **1,130-1,170 PP**, essentially unchanged there;
- 26-needle seed identical to INT8;
- KV at 131K: **1.39 GB vs 1.80 GB** INT8;
- at max-context 204,800: **1,024 PP**, **82-91 TG**, 25/26 needles at ~197.9K.

Strata docs summarize at ~198K:
- output **99 TG vs 85 TG INT8**;
- same needle result;
- prompts **2-5% slower**.

Limitations:
- no KV streaming support under K8V4;
- no source-paired semantic/agent/AA certification;
- decode uplift may be from freed VRAM/expert residency rather than cheaper attention itself.

P51 target-plan consequence:
- **INT8 K/V stays the quality baseline**;
- **K8V4 becomes the preferred capacity/speed experiment**;
- whole-cache Q4 becomes the more aggressive lower-precision arm.

### NEW — MLX-Serve multi-slot QSA launch

Source:
https://github.com/ddalcu/mlx-serve/commit/442668946bfd26708312859bfdcc4932f6f9558b  
Timestamp: **2026-09-29 18:28:10 UTC**.

One sparse-QSA split + merge launch now serves **2-4 quantized S=1 decode slots**:
- one slot per grid-z lane;
- each slot retains its own KV length/capacity and block list;
- output is bit-identical to separate per-slot launches.

This is directly relevant to the P51 B2-B4 Apple aggregate lane.

No end-to-end 2/4-stream throughput result accompanies the commit, so:
- promote the mechanism;
- **do not move the B2-B4 aggregate confidence ladder** yet.

### NEW — MLX-Serve QSA and MoE Flash prefill mining

QSA:
https://github.com/ddalcu/mlx-serve/commit/bfe518f77e4db2872c5f0987157cdf158ad62367  
Timestamp: **17:40:14 UTC**.

M5 Ultra / mid48:
- occupancy-tuned tensor-unit QSA;
- first sparse chunk uses gathered attention immediately;
- per-stage examples:
  - first chunk **634 -> 120 ms**;
  - 16K **503 -> 193 ms**;
  - 32K **544 -> 158 ms**;
  - 64K **574 -> 165 ms**;
- commit reports **+22.6% Flash-Next prefill**.

MoE:
https://github.com/ddalcu/mlx-serve/commit/9a5c98126fb8054a630bea93fd789e7bbe3cf22d  
Timestamp: **18:11:37 UTC**.

Ports oMLX's segmented sorted gather, removes repeated hidden-row expansion and fuses gate/up + SwiGLU. Commit reports **+10.5% Flash-Next prefill**, with first-use canary/fallback and bit-identical supported shapes.

P51 interpretation:
- strong sources for the 400-PP Apple mining plan;
- M5 Ultra numbers do not transfer numerically to M1.

### NEW — allocator cache is part of residency accounting

Source:
https://github.com/ddalcu/mlx-serve/commit/f5acdade2cdf42424eb4af03e43f750c810c4bb2  
Timestamp: **18:16:43 UTC**.

A make-room eviction freed a model into MLX's allocator cache but did not return the pages to the OS before the next model's physical-memory preflight. The new path clears the allocator cache first.

P51 rule:
- "evicted" / registry-free state is not the same as physically available memory;
- resident-agent admission should track runtime allocator cache and OS physical/reclaimable memory separately.

### NEW — llama.cpp stops speculative acceptance at EOG

Source:
https://github.com/ggml-org/llama.cpp/commit/d280808f5d82fcc3142b53f94ea5f594250cd765  
Timestamp: **16:25:41 UTC**.

Draft acceptance now stops at EOG instead of accepting speculative tokens beyond the serial stop boundary.

P51 rule:
- EOG/stop behavior is part of exact speculative semantics;
- no accepted proposal may advance beyond the target sampler's terminal frontier.

## UPDATE / SAME-DAY CURRENT — domain-aware compact MTP vocabulary

Strata issue #137 now contains a second Windows RTX 5070 Ti reproduction.

The expanded subset:
- shipped: **40,525 ids**, 52.6 MiB;
- CJK-expanded: **106,285 ids**, 137.9 MiB;
- full head: 322.1 MiB.

Expert-cache slots:
- shipped: **5,627**;
- CJK-expanded: **5,627**;
- full head: **5,551**.

Real English-novel -> Chinese translation:
- shipped: **68.1 TG**, 34-36% acceptance, 108.9 s;
- expanded: **99.0 TG**, 70-77%, 78.5 s;
- full head: **96.4 TG**, 70-77%, 80.2 s.

The compact expanded head is therefore the best measured trade on this box.

P51 production order:
1. audit candidate coverage against expected **output** domains;
2. expand the compact subset for missing token classes;
3. retain full-head/fail-open as a fallback;
4. only then tune S.

## UPDATE / SAME-DAY CURRENT — Strata NVMe delta cache

PR #52 has moved from whole-file rewrite to an incremental/delta KV format on the #57 shared core.

Improvement:
- a continuing turn appends new KV chunks instead of rewriting a ~2-GB image;
- one cited 6,872-token continuation appended ~26 chunks.

Remaining gaps:
- ~**113 MB mutable State** still written synchronously every turn;
- restore stages the complete assembled image in RAM, ~**2.3 GB for 142K** in the cited run;
- write policy is still every DONE, not RAM-eviction-driven;
- the new delta manifest binds weights fingerprint + KV quant;
- the old long-session v3 fallback remains **weight-blind / geometry-only**.

P51 rule:
- no legacy/fallback state representation may weaken identity validation;
- same-geometry/different-weights state must hard-miss;
- delta/NVMe promotion is not qualified until fallback identity, bounded/streaming staging and durability are closed.

## SAME-DAY CURRENT — Splash dense-27B quality warning

A current community discussion around very high Splash 27B Mac throughput includes a user reporting that their Splash-tuned and Swift+Splash variants miss debugging/code issues found by base Qwen3.8-27B.

This is anecdotal and pack-specific, not a formal quality result.

P51 interpretation:
- reinforces existing policy: a speed-tuned dense-27B artifact is not promoted from TG alone;
- use base-vs-candidate agent/code tasks and artifact-producing evals.

## Strict-window negative scan

From **2026-09-29 15:03:35 -> 19:09:40 UTC**:

- **Exact M1 Max Flash-Next:** the ~27-TG comment still has no public fork/settings/context denominator. Current search still resolves to the published MoEspresso 12-15-TG M1-Max result and the separate M5-Pro ~27.6-TG fork.
- **Exact dual M1 Max / TB4:** no new sustained genuine-128K receipt.
- **DASLab Flash IQ3_S:** SWE-bench 82.0 vs 82.8 remains the newest official long-horizon result; no new source-paired 32K/64K/128K/262K semantic-quality result found.
- **oMLX:** no strict-window commit after the earlier verifier fixes.
- **Ishizuki:** no commit.
- **MoEspresso:** no strict-window commit.
- **Strata IQ3 0.1.25 matrix:** no same-quant 32K/64K/128K replacement for the 0.1.22 matrix yet.
- **User's exact 5070 Ti Windows host:** no new frozen full ladder/8h+ soak receipt in-window.

## Durable target-plan changes

No numeric center/probability change.

### Apple mixed-bit feasibility

TensorFold 0.4.0 is now explicit supporting evidence that:
- per-module mixed 2-8-bit Flash checkpoints can load on pre-M5 Metal;
- 5/6/8-bit protected tensors need not automatically fall onto a much slower generic path;
- row-exact verification can coexist with those widths.

Still require exact M1/P69 qualification before counting performance.

### KV capacity arm

Order is now:
1. **INT8 K/V** — quality baseline.
2. **K8V4** — preferred capacity/speed candidate.
3. whole-cache Q4 — aggressive low-precision capacity arm.

K8V4 needs long-horizon semantic/agent certification before production promotion.

### Draft candidate-space strategy

Order is now:
1. compact subset audited on output-domain coverage;
2. domain-aware compact expansion;
3. full-head/fail-open fallback;
4. verifier-width tuning.

## Canonical planning state after this pass

Unchanged numerically:
- dual-M1 Flash-Next: **40 TG @ genuine ~128K / 400 cold PP / ~70% >=40 TG**;
- single-M1 dense27B: **25 TG / ~110 PP**;
- Strata IQ3_XXS ~128K: **78 TG / ~85% confidence**;
- Strata IQ3_XXS PP: **1,500 / 1,400 / 1,300**;
- Strata IQ3_S PP: **1,450 / 1,250 / 1,200**;
- IQ3_XXS AA>=38: **~85%**;
- IQ3_XXS AA>=40: **~65%**;
- IQ3_S AA>=40: **~80%**;
- B2-B4 aggregate ladder unchanged pending an end-to-end receipt.

## New hard boundary

**2026-09-29 19:09:40 UTC**
