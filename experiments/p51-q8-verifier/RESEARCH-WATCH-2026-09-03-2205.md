# Runtime Research Watch — 2026-09-03 22:05 ET

Scope: focused recurring pass after `RESEARCH-WATCH-2026-09-03-1950.md`, using branch checkpoint `9d48c7096cb34123be4120d699c154a7f147494d` / 2026-09-03 23:53:02 UTC as the hard freshness boundary.

The recurring targets remain intentionally narrow:

1. **Qwen3.8-Flash-Next on the exact planned 2x M1 Max 64 GB / Thunderbolt 4 cluster** — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, sparse long-context prefill, cache/state lifecycle, compiled decode, and multi-agent pipeline filling.
2. **DeepSeek-V4-Flash-0731 / DS4 on the same 2x M1 Max 64 GB / TB4 cluster** — distributed decode, PP-vs-TP, Metal shard mapping, sparse-attention/activation economics, speculation policy, multi-session bubble fill, and portable pre-M5 Metal work.
3. **Qwen3.8-27B on one M1 Max 64 GB** — exact/native verifier/runtime/kernel work and serving-memory behavior.
4. **Qwen3.8-27B on the RTX 5070 Ti 16 GB + 64 GB host rig** — low-bit fit, native MTP/DFlash, MTP-head quantization, Blackwell verify kernels, context headroom, and coding/tool throughput.

Other machines are promoted only when they expose a mechanism likely to transfer into one of those lanes. External research does not modify the certified exact-Q8 verifier state: P69B12 remains frozen/promoted and **P69B13 remains next using existing local profiling only**.

## Executive delta

1. **FRESH / MATERIAL — oMLX #3334 gets a much stronger full-model compiled-decode physical gate.** A post-cutoff benchmark on an M3 Ultra 256 GB ran the full 104 GB `Jundot-Qwen3.8-Flash-Next-oQ4e-mtp` model with TurboQuant KV and depth-6 MTP, alternating the eager path against `OMLX_QWEN4_COMPILED_DECODE=1`. Reported per-token latency speedup for the compiled lane was:

   | Batch | Compiled lane vs eager |
   |---:|---:|
   | B1 | **+79.6%** |
   | B2 | **+21.9%** |
   | B4 | **+0.9%** |
   | B8 | **+9.6%** |

   No correctness divergence was observed at any tested batch size. This is materially stronger than the earlier #3334 evidence because it uses the full Flash-Next model rather than only the isolated in-process B4 gate. The benefit is strongly occupancy-sensitive: B1/B2 host dispatch can dominate, while higher concurrency pushes execution toward the memory-bandwidth wall. Do **not** transfer the M3-Ultra percentages numerically to M1 Max or interpret them as a measured dual-M1 HTTP throughput multiplier.

2. **FRESH / MECHANISM — llama.cpp #28351 adds imatrix collection for the native MTP / NextN head.** The ordinary imatrix collector sees the trunk graph but not the separate NextN head weights. The draft PR adds `--process-mtp`, creates an MTP context, feeds it the trunk tokens plus the previous trunk hidden state, and lets the same collector observe activation importance for the head. There is no throughput or quality A/B yet. This opens a useful future quantization seam for the 16-GB 5070-Ti lane: the MTP head can eventually be quantized with real activation importance rather than only conservative fixed-type choices. Treat it as a test-plan mechanism, not a speed claim.

3. **FRESH CAUTION — #27210 shows adaptive draft depth can lose through backend graph-cache churn.** A new two-MI50 Qwen3.8-27B test at temp 0.8 compared fixed depth 3 with adaptive ranges. Adaptive 2..6 improved a file rewrite from 75.7 to 79.8 tok/s, but fresh code fell from roughly 68-71 to 66.3 and prose from 42.4 to 41.3; the draft length changed 36 times. The operator observed separate recorded GPU work per draft width, with setup/retention costs when widths changed. This is AMD/fork evidence, not a 5070-Ti result, but it adds an important benchmark requirement: when testing adaptive MTP on Blackwell, record CUDA-graph rebuild/capture churn, prewarm candidate widths, and compare a narrow range such as 2-4 or 3-5 against fixed depth 3 rather than assuming 3-12 is free.

