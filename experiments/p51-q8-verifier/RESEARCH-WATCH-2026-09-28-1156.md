# Project 51 primary-lane research watch — 2026-09-28 11:56 ET

**Freshness boundary entering this pass:** **2026-09-28 13:58:58 UTC**.  
**User cutoff:** **2026-09-28 15:56:26 UTC**.

## Decision

**Dual-M1 and single-M1 targets unchanged. A dedicated Strata / RTX 5070 Ti target ladder is added to TARGETS.**

The new Strata lane is deliberately separate from the dense Qwen3.8-27B CUDA-v2 lane.

## NEW — exact RTX 5070 Ti post-fix liveness validation finally lands

Strata issue #31 comment at **2026-09-28 14:28:36 UTC** reports validation of the 0.1.14 GPU-copy fix on the original failure box:
- Windows
- **RTX 5070 Ti 16 GB**
- Ryzen 9800X3D
- 63/64 GB host RAM
- sustained single-slot HE+ workload
- three 164-task sweeps
- roughly **3.5 hours**
- q4_0 and int8 KV legs
- **zero stalls**
- **zero watchdog trips**

Before the fix, this workload was freezing roughly every **20–45 minutes**.

Reported HE+ score on the same run:
- q4_0: **153/164 = 93.3%**
- int8: **153/164 = 93.3%**

The reporter says 0.1.14 is at or above prior score bands while removing the stall.

**P51 consequence:** the production gate moves from 'exact-card fix not yet validated' to **'exact-card fix validated for ~3.5 h; require 8 h zero-stall soak for production promotion and 24 h for high-confidence endurance.'**

TARGETS now records:
- 8 h zero stalls/watchdogs: **~90% planning confidence**
- 24 h zero stalls/watchdogs: **~75%**

## NEW CORROBORATION — second 16-GB Blackwell / 64-GB host also clean on 0.1.14

Issue #31 comment at **14:52:36 UTC** reports a separate RTX 5060 Ti 16 GB / Ryzen 5700X3D / 64 GB host running a few sustained hours on 0.1.14 with **no stall and no watchdog trip**.

That box also confirms PCIe-link sensitivity: on PCIe 4.0 x8, measured H2D is ~13.7 GB/s and a lower pcie_frac materially beats the x16-style setting.

**P51 consequence:** Strata tuning must treat **PCIe bandwidth as an input to expert-streaming policy**, not assume one optimal resident/miss balance across cards.

## UPDATE — Strata 0.1.18

v0.1.18 published **2026-09-28 14:06:44 UTC**.

No core performance change relevant to P51. It adds clearer update behavior, a setup shortcut, and a guard so a zero-length penalty window does not touch an unsized sampler buffer. The server's normal path was not affected by that sampler guard.

## UPDATE — 16-GB / 64-GB Windows admission issue remains open

Strata #60 received another similar-issue report at **15:10:53 UTC**, but no maintainer diagnosis by cutoff.

The original failure still looks like an admission/headroom mismatch: whole-arena registration partly fails, auto cache sizing sees enough nominal free VRAM, then large expert-cache cudaMalloc fails.

This remains a separate production gate from the now-fixed generation deadlock.

## TARGET UPDATE — Strata / RTX 5070 Ti lane

TARGETS now has a dedicated section for **Qwen3.8-Flash-Next on Strata / RTX 5070 Ti 16 GB / 64 GB Windows**.

### IQ3_XXS balanced lane

| Context | TG target | TG confidence | Cold PP target | PP confidence |
|---|---:|---:|---:|---:|
| <=8K | **100** | **~75%** | — | — |
| ~32K | **95** | **~75%** | **1,300** | **~85%** |
| ~64K | **90** | **~80%** | **1,250** | **~80%** |
| ~128K | **78** | **~65%** | **1,150** | **~75%** |

Stretch: **90 TG @128K**, ~35–40% confidence until direct exact-card 128K receipt.

### IQ3_S quality-first lane

| Context | TG target | TG confidence | Cold PP target | PP confidence |
|---|---:|---:|---:|---:|
| <=8K | **85** | **~65%** | — | — |
| ~32K | **78** | **~65%** | **1,200** | **~80%** |
| ~64K | **70** | **~60%** | **1,150** | **~75%** |
| ~128K | **60** | **~55%** | **1,050** | **~70%** |

### Quality priors for custom AA certification

These are planning probabilities, not measured AA scores:
- IQ3_XXS **AA>=38: ~85%**
- IQ3_XXS **AA>=40: ~65%**
- IQ3_S **AA>=40: ~75%**

INT8 KV remains the quality baseline. Q4 KV remains an optional capacity/speed lane.

## Strict-window scan summary

From **13:58:58 -> 15:56:26 UTC**:
- **Strata:** exact-card 0.1.14 clean-soak receipt promoted; second 16-GB-card corroboration; 0.1.18 release; #60 admission risk persists.
- **Splash:** server/test/memory-plan maintenance only; no new M1 performance receipt.
- **vLLM:** no P51-primary Qwen3.8 result in-window.
- **llama.cpp:** no new P51-primary Apple/CUDA result in-window.
- **TensorFold / mlx-serve / oMLX / Ishizuki / MTPLX / DFlash:** no new merged physical M1 receipt in-window.

## Canonical planning effect

- dual-M1 Flash: **unchanged 40 TG @ ~128K / 400 cold PP / ~70% >=40**
- single-M1 dense: **unchanged 25 TG / ~110 PP**
- dense 5070-Ti CUDA-v2 ladder: unchanged
- **new Strata-specific Flash-Next target ladder added**

## New hard boundary

**2026-09-28 15:56:26 UTC**
