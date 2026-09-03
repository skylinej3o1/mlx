# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-0340.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current newest delta — 2026-09-03 03:40 ET

This pass materially sharpens Hermes state ownership, rewind behavior, and speculative safety. It does **not** change the certified verifier state or dual-M1 throughput forecast bands.

Material deltas:

- **NEW — llama.cpp #28302 hybrid-agent rewind checkpoint retention:** draft PR physically tested on M1 Pro 32 GB. Editing an earlier turn after advancing the conversation changes from **704 tokens / 3355 ms** of prompt work on master to **26 tokens / 264 ms** with the fix; a master-again control reproduces 704 / 3323 ms. An M5 hybrid coding-agent replay drops warm reprocessed tokens 2436 -> 1776 and wall time 18.25 -> 17.12 s (-6.2%). Rewind checkpoints need a byte budget as well as a count bound.
- **UPDATE — llama.cpp #28243 Apple MTP caution:** M5 Pro 64 GB / Flash-Next IQ3_XXS measures 26.8 tok/s no-spec, 26.3 at draft depth 2 with identical greedy output, and 22.1 (-18%) at depth 5 with a different greedy token stream. Do not transfer this to oMLX's separate exact MTP implementation, but require both identity and wall-clock qualification before enabling speculative depth.
- **RECOVERED OLDER EVIDENCE — DS4 #765 session-aware subagent slot routing:** old August work directly relevant to Hermes. On M3 Ultra / Metal, preserving the main session while placing a subagent into an empty second slot changes the main continuation from 2,881-token reprefill / 5.06 s TTFB to a 12-token suffix / 0.27 s. Use exact session-aware reuse plus staleness-aware eviction; do not let short subagents trash expensive long main-agent state.
- **RECOVERED + UPDATE — oMLX #2628/#2630 SSD-cache hardening:** future recurrent/boundary snapshots are now explicitly priced in long-prefill admission, and SSD persistence teardown is bounded so a saturated cache writer cannot let one memory-pressure eviction kill the entire multi-model process. Relevant to cold-agent/unload reliability, not raw TG.
- **UPDATE — reasoning-effort discovery:** oMLX #2746/#3395 can advertise model-specific effort vocabularies (Qwen3.8: xhigh/medium/low; DeepSeek V4: low/high/max), but `none/off` semantics remain under discussion. Useful for future Hermes workload routing; do not assume a stable cross-provider off token yet.
- **NO CHANGE — exact dual-M1 receipts:** llama.cpp #27993 and DS4 #922 still have no new sustained 2x M1 Max Flash-Next/0731 TG result. DS4 #957 has no post-fix throughput receipt. No new Layr submission; mlx-dspark still has no code push after 2026-09-01 10:54 UTC.

## Forecast consequence

B1 short/medium, B1 ~128K, and mature B2-B4 aggregate confidence bands remain **unchanged**. There is still no exact dual-M1 Flash-Next TG calibration.

Hermes policy becomes more explicit: 3-4 logical agents, 2-3 active compute slots, session-aware hot-state ownership, staleness-aware eviction, rewind-capable recurrent checkpoints under a byte budget, durable SSD exact-terminal fallback, and speculative depth enabled only after identity + wall-clock gates on the exact runtime/hardware/quant/workload.

The user's mature-system target of roughly **400+ tok/s cold prefill plus excellent prompt/prefix caching** remains sensible and unproven on dual M1 Max.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
