# Qwen3.8 Aug 30 afternoon delta

Status: **research delta / external receipts**

Cutoff: 2026-08-30 afternoon ET.

This note records material changes since `QWEN38_AUG30_LATE_MORNING_DELTA.md`. No production runtime code is changed.

## 1. Flash-Next predecessor lookup converges on a cache-integrated O(log n) design

llama.cpp PR #28040 is the maintainer-shaped follow-up to the earlier #28011 / #27992 predecessor-lookup work.

Instead of maintaining lookup state in `llama_kv_cache`, it moves the necessary cell index into the existing per-sequence position structure inside `llama_kv_cells`. This matches the direction requested by maintainers after #28011 and removes the separate hash map, M-RoPE fallback array and descending scan.

Net tree change reported by the author is **-62 lines**.

Correctness checks reported:

- 55K needle retrieval unchanged;
- 12 sequences with `-np 4`, greedy fixed-seed output byte-identical to master;
- single-image and two-image multimodal cases byte-identical, including position gaps.

RTX PRO 6000, `Qwen3.8-Flash-Next UD-Q4_K_XL`, FA on, warm alternated A/B:

| Context | baseline | indexed #28040 | gain |
|---:|---:|---:|---:|
| 55K | 74.5 | 77.6 tok/s | +4.2% |
| 132K | 52.0 | 56.7 tok/s | +9.0% |

Source: https://github.com/ggml-org/llama.cpp/pull/28040

### MXFORGE implication

If predecessor lookup remains first-order on Metal at 64K+, prefer a cache-integrated position index rather than a parallel side structure or repeated scan micro-optimization. The important contract is no longer merely speed: sequence copy, defrag, multimodal position gaps, rollback and prefix-cache semantics must all mutate the same authoritative index.

## 2. Flash-Next QSA large-TOP_K is still a first-order runtime tax on non-Metal backends

llama.cpp PR #28032 adds a Vulkan radix-sort path for QSA's large `TOP_K` (Flash-Next uses approximately 2048/2051 candidates) and fuses the QSA indexer pattern.

The short-context path is roughly neutral, but the benefit grows sharply with context.

### DGX Spark / GB10

| test | Vulkan master | radix+fusion |
|---|---:|---:|
| PP512 d0 | 693.8 | 691.2 |
| TG128 d0 | 26.18 | 26.19 |
| PP512 d16K | 449.0 | 585.5 |
| TG128 d16K | 13.74 | 22.36 |
| PP512 d32K | 390.1 | 520.8 |
| TG128 d32K | 12.02 | 19.78 |

### Strix Halo / Radeon 8060S

| test | Vulkan master | radix+fusion |
|---|---:|---:|
| PP512 d16K | 183.3 | 219.9 |
| TG128 d16K | 15.82 | 18.21 |
| PP512 d32K | 145.8 | 179.5 |
| TG128 d32K | 12.84 | 15.16 |

Source: https://github.com/ggml-org/llama.cpp/pull/28032

