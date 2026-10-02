# Project 51 research watch — 2026-10-02 05:52 ET

Freshness boundary entering: **2026-10-02 04:18:49 UTC**
Cutoff: **2026-10-02 09:52:00 UTC**

## Decision

Mature TG/PP centers are unchanged. This pass changes confidence.

The strongest new fit evidence is Strata #469: IQ3_S at native 262,144 on only 11 GB VRAM, with a real 250K cold prompt. Engine RSS stayed about 52.3-52.9 GiB. Together with Strata v0.1.35's Windows low-RAM fix, the user's RTX 5070 Ti 16 GB / 64 GB physical-fit prior rises to about **90%**.

The strongest negative evidence is Strata #481: repeated permanent deadlocks on a Windows 16-GB Blackwell / 64-GB coding-agent box under long reasoning and heavy prefix reuse. So fit confidence rises while production-soak confidence falls.

## NEW — Strata v0.1.35 baseline

Release: https://github.com/Niko1221/Strata/releases/tag/v0.1.35

Relevant changes:
- fixes Windows low-RAM resident-mode admission after GPU-cache warmup;
- releases file-cache pages before the RAM fit check;
- if all non-GPU experts do not fit, keeps the hottest subset resident instead of falling straight to SSD-backed mapping;
- release gate reports same fixed-cache answers as 0.1.34 and no meaningful speed change.

Project-51 baseline becomes **v0.1.35**.

## NEW — IQ3_S native262K on RTX 2080 Ti 11 GB

Strata #469:
https://github.com/Niko1221/Strata/pull/469

Configuration:
- RTX 2080 Ti 11 GB;
- Threadripper 3960X, AVX2;
- 128 GB DDR4-2133 host;
- IQ3_S;
- native max-context 262,144;
- INT8 KV with 32,768 resident cells/layer;
- MTP spec4;
- 3.25 GiB expert cache.

Measured:
- 4K: 496.9 PP / 39.6 TG;
- 32K: 636.9 PP / 38.0 TG;
- 128K: 566.2 PP / 34.1 TG;
- one 250K cold run: **466.6 PP / 31.8 TG**;
- 250,463-token follow-up reused 249,993 tokens, TTFT **4.55 s**, decode 34.6 TG;
- engine RSS about **52.3-52.9 GiB**;
- GPU use 10,525 MiB;
- no active swap-in/out during prompt reads.

Limitation: the host had 128 GB, so this is not the exact 64-GB proof. But the engine itself fits below 53 GiB RSS on a GPU with 5 GB less VRAM than the target 5070 Ti. This materially strengthens exact-box fit.

Planning change: **IQ3_S + native262K physical-fit/admission prior on 5070-Ti-16GB / 64-GB host -> about 90%**.

## NEW — MTP draft-vocab headroom lever

Strata #474:
https://github.com/Niko1221/Strata/issues/474

A 12-GB RTX 3060 running IQ3_S at 262K failed MTP startup on the default CJK draft head.

Reported draft-head VRAM:
- CJK 106,299 tokens: ~348 MiB;
- Cyrillic 57,793: ~189 MiB;
- English 40,525: ~133 MiB.

Switching to the English draft vocabulary fixed startup.

For the user's code-heavy lane, if MTP binding is tight, use the English draft vocabulary before reducing context or disabling MTP. Keep the larger vocabulary for multilingual/Korean qualification.

vLLM #59740 independently reports a reduced Flash-Next draft vocabulary as a real speed mechanism on DGX Spark, but its +23.7% BS1 number does not transfer to Strata.

## NEW — BF16 PLE source-fidelity control

Strata #464:
https://github.com/Niko1221/Strata/pull/464

The checkpoint's original BF16 n-gram/PLE table can be streamed directly.

Reported:
- IQ4_NL PLE: ~28.8 GB;
- BF16 PLE: **102.4 GB** on disk;
- prompt-speed delta across 9K-237K within roughly ±2.3%;
- **14.6% of measured routing entries differ** between IQ4_NL and BF16;
- all probed first-window logits differ, mean absolute delta ~0.22, max 1.69;
- tested argmax remained the same.

