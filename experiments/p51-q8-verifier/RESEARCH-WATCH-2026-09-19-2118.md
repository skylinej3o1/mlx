# Project 51 external runtime watch — 2026-09-19 21:18 ET

**Hard freshness window:** strictly after **2026-09-19 22:24:30 UTC** through **2026-09-20 01:18:00 UTC**.

This watch continues from the actual repository boundary, not from an earlier conversational cutoff. Substantive source timestamps are used; merge/rebase/bot/crawler timestamps do not by themselves create new evidence.

## Decision

**No numeric target change.** Flash-Next planning remains:

| Metric | Planning confidence |
|---|---:|
| >=35 TG @ ~128K | ~85% |
| >=40 TG @ ~128K | ~65% |
| >=45 TG | ~40% |
| >=50 TG | ~20% |
| 400 cold PP | ~70% |

The interval adds important **multi-sequence QSA correctness**, **incremental QSA-summary caching**, **memory-pressure lifecycle**, **speculative-state sizing**, and **cold-cache benchmark hygiene** evidence. It does **not** add the missing exact 2x M1 Max / TB4 / ~128K / custom-quant / MTP+PP2 throughput receipt, so it does not justify promoting or cutting the headline forecast.

## NEW — llama.cpp #29166: Qwen4Exp QSA block visibility can cross-contaminate concurrent sequences

Source: https://github.com/ggml-org/llama.cpp/pull/29166

Draft PR created **2026-09-20 00:54:52 UTC**; head commit authored **00:19:09 UTC**.

The Qwen4Exp / Flash-Next per-block `blk_bias` path in `set_input_qsa` indexed per-sequence bid arrays by block number even though those arrays are indexed by bid. In a unified cache with more than one live sequence, block number and bid no longer coincide. A block can therefore inherit another sequence group's visibility: one sequence's own block can be masked while another sequence's block passes.

The fix builds an inverse **block -> owning bid** map once per ubatch and uses it for both ownership and tail comparisons. Single-sequence caches keep the old correspondence.

Reproduction under concurrent requests with two live sequences sharing a stream:

- before: **2/4** attempts answered correctly; failing turns could behave as if the latest user input were empty;
- after: **4/4** correct.

**Project 51 rule:** QSA visibility metadata is keyed by **sequence identity + block identity**, not by positional/block-array coincidence. Multi-row certification must include overlapping position ranges from independent live sequences and assert that selected blocks/summary rows are sequence-local.

This is exact model-family correctness evidence, not M1/TB4 speed evidence.

## RECOVERED + strict-window update — llama.cpp #28699: incremental pooled QSA summaries

Source: https://github.com/ggml-org/llama.cpp/pull/28699

The baseline PR predates this window, so its performance result is **recovered older evidence**, not NEW. It identifies a directly relevant long-context cost: Qwen4Exp QSA was regathering/recomputing block-summary keys over the whole cached context every token in every QSA layer. The branch instead stores one f32 summary row per completed position block/layer and only pools newly completed blocks.

On an 8-GPU Qwen3.8-Flash-Next UD-Q3_K_XL setup with Q8 KV, MTP n_max=2 and ctx=131072:

| Depth | pooled OFF | pooled ON | Delta |
|---:|---:|---:|---:|
| 63K | 22.25 TG | 24.33 TG | **+9.3%** |
| 114K | 25.41 TG | 27.80 TG | **+9.4%** |

Prefill was unchanged within noise; greedy output was bit-identical and prefix rollback matched fresh execution. These percentages do **not** transfer numerically to M1.

The original port also found that placing all pooled-indexer layers in one buffer caused other split devices to read/write that buffer across interconnects and cost roughly **2x decode** on its 8-GPU test; per-device indexer buffers recovered the loss. That is strong topology guidance for Project 51: **QSA summary/indexer state should be stage-local on PP2 rather than bouncing over TB4.**

A strict-window comment at **2026-09-20 00:55:49 UTC** reports a second concurrency defect in the pooled path: rows keyed only by position block let two sequences occupying the same positions overwrite one another. Instrumentation on a failing turn recorded `cross_seq_rows=1` and `foreign_bids=140`. Laying pooled rows out per sequence plus own-block-only filling changed the same 8.8K-main + small-concurrent-request shape from **2/4 wrong to 4/4 correct**.

**Project 51 action:** add an MLX experiment for incremental QSA block-summary caching, but require per-sequence row ownership and stage-local buffers from the first implementation.

## NEW — Splash #13: memory pressure must preserve the resumable recurrent-state publication

Source: https://github.com/incoai/splash/pull/13  
Merged as `09409b5d8d05` at **2026-09-20 00:34:23 UTC**.

Splash changed Apple host-memory admission and cache reclaim after finding two lifecycle problems.

