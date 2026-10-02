# Project 51 research watch — 2026-10-02 10:24 ET

Freshness boundary entering: **2026-10-02 12:27:00 UTC**
Cutoff: **2026-10-02 14:24:02 UTC**

## Decision

**No canonical TG/PP center, fit prior, context target, hardware-purchase decision, or Strata/TurboQuant implementation order changes.**

Strata **v0.1.35 remains the latest release** at this cutoff. The exact-box plan remains:
- IQ3_S first;
- stock Strata first;
- one RTX 5070 Ti 16 GB + 64 GB DDR5;
- native 262,144;
- vision off initially;
- MTP off for base fit, then spec4;
- stock INT8 KV -> K8V4 -> Q4 capacity arm;
- custom TurboQuant only if stock measurements justify it.

This pass does, however, change two implementation beliefs:

1. **oMLX now has an active, direct Qwen4Exp / Flash-Next TurboQuant-QSA integration PR.**
   This is the first adjacent runtime in the current watch chain with source-visible TQ handling for QSA state,
   prefix-cache reconstruction and fused prefill rather than a generic KV wrapper only.

2. **The obvious Strata CPU-affinity fix is dead.**
   New measurement shows the serve host thread was already pinned. The CPU expert pool remains first-order on
   low-VRAM lanes, but future speed work should target pool arithmetic / serialization rather than host-thread placement.

## NEW — oMLX #4206: direct Flash-Next TurboQuant-QSA integration

PR:
https://github.com/jundot/omlx/pull/4206

Created **2026-10-02 13:23:24 UTC**, therefore inside this strict window.

The title advertises:
- Qwen4Exp YaRN context extension;
- full fused TurboQuant-enabled prefill on NAX and simdgroup;
- 1M context on an M5 Max at 4-bit TQ.

The source diff is more important than the headline. It adds explicit Qwen4Exp/QSA TurboQuant machinery, including:
- `TurboQuantQSAKVCache` / `BatchTurboQuantQSAKVCache`;
- QSA-specific cache payloads carrying compressed K/V plus dense indexer sidecar;
- block/prefix-cache slicing and reconstruction for the hybrid TQ-QSA state;
- fused QSA TQ parameter structures and prefill kernel plumbing;
- YaRN scaling support derived from the native 262,144 window.

This means TurboQuant is no longer merely an abstract port idea in the Apple Flash-Next ecosystem: an active oMLX
branch is wiring it through QSA and cache reuse.

**Limitations at this cutoff:**
- PR is open / unmerged;
- no M1 Max measurement;
- no controlled M1/M2/M3 simdgroup benchmark;
- no long-agent quality/KL table;
- no evidence that TQ4 is appropriate for Project-51's fidelity target;
- the 1M claim is outside Project-51's production target anyway.

Project-51 action:
- add #4206 to the Apple watch lane;
- once review stabilizes, test the **native262K** path first, not 1M YaRN;
- for dual M1 Max, require simdgroup-path PP/TG and long-agent quality before any target movement;
- do not transfer M5-Max capacity claims to M1 Max.

This does **not** alter the Windows/Strata decision to test stock INT8/K8V4 first.

## NEW — Strata #500: real serial CPU barrier found, but the +69-78% headline is not certified

PR:
https://github.com/Niko1221/Strata/pull/500

Created **2026-10-02 13:18:49 UTC**.

Source-code fact:
- multi-token verification previously quantized intermediate expert activations serially on the host between
  gate/up and down phases;
- the patch adds pool `mode 7` and distributes those independent quantization jobs across ExpertPool workers;
- the diff is small and the intended arithmetic is unchanged.

Reported box:
- i9-14900K;
- RTX 4090 24 GB;
- 64 GB DDR5;
- Windows 11;
- heavy DASLab IQ3_S;
- MTP spec4.

Reported decode:
- cold: **51.2 -> 91.1-92.9 TG**;
- warm: **62.1 -> 105.2 TG**.

Do **not** accept those percentages as a Project-51 speed receipt yet.

The performance arms also report:
- expert-cache hit rate **~80-85% -> 92.8-95.0%**;
- MTP acceptance **50-60% -> 60.7-67.9%**.

Those quantities should not move merely because independent activation-quant jobs execute in parallel under a truly
frozen residency / deterministic A/B. They show that the measured run changed more than the isolated barrier
(or at minimum that state-dependent residency/drafting contaminated the end-to-end comparison).

Project-51 certification request for this mechanism:
- fixed expert-cache size and placement;
- `--adapt-swaps 0`;
- `--pcie-frac 0` for arithmetic repeatability arm;
- `--prompt-cache 0`;
- same prompt/token stream;
- fresh process per arm;
- report phase-7 time directly;
- then separately re-enable production cache behavior.

