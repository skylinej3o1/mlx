# Runtime Research Watch — 2026-09-02 05:30 ET

Scope: fresh delta after `RESEARCH-WATCH-2026-09-02-MIDNIGHT.md`, with canonical-state-first classification. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B, and DeepSeek-V4-Flash/DS4, especially 2x M1 Max 64 GB / TB4 and agent-serving economics.

This pass does **not** change the certified exact-Q8 verifier state. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling data only**.

## Executive delta

1. **CORRECTION — #3368 was not a missing new upstream prerequisite.** oMLX closed it without merge because merged #3246 already handled the production ragged-batch QSA offset/indexer path. The midnight note overstated how immature plain Flash-Next B>1 was.
2. **UPDATE — #3369 merged.** The remaining mixed-rank BatchQSAKVCache join hardening (text vs MRoPE position rank and indexer-length vs KV-offset separation) is now on main.
3. **UPDATE — long-context gathered-QSA prefill became materially more production-ready.** #3355 and #3351 landed, preserving gathered text prefill through mRoPE rebinds and pricing gathered QSA correctly in the memory guard, including a 233,472-token cached-prefix / 5,244-token continuation case.
4. **NEW — #3372 gives a measured SSD-PLE decode win.** On M5 Max 128 GB at a 92K warm prefix, batching the SSD-backed PLE sharded-embedding gather measured 35.42 -> 37.32 tok/s (+5.4%, paired). This is especially relevant to the M1 plan because M1 is the class most likely to need selective SSD backing.
5. **NEW CAUTION — #3370 reports Lightning MTP collapsing at temperature > 0.** On M3 Ultra / Qwen3.8-Flash-Next-oQ8-MTP, one user reports ~70.7 tok/s and 100% draft acceptance at temp=0 but ~21 tok/s and 0% acceptance at temp=0.3/0.7. The reporter's proposed root cause (greedy/exact-match acceptance rather than stochastic rejection sampling) is not maintainer-confirmed yet.
6. **KNOWN/UPDATE — #3334 quantifies host-dispatch headroom for B>1.** Compiled B4 decode cuts host dispatch 8.8 -> 2.0 ms (-77%) and pure decode-step time 54.5 -> 44.4 ms (-18%) on M3 Ultra, but controlled HTTP E2E remained 0.93-1.02x, so there is no E2E speed claim yet.
7. DS4 #922 still has no sustained 0731 dual-M1 TG; llama.cpp #27993 still has no dual-M1 Flash-Next throughput/deep-context follow-up; Layr remains 3.7291100105909 with #1481 newest visible.

Net: **B1 confidence stays unchanged. B2-B4 aggregate confidence also stays unchanged from the midnight trim, but the reason changes.** Plain continuous-batching correctness is stronger than we thought; the remaining uncertainty is M1-generation speculative economics and the lack of a direct M1-Max Flash-Next B2/B4 end-to-end receipt.

## CORRECTION — oMLX #3368 was superseded by already-merged #3246

Source: https://github.com/jundot/omlx/pull/3368

Maintainer review closed #3368 without merging. On current main, #3246 already converts a batched QSA offset to the aligned physical index width before the relevant grid is built, and the proposed #3368 tests passed unchanged on main because they exercised a local mask copy rather than the production method.

The more accurate existing foundation is #3246:

Source: https://github.com/jundot/omlx/pull/3246

It merged on 2026-08-29 and fixed the real continuous-batching join chain:

- honor model-owned `to_batch()` when a warm QSA singleton joins a running batch;
- use aligned scalar past length for ragged QSA batches;
- skip singleton MTP fold on mid-cycle joins;
- slice indexer arrays correctly during BatchQSAKVCache trim.

Physical M3 Ultra validation in #3246 ran a 14K-token request decoding 500 tokens while four short requests joined mid-flight and completed. The follow-up trim fix removed the residual corruption/recovery cycles and reduced observed join latency from up to ~13 s to ~2 s.

### Revised interpretation

The midnight statement that upstream Qwen4-exp was only now acquiring fundamental per-row QSA safety was too pessimistic. Core mixed-length continuous batching had already landed. Keep #3368 only as a rediscovery/superseded diagnostic, not as a current prerequisite.

## UPDATE — oMLX #3369 merged

Source: https://github.com/jundot/omlx/pull/3369

Merged 2026-09-02 08:25 UTC as `2246290a1000ef50317151868b20537dd7e0e4c2`.

It hardens the remaining runtime cache-join seams:

- rank-2 text and rank-3 MRoPE/image positions promote to the widest rank before join;
- merge uses actual indexer length rather than conflating it with KV offset;
- homogeneous normal joins retain the existing path.

This increases confidence that **plain target continuous batching is technically viable on current main**. It is still not a throughput measurement on M1 Max.

## UPDATE — merged long-context gathered-QSA prefill stack (#3355 + #3351)

Sources:
- https://github.com/jundot/omlx/pull/3355
- https://github.com/jundot/omlx/pull/3351

### #3355 — preserve gathered prefill through mRoPE rebinds

Physical M3 Ultra / Qwen3.8-Flash-Next evidence reported:

- 19,992 uncached tokens: 892.56 tok/s;
- 219,994 uncached tokens: 885.27 tok/s overall;
- pure-model windows taper from 944.69 tok/s at 0-8K to 851.68 tok/s at 213-220K;
- exact cached repeat reused 19,991 / 19,992 tokens with 0.15 s model TTFT and identical output hash.

This is not M1 decode evidence, but it demonstrates that the exact gathered-QSA long-prefill route is now a real merged serving path rather than only an experimental branch.

