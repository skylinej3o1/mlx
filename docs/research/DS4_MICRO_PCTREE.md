# DeepSeek V4 Flash 0731 — Micro-PCTree for expensive TP verification

Status: **CORE / promoted experiment**

This note captures an MXFORGE adaptation of **Parent-Conditioned Drafting Trees (PCTree)** for the existing DeepSeek V4 Flash 0731 two-M1-Max tensor-parallel target plus RTX 5070 Ti speculative sidecar.

The upstream PCTree idea is useful, but the default datacenter-oriented tree sizes are not the right objective for the Thunderbolt 4 target topology. MXFORGE should port the **parent-conditioned branching principle**, not blindly port the published branch factors or node counts.

Primary references:

- Reddit llama.cpp fork discussion: https://www.reddit.com/r/LocalLLaMA/comments/1vunqoz/llamacpp_dspark_pc_tree_fork_up_to_3295_faster/
- PCTree paper: https://arxiv.org/abs/2608.02123

## Core observation

Linear speculative drafting has a rejection-cascade problem:

```text
A -> B -> C -> D -> E

if B is rejected:
A is useful
B is rejected
C/D/E become useless speculative work
```

PCTree spends additional candidate rows near uncertain parent decisions so an early rejection does not necessarily destroy the entire suffix:

```text
        B -> C -> D
       /
A ----
       \
        B' -> C' -> D'
```

For a conventional large GPU, the natural implementation can verify a wide tree in one target pass. For MXFORGE the target is distributed across two M1 Max machines over Thunderbolt 4, and verifier width is expensive because additional rows can amplify collective, routing, gating, and synchronization cost.

Therefore the MXFORGE objective is not maximum tree acceptance. It is:

> **maximum increase in committed target-verified tokens per incremental TP verifier row and per incremental verifier millisecond.**

Equivalent whole-system objective:

```text
(drafter time + sidecar transport + TP verify time + commit overhead)
-------------------------------------------------------------------
                 committed target-verified tokens
```

Minimize that quantity for each workload/context class.

## Important interpretation of the public result

Do **not** record the Reddit headline as a free `+29.5%` MXFORGE gain.

The llama.cpp fork report shows that the best tree is workload- and verifier-cost-dependent. In the reported RTX 5090 comparison, a larger tree could produce higher acceptance while still losing throughput to a smaller tree because target verification became more expensive. That is direct validation of the MXFORGE rule that **acceptance is a secondary metric**.

Likewise, the paper's larger headline gains are evidence that parent-conditioned branching can help, not a prediction for DeepSeek V4 Flash 0731 over two M1 Max nodes.

## Why k=2 matters most for MXFORGE

The paper's branching-factor sweep suggests that moving from a linear path (`k=1`) to a very small amount of branching (`k=2`) captured most of the acceptance/speed benefit in the tested environment, while larger branch factors added little.

That is unusually compatible with the Thunderbolt topology.

Initial MXFORGE hypothesis:

> **one alternate parent near the root may recover most rejection-cascade loss without making the distributed target batch wide enough to trigger pathological TP verification cost.**

This should be tested, not assumed.

## Micro-PCTree

Define **Micro-PCTree** as a deliberately tiny, hardware-cost-aware parent-conditioned tree designed for expensive distributed verification.

Initial search region:

- branch factor: `k=2` first
- total verified tree nodes: `N=3..8`
- branch primarily near the root / first uncertain decision
- no large `N=16/32` sweep until the small-tree verifier curve proves that wider batches remain economical

Candidate shapes:

### Root hedge

```text
        B -> C
       /
A ----
       \
        B'
```

### Root hedge with two short suffixes

```text
        B  -> C
       /
A ----
       \
        B' -> C'
```

### Asymmetric root hedge

```text
        B -> C -> D
       /
A ----
       \
        B'
```

The asymmetric form may be especially attractive: spend one expensive extra verifier row to protect the highest-risk parent transition, then continue linearly along the best branch.

## 5070 Ti sidecar fit

The current heterogeneous design is:

```text
M1 Max #1 ----\
                +-- DS4 0731 Q2/Q4 TP target + KV + verifier
M1 Max #2 ----/
        ^
        | tiny feature / candidate protocol
        v
RTX 5070 Ti 16GB
        +-- compact DSpark / future DFlash2 / custom drafter
```

Micro-PCTree fits this topology well because the additional tree construction should happen on the **5070 Ti**, where draft-side compute is cheap relative to target verification.

The 5070 should perform:

- DSpark backbone work
- parent-conditioned / Markov-head candidate scoring
- tiny-tree construction
- confidence / topology metadata generation

The Macs should perform only authoritative target verification and commit.

Network traffic should contain compact feature/candidate/tree metadata rather than target activations or expert tensors. Bandwidth is expected to be a minor term; round-trip latency and target-side TP synchronization are the terms to measure.

## Verifier-first integration

Micro-PCTree should not precede verifier work. It should consume the same specialized small-M verifier infrastructure being built for MTP/DSpark.

Target widths to optimize and certify:

- M=2
- M=3
- M=4
- M=5
- M=6
- then M=7/8 only if the curve remains favorable

The verifier needs to support both:

1. linear speculative rows;
2. tiny parent-conditioned tree masks / ancestor relationships.

Then compare at equal target-row budgets:

| Target row budget | Linear candidate | Micro-PCTree candidate |
|---:|---|---|
| 2 | DSpark M2 | root hedge only if representable economically |
| 3 | DSpark M3 | k2 / N3 |
| 4 | DSpark M4 | k2 / N4 |
| 5 | DSpark M5 | k2 / N5 |
| 6 | DSpark M6 | k2 / N6 |
| 7-8 | optional | k2 / N7-8 |

This prevents a tree from appearing faster merely because it consumes a much larger target batch.

## Required measurements

For every prompt replay and tree shape log:

- context length
- workload class
- DSpark / drafter wall time
- sidecar network round-trip time
- number of target rows verified
- TP verifier wall time
- collective / wire time inside verification
- local compute time
- accepted/committed tokens
- longest accepted path length
- acceptance probability by tree depth
- rejection depth histogram
- effective tok/s
- **ms per committed target-verified token**
- memory / transient workspace
- exact-output correctness / hash where applicable

Also log the counterfactual reason for tree value where possible:

- linear path would have failed at depth X
- alternate parent recovered Y additional committed tokens
- incremental verifier rows cost Z ms

That gives a direct estimate of whether the hedge paid for itself.

## Initial experiment ladder

1. Preserve the current ~17.5 tok/s plain TP target baseline.
2. Finish the first clean M=2..8 TP verifier latency curve.
3. Bring up the compact 0731 DSpark on the RTX 5070 Ti sidecar.
4. Certify **linear M2 and M3 DSpark** first.
5. Add parent-conditioned candidate generation without changing the target verifier.
6. Add **k=2 / N=3** target verification.
7. Sweep `N=3..8` on identical replayed prompts.
8. Test root-only and asymmetric branching.
9. Compare tree versus linear speculation at equal row budgets and equal contexts.
10. Add scheduler selection only after each path is individually certified.

Do not begin with a 16- or 32-node tree.

## Workload hypothesis

Micro-PCTree is most likely to win where:

- linear DSpark acceptance is already useful;
- early-parent uncertainty frequently destroys otherwise-good suffixes;
- code/copy/structured output creates predictable continuation after the correct parent is selected;
- the extra one or two verifier rows are much cheaper than a second full distributed target cycle.

It may lose on:

- creative prose;
- reasoning with low draft predictability;
- contexts where TP M>1 cost becomes sharply superlinear;
- very high contexts where memory/workspace or attention cost dominates;
- workloads where linear M2 already captures almost all useful speculation.

## Adaptive scheduler integration

Micro-PCTree becomes another candidate in the DS4 phase diagram rather than a global default.

Candidate speculation policies should include:

- target only
- small native/0731-specific MTP
- linear DSpark M2/M3/...
- **Micro-PCTree k2/N3..N8**
- future DFlash2 / DDTree-like paths when genuinely compatible with 0731
- lookup/context-copy drafting where useful

Scheduler inputs should include:

- current context
- workload/content class
- recent rejection depth
- recent linear DSpark acceptance
- recent benefit from alternate-parent recovery
- free memory
- TP verifier latency curve
- sidecar RTT
- expected output length

The scheduler should select the policy minimizing expected whole-system wall time per committed verified token, with hysteresis to avoid oscillating between nearly equal tree shapes.

## Relationship to the broader interconnect attack

Micro-PCTree does not replace the Thunderbolt optimization program. Its value rises as the verifier gets cheaper.

Continue attacking:

- communication-aware TP partitioning
- expert locality / placement
- smaller or compressed exchanges where correctness permits
- async collectives
- double buffering
- compute/communication overlap
- fused verification spans
- fewer synchronization points
- topology-aware M=2..8 kernels

The ideal outcome is complementary:

> **5070 makes branching cheap; M1 verifier work makes tiny-tree target verification cheap; parent-conditioned branching reduces wasted expensive target cycles.**

## Promotion rule

Promote Micro-PCTree into the default DS4 speculative scheduler only if paired certification shows a whole-system gain over the best linear DSpark/MTP candidate at the same context/workload, with no target-output correctness regression.

Do not promote based on acceptance rate alone.
