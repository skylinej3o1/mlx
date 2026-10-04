# Project 51 research watch — 2026-10-04 13:00 ET

Freshness boundary entering: **2026-10-04 15:18:32 UTC**
Cutoff: **2026-10-04 17:00:03 UTC**

## Decision

**No numeric TG/PP target movement and no fit/admission/stability-prior movement.**

Durable changes from this window:

1. **Exact RTX 5070 Ti + DASLab IQ3_S gets a useful 512..131K calibrated ladder.**
   Strata #791 reports roughly 96-100 TG from 2K through 131K and ~3.1K PP at 131K on a 96-GB Linux host.
   This complements, rather than replaces, #775's 257.6K Windows result (~43-53.5 TG after tuning).
2. **CORRECTION:** #781's apparent 1M-context decode collapse was not evidence that the configured context size itself
   was the cause. Updated #780 plus #799 show the slow arm had an oversized explicit expert cache that WDDM silently
   paged/overcommitted. With auto sizing, the same 1M configuration returned to ~102-122 TG.
3. **WDDM admission rule strengthens:** successful allocation is not enough. Preserve real VRAM headroom, use auto
   expert-cache sizing first, and treat near-zero free VRAM / sysmem fallback as a throughput failure even if startup succeeds.
4. **#796 is a serious admission-planner candidate:** it prices exact prefill bytes before committing expert residency and
   rejects/clamps unsafe plans, but it is open and lacks original Windows validation. No admission-prior raise.
5. **Slipstream current-head audit gets a hard MTP-enabled guard.** Commit 8df6674 restored one missing
   buffers.mtpEnabled assignment; its project notes say the regression caused 0% draft acceptance and ~15 TG instead
   of ~40-50+ TG. Any Slipstream benchmark must record commit + MTP acceptance.
6. **Tool-call quality accounting gets another middleware-assistance case:** Strata #790 can force the opening of a
   required/named tool call server-side. Useful in production, but not native model tool-choice success.
7. **Windows prebuilt stability gets a new negative signal:** #795 reports 20 STATUS_ILLEGAL_INSTRUCTION crashes across
   0.1.35/0.1.38 on a non-AVX512 i9-13900KF. Current 0.1.39 is not implicated yet; exact-box soak remains mandatory.

The strict hard boundary advances to **2026-10-04 17:00:03 UTC**.

## NEW — Strata #789: modest routed-only prefill scheduling gain

PR:
https://github.com/Niko1221/Strata/pull/789

Created **2026-10-04 15:31:38 UTC**.

Changes routed-only short-chunk prefill scheduling so shared-expert work overlaps CPU grouping/uploads and resident
experts no longer consume stream-ahead slots.

On RTX3060/Linux/Coder IQ1_M:
- routed-only cases: roughly **+0.8% to +2.8% PP**;
- full 1024-token stream chunks: essentially flat.

Correctness checks report matching generated tokens, GDN state hashes and sampled residual bytes.

Project-51:
- useful scheduling seam;
- too small / wrong hardware/model to move any target.

## NEW — Strata #790: forced OpenAI tool_choice

PR:
https://github.com/Niko1221/Strata/pull/790

Created **2026-10-04 15:34:43 UTC**.

Adds Chat Completions support for tool_choice="required" and named-function choices by writing the opening tool-call
prefix server-side, including after reasoning ends.

Project-51 rule:
- production clients may use this;
- benchmark accounting marks it **server-forced tool intent**, not native model selection;
- argument quality remains a model/parser question.

## NEW — Strata #791: exact 5070 Ti + IQ3_S context ladder

Issue:
https://github.com/Niko1221/Strata/issues/791

Created **2026-10-04 15:47:02 UTC**.

Hardware/config:
- single RTX 5070 Ti 16 GB;
- Linux;
- 96 GB DDR5;
- Core Ultra 7 265K;
- Strata 0.1.38 source build;
- DASLab IQ3_S;
- context 262144;
- INT8 KV resident in VRAM;
- calibrated per configuration;
- spec4 / min-p 0.70;
- one request at a time.

Single-card IQ3_S:
- 2K: **1982 PP / 100.4 TG**;
- 8K: **3241 PP / 100.4 TG**;
- 32K: **3393 PP / 95.9 TG**;
- 64K: **3333 PP / 99.5 TG**;
- 131K: **3147 PP / 99.1 TG**.

The native GSQ path was reported within about ±5% on repeat sweeps. No retrieval/quality suite was run.

Same report compares 2x RTX5060Ti layer split:
- 131K: ~2969 PP / ~62.7 TG;
- single 5070 Ti is materially faster for decode across the ladder.

