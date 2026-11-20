# Project 51 research watch — November 20, 2026 at 16:00 EST

**STRICT DELTA WINDOW:** previous verified research cutoff **2026-11-20T19:04:42Z** (14:04:42 EST) through this user's request **2026-11-20T21:00:28Z** (16:00:28 EST). **Verified input GitHub HEAD:** `15d0a3b23edab5fc535d9ca645f89e2c2d67d741`. Public-source research only; FRESH = underlying creation or evidence in the interval, UPDATED OLD = specific new comment/measurement/review in older issue/PR, REDISCOVERED = material published earlier uncovered now, ANALOGUE = different model, quant, hardware, runtime or not verified. Tool-provided current `updated_at` values can be later than the cutoff: do not treat those future changes as evidence. Source links refer to publicly read primary GitHub API issues/PR bodies and authoritative Chinese Alibaba model changelog. No owner-device hardware run, installs, source code changes, CI, re-quantization or runtime configuration work; documents only.

## A. Highest-signal new findings

### 1. FRESH on exact M1 Max 32c/64GB hardware — [Strata #6434](https://github.com/Niko1221/Strata/pull/6434), created **2026-11-20T19:12:03Z**, OPEN DRAFT

Apple M1 resident-v2 MoE expert GEMM now optionally uses eight-row tail instead of padding every final expert group to16 (`STRATA_METAL_PROMPT_M8_TAIL=1`, OFF by default). **Author's device: 2021-class M1 Max 32GPU 64GiB**, macOS26.6.2, upstream based `3142b66`, branch `0689549`. On synthetic **Q2_0 gate/up/down** at300 routed rows, padded rows **8192→4592**, per-layer expert-chain GPU **18.155→15.266ms (−15.9%)**, controlled output hashes pair-match across Q2_0/Q5_0/Q4_K/Q5_K fixtures. **Earlier local branch, source ISTA GSQ-RCO Q2_0 with PLE, prefill chunk256:** 2K prompt **239.41→254.85 tok/s (+6.45%)**, 4K **235.26→249.88 (+6.21%)**, first logit hashes and128 generated IDs matched per input. **Crucial negative replication:** new upstream complete model at chunk256 stopped by 15% memory guard in stock and patched; chunk128 retry stopped during stock load after48 swapouts, patched never run; this is **not** an upstream full-model confirmed gain. No source **GSQ IQ3_XXS/ IQ3_S**, no physically128K or259K, no concurrent 3–5 agent quality. More relevant for owner M1 hardware than preceding M2 split-K #73, but format/memory constraints remain.

### 2. FRESH SSD conversation persistence after process restart — [Strata #6439](https://github.com/Niko1221/Strata/pull/6439), created **2026-11-20T20:13:19Z**, OPEN

New OFF-by-default `--conversation-spill-persist` stores SSD tier in stable fingerprint-specific folder, index files validate model+config, incomplete/foreign shards removed, keeps LRU capacity across restarts, and second simultaneous same-model process falls back to temporary tier. **Core tests:** `conversation_spill_test` 96 checks, `conversation_file_test`209, `conversation_cache_test`13,534 passed; reports adoption of **74 conversations /85,794MiB** after restart. **Not** a 74-real-inference end-to-end correctness verification, full engine/CUDA/HIP and Windows paths untested, depends on still-open fingerprint fix #6305. This is separate from older [Strata #6288](https://github.com/Niko1221/Strata/pull/6288) 2×CMP50HX stage split/SSD proposal. Significant Molt-type long-session cache mechanism, **not proof original M1 external Splash state survives**.

### 3. FRESH large-context original GSQ IQ3_S correctness failure — [Strata #6437](https://github.com/Niko1221/Strata/issues/6437), created **2026-11-20T20:07:50Z**, OPEN

