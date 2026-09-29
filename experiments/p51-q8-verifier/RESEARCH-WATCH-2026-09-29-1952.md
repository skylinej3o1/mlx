# Project 51 primary-lane research watch — 2026-09-29 19:52 ET

**Freshness boundary entering this pass:** **2026-09-29 21:50:01 UTC**.  
**User cutoff:** **2026-09-29 23:52:05 UTC**.

## Decision

**Durable STATE + TARGETS update; no TG/PP-center change.**

The important change is confidence/implementation status for the maximum-context lane:

> **IQ3_XXS 3.00-bpw + native 262K + 16-GB NVIDIA GPU is now physically demonstrated in another Qwen3.8-Flash-Next runtime with compressed KV.**

The user's exact 5070 Ti + 64-GB host + Strata integration is still unproven. Therefore:
- conditional physical-fit prior for P51 IQ3_XXS + 262K rises **~75-80% -> ~85%**;
- K6/V4 quality prior stays **~60-70%**;
- no 262K TG/PP center is assigned yet.

## Strict-window NEW findings

### NEW — vLLM rejects impossible hybrid prefix-match granularity

Source commit:
`be255076d0498c163441d4aa3fc9d2da142f30fd`  
Timestamp: **2026-09-29 23:12:15 UTC**.

A configured `prefix_match_unit` is now rejected when even one participating KV cache group cannot honor it.

P51 rule:
- reusable-prefix granularity is part of state identity;
- every participating KV/recurrent/indexer group must represent the same reusable frontier;
- fail closed instead of constructing a cache configuration where one group silently cannot match the boundary.

### NEW — SGLang tunes GDN recurrent target-verify only behind bit-exact state/output tests

Source:
`37a47737c805782028e2c7cdbcc99f8770c0774c`  
Timestamp: **22:03:33 UTC**.

For SM90 and target verification only:
- N <= 64;
- K=V=128;
- non-KDA GDN;
- launcher moves from BV=32 to **BV=4 / one warp**.

Tests cover:
- N 1/3/16/64;
- T 4/16;
- multiple head/hidden layouts;
- tree and non-tree verification;
- exact equality of output and intermediate recurrent-state buffer against BV=32.

P51 interpretation:
- verifier-specific launch tuning may differ from serial decode;
- but it earns promotion only when **both output and rollback/intermediate state are bit-identical**;
- mechanism evidence only for P69, not a 5070/M1 speed transfer.

### NEW — SGLang adds DSpark speculative/prefill coordination

Source:
`d3f8a8f4f57f0b058aa0e4eb0cff6b7da7c0b1ce`  
Timestamp: **23:08:01 UTC**.

DSpark now participates in DP speculative/prefill coordination:
- heterogeneous ranks can pair local prefill with peer verification;
- draft and target views of global token counts are explicitly switched;
- static ragged verify is required for the relevant DP mode.

P51 takeaway:
- prefill/decode/speculation coordination needs an explicit phase/layout plan;
- never reuse token-count or layout metadata across draft/target phases merely because physical buffers are shared.

### NEW — SGLang memory-saver SWA KV allocation cleanup

Source:
`f0e4001930f86cf4b418411ba7dd20e917ce6f90`  
Timestamp: **23:29:02 UTC**.

SWA KV pools now allocate inside the runtime's memory-saver region.

P51 interpretation:
- auxiliary KV pools must be owned by the same admission/reclaim domain as the main cache;
- otherwise resident-capacity accounting can understate physical memory.

No target-number movement.

### NEW — vLLM sparse-indexer workspace is sized after compression geometry is known

Source:
`c37f86e5721f089a27c8e4358c30e435805fcaab`  
Timestamp: **22:36:39 UTC**.

GLM sparse-MLA/indexer initialization now computes compression ratio before sizing the prefill workspace, rather than allocating a larger uncompressed-shaped buffer first.

P51 relevance:
- compressed cache/state formats only earn memory credit if temporary/indexer workspaces are also sized from the compressed geometry;
- a full-size scratch allocation can erase the resident-memory win.

Cross-architecture only.

### NEW — Strata independent AMD backend receipt

Issue #178 created **23:38:09 UTC**.

