# Project 51 primary-lane research watch — 2026-09-23 09:53 ET

**Freshness boundary checked:** prior hard boundary **2026-09-23 10:19:31 UTC**. This pass covers substantive evidence through the user cutoff **2026-09-23 13:53:27 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

The strongest fresh result is an exact-family cache-correctness receipt: SGLang now demonstrates on Qwen3.8-Flash-Next that restoring ordinary KV from host while leaving the QSA compressed-index keys stale can produce large divergence, while restoring the QSA sidecar with the KV preserves argmax and packed-MTP acceptance. This materially strengthens Project 51's existing rule that a warm/restored Flash session is a **multi-state-machine restore**, not "KV cache reuse."

Other useful deltas:

1. oMLX #3873 opens a bounded Flash-Next FP16 PLE/HyperConnection path and publishes historical M2 Ultra measurements suggesting large prefill upside, but current-main GDN/L2-verify/MTP correctness is explicitly unfinished.
2. vLLM #58329 proposes layer-owned KV pipeline parallelism. Its supporting cache-pooling data is strong, but its own RFC warns decode-time broadcasts can lose when cache capacity is not the bottleneck. For P51 this strengthens **stage-local state ownership**, not remote per-token KV movement.
3. EXL3 #403 provides a real 90K-135K agent-session DFlash2-vs-MTP comparison: DFlash2 draft acceptance is ~28 points below MTP and does not create a clear session-level win. Keep MTP as the 27B production baseline; DFlash2 remains a challenger that must prove itself on the actual long-agent workload.
4. llama.cpp #29313 is another concrete acceptance-collapse bug caused by runtime graph-allocation corruption rather than the draft model. Acceptance telemetry must be treated as a correctness sensor, not just a quality metric.
5. vLLM #58340 adds the exact metric P51 needs for adaptive verify: **verified draft tokens**, distinct from proposed draft tokens.

No new exact 2x M1 Max / TB4 Flash-Next throughput receipt appeared. No new DASLab / GSQ-RCO xhigh behavioral result appeared. Keep:

- production quant search: **~3.0 / 3.2 / 3.4 / 3.6 average transformer BPW**;
- current likely source-like xhigh region: **~3.3-3.6**, center hypothesis **~3.4-3.5**;
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**;
- planning confidence for >=40 TG: **~70%**;
- 50/500 remains stretch/headline territory.

---

## NEW — SGLang #40916: QSA compressed keys are part of durable Flash cache state

Source:
https://github.com/sgl-project/sglang/pull/40916

This is the most important fresh finding in this window.

On main, Qwen4Exp/Qwen3.8-Flash-Next host-cache restore could restore normal KV while leaving the QSA compressed index keys stale because those keys live outside the ordinary full-KV pool. The restored session then uses stale block-selection state.

Reported failure magnitude on main:
- host-restore KL against a warm reference: **~0.39 to 0.87**.

The PR adds a separately declared host pool for the QSA compressed key state and waits for its layer transfer before the indexer can read it.

Qwen3.8-Flash-Next BF16, TP8 validation:
- host stack: **KV + INDEXER + MAMBA**;
- QSA indexer host storage: **0.91 GB**;
- geometry: 12 layers x 18,446 pages x 4,096 B;
- host-restore KL against warm: **2.9e-3, 4.3e-3, 5.9e-3**;
- argmax: matching;
- packed MTP / EAGLE 3-step acceptance: **3.317 warm vs 3.317 host**;
- chat-format GSM8K: **96.97 with HiCache vs 96.89 without**.

### P51 consequence

Promote this from a general cache principle to an **exact-family hard gate**.

A restorable Flash checkpoint / warm-agent state must version and restore together:

- ordinary target KV;
- QSA compressed/indexer keys and any selection metadata;
- recurrent/GDN checkpoint state;
- PLE/history state needed by the selected runtime;
- draft/MTP cache/history/checkpoint state where speculation is retained;
- PP-stage ownership / cache geometry identity.

