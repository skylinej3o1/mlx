# Research watch delta — 2026-09-12 03:13 ET

## Scope and freshness

Starting project checkpoint: `94cf59945d9fcc2aa06547467bc1883bfb522399` on `project51-q8-verifier`.

Previous hard source-freshness boundary: `2026-09-12 05:11:02 UTC`.

This pass screens substantive source activity through the user's request at `2026-09-12 07:13:21 UTC` and also admits one user-supplied older checkpoint as a targeted experiment candidate. Rediscovery, crawler time, rebases, and later comments do not make older measurements fresh.

**Hard source-freshness boundary for the next complete external search: `2026-09-12 07:13:21 UTC`.**

Evidence classes remain separate:

- exact-target measured receipt;
- transfer / mechanism evidence;
- experimental A/B candidate;
- planning target.

P69 is isolated from this external-research pass.

---

## Canonical targets — unchanged

| Model / hardware | Working TG | Status | Working cold PP | Status |
|---|---:|---|---:|---|
| **Qwen3.8-Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | planning objective | **400 tok/s** | planning objective |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | working target | **110 tok/s native/exact-runtime** | working target |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | working target | **250 tok/s** | working target |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | working target | **180 tok/s** | working target |

No target moves in this pass.

---

# 1. Qwen3.8-27B DFlash2 FP16 drafter — newly admitted M1 experiment candidate

Source: `deepsweet/Qwen3.8-27B-DFlash2-FP16`

https://huggingface.co/deepsweet/Qwen3.8-27B-DFlash2-FP16

**BACKFILL / USER-SUPPLIED EXPERIMENTAL CANDIDATE. Not a fresh post-boundary receipt. Not target evidence.**

The checkpoint is the Qwen3.8-27B DFlash2 drafter converted from the original BF16 `z-lab/Qwen3.8-27B-DFlash2` to FP16. It is a small ~2B drafter rather than a second 27B target. The model card explicitly positions the FP16 conversion as an M1/M2 Apple-Silicon optimization and recommends the original BF16 drafter for M3+.

This is unusually well aligned with our **single M1 Max64 Qwen3.8-27B lane**, but there is still no direct Qwen3.8-27B/M1 Max receipt proving it wins. The correct treatment is a controlled A/B candidate.

Older oMLX evidence from `jundot/omlx#880` supports the mechanism: on an M1/M2-oriented Qwen3.6 DFlash path, an FP16 drafter materially outperformed the BF16 drafter at short/medium contexts, while the benefit collapsed by 32K. That older result is transfer evidence only and must not be projected numerically onto Qwen3.8-27B.

### Promote to the M1 27B test matrix

Matched arms:

1. plain Qwen3.8-27B;
2. stock BF16 `z-lab/Qwen3.8-27B-DFlash2`;
3. `deepsweet/Qwen3.8-27B-DFlash2-FP16`.

Initial context cells: **4K / 16K / 32K**. Extend to **64K / 128K** only if the FP16 arm remains profitable and stable.

Hold target checkpoint/quant, prompt/token IDs, sampling, seed, output budget, cache state and runtime constant. Record:

- target TG and end-to-end wall time;
- TTFT / PP separately;
- draft acceptance rate and mean acceptance length;
- draft/proposal latency or tokens proposed per step where exposed;
- peak/resident memory;
- actual draft dtype and executed DFlash2 route;
- final-output/task-quality checks.

**Promotion rule:** prefer the FP16 drafter only if it improves end-to-end decode while preserving acceptance/task quality. A faster drafter with lower acceptance is not automatically a win.

This does not change the M1 27B `25 TG / 110 PP` target and does not alter P69.

---

# 2. Qwen3.8-Flash-Next FP8 proposal head — vLLM #56577

Source: https://github.com/vllm-project/vllm/pull/56577

Created `2026-09-12 06:38:57 UTC`.

**FRESH / STRONGER-HARDWARE FLASH MECHANISM TRANSFER. Not dual-M1 target evidence.**

The PR separates **proposal-head precision** from **target-verifier precision** for Qwen4Exp/MTP: the target keeps its BF16 vocabulary head while proposal projection uses a private rowwise-E4M3 copy.

Full-model validation used two DGX Spark GB10 nodes, TP2, Model Runner V2, eager MTP4, BF16 KV and `nvidia/Qwen3.8-Flash-Next-NVFP4`.

Measured serving A/B:

| GDN route | BF16 proposal head | FP8 proposal head | change |
|---|---:|---:|---:|
| default FlashInfer | 63.075 tok/s | 71.2475 tok/s | **+12.96%** |
| explicit Triton | 62.148 tok/s | 72.359 tok/s | **+16.43%** |

A token-capture run measured 63.130 -> 69.317 tok/s (**+9.80%**) while acceptance changed only 0.7823 -> 0.7781. The FP8 proposal copy added about **318 MB/rank** and reduced effective KV capacity somewhat. Single-run task checks were mixed: GSM8K moved -0.30 pp while AIME25 moved +3.33 pp, so the PR correctly does not claim quality equivalence.

### Durable promotion

Draft-side / proposal-side precision is an independent execution-identity dimension. For speculative paths record separately:

- target-verifier head precision;
- drafter/proposal head precision;
- proposal activation precision/scaling;
- ownership/lifetime of any private derived head;
- memory cost and resulting KV-capacity change;
- acceptance rate/length and task quality.

This strongly supports our broader mixed-precision/Blazer thesis: **do not force the verifier and proposal path to share one precision policy**. It does not imply FP8 is appropriate on M1 Metal, nor does it move the dual-M1 Flash target.

---

# 3. Speculative-verifier peak-memory profiling — vLLM #56572

Source: https://github.com/vllm-project/vllm/pull/56572

Created `2026-09-12 06:23:02 UTC`.

**FRESH / MEMORY-ADMISSION AND PROFILING TRANSFER.**

The triggering failure was an intermittent Gemma4 MTP OOM while allocating another **1.33 GiB** for logits soft-capping. The investigation exposed a more general MRV2 profiling gap: startup profiling sampled only up to **1,024 logits rows**, while runtime speculative verification reached **2,721 rows**.

The patch both removes an avoidable full-vocabulary temporary and profiles speculative target-verification rows before KV-cache sizing, using the real sampling/rejection path so TP projection, sharding and communication are represented.

### Durable promotion

Our admission/certification model must include a **spec-verifier peak-shape phase**, not just nominal prefill/decode shapes. Record:

- maximum physical verifier rows under the configured speculative width and batch limits;
- full-vocabulary temporary ownership and lifetime;
- sampling/rejection route used during profiling;
- TP projection/sharding/communication buffers where applicable;
- profile shape versus maximum runtime shape;
- whether adaptation after startup is bounded and memory-safe.

A startup profile that is smaller than the reachable runtime verifier shape is not valid capacity proof. This extends the existing QSA workspace/live-vs-retained-memory discipline.

---

# 4. Shared-expert physical padding and fusion — vLLM #56568

Source: https://github.com/vllm-project/vllm/pull/56568

Created `2026-09-12 06:07:56 UTC`.

**FRESH / LATER-DEEPSEEK GPU MECHANISM TRANSFER. Not DS4-0731 target evidence.**

DeepSeek-V4.1-Flash uses a logical MoE intermediate size of 2304. Routed experts were already physically padded to 2560 for the native MegaMoE path, but the shared expert retained checkpoint geometry and therefore forced all 40 layers onto a separate shared-MLP fallback. Padding the shared gate/up and down-projection geometry with zero weights/unit scales enabled the fused route.

On 8x B200 TP8/EP, the fresh implementation A/B reported:

| fixed batch | serial shared | fused shared | change |
|---:|---:|---:|---:|
| 1 | 96.3 tok/s | 107.1 tok/s | **+11.2%** |
| 16 | 715.0 tok/s | 814.6 tok/s | **+13.9%** |
| 64 | 1212.3 tok/s | 1397.3 tok/s | **+15.3%** |

