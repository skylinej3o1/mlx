# Project 51 / Relay — research watch 2026-10-17 15:05 EDT

**PREVIOUS STRICT CUTOFF:** **2026-10-17 16:08:29 UTC**.
**NEW STRICT CUTOFF:** **2026-10-17 19:05:57 UTC** (user request 15:05:57 EDT).
**Protocol:** Canonical `RESEARCH-STATE.md`, `RESEARCH-TARGETS.md`, and `RESEARCH-WATCH-LATEST.md` read first; dated watch continuity confirmed. Queried live GitHub PRs/issues and selected web/model-card references. Only sources created/updated before strict cutoff are in-scope. Categories **NEW**, **UPDATE**, and **KNOWN** retained below; do not conflate a PR body updated after cutoff, an OPEN/stacked PR, physical model admission, training-context length, native actor quality, and sustained real agent runtime. All benchmarks external; **none conducted on owner hardware**. Only research docs updated; no numeric target/verifier/engine changes.

## Short verdict, ordered by direct hardware relevance

### 1. NEW, exact owned Radeon: Strata #2941 OPEN — mixed FP16-K / INT8-V QSA cache

- Author on physical **RX 6800 16GB gfx1030**, HIP, FlashNext **IQ3_S**, MTP spec4, **13,109 prompt tokens** reports `--kv k16v8` = **917.9 PP / 34.48 TG** vs INT8 **919.2 / 32.15** and FP16 **906.6 / 33.90**. The source explicitly says decode difference is **within run-to-run and draft-acceptance noise**. Do **not** present ~7.2% as demonstrated reliable speedup.
- Attention cache bytes per cell: INT8 **1056**, K16V8 **1552**, FP16 **2048**. At 96K ctx ×12 QSA layers, author estimates ~1.16 / **1.71** / 2.25 GiB host KV. At 32,768 resident cells, VRAM ~415 / **610** / 805 MB; K16V8 costs ~195MB more than INT8, displacing a material fraction of 16GB GPU expert cache. Draft KV remains INT8; streaming moves K FP16 and V data/scales separately.
- One author's SVG task **37K output INT8 /29K K16V8 /25K FP16**; illustrative *quality/length hypothesis only*, not a proven response improvement or token-efficiency causal estimate. Compatibility tested on gfx1030 for 13K/63K retrieval and 96K service, prefix restore, vision/adapt-async; **not** tested CUDA, batch, layer split, pipeline windows, elastic KV, 200–262K exact-owner host32GB. Parity tests report 4,872 snapshot checks and streamed/resident bitwise route equality. Precision might help QSA attention fidelity, but **memory cost and completed-task A/B decide adoption**. Do not turn on by default.
- Source: https://github.com/Niko1221/Strata/pull/2941 . Created 2026-10-17 17:55:50 UTC.

### 2. NEW, exact owner OS/RAM class: Linux glibc cache refusal and agent switch loss

- **#2934 NEW** Linux Ubuntu22/glibc2.35 / RTX3090 / **64GB RAM** / Flash IQ3_S / 262K: after repeated large session park/eviction, glibc's dynamic mmap threshold causes 16MiB freed conversation segments to remain inside userspace heap, so the `MemAvailable` physical-RAM gate sees no change. Example: three cached sessions evicted and then parking still refused; returning **214K agent re-prefills in 90s instead of ~11s**. A controlled system-level workaround `GLIBC_TUNABLES=glibc.malloc.mmap_threshold=4194304` (4 MiB) or `malloc_trim` proposed in **#2253** helped this specific machine, **with 2–9% observed cold PP overhead**, decoder unchanged; verify independently, no universal OS fix. This is a **very high-priority exact-headless-Linux/64GB qualification gate**: memory accounting, snapshot lifetime, library allocator, no silent resume misses.
- **#2930 NEW** Pi-style tool-agent switches with thinking excluded from resubmitted history; boundary checkpoints rotate out of `--prompt-cache` chain and superseded parked SUB copies are not recognized. Under 4-slot parking, MAIN gets evicted: 82K restored? No, MAIN re-read 82,329 tokens from **zero** in 174s in the author's 2xgfx906 setup. Proposed prefix-of-later-boundary criterion has unit test but not a merged fix. This does *not* establish all Pi harnesses fail; it flags our repeated subagent context pattern.
- Prior known **#2923** Windows3090/80GB RAM-tight resume loses 310–372K and incurs233–285s full prefill. Three independent causes need independent diagnostics: cache *not parked*, parked copy *superseded incorrectly*, or restore *skipped due to RAM*. Disk snapshot #2915 OPEN is an option but no 3–5-agent/full262K parity yet.
- Sources: https://github.com/Niko1221/Strata/issues/2934 ; https://github.com/Niko1221/Strata/issues/2930 ; https://github.com/Niko1221/Strata/pull/2253 ; previously #2923.

