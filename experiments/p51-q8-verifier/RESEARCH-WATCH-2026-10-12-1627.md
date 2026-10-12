# Project 51 research watch — 2026-10-12 16:27 ET

Prior hard boundary: **2026-10-12 16:49:11 UTC**.
New cutoff: **2026-10-12 20:27:25 UTC** (user request).
Method: GitHub PRs/issues/commits and releases on Strata, oMLX, mlx-serve, llama.cpp, vLLM, SGLang, DS4, pi-vcc and adaptive-KV fork, plus model/Hugging Face and Reddit evidence. Classify **NEW** by substantive creation/measurement time inside window; **UPDATE** for older issues newly fixed/merged; **RECOVERED** for older community receipts. Do not treat a later commit or crawler date as the result's measurement date.

## Canonical decision

**No promotion of exact dual-M1 Max PP2 / TB4 128K TG or cold PP, no owner's RTX5070Ti/64GB Swift IQ3_S xhigh long-context numeric target change, no model-quality promotion and no hardware purchase.** The certified P58/P61/P69B3/P69B6/P69B11/P69B12 exact-Q8 verifier baseline, `CURRENT.md`, `RUNTIME-STATE.md`, `RESEARCH-TARGETS.md` are unchanged.

**Operational candidate update:** new stable Strata **v0.1.43.1** published 2026-10-12 17:30:57 UTC supersedes plain v0.1.43 as the *test candidate*, **not** automatically the certified baseline. Keep v0.1.42 pinned for ABBA and all quality/liveness gates, and explicitly distinguish the release's asserted parity from exact-user verification. No new supported Strata source commit beyond v0.1.43 itself was in the last default-branch commit list before this release query; release artifact is authoritative for shipping state.

## UPDATE: Strata 0.1.43.1 hotfix (published within window)
https://github.com/Niko1221/Strata/releases/tag/v0.1.43.1

The release consolidates fixes for issues known in earlier watches; the shipped release is NEW, the original failures are KNOWN:
- **Adaptive overlap OFF by default on all GPUs**, opt in via `STRATA_ADAPT_OVERLAP=1`, startup records effective status. Reacts to published RTX5070Ti (68.4 on versus 86.4 off), RTX5060Ti -19%, RTX5090 laptop -21% regressions and one RTX5090 desktop small benefit. Earlier 0.1.43 OFF workaround now default; benchmark ON vs OFF on owner's host, not globally ban ON.
- **Linux NVIDIA callback affinity/overlap signaling**: warm callback before decode CPU pin; replace host callbacks with 4-byte pinned-memory stream-ordered signal (opt back to callback with `STRATA_ADAPT_SIGNAL=host`). On RTX3060 / Core Ultra 7 265 Linux, 5 paired runs under reporter's overlap settings **36.5 -> 56.5 TG**. This is not 5070Ti or long context.
- **PLE `direct` no longer silently switched to `mmap`** when throughput probe low (old auto via `STRATA_PLE_AUTO_MMAP=1`). Windows cold-table 60-second watchdog and Linux SATA SSD long-prompt regressions addressed; measured SATA 77.8K prompt 884 PP direct vs 76-154 PP mapped in older release and mapped 32K prefetch ~269->301 PP after patch. Collect actual I/O mode and storage queue/throughput; do not call cached page reads disk I/O.
- **Multi-agent CUDA:** split + batch-MTP restores pipelined groups (2x A4000, four simultaneous requests 62.3->85.2 aggregate TG); admission BGEN 400 becomes wait/retryable 503; GPU ownership before_load hook can fail-closed with `before_load_strict` and load/unload waits. Strict failure handling preferred for fleet.
- **Owner's RX6800 exact model of GPU:** RX6000 Windows side-stream correction tested RX6800 7.9K prompt **584–596->798–808 PP**, not a Linux result, TG unchanged/unreported.
- **Short-prompt cache loan and PLE/parking watchdog:** #2090 cache-loan fatal fit repaired; #2049 parked snapshot writes now report progress, startup install stamp compares engine source build/version. Distinguish load/compile from runtime.
- **AMD multi-slot GPU source-lifetime and Intel SYCL swap defects** fixed; not exact target speed receipts.
- **Server tool delimiter recovery** and JSON fenced tool support; more detailed compatibility tests required.
- **Important not fixed by reported release changelog:** optional Foresight expert identity race #2134 (`STRATA_FS_SLOTS=0` remains); Pi client's ignored `thinking_budget_tokens` #2141/#2140 not listed as included. Explicitly use supported `reasoning_budget_tokens` or verify adapter; don't infer these fixes shipped.

