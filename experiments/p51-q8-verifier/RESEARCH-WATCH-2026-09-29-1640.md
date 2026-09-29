# Project 51 primary-lane research watch — 2026-09-29 16:40 ET

**Freshness boundary entering this pass:** **2026-09-29 19:09:40 UTC**.  
**User cutoff:** **2026-09-29 20:40:47 UTC**.

## Decision

**Durable STATE + TARGETS update.**

The full Strata 0.1.26 prompt matrix justifies another conservative cold-PP true-up:

| Quant | 32K PP | 64K PP | 128K PP |
|---|---:|---:|---:|
| IQ3_XXS measured on RTX 5070 12 GB | **1,745** | **1,609** | **1,602** |
| **P51 5070-Ti target** | **1,650** | **1,550** | **1,500** |
| IQ3_S measured on RTX 5070 12 GB | **1,624** | **1,640** | **1,443** |
| **P51 5070-Ti target** | **1,550** | **1,550** | **1,350** |

No TG center or AA prior changes.

A new mandatory correctness gate is also added:
- **native CPU expert arithmetic must be width-invariant before plain-vs-MTP/source-equivalence certification.**

## Strict-window findings

### NEW — Strata publishes the full 0.1.26 speed matrix

Source:
https://github.com/Niko1221/Strata/commit/4c68013ea5fc413199584932b23fc654daf2bb5c  
Timestamp: **2026-09-29 20:09:44 UTC**.

Hardware / fixture:
- RTX 5070 **12 GB**, PCIe 5 x16;
- Ryzen 5 7600;
- 64 GB DDR5-5200;
- Windows 10;
- ready-made 0.1.26;
- same code-agent prompts as the 0.1.22 matrix;
- MTP spec4, greedy;
- INT8 KV above 4K;
- KV streaming from 64K;
- one shot / 256 generated tokens per cell.

Prompt throughput:

| Quant | 32K | 64K | 128K |
|---|---:|---:|---:|
| Q2_0 | 2,171 | 2,126 | 2,107 |
| IQ2_XS | 2,092 | 1,754 | 1,752 |
| **IQ3_XXS** | **1,745** | **1,609** | **1,602** |
| **IQ3_S** | **1,624** | **1,640** | **1,443** |
| Coder | 2,177 | 2,236 | 2,208 |

Versus 0.1.22, Strata documents **8-28% faster prompt processing at 32K-128K**.

The gains combine:
- 0.1.24 tensor-core QSA selection;
- 0.1.25 mapped grouping tables + fused norms/hyperconnection work;
- 0.1.26 batched draft-layer prompt execution.

This is strong enough to move P51 PP centers because the same weaker 12-GB GPU now clears the previous 5070-Ti centers by material margins.

### RECOVERED CURRENT — Strata engine 0.1.26 release

Source:
https://github.com/Niko1221/Strata/commit/f97ebb7a9238f2c5333cf5fff005cfff5286c04e  
Timestamp: **2026-09-29 18:01:05 UTC**, before this pass's strict boundary.

0.1.26 adds the MTP draft layer's batched prompt pass.

It should have been visible in the previous sweep, so it is classified **RECOVERED CURRENT**, not NEW. The target-moving evidence is the strict-window matrix publication above.

### PP target true-up

Previous IQ3_XXS:
- 32K 1,500
- 64K 1,400
- 128K 1,300

New:
- **32K 1,650 / ~90%**
- **64K 1,550 / ~90%**
- **128K 1,500 / ~90%**

Previous IQ3_S:
- 32K 1,450
- 64K 1,250
- 128K 1,200

New:
- **32K 1,550 / ~90%**
- **64K 1,550 / ~90%**
- **128K 1,350 / ~85%**

The centers remain below the single measured cells instead of copying them directly.

### Decode rows do NOT move TG targets

The same 12-GB matrix gives:

| Quant | 32K TG | 64K TG | 128K TG |
|---|---:|---:|---:|
| IQ3_XXS | 58.5 | 57.2 | 49.0 |
| IQ3_S | 48.3 | 46.3 | 45.5 |

These are useful physical receipts for the weaker card but do not supersede the exact RTX 5070 Ti evidence.

P51 retains:
- IQ3_XXS 128K mature center **78 TG / ~85%**;
- all other TG centers unchanged.

