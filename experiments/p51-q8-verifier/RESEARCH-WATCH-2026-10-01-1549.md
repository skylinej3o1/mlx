# Project 51 research watch — 2026-10-01 15:49 ET

Freshness boundary entering: **2026-10-01 14:26:16 UTC**  
Cutoff: **2026-10-01 19:49:37 UTC**

## Decision

**No canonical numerical target movement.**

The main planning change is qualitative and important:

- Do **not** make symmetric Turbo3 K+V the default Strata port target for Flash-Next.
- First prove **IQ3_S + native 262,144 + stock Strata memory tiers** on the exact RTX 5070 Ti 16 GB / 64 GB host.
- If a custom TurboQuant port is still useful, start with **INT8 K + Turbo3 V**, keeping the MTP/draft KV INT8 initially.
- Treat symmetric Turbo3 K+V as an experimental quality arm only, because current TurboQuant source automatically upgrades K to Q8 on high-GQA models and Flash-Next is 12:1 GQA.
- The new 64-GB IQ3_S evidence strengthens the native-262K feasibility case, but it is on a 32-GB GPU and therefore does not promote an exact-box fit or speed number for the user's 16-GB 5070 Ti.

Qualification additions:
- deterministic KV/quant A/Bs must use a **fixed expert cache**, disable adaptive swaps, and preferably start from a fresh engine/server state;
- on Windows, GPU admission must include the **desktop/WDDM budget**, not just cuda/hip free-memory reporting;
- for 64-GB resident-budget experiments, leave explicit RAM margin rather than relying on clamp-at-the-limit behavior;
- record MTP prompt-path behavior separately when KV streaming/ring mode is active;
- v0.1.32 Windows text inference is usable on non-AVX512 CPUs, but its released vision helper has a confirmed AVX-512 startup bug, so Project 51 stays **vision off** for the first qualification.

## NEW — Strata v0.1.32 is the current baseline

Release v0.1.32 published at 17:28:36 UTC:
https://github.com/Niko1221/Strata/releases/tag/v0.1.32

Relevant release changes:
- multi-GPU prompt-path refill/borrowing was reworked after the 0.1.30/0.1.31 short-prompt regression;
- default Q2/IQ3_S decode is reported **+1.5% to +3.8%** versus 0.1.31 at equal expert slots with the same output in the maintainer's validation;
- AMD router work is reported +12% on R9700 and +4% on RX 9070 XT with bit-identical output;
- several prompt-path and cache correctness fixes landed.

Project-51 effect: **v0.1.32 replaces v0.1.31 as the text-engine baseline**, subject to exact-box requalification rather than inheriting its percentages.

### Immediate release caveat — Windows vision helper is broken on non-AVX512 CPUs

Issues #411 / #412 / #419 were filed after the release:
https://github.com/Niko1221/Strata/issues/419

#419 includes WinDbg evidence of an unconditional EVEX/ZMM instruction in the released strata-vision.exe on a non-AVX512 CPU. The main strata.exe text engine falls back correctly and remains usable.

Project-51 effect: initial 5070-Ti qualification remains **text-only / vision off**. Do not treat v0.1.32's vision path as certified on the user's Ultra 7 265F.

## NEW — direct evidence that Strata's 128K IQ3_S setup cap can be conservative on 64 GB

Issue #406, created 17:13 UTC:
https://github.com/Niko1221/Strata/issues/406

A Linux user with:
- IQ3_S;
- **64 GB RAM**;
- **32 GB VRAM**;

reports that setup forced a requested 256K context down to 128K, but a manual run-script change served the full native ~256K window with **>6 GB RAM still free** at full context. The reporter says the 256K window cost about 1.8 GB more RAM than 128K and saw 70%+ expert-cache hit rate.

Classification: **NEW feasibility evidence**.

This directly supports the conclusion that setup's conservative context gate is not a physical proof that 64-GB IQ3_S cannot run native context. It does **not** prove the user's 16-GB 5070 Ti topology, because the reporter had twice the VRAM.

## NEW — IQ3_S is being used as a real coding-agent backend on consumer GPUs

Issue #392, created 15:50 UTC:
https://github.com/Niko1221/Strata/issues/392

Hardware:
- i9-9900KF;
- 128 GB DDR4-3000;
- 2 x RTX 5060 Ti 16 GB, PCIe Gen3 x8/x8;
- Windows 10;
- Strata 0.1.30;
- IQ3_S + MTP.

Measured:
- 1 GPU short decode **38.7-41.5 TG**;
- 1 GPU after 23.8K prompt **33.6-39.8 TG**;
- 1 GPU cold 23.8K prefill **860 PP**;
- 2 GPU short decode **50.5-60.5 TG**;
- 2 GPU after 23.8K **46.3-58.2 TG**;
- 2 GPU cold 23.8K prefill **~996 PP**.

Three Forge coding-agent sessions totaled about 3 hours / 486 tool calls. Context passed 86K; decode stayed around 47 TG past 75K on the two-card configuration. A separate Claude reviewer checked/finished changes before commit, so this is operational evidence, not a clean autonomous-quality benchmark.

Classification: **NEW real-agent / consumer-GPU evidence**. Useful for the IQ3_S usability prior, not an exact 5070-Ti target transfer.

## NEW / UPDATED — Strata #378 elastic KV shows the size/speed lever, but excludes our low-RAM topology

PR #378, created 14:31 UTC and updated inside the window:
https://github.com/Niko1221/Strata/pull/378

At 262,144 Strata reports **3.35 GiB** for all-INT8 KV including the drafter. --kv-grow reserves the full virtual address range but physically maps KV as context grows, lending unused VRAM to the expert cache.

RTX 5090 / IQ2_XS:
- stock cache 15,119-15,207 slots;
- kv-grow 17,300-17,503;
- short chat 161-163 -> 164-167 TG.

On an emulated 16-GB budget:
- cache 3,396 -> 5,719 slots;
- short chat 100 -> 115 TG;
- 32K prompt 7.44 -> 6.36 s.

Critical restriction: it currently requires **one GPU, full KV in VRAM, and every expert in RAM — not the low-RAM tier**.

Classification: **NEW capacity/performance mechanism**. It reinforces that KV savings primarily buy expert-cache capacity/speed, but does not solve the user's 64-GB low-RAM configuration today.

## NEW — Windows desktop/WDDM memory accounting can dominate apparent expert-cache capacity

PR #380, created 14:35 UTC:
https://github.com/Niko1221/Strata/pull/380

On an RX 6800 16 GB that drives the Windows desktop, HIP's free-memory figure did not subtract VRAM held by the desktop/other programs. Strata therefore overfilled the process budget and WDDM moved engine memory into shared system memory.

With DXGI budget-aware sizing:
- cache size actually became smaller;
- shared GPU memory spill disappeared;
- median decode **30.5 -> 41.4 TG (+36%)** in that exact test.

Classification: **NEW exact Windows admission evidence**.

Do not transfer the percentage to CUDA/5070 Ti. Durable rule: because the user's 265F has no iGPU, **desktop VRAM and WDDM budget are part of the 5070-Ti qualification**. More nominal expert slots are not a win if they cause migration.

## NEW — resident-budget clamping has a race at the RAM safety boundary

Issue #403, created 16:44 UTC:
https://github.com/Niko1221/Strata/issues/403

On Windows / RTX 5090 / 64 GB RAM, --resident-budget-gib 40 was clamped to the available-memory limit, filled, then rejected when a second available-memory reading dropped slightly. An explicit smaller budget (26 GiB in that case) worked.

Classification: **NEW low-RAM admission bug**.

Project-51 rule: prefer --resident-experts when the exact complement fits; when using a bounded budget, leave explicit margin and do not depend on clamp-at-the-limit behavior.

## NEW — deterministic A/B needs more than STRATA_IQ_MT_MIN=1

Issue #410, created 18:11 UTC:
https://github.com/Niko1221/Strata/issues/410

RTX 5090 / IQ2_XS / v0.1.32:
- fresh CLI process, fixed tokens: 1 output across 5 runs;
- server defaults: identical short requests produced 2 distinct outputs in 5;
- prompt cache off: 3/6;
- prompt cache off + **--adapt-swaps 0**: short prompt became 1/6;
- medium prompts still showed residual state-dependent variation under some settings.

The adaptive expert tier moves work between CPU/GPU, and those paths round differently. That can change tokens even at temperature 0.

Classification: **NEW measurement-method evidence**.

Project-51 fidelity tests must freeze expert residency/adaptation and reset persistent server state. STRATA_IQ_MT_MIN=1 alone is not a sufficient deterministic-A/B guarantee.

## RECOVERED OLDER — TurboQuant itself says high-GQA symmetric Turbo K is unsafe

Current TurboQuant branch source:
https://github.com/TheTom/llama-cpp-turboquant/blob/bcb85fc3ae85efa0f5f392c6c880dfc524923860/src/llama-kv-cache.cpp

The source resolves symmetric Turbo K+V to **Q8 K** when:
- K is Turbo2/3/4;
- K and V requested types are the same;
- GQA ratio is **>= 6**;
- the auto-asymmetric safeguard is not disabled.

Its source comment cites Qwen2.5 at 7:1 where Turbo3-K perplexity was catastrophic, while 4:1 Mistral was workable.

PR #197 also reports that **Q8 K + Turbo4 V** reduced mean KLD by ~26% versus symmetric Turbo4, and labels K as the dominant KLD side:
https://github.com/TheTom/llama-cpp-turboquant/pull/197

Flash-Next's Strata QSA shape is 24 query heads / 2 KV heads = **12:1**.

Classification: **RECOVERED OLDER, materially planning-changing**.

Project-51 change:
- symmetric Turbo3 K+V is no longer the default production proposal;
- first custom arm, if needed, becomes **INT8 K + Turbo3 V**;
- symmetric Turbo3 remains a research arm requiring direct Flash-Next KL/logit/agent validation.

## RECOVERED CURRENT — Strata's fast prompt path favors keeping K INT8

Current Strata qsa_prompt_attn_batch rejects the optimized path when a q4 K pool is present, while K8V4 composes INT8 K with Q4 V and remains eligible for the optimized K path. Verify batching also has a !kv_q4 gate.

Classification: **RECOVERED CURRENT source-code mechanism**.

Combined with TurboQuant's high-GQA safeguard, this is a second independent reason to test V-only Turbo compression before a compressed-K production format.

## NEW — AMD MTP prompt-ring hang and per-group workaround

PR #382, created 14:51 UTC:
https://github.com/Niko1221/Strata/pull/382

R9700 / 30 GB RAM / full IQ3_XXS / 131K / INT8 KV streaming + MTP:
- released 0.1.31 hung during MTP prompt prefill;
- forcing the older per-group loop ran **30 rounds / 0 hangs**;
- branch default also ran **30 rounds / 0 hangs**;
- warm 32K PP ~1,131, 7K ~1,153, code decode 72-80 TG.

Classification: **NEW correctness evidence**. MTP prompt processing with ring/streamed KV remains a separate qualification path.

## NEW — TensorFold #191 removes a routed-expert prompt-grouping bottleneck

PR #191, created 14:45 UTC:
https://github.com/ashhart/TensorFold/pull/191

One GB10, Flash-Next EXL3 3.05 bpw:
- grouping at 1,024/2,048 rows: 2.53/5.07 ms -> 0.083/0.16 ms;
- routed() 1,024 rows: 18.71 -> 16.35 ms;
- 8K prompt: 10.27 -> 9.41 s;
- 32K prompt: 41.58 -> 38.64/37.86 s;
- downstream output is reported bit-identical.

Classification: **NEW prompt-kernel mechanism evidence**, no direct 5070-Ti target credit.

## NEW — llama.cpp Flash-Next MTP still has model-specific correctness churn

Issue #29811, created 16:19 UTC and updated at 19:49:28 UTC:
https://github.com/ggml-org/llama.cpp/issues/29811

A Qwen3.8-Flash-Next + MTP startup assert on HIP/R9700 is traced to building k-pool inputs for an MTP block that does not use the QSA pool. The reporter's conditional fix gets through warmup.

Classification: **NEW Flash/MTP correctness evidence**. Mainline MTP availability is not the same as architecture-path maturity; keep exact target runtime validation.

PR #29807, updated inside the window, removes redundant recurrent-state copies after SSM_SCAN and reports a **3.5% MTP-on** speed gain on a different recurrent model, with no MTP-off change. Mechanism only.

## NEW — Strata DGX Spark support gives another full-engine hybrid receipt

PR #409, created 18:08 UTC:
https://github.com/Niko1221/Strata/pull/409

Experimental aarch64 / DGX Spark / IQ2_XS, 128K INT8 KV, all experts in the unified-memory GPU cache:
- prefill ~928-1,515 PP across tested prompt/depth combinations;
- decode ~54.9-62.0 TG;
- MTP acceptance ~75-83%.

Classification: **NEW Spark software-maturity evidence**, not a Project-51 purchase or target signal.

## NEW — additional Strata prompt/cache observations

PR #407 adaptive-tier tuning:
- on RTX 5090 / UD-Q4_K_XL, misses -31%, CPU expert time -19%, PCIe traffic -22%;
- overall round time did **not** measurably improve in the primary test.

Durable lesson: hit-rate/miss-rate improvements are not themselves TG improvements.

PR #413:
- DeltaNet recurrence kernel 1.44x and output norm 1.52x on RTX 4080 SUPER;
- only about **+2% end-to-end prefill**.
Again, optimize whole-request time, not one kernel percentage.

PR #416, RTX 5060 Ti 16 GB + 64 GB RAM + AVX2:
- an IQ4_XS model with 60.94 GiB of routed experts ran 37.5-39 TG on its best mmap path;
- an IQ3_S arena reference was 51.5 TG;
- raising that test's context to 220K cost 2.2%.
The IQ3_S reference is not documented as a native-262K exact run, so it is **supporting topology evidence only**, not a new target anchor.

## NEW — oMLX cache/telemetry cautions

Issue #4175:
- on an M4 Max 36 GB / Qwen3.8-27B 4-bit / ~82.5K prefix, enabling a 4-GB hot cache made prefix reconstruction **1.8-7.2 s** versus ~99 ms with hot cache off.
- suspected memory-enforcer interaction is not yet proven.

Project-51 Apple rule: separately benchmark lookup and reconstruction under real memory pressure; a nominal RAM hot tier can be slower than SSD-backed reconstruction.

Issue #4172 reports intermittent missing/null usage telemetry on long qwen4_exp requests. Archive raw timing logs and do not let missing API usage fields silently enter benchmark aggregates.

## Secondary-lane notes

- Strata #377 fixes Windows-HIP PCIe probe timing; exact RX 6800 x16 result is ~27.2 GB/s. No speed change on that x16 card because pcie_frac stays 0.55.
- llama.cpp #29820 finds an R9700 MMVQ/MMQ crossover where 5-8-token passes improve materially by lowering the threshold. RDNA4-only evidence; no RX6800/5070 target transfer.
- SGLang #42074 reports a ~5% DeepSeek-V4-Pro single-stream regression after a specific GB300 optimization commit. DS4 implementation maturity remains volatile; no P51 DS4 target move.
- vLLM #59642 reports 0% Flash-Next MTP acceptance in a disaggregated prefill/decode setup. Treat cross-worker state handoff as a separate MTP correctness gate.
- vLLM #59671 was opened and closed inside the window because its int4-K quality claim was emulator-only and not confirmed on a real GPU. Do not use it as evidence for Project-51 KV quality.

## Community / broad-web scan

Recovered current community data:
- a 5070 Ti **laptop 12 GB** + 64 GB DDR5 user reports IQ3_XXS around **51 TG at ~43K depth** and **~1,500 PP at 32K** on Strata. This is a self-report on a laptop GPU, not the user's desktop 5070 Ti or IQ3_S.
- community impressions of IQ3_XXS/IQ3_S intelligence are mixed and anecdotal. No new structured agentic/AA-class quality evaluation appeared in this strict window.

No quality-prior movement from anecdotes.

## Strict-window negative scan

- DASLab Flash-Next GSQ-RCO repository shows no new strict-window checkpoint or quality table; the collection remains the same four main GGUF sizes plus the separate Coder variant.
- No new strict-window TurboQuant PR/issue materially changes the recovered high-GQA finding above.
- No Project-51-relevant Ishizuki release/update found.
- No Project-51-relevant MoEspresso or mlx-serve release found in the broad search.
- oMLX stable remains **0.7.0**.
- TensorFold stable remains **0.6.0**.

## Target state

**Canonical numerical targets unchanged.**

Planning state changes:
1. v0.1.32 becomes the Strata text baseline.
2. IQ3_S + native262K gets a stock-runtime qualification before any TurboQuant port.
3. First custom Turbo arm, if needed: INT8 K + Turbo3 V; MTP KV stays INT8 initially.
4. Symmetric Turbo3 K+V is experimental only.
5. 64-GB native-context feasibility is stronger, but exact single-5070-Ti/64-GB IQ3_S evidence is still required.
6. Deterministic A/B requires fixed residency, adaptive swaps off, and controlled server state.
7. Vision stays off on the current v0.1.32 Windows prebuilt until the AVX-512 helper regression is fixed.

## New hard boundary

**2026-10-01 19:49:37 UTC**
