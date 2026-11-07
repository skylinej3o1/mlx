# QFN expert-wise MFQ — older quant family newly added to Project 51 radar

REDISCOVERED before 2026-11-07T13:52:05Z, NOT newly released Nov7. [Tylogi EW-MFQ model card](https://huggingface.co/Tylogi/Qwen3.8-Flash-Next-EW-MFQ), [TyloQuant code](https://github.com/Tylogi/TyloQuant) latest tagged v0.4.0 October17, latest commit Nov4. Non-GGUF .mfq native C++ Metal/CUDA, sensitivity per expert/projection NINT/NVQ quant. Current old-M1 generation Metal performance NOT verified.

In publisher's OWN single WikiText2 BF16 KL tests: V1M weights~74.529GB, resident43.36GiB, KL.19689 top1 84.72% versus GSQ XXS~75.840GB KL.22134 top1 83.00%; V3XXS weights~81.952GB resident50.33GiB KL.12436 top1 87.62% versus GSQ IQ3S~83.618GB KL.13717 top1 86.90%. Do NOT compare numeric KL directly against Basalt's separate Nov7 Unsloth D3.1 scores, since reference/checkpoint/calibration/evaluation not matched. No independent hard coding, BF16 source oracle or xHigh agent pass.

Publisher only M5Max40GPU128GB 4K prefill V1M2538.5TG101.2, V3XXS PP2527.6TG105.4. Single M1Max64 requires added KV~4.1GB128K/~8.1GB262K, OS/Metal/MTP memory before deciding fit; V1M possible candidate, V3XXS extremely tight. No direct M1 hardware measurement. Compare source original GSQ XXS/S, revised Unsloth D3.1 and MFQ on same heldout BF16 and full coding tools before any quality-floor change. No download/benchmark authorized.
