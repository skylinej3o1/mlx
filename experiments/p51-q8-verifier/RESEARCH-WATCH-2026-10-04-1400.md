# Project 51 research watch — 2026-10-04 14:00 ET

Freshness boundary entering: **2026-10-04 17:00:03 UTC**
Cutoff: **2026-10-04 18:00:16 UTC**

## Decision

**No numeric TG/PP target movement and no fit/admission/stability-prior movement.**

This pass does tighten the Strata quality/correctness gate:

1. **NEW quality blocker / unresolved:** Strata #803 reports roughly **7-10% worse teacher-forced perplexity than
   llama.cpp on the same token IDs / GGUF**, already at 2K where QSA is dense. The issue is not yet reproduced on the
   production DASLab IQ3_S artifact, so it is not evidence that IQ3_S quality is degraded. It is strong enough that
   Strata production promotion now requires a cross-engine teacher-forced sanity check on the exact production artifact.
2. **UPDATE correctness blocker:** #783's kernel parity suite passed, yet a partially-resident dual-3090 Swift run
   diverged on 4/5 greedy prompts. The author isolated a 1-ULP fused norm/RoPE SASS difference plus a partial-residency
   expert-buffer path and pushed a fix at 17:58 UTC. The fix has not yet been independently rerun on that reporter's
   end-to-end gate by this cutoff. Project-51 exactness therefore requires full-request controls under realistic
   residency/topology, not only kernel parity.
3. **NEW real-agent parser evidence:** #804 reports complete tool calls emitted inside an unclosed thinking block in
   4 of ~1050 IQ3_S agent responses. This independently validates the reasoning->tool parser gate already tracked.
4. **UPDATE KPI evidence:** #764 shows ~8.5% higher raw decode in one Swift laptop A/B while median request wall time
   stays essentially unchanged because reasoning length/acceptance changed. This is direct support for the
   time-to-correct-agent-result KPI over raw TG.
5. **UPDATE AMD caution:** #646 receives a gfx1100 report where 0.1.39 is ~2.3% slower than 0.1.38 in a controlled
   partially-resident setup. Root cause is unknown; exact RX6800/gfx1030 measurements remain mandatory.
6. No new paperniuk/ds4 work landed in-window. No public Swift Flash GSQ-RCO IQ3_S artifact appeared.

The strict hard boundary advances to **2026-10-04 18:00:16 UTC**.

## NEW — Strata #800: Volta QSA accumulation accuracy fix

PR:
https://github.com/Niko1221/Strata/pull/800

Created **2026-10-04 17:03:11 UTC**.

V100-only prompt-attention change keeps high/low FP16 products in separate accumulator chains before FP32 combination.
Reported parity-vs-FP64 improves materially with ~1.5-2% kernel-time cost; one teacher-forced model check also moves in
the expected direction.

Project-51:
- useful reminder that seemingly tiny accumulation-order choices can measurably alter distributions;
- Volta-only, no 5070/M1/RX target transfer.

## UPDATE — Strata #783: end-to-end greedy divergence found despite parity suite, then root-caused

PR:
https://github.com/Niko1221/Strata/pull/783

New comments at **17:09:19 UTC** and **17:58:33 UTC**.

First external A/B:
- 2x RTX3090 24 GB;
- Swift 1.5 IQ3_XXS;
- partial residency (~82%);
- 0.1.39 vs #783;
- raw decode **+6.5-7.8%**;
- stock-vs-stock exact on 5/5 greedy prompts;
- PR-vs-stock exact on only 1/5.

The PR author then identified:
- a 1-ULP difference in fused QSA RMSNorm+RoPE caused by fast-math/SASS contraction/FTZ behavior;
- a separate !all_resident expert-buffer path mismatch;
- added kill switches and new bitwise fused-vs-unfused RoPE tests;
- force-pushed a fix at 17:58:33 UTC.

Important classification:
- the divergence finding and proposed fix are **UPDATE** to an older PR, not a new PR;
- by cutoff there is **no independent rerun** of the reporter's 5-prompt end-to-end gate after the fix.

Project-51 quality rule:
- kernel/unit parity is necessary but insufficient;
- every performance patch touching arithmetic/scheduling must run end-to-end greedy controls under:
  - full and partial residency;
  - single-card and split topology where applicable;
  - long prompt;
  - fixed MTP acceptance/draft counts where possible;
- no speed credit until the relevant end-to-end gate passes.

## NEW — Strata #802: IQ1_S support + low-bit CPU/file-tier work

PR:
https://github.com/Niko1221/Strata/pull/802

Created **2026-10-04 17:19:47 UTC**.

Adds IQ1_S GPU support, IQ1_S/IQ1_M AVX2 kernels and faster file-tier read-ahead. W7800/30-GiB-host data reports:
- UD-IQ1_S now loads;
- 14.5 -> 20.4 TG with new AVX2 low-bit expert kernels in the compared arm;
- cold start ~193 -> ~110 s on FUSE-NTFS.

Project-51:
- low-bit implementation evidence only;
- quality class is far below the production IQ3_S policy and receives no target/quality credit.

## NEW — Strata #803: unresolved cross-engine perplexity gap

Issue:
https://github.com/Niko1221/Strata/issues/803

Created **2026-10-04 17:29:48 UTC**.

Reporter compares identical token IDs and scoring positions across Strata and llama.cpp on Qwen3.8 Flash-Next.

