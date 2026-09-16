# External runtime watch — 2026-09-16 07:07 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-16 04:31:59 UTC` through the user-request cutoff `2026-09-16 11:07:39 UTC`.

Evidence timestamp is the substantive source / measurement timestamp, not crawler time, rebase time, merge-only activity, or a later merge of older evidence. Merge-only changes whose underlying evidence predates the boundary were screened out.

## Executive result

No exact active-topology receipt appeared for any canonical target. **No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max64: **25 tok/s / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max64/TB4: **15 tok/s / 180 tok/s cold PP**.

This window was nevertheless unusually useful for implementation design:

1. **oMLX #3695 / `4d4750ee`** adds multi-request Lightning MTP and publishes direct Apple M3 Ultra measurements for both Qwen3.8-27B and Qwen3.8-Flash-Next. Flash-Next whole-response aggregate throughput moves **54.12 -> 82.98 tok/s** at one request and **71.74 -> 96.32 tok/s** at two requests. This is strong Apple/MTP mechanism evidence, but it is oQ4e, M3 Ultra, context-unspecified aggregate throughput, not a 128K dual-M1 receipt.
2. **vLLM #57121** catches a pipeline-parallel correctness hole in a hyper-connection model: the declared PP handoff carried `hidden_states` and `residual` but silently dropped deferred HC `post` / `comb` state. vLLM is disabling PP rather than accepting silent wrong output. This directly upgrades our dual-M1 PP bridge state-interface certificate.
3. **vLLM #57128** shows prefix-cache + MTP corruption when the newest recurrent-state checkpoint containing rejected draft state is reused. The correct operation is not “subtract one logical block”; it is “skip the newest actual speculative checkpoint and fall back to the next committed snapshot.”
4. **llama.cpp #26223 / `0a8b29a6`** fixes a Metal route where MoE activations above FP16 range become `inf` and an entire SIMD-group MMA tile becomes NaN. The same model was correct below a 32-row route threshold and all-NaN above it. This adds a hard range/crossover check to our Metal execution-identity ruler.
5. **oMLX `ef07ca6a`** adds layer-streamed calibration for oversized models and exposes several Flash-Next conversion hazards: wrong module identity caused a ~100GB PLE table to materialize, filtering after materialization caused RSS **11 -> 113GB**, training-vs-eval mode changed GDN numerics enough to flip MoE routes, and raw-key sanitizer fallback could create a **349GB** artifact where **206GB** was predicted. These become artifact-certification rules before any speed number counts.
6. **vLLM #57129** fuses sparse-indexer score + exact top-k. Operator speedups grow **2.78x @4K -> 5.40x @64K**, yet E2E generation improves only ~0.7–0.9%. This is another clean reminder to optimize QSA by end-to-end bottleneck share, not isolated kernel multiplier.
7. **vLLM #57140** removes an output-sized temporary/copy from mixed GDN speculative batches. Isolated assembly roughly halves at small sizes, while serving improves ~4% only at some middle batch sizes and is neutral/slightly negative elsewhere. Direct-to-authoritative-buffer mutation is useful, but workload geometry decides whether it matters.
8. **vLLM #57158** proves graph capture can corrupt a reserved null KV block with NaN/huge values. Kernels that gather the sentinel and rely on a zero softmax weight still fail because `0 * NaN = NaN`. Persistent sentinel state must be revalidated after capture/warmup, not merely initialized correctly at boot.
9. **vLLM #57161** collapses a GLM sparse-indexer prefill path from **12 launches to 1** and overlaps independent preparation; local GPU work drops dramatically but prefill-heavy E2E improves only a few percent and decode-heavy traffic is neutral. This is strong transfer evidence for our QSA/indexer launch census and stream-overlap plan.

External web/HF/community screening found no new source-time-qualified exact dual-M1 Flash receipt, exact one-M1 canonical-quant 27B receipt, controlled RTX5070Ti16 canonical target receipt, or dual-M1 DS4 receipt inside this window. A newly indexed oMLX M2 Ultra Flash-Next benchmark and several 5070Ti community results were measurements from September 15 or earlier, so they were not promoted and do not refresh the hard boundary.

---

## Promoted direct Apple evidence — oMLX #3695: concurrent Lightning MTP with request-local state

