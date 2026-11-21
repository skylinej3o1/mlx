# Project 51 strict research watch — Nov 20, 2026, 22:36 EST

**STRICT DELTA:** from prior verified `2026-11-20T21:56:17Z` (Nov20 16:56:17 EST) through this request `2026-11-21T03:36:49Z` (Nov20 22:36:49 EST). Independently confirmed source branch HEAD `465daa8d2bef35ffa882c7fee7f0520ddffff0ad` at research start. Timezone America/New_York, UTC dates Nov20–21. Primary sources GitHub API issue/PR bodies, comments with timestamps, release tags, official Chinese Qianwen changelog and official Qwen Hugging Face. Some GitHub issue/PR bodies are mutable, so comments/created timestamps and source revisions are distinguished. **FRESH** created/published in window; **UPDATED OLD** dated substantive new evidence on older item; **REDISCOVERED** prior evidence newly located, not a fresh event; **ANALOGUE** model/quant/rig/runtime differs. No user hardware runs, software installs, code, CI, model downloads/quantization, config changes or deployment; documentation only.

## 1. Top priority: actual agent correctness regression cluster (fresh Nov21 01:52Z)

### FRESH [Strata #6461](https://github.com/Niko1221/Strata/issues/6461), created **2026-11-21T01:52:35Z** — declared Playwright MCP function argument silently dropped

On other **RTX4090 24GB, Ubuntu, host128GB**, QFN original GSQ IQ3_S, Claude Code2.1.328, Playwright MCP0.0.86: tool argument literally named `function` is silently discarded by Strata `serve/frontend.py` `NOT_PARAMS=("function","think","parameter")` even where tool's declared schema requires a `function` JS string (e.g. `browser_evaluate`). Reporter **0/29 working** calls; raw parser shows `{}` or empty `function`. Proposes schema-aware `param_name(...,declared)` across streaming and non-stream parse paths; reproducer returns expected `() => document.title` after patch, live Playwright worked. **Still OPEN ISSUE with supplied patch, not verified merged release**. Highly direct HaikuSwarm failure: correctly sampled tool output can be mutilated by server. New evaluation requirement exact tool schema key retention, no HTML/JS/file side effect executed unless actual API args valid.

### FRESH [Strata #6463](https://github.com/Niko1221/Strata/issues/6463), created **2026-11-21T01:52:38Z** — tiny side requests evict primary long agent cache

Same reporter RTX4090 host128, GSQ IQ3_S, 262K DFlash2. Claude Code sends **80–190-token** titles/classifications between major coding-agent turns; four parked conversation slots with no size floor admit these tiny sessions and evict the valuable 18K–34K main agent prefix, forcing new prefill. Reporter attributes **~29% task wall time to prompt read**. Their alternative `--conversation-cache-min-tokens 2048 --conversation-cache-slots 8 --conversation-cache-mib 16384` kept main agent cached: next line `prompt 12395 = 12280 reused + 115 read`. **This is one other 128GB host report, not a benchmark on owner's 64GB PC or either M1 and NOT a mandate to adopt sizes**. Molt/orchestrator must partition cache importance by primary agent vs helper traffic.

### FRESH [Strata #6460](https://github.com/Niko1221/Strata/issues/6460), created **2026-11-21T01:52:33Z** — Claude Code compaction empty response at 250K

Under Claude Code2.1.328 `/v1/messages` with QFN GSQ IQ3S + DFlash2 262K, an automatic compaction near ~250K failed `summarization produced empty response` and later `Prompt is too long`, ending ~56min task. Cause reported: default `anthropic_thinking` continues reasoning on supposedly no-thinking summary request, burning available answer budget. Setting `anthropic_thinking:"on_request"` (plus `reasoning_close_retry:true`) gave manual compact **130K→4.9K in24s** and automatic **257K→14K in43s** with later recall preserved. **No rigorous paired 257K default retest**, reporter's successful condition not owner source inference proof. HaikuSwarm Molt should test summary text non-empty and valid handoff with complete work artifacts, not rely on model stop alone.

