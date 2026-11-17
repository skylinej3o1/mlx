## 2026-11-17 08:50 EST — actionable research leads

[Watch](./RESEARCH-WATCH-2026-11-17-0850.md), strict cutoff **2026-11-17T13:50:06Z**.
1. **FRESH upstream Splash 1.7.0 official GitHub tag/release12:42Z**: inspect old M1 compatibility, port status Paperniuk fork (no changes), difference between lossy INT8 cached states and exact; M5Pro64 27B agent1.23× completion and1.46× TG vs 1.6.2 dev not owner source M1 benchmark. No installs.
2. **Basalt QFN clock-free window selection** removes wall-clock variation in draft shape and adaptive expert-tier toggles, greedy/seeded same session reproducible; arrived parallel slots still non-deterministic. Important later quality tests, not frozen first no-draft.
3. **Basalt 8gram suffix** other5090 dense27B 33K file edits TG518→595 &555→626, greedy13 requests same; possible high benefit for coding sessions, needs real long-context replay/correctness and owner HW HIGH.
4. **oMLX 128K code repeated question** #5357 optional live KV saves~200ms rebuild with 4GB resident per session; #5359 first token emitted before DFlash init, ~80–140ms TTFT saved M5Pro64. Observe combined correctness and long-ctx memory demand.
5. **AMD HIP field report Strata#6147** Navi32 16GB host64 near40TG 25h self-report, unverified full log, **not owner RX6800 nonXT host16**; 59.6GB system memory used.
6. **Strata L2 cache #5500 and gateway #6142** OPEN and old 3-week retrospective data high reuse on AMD48, disk restore ~1.6–2.4s vs cold56–66s145K; fail-closed, byte budget, exact session keys and lease necessary for Molt.
7. **vLLM #61051** merged direct Triton KV CoW copy near memory limit, GB200 83.7→3.03ms and async wave1383→1148ms; not QFN M1/owner PC.
8. **Qwen4 actual open weights** no first-party Flash/27B/35B model card/size; Chinese Qwen Max posts repeat old conference hints, not primary leak.
9. **Owner unchanged:** M1Max64 original GSQXXS physically128K PP278/TG34.2,259K PP258/TG31.7; first Basalt pristine original GSQ IQ3S v2 .basalt real32K int8KV slot1 spec1 OFF; Relay not proven; all hardware actions require HIGH.
## Nov17 2026 06:51 EST strict checkpoint

[Research watch](./RESEARCH-WATCH-2026-11-17-0651.md); cutoff 2026-11-17T11:51:16Z.
- First-party Qwen4-Flash/27B/35B actual configs/weights/sizes **NONE** new, Chinese community still speculates; do not confuse Max2.4T/71B with Flash.
- Actual single5070Ti community source #394/#401 new IQ3XXS weighted100.4TG against NVFP4 78.4, but hardware host96GB, draft, max66661, not owner first Basalt original GSQIQ3S v2 real32K no draft.
- TensorFold#3688 OPEN two M5 Ultra256GiB replicated whole decode + split PP 115.3TG vs earlier paired51.1, 49/49 exact. Evaluate TB4, residency and GGUF quality before any M1 expectations.
- Paperniuk#63 new SSD-spilled KV150–220K + idle hypothesis; M1 m1.1 long soak not verified, #66 ANE still OPEN, DS4 no commits.
- Upstream Splash1.7 #780 OPEN, M5Pro only, QFN2K 1.14–1.28×, 27B GDN cache 152.6→46.9 MiB via lossy INT8, exact opt-in, default auto verify output variability, non-equivalent M1.
- oMLX#5317 oQh dense27B Q3/Q4 BF16 KL lower at same-size, QFN oQ2 min70.8GiB and no Splash/ANE/Helper support. Real coding agent task comparisons missing.
- Strata#6136 old vs new append-tail 6.4× slower at67K even when cold PP faster; mandatory cached follow-up test for agents.
- Basalt#391 masked schema H2D ordering bug patched; HaikuSwarm tool/schema accuracy; vLLM#65186 GDN checkpoint design, still no QSA/PLE MTP full Relay.
- Two M1Max64 old pristine XXS128K/259K TG34.2/31.7 unchanged. RX6800 nonXT host16GB mismatch vs RX6800XT host62 benchmarks.
- Separate HIGH explicit consent needed owner device benchmark/model downloads, docs-only action allowed.

## 2026-11-16 10:58 EST — strict discovery checkpoint

[Watch](./RESEARCH-WATCH-2026-11-16-1058.md) · [detail](./RX6800-OMLX-BASALT-2026-11-16-1058.md), cutoff **2026-11-16T15:58:46Z**.
- **Qwen4 Flash/27B weights**: zero new verified official models/sizes in last130m, monitor source manifests not Chinese echoes; 27B dense from older Intel XPU code, Flash ~125B only hypothesis, 35B-A3B desires not official.
- **RX6800 XT (other host62GB) / HIGH owner adjacency**: Strata#6093 one/dual-card standard GSQ IQ3S bench; CPU_SHARE feature can outrun PCIe expert movement; one nonXT+host16GB *not* validated. Investigate host RAM minimum and stability #5892 before planning any owner run.
- **oMLX deep agent**: #5321 batch join-leave partial copy + #5253 needed for successful real 2×245K M5Pro64 test, #5322 scheduler finite requeue or fail; new exact memory budget and Molt retention tests.
- **quant quality**: #5292 oQe correlation refinements dense27B code-KL−18.6% at oQ4e and QFN oQ4e FLORES−8.9% no tool test, #5317 rotated oQh no QFN checkpoint, no offload support, compare against old same-byte GPTQ/Unsloth UD.
- **Basalt**: version commit0.4.1 no verified release/tag, host planner, prompt-id cached state, streaming #382 open, `dl` metric wrong on parallel #387, #352 prompt split off returns RAM when planned but unavailable on OTHER hardware; do not alter frozen test.
- **cross-chip TP**: TensorFold#3587 XPU 4×B70 QFN Q4@262K physically, not owner M1 or Relay.
- **warnings**: Strata#5751 NVIDIA5070Ti other user power-off and Radeon780M warm-up first replay on Windows; both engine-specific, not owner Basalt. Strata#6085 CPU VBMI earlier SIGILL still hold.
- **Molt**: Splash#779 unified replay/RAM parking design, vLLM#67965 hidden-state connector, Qwen Code host hooks asynchronous; no complete token+tool correct owner experiment.
- **Auth**: docs only; HIGH for downloading models, running benchmarks, changing owner runtime/hardware.

## Nov 16 2026 08:48 EST — discovery checkpoint

[Watch](./RESEARCH-WATCH-2026-11-16-0848.md) · [deep note](./QWEN4-RELAY-M1-QUANT-2026-11-16.md). New strict cutoff **2026-11-16T13:48:42Z**.
1. **Q4-WEIGHTS / priority highest (official-source)**: [Alibaba Nov16](https://www.alibabacloud.com/en/press-room/alibaba-unveils-qwen4-max) promises smaller open Qwen4; Max2.4T/71B API-only; next model-card/tensor index Flash/27B/35B first-party; no sizes/dates yet.
2. **RELAY-HELPER-015 / F3N2E2A3I0 = 21**: [oMLX#5316](https://github.com/jundot/omlx/pull/5316) merged M3Ultra DGXSpark helper prefix+3bit/memory fixes; inspect full QFN QSA/GDN/PLE state and layer-budget RTX5070Ti16; not yet owner proof.
3. **M1-ANE-AUTO / F3N2E2A2I0 = 19**: [Paperniuk#66](https://github.com/paperniuk/splash/pull/66) open, dense27B MLX4 M1Max32 TTFT improvement with 769-row threshold; need high-quality quant and correct tools.
4. **M1-SOAK / F3N1E1A3I1 = 21**: [Paperniuk#63](https://github.com/paperniuk/splash/issues/63) >12h clean on1.6.1-m1.1, earlier24h decline remains open; quantify full day reliability.
5. **DENSE27-GPTQ / F2N1E3A3I2 = 22**: [older Oct26 GPTQ MLX4](https://huggingface.co/mlx-community/Qwen3.8-27B-GPTQ-4bit) matched BF16 KL and independent 78 turn replay, same15GB. Need full completed coding tasks, KV long context, vision and Q5 comparator; REDISCOVERED old, not fresh Nov16.
6. **AGENT-PARK / F2N2E2A2I1 = 21**: [Strata#6034](https://github.com/Niko1221/Strata/pull/6034) parked conversations disk tier, independent corruption accounting failure; optional Molt integration after repair.
7. **DENSE27-DSPINE / F1N2E2A2I0 = 16**: [vLLM#67094](https://github.com/vllm-project/vllm/pull/67094) H100 BF16 C8 acceptance real checkpoint, no owner backend.
8. **CPU-AVX512-QUANT / SAFETY HOLD**: [Strata#6085](https://github.com/Niko1221/Strata/pull/6085) VBMI IQ3 accelerate with SIGILL on AVX2 before main even OFF; block until fixed and independent tested.
9. **AGENT-EXACTNESS**: [oMLX#5312](https://github.com/jundot/omlx/pull/5312) benchmark queue waves overreport, [Splash#776](https://github.com/incoai/splash/pull/776) relaxed token drift optional not for exact agent, [Splash#778](https://github.com/incoai/splash/pull/778) QFN synthetic recurrent-state continuation.
10. **FIRSTPC-FROZEN**: original pristine GSQIQ3S v2 .basalt true32K INT8KV one slot spec1=OFF RTX5070Ti16 host64, CPU double/tool gate; no change.
Deprioritize generic Qwen4 size speculation, M5Pro/M6/Ultra extrapolation to 2021 M1Max, dual5090 and RTX5080 example results, untested low-bit QFN substitutions. Next desk actions: official weights; QSA helper0.1.5 state cost + Paperniuk soak; GPTQ real agent parity and KQuant comparison. HIGH separate approval for device work/weights.

## Nov 15 2026 12:52 EST — ranked discovery checkpoint

[Watch](./RESEARCH-WATCH-2026-11-15-1252.md) and [M1 note](./SPLASH-M1-1611-AND-AGENT-2026-11-15.md). New strict cutoff **2026-11-15T17:52:37Z**. Active verification seeds (rank indicative, F/N/E/A/I all 0–3, heuristic =3F+2N+3E+2A+I):
1. SPLASH-24H F3N2E3A2I1 score27: [1.6.1-m1.1](https://github.com/paperniuk/splash/releases/tag/1.6.1-m1.1) streamed GSQXXS startup fixed but [#63](https://github.com/paperniuk/splash/issues/63) 24h resident speed degradation unresolved. Source causal analysis then HIGH for owner soak.
2. SPLASH-ANEPAIR F3N2E2A2I1 score24: [#64](https://github.com/paperniuk/splash/pull/64) M1Max64 dense27B MLX4 +19% PP at16.7K, -5% at560, different output path. Next model/quant and BF16-quality parity on actual user M1.
3. QWEN4-OFFICIAL high: [Qwen HF](https://huggingface.co/Qwen) and [QwenCloud](https://docs.qwencloud.com/changelog/models), no new Flash/27B/35B official weights or Flash size; verify real manifest.
4. MOLT-CAUSALITY F3N2E2A2I1 score21: [Qwen Code#15959](https://github.com/QwenLM/qwen-code/pull/15959) interrupted original user instruction + paired tool records, excluding cancelled turns.
5. AGENT-SLOT F2N3E2A2I0 score22: [Strata#6044](https://github.com/Niko1221/Strata/pull/6044) other 2080Ti QFN idle VRAM recycle, HIP and DFlash2 veto, no owner source benchmark.
6. DENSE27B-CONCEPT F2N2E1A2I0 score17: [Nov8 author paper](https://concept.country/research/weight-space-programming), claimed +13pp LiveCodeBench, Q4 not evaluated; seek independent reproduction and tool checks before downloading.
7. RELAY-STATE: [oMLX#5163](https://github.com/jundot/omlx/pull/5163) other dualA6000 CUDA helper; single5070Ti QSA/GDN/PLE state not established.
8. AGENT-TOOL-PARITY: [Kapitsa#1277](https://github.com/nace-ai/kapitsa/issues/1277), [llama.cpp#32348](https://github.com/ggml-org/llama.cpp/issues/32348) and [oMLX#5305](https://github.com/jundot/omlx/issues/5305) for no-silent-tool-drop, cache and retry idempotence.
9. 27B DSPINE: [Tencent card](https://huggingface.co/tencent/Qwen3.8-27B-DSpine-b16), [Basalt#360](https://github.com/jesdga95/basalt/issues/360) CLOSED no conversion.
10. QUANT-BUDGET: previously examined [llama.cpp#15550](https://github.com/ggml-org/llama.cpp/pull/15550) imatrix target bpw, no QFN model comparison.

Deprioritized: KimiK3 ~28 seconds per decode step/800GiB SSD; M5Pro/M6 numerical gain predictions for M1; other dual5090/cross quant; Strata RX9070XT report has issue dated Nov15 but text says measured Nov16, provenance inconsistent. Next source actions: official Qwen4 manifest; Splash #63 24h state and GSQ provenance; independent edited 27B Q4 quality. All owner device experiments, weights or repacking require HIGH.

## Nov 15 2026 ~10:49 EST — discovery checkpoint (strict research window)
[Watch](./RESEARCH-WATCH-2026-11-15-1049.md) · [focused mechanism note](./M1-VERIFY-QUANT-QUALITY-2026-11-15.md). New cutoff **2026-11-15T15:49:00Z minute-resolution**; earlier cutoff14:32. Ranked active verification seeds (triage F/N/E/A/I 0–3, score =3F+2N+3E+2A+I; judgment not empirical performance):
1. **Q4OFFICIAL / ~20:** [official Qwen HF](https://huggingface.co/Qwen) and [QwenCloud](https://docs.qwencloud.com/changelog/models). Need real weights/config and Flash body/PLE/MTP/active specs; no Flash/27B weight release verified. Trigger: new Qwen-controlled model card and manifests.
2. **M1VERIFY68 / 20** (F2 N2 E2 A2 I0): [oMLX#5304](https://github.com/jundot/omlx/pull/5304) M1Ultra 6/8-bit qmv row kernels; next replicate quality/throughput on 2021 M1Max64 27B Q5/Q6, end2end MTP/agent, ideally with independent reproduction. OPEN and not QFN source.
3. **QUANTBUDGET / 18** (F1 N2 E2 A2 I1): [llama.cpp#15550](https://github.com/ggml-org/llama.cpp/pull/15550) 2025 old rediscovery, imatrix adaptive bits at fixed bytes. Need original GSQ QFN BF16 calibration, PLE and MTP support; benchmark before any precision replacement; no repack authorized.
4. **27BTOOL / 15** (F2 N1 E1 A1 I1): [Kapitsa#1231](https://github.com/nace-ai/kapitsa/issues/1231) M4Pro Pi looping, unresolved. Seek reproducible effort-setting and tool-envelope traces, full completed-agent-task evaluation.
5. **RELAYSTATE / 19:** [oMLX#5163](https://github.com/jundot/omlx/pull/5163) CUDA→Metal exists on other hardware; full QSA/GDN/PLE state and 5070Ti16VRAM layer placement still unsolved; next source-code shape audit only.
6. **MOLTISOLATION / 13:** [QwenCode#17185](https://github.com/QwenLM/qwen-code/pull/17185) machine-enforced verifier isolation, atomic watch bookkeeping; possible HaikuSwarm design, not model performance.
Deferred: M5 Kapitsa #1276 cache-turn speed is not M1 silicon; TensorFold #3442 is GLM M5 Ultra; Basalt #362 dual5090 UD-IQ1_M not frozen original source. The prior 09:32 Qwen4 rumor audit remains canonical and should NOT be counted fresh.
Next 3 actions: (a) official weight-manifest/Qwen4 Flash and 27B triage; (b) M1 Ultra6/8-bit pathway compatibility with 27B and original QFN quant kernels; (c) quant-target-bpw scope/PLE/MTP and original source fidelity. No model downloads/benchmarks or autonomous tasks without HIGH.

## Nov 15 2026 ~09:32 EST — Qwen4 rumored sizes / Flash forensic research
[Full primary-source rumor assessment](./QWEN4-SIZE-RUMOR-FORENSICS-2026-11-15.md) · [dated watch](./RESEARCH-WATCH-2026-11-15-0932.md). Official Qwen4-Max Preview API Nov11 only; conference **reported** Max/Plus/Flash/27B names with NO Flash parameter count. Existing Qwen3.8 Flash-Next OFFICIAL **125B main/6B active+51B ngram+4B MTP** is architecture preview, not Qwen4-Flash size announcement. Qwen4-35B-A3B secondhand A3B test has no total-size or official model id; genuine third-party Whittle Qwen3.8 35.1B/3B-active Qwen4Exp with 10B memory table (21.3GB Q4) is only feasibility evidence, NOT a Qwen checkpoint. Qwen-code 1M family default, qwen4.5-max and omni-120b-think fixtures do NOT confirm actual sizes; cited Intel XPU primary kernel PR unavailable. Many third-party Qwen4 HF model names are empty placeholders. If Qwen4-Flash resembles current original GSQXXS source model, near57GiB at actual259K on M1Max64 makes even modest parameter growth difficult; 35B class would be much more comfortable if quality meets gate. Two Macs separate64GB. No owner execution, no quality floor changes. Documentation cutoff 2026-11-15T14:32:00Z minute-resolution.

### Ranked verification triggers
1. Official Qwen/Qwen4-Flash(-Next) config+weights: body/PLE/MTP and active expert count
2. Trace source A3B tester: model identifier and actual HF weight manifest, no hearsay
3. Actual Qwen4-27B official config, distinguish dense from model-type inference
4. Official hosted Flash vs open checkpoint availability/licence
5. Same original GSQXXS 128K/259K memory feasibility and coding quality for successor

## Nov 11 2026 22:49 EST — new M1Max ANE 27B, Ornith35B, dense27B Q5 KQuant, Basalt hang, MACaQ

[Full strict watch](./RESEARCH-WATCH-2026-11-11-2249.md). Previous 2026-11-11T18:25:32Z; NEW STRICT CUTOFF **2026-11-12T03:49:45Z**. FRESH [Kapitsa#1194](https://github.com/nace-ai/kapitsa/issues/1194) real 2021 M1Max32GB dense27B4bit NeuralEngine prefill 4K129–134→225–236PP (1.7–1.76x),16K124→173PP(1.4x), decode unchanged; **greedy wording changed 2/2 and logit-quality gate missing**, NOT original QFN source. FRESH [Kapitsa#1198](https://github.com/nace-ai/kapitsa/issues/1198) Ornith1.5-35B-A3B native MLX4 19.51GB on M1Max32, no draft101–103TG, with DFlash2 code198TG, prose106TG, deterministic greedy drift, no hard code evaluation; GGUF import+2.4GB and 32K KV fails on 32GB. FRESH [Kapitsa#1210](https://github.com/nace-ai/kapitsa/pull/1210) dense27B Q5 KQuant new opt-in catalog candidate20.69GB model+3.85GB drafter+0.24GB MTP=24.77GB, **no 27B GPU proof yet**; 9B drafter attach51.6→144.3TG is draft ON/OFF, not KQuant intrinsic. FRESH [Kapitsa#1199](https://github.com/nace-ai/kapitsa/pull/1199) M5 matrix units dense27B 5bit prefill time−34% at4K, **does not apply M1**. FRESH [Basalt#325](https://github.com/jesdga95/basalt/issues/325) OTHER Windows5060Ti96GB UD-IQ4XS spec12, long coding agent 78K/127K sessions hang between requests, no watchdog; not owner's GSQIQ3S frozen32K spec1. FRESH [oMLX#5180](https://github.com/jundot/omlx/issues/5180) CUDA/Metal helper auto layer memory reserve 8GB inadequate for GLM5.3, transient16GB; not exact QFN but Relay admission caution. UPDATED OLD [Splash DSpine#731](https://github.com/incoai/splash/pull/731) M5Pro DSpine16 some clone gain11–12% but agent/mixed warm quality and throughput unqualified, no default. MACaQ Huawei dense27B IQ4XS14.96GB claimed KL0.036784 vs Bartowski0.104170 in one author eval; different Bartowski published0.0188 measurement not comparable; **cannot claim Q5-equivalence**; no new repo update. Qwen4-Max API preview already previous watch, no official open-weight Qwen4-27B/Flash. Two independent M1Max64 originalGSQXXS source historical DS4 true128K PP278/TG34.2,259K PP258/TG31.7 unchanged. First-PC Basalt original GSQIQ3S v2 source SHA TRUE32K INT8KV one slot spec1 NO DRAFT, HIGH approval only. No user hardware actions or CI.

# Active ranked leads — November 11 2026 13:25 EST

## Nov 11 2026 13:25 EST — actual Qwen4-Max API preview, merged CUDA→Metal prefill, Splash1.6.1, old M1 compiler diagnosis

[Strict watch](./RESEARCH-WATCH-2026-11-11-1325.md) · [CUDA-to-Metal Relay research](./RELAY-OMLX-CUDA-METAL-2026-11-11.md) · [Old M1 compatibility](./M1MAX-SPLASH-161-2026-11-11.md) · [Qwen4 & quant radar](./QWEN4-KQUANT-2026-11-11.md). Previous 2026-11-10T19:19:15Z; NEW STRICT CUTOFF **2026-11-11T18:25:32Z**. FRESH official [Qwen4-Max preview](https://www.alibabacloud.com/help/en/model-studio/newly-released-models) Nov11 `qwen4-max-preview` 1M context TokenPlan-only through Nov25, **NO open weights**. FRESH [oMLX#5163](https://github.com/jundot/omlx/pull/5163) MERGED Nov11 06:27Z CUDA NVIDIA Docker prefill helper, OTHER M3Ultra512GB + 2×A600048GB 2.5GbE PP dense27B405→2079 and QFN1388→3574; approximate CUDA/Metal rather than byte parity, lookup tests only, NOT owner 5070Ti→M1 source GSQ Relay. FRESH [Splash1.6.1](https://github.com/incoai/splash/releases/tag/1.6.1) tagged 11:50Z, 28.8GB PLE streamed by default, M5 optimizations **NOT** exact 2021 M1; [Paperniuk M1Max issue#62](https://github.com/paperniuk/splash/issues/62) finds cold Metal JIT blocking engine55–77s, off-loop prototype167 requests no timeouts with dense27B FP16 but full tests outstanding and long20K PP120. FRESH Paperniuk M1 Apple7 [PR#58](https://github.com/paperniuk/splash/pull/58) dense27B MLX4 1-row GPU step−2.77%, [#60](https://github.com/paperniuk/splash/pull/60) −1.61%, source GSQ XXS untested. FRESH [Kapitsa#1188](https://github.com/nace-ai/kapitsa/pull/1188) MERGED15:48Z `flash-next:kquant` QFN MLX4 pack **105.86GB > 64GB**, cannot single-M1; no GPU catalog benchmark, not pristine GSQ. FRESH [Splash#737](https://github.com/incoai/splash/pull/737) compile-validated multi-turn coding runner 25/48 vs29/48 passed, 4.5% speed diff within 6.3% noise; [#738](https://github.com/incoai/splash/pull/738) branch tokenizer reuse micro14.74→0.38ms, combined stack end2end not isolated; [#741](https://github.com/incoai/splash/pull/741) foreground first-burst TTFT regresses395→536ms, DON'T deploy. FRESH [oMLX#5161](https://github.com/jundot/omlx/issues/5161) Qwen3.6 tool choice expected24/40→10/40 in 0.7.3 despite faster decode, cause unknown, underscores agent tooling. FRESH [Basalt#317](https://github.com/jesdga95/basalt/pull/317) OTHER RTX5060Ti16 +126GiB RAM NVFP4 short preset91.6 TG, NOT owner 5070Ti64 originalGSQ IQ3S first spec1. Kapitsa0.2.34 and0.2.35-rc1 released, still no source Apple7 GGUF IQ3XXS validated. Original baseline two M1Max32GPU64 EACH, sourceGSQXXS DS4 128K PP278/TG34.2 and259K PP258/TG31.7 historical; dualIQ3S /3–5 xHigh correct agents UNMEASURED. Owner RTX5070Ti16/CoreUltra7/64GB original .basalt GSQIQ3S TRUE32K INT8KV spec1=NO DRAFT CPU-double/full tool gates HIGH. RX6800 nonXT host16GB. Gosset private packed13.8GB independent loader/code still absent. No owner hardware/model/CI actions.

|Rank|Lead|Proof missing before promotion|
|---|---|---|
|1|Merged oMLX CUDA Prefill Accelerator|RTX5070Ti16 single + old M1Max64, pristine GSQXXS source compatibility, QSA/GDN/PLE logit and completed coding tools|
|2|Paperniuk off-loop Metal compiler fix|PR and full check, source original QFN IQ3XXS true128/259K old M1 no hang|
|3|Splash1.6.1 PLE streaming|Actual old M1 Apple7 source GSQXXS full state and SSD latency, tool/agent correctness|
|4|Dense27B MLX KQuant existing20GB|Same owner M1 Q4/Q5 coding-agent tasks and full wall, proper drafter|
|5|Qwen4-Max Preview remote eval|Only user authorized Token Plan, remote privacy/expense, no local weights|
|6|QFN MLX KQuant105.86GB|Not owner M1 64GB resident; quality/source A/B only on other hardware|
|7|Real multi-turn coding validators and session tool fidelity|All validators pass, tool names & booleans, agent cache exact state, no overclaim from synthetic TPS|

## Previously ranked leads and historical research

# Active research leads November 10 14:19 EST

## Nov 10 2026 14:19 EST — M1–M4 FlashNext kernels, oMLX DFlash2, GSQ quant A/B, KQuant catalog and Relay mixers

[Strict watch](./RESEARCH-WATCH-2026-11-10-1419.md) · [Apple7 Metal focus](./QFN-APPLE7-METAL-2026-11-10.md) · [GSQ/KQuant/Relay detailed](./GSQ-KQUANT-RELAY-2026-11-10.md). Prior 2026-11-10T14:55:03Z; NEW STRICT CUTOFF **2026-11-10T19:19:15Z**. FRESH [TensorFold#2784](https://github.com/ashhart/TensorFold/pull/2784) QFN MLX4 group32 M3Ultra grouped expert decode window≥5 copy256.6→276.3TG +7.7%, code/prose flat, hashed exact; applies in theory M1–M4 but **NO M1 SOURCE GSQ experiment**. FRESH [TensorFold#2760](https://github.com/ashhart/TensorFold/pull/2760) scale index16bit M3Ultra code192.6→197 (+2.3%), but +7.3GiB RAM and+4s load before original arrays freed; no source GGUF. FRESH [oMLX#5158](https://github.com/jundot/omlx/pull/5158) adds QFN paired DFlash2 and PLE rollback, M4Max screenshot not controlled; [oMLX#5160](https://github.com/jundot/omlx/pull/5160) better short request chunk fairness on M5Pro, not owner. FRESH [Strata#5728](https://github.com/Niko1221/Strata/pull/5728) and [#5732](https://github.com/Niko1221/Strata/pull/5732) SAME RTX508016/127GB host source ISTA GSQ IQ3S short78.7/4K72.6/16K70.8TG vs XXS89.6/79.9/79.1TG; PPXXS slower and wide/noisy, configured262K not physically tested, not original .basalt spec1. FRESH [Kapitsa#1153](https://github.com/nace-ai/kapitsa/pull/1153) MERGED17:59Z opt-in dense27B 4bit KQuant with KL0.0349 vs0.0544, sampled TG72.5 vs80.0 slower, greedy91 vs82.8 faster on M5Pro, DFlash2 mismatched post-catalog. FRESH [TensorFold#2791](https://github.com/ashhart/TensorFold/issues/2791) stripped reasoning on client 34K cache resume collapses34.3K→7.4K TTFT0.2→84–86s, model dense27B M3Ultra; agent serialized history correctness. FRESH [vLLM#66870](https://github.com/vllm-project/vllm/pull/66870) QFN GDN/QSA whole mixer replication inter-node RTX PRO6000 25GbE TP2 conc32 +33% throughput, TP4+49% but QSA rank ordering not deterministic and no cross-rank parity; NOT CUDA5070Ti→M1 Relay. FRESH [TensorFold#2761](https://github.com/ashhart/TensorFold/issues/2761) dense27B M5Max128 swapping 262K startup reserves67.3GB and panic, memory admission critical. NEGATIVE no official Qwen4 true downloadable checkpoint, original Gosset gated decode unverified, no M1 old original GSQ new actual owner device. Owner two M1Max32GPU64 sourceGSQXXS minimum, DS4 physically128K PP278/TG34.2 &259K PP258/TG31.7 unchanged, dualGSQIQ3S targets and3–5 correct xHigh remain UNMEASURED. Owner PC pristine GSQ IQ3S Basalt spec1 INT8KV actual32K full tool parity HIGH only; secondary RX6800 nonXT host16GB. No hardware actions.

|Rank|Seed|Next evidence gate|
|---|---|---|
|1|M1–M4 TensorFold #2784 grouped decode|Apple7 source original GSQ XXS port and true128/259K hard tasks|
|2|KQuant dense27B now catalog|same DFlash2, M1 Q4/Q5 versus KQuant coding success +wall|
|3|QFN original GSQ XXS vs S controlled Strata|PC Basalt first original IQ3S spec1 full tools, don't conflate engine|
|4|Multiagent lost reasoning cache #2791|End last user prompt state and sample serializations with tool calls|
|5|vLLM QFN mixer replication |Cross-rank canonical order and actual QSA/GDN numeric parity, not old Relay|
|6|Qwen4 official / Gosset runtime|True official weight manifest and independently loadable model|

## Previously ranked leads and earlier scans

# Active ranked leads — Nov10 09:55 EST

## Nov 10 2026 09:55 EST — new NVFP4 KV, KQuant quality, QFN indexed Metal, agent KV prefix sharing

[Strict watch](./RESEARCH-WATCH-2026-11-10-0955.md) · [Basalt fidelity detail](./BASALT-NVFP4-KV-2026-11-10.md) · [Metal quant/cache detail](./METAL-KQUANT-KV-SHARE-2026-11-10.md). Previous 2026-11-10T11:47:57Z; new strict cutoff **2026-11-10T14:55:03Z**. FRESH [Basalt#314](https://github.com/jesdga95/basalt/pull/314) OPEN other 2×RTX5080 NVFP4 KV QSA saves262K elastic memory3.30→1.98GiB but vs INT8 PP64K8051→6389 and conv TG205→174, BF16-KLD 0.0667→0.0844, top1 91.71→90.77%, do NOT change frozen source GSQ IQ3S first-PC INT8/spec1. FRESH [Kapitsa#1151](https://github.com/nace-ai/kapitsa/pull/1151) OPEN dense27B KQuant KL0.0544→0.0349, top1 91.2→92.9%, GSM8K not significant, **speed held due missing MTP config**; new 35B-A3B separate KQuant record [#1148](https://github.com/nace-ai/kapitsa/pull/1148) MERGED and catalog [#1149](https://github.com/nace-ai/kapitsa/pull/1149) OPEN/private repo. FRESH [TensorFold#2751](https://github.com/ashhart/TensorFold/issues/2751) QFN MLX4/32 16bit scales+bias indices 10% fewer weight bytes, M3Ultra drafted +3.2% but prototype +7.3GiB resident (not old M1 feasible yet). FRESH [TensorFold#2756](https://github.com/ashhart/TensorFold/pull/2756) OPEN dense27B complete immutable KV prefix pages shared between agent checkpoints; host tests only, device M3/M5 pending. UPDATED OLD [TensorFold#2725](https://github.com/ashhart/TensorFold/pull/2725) M5Ultra cache-filled prefill TTFT−3.5%/−5.9% with 360 token hashes equal, READY-TO-LAND comment but still OPEN. UPDATED OLD [Basalt#282](https://github.com/jesdga95/basalt/pull/282) older Windows 5070Ti source GSQIQ3S true120K spec4 staging72→76.9TG, FRESH Nov10 quality comment KLD 0.21948→0.22074, top1 87.90→87.82%; never first frozen 32K/spec1. FRESH [Basalt#313](https://github.com/jesdga95/basalt/issues/313) OTHER 5090 183GiB host high Q6/Q8 864K needle retrieval (not xHigh); cgroup caps can collapse TG95→6. [antirez DS4#1340](https://github.com/antirez/ds4/pull/1340) OPEN chunk-aligned continued checkpoint cuts redo5307→1211 tokens on OTHER DeepSeek V4, not old M1 source QFN. NEGATIVE no verified official Qwen4 weights; third-party Qwen4-named placeholders not releases. Gosset decoder/physical load unverified, no new qualifying model. Owner 2×separate M1Max32GPU64 source originalGSQXXS physical128K278PP34.2TG and259K258PP31.7TG historical; dual sourceIQ3S and 3–5 correct xHigh agent UNMEASURED, AMD RX6800 nonXT host16GB. No owner machine action or benchmark, HIGH approval remains enforced.

|Rank|Discovery|Evidence/next necessary check|
|---|---|---|
|1|KQuant dense27B fidelity|Need complete runtime/MTP config and M1 difficult agent outcomes|
|2|Basalt NVFP4 KV|Savings verified on dual5080 but KLD/top1 and TG worse; first PC unchanged|
|3|TensorFold 27B immutable KV-prefix pages|M3/M5 device test and cross-agent state correctness unrun|
|4|TensorFold QFN MLX scale index|Preliminary +3.2% TG but +7.3GiB until prompt-index frees originals; not source GSQ|
|5|Basalt source GSQ expert staging|Older 72→76.9TG true120K spec4, newly smaller sample top1/KLD slight worse|
|6|Qwen4 official / Gosset|No source verified released Qwen4 or loadable Gosset M1/PC checkpoint|

## Archived prior discovery seeds

# Active ranked leads — Nov 10 06:47 EST

## Nov 10 2026 06:47 EST — Splash1.6.1 proposal, concurrent agent cache, dense27B drafts & quant residency

[Strict watch](./RESEARCH-WATCH-2026-11-10-0647.md) · [Splash/M1 note](./SPLASH-161-M1-RESIDENCY-2026-11-10.md) · [Dense27B DSpine+Relay](./DENSE27B-DSPINE-RELAY-2026-11-10.md). Prior 2026-11-09T18:05:38Z; next strict cutoff **2026-11-10T11:47:57Z**. FRESH [Splash#733](https://github.com/incoai/splash/pull/733) 1.6.1 ENGINE OPEN/unreleased, cold shader warmup, long-context memory-wall/SSD watchdog and prompt-cache fixes, optional PLE streams28.8GB through≤237MiB (M5 Pro TTFT +0.6s at6K); NO Apple7 exact M1 qualification. FRESH [TensorFold#2699](https://github.com/ashhart/TensorFold/pull/2699) MERGED Nov10 09:00Z fixes multiagent cache state eviction, M3Ultra dense27B 8-agent follow-up TTFT50→1.4s,16-agent546→16.5s, output tokens match; no M1 QFN result. FRESH [Basalt#311](https://github.com/jesdga95/basalt/pull/311) OTHER NVFP4 PLE Q8→IQ4NL save23.2GiB, KLD NOT RUN and greedy changes first token, original GSQ first PC remains frozen. FRESH [Splash#731](https://github.com/incoai/splash/pull/731) DSpine dense27B M5Pro opt-in 8-row worse−5.8% solo vs DFlash, research16-row long native +6–7% but HTTP unqualified/experimental; NOT QFN, not M1. FRESH [Kapitsa#1122](https://github.com/nace-ai/kapitsa/pull/1122) M5Pro dense27B MLX3bit 4K prefill446→769/8bit443→739/ GGUF Q4KM444→751, unchanged Q4g64, no M1 matrix units. FRESH [TensorFold#2718](https://github.com/ashhart/TensorFold/pull/2718) TCP host collective USB4 two AMD Linux boxes tests, NO inference TP2/Relay engine. FRESH [Strata#5709](https://github.com/Niko1221/Strata/pull/5709) OTHER RTX4080Super16 source GSQXXS short95/agent113.6 vs GSQIQ3S91.4/108.9, not full context coding. [mlx-serve#1153](https://github.com/ddalcu/mlx-serve/issues/1153) malformed required QFN tool name, real agent correctness gate. NEGATIVE no official Qwen4 downloadable weights. REDISCOVERED Gosset3.65BPW custom gated dense27B Nov9 not independently verified. Exact owner two M1Max32GPU64 originalGSQXXS floor DS4 physically128K278PP34.2TG/259K258PP31.7; dual sourceIQ3S true128/262K and3–5 correct xHigh NOT achieved. Owner first original GSQIQ3S Basalt historical source bytes unverified,32K INT8KV **spec1 OFF**, double precision and fully executed tool correctness HIGH only; RX6800 nonXT host16GB. No owner actions.

|Rank|Lead|F/N/E/A/I (0–3 each); triage only|Next acceptance gate|
|---|---|---|---|
|1|Splash 1.6.1 M1 PLE streaming and cold precompile|3/3/2/3/0|2021 M1 verified cold, full 128/259K task correct|
|2|TensorFold merged multiagent cache protection|1/3/3/3/0|QFN state-aware M1 agent persistence|
|3|Dense27B DSpine Metal 16-row research|1/3/2/2/0|HTTP correctness, Apple7 exact and hard agent tasks|
|4|Basalt PLE IQ4NL −23.2GiB|1/3/2/2/0|BF16 KL and coding outcome; NOT frozen first PC|
|5|TensorFold TCP host USB4 transport|1/2/3/2/0|Integrated TP=2 and cross-platform checkpoint parity|
|6|Qwen4 official weights, Gosset reproducibility|1/1/1/2/0|Official model manifest / loader / full coding trials|

## Archived earlier scratchpad

# Ranked Project51 discovery seeds — November 9 13:05 EST

## November 9, 2026 13:05 EST — first measured dense27B CUDA→Mac Relay analogue and new draft ecosystem

[Strict watch](./RESEARCH-WATCH-2026-11-09-1305.md) · [Relay deep dive](./RELAY-DENSE27B-GB10-M5-2026-11-09.md) · [model radar](./RESEARCH-MODEL-QUANT-RADAR.md). Previous verified cutoff 2026-11-09T02:38:09Z; new strict cutoff 2026-11-09T18:05:38Z. FRESH [TensorFold#2648](https://github.com/ashhart/TensorFold/pull/2648) actual dense27B GB10→M5Max ConnectX prefill handoff,120832 tokens TTFT385.3→136.4sec, seven turns468.7→208.7sec, but GB10 alone faster and teacher-forced correctness1/5 FAIL. NOT owner CUDA5070Ti→M1 QFN Relay. FRESH [llama.cpp#31941](https://github.com/ggml-org/llama.cpp/pull/31941) DSpine draft port OPEN, CPU/CUDA/HIP/Vulkan parity, no M1 Metal. FRESH [Kapitsa#1107](https://github.com/nace-ai/kapitsa/pull/1107) dense27B retrained16-row DFlash2 M5Pro ~8% TG in2/3 rounds, M3Pro~3%, no M1. FRESH [Strata#5675](https://github.com/Niko1221/Strata/issues/5675) M5Ultra sourceGSQIQ3S short/4K/16K146.2/135.8/124.9TG and UD-IQ4XS residency stream 65→127 at16K, not owner. FRESH [Strata#5674](https://github.com/Niko1221/Strata/issues/5674) Metal two-request batch-MTP crash. FRESH [TensorFold#2686](https://github.com/ashhart/TensorFold/pull/2686) warm prompt chunk/tool-result/reasoning parity, unproven served loop. FRESH [Basalt#303](https://github.com/jesdga95/basalt/issues/303) OTHER 4x5070Ti OpenCode concurrent title request PP3402→520-897, not owner source quant. FRESH [Basalt#306](https://github.com/jesdga95/basalt/pull/306) OTHER 5070Ti i1-IQ3S142.9TG/PP4427 at16K NOT original ISTA. NEGATIVE no independently verified official downloadable Qwen4 weights in checked primary artifacts. Owner exact M1Max source GSQXXS physically128K278PP34.2TG and259K258PP31.7TG holds, two separate64GB Macs, dual original IQ3S and3–5 correct xHigh not measured. Frozen owner first-PC original IQ3S official historic pack byte proof still unverified. No owner device/CI/download actions.


|Rank|Lead|Next gate|
|---|---|---|
|1|TensorFold #2648 dense27B GB10→M5 Relay TTFT 385.3→136.4s|Fix 1/5 failed parity, inventory state, test Apple7+TB4 feasibility|
|2|llama.cpp #31941 DSpine 27B new draft PR|Metal implementation and held-out code-task performance|
|3|Strata #5674 M5Ultra batched MTP crash|Don't enable multiagent batch MTP until corrected|
|4|TensorFold #2686 warm-next-turn prompt parity|Multi-turn real tool-use replay|
|5|Kapitsa #1107 dense27B retrained DFlash2|M1 exact task baseline and fidelity|
|6|Official Qwen4 weights NOT verified|Actual model source manifest, architecture, fit|

## Prior scratchpad


# Ranked Project51 discovery seeds — November 8 21:38 EST

[Watch](./RESEARCH-WATCH-2026-11-08-2138.md). Previous 2026-11-08T21:35:14Z, next strict 2026-11-09T02:38:09Z. Frozen two independent M1Max32GPU64 source GSQ IQ3XXS min/IQ3S stretch, true source XXS DS4 128K278PP34.2TG,259K258PP31.7TG, dual IQ3S128/262K and3–5 correct xHigh UNMEASURED; owner Linux 5070Ti16/64GB source GSQIQ3S first32K full tools HIGH.

| Rank | Lead | Test required |
|---|---|---|
|1|FRESH [Strata#5615](https://github.com/Niko1221/Strata/issues/5615) tuned draft short92.6 vs83TG, full tasks wall1430→1660, graded pass98→96|Same model revision and correct tool tasks vs TG|
|2|FRESH [Strata#5612](https://github.com/Niko1221/Strata/issues/5612) subagent steals parent's137K cache; borrow TTFT23.6→0.67s, no output identity|Greedy identical and true agent run, M1 support|
|3|UPDATED OLD [Paperniuk#51](https://github.com/paperniuk/splash/issues/51) real M1Max32GPU64 m32 compiler217.6s >30s watchdog; warm16/16 small tasks, cold6/16|PR52 real cold patch test and physically128/259K|
|4|FRESH [TensorFold Metal DSpine#2634](https://github.com/ashhart/TensorFold/pull/2634) dense27B M3Pro agent3.88 vs DFlash2 4.92; CUDA#2633 agent+17%TG chat/code worse|Served Metal, actual tasks, not sparse QFN|
|5|FRESH [Strata#5623](https://github.com/Niko1221/Strata/pull/5623) shared host KV chunks COW, recurrent/draft private|Actual multistream QFN, M1 not supported|
|6|UPDATED OLD [Splash#715](https://github.com/incoai/splash/issues/715) M4Pro compiler hang even ANE off|Cold/warm shader different family control|
|7|FRESH [Kapitsa0.2.32](https://github.com/nace-ai/kapitsa/releases/tag/v0.2.32) Ollama API/cancel recovery not original GSQ M1 tested|Native exact quant and context|
|8|FRESH [Basalt NVFP4 dual5080#295](https://github.com/jesdga95/basalt/pull/295)355TG OTHER247GiB host|Cannot extrapolate one5070Ti IQ3S|
|9|NEGATIVE no verified new official Qwen4 weights or dual M1 source IQ3S full128/262K|Primary artifact/physical benchmark|

No owner machine actions; next cutoff 2026-11-09T02:38:09Z.
