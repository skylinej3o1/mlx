# Runtime Research Watch — 2026-09-01 Post-Early-Evening

Scope: external runtime/model research only. This is a delta from
`RESEARCH-WATCH-2026-09-01-EARLY-EVENING.md`. It does **not** modify the
certified P69 verifier state. **P69B13 remains next, using existing profiling
data only.**

## Qwen3.8-Flash-Next

### oMLX 0.6.4: direct Metal evidence for QSA + projection + MTP-state work

Source: https://github.com/jundot/omlx/releases/tag/v0.6.4

The 0.6.4 release adds three directly relevant Flash-Next optimizations:

- exact QSA prefill/decode acceleration with native FP32 QSA scoring,
  deterministic block selection, direct sparse-GQA Metal attention, and a
  selected-K/V decode path;
- resident PLE, GDN, and hyperconnection projection acceleration;
- warm-prefix restoration of Lightning-MTP prompt history, avoiding replay of
  the reusable prompt head when a matching prefix-cache entry exists.

Maintainer benchmark, Apple M3 Ultra 512 GB, `Qwen3.8-Flash-Next-oQ4e-mtp`,
Code/Python, 128 generated tokens, Lightning MTP adaptive max depth 3:

| Context | PP before | PP after | TG before | TG after | Total before | Total after |
|---:|---:|---:|---:|---:|---:|---:|
| 4K | 999.61 | 1061.34 | 48.65 | 53.59 | 6.73 s | 6.25 s |
| 16K | 950.06 | 1061.31 | 48.74 | 55.70 | 19.87 s | 17.74 s |
| 32K | 834.31 | 1113.63 | 40.08 | 45.92 | 42.47 s | 32.21 s |

At 32K this is +33.5% PP, +14.6% TG, and -24.2% total request time.

Interpretation for the dual-M1 plan:

- this is strong evidence that QSA/indexer execution and the surrounding
  recurrent/projection path still contain substantial software headroom;
- selected-K/V decode and QSA scoring should be part of the single-node
  baseline before attributing long-context losses to TB4;
- MTP sidecar/prompt-history restoration belongs in the multi-agent server
  design so returning sessions do not replay reusable draft state;
- absolute M3 Ultra throughput must not be transferred to M1 Max.

### QSA top-k/indexer can itself become the decode bottleneck

Source: https://github.com/ggml-org/llama.cpp/discussions/27950

A current Strix Halo Flash-Next implementation reports that QSA TOP_K over
full context, executed 12 times per token, can dominate long-context decode.
Moving/fixing the top-k path on GPU produced roughly +38% to +53% end-to-end
improvement at 24K in that ROCm implementation.

The same work also reports large return-TTFT reductions when recurrent GDN
checkpoints and session state remain warm instead of being reconstructed.

This is **architectural signal, not an M1/Metal receipt**. The actionable
lesson is to instrument QSA/indexer/top-k separately and preserve recurrent
checkpoints stage-locally in the eventual PP2 server.

## Qwen3.8-27B exact verifier track

Source: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge

Fresh GitHub inspection still shows:

- current best score: `3.7291100105909`;
- #1481 is the newest visible submission;
- no #1482+ promoted result is visible;
- the repository has not produced a new exact-Q8 frontier signal that changes
  the P69 plan.

Therefore:

- certified P69B12 remains untouched;
- no lossy Flash-Next or DS4 quantization result is admissible evidence for the
  exact-Q8 ruler;
- **P69B13 remains next using existing P69B7/P69B10 measurements only.**

## DeepSeek V4 Flash 0731 / DS4

### Exact 2x M1 Max 64 GB TB4 deployment now has a quantitative receipt

Source: https://github.com/antirez/ds4/issues/922

This is the most important new result in this pass because it matches the
planned hardware topology closely.

Reported setup:

- 2x MacBook Pro M1 Max, 64 GB each;
- point-to-point Thunderbolt 4 bridge;
- DeepSeek-V4-Flash-0731 DS4-Quality128, 95.76 GiB;
- coordinator layers 0:22 / worker layers 23:output;
- `dist-activation-bits=8`;
- context allocation 262,144;
- prefill chunk 1024.