### UPDATE — Strata confirms verifier-width-dependent target arithmetic

Issue:
https://github.com/Niko1221/Strata/issues/152

The issue itself was opened before this pass's boundary, but the maintainer confirmation is a strict-window update.

Current native i-quant CPU expert dispatch:
- singleton expert groups: ggml `vec_dot`;
- groups with `nt >= 2`: custom AVX kernels.

Those implementations have slightly different FP32 reductions. Because expert group size changes with speculative/verifier width, **the target model's arithmetic can change when S changes**.

Reporter reproduction:
- same fixed weights + activations;
- width-1 calls versus width-2/4 grouped calls;
- **9,566 differing output cells**;
- forcing ggml `vec_dot` at every width makes width 1/2/4 bitwise equal;
- with the width-invariant path, a fixed **21,999-token** greedy prompt gives the same 150 target token IDs between plain and MTP;
- MTP accepts 93/130 proposals.

Maintainer confirmation:
- the width-dependent AVX dispatch is real;
- temporary width-invariant mode:
  `STRATA_NO_IQ512=1 STRATA_NO_IQ256=1 STRATA_NO_IQ4NL=1`;
- upstream intends one arithmetic path for all widths plus a width 1/2/4 gate.

P51 consequence:
- **target arithmetic may not depend on verifier width**;
- all AA/source-equivalence/MTP-certification runs must use the fixed/upstream-width-invariant path;
- default fast-path TG remains a legitimate throughput measurement but not an exact-serial quality certificate.

This is highly relevant to P69B13's existing rule that logical S cannot silently select a different arithmetic implementation.

### NEW — Strata low-RAM mode

Source:
https://github.com/Niko1221/Strata/commit/ac8b251b8120296dd013e4106a797461eab6a4c6  
Timestamp: **2026-09-29 19:23:21 UTC**.

Normal Strata:
- copies the model's expert corpus into pinned system RAM;
- GPU keeps the most-used experts resident.

Low-RAM mode:
- mmap's the pack's `experts.bin`;
- OS file cache retains/reclaims the cold expert pages;
- selected automatically when expert corpus + ~10 GB OS headroom does not fit;
- explicit `--low-ram on|off`.

Published Coder example:
- committed memory roughly **36 -> 13 GB**;
- same answers;
- big GPUs that retain most experts can stay near normal speed;
- smaller GPUs can become much slower because cold experts arrive from SSD.

P51 interpretation for the user's 64-GB host:
- valuable **fit/admission fallback**, particularly for tight IQ3_S;
- not the canonical benchmark mode;
- always label low-RAM results separately because they can become SSD/expert-I/O limited.

### UPDATE — Windows shared-GPU / commit accounting clarification

Strata issue #141 was closed during the strict window.

Maintainer explanation:
- Task Manager "shared GPU memory" can be the same pinned system RAM holding experts, counted again;
- Windows also charges GPU VRAM against process/system commit;
- pagefile reservation therefore does not by itself mean real paging.

P51 rule:
- admission should use actual physical availability + observed page activity/working-set behavior;
- do not sum RAM + shared-GPU + commit values as if they are three independent resident allocations.

### NEW — vLLM Mooncake coalesces packed hybrid/MLA KV transfer regions

Source:
https://github.com/vllm-project/vllm/commit/faacc13565312d29e9596d182fc808b452a4508e  
Timestamp: **2026-09-29 20:29:04 UTC**.

The connector now models transfer regions with:
- layer name/index;
- KV group;
- shared packed-group identity;
- block length / payload length;
- row offset.

It then coalesces adjacent compatible packed slices into larger copy operations.

Important semantics:
- physical contiguity alone is not enough;
- heterogeneous PP can transfer only the layer span shared by producer and consumer;
- same-PP incompatible layouts fail closed;
- hetero PP with no common layers can be an empty-success case;
- row bounds and packed-group identities constrain coalescing.

P51 CUDA->Apple/persistent-state consequence:
- first align **semantic state regions**;
- only then coalesce physically contiguous copies;
- transfer identity should include component/layer/group/row-offset/block-stride;
- pipeline partition differences may omit genuinely non-shared state, but never reinterpret a packed row.

This is cross-runtime transfer-contract evidence, not a CUDA->MLX physical bridge receipt.

