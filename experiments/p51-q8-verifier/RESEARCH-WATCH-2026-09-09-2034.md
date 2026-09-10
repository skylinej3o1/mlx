# External runtime watch — 2026-09-09 20:34 ET

Starting canonical head: `079265791bc4685aad80bb701410f179944d45b8`.

Starting hard source-freshness boundary: **2026-09-09 21:58:00 UTC**.

Classification discipline: measured exact-target receipts remain separate from cross-hardware transfer evidence, implementation A/Bs, and backfill. Nothing in this pass justifies moving a canonical TG/PP target.

---

## FRESH / antirez/ds4 #952 — selective projection Q4 remains decode-positive but prefill-shape sensitive

Fresh comment `5609589642` at **2026-09-09 22:26:45 UTC** retests the DeepSeek-V4-Flash-0731 AProjQ4 layout on **Ryzen AI Max+ 395 / Radeon 8060S gfx1151 / ROCm 7.1.1** at commit `4a87d9c`.

AProjQ4 converts only the selected dense attention-projection families from Q8_0 to imatrix-guided Q4_K; the fresh Q4-vs-Q8 large-chunk result is:

| ctx | prefill delta | decode delta |
|---:|---:|---:|
| 8,192 | -3.3% | +11.4% |
| 16,384 | -9.2% | +11.3% |
| 24,576 | -8.3% | +11.0% |
| 32,768 | -8.2% | +10.8% |

The reporter states that the ROCm decode benefit stayed around **+11%** across `96f5b46 -> 77a054e -> 4a87d9c`, while the large-chunk prefill deficit remains roughly **-8% to -9%**.

**Promotion:** quantization must be qualified by execution phase and matrix shape, not by one whole-model throughput scalar. A lower-bit projection recipe can be an unambiguous decode win and still regress large-M/chunked prefill. For any future custom 5.x-bit recipe, measure at least B1/small-M decode, verifier small-M, realistic chunked prefill, and cold long-prefill separately before promoting a tensor-family bit assignment.

No DS4 dual-M1 target movement: this is ROCm transfer evidence, not the canonical 2x M1 Max64/TB4 lane.

---

## BACKFILL / ds4 #952 — Apple Metal evidence for tensor-family-selective quantization

The current PR body consolidates older production evidence that was not yet in our research chain. Treat this as **BACKFILL**, not post-cutoff evidence.

The AProjQ4 recipe requantizes **215 dense attention-projection tensors** across 43 layers (`attn_q_a`, `attn_q_b`, `attn_kv`, `attn_output_a`, `attn_output_b`) from Q8_0 to imatrix-guided Q4_K while leaving all other tensor families unchanged. It reduces the artifact by **2.14 GiB / 2.65%**.

On a fully-resident **M5 Max 128GB / 40-core GPU** Metal lane, the PR reports a paired median decode improvement of about **+15.5%**, with all 32 tested decode frontiers favoring Q4, while full-model prefill was effectively at parity. Its 100-case / 2,313-target-token quality fixture showed no measured regression, though that fixture is explicitly not universal quality proof.

**Blazer implication:** this is unusually direct support for the user's long-term custom-quant strategy: tensor-family-selective precision can buy meaningful Apple decode speed and memory headroom without requiring a uniform whole-model bit drop. The correct target is therefore not a sacred nominal BPW; it is a sensitivity-weighted recipe whose promoted tensors earn their bandwidth on task quality, MTP acceptance, and the actual M1 kernel shapes.

Do not numerically transfer M5 rates to M1 Max.

---

## FRESH / vLLM #52664 — sparse indexer score/top-k/attend must be one kernel contract

Commit `83252ea899c6538eaa0c1fb31f28a92c661bbffc` at **2026-09-09 22:40:33 UTC** integrates AITER indexer scoring and top-k kernels into MiniMax-M3 sparse attention.

Important architecture details:

- decode and ragged-prefill scoring use dedicated fused fp8 MFMA paths;
- top-k emits the attend page table directly while winners are still resident in the workgroup;
- the indexer refuses the fast path unless it is paired with the matching sparse-attend backend;
- the compiled contract explicitly gates index-cache/query dtype, sparse block size, top-k width, index-head dimension, architecture, context-block ceiling and speculative decode width;
- notably, `num_index_heads * max_decode_query_len` must fit the MFMA column budget, so speculative width can change whether the fast sparse-index path is even legal.

**Promotion for Flash-Next QSA:** treat score -> top-k -> selected-page-table -> attend as one producer/consumer contract. A benchmark must record the actual indexer backend, selected-attend backend, top-k/block geometry, index-cache dtype/layout, context ceiling and speculative verify width. Do not certify the scorer independently if the selected indices are reformatted or resolved through a different attend path.

For our portable implementation, favor a fused path in which selection emits exactly the representation consumed by gathered attention, avoiding a separate dense/global reindex pass.

---

## FRESH / llama.cpp #25940 — wider quant is not monotonically faster; matrix shape can dominate

Comment `5609859741` at **2026-09-09 22:55:22 UTC** adds gfx1200 / RX 9060 XT 16GB coverage for ROCm matmul kernels.

At `m=4096, k=14336, n=512`:

| quant | rate |
|---|---:|
| q2_K | 9.89 TFLOPS |
| q6_K | 15.57 TFLOPS |
| q4_K | 30.52 TFLOPS |
| q4_0 | 33.61 TFLOPS |
| iq4_xs | 37.61 TFLOPS |

The same report explicitly calls q2_K and q6_K at n=512 a backend regression/cliff and notes that matrix orientation changes timings materially.

**Promotion for 5.x-bit / Blazer work:** never assume `Q6 > Q5 > Q4` in runtime cost merely from BPW. Kernel maturity, packing, N/M/K geometry and backend dispatch can dominate nominal precision. Our future quant search must optimize the joint pair **recipe + kernel layout**, with separate measurements for decode GEMV/QMV, MTP verifier small-M, and large-M prefill. A slightly larger custom packing may be faster than a nominally smaller generic format if it maps better to Apple SIMD/tile geometry.

This is cross-vendor mechanism evidence only; no M1 or RTX5070Ti numeric transfer.

---

## FRESH / vLLM #55819 — avoid redundant staging copies when the consumer can read shared-visible storage

PR head `f0730f78668c523010413529663aa7a4af15bac5` was refreshed at **2026-09-09 22:40:14 UTC** and approved post-cutoff. The PR changes MRV2 staged writes so UVA-backed targets use pinned UVA contents directly instead of always materializing a temporary GPU contents buffer via H2D first.

Its synchronized `apply_write()` microbenchmarks show roughly **1.26x to 1.96x** improvements depending on size, and its GSM8K staged-write timing improves about **1.40x**; the PR correctly does **not** claim an end-to-end model throughput multiplier.

**Promotion:** for PLE/QSA/index metadata and other small selected-row/control traffic, do not insert a staging copy merely because the generic path has one. If the actual consumer can safely address the producer storage, compare direct-visible consumption against staged-copy consumption with explicit lifetime/happens-before guarantees. On Apple this is a design-shape analogy, not a CUDA-UVA implementation prescription.

---

## SCREENED / no target move

- `jundot/omlx` main: no post-cutoff main commit. Fresh comments were K2/tool-template handling, not Flash-Next throughput evidence.
- `Pushkinist/rMLX`: no post-cutoff main commit.
- `ggml-org/llama.cpp` main: no post-cutoff main commit; the fresh gfx1200 comment above is transfer evidence only.
- `antirez/ds4` main: no post-cutoff main commit; fresh #952 ROCm result is not the dual-M1 lane.
- broad web/exact-rig search surfaced the already-known RTX5070Ti 256K Qwen3.8-27B work and older single-M1 Flash-Next material, but no timestamp-qualified new exact target receipt after the cutoff.
- no new exact 2x M1 Max64/TB4 Flash-Next sustained TG/PP receipt.
- no new one-M1 Max64 Qwen3.8-27B receipt.
- no new fully-resident Q3_K_XL/native-MTP RTX5070Ti16 speed-lane receipt.
- no new exact 2x M1 Max64/TB4 DS4-0731 rate receipt.

---

# Consequences for the planned 2x M1 Max Flash-Next system

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen these qualification items:

1. quant recipe certification by phase/shape: decode, verifier small-M, realistic chunked prefill, long cold prefill;
2. QSA scorer/top-k/selected-page-table/attend as one backend contract;
3. record whether speculative width changes sparse-index fast-path eligibility;
4. selection should emit the representation the gathered-attend consumer actually needs;
5. selected-row/index/control traffic should compare direct-visible access versus explicit staging, with device-lifetime proof;
6. generic 5.x-bit kernels must support multiple pack/group/tensor precision configurations rather than hard-code one quant artifact;
7. future Blazer search evaluates **quality + TG + PP + MTP acceptance + memory + PP balance**, not BPW alone;
8. preserve all prior ownership, rollback, boundary-materialization, B2 interleaving, resident-engine provenance, PLE placement, mixed-concurrency and long-soak gates.

Safe serving remains **profitable singleton MTP + plain concurrent work** until the existing concurrency/state-isolation gates are passed.

---

# Lane decisions

- **Flash-Next 2x M1 Max64/TB4:** 40 TG / 400 cold PP working targets unchanged.
- **Qwen3.8-27B M1 Max64:** 25 TG / 110 native cold PP unchanged. P69 remains isolated; P69B12 stays frozen/promoted and P69B13 remains next from existing profiling only.
- **Qwen3.8-27B RTX5070Ti16:** 120 TG / 250 cold PP speed-lane targets unchanged; long-context host-backed lanes remain separate.
- **DS4-0731 2x M1 Max64/TB4:** 15 TG / 180 cold PP unchanged. The new AProjQ4 evidence strengthens selective-quant methodology but does not move the exact dual-M1 rate.

---

# Standing decision strengthened this pass

The long-term custom quant project should be treated as a **co-designed 5.x-bit execution format**, not just a quantizer recipe. Tensor sensitivity, packing/group layout, phase-specific matrix shapes, sparse gathers, MTP small-M kernels, PP stage balance and task-level quality must be optimized together. A nominally higher-bit format can be slower than a lower-bit format when its kernel shape is poor; conversely, selectively spending bits on sensitive tensors can preserve quality while retaining most of the lower-bit speed/memory benefit.

**No canonical target movement this pass. P69 remains isolated.**