RTX6000 Ada48GB/host128 Windows, original **Qwen3.8-Flash-Next GSQ-RCO IQ3_S** 2-part GGUF incl PLE, Strata0.2.16/engine0.1.62, physically **139.6K-token input**, `--kv int8 --mtp --spec 4`, 262K configured context. **3 of27** replies ended midword/midtable with apparently clean `finish_reason:"stop"`, 12.4K–17.5K outputs, under 24K limit. Short1–3K input **0/270**; fp16 **0/3**, k8v4 **0/3** too small to attribute cause to int8; no draft-off control or 0.2.17 replication yet. Independent author report, not seen on owner's systems. Add finish reason/terminator/content integrity and repeated long-agent tasks to evaluation; don't assume returned stop=success or claim model itself broken.

### 4. FRESH CUDA engine parking proof of concept — [Strata #6436](https://github.com/Niko1221/Strata/issues/6436), created **2026-11-20T20:04:07Z**, OPEN issue, NOT landed feature

On one RTX3090Ti24GB hosting Swift QFN IQ3_S with MTP and long 410K–508K context, an `LD_PRELOAD` interception of CUDA allocations/VMM parked **~23,180MiB resident GPU→836MiB** while maintaining device virtual addresses, preserved conversation with ~507K reused on next request. Six cycles: pinned host kept park **2.07s** after first13.4s, unpark **2.2–2.5s**; without pinned copies kept ~13.2–13.5s park and4.5–4.7s unpark. **Cost: +22.3GiB host RAM while parked**. Post-unpark TTFT ~0.59–0.62s vs no park0.61–0.64, throughput112–117 vs111–118 tok/s. Output identity **not deterministically proven**, author observes temp0 variance without parking. This is an interesting shared-GPU concept for local multi-agent, but requires native engineering, sufficient RAM, CUDA, and no valid external Metal transfer claim.

### 5. FRESH on another dual CUDA rig — [Basalt #509](https://github.com/jesdga95/basalt/pull/509), created **2026-11-20T20:36:22Z**, OPEN

Co-stage **CPU expert misses** alongside peer expert tier; maintains primary/peer hits, skips staging while adaptive refills use interconnect. **Two RTX5080** mixed IQ3_S-Q4 pack, A/B/B/A, int8 KV, no adaptive swaps in first series: conversation window **24.589→20.861ms (−15.2%)**, prose **20.592→18.250ms (−11.4%)**; number of windows differs and outputs **NOT bit-identical** as some experts move CPU→GPU. With adaptive swaps improvement in conversation16.164→15.427ms, structured20.985→19.941ms, prose12.286→12.303ms essentially flat. Quality teacher forced 25,500 rows, BF16 reference: mean KLD **0.095644→0.095278**, top1 **89.9333→90.0078%**, PPL **3.23261→3.23581 (+0.099%, bootstrap interval −0.098% to+0.308%)**; lower mean KLD does not establish full coding agent quality. Previous single RTX16GB adaptive-staging counterexample remains. No direct user 5070Ti single-card or exact source original IQ3_S no draft equivalence.

### 6. UPDATED OLD new long-context split prefill measurements — [Basalt #501](https://github.com/jesdga95/basalt/pull/501) originally created **2026-11-20T12:27:58Z** BEFORE prior cutoff; updated **2026-11-20T19:26:01Z** inside this delta; OPEN

On **2×RTX5080** original-ish IQ3_S-Q4 mixed pack and 232,031-token occupied prefix, when `--prefill auto:8192` under-reserves finite-draft handoff buffers, planner rejects viable split; patches buffer row size, PP uses peer. **Cold TTFT 74.76→40.53s (−45.8%)**, while at 32K chunks **33.22→33.19s** (no gain). Warm followup reused232,024 tokens and TTFT **0.417→0.416s**. **Correctness caveat:** at8K mode stock/split output differs; controlled 255 target top picks agree **244/255 (95.7%)** with changed target NLL. This is a *planner enabling split*, not same-algorithm 46% generalized speed, and not CUDA5070Ti→M1 Relay. Distinguish new update from original creation.

### 7. UPDATED OLD multi-GPU BF16 HC copies — [Strata #2427](https://github.com/Niko1221/Strata/pull/2427) older Oct PR, updated **2026-11-20T20:49:36Z**, OPEN

