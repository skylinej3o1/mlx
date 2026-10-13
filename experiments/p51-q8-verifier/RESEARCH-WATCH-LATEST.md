# Project 51 research watch — 2026-10-13 11:37 EDT

Previous strict cutoff: **2026-10-13 11:13:33 UTC**.
New strict cutoff: **2026-10-13 15:37:36 UTC** (user message).
Method: GitHub connector PR/issue created-at verification, default-branch commit scans including Basalt, review of issue bodies/test recipes, and contemporaneous external web search. NEW means creation within the stated interval; RECOVERED/KNOWN means older evidence surfaced now; unmerged proposals are never called released. Earlier Oct13 07:13 watch already covers #2240 cross-SYCL stage, #4507 loader/LES, #4508 batched DFlash, #4509 SSD resume, #2247 BF16 saved state, #4496 M1 benchmark. Basalt is an addition to tracked external engines following its Oct13 08:32 EDT audit.

## Verdict
**Do not promote any numeric certified benchmark/target, exact-source custom xhigh quant, P58/P61/P69B3/P69B6/P69B11/P69B12 verifier code, or buy hardware.** No actual owner equipment benchmark or CUDA->M1 state handoff was run. Maintain Strata 0.1.42 pinned ref and 0.1.43.1 single-GPU candidate (with separate layer-split version caveat); treat Basalt as an isolated alternative for Linux RTX5070Ti, not a confirmed Swift1.5 IQ3_S 262K winner. M1 Max two-lane oMLX/Splash work and experimental PP2 unaffected.

## NEW: Strata multi-user layer-split scheduling bottleneck #2275
Created 2026-10-13 13:42:54 UTC, open. https://github.com/Niko1221/Strata/issues/2275

2xRTX2080Ti 11GiB, 123GB RAM, original Flash IQ3_XXS, CUDA 0.1.43, layer-split 0–23/24–47, 96K/192K actual context. Single 96K stream ~1555 cold PP and 135 TG in reporter's setup. With another 96K prompt running, old stream gets **3.67 TG across 63s fresh prefill** vs **36.6 TG while only decoding**, because prompt reads own device and draft path. Four simultaneous unique 96K prompts TTFT **51.1/102.9/154.6/206.4s** and 4 streams total 412s cumulative TTFT; single prompt read at a time, and split batch verify does not perform per-slot MTP: **one emitted token per slot/window**. Strong evidence of an issue for this older-GPU layer-split topology, not a claim that RTX5070Ti solo or two independently served Macs behave similarly.
P51: preserve independent-agent scheduling baseline; only use distributed PP2/Relay when demonstrably better with measured *concurrent TTFT, live per-agent TPOT, total task completion and quality*. No 90TG inference from solo into parallel.

## NEW: Strata conversation-cache re-parking waste #2264 / proposal #2265
Issue created 2026-10-13 12:33:10; PR created 12:33:33 UTC, both open.
https://github.com/Niko1221/Strata/issues/2264
https://github.com/Niko1221/Strata/pull/2265

On RTX5090 Laptop 24GB/WSL 54GB allowance, one 100–185K agent session, v0.1.43.1 and 1,418 successful parks: **2,251.9 GB** host-RAM buffer copying, **4.7%** later reused, **1,548s** cumulative copy time, 425 superseded park images; not SSD I/O. Root: same conversation parked and recaptured every turn even when cache would retain same prefix. Proposed `--conversation-cache-park-gain N` opt-in, default zero, parks only when appended growth since preserved ancestor merits it; reporter shows **66.7% less copied data** on limited gate test, not a model throughput improvement or reproduced owner setting.
P51: trace cache write bytes, retained state age, fetched bytes, copy-overhead and memory headroom, not mere cached token count. When compiling multi-agent platform ensure parking cost and reused bytes are observable; avoid copying gigabytes to save milliseconds.

## NEW: Strata v0.1.43.1 layer-split regression #2281
Created 2026-10-13 14:20:59 UTC, open. https://github.com/Niko1221/Strata/issues/2281

2xRTX3090/48GiB aggregate, UD-Q4_K_XL, k8v4, layer-split, CUDA container; interleaved `tools/ab_engine.py`: v0.1.43 decode ~82.2–82.7 TG vs v0.1.43.1 **64.7 TG**, ~20–22% regression. `STRATA_ADAPT_OVERLAP=1` ignored/rejected for layer split (`off: not on a layer split`), so forcing it cannot recover baseline. Source hypothesizes another pinned-bounce change but has **not bisected causal commit**. Do not infer the single RTX5070Ti regression travels across topology, and don't deploy any hotfix untested to future split without A/B across exact pipeline. Strata default branch head observed `a0116b2782` and stable v0.1.43.1 remains our *candidate*, not validated production build.

