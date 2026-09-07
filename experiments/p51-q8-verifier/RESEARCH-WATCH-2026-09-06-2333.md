# External runtime research watch — 2026-09-06 23:33 ET

Starting freshness boundary: `d2ca23f5082b0a2dfede97fe480c8ddbe26cc1b7` / **2026-09-06 23:55:24 UTC**.

Result: **material certification / measurement-method update; no exact target-rig throughput receipt; all canonical TG / PP targets unchanged.**

---

# FRESH / material

## vLLM #55533 / WIP #55617 UPDATE — physical recurrent-block capacity now strongly corroborates the MTP concurrency cap

The previous pass recorded a plausible mechanism: Qwen3.8-27B-class MTP reserves extra recurrent / Mamba-state blocks per sequence, increasing per-request state footprint and lowering the number of requests the scheduler can physically back at once.

A fresh independent 48 GB Qwen3.8-27B experiment artificially pinned the available recurrent / KV block pool and reproduced the scheduling width almost exactly from block capacity:

- **22–28 blocks -> 3 scheduled requests**;
- **29–35 -> 4**;
- **36 -> 5**;
- **43 -> 6**;
- **57 -> all 8**.

This does not replace the original reporter's requested identical-runtime MTP-on / MTP-off diagnostic, so classify it as **strong corroboration, not final root-cause proof**. PR #55617 remains diagnostic rather than a merged scheduler fix.

**Promotion:** B2–B4 claims must record, in the same run:

- total physically available recurrent-state blocks / rows;
- per-request recurrent footprint;
- MTP speculative reserve;
- configured request / slot count;
- actually scheduled independent sequences per iteration;
- emitted tokens per scheduled sequence / iteration;
- aggregate TG and TTFT.

A configured slot does not count as concurrency unless it owns the required state and is actually scheduled simultaneously.

---

## rMLX #532 / `e14a1d5c55d12786031c56b6dc304775a3423c6d` — lazy MLX execution can invalidate speculative sub-phase timing

Fresh charged-phase instrumentation found that forcing a timer boundary is insufficient if the arrays / captures carried across the boundary remain lazy.

Measured attribution corrections on that host included drafter-time over-reporting of roughly:

- **10%** for DFlash2;
- **58%** for the MTP sidecar;
- **8%** for the Gemma4 assistant.

The previous interpretation that rollback replay was simply billed to the next verify phase was therefore incomplete / wrong for these paths: substantial work could be pulled into the next **draft** by the first consumer of a still-lazy capture / replay result.

The commit added availability / materialization checks and charges the relevant carry before closing a measured phase.

**Promotion:** do not use MLX draft / verify / rollback / capture wall-clock splits to choose optimization work unless phase-boundary carry state is proven materialized. Every charged profiling run records the arrays / state whose availability closes each phase.

This changes attribution and experiment order; it is **not throughput evidence for the M1 target rig**.

---

## vLLM #55637 — request-row metadata can address another request's sparse-attention state without an immediate crash

Fresh sparse-attention debugging found producer / consumer cardinality disagreement where request-row metadata can contain an index outside the block-table row count. The dangerous case is not only an illegal access: an invalid logical request id can sometimes land on another valid memory / KV row and produce plausible but wrong output.

**Promotion:** concurrent and graph-warmup certification treats request-row identity as typed state. For every producer / consumer seam:

- prove metadata row count and live-request cardinality agree;
- bound both the request-row index and the per-request block-column index;
- fail closed on impossible request ids;
- never clamp / alias an invalid request onto a neighboring valid request;
- include mismatched prompt lengths and request arrival / retirement transitions.

This reinforces the existing Apple batch-composition oracle even though the fresh report is CUDA-side transfer evidence.

---

## rMLX #533 / `3b18eb9a39d001f928cd2abc29274f190484c476` — cache publication is not certified until a real follower consumes it correctly

Fresh prompt-cache race work strengthens the async-store gate: bookkeeping order alone does not prove that a concurrent second request can safely consume the newly published prefix.

The test now races a real follower request through the storage seam and requires the restored prefix to produce the same token / content. Related fixture work also forces the eviction condition rather than hoping thread timing happens to create it.

The same work corrected telemetry so one logical request produces one coherent metric event rather than multiple partial observations.

**Promotion:** async cache certification requires:

- store -> publication ordering;
- concurrent follower lookup while the store is in flight / just completed;
- restored-prefix content / state identity;
- same next-token / frontier result as the serial oracle;
- one logical request -> one canonical telemetry record.

---

## vLLM #54975 / `1f778486fc313f3599a6b59e67f65b1c186477fd` — offload buffers need stable slot ownership, not modulo coincidence

Fresh offloader work fixed circular prefetch indexing where wraparound could refill data into a static-buffer slot owned by a different logical stream / module class. The fix preserves slot ownership across prefetch steps rather than relying on `next = (index + step) % count` alone.

**Promotion:** Tiel partial expert offload, PLE offload and any future SSD / host-resident path must record an explicit logical-owner -> physical-slot invariant. Wraparound / reuse is valid only inside the same ownership class.

This is **mechanism-transfer evidence**, not 5070-Ti rate evidence.

---

## rMLX #531 / `2275ab8787a5d416ebae2699d4fd3dc1ddb901a1` — separate performance-row equivalence from near-tie semantic classification

Greedy speculative answer-equivalence coverage expanded and showed an important distinction: a tiny / near-tie arithmetic change can produce a different greedy token without implying recurrent-state corruption.

**Promotion:** keep two layers of policy:

1. **benchmark admission:** a greedy speed row can remain strict and require whole-completion identity to a repeatable plain reference;
2. **failure diagnosis:** when identity fails, record the first divergent frontier, top-two margin and full-vector / state evidence so a near-tie numeric divergence is not automatically labeled state corruption.

This preserves a strict published table without losing diagnostic nuance.

---

## llama.cpp #28522 — large optional tool schemas + parallel tool calls need a dedicated agent-correctness gate

A fresh report across multiple Qwen models describes a large tool schema (~48 optional parameters) compiling / serving incorrectly under parallel tool calls: malformed duplicate keys / missing fields and, in one run, an extended CPU hang. Smaller tool schemas reportedly work; disabling MTP did not fix the behavior.

A contributor could not reproduce the problem from the schema alone and requested fuller verbose logs, so the mechanism remains **unproven / environment-dependent**.

**Promotion:** before calling the appliance agent-ready, qualify:

- large optional-parameter tool schemas;
- compiled grammar / schema field coverage against the original schema;
- two or more parallel tool calls;
- duplicate / missing-key detection;
- request timeout / hang guard;
- MTP-off control.

Treat this as runtime / grammar-compiler correctness evidence, **not model-quality evidence**.

---

# Focused watch status

- **vLLM #55533 / #55617:** materially stronger physical-capacity corroboration; still awaiting the original decisive MTP-on/off diagnostic and a real fix.
- **oMLX #3462 / #3464:** no new post-cutoff target-changing evidence surfaced.
- **llama.cpp #25187 / #28425 / #28433 / #28448:** no new post-cutoff target-changing evidence surfaced.
- **MLX #4409:** no new exact target result surfaced.
- **Tiel Coder:** no fresh exact RTX 5070 Ti result surfaced.
- **ds4:** no fresh exact dual-M1 0731 throughput denominator surfaced.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64 / TB4 generated-token throughput or new exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64 / TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max target-model TG / PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG / PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

Therefore **`RESEARCH-TARGETS.md` remains unchanged**:

- Flash dual M1: **40 TG / 400 cold PP**;
- Qwen3.8-27B M1: **25 TG / 110 PP**;
- Qwen3.8-27B RTX 5070 Ti: **120 TG / 250 PP**;
- DS4-0731 dual M1: **15 TG / 180 PP**.

---

# Updated consequences — Dual-M1 Flash-Next

Keep PP2 / layer ownership primary and TP2 as control.

Current order:

1. historical pinned llama control;
2. corrected-GDN semantic candidate + reference frontier / state certification;
3. exact PP2 / layer-owned baseline; TP2 control;
4. ordinary no-spec recurrent rollback / growing-session correctness;
5. typed cache/state-grid identity + unequal-grid restore;
6. **plain no-MTP batch-composition invariance at concurrency 1/2/3/4, including request-row metadata cardinality / bounds and actual scheduled occupancy**;
7. cache-layout / handler + model / tokenizer / runtime / GDN identity;
8. cold-first request + PLE / state epoch ownership;
9. QSA selected-set / tie / order oracle;
10. **large-schema + parallel-tool-call agent correctness gate**;
11. real-agent cache capture + canonical recurrent / attention reusable boundary;
12. **async store -> real concurrent follower usability**, plus forced eviction / pause progress;
13. warm-slot PP + Metal interior-mask-skip proof;
14. realistic-depth profiler + long-context small-N route/version matrix;
15. **charged-phase profiler with explicit MLX carry-materialization proof** before optimizing by sub-phase time;
16. QSA known-horizon reservation + route / footprint accounting;
17. PLE residency / page-cache / direct-read with explicit slot ownership;
18. chunk-faithful MTP reconcile;
19. pre-verify snapshot / commit / replay with temporary drafts excluded from persistent history;
20. **MTP off/on physical recurrent-capacity accounting: total blocks, per-request blocks, speculative reserve and actually scheduled sequences**;
21. per-slot draft context + adversarial multi-slot isolation;
22. production sampler-law certification;
23. strict greedy benchmark identity + near-tie diagnostic classifier;
24. full-vector frontier / state fingerprints;
25. file / memory session byte identity + semantic restore equivalence;
26. concurrent pure-prefill isolation;
27. M1/M2 activation-FP16 approximate lane after exact freeze;
28. compiled B2/B4; combine passing mechanisms; long prefill while other sessions decode.

Safe serving remains profitable singleton MTP + plain concurrent work until the multi-slot state-isolation and physical-capacity gates pass.

The appliance concurrency claim remains deliberately strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct state. Configured, admitted or queued slots alone do not count.

---

# Other lanes

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the known Qwen resident baseline. For Tiel, keep Q4/Q5 partial expert offload using the 64 GB host-RAM budget rather than defaulting to 3-bit. Add explicit host/offload-slot ownership and realized backend/residency provenance.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External runtime findings do not silently rewrite frozen P69 evidence.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as mechanism / certification evidence until a sustained current-head exact dual-M1 generated-token denominator exists.

---

# Standing decisions strengthened this pass

- Physical recurrent-state capacity is part of concurrency, not merely a memory statistic.
- Configured / admitted slots do not count as active concurrency without simultaneous scheduling and independent correct state.
- MLX sub-phase clocks are inadmissible unless lazy carry work is materialized at the phase boundary.
- Request-row metadata carries typed ownership and must be bounded at producer and consumer seams.
- Invalid request ids fail closed; they must never alias a neighboring valid request.
- Cache publication is not proven until a real concurrent follower consumes the new state correctly.
- Static offload buffers require persistent logical slot ownership across wraparound.
- Strict greedy benchmark identity and semantic near-tie classification are different layers of evidence.
- Agent readiness includes large-schema grammar compilation, parallel tool semantics and hang guards.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
