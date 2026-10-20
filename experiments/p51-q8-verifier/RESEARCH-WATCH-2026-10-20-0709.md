# Project 51 / Relay — 2026-10-20 07:09 EDT research watch

Previous strict cutoff: 2026-10-20 05:00:48 UTC, committed as bc68f37c784399af0edf027a0ece422902ee7633.
New strict cutoff: 2026-10-20 11:09:11 UTC (the user's 07:09:11 EDT request).
Protocol: canonical STATE/TARGETS/LATEST/previous dated watch read before search. Sources checked: GitHub PR bodies and releases, Hugging Face primary model cards, public quant discovery. NEW = created after previous cutoff; UPDATE = material in-window change to known PR; RECOVERED OLDER = older release newly examined. OPEN != merged, configured context != completed long agent, model card quant quality != source-grade agent task quality, another GPU != user GPU.

## QFN quant — NEW integration but older trained model

- NEW Strata OPEN DRAFT #3384 created 2026-10-20 07:10:48Z: https://github.com/Niko1221/Strata/pull/3384 integrates Mirai QNS 1.5–5bpw-per-expert, approximately 2.4bpw average trellis Qwen3.8-Flash-Next-S/S-small model into Strata 0.2.x CUDA/AVX2. Original model and 0.1.43 patch predate cutoff (Oct15 fix): https://huggingface.co/trymirai/Qwen3.8-Flash-Next-S-strata-experimental . Mirai's self-reported teacher-forced ROMA KL 0.040 and top1 93.4% vs GSQ-RCO IQ2_XS KL0.303, same 37,620 token positions outside Strata. Not comparison to Swift1.5 IQ3_S on agent benchmarks. 36.3GB expert weights vs IQ2_XS35.5GB; optional ~2.1GB 5-bit dense GGUF saves ~1.45GiB VRAM vs Q8 dense. Full GGUF42.3GB plus 28.8/51.2GB SSD PLE; 64GB host minimum. 1/2 RTX3090 tests up to32K shallow tool/recall; six QA tests, MTP acceptance 117/170, single-run per-prompt speed ranges only. No 5070Ti16, 128K, 262K, AA quality, M1 Metal or AMD HIP evidence. Experimental low-bit candidate, no promotion.
- No timestamp-verified NEW full primary QFN/27B quant released since 05:00:48Z. Q4 DFlash2 in earlier watch is a draft model quant, not the QFN backbone. QUASAR, QAD and Swift/GSQ-RCO previously covered.

## Metal trellis source milestone

- UPDATE older OPEN Strata #3299 (created before prior cutoff; updated10:18Z): https://github.com/Niko1221/Strata/pull/3299 . Gyro-M TQ2_T/Hadamard QFN served on Metal, 81/81 kernel parity. Separates embedded ~54GB PLE from GPU wrapping. On M5Max128GB IQ3_S vs Gyro-M: prose84 vs73–79TG, edit121 vs110TG, three-part coding agent7.4 vs8.1 minutes with all tests passed. Two Gyro-M engines fit on ONE 128GB Mac; aggregate work1.28x with per-engine slowdown. No M1Max64 testing, no 128K contexts, no two-Mac TB4 pipeline, Gyro-S full model not run. #3231 Metal checkpoint base OPEN. Mechanism progress, no Apple7 speed credit.

## SHIPPED Strata release

- NEW released Strata v0.2.1 at 2026-10-20 08:19:38Z, engine0.1.46: https://github.com/Niko1221/Strata/releases/tag/v0.2.1 . Linux CUDA13 package & Mac notarized DMG. Headless NVIDIA default VRAM reserve reduced1536 to512MiB (700MiB vision); could yield extra expert residency on native headless5070Ti if default was applied, but owner measurements absent. User custom flags now honored, MTP size (~1GB) counted in model fit. New standard-v1 34-request benchmark packaged, protocol still draft and no first release-hardware result. Mac GPU vision included; M4 GPU picture0.45sec vs CPU50.7sec in small example, uses~1.2GB; M1 result untested. RX6000/gfx1030 STILL NOT in release packages; earlier #3329 source route not merged. FP4-Local setup dependency fix shipped, no host-fit performance result for QAD.
- NEW OPEN #3416 https://github.com/Niko1221/Strata/pull/3416 fixes probability bias in opt-in gated MTP, rebased older #2591 CLOSED UNMERGED. Example p=(.5,.5), q=(.875,.125), prior output=(.5625,.4375), repaired=(.5,.5); repaired HIP numerical target-logit 12/12 matching singleton vs original1/12, TV0.03613 at position12; default sampler unaffected. CUDA/HIP/SYCL/Metal build tests, full model sampling path only HIP; no owner model quality or speed. Keep quant quality scoring on a valid sampler.
- NEW issue #3364 https://github.com/Niko1221/Strata/issues/3364 Windows HIP two R9700 at 1M configured context (trained262K) finds expert-cache auto consumes VRAM before batch4 state/MTP allocations, engine exits1. Extreme config, not owner proof. Multi-agent admission must reserve batch slots/MTP/vision first.

## Mac cluster, GGUF and SSD work

- NEW MERGED oMLX #4678 09:23:49Z: https://github.com/jundot/omlx/pull/4678 adds GLM5.3 and DeepSeekV4.1 pipeline/tensor-parallel text cluster capability and trusted Thunderbolt staging. Validation two ranks on ONE M3Ultra512GB, basic answer+3 stream tasks (GLM TP2 prompt7020/18.3s, DS4 TP2 7012/21.3s); second Mac only SSH/100MB copy verified, no real two-Mac inference speed. No native QFN full state or CUDA→Metal committed frontier handoff, not owner M1Max64 solution.
- NEW OPEN oMLX #4679 https://github.com/jundot/omlx/pull/4679 provides GGUF selection and Splash external serving Qwen3.8-27B GGUF and NVFP4/FP8; basic tool/image/chat checks M3Ultra512GB with 11.9GB IQ3_XXS GGUF and23.4GB NVFP4, no owner M1Max64 128K TG/agent quality. Experimental convenience, not speed result.
- NEW MERGED oMLX #4674 09:11Z: https://github.com/jundot/omlx/pull/4674 precise SSD Engram row fetches for DS4.1 on M5Max, stock8K +5.9% PP/TTFT -5.5%, 3 alternating pairs, byte-identical rows, not M1/QFN direct receipt.
- NEW OPEN DRAFT TensorFold #1113 https://github.com/ashhart/TensorFold/pull/1113 : EXL3 QFN CUDA dual RTX5060Ti16 proposed TP2/paged BF16 KV/async expert offload/graphs. Current head not fully revalidated; claimed earlier development hardware gate but no 200K x2 or graph performance proof, no single5070Ti owner fit, many lint blockers. Do not call new quant or production runtime.
- NEW Strata OPEN #3381/#3382 https://github.com/Niko1221/Strata/pull/3381 https://github.com/Niko1221/Strata/pull/3382 on 2x RX6900XT gfx1030: opt-in RDNA2 INT8 QSA attention prompt -3.49% at31/119K; CPU sharing during batched but idle decode phase short continuation/read <2048 -21 to -31%, >2K almost no improvement. Same gfx architecture as RX6800, but owner single RX6800 gfx1030/32GB different and untested.

## Decisions unchanged

Owner RTX5070Ti16 +64GB DDR5 native Linux source-grade default Swift1.5 GSQ-RCO IQ3_S, pending quality gates. Mirai-S trellis is a new low-bit comparison arm, not a speed or AA victory; frozen quantitative goals unchanged. Check Strata 0.2.1 native headless default/reserve vs pinned baseline on exactly same source task32/64/128K, cache resident experts, 3–5 agent slot capacity and restart/persistence. M1Max64x2 needs a real M1 Gyro/Metal benchmark, dual-Mac physical TB4 benchmark and full CUDA-to-Metal QSA/GDN/PLE/MTP state import. RX6800 needs source HIP run on its actual card, not transferred dualRX6900 results.

No numerical planning target or probabilities changed: dual-M1 QFN 40TG at128K, 400 cold PP remain ambitious projections. No production artifact, frozen verifier, hardware purchase or code changed.

Next strict cutoff begins strictly AFTER 2026-10-20 11:09:11 UTC.
