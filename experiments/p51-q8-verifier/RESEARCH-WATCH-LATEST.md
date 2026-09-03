# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-1030.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-03 10:30 ET

This pass recovers an important older M1-generation Flash-Next **Prompt Lookup Decoding** receipt and adds fresh multimodal cache-correctness evidence. It does **not** change the certified verifier state or generic dual-M1 throughput forecast bands.

Material deltas:

- **RECOVERED OLDER EVIDENCE + STATUS UPDATE — oMLX #3203 Prompt Lookup Decoding:** on M1 Ultra 128 GB / Flash-Next oQ4e MTP / resident PLE, repeated agent workloads measured **36.5 -> 56.5 tok/s (1.55x)** while novel prose was unaffected. Independent M5 Max 128 GB evidence with SSD-PLE gather/prefetch measured a copy-heavy Python rewrite **48.3 -> 108.4 tok/s (2.24x)** at default draft_max=16, while novel prose was inside noise. This evidence dates to August and is not new today; the fresh Sep-3 commit only renames the feature from n-gram lookup drafting to **Prompt Lookup Decoding** to distinguish it from Flash-Next's unrelated PLE n-gram table. Hermes should treat prompt lookup as a first-class conditional optimization for copy/rewrite-heavy agent turns, with memory-pressure width limits and fenced cross-request history.
- **NEW — DS4 #962 live multimodal replay correctness:** same-image live-KV checkpoints now keep visible and raw checkpoint boundaries aligned when pending thinking tags are removed, and refuse to checkpoint unfinished reasoning as a completed visible turn. M5 Max / Metal server regressions pass. State correctness only; no raw-speed claim.
- **UPDATE — DS4 #961 hot-path overhead recheck:** fresh M3 Ultra paired checks show conditioning-complete vision persistence within <0.5% of main at 2K and 16K frontiers, with byte-identical frontier logits. This removes an obvious concern that complete multimodal cache provenance materially taxes normal prefill/decode.
- **NEW COMMUNITY LEAD — stochastic MTP + lookup tuning:** fresh Strix Halo/llama.cpp 50-trial tuning at temp=1.0 reports a best point of 29.8 tok/s and 65.84% acceptance with MTP max depth 5 plus lookup match/max settings 48/18. No clean baseline and non-Apple hardware, so not a forecast input; it reinforces exact-runtime/sampling/workload qualification and does not resolve oMLX #3370.
- **NO CHANGE — exact dual-M1:** llama.cpp #27993 and DS4 #922 still have no sustained 2x M1 Max Flash-Next/0731 TG receipt. DS4 #957 still has no post-fix Apple mapping throughput result.
- **NO CHANGE — Layr / mlx-dspark:** no new Layr submission; mlx-dspark still reports last code push at 2026-09-01 10:54 UTC.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged** because there is still no exact dual-M1 Flash-Next TG calibration.

Maintain a separate **copy-heavy agent upside** track: Prompt Lookup has physically delivered 1.55x on M1 Ultra and 2.24x on an independent M5 Max setup, but those single-node workload-specific multipliers must not be applied directly to PP2 forecasts.

Hermes policy remains 3-4 logical agents, normally 2-3 active compute slots, session-aware hot ownership, transactional cancellation frontier snapshots, bounded rewind checkpoints, durable SSD cold state, conditioning-complete multimodal cache identity, asymmetric resident PP2, and speculation/Prompt Lookup enabled only after exact workload/hardware/runtime qualification.

The mature target remains roughly **400+ tok/s cold prefill plus excellent prompt/prefix caching** as a design target rather than a dual-M1 measurement.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
