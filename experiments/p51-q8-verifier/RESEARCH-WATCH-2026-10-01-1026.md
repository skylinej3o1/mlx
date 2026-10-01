# Project 51 research watch — 2026-10-01 10:26 ET

Freshness boundary entering: **2026-10-01 11:01:03 UTC**  
Cutoff: **2026-10-01 14:26:16 UTC**

## Decision

**No canonical numerical target movement.**  
One secondary-lane planning statement changes: the RX 6800 now has an **exact-card short-context decode receipt (~28.1-28.3 TG)**, so the lower edge of the existing ~28-36 TG lane is no longer purely transferred from RX 6900 XT. The ~128K numbers remain inferred.

Durable qualification additions:
- measure **MTP-on and MTP-off cold prefill separately**; speculative decode wins do not imply free prompt processing;
- add a **full-cache boundary** test for QSA/k-pool models;
- keep shared expert cache as the default until Strata per-layer native-pack admission is fixed and shown useful;
- on AMD, record release HIP optimization flags/build-folder provenance, because a poisoned configure can silently leave kernels at `-O0`;
- prefix-cache reuse on hybrid recurrent models must prove that rejected speculative positions cannot re-enter through cached recurrent state.

## UPDATE — llama.cpp #29761 merged: Flash-Next MTP is now mainline, with a deep-prefill caveat

PR #29761 merged at 11:13:30 UTC:
https://github.com/ggml-org/llama.cpp/pull/29761

Published DGX Spark / Flash-Next IQ4_XS sample:
- baseline decode **28.36 TG**
- MTP decode **43.88 TG**
- overall decode speedup **1.55x**
- overall acceptance **0.640**

Post-merge user testing in the strict window adds an important caveat. On a 3-GPU setup with a Q8 target, Q4 MTP draft,
262,144 configured context and a real ~98.4K prompt:
- MTP-on prompt processing was about **332-333 PP**;
- the same reporter says a non-MTP configuration reached about **850 PP**, but that comparison also changed batching
  parameters and is not a controlled A/B.

Maintainer follow-up says layer split is pipeline parallel and should scale with any GPU count, so the reported MTP
prefill result is still under diagnosis.

Classification: **UPDATE / merged-current + runtime caveat**. MTP is now broadly available in llama.cpp, but Project 51
must benchmark prompt processing and decode independently.

## RECOVERED OLDER -> MERGED CURRENT — llama.cpp #29751 fixes deep QSA attention path

PR #29751 was created before this watch but merged at 11:13:27 UTC:
https://github.com/ggml-org/llama.cpp/pull/29751

Exact model-family receipt, DGX Spark / Qwen3.8-Flash-Next UD-IQ4_XS:

At 131,072 prior-token depth:
- ub512 PP2048: **356.99 -> 570.56 PP**
- ub512 TG64: **14.08 -> 21.83 TG**
- ub2048 PP2048: **370.71 -> 650.60 PP**
- ub2048 TG64: **14.08 -> 21.20 TG**

The fix changes how the Qwen4Exp attention path uses hybrid-indexer pooling.

Classification: **RECOVERED OLDER / MERGED CURRENT**. This is strong evidence that deep-context QSA runtime path quality
can dominate both PP and TG, but it is DGX Spark/IQ4_XS and does not transfer numerically to the 5070 Ti or M1 targets.

## NEW — llama.cpp recurrent/k-pool boundary hardening

PR #29799 merged at 11:49 UTC as a continuation of #29761:
https://github.com/ggml-org/llama.cpp/pull/29799

It fixes an invalid recurrent-memory assertion exposed by the new MTP path.

PR #29805, created 13:41:55 UTC:
https://github.com/ggml-org/llama.cpp/pull/29805

It fixes a QSA/k-pool cache-fill boundary where `n_tokens == n_ctx` could build one pool beyond the real cache,
triggering unexpected graph reallocation/abort. Its reported recurrent rollback suite passes 11/11 and save/load
state passes 128/128 after the fix.

Classification: **NEW correctness / boundary evidence**. Add an exact-full-cache boundary case to long-context certification.

## NEW — Strata #372: group prompt expert gathers instead of synchronizing per expert

PR #372 created 14:17:02 UTC:
https://github.com/Niko1221/Strata/pull/372

RTX 5090 / IQ2_XS / Windows:
- 32K prompt: **~6102 ms -> ~5581 ms (-8.6%)**
- 8K: about **-10%**
- 2K fixed-cache: **872 -> 762 ms (-12.6%)**

