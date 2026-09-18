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

- **Flash-Next target quant is Q5-class / eventual ~5.x BPW, not Q6/Q8.** Q6/Q8 wording for the Flash lane is stale. The current headline remains Qwen3.8-Flash-Next on 2x M1 Max 64 GB / TB4 at ~128K active context, targeting 40 tok/s TG and 400 tok/s cold PP.
- **oQ4e is a comparator/fallback lane**, useful for measuring the speed/quality frontier; it is not the canonical Flash target unless a later evidence-driven decision explicitly changes the target.
- Q6/Q8 may still be relevant to the much smaller Qwen3.8-27B lanes and to verifier work; do not transfer that wording to Flash-Next.

## Research-update search protocol

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

## Continuity rule

If a future conversation's chat context or memory conflicts with these files, re-read the repository and follow the repository's current state. If this protocol itself changes, update this README so the next conversation inherits the change.