### 3. NEW, sampling correctness and regressions on Strata 0.1.45

- **#2940 NEW** notes `serve/server.py` in 0.1.45 merges the model-card instruct `presence_penalty=1.5` into non-thinking requests **including temperature 0** unless client/config explicitly sets 0. On a four-RX7900XT model, code ~89→65–72 TG; explicit presence penalty=0 restored91–96, and old 0.1.44 engine under *new* 0.1.45 Python server also regressed. This is a **sampling/config/server-policy regression**, not evidence that native CUDA engine arithmetic is 25% slower. For AA and Swift vs base A/B, log effective temperature, presence penalty, top-k/p, effort and thinking. Force exact same intended sampling values, including `presence_penalty: 0` for truly greedy control where appropriate; evaluate semantics before picking a default.
- **#2936 NEW** source-controlled RTX3090 (sm86) on Linux 64? actual RAM88GB and Xeon E5 CPU, 0.1.43→0.1.45 Flash IQ3_S with pinned same CUDA compiler/submodule and matching build flags: narrative **102.6→79.4 TG** (−23%), code **118.4→86.3** (−27%) with CPU-per-expert matched (82–85µs). This is one hardware/config-only contributor observation, **not** proof of owner sm120 regression but enough to require explicit version A/B after fixing effective sampling. 
- **#2932 NEW** dual Radeon Pro VII gfx906 on Linux finds 0.1.45 32K decode 51.3→44.8 (−13%) and **12/12 greedy replies differ** from 0.1.43.1. The observed card is **gfx906**, not owner gfx1030, and writer proposes wide top-k wave64 issue rather than proving it.
- **#2935 NEW OPEN** calibration survives individual dying candidates (e.g., adaptive-tier GPU copy gate) and records diagnostics rather than discarding all previous winners; measured RTX4080Super CUDA, HIP untested. Useful for owner automated calibration but do not treat a run that recovered from one crashing option as a production-stability certificate.
- Sources: https://github.com/Niko1221/Strata/issues/2940 ; https://github.com/Niko1221/Strata/issues/2936 ; https://github.com/Niko1221/Strata/issues/2932 ; https://github.com/Niko1221/Strata/pull/2935 .

### 4. NEW and already MERGED: oMLX #4637 cross-model GPU-hang mitigation

- **#4637** created Oct17 16:48:03Z; merged by 17:08:28Z; shares an MLX/Metal command queue across engine streams while retaining per-engine executors/encoders. Author physical **M3 Ultra512GB**, seven different models, fourteen active requests, before 75min **5 GPU resets /24 failed requests**, after 151min **0 resets /0 failed**, plus 1.2% two-engine synthetic throughput penalty; no direct M1 Max64 run, no proof all long-context GPU failures fixed. Plain MLX multi-queue repro strengthens causal case, but MLX private-member dependency and external-drafter VLM path remain uncovered. For your M1×2 **multi-model agent fleet**, track upgrade and create two simultaneously busy model stress + cache checkpoint correctness test.
- Separate **#4638 MERGED** improves HF downloader slow-link retry/resume progress only; lower Project51 priority.
- Source: https://github.com/jundot/omlx/pull/4637 ; https://github.com/jundot/omlx/pull/4638 .

