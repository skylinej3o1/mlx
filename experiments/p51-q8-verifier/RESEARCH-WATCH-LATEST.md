# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-02-0945.md`

3. Because the canonical state was last consolidated at 05:30 ET, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-02 09:45 ET

This pass adds new Flash-Next capacity/headroom evidence and fresh long-context QSA/MTP leads
without changing the certified verifier state or the dual-M1 throughput forecast bands.

Material deltas:

- **NEW — oMLX #3359 SSD expert streaming:** exact-routing streamed MoE now has a substantial
  Qwen3.8-Flash-Next implementation. An independent M5 Pro 64 GB validation ran Flash-Next
  oQ2-MTP at ~32.7 GB resident and ~25-28 tok/s warm after correctness fixes. The PR's best
  development run reports 32.23/34.09 GiB loaded/peak, 362.3 tok/s PP and 40.36 tok/s TG,
  but its hardware is not named, so those absolutes are not M1 evidence.
- **NEW CAUTION — native-demand route floor:** M5 Pro follow-up measures ~217 us/layer total
  native-demand turnaround versus ~67 us for plain gather. The incremental ~150 us/layer is
  roughly a **7 ms extra 48-layer decode-step floor** even before servicing a true SSD miss.
  Therefore full-resident experts remain preferable on our 2x M1 Max pair when capacity allows.
- **NEW — PLE prefaulting:** the streamed Qwen4-Exp path could swing from 3.6 s to 6-10 s on a
  1023-token prompt because 16,368 random PLE rows faulted synchronously from mmap. Parallel
  prefaulting stabilized seven runs to 3.57-3.89 s. Cold-page testing is now a bring-up gate.
- **UPDATE — llama.cpp #28213:** independent ~60K-context test confirms gathered selected-K/V
  at 15.5 -> 19.6 tok/s (+26%). Once attention is compact, full-context QSA top-k/indexer
  selection becomes the next context-scaling bottleneck.
- **NEW sibling #28244:** guarded selected-cell gather keeps 4K decode unchanged at 103.4 tok/s
  and raises 50K 73.2 -> 78.9 on RTX PRO 6000, but depth output is not bit-identical to master.
- **NEW lead #28243:** dedicated upstream llama.cpp Flash-Next MTP draft claims 1.3-2x and
  shared-module/RAM savings, but currently provides no benchmark/hardware table. Track only;
  do not price it into forecasts yet.
- llama.cpp #27993, DS4 #922 and DS4 #861 have no new dual-M1 throughput updates. oMLX #3370
  still has no maintainer response on the temp>0 acceptance-collapse report. mlx-dspark has
  no new code push in the pass window.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands are **unchanged**.

The design implication is more specific now: SSD streaming strengthens the case that the
primary 64-GB Mac can retain real workstation/Hermes headroom, but it is a capacity mode with
measurable host/I/O tax. For the mature 2x M1 Max system, prefer asymmetric PP with a resident
hot execution path; selectively SSD-back PLE or colder expert capacity only when memory/headroom
requires it.

The ~400 tok/s mature prefill target plus strong prompt/prefix caching remains sensible, but
this pass does not supply a dual-M1 400-PP receipt.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and
`CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using
existing profiling data only**.
