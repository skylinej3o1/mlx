# Runtime Research Watch — 2026-09-01 Midday

Scope: external runtime/model research only. This note does **not** modify the certified P69 verifier state. **P69B13 remains next, using existing profiling data only.**

This is a delta from `RESEARCH-WATCH-2026-09-01-MORNING.md`.

## Qwen3.8-Flash-Next

### oMLX #3356 — +26% long-context decode on Metal from PLE gather + split-K QSA

PR: https://github.com/jundot/omlx/pull/3356

Physical A/B on **M5 Max 128 GB** at roughly **92K context**:

- combined chain: **34.2 -> 43.3 tok/s (+26%)**
- PLE gather isolate, n=24: **34.23 -> 36.71 tok/s (+7.3%)**
- split-K isolate, n=8, with the PLE fix live in both arms: **35.75 -> 43.25 tok/s (+21.0%)**
- sparse-GQA kernel at ~98K, 16 splits: **1.21 -> 0.30 ms/layer (~4.0x)**

Root causes:

1. The PLE gather evaluated the id tensor, read it to the host with `.tolist()`, then rescanned shards per id. That created an ~11 ms/forward host stall mid-GPU-forward and failed to overlap cold faults spread across many shards. The replacement buckets ids, warms all touched shards through threaded pread, dequantizes once, and uses a bounded hot-row LRU. The PR reports bitwise-identical output versus the legacy gather on the real 320M-row / 128-shard table.
2. QSA sparse-GQA verification had only about six threadgroups at common MTP verify widths on a 40-core GPU. Split-K partitions the selected-key tile loop across more threadgroups, then merges fp32 partial softmax/output state. The PR reports 99.96% elementwise bit equality to the single-pass output and a maximum deviation of 0.2 bf16 ULP.

Implication for the dual-M1 project: **strong evidence that a large part of Flash-Next long-context decay is still removable Metal/runtime overhead rather than unavoidable model cost.** Do not scale the M5 number directly to M1, but PLE host-stall removal and sparse-QSA width/occupancy are high-priority portable mechanisms to benchmark on M1.

### llama.cpp #28136 — correction: direct PLE reads, not a B1 async-scheduling PR

PR: https://github.com/ggml-org/llama.cpp/pull/28136

The current upstream #28136 is **`qwen4exp: direct reads for the lazy PLE table`**. A prior watch entry had misidentified this PR number as a lean-B1 scheduling change; do not carry that attribution forward.

On a **single DGX Spark GB10**, the reporter found repeated-token synthetic prefills could show 700+ tok/s while real prompts fell to roughly **300 tok/s** because lazy mmap demand paging caused severe PLE over-read/page-fault serialization. An explicit `pread()`-based `--lazy-mode on-direct` path raised real-world input prefill to roughly **750–800 tok/s**, without pinning the PLE table in RAM.

Implication: benchmark prompt composition matters materially for Flash-Next PLE paths. Repeated-token PP benches can systematically overstate real-agent prefill. This independently agrees with oMLX's finding that the PLE gather/storage path is still a major runtime lever.

### Exact 2x M1 Max / TB4 llama.cpp RPC report — no new throughput receipt

Issue: https://github.com/ggml-org/llama.cpp/issues/27993
Fix: https://github.com/ggml-org/llama.cpp/pull/27960

The exact **2x M1 Max 64 GB MacBook Pro + point-to-point Thunderbolt 4** report still has no newer sustained TG/PP measurement after the RPC allocation fix. The latest operator comment remains the Aug 30 correctness confirmation:

- 2.5K needle coherent after the fix
- 4K needle passes
- Q8 K/V passes the formerly broken threshold
- 115K needle at 256K context was started, with no later result posted

Therefore the dual-M1 throughput figures remain **forecasts**, not measurements.

### MTP artifacts

Fresh Qwen3.8-Flash-Next GGUF MTP artifacts are appearing publicly on Sep 1. This improves bring-up availability but is **not** counted as a performance result until a controlled target-only/MTP A/B with acceptance and output-fidelity data is published.

## DeepSeek V4 Flash 0731

### DS4 #861 — Thunderbolt/USB4 NHI provides a direct PP-vs-TP transport control

PR: https://github.com/antirez/ds4/pull/861

Two **Radeon 8060S / Strix Halo** nodes over Thunderbolt/USB4 NHI, MXFP4 target:

TP prefill chunk sweep:

- chunk 256: **126.1 tok/s**
- chunk 512: **137.5 tok/s** — best / new default
- chunk 1024: **122.9 tok/s**

The same binary in **layer-split pipeline mode** reaches **222 tok/s average / 260 tok/s peak prefill** and **13.6 tok/s decode**. The PR states that layer-PP moves about **33x fewer bytes per token** than the per-layer TP all-reduces on this two-node link. TP decode remains gate-RTT-bound at roughly **0.44 ms/gate** despite transport work that reduced a previously serialized FFN exchange from ~34 ms/layer to ~2 ms/layer.

This does not supersede the older 2x M3 Ultra result where tuned target-only TP reached 33.12 tok/s versus ~26.8 tok/s for layer-PP; hardware, transport, kernels and workload differ. It **does** strengthen the specific rule for latency-heavy commodity interconnects: topology choice is dominated by communication frequency and useful compute between synchronizations, not by an abstract TP-vs-PP preference.

Implication for 2x M1 Max/TB4 Flash-Next: this is strong external support for keeping **PP2 primary and TP2 as a falsification benchmark**, especially once speculative spans or request concurrency can fill pipeline bubbles.

### DS4 #799 — Apple Metal multi-session overlap is real

PR: https://github.com/antirez/ds4/pull/799

On **M5 Max 128 GB**, DeepSeek V4 Flash IQ2XXS, `ds4-server --batched-session 8`:

- solo request: ~**116 ms/token/session**
- existing native Metal session batch, B2-B3: ~**110 ms/row**
- per-stream Metal command-queue overlap at count=8: **68.5 ms/row (~1.7x aggregate)**

A separate skinny-dependent-kernel microbenchmark showed about **2.3x aggregate overlap with four queues**. The PR also reports N=4 concurrent streams produced byte-identical output to solo runs at temperature 0. It caps the overlap path at eight streams and notes that normal Metal hazard tracking on the shared model buffers otherwise serializes queues; its untracked-buffer mode measured +63% under multistream.

Caveats: one M5 Max, machine was under unrelated GPU load, PR remains draft, and this is DS4 rather than Flash-Next. Treat it as **mechanism evidence**, not a Flash-Next B8 forecast.

Implication: the user's 3-5 concurrent-agent target is not merely a PP-network utilization story. On Apple GPUs themselves, independent latency-bound decode chains may have meaningful queue-level overlap when state/scratch ownership is made per stream.

### DS4 #919 — multi-request layer-PP remains the direct software pattern

PR: https://github.com/antirez/ds4/pull/919

Still no controlled throughput A/B, but the implementation now permits multiple independent distributed sessions/jobs to be submitted before results are collected, allowing different requests to occupy different pipeline stages instead of serializing one request across the split. Tested on two 128 GB Strix Halo nodes.

For the dual-M1 project, this remains the cleanest public implementation analogue for **multi-agent PP bubble filling**.

## Qwen3.8-27B exact verifier track

Layr challenge: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge

- external frontier remains **3.7291100105909**
- #1481 remains the newest visible candidate and still has no promoted Apple-Silicon score
- no #1482+ result was found in this pass

No external evidence changes the frozen exact-Q8 plan. **P69B13 remains next, existing profiling data only.**

## Updated decisions

1. **Dual-M1 Flash-Next topology stays PP2-first.** DS4 #861 strengthens this specifically for Thunderbolt-class links; #919 supplies the multi-request PP scheduling pattern.
2. **Multi-agent concurrency deserves first-class tuning.** DS4 #799 is direct Apple evidence that independent decode streams can overlap materially on one GPU when mutable scratch/state is separated correctly.
3. **Long-context Flash-Next upside improves.** oMLX #3356 adds a measured +26% Metal result at ~92K from two runtime mechanisms that are conceptually portable to older Apple GPUs.
4. **PLE benchmark hygiene is mandatory.** llama.cpp #28136 shows repeated-token PP tests can hide severe real-prompt mmap/page-fault costs.
5. **Do not raise the dual-M1 >=40 tok/s confidence solely from this pass.** The strongest new number is M5 Max, and the exact dual-M1 operator still has not published throughput. Keep the mature short-context planning confidence around the prior ~85% until exact-hardware measurements arrive.
6. **27B certified verifier state is unchanged.** Do not reopen closed P69 seams from external speculation.
