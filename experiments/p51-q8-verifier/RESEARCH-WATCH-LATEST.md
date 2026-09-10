# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-09-2034.md`

   **The 20:34 note is authoritative for fresh DS4 selective-projection Q4 phase/shape evidence, fused sparse-index score/top-k/attend contract evidence, quant-format matrix-shape cliffs, direct-visible versus staged-copy control traffic, and the resulting 5.x-bit / Blazer co-design implications.**

4. Retain the immediately previous runtime deltas:

   - `RESEARCH-WATCH-2026-09-09-1752.md` — full-machine-residency benchmark provenance, PP speculative broadcast operand lifetime/device happens-before, rMLX single-source recurrent rollback/state construction, shared-KV read-only ownership;
   - `RESEARCH-WATCH-2026-09-09-1402.md` — Qwen3.8-Flash-Next UVA PLE offload / Engram parallelism, NVFP4 packed gathered top-k projection, backend dispatch-limit qualification;
   - `RESEARCH-WATCH-2026-09-09-0941.md` — rMLX request-record provenance, quantized-FA compiled-capability provenance, routed-MoE active-expert tile geometry;
   - `RESEARCH-WATCH-2026-09-09-0628.md` — exact RTX5070Ti IQ4_XS 256K capacity lane, Atlas concurrent-MTP ownership/counter regression, round/acceptance invariants, oMLX boundary materialization, vLLM mixed-concurrency/tail-ring/soak attribution;
   - retain 2026-09-08 and older dated deltas for the remaining QSA, GDN/projection, recurrent rollback, cache lifecycle, concurrency and provenance evidence.

5. Also retain:

   `RESEARCH-MINING-2026-09-09-CROSS-MODEL-KV-TRANSFER.md`

   as **BACKFILL / future serving research**, not fresh target evidence. It does not interrupt P69.

6. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, dated deltas newer than that remain part of the evidence chain.

7. Read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when mining portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 20:34 pass moves no row.** New evidence materially strengthens the custom-quant/kernel co-design methodology and sparse-QSA qualification plan, but it is not a new exact canonical target-lane rate receipt.

---

# Current newest evidence delta — 2026-09-09 20:34 ET

Starting canonical head: `079265791bc4685aad80bb701410f179944d45b8`.

Starting hard source-freshness boundary: **2026-09-09 21:58:00 UTC**.

## FRESH / ds4 #952 — selective attention-projection Q4 is phase sensitive

Fresh ROCm retest at **2026-09-09 22:26:45 UTC** compares DeepSeek-V4-Flash-0731 AProjQ4 versus AProjQ8 on gfx1151. Q4 decode remains about **+10.8% to +11.4%** across 8K-32K while large-chunk prefill is **-3.3% at 8K and roughly -8% to -9% at 16K-32K**.

**Promotion:** certify every future mixed/dynamic quant recipe separately on decode/small-M, MTP verifier small-M and realistic large-M/chunked prefill. A tensor-family bit drop can be a clear decode win while harming prefill.

## BACKFILL / ds4 #952 — direct Apple support for tensor-family-selective quantization

The current PR body consolidates older M5 Max evidence not previously in our chain: converting only 215 dense attention-projection tensors from Q8_0 to imatrix-guided Q4_K saves **2.14 GiB / 2.65%**, improves fully-resident Metal decode by about **15%**, and leaves full-model prefill effectively at parity on the reported tests. A 100-case quality fixture showed no measured regression, but is not universal quality proof.

**Blazer consequence:** custom 5.x-bit work should assign precision by tensor sensitivity and actual kernel cost rather than enforce one uniform model-wide bit width.

## FRESH / vLLM #52664 — sparse indexer and attend form one kernel contract

`83252ea899c6538eaa0c1fb31f28a92c661bbffc` at **2026-09-09 22:40:33 UTC** fuses sparse index scoring + top-k and has top-k emit the attend page table directly. The fast path is gated jointly by index-cache/query dtype, sparse block size, top-k, head geometry, context ceiling, paired attend backend and speculative decode width.

**Promotion:** Flash-Next QSA score -> top-k -> selected-page-table -> gathered-attend is one producer/consumer contract. Record the actual paired backends and verify that MTP/speculative width does not silently force a fallback path.

## FRESH / llama.cpp #25940 — quant runtime cost is not monotonic in BPW

Fresh gfx1200 evidence at **2026-09-09 22:55:22 UTC** reports `m=4096, k=14336, n=512` rates of roughly **15.57 TFLOPS for q6_K versus 30.52 for q4_K**, with q2_K also on a backend-specific cliff. Matrix orientation materially changes timing.

**Promotion:** the future 5.x-bit / Blazer search optimizes **quant recipe + packing + kernel geometry** together. Do not assume a nominally wider format is simply a slower version of a narrower one; backend shape support can dominate bit count.

## FRESH / vLLM #55819 — avoid redundant staging for directly visible control data

Post-cutoff PR head activity keeps a path that lets UVA-backed staged-write targets consume pinned UVA contents directly instead of always staging them through a temporary GPU buffer. The PR reports **1.26x-1.96x** synchronized `apply_write()` microbench improvements and about **1.40x** improvement in its GSM8K staged-write timing, without claiming E2E model throughput.

**Promotion:** PLE/QSA/index metadata and other selected-row/control traffic should compare direct-visible consumption against generic staged-copy paths, with explicit lifetime/happens-before proof. This is a design-shape transfer, not an Apple numeric transfer.

## SCREENED / no target move

- oMLX main: no post-cutoff main commit; fresh comments were unrelated K2/tool-template work.
- rMLX: no post-cutoff main commit.
- llama.cpp main: no post-cutoff main commit; fresh gfx1200 evidence is transfer-only.
- antirez/ds4 main: no post-cutoff main commit; #952 ROCm result is not the exact dual-M1 lane.
- broad exact-rig search surfaced already-known RTX5070Ti 256K Qwen3.8-27B and older single-M1 Flash evidence, but no timestamp-qualified new exact target receipt after the cutoff.
- no new exact dual-M1 Max64/TB4 Flash-Next sustained receipt.
- no new single-M1 Max64 Qwen3.8-27B receipt.
- no new fully-resident Q3_K_XL/native-MTP RTX5070Ti16 speed-lane receipt.
- no new exact dual-M1 Max64/TB4 DS4-0731 receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen:

1. quant recipe certification by phase and matrix shape;
2. QSA score/top-k/page-table/attend as one paired backend contract;
3. explicit proof of sparse fast-path eligibility at the chosen MTP/speculative width;
4. selection output should already match the gathered-attend consumer representation when practical;
5. direct-visible versus staged-copy A/B for PLE/QSA/index/control traffic with lifetime proof;
6. generic 5.x-bit kernels that can support multiple group/pack/tensor precision assignments;
7. Blazer objective = **task quality + TG + PP + MTP acceptance + memory + PP balance**, not BPW alone;
8. all prior ownership, rollback, boundary-materialization, resident-engine provenance, mixed-concurrency and long-soak gates remain.

Safe serving remains **profitable singleton MTP + plain concurrent work** until the existing concurrency/state-isolation gates are certified.

## Single M1 Max64 Qwen3.8-27B

No target movement. **P69B12 frozen/promoted; P69B13 remains next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the speed lane; host-backed long-context configurations remain a separate capacity lane.

## Dual-M1 DS4-0731

No target movement. The AProjQ4 evidence strengthens selective-quant methodology but does not change the exact dual-M1 rate.

---

# Standing decisions strengthened this pass

- Quantization is an execution-format problem, not just a file-size problem.
- Tensor-family precision must be judged against both decode and prefill shapes.
- Sparse indexer selection and sparse attend should be certified as one contract.
- Speculative width can change sparse-kernel eligibility and therefore belongs in route provenance.
- A wider quant can be slower than a narrower one when its backend kernel/shape is poor.
- The long-term custom 5.x-bit / Blazer project should co-design sensitivity, packing, group geometry, sparse gathers, MTP small-M kernels and PP stage balance.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**
