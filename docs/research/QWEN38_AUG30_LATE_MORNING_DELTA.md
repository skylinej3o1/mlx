# Qwen3.8 Aug 30 late-morning delta

Status: **research delta / external receipts**

Cutoff: 2026-08-30 late morning ET.

This note records only material changes since `QWEN38_AUG30_MORNING_RUNTIME_DELTA.md` and the subsequent manual sweeps. No production runtime code is changed.

## 1. Flash-Next predecessor lookup: simple scan fix vs indexed lookup

Two llama.cpp approaches now have a clean same-stack comparison.

### Small scan-shortcut patch: llama.cpp #28011

The simple patch stops checking all 256 possible sequence IDs once the KV cell's actual sequence membership has been exhausted. It is only 5 additions / 4 deletions and preserves visit order/callback behavior.

Initial RTX PRO 6000 `Qwen3.8-Flash-Next UD-Q4_K_XL` warm results:

- 55K generation: 56.3 -> 74.3 tok/s
- 132K generation: 33.6 -> 50.9 tok/s

Fresh independent Strix Halo / ROCm A/B on plain master:

- 4K: 19.33 -> 19.56 tok/s (+1.2%)
- 16K: 15.21 -> 15.65 (+2.9%)
- 32K: 13.30 -> 13.85 (+4.1%)

The smaller ROCm gain is plausibly explained by a separate CPU TOP_K fallback already consuming host cores.

Source: https://github.com/ggml-org/llama.cpp/pull/28011

### Indexed `(seq,pos)` lookup: llama.cpp #27992

The larger design maintains a per-sequence position index rather than rescanning used KV cells for predecessor-token queries.

Same-stack head-to-head posted Aug 30 on RTX PRO 6000:

| Context | #28011 simple scan | #27992 indexed | indexed advantage |
|---:|---:|---:|---:|
| 55K | 74.7 | 77.5 | +3.7% |
| 132K | 48.1 | 56.7 | +17.9% |

Prompt processing was effectively unchanged within run-to-run drift.

Important integration fact: these approaches are not additive. Once the index answers the lookup, the old scan does not execute; stacking both can therefore add overhead rather than compose.

Source: https://github.com/ggml-org/llama.cpp/pull/27992

### MXFORGE implication

For the eventual Apple Flash-Next port:

1. treat `get_prev_tokens` / PLE predecessor lookup as an explicit 64K+ profiling surface;
2. the tiny early-exit patch is a low-risk upstream-style quick win;
3. if predecessor lookup remains first-order at 64K-262K, prefer an indexed `(sequence,position)` state structure rather than progressively optimizing a linear scan;
4. certify the index as part of cache mutation/copy/defrag/rollback semantics, not as an isolated lookup helper;
5. do not stack the indexed and linear-scan fixes merely because both win independently.

This strengthens the broader rule that Flash-Next long-context performance is still limited by removable bookkeeping rather than only QSA arithmetic or memory bandwidth.

## 2. Dual-GB10 Flash-Next: speed/correctness boundary matters more than peak TPS

A fresh NVIDIA Developer Forum incident report qualified `RadixArk/Qwen3.8-Flash-Next-NVFP4` on two GB10 systems over RoCEv2 with SGLang TP2.

Retained correctness-qualified profile:

- native 262,144 context
- NEXTN 3 speculative steps / top-k 1 / 4 draft tokens
- ReplaySSM enabled
- eager execution; decode CUDA Graph disabled
- overlap scheduling disabled
- FP32 Mamba/SSM state
- Triton GDN
- cuDNN dense FP4 GEMM
- FlashInfer CUTLASS MoE
- max two running requests

Measured warmed 2K code decode:

- 41.60 / 42.39 / 42.86 tok/s
- median 42.39 tok/s

A 16,384-token continuous generation completed at 48.01 tok/s and the following short request also succeeded. NEXTN-off on the retained stack was about 18-20 tok/s, implying roughly 2.1-2.35x for that workload.

The critical result is the rejected faster profiles:

- decode CUDA Graph path: ~50.66 tok/s, but punctuation-loop degeneration and failed ~25K marker retrieval;
- FlashInfer GDN FP32: ~60.84 tok/s, but vision/looping/retrieval semantic failures;
- BF16 Mamba state: +12-15%, but severe semantic degradation;
- overlap scheduling: reproduced a long-output -> next-short-prefill service crash boundary.

The original live agent failure occurred after five execution rounds / 15 tool calls at ~31K total context and produced invalid sampling probabilities, CUDA assert, Xid 43, and TP/NCCL termination despite low KV utilization and no OOM.

Source: https://forums.developer.nvidia.com/t/qwen3-8-flash-next-nvfp4-on-2x-gb10-long-agent-service-crash-isolation-42-4-tok-s-qualified-tp2/381836

