# Project 51 discovery scratchpad — Nov19 12:47 EST

**Cutoff 2026-11-19T17:47:41Z.** [Full watch](./RESEARCH-WATCH-2026-11-19-1247.md). F=owner hardware fit, N=novelty, E=evidence, A=action, I=independence 0–3, weighted 3F+2N+3E+2A+I max33 heuristic, not probability.

## Active leads (top 12)
1. **Exact GPU provider QFN Basalt / test gate F2N3E2A3I0=24.** [#464](https://github.com/jesdga95/basalt/pull/464) one5070Ti16/host62 original GSQ XXS *tuned drafted*, PP64K4336/TG166.5; owner exact GSQ IQ3S no draft32K still not measured.
2. **Original quant 5080 source / Swift F2N3E2A2I0=22.** [#455](https://github.com/jesdga95/basalt/pull/455) 5080 source IQ3S PP64K5220/TG143, Swift5238/TG141; no quality control.
3. **HaikuSwarm tool schema & exact file integrity F2N3E3A3I1=28.** [Strata#6315](https://github.com/Niko1221/Strata/pull/6315) OPEN fixes #6285 tool malformed schema; prior Basalt#429 tool delimiter corruption OPEN and TensorFold#3832 tool ID inversion MERGED. Replays with count, typed arg match and hash.
4. **Under-uptime prefill degradation F2N3E2A3I1=25.** [Strata#6248](https://github.com/Niko1221/Strata/issues/6248) Nov19 owner retracts version bug, tests uptime degradation under RAM expert offload, persistent root unknown; next independent reproduction, watchdog and reset memory curve.
5. **Basalt loader partial fix failing F2N3E3A3I1=28.** [Basalt#430](https://github.com/jesdga95/basalt/issues/430) retest pin10→3.2s but desktop ~174s still stalls; source fixed subproblem, not the user symptom. No automatic main upgrade for owner first baseline.
6. **Apple GDN cache checkpoint fallback F2N3E3A3I0=27.** [oMLX#5424](https://github.com/jundot/omlx/pull/5424) open long-lived SSD under GDN sidecar eviction, fallback system prefix 2 x40-50s failures/1639 requests; native dense M5, not source GGUF M1.
7. **RDNA2 original GSQ model comparison F1N3E3A2I0=21.** [Strata#6314](https://github.com/Niko1221/Strata/pull/6314) one/two6600/6700XT host62 physically4/16K, tables gfx1031/1032 not owner RX6800 gfx1030 /host16. Feasibility still unanswered.
8. **Old M1 Splash tail checkpoint F2N3E2A3I0=24.** Previous Splash784/785 M2Pro32 dense27B old-fork 21 turn TTFT -25%, PRs open not source GSQ XXS M1 physical128/259K.
9. **Qwen4-Flash authenticated manifest F3N1E1A3I0=20.** Qianwen official Chinese feed Nov18 latest, Qwen4-Max Nov16, HF Qwen no Flash; do not guess from community wishes or fake releases.
10. **Owner Basalt first controlled run F3N2E2A3I0=25.** Frozen original ISTA GSQ IQ3S v2 RTX5070Ti16/host64 Intel265F Linux true32K KVint8 slot1 spec1 no draft; no runs absent HIGH.
11. **Strata Metal auto prefill F1N2E2A2I0=17.** [#6293](https://github.com/Niko1221/Strata/pull/6293) M5Pro other model PP488 vs480 within noise, old M1 untested.
12. **Splash LoRA adapter cache fingerprints F1N3E2A2I0=19.** [#786](https://github.com/incoai/splash/pull/786) modern M5 dense27B adaptation ~3% decode cost, not source MoE goal; cache invalidation meaningful later.

## Deprioritized and corrections
- **Retraction** old Basalt#430 "fixed" on main: pin submechanism yes, RAM pressure symptom persists after matched retest.
- **Retraction** Strata#6248 simplistic release 0.1.62 regression: fresh release boots fast; long soak degrades.
- Qwen4-Flash alleged 30B/3.3B sizes and Chinese large Flash guesses unsupported.
- Hardware RX6800 nonXT/host16 not RX6800XT, RX6700XT with host62 or RDNA4 host64.
- New 5070Ti GSQXXS data is **drafted IQ3XXS**, not owner first pristine IQ3S spec1.
- No Paperniuk source Mac benchmark record or full source CUDA-to-Metal Relay.
- New Splash LoRA not equal Flash-Next MoE fine-tuning throughput.
- Basalt#455 Swift and original ~same speed, no published same-task accuracy parity.

## Top three next seed searches
1. Basalt issue#464 same 5070Ti original GSQ XXS vs IQ3S/NO DRAFT comparative, check typed RT, source provenance and actual agent fidelity; separate HIGH before owner local test.
2. Basalt #430 ongoing host-first scheduling, Strata #6248 uptime root; track persistent resident expert cache and failed tool-call response #6315.
3. Qwen official Flash4 manifest and weights; Mac pristine GSQ M1 caching #784/#785 exact hybrid state plus oMLX #5424 sidecar eviction, no new hardware action.

Owner: separate two old M1Max64GSQXXS physical128K PP278/TG34.2 &259K PP258/TG31.7; RTX5070Ti16 host64 GSQIQ3S true32K no draft frozen; RX6800 NONXT16VRAM host16. Docs only.
