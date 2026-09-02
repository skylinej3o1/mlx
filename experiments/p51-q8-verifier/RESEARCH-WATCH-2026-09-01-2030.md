# Runtime Research Watch — 2026-09-01 20:30 ET

Scope: full-context correction plus genuinely fresh external deltas for
Qwen3.8-Flash-Next, Qwen3.8-27B, and DeepSeek-V4-Flash/DS4.

This pass was intentionally performed **after** scanning every formal architecture/runtime
watch currently in the branch and recovering older project context.

It does **not** modify the certified P69 state. **P69B12 remains promoted/frozen and
P69B13 remains next using existing profiling data only.**

## Context-lineage correction

The 2026-09-01 Night note described DS4 issue #607 as a newly found missing dual-M1 TG
anchor. That classification was wrong.

DS4 #607 had already been found, discussed, and used as an empirical dual-M1 anchor in
the project on 2026-08-01. What was actually missing was **persistence into the later
formal `RESEARCH-WATCH-*` chain**. It had fallen out of the repo research notes, and
`RESEARCH-WATCH-LATEST.md` was stale at Early Evening, which made a later pass capable
of rediscovering an old source as though it were new.

The underlying measurements remain valid and useful:

- exact 2x M1 Max 64 GB / TB4 hardware class;
- pre-0731 DS4 q2-q4 model;
- ~10.0 tok/s long-document decode;
- ~11.0-12.95 tok/s short-code decode;
- ~153.7-162.7 tok/s long-prompt prefill.

But the correct label is now **KNOWN SINCE 2026-08-01**.

To prevent recurrence, this pass creates:

`experiments/p51-q8-verifier/RESEARCH-STATE.md`

That file is now the durable baseline that must be read before future research passes.

## Fresh delta — llama.cpp #28213, selected-K/V QSA gather

Source: https://github.com/ggml-org/llama.cpp/pull/28213

This is a newer qwen4exp QSA implementation than the earlier masked sparse-attention
work already recorded.

Instead of selecting ~2048 history positions and then running attention over the full KV
history with a mask, it gathers only the selected K/V rows into a compact buffer and runs
attention on that compact set.

Dual RTX A6000, IQ4_XS, q8 KV, temp 0:

- 31K context: 36.5 -> 38.5 tok/s (+6%)
- 62K: 26.5 -> 31.6 tok/s (+19%)
- 130K: 15.7 -> 23.6 tok/s (+50%)

At 130K it also removes roughly 17 MB of attention-mask upload per decoded token.

This is not M1/Metal evidence, but it materially strengthens the architectural case that
**gathered selected-K/V decode is the right long-context QSA shape** rather than merely
optimizing a full-context masked implementation.

## Fresh status change — oMLX #3320 requires requalification

Source: https://github.com/jundot/omlx/pull/3320

The long-context direct-QSA / wide-MTP work now remains draft behind a technical
requalification gate. A later low-margin workload exposed a parity failure in prior fast
wide-verifier evidence, so the experimental path is not being promoted until exact
output-hash, cache-state, selector, prefill, and decode gates are refreshed across the
10K-220K range.

The previously recorded high-acceptance M3 Ultra results remain valuable as architecture
signal, but they should carry less weight in aggressive two-M1 throughput forecasting
until the requalification passes.

This is the main reason the >=40 and >=45 B1 confidence bands are trimmed slightly in the
new canonical state.

## Fresh 27B serving updates — oMLX #3364/#3365

Sources:

- https://github.com/jundot/omlx/pull/3364
- https://github.com/jundot/omlx/pull/3365

These repair Qwen3.8-27B ANE long-prefill memory admission/escalation. A stale transient
reserve and a no-op first retry could prevent escalation to the bank-release rung.

With the source repair, a 65,536-token Qwen3.8-27B oQ4e-mtp benchmark completes at
roughly 397 tok/s where the captured v0.6.4 path could reject at 4,096 tokens.

This is operational/serving headroom, not an exact-P69 decode result.

## DS4 0731 exact dual-M1 follow-up

Source: https://github.com/antirez/ds4/issues/922

Rechecked the full comment thread specifically for the missing decode number.
There is still only one follow-up: the external-USB mmap root cause, internal-NVMe fix,
TSO=0 note, and successful 34K prefill+generation completion.

**No completion-token count or sustained decode TG has been added.**

Do not infer TG from the 257-second total.

## DS4 distributed architecture calibration

Fresh DS4 scan does not change the PP2-first decision.

PR #861 on two Strix Halo nodes provides another topology comparison:

- layer-split pipeline mode: ~222 tok/s average prefill / 260 peak and 13.6 tok/s decode;
- TP over the same Thunderbolt/USB4-class link remains communication/gate-RTT bound despite
  substantial transport work.

Different hardware/model path, but the qualitative result matches the older dual-M1 #607
anchor: pipeline/layer split minimizes link traffic, while frequent per-layer collectives
are hostile to this class of interconnect.

## Qwen3.8-27B exact frontier

Fresh check:

- Layr best remains `3.7291100105909`;
- #1481 remains the newest visible submission;
- no #1482+ promoted result.

No exact external result changes P69B13 selection.

## Updated planning ladder

The canonical confidence ladder is now maintained in `RESEARCH-STATE.md`.

Short/medium-context mature dual-M1 Flash-Next B1:

- >=30 tok/s: ~90%
- >=35 tok/s: ~75-80%
- >=40 tok/s: ~55-60%
- >=45 tok/s: ~30-35%
- >=50 tok/s: ~15%

Long-context (~128K active) B1:

- >=20 tok/s: ~85%
- >=25 tok/s: ~65%
- >=30 tok/s: ~40%
- >=35 tok/s: ~20%

Mature B2-B4 aggregate:

- >=50 tok/s: ~90%
- >=60 tok/s: ~80%
- >=70 tok/s: ~65%
- >=80 tok/s: ~45%
- >=90 tok/s: ~25%

These are engineering planning probabilities, not statistical confidence intervals.

## Decision

1. DS4 #607 is restored as a **historical known anchor**, not a new result.
2. Future searches must start from `RESEARCH-STATE.md` plus all newer deltas.
3. `RESEARCH-WATCH-LATEST.md` must be updated on every useful pass.
4. Exact dual-M1 0731 and Flash-Next decode TG remain the two most valuable missing
   measurements.
5. Gathered selected-K/V QSA gets a stronger priority for long-context Flash-Next.
6. Aggressive MTP extrapolation is slightly de-weighted until oMLX #3320 requalifies.
7. P69 exact state is unchanged: P69B13 remains next.