On different 2×RTX5060Ti16 UD-Q4_K_XL, Q8 hyper-connection option omits redundant BF16 copies from each stage; mainline decoder 4K **44.6→46.1 tok/s (+3.4%)**, 32K **41.1→44.0 (+6.9%)**, stage cache grew. On by default for certain UD packs, **greedy answers differ from v0.2.17** because Q8 dequantization replaces BF16 reads and changes residency; not owner single source GSQ IQ3_S Basalt first experiment.

### 8. FRESH tool-argument typing for coding agents — [antirez/ds4 #1363](https://github.com/antirez/ds4/pull/1363), created **2026-11-20T19:30:37Z**, OPEN

QFN sometimes writes XML tool boolean parameters as Python-style `True`/`False`; parser formerly exposed JSON strings `"True"`/`"False"`, which clients reject when schema expects boolean. Proposed schema-aware coercion only for declared bool parameters, preserving actual string arguments. **M5 Max128** QFN Q4 local tool probe from **0/3→3/3 valid**. Tests pass. No speed effect, no exact old M1 GSQ cross-runtime verification; high-value tool correctness regression fixture.

### 9. FRESH unrelated GPU/quant version caveat — [Strata #6435](https://github.com/Niko1221/Strata/issues/6435), created **2026-11-20T19:31:06Z**, OPEN

Different **RX9070 non-XT RDNA4 +32GB host + Gyro-S TQ1_0** on Windows; v0.2.17 default cold55K prompt **~1057** vs v0.2.16 **~1524tok/s**, decode**62.2 vs70.7**, partly 4GiB host reserve and default rank7 skip disabled; author both custom settings ~1422 PP/84.2 TG but route skipping changes output semantics. **NOT** user RX6800 nonXT RDNA2 +ONLY16GB host and NOT original GSQ quant; do not transplant flags or promise feasibility.

### 10. Other fresh leads with limited direct relevance

