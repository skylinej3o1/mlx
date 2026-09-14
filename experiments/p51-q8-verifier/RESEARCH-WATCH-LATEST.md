# Latest external runtime watch

## Active scope

Research remains centered on:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**
- **Qwen3.8-27B — one M1 Max 64 GB**
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**
- **Blazer / custom ~5.x-BPW execution work** where evidence transfers cleanly

Do not maintain a dedicated future M5/M5-Ultra lane unless explicitly reopened. Stronger-Apple evidence remains transfer/mechanism evidence unless it reproduces an active topology.

---

## Read order for the next research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-2057.md` — newest complete delta: generated-prefix MTP history, SDPA transient capacity, distributed-MTP constraint, multi-slot coherent prompt cache, expert-major offload prefill, live-length gather geometry, sampler-support-aligned drafting, dummy-draft KV poisoning, fresh M1 128K correctness, QSA top-k/request-lifecycle mechanisms, recovered #3614/#28213/#28699.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1533.md` — TB routable-address discovery, executed PP ownership, live memory admission, lazy-send/collective ordering, internal prefill checkpoints, DCP interleave mapping, EPLB warmup isolation.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1237.md` — live-context-bounded sparse work, DFlash2 per-layer causality, DSpark candidate-pruned proposal head, MTP retained-history offload coverage, parallel JIT warmup, multimodal pre-prefill TTFT.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-0343.md` — dual-Mac failed-runtime recovery, exact rendered-context budgeting, SM120 physical-stride correctness, compiled speculative drafter evidence, producer-side norm/quant fusion.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-2300.md` — fused RMS/GDN verifier recurrence, expert-offload I/O/speculation economics, direct TB/RDMA cluster failure modes, shared physical host-cache ownership, speculative JIT warmup cardinality, draft-architecture provenance.
8. Older 2026-09-12 / 2026-09-11 / 2026-09-10 / 2026-09-09 notes remain retained for QSA/MTP, offload, PP/TP, recurrent rollback, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-13 19:33:05 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-14 00:57:57 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase, comment-only activity or merge-only churn. Resurfaced older evidence stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved in the 20:57 ET pass. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C from external evidence.**

---

# Newest directly relevant evidence — 2026-09-13 20:57 ET

## oMLX #3647 — generated-prefix MTP head history

**FRESH NEW / HIGH-VALUE FLASH-MTP PREFIX-CACHE CORRECTNESS.**

Generated tokens could enter the backbone prefix cache without matching MTP head history. The proposed sidecar captures a detached head cache plus pending normalized hidden row at committed full-block boundaries and trims the preceding speculative chain before the confirmed fold. Focused suites report 337 passes + 3 skips; full Qwen4 repeated-prompt qualification remains pending.

**Promote:** prefix-cache identity under MTP includes backbone state + head-history boundary + pending hidden row + rollback state at one committed token boundary.

## oMLX #3651 — route-specific SDPA transient belongs in context capacity

**FRESH NEW / DIRECT 2x64 GB LONG-CONTEXT CAPACITY EVIDENCE.**

A real 2x64 GB pipeline was signed for 425,984 tokens but rank 0 rejected above ~320K because runtime admission charged an unfused head-dim-256 fp32 SDPA transient omitted by the planner: ~24.25 GB `KV+SDPA` versus 8.7 GB pure KV at 320K.

**Promote:** planner and runtime admission must share the same executed attention route, chunk size and transient formula. Aggregate RAM/KV-only arithmetic is insufficient.

## oMLX #3653 — distributed Lightning MTP remains a real blocker

**FRESH NEW / CRITICAL ACTIVE-PLAN CONSTRAINT.**

The MTP-compatible Qwen3.5 model patch is being made pipeline-aware for ordinary distributed serving, but the PR explicitly states that **distributed MTP remains rejected elsewhere**.

**Promote:** dual-M1 Q4 capacity plausibility does not mean PP2 + Lightning MTP works stock. Distributed speculative execution remains a separate enablement/certification workstream.

## oMLX #3655 — coherent multi-slot distributed prompt cache

**FRESH NEW / DIRECT LONG-AGENT DISTRIBUTED EVIDENCE.**

The tuner silently forced `prompt_cache_size=1`, so interleaved traffic could evict the active conversation and trigger full re-prefill; the field report cites ~110 s at ~45K tokens. Proposed fix keeps byte-based eviction disabled for cross-rank correctness but honors deterministic count-based LRU slots.

## oMLX #3654 — expert-major offload prefill

**FRESH NEW / OFFLOAD CONTINGENCY.**

Sorting/chunking by expert instead of token range removes repeated expert refetch churn. At 12.5% residency, a 585-token Gemma-4 prompt went 64,369 -> 2,913 expert fetches and warm TTFT 16.60 -> 0.97 s. Decode unchanged. Useful if expert offload is ever used, but not a reason to abandon the primary full-resident/MTP Flash plan.

## vLLM #56720 — live gather length should determine launch geometry

**FRESH NEW / STRONG LONG-CONTEXT SPARSE-PREFILL TRANSFER.**

DeepSeek-V4.1 compressed-KV gather improved 131K warm-cache prefill 446.9 -> 320.8 ms (-28.2%) by sizing worker count from live gather length; a 399K profile reduced full-prefix gather calls from median 8835 -> 1093 us. Static graph geometry and static worker count are separate choices.

## vLLM #56724 — draft inside target top-k/top-p support

**FRESH NEW / SPECULATIVE ACCEPTANCE MECHANISM.**

For probabilistic drafting, restricting proposals to the target sampler's top-k/top-p support preserved distribution, raised accepted tokens/step ~5-8%, and improved pooled Qwen3.5 MTP output throughput ~2.8-4.3% depending concurrency. Greedy unaffected. Transfer the sampler-alignment rule, not the CUDA percentage.

## vLLM #56734 — dummy draft steps can poison persistent drafter KV

**FRESH NEW / HIGH-VALUE SPECULATIVE CACHE CORRECTNESS.**

Idle dummy batches could resolve stale persistent block-table rows and write drafter KV into prefix-cached blocks. Production GLM-5.2 repro showed p0=0 acceptance with NaN drafter rows while target KV stayed clean. Forcing dummy slot mappings to PAD removed the writes; one validation logged 66,164 dummy draft steps all PAD.

**Promote:** dummy/padding/warmup paths must be write-side-effect-free on drafter-only persistent state, not merely read-masked.

## llama.cpp #28805 — fresh M1 Max64 long-context correctness

**FRESH COMMENT / DIRECT ACTIVE-HARDWARE CORRECTNESS EVIDENCE.**

Fresh exact-seed qwen4exp tests show clean retrieval at 82K and 98.5K but prompt/seed-dependent ~131K failures; under thinking-low the bad mode can look like semantic/instruction-scope drowning rather than instant EOS. Reporter treats 64K as verified-correct and ~96K (2.5/3 across seeds) as non-shippable.

**Promote:** Flash 128K ruler needs repeated semantic probes near 96K/128K; HTTP 200/nonempty output is not correctness evidence.

## llama.cpp #28871 / #28872 — sparse top-k + allocator lifecycle transfer

#28871 replaces whole-row argsort with deterministic radix selection for long-context sparse top-k when DeviceTopK is unavailable; example 262144x5/k2051 2.12 -> 0.183 ms. Route execution on our 5070 Ti is not established.

#28872 finds per-request scheduler recreation caused large buffer realloc/page-fault warmup; on a 4-GPU Flash-Next layer split TTFT reportedly moved ~0.8-1.1 s -> 0.25-0.4 s by retaining/re-reserving the scheduler. Treat as lifecycle transfer, not Apple evidence.

---

# Recovered older evidence — timestamp retained

- **oMLX #3614:** oQ4e-mtp measured ~106.3 GB total, ~74.3 GB non-PLE resident, ~32 GB PLE/ngram. Supports PP2 capacity plausibility on two 64GB nodes, but #3653 prevents conflating capacity with distributed-MTP availability.
- **llama.cpp #28213:** compact gathered QSA K/V instead of full-context masked attention; reported +50% at 130K on dual A6000. Mechanism only.
- **llama.cpp #28699:** incremental pooled QSA indexer cache; reported ~+9.4% at 114K and showed pooled state should live on its device/layer owner to avoid interconnect traffic. Mechanism only.

---

# Fresh-screen negatives / non-promoted current artifacts

- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No exact RTX5070Ti16 Qwen3.8-27B throughput receipt.
- No exact new dual-M1 DS4-0731 receipt.
- `antirez/ds4`: no in-window commits.
- Current web/HF screening surfaced an M1 Max64 Flash-Next REAP/MTP package reporting ~40.3 GB short-test peak and native MTP active, but it explicitly is not a throughput benchmark and source timing is not clean enough to promote.
- vLLM #56722/#56723 are topology-enablement drafts for PCP/DCP + MTP/DFlash; validation is still in progress.
- No P69 target/order change.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Add/retain:

1. explicit distributed-Lightning-MTP enablement gate; stock distributed serving still rejects MTP;
2. prefix-cache bundle identity: backbone KV + QSA/indexer + GDN/recurrent + PLE + MTP head history + pending hidden + committed boundary;
3. route-specific SDPA prefill transient in capacity planning;
4. coherent count-based prompt-cache slots with byte eviction disabled;
5. repeated 64K/~96K/128K semantic correctness ruler;
6. audit compact selected-K/V QSA, incremental pooled indexer state, deterministic exact top-k and owner-local state;
7. dummy/warmup speculative write isolation;
8. existing TB/RDMA, actual layer ownership, live memory ceiling, lazy collective ordering, recurrent checkpointing, live-span/workspace and failure/reload gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement. Sampler-support alignment is worth checking only for non-greedy MTP experiments; it does not alter the frozen P69 order. **P69B12 frozen/promoted; P69B13 next.**

## RTX5070Ti16

No target movement. #28871 reinforces exact/deterministic sparse top-k as a possible long-context hotspot, but the executing SM120 route is not established. Existing SM120 stride/executed-route gates remain.

## DS4-0731 dual M1

No target movement. #56720 is later-V4.1/ROCm mechanism transfer; oMLX capacity/cache/distributed-state lessons transfer to the dual-Mac methodology.

---

# Standing rules added/reinforced

- Fits in aggregate RAM != runnable target stack; feature mutexes/distributed capability gates are feasibility dimensions.
- Distributed MTP is a distinct execution topology and must be certified separately from ordinary PP.
- Prefix-cache correctness is multi-state committed-boundary correctness, not backbone-KV correctness alone.
- Dummy/warmup/padding speculative work must be write-side-effect-free.
- Sampler support alignment is speculative execution identity for non-greedy workloads.
- Sparse selection needs bounded work **and** launch geometry appropriate to the live span.
- Planner capacity and runtime admission must share the executed route's transient model.
- Semantic long-context correctness needs repeated probes near the operating boundary.
- Merge/crawl time does not refresh older evidence.
- Requested/configured/planned remains distinct from built/available/contracted/admitted/executed.
- Component/kernel gains do not move canonical targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
