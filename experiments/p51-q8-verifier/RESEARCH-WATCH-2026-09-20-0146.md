# Project 51 external runtime watch — 2026-09-20 01:46 ET

**Hard freshness window:** strictly after **2026-09-20 01:18:00 UTC** through **2026-09-20 05:46:36 UTC**.

This pass continues from the repository's actual hard boundary. Evidence timestamp means the substantive measurement/source timestamp, not merge/rebase/bot/crawler time.

## Decision

**No numeric target or probability change.**

Flash-Next planning remains:

| Metric | Planning confidence |
|---|---:|
| >=35 TG @ ~128K | ~85% |
| >=40 TG @ ~128K | ~65% |
| >=45 TG | ~40% |
| >=50 TG | ~20% |
| 400 cold PP | ~70% |

The strongest new evidence is not a new exact dual-M1 speed receipt. It is a pair of exact Apple Flash-Next regression diagnoses showing that current MTP throughput can be materially suppressed by **runtime integration choices that accidentally force verify/rollback machinery onto non-verify forwards** and by a **fused-GDN verify fast path that stopped engaging**. This strengthens the implementation case for Project 51's explicit fast-path/verify instrumentation, but it does not justify transferring M5 Max short-context rates onto 2x M1 Max / TB4 / ~128K.

The decisive missing receipt remains: **custom ~4.6-4.9 effective hot-trunk BPW on 2x M1 Max 64 GB / TB4 at ~128K, first target-only and then MTP, with PP2 stage occupancy/bubbles, QSA/indexer behavior, acceptance/tokens-per-cycle, cache-state correctness and TB4 traffic recorded.**

## NEW — oMLX #3770: speculative cache transactions accidentally wrap every Flash-Next MTP forward

Source: https://github.com/jundot/omlx/issues/3770  
Created **2026-09-20 03:12:22 UTC**.

Environment:

- Apple **M5 Max 128 GB**
- oMLX dev4 `14194fe7`
- `Qwen3.8-Flash-Next-oQ4e-mtp`
- B1 / max concurrent requests 1
- same weights and server configuration across compared builds.

Measured regression:

| Build | Code TG | Prose TG | MTP tokens/cycle | Behavior |
|---|---:|---:|---:|---|
| pre-#3719 `7e6893e8` | **92.6** | **59.1** | 1.8-2.4 | 60-85% acceptance, sustains |
| dev4 `14194fe7` | **68.2** | **51.2** | 1.2-1.3 | parks after 21 cycles |
| dev4 + lazy transaction | **79.8** | **54.6** | 2.4-2.8 | 91-95% acceptance, sustains |

The report isolates the regression to Qwen4Exp/Flash-Next. Dense Qwen3.5 27B Q8 on the same VLM engine/build remained 51.6/34.2 TG, unchanged from the earlier build.

### Mechanism

After #3719, the vendored Flash-Next `LanguageModel.__call__` opens a `SpeculativeCacheTransaction` whenever hidden-state capture is active. The MTP backbone always requests hidden state, so the transaction fires on:

- ordinary one-token target decode;
- draft-head calls;
- real multi-token verify calls.

That has two costs even when rollback is impossible:

1. all 36 GDN layers record speculative recurrent intermediates;
2. cache leaves gain `_speculation`, which forces the model onto target-verify implementations instead of ordinary quantized/fused decode paths.

The depth controller then correctly observes that speculation is expensive and parks MTP after its 5 warmup + 16 losing-cycle exit streak.

The reported fix moves transaction creation into the MTP backbone and opens it **only when there is an actual multi-token verify/rollback domain**: `n_confirmed > 0` and input width exceeds confirmed width. Removing transactions entirely is not valid; the reporter measured a catastrophic prose collapse to ~16 TG because rollback state is genuinely required on verify.

Classification: **NEW exact Apple / exact Flash-family runtime regression evidence; not M1/TB4 or long-context target evidence.**

### Project 51 rule

**Speculative transaction scope is part of benchmark identity.** Only forwards that can mutate speculative state needing rollback may enable rollback history / verifier kernels. B1 target decode and draft proposal forwards must have an explicit assertion that they did not accidentally enter verify mode.

Qualification telemetry should separately count:

- standard target forwards;
- draft forwards;
- real verify forwards;
- speculative-transaction starts/aborts;
- GDN history records;
- target-verify kernel invocations;
- controller park/re-entry cycles.

No target change.