Measured result:

- 34,384-token distributed prefill completed in about 225 s;
- reported average prefill throughput: **~152 tok/s**;
- the same setup also completed a 51K-token prompt through the CLI.

The original server run crashed only when generation began. The follow-up
identified the cause as a vocab/model mmap on a sleeping external USB SSD,
not the distributed compute path. Moving the model to internal NVMe removed
the SIGBUS; the 34K prefill plus generation then completed successfully in
257 s.

The report additionally notes that disabling TSO on the TB4 bridge and
removing an unrelated auto-start service consuming about 46 GB were needed
for overall stability.

Important limit:

**No sustained generated-token/decode throughput was posted.** Do not infer a
TG number from 225 s versus 257 s because the generated-token count is not
specified.

Implication:

- PP2 feasibility is upgraded from a correctness-only receipt to a
  quantitative long-prefill receipt on the exact M1 Max class;
- the existing dual-M1 B1 decode forecast should **not** be raised yet;
- internal NVMe, TB4 TSO state, and background-memory hygiene should become
  explicit bring-up checklist items.

### PR #621: AProjQ4 makes per-projection mixed quantization concrete

Source: https://github.com/antirez/ds4/pull/621

PR #621 converts exactly 215 dense attention-projection tensors across the 43
0731 layers from Q8_0 to Q4_K:

- `attn_q_a`
- `attn_q_b`
- `attn_kv`
- `attn_output_a`
- `attn_output_b`

Matched model size:

- AProjQ8: 80.76 GiB
- AProjQ4: 78.62 GiB
- saving: ~2.14 GiB

The imatrix AProjQ4 quality fixture shows no measured regression on its small
100-case / 2,313-target-token sample, while the Metal reports show a decode
advantage; an M5 Max result exceeds 50 generated tok/s with AProjQ4 ahead of
AProjQ8 across the tested frontiers.

This strengthens the case for **workload- and projection-specific mixed
quantization** in the future Flash-Next/DS4 capacity track. It does not belong
inside the frozen exact-Q8 P69 campaign because Q8->Q4 is intentionally lossy,
even if a small quality fixture is neutral or positive.

### DS4 #913: verifier semantics must match ordinary decode semantics

Source: https://github.com/antirez/ds4/issues/913

The DSpark investigation found a real decode/verify mismatch around sparse
indexer thresholds: ordinary decode and batched verification could select
different attention candidate sets in the 512-1024 compressed-row range.
It also found that a one-row speculative verification should use ordinary
decode rather than paying the generic batch-verifier overhead; on the tested
M5 Max the batch verifier at `n_tokens==1` was about 3x the relevant plain
path cost.

After multiple fixes, stochastic temp>0 speculation still remained roughly
4-6% slower than no DSpark on that hardware/model configuration.

Implication for both Flash-Next and distributed DS4 work:

- prove decode/verify QSA/indexer threshold parity before optimizing the
  verifier;
- benchmark the one-row fallback independently;
- do not assume a generic batched verify path is semantically identical or
  economically useful at every draft depth.

## Decision update

1. **Biggest new evidence:** exact 2x M1 Max / TB4 DS4 now has a measured
   34K distributed-prefill receipt at ~152 tok/s, and 51K CLI operation works.
2. **No decode TG has been published for that exact setup.** Keep the current
   dual-M1 B1 throughput forecast unchanged until a generated-token ruler is
   posted or measured locally.
3. **Flash-Next Metal software headroom is stronger than before.** QSA
   scoring/indexer, selected-K/V decode, PLE/GDN/hyperconnection projection,
   and MTP prefix-state restoration are high-priority single-node seams.
4. **Mixed per-projection quantization is increasingly credible for a separate
   capacity/performance track.** It remains outside the exact-Q8 P69 campaign.
5. **Operational PP2 bring-up now has concrete requirements:** internal NVMe
   for long-lived mmaps, explicit TB4 TSO configuration, removal of hidden
   memory hogs, and stage-local recurrent/session checkpoints.
6. **27B exact frontier is unchanged.** Certified P69B12 remains frozen and
   **P69B13 remains next using existing profiling data only.**