Source PR created: `2026-09-16 07:23:15 UTC`.
Merged commit: `jundot/omlx 4d4750ee1af9d32bd7eddc5cda5a10ad34ed9786` at `08:10:56 UTC`.

The implementation allows compatible concurrent requests to share draft-head work and target verification while preserving request-local:
- acceptance decisions;
- draft history;
- cache frontier / commit boundary;
- termination / EOS / custom-stop handling.

DeepSeek V4.1 keeps independent target verification. Unsupported architectures retain single-request MTP and fall back to ordinary decoding for multiple requests. Auto-depth and parking use the whole batch's measured cost against ordinary decoding.

### Direct Apple measurements

Hardware: **Apple M3 Ultra, 512 GiB**, MLX 0.32.2. All bodies oQ4e. Direct aligned `BatchGenerator`, auto depth, fresh caches, no warmup, long Python prompts, temp 1, top-p 0.95, top-k 20, 4096 output cap, natural EOS.

These are **whole-response aggregate medians**, including prefill, calibration, parking, and smaller-batch tails — not isolated sustained decode measurements.

| Model | requests | non-MTP | Lightning MTP | delta |
|---|---:|---:|---:|---:|
| Qwen3.8-27B-oQ4e-mtp | 1 | 33.71 | **73.89** | +119.2% |
| Qwen3.8-27B-oQ4e-mtp | 2 | 53.86 | **84.08** | +56.1% |
| Qwen3.8-27B-oQ4e-mtp | 3 | 70.96 | **85.85** | +21.0% |
| Qwen3.8-27B-oQ4e-mtp | 4 | 81.32 | **91.52** | +12.5% |
| Qwen3.8-Flash-Next-oQ4e-mtp | 1 | 54.12 | **82.98** | +53.3% |
| Qwen3.8-Flash-Next-oQ4e-mtp | 2 | 71.74 | **96.32** | +34.3% |
| Qwen3.8-Flash-Next-oQ4e-mtp | 3 | 95.51 | **107.45** | +12.5% |
| Qwen3.8-Flash-Next-oQ4e-mtp | 4 | 111.14 | **116.47** | +4.8% |

Validation included 2K-input/256-output concurrent MTP tests, six concurrent generations for the Qwen/GLM models, cancellation, late join, prefix-cache reuse, streaming/custom-stop behavior, and tested GLM rollback parity with scalar reference.

### What this means for our Flash lane

This is strong evidence that Lightning MTP can remain profitable on Apple after the implementation is mature, and that batching verifier/head work does not require merging request state ownership.

Promoted design rules:
- **Share computation, not commit authority.** Batch compatible draft/verifier math, but acceptance and state commit remain per request.
- Each request owns its MTP history and commit frontier even if a fused verify block spans multiple requests.
- Batch parking/depth control must use measured whole-cycle economics, not acceptance alone.
- Cancellation / late join / custom stop are state-transition tests, not API-only tests.
- For our single-stream dual-M1 target this does **not** imply 82.98 tok/s, because chip, quant, context, topology and metric differ materially.

The result does make “Lightning MTP is probably worth engineering correctly on Apple” stronger than before. It does not move the canonical 40@128K target.

---

## Promoted PP correctness transfer — vLLM #57121: HC deferred state is part of the pipeline interface

Source PR created: `2026-09-16 05:37:18 UTC`.

`Glm5NextForCausalLM` declared pipeline-parallel support even though its PP intermediate object only exposed:
- `hidden_states`;
- `residual`.

The model's multi-hyper-connection layer also holds deferred **`post` / `comb`** state. The code explicitly noted that this state would need to propagate across PP ranks but was currently dropped. Wiring only the obvious tensors would therefore remove the startup error while creating silent incorrect output.

vLLM's fix is to remove the PP capability declaration until the complete state handoff exists.

### Direct transfer to our dual-M1 Flash PP bridge

Qwen3.8-Flash-Next also has hyper-connection/mixer state, so stage ownership cannot be certified from layer boundaries alone.

Before the first real PP performance experiment, produce a **stage-interface state ledger** for every cut:

`state name -> producer -> authoritative owner -> wire representation -> consumer -> commit/rollback boundary -> recovery/cancellation behavior`.