### 5. NEW Splash FlashNext #447 split into 20 independently reviewable but stacked OPEN PRs

- **#449–#468**, created near **2026-10-17 18:13Z**, split the PREVIOUSLY KNOWN #447 FlashNext (and #448 MTP proposal) into review components: A/B logits oracle tooling, 64-row quant plane, indexed attention, expert slots/streaming, GPU/host steps, PLE row streaming, 512 experts, hyperconnection/GDN/QSA, terminal model. **Twenty OPEN dependent PRs are not 20 independently merged features, and not 20 independent benchmarks.**
- **#449 NEW** full-vocab logit dump and top1/KL control; useful as cross-engine parity infrastructure and *specifically* for a CUDA→Metal Relay state importer. **#467 NEW** reports teacher-forced compare with llama.cpp, 257 positions at1K/8K/32K: ISTA Q2_0 top1 ~96.9/96.5/97.3%, mean KL0.0034/0.0041/0.0051; Unsloth UD-IQ3_XXS top1 ~97.3/96.1/94.6%, KL0.0092/0.0085/0.0115. These are **same-GGUF cross-runtime numerical comparisons**, not token-identical and not comprehensive source-quality certification. llama.cpp itself differs by batch plan ~0.0012–0.0058 KL. Require repeatable M1 64GB B1 true-history parity and full source-like multi-agent correctness before Relay import.
- **#468 NEW** PLE `--ple-memory` SSD row-cache design, 36GB Mac author says UD-IQ3_XXS fits with 16G streamed experts +2G PLE cache; 36GB **M5** machine, not Apple7 M1. **#447/#448 already described M5 benchmarks in previous watch**, do not double-count them as new.
- Source: https://github.com/incoai/splash/pull/449 ; https://github.com/incoai/splash/pull/467 ; https://github.com/incoai/splash/pull/468 ; https://github.com/incoai/splash/pull/447 ; https://github.com/incoai/splash/pull/448 .

### 6. NEW TensorFold #1005 pushes FlashNext Metal 1,048,576-token admission (M5 Ultra256GB ONLY)

- **#1005 OPEN STACKED** on #986; static YaRN ×4 extends FlashNext RoPE and QSA indexer, measures actual needle hits at **138,830;553,139;1,032,827 tokens**, cold TTFT **34;169;417s** respectively on **M5 Ultra256GB with 203.2GiB wired**. At 1M, author describes 1M context resident prompt and draft/plain matching at316K. **Not tested quality at 1M**, not owner M1Max64 or RTX5070Ti, and explicit source says **two-Mac pair refuses >trained262K**. This is important architecture progress but cannot justify any 128K or 262K owner target increase.
- Source: https://github.com/ashhart/TensorFold/pull/1005 .

### 7. NEW AMD 64GB example; M1 Metal loader correctness

- **#2933** author RTX? actually **RX7900XTX 24GB +64GB Windows11**, Flash IQ2_XS 80.2 short chat/90.2 agent and Coder IQ1_M 65.6/83.4, 16K PP1367/1631; actual255K fill3.7min/3.2min, HumanEval81/82 vs82/82. Single model/session, not source Swift IQ3_S, no reasoning/long-agent tool quality. Windows pagefile/commit gate required64GB pagefile to restore13.26GiB expert cache vs4.93GiB with48GB pagefile. **Owner native Linux uses different commit/reservation behavior; don't translate pagefile fix to Linux.**
- **#2931 OPEN** M2Max96GB Metal loader for uncommon quantized HC and shared-expert GEMV corrects first-token NaN/invalid vocab and missing GEMV for IQ3_XXS/IQ2_S, 9–10TG streamed 88.9GB 0.1.45 custom fine tune. Not native owner M1 Swift IQ3_S performance; critical warning that successful load/coherent text is not parity. Need exact tensor dtype and sample-logit equality.
- Sources: https://github.com/Niko1221/Strata/pull/2933 ; https://github.com/Niko1221/Strata/pull/2931 .

## Unchanged key anchors (KNOWN; not measured anew this pass)