### #3351 — price gathered QSA correctly in the memory guard

The motivating real case had:

- 233,472 cached tokens out of 238,716;
- only 5,244 tokens left to prefill;
- ~147.56 GB current memory;
- old guard prediction 90.45 GB transient, causing a false rejection against a ~214 GB safety cap.

The repaired Qwen4 gathered profile reports a representative 4,096-row / 233,472-KV static charge around **4.04 GB versus 46.41 GB dense**, while keeping image/multimodal paths dense and still charging fixed recurrent state. The merged stack also separates gathered and dense transient history so stale dense spikes do not poison later gathered chunks.

### Implication

Long-agent continuation viability improved materially. Cached long conversations should be much less likely to fall off the exact gathered path or be falsely rejected by admission. This is principally a TTFT/prefill/robustness improvement, not a reason to raise the dual-M1 decode forecast.

## NEW — oMLX #3372 batches SSD-backed PLE gathers

Source: https://github.com/jundot/omlx/pull/3372

Problem:

- PLE sharded embedding gather called `.tolist()` on IDs, forcing a host/GPU synchronization once per forward;
- IDs then triggered per-ID shard scans and serialized mmap faults across many tiny shards.

Change:

- bucket IDs by shard;
- warm all required shards with threaded pread;
- dequantize once;
- maintain a bounded hot-row LRU;
- preserve bitwise equivalence to the upstream row reader in the tested path.

Measured on M5 Max 128 GB, 92K warm-prefix context, 600 generated tokens, paired/interleaved on current main:

- OFF: 35.42 tok/s
- ON: 37.32 tok/s
- delta: +1.90 tok/s / **+5.4%**
- reported 95% CI: [+0.13, +3.78] tok/s

The author also reports +5.9% when stacked on #3320.

### Implication for 2x M1 Max

Do not transfer the M5 absolute rate or percentage directly. The portable lesson is stronger: if the M1 deployment SSD-backs PLE/ngram shards, **avoid a host readback and row-at-a-time mmap-fault loop in the token path**. This becomes a first-class single-node optimization before distributed tuning.

## NEW CAUTION — oMLX #3370 temp>0 Lightning-MTP report

Source: https://github.com/jundot/omlx/issues/3370

User report on M3 Ultra 512 GB / Qwen3.8-Flash-Next-oQ8-MTP, same prompt and ~400 generated tokens:

| Sampling | Acceptance | tok/cycle | Throughput |
|---|---:|---:|---:|
| temp=0 | 295/295 = 100% | 3.88 | ~70.7 tok/s |
| temp=0.3 | 0/387 = 0% | 1.01 | ~21 tok/s |
| temp=0.7 | 0/311 = 0% | 1.01 | ~21 tok/s |

The reporter suspects the current Qwen4-exp MTP acceptance is effectively exact-match/greedy-only instead of proper stochastic rejection sampling. There is no maintainer confirmation yet, so record this as an **operational warning / measurement lead**, not a proven root cause.

### Benchmark change

The eventual M1-Max bring-up must run MTP economics at:

- temperature 0 / deterministic code continuation; and
- the actual sampling configuration intended for agents.

If acceptance collapses under realistic sampling, the serving policy should dynamically disable MTP rather than pay verifier/head cost for ~1 token/cycle.

## KNOWN / still open — oMLX #3334 compiled multi-row decode

Source: https://github.com/jundot/omlx/pull/3334

M3 Ultra, Qwen3.8-Flash-Next oQ4e, B4:

- host dispatch: 8.8 -> 2.0 ms (-77%);
- pure step: 54.5 -> 44.4 ms (-18%);
- bit-exact at 2K and 16K in the controlled checks.

However, repeated HTTP B1/B2/B4/B8 runs were 0.93-1.02x versus control. The PR explicitly makes no end-to-end speedup claim yet. Keep compiled batching as a plausible host-overhead lever, but do not price its isolated -18% step result into the aggregate forecast.

## External no-change checks

### DS4 #922

No newer comment. Exact 2x M1 Max 64 GB / TB4 0731 still has ~152 tok/s 34K prefill and successful generation after the internal-NVMe fix, but **no generated-token count and no sustained TG**.

### llama.cpp #27993

No follow-up after the 2.5K/4K/q8-KV correctness confirmation. The 115K/256K needle run still has no posted result and there is no dual-M1 Flash-Next TG.

### Layr Qwen3.8-27B exact frontier

Unchanged:

- best score 3.7291100105909;
- #1481 newest visible;
- no #1482+ promoted result.

## Forecast consequence

### Short/medium-context mature dual-M1 Flash-Next B1

Unchanged:

| Target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

### ~128K active-context B1

Unchanged:

| Target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate

Also unchanged from midnight:

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

The rationale is refined: **plain batching correctness is now stronger than the midnight note stated**. We retain the trim because the direct M1-generation batched-MTP result remains negative, #3334 has no E2E gain yet, and there is still no actual M1-Max Flash-Next B2/B4 measurement.

## Updated test ladder

For the eventual M1 pair:

1. single-M1 target-only B1;
2. single-M1 MTP B1 at temp=0 and real agent sampling;
3. single-M1 B2/B4 plain target batching on current main;
4. single-M1 B2/B4 singleton-MTP lane vs batched depth-1 MTP;
5. single-M1 SSD-PLE gather A/B if PLE is offloaded;
6. PP2 target-only B1;
7. PP2 MTP B1;
8. PP2 B2/B4/B6 with stage-idle %, acceptance, committed tokens/cycle, and actual TB4 bytes/round.

PP2 remains primary; TP2 remains the controlled falsification benchmark.
