# Runtime Research Watch — 2026-09-03 07:30 ET

Scope: fresh external delta after `RESEARCH-WATCH-2026-09-03-0400.md`, following the canonical-state-first protocol. Fresh audit window begins at branch checkpoint `5441fa443bbc915ecc194112c83a6ebf93552006` / 2026-09-03 08:01 UTC. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DS4 distributed serving, and the planned 2x M1 Max 64 GB / TB4 Hermes system.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **NEW — DS4 #960 makes cancellation/retry a transactional prompt-frontier operation.** The PR was created 2026-09-03 10:59 UTC. It snapshots the mutable generation frontier before decode so a client cancellation can restore not only token count but raw KV-ring contents plus compressor/indexer recurrent state. On M3 Ultra / Metal / DeepSeek-V4-Flash-Vision-Exp MXFP4, prior validation overwrote the entire raw ring and reproduced **607 full-logit vectors exactly** after restore. In the integration test, an image/tool-result cancellation restored **1,272 tokens** and an identical retry reused all **1,272 with zero suffix prefill**; two ten-resident rounds later reused **1,061 and 1,076 tokens** after unrelated requests. Snapshot capture averaged **2.717 ms** and used about **22.39 MiB** of GPU backup tensors plus host state. The binding is exact, session-owned and resident-only; ordinary slot eviction still destroys it. For Hermes, cancellation, timeout and retry should be treated as a state transaction: checkpoint the mutable frontier before generation and restore on abort rather than merely trimming the transcript/token list.

2. **NEW — DS4 #961 persists multimodal KV only with exact conditioning provenance.** Created 2026-09-03 11:01 UTC. The PR recognizes that identical text tokens are not sufficient cache identity once image embeddings have conditioned the model. Its persistence key includes image count, token spans, hashes of the final conditioning vectors and canonical token text; changed/moved/missing images cannot select the checkpoint. Physical M3 Ultra / Metal / Vision-Exp MXFP4 validation saved and restored a **1,044-token image-conditioned checkpoint across restart in 9.2 ms**, while changed-image and text-only controls rebuilt. Durable Hermes implication: any future multimodal/attachment-aware agent cache key must include non-text conditioning provenance, not only rendered text/token identity.

3. **STATUS UPDATE — oMLX #2595 generic MoE expert offload remains an interesting capacity mechanism but is currently out of sync with main.** The PR streams non-resident `SwitchGLU` experts directly from checkpoint safetensors and has strong memory-vs-latency measurements on Gemma-4-26B-A4B: 14.20 GB / 122.5 tok/s at full residency; 7.78 GB / 59.4 tok/s at 50%; 4.57 GB / 40.1 tok/s at 25%; 2.96 GB / 29.3 tok/s at 12.5%. Current GitHub state is open and `mergeable=false`, with a fresh comment asking for rebase/conflict resolution. This is not a new Flash-Next receipt and does not change the preferred resident-hot Flash-Next design; it remains a future capacity/reference seam rather than a throughput lever.

4. **NEW but non-material to our runtime — oMLX #3401/#3400.** #3401 identifies a Browse/Search UI size-estimation bug where U32-packed MLX quants can be shown at roughly 6x their actual safetensors size, hiding models that fit. #3400 is a GLM-5.3-Flash affine-quant sanitize-sidecar loading bug. These affect model discovery/GLM compatibility, not current Flash-Next performance or Hermes topology.

5. **NO CHANGE — exact dual-M1 calibration.** llama.cpp #27993 has no new comments/results after the 08:01 UTC boundary; DS4 #922 likewise has no new sustained 2x M1 Max 0731/Flash-Next TG result. DS4 #957 still has no post-fix Apple throughput receipt for the coalesced Metal `--layers` mapping. llama.cpp #28243 and #28302 have no new follow-up to the Apple MTP and rewind-checkpoint results already recorded. DS4 #861 has no new distributed throughput result.

6. **NO CHANGE — Layr / mlx-dspark / broader ecosystem.** Layr has no new submission after the current exact frontier. `ARahim3/mlx-dspark` still reports `pushed_at = 2026-09-01T10:54:45Z`. A fresh web/Reddit/Hugging Face sweep mainly resurfaced already-recorded single-M1/64-GB Flash-Next and oMLX results; no new physical dual-M1 Flash-Next calibration appeared.

## Hermes consequence

This pass strengthens **state correctness and lifecycle semantics**, not raw compute expectations.

Add two explicit requirements to the preferred Hermes runtime policy:

- **Cancellation-safe frontier transactions:** before a generation that may be cancelled/retried, preserve the model-owned mutable frontier (KV ring + recurrent/indexer/compressor state), not merely transcript text or token count. On abort, restore that frontier exactly before accepting a retry. Keep the binding session-owned and invalidate conservatively on ambiguous mismatch.
- **Conditioning-complete cache identity:** text/token equality is insufficient for multimodal turns. Cache/session keys must incorporate every non-text conditioning input that can change hidden/KV state (image identity/spans/conditioning hashes; analogous provenance for future audio or other modalities).

These compose with the already preferred design: 3-4 logical persistent Flash-Next agents, normally 2-3 active compute slots, exact session-aware hot-state ownership, staleness-aware eviction, rewind-capable recurrent checkpoints under a byte budget, durable SSD exact-terminal fallback, bounded persistence under memory pressure, asymmetric resident PP2, and speculative depth enabled only after identity + wall-clock qualification.

A useful implementation distinction is now clearer:

- **hot transactional checkpoint** — cheap, resident snapshot for cancellation/retry during an active request;
- **rewind checkpoints** — bounded resident history for edits/branching/compaction;
- **durable exact terminal / paged SSD state** — cold persistence across unload/restart/slot eviction.

Do not collapse those three responsibilities into one cache mechanism.

## Forecast consequence

Short/medium B1, ~128K B1, and mature B2-B4 aggregate probability bands remain **unchanged**. There is still no physical sustained 2x M1 Max Flash-Next decode receipt.

The user target of roughly **400+ tok/s cold prefill plus excellent prompt/session reuse** remains sensible and unproven on dual M1 Max. This pass improves confidence that long-lived Hermes sessions can survive realistic agent lifecycle events (abort, retry, branching, multimodal continuation) without unnecessary replay, but it does not change the M1 compute ceiling.

External evidence does **not** modify the certified P69 checkpoint; **P69B13 remains next using existing profiling data only**.

## Sources

- DS4 #960 cancellation frontier restore: https://github.com/antirez/ds4/pull/960
- DS4 #961 vision-conditioned KV provenance: https://github.com/antirez/ds4/pull/961
- oMLX #2595 MoE expert offload: https://github.com/jundot/omlx/pull/2595
- oMLX #3401 quant size-estimation issue: https://github.com/jundot/omlx/issues/3401
- oMLX #3400 GLM affine-quant sanitize issue: https://github.com/jundot/omlx/issues/3400
- llama.cpp #27993 exact dual-M1 Flash-Next thread: https://github.com/ggml-org/llama.cpp/issues/27993
- DS4 #922 exact dual-M1 0731 long-context thread: https://github.com/antirez/ds4/issues/922
- DS4 #957 Metal `--layers` mapping coalescing: https://github.com/antirez/ds4/pull/957
