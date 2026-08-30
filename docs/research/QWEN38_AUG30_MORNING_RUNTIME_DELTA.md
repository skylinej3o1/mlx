# Qwen3.8 Aug-30 morning runtime delta

Status: **FIELD ADDENDUM / IMPLEMENTATION GUIDANCE**

Updated: 2026-08-30 ET.

This note records the fresh post-Aug-29 scan that materially changes or sharpens the MXFORGE Flash-Next plan. It does not modify the active `project51-q8-verifier` experiment state.

## Executive summary

The highest-leverage new conclusion is that **context-derived drafting should move forward alongside the first two-node pipeline-parallel Flash-Next bring-up, rather than waiting for distributed native MTP**. The new Apple receipts show that history/ngram drafting can turn repeated code/edit workloads into very wide exact target verification while standing down on novel prose. That creates a plausible high-throughput two-M1 path even if cross-node native-MTP hidden-state/rollback remains difficult.

A second important conclusion is that part of Flash-Next's long-context degradation is still ordinary software overhead: predecessor lookup, QSA selected-window materialization, indexer reductions, and used-cell bookkeeping. Fresh Metal results show meaningful recovery at 64-100K-class context without changing the model.

## 1. Context-derived drafting is now a core serving lane

### oMLX PR #3203 — history/ngram drafting on Lightning MTP verify

Source: https://github.com/jundot/omlx/pull/3203

Mechanism:

- search the request's own prompt/generation history for a repeated recent suffix;
- reuse the following historical tokens as a deterministic draft;
- verify the copied span in one wide target forward;
- fall back to native MTP on a miss;
- retain a cross-request shared ngram pool with fencing so unrelated requests cannot splice;
- reduce/disable wide drafting under memory pressure.

Original M1 Ultra 128GB result on `Qwen3.8-Flash-Next-oQ4e-mtp`, resident PLE:

- repeated/agent workload: **36.5 -> 56.5 tok/s** at MTP depth 6;
- novel prose: essentially unaffected because the history drafter served only about 1/195 cycles.

Independent M5 Max 128GB reproduction with SSD PLE and the cold-PLE gather work from oMLX #3235:

- repeated Python rewrite: **48.3 -> 108.4 tok/s**, **2.24x**;
- novel prose: **30.0 -> 31.7 tok/s**, inside noise;
- mean tokens per streamed chunk: 7.4 -> 17.0 on rewrite, 4.6 -> 4.7 on prose;
- importantly, this used the default `draft_max=16`, not 48.

The same discussion showed that #3235 adds essentially nothing when PLE is already resident, supporting the interpretation that SSD prefetch mainly makes wide verifies cheaper when page misses would otherwise serialize them.

### MXFORGE implication

Promote context-derived drafting from a post-MTP optimization to an early distributed experiment:

1. two-M1 PP target-only exact baseline;
2. PP + history/ngram proposed spans + one wide target verification;
3. TP target-only attack path;
4. distributed native MTP as a separate state/rollback qualification project;
5. adaptive runtime choosing context draft, native MTP, or target-only by workload and acceptance.

Why this matters for two M1 Maxes:

- history drafting does **not** require a second neural draft model or a distributed MTP head;
- a 16-token copied span can cross the PP boundary as one wide verification batch;
- Thunderbolt boundary cost can therefore be amortized across many committed tokens on copy/edit-heavy agent traffic;
- this is particularly well matched to coding agents that repeatedly resend, rename, refactor, patch, or reproduce source.

## 2. Fresh Metal evidence: long-context slowdown is partly software overhead

### llama.cpp PR #27977 — reduce Qwen4-exp generation slowdown with context

Source: https://github.com/ggml-org/llama.cpp/pull/27977

Profiling identified five important costs:

1. PLE/ngram predecessor lookup scanned far too much of the cache and too many possible sequences;
2. QSA selected ~2K cells but the selection was sometimes used only to construct a mask while essentially the whole cache still reached Flash Attention;
3. the indexer summed four heads through a transpose + poor `sum_rows` geometry, including unnecessary large surface copies;
4. predecessor lookup scanned from position zero even though only recent positions normally matter;
5. used-cell tracking used a locality-poor `std::set` rather than a bitmap.

CUDA anchor on a real ~149K agentic conversation:

