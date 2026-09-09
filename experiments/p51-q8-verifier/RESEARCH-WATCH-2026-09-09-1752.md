# External runtime research watch — 2026-09-09 17:52 ET

Starting canonical branch head: `1db04e8db706aaa281a82cf29805bd86af8ae574`.

Starting hard source-freshness boundary: **2026-09-09 18:04:46 UTC**.

---

# Verdict

**Material serving/correctness mechanism pass; no canonical TG/PP target movement.**

The strongest fresh evidence is a production M3 Ultra Flash-Next validation showing that merely leaving sibling engines resident can materially depress the same single-engine decode cell, plus a fresh vLLM pipeline-parallel speculative-draft lifetime bug that required the mapping tensor—not merely the derived send tensor—to remain owned by the broadcast stream. rMLX #553 independently consolidates recurrent rollback/refold/state-stack construction behind authoritative shared seams. A late vLLM shared-KV fix also strengthens the rule that a shared-state consumer must be proven read-only against the owner cache.

These are directly useful qualification/provenance lessons for dual-M1 PP2 + MTP, but none is an exact dual-M1 target-rate receipt.

---

## FRESH / oMLX #3520 — resident sibling engines are part of the benchmark cell

Fresh substantive comment `5606588580` at **2026-09-09 18:12:36 UTC** reports production validation on an **M3 Ultra 512GB** with `Qwen3.8-Flash-Next-oQ4e-mtp`, gathered row paths, fused HC, eager dispatch and adaptive MTP.

Full-machine-exclusive single-stream decode is reported as:

| context | observed rounds / best |
|---|---|
| 1K | 149.5–162.6 tok/s / 162.8 best |
| 16K | 74.1–86.0 / 86.1 best |
| 32K | 76.4–80.6 / 89.8 best |
| 64K | 73.9–89.5 / 89.5 best |

The important production observation is not the absolute M3-Ultra rate. With **two sibling engine instances idle but resident**, including keepwarm activity and their resident weights, the same 16K request falls to roughly **46–62 tok/s** instead of **74–86 tok/s**.

The same comment reports controlled warm-cache concurrency A/Bs where the project's batched-MTP path is **14–27% lower aggregate throughput than plain batching** across c2/c4 × 4K/16K.

**Promotion:** benchmark provenance must include the full resident engine/process set, keepwarm/preload activity and relevant allocator/wired-memory residency—not merely the selected request route. “Idle” sibling engines are not equivalent to absent engines. A concurrent-MTP path earns promotion only against an equal-residency plain-batching control.

This strengthens the existing safe-serving posture: **profitable singleton MTP + plain concurrent work** until multi-slot recurrent/speculative ownership and actual concurrent benefit are proven on the target topology.

**Classification:** transfer/serving evidence. M3 Ultra rates do not move the dual-M1 numeric target.

---

## FRESH / vLLM #55745 — PP speculative broadcast lifetime is a device-happens-before fact

Commit `e8064a96d02db70ebc1ca922bc9aba967a654483` at **2026-09-09 19:55:56 UTC** fixes pipeline-parallel speculative draft broadcast ownership.

The broadcast stream waits on the main stream and builds `send = draft_tokens[input_batch.idx_mapping].contiguous()`. The bug fix records **`input_batch.idx_mapping` itself** on the broadcast stream. Recording only the derived `send` tensor is insufficient because the indexing operation consumes the mapping tensor asynchronously after the Python/main-stream ownership point.

**Promotion for PP2 + MTP:** every control/index/mapping tensor participating in a cross-stream or cross-rank speculative path must remain live through the actual consumer stream completion. Host/Python scope, successful collective issue, or lifetime of the derived output does not prove the lifetime of all source operands.

Qualification should explicitly establish:

1. producer-stream completion for every source operand;
2. collective/broadcast-stream ownership for every asynchronously consumed operand;
3. consumer-stream happens-before before reuse/free;
4. stress where producer-side references/allocator reuse happen immediately after issue;
5. actual executed broadcast/consumer path provenance.

This is a particularly direct reinforcement of the standing rule: **host ownership stamps and successful broadcast admission do not prove device happens-before.**

**Classification:** cross-runtime distributed/speculative correctness mechanism; no numeric transfer.

---

## FRESH / rMLX #553 — one emit, one rollback/refold decision, one recurrent-state stack

Commit `85690ce5208822024e9fa4a71f51b34e7576e66a` at **2026-09-09 20:50:08 UTC** continues the speculative-loop consolidation:

- one round-token emitter;
- one `rollback_round` wrapper choosing refold versus disarm;
- one recurrent/linear-attention cache-stack builder;
- low-level recurrent refold and rollback kept private behind the shared seam;
- CPU-readable coverage for which rollback arm the round actually took;
- shared fed/verified round-input buffers rather than driver-local copies.

