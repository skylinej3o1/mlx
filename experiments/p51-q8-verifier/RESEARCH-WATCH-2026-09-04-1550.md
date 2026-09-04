# External runtime watch — 2026-09-04 15:50 ET

Freshness boundary: `205d81a5bd0109d80948c3727d53e0d4f119365f` / 2026-09-04 13:22:48 UTC.

This pass is material for architecture and qualification policy, but it does **not** move any
canonical TG / cold-PP target or confidence in `RESEARCH-TARGETS.md`.

## Executive result

- **Dual-M1 Flash and DS4 stay PP2/layer-ownership first, TP2 control.** Fresh two-node physical
  evidence on another Thunderbolt-class topology now shows pipeline beating tensor parallelism even
  when the TP path uses the lower-latency transport.
- **Short-turn cache granularity is now a workload-adaptive requirement, not just an A/B knob.** A
  fresh real coding-agent workload shows an auto-enlarged ArraysCache block size can reduce the
  cache-store rate to 3.9% even on a 256 GB Mac.
- **RTX/Blackwell qualification gains a build/runtime-linkage preflight.** A fresh qwen4exp CUDA
  failure was resolved solely by fixing a CUDA-13-compiled / CUDA-12-linked binary; do not diagnose
  model/runtime instability before proving the binary is linked to the intended toolkit.
- **DS4 agent context and engine context are separate gates.** A fresh M1 Ultra report shows
  `ds4-agent` prematurely compacting a tool result around 1.9K despite a 32.8K configured model
  context. This is an agent-shell bug, not evidence of a model-context ceiling.
- No new sustained physical **2x M1 Max64/TB4 Flash TG**, no sustained exact **DS4-0731 dual-M1 TG**,
  and no newer direct **RTX 5070 Ti 27B** speed receipt surfaced.

---

# FRESH / material after cutoff

## 1. DS4 #861: pipeline beats TP on the same two-node pair even when TP has the faster wire

`antirez/ds4` PR #861 was updated after the cutoff with a direct post-rebase pipeline-vs-TP
comparison on the same two Radeon 8060S Strix-Halo nodes over TB5.

Matched current-head results:

| workload | pipeline | TP |
|---|---:|---:|
| prefill, ~4–5K prompt | **242 tok/s** over TCP | 166 tok/s over NHI |
| decode, 1024 tokens / small ctx | **15.08 tok/s** | 13.86 tok/s |
| decode, 128 tokens @ ~4–5K ctx | **14.01 tok/s** | 12.93 tok/s |

The authors' interpretation is that pipeline is about **1.45x faster on prefill** and **8–9% faster
on decode** on this two-node deployment. TP pays many synchronization/gate exchanges per token;
pipeline moves an activation once across the stage boundary. The same PR reports a current-head
NHI TP run at 14.01 tok/s with byte-identical completion and clean transport counters, so this is
not simply a broken-TP comparison.

The hardware, backend and transport are not the planned M1 pair, so **none of these absolute rates
transfer**. The mechanism does transfer strongly:

- two-node layer ownership remains the primary deployment hypothesis;
- TP stays the falsification/control topology;
- low wire latency by itself is not a reason to prefer TP when the algorithm multiplies the number
  of synchronization points;
- multi-session pipeline filling is the more promising aggregate-throughput lever once per-node
  matvecs approach the memory wall.

The same PR also reports 2-client batched-session aggregate gains of +3% on short prompts to +14%
on longer prompts versus serial, reinforcing the multi-agent bubble-fill direction. Again, this is
mechanism evidence only.

**Consequence:** strengthen architecture confidence in **PP2/layer ownership first** for both DS4
and Flash, without changing the numerical performance-target probability ladders.

## 2. oMLX #3443: real coding-agent traffic confirms coarse ArraysCache blocks can destroy reuse

Fresh issue #3443 reports a production-style coding-agent workload on an M3 Ultra 256 GB using
hybrid GDN / ArraysCache models including Qwen3.8-Flash-Next.

Key workload facts:

- 51,700 requests over ~32.3 hours;
- 88.0M prompt tokens versus 2.9M completion tokens (~30:1 prompt-heavy workload);
- median prompt **1,514 tokens**;
- runtime enlarged `paged_cache_block_size` from 256 to **4096**;
- 32,542 boundary-snapshot-unavailable skips versus only 1,325 stores;
- effective store rate **3.9%**;
- essentially all skipped prompts were below one 4096-token block.

The cache itself worked when a full boundary existed. A ~7,068-token repeated prompt fell from
18.48 s cold to 6.09 s and then 2.39 s; a ~2,819-token identical prompt below one block showed no
useful reuse. Absolute wall times are noisy because the host was serving ordinary traffic, but the
mechanism is explicit in the boundary diagnostics.

Especially important: the runtime chooses 4096 on >=64 GB systems in this path, so a larger Mac can
receive **coarser cache granularity** than a smaller one. Hardware RAM size is therefore a bad proxy
for conversation-turn geometry.

This materially strengthens #3430. The dual-M1 Flash qualification should no longer be just a
64/128/256/2048/4096 static A/B. Record the real workload distribution and optimize against it:

1. prompt-length distribution (p50/p90/p99 and common shared-prefix lengths);
2. attempted-store count, successful-store rate and `available_boundaries=0` skip rate;
3. cached-token ratio and exact-prefix hit rate;
4. cold-turn and repeated-turn wall latency;
5. boundary-capture/snapshot overhead;
6. memory/high-water impact;
7. exact serialization continuity for assistant/tool turns.

**Promotion rule:** a cache policy is not good merely because its isolated hit is fast. It must
produce a high store/hit rate on the intended Hermes/coding-agent workload without excessive cold
snapshot cost. Prefer an exposed/workload-selected or adaptive block size over one inferred only
from installed RAM.

## 3. llama.cpp #28403: verify CUDA compile/link/runtime consistency before blaming qwen4exp

Fresh qwen4exp report #28403 initially looked like a Blackwell SOFT_MAX failure on an RTX PRO 4500.
The reporter later resolved the failure **without any source change**.

Diagnosis:

- `nvcc`/compile toolkit: CUDA 13.3;
- produced `libggml-cuda.so` was silently linked against system CUDA 12 `cudart/cublas`;
- rebuilding with explicit `CUDAToolkit_ROOT`, CUDA compiler and architecture linked CUDA 13
  libraries and removed the abort on the same commit/model/driver.

The same report then showed a non-monotonic CPU-MoE offload curve on that 32 GB card; for example
`-ncmoe 36` delivered higher PP/TG than heavier CPU-MoE placements, while pushing to `-ncmoe 28`
OOMed. That result is useful as a reminder that hybrid placement has a fit/throughput optimum, but
it is a **104 GiB Flash model on a 32 GB PRO 4500**, not the user's 16 GB 5070-Ti 27B lane. Do not
transfer its rates or optimal split.

Add a preflight to every exact 5070-Ti promotion run:

- record driver version, toolkit/nvcc version and target SM;
- inspect the actual linked `cudart`, `cublas`, `cublasLt` major versions (`ldd` or Windows
  equivalent);
- record llama.cpp/runtime commit and build flags;
- fail the benchmark if the linked runtime is not the intended toolchain;
- only then run the existing prompt-shape/ubatch stability matrix.

This complements, not replaces, the still-open #28377 ubatch/content-dependent cuBLAS stability
probe; #28403 explicitly warns that its linkage diagnosis does not explain every similar CUDA
report.

## 4. DS4 #973: agent compaction can fail far below configured model context

