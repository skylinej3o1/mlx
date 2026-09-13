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
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-0343.md` — newest complete delta: dual-Mac failed-runtime recovery, exact rendered-context budgeting, SM120 physical-stride correctness, compiled speculative drafter evidence, producer-side norm/quant fusion.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-2300.md` — fused RMS/GDN verifier recurrence, expert-offload I/O/speculation economics, direct TB/RDMA cluster failure modes, shared physical host-cache ownership, speculative JIT warmup cardinality, draft-architecture provenance.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1735.md` — live-context-bounded DSA work, fused/graph-capturable prefill metadata, draft-config provenance, direct Flash-Next cluster PLE failure, 64-GB capacity/recovered REAP evidence.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1257.md` — GDN kernel-image route admission, device-authored adaptive metadata, no-forward KV-store lifecycle, coordinated long-prefill cancellation, recovered Flash-Next SP evidence.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1103.md` — V4.1 CED bounded-replay Apple prefill, ds4 V4.1 Metal support, device-authoritative speculative metadata.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0313.md` — M1-targeted 27B DFlash2 FP16 candidate, proposal-head precision A/B, verifier-peak profiling, shared-expert padding/fusion.
9. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0111.md` — Blackwell NVFP4-KV physical execution identity.
10. Older 2026-09-11 / 2026-09-10 / 2026-09-09 notes remain retained for QSA/MTP, offload, PP/TP, recurrent rollback, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-13 03:00:39 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-13 07:43:32 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase, comment-only activity or merge-only churn. Resurfaced older evidence stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved in the 03:43 ET pass. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C from external evidence.**

---

# Newest directly relevant evidence — 2026-09-13 03:43 ET

## oMLX #3631 — dual-Mac failed-runtime recovery

**FRESH NEW / DIRECT DUAL-MAC QWEN3.8 RELIABILITY EVIDENCE.**

A dead distributed worker could leave stale rank-zero `active_requests` state and permanently block reload. The proposed fix treats runtime failure, dead marker ownership, or marker error as terminal/quiescent and allows unload/reload. Validation includes 262 targeted tests and a live dual-Mac Qwen3.8 deployment.

**Promote:** certify `healthy -> failed -> quiescent -> unload -> reload -> healthy`; stale positive activity markers are not authoritative after terminal failure.

## oMLX #3632 — exact rendered prompt controls context capacity

**FRESH NEW / LONG-CONTEXT API-CORRECTNESS.**

Completion output is bounded by `effective_context - rendered_prompt_tokens`, and token counting now forwards the same chat-template/thinking controls used by generation. Live Qwen3.8-27B verification found `enable_thinking: false` rendered **40 fewer prompt tokens** than the old count route reported.

**Promote:** context identity includes the exact rendered template and controls; count route, admission and generation must agree.

## vLLM #56659 — SM120 FP8 physical-stride correctness

**FRESH NEW / DIRECT RTX5070Ti ARCH-FAMILY TRANSFER.**

The SM120 blockwise FP8 caller reconstructed packed strides from logical shape and corrupted padded/subview operands. RTX 5090 SM120 validation: baseline **24 padded-layout failures / 6 passes**; patched **30/30**, with full blockwise subset **53 passed**. The RTX 5070 Ti is also consumer Blackwell SM120 / compute capability 12.0.

**Promote:** physical leading strides are part of 5070-Ti kernel execution identity; packed-only microbenchmarks are insufficient.

## vLLM #56664 — speculative drafter compilation as a separate optimization surface

**FRESH NEW / SPECULATIVE COMPILE-FUSION TRANSFER.**

Compiling the Kimi-K3 DSpark drafter, with graph partitioning and MLA RoPE/KV fusion enabled, produced on 8x MI355X TP8/depth-3:

- interactivity p90 **144.82 -> 154.57 tok/s (+6.7%)**;
- p90 ITL **6.91 -> 6.47 ms (-6.4%)**;
- throughput/GPU **2043.29 -> 2057.70 (+0.7%)**.

**Promote:** target and drafter compile/fusion routes are independent execution dimensions. Record both, plus compile cost and warm steady state, in Lightning-MTP/DFlash experiments.

## vLLM #56674 — producer-side RMSNorm + MXFP8 quant fusion

**FRESH NEW / STRONG DSv4.1 MECHANISM TRANSFER.**

DeepSeek-V4.1-Flash shows roughly **187–198** adjacent activation-quant/GEMM pairs per decode step. Producer-side add+RMSNorm+quant fusion saves **2.2–4.1 µs per occurrence**, gives **1.49–1.77x** on the pair and about **~1% of decode-step time**. A GEMM-prologue fusion attempt measured only **0.28–0.89x** baseline and was rejected.

**Promote:** fusion placement must be measured; reuse a representation at the producer that already owns the data rather than assuming the GEMM prologue is optimal.

---

# Fresh-screen negatives / non-promoted current artifacts

- vLLM #56621 merged in-window, but its no-forward KV-store evidence was already recorded earlier; merge time does not refresh evidence.
- `jundot/omlx` main: no in-window commit; the fresh Apple work above is in open PRs.
- `antirez/ds4`: no in-window commit and no new exact dual-M1 0731 receipt.
- `llama.cpp`: in-window CI/Vulkan maintenance only; no new relevant Metal/Qwen throughput receipt.
- Current HF/community search surfaced M3-Ultra Qwen3.8-Flash-Next Q6/Q8 artifacts and a Sep-12 M4 Pro 64GB REAP-288 community claim around 30 tok/s near ~100K context, but source time is not post-boundary-qualified and neither is exact M1 topology. Keep as unpromoted/backfill context only.
- no new exact dual-M1 Flash-Next TG/PP receipt;
- no new exact M1 Max64 Qwen3.8-27B receipt;
- no exact RTX5070Ti16 Qwen3.8-27B throughput receipt;
- no exact new dual-M1 DS4-0731 receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Certification now explicitly includes:

1. terminal distributed failure -> quiescence -> reload without server restart;
2. exact rendered-prompt/context-budget identity;
3. producer-side fusion placement analysis;
4. target-vs-draft compile/fusion route separation;
5. existing helper ABI/environment, physical TB/RDMA interface, watchdog tolerance, live-context span, QSA workspace, verifier peak, PLE, MTP pointer/state and long-context gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement. #3632 strengthens long-agent/context correctness. #56664/#56674 are mechanism-transfer ideas only and do not change P69B13 ordering. **P69B12 frozen/promoted; P69B13 next.**

## RTX5070Ti16

No target movement. #56659 is high-value SM120 correctness transfer: test padded/subview A/B/output layouts, runtime leading strides, swap/transpose dispatch boundaries and untouched padding on the actual 5070 Ti.

## DS4-0731 dual M1

No target movement. #56674 is later-V4.1 ROCm mechanism transfer only; #3631 directly improves distributed recovery methodology.

---

# Standing rules added/reinforced

- Terminal distributed failure invalidates stale positive activity markers; recovery includes reload without server restart.
- Context-window identity is the exact rendered prompt plus template/thinking controls, not raw messages alone.
- Physical leading stride is part of kernel execution identity; logical shape is insufficient for padded/subview tensors.
- Target compilation and drafter compilation are separate speculative execution dimensions.
- Fusion placement must be measured; producer-side representation reuse may beat consumer/prologue fusion.
- Merge time does not refresh already-recorded evidence.
- Requested/configured route remains distinct from built/available/admitted/executed route.
- Final-output correctness does not certify speculative correctness; acceptance/task quality remain separate.
- Component/kernel gains do not move TG/PP targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
