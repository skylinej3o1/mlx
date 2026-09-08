# External runtime research watch — 2026-09-08 14:38 ET

Starting branch checkpoint: `4331d0ec753ffb3456fe1bd817ebdfc1056143f6`

Starting hard freshness cutoff: **2026-09-08 14:55:14 UTC**.

This pass searched forward from that cutoff across the recurring Apple/CUDA inference sources and exact-rig queries. Evidence is classified by the timestamp of the evidence itself, not by when it was rediscovered.

---

# Executive result

**No performance target moves.** No fresh sustained receipt surfaced from any exact target topology:

- 2x M1 Max 64 GB / TB4 Qwen3.8-Flash-Next;
- 2x M1 Max 64 GB / TB4 DS4-0731;
- one M1 Max 64 GB Qwen3.8-27B mature target lane;
- RTX 5070 Ti 16 GB Qwen3.8-27B;
- RTX 5070 Ti 16 GB Tiel-Coder partial-offload lane.

The pass does materially strengthen the **long-context Flash QSA/MTP plan**, the **warm reasoning/tool-call cache plan**, and the **device state-publication happens-before requirements**.

Canonical targets therefore remain:

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

`RESEARCH-TARGETS.md` remains authoritative.

---

# UPDATE / strongest new measurement evidence

## oMLX #3520 — long-context decode and Lightning-MTP verify rows on gathered QSA

PR: `jundot/omlx#3520`

The underlying implementation commits predate this pass's cutoff, so this is **UPDATE**, not a fresh commit. The PR was revised after the cutoff with the full controlled server benchmark matrix and threshold analysis.

### Exact measured rig

- Apple **M5 Max 128 GB**;
- Qwen3.8-Flash-Next-oQ4e-mtp;
- current-main comparison based on the PR's stated `b908f563` reference;
- 512-token completions;
- contexts from ~3.9K through ~229K;
- fresh server per arm, interleaved chains, two passes per prompt / mean of four as reported.

This is direct Apple/Flash evidence, but it is **not** M1 Max and **not** PP2/TB4, so percentages do not transfer numerically.

### Mechanism 1 — selected-row gather must not copy the whole cache

The old gathered QSA route transposed/reshaped the entire stored KV cache into token-major layout before selecting rows. That made the supposedly sparse path scale with total context.

The replacement selects directly along the token axis of the stored `(B,H,N,D)` cache with `mx.take`.

Reported per-QSA-layer / per-token cost on M5 Max:

| cached tokens | old transpose+reshape | direct selected-row take | dense masked SDPA |
|---:|---:|---:|---:|
| 41K | 0.65 ms | 0.32 ms | 0.43 ms |
| 82K | 0.91 ms | 0.25 ms | 0.42 ms |
| 206K | 1.83 ms | 0.27 ms | 0.66 ms |

The new helper is reported bit-identical to the old gathered helper and its cost is approximately flat with total context.

**Promotion:** a selected-KV route is not qualified merely because it selects a sparse set mathematically. The materialized implementation must also be **O(selected set)** in traffic/work, or at least demonstrate context-flat cost. Any hidden full-cache transpose/copy/materialization fails the optimized cell.

### Mechanism 2 — the backbone decode and target-verify rows must actually take the gathered route

The PR identifies a live-server provenance failure: text-only positions were proven during prefill, but decode and MTP verify steps rebound positions through the mRoPE path and reached the model as rank-three planes. The model's gathered decode eligibility predicate therefore failed and backbone rows silently stayed on dense full-KV attention.

The branch persists a request-level text-only proof established at insert/prefill and realizes it step-by-step for qualifying batch-one decode/verify work. Multimodal, batched or unproven requests remain on the rank-three fail-closed route.

Target verify rows are also routed through the gathered multi-query path when they satisfy the exact eligibility conditions.

**Promotion:** benchmark provenance now distinguishes at least:

- QSA/indexer enabled;
- selected indices actually produced;
- draft head attention route;
- **target backbone decode route**;
- **target verify-row route**;
- materialized selected-KV gather implementation;
- exact position-shape / semantic proof that made the optimized route legal.

A cell where QSA is configured but backbone/verify still reads the dense prefix is not a QSA-decode cell.

### Mechanism 3 — optimization threshold is workload/depth dependent

The initial verify eligibility admitted broadcast-equivalent rank-three mRoPE planes. That incurred two host synchronizations for per-step plane comparison and caused severe short-context regressions under greedy adaptive MTP:

- ~4K: **-14%**;
- ~8K: **-8%**;
- ~16K: **-5%**.

The revised route requires absent/rank-two positions and uses the step-scoped proof instead of tensor comparison.

Reported crossover differs by workload:

- serial decode: ~12K;
- sampled adaptive MTP: ~16K;
- greedy/deeper adaptive MTP: ~36–40K.

The PR therefore uses a conservative default threshold of **32,768** tokens, while noting sampled-only deployments can lower it.

**Promotion:** the long-context route threshold is **not a single architecture constant**. Sweep it separately for:

1. serial / MTP-off decode;
2. realistic sampled MTP;
3. greedy/deeper MTP;
4. the exact native/default MTP depth and any separately qualified deeper depth.

Short-context negative controls are mandatory because a semantically valid optimization can still lose badly below crossover and can perturb the adaptive depth controller.

### Controlled server throughput matrix

#### Serial decode, MTP off, greedy

| context | main | branch | delta |
|---:|---:|---:|---:|
| 3.9K | 62.3 | 62.2 | -0.3% noise |
| 7.7K | 61.1 | 61.4 | +0.5% noise |
| 16K | 59.0 | 59.2 | +0.4% noise |
| 32K | 57.4 | 57.6 | +0.4% noise |
| 63K | 53.1 | 57.5 | **+8.3%** |
| 134K | 46.8 | 55.5 | **+18.5%** |
| 229K | 40.7 | 52.8 | **+29.6%** |

#### Adaptive Lightning MTP, temp=1 / top-p=.95 / top-k=20

| context | main | branch | delta |
|---:|---:|---:|---:|
| 3.9K | 59.7 | 62.5 | reported noise |
| 7.7K | 62.1 | 62.2 | +0.3% |
| 16K | 61.3 | 60.7 | -0.9% |
| 32K | 60.0 | 62.0 | +3.3% |
| 63K | 54.2 | 58.6 | **+8.2%** |
| 134K | 46.7 | 58.6 | **+25.7%** |
| 229K | 41.5 | 52.7 | **+27.0%** |

#### Adaptive Lightning MTP, greedy

| context | main | branch | delta |
|---:|---:|---:|---:|
| 3.9K | 71.2 | 69.8 | -2.1% / noise range |
| 7.7K | 73.1 | 72.6 | -0.7% |
| 16K | 77.7 | 78.1 | +0.6% |
| 32K | 71.3 | 72.2 | +1.2% |
| 63K | 56.1 | 63.5 | **+13.3%** |
| 134K | 48.7 | 65.4 | **+34.3%** |
| 229K | 42.0 | 58.6 | **+39.5%** |

The PR also reports 4–10 point acceptance improvements in an 82K comparison when target verify and drafter are kept on compatible gathered paths (example code 69→73%, prose 64→74%). This is useful diagnostic evidence, but acceptance remains subordinate to emitted tokens / wall-second.

### Dual-M1 Flash consequence

This materially raises confidence that the **~128K degradation problem has an implementation-level selected-KV solution**, but does not move the 30 tok/s @ ~128K planning ladder because the measured hardware/runtime is M5 Max single-node.

For PP2 specifically:

- QSA state and selected K/V stay stage-local;
- do not move a dense prefix across TB4 merely to enable a selected-row path;
- record stage-local selected-row gather bytes and latency;
- record whether target decode and target verify both use gathered QSA;
- run ~16K / 32K / 64K / ~128K plus a deeper stress point;
- run serial, sampled native-depth MTP and greedy/deeper MTP threshold cells separately.

---

# FRESH / MTP paged-boundary publication correctness

## oMLX #3525 / commit `6b21d06ad21aa668d834e0e2ef957dca0bd56d5e`

Fresh commit at **2026-09-08 15:32:48 UTC**.

### Failure

Paged-cache MTP commit alignment was armed lazily by `_detect_boundary_snapshot_need()` only when a snapshot capture was first attempted.

For a prompt **shorter than one cache block**, no prefill capture occurs before the first block boundary. That first boundary is reached during speculative decode. The MTP cycle crossing it could therefore land off-boundary; the cache snapshot was skipped with an observed offset of **2047 or 2049 at the 2048 boundary**; the split-GDN store rejected the block and the output remained uncached.

The fix arms boundary alignment during `add_request`, before decode can cross the first boundary.

### Promotion

MTP/paged-cache commit alignment becomes a **request-admission invariant**, not a feature lazily enabled by the first cache event.

Add an explicit certification cell:

- prompt shorter than block size;
- long sampled speculative output;
- first paged boundary occurs during MTP decode;
- assert committed frontier exactly equals the block boundary;
- assert recurrent/GDN + attention snapshot is accepted;
- assert next request reuses that exact boundary;
- repeat across cancellation/retry and slot reuse.

This complements llama.cpp #28302 from the prior watch:

- #28302: retain the useful recurrent checkpoint after it exists;
- #3525: ensure speculative execution **creates/publishes the useful block-aligned checkpoint in the first place**.

### Broader PR context — cacheability follows rendered-history semantics

The same PR, mostly from earlier commits, fixes reasoning/tool-call output reuse when the next turn preserves that output verbatim in rendered history.

The durable rule is stronger than a model-name heuristic:

> generated output is cacheable only when the exact next-turn rendered token history can prefix-match it.

That means:

- preserved reasoning/native `reasoning_content`: output may be reusable;
- stripped `<think>` output: prompt-only store remains correct;
- tool-call/parser-stop paths must apply the same predicate;
- streaming and non-streaming paths must propagate identical cacheability provenance.

Reported M5 Flash two-turn probe with 3,126-token prompt + 6,000-token answer moved the reusable stored frontier from 2,048 to 8,192 tokens when history preserved the answer/reasoning. Tool-call render probes were reported token-exact in both stock and derived templates.

**Promotion:** warm agent-loop certification records exact stored frontier, exact next-turn prefix match, reused token count and warm wall, separated by streamed/non-streamed/tool-call/reasoning-history mode.

---

# FRESH / device publication happens-before

## NInfer / `b88c0f6fc7e999f13eb2fcf7fc9105ed79a91868`

Fresh commit at **2026-09-08 16:35:48 UTC**.

NInfer's `DeviceBuffer::copy_from_host` performed a pageable host→device `cudaMemcpy` and returned. The patch explicitly synchronizes the default stream before returning because a pageable H2D transfer can otherwise still be in flight when a caller submits a consumer on a non-blocking stream.

The API comment separately states that callers must first order any **prior device accesses to the destination range** before overwriting it.

### Promotion

This cleanly separates two state-publication edges that our certification must prove independently:

1. **old reader → overwrite/upload**: no previous device consumer may still be using the destination state when it is replaced;
2. **upload/capture completion → new reader**: the newly published state must be physically complete/visible before a consumer on another stream/rank begins.

Host metadata such as owner/epoch/range does not prove either edge.

For Apple/PP2 equivalents, use the exact MLX/Metal synchronization primitive appropriate to the path; do not cargo-cult CUDA's default-stream synchronization. The portable invariant is the happens-before relation, not the API call.

---

# SCREENED / useful negative or non-target evidence

## NInfer T=1 L2 prefetch candidate

A post-cutoff merge carries an RTX 5090 / Qwen3.6-35B-A3B target-only decode optimization that prefetches the next layer's projection weights from the MoE down tail.

Reported no-spec decode gain is ~+1.7–1.9%, but at MTP draft=3 the measured effect is approximately zero and T>=2 routes structurally bypass the modified T=1 kernel.

**Screening lesson:** an optimization can be real for target-only T=1 decode and completely disappear under MTP because speculative verify/draft changes the executed kernel geometry. Keep target-only and actual MTP execution identities separate.

No direct promotion to Flash targets.

## Rapid-MLX

Fresh commits are service-doctor / diagnostic tooling (`8ecfee5...`, `620d133...`) rather than Qwen3.8 rate/mechanism evidence. Screened.

## llama.cpp

`f3f1a8f...` changes lazy-loading AUTO behavior for integrated GPUs. It is not an Apple Metal target receipt and adds no relevant rate evidence for this plan. Screened.

## antirez/ds4

`6289c516...` is agent-hint terminal presentation only. Screened.

## Avarok Atlas

Fresh GLM-5.3/KDA native-port work is substantial but belongs to another model lane. It does not alter Qwen3.8/DS4 targets. Screened.

## vLLM sustained Blackwell fault threads

Same-day issue activity continues around hybrid recurrent/MTP/graph instability, including older Qwen3.8-27B incidents, but this pass found no clean new root-cause/fix receipt that supersedes the attribution caution from the 10:48 watch. Do not promote an issue-update timestamp into fresh measured evidence when the incident itself predates the cutoff.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact target-configuration mature-runtime receipt after the cutoff.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt after the cutoff.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt.

---

# Updated dual-M1 Flash certification order

Keep **PP2/layer ownership primary and TP2 as control**.

1. Exact PP2 model/recurrent/QSA identity and distributed lifecycle.
2. Cold-PP harness with real chunking, stage balance and TB4 traffic/bubbles.
3. Mixed-phase correctness: first speculative decode sharing a physical step with another request's continuing chunked prefill.
4. Speculative ownership / rollback / replay with one authoritative committed frontier.
5. Bound verifier hidden capture to the exact drafter-readable horizon.
6. **Admission-time paged-boundary alignment**; short-prompt/long-MTP-output first-boundary crossing.
7. Recurrent checkpoint retention across branch/edit/retry/compaction/reopen; warm `prompt_n`, wall, exact frontier, count and bytes.
8. Render-semantic cacheability for preserved reasoning/tool-call output, with streaming/nonstreaming parity.
9. Native/default MTP depth whole-round baseline.
10. Workload-separated deeper-depth A/Bs and segmented long-generation acceptance/TG.
11. **Realized QSA route certification for backbone decode and target verify**, not only draft/indexer configuration.
12. Selected-KV gather traffic/cost must scale with selected rows, not total dense context.
13. Long-context route threshold sweep by serial / sampled MTP / greedy-deeper MTP, with short-context negative controls.
14. Stage-local GDN/routed-MoE/projection/sync profiling at realistic chunks, including exact active SIMD-lane utilization.
15. Per-quant/per-kernel chunk-width sweep before kernel promotion.
16. Block-history/repeated-work candidate first; double buffering / small-width row split only where exact M1 profiling proves the matching bottleneck.
17. Combine only passing mechanisms and rerun cluster cold PP, ~128K TG, append/live-prefix, branch/retry and real coding-agent wall cells.

For PP2 long context specifically, selected K/V and recurrent/QSA state remain stage-local. Any design that turns sparse attention into dense TB4 traffic fails the intended economics even if single-node math is correct.

---

# Standing decisions strengthened this pass

- "QSA enabled" is insufficient provenance; record the realized attention route of **draft, target decode and target verify**.
- A selected-KV implementation must prove it did not materialize/copy the dense cache as hidden work.
- Selected-row gather cost/bytes are measured against context depth.
- Long-context optimization thresholds are workload/depth specific.
- Short-context negative controls are mandatory for long-context route changes.
- Adaptive-MTP controller state/parking is part of the whole-round result, not noise to discard.
- Acceptance changes are diagnostic; emitted tokens per wall-second remains the objective.
- Text-only / route-eligibility facts are persistent request provenance with step-scoped realization and explicit reset.
- MTP paged-boundary alignment is armed at request admission, before the first speculative decode can cross a cache boundary.
- Short-prompt / long-output cells are required because long prompts can accidentally mask lazy-initialization bugs.
- Cacheability of generated reasoning/tool output is determined by exact next-turn rendered-token semantics.
- Streaming, non-streaming and parser/tool-call paths must propagate the same cacheability provenance.
- Reusable warm state is certified by exact stored/restored frontier identity, not a generic cache-hit flag.
- Old-reader→overwrite and upload-complete→new-reader are separate happens-before requirements.
- Host owner/epoch/range metadata does not establish device completion.
- Target-only T=1 optimizations do not transfer to MTP unless the speculative path executes the same kernel geometry.
- Existing grammar-state, sampler-owner/fallback, fairness, request-slot owner/epoch/range, cancellation/reuse/restart reset, quantized-hook coverage and actual-resolved MTP-depth gates remain active.
- Chunk width remains quant/kernel/topology-specific.
- Cross-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.