## NEW: explicit KV memory correctness races
- **SGLang #44070 issue created 2026-10-13 13:46:28 UTC**, https://github.com/sgl-project/sglang/issues/44070 : 1P1D NIXL + HiCache, 2 concurrent identical 100K prompts with host-only shared prefix. A just-created GPU page becomes visible as a device cache hit before async H2D fill completes. Early cached-prefix transfer sends stale bytes to decoder; reporter **39/40 corrupted in older direct image, 29/30 in kernel image, 29/30 checksum mismatches on Sep23**, with early-send disabled **0/84**. The *report is newly filed*, but **measurements on Sept14 and Sept23 images are historical**. Don't call an Oct13 new model-speed or exact Project51 experiment.
- **SGLang proposed fix #44081 created 2026-10-13 14:59:45 UTC, open** https://github.com/sgl-project/sglang/pull/44081 : suppress early KV send for any batch with pending HiCache load-back. A 2026-10-13 nightly patch repro: checksum errors **29/30 -> 0/30** for direct, kernel fix 0/30, both clients' greedy outputs match cold. Delay transfer ~54ms in that affected 100K case. **Not merged.**
- **SGLang #44076 created 14:28:14 UTC, open** https://github.com/sgl-project/sglang/pull/44076 : GatedDeltaNet prefill chunk boundaries must be 64-token-aligned in deterministic mode. MI350X/Qwen3.8-27B: splitting same 3000-token prompt with other batchmate at arbitrary boundaries caused 21/24 outputs differ, 12/12 matched when aligned, 24/24 when unsplit. Shared radix-prefix nonaligned cases need aligning **absolute chunk end**, not only chunk length.
P51 Relay oracle: no page published/reused until complete CPU→GPU/remote materialization fences and epoch/identity check; include immutable QSA indexer + sparse key state alongside KV and GDN, and ensure chunk/block-boundary determinism.

## NEW: Strata Pi/Anthropic/vision contract fixes, all OPEN
- #2284 created 14:57:26 UTC https://github.com/Niko1221/Strata/pull/2284 : declared namespaced tool alias may lose its parameter schema on streaming, e.g. intended literal string path `"123"` parsed as numeric 123; proposed canonicalize unambiguous aliases, restore declared types. 63 unit checks/8 regressions, no GPU run. Test tool names, namespaces, types, chunk splits.
- #2285 created 14:58:32 UTC https://github.com/Niko1221/Strata/pull/2285 : late system/developer messages downgraded to user roles by OpenAI Chat/Anthropic/Responses adapters. Proposed role preservation; 52 focused model-free tests. Privilege/precedence is an agent correctness/security requirement.
- #2286 created 14:59:14 UTC https://github.com/Niko1221/Strata/pull/2286 : vision image cache lifetime ends before combined embeddings copy, concurrent request may evict images and corrupt/reject read; add lock and ordering, 20 focused model-free tests, GPU throughput impact unknown.
- #2290 created 15:09:45 UTC https://github.com/Niko1221/Strata/pull/2290 : Anthropic `cache_creation_input_tokens` reporting missing; proposed split new vs reused tokens while keeping `input_tokens>=1` to avoid Claude Code double count; **display/cost accounting only**, not improved actual reuse or decode.
- #2287/#2288 created ~15:03 UTC propose better partial GGUF download resume, SHA verification/header/tensor extent checks. Operationally relevant for 80+GiB artifacts. No inference speed.
- #2278 created 14:05 UTC adds legacy raw `/v1/completions` endpoint; doesn't change Pi Chat/Responses semantics.
All above are proposals, not Strata 0.1.43.1 shipped changes.

## NEW: CUDA/AMD/quant observations
- **llama.cpp #30449 created 2026-10-13 12:27:18 UTC, OPEN** https://github.com/ggml-org/llama.cpp/pull/30449 . With `--load-mode none` and large MoE buffers, single 56GiB cudaMallocHost allocation fails on Windows, silently falls back to pageable expert buffer. Proposed 4GiB cap on each pinned CUDA host allocation. RTX5090 Windows/UD-IQ4_XS 8 coding samples fresh PP **73.28→110.66**, decode **37.76→62.73 TG**, 0.6013 acceptance unchanged. Hardware/quant and load-mode-specific; **pinned actually succeeded** prerequisite to extrapolating. Basalt/Strata use own expert memory manager; can't assume this patch applies directly.
- **llama.cpp #30448 created 11:53:17 UTC** https://github.com/ggml-org/llama.cpp/pull/30448 : CPU AVX2 IQ3_S/XXS single-dot speed about +23%/+15% on Zen2, exact arithmetic claimed; model-level host pool gains unmeasured, and 265F is not Zen2. CPU fallback reference only.
- **llama.cpp #30460 created 15:26:07 UTC** https://github.com/ggml-org/llama.cpp/issues/30460 : proposed fixed-rate 11.5 bpw near-lossless BF16X preserves ~99% raw BF16 bits within exponent-range, two small models and RTX4090 test, unmerged PR #29896. No evidence for Flash GDN sensitive island or full Swift quant; too large for 3.3–3.6bpw routed expert plan. Keep in speculative precision research appendix, not purchase/deployment priority.
- **vLLM #61434 created 15:10:30 UTC** https://github.com/vllm-project/vllm/pull/61434 : defer FP32 GDN speculative recurrence stores for unaccepted draft steps, MI355X Qwen3.8-27B DFlash2 at 16/64 concurrent **+5.6%/+10.6% aggregate**, single neutral, max actual context 16K, output parity conditional FP32 reduction. Methodology inspiration for deferred rollback, no owned M1 timing transfer.

