# Project 51 primary-lane research watch — 2026-09-28 22:19 ET

**Freshness boundary entering this pass:** **2026-09-29 01:03:02 UTC**.  
**User cutoff:** **2026-09-29 02:19:04 UTC**.

## Decision

**Durable architecture/target update, but no physical TG/PP-center change.**

This pass promotes:
1. a **persistent canonical agent-root image** as an explicit production target separate from cold PP;
2. **Swift 1.5 Qwen3.8-27B** as a first-class alternate checkpoint lane measured by effective solved-task throughput, not physical TG.

Physical targets remain unchanged:
- dual-M1 Flash-Next: **40 TG sustained @ genuinely filled ~128K / 400 cold PP / ~70% >=40 TG**;
- single-M1 dense27B: **25 TG / ~110 PP**;
- RTX 5070 Ti dense CUDA-v2 ladder unchanged;
- Strata Flash-Next ladders unchanged;
- IQ3_S AA>=40 planning prior unchanged at **~80%**.

## Strict-window findings

### NEW — MLX-Serve DFlash2 selector codebook guard

Source: https://github.com/ddalcu/mlx-serve/commit/cb24806ff9a043eb0401422ab75c436c39d375d7  
Timestamp: **2026-09-29 02:07:33 UTC**.

DFlash2's predecessor/successor selector codebooks are consumed through dense gathers. A generic quantizer can pack them into a shape the selector cannot use, turning every draft into failure. The loader now rejects such packs immediately.

P51 rule:
- keep tiny selector/codebook/control tables dense BF16/F16 unless a quantized-gather path is explicitly qualified;
- fail at load rather than diagnosing zero acceptance later as draft/model quality.

### NEW — oMLX exact fused decode/verify stack

Source: https://github.com/jundot/omlx/commit/4626613b07e77b74e20b8fdaef550ddbc8c497de  
Timestamp: **2026-09-29 02:12:26 UTC**.

The GLM-5.3 stack fuses long dependent decode/verify op chains while replaying reference arithmetic and maintaining bitwise/fallback checks. In the preceding measured stage of this combined stack on M5 Ultra, greedy decode moved from **38.9 / 38.7 / 32.7 -> 51.7 / 51.2 / 49.0 TG** at pp200/1024/4096. The work also found several attractive custom kernels slower in-model than the reference and keeps them default-off.

P51 interpretation:
- strong cross-model evidence for exact dependent-chain fusion + per-family fallback;
- reinforces that microkernel wins are subordinate to in-model occupancy/scheduling;
- M5/GLM percentages do **not** transfer numerically to M1/Qwen.

### NEW — SGLang Rust radix TreeCore becomes default with hybrid-state backup semantics

Source: https://github.com/sgl-project/sglang/commit/77091cea68d0701d6cc71edfb45f2815c4f8d791  
Timestamp: **2026-09-29 02:18:57 UTC**.

SGLang switched the unified radix cache's default tree core to Rust where supported and added/ported hybrid-state mechanisms including Mamba/SWA internal-state backup-before-eviction, SWA relocation-aware backup indices, rotation-base support and configured eviction policies.

P51 rule:
- a persistent/shared hybrid root may not tombstone/free internal state until backup is safely materialized;
- allocator compaction/relocation can invalidate physical indices even when logical prefix identity remains valid;
- persistent-root metadata needs logical identity plus refreshable physical placement.

### Outside cutoff

vLLM commit `0af34418` landed at **02:19:10 UTC**, six seconds after this pass's cutoff. It is intentionally deferred to the next pass.

## RECOVERED CURRENT / USER-SUPPLIED — Pi persistent root reuse

Source: https://www.reddit.com/r/LocalLLaMA/comments/1wrz901/who_wants_to_try_a_pi_trick_for_27b_to_reuse/

The Pi extension uses llama.cpp slot persistence with:
- `--slot-save-path`;
- `--ctx-checkpoints 32`;
- `--checkpoint-min-step 4096`;
- a deterministic chat template;
- persistent client-side prefix-cache identity.

The goal is to reuse the stable system/tools/extensions root across different Pi sessions and server restarts.

This is useful evidence for **persistent forkable root images**, not physical shared-prefix state.

## RECOVERED OLDER — patched llama.cpp proves hybrid slot restore can be real

Sources:
- https://github.com/ggml-org/llama.cpp/issues/27813
- https://github.com/ggml-org/llama.cpp/issues/25913
- https://github.com/ggml-org/llama.cpp/issues/28619

On Qwen3.8-Flash-Next:
- cold 5,892-token prompt: **~19.06 s**;
- stock save/restore: **~19.24 s**, because restored recurrent checkpoints were absent;
- patched restore: **~153 ms restore + 4 tokens / ~508 ms next request**.

A separate open issue shows live speculative/draft `ctx_dft` can still be omitted from slot persistence. Therefore a valid P51 root image must include the complete target + recurrent + checkpoint + MTP/draft state, not merely target KV.

## KNOWN CORROBORATION — TensorFold disk spill

