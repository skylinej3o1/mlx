# DeepSeek V4 Flash 0731 — adaptive topology/speculation waterfall

Status: **CORE / promoted**

This note restores and generalizes the earlier four-stage MXFORGE waterfall idea for two-node DeepSeek V4 Flash 0731 inference.

The original starting hypothesis was:

| Context band | Earlier candidate |
|---|---|
| 0–~128K | TP + DSpark |
| ~128K–~250K | PP + DSpark |
| ~250K–~350K | TP target-only |
| ~350K–PP ceiling | PP target-only |

Those boundaries were always placeholders. The scheduler rule was the important part: **choose the fastest measured configuration that safely contains the current context plus output reserve**, with hysteresis so the runtime does not thrash between modes.

## Why the old four-stage model should become a measured phase diagram

We now have more viable execution dimensions than when the four-stage hypothesis was first proposed:

### Topology

- tensor parallel (TP)
- pipeline/layer split (PP)
- potentially hybrid variants later

### Speculation

- target-only decode
- small / one-stage MTP
- deeper or custom MTP
- DSpark
- DFlash / DFlash2 if a real 0731-compatible drafter becomes available
- lookup/context-copy drafting where useful

### Context / memory policy

- KV precision / compression mode
- prefill kernel / chunk policy
- drafter resident vs loaded only for decode
- memory hard-limit / wired-limit profile
- optional topology-specific KV layout

The final runtime should therefore not hardcode "four stages." It should build an empirical **context-performance phase diagram** and create as many bands as are justified by real crossover points.

## Candidate matrix

At each context checkpoint, benchmark all configurations that fit safely:

| Topology | Target only | small MTP | deeper/custom MTP | DSpark | future DFlash2 |
|---|---:|---:|---:|---:|---:|
| TP | test | test | test | test | test if available |
| PP | test | test | test | test | test if available |

A candidate is eligible only if it satisfies:

- current context fits with output reserve
- transient prefill / verify working memory fits
- no swap / pathological compression regime
- required drafter weights fit
- correctness gates pass
- no distributed worker/coordinator instability

Among eligible candidates, select the lowest **wall-clock time per emitted target-verified token** for the workload class.

## Example future waterfall — illustrative only

A plausible measured result could look like:

| Context | Example winner | Why it might win |
|---|---|---|
| 0–50K | TP + DSpark | abundant memory; high code acceptance; TP raw decode strongest |
| 50–100K | TP + small/custom MTP | less drafter memory and cheaper M=2/3 verification |
| 100–150K | PP + small MTP | PP buys memory headroom while speculation still repays its verify cost |
| 150–220K | TP target-only | DSpark/MTP workspace no longer earns its memory/communication cost |
| 220–300K | PP target-only | PP becomes the fastest configuration that still fits safely |
| very high context | PP + aggressive KV / compacted state | maximum capacity mode |

This table is an example of the policy shape, **not a prediction of the final boundaries**.

It is equally possible that TP remains fastest much farther than expected, or that small MTP beats DSpark at short context because the TP verifier is cheaper at M=2 than at M=6.

## Benchmark grid

Recommended context checkpoints:

- 2K
- 8K
- 16K
- 32K
- 50K
- 64K
- 96K
- 128K
- 160K
- 192K
- 256K
- then larger checkpoints up to the safe ceiling

For every viable candidate log:

- prefill tok/s and TTFT
- target-only decode tok/s
- effective speculative tok/s
- drafter latency
- verify latency at actual M
- accepted tokens / verify
- collective / wire time
- GPU busy / idle time
- steady-state memory
- peak transient memory
- KV size
- safe output reserve
- correctness / hash or semantic gates

Use separate workloads for:

- code generation
- copy/refactor/code editing
- tool-calling agent traffic
- structured output
- reasoning/prose

A configuration can win one workload class and lose another at the same context length.

## Scheduler rule

The runtime should choose:

> **fastest certified configuration for the current context band + workload class that preserves a configured memory/output safety reserve.**

Inputs can include:

- current context tokens
- expected output budget
- recent speculative acceptance
- free / wired memory
- drafter residency
- TP collective latency
- PP stage balance
- workload classification

## Hysteresis

Do not switch exactly at a measured crossover point. Use separate enter/exit thresholds.

Example:

- TP+DSpark measured best below 55K
- TP+MTP measured best above 55K
- runtime enters MTP at 60K
- runtime does not return to DSpark unless context falls below 50K

This prevents repeated topology/speculation switching near a noisy boundary.

## Topology migration problem

The main implementation challenge is switching TP <-> PP without making the transition cost destroy the benefit.

Research options:

1. maintain compatible KV representations for both topologies when memory permits;
2. migrate / repartition KV at the boundary;
3. rebuild from a prefix cache / compacted checkpoint;
4. schedule topology changes at natural compaction or session boundaries;
5. include migration cost in the crossover model rather than comparing steady-state TPS only.

A theoretically faster band is useless if a topology transition costs minutes of refill.

## Drafter residency policy

DSpark is decode-only, so it does not necessarily need to remain resident during a large cold prefill.

Potential policy:

1. cold prefill with target + KV + prefill workspace;
2. release large transient prefill buffers;
3. load / warm the chosen drafter for decode;
4. unload DSpark and fall back to smaller MTP or target-only if memory pressure crosses a threshold.

This can shift the DSpark context boundary materially upward compared with permanently resident drafting.

## Current research priority

1. Optimize/certify plain TP first.
2. Measure TP M=2..8 verify latency and communication cost.
3. Test a small 0731-specific MTP path before assuming full DSpark is required.
4. Test DSpark after the verifier economics are known.
5. Benchmark PP equivalents on the same machines / quant / contexts.
6. Populate the context-performance phase diagram.
7. Implement the adaptive waterfall only after the individual paths are tuned and certified.

The waterfall is the **integration layer after path tuning**, not a substitute for tuning each path independently.