- generation: **30 -> 56 tok/s**;
- prefill: **1617 -> 2148 tok/s**.

More important for MXFORGE, an Apple Silicon comment measured M5 Max 128GB, Metal, `UD-IQ4_XS`, Q8 KV and native MTP with source-code prompts:

| Prompt depth | PP baseline | PP #27977 | TG baseline | TG #27977 |
|---:|---:|---:|---:|---:|
| 32K | 663 | 685 | ~33 | 34.6 |
| 74K | 488 | 512 | 24.4 | 28.8 |
| 115K | 387 | 409 | ~25 | 25.9 |

At 74K, generation recovered about **18%**. The CUDA-sized gains do not transfer directly to unified-memory Metal, but the Metal result proves that the software taxes remain material.

### Profiling checklist for future Flash-Next MXFORGE work

Explicitly measure:

- predecessor-token / PLE history lookup;
- QSA selected-cell/window materialization;
- whether sparse selection actually reduces the downstream attention working set;
- indexer head reduction and temporary copies;
- used-cell bookkeeping / data structure locality;
- per-stage CPU vs GPU utilization as context grows.

## 3. Indexed predecessor lookup is powerful but does not automatically compose

### llama.cpp PR #27992 — `(seq,pos)` KV-cell index

Source: https://github.com/ggml-org/llama.cpp/pull/27992

Instead of rescanning used KV cells on every predecessor lookup, the cache maintains a per-sequence position index. On 2x L40S the reported target-only decode curve changed from:

| Context | Scan path | Indexed path | Gain |
|---:|---:|---:|---:|
| 16K | 43.86 | 55.59 | 1.27x |
| 65K | 24.00 | 44.14 | 1.84x |
| 131K | 14.93 | 34.99 | 2.34x |
| 240K | 8.92 | 24.25 | 2.72x |

The giant factors are CUDA/CPU-overhead specific and should not be projected to M1. The M5 Max comparison against #27977 is more useful: both approaches recovered about the same generation performance around 74K.

Crucial negative control: carrying **both** #27977 and #27992 together measurably regressed M5 TG around 32K, about 27.6-29.0 tok/s versus roughly 34.4-34.8 for #27977 alone.

MXFORGE rule reinforced: **individually good optimizations do not automatically compose**. Every structural optimization still needs integrated A/B certification on the exact workload ruler.

## 4. Higher-bit affine MoE kernels are becoming less of a speed penalty

### oMLX PR #3304 — native affine block kernels for Q4/Q6/Q8

Source: https://github.com/jundot/omlx/pull/3304

The existing native block-list MoE fast path was extended to ordinary group-64 affine Q4/Q6/Q8 weights, including paired gate/up projection and plan reuse for down projection.

Layer-level M3 Ultra results at 8192 routes:

- paired kernels: about **1.11x-1.17x** faster than stock;
- single kernels: about **1.09x-1.12x** faster.

A retained Q6 GLM-5.3-Flash checkpoint then showed uncached prefill improvements with matching output hashes:

- 2K: **+6.43%**;
- 4K: **+4.71%**;
- 8K: **+4.27%**;
- 16K: **+3.80%**.

This PR currently targets the existing DeepSeek/GLM MoE dispatch seam; it is **not yet a Flash-Next Qwen4-exp fast path**.

MXFORGE implication: the planned quality-oriented ~5.5-6 bpw Flash-Next quant does not have to accept generic `gather_qmm` forever. Reusing equivalent group-64 Q4/Q6/Q8 block-list machinery for Qwen4-exp SwitchGLU geometry becomes a concrete later lane.

## 5. Route preparation can dominate Flash-Next prefill

### llama.cpp PR #27978 — fast `mm_ids_helper` for top-10 experts

Source: https://github.com/ggml-org/llama.cpp/pull/27978

Flash-Next uses 10 routed experts. llama.cpp's CUDA fast token-to-expert grouping path historically assumed expert counts dividing 32 plus a special case for 6, so 10 silently took a slow generic path.

Profiling on RTX PRO 6000 put this tiny helper at **13.3% of prefill time**, ahead of Flash Attention. Fixing the grouping geometry moved 55K-context prefill from **2334 -> 2600 tok/s** (~+11.4%). Generation did not move because the issue is multi-token route grouping.

MXFORGE implication: profile router preparation and token->expert grouping explicitly. On a model with only ~6B active neural parameters, bookkeeping kernels can become first-order runtime costs.

