# External runtime watch — 2026-09-11 13:48 ET

Search window: **strictly after 2026-09-11 10:39:19 UTC through 2026-09-11 17:48:40 UTC**.

This is a complete fresh pass across the standing lanes: oMLX / Apple cluster work, rMLX speculative-state work, llama.cpp Metal/quant/MoE kernels, vLLM sparse/spec/cache work, antirez/ds4, mlx-serve, DeepSeek V4.1 Apple work, and exact-rig receipt screening.

Evidence discipline remains unchanged:

- source timestamp, not rediscovery time, determines freshness;
- exact target receipts are separated from stronger-hardware transfer receipts and kernel/mechanism evidence;
- requested/configured support is not counted as executed support without route provenance;
- component/kernel speedups do not become TG/PP multipliers without production-style wall-clock evidence;
- context, workload shape, speculation state, cache/offload state and residency remain part of benchmark identity.

## Executive result

**No canonical target moves.**

The headline Flash objective remains **40 tok/s sustained at ~128K active context** with **400 tok/s cold PP** on the planned 2x M1 Max 64 GB / TB4 system. No fresh exact dual-M1/TB4 Flash receipt appeared. No fresh exact one-M1-Max64 Qwen3.8-27B receipt, RTX5070Ti16 canonical fully-resident speed-lane receipt, or dual-M1 DS4-0731 receipt appeared either.

This pass is nevertheless high-value because it adds:

1. the first merged oMLX **DeepSeek V4.1 Flash Apple performance receipt** on M3 Ultra 512 GB, including RAM-vs-SSD Engram memory/performance cells;
2. a directly relevant **two-node Flash-Next TP2 load-transient fix** measured on Qwen3.8-Flash-Next-REAP-288;
3. a macOS/TB cluster **control-plane transport failure mode** and direct-first/fallback contract;
4. new Metal evidence that **routed-expert token-tail occupancy** is a first-class MoE kernel geometry;
5. new grouped small-batch cache-insertion evidence reinforcing dispatch-amortization for compact state writes;
6. a fresh **Affine8 long-context KV capacity/error lane** on M5 Pro;
7. exact expert-offload evidence that confirms SSD expert streaming is primarily a capacity escape hatch, not the preferred speed path.

---

# FRESH — oMLX #3574: DeepSeek V4.1 Flash + DSpark MTP + Engram SSD offload

Merged commit:

`f79b785485b36f81dcd669de86c1175f0507f851` — **2026-09-11 12:33:30 UTC**

PR: `jundot/omlx#3574`

Classification: **FRESH / STRONGER-APPLE TRANSFER / FUTURE V4.1 LANE**.

This is not DS4-0731 target evidence and not an M5 Ultra receipt.

## Runtime/model support

The merged implementation adds native oMLX support for DeepSeek V4.1 Flash including:

- original FP4/FP8 checkpoint loading with packed repacking;
- oQ3/oQ3e and oQ4/oQ4e conversion paths;
- DSpark drafting and packed target verification through Lightning MTP;
- Engram RAM and SSD-backed modes;
- packed window KV, compressed KV and index keys;
- sparse attention and streaming index selection;
- grouped expert execution;
- affine 2/3/4/6/8-bit Metal kernels;
- accepted-boundary restoration without target replay;
- SSD prefix-cache persistence and 2,048-token boundary snapshots;
- vision support and original vision precision retention.

Published V4.1 oMLX builds report:

| build | resident weights | loader budget with Engram SSD offload |
|---|---:|---:|
| oQ3e-mtp | 239.34 GiB | ~251.34 GiB |
| oQ4e-mtp | 287.92 GiB | ~302.35 GiB |

The stated budgets are checkpoint-header estimates, **not measured total-system peaks**.

## M3 Ultra 512 GiB measured receipt

Hardware / run identity:

- Apple M3 Ultra, **512 GiB** unified memory;
- DeepSeek-V4.1-Flash-oQ4e;
- `code_python` workload;
- temperature 1, top_p 1, top_k 0;
- prefix caching off;
- 4K warm-up;
- up to 2K prefill chunks;
- 128 generated tokens;
- each table row is one sampled run;
- model-loading time excluded.

### Engram resident in RAM

| context | PP MTP OFF -> ON | TG OFF | TG MTP ON | peak MLX GiB | peak RSS GiB |
|---:|---:|---:|---:|---:|---:|
| 4K | 457.99 -> 452.15 | 20.23 | 32.06 | 404.04 | 403.16 |
| 16K | 459.12 -> 454.77 | 20.00 | 34.72 | 404.52 | 403.19 |
| 32K | 452.19 -> 447.73 | 19.80 | 31.51 | 404.54 | 403.22 |
| 64K | 439.39 -> 435.56 | 19.67 | 39.66 | 404.56 | 403.25 |

### Engram SSD offload

| context | PP MTP OFF -> ON | TG OFF | TG MTP ON | peak MLX GiB | peak RSS GiB |
|---:|---:|---:|---:|---:|---:|
| 4K | 458.62 -> 452.48 | 19.96 | 34.45 | 289.60 | 295.05 |
| 16K | 441.40 -> 436.41 | 19.83 | 35.42 | 290.08 | 306.39 |
| 32K | 443.11 -> 442.52 | 19.75 | 34.14 | 290.09 | 315.37 |
| 64K | 429.41 -> 431.74 | 19.58 | 36.00 | 290.12 | 329.09 |

## Interpretation

This is a strong new Apple UMA receipt:

- V4.1 oQ4e already achieves roughly **430-460 tok/s prompt processing** through 64K on M3 Ultra 512 GB;
- single-stream DSpark/Lightning MTP lands roughly **32-40 tok/s** in these 128-token sampled cells;
- keeping Engram on SSD reduces active MLX memory at 64K from **404.56 -> 290.12 GiB**, about **114.44 GiB**;
- the corresponding 64K PP row is nearly flat (**435.56 -> 431.74 tok/s**) while MTP TG is lower (**39.66 -> 36.00 tok/s**) in those single sampled runs;
- SSD-mode RSS rises materially with context (**295.05 -> 329.09 GiB** from 4K to 64K), so active MLX allocation alone is not the residency story.

Do **not** convert the large MTP percentage deltas into a universal multiplier. The rows are sampled, generation length is 128, and acceptance/cycle decomposition is not provided here.

Do **not** extrapolate numerically to M5 Ultra. This result makes a high-performance M5-Ultra/V4.1 lane much more plausible, but no M5 Ultra production receipt exists in this pass.

## Promotion

Create/retain a distinct planning lane:

> **DeepSeek V4.1 Flash — large Apple UMA / future M5 Ultra**

Track at minimum:

- oQ3e/oQ4e/oQ5-ish resident payload;
- Engram resident vs SSD vs hot/cold placement;
- cold PP by context;
- TG with and without DSpark/MTP;
- acceptance / tokens-per-cycle / cycle wall time;
- active MLX, RSS/physical, wired/compressed memory and swap;
- 128K / 256K / 1M validation;
- code / prose / agent / tool / multilingual quality;
- load/materialization peak separately from steady-state serving.

This lane is **informational/future hardware** and does not modify the four canonical target rows.

Validation limitation retained from the PR: broad vision and 1M-context validation remain pending; the reported serving is single-stream Lightning MTP with sequential per-row execution.

---

# FRESH — oMLX #3578: TP2 progressive loading retained unsharded layers

Merged commit:

`f37f7c5b80122e5a55bfa29b39425f7406f9686c` — **2026-09-11 13:27:05 UTC**

PR: `jundot/omlx#3578`

Classification: **FRESH / EXACT MODEL-FAMILY + TWO-NODE MECHANISM / LOAD-MEMORY RECEIPT**.

During progressive tensor-parallel loading, intermediate Python/MLX trees (`flat`, `fixed`, `sharded_fixed`) retained references to the unsharded arrays while newly sharded tensors were materialized. Nodes could therefore hold **up to ~1.5x layer weights during initial load**.

Fix:

- evaluate fixed weights;
- explicitly delete intermediate trees;
- `gc.collect()`;
- `mx.clear_cache()`;
- then materialize the sharded representation;
- repeat cleanup before advancing to progressive layer distribution.

Physical validation:

- **2-node cluster**;
- **Qwen3.8-Flash-Next-REAP-288**;
- **TP2**;
- sharding-phase peak allocation reduced by **~4.2 GiB**;
- maintainer independently verified lower peak with real MLX arrays, identical sharded values and unchanged embeddings.

## Project consequence

This does not say PP2 and TP2 have equal steady-state economics. It says **distributed load-time residency is its own admission phase**.

For our 64-GB/node bring-up, record at least:

1. checkpoint/lazy source residency;
2. fixed/global tensor materialization;
3. sharding/stage-placement transient;
4. final per-node model residency;
5. first-eval/JIT/transformation transient;
6. runtime state/cache headroom.

A steady-state estimate that fits at 58-60 GB can still fail before serving if load transforms temporarily pin whole and sharded copies.

This strongly supports keeping PP2/layer ownership primary for our model-specific architecture while using TP2 as a control, but it is **not a PP2-vs-TP2 speed receipt** and moves no TG/PP target.

---

# FRESH — oMLX #3577: Tahoe / Thunderbolt cluster control transport

Relevant commits:

- `b7090d9f5bf7dcbd9453d374a7763b71c86f44c1` — **13:15:48 UTC**;
- `2a1993a448f3be58c36627712df315a7a53789ca` — **13:28:49 UTC**.

Classification: **FRESH / CLUSTER RELIABILITY / TRANSFER**.

Reported failure mode on macOS 26 Tahoe:

- `/usr/bin/python3`, when spawned non-interactively/background, could silently lose outbound socket connectivity over Thunderbolt bridge interfaces (`10.0.0.x`);
- the active virtual-environment Python connected normally;
- rank coordination could otherwise hang indefinitely.

The revised control plane:

- attempts direct TCP first in auto mode;
- retains a system-proxy fallback for supported failures;
- authenticates before normal stream configuration;
- carries one overall connection deadline across direct and proxy attempts;
- does not reinterpret invalid authentication as a transport failure;
- keeps late-listener connection-refused retry behavior separate from proxy fallback.

The originating PR reports physical validation on a dual-Mac M4 / TB5 bridge with direct connection under 1 ms.

## Project consequence

For the dual-M1 TB4 bring-up, separate:

- **data-plane transport** identity;
- **rank/control-plane transport** identity;
- executable/runtime used for each control socket;
- authentication success;
- connect/handshake deadlines;
- direct vs proxy fallback route.

A cluster that is configured and listening is not necessarily a cluster whose control route executed successfully. Add control-route provenance beside collective-route provenance.

No throughput transfer from TB5/M4 to TB4/M1.

---

# FRESH — oMLX #2595: exact MoE expert offload is a capacity escape hatch

Merged commit:

`6df0d8d6499e86fa8610d8193b3d5b9b6bbc9093` — **2026-09-11 13:36:09 UTC**.

Classification: **FRESH / CAPACITY TRANSFER / NOT A FLASH SPEED RECEIPT**.

Mechanism:

- keep only a configurable expert fraction resident;
- fetch non-resident experts synchronously from the original safetensors checkpoint through mmap slab/whole-tensor reads;
- preserve exact routing; misses change latency, not which expert is selected;
- wrap expert modules before materialization so non-resident expert banks never become resident;
- fixed preallocated slots + LRU replacement avoid allocator churn;
- admission discounts only expert layouts the runtime can actually wrap.

Representative Gemma-4-26B-A4B 4-bit results from the PR:

| resident experts | memory after generation | process peak | decode TG | TTFT |
|---:|---:|---:|---:|---:|
| 100% | 14.20 GB | 14.84 GB | 122.5 | 0.30 s |
| 50% | 7.78 GB | 8.12 GB | 59.4 | 2.9 s |
| 25% | 4.57 GB | 4.85 GB | 40.1 | 9.6 s |
| 12.5% | 2.96 GB | 3.24 GB | 29.3 | 18.1 s |

The implementation has additional live exactness/behavioral checks, but these are **not Flash-Next numbers**.

## Project consequence

For our dual-M1 Flash work:

- expert streaming stays an emergency **capacity** lane, not the preferred canonical speed architecture;
- spend SSD/offload complexity on the sparse PLE/n-gram plane before evicting frequently needed routed-expert weights when memory allows;
- if expert offload is ever tested, record per-layer hit rate, fetch bytes, miss latency, TTFT and sustained task wall-clock—not only TG;
- a calibrated pinned “hot expert subset” is not behaviorally equivalent to exact fetch-on-miss; do not replace misses with skipped experts.

---

# FRESH — llama.cpp #28301: MoE token-tail occupancy changes Metal work

Commit:

`5bda51bfbc62e64193221e639f6ad4e08767d760` — **2026-09-11 11:12:55 UTC**.

Classification: **FRESH / PORTABLE METAL KERNEL MECHANISM**.

`kernel_mul_mm_id` uses an NR1=32 token tile split into two 16-row halves. When a routed expert receives <=16 rows in the final tile, the upper half now skips matrix work instead of executing an empty half.

The change covers both tensor and simdgroup paths and adds explicit boundary cases where experts receive final tiles of:

- 32 rows;
- 1 row;
- 15 rows;
- 16 rows;
- 17 rows.

The benchmark harness also redraws expert IDs between timed iterations so repeated MoE timing cannot benefit from an unrealistically warm fixed routing pattern.

## Blazer consequence

Extend MoE kernel identity beyond `(M,N,K,bits,group-size)` with:

- routed token count per expert;
- distribution/histogram of expert occupancy;
- full-tile vs lower-half-only vs tail fraction;
- expert-ID/cache locality across tokens;
- batch / verify / prefill phase.

This complements earlier shape evidence: a nominally fast packed quant can lose if real expert occupancy strands tile work.

Future expert-aggressive Blazer A/Bs should preserve or replay the same routing/occupancy trace when comparing packing kernels.

---

# FRESH — vLLM #55356: group compact cache writes across speculative layers

Commit:

`1e1060f9988fa188fd243c093610889594ba18fd` — **2026-09-11 15:16:57 UTC**.

Classification: **FRESH / KERNEL-LEVEL TRANSFER**.

The grouped MLA cache insertion path now inserts K/V for all draft layers in one launch, including plain FP8 cache conversion with per-layer scales. The commit reports **4-6x kernel-level improvement for small batches**.

Do not transfer this as a model-level speedup.

## Project consequence

The portable lesson is launch amortization for small state writes:

- MTP head/state insertion;
- recurrent snapshot/cadence writes;
- compact KV/index sidecars;
- per-layer metadata/state materialization.

When several layers perform the same narrow operation at one round boundary, test grouped pointer-array dispatch versus one dispatch per layer. Require exact ownership/lifetime proof before grouping mutable state.

---

# FRESH / OPEN — oMLX #3582: Affine8 long-context KV lane on M5 Pro

PR created **2026-09-11 16:33:49 UTC**, updated **16:39:38 UTC**; open at this pass.

Classification: **FRESH / OPEN EXPERIMENT / STRONGER-HARDWARE KV CAPACITY LANE**.

Hardware:

- Apple M5 Pro 48 GiB;
- Qwen3.8-27B-oQ4e-mtp;
- native attention KV BF16;
- speculation / DFlash / ANE / INT8 activation prefill disabled for the full-model cells.

Affine8 keeps one FP32 scale per token/head vector. At head dimension 256, one K or V vector is reported as **260 bytes**, versus 132 Affine4 and 512 FP16. Across the attention sweep Affine8 uses about **50.8-51.5% of native FP16 cache bytes**.

At 250K, attention-only relative-L2 vs native FP16 is ~0.0093-0.0102 across the reported geometries. The PR explicitly states this is not semantic/retrieval quality proof.

Full-model Qwen3.8 cells:

| prefill rows | generated | PP tok/s | decode tok/s | peak active MLX GiB | sampled physical GiB |
|---:|---:|---:|---:|---:|---:|
| 50K | 128 | 410.3 | 14.3 | 18.98 | 21.71 |
| 150K | 128 | 295.3 | 10.7 | 22.66 | 28.37 |
| 200K | 128 | 259.5 | 9.3 | 24.46 | 31.98 |
| 200K | 4096 | 255.3 | 9.4 | 24.46 | 36.13 |

A 250K request was rejected before generation because estimated peak exceeded that run's dynamic ceiling. That is admission behavior, not a fixed Affine8 model limit.

## Project consequence

Keep KV precision as a separate design axis from weight BPW and from activation precision.

For Qwen/Flash long-context work compare:

- native/BF16 state;
- candidate 8-bit affine state;
- 4-6-bit aggressive state where supported;
- precision of **selection-critical** indexer state separately from value/state bulk.

Promotion requires task-level retrieval/agent quality and continuation stability, not relative-L2 alone.

This does not alter the M1 Max64 Qwen3.8 target or the Flash target.

---

# FRESH / ADJACENT — GLM-5.3 Lightning MTP reinforces all-or-nothing rollback

Commit:

`e92df47c76005ae75c20e73aced4d9f5a2ca4794` — **2026-09-11 12:36:12 UTC**.

Classification: **FRESH / TRANSFER / SPECULATIVE CORRECTNESS**.

The implementation found several recurrent/sparse rollback hazards:

- gate mask must be captured and replayed on the accepted prefix;
- recurrent position must rewind with rejected rows;
- rollback must preflight every participating cache before mutating any of them;
- if one sparse cache cannot undo the tail, do not partially rewind the others;
- accepted count may need to clamp downward until all state families can undo safely;
- speculative head cache with incompatible position semantics should stay committed-only and use a per-cycle clone.

Reported M3 Ultra256 GLM-5.3 oQ4e-mtp receipt: 24.9 TG MTP-off versus 44.1-47.6 TG MTP-on at a 4,233-token warm-prefix prompt, with ~95% acceptance and 3.58 tokens/cycle. This is an adjacent-model transfer only.

## Project consequence

Keep our existing fail-stop rule:

> **preflight the entire rollback/refold transaction, then mutate all owned states; never partially rewind and continue.**

No target movement.

---

# SCREENED / no target movement

## rMLX

No commit after the 10:39:19 UTC cutoff materially changes the current speculative-state plan. The newest surfaced rMLX commit remains before this window.

## antirez/ds4

No post-cutoff DS4 main commit provides a new dual-M1 DS4 rate receipt or changes the DS4-0731 target lane.

## mlx-serve

No post-cutoff main commit appeared in this window. Previously incorporated Qwen3.8 1M work and the MoBA source-specific mining remain in force.

## Exact target-topology receipts

No fresh exact receipt was found for:

- Flash-Next — 2x M1 Max64 / TB4;
- Qwen3.8-27B — one M1 Max64;
- Qwen3.8-27B — RTX 5070 Ti16 fully-resident Q3_K_XL/native-MTP speed lane;
- DS4-0731 — 2x M1 Max64 / TB4.

Rediscovered older web/HF/Reddit cards are not freshness merely because their page was crawled today.

---

# Current project consequences

## Dual-M1 Flash-Next

No target movement. Keep **PP2/layer ownership primary**, TP2 as control.

Add/retain these bring-up and certification requirements:

1. **load-time peak is a benchmark phase** — record source/lazy, transform, sharding/placement and first-eval peaks separately;
2. explicitly release source/intermediate parameter trees before materializing the next representation;
3. control-plane route provenance: direct/proxy, executable, auth, deadline and handshake result;
4. PP/data-plane transport remains separately measured from control-plane transport;
5. expert occupancy/tail geometry is part of MoE kernel identity;
6. grouped small state writes are a candidate only when ownership/lifetime is proven;
7. KV precision and activation precision remain separate from stored-weight BPW;
8. all prior QSA/MTP/recurrent/rollback/content-shape/fusion-census gates remain.

The new TP2 load fix is especially important for 64-GB nodes: steady-state fit does not prove load-time fit.

## Future Blazer / ~5.x BPW

Candidate evaluation now explicitly includes:

- stored-weight precision by tensor class;
- activation execution precision by phase;
- KV/state precision by state class;
- exact `(M,N,K)` + packing/group geometry;
- expert routing occupancy / tail-tile utilization;
- MTP verify-row widths;
- selection-critical state fidelity;
- load/transformation transient memory;
- task/tail robustness and wall-clock-to-solution.

The destination remains a quality-preserving ~5.x-BPW operating point, not a nominal bit-rate contest.

## DeepSeek V4.1 / future large Apple UMA

Promote this to a tracked **future hardware lane**, but not to the canonical target table yet.

The M3 Ultra512 receipt establishes a real Apple baseline. The most useful next evidence will be:

- M5 Max / M5 Ultra exact receipts;
- 128K/256K/1M cells;
- sustained 1K+ generation;
- DSpark acceptance/cycle decomposition;
- load peak and first-eval transient;
- agent/tool/coding quality across oQ3e/oQ4e/higher-quality packs;
- Engram RAM vs SSD vs hybrid residency.

Do not infer M5 Ultra rates from memory-bandwidth ratios alone.

## Qwen3.8-27B M1 Max64 / P69

No target movement and **no P69 experiment movement**.

P69B12 remains frozen/promoted. P69B13 remains the next experiment only from the already measured high-leverage GDN/projection/downstream-tail structure. Do not reopen P69B8, P69B9 or P69B10-C.

## RTX5070Ti16

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed IQ4_XS remains separate capacity evidence.

## DS4-0731 dual M1

No target movement. The V4.1 Apple results belong to a different architecture/model lane.

---

# Standing target table — unchanged

| Model / hardware | Working TG | status | Working cold PP |
|---|---:|---|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | planning objective | **400 tok/s** |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | unchanged | **110 tok/s** |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | fully-resident canonical speed lane | **250 tok/s** |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | unchanged | **180 tok/s** |

No row moved in this pass.

---

# Next-search boundary

This complete external pass ends at:

**2026-09-11 17:48:40 UTC**

Future complete searches start strictly after that timestamp. Source-specific mining and repository-only commits do not advance this boundary.
