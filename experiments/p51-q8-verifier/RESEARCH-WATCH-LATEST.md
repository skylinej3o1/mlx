# External runtime watch — 2026-09-15 14:32 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-15 16:44:45 UTC` through the user-request cutoff `2026-09-15 18:32:30 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, comment-only activity, or a later merge of older measurements.

## Executive result

No exact active-topology receipt appeared for any canonical target. No target moves.

The strongest fresh items in this short window are:

1. **vLLM #57053** — adaptive speculative depth was selected by the scheduler but not propagated into the actual autoregressive proposer; a K=3 policy still executed five draft forwards until fixed. This is directly relevant to our Lightning adaptive-depth contract.
2. **vLLM #57048** — Kimi-K3 DSpark single-stream launch-overhead work shows a useful split strategy: defer tiny residual work across a safe boundary and graph-capture only the graph-safe speculative tail while leaving the awkward projection GEMM eager. Synthetic short-run step time improved 13.8%; output throughput improved 4.4%.
3. **vLLM #57047** — a fused AWQ W4A16 dequant+GEMM path on RTX 4090 eliminates full FP16 weight materialization and produces very large wins in the batch-invariant path, while exposing another correctness rule: incidental input contiguity must not silently switch arithmetic implementations.
4. **vLLM #57042** — one-stage and two-stage custom all-reduce can differ bitwise because the rank accumulation order changes across the payload-size crossover. This is important distributed-correctness context, but the concrete rank-order issue does not directly bite our two-rank PP2 path.
5. **vLLM #57050** — an independent fresh report reproduces the same Mamba physical-vs-logical admission failure already promoted from #57000, now with a 1M-token Kimi-K3 request on 8x B300. It strengthens confidence in that rule but adds no distinct mechanism.

mlx-serve and oMLX had no main-branch commits inside this hard window. ds4-dfm-rs likewise had no main-branch commit in-window. llama.cpp had a fresh merge of older OpenCL MTP/MoE work, but the underlying work predates the hard boundary, so merge time is not treated as new evidence.

## Promoted — vLLM #57053: scheduler-selected speculative K must reach the actual proposer

Source created: `2026-09-15 18:30:01 UTC`.

MRV2 dynamic speculative decoding computed a runtime `num_spec_tokens_to_schedule`, but autoregressive speculators did not receive it. The proposer therefore fell back to its configured maximum depth.

Fresh synthetic reproducer:
- configured max K = 5;
- dynamic schedule selects K = 3;
- before: proposer executes **5** forwards;
- after: proposer executes **3** forwards.

Measured synthetic proposer wall time across batch sizes 1..48:

| batch | buggy | fixed | speedup |
|---:|---:|---:|---:|
| 1 | 0.151 ms | 0.115 ms | 1.306x |
| 2 | 0.148 | 0.115 | 1.286x |
| 4 | 0.149 | 0.115 | 1.298x |
| 8 | 0.148 | 0.115 | 1.282x |
| 16 | 0.151 | 0.115 | 1.315x |
| 32 | 0.150 | 0.114 | 1.306x |
| 48 | 0.149 | 0.115 | 1.287x |

The benchmark replaces the real draft model with a matmul and is not an E2E throughput receipt. The correctness issue is still real: unused draft forwards create needless work and stale draft-token state.

### Promoted rule for our distributed Lightning MTP

Adaptive depth is not a policy/config field; it is **execution identity**.

For every verifier cycle, record and certify:

`policy-selected K -> authoritative K -> broadcast/sync K -> proposer-executed K -> verifier row count -> committed accepted prefix`.

A distributed implementation must prove that every stage/rank and every graph/eager path sees the same current K. If a scheduler changes K but an old graph, proposer, or remote PP stage still executes max-K work, the optimization is fictitious and state may become stale.

This strengthens the existing rule that any speculative policy changing tensor shape, budget, boundaries, or collectives becomes distributed consensus state.

## Promoted transfer — vLLM #57048: graph only the safe speculative tail

Source created: `2026-09-15 17:55:21 UTC`.

Kimi-K3 DSpark, ROCm MI355X TP8, concurrency 1, depth 6, synthetic acceptance length 3.75.

Two ideas are combined:
- defer low-token MLP residual adds into the next safe attention/residual boundary, with exact eager fallback and a 16-token ceiling;
- graph-capture only the graph-safe DSpark context norm/RoPE/cache tail while keeping the AITER projection GEMM eager.

Fresh short A/B:
- step: **35.34 -> 30.48 ms (-13.8%)**;
- p90 ITL: **31.97 -> 27.56 ms (-13.8%)**;
- mean TPOT: **9.40 -> 8.30 ms (-11.7%)**;
- output throughput: **+4.4%**.

A longer 3600-second AgentX A/B and accuracy confirmation are still pending, so the above is preliminary scoped evidence.

### Transfer to Apple Lightning MTP

Promote the decomposition strategy, not the ROCm numbers:

- Do not force an entire speculative cycle into one graph merely for graph coverage.
- Identify the subset with stable shapes/pointers/lifetimes and capture that tail.
- Keep shape-sensitive or backend-hostile projections eager if graphing them adds restrictions or loses a better kernel.
- Deferred residual/add work is valid only across a mathematically safe boundary with an exact eager fallback.
- Measure launch count / host gaps / GPU busy span separately from acceptance/content variance.

This is especially relevant if our dual-M1 verifier has a stable norm/RoPE/state-commit tail but dynamic proposal/head geometry.

## Promoted RTX transfer — vLLM #57047: fuse dequantization into GEMM and pin route identity

Source created: `2026-09-15 17:39:46 UTC`.

Hardware: RTX 4090 / SM89.
Model validation checkpoint: Qwen3-4B-AWQ.
Path: batch-invariant AWQ Triton W4A16, asymmetric int4, group size 128.

The old batch-invariant route fully dequantized int4 weights to FP16 and then called matmul. The new kernel unpacks/dequantizes inside the GEMM and never materializes the full FP16 weight tensor.

ABBA measurements report:

| workload | wall reduction | throughput gain | peak-memory reduction |
|---|---:|---:|---:|
| decode B1 | 54.6% | 120.3% | 157.1 MiB |
| decode B8 | 55.6% | 125.3% | 144.0 MiB |
| decode B32 | 51.3% | 105.5% | 111.5 MiB |
| long-context B1 | 31.2% | 45.3% | 111.5 MiB |
| mixed B8 | 34.7% | 53.1% | 110.8 MiB |

All output-token hashes matched across the compared processes/arms. Full GSM8K moved 82.87% -> 82.94%, effectively parity at this granularity.

Important qualification: this compares against the slow **batch-invariant dequant+matmul fallback**, not against every normal optimized AWQ path. Do not project a 2x gain onto our RTX5070Ti target.

Two correctness bugs found during development are directly transferable:
1. non-exact K/group geometry could pass integer-division validation and read past scales/qzeros;
2. gating the fused route on incidental input contiguity let the same layer silently switch between two numerically different arithmetic paths.

### Transfer to the 5070 Ti / Qwen3.8-27B lane

- Audit whether any 27B AWQ/quant route materializes a large dequantized tensor before GEMM.
- Physical quant execution should stay packed through the hot GEMM when a fused route exists.
- Route selection must be a function of stable tensor geometry/capability, not incidental contiguity/history.
- If contiguity is required, normalize it explicitly before dispatch and bill the copy.
- Exact divisibility/padding/tail validation is part of kernel admission.
- First-use JIT remains separate from steady-state cost; this fresh kernel currently lacks warmup registration.

This strengthens, but does not move, the RTX 120/250 planning target.

## Fresh distributed-correctness context — vLLM #57042

Source created: `2026-09-15 16:49:27 UTC`.

vLLM's one-stage custom all-reduce sums ranks in absolute rank order. Its two-stage path rotates the starting rank by partition owner. Both accumulate in FP32, but floating-point addition order changes the result bits. The algorithm choice itself changes at a message-size threshold.

CPU emulation with adversarial four-rank inputs shows roughly 62% of elements differing between the two accumulation orders for fp16/bf16/fp32 input sets. The required four-rank GPU differential had **not yet been run**, so this remains correctness-mechanism evidence, not completed GPU validation.

For two ranks, the rotation only swaps `a+b` to `b+a`, so this exact mechanism does not directly threaten our two-M1 PP2 topology. Still retain the general rule:

- payload-size or route thresholds that switch collective algorithms may also switch reduction order;
- if exact distributed reproducibility matters, collective algorithm identity and rank accumulation order belong in the execution receipt.

Do not promote this into an active PP2 blocker.

## Fresh corroboration — vLLM #57050: 1M hybrid request admission stall

Source created: `2026-09-15 18:14:29 UTC`.

A separate fresh Kimi-K3 reproduction on **8x B300** with a 1,048,576 max context reports the same class already captured from #57000: after loading the prefix from external Mooncake storage, a 1M-length request can fail Mamba admission and wedge the system because `get_num_blocks_to_allocate` overestimates physical blocks.

A new unit test compares estimated blocks against actual allocated blocks; main fails and the branch passes.

This is useful independent corroboration of the **physical allocator == admission ruler** principle, but it adds no new optimization mechanism, so #57000 remains the canonical explanation in our stack.

## Fresh but not promoted

- vLLM #57041: infers HiSparse attention config from the HiSparse connector. Configuration simplification only.
- vLLM #57043/#57044/#57045/#57046/#57051/#57054: docs, CI, parser, or UX changes with no active inference-target mechanism.
- vLLM #57049: interesting design draft for restoring a final imported HiSparse page to avoid tail prefill on the decode side; **no GPU/E2E performance measurement yet**, so keep as watch-only until measured.
- llama.cpp main commit `9f31776c...` at `18:21:05 UTC` merges older OpenCL MoE routing-count work for speculative decoding/MTP. The underlying PR predates this hard window, so merge time does not refresh its evidence.
- mlx-serve main: no commits in-window.
- oMLX main: no commits in-window.
- ds4-dfm-rs main: no commits in-window.

## External/community screen

Current oMLX benchmark pages visible today include Qwen3.8-27B-MLX-8bit on an M1 Ultra 64-GPU-core / 128 GB machine at roughly **18.6 TG / 178.6 PP at 1K** and **18.2 TG / 168.1 PP at 4K** on oMLX 0.6.4. This is stronger hardware than one M1 Max, short context, and the page exposes the date only at day granularity, not a source timestamp inside this hard window.

Therefore it is background calibration only and is **not promoted** or used to move the M1-Max 25/110 target.

No source-time-qualified fresh exact dual-M1 Flash receipt, one-M1-Max64 Qwen3.8-27B canonical-quant receipt, controlled RTX5070Ti16 target receipt, or dual-M1 DS4-0731 receipt appeared.

## Target status

Canonical targets remain unchanged:

- Qwen3.8-Flash-Next dual M1 Max64/TB4: **40 tok/s @ ~128K active context**, **400 tok/s cold PP**.
- Qwen3.8-27B one M1 Max64: **25 tok/s**, **110 tok/s native/exact-runtime cold PP**.
- Qwen3.8-27B RTX5070Ti16 + host RAM: **120 tok/s**, **250 tok/s cold PP**.
- DS4-0731 dual M1 Max64/TB4: **15 tok/s**, **180 tok/s cold PP**.

No P69 reorder/reopen.

## Planning impact

Add or strengthen these rows in the implementation/tuning ruler:

1. `selected_K -> executed_K` provenance on every speculative cycle and every rank/stage.
2. Graph only the stable speculative subgraph; do not require all-or-nothing graph capture.
3. Measure deferred residual/add fusion across mathematically safe boundaries with exact eager fallback.
4. Audit packed-quant execution for dequantized-weight materialization before GEMM, especially on the RTX lane.
5. Normalize required tensor layout explicitly; never let incidental contiguity silently select a numerically different kernel.
6. Exact quant group/tail divisibility belongs in kernel admission.
7. Collective algorithm and reduction order belong in distributed execution identity when exact reproducibility is required.
8. Keep physical recurrent-state admission equality tests after external cache restore / checkpoint transition.

This pass improves confidence that there is still significant avoidable speculative/runtime overhead to mine, but it provides no exact dual-M1 calibration and therefore does not justify moving 40/400.

## New hard freshness boundary

`2026-09-15 18:32:30 UTC`
