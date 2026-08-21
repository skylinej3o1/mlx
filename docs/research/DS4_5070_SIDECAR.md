# DeepSeek V4 Flash 0731 — RTX 5070 Ti speculative sidecar

Status: **CORE / promoted experiment**

This note captures the **ThriftOps Supreme** heterogeneous design for the existing two-M1-Max DeepSeek V4 Flash 0731 Q2/Q4 tensor-parallel target.

The central idea is to stop asking the two Macs to hold the giant target, perform Thunderbolt TP, host a speculative drafter, and perform verification at the same time. Instead, assign each device the work it is best at:

```text
M1 Max #1 ----\
                +-- DS4 0731 Q2/Q4 TP target + KV + verifier
M1 Max #2 ----/
        ^
        | small feature / candidate protocol
        v
RTX 5070 Ti 16GB
        +-- DSpark / DFlash2 / future custom drafter
```

The RX 6800 remains optional auxiliary capacity for independent agents, embeddings, reranking, evaluation, or other non-synchronous work.

## Why this is attractive

The current two-M1-Max TP path is already a strong baseline at roughly **17.5 tok/s**. Its problem is not simply target compute: deeper speculative verification can amplify TP communication and synchronization over Thunderbolt 4 enough to erase the gain from a good drafter.

A discrete CUDA sidecar lets us attack the system in two independent places:

1. **make drafting cheap and remove drafter residency/workspace from the Macs**;
2. **specialize the M1 TP verifier for small M, beginning at M=2, so speculative verification amortizes rather than amplifies Thunderbolt cost**.

The performance objective is therefore:

> **minimum wall-clock milliseconds per committed target-verified token**, including drafter latency, network latency, TP collective time, verification, and acceptance.

Do not optimize draft acceptance or draft TPS in isolation.

## Current 0731 DSpark facts to verify against the exact checkpoint/runtime

Current public 0731 DSpark implementations indicate a drafter with approximately these properties:

- compact Q2K/Q4K-class DSpark around **7.8 GiB**
- larger Q8-class DSpark around **10-11 GiB**
- draft block size around **5**
- hidden size **4096**
- conditioning on target features from only a small set of late target layers, currently reported as **[40, 41, 42]**

These are implementation/checkpoint facts, not MXFORGE invariants. Re-confirm them before coding against a specific model revision.

If three FP16 feature vectors of width 4096 are sufficient, the raw feature payload is only:

```text
3 * 4096 * 2 bytes = 24,576 bytes ~= 24 KiB
```

per target step before protocol overhead.

That makes **bandwidth almost irrelevant** for the sidecar link. The engineering concern is round-trip latency, synchronization, serialization, and pipeline bubbles.

## Stock DSpark limitation

Do not assume a stock DSpark GGUF is a fully independent remote model.

Current DSpark packaging may omit or borrow target components such as token embeddings and/or the output head and consume internal target features. Same-host runtimes can place drafter and target on different local GPUs, but that does not automatically make a Mac-target / remote-5070 topology work.

The sidecar experiment therefore needs one of two solutions:

1. **self-contained DSpark packaging** — duplicate/quantize any borrowed embedding/output components on the 5070; or
2. **explicit sidecar protocol** — expose the minimal target state DSpark needs and return candidate IDs/confidences to the Mac coordinator.

Because the 5070 Ti has 16GB VRAM, a compact ~7.8GiB DSpark plus duplicated Q8-ish embedding/output components and workspace appears capacity-plausible. Measure exact residency rather than relying on arithmetic estimates.

## Why the 5070 Ti before the RX 6800

Prefer the RTX 5070 Ti for the speculative sidecar because it provides:

- CUDA and the most active speculative-decoding ecosystem
- strong low-precision Blackwell execution
- CUDA graphs / mature profiling
- better path toward DFlash2 and custom learned drafters
- simpler reuse of current llama.cpp/SGLang/vLLM-style ideas

The RX 6800 can remain useful, but heterogeneous synchronous HIP/Vulkan drafting adds engineering risk without an obvious advantage over the 5070.

## Context benefit: preserve Mac memory for target state

The 5070 sidecar does **not** magically add 16GB of KV memory to the M1 target.

The useful effect is different:

> **speculation can be added without paying the drafter-residency and drafter-workspace cost out of the Macs' unified-memory budget.**

That preserved memory can remain available for:

- target KV / MLA state
- larger context
- higher KV precision
- larger prefix cache
- M=2..N verifier workspace
- healthy OS / Metal headroom

When comparing context ceilings, always distinguish:

- current **target-only** TP baseline, which does not pay DSpark residency at all;
- Mac-resident DSpark, which may reduce context headroom;
- 5070-sidecar DSpark, which should preserve most of the target-only Mac memory budget.

Do not claim a fixed `+N tokens` from moving the drafter. Measure the exact target-state bytes/token and actual freed Mac residency first.

## First verifier target: M=2

Previous TP speculative experiments warn that broad verification can become expensive over Thunderbolt because multiple verification rows increase distributed communication/gating cost.

Therefore do **not** begin by forcing the drafter's maximum block depth.

Start with **M=2**:

1. freeze/certify target-only TP;
2. measure M=2 target verification with no remote drafter in the loop;
3. split verifier wall time into local Metal compute, TB4 collective/wire, coordinator overhead, and idle/bubble time;
4. specialize the M=2 execution/communication path;
5. only after M=2 is efficient, add the 5070 drafter;
6. then sweep M=3, M=4, M=5 and stop when accepted-token economics worsen.

