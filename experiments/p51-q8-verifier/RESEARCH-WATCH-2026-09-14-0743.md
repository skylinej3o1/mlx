# External runtime watch — 2026-09-14 07:43 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-14 04:07:40 UTC` through the user-request cutoff `2026-09-14 11:43:49 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawl, rebase, comment-only activity or merge-only churn. Several PRs merged in this window but were already measured before the boundary; those are not reclassified as fresh.

**New hard source-freshness boundary for the next complete external search: `2026-09-14 11:43:49 UTC`.**

One edge case is intentionally excluded: vLLM #56822 was created at `2026-09-14 11:43:58 UTC`, nine seconds after this cutoff. It should be the first item examined in the next complete pass.

---

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured internal GDN/projection/downstream-tail evidence.**

Recent Apple Flash evidence continues to support treating 40 tok/s @ ~128K as a credible success floor for a fully tuned implementation, while 50+ remains a stretch hypothesis until exact dual-M1 measurement exists.

---

# Fresh evidence

## mlx-serve #422 — reuse exact grouped-verifier kernels for single-stream Flash-Next MTP

Source created `2026-09-14 04:20:33 UTC`.

**FRESH NEW / DIRECT APPLE FLASH VERIFIER-MECHANISM RECEIPT.**

The grouped MTP work had already introduced exact, specialized verifier kernels, but a single Flash-Next request still paid the older gather-heavy verifier chain. #422 reuses the same exact route/indexed-input/down-reuse/reduction machinery for batch-1 verify widths 2..6 and also reuses prepared hyper-connection graphs across rounds.

Physical changes include:

- one route-pack operation per layer;
- indexed gate/up inputs instead of expanded activation copies + implicit index generation;
- adjacent-expert reuse in the down projection;
- fused weighted reduction while preserving stock BF16 reduction order;
- prepared HC graph reuse to remove repeated host graph construction.

The gate remains shape/hardware/dtype/quant aware. The MTP prior is recalibrated for the actual mixed-4/8 Qwen4 physical head rather than incorrectly inheriting the older Q4 prior.

M5 Max 128 GB, mixed-4/8, target/head KV8, single stream, greedy, 300 generated tokens, warm full-prefix restore, auto planner, four runs per arm:

| Context | Control runs tok/s | Candidate runs tok/s | Median gain |
|---|---|---|---:|
| 4K | 92.2 / 95.6 / 98.4 / 99.5 | 101.1 / 102.1 / 105.0 / 104.8 | **+6.6%** |
| 16K | 90.4 / 94.5 / 102.8 / 101.1 | 109.4 / 102.6 / 99.7 / 105.1 | **+6.2%** |
| 64K | 91.6 / 94.6 / 101.2 / 98.6 | 102.0 / 104.2 / 100.4 / 98.2 | **+4.8%** |
| 128K | 83.3 / 84.1 / 88.0 / 80.4 | 89.9 / 86.3 / 97.7 / 90.8 | **+7.9%** |

Exactness qualification compares logits, hidden outputs, recurrent state, PLE, QSA state and logical speculative captures bit-for-bit across eligible widths; forced-depth HTTP comparisons matched output/reasoning/token counts/finish reasons at ~4K, ~16K and ~65K prompts.

**Project consequence:** this is the closest external Apple confirmation yet of the P69-style thesis that verifier-cycle execution itself has meaningful headroom even after MTP is already working. Do not transfer +7.9% to dual M1, but promote the concrete route candidates: indexed expert inputs, adjacent-expert down reuse, fused weighted reduction and prepared-HC graph reuse. These should be examined before inventing new Flash-specific verifier machinery.

## mlx-serve #423 — price 8192-token Flash prefill chunks instead of architecture-capping at 4096

Source created `2026-09-14 07:49:10 UTC`; substantive measurements updated through `11:39:31 UTC`.

**FRESH NEW / DIRECT APPLE LONG-CONTEXT PREFILL + ADMISSION EVIDENCE.**

Flash-Next's request-level prefill chooser could price smaller chunk widths, but an architecture cap prevented the 8192 rung from ever reaching the admission estimator. #423 makes 8192 a candidate only for the long-context-gated architecture and lets live admission decide whether it fits.

Forced 4096 vs 8192, M5 Max 128 GB, mixed-4/8, KV8, MTP on, cold prefill, prefix cache off:

| Context | 4096 PP tok/s | 8192 PP tok/s | Gain | active+cache step |
|---|---:|---:|---:|---:|
| 16K | 1713 | 1799 | +5.0% | 74.7 -> 77.9 GB |
| 64K | 1706 | 1777 | +4.2% | 76.3 -> 79.0 GB |
| 128K | 1644 | 1724 | **+4.9%** | 77.6 -> 80.7 GB |
| 326K | 1589 | 1593 | +0.3% | 82.7 -> 85.9 GB |

