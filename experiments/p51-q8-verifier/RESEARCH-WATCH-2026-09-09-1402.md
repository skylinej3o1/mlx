# External runtime research watch — 2026-09-09 14:02 ET

Starting canonical branch head: `e4a832db893151f0694e5230de0dddce355b2d8f`.

Starting hard source-freshness boundary: **2026-09-09 13:57:01 UTC**.

The intervening `e4a832db...` commit records the 2026-08-04 cross-model KV/state-transfer paper as a portable research lead. It is preserved as **BACKFILL / mining**, not counted as post-cutoff source evidence. It moves no target and does not change P69.

---

# Verdict

**Material mechanism pass; no canonical TG/PP target movement.**

The strongest fresh evidence is direct Qwen3.8-Flash-Next runtime work in vLLM showing that the giant PLE/n-gram table can be independently placed/sharded and, on the measured NVIDIA topology, pinned-host/UVA offload is approximately decode-neutral after acceptance normalization. A second fresh vLLM change shows a quantized speculative top-k projection can operate directly on selected packed NVFP4 rows rather than materializing a dense/dequantized matrix. Both are highly relevant to the dual-M1 Flash plan and the eventual custom 5.x-bit quant/kernel co-design, but neither is target-M1 numeric evidence.

---

## FRESH / Qwen3.8-Flash-Next PLE offload + Engram tensor parallelism

vLLM merge `3116c5d06bfe76501b3dd6b5434bfc7f3274f5e7`, **2026-09-09 14:32:34 UTC**, PR #54371: `[Qwen4Exp] Support UVA PLE-offload and Engram tensor parallelism`.

Despite the internal `Qwen4Exp` naming, the PR's measured model is `Qwen/Qwen3.8-Flash-Next-FP8`.

The new `engram_config` separates two placement choices:

- `cpu_offload=true`: each local PLE shard is retained in pinned host memory and required rows are accessed/copied through CUDA Unified Virtual Addressing on a dedicated stream;
- `cpu_offload=false`: PLE is accelerator resident;
- `embedding_across_dp=false`: PLE sharding follows TP independently per DP replica;
- `embedding_across_dp=true`: the embedding parallel group spans TP x DP, reducing PLE replication across replicas.

The PR explicitly treats PLE placement and PLE sharding as independent dimensions rather than assuming the main-model TP/DP topology must also define the lookup table topology.

### Measured cells reported in the PR

Model: Qwen3.8-Flash-Next-FP8. Prefill uses 8K input, concurrency 2. Decode uses 1024 output tokens, concurrency 64, MTP=3.

| PLE offload | across DP | topology | prefill tok/s | raw decode tok/s | draft acceptance | seq-steps/s | est. C64 step |
|---|---|---|---:|---:|---:|---:|---:|
| false | false | TP4 / DP1 | 33,544.13 | 2,261.37 | 53.72% | 865.89 | 73.91 ms |
| true | false | TP4 / DP1 | 33,322.61 | 2,245.84 | 51.56% | 881.83 | 72.58 ms |
| false | false | DP2 / TP4 / EP8 / FI2S | 26,872.32 | 2,762.68 | 39.80% | 1,259.20 | 50.83 ms |
| false | true | DP2 / TP4 / EP8 / FI2S | 26,763.57 | 2,775.67 | 43.28% | 1,207.65 | 53.00 ms |
| true | false | DP2 / TP4 / EP8 / FI2S | 25,751.63 | 3,101.35 | 46.48% | 1,295.25 | 49.41 ms |

The PR normalizes for the differing speculative acceptance and characterizes PLE-offload decode differences as about **+1.84% on TP4 and +2.86% on DP2**, i.e. approximately flat single-run differences rather than a meaningful offload penalty.

Correctness coverage includes TP2/DP1/MTP3 serving with the BF16 PLE weights remaining pinned on CPU; the PR reports GSM8K **0.9727 / 1,319 samples** for that path.

### Promotion

Treat PLE as a **separately placeable and separately shardable sparse lookup plane**, not as ordinary streamed model weights.

For dual-M1 Flash qualification, explicitly measure:

1. resident vs file-backed/mmap/pread PLE placement;
2. actual selected rows and bytes/token, not total PLE table size;
3. page-fault/page-cache state and cold/warm lookup latency;
4. overlap of PLE fetch/gather with stage-local compute;
5. PLE replication vs sharding across the two nodes independently of PP layer ownership;
6. any TB4 traffic caused by placing a PLE shard away from the consuming stage;
7. requested/configured/actual PLE route and fallback reason.

Apple UMA is not CUDA UVA, so the mechanism transfers but the absolute NVIDIA result does not. No M1 target rate moves from this evidence.

This directly strengthens the project's existing view that the giant PLE table is much less threatening than its headline parameter count if selected-row access remains sparse, overlapped and local to the consuming stage.

---

## FRESH / NVFP4 DSpark gathered top-k projection over packed weights

vLLM merge `83fe99399ec0603b32393a14324b65c67ad04af2`, **2026-09-09 17:33:46 UTC**, PR #55713: `[Spec Decode] Add NVFP4 DSpark gathered top-k projection`.

The DSpark Markov head corrects only selected top-k vocabulary rows. With packed NVFP4 W2, a normal BF16 row gather is impossible without dequantization. The new path therefore retains the packed W2 and scales and performs:

`selected row ids -> gather packed NVFP4 rows/scales -> dequantize selected 16-element groups -> dot with Markov embedding -> add base value -> scatter corrected logits`.

It does **not** dequantize/materialize the full vocabulary matrix merely to consume a sparse subset.

Correctness tests cover batch sizes 1/2/4/8 plus CUDA graph replay, with CPU/CUDA FP16/W4A16 fallbacks retained.

### Reported serving A/B

Nemotron 3.5 Lightning, DSpark depth 5, synthetic acceptance length target 3.3, ISL 34,817, OSL 1,024, concurrency 1; two warmups + five measured requests.

- T=0, top-k 512 ON: **135.337 TPS/user, 128.986 global TPS, observed AL 3.5168**;
- T=0, top-k OFF: **130.861 / 124.296, AL 3.4944**;
- T=1, top-k 512 ON: **133.502 / 126.880, AL 3.4628**;
- T=1, top-k OFF: **128.542 / 121.981, AL 3.4275**.

This is roughly a **3-4% serving gain** for the gathered top-k path in those cells. It is cross-hardware/model transfer evidence, not a rate for our target.

### Promotion

Add a portable kernel candidate for the custom 5.x-bit / "Blazer" direction:

> **packed gather -> local dequant -> small dot/reduction -> scatter**

For any Flash MTP/QSA/selector/projection path that consumes only selected rows, do not assume a dense quantized GEMM or whole-matrix dequant is the right primitive. Benchmark the sparse selected-row path directly at real M1 small-M / verifier widths and candidate counts.

This is also evidence that the future quant recipe and runtime should be co-designed: packing/group geometry that is excellent for dense GEMV can be poor for selected-row gathers, and vice versa. Quant-format selection therefore belongs in the kernel/objective loop, not only the quality loop.

No canonical target movement.

---

## FRESH / llama.cpp Flash-Next Vulkan grid-limit robustness

llama.cpp `22397c31a00e78f55ae556c41fc78b717c5911bd`, **2026-09-09 14:54:15 UTC**, PR #28592, changes `FILL` dispatch from one-dimensional to two-dimensional workgroup distribution because Qwen3.8-Flash-Next could exceed Intel Vulkan `maxComputeWorkGroupCount`.

This is not an Apple performance result. Its portable lesson is qualification-only: model-scale tensors can hit backend launch/grid limits even when arithmetic and memory capacity are otherwise valid. Long-context and large-state cells should certify actual dispatch dimensions/backend limits rather than extrapolate from smaller shapes.

---

## SCREENED / no target-rate evidence

- oMLX main: no post-cutoff main commit.
- rMLX: newest commit remains `0b2a152...` at 13:21:09 UTC, before this cutoff.
- antirez/ds4: no post-cutoff commit; latest main activity remains 2026-09-08.
- TurboQuant-MLX: no post-cutoff commit.
- vLLM #56037: no new substantive post-cutoff comment; the latest visible comment predates the cutoff.
- additional vLLM post-cutoff commits were generic backend/CI/model-support work and did not provide stronger target-lane receipts.
- broad exact-rig web searches produced no new timestamp-qualified post-cutoff receipt for 2x M1 Max64/TB4 Flash-Next or DS4, one M1 Max64 mature Qwen3.8-27B, or fully-resident Q3_K_XL RTX5070Ti16.
- web results around quantized/mmap PLE tables are interesting but were not promoted as FRESH where a substantive post-cutoff timestamp could not be established.

---

# Consequences by target lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary; TP2 control**.

Add to the qualification order:

- PLE physical-placement identity and sparse selected-row traffic;
- PLE replication/sharding topology independent of PP stage ownership;
- cold/warm page-cache and lookup behavior for file-backed PLE;
- proof that PLE placement does not accidentally create dense or repeated TB4 traffic;
- packed selected-row quantized projection kernels as a candidate alongside dense QMV/GEMV;
- dispatch/grid-limit checks at real long-context/state sizes.

Existing gates remain unchanged: distributed lifecycle, stage-local recurrent/QSA state, mixed prefill/decode ordering, one committed speculative frontier, rollback/round accounting, boundary materialization/restart reuse, B2 interleaving, actual executed-route provenance, mixed-long/short stress, long soak and no accidental dense TB4 materialization.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. The canonical speed lane remains fully-resident Q3_K_XL/native-MTP; the IQ4_XS host-backed long-context lane remains separate.

## Dual-M1 DS4-0731

No target movement. The new DSpark packed-gather path is a portable quantized sparse-projection mechanism only.

---

# Standing decisions strengthened this pass

- PLE/n-gram tables are a distinct lookup plane whose placement and sharding should be optimized separately from ordinary model layers.
- Headline total parameter count is not an inference-bandwidth claim when a large component is sparse selected-row lookup.
- Offload is judged by actual selected-row traffic, overlap and wall time, not by the offloaded table's full byte size.
- PLE sharding topology is not automatically identical to PP/TP/DP topology.
- Sparse selected-row consumers should operate on packed quantized rows where possible instead of forcing dense dequantization.
- Custom quant design must consider sparse-gather kernel cost as well as dense GEMV/QMV quality and speed.
- Cross-hardware mechanism evidence does not move target-M1 rates.
- No canonical target movement this pass.
- P69 remains isolated.