- Source-quality daily driver remains **Swift1.5 GSQ-RCO IQ3_S at low effort** for RTX5070Ti16+64GB / Intel Ultra7-265F / **native headless Linux** based on prior Oct14 #1850 external quality battery, with Swift Q2_0 low as fast but quality-sensitive alternate.
- oMLX M1Max64 dense27B oQ4e + custom verify PR **#4496 OPEN** best relevant physical **24.2TG at133K**, no verified 3bit mixed conversion retaining 4bit verifier speed. `#4508` has *already merged* adaptive DFlash width, do not multiply Agention 3.2x.
- Direct owner class Strata Swift IQ3_S fully filled **262K + 4K generation + 16+ agent turns**, **three-to-five simultaneous retained session tests**, and **two-M1 TB4 FlashNext 40TG@128K/400PP** remain unverified. No physical complete QSA/GDN/PLE/CUDA→Metal handoff, no combined Gyro Signal released; model cards top out Oct13 update. No hardware purchase or numerical target move warranted.
- Different RTX5070Ti from older WSL2+Ryzen9800X3D PDF is **NOT** owner deployment identity. GPU headless native Linux may reduce overhead but its performance benefit is not yet measured.

## Actionable next gates and branch decisions

1. **Pin Strata 0.1.44.1 +0.1.45 on owner's exact native Linux sm120 with same model/quant/sampling and CPU expert pool;** log effective presence_penalty and `reasoning_effort`, make controlled greedy output hashes (and separately native sampling). Monitor sustained 32K/128K/262K, verifier acceptance, CUDA compiler hashes, no overfit to sm86/gfx906.
2. **System RAM and conversation cache:** reproduce 3–5 concurrent Pi agents and 32K/128K/200K growing session switching. Distinguish clean parked snapshot, false superseded/drop (#2930), glibc mmap gate (#2934), RAM-pressure restore miss (#2923), SSD snapshot. Test allocator `GLIBC_TUNABLES` as an isolated OS-control with long soak and full prompt/content equality before considering default; do not silently weaken RAM headroom.
3. **RX6800 HIP gfx1030:** isolate `k16v8` vs int8/fp16 on same Swift/base IQ3_S 13K/64K/96K, quality + solved-task wall, PLE/VRAM expert residency and QSA prompt correctness; then 1h+ #2788 async copy soak. No 262K promise with host32GB.
4. **M1 Max ×2:** oMLX #4637 multi-model queue stress with DFlash/MTP where supported, #4496 dense27B 133K reproduction + sampling parity; evaluate Splash 20-stack source logit oracle on physical M1/64GB only if Apple family7 patch #442 and experts/PLE offload runs. Test editor-prefix and repeated tool budget stability (#4627), avoid M5/M5Ultra transfer.
5. **Relay:** retain committed-frontier tensor lineage; check QSA pooled-index states, GDN recurrent states, KV keys and quant formats, draft lineage and abort-epoch fences. Splash KL logit oracle useful but does not establish exact imported-state parity.

**Research-only changes. No numerical target, source GGUF, inference binary, verifier, or kernel modification. Next strict watch begins after 2026-10-17 19:05:57 UTC.**

## Primary sources
- https://github.com/Niko1221/Strata/pull/2941
- https://github.com/Niko1221/Strata/issues/2934
- https://github.com/Niko1221/Strata/issues/2930
- https://github.com/Niko1221/Strata/issues/2940
- https://github.com/Niko1221/Strata/issues/2936
- https://github.com/Niko1221/Strata/issues/2932
- https://github.com/Niko1221/Strata/pull/2935
- https://github.com/jundot/omlx/pull/4637
- https://github.com/incoai/splash/pull/449
- https://github.com/incoai/splash/pull/467
- https://github.com/incoai/splash/pull/468
- https://github.com/ashhart/TensorFold/pull/1005
- https://github.com/Niko1221/Strata/pull/2933
- https://github.com/Niko1221/Strata/pull/2931
- https://github.com/jundot/omlx/pull/4496