At minimum inventory:
- hidden/residual stream(s);
- HC/mixer deferred pre/post/comb state;
- GDN recurrent state / convolution tail;
- QSA/indexer history and selected-block metadata if the cut crosses ownership;
- PLE state/claim metadata if relevant;
- MTP proposal/head state;
- accepted-prefix / continuation control metadata.

A PP run is invalid if the receiver reconstructs a default/standalone state merely because a side tensor was omitted.

This materially affects the implementation plan: **prove complete PP semantics before optimizing TB4 bytes.** The right state can then be collapsed/projected before transport; missing state cannot be optimized away.

---

## Promoted MTP/prefix-cache correctness — vLLM #57128: drop the newest actual speculative checkpoint, not one logical unit

Source PR created: `2026-09-16 06:31:12 UTC`.

A Mamba/GDN prefix-cache finder accepted `drop_eagle_block` but ignored it. With MTP/EAGLE, the newest recurrent checkpoint can contain state advanced over draft positions that were later rejected. Reusing that checkpoint silently corrupts later requests sharing the prefix.

An older/simple repair — pre-shrink the search ceiling by one logical unit — also fails in current sparse-checkpoint mode because real recurrent snapshots do not exist at every hash/block unit. It can land in a checkpoint gap and produce **0% cache hits**.

The correct semantics are:
1. scan the full available checkpoint window;
2. find actual recurrent snapshots;
3. when speculative tail invalidation applies, skip only the most recent snapshot actually found;
4. continue to the next older, committed snapshot.

Live test: Qwen3.8-27B-NVFP4, 2x RTX5060Ti16, MTP1, prefix cache, max context 131072. A ~24K shared prefix dropped warm-request time from ~77s cold to ~30–32s, with an instrumented real partial hit of 15,440 / ~18,528 available tokens while correctly skipping the newest unverified checkpoint.

### Promoted rule

Speculative cache invalidation is based on **physical committed snapshots**, not logical token arithmetic.

For Flash distributed MTP:
- maintain an explicit accepted commit epoch / snapshot id;
- every KV/GDN/QSA/PLE/MTP side state is either at that epoch or marked uncommitted;
- rollback/prefix reuse chooses the latest common **actual committed** epoch;
- never infer state validity by simply subtracting `draft_depth` tokens or one block unless that arithmetic is proven to map to a real snapshot.

This reinforces the existing accepted-prefix authority and cache-sidecar boundary rules.

---

## Promoted Metal correctness — llama.cpp #26223 / `0a8b29a6`: route threshold can turn FP16 narrowing into total NaN failure

Fresh merged commit timestamp: `2026-09-16 06:37:40 UTC`.

The Metal `mul_mm_id` path narrows F32 activations to FP16 for SIMD-group MMA. Activations above FP16 max (`65504`) become `inf`, and the SIMD-group matrix multiply propagates NaN through the whole tile.

The dangerous part is route dependence:
- below `ne21_mm_id_min = 32`, the mat-vec path keeps values in F32 and is correct;
- at 32+ rows, the matrix path narrows to half and failed.

A real Mistral Small 4 layer reached ~`1e5` activations. On Metal:
- prefill **<32 tokens** was correct;
- prefill **>=32 tokens** produced an entirely NaN vocabulary.

The fix computes max absolute activation, rescales by a power of two to fit FP16, performs the existing MMA, then exactly undoes that scale in the FP32 accumulator. A first serialized reduction cost up to +451%; the final two-stage bandwidth-bound reduction is much cheaper.

Apple M2 Max component cost for the safe path:
- n=32: +1.73% median;
- n=64: +1.30%;
- n=128: +1.80%;
- n=256: +3.98%;
- n=512: +3.74%, +7.20% worst;
- decode mat-vec cells remained noise-level;
- overall 99-case median +1.14%.

### Promoted Metal qualification rules

- Kernel route crossover is part of numerical correctness. Test **both sides of every dispatch threshold**.
- A short-context/low-row correctness pass does not certify a higher-width prefill route.
- Any Metal kernel that narrows a dynamic activation/control operand to FP16 needs either a proven range bound or a runtime-safe scaling strategy.
- Add finite/range assertions to diagnostic builds at HC/GDN/MoE/QSA route boundaries.
- Correctness ladders should include `[threshold-1, threshold, threshold+1]` geometry cells, not only powers of two.
- If the fix adds a reduction/scan, profile whether it serializes the GPU; correctness repair still needs a parallel implementation.

