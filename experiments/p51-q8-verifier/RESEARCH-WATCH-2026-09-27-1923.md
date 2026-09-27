# Project 51 primary-lane research watch — 2026-09-27 19:23 ET

**Freshness boundary entering this pass:** **2026-09-27 18:28:19 UTC**.  
**User cutoff:** **2026-09-27 23:23:40 UTC**.

This pass preserves the strict boundary. Older/same-day material newly recovered is labeled **RECOVERED CURRENT** rather than NEW.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash-Next: **40 TG sustained at genuinely filled ~128K**
- dual-M1 Flash-Next: **400 realistic cold PP**
- planning confidence for >=40 TG: **~70%**
- single-M1 dense 27B: **25 TG canonical / ~110 native cold PP**
- 5070 Ti + Strata: high-potential experimental Flash lane, **not yet production-qualified**
- Flash quant search: roughly **3.0–3.6 transformer BPW**, with source-like xhigh still requiring the full AA certification suite

This pass materially strengthens the exact-verifier architecture. TensorFold and mlx-serve now independently implement the same core idea: **a verify row must use arithmetic whose bits do not depend on how many sibling rows happen to share the call.**

---

## NEW — mlx-serve #590 ports TensorFold's exact DFlash machinery into a second Apple runtime

Source: https://github.com/ddalcu/mlx-serve/pull/590  
Merged **2026-09-27 22:50:37 UTC**, merge commit eca42620018566d4dd0acc3eab9565685b46dd5b.

The implementation ports/reimplements TensorFold mechanisms in Zig/Metal:
- rowqmv: row-exact **4/6/8-bit** affine matvec / routed-expert / router kernels
- simd_qmm: fixed-order multi-row quantized matmul
- row_attn: fixed-split attention whose result for a row is independent of sibling rows
- keyed_sample: GPU sampling keyed by **absolute token position**
- DFlash2 best-first draft-tree/lattice construction
- GDN multi-row verification with per-token state rounding/commit semantics

The correctness contract is explicit: when exact DFlash mode is active, a drafted verify row must reproduce the one-row serial decoder's result. Seeded sampled requests are also required to give the same text whether the prompt is cold or prefix-cached.

Exactness is not free. mlx-serve deliberately enables the row-exact path for DFlash rather than globally; its notes say forcing the exact path for ordinary native MTP costs roughly **30%**, so serial/MTP retain the stock path.

Verify width remains hardware-specific. On one recorded applegpu_g16s 4-bit Muse fixture, with serial reference **28.2 TG**, the same runtime reports:
- block 16: **0.92x**
- block 8: **1.16x**
- block 7: **1.43x**
- block 6: **1.79x**
- block 5: **1.97x**
- block 4: **1.81x**
- block 3: **1.77x**

At block 5 its diagnostic round profile is approximately target verify **50.2 ms**, assistant **6.2 ms**, draft head **2.9 ms**, append **0.9 ms**, accept **0.2 ms**, scheduler gap **0.01 ms**.

The fixture is **not an M1 receipt**, so none of these multipliers move the Apple7 forecast. The transferable result is the shape of the optimum: wider is not automatically better. DFlash2 tree rounds also get their own block-8 cap; no explicit M1 hardware row has yet been published in this runtime.

**P51 consequence:** before inventing more P69B13 arithmetic, directly audit/cross-diff TensorFold rowqmv/simd_qmm, mlx-serve's ports, Ishizuki's Apple7 few-row kernels and frozen P69B12. Compare split-K/reduction order, row isolation, bf16/fp32 boundaries, quant unpack/dequant order, router exactness, fixed-split attention, GDN commit/rollback and absolute-position sampling.

---

## NEW — TensorFold 0.3.5 makes exact multi-row execution a broader runtime architecture

Primary commits:
- b41a6b6794d6bdbced1d85cae8132a59034b809f — **20:16:15 UTC**
- 4b354d72aac679db2b782a93f25234562d7c528b — **20:36:32 UTC**
- eea15fd877ac86b012001afc4523b31fd1944564 — **21:12:56 UTC**
- a3274f1d9df2ba93d1c523c20c6bc18ea5008865 — **22:55:52 UTC**

Repo: https://github.com/ashhart/TensorFold

TensorFold 0.3.5 can share a target verification round across concurrent MLX requests while requiring each stream's reply to equal its solo run. This reinforces that batching and exactness are compatible when arithmetic/state identity is deliberately designed.

The current M5 lane path now reads affine **2/3/4/5/6/8-bit** projections. For **M1 through M4**, dense Qwen3.8 remains on the row-exact simd_qmm route for **4-bit/group-64**, with windows up to 16 rows and the same decoder for serial and drafted calls.

