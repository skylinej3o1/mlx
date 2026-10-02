# Project 51 research watch — 2026-10-02 00:18 ET

Freshness boundary entering: **2026-10-01 19:49:37 UTC**  
Cutoff: **2026-10-02 04:18:49 UTC**

## Decision

**No canonical numerical target movement.**

This window materially strengthens the RTX 5070 Ti / Strata execution case and changes the current runtime baseline:

- **Strata v0.1.34** is now the baseline. v0.1.33 removed the forced 128K setup cap for a user-selected 262,144 context on 64-GB PCs and fixed the v0.1.32 Windows vision build; v0.1.34 adds the MMQ fallback and request-cancellation fixes while retaining answer parity with v0.1.33 in the maintainer gate.
- New PRs #439/#452/#453 provide **exact RTX 5070 Ti 16-GB physical measurements** on a deliberately weak host: PCIe 3.0 x16 and DDR4-2133. They anchor the weak-host prompt path around roughly 1.6-1.9K PP at 8K-32K depending on the independent optimization arm.
- These receipts do **not** lower the canonical 3,000 / 2,900 / 2,750 / 2,500 IQ3_XXS PP planning centers. Older exact-card measurements already reach about 3.0K around 60K and 2,668 PP at 257K on a faster host. The new data instead confirms that **host PCIe/RAM bandwidth and prompt-path implementation are first-order variables**.
- Strata #440 provides a new **IQ3_S full-native-window** receipt: real 261,669-261,670-token prompts on one RTX 5090, with 9/9 needle retrieval across 32K/128K/256K.
- The active custom KV plan remains **INT8/Q8 K + Turbo-compressed V**, not symmetric Turbo3 K+V. The old K6/V4 candidate ladder in TARGETS is now historical/superseded.
- TensorFold stable advances to **0.6.1**. MLX #4609 adds an Apple qualification hazard: wired memory can be reclaimed within seconds of GPU idle, causing a large first-request penalty unless residency is renewed.

## NEW — Strata v0.1.33 and v0.1.34 supersede v0.1.32

v0.1.33 published 2026-10-01 21:16:13 UTC:
https://github.com/Niko1221/Strata/releases/tag/v0.1.33

v0.1.34 published 2026-10-02 01:21:56 UTC:
https://github.com/Niko1221/Strata/releases/tag/v0.1.34

### v0.1.33: user-selected full context is no longer forcibly capped

Directly relevant changes:
- setup still recommends 128K for IQ3_XXS / IQ3_S on a 64-GB PC, but if the user explicitly chooses 262,144 it now keeps that choice and warns about RAM risk instead of silently forcing 128K;
- low-RAM mode no longer counts context against the setup RAM heuristic;
- resident-budget clamping is hardened so an oversized budget can be lowered with margin instead of failing the second safety check;
- the v0.1.32 Windows vision helper regression is fixed by returning to a portable AVX2/no-OpenMP build.

Project-51 effect: **the exact-box stock experiment no longer requires manually editing the generated run script to request native 262K**.

### v0.1.34: current baseline

Relevant fixes:
- #420: if llama.cpp MMQ cannot find a tile, the prompt path falls back instead of aborting;
- #430/#431: disconnected clients cancel within about one second rather than continuing a long generation/prefill while blocking the next request;
- #410 follow-up: release notes confirm byte-identical server repeats also needed **--pcie-frac 0** in the maintainer reproduction, in addition to the previously recorded prompt-cache/adaptive controls.

Maintainer release gates report the same answers as v0.1.33 on Q2_0/IQ3_XXS/IQ3_S/Coder at fixed cache, and no meaningful speed change.

Classification: **NEW baseline advancement**.

Project-51 deterministic A/B rule is now:
- fixed expert cache/residency;
- --prompt-cache 0;
- --adapt-swaps 0;
- --pcie-frac 0;
- STRATA_IQ_MT_MIN=1;
- fresh process/server state where persistent-state effects are under test.

## NEW — exact RTX 5070 Ti 16-GB prompt-path receipts on a weak host

