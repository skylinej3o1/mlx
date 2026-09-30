# Project 51 primary-lane research watch — 2026-09-30 04:40 ET

**Freshness boundary entering this pass:** **2026-09-30 05:37:52 UTC**.  
**User cutoff:** **2026-09-30 08:40:26 UTC**.

## Decision

**Durable STATE + TARGETS update.**

Two planning changes:

1. **IQ3_XXS + genuine 262K on the exact RTX 5070 Ti is now physically demonstrated in Strata.** The remaining fit uncertainty is the user's 64-GB host, not GPU/native-context execution.
2. The old Strata IQ3_XXS PP centers are retired. Exact-card cold prefill is roughly **3.0K PP around 60K** and **2.668K PP at 257K**, so the planning ladder moves materially upward.

No generic TG-center or AA-prior movement because the new 95–118 TG full-context samples were list-style outputs with favorable draft acceptance.

Maximum-context physical-fit prior, conditional on the planned compressed-streaming implementation:
- previous: **~85%**
- now: **~90%**

## NEW — exact RTX 5070 Ti + IQ3_XXS genuinely processes 257K in Strata

Strata issue #200  
Created: **2026-09-30 06:00:03 UTC**

Setup:
- RTX **5070 Ti 16 GB** / sm_120
- Ryzen 7 7700
- **93 GB RAM**
- Ubuntu 24.04
- CUDA 13.2
- IQ3_XXS native pack
- streamed **INT8 KV**
- `--kv-resident 32768`
- MTP `--spec 4` / rt-cjk
- context **262,144**
- engine 0.1.27 + PR #189/#194; those PRs do not alter prompt/decode math.

Direct physical receipt:
- **257,466-token prompt read from zero**
- **96.5 s**
- **2,668 PP**
- clean rejection when prompt + reply exceeds 262,144.

Other observed output:
- ~151K–257K active depth: **95–118 TG**
- reporter explicitly says these were list-style answers that draft unusually well.

Classification:
- **real filled-context PP receipt**
- **real full-context decode receipt**
- TG is **optimistic workload evidence**, not a generic 262K center.

This replaces our prior state where exact-5070Ti 262K evidence was only allocation/startup or transferred from another 16-GB NVIDIA card.

## NEW — exact-card host/KV footprint substantially narrows the 64-GB uncertainty

Same issue #200:

| Window | Pinned K/V | System RAM available after load on 93-GB host |
|---|---:|---:|
| 128K | **1.55 GiB** | **~44 GB** |
| 262K | **3.09 GiB** | **~43 GB** |

Interpretation:
- 262K adds only ~1.54 GiB pinned host K/V over 128K;
- the 93-GB machine still has ~43 GB available after load;
- therefore the steady loaded model/runtime footprint is far below 93 GB.

Still missing:
- exact 64-GB machine;
- peak load/staging overlap;
- Windows commit/headroom behavior;
- exact custom K6/V4 streamed implementation.

P51 fit prior therefore moves **~85% -> ~90%**, not to 100%.

One metadata caution: issue #200's setup says `--vram-reserve-mib 1058`, while one table header says expert-cache slots use reserve 700. Do not use that slot-count row as an exact 1058-reserve comparison. Issue #199 provides the controlled reserve A/B separately.

## NEW — exact-card Strata PP planning ladder moves sharply upward

Issue #199  
Created: **06:00:02 UTC**

Same RTX 5070 Ti / IQ3_XXS class, with safe 1,058-MiB VRAM reserve:
- ~60K cold prompt 1: **2,993 PP**
- ~60K cold prompt 2: **3,000 PP**

Issue #200:
- 257,466 cold prompt: **2,668 PP**

New P51 IQ3_XXS planning centers:

| Context | Previous | New |
|---|---:|---:|
| 32K | 1,650 | **3,000 PP** |
| 64K | 1,550 | **2,900 PP** |
| 128K | 1,500 | **2,750 PP** |
| 262K | none | **2,500 PP** |

The new centers include a deliberate haircut from Linux/93-GB measurements for the user's Windows/64-GB target.

IQ3_S PP remains unchanged until an exact-card IQ3_S ladder lands.

## NEW — 262K retrieval quality declines with length; FP16 KV does not fix it

Issue #200 uses an adversarial exact-value retrieval task:
- thousands of nearly identical records;
- query one value;
- 10 positions distributed from 2% to 99.5%;
- greedy.

INT8 KV:
- 29K: **10/10**
- 73K: **9/10**
- 151K: **8/10**
- 257K: **6/10**

INT8 vs FP16:
- 151K: **8/10 vs 8/10**, including the same two wrong answers;
- 257K: **6/10 vs 7/10**.

FP16 penalty:
- ~60K PP: **2,993 -> 2,463**
- 257K cold: **96.5 s -> 117.3 s**
- roughly **18–20% slower PP**
- output speed unchanged.

