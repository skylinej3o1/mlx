# External runtime research watch — 2026-09-05 04:00 ET

Previous canonical head: `e74f3dc6683be61e1084fde59e294228351410e4`

Starting freshness boundary: **2026-09-04 23:35:16 UTC**.

## Verdict

This pass found material Flash-serving correctness and prefill-architecture evidence, but **no new
exact physical receipt from the target dual-M1, single-M1 or RTX 5070 Ti rigs**. Therefore the
canonical planning centers and confidence ladders in `RESEARCH-TARGETS.md` do not move.

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

The new findings change **what must be certified and which mechanisms deserve A/Bs**, not the
calibrated exact-rig performance distribution.

---

## Fresh / material

### vLLM #55430 — Qwen3.8-Flash-Next QSA tile-union prefill reuses neighboring selections

Fresh Qwen3.8-Flash-Next work on SM121/DGX Spark exploits the high overlap between neighboring QSA
query rows. Rather than gather the same selected compressed blocks separately for each row, the
kernel forms a union for a small row tile, gathers each selected block once, then applies per-row
membership masks inside the online softmax.

Reported end-to-end measurements on the author's GB10 / TP1 setup:

- 7,503-token TTFT: **2.58/2.57 s vs 2.65/2.65 s**, about **2.8% faster**;
- 29,263-token TTFT: **10.13/10.09 s vs 10.28/10.28 s**, about **1.7% faster**;
- two concurrent ~8K requests: **5.20/5.19 s vs 5.31/5.31 s**, about **2.2% faster**;
- concurrent ~30K + ~8K: **12.61/12.55 s vs 12.80/12.79 s**, about **1.6% faster**.

The standalone sparse-attention kernel reportedly gains much more on large chunks; the full-model
benefit is low-single-digit because QSA is only part of prefill. Tile boundaries are request-aware,
which matters for multi-request correctness.

**Classification: mechanism transfer only.** This does not move the dual-M1 `400 PP` center. It does
strengthen an Apple experiment: after the exact sparse-QSA baseline, test whether neighboring
query rows can share selected-block gather work without changing row semantics, especially on
large cold prompts and simultaneous requests.

### llama.cpp #28243 — Apple MTP divergence is now isolated to batch-width-dependent `MUL_MAT`

A fresh correction materially changes the Apple speculative-decoding diagnosis. The investigation
reports that tested Metal `FLASH_ATTN_EXT` paths were bitwise batch-invariant, while `MUL_MAT` was
**not**. The first differing verify width tracked source dispatch thresholds for several tensor
formats:

- q6_K: first divergence at width **4**;
- q8_0: width **2**;
- iq4_nl: width **2**;
- f16: width **2**;
- at wider widths where dispatch falls to `mul_mm`, differences can become substantially larger.

That is structurally important for MTP: autoregressive target evaluation uses width 1, while a
verifier evaluates roughly `n_max + 1` positions together. Speculation can therefore silently move
large numbers of target matmuls onto a different numerical kernel even when recurrent-state commit
logic itself is correct.

The corrected M5 Pro64 matrix withdraws the earlier large speed claim. The only reported
greedy-exact tested speculative cell was **FA off / f16 / n-max 2**, at about **0.919x** baseline.
The only faster cell was about **1.024x**, but it was not greedy-exact. FA-on variants were not exact
and did not beat baseline materially.

**Classification: strong correctness transfer, not an M1 rate ruler.** Before any Flash MTP lane is
promoted, add an op-level **batch-width numerical-invariance gate** over the actual Metal matmul
formats and verifier widths, plus long greedy continuation comparisons. “Same logits/output on one
short prompt” is not enough.

### DS4 #952 — prefill benchmark interpretation tightened; actual work must be logged

A fresh follow-up corrected an earlier hypothesis about AProjQ4 prefill variation. The longer prompt
file was repetition and both runs consumed the same prefix at the 8K frontier; file length therefore
did not explain the difference. Remaining variables include the compared engine commit and whether
generation was requested after prefill.

More importantly, the benchmark harness exposes that a displayed context frontier and the number of
**new tokens actually prefetched** are not always the same. Example rows from the investigation:

- ctx 8192 -> `prefill_tokens=8192`;
- ctx 16384 -> `prefill_tokens=8192`;
- ctx 32768 -> `prefill_tokens=16384`;
- ctx 65536 -> `prefill_tokens=32768`.

This does not invalidate the existing AProjQ4 decode evidence. It changes our certification hygiene:
all PP receipts must record both **context frontier and actual prefill-token work**, and comparative
cold-PP tests should hold prompt-token work fixed and isolate generation from prefill whenever
possible.

**Classification: benchmark-methodology update only.** No DS4 target movement.

---

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact dual-M1 TG result, completed long-context exact receipt
  or post-boundary M1-Max Flash follow-up surfaced.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on the exact 2x M1 Max64 / TB4
  topology surfaced.
- **RTX 5070 Ti 27B:** the direct `aipruner/qwen3.8-3bit-test-in-16GB-GPU` repo remains
  `pushed_at=2026-08-20T19:16:50Z`.
- **Apple 27B:** `ARahim3/mlx-dspark` remains `pushed_at=2026-09-01T10:54:45Z`; the Layr challenge
  repo remains `pushed_at=2026-08-29T07:05:19Z`.
- **Core MLX GDN work:** #4409 is useful recurrent-kernel evidence but its last material update was
  before this pass's hard cutoff and was already captured in the 19:30 note.

---

# Consequences by lane

## Dual-M1 Flash-Next

Updated qualification order:

1. pin/certify llama.cpp `v0.4.0` / exact tagged commit on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. PLE residency/page-cache/direct-read policy A/B;
4. sparse-QSA wide-prefill A/B;
5. **QSA neighboring-row selection/gather reuse A/B** after the sparse-QSA baseline;
6. pooled QSA-prefix retention / rollback correctness;
7. **Metal `MUL_MAT` batch-width invariance gate** across target quant types and planned verify widths;
8. singleton MTP depth/acceptance A/B with pre-verify snapshot + exact recurrent commit/replay;
9. multi-request pure-prefill state isolation with deliberately mismatched request lengths and
   serial references;
10. only then adversarial parallel-MTP slot isolation and MTP concurrency >1;
11. compiled-decode B2/B4;
12. workload-derived cache matching / exact prefix-session reuse;
13. combine passing mechanisms, then long-prefill-arrives-during-decode multi-agent stress.

The new QSA result raises confidence in the **optimization surface**, not in a particular exact-M1
rate. The MTP update makes correctness certification stricter rather than making speculation more
likely to be enabled by default.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

No target or topology change. Keep PP2/layer ownership primary and TP2 as control; AProjQ4 remains the
primary serving candidate with Q8 control.

Add to every PP certification row:

- context frontier;
- actual `prefill_tokens` performed;
- whether generation was requested in the same run;
- commit/build identity and model artifact identity.

Use fixed-work cold-PP comparisons before attributing a rate change to a kernel or quant choice.
Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No target change. The Metal matmul batch-width result is relevant if this lane uses batched verifier
execution, but it does not alter P69. **P69B12 remains frozen/promoted; P69B13 remains next from the
existing profiling only.**

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change and no new exact-5070 speed receipt. Existing qualification order remains: linked
CUDA-runtime provenance; ubatch/prompt-shape stability; fully resident Q3_K_XL + native MTP; draft
cache net-memory A/B; DFlash control; small-N Blackwell verify; MTP-head quant; GSQ-RCO quality /
context controls.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing architecture decisions after this pass

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- Stable llama.cpp `v0.4.0` remains the reproducible first Flash baseline candidate; it does not
  imply optimized Flash throughput.
- Stage-local recurrent/GDN/QSA/expert state remains preferred when residency permits.
- **QSA selection/gather reuse across neighboring query rows is now an explicit experimental Apple
  prefill lane**, not a forecast input.
- **MTP exactness includes batch-width numerical invariance of the target matmuls.** Correct recurrent
  snapshot/commit semantics alone are insufficient when verifier batching selects another Metal
  kernel path.
- Coherent text is not an exactness proof. Verify state, logits/greedy continuation, acceptance by
  position and serial-vs-batched behavior.
- Multi-request pure prefill remains a dedicated Flash correctness gate before concurrent MTP.
- **PP throughput is only comparable when the amount of actual prefill work is explicit.** Log
  `prefill_tokens`, context frontier and generation coupling separately.
- Physical cache-page size and prefix-match granularity should remain independently tunable.
- Prefix/session reuse remains a separate latency objective from cold PP.
- P69 exact verifier work remains isolated from external serving/runtime research.
- Stronger-chip percentages, alternate runtimes and microbenchmarks do not move exact-machine targets
  by themselves.

The detailed target ladders and target-change rules remain centralized in `RESEARCH-TARGETS.md`.
