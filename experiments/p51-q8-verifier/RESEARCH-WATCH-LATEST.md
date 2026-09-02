# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-02-1520.md`

3. Because the canonical state was last consolidated at 05:30 ET, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-02 15:20 ET

This pass adds one fresh AProjQ4 requalification and recovers a useful Flash-Next PLE-only
quantization/capacity track. It does **not** change the certified verifier state or dual-M1
throughput forecast bands.

Material deltas:

- **UPDATE — DS4 #621 current-head Metal reproduction:** M5 Max 128 GB at `6a20b13` again
  reports 3-rep paired median AProjQ4/AProjQ8 decode ratio **1.155**, with Q4 winning 32/32
  frontiers through 65K; prefill remains effectively tied. Strong future lossy/capacity
  evidence, not exact-Q8 P69 evidence.
- **RECOVERED — quantized Flash-Next PLE tables:** `primitive-ai/Qwen3.8-Flash-Next-PLE-quant`
  reduces the 95.4 GB BF16 n-gram/PLE table to 49 GB FP8, 32 GB INT4, or 28.8 GB NVFP4-style
  sidecars served mmap-backed. On the published RTX PRO 6000/vLLM stack, INT4/NVFP4 throughput
  is roughly 5-6% below in-RAM BF16 while measured quality remains in the same run-to-run band;
  INT4 was validated inside a 48 GB container.
- **RECOVERED PLE+MTP signal:** the same project reports real-prompt depth-3 MTP at 142.6 tok/s
  with BF16 PLE in RAM, 129.6 with INT4 mmap, 128.8 with NVFP4 mmap, versus 77.5-82.3 with raw
  BF16 PLE on NVMe. Absolute numbers are not Apple evidence; portable lesson is that PLE-only
  quantization may preserve much more speculative benefit than raw large-table disk streaming.
- **NO CHANGE — llama.cpp #28243:** dedicated Flash-Next MTP remains draft with no hardware or
  acceptance benchmark table.
- **NO CHANGE — exact dual-M1 receipts:** llama.cpp #27993 and DS4 #922 still have no new
  sustained decode/TG result.
- **NO CHANGE — oMLX #3382/#3330/#3359/#3370:** no new result changes verify economics,
  warm-agent caching, SSD expert streaming, or the temp>0 MTP caution.
- **NO CHANGE — DS4 #861, Layr, mlx-dspark:** no newer distributed B4 result; Layr remains at
  score `3.7291100105909` / #1481; mlx-dspark still shows last push 2026-09-01 10:54 UTC.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged**.
There is still no exact dual-M1 Flash-Next TG calibration.

The capacity strategy is sharpened: treat **PLE precision as an independent memory knob** from
target-weight precision and expert residency. For the eventual Hermes system, prefer resident
PP2 target execution, exact/paged prefix state, PLE offload/quantization as the first sparse
capacity lever, and broad expert streaming only when headroom requires it.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and
`CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using
existing profiling data only**.
