# Project 51 external runtime watch — 2026-09-20 09:58 ET

**Hard freshness window:** strictly after **2026-09-20 10:43:46 UTC** through **2026-09-20 13:58:56 UTC**.

## Decision

**No numeric target/confidence change.** Keep **40 TG @ ~128K / 400 genuinely cold PP** on 2x M1 Max 64 GB / TB4.

## NEW — DS4 #1089: rewind live sessions instead of re-prefilling agent history

Source: https://github.com/antirez/ds4/pull/1089  
Updated **2026-09-20 13:33:47 UTC**.

DeepSeek V4.1 tool loops previously lost live-state reuse whenever sampled reasoning/tool bytes diverged from the client's re-rendered history. The PR keeps an 8192-position per-layer raw recovery ring and rewinds compressed/index state to the longest safe shared prefix.

M5 Max 128 GiB / Metal, ~21K-token 3-turn tool chat:

- one-slot turn 2: re-read **21,357 tokens / 54.6 s -> 95 / 7.3 s**; total **66.8 -> 20.8 s**;
- batched-session-2 turn 2: **21,357 / 197.6 s -> 95 / 7.4 s**; total **218.2 -> 26.5 s**;
- batched turn 3: **21,445 / 196.3 s -> 89 / 6.9 s**; total **215.0 -> 17.8 s**;
- concurrent title call: **204.6 -> 13.5 s**;
- batched 3-turn total: **631.2 -> 245.4 s**.

Cold prefill did not regress. With one slot, an auxiliary request can steal the only live session and make the next turn cold.

**P51:** `sup` should maintain a **rewindable live agent session**, not only immutable prefix caches. Retain enough recurrent/QSA recovery history for safe truncation after tool/client divergence and reserve >=2 live slots if auxiliary calls may evict the primary state.

## NEW MERGE — mlx-serve live memory re-admission + batched MTP

Source: https://github.com/ddalcu/mlx-serve/commit/06d53afb948b  
Commit **2026-09-20 12:29:27 UTC**.

Four simultaneous 64K requests were all admitted against the same stale free-memory snapshot; the fourth could exceed wired memory and kernel-panic macOS. Requests are now re-billed against **live memory immediately before prefill**.

M4 Max evidence in the same commit:

- MTP lanes as rows of one head forward: **109 -> 119 aggregate tok/s at N=4**;
- concurrency policy with MTP: **64 -> 122 tok/s** for four streams;
- when DFlash is loaded, a request with peers switches to MTP because MTP slots batch;
- auto-depth below 8K KV reported roughly +2% on code/prose.

**P51:** admission is an execution-time live-headroom decision per 64-GB node. Batch MTP head rows across lanes/requests where possible; DFlash remains B1-optional rather than the concurrency path.

## NEW — Splash #36: measured Apple9 prefill tile policy

Source: https://github.com/incoai/splash/pull/36  
Created **2026-09-20 12:49:05 UTC**.

M4 Max 32-core / Apple9 / Qwen3.8-27B-Splash: N128/four-simdgroup Q4 prefill tiles beat N256/eight-simdgroup across measured row counts.

- cold 2K **10070 -> 9706 ms (-3.6%)**
- 10K **50099 -> 48253 (-3.7%)**
- 50K **288691 -> 278286 (-3.6%)**
- 128K **925667 -> 903952 (-2.3%)**
- 176-row continuation **1260 -> 1210 (-3.9%)**
- decode unchanged; transcripts bit-identical.

**P51:** copy the measurement method, not M4 constants. Tune M1 prefill at actual contention/continuation rows (64/256/512/1024/2048), not only full chunks.

## NEW exact model-family evidence — vLLM #57128 Qwen3.8-27B MTP prefix corruption

Source: https://github.com/vllm-project/vllm/pull/57128  
Updated **2026-09-20 13:29:06 UTC**.

Qwen3.8-27B-NVFP4, native MTP k=1, prefix caching, 131072 max context, 2x RTX 5060 Ti. Mamba prefix lookup ignored `drop_eagle_block`, allowing the newest recurrent checkpoint—potentially containing rejected draft positions—to be reused.

Correct fix: scan normally, skip only the newest matched checkpoint when speculative drop is required, then use the next older committed checkpoint. Blindly shrinking the token ceiling can land between sparse recurrent checkpoints and produce zero hits.

Live ~24K shared-prefix case: warm requests **~77 s -> 30-32 s**, with **15,440 / ~18,528** available tokens genuinely reused.

**P51:** rejected speculation taints the newest recurrent/QSA checkpoint until commit. Cache lookup must understand checkpoint topology, not apply a generic token margin.

## NEW/UPDATE — observability and runtime identity

- vLLM #56810 merged **10:58:55 UTC**: non-prefix-cacheable scratch/QSA-tail groups are excluded from offload. Cache-class separation is now merged precedent.
- vLLM #43310 merged **12:21:33 UTC**: per-request speculative metrics can be returned by the generate API. P51 traces should expose proposed/accepted counts, acceptance, effective tokens/cycle, depth and park/re-entry per request.
- vLLM #56742 updated **13:57:03 UTC**: Qwen4Exp MTP hidden buffer is explicitly allocated on configured device, target Triton kernels join warmup, and config layer-type spelling is normalized so sparse/QSA layers classify correctly.
- vLLM #56698 updated **13:57:03 UTC**: pinned KV capacity must still profile activations/allocator retention. In its different-GPU setup a **3.53 GiB** unmargined bound still OOMed at concurrency 4 while **3.07 GiB** completed. Profiled max is an upper bound, not a safe setting.

## NEW Splash agent-preparation work

Merged around **12:29 UTC**:

- #32 bounded exact rendered-text tokenization reuse with single-flight concurrent encodes;
- #33 phase latency histograms for HTTP/preparation/tokenization/native queue/token delivery;
- #34 includes token-mask waiters in prefill contention budget;
- #35 compiles independent grammars outside the cache lock and single-flights identical cold compilations.

**P51:** `sup` can prewarm stable tokenization/grammar/tool-schema artifacts in addition to model state, while separately measuring preparation, queue, prefill and first-token latency.

## Cutoff note

vLLM #54335 fixed-token prefill scoring was updated at **14:00:05 UTC**, after this user's **13:58:56 UTC** cutoff. It is a watch item for the next pass and is not used here.

## Screened / no target-changing evidence

- DS4 default branch: no new default commit; #1089 is PR evidence.
- oMLX: no new default-branch Flash performance commit.
- llama.cpp: no P51-relevant post-boundary default commit.
- Kadir repos: no activity.
- MTPLX: no post-boundary commit.
- APEX: no post-boundary commit.
- No new exact **2x M1 Max 64 GB / TB4 / ~128K / P51 mixed quant + MTP** physical throughput receipt.

## Target impact

**No numeric or confidence change.** The major gain is architectural confidence in rewindable warm agent sessions, which can transform practical tool-loop latency without being mislabeled as cold PP.

**New hard boundary: 2026-09-20 13:58:56 UTC.**
