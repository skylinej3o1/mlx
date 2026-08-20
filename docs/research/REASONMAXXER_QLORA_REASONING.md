# MXFORGE reasoning adapters — QLoRA / ReasonMaxxer-style branch selection

Status: **CORE / promoted research workstream**

Primary paper: https://arxiv.org/html/2605.06241v2

This workstream asks whether a strong frozen base model such as Qwen3.8-27B can be made materially more reliable at coding/reasoning through a very small adapter rather than expensive full-model RL/post-training.

## Working thesis

The ReasonMaxxer paper argues that a large fraction of RLVR reasoning gains may come from changing a small number of high-entropy branch decisions rather than creating wholly new capabilities. The paper reports that RL-induced token reranking is sparse, often concentrated at uncertain decision points, and that small LoRA adapters can recover much of the measured reasoning improvement on its math benchmarks.

For MXFORGE, treat the broad claim conservatively:

> **If the frozen model already sometimes solves a task, a small adapter may be able to raise pass@1 by steering it toward successful latent trajectories.**

Do **not** assume that QLoRA/LoRA can create capabilities that the frozen model never demonstrates, or that math results automatically transfer to coding agents.

## Why coding is an attractive test domain

Coding provides unusually strong automatic outcome signals:

- compile / type-check success
- unit and integration tests
- benchmark gates
- patch application
- lint/static-analysis gates
- tool-call correctness
- regression-suite pass/fail
- task-specific acceptance checks

This lets us generate many trajectories from the same frozen target and label success/failure without relying on subjective reward models.

## First target

Start with **Qwen3.8-27B frozen** and train small adapters rather than altering the base weights.

Candidate adapter ladder:

- rank 8
- rank 16
- rank 32
- rank 64 only if smaller ranks saturate

Candidate target modules:

1. Q/K/V/O attention projections only
2. Q/K/V/O + selected MLP projections
3. broader adapter placement only if the small surface underfits

Use QLoRA where needed for training-memory efficiency: base weights frozen/quantized for forward/backward storage, adapter weights trained in higher precision.

## Training-data pipeline

For each automatically verifiable coding task:

1. sample multiple independent trajectories from the frozen model;
2. execute the resulting tool/code actions in a sandbox;
3. label trajectories using objective task outcomes;
4. retain tasks where the base model demonstrates both successes and failures whenever possible;
5. record token logprobs / entropy around key decisions if the runtime exposes them;
6. preserve full trajectory metadata so failed experiments remain reproducible.

The useful regime is the **edge of competence**: tasks where the base model can succeed but does so inconsistently.

## Objectives to compare

### A. Plain positive SFT / QLoRA

Train only on successful trajectories and ask whether simple imitation raises pass@1.

### B. Success-vs-failure contrastive tuning

For the same task, increase probability of successful choices and suppress corresponding failed choices where alignment between trajectories is meaningful.

### C. ReasonMaxxer-style entropy targeting

Concentrate the update on high-entropy / high-uncertainty decision tokens and anchor non-targeted behavior toward the frozen base model.

The objective is **not** maximum training loss reduction. It is higher downstream task success with minimal behavioral drift.

## Evaluation protocol

Use a held-out coding suite and compare the frozen model against every adapter on identical tasks and inference settings.

Primary metrics:

- pass@1
- pass@k
- task completion rate
- regression-test rate
- tool-call validity
- total generated tokens
- wall-clock task time
- number of tool actions / retries
- unrelated-task regression score

Secondary diagnostics:

- entropy distribution at changed decisions
- base-model rank of adapter-preferred tokens
- KL divergence from frozen model
- adapter parameter count / disk size
- inference overhead

A candidate is only useful if it raises task success without unacceptable degradation on unrelated/general tasks.

## Initial proof-of-concept

Do **not** start by trying to build a universal "Qwen3.8 reasoning edition."

Start with roughly hundreds of verifiable coding tasks, multiple rollouts per task, and rank-16 / rank-32 adapters. Compare:

1. frozen baseline
2. positive-only QLoRA
3. contrastive success/failure QLoRA
4. entropy-targeted / ReasonMaxxer-style candidate

If there is no meaningful held-out pass@1 gain, stop or redesign before scaling the dataset.

If there is a clear gain, increase task diversity and adapter capacity gradually.

## Runtime integration

Reasoning adapters can become another MXFORGE policy dimension.

Potential future adapter set:

- stock / no adapter
- coding-high
- debugging-high
- architecture/review-high
- domain-specific adapters only where independently justified

The request inspector can choose independently:

- **behavior adapter**
- reasoning-effort mode
- topology (TP / PP)
- speculation mode / depth
- KV / context policy

Example:

```text
incoming hard repo-debug task
        ↓
request classifier
        ↓
behavior: debugging-high QLoRA
reasoning: high
compute: TP + MTP2
context policy: current best certified band
        ↓
execute
```

Adapter selection should depend on current content/workload, not session history or whether context was recently compacted.

## Interaction with custom reasoning effort

Qwen3.8's stock effort ladder is low / medium / xhigh. MXFORGE may add a calibrated **high** prompt/template level between medium and xhigh.

Keep reasoning effort and behavioral adapters separate in experiments:

- prompt-only high
- adapter + medium
- adapter + high
- adapter + xhigh

This prevents attributing gains from a stronger reasoning instruction to the adapter itself.

## Interaction with MTP/speculative tuning

An adapter can change token distributions and therefore speculative acceptance. After any adapter is promoted:

- remeasure MTP acceptance
- remeasure DSpark/DFlash2 acceptance where applicable
- remeasure effective tok/s
- check whether draft-depth thresholds move

Do not assume a behavioral gain is performance-neutral.

## Hardware plan

Use the RTX 5070 Ti / available CUDA hardware for the first training experiments where practical, and certify inference behavior on the actual M1 Max target runtime.

The two-M1 setup remains the deployment/performance laboratory; the training host can differ as long as adapter outputs are portable and the final target-model behavior is certified on Metal.

## Success criteria

Promote reasoning adapters beyond research only if a held-out coding suite shows:

1. statistically meaningful pass@1/task-success improvement;
2. acceptable general-task regression;
3. negligible or justified inference overhead;
4. reproducible gains across multiple seeds/task subsets;
5. compatibility with the chosen quant/runtime;
6. speculative acceptance re-certified after adapter application.

## Priority

High-value **post-core-runtime** experiment. It is cheap enough to prototype early, but it should not interrupt the immediate M1 kernel/MTP/DeepSeek tuning ladder.

If the first rank-16/32 proof-of-concept works, this becomes a major MXFORGE branch because it extends the project from optimizing **how fast the model executes** to cheaply optimizing **which reasoning branches it selects** while keeping the foundation model frozen.
