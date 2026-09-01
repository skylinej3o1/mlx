# Runtime Research Watch — 2026-09-01 Late Afternoon

Scope: external runtime/model research only. This note does **not** modify the certified P69 verifier state. **P69B13 remains next, using existing profiling data only.**

This is a delta from `RESEARCH-WATCH-2026-09-01-AFTERNOON.md`.

## Qwen3.8-Flash-Next

### oMLX #3355 — gathered-QSA prefill remains nearly flat through 220K after mRoPE rebind fix

PR: https://github.com/jundot/omlx/pull/3355

A Qwen4 text-prefill correctness rebind had an unintended performance consequence: ordinary text positions were being exposed as rank-three `(3,1,T)` mRoPE state. The gathered-QSA gate accepts canonical rank-two `(1,T)` text positions and therefore silently fell back to the slower official/dense route. Real agent traffic tapered from roughly 862 tok/s around 4–8K to ~510 tok/s around 40K and ~479 tok/s near 49K.

The fix keeps scheduler-proven B1 text positions in canonical rank-two form while rebinding each request's mRoPE delta before every external/interleaved prefill. Media, B2, generic models, and unproved shapes fail closed.

Physical M3 Ultra validation with fresh unique-salt, zero-cache B1 text:

- 19,992 uncached tokens: **892.56 tok/s**
- 219,994 uncached tokens: **885.27 tok/s overall**
- windowed pure model throughput: **944.69** at 0–8K, **907.60** at 40–49K, **891.63** at 98–106K, **880.05** at 147–155K, **866.86** at 196–205K, **851.68 tok/s** at 213–220K
- exact cached repeat: 19,991/19,992 tokens reused, **0.15 s model TTFT / 0.47 s visible TTFT**, identical output SHA-256

The repaired curve loses only about 9.8% from the first 8K window to the 213–220K window.

Implication for the dual-M1 project: long-context prefill decay is increasingly dominated by runtime path selection and bookkeeping rather than an unavoidable Flash-Next architecture wall. Do not scale M3 Ultra throughput directly to M1 Max, but explicitly certify that request-local mRoPE state does not demote the gathered/sparse path during interleaved multi-agent prefills.

### oMLX #3360 — unfinished reasoning must remain private across speculative rollback

PR: https://github.com/jundot/omlx/pull/3360

This is a protocol/correctness result, not a performance result. A reasoning model could sample a model-owned terminal token before emitting its closing reasoning marker; oMLX could then turn accumulated unfinished private reasoning into visible assistant content.

The patch:

- masks only model-owned terminal tokens while a prompt-opened reasoning block remains active
- restores normal EOS immediately after the natural close marker
- preserves explicit caller stop tokens and overlapping close markers
- retains processor state across speculative MTP snapshot/rollback
- never promotes unfinished reasoning into visible content
- reports malformed OpenAI, Anthropic, and Responses streams as incomplete

Validation reports 557 passed / 3 deselected.

Implication for the multi-agent certification plan: speculative state qualification is not only KV/GDN numerical rollback. Stateful protocol processors must also snapshot/restore correctly. Add an explicit reasoning-boundary + rollback + cancellation/tool-stream gate to the persistent-agent soak.

### Single-GB10 comparison lane — no newer commit after Aug 30

A fresh commit scan of the tracked single-GB10/Spark repositories found no Sep 1 change that supersedes the current comparison ruler.

The newest material tracked in `hashd1ve/qwen38-flash-next-one-dgx-spark` remains the Aug 30 KDA/QSA update. Its commit reports exact 9/9 needle retrieval at 120K/190K/210K and **46–92 tok/s decode after those long prompts**, compared with 30–48 tok/s before that kernel update, while short-context decode was unchanged.

This remains architecture/runtime evidence for long-context sparse-attention headroom, not a dual-M1 projection.

## DeepSeek V4 Flash 0731

### DS4 #915 — verify correctness must match decode policy; tiny speculative widths can be slower than plain decode

PR: https://github.com/antirez/ds4/pull/915

Two useful findings on DeepSeek V4 Flash / M5 Max / Metal:

1. **Decode and verifier sparse thresholds diverged.** Single-token decode used a 1024 compressed-row threshold while verify-shaped batches switched to indexed top-512 above 512 rows. For `n_comp` in (512,1024], verifier and decode could therefore attend to different candidate sets. A new real-weight boundary test measured `worst_argmax_gap=0.939` before the fix and **0.000 after**.
2. **A bare one-draft acceptance should skip the batched verifier.** When `draft_n==1`, nothing remains to verify after accepting position 0. The old path still paid for a full 43-layer batch verifier. The patch commits the token and gets next logits through plain decode instead. The reporter's machine measured roughly **23 ms/token plain decode versus ~48 ms/call batched verify for n_tokens=2–5**. Five stochastic prompts were bit-identical with the fast path enabled/disabled.

Implication for Flash-Next scheduling: the controller should compare actual verifier cost against plain target decode by `(verify width, context, concurrency, hardware)` rather than assuming every nonzero draft span is profitable. This reinforces the earlier M1 Ultra result where batched depth-1 MTP became net-negative at high concurrency.

For MXFORGE bring-up, record a width-cost table before tuning acceptance policy:

- target-only B1 step cost
- verify width 2/3/4/5/6 cost
- draft-head cost
- accepted tokens/cycle by workload
- context and concurrency at each measurement

Then choose speculation only when expected accepted-token value clears the measured target-only alternative.

## Qwen3.8-27B exact verifier track

Layr challenge: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge

Fresh PR search still shows:

- frontier **3.7291100105909**
- #1481 newest visible submission
- #1481 remains a blind, non-Apple-measured elementwise-fusion proposal
- no #1482+ promoted result found

No external evidence changes the frozen exact-Q8 plan. **P69B13 remains next, existing profiling data only.**

## Updated decisions

1. **Dual-M1 topology stays PP2-first.** Nothing in this pass resurrects TP2 over TB4 as the primary deployment.
2. **Long-context Flash-Next confidence improves qualitatively, not as a new M1 speed forecast.** #3355 shows ~220K prefill can remain nearly flat on a correctly routed Metal path, but the hardware is M3 Ultra.
3. **Speculation must be economically gated by measured width cost.** DS4 #915 is direct evidence that a nominal verifier path can cost more than plain decode at small widths.
4. **Persistent-agent qualification must include protocol state.** Reasoning-boundary processors, stop-token state, rollback, cancellation, tool streams, and re-prefill all need soak coverage alongside KV/GDN state.
5. **Keep the mature dual-M1 >=40 tok/s B1 planning confidence around the prior ~85%.** No exact dual-M1 throughput receipt appeared in this pass.
6. **Single-Spark/GB10 remains the external multi-agent ruler; no newer Sep 1 commit superseded the current baseline in this scan.**
7. **27B certified verifier state is unchanged.** Do not reopen closed P69 seams from external speculation.
