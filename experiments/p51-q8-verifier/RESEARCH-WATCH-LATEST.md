# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-02-1630.md`

3. Because the canonical state was last consolidated at 05:30 ET, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-02 16:30 ET

This pass adds a strong exact-session lifecycle result, a production-track transition for
AProjQ4, and a fresh 64-GB Apple Flash-Next capacity receipt. It does **not** change the
certified verifier state or dual-M1 throughput forecast bands.

Material deltas:

- **UPDATE — oMLX #3330 unload/reload rehydration:** physical M3 Ultra / Flash-Next-oQ4e-MTP
  persisted an exact terminal to SSD before unload; after reload a 5,039-token prompt restored
  5,035 tokens and processed only a 4-token suffix. This strongly supports cold persistent
  Hermes agents without full-history reprefill.
- **NEW production transition — DS4 #952 supersedes #621:** #621 remains the development
  archive; #952 is the focused production-ready AProjQ4 PR. The durable evidence remains
  2.14 GiB smaller, Metal paired median decode ratio 1.155, 32/32 frontiers won through 65K,
  and prefill effectively tied. Future lossy/capacity track only; not exact-Q8 P69 evidence.
- **NEW Apple receipt — M3 Max 64 GB:** a fresh AtomicChat 4.27-bpw / llama.cpp report at 128K
  context gives ~300 tok/s PP, >20 tok/s short-context generation falling to ~12 tok/s at
  128K. The single-node SSD-streaming configuration is memory-saturated enough that the user
  reports other normal workstation use is impractical while loaded. This is a useful negative
  control for our desired workstation mode.
- **FRESH anecdote — oMLX MTP full-context speed:** a new comment in a 128-GB M5 Max 262K
  thread reports PP close to 400 tok/s and ~36 tok/s generation at max context. Configuration
  is insufficiently restated for calibration; track only, do not move forecasts.
- **NEW cross-model memory-control lead — oMLX #3384/#3381:** on GLM-5.3-Flash, reducing
  prefill chunk 2048 -> 1024 cut peak process memory by 13.87 GB and eliminated long-prefill
  livelock for an 8.8% PP penalty. This demonstrates prompt chunk width as a real peak-memory
  knob, but current qwen3.5/qwen4 scheduling floors mean it is not directly transferable to
  the planned Flash-Next path without physical qualification.
- **NO CHANGE — exact dual-M1 receipts:** llama.cpp #27993 and DS4 #922 still provide no new
  sustained dual-M1 Flash-Next/0731 TG result.
- **NO CHANGE — #28243/#3382/#3370/#3320, Layr, mlx-dspark:** no new calibrated MTP result,
  verify-cost follow-up, temp>0 fix, wide-MTP requalification, Layr submission, or mlx-dspark
  code push.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged**.
There is still no exact dual-M1 Flash-Next TG calibration.

The Hermes architecture case improves materially on lifecycle behavior: logical agents can be
allowed to go cold or trigger model unload under memory/workstation pressure while retaining an
exact SSD terminal that can be restored without replaying the full history. This complements
exact-resident hot caching rather than replacing it.

The user's mature-system goal of roughly **400+ tok/s cold prefill plus excellent prompt/prefix
caching** remains sensible; this pass strengthens the caching/lifecycle side but does not prove
400 PP on dual M1 Max.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and
`CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using
existing profiling data only**.
