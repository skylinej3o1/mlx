# Runtime Research Watch — 2026-09-03 17:25 ET

Scope: focused recurring pass after `RESEARCH-WATCH-2026-09-03-1530.md`, using branch checkpoint `bd752888fea910b34df0059a9b369dcfd542766b` / 2026-09-03 19:32:49 UTC as the hard freshness boundary.

Current recurring targets remain intentionally narrow:

1. **Qwen3.8-Flash-Next on the exact planned 2x M1 Max 64 GB / Thunderbolt 4 cluster** — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, cache/state lifecycle, and multi-agent pipeline filling.
2. **DeepSeek-V4-Flash-0731 / DS4 on the same 2x M1 Max 64 GB / TB4 cluster** — distributed decode, PP-vs-TP, Metal shard mapping, activation transport, speculation policy, and multi-session bubble fill.
3. **Qwen3.8-27B on one M1 Max 64 GB** — exact/native verifier/runtime/kernel work and serving-memory behavior.
4. **Qwen3.8-27B on the RTX 5070 Ti 16 GB + 64 GB host rig** — low-bit fit, native MTP/DFlash, verify economics, Blackwell kernels, and coding/tool throughput.

Other hardware is included only when it exposes a mechanism likely to transfer into one of these lanes. External research does not modify the certified exact-Q8 verifier state: P69B12 remains frozen/promoted and **P69B13 remains next using existing local profiling only**.

## Executive delta

1. **FRESH — DS4 #965 adds a deterministic Metal lifetime bypass when DSpark speculation proves unprofitable.** On DeepSeek-V4-Flash-0731 IQ2_XXS/Q2_K on an M5 Max 128 GB, the existing scheduler could repeatedly pause and re-probe low-predictability prose for the whole request even when verification never paid back. The new rule waits for two probe windows, then disables speculation for the rest of the request when lifetime average acceptance falls below **0.5 accepted drafts per scheduler cycle**. It is counter-based rather than wall-time based and is sticky per request. Measured Italian prose improved from **35.9 to 38.5 tok/s** versus 40.6 plain after bypass triggered; reasoning remained **47.9 -> 47.95** versus 45.0 plain; Python remained **54.7 -> 54.6** versus 44.8 plain. English prose remained a mild speculative loss at 41.6 versus 45.0 because its early acceptance did not cross this conservative bypass threshold. These are M5 numbers, not M1 forecasts. The transferable result is the policy: **speculation should be request-adaptive and should permanently fall back to plain decode once lifetime acceptance proves deeply unprofitable.**

2. **NEW-TO-REPO BACKFILL / CURRENT FORMALIZATION — DS4 #952 AProjQ4 is the strongest directly relevant Metal model-layout candidate for the dual-M1 lane found in this pass.** It requantizes only the 215 dense attention-projection tensors across the 43-layer DeepSeek-V4-Flash-0731 checkpoint from Q8_0 to imatrix-guided Q4_K, preserving routed experts, shared experts, output head, tokenizer, and the rest of the checkpoint. The published AProjQ4 artifact is **78.62 GiB versus 80.76 GiB** for AProjQ8, saving **2.14 GiB / 2.65%**. On a fully resident M5 Max 128 GB Metal test, paired decode median was **1.155x / +15.5%**, an independent hot-start median was +14.7%, and Q4 won **32/32** tested context frontiers; the ratio was +17.3% at 2K and +12.9% at 65,536. Full-model prefill was at practical parity. A separate third-party M5 Max validation reproduced **1.155x** decode and prefill ratio **1.003**. The 100-case continuation fixture showed no measured quality regression; it is not evidence that Q4 is universally more accurate. This performance evidence predates the current cutoff, so it is explicitly backfill/formalization rather than a newly published result.

