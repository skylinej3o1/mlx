# Project 51 research watch — 2026-10-02 15:02 ET

Freshness boundary entering: **2026-10-02 16:59:41 UTC**
Cutoff: **2026-10-02 19:02:53 UTC**

## Decision

**No numeric fit, TG/PP, 8 h / 24 h zero-stall, recovery, context-target, or hardware-purchase prior changes.**

This pass does make one important baseline correction:

- **Strata 0.1.36 is the current exact-box baseline.**
- The earlier watch chain incorrectly kept calling 0.1.35 latest even though the 0.1.36 release commit existed before
  the prior cutoff.
- 0.1.36 adds RTX-50-class bitwise-exact decode work and new prompt kernels, but the native-IQ fused prompt path
  remains opt-in.
- **The #481 long-agent lost-step recovery is not part of the 0.1.36 release commit and #481 has no post-boundary
  confirmation that it is fixed.** Do not raise the stability/recovery priors yet.

Current Project-51 exact-box priors therefore remain:
- IQ3_S + native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h zero-stall: **~75%**;
- 24 h zero-stall: **~55%**;
- current-release built-in restart/recovery <60 s: **~55%**.

Native 262,144 remains the production target. No new GPU or 128-GB host-RAM purchase is justified.

## RECOVERED OLDER EVIDENCE — Strata 0.1.36 existed before the prior cutoff

Release commit:
https://github.com/Niko1221/Strata/commit/5ccf3a72cd30159ecaa60d7324a4b79ea9b7b1b5

Created **2026-10-02 09:17:13 UTC**, so this is recovered older evidence, not NEW in the strict window.

