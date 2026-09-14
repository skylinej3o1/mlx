# External runtime watch — 2026-09-13 20:57 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-13 19:33:05 UTC` through the user-request cutoff `2026-09-14 00:57:57 UTC`.

Evidence timestamp remains the substantive source timestamp, not crawl/rebase/merge-only churn. Older items surfaced by the user are retained as **RECOVERED OLDER EVIDENCE** and are not date-refreshed.

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | 40 tok/s @ ~128K active context | 400 tok/s | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | 25 tok/s | 110 tok/s native/exact-runtime | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | 120 tok/s | 250 tok/s | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | 15 tok/s | 180 tok/s | unchanged |

P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured internal GDN/projection/downstream-tail evidence.

---

# Fresh evidence

## oMLX #3647 — generated-prefix MTP head history must be cached with the backbone

**FRESH NEW / HIGH-VALUE FLASH-MTP PREFIX-CACHE CORRECTNESS.**

Generated tokens could enter the backbone prefix cache without a matching MTP head-history sidecar. A later turn could restore the backbone block while losing drafter history. The draft fix publishes a detached head-cache snapshot plus pending normalized hidden row at committed full-block boundaries and explicitly trims the previous speculative chain before folding the confirmed boundary row.

Focused MTP/scheduler/VLM suites report 337 passes + 3 skips; tiny-model full-history oracle coverage exercises depth 1/3 and shared/cloned head caches. Full Qwen4 repeated-prompt qualification is still pending and no throughput claim is made.

**Promote:** a prefix-cache hit is not MTP-correct unless backbone block, head-history boundary, pending hidden row and speculative rollback state identify the same committed token boundary.

## oMLX #3651 — 2x64 GB planner can over-promise context if SDPA transient is omitted

**FRESH NEW / DIRECT DUAL-64GB LONG-CONTEXT CAPACITY EVIDENCE.**

A real 2x64 GB pipeline was planned for 425,984 tokens yet rank 0 refused prompts above ~320K because admission charged an unfused head-dim-256 fp32 SDPA score transient that the planner omitted: at 320K the report measured roughly 24.25 GB `KV+SDPA` versus 8.7 GB pure KV.

The proposed planner now uses the same transient estimator as admission and binary-searches the longest context whose KV + transient fits. Physical 2x64 rerun remains pending.

**Promote:** context capacity identity = resident weights + persistent KV/state + route-specific peak transient. Planner and runtime admission must use the same executed attention route and chunk size.

## oMLX #3653 — pipeline-aware MTP patching does NOT mean distributed MTP is enabled

**FRESH NEW / CRITICAL ACTIVE-PLAN CONSTRAINT.**

The Qwen3.5 MTP compatibility patch had dropped the ordinary pipeline flow and is being repaired to mirror upstream recv/send/all-gather behavior. The PR explicitly states: **distributed MTP remains rejected elsewhere; this fix only restores ordinary distributed serving.**

**Consequence:** the dual-M1 Flash plan cannot assume stock oMLX gives PP2 + Lightning MTP just because the model fits and the patched model call is pipeline-aware. Distributed speculative execution remains an engineering/certification workstream.

## oMLX #3655 — distributed prompt-cache slot count was silently forced to one

**FRESH NEW / DIRECT AGENT-LONG-CONTEXT DISTRIBUTED EVIDENCE.**

The distributed tuner forced `prompt_cache_size=1` on every path. Any interleaved request could evict the active conversation prefix; the field report saw ~110 s re-prefills around 45K tokens. The proposed fix keeps byte-based eviction disabled for cross-rank coherence but honors a deterministic count-based LRU slot limit.

**Promote:** distributed prefix-cache identity includes eviction policy. Byte-budget eviction may diverge across unequal PP stages; count-based recency can remain rank-coherent when request-event order is shared.

## oMLX #3654 — expert-major chunking removes pathological prefill refetch churn

**FRESH NEW / OFFLOAD CONTINGENCY + MOE PREFILL MECHANISM. Not primary Flash lane while Lightning MTP and expert offload are mutually exclusive.**

