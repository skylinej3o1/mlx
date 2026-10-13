# Project 51 research watch — 2026-10-13 07:13 EDT

Previous hard cutoff: **2026-10-13 06:13:56 UTC**.
New hard cutoff: **2026-10-13 11:13:33 UTC** (user message time).
Method: GitHub upstream PR/issue search and **main-branch commit/release checks**, plus limited Reddit/Hugging Face searches for fresh benchmarks. Classifications reflect **source creation/test/merge timestamp**, not API crawl date. This window follows the prior 02:13 EDT watch, which already contains MiniCPM-V 4.7, exact M1 Max #4496, Strata #2173, and #2234. Do **not** double-count those prior sources as new.

## Decision / state

**NO changes to certified Project 51 P58/P61/P69B3/P69B6/P69B11/P69B12 verifier, dual M1 Max PP2/TB4 B1/B2 target 40 TG at actual ~128K / 400 cold PP, per-Mac 27B target, RTX5070Ti Swift Flash long-context xhigh target, or custom xhigh mixed-bit Flash (~3.3–3.6 transformer BPW) design.** Keep oQ5e quality reference, oQ4e aggressive fallback, 0.1.42 pinned Strata control versus 0.1.43.1 candidate, FS off, source-like quality and resume gates. No hardware purchases.

Major change is **implementation research priority**: direct SYCL/CUDA stage-link test on an RTX5070Ti, integration plans for DFlash into oMLX batching, stateful SSD requeue, and typed/lossy state snapshot tradeoffs. None demonstrates the user's target actual 2xM1 Max physical PP2 or cross-vendor CUDA→Apple Metal state import.

## NEW Strata #2240: cross-vendor *stage worker*, but not CUDA→Metal Relay
Created 2026-10-13 07:27:57 UTC; open. https://github.com/Niko1221/Strata/pull/2240

Stacked on still-experimental remote-stage PR #1748; SYCL Arc Pro B70 can serve late layers from GGUF while CUDA or HIP main runs early layers; requires all worker-side experts resident and supplies no standalone head/MTP/PLE. Adds opt-in `STRATA_LOGPOS_IDS` to collect distributions over identical token ids for KL comparison; source verifies default CUDA and SYCL logits dumps byte-identical with new flags absent.

Actual experiments reported:
- RTX4070 + B70 on one Linux PC via loopback, Qwen3.8-Flash-Next IQ2_XS, K=12: **73–109 TG**, **1291 PP for 4K** vs B70-alone **44–74 TG** and RTX4070-alone **26–32 TG** (latter uses mapped experts); mean top-20 teacher-forced KL **0.135** over 25,256 positions, against B70-alone/RTX4070-alone baseline floor **0.152**. Not a strict equivalent compute/quality comparison.
- RTX5070Ti as early-layer CUDA producer and remote Arc B70 as later-layer worker via **2.5Gb Ethernet**, different model OrcaRouter IQ3_XXS, K=23: **78–108 TG** vs standalone 5070Ti **81–104 TG**; 4K PP **1145** vs standalone **2244**; split transfer window RTT **17.2 ms** (16.1 ms worker+1.1 ms link); teacher-forced KL vs 5070Ti alone **0.015** over 1,363 positions. Result is effectively neutral TG, **~49% PP loss**, hardware and model not the owner configuration. Tests lack HIP main, multi-worker relay, vision, Swift xhigh long agent traces.

P51: genuine cross-vendor stage link and useful KL/logprobs verification mechanism. **Do not conflate** stage-layer split (host→foreign GPU per-layer activation transfer) with our harder whole-prefill CUDA→Metal MLX cache/recurrent/QSA state handoff; do not assume Ethernet RTT models TB4. Need remote stage protocol provenance, committed frontier, exact quant/layout validation and coding accuracy, 32K→128K checkpoint verification before any topology promotion. Avoid a permanent stage split on a slow link without throughput gain.

## NEW oMLX #4508: DFlash migration into batched engines and cache
Created 2026-10-13 09:24:50 UTC, open.
https://github.com/jundot/omlx/pull/4508

Replaces separate, largely one-at-a-time DFlashEngine/dflash-mlx path with batched block drafter running under common oMLX scheduler and paged hot/SSD prefix cache. Concurrent-row DFlash on Qwen3.5/3.6/3.8 and GLM5.3, single-row speculative fallback for families with incompatible ragged rollback. Adaptive draft verify widths and the prior L1/L2 DFlash-only caches/settings removed or remapped.

