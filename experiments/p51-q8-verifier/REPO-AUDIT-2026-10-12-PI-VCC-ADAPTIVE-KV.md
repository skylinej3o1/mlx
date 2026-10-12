# Project 51 source audit: pi-vcc and Adaptive KV Streaming V2
Date: 2026-10-12. Evidence cutoff: 2026-10-12 13:07:45 UTC. Status: **research only; no code promotion**.

## 1. sting8k/pi-vcc
Source: https://github.com/sting8k/pi-vcc ; package v0.10.1 and master as inspected October 12.

**Mechanism:** deterministic, non-LLM conversation compaction for the Pi coding agent. It extracts goals, file operations, commits, failed/test commands, durable preferences, and an abbreviated transcript, while exposing a session-JSONL search/expand tool (`vcc_recall`). It does **not** change LLM KV residency, model capacity, or GGUF execution. Only current session/branches are searchable; not automatically shared across fleet agents.

**Source evidence:** `src/hooks/before-compact.ts` implements Pi's `session_before_compact` hook; `src/core/rank.ts` ranks durable code-work facts (edits/tests/failed commands); `src/core/recall-run.ts` reads session lineage and supports direct expansion; `src/core/search-entries.ts` has BM25-related scoring, hard limits and search-budget checks. `.github/workflows/ci.yml` runs typecheck and tests on locked and Pi 1.1.0 configurations. Pi 1.1 `context_edit` handling fix merged in PR #49 (https://github.com/sting8k/pi-vcc/pull/49).

**Evidence limits:** 97.6% median size reduction is NOT semantic information-retention accuracy. `benchmarks/README.md` reports ranked brief weighted fact recall median 69.2% vs its *older pi-vcc baseline* 72.0%; ~1.4x normalized fact density; around 17-20% absolute weighted fact recall on huge held-out sessions. Its baseline is **not** an independent Pi LLM-compaction comparison. Tested fact categories primarily identify commands/files/commits, not complex invariants or architecture tradeoffs. Some historical context can be recalled only if the agent elects to call the tool. Search may find superseded edited branches when scope broadens; retrieved claims need source and recency checks.

**Action:** pilot side-by-side using `overrideDefaultCompaction: false`; invoke `/pi-vcc` explicitly on noncritical test sessions. Grade hidden architectural facts, superseded decisions, required exactness constraints, action continuity, recovery from failure, elapsed task wall time, and token costs. Maintain a separate curated canonical decision ledger. Only consider automatic override after positive A/B results.

## 2. RaymondHuang210129/llama.cpp-adaptive-kv-streaming
Source: https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming ; default branch `feature/adaptive-kv-stream-v2` as inspected October 12.

**Mechanism:** full-context Qwen3.8-27B attention KV is authoritative in pinned host RAM, while a bounded CUDA GPU arena holds resident KV pages and a streaming ring. It has ready/consumed fences, prefetch, phase-specific arena leases (prefill/decode/MTP/vision), MTP KV in the same physical pool but separate logical host history, and host-staged recurrent/GDN rollback on rejected speculative candidates. This is full-history streaming, **not sliding-window truncation** and not compression of the model weights.

**Source evidence:** `src/llama-kv-stream-*.[ch]pp` and `ggml/src/ggml-cuda/kv-stream-*.[ch]u*` implement explicit policies and ownership; `tests/test-kv-stream-*.cpp` spans caching, copying, lease, attention, MTP, resume and persistence cases. Qualifying runtime is **single RTX 5070 Ti CUDA GPU, one serial request, Unsloth Qwen3.8-27B UD-IQ4_XS, Q8_0 K/Q4_0 V, 256/256 batches, fixed 2,240-MiB participating arena**.

**Measured historical V2 single-run at actually filled context:** ~32K: no MTP 41.04 TG, MTP depth 3 101.05 TG; near 256K: no MTP 8.73 TG, MTP depth 3 19.12 TG. These compare MTP modes on the older V2 build, NOT V1 vs V2.
**Separately reported Oct 11 upstream-attention rebase:** MTP=3 96K 69.96 TG, 128K 54.06 TG, 192K 28.51 TG. Different revision and qualification cohort; **do not splice 256K historical point into this curve**. Benchmark script `benchmarks/run-fixed-span-sweep.py` constructs a prompt nearly filling context, checks actual `prompt_n` and `predicted_n`, and supports `--no-manage-production`; this evidence exceeds a mere advertised-context flag. Still author-produced, mostly single-run, and without our independent quality/throughput audit.

**Boundaries:** weights, pinned host KV, persistent recurrent state, MTP weights and CUDA runtime allocations fall outside the fixed 2,240-MiB participating arena. Mixed vision/MTP example reports 15,836 MiB sampled on a 16,303-MiB RTX 5070 Ti; sampled usage is not a peak-safety guarantee. Parallel slots, multi-GPU execution, cross-backend CUDA/Metal checkpoint handoff, direct Metal streamed attention, generic future models and arbitrary KV pairs are NOT qualified. Multi-GPU PR #2 remains unmerged (https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming/pull/2). No inference runs were executed on the user's equipment in this audit.

**Action:** retain as a dense-27B CUDA research lane and implementation reference for a bounded-state Relay memory manager, leases, checkpoint ownership, and MTP recurrent rollback; do **not** substitute it for our Flash-Next/Swift Strata deployment and do not assume Metal portability. A/B on separate isolated 5070 Ti test environment at real 32K/128K/192K/near-256K with full tokens, correct output/needle/tool tests, TTFT, cold prefill, TG, host pinned bytes, total VRAM peak and failures. Match model/quant/draft context with controls. Keep CUDA-only port risk separate from Project 51 PP2 feasibility.

## Decisions and negative results
- Neither repository is production-promoted or an exact dual-M1 Max / Thunderbolt 4 Project 51 performance receipt.
- pi-vcc and physical KV streaming solve different layers: prompt-token reduction/recall versus preservation and placement of full inference state.
- Preserve the user's exact verifier/runtime proof gates, source-like xhigh quality objective and accepted certified optimizations; none of the benchmark reports revises those.
- No new GPU, RAM or Apple hardware purchase is recommended from this audit.