First, startup had required the whole model package plus roughly 10% of physical memory to be reclaimable before loading, even though mapped weights become resident gradually. A cited 35B package could require **27.3 GiB reclaimable on a 64 GiB Mac**, causing machines that later ran successfully to be refused. The replacement uses measured availability plus a capped macOS reserve and allocation/submission-time guards during bootstrap.

Second, periodic pressure reclaim could evict the only published recurrent state while the engine was idle. Hybrid models cannot resume from KV alone without that state, so the next request replayed the entire prompt.

On an **M5 Pro 48 GiB**, 27B package, primed 8K prompt, 15 s warning-pressure hold:

| | before | after |
|---|---:|---:|
| State survives pressure | no | yes |
| Cached follow-up | 22.2 / 21.2 s | **3.03 / 3.02 s** |
| Resume | no cache hit | **8,160 tokens resumed** |

A strict-window correction at **23:57:08 UTC** establishes the reclaim priority: a newer disposable speculative checkpoint must not displace the warmed ordinary resume point. Preserve the newest ordinary publication under advisory pressure; only use a checkpoint as the resume floor if no ordinary state exists. A waiting request or critical pressure may still reclaim it.

Splash still targets newer Apple GPU families, so this is lifecycle/architecture transfer evidence rather than an M1 kernel receipt.

**Project 51 rule:** reclaim semantic value, not merely LRU bytes. Disposable speculative checkpoints go before the newest reusable ordinary recurrent-state publication when pressure is advisory.

## NEW — Splash #15: preserve completed prefill work when concurrency shrinks

Source: https://github.com/incoai/splash/pull/15  
Created **2026-09-20 00:15:03 UTC**, merged as `298852ec603a` at **00:39:16 UTC**.

When KV growth failed, the engine could suspend a request already deep into prefill while keeping a resident peer that had not started. The fix chooses a victim across runnable residents using request priority, phase and actual completed work, while retaining each request's own resume target.

M5 Pro 48 GiB, two distinct **48,022-token** 27B requests, **20 GiB Metal limit**:

- fixed branch: both complete in **279 s** with exactly **96,044 physical prefill rows**;
- old path: one completes at **265.8 s**, test stopped at **360 s** after **129,942 rows**, showing large duplicated prefill work.

This is targeted recovery validation, not a throughput benchmark.

**Project 51 rule:** record **physical prefill rows executed** separately from logical prompt tokens. PP2/memory-pressure policies that replay already-computed prompt work can make PP/TTFT figures misleading even when nominal model PP is unchanged.

## NEW — vLLM #57721: speculative width must be included in recurrent-state page sizing

Source: https://github.com/vllm-project/vllm/issues/57721  
Created **2026-09-19 22:30:23 UTC**.

A Mamba-hybrid startup path planned padded recurrent pages without `num_spec`, while the actual recurrent state included speculative widening. On the reproduced Granite hybrid:

- planned padded page: **819,200 B**;
- base recurrent page: **806,400 B**;
- incidental slack: **12,800 B / 1.59%**;
- each speculative token adds **6,656 B**;
- n_spec=1: **813,056 B**, fits;
- n_spec=2: **819,712 B**, exceeds the planned page and asserts.

Increasing the page/block geometry allowed n_spec=2 to start and generated the same output as n_spec=1, isolating the failure to sizing.

**Project 51 rule:** fit/admission and recurrent workspace geometry are qualified at the **maximum verify/draft width actually enabled**. A target-only or depth-1 fit does not certify depth-2+ MTP.

This is non-Flash transfer evidence and does not move targets.

## STRICT-WINDOW Apple confirmation — llama.cpp #28433: do not size MTP draft context from total target context

Source: https://github.com/ggml-org/llama.cpp/issues/28433

The issue itself predates the window. A **2026-09-19 23:41:23 UTC** comment from an M3 Pro / Metal user confirms that the current draft-MTP path allocates draft KV context at the target model's total `n_ctx`, even where per-sequence / bounded draft history would be sufficient. The provided Qwen3.8-27B repro uses parallel=3, q8 KV and draft-MTP.

This strengthens an existing Project 51 rule rather than creating a new one: **target context reserve and draft/verifier reserve are separate memory identities**. At 128K+ target context, MTP should not blindly inherit the entire target reserve.

## NEW — vLLM #57727: a successful prefix-cache reset can still be warm

Source: https://github.com/vllm-project/vllm/issues/57727  
Created **2026-09-19 22:44:24 UTC**.

With a CPU offload connector, `POST /reset_prefix_cache` returned success and cleared the GPU tier but left CPU-offloaded blocks available. In a 1,024-token reproducer, the first request after reset showed **1,008 external cache hits** while GPU hits remained zero. A fresh `cache_salt` produced the genuinely cold path.

**Project 51 cold-PP rule:** a cold run must prove all reusable tiers are cold—Metal/GPU KV, host/offload tier, SSD/prefix cache, recurrent-state publication, prompt/MTP sidecars—or use a unique cache namespace/salt and assert zero hits. An API “reset succeeded” response is not sufficient.

This is especially relevant to the **400 cold PP** target.

## NEW — llama.cpp #29163: cancellation can destroy reusable prefix state

Source: https://github.com/ggml-org/llama.cpp/issues/29163  
Created **2026-09-19 22:32:33 UTC**.

A user reports that aborting an in-flight HTTP generation to steer an agent causes the server to discard its KV state, so the next request re-prefills the whole shared conversation. Their log shows cancelled work followed by prompt processing from the beginning.

This is not a measured Project 51 performance result, but it reinforces the lifecycle gate for Hermes/agent workloads: cancellation/interruption must either preserve a verified reusable prefix checkpoint or explicitly account for the replay cost. Add cancellation + immediate continuation to the cache/state qualification matrix.

## CURRENT community quant surface — heterogeneous Flash-Next MLX quantization exists, but is older evidence

Current Hugging Face inspection found `Vontra/Qwen3.8-Flash-Next-MLX-oQ4`, a sensitivity-guided mixed-precision MLX conversion:

- 4-bit affine base;
- **228 protected modules at 5/8-bit**;
- group size 32;
- **111.69 GB / 104.02 GiB** weight payload;
- measured M3 Studio sustained decode around **27 tok/s** on the published card.

The commit history shows the relevant card/performance material predates this strict window, so it is **not NEW**. It is nonetheless useful precedent for Project 51's APEX/I-Balanced-style goal: Flash-Next MLX already supports a practical “low-bit mass + protected sensitive modules” artifact design. It does **not** prove our desired ~4.6-4.9 hot-trunk BPW can match oQ5e/BF16 behavior, and its whole-file payload is not directly comparable because Project 51 separates PLE/ngram placement from hot-trunk BPW.

Sources:
- https://huggingface.co/Vontra/Qwen3.8-Flash-Next-MLX-oQ4
- https://huggingface.co/Vontra/Qwen3.8-Flash-Next-MLX-oQ4/commits/main/README.md

## Required upstream scan — no qualifying new speed receipt

- **DS4:** no default-branch commit in the strict interval; no new post-boundary #952/#1056 comments. No new exact-M1 ~128K MTP receipt.
- **vLLM:** one default commit in-window, SM100 FP8 DSA/MLA cache-scale fix, unrelated to Project 51's Apple target. The relevant new items are #57721 and #57727 above.
- **oMLX:** no new default-branch commit in-window. #3594 only received a non-substantive “Thoughts?” comment after the previous boundary; no new 1M/Flash measurement. #3533/#3767 had no new substantive post-boundary comments.
- **mlx-serve:** its Linux/Vulkan port landed before the current boundary; no qualifying post-boundary Apple/Flash result.
- **llama.cpp:** default-branch commits in-window were parser/tooling work, not Flash performance. Draft #29166 and lifecycle issue #29163 are relevant as above.
- **Splash:** #13/#15 are the meaningful new Apple-runtime changes; no M1 backend appeared.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no new activity.
- **Community Flash-Next:** no new exact dual-M1/TB4 or exact-M1 ~128K receipt found in the cutoff window.

## Durable qualification changes from this watch

1. QSA pooled/visibility state is **sequence-local**; certify overlapping concurrent sequences.
2. Prototype **incremental QSA block-summary caching** and keep its storage stage-local under PP2.
3. Memory-pressure reclaim preserves the newest reusable ordinary recurrent-state resume point ahead of disposable speculative checkpoints under advisory pressure.
4. Track **physical prefill rows** vs logical prompt tokens to expose replay amplification.
5. Size recurrent/cache/workspace state at maximum enabled speculative width/depth.
6. Keep target and draft/verifier context reserves independent; do not inherit full target n_ctx blindly.
7. A cold PP run proves **every cache tier cold** or uses a fresh namespace/salt with zero-hit telemetry.
8. Test cancellation/interruption followed by immediate continuation for prefix/state reuse.

## Target impact

**None.** The architecture story improves—especially the case for incremental QSA summaries, stage-local indexer state, and memory-headroom-aware serving—but the new evidence is mostly correctness/lifecycle or non-M1 transfer evidence.

The decisive missing receipt remains unchanged: **the intended ~4.6-4.9 hot compute trunk at ~128K on 2x M1 Max 64 GB / TB4, first target-only and then with MTP, with real PP2 stage occupancy/bubbles, acceptance/tokens-per-cycle, QSA/indexer behavior, cache-tier state, and TB4 traffic recorded.**

**New hard boundary: 2026-09-20 01:18:00 UTC.**
