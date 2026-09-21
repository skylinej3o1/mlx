# Project 51 research watch — 2026-09-21 17:48 ET

**Freshness boundary checked:** previous hard boundary **2026-09-21 18:51:47 UTC**. Search ran through the user's cutoff **2026-09-21 21:48:06 UTC**.

## Decision

**Flash 40-TG confidence moves modestly upward; targets themselves do not change.**

The decisive new information in this pass is recovered rather than exact-window: DGPP has a substantially stronger two-Spark Qwen3.8-Flash-Next implementation than the earlier SGLang recipe we had recorded. Its two-node NVFP4 lane reaches the 60-70+ TG range, and its September 21 long-context QSA campaign keeps effective speculative throughput around the low/mid-60s near 128K and around 60 near 260K with exact response parity.

That is strong enough to move the Project 51 engineering-confidence ladder while still taking a large transfer discount for GB10/CUDA/TP/RoCE versus M1/Metal/PP2/TB4:
- **>=40 TG @ ~128K: ~65% -> ~70%**;
- **>=45: ~40% -> ~45%**;
- **>=50: ~20% -> ~25%**;
- >=30 and >=35 unchanged;
- cold PP confidence unchanged.

Canonical goals remain **40 TG @ ~128K**, **400 genuinely cold PP**, and **>=38 AA-class behavior**.

## RECOVERED — DGPP proves the first 2-Spark result was not close to the decode ceiling

Sources:
- https://github.com/HawkBearPig/dgpp
- https://forums.developer.nvidia.com/t/dgpp-a-gb10-optimized-c-cuda-inference-engine/383406
- `benchmarks/results/2026-09-16-qwen-nvfp4-w2.md`

DGPP is a model/hardware-specific native C++/CUDA engine rather than a wrapper around vLLM/SGLang. Multi-node worlds use tensor parallelism over RoCE.

Current shipped Qwen3.8-Flash-Next NVFP4 world-2 configuration:
- 2x DGX Spark / GB10;
- `nvidia/Qwen3.8-Flash-Next-NVFP4`;
- FP8 dense stack encoded at load;
- mapped n-gram/PLE table;
- BF16 KV;
- MTP depth 1;
- 262,144-token pool;
- four request slots.

Measured single-request engine decode across five prompt classes:

| class | ms/pass | tok/pass | effective TG |
|---|---:|---:|---:|
| prose | 25 | 1.83 | 73.7 |
| code | 25 | 1.73 | 67.9 |
| json | 25 | 1.88 | 74.9 |
| math | 25 | 1.83 | 73.8 |
| chat | 26 | 1.59 | 62.1 |

At C4 the same mmap deployment reports **119.0-136.9 aggregate TG**. The corresponding one-Spark lane is **42.6-50.3 TG**, so the second Spark plus distributed execution provides substantial real headroom even though the scaling is not 2x.

Important: this does not identify PP2 as the reason. DGPP currently uses **TP over RoCE**, so it is evidence for distributed Flash headroom, not evidence that TP is appropriate for TB4.

## RECOVERED — DGPP exact QSA selection keeps 2-Spark Flash fast at deep context

Source file: `HawkBearPig/dgpp/benchmarks/results/2026-09-21-qwen-qsa-select.md`
Evidence commit: `1f357dad7f12`, timestamp **2026-09-21 04:14:08 UTC** — before the prior hard boundary, so classified as recovered older evidence.

The old long-context selector sorted every 2048-key tile and became severely underfilled/serial. At 131,072 pools, selection alone was **4.446 ms warm** while scoring was only **0.224 ms**. DGPP replaces this with an exact radix-boundary selector while preserving score arithmetic, tie rules, output ordering and graph shape.

Two-node model campaign: NVFP4, mapped PLE, FP8 dense, BF16 KV, depth-one MTP, YaRN factor 2. Each point is one cold + two cached requests, 256 generated tokens.

| prompt | old ms/pass | new ms/pass | reduction | cold prefill old/new |
|---:|---:|---:|---:|---:|
| 3,139 | 28.54 | 28.12 | 1.5% | 2.11 / 2.07 s |
| 31,670 | 31.31 | 28.04 | 10.4% | 20.74 / 20.32 s |
| **129,560** | **43.39** | **29.55** | **31.9%** | 98.62 / **93.16 s** |
| **260,062** | **59.38** | **31.36** | **47.2%** | 235.97 / **215.07 s** |
| **520,742** | **93.52** | **37.06** | **60.4%** | 732.40 / **655.18 s** |

Tokens/pass remains **1.85-1.92**. Therefore the new pass times imply approximately:
- 129.6K: **62.6-65.0 TG**;
- 260.1K: **59.0-61.2 TG**;
- 520.7K: **49.9-51.8 TG**.

All **15/15 response hashes** match baseline, including reasoning and usage; prompt hashes, token counts, decode steps and computed prompt-token counts also match.

### P51 consequence

This is the strongest recovered exact-family two-node long-context mechanism evidence currently in the file chain. It shows that a seemingly fundamental long-context falloff can actually be a specific QSA selection algorithm problem, and that fixing it can leave speculative throughput nearly flat through 260K.

