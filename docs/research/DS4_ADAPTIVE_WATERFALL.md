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

We now have more viable execution dimensions than when the four-stage hypothesis was first proposed.

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

At the time of this note, DSpark is the native 0731-specific speculative path in DwarfStar. Do **not** assume that a z-lab-style DFlash/DFlash2 checkpoint exists for DeepSeek V4 Flash 0731 merely because some tooling uses `dflash` as an internal architecture name for DSpark-derived support models. Treat DFlash2 as a future candidate until a real 0731-compatible drafter is identified and validated.

### Context / memory policy

- KV precision / compression mode
- prefill kernel / chunk policy
- drafter resident vs loaded only for decode
- memory hard-limit / wired-limit profile
- optional topology-specific KV layout

The final runtime should therefore not hardcode "four stages." It should build an empirical **context-performance phase diagram** and create as many bands as are justified by real crossover points.

## DS4 tuning ladder before the waterfall

The waterfall is the integration layer after the individual paths are optimized. Current order:

1. **Plain TP first** — preserve the current ~17.5 tok/s two-M1-Max result as the distributed baseline and continue raw TP/kernel/collective tuning.
2. **Measure TP verification economics** — explicitly benchmark M=2..8 verify latency and split local compute from wire/collective time.
3. **Small 0731-specific MTP next** — a one- or two-stage drafter may beat DSpark despite lower acceptance if it is much cheaper to keep resident and only requires efficient M=2/3 verification.
4. **DSpark after verifier tuning** — DSpark has higher upside on predictable code, but its deeper blocks only win when target verification and TP communication are cheap enough.
5. **PP equivalents** — tune PP target-only, PP+small-MTP, and PP+DSpark separately rather than assuming PP is only a capacity fallback.
6. **Future DFlash2 / lookup** — add only when a real compatible implementation exists and its complete target-verified economics are measured.
7. **Then populate the phase diagram** and derive runtime thresholds from measured crossovers.

DSpark is therefore **not mandatory** for the fastest practical two-M1 system. The objective is minimum wall time per accepted target-verified token, not maximum draft depth or acceptance in isolation.

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

It is equally possible that TP remains fastest much farther than expected, that target-only TP temporarily reappears between speculative bands, or that small MTP beats DSpark even at short context because the TP verifier is much cheaper at M=2 than at M=6.

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

> **fastest certified configuration for the current context band + workload class that preserves a configured memory/output safety reserve and repays any transition cost.**

Inputs can include:

- current context tokens
- expected output budget / expected remaining session work
- recent speculative acceptance
- free / wired memory
- drafter residency
- TP collective latency
- PP stage balance
- workload classification
- measured cost of the proposed mode/topology transition

The transition rule should be economic, not purely threshold-based:

> **switch only when expected future wall-time savings exceed reload + KV migration/repartition cost by a safety margin.**

## Hysteresis

Do not switch exactly at a measured crossover point. Use separate enter/exit thresholds.

Example:

- TP+DSpark measured best below 55K
- TP+MTP measured best above 55K
- runtime enters MTP at 60K
- runtime does not return to DSpark unless context falls below 50K

This prevents repeated switching near a noisy boundary. Use much wider hysteresis for TP <-> PP than for drafter changes because topology transitions can require KV repartition or reconstruction.

## Metal-specific transition advantage

Apple Silicon makes this strategy unusually practical because the target and auxiliary weights live in unified memory rather than being copied from host RAM into separate discrete-GPU VRAM over PCIe.

Project observation: on the target Macs, model/drafter reloads can be on the order of seconds when files/pages are hot. macOS file caching and memory-mapped model files may make repeated auxiliary-model swaps substantially cheaper than on a conventional discrete-GPU stack.

Treat transitions in two classes:

### Cheap / moderate: same-topology speculation changes

Examples:

- TP+DSpark -> TP+small-MTP
- TP+MTP -> TP target-only
- PP+DSpark -> PP target-only

These can potentially keep the same target model and KV ownership while only changing auxiliary weights/runtime state. The scheduler can be relatively aggressive here if the measured reload cost is small.

### Expensive: topology changes

Examples:

- TP -> PP
- PP -> TP

The target weights may still reload quickly on Metal, but **session state is the critical variable**. If the existing KV/compressed/indexed state cannot be repartitioned, a full long-context prefill can dwarf the model reload.

## KV migration versus full reconstruction

Do not conflate model reload with KV reconstruction.

A full 200K-token reconstruction would cost approximately:

| Effective prefill | 200K rebuild |
|---:|---:|
| 150 tok/s | ~22.2 min |
| 200 tok/s | ~16.7 min |
| 250 tok/s | ~13.3 min |
| 300 tok/s | ~11.1 min |
| 400 tok/s | ~8.3 min |
| 500 tok/s | ~6.7 min |

These are simple `tokens / prefill_rate` estimates, not measured DS4 transition times. They show why a TP->PP switch that throws away 200K of state is usually unacceptable even if the new steady-state topology is faster.

Research options:

1. maintain compatible/topology-neutral cache metadata where practical;
2. migrate / repartition existing KV or DeepSeek compressed/indexed state at the boundary;
3. convert layouts directly instead of replaying tokens;
4. rebuild from a smaller prefix cache / compacted checkpoint only when migration is unavailable;
5. schedule topology changes at natural compaction or session boundaries;
6. include migration cost in the crossover model rather than comparing steady-state TPS only.

A theoretically faster band is useless if the transition cost never amortizes during the remaining session.

## Reference architectures: use intellectually, not literally

