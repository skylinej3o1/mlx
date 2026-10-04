# Project 51 research watch — 2026-10-04 11:18 ET

Freshness boundary entering: **2026-10-04 14:31:51 UTC**
Cutoff: **2026-10-04 15:18:32 UTC**

## Decision

**No numeric TG/PP target movement and no fit/admission/stability-prior movement.**

Durable changes:

1. **CORRECTION / RECOVERED OLDER:** Strata 0.1.39 already contains a native stateless OpenAI Responses endpoint from
   commit 0ad8f70 (2026-10-03 16:35:35 UTC, #451). PR #759 was an alternative/duplicate contribution that closed
   unmerged; its closure did not remove Responses support.
2. **NEW:** current Codex compatibility is incomplete: issue #782 shows Codex 0.160.0 can send an input item of type
   additional_tools that Strata 0.1.39 rejects. Native Responses is therefore **present but not yet fully Codex-complete**.
3. **NEW:** #783 rebases the remaining verify/MTP CUDA fusion work onto 0.1.39 and reports ~9-10% decode gains on a
   fully resident 2x3090 IQ2_XS layer split with 0-ULP parity tests. This is promising mechanism evidence only; no
   sm_120 / 5070-Ti production credit yet.
4. **NEW:** #780 independently confirms that expert-pool worker count on hybrid Intel CPUs can be a major decode knob;
   four workers beat the 15-worker default by ~28.7% on its Windows IQ3_S configuration. This reinforces mandatory
   exact-box worker calibration after #775.
5. **NEW:** #781 shows that merely configuring 1M max context can roughly halve decode on a fixed ~44K active prompt
   even when expert work and cache residency are unchanged. Keep Project 51's production cap at native262K rather than
   overprovisioning max-context speculatively.
6. **UPDATE:** #378 elastic-KV rebased onto 0.1.39 but remains mutually exclusive with vram-elastic and batch slots.
   Our streamed INT8 KV / ~32K-resident production arm remains the simpler first 16-GB baseline.
7. **NEW:** #787 adds a parser fix for complete tool calls emitted before the model closes reasoning; useful server
   correctness work, but not native-model quality credit.

The strict hard boundary advances to **2026-10-04 15:18:32 UTC**.

## CORRECTION / RECOVERED OLDER — Strata 0.1.39 already has native Responses

Implementation commit:
https://github.com/Niko1221/Strata/commit/0ad8f70be456c79dcf5c9591f2daad0e1502de3b

Commit time: **2026-10-03 16:35:35 UTC** — older than this strict window, so this is never classified as NEW.

Current 0.1.39 source at 6f32ec0 contains:
- serve/responses.py;
- POST /v1/responses;
- README/DETAILS documentation for Codex CLI;
- function/namespace/custom tool handling;
- reasoning effort and structured-output translation;
- stateless full-history replay.

PR #759, which was noted in the previous pass, was a separate later contribution and closed unmerged. Its closure does
**not** mean Responses is absent.

Canonical correction:
- native Responses is **present in 0.1.39**;
- #759's 92.7K Codex/subagent receipt is still useful as a separate implementation receipt, but is not the origin of
  current upstream support.

## NEW — Strata #780: hybrid-CPU expert-pool worker calibration is a first-order decode knob

PR:
https://github.com/Niko1221/Strata/pull/780

Created **2026-10-04 14:36:51 UTC**.

Windows / IQ3_S / Intel 8P+16E host:
- 4 workers vs default 15;
- four-arm ABBA means: **95.05 vs 73.84 TG**, +28.7% for 4 workers;
- 8/8 workload-by-pair cells favor 4;
- pool-15 shows much larger variance.

The same report revises STRATA_PF_FUSED=1 on its IQ3_S arm to about +8.9% cold PP, but recall was not tested and the
fused path is not source-certification baseline material.

Project-51:
- #775 already showed 13 workers beating 19 on an i7-14700KF 5070-Ti system;
- #780 independently confirms the broader hybrid-core effect;
- exact-box pool-worker calibration is **mandatory before any 5070-Ti TG conclusion**;
- do not infer one universal worker count from either machine.

No numeric target movement.

## NEW — Strata #781: 1M configured context can damage performance before the active prompt is large

Issue:
https://github.com/Niko1221/Strata/issues/781

Created **2026-10-04 14:36:53 UTC**.

Same Windows IQ3_S system, same ~43,969-token prompt, same expert cache and similar routed-expert work:
- max-context 262K: 103.9 TG;
- 524K: 94.4 TG;
- 1M: **46.4 TG**.

At 1M, GPU-reach wait and GDN/QSA VRAM-touching stages grow sharply even though expert-work counters remain similar.
The reporter labels TLB/session-state locality as a hypothesis, not a measured root cause.

Project-51:
- keep configured production max-context at **262144**;
- do not configure 524K/1M “just in case” unless a workload requires it and the exact runtime is qualified;
- this reinforces the user's existing choice that native262K is enough;
- it does not change native262K TG/PP targets.

## NEW — Strata #782: native Responses exists, but Codex additional_tools is not accepted

Issue:
https://github.com/Niko1221/Strata/issues/782

Created **2026-10-04 14:48:28 UTC**.

Codex CLI 0.160.0 against the current Responses path receives:
- unsupported_parameter;
- input[0].type = additional_tools.

Project-51 protocol qualification therefore adds:
- current Codex CLI initial payload with additional_tools;
- full tools/skills prefix;
- function/custom/namespace tools;
- spawn/wait/close subagent workflow;
- full-history replay.

Until this passes, describe Strata 0.1.39 as **native Responses-capable but not fully Codex-compatible**.

## NEW — Strata #783: remaining verify/MTP fusion stack rebased onto 0.1.39

PR:
https://github.com/Niko1221/Strata/pull/783

Created **2026-10-04 14:51:01 UTC**, updated **15:04:03 UTC**.

On 2x RTX3090 24 GB, IQ2_XS, 100% resident layer split:
- verify-window latency: ~15.10 -> **13.07 ms** vs 0.1.39;
- three-prompt decode: roughly **+9-10%**;
- 25/25 GPU parity tests pass, described as 0-ULP bitwise parity.

Mechanisms include:
- fused HC/RMSNorm/quant operations;
- multi-row IQ kernels;
- shared expert / MMVQ fusions;
- QSA indexer/RoPE/router/KV multi-token fusions;
- MTP graph capture;
- parallel resident planning.

Project-51:
- high-priority future 5070-Ti A/B after base 0.1.39 qualification;
- **no production credit yet** because the receipt is dual 3090 / fully resident / IQ2_XS, not sm_120 16-GB IQ3_S;
- keep the earlier #646 sm_120 caution until an independent exact-5070 test exists.

## NEW — Strata #784/#785: 0.1.39 integration cleanup

#784:
https://github.com/Niko1221/Strata/pull/784
Created **2026-10-04 14:52:32 UTC**.

Fixes the SYCL port so the 0.1.39 tree compiles after thread-affinity/layer-range changes. No Arc physical run in the PR.

#785:
https://github.com/Niko1221/Strata/pull/785
Created **2026-10-04 14:59:55 UTC**.

Fixes a Responses test assumption when optional jsonschema is absent. This is also direct evidence that Responses is
part of the 0.1.39 server tree.

No Project-51 target effect.

## NEW — Strata #786: RDNA3 WMMA QSA prompt-attention path

PR:
https://github.com/Niko1221/Strata/pull/786

Created **2026-10-04 15:03:43 UTC**.

RX7900XTX / gfx1100 / IQ3-class production-mirrored setup:
- QSA prompt-attention kernel itself ~4-5x faster;
- 128K prefill **1513.8 -> 1863.2 PP (+22.8%)**;
- 32K **1669.3 -> 1968.0 (+17.9%)**;
- decode flat;
- opt-in only; default arithmetic unchanged.

Project-51 RX6800:
- mechanism is RDNA3/gfx1100-specific and does not transfer to gfx1030;
- useful evidence that QSA prompt attention is a major AMD PP seam;
- no RX6800 target credit.

## NEW — Strata #787: tool calls inside reasoning parser fix

PR:
https://github.com/Niko1221/Strata/pull/787

Created **2026-10-04 15:11:43 UTC**.

The patch lets the reasoning-state parser run the existing tool-call parser when a complete tool call appears before
the model closes its reasoning span, including chunk-split tags.

Project-51:
- add as a server/parser A/B for the existing reasoning->tool boundary gate;
- passing through this recovery path is logged separately from native well-formed model output;
- no model/quant quality credit from parser repair itself.

## UPDATE / RECOVERED OLDER — Strata #378 elastic KV rebased onto 0.1.39

PR:
https://github.com/Niko1221/Strata/pull/378

Created **2026-10-01**, updated **2026-10-04 15:17:39 UTC**.

New in-window comment:
- rebased onto 0.1.39;
- kv-grow cannot run beside vram-elastic because both reserve the expert-cache address range;
- it is also disabled beside batch slots;
- without the flag, short/2K/16K control outputs remain byte-identical to v0.1.39 in the stated test.

Project-51:
- keep streamed INT8 KV / ~32K resident as first production arm;
- elastic KV remains a later single-request optimization experiment, not the baseline.

## UPDATE / RECOVERED OLDER — Strata #358 deferred Windows arena registration

PR:
https://github.com/Niko1221/Strata/pull/358

Created **2026-10-01**, updated **2026-10-04 15:17:38 UTC**.

New in-window comment rebases it onto 0.1.39 and reports, on RTX5090/IQ2_XS/4-KB pages:
- old arena read 6.53 s;
- deferred registration 4.37 s;
- matching arena checksum.

Useful startup optimization evidence only; no steady-state target movement.

## NEW — Strata #788 cleanup BrokenPipe handling

PR:
https://github.com/Niko1221/Strata/pull/788

Created **2026-10-04 15:18:19 UTC**, 13 seconds before cutoff.

Handles a BrokenPipeError during server cleanup after the native engine has already exited. Lifecycle robustness only;
no runtime target effect.

## PUBLIC ARTIFACT CHECK — Swift Flash GSQ-RCO bucket unchanged

Public bucket:
https://huggingface.co/buckets/adamm-hf/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF-bucket

At cutoff it still lists:
- IQ3_XXS;
- IQ2_XS;
- Q2_0 experimental;
- **no IQ3_S**.

The bucket itself reports last update Sep 28. Therefore no Swift IQ3_S publication is classified as new in this pass.

## KNOWN / NO CHANGE

- No new paperniuk/ds4 commit after the prior boundary was found.
- No new npanj/slipstream commit after the prior boundary was found.
- DASLab IQ3_S remains the production-quality baseline.
- Swift Flash IQ3_S remains the highest-priority artifact to build/qualify.
- 5070-Ti fit remains ~97%; Windows 16-GB/64-GB admission ~90%; 8h/24h zero-stall ~75%/~55%.
- Dual-M1 production target remains native262K >=35 TG / >=400 cold PP.
- Dual-M1 performance target remains ~128K >=40 TG / >=425 cold PP.
- Native262K >=40 TG remains stretch.