The mechanism is credible and potentially high-leverage for the user's strong DDR5 host.
The **69-78% headline is planning-excluded** until a controlled arm exists.

## NEW / CORRECTION — Strata #501 closes the host-thread pinning hypothesis

PR:
https://github.com/Niko1221/Strata/pull/501

Created **2026-10-02 13:37:18 UTC**, then closed unmerged.

Follow-up measurement to #494 found that the serve host thread is already pinned:
- main/host stayed on core 0;
- eight workers stayed on 2,4,6,8,10,12,14,16;
- 120 x 50-ms samples found no host/worker collision.

Same-binary A/B:
- pin-off mean 25.88 TG;
- explicit pin-on mean 25.82 TG;
- **-0.3% mean delta**, inside noise.

The proposed fix was therefore closed as redundant.

Durable correction:
- #494 remains strong evidence that the CPU expert pool can dominate a low-VRAM decode round;
- **host-thread pinning is not the next lever on the measured path**;
- attention moves to pool compute, expert-cache behavior and serialized phases such as #500.

## NEW — Strata #499: IQ3_S operational on a 16-GB Windows AMD card

PR:
https://github.com/Niko1221/Strata/pull/499

Created **2026-10-02 12:50:14 UTC**.

Reported setup:
- RX 9070 XT 16 GB;
- Threadripper 3960X;
- 128 GiB DDR4-3200;
- Windows 11;
- ready-made Strata 0.1.35 HIP engine;
- IQ3_S;
- 65,536 context;
- INT8 KV;
- MTP on;
- vision off.

Measured medians:
- decode: **45.2 TG** [37.1-46.4];
- 4K cold prompt: **370 PP**;
- 32K cold prompt: **601.5 PP**.

Memory:
- expert arena: **46.84 GiB** host;
- expert cache: 4,983 slots / **9.48 GiB**;
- ~462 MiB VRAM free with everything loaded.

This is a useful **Windows + 16-GB + IQ3_S** operational receipt.
It is not a 64-GB-host or 262K receipt and therefore does not move the current ~90% exact-box physical-fit prior.

## UPDATE — Strata #486 gets another similar multi-GPU/vision report

Issue:
https://github.com/Niko1221/Strata/issues/486

A second commenter supplied another 262K, multi-GPU, layer-split, vision-on configuration reporting the same general
problem shape. It is still not the user's one-GPU / vision-off topology.

No prior movement. Keep the late-allocation / real-cold-prefill gate.

## NEW — TensorFold #247: INT8 KV helps Qwen3.8-27B CUDA increasingly with depth

PR:
https://github.com/ashhart/TensorFold/pull/247

Created **2026-10-02 14:15:35 UTC**.

This is the 27B CUDA lane, not Flash-Next Strata.

On one DGX Spark, `--kv-dtype int8` reportedly changes drafted-round time:
- ~90K: about **-6 to -7%**;
- ~180K: about **-9 to -10%**;
- ~242.5K: about **-13%**.

Startup estimate at 262,144:
- MLX 4-bit checkpoint: **37.39 -> 30.38 GiB**;
- NVFP4/FP8 mixed: **43.60 -> 36.59 GiB**.

The 100-task quality table changes a few items in both directions and greedy continuations are not bit-identical.
Therefore this is performance/capacity evidence for a specific TensorFold INT8 scheme, not a fidelity-equivalence proof
for Strata INT8.

No Project-51 Flash-Next target movement.

## NEW — TensorFold #248: Flash-Next decode-share scheduling fix on CUDA

PR:
https://github.com/ashhart/TensorFold/pull/248

Created **2026-10-02 14:16:36 UTC**.

For Flash-Next NVFP4 on a DGX Spark, `--decode-share` was effectively a no-op because row timing was never calibrated
on the relevant standalone pass. The patch feeds that timing and caps share-sized prefill passes at 512 rows.

Reported effect with a simultaneous prefill:
- decode inter-delta gap: **~1.33 s -> ~76 ms**;
- two 30K requests finish in about the same total wall time;
- outputs unchanged.

This is a responsiveness/scheduling result, not a B1 TG/PP target result.

## NEW — vLLM #59774: specialized native 3-bit KV substantially beats its TurboQuant control on RDNA3

PR:
https://github.com/vllm-project/vllm/pull/59774

Created **2026-10-02 12:31:52 UTC**.