M3 Ultra self-reported two-run request A/B vs prior DFlash engine, 512 output tokens, greedy and temp1/top_p0.95/top_k20:
- Qwen3.6-35B-A3B **4 concurrent +53% greedy / +100% sampled**, single-row varied +4–28% greedy / +11–21% sampled.
- Qwen3-4B **4 concurrent +112% greedy / +156% sampled**; Gemma4 26B 4 concurrent +85–129% though single-row can regress.
- GLM5.3 DFlash2 **+25–34% 4 concurrent**, multi-turn cached TTFT ~1.2s vs 4–5s cold-per-turn.
- Actual **M1 Max dense Qwen3.8-27B or dual M1 PP2 was not benchmarked**; quality equivalence across sampled cases and MTP/output drift needs more than tiny-model tests.

P51: prioritize this batching path for 3–5 independent-agent fleet once merged and qualified; single-lane and B2/B4 actual ~16K/64K/128K, cache-hit, streamed tool calls, DFlash2 acceptance and state rollback. This is **not evidence of Apple 128K 40 TG** nor that new DFlash works with #4496 M1-specific kernels without interaction tests.

## NEW oMLX #4509: maintainers propose a simpler cancellation/memory-preservation design
Created 2026-10-13 09:55:17 UTC, open. https://github.com/jundot/omlx/pull/4509

Explicitly **replaces the 12-part open #4478–#4489 stack** previously tracked; implementation requeues parked running requests through SSD cache under hard nonemergency memory pressure and caches cancelled prompt progress. Not supported: lone live request, no paged SSD, DFlash, SpecPrefill, VLM MTP, >2 requeues. *Lightning MTP* in tested VLM backend is supported. Lost progress up to one ~4096-token cache block; no never-fits capacity API or cached-media suffix path from old stack.

Qwen3.8-27B-oQ4e + Lightning MTP / **M3 Ultra**, three concurrent ~38K/32.5K/28K with forced 40GB ceiling: **main 0/3 completed vs candidate 3/3**; parking takes 0.8–1s; sequential resumed agents wait 40–60s. Cancel/retry 38K during prefill: cached 0 vs 28,672 tokens, TTFT **102.8→34.1s**; cancel/retry 32.5K during decode cached 0 vs 32,549 and TTFT **80.7→0.5s**. Small author demo, one stronger machine and quant, opt-in PR—not M1 B1 TG. Extend P51 'native Mac independent-agent deploy' roadmap with immutable identity, exact resumed output, connection/client cancel, park resources, fair queued execution and LRU pin credit.

## NEW oMLX #4507: LES expert lookahead, honest ablation
Created 2026-10-13 09:12:54 UTC; open.
https://github.com/jundot/omlx/pull/4507
https://github.com/tc-mb/llama.cpp-omni/blob/master/docs/les/lookahead-expert-scheduling.md

Port predicts next-layer routed experts from current layer hidden using next gate; launches SSD pread without blocking consumer; model computes **actual experts** on primary path so this is a scheduling hint, not routing approximation. More important implementation change: batched reserve/write for missed experts + IO worker pool4/batch16. Report on **occamy-1.0-oQ2e-mtp**, 50% resident, draft/MTP disabled: reported ~13.87→16.21 TG cold-series (+17%); ~14→17.24 warm (+23%), hit 96.0→96.7%, SSD bytes 3.27→2.70 GB per request. Full resident ~38 TG consumes more memory. Critical ablation: **predictor alone on/off 15.4 vs 15.6 TG, essentially zero**; primary gains from bulk expert installation/I/O overlap. At 70% resident both approaches converge around 20 TG. *Not* Qwen Flash/SwiFT, not user's M1 Max or exact dual host.
P51: take batched expert slot allocation + IO depth and provenance/cache validation as experiment candidates. **Do not credit LES prediction with +23% nor accept forecasted routing instead of ground truth.** Compare predictor only, loader only, combined, cache-residency-controlled across exact hardware.

## NEW oMLX #4510: silent OpenAI sampling field omission
Created 2026-10-13 10:24:22 UTC; open. https://github.com/jundot/omlx/pull/4510

`/v1/chat/completions` silently discarded `no_repeat_ngram_size` and `ngram_window` because request schemas lacked fields, leading to same OCR page repeats. Proposed history-based ngram hard-ban via processor with explicit 400 for DFlash/distributed unsupported paths; `/v1/responses` and `/v1/messages` still lack typed support and ignore, by PR's own admission. M5 OCR 1063 tests pass on branch vs 1041 base; constrained scenario has repeats removed, but exact-changing coordinate sequences still can loop to 1024. No direct Swift sampled MTP end-to-end quality parity.
P51: per-provider API feature-compatibility matrix; *unknown/ignored sampling controls must fail explicitly*, and agent loop guard cannot rely on unverified repetition flags.