## NEW — oMLX #3771: fused GDN verify prework stopped engaging on Flash-Next

Source: https://github.com/jundot/omlx/issues/3771  
Created **2026-09-20 05:13:12 UTC**.

Environment:

- M5 Max 128 GB
- oMLX dev4 `14194fe7`
- Qwen3.8-Flash-Next-oQ4e-mtp
- 48 layers / 36 GDN layers
- measurements include the #3770 lazy-transaction fix so MTP remains active.

Measured:

| Build | Code TG | Prose TG | Fused verify prework |
|---|---:|---:|---|
| pre-#3719 `76d19fed` | **96.4** | **66.6** | yes |
| dev4 + #3770 fix | **77.4** | **57.7** | no |
| dev4 + #3770 fix + gate removed | **81.1** | **58.8** | yes |

The gate in `qwen35_gdn_prework.py` uses exact method identity to decide whether the fused verify prework can run. Qwen4Exp subclasses the verifier and overrides the normalization method, so the identity test is always false even though the report finds the numerical difference tiny on sampled verify inputs.

The report measured max q delta ~**1.2e-4** at magnitude ~0.03 and max k delta ~**2.0e-3** at magnitude ~0.35, and notes the pre-#3719 build had run the fused path for weeks around 91-92% MTP acceptance without observed correctness issues. This is still a report, not a merged qualification result; Project 51 should require its own output/logit/acceptance parity before widening an eligibility gate.

This is separate from already-recorded oMLX #3760, where exact **type** identity disabled the B1/T1 fused GDN decode path. #3771 shows the same class of fragility now on the **verify** side through exact **method** identity.

### Project 51 rule

Prefer **semantic/capability fast-path gates** over exact Python type/method identity. Instrument decode and verify fast-path engagement separately. Any wrapper/subclass/runtime upgrade must fail qualification if expected fused kernels silently stop engaging.

No target change. The report still shows a substantial residual gap after restoring this one path, so do not treat 81.1 TG as the fully recovered dev4 ceiling.

## NEW — llama.cpp #29168: a target-side MoE fusion can destroy speculative exactness and acceptance

Source: https://github.com/ggml-org/llama.cpp/issues/29168  
Created **2026-09-20 03:18:20 UTC**.

Different model/backend, but a strong verifier-design warning:

- Gemma 4 26B-A4B MoE target + MTP sidecar
- CUDA / RTX 2070 SUPER
- partial offload
- exact bisection from build b10750 to b10751, one commit boundary.

Before the fused weighted-expert reduction:

- acceptance **0.823**, mean accepted length 2.65
- MTP **46.35 TG**
- no-draft **38.10 TG**
- drafted greedy output byte-identical to plain greedy.

After the target MoE reduction fusion:

- acceptance **0.481**, mean accepted length 1.95
- MTP **35.36-36.73 TG**
- no-draft **37.02-38.33 TG**
- drafted output no longer byte-identical to greedy.

The no-draft path remains essentially unchanged, so the issue is not a general decode speed regression. The suspected mechanism is floating-point accumulation-order drift between the normal target path and the target verify shape/path. Small logit changes can flip argmax and therefore both output and acceptance.

Classification: **NEW non-Apple / non-Flash exact speculative-correctness evidence.**

### Project 51 rule

A fusion is not speculative-safe merely because its standalone outputs are numerically reasonable. Every target-side fusion used by only one of {plain decode, verify} must pass:

- greedy token identity against the corresponding plain-target path;
- logit-delta envelope;
- MTP acceptance/tokens-per-cycle A/B;
- sampled-mode distribution/rejection-sampling checks where applicable.

An acceptance collapse can be a **target-path numerical mismatch**, not a weak draft model.

## NEW — Splash #16: concurrent cold requests can share a producer's prefix work before the cache is fully published

Source: https://github.com/incoai/splash/pull/16  
Created **2026-09-20 01:23:34 UTC**.

Splash adds a producer/waiter path for concurrent requests sharing a cold prefix. A waiting request can reuse the resident producer's planned recovery/checkpoint points instead of redundantly prefilling the same prefix. Waiters hold no active state cell or KV pages, respect priority/deadlines and fall back to ordinary admission if the producer or cached state disappears.

Validation reported:

- CPU engine tests + ASan/UBSan + TSan;
- 178 server tests;
- real-model HTTP smoke on Qwen3.8-27B and Qwen3.6-35B-A3B;
- four- and eight-request shared-prefix cases;
- cancellation/deadline/priority/image-identity/publication-failure/eviction coverage.

