# Tameru context-compaction audit

Status: **AGENT LAYER / research lead; do not promote as production default yet**

Audited: 2026-08-26

Upstream:

- https://github.com/0xWhiteMage/tameru-compaction-system
- audited upstream commit: `a1072db78fe393875592aae27fa17463673270db`

## Executive conclusion

Tameru is a serious idea mine with considerably better defensive engineering than its age suggests, but its public benchmark marketing currently outruns the reproducible evidence.

The strongest transferable idea is not the headline "beats hosted compressors" claim. It is a deterministic **query-aware extractive view** for bulky agent/tool output, with content-specific log/JSON/CSV handling, conservative fail-open behavior, audit receipts, optional recovery storage, and exact-source snippets instead of free-form summarization.

For MXFORGE/Hermes, do **not** adopt the current live-history pruning design unchanged. Retrospectively mutating old tool messages can invalidate prompt/KV-cache prefixes, and the current Hermes adapter disables recovery storage. The preferred experiment is **ingest-time compaction**: compact a bulky tool result before it first enters the durable transcript, keep the raw result in a local content-addressed artifact store, and expose a retrieval tool. A second safe option is request-only context selection through current Hermes `select_context()` without rewriting persisted history.

## Upstream maturity

At audit time the public repository is extremely new:

- created 2026-08-24
- one visible commit, published 2026-08-25
- v1.1.0 is the initial public commit
- no visible GitHub Actions workflow in the tree
- no community validation signal yet
- core implementation is primarily one ~127 KB Python module

The changelog reports extensive earlier version work and large local test counts, but the public repository history does not independently expose that development sequence. Treat release-verification counts as author-reported until reproduced externally.

## What is genuinely good

### 1. Deterministic extractive core

The default path does not ask another model to rewrite context. It scores blocks and preserves selected source wording. This is attractive for coding agents where exact filenames, hashes, line numbers, error messages, configuration values, and command output matter.

The stdlib-only core dependency claim is accurate. `sentence-transformers` is optional for a semantic tier.

### 2. Content-shape-specific preprocessing

Useful mechanisms include:

- ANSI/progress stripping
- count-preserving repeated-log collapse
- query-selected volatile log rescue
- stack-frame-run collapse
- JSON and CSV query-aware filtering
- git/npm line-record handling
- fenced-code closure
- error-signal preservation

This is more useful for agent traffic than a generic prose compressor because a large share of agent context is structured tool output.

### 3. Conservative hardening

The code contains real defensive work rather than only README claims:

- malformed JSON scanning bounded to avoid quadratic behavior
- cross-`PYTHONHASHSEED` determinism regression coverage
- symlink/path-traversal checks in CCR retrieval
- atomic private cache writes
- digest revalidation
- CCR TTL/future-time validation
- bounded cleanup work
- local-only summarizer endpoint by default, with explicit remote opt-in
- bounded decision cache
- Unicode normalization for some instruction-risk classification

These are worthwhile design patterns even if the selector itself is not yet certified.

### 4. Temporal supersession and graph closure

The engine attempts two agent-relevant problems that simple top-k lexical retrieval misses:

- explicit newer state can supersede an older kept fact
- short rare-entity chains can rescue A -> B -> C evidence

Both are conservative heuristics and need broader evaluation, but the problems are correctly identified.

### 5. Auditability

Machine-readable kept/dropped IDs, risk metadata and optional JSONL audit logging are good production instincts. A context compressor should be inspectable because failures can otherwise appear later as model-quality failures.

## Benchmark audit

### Critical issue: competitive table is not reproduced by checked-in runner

`benchmarks/COMPARISON.md` claims a same-17-case comparison approximately:

- Tameru: 17/17
- BM25 / vector RAG: 12/17
- LLM summarizer: 7/17
- LCM: 3-7/17

But the checked-in `benchmarks/run_battery.py` contains **13 Tameru-only cases**. It does not execute the claimed BM25/vector system, hosted compressor, LLM summarizer, or LCM on the same fixtures.

Therefore:

- the 13-case Tameru battery is reproducible in principle;
- the cross-system headline is **not currently reproducible from this repository**;
- do not cite the competitive ranking as evidence for MXFORGE.

A proper comparison needs frozen inputs, exact system versions/configs, exact compressor outputs, downstream-answer scoring, and one script that runs every arm.

### Latency headline is too broad

The README advertises roughly 5 ms and visually illustrates a 500 KB -> 12 KB transformation in that regime.

The checked-in `production-qa-v3-results.json` instead records the synthetic 4,000-record large-document case at roughly **468.8 ms CPU time**, with 99.5% reported heuristic-token savings. The generated input is roughly a 500 KB-class document.

Other recorded cases show 0.0 or 15.6 ms, indicating coarse/host-dependent timing resolution in the published artifact. The results also omit machine/CPU/OS/Python metadata.

Interpretation:

- tiny/mid-size tool dumps may indeed be millisecond-class;
- the blanket ~5 ms claim is not supported for large contexts;
- benchmark wall time and CPU time separately on the target agent machine.

### Gold-retention metric is narrow

The battery primarily checks whether hand-selected exact strings remain and forbidden exact strings disappear. That is useful regression coverage, but it is not equivalent to downstream agent correctness.

Required future metrics:

- target-model answer/task success after compaction
- tool validity
- exact identifier retention
- multi-turn future-query recall
- false-positive stale/supersession pruning
- compressor-triggered prefix/KV invalidation cost
- actual tokenizer counts for the target model

### Token savings are estimates

`estimate_tokens()` counts a custom regex tokenization. It is not Qwen/Claude/OpenAI/llama tokenizer output. Savings percentages are therefore an internal proxy, especially for code and multilingual text.

Use the actual deployed tokenizer in MXFORGE certification.

## Concrete correctness / contract issues

### 1. Long whitespace-free JSON strings can be dropped

The JSON crusher drops a dictionary string value when it is longer than 120 characters and contains no whitespace, before checking whether that value is query relevant.

That is dangerous for exactly the artifacts an engineering agent may care about:

- JWTs
- base64 values
- long hashes/checksums
- signed URLs
- opaque IDs
- encoded blobs

This conflicts with broad claims that exact identifiers are preserved. Add an adversarial test where the answer is a >120-character whitespace-free value explicitly named by the query.

### 2. "Fail open" is qualified, not literal in every path

The public description implies uncertainty returns the exact original context. In implementation, some uncertainty paths still remove blocks classified as trust-risk, and large structured preprocessing reductions can be retained instead of restoring original bytes.

That may be an intentional safety policy, but the contract should be described as:

> conservative fallback with exceptions for security annotations / proven structural transforms

rather than universally byte-identical fail-open.

### 3. Post-compression verifier is diagnostic only

`verify_compression()` can report medium/high risk, but the core comments explicitly state that this verifier does not alter output. The Hermes live prune path checks `fail_open`, not the verifier's final risk score.

For a production deployment, high verifier risk should normally trigger one of:

1. expansion,
2. original-view fallback,
3. semantic second pass,
4. explicit retrieval attachment.

### 4. ARC block citations are not individually reversible

Rendered omitted-block stubs use short per-block hashes such as `§deadbeef`, while `retrieve()` accepts the separate 24-hex whole-context CCR key. The CCR store persists the complete original context, not a mapping from each short ARC block hash to that exact omitted block.

So current reversibility is best described as **whole-context recovery when CCR is enabled**, not independently retrievable per-block ARC citations.

### 5. Hermes live path intentionally disables reversibility

`apply_extractive_tool_prune()` calls the compressor with:

- `ccr=False`
- `citations=False`

because the Hermes adapter has no retrieval path and tool payloads may contain secrets.

That privacy decision is reasonable, but it means an old tool fact removed by live pruning is gone from the agent-visible transcript unless it exists elsewhere.

### 6. Future-query blindness

The Hermes adapter compresses old tool output against the **current/latest user query** and protects only the two most recent tool outputs.

That is inherently unable to protect a fact that looks irrelevant now but becomes necessary three turns later.

This is the largest correctness concern for autonomous coding agents. A query-aware view is safe when the raw source remains retrievable; it is much less safe when pruning is destructive.

### 7. Decision-cache cache-stability story is weaker in normal chat

The freeze-on-first-sight cache is query-scoped: a different query hash clears prior decisions. In normal multi-turn chat the user query commonly changes every turn.

Additionally, the supplied Hermes pruning adapter does not pass a `decision_cache` into `compress_context()`.

Therefore do not assume the current Hermes integration produces a stable compacted prefix across changing turns.

### 8. Prompt-injection "containment" is heuristic

The trust-risk classifier recognizes a useful set of phrases and normalizes some Unicode tricks, but regex classification is not a security boundary. Paraphrases can evade it and legitimate text can trigger it.

Treat it as ranking/annotation metadata, not prompt-injection prevention.

### 9. One test contains a vacuous assertion

`tests/test_path_re_hang.py` contains:

```python
self.assertTrue(any("acmecorp-genesis" in e for e in ents) or True)
```

which always passes. The latency part of the test still has value, but this assertion does not verify successful entity extraction and should be fixed.

## Hermes compatibility and a better integration seam

Current Hermes officially supports pluggable context engines. More importantly, current Hermes exposes a request-only `select_context()` hook whose returned messages apply to one provider request while persisted history remains untouched.

That seam is preferable for a Tameru-like selector because it separates:

- authoritative history
- request-time compact view

and avoids irreversible mutation of durable session state.

However, changing the request-time prefix can still reduce prompt-cache reuse. The selector therefore needs cache-aware economics rather than firing only because token count crossed a fixed threshold.

## MXFORGE cache interaction: critical

Recent DS4/DwarfStar evidence makes exact context continuity a first-class inference optimization. Rewriting already-cached history can force a large re-prefill.

For a local long-context agent, evaluate compaction as:

```text
future tokens avoided
+ context-capacity headroom gained
- current cached-prefix invalidation / re-prefill cost
- future-query recall risk
- compactor CPU cost
```

A 90% reduction is not automatically a win if it rewrites 80K already-live tokens to save only a few subsequent turns.

## Preferred MXFORGE design

### Option A — ingest-time stable tool compaction (preferred)

```text
tool returns raw payload
        |
        +--> content-addressed raw artifact store
        |
        +--> Tameru-like deterministic compact view
                 |
                 v
        inserted into transcript ONCE
                 |
                 v
        stable prompt / KV prefix
```

The compact transcript should carry a stable artifact ID and the agent should have an explicit retrieval tool for raw/section-level recovery.

This combines Tameru's best property (exact extractive filtering) with DwarfStar's best property (never needlessly invalidate the live prefix).

### Option B — Hermes request-only `select_context()`

Keep canonical history immutable and produce a query-aware ephemeral view per request. Use this only when context pressure warrants the cache churn, and retain a retrieval path.

### Option C — retrospective destructive pruning

Use only as an emergency capacity mode. Do not make this the normal MXFORGE agent path.

## Proposed experiment

Replay real agent sessions with bulky outputs under four arms:

1. raw / no compression
2. current Tameru-style retrospective prune
3. ingest-time extractive + raw artifact retrieval
4. request-only compact view

At 4K / 16K / ~30K / 64K+ context, record:

- real model tokenizer tokens
- compressor CPU wall time
- prefix/KV reuse tokens
- delta-prefill versus full re-prefill
- TTFT
- decode throughput
- complete task wall time
- gold/current-query recall
- delayed future-query recall after 1/3/5/10 turns
- tool-call validity
- retrieval-tool invocations
- artifact-store bytes and SSD writes

Promotion criterion should be **cost per successful completed task**, not compression percentage.

## Audit scorecard

| Dimension | Audit view |
|---|---|
| Core idea | **B+** — highly relevant agent-layer mechanism |
| Defensive implementation | **B** — thoughtful, especially for a two-day public repo |
| Security claims | **C** — file/network hygiene good; injection containment overstated |
| Benchmark credibility | **C-** — own battery useful, competitive table not reproduced |
| Public maturity | **C-/D+** — one commit, no visible CI/community validation yet |
| Hermes as-is production default | **C** — destructive/current-query pruning risk |
| MXFORGE ingest-time adaptation | **A-/B+ research priority** |

## Decision

**Preserve and test; do not promote the upstream runtime unchanged.**

The project is worth tracking because it attacks the correct agent-layer problem and contains several concrete implementation ideas. The next MXFORGE step should be a small clean-room/adapter experiment around **stable ingest-time extractive tool compaction + durable raw retrieval**, benchmarked together with prefix/KV reuse.