Interpretation:
- INT8 remains the source-quality control;
- long-context semantic degradation is not primarily an INT8-KV problem in this fixture;
- “fits at 262K” does not certify “agent semantics stay source-like at 262K.”

P51 262K qualification must include:
- MRCR / adversarial retrieval;
- semantic continuity;
- tool/agent trajectory persistence;
- xhigh source-vs-quant;
- compaction policy.

## NEW — safe 16-GB VRAM reserve for CJK draft + vision

Issue #199:

RTX 5070 Ti / IQ3_XXS / vision / rt-cjk / streamed INT8 KV:
- old setup reserve 700 MiB -> **154–156 MiB free**, below Strata's 256-MiB warning threshold;
- reserve **1,058 MiB** -> **~510 MiB free**.

Cost:
- ~2% lower PP;
- no meaningful TG loss in the reported A/B.

P51 production rule:
- for **vision + CJK draft** on a 16-GB Blackwell card, begin around **1.0–1.1 GiB reserve** and log actual free VRAM;
- do not maximize expert slots into the engine's own low-headroom warning region.

This does not necessarily apply unchanged to text-only/no-vision operation.

## NEW — Strata sm_120 Linux CUDA 12.8 MTP prefill crash; CUDA 13.0 works

Issue #220  
Created: **08:38:38 UTC**

Setup:
- RTX PRO 5000 Blackwell 48 GB, sm_120;
- Strata 0.1.27;
- IQ3_S;
- context 262K;
- Linux.

CUDA 12.8 build:
- short decode works;
- multi-thousand-token MTP prefill deterministically dies with:
  `prefill copy_i32: an illegal memory access was encountered`.

Same source rebuilt with CUDA 13.0:
- 17,104-token prompt: **2,473 PP**
- decode: **98 TG**
- no crash.

P51 rule:
- record Strata toolkit/runtime on every Blackwell result;
- require a qualified **CUDA 13.x** Strata build for sm_120.

Keep separate from the existing llama.cpp IQ compiler correctness gate:
- CUDA 13.2.0/13.2.1 had silent IQ corruption;
- llama.cpp IQ lane requires **13.2.2 / nvcc 13.2.86+**.

Do not merge those into one universal version rule without evidence.

## NEW — unresolved Strata first-request batched-prefill stall on RTX 5060 Ti

Issue #217  
Created: **08:00:19 UTC**

RTX 5060 Ti 16 GB / Swift IQ2_XS / 0.1.27:
- first request of a fresh server;
- batched prompt path;
- stalls before generation;
- watchdog reports GPU ring fired but plan/copy flags remain zero;
- persists after prior generation-stall and stale-error fixes.

No exact 5070-Ti reproduction.

P51 consequence:
- no speed/fit probability change;
- production promotion still requires >=8h exact-box soak **plus repeated cold long-prompt starts**, not just steady decode.

## NEW — oMLX Flash-Next B8: shared MTP is slower than MTP-off

Issue #4111  
Created: **05:54:10 UTC**

M5 Ultra / Qwen3.8-Flash-Next oQ5e:
- 8 concurrent requests
- MTP on: **272 TG aggregate**
- MTP off: **293 TG aggregate**

In-process:
- ordinary 8-row decode step: **23.9 ms**
- depth-3 shared verify across 8 requests: **81.5 ms**
- ordinary step while MTP enabled but parked: **25.1 ms**
- MTP fully off: **23.6 ms**

Reason:
- at B8, rows mostly route to different experts;
- shared verification loses much of the expected shared-weight advantage;
- current policy spends many warmup/losing cycles before parking and relearns after cohort changes.

P51 rule:
- MTP enable/depth must depend on **batch size + context + cohort stability**;
- park immediately on a clear loss;
- retain the verdict across a stable cohort;
- don't assume MTP is beneficial merely because B1 acceptance is high.

## NEW — mlx-serve M5 Max sorted-gather parity hole just above 32K rows

Issue #649  
Created: **08:31:27 UTC**

M5 Max 128 GB:
- segmented NAX sorted gather;
- **33,010 rows**
- n=64, k=128
- 4-bit, group64
- differs from stock MLX despite a test contract expecting bit equality.

Other shapes pass, including:
- smaller 2,048/4,096-row small-N/K;
- **81,920-row** Flash-shaped large-N/K cases.

P51 Apple rule:
- long-context kernel certification must sweep:
  - row-count boundaries;
  - small-N/K tails;
  - verifier-width shapes;
  - production large-N/K shapes.
- Passing the big 80K production shape does not prove the 32K-boundary tail/verifier shape.

## NEW — SGLang clamps restored state to the frontier promised at admission

Commit:
`51cae5f303ec3c0c8fe20976c274fda8fc5bb1fe`  
Timestamp: **07:26:15 UTC**