Action: release-locked runtime experiment matrix 0.1.42 vs 0.1.43.1 (overlap 0/1, pinned host, effective PLE, RAM/pagefile/commit, VRAM reserve, prefill, KV type), at actual filled 16K/64K/128K/192K/near262K and full coding/tool correctness. B1 vs B2 separately, stable output/health/24h soak.

## NEW: 12-part oMLX memory-scheduling/pause-resume stack #4478–#4489
Created 2026-10-12 19:45:52–19:46:20 UTC, all **open/unmerged**, mutually dependent, opt-in/off defaults.
Start https://github.com/jundot/omlx/pull/4478 ; finish https://github.com/jundot/omlx/pull/4489

Mechanisms:
1. #4478 independently commit completed prompt-prefill blocks (including TurboQuant) asynchronously to SSD prefix before request finishes; no re-prefill from zero on later parked session.
2. #4479 park one prefill victim under nonemergency memory pressure, pin committed blocks, preserve client stream and arrival order.
3. #4480 single-victim abort fallback and per-request domain-separated **exact-chain** cache (do not match recurrent/MTP private state as generic prefix).
4. #4481 pause one decoding row: emit pending token, save exact prefix and parser, sampler, stop conditions, RNG, output budget; restore without cold prefill. Singleton Lightning MTP hands off to non-MTP before pause; batched MTP/DFlash/VLM MTP rows not supported. Loss of cache fails with explicit `decode_resume_lost`.
5. #4482/#4486 resume only when estimated capacity permits; pressure hysteresis, solo mode for parked head, no immediate re-park/abort thrash.
6. #4483 media-aware text suffix chunking after a cached media prefix with mRoPE checks, not an unrestricted multimodal-cache proof.
7. #4484/#4485 cap-aware memory scheduling: `memory_scheduling` mode, `context_exceeds_capacity` structured nonretryable 400 with required/capacity/token math; requests fitting later wait rather than fail, capacity API for harness.
8. #4487–#4489 emergency pause-first and explicit stall/progress clock; count hot-cache pages releasable before capacity refusal; avoid false timeout while another request makes progress.

Validation: latest slice #4489 Python suite **17,580 passed, 3 failed, 721 skipped**, same 3 pre-existing `test_gemma4_rendering.py` failures on base; **not a clean 100% pass, and no physical user's M1 test**. Author's full-stack M5 Max 128GB / Qwen3.8-27B-oQ4e-MTP/TurboQuant4 runs report no aborts in forced 42–44GB pressure scenarios against aborting main, but **one Mac, one checkpoint family, single scenario runs, full stack plus other fork features, and not a current-main isolated 12-PR A/B**. Do not substitute for measured 64GB M1 Max headroom or core PP2. Do not deploy until upstream merges sequentially and passes exact resume state/long-token streams/duplicate parser behavior/memory high-water mark tests.

P51 takeaway: exact SSD parking, tiered admission, and structured fits-later vs never-fits capacity are explicit fleet implementation requirements; maintain deterministic state identity, consumer epochs, fail closed and restore-by-commit-frontier, not just cache-hit counts.