ROCm `ROCM_OCTAVE` is a native 3-4-bit KV backend for head_dim 256 models. On 4x RX 7900 XTX / Qwen3.8-27B the
author compares against an existing TurboQuant K3/V4 control.

At a 380K attention-layer microbench, reported:
- TurboQuant K3/V4 decode: 2,565 us;
- Octave K3/V3 compact: 563 us;
- TurboQuant 4-token verify: 6.65 ms;
- Octave: 0.58 ms.

The author also reports lower NLL drift for some Octave formats at comparable size.

Project-51 interpretation:
**compressed KV capacity is not enough; kernel/data-layout integration can dominate.**
This strengthens, rather than weakens, the decision not to rush a generic TurboQuant port into Strata before stock
K8V4/INT8 measurements.

Do not transfer AMD speed or quality percentages to CUDA/Strata.

## NEW — vLLM #59778: GB10 skinny-GEMM tuning was measured, then closed unmerged

PR:
https://github.com/vllm-project/vllm/pull/59778

Created **2026-10-02 13:34:50 UTC** and closed unmerged.

Qwen3.8-Flash-Next NVFP4 on one GB10:
- B1 MTP3 TPOT: about **-6.7%** in the submitted table;
- gain shrinks rapidly with batch size;
- author says 84% of measured gain was the LM head.

Useful mechanism evidence for sm_121 only; no RTX 5070 Ti target movement.

## NEW — llama.cpp #29856: hybrid recurrent-state reserve fix

PR:
https://github.com/ggml-org/llama.cpp/pull/29856

Created **2026-10-02 14:00:57 UTC**.

Hybrid recurrent states could trigger an unplanned graph reallocation when moved back into place. The patch gathers
the states once into a buffer covered by the worst-case reserve.

Reported:
- bit-exact output;
- no decode-speed change.

This reinforces explicit recurrent-state peak accounting but does not change Strata memory estimates.

## RECOVERED CURRENT / UPDATE — oMLX #3964 canonical-state recovery

PR:
https://github.com/jundot/omlx/pull/3964

Older PR, updated in this window.

It repays SpecPrefill's non-reusable sparse-state debt during idle time by densely rebuilding canonical prefix state
in bounded slices. On one M4 Max / Qwen3.8-27B workload it sharply reduces cumulative foreground work, but the PR
itself calls the result single-run and notes arrival-latency tradeoffs.

Useful for future multi-turn Apple-agent architecture, not a current numerical target change.

## KNOWN / SAME-DAY CURRENT — DASLab IQ3_S

Live DASLab model card still shows the already-known IQ3_S line:
- 3.50 transformer bpw;
- ~54.8 GB transformer;
- ~28.8 GB IQ4_NL PLE;
- ~83.6 GB combined file/table footprint;
- short benchmark task average 93.26.

This is not new in the strict window and is **not** long-agent parity evidence.

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- DASLab / Hugging Face;
- TurboQuant;
- mlx-serve;
- Ishizuki;
- broader Qwen3.8-Flash-Next GitHub results.

No strict-window evidence moves:
- IQ3_S vs IQ3_XXS model preference;
- the ~90% physical-fit prior;
- Windows auto-admission ~85%;
- 8 h / 24 h zero-stall priors ~75% / ~55%;
- current IQ3_S TG/PP centers;
- native262K as production target;
- no-new-GPU / no-128-GB-RAM-before-testing decision;
- protected-K policy;
- stock-Strata-before-custom-TurboQuant order.

No new commit appeared in `TheTom/llama-cpp-turboquant`.
No relevant new Ishizuki item.
No relevant MLX-core change supersedes the batch-shape exactness concern.
No new DASLab long-agent / SWE-style IQ3_S validation appeared in this strict window.
No relevant SGLang strict-window item changes the Qwen3.8 Flash-Next plan.
mlx-serve's M3-Ultra deep-prefill issue remains an open non-NAX optimization gap; no new controlled 26.10.1 A/B was posted.

## Target state

Unchanged:
1. Strata baseline: **v0.1.35**.
2. IQ3_S/native262K physical-fit prior on RTX 5070 Ti 16 GB / 64 GB: **~90%**.
3. Windows auto-admission: **~85%**.
4. 8 h zero-stall soak: **~75%**.
5. 24 h zero-stall soak: **~55%**.
6. Built-in restart/recovery <60 s: **~55%**.
7. Mature IQ3_S TG/PP centers: **unchanged**.
8. Production context target: **262,144 native**.
9. No hardware purchase before exact-box data.
10. oMLX #4206 becomes the active **Apple Flash-Next TurboQuant-QSA watch branch**, not a production target.

## New hard boundary

**2026-10-02 14:24:02 UTC**
