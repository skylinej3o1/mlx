# Project 51 — November 20, 16:56 EST: real M1Max optimization A/B and memory provenance

[Strict research watch](./RESEARCH-WATCH-2026-11-20-1656.md) · timebox **2026-11-20T21:00:28Z to 2026-11-20T21:56:17Z** (source events only).

## A. What changed in just 56 minutes

| Evidence | State | Actual M1Max32/64 measured on QFN GSQ-RCO Q2_0+PLE | Key qualification |
| --- | --- | --- | --- |
| [Strata #6434](https://github.com/Niko1221/Strata/pull/6434), updated21:40Z | Open draft | Resident 2K PP **239.66→255.27/255.60 tok/s** (+6.5–6.7%); 128 output IDs, first-logit hashes, MTP acceptance match | Shared #6440 memory changes in each arm; warm setup, control n1 optimized n2; 2K not source IQ3XXS at128/259K |
| [Strata #6440](https://github.com/Niko1221/Strata/issues/6440), new21:18Z | Open proposal | Process footprint at READY **5.909→2.992GB** when both duplicate host weight groups released, only both flag modes allow full MTP2 2K answer under guard | Two owners: pack arena and NativeDense; PLE key retained; not a full baseline MTP paired hash comparison |
| [Strata #6441](https://github.com/Niko1221/Strata/pull/6441), new21:24Z | Open draft | **Owned QSA scratch at512 rows 1337.55→966.28MB**, 371.27MB saved, 5 paired correct 2K output arms | On #6440 common memory release baseline; 16K time95.99→71.06s changes chunk128→256 simultaneously with flags |
| [Strata #6432](https://github.com/Niko1221/Strata/pull/6432), updated21:37Z | Open draft | Lifetime sharing of QSA partials/expert XS/YE: initial one-run process peak **6841.4→6676.3MB**; newer 3 turns final footprint **184–204MB less** | Whole-run peaks similar in 3 turns; this is not added linearly to other savings |
| [Strata #6443](https://github.com/Niko1221/Strata/pull/6443), new21:54Z | Open | Streaming expert topK min cache host overhead **1.85→1.14ms/window** and **1.79→1.12**, end-to-end TG **21.41→22.12** / **20.12→20.55 tok/s** (same128 IDs) | Different 12GB streaming expert arena, single samples and I/O variation, no original source IQ3 accepted quant |

The contributor's updated #6434 now **completes current-upstream-based full-model checks**, correcting the previous watch's blocked-only status, but only by putting the separately proposed #6440 host releases in every arm. Need not collapse the 16% synthetic kernel improvement into claimed 16% whole-model speed. No real original source IQ3XXS 128K/259K measurement.

## B. Source / algorithm / numerical caution

- **Quant**: GSQ-RCO **Q2_0** tested, quality floor **original IQ3_XXS**, preferred IQ3_S; no acceptance downgrade.
- **Mode**: #6434/#6441/#6440 resident MoE and #6443 streaming, so benchmark speeds are incompatible. QSA scratch allocation (own buffer) vs ready process footprint vs process peak overlap; do not sum 2.917GB + 371MB +165MB into a promised owner RAM saving.
- **Tools/fidelity**: 128 identical generated IDs + 2K first logit hash are good *local* parity but not completed agents, long context, silent truncation, model quality vs BF16 or exact repo mutation, multiple workers, MTP state after cache restore.
- **Other architecture**: [TensorFold #4178](https://github.com/ashhart/TensorFold/pull/4178) maintains native dense27B Metal GDN rollback as recurrent workspace lease, no speed claim and not cross-runtime state. [vLLM #69042](https://github.com/vllm-project/vllm/pull/69042) fresh reproducible logprob drift measure NLL, top1 and KL, originally different Qwen2.5-1.5B RTX5090, useful proposed quality gate not an owner benchmark.
- **Negative other hardware**: [Strata #5678](https://github.com/Niko1221/Strata/issues/5678) new21:24Z second NVFP4 QAD N1X120GB prefill stuck near29.18K + `NV_ERR_NO_MEMORY`, not an M1Mac test or diagnosis for the #644x QSA changes.

## C. Strategic boundary

Two separate M1Max64 systems, historical pristine original GSQXXS physically128K PP278/TG34.2 and259K PP258/TG31.7 unchanged. Frozen initial Basalt PC original **IQ3_S v2** PLE, one RTX5070Ti16+CoreUltra7 265F+host64, physical32K single slot int8 KV spec1 no draft CPU-double: unrun, no code/config modification. RX6800 **NONXT 16VRAM+ONLY16GB host** unsupported inference fit. No correct end-to-end RTX5070Ti CUDA→external M1 Splash Metal QSA/GDN/PLE/MTP Relay proven. Qwen4 Flash firstparty config/weights remain unknown [Chinese changelog](https://platform.qianwenai.com/docs/changelog/models) and [Qwen HF](https://huggingface.co/Qwen). New [Kapitsa v0.2.39](https://github.com/nace-ai/kapitsa/releases/tag/v0.2.39) pertains Tencent Hy4 Flash M5 and catalog, not Alibaba Qwen4 Flash. Research docs only, no HIGH authorization for hardware.