## NEW: oMLX Flash quality/throughput and quantization changes
- **#4476 created 18:26:56 UTC**: expose `preserve_ngram_table` through oQ streaming APIs/UI to leave Flash-Next PLE table **16-bit unquantized**; table file about **30GiB quantized->95GiB raw**. Proper quantization accounting now separates external ngram table from transformer `effective_bpw` and resident model bytes. **No BF16-quality/E2E experiment, no TG evidence**; upstream proposal open. On 64GB Mac such a raw table must be SSD streamed; poor page-density can reduce hot cache. P51 quant objective: separate actual resident transformer BPW, on-disk PLE quality and MTP/draft size, qualify quality differences with frozen xhigh tasks before adopting extra 65GiB disk footprint.
  https://github.com/jundot/omlx/pull/4476
- **#4475 created 17:33:06 UTC**: padded tails for shared large Q8 projection on MTP verification row counts; M5 Max single head micro 7-row **2.798->1.876 ms**; full model 8k decode 101.5->102.5 TG (within noise), and the author's extended suite was interrupted by host freeze. Do not promote full-model TG.
  https://github.com/jundot/omlx/pull/4475
- **#4474 created 17:02:04 UTC**: rebase of earlier ANE/prefill patches to DFlash target path, M4 Pro 64GB dense Qwen3.8-27B/oQ4e DFlash2: 16K cold prefill **75.2->110.8 PP**, TTFT **217->147 s**; decode **~10–11 TG unchanged**. Adds ANE verification guard and load-time cost (2.5s->31.5s); greedy output sometimes differs, so review the quality boundary. Weak M1 Max transfer and not Project51 Flash dual-host PP2 direct evidence.
  https://github.com/jundot/omlx/pull/4474

## NEW: 5070Ti-class adjacent actual-context community reports
- **Strata #2156 created 19:11:04 UTC:** RTX4090 24GiB /63.9GiB Windows 0.1.43, **Swift1.5 IQ3_S**, configured 131K but short-chat **88.9 TG**, fresh 16K **2409.2 PP**, agent 14.5K **115.8 TG**, greedy/thinking off, speed-only. Same host Unsloth UD-IQ4_XS Flash reported 38.6 TG with 204.8K setting and 32.4 TG with 131K setting under *different cache policies*, so these are not controlled source-like quality comparisons.
  https://github.com/Niko1221/Strata/pull/2156
- **Strata #2163 created 20:10:00 UTC:** two RTX3080Ti 12GB, 76GB RAM, asymmetric second GPU PCIe x4 and abliterated Flash Q4_K_M with ~196K configured: tuned manual layer split K27 vs auto K41 increases expert residence 4694->6714 and source author reports +24% decode; stock suite short 104.5 TG /16K 1198 PP, agent 14.5K 104.1 TG. **No 196K filled-context measurement and no quality check**, non-Flash Swift quant, user lacks same topology.
  https://github.com/Niko1221/Strata/pull/2163
- **NEW Reddit report during sweep** (self-reported, not independently reproduced): RTX3090 24GB VRAM +32GB DDR5 i7-12700KF/Linux Strata original Flash IQ3_XXS, **actual 121,566-token fresh prompt** ~1,325 cold PP and ~59–62 TG, **actual 249K prompt** ~1,008 cold PP and **41.8 TG**, 90.5% expert-cache hits. 21GiB pinned host-resident experts +12.2GiB VRAM experts with `--mmap-experts --resident-cpu-experts --ple-io direct`; 2.45GB RAM free at 249K, no proof of sustained 262K output. On an 11.7K prompt native RAM residence improved 555.6->656.1 PP, 48.4->61.1 TG; P-core pinning combined with a second changed parameter so attribution is confounded. **Not exact owner 16GB 5070Ti, not Swift IQ3_S/xhigh and not agent-quality tested; do not extrapolate.**
  https://www.reddit.com/r/LocalLLM/comments/1x3ohgh/iq3_xxs_qwen38flashnext_125b_at_full_262k_context/
