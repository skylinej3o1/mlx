# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-1950.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the current state.
   Retain `RESEARCH-WATCH-2026-09-03-1330.md` for broader machine-specific backfill,
   `RESEARCH-WATCH-2026-09-03-1530.md` for Blackwell verify / M1 serving-memory findings, and
   `RESEARCH-WATCH-2026-09-03-1725.md` for DS4 AProjQ4 + request-adaptive DSpark policy.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans are intentionally narrow:

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, sparse long-context prefill, cache/state lifecycle, and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — distributed decode, PP-vs-TP, Metal shard mapping, sparse-attention/activation economics, speculation policy, multi-session bubble fill, and portable pre-M5 Metal work.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel work and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit fit, native MTP/DFlash, Blackwell verify kernels, and coding/tool throughput.

Other machines should be promoted only when they expose a mechanism likely to transfer into one of those four lanes.

## Current newest delta — 2026-09-03 19:50 ET

Freshness boundary: branch checkpoint `c079ac2a69315526fde9d90e507ad65caa917ea0` / 2026-09-03 21:31:01 UTC.

Material deltas:

- **FRESH / MATERIAL — llama.cpp #28349:** Qwen3.8-Flash-Next now passes QSA indexer top-k as `n_kv_max`, allowing the merged Metal/CUDA sparse-FA backends to **gather only selected K/V rows instead of masking the full cache**. M5 Max / IQ4_XS / q8 KV physical results: `pp2048 @ 65K` **388.1 -> 702.2 tok/s**, `@131K` **340.0 -> 588.7**; server cold prefill across three ~33K prompts **664 -> 760 tok/s** with matching 36K greedy output. Long-context TG moved only slightly: 32K 34.5->35.1, 65K 28.3->28.7, 131K 20.6->20.7. Therefore this is a major **prefill/scaling** result, not a decode-band result.
- **RECOVERED OLDER EVIDENCE — merged llama.cpp #28098:** the Metal sparse-FA backend underlying #28349 was missing from the canonical/recent chain. On M2 Ultra DSv4 it transformed long-context prefill: 8K 323.58->373.49, 16K 248.67->362.21, 32K 170.35->347.85, 65K **107.08->323.54 (~3x)**. 65K decode improved 20.36->23.84. This is llama.cpp/M2-Ultra DSv4 mechanism evidence, not antirez/ds4 or M1 calibration.
- **FRESH SUPPORTING — adaptive MTP #27210:** another mixed-workload datapost reproduces the already-recorded conclusion that adaptive [3..12] beats globally deep fixed drafting on mixed code/prose. Treat as confirmation, not a new 5070-Ti ruler.
- **FRESH BUT GLM-ONLY — DS4 #964:** new quantized GLM-5.3-Flash ABBA runs show ~35-37% Metal decode gains with flat prefill; DeepSeek V4 remains explicitly near main, so this remains kernel-mining only.
- **NO CHANGE — exact dual-M1 Flash-Next:** #27993 still has no sustained 2x M1 Max/TB4 TG or published 115K follow-up.
- **NO CHANGE — exact dual-M1 DS4-0731:** #922 still has ~152 tok/s at 34K distributed prefill and successful long generation but no sustained TG denominator; #957 still lacks a physical post-coalescing Apple `--layers` throughput gate.
- **NO CHANGE — exact 5070-Ti / Apple exact frontier:** direct 5070-Ti Q3+native-MTP repo remains ~97.2 tok/s mixed at 8K / ~111-115 tok/s 24K tool calls and has not pushed since Aug 20. `mlx-dspark` has no code push after Sep 1 10:54 UTC. Layr has no post-cutoff PR update. #28196 has no new Blackwell verify trace after the prior pass.
- **BROADER SEARCH:** no independent new sustained 2x M1 Flash-Next or DS4-0731 decode receipt surfaced.

## Current consequences

### Dual-M1 Flash-Next

**Test-plan priority changes; decode forecast does not.** The #28349-equivalent sparse-QSA FA path is now a mandatory baseline before accepting long-context or multi-agent results. Verify exactness first, then measure cold prefill/cached continuation/B1/B2-B4. Each PP stage should gather its selected KV locally; TB4 should continue carrying activations/compact metadata rather than dense cache material.

The new result is especially operationally relevant when a long-prefill agent joins while other agents decode: faster sparse prefill may reduce how long the new request occupies a stage even if steady TG barely changes.

### Dual-M1 DS4

Keep the 17:25 plan: PP2/layer ownership primary, TP2 control, current-head AProjQ4 primary serving candidate with AProjQ8 control, coalesced Metal shard-map gate first, and request-adaptive speculation by workload. Mine #28098/#964 for sparse-attention/exact-dispatch ideas, but credit no speedup until antirez/ds4 physical validation exists.

### RTX 5070 Ti 27B

No new exact-rig result. Keep 3-bit residency first-order, native MTP as baseline, adaptive/shallow draft profiling by workload, and the #26705-equivalent Q4_K/Q5_K small-N verify A/B where the target tensor mix reaches it. Do not project other Blackwell/ROCm absolute rates to the 5070 Ti.

### Single M1 Max 64 GB 27B

No new physical rate. Preserve bounded MTP/session state construction, no full-history replay solely to manufacture reusable cache state, and process/system/transient memory telemetry in addition to MLX-active memory.

## Forecast consequence

Do **not** change the canonical dual-M1 Flash-Next B1, ~128K B1, or B2-B4 confidence bands. #28349 strongly validates the selected-KV sparse-attention prefill path but its own long-context TG is nearly unchanged.

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**. #28349 strengthens confidence in the architecture needed to reach that target on Apple, but the target remains unmeasured on the real 2x M1 Max 64 GB / TB4 pair.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