## NEW Strata #2247: optional BF16 serialized state, not BF16 runtime state
Created 2026-10-13 08:58:56 UTC, open. https://github.com/Niko1221/Strata/pull/2247

`--session-state-codec bf16` stores GDN recurrent, conv, PLE history, QSA indexer + dead-key state as BF16 at SAVE/park boundary; execution still FP32. State payload **118,063,152→59,031,600 bytes (halves)**. Whole files shrink less because K/V unchanged: **1205.3→1087.2 MB (-9.8%)** for 63,459 tokens, **734.8→616.7 MB (-16.1%)** at 32,650 tokens, ~236.7→118.7MB tiny 37 tokens. On V100 32GB/96GB RAM original IQ3_S, measured 63K save 546.4→503.2ms, restore 759.5→714.3ms (single measurements). Largest sampled relative state rounding error **0.3891%**, small 32K needle recall checks pass at 10/50/90% depth but **no long continuation logits/KL, source-like code quality, rollback, older-checkpoint restored parity**, no HIP/SYCL builds. New saved file format v2 when coded, old engines reject. Defaults FP32.

P51: promising parked-disk/RAM state tier only; reject immediate canonical checkpoint precision reduction. Require 32/64/128/262K frontiers, xhigh tool tasks, recurrent/decay drift vs fp32, multi-turn branch rollback and format/schema identity. Serialize lossy state only as explicitly noncanonical approximate option; exact verifier stays FP32.

## NEW Strata #2253: RAM-gate malloc_trim and useful eviction bounds
Created 2026-10-13 09:45:38 UTC; open. https://github.com/Niko1221/Strata/pull/2253

glibc dynamic mmap threshold pushes second-generation 16MiB conversation chunks into process heap; freeing them can leave RSS / `MemAvailable` unchanged. Main's eviction loop then evicts all parked sessions chasing an unattainable free-RAM increase. Test example: free 64MiB parked heap→RSS -0.3MB, after `malloc_trim(0)` RSS -127.7MB; proposed call trim after evictions and refuse eviction when deficit >evictable bytes. 4276 +24 test checks pass, no exact long concurrent serving stress proof. This matters on the owner's 64GB host and Mac/PC cache pressure architecture, but single-node Lenovo NUMA tricks #2242 are irrelevant.

## NEW Strata #2243: opt-in Linux file-cache reclamation
Created 2026-10-13 08:16:05 UTC; open. https://github.com/Niko1221/Strata/pull/2243

Only if no experts read model files after startup: release redundant mapped GGUF page-cache copies using MADV_DONTNEED+POSIX_FADV_DONTNEED, preserving pinned/RAM and VRAM real expert stores. V100 32GB/125GB host, 50–57GiB cached freed in 6.7–8.2s at setup, decode 46.6→46.7 TG and first large prompt 5–8% slower once. **Not extra RAM/VRAM to allocate** without accounting for pagecache recoverability; owner Flash IQ3_S may stream experts and fail the safety preflight. Test memory.high/NUMA/pinned pages/PLE IO before enabling.
#2242 dual-socket `--numa-hot-node` no direct value on owner's single-socket Core Ultra7 265F.

## NEW TencentDB-Agent-Memory v2.0.3-beta.1 + Pi control-plane audit
New commit `badbd2179d06` at 2026-10-13 07:37:05 UTC; changelog v2.0.3-beta.1.
https://github.com/TencentCloud/TencentDB-Agent-Memory
October 13 beta adds optional pluggable decision-service for selecting skill / L3 memory changes (JEV default provider, disabled by default); optional *on-demand* skills instead of whole skill directory injected each turn; session transcript capture (under tdai.enabled), private repo SSH indexing, FTS health diagnostics. Oct9 v2.0.2's Pi-compatible Chat-protocol integration is older and not a new speed result.
New **unmerged** MCP PR #1642 created 09:03:13 UTC:
https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/1642
Optional stateless read-only `POST /mcp` exposes three Skill + two L2 scenario operations, identity forced from trusted headers rather than LLM arguments, with permission check. A bridge alternative, not shipped. Pi integration documentation is not one-click validated for our Strata/oMLX provider; existing `agents/README.md` does not list Pi as standalone adapter, even though changelog says Pi support. Test API auth, identity scope, stale memory, conflict/supersession, tool call sequencing, overhead and retrieved source citations before enabling team-wide. Keep GitHub canonical decisions authoritative and TencentDB derived.

