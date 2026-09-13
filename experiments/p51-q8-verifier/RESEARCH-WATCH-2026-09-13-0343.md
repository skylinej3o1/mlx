# External runtime research watch — 2026-09-13 03:43 ET

## Search window

This pass covers substantive source activity strictly after `2026-09-13 03:00:39 UTC` through the user-request cutoff `2026-09-13 07:43:32 UTC`.

Evidence time means the substantive source timestamp, not crawl time, rediscovery, rebase-only activity, or a merge of evidence already recorded in an earlier watch.

## Canonical targets

No canonical target moves in this pass:

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | 40 tok/s @ ~128K active context | 400 tok/s | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | 25 tok/s | 110 tok/s native/exact-runtime | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | 120 tok/s | 250 tok/s | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | 15 tok/s | 180 tok/s | unchanged |

P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. No external result in this pass reopens P69B8/B9/B10-C.

---

## oMLX #3631 — failed distributed runtimes must become quiescent and reloadable

**FRESH NEW / DIRECT DUAL-MAC QWEN3.8 RELIABILITY EVIDENCE. Not a throughput receipt.**

A failed distributed worker could leave stale rank-zero marker state reporting positive `active_requests`, causing the coordinator to believe the deployment was still busy and reject a reload with HTTP 409. The proposed fix makes runtime failure, dead marker ownership, or marker error authoritative terminal evidence for quiescence and allows forced unload/reload of the failed engine.

Validation includes 262 targeted tests and a live deployment on a **dual-Mac cluster serving Qwen3.8**.

**Promote:** distributed liveness is a state machine, not a counter. Once a runtime is terminally failed, stale positive request counters must not retain ownership or block recovery. Certification should include `healthy -> failed -> quiescent -> unload -> reload -> healthy` under rank death, Metal watchdog failure, and disconnect.

This directly extends the TB4/PP2 reliability checklist from #3620/#3621/#3625.

---

## oMLX #3632 — output budget must use the exact rendered prompt and remaining context

**FRESH NEW / LONG-CONTEXT API-CORRECTNESS EVIDENCE. Not TG/PP evidence.**

The patch bounds chat completion output by `effective_context_window - rendered_prompt_tokens`, rejects explicit over-budget requests with exact remaining capacity, and forwards chat-template controls through Anthropic token counting so counting and generation use the same render path.

Live Qwen3.8-27B verification found that `enable_thinking: false` renders **40 fewer prompt tokens** than the existing count route reported when template controls were not forwarded.

**Promote:** long-context certification must define context against the exact rendered request, including thinking/template controls. Token-count route, scheduler admission, cache position, and generation must agree on the same prompt identity. A nominal 128K/262K context limit is not sufficient if the control-plane count is based on a different template.

---

## vLLM #56659 — SM120 blockwise FP8 GEMM must honor physical leading strides

**FRESH NEW / DIRECT RTX 5070 Ti ARCH-FAMILY CORRECTNESS TRANSFER. Not a 5070 Ti speed receipt.**

The SM120 blockwise FP8 CUTLASS caller reconstructed packed strides from logical shape and therefore read padded tensor views with the wrong leading stride. RTX 5090 / SM120 validation covered M=3/64/128, BF16/FP16 output, and packed/padded A/B/output layouts:

- baseline padded layouts: **24 failed / 6 passed**;
- patched: **30/30 passed**;
- full blockwise subset after patch: **53 passed**;
- example baseline corruption ranged from 66.7% mismatched elements to ~99.7%, with max absolute difference 152.

The RTX 5070 Ti is also consumer Blackwell **SM120 / compute capability 12.0**, so this is unusually direct architecture-family evidence for our 5070 Ti lane even though the measured board was a 5090.

**Promote:** kernel execution identity includes runtime physical strides, not just logical M/N/K, dtype and quant format. Certification for the 5070 Ti must include packed vs padded/subview operands and outputs, both sides of swap/transpose dispatch thresholds, and untouched padding checks.

---

## vLLM #56664 — compile the speculative drafter as its own optimization surface

**FRESH NEW / SPECULATIVE COMPILE-FUSION TRANSFER. Not Qwen/Apple evidence.**

Kimi-K3 DSpark's draft model was compile-free. Enabling `torch.compile` for the drafter allowed Inductor graph partitioning and MLA RoPE/KV-cache fusion while leaving the target model scope unchanged.

8x MI355X TP8, concurrency 1, speculative depth 3, FP8 KV, synthetic accepted length 3.75:

- interactivity p90: **144.82 -> 154.57 tok/s (+6.7%)**;
- p90 ITL: **6.91 -> 6.47 ms (-6.4%)**;
- throughput/GPU: **2043.29 -> 2057.70 tok/s (+0.7%)**.

The experiment changes both compile admission and the enabled fusion config, so the delta belongs to the compiled-draft path as a whole, not the decorator alone.

**Promote:** target compile state and drafter compile state are independent execution dimensions. For Lightning-MTP/DFlash2 experiments, record target compiled route, draft compiled route, graph/fusion set, first-compile cost, and warm steady state separately. Drafter-only fusion can materially improve interactive latency even when aggregate throughput moves little.

---

## vLLM #56674 — fuse quantization at the producer when the required representation already exists

**FRESH NEW / STRONG DSv4.1 KERNEL-MECHANISM TRANSFER. Not Apple evidence.**

DeepSeek-V4.1-Flash on MI355X executes roughly **187–198** standalone MXFP8 activation-quantize/GEMM pairs per decode step, adjacent 100% of the time. The producer is usually fused add+RMSNorm, and AITER can emit exactly the FP8 values + per-32 scale representation the GEMM consumes.

Producer-side norm+quant fusion reports:

- **2.2–4.1 µs saved per occurrence**;
- **1.49–1.77x** speedup for the norm+quant pair;
- about **~1% of total decode-step time** at ~190 occurrences.

A first attempt to move quantization into the GEMM prologue was explicitly rejected after measuring **0.28–0.89x** baseline because the reshape/reduction cost overwhelmed the saved launch.

**Promote:** fusion placement matters. Prefer the earliest producer that already owns/materializes the needed representation; do not assume a consumer/GEMM prologue is optimal merely because it reduces launch count. For Flash/P69-style work, trace where normalization/projection/quant data are already resident before designing the fusion boundary.

---

## Merge-only and screened items

- vLLM #56621 merged during this window, but its no-forward CPU-KV-store lifecycle evidence was already recorded in the 12:57 ET watch. Merge time does not reset evidence freshness.
- llama.cpp had in-window CI/Vulkan maintenance; no new active-lane Metal/Qwen throughput receipt.
- antirez/ds4 had no in-window commit.
- jundot/omlx main had no in-window commit; the relevant new Apple evidence above remains in open PRs.
- Current HF/community search surfaced Qwen3.8-Flash-Next Q6/Q8 artifacts on M3 Ultra and a Sep-12 M4 Pro 64GB REAP-288 community claim around 30 tok/s decode near ~100K context. Their substantive timestamps are not post-boundary-qualified, and neither is our exact M1 topology, so they are not promoted as fresh evidence in this pass.
- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No exact RTX5070Ti16 Qwen3.8-27B throughput receipt.
- No exact new dual-M1 DS4-0731 receipt.

---

## Current consequences by lane

### Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Add:

1. terminal distributed failure -> quiescence -> reload certification;
2. exact rendered-prompt/context-budget identity;
3. producer-side fusion placement analysis before adding consumer/prologue fusion;
4. target and drafter compile/fusion routes as separate execution identities;
5. existing transport, watchdog, helper ABI, live-context work-span, QSA workspace, verifier-peak, PLE, MTP pointer/state, and long-context gates.

No target movement.

### Qwen3.8-27B M1 / P69

No target movement and no P69 branch movement. #3632 matters to long-agent/context correctness. #56664/#56674 are mechanism-transfer ideas only; they do not alter P69B13 ordering.

### RTX5070Ti16

No target movement. #56659 is high-value architecture-family correctness evidence: physical tensor strides/padded views must be part of any SM120 FP8/NVFP4 kernel certification. This should be tested explicitly on the actual 5070 Ti before trusting packed-only microbenchmarks.

### DS4-0731 dual M1

No target movement. #56674 reinforces producer-side fusion methodology; later V4.1 ROCm remains mechanism transfer only. #3631 directly improves dual-node recovery methodology.

---

## Standing rules added/reinforced

- Terminal distributed failure invalidates stale positive activity markers; recovery correctness includes reload without server restart.
- Context-window identity is based on the exact rendered prompt and template/thinking controls, not only raw message tokens.
- Physical leading stride is part of kernel execution identity; logical shape alone is insufficient for padded/subview tensors.
- Target compilation and drafter compilation are independent speculative execution dimensions.
- Fusion placement must be measured; producer-side representation reuse can beat GEMM-prologue fusion even when both remove a launch.
- Merge time does not refresh previously recorded evidence.
- Requested/configured route remains distinct from built/available/admitted/executed route.
- Final-output correctness does not certify speculative correctness; acceptance/task quality remain separate.
- Component/kernel gains do not move TG/PP targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**

## Next hard source-freshness boundary

`2026-09-13 07:43:32 UTC`