**Promotion:** keep one authoritative producer for recurrent state-stack construction and the rollback/refold/disarm transition. Individual draft drivers should own the semantic decision and telemetry, but not duplicate the low-level state mutation. Record the arm that actually executed, because two paths can preserve the same high-level token counters while mutating state differently.

This extends the #549/#550/#552 rule from round arithmetic / acceptance / record assembly to the recurrent rollback machinery itself.

**Classification:** portable correctness/provenance mechanism; no target-rate movement.

---

## FRESH / vLLM #55887 — shared-KV consumers must prove read-only ownership

Commit `dcd544486b7f4672b3c2e60ea289f19d86cf355c` at **2026-09-09 21:51:34 UTC** adds shared-KV prefill/extend support to ROCm AITER attention.

The relevant correctness contract is explicit in its tests: a shared layer reads K/V from the target layer's cache for prefill/extend, is checked against the reference path across prefill/extend/mixed batches and multiple cache layouts/dtypes, and the backing target KV cache is asserted **byte-identical before and after** the shared consumer runs.

**Promotion:** whenever QSA/shared-cache/indexer work reuses state owned by another layer/stage, provenance should identify owner versus reader and certify that a reader path cannot mutate the owner state. Exercise pure prefill, pure extend/decode-adjacent, mixed batches, quantized state and alternate physical layouts.

This is especially relevant to future Flash-Next state sharing, gathered-QSA and cross-model/state-transfer work: sharing storage is not ownership transfer.

**Classification:** cross-runtime cache-ownership mechanism; no numeric transfer.

---

## UPDATE / exact-rig search

A fresh Reddit discussion update exists on the previously known M1 Max 32GB Qwen3.8-27B baseline, but the underlying measured cell predates this cutoff and is a **32GB** machine, not the canonical M1 Max64 lane. No new post-cutoff exact M1 Max64 measurement was promoted.

No new timestamp-qualified exact target-lane receipt was found for:

- dual-M1 Max64/TB4 Flash-Next;
- one M1 Max64 Qwen3.8-27B;
- fully-resident Q3_K_XL/native-MTP RTX 5070 Ti16;
- dual-M1 Max64/TB4 DS4-0731.

---

## SCREENED / no target move

- oMLX #3539: no new substantive post-cutoff boundary-snapshot result.
- vLLM #56037: no new substantive post-cutoff mixed-concurrency/tail-ring result.
- antirez/ds4: no post-cutoff target-lane rate evidence.
- TurboQuant-MLX: no post-cutoff target-lane rate evidence.
- broad GitHub/web exact-rig searches did not produce a stronger timestamp-qualified canonical cell.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add/strengthen the qualification order with:

1. **resident-engine-set provenance** — all loaded sibling engines, keepwarm/preload activity, allocator/wired-memory state;
2. **equal-residency concurrency controls** — batched MTP must beat plain batching under the same resident/process state;
3. **PP source-operand lifetime** — mappings/indexes/control tensors remain live through consumer-stream completion;
4. **producer -> collective -> consumer happens-before** for speculative control and data tensors;
5. **one recurrent rollback/refold/state-stack producer**, with the actually executed rollback arm recorded;
6. **shared-state owner/reader identity** and byte-stability/read-only checks for reader paths;
7. retain all prior PLE placement, QSA route, packed-gather, boundary materialization, B2 admission-interleaving, long-soak and mixed-concurrency gates.

Safe serving remains **profitable singleton MTP + plain concurrent work** until per-slot recurrent/speculative state isolation, physical concurrent capacity, distributed PP+MTP ownership and equal-residency throughput benefit are all certified.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from the existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. The canonical speed lane remains fully-resident Q3_K_XL/native-MTP; host-backed long-context configurations remain separate capacity evidence.

## Dual-M1 DS4-0731

No target movement.

---

# Standing decisions strengthened this pass

- A benchmark cell includes **what else is resident on the machine**, not only the request/model selected for measurement.
- “Idle” is not equivalent to “absent” when sibling engines keep weights/state resident or run keepwarm activity.
- Batched speculative decoding needs an equal-residency plain-batching A/B before it is called a throughput win.
- A derived broadcast tensor's lifetime does not prove the lifetime of the asynchronous source/index tensors used to build it.
- Cross-rank correctness requires explicit device-stream happens-before and operand lifetime, not host scope or successful collective issue.
- Recurrent rollback/refold/state construction should have one authoritative mutation seam while driver-local semantic decisions remain attributable.
- Shared-cache readers must prove they cannot mutate owner state.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**
