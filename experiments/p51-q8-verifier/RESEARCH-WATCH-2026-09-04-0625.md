# External runtime watch — 2026-09-04 06:25 ET

Freshness boundary: `7672162d1ae45a90a6a10fe6d1457bdcd7cf8057` / 2026-09-04 05:21:00 UTC.

This pass preserves the four narrow lanes: exact 2x M1 Max 64 GB / TB4 Flash-Next, the same pair for DS4-0731, single-M1-Max-64 Qwen3.8-27B, and RTX 5070 Ti 16 GB + 64 GB host Qwen3.8-27B. Older discoveries are backfill only; direct physical evidence is required to move forecasts.

## Findings

### FRESH / MATERIAL — Flash-Next PLE residency is now an explicit serving variable

llama.cpp #28355 was updated/closed after the prior checkpoint. The apparent regression where Qwen3.8-Flash-Next's ~27 GiB `per_layer_token_embd` table was no longer resident is the intended result of the new lazy-loading default from #27969, not a loader failure.

Key facts from the report/discussion:

- tensors above 4 GiB are eligible for `--lazy-mode auto`;
- the Flash-Next per-layer n-gram/PLE table is ~27 GiB and can therefore be served from mmap/page cache row-by-row instead of being permanently resident;
- `--no-mmap` alone does not force this tensor resident because the lazy tensor still receives a mapping;
- after other model/disk activity evicted useful page-cache state, the reporter saw prefill fall from roughly **2400 to 1000 tok/s**;
- when host RAM permits, the explicit resident control is `--lazy-mode off -ot per_layer_token_embd=CPU`.

Consequence for the planned 2x M1 Max 64 GB / TB4 system: PLE/n-gram residency must be a recorded qualification variable. Do not compare prefill runs unless lazy/resident mode, page-cache state and competing I/O/model activity are controlled. On the real 64 GB nodes, do not blindly force a 27 GiB table onto one host; test stage-local/layer-owned placement, direct-read/quantized variants and page-cache eviction behavior against remaining model/context headroom.

This can explain large prefill variance without any kernel change. It does not move decode confidence bands.

### FRESH / MATERIAL DIAGNOSTIC — DS4 `--layers` coalescing is necessary but not sufficient

DS4 #845 received a new physical two-host report after the cutoff. Hardware was **2x M3 Ultra 512 GB** over direct Thunderbolt, using split DeepSeek-V4-Pro-Q4K shards.

Reported timeline on the same hosts/model/scripts:

- macOS 27 Beta 2 / Beta 4, Aug 28-31: **10-13 tok/s** distributed decode;
- macOS 27 Beta 8 (26A5425a), Sep 1-3: **0.14-0.19 tok/s**.

The fresh diagnostics are important:

- wire transfer remained negligible;
- local kernels themselves measured healthy, roughly ~1 ms/layer for the profiled MoE path;
- GPU-busy time was only ~412 ms across 448 command buffers while wall time was ~6.1 s/token, i.e. the GPU was about 97% idle;
- sampled threads spent most time waiting on result/command-buffer completion;
- wired memory stayed near ~433 GiB with zero swap/page-in pressure, unlike the residency-churn failure described in #501;
- a local Metal mapping patch reduced the shard mapping from ~156 buffers to **4 contiguous <=128 GiB buffers**, yet decode remained **~0.16 tok/s**.

Therefore the #957 coalescing fix remains good mapping hygiene and still needs a physical Apple gate, but it is no longer reasonable to treat coalescing alone as the expected cure for every `--layers` collapse. Distributed qualification must also record macOS build, command-buffer completion/wait time, GPU-busy fraction, wired residency and a same-host plain-model control.

This is M3 Ultra + V4 Pro + macOS beta evidence, not direct M1 Max / DS4-0731 calibration. It changes diagnostic order, not the DS4 forecast.

### FRESH / MATERIAL BLACKWELL CAUTION — qwen4exp prompt-dependent cuBLAS failure

llama.cpp #28377 was opened after the cutoff with a deterministic qwen4exp prefill failure on **DGX Spark GB10 / sm_121 / CUDA 13.0** using Qwen3.8-Flash-Next UD-Q4_K_XL (~104 GiB), CPU PLE and Q8 KV.

Reported shape:

- default `-ub 512`: specific prompt lengths/content can fail inside `ggml_cuda_mul_mat_cublas_impl` / `cublasGemmEx` with `CUBLAS_STATUS_INTERNAL_ERROR`;
- the failure is data-dependent rather than a simple length threshold: adjacent neutral lengths can pass while a particular HumanEval-shaped prompt fails;
- memory pressure was ruled out in the report and MTP was not required to reproduce;
- `-ub 256` passed the reporter's 1..600-token sweep and the previously failing HumanEval case.

For the RTX 5070 Ti campaign, add prompt-shape/ubatch fuzzing before accepting a Blackwell build as stable: neutral lengths, code/tool-shaped prompts, `ub=256` vs `512`, MTP off/on, and error-free repeated prefill. Treat `-ub 256` as a workaround/control candidate only. Do not transfer a GB10 failure rate or throughput effect to the 5070 Ti.

### FRESH / MATERIAL SERVING POLICY — short-turn cache block granularity

oMLX #3430 reports that the hybrid ArraysCache currently uses a hard-coded **2048-token block** and only commits whole blocks, which means short repeated turns below that boundary can receive no reusable prefix state.

