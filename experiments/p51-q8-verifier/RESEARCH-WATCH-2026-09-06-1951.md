# External runtime research watch — 2026-09-06 19:51 ET

Starting branch checkpoint: `9804a511b1adfaa1726b1858fb7a58c101fccd1b`

Starting hard freshness cutoff: **2026-09-06 22:41:15 UTC**.

## Executive result

This pass is **material for multi-agent scheduling/correctness certification and benchmark integrity, but does not move any canonical TG/PP target**.

No fresh sustained receipt surfaced on the exact 2x M1 Max 64 GB / TB4 Flash topology, the exact 2x M1 Max DS4-0731 topology, the exact M1 Max 64 GB Qwen3.8-27B serving lane, the exact single RTX 5070 Ti Qwen3.8-27B lane, or RTX 5070 Ti Tiel Coder.

The useful changes are:

1. vLLM #55533 now has a focused WIP diagnostic PR (#55617) testing whether **MTP speculative blocks inflate each request's recurrent-state footprint and therefore reduce physically schedulable concurrency**;
2. DeepSeek-V4 Flash concurrency nondeterminism now reproduces **more often with speculative decoding disabled**, after independent attention/MoE/cache/graph swaps, strengthening batch-metadata/state-ownership suspicion rather than a speculative-loop-only explanation;
3. fresh ROCm evidence shows a long-context sparse top-k dispatch rule can become stale when a dependency version advances, reinforcing version-qualified kernel routing and long-context small-N route certification;
4. BACKFILL: rMLX now refuses to record a greedy speculative throughput row unless the speculative arm actually produced the same whole completion as the repeatable plain arm; sampled runs are explicitly classified rather than falsely compared.

`RESEARCH-TARGETS.md` remains untouched.

---

# FRESH / material

## vLLM #55533 + WIP PR #55617 — MTP recurrent-state reserve is now the explicit concurrency hypothesis

Issue #55533 remains the strongest direct evidence that configured batch width can exceed physically schedulable recurrent-state width on a large hybrid GDN model.

Reported Qwen3.8-27B-class behavior remains:

- 48 GDN + 16 full-attention layers;
- MTP k=1;
- batch <=3 healthy;
- batch 8 schedules exactly three sequences per decode iteration (`dist=[2,2,2]`);
- batch 20 MTP throughput ~211 tok/s versus no-spec ~649 tok/s;
- the smaller 24-GDN-layer sibling can schedule much larger batches.

The fresh update is the mechanism test.

A maintainer/contributor explicitly proposes that MTP reserves an extra recurrent/mamba state block per sequence via `num_speculative_blocks = num_speculative_tokens`, increasing `per_req_blocks` and lowering:

`max_concurrency = num_blocks / num_blocks_per_request`.

WIP PR #55617 adds diagnostics for:

- `mamba_cache_mode`;
- speculative-token count;
- cache-group/block details;
- per-request block count;
- resulting max concurrency.

The requested A/B is MTP on versus MTP completely off, otherwise identical. The expected discriminant is whether the recurrent group's `spec_blocks` and `per_req_blocks` shrink and `max_concurrency` rises when speculation is removed.

Important: **this is not confirmed root cause yet**. PR #55617 is diagnostic-only and currently changes no scheduler behavior.

### Promotion

For the dual-M1 appliance, B2-B4 certification must expose both configured and physically backed concurrency:

- requested logical agents / active slots;
- target recurrent rows/columns per slot;
- draft/speculative recurrent reserve per slot;
- total recurrent-state capacity;
- realized per-request state footprint;
- actually scheduled sequences each decode step;
- emitted tokens/sequence/iteration;
- aggregate TG and TTFT distribution.

Add MTP off/on as an explicit physical-capacity A/B. If enabling MTP reduces the number of simultaneously scheduled target sequences, report that as a capacity cost in addition to MTP acceptance/speedup.