### MXFORGE implication

For Flash-Next, benchmark speed without semantic qualification is actively dangerous. Our serving gate should include:

- long non-looping generation;
- ordered-marker / literal retrieval at 25K+;
- tool-call / tool-result continuation;
- long-output -> short-prefill transition;
- prefix/cache reuse;
- concurrent joins;
- recurrent rollback after speculative rejection;
- restart / post-cancel health.

The 50-60 tok/s rejected configurations are a useful reminder that a plausible-looking HTTP 200 response can still be corrupted.

## 3. Distributed speculative transport: concrete PP pattern from heterogeneous vLLM

A heterogeneous five-GPU deployment (`v100-skinny` PR #7) now demonstrates PP speculative decoding across hardware generations, including explicit draft-token transport and recurrent rollback.

Reported single-stream results:

| Model / topology | plain | with MTP |
|---|---:|---:|
| Qwen3.8-27B-NVFP4, PP=2 on 2x V100 | 32.3 | 79.8 +/- 1.2 |
| Qwen3.8-27B-NVFP4, TP2 + PP across RTX/V100 stages | 32.2 | 85.0 +/- 1.1 |
| Flash-Next, same 2x2 grid | 32.2 | 51.9 |

The transport design is the useful part:

- the last PP stage broadcasts the sampled matrix `[num_reqs, k+1]` plus draft token IDs;
- non-last ranks derive accepted counts and rollback locally;
- all ranks trim optimistic output-token growth after acceptance/rejection;
- hybrid GDN/Mamba state rollback remains rank-consistent.

Without explicit draft-token transport, proposal values existed only on the last rank and PP0 failed in round 1. Without output-length trim on every rank, rank-local sequence state eventually diverged and NCCL wedged.

Source: https://github.com/dnv2003/v100-skinny/pull/7

### Two-M1 implication

This does **not** prove a fast Thunderbolt implementation, but it gives a concrete distributed-MTP state-machine template:

1. draft on the owning stage;
2. transport compact proposal/score metadata, not large hidden states where avoidable;
3. derive accept/rollback decisions identically on every rank;
4. trim optimistic sequence state on every rank;
5. keep GDN/QSA/PLE rollback transactional and rank-consistent.

That makes the two-M1 distributed native-MTP problem more bounded. PP + context/history drafting is still the lower-risk first lane, but native distributed MTP now has a proven architectural precedent outside Apple.

## 4. Fresh oMLX agent integration: local Codex model catalog

oMLX PR #3313 generates a Codex-compatible local model metadata catalog and process-scoped Codex profile from served oMLX model metadata.

The practical goal is to prevent Codex from treating local endpoints as unknown models, which can otherwise select incorrect context-window/tool defaults. The PR preserves aliases/profiles, excludes hidden helper models, leaves the user's ordinary Codex config unchanged, and requires explicit model selection when model-type metadata cannot be resolved.

Source: https://github.com/jundot/omlx/pull/3313

This is not a kernel-performance result, but it is directly useful to the eventual local coding-agent serving stack.

## 5. NVFP4 naming / quality bookkeeping rule

Do not record `NVFP4` as though it uniquely defines checkpoint quality.

For research notes and future quant builds, record at least:

- actual on-disk / payload bytes;
- effective average bpw over the full model;
- tensor-family allocation (e.g. NVFP4 experts/MLP, FP8 attention, BF16 MTP/norm/router islands);
- calibration method / importance weighting;
- activation quantization if applicable;
- MTP-head precision separately.

Working quality heuristic: a well-calibrated architecture-aware checkpoint around ~6.5 effective bpw is generally in the high-confidence daily-driver zone, but functional allocation still matters more than the single average number.

## 6. 27B exact-Q8 project impact

No new external result in this pass justifies reopening a closed P69 lane or changing the current frozen-ruler forecast.

The most relevant fresh 27B information is distributed-serving architecture, not a new exact-Q8 kernel frontier.

Continue to keep:

- P69 experiment selection tied to measured local structural remainder;
- DFlash2 / context drafting as post-P69 serving lanes;
- exact-Q8 champion separate from lower-bit/NVFP4 speed profiles.

## Current planning delta

Flash-Next priority additions:

1. profile predecessor lookup explicitly at 64K/128K/262K;
2. if first-order, prototype indexed `(seq,pos)` lookup rather than endlessly tuning a scan;
3. preserve PP + history-derived wide verification as the lowest-risk two-M1 speculation lane;
4. use the distributed-MTP transport pattern above when native PP MTP work begins;
5. add semantic/retrieval/transition qualification before accepting graph/overlap/kernel speedups;
6. maintain explicit effective-bpw and tensor-allocation metadata for every quant artifact.

No production code change is implied by this note.
