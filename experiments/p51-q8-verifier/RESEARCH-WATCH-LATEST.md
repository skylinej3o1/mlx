# Project 51 research watch — 2026-10-04 10:31 ET

Freshness boundary entering: **2026-10-04 12:27:27 UTC**
Cutoff: **2026-10-04 14:31:51 UTC**

## Decision

**No dual-M1 TG/PP target movement. No fit/admission/stability-prior movement.**

Durable changes from this window:

1. **Exact RTX 5070 Ti + DASLab IQ3_S + native262K Windows performance is now directly demonstrated**, but on a
   96-GB host rather than the target 64-GB host. A single-run community receipt reaches 43.0-53.5 TG after calibration
   at a 257,630-token prompt, versus ~17 TG stock.
2. **Do not assume native OpenAI Responses support in Strata.** PR #759 was closed unmerged; a community router can
   translate Responses to Chat Completions, but that is an adapter lane, not the engine baseline.
3. **gfx1030 bring-up improves:** PR #778 fixes a current-main HIP compile blocker and reports end-to-end RX6950XT
   execution, but the intermittent #649 verify-timeout signal remains unresolved and the Project-51 RX6800 producer
   still requires exact gfx1030 measurements.
4. **Current source/engine line identifies as 0.1.39 at commit 6f32ec0**, and #777 reports a published Windows engine
   at that commit. The GitHub Releases page still showed v0.1.38 as Latest during this pass. Pin BUILD.json + commit
   for every benchmark instead of relying on the word “latest.”
