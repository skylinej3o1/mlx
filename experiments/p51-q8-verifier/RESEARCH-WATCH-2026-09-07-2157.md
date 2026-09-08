# External runtime research watch — 2026-09-07 21:57 ET

Starting freshness boundary: `e6357f532ed226b1073a78799b84760d0f25b751` / **2026-09-07 23:21:27 UTC**.

Classification: **material agent-serving / scheduler / distributed-sampler update; no performance target movement.**

`RESEARCH-TARGETS.md` is intentionally unchanged. No fresh sustained exact-target receipt surfaced for dual-M1 Flash-Next, dual-M1 DS4-0731, single-M1-Max Qwen3.8-27B, RTX 5070 Ti Qwen3.8-27B or RTX 5070 Ti Tiel Coder.

This pass is valuable primarily because it sharpens the production qualification order: grammar-constrained speculative state, prefill/decode fairness and sampler-backend ownership are now explicit serving surfaces, while a fresh Apple prefill-kernel update reinforces that a large isolated component speedup is not automatically an end-to-end PP win.

---

# FRESH / material

## oMLX #3504 — grammar-constrained MTP can preserve exact grammar state and remain profitable

Fresh post-boundary measurement comment: **2026-09-08 00:16:25 UTC**.

The implementation itself predates this cutoff, so the code is not classified as newly discovered. The **611-request Apple serving A/B is fresh evidence**.

Setup reported by the contributor:

- oMLX 0.6.4 release wheel with the #3504 branch files overlaid;
- `qwen3.8-27b-oQ6e-mtp`;
- C=1;
- 611 structured-output requests: 385 classification + 226 extraction;
- `response_format=json_schema` on every call;
- temperature 0.1, thinking disabled;
- identical request order/seed between MTP-off and MTP-on arms.

### Correctness / engagement

- grammar compiled on **611/611** requests in both arms;
- MTP-on logged an MTP completion with nonzero drafted count on **611/611** requests;
- MTP-off logged no MTP rows;
- non-truncated corpus outputs:
  - MTP on: **0/601 off-grammar**, 1202/1202 deliberately mutated outputs rejected;
  - MTP off: **0/602 off-grammar**, 1204/1204 mutants rejected;
- streaming raw-byte sample:
  - MTP on: **0/50 off-grammar**, 100/100 mutants rejected;
  - MTP off: **0/48 off-grammar**, 96/96 mutants rejected;
- lax parse + JSON-schema validity was **601/611 = 98.36%** MTP on versus **602/611 = 98.53%** off;
- length truncations were 10 versus 9, respectively.

This is stronger than a coherent-text check because the author used a fresh grammar matcher plus mutation controls.

### Economics

Unconstrained control probes measured roughly **28.1 tok/s MTP off -> 43.8 tok/s MTP on**.

For the 611-request constrained corpus:

- paired wall-latency ratio, MTP-on / MTP-off: **1.283 [1.275, 1.293]**, n=608;
- classification: ~1.272x;
- extraction: ~1.323x;
- equal-output-length pairs: ~1.279x;
- streaming `generation_duration` sample: **25.6 tok/s -> 47.9 tok/s**, paired ratio ~1.870x on 50 pairs;
- median MTP acceptance: ~0.85;
- median emitted tokens/cycle: ~2.58;
- whole corpus wall: **4,931 s off -> 3,836 s on**.

The contributor notes an important workload effect: constrained fixed-key / bounded-value JSON can leave relatively few legal continuations, and the MTP head may therefore achieve **higher acceptance under grammar than on unconstrained prose**. This is a measured property of that workload, not a general assumption.

### Evidence class / promotion

This is a **measured Apple serving A/B**, but the host is clearly not the target single M1 Max 64 GB lane (the report describes a ~190+ GiB loaded-model pool). It is therefore **transfer evidence**, not a target TG receipt.

Promote these requirements into our production agent qualification:

1. Grammar/parser state is speculative state. It must support snapshot / restore / rewind at every verify-row frontier and a correct hand-back to the ordinary deferred path.
2. A structured-output MTP cell must prove the grammar was actually armed and MTP actually engaged; configuration alone does not count.
3. Validate non-truncated outputs with an independent grammar oracle and mutation-positive controls.
4. Record parse/truncation rates, per-position acceptance, tokens/cycle and wall/decode against MTP-off.
5. Do **not** assume constrained decoding hurts speculation; measure acceptance under the actual tool/schema workload.
6. Row-wise batched constrained MTP remains a separate qualification surface; #3504 explicitly leaves that path out.

For Flash-Next, add this after the ordinary sampler-law / singleton-MTP semantic baseline and before claiming production agent correctness under structured tools.

---

## Ollama #18302 — distributed speculative sampling must respect where complete logits exist

Fresh PR created **2026-09-08 01:56:36 UTC**.

Ollama was unconditionally adding `--spec-draft-backend-sampling` for embedded-MTP drafts. Under llama.cpp `SPLIT_MODE_TENSOR`, the output logits are sharded across devices and the backend sampler cannot reduce them across ranks, so llama.cpp rejects the backend sampler and falls back to CPU sampling.