The implementation turns per-expert gather/wait/release into one launch/wait/event per MMQ group. First-token logits
are reported bit-identical on 2K/8K/16K/32K with a fixed expert cache.

Classification: **NEW exactness-preserving prefill mechanism**. Useful Strata optimization direction; no 5070-Ti target credit.

## NEW — Strata #374 overlaps the first PLE-row gather with layer 0

PR #374 created 14:21:38 UTC:
https://github.com/Niko1221/Strata/pull/374

RTX 5090 / IQ2_XS / Windows:
- 32K: about **-2.9% prompt time**
- 8K: about **-5.3%**
- first-token logits reported bit-identical to 0.1.31 at 8K/32K.

It also raises default PLE inflight reads from 64 to 256; the reporter says this saturates a Samsung 9100 PRO.

Classification: **NEW prompt-I/O overlap mechanism**. Transfer the overlap design, not the storage-specific percentage.

## NEW — Strata #369: native per-layer expert cache is currently wrong and not a throughput win after fixing

Issue #369 created 13:25:39 UTC and updated 14:19:17 UTC:
https://github.com/Niko1221/Strata/issues/369

On native/sized packs, `--expert-cache-per-layer` starts every layer's cursor at slot 0 and the global fill loop can
stop when one layer exhausts its quota. The engine's startup byte verifier catches the bad residency map.

With the proposed fixes:
- a 64-slot/layer run reaches ~72% hit rate and **23.6 TG** in one configuration;
- under an equal ~10.9-GiB VRAM reserve, shared cache measured **20.7 TG** vs per-layer **19.1 TG**.

Classification: **NEW correctness finding**. For Project 51, shared cache remains the default; per-layer gets no speed credit.

## NEW — exact RX 6800 short-decode receipt + HIP build-integrity trap

Strata PR #376 created **14:24:45 UTC**, 91 seconds before cutoff:
https://github.com/Niko1221/Strata/pull/376

Exact card: **RX 6800**, Windows 11, HIP SDK 7.2, Strata 0.1.30 + Windows HIP work, expert cache 2048.

A failed first HIP configure can leave cached release flags empty, so later builds compile GPU kernels at `-O0`:
- poisoned build: **0.24-0.27 TG**
- proper `-O3 -DNDEBUG`: **28.1-28.3 TG**
- verify/commit/draft window: **7.06-7.50 s -> 59-62 ms**

The same cache-poisoning mechanism is reproduced on Linux configure flows too, though the exact RX-6800 speed receipt is
Windows and does not state a long-context depth.

Classification: **NEW exact-card evidence / build-integrity mechanism**.

Target effect:
- retain **~28-36 TG short-to-128K** and **~27-34 TG filled ~128K**;
- the **~28 TG lower edge now has an exact RX 6800 short-context physical anchor**;
- filled-128K and PP remain inferred until an exact long-context run exists.

## NEW — Strata #370 quality-first 111-GB quant remains fast on a very large host tier

Issue #370 created 13:40:50 UTC:
https://github.com/Niko1221/Strata/issues/370

Community report:
- RTX 4080 SUPER 32 GB
- Ryzen 9 5950X
- 128 GB DDR4
- Qwen3.8-Flash-Next UD-Q4_K_XL, ~111.3 GB
- 262,144 configured context, INT8 KV
- reported **1,850-2,060 PP** and **48.3 TG**

The report says ~250K tokens prefill in ~124 s, but does not include a controlled quality/reference protocol.

Classification: **NEW capacity/performance receipt**, not transferable to the user's 16-GB/64-GB 5070-Ti box.

## SAME-DAY CURRENT — Strata DFlash2 is still only an investigation

PR #366:
https://github.com/Niko1221/Strata/pull/366

It explicitly separates:
1. compatible Flash-Next DFlash2 checkpoint availability;
2. verifier/rollback correctness;
3. end-to-end performance after memory/expert-cache cost.

It does **not** claim a compatible Flash-Next checkpoint, completed implementation, or benchmark.

Classification: **SAME-DAY CURRENT / planning only**. No DFlash2 target credit.

## UPDATE — oMLX Splash integration rebased onto current main

PR #4154 rebases #4133:
https://github.com/jundot/omlx/pull/4154