The implementation then adds a conservative margin for a newly widened rung because measured quantized-prefill transients can exceed the estimator. The deployed geometry bills roughly 3.64 GiB more for 8192 than 4096 and requires `bill * 1.22 <= available` before taking the wide rung.

Automatic chooser A/B initially showed +11.0% at 128K, but session drift was large. Combining mirror-image run order to cancel the order term gives the more defensible estimates:

- 16K: **+9.7%**;
- 64K: **+8.2%**;
- 128K: **+7.9%**.

The author explicitly frames the honest claim as roughly **+8%**, with a broad +5%..+15% bracket. A 350K request was admitted/completed with 8192 while a 1M bill stepped back to 4096.

**Project consequence:** prefill chunk width should be **priced from actual request geometry and live headroom**, not frozen by model family. For our dual-M1 400-PP objective, sweep 4096/8192 (and any physically valid neighboring width) under the exact PP2 ownership and transient layout, with a safety margin based on measured active+reserved peak. The gain is a mechanism receipt, not a dual-M1 calibration.

## ds4 #1041 — eliminate per-layer Metal waits in single-box V4.1 decode

Source created `2026-09-14 11:18:27 UTC`.

**FRESH NEW / STRONG METAL COMMAND-SCHEDULING TRANSFER.**

The single-Mac V4.1 path committed **and waited** after every one of 40 layers, while the two-Mac TP path already allowed command buffers to remain queued. #1041 queues single-box layers too, draining only at the Engram reuse boundary (layer 13) and the final layer; an additional variant commits each queued layer without waiting so the GPU begins work while the CPU encodes the next layer.

M3 Ultra 512 GB, fully resident DeepSeek-V4.1-Flash-Q4, ABBA same binary, generated text byte-identical:

- 2K / 128: per-layer drain **17.08 / 16.78** vs queued **21.73 / 21.72 tok/s**;
- 16K / 128: **16.67 / 16.68** vs **21.47 / 21.42**;
- 2K / 512: **16.68 -> 21.60**;
- queue + commit-per-layer at 2K / 256: **21.63 -> 23.08 / 23.09**.

GPU-stage timing explains the effect:

- per-layer waits: **37.3 ms GPU busy inside 46.9 ms span**, leaving ~9.6 ms scheduling gap;
- queued: **36.9 ms busy inside 37.7 ms span**, leaving ~0.75 ms gap.

It composes with #1035's parallel Engram reads to **24.86 tok/s**, +48% vs the prior default on that M3 Ultra configuration.

**Transfer:** this is V4.1/M3-Ultra evidence, not DS4-0731 or dual-M1 target evidence. But the mechanism is directly relevant to all Metal work: command-commit boundary and wait boundary are separate execution decisions. Our PP2 ruler should record per-stage CPU encode gap, GPU busy span, commit points and hard synchronization points. Avoid per-layer host waits unless a state/resource dependency proves one is necessary.

## ds4 #1035 — fresh current-upstream revalidation of parallel macOS Engram decode reads

Original PR is older, but the body contains a substantive **2026-09-14 current-upstream revalidation** after the V4.1 CUDA merge and was updated at `11:12:35 UTC`.

**FRESH SUBSTANTIVE REVALIDATION / METAL I/O TRANSFER.**

M2 Ultra 192 GB, V4.1 Flash IQ2_XXS/Q2_K, isolated from streaming-expert slabs, 2,048-token prompt, 512-token decode:

- serial Engram reads mean: **10.205 tok/s**;
- four joined macOS readers: **10.740 tok/s**;
- delta: **+5.2%**;
- all decoded outputs match.

Two observations per arm only; do not overfit the percentage. The important transfer is that tiny scattered host-resident state reads can be parallelized independently from expert slab streaming when ordering and disjoint output ranges are explicit.

## llama.cpp #28889 — top-k/argsort transient allocation can be invisible to admission

Source created `2026-09-14 08:32:42 UTC`.

**FRESH NEW / SPARSE-TOP-K MEMORY-PROVENANCE TRANSFER.**

CUDA argsort chunking targeted ~64 MB of input, but actual `top_k` execution required destination indices, another index set, key copies and CUB scratch. One call could therefore reserve **300–450 MB** at graph execution time even though context creation/admission did not see that transient.

On a 16-GB V100 configuration, DeepSeek-V4 sparse-indexer prefill at a 55K prompt OOMed on the first top-k despite otherwise fitting. Lowering the chunk target to 16 MB bounded the transient near **100 MB** and let the request complete, with no measurable PP change in the reported backend microbenchmarks.

**Promote:** sparse/indexer workspace admission must include the allocator's **actual execution-time transient**, not a logical input-size proxy. This reinforces our existing QSA workspace and route-specific prefill-transient rules.