The Sep-27 Flash prefill commit says its 0.3.5 path is faster than 0.3.4.1 from **1K through 128K** and removes the pause between long-prompt prefill and first decode. The current release recipe deliberately leaves final 0.3.5 decode/prefill numbers **TBD**, so this gets no PP target credit.

Current public TensorFold material separately advertises Flash-Next on **M3 Ultra 256 GB at ~88–92 TG**, with **79 TG without drafts** for its stated short-answer workload. That is current stronger-chip evidence, not strict-window M1 evidence.

0.3.5 also replaces a purely fixed-grid resume policy with tokenizer/chat-template-derived boundaries, including assistant-message starts and the second message boundary for shared system prefixes. Fresh and resumed requests use the same chunk plan.

**P51 consequence:** session-cache identity should encode tokenizer/chat-template/chunk-plan identity. Message-aware checkpoints can reduce follow-up re-prefill without sacrificing exactness only if fresh and resumed execution share the same reachable boundaries.

---

## NEW — Strata v0.1.12 root-causes the original wedge, but the exact 5070 Ti still shows a residual liveness failure

Fix commit: 06438fd6c0c9319f89772bfff56cff201569a824 — **18:53:38 UTC**.  
Setup follow-up: b742ff998704638903461a2d7d6c1e03b8032509 — **19:40:19 UTC**.  
Issues: https://github.com/Niko1221/Strata/issues/29 and https://github.com/Niko1221/Strata/issues/31

The maintainer isolated a race in the **CPU expert pool**. Workers sleep after idle periods; on a large GPU many layers need no CPU expert work, so workers can sleep mid-answer. A late-waking worker could remain counted idle and claim work from the next batch while it was still being published, corrupting completion accounting and deadlocking host/GPU progress.

v0.1.12 ties claims to batch/epoch and adds ordering around published work. It also adds a **120-second no-progress watchdog**: rather than wedging forever, the engine logs its last progress stage, exits, and the server restarts it on the next request.

However, the exact **RTX 5070 Ti 16 GB** reporter caught a stall on 0.1.12 after roughly **45 minutes** of sustained load. The watchdog localized it to **verify window: the CPU experts of layer 9**, restarted the engine, and the benchmark continued. Reporter summary: about one watchdog event in roughly **65 minutes**, with a longer soak still underway.

Therefore P51 status changes from **known hard wedge with no recovery** to **root-caused/mitigated and self-recovering, but residual liveness failure remains**. Do not promote Strata to default/daily-driver until the exact 5070 Ti completes a meaningful zero-watchdog soak.

Linux also had a setup problem: git pull could leave a locally compiled old engine running. b742ff9 now fingerprints engine sources and rebuilds on change.

---

## NEW — SGLang LiLiCorr shows a better way to spend acceptance budget than simply widening verify

Source: https://github.com/sgl-project/sglang/pull/37462  
Merged **2026-09-27 22:36:48 UTC**, commit 78eee88113510d6b0d70f6978739d0845e2fff0f.

LiLiCorr retains top-k candidates per DFlash position, scores transitions with a small two-layer transformer, chooses a coherent lattice path, and leaves target verification unchanged.

On **Qwen3-8B / single H100 80 GB / greedy / FA3 / draft length 15**, LiLiCorr+conv versus head-free DFlash improves output throughput by approximately **+14.6% GSM8K, +12.9% MBPP, +11.1% Math500, +10.5% LiveCodeBench, +9.9% MTBench, +9.1% HumanEval**. Acceptance gains are reported in the **+7.6% to +21.7%** range.

This is H100/8B evidence and receives zero M1 numeric credit.

Two systems lessons matter:
1. backends that publish CPU sequence lengths every speculative block pay a **device-to-host sync worth ~8% throughput** here;
2. forcing the reranker outside the captured draft graph costs **~8.4%** despite identical acceptance, while torch.compile itself is effectively noise around zero.

**P51 consequence:** after verifier-cost work, increasing accepted useful tokens per fixed verify window is a serious alternative to widening S. Keep LiLiCorr-like coherence as a later acceptance-quality lane; it requires a trained sidecar, so it is not the immediate P69B13 experiment.

---

## UPDATE — vLLM hybrid cache grouping puts a measured number on speculative metadata explosion

Source: https://github.com/vllm-project/vllm/issues/58638  
Updated **2026-09-27 21:51 UTC**.

