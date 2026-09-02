# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-02-1350.md`

3. Because the canonical state was last consolidated at 05:30 ET, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-02 13:50 ET

This pass adds strong physical cache/agent-turn evidence, a new Flash-Next MTP verify-cost
breakdown, a long-context bottleneck correction, and a more conservative multi-agent memory
qualification rule. It does **not** change the certified verifier state or dual-M1 throughput
forecast bands.

Material deltas:

- **RECOVERED + UPDATE — oMLX #3330 ExactResident/prompt-tail keepwarm:** physical M3 Ultra
  Flash-Next integration drops an 18,174-token rewritten agent/tool turn from 4.17 s visible
  TTFT to 0.62 s with exact output parity; structured tool follow-up is ~0.51 s. A fresh
  Qwen3.8-27B MTP-terminal fix reduces MTP-on TTFT from 4.831 s to 0.197 s, essentially equal
  to the 0.208 s MTP-off control.
- **RECOVERED — oMLX #3328:** a ~100K Flash-Next restart restored 98,304 prompt tokens from
  target prefix cache, primed only a 1,689-token exact suffix into MTP, then measured 98.3%
  acceptance, 5.38 tokens/target-cycle and 65.25 tok/s decode with the exact target output.
- **NEW — oMLX #3382:** measured M3 Ultra Flash-Next B1/depth-5 verify cost is ~2.3x a base
  forward, decomposed approximately into +0.5x GDN sequential recurrence, +0.6x MoE expert
  union and +0.2x QSA indexer. Reported prose acceptance (~2.4 tok/cycle) is near break-even;
  tool-call acceptance (~3.1) is ~1.35x net. Proposed expert-union/TreeWY gains are estimates.
- **CORRECTION — llama.cpp #28213:** the prior statement that QSA top-k is the demonstrated
  next residual bottleneck was too strong. On the follow-up host, shrinking top-k work did not
  move throughput; merged #28040's O(N)->O(log n) KV previous-token lookup did, moving
  19.6 -> 21.6 tok/s at ~60K. Keep indexer optimization as a seam, not a proven dominant one.
- **NEW MEMORY CAUTION — llama.cpp #27941:** dense QSA-mask compute buffering can reserve
  ~9 GB at 128K / 4K ubatch in that runtime. oMLX gathered-QSA is materially more memory
  efficient, but raw K/V arithmetic alone is insufficient for Hermes capacity planning.
  **4 x 128K simultaneously hot on 2x M1 Max is a design target, not a proven comfortable
  resident configuration.**
- **UPDATE — DS4 #861:** four concurrent clients now execute bit-exactly and a fifth queues
  cleanly, but aggregate is still ~13.2 tok/s because only part of the expensive path is row
  batched. The contributor's 1.5-1.8x wider-batching ceiling is an estimate, not a result.
- **UPDATE — DS4 #621:** AProjQ4 remains a strong lossy/capacity track (Metal median decode
  +15.5%, 2.14 GiB smaller), but an order-balanced GB10 series requalifies long-context prefill
  to near parity rather than a multi-percent Q4 win.
- Exact dual-M1 Flash-Next #27993 and dual-M1 0731 #922 still have no new sustained TG.
  Layr remains at best score `3.7291100105909` with #1481 newest; mlx-dspark has no new push.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged**.
There is still no exact M1-Max Flash-Next B2/B4 receipt and no dual-M1 Flash-Next TG.

The Hermes architecture case improves in a different dimension: exact prefix ownership,
suffix-local MTP reconstruction and prompt-tail keepwarm now have strong physical evidence for
low-TTFT long-lived agents. At the same time, real runtime/transient/cache-snapshot memory must
be measured before fixing the default per-agent context ceiling.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and
`CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using
existing profiling data only**.