## UPDATE merged upstream code in this exact window
- **llama.cpp #30397 merged Oct13 10:34:47 UTC**: Qwen3.8 Flash-Next MTP accepts image embeddings; author's image/text/image-repeat smoke passed. No full vision/OCR QA or M1 speed. https://github.com/ggml-org/llama.cpp/pull/30397
- **vLLM #60602 merged Oct13 07:30:19 UTC**: FP8 QSA attention KV on Ampere sm80/86 (Qwen3.8 Flash-Next). 8×A100 TP8+EP cache tokens 1.16M→2.13M; at concurrency16 higher prefix-cache hit and throughput (requests/s BF16 0.58–0.64 vs FP8 1.58–1.63) but different cache residency causes the gain; no same-context model computation TG advantage, attention kernel 0.92–1.14×. Not owner's SM120 RTX5070Ti nor TB4. https://github.com/vllm-project/vllm/pull/60602
- **vLLM #60797 merged Oct13 10:09:17 UTC**: speculative Mamba2 checkpoint was saving conv window too far into scratch. On source-controlled ~71K and ~11.6K prefix-hit tests with 5–7 draft tokens, baseline errors included 8/24,10/12,6/24,12/12 and 13/24 PD, all 0 after; no speed change. Recurrent export records only logical `conv_kernel-1` history, excludes draft scratch. Project51 Relay exact-window fixture reinforced. https://github.com/vllm-project/vllm/pull/60797
- **oMLX #4472 merged Oct13 09:24 UTC**: cap PLE prefetch Future count to worker limit; M5 Max 2,048-page synthetic 16.0877→11.6100ms, no end-to-end TG result. **oMLX #4464 merged 09:24 UTC**: remove extra mmap row copy; 8K full-model PP actually 2036→1957, TG 99.9→100.0, TTFT3.947→4.104s. Micro wins do not imply physical M1 PP. https://github.com/jundot/omlx/pull/4472 https://github.com/jundot/omlx/pull/4464
- **oMLX main Oct13 09:43/09:58**: bound batched array padding graphs; merge back-to-back messages for VLM models. Qualify multi-turn message ordering, but no model/hardware new TG. https://github.com/jundot/omlx/commit/64bf5d1ba633
- vLLM and SGLang also merged several model/backend/attention changes; none directly establishes exact dual-M1 PP2 numbers. The 02:13 EDT M1 Max #4496 author DFlash2 ~24.2 TG at actual ~133K is a **known prior source**, not a new benchmark this window.

## Negative checks
- Strata main-branch most recent commit predates window, open PRs above are not shipped; v0.1.43.1 remains the release candidate. Do not silently claim #2240, #2247, #2253 are in release.
- DS4 default head Oct7, **no new window commits** / no direct M1 PP2 proof; pi-vcc default head Oct12 05:27, no new commits; RaymondHuang KV fork default head Oct11. Web search retrieved older Qwen3.8/Swift Reddit threads, not new reproducible exact 128–262K Swift IQ3_S xhigh on owner's 5070 Ti.
- No native M1 Max physical tests run this turn, no remote CUDA/Metal checkpoint implementation, no experimental GitHub Actions launched, no user equipment modified.

## Updated engineering to-do
1. Prioritize **relay state interop** from #2240 network/ownership protocol and vLLM logical conv history, but first one checkpoint-based CUDA→MLX transfer with exact model layout, KL and transcript parity. Never infer TG scaling from stage-link.
2. Per-Mac dense 27B: oMLX #4496 existing exact M1 performance baseline; investigate #4508 batched DFlash and #4509 SSD pause only in an isolated M1 sandbox. B1/B2/B4 16/64/128K + tool success, output hashes, TTFT.
3. Lenovo: v0.1.42 control vs 0.1.43.1, actual context ladder, no Foresight; test malloc-trim and allocator ownership separately. Half-precision saved state is opt-in lossy; wait for KL/full agent quality.
4. Native SSD expert: A/B loader-only vs LES-only vs combined, I/O, memory residency and side effects. Only loader change proven important in #4507.
5. Pi control plane: check per-provider API accepted/rejected keys, memory injection provenance and user/team ACL; consider TencentDB MCP only when upstream merged.
6. Preserve canonical custom xhigh mixed-bit Flash transformer target / oQ5e cert comparator and explicit PLE/MTP precision ledger. **No target or confidence promotion without exact active topology evidence.**

**New strict research boundary: 2026-10-13 11:13:33 UTC.**