TensorFold 0.3.6.2-era evidence:
- 35,583-token Qwen3.8-27B conversation;
- snapshot **2.2-2.4 GiB**;
- spill **~0.18-0.19 s**;
- reload **~0.24 s**;
- resumed answer **~2.3 s vs 26.2 s cold**, byte-identical.

This strongly corroborates that same-runtime full-state persistence is production-useful.

## RECOVERED CURRENT — NInfer complete session persistence

Source: https://github.com/tensorninja/ninfer-4090

NInfer persists a complete resident Qwen3.8-27B session:
- paged target and MTP KV;
- GDN linear-attention state;
- MTP tail hidden;
- checkpoint/long-anchor state;
- prefix/session identity.

A documented 6.9K session is ~416 MiB, saves in ~0.24 s and restores in ~0.12 s. This is same-runtime persistence; DFlash persistence is not yet supported.

## RECOVERED CURRENT — Swift 1.5 alternate 27B lane

Source: https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-27b

Swift 1.5 keeps Qwen3.8-27B's architecture lineage but post-trains for less pathological overthinking. Published xhigh BF16 results show workload-dependent **mean-token reductions roughly 16-54%**, not a universal 58.5%. LiveCodeBench rises while mean tokens fall ~24.5%; Terminal-Bench rises while token use falls ~16%.

Project-51 consequence:
- add an **effective task-throughput** metric: solved-task wall time, reasoning/output tokens and tool trajectory length;
- keep physical TG/PP untouched;
- retain base Qwen3.8-27B as control until Swift passes the full xhigh AA/tool/long-context suite.

Swift-specific GSQ-RCO IQ3_S+MTP (~12.12 GB) is an attractive capacity artifact but remains uncertified for P51 long-context/agent behavior.

## RECOVERED OLDER — InferredThoughts SSD-streamed full Flash-Next

Sources:
- https://github.com/compiledthoughts/Inferred-Thoughts
- https://www.reddit.com/r/LocalLLaMA/comments/1wrxap8/qwen38flashnext_177b_nvfp4119gib_ssd_streaming_at/

Qwen3.8-Flash-Next 176.9B runs on an RTX 5060 Ti 16 GB + 32 GB host by keeping ~20 GiB model data resident and streaming cold experts/ngram rows from NVMe.

Repo depth curve:
- ~0.2K: **10.40 TG**;
- ~6K: **8.35 TG**;
- ~29K real Cline session: **6.88 TG**;
- cold PP around **49.2**.

P51 conclusion:
- dynamic expert residency, layer-ahead prefetch and SSD-byte accounting are useful mechanisms;
- the 9-10 TG headline is short-context and is not evidence for filled-128K speed.

## RECOVERED OLDER — rotated 3-bit dense-27B quality/capacity evidence

Sources:
- https://www.reddit.com/r/Qwen_AI/comments/1wru8fq/qwen38_27b_in_3bit_keeps_math_code_and_61k/
- https://eliovp.com/blog/paiton-qwen38-w3a4-radeon-ai-pro-r9700

On one R9700, a ~3.1-bpw Hadamard-rotated INT3 Qwen3.8-27B:
- preserves 61,440-token needle retrieval at **100% vs 100%** against MXFP4;
- GSM8K/HumanEval deltas are within the reported paired uncertainty;
- MMLU-Pro subset falls **~2.86 points**, statistically significant;
- the lower weight footprint can be traded for more KV/concurrency.

P51 interpretation:
- keep rotation/protected-island experiments below 4 bpw in the search space;
- long-context retrieval parity is not intelligence/source-like certification.

## Durable target changes

### Persistent canonical agent-root target

Dense 27B first:
- **20K-40K** invariant system/tools root;
- survives runtime restart;
- same-runtime restore-to-ready **<5 s initial gate / <2 s stretch**;
- complete target + recurrent + checkpoint + MTP/draft state;
- exact identity mismatch -> hard miss/re-prefill;
- 32K CUDA->Apple portable-state qualification next, then 96K/128K;
- physical shared-root/COW remains a separate later target.

At ~110 native M1 PP, cold construction of a 20K root is ~182 s and 40K is ~364 s, which explains why eliminating repeated cold root-prefill matters more than modest PP tuning for agent startup.

### Swift effective-task-throughput lane

Do not change physical 25-TG / 110-PP targets. Report:
- physical TG/PP;
- solved-task wall time;
- generated reasoning/output tokens;
- tool-call trajectory length;
- source-vs-Swift AA/tool/long-context pass/fail.

## Strict-window negative scan

- **TensorFold:** no post-boundary commit after 0.3.6.2.
- **Strata:** no post-boundary commit/release after 0.1.20; no exact 5070-Ti ladder/longer soak.
- **Ishizuki:** no post-boundary commit.
- **llama.cpp:** no P51-relevant commit in-window.
- **M1 / M1 Max Flash-Next:** no new physical strict-window receipt.
- **DASLab:** no new official Flash-Next IQ3_S 32K/64K/128K/262K source-paired quality result found.

## New hard boundary

**2026-09-29 02:19:04 UTC**