### UPDATE — StrataGP audit confirms future optimization candidates

Issue:
https://github.com/Niko1221/Strata/issues/149

The maintainer responded in this window that future PRs should start with:
- sampler top-k;
- grouped Q2_0 kernel;
- IQ-grid decode;
- each rebased on 0.1.26;
- each default path byte-identical with parity tests and long-prompt / multi-GPU gates.

No P51 target changes until those PRs land and measure.

### SAME-DAY CURRENT — RTX 3090 / dual-3090 benchmark proposal

Issue:
https://github.com/Niko1221/Strata/issues/165  
Created: **2026-09-29 20:37:14 UTC**.

Proposed hardware:
- 2x RTX 3090 24 GB;
- EPYC 7453 VM;
- 165 GiB visible RAM;
- Strata 0.1.26;
- initial IQ3_XXS / 131K.

No benchmark data yet. Watch only.

### SAME-DAY CURRENT — M5 Max task-time warning

A current community report describes Qwen3.8-Flash-Next on M5 Max / MTPLX decoding around **30-40 TG** but taking dramatically longer than a hosted model on a simple coding task because the local model repeatedly reasons in circles.

P51 interpretation:
- another reason to keep **solved-task seconds / generated thinking tokens / agent trajectory quality** separate from physical TG;
- no Apple hardware calibration movement because the report lacks a controlled runtime/context/quality A/B.

### No new exact M1-Max receipt

Search again found:
- published MoEspresso exact 2021 M1 Max result around **12-15 TG**;
- M5-class reports/forks above that;
- no newly public exact-M1-Max fork/settings/context denominator for the claimed ~27 TG comment.

Dual-M1 40-TG probability stays unchanged.

## Strict-window negative scan

From **2026-09-29 19:09:40 -> 20:40:47 UTC**:

- **TensorFold:** no post-0.4.0 strict-window commit.
- **oMLX:** no strict-window Flash/27B commit.
- **mlx-serve:** no strict-window commit after the already-promoted multi-slot/QSA/MoE work.
- **Ishizuki:** no commit.
- **MoEspresso:** no commit.
- **DASLab official Flash IQ3_S:** no new source-paired 32K/64K/128K/262K semantic result found.
- **Exact dual M1 Max / TB4:** no new sustained filled-128K receipt.
- **Exact user's Windows 5070 Ti:** no frozen 0.1.26 IQ3 full PP ladder or >=8h soak on that exact machine yet.
- **Strata NVMe/shared conversation state:** no new strict-window merged production result beyond the work already tracked.

## Durable target changes

### IQ3_XXS cold PP

New:
- **32K 1,650 PP / ~90%**
- **64K 1,550 PP / ~90%**
- **128K 1,500 PP / ~90%**

### IQ3_S cold PP

New:
- **32K 1,550 PP / ~90%**
- **64K 1,550 PP / ~90%**
- **128K 1,350 PP / ~85%**

### Mandatory exactness gate

Before AA/source-equivalence/speculative certification:
- native expert arithmetic must be invariant to S/verifier grouping;
- use the conservative disable flags until upstream provides a qualified width-invariant fast path.

### Low-RAM fallback

For tight 64-GB-host configurations:
- low-RAM mmap experts may be used to achieve safe fit;
- do not mix its TG/PP into canonical tables unless explicitly labeled.

## Canonical planning state after this pass

- Dual-M1 Flash-Next: **40 TG @ genuine ~128K / 400 cold PP / ~70% >=40 TG**.
- Single-M1 dense27B: **25 TG / ~110 PP**.
- Strata IQ3_XXS ~128K: **78 TG / ~85% confidence**.
- Strata IQ3_XXS PP: **1,650 / 1,550 / 1,500**.
- Strata IQ3_S PP: **1,550 / 1,550 / 1,350**.
- Remaining Strata TG rows unchanged.
- IQ3_XXS AA>=38: **~85%**.
- IQ3_XXS AA>=40: **~65%**.
- IQ3_S AA>=40: **~80%**.
- INT8 K/V baseline -> K8V4 capacity candidate -> full Q4 aggressive arm.
- Swift lanes remain effective-task-throughput lanes.
- B2-B4 aggregate Apple ladder unchanged.

## New hard boundary

**2026-09-29 20:40:47 UTC**
