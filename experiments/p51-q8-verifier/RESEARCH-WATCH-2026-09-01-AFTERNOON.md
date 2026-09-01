# Runtime Research Watch — 2026-09-01 Afternoon

Scope: external runtime/model research only. This note does **not** modify the certified P69 verifier state. **P69B13 remains next, using existing profiling data only.**

This is a delta from `RESEARCH-WATCH-2026-09-01-MIDDAY.md`.

## Qwen3.8-Flash-Next

### oMLX #3359 — exact SSD expert streaming creates a low-residency Flash-Next lane

PR: https://github.com/jundot/omlx/pull/3359

This is the most important new deployment-architecture result in this pass. oMLX now has an opt-in exact-routing SSD expert-streaming path for supported MoE checkpoints. For `qwen4_exp`, the 48 backbone routed-MoE layers can use the streaming bank while shared experts and the separate MTP expert layer remain resident; PLE continues through its mmap/SSD path.

Best Qwen development run reported in the PR:

- checkpoint: `Qwen3.8-Flash-Next-MLX-oQ2-MTP`
- routed geometry: 48 layers, 512 experts/layer, top-10
- residency: `cache_only`, zero pinned routed experts
- cache / scratch: 288 / 32 experts per layer, giving a 320/512-row decode bank after scratch lending
- PLE: SSD mmap
- MTP: fixed depth 3
- prompt / generation: 901 / 128 tokens
- loaded / peak MLX memory: **32.230 / 34.092 GiB**
- prompt processing: **362.306 tok/s**
- generation: **40.3625 tok/s**
- MTP acceptance: **100% (96/96 drafts)**
- 2,553 just-in-time loads; 15.496 GB logical expert reads

The material decode gain came from direct publication into proven-idle expert-bank slots. Across three matched runs, direct I/O averaged **363.00 PP / 39.62 TG tok/s** versus **353.23 / 32.62** for staged publication: about **+2.8% PP and +21.5% TG**. The best direct run reached 40.36 TG.

Important caveats:

- the PR body does **not identify the Apple machine used for the Qwen throughput rows**, so these numbers must not be mapped onto M1 Max, M5 Max, or any other specific Apple chip;
- the checkpoint is Q2 and the benchmark had 100% depth-3 MTP acceptance on a forced TerminalBench-derived trajectory;
- this is experimental/default-off and is a development tuning reference, not a portable speed guarantee.

Implication for the dual-M1 project: the important result is **memory architecture, not the 40 tok/s number**. A Flash-Next serving lane can keep the trunk plus a bounded expert bank resident while streaming cold routed experts and PLE, leaving dramatically more unified memory for KV/cache and concurrent agents. This strengthens the case for testing a streamed/degraded-memory mode as a fallback or high-concurrency profile. It also makes a single-64GB-Mac bring-up lane more plausible in principle, but no single-M1 performance claim follows from this result.

### oMLX #3328 — cached-drafter priming result improved

PR: https://github.com/jundot/omlx/pull/3328

The physical M3 Ultra cached-prefix restart receipt has advanced since the earlier watch:

- 98,304 prompt tokens restored from target prefix cache
- 1,689 exact local suffix tokens primed into the drafter
- **98.3% draft acceptance**
- **5.38 committed tokens / target cycle**
- **65.25 tok/s** for 500 generated tokens
- exact output hash matched the unmodified target result
- a cold 99,993-token control skipped priming and retained **867.11 tok/s** prefill

This reinforces the Tameru/prefix-cache design: restoring a huge target prefix does not require replaying the entire MTP history; a verified local suffix can reconstruct useful draft state while leaving cold prompts untaxed.

## Single-GB10 comparison target for multi-agent Flash-Next

The dual-M1 project now has useful measured external targets. These are **comparison baselines, not forecasts for Apple hardware**.

### Felliks / ASUS Ascent GX10, SGLang NVFP4

Repo: https://github.com/Felliks/qwen38-flash-next-one-dgx-spark