A target-KV hit is **not** a valid warm hit if its QSA sidecar is missing or stale.

Restore ordering matters: QSA compressed keys must be complete before any indexer/attention use.

---

## NEW — SGLang #40913-#40917: declare every cache sidecar, fail closed if one is missing

Sources:
- #40913 DSA indexer host-pool declarations
- #40914 separate draft sidecars
- #40915 hybrid-Mamba indexer host pool
- #40916 QSA compressed-key host pool
- #40917 plain-KV assembly through the same declaration system

The stack replaces architecture-specific "remember to also allocate this sidecar" code with explicit device-pool declarations. A declared dependent state pool that is not assembled now fails rather than silently serving with incomplete state.

Related direct evidence:
- GLM-5.3-Flash hybrid-Mamba + stale indexer path on main: KL **0.06 to 0.71**;
- after restoring the declared indexer sidecar: **1.9e-3, 1.6e-3, 3.5e-3**.

### P51 consequence

Adopt a typed state-manifest design rather than implicit cache ownership.

For every P51 stage/model identity, the runtime should be able to enumerate:
- required durable state components;
- shape/dtype/layout;
- owner stage;
- whether state is target-only, draft-only, or shared;
- restore dependency/order;
- version/schema identity.

Missing declared state should **fail closed or force replay**, never silently degrade.

This is directly relevant to the planned SSD sleep/wake tier and PP2 warm-agent restore.

---

## NEW — vLLM #58329: KV pipeline parallelism / layer-owned cache is useful only when capacity/reuse pays for communication

Source:
https://github.com/vllm-project/vllm/issues/58329

The RFC proposes **KV-PP**: each rank persistently owns the KV for a subset of layers and broadcasts a complete layer bundle to the other compute ranks when that layer runs.

Important state-contract detail:
- one ownership bundle includes the layer's main KV, indexer cache and associated scales;
- draft caches that must remain rank-local are excluded;
- scratch buffers are temporary and must not be advertised as durable state.

Supporting Ascend A5 cache-pooling evidence with ~90% shared prefix:
- one node / 8 dies input throughput: **66,362.5 -> 97,318.3 tok/s (+46.65%)**;
- HBM prefix-hit rate: **8.46% -> 45.46%**;
- two nodes / 16 dies / PP2: **86,438.8 -> 125,699.3 tok/s (+45.42%)**;
- HBM prefix-hit rate: **0.59% -> 53.87%**;
- cited logical KV capacity increase: **5.35x-8.17x**.

But the RFC also reports the important counterexample:
- when there is no capacity-constrained pooling benefit, KV-PP produces **2.30%-12.77% lower input-token throughput** in the cited A5 tests.

The RFC explicitly says simple layer-ahead broadcasting is much harder to hide during decode because per-token compute is small.

### P51 consequence

This strengthens, rather than weakens, our PP2 design:

- persistent state should remain **stage-local**;
- a layer bundle includes KV + indexer + scales/sidecars, not KV alone;
- do **not** add per-token cross-TB4 KV broadcasts just because layer-sharded storage works in cache-pooling regimes;
- TB4 should continue carrying the minimum stage-boundary activation/control traffic.

KV-PP is useful evidence for **ownership semantics and cache-capacity economics**, not a new P51 decode topology.

No TG/PP forecast credit.

---

## NEW — oMLX #3873: Flash-Next FP16 PLE + HyperConnection work opens the M1/M2 FP16 lane, but GDN/MTP is not ready

Source:
https://github.com/jundot/omlx/pull/3873

Created in this window.

The draft fixes two Qwen4Exp FP16 incompatibilities while preserving packed oQ weights:

- PLE mmap/FP8 row decoding now preserves the loaded shared scale's compute dtype instead of forcing BF16-specific behavior;
- fused HyperConnection decode/prefill paths accept uniform FP16 metadata and QuantizedLinear subclasses.