Three strict-window Strata PRs use the same physical box:

- RTX **5070 Ti 16 GB**;
- PCIe **3.0 x16**;
- Ryzen 9 5900XT;
- **DDR4-2133**;
- Windows 11 / CUDA 13.0;
- Qwen3.8-Flash-Next **IQ3_XXS**.

This host side is materially weaker than the user's Ultra 7 + DDR5 setup, so the measurements are a conservative host-bandwidth anchor rather than a target-machine prediction.

### Strata #439 — grouped native expert gathers, bit-identical

https://github.com/Niko1221/Strata/pull/439

At about 30K prompt:
- one gather launch per expert: about **1,633 PP**;
- grouped gather: about **1,702 PP**;
- **+4.3%**;
- final residual dumps and greedy tokens are reported byte-identical across the tested prompt ladder.

Short prompts below about 4K do not move because PCIe expert copies dominate.

Classification: **NEW exact-GPU / exactness-preserving prompt mechanism**.

### Strata #452 — Q4_0 KV prompt attention on tensor cores

https://github.com/Niko1221/Strata/pull/452

Configuration:
- Q4_0 KV with 32K resident cells;
- 4,560 expert slots;
- standard 8,192-token prompt chunks;
- display off.

Prompt A/B:
- about 8K: mean roughly **1,595 -> 1,888 PP**;
- about 16K: roughly **1,578 -> 1,888 PP**;
- about 30K: roughly **1,585 -> 1,901 PP**;
- gain **about 18.5-19.9%**.

Kernel-level Q4 attention is about 3.8x faster than the prior per-query path in the provided microbench.

Quality boundary:
- 15/15 needles pass on both old/new paths at 8K/16K/32K;
- greedy continuations can diverge after a few tokens because the tensor-core path changes FP32-level arithmetic.

Classification: **NEW exact-GPU performance mechanism / non-bitwise**. Useful Q4 capacity path, not a source-fidelity control.

### Strata #453 — streamed MTP draft KV gets the batched prompt path

https://github.com/Niko1221/Strata/pull/453

Same 5070-Ti host, Q4 streamed KV, MTP spec4.

Prefill:
- 8,128 tokens: roughly **1,653 -> 1,730 PP**;
- 15,547: roughly **1,667 -> 1,744 PP**;
- 31,649: roughly **1,682 -> 1,762 PP**;
- consistent **+4.6-4.7%**.

The old drafter prompt pass drops from hundreds of milliseconds to tens of milliseconds.

Decode samples after 8K/16K prompts are roughly **46.6-60.1 TG**, with draft acceptance about **61-68%**.

Exactness caveat: the batched drafter pass rounds differently; target continuations can diverge because verifier arithmetic depends on draft-window width. This is a speed path, not a byte-identical path.

Classification: **NEW exact-GPU streamed-KV/MTP evidence**.

### Target interpretation

Do **not** add #439 + #452 + #453 percentages mechanically: they were not measured as one combined arm.

Do **not** downgrade the canonical IQ3_XXS PP ladder from these weak-host numbers. Earlier exact-card receipts remain:
- about 3,000 PP around 60K;
- 2,668 PP at a real 257,466-token cold prompt.

The new receipts instead prove that:
1. same-GPU PP can vary by nearly 2x with host/link and prompt-path choices;
2. 1.6-1.9K is a credible **weak-host floor region** for current v0.1.34/Q4-streaming experiments;
3. the user's DDR5/newer-platform box still needs its own exact ladder.

## NEW — full-native IQ3_S receipt at the edge of 262K

Strata PR #440:
https://github.com/Niko1221/Strata/pull/440

Hardware:
- RTX 5090 32 GB;
- Ryzen 9 9950X3D;
- 96 GB RAM;
- Windows 11;
- Strata 0.1.33;
- DASLab GSQ-RCO **IQ3_S**;
- native max-context 262,144;
- INT8 KV with 65,536 resident cells;
- 12,439 expert slots / 23.61 GiB expert cache.

