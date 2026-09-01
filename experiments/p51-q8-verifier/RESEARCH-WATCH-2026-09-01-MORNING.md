# Runtime Research Watch — 2026-09-01 Morning

Scope: external runtime/model research only. This note does **not** modify the certified P69 verifier state. P69B13 remains next, using existing profiling data only.

## Qwen3.8-Flash-Next

### oMLX #3351 — long text mRoPE prefills can stay on gathered QSA

A pure-text Qwen4Exp continuation with roughly 233,472 cached prefix tokens plus a ~5,244-token follow-up had been rejected by the memory guard because it was priced like dense SDPA. The fix recognizes broadcast-identical three-plane text mRoPE as valid for gathered QSA while unequal planes fail closed.

- Static long-Q=4096, KV=233472 estimate: ~4.04 GiB gathered versus ~46.41 GiB dense.
- The original ~5K continuation after the ~233K cached prefix now proceeds instead of failing memory admission.
- This is primarily a long-session memory / continuation / TTFT robustness improvement, not a decode-TG claim.

Source: https://github.com/jundot/omlx/pull/3351

Implication: 200K+ cached-prefix agent continuations look increasingly practical without pricing every long pure-text re-prefill as dense attention.

### oMLX #3352 — fixed MTP depth is a useful instrument, not the default policy

Physical M3 Ultra, Qwen3.8-Flash-Next oQ4e, single-stream prose around 10K context:

- adaptive depth <=5: ~52.4 tok/s
- fixed depth 5: ~55.5 tok/s, roughly +6%
- fixed-depth acceptance by position was approximately 0.74 / 0.65 / 0.61 / 0.55 / 0.45, yielding only about 2.8 useful committed draft tokens per target cycle.
- Tool/rewrite workloads can sustain roughly 3.1 committed draft tokens/cycle at ~87–92% acceptance, where the adaptive controller re-centers appropriately.

Source: https://github.com/jundot/omlx/pull/3352

Implication: do not globally pin max MTP depth. Workload-aware adaptive speculation remains the better production policy; fixed-depth mode is valuable for controlled A/Bs.

### oMLX #3330 — Fusion warm-turn evidence expanded materially

The same Fusion line now has stronger persistent-agent evidence on M3 Ultra:

- rewritten-turn visible TTFT: ~4.17 s off -> ~0.62 s on (~6.7x)
- matching terminal turn: ~0.47 s
- tool follow-up: 18,445 / 18,487 prompt tokens cached, ~0.51 s total
- cold ~9,994-token prompt: ~907.7 tok/s PP; 500-token decode ~74.36 tok/s at ~98.2% MTP acceptance
- a low-acceptance recovery path can park/retry after 128 native tokens, recover to ~95.7% acceptance, finish around 50.11 tok/s, and retain the exact output hash
- B2/B4/B6 multi-request smoke passed with unique markers and zero errors

The PR also adds an exact hybrid ArraysCache+KV provider for Qwen3.8-27B. On a ~4.5K prompt, M3 Ultra rewritten-turn model TTFT fell from ~1.72–1.78 s to ~0.24 s; visible TTFT fell from ~1.89–1.94 s to ~0.40 s. Snapshot cost was ~10.2–12.2 ms for roughly 0.42 GiB, and exact-resident / paged-fallback paths were byte-identical.

Source: https://github.com/jundot/omlx/pull/3330

Implication: persistent-agent warm-turn latency keeps improving independently of the decode ruler. This is especially relevant to Tameru-style compaction, prefix reuse, and durable long sessions.

### llama.cpp #28136 — keep the B1 path synchronous and lean

This patch restricts asynchronous compute scheduling to multi-token batches instead of paying its overhead on B1 single-token decode.

On Qwen3.8-Flash-Next with an RTX Pro 6000, real-run single-token generation improved by roughly 6% on average across short/medium/long contexts, with individual rows reaching ~8%. Multi-token / PP behavior was essentially unchanged.

Source: https://github.com/ggml-org/llama.cpp/pull/28136

Implication: the desired topology becomes even clearer: keep ordinary B1 decode minimal, but use asynchronous overlap where MTP, context drafting, or multi-request batching creates enough rows to amortize scheduling.

## DeepSeek V4 Flash 0731

### ds4 #919 — multiple independent requests in flight through layer-parallel PP

PR #919 adds multi-request pipeline execution so layer-split nodes can work on different independent requests concurrently instead of leaving one stage idle during a B1 request. The author reports testing on two Strix Halo nodes without issue, but does **not** publish a throughput number yet.

Source: https://github.com/antirez/ds4/pull/919

This is qualitative support for the cluster rule we have been converging on: PP becomes materially more attractive as request concurrency rises because independent agent requests fill pipeline bubbles. It does not supersede the existing measured DS4 target-only result where tuned TP beat layer-PP on 2x M3 Ultra.

## Qwen3.8-27B exact verifier track

The external Layr frontier remains **3.7291100105909**. PR #1481 remains an unmeasured compiled/shapeless elementwise-fusion proposal without a new Apple-Silicon score.

Source: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1481

No external result from this pass changes P69B12 or the P69B13 selection. oMLX #3330's repeated-turn cache work is relevant to eventual serving, not to the frozen exact-Q8 decode ruler.

## Current decisions

- Dual-M1 Flash-Next primary topology remains **PP2 + coarse native MTP/context drafting + continuous batching + smart cache reuse**.
- Keep one TP2 bring-up benchmark as a falsification test, not as the primary engineering plan.
- Mature dual-M1 >=40 tok/s confidence stays around **~85%**; this pass improves long-context / warm-agent confidence rather than the short-context ceiling.
- 200K+ continuation confidence increases because gathered QSA is now admitted for the relevant text-mRoPE geometry instead of being priced as dense SDPA.
- Adaptive speculation remains preferred over globally pinning maximum draft depth.
- 3–5 concurrent agents should help PP utilization by filling pipeline bubbles, but this remains a benchmark requirement rather than a claimed speedup on M1.
- The certified 27B exact-Q8 verifier plan is unchanged: **P69B13 next, existing profiling data only**.
