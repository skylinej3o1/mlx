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
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1237.md` — newest complete delta: live-context-bounded sparse work, DFlash2 per-layer causality, DSpark candidate-pruned proposal head, MTP retained-history offload coverage, parallel JIT warmup, multimodal pre-prefill TTFT.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-0343.md` — dual-Mac failed-runtime recovery, exact rendered-context budgeting, SM120 physical-stride correctness, compiled speculative drafter evidence, producer-side norm/quant fusion.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-2300.md` — fused RMS/GDN verifier recurrence, expert-offload I/O/speculation economics, direct TB/RDMA cluster failure modes, shared physical host-cache ownership, speculative JIT warmup cardinality, draft-architecture provenance.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1735.md` — live-context-bounded DSA work, fused/graph-capturable prefill metadata, draft-config provenance, direct Flash-Next cluster PLE failure, 64-GB capacity/recovered REAP evidence.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1257.md` — GDN kernel-image route admission, device-authored adaptive metadata, no-forward KV-store lifecycle, coordinated long-prefill cancellation, recovered Flash-Next SP evidence.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1103.md` — V4.1 CED bounded-replay Apple prefill, ds4 V4.1 Metal support, device-authoritative speculative metadata.
9. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0313.md` — M1-targeted 27B DFlash2 FP16 candidate, proposal-head precision A/B, verifier-peak profiling, shared-expert padding/fusion.
10. Older 2026-09-11 / 2026-09-10 / 2026-09-09 notes remain retained for QSA/MTP, offload, PP/TP, recurrent rollback, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-13 07:43:32 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-13 16:37:16 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase, comment-only activity or merge-only churn. Resurfaced older evidence stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved in the 12:37 ET pass. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C from external evidence.**

---

# Newest directly relevant evidence — 2026-09-13 12:37 ET

## vLLM #56686 — live-context-bounded sparse work under graph capture

**FRESH NEW / HIGH-VALUE LONG-CONTEXT MECHANISM TRANSFER. Not active Apple-topology evidence.**

DeepSeek-V4.1-Flash on 8x B200 TP8 showed sparse candidate work and workspace scaling with the model's **1,048,576-token configured context**, not the batch's live sequence lengths. The experimental fix bounds work by live span behind graph-compatible static launch geometry, replaces full-width top-k with exact row-bounded selection, and buckets/prewarms arbitrary eager output-projection shapes.

Controlled 1000-request workload:

- **24.6 s / 18,040 tok/s -> 22.9 s / 19,390 tok/s (+7.4%)**;
- large-decode median **25.6 -> 22.2 ms**;
- single-request **6.2 -> 5.4 ms**;
- cited transient indexer buffer roughly **3.5 GB -> ~4 MB** for the large batch.

The same investigation found **3–3.6 s** first-seen DeepGEMM compile stalls for arbitrary eager prefill token counts.

**Promote:** static graph shape and dynamic live-work span are separate execution dimensions. Flash-Next/QSA/DSA certification must record configured max context, live span, workspace extent, touched span, candidate count, full-width reductions/top-k and first-seen JIT shape costs.

## vLLM #56692 — DFlash/DFlash2 per-layer causality correctness

**FRESH NEW / DIRECT DFLASH2 CONFIG-CORRECTNESS EVIDENCE.**

A Speculators converter could incorrectly apply a causal setting globally when only SWA layers should be causal; full-attention draft layers are trained bidirectionally within the draft block. Patched regression suite: **46 passed** versus **6 failures / 31 passes** unpatched in the newly covered cases.

B300 diagnostics with identical draft weights:

- short prompts: acceptance **3.026 -> 3.147**, throughput **2715.7 -> 2748.9 tok/s**;
- 16K prefix: acceptance **2.916 -> 3.078**, throughput **383.9 -> 393.7 tok/s**.

**Promote:** draft attention causality belongs in execution identity at per-layer granularity. DFlash acceptance/speed is not architecture evidence until masking semantics match the training contract.

## vLLM #56694 — candidate-pruned DSpark W2 projection

**FRESH NEW / SPECULATIVE-DRAFT MECHANISM TRANSFER.**

The DSpark Markov head restricts full-vocabulary W2 projection to a candidate union from top base logits and top Markov-bias candidates. Submitted Hopper sweeps report roughly **5–8% output-throughput gains** with little accepted-length loss; target verification/sampling remains authoritative.

**Promote as experiment idea only:** inspect draft/proposal paths for verifier-safe candidate pruning of full-vocabulary work. Do not transfer the reported percentage to M1 or Lightning MTP.

## vLLM #56709 — MTP retained-history / SWA offload coverage

**FRESH NEW / LONG-CONTEXT STATE-CORRECTNESS.**

KV offload could admit a hit using ordinary SWA coverage while MTP extra-retained tokens required an older block that lookup had not checked and the producer might not have stored. The fix aligns lookup, in-flight checks and producer reachability with `extra_retained_tokens`.

Focused regressions: **102 passed** patched; reverting the production fix produced **14 failures / 88 passes**. GPU smokes exercised rejected-draft re-prefill and identical cold/warm outputs.

**Promote:** speculative retained history outside the nominal window belongs to cache/store/restore identity. Lookup, storage, transfer ownership, restore and rejection/re-prefill must agree on the same retained span.

## vLLM #56683 — parallel compilation of independent warmup variants

**FRESH NEW / COMPILE-LIFECYCLE MECHANISM.**

Nine cold-cache DSV4.1 mHC variants compiled in **95.03 s sequentially vs 43.39 s with four compiler workers (2.19x isolated compile-stage speedup)**. A later real-weight TP4 startup compiled four remaining variants in parallel in ~14 s; no full-engine startup speedup is claimed.

**Promote:** after controlling warmup-key cardinality, compiler scheduling/worker count is another startup optimization dimension. Keep compile-key enumeration, serial elaboration, compile wall time, cache state and final engine startup separate.

## oMLX #3634 — multimodal long-agent TTFT before prefill

**FRESH MERGED / APPLE AGENT-RUNTIME EVIDENCE. Text-only lanes unaffected.**

Repeated historical screenshots were decoded again on every turn. A DeepSeek-V4.1 multimodal agent session around 200K context observed roughly **22 s of image decode before prefill**. The merged content-hash decoded-image cache makes decode proportional to unique images rather than cumulative history.

Real-server Mac Studio A/B over six cumulative-image turns showed roughly **21–35% TTFT reductions** and **86% fewer PNG decode chunks** in that run.

**Promote for agent benchmarking:** decompose TTFT into request/media decode, feature lookup/encode, KV restore, prefill, compile and first decode. Pre-model host work must not be attributed to PP/model kernels.

---

# Fresh-screen negatives / non-promoted current artifacts

- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No exact RTX5070Ti16 Qwen3.8-27B throughput receipt.
- No exact new dual-M1 DS4-0731 receipt.
- `antirez/ds4`: no in-window commits.
- `llama.cpp`: in-window SYCL/CI/Vulkan/general maintenance only; no relevant Metal/Qwen active-lane receipt promoted.
- Current web/HF screening surfaced Qwen3.8-Flash-Next oQ6/oQ8 artifacts and DFlash2 community/model pages, including stronger-hardware results, but source timing/topology did not establish a new post-boundary exact active-lane receipt.
- oMLX #3635 improves evaluation worker scheduling but does not change runtime throughput; keep as harness methodology.
- vLLM #56682 improves dummy/startup initialization behavior but does not provide an isolated active-lane throughput result.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Add:

1. graph-compatible **live-span-bounded** QSA/DSA/candidate work;
2. workspace extent vs actually touched span;
3. first-seen JIT shape detection and exact bucketing/prewarm;
4. MTP retained-history coverage across store/lookup/restore/rejection;
5. pre-model TTFT accounting for multimodal/agent workloads;
6. existing TB/RDMA, watchdog, failure/reload, helper ABI, PLE, verifier peak, pointer/state and long-context gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement and no P69 ordering change. DFlash2 experiments must certify **per-layer masking semantics** before acceptance/speed can be compared. DSpark candidate pruning is an external draft-side idea only. **P69B12 frozen/promoted; P69B13 next.**

## RTX5070Ti16

No target movement. Previous SM120 stride gate remains. This pass adds no exact 5070-Ti speed receipt. JIT-shape/warmup and draft-config lessons transfer only as methodology.

## DS4-0731 dual M1

No target movement. #56686 is later-V4.1/B200 mechanism evidence reinforcing live-context-bounded sparse work and JIT-shape accounting. #3634 is later-V4.1 Apple multimodal host-runtime evidence only.

---

# Standing rules added/reinforced

- Static graph geometry does not justify work over maximum configured context; certify dynamic live-work span and touched workspace.
- Draft masking/causality is per-layer execution identity unless the model contract proves a global setting.
- Draft-side full-vocabulary work may be candidate-pruned only with verifier-safe coverage and acceptance/correctness certification.
- MTP retained-history span is part of cache/store/restore identity even outside nominal SWA.
- Warmup-key cardinality and compiler scheduling are separate startup dimensions.
- TTFT includes host work before prefill.
- Merge/crawl time does not refresh older evidence.
- Requested/configured route remains distinct from built/available/admitted/executed route.
- Final-output correctness does not certify speculative correctness; acceptance/task quality remain separate.
- Component/kernel gains do not move canonical targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
