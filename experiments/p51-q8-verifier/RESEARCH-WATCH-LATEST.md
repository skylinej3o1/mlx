# Project 51 research watch — 2026-10-04 07:00 ET

Freshness boundary entering: **2026-10-04 00:51:42 UTC**
Cutoff: **2026-10-04 11:00:23 UTC**

## Decision

**No numeric fit/admission/stability/TG/PP target movement.**

The strict boundary advances to **2026-10-04 11:00:23 UTC**.

This pass does make seven durable strategy/qualification refinements:

1. **Swift 1.5 Flash-Next IQ3_S becomes the highest-priority model artifact to build and qualify.**
   The current public Swift Flash GSQ-RCO bucket still has IQ3_XXS / IQ2_XS / Q2_0 and no IQ3_S at the cutoff.
   However, the same Swift quant workflow already publishes an IQ3_S tier for Swift 1.5 27B, and the Flash release
   explicitly reuses matching ISTA allocation profiles before Swift-specific GSQ refinement. Therefore an IQ3_S
   Flash build is an engineering/reproduction task, not a new quantization research problem. DASLab IQ3_S remains
   production baseline until the Swift build passes the full xhigh suite.

2. **INT8 KV remains the practical long-context baseline, but “indistinguishable from FP16” is no longer an
   acceptable trajectory claim.** Strata #729 finds tiny median distribution shift and no depth-dependent KL growth
   through 240K, yet 13/16 greedy continuations fork within 32 tokens because near-ties amplify tiny perturbations.
   Certification must therefore compare task success / tool behavior / long-agent trajectories against FP16 controls,
   not require token identity and not infer equivalence from teacher-forced KL alone.

3. **RX6800 prefill-producer work remains exact-gfx1030, speculation-OFF first, with an added kernel-coverage gate.**
   Strata #703 shows nearby gfx1031 can sustain long heterogeneous Flash decode but then fail on long-history prefill
   with a missing PLE kernel image. That is useful caution, not direct gfx1030 evidence. No RX bridge/PP credit moves.

4. **Disk-backed continuation persistence graduates from a speculative feature to a serious post-baseline lane.**
   Strata #751 demonstrates an opt-in bounded disk LRU restoring a 4.46-GiB snapshot at ~258K tokens and reusing
   258,012 tokens with the same structured checks, plus byte-exact deterministic continuation across restarts at 4K.
   Initial production certification still keeps RAM conversation parking/persistence OFF; persistence is qualified
   separately after core inference/state correctness.

5. **Windows admission must consider commit capacity, not only reported free RAM.** Issue #730 shows page-locked
   complement allocation can fail while apparent RAM remains; PR #749 adds commit-capacity-aware admission/logging.
   This is pending/unmerged, so no admission-probability raise.

6. **Agent correctness gates expand beyond token generation.** Strata #710 shows a cross-request tool loop repeating
   an ineffective repair 98 times despite a per-request reasoning budget; #754 shows Anthropic tool markup can be
   emitted inside thinking and returned as end_turn rather than structured tool_use. Add cross-request repetition
   detection and Anthropic thinking/tool boundary cases to the Project-51 agent gate.

7. **Generic MLX still has meaningful prefill kernel headroom, but paperniuk/ds4 stays the M1 Flash baseline.**
   MLX #4621 reports large-M quantized_matmul slower than dequantize+BF16 matmul on M2 Max, with Qwen3.8-27B 4-bit
   8K prefill moving 137 -> 179 tok/s when switching paths. MLX #4516 separately updates a narrow-output QMV path
   with ~18-20% model-shaped Flash-layer step gains on M5 Max and bitwise-identical outputs. These are upstream
   mechanism clues only; they do not replace or numerically transfer into the M1-specific ds4 fork.

No newer Strata release than **0.1.38** was found in-window.

## SAME-DAY / KNOWN — paperniuk/ds4 M1 Flash work

The targeted 03:09 ET design true-up already persisted the important M1-Max Flash receipts that fall on the same
calendar day:
- tuned Q2_0 / IQ3_XXS / IQ3_S M1-Max rates;
- long-context QSA/indexer improvements;
- current prefill table including the ~398K chat;
- checkpoint/session-anchor behavior;
- IQ3_S memory planning and the shallow-expert-spill architecture.

Do not re-label these as new in this strict pass.

Repository:
https://github.com/paperniuk/ds4/tree/m1-flash-next