Current branch validation:
- combined PLE + HC suites: **131 passed**;
- existing Qwen4 compatibility: **67 passed, 2 failed**, with the same two tiny FP32 exact-equality failures reproducing on untouched base;
- full model serving and full repository suite are **not** acceptance-complete;
- current-main FP16 GDN decode and Qwen4 **L2** verify remain unfinished;
- MTP/cache rollback acceptance remains unfinished.

### Historical M2 Ultra motivation published with the PR

Local dev2 experiment, M2 Ultra 128 GB, packed oQ4e-mtp, adaptive Lightning MTP, cold prefix cache:

| prompt | BF16 PP | FP16 PP | BF16 TG | FP16 TG |
|---:|---:|---:|---:|---:|
| ~4K | 451.7 | **527.7** | **42.5** | 38.6 |
| ~31K | 585.3 | **805.9** | 36.6 | **42.1** |
| ~62K | 578.9 | **796.8** | 33.9 | **38.3** |

Approximate historical deltas:
- PP: +17% at ~4K and ~+38% at ~31K/~62K;
- decode: -9% at ~4K, +15% at ~31K, +13% at ~62K.

### Qualification

These are **historical local records, not reproducible current-PR acceptance**. MTP acceptance varied; one prompt length differs by one token; raw immutable artifacts are not published; and the old GDN path had known migration/correctness defects.

### P51 consequence

Keep **M1-FP16-friendly compute for the protected floating islands** as a high-priority baseline experiment.

The result is especially interesting for cold PP, but receives no numeric target credit until:
- current Qwen4 L2 GDN verify is implemented correctly;
- cache transitions/rollback pass;
- real-model xhigh/tool/agent parity passes;
- balanced current-main A/B exists on Apple7.

---

## UPDATE — oMLX #3869 first MCDMA stage-edge transport merged; #3870 extension remains unvalidated on real hardware

Source:
https://github.com/jundot/omlx/pull/3869

The first MCDMA Mac<->CUDA stage-edge transport from the prior watch is now represented in main commits during this window, including follow-up probe/service-lifetime fixes.

The broader #3870 work (all hops, sampled-token piggyback, remote vLLM prefill) still states that it has not been run on ConnectX hardware or inside live vLLM.

### P51 consequence

Status confidence in the **message/ownership design** rises; throughput confidence does not.

No target change.

---

## NEW — EXL3 #403: DFlash2 loses to native MTP as the stable baseline in a real 90K-135K 27B agent session

Source:
https://github.com/turboderp-org/exllamav3/issues/403

Hardware/runtime:
- RTX 3090 24 GB, 250 W;
- Qwen3.8-27B EXL3 4.00 bpw target;
- third-party Qwen3.8-27B DFlash2 EXL3 4.00-bpw draft;
- exllamav3 1.5.1 plus PR #379 q-aware verify overlay;
- max sequence ~180K;
- real long agentic coding session with heavy prefix reuse.

Acceptance from server logs:

| regime | 30-90K | 100-135K |
|---|---:|---:|
| native MTP | **69% median** | **69% median** |
| DFlash2 | **43% median** | **41% median** |

DFlash2 is roughly **28 acceptance points lower** through the long-context region.

Real-session decode:
- DFlash2 requests: roughly **35.3-51.1 TG**;
- warm MTP requests: roughly **41.5-49.0 TG**;
- full session aggregate: **40.28 TG over 38,464 generated tokens**.

Synthetic contrast:
- 10K, stock token-match verify: **15.2 TG, 53% acceptance**;
- 10K, q-aware overlay: **75.1 TG, 40% acceptance**;
- 100K q-aware: **52.1 TG non-streaming / 43.1 TG streaming, 46% acceptance**.

The q-aware path drafts more tokens per output token and can be dramatically faster in a synthetic prompt while lowering the simple accepted/proposed ratio; that speed advantage did not clearly survive into the real long prefix-cached session.

### P51 consequence

For the RTX 5070 Ti 27B lane:

- keep **native MTP as the production baseline**;
- treat DFlash2 as a challenger, not an assumed upgrade;
- qualify draft quants independently from target quants;
- run the actual 100K+ prefix-cached agent workload before promotion;
- report drafts/token, verified width, accepted useful tokens, verifier cost and E2E TG—not acceptance alone.

This does **not** change the 5070 Ti 120-TG mature target, which was not based on assuming DFlash2.

---

## NEW — llama.cpp #29313: acceptance collapse can be allocator/output-lifetime corruption

Source:
https://github.com/ggml-org/llama.cpp/issues/29313

A stale `ggml_gallocr` graph plan can be reused after tensors change to OUTPUT lifetime. The old allocation plan then aliases multiple outputs that must remain live, and later writes overwrite earlier draft candidates.

EAGLE-3 symptom, five concurrent slots:
- broken backend-sampling path: mean accepted length **1.33**, acceptance **alpha=0.251**;
- backend sampling disabled: mean accepted length **2.10**, acceptance **alpha=0.53**.

### P51 consequence

Add graph/output-liveness to compiled-path identity.

If acceptance suddenly collapses:
1. verify draft numerics;
2. verify target/verify numerical parity;
3. verify cache/checkpoint state;
4. verify graph capture/allocation/output lifetime;
5. only then conclude the draft model itself is weak.

This is another concrete example where speculative acceptance is a **runtime correctness sensor**.

---

## NEW — vLLM #58340: count verified draft tokens separately from proposed draft tokens

Source:
https://github.com/vllm-project/vllm/pull/58340

Adaptive verification can verify fewer tokens than the drafter proposed. Existing "draft tokens total" therefore does not represent actual target verification work.

The PR adds:
- `spec_decode_num_verified_draft_tokens_total`.

### P51 consequence

The mandatory speculative telemetry becomes:

- proposed/drafted tokens;
- **verified draft tokens**;
- accepted/committed tokens;
- accepted tokens per verification pass;
- verification rows/width distribution;
- target-only passes;
- verify wall time / target-forward-equivalents;
- draft wall time;
- MTP park/fallback cycles.

This directly supports the P51 objective:
**accepted useful tokens per expensive target verification cycle**, not raw acceptance percentage.

---

## NEW — vLLM #58343: quantized DFlash2 selector/head ownership work converges on the same loader-identity rule

Source:
https://github.com/vllm-project/vllm/pull/58343

The draft passes quantization settings into DFlash2 selector projections / explicitly owned heads and rejects some missing-head cases instead of silently treating packed tensors as ordinary float parameters.

Validation:
- focused allocation/loading tests pass;
- DFlash2 test file: **12 passed, 10 CUDA tests skipped**;
- **GPU execution, post-load quantized inference and real-checkpoint quality/performance are still pending**.

### P51 consequence

Useful convergent implementation evidence, but weaker than the real-model SGLang quantized-draft receipt from the previous pass.

No target or experiment-order change beyond the already-promoted draft tensor-consumption/load-identity gate.

---

## Checked with no qualifying fresh target evidence

Between the hard boundary and cutoff:

- **DASLab / GSQ-RCO:** no new xhigh-quality receipt or updated weights located; the existing medium-vs-xhigh calibration discussion remains unchanged.
- **MTPLX:** no new commit/PR/issue in-window.
- **official Qwen3.8 repo:** no new commit/PR/issue in-window.
- **MiaAI-Lab dual-DGX-Spark Flash repo:** no new commit/PR/issue in-window.
- **flashnext-hybrid:** no new commit/PR/issue in-window.
- **Weschera single-DGX-Spark Flash repo:** no new commit/PR/issue in-window.
- **PonyExl3:** no new commit/PR in-window.
- **mlx-serve:** no P51-relevant fresh item.
- **DS4:** new #1111 merely asks about the DASLab quant; no substantive reply at this cutoff.
- no new exact **2x M1 Max/TB4 Flash-Next** TG or cold-PP receipt.
- no new **5070 Ti exact-rig** result strong enough to move its canonical target.

## Target / confidence impact

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- single-M1 27B: **25 TG**.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-23 13:53:27 UTC**
