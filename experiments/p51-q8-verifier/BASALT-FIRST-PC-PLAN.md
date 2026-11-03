# Project 51 — Basalt-first RTX 5070 Ti PC plan

## November 3, 2026 13:50 EST — near-card 5060Ti source IQ3_S physical rates, source main moves, FIRST PC gate unchanged

[Latest watch](./RESEARCH-WATCH-2026-11-03-1350.md) strict cutoff **2026-11-03T18:50:28Z**. First PC **ONE Linux RTX5070Ti16 sm120/CoreUltra7 265F/64GB DDR5/2TB NVMe**, **ONLY pristine ISTA GSQ-RCO IQ3_S official .basalt v2 full checkpoint**. New [Basalt #226](https://github.com/jesdga95/basalt/issues/226) is **OTHER RTX5060Ti16 sm120/Ryzen7600/60GB** using original source IQ3_S, q4_0 KV and spec6: **77–78 TG short; 57.9–66.1 TG after134K history; cold actual91/162K prompt2030–2130 PP**, 262K just max-context configuration. No quality-equivalent test, tool-call suite, owner's Linux reference, or physical full262K. Correctly retract claim DFlash2 0.7GB replaces a 5.2GB Basalt MTP layer: **Basalt built-in ~786MiB, DFlash2 ~625MiB** (~160MiB delta), DFlash2 per-run switch NOT available. Do not use other card's numbers as direct 5070Ti projection.

**Source ancestry after previous 05:35Z snapshot:** eligible latest main [6e67f90c](https://github.com/jesdga95/basalt/commit/6e67f90cd303eb1230a001cfe13ed683ded0781b) 17:21Z, additional explicit IQ3XXS/IQ1M packed byte extraction06:07, generalized packed accessor07:04, tolerant RAM guard11:24, expert-profile flag16:37, docs BF16 quality reference. Prior IQ3S/IQ2S numerical fix **5bdb6c61** remains ancestor. Original issue #121 OPEN despite patches in main, and physically verified wrong dot on OTHER RTX5070Ti WINDOWS before fix; **owner Linux not certified**. Exact main commit may be PROPOSED for user HIGH-controlled future smoke, never silently upgrade/test. **Initial gate still one GPU/one slot,32K, int8KV,spec1,no lossy expert routing, all CPU-double IQ3S/IQ2S MMQ/MMVQ + GDN/heads correctness, exact Codex/Copilot tool JSON and permissions, then speed ladder.** [Strata route-tail skip #5136](https://github.com/Niko1221/Strata/issues/5136) affects Strata conditional CUDA/HIP default, not proof Basalt does same; fidelity guard in all runtimes.



## November 3, 2026 00:37 EST — MAIN AFTER v0.2.0 contains material IQ3_S CUDA and agent fixes (supersedes earlier code-status notes)

[Strict latest research watch](./RESEARCH-WATCH-2026-11-03-0037.md), exact cutoff `2026-11-03T05:37:47Z`. **Model/owner first-PC choice unchanged: ONLY original official ISTA Qwen3.8 FlashNext GSQ-RCO IQ3_S pack in .basalt v2**, one Linux RTX5070Ti16 sm120/CoreUltra7 265F64GB host. Never Q2_0/IQ3XXS/NVFP4/third-party PLE for initial smoke or fallback. **NEW source-version distinction:** v0.2.0 is the pack FORMAT minimum, not equivalent to the current post-tag main. The previously OPEN critical defects were merged November 3 into **main at exact SHA `5bdb6c61ff99247899515c378856f49728e4a69b`** (last fix 05:35:36Z). For any user-controlled first trial *propose PINNING this specific commit*, not an old v0.2.0 tagged binary, if user elects current fixes; use official v2 IQ3_S pack. No build/download/CI/model run initiated by research.

**Merged source gates and what still needs physical owner validation:**
- **[same-card Windows original #121](https://github.com/jesdga95/basalt/issues/121)**: main [5bdb6c61](https://github.com/jesdga95/basalt/commit/5bdb6c61ff99247899515c378856f49728e4a69b) changes packed IQ3S/IQ2S register byte reads to explicit unsigned shift+mask in CUDA MMQ, MMVQ, decode-once. Original RTX5070Ti Win CPU-double wrong dot3412 vs5726 fixed locally; owner Linux exact build no test yet. Issue remains OPEN despite source code merge. Independent CPU-double per-tensor MMQ+MMVQ+Q6K head and no loops/NaNs REQUIRED before performance.
- **[#175](https://github.com/jesdga95/basalt/pull/175)/[#178](https://github.com/jesdga95/basalt/pull/178)** merged exact Q6K output-head above-column-bound rescoring at spec7/8 and skip unused prompt scoring. **#130** mid-chain persistent windowsT5–8 on RTX5070Ti under160SM gives normal-width-invariant logits (profiled/batch may still numerically differ). Keep **spec1** for earliest controlled reference and compare spec1/4/8 only after independent CPU reference; do not assume no errors in whole service.
- **[#208](https://github.com/jesdga95/basalt/pull/208)** union oneOf/anyOf/$defs tool-call props/decoding, **[#167](https://github.com/jesdga95/basalt/pull/167)** nested quoted inner tool tags in string arguments, now in main. Need real Codex/Copilot Zod variant discriminator and server/client allowlist+permission checks; merged schema exposes union of keys and can allow cross-variant mix. Record literal UTF8 JSON, all stream chunks, file contents exact and no unintended side effects.
- **[#176](https://github.com/jesdga95/basalt/pull/176)** final speculative-window commit stops at client-visible token; 2/8-token reply→new tool response and exact cached prefix, verify real session continuation and no stale speculative tokens. **[#177](https://github.com/jesdga95/basalt/pull/177)** CPU expert selection canonical cache tier prevents prompt numeric drift on resident/streamed KV.
- **Corrected test [#136](https://github.com/jesdga95/basalt/issues/136)** previous v2-vs-fused test compared v2 against itself; main now forces genuinely native comparison. Need actually run test and inspect nonzero expected differences, no false green.
- **Mixed CPU tensor AVX-VNNI BMI2 [#197/#199/#200]** merged on main, but owner Intel 265F speed not measured; do not enable lossy route flags/relaxed drafting or infer token improvement from microseconds.
- **[new #219](https://github.com/jesdga95/basalt/issues/219)** two 5060Ti peer tier Linux cold157K uncached prefill CUDA702/Xid8 watchdog, not single 5070Ti symptom; capture Xid on any hung long-context test instead of blaming memory. **new #220** explicit expert-profile path OPEN; model performance depends on exact learned profile and source tree; keep pinned profile metadata and avoid deleting build source before initial tests.

**Owner-controlled first staged gate**: read-only NVIDIA driver/CUDA Toolkit and system RAM/disk memory safety, pin main SHA/official pack file hash, one GPU0 / slot1 /32K configured /int8 KV /spec1, no alternate quant and no lossy flags; CPU-double and q6 head at short controlled prompts, Codex 15-tool Zod/literal quoted calls/new developer role, 2/8-token followup exact state; only then true physically occupied128/262K if RAM safe and full xhigh coding tasks with PP/TG/TTFT, p95 wall, cache-hit, SSD I/O and swap. No assistant-controlled commands, install or HIGH hardware permission.

## November 2, 2026 14:02 EST — first-PC original IQ3S-only and agent-continuity gates

[Strict current watch](./RESEARCH-WATCH-2026-11-02-1402.md); new hard cutoff **2026-11-02T19:02:00Z** (minute-level conservative). Owner FIRST remains Basalt0.2.0 **ONLY official GSQ-RCO IQ3_S version2 .basalt** on single RTX5070Ti16 Linux/CoreUltra7 265F64GB host. No Q2_0/IQ3XXS/NVFP4 or FP8 PLE alternate, even for smoke. One GPU0/slot, configured32K/int8KV/spec1 and default lossless routing. **Original IQ3S PLE IQ4NL remains unchanged**: Strata #5010 physical HIP FP8 acceptance+1.71pp only short, not long tasks, plus20.9GiB disk and no user-approved model change. **New open Basalt [#214](https://github.com/jesdga95/basalt/pull/214)** session-affinity headers bind agent identity to slot already holding KV to avoid previous 71K copy1.35sec; NO tests/A/B, and with initial parallel1 it yields no speed gain. Future multi-slot test needs authenticated session IDs, cache hit counters, no cross-agent state, per-agent p95 TTFT/complete actions. **Open #215** exposes hit_pct/hits/lookups on -o json from existing engine decode logs; no kernel/throughput gain, avoid projecting RTX5090 NVFP4 results onto IQ3S owner. **Open #213** exclusive prompt read on FOUR GPU layer split prevents expert-loan thrash (unmatched throughput, no tests) and should NOT modify single-5070Ti initial plan. **First-PC hard correctness** still OPEN #208 union Codex schema args {}, #175 Q6K high-spec vhead wrong argmax and #176 speculative client boundary, plus #121 Windows same-card optimized IQ tensor math not proven Linux. Read-only system/VRAM/CPU/SSD safety inventory and explicit CPU-double MMQ/MMVQ and output-head, exact tool args and 2/8-token continuation before any speed or 3–5 agent work. Strata #5020 other GPU/quant doubled expert host arena and host OOM is a warning to inspect actual resident bytes and OS pressure, not a proven Basalt bug. oMLX #5045 silent stream abort after QFN pressure demands explicit terminal error/cancel/timeout on user agent clients; not a known Basalt reproduction. No owner model commands, installs, CI/auto work or HIGH approval initiated.

## November 2 2026 10:02 EST — first-PC IQ3S-only gates unchanged, new numerical reproducibility warning

[Strict dated watch](./RESEARCH-WATCH-2026-11-02-1002.md); **new hard cutoff 2026-11-02T15:02:32Z**. **ONLY official GSQ-RCO IQ3_S .basalt v2 on Basalt0.2.0 and one Linux RTX5070Ti16/64GB host**, even for smoke; never Q2_0/IQ3XXS/NVFP4/third-party PLE fallback. First-start one GPU/slot, max-context32K, int8 KV/spec1, lossy routing disabled, logs and free RAM checked. **Current unresolved source correctness:** [#208](https://github.com/jesdga95/basalt/pull/208) Codex discriminated-union oneOf/anyOf tools can get literal {} params; [#175](https://github.com/jesdga95/basalt/pull/175) Q6_K vhead spec7/8 wrong argmax; [#176](https://github.com/jesdga95/basalt/pull/176) last speculative window commits extra undelivered tokens and breaks next-turn prefix reuse. Earlier Windows same RTX5070Ti [#121](https://github.com/jesdga95/basalt/issues/121) IQ3S/IQ2S CUDA dot wrong, not shown on owner's Linux. Require independent CPU-double mixed-format tensor parity, head ref, Codex exact tool+roles+argument bytes, and two/8-token continuation before full xhigh test. **UPDATED OLD [#157](https://github.com/jesdga95/basalt/pull/157)** prepared GEMM on RTX5080 IQ3S is neutral to 16K/64K prefill but two fresh same-build engine starts still differ numerically; draft explicitly not merge-ready, do not cherry-pick. **UPDATED OLD [#201](https://github.com/jesdga95/basalt/pull/201)** pinned home allocation page roundup undercount means 64GB host admission could be inaccurate, CLOSED without merge; do not enable it. New oMLX #5033 distributed MLX oQ5 model on heterogeneous Macs and TensorFold partial GGUF infrastructure are **separate from user PC setup**. No device/CI/model run or HIGH approval granted.

## November 2, 2026 01:03 EST — Codex tool contract tests BEFORE first real agent (supersedes old examples)

[New strict research watch](./RESEARCH-WATCH-2026-11-02-0103.md); **next strict cutoff 2026-11-02T06:03:46Z**. First-PC runtime decision **unchanged**: upstream Basalt v0.2.0, one RTX5070Ti sm120 CUDA13 Linux, **ONLY official original GSQ-RCO IQ3_S v2 .basalt pack** for initial smoke/coding/long-context; no Q2_0, IQ3XXS, NVFP4, modified PLE or alternate model fallback. No machine actions performed by this documentation. Start user-owned testing with one GPU0, one slot, config max-context32768/int8 KV/spec1/expert-cache auto/prefill auto; lossy route-prior/route-tail-skip/relaxed drafting all OFF. Freeze exact engine build/model section SHA, verify actual GPU/host RAM+SSDs and matching pack v2, do NOT assume correctness solely from fluent code.

**NEW CRITICAL Codex contract:** [Basalt #208](https://github.com/jesdga95/basalt/pull/208) OPEN demonstrates `oneOf`/`anyOf` Zod-discriminated tool schemas with $defs/$ref cause lost argument object `{}` 4/4 on physical source IQ3S two RTX5070; branch 4/4 correct typed keys but combined with two local Codex changes. Validate tool names, oneOf variant/discriminator, type/required fields, JSON streaming, exact UTF8 argument bytes and **server + client authorization before any tool action**. Fix merges not verified at cutoff, don't copy unreviewed PR as safe. [Basalt #152](https://github.com/jesdga95/basalt/issues/152) Codex /v1/responses JSON title and full tools request gave400, late developer messages mapped as user; new **main [2c88993](https://github.com/jesdga95/basalt/commit/2c8899327e79) and [a04edb9](https://github.com/jesdga95/basalt/commit/a04edb960cf3)** at Nov2 02:28Z address those roles/format cases; test title request and role ordering against exactly pinned build. For coding agents check 2/8 token reply→next turn reused state, two parallel out-of-order tool results, literal angle-tag snippets never executed, nontrivial tool messages not truncated, optional/required/named tool_choice and refusal semantics; never claim a provider supports a mode unless separately shown.

**Numerical and operating gates still before performance:** older Basalt #121 physical 5070Ti Windows optimized IQ3S/IQ2S dot may be wrong (Linux user not confirmed), IQ3S Q6K head #175 OPEN wrong argmax at spec7/8, so first spec1 and independent CPU-double MMQ+MMVQ/K-quant/head parity. Do not enable speculative widths until correct. Record complete xhigh coding task quality, true occupied prompt size, cold vs warm PP, TG/TTFT, swap, RAM/VRAM/SSD I/O and repeated turns. If no fit or errors, STOP and diagnose IQ3S. New Strata #4963 same RTX5070Ti uses **wrong whole-model NVFP4 pack and128GB host**, so do not substitute or project its measured87–111tok/s to Basalt. ALL future model tests physically user-operated or require explicit human HIGH gate.

## November 1 2026 — Basalt 0.2.0 mandatory first-run correction (supersedes older instructions below)

**Latest strict cutoff 2026-11-01T21:15:58Z**, [verified dated watch](./RESEARCH-WATCH-2026-11-01-1615.md). **ONLY official Qwen3.8-FN-GSQ-RCO-IQ3_S.basalt pack** for first startup, semantic smoke, quality and deployment; never Q2_0, IQ3_XXS, NVFP4 or a changed-PLE third-party pack, even if startup or speed fails. The original October31 user override remains authoritative. Older instructions/exemplar model paths lower in this runbook which mention Q2_0 are HISTORICAL and not to be executed. User controls any actual machine commands; this is research/documentation, not approval to run anything.

**Version compatibility:** [Basalt 0.2.0](https://github.com/jesdga95/basalt/blob/main/docs/changelog/0.2.0.md) only reads **.basalt v2** and refuses v1. Match a pinned source build to an official v2 GSQ-RCO IQ3_S pack from [Basalt HF](https://huggingface.co/jesdga/Qwen3.8-Flash-Next-Basalt). If a full IQ3S v1 pack was already downloaded, [upstream migration](https://github.com/jesdga95/basalt/blob/main/tools/migrations/README.md) uses the command `python3 tools/migrations/basalt_v1_to_v2.py OLD-IQ3_S.basalt NEW-IQ3_S.v2.basalt` (Python3.10+, numpy), preserves every original weight section, creates a second large file and requires free disk for that copy. Do NOT interpret pack-header version mismatch as GPU tensor corruption. v2 moves expert profile into engine data/profiles and includes hc8 in pack; old converter --profile and --hc8 options removed. Pin engine git tag/SHA and pack identity before testing.

**Single GPU0, one slot, example config's model path must be** `models/Qwen3.8-FN-GSQ-RCO-IQ3_S.basalt`, max-context32768/int8 KV/spec1/expert-cache auto/prefill auto, no cross-vendor peer or multiple slots. Exact flags read from 0.2.0 config docs. **No lossy options:** keep --route-prior, --route-tail-skip and --relaxed-drafting DISABLED. Author source-IQ3S benchmark with route-prior1.5+tail-skip7 reduced top1 from87.27 to84.33%, increased KLD.1551→.244 and worsened measured prose decode341→314tok/s on different 2-GPU machine. Thinking-loop safeguards do not make an incorrect model correct. **Still OPEN [#175](https://github.com/jesdga95/basalt/pull/175)** source IQ3S Q6_K head candidate overflow at spec7/8, not resolved by release's Q8_0 head feature; no high-spec test until fix parity. Current release main includes aligned pinned O_DIRECT startup fix [5aa4b15](https://github.com/jesdga95/basalt/commit/5aa4b15be379ea), so old #179 error should be retested on exact build rather than assumed.

**First quality gates:** run independent CPU-double MMQ/MMVQ mixed IQ3_S/IQ2_S (plus IQ4NL and Q2_0 *tensor types* inside IQ3_S; NOT the disallowed whole Q2_0 pack), Q6_K exact head spec1/4/7/8 reference with pinned expert placement, complete semantic/code response and tool-call JSON bytes, 2/8-token reply→next turn cache/token boundary. [#176](https://github.com/jesdga95/basalt/pull/176) still-open continuation repair has new physical source 5080 evidence and large TTFT improvement on a combined patch stack, not current main. CPU BMI2/VNNI IQ3_S-focused [#197](https://github.com/jesdga95/basalt/pull/197), [#199](https://github.com/jesdga95/basalt/pull/199), [#200](https://github.com/jesdga95/basalt/pull/200) OPEN/no full model speed. Do not chase speed before fidelity. Only after clean one-slot 32K setup, consider authorized true physically occupied 4K/16K/32K→128K/262K and 1/2/4 agents, with cold PP, warm PP, decode TG, TTFT, total wall, model/output hashes, free host/VRAM/swap/SSD and complete correct xhigh tool tasks; no fake 262K based on configured context.

## AUTHORITATIVE USER CHOICE — October 31, 2026, 22:53:39 UTC

**ONLY GSQ-RCO IQ3_S on the Linux RTX 5070 Ti PC.** Basalt's `Qwen3.8-FN-GSQ-RCO-IQ3_S.basalt` (~86.9GB download) is the **first startup, semantic smoke, quality baseline and intended long-context deployment**. Do **not** select IQ3_XXS, Q2_0 or NVFP4 as a functional smoke or fallback. Historical performance and size references below remain useful for research comparisons, not deployment alternatives. If the actual working set, CPU/CUDA numeric math or user experience doesn't meet requirements, STOP and investigate memory tiers, SSD-mapped PLE, draft and expert pool rather than silently decreasing quant precision. Use one GPU0, one slot, initial32K context, int8 KV, conservative spec1. No model run or test result is claimed by this update. **Research freshness cutoff stays 2026-10-31T22:12:24Z**; this is a decision correction, not a new scan.

**Decision:** On October 31, 2026, the user chose to **try Basalt on the Linux PC first**, while retaining the two 64GB M1 Max Macs as the separate distributed Metal/quality research lane. **Documentation and user-executable instructions only; nothing installed, downloaded, run or tested by ChatGPT.** Any assistant-controlled hardware/model/CI experiment remains blocked by the Project 51 **HIGH** human-approval process. Last direct-source research cutoff **2026-10-31T18:08:01Z**, [dated strict watch](./RESEARCH-WATCH-2026-10-31-1408.md).

## Owner hardware, goals, important difference from Basalt's README example

**PC:** Linux x86-64, Intel Core Ultra7 265F, **RTX 5070 Ti 16GB Blackwell sm120**, 64GB DDR5, 2TB NVMe. Other machine RX6800 16GB gfx1030 and ONLY16GB host RAM must NOT be passed to Basalt as if it were a second CUDA Blackwell GPU; `"gpu":"0,1"` in Basalt's README is an example for two supported NVIDIA GPUs. Basalt [README](https://github.com/jesdga95/basalt/blob/main/README.md) and [platforms](https://github.com/jesdga95/basalt/blob/main/docs/platforms.md) explicitly support Linux+sm120+CUDA13, not this exact particular owner build tested. **Use GPU0 alone.**

Primary first-PC objective: **trusted working local API + successful xhigh-like long coding/tool tasks**, with exact model/quant/provenance, correct output, safe memory and repeatable throughput; performance optimization comes after numerical parity. Mac original IQ3_S 128/262K long-context targets remain separate and UNMEASURED.

### Official preconverted Basalt packs — only IQ3_S is selected; other rows are historical reference

Existing (not new Oct31 releases) official [Basalt HF pack tree](https://huggingface.co/jesdga/Qwen3.8-Flash-Next-Basalt/tree/a229744b82e18c3e12057ab944062c0c713c7006) and [source ISTA GGUF card](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF), sizes in decimal GB:

| Pack | Basalt file download | Original GGUF transformer + separate ngram | Intended first-PC role |
|---|---:|---:|---|
| **Qwen3.8-FN-GSQ-RCO-Q2_0.basalt** | **69.7GB** | 37.6GB +28.8GB SSD-map | Rejected by user, even as initial smoke |
| **Qwen3.8-FN-GSQ-RCO-IQ3_XXS.basalt** | **79.9GB** | 47.0GB +28.8GB SSD-map | Rejected by user, not a fallback |
| **Qwen3.8-FN-GSQ-RCO-IQ3_S.basalt** | **86.9GB** | 54.8GB +28.8GB SSD-map | Sole PC target including first smoke; tight memory headroom and Q6_K head width7–8 bug #175 |
| **Qwen3.8-FN-NVFP4.basalt** | **131GB** | Different NVIDIA source; ~122GiB Basalt pack | Rejected by user, not a fallback |

The .basalt pack is ONE self-contained model file including tokenizer, draft, expert profile, optional vision. Source shards are not directly usable as .basalt without the converter; an independent convert without published drafter/profile may be slower. A **69.7–86.9GB file does NOT imply 69.7–86.9GB fully resident RAM**: ngram lookup is file-backed and experts move across tiers. It DOES require disk download space and sufficient verified system free RAM + VRAM for the resident expert plan. Do not count 64+16GB as 80GB freely available (OS/graphics, pinned memory, KV, draft, page cache, transient buffers). Q2_0 is easiest to fit, IQ3_XXS is first serious quality run, IQ3_S is a second-stage option.

## Basalt-first, user-controlled finite sequence

### A. Read-only inventory, pin sources, no runs behind the scenes

On the owner's PC before downloading any model, capture:
```sh
nvidia-smi
nvcc --version
free -h
df -h
uname -a
```
Check Linux x86-64, CUDA13 compiler toolkit actually installed, NVIDIA driver compatible with toolkit, single sm120 5070Ti, RAM/swap and SSD free. Record exact Basalt Git SHA, model filename, source hash/pack's section SHA and main branch status, environment variables, and thermal/power conditions. Use the source's `docs/configuration/index.md`, `docs/running.md`, `docs/probe.md`. Basalt may support local CUDA13 even if `nvcc` isn't yet installed; this check doesn't authorize installing it. **Do not enable second GPU; do not use Windows-only flags.**

### B. Owner executes the plain upstream README build only when ready

Documented [README](https://github.com/jesdga95/basalt/blob/main/README.md) build shape (run it yourself, not executed in this research watch):
```sh
git clone https://github.com/jesdga95/basalt
cd basalt
git rev-parse HEAD
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build -j 8
ctest --test-dir build -L cpu --output-on-failure
```
If exact platform/toolchain dependencies fail, capture CMake/compiler logs; don't silently switch forks, apply unreviewed patches, suppress failed tests or declare a model run passed. Git default-branch HEAD is moving quickly, so freeze SHA after build before comparing speed to another version.

### C. Download ONLY IQ3_S after user initiates the manual setup

```sh
hf download jesdga/Qwen3.8-Flash-Next-Basalt Qwen3.8-FN-GSQ-RCO-IQ3_S.basalt --local-dir models
```
No lower-precision alternative. Check free disk and pack/section hashes, and validate IQ3_S/IQ2_S mixed submatrices plus Q6_K output head numerical parity. On failure, diagnose or stop rather than downgrading.

### D. Single GPU, single slot, conservative context/verification settings

Suggested **starter example**, NOT a claim these settings have already passed on the user's PC:
```json
{
  "server": {
    "model": "models/Qwen3.8-FN-GSQ-RCO-IQ3_S.basalt",
    "gpu": "0",
    "port": 8080,
    "parallel": 1
  },
  "engine": {
    "max-context": 32768,
    "kv": "int8",
    "spec": 1,
    "expert-cache": "auto",
    "prefill": "auto"
  }
}
```
Store as `basalt_config.json` in repository root, model path relative to file. Start manually `bin/basalt serve --config basalt_config.json`. A configured `--spec 1` is conservative verification width, **not proof all drafting is disabled**; test an explicitly documented no-draft control before using the term MTP-off in comparisons. Basalt may still choose an automatic resident expert arena according to free RAM; observe startup logs. Initial sanity is **32K configured context / one slot**, not actual occupied32K. `GET /health`, `GET /v1/models` reveal loaded model/alias; all API requests must name actual served model. Avoid external network bind or unreviewed cloud frontends at first (localhost by default). Avoid high MTP (7/8), 262K reserved KV, parallel>1, peer GPU and vision until earlier gates pass.

### E. First-run stop conditions: DO NOT chase fast nonsense

| Failure/symptom | Source and response |
|---|---|
| **`DirectFile: unaligned request`, profile fill fails on startup** | [Basalt #179](https://github.com/jesdga95/basalt/pull/179) FRESH OPEN; host pinned stage alignment under O_DIRECT, proposed aligned interior+mapped fallback; pack can be fine. Record SHA/driver/offset; wait for approved upstream fix rather than randomly altering filesystem. |
| **IQ3_S incoherent or endless reasoning, mixed IQ CPU-double wrong** | [#121](https://github.com/jesdga95/basalt/issues/121) OPEN Windows5070Ti optimized IQ3S/IQ2S byte alias corruption; Linux not demonstrated. Check MMQ+MMVQ independent parity, not only speed or token endpoint. |
| **IQ3_S spec7/8 first token changes / flat head row** | [#175](https://github.com/jesdga95/basalt/pull/175) FRESH OPEN Q6_K head 65,536-candidate shared cap, approximate argmax wrong vs exact. Test spec1 before higher widths; #178 depends on #175. |
| **Short live chat continuation rereads older checkpoint** | [#176](https://github.com/jesdga95/basalt/pull/176) FRESH OPEN drafted rows beyond actually emitted final token wrongly committed; 12/36 fallback vs proposed0/36, check `reused/read` logs. |
| **GPU illegal instruction/Xid, nvidia-smi unresponsive** | [#161](https://github.com/jesdga95/basalt/issues/161) OPEN RTX5060 Linux Swift1.5 under different flags. Stop load, inspect logs and NVIDIA Xid, do not torture GPU unattended. Not evidence owner5070Ti reproduces. |
| **File-write truncation, unknown namespace tool, abnormal tool order** | [#166](https://github.com/jesdga95/basalt/pull/166), [#167](https://github.com/jesdga95/basalt/pull/167) OPEN, merged [#168](https://github.com/jesdga95/basalt/pull/168). Require exact bytes, schema, call ID, finish reason. |
| **Token0 loop with suspicious ~100% draft acceptance** | Older [#139](https://github.com/jesdga95/basalt/issues/139) dual5070Ti closed Oct30 WITHOUT long-soak retest receipt. Different hardware, still fail integrity gate. |

### F. Minimal acceptance battery; full quality follows baseline

- **First fresh process, one-model**: three semantic canaries (simple factual, tiny coding generation, structured JSON/tool request), 256–400 output tokens that end with natural stop and no nonsense loop; log required exact model id, full prompt, response tokens, token counts and finish reasons. Verify byte-precise tool arguments including literal `<tool_call>` examples and multi-call IDs.
- **Reference parity** for actual quant mix: IQ3_S, IQ2_S and every relevant output/head quant used, Q6_K vhead candidate edge; compare CPU double/FP32 for prefill (MMQ), decode (MMVQ), speculative T1/4/8 under fixed expert placement and with/without draft. Fail on NaNs, invalid reference dumps, skipped parity test cases. Running built-in CTest is necessary but not sufficient.
- **Physical prompt/coding tasks**: exact new cold 4K/16K/32K prompt content, 512+ completion budget, meaningful coding+tool outputs, no only 512-token truncated reasoning disguised as success, record sustained TG, *truly cold* PP, TTFT, peak GPU+CPU+swap, resident/expert cache and SSD reads. First run only spec1; compare higher width only after #175 merged/independently verified.
- **Long/parked** (later human-approved stage): true occupied40K→128K→262K only if per-slot KV and free RAM permit; chat turns with 2/8 token replies followed by next tool message; check exact reused tokens and no speculative overcommit, question repeated after eviction/restore, 1/2/4 active with fair scheduling and independently correct semantic results. Default `--parallel N` divides `--max-context` by N; do not accidentally call 4 agents each 262K with total262K configured.
- **Optional Basalt probe only after clean startup**: documented `bin/basalt-probe --model models/Qwen3.8-FN-GSQ-RCO-IQ3_S.basalt -- --kv int8 --spec 1`, measures **cold** conv/struct/prose 400-token decode plus copy/CPU tiers; suggested values are just text and do not edit engine config. It is NOT a deep 128K/262K benchmark or xhigh evaluation.
- Preserve reproducible reference manifests with SHA, engine build and git branch, memory, OS/driver/CUDA, profile and flags, actual occupied per-run context, raw response/tool traces, parity outcomes and negative startup arms. One knob at a time, fixed reference source, no changing source model/quant between labeled A/B.

## New source evidence and research promotion state

**FRESH MERGED #125** Oct31 17:37Z grids elastic KV memory extents, now can return expert cache slots after a deep131K→medium40K request (RTX5080 +644 slots over main). +6.07% micro-measurement depended on separate #117+8192 floor; NOT a generic merged speedup. **FRESH MERGED #168** ordered tool results by call ID and **#169** single-token position0 generation fix, quality-only. **FRESH MERGED #173** Windows file-cache PLE fix not relevant to Linux performance; **FRESH OPEN #174** warm dense verify microkernels 2.2–2.7× but no end-to-end speed; **FRESH OPEN #175/#176/#177/#178/#179** above.

**Research statuses:** Basalt first-PC runbook now prioritized, **but no actual user physical runs initiated or results claimed**. Original M1 source IQ3S real128K/262K and3–5 agents goals remain unchanged; one day may compare Basalt source to distributed Macs on frozen evals, keeping operating-system quant and PLE differences honest. No spontaneous background monitoring, purchases or autonomous model execution.

**Last strict cutoff:** 2026-10-31T18:08:01Z.


## Halloween 2026 18:12 EDT — newly verified Basalt enhancements and safe follow-ups

[Full strict watch](./RESEARCH-WATCH-2026-10-31-1812.md), cutoff **2026-10-31T22:12:24Z**. Research/plan only; user remains in charge of installing/running on PC; all model/CI/hardware actions by assistant require explicit HIGH.

**[OPEN #182](https://github.com/jesdga95/basalt/pull/182)** Intel ArrowLake AVX-VNNI-INT8 optimization applies to **NVFP4 CPU-tier expert rows**, NOT the default user's GSQ IQ3XXS or IQ3S expert row format. Intel Ultra9 285K+RTX5090 source NVFP4 whole decode improved +5.6–7.5% while 16K PP +0.5% with 1024 identical tokens. User CoreUltra7 265F is same generation but instructions/actual clocks/host RAM pressure must be independently checked if NVFP4 becomes feasible. **Do NOT download the huge 131GB NVFP4 pack merely because this PR is new**; 16GB VRAM and64GB RAM remain first-run limits.

**[OPEN #183](https://github.com/jesdga95/basalt/pull/183)** BF16 PLE table vs Q8_0 and optional RAM quantization is a **separate** question. BF16 table of original family is ~95.4GB and not 64GB-host-resident. Primitive-ai's old 200-task tool-call comparison BF16 79.2 vs NVFP4 78.7/INT4 78.2 is small and may not transfer to owner's xhigh coding tasks. On RTX PRO6000 Windows BF16 structured/prose/16K PP faster, Q8 conversation faster; PLE format should be an independent frozen-eval switch after basic numerical certification, with SSD page-cache/cold TTFT tracked.

**[OPEN #184](https://github.com/jesdga95/basalt/pull/184)** overlay fine-tune adapters avoid duplicate multi-GB checkpoint copies, but switching the loaded variant **flushes all live/prefix/parked states**, so a coding agent must capture/acknowledge tool results before any adapter switch. Cannot serve several adapter variants concurrently yet.

**[MERGED #180](https://github.com/jesdga95/basalt/pull/180)** two RTX5060Ti16 community benchmark uses 128GB host, custom BF16PLE fork and +2500MHz VRAM overclock; cannot predict **single owner 5070Ti** speed. [Open #175](https://github.com/jesdga95/basalt/pull/175) speculative high-width Q6 head overflow, [#179](https://github.com/jesdga95/basalt/pull/179) direct-I/O alignment abort, [#176](https://github.com/jesdga95/basalt/pull/176) short-reply checkpoint overcommit and [#121](https://github.com/jesdga95/basalt/issues/121) Windows same-card low-bit numerical parity remain correctness gates. Starter **one GPU0, 1 slot, 32K context, spec1, IQ3_S only**. Earlier Q2/XXS recommendations are superseded.

**New agent-tool correctness canary:** [oMLX #4999](https://github.com/jundot/omlx/issues/4999) shows Claude Code returns parallel Read/Grep results in completion order with correct IDs but Qwen template reassigns values by position. Basalt merged call-ID sorting #168 already; confirm with synthetic parallel 2/3 tool results reversed, each file value must be attributed to its named call even under streaming. Assert no phantom file operations, incorrect path or hidden tool error. This is a reusable low-risk parser-only test, not a GPU benchmark.

No first-run commands executed by assistant, no model files installed, and no automatic monitoring initiated.
