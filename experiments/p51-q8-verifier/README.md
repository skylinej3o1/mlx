# Project 51 — Read First

This file is the entry point for **every new conversation/session** that continues Project 51 research or tuning.

## Required read order

Before searching, updating, benchmarking, or changing a Project 51 conclusion, read:

1. `README.md` (this file)
2. `RESEARCH-STATE.md`
3. `RESEARCH-TARGETS.md`
4. `RESEARCH-WATCH-LATEST.md`
5. Any newer dated watch/addendum needed for continuity

The repository is the durable source of truth. Do not reconstruct project state from chat memory when the repo can be read.

## Canonical lane reminders

- **Flash-Next deployment-quant design is an xhigh-specialized custom mixed lane, not a stock whole-model BPW label.** Start the serious production search around **~3.5 average transformer BPW** and test roughly **3.0 / 3.2 / 3.4 / 3.6** heterogeneous arms, with the current likely source-like xhigh frontier estimated around **~3.3-3.6 BPW**. PLE/ngram precision and MTP precision are tracked separately. Promotion requires repeated source-like xhigh reasoning/coding/tool/long-context/agent behavior; nominal BPW alone is never certification.
- **oQ5e remains the quality/certification comparator.** The custom deployment quant should retain essentially oQ5e/BF16 behavior on the frozen Project 51 eval battery before it can replace the quality reference.
- **oQ4e remains the aggressive performance comparator/fallback lane**, useful for bounding the speed side of the frontier; it is not the quality reference.
- Q6/Q8 may still be relevant to sensitive Flash submodules (for example MTP/QSA/GDN/HC/head) and to the smaller Qwen3.8-27B lanes; do not interpret those local precisions as a whole-model Flash target.

## Research-update search protocol

**User shorthand:** when the user says **"search and update"**, that is an instruction to do both halves in the same turn:

1. **Search** for fresh Project 51 evidence after the current hard freshness boundary.
2. **Update / true up GitHub**: write the dated research watch, replace `RESEARCH-WATCH-LATEST.md`, update `RESEARCH-STATE.md` and/or `RESEARCH-TARGETS.md` whenever durable conclusions or planning state changed, commit on `project51-q8-verifier`, then read back and verify the final canonical state.

A chat-only research summary does **not** satisfy "search and update." Do not wait for a second request such as "update GitHub." If the search produces no durable change, still advance the dated watch / `LATEST` freshness boundary and record that targets/state are unchanged.


For every external research update:

- Start strictly **after the hard freshness boundary in `RESEARCH-WATCH-LATEST.md`** and stop at the exact user-requested/message cutoff.
- Explicitly scan **PRs, issues, and commits** for DS4, vLLM, oMLX, mlx-serve, and llama.cpp, plus relevant Hugging Face/community surfaces.
- Evidence timestamp means the substantive source/measurement timestamp, **not** crawler, merge, rebase, label, or comment time.
- Keep exact receipts, transfer evidence, experimental A/B results, and speculation/planning targets distinct.
- Do not move canonical targets without exact active-topology evidence.
- Write a dated `RESEARCH-WATCH-YYYY-MM-DD-HHMM.md`, replace `RESEARCH-WATCH-LATEST.md` with identical contents, commit on `project51-q8-verifier`, verify final HEAD, verify the dated watch and LATEST are identical, and report the new hard boundary.

## Required chat briefing after each research update

**Do not reduce the user-facing response to only a commit SHA, freshness boundary, and one-line highlights.** The chat response is a research briefing; the watch file is the durable detailed record.

For each meaningful new finding, summarize:

1. **What happened** — source/issue/PR and the mechanism or result.
2. **Measurements** — the important exact numbers, topology, model, context, quantization/backend, and relevant conditions.
3. **Relevance to Project 51** — whether it is exact active-topology evidence, exact non-target evidence, strong/weak transfer evidence, or planning/speculation.
4. **Action / durable rule** — what benchmark, implementation, qualification, or instrumentation rule changes because of it.
5. **Target impact** — explicitly say whether canonical targets change and, when useful, whether confidence in a target moved even if the numeric target did not.

Also report the final commit SHA and new hard freshness boundary. Mention meaningful negative results and important things checked that produced no qualifying evidence when they help explain why targets did not move.

The briefing should be **reasonably detailed and analytical, comparable to the fuller Project 51 research summaries from earlier conversations**, while avoiding a dump of irrelevant PRs/commits. Measurements must remain clearly separated from estimates, extrapolations, and speculation.

## High-reasoning tuning control plane

Project 51 tuning must separate **decision authority** from **execution**.

- ChatGPT web running **GPT-5.6 Sol with High reasoning effort** is the experiment decision/orchestration plane for substantial tuning decisions: proposing the next mutation, interpreting causal evidence, promoting/rejecting an optimization, or changing the benchmark plan.
- GitHub Actions and the self-hosted Macs are the execution plane. They may compile, benchmark, collect telemetry/artifacts, verify SHAs, and finish work that was already approved, but they must not invent or promote the next tuning mutation on their own.
- Use an explicit lifecycle such as: **PROPOSED -> HIGH-APPROVED -> RUNNING -> RESULTS -> AWAITING-HIGH-REVIEW**.
- A new experiment definition may run only from **HIGH-APPROVED**. After results are produced, the workflow must stop at **AWAITING-HIGH-REVIEW** until a later High-reasoning ChatGPT turn reviews the result and explicitly approves the next experiment.
- Record provenance in a machine-readable experiment manifest. At minimum include: `decision_model: GPT-5.6 Sol`, `reasoning_effort: High`, `decision_source: ChatGPT web`, experiment ID, approving/decision commit SHA, exact benchmark/runtime SHA(s), and the state transition.
- This provenance is an operational gate, **not a cryptographic attestation**: GitHub Actions cannot independently verify the user's ChatGPT web model-picker/reasoning setting. Therefore a workflow may trust only the repository's explicit approval state, not infer High from environment or account state.
- If the ChatGPT reasoning allowance changes, an already approved run may finish, but **no new hypothesis or mutation may auto-promote**. The next decision waits for a fresh High-reasoning review.
- For distributed runs, keep the existing invariant: `Mac1 SHA == Mac2 SHA == result metadata SHA` before accepting a result.

This rule is intended to ensure that **High does the thinking; Actions does the labor** while preserving reproducible, auditable tuning loops.

## Continuity rule

If a future conversation's chat context or memory conflicts with these files, re-read the repository and follow the repository's current state. If this protocol itself changes, update this README so the next conversation inherits the change.