# External runtime research watch — 2026-09-08 08:43 ET

Starting branch checkpoint: `51a5b0ed65657ac4d0ea337ce81d2cc5abf0afe0`

Starting hard freshness cutoff: **2026-09-08 06:47:16 UTC**.

Classification rule:

- **FRESH** = created, merged, committed, commented or materially updated strictly after the cutoff;
- **UPDATE** = fresh activity that changes the status or strength of already-known evidence;
- **BACKFILL** = older evidence newly surfaced and material to experiment design;
- **KNOWN / NO CHANGE** = already represented or unchanged after the cutoff.

---

# Result

This pass found **three fresh material correctness / mechanism results, one fresh QSA monitor item, one fresh speculative-placement cleanup, and one useful older MTP depth backfill**:

1. oMLX #3258 merged to main, upgrading the prior distributed cancellation/cache-agreement repair from reviewed branch evidence to landed mainline behavior;
2. rMLX #545 bounded verifier hidden capture at prefill and incrementally carries only committed conditioning rows, with a measured ~600 MB Metal peak reduction at a 16K DFlash2 prompt;
3. vLLM #55894 isolates a hybrid recurrent + MTP batch-ordering failure where an independently selected drafter backend lowers the global reorder threshold and decode rows silently execute through recurrent prefill kernels;
4. vLLM #55872 adds an opt-in deterministic FlashInfer TopK backend and sharpens the distinction between observed endpoint evidence and unresolved server configuration;
5. llama.cpp #28390 removes an unused Meta backend context for a single-device speculative drafter, reinforcing realized backend-context / VRAM provenance;
6. Ling's reported single-DGX-Spark n=1/2/3 MTP sweep is useful **BACKFILL**: acceptance length rises monotonically while prose throughput falls, strengthening whole-round and workload-specific depth qualification.

No fresh sustained physical receipt surfaced from any of the four exact target rigs. `RESEARCH-TARGETS.md` therefore remains unchanged.

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

---

# FRESH / material

## 1. oMLX #3258 / `94530d8d49541ede9e99ef04a4431ee4953117a6` — distributed request safety actually lands on main

Source: https://github.com/jundot/omlx/pull/3258

Merge/main commit time: **2026-09-08 06:57:56 UTC**.

The 02:38 watch captured maintainer review plus the contributor's repaired branch. Ten minutes after our cutoff, the full change merged to oMLX main as:

`feat(cluster): make TP and pipeline serving request-safe (#3258)`.

The landed integration includes:

- request-scoped `abort_request(request_id)` rather than closing every distributed request;
- bounded `abort_all_requests` drain confirmation requiring both coordinator active-request accounting and rank-side marker telemetry to reach zero;
- an orphan-generator reaper so abandoned consumers cannot leak `_active_requests` and wedge or falsely satisfy quiescence;
- rank-side cancellation on distributed read timeout so a stalled/abandoned request does not keep computing unattended;
- request identity preserved through targeted cancellation and public disconnect paths;
- cancellation bounded at prefill-chunk boundaries and fenced/synchronized before batch mutation;
- persisted distributed prompt snapshots across rank restarts;
- loaded and unloaded prompt-cache clearing on every rank, including peer-local cleanup through enrolled cluster SSH rather than coordinator-local paths;
- rank acknowledgement of cache maintenance;
- synchronized pipeline prompt-cache plans;
- normalized rank response tokens at the server boundary;
- restoration of the integration paths called out during maintainer review.

### Important current-runtime boundary

The merged tree's pipeline compatibility path explicitly documents that **MTP is inactive on the distributed path** and distributed workers currently drive `n_confirmed == 0`.

That distinction matters: request-safe TP/PP mainline support is not evidence that distributed PP+MTP is enabled, let alone certified.

### Promotion to our PP2 qualification

- Treat #3258 as the current mainline reference implementation for distributed cancel/cache lifecycle semantics, not as a performance receipt.
- Retain exact two-Mac tests for targeted cancel during prefill/decode, all-request/watchdog cancel, orphaned stream, stale/future epoch, peer restart, cache clear loaded/unloaded, request-ID continuity and post-cancel slot reuse.
- A rank may release/reuse request-owned state only after the synchronized drain/fence frontier.
- Record **distributed MTP active/inactive** as benchmark provenance. Never infer speculative execution from a cluster-capable runtime or config surface.
- The absence of an original two-Mac rerun in the merge evidence remains a qualification gap for our topology.

This is **FRESH mainline integration correctness evidence**, not an exact dual-M1 rate result.

---

## 2. rMLX #545 / `c86e45dbf9c6eaefbafa050df567382f8dec7915` — bound verifier capture to the drafter's actual read horizon

Source: https://github.com/Pushkinist/rMLX/pull/545

Merged: **2026-09-08 10:45:40 UTC**.

PR title:

`spec: the verifier capture is bounded at prefill, and a round projects only the rows it committed`

This is a strong Apple/MLX mechanism result because it changes both speculative memory construction and the ownership boundary for carried conditioning.

### A. Capture is bounded while prefill is produced, not after full materialization

For DFlash2, `forward_verify_capture_chunked` now takes a trailing-row `CaptureTail` and releases old prefill chunks as they fall outside the drafter-visible tail instead of concatenating every captured hidden row and trimming afterward.

The bound follows the drafter's actual semantics:

- DFlash2: `sliding_window - 1`;
- EAGLE-3: no tail bound because its drafter prefill reads all prompt positions;
- DFlash1 / the cited MTP sidecar: no verifier-prompt capture on this path.

The PR reports that rows entering the round loop remain byte-identical to the previous implementation.

### Measured memory result

On the shipped DFlash2 pair with a **16K prompt**, the bounded prefill capture reduced **Metal peak memory by ~600 MB**, reproduced twice per arm in an independent proof run.

This is a real measured Apple memory result. It is not a Flash-Next M1-Max throughput receipt.

### B. Conditioning projection becomes incremental and commit-scoped

For DFlash2 and DFlash1, the drafter's row-wise conditioning projection (`fc` + `hidden_norm`) is carried across rounds. A new round projects only the rows that round actually committed:

- DFlash2 slides the carried conditioning through its declared window;
- DFlash1 grows full history because the checkpoint declares no window and the reference conditions on all history.

The carried representation is `hidden_size` wide instead of `len(target_layer_ids) * hidden_size`.

The stated reduction from projecting roughly a window to projecting `accept + 1` rows is a **trip-count derivation**, not a throughput measurement. The PR deliberately does not claim a TG gain from it.

### C. One producer owns the definition of a committed round

Shared `committed_rows` is now the single producer of "the accepted prefix of the capture" for both speculative loops. It validates rank/batch/width, refuses empty commits, and feeds the conditioning update.

Each round checks that the rows projected are exactly the rows committed, and request-level accounting independently checks conditioned rows against emitted-in-rounds counts.

This is important for us: the same authoritative committed frontier must drive every derived speculative state update rather than letting capture, conditioning and request accounting reconstruct subtly different frontiers.

### D. Fresh-vs-carried projection is numerically close but not necessarily byte-identical

GPU tests on shipped pairs compare the carried conditioning against a fresh projection:

- DFlash1: gap under one bf16 ULP on every tested row;
- DFlash2: a small multiple of one ULP on three rows out of a few hundred.

The PR attributes the residual to dispatch-height rounding. It can move a near-tie drafter proposal, which can change the accept split and therefore the composition of a later verify block.

One proof run diverged around token ~1010/1024, yet the answer-equivalence oracle placed branch and main at the same rank and within the published ceiling. All six equivalence pairs driving these loops passed; EAGLE-3 and Gemma4-assistant controls stayed byte-identical.

### Promotion to our Flash/MTP plan

1. **Capture horizon is semantic provenance.** Record whether a drafter reads full history, a declared sliding window, or no verifier-prompt hidden capture at all.
2. Bound capture **during production** whenever the exact dependency permits it; do not materialize full prompt hidden state only to throw most of it away.
3. Make one identity-checked committed frontier the producer for conditioning, cache/state updates and round accounting.
4. Compare carried/incremental projections with a fresh reference on the actual model; define the allowed numerical/equivalence criterion explicitly rather than requiring byte identity where execution height legitimately changes rounding.
5. Record realistic-context **peak Metal memory** alongside TG and acceptance. Memory saved before serving can become concurrency/context headroom even when TG is unchanged.
6. Do not turn a reduced operation/trip count into a speed claim until measured with wall/TG A/Bs.

This strengthens the existing recurrent-tape / delayed-commit / replay work without replacing the replay baseline.

---

## 3. vLLM #55894 — a lower drafter reorder threshold can silently corrupt hybrid recurrent MTP state

Source: https://github.com/vllm-project/vllm/issues/55894

Created: **2026-09-08 12:14:05 UTC**.

Environment:

- vLLM 0.27.1; reporter says relevant paths unchanged on main `34b9899`;
- 1x RTX PRO 6000 Blackwell, sm_120;
- `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`;
- hybrid Mamba2 + attention + MoE with in-weights MTP;
- `num_speculative_tokens=3`.

### Root mechanism

The target and speculative drafter choose attention backends independently. The drafter auto-selects FlashInfer, whose builder reports a reorder threshold of **1** in the reported configuration. The target's Mamba2 builders require **1 + k = 4**.

`GPUModelRunner.calculate_reorder_batch_threshold` takes the minimum over attention groups, so the global runner threshold becomes 1.

That allows a continuing chunked-prefill row to remain ahead of 4-token speculative decode rows. Mamba2 later performs its own positional split at threshold 4, so those decode rows behind the continuing prefill are classified as prefill and execute through recurrent prefill kernels.

The prefill path writes state slot 0 rather than the `k` speculative recurrent slots. On the first decode step, the speculative slots have not yet been correctly initialized; the next step reads a slot indexed by `num_accepted - 1`, and recurrent state is thereafter corrupted while API calls continue succeeding.

### Reported controls

| cell | corrupted responses |
|---|---:|
| production flags | 15 + 2 / 400; two other nodes 12 / 400 and 9 / 400 |
| no async scheduling | 14 / 400 |
| prefix caching off | 4 / 400 |
| `max_num_batched_tokens=65536` | 6 / 400 |
| **MTP off** | **0 / 400** |
| force runner reorder threshold to `1+k` | **0 / 400**, 0 misordered prefill steps in 418 |
| pin drafter attention backend to TRITON_ATTN | **0 / 400** |

A mixed workload reportedly reproduces about 0.2-1.6% corruption with production flags and 0/1000 without MTP.

The instrumentation found 75/154 requests corrupted when their **first decode step** landed in the misordered region, versus 1/3246 other requests in the six probed runs.

### Why this matters to our recurrent/GDN serving gates

This is not Apple evidence, and it does not prove the same bug exists in MLX. It establishes a portable scheduler invariant:

- for stateful/recurrent backends, decode-vs-prefill row ordering can be a **correctness requirement**, not merely a performance preference;
- independently chosen target and drafter backends may carry incompatible scheduler requirements;
- taking a global minimum threshold is unsafe when any backend requires stricter ordering to address the correct recurrent state slots.

### Promotion

Add a mixed-phase recurrent/speculative certification cell:

1. long request is in a **continuing chunked prefill**;
2. an independent short request joins and executes its **first speculative decode step** in the same physical batch;
3. compare against isolated/lockstep controls;
4. run MTP on/off and backend-pinned controls;
5. record the realized target backend, drafter backend, each backend's reorder/split requirement and the realized global threshold;
6. prove every decode row used decode-state semantics even when physically mixed with prefill rows.

For B2/B3/B4, simultaneous correct persistent state is therefore not enough. The qualification matrix must also include **mixed phase composition** and slot/state selection under staggered admission.

---

# FRESH / monitor or bounded methodology

## 4. vLLM #55872 — opt-in deterministic FlashInfer TopK backend

Source: https://github.com/vllm-project/vllm/pull/55872

Created: **2026-09-08 10:07:55 UTC**. Open at scan time.

The PR adds an opt-in deterministic FlashInfer TopK route for sparse-attention index selection when values tie at the TopK boundary. It explicitly leaves vLLM's native default unchanged and makes no model-quality or performance claim.

Fresh #54521 discussion points users at this branch for live GB10 validation, but no qualifying end-to-end fix receipt had landed by this pass.

A companion parity collector in the discussion also makes a useful provenance distinction: live endpoint observations can be collected from `/v1/completions` with native prompt logprobs/token IDs while server-side launch/runtime configuration remains unresolved. Its schema marks the source as observed-plus-user-supplied and leaves resolved vLLM config null rather than guessing.

**Promotion:** retain QSA set/order determinism and canonical-order logit tests; allow deterministic TopK to be a separately named route; never fill benchmark provenance with inferred server flags that were not observed.

## 5. llama.cpp #28390 / `415e909d84334a7b1f582229c166aa98be6c4678` — speculative backend contexts must reflect actual placement

Source: https://github.com/ggml-org/llama.cpp/pull/28390

Merged: **2026-09-08 12:44:33 UTC**.

When a single-device drafter was requested with `--spec-draft-device CUDA0` while the target used `-sm tensor`, llama.cpp could still create a Meta backend context that consumed VRAM even though the drafter never used it. The merged change special-cases the single-device drafter so the unnecessary Meta wrapper is not created.

No quantified VRAM result is attached, so this is placement/memory-hygiene evidence, not a performance receipt.

**Promotion:** speculative benchmark provenance records the **actual target and drafter backend contexts created**, not only requested split/device flags. Peak VRAM/context headroom belongs beside realized backend placement. An unused context that consumes scarce VRAM is still a failed optimized-placement cell even if token output is correct.

This is especially relevant to the 5070 lane's residency/headroom discipline, but moves no target.

---

# BACKFILL / useful external MTP depth evidence

## Ling single-DGX-Spark n=1/2/3 sweep — acceptance length can improve while useful throughput gets worse

Source: https://www.reddit.com/r/LocalLLaMA/comments/1w9v4yz/higher_acceptance_length_slower_prose_lings_n123/

The Reddit post surfaced after the previous watch, but the underlying run is described as an **August 22, 2026** single-DGX-Spark test. Classify it as BACKFILL, not fresh target evidence.

Reported cells include:

| `num_speculative_tokens` | n=1 | n=2 | n=3 |
|---|---:|---:|---:|
| mean acceptance length | **1.87** | **2.39** | **2.77** |
| freeform 512-token output | **38.7** | 34.8 | 33.6 tok/s |
| freeform 2048-token output | **37.3** | 33.6 | 31.6 tok/s |
| code 2048-token output | **38.8** | 38.6 | 37.8 tok/s |

The reported baseline isolation was approximately:

- eager / no MTP: 20.8 tok/s;
- CUDA graphs / no MTP: 22.9 tok/s;
- CUDA graphs / MTP n=1: 40.9 tok/s.

The checkpoint reportedly has one native NextN layer, so n>1 autoregressively reuses the same drafter rather than invoking independently trained successive heads.

### Promotion

- **Acceptance length is diagnostic, not the objective.** Optimize useful emitted tokens per wall-second under the target workload.
- Depth is qualified by workload class: code/agent and prose/freeform can respond differently to the same n sweep.
- Record native trained MTP/NextN head count, requested n and how proposals beyond the native head count are generated.
- Certify the native/default shallow depth first; deeper n values are separate correctness + whole-round wall/TG cells.
- For long generations, segment acceptance and TG over the output (for example quarters) to distinguish acceptance decay from context-depth or thermal/runtime slowdown.
- Configured/queued clients still do not count as physical Bn concurrency. The existing B2/B3/B4 definition remains unchanged.

This backfill independently supports the rMLX whole-round economics result; it does not move any Apple or 5070 rate target.

---

# FRESH / screened and no-change checks

- **rMLX #546 / `98e1da8ab3443c59654c77b94ec202e1f82ab579`** is fresh documentation/process cleanup after #545; no new measured runtime claim.
- **antirez/ds4 main:** no post-cutoff main commit; the previously captured #991 experimental Flash-Next prefill work remains the current ds4 transfer evidence.
- **Avarok Atlas:** no post-cutoff commit surfaced.
- **vllm-mlx:** no post-cutoff commit surfaced.
- **vLLM #54521:** fresh discussion now points at #55872 and a client-side parity collector; no fresh end-to-end deterministic-TopK fix receipt yet.
- Broad same-day exact-rig searches did not surface a new sustained dual-M1 Flash, dual-M1 DS4-0731, single-M1-Max64 27B or RTX5070Ti 27B rate receipt.
- Rapid-MLX / MTPLX / other Qwen3.8 hits surfaced by broad search were pre-cutoff results or already represented mechanism lanes, not new exact target receipts.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt.

---

# Updated consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

The current qualification / optimization ordering is now:

1. exact PP2 model/recurrent/QSA identity and distributed request lifecycle;
2. cold-PP harness with real chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase batch-composition correctness, including a new request's first decode while another request is in continuing chunked prefill;
4. exact speculative state ownership, rollback/replay and commit-frontier identity;
5. bound verifier capture to the exact drafter-readable horizon and record realistic-context Metal peak;
6. default/native MTP depth whole-round baseline, then workload-separated deeper-depth A/Bs;
7. long-generation segmented acceptance/TG rather than one aggregate acceptance number;
8. stage-local GDN/routed-MoE/projection/sync profiling at realistic chunks;
9. per-quant/per-kernel chunk-width sweep before kernel promotion;
10. block-history/repeated-work candidate first, double-buffered routed-expert staging only if M1 profiling shows the same exposed load/barrier bottleneck;
11. combine only passing mechanisms and rerun cluster cold PP + append/live-prefix + agent wall tests.

Additional current gates:

- oMLX #3258 is a landed mainline distributed-lifecycle reference, but its current distributed path explicitly has MTP inactive. Distributed MTP remains a separate future certification.
- target and drafter backend/scheduler requirements are independent provenance. A stateful backend's required decode ordering cannot be weakened by another backend's lower threshold.
- one committed frontier drives conditioning/state updates and accounting.
- capture horizon, projection carry semantics, native MTP head count and realized requested depth are explicit provenance.
- peak Metal memory is recorded at realistic prompt depth beside TG/acceptance.
- acceptance length never substitutes for wall/TG.
- retain QSA selected-set **and order** determinism, near-tie tests, actual `top_k`, context depth and realized route.
- retain grammar-state rollback, sampler-owner/fallback, fairness, request-slot ownership, device happens-before, cancellation/reuse/restart resets and quantized hook coverage.
- tape/refold remains post-replay-baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

The strict concurrency definition remains:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

The new scheduler evidence adds that those physical requests must also remain correct under **staggered mixed prefill/decode composition**.

Canonical center remains **40 TG / 400 cold PP**.

## RTX 5070 Ti 16 GB — Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt.

Preserve:

- full residency first;
- realized target/drafter backend placement and sampler path;
- actual backend contexts created, not just requested device/split flags;
- peak VRAM plus context headroom;
- native/default MTP depth first, then workload-specific deeper-depth whole-round A/B;
- staggered mixed-phase recurrent/spec cells if the selected runtime uses hybrid stateful blocks;
- real coding-agent wall-time and answer/equivalence qualification.

Canonical center remains **120 TG / 250 cold PP** for the Qwen3.8-27B lane.

## Single M1 Max64 Qwen3.8-27B

External speculative evidence does not modify the certified verifier stack.

**P69B12 remains frozen/promoted; P69B13 remains next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

Canonical center remains **25 TG / 110 native cold PP**.

## Dual-M1 DS4-0731

No exact-rig rate update. The new rMLX capture/conditioning result is general speculative-state transfer evidence only; it is not a DS4-0731 throughput receipt.

Canonical center remains **15 TG / 180 cold PP**.

---

# Standing decisions strengthened this pass

- Acceptance length is not the optimization objective; useful emitted tokens per wall-second is.
- MTP depth is workload-specific and must be evaluated as a whole speculative round.
- Native trained MTP-head count and requested/resolved depth are benchmark provenance.
- Long-generation MTP qualification segments acceptance and throughput over the generated sequence.
- Capture only the verifier hidden history the drafter can mathematically read; the capture horizon is model semantics, not a universal constant.
- One authoritative committed frontier drives every derived speculative state update.
- Incremental/carried projections need a fresh-reference numerical/equivalence test on the real checkpoint.
- Reduced trip counts are not measured speedups.
- Realistic-context peak memory is a first-class speculative metric.
- Stateful recurrent batch ordering can be a correctness invariant.
- Target and drafter backend selection and their scheduler/reorder requirements are independent realized provenance.
- First-decode-during-continuing-prefill is now an explicit mixed-phase concurrency cell.
- Distributed request safety landing on main does not imply distributed MTP support; actual speculative execution is recorded separately.
- Requested device/split mode does not define realized backend-context allocation.
- QSA deterministic TopK is a separately named route until live validation proves its end-to-end effect.
- Endpoint-observed evidence and user-supplied/unresolved runtime configuration stay distinct.
- Existing grammar-state, sampler-owner, fairness, recurrent rollback, QSA order, persistent-slot ownership, device happens-before and cancellation/reuse/restart gates remain active.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
