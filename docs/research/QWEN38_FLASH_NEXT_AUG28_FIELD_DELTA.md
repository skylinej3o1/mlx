# Qwen3.8-Flash-Next Aug-28 field delta

Status: **FRESH FIELD EVIDENCE / high leverage for MXFORGE 2x M1 Max planning**

Updated: 2026-08-28 late morning ET.

This note captures the high-signal runtime developments that appeared after `QWEN38_FLASH_NEXT_DAY2_RUNTIME_DELTA.md`. The ecosystem changed materially in less than a day. The most important new evidence is now: exact/direct Metal QSA, much faster cold SSD-PLE gathering, native NextN/MTP on llama.cpp, recurrent-state rollback fixes, mixed-length continuous-batching fixes, context-derived `ngram-mod` speculation, and an adjacent Qwen3.8-27B adaptive-KV result on RTX 5070 Ti.

## Executive delta

1. **Upstream llama.cpp now has merged Qwen3.8-Flash-Next support.** PR #27742 merged the `qwen4exp` architecture with GDN, QSA, PLE, vision and required quantizer fixes.
2. **Native Flash-Next NextN/MTP now has direct Metal evidence.** llama.cpp PR #27836 reports an M3 Max 128GB moving from 27.43 tok/s target-only to 37.22 tok/s at draft depth 2 and 38.83 tok/s at depth 3; a broader code sweep reaches 40.01 tok/s at depth 3. Coding benefits strongly; prose does not.
3. **oMLX PR #3244 substantially raises the Apple QSA ceiling.** On M3 Ultra 256GB, exact direct sparse QSA gives ~886-896 tok/s cold prefill at 20-50K and remains ~859 tok/s at 150K. Native decode is 35.90 tok/s. Lightning MTP depth 5 reaches 82.31 tok/s at 99.5% acceptance on the reported 10K-code workload.
4. **oMLX PR #3235 independently validates the MXFORGE SSD-PLE planner thesis.** On M5 Max 128GB with a cold page cache and SSD-backed PLE, batching/advising/deduplicating n-gram row reads raises cold prefill from 256.7 -> 931.7 tok/s at 1K, 376.3 -> 1120.1 at 4K, 547.0 -> 1119.4 at 8K, and 674.3 -> 1029.5 at 16K without increasing peak memory.
5. **PLE is part of speculative recurrent state and must roll back exactly.** oMLX PR #3232 found that rejected Lightning-MTP drafts could leave PLE n-gram history and short-convolution state ahead of the committed prefix even when inherited QSA/GDN rollback was correct. The fix transactionally restores PLE state and validates through 128K retrieval tests.
6. **Mixed-length agent serving is actively being hardened.** oMLX PR #3246 fixes QSA singleton->batch conversion, ragged QSA offsets, MTP mid-cycle joins and trimmed indexer arrays. A 14K request generating 500 tokens completed while four shorter requests joined mid-flight under Flash-Next + Lightning MTP.
7. **Context-derived `ngram-mod` speculation is a serious second speculation lane.** A controlled DGX Spark paired test reports 27.26 -> 82.61 server decode tok/s aggregate and 2.49x wall-time speedup, with exact outputs in all four cases. Copy/edit-heavy cases can exceed 100 tok/s; novel code can get essentially no gain.
8. **Distributed Flash-Next MTP remains the major unsolved 2x-M1 risk.** oMLX Cluster v2 work reports Qwen TP2 MTP still fail-closed after a physical qualification stalled at the first distributed `return_hidden` / rollback graph. Single-Ultra MTP numbers must not be transferred directly to Thunderbolt TP2.
9. **Adjacent 27B memory-hierarchy evidence is strong.** An experimental llama.cpp adaptive-KV branch on RTX 5070 Ti 16GB runs Qwen3.8-27B around 15 tok/s at ~205K context and ~10 tok/s near 262K by keeping authoritative KV in system RAM and using a VRAM prefetch ring. This is not Flash-Next, but it reinforces MXFORGE's broader principle: capacity should be treated as a tiered residency/prefetch problem rather than a binary fit/no-fit problem.

## 1. Upstream llama.cpp Flash-Next support is real now

PR #27742 merged on 2026-08-27:

- architecture: `qwen4exp` / Qwen3.8-Flash-Next;
- Gated DeltaNet path;
- QSA sparse attention;
- PLE `get_rows` handling;
- hyper-connections;
- vision path;
- required quantizer/model-loader fixes.

The PR also provides useful correctness anchors: below the QSA sparse crossover, QSA vs dense is bit-identical in BF16/F32; above the budget, the sparse selection path is validated against the reference rather than treated as a generic dense fallback.

