# Project 51 external runtime watch — 2026-09-20 10:50 ET

**Hard freshness window:** strictly after **2026-09-20 13:58:56 UTC** through the user's message cutoff **2026-09-20 14:50:36 UTC**.

## Decision

**No numeric target/confidence change.** Keep **40 TG @ ~128K / 400 genuinely cold PP** on 2x M1 Max 64 GB / TB4.

This short window still produced two high-value correctness/performance items: a direct Apple Flash verify-fusion fix in oMLX and a new warmup/cache-pointer lifetime bug in vLLM. The fixed-token prefill-scoring work that missed the prior cutoff is now eligible as an UPDATE.

## NEW — oMLX #3776 restores fused Qwen4/Flash GDN verify prework with bit-exact L2 normalization

Source: https://github.com/jundot/omlx/pull/3776  
Created **2026-09-20 14:11:04 UTC**.

This is the concrete implementation follow-up to the #3771 regression already in state.

After mlx-vlm #3719, Qwen4Exp's verifier uses an L2 normalization path, while the fused GDN verify prework gate still expected the Qwen3.5 RMS normalization method. The gate therefore never opened and every T=4 verify cycle fell back to the unfused conv -> SiLU -> split -> normalize sequence.

The PR does **not** simply weaken the compatibility check. It adds a Qwen4 L2 kernel variant that reproduces the stock chain bit-exactly at the relevant rounding sites:

- bf16 per-element squares;
- sequential bf16 partial sums over four contiguous elements;
- fp32 xor-tree reduction;
- one final bf16 rounding;
- bf16-rounded epsilon/scalar inputs to `metal::precise::rsqrt`.

Apple Silicon, MTP T=4, `pp65536/tg128`:

- verify backbone: **38.9-43.2 -> 33.7-36.1 ms/cycle**;
- restored to the reported pre-upgrade **33.5-34 ms** band;
- acceptance unchanged at roughly **70-77%**.

The fallback had been roughly **10 extra dispatches x 64 layers per verify cycle**.

**Project 51 rule:** fast-path eligibility needs semantic capability checks **and** exact numerical-contract checks. When the model's reference normalization changes, add a matching fused variant rather than bypassing the gate. Log first-use/rejection diagnostics so a fused path cannot silently disappear for days.

## NEW — vLLM #57807: dummy warmup can capture temporary cache pointers into persistent runtime context

Source: https://github.com/vllm-project/vllm/pull/57807  
Created **2026-09-20 14:25:12 UTC**.

Hybrid/Mamba aligned-attention metadata and state-copy code shared one lazily initialized context. Dummy graph warmup can run metadata preparation before real state preprocessing; whichever path initializes the context first captures block-table pointers.

If warmup initializes it against temporary graph-profiling cache groups, those pointers can survive into real cache allocation and make correctness depend on call order.

The fix:

- gives aligned-attention metadata and state-copy separate contexts;
- preserves stable pointer ownership for each;
- explicitly releases both during graph-profiling teardown so temporary cache layout/pointers cannot escape into serving.

**Project 51 `sup` consequence:** prewarming kernels is not allowed to create serving-state objects that retain temporary buffer/cache/table addresses. Separate **compile/warmup artifacts** from **live request-state bindings**, and assert teardown/rebind before real PP2/QSA/recurrent state is admitted.

## UPDATE — vLLM #54335 fixed-token prefill scoring is now inside the watch window

Source: https://github.com/vllm-project/vllm/pull/54335  
Updated **2026-09-20 14:00:29 UTC**.

This item was intentionally deferred in the prior watch because it landed just after that cutoff.

It scores a caller-selected set of token IDs only on selected causal prefill rows and reuses the existing fp32 logprob reduction kernel instead of materializing a full `[rows, vocab]` result.

Current performance example, Qwen3-30B-A3B, TP4, 8192-token prompt:

- baseline: **75.2 ms**;
- 1000 rows x 64 IDs: **77.1 ms (+2.0 ms)**;
- 1000 x 242: **77.7 ms (+2.6 ms)**;
- 4000 x 242: **81.7 ms (+6.6 ms)**;
- existing full-row `prompt_logprobs=0`: **146.2 ms (+71.0 ms)**.

The current implementation is **not** a full score-only serving lifecycle and explicitly does not support prefix-cache reads. It is nevertheless useful mechanism evidence that small candidate sets can be scored much more cheaply than generic full-vocabulary/full-row logprob plumbing.

A correctness fix in this update also rejects scoring when resumed/prefix-reused prefill starts past the first requested scored row instead of returning a correctly shaped array containing unwritten/fabricated leading rows.

**Project 51 consequence:** closed-set routing/failure classification should compute only the answer-token logits it needs. But a P51 implementation must bind this to the **warm checkpoint's actual final row**, not fabricate results for rows skipped through prefix/session reuse.

## UPDATE — vLLM #56984: per-row candidate scoring makes API representation itself a measurable cost

Source: https://github.com/vllm-project/vllm/pull/56984  
Updated **2026-09-20 14:00:50 UTC**.

Per-row candidate-ID tables are represented as a contiguous NumPy array rather than nested Python lists. For a 4000 x 1024 request, the reported API-side comparison was:

- validation: **235 -> 30 ms**;
- deepcopy: **812 -> 1.5 ms**;
- msgpack encode/decode: **42/104 ms -> ~0** via zero-copy array transport;
- worker padding: **115 ms -> none**.

The table itself can then dominate at very wide shapes: 4000 x 1024 int64 is 32 MB per request.

**Project 51 rule:** agent-control scoring should keep candidate domains tiny and tensorized. Avoid Python-object/nested-list control planes for per-row metadata; serialization/copy cost can dwarf the actual scoring kernel.

## Screened / no target-changing evidence

- **DS4:** no new default-branch commit in the strict window; #1089 remains the current rewindable-session evidence.
- **oMLX:** #3776 is the relevant new Flash item; no new default-branch merge yet.
- **mlx-serve:** several older merged PRs received metadata/update timestamps around 14:14, but their substantive measurements/commits predate this window; they are **not reclassified as new**. #449's actual commits remain September 17.
- **llama.cpp:** no cutoff-qualified Project-51-relevant default-branch commit. #29180's substantive creation was before the boundary.
- **Splash:** no new commit after the boundary before the cutoff.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no activity.
- **MTPLX:** no post-boundary commit.
- **APEX:** no post-boundary commit.
- **npanj/llama.cpp:** no post-boundary commit.
- **Current Reddit/Hugging Face/community search:** no substantive source timestamped inside this exact 51-minute window that adds an exact M1/TB4 or Flash quant receipt.
- No new exact **2x M1 Max 64 GB / TB4 / ~128K / P51 mixed quant + MTP** physical throughput receipt appeared.

## Target impact

**No change.**

The direct oMLX fix strengthens confidence that a material portion of recent Flash MTP regression is recoverable runtime overhead rather than a model limitation, but it is M5-class Apple evidence and not a dual-M1/TB4 throughput receipt.

**New hard boundary: 2026-09-20 14:50:36 UTC.**
