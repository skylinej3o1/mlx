# External runtime watch — 2026-09-04 19:30 ET

Freshness boundary: `e8ddf943f3f034f0502afffbab798d1a259a7670` / 2026-09-04 22:42:14 UTC.

This pass searched for post-boundary evidence relevant to the exact dual-M1 Flash-Next and DS4
lanes, the single-M1 Qwen3.8-27B lane, and the RTX 5070 Ti Qwen3.8-27B lane. It also swept core MLX
GDN work and newly appearing Qwen4-Exp serving work when the mechanism is plausibly transferable.

## Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

No post-boundary result is an exact sustained rate receipt from one of the four target rigs. The new
evidence changes correctness gates and kernel candidates, not the calibrated performance rows.

---

# Fresh / material

## MTPLX #457 — Flash-Next MTP can be ~2x when recurrent commit/replay is correct

Fresh PR created 2026-09-04 23:16:02 UTC. Apple M3 Max 128 GiB, MLX 0.32.0 / mlx-lm 0.31.3,
Qwen3.8-Flash-Next optimized MTPLX pack, 192-token cold-long-code prompts, two repeated depth sweeps:

- AR: **36.27 / 36.28 tok/s**;
- D1: **45.30 / 45.26** = ~1.25x;
- D2: **58.42 / 58.73** = ~1.61x;
- D3: **73.60 / 73.88** = ~2.03x.

D3 per-position acceptance was **0.961 / 0.922 / 0.882** and reproduced identically across the two
runs. The quality gate passed on every row and D3 reproduced the pack's existing 73.47 tok/s result
within ~0.2%.

This is **stronger-chip / custom-runtime evidence, not an M1-Max rate ruler**. The more important
finding for our bring-up is correctness: forcing the wrong qwen3-next-style capture/commit path ran
D3 at only 0.80x with acceptance 0.214 on corrupted recurrent state **while the quality gate still
passed**. Qwen4-Exp's family path requires the pre-verify snapshot because verified-window commit
replays the GDN recurrence from that state.

Consequence: MTP promotion must validate recurrent state and commit/replay semantics, not merely
coherent text or a top-level quality gate. Acceptance-by-position is a useful corruption diagnostic.
Keep singleton MTP as the first production lane; this result raises the upside if the exact M1 path
can reproduce correct deep verification economics.

## DS4 #964 — exact Apple-Metal recurrent prefill optimization family gets much stronger

Fresh comment at 2026-09-04 22:49:45 UTC reports corrected GLM-5.3-Flash prefill on a fully resident
M3 Ultra Q4_K model, comparing separate binaries against commit `8969dbb`:

| Context | Old PP | New PP | Gain | Old TG | New TG |
|---:|---:|---:|---:|---:|---:|
| 512 | 325.74 | 410.14 | +25.9% | 28.60 | 28.45 |
| 1024 | 320.27 | 403.40 | +26.0% | 28.43 | 28.21 |
| 2048 | 376.42 | 454.36 | +20.7% | 27.89 | 27.74 |
| 4096 | 389.79 | 454.56 | +16.6% | 27.16 | 27.12 |
| 8192 | 391.77 | 460.43 | +17.5% | 27.08 | 26.98 |
| 16384 | 389.27 | 457.31 | +17.5% | 26.97 | 26.87 |

The measured frontier dumps were byte-identical for all 154,880 logits at each frontier, with
additional short/continued-prefill coverage. The five promoted prefill mechanisms are:

1. qk-low **token tiling** with fixed 64-bit addressing;
2. **two-head indexed attention** while retaining each head's reduction and online-softmax order;
3. Q4_K **MoE tail culling** for the exact measured Flash geometry;
4. **blocked recurrent/KDA prepare** with immutable incoming block history and an explicit race fix;
5. **recurrence-value packing**, sharing q/k/decay/beta loads while preserving each row's arithmetic.

A balanced 8K recurrence A/B measured 460.25 / 469.60 / 469.81 / 460.70 PP, or **+2.0%** for the
two-value layout with identical frontier dumps.

This is GLM/M3-Ultra evidence, so it does not move DS4 or Flash exact-M1 forecasts. It does elevate
**exact recurrent-state packing / tiling / shared-load kernels** as a serious Apple-Metal mining
family rather than a speculative micro-optimization. Mine mechanisms after the plain exact
baseline; do not alter the frozen P69 workstream from this external evidence.

## local-inference-lab/vllm #646 — cache memory geometry can be decoupled from hit granularity

Fresh PR created 2026-09-04 23:12:39 UTC on a four-node DGX Spark TP4 GLM-5.3-Flash + DFlash2
setup. Geometry `target block 2048 / recurrent block 256 / prefix-match unit 256` reports:

- 33-GB KV pool: **791,273 -> 4,297,015 tokens**;
- concurrent 262K capacity: **3.02x -> 16.39x**;
- equivalent 3x concurrency: ~33 GB -> **~9 GB**;
- prefix-hit granularity remains **256 tokens**;
- cold PP and decode broadly at parity; long-context correctness passed in the reported checks.

A 52K shared-prefix request reused 51,968 / 52,445 tokens in 0.62 s with fine matching; the old
coarse 2048/2048 geometry reused only 45,056 and took 1.4 s. This is not Apple/Qwen4 rate evidence.
It strengthens our existing cache principle:

> **memory page/block geometry, recurrent checkpoint geometry and prefix-match granularity are
> separate knobs and should be decoupled when the runtime permits it.**

For the community serving recipe, avoid letting a coarse physical page silently force coarse
conversation reuse.

## FreeToken #389 — dense-projection FP8 is a useful Qwen4-Exp GPU mechanism, not a 5070 ruler

Fresh PR created 2026-09-04 23:10:31 UTC. On 2x RTX 6000 Ada TP2, Qwen3.8-Flash-Next with load-time
per-tensor FP8 W8A8 for dense attention/GDN projections:

- single-stream decode: **89.8 -> 99.2 tok/s (+10.4%)**;
- 8-concurrent aggregate: **323.7 -> 331.9 (+2.5%)**;
- 1.8K TTFT: **0.84 -> 0.85 s**;
- corrected expert residency: **91.9% -> 95.8%**.

The quality check is only a smoke test and numerics change, so this is not exactness evidence.
A useful memory-lifecycle trap also surfaced: an apparently contiguous tensor slice retained the
full parent BF16 projection allocation, costing ~1.5 GiB/rank until the slice was explicitly cloned.

For our current 5070 **Qwen3.8-27B** lane this is mechanism transfer only. If/when the NVIDIA lane
moves to Flash-Next, dense-projection FP8 and hidden parent-view retention become explicit A/B and
residency checks.

---

# Fresh update / correctness transfer

## vLLM #55375 — multi-prefill PLE state-index stride bug is exactly the class our agent stress must catch

PR existed before the cutoff but was updated at 2026-09-04 22:58:03 UTC. Qwen3.8-Flash-Next with
MTP3 and multiple pure-prefill requests could produce corrupted repetitive output such as
`Theductductduct...` in the fused PLE short-convolution path.

Root cause is concrete: `state_indices_tensor_p[:, 0]` is a one-dimensional **non-contiguous** view.
With base state + three speculative states its logical stride is four. The fused kernel indexed
request `r` as `state_idx_ptr + r`, so request zero was correct while later requests read/write the
wrong cache slots. Passing the actual stride fixes the address calculation without a materialized
copy.

Reported validation:

- old unit-stride addressing mismatched **90.3%** of output elements in the new regression cases;
- patched minimal reproducer: **5/5** concurrent request pairs pass;
- extended eager: **20/20**;
- compiled/CUDA-graph: **20/20**;
- full PLE test file: **35 passed**.

This is CUDA/vLLM, **not evidence that MLX or llama.cpp has the same bug**. The failure class transfers
strongly to our intended multi-agent Flash server. Before promoting concurrent MTP/prefill, run an
adversarial slot-isolation test with two or more very different prompt lengths, nontrivial slot/state
layouts, MTP enabled, and compare each result/state against serial references. Include PLE
convolution state, recurrent/GDN state, rollback and verified-window commit.

---

# Updated / newly relevant upstream kernel work

## MLX #4409 — packed `gated_delta_seq` is now a high-priority Apple GDN watch item

Existing PR, updated 2026-09-04 23:10:58 UTC. It packs eight value rows per SIMD-group in the
sequential `gated_delta_update` kernel while preserving the reduction tree's bit pattern on the
tested toolchain.

M5 Max validation reports **77/77 cross-build `mx.array_equal` cases** for both output and final
state, plus 20,000 float32 reduction simulations with zero mismatches. Interleaved M5-Max kernel
ratios report:

- B1 T2048: **1.90x** median;
- B8 T2048: **2.16x**;
- B16 T2048: **1.86x**;
- T512-1024 across B1-16: **1.78-1.96x**;
- B8/B16 T8: **1.36-1.43x**;
- separate default T<=16 probe: roughly **+7-24%** on B1 T1/4/16 and ~+15% on B8 T16.

Absolute latency drift was large, so the author correctly reports paired ratios rather than raw
latency. This is a core-MLX GDN kernel candidate, but it is **not yet a mainline exact-M1 serving
receipt** and must not contaminate P69B13. Track its upstream fate and, after the serving baseline
is frozen, test the landed/pinned implementation on the exact M1 model geometry.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no new sustained exact TG, no completed long-context exact follow-up, and no
  post-cutoff exact-M1 Flash receipt surfaced.
- **Dual-M1 DS4-0731:** no new exact sustained generated-token denominator surfaced.
- **RTX 5070 Ti Qwen3.8-27B:** `aipruner/qwen3.8-3bit-test-in-16GB-GPU` remains
  `pushed_at=2026-08-20T19:16:50Z`.
- **Apple Qwen3.8-27B:** `mlx-dspark` remains `pushed_at=2026-09-01T10:54:45Z`; Layr remains
  `pushed_at=2026-08-29T07:05:19Z`.
- **oMLX:** no post-boundary issue/PR surfaced in the focused scan.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep the existing qualification order, with one important insertion before any concurrent MTP
promotion:

1. pin/certify llama.cpp `v0.4.0` / exact tagged commit;
2. plain exact PP2/layer-owned baseline; TP2 control;
3. PLE residency/page-cache/direct-read A/B;
4. sparse-QSA wide-prefill A/B;
5. pooled QSA-prefix retention / rollback correctness;
6. singleton MTP depth/acceptance A/B with **pre-verify snapshot + exact recurrent commit/replay**;
7. **multi-request pure-prefill state-isolation gate**: mismatched prompt lengths, serial-reference
   comparison, PLE/GDN state-address correctness, rollback and verified-window commit;
8. only then adversarial parallel-MTP slot isolation and MTP concurrency >1;
9. compiled decode B2/B4;
10. workload-derived cache matching, with physical cache-page geometry decoupled from prefix-match
    granularity where feasible;
11. combine passing mechanisms and run long-prefill-arrives-during-decode multi-agent stress.

Add exact recurrent/GDN packing, tiling and shared-load kernels to the post-baseline mining queue.
Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

No target or topology change. Keep PP2/layer ownership primary, TP2 control; AProjQ4 primary serving
candidate; command-buffer/OS/residency diagnostics; adaptive speculation; and agent-shell
observation/compaction/session gates. DS4 #964 strengthens the general Apple-Metal recurrent-kernel
mining case, not the DS4-0731 rate forecast.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No target change. MLX #4409 is relevant future kernel evidence, but P69 stays separate:
**P69B12 frozen/promoted; P69B13 next from existing profiling only**. Any upstream GDN packing is a
future serving/runtime A/B after the exact verifier sequence.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Keep the 18:40 qualification order: linked CUDA runtime provenance; ubatch/prompt
shape stability; fully resident Q3_K_XL + native MTP; draft-cache net-memory A/B; DFlash control;
small-N verify; MTP-head quant; GSQ-RCO. FreeToken #389 is a future Qwen4-Exp GPU mechanism, not a
27B calibration input.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing decisions added by this pass

- **Coherent output is not sufficient evidence of correct MTP state.** Verify recurrent snapshots,
  verified-window commit/replay and acceptance-by-position.
- **Concurrent pure-prefill is now a dedicated Flash correctness gate.** Cross-slot PLE/GDN state
  must match serial reference under deliberately different request lengths/layouts.
- **GDN/recurrent Metal kernels remain a large optimization surface even under bit-exactness.**
  Packing value rows, sharing invariant loads, blocked state preparation and token tiling are now
  high-priority mechanism families.
- **Physical cache page size and prefix-match granularity should be independently selectable.**
- P69 exact verifier work remains isolated from these external serving/runtime findings.

The canonical performance targets and their threshold ladders remain centralized in
`RESEARCH-TARGETS.md`.