Source:
- https://github.com/ggml-org/llama.cpp/pull/27742

## 2. Native llama.cpp MTP / NextN: direct Metal result

PR #27836 adds `--spec-type draft-mtp` for Flash-Next and exports the official one-layer MTP head.

Hardware / setup:

- M3 Max 128GB;
- Qwen3.8-Flash-Next UD-IQ4_XS;
- context 8192;
- Flash Attention on;
- temperature 0.

Fresh 300-token code prompt:

| Mode | Acceptance | Decode | Gain |
|---|---:|---:|---:|
| target-only | - | 27.43 tok/s | - |
| MTP depth 2 | 89.2% | 37.22 tok/s | +35.7% |
| MTP depth 3 | 85.7% | 38.83 tok/s | +41.6% |

Wider code/prose sweep:

| Depth | Code | Prose |
|---:|---:|---:|
| 2 | 38.66 tok/s, 93.6% accept | 29.38 tok/s, 69.1% accept |
| 3 | **40.01 tok/s, 89.6% accept** | 28.22 tok/s, 62.7% accept |
| 4 | 38.43 tok/s, 85.9% accept | 25.65 tok/s, 54.2% accept |

The key structural finding is more important than the raw speed: the MTP combiner must operate **per hyper-connection stream on the wide state**. Collapsing the four streams first dropped acceptance from roughly 89.6% to 48.1% and became a net slowdown.

The PR reports temp-0 byte-identical output with MTP on/off for the tested depth-2/depth-3 Metal runs, while correctly warning that routing/reduction-order changes can still perturb a quantized MoE trajectory on other backends.

Source:
- https://github.com/ggml-org/llama.cpp/pull/27836