No quality improvement is claimed or measured. Add BF16 PLE as a **source-of-record control** for AA/agentic testing; keep IQ4_NL as production default unless BF16 produces a meaningful quality gain.

## NEW — adaptive-swap reproducibility race localized

Strata #462/#463:
https://github.com/Niko1221/Strata/pull/462
https://github.com/Niko1221/Strata/pull/463

Adaptive expert copies could be read as resident or non-resident depending on PCIe completion timing, changing CPU-vs-GPU arithmetic and eventually greedy tokens. The proposed wait makes the reported test 5/5 reproducible at under 0.3% cost.

At this cutoff #463 is still open and is not in the v0.1.35 release notes.

Certified Project-51 A/Bs continue to disable adaptive swaps and freeze residency.

## NEW — Windows long-agent deadlock is a production blocker

Strata #481:
https://github.com/Niko1221/Strata/issues/481

Very relevant setup:
- RTX 5060 Ti 16 GB, sm_120;
- Intel i5-14600K, AVX2;
- 64 GB RAM;
- Windows 11;
- Strata 0.1.34;
- 205,824 context, INT8 KV, MTP spec4;
- coding-agent client;
- 34K-85K prompts with heavy prefix reuse;
- long high-reasoning streams.

Reporter observed 4+ permanent engine deadlocks over two days. GPU fell to 0%, all threads blocked, stall watchdog did not fire, and killing the engine did not make the Python server recover without a full service restart.

No matching v0.1.35 fix is identified at this cutoff.

Planning changes:
- 8 h zero-stall soak: **~75%**;
- 24 h zero-stall soak: **~55%**;
- Windows auto-admission: **~85%**;
- built-in restart/recovery under 60 s: **~55%**.

Exact-box soak must include long xhigh/high reasoning, tool loops, cancellation, heavy prefix reuse, and immediate follow-up. Use an external supervisor during early production testing.

## NEW — small agentic IQ3_S receipt

Strata #483:
https://github.com/Niko1221/Strata/pull/483

2x RTX 5060 Ti 16 GB, i9-9900KF, IQ3_S:
- current speed test ~1,108 PP at ~21K and 56-63 TG decode;
- one semver agent task:
  - IQ3_S medium: 55/55 in 797 s;
  - IQ3_S xhigh: 55/55 in 872 s;
  - Qwen3.8-27B Q6 xhigh: 55/55 in 1,824 s.

Useful practical evidence, but n=1 on a ceiling task. No AA/intelligence-prior movement.

## NEW — 1M context remains research-only

Strata #466:
https://github.com/Niko1221/Strata/pull/466

Community IQ3_S/5090/122-GB report reaches a real ~1.048M prompt under YaRN x4 with 5/5 midpoint needles. Project-51 remains **native 262,144**.

## Strict-window negatives

- No new DASLab main quant family or structured long-agent quality table.
- No new TurboQuant development changes the high-GQA decision; symmetric compressed K remains demoted.
- oMLX stable remains 0.7.0.
- TensorFold stable remains 0.6.1.
- No relevant Ishizuki release.

## Target state

Mature TG/PP centers: **unchanged**.

Confidence/state:
1. Strata baseline: **v0.1.35**.
2. IQ3_S/native262K physical-fit prior on 5070-Ti-16GB / 64 GB: **~90%**.
3. Windows auto-admission: **~85%**.
4. 8 h zero-stall soak: **~75%**.
5. 24 h zero-stall soak: **~55%**.
6. Built-in restart/recovery <60 s: **~55%**.
7. BF16 PLE added as source-fidelity control.
8. English draft vocabulary is the first code-lane MTP headroom lever.
9. Production context target remains **262,144 native**.

## New hard boundary

**2026-10-02 09:52:00 UTC**
