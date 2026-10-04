# Project 51 research watch — 2026-10-03 20:51 ET

Freshness boundary entering: **2026-10-03 19:42:13 UTC**
Cutoff: **2026-10-04 00:51:42 UTC**

## Decision

**No numeric fit/admission/stability/TG/PP target movement.**

Primary Windows state remains:
- Strata baseline: **0.1.38**;
- IQ3_S + native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**;
- #481-style automatic containment/no-manual-service-restart: **~85%**;
- native production context: **262,144**, with **204,800** first fallback;
- baseline long-context KV: **INT8 streamed, ~32K resident first**;
- conversation parking OFF for initial certification;
- explicit `reasoning_budget_tokens` for high/xhigh;
- frozen residency for source/AA qualification.

This pass makes six durable strategy changes/refinements:

1. **Exact RTX 5070 Ti evidence makes larger adaptive prefill chunks a first-class qualification arm.**
   Strata #693, on a 5070 Ti 16 GB / 64 GB Windows host, raises IQ3_XXS long-prompt PP from ~2.4-2.6K to
   **~3.1-3.4K** at 32-100K using `--prefill auto:16384` plus finer/equal chunk planning. This is exact-GPU
   evidence, but not exact IQ3_S, so it changes the test plan—not the canonical IQ3_S PP center.

2. **#646 remains excluded from the 5070-Ti baseline, but its status improves from “unknown crash” to
   “plausible fix awaiting independent sm_120 retest.”**
   The author traced the 5080 crash to mixed shared/global codebook pointer lowering on sm_120 and the source-gate
   drift to final-mixer / fast-math differences, then pushed compile-time staging and exactness fixes. A separate
   partially-resident RTX4090 now reports +5% short, +8% at 32K and +16% at 119K with matching compared outputs.
   Until an independent 5080/5070 retest passes, #646 still receives zero production credit on our lane.

3. **Agent serving should use `fit_max_tokens=true` for long coding sessions, while logging the effective cap.**
   Strata #694 shows a real OMP session where prompt + configured 64K max output exceeded a 131K window and hard-400'd;
   enabling the already-supported fit behavior solved it. This is server admission hygiene, not model context
   expansion.

4. **Copy-from-context drafting becomes a future custom-engine optimization for rewrite-heavy coding work.**
   TensorFold #319 verifies copied spans before MTP chains and accelerates a file-rewrite response **~3.7x** while
   keeping drafted output equal to serial. This is CUDA evidence, not an M1 receipt, but it maps unusually well to
   the user's brownfield QA/file-edit workload and belongs after the basic M1 verifier is correct.

5. **Apple long-context qualification keeps “prefill success != usable context.”**
   oMLX #4206 now has an M5 Max 128-GB stock-config 510K run passing 12/12 structured needles, but 800K can complete
   prefill and then die at decode start from a +15-25 GB transient. It also observes a sharp prefill-cost step exactly
   at the native 262,144 boundary. This strengthens the existing transient/decode-start gate; it does not move M1
   Max targets.

6. **Agent parser gate expands again.**
   Strata #700 catches `<tool_call>` named in prose before a real call; oMLX #4233 and MTPLX #588 independently
   reinforce unclosed-thinking recovery ambiguity. Parser correctness remains a separate production blocker from
   hardware/runtime fit.

No newer Strata release than **0.1.38**.
No new exact M1 Max DASLab/ByteShape benchmark.
No new exact single-RX6800 dense-27B PP receipt.

## NEW — Strata #693: exact RTX 5070 Ti shows large PP headroom from chunk planning

PR:
https://github.com/Niko1221/Strata/pull/693

Created **2026-10-03 22:21:32 UTC**, open.

Environment:
- RTX **5070 Ti 16 GB**, PCIe 3.0 x16;
- Ryzen 9 5900XT;
- 64 GB DDR4-2133;
- Windows 11;
- IQ3_XXS;
- 400K configured context, INT8 KV.

Mechanism:
- current `auto:16384` tries 16K, then falls directly to 8K;
- a 16-GB card may fit an intermediate chunk such as 13K but not 16K;
- because >=1K chunks stream nearly all non-resident experts, fewer/larger chunks substantially reduce repeated
  expert streaming;
- patch tries every 1K size above 8K and uses equal-sized chunks when that does not create a tiny last chunk.

Measured PP:
- ~20K: **2,101 -> 2,898 (+38%)**;
- ~32.7K: **2,570 -> 3,120 (+21%)**;
- ~40K: **2,546 -> 3,088 (+21%)**;
- ~65K: **2,597 -> 3,392 (+31%)**;
- ~100K: **2,428 -> 3,275 (+35%)**.

Needles:
- 9/9 at 32K, 128K and 262K depths 10/50/90 with `auto:16384`.

Important limits:
- model is IQ3_XXS, not target IQ3_S;
- host is DDR4/PCIe3, not the user's stronger DDR5 platform;
- branch is open;
- `auto:32768` not measured.