Hardware:
- Radeon AI PRO R9700 32 GB;
- ROCm 7.14;
- Ubuntu 24.04;
- Qwen3.8-Flash-Next Coder IQ1_M;
- 128K configured context.

Reported:
- ~31.9 GB VRAM;
- ~27 GB host mapped;
- **62.7 PP**;
- **44.7 TG**;
- MTP 12/14 accepted.

Useful independent evidence that Strata is a real portable engine rather than a single CUDA benchmark stack. No P51 NVIDIA target change.

### NEW/UPDATE — Strata snapshot-core convergence progresses

Issue #57 was updated inside the strict window.

Current shared-core development status:
- RAM and optional NVMe use one snapshot/restore core;
- bounded staging;
- compatibility/integrity checks;
- atomic disk writes and quotas;
- host tests pass serialization, corruption, restart, eviction and memory admission.

Still pending:
- linked full engine/model validation;
- K8V4 snapshot coverage;
- batched-draft-KV coverage;
- disk restart/restore parity;
- HIP/multi-GPU coverage.

A Windows contributor also retested a local auxiliary snapshot patch against **0.1.27** on RTX 4070 Laptop / 64 GB / low-RAM Swift IQ3_XXS:
- official binary after unrelated calls: zero prefix reuse, **10.7-11.9 s** return;
- local snapshot patch: reused **3,216 / 3,223 tokens**, **0.8-1.4 s**;
- correct answer in both cases.

This is only a 3.2K fixture; it is architecture evidence, not long-context capacity evidence.

### NEW/UPDATE — TensorFold 0.4.0 still overstates Flash SSD-expert window on real 64 GB Mac

Issue #95 updated inside the strict window.

M5 Pro 64 GB / Flash-Next / `--ple-on-ssd --ssd-experts 24`:

Fixed:
- a ~34,434-token prompt is retained;
- next turn resumed with 34,427 cached;
- **2.18 s TTFT vs 195.4 s cold**.

Still broken:
- startup advertises **65,536** tokens;
- a 65,378-token prompt is refused;
- fresh-server admission says it fits only **51,392** prompt tokens;
- after retaining a 1.10-GiB checkpoint, effective fit fell further.

P51 rule:
- startup/context fit, live request admission and checkpoint retention must use the **same physical-memory accounting**;
- an advertised window is not a resident/resumable capacity receipt until an in-window request is both admitted and retained.

## RECOVERED CURRENT — Strata 0.1.27

Release commit:
`a79080535d1b2a71a3419a0d97d8e7dca194b0f1`  
Timestamp: **2026-09-29 20:58:59 UTC**, before this pass boundary.

Classify **RECOVERED CURRENT**, not NEW.

Important P51 item:
- the CJK-expanded MTP draft subset is now officially shipped;
- setup replaces recognized older vocab files and reports that Chinese/Japanese/Korean are included.

This converts our earlier issue-#137 workaround into current production behavior.

The verifier-width native-expert arithmetic issue #152 is **not** fixed in this release. The maintainer's current recommendation remains:
`STRATA_NO_IQ512=1 STRATA_NO_IQ256=1 STRATA_NO_IQ4NL=1`
for width-invariant certification.

## RECOVERED OLDER — Qwen3.8-Flash-Next TurboQuant/TBQ KV is already physically implemented

This is the most important audit correction of the pass.

### A. starsder/qwen3.8-flash-next-inference-research

Hardware/model:
- RTX **A5000 16 GB**;
- Ryzen 5950X;
- 128 GB host RAM;
- Qwen3.8-Flash-Next **UD-IQ3_XXS**;
- `-c 262144`.

Architecture:
- 48 blocks;
- only **12 full-attention layers** have K/V;
- 2 KV heads;
- head_dim 256.

Physical 256K KV sizes:

| Format | Approx bpw | 256K KV |
|---|---:|---:|
| f16 | 16 | **6.0 GiB** |
| q8_0 | 8.5 | **3.19 GiB** |
| q4_0 | 4.5 | **1.69 GiB** |
| TBQ4 | 4.06 | **1.52 GiB** |
| TBQ3 | 3.06 | **1.15 GiB** |