The release commit bumps the engine to 0.1.36 and names:
- cancelled-prompt accounting (#471);
- draft-head failure guidance (#474);
- UPDATE.bat / update.sh (#475);
- learned expert-profile persistence (#477).

It does **not** name #481 or the server/engine lost-step recovery described by the maintainer in that issue.

Therefore:
- move the exact-box baseline from 0.1.35 -> **0.1.36**;
- do **not** treat 0.1.36 as the #481 fix;
- keep the exact #481 stress test in the production gate.

## RECOVERED OLDER EVIDENCE + NEW confirmation — 0.1.36 RTX-50 decode and native-IQ prompt kernels

Relevant commits:
- https://github.com/Niko1221/Strata/commit/bbe3d2acb58f750731e7e583fedbfbd4a3e31ccf
- https://github.com/Niko1221/Strata/commit/b3e954592f6e510dbb746261fd57fd84fe335dbe
- https://github.com/Niko1221/Strata/commit/78f071c1715f2e75213fd0b40717d62cd4f092cf

These landed before the entering boundary and were missed by the previous pass.

### RTX-50 decode kernels

The new cluster path is eligible on sm_90+ and explicitly documented as RTX-50-class for Strata's shipped build.

On an RTX 5070, the kernel-level measurements report:
- QSA top-k at 32K: **21.9 -> 15.6 us**;
- 128K: **58 -> 18 us**;
- 262K: **200 -> 22 us**;
- greedy argmax over 248,320 logits: **39.6 -> 5.9 us**.

The parity harness checks selected ids/tokens bit-for-bit over contexts through 262,144, ties, NaNs, infinities,
1-16 queries and captured CUDA graphs.

This is directly favorable for the user's RTX 5070 Ti, especially at deep context, but it is **subphase evidence**.
No controlled IQ3_S full-request TG ladder on the target card is available, so the canonical IQ3_S TG centers do not move.

### Native IQ fused prompt experts stay opt-in

0.1.36 can run fused native-IQ expert kernels under **STRATA_PF_FUSED=1**.

Exact RTX 5070 end-to-end measurements in the implementation commit show:
- IQ3_XXS: ~+1.8% at 4K, ~-0.4% at 32K;
- IQ3_S: **~-0.2% at 4K, ~-1.4% at 32K**.

More importantly for certification, the fused and default prompt paths are numerically close but not the same arithmetic.
The implementation report gives greedy A-vs-B common-prefix lengths including only **31/256** on one IQ3_S 4K arm,
while another IQ3_S arm matched 256/256.

Project-51 rule:
- **do not enable STRATA_PF_FUSED=1 for the IQ3_S source-certification baseline**;
- benchmark it only as a separate experimental speed/quality arm;
- default native-IQ path remains the canonical fidelity lane.

## NEW — Strata #519: 0.1.36 is now being exercised on production RTX hardware

Issue:
https://github.com/Niko1221/Strata/issues/519

Created **2026-10-02 18:04:51 UTC**, inside this strict window.

RTX 5090 / Windows / 96 GB host / Swift IQ3_XXS:
- 0.1.36 default PP is close to 0.1.34 in the reported 2.7K/14.7K/28.9K prompts;
- opt-in STRATA_PF_FUSED=1 gives **+19% / +23% / +13%** PP on that 5090;
- the author did **not** retain answer text, so this is speed evidence only;
- short ~550-token prompts still spend roughly 470 ms in the batched path.

This shows the optional fused-IQ path can pay on a much larger GPU even though it did not pay on the RTX 5070 IQ3
measurements. That makes it hardware-dependent, not a target-card planning uplift.

## UPDATE — Strata #481: no new fix receipt in this window

Issue:
https://github.com/Niko1221/Strata/issues/481

The issue remains open and its latest maintainer comment is still the pre-boundary diagnosis:
- engine main thread in an untimed condition-variable wait;
- likely server/engine lost step;
- next release intended to restart on no-output / unacknowledged-stop conditions.

There is **no post-boundary comment or commit tying that recovery to 0.1.36**.

Because the 0.1.36 release commit does not list #481 and recent commit history does not show the promised recovery,
Project 51 must continue treating it as pending.

This matches the user's intuition that it looks fixable, but it is not yet evidence that it **is fixed**.

## NEW — Strata #525: agent tool calls can be swallowed inside thinking

PR:
https://github.com/Niko1221/Strata/pull/525

Created **2026-10-02 18:48:58 UTC**, open/unmerged.

Observed live on Qwen3.8-Flash-Next:
- the model can move directly from reasoning into a `<tool_call>` without emitting `</think>`;
- current parsing can therefore emit the whole call as `reasoning_content`;
- an agent sees a thinking-only response with no executable tool and can silently stop mid-task;
- reporter saw two occurrences in one overnight session.

The patch treats a tool-call opener inside reasoning as an implicit think end and has streaming/non-streaming tests.

This is **directly relevant to the user's QA/coding-agent workload**. It is not a model-quality failure and not a
runtime deadlock, but source certification should not call Strata production-ready for agent work until this class is
merged/released or independently worked around.

Track alongside #510's malformed/partial historical tool-call fix.

## UPDATE — Strata #500 gets an adaptive threshold, still no planning-speed credit

PR:
https://github.com/Niko1221/Strata/pull/500

After the independent RX 7900 XTX result showed the parallel quant phase losing ~2.3% decode, the author added an
adaptive threshold:
- small quant-job counts stay sequential;
- larger counts use the worker pool;
- default threshold scales with worker count;
- STRATA_POOL_QUANT_THRESH can override.

This is the right shape for avoiding fixed barrier overhead, but no new controlled exact-box A/B exists.
The original +69-78% result remains excluded from Project-51 TG centers.

## UPDATE — Strata #413: bitwise GDN-prefill optimization broadens across Ampere/Ada

PR:
https://github.com/Niko1221/Strata/pull/413

Additional RTX 3090 testing confirms the new DeltaNet recurrence kernel remains bitwise and is a draw-or-win across
the tested SM-count bands. Engine-level expectation remains only ~1.5-2% prefill on the tested IQ3_S split deployment.

No RTX 5070-Ti end-to-end receipt and no PP target change.

## NEW — Strata #507: another 64-GB/16-GB box reports successful real harness use

Issue:
https://github.com/Niko1221/Strata/issues/507

A user reports successful Qwen3.8-Next use in both browser and Pi programming harness on **64 GB RAM / 16 GB VRAM**,
around **40 tok/s** for the session, eventually hitting the configured maximum context.

The quant/context configuration is not stated precisely enough to turn this into an IQ3_S/native262K receipt.
Useful maturity evidence only; no fit-prior move.

## NEW — Strata #511 shows why zero-VRAM-margin configurations remain out of scope

Issue:
https://github.com/Niko1221/Strata/issues/511

RTX 3070 Ti / IQ3_S / 0.1.35:
- startup explicitly reports **0 MiB VRAM free**;
- long OMP-harness use eventually produces GPU/verify timeouts;
- a second stall triggers the existing 60-second watchdog and dump;
- memory snapshot shows ~59.9 GiB committed and only ~1.5 GiB RAM available.

This is not analogous to the target 16-GB card with a mandatory reserve gate.
It reinforces Project 51's existing rule that "fits with 0 MiB free" is a fail, not a success.

## NEW — TensorFold #265: finished-reply resume removes repeated agent-turn prefill

PR:
https://github.com/ashhart/TensorFold/pull/265

On Apple Silicon, planned serving previously failed to reuse a finished reply as the next turn's resume point.

Reported Flash-Next 4-bit agentic multi-turn result:
- turn TTFT **3.55 -> 2.80 s (-21%)**;
- uncached tokens per turn **4,165 -> 3,142**;
- drafted-vs-serial exactness bench: all equal.

Mechanism is relevant to Project 51's retained-agent design, but no Windows/Strata target transfer.

## NEW — TensorFold #268: long-context tree-attention folding improves drafted rounds

PR:
https://github.com/ashhart/TensorFold/pull/268

One GB10, Qwen3.8-27B DFlash2:
- drafted round time ~-5% at 90K;
- ~-8% at 180K;
- ~-9 to -10% at 242K;
- short contexts unchanged;
- drafted rows remain equal to serial under the PR's exactness contract.

Separate 27B runtime; useful mechanism evidence only.

## NEW — TensorFold #271: 128-GB M5 Max resumable-context planner can regress when memory budget rises

Issue:
https://github.com/ashhart/TensorFold/issues/271

TensorFold 0.6.0 / M5 Max 128 GB / Flash-Next 4-bit:
- default 89.6-GiB budget reports a 48,128-token resumable window;
- raising the budget to 107.5 GiB changes prefill chunk 2,048 -> 8,192 and reports only a 10,240-token resumable window;
- reporter's code reading suggests chunk working-memory accounting is inconsistent with retained-window accounting;
- the reporter estimates 2,048-token chunks at the larger budget could allow ~130-140K, but could not configure them;
- one series of high-budget starts coincided with a Mac restart, attribution unknown.

This is an Apple/TensorFold planner issue, not evidence against Strata/Windows native262K.
It strengthens the existing rule that advertised context and resumable agent context must be qualified separately.

## NEW — oMLX #4213: GA memory guard rejects a long Flash-Next session around 139K

Issue:
https://github.com/jundot/omlx/issues/4213

M5 Max 128 GB / oMLX 0.7.0 / Qwen3.8-Flash-Next-oQ4e-mtp:
- long session around ~139K is rejected by the dynamic memory guard;
- reported current+prefill peak is ~78.05 GB against a ~77.82-GB dynamic ceiling despite a much higher static cap.

Again, this is Apple/oMLX admission behavior, not a Windows Strata fit signal.

## OTHER strict-window checks

Searched:
- Strata;
- oMLX;
- TensorFold;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- DASLab / Hugging Face;
- TurboQuant;
- mlx-serve;
- Ishizuki.

Notable adjacent-runtime items that do not move Project-51 targets:
- llama.cpp #29869: major few-row Metal MMA speedup for speculative decode on pre-tensor-API Apple GPUs; strong M3 Ultra
  DFlash2 result, but dense 27B / llama.cpp / M3, not dual-M1 Flash proof;
- SGLang #41729: breakable Qwen3.8 Flash-Next prefill CUDA graphs with explicit non-bitwise graph/eager analysis;
- vLLM #59533: merged QSA/indexer projections improve small-M GEMMs on GB300/B200 but B1 end-to-end is ~neutral;
- no TurboQuant repository change;
- no Ishizuki change;
- no new DASLab long-agent IQ3_S certification table;
- current DASLab model card still lists IQ3_S at 3.50 transformer bpw, 54.8-GB transformer shard + 28.8-GB n-gram
  shard, with AIME25 100, GPQA-D 92.93 and LCBv6 86.86.

## Target state after this pass

1. Current exact-box Strata baseline: **0.1.36**.
2. IQ3_S/native262K physical-fit prior: **~95%**.
3. Windows 16-GB/64-GB full-context admission prior: **~90%**.
4. 8 h zero-stall: **~75%**.
5. 24 h zero-stall: **~55%**.
6. Current-release built-in restart/recovery <60 s: **~55%**; #481 recovery still pending.
7. IQ3_S TG/PP centers: **unchanged**.
8. Default native-IQ prompt path remains the source-certification baseline; STRATA_PF_FUSED=1 is experimental.
9. Add #525 tool-call-inside-thinking to the agentic-production gate.
10. Native production context target remains **262,144**.
11. No hardware purchase change.

## New hard boundary

**2026-10-02 19:02:53 UTC**