4. **NEW-TO-REPO BACKFILL / DIRECT 5070-TI OPERATING POINT — GSQ-RCO + native MTP provides much more context headroom than the current speed ruler.** The community `cruizba/ISTA-DASLab-Qwen3.8-27B-GSQ-RCO-GGUF-Unsloth-MTP` card contains physical RTX 5070 Ti 16 GB measurements on llama.cpp b10689, threads 14, ubatch 256, Flash Attention on, Q4_0 KV, no mmproj loaded. It grafts the native MTP head onto ISTA-DASLab GSQ-RCO target quants while preserving every target tensor byte-for-byte; reported perplexity is identical before/after the graft.

   | Target | File size | Proven max context on 16 GB | Greedy MTP on/off | Sampled E2E MTP on/off | Sampled acceptance |
   |---|---:|---:|---:|---:|---:|
   | GSQ IQ2_XS + MTP | 8.63 GB | **224K** (216K comfortable) | 88.9 / 47.7 | 74.8 / 60.7 | 0.450 |
   | GSQ IQ2_S + MTP | 9.46 GB | **204K** (192K comfortable) | 92.0 / 46.2 | 78.1 / 57.8 | 0.511 |
   | GSQ IQ3_XXS + MTP | 10.30 GB | **160K** | 92.8 / 45.0 | 73.9 / 55.9 | 0.459 |

   The sampled protocol is the more useful agent ruler: 800 generated tokens, temp 1.0, top-p 0.95, top-k 20, ctx 163,840. The card explicitly notes that greedy acceptance (~0.69-0.77) overstates real sampled gains versus acceptance ~0.45-0.54. A deeper cached-prefix example on IQ3_XXS reports 42.4 tok/s at a 60K prefix versus 21.97 spec-off, but this is endpoint/prompt dependent and should remain secondary.

5. **CURRENT OFFICIALIZATION — ISTA-DASLab now ships native `-mtp` GSQ-RCO files directly.** The official `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF` repository now publishes optional MTP-integrated variants, roughly 0.35 GB larger, while preserving the target quant weights. The official quality table identifies the useful operating points:

   - IQ2_XS: 2.50 bpw / ~8.4 GB target, smallest;
   - IQ2_S: 2.75 bpw / ~9.3 GB target;
   - IQ3_XXS: 3.00 bpw / ~10.1 GB target, strong all-round point;
   - IQ3_S: 3.50 bpw / ~11.8 GB target, described as task-lossless, matching BF16 on AIME25 and LiveCodeBench and within ~0.51 points on GPQA-Diamond.

   The native MTP files add about 0.35 GB. There is not yet an independent exact-5070-Ti speed sweep of the new official files in this pass, so use the community physical benchmark as the deployment receipt and the official repo as the quality/artifact source. For the user's 16-GB card, **official IQ3_XXS-mtp is now the highest-priority quality/context A/B candidate**, with IQ3_S-mtp a quality-first control if its reduced context headroom is acceptable.

6. **FRESH SECONDARY — DS4 #967 repairs a current CUDA build regression from shared Metal/TP changes.** `g_tp_block_ctx` had become Apple-scoped while shared code still referenced it, and several shared calls had definitions only in `ds4_metal.m`. The PR restores the non-Apple guard and adds CUDA fallback stubs. `make cuda-spark` builds all five binaries and `./ds4 --help` runs on DGX Spark GB10; full inference was still in progress. This is integration/correctness evidence only, not a speed result.

7. **UPDATE / NO NEW PHYSICAL NUMBER — DS4 #861 was rebased and consolidated again.** Its current body preserves the known two-Radeon-8060S/TB5 measurements: PP prefill 250 tok/s at ~6K and 274 at ~23K, short decode 15.5, long thinking decode ~14.3-14.4, and two-session aggregate +3% to +14%. No new post-cutoff M1/Metal measurement appeared, so the architectural conclusion is unchanged: pipeline/layer ownership remains the practical two-node default and multi-session row batching is the aggregate-throughput path when kernels are already near the DRAM wall.

8. **NO CHANGE — exact dual-M1 Flash-Next and DS4-0731 calibration.** There is still no sustained physical Flash-Next TG on the exact 2x M1 Max 64 GB / TB4 pair and no published 115K follow-up. DS4 #922 still has the exact ~152 tok/s 34K distributed prefill receipt and successful long generation without a sustained generated-token denominator. DS4 #957 still lacks a physical post-coalescing Apple `--layers` throughput gate. Therefore neither dual-M1 decode forecast moves.

9. **NO CHANGE — exact verifier frontier / current direct 5070-Ti speed ruler.** The existing `aipruner/qwen3.8-3bit-test-in-16GB-GPU` Q3_K_XL + native-MTP result remains the primary **speed** ruler: ~97.2 tok/s mixed at 8K and ~111-115 tok/s 24K tool-call generation. The GSQ-RCO lane is a **quality/context** ruler, not evidence that this older direct speed result should be replaced. `ARahim3/mlx-dspark` still has no code push after 2026-09-01 10:54 UTC, and Layr has no post-cutoff submission update.

## Dual-M1 Flash-Next consequence — compiled decode joins sparse QSA as a mandatory architecture gate

The 19:50 pass made selected-KV sparse FA mandatory for long-context prefill. This pass adds a second high-priority serving gate: **compiled low-occupancy decode**.

For the real two-M1 Hermes bring-up:

- keep PP2 / layer ownership primary and TP2 as a control;
- qualify #28349-equivalent selected-KV sparse FA before any long-context score is accepted;
- then A/B an #3334-equivalent compiled B1/B2 decode lane on each stage, with all cache write positions, GDN recurrent state, QSA/indexer state and rope positions represented as explicit tensor state rather than Python-side mutable scalars;
- measure B1 and B2 separately from B4 because the new physical data says dispatch savings are highly occupancy-sensitive;
- run the important operational case where one long-prefill agent joins while one or two agents are already decoding;
- measure stage utilization, CPU/host dispatch time, Metal command submission, and aggregate wall throughput rather than only model-kernel time;
- preserve eager fallback for shapes that do not compile cleanly, including MTP verification and reshape/join events until independently qualified.