This is direct Qwen3.8-27B hybrid GDN scheduling evidence on CUDA, not an Apple performance ruler.

---

## vLLM #53257 UPDATE — concurrency-dependent greedy corruption survives removal of speculation and major kernel swaps

Fresh follow-up on DeepSeek-V4 Flash makes the earlier concurrency nondeterminism more informative.

Same temperature-0 repeated-request test at concurrency 32 / n=500 showed minority-output rates across multiple configurations. Most importantly:

- DSpark enabled variants remained nondeterministic;
- **with speculative decoding completely disabled, all 5 runs were still nondeterministic and the mean minority rate increased to 2.36% (1.80-2.80%)**;
- 0 clean runs out of 26 reported across the matrix.

Independent component swaps did not remove the problem:

- MARLIN vs FlashInfer TRTLLM MoE;
- FlashInfer sparse MLA vs FlashMLA sparse MLA;
- FP4 vs FP8 indexer cache;
- speculative depth 7 vs 5;
- CUDA graphs vs eager;
- prefix cache on vs off.

The reporter therefore narrows suspicion toward something shared by these paths, such as per-step batch metadata, while explicitly noting that this is still a hypothesis.

### Promotion

The Flash multi-agent gate should treat **batch composition/state metadata** as an independent correctness axis before MTP is even enabled:

1. no-MTP, concurrency 1/2/3/4;
2. identical prompts and deliberately different prompt lengths;
3. stable serial reference logits/hash;
4. row/slot/request identity attached to every recurrent/QSA/attention state update;
5. verify that changing only batch width/composition cannot alter a greedy request's position-resolved result beyond the accepted numerical tolerance;
6. only after this passes, add MTP and repeat.

Do not conclude that a passing speculative path proves the base batched path correct; verification can sometimes reject corrupt proposals and partially mask an underlying batch-state defect.

This is DeepSeek-V4/B300 CUDA evidence and therefore mechanism-transfer only for Apple.

---

## vLLM #55615 — dependency-version-qualified long-context small-N routing

Issue created **2026-09-06 22:47:35 UTC**, after the hard cutoff.

On MI355X/gfx950, a sparse-MLA decode top-k dispatch rule disables the AITER path above 64K because of an old AITER 0.1.19 limitation. With AITER 0.1.21.post1, the previously-disabled kernel handles the shape and is faster.

Measured at 40 rows (8 concurrent requests x MTP-5), top-k 2048:

- 65,536 context: 0.0505 ms current fallback vs 0.0383 ms AITER (~24% operator reduction);
- 131,072 context: 0.0785 ms vs 0.0624 ms (~20.5% operator reduction);
- checked selected-index set matched exactly;
- reporter estimates this op is only ~1.1% of total decode TPOT, so end-to-end impact is small.

### Promotion

Kernel-route guards must record the dependency/runtime version that justified them. During baseline bring-up, enumerate long-context small-N routes at representative widths rather than trusting historical version gates.

For Flash-Next specifically, preserve the existing matrix across:

- B1 decode;
- MTP verify widths;
- B2/B4;
- 64K/~128K context;
- selected QSA/top-k route;
- exact selected-set/state oracle;
- operator share of total TPOT before spending optimization effort.

This is ROCm/DeepSeek sparse-MLA transfer evidence, not a numerical Flash target update.

---

# BACKFILL / benchmark-integrity evidence

## rMLX `128932f3379baaf7e4923ddd24cbf50d1dd7b26e` — a faster greedy speculative arm must first answer the same thing

Commit timestamp: **2026-09-06 16:50:48 UTC**. It predates this pass's cutoff and is therefore BACKFILL.

The speculative benchmark previously compared rates without proving answer equivalence. The new rule is stronger:

- digest the whole completion for every measured run;
- require the plain greedy reference to repeat itself;
- require the greedy speculative arm to match the plain completion run-by-run **before any median throughput is recorded**;
- a divergence anywhere in the completion blocks the row;
- sampled runs are explicitly tagged `answer_check=sampled` rather than incorrectly required to be token-identical;
- partial/ambiguous sampler coverage is refused.