Measured:
- prefill 1K/4K/32K/128K: **999 / 2,439 / 5,045 / 6,004 PP** with larger 32K prompt chunks;
- decode: **144 / 149 / 142 / 125 TG**;
- MTP acceptance **75-76%**;
- needle bench: **9/9** at 32K/128K/256K and depths 10/50/90;
- the 256K cases are **261,669-261,670 actual prompt tokens**.

Classification: **NEW full-window IQ3_S runtime/semantic evidence**.

This is the strongest public Strata IQ3_S native-window receipt in the watch chain. It strengthens the IQ3_S/full-context hypothesis, but the 32-GB GPU + 96-GB host means it does not resolve the user's **16-GB GPU + 64-GB host admission**.

## NEW — long-context peak memory includes transient QSA/indexer scratch

llama.cpp PR #29825:
https://github.com/ggml-org/llama.cpp/pull/29825

Qwen4Exp indexer score construction is changed to score one head at a time and reuse/in-place the relu path.

Reported CUDA compute-buffer reduction:
- 131K, ub2048: **3.0 -> 1.5 GiB**;
- 131K, ub4096: **6.1 -> 3.0 GiB**;
- 262K, ub4096: **11.7 -> 5.6 GiB**.

Reported logits are bit-exact; top-k scores can differ only at FP32 rounding level from the changed reduction order; PP/TG unchanged.

Classification: **NEW long-context temporary-memory mechanism**.

This reinforces a Project-51 distinction: **context fit is not just model+KV bytes; temporary QSA/indexer buffers at large prompt chunks can dominate peak VRAM.** Strata's own prompt path must measure peak scratch, not only steady KV/expert residency.

llama.cpp PR #29827 separately shows a generic quantized-KV FA conversion buffer can erase a meaningful fraction of KV VRAM savings and can be bounded to a fixed cap. This is not Strata's implementation, but it reinforces the same accounting rule.

## NEW — TensorFold 0.6.1 is stable

TensorFold v0.6.1 published 2026-10-01 20:19:24 UTC:
https://github.com/ashhart/TensorFold/releases/tag/v0.6.1

Relevant Flash signals:
- on an 80-core M3 Ultra, Flash-Next one-stream long-context code/chat improves up to roughly **9.6-10.2%** at 64K-128K while preserving reported tokens;
- CUDA Flash-Next adds shared system-prefix copying into new streams and fork/resume improvements;
- the release is the new stable TensorFold baseline.

No exact M1-Max or dual-M1/TB4 receipt, so **no Apple target movement**.

### TensorFold #212 — EXL3 prompt-expert kernel

https://github.com/ashhart/TensorFold/pull/212

On one GB10 / Flash-Next EXL3:
- 4.05 bpw 24,576 prompt: **35.69 -> 13.63 s (-62%)**;
- 3.05 bpw 24,576: **32.73 -> 15.66 s (-52%)**;
- about **1,800 PP** at 24K on the 4.05-bpw arm;
- same-load token/hash tests are reported identical.

Classification: **NEW CUDA prompt-kernel mechanism**, not DASLab/Strata target credit.

### TensorFold #213 — Mac + CUDA split exists for Qwen3.8-27B

https://github.com/ashhart/TensorFold/pull/213

A Mac + CUDA machine can now hold separate layer ranges of one model with residual-row transport. Current wired family is dense Qwen3.8-27B, not Flash-Next; single-stream splitting is described as a capacity feature.

Classification: **NEW future topology option** for the user's mixed hardware, not a Project-51 Flash target path yet.

## NEW — MLX wired-memory residency can evaporate after idle

MLX issue #4609, created 2026-10-02 02:19 UTC:
https://github.com/ml-explore/mlx/issues/4609

Reporter measurements on MLX 0.32.3 show:
- after wiring about 8.1 GiB, 12 seconds idle can drop wired residency to about 3.2 GiB;
- first compute after idle rises from about 60 ms warm to **about 342 ms**;
- a tiny GPU operation every 1 second keeps most memory resident and the first compute around 69 ms;
- every 3 seconds was too sparse in that test.