The M3 Ultra +79.6% B1 result is a strong *mechanism* signal but is **not** a numerical M1-Max/TB4 forecast.

## RTX 5070 Ti 27B consequence — split the campaign into speed and context/quality lanes

The 5070-Ti plan should now explicitly have two resident target lanes:

### Speed lane — unchanged ruler

- existing Q3_K_XL + native MTP;
- direct result remains ~97.2 tok/s mixed at 8K / ~111-115 tok/s tool-call generation at 24K;
- preserve the #26705-equivalent Q4_K/Q5_K small-N verify-kernel A/B and workload-adaptive draft-depth work.

### Context/quality lane — new candidate

Start with official **GSQ-RCO IQ3_XXS-mtp**:

- materially smaller target than the prior Q3_K_XL / UD-IQ3 families;
- community physical evidence shows the closely matching grafted target survives 160K on 16 GB with MTP active;
- official quality results make it a much stronger low-bit quality candidate than choosing by file size alone.

Then test official IQ2_S-mtp for maximum context-per-quality and IQ3_S-mtp as the quality-first control if it still leaves enough KV/MTP headroom.

The exact-rig matrix should include 8K, 24K, 64K, 128K and the highest no-offload context that survives; real sampled agent traffic; acceptance; VRAM high-water; TTFT; tool/code wall throughput; and explicit verification that no target tensors spill. Greedy MTP results should never be substituted for the sampled agent row.

### MTP quantization follow-up

#28351 makes a future third axis credible: once stable, collect an imatrix for the MTP head itself and compare smaller head quantization under **acceptance + target-equivalence + total VRAM**, not only head file size. A smaller draft that materially reduces acceptance is not a win.

## Adaptive MTP benchmark rule refinement

The existing conclusion remains that draft depth should adapt to workload/acceptance, but the new #27210 result adds a constraint: **adaptation itself has a runtime cost when a backend records or compiles a different graph per width**.

For both Blackwell and Apple:

- prewarm every width admitted by the controller;
- count graph/command capture or compilation events;
- record time spent immediately after a width change;
- compare a narrow adaptive band against a fixed shallow baseline;
- prefer sticky/hysteretic changes over rapid width oscillation;
- keep workload-level acceptance and wall time together in the same result table.

This is complementary to DS4 #965's request-lifetime bypass: one controls *whether* speculation remains profitable, the other controls *how much width churn* the runtime can afford.

## Single M1 Max 64 GB 27B consequence

No new physical M1 result and no P69 consequence. Continue to require bounded MTP/session state construction, no full-history replay merely to manufacture reusable cache state, and process/system/transient memory telemetry in addition to MLX-active memory.

## Forecast consequence

**No change to any canonical dual-M1 Flash-Next decode confidence band.** The fresh Flash result is on M3 Ultra and concerns dispatch/compiled execution, while the exact two-M1 ruler remains missing.

Keep the current mature dual-M1 Flash-Next bands:

### B1 short/medium

| Target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

### ~128K active-context B1

| Target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**. Sparse QSA and low-occupancy compiled decode now have strong physical Apple evidence as two separate pieces of that system, but neither has yet been measured on the real dual-M1 topology.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative; **P69B13 remains next using existing profiling data only**.

## Sources

- oMLX #3334 — compiled Qwen4Exp/Flash-Next decode: https://github.com/jundot/omlx/pull/3334
- llama.cpp #28351 — imatrix collection for MTP / NextN: https://github.com/ggml-org/llama.cpp/pull/28351
- llama.cpp #27210 — adaptive MTP and width-churn follow-up: https://github.com/ggml-org/llama.cpp/pull/27210
- community GSQ-RCO + MTP exact-5070-Ti benchmark: https://huggingface.co/cruizba/ISTA-DASLab-Qwen3.8-27B-GSQ-RCO-GGUF-Unsloth-MTP
- official ISTA-DASLab GSQ-RCO files and quality table: https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF
- official MTP discussion/update: https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF/discussions/4
- DS4 #967 — CUDA build regression fix: https://github.com/antirez/ds4/pull/967
- DS4 #861 — distributed PP/TP/batching branch: https://github.com/antirez/ds4/pull/861
- llama.cpp #27993 — exact 2x M1 Max Flash-Next correctness: https://github.com/ggml-org/llama.cpp/issues/27993
- DS4 #922 — exact 2x M1 Max DS4-0731 long-context thread: https://github.com/antirez/ds4/issues/922
- DS4 #957 — Metal layer-map span coalescing: https://github.com/antirez/ds4/pull/957
- direct 5070-Ti speed-ruler repo: https://github.com/aipruner/qwen3.8-3bit-test-in-16GB-GPU
- Apple speculative-decoding reference: https://github.com/ARahim3/mlx-dspark
- Layr Qwen3.8 MTP challenge: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge
