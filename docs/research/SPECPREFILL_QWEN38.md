# SpecPrefill on Qwen3.8-27B / Apple Silicon

Status: **CORE / promoted experimental prompt-processing workstream**

Updated: 2026-08-22

## Why this matters

A growing fraction of the strongest public Apple-Silicon Qwen3.8-27B configurations report using **SpecPrefill** alongside native MTP, ANE prompt processing, or DFlash. This deserves explicit MXFORGE treatment rather than being buried inside benchmark settings.

SpecPrefill is different from decode speculation. It is an **attention-based sparse prefill** technique: a small draft model scores prompt-token importance, the runtime keeps only a selected fraction of prompt tokens for target-model prefill, and original positional information is preserved through adjusted RoPE handling.

Primary implementation:

- https://github.com/jundot/omlx/blob/main/omlx/patches/specprefill.py

Relevant oMLX setting surface:

- https://github.com/jundot/omlx/blob/main/omlx/model_settings.py

The implementation pipeline is approximately:

1. prefill the small scoring model over the full prompt;
2. derive token-importance scores from captured attention queries/keys;
3. select chunked top-K prompt tokens plus protected regions/tail;
4. prefill the target only on the selected tokens;
5. preserve original-position RoPE semantics during subsequent decode.

Default/current knobs include:

- `specprefill_enabled`
- `specprefill_draft_model`
- `specprefill_keep_pct` (typically 0.1-0.5; 0.2 is commonly used)
- `specprefill_threshold` (default commonly 8192 tokens)

Important benchmark-reading rule: a benchmark page can display `SpecPrefill` as enabled even when a short prompt is **below the activation threshold**. Do not attribute 1K/4K results to SpecPrefill unless logs confirm it actually engaged.

## Dense Qwen3.8 applicability

There is conflicting community documentation that must be handled carefully.

A fresh Qwen3.8 benchmark issue claimed SpecPrefill was N/A because Qwen3.8-27B is dense:

- https://github.com/jundot/omlx/issues/2777

However, that statement conflicts with both the actual oMLX implementation and current usage:

- https://github.com/jundot/omlx/issues/1045 documents that SpecPrefill has **no MoE-only gating** and includes architecture-generic/dense query extractors.
- Current public Qwen3.8-27B benchmark submissions explicitly enable SpecPrefill with small Qwen-family scoring models.
- Current oMLX source contains a Qwen3.5/3.8-style query extractor and no simple `dense => disabled` gate in the SpecPrefill implementation.

Therefore MXFORGE should treat SpecPrefill as **applicable to Qwen3.8-27B in current oMLX**, while retaining a version-specific compatibility check before every experiment.

## Fresh Qwen3.8 field evidence

Examples observed in August 2026 include:

- M4/M4 Pro Qwen3.8-27B configurations using Qwen3.5-0.8B or related Qwen-family models as the SpecPrefill scorer.
- M2 Max Qwen3.8-27B configurations using a Qwen3.5-2B scorer together with Lightning MTP.
- A 2026-08-22 M3 Max 96GB Qwen3.8-27B run at roughly **200K prompt tokens** reporting SpecPrefill + Lightning MTP + Qwen ANE prefill, with ~474.6 PP tok/s and ~15 TG tok/s. This is not an M1 transfer number; it is evidence that the three mechanisms can coexist operationally.
- A fresh Qwen3.8 Apple-speed discussion reports an M3 Ultra user combining SpecPrefill with a tuned Qwen3.8 stack and explicitly warning that SpecPrefill is lossy while reporting good practical reliability in their own compaction-heavy use.

Useful discussion / field pointers:

- https://www.reddit.com/r/oMLX/comments/1vr3agq/if_you_were_initially_put_off_by_qwen3827b_pptg/
- https://www.reddit.com/r/LocalLLM/comments/1vv2tw5/people_running_qwen_38_27b_on_apple_silicon_whats/

## Critical caveat: SpecPrefill is lossy

Unlike MTP/DFlash target verification, sparse prefill is **not lossless target execution**. Tokens deliberately omitted from target prefill can remove information that would have influenced hidden/recurrent/KV state.

That makes the objective different from speculative decode:

- decode speculation can remain exact because the target verifies candidates;
- SpecPrefill changes the target's effective prompt representation and therefore can change model behavior.

This matters especially for MXFORGE because the intended workload is agentic coding, where one skipped constraint, identifier, tool schema detail, or earlier error message can matter disproportionately.

Community reports include both positive and negative evidence. An older Qwen3.6-35B-A3B issue showed a severe decode-side regression once SpecPrefill activated:

- https://github.com/jundot/omlx/issues/1262

That issue used an older oMLX build and a different model, so it is not evidence that current Qwen3.8 has the same bug. It is evidence that SpecPrefill must be **whole-request certified**, not judged only by PP tok/s.

## MXFORGE experimental policy

Treat SpecPrefill as a first-class **optional lossy acceleration mode**, not a universal default.

First M1 Max experiment should use the frozen Qwen3.8 coding workload and compare:

1. exact full prefill control;
2. SpecPrefill 50% keep;
3. SpecPrefill 40%;
4. SpecPrefill 30%;
5. SpecPrefill 20% only if quality remains acceptable.

Candidate scoring models:

- Qwen3.5-0.8B, same tokenizer family, speed-first;
- Qwen3.5-2B, potentially better importance ranking at higher scorer cost;
- FP16/BF16 scorer versus quantized scorer if memory permits.

The scorer must share the target tokenizer semantics. Do not use a smaller-vocabulary model merely because it benchmarks faster without first validating token-ID compatibility and importance quality.

## What to measure

Performance:

- scorer full-prompt PP time;
- sparse target-prefill time;
- total TTFT / time-to-first-action;
- selected-token count / keep fraction;
- peak and steady-state memory;
- subsequent TG and verifier latency;
- interaction with native MTP;
- interaction with ANE/GPU prompt processing;
- prefix-cache compatibility / reuse behavior.

Correctness / quality:

- exact tool-schema retention;
- system-prompt constraint retention;
- code-symbol / filename / line-reference retrieval;
- long-range instruction following;
- patch correctness and test pass rate;
- tool-call validity;
- repeated long agent trajectories, not only one-shot answers;
- behavior across compaction boundaries.

For a lossy mechanism, **time per successfully completed task** is the primary metric. A 3x PP speedup that causes materially more failed or misdirected agent turns is a regression.

## Adaptive-runtime role

SpecPrefill should eventually be selected by context/workload policy rather than permanently enabled.

Likely policy shape:

- short prompts below threshold -> exact full prefill;
- stable cached prefix -> reuse prefix, no need for SpecPrefill;
- large cold low-risk context -> SpecPrefill candidate;
- high-stakes tool/schema/constraint-heavy prompt -> exact prefill or conservative keep rate;
- memory pressure -> balance scorer residency, ANE buffers, KV reserve and output reserve;
- after compaction -> consider a conservative sparse prefill only if the compacted state has been quality-certified.

SpecPrefill, ANE/GPU prefill, and prefix-cache reuse are three separate levers:

- **SpecPrefill:** compute fewer target prompt tokens, lossy;
- **ANE/GPU prefill:** compute the prompt faster, intended to preserve semantics;
- **prefix reuse:** avoid recomputing already-seen exact prompt state.

They should be benchmarked independently before stacking.

## Current conclusion

Yes, the community signal is strong enough that MXFORGE should investigate SpecPrefill on Qwen3.8-27B / M1 Max.

But the project should not chase headline PP tok/s. The winning configuration is the **most aggressive keep rate that preserves agent/tool reliability under real ~30K+ coding workloads**, with exact full-prefill fallback available whenever workload risk or observed quality warrants it.
