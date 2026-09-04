# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-04-0115.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the current state.
   Retain `RESEARCH-WATCH-2026-09-03-1330.md` for broader machine-specific backfill,
   `RESEARCH-WATCH-2026-09-03-1530.md` for Blackwell verify / M1 serving-memory findings,
   `RESEARCH-WATCH-2026-09-03-1725.md` for DS4 AProjQ4 + request-adaptive DSpark policy,
   `RESEARCH-WATCH-2026-09-03-1950.md` for the original Flash sparse-QSA M5 measurements, and
   `RESEARCH-WATCH-2026-09-03-2205.md` for GSQ-RCO / MTP-imatrix leads. **The 01:15 note supersedes the 22:05 note's promotion level for compiled B1 decode and #28349 sparse-FA wiring.**

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans are intentionally narrow:

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, sparse long-context prefill, compiled-decode experiments, cache/state lifecycle, and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — distributed decode, PP-vs-TP, Metal shard mapping, sparse-attention/activation economics, speculation policy, multi-session bubble fill, and portable pre-M5 Metal work.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel work, ANE prefill economics, and serving-memory/admission behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit fit, native MTP/DFlash, MTP-head quantization, Blackwell verify kernels, context headroom, and coding/tool throughput.

Other machines should be promoted only when they expose a mechanism likely to transfer into one of those four lanes.

## Current newest delta — 2026-09-04 01:15 ET

Freshness boundary: branch checkpoint `ba9277ad14259b8d0e745f8b07da6378010defda` / 2026-09-04 02:09:16 UTC.

Material deltas:

- **FRESH / MATERIAL CORRECTION — oMLX #3334:** the previously reported full-model **+79.6% B1 compiled-decode** result did **not reproduce**. On M3 Ultra 512 GB, quiet matched B1 rounds measured eager/lane **46.1/45.5 tok/s** with TQ off + MTP d5 and **46.7/43.7** with TurboQuant on + MTP d6. A +22% lane delta appeared only while a sibling serving instance was loaded. Keep the controlled host-dispatch `8.8->2.0 ms` and in-process B4 step `54.5->44.4 ms` evidence, but do **not** treat large B1/B2 serving gains as established.
- **FRESH / MATERIAL STATUS DOWNGRADE — llama.cpp #28349:** closed without merge on 2026-09-04 04:04 UTC because broader device validation is required before enabling the Qwen4Exp `n_kv_max` sparse-FA wiring. The M5 measurements remain mechanism evidence, while merged backend #28098 remains real infrastructure. For M1, sparse-QSA FA is now an **experimental A/B lane**, not an assumed upstream baseline.
- **FRESH / MATERIAL CAPACITY — oMLX #3425:** ANE Qwen3.8-27B prefill banks consume **7.06 GB resident memory** that RSS/`vmmap`/MLX accounting cannot see because the banks live in the neural-engine ledger. The isolated total is 64 MLP programs at ~90 MB plus 48 GDN programs at ~30 MB. This is now a first-order admission term for constrained Apple serving. Keep it separate from the existing exact-M1 field result of roughly **+9.54 to +9.64 GB total peak-memory increase** with ANE; 7.06 GB is only the isolated compiled-bank component.
- **FRESH SUPPORTING / GLM-ONLY — DS4 #964:** M3 Ultra GLM-5.3-Flash-Q4_K drift-balanced testing now extends through 262K: roughly +31.6% decode @2K tapering to +27.3% @262K, flat prefill, ~19-22% lower first-token latency. DeepSeek V4 itself remains explicitly within ~0.5% of main, so this remains mining evidence only.
- **NO CHANGE — exact dual-M1 Flash-Next:** #27993 still has no sustained 2x M1 Max/TB4 TG or published 115K result.
- **NO CHANGE — exact dual-M1 DS4-0731:** #922 remains ~152 tok/s @34K distributed prefill with no sustained TG denominator; #957 still lacks physical post-coalescing Apple `--layers` throughput.
- **NO CHANGE — direct 5070-Ti ruler:** Q3_K_XL + native MTP remains the speed lane (~97.2 tok/s mixed @8K / ~111-115 tool calls @24K). The GSQ-RCO lane remains the context/quality alternative. #28196 has no post-cutoff update.
- **NO CHANGE — MTP-head imatrix / exact verifier:** #28351 remains draft with no new measurement. P69B12 remains frozen and **P69B13 remains next using existing profiling only**.
- **BROADER SEARCH:** no new sustained exact 2x M1 Max Flash-Next or DS4-0731 decode receipt surfaced.

## Current consequences

### Dual-M1 Flash-Next

Corrected bring-up order:

1. **Establish the plain exact PP2/layer-owned baseline first**: correctness, sustained B1/B2/B4, cold prefill, long context, and multi-agent behavior.
2. **Sparse-QSA A/B second**: apply #28349-equivalent wiring as an experimental patch, not an assumed baseline. Require retrieval/output checks plus 4K/32K/64K/~128K performance.
3. **Compiled-decode A/B third**: qualify #3334-equivalent explicit tensor-state compilation using real end-to-end B1/B2 serving metrics. Dispatch/microstep wins alone are insufficient.
4. Only combine sparse-QSA + compiled decode after each passes in isolation.

Keep PP2/layer ownership primary and TP2 as control. The long-prefill-arriving-while-other-agents-decode test remains important.

### Single M1 Max 64 GB 27B

ANE prefill admission must include hidden resident-bank memory. For qualification record:

- process/system peak;
- MLX active peak;
- ANE compiled-bank estimate/measurement;
- full memory high-water after bank creation;
- remaining context headroom;
- model eviction/reload behavior;
- matched ANE-off control.

Do not use `phys_footprint` or MLX-active memory alone to decide whether an ANE-enabled 27B serving configuration fits. The exact-M1 ~+9.5 GB observed peak delta remains the safer machine-specific planning ruler; the fresh 7.06 GB result explains a large hidden component of it.

### RTX 5070 Ti 27B

Keep two resident lanes:

- **Speed:** Q3_K_XL + native MTP, plus #26705 small-N verify work.
- **Context/quality:** official GSQ-RCO IQ3_XXS-mtp first, IQ2_S-mtp and IQ3_S-mtp controls.

#28351 MTP-aware imatrix remains a separate future quantization axis. No fresh exact-rig result changes either ruler.

### Dual-M1 DS4

No forecast or topology change:

- PP2/layer ownership primary;
- TP2 control;
- current-head AProjQ4 primary serving candidate with AProjQ8 control;
- coalesced Metal shard mapping prerequisite;
- request/workload-adaptive speculation;
- GLM #964 ideas remain mining candidates until DeepSeek-V4 itself moves in physical tests.

## Forecast consequence

Do **not** change the canonical dual-M1 Flash-Next B1, ~128K B1, or B2-B4 confidence bands.

This pass actually **reduces evidentiary confidence in two implementation promotions** from the previous note: compiled B1 serving gains did not reproduce, and #28349 is not merged. It does not reduce the architectural case for sparse selected-KV attention or explicit tensor-state compilation; it simply restores them to controlled experimental lanes until M1-generation evidence exists.

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, still unmeasured on the real 2x M1 Max 64 GB / TB4 pair.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative; **P69B13 remains next using existing profiling data only**.
