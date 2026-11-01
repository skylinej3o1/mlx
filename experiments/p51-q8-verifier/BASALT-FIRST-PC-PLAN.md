# Project 51 — Basalt-first RTX 5070 Ti PC plan

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