No throughput number is published, so this is architecture/serving evidence only.

### Project 51 implication

For Hermes/multi-agent workloads, **prefix reuse need not wait for a completed cache entry**. Consider a PP2 producer/waiter policy where one request owns the cold prefix prefill and siblings attach only at certified recurrent/QSA checkpoint boundaries. Measure saved **physical prefill rows**, TTFT distribution and cancellation fallback; do not count logical duplicate prefixes as executed PP.

## NEW — Splash #18: prefill admission should consume a work/row budget, not merely state-cell capacity

Source: https://github.com/incoai/splash/pull/18  
Created **2026-09-20 02:10:02 UTC**.

Splash found that long queued prefills could occupy every state cell before receiving GPU work, delaying later short requests. Admission now uses priority, remaining work and row-budget rules; cache probes remain read-only and scheduling delay is kept distinct from memory-retry deadlines.

Validation across Qwen3.8-27B and Qwen3.6-35B-A3B completed **68 requests without errors**, preserving shared-prefix reuse and four-lane decode. No end-to-end speed claim is published.

Project 51 scheduler implication: state-cell admission and PP work admission are different resources. Under mixed long-prefill + interactive decode load, budget **rows/work**, not only slots or resident bytes.

## NEW MERGE — vLLM #57434: cache ragged top-k metadata once per index source, not once per consumer layer

Source: https://github.com/vllm-project/vllm/pull/57434  
Merged **2026-09-20 03:46:34 UTC**.

DeepSeek-V4.1-Flash ROCm code rebuilt ragged top-k metadata on every compressed layer even though layers under one index source shared the same result. The model has 38 compressed-cache layers but only 8 index sources, creating a **4.8x metadata rebuild redundancy**.

MI355X TP4, fp8 KV, MTP decode:

- over 10 steps, pack/lens launches fall **380 -> 80**;
- pack kernel **173.1 -> 38.0 us/step**;
- lens kernel **158.4 -> 34.1 us/step**;
- net removed GPU work **250.2 us/step**, very close to predicted 255 us.

Importantly, end-to-end paired step time did **not** resolve a corresponding gain:

- C1: 45.57 +/-1.24 -> 46.15 +/-1.21 ms, noise/worse direction;
- C32: 44.65 +/-0.21 -> 44.41 +/-0.08 ms, -0.54%;
- spec-off loop was host-bound at 12.61 ms/step and showed essentially zero change.

Classification: **NEW non-Apple metadata-reuse evidence with explicit negative E2E result.**

### Project 51 rule

Cache query-independent/request-step metadata at the **producer/source lifetime**, not once per downstream layer. But never turn a kernel-time saving into a TG forecast without proving the runtime is not host/dispatch-bound.

This reinforces the existing QSA/indexer summary-reuse and host-dispatch rules; no new numeric target.

## NEW transfer evidence — vLLM #57753: low-concurrency recurrent kernels can require narrower tiles for occupancy

Source: https://github.com/vllm-project/vllm/pull/57753  
Created **2026-09-20 05:17:30 UTC**.

On MI355X / Kimi-K3 TP8, a KDA sigmoid-gating recurrent update launched too few workgroups at C1/C2. Making the V tile batch-aware changed kernel time:

- C1 decode: **3.185 -> 2.830 us (-11.1%)**
- C1 spec: **7.810 -> 6.529 us (-16.4%)**
- C2 decode: **3.308 -> 3.068 us (-7.3%)**
- C2 spec: **8.292 -> 7.332 us (-11.6%)**
- C4+: unchanged by construction.

This is different silicon/model/kernel and does not transfer numerically. It supports Project 51's existing focus on **B1/low-row occupancy as a separate kernel regime**: verify and decode shapes can want different tile geometry.

## NEW DS4 correctness note — #1073 current branch has prompt-length-dependent greedy divergence on CUDA

Source: https://github.com/antirez/ds4/pull/1073#issuecomment-5747377858  
Comment timestamp **2026-09-20 03:39:44 UTC**.

A DGX Spark tester built the current #1073 Metal-optimization branch at `a15028ee4` against main `8db1d1d1`. CUDA decode measured a tie inside that round's noise floor, but greedy output differed from main depending on prompt length.

Five prompt lengths (81 / 280 / 1,040 / 4,391 / 17,706) produced median top-20 logit deltas of:

- **1.560051**
- **0**
- **0**
- **0.058922**
- **0**

A short prompt flipped an actual token; main-vs-main remained exactly zero.

This is DeepSeek-V4.1 / DGX Spark rather than Flash-Next/M1, and the PR is still a draft. The value to Project 51 is methodological: a branch optimized for one backend can accidentally perturb another backend even when throughput there is unchanged. Frozen quality certification must run on every backend/topology we claim to preserve, not merely the optimized one.

## NEW DS4 streaming transfer — #1098 hits-first/pread overlap generalizes to GLM Flash on DGX Spark

Source: https://github.com/antirez/ds4/pull/1098  
Created **2026-09-20 03:22:38 UTC**.

Forced-streamed GLM 5.3 Flash Q2 on one DGX Spark, same 24 GB requested / 3,064 delivered expert cache in both arms:

| Context | hits-first OFF | ON | Delta |
|---:|---:|---:|---:|
| 2K | 4.50 | 5.28 | +17.1% |
| 4K | 4.32 | 5.20 | +20.1% |
| 6K | 3.79 | 4.74 | +25.2% |

The author decomposes the gain and finds the threaded pread pool does most of the work in this many-miss regime; pure ordering alone is near the round's floor. The branch reports byte-identical output across the tested switch arms.

This is not an Apple/Flash-Next result, but it reinforces a principle already present in Project 51: **when storage misses exist, overlap their acquisition with resident compute and measure the actual delivered cache population**, not just the configured cache budget.

No target change.

## Screened but not strict-new / no-change

- **DS4 main:** no default-branch commit in this interval. #1097/#1098 are new draft-side DGX Spark work; no exact dual-M1/TB4 receipt.
- **oMLX main:** no new default-branch commit. #3770/#3771 are issue-level diagnoses, not merged fixes yet.
- **mlx-serve:** no post-boundary default-branch Apple/Flash commit. PR #476 only adds raw BF16 ngram-table acceptance.
- **llama.cpp main:** interval commits are Mamba contiguity and F16 FWHT support; no new Qwen4Exp performance merge. #29166/#28699 had no new substantive post-01:18 comments.
- **Splash:** #16/#18 are relevant scheduler architecture work; no M1 backend appeared.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no activity.
- **MTPLX:** no new commit after 2026-09-17 in the strict window. Its current high M5 Flash-Next numbers are older evidence and are not reclassified as new.
- **npanj/llama.cpp:** no new strict-window commit.
- **Current Reddit/Hugging Face/community search:** surfaced strong but already-known/older Apple Flash-Next observations, including M5/M4/M2 and streamed-expert runs; nothing with a substantive timestamp inside 01:18-05:46 UTC qualified as a new exact Project 51 receipt.
- **vLLM #52244:** updated in the window but its substantive Qwen3.5 hybrid/MTP prefix-cache evidence predates this pass; no post-boundary comment supplied a new measurement, so it is not reclassified.
- **vLLM #57416:** merged in-window, prefill-only logit-row sizing; not relevant enough to alter Project 51 state.

## Durable qualification changes from this watch

1. **Scope speculative transactions narrowly:** rollback/history state exists only around forwards that can actually require rollback.
2. Count **target, draft and verify forwards separately**, including transaction starts and controller park/re-entry cycles.
3. Treat **decode and verify fast-path engagement as separate invariants**; semantic/capability gates beat exact type/method identity.
4. Every target fusion must prove **plain-target vs verify-target numerical compatibility**; acceptance collapse may be a target-path mismatch.
5. Shared cold prefixes may use a **producer/waiter** policy at certified state boundaries instead of duplicating PP.
6. Budget **prefill work/rows separately from state slots and bytes** under mixed workloads.
7. Reuse QSA/sparse-attention metadata at its **source lifetime**, but require E2E proof because kernel savings can disappear into host slack.
8. Low-row B1/verify shapes remain a distinct tile/occupancy regime.
9. Cross-backend quality parity is mandatory even when an optimization nominally targets only one backend.

## Target impact

**No change.**

The M5 Max Flash-Next reports make the recoverable runtime headroom more concrete, but they are short/medium-context, stronger-Apple, oQ4e measurements. They do not answer the hard Project 51 question: whether the intended **~4.6-4.9 hot-trunk BPW** can preserve oQ5e/BF16 behavior and sustain the target topology at **~128K on 2x M1 Max / TB4**.

**New hard boundary: 2026-09-20 05:46:36 UTC.**
