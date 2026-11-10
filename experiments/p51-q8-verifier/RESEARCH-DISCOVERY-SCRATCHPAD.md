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