3. **FRESH CAVEAT ON AProjQ4 — current-head reproduction is still required.** A new #952 comment notes that the quoted AProjQ4 measurements are from `6a20b131`; the branch has since absorbed `b0a147a7` and a `main` merge at `6cae5b81`. A prior main merge moved quality numbers slightly but reproducibly, so the current head should be requalified before treating the old ratios as current-head certification. The same fresh note also demonstrates measurable arm-order drift on GB10 and recommends alternating Q4->Q8 / Q8->Q4 when resolving sub-percent effects. For our M1 work, use balanced/interleaved ordering from the start.

4. **NEW-TO-REPO BACKFILL — llama.cpp #26705 directly connects the Blackwell 3-5-column verify bottleneck from the previous pass to an existing CUDA kernel optimization.** The Q4_K/Q5_K vector kernel repeatedly unpacked scale metadata inside the `ncols_dst` loop; branchless scale selection hoists/removes much of that repeated work. The PR reports gains beginning around batch/column width 4-5 on high-bandwidth RTX cards. A direct Qwen3.8-27B Blackwell end-to-end test on an RTX PRO 4000 SFF 24 GB using a 5.01-BPW imatrix/NVFP4 hybrid with embedded MTP measured **41.76 -> 43.11 tok/s (+3.22%)** at 40K context with **78.73% acceptance unchanged and matching response hashes**. On RTX 4090 pure-kernel Q4_K tests, the branchless path improves roughly **+4.8% at ncols=5, +8.9% at 6, +10.8% at 7, +16.5% at 8**; Q5_K shows a similar smaller ladder. The post-cutoff activity on this PR was only code review, so the performance evidence is backfill, not fresh publication.

5. **FRESH SECONDARY CAPACITY LEAD — llama.cpp #28346 proposes swapping multimodal projection and speculative-draft weights rather than making them co-resident.** The draft PR keeps mmproj weights in host RAM, evicts the speculative draft model's unique GPU weights while image/audio encoding runs, streams mmproj to the compute device, then restores the draft. `-fit` is adjusted so it does not reserve both weight sets against VRAM simultaneously. This could matter for the user's 5070 Ti 16 GB if 27B + MTP + vision is desired, but there are no physical throughput, swap-latency, or exact-5070-Ti results yet. Treat as a capacity mechanism only.

6. **FRESH REFINEMENT ONLY — DS4 #964 now publishes a crossover for its exact staged indexed-attention kernel.** The GLM-5.3-Flash specialization engages from 128 selected rows; below that its extra dispatches can cost more than saved row traffic. The reported examples are about **-0.4% at 36 rows, +2.2% at 308, and +10.7% at 1,500**. DeepSeek V4 itself remains explicitly within 0.5% of main, so this does not change DS4 performance. The transferable method is to gate specialized exact kernels on a measured problem-size crossover rather than enabling them universally.

7. **NO CHANGE — exact two-M1 physical rulers remain missing.** No post-cutoff DS4 issue update supplied sustained 0731 generation on 2x M1 Max 64 GB / TB4; #922 remains the ~152 tok/s 34K distributed-prefill receipt with successful 51K CLI generation but no generated-token denominator. No new exact 2x M1 Flash-Next sustained TG surfaced either. `ARahim3/mlx-dspark` still has no code push after 2026-09-01 10:54 UTC, and the Layr Qwen3.8 MTP challenge has no PR updated after the cutoff.

8. **NO CHANGE — oMLX post-cutoff items are correctness/admin follow-ups rather than new machine performance.** #3330 fixed a partial-Scheduler test-double fail-closed path and returned hosted CI green across Python 3.11-3.13; production performance is unchanged. #3419 fixes model-browser sizing for U32-packed MLX quants that could make a ~15.4 GB 4-bit repository appear near 102 GB and be incorrectly marked high-OOM-risk on 64-96 GB machines. Useful operational correctness, but not throughput evidence.

## Dual-M1 DS4 consequence — AProjQ4 should enter the first physical PP2 matrix

This pass changes the **test-plan priority**, not the forecast.

For the first serious DeepSeek-V4-Flash-0731 qualification on 2x M1 Max 64 GB / TB4:

- keep **PP2 / layer ownership** as the primary topology and TP2 as the falsification/control topology;
- qualify the coalesced Metal `--layers` shard-map path before interpreting throughput;
- test the current-head **AProjQ4** artifact/layout as the primary serving candidate;
- retain **AProjQ8** as the same-checkpoint control;
- use alternating/interleaved Q4/Q8 ordering so session drift cannot manufacture a small ratio;
- record per-stage memory, host/process peak, prefill, B1 decode, and B2-B4 aggregate throughput;
- run both plain decode and DSpark;
- record lifetime draft acceptance and scheduler cycles by workload class;
- add a sticky low-acceptance bypass equivalent to #965 if the tested branch supports it;
- separately classify prose, reasoning, and code/tool workloads rather than averaging speculation economics into one number.

Why AProjQ4 is high leverage for this topology: the 215 changed tensors are stage-local dense attention projections. Under layer ownership, each Mac reads only the projections belonging to its local layers; the layout does not create a new TB4 collective. The **2.14 GiB model saving plus repeatable newer-Mac Metal decode win** are therefore directionally compatible with PP2. The measured +15.5% M5 ratio must **not** be transferred numerically to M1 Max until physically measured.

## RTX 5070 Ti consequence — make branchless Q4/Q5 `mmvq` an exact-harness candidate

The direct 5070-Ti Q3/native-MTP receipt remains the primary machine ruler. The previous pass identified small-N target verification as a Blackwell bottleneck; #26705 now supplies a specific implementation candidate for one part of that cost.

Next exact-rig CUDA qualification should:

- preserve the known-fitting low-bit target and current native-MTP baseline first;
- inspect the target tensor-type mix to determine how much verify time actually reaches Q4_K/Q5_K before expecting a gain from #26705;
- A/B an equivalent branchless Q4_K/Q5_K scale-unpack path at verify widths around 3-5;
- record acceptance and response hashes so any speed movement is known to be kernel-level;
- separate code/tool and prose workloads because acceptance remains strongly workload-dependent;
- run both 8K and the practical 24K agent context;
- keep VRAM-residency telemetry: a few-percent verify win is irrelevant if a different quant spills on 16 GB.

The existing exact-GPU result remains the forecast ruler: roughly **97.2 tok/s mixed** in the controlled 8K test and **111-115 tok/s tool-call generation** in the measured 24K lane. The RTX PRO 4000 +3.22% result is mechanism evidence, not a 5070-Ti uplift assumption.

If multimodal serving becomes a goal, #28346 is worth a separate capacity experiment: measure mmproj/draft swap latency, temporary high-water VRAM, context retained, and whether MTP state survives the swap cleanly before considering it production-ready.

## Flash-Next exact dual-M1 consequence

No topology, confidence-band, or bring-up change.

Continue to require:

- exact distributed recurrent/QSA correctness first;
- PP2/layer ownership as the primary topology;
- stage-local recurrent/QSA state;
- TB4 carrying activations and compact metadata rather than recurrent snapshots;
- current gathered/selected-KV sparse-attention path;
- PLE placement/offload tested separately from routed-expert placement;
- workload-gated MTP rather than mandatory speculation under concurrency;
- 3-4 logical agents with normally 2-3 compute-active slots as the practical bubble-fill design point.

The missing physical ruler is still sustained Flash-Next TG on the real 2x M1 Max 64 GB / TB4 topology.

## Forecast consequence

**Do not change the canonical dual-M1 Flash-Next B1, ~128K B1, or B2-B4 probability bands from this pass.** No exact two-node Flash decode receipt appeared.

**Do not synthesize a DS4-0731 dual-M1 decode forecast from the M5 AProjQ4 or DSpark measurements.** Instead, promote AProjQ4 and request-adaptive speculation into the physical test matrix. The exact historical pre-0731 M1/TB4 low-teens decode anchor and the exact 0731 ~152 tok/s prefill receipt remain the physical topology rulers until a current 0731 generated-token measurement exists.

External evidence does **not** modify the exact verifier project. P69B12 remains frozen/promoted; `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
