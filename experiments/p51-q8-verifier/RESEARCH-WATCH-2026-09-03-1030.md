# Runtime Research Watch — 2026-09-03 10:30 ET

Scope: fresh external pass after `RESEARCH-WATCH-2026-09-03-0730.md`, with 2026-09-03 11:27:46 UTC as the hard GitHub freshness boundary. Canonical-state-first protocol preserved. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DS4 distributed serving, and the planned 2x M1 Max 64 GB / TB4 Hermes system.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **RECOVERED OLDER EVIDENCE + STATUS UPDATE — oMLX #3203 Prompt Lookup Decoding is a first-class agent-workload seam.** The PR itself dates to August, so its performance evidence is not new and must not be described as a fresh September result. The watch chain had carried the general n-gram-history/self-speculation idea but had not promoted the strongest physical receipts. On **M1 Ultra 128 GB**, `Qwen3.8-Flash-Next-oQ4e-mtp` with resident PLE measured repeated/agent workloads **36.5 -> 56.5 tok/s (1.55x)** at MTP depth 6 / draft 48, while novel prose was unaffected. The implementation copies tokens following a repeated suffix from the request's own history and verifies them in one wide target forward; on miss it falls back to the regular Lightning-MTP chain. It also has a fenced cross-request shared pool specifically for agent loops that resend the same file/content. Verify width is memory-bound; the PR documents 16 as the safer 128-GB default and reports that k=32 can approach/OOM at the Metal cap in the tested configuration.

   Independent older **M5 Max 128 GB** evidence on the same Flash-Next oQ4e model, with SSD PLE plus the batched/prefetched gather stack, measured a copy-heavy 246-line Python rewrite at **48.3 -> 108.4 tok/s (2.24x)** with default draft_max=16; novel prose was **30.0 -> 31.7 tok/s**, inside noise. Prefix cache was deliberately defeated with unique nonces. This is unusually relevant to Hermes because file rewrites, repeated diffs, boilerplate regeneration and re-sent source are exactly the workloads where lookup drafting can fire.

   Fresh 2026-09-03 commit `2c62b557640a41d945feba135bffd77d8786959f` is only a terminology/UI change: the feature is now called **Prompt Lookup Decoding** to distinguish it from Qwen4-Exp's unrelated in-checkpoint PLE n-gram table. Do not call the performance receipt new today.

2. **NEW — DS4 #962 tightens live multimodal cache correctness for Pi-style replay.** Created after the prior boundary. It preserves an image-conditioned live-KV checkpoint for same-image follow-up turns, but fixes two subtle replay hazards: (a) visible-transcript removal of a pending `<think>` tag must move the raw checkpoint boundary too, otherwise the next user tag can be tokenized from the wrong byte boundary; (b) unfinished reasoning must never be checkpointed as a closed visible assistant turn. Apple M5 Max / Metal server regressions pass. This is API/session-state work, not an inference speed claim.

3. **UPDATE — DS4 #961 current-main requalification shows conditioning-complete vision persistence has effectively zero hot-path speed tax in the measured case.** Fresh M3 Ultra 512 GiB / Metal paired checks on DeepSeek-V4-Flash-Vision-Exp MXFP4, no MTP, measured:

   - 2,048 frontier: prefill **630.45 main vs 629.54 PR**, generation **42.800 vs 42.855 tok/s**;
   - 16,384 frontier: prefill **573.94 vs 573.32**, generation **37.430 vs 37.410 tok/s**.

   Frontier logits were byte-identical and all differences were below 0.5%. This does not prove a production scheduling result, but it removes an obvious concern that conditioning-complete cache provenance itself materially taxes ordinary decode/prefill.

4. **NEW COMMUNITY LEAD — combined MTP + prompt-lookup tuning remains strongly workload/runtime specific.** A fresh 2026-09-03 Strix Halo / llama.cpp user ran 50 Optuna trials on Flash-Next IQ4_XS at **temperature 1.0**. Best reported point was **29.8 tok/s**, acceptance **0.6584**, with MTP draft max 5 plus modified n-gram lookup (`match=48`, `max=18`, `min=5`). There is no clean no-spec baseline in the post and the hardware/runtime are non-Apple, so this is not a forecast input. It is useful because it shows that combined MTP + lookup can be tuned under stochastic sampling in another runtime, while oMLX #3370's temp>0 zero-acceptance report remains unresolved. Preserve the rule that speculation must be qualified on the exact runtime/sampling/workload.