Historical 256K matrix:
- q8_0: 29 MoE slots;
- q4_0: 45;
- TBQ4: 47;
- **TBQ3: 51**;
- TBQ3 peak GPU memory ~**14,496 MiB**.

This is direct evidence that **16-GB VRAM can carry IQ3-class Flash at native 262K when KV is aggressively compressed**.

Host was 128 GB, so it does not establish the 64-GB host result.

Quality matrix on the repository's short controlled PPL/KLD fixture:

| KV | PPL(8ch) | Mean KLD |
|---|---:|---:|
| f16 | 2.0120 | baseline |
| q8_0 | 2.0128 | 0.03085 |
| q4_0 | 2.0234 | 0.05689 |
| **TBQ3** | **2.0728** | **0.11640** |

TBQ3 is a real capacity option, but it is not quality-neutral in this test.

TBQ4's tested Flash-attention path was broken/unusable in that branch (single-chunk PPL ~63.7), so its capacity number is not a valid quality receipt.

### B. thadreber-web/llama.cpp-qwen38-flash-next

A separate Qwen3.8-Flash-Next llama.cpp fork independently ports TurboQuant KV.

Matched n=10 decode:
- q8_0 K/V: median **40.024 TG**;
- Turbo3 K/V: **40.574 TG**;
- difference statistically indistinguishable in that experiment.

Memory:
- q8_0: 61,414 MiB;
- Turbo3: 61,073 MiB;
- saving **341 MiB** in that 131K-class configuration.

Later same-binary quality work records approximately **+2.56% PPL vs q8_0**.

Implementation lessons:
- TurboQuant KV must not be double-rotated;
- qwen4exp recurrent-state rollback must remain exact for MTP;
- compression can be useful purely for memory even when it does not improve TG.

### P51 consequence

The missing work is **not inventing Flash compressed KV**.

The missing work is:
- porting/adapting the proven geometry/rotation/cache handling to Strata;
- adding a quality-safer **K6/V4** representation;
- retaining compressed host state under Strata KV streaming;
- preserving QSA/indexer/GDN/MTP state exactly;
- qualifying it on the exact 5070 Ti / 64-GB Windows box.

Physical-fit prior:
- previous: **~75-80%**;
- new: **~85% conditional on a correct Strata integration**.

K6/V4 quality prior remains **~60-70%** because no direct Flash K6/V4 long-context quality result exists.

## Strict-window negative scan

From **2026-09-29 21:50:01 -> 23:52:05 UTC**:

- **Strata engine repo:** no new engine commit in-window; 0.1.27 is RECOVERED CURRENT from before the boundary.
- **TensorFold:** no new commit, only issue follow-up evidence.
- **oMLX:** no strict-window commit.
- **mlx-serve:** no strict-window commit.
- **TurboQuant-MLX:** no strict-window commit.
- **OnlyTerp / 0xSero / varjoranta TurboQuant:** no strict-window commit.
- **Ishizuki:** no commit.
- **MoEspresso:** no new public M1-Max ~27-TG fork/settings/context receipt.
- **Exact user's 5070 Ti:** still no IQ3_XXS 262K physical Strata run.
- **DASLab:** no new official source-paired Flash IQ3_S/IQ3_XXS 262K semantic-quality result.
- **Dual-M1:** no new sustained filled-128K physical receipt.

## Canonical planning state after this pass

Numerical speed targets unchanged:
- dual-M1 Flash: **40 TG @ genuine ~128K / 400 PP / ~70% >=40 TG**;
- single-M1 dense27B: **25 TG / ~110 PP**;
- Strata IQ3_XXS @128K: **78 TG / ~85%**;
- IQ3_XXS PP: **1,650 / 1,550 / 1,500** at 32K / 64K / 128K;
- IQ3_S PP: **1,550 / 1,550 / 1,350**.

Maximum-context lane:
- **IQ3_XXS 3.00 bpw + genuine 262K + Flash-aware compressed KV**;
- conditional physical-fit prior: **~85%**;
- K6/V4 long-horizon quality prior: **~60-70%**;
- no 262K TG/PP center until exact-card physical measurement.

## New hard boundary

**2026-09-29 23:52:05 UTC**
