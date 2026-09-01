# External runtime watch — 2026-09-01 early AM

This is a delta-only follow-up to the 2026-08-31 Qwen + DS4 research watch. It records external runtime evidence relevant to the separate Qwen3.8-Flash-Next dual-M1 research plan while preserving the certified P51/P69 exact-Q8 verifier state.

These are upstream/community measurements, not results produced by this repository. Do not turn them into local performance claims without reproduction.

## Executive delta

- Qwen3.8-27B Layr-Labs MTP frontier remains `3.7291100105909`; PR #1481 remains the newest visible submission. Nothing changes P69B13 selection.
- Flash-Next recurrent rollback looks more solvable than the previous checkpoint suggested: llama.cpp PR #28123 adds the missing qwen4exp convolution snapshot planes, explicitly covering both GDN QKV convolution state and the PLE convolution row. This materially lowers the implementation-risk side of native MTP, but its published test is still one slot, so it does not retire multi-sequence / multi-agent rollback risk.
- Flash-Next long-context decode still contains large runtime taxes unrelated to the neural architecture. A new gather-based QSA proposal (#28130) turns QSA top-k from mostly a mask/memory optimization into actual sparse attention compute and reports +41–45% generation at ~129.6K on 2x RTX A6000. Combined with neighboring CPU/TOP_K fixes, the same stack reports +75% versus master at that depth.
- A new flat-position KV lookup proposal (#28128) reports 17 -> 19.7 tok/s at ~130K by removing a `std::set` walk that consumed ~17% CPU at long context.
- Batched CUDA TOP_K routing (#28129) reports roughly +20–27% prompt-processing throughput at 30K–130K by avoiding hundreds of serial per-row DeviceTopK launches. This reinforces the rule that shape-aware routing matters: the best B1 kernel need not be the best large-batch kernel.
- An independent dual-RTX-5090 target-only deployment has passed a resident 20-turn soak plus exact three-needle retrieval at 260,998 input tokens with MTP disabled. This is a useful control: target-only service stability can be strong while speculative/recurrent state remains the higher-risk subsystem.
- DeepSeek-V4-Flash-0731 has no new distributed-topology receipt that supersedes the prior watch. The existing target-only TP versus speculative-PP lesson remains intact.

## Flash-Next: recurrent rollback now snapshots qwen4exp custom convolution state

llama.cpp PR #28123 (`qwen4exp: support recurrent state rollback`) is the clearest response yet to the rollback gap documented in issue #28019.

The important detail is that merely adding `LLM_ARCH_QWEN4EXP` to the recurrent-rollback allowlist is not sufficient. qwen4exp overrides the shared convolution-state write through `build_conv_state_at()`, and that implementation previously wrote only the current plane. A rollback could therefore restore SSM/GDN state beside convolution history that had never been snapshotted.

The proposal writes one convolution snapshot per rollback slot, mirroring the shared DeltaNet path, and explicitly covers both:

- the delta-net QKV convolution state; and
- the PLE convolution state.

Published RTX PRO 6000 / MTP / n-max=3 / one-slot numbers:

| configuration | decode |
|---|---:|
| no draft | 108 tok/s |
| before rollback fix, code | 123 tok/s |
| before rollback fix, prose | 83 tok/s |
| after rollback fix, code | 183 tok/s |
| after rollback fix, prose | 144 tok/s |

The 83 tok/s prose result is important because it is slower than the 108 tok/s no-draft target; incomplete rollback economics can make otherwise-valid MTP a regression.

Source: https://github.com/ggml-org/llama.cpp/pull/28123

### Dual-M1 implication

This strengthens the intended PP state-ownership design:

1. every stage owns its recurrent/PLE state locally;
2. every speculative rollback slot must include all architecture-specific recurrent state, not merely generic GDN arrays;
3. Thunderbolt carries activation rows and small propose/accept/commit metadata, not recurrent snapshots.

It also sharpens the multi-agent qualification gate. PR #28123 reports one slot only. Do not consider native MTP production-qualified until 2–5 sequence split/replay tests pass and repeated partial/full rejection patterns reproduce the same target trajectory.

## Flash-Next: QSA sparsity can become real compute sparsity

llama.cpp PR #28130 (`qwen4exp: gather-based sparse attention for QSA decode`) profiles a major inefficiency in the current qwen4exp decode graph: the QSA indexer chooses a sparse set, but decode still builds a full-`n_kv` mask and runs attention over the full KV cache. In that implementation, the top-k selection saves mostly memory/selection semantics rather than attention compute.

The proposed decode-only path:

1. computes block-level top-k over indexer scores;
2. maps selected blocks to cell indices;
3. gathers K/V and compact mask values for the selected cells;
4. runs dense attention over roughly the selected ~2K cells rather than the whole history.

It also removes a reported ~18 MB of host-to-device mask traffic per token at 141K and skips an O(n_kv) host `cell_blk` fill when the graph does not consume it.

Reported 2x RTX A6000 / UD-IQ4_XS / Q8 KV / B1 temp-0 results:

| KV depth | master masked path | gather path |
|---:|---:|---:|
| 30.8K | 36.4 tok/s | 39.3–42.4 tok/s |
| 61.8K | 25.4–26.9 tok/s | 27.6–34.3 tok/s |
| 129.6K | 16.9–17.0 tok/s | 23.8–24.7 tok/s |

At 129.6K that is a stated +41–45%. Combined with #28128 and #28129, the author reports 29.8 tok/s, about +75% versus master at the same depth.

Retrieval/factual tests were reported md5-identical between the masked and gather paths at tested depths. Long open-ended generation can diverge after ~150 tokens, but the author reports the same run-to-run floating-point nondeterminism on unpatched master; that is not proof of universal equivalence and should be requalified per backend.

The PR was closed without merge shortly after submission because of contribution-process issues (new-contributor open-PR limit / template / AI-description policy), not because the published mechanism was benchmark-refuted. Treat it as an unmerged research receipt, not upstream capability.

Source: https://github.com/ggml-org/llama.cpp/pull/28130

### MXFORGE / Apple implication

Do not model QSA as one opaque attention timer. Profile these separately at 32K/64K/128K/262K:

- indexer score;
- pooled-key maintenance;
- head reduction;
- TOP_K;
- selected-cell construction;
- K/V gather;
- sparse-window attention;
- host mask/index bookkeeping.

Apple Metal radix TOP_K has already landed upstream, so benchmark that before building a competing selector. A more interesting remaining seam is incremental pooled-key state: #28130 still recomputes pooled block keys from the raw indexer cache every QSA layer/token, leaving O(n_kv) work after sparse attention itself is bounded.

This evidence makes the long-context outlook more optimistic, but it does not justify multiplying the dual-M1 short-context forecast by CUDA/A6000 gains.

## Flash-Next: long-context CPU lookup remains material

llama.cpp PR #28128 (`kv-cells: scan the flat pos array instead of walking the used std::set`) reports that walking the used-cell `std::set` consumed roughly 17% CPU at long context. Replacing it with a flat position-array scan preserved cell order and produced identical outputs in the stated test.

Reported ~130K decode:

- before: ~17 tok/s;
- after: ~19.7 tok/s.

Source: https://github.com/ggml-org/llama.cpp/pull/28128

This reinforces the existing #28011/#28040 lesson: once the active neural compute becomes cheap, host-side cache/index bookkeeping can dominate. For the Apple implementation, profile CPU wall time and GPU idle gaps explicitly rather than assuming long-context slowdown is a Metal bandwidth problem.

## Flash-Next: batch-shape-specific TOP_K routing

llama.cpp PR #28129 finds the opposite shape problem on CUDA prompt processing. With CCCL >= 3.2, `DeviceTopK` was invoked serially per row; a ~141K qwen4exp prefill reportedly produced ~903,702 DeviceTopK invocations across 512-row ubatches and 12 QSA layers.

The proposal keeps DeviceTopK for small row counts and routes larger batches through the existing row-parallel argsort/copy path.

Reported 2x RTX A6000 prompt-processing results:

| prompt tokens | serial per-row path | batched path |
|---:|---:|---:|
| 30,802 | 758–781 tok/s | 921–923 tok/s |
| 61,767 | 675–698 tok/s | 872–874 tok/s |
| 129,584 | 563–580 tok/s | 712–713 tok/s |

Source: https://github.com/ggml-org/llama.cpp/pull/28129

The transferable rule is not the CUDA number. It is: **route by geometry**. Microbench winners at B1/small-row shapes can lose badly when prefill supplies hundreds of rows.

## Target-only control: dual RTX 5090 deep soak

The public `furedericca-lab/Qwen3.8-Flash-Next-dual-5090` deployment is useful primarily as a qualification control, not as a hardware comparison to Apple.

Documented profile:

- 2x RTX 5090 32 GB + 48 GB host RAM;
- AD-4.27bpw Q4_K_M-M64 model profile;
- layer split 1,1;
- Q8_0 K / Q8_0 V;
- 261,888 configured context;
- MTP explicitly excluded from the baseline.

The repository reports:

- resident deterministic 20-turn soak: PASS;
- exact EARLY/MIDDLE/LATE three-needle recall at 260,998 input tokens: PASS;
- short `tg128`: 85.967972 tok/s;
- `pp512`: 334.135611 tok/s.

Source: https://github.com/furedericca-lab/Qwen3.8-Flash-Next-dual-5090

This complements the previously documented withdrawn dual-GB10 speculative profile. The lesson is not that one runtime is universally safer than another; it is that target-only long-context correctness can survive a meaningful soak while speculative/recurrent paths introduce additional state-machine failure modes. Keep target-only as an independent certification control throughout MTP bring-up.

## Qwen3.8-27B verifier watch

No promotion change.

- Layr-Labs current best remains `3.7291100105909`.
- #1481 remains the newest visible candidate.
- It is still unmeasured/blind from the submitter's non-Apple environment.
- No new result justifies reopening P69B8, P69B9, P69B10-C, or changing P69B13 selection.

Verifier campaign remains governed by `CURRENT.md` / `STATUS.md` and the local exactness/paired-certification rules.

## DeepSeek-V4-Flash-0731 watch

No new distributed topology receipt supersedes the prior checkpoint.

Retain the existing control-case lesson:

- target-only TP can win when enough per-layer compute amortizes collectives;
- speculative verification can invert those economics because every verify row multiplies communication/synchronization work;
- layer/pipeline parallelism becomes attractive when a whole multi-row verify span can cross a coarse stage boundary instead.

Do not generalize either TP or PP into a universal rule across architectures/execution modes.

## Decision update

For the 2x M1 Max 64 GB Flash-Next research plan:

1. **PP2 remains primary.** Nothing here resurrects TB4 TP as the preferred topology.
2. **Distributed native MTP looks more tractable.** #28123 identifies and snapshots the custom PLE/GDN convolution state that made allowlist-only rollback incorrect.
3. **Multi-agent rollback remains unretired risk.** One-slot success is not 3–5-slot split/replay correctness.
4. **Long-context upside is larger than the current naive runtime suggests.** #28130 demonstrates that QSA selection can actually bound attention compute instead of merely constructing a sparse mask over dense attention.
5. **Profile host bookkeeping aggressively.** #28128 and earlier predecessor-index work show CPU data structures can consume double-digit percentages of long-context decode.
6. **Benchmark existing Metal radix TOP_K first.** Do not spend MXFORGE effort re-inventing a selector before measuring the newly upstreamed path.
7. **Keep a target-only control server/profile.** MTP qualification must prove repeated tool-turn re-prefill, partial/full rejection, compaction/restore, and 2–5 concurrent sequence replay against that control.
8. **Do not change the P69 campaign.** P69B13 remains next using existing profiling only.