5. **Linux 0.1.39 THP policy can catastrophically slow startup under memory pressure** (#771), relevant to the RX6800
   Linux producer host even though it does not alter steady-state TG/PP.

The strict hard boundary advances to **2026-10-04 14:31:51 UTC**.

## NEW — Strata #766: packaged ROCm 10.0 gfx1100 hipBLASLt table

PR:
https://github.com/Niko1221/Strata/pull/766

Created **2026-10-04 12:36:12 UTC**.

Independent RX7900XTX / ROCm 10.0.0 / hipBLASLt 1.4.1 (100401) data reports, with an exact-version tuning table:
- 370-token prompt: 319 -> 371 PP;
- 1,670: 682 -> 1,038 PP;
- 6,471: 857 -> 1,524 PP;
- decode unchanged within noise.

This independently reinforces the previous #745/#755 conclusion: exact hipBLASLt table/version state can dominate AMD
prefill. For RX6800, record the exact ROCm/hipBLASLt build and whether a gfx1030 table is active. No gfx1100 numeric
transfer.

## UPDATE — Strata #759 native Responses contribution was closed unmerged

PR:
https://github.com/Niko1221/Strata/pull/759

At the previous cutoff it was open. It was closed **2026-10-04 12:54 UTC**, unmerged.

Therefore:
- do not list native /v1/responses as an assumed upcoming Strata production capability;
- retain its 92,672-token Codex/tool/subagent run as useful **protocol feasibility evidence only**;
- if Project 51 uses Codex against Strata before native support lands elsewhere, qualify an explicit adapter/router
  separately from model/runtime quality.

This supersedes the previous pass's “once the selected Strata build includes this work” wording.

## NEW — Strata #768 ROCm Docker build

PR:
https://github.com/Niko1221/Strata/pull/768

Created **2026-10-04 12:41:22 UTC**.

Adds a ROCm Docker build path, defaulting to gfx1100/gfx1101/gfx1200/gfx1201 but explicitly allowing gfx1030 additions.
Operationally useful for repeatable RX experiments; no performance or correctness credit by itself.

## NEW — Strata #770 asks for 27B support

Issue:
https://github.com/Niko1221/Strata/issues/770

Created **2026-10-04 13:07:37 UTC**.

This is a feature request only. No Strata 27B implementation/benchmark exists from this issue, so Project 51's
single-M1 27B lane remains based on MLX/oMLX/TensorFold/Splash work, not Strata.

## NEW — Strata #771: 0.1.39 Linux MADV_HUGEPAGE startup pathology

Issue:
https://github.com/Niko1221/Strata/issues/771

Created **2026-10-04 13:15:09 UTC**.

On Linux / RTX5070Ti / 62-GiB RAM / IQ3_XXS, the reporter isolates a host-memory-pressure case where requesting
transparent huge pages with kernel defrag=madvise makes the expert arena fault path crawl. The reported end-to-end
startup is about **432 s** with the THP request versus **~25 s** when that request is skipped, even though the engine's
later “loaded GiB/s” line can look healthy.

Project-51 RX6800/Linux producer implication:
- record /sys/kernel/mm/transparent_hugepage/enabled and defrag policy;
- include an arena-THP-off A/B if startup becomes pathological;
- do not confuse startup compaction stalls with model prefill throughput.

No TG/PP target movement.

## NEW — oMLX #4245: exact g32 hyper-connection projection

PR:
https://github.com/jundot/omlx/pull/4245

Created **2026-10-04 13:20:02 UTC**.

On M5 Ultra, group-size-32 Qwen3.8 Flash 4-bit checkpoints gain an exact hybrid hyper-connection projection path.
Reported MTP-off decode moves ~48 -> 75-77 TG (+55-57%) while outputs remain byte-identical to the pre-change canonical
path. MTP-on is essentially unchanged because that path is not used there.

Project-51 interpretation:
- strong Apple mechanism evidence that HC dispatch compatibility can hide a very large single-row penalty;
- audit ds4's IQ3_S/Swift tensor shapes and HC path before assuming a generic MLX/oMLX fast path applies;
- no M5 numeric transfer to M1 and no reason to replace paperniuk/ds4 as the M1 Flash baseline.

## NEW — Strata #772: external Responses router, not native engine support

Issue:
https://github.com/Niko1221/Strata/issues/772

Created **2026-10-04 13:51:45 UTC**.

Community project strata-router translates /v1/responses to Strata Chat Completions and adds sticky multi-node routing.
It is useful architecture evidence for:
- explicit protocol adaptation;
- session affinity to preserve KV;
- move-to-idle-node only when reread cost is small.

But it is external middleware. It does not change Strata's native protocol baseline or model-quality certification.

## NEW — Strata #773: Linux direct expert-file reads under severe SSD streaming

PR:
https://github.com/Niko1221/Strata/pull/773

Created **2026-10-04 13:57:04 UTC**.

On a 30-GB Linux host / RTX3080Ti 16 GB / native Q4_K_M with only 16 GiB of experts resident, O_DIRECT + Linux AIO
raises reported decode from **4.38 -> 7.90 TG aggregate (~1.8x)** across the test prompts and improves startup.

Project-51:
- additional mechanism support for direct/unbuffered SSD expert streaming under severe memory pressure;
- not transferable to the much shallower ~8-12-GiB M1 IQ3_S spill plan;
- keep direct-I/O/read-ahead as optional spill experiments after the basic almost-local topology works.

## NEW — Strata #775: exact RTX5070Ti + IQ3_S + native262K Windows speed receipt

Issue:
https://github.com/Niko1221/Strata/issues/775

Created **2026-10-04 14:05:29 UTC**, updated **14:24:06 UTC**.

Hardware/config:
- RTX 5070 Ti 16 GB;
- i7-14700KF;
- **96 GB DDR5-5600** host RAM;
- Windows;
- Strata 0.1.38;
- DASLab Qwen3.8-Flash-Next GSQ-RCO **IQ3_S**;
- vision encoder on GPU;
- max context 262,144;
- INT8 KV streaming with 32,768 resident cells;
- one 257,630-token repo-source/docs prompt;
- greedy, reasoning off.

Single-run results (reporter explicitly warns normal ±20% noise):
- stock spec4 / no calibration / shipped profile: **17.5 cold / 17.2 warm TG**;
- spec6 + calibration: **43.0 cold / 53.5 warm TG**;
- plus learned expert profile: **45.5 cold / 47.0 warm TG**;
- prompt reading: **1,468 -> 1,744 PP**.

Calibration sub-results on that box:
- pool workers: 19 -> 36.9 TG, **13 -> 54.4**, 10 -> 41.3;
- spec-min-p: 0.3 -> 36.6, 0.5 -> 41.7, **0.7 -> 44.6**;
- pcie-frac: **0.0 -> 42.1**, 0.2 -> 37.9, 0.35 -> 27.9, 0.55 -> 23.9, 0.75 -> 20.7.

Interpretation:
- **Measured source fact:** exact target GPU + exact target quant + native262K can exceed 40 TG on Windows.
- **Non-transfer:** host RAM is 96 GB, CPU is known, runs are single samples, and settings change expert placement /
  speculation. This is not proof of the user's 64-GB exact box.
- **Engineering inference:** after clean admission, >=40 TG at native262K is now a realistic 5070-Ti tuning expectation,
  not a speculative ceiling.
- **Qualification rule:** do not simply copy spec6/profile settings. Sweep pool workers, spec4/spec6, pcie-frac,
  spec-min-p and profile use on the exact box. Keep deterministic source/quant gates on frozen residency first.

No fit/admission prior moves: the 96-GB host does not close the 64-GB Windows admission question.

## UPDATE — Strata source/engine line is 0.1.39, but release labeling is transient

Commit:
https://github.com/Niko1221/Strata/commit/6f32ec070f23ced9f50e704d854d775da52591ab

The source at 6f32ec0 identifies project version **0.1.39**, and #777 below says its Windows benchmark used the
published 0.1.39 engine at that exact commit.

However, during this pass GitHub's Releases page still listed **v0.1.38 as Latest**.

Project-51 rule:
- benchmark software identity by **BUILD.json + git commit + engine version**, not “latest”;
- use 0.1.39/6f32ec0 as the next current-engine qualification candidate when setup actually supplies it;
- retain 0.1.38 as the comparator until 0.1.39 passes the exact 5070-Ti/64-GB cold-admission + agent soak;
- do not move 8h/24h stability priors based on version number.

## NEW — Strata #777: 0.1.39 Windows benchmark on RTX5090

PR:
https://github.com/Niko1221/Strata/pull/777

Created **2026-10-04 14:14:57 UTC**.

Windows / RTX5090 32 GB / ~93.7 GiB host / IQ3_XXS / context262144 / INT8 KV streamed at 32K:
- 4K: 3775 PP / 171.7 TG;
- 32K: 6367 PP / 181.2 TG;
- 128K: 6080 PP / 178.3 TG;
- 6/6 needles.

Useful as a current-engine smoke/identity receipt, not a 5070/IQ3_S speed transfer.

## NEW — TensorFold #386: level-2 CUDA sleep/wake with prefix preservation

PR:
https://github.com/ashhart/TensorFold/pull/386

Created **2026-10-04 14:20:31 UTC**.

Single-device CUDA can release model memory while keeping the HTTP frontend and optional conversation-prefix snapshots.
Reported Qwen3.8-27B + DFlash continuation remains exact in its tested configurations and decode medians stay within
~1% across sleep/wake.

Project-51: useful future workstation-sharing mechanism; no production credit now. Initial qualification still avoids
dynamic memory lifecycle features.

## NEW — TensorFold #387: mixed prefill/decode fairness matters for multi-agent throughput

PR:
https://github.com/ashhart/TensorFold/pull/387

Created **2026-10-04 14:24:02 UTC**.

On one DGX Spark / Flash EXL3 / 4 concurrent long requests, scheduler changes move aggregate generation roughly:
- 32K: ~47 -> ~101 TG;
- 64K: ~44 -> ~80 TG;
while preventing individual streams from sitting near 1-4 TG during another request's long prefill.

Project-51 multi-agent rule:
- report per-agent progress/latency, not aggregate TG alone;
- mixed prefill+decode fairness is part of time-to-correct-agent-result;
- no single-stream M1/5070 target movement.

## NEW — Strata #778: current-main gfx1030 compile fix + RX6950XT smoke

PR:
https://github.com/Niko1221/Strata/pull/778

Created **2026-10-04 14:27:06 UTC**.

HIP clang / ROCm 7.1 rejects the current shared-buffer alignas placement on gfx1030. The PR moves alignment to a
portable declarator attribute. With this plus #648's split-shard arch guard, the author reports:
- current main builds for gfx1030;
- UD-Q4_K_XL re-split runs end to end on RX6950XT;
- 3/3 clean verify-window runs;
- the #649-class stall did not reproduce in those three runs.

Project-51 RX6800 impact:
- gfx1030 is no longer treated as merely hypothetical compile support;
- **do not close the reliability question**: #649 remains an intermittent timing-sensitive report, three clean runs
  are insufficient, the quant is UD-Q4 rather than target IQ3_S, and the card is RX6950XT rather than RX6800;
- exact RX6800 first proof remains target-only/speculation OFF, cold 32/64/96/128K PP, required QSA/PLE kernel coverage,
  then state export/import to M1.

## NEW — Strata #779: last-second 0.1.39 Swift/16GB/64GB crash report

Issue:
https://github.com/Niko1221/Strata/issues/779

Created **2026-10-04 14:31:30 UTC**, 21 seconds before this cutoff.

Windows / RTX4090 Laptop 16 GB / 64 GB host / Swift IQ3_XXS / engine0.1.39 startup logs show:
- streamed KV;
- partial host pinning after whole-arena registration fails;
- ~444 MiB VRAM free after load.

The issue title says “laptop crash with latest,” but the body at cutoff is primarily startup logs plus a screenshot,
without enough textual root-cause detail to classify the failure.

Project-51:
- record as **NEW negative signal / insufficient diagnosis**;
- do not move Swift, fit or stability priors from one incomplete report;
- revisit after maintainer diagnosis or reproducible failure steps.

## KNOWN / SAME-DAY / NO CHANGE

- No new paperniuk/ds4 commit after the prior boundary was found.
- No new npanj/slipstream commit after the prior boundary was found.
- No public Swift 1.5 Flash-Next **GSQ-RCO IQ3_S** release was found by cutoff.
- Swift Flash IQ3_S remains the highest-priority artifact to build/qualify.
- DASLab IQ3_S remains the production-quality baseline.
- Dual-M1 goals remain:
  - production native262K >=35 TG / >=400 cold PP;
  - ~128K >=40 TG / >=425 cold PP;
  - stretch native262K >=40 TG.
- 5070-Ti 16GB/64GB fit prior remains ~97%; Windows admission remains ~90%; 8h/24h zero-stall remain ~75%/~55%.