Representative reported values:
- llama.cpp AP-Q4_K_XL: ~4.00-4.02 perplexity;
- Strata 0.1.32 / 0.1.39 AP-Q4_K_XL: **~4.387**;
- 6-chunk aggregate: llama.cpp ~5.015 vs Strata ModelOpt-NVFP4 ~5.552;
- 2K chunks still show ~7% gap, where QSA is dense.

A/B switches that reportedly do not remove it include FP16 KV, RoPE table, adaptive swaps, CPU-vs-GPU expert ownership,
GR variants and several fork defaults.

Important limits:
- this is **not** the production DASLab IQ3_S artifact;
- it uses AP-Q4_K_XL / NVFP4 variants and a custom packing path;
- docs contain older UD-Q4_K_XL parity evidence that appears inconsistent with this report;
- root cause is unknown and the methodology has not yet been independently audited.

Project-51 decision:
- do **not** lower the DASLab IQ3_S quality prior from this issue;
- before Strata is promoted as a production quality runtime, run exact-artifact cross-engine teacher-forced/logprob
  controls at 2K and long context using identical token IDs;
- if a persistent gap exists, isolate dense/recurrent/QSA/MTP/output-head paths before trusting task parity alone.

## NEW — Strata #804: tool call inside unclosed reasoning observed in real IQ3_S agents

Issue:
https://github.com/Niko1221/Strata/issues/804

Created **2026-10-04 17:31:23 UTC**.

Observed on GSQ-RCO IQ3_S agent use:
- **4 / ~1050 responses** emitted a complete <tool_call> inside <think> without </think>;
- current parser returns it as reasoning_content, with no structured tool_calls and finish_reason=stop;
- the agent silently stops.

This is the same class already targeted by PR #787, but #804 adds real-agent frequency and stronger reproduction/false-positive
controls.

Project-51:
- retain reasoning->tool boundary as a mandatory agent gate;
- parser rescue is reported separately from native well-formed model output;
- add the observed implicit-reasoning-end rate to parser telemetry.

## NEW — Strata #805: lazy vision / per-GPU elastic caches, closed unmerged

PR:
https://github.com/Niko1221/Strata/pull/805

Created **2026-10-04 17:41:50 UTC**, closed unmerged.

On a 2xV100 service, lazy vision temporarily returns ~1.74 GiB VRAM to expert caches when no image request is active.
Useful mechanism, but:
- closed unmerged;
- multi-GPU/vision lane only;
- not relevant to initial Project-51 text qualification.

No canonical target effect.

## UPDATE — Strata #646: gfx1100 0.1.39 regression signal

PR:
https://github.com/Niko1221/Strata/pull/646

New comment **2026-10-04 17:42:50 UTC**.

RX7900 GRE / IQ3_XXS / 128K / partially resident:
- seven alternating fresh-process pairs;
- 0.1.39 reportedly **~2.33% slower** decode than 0.1.38;
- all seven pairs slower;
- fresh prefill roughly flat;
- configuration also changes THP behavior / prompt loans between versions, so kernel attribution is unresolved.

Project-51:
- no numerical transfer to RX6800/gfx1030;
- keep 0.1.38-vs-current A/B in the RX producer bring-up if 0.1.39 underperforms unexpectedly.

## UPDATE — Strata #764: faster raw TG does not imply faster task completion

PR:
https://github.com/Niko1221/Strata/pull/764

New Windows laptop comment **2026-10-04 17:55:34 UTC**:
- Swift 1.5 IQ3_XXS;
- same short coding request;
- delayed adaptive swap arm raises median decode about **8.5%**;
- all implementations pass the independent task checks;
- median request wall time is essentially unchanged: ~40.37 vs ~40.05 s;
- generated reasoning lengths and draft acceptance differ.

Project-51:
- direct support for tracking total successful task wall-clock, reasoning tokens, retries and output length in addition
  to TG;
- no raw-TG-only promotion.

## UPDATE — Strata #757 same 16GB/64GB fit receipt

PR #757 was updated at **17:58:43 UTC**, but its current body retains the already-canonical 4090-Laptop / 64-GB
IQ3_S 128K/256K fit and speed data. No new planning movement is extracted.

## PUBLIC ARTIFACT CHECK — Swift Flash IQ3_S still absent

Current public Swift Flash GSQ-RCO page still lists:
- IQ3_XXS: 75.97 GB;
- IQ2_XS: 68.15 GB;
- Q2_0 experimental: 66.55 GB;
- **no IQ3_S**.

Do not confuse newly published 27B Swift IQ3_S derivatives with a Flash-Next IQ3_S artifact.

## KNOWN / NO CHANGE

- No new paperniuk/ds4 commit after the prior boundary.
- Slipstream's MTP-enable restoration at 16:57:51 UTC was already inside the previous strict window and remains KNOWN.
- DASLab IQ3_S remains the production-quality artifact.
- Swift Flash IQ3_S remains the highest-priority challenger to build/qualify.
- 5070-Ti physical-fit prior remains ~97%.
- Windows 16-GB/64-GB admission remains ~90%.
- 8h / 24h zero-stall remain ~75% / ~55%.
- Dual-M1 production remains native262K >=35 TG / >=400 cold PP.
- Dual-M1 performance remains ~128K >=40 TG / >=425 cold PP.
- Native262K >=40 TG remains stretch.