## Basalt status as candidate for RTX5070Ti
https://github.com/jesdga95/basalt
A substantial October 13 morning audit established Linux sm120-only, specialized Qwen3.8-Flash-Next, original IQ3_S 81.0GiB pack/46.8GiB experts, custom format, prefill/parallel/vision and quality harness. Claim of gains on 5090+5060Ti **must not transfer** to single 5070Ti + 64GB RAM. Community has converted Swift1.5 IQ3_XXS, but **no exact Swift1.5 IQ3_S xhigh at actual 262K on owner box**, no Metal backend. Basalt #1 previously had actual cross-Pi-agent KV leakage under `--parallel 2`+conversation cache; fixed commit `5b7eff1`, commenter several hours without recurrence, not long fleet stress.
Since previous 2026-10-13 12:32 UTC Basalt audit, **only new main branch change inside this watch** was 2026-10-13 14:24:59 UTC commit `92d9e2f308`, README reorder/removal of coder pack notes. Earlier Oct13 GPU checkpoint buffer pool/GDN async copy commits `426f552f57`, `f0f637c499` preceded cutoff; do not call them new now. No new 5070Ti benchmark or release in this sweep.
**Basalt to test isolated** on Lenovo Linux only after memory-admission check and model identity, first `--parallel 1` then adversarial Pi cross-session cache isolation, since `--parallel N` splits 262144 max context across slots unless full-slot mode reserves N KV. Compare same source artifact with Strata and test xhigh tasks, file cache, MTP acceptance and 192/262K physically filled.

## New separate memory/storage reference: Strata shared expert arena #2271
Created 2026-10-13 13:26:14 UTC, open. https://github.com/Niko1221/Strata/pull/2271
Multiple separate GPU-serving engines using same GGUF can share a single immutable RAM expert arena with OFD fill/attach locks, persistent mapped file and identity/version checks. Example 55.43GiB RAM pack vs duplicate RAM copies on multi-engine host. On **single Lenovo with one independent 5070Ti Strata instance** there is no added benefit; relevant to future multiple CUDA engines per Linux host, not independent Apple Metal devices.

## oMLX and model-server updates
- **oMLX #4515 created 2026-10-13 15:34:15 UTC, OPEN** https://github.com/jundot/omlx/pull/4515 : DeepSeek-V4.1 unconverted 475GB model source-checkpoint reader 4-thread read-ahead, M3 Ultra/512GiB full model load **91.2→61.4s**. Not target M1 64GB size, not ongoing decode TG improvement.
- **oMLX #4513 created 13:32 UTC, OPEN** https://github.com/jundot/omlx/pull/4513 displays exact refused setting names, not inference performance.
- **No new oMLX main merge after prior 09:58 UTC** in branch scan; #4496 exact M1 Max, #4508 batched DFlash, #4509 memory requeue remain prior-known and open.
- **mlx-serve issue #837 created 11:55 UTC** https://github.com/ddalcu/mlx-serve/issues/837 : ds4 runtime version 26.10.2 wrong MTP head detection; `--no-mtp` ignored; a M3 Ultra model that loaded on 26.10.1 now fails. Different backend from our intended oMLX/DS4 but adds configuration enforcement and backcompat tests.

## Action plan, no target movement
1. Strict **agent isolation + role/tool-schema fidelity** across Pi, Strata/Basalt, oMLX, and TencentDB: user namespace, session private prefix, returned slot identity, stream continuation and canceled request.
2. **Relay remote state fence/epoch:** no early cached-prefix send until host/SSD materialization complete, all QSA indexer keys and GDN state included; 64-token recurrence chunk alignment where model requires exact equivalence.
3. **5070Ti Linux runtime ABBA:** Strata0.1.42 vs0.1.43.1 vs Basalt same quant/model where convertible; show actual context and target xhigh, MTP disabled/enabled, free/pinned RAM/VRAM/file cache, TTFT, decode, sustained 2-agent throughput and quality. Do not port pinned memory RTX5090 numbers without verification.
4. **Two Macs:** keep independent dense27B agent lanes, optional upcoming batched DFlash/cache requeue; PP2 remains exact-Q8 verifier research. No hypothetical tokens/s increase until physical owner test.
5. **Cache telemetry**: track park bytes/usefulness, copy latency and full client-perceived TTFT/TPOT, not single-stream TG. Investigate opt-in park-gain after merge.
6. **Provenance:** no exact Swift long-context improvement, no new official Qwen refresh or DS4 default-branch activity established in this window, pi-vcc and TencentDB main unchanged since latest prior check.

**New strict hard research boundary: 2026-10-13 15:37:36 UTC.**