On M5 Pro 64 GB / Qwen3.6-35B-A3B-oQ4e-mtp, reducing block size to 256/128/64 sharply improved repeated short-turn latency, while smaller blocks increased cold snapshot/boundary overhead. The report also showed that exact replay formatting matters: preserving the prior assistant `<think>\n\n</think>\n\n` serialization retained a longer cached prefix.

No M5 timing transfers numerically to M1. For Hermes-style multi-agent/control traffic, however, cache/state block granularity is now an explicit A/B axis. Test 64/128/256/2048 on realistic short agent turns, and judge total cold + repeated-turn wall time, memory, restore cost and exact state continuity rather than cache-hit percentage alone.

### FRESH / SECONDARY OPERATIONAL — process stop must prove resource release

oMLX #3431 reports `omlx stop` returning success while `omlx-server` remained alive, listening and retaining roughly 30 GB of Metal memory on the reporter's M5 Pro setup. SIGTERM released it.

For constrained Apple qualification, shutdown/reload tests must verify all three: process exit, port release and Metal/system-memory release. Do not trust a CLI success message as proof of lifecycle completion.

### NO CHANGE — exact dual-M1 Flash-Next

No new sustained physical 2x M1 Max 64 GB / TB4 Flash-Next generation rate or completed 115K-class follow-up surfaced. #27993 remains the exact topology correctness anchor, not a TG ruler.

The broader Reddit/Hugging Face pass also did not surface a new exact dual-M1 receipt.

### NO CHANGE — exact dual-M1 DS4-0731

#922 remains unchanged since 2026-09-01: 34,384-token distributed prefill at roughly **152 tok/s**, successful CLI long generation, but no generated-token denominator / sustained TG measurement. #957 itself still has no physical post-fix Apple throughput report.

The fresh #845 Beta-8 report is a valuable negative diagnostic control, not an exact M1-Max DS4-0731 throughput datapoint.

### NO CHANGE — direct RTX 5070 Ti speed ruler / Apple exact frontier

- `aipruner/qwen3.8-3bit-test-in-16GB-GPU` still shows `pushed_at=2026-08-20T19:16:50Z`; no new direct-rig result.
- `ARahim3/mlx-dspark` still shows `pushed_at=2026-09-01T10:54:45Z`.
- `Layr-Labs/qwen-3.8-mtp-challenge` still shows `pushed_at=2026-08-29T07:05:19Z`.
- The existing direct 5070 Ti Q3_K_XL + native-MTP ruler therefore remains the speed lane; GSQ-RCO remains the context/quality lane.

A fresh/broader Hugging Face search contains additional 5070-Ti-class quant recipes, including a single-card vLLM build around ~50.8 tok/s at 4K with no MTP and a two-card 5070-Ti TP2 NVFP4/MTP recipe. Neither supersedes the existing exact single-5070-Ti GGUF ruler because runtime, quant, topology and residency differ.

## Updated test consequences

### Dual-M1 Flash-Next

Bring-up order is now:

1. plain exact PP2/layer-owned baseline;
2. explicit PLE residency policy A/B: lazy/page-cache vs stage-local resident/direct-read/quantized, with competing I/O eviction test;
3. sparse-QSA experimental A/B;
4. compiled-decode experimental A/B using end-to-end serving metrics;
5. short-turn cache-block granularity / exact assistant replay;
6. only then combine passing mechanisms and run long-prefill-joins-active-decoders multi-agent tests.

Every prefill result should record PLE residency mode and page-cache condition. Every lifecycle result should prove actual memory release.

### Dual-M1 DS4

Keep PP2/layer ownership primary and TP2 as control. Keep current-head AProjQ4 as the serving candidate with AProjQ8 control. Update the mandatory distributed diagnostic gate:

1. verify coalesced/sane Metal mappings;
2. record OS build and command-buffer wait/completion behavior;
3. measure GPU-busy fraction and wired residency during decode;
4. run a same-host non-distributed/control model path before blaming TB4;
5. only then evaluate PP bubble/interconnect and multi-session filling.

### RTX 5070 Ti 27B

Keep Q3_K_XL + native MTP as speed lane and GSQ-RCO as context/quality lane. Add a Blackwell stability matrix before performance promotion:

- ubatch 256 / 512;
- neutral length ladder plus code/tool-shaped prompts;
- MTP off/on;
- error-free repeated cold/warm prefill;
- then #26705-equivalent small-N verify A/B and normal 8K/24K agent throughput.

### Single M1 Max 64 GB 27B

Retain the 01:15 ANE rule: hidden ANE bank memory is a first-order admission term. Add cache-block granularity and stop/reload resource-release checks to the serving qualification matrix.

## Forecast / exact-verifier consequence

**No canonical performance forecast moves.** None of the fresh items is a sustained exact 2x M1 Max Flash-Next/DS4 TG result or a new exact single-5070-Ti speed ruler.

The pass changes diagnostics and serving policy substantially:

- Flash prefill must control PLE residency/page-cache state;
- DS4 mapping coalescing is necessary but not sufficient;
- Blackwell qwen4exp qualification needs prompt-shape/ubatch fuzzing;
- short-turn cache block size and exact replay serialization become explicit serving variables.

The mature dual-M1 Flash design target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, still unmeasured on the real pair.

P69 is unchanged. **P69B12 remains frozen/promoted and P69B13 remains next using existing profiling data only.**