This is transfer evidence, not a Qwen-specific performance receipt, but it is directly applicable to our custom Metal work.

---

## Promoted Flash-Next conversion evidence — oMLX `ef07ca6a`: streaming calibration must preserve runtime identity before touching weights

Fresh substantive commit timestamp: `2026-09-16 09:04:46 UTC`.

This change adds layer-streamed imatrix/sensitivity calibration for models larger than RAM and extends it to the Qwen4-Exp / Flash-Next layout. Several implementation failures are highly relevant to our future pack-building/certification lane.

### 1. Module identity / configuration ordering can materialize the wrong physical state

The PLE runtime needed mmap mode. A pre-load patch could reinstall the model module after the mode had been configured, leaving the layer class bound to a different module object. One path thought PLE was mmap while the constructor thought it was resident.

Observed consequence:
- full ~100GB N-gram table became active;
- streaming budget aborted around **114GB active**.

After configuring the exact module object *after* pre-load patching, active memory stayed **~11.6GB** across layers/rounds on the truncated fixture.

### 2. Filtering after materialization is not filtering

The streamed layer loader originally popped/materialized all PLE shard tensors and only then discarded the unwanted mmap-mode shards.

Observed RSS:
- before: **~11GB -> 113GB** while sourcing PLE;
- after moving the predicate before the pop/materialization: **12.9GB peak** on the same probe.

Rule: exclusion must happen before any read/allocation of the excluded physical tensor.

### 3. Training/eval mode is execution identity

Freshly constructed streamed blocks defaulted to training mode. Qwen-family GDN selected a different fused-kernel path based on `not self.training`. One-BF16-ULP differences were enough to flip borderline MoE routing choices and break bitwise parity against the resident collector.

Calling `block.eval()` restored bitwise routing counts and parity.

### 4. Silent sanitizer/raw-key fallback can create the wrong artifact while appearing successful

On one cache-hit/sensitivity path, sanitizer discovery failed and writing silently fell back to raw checkpoint keys:
- expert stacking did not happen;
- recipe matching missed;
- output became **349GB** instead of the predicted **206GB**.

The path now fails hard when the required sanitizer is unavailable.

### 5. Synthetic model placeholders are not checkpoint parameters

The mmap PLE module registered a synthetic `weight_scale` placeholder not present in the source artifact. Writing it made strict loaders reject the output. It must be stripped rather than treated as serialized source state.

### Promoted artifact gate

Before any benchmark of our generated Q6/Q8/Flash pack:
- certify exact module/runtime identity during calibration;
- force evaluation mode consistently;
- record physical source tensors actually read;
- reject unexpected materialization of excluded/SSD/mmap state;
- require planned output-byte accounting to match emitted artifact within defined tolerance;
- sanitizer/stacking failure is fatal, never a silent passthrough;
- distinguish checkpoint tensors from runtime/synthetic placeholders;
- strict-load the produced artifact and compare routing/state probes against the source model.

This complements the prior missing-FP8-scale finding: artifact construction and runtime correctness must be proven before throughput is meaningful.

---

## Promoted sparse-indexer transfer — vLLM #57129: fused score+top-k has huge operator gain but small E2E gain

Source PR created: `2026-09-16 06:31:59 UTC`.

The proposed backend replaces a DeepGEMM score operation plus separate exact top-k with a fused score/remap path for constrained SM90 decode geometry.

H200 operator speedup vs baseline:
- 4K: **2.78x**;
- 8K: **3.22x**;
- 16K: **3.86x**;
- 32K: **4.61x**;
- 64K: **5.40x**.

Yet serving E2E throughput changes are only about:
- 4K/4K: +0.9%;
- 8K/8K: +0.9%;
- 1K -> 32K: +0.7%;
- 32K -> 1K: +0.7%.

Accuracy comparisons passed for the fused operator.

### Transfer to Flash QSA

- Fuse score/select only after measuring its share of **full verifier cycle** at target context.
- A 5x kernel win can be sub-1% system win if projection, gather, GDN, MoE, synchronization or transport dominates.
- Track `QSA score`, `select`, `gather`, `attention`, `proposal`, `target verify`, and TB4 transport as separate cycle slices.
- Re-run micro-optimization value after each larger bottleneck shift.