Project-51 decision:
- exact-box IQ3_S qualification gains explicit prefill arms:
  1. released `--prefill auto`;
  2. `--prefill auto:16384` with #693-equivalent finer sizing;
  3. optionally `auto:32768` if VRAM reserve/transient gate still passes.
- benchmark 16/32/64/128/200/250K cold prompts and record actual chunk size, expert-loan slots, file/RAM reads,
  transient VRAM and final PP.
- **no IQ3_S PP-center raise until exact-quant measurement**.

## UPDATE — Strata #646: author fixes the reported sm_120 crash/exactness roots, but independent retest is still required

PR:
https://github.com/Niko1221/Strata/pull/646

After the previous pass's RTX5080 crash and IQ3_S exactness failures, the author reports two root causes/fixes.

### sm_120 crash root cause

The new expert code selected between shared-memory and global/constant codebook pointers through a runtime ternary.
CUDA 13.2 on sm_120 emitted a mixed address-space generic-pointer sequence that miscompiled for multi-column IQ3_S.

Patch:
- compile-time `STAGE_GRID` selection;
- IQ3_S/IQ3_XXS use constant/global cache rather than staging;
- staging remains only on the wider 64-bit tables;
- kill switch `STRATA_IQ_STAGE_GRID=0`;
- PTX inspection shows the mixed `selp.b64` path removed.

### exactness root causes

Two sources were identified:
- fused final mixer changed the FP32 reduction order / exp implementation immediately before lm_head;
- Q8_1 quantization had crossed a `--use_fast_math` compilation boundary.

Patch:
- restores the old final mixer by default (`STRATA_FUSE_HEAD_GR=1` becomes opt-in);
- moves/fixes SwiGLU/Q8_1 arithmetic to reproduce the unfused instruction behavior;
- adds component kill switches for A/B.

Micro parity now reports the IQ kernels bitwise equal to the old path in the author's tests.

### New independent Ada partial-residency data

RTX4090 24 GB, IQ2_XS, ~1/3 experts in VRAM, 262K:
- short decode: **+5%**;
- 32K: **+8%**;
- 119K: **+16%**;
- prompt speed unchanged;
- compared recall outputs / MTP acceptance matched;
- no spec4 faults in ~40 requests.

This is encouraging mechanism evidence but is **sm_89 / 24 GB / IQ2_XS**, not the target.

Project-51 status:
- move #646 from “reject until root cause known” to **“watch, fixes plausible”**;
- still **zero speed credit** in 5070-Ti planning;
- promotion requires the original/another independent **sm_120 16-GB partially-resident IQ3-family retest**, then exact
  IQ3_S source gate and soak.

## NEW — Strata #694: fit max_tokens for agent clients that advertise huge output budgets

Issue:
https://github.com/Niko1221/Strata/issues/694

OMP client:
- context 131,072;
- prompt 67,811;
- client `max_tokens=64,000`;
- request hard-fails because 67,811 + 64,000 > 131,072.

Enabling existing `fit_max_tokens=true` caps the output budget to the remaining context and the workflow proceeds.

Project-51 agent-serving profile:
- enable **`fit_max_tokens=true`** for coding clients that send a large static output allowance;
- still set explicit `reasoning_budget_tokens`;
- log requested max, fitted effective max, reasoning tokens and visible-answer tokens;
- never interpret the fitted cap as additional model context.

## NEW — Strata #700: a tool tag mentioned in prose can currently abort a real tool call

PR:
https://github.com/Niko1221/Strata/pull/700

Created **2026-10-03 23:31:42 UTC**, open.

Current parser treats every literal `<tool_call>` as the start of a call. Example:
- model says in prose: “I will use the `<tool_call>` format now.”
- then emits the real call.

The first prose tag captures the remainder and the parser raises malformed-tool-call.

Patch only treats the tag as a call opener when followed by `<function=`; streaming holds the potential tag until
its follower is known.

Project-51 parser suite adds:
- literal/backticked `<tool_call>` mentioned in prose;
- then a genuine call later in the same response;
- streaming and non-streaming parity.

## UPDATE — TensorFold #319: copied-context proposals can dominate rewrite-heavy coding responses

PR:
https://github.com/ashhart/TensorFold/pull/319

Flash-Next CUDA now tries a copied continuation from already-present context before an MTP chain when >=8 tokens
repeat. Copy verify windows start at 16 rows and grow to 64 while the copy keeps landing.

DGX Spark / Flash-Next 4-bit MTP / 262K:
- rewrite a 2,274-token file already in the prompt: **~92 -> 340-341 TG (~3.7x)**;
- OLD/NEW edit block: ~91 -> **~224 TG**;
- unrelated new-code generation: essentially unchanged;
- drafted outputs were checked equal to serial in the reported suite.

Memory at parallel5 rises modestly (~84.9 -> 86.8 GiB startup estimate); concurrency can make unrelated requests
share wider rounds, so scheduling needs care.

Project-51 custom-engine implication:
- after the base M1 27B verifier/state engine is correct, add a **copy-index / context-copy proposal lane** before
  MTP for repo/file rewrite operations;
- verify every copied row through the same target path;
- measure the user's actual Playwright patch/rewrite traces, not generic prose;
- no single-M1 target movement because this is CUDA and workload-dependent acceleration.

## UPDATE — oMLX #4206: 510K works on M5 Max, 800K exposes decode-start transient cliff

M5 Max 128 GB / Qwen3.8-Flash-Next / 4-bit TQ / YaRN:
- **509,676 tokens: 12/12 structured needles**, including six beyond native262K;
- cold PP roughly **1,452-1,537**;
- decode ~140-190 TG with MTP;
- stock settings also pass.

At 800K:
- prefill can finish around ~96 GB resident;
- first decode step adds roughly **15-25 GB** transient and aborts;
- forcing gathered attention and disabling MTP do not remove the spike.

Another repeatable observation:
- same 8K chunk below native boundary: ~6.2 GB step;
- chunk ending exactly at **262,144**: ~18.6-19.5 GB step;
- ~3x cost discontinuity at native-context crossing.

Project-51 lesson:
- “cold prefill completed” does not certify a context size;
- admission must include first decode/verify and at least one continuation;
- this further validates our Apple cold-prefill transient gate but does not transfer M5 rates/capacity to M1.

## NEW — oMLX #4233 / MTPLX #588: unclosed reasoning remains a cross-runtime parser ambiguity

oMLX #4233:
- Qwen3.8-27B can EOS while still inside template-opened `<think>`;
- non-streaming path may return ~14.5K reasoning tokens as ordinary `content` with `reasoning_content=null`;
- deterministic on the reported case.

MTPLX #588:
- fixes the opposite agent symptom after tool use: a clean-stop answer inside an unclosed reasoning block can be
  recovered as visible content when tools are declared, but only when no tool-control markup/call is present.

These are not contradictory: they show that “unclosed think + stop” is semantically ambiguous.
Project-51 parser must distinguish:
- genuine final answer written inside an unclosed think block;
- model simply stopping mid-reasoning;
- actual tool markup/call;
- length truncation.

Do not solve this by blindly moving every unclosed reasoning block to content or every one to reasoning.

## UPDATE — ByteShape / DASLab 27B check

No new exact M1 Max 64-GB benchmark or long-agent table appeared in this strict window.

Current artifacts remain unchanged for Project 51:
- DASLab IQ3_S target-only ~11.8 GB;
- DASLab IQ3_S-MTP integrated ~12.1 GB;
- DASLab IQ3_XXS ~10.1 GB / MTP ~10.4 GB;
- ByteShape remains the alternate ~3.2-3.8-bpw quality-allocation family.

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- MTPLX;
- Splash;
- Ishizuki;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- TurboQuant;
- mlx-serve;
- DASLab/Hugging Face;
- ByteShape.

Strata main still declares **0.1.38**.
No strict-window TurboQuant repository change.
No strict-window MLX-core Metal change relevant to the M1 lane.
No strict-window Splash/Ishizuki change.
No exact single-RX6800 dense-Qwen3.8-27B PP receipt.
No hardware-purchase evidence.

## Target state after this pass

1. Primary Windows baseline: **Strata 0.1.38**.
2. IQ3_S/native262K physical fit: **~95%**.
3. Windows 16GB/64GB admission: **~90%**.
4. 8 h / 24 h zero-stall: **~75% / ~55%**.
5. #481 automatic containment: **~85%**.
6. Native target 262144; 204800 first fallback.
7. Long-context baseline: INT8 streamed KV, ~32K resident first.
8. Exact 5070-Ti PP qualification adds **#693-style `auto:16384` fine/equal-chunk arm**; no IQ3_S PP-center move yet.
9. #646 remains outside 5070-Ti production baseline; root fixes are plausible but need independent sm_120 retest.
10. Agent-serving profile: explicit reasoning budget + **`fit_max_tokens=true`**, with effective cap logged.
11. Agent parser gate adds prose tool tags and ambiguous unclosed-thinking cases.
12. PLE ladder unchanged: IQ4_NL -> FP8 candidate -> BF16 exact control.
13. Single-M1 27B remains **25 TG / 110 cold PP**.
14. Custom M1 engine priority: multi-row long-context verify/state lifecycle first; later add **copy-from-context drafts**
    for rewrite-heavy QA/coding workloads.
15. RX6800 producer remains target-only prefill/spec-off first, pending exact PP + state bridge.
16. Conversation parking remains OFF initially; disk session restore remains a separate persistence candidate.
17. No hardware purchase change.

## New hard boundary

**2026-10-04 00:51:42 UTC**
