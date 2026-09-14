# External runtime watch — 2026-09-14 18:42 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-14 19:17:07 UTC` through the user-request cutoff `2026-09-14 22:42:15 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, comment-only activity, or a later merge of already-known measurements.

**New hard source-freshness boundary for the next complete external search: `2026-09-14 22:42:15 UTC`.**

Cutoff edge intentionally excluded: vLLM #56908 was created at `2026-09-14 22:49:17 UTC`, about seven minutes after this cutoff. Examine it first on the next complete pass.

---

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured internal GDN/projection/downstream-tail evidence.**

---

# Fresh evidence

## mlx-serve `008dbfdf` — persistent ds4 session + embedded MTP for Flash-Next GGUF

Source commit `008dbfdf3bc7c649512291751a9a8decb9517942`, committed `2026-09-14 21:38:42 UTC`.

**FRESH MAIN-COMMIT / DIRECT APPLE FLASH STATE-LIFETIME + EMBEDDED-MTP EVIDENCE.**

mlx-serve updated its embedded ds4 engine and changed ds4-backed serving from one session per request to **one persistent session per loaded model**, protected by the existing single-flight claim.

The failure mode was concrete and highly relevant to long-context capacity:

- a ds4 session at roughly **131K context** consumes about **13 GB** of context buffers;
- four concurrent requests previously created four private sessions;
- the documented run moved RSS roughly **41 -> 97 GB**, free RAM to ~0.07 GB, and the process was killed;
- the persistent model-owned session removes that request-count multiplication and also enables ds4 prefix reuse (`cached_tokens > 0`).

The same commit arms in-checkpoint ds4 MTP when the GGUF advertises `nextn_predict_layers`, including sampled requests. The commit/release note reports **Flash-Next Q2 on an M4 Max: 35 -> 47 tok/s** with embedded MTP.

Important qualification: the 35 -> 47 cell does **not** state the active-context length in the commit message, uses Q2 rather than our preferred Q6/Q8-quality lane, and is a single-Mac M4 result. Treat it as direct Apple proof that embedded MTP can materially help this ds4 Flash path, **not** as calibration for 40 tok/s @ 128K on dual M1.

**Project consequence:** request concurrency and model-state lifetime are part of capacity identity. Shared/persistent recurrent/KV/speculative state should not be multiplied per request when the runtime serializes access to one model session. For dual-M1 Flash, explicitly inventory model-owned versus request-owned QSA/GDN/KV/MTP state and prove concurrency does not silently duplicate the long-context working set.

## vLLM #56902 — stale workspace views can pin superseded sparse-attention storage

Source created `2026-09-14 22:08:10 UTC`.

**FRESH NEW / MEMORY-LIFETIME + ADMISSION-PROVENANCE TRANSFER.**

`FlashMLASparseImpl` held constructor-time tensor views into a shared `WorkspaceManager`. When another layer grew the manager's allocation, those old views kept the superseded storage alive, so both the old and new workspaces remained resident even though the manager logically had only one current workspace.

Observed on a GLM-5.3 DP/EP64 deployment:

- **5,904 MiB** old FlashMLA workspace remained resident beside a new **6,144 MiB** MoE workspace on 18/64 ranks;
- ranks retaining both: **18 -> 0** after the fix;
- minimum KV capacity/rank: **490,816 -> 603,904 tokens**;
- aggregate KV capacity: **36,934,975 -> 38,971,455 tokens**;
- reported physical allocation recovered across 64 ranks: **103.78125 GiB**.

No throughput or model-quality claim is made.

The fix stores shapes/dtypes rather than permanent views and reacquires simultaneous views from the current workspace when used.

**Project consequence:** workspace ownership is not described by the manager's current logical size alone. Any persistent view/pointer can keep obsolete storage physically alive. Our Flash admission ruler should include allocator-observed retained storage after workspace growth and test that old views are released/rebound before using the reclaimed capacity for KV/context.

## vLLM #56903 — collapse draft state locally before distributed gather

Source created `2026-09-14 22:11:24 UTC`.

**FRESH NEW / DISTRIBUTED SPECULATIVE-COMMUNICATION TRANSFER.**

DeepSeek-V4.1 DSpark under sequence parallelism gathered BF16 `[T_local, 4, H]` residual streams **plus** FP32 `[T_local, 4]` pre-mix coefficients, then collapsed them to the `[T, H]` state the draft head actually consumes.

The PR reverses that order:

1. collapse each token's HC streams locally;
2. gather only `[T_local, H]`;
3. trim SP padding.

For `hc_mult=4`, this cuts hidden-state payload by 4x and removes the separate pre-mix collective, reducing the tail from two collectives to one.

TP4 / 4x GB200 NV18 scoped tail microbenchmark:

| Global T | Before us | After us | Speedup |
|---:|---:|---:|---:|
| 1 | 24.61 | 18.88 | 1.30x |
| 7 | 26.82 | 18.94 | 1.42x |
| 32 | 43.14 | 19.60 | 2.20x |
| 128 | 108.69 | 20.78 | 5.23x |
| 512 | 163.89 | 28.80 | 5.69x |
| 2048 | 168.43 | 88.14 | 1.91x |

The NCCL-only control improved about 1.35–1.99x across the same sizes. Tests require exact BF16 equivalence, including graph replay. There is **no end-to-end serving, acceptance-rate or quality claim**.

**Project consequence:** communicate the smallest authoritative semantic state, not the producer's richer internal representation. For PP2 distributed Lightning MTP, inspect every TB4 transfer boundary for states that can be collapsed/projected/reduced locally before transport. This is especially relevant if the verifier/control rank consumes only a collapsed head state rather than full HC/recurrent streams.

## llama.cpp #28918 — coalesce long-context FlashAttention softmax memory access

Source created `2026-09-14 22:25:17 UTC`.

**FRESH NEW / STRONG QWEN3.8-27B LONG-CONTEXT PREFILL MECHANISM TRANSFER.**

The SYCL MKL FlashAttention online-softmax path assigned one work-item to each query row and had that work-item serially walk an 8192-element KV chunk twice. Adjacent workers therefore accessed memory roughly 32 KB apart instead of coalescing; the author measured only ~32 GB/s effective bandwidth on a 608-GB/s Arc Pro B70. At 64K–128K prefill that softmax kernel accounted for roughly 70–75% of FlashAttention time.

The rewrite assigns a whole work-group to one row, stripes the chunk over lanes, and uses group reductions for max/sum while preserving the per-element math aside from floating-point summation order.

Qwen3.8-27B UD-Q4_K_XL, Arc Pro B70:

| Prefill | Baseline F16 KV | Coalesced | Delta |
|---:|---:|---:|---:|
| 8,960 | 1010.67 tok/s | 1081.19 | +7.0% |
| 64,000 | 586.10 | 781.59 | +33.4% |
| 126,976 | 402.99 | 601.70 | **+49.3%** |

q8_0 KV showed essentially the same shape. A later fresh-master/default-batch recheck reported pp64K **416.34 -> 649.35 tok/s (+56.0%)**. At 126,976 tokens the softmax component itself fell **306.4 s -> 93.3 s**, while the two GEMMs and dequant stayed flat. Decode was unchanged by construction: tg256 **23.79 ±0.09 -> 23.83 ±0.09**.

Correctness coverage included backend-op tests and a long-context generation battery; 9/9 needle tests hit on both arms and 26/27 outputs were byte-identical, with one late open-ended paraphrase divergence.

**Transfer:** this is Intel SYCL, not Metal or our runtime. Do not transfer the percentage. Promote the physical lesson: a kernel that looks inherently bandwidth-bound may actually be **access-pattern-bound**. At 128K, audit Apple QSA/attention/indexer kernels for row-to-threadgroup mapping, coalescing, repeated passes and effective bandwidth before accepting a roofline conclusion.

## ds4 #1051 — padded sparse-selection sentinels must preserve bounds semantics

Source created `2026-09-14 21:11:42 UTC`.

**FRESH NEW / METAL SPARSE-ATTENTION CORRECTNESS TRANSFER.**

GLM-5.3 pooled selection pads unused slots with `0xffffffff`. Serial decode incorrectly marked those selected rows as fully valid, allowing the split-group8 Metal kernel to skip bounds checks and interpret padding sentinels as cache rows, diluting attention output.

The patch is the decode-side counterpart of an earlier prefill masking fix. No performance receipt is claimed.

**Project consequence:** sparse-selection validity is execution identity. Before enabling a no-bounds-check fast path, certify the producer's exact padding/sentinel contract, valid-count semantics and tail behavior. This belongs in the same long-context correctness gate as deterministic top-k tie order and physical indexer/KV layout.

---

# Screened but not promoted

## mlx-serve #430

Created `2026-09-14 21:31:01 UTC`; moves persisted audio attachments from base64 float32 chat history to on-disk 16-kHz mono WAV. Useful app/runtime hygiene but unrelated to the active inference targets, so no project promotion.

## ds4 #1050

Created `2026-09-14 20:15:49 UTC`; improves the diagnostic when Qwen3.8 emits `<parameter=TOOL>` where `<function=TOOL>` belongs. The report observed the malformed opener in 5/98 stanzas and one failed tool turn costing 2,604 regenerated tokens / ~66 seconds, but there is no model/runtime execution optimization. Retain as agent-quality context only.

## oMLX

No substantive oMLX PR or main-branch source activity strictly after the `19:17:07 UTC` boundary appeared in this pass. #3666 remains the most recent relevant item and was already recorded in the prior watch.

## External HF / Reddit

A fresh community screen surfaced a same-day RTX 4080 16-GB ExLlamaV3 result at **102,400 active tokens**: no-MTP 33.68 tok/s versus fixed-k=2 Q6-draft MTP 56.48 tok/s, with roughly 15.2/16.4 GB VRAM reported. A comment in the same thread also claims a 5070 Ti 16-GB result around 82 tok/s at ~90K and ~92 tok/s at ~60K under another quant/runtime.

These are **not promoted into the source-time watch** because the exact post/comment timestamps relative to this cutoff are not exposed reliably by the retrieved community source, the quants/runtimes differ materially from our canonical RTX lane, and the 5070-Ti number is an unverified comment rather than a controlled receipt. Revisit on a later pass if a source-timestamped benchmark artifact appears.

---

# Cutoff edge

## vLLM #56908 — intentionally excluded

Created `2026-09-14 22:49:17 UTC`, after the requested `22:42:15 UTC` cutoff. It should be the first vLLM item checked next pass; do not use it to advance this watch.

---

# Fresh-screen negatives

- No exact fresh **dual-M1 Flash-Next** TG/PP receipt.
- No exact fresh **M1 Max64 Qwen3.8-27B** receipt.
- No source-time-qualified exact fresh **RTX5070Ti16 Qwen3.8-27B** controlled receipt.
- No exact fresh **dual-M1 DS4-0731** receipt.
- No evidence justifies moving any canonical target.
- No evidence justifies reopening/reordering P69.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 control.

Add these explicit checks/work items:

1. **Persistent-state ownership / concurrency:** inventory model-owned versus request-owned KV, QSA history, GDN recurrent state, PLE, MTP snapshots and draft state. Benchmark RSS/active memory at B1/B2/B4 and ensure concurrency does not duplicate a ~128K session-sized working set unnecessarily.
2. **Collapse before TB4:** whenever a downstream stage/control rank consumes only a collapsed/projected state, perform that reduction locally before transport. Record bytes/cycle and collectives/cycle, not only latency.
3. **Workspace-view lifetime:** force workspace growth in a test, then prove all stale views are released/reacquired and allocator-observed memory actually falls before assigning the reclaimed bytes to KV/context.
4. **Long-context coalescing audit:** for QSA sparse attention, selected-K/V gather, indexer pooling and ordinary attention glue, record effective bandwidth and worker-to-row/data mapping. Do not infer bandwidth saturation from bytes alone.
5. **Sparse tail/sentinel gate:** certify valid-count, padding values, sentinel indices and no-bounds-check admission at 64K/~96K/~128K semantic ruler points.
6. Retain compact selected-K/V QSA, incremental pooled indexer state, live-span-bounded work, verifier specialization, transient-aware prefill chunks, exact PP ownership, TB4 discovery/recovery, distributed MTP consensus/rollback and recurrent-state checkpointing.

The fresh M4-Q2 embedded-MTP 35 -> 47 receipt increases confidence that MTP remains worthwhile on Apple, but **does not calibrate our 128K dual-M1 target because its context is unspecified and quant/topology differ**.

## Qwen3.8-27B M1 / P69

No target movement or internal sequencing change. **P69B12 remains frozen/promoted; P69B13 remains next.**

#28918 reinforces long-context memory-layout/coalescing audits for 27B prefill but is SYCL/B70 evidence only. It does not alter the one-M1 target.

## RTX5070Ti16

No target movement. The fresh community screen is interesting but not controlled/source-time-qualified enough to move **120/250**. Keep the existing SM120 physical-stride, kernel-image/fallback, concurrent-long-prompt and exact-runtime gates.

## DS4-0731 dual M1

No target movement. #1051 is later GLM-5.3 Metal correctness transfer only. The persistent-session lesson from mlx-serve is broadly useful for any long-context ds4 engine integration, but no DS4-0731 topology receipt appeared.

---

# Standing rules added / reinforced

- **Communication form is semantic, not internal:** collapse/project/reduce state locally before transport if the receiver never needs the richer representation.
- **Workspace growth invalidates view provenance:** a logical manager resize is not memory recovery until every old view/pointer is gone and physical allocation confirms release.
- **Session lifetime is capacity identity:** distinguish model-owned persistent state from request-owned state and measure B1/B2/B4 physical residency.
- **Sparse padding is part of execution identity:** sentinel value, valid count and bounds-check policy must agree before a fast path can skip validation.
- **Effective bandwidth requires access-pattern proof:** row/threadgroup mapping, coalescing and repeated passes belong in the long-context performance ruler.
- **Community results without exact source time do not advance the hard freshness boundary or canonical targets.**
- Exact target receipts remain distinct from mechanism transfer, experimental A/Bs and planning targets.