A separate alternative PR (#27842, closed in favor of the active path) is still useful engineering evidence. On Ryzen AI Max+ 395 / Vulkan it measured ~25.2 -> 41.1 tok/s at depth 3 and identified a critical recurrent-rollback requirement: missing convolution-state rollback slots could collapse acceptance and trigger pathological full state restore/replay.

Source:
- https://github.com/ggml-org/llama.cpp/pull/27842

## 3. oMLX exact direct QSA changes the Apple long-context ceiling

oMLX PR #3244 (`perf(qwen4): flatten exact QSA prefill and accelerate Lightning MTP`) is the most important new Apple-side result.

Hardware / model:

- M3 Ultra 256GB;
- 819 GB/s memory bandwidth;
- `Qwen3.8-Flash-Next-oQ4e-mtp`;
- resident packed PLE;
- batch 1;
- unique salted cold prompts;
- MTP/DFlash/ANE/SpecPrefill disabled for baseline.

Cold prefill:

| Prompt | Before | Direct QSA | Gain |
|---:|---:|---:|---:|
| 20K | 631.15 | **886.09** | +40.4% |
| 50K | 619.48 | **895.83** | +44.6% |
| 100K | - | **877.44** | - |
| 150K | - | **858.80** | - |

The 50K -> 150K taper is only ~4.1%.

Sustained 10K + 500-token decode:

| Mode | Decode | Acceptance |
|---|---:|---:|
| native, MTP off | **35.90 tok/s** | - |
| Lightning MTP depth 5, cold | **82.31 tok/s** | 99.5% |
| Lightning MTP depth 5, warm | **82.05 tok/s** | 98.8% |

The implementation is not a lossy QSA approximation. It adds:

- cached normalized/rotated QSA block state;
- native FP32 index scoring + deterministic top-512 selection;
- direct sparse-GQA Metal kernel for the production `24q / 2kv / D256` geometry;
- chronological selected block IDs consumed directly without dense score or gathered-K/V materialization;
- FP32 QK, online softmax and PV accumulation;
- exact/fail-closed projection paths;
- official/composed fallback for unsupported shapes, batching, multimodal positions and target verification.

Reported production-shape attention differs by at most one BF16 output ULP from the portable reduction order, while qualified end-to-end greedy tokens/cache state remain identical.

Source:
- https://github.com/jundot/omlx/pull/3244

### MXFORGE implication

The prior `~275-350 tok/s optimized SSD PLE @ ~30K` forecast should be treated as **reopened**, not blindly promoted. The M3 Ultra is not an M1 pair and this benchmark keeps PLE resident. However, the result proves that QSA itself can sustain near-flat ~900 tok/s long-context prefill on Apple when the gather/materialization path is removed. Combined with the SSD-PLE result below, the old PP ceiling is likely conservative if comparable kernels transfer to M1.

Do not assign a new 2x-M1 PP number until measured. Add direct QSA to the first-tier port list.

## 4. SSD PLE planner: independent validation of the exact idea

oMLX PR #3235 attacks the cold SSD n-gram gather on M5 Max 128GB with `Qwen3.8-Flash-Next-oQ4e-mtp`, PLE SSD offload enabled and page cache purged before each run.

| Prompt | Before | After | Speedup |
|---:|---:|---:|---:|
| 1K | 256.7 | **931.7** | 3.63x |
| 4K | 376.3 | **1120.1** | 2.98x |
| 8K | 547.0 | **1119.4** | 2.05x |
| 16K | 674.3 | **1029.5** | 1.53x |

Peak memory remains ~72-79GB.

Measured cold gather cost on one 512-token chunk falls from **181.3 us/row -> 16.6 us/row**.

Root cause and fix map almost exactly to the MXFORGE planner hypothesis:

- model asks for 16 PLE rows/token;
- naive path serially faults tiny rows from 16KB macOS pages;
- collect page ranges for the batch before reading;
- issue advisory `madvise` in parallel;
- bucket by shard via `searchsorted`/`argsort`;
- deduplicate repeated rows;
- read each distinct row once per shard.

This does **not** yet prove the final whole-prompt async double-buffered ceiling. It does prove that the old row-by-row SSD penalty was largely an implementation artifact rather than a fundamental SSD bandwidth limit.

Source:
- https://github.com/jundot/omlx/pull/3235

### Updated PLE priority

Keep the existing production ladder:

1. BF16 SSD correctness ruler;
2. Q5_1 / ~6-bit SSD primary production candidate;
3. Q8 SSD quality control if ~6-bit fails coding certification.

But move the access planner from “nice optimization” to **mandatory first-class runtime work**:

```text
prompt token IDs
 -> exact bigram/trigram hashes
 -> dedupe rows/pages
 -> group by shard + SSD locality
 -> advise/coalesce reads
 -> async prefetch
 -> overlap with GDN/QSA compute
```

## 5. PLE rollback is part of speculative correctness

oMLX PR #3232 identifies a subtle but critical Flash-Next-specific speculative bug.

A verifier forward processes one confirmed token plus draft tokens. The inherited Qwen3.5 rollback restored QSA/GDN state but did not restore:

- PLE n-gram history (`ArraysCache[3]`);
- PLE short-convolution state (`ArraysCache[2]`).

Therefore rejected draft tokens could remain in PLE state after the target had logically rejected them.

The fix:

1. snapshots PLE state only on a multi-token verify forward;
2. validates the snapshot before mutating inherited recurrent state;
3. performs inherited QSA/GDN rollback;
4. reconstructs PLE state for `confirmed + accepted drafts` only;
5. consumes/clears the snapshot transactionally;
6. fails closed to committed-prefix cache rebuild if validation fails.

Real-model validation reports:

- zero rejected-draft history leaks in instrumented runs;
- 0.0 max abs error on short-conv reconstruction;
- byte-identical committed greedy stream old/new on the controlled A/B;
- deterministic retrieval through 2K/8K/32K/64K/128K;
- 5/5 needles at each tested size;
- at 128K, MTP off/on and prefix cold/warm produced the same output-token hash on that retrieval workload.

Source:
- https://github.com/jundot/omlx/pull/3232

### MXFORGE implication

For Flash-Next, verifier exactness is at least a four-state problem:

```text
QSA cache/state
GDN recurrent/conv state
PLE n-gram history
PLE short-conv state
```

Do not certify MTP merely from output equality on all-accept workloads. Force natural and synthetic partial-reject cycles and compare every recurrent state against committed-prefix replay.

## 6. Continuous batching / multi-agent reliability

oMLX PR #3246 fixes a chain of Flash-Next mixed-length batching failures:

- `QSAKVCache` singleton was not converted through its model-owned `to_batch()` protocol before an incoming row joined;
- ragged batched QSA offsets were treated as scalar in indexer construction;
- a mid-MTP-cycle join could feed batch-shaped trunk hidden state into a singleton MTP fold;
- trimmed `BatchQSAKVCache` did not slice all indexer arrays, causing residual corruption/recovery.

With the fixes, an M3 Ultra completed a **14K-token request generating 500 tokens while four short requests joined mid-flight**, with Lightning MTP enabled.

The repro path that previously logged repeated corruption/recovery and up to ~13-second joins fell to roughly ~2-second joins with zero corruption events in the reported repeated rounds.

Source:
- https://github.com/jundot/omlx/pull/3246

This is highly relevant to an orchestrator + subagent server. Mixed-length late joins are not an edge case for agentic serving; they are the normal workload.

## 7. Context-derived `ngram-mod` speculation: a second adaptive lane

A controlled DGX Spark paired benchmark now gives strong evidence for llama.cpp `--spec-type ngram-mod` on Flash-Next.

Aggregate treatment:

- same request bytes baseline/treatment;
- temperature 0;
- seed 42;
- thinking off;
- 3,496 completion tokens/arm;
- exact output matches: 4/4;
- baseline server decode: **27.256 tok/s**;
- ngram-mod server decode: **82.609 tok/s**;
- server decode speedup: **3.03x**;
- wall speedup: **2.49x**;
- draft acceptance: **67.75%**.

The distribution matters more than the average:

- copy/modify Python: **142.5 tok/s** treatment, ~3.8x wall speedup;
- JSON/copy/structured transforms: large wins;
- novel code: essentially no win because the context contains little useful future-token overlap.

This mechanism drafts candidate spans from token sequences already present in the current context and lets the target verify the span. It is lossless under the normal verifier contract; the useful predictor is **output novelty**, not simply “code vs prose.”

Sources:
- https://github.com/0xBakeer/qwen38-flash-next-spark/blob/main/docs/speculative-decoding.md
- https://github.com/sxuff/qwen38-flash-next-dgx-spark/blob/main/results/q3-q3kxl-ngram-mod.json

### MXFORGE runtime policy hypothesis

Do not assume MTP and ngram gains multiply. Treat them as candidate speculation lanes selected by measured expected committed-token cost:

```text
high context-overlap / edit-copy-transform
    -> ngram-mod candidate

novel coding with high native-MTP acceptance
    -> MTP D2/D3 candidate

low acceptance / prose / unstable verifier economics
    -> shallow MTP or target-only
```

The finished agent runtime should choose by rolling acceptance, accepted span length, verifier cost and task/context novelty rather than one global speculation setting.

## 8. Distributed MTP remains the decisive 2x-M1 uncertainty

oMLX Cluster v2 PR #3118 is strong evidence that the distributed base runtime is becoming much better, but it also contains a direct warning for Flash-Next/Qwen MTP.

The cluster work has physical M3 Ultra + M5 Max JACCL/RDMA qualification, TP and pipeline infrastructure, cache lifecycle, continuous batching and high-throughput DS4 MTP work. However, its current Qwen TP2 MTP qualification remains **fail-closed**: the two ranks produced matching collective traces but stalled at the first Qwen `return_hidden` / rollback graph before the distributed draft cycle.

Source:
- https://github.com/jundot/omlx/pull/3118

This is the single most important reason **not** to extrapolate `35.9 -> 82.3 tok/s` from one Ultra into `2x M1 Max -> 2.3x`.

For MXFORGE:

1. bring up PP and target-only TP separately;
2. measure target-only topology crossover;
3. treat distributed MTP as its own certification project;
4. report local verifier compute, collectives/wire time, rollback cost, acceptance and ms/committed-token;
5. retain PP as a plausible verifier-friendly topology even if TP wins target-only decode.

## 9. Adjacent Qwen3.8-27B result: adaptive KV on RTX 5070 Ti 16GB

This is **not Flash-Next**, but it is high-value memory-system evidence and directly relevant to a 16GB consumer-GPU sidecar.

An experimental llama.cpp branch keeps authoritative KV in system RAM while dynamically resizing a GPU-resident portion and a shared VRAM prefetch ring. The current validation setup is:

- RTX 5070 Ti 16GB;
- Qwen3.8-27B with UD-Q3-XL;
- Q8 K / Q4 V KV cache;
- CUDA Unified Memory available;
- one server slot.

Reported behavior:

- stock llama.cpp is healthy until roughly 120K and then degrades hard from VRAM oversubscription/page thrash;
- adaptive streaming reaches **~205K at ~15 tok/s**;
- reaches nearly the native **262K at ~10 tok/s**;
- implementation dynamically evicts per-full-attention-layer KV and reuses freed VRAM as a prefetch ring;
- current version does **not** support parallel requests.

Sources:
- https://www.reddit.com/r/LocalLLM/comments/1w0impd/breaking_vram_barrier_qwen_38_27b_at_262k_context/
- https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming

### Broader MXFORGE lesson

The same systems principle now appears independently in several places:

```text
Flash-Next PLE: SSD -> page cache / hot set -> compute
Qwen27B KV:      RAM -> VRAM prefetch ring -> attention
prefix state:    SSD -> hot prefix cache -> live request
2x M1 weights:   node-local UM shards -> compute + wire collectives
```

The correct capacity question is increasingly not “does the entire state fit in the fastest tier?” but:

> **Can the runtime know the next-needed subset early enough to move it while useful compute is happening?**

## 10. What changed in the MXFORGE plan

### Promote to top-tier implementation references

- oMLX #3244 direct exact QSA Metal path;
- oMLX #3235 SSD-PLE gather batching/prefetch;
- llama.cpp #27836 native NextN/MTP per-HC-stream semantics;
- oMLX #3232 transactional PLE rollback;
- oMLX #3246 mixed-length QSA/MTP batching fixes;
- llama.cpp `ngram-mod` as an adaptive speculation lane.

### Keep unchanged

- architecture-aware quant rather than global Q5/Q6;
- Q5_1/~6-bit SSD PLE as first production candidate;
- BF16 SSD PLE as exactness ruler;
- PP-first correctness/control path, TP immediately after;
- frozen ~29.3K coding ruler plus broader agent tasks for promotion;
- exact prefix/state reuse before lossy SpecPrefill.

### Forecast discipline

The new results raise the **upside** materially but do not yet justify replacing the existing two-M1 central estimate with single-Ultra numbers.

Current disciplined interpretation:

- **target-only 2x M1:** still needs direct measurement; high-20s/low-30s remains plausible;
- **mature coding MTP:** 40+ tok/s now has stronger independent plausibility;
- **50+ tok/s:** more credible if distributed verifier economics are excellent, but still upside rather than baseline;
- **cold PP:** old 275-350 tok/s optimized-SSD band is now likely conservative if exact direct QSA and batched SSD-PLE gather both transfer; reopen after first M1 port rather than promote a speculative number;
- **agent edit/copy effective throughput:** can be much higher than novel decode when `ngram-mod` finds long overlapping spans.

The single biggest technical risk has become clearer rather than smaller: **distributed speculative verification and recurrent rollback across Thunderbolt**.

## 11. Immediate experiment queue after travel / ecosystem rescan

Before writing custom code, re-scan upstream because these paths are changing daily.

Suggested order:

1. establish latest oMLX / MLX / llama.cpp Flash-Next baseline;
2. reproduce exact direct-QSA behavior on one M1 Max if model fit permits, otherwise on the two-node control topology;
3. reproduce SSD-PLE batched gather and measure cold 1K/4K/16K/32K PP;
4. certify PLE Q5_1 vs Q8 vs BF16 on the coding ruler;
5. establish target-only PP and TP baselines on the same quant/ruler;
6. implement/qualify all recurrent-state rollback including PLE;
7. sweep MTP D1/D2/D3 (and deeper only if measured profitable), reporting ms/committed token;
8. evaluate `ngram-mod` separately on copy/edit/transform vs novel-code agent workloads;
9. test mixed-length late-join batching with an orchestrator-like request pattern;
10. only then revisit the 2x-M1 production forecast.

## Source index

- llama.cpp Flash-Next merge: https://github.com/ggml-org/llama.cpp/pull/27742
- llama.cpp native MTP: https://github.com/ggml-org/llama.cpp/pull/27836
- llama.cpp alternative MTP / recurrent rollback evidence: https://github.com/ggml-org/llama.cpp/pull/27842
- oMLX direct exact QSA + MTP: https://github.com/jundot/omlx/pull/3244
- oMLX SSD-PLE gather batching: https://github.com/jundot/omlx/pull/3235
- oMLX PLE speculative rollback: https://github.com/jundot/omlx/pull/3232
- oMLX continuous-batching QSA/MTP fixes: https://github.com/jundot/omlx/pull/3246
- oMLX Cluster v2 distributed evidence: https://github.com/jundot/omlx/pull/3118
- ngram-mod mechanism: https://github.com/0xBakeer/qwen38-flash-next-spark/blob/main/docs/speculative-decoding.md
- paired ngram benchmark: https://github.com/sxuff/qwen38-flash-next-dgx-spark/blob/main/results/q3-q3kxl-ngram-mod.json
- adaptive KV Reddit report: https://www.reddit.com/r/LocalLLM/comments/1w0impd/breaking_vram_barrier_qwen_38_27b_at_262k_context/
- adaptive KV branch: https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming
- tarruda M1-generation QSA/split-PLE branch (unchanged at last scan): https://github.com/tarruda/llama.cpp/tree/metal-qwen4exp-split-ngram