## 6. DFlash benchmark hygiene: verify the effective engine, not the toggle

### oMLX PR #3310 — local DFlash draft resolution

Source: https://github.com/jundot/omlx/pull/3310

A bare local `dflash_draft_model` name could fail local resolution, trigger a Hugging Face download attempt, fail, and silently fall back to the ordinary engine. The benchmark upload could still tag the run as `dflash` because it read the requested settings rather than the engine that actually loaded.

The current PR fixes local model-path resolution but explicitly calls out effective-engine reporting as a follow-up concern.

Post-P69 DFlash2 qualification rule for Qwen3.8-27B:

- verify the effective engine type;
- record draft acceptance/span counters;
- record actual draft-cycle execution;
- never accept `dflash_enabled=true` alone as evidence that the run used DFlash.

## 7. Flash-Next correctness fixes continue to surface

### llama.cpp PR #27941

Source: https://github.com/ggml-org/llama.cpp/pull/27941

Fresh follow-up fixes cover:

- sequence copies losing indexer keys;
- unified-KV blocks incorrectly keyed on position alone instead of sequence set + bucket;
- multimodal image cells collapsing onto one block slot under M-RoPE;
- malformed metadata assertions reachable from edited GGUFs;
- a pre-existing CUDA long-context abort when pooled block count reached the 65535 `gridDim.y` limit at native 262K context.

MXFORGE implication: exact cache/indexer state is still a moving correctness surface. Distributed work must retain explicit sequence identity and transactional state semantics, especially under copy, rollback, prefix restore and multi-request batching.

## 8. Vulkan ecosystem: full native context is becoming ordinary

### llama.cpp PR #28005

Source: https://github.com/ggml-org/llama.cpp/pull/28005

Large Top-K support was added via an exact argsort fallback. Layered on the same selective lazy-loading work needed to fit Flash-Next on the test iGPU system, `UD-Q4_K_XL` was exercised over **two Vulkan RPC workers at 262,144 context with Q8 K/V**, and a five-run stateful tool-calling smoke completed 5/5.

This is not an Apple performance result, but it is useful external confirmation that full-native-context Flash-Next serving is quickly becoming normal infrastructure rather than a one-off demo.

## 9. Qwen3.8-27B challenge status

The Layr challenge remains at the **3.7291100105909** scored frontier in the latest check. The newest visible #1481 broad compiled-shapeless fusion candidate did not produce a new accepted score and remains unqualified as performance evidence.

No change to the current exact-Q8 P69 policy:

- finish the measured structural remainder first;
- do not reopen closed B8/B9/B10-C/B12-A lanes from external similarity alone;
- keep DFlash2, history/ngram drafting, and context-aware speculative routing as post-P69 serving lanes.

Current rough frozen-ruler confidence remains approximately:

- >=20.0 tok/s: 80-85%;
- >=20.5: 55-60%;
- >=21.0: 35-40%;
- >=21.5: ~20%;
- ~22+: ~10%.

## Revised Flash-Next bring-up order

1. **PP target-only** — exact/correct distributed baseline.
2. **PP + context/history drafting** — verify repeated spans in one wide target pass; does not require distributed neural MTP.
3. **TP target-only** — attack architecture exploiting both memory controllers.
4. **Distributed native MTP** — separately solve hidden-state transport, rollback and recurrent/PLE state.
5. **Adaptive serving policy** — choose history draft, native MTP, or target-only by repetition, acceptance, context depth and memory pressure.
6. Add cache-affinity/concurrency policy for 3-5 agents only after each single-session path is qualified.

## Forecast effect

Do not raise the central two-M1 20-30K target yet solely from these results. Keep roughly **40-50 tok/s** as the mature central Flash-Next TG band pending measured two-M1 results.

Confidence does improve for the **64-100K usability regime**: the new M5 Metal receipt demonstrates that meaningful long-context degradation still comes from removable runtime overhead. It is increasingly plausible that 64-100K can remain a normal interactive coding-agent mode rather than a deliberately slow deep-context profile.

The most important architecture change from this scan is therefore not a headline TPS increase. It is a risk reduction: **high effective coding-agent throughput may be reachable on two M1 Maxes through PP + context-derived wide verification even before distributed native MTP is solved.**
