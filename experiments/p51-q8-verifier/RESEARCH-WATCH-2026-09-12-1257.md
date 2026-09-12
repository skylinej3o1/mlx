# External runtime research watch — 2026-09-12 12:57 ET

## Freshness window

This pass covers substantive source activity strictly after `2026-09-12 15:03:42 UTC` through the user-request cutoff `2026-09-12 16:57:49 UTC`.

Evidence timestamp means the timestamp of the substantive source/change, not a crawler timestamp, rebase-only commit, merge-only churn, or later rediscovery. Older evidence resurfacing inside the window is labeled **RECOVERED OLDER EVIDENCE** rather than made fresh.

## Active lanes

- Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4
- Qwen3.8-27B — one M1 Max 64 GB
- Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM
- DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4
- Blazer / custom ~5.x-BPW work where mechanisms transfer cleanly

No dedicated future M5/M5-Ultra lane is reopened.

---

# Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning target; no exact dual-M1 receipt |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moves in this pass. P69 remains isolated and unchanged. P69B12 stays frozen/promoted; P69B13 remains next only from the existing measured GDN/projection/downstream-tail profiling. Do not reopen B8/B9/B10-C.**

---

# Fresh findings

## vLLM #56618 — runtime GDN kernel-image availability / fallback

**FRESH NEW / EXECUTED-ROUTE PROVENANCE TRANSFER. Not an active-lane performance receipt.**

Created `2026-09-12 15:17:09 UTC`.

The failure mode is subtle and directly relevant to our runtime-provenance discipline: the fused GDN decode operator may be built and registered, yet the active CUDA device can still lack a compatible kernel image. The proposed fix calls `cudaFuncGetAttributes` on the actual device and falls back to the existing Triton GDN decode path when the fused image is unavailable.

This adds another necessary rung to route identity:

`requested -> configured -> op built/registered -> device-compatible kernel image present -> admitted/selected -> executed`

A log or config saying “fused GDN enabled” is therefore insufficient. For any fused/compiled path, record the actual device-capability admission result and fallback reason when available.

No throughput benchmark is supplied by the PR, so this is correctness/observability transfer only.

## vLLM #56620 — V4.1 adaptive verification and device query lengths on ROCm

**FRESH NEW / SPECULATIVE-METADATA CORRECTNESS TRANSFER. Patch not yet end-to-end validated.**

Created `2026-09-12 16:02:47 UTC`.

The published DeepSeek-V4.1-Flash DSpark configuration enables adaptive verification, which rewrites query boundaries on device. On the tested ROCm path the engine rejected this after model load because the sparse indexer did not declare support for device/CPU query-length mismatch.

The proposed fix recognizes that ROCm DSpark already uses the flattened decode path for the relevant draft width and can derive metadata from device `query_start_loc`, rather than routing through the SM100-specific metadata kernel.

Important classification: the author reproduced the failure on MI355X TP4, but had **not yet completed serve validation with the patch** at source time. Do not treat this as a passed speed/correctness receipt.

Durable lesson for Flash/MTP work:

- adaptive verification can make host-side request lengths stale;
- backend capability must be expressed in terms of the exact metadata path it executes;
- a backend may support device-authored boundaries through one flattened route but not another native/varlen route;
- metadata provenance must include backend-specific physical decode shape, not just logical request lengths.

This reinforces, rather than replaces, the prior #56562 device-authoritative-metadata rule.

## vLLM #56621 — asynchronous KV offload completion on no-forward steps

**FRESH NEW / CACHE-LIFECYCLE STATE-MACHINE TRANSFER. Not a speed receipt.**

Created `2026-09-12 16:10:11 UTC`.

Simple CPU KV offload could leave a pending asynchronous store unsubmitted when a scheduler step performed no model forward. The old lifecycle submitted stores from `wait_for_save()`, but no-forward steps skipped that path and could clear metadata first. The patch moves submission into `get_finished()`, which runs on both forward and no-forward completion paths, and adds a regression that verifies copied bytes and completion events.

Promote the lifecycle rule:

`request/control step -> async state/cache side effect issued -> completion observed -> metadata/state retired`

A “no model forward” step is **not** necessarily a “no runtime side effects” step. This matters for any future Apple cache/offload/prefix path where request completion, cancellation, or control-only scheduling can race with asynchronous state movement.

The PR remains draft and fresh GPU validation of the extracted fix was pending.

## oMLX #3613 — coordinated cancellation during sequential long-prompt prefill

**FRESH NEW / DISTRIBUTED-SERVING ROBUSTNESS TRANSFER. No throughput claim.**

Created `2026-09-12 16:38:45 UTC`.

Sequential serving routes could continue synchronously prefilling 100K–300K+ prompts after a client disconnected because cancellation was only observed once decode began. #3613 polls cancellation at prefill-step boundaries and, in distributed TP/ring modes, preserves rank agreement so all ranks leave the prefill chunk at the same boundary rather than hanging collectives.

Promote for long-agent qualification:

- cancellation/checkpoint boundaries are part of distributed prefill execution identity;
- every rank must agree on the stop boundary before leaving a collective phase;
- long-prompt serving should test cancellation during cold prefill, continued prefill, and decode separately;
- abandoned work after disconnect is an operational failure even if ordinary benchmark throughput is unchanged.

This is serving robustness, not evidence for the 400 tok/s Flash cold-PP target.

---

# Recovered older evidence / screened updates

## vLLM #56322 — Qwen3.8-Flash-Next sequence parallelism for GR/PLE

**RECOVERED OLDER EVIDENCE / NOT FRESH.**

The PR surfaced because it was updated after the boundary, but its sole implementation commit is dated `2026-09-10 16:59:51 UTC`. Do not relabel its measurements as fresh.

Still useful architecture context:

- token-shards GR/PLE and optionally MoE sequence work instead of replicating it across TP ranks;
- current implementation requires `PP=1`, so it is not directly compatible with our primary PP2 Flash architecture;
- reported BF16 TP2/ETP2 PLE-offload prefill improved roughly 7.7–7.8% at 8K/16K, while C32 decode was essentially flat/slightly worse;
- a DP2/TP2/EP4/ETP2 configuration showed larger decode gains, but that is a different multi-GPU server topology and low-acceptance workload.

Retain this as a control-path idea: if we benchmark TP2 Flash, GR/PLE sequence sharding deserves a matched A/B. It does **not** justify changing PP2 ownership or transferring GPU percentages to dual M1 Max.

## vLLM #56451 and older speculative PR churn

Post-boundary updates resurfaced adaptive-DSpark material, but the implementation commits predate this freshness window. Keep their device-ragged metadata, physical padding and adaptive-verification lessons in the retained evidence set; do not count their older MiniMax measurements as new.

---

# Negative / no-change screening

- `jundot/omlx` main had only a post-boundary API-key security change; no new Qwen3.8/Flash-Next/DFlash2 performance receipt.
- `ggml-org/llama.cpp` had no main commits in the strict window and no newly created PR in the window.
- `antirez/ds4` had no commits or newly created issue evidence in the strict window.
- vLLM main activity did not produce a new exact active-topology Qwen3.8 or DS4 receipt.
- Hugging Face / Reddit searches resurfaced useful but older DFlash2, M1 Flash-Next and GPU measurements. Crawl time is not evidence time; nothing source-dated inside this two-hour window is promoted.
- No exact new 2x M1 Max64/TB4 Flash-Next TG or PP receipt.
- No exact new M1 Max64 Qwen3.8-27B receipt.
- No exact new RTX5070Ti16 canonical-lane receipt.
- No exact new 2x M1 Max64/TB4 DS4-0731 receipt.

---

# Consequences for active lanes

## Dual-M1 Flash-Next

PP2/layer ownership remains primary; TP2 remains a control.

Add/retain the following certification items:

1. actual fused/kernel route must record device-capability admission, not only build/registration;
2. fallback reason and executed implementation must be observable;
3. device-authored speculative/request boundaries remain authoritative when adaptive verification mutates shape;
4. backend-specific flattened/native/varlen metadata route is part of execution identity;
5. asynchronous cache/state side effects must drain on forward and no-forward completion paths;
6. cancellation during cold/continued long prefill must terminate all participating ranks at an agreed chunk boundary;
7. existing QSA workspace, logical-vs-physical shape, MTP-stage ownership, per-layer draft normalization, proposal-vs-target precision, verifier-peak and positional-state rules remain in force.

Recovered #56322 sequence-parallel GR/PLE is a **TP control experiment candidate only** because its current implementation requires PP=1.

## Qwen3.8-27B M1 / P69

No change. External GDN fallback work reinforces route-verification discipline but does not alter the certified verifier campaign. DFlash2 FP16 remains an external challenger experiment, not a promoted replacement.

## RTX5070Ti16

No change. The GDN kernel-image PR reinforces that compiled/registered CUDA support is not proof of execution on a specific SM. Continue to record actual physical KV format, kernel/backend admission and executed route.

## DS4-0731 dual M1

No change. Fresh V4.1 ROCm metadata work and prior V4.1 Apple work are later-lineage mechanism transfer only. No 0731 dual-M1 target movement.

---

# Standing rules

- Separate exact-target measured receipt, transfer/mechanism evidence, experimental A/B and planning target.
- Context is part of target identity.
- Requested/configured route is not executed route.
- Built/registered fused ops are not proof that a compatible binary image executes on the current device.
- Requested/configured precision is not proof of physical precision.
- Logical request shape is not necessarily physical execution shape.
- Host metadata is not authoritative when device-side adaptive logic can mutate request boundaries.
- A no-forward scheduler step can still carry cache/state/transport side effects that must complete before metadata retirement.
- Distributed cancellation is a coordinated state transition, not a local client event.
- Final-output correctness alone does not certify speculative correctness; record acceptance and task quality independently.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**

## Next search boundary

**`2026-09-12 16:57:49 UTC`**