5. **NO MATERIAL CHANGE — oMLX main / other fresh PRs.** Main only merged a macOS UI-conventions change in this window. #3403 fixes non-ASCII `response_format` serialization and is API correctness, not Flash-Next performance. #3203's fresh commit is naming only. No new Flash-Next mainline performance merge landed after the boundary.

6. **NO CHANGE — exact dual-M1 calibration.** llama.cpp #27993 has no new result/comment after the boundary. DS4 #922 likewise has no sustained 2x M1 Max 0731/Flash-Next TG receipt. DS4 #957 still has no post-fix Apple throughput receipt for the coalesced Metal `--layers` mapping. No new Layr submission. `ARahim3/mlx-dspark` still reports `pushed_at = 2026-09-01T10:54:45Z` despite metadata activity.

## Hermes consequence

The generic throughput forecast does not move, but the **workload router should now explicitly understand Prompt Lookup Decoding**.

Recommended policy addition:

- enable/consider Prompt Lookup for copy-heavy code edits, full-file rewrites, repeated diffs, boilerplate regeneration and agent loops that resend previously seen source;
- keep it opportunistic and self-disabling on novel prose/reasoning, where the measured systems show essentially no benefit;
- fence cross-request history so two unrelated agent sessions cannot splice continuations;
- cap verify width from memory pressure rather than maximizing draft width blindly;
- treat Prompt Lookup and the Flash-Next PLE n-gram table as completely separate mechanisms;
- benchmark it independently under PP2: wide target verification may interact differently with dual-node pipeline bubbles than it does on a single M1 Ultra/M5 Max;
- keep the three state layers from the prior pass: transactional hot frontier, bounded rewind checkpoints, durable SSD cold state;
- for multimodal Hermes turns, cache identity and replay checkpoints must remain conditioning-complete and must never snapshot an unfinished reasoning state as if it were a completed visible turn.

The recovered M1-Ultra receipt is encouraging for **effective agent throughput**, but it is deliberately **not folded into the generic B1/B2-B4 probability bands**. A copy-heavy rewrite can be far faster than ordinary novel generation without changing the model's underlying dependent-chain decode ceiling.

## Forecast consequence

Short/medium B1, ~128K B1, and mature B2-B4 aggregate probability bands remain **unchanged**. There is still no sustained physical 2x M1 Max Flash-Next decode calibration.

Keep a separate conditional upside track: on sufficiently repetitive/copy-heavy agent turns, Prompt Lookup has physically delivered **1.55x on M1 Ultra** and **2.24x on an independent M5 Max setup**. These are single-node/runtime-specific receipts and must not be multiplied directly into the dual-M1 forecast.

The mature target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, 3-4 logical agents, normally 2-3 active compute slots, asymmetric resident PP2, transactional/replay-safe state management, and a fourth Flash-Next identity available elastically rather than permanently compute-hot.

External evidence does **not** modify the certified P69 checkpoint; **P69B13 remains next using existing profiling data only**.

## Sources

- oMLX #3203 Prompt Lookup Decoding: https://github.com/jundot/omlx/pull/3203
- DS4 #962 live multimodal/Pi replay checkpoint correctness: https://github.com/antirez/ds4/pull/962
- DS4 #961 conditioning-complete vision KV persistence + current-main speed check: https://github.com/antirez/ds4/pull/961
- Fresh community MTP + lookup tuning lead: https://www.reddit.com/r/LocalLLM/comments/1w5xaqt/qwen_38_flash_next_optimal_mtp_settings/
- llama.cpp #27993 exact dual-M1 Flash-Next correctness thread: https://github.com/ggml-org/llama.cpp/issues/27993
- DS4 #922 exact dual-M1 0731 long-context thread: https://github.com/antirez/ds4/issues/922
- DS4 #957 Metal `--layers` mapping coalescing: https://github.com/antirez/ds4/pull/957