Bug:
- prefill promises decode a specific restore length;
- while L3->L2 restore waits, another request can grow the radix tree;
- a later rematch then finds *more* tokens than the original promised frontier;
- restoring the longer match breaks destination geometry.

Fix:
- clamp restore to the original `restore_token_count`.

P51 rule:

> A restore/import transaction is valid only through its **committed promised frontier**. Later cache growth may create a better future match, but cannot silently advance the state already in flight.

This directly reinforces the CUDA->Apple committed-frontier contract.

## NEW — SGLang makes Qwen3.8-Flash-Next-FP8 an AMD nightly correctness target

Commit:
`b87a241a6f977c2de475b1f7029d23c0b50adf09`  
Timestamp: **07:54:36 UTC**.

Nightly:
- Qwen/Qwen3.8-Flash-Next-FP8;
- MI35x TP1;
- MI30x TP2+EP2;
- EAGLE speculation;
- graph decode;
- GSM8K + multimodal smoke.

Reported GSM8K across ROCm versions:
- **0.968–0.971**.

Useful as cross-backend correctness/adoption evidence only.

## NEW — oMLX overlaps SSD expert reads with resident-route GPU compute

Commit:
`503fdb9cff317273bc422c1952e9a79adbb92e0e`  
Timestamp: **07:13:59 UTC**.

Qwen3.8-Flash-Next oQ4e / M4 Air 32 GB / USB4 SSD / ~18.8% expert residency:
- warm: **3.56 -> 5.03 TG**
- cold: **3.17 -> 4.52 TG**
- later refined A/B: USB4 SSD **3.38 -> 4.54 TG**
- output byte-identical.

Mechanism:
- gather resident routes before blocking for missing experts;
- overlap read latency with GPU work;
- only enable overlap when reads remain pending >0.5 ms;
- preserve cache mutation order.

P51 interpretation:
- good mechanism for low-residency / SSD-backed Apple lanes;
- no numerical transfer to M1 Max;
- especially relevant if Flash weights/PLE cannot stay fully resident.

## NEW — oMLX fixes misleading PP telemetry with prefix hits

Commit:
`853d69cf92d94c661c7934688442ea17dce2bed8`  
Timestamp: **07:41:31 UTC**.

Old metric:
- divided the *whole prompt*, including cached prefix, by actual prefill time;
- prefix hits produced fake **6K–23K PP** numbers on a machine whose real prefill was ~1.7K.

New metric:
- counts only tokens actually prefilled in the request.

P51 measurement rule strengthened:
- PP denominator must be **freshly computed tokens**, not total logical prompt length when restored/reused state exists.

The exact Strata #200 257K receipt is safe under this rule because it explicitly reads **from zero**.

## SAME-DAY CURRENT — Reddit/community evidence

Current Reddit search finds:
- 64-GB consumer systems running Strata IQ3-class Flash at shorter context and reporting large gains;
- no timestamped, auditable **64-GB + IQ3_XXS + filled ~257K** Strata receipt inside this strict window.

Classify as adoption/supporting evidence only.

## Strict-window negative scan

From **2026-09-30 05:37:52 -> 08:40:26 UTC**:

- **Strata main:** no new engine commit/release; the key new evidence is issues #199/#200/#217/#220 and open PR work.
- **Exact user host class:** no 64-GB filled-257K IQ3_XXS receipt.
- **TurboQuant Flash:** no new K6/V4 Strata implementation.
- **DASLab:** no new official source-paired 262K AA/semantic-quality result.
- **Dual M1 Max/TB4:** no new sustained filled-128K physical TG receipt.
- **MoEspresso / TensorFold / Ishizuki:** no strict-window commit moving the primary P51 targets.

## Canonical target state after this pass

### RTX 5070 Ti / Strata IQ3_XXS

TG:
- keep existing controlled TG centers;
- new **95–118 TG @151K–257K** is an optimistic list/draft-friendly receipt, not the generic center.

Cold PP:
- **32K: 3,000**
- **64K: 2,900**
- **128K: 2,750**
- **262K: 2,500**

262K physical fit:
- exact 5070 Ti / 257K execution: **proven**
- exact 64-GB host: **not yet proven**
- Project-51 compressed-streaming conditional fit prior: **~90%**

Quality:
- IQ3_XXS AA>=38: **~85%**
- IQ3_XXS AA>=40: **~65%**
- IQ3_S AA>=40: **~80%**
- K6/V4 262K long-horizon quality: **~60–70%**

### Apple / dual-M1

No TG/PP-center movement.

New mandatory gates:
- B1/B2/B4 context ladder;
- MTP-on/off/depth by cohort size;
- 32K-ish row-boundary + small-N/K kernel parity;
- SSD overlap only with exact output/state parity.

## New hard boundary

**2026-09-30 08:40:26 UTC**