---

# Recovered older / merge-only evidence in this screen

## oMLX #3654 — expert-major chunking for offloaded MoE prefill

Created `2026-09-13 20:46:46 UTC`, so this is **RECOVERED OLDER EVIDENCE**, despite merging in the current window.

For over-capacity expert offload, token-axis halving repeatedly re-fetched the same experts. Sorting routes by expert and chunking on up to `capacity` distinct experts guarantees each expert is installed at most once per call.

M5 Max 128 GB, Gemma-4-26B-A4B 4-bit, 585-token prompt:

- 50% residency: fetches **6073 -> 1719**, warm TTFT **2.38 -> 0.69 s**;
- 25%: **30302 -> 2675**, **8.87 -> 0.85 s**;
- 12.5%: **64369 -> 2913**, **16.60 -> 0.97 s**;
- decode path unchanged.

Retain as offload/capacity mechanism evidence, not primary resident Flash/DS4 target evidence.

## merge-only items not refreshed

- oMLX #3659 merged after the boundary but its expert-geometry evidence was already in the prior watch.
- mlx-serve #421 merged immediately after the boundary but its cold-MTP calibration evidence was already recorded.
- llama.cpp #28670 merged in this window but its substantive Qwen Flash/SYCL top-k work predates the boundary.

---

# External HF / Reddit screen

Fresh web screening did **not** produce a source-time-qualified post-boundary active-topology receipt.

Resurfaced material includes:

- the already tracked M5 Max 1M mlx-serve post;
- the Sept. 12 M4 Pro 64-GB REAP report around 30 tok/s / ~100 tok/s PP near 100K;
- older M1/M4 Qwen3.8-27B and Flash-Next community cells;
- the newly crawled 3.3-bpw HF model card, whose substantive implementation evidence is already captured from source commits.

No evidence timestamp is refreshed merely because a page was crawled today.

---

# Fresh-screen negatives

- No exact fresh **dual-M1 Flash-Next** TG or PP receipt.
- No exact fresh **M1 Max64 Qwen3.8-27B** receipt.
- No exact fresh **RTX5070Ti16 Qwen3.8-27B** throughput receipt.
- No exact fresh **dual-M1 DS4-0731** receipt.
- No target movement.
- No P69 reorder/reopen.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 control.

Highest-value additions from this pass:

1. **Verifier port queue:** inspect/reproduce mlx-serve #422 primitives — indexed gate/up input, route packing, adjacent-expert down reuse, fused weighted reduction, prepared-HC reuse — against our actual Flash/P69 shape census.
2. **Prefill width sweep:** let 4096/8192 be live admission candidates under exact PP2 geometry; price expert gather + GDN stream + MLP envelope + QSA sheet/workspace + KV + allocator reserve and apply a measured safety margin.
3. **Metal scheduling ruler:** separate command encode, commit, GPU busy and wait spans; prove each per-layer synchronization is necessary. #1041 shows host waits can dominate even when GPU kernel work itself barely changes.
4. retain compact-QSA, exact top-k, minimal QSA history, prefix-sidecar, distributed-MTP, TB4, actual layer ownership, transient admission, cancellation/recovery and 64K/~96K/~128K semantic gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement or internal sequencing change. **P69B12 frozen/promoted; P69B13 next.**

#422 is particularly supportive of the existing P69 thesis: specialized verifier routing/reduction/graph reuse remains worth several percent even in a mature Apple Flash engine. Treat it as an experiment-source list, not as permission to alter P69 order or transfer percentages.

## RTX5070Ti16

No target movement. Prior SM120 stride and concurrent-long-prompt gates remain. No post-boundary exact 5070-Ti receipt appeared.

## DS4-0731 dual M1

No target movement. #1041/#1035 are later-V4.1 and stronger-Apple transfer evidence only. Promote their **scheduling/I/O methodology**, not their percentages.

---

# Standing rules added / reinforced

- Verifier specialization should be audited at the physical route level: route packing, indexed LHS/gathers, expert-pair reuse, weighted reduction and host graph construction are independent cost centers.
- A model-family prefill chunk cap is weaker than request-level transient-aware pricing; wider chunks should be considered only when the exact physical bill plus safety margin fits live headroom.
- Compile/warmup state and cost-table identity remain part of every MTP benchmark cell.
- Command-buffer **commit** and **wait** are separate controls; avoid host waits unless a dependency requires completion, and measure GPU busy span vs scheduling gap.
- Host-resident sparse state reads and large expert-slab reads are distinct I/O shapes and may need different concurrency policies.
- Sparse top-k/argsort scratch must be accounted from real execution-time allocator behavior, not logical input bytes alone.
- Merge time never refreshes older evidence.
- Component percentages never move canonical targets without exact active-topology reproduction.
- **P69 remains isolated.**
