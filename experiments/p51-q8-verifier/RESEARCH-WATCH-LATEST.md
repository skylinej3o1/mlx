# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-04-0625.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the current state.
   Retain `RESEARCH-WATCH-2026-09-03-1330.md` for broader machine-specific backfill,
   `RESEARCH-WATCH-2026-09-03-1530.md` for Blackwell verify / M1 serving-memory findings,
   `RESEARCH-WATCH-2026-09-03-1725.md` for DS4 AProjQ4 + request-adaptive DSpark policy,
   `RESEARCH-WATCH-2026-09-03-1950.md` for the original Flash sparse-QSA M5 measurements,
   `RESEARCH-WATCH-2026-09-03-2205.md` for GSQ-RCO / MTP-imatrix leads, and
   `RESEARCH-WATCH-2026-09-04-0115.md` for the compiled-decode reproduction correction, #28349 downgrade, and hidden ANE-bank accounting.

   **The 06:25 note is authoritative for current promotion level and diagnostic order.**

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans are intentionally narrow:

- **Flash-Next:** exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement and residency, sparse long-context prefill, compiled-decode experiments, cache/state lifecycle, and multi-agent pipeline filling.
- **DS4-0731:** same **2x M1 Max 64 GB / TB4** cluster — distributed decode, PP-vs-TP, Metal shard mapping, command-buffer/OS behavior, sparse-attention/activation economics, speculation policy, multi-session bubble fill, and portable pre-M5 Metal work.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel work, ANE prefill economics, cache/session granularity, and serving-memory/admission behavior.
- **Qwen3.8-27B / NVIDIA:** user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit fit, native MTP/DFlash, MTP-head quantization, Blackwell verify kernels/stability, context headroom, and coding/tool throughput.

Other machines should be promoted only when they expose a mechanism likely to transfer into one of those four lanes.

## Current newest delta — 2026-09-04 06:25 ET

Freshness boundary: branch checkpoint `7672162d1ae45a90a6a10fe6d1457bdcd7cf8057` / 2026-09-04 05:21:00 UTC.

Material deltas:

- **FRESH / MATERIAL — llama.cpp #28355 resolution:** Flash-Next's ~27 GiB `per_layer_token_embd` / n-gram table can now be lazy by default under `--lazy-mode auto`. `--no-mmap` alone does not force it resident. The reporter saw prefill fall roughly **2400 -> 1000 tok/s** after page-cache eviction from competing model/disk activity. Flash qualification must now record PLE residency/lazy mode and page-cache condition explicitly; compare stage-local resident/direct-read/quantized variants on the real 64 GB nodes rather than assuming one universal placement.
- **FRESH / MATERIAL DIAGNOSTIC — DS4 #845:** on 2x M3 Ultra 512 GB / direct TB, DeepSeek-V4-Pro-Q4K reportedly ran **10-13 tok/s** on earlier macOS 27 betas but **0.14-0.19 tok/s** on Beta 8. Local coalescing of ~156 Metal shard buffers to **4** did not recover speed (~0.16 tok/s); GPU-busy time was ~412 ms during ~6.1 s/token wall time with stable wired residency and negligible wire cost. Therefore #957-style mapping coalescing remains necessary hygiene but is **not sufficient** as a distributed-performance gate; OS build and command-buffer completion behavior must be measured too. This is not M1/0731 calibration.
- **FRESH / MATERIAL BLACKWELL CAUTION — llama.cpp #28377:** DGX Spark GB10 qwen4exp has a deterministic prompt/content-dependent `cublasGemmEx` prefill failure at `-ub 512`; `-ub 256` passed the reporter's 1..600-token sweep and failing HumanEval case. Add prompt-shape + ubatch fuzzing to the exact 5070-Ti campaign before promoting a build. Do not transfer the GB10 failure rate or performance to the 5070 Ti.
- **FRESH / MATERIAL SERVING POLICY — oMLX #3430:** hybrid ArraysCache's hard-coded 2048-token whole-block commit can prevent short repeated turns from reusing prefix state. M5 Pro testing shows smaller 256/128/64 blocks improve repeated short-turn latency at higher cold snapshot/boundary cost, and exact prior assistant serialization affects cached-prefix length. Add cache-block granularity + exact replay to Hermes serving A/B; no M5 number transfers to M1.
- **FRESH / SECONDARY OPERATIONAL — oMLX #3431:** `omlx stop` can report success while a server remains alive/listening with Metal memory retained on the reporter's machine. Shutdown/reload qualification must verify process exit, port release and memory release rather than trusting CLI status.
- **NO CHANGE — exact dual-M1 Flash-Next:** #27993 still has no sustained physical 2x M1 Max/TB4 TG or completed 115K-class follow-up.
- **NO CHANGE — exact dual-M1 DS4-0731:** #922 is unchanged: ~152 tok/s @34K distributed prefill, no sustained TG denominator. #957 itself still has no physical post-fix Apple throughput result.
- **NO CHANGE — direct RTX 5070-Ti ruler:** `aipruner/qwen3.8-3bit-test-in-16GB-GPU` remains unpushed since 2026-08-20. Q3_K_XL + native MTP remains the direct speed lane; GSQ-RCO remains the context/quality lane.
- **NO CHANGE — Apple exact frontier:** `mlx-dspark` still has no push after 2026-09-01 10:54 UTC. Layr's challenge repo still has no push after 2026-08-29. P69B12 remains frozen and **P69B13 remains next using existing profiling only**.
- **BROADER SEARCH:** no independent fresh sustained exact 2x M1 Max Flash-Next/DS4 decode receipt surfaced. Additional 5070-Ti-class vLLM/NVFP4 cards use different runtimes/quants/topologies and do not supersede the current exact single-card GGUF rulers.