- **Strata v0.1.43.1 release** is now best physical baseline candidate; last run's shorter 0.1.43 speed tables are not hotfix results. No exact xhigh Swift at 262K with the user's 64GB host.

## NEW: speculative long-context drafter work / PP roadmap
- **vLLM #61261 created 18:34:24 UTC:** opt-in `draft_context_window=32768` for DFlash/DSpark leaves target's KV and verification unchanged; Kimi K3 draft's accepted length had collapsed above ~128K; draft window restores acceptance **1.45->2.29 (128K–256K)**, **1.26->2.22 (256K+)** and output **+31%/+23%** respectively, mixed 16–300K c16 +9%. Self-reported Kimi K3 with two attention backends tested, 200-GSM8K check minimal, not Qwen3.8/Flash-MTP and not model quality improvement. Mechanism supports separate *draft effective window* and *target context capacity* in Project51, subject to output-distribution verification.
  https://github.com/vllm-project/vllm/pull/61261
- **vLLM #61255 created 17:11:40 UTC:** speculative scratch inflated physical convolution rows when exporting Kimi K3 recurrent checkpoint: 12/12 synthetic histories wrong on base, 0/12 wrong with logical history length. No full-weight quality validation. Add checkpoint 'logical history length != scratch capacity' to Relay recurrent-state fixtures.
  https://github.com/vllm-project/vllm/pull/61255
- **SGLang #43885 created 18:20:46 UTC:** Q4 pipeline-parallelism roadmap: PP prefill/PD mature but PP decode x DFlash/EAGLE3, PP CP, microbatch bubble instrumentation remain open. Reinforces PP2-first architecture on TB4 and *do not infer decode TG from PP prefill feasibility*.
  https://github.com/sgl-project/sglang/issues/43885
- **DS4 #1210 created 20:19:20 UTC:** Strix Halo ROCm10.1 compile/rounding fix for MXFP4 Q8_K scales; author reports one 1-ULP rounding-boundary quant error flipping one activation and downstream 0.041 output max-abs, fixed tests 1–512 tokens. Portability/precision provenance, no dual-M1 TG movement.
  https://github.com/antirez/ds4/pull/1210

## Negative and existing sources
- Strata optional Foresight race #2134 and Pi `thinking_budget_tokens` alias #2140 are **not listed** among v0.1.43.1 fixes; keep those safeguards.
- pi-vcc and RaymondHuang adaptive KV fork: no new Oct12 PR/issue or recent code commit after cutoff, earlier audit stands.
- A number of October 12 Reddit Flash-Next posts exist, but only reports with actual context, mode, quant and hardware deserve benchmark credit. No official Qwen successor weights or direct Project51 M1 Max PP2 after last boundary verified in this sweep.
- No runtime testing on the user's hardware and no GitHub Actions experimental tuning was launched. Research watch and GitHub canonical state updates are **documentation only**.

## Action priority

1. Pin Strata v0.1.42 and trial v0.1.43.1 with strict QA. Keep Foresight off; test owner exact 16GB/64GB over context ladder, check effective overlap signal, PLE I/O, file-cache reads vs device reads, xhigh API budget, expert profile preserve, VRAM/host commit.
2. oMLX memory-scheduling stack only after its dependencies merge; adversarial pause/resume with 3-5 agents and forced 64GB ceiling, unique decoder output hashes and model/GDN/MTP/parser state.
3. Separate transformer quant, disk PLE and draft precision sizes/quality. No raw-PLE size penalty justified without source-like xhigh evaluation.
4. Test draft attention window as a controlled separate setting for compatible draft models; never truncate target state.
5. Keep active project 2xM1 Max PP2 and dense 27B independent-agent path; request direct physical data before moving targets.

**New hard research boundary: 2026-10-12 20:27:25 UTC.**
