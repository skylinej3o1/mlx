# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-02-0530.md`

3. If reconstructing history or validating whether a source is genuinely new, scan all
   dated `RESEARCH-WATCH-*` files newer than the canonical state's consolidation point.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-02 05:30 ET

This pass corrects the midnight continuous-batching interpretation and records two new
Flash-Next serving/performance leads.

Material deltas:

- **CORRECTION — oMLX #3368 was superseded.** Already-merged #3246 had fixed the real
  production qwen4_exp ragged-QSA / `to_batch` / join path. #3368 was closed without merge;
  its proposed tests passed unchanged on current main. Plain B>1 correctness was therefore
  more mature than the midnight note implied.
- **UPDATE — #3369 merged.** Mixed text/MRoPE BatchQSAKVCache joins and indexer-length vs
  KV-offset handling are now hardened on main.
- **UPDATE — #3355 + #3351 merged.** Gathered-QSA long text prefill now survives mRoPE
  rebinds and is priced correctly by memory admission. A 233,472-token cached-prefix +
  5,244-token continuation scenario that was falsely rejected is now explicitly covered.
- **NEW — #3372 SSD-PLE gather:** M5 Max 128 GB at 92K warm prefix measured
  35.42 -> 37.32 tok/s (+5.4%) by removing per-forward host readback and row-at-a-time shard
  faulting. Treat this as a portable SSD-PLE design signal, not an M1 percentage forecast.
- **NEW CAUTION — #3370:** one M3 Ultra Qwen3.8-Flash-Next-oQ8-MTP report shows 100%
  acceptance / ~70.7 tok/s at temp=0 but 0% acceptance / ~21 tok/s at temp=0.3 and 0.7.
  The proposed greedy-only acceptance root cause is not maintainer-confirmed. Future M1
  qualification must test real agent sampling separately from temp=0.
- **KNOWN #3334:** compiled B4 decode reduces host dispatch 77% and pure step time 18% on
  M3 Ultra, but controlled HTTP E2E remains 0.93-1.02x, so no aggregate speed claim yet.
- DS4 #922 still has no sustained 0731 dual-M1 TG; llama.cpp #27993 still has no dual-M1
  Flash-Next throughput/deep-context follow-up; Layr exact 27B remains 3.7291100105909 with
  #1481 newest visible.

## Forecast consequence

B1 short/medium and long-context confidence bands are unchanged.

Mature B2-B4 aggregate confidence also remains unchanged from the midnight trim:

- >=50 tok/s: ~85%
- >=60 tok/s: ~70-75%
- >=70 tok/s: ~50-55%
- >=80 tok/s: ~30-35%
- >=90 tok/s: ~15%

The rationale is now cleaner: **plain continuous batching is more mature than we thought**;
the uncertainty is M1-generation speculative economics and the absence of an actual M1-Max
Flash-Next B2/B4 end-to-end receipt.

Updated serving test policy: benchmark plain batching, singleton-MTP arbitration, and batched
depth-1 MTP separately; test MTP at both temp=0 and the intended agent sampling configuration;
A/B SSD-PLE gather before distributed tuning when PLE is offloaded.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and
`CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using
existing profiling data only**.