The old token-axis chunking could fetch the same expert repeatedly. On a 585-token Gemma-4 MoE prompt, 12.5% residency caused 64,369 expert fetches; expert-major chunking reduced that to 2,913 and warm TTFT 16.60 s -> 0.97 s. 25% residency: 30,302 -> 2,675 fetches and 8.87 -> 0.85 s warm TTFT. Decode path is unchanged.

**Promote as mechanism:** when offload is used, chunk work by stable resource ownership/expert set rather than token slices that repeatedly evict/reload the same resource.

## vLLM #56720 — long-context compressed-KV gather needs launch width proportional to live gather length

**FRESH NEW / STRONG LONG-CONTEXT SPARSE-PREFILL TRANSFER.**

DeepSeek-V4.1-Flash ROCm prefill used a fixed 128-worker gather grid even when each worker walked thousands of dependent cache loads. Sizing workers by the host-known live gather length improved 131K warm-cache mean prefill 446.9 -> 320.8 ms (-28.2%) and 32K warm 214.8 -> 186.3 ms (-13.3%). In one 399K profile, full-prefix gather calls dropped median 8835 -> 1093 us and total gather time 262.2 -> 32.4 ms.

**Promote:** live span must influence not only amount of work but launch geometry/latency hiding. This complements live-span-bounded QSA/DSA work; static graph shape does not justify static worker count.

## vLLM #56724 — probabilistic drafter should sample only from target top-k/top-p support

**FRESH NEW / SPECULATIVE ACCEPTANCE MECHANISM.**

For probabilistic drafting, proposing outside the target sampler's top-k/top-p support guarantees rejection. Restricting the drafter to the same support preserved the output distribution and increased accepted tokens/step by roughly 5-8%; pooled 72-round Qwen3.5 MTP output throughput improved +3.2% c1, +4.3% c8 and +2.8% c32. Greedy drafting is unchanged.

**Promote for sampled Flash/27B experiments:** acceptance comparisons must certify target/draft sampler support alignment, including temperature/top-k/top-p. Do not transfer CUDA percentage to Apple.

## vLLM #56734 — dummy speculative steps can silently poison cached drafter KV

**FRESH NEW / HIGH-VALUE SPECULATIVE PREFIX-CACHE CORRECTNESS.**

Idle DP dummy batches could resolve slot mappings through stale persistent block-table rows and write drafter K/V into blocks already present in prefix cache. Production GLM-5.2 repro showed per-request p0=0 acceptance and NaN drafter rows while target K/V stayed clean; resetting prefix cache removed the latch. Patched runs forced dummy mappings to PAD, including 66,164 dummy draft steps with no stale writes.

**Promote:** dummy/padding/warmup speculative execution must be side-effect free on all persistent state, including drafter-only KV. Read-side masking is insufficient; write addresses must be invalid/PAD too.

## llama.cpp #28805 — fresh 128K Flash-Next correctness data on M1 Max64

**FRESH COMMENT / DIRECT ACTIVE-HARDWARE CORRECTNESS EVIDENCE. Not a speed target receipt.**

Fresh exact-seed testing on M1 Max64 / qwen4exp / IQ4_XS / q4v4 / Metal FA found 82K and 98.5K clean retrieval, while ~131K behavior is prompt/seed dependent: one 130,937-token case passed 3/3 with a 2K output budget, while the same 131,220-token text remained bad even when budget increased. Under thinking-low the bad mode can be semantic/instruction-scope drowning rather than obvious one-token EOS.

The reporter now treats 64K as verified-correct and ~96K as non-shippable (2.5/3 across seeds). This strengthens the need for repeated semantic rulers at ~96K/128K, not just successful generation or HTTP status.

## llama.cpp #28871 / #28872 — QSA top-k and request-lifecycle overhead

**FRESH NEW / MECHANISM TRANSFER.**

#28871 replaces whole-row CUDA argsort with deterministic radix selection when CUB DeviceTopK is unavailable; sparse indexers with ncols up to 262K and k~2051 are the motivating shape. Example 262144x5: 2.12 ms -> 0.183 ms while matching deterministic argsort output. This is not evidence that our SM120 route executes this kernel, but reinforces exact top-k selection as a long-context hotspot and tie-order as execution identity.