Fresh issue #973 is on **M1 Ultra 128 GB**, DS4-0731 AProjQ8 + DSpark sidecar, Metal, configured
with `-c 32768`. A request to read a 1:500-line source file immediately triggered the agent's
internal compaction around an ~1.8K old context and rebuilt to ~1.96K, after which `ds4-agent`
reported context full despite the 32.8K configured context.

This does **not** establish a DS4 engine context limit. It is an agent/tool-result compaction-layer
failure.

For eventual turnkey coding-agent qualification, add an independent shell/harness gate:

- large tool-result ingestion;
- compaction threshold relative to configured context;
- summary + tail reconstruction;
- continuation after compaction;
- repeated tool calls after compaction;
- model engine metrics kept separate from agent-shell context accounting.

Do not let this issue alter DS4 TG/PP or KV-capacity estimates.

## 5. llama.cpp #28213: QSA gather branch remains live after API churn

PR #28213 was freshly rebased after the cutoff to follow a `build_attn_mha` API change. No new Apple
performance result accompanied the rebase. This keeps selected-K/V gather as a live experimental
long-context branch; it does not promote it or move the Flash target.

---

# NEW-TO-REPO BACKFILL / material mechanisms

These predate this pass's freshness boundary, so they are **not fresh**, but they improve the test
plan.

## oMLX #3428: gather wide prefill, not tiny MTP verify rows; retain pooled QSA prefix across trim

M5 Max128 physical work on Flash-Next found:

- gathered QSA is worse than the official masked path for very small query widths used by MTP
  history/verify rounds;
- around wider query widths the gather path becomes profitable;
- keeping the already-valid pooled QSA index prefix across `trim()` avoids fully re-pooling long
  context after rejected drafts.

At 206K context, the reported per-layer numbers illustrate the crossover: S=1 was ~4.20 ms gathered
vs ~1.40 ms official, while S=16 was ~8.65 ms gathered vs ~12.2 ms official. Retaining pooled QSA
state saved roughly 0.75 ms/layer, about 9 ms per speculative cycle over 12 QSA layers in the
reported long-context in-process case.

M5 absolute results do not transfer to M1. The portable rule is:

- **wide/chunked prefill gather A/B**;
- **tiny verify/history rows stay on the cheap official path unless exact M1 data says otherwise**;
- preserve immutable completed pooled-index blocks across rollback/trim and rebuild only the tail.

## oMLX #3437: mmap expert streaming provides a 64 GB capacity fallback, not the primary dual-M1 path

M4 Pro64 Flash-Next oQ2-MTP work streams ~46.9 GB of routed experts from an mmap sidecar. It enables
long-context serving where full residency does not fit, but the measured single-request prefill
ladder falls from ~178 tok/s around 40K to ~124 around 76K and ~111 around 96K. Live testing put the
practical ceiling around 121–122K, not the earlier ~200K projection; 120K was chosen as the
production cap in that report. Concurrent traffic was explicitly untested.

This reinforces the existing policy:

- SSD/mmap expert streaming is a **capacity/fallback/control lane**;
- primary dual-M1 deployment should prefer stage-owned resident experts when aggregate 128 GB
  makes that feasible;
- if streaming is needed, qualify real-context transients and concurrency rather than estimating
  capacity only from steady resident bytes.

---

# Exact-rig no-change confirmations

## Dual-M1 Flash-Next

- No new sustained physical 2x M1 Max64/TB4 TG surfaced.
- No completed ~115K-class exact follow-up surfaced.
- llama.cpp #27993 remains the exact topology/correctness anchor, not a throughput ruler.
- Broader web/community search surfaced older single-M1 64 GB Flash receipts, but nothing fresh and
  independent on the planned dual-M1 topology.

## Dual-M1 DS4-0731

- #922 remains the exact 2x M1 Max64 anchor: ~152 tok/s for 34,384-token distributed prefill,
  successful long CLI generation, but still no sustained generated-token denominator.
- Fresh #861 strengthens PP-vs-TP architecture direction only; it is Strix Halo/TB5, not M1.
- No exact-M1 physical post-#957 coalescing throughput result surfaced.