This does not reduce the value of QSA work; it changes how we decide which QSA work is worth engineering first.

---

## Promoted GDN/spec transfer — vLLM #57140: write directly into the authoritative output when ownership is clear

Source PR created: `2026-09-16 09:01:42 UTC`.

Mixed speculative/non-speculative GDN batches allocated an output-sized `merged_out`, scattered both partitions into it, then copied the complete tensor into `core_attn_out`. The patch scatters directly into the caller-owned output buffer.

H100 isolated assembly, one GDN layer:
- 32 tokens: eager **35.05 -> 17.95 us**, graph **6.59 -> 5.33 us**;
- 256: **36.71 -> 18.55**, graph **8.92 -> 7.05**;
- 4096: **109.37 -> 75.60**, graph **102.74 -> 71.61**.

But E2E serving on Qwen3.5-4B + MTP3 is geometry-dependent:
- client B1: +0.32%;
- B4: +3.92%;
- B8: +4.10%;
- B16: -1.01%;
- B32: -0.46%.

Some tail-latency cells also regress at high client batch.

### Transfer

- If ownership/order are exact, write directly into the authoritative destination and avoid merge temporaries.
- Do not assume a local copy removal is universally beneficial after graph capture / batching.
- For our primary single-stream lane, prioritize this only where profiling shows a real buffer-copy bubble.
- Any direct-write fusion must preserve aliasing, padding rows and rollback semantics exactly.

---

## Promoted graph/sentinel correctness — vLLM #57158: graph capture can mutate the null block into poison

Source PR created: `2026-09-16 10:36:55 UTC`.

CUDA graph capture runs dummy batches whose block table points at the reserved null block. Capture left block 0 with non-finite data:
- eager slot-0 NoPE: `0.0`;
- PIECEWISE capture slot-0 NoPE: `NaN`;
- PIECEWISE slot-0 RoPE: approximately `3.2e35`.

Sparse attention kernels deliberately clamp invalid indices to slot 0 and rely on a mask to make that contribution zero. That is only valid when the sentinel data itself is finite: `0 * NaN` remains NaN and poisons real tokens.

Zeroing the reserved null block once after capture restored correct output. The report also shows why simply forcing eager is not acceptable as the final answer: on that setup single-stream CUDA-graph throughput was **32.6 tok/s vs 17.2 tok/s eager**.

### Promoted rules

- Reserved/padding/sentinel buffers are **persistent state**, not constants merely because they are conceptually “unused.”
- After warmup/JIT/graph capture, revalidate sentinel finiteness/zero invariants.
- A mask does not sanitize NaN/Inf payloads.
- Dummy/warmup/capture paths must be tested for writes to persistent cache/state.
- For our Metal graph/command-buffer warmup, perform before/after hashes or sentinel probes on KV/QSA/GDN/MTP scratch/state that should remain invariant.

This composes with the previous padded-selection sentinel and zero-length graph-row findings.

---

## Promoted indexer/prefill transfer — vLLM #57161: collapse launches and overlap independent preparation, but judge the whole workload

Source PR created: `2026-09-16 10:59:30 UTC`, inside the cutoff by ~8 minutes.

Fresh GLM-5.3-Flash sparse-indexer work changes kpool compress and scheduling:
- two-pass softmax -> online softmax, reading gate scores once;
- prefill compress/write path **12 launches -> 1**;
- eager pure-prefill can overlap compress/tail writes on an auxiliary stream with top-k-buffer and gather/logits preparation;
- graph/breakable-graph modes use different scheduling to keep capture semantics valid;
- head gate avoids an explicit FP32 input copy while retaining FP32 accumulation/output.

H100 component measurements:
- prefill compress-write wall **154–216 us -> 32–36 us** at n=256/2048/8192 (-79% to -84%);
- summed GPU kernel time at n=2048: **29.0 -> 4.4 us**;
- n=8192: **67.9 -> 6.7 us**;
- Indexer.forward T48: **39.7 -> 22.7 us** (-43%);
- T288: **50.8 -> 30.8 us** (-39%);
- T1024: **94.4 -> 54.3 us** (-42%);
- decode tail remains launch-bound and effectively unchanged.