The implementation has direct M1 Max 64-GB validation for integrating `splash-m1` as an oMLX backend and serving
Qwen3.8-27B-Splash. It does not add Flash-Next support, concurrency validation, or clean benchmark numbers.

Classification: **UPDATE**, useful for M1 fleet orchestration but no dual-M1 Flash numeric transfer.

## NEW — oMLX #4157 catches a silent prefix-cache dedup race

PR #4157 created 14:07:34 UTC:
https://github.com/jundot/omlx/pull/4157

A store-cache dedup path could drop its lock after lookup; another thread could free/reuse the block ID before the
reference was incremented, allowing the wrong block to be attached and silently polluting restored KV. The fix
revalidates `block_id + expected_hash` atomically.

Classification: **NEW cache-correctness evidence**. Add concurrency stress around cache-store/fetch/reconstruct ownership.

## NEW — TensorFold mixed-width data supports sensitivity-aware allocation, not DASLab fidelity

Issue #188 created 13:23:53 UTC:
https://github.com/ashhart/TensorFold/issues/188

For Qwen3.8-27B on 96 x 512-token held-out windows:
- 4-bit g64: KL **0.057**, top-1 **92.2%**
- 5-bit g64: KL **0.016**, top-1 **96.4%**
- 6-bit g64: KL **0.006**, top-1 **98.2%**
- EXL3 4.0 bpw: KL **0.018**, top-1 **96.7%**

The same issue reports attention carrying disproportionate drift on Qwen3.6-35B-A3B.

Classification: **NEW mixed-precision mechanism evidence**. This supports sensitivity-aware allocation generally, but
does not raise the DASLab Flash IQ3_XXS AA priors.

## NEW — vLLM #59605 shows large untuned skinny-GEMM headroom on DGX Spark

Issue #59605 created 13:44:52 UTC:
https://github.com/vllm-project/vllm/issues/59605

On TP2 DGX Spark / Qwen3.8-Flash-Next derivative:
- dense BF16 projections consume about 28 ms of a ~51-ms decode step;
- tuned skinny GEMMs reduce dense-GEMM time **31.4 -> 27.9 ms**;
- re-storing selected dense layers in FP8 reduces the reported decode step **51 -> 43 ms** with held-out NLL
  **0.3838 vs 0.3842**.

Classification: **NEW Spark software-maturity evidence**. It strengthens the view that Spark performance is still
kernel-limited; it does not create a reason to buy.

## RECOVERED OLDER / CURRENT UPDATE — hybrid prefix cache + MTP can reuse rejected recurrent state

vLLM issue #53912 was created in August and updated inside this window:
https://github.com/vllm-project/vllm/issues/53912

On a Qwen3.5-class GDN/full-attention hybrid with MTP and prefix caching, the report sees malformed responses only after
prefix-cache hits begin. The suspected path leaves a trailing recurrent block containing state written over rejected
draft positions reachable to later requests.

Classification: **RECOVERED OLDER / updated-current**, not NEW. It materially reinforces the Project-51 rule that
prefix reuse on hybrid recurrent models must prove rejected speculative state cannot be restored.

## Strict-window negative scan

- DASLab Flash-Next GSQ-RCO main remains **`ed59f92`**; no new checkpoint/allocation/benchmark.  
  https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/main
- Strata latest release remains **0.1.31**.
- oMLX stable remains **0.7.0**.
- TensorFold stable remains **0.6.0**.
- No Project-51-relevant strict-window MoEspresso, Ishizuki, TurboQuant or MLX-core release/commit.
- mlx-serve's strict-window commit is test/changelog-only for this project.

## Target state

Canonical targets unchanged:
- RTX 5070 Ti IQ3_XXS PP: **3,000 / 2,900 / 2,750 / 2,500** at 32K/64K/128K/262K;
- 262K/64-GB conditional fit prior: **~90%**;
- IQ3_XXS AA>=38 **~85%**, AA>=40 **~65%**;
- IQ3_S AA>=40 **~80%**;
- K6/V4 long-horizon quality **~60-70%**;
- dual-M1 Flash target: **~40 TG @128K / ~400 PP**.

RX 6800 secondary lane remains numerically:
- **~28-36 TG** short-to-128K;
- **~27-34 TG** genuinely filled ~128K;
- **~220-300 PP** cold prefill;
but the short-context lower edge now has an exact RX-6800 physical anchor.

## New hard boundary

**2026-10-01 14:26:16 UTC**