## SAME-DAY / UPDATE — Swift 1.5 IQ3_S build feasibility

Public Swift Flash bucket at cutoff:
https://huggingface.co/buckets/adamm-hf/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF-bucket

Swift 1.5 source / quant references:
https://huggingface.co/ukisai/Swift1.5-Qwen3.8-Flash-Next
https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF

ISTA Flash GSQ-RCO reference:
https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF

Classification:
- the 03:53 ET Swift BF16/IQ3_XXS audit is **SAME-DAY / KNOWN**;
- the conclusion that Project 51 should **build Swift Flash IQ3_S as the preferred challenger artifact** is an
  **UPDATE** to challenger ordering.

Implementation interpretation:
- reuse the exact ISTA Flash IQ3_S per-tensor allocation as the starting layout;
- quantize Swift weights with the Swift-specific importance/calibration path;
- apply Swift-specific GSQ refinement where reproducible;
- preserve and separately verify the MTP package;
- package n-gram/PLE separately/mmap-friendly;
- call an allocation-only build exactly that until GSQ refinement is actually applied.

Do not assume Swift BF16's coding/Terminal gains survive the new quant. The full Project-51 xhigh task ladder controls
promotion.

## NEW — Strata #703: nearby gfx1031 can decode long Flash, but long prefill can miss a kernel

Issue:
https://github.com/Niko1221/Strata/issues/703

Created **2026-10-04 00:54:36 UTC**.

On a heterogeneous RX9070XT gfx1201 + RX6750XT gfx1031 layer split:
- Qwen3.8 Flash IQ2_XS completed a 262K-token long generation at ~80.9 tok/s;
- Swift IQ2_XS completed ~75K generated tokens at ~72.5 tok/s;
- short prefill and fresh multimodal use worked;
- a later ~75K history prefill failed on gfx1031 with a native PLE post-op “no kernel image” error.

Project-51 impact:
- nearby gfx1031 proves useful HIP functionality exists in the RDNA2 family, but it does **not** certify RX6800/gfx1030;
- exact gfx1030 prefill remains the first proof target;
- require all prompt/PQSA/PLE kernels used by the producer path to execute at 32/64/96/128K before state-export work;
- speculation stays OFF for first proof.

## NEW — Strata #710: per-request reasoning budgets do not bound cross-request agent loops

Issue:
https://github.com/Niko1221/Strata/issues/710

Created **2026-10-04 01:25:34 UTC**.

A v0.1.38 Q2_0 coding/review workflow repeated the same ineffective shell repair **98 times** across separate
tool-result requests for ~34.9 minutes and still failed to complete by the one-hour harness deadline.

Project-51 impact:
- add harness-level repeated-action / no-state-change detection;
- report retries/corrections in the time-to-correct KPI;
- do not treat a per-request reasoning-token budget as an end-to-end loop bound.

This is a single workflow report, not evidence that IQ3_S or Swift necessarily shares the failure.

## NEW — Strata #729: INT8 KV stays statistically close but forks free generation at near ties

Issue:
https://github.com/Niko1221/Strata/issues/729

Created **2026-10-04 06:47:09 UTC**.

Setup:
- Qwen3.8 Flash-Next IQ3_S;
- RTX5090 32 GB / 192 GB RAM;
- 16 prefixes from 15K through 240K;
- FP16 KV vs INT8 KV, otherwise fixed engine/expert/prefill settings.

Results:
- median KL is around 1e-3 with no monotonic growth with context depth;
- several 195-240K points are lower than the older 8K mean;
- heavy-tail near-tie positions exist (e.g. 45K top-1 flips);
- **13/16 depths fork within 32 greedy tokens**, median first fork around token 8;
- three tested depths remained identical for all 32 tokens.

Interpretation:
- INT8 KV remains the fit/performance baseline;
- tiny average KL is compatible with rapidly different deterministic trajectories;
- xhigh certification compares task/agent outcomes to FP16 controls, especially near ties, tool loops and long
  trajectories;
- token identity is not required for quality equivalence.

No KV-memory or fit target moves.

## NEW — Strata #728 / #736: Swift field reports remain anecdotal controls

#728:
https://github.com/Niko1221/Strata/issues/728
Created **2026-10-04 06:43:29 UTC**.

A Windows RTX4090/64-GB user reports Swift 1.5 IQ2_XS at ~103 tok/s but later endless loops in OpenCode/Qwen Coder.
Root cause is unresolved; do not transfer this to Swift IQ3_XXS or a future IQ3_S build.