The reporter attributes this to a standing residency request not being renewed and notes llama.cpp solved a similar macOS behavior with a residency heartbeat.

Classification: **NEW Apple warm-residency/TTFT hazard**.

Project-51 Apple qualification now needs:
- warm request;
- idle 2s / 10s / 60s;
- next-request TTFT and resident-memory measurement;
- heartbeat-on/off A/B if the runtime exposes one.

Do not count a cached/resident agent as warm merely because its Python/MLX objects still exist.

## RECOVERED OLDER — exact 5070-Ti lanes at 141K-145K were already public

Strata issue #127, created Sep 29:
https://github.com/Niko1221/Strata/issues/127

Three independent RTX 5070 Ti 16-GB lanes running IQ3_XXS with 262K configured context report:
- **78.8 / 78.4 / 80.1 TG**;
- each lane completed a concurrent request with roughly **141K-145K real input**.

Classification: **RECOVERED OLDER**, not NEW.

This is strong exact-GPU filled-context decode support, but the shared host arena/multi-lane machine is not the user's 64-GB single-lane host, so it does not move the canonical target.

## Secondary-lane notes

- Strata #445 finds a discrete large-arena pinning cliff on a multi-P100 Linux IQ3_S setup: capping the pin around 40 GiB restored prompt speed. General lesson: more host pinning is not automatically faster; qualify the pin budget on the exact topology.
- Strata #448 shows a small second GPU in a layer split can force prompt chunks down to 512 and make prompt reads about 6.2x slower while decode stays similar. A helper-GPU expert tier performed better in that topology. Do not assume adding a small GPU improves an agent workload.
- Strata #438 reports a severe CJK failure on the extreme IQ1_M Coder quant while English remains clean. It does not transfer to DASLab IQ3_S/XXS, but it reinforces multilingual greedy/agent certification for every aggressive quant.
- vLLM #59724 reports another architecture-specific MTP path with 0% acceptance on SM120/GLM-5.3. This is not Qwen3.8-Flash-Next, but it reinforces backend-specific speculative-validation requirements.
- SGLang #42146 finds a DeepSeek-V4 SM120 indexer planner interaction that costs roughly 3.3-3.8 GiB peak memory around 128K with no output benefit. This reinforces the long-context scratch-accounting rule for the DS4 lane.

## Strict-window negative scan

- DASLab GSQ-RCO Flash-Next shows no new strict-window main quant family or structured quality table.
- TurboQuant has no new strict-window PR/issue that changes the high-GQA conclusion; **symmetric Turbo K remains demoted**.
- oMLX stable remains **0.7.0**.
- TensorFold stable advances **0.6.0 -> 0.6.1**.
- No Project-51-relevant Ishizuki release found.
- No new structured AA/agentic quality suite appeared for DASLab IQ3_S/XXS in this strict window.

## Target state

**Canonical numerical targets unchanged.**

Planning state after this pass:
1. **Strata v0.1.34** is the exact-box baseline.
2. Request native 262,144 directly; setup now preserves the user's explicit choice.
3. First qualification remains **IQ3_S stock controls before custom TurboQuant**.
4. Built-in controls: INT8 K/V and K8V4; Q4 streamed KV is a capacity/performance arm, not a fidelity control.
5. If custom TurboQuant is still needed, protect K first: **Q8/INT8 K + Turbo V**. Use Turbo4-V as a parity bridge if useful, then Turbo3-V as the capacity candidate. Symmetric compressed K+V is experimental only.
6. Exact 5070-Ti weak-host prompt evidence is now public, but it does not replace the user's own DDR5/new-platform ladder.
7. IQ3_S has a real 261.67K Strata receipt; exact **16-GB/64-GB IQ3_S** remains the missing admission proof.
8. Apple qualification gains an idle-residency/heartbeat TTFT gate.

## New hard boundary

**2026-10-02 04:18:49 UTC**