#28872 finds llama-server was recreating its backend scheduler on every request; at 262K/-ub1024 that freed/reallocated ~512 MB pinned host input buffers. A 4-GPU Flash-Next layer-split continuation reportedly improved TTFT ~0.8-1.1 s -> 0.25-0.4 s by retaining/re-reserving the scheduler. Treat as request-lifecycle/allocator transfer, not Apple evidence.

---

# Recovered older evidence surfaced by the user — do not refresh timestamps

## oMLX #3614 — 64GB quant gap

The current oQ4e-mtp was measured from headers at ~106.3 GB total, ~74.3 GB non-PLE resident and ~32 GB PLE/ngram. That does not fit one 64GB Mac, motivating <=52 GB non-PLE oQ3. For our two 64GB Macs the non-PLE number is encouraging for PP2 capacity, but this is **capacity evidence only**; #3653 confirms distributed MTP is still rejected in stock distributed serving.

## llama.cpp #28213 / #28699 — QSA compact gather + incremental pooled indexer cache

Older but high-value mechanism evidence: #28213 gathers only selected QSA K/V rather than attending over a full-context mask and reported +50% at 130K on dual A6000; #28699 incrementally caches pooled indexer keys and reported ~+9.4% at 114K, including the lesson that pooled state should be allocated on the device/layer owner to avoid interconnect traffic. Percentages do not transfer to Apple.

---

# Fresh-screen negatives / non-promoted artifacts

- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No exact RTX5070Ti16 Qwen3.8-27B throughput receipt.
- No exact new dual-M1 DS4-0731 receipt.
- `antirez/ds4`: no in-window commits.
- Current web/HF screen surfaced an M1 Max64 Flash-Next REAP/MTP package claiming ~40.3 GB short-test peak with native MTP active, but it is explicitly a smoke test rather than a throughput benchmark and source timing is not clean enough to promote.
- vLLM #56722/#56723 are useful PCP/DCP + MTP/DFlash topology-enablement work but remain draft/in-progress validation; do not promote their throughput as active evidence.
- No P69 target/order change.

---

# Consequences for dual-M1 Flash-Next

1. Keep PP2/layer ownership primary and TP2 as control.
2. Treat Q4-class capacity as plausible on two 64GB nodes with PLE SSD, but **do not equate fit with distributed-MTP availability**.
3. Add a specific distributed Lightning-MTP enablement gate: proposal/head state ownership, verify across stage boundaries, rollback, sidecar cache, collectives and failure recovery.
4. Certify prefix cache as a state bundle: backbone KV + QSA/indexer + GDN/recurrent + PLE + MTP head history + pending hidden + committed boundary.
5. At 64K/~96K/~128K use repeated semantic retrieval/agent correctness, not only generated-token count/output hash.
6. Audit QSA for compact selected-K/V execution, incremental pooled-key state, exact/deterministic top-k and owner-local indexer state.
7. Context capacity must include executed-route prefill transient and actual chunk size, not KV alone.
8. Cache slot policy and allocator/scheduler lifecycle are first-token performance dimensions for agent workloads.

# Standing rules added/reinforced

- Fits in aggregate RAM != runnable target stack; feature mutexes and distributed capability gates are part of feasibility.
- Distributed MTP is a separate execution topology from ordinary PP serving and must be certified explicitly.
- Prefix-cache correctness is multi-state boundary correctness, not backbone-KV correctness alone.
- Dummy/warmup/padding speculative work must be write-side-effect-free.
- Sampler support alignment is part of speculative acceptance identity for non-greedy workloads.
- Sparse selection needs both bounded work and launch geometry appropriate to the live span.
- Planner capacity and runtime admission must share the same route-specific transient model.
- Semantic long-context correctness requires repeated seeds/prompts near the operating boundary; HTTP 200 / nonempty output is not a gate.
- Merge/crawl time does not refresh older evidence.
- Component gains do not move canonical targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