8x H100 E2E, MTP5:
- 8192-in / 16-out, C1: mean TTFT -3.2%, output throughput +2.7%;
- same prefill-heavy shape at C16: mean E2EL -4.8%, output throughput +5.1%;
- decode-heavy 2048-in / 256-out is neutral/noisy, including a small throughput regression in some cells.

### Transfer to our Flash implementation order

- Build the QSA/indexer **launch census** first; small dependent-kernel chains can be worth collapsing even when individual kernels look fast.
- Prefer single-pass/online reductions where they remove repeated memory reads and intermediate tensors without changing required numerics materially.
- Overlap only genuinely independent work and explicitly gate scheduling by capture/graph mode.
- Separate prefill and decode optimization ledgers; a strong prefill win may be irrelevant to TG.
- Always report E2E after a large microbenchmark win.

For the dual-M1 target, the most relevant analog is to collapse local preparation before TB4 transfer and overlap independent stage-local work with communication, without introducing extra synchronization points.

---

## Fresh items screened but not promoted as target evidence

### External benchmark/community pages

A fresh web screen surfaced:
- an oMLX M2 Ultra Flash-Next performance page dated September 15;
- tracker/aggregator pages for Flash-Next and Qwen3.8-27B;
- several RTX5070Ti community measurements from September 9–12 and August.

They are useful background but their measurement/source times predate this window. They therefore **do not advance the hard freshness boundary and do not move targets**.

### Merge-only repository activity

Several vLLM commits merged during this window whose underlying PR/evidence source was older. Those were deliberately excluded from freshness promotion. A later merge timestamp is not new evidence.

### DS4 / mlx-serve

No fresh source-time-qualified target-changing DS4-0731 or mlx-serve dual-M1 receipt appeared after the boundary. Routine/UI activity was not promoted.

---

## Changes to implementation/certification plan from this pass

Add these explicit gates to the Flash implementation checklist:

1. **PP stage-interface certificate**
   - enumerate hidden/residual + HC `post/comb` + recurrent/QSA/MTP/PLE side state;
   - prove receiver state equals single-device reference at every cut;
   - only then optimize/collapse the TB4 payload.

2. **Physical commit epoch**
   - rollback/prefix reuse chooses actual committed snapshots;
   - never approximate speculative invalidation with logical block subtraction unless proven identical.

3. **Metal route-threshold numeric sweep**
   - test threshold-1 / threshold / threshold+1 for every kernel route crossover;
   - assert finite/range bounds around FP16 narrowing and reductions.

4. **Post-warmup persistent-state audit**
   - sentinel/null rows finite and initialized;
   - graph/JIT/warmup/dummy routes cannot leave cache poison.

5. **Artifact construction certificate**
   - exact runtime module identity and eval mode;
   - filter excluded tensors before materialization;
   - sanitizer/stacking failure is fatal;
   - emitted byte budget checked against plan;
   - strict-load + routing/state parity before perf qualification.

6. **Optimization accounting**
   - microbench improvement is recorded separately from full-cycle and E2E;
   - launch/copy/indexer fusions promoted only after target-context bottleneck accounting;
   - prefill and decode ledgers remain separate.

7. **Lightning MTP state ownership**
   - computation may batch/share;
   - acceptance, commit frontier, rollback, termination and history remain request-owned;
   - distributed rank authority remains explicit for depth/policy and commit.

These additions strengthen correctness and should reduce wasted tuning passes; none changes the current numeric performance target.

---

## Target status after this pass

**Unchanged.**

For dual-M1 Flash, the new Apple Lightning-MTP numbers are encouraging mechanism evidence, but they do not establish our topology/context/quant target. The main new practical consequence is architectural: the PP bridge must propagate the full HC deferred-state contract before we trust any speed result.

Current interpretation remains:
- `<30–34 TG @128K`: important failure / missing mechanism;
- `35–39`: decent but keep tuning;
- `40–45`: realistic core success range;
- `45–50`: good stretch;
- `50–60`: upside only if the major mechanisms stack; not promised and not canonical.

No evidence in this window justifies moving the **40 @ ~128K / 400 cold PP** planning target.

## New hard source-freshness boundary

`2026-09-16 11:07:39 UTC`

The next complete pass must evaluate substantive source/measurement activity **strictly after** this timestamp. Crawler time, merge-only time and rediscovery of older measurements do not qualify.