# Project 51 research watch — November 15, 2026, 06:45 EST

Prior cutoff 2026-11-15T03:29:48Z; new cutoff 2026-11-15T11:45:32Z. GitHub issues updated since cutoff; not all were created in this interval. Research-only, no hardware/code/CI/model downloads.

## Relay-adjacent CUDA-to-Metal prefill accelerator: important (UPDATED/NEW)
[oMLX #5283](https://github.com/jundot/omlx/issues/5283) M3 Ultra256 host + DGX Spark GB10 119.6GiB helper over 10GbE, Qwen3.8-Flash-Next-oQ4e-mtp. 64K prefill ~2.4K tok/s with helper vs ~1.0K Mac-only. This is CUDA-assisted layer prefill with state handoff inside oMLX architecture, NOT verified full-state PC RTX5070Ti16→M1Max64 Relay, nor same quant.
[oMLX #5288](https://github.com/jundot/omlx/issues/5288) Auto loads 47 layers ~71GiB but executes31-34; fixed32 layers 64K2518 tok/s vs Auto2459, ~55.1GiB vs71. Fixed47 only~1757-1775. Layer scheduling matters.
[oMLX #5287](https://github.com/jundot/omlx/issues/5287) QSACache.append repeated concatenate causes suspected quadratic KV copying; helper 64K2545,128K2405,320K2114,512K1827 tok/s. Proposed preallocated/paged buffers not benchmarked.
[oMLX #5285](https://github.com/jundot/omlx/issues/5285) helper cached MLX pool grows to29.91GiB during94K and persists, 128K113.6GiB GPU used; local clear_cache workaround 320K peak92.9GiB and returns to48GiB baseline.
[oMLX #5283](https://github.com/jundot/omlx/issues/5283) QSACache position rank 2D/3D crash; local reshape workaround, root cause unknown.
Also [#5284](https://github.com/jundot/omlx/issues/5284) failed helper job poisons session; [#5286](https://github.com/jundot/omlx/issues/5286) host guard can't see helper GPU usage; [#5289](https://github.com/jundot/omlx/issues/5289) documentation asks for chunked prefill interaction.

## Basalt million-context and startup variance (NEW)
[Basalt #374](https://github.com/jesdga95/basalt/issues/374): Windows RTX5090D24 +192GB RAM, QFN Basalt NVFP4-DQ6K/DQ8/UD-Q6KXL; configured YaRN1M, true 1,044,546 token read TTFT213-220s ~4800-4900 PP; needle14-16/16 depending run and pack, recurring particular needle miss, not general proof of quality. Same config 3000 output TG 110/120/143 tok/s across restarts, suspected expert-pool placement unproven. Not user's RTX5070Ti16+64GB.

## Reliability and quality watch (NEW)
[Strata #6019](https://github.com/Niko1221/Strata/issues/6019): QFN native IQ2XS 2/1410 and IQ3XXS 1/262 non-finite-logits events on sm86 eGPU, Q2_0 0/1142 matched config; confounders control vector, prior GPU workloads, link; not generalized pack flaw.
[oMLX #5291](https://github.com/jundot/omlx/issues/5291): M5Max Splash1.6.1 int8 attention activations auto and oMLX no --activations bf16 override; reported multi-tool regressions after upgrade, reverted after downgrade, causality unproven and M5+ only.
[Strata #6013](https://github.com/Niko1221/Strata/issues/6013): Unsloth engram Q8 table manually repack header strata-ple for native UD-Q4KXL, data unchanged; verified HIP gfx1100. Not quality benchmark, not original GSQ.

## Frozen Project51 decisions
Two M1Max64 32GPU; RTX5070Ti16+64GB; RX6800 16+16GB host. Original GSQ IQ3XXS minimum, IQ3S preferred; QFN128K/262K; correctness over speed. Basalt first PC test original GSQ IQ3S true32K INT8KV one slot spec1 NO DRAFT. Relay full CUDA→Metal KV and recurrent-state compatibility still unverified on owner's exact hardware. Paperniuk DS4 DFlash2 vs MTP 128K no new confirmed direct run. Monitor Qwen4 open weights and dense27B but no new verified release in this targeted scan.

NEXT CUTOFF 2026-11-15T11:45:32Z.
