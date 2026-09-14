# External runtime watch — 2026-09-14 00:07 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-14 00:57:57 UTC` through the user-request cutoff `2026-09-14 04:07:40 UTC`.

Evidence timestamp remains the substantive source timestamp, not crawl/rebase/merge-only churn. Older PRs that merely merged in this window are not refreshed.

**New hard source-freshness boundary for the next complete external search: `2026-09-14 04:07:40 UTC`.**

---

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured internal GDN/projection/downstream-tail evidence.**

Recent mlx-serve evidence still changes confidence rather than the target: 40 tok/s @ ~128K remains a credible success floor for a fully tuned dual-M1 implementation, while 50+ stays a stretch hypothesis until exact dual-M1 measurement exists.

---

# Fresh evidence

## mlx-serve `4b2ab272...` — iQ-MLX 3.3 bpw Flash-Next pack for 64 GB Macs

**FRESH NEW / FLASH CAPACITY-QUALITY TRADEOFF EVIDENCE.**

The new iQ-MLX pipeline streams one BF16 decoder layer at a time instead of materializing the ~360 GB source checkpoint, collects per-expert/per-linear activation statistics, and allocates expert quantization widths per layer under a byte budget.

The shipped `Qwen3.8-Flash-Next-MLX-Serve-iQ-MLX-3.3bpw` reports:

- **52 GB resident**;
- **85.6% top-1 agreement vs BF16** on 1,200 held-out positions;
- mixed-4/8-bit comparison: **89.1%** top-1 agreement.

This establishes a real single-64-GB capacity fallback, but the quality delta is visible. It is not a reason to abandon the higher-quality dual-M1 primary plan. The reusable lesson is the per-layer/per-role expert-width allocation methodology and served-model scoring against held-out BF16 logits.

## mlx-serve `cb477466...` — fused MoE decode admits 3-bit experts and improves the shared down-reduce path

**FRESH NEW / DIRECT APPLE FLASH MOE-DECODE MECHANISM RECEIPT.**

The 3.3-bpw pack put most expert layers at 3-bit, but the fused MoE decode kernels previously declined that physical quant width and fell back to stock `gather_qmm`. The new packed loader admits 3-bit expert weights into the fused path, while the expert down+reduce kernel changes from one full simdgroup per output row to 8 lanes per row with four rows reduced together.

Measured per-layer kernel time:

- 2/3/4-bit: **34 -> 24 us**;
- 8-bit: **43 -> 37 us**.

M4 Max, four alternated boots, MTP off:

- 3.3-bpw pack: **52.1 -> 56.5 tok/s**;
- mixed 4/8-bit pack: **54.3 -> 56.3 tok/s**;
- prefill unchanged.

The mixed-4/8 improvement matters most for us: the lane/reduction change transfers beyond the low-bpw contingency pack. Do not transfer the percentage to M1; promote the rule that configured quantization is not execution evidence until the desired fused kernel actually admits and executes that physical width/packing.

## mlx-serve `7de9af0f...` — dispatch grouped MTP draft work before verify-graph construction

**FRESH NEW / APPLE MULTI-REQUEST MTP SCHEDULING EVIDENCE.**

Grouped MTP built its draft chain lazily, so GPU draft work did not start until the deferred PLE flush waited on it, after the verify graph had already been built. A batched async evaluation now launches the draft graphs before verify construction so GPU work overlaps CPU graph building.

Reported effects:

- deferred-PLE wait: about **7 ms -> <1 ms per round**;
- four streams @128K, four counterbalanced boot pairs: **+2.6%, +3.3%, +1.1%, +0.8%**;
- 16K: +0.1% / +1.4%;
- one stream unchanged;
- 14/14 greedy parity cells byte-identical; EOS/cancellation gate passed.

This is not a single-request target receipt. Promote the scheduling lesson: lazy draft/verify work should be dispatched early enough to overlap graph construction, and PLE synchronization deserves explicit sub-lap telemetry.

## mlx-serve #421 — cold JIT can poison the learned MTP round-cost surface

**FRESH NEW / HIGH-VALUE MTP CALIBRATION + COMPILE-LIFECYCLE EVIDENCE.**

On a cold boot the first live MTP round at each width can pay Metal compilation inside the very measurement used to teach the planner. The PR reports first-round costs of **139–148 ms** versus **25–31 ms steady**. A pathological cold run could then remain stuck at one drafted token because the bad wide-width cells became trusted and were never revisited.

The proposed fix:

1. eagerly warms solo verify widths 1..cap, grouped verify row totals, and both MTP-head projection modes using throw-away KV/SSM/request state;
2. when a narrower cost cell becomes trustworthy, re-checks and drops implausible wider cells;
3. keeps long-context QSA arms out of load-time warmup because those need a large real KV and therefore require separate bucket qualification.

Measured first MTP round after the fix: about **25 ms**. Load-time cost is +1.1–1.4 s. End-to-end cold-boot throughput cells are noisy, so this is calibration evidence rather than a clean TG gain.

**Promote:** planner/cost-surface samples must disclose first-compile state. A kernel compile must not silently become the learned steady-state price of an execution width. Cost tables also need engine/build/physical-route identity and post-trust invalidation of stale neighboring cells.

## oMLX #3659 — target MoE geometry and MTP-head MoE geometry can differ

**FRESH NEW / CRITICAL MTP MODEL-GEOMETRY PROVENANCE.**

The Qwen4-Exp MTP module previously inherited the main model's expert counts. The new config adds MTP-specific `mtp_num_experts` and `mtp_num_experts_per_tok`, with the example of a main model using 384 experts while the embedded MTP head uses 512.

**Promote:** the MTP head is not necessarily a one-layer clone of target MoE geometry. Record target and proposal expert counts/top-k independently. Wrong inherited geometry can invalidate weight loading, routing, quantization dispatch, kernel selection, memory planning, and acceptance.

## llama.cpp #28873 — partial checkpoints were serializing reconstructible full draft KV

**FRESH NEW / SPECULATIVE CHECKPOINT-OWNERSHIP + TTFT TRANSFER.**

`LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY` was set for target and MTP draft checkpoints, but full-attention KV state ignored it. Every request therefore serialized and restored the draft model's entire KV cache even though rollback already uses `seq_rm` for that state.

Reported size: about **2 KB/token**, or **400–900 MB around 200K context**. On Qwen3.8-Flash-Next at 200K on a 4-GPU deployment, new-turn TTFT reportedly fell **3.5 s -> <1 s** after omitting the reconstructible full-attention KV from partial checkpoints; edited-history rewinds still restored correctly.

**Promote:** logical checkpoint completeness does not mean physically duplicating every state tensor. Persist irreconstructible state and explicit boundary metadata; let rollback/replay reconstruct state whose semantics already define that path.

## vLLM #56742 — Qwen4Exp MTP device placement, QSA classification and warmup dispatch

**FRESH NEW / ROUTE-PROVENANCE + WARMUP CORRECTNESS.**

Three bring-up bugs reinforce execution-identity discipline:

- the MTP hidden buffer was allocated without an explicit configured device;
- Transformers can serialize QSA layers as `qwen_sparse_attention`, while vLLM classification expected `full_attention`, potentially changing which layers execute QSA;
- Qwen4Exp was missing from the existing Qwen Triton warmup dispatch, so gated RMS, causal-conv, post-conv and decode-state kernels could compile on first use.

**Promote:** serialized config spelling -> normalized layer classification -> allocated physical device -> warmup route -> executed kernel is one provenance chain. Never infer QSA/MTP execution from model family alone.

## vLLM #56743 — DSV4.1 K=512 decode top-k needs shape-specific dispatch

**FRESH NEW / EXACT TOP-K SHAPE-SPECIALIZATION TRANSFER.**

DeepSeek-V4.1 uses K=512 for decode indexer selection, which missed an existing gfx950 tuning and fell back to a generic path. The ROCm-specific K=512 path uses device sequence lengths to select active splits while remaining valid under FULL graph replay, reduces `-inf` histogram contention and uses a smaller final sort.

Across 1,008 kernel matrix cases from 10K to 1M context and 1–6 speculative tokens:

- warm-graph geomean speedup: **2.310x**;
- 256-MiB cache-pressure geomean: **1.824x**;
- profiled GPU busy-time geomean: **2.291x**.

But two short serving repetitions showed no clear E2E throughput change, and the PR explicitly makes no serving-speed claim.

**Promote:** sparse top-k dispatch identity includes exact K, live rows/context and graph mode; kernel wins do not imply server wins.

## vLLM #56749 — sparse prefill top-k tie membership must be deterministic

**FRESH NEW / SPARSE-SELECTION DETERMINISM CORRECTNESS.**

Equal finite indexer scores could produce different selected compressed-context indices depending on how a row was batched. The proposed prefill selector uses stable value-descending / index-ascending order so an equal-score boundary always keeps the lower index.

Current branch validation is CPU-only; deployment evidence cited by the author is from a different tree and therefore remains supporting rather than current-main proof. No performance claim is made.

**Promote:** exact sparse-selection identity includes tie-break order. Batch-size/row-shape changes must not alter selected context under tied scores. Add batching/shape-invariance checks to long-context correctness qualification.

## vLLM #56752 — decoder-side SWA bounded replay

**FRESH NEW / STRONG BOUNDED-REPLAY ARCHITECTURE TRANSFER.**

For DSV4.1 layers after the final KV-source layer, the physical dependency is only a 128-token sliding window. The proposed decoder path therefore compacts each request to its trailing replay window after the source layer, executes later replay layers on those rows, then scatters results back to full-batch shape. It also trims an all-SWA DFlash/DSpark drafter's context-KV precompute to the same valid window.

The implementation explicitly disables the optimization where stage ownership, CP, adaptive-verification metadata, Engram placement or drafter SWA geometry make the replay contract unsafe. GSM8K on/off results are within run-to-run noise; there is no throughput receipt in the PR.

This reinforces the earlier bounded-replay principle: an expensive later phase need not forward the full history when its authoritative dependency is provably bounded, but metadata lifetime, physical stage ownership and speculative geometry are part of the safety proof.

## llama.cpp #28877 — fresh SM120 Qwen3.8 concurrent-long-prompt regression

**FRESH NEW / DIRECT SM120 ARCH-FAMILY CORRECTNESS WARNING.**

A new report on RTX 5090 Laptop (SM120 / compute capability 12.0) running Qwen3.8-27B with FA and two parallel slots reproduces a CUDA misaligned-address crash in the unary sigmoid path under concurrent ~3K–4K-token prompt processing. The reporter bisected a good older build against a bad newer range; lowering configured context did not avoid the crash.

This is **not** an RTX5070Ti receipt, but it is directly relevant architecture-family evidence because the 5070 Ti is also SM120.

**Promote for the 5070-Ti lane:** current-build qualification must include concurrent long-prompt soak, unary sigmoid/PDL route provenance and exact revision/driver tracking. “SM120 supported” is not enough to certify a current binary under real concurrency.

---

# Secondary fresh mechanisms / non-promoted performance

- llama.cpp #28874: in a multi-GPU split, synchronizing a user-input stream after a cross-device input had already attached a wait event could serialize host enqueue at every split boundary. Copying user inputs before cross-device inputs removes the stall. Retain as PP communication-order transfer; no active-lane receipt.
- llama.cpp #28875: tiny-N F32/F16 Qwen4Exp projections were dispatched to bulk cuBLAS paths; expanding vector-kernel eligibility reinforces exact-shape dispatch, but this is CUDA-only mechanism evidence.
- vLLM #56737: PCP compatibility checks must be scoped to target layers because the DFlash/DSpark draft can have a different physical CP layout. Target and draft physical topology are separate execution identities.
- vLLM #56750: sequence-parallel collective backend/cap policy is message-size dependent; useful transport-policy transfer, not Apple/TB4 percentage evidence.
- vLLM #56751: tiny-M decode projections benefit from shape-keyed skinny GEMM dispatch; reinforces P69-style shape specialization, not an active-topology receipt.
- vLLM #56738: initial V4.1 DCP correctness baseline, explicitly no serving-speed claim.
- Main-branch merges of older PRs do not refresh their evidence timestamps.

---

# Fresh-screen negatives

- No new exact **dual-M1 Flash-Next** TG/PP receipt.
- No new exact **M1 Max64 Qwen3.8-27B** receipt.
- No exact **RTX5070Ti16 Qwen3.8-27B** throughput receipt.
- No exact new **dual-M1 DS4-0731** receipt.
- External HF/Reddit screening resurfaced current Flash-Next quant packs and old M1/Apple receipts, but no source-time-qualified new active-topology benchmark in this window.
- `antirez/ds4` had no substantive post-boundary active-lane update inside this window; the V4.1 CUDA commit predates the boundary.
- No P69 target/order change.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Add/retain explicit gates:

1. target MoE geometry and MTP-head expert geometry recorded separately;
2. physical quant width/packing -> fused-kernel admission -> executed route, including 3-bit/mixed experts;
3. speculative cost surfaces measured only after relevant width/shape JIT is compiled, with stale cells revalidated;
4. long-context buckets qualified separately from load-time warmup;
5. checkpoint bundle remains logically complete while avoiding physical duplication of reconstructible KV;
6. sparse top-k tie policy stable under row/batch reshaping;
7. bounded replay only where physical stage ownership + metadata lifetime + drafter geometry certify it;
8. existing compact-QSA, prefix-sidecar, TB4, actual layer ownership, transient admission, lazy collective ordering and failure/reload gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement or sequencing change. **P69B12 frozen/promoted; P69B13 next.** Fresh work reinforces exact-shape dispatch, physical kernel admission and warm-JIT measurement discipline, but does not reorder the internal program.

## RTX5070Ti16

No target movement. Add a **current-build SM120 concurrent-long-prompt soak gate** because #28877 demonstrates a fresh Qwen3.8 SM120 device fault in an adjacent 50-series configuration. Track driver, commit, PDL/unary sigmoid route and concurrency explicitly alongside the existing physical-stride and executed-route gates.

## DS4-0731 dual M1

No target movement. DSV4.1 K=512/top-k and bounded-replay work transfer as mechanism/methodology only; later-model ROCm/CUDA percentages do not calibrate the 0731 Apple target.

---

# Standing rules added/reinforced

- MTP proposal-head expert geometry may differ from target MoE geometry; record both.
- First-use JIT/compile time must not silently become the learned steady-state price of a speculative width.
- Warmup identity includes widths, row totals, projection mode and physical kernel route; long-context-only kernels may need separate live-bucket qualification.
- Configured quantization is not execution evidence; record physical packing and whether the fused kernel actually admitted it.
- Logical checkpoint completeness does not require duplicating state that rollback/replay can deterministically reconstruct.
- Sparse top-k correctness includes deterministic tie-break order under batch reshaping.
- Architecture-family support does not certify a current build under concurrent long prompts; soak the exact binary/driver/runtime route.
- Kernel wins do not move server targets without active-topology E2E evidence.
- Merge/crawl time does not refresh older evidence.
- Requested/configured/planned remains distinct from built/available/admitted/executed.
- **P69 remains isolated.**