Validated on an ASUS Ascent GX10, which uses the same GB10 architecture and 128 GB unified-memory class as DGX Spark; the repository explicitly asks for exact DGX Spark confirmations.

- NVFP4 target, 51.2 GB FP8 PLE mmap on NVMe
- native 262,144 context
- BF16 shared KV pool: 524,288 tokens
- native NEXTN / MTP-213
- **B1: 32.7 tok/s steady**
- **B4: 93.0–93.4 tok/s aggregate**, observed peak 103.36
- repeated B4 batches: each request ~23.6–23.8 tok/s
- resident system memory: 120.45 / 128 GB including OS

### dolf3131 / actual DGX Spark, vLLM NVFP4

Repo: https://github.com/dolf3131/qwen3.8-flash-next-dgx-spark

Measured on one DGX Spark with the Inferact NVFP4 checkpoint and SSD-paged PLE:

- **B1: 32.7 tok/s warm** (30.9 first run after boot)
- **B8: ~102 tok/s aggregate**
- ~2,719 tok/s prefill at 30K
- repeated-prefix TTFT improved ~5.4x with prefix caching
- 76.3 GiB resident weights + ~16 GiB KV; 95.37 GiB PLE paged to swap

These two stacks differ materially in checkpoint, runtime, PLE format, context policy and concurrency limit. Do not average them. They do, however, establish a useful practical target band: **roughly low-90s aggregate at B4 and ~100 aggregate at B8 is already achievable on one GB10-class appliance.**

Implication for 2x M1 Max: do not assume the two Macs beat one Spark under concurrency. The more defensible success criterion is that the old-laptop cluster delivers a large fraction of the single-Spark agent-serving experience. A measured **~80–90 tok/s B4** on the two Macs would already be an exceptional price/performance result; beating ~93 B4 or ~102 B8 should be treated as an ambitious benchmark target, not the base forecast.

## DeepSeek V4 Flash 0731

No new topology result in this pass supersedes the midday DS4 evidence:

- #861 remains the best Thunderbolt/USB4 communication-frequency control: layer-PP moves far less data than per-layer TP collectives on the tested two-node link.
- #919 remains the clean public pattern for filling layer-PP bubbles with multiple independent requests.
- #799 remains mechanism evidence that independent Apple Metal decode streams can overlap when scratch/state ownership is separated.
- the older 2x M3 Ultra result still demonstrates that tuned target-only TP can beat layer-PP on a different hardware/interconnect/runtime cell.

Therefore the topology rule remains conditional rather than ideological: **TP can win when per-layer compute amortizes synchronization; PP becomes increasingly attractive as interconnect latency rises and as speculative spans / independent requests create pipeline depth.**

## Qwen3.8-27B exact verifier track

Layr frontier remains **3.7291100105909**. PR #1481 is still the newest visible candidate and has no promoted Apple-Silicon score; no #1482+ result was found in this pass.

No external result changes the exact-Q8 verifier plan. **P69B13 remains next, using existing profiling only.**

## Updated decisions

1. **PP2 remains the primary dual-M1 Flash-Next topology.** Keep TP2 as a measured falsification experiment rather than the main engineering lane.
2. **Add a streamed-memory serving profile to the future qualification matrix.** #3359 suggests that expert/PLE streaming can exchange residency for much larger KV/cache/concurrency headroom while remaining exact-routing.
3. **Do not infer M1 speed from #3359.** Its Qwen hardware is unspecified and the benchmark is Q2 with 100% fixed-depth MTP acceptance.
4. **Treat ~93 tok/s B4 and ~102 tok/s B8 as external single-GB10 comparison targets.** The dual-M1 project does not need to beat those numbers to be compelling.
5. **Cached-prefix MTP reconstruction remains high-value for persistent agents.** #3328's updated 100K restart result strengthens the compaction/prefix-reuse architecture.
6. **Do not raise the mature dual-M1 >=40 tok/s B1 confidence solely from this pass.** Keep the prior planning confidence around ~85% until exact-hardware throughput is measured.
7. **27B certified verifier state is unchanged.** Do not reopen closed P69 seams from external research.
