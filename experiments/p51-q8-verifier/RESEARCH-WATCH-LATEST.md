# External runtime watch — 2026-09-17 23:56 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-18 02:28:04 UTC` through `2026-09-18 03:56:56 UTC`.

PRs, issues, and default-branch commits were explicitly screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Current Qwen3.8-Flash-Next Hugging Face/community and oMLX benchmark surfaces were also searched. Evidence time means substantive source/measurement time, not crawler, merge, rebase, label, or comment time.

## Executive result

**No exact active-topology dual-M1/TB4 Q5 receipt appeared. Numeric canonical targets do not move.**

Flash-Next remains:
- canonical quant lane: **Q5-class / eventual ~5.x BPW**
- hardware/topology: **2x M1 Max 64 GB / TB4**
- headline target: **40 tok/s sustained TG at ~128K active context**
- cold PP target: **400 tok/s**

However, this pass recovers a materially useful exact-M1 physical anchor and adds a new strict-window sparse-cache correctness result:

1. **RECOVERED OLDER EVIDENCE:** a full Qwen3.8-Flash-Next PLE-last GGUF on **one M1 Max 64 GB** reports about **21 tok/s at 128K** and about **200 tok/s prefill**, with the huge PLE table mmap/SSD-backed. A separate MTP sidecar gives about **24 tok/s on code**. This is low-bit Q2/IQ1 rather than Q5, so it strengthens the M1 silicon/runtime case without certifying the production quant lane.
2. **NEW:** vLLM #57477 shows that a sparse-indexer tail-cache stride bug can silently corrupt unrelated hot prefix-cache pages over time. The bug survives normal serving for a while and then progressively destroys cached answers. This is highly transferable to Project 51's QSA/indexer/cache qualification.
3. **RECOVERED CALIBRATION:** nominal `oQ5e` is not enough to identify a performance lane. Public M5 Max Q5 artifacts/recipes show substantially different deep-context TG, reinforcing that artifact/revision + recipe + fast-path state must be recorded with every receipt.

## RECOVERED OLDER EVIDENCE — exact M1 Max 64 GB long-context Flash receipt

Source:
- https://huggingface.co/whm0627/Qwen3.8-Flash-Next-177B-A3B-fits64GB-PLElast-GGUF
- benchmark commit: https://huggingface.co/whm0627/Qwen3.8-Flash-Next-177B-A3B-fits64GB-PLElast-GGUF/commit/2cbcd1e173ea46a98b51ff558d2166195f82257b

Configuration:
- Apple **M1 Max 64 GB**
- llama.cpp Metal, `-ngl 99 -fa on`
- full Qwen3.8-Flash-Next model
- Q2_K_XL PLE-last GGUF, 79 GB file; sibling IQ1_S 68 GB
- same quantized tensors as the source GGUF; PLE-last only reorders tensors so the large PLE/n-gram table can remain disk/mmap-backed
- reported wired/VRAM use about **44-48 GB**
- ~27 GB PLE/embedding table read on demand from SSD/mmap

Reported performance:
- Q2_K_XL decode: **~21 tok/s**
- prefill: **~200 tok/s**
- **128K context: same ~21 tok/s decode rate**
- MTP sidecar on structured/code output: **~24 tok/s**
- source says MTP yields roughly **27-41%** on structured code/JSON/repetitive output with 85-100% draft acceptance, but little benefit on free-form prose.

Small quality smoke:
- Q2_K_XL GSM8K: **37/40**
- IQ1_S GSM8K: **38/40**
- Q2_K_XL HumanEval: **20/20**
- IQ1_S HumanEval: **19/20**
- reported perplexity: **1.084 / 1.156** respectively.

Classification: **exact M1-generation / exact Flash-Next model-family physical receipt, but low-bit non-target quant and community benchmark methodology. Strong silicon/runtime/offload calibration; not Q5 production proof.**

### Project 51 interpretation

This is much more useful than a stronger-chip transfer result for one specific question: **can an M1 Max execute full Flash-Next at deep context without collapsing into single-digit TG?** This receipt says yes for a sufficiently low-bit, PLE-offloaded layout: about 21 TG at 128K on one M1 Max.