P51 should explicitly profile:
- QSA scoring versus QSA selection separately;
- selected-block expansion and ordering;
- underfilled selection-grid occupancy as context grows;
- deterministic/tie-preserving exact top-k parity;
- per-stage QSA selection time under PP2 rather than treating sparse attention as one bucket.

## RECOVERED — clean two-Spark uncached prefill receipt

Source: `PixelML/qwen3-8-flash-next-sglang-2x-dgx-spark`.

The separate TP2/SGLang deployment measures client-observed, unique-prefix, one-request-at-a-time prefill with exactly one output token and **zero server-side cached prompt tokens**:

| target | actual prompt | TTFT | input tok/s |
|---:|---:|---:|---:|
| 1K | 1,046 | 0.4524 s | 2,327.78 |
| 4K | 4,103 | 1.4924 s | 2,758.65 |
| 16K | 16,471 | 5.5729 s | **2,960.12** |

This is stronger evidence that the earlier ~2.5K cold-PP number was not the exact ceiling, but it does **not** establish the 5-7K cold-B1 range previously speculated about.

DGPP's deep-context cold prefill in the QSA campaign is approximately:
- 129,560 / 93.16s = **~1.39K PP**;
- 260,062 / 215.07s = **~1.21K PP**;
- 520,742 / 655.18s = **~0.80K PP**.

So decode headroom is now strongly demonstrated; extreme cold-prefill headroom is less clear. P51's **400 cold PP** remains unchanged at ~70% confidence.

## NEW exact-window — vLLM #58020: scheduler/worker cache geometry can silently diverge

Created **2026-09-21 21:44:28 UTC**.

vLLM EngineCore can resolve a fine-grained hybrid prefix-match unit from all KV groups, but the worker currently does not receive that resolved value. The concrete in-tree geometry is attention block 16 + Mamba block 1600:
- engine resolves match/hash unit = **16**;
- Mamba worker locally derives = **1600** when `prefix_match_unit=None`;
- worker computes the recurrent checkpoint on the wrong grid;
- position floors to zero and the checkpoint is silently dropped.

### P51 rule

The coordinator owns resolved cache geometry. PP stages/workers must receive the exact resolved values for:
- prefix/hash unit;
- page/block geometry;
- recurrent/QSA checkpoint grid;
- target/draft cache grouping and offsets.

No worker may independently derive a different geometry after scheduler admission. If authoritative geometry is absent or incompatible, fail closed rather than silently dropping state.

## NEW exact-window — DGPP wide Qwen MTP serving correctness

DGPP commits inside this exact window merged PR #13 and #14.

PR #13 adds Qwen **C16/MTP3 with up to 64 verification rows** on two Sparks. Real NVFP4 validation reached 16 active requests with all API checks passing and identical rank operation-stream digests. The author explicitly claims **no throughput improvement**.

PR #14 adds conservative sparse physical-slot compaction. Final four-node validation covered **50,890 positions** with **zero NLL differences and zero top-1 changes** and successful C1/C2/C4/C8/C16 API serving. Unrestricted compaction had failed the real-model numerical gate, so the final policy intentionally contracts only within validated graph families and makes no performance claim.

Durable takeaway: row compaction/remapping and graph-family choice are part of numerical identity. P51 should certify them, not treat them as scheduler-only transformations.

## Other exact-window / checked surfaces

- vLLM main merged no new exact Apple/Flash performance commit in this window. Fresh #58020 is the main distributed-state finding.
- vLLM #55390 was active with hybrid-MTP draft cache-group annotation and B300 validation; its measurements are not timestamped tightly enough to count as NEW here. Treat it as supporting evidence that draft-containing cache groups require explicit identity under offload.
- `antirez/ds4`: no commits in-window; Qwen3.8 Flash Strix Halo PR remained active but its benchmark body is older.
- `jundot/omlx`: no runtime commits in-window; activity was mostly UI. No fresh M1/Flash TG receipt.
- `ggml-org/llama.cpp`: only cpp-httplib merged in-window. Older hybrid checkpoint/save and long-context issues were reviewed but are not exact-window performance evidence.
- `incoai/splash`: no new commits in-window; no Apple7/M1 backend appeared. Apple-family-8 request remains open.
- `ddalcu/mlx-serve`, Kadir, MTPLX, APEX, ik_llama, AutoRound: no qualifying performance commit in-window.
- Web/community/Hugging Face search found no exact **2x M1 Max / TB4** Flash receipt.

## Target / confidence impact

Canonical targets unchanged:
- Flash: **40 TG @ ~128K**;
- cold PP: **400**;
- production floor: **>=38 AA-class**, preferred 39-40.

Updated Flash ~128K planning ladder:

| Mature B1 TG | confidence |
|---:|---:|
| >=30 | ~95% |
| >=35 | ~85% |
| **>=40** | **~70%** |
| >=45 | ~45% |
| >=50 | ~25% |

Cold-PP confidence remains **~70% for >=400**.

## New hard boundary

**2026-09-21 21:48:06 UTC**
