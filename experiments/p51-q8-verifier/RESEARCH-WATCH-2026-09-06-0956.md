# External runtime research watch — 2026-09-06 09:56 ET

Starting branch checkpoint: `b67893dc685847fa4a2508ef074a6cff82790984`

Starting hard freshness cutoff: **2026-09-06 11:07:17 UTC**.

## Executive result

This pass is **material for Flash-Next implementation mining, long-context correctness, cache/prefill certification and experiment ordering, but it does not move any canonical TG/PP target**.

No fresh sustained receipt surfaced on the exact 2x M1 Max 64 GB / TB4 Flash topology, exact 2x M1 Max DS4-0731 topology, exact M1 Max 64 GB Qwen3.8-27B topology, exact RTX 5070 Ti 16 GB Qwen3.8-27B topology, or the RTX 5070 Ti Tiel-Coder lane.

The major changes are:

1. antirez/ds4 now has an open Qwen3.8-Flash-Next PR with a serious Metal implementation, external PLE, optional MTP, long-context correctness work and reproducible M3-Ultra performance receipts; treat it as a Flash alternative-runtime/mechanism-mining lane, not an M1 rate ruler;
2. oMLX merged a cluster of directly relevant long-context fixes: eviction-pause progress preservation, chunk-faithful MTP reconciliation, QSA known-horizon reservation, Qwen4-exp route-aware memory accounting and immediate-follow-up cache-store freshness;
3. forced eviction/pause and MTP reconcile are promoted to explicit adversarial correctness oracles, because both can create plausible output while reconstructing the wrong cache state or execution geometry;
4. QSA capacity reservation and physical-footprint accounting move earlier in the Flash long-context sequence;
5. prefix caching must fail closed for cache classes that cannot round-trip through the stored representation, and cache-handler identity joins persistent model/tokenizer/runtime identity in serving provenance;
6. the previous llama.cpp distributed-MTP regression (#28484) is no longer reproducible by its reporter. Retain the measurement discipline it motivated, but downgrade the claimed regression itself.

`RESEARCH-TARGETS.md` remains unchanged.

---

# BACKFILL / material

## antirez/ds4 PR #991 — Qwen3.8 Flash-Next becomes a serious Metal mining/control runtime

PR #991 (`Qwen3.8 flash next`) was created **2026-09-06 09:25:41 UTC**, before this pass's hard cutoff, so it is a backfill rather than a fresh post-cutoff event. It is still open.

PR head:

- fork: `ivanfioravanti/ds4-metal`;
- branch: `qwen3.8-flash-next`;
- head: `236cb2a549d05ea1941a19bd4f154e0abc858661`.

The PR adds:

- Qwen3.8-Flash-Next / `qwen4_exp` Metal inference;
- combined target+MTP model plus required external PLE sidecar;
- optional MTP decode;
- model-specific Metal kernels;
- correctness checks;
- documented benchmarks through 262K context.

### Corrected non-MTP implementation — measured M3 Ultra evidence

Physical setup in the checked-in benchmark report:

- Apple M3 Ultra, 512 GiB unified memory;
- macOS 27.0;
- Qwen3.8-Flash-Next Q4K imatrix combined MTP GGUF;
- external PLE Q4_1 sidecar;
- greedy decode and 262K context validation.

A previous specialized Q4K mid kernel had changed numerical semantics: only **1/256** sampled FP32 logit vectors matched the original reference, with maximum absolute difference **3.043321**. A corrected replacement preserves the original accumulation/lane/block/element order and `qwen4_silu` behavior.

The corrected candidate reports:

- **896/896 full-vocabulary FP32 decode logit vectors byte-identical** to the original numerical reference;
- all top predictions matching;
- maximum difference **0**;
- all 28 frontier-logit dumps and all 14 candidate greedy continuations matching through frontiers from 4K to 262K.

Repeated fresh-8K medians versus the prior performance baseline:

- prefill: **1149.37 -> 1201.06 tok/s (+4.50%)**;
- total decode: **45.59 -> 47.24 tok/s (+3.62%)**;
- steady decode: **45.69 -> 47.45 tok/s**;
- first post-prefill evaluation worsened **23.150 -> 35.498 ms**.

Decode improved at every frontier in both full sweep orders. Representative baseline->candidate values in one sweep:

| context | decode tok/s |
|---:|---:|
| 4K | 45.63 -> 47.31 |
| 8K | 45.44 -> 47.13 |
| 16K | 45.25 -> 46.88 |
| 32K | 45.25 -> 46.79 |
| 65K | 44.86 -> 46.45 |
| 131K | 44.11 -> 45.63 |
| 262K | 42.40 -> 43.64 |

At 262K the two-observation combined medians were prefill **1076.34 -> 1082.79 (+0.60%)** and decode **42.425 -> 43.735 (+3.09%)**.

Long-prefill results were order/noise sensitive: one sweep regressed at 65K/131K while the reverse sweep improved. Do **not** promote a uniform long-context PP gain from those rows. The reported prefill windows also measure newly appended tokens rather than one monolithic cold-prefix ruler.

A one-repetition-per-prompt MTP regression smoke on the corrected candidate preserved output bytes and acceptance counts and measured:

- Hamlet: 60.50 -> 61.53 tok/s;
- Fibonacci: 73.09 -> 74.37 tok/s;
- explanation: 64.40 -> 65.61 tok/s.

### Earlier MTP-specific optimization — useful mechanism evidence, not the final exact engine

The preceding MTP-focused candidate measured on the same M3 Ultra:

| prompt | baseline | candidate | gain | accepted/cycles |
|---|---:|---:|---:|---:|
| Hamlet | 57.40 | **60.51** | +5.4% | 37/56 |
| Fibonacci | 69.29 | **73.31** | +5.8% | 198/201 |
| explanation | 61.49 | **64.87** | +5.5% | 110/145 |

All nine measured pairs preserved generated bytes and acceptance counts. Its exact-sampling regression also matched, and a 1,324-pair / 2,650-token predictor comparison kept all top predictions with maximum logit difference `0.000596046`.

Mechanisms include:

- two-token hyper-connection mixer reuse;
- shared Q/K loads in the GDN two-token verify scan;
- shared input loads for Q4_K expert gate/up work;
- one causal two-token predictor pass after an accepted draft to reduce submissions and weight reads.

However, later long-context work found numerical drift in that older implementation and the corrected non-MTP candidate repaired it. Therefore the ~5–6% MTP rows are **short-case mechanism evidence**, not a whole-engine exact-runtime promotion receipt.

### Consequence

Add ds4 #991 as an explicit Flash mechanism-mining/control runtime. Mine:

- exact two-token GDN/HC kernel geometry;
- Q4_K expert input reuse;
- predictor batching/command-submission reduction;
- its 262K correctness harness and run-order discipline.

Do not transfer M3 Ultra absolute rates or percentages to M1 Max. It moves no target.

---

# FRESH / material

## oMLX `9a544e37f22c493fe281e5d1284c3cadaf44dedb` — eviction pauses can duplicate already-prefilled tokens into KV

Merged **2026-09-06 11:37:54 UTC**.

The adaptive prefill throttle can pause a request after some chunks have already advanced the live cache. The broken path requeued the request with stale cached/remaining counters while the actual cache was ahead. On retry, already-consumed tokens were fed again.

Consequences included:

- duplicated KV spans;
- boundary snapshots one block behind the real logical prefix;
- later stored blocks misaligned to token hashes;
- future prefix hits restoring corrupted state.

A reproduced API sequence stored one request, restored/prefilled another under a throttle pause, then hit that stored prefix from a third request; the corrupted-cache leg produced obviously wrong continuations in repeated trials. MTP exposed the condition through memory pressure but was not the root cause.

A long cold-prompt control also showed the operational cost: a GLM 5.3 Flash oQ2e prompt around 230K tokens paused after ~206K. The old behavior discarded roughly 19 minutes of progress and restarted from zero. The corrected path preserved progress across two pauses and resumed only the remaining suffix.

### Promotion to Flash certification

Add a **forced eviction/pause oracle** before long-context promotion:

- force a pause after multiple completed prefill chunks;
- record logical consumed tokens and every cache family's offset before pause;
- resume and assert the next token index equals the true cache frontier;
- compare post-resume recurrent/QSA/KV state and logits against an uninterrupted chunked control;
- assert boundary-snapshot frontier is exact;
- complete/store the session and prove a later prefix hit is output/logit equivalent.

Cache correctness now explicitly includes progress-commit correctness across scheduler interruptions.

## oMLX `e69d707359eb2f682beacc1802b7dee5b35b4c02` — MTP reconcile must preserve ordinary prefill chunk geometry

Merged **2026-09-06 12:54:35 UTC**.

When MTP fell back to standard decode, `_reconcile_mtp_to_standard` could rebuild an entire 13–30K token history in one forward pass rather than replaying with the generator's normal prefill step size.

That is not only a memory problem. On a sparse-attention/GDN hybrid, one-shot reconstruction can execute a different attention geometry from the original chunked prefill.

A measured GLM 5.3 Flash oQ2e comparison at 2,602 tokens found the one-shot reconstructed cache diverging from a 512-token-chunk reference beginning around layer 7 and across many positions deeper in the model.

The fix rebuilds using the normal generator `prefill_step_size`. A 1,300-token test pins the expected replay shape as `[512, 512, 276]`.

### Promotion

For Flash MTP reconcile/fallback/rollback:

- record the exact original prefill chunk sequence;
- rebuild with the same effective chunk geometry;
- compare recurrent/QSA/KV state and target logits against normal prefill;
- include histories crossing QSA route/indexer thresholds;
- include prefill tails shorter than the nominal minimum chunk.

A cache with the same token count but different construction geometry is not automatically equivalent.

## oMLX Qwen4-exp long-context memory stack — actual route and retained-vs-reclaimable bytes matter

Several post-cutoff commits materially sharpen the long-context memory model.

### `a0a16857301a39eae8ba9c98577063d2ff47b1b5` — bounded masked SDPA256 pricing

Merged **2026-09-06 12:41:49 UTC**.

For head-dim-256 attention, the unfused fallback materializes fp32 score storage. The fix prices that path accordingly, allows supported array masks through the bounded tiled route, and makes the Qwen4 memory profile trust only bounded routes that actually support the observed mask type.

It also prevents stale transient measurements from one route from throttling a later bounded execution regime.

### `58df5bd5e3f75ac25cb5a16697c73374a0a9eded` + `d90d6fcbaa725bb03023f85c339868ab9151a0d6` — Qwen4-exp route-aware prefill accounting

Merged around **2026-09-06 13:28 UTC** as PR #3465.

The stack corrects three coupled problems:

- masked SDPA256 could be priced/routed inconsistently;
- retained allocator growth was treated as token-linear transient work;
- overhead could be assigned to the predicted QSA route rather than the route actually executed, then charged again while already resident.

The new logic separates gathered and dense histories, records the runtime route, treats retained pool growth as part of current footprint, and only re-charges bytes actually reclaimed and therefore potentially needing allocation again.

Reported macOS release-app validation:

| scenario | prompt tokens | cached | result |
|---|---:|---:|---|
| cold multimodal prefill | 180,161 | 0 | completed |
| cached continuation | 190,190 | 178,176 | completed |
| restored-prefix dense-mask replay | 143,711 | 139,264 | completed and later continued >158K |

Before the accounting correction, the restored-prefix replay rejected around 143,711 tokens after predicting another ~26.7 GB. In the corrected run, a first dense-mask chunk retained roughly 30 GB of MLX pool buffers; subsequent chunks were admitted because those retained buffers were recognized as already resident rather than charged a second time.

PR #3465 reports 505 passing tests.

### Promotion

Flash long-context memory qualification must record:

- predicted route and **actual executed route**: gathered vs dense-mask, bounded vs unfused;
- current physical footprint, MLX active memory and model-resident bytes;
- retained pool bytes vs actually reclaimed bytes;
- per-chunk predicted transient and observed footprint delta;
- prefill chunk size and any throttle/re-expansion decision.

Do not turn allocator retention into a recurring per-token charge, and do not trust a route prediction when runtime instrumentation can identify the executed path.

## oMLX #3455 — known-horizon QSA reservation becomes a high-priority long-context Flash candidate

Fresh merged commits:

- `aeb1f68378e13bebccb233be2557d24450383426`;
- follow-up `2393893396610fe3484d9df773973206efafe04b`.

Measured Qwen3.8-Flash-Next-oQ4e-mtp on an M-series 128 GB machine with a ~205K prompt showed the prior capacity-growth policy crossing 196,608 tokens and causing roughly **+12.25 GB** process-footprint growth in one chunk, from about 91.40 to 102.17 GB. It allocated capacity for 393,216 positions even though the model maximum was 262,144, then tripped the hard memory enforcer near the end of prefill.

The change lets prefill reserve a known final horizon once rather than repeatedly growing the QSA/indexer storage. The follow-up covers restored prefixes and integration with boundary snapshots.

This is not exact M1 hardware, but the mechanism maps directly to Flash-Next's long-context QSA state.

### Promotion

Move known-horizon reservation before heavy long-context PP tuning. Record:

- logical horizon;
- reserved and realized QSA/indexer capacity;
- capacity reallocation count and copied bytes;
- physical-footprint delta at each growth boundary;
- restored-prefix and cold-prefix behavior;
- output/logit equivalence.

## oMLX `8827f0956f09ef31b1817aac3598b65ffe330e08` — immediate short follow-ups can race async cache storage

Merged **2026-09-06 13:53:56 UTC**.

A fixed minimum prompt length had allowed an immediate follow-up under 4K tokens to skip in-flight `store_cache` deferral, race the store, and re-prefill every turn even though a useful boundary would shortly become restorable.

The fix bases waiting on the actual reusable overlap instead of raw prompt length:

- at least one full restorable block must overlap;
- a candidate store is ignored if it is more than 16x larger than that restorable overlap.

The regression suite includes a GDN-shaped case with a 2,875-token second turn and a 2,048-token boundary store.

### Promotion

Real-agent cache qualification now needs an **immediate follow-up race cell**, not only settled repeated prompts:

- send the next turn as soon as response completion allows;
- record whether the previous store is still in flight;
- record common/restorable overlap and chosen wait/skip decision;
- measure first-repeat reused/fresh tokens and TTFT;
- compare against a deliberately-settled control.

This strengthens the rule that `cache enabled` and `cache effective` are different claims.

## oMLX cache-layout reconstruction — fail closed on cache classes that cannot round-trip

Fresh commits include:

- `2f6aa9a2c157b3dc13e0b85caec24ef434ce69b3` — refuse prefix reuse for unreconstructible cache classes;
- `b2cb698ffc5989bca92ac9930f6aad2d9c34040b` — skip storage as well for unsupported layouts.

The motivating failure class is an unregistered KV-like cache subclass that structural detection could misidentify as plain `KVCache`. Reconstructing it as plain KV drops extra semantic state such as sliding/ring position. A partial prefix hit can therefore be semantically wrong even if tensor shapes look valid.

### Promotion

Add to persistent serving identity/certification:

- concrete cache class per layer/family;
- handler/registry identity;
- handler round-trip test for every semantically meaningful field;
- partial-hit and exact-hit reconstruction tests;
- fail closed on unknown/unreconstructible cache types.

Model/tokenizer/runtime identity alone is not sufficient if the stored cache representation changes semantics.

## oMLX prefill-tail invariant — throttle may shrink a chunk, never inflate past remaining tokens

Commit `1b8d93b558b656842fd542738d01418ddfaa199a` fixes a related Qwen4-exp prefill invariant. A minimum-chunk floor could inflate the final short tail beyond the tokens actually remaining. MLX slicing silently clamps, so token rows and VLM embeddings could become off by one and PLE could fail during reshape; progress/boundary accounting could also drift.

Fold this into the chunk-geometry gate: every adaptive/throttled chunk must satisfy `1 <= actual_chunk <= remaining_tokens`.

---

# FRESH / supporting or separate-lane evidence

## Qwen3.8-27B ANE memory release/accounting fixes — approximate lane only

Several oMLX commits repair the separate ANE-assisted Qwen27 production lane:

- `4e6eba50744efcec3acf0eeb51e023abc6c47054` clears per-module state caches that otherwise kept ANE bank/native-handle references alive after the nominal release;
- `034ceeec25ec1a9731a007d5ed24bbbbb7ffa130` refreshes ANE transient reserve after VLM-path bank compilation so the scheduler prices the actual compiled surfaces;
- `40b9f23dd18a9514bf4a62b2bfa803c1d7a3e567` fixes headroom escalation so a no-op first callback does not exhaust the retry ladder before the durable ANE-bank release rung.

One live source-build report says Qwen3.8-27B-oQ4e-mtp then completed 65,536 tokens at roughly **397 tok/s prefill** where v0.6.4 had rejected at 4K.

This is **not an exact M1-Max native-runtime ruler**. Hardware is not the user's exact target, and ANE arithmetic is already a separate approximate production lane. Keep the number out of canonical target calibration.

The useful transfer is memory-accounting discipline: compiled-bank resident bytes, releaseability and the actual release action must be measured rather than inferred from RSS or a feature flag.

## llama.cpp PR #28475 — CUDA `MUL_MAT_ID` / MMF races fixed

Merged **2026-09-06 11:45:02 UTC**, merge commit `73a43d1f69345aee8bb186ef4b3172cef892f2e5`.

The PR fixes CUDA racecheck findings in MMID/MMF; the inspected MMID patch adds a warp synchronization after a reduction before compacted expert work is consumed.

There is no exact 5070/Tiel/Qwen speed receipt attached. Treat this as a correctness/provenance update for CUDA MoE experiments: deterministic repeated logits and race-clean execution remain required before promoting a faster `MUL_MAT_ID` path.

## rMLX `285a51abbbd7b0ce9cb6e8888dcd4a3125fb1319` — benchmark provenance hardening

Fresh rMLX work adds content-addressed published sample sets, fail-closed sample verification, server lifecycle/log attribution, per-request decode-window cross-checks and repeated-pass stability refusal logic.

No new model rate is produced by this commit. It is useful harness/provenance mining only and reinforces the standing rule that a published performance row needs sample, sampling, server-build and measurement-window identity.

---

# FRESH UPDATE / previous evidence downgraded

## llama.cpp #28484 — reporter can no longer reproduce the distributed MTP regression

The 06:58 note recorded a reported Qwen3.8-27B distributed RPC MTP drop from roughly 27–32 to 21.3 tok/s while acceptance and no-spec decode stayed healthy.

Fresh reporter update at **2026-09-06 13:06:03 UTC** says the failure is **no longer reproducible**, without a driver or Windows update, although TG remains lower than the historical value.

### Consequence

Downgrade #28484 from a reproducible-regression claim to an unstable observation.

Retain the engineering lesson it motivated:

- same-topology no-spec control;
- speculative TG and E2E wall;
- acceptance/accepted length;
- graph reserve;
- per-round transport/sync and draft/target context sizing.

But do not use #28484 as evidence that a specific current llama.cpp change definitively causes a 25–30% distributed-MTP regression.

---

# FRESH UPDATE / first-repeat cache control strengthened

## vLLM #53504 — no-drop diagnostic restores hits on another hybrid

A fresh Qwen3.6-35B-A3B W4A16 hybrid reproduction on current main strengthens the MTP/EAGLE first-repeat issue:

- default MTP prefix cache: **0 hits out of 72,992 queried tokens** across the tested prompt/history policies;
- a 1,308-token shared prefix repeated four times: **0 / 0 / 0 / 0** hits;
- no-spec control: 1,056 tokens hit from the second request;
- `disable_eagle_block_drop=true` restores the no-spec total hit count (**22,176**) at unchanged acceptance in that run.

Use the no-drop flag as a **diagnostic A/B**, not as an assumed universal fix. The standing correctness requirement remains one canonical reusable boundary shared by recurrent and attention state, with verifier-only greedy equivalence preserved.

---

# Focused follow-up status

- **oMLX #3462:** no post-cutoff comments; the original real-agent cache-capture issue remains open, but the new async-store and pause/resume fixes materially strengthen its test matrix.
- **oMLX #3464:** no post-cutoff comments; explicit generated-token/TG provenance remains active.
- **llama.cpp #28425:** no post-cutoff update; ordinary no-spec recurrent rollback gate remains active.
- **llama.cpp #28433:** no post-cutoff update; per-slot MTP draft-context sizing remains active.
- **llama.cpp #28448:** no post-cutoff update; allocator identity remains a monitor item.
- **llama.cpp #25187:** no post-cutoff update; full-head MTP quantization before aggressive FR-Spec remains active.
- **MLX #4409:** no post-cutoff result; packed gated-delta work remains monitored.
- **Tiel Coder:** no fresh exact 5070 Ti result surfaced.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG receipt and no new exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max serving receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

Therefore the canonical targets remain:

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| Flash-Next — 2x M1 Max64 / TB4 | **40** | ~55–60% | **400** | ~55–60% |
| Qwen3.8-27B — M1 Max64 | **25** | ~55–60% | **110 native/exact** | ~60% |
| Qwen3.8-27B — RTX 5070 Ti16 | **120** | ~60–65% | **250** | ~55–60% |
| DS4-0731 — 2x M1 Max64 / TB4 | **15** | ~60–65% | **180** | ~60% |

These remain planning targets, not measurements.

---

# Updated consequences by lane

## Dual-M1 Flash-Next — revised current order

Keep PP2/layer ownership primary and TP2 as control.

1. Pin/certify the exact PP2/layer-owned baseline; TP2 control.
2. Ordinary no-spec recurrent rollback / growing-session correctness.
3. Cache-layout/handler round-trip + persistent model/tokenizer/runtime identity.
4. Real-agent cache capture with one canonical recurrent/attention reusable boundary; MTP on/off; first/second repeat.
5. **Immediate short-follow-up async-store race**: in-flight store, restorable overlap, settled control.
6. **Forced eviction/pause progress oracle**: true cache frontier, boundary snapshot and resumed logits/state vs uninterrupted chunked control.
7. QSA selected-set/order determinism plus position-resolved behavioral regression.
8. Realistic-depth long-context profiler: QSA/attention vs MoE vs GDN vs launch/host.
9. **QSA known-horizon reservation**: reserved/realized capacity, realloc count/bytes, physical footprint.
10. PLE residency/page-cache/direct-read policy.
11. **MTP reconcile with the same effective prefill chunk geometry** as ordinary prefill; enforce `actual_chunk <= remaining_tokens`.
12. MTP recurrent commit/replay correctness + per-slot draft-context sizing.
13. Scheduled-sequence occupancy at parallel 1/2/3/4 and stress above 4.
14. Concurrent pure-prefill state isolation.
15. Adversarial parallel-MTP slot isolation.
16. M1/M2 activation-FP16 approximate lane only after the exact path is frozen.
17. Compiled B2/B4 decode.
18. Combine passing mechanisms; then test long prefill while other sessions decode.

### New first-class metrics

- logical consumed-token frontier vs physical cache offsets;
- boundary-snapshot frontier before/after pause;
- original and reconcile prefill chunk sequences;
- QSA reserved/realized capacity and realloc bytes;
- actual QSA/attention execution route;
- cache class + handler round-trip identity;
- async cache-store status + restorable overlap on immediate follow-ups.

### New alternative-runtime lane

Use ds4 PR #991 as a Qwen3.8 Flash-Next **mechanism-mining and control runtime**. Reproduce useful mechanisms on exact M1 hardware before importing them into the target runtime. M3-Ultra absolute rates and percentages are not target evidence.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement.

Keep the practical shootout focused on:

- Qwen3.8-27B known fully-resident baseline;
- Tiel 35B-A3B Q4/Q5-class partial expert offload using host RAM rather than forcing 3-bit residency;
- actual CUDA backend/operator placement;
- MMID/MMF correctness after current race fixes;
- whole-round MTP economics and full-head quant before aggressive FR-Spec;
- peak VRAM/context headroom and real coding-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

The ANE commits above belong only to the separate approximate production lane and do not alter the native/exact 25 TG / 110 PP plan.

## Dual-M1 DS4-0731

No exact-rig target update. Continue to use DS4 as a topology/mechanism control lane; current Flash-support PR #991 is about Qwen3.8 on a different hardware/runtime configuration and does not establish DS4-0731 dual-M1 TG.

---

# Standing decisions strengthened this pass

- A cache hit is valid only if the cache's **semantic class/handler state** round-trips, not merely if token hashes match.
- Scheduler pause/resume is part of cache correctness: logical progress, cache progress and boundary snapshots must commit atomically enough to resume without duplicate tokens.
- Reconcile/rollback prefill must preserve the execution geometry that defines recurrent/QSA state; token-count equality alone is not proof.
- Long-context memory accounting must distinguish current resident/retained memory from bytes that were actually reclaimed and may need allocation again.
- When multiple attention/QSA routes exist, benchmark and memory provenance must record the **route actually executed**.
- Known final context horizon is a legitimate capacity-management input; over-allocation beyond model horizon is not harmless if it changes physical footprint or causes eviction.
- Immediate agent follow-ups belong in prefix-cache qualification because async storage races can make a cache look ineffective even when settled microbenchmarks pass.
- Cross-runtime performance gains are mechanism candidates until reproduced on the target hardware/topology.
- The #28484 distributed-MTP observation is downgraded; preserve controls, not the causal claim.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
