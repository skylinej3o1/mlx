# Project 51 research watch — November 14, 2026, 18:29 EST

Previous cutoff 2026-11-14T22:11:31Z; new cutoff 2026-11-14T23:29:43Z. Targeted GitHub issue updates. No confirmed new Paperniuk DS4 DFlash2 or M1 Max 128K throughput. This is a quiet watch, not an inference breakthrough.

## MTP memory-headroom failure (NEW)
[Strata #5989](https://github.com/Niko1221/Strata/issues/5989), updated Nov14 23:13Z: AMD Strix Halo Ryzen AI Max+395 125GiB host, Radeon8060S gfx1151. The principal complaint is an unresolved ROCm HSA_STATUS_ERROR_INVALID_DISPATCH_PARAMETERS crash around 10% context fill on Strata0.2.13. Diagnostic log also shows QFN IQ3_S MTP draft head over 106299 tokens needs 213MiB VRAM but only 169MiB free, preventing load. Separate failure mechanism, not M1 or DS4. Relevant as memory-headroom warning for 128K-262K speculative setups; cannot transfer exact allocations.

## Resource scheduler failure transparency (NEW)
[Strata #5987](https://github.com/Niko1221/Strata/issues/5987), updated Nov14 22:29Z: shared Linux server launcher refuses insufficient GPU/RAM reservation but Strata retries three times and gives generic 503 after ~35s. Local patch propagates actual refusal in 3-6s. Useful for orchestrator fault diagnosis, not decode speed. Not merged confirmed.

## Built-in benchmark accounting gap (UPDATED)
[oMLX #5182](https://github.com/jundot/omlx/issues/5182), updated Nov14 22:30Z: throughput/context/accuracy Bench tab calls engine directly and do not increment HTTP-serving usage history or status counters. Preserve raw benchmark artifacts; do not infer no tests ran from dashboard zero.

## No material change
Paperniuk DS4 fork latest seen 9da1288 (Nov12); Splash fork d61103e (Nov12). No new verified same-quant GSQ IQ3_XXS M1Max64 128K DFlash2 vs native MTP comparison in targeted scan. No new Kapitsa/Basalt/Splash issues in this window. Earlier DSpine dense27B request and Flint M4Max agent report unchanged.

## Frozen Project 51 controls
Two M1Max64 32GPU, RTX5070Ti16+64GB, RX6800 16+16GB host. Original GSQ IQ3_XXS minimum, IQ3_S preferred; 128K/262K; quality and schema-valid tools first. First Basalt PC experiment original GSQ IQ3_S 32K INT8KV one slot spec1 NO DRAFT. Relay CUDA→Metal KV and recurrent-state handoff unverified. No code/CI/hardware changes authorized.

NEXT CUTOFF 2026-11-14T23:29:43Z.
