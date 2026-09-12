# Latest external runtime watch

## Active scope

Research remains centered on:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**
- **Qwen3.8-27B — one M1 Max 64 GB**
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**
- **Blazer / custom ~5.x-BPW execution work** where evidence transfers cleanly

Do not maintain a dedicated future M5/M5-Ultra lane unless explicitly reopened.

---

## Read order for the next research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1257.md` — newest complete delta: GDN kernel-image route admission, device-authored adaptive metadata, no-forward KV-store lifecycle, coordinated long-prefill cancellation, recovered Flash-Next SP evidence.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1103.md` — V4.1 CED bounded-replay Apple prefill, ds4 V4.1 Metal support, device-authoritative speculative metadata.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0313.md` — M1-targeted 27B DFlash2 FP16 candidate, proposal-head precision A/B, verifier-peak profiling, shared-expert padding/fusion.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0111.md` — Blackwell NVFP4-KV physical execution identity.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-2022.md` — QSA bounded-workspace lifetime, DFlash per-layer normalization, YaRN consistency.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md` — exact expert-offload read overlap, logical-vs-physical padded shape, JIT specialization.
9. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md` — PP+MTP ownership and pointer freshness.
10. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md` — dual-node load transient, TB control transport, Metal expert-tail geometry, rollback correctness.
11. `RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` and `RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` remain backfill/mechanism context only.
12. Older 2026-09-10 / 2026-09-09 notes remain retained for TP/PP, recurrent rollback, QSA/MTP, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-12 15:03:42 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-12 16:57:49 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase or merge-only churn. A resurfaced older PR/benchmark stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved in the 12:57 ET pass. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

---

# Newest directly relevant evidence — 2026-09-12 12:57 ET

## vLLM #56618 — fused GDN kernel-image availability

**FRESH NEW / EXECUTED-ROUTE PROVENANCE TRANSFER.**

A fused GDN op can be built and registered while the current CUDA device still lacks a compatible kernel image. The PR checks the actual device image via `cudaFuncGetAttributes` and falls back to Triton GDN when unavailable.

Promote the route ladder:

`requested -> configured -> built/registered -> device-compatible image present -> admitted/selected -> executed`

Do not infer execution from a fused-op config, registration, or successful import. Record admission/fallback reason when possible. No performance benchmark was provided, so there is no target impact.

## vLLM #56620 — adaptive V4.1 metadata from device query lengths

**FRESH NEW / SPECULATIVE-METADATA CORRECTNESS TRANSFER. Patch not yet end-to-end validated.**

DeepSeek-V4.1 adaptive verification mutates query boundaries on device. The ROCm sparse-indexer path reproduced a startup rejection on MI355X TP4 because its capability declaration did not acknowledge the flattened device-query-length route it already uses. The patch changes that declaration while avoiding the SM100-specific metadata kernel.

Promote:

- device-authored boundaries remain authoritative when adaptive verification changes physical request shape;
- backend capability is route-specific: flattened/native/varlen paths may differ;
- backend-specific physical decode shape is part of metadata provenance.

At source time the failure was reproduced but post-patch serving remained unchecked. No speed or correctness receipt is promoted.

## vLLM #56621 — no-forward steps must drain async KV stores

**FRESH NEW / CACHE-LIFECYCLE STATE-MACHINE TRANSFER.**

Simple CPU KV offload could lose a pending async store because no-forward scheduler steps skipped `wait_for_save()` and could clear metadata before submission. The proposed fix issues the store from `get_finished()`, which executes on forward and no-forward completion paths, and adds a copied-byte/completion-event regression.

Promote lifecycle identity:

`control/request step -> async state/cache side effect issued -> completion observed -> metadata/state retired`

“No forward” does not mean “no runtime side effects.” This is relevant to future cache/offload/prefix work but does not move performance targets.

## oMLX #3613 — coordinated cancellation during sequential long prefill

**FRESH NEW / DISTRIBUTED-SERVING ROBUSTNESS TRANSFER.**

Sequential 100K–300K+ prompt prefill could keep running after client disconnect because cancellation was observed only at decode. #3613 polls at prefill-step boundaries; distributed TP/ring ranks preserve agreement so they leave at the same chunk boundary rather than stranding collectives.

Promote long-agent robustness tests for cancellation during cold prefill, continued prefill and decode separately. Cancellation is a coordinated distributed state transition. No throughput target impact.

## vLLM #56322 — Qwen3.8-Flash-Next GR/PLE sequence parallelism

**RECOVERED OLDER EVIDENCE / NOT FRESH.**

The PR resurfaced via a post-boundary update, but its sole implementation commit is from `2026-09-10 16:59:51 UTC`; its performance numbers are not relabeled as fresh.

Retain as architecture context only:

- token-sharded GR/PLE reduces replicated TP work;
- current implementation requires `PP=1`, so it is not directly compatible with our primary PP2 design;
- reported TP2/ETP2 BF16 PLE-offload prefill improved about 7.7–7.8% at 8K/16K, while C32 decode was roughly flat/slightly worse;
- larger gains appeared in a different DP/TP/EP server topology and low-acceptance workload.

Use it as a matched TP-control experiment candidate; do not transfer GPU percentages to dual M1 or change PP2 ownership.

---

# Fresh-screen negatives

- `jundot/omlx` main: only a post-boundary API-key security change; no new active-lane speed receipt.
- `ggml-org/llama.cpp`: no main commit or new PR inside the strict window.
- `antirez/ds4`: no commit/new issue evidence inside the strict window.
- vLLM: no exact active M1/5070Ti topology receipt.
- HF/Reddit searches resurfaced older DFlash2 and M1 Flash material only; crawl time does not make them fresh.
- no exact new dual-M1 Flash-Next TG/PP receipt;
- no exact new M1 Max64 Qwen3.8-27B receipt;
- no canonical RTX5070Ti16 receipt;
- no exact new dual-M1 DS4-0731 receipt.

---

# Important retained evidence

- **oMLX #3607 CED bounded replay:** full-context authoritative state + bounded decoder-tail forwarding can materially cut Apple prefill on V4.1; mechanism only for Flash-Next until reproduced.
- **antirez/ds4 V4.1 Metal:** later-lineage source transfer for Engram-on-disk ownership, streaming/residency and TP; not 0731 evidence.
- **vLLM #56577:** target-verifier and proposal-head precision are separate execution planes; account for private draft-weight memory/acceptance/quality.
- **vLLM #56572:** profile maximum reachable speculative-verifier shape and full-vocab temporaries for admission.
- **vLLM #56500/#56457:** bounded single allocations can still create allocator-retained workspace ladders; record live/reserved bytes and allocation count.
- **vLLM #56550:** requested KV dtype does not prove physical KV format/backend/layout/scale/block geometry/execution.
- **vLLM #56431:** draft semantic axes/per-layer normalization must remain correctly mapped; final output can hide bad speculation through rejection.
- **vLLM #56181:** logical request shape and physical padded graph shape must remain aligned across metadata/cache/draft paths.
- **vLLM #56153:** structural JIT specialization and dynamic runtime shape are different identities; benchmark first compile/new shape/warm/churn.
- **vLLM #46994:** physical drafter stage, hidden-state producer/consumer, explicit draft transport and stage-local dependencies are required under PP+MTP.
- **oMLX #3594:** positional scaling beyond native horizon must be consistently installed across main attention/QSA/MTP.
- **oMLX #3578:** load/transform/sharding/first-eval memory transients are distinct from steady-state residency.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Required evidence now explicitly includes:

1. actual fused/kernel route with device-capability admission, not merely build/registration;
2. observable fallback reason and executed implementation;
3. authoritative device/stage boundaries for adaptive speculative metadata;
4. flattened/native/varlen metadata route as part of physical execution identity;
5. async cache/state effects drained on forward and no-forward completion paths;
6. coordinated rank cancellation during long cold/continued prefill;
7. prior workspace, physical-shape, MTP-stage, draft-normalization, precision-plane, verifier-peak, PLE and long-context correctness gates.

#56322 GR/PLE sequence parallelism remains a **TP control experiment candidate only** because that implementation currently requires PP=1.

## Qwen3.8-27B M1 / P69

No change. External GDN work reinforces execution-route verification but does not modify the exact verifier campaign. FP16 DFlash2 remains an external challenger experiment.

## RTX5070Ti16

No change. Continue to record actual physical KV format, kernel/backend admission and executed route; built CUDA support alone is not proof that a chosen kernel image executes on the card.

## DS4-0731 dual M1

No change. V4.1 ROCm/Apple developments remain later-lineage transfer evidence only.

---

# Standing rules

- Separate exact-target receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Context is part of target identity.
- Requested/configured route is not executed route.
- Built/registered fused ops are not proof of a compatible executing device image.
- Requested/configured precision is not proof of physical precision.
- Logical request shape is not necessarily physical execution shape.
- Host metadata is not authoritative when device-side adaptive logic mutates request boundaries.
- A no-forward step can still carry cache/state/transport side effects that must complete before metadata retirement.
- Distributed cancellation is a coordinated state transition, not merely a local client event.
- Final-output correctness does not certify speculative correctness; record acceptance and task quality independently.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
