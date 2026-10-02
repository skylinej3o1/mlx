# Project 51 research watch — 2026-10-02 16:03 ET

Freshness boundary entering: **2026-10-02 19:02:53 UTC**
Cutoff: **2026-10-02 20:03:27 UTC**

## Decision

This pass makes a **real production-readiness change**, but **not** a physical-fit or zero-stall change.

- Current exact-box baseline moves **Strata 0.1.36 -> 0.1.37**.
- IQ3_S + native262K physical-fit/admission remains **~95%**.
- Windows 16-GB/64-GB full-context admission remains **~90%**.
- 8 h / 24 h **zero-stall** priors remain **~75% / ~55%** because the #481 root cause is still open.
- Strata 0.1.37 now ships a server-side #481 safety net: a silent/stuck engine is killed, the current request errors,
  and the **next request restarts the engine**.
- New planning prior: **~85% automatic containment/no-manual-service-restart** for a #481-shaped lost-step recurrence.
  This is source/test-based confidence, not a live recurrence/soak receipt.
- Do **not** keep the old “<60 s built-in recovery” probability as if it described 0.1.37. The default
  `engine_silence_s` is **300 s**, plus prompt-reading allowances. Sub-minute recovery requires a deliberately lower
  production setting and its own soak.
- New agent-production restrictions:
  1. **conversation parking/cache OFF** until Strata #528 is fixed/qualified;
  2. **explicit `reasoning_budget_tokens` for high/xhigh** until Strata #530 gains a safe default/warning;
  3. #525 reasoning->tool-call parsing remains an open agent gate.

No TG/PP center move. No hardware purchase. Native 262,144 stays the target.

## RECOVERED OLDER EVIDENCE + UPDATE — Strata 0.1.37 ships the #481 safety net

Release commit:
https://github.com/Niko1221/Strata/commit/db4f91a1171d697928b0d2e1f50ef95e25559d4c

The release commit itself is **RECOVERED OLDER EVIDENCE**: it was created at **2026-10-02 17:26:00 UTC**, before the
entering 19:02:53 UTC hard boundary and was missed by the prior pass.

The strict-window **UPDATE** is the maintainer's new #481 comment explicitly identifying
[0.1.37](https://github.com/Niko1221/Strata/releases/tag/v0.1.37) as the release carrying the safety net.

Implementation commit:
https://github.com/Niko1221/Strata/commit/e07540f84a09639c40f26c176881f66dfdce1e19

The mechanism is concrete:
- during a request, if the engine emits no line for `engine_silence_s`, the server raises `EngineSilent`;
- default silence threshold is **300 s**;
- prompt reads get a larger allowance so a slow 32K prefill chunk is not mistaken for a dead engine;
- the STOP drain is no longer an untimed wait;
- the server kills the engine and marks it ended;
- the current request fails with an error;
- the **next request** starts the engine again;
- `"engine_silence_s": 0` restores the old wait-forever behavior;
- tests cover silence, prefill chunk allowances, STOP-not-acknowledged and HTTP stream/non-stream behavior with a
  fake engine process.

Interpretation:
- this directly addresses the operational consequence of #481;
- it does **not** identify/fix the underlying server/engine desynchronization itself;
- there is no real post-release recurrence receipt or 8 h / 24 h soak yet.

Therefore keep zero-stall priors unchanged but introduce:
- **#481-style automatic containment/no-manual-service-restart: ~85% planning confidence**;
- default recovery latency is **not sub-minute**; 300 s detection is the shipped default.

For Project 51 qualification, test both:
1. default 300 s behavior once, to verify the shipped path;
2. a production candidate lower threshold (after cold/slow-prompt safety testing), measuring stall->error,
   next-request->READY, retained-prefix recovery and total operator intervention.

## NEW — Strata #528: conversation parking can destroy decode throughput after restore

Issue:
https://github.com/Niko1221/Strata/issues/528

Created **2026-10-02 19:16:23 UTC**.

Environment:
- Windows 11;
- RTX 5090 32 GB;
- 96 GB system RAM;
- Strata 0.1.36;
- GSQ-RCO IQ3_XXS;
- INT8 KV, 32K KV-resident, max-context 262144, spec4.

A/B around a ~100K conversation:
- **conversation cache ON**, restored parked snapshot: **17.6 / 20.4 / 26.0 / 31.1 TG**;
- same conversation with conversation cache OFF and ordinary prompt reuse: **86.6 / 100.5 / 115.8 TG**;
- fresh ~100K read without parking: **80.4 / 83.0 / 94.5 TG**.

Longer 27-turn cached session:
- first two turns ~59-64 TG;
- turns 3-27 mostly ~15-31 TG;
- GPU clocks remain full;
- KV streaming ~97-98% resident and expert-cache hit ~93-98%;
- slowdown tracks **restore from parked snapshot**, not generic cache pressure.

This is a major production-agent finding even though it is not the target GPU or IQ3_S.

Project-51 decision:
- **do not enable `--conversation-cache-mib` / conversation parking in the first production baseline**;
- use ordinary prompt/prefix reuse first;
- re-enable parking only after #528 has a root cause/fix and exact-box restore-vs-reprefill A/B;
- this does not lower physical-fit or zero-stall priors because the feature is optional.

## NEW — Strata #530: high/xhigh can consume the whole output budget in reasoning and return empty content

Issue:
https://github.com/Niko1221/Strata/issues/530

Created **2026-10-02 19:26:47 UTC**.

Reporter saw five runs, across Strata 0.1.32 / 0.1.35 and both high/xhigh, finish with:
- `finish_reason: length`;
- empty `content`;
- reasoning alone consumed the request's entire token allowance.

Setting `reasoning_budget_tokens` fixed the reproductions: the server closes the thinking span at the budget and lets
the model answer.

Older issue #123 confirms:
- `reasoning_budget_tokens` has existed since 0.1.31;
- it may be supplied per OpenAI/Anthropic request or as a config default;
- it is **off by default**.

Project-51 decision:
- production high/xhigh requests require an **explicit reasoning budget** until a safe runtime default/warning lands;
- do not treat an empty `content` at `finish_reason:length` as model incapability;
- certification must separately record reasoning tokens, answer tokens and termination reason.

No exact budget number is promoted from this evidence; tune it against the user's actual xhigh QA workload.

## NEW — Strata #529: Anthropic tool_result images are currently dropped before the vision encoder

PR:
https://github.com/Niko1221/Strata/pull/529

Created **2026-10-02 19:19:18 UTC**, open/unmerged.

Claude Code can return an image from `Read` inside an Anthropic `tool_result`.
Current Strata text-flattens that tool result, so the image never reaches the encoder and the model can hallucinate
about a screenshot it has not seen.

The patch preserves image parts inside tool results and reports a successful Windows/RTX5090/Flash-Next end-to-end
screenshot test.

For the user's Playwright/QA lane, this matters if agents inspect screenshots through Anthropic-style tool results.
Add it to the agent-surface gate, but it does not affect text-only certification.

## NEW — Strata #531: peer-GPU expert tier works on 2x3090, irrelevant to the current no-new-GPU plan

PR:
https://github.com/Niko1221/Strata/pull/531

On 2x RTX 3090 + NVLink, IQ3_S / 0.1.36, the opt-in second-GPU expert tier reports roughly:
- prefill +15-25%;
- decode +14-19%;
- byte-identical against the single-GPU baseline under the stated frozen controls.

This is interesting architecture work but does not justify buying another GPU for Project 51.
The user's single 5070 Ti remains the qualification target.

## UPDATE — Strata #418: 0.1.36 dual-Blackwell community run is faster, but not transferable

2x RTX PRO 4500 / 64 GB DDR5 / Swift IQ3_XXS:
- 0.1.36 prompt reading roughly doubled versus the submitter's earlier 0.1.30 run;
- 32K ~5,065 PP, 128K ~5,762 PP;
- output 104.8-132.3 TG;
- 6/6 needles.

Driver/CUDA also changed and this is dual-GPU IQ3_XXS, so no 5070-Ti/IQ3_S target movement.

## UPDATE — Strata #372 / #407 remain optimization candidates, not planning-center inputs

### #372 grouped prompt gathers
Rebased to 0.1.36. Published controlled Windows IQ3_S evidence on an RTX 4080 SUPER remains favorable:
~+4.3% at 32K and +3.8% at 64K, with same short greedy continuation.

This is a credible prompt-path optimization but not yet merged/exact-5070-Ti measured.

### #407 adaptive tier
Also rebased to 0.1.36. Existing IQ3_S tests show no reliable end-to-end round-time win.
Do not add it to TG centers.

## NEW/UPDATE — adjacent runtimes

### TensorFold #273
New CUDA Flash-Next draft-vocabulary superset:
- 79,591 -> 80,014 ids;
- code-shaped held-out coverage ~99.30-99.60% -> ~99.81-99.92%;
- decode measured neutral on one GB10;
- missing draft ids affect speed, not target correctness because every draft is verified.

Mechanism supports Project 51's rule that reduced-vocab MTP is a capacity/speed lever that needs workload-specific
acceptance measurement.

### vLLM #52244
Older PR updated in-window. It fixes hybrid recurrent/GDN prefix-cache replay under MTP so cached prompts can resume
near the true hash-unit ceiling instead of falling back by whole recurrent pages or to zero. Separate runtime/model,
but directly reinforces the need to test prefix reuse **with MTP enabled**, not only serial decode.

### SGLang #41593
Older PR updated in-window. It keeps waiting requests' cached prefixes warm under FCFS-style scheduling so long
multi-turn prefixes are not evicted merely because the request sat in queue. Multi-agent scheduling mechanism only;
no single-stream target movement.

### oMLX #4213
New in-window commenter independently reproduces the 0.7.0 dynamic-memory-guard regression and reports RC1 does not
show the same restrictive ceiling. This strengthens the Apple-runtime regression diagnosis but does not affect Strata.

### mlx-serve #703
Anthropic usage accounting now separates cached from uncached input tokens in an open PR. Useful for Claude-Code
monitoring, not a throughput target.

## Strict-window negatives

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

No TurboQuant repository change.
No Ishizuki change.
No MLX-core change relevant to the current lane.
No new DASLab long-agent/xhigh IQ3_S quality table. The live model card remains at IQ3_S **3.50 transformer bpw,
54.8-GB weight shard + 28.8-GB n-gram shard**, with the same conventional benchmark table.
No target-moving llama.cpp item in this one-hour window.

## Target state after this pass

1. Current exact-box Strata baseline: **0.1.37**.
2. IQ3_S/native262K physical-fit prior: **~95%**.
3. Windows 16-GB/64-GB full-context admission prior: **~90%**.
4. 8 h zero-stall: **~75%**.
5. 24 h zero-stall: **~55%**.
6. #481-style **automatic containment/no-manual-service-restart: ~85%**; no live post-release recurrence receipt yet.
7. Default 0.1.37 silence detection is **300 s**, so do not claim default sub-minute recovery.
8. Conversation parking/cache: **OFF for production baseline** pending #528.
9. High/xhigh: **explicit `reasoning_budget_tokens` required** pending #530.
10. Agent parser/tool gates: #510, #525, and vision-tool_result #529 if screenshot workflows are in scope.
11. IQ3_S TG/PP centers: **unchanged**.
12. Default native-IQ prompt path remains the source-certification baseline; `STRATA_PF_FUSED=1` remains experimental.
13. Native production context target remains **262,144**.
14. No hardware purchase change.

## New hard boundary

**2026-10-02 20:03:27 UTC**