#736:
https://github.com/Niko1221/Strata/issues/736
Created **2026-10-04 07:49:51 UTC**.

A 5090-laptop/96-GB report says INT8 KV outperformed Q4_0 KV by ~12% in its tested Qwen setup. Useful directional
support for INT8 as the first baseline, but the issue's key measurements are screenshots and do not override the
stronger #729 distribution study.

## NEW — Strata #730 + PR #749: Windows free-RAM reporting is not enough for page-locked admission

Issue #730:
https://github.com/Niko1221/Strata/issues/730
Created **2026-10-04 07:10:13 UTC**.

On Windows 11 / 96 GB / RX6900XT, a Q4 run reports ~73 GiB available but cannot allocate the planned ~65.9-GiB
page-locked complement; it falls back to file reads and ~1 tok/s behavior while IQ3 works normally.

PR #749:
https://github.com/Niko1221/Strata/pull/749
Created **2026-10-04 10:26:02 UTC**, open.

The patch changes Windows allocation planning to respect **commit capacity** and improves allocation diagnostics.

Project-51:
- exact 5070-Ti qualification records Windows commit headroom in addition to RAM/VRAM;
- no admission-probability raise until the patch or equivalent behavior is independently exercised on the target box.

## NEW — MLX #4621: large-M quantized_matmul can lose to dequantize + BF16 matmul

Issue:
https://github.com/ml-explore/mlx/issues/4621

Created **2026-10-04 08:14:27 UTC**.

M2 Max 64 GB / MLX 0.32.3:
- affine 4/8-bit quantized_matmul is faster at decode-sized M;
- from ~512 rows upward it falls behind dequantize + BF16 matmul;
- Qwen3.8-27B 4-bit 8K prompt throughput reportedly rises **137 -> 179 tok/s** with the prefill-only path switch,
  without a peak-memory increase in that test.

Project-51:
- track as a generic MLX/prefill dispatch seam;
- do not transfer its M2 dense-27B rate to M1 Flash;
- paperniuk/ds4's model-specialized prompt kernels remain the production starting point.

## NEW — Strata #741/#742/#743: old NVIDIA prompt path gets large QSA/prefill gains

PRs created **2026-10-04 09:09 UTC**:
- #741 converts selected BF16 prefill projections to FP16 tensor-core paths below sm_80;
- #742 adds an FP32 tiled QSA scorer;
- #743 adds a streaming long-context top-k path.

On RTX2080Ti + Swift IQ3_XXS, the combined family of changes reports large prompt gains, including #742's
~22% at 128K / ~33% at 248K and #743's additional ~23% at 248K in its tested stack.

These are **sm_75-specific** and do not move 5070-Ti or M1 targets. They reinforce the general rule that QSA/top-k
and prompt projection dispatch can dominate deep-context PP.

## NEW — TensorFold #351/#352/#355/#357: more exact-kernel / multi-row / two-rank mechanism evidence

Relevant PRs created **2026-10-04 09:17-09:32 UTC**:
- #351: EXL3 Flash prompt chunk sizing up to 4,096 rows, up to ~16% one-stream PP in its GB10 tests;
- #352: B16 verify windows share each head weight load across rows and keep the same bits, yielding large verify
  speedups on GB10;
- #355: Qwen3.8-27B NVFP4 two-rank execution while preserving stored precision/layout;
- #357: page-locked host-memory row-parallel sums when two CUDA GPUs lack peer mapping.

Project-51:
- these are useful cross-runtime mechanism confirmations;
- #352 especially reinforces the already-adopted “read a weight once across multi-row verification” direction;
- no CUDA/GB10 rates transfer to M1/TB4.

## NEW — Strata #744/#745: gfx1100 tuning shows both warm-up and hipBLASLt table choice matter

#744:
https://github.com/Niko1221/Strata/pull/744
Created **2026-10-04 09:42:42 UTC**.

#745:
https://github.com/Niko1221/Strata/pull/745
Created **2026-10-04 09:55:00 UTC**, updated before cutoff.

On RX7900XTX 24 GB / IQ3_S:
- ROCm nightly vs packaged stack gives ~+10% warm steady-state decode in the submitted comparison;
- cold->warm decode rises roughly 35% on both stacks;
- after tuning a matching hipBLASLt table, 128K prefill is reported at **1687 vs 926 tok/s (+82%)** for the tuned
  table vs fallback, with decode unchanged.

