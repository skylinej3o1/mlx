# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-03-1530.md`

3. Because the canonical state was last consolidated at 05:30 ET on 2026-09-02, also read every dated
   `RESEARCH-WATCH-*` delta newer than that consolidation point when reconstructing the
   current state. In particular, retain `RESEARCH-WATCH-2026-09-03-1330.md` for its broader
   machine-specific backfill receipts, but use the narrower scope below for future recurring scans.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Current watch scope

Recurring scans are now intentionally narrow:

- **Flash-Next:** primarily the exact planned **2x M1 Max 64 GB / TB4** cluster — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, cache/state lifecycle, and multi-agent pipeline filling.
- **DS4-0731:** primarily the same **2x M1 Max 64 GB / TB4** cluster — distributed decode, PP-vs-TP, Metal shard mapping, activation transport, multi-session bubble fill, and portable pre-M5 Metal work.
- **Qwen3.8-27B / Apple:** one **M1 Max 64 GB**, especially exact/native verifier/runtime/kernel work and serving-memory behavior.
- **Qwen3.8-27B / NVIDIA:** the user's **RTX 5070 Ti 16 GB + 64 GB host RAM** rig, especially low-bit fit, native MTP/DFlash, verify economics, Blackwell kernels, and coding/tool throughput.

Other machines should be promoted only when they expose a mechanism likely to transfer into one of those four lanes.

## Current newest delta — 2026-09-03 15:30 ET

Freshness boundary: branch checkpoint `a11fbb354a8643007a2b203b31f5411e8e7e1065` / 2026-09-03 17:35:38 UTC.

Material deltas:

- **NEW — 5070-Ti-relevant Blackwell MTP mechanism:** fresh llama.cpp #28196 tracing on native-Linux sm_120 with the exact Qwen3.8-27B-0814 Q4_K_M blob measured **67.7 -> 119.8 tok/s (1.77x)** at draft depth 4. Code gained **2.18-2.38x** at 0.68-0.75 acceptance; prose gained 1.30-1.41x at 0.29-0.34 acceptance. The trace identifies the small-N wide target verify path as a concrete target: five-column quantized matvecs ran at **66-71% of bandwidth bound vs ~84% single-column**, costing roughly 5 ms per MTP step, plus ~2.8 ms for four LM-head draft passes. Absolute PRO-6000 rates do not transfer to the 5070 Ti; the kernel shape does.
- **NEW — M1-Max-64 serving-memory mechanism:** oMLX #3330 fixes a Qwen3.8-27B MTP cache-miss path that could replay a completed **10K/30K prompt solely to manufacture a cache terminal**, creating **159-236 GB transient attention graphs**. The new path writes normal prefill blocks through hot/SSD cache and reconstructs only a bounded suffix. Physical validation is M3 Ultra, so this is not an M1 TG receipt, but it directly removes a catastrophic 64-GB transient-allocation pattern.
- **SUPPORTING — adaptive MTP:** fresh llama.cpp #27210 results on other hardware again show adaptive draft depth preserving prose while exploiting high-acceptance code. Treat this as policy evidence, not a 5070-Ti performance ruler.
- **NEW APPLE METHOD LEAD ONLY — DS4 #964:** GLM-5.3-Flash gets ~30-32% bit-exact Metal decode improvement on M3 Ultra from staged indexed attention and producer/epilogue fusion, but the PR explicitly reports **DeepSeek V4 Flash within 0.5% of main**. Track the methodology; do not move the DS4 forecast.
- **NO CHANGE — exact dual-M1 Flash-Next:** llama.cpp #27993 still has no sustained 2x M1 Max/TB4 decode receipt. #28330 has no new physical result and #28243 has no fresh Apple MTP result.
- **NO CHANGE — exact dual-M1 DS4-0731:** #922 still has ~152 tok/s 34K distributed prefill but no sustained decode TG. #957 still lacks a post-fix Apple `--layers` throughput gate; #861 has no post-boundary update.
- **NO CHANGE — exact 5070-Ti / Apple exact frontier:** the direct 5070-Ti Q3+native-MTP test repo has not been pushed since 2026-08-20; its ~97.2 tok/s mixed 8K mean / ~111-115 tok/s 24K tool-call result remains the exact-rig ruler. `ARahim3/mlx-dspark` still has no code push after 2026-09-01 10:54 UTC, and the Layr Qwen3.8 MTP challenge has no post-boundary PR update.
- **BROADER SEARCH:** no new sustained two-M1 Flash-Next or DS4-0731 decode receipt surfaced.

## Current consequences

### Dual-M1 Hermes

No topology or probability-band change. Keep **PP2/layer ownership primary and TP2 as a control**, state local to each stage where possible, TB4 carrying activations/compact metadata rather than recurrent snapshots, 3-4 logical agents with normally 2-3 compute-active slots, exact hot-session ownership plus durable cold state, and workload-gated speculation.

### RTX 5070 Ti 27B

The direct low-bit/native-MTP receipt remains primary. Add a specific profiling target: shallow/adaptive draft depths, acceptance by workload, and the **3-5-column Blackwell verify matvec / repeated LM-head cost**. Code/tool traffic remains the strongest candidate for deep speculation. Do not sacrifice target fit: the already-tested larger 4-bit file can spill catastrophically on 16 GB.

### Single M1 Max 64 GB 27B

Treat session/MTP terminal construction as a peak-memory problem, not just a steady-state model-fit problem. Avoid any path that replays an entire completed history merely to publish reusable cache state; measure process/system peak and transient graph size in addition to MLX-active memory.

## Forecast consequence

Do **not** change the canonical dual-M1 Flash-Next B1, ~128K B1, or B2-B4 confidence bands. The missing physical ruler remains sustained Flash-Next TG on the real 2x M1 Max 64 GB / TB4 topology; the DS4-0731 sustained two-node TG is likewise still missing.

The mature target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, with multi-agent pipeline filling doing much of the practical throughput work. It remains a design target, not a dual-M1 measurement.

External evidence does **not** modify the certified P69 checkpoint. P69B12 remains frozen and `CURRENT.md` remains authoritative for exact-verifier state; **P69B13 remains next using existing profiling data only**.