### FRESH [Strata #6459](https://github.com/Niko1221/Strata/issues/6459), created **2026-11-21T01:52:31Z** — Codex CLI remote compaction unsupported

Codex CLI0.171.0 `/v1/responses` sends `input.type="compaction_trigger"` around200K and Strata responds **HTTP400**, ending ~1h tool task. Reporter marks provider `[model_providers.strata.capabilities] remote_compaction="unsupported"`, invoking local compaction instead. Forced 15K compaction succeeded and complete rerun of Terminal-Bench `make-mips-interpreter` passed **3/3 checks in64.5min**. Other RTX4090 host GSQ IQ3S 262K not user devices. Separate API behavior vs above Claude Code model-thinking mismatch.

### UPDATED OLD [Strata #5225](https://github.com/Niko1221/Strata/issues/5225), updated **2026-11-21T01:46:46Z**, not a new issue

RX Radeon AI PRO R9700 32GB, source GSQ IQ3S128K: cache-hot repeated tool calls sometimes emit enum/schema text pasted into JSON arguments (~6% scripted at T0). Reporter says setting `STRATA_ROUTE_TAIL_SKIP=0` yielded 0/32 copied schema failures vs1 hard and1 whitespace corruption in first17; **not** causal isolation nor enough samples to guarantee clean. Prior v0.2.17 tail route skip DEFAULT OFF already recorded, so do not enable for speed. Distinguish returned valid JSON from correct semantics.

## 2. UPDATED OLD Basalt cache state, long QSA, and first PC

### UPDATED OLD [Basalt #382](https://github.com/jesdga95/basalt/pull/382) updated **2026-11-21T02:09:27Z** — rebase with long-sessions measurements; OPEN

Previously known #382 direct disk K/V streaming, now body cites new rebased main `8ba264c0` versus PR `6ee2e881` and exact long conversation A/B. Different **dual RTX5080+RTX5070Ti expert peer, PCIe4x4, Linux, 64GB host** with **Unsloth UD-IQ3_XXS** model, NOT user's single 5070Ti original ISTA GSQ IQ3S Basalt v2 configuration. 8 conversations physically **109–121K**, 4 slots, saved to disk/host, 16 continuing turns. With 20s idle between loads: **10/16→16/16** cache continuations, 2 full rereads→0, refusals4→0, **14.1→11.3min wall (−19.9%)**. Under continually busy fifth chat: **11/16→16/16**, 5 full rereads(60–97s)→0, **18.5→11.3min (−38.9%)**; some restored cached TTFT grew to4.63s vs main1.3, so gains are from avoiding reruns/refusal, NOT faster per-token inference. Direct stream host source writes ~0.5–0.6s, file K/V read setup21–72ms. Same placement short base vs PR PP5238→5211tok/s (−0.5%), TG conversation241.2→240.2, structure160.7→161.3, prose214.3→214.0, greedy token identity 900 tokens. Under RAM guard a declined conversation put back and can resume instead of cold read100K ~40.2s. Tests6/6 conversation,84/84 CPU, 91/91 all-model CPU. Known caveat source disk writes synchronous, incomplete failed streamed read can cold-prefill, one rare no-progress watchdog stall reported, expert eviction tier bug exists in main. Single A/B run; unmerged. Direct benefit to future multiagent cache survivability, not owner's frozen first 32K single-slot test.

### UPDATED OLD [Basalt #445](https://github.com/jesdga95/basalt/pull/445), dated **2026-11-21T01:17:36Z** author comment

Two-pass QSA 3xTF32 rescoring threshold, prior-created PR. New **232,031 physical-token** prefill with original-ish mixed IQ3S-Q4 pack, KV INT8: **2×RTX5080** 32.83→31.67s (PP7068→7328, **+3.7%**) and **RTX5090D** 26.36→25.19s (PP8802→9209, **+4.6%**), A/B/B/A and **0 selected ID differences across2,000,928 queries** in each. A checker-specific dual-layer-split bug shared static reference pointers was repaired locally; not normal algorithm bug and checkpoint only in PR thread. For 32K no benefit and threshold64K; owner first Basalt **physical32K** run unchanged. Not user RTX5070Ti single GPU and no full task output comparison in this new comment.

### FRESH [Strata #6462](https://github.com/Niko1221/Strata/issues/6462) 2026-11-21T01:52:36Z — other NVIDIA agent followup optimization analogue

One RTX4090+Core i9-14900K+128DDR5 QFN GSQ IQ3S or UD packs: on **UD-Q4KXL** 3K followup TTFT **3.31→2.44s (−26%)** raising CPU prompt share; on **source IQ3S** same from **2.00→1.86s (−7%)**. Also bit-exact +6% short decode on UD-Q4KXL from sm86 kernel flags, user rig RTX5070Ti sm120 different. Enabling `STRATA_ROUTE_TAIL_SKIP=7` produced faster source IQ3S real-sampling TG109→125 but quant-to-UDQ4 reference drift KL0.290→0.301; **do not compromise quality**. Data not from Basalt source IQ3S first test; do not adopt changes.

### UPDATED OLD [Strata #5751](https://github.com/Niko1221/Strata/issues/5751) comment **2026-11-21T02:28:33Z** — external RTX5070Ti hard-reboot caution

Different Windows machine with **RTX5070Ti16, Ryzen5900X,32GB host**, older Strata CUDA engine versions: reporter's official Strata0.1.63 CUDA build at250W cap **rebooted before READY** with default window warm, whereas `STRATA_WINDOW_WARM=0` at300W got to READY and QUIT with **NO inference**; source diagnostic no clear root cause. Not owner's Linux Basalt, not proof 5070Ti hardware unsafe or a workaround validated for production. Reinforces no automatic risky tuning / owner run without HIGH.

### NEW [Strata #6458](https://github.com/Niko1221/Strata/pull/6458) created **2026-11-21T01:34:40Z** — Linux Nvidia Spark pageable mmap issue

On HP RTX Spark N1X120GB unified with NVFP4-QAD *not user hardware*, mapped experts upload degraded31MB/s and cold startup ~42min, batched prefill watchdog stalled. Proposed opt-in `STRATA_FILL_STAGED=1` through pinned bounce buffers lowered profile fill from2184s to44–48s, whole start58–73s, 16K–128K prompts completed; **not validated DGX Spark, PCIe discrete5070Ti, Mac, RX6800 or original GSQ**. CUDA Linux only. Interesting pinned memory transfer mechanism but no promise to user's GPUs.

## 3. FRESH real old M1 Max resource correctness, NOT accepted-quant long speed

### [Strata #6446](https://github.com/Niko1221/Strata/pull/6446), created **2026-11-20T22:49:07Z**, OPEN

Author actual **M1 Max32GPU64GB**, original GSQ Q2_0+PLE streaming. Four reader teardown cycles in main leaked one file descriptor and fallback mapped scratch allocation each; patched code closes descriptors and wraps Metal scratch lifecycle correctly; GPU `MTLDevice.currentAllocatedSize` 17,235,968→458,752 bytes each of four teardown cycles, where main resource retained. Full 192-ID prompt and 128 IDs generated equivalent on 1GB/12GB expert arenas, MTP72/114; two linked serve turns completed. **No 128/259K IQ3XXS performance gain claim**, fixes process/resource leaks after unload/replace.

### [Strata #6447](https://github.com/Niko1221/Strata/pull/6447), created **2026-11-20T22:57:01Z**, OPEN

On actual M1Max32GPU64 source GSQ Q2_0+PLE streaming context cap16,384, host rejected `--batch 1` but Metal allocated state for nonexistent extra slot. Process engine Metal allocation at startup **5.00GB→4.65GB** on rejected batch, same4.65GB as no batch after fix, saving **0.35GB only on that invalid batch setting**. Matching first logits, 128 tokens, MTP63/64 and no swap; valid `--batch 2` still admitted two slots. Does **not** imply M1 IQ3XXS at259K automatically saves350MB or decoding improves.

### UPDATED OLD Paperniuk/other M1 targets

[Paperniuk Splash #72](https://github.com/paperniuk/splash/pull/72), [#73](https://github.com/paperniuk/splash/pull/73) remain open with **no substantively timestamped new source** this 5h40 window. #72 explicitly excluded IQ3_XXS/S for speed regression; #73 M2Max Q2_0 cached short append Split-K nonbit-identical. No new direct original GSQ IQ3_XXS with physical128/259K or Paperniuk dstar release after dstar1.3. Previously published dstar1.3 M1Max short IQ3XXS34.5→38.2 and experimental DFlash2 code41.8 at short context remain older results, not new. The previous good-case forecast 128K decode40–44 and259K37–40tok/s **is speculative and unchanged**, not promoted by these M1 fixes.

### FRESH [Strata #6451](https://github.com/Niko1221/Strata/pull/6451) created **2026-11-21T01:29:25Z**, OPEN — Swift1.5 PLE shard provenance

`strata launch --model-path` incorrectly sets `--ple-gguf` to shard2 for two-file **Swift1.5** original-like packs where `per_layer_token_embd.weight` lives in **shard1**; engine aborts at startup. Proposed family check selects shard1 only for Swift; same file loaded and answered on other **Arc Pro B390** after fix. **NOT** original pristine ISTA GSQ source sharding by default; relevant if discussing Swift swap-in, no model or quant promotion.

## 4. FRESH oMLX 0.8.1 and serious correctness warnings

### [oMLX v0.8.1](https://github.com/jundot/omlx/releases/tag/v0.8.1), **released 2026-11-21T01:17:02Z**

Public release adds Hy4 Flash/Inkling2 support, LoRA, CUDA helper0.1.7, memory and cache fixes. Reports cached long-document follow-up **Qwen3.8-27B at245K TTFT16.4→2.9s (−83%)**, MTP batch Qwen27B M5Ultra +15–26%, M1Ultra Qwen3.6-35B MoE DFlash2 193.3→204.5tok/s (+6%), and fixing [#5454](https://github.com/jundot/omlx/issues/5454) M3Max64 oQ4e MTP long-input cache store lock preventing MLX pool clear, causing 5.5–10.6GB retained and model eviction. Not measurements on user's old M1 GGUF pristine source; changes include compatibility fix for single-file Flash-Next PLE index.

### FRESH [oMLX #5474](https://github.com/jundot/omlx/issues/5474), created **2026-11-21T03:01:12Z**, OPEN — VLM grounding + cached corrupted state

Contributor M5Ultra256GB source family Qwen3.8-Flash-Next **oQ4e+MTP** tests132 click targets in44 synthetic 1280x800 screenshots: normalized coordinate no-think hit-rate **96% in0.7.3→14% in0.8.0/0.8.1**, thinking 100→16%; text OCR unchanged. Disabling `attn_fused.prep_qk` path restores96–100% with no meaningful measured speed loss, **but SSD prefix K/V cached from bad path continues returning bad coordinates until paged SSD cache invalidated** (7/7 fixed empty cache,3/7 fixed+old bad cache). Suggested MRoPE image position axis issue plausible, **not root cause definitively proven**. Does NOT show user's original GSQ GGUF has bug. Essential GUI agent regression case: image-grounding accuracy and cache-version validity, not only text output/throughput.

### FRESH [oMLX #5472](https://github.com/jundot/omlx/pull/5472), created **2026-11-20T22:42:35Z**, OPEN — real but DIFFERENT CUDA prefill helper

Qwen3.6-35B-A3B **oQ4 MTP**, host **M3Ultra512GB**, helper **NVIDIA GB10 DGX Spark**, physically38,771 tokens, no cached input: **host PP1668.7→helper3347.3tok/s (2.01x), TTFT23.23→11.58s**, 8 output IDs, one measured run per arm. CUDA helper family `qwen3_5_moe` added; not Qwen3.8-Flash-Next GSQ and not RTX5070Ti→M1 M1 Metal GGUF Relay, nor Mac helper. Still strong proof that cross-platform P/D *can* accelerate a specifically implemented MoE helper family. Do not equate to a general transfer protocol.

### FRESH [oMLX #5473](https://github.com/jundot/omlx/issues/5473), created **2026-11-21T00:05:26Z**, OPEN — two-Mac prefill pairing can fail

Two *M5 Ultra*512+256 Macs with TB5, DeepSeekV4.1 Flash FP8, oMLX0.8.0: raw shell HTTP reaches peer, but `pair/join` HTTP400, control socket helper not ready, multicast fails to include TB interface; one device manual registration only works after server restart. No prefill actually executed, no applicability to old dual M1 TB4 beyond warning that orchestration/control plane must work.

## 5. Lower priority, drift warnings and negative model watch

- NEW [Strata #6465](https://github.com/Niko1221/Strata/pull/6465) created **2026-11-21T02:59:54Z** OPEN opt-in chunked RAM K/V swap to avoid temporary third full host K/V image when two sessions alternate; host tests pass but **no measured full runtime RSS, latency, GPU, Metal or Windows runs**. Concept relevant HaikuSwarm, not quantitative gain.
- UPDATED OLD [Strata #1614](https://github.com/Niko1221/Strata/pull/1614) comment **2026-11-21T03:18:42Z** one RTX3090 user daily-driving shared KV pool `parallel 8` says good performance, anecdotal, no new numeric test. Older 2×RTX3080 two256K physical test with ~10x faster slot moves (0.36–0.5s vs3.5–5.2s) remains older data, not new current revision performance.
- REDISCOVERED [Strata #6404](https://github.com/Niko1221/Strata/issues/6404) originally **created 2026-11-20T13:33:10Z** prior cutoff: **RX6800 XT gfx1030 16GB VRAM but47.4GB HOST**, Windows Coder IQ1_M, version0.1.60→0.1.63 PP504.8→1067.4tok/s **+111%**, TG42→37.5 **−11%**. Not new underlying result and NOT user RX6800 **NONXT16GB VRAM with ONLY16GB HOST**, not original IQ3XXS. **UPDATED OLD only in window** commenter **2026-11-21T03:33:27Z** analogous RX9060XT RDNA4, host64, source IQ3S anecdotal TG42→35 on v0.1.63.
- FRESH [Strata #6466](https://github.com/Niko1221/Strata/issues/6466), created **2026-11-21T03:21:15Z**, other RX9060XT gfx1200 16VRAM+host64 reporter 0.2.14→0.2.17 thinking TG45–47→32–35 (uncontrolled and subjective) despite improved benchmark PP. Not RX6800 owner.
- UPDATED OLD [Basalt #436](https://github.com/jesdga95/basalt/pull/436) update timestamp **2026-11-20T22:07:33Z** is a *post-merge repository metadata change*; PR already **merged 2026-11-20T00:51:33Z before previous cutoff**. Existing fix maps server-stopping truncation from misleading 200 `finish_reason:"length"` to 503/stream error; record as REDISCOVERED / previously merged, NOT fresh feature.
- UPDATED OLD [antirez/ds4 #1020](https://github.com/antirez/ds4/pull/1020) revised **2026-11-21T00:50:08Z** tokenizer behavior fingerprint in saved conversation checkpoints to reject incompatible tokenizer migrations before restoring old K/V. Built on M5Max128 QFN Q4K, **not merged** and excludes legacy untagged files. A correctness mechanism of same class as oMLX #5474's cache invalidation; distinct tokenizer vs fused-kernel semantic change.
- UPDATED OLD [incoai/Splash #767](https://github.com/incoai/splash/pull/767), updated **2026-11-21T03:30:39Z**, Apple8 M2Max38/64 Qwen3.8 27B **IQ4_XS** DFlash2 context250K TG20tok/s and incremental PP38; M1 Apple7 **still deliberately refused**. No first-party direct user M1 QFN.
- Official [Chinese Qianwen model changelog](https://platform.qianwenai.com/docs/changelog/models) and [official Qwen HF org](https://huggingface.co/Qwen) inspected: as of request cutoff **NO authenticated official open Qwen4-Flash release, shard manifest, total/active param size, PLE/MTP tensor architecture, usable GSQ quant or release date**. Qwen4-Max API Nov16 and Tencent Hy4-flash are different. Community `Qwen4-27B`/Flash placeholders from non-Qwen HF authors are NOT first-party model evidence. Old size rumors remain unconfirmed. This is a scoped negative check, not proof it will never ship.
- No newly dated Paperniuk dstar release, no old M1Max32GPU64 original pristine GSQ IQ3_XXS physically128/259K *completed coding agent* PP/TG, and no verified CUDA5070Ti→Mac M1Metal GGUF original QFN Relay end-to-end.

## 6. Owner hardware, frozen source policy, and derived next research seeds

**Two independent M1Max32GPU64GB 2021 Macs** each distinct64GB address space. Historic original source ISTA GSQ IQ3_XXS physical128K **PP278 TG34.2** and259K **PP258 TG31.7**; Paperniuk dstar1.3 short-context TG~38.2 and DFlash2 code~41.8 other condition; good future **128K40–44,259K37–40** remain subjective forecasts only, not this delta measurement. **Original quant quality IQ3_XXS minimum, IQ3_S preferred when headroom**; never switch to Q2_0 or Coder IQ1_M by stealth. Cache and GPU-resource correctness before speed.

**Frozen PC first:** single RTX5070Ti16, IntelCoreUltra7 265F host64GB DDR5-4800 Linux, **original pristine ISTA QFN GSQ-RCO IQ3_S** official Basalt `.basalt` v2 proven pack PLE provenance; physical32K, single slot INT8 KV, **spec1 NO DRAFT**, CPU-double, exact tool JSON/side-effect and complete coding-agent tasks. Not run or changed. Distinguish fresh other RTX5070Ti as **second GPU expert tier** under RTX5080 in Basalt #382 from owner's single. RX6800 **non-XT VRAM16 + ONLY16GB HOST** not equated to RX6800XT plus47GB host. Relay not validated across CUDA+old M1 external Splash format (QSA indexer/GDN state, KV, PLE, MTP, sample/template exact).

**High-priority followups:** (1) agent compaction + tool parser + cache-protection contract test with Playwright `function` and exact durable file effects; (2) source artifact provenance and paged SSD stale-state invalidation whenever kernel/template changes; (3) repeated 8-conversation 120K throughput/TTFT continuity with same GSQ quant, no silent resend; (4) old M1 Q2 memory lifecycle fixes evaluated *only for equivalent IQ3_XXS and true occupied128/259K* under explicit HIGH approval; (5) official Qwen4 Flash artifact watch, no hearsay parameter choices. No autonomous CI or device activity.

## 7. Commit/verification contract

Write this note byte-identically to dated `RESEARCH-WATCH-2026-11-20-2236.md` and `RESEARCH-WATCH-LATEST.md`, link new focus `AGENT-CACHE-M1-2026-11-20-2236.md`, prepend documentation lead entries to README, STATE, TARGETS, SCRATCHPAD, QUANT-RADAR, METAL and BASALT docs. Independently confirm GitHub branch/head, parent, only markdown diff, and watched matching Git SHA after upload.
