# External runtime research watch — 2026-09-07 06:55 ET

Starting freshness boundary: `377501fa9c7bec9662803c926d97f6aad3e0c1c5` / **2026-09-07 03:42:29 UTC**.

## Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55–60%** | **400 tok/s** | **~55–60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55–60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60–65%** | **250 tok/s** | **~55–60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60–65%** | **180 tok/s** | **~60%** |

**This pass moves no target.** No new sustained receipt surfaced from an exact target topology.

---

## FRESH / material

### rMLX `0cec5a187fb2716d5f45c4bd105b572b6da0aa6e` — partial-accept recurrent tape/refold removes the second model replay

The old speculative partial-accept path could not slice recurrent state to an accepted sequence position, so it restored the pre-round recurrent snapshot and replayed the accepted prefix through the entire model stack. That meant a second full model-weight read on every partial-accept round.

The new path tapes the causal per-position inputs consumed by recurrent layers during the original round, then rebuilds only the accepted prefix by refolding those taped inputs through the recurrence kernel. K/V truncates directly; no second full forward or model-weight reread is required.

Correctness evidence in rMLX:

- synthetic guards and mutation tests for incomplete/unarmed tape state;
- real recurrent-stack refold agrees exactly with the replay it replaced at every accepted length;
- equivalence holds for both one verify-forward and forward-per-token draft geometry;
- the tape accumulates across the per-token forwards used by a two-model drafter;
- the dense hybrid reproduces across forward lengths, while the MoE path can expose forward-geometry differences, so the tape intentionally preserves the geometry under which emitted tokens were originally chosen.

**Classification:** mechanism transfer, not target-hardware rate evidence.

**Promotion:** after the Flash MTP pre-verify snapshot / commit / replay path is certified, test **recurrent tape/refold before deeper drafting or compiled multi-agent MTP**. Measure whole speculative-round wall time, acceptance, refold cost, weight traffic / second-forward elimination, and semantic equivalence.

### oMLX #3494 — cold long-prefill → first MTP cycle can collapse under eager-dispatch contention

M3 Ultra 512 GB, Qwen3.8-Flash-Next oQ4e-mtp, oMLX 0.6.4 plus PR #3469 eager `mx.async_eval`:

- first MTP verify cycle after a >=16K prefill intermittently accepted **0/6** positions;
- adaptive depth then parked MTP and the affected request ran near plain-AR economics;
- reported occurrence **2/13 fresh boots**, both under contention; quiet-window arms were healthy;
- every observed collapse was the boot's first long-prefill request; subsequent long requests were healthy;
- short prompts were healthy;
- an 8192-token context gate on eager dispatch produced **8/8 healthy 16K boots** in the reported mitigation arm.

The reporter localizes the seam to prefill→speculation handoff / scheduling / materialization, not to prefill chunks themselves. Root cause is not yet proven.

**Classification:** other-Apple-hardware issue-level evidence / mechanism transfer; reported speedups and regressions do not calibrate M1 targets.

**Promotion:** add a dedicated `cold engine -> short warmup -> first long prefill -> first MTP cycle` oracle under both quiet and contended conditions. Record first-cycle acceptance and prove recurrent/QSA/MTP handoff state is materialized before speculative step 1.

### LMCache #4984 — multi-step cached restore can be exact without MTP and deterministically corrupt with MTP

Qwen3.8-27B hybrid, 2x RTX3090 TP2, vLLM + LMCache, long prompt stored externally and then local prefix cache reset before deterministic replay:

- after the hybrid-layout fix, MTP off: **9/9 bit-identical** across 2/3/5-chunk prompts;
- a 258K-token retrieve was reported bit-identical twice;
- same fixed base with MTP on: **0/10 identical** when retrieve crossed more than one scheduler step;
- single-step <=2-chunk retrieves were fine;
- waiting for async-store drain was necessary to avoid false passes via recompute.

This separates base hybrid-layout correctness from a distinct multi-step MTP restore failure.

**Classification:** external-runtime correctness evidence; not target-rate evidence.

**Promotion:** session/external-cache qualification now requires:

1. proven cache hit and completed store publication;
2. no-MTP multi-step restore equivalence;
3. MTP-on multi-step restore equivalence;
4. single-step success is explicitly insufficient.

### Mesh-LLM #1680 — distributed model identity must be content-addressed, not path/mtime-addressed

A distributed Qwen3.8-Flash-Next GGUF split failed despite identical bytes on both nodes because the synthetic local model identity included file modification time. Matching mtimes made both nodes agree and the split began immediately.

The issue reproduced on M4+M5 with a 68 GB Flash-Next GGUF; three generations then ran at 12.7 tok/s. That throughput is **not** dual-M1 target evidence.

**Promotion:** dual-node startup identity must derive from content digest / canonical model revision plus tokenizer/runtime identity. File path, copy method and mtime are not semantic identity. On mismatch, print both node identifiers and fail closed before split planning.

### llama.cpp `9a7570587ce908b0073a0458877205b80627f393` — converters now emit explicit recurrent-layer manifests