That materially strengthens the plausibility of the dual-M1 40-TG thesis because the target is no longer being inferred only from old ~8-13 TG single-M1 paths. But do **not** double 21:
- Q2/IQ1 is materially lighter than the target Q5;
- PP2 introduces TB4 transfer/bubbles;
- Q5 per-stage working sets and bandwidth differ;
- the community report does not provide our frozen workload/measurement protocol.

The correct takeaway is **higher architecture confidence, unchanged numeric target**.

### New implementation clue: physical checkpoint order can matter

The PLE-last repack does not requantize; it changes tensor ordering so expert weights remain contiguous for GPU residency while the huge PLE table remains mmap-backed and is touched on demand.

For oMLX we already have explicit SSD PLE machinery, so the literal GGUF trick is not directly portable. The transferable principle is that **checkpoint/storage layout is part of offload performance identity** when the runtime relies on mmap/page-cache behavior. Project 51 should record physical PLE shard/file layout and page-fault pattern in SSD-offload experiments, not only logical tensor placement.

## RECOVERED CALIBRATION — “Q5” alone does not define the performance lane

A separate public Q5 artifact:
https://huggingface.co/tls20/Qwen3.8-Flash-Next-oQ5e-mtp

reports on M5 Max 40c / 128 GB:
- 1K: **35.5 TG / 1,031 PP**
- 4K: **36.2 TG / 1,318 PP**
- 32K: **31.5 TG / 791 PP**
- 64K: **33.0 TG / 862 PP**
- 131,072: **25.8 TG / 904.7 PP**, peak 101.5 GB.

That differs sharply from the already-recorded M5 Max oQ5e receipt at **47.3 TG / 1,203 PP at 128K**.

The cards are not sufficiently controlled to infer a single cause: model artifact, mixed-precision allocation/imatrix provenance, oMLX version, MTP/recipe state, PLE policy, sampling/thinking state, and fast-path eligibility can all differ.

Classification: **recovered cross-artifact calibration, not a matched A/B.**

Durable rule: **quant label is not topology identity.** Every Q5 receipt must record exact artifact/revision/checksum and runtime recipe before comparison. Do not average nominally identical bit-width results.

A separate oQ5e community card (GBP-DE) also reports selected reasoning/constraint tests where Q5 was more robust than Q4, while other tests tied and Q4 was faster. Those are useful qualitative support for keeping Q5 as the quality lane but are not a standardized general-quality proof.

## NEW — vLLM #57477: padded sparse-cache stride silently corrupts hot prefixes

PR #57477, created **2026-09-18 02:39:06 UTC**, fixes GLM-5.3-Flash NVIDIA kpool tail-cache addressing.

Mechanism:
- the tail cache lives inside a padded indexer pool with a physical stride of **38,016 bytes** per block;
- the seed kernel incorrectly used a dense **2,048-byte** stride;
- a request therefore failed to seed its own tail block and instead wrote 2,048 bytes into another request's indexer region;
- prefix-cached blocks are not recomputed, so corruption accumulates across unrelated requests.

Kernel reproduction:
- physical tail view stride: `(19008, 512, 128, 1)` elements;
- main, tail block 200: own block remains unseeded; write lands at bytes `[409600, 411648)`, inside indexer block 10;
- fixed PR: write lands in block 200 bytes `0..2048` as intended.

End-to-end:
- GLM-5.3-Flash TP4 on **4x GB300**
- 14.5K-token cached system prompt
- 800-block pool forced to wrap quickly
- 8 rounds x 50 unrelated filler prompts
- watched 38 cached indexer pages.

Progressive damage on main:
- after 50 fillers: **16/38 pages modified**, 18.4 KB
- after 150: 21/38, 36.7 KB, lookup already wrong
- after 400: **30/38 pages modified**, 64.1 KB
- final seven lookups: **1/7 correct**.

With fix:
- **0 watched pages modified**
- final seven lookups: **7/7 correct**.

Classification: **new exact sparse-cache correctness receipt; non-target hardware/model but very strong transfer evidence.**

### Project 51 action

Add a cache-isolation qualification cell:
- snapshot a hot long prefix's QSA/indexer/cache pages;
- issue many unrelated requests until allocator/block IDs wrap;
- byte/hash compare the hot prefix state after each epoch;
- re-hit semantic fixtures throughout;
- assert logical block ID -> physical stride/offset mapping for every cache family.

A one-time successful prefix-cache hit is not enough. **Unrelated traffic must be unable to mutate cached sparse state.**

This extends the existing rule that physical span/group/write ownership is part of distributed-cache identity.

## NEW — vLLM #57475: fit can fail after KV admission because graph capture needs margin

Issue #57475, created **2026-09-18 02:32:19 UTC**:
- Qwen3.8-27B NVFP4
- RTX 5090 Laptop 24 GB / SM12x
- FlashInfer
- max model len 124K
- CUDA graphs.

At `--gpu-memory-utilization 0.98`:
- available KV: **2.97 GiB**
- KV capacity: **150,745 tokens**
- graph estimate: **0.46 GiB**
- engine passes KV admission, then real graph capture OOMs trying to allocate 136 MiB with only 120.88 MiB free.

At `0.97`:
- available KV: **2.73 GiB**
- capacity: **138,588 tokens**
- boots and serves.

Eager mode at 0.98 reportedly permits ~166K KV tokens but loses graph speed.

Classification: **new same-Qwen-generation fit/lifecycle evidence, not Flash/M1 evidence.**

Project 51 already separates model-live, allocator, workspace and staging memory. Strengthen that rule: **fit certification must include all post-admission compiled/graph/fast-path initialization**, not stop when model + KV allocation succeeds. On Apple, the analogous concern is compiled-kernel/cache/transient footprint rather than CUDA graph memory.

## NEW transfer-only items

vLLM #57478 (created 02:39 UTC) adds a fused DeepSeek-V4.1 router gate on MI355X/gfx950. Its kernel operation is **1.47-3.86x** faster than the runnable unfused baseline across measured M, but the PR explicitly has no serving dispatch and claims no model-level speedup. Useful kernel-mining evidence only; no target movement.

DS4 #1074 (created 03:47 UTC) broadens server parsing of `reasoning_effort` string values for Pi compatibility. No inference-speed evidence.

oMLX #3710 / #3290 commits landed just after the boundary, but their substantive measurements and investigations predate it. They are not relabeled new merely due merge/rebase timing.

llama.cpp's strict-window PR #29062 is an Intel SYCL large-register optimization and does not inform Apple Flash targets. mlx-serve's strict-window activity is media-generation related. No strict-window oMLX Flash PR/issue introduced a new target performance receipt.

## Target / confidence decision

### Flash-Next dual M1

**Hold 40 TG @ ~128K and 400 cold PP. Hold Q5-class as canonical quant.**

Confidence moves **up modestly** because the recovered physical M1 receipt demonstrates roughly 21 TG at 128K on one M1 Max with the full Flash model and practical PLE offload. The strongest remaining unknown is now even more specifically **Q5 PP2 economics over TB4**, not whether M1 silicon can sustain useful deep-context Flash execution at all.

Do not promote the target to 45-50:
- exact dual-M1 Q5 remains unmeasured;
- the 21-TG M1 anchor is Q2/IQ1;
- PP2/TB4 and distributed state correctness are still unresolved.

### Qualification changes

1. **Artifact identity gate:** nominal Q5 is insufficient; record exact artifact/revision/checksum and full runtime recipe.
2. **Cache isolation under churn:** hot prefix state must survive allocator/block-pool wrap caused by unrelated requests.
3. **Physical-stride assertion:** cache family logical block mapping must match actual padded/strided storage views.
4. **Checkpoint/offload layout:** record PLE physical file/shard ordering and page-fault/mmap behavior when offload is used.
5. **Post-admission fit:** fit is certified only after compiled/graph/fast-path initialization and representative first execution.

## Hard freshness boundary

`2026-09-18 03:56:56 UTC`