A competing global-memory TOP_K implementation (#28036) had a faster isolated decode TOP_K microkernel on both GB10 and Strix Halo, but #28032 produced the stronger whole-model/prefill results and #28036 was closed without merge. This is another useful reminder that isolated operator speed is not the optimization target.

Sources:
- https://github.com/ggml-org/llama.cpp/pull/28036
- https://github.com/ggml-org/llama.cpp/pull/28032

### Apple implication

Do not transfer Vulkan numbers to Metal. The actionable lesson is to profile the QSA selector as a complete pipeline on Apple — score/reduction, TOP_K, selected-index materialization and sparse-window gather — rather than assuming sparse attention itself is the only long-context cost.

## 3. Fresh single-96GB Flash-Next long-agent field receipt

A LocalLLaMA report posted Aug 30 runs Flash-Next on one RTX PRO 6000 96GB with:

- `primitive-ai/Qwen3.8-Flash-Next-NVFP4` trunk;
- quantized INT4 PLE, approximately 32GB, memory-mapped/offloaded through the PLE path;
- native MTP with 3 speculative tokens;
- prefix caching enabled;
- active context around 165K-170K;
- approximately 89GB GPU memory plus ~33GB host page cache reported.

Reported single-stream generation spans **76-125 tok/s**, with the spread attributed primarily to MTP acceptance: about 87% on code/JSON and about 40% on conversational prose. Prefix-cache hit rate was reported above 90% on a long-horizon task.

Source: https://www.reddit.com/r/LocalLLaMA/comments/1w2b2j0/qwen38flashnext_at_170k_context_on_a_single_96_gb/

This is field evidence, not a controlled benchmark and not transferable numerically to M1. It nevertheless reinforces the memory-tier thesis: compress/page the very large sparse PLE resource and reserve the highest-bandwidth tier for the neural trunk, KV/state and active work.

## 4. Memory-rich / GPU-poor Flash-Next field receipt

A separate Aug-30 report runs `UD-Q4_K_XL` Flash-Next on an older Xeon W-2145 system with RTX 3060 12GB and 256GB quad-channel DDR4 (~80GB/s stated).

Reported configuration/outcome:

- ~110GB RAM resident;
- ~10.5GB VRAM;
- ~65K context;
- ~200 tok/s prefill;
- ~12-15 tok/s generation.

The author reports generation collapsing to ~3-5 tok/s when other memory-heavy workloads run concurrently, and warns that random/synthetic contexts gave misleading MoE performance relative to realistic agent traces.

Source: https://www.reddit.com/r/LocalLLaMA/comments/1w2e40k/experience_report_qwen_38_flash_next_on_memory/

### Two-M1 implication

Unified memory does not make bandwidth contention disappear. Our qualification should run with the intended headless-service background load and real coding-agent traces, not only a clean synthetic benchmark process.

## 5. Local agentic coding evidence favors Flash-Next, and medium reasoning

WonderRico's E2Studio local-agent benchmark currently uses the first 100 Django tasks from SWE-verified with a consistent mini-swe-agent-style harness. It is not a universal coding benchmark and the author explicitly warns against extrapolating to other languages/domains.

Current reported results:

- `Qwen3.8-Flash-Next`: score **91**;
- Flash-Next medium reasoning: score 91 and **29 requests per point**, the best efficiency among all tested local/API models in this harness;
- Flash-Next xhigh: score 91 on the exact same successful tasks, but more chatty with no score benefit;
- `Qwen3.8-27B` family: score **74-81**;
- 27B medium: 75-81 and materially more efficient than xhigh;
- 27B xhigh: 74-81 while generating roughly 4x the tokens in the author's analysis;
- fastest local completion cited for 27B medium NVFP4/FP8: ~43 min; Flash-Next completion ~1h03 in that hardware/harness.

Source: https://wonderrico.github.io/local_llm_benchmark/benchmark-main.html

### Serving implication

For our eventual multi-agent endpoint, **medium reasoning should be the default qualification mode for both 27B and Flash-Next**, with xhigh reserved for an explicit escalation lane. This is a task-time/agent-efficiency result rather than a pure model-intelligence claim.

## 6. Missed-but-material 27B DFlash2 NVFP4 correctness fix

llama.cpp PR #28000 merged Aug 30. It fixes a missing NVFP4 scale handoff in DFlash2 attention projections. Before the fix, an NVFP4 DFlash2 drafter could appear to run but produce almost no accepted speculative tokens because Q/K/V/output projection scales were not supplied to graph operations.

RTX 5090 test, target `Qwen3.8-27B-Q5_K_M`, NVFP4 DFlash2 drafter, greedy fixed seed, max draft 7:

| generated | broken path | fixed path | acceptance after fix |
|---:|---:|---:|---:|
| 128 | 34.4 | 93.1 tok/s | 36.33% |
| 512 | 35.7 | 97.6 | 25.59% |
| 1024 | 38.4 | 119.0 | 33.10% |

Before-fix acceptance was only ~0.12-0.39%. Compared with ordinary decoding from the patched build, the author reports DFlash speedups of ~1.62-1.93x.

Source: https://github.com/ggml-org/llama.cpp/pull/28000

This PR predates the immediately previous manual sweep; it is included here because it was missed and materially changes how NVFP4 DFlash2 results should be interpreted.

### 27B implication

When we qualify DFlash2 post-P69, validation must include:

- effective engine identity;
- actual draft acceptance / accepted tokens per round;
- projection-scale/quant metadata correctness;
- target-only paired control;
- emitted-token fidelity under the chosen greedy contract.

An acceleration toggle plus coherent-looking output is insufficient evidence.

## 7. 27B exact-Q8 frontier remains unchanged

No new Layr submission exists beyond #1481 in the Qwen3.8 27B challenge, and no new scored result changes the `3.7291100105909` external frontier.

Therefore this pass does **not** change the active P69 experimental plan or the current rough frozen-ruler confidence:

- >=20.0: ~80-85%
- >=20.5: ~55-60%
- >=21.0: ~35-40%
- >=21.5: ~20%
- ~22+: ~10%

Do not reopen closed P69 lanes from these external runtime developments.

## Current planning delta

### Flash-Next

1. Prefer cache-integrated O(log n) predecessor indexing if Metal profiling shows the scan is first-order at 64K+.
2. Profile the complete QSA selector/TOP_K/window-gather pipeline at 32K/64K/128K/262K.
3. Keep PLE compressed/pageable as a first-class serving profile rather than treating full PLE residency as mandatory.
4. Use realistic long-horizon agent traces under representative background memory pressure.
5. Default agent reasoning to medium; use xhigh as an escalation mode, not the baseline.

### 27B

1. P69 remains unchanged.
2. DFlash2 remains post-P69, but qualification must prove that the quantized drafter is genuinely executing correctly and accepting useful drafts.
3. Medium-reasoning agent evaluation deserves equal status with raw token-generation throughput when choosing the serving profile.

No production code change is implied by this note.
