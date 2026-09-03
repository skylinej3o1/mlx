# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-02-2320.md`

3. Because the canonical state was last consolidated at 05:30 ET, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-02 23:20 ET

This pass adds independent Apple persistent-cache evidence, a pre-M5 Metal optimization bundle,
a pipeline-shard mapping hazard/fix under review, and calibrated evidence that Flash-Next MTP
can be either strongly positive or net-negative depending hardware/quant/branch. It does
**not** change the certified verifier state or dual-M1 throughput forecast bands.

Material deltas:

- **NEW — llama.cpp #28092 persistent Flash-Next cache:** M5 Max 128 GB / ~90 GB Flash-Next
  restored a ~33K-token hybrid+draft state after full restart in **0.09 s** versus 39.2 s cold;
  disk cost was ~900 MiB for that prompt. Independent confirmation that cold Hermes agents do
  not need full-history replay.
- **NEW — DS4 #954 pre-M5 Metal bundle:** explicitly targets M1-M4 paths; M3 Ultra validation
  reports bit-exact **+5.0–8.6% greedy decode**, ~+4% prefill at 4K-8K and 28.1 -> 24.3 ms
  first-token latency. Portable Apple lead, not direct Flash-Next/M1-Max calibration.
- **NEW — DS4 #957 / #845 PP shard-map hazard:** a two-host Apple pipeline run with `--layers`
  fragmented a shard into ~156 Metal buffers and measured 10.01 -> 0.13 tok/s (~77x). #957
  now coalesces adjacent spans, but has **no post-fix throughput receipt yet**. Add a coalesced
  model-map startup gate to eventual PP2 bring-up.
- **UPDATE — llama.cpp #28243 MTP:** 5090+5060Ti gets 36.4 -> 45.3 tok/s average with 0.767
  acceptance, while 2x A6000 falls to ~0.37 acceptance and never beats a 41-42.5 baseline.
  MTP remains quant/workload/hardware/branch-qualified, never mandatory.
- **RECOVERED/UPDATE — llama.cpp #28136:** direct PLE reads raise realistic GB10 prefill from
  ~300 to ~750-800 tok/s; repeated-token microbench prompts under-touch PLE. Reinforces using
  realistic code/agent prompts and avoiding random mmap faults on the inference thread.
- **NEW cross-model memory caution — oMLX #3394:** M5 Max 64 GB / Qwen3.8-27B newer source
  build rejects a 128K run at 114,688 despite forced bounded hd256 attention; static KV math is
  not enough to determine context admission.
- **UPDATE correctness caution — oMLX #3181:** a community Flash-Next oQ8 conversion still
  produces degenerate constant output even after RMSNorm canonicalization. Qualify checkpoint
  lineage/output before benchmarking; do not assume arbitrary community MLX conversions work.
- **NEW instrumentation — oMLX #3391:** adds timing for previously invisible prefill boundary
  snapshot capture implicated in ~5-6 s hybrid block-crossing premiums. Await physical
  attribution before changing cache policy.
- **UPDATE — DS4 #861:** rebased current distributed branch measures ~250-274 PP and ~14-15.5
  TG on 2x gfx1151/TB5; B2 partial batching +3-14%. Decode kernels measure near DRAM limits.
- **NO CHANGE — exact dual-M1 receipts:** llama.cpp #27993 and DS4 #922 still have no new
  sustained dual-M1 Flash-Next/0731 TG result. No new Layr submission; mlx-dspark still has no
  code push after 2026-09-01 10:54 UTC.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged**.
There is still no exact dual-M1 Flash-Next TG calibration.

Hermes lifecycle confidence improves again: independent runtimes now physically demonstrate
persistent hybrid state across restart/unload. For PP2, explicitly reject fragmented per-tensor
Metal shard mappings before measuring performance. The mature target remains 3-4 logical
agents, 2-3 active compute slots, exact hot/cold state, asymmetric resident PP, and roughly
400+ tok/s cold prefill as a design target rather than a measurement.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and
`CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using
existing profiling data only**.
