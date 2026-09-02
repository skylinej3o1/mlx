# Runtime Research Watch — 2026-09-02 Midnight ET

Scope: fresh delta after reading `RESEARCH-STATE.md`, the current latest pointer, and the
preceding dated watch. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B, and
DeepSeek-V4-Flash/DS4, with special emphasis on the 2x M1 Max 64 GB / TB4 deployment and
multi-agent serving economics.

This pass does **not** modify the certified P69 verifier state. P69B12 remains frozen and
**P69B13 remains next using existing profiling data only**.

## Executive delta

The important new information is about **concurrency**, not another isolated B1 kernel
record:

1. Two new oMLX Qwen4-exp fixes (#3368 and #3369) show that Flash-Next continuous batching
   still had hard correctness/runtime join failures at B>1. The fixes are foundational
   for real B2/B4, but do not yet provide a new throughput receipt.
2. An older oMLX batched-depth-1 MTP experiment (#3265), newly recovered into our project
   state, includes a highly relevant M1-generation negative result: on M1 Ultra at eight
   concurrent requests, batched MTP measured 36.03-38.50 tok/s versus 57.09 tok/s plain
   batching because draft-head cost was roughly as large as verifier cost.
3. oMLX Cluster v2 (#3118), on much stronger M3 Ultra + M5 Max / TB5 RDMA hardware,
   physically demonstrates that a production distributed MTP server may preserve
   throughput by **serializing the speculative lane** rather than by running N independent
   speculative windows simultaneously. Its final cached B1/B2/B4 aggregate wall rates
   are approximately 75.1 / 75.2 / 73.1 tok/s; the PR explicitly labels this serialized
   throughput arbitration, not simultaneous batched-MTP scaling.
4. Positive counterweight: existing M1 Max Qwen3.8-27B oMLX benchmark records show that
   ordinary multi-row batching can scale aggregate throughput strongly in some configs.
   The exact multiplier is highly runtime/configuration-sensitive, so these are useful
   feasibility anchors rather than a Flash-Next forecast by themselves.

Net: **B1 forecast stays unchanged. B2/B4 aggregate confidence is trimmed.** The two-Mac
agent-server thesis remains good, but the safe architecture is now: prove plain multi-row
batching first, then test whether MTP should be singleton-lane, batched depth-1, or disabled
under concurrency on M1 Max.

## NEW — oMLX #3368: QSA per-row past length unlocks multi-row batching

Source: https://github.com/jundot/omlx/pull/3368

Created after the previous research pass.

The Qwen4-exp indexer treated `BatchQSAKVCache.offset` as though it were one scalar. At
B>1 it is a per-row array. That axis mistake could broadcast score state to
`(batch, batch, blocks)` and then crash when concatenating the real sequence padding.
Batch 1 hid the defect.

The patch:

- normalizes past length to a per-row column;
- builds a true `[batch, seq_len]` grid;
- fixes the related per-row causal/tail/sparse/default-position calculations;
- preserves B1 numerics;
- adds 14 tests that validate selected-mask contents per row, not just shapes.

The PR states the practical consequence plainly: Qwen4-exp deployments with
`max_concurrent_requests >= 2` could die when the continuous batch actually formed and
were effectively forced to clamp concurrency to one.

### Implication

This is excellent news for the *direction* of our B2/B4 plan because the bug is understood
and narrowly fixable. But it also means earlier aggregate forecasts were assuming a path
that was not yet generally runnable upstream. Until this and the companion join fixes are
physically benchmarked on Flash-Next, do not price continuous batching as solved.

## NEW — oMLX #3369: BatchQSAKVCache join correctness

Source: https://github.com/jundot/omlx/pull/3369

Created after the previous pass and follows #3368.

Two additional B>1 runtime-join defects were found:

1. text positions are rank 2 while MRoPE/image positions are rank 3; selecting the first
   non-null sample could make `extend` / `merge` choose the wrong join rank and crash;
2. `merge` used KV offset as if it were also indexer length, which becomes ill-defined for
   per-row array offsets and can silently mis-slice when KV/indexer lengths diverge.

The fix selects the widest position rank, promotes narrower text state when required, and
uses actual indexer lengths rather than KV offsets. Five direct repros pass and existing
Qwen4 compatibility tests remain green.

### Implication

Treat #3368 + #3369 as one **continuous-batching correctness foundation**. They strengthen
confidence that B2/B4 is technically tractable, but provide no throughput multiplier yet.

## RECOVERED OLDER EVIDENCE — oMLX #3265 batched depth-1 MTP

Source: https://github.com/jundot/omlx/pull/3265

This PR predates the current pass, so it is **not classified as new**. It was not present in
our canonical project state and is worth preserving now because its M1 result directly
changes how we should think about agent concurrency.

Design:

- opt-in `OMLX_MTP_BATCHED_VERIFY`;
- depth-1 always-advance speculation across the whole multi-row decode batch;
- default off;
- exact-once sampler contract and per-row recurrent rollback.

Reported M3 Ultra signal:

- Qwen3.8-Flash-Next oQ4e;
- batched acceptance about 56% versus 61% single stream;
- four concurrent requests reported about +70-90% aggregate versus plain batching.

But an independent **M1 Ultra** measurement is the important calibration for us:

- 8 concurrent requests;
- 580 cycles;
- 52.4% acceptance;
- zero fallbacks;
- batched MTP: **38.50 / 36.03 tok/s**;
- plain-batched baseline: **57.09 tok/s**;
- draft-head work: ~12,226 ms;
- verifier work: ~10,196 ms.

The draft head cost approximately as much as verification, so speculation lost badly even
though acceptance was reasonable. The PR author reports a better M3 Ultra cost balance,
but also notes the margin narrows as concurrency rises.

A current review comment also notes that the current head has not yet run CI and should not
land until the batched-verify correctness suite is green.

### Implication for our M1 Max pair

This materially weakens the assumption that **MTP x concurrency** multiplies automatically
on M1-generation silicon. For our benchmark ladder, measure these as separate modes:

1. B1 target-only
2. B1 MTP
3. B2/B4 plain multi-row batching
4. B2/B4 with singleton MTP lane / queued arbitration
5. B2/B4 batched depth-1 MTP

Whichever wins should be the serving policy. Do not make MTP mandatory under load.

## UPDATE / NEW-TO-PROJECT — oMLX Cluster v2 #3118

Source: https://github.com/jundot/omlx/pull/3118

The PR is older, but its large current physical evidence set was absent from our project
research state. It is therefore an **update/new-to-project evidence source**, not a newly
created PR.

Physical reference pair:

- M3 Ultra 256 GB + M5 Max 128 GB;
- direct Thunderbolt 5;
- JACCL/RDMA measured roughly 6.1-6.5 GB/s and 27-31 us.

DeepSeek-V4 physical TP2 results include:

- ~732.49 tok/s average cold prefill at 30K;
- ~684.66 tok/s at 100K;
- non-MTP B1 decode about 29-31 tok/s;
- non-MTP aggregate B1/B2/B4 about **31.22 / 47.35 / 75.22 tok/s**;
- fixed-depth-5 high-acceptance MTP about **79.8-80.6 tok/s raw**.

Later follow-ups repaired ragged verifier widths and agent-concurrency stalls. Critically,
the final MTP-lane policy caps rank decode, prompt admission, and microbatch lanes to one
while MTP is active until true N x M speculative verification exists. Cached physical
B1/B2/B4 aggregate wall rates become approximately:

- B1: **75.1 tok/s**
- B2: **75.2 tok/s**
- B4: **73.1 tok/s**

The author explicitly describes this as **serialized throughput arbitration, not
simultaneous batched-MTP scaling**.

### Interpretation

Do not transfer the absolute throughput to M1 Max/TB4: the hardware, link, model layout,
and residency are much stronger. The transferable lesson is architectural:

- preserving one profitable speculative lane while queueing/overlapping independent work
  can beat forcing speculation into every concurrent row;
- B2/B4 aggregate can stay close to the best profitable B1 speculative rate without
  needing linear speculative scaling;
- concurrency policy is itself an inference optimization.

### Qwen3.8-27B distributed signal in the same PR

The Cluster-v2 branch also reports a Qwen3.8-27B full-replica Phase split:

- 9,410-token cold prefill compute average ~991.36 tok/s;
- decode ~29.59 tok/s;
- lossless cache handoff 7.34 GB/s;
- exact-prefix wall reduction 12.31 s -> 1.40 s;
- B4 queued throughput ~1.29x sequential stage time.

Single-node Lightning MTP can bind a donor head, but Qwen TP2 MTP physically stalled at
the first `return_hidden` / rollback graph and the family enable was reverted. This is a
useful reminder that distributed target execution and distributed speculative-state
lifecycle are separate qualification problems.

## UPDATE — DS4 #861 distributed batched serving scaffold

Source: https://github.com/antirez/ds4/pull/861

The existing two-node Strix Halo topology evidence was already known. The current PR text
adds a distributed-batched-serving L0 step:

- `--batched-session N` coordinator mode now shares one worker registry instead of each
  slot trying to bind its own coordinator port;
- the wire already multiplexes `(session_id, request_id)` and keeps per-session KV planes;
- **decode remains serialized** and coalescing/mixed-prefill are disabled until row-batched
  spans are implemented.

No new throughput receipt accompanies this update. It reinforces the same maturity signal
as oMLX: distributed multi-session correctness comes first; actual batched transport and
compute overlap are a separate throughput milestone.

## RECOVERED M1 MAX 27B BATCHING BASELINES

Existing oMLX benchmark records provide useful, but configuration-sensitive, evidence that
M1 Max itself can benefit materially from multi-row target batching on Qwen3.8-27B.
Examples found in this pass include B1/B2/B4 aggregate rows such as:

- 18.9 / 22.0 / **44.9 tok/s** on one 4-bit M1 Max 64 GB run;
- 18.1 / **31.0 / 63.8 tok/s** on one oQ4e-mtp M1 Max run;
- 16.2 / 26.4 / **45.1 tok/s** on another oQ4e-mtp M1 Max 64 GB run;
- 15.5 / 31.9 / **61.7 tok/s** on one AX-6bit-MTP M1 Max run.

Another M1 Max 64 GB record showed only ~19.0 / 22.3 / 23.7, demonstrating substantial
runtime/model/config sensitivity.

### Interpretation

The durable conclusion is not "M1 Max B4 = 60 tok/s." It is:

- ordinary multi-row execution can expose substantial aggregate headroom on M1 Max;
- the benefit can vary from modest to several-fold;
- Flash-Next's QSA/recurrent state makes it a distinct batching problem;
- therefore our B2/B4 optimism should remain, but it should be attached to **measured plain
  batching first**, not assumed speculative batching.

## Qwen3.8-27B exact frontier

Fresh check remains unchanged:

- Layr best score `3.7291100105909`;
- #1481 remains newest visible submission;
- no newer promoted exact result.

No external exact result changes P69B13 selection.

## Confidence update

These are engineering planning probabilities, not statistical confidence intervals.

### Short/medium-context mature dual-M1 Flash-Next B1

**Unchanged from the prior pass:**

| B1 target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

Nothing in this pass directly changes dependent-chain B1 economics.

### Long-context B1 around 128K

**Unchanged:**

| B1 target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate throughput

Trimmed because the evidence now separates three things that had been blended together:
plain batching, speculative batching, and serialized speculative-lane arbitration.

| Aggregate target | Previous | Current |
|---|---:|---:|
| >=50 tok/s | ~90% | **~85%** |
| >=60 tok/s | ~80% | **~70-75%** |
| >=70 tok/s | ~65% | **~50-55%** |
| >=80 tok/s | ~45% | **~30-35%** |
| >=90 tok/s | ~25% | **~15%** |

This is still a favorable agent-server outlook. The adjustment means only that we should
not count on concurrent MTP itself being the multiplier on M1 Max.

## Updated deployment hypothesis

Primary topology remains **PP2**, with TP2 as a falsification/control benchmark.

For multi-agent service, the candidate scheduler order is now:

1. preserve warm resident sessions beyond active concurrency;
2. use plain multi-row target batching whenever it is profitable and correct;
3. maintain one MTP/speculative lane when B1 speculation materially wins;
4. allow independent requests to fill PP idle time around that lane;
5. enable batched MTP only if M1-Max measurements beat plain batching;
6. use context/acceptance economics to disable speculation dynamically.

This is a more conservative concurrency architecture than "MTP everywhere," but likely a
better one for first-generation M1 Max hardware.

## Highest-value missing measurements

1. Exact Flash-Next 2x M1 Max/TB4 target-only B1 TG.
2. Exact Flash-Next 2x M1 Max/TB4 MTP B1 TG and committed tokens/cycle.
3. Flash-Next single-M1 B2/B4 plain batching after #3368/#3369.
4. M1 Max plain batching versus singleton-MTP-lane versus batched-depth-1 MTP.
5. PP2 B2/B4 aggregate with stage-idle % and actual TB4 bytes per request/cycle.

Those measurements will move the aggregate confidence ladder far more than another
cross-hardware kernel microbenchmark.