The loader already preferred an explicit `<arch>.attention.recurrent_layers` array, but the converter only emitted `full_attention_interval`. A non-uniform `layer_types` layout could therefore load successfully with wrong layers assigned recurrent vs full-attention operators.

The fix emits an explicit recurrent-layer boolean array and validates `layer_types` length. End-to-end testing on a non-uniform 62-layer Qwen3.8-27B variant reported **0 layer-type mismatches**. Real MTP padding remains untested.

**Promotion:** conversion/startup certification records the explicit recurrent/full-attention layer manifest and compares converter metadata to runtime interpretation. Add a real-MTP padded-array exact test.

### vLLM #55272 — Flash-Next NVIDIA execution route changed; benchmark provenance includes compile/graph route

Merged post-cutoff: the NVIDIA Flash-Next implementation removed model-level `torch.compile` support and custom-op wrappers. The PR notes an approximately 50 GB temporary n-gram-table autotune peak that could OOM a GB300 and shows mixed/noisy throughput changes after removing compile.

**Classification:** NVIDIA execution-route provenance only; not Apple target evidence.

**Promotion:** benchmark receipts stamp graph/compile/eager route and dependency revision. Results across a route change are not silently compared as the same runtime.

### ds4 PR #990 UPDATE — narrow Metal Flash port is a useful mechanism-mining control

The open Metal-only Flash-Next port reports on a single M5 Pro 20-core / 64 GB host, Q2 main weights + Q8 PLE:

- resident footprint ~44.4 GiB;
- generation **30–33 tok/s**;
- prefill **58–73 tok/s**;
- forced sparse vs dense below the selection budget was byte-identical on the reported 1500-token case;
- sparse 3500-token case reported 121 PP / 28.9 TG;
- greedy decode token-identical to the reporter's CPU reference.

Known limits include no MTP, no serialized recurrent/PLE session state, and proof on only one M5 Pro host.

**Classification:** alternative-runtime / Metal mechanism evidence only. It does **not** move dual-M1 Flash targets.

Useful mining surfaces: QSA pooled selection, PLE row-store/no-cache access, 64-GB residency strategy, GDN gate details, sparse-path equivalence tests.

---

## Focused follow-up / no-change

- vLLM #55533 / #55617: no new post-cutoff result; prior physical recurrent-block concurrency corroboration remains standing evidence but is not double-counted as fresh.
- oMLX #3462 / #3464: no material post-cutoff target-rate result surfaced.
- llama.cpp #25187 / #28425 / #28433 / #28448: no material post-cutoff target-rate result surfaced.
- No fresh exact RTX 5070 Ti Tiel result surfaced.

## Exact-rig no-change confirmation

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Updated high-level order:

1. historical pinned llama control;
2. corrected-GDN semantic baseline + reference frontier/state certification;
3. explicit recurrent/full-attention layer-manifest identity + distributed content-addressed model identity;
4. exact PP2/layer-owned baseline; TP2 control;
5. ordinary no-spec recurrent rollback / growing-session correctness;
6. typed cache/state-grid identity + unequal-grid restore;
7. no-MTP batch-composition invariance at concurrency 1/2/3/4, including actual scheduled occupancy;
8. cold-first request + PLE/state epoch ownership;
9. QSA selected-set/tie/order oracle;
10. real-agent cache capture + canonical reusable boundary + async-store follower tests;
11. **multi-step session/cache restore: no-MTP first, then MTP-on**;
12. realistic-depth profiler + explicit MLX carry materialization;
13. QSA horizon / route / footprint accounting and PLE residency;
14. chunk-faithful MTP reconcile;
15. pre-verify snapshot / commit / replay with temporary drafts excluded from persistent history;
16. **cold long-prefill -> first MTP-cycle handoff under quiet and contention**;
17. MTP off/on physical recurrent-capacity accounting;
18. per-slot draft context + adversarial multi-slot isolation + sampler-law certification;
19. **recurrent tape/refold candidate after replay correctness is frozen**;
20. full-vector/frontier/session fingerprints, approximate FP16 lane only after exact freeze;
21. compiled B2/B4, combine passing mechanisms, long prefill while other sessions decode.

Safe serving remains profitable singleton MTP + plain concurrent work until multi-slot state isolation, physical-capacity behavior and multi-step MTP restore are certified.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Keep Qwen resident control and Tiel Q4/Q5 partial-expert-offload plan. Preserve realized backend/placement, offload-slot ownership, whole-round speculative economics and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. External serving findings do not rewrite frozen P69 evidence.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as topology/mechanism evidence until sustained current-head exact dual-M1 generated-token throughput exists.

---

# Standing decisions strengthened this pass

- Partial speculative acceptance should not imply a second full model replay when recurrent inputs can be refolded safely.
- A cold long-prefill -> first speculative cycle is a distinct correctness phase and is tested under contention.
- Single-step cache/session restore does not certify multi-step MTP restore.
- Distributed model identity is content/revision identity, never mtime identity.
- Recurrent/full-attention layer layout is explicit model metadata and part of runtime identity.
- Graph/compile/eager route is benchmark provenance.
- Cross-runtime and other-hardware rates remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