The failure is not merely a log cosmetic: the unsuccessful sampler-offload attempt and scheduler reserve churn were measurable.

Physical A/B reported on **2x TITAN RTX over NVLink**, Qwen3.8-27B embedded MTP n=5, ~96.8K active context:

- before: **27.67 tok/s** end-to-end decode;
- after skipping the unsupported backend-sampling flag in tensor split: **35.14 tok/s**;
- reported delta: **+27%**;
- LongBench-v2 answer remained correct in both arms.

The fix leaves single-GPU and layer/row split behavior unchanged.

### Evidence class / promotion

This is **cross-hardware distributed mechanism evidence**, not Apple PP2 evidence and not numerically transferable.

Promotion for our dual-M1 design:

- PP2 remains primary; sampling should have an explicit owner, normally the stage/rank that possesses complete output logits;
- TP2 control runs must record whether logits are sharded, whether the chosen sampler can reduce across ranks, and whether any fallback occurred;
- sampler backend / actual realized sampler path becomes benchmark provenance for distributed MTP;
- a silent CPU/host fallback is a failed optimized cell even if output correctness survives;
- do not attribute a distributed-MTP slowdown to target compute until sampler placement/fallback is ruled out.

This strengthens the architectural preference for PP2/layer ownership over chatty TP2 for the primary dual-M1 appliance, while keeping TP2 as a useful control.

---

# UPDATE / material status changes

## oMLX #3487 — merged prefill/decode fairness enforcement

Merged **2026-09-08 00:55:01 UTC** as merge commit `0ca0953d7dff1e44237994a1e429d5a5f663158e`.

The underlying work predates this cutoff; the merge is an **UPDATE**, not a fresh mechanism discovery.

It closes two concrete enforcement gaps in the existing fairness policy:

1. `_advance_chunked_prefills()` could run several in-flight prefill chunks back-to-back after the first chunk had already accrued decode debt, because the gate was checked only outside the loop.
2. non-embedding external prefills did not accrue corresponding decode debt, allowing short requests to bypass the intended pacing.

The merged path now:

- rechecks the fairness gate before each in-flight prefill chunk;
- rotates the unprocessed suffix ahead of requests that already advanced, preserving progress fairness;
- charges measured non-embedding external-prefill work to decode debt;
- uses the same gate predicate for new-request admission.

Red/green evidence: the parent plus the new regression tests had **6 failures / 2 passes**; the patched related suite reported **112 passes**.

The PR explicitly makes **no throughput claim**. This is scheduler-correctness / latency-fairness evidence.

### Promotion

For the dual-M1 appliance, aggregate B2/B3/B4 is not sufficient. Under long prefill + active decode, qualification must also prove:

- prefill cannot monopolize several successive chunks after decode debt closes the gate;
- deferred request ordering makes progress rather than repeatedly favoring the same prefill;
- short/external prefill is included in the same accounting;
- per-request decode latency and aggregate throughput are both reported;
- cooperative yielding is labeled as such — an executing Metal operation is still not preemptible.

Add this to the long-prefill-while-other-sessions-decode serving gate.

---

## oMLX #3492 — fresh shape generalization, but isolated HC-prefill RMSNorm win still does not appear end-to-end

Fresh commit `9686ddfc09dfb2e2d45f266f361e6815fb02328a` at **2026-09-08 01:28:46 UTC** generalizes the prefill RMSNorm kernel from the shipped Qwen4-Exp hyper-connection shape to any positive `hc_count` with `hidden_size % 32 == 0`, adding five non-production-shape correctness checks.

The more important planning result is the current controlled performance state of the PR:

- isolated fused RMSNorm is roughly **3.4-3.5x** faster around S=1K-4K in the current report;
- component profiling projects a few-percent whole-forward improvement;
- but restart-per-sample 100K end-to-end validation, 10 samples/arm, measured approximately **255.06 s canonical vs 254.56 s candidate** — only ~0.2%, not statistically meaningful;
- an additional hand-written tiled projection path was not retained because it regressed at S=1024 despite wins at larger S.

### Promotion consequence

This is **negative/neutral end-to-end evidence** against promoting a component microbenchmark by itself.

For our Flash prefill queue:

- keep the 19:19 block-history GDN/repeated-work candidate ahead of standalone HC-prefill norm fusion;
- a large isolated kernel ratio does not enter the PP forecast without cold-request / append-request wall A/B;
- if revisited, first prove the hyper-connection share remains material on the exact M1 quant/layout and look for a larger fusion boundary rather than assuming the isolated norm ratio survives pipeline overlap/noise.

---

## vllm-mlx #752 — Apple CI now exercises MTP drafter-loader regressions

Fresh commit `22b76982b79a82e023847fe1fdc26c4df68c7950` at **2026-09-08 01:49:07 UTC** adds the registered-MTP drafter loader regression tests to Apple CI.

The PR's existing composed validation says the Flash-Next serving path passed 64K continuous batching and 128K MTP qualification, but those qualification results predate this freshness boundary; they remain **KNOWN**, not fresh measurements.

The fresh consequence is narrower but useful: drafter metadata resolution, architecture normalization and target/drafter compatibility are now continuously checked on Apple CI rather than relying only on local tests.