This is deliberately the opposite of maximizing speculative depth first.

## Communication attack across all phases

Treat Thunderbolt as an optimizable systems constraint rather than a fixed tax.

Research axes:

### TP partition / placement

- place target tensors and experts to minimize cross-node traffic, not merely equalize bytes
- test asymmetric placement when one side becomes communication-hot
- consider selective replication of tiny/high-frequency shared state when memory permits

### Collective reduction

- fuse adjacent communication where correctness permits
- avoid repeated synchronization inside one verification block
- batch candidate-row communication
- test block-level commit/verification protocols inspired by current DS4 PP/speculation work

### Overlap

- overlap Mac local compute with TB4 transfers
- double-buffer verification state
- overlap 5070 drafting with the next available Mac-side preparation whenever dependency boundaries allow it

### Compression

- quantify whether activation/feature exchange can use lower precision without changing target correctness or materially harming acceptance
- candidate IDs and metadata should remain tiny; do not invent large remote-state transfers unnecessarily

### Topology alternatives

- retain TP as the primary baseline
- benchmark PP and hybrid approaches where they reduce synchronization frequency
- do not switch topology in a live long-context session unless KV/state migration economics justify it

## Sidecar protocol sketch

A first explicit protocol can remain very small:

### Mac coordinator -> 5070

- request/session ID
- latest committed token IDs / minimal draft prefix
- required target feature vectors
- draft depth / policy parameters
- optional workload/policy flags

### 5070 -> Mac coordinator

- candidate token IDs
- optional candidate probabilities/confidences
- drafter latency telemetry
- model/policy revision identifier

The Mac target remains authoritative. No candidate is emitted unless target verification accepts it.

Favor a persistent binary connection with preallocated/pinned buffers over high-overhead request/response serialization. Benchmark local/direct-network latency separately from model time.

## Candidate drafter ladder

The 5070 makes it possible to compare multiple drafters without consuming Mac target memory:

1. compact 0731 DSpark (~7.8GiB class)
2. larger/higher-precision DSpark as acceptance control
3. DFlash2 if/when a real 0731-compatible implementation is validated
4. small/native MTP where it can be separated cleanly
5. future custom compact drafter trained specifically for DS4 0731 and coding/agent workloads

The smallest drafter is not automatically best. Sweep the Pareto frontier of:

- draft latency
- VRAM
- acceptance
- accepted tokens per verify
- effective end-to-end tok/s

## Benchmark matrix

At minimum record:

| Metric | Required |
|---|---|
| target-only TP tok/s | yes |
| M=2..5 verify latency | yes |
| local Metal compute time | yes |
| TB4 collective/wire time | yes |
| 5070 draft latency | yes |
| sidecar RTT / serialization | yes |
| accepted tokens / cycle | yes |
| effective target-verified tok/s | yes |
| Mac steady/peak memory | yes |
| 5070 steady/peak VRAM | yes |
| KV/state bytes per token | yes |
| context ceiling with output reserve | yes |

Use separate workloads for code, copy/refactor, tool/JSON, and reasoning/prose because speculative acceptance can vary enough to change the winning configuration.

## Suggested milestone targets

Treat these as engineering goals, not forecasts.

### Baseline

- preserve ~17.5 tok/s target-only TP
- obtain a trustworthy communication/computation profile

### Communication-only improvement

- target roughly **20-22 tok/s** target-only if collective/placement/overlap work pays off

### Sidecar + efficient small-M verification

- first meaningful milestone: **25+ effective tok/s**
- strong milestone: **30+ effective tok/s** on favorable coding/agent traffic
- higher results require measured acceptance and verifier economics; do not multiply unrelated speedups

Long-context targets should be certified separately. Peak short-context speculation must not be used as evidence for sustained 100K+ performance.

## Relationship to the adaptive waterfall

The sidecar becomes another scheduler dimension rather than a permanent mode.

Possible policy outputs now include:

- target topology: TP / PP / future hybrid
- speculative method: target-only / small MTP / 5070 DSpark / DFlash2 / lookup
- verification width M
- drafter residency: Mac / 5070 / none
- KV precision/compression mode
- prefill strategy

A plausible measured phase diagram could select the 5070 sidecar for short/medium code traffic, fall back to small MTP as acceptance or context changes, and disable speculation entirely when verification no longer repays its communication cost.

## Priority order

1. freeze/certify current DS4 Q2/Q4 TP baseline;
2. profile TB4 communication at M=1 and M=2..5;
3. optimize **M=2 verifier/collective path first**;
4. package/prototype a self-contained compact 0731 DSpark on the 5070 Ti;
5. build the minimal feature/candidate sidecar protocol;
6. certify M=2 end-to-end;
7. sweep M and workload class;
8. compare DSpark against small MTP and any real 0731 DFlash2 candidate;
9. integrate the winning modes into the adaptive waterfall;
10. only then spend time on increasingly exotic drafter compression/custom training.

## ThriftOps principle

This branch intentionally treats heterogeneous existing hardware as an advantage:

> **do not ask one box to do everything; assign each piece of silicon the phase it executes most efficiently, and minimize the information that must cross device boundaries.**

For this system, that means the Macs remain the capacity-rich Metal target cluster while the 5070 Ti becomes a low-precision speculative accelerator. The success metric is whole-system time-to-useful-token, not whether any individual device wins a conventional benchmark.
