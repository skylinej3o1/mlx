# Project 51 research watch — 2026-10-01 07:01 ET

Freshness boundary entering: **2026-10-01 10:28:50 UTC**  
Cutoff: **2026-10-01 11:01:03 UTC**

## Decision

Durable STATE/TARGETS gate updates; **no numerical target movement**.

New rules:
- distributed/head-split GEMMs must control **split-K/reduction arithmetic**, not just match the mathematical GEMM;
- Apple long-prefill qualification must make chunk sizing **depth/watchdog-aware**;
- checkpoint restore continues to require resume-vs-fresh identity, reinforced by a new q8_0 OpenCL silent-restore bug.

## UPDATE — Strata #204: two-GPU GDN split exposes shape-dependent split-K exactness

Strict-window comment at 10:29:18 UTC:
https://github.com/Niko1221/Strata/issues/204#issuecomment-5929534606

2x RTX 3090 + NVLink / IQ3_S, opt-in prompt GDN head split:
- 8K: **2,202 -> 2,337 PP (+6.2%)**;
- 32K: **2,615 -> 2,809 (+7.4%)**;
- 128K: **2,696 -> 2,913 (+8.0%)**;
- decode unchanged ~102-104 TG.

Correctness finding: cuBLAS GemmEx chooses split-K based on GEMM shape, so a half-width projection can reduce in a
different order than the unsplit full projection and change bits. Matching the full-shape split-K via cublasLt restores
GDN-state hash identity at 8K and 21K multi-chunk and passes the long gate.

Classification: **UPDATE / durable exactness mechanism**. No numerical transfer to M1 or 5070 Ti.

## NEW — Strata PR #363 trims verify-window PCIe grouped-expert overhead

Created 10:59:28 UTC:
https://github.com/Niko1221/Strata/pull/363

RTX 4080 SUPER / IQ3_S:
- empty PCIe grouped call **16.51 -> 4.01 us**;
- one-group call **19.11 -> 10.71 us**;
- PCIe expert stage about **0.67 -> 0.20 ms/window**;
- deterministic requests improve about **1.1% TG**;
- ordinary request TG remains within substantial run-to-run scatter.

Bitwise parity tests cover supported grouped quant combinations.

Classification: **NEW verifier-overhead mining evidence**, no target credit.

## NEW — oMLX PR #4147 fixes hybrid KV over-accounting

Created 10:35:47 UTC:
https://github.com/jundot/omlx/pull/4147

Two M5 Pro 64-GB Macs / TB5 RDMA / Qwen3.8-27B-oQ4e-mtp:
- planner KV reservation at 262K: **~49 -> ~17 GB/node**;
- 245,515-token needle admitted and answered **3/3**;
- minimum free memory ~31%, swap flat.

Classification: **NEW mechanism evidence**. Different model/hardware; no Flash/M1 numeric transfer. P51 admission
geometry must charge KV only to KV-bearing layers.

## NEW — oMLX PR #4149 makes deep prefill chunk size depth-aware

Created 10:35:52 UTC:
https://github.com/jundot/omlx/pull/4149

Same 2x M5 Pro 64-GB pipeline:
- fixed 1024-token chunks pass ~124K but trigger Metal watchdog during a ~245K run;
- fixed 512 is safe but shallow standalone PP falls ~680 -> ~380;
- depth-aware chunking keeps 1024 shallow, switches to 512 deeper, and the 245,515-token needle passes **3/3**.

Classification: **NEW Apple long-context safety mechanism**. Add depth x chunk command-buffer qualification; do not
transfer the M5 thresholds to M1.

## NEW — llama.cpp q8_0 OpenCL state restore can report success with an empty cache

Issue #29798 created 10:51:56 UTC:
https://github.com/ggml-org/llama.cpp/issues/29798

On Android/Adreno OpenCL, q8_0 KV state load reports 2,779 tokens successfully restored while writes through q8_0
views are silently dropped; the next decode runs against an empty cache and produces garbage. CPU q8_0 and OpenCL f16
controls restore correctly.

Classification: **NEW backend-specific correctness warning**. Existing P51 resume-vs-fresh token/state identity gate
is confirmed as necessary.

## Strict-window exclusion — llama.cpp Flash-Next MTP

PR #29761 is directly relevant, but its latest update is **11:01:35 UTC**, 32 seconds after the cutoff:
https://github.com/ggml-org/llama.cpp/pull/29761

It is deliberately excluded from this watch and belongs to the next strict window.

## Strict-window negative scan

DASLab GSQ-RCO remains at `ed59f92`; no new checkpoint/allocation/benchmark. citeturn679739search0

Strata latest release remains 0.1.31; oMLX stable remains 0.7.0; TensorFold remains 0.6.0. No material post-boundary
TurboQuant-MLX, MoEspresso, Ishizuki, mlx-serve or MLX-core change affects Project-51 targets.

## Target state

Unchanged:
- RTX 5070 Ti IQ3_XXS PP: **3,000 / 2,900 / 2,750 / 2,500** at 32K/64K/128K/262K;
- 262K/64-GB conditional fit prior: **~90%**;
- IQ3_XXS AA>=38 **~85%**, AA>=40 **~65%**;
- IQ3_S AA>=40 **~80%**;
- K6/V4 long-horizon quality **~60-70%**;
- dual-M1 Flash target: **~40 TG @128K / ~400 PP**;
- RX 6800 secondary lane: **~28-36 TG / ~220-300 PP** planning range.

## New hard boundary

**2026-10-01 11:01:03 UTC**