## RTX 5070 Ti 16 GB / 27B

- `aipruner/qwen3.8-3bit-test-in-16GB-GPU` still has
  `pushed_at=2026-08-20T19:16:50Z`.
- No fresh exact single-5070-Ti physical receipt superseded the existing Q3_K_XL + native-MTP speed
  ruler or the GSQ-RCO context/quality lane.
- Broader HF search continues to show distinct 16-GB and 2x16-GB recipes, but topology/runtime/quant
  differences prevent them from replacing the exact-card rulers.

## Apple 27B external frontier

- `ARahim3/mlx-dspark` still has `pushed_at=2026-09-01T10:54:45Z`.
- `Layr-Labs/qwen-3.8-mtp-challenge` still has `pushed_at=2026-08-29T07:05:19Z`.

## llama.cpp release surface

The 0.4.0 version bump from the prior pass remains merged, and fresh automated build releases are
being published, but a stable GitHub `v0.4.0` release/tag was still not visible at this check. Keep
pinning an exact commit/build rather than assuming the version label alone is enough.

---

# Consequences by lane

## Dual-M1 Flash-Next

Updated bring-up order:

1. pin/certify one exact 0.4.0-era baseline on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 is control;
3. PLE residency/page-cache policy A/B;
4. sparse-QSA wide-prefill A/B;
5. QSA pooled-prefix-retention / trim-tail A/B; keep tiny MTP verify windows on the official path by
   default;
6. recurrent rollback + singleton MTP A/B;
7. adversarial parallel-MTP slot-isolation gate before any MTP concurrency >1;
8. compiled-decode B2/B4 E2E A/B;
9. **workload-derived short-turn cache policy**: prompt distribution + store/hit rates + cold/hot
   wall time, not a RAM-derived block size;
10. SSD expert streaming/direct I/O only as secondary capacity/control lane;
11. combine passing mechanisms, then long-prefill-arrives-during-decode multi-agent stress.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

Keep **PP2/layer ownership primary, TP2 control**; fresh #861 increases structural confidence in
that ordering without moving the numerical target.

Keep AProjQ4 primary serving candidate, AProjQ8 control, adaptive speculation, and the existing
Metal mapping/OS/command-buffer diagnostic gate.

Add a separate `ds4-agent` tool-result/compaction certification if DS4 is exposed directly as the
coding-agent shell. Do not count an agent-shell compaction failure as engine context failure.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No target change. The #3443 workload-level cache result is relevant here too: if oMLX/ArraysCache
is used, block size must fit the actual conversation-turn distribution and be judged by store/hit
rates. ANE remains a separate approximate lane.

Canonical center remains **25 TG / 110 native PP**.

P69 is unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

## RTX 5070 Ti16 Qwen3.8-27B

Updated qualification order:

1. **CUDA build/link/runtime preflight** and exact SM/build provenance;
2. ubatch 256/512 + neutral/code/tool prompt-shape stability matrix;
3. fully resident Q3_K_XL + native MTP speed lane;
4. small-N Blackwell verify A/B;
5. BF16/Q6_K/Q4_K-imatrix MTP-head A/B for usable context headroom;
6. GSQ-RCO context/quality controls.

Canonical center remains **120 TG / 250 PP**.

---

# Target decision

No canonical target or probability ladder moves in this pass because none of the fresh findings is
a direct physical measurement on the exact user topology for the metric being forecast.

Current normalized centers remain:

| Model / hardware | TG | cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64 / TB4 | **40** | **400** |
| Qwen3.8-27B — M1 Max64 | **25** | **110 native/exact** |
| Qwen3.8-27B — RTX 5070 Ti16 | **120** | **250** |
| DS4-0731 — 2x M1 Max64 / TB4 | **15** | **180** |

Fresh mechanism evidence changes **what we test and what defaults are safe**, not the calibrated
performance distribution.