## Current consequences

### Dual-M1 Flash-Next

Current bring-up order:

1. **Plain exact PP2/layer-owned baseline first**: correctness, sustained B1/B2/B4, cold prefill, long context and multi-agent behavior.
2. **PLE residency policy A/B**: lazy/page-cache vs stage-local resident/direct-read/quantized. Record page-cache state and deliberately add competing I/O/model eviction.
3. **Sparse-QSA A/B**: #28349-equivalent wiring remains an experimental patch, not an assumed upstream baseline.
4. **Compiled-decode A/B**: qualify #3334-equivalent explicit tensor-state compilation using real end-to-end B1/B2 serving metrics; do not credit the non-reproduced +79.6% B1 result.
5. **Short-turn cache granularity / exact replay A/B**: 64/128/256/2048-style state blocks or the closest runtime equivalents, measured on real agent/control traffic.
6. Combine only mechanisms that pass separately, then run the long-prefill-arriving-while-other-agents-decode stress test.

Keep PP2/layer ownership primary and TP2 as control. Every prefill result should record PLE residency policy; every stop/reload result should prove actual memory release.

### Dual-M1 DS4

Keep topology and artifact policy unchanged:

- PP2/layer ownership primary;
- TP2 control;
- current-head AProjQ4 primary serving candidate with AProjQ8 control;
- request/workload-adaptive speculation.

Update the mandatory distributed diagnostic gate:

1. verify sane/coalesced Metal shard mapping;
2. record macOS build and command-buffer completion/wait behavior;
3. record GPU-busy fraction and wired residency through decode;
4. run a same-host non-distributed/control path before blaming TB4;
5. only then evaluate PP bubbles/interconnect and multi-session filling.

The fresh M3-Ultra/Beta-8 report means mapping coalescing is necessary but not sufficient. It does **not** change the M1/0731 forecast.

### RTX 5070 Ti 27B

Keep two resident lanes:

- **Speed:** Q3_K_XL + native MTP, plus #26705 small-N verify work.
- **Context/quality:** official GSQ-RCO IQ3_XXS-mtp first, IQ2_S-mtp and IQ3_S-mtp controls.

Add a Blackwell stability matrix before performance promotion:

- ubatch 256 and 512;
- neutral prompt-length ladder plus code/tool-shaped prompts;
- MTP off/on;
- repeated cold/warm prefill with zero CUDA/cuBLAS faults;
- then normal 8K/24K agent throughput and acceptance measurement.

#28351 MTP-aware imatrix remains a separate future quantization axis.

### Single M1 Max 64 GB 27B

Retain the 01:15 ANE admission rule: hidden compiled ANE banks are first-order memory. Add short-turn state-block granularity and stop/reload resource-release checks to the serving qualification matrix.

Record process/system peak, MLX-active peak, ANE-bank estimate/measurement, context headroom and actual post-stop memory release.

## Forecast consequence

**Do not change the canonical dual-M1 Flash-Next B1, ~128K B1, or B2-B4 confidence bands. Do not change the DS4 or direct 5070-Ti rulers.**

The fresh evidence changes diagnostics and serving policy, not calibrated throughput:

- Flash prefill must control PLE residency/page-cache state;
- DS4 coalesced mapping is necessary but not sufficient;
- Blackwell qwen4exp needs prompt-shape/ubatch fuzzing;
- short-turn cache block size and exact replay are now explicit serving variables.

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, still unmeasured on the real 2x M1 Max 64 GB / TB4 pair.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative; **P69B13 remains next using existing profiling data only**.
