# Project 51 strict research watch — November 11 2026 22:49 EST

**Previous cutoff:** 2026-11-11T18:25:32Z; **new strict cutoff:** 2026-11-12T03:49:45Z. FRESH sources created inside window, UPDATED OLD sources whose substantive updates happened inside window; previous news not relabeled new. GitHub primary issues/PRs/release scan Basalt, Strata, TensorFold, Kapitsa, Splash, Paperniuk, oMLX, Huawei MACaQ; official QwenCloud Qwen4 model page and Reddit quant claims. NO local user hardware actions, installs, weights downloads, CI, conversions, tests, or purchases.

## FRESH top priority: Apple7 M1 Max dense27B Neural Engine prefill split

[Kapitsa issue#1194](https://github.com/nace-ai/kapitsa/issues/1194) Nov11 20:31Z **2021 M1 Max32GPU/32GB**, macOS27.2, Kapitsa0.2.31, Qwen3.8-27B 4bit. Cold4K GPU only TTFT30.8–31.8s,129–134 PP vs split26/34 FFN units TTFT17.5–18.4s,225–236 PP (**1.70–1.76×**). True16,285 prompt131.8s/124PP →93.8s/173PP (**1.40×**); decode unchanged. ANE part startup self-check0.77–0.89% difference; **greedy text changed in 2/2 dense27B examples**, NO quality floor logit check, not default (NI_ANE=1 NI_ANE_UNITS=26), Kapitsa bench omits NI_ANE env so results via client-side TTFT. Important old Apple7 concrete improvement, but does not apply to original QFN GSQXXS, M1Max64 untested, no xHigh coding task. Source 32GB Mac qualifies chip architecture not 64GB user exact.

## FRESH new model 35B MoE Ornith 1.5 M1Max

[Kapitsa issue#1198](https://github.com/nace-ai/kapitsa/issues/1198) Nov11 22:39Z 2021 M1Max32GPU/32GB native [Ornith-1.5-35B-A3B-MLX-4bit](https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B-MLX-4bit) pack19.51GB, alloc21.34GB, 32K context, no draft decode101–103 TG short, with Qwen3.6-35B DFlash2 b8 198.3 TG short deterministic code,170.7 grammar,105.6 prose. Draft adds1.23GB and 32K still fits. Different trained Ornith b16 drafter unsupported; GGUF Q4_K_M import converts to 5bit group64 experts and costs +2.4GB, leaving only4605 KV tokens when requesting 32K on 32GB; native MLX preferred. **Greedy outputs diverge** with drafter, same 3/3 per mode, even though docs promise precise. NOT hard agent evidence, 198TG not normal long reasoning speed, not QFN replacement. [Kapitsa #1201](https://github.com/nace-ai/kapitsa/pull/1201) new catalog proposal; status not assumed.

## FRESH dense27B Q5 KQuant + M5 prefill improvements (NOT M1 improvement)

[Kapitsa PR#1210](https://github.com/nace-ai/kapitsa/pull/1210) Nov12 03:08Z proposes opt-in `27b:kquant5` pinned repo [nace-ai/Qwen3.8-27B-MLX-Q5-KQuant](https://huggingface.co/nace-ai/Qwen3.8-27B-MLX-Q5-KQuant), model20.69GB +MTP0.24 + DFlash2 3.85 = **24.77GB download**. Also 9B/35B Q5. No 27B Q5 GPU run yet at cutoff; model format catalog companion change, NOT demonstrated better than ordinary Q5 or MACaQ IQ4XS. 9B Q4 drafter attaches and reported51.6→144.3TG M5Pro, due speculation ON vs OFF, NOT intrinsic KQuant quality or weights. [Kapitsa PR#1199](https://github.com/nace-ai/kapitsa/pull/1199) Nov12 00:14Z M5 Pro **matrix units only** 27B regular5bit 4K prefill−34% time, 100row−67%, near-exact logits and 256 cold greedy tokens same. M1Max has NO M5 matrix units; don't transfer. [Kapitsa #1195](https://github.com/nace-ai/kapitsa/issues/1195) 9B KQuant4 prefill 37% slower than plain4 on M5 before optimized 5bit tile; numerical fidelity alone doesn't guarantee performance.

## FRESH Basalt reliability warning for long agent work

[Basalt issue#325](https://github.com/jesdga95/basalt/issues/325) Nov12 03:35Z OTHER Windows10 RTX5060Ti16GB/96GB RAM, official Basalt0.3.2, QFN Unsloth UD-IQ4_XS 56.2GiB, INT8KV, configured262K, spec12, adapt-swaps160, one slot. Two long coding-agent sessions hung *between requests*, no CPU usage/watchdog/log, last completed near127.5K and78K with 39.3 and34TG. Restart recovered cache. Cause unknown and different source/OS/pack/spec from owner's original GSQIQ3S 5070Ti Linux frozen spec1; don't claim same bug. For future owner run, log request ingress/egress, watchdog and ability to resume, never accept raw TPS as reliability proof. [Basalt#324](https://github.com/jesdga95/basalt/issues/324) new proposal decouple advertised context ceiling from asymmetric pool; no merged owner feature. No new exact 5070Ti original GSQ32K spec1 hard coding completed benchmark.

## FRESH multiagent/Relay state concerns

[oMLX issue#5180](https://github.com/jundot/omlx/issues/5180) Nov11 20:50Z prefill helper Auto chooses too many layers for GLM5.3, assumed 8GiB working reserve but measured16GiB necessary on OTHER M3Ultra512/M5Max128 helper; 25 layers fallback host 517PP,24 layers helper1030PP. Does not establish QFN-specific problem, but generic lesson CUDA5070Ti16 needs measured transient workspace, not naive packed-size fit; failover must be visible. [oMLX#5178](https://github.com/jundot/omlx/pull/5178) fixes double-encoded tool-call args from rank0; tool JSON schema correctness critical. [TensorFold#2958](https://github.com/ashhart/TensorFold/pull/2958) proposed execution witness with prompt/params/tokens model epoch for multiagent audit; implementation not original source Apple7. [Strata#5822](https://github.com/Niko1221/Strata/issues/5822) QFN CUDA QSA batch indexer reject args on engine0.1.58; avoid mixing runtime generations. [Strata#5818](https://github.com/Niko1221/Strata/issues/5818) Unsloth UD-IQ1_M on M2Ultra garbage in Strata but coherent llama.cpp: engine/quant compatibility is a correctness gate, not generic quant inferiority. Other multi-GPU and HIP developments not owner's exact RX6800 nonXT with16GB host.

## UPDATED OLD dense27B speculative alternative: DSpine

[Splash PR#731](https://github.com/incoai/splash/pull/731) older Nov9, updated within window, experimental Tencent Qwen3.8-27B DSpine16 on OTHER M5Pro20GPU. Controlled three-lane 256token cloned B3 M48 GPU +11–12%, but agent12 overall unqualified and short agent category ~6% slower than DFlash2, warm HTTP −33% and 35/48 warm/cold text mismatches across arms; no default change. Do NOT promote DSpine as general better drafter or M1 validated.

## MACaQ Reddit comparison and source status

[Huawei MACaQ repo](https://github.com/huawei-csl/MACaQ), [Nov11 Reddit post](https://www.reddit.com/r/LocalLLaMA/comments/1xto0fa/opensource_method_macaq_beats_unsloth_ggufs/): claimed dense Qwen3.8-27B MACaQ IQ4_XS **14.96GB meanKL0.036784** vs Bartowski IQ4_XS15.48GB meanKL0.104170 in author's test. Earlier Bartowski external evaluation IQ4XS0.0188 used **different measurement**, cannot compare absolute KL or equate MACaQ to Q5/Q6. No new MACaQ GitHub issues/PRs inside window; code/runtime requires custom llama.cpp preprocessing, no independently verified original M1Metal exact tool-coding run, no source GSQ QFN IQ3XXS adaptation. Maintain HIGH research dense27B fidelity, NOT known Q5 equivalence. A matched BF16 reference, same eval corpus and actual coding-agent tasks needed.

## Qwen4 / new model watch

[Official QwenCloud model changelog](https://docs.qwencloud.com/changelog/models) confirms Qwen4-Max-Preview launched Nov11 (PREVIOUS WATCH), 1M context, Token Plan only through Nov25; no newly verified official downloadable Qwen4-27B/Flash weights inside this window. This is unchanged, not new. Other emerging Ornith35B is an alternate model with unknown hard coding quality. Existing Gosset 27B 3.65BPW no independently verified new loader/coding. Original QFN source GSQXXS M1 historical DS4 128K PP278/TG34.2 and259K PP258/TG31.7 unchanged; two M1Max64 independent; quality floor IQ3XXS and stretch IQ3S unchanged. Basalt first-PC frozen pristine original GSQIQ3S pack,32K true one slot,INT8KV,spec1=NO DRAFT, full tool and PLE/source numerical parity HIGH approval. No actual owner hardware activity.

## Priorities

1. Dense27B **M1Max Neural Engine prefill split**: quality gate and true16/32K tool tasks before claiming improvement; attractive same-chip unused ANE.
2. **Original source GSQ QFN** remains first for hard quality; no quant downgrade or silent engine swap. Original XXS full128/259K evidence preserved.
3. **Ornith35B** candidate fast cheap workers, must independently test hard code and deterministic speculation; not promoted as QFN equivalent.
4. **Dense27B KQuant Q5** new radar; no actual M1 GPU proof, compare MACaQ/ordinary Q4/Q5 using matched BF16 and code tasks.
5. **Relay** oMLX merged CUDA helper prior watch; verify per-helper transient VRAM/workspace, fallback, state/logits and full tool completion before owner 5070Ti→M1.
6. **Basalt reliability** add ingress/egress timeout/deadlock detection; frozen first experiment unchanged.
7. Watch official open-weight Qwen4 and MACaQ independent quant quality. No automatic actions.

**NEXT STRICT CUTOFF 2026-11-12T03:49:45Z.**
