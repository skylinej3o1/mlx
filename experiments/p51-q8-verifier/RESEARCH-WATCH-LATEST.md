# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-2205.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the current state.
   Retain `RESEARCH-WATCH-2026-09-03-1330.md` for broader machine-specific backfill,
   `RESEARCH-WATCH-2026-09-03-1530.md` for Blackwell verify / M1 serving-memory findings,
   `RESEARCH-WATCH-2026-09-03-1725.md` for DS4 AProjQ4 + request-adaptive DSpark policy, and
   `RESEARCH-WATCH-2026-09-03-1950.md` for Flash-Next sparse-QSA FA / long-context prefill.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans are intentionally narrow:

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, sparse long-context prefill, compiled low-occupancy decode, cache/state lifecycle, and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — distributed decode, PP-vs-TP, Metal shard mapping, sparse-attention/activation economics, speculation policy, multi-session bubble fill, and portable pre-M5 Metal work.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel work and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit fit, native MTP/DFlash, MTP-head quantization, Blackwell verify kernels, context headroom, and coding/tool throughput.

Other machines should be promoted only when they expose a mechanism likely to transfer into one of those four lanes.

## Current newest delta — 2026-09-03 22:05 ET

Freshness boundary: branch checkpoint `9d48c7096cb34123be4120d699c154a7f147494d` / 2026-09-03 23:53:02 UTC.

Material deltas:

- **FRESH / MATERIAL — oMLX #3334 full-model compiled decode:** M3 Ultra 256 GB, full 104 GB Flash-Next oQ4e + TurboQuant KV + depth-6 MTP. Alternating eager/compiled physical A/B reports per-token latency speedups **B1 +79.6%, B2 +21.9%, B4 +0.9%, B8 +9.6%**, with no observed correctness divergence. This strongly promotes compiled low-occupancy decode into the Hermes test plan, but the M3 percentages are not an M1/TB4 forecast.
- **FRESH / MECHANISM — llama.cpp #28351:** `llama-imatrix --process-mtp` now lets the collector run the separate NextN/MTP head against trunk tokens + hidden states so MTP-head weights can receive real activation-importance data. No speed/quality A/B yet; treat as a future low-bit MTP-head quantization seam for the 5070 Ti.
- **FRESH CAUTION — adaptive MTP #27210:** a two-MI50 sampled test shows rapid draft-width changes can create backend graph-record/cache churn and erase adaptive-depth gains on code/prose even while helping a file-rewrite workload. For Blackwell/Apple, prewarm widths, count graph captures/compiles, use hysteresis, and compare narrow adaptive ranges against fixed shallow depth.
- **NEW-TO-REPO BACKFILL / DIRECT 5070-TI CONTEXT-QUALITY LANE:** community GSQ-RCO + native-MTP physical testing on RTX 5070 Ti 16 GB shows roughly **74-78 tok/s sampled E2E** while keeping MTP-active context headroom of **160K-224K**, depending on quant. This does not replace the existing Q3_K_XL ~97.2 mixed / 111-115 tool-call tok/s speed ruler; it establishes a second quality/context operating point.
- **CURRENT OFFICIALIZATION — ISTA-DASLab GSQ-RCO:** official optional `-mtp` files are now published. IQ3_XXS is the first quality/context A/B candidate; IQ3_S is the quality-first control. The official repo supplies artifact/quality evidence, while the community card supplies the current exact-5070-Ti physical speed/context receipt.
- **FRESH SECONDARY — DS4 #967:** fixes a CUDA build break introduced by shared Metal/TP changes; GB10 build/help gate passes, no inference speed claim yet.
- **UPDATE / NO NEW NUMBER — DS4 #861:** rebased/consolidated; known two-node 8060S/TB5 PP/TP/batching measurements remain unchanged.
- **NO CHANGE — exact dual-M1 Flash-Next:** still no sustained physical 2x M1 Max/TB4 Flash TG or published 115K result.
- **NO CHANGE — exact dual-M1 DS4-0731:** #922 still has ~152 tok/s @34K distributed prefill and successful generation without sustained TG denominator; #957 still lacks a physical Apple post-coalescing `--layers` gate.
- **NO CHANGE — exact P69 / current direct 5070-Ti speed ruler:** P69B12 remains frozen and P69B13 remains next using existing profiling only. `aipruner` Q3 + native-MTP remains the direct 5070-Ti speed ruler. `mlx-dspark` still has no push after Sep 1 10:54 UTC; Layr has no post-cutoff submission.

## Current consequences

### Dual-M1 Flash-Next

**Two architecture gates are now mandatory before accepting a mature result:**

1. #28349-equivalent selected-KV sparse FA for long-context QSA/prefill.
2. #3334-equivalent compiled B1/B2 decode with cache positions, recurrent GDN state and QSA/indexer state represented as explicit tensor state.

Keep PP2/layer ownership primary and TP2 as control. Measure B1/B2 separately from B4, because dispatch savings are strongly occupancy-sensitive. The operational test where a long-prefill agent joins while other agents decode remains especially important.

### RTX 5070 Ti 27B

Split the campaign into two resident lanes:

- **Speed lane:** existing Q3_K_XL + native MTP; retain the ~97.2 tok/s mixed / ~111-115 tool-call ruler and #26705 small-N verify work.
- **Context/quality lane:** official GSQ-RCO **IQ3_XXS-mtp** first, then IQ2_S-mtp for context-per-quality and IQ3_S-mtp as quality-first control. Benchmark real sampled agent traffic, acceptance, VRAM high-water and no-offload fit at 8K/24K/64K/128K plus the highest surviving context.

When #28351 matures, add MTP-head imatrix quantization as a separate A/B axis; judge it by acceptance + equivalence + VRAM, not file size alone.

### Adaptive speculation

Keep workload/acceptance-adaptive depth, but now explicitly price width-transition overhead. Prewarm candidate widths, count graph/command captures, use sticky/hysteretic transitions, and compare narrow adaptive bands against fixed depth 3. DS4 #965's lifetime bypass remains complementary: bypass controls whether speculation stays active; width hysteresis controls how much runtime churn adaptation creates.

### Dual-M1 DS4

No forecast change. Keep PP2/layer ownership primary, TP2 control, current-head AProjQ4 with AProjQ8 control, coalesced Metal mapping as a prerequisite, and request-adaptive speculation by workload. No new exact M1 physical rate appeared.

### Single M1 Max 64 GB 27B

No new physical rate. Preserve bounded MTP/session state construction, no full-history replay solely to manufacture reusable cache state, and process/system/transient memory telemetry in addition to MLX-active memory.

## Forecast consequence

Do **not** change the canonical dual-M1 Flash-Next B1, ~128K B1, or B2-B4 confidence bands. The new compiled-decode evidence is M3 Ultra, and the missing physical ruler remains sustained Flash-Next TG on the real 2x M1 Max 64 GB / TB4 pair.

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**. Sparse QSA and compiled low-occupancy decode now have strong physical Apple evidence as separate building blocks, but neither is a measured dual-M1 result.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative; **P69B13 remains next using existing profiling data only**.