Project-51 RX6800 implication:
- always separate cold and warmed cells;
- record ROCm/hipBLASLt versions and whether an exact gfx1030 tuning table is active;
- a missing/mismatched table can masquerade as a hardware/architecture limit;
- no numeric transfer from gfx1100 to gfx1030.

## NEW — Strata #748: fatal verification timeout containment gets an automatic-reload patch

PR:
https://github.com/Niko1221/Strata/pull/748

Created **2026-10-04 10:20:41 UTC**, open.

The patch marks the engine unavailable after native verification-timeout signatures, terminates it, and relies on the
existing lifecycle to reload on the next request instead of leaving a poisoned verifier reported as loaded.

Validation is synthetic/process-level, not an exact 5070-Ti soak. Keep zero probability credit until merged and
physically exercised, but it matches Project-51's required automatic-containment behavior.

## NEW — Strata #751: bounded disk LRU restores ~258K continuation state across restart

PR:
https://github.com/Niko1221/Strata/pull/751

Created **2026-10-04 10:32:27 UTC**, open.

Mechanism:
- streams authoritative INT8 K/V, QSA/GDN/PLE state, stage checkpoints and MTP draft K/V;
- bounded global disk LRU with atomic indexing;
- text-only INT8/MTP path, including layer-split GPUs, with RAM parking disabled.

Validation reported:
- Windows + 2x RTX3080 20 GB + IQ3_S;
- byte-exact deterministic continuation/branch checks across engine restarts at 4K;
- a **258,019-token** structured request passes nine checks;
- after graceful restart, a **4.46-GiB** snapshot restores and reuses **258,012 tokens**, with the same checks passing.

Project-51:
- elevate disk persistence to a serious later lane;
- still certify inference with conversation parking/persistence OFF first;
- later gate atomic failure handling, identity/version mismatch refusal, bounded disk behavior, write/restore latency and
  continuation equivalence at 128/200/250K.

## NEW — Strata #752/#753: concurrency correctness work is blocked on unmerged #559

Created **2026-10-04 10:36 UTC**, both draft/open:
- #752 preserves checkpoints when split allocation fails;
- #753 isolates per-request metrics under concurrent batch work.

Useful design material, but both explicitly depend on unmerged #559. No production or multi-agent capacity credit.

## NEW — Strata #754: Anthropic tool call can remain inside thinking and end as end_turn

Issue:
https://github.com/Niko1221/Strata/issues/754

Created **2026-10-04 10:47:04 UTC**.

On v0.1.38, a Pi/Anthropic-compatible workflow intermittently receives the intended <tool_call> markup as
thinking_delta content, then end_turn, with no structured tool_use block. The same session also has successful turns.

Project-51 parser/agent gate adds:
- tool markup emitted while the server believes it is inside reasoning;
- transition from thinking -> structured Anthropic tool_use;
- correct stop_reason;
- repeated runs because the failure is intermittent.

This joins the existing literal-tag / unclosed-think parser cases.

## UPDATE — MLX #4516: narrow-output QMV fast path gets model-shaped Flash evidence

PR:
https://github.com/ml-explore/mlx/pull/4516

Originally opened 2026-09-15; updated **2026-10-04 10:54:41 UTC**.

On M5 Max, the updated receipt reports:
- ~1.38x on an N=1 8-bit QMV microcase;
- ~1.20x / ~1.19x on Qwen3.8 Flash-Next layers 4-7 at context 128 / 4096;
- bitwise-identical outputs over the reported eight-step layer benchmark.

This is **UPDATE**, not new. It is M5/generic-MLX evidence and does not move the M1 ds4 target; audit whether the
corresponding narrow projections in paperniuk/ds4 already avoid this fallback before porting anything.

## KNOWN / NO CHANGE

- Strata release baseline remains **0.1.38**.
- 5070-Ti baseline remains IQ3_S/native262K with streamed INT8 KV (~32K resident first), released #646 excluded,
  and #693-style fine prefill chunking as the exact-box high-priority PP arm.
- No hardware purchase is needed.
- DASLab IQ3_S remains the production quality artifact.
- Dual-M1 goals remain:
  - production: native262K / >=35 TG / >=400 cold PP;
  - performance: ~128K / >=40 TG / >=425 cold PP;
  - stretch: native262K / >=40 TG.
- The strict quality rule remains source-like xhigh task/agent behavior; low-bit artifacts are never called lossless.
