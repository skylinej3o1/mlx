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
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1735.md` — newest complete delta: live-context-bounded DSA work, fused/graph-capturable prefill metadata, draft-config provenance, direct Flash-Next cluster PLE failure, 64-GB capacity/recovered REAP evidence.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1257.md` — GDN kernel-image route admission, device-authored adaptive metadata, no-forward KV-store lifecycle, coordinated long-prefill cancellation, recovered Flash-Next SP evidence.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-1103.md` — V4.1 CED bounded-replay Apple prefill, ds4 V4.1 Metal support, device-authoritative speculative metadata.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0313.md` — M1-targeted 27B DFlash2 FP16 candidate, proposal-head precision A/B, verifier-peak profiling, shared-expert padding/fusion.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-12-0111.md` — Blackwell NVFP4-KV physical execution identity.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-2022.md` — QSA bounded-workspace lifetime, DFlash per-layer normalization, YaRN consistency.
9. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1831.md` — exact expert-offload read overlap, logical-vs-physical padded shape, JIT specialization.
10. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1430.md` — PP+MTP ownership and pointer freshness.
11. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-11-1348.md` — dual-node load transient, TB control transport, Metal expert-tail geometry, rollback correctness.
12. `RESEARCH-MINING-2026-09-11-MOBA-QSA-BLOCK-INVERSION.md` and `RESEARCH-MINING-2026-09-11-MLX-SERVE-1M-FLASH.md` remain backfill/mechanism context only.
13. Older 2026-09-10 / 2026-09-09 notes remain retained for TP/PP, recurrent rollback, QSA/MTP, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-12 16:57:49 UTC` through the user-request cutoff.

**Hard source-freshness boundary for the next complete external search: `2026-09-12 21:35:07 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase or merge-only churn. A resurfaced older issue/benchmark stays older unless a clearly substantive post-boundary result can be identified.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved in the 17:35 ET pass. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C.**

---

# Newest directly relevant evidence — 2026-09-12 17:35 ET

## vLLM #56628 — useful work must scale with live context, not padded/max context

**FRESH NEW / STRONG LONG-CONTEXT MECHANISM TRANSFER.**

A DeepSeek-V4.1 ROCm DSA candidate-mask kernel was doing work across a `max_model_len`-wide workspace even though consumers read only each row's live span. With max length 1,048,576, the old path could launch 1,024 programs/row while only ~128 were useful.

The replacement keeps a capture-safe static launch grid but strides only to device-resident live ends. MI355X/gfx950/TP4 evidence includes:

- 131K, 96 rows: `0.1236 -> 0.0201 ms` (~6.16x);
- 32K/131K/524K at 96 rows: ~9.9x / ~6.3x / ~1.9x mask speedups;
- in-situ concurrency 16: `0.464 -> 0.077 ms/step` across the four mask calls;
- indexer chain `2.95 -> 2.58 ms/step`.

No reliable low-concurrency end-to-end TG delta was claimed because TP rank-arrival skew was larger than the kernel-sized win.

**Promote:** record `configured max span -> allocated workspace -> live consumer-visible span -> actual kernel iteration span`. Static graph capture does not justify work over padded/max-context regions.

## vLLM #56638 — fused prefill metadata/index preparation

**FRESH NEW / PREFILL MECHANISM TRANSFER.**

A V4.1 ROCm prefill path used Torch indexing after an inherited Triton kernel proved unsafe. The fallback contributed 55.2 ms of pure-copy kernels (~4.4% of the busiest stream) and used `repeat_interleave`, which synchronized to the host and prevented graph capture.

A safe one-program-per-row Triton replacement reports, on 4x MI355X TP4:

- ISL 8K TTFT: about **-11.0%**;
- ISL 32K TTFT: about **-7.8%**;
- 22 edge/correctness cases matched the reference;
- prefill only; decode unchanged.

**Promote:** prefill metadata/index preparation is first-class PP work. Profile host-syncing convenience ops and graph-capture eligibility; do not assume all TTFT cost lives in model GEMMs/attention.

## vLLM #56627 — target and drafter configs are separate execution identities

**FRESH NEW / SPECULATIVE CORRECTNESS TRANSFER.**

Draft attention metadata builders were receiving the target `vllm_config`. The fix consistently builds/uses `draft_vllm_config` for the draft model and its metadata builders.

**Promote:** target vs draft geometry/precision/backend/cache/block metadata are independent unless equivalence is proven. This applies directly to Lightning-MTP and DFlash2 experiments.

## oMLX #3619 — direct Flash-Next cluster PLE/n-gram prefill failure

**FRESH NEW / APPLE FLASH-NEXT BRING-UP CORRECTNESS.**

The flat `mlx-lm` qwen4_exp model calls `bisect_right` for PLE n-gram shard lookup without importing it. The vendored VLM path imports it correctly, but cluster/text-only ranks can load the flat model and bypass that compatibility path; n-gram prefill then raises `NameError`.

**Promote:** certify PLE/n-gram prefill per physical rank and actual model-loading surface. A passing VLM/single-process path does not prove a flat cluster rank executes equivalent code.

## oMLX #3614 — fresh single-64GB capacity bookkeeping

**FRESH / CAPACITY OBSERVATION ONLY. Not a speed receipt and not PP2 numeric evidence.**

Safetensors-header accounting in the issue reports current Flash-Next MTP checkpoints exceeding a single 64-GB Mac's non-PLE resident budget even with PLE on SSD. Keep this as a quant/capacity signal only; our two-M1 PP2 ownership plan changes the residency geometry.

## oMLX #3610 — recovered older REAP/MTP evidence

**RECOVERED OLDER EVIDENCE / NOT FRESH.**

Created before the previous boundary. Reported M2 Ultra 64 GB REAP-288 Flash-Next 4-bit with PLE on SSD: ~39 GB resident, ~36 tok/s @4K and ~22 tok/s @100K without MTP. oMLX cannot currently load the available full-width 512-expert MTP head onto the 288-expert pruned trunk because head geometry is inherited from the target trunk. A claimed ~1.5-2.2x MTP gain on that trunk came from another runtime and remains second-hand transfer.

Retain for geometry/capacity context only; no dual-M1 target movement.

---

# Fresh-screen negatives

- `jundot/omlx` main: no new active-lane performance commit; #3619 remains open at cutoff.
- `antirez/ds4`: no in-window commit/new exact 0731 receipt.
- `llama.cpp`: in-window schema/Jinja/general maintenance only; no new relevant Metal/Qwen3.8 throughput receipt.
- vLLM: no exact active M1/5070Ti topology receipt despite useful ROCm mechanism work.
- HF/Reddit/web searches resurfaced older Apple Qwen3.8/DFlash/Flash-Next evidence only; crawl time does not make it fresh.
- no new exact dual-M1 Flash-Next TG/PP receipt;
- no new exact M1 Max64 Qwen3.8-27B receipt;
- no canonical RTX5070Ti16 receipt;
- no exact new dual-M1 DS4-0731 receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Certification now explicitly includes:

1. actual fused/kernel route and device-capability admission;
2. live-context work span separately from allocated/max context;
3. graph launch geometry separately from device-bounded inner work;
4. prefill metadata/index preparation host-sync and graph-capture provenance;
5. target-vs-draft config/geometry/precision/backend separation;
6. rank-specific model-loading path and PLE/n-gram prefill correctness;
7. existing workspace, physical-shape, MTP-stage, pointer-freshness, precision-plane, verifier-peak, PLE and long-context gates.

The recovered REAP result reinforces long-context degradation and pruned-target/full-width-drafter compatibility as experiment dimensions, not target evidence.

## Qwen3.8-27B M1 / P69

No change. #56627 strengthens target/draft execution identity for DFlash2/Lightning-MTP comparisons. **P69B12 frozen/promoted; P69B13 next.**

## RTX5070Ti16

No change. #56628/#56638 are stronger-GPU mechanism evidence only. Continue recording live-work span, actual admitted kernel and physical cache/metadata routes.

## DS4-0731 dual M1

No change. Later V4.1 ROCm evidence is mechanism transfer only: live-span sparse work and fused device-only metadata preparation.

---

# Standing rules added/reinforced

- `max_model_len` / padded workspace width is not a valid proxy for useful per-step work.
- Static graph launch shape can coexist with device-resident live bounds controlling actual work.
- Prefill/indexer metadata kernels are first-class performance paths; host synchronization belongs in PP accounting.
- Draft metadata/cache/backend construction must derive from draft configuration, not silently inherit target configuration.
- Cluster correctness must be certified on each actual rank/model-loading surface.
- Requested/configured route remains distinct from compiled, admitted and executed route.
- Final-output correctness does not certify speculative correctness; acceptance/task quality stay separate.
- Component/kernel gains do not move TG/PP targets without exact target-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