Project-51 interpretation:
- measured exact-GPU performance anchor for <=131K;
- complements #775 at ~257.6K;
- **does not transfer admission to the user's 64-GB host**;
- reinforces that one strong 16-GB card can beat a two-card layer split when per-token synchronization/CPU work dominates.

No prior movement.

## NEW — Strata #792: fully-resident batch zero-doorbell fix

PR:
https://github.com/Niko1221/Strata/pull/792

Created **2026-10-04 15:50:39 UTC**, updated **16:49:27 UTC**.

Fixes #776: fully resident stages record a zero-doorbell verify graph, while batch host paths incorrectly waited for a
per-layer ring that never fires.

On 4x RTX4090 + IQ3_S:
- before: first batch window repeatedly kills/restarts the engine;
- after: 12/12 short-prompt and 6/6 30K-100K concurrent requests complete;
- solo path stays ~178 -> 177 TG.

Project-51:
- useful multi-agent correctness fix;
- irrelevant to initial single-5070 baseline;
- no throughput credit to M1 or 5070 single-request targets.

## NEW — Strata #793: active-slot batching + Prometheus metrics/autoconfig

PR:
https://github.com/Niko1221/Strata/pull/793

Created **2026-10-04 16:06:21 UTC**.

Relevant pieces:
- avoids padding all idle slots in a batch group;
- adds Prometheus metrics including TTFT, inter-token latency, e2e latency, prefix-cache hits and draft acceptance;
- adds an autoconfig/calibration helper.

On 4x RTX5080 IQ3_S:
- 2 concurrent: 99 -> 149 aggregate TG;
- 4 concurrent: 199 -> 222;
- 8 concurrent: ~366 -> 371.

Project-51:
- useful instrumentation for the time-to-correct-agent-result KPI;
- no single-request target transfer.

## NEW — oMLX #4248: group-size-32 fused HC kernels

PR:
https://github.com/jundot/omlx/pull/4248

Created **2026-10-04 16:02:31 UTC**.

M5 Ultra / Qwen3.8 Flash group-size-32 4-bit checkpoints:
- MTP off: ~48 -> **110-113 TG (~2.3x)**;
- Lightning MTP: ~170 -> **219 TG (+29%)**;
- prefill: **+21-22%**;
- oQ5e group-size-64 control remains effectively unchanged.

The new fused path changes text on affected g32 checkpoints because its FP32 epilogue rounds differently from canonical
BF16 operations; it is not an exact-path optimization for those checkpoints.

Project-51:
- strong warning to audit HC fast-path eligibility/layout before comparing Apple quant formats;
- no M5 numeric transfer and no direct IQ3_S/ds4 target credit.

## NEW — Strata #795: non-AVX512 Windows illegal-instruction report

Issue:
https://github.com/Niko1221/Strata/issues/795

Created **2026-10-04 16:20:01 UTC**.

Reporter:
- i9-13900KF (no AVX512), RTX4090, Windows 11, 64 GB RAM;
- official prebuilt 0.1.35 and 0.1.38;
- IQ2_XS / IQ3_S;
- long 100K-230K agent workloads;
- **20 Windows Error Reporting crashes**, all c000001d / strata.exe, with clustered instruction offsets.

This is a serious negative signal for the older Windows prebuilts, but current 0.1.39 has not yet been shown to share it.

Project-51:
- exact-box 0.1.39 qualification records CPU ISA and includes long-agent soak;
- if the target CPU lacks AVX512, do not assume the expert-kernel AVX2 log proves every binary path is portable;
- no 8h/24h prior movement until 0.1.39 is reproduced or cleared.

## NEW — Splash #299: tool-call grammar/parsing moves toward vLLM semantics

PR:
https://github.com/incoai/splash/pull/299

Created **2026-10-04 16:22:58 UTC**.

Fixes cases where constrained argument grammar could reorder/drop/rename fields or coerce strings such as "12:00" into
numbers. The new default leaves auto/non-strict tool arguments unconstrained, closer to vLLM/SGLang behavior, while
strict/required/named calls retain structural grammar.

Real-model testing reports large gains in exact tool-call argument reproduction.

Project-51:
- add schema-order / union-type / extra-field cases to the tool gate;
- parser/grammar assistance remains separate from native model quality.

## NEW — Strata #794: layer-split cost model sees per-stage PCIe bandwidth

PR:
https://github.com/Niko1221/Strata/pull/794

Created **2026-10-04 16:19:30 UTC**.

On an intentionally asymmetric 2x4090 setup where card 2 is physically x1:
- old auto split: ~350 PP at a 29K prompt;
- link-aware split: ~1410 PP.

Project-51:
- direct evidence that topology-aware placement matters;
- reinforces the M1 rule that TB4 transfer cost must be priced explicitly in stage placement;
- no numeric transfer.

## NEW — Strata #796: unified startup VRAM plan

PR:
https://github.com/Niko1221/Strata/pull/796

Created **2026-10-04 16:46:22 UTC**.

Mechanism:
- price exact Prefill::bytes_needed before committing expert-cache residency;
- make expert residency the elastic consumer;
- use one accepted chunk/loan/ring plan as the runtime contract;
- revalidate after WDDM-touch behavior;
- refuse/clamp unsafe configurations before the first prompt rather than relying on allocation success.

Measured on RTX4070Ti SUPER 16 GB / Linux:
- 524K + requested 24576 prefill: previously failed before READY;
- planner selects safe 17664 owned chunk and reaches **2139 PP / 22.8 TG**;
- another unsafe no-KV-residency arm is clamped to 2048 rather than handed blindly to the driver.

Not yet validated on the original Windows/WDDM rig or layer-split stage caches.

Project-51:
- high-priority candidate for exact 5070-Ti/64-GB admission;
- **no ~90% Windows-admission increase until physical target-box validation**.

## UPDATE — Strata #780/#799 correct the prior 1M-context interpretation

#780:
https://github.com/Niko1221/Strata/pull/780

#799:
https://github.com/Niko1221/Strata/pull/799

Updated/created in-window through **16:59 UTC**.

The prior #781 observation was real, but its interpretation changed:
- explicit 11,631-slot cache at 1M: 0 MiB free, **13.7-14.7 TG**;
- auto cache 11,178 slots: ~217 MiB free, **102-122 TG**;
- auto + 1500-MiB reserve: 88.9-101.4 TG;
- explicit 9,148 slots / ~4.1 GiB free: 94-97 TG.

Only ~453 slots (~0.86 GiB) separated catastrophic slowdown from normal performance.

The slow arm even had a higher cache hit rate. The explanation is Windows/WDDM overcommit/sysmem fallback, not extra
expert work and not demonstrated TLB pressure from max-context alone.

Canonical correction:
- configured 1M is **not proven inherently slow**;
- Project 51 still does not need >262K for production;
- use auto cache/reserve first and verify real free VRAM after allocations;
- “cudaMalloc succeeded” or high hit rate is not a throughput-safety proof.

## NEW — Slipstream 8df6674: MTP enable flag restored

Commit:
https://github.com/npanj/slipstream/commit/8df66743474af7d3ec353234172a82e8b13025c8

Committed **2026-10-04 16:57:51 UTC**.

A one-line runtime assignment restores buffers.mtpEnabled = mtpDrafting(). Slipstream's project notes say an earlier
multi-architecture merge omitted it, leaving 0% draft acceptance and ~14.6-15.9 TG; restoring it returns the project's
observed Flash-Next decode to roughly 40-50+ TG.

Project-51:
- Slipstream remains a mechanism donor, not the quality artifact;
- pin commit identity for every comparison;
- verify MTP acceptance is non-zero before using a Slipstream TG receipt;
- treat silent 0% acceptance as a runtime regression, not model-quality evidence.

Companion commits at 16:58 rename the canonical binary to slipstream and update docs; no target effect.

## NEW — Strata #798: Linux hybrid CPU P/E detection bug

Issue:
https://github.com/Niko1221/Strata/issues/798

Created **2026-10-04 16:57:23 UTC**.

On Arrow Lake Linux, cpu_capacity equality classifies only two favored cores as P-cores rather than 8P/16E, which can
distort pool-worker/affinity defaults.

Project-51:
- target 5070-Ti Windows path is not affected by this Linux-specific detector;
- if the RX6800 Linux producer uses a hybrid Intel CPU, pin pool workers manually until fixed.

## PUBLIC ARTIFACT CHECK — Swift Flash IQ3_S still absent

At cutoff the public Swift Flash GSQ-RCO repository still lists:
- IQ3_XXS: 75.97 GB;
- IQ2_XS: 68.15 GB;
- Q2_0 experimental: 66.55 GB;
- **no IQ3_S**.

Swift Flash IQ3_S therefore remains a Project-51 build/qualification target rather than a newly published artifact.

## KNOWN / NO CHANGE

- No new paperniuk/ds4 commit after the prior boundary was found.
- DASLab IQ3_S remains the production-quality baseline.
- Swift Flash IQ3_S remains the highest-priority model challenger to build/qualify.
- 5070-Ti physical-fit prior remains ~97%.
- Windows 16-GB/64-GB admission remains ~90%.
- 8h / 24h zero-stall remain ~75% / ~55%.
- Dual-M1 production remains native262K >=35 TG / >=400 cold PP.
- Dual-M1 performance remains ~128K >=40 TG / >=425 cold PP.
- Native262K >=40 TG remains stretch.