MXFORGE should remain a specialized Metal/DS4 runtime, but current datacenter engines validate important architectural pieces.

### TensorRT-LLM

Reference: https://nvidia.github.io/TensorRT-LLM/features/disagg-serving.html

TensorRT-LLM disaggregated serving supports KV transfer between context/prefill and generation executors and documents **cache layout transformation when the two sides use different parallel strategies**, including a TP2 -> PP2 example. This is direct validation that topology-changing KV mobility is a real inference-engine design problem with a production precedent.

Mine the architecture, not the CUDA implementation: block mapping, layout conversion, transfer accounting, and transition correctness are especially relevant.

### vLLM

Reference: https://docs.vllm.ai/en/stable/features/disagg_prefill/

vLLM disaggregated prefill likewise allows prefill and decode instances to use different parallel strategies. Treat vLLM primarily as a scheduler/cache/API reference: prefix caching, chunked/disaggregated prefill, request telemetry, speculative framework, and serving semantics.

Neither framework replaces the current custom Metal/DS4 core. Their value is architectural precedent for **phase-specific execution and movable KV state**.

## Drafter residency policy

DSpark is decode-only, so it does not necessarily need to remain resident during a large cold prefill.

Potential policy:

1. cold prefill with target + KV + prefill workspace;
2. release large transient prefill buffers;
3. load / warm the chosen drafter for decode;
4. unload DSpark and fall back to smaller MTP or target-only if memory pressure crosses a threshold.

This can shift the DSpark context boundary materially upward compared with permanently resident drafting.

The current DwarfStar 0731 DSpark support model is a several-GiB sidecar, so residency policy matters. Do not use issue #607's reported ~51.3 GiB Metal working-set ceiling as evidence that a 64GB M1 Max physically cannot fit DSpark: that field report was operating under a comparatively low Metal wired/working-set ceiling. The correct MXFORGE test is to measure safe wired-limit settings, OS headroom, steady residency, and transient prefill/verify peaks on our own machines.

## Transition benchmark matrix

Every waterfall certification should include a transition table in addition to steady-state throughput:

| Transition | Weight/runtime reload | KV migration/repartition | Total transition cost | Break-even future work |
|---|---:|---:|---:|---:|
| TP+DSpark -> TP+MTP | measure | ideally none | measure | calculate |
| TP+MTP -> TP plain | measure | none | measure | calculate |
| TP -> PP | measure | critical | measure | calculate |
| PP -> TP | measure | critical | measure | calculate |

The scheduler should consume these measurements just as it consumes TPS and memory headroom.

## Current research priority

1. Optimize/certify plain TP first.
2. Measure TP M=2..8 verify latency and communication cost.
3. Test a small 0731-specific MTP path before assuming full DSpark is required.
4. Test DSpark after the verifier economics are known.
5. Benchmark PP equivalents on the same machines / quant / contexts.
6. Prototype KV migration/repartition and measure TP<->PP transition cost.
7. Populate the context-performance phase diagram.
8. Implement the adaptive waterfall only after the individual paths are tuned and certified.

The waterfall is the **integration layer after path tuning**, not a substitute for tuning each path independently.

## Micro-PCTree / parent-conditioned branching — promoted 2026-08-21

PCTree adds a new speculative-policy dimension: instead of committing DSpark's cheap conditional/Markov stage to one linear suffix, retain a small number of parent-conditioned alternatives so an early mismatch does not automatically invalidate all later draft work.

Primary sources:

- https://arxiv.org/abs/2608.02123
- https://www.reddit.com/r/LocalLLaMA/comments/1vunqoz/llamacpp_dspark_pc_tree_fork_up_to_3295_faster/

The public fork provides a useful systems warning: on an RTX 5090, a k4/N22 tree reported **higher acceptance but lower throughput** than k3/N16. It also reported that Qwen3.8-27B Q4 was worse with tested k2-k4 tree settings. Therefore the headline 3.1%-29.5% paper range is not a transferable speed prediction.

For the two-M1 TB4 target, treat large PCTree batches as ineligible until proven otherwise. Introduce **Micro-PCTree**:

- k=2 first;
- N=3..8 initial tree-node budget;
- root-only / first-uncertain-parent hedging;
- asymmetric trees before broad/deep trees;
- equal target-row budgets when comparing against linear DSpark;
- scheduler objective remains `ms / committed target-verified token`.

The 5070 Ti speculative sidecar is the preferred place to build and score the tiny tree. The M1 pair spends the scarce resource: authoritative distributed target verification.

### Updated speculative ladder

For the 5070-sidecar branch, refine the earlier ladder to:

1. plain TP baseline and complete M=2..8 verifier-cost curve;
2. compact 0731 DSpark sidecar bring-up;
3. linear DSpark M2/M3 certification;
4. **Micro-PCTree k2/N3**;
5. sweep N=3..8, including root-only and asymmetric shapes;
6. small/native 0731 MTP comparison;
7. future compatible DFlash2 / lookup candidates;
8. scheduler integration after paired certification.

This ordering is specific to the sidecar experiment and does not invalidate testing a cheap MTP path during verifier development.

### Additional scheduler inputs

The waterfall should now be able to consume:

- rejection-depth histogram;
- recent alternate-parent recovery rate;
- tree shape and node count;
- incremental verifier cost per added node;
- committed-token gain attributable to branching;
- sidecar RTT and tree-construction latency.

A tree candidate is eligible only if its expected hedge value exceeds its additional target-row/collective cost.

Detailed design: [`DS4_MICRO_PCTREE.md`](DS4_MICRO_PCTREE.md).
