# Research mining — cross-model KV/state transfer for model-family handoff

Source:
https://arxiv.org/abs/2608.03893

Paper: **Cross-Model KV Cache Transfer in LLM Families: A Closed-Form Linear Mapping for Prefill Reuse** (Heo et al., arXiv:2608.03893v1, 2026-08-04).

Classification: **portable research lead / future serving seam**. This is not target-lane performance evidence for this repository, does not move any canonical TG/PP target, and does not change the current P69 sequence.

## What the paper establishes

The paper asks whether a running session can move between different-sized members of the same model family without forcing the receiving model to re-prefill the entire accumulated prompt.

For dense full-attention models with matched KV topology, the authors fit a per-head closed-form ridge mapper from source-model KV state to target-model KV state. The mapper combines several source layers for each target layer and maps keys after stripping source RoPE, then reapplies target RoPE.

The useful results are:

- cross-model KV contains substantial approximately linear structure;
- using several selected source layers is materially better than a naive same-layer or single-layer map;
- four of six evaluated matched-KV model pairs retain roughly 73–98% of the target model's standalone accuracy with the linear mapper;
- a small nonlinear MLP substantially recovers the harder pairs, so poor linear transfer is not necessarily a dead end;
- downstream attention-output similarity predicts transfer quality better than raw reconstruction R², which argues for evaluating the consumer of the mapped state rather than only tensor reconstruction error;
- on Qwen3 14B -> 32B at 32K context, mapper application is about 0.28 s versus about 7.0 s for target re-prefill on the paper's 8xH100 setup; the authors report 2.7–25x mapper-vs-reprefill speedups across the evaluated pairs and sequence lengths;
- multi-turn handoff remains stable enough to make the mechanism relevant to long agentic sessions rather than only one-shot cache conversion.

The fitting procedure is calibration rather than full model training: the paper uses 500 FineWeb-Edu sequences of 1,024 tokens and a closed-form ridge solve. The authors nevertheless used a large 8xH100 node for fitting, so fitting cost should not be assumed trivial on our hardware.

## Critical limitation for Flash-Next

The paper's experiments are deliberately limited to **dense full-attention** models. It explicitly leaves attention-recurrent hybrids that carry recurrent/SSM state alongside KV to future work.

That means the method is **not directly drop-in for Qwen3.8-Flash-Next**.

For Flash-Next, a useful model handoff would need to account for the complete live inference state, not merely conventional KV. In our terminology that includes at least the relevant recurrent/GDN state and any model-specific QSA/indexer/cache state required for exact continuation.

A KV-only conversion that leaves recurrent state stale, reconstructed incorrectly, or silently reinitialized could appear fast while changing the trajectory. Treat full-state continuity as a correctness prerequisite.

## Why this is still relevant to the project

The paper suggests a new future serving direction:

> **route live inference state between related model sizes instead of routing only prompts and paying target re-prefill on every escalation.**

That could eventually matter for a local agent stack where a smaller/cheaper family member handles routine work and a stronger family member takes over only when required. If state transfer works, model escalation could preserve the accumulated session without making the stronger model reread and re-prefill the whole prefix.

The most portable idea for current research is not the exact ridge formula; it is the evidence that **cross-layer state alignment may be sparse and learnable**. A target layer may be best reconstructed from a small set of source layers rather than the nominally corresponding layer.

That is worth testing for Flash-Next recurrent state before designing any production mapper.

## Lowest-cost Flash-Next research probe

Do **not** interrupt P69B13 for this.

When a compatible Flash-Next family pair and spare research window exist, the first probe should be diagnostic only:

1. run identical token sequences through both models;
2. capture corresponding conventional KV plus the recurrent/GDN state needed for continuation;
3. test simple per-layer and cross-layer linear probes before any learned nonlinear mapper;
4. measure whether a small top-k set of source layers explains target state better than same-layer mapping;
5. evaluate downstream-consumer similarity in addition to raw state reconstruction;
6. only if the state relationship is promising, build a handoff mapper and measure end-to-end continuation quality and latency.

For Flash-Next, candidate quality checks should be ordered roughly as:

- mapped-state reconstruction diagnostics;
- downstream GDN/projection/QSA consumer output similarity;
- next-token logit/trajectory divergence;
- exact continuation/output-hash checks where the runtime permits them;
- actual task/agent continuation quality;
- transfer wall time versus target re-prefill, including any cross-device movement.

The paper's attention-output-cosine result is the important warning: a mapper can look numerically good in state space while placing error in directions that matter disproportionately to the next computation.

## Distributed / dual-M1 implication

If a future source and target model run on different nodes, the economics become:

`map state + move mapped state over the link` versus `move/reuse prompt + target re-prefill`.

The paper's published latency result is on NVLink-class hardware and does not establish a TB4 win. Any dual-M1 version must include actual mapped-state transfer bytes, serialization/materialization cost, and TB4 wall time before claiming benefit.

This fits the repository's existing provenance rule: a mathematically valid mapper is not a serving win until the intended route is actually executed and measured on the target topology.

## P69 / current campaign decision

**No immediate P69 change.**

P69B12 remains frozen/promoted and P69B13 remains next from the existing measured high-leverage GDN/projection/downstream-tail evidence. Do not reopen P69B8, P69B9, or P69B10-C and do not redirect the exact-Q8 verifier campaign toward cross-model state transfer.

This is a future architecture seam for local serving / model escalation, not a current verifier optimization.

## Carry-forward statement

> **Cross-model family handoff may be able to transfer live inference state instead of re-prefilling, but Flash-Next requires full hybrid-state continuity. Probe cross-layer linear structure first, judge mappings by downstream computation rather than reconstruction alone, and require exact target-topology end-to-end evidence before promotion.**
