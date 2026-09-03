# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-1725.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the current state.
   Retain `RESEARCH-WATCH-2026-09-03-1330.md` for its broader machine-specific backfill receipts and
   `RESEARCH-WATCH-2026-09-03-1530.md` for the Blackwell verify trace / M1 serving-memory findings,
   but use the narrower scope below for future recurring scans.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans are intentionally narrow:

- **Flash-Next:** primarily the exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, cache/state lifecycle, and multi-agent pipeline filling.
- **DS4-0731:** primarily the same **2x M1 Max 64 GB / TB4** cluster — distributed decode, PP-vs-TP, Metal shard mapping, activation transport, speculation policy, multi-session bubble fill, and portable pre-M5 Metal work.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel work and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** the user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit fit, native MTP/DFlash, verify economics, Blackwell kernels, and coding/tool throughput.

Other machines should be promoted only when they expose a mechanism likely to transfer into one of those four lanes.

## Current newest delta — 2026-09-03 17:25 ET

Freshness boundary: branch checkpoint `bd752888fea910b34df0059a9b369dcfd542766b` / 2026-09-03 19:32:49 UTC.

Material deltas:

- **FRESH — DS4 #965 / Metal DSpark policy:** DeepSeek-V4-Flash-0731 on M5 Max shows that low-predictability requests can repeatedly lose to speculation. A new deterministic lifetime rule disables DSpark for the rest of a request after two probe windows when lifetime average falls below **0.5 accepted drafts per scheduler cycle**. Italian prose improved **35.9 -> 38.5 tok/s** versus 40.6 plain after bypass, while profitable reasoning/code lanes stayed speculative. Treat the policy as transferable; do not transfer M5 rates to M1.
- **NEW-TO-REPO BACKFILL / FORMALIZATION — DS4 #952 AProjQ4:** imatrix-guided Q4_K for the 215 dense attention projections shrinks the same 0731 layout **80.76 -> 78.62 GiB (-2.14 GiB / -2.65%)**. Fully resident M5 Max Metal measurements show a **1.155x / +15.5% paired decode median**, +14.7% independent hot-start median, **32/32 frontiers** favoring Q4, and practical prefill parity. A separate third-party M5 validation reproduced 1.155x. The limited quality fixture shows no measured regression. This is directly relevant DS4/Metal model-layout evidence, but not an M1 speed forecast.
- **FRESH AProjQ4 caveat:** quoted results are from `6a20b131`; the branch has since merged newer main state. Current-head requalification is required. Use balanced/interleaved arm order because measurement-order drift can exceed sub-percent effects.
- **NEW-TO-REPO BACKFILL — llama.cpp #26705 / Blackwell verify candidate:** branchless Q4_K/Q5_K scale unpack attacks repeated work inside multi-column `mmvq`. A Qwen3.8-27B RTX PRO 4000 Blackwell end-to-end A/B measured **41.76 -> 43.11 tok/s (+3.22%)** with 78.73% acceptance unchanged and matching response hashes. Pure Q4_K kernel gains on RTX 4090 rise from ~+4.8% at ncols=5 to ~+16.5% at ncols=8. This directly complements the previous pass's 3-5-column verify bottleneck and is now a concrete exact-5070-Ti A/B candidate, but no 5070-Ti uplift is assumed.
- **FRESH SECONDARY — llama.cpp #28346:** proposes swapping speculative-draft and multimodal-projection weights so they are not simultaneously VRAM-resident. Potentially useful for 27B+MTP+vision on a 16-GB 5070 Ti, but currently only a capacity mechanism with no physical performance gate.
- **FRESH REFINEMENT — DS4 #964:** its GLM-only exact indexed-attention path now documents a problem-size crossover (-0.4% at 36 selected rows, +2.2% at 308, +10.7% at 1,500). DeepSeek V4 remains within 0.5% of main. Carry the gated-kernel methodology, not the speedup.
- **NO CHANGE — exact dual-M1 Flash-Next:** no sustained 2x M1 Max/TB4 decode receipt appeared. Flash probability bands remain unchanged.
- **NO CHANGE — exact dual-M1 DS4-0731:** #922 remains ~152 tok/s at 34K distributed prefill with successful long generation but no sustained generated-token TG denominator. No current 0731 dual-M1 decode ruler appeared.
- **NO CHANGE — exact frontier:** the direct 5070-Ti Q3+native-MTP result remains ~97.2 tok/s mixed at 8K / ~111-115 tok/s tool-call generation at 24K. `ARahim3/mlx-dspark` still has no code push after 2026-09-01 10:54 UTC, and Layr has no post-cutoff submission update.

## Current consequences

### Dual-M1 DS4

**Test-plan priority changes, forecast does not.** Keep PP2/layer ownership primary and TP2 as control, but promote current-head **AProjQ4** into the first physical PP2 matrix with **AProjQ8 as the same-checkpoint control**. Qualify coalesced Metal shard mapping first, use interleaved model-order A/B, measure per-stage memory + prefill + B1/B2-B4, and classify DSpark economics separately for prose, reasoning, and code/tool traffic. Add a sticky low-lifetime-acceptance bypass equivalent to #965 where supported.

AProjQ4 is topologically attractive because the changed attention projections are stage-local under layer ownership; it reduces local model bytes without adding a TB4 collective. The M5 +15.5% ratio is **not** an M1 forecast.

### Dual-M1 Flash-Next

No topology or confidence-band change. Keep **PP2/layer ownership primary, TP2 control**, stage-local recurrent/QSA state, TB4 carrying activations/compact metadata rather than recurrent snapshots, gathered selected-KV, separate PLE/offload qualification, workload-gated speculation, and 3-4 logical agents with normally 2-3 compute-active slots.

### RTX 5070 Ti 27B

The direct low-bit/native-MTP receipt remains primary. Add **#26705-equivalent branchless Q4_K/Q5_K scale unpack** to the exact-rig candidate list, but first inspect the target tensor mix to prove the 3-5-column verify path reaches those quant types. A/B at 8K and 24K, preserve response hashes/acceptance, and keep fit/residency telemetry first-order. If multimodal serving becomes important, #28346 deserves a separate swap-latency/high-water-VRAM test before production use.

### Single M1 Max 64 GB 27B

No new physical M1 rate. Preserve the prior operational rule: MTP/session terminal construction must be bounded in peak memory and must not replay complete histories merely to manufacture reusable state.

## Forecast consequence

Do **not** change the canonical dual-M1 Flash-Next B1, ~128K B1, or B2-B4 confidence bands. The missing physical ruler remains sustained Flash-Next TG on the real 2x M1 Max 64 GB / TB4 topology.

Do **not** synthesize DS4-0731 dual-M1 decode from M5 AProjQ4 or DSpark results. Instead, AProjQ4 + request-adaptive speculation are now high-priority physical experiments. The historical exact-M1/TB4 pre-0731 low-teens decode anchor and exact 0731 ~152 tok/s prefill receipt remain the physical topology rulers until current sustained 0731 generation is measured.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