The fused path cost about **+1.87 GiB/rank** model-load memory. GSM8K flexible extraction was essentially flat in the reported paired run; the authors do not claim broad numerical equivalence.

### Durable promotion

For MoE / Blazer execution identity, distinguish:

- checkpoint logical expert dimensions;
- physical padded dimensions used by the kernel;
- routed-expert versus shared-expert padding policy;
- scale values in padded lanes;
- requested versus actually fused route;
- extra resident/load memory caused by padding;
- tail occupancy and tile geometry.

Logical checkpoint compatibility does not prove that a shared expert takes the intended fused physical route.

For DS4-0731 this is mechanism-only: later architecture, CUDA/B200 and different topology. No DS4 target movement.

---

# Secondary provenance signal — vLLM #56571

PR #56571 adds logging for the **resolved** KV dtype when the user requested `auto`. This is a small observability change, but it independently reinforces the existing rule that requested/configured dtype is not sufficient evidence. Keep physical/resolved KV dtype in benchmark provenance.

No target impact.

---

# Fresh-screen negative results

- `jundot/omlx` main had **no post-boundary commits** through this cutoff. Post-boundary PR activity was dominated by UI/i18n and unrelated API work; no new exact M1/Qwen3.8 runtime receipt appeared.
- `antirez/ds4` had **no post-boundary commits**; no fresh DS4-0731 receipt.
- `llama.cpp` had post-boundary commits, but the screened changes were SYCL/OpenCL/RPC/server maintenance rather than new Metal/Qwen active-lane measurements.
- No new exact dual-M1 Flash-Next rate.
- No new exact M1 Max64 Qwen3.8-27B rate.
- No new exact RTX5070Ti16 canonical-topology rate.
- No new exact dual-M1 DS4-0731 rate.

---

# Consequences by active lane

## Qwen3.8-27B — M1 Max64

`deepsweet/Qwen3.8-27B-DFlash2-FP16` is now the primary **experimental drafter candidate** to compare against the stock BF16 DFlash2 drafter. It is not a target receipt.

**P69 remains untouched:** P69B12 frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail structure. Do not reopen P69B8/B9/B10-C.

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary, TP2 control. Add to certification:

- proposal/draft head precision separately from target verifier precision;
- private proposal-head memory/KV-capacity tradeoff where applicable;
- maximum physical verifier-row shape during admission profiling;
- speculative sampling/rejection temporary lifetime.

The GB10 FP8 proposal result is transfer evidence only.

## Blazer / custom ~5.x BPW

Execution identity now explicitly includes:

- verifier versus drafter/proposal precision policy;
- proposal-head private derived storage/lifetime;
- logical versus physically padded routed/shared expert geometry;
- padded-lane scale semantics;
- actual fused/fallback route;
- verifier peak rows and temporary-buffer lifetime.

## RTX5070Ti16

No target move. Previous consumer-Blackwell KV physical-format provenance remains required. #56577 is useful speculative-precision transfer but not a 5070 Ti measurement.

## DS4-0731 dual M1

No target move. #56568 reinforces physical shared/routed-expert geometry and fused-route provenance only; later V4.1 CUDA/B200 rates are not DS4 evidence.

---

# Standing rules retained

- Benchmark cell = actual executed route, not requested flags.
- Context is part of target identity.
- Final-output correctness is not sufficient speculative correctness.
- Track acceptance rate/length and task quality independently.
- Requested/configured precision is not physical/executed precision.
- Memory provenance includes load/materialization transients, live tensors, allocator-retained workspace, private derived speculative weights and verifier temporaries.
- Structural physical geometry includes layout, packing, padding, tile/tail occupancy and fused-route admission.
- Component gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
- **No dedicated future M5/M5 Ultra performance lane unless explicitly reopened.**
