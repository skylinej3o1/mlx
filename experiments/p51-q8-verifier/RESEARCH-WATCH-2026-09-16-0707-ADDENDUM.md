# Research watch addendum — DS4 #1062 backfill

## Why this addendum exists

DS4 PR #1062 was created at `2026-09-16 10:07:55 UTC`, so it belonged to the completed `2026-09-16 04:31:59–11:07:39 UTC` research window. The previous pass captured several of its underlying commits but did not promote the PR-level benchmark summary or the long-context sweep. This note repairs that omission as **RECOVERED OLDER EVIDENCE**.

This addendum does **not** move the current hard freshness boundary, which remains `2026-09-16 16:46:32 UTC` after the later 12:46 ET watch.

## Source

- `antirez/ds4` PR #1062: **Qwen3.8 Flash Next: batched decode and MTP across sessions on Metal (16 streams: 203 tok/s aggregate), single stream +8%**
- Machine: Apple **M5 Max 128 GB**
- Model: `ds4flash.gguf`, Qwen3.8-Flash-Next **Q4**, 69.7 GiB resident
- Branch: `qwen3.8-flash-next-batched`, compared with upstream main `9139e2a`
- Long-context sweep: `speed-bench/m5_max_ctx_sweep.md`
- Harness: `speed-bench/session_concurrency_bench`

## The evidence that matters for our project

The PR headline emphasizes aggregate concurrency, but the most relevant transfer evidence for our dual-M1 B1 target is the **single-stream long-context sweep**.

### Branch, C=1

| active context | plain TG | batched-MTP TG |
|---:|---:|---:|
| 4K | 54.3 | 59.1 |
| 8K | 53.4 | 58.3 |
| 16K | 50.9 | 61.0 |
| 32K | 51.0 | 54.5 |
| 64K | 51.9 | 53.7 |
| **128K** | **51.5** | **53.1** |
| **256K** | **48.2** | **48.5** |

### Upstream main, C=1

| active context | plain TG | MTP TG |
|---:|---:|---:|
| 4K | 50.2 | 50.5 |
| 8K | 47.8 | 50.6 |
| 16K | 50.9 | 54.0 |
| 32K | 49.6 | 50.4 |
| 64K | 51.0 | 50.6 |
| **128K** | **48.4** | **51.2** |
| **256K** | **46.4** | **44.6** |

The branch therefore demonstrates an absolute **~50+ tok/s class single-stream long-context receipt on stronger Apple hardware** at 128K, and high-40s even at 256K.

The branch-vs-main delta at 128K is much weaker evidence than the absolute rate. The authors report **5–15% thermal drift** over the three-hour sweep; one 128K C=1 MTP cell measured **63.9 tok/s** and later **53.1 tok/s** an hour apart. Therefore the 48.4→51.5 plain and 51.2→53.1 MTP differences are inside the disclosed drift envelope and must not be treated as clean causal speedups.

## Concurrency / batched-MTP evidence

At 4K the PR reports:
- C=16 plain aggregate: about **203 tok/s**;
- C=8 plain aggregate: **133 tok/s**;
- C=8 batched MTP prose: **149 tok/s**;
- C=16 batched MTP code: **214 tok/s**;
- C=1 plain: **50.2→54.3 tok/s** vs upstream main;
- C=1 MTP: **59–66 tok/s prose / 78–84 tok/s code** in the headline experiments.

This is primarily **server/concurrency evidence**, not a B1 planning receipt. The implementation shares weight-only work across rows while keeping recurrent state, attention caches and n-gram history session-local. Batched MTP uses a per-cycle economics policy: draft only when measured acceptance and speculative-cycle cost beat the plain-cycle alternative.

## Transfer interpretation for dual M1 Max / TB4

This is **not** an exact active-topology result:
- M5 Max != M1 Max;
- one 128 GB machine != two 64 GB machines over TB4;
- Q4 != our eventual quality-preserving ~5.x-BPW lane;
- DS4 runtime != our eventual tuned MLX/bridge implementation;
- no TB4 stage-transfer cost exists in this receipt.

But it materially strengthens the mechanism case behind the existing Flash target. A stronger single Apple SoC sustaining roughly **51–53 tok/s at 128K** means the model itself is not intrinsically forced into the 20–30 tok/s range by long-context QSA/recurrent work. Our dual-M1 plan still has to recover that capability despite heavier weights and distributed/TB4 overhead.

### Planning consequence

**No canonical target change.** Keep:
- **40 tok/s sustained TG @ ~128K active context** on 2x M1 Max 64 GB / TB4;
- **400 tok/s cold PP**.

Qualitatively, #1062 increases confidence that **40 @ 128K is a credible success floor rather than an aggressive fantasy**, and supports retaining the existing noncanonical 45–50 stretch / 50–60 upside bands if the major distributed-MTP, QSA, verifier and scheduling mechanisms stack. It does **not** justify promoting 50+ as the dual-M1 expectation.

## Implementation rules promoted from #1062

1. Benchmark **context x concurrency**, not only a single context or C=1.
2. Shared transients must resize/rebind safely as context grows; otherwise later sessions can silently fall back to multi-GiB private arenas.
3. Decode and prefill need different kernel-routing thresholds; a decode-friendly FP32/k-split tile can regress prefill.
4. Speculation policy should price the **whole batch cycle**, not each row independently, because tile boundaries make marginal row cost highly non-linear.
5. Preserve exact-sampling fallback for sampled requests when greedy speculative acceptance changes random-draw semantics.
6. Treat small throughput deltas below the measured thermal-noise envelope as inconclusive unless paired/interleaved A/B evidence exists.
7. Long-context absolute receipts are useful transfer evidence even when the causal branch delta is noisy; keep those evidence classes separate.

## Freshness bookkeeping

This PR is backfilled into the 07:07 ET watch chain as recovered older evidence. It **does not advance** the post-12:46-ET hard source-freshness boundary of `2026-09-16 16:46:32 UTC`.
