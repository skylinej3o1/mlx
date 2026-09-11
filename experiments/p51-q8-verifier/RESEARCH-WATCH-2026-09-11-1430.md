# External runtime watch — 2026-09-11 14:30 ET

Search window: **strictly after 2026-09-11 17:48:40 UTC through 2026-09-11 18:30:00 UTC**.

This is a deliberately narrow complete delta. The previous pass ended only ~42 minutes earlier, so this pass prioritizes source-timestamp correctness over rediscovery volume. Active scope remains the hardware we own / are actively building: dual-M1 Flash-Next, single-M1 27B, RTX5070Ti16 27B, dual-M1 DS4-0731, and portable Blazer/kernel mechanisms. No dedicated future-M5 lane is reopened.

Evidence discipline remains unchanged:

- source timestamp, not crawl/rediscovery time, determines freshness;
- exact target receipts, transfer/mechanism evidence, experimental A/Bs and planning targets stay separate;
- component/runtime support does not become a TG/PP multiplier without exact or exceptionally strong target-topology evidence;
- benchmark identity includes context, workload, cache/offload state, speculation state, physical residency and actually executed route.

## Executive result

**No canonical target moves.**

No fresh exact receipt appeared for:

- Qwen3.8-Flash-Next on 2x M1 Max 64 GB / TB4;
- Qwen3.8-27B on one M1 Max 64 GB;
- the RTX5070Ti16 fully-resident Q3_K_XL/native-MTP speed lane;
- DS4-0731 on 2x M1 Max 64 GB / TB4.

The useful new evidence is architectural: vLLM merged MTP speculative decoding under pipeline parallelism, and its failure/fix set materially sharpens the ownership and correctness gates for our planned Flash PP2 + MTP path.

---

# FRESH — vLLM #46994: MTP speculative decoding under pipeline parallelism

Merged:

`6fe67cbbf3e43da89bebf6ab0eeaca4ba6c75663` — **2026-09-11 17:55:21 UTC**

PR:

https://github.com/vllm-project/vllm/pull/46994

Classification: **FRESH / PP+MTP ARCHITECTURE TRANSFER / CORRECTNESS + ACCEPTANCE EVIDENCE / NOT APPLE SPEED EVIDENCE**.

The important result is not GPU throughput. It is the concrete list of things that broke when MTP was combined with pipeline parallelism and the conditions needed to make it correct.

## 1. Draft placement is stage-local, not implicitly replicated

The MTP drafter runs only on the **last PP stage**. The runtime still needs an explicit PP-capable interface and draft-token transport; merely having the target model pipelined does not make the speculative lifecycle pipelined.

Project promotion:

- our Flash PP2 design must name the physical owner of the draft head;
- target-stage ownership and draft-stage ownership are separate fields;
- cross-stage draft/accept/reject traffic must be explicit rather than inferred from target hidden-state flow.

## 2. Stage identity can silently skip required draft work

The Qwen draft head used an `is_first_rank` branch for its `fc` projection. Under PP, the drafter lived on the last stage, so that predicate was false and the projection was skipped. The corrected rule branches on whether `intermediate_tensors` actually exist rather than on global rank position.

Project promotion:

> **semantic data availability beats rank-number heuristics.**

For Flash PP2, do not gate MTP/QSA/recurrent work merely on `rank == 0/last`. Gate on the actual producer/consumer contract for the tensor/state involved.

## 3. Tied/shared embeddings still require a real owner on the draft stage

DeepSeek MTP could not simply borrow the target embedding because the target's corresponding layer may be a `PPMissingLayer` on the stage where the drafter executes. The draft checkpoint's own embedding had to be loaded.

Project promotion:

- stage-local speculative modules must have explicit ownership for embeddings, projections, recurrent state and auxiliary tables;
- a logically tied target weight is not physically available merely because it exists somewhere else in the pipeline.

## 4. Sparse-attention/indexer buffer aliasing can destroy acceptance without obvious target failure

Sparse MLA backends had snapshotted a `topk_indices_buffer` before the MTP proposer repointed the draft indexers to the target buffer. They then read a stale buffer that nothing updated, producing degenerate drafts.

A related DeepSeek-V3.2 / GLM path still served correct final output because bad drafts were rejected, but acceptance exposed the bug: **32.69% before the correct embedding load vs 93.51% after** in the cited GLM-5.2 cell.

Project promotion:

- acceptance collapse can be a **state-alias / ownership bug**, not merely a weak draft model;
- QSA/indexer/shared-selection buffers need runtime pointer/source provenance, not only shape/dtype checks;
- final-output correctness is insufficient to certify speculative correctness because rejection can mask draft corruption.

## 5. PP2 acceptance can match PP1 when ownership is correct

The PR reports greedy GSM8K acceptance on real models. Representative Qwen3.6-35B-A3B AWQ results at PP2 / TP1:

| K | mean acceptance length | token acceptance |
|---:|---:|---:|
| 1 | 1.9459 / ceiling 2 | 94.56% |
| 2 | 2.7995 / ceiling 3 | 89.86% |
| 3 | 3.5474 / ceiling 4 | 84.67% |

For a longer `max_tokens=2048` K=1 comparison, Qwen3.6 PP1 measured **1.9375** mean acceptance length; four PP2 runs measured **1.9380 / 1.9373 / 1.9354 / 1.9357**.

This is strong evidence that PP itself need not degrade MTP acceptance when the speculative state graph is wired correctly. It is **not** evidence that our M1/TB4 PP2 will be fast enough, nor that Qwen3.8-Flash-Next shares the same acceptance distribution.

## Flash PP2 consequence

Add these explicit bring-up/certification fields:

1. physical draft-head stage;
2. target hidden-state producer and draft consumer;
3. draft-token transport path;
4. stage-local embedding/projection ownership;
5. QSA/indexer buffer source and pointer freshness;
6. recurrent/spec checkpoint owner;
7. accepted-length clamp/rollback owner;
8. PP1-vs-PP2 acceptance parity under identical prompt/sampling cells;
9. final-output hash/parity separately from draft acceptance/parity;
10. fail-closed behavior when any speculative participant is unavailable on its executing stage.

This strengthens the existing rule that PP+MTP is a separate qualification problem from plain PP target execution.

---

# FRESH STATUS — oMLX #3359 closed as superseded by upstream MoE streaming

PR:

https://github.com/jundot/omlx/pull/3359

Closed without merge at **2026-09-11 17:51:55 UTC** with the author explicitly stating that MoE streaming had been added upstream and that this branch was therefore being closed.

Classification: **FRESH STATUS / DUPLICATE-LANE CLOSURE / NO NEW TARGET EVIDENCE**.

The body contains older experimental Qwen3.8/DeepSeek streaming measurements, but those measurements predate this freshness window. They are not re-promoted as fresh simply because the PR closed now.

Project consequence:

- treat merged upstream expert offload (`jundot/omlx#2595`, already captured in the 13:48 pass) as the maintained implementation lane;
- do not double-count #3359's older Qwen/DeepSeek rates;
- retain the prior stance: routed-expert SSD streaming is primarily a **capacity escape hatch**, while resident experts + separately managed PLE/n-gram state remain the preferred speed architecture when memory permits.

The closure is useful because it removes an implementation fork from the watch set.

---

# FRESH BUT SCREENED — vLLM sparse-config fix

Commit:

`dc07f1638f73814b95776832b85df1cc92850416` — **2026-09-11 18:02:13 UTC**

Title: `[Bugfix][MLA] Read sparse model settings from text config (#56160)`.

Classification: **FRESH / CONFIG-PROVENANCE MECHANISM / SCREENED**.

This reinforces a standing rule rather than adding a new target mechanism: sparse-attention route/config identity must be read from the model's real text configuration and verified at execution. Requested flags or a nearby wrapper config are not enough.

No target or experiment priority changes from this commit alone.

---

# FRESH BUT SCREENED — llama.cpp nrc=2 quant-kernel test expansion

Commit:

`982937a3337f7e97ef08fd5603f4157575ece7e1` — **2026-09-11 18:19:37 UTC**

Title: `tests: extend test-quantize-fns to test nrc=2 (i8mm) kernels (#16234)`.

Classification: **FRESH / TEST INFRASTRUCTURE / NON-METAL / NO CURRENT PROJECT PROMOTION**.

The change improves multi-row dot-product test coverage, including independent row data and non-trivial strides, but is aimed at i8mm-capable paths rather than our Apple Metal execution lane. Keep only the generic testing lesson: multi-row kernels should be tested with genuinely distinct rows/strides so accidental row aliasing cannot pass.

---

# FRESH STATUS — llama.cpp #28744 closed as client-side issue

Issue:

https://github.com/ggml-org/llama.cpp/issues/28744

The report used Qwen3.8-27B with MTP and long-context server state on Windows/Vulkan and showed a generation stream stopping around ~78K resident tokens. At **2026-09-11 18:13:43 UTC** the reporter closed it after updating LangChain4j, stating that the problem appeared to be client-side.

Classification: **FRESH STATUS / SCREENED OUT AS RUNTIME REGRESSION EVIDENCE**.

Do not promote it into llama.cpp long-context instability evidence.

---

# Repository/source scan result

Within the strict window:

- `jundot/omlx` main: **no new commits** after the cutoff;
- `antirez/ds4`: **no new commits** after the cutoff;
- `ddalcu/mlx-serve`: **no new commits** after the cutoff;
- `ggml-org/llama.cpp`: one fresh nrc=2/i8mm test commit, screened above;
- `vllm-project/vllm`: PP+MTP merge and sparse-config fix captured above;
- fresh oMLX PR activity was screened; #3359's closure is retained only as duplicate-lane cleanup;
- fresh exact-hardware/model searches produced no source-dated receipt newer than the cutoff for the four canonical target lanes.

Older September 8-10 Reddit/web/HF receipts rediscovered in this pass remain older evidence and do not advance the freshness ledger.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence / status | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **planning objective; exact confidence not separately calibrated** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

No target moves and no P69 state changes.

---

# Updated project consequences

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control.

Add PP+MTP certification requirements from vLLM #46994:

- draft head has one explicit physical stage;
- no rank-number shortcut substitutes for actual tensor/state availability;
- tied/shared weights required by the drafter have a physical owner on the executing stage;
- QSA/indexer/spec buffers expose source/pointer freshness through each speculative cycle;
- compare PP1 vs PP2 acceptance before interpreting TG differences;
- final-output correctness and speculative correctness are separate gates;
- rejection masking must not allow corrupted drafts to pass certification unnoticed.

These are correctness gates first. They do not change the 40 @ ~128K target probability.

## Qwen3.8-27B / P69

No change. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen closed P69B8/B9/B10-C work.

## RTX5070Ti16

No fresh exact receipt. Keep the fully resident Q3_K_XL/native-MTP speed lane separate from host-backed capacity experiments.

## DS4-0731 dual M1

No fresh exact receipt. The PP+MTP transfer evidence is relevant only to distributed speculative ownership/correctness, not to DS4 rate targets.

---

# Freshness boundary

**Hard source-freshness boundary for the next complete external search: 2026-09-11 18:30:00 UTC.**

Future complete passes should search strictly after this timestamp. Repository-only edits and source-specific backfills do not independently advance it.
