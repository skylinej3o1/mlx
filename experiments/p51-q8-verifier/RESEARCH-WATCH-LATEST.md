# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-02-MIDNIGHT.md`

3. If reconstructing history or validating whether a source is genuinely new, scan all
   dated `RESEARCH-WATCH-*` files newer than the canonical state's consolidation point.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-02 Midnight ET

This pass focuses on concurrency and distributed serving economics rather than another
isolated B1 kernel result.

Material deltas:

- **NEW oMLX #3368:** fixes Qwen4-exp QSA indexer per-row `past_len`; B>1 continuous
  batching could crash because a per-row cache offset was treated as scalar. This is a
  correctness prerequisite for real Flash-Next B2/B4.
- **NEW oMLX #3369:** fixes BatchQSAKVCache join rank/length handling across text/MRoPE
  state and separates indexer length from KV offset.
- **RECOVERED oMLX #3265:** batched depth-1 MTP is not automatically profitable on
  M1-generation silicon. An M1 Ultra B8 run measured 36.03-38.50 tok/s with batched MTP
  versus 57.09 tok/s plain batching because draft-head cost was approximately verifier
  cost.
- **UPDATE/new-to-project oMLX #3118:** physical M3 Ultra + M5 Max / TB5 Cluster-v2
  evidence shows a mature distributed server can preserve speculative throughput by
  serializing one profitable MTP lane and arbitrating concurrent requests around it,
  rather than forcing simultaneous batched MTP.
- **UPDATE DS4 #861:** distributed multi-session serving now shares a worker registry,
  but decode remains serialized until true row-batched spans/coalescing land.
- **RECOVERED M1 Max 27B benchmark baselines:** ordinary target batching can show strong
  B2/B4 aggregate scaling on M1 Max, but the multiplier is highly runtime/configuration
  sensitive.
- Layr exact Qwen3.8-27B frontier remains `3.7291100105909`, #1481 newest visible.

## Forecast consequence

B1 short/medium and long-context confidence bands are unchanged.

Mature B2-B4 aggregate confidence is now:

- >=50 tok/s: ~85%
- >=60 tok/s: ~70-75%
- >=70 tok/s: ~50-55%
- >=80 tok/s: ~30-35%
- >=90 tok/s: ~15%

The updated serving hypothesis is: prove plain multi-row batching first; under concurrency,
measure plain batching versus a singleton profitable MTP lane versus batched depth-1 MTP,
and dynamically disable speculation when its economics turn negative.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen
and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next
using existing profiling data only**.