- **[vLLM #69024](https://github.com/vllm-project/vllm/issues/69024)** NEW 19:16:58Z, hybrid prompt-tail checkpoint CPU-offload may lose remainder of restored chunk, material Relay/state correctness warning but unrelated to actual CUDA→Metal Flash-Next proof.
- **[vLLM #68347](https://github.com/vllm-project/vllm/pull/68347)** UPDATED OLD, OPT-IN prefill skipping draft-side context for model-specific target-KV-only speculators (Gemma4 tested H200; Hy4 DFly2 future). Explicitly says DFlash-style draft still needs own context K/V. **DOES NOT** solve original GSQ QFN CUDA→Metal recurrent GDN/QSA/PLE/MTP. Its reported Gemma4 H200 P/D end-to-end eval latency actually rose27.9→32.5s while prefill draft memory dropped: don't promote abstract component savings without net workload wins.
- **[incoai/Splash #793](https://github.com/incoai/splash/issues/793)** FRESH Nov20 19:19Z M5Max user requests dense27B 8-bit model, no benchmark/m1 original source data.
- **[Kapitsa catalog #1366](https://github.com/nace-ai/kapitsa/pull/1366)** merged20:00Z adds Hy4-flash 133.83GB artifact *not* practical in64GB old M1 memory, no Qwen4 evidence. No new comparable Paperniuk Splash source original GSQXXS physical128/259K benchmark after previous #72/#73.
- No new actual direct original GSQ XXS M1 Max32GPU dual-node performance measurements, nor any independently proven distributed two separate M1Max64 decode.

## B. China/US Qwen4 Flash verification (negative, not proof it never ships)

Official [Chinese Alibaba Qianwen model changelog](https://platform.qianwenai.com/docs/changelog/models) **current top shows Qwen4-Max on Nov16 and Qwen4-Max Preview Nov11**; up through cutoff no `qwen4-flash` or `qwen4-27b` open weights, tensor manifest, active/total parameter sizes, PLE/MTP architecture, GGUF quant bytes, or licensed open model date from [official Qwen HF](https://huggingface.co/Qwen). Targeted Linux.do, Zhihu, V2EX and US Reddit search found only older rumors (30B/3.3B Dec20; 125B-ish; 200–300B+), restated model family slides or unrelated `Qwen4-Max` API provider. No authoritative fresh independent Qwen4-Flash size leak during strict interval. Name `qwen4exp` in Basalt/Strata Qwen3.8-Flash-Next code is **an engine class, not proof Qwen4 weights shipped**. Avoid mixing Tencent Hy4 with Alibaba Qwen4.

## C. Hardware-specific decisions and unchanged hard guardrails

- **Two independent 2021 M1 Max 32 GPU /64GiB Macs**: default minimum original ISTA-DASLab pristine QFN GSQ-RCO **IQ3_XXS**, IQ3_S preferred if practical; no automatic shift to pruned Coder/IQ2. Historic original source XXS physically128K **PP278/TG34.2**, physically259K **PP258/TG31.7** unchanged, and May2027 40–48/36–44 TG still forecasts only. New Strata #6434 is exact *hardware class* but Q2_0 quant and 2K/4K, unreplicated latest full-model.
- **RTX5070Ti PC**: freeze initial experiment one NVIDIA RTX5070Ti16 + Intel CoreUltra7 265F +64GB DDR5-4800 Linux, original pristine ISTA GSQ-RCO **IQ3_S**, historical Basalt official `.basalt` v2 model shards/PLE provenance, actual **32K** context, **one slot**, **INT8 KV**, `spec=1 NO DRAFT`, CPU-double and exact complete tool/file-task validation. Other dual5080 drafted/mixed quant PRs do NOT modify first run. Prior Basalt loader #430 independently retested elsewhere and tool write delimiter #429 still OPEN.
- **Secondary RX6800 NON-XT VRAM16 + ONLY16GB host RAM**: no direct source-GSQ IQ3_S full model fit or meaningful cold PP/TG established, RX9070 RDNA4/32GB #6435 irrelevant as feasibility proof.
- **Relay vs oMLX partial prefill**: Native oMLX helper is not external GGUF Splash, no demonstration of exact CUDA5070Ti prefill state→old M1Max decode for recurrent GDN, QSA indexer, PLE, KV, MTP and tokenizer/template. New CPU/GPU stage and SSD survival work are *architectural analogues only*.
- **Dual M1**: serve independent full model agents on each separate RAM island as baseline. Need strict complete tasks/hour, transient peak RAM, tail latency, safe tool calls and restored first answer to justify any split inference.

## D. Discovery priority updates and next check (not authorized to run)

1. **NEW first-priority OLD M1 candidate:** compare Strata #6434 8-row tail and Paperniuk #73 Split-K *only when format/quant parity verified*: source **GSQ IQ3_XXS**, occupied128K and259K, multi-agent recall, full coding task hashes, first response after SSD/engine restart and correctness. The 15.9% fixture is not whole-model TG.
2. **Agent recovery:** #6439 fingerprint persistent SSD and #6436 CUDA VMM park: classify offline state durability vs active GPU state parking. Measure saved state vs migration, memory tax, recover-to-correct-answer.
3. **Agent fidelity:** repeated original GSQ IQ3S 139.6K truncation #6437; boolean tools #1363; prior #790 JSON grammar; #429 Basalt literal delimiter; compare clear final outputs/tool count/file hashes across versions/guards.
4. **Avoid misleading speedup extrapolation:** Basalt #501's dramatic 232K prefill result is due to *enabling split previously disabled*, changes outputs; #509 CPU staging changes placement; Strata #6435 performance gain turns expert skipping on and changes quality.
5. **Qwen4 official artifact watch** until named firstparty model id, manifest, PLE and MTP bytes, memory feasibility and actual model-card eval.
6. **Frozen owner PC run unchanged, NO execution.** No CI, model downloads, hardware tests, source edits, user runtime changes without separate explicit HIGH approval.

## E. GitHub provenance

- Input branch HEAD `15d0a3b23edab5fc535d9ca645f89e2c2d67d741`; previous 2026-11-20T19:04:42Z; cutoff **2026-11-20T21:00:28Z**; source dates scoped strictly.
- Documentation-only proposed delta: new dated watch, byte-identical LATEST, focused M1 cache-and-fidelity note; prepend only research annotations to canonical README/STATE/TARGETS, scratchpad, quant radar, frozen PC and Metal plans.
- Commit and HEAD verification **must occur after writing**; this watch does not predict the resulting SHA. Source reports contain developer/test claims rather than owner-device independent reproduction.