Hybrid targets plus a small draft-model cache bucket can explode independently managed cache groups: Qwen3.5-27B + DFlash **4 -> 70 groups** and Qwen3.6-35B-A3B + DFlash **4 -> 46 groups**.

For Qwen3.6 + DFlash on B300, changing the grouping **46 -> 17** reports **460 -> 733 TG at c=1 (~+54%)** and roughly **+36% at c=32**. A second supported packed layout can reach **5 groups** without the same padding cost.

This is CUDA/B300 and receives no Apple numeric transfer. It does make **cache-group count / metadata-builder count** an explicit P51 speculative cost term beside target verify time.

---

## RECOVERED CURRENT — reduced draft vocabulary can remove much of an MTP head's bandwidth cost without changing target vocabulary

Source: https://github.com/vllm-project/vllm/issues/58578  
Last pre-boundary update: **2026-09-27 18:15:38 UTC**. Missed in the previous watch, so RECOVERED CURRENT.

On Intel Arc Pro B70, Qwen3.8-27B's native MTP proposer shares a target lm_head with **248,320 vocabulary x 5,120 hidden**, roughly **2.54 GB** read for each draft token in that checkpoint.

A **50,521-token draft-only vocabulary** changes measured 3-draft step cost **50.7 -> 40.2 ms** and extra-draft marginal cost **5.5 -> 2.3 ms**. At approximately unchanged acceptance, Qwen3.8-27B reports **59.5 -> 74.6 TG**; Qwen3.6-35B-A3B reports **147.4 -> 189.8 TG**.

The target still verifies/emits over the full vocabulary, so omitted draft tokens reduce acceptance rather than target expressivity.

**P51 consequence:** add a separate **reduced-vocabulary draft head + full protected target head** arm. Test it independently before combining it with draft-head quantization.

---

## Strict-window source scan

From **18:28:19 -> 23:23:40 UTC**:
- **mlx-serve:** exact TensorFold-derived DFlash landed; promoted above.
- **TensorFold:** substantial 0.3.5 work landed; promoted above.
- **Strata:** v0.1.12 race mitigation + watchdog landed, followed by an exact-5070-Ti residual stall; promoted above.
- **SGLang:** LiLiCorr landed; promoted above.
- **vLLM:** hybrid cache-group RFC materially updated; promoted above.
- **oMLX:** no new Qwen runtime commit in-window.
- **Ishizuki:** no new commit after the boundary.
- **MTPLX:** no new commit.
- **upstream Splash:** no new commit.
- **DFlash upstream:** no new commit.
- **llama.cpp:** no qualifying P51 inference commit.
- **DASLab / GSQ-RCO:** no new strict-window quant-quality receipt.
- **DS4:** no new qualifying commit.

### Deferred edge item

oMLX issue **#4040** opened at **23:17:46 UTC**, before this cutoff, but its currently visible body was edited at **23:24:41 UTC**, after the cutoff. To preserve the hard boundary, this watch does not promote its current claims; pick it up next pass as a post-boundary update.

---

## Project 51 actions promoted by this pass

1. **P69B13 starts with cross-implementation kernel archaeology, not a blind new shader:** compare TensorFold, mlx-serve, Ishizuki and P69B12; isolate what exact-row mechanism we are actually missing.
2. **Add row-exact sampled certification:** S=1 serial vs S=2–8 verify, greedy + sampled, same absolute position/seed, cold + prefix-hit, near ties, partial GDN acceptance.
3. **Add a draft-only reduced-vocabulary MTP arm:** target head remains full/source-like; measure head bytes/draft, acceptance, TG and xhigh agent workload.
4. **Instrument speculative cache-group count:** group count, metadata builder calls, host planning, D2H syncs, separate from GPU verify time.
5. **Keep Strata's production gate:** v0.1.12 self-recovers but is not liveness-clean on the exact 5070 Ti.
6. **Message-aware exact resume:** snapshot identity includes tokenizer/chat-template/chunk-plan identity and only reachable committed recurrent boundaries.
7. **Future acceptance-quality lane:** improve coherent accepted tokens per target round before simply widening S.

---

## Canonical planning effect

**Targets unchanged.**

The important movement is implementation confidence, not the forecast. Exact row-invariant verification now has multiple independent implementations, but there is still no new physical **dual-M1/TB4 Flash-Next @ ~128K** receipt and no exact M1 Flash-Next result sufficient to move the 40-TG distribution. Strata's exact-5070-Ti lane is safer operationally but still fails the production-liveness gate.

Keep **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence** and **single-M1 dense 25 TG / ~110 PP**.

## New hard boundary

**2026-09-27 23:23:40 UTC**