Promotion:

- target/drafter architecture and model identity are part of the persistent runtime identity gate;
- unknown/malformed/incompatible drafter configurations should fail **before serving starts**;
- qualification records the source of target and drafter metadata rather than trusting a model name or CLI flag.

---

# KNOWN / screened non-promotions

- `antirez/ds4`: no PR or issue update after the starting cutoff relevant to the target lanes. The 19:19 M3-Ultra Flash prefill A/B remains the latest material ds4 result.
- `Pushkinist/rMLX`: no post-cutoff PR update surfaced.
- Rapid-MLX: no post-cutoff Qwen3.8 update surfaced.
- NInfer #188/#70: the useful DFlash2 and fuller-NVFP4 measurements were already present before this cutoff; later activity does not establish the exact RTX 5070 Ti lane. **KNOWN/BACKFILL only.**
- vLLM #54094: the 1.04M DFlash2 prefix-cache miss is important long-context evidence, but its latest substantive update predates this cutoff. Keep it in the existing cache-state chain; do not relabel it fresh.
- oMLX #3442's post-boundary edit is a user-side mitigation report involving SpecPrefill/repetition penalty and malformed tool envelopes; it is too confounded to promote as a runtime conclusion.
- no fresh exact M1-Max Qwen3.8-27B receipt surfaced;
- no fresh exact RTX 5070 Ti Qwen3.8-27B receipt surfaced.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash-Next:** no fresh sustained exact 2x M1 Max 64 GB / TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max 64 GB / TB4.
- **Single M1 Max64 Qwen3.8-27B:** no fresh exact target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt.

Therefore the canonical planning centers remain:

| Lane | TG | Cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64/TB4 | **40** | **400** |
| Qwen3.8-27B — M1 Max64 | **25** | **110** |
| Qwen3.8-27B — RTX5070Ti16 | **120** | **250** |
| DS4-0731 — 2x M1 Max64/TB4 | **15** | **180** |

These are **planning targets, not measurements**.

---

# Incremental dual-M1 Flash bring-up consequences

Keep **PP2/layer ownership primary and TP2 as control**. Preserve the 15:10 + 17:53 + 19:19 correctness and performance-ordering chain, with these additions:

- under the model/drafter identity gate, fail fast on malformed/incompatible MTP drafter metadata and record both identities/provenance;
- after ordinary sampler-law certification and the singleton replay semantic baseline, add a **grammar-constrained structured-output MTP state oracle**:
  - snapshot/restore/rewind grammar state across verify rows;
  - prove independent grammar validity with mutation controls;
  - prove actual MTP engagement;
  - compare parse/truncation, acceptance/tokens-per-cycle and wall/decode versus MTP-off;
- row-wise batched grammar+MTP remains unqualified until separately proven;
- distributed sampler provenance is mandatory: owner rank/stage, complete-vs-sharded logits, reduction capability, realized backend and any fallback;
- TP2 control fails optimized qualification if backend sampling silently falls back because sharded logits cannot be reduced;
- long-prefill-with-active-decode qualification now includes **per-chunk fairness/debt enforcement and per-request latency**, not aggregate throughput alone;
- retain the 19:19 prefill candidate order: block-history GDN/repeated-work elimination before broad repacking; standalone HC-prefill norm fusion remains lower priority until an exact production-style wall A/B demonstrates value.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot recurrent/spec state isolation, physical recurrent capacity, PP+MTP distributed ownership and concurrent-state semantics are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

---

# Other lanes

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. The fresh 2x-TITAN tensor-split sampler result is topology/mechanism evidence only; it does not alter the single-5070-Ti resident target. Preserve realized placement/backend, VRAM/context headroom, sampler path and real coding-agent wall-time provenance.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next only from existing profiling.** The oMLX grammar A/B is production-serving evidence and does not rewrite frozen verifier evidence.

## Dual-M1 DS4-0731

No target movement. No fresh exact dual-M1 0731 generated-token receipt surfaced.

---

# Standing decisions strengthened this pass

- Structured-output grammar state is part of speculative state and must be checkpointed/rewound with the emitted frontier.
- Constrained decoding can improve speculative acceptance on some workloads; measure it rather than assuming the direction.
- An MTP-enabled configuration is not evidence that MTP executed; actual draft/verify engagement is mandatory provenance.
- Distributed sampling must be placed where complete logits exist or have an explicit supported reduction path.
- Silent sampler fallback is a performance failure even if output correctness survives.
- Prefill/decode fairness is a serving correctness property, not merely a throughput tuning knob.
- Aggregate concurrency claims must include per-request progress/latency under concurrent long prefill.
- Isolated component microbench speedups do not become PP gains without production-style wall A/B.
- Controlled negative experiments remain first-class mining evidence.
- A benchmark cell is defined by what the engine actually executed, not merely what the CLI requested.
- QSA/indexer cache precision remains a separate state surface optimized only after deterministic semantic certification.
- Speculative cache/offload state carries explicit group ownership and lifecycle.
- The 15:10 oMLX #3494 attribution correction remains authoritative.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for replay correctness.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