### Promotion

Our benchmark publication rule becomes:

- **greedy exact-semantic lane:** no speed row unless the candidate passes the chosen whole-output + frontier/state equivalence gate against a repeatable reference;
- **sampled lane:** never require token identity between independent draws; certify the sampling law separately and label the throughput row accordingly;
- no benchmark row may silently mix greedy and sampled requests.

This strengthens the rule already implied by the full-vector/state gates: performance data is only meaningful after the semantic class of the run is known.

---

# Focused follow-up status

- **oMLX #3462 / #3464:** no post-cutoff issue activity surfaced; cache-capture efficacy and explicit TG provenance remain active.
- **llama.cpp #25187 / #28425 / #28433 / #28448:** no post-cutoff activity surfaced.
- **llama.cpp:** no new post-cutoff relevant commit surfaced in this pass.
- **oMLX:** no new post-cutoff relevant commit surfaced.
- **ds4:** no new post-cutoff commit surfaced; latest relevant state/session work remains in the prior 18:32 note.
- **rMLX:** no post-cutoff commit surfaced; `128932f...` is BACKFILL.
- **MLX #4409 / packed gated-delta work:** no new target-relevant update surfaced.
- **vLLM #55533:** materially updated; WIP diagnostic PR #55617 is active, but no fix/root-cause proof yet.
- **vLLM #53257:** materially updated; no-spec base batching remains nondeterministic under the reported workload.
- **Tiel Coder:** no fresh exact RTX 5070 Ti receipt.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

Therefore canonical targets remain unchanged:

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| Flash-Next — 2x M1 Max 64 / TB4 | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| Qwen3.8-27B — M1 Max 64 | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| Qwen3.8-27B — RTX 5070 Ti 16 GB | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| DS4-0731 — 2x M1 Max 64 / TB4 | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

---

# Updated consequences for dual-M1 Flash-Next

Keep the 18:32 ordering, with these refinements:

1. historical llama control;
2. corrected-GDN semantic baseline + frontier/state certification;
3. exact PP2 baseline / TP2 control;
4. ordinary no-spec recurrent rollback;
5. typed state-grid identities;
6. **no-MTP batch-composition invariance before speculative testing**;
7. cache/PLE epoch ownership and real-agent reuse;
8. warm-slot PP + Metal interior-mask proof;
9. realistic-depth profiler and long-context route matrix;
10. MTP reconcile + pre-verify snapshot/commit/replay;
11. **MTP off/on recurrent-capacity accounting: target rows + speculative rows + actual scheduled sequences**;
12. per-slot draft-context and adversarial multi-slot isolation;
13. sampled-law certification;
14. full-vector/session-byte identity;
15. compiled B2/B4 and combined mechanisms only after those gates pass.

For the intended appliance workload, mild concurrency remains an important upside hypothesis, but the certification language should now be explicit:

> aggregate scaling is measured only over requests that are simultaneously physically scheduled with independent correct state; configured or queued slots do not count as active concurrency.

Safe serving remains profitable singleton MTP + plain concurrent work until multi-slot state isolation and physical-capacity behavior are proven.

---

# Standing decisions strengthened this pass

- MTP can consume recurrent-state capacity as well as compute; measure both.
- Configured parallelism is not scheduled parallelism.
- Greedy batch-composition invariance must pass before speculative decoding can be credited with correctness.
- A speculative verifier may partially mask corruption in the underlying base batched path.
- Per-step batch metadata/state ownership is a first-class correctness surface.
- Historical dependency-version guards are not permanent truths; route gates carry version provenance.
- Optimize long-context small-N kernels only after measuring their share of total TPOT.
- A greedy speed row requires semantic equivalence to a repeatable plain reference before recording.
- Sampled performance requires sampling-law certification, not token identity.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.