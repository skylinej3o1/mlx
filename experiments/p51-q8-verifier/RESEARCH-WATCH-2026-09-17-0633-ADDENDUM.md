# RECOVERED OLDER EVIDENCE addendum — 2026-09-17 06:33 ET watch

## Why this addendum exists

During the next search pass, four high-value vLLM PRs were found whose substantive creation timestamps fall **before** the prior hard boundary `2026-09-17 10:33:10 UTC` but were not captured in `RESEARCH-WATCH-2026-09-17-0633.md`.

They are backfilled here under the standing timestamp rule. They improve the evidence record but **do not refresh or move the current source-freshness boundary**.

Recovered items:
- vLLM #57317 — created `2026-09-17 07:37:02 UTC`;
- vLLM #57318 — created `2026-09-17 07:37:51 UTC`;
- vLLM #57319 — created `2026-09-17 07:44:01 UTC`;
- vLLM #57329 — created `2026-09-17 08:30:26 UTC`.

No canonical target moves from this recovered evidence.

---

## vLLM #57317 — a bounded ring must not inherit unbounded logical-position addressing

GLM-5.3-Flash's Kpool tail is a fixed-size per-request ring. Its correct address is effectively `position % kpool`. A generic KV slot-mapping kernel instead derives storage from monotonically increasing logical position / block size.

The Kpool tail spec inherited the generic `uses_slot_mapping` behavior even though its physical storage is ring-shaped. At sufficiently long context the generic index therefore grew beyond the fixed tail allocation and caused an out-of-bounds memory access.

The fix declines the generic mapper and uses the Kpool-specific ring mapping from the metadata builder.

Validation included 16 successful requests with **500,000 input tokens each** (8,000,000 total input tokens), with zero failed requests after the fix. GSM8K remained essentially unchanged within the reported run noise.

### Promoted rule

Physical cache topology owns address arithmetic. A bounded ring/circular side state must explicitly reject any generic mapper whose index is derived from unbounded logical position.

For our long-context state qualification, every cache/state family should declare its physical indexing contract:

`append-only / block-table / ring / pooled-block + tail / checkpointed recurrent / owner-local sidecar`.

Do not infer one from a superclass or logical token span.

---

## vLLM #57318 — narrow GDN verifier projection is a shape-specific kernel problem

On `Qwen3.8-27B-NVFP4`, RTX 5090, batch size 1 with three speculative tokens, the GDN `in_proj_ba` projection has shape approximately `[M,5120] x [5120,96]` in BF16. The stock cuBLAS heuristic chose a poor kernel in the exact M=2–4 speculative regime.

Measured end-to-end cell:
- projection per call: **27.2 us -> 3.40 us**;
- projection total: **112.4 ms -> 14.0 ms**;
- decode: **1494.3 ms -> 1397.7 ms (-6.5%)**.

A GB10 measurement showed the same projection moving about 34.0 -> 6.2 us.

The sweep is especially informative because the fast route is **not monotonic**. It wins for narrow N and M=2–4, while at wider N or larger M the FlashInfer route can become slower than cuBLAS. The proposed default N ceiling is therefore measured rather than derived.

The PR also calls out a compile hazard: a normal Python shape branch inside a no-guards trace can freeze whichever branch the one tracing pass saw, often prefill, and then silently use it for decode. The dynamic decision therefore belongs in a runtime/custom op or equivalent execution-time dispatch.

### Promoted rules

- Kernel route identity for verifier/GDN projections includes `(M,N,K, device/backend, quant state)`.
- Speculation depth changes M and can move a projection across a kernel crossover.
- A microkernel that wins at verifier width 3 need not win at B1 ordinary decode or at batched widths.
- Dynamic route predicates must remain dynamic after compilation; certify the **executed** branch, not the source-level condition.
- This PR changed split-K reduction order and accuracy evaluation was still outstanding at the captured source state, so treat the 6.5% as performance/mechanism evidence, not fully certified quality evidence.

This directly supports keeping GDN/projection work high in the P69/Flash optimization queue, but it is CUDA transfer evidence rather than an Apple rate receipt.

---

## vLLM #57319 — a 3x component win can still be zero end-to-end

This PR fuses the final Gumbel sampler `argmax` plus token-ID gather into one Triton reduction.

At Qwen3.8-27B's 248,320-token vocabulary, the graph-executed final reduction improved roughly **2.46–3.50x** across the tested row counts. For example at one row the final reduction was 4.43 -> 1.55 us and the full FP32 sampler 8.05 -> 4.89 us.

The serving result is the important calibration. Across client concurrency 1/4/8/16/32 on an H100 PCIe, median throughput changes ranged from **-0.65% to +0.14%**. The PR explicitly concludes that it does not establish a model-level throughput gain.

Correctness evidence was strong at the changed component: 1,544/1,544 live rows matched when both samplers received the exact same logits, alongside dedicated tie/NaN/precision/CUDA-graph tests.

### Promoted rule

Component speedup is not target evidence. For every micro-optimization record both:

`component time share before` and `end-to-end ruler delta after`.

A 3x kernel result on a low-share tail can be operationally irrelevant, and scheduler/model drift can easily exceed the expected total gain. This is a clean empirical reason to keep our target-moving standard tied to end-to-end exact-topology receipts.

---

## vLLM #57329 — export internal recurrent checkpoints from an existing full prefill instead of splitting the model forward

Mamba2 align-mode prefix caching needs a recurrent state at a cacheable boundary. Previously the scheduler split prefill so a full model forward ended exactly at that boundary. That guarantees the state exists, but pays an extra model forward through attention, MoE/routing and collectives.

The new design observes that the Mamba scan already materializes state at logical chunk ends. The request metadata is split at the intended checkpoint position so that position becomes a logical scan boundary, and the checkpoint is indexed out of the intermediate state array while the overall model prefill remains one forward.

For an 8K prompt on the tested Nemotron-H/Mamba2 hybrid, the conceptual change is:

`6288-token full forward + 1712-token full forward`

becoming

`8000-token full forward + one scan exposing the internal checkpoint`.

Measured TTFT:
- C1: **97.26 -> 84.24 ms (-13.4%)**;
- C4: **239.21 -> 197.31 ms (-17.5%)**;
- C16: **590.56 -> 496.14 ms (-16.0%)**.

Prompt throughput changed only about +0.1–0.6%, and request latency about -0.3–0.6%, consistent with removing fixed extra-forward overhead rather than reducing the amount of token math.

The 20-shot GSM8K route exercised prefix checkpoints and reported 0.87 with ordinary execution, MTP, and ReplaySSM in the listed tests.

### Strong correctness lesson

The PR centralizes the predicate that decides whether a recurrent checkpoint is exportable. Scheduler, cache manager and attention metadata builder must all use the same rule. If one layer allocates/hashes a checkpoint that another layer never writes, the prefix cache can later serve **uninitialized recurrent state**.

### Promoted rules

- If a scan/forward already materializes intermediate recurrent state, prefer exporting the exact required checkpoint from that execution over splitting the entire model forward solely to make the checkpoint terminal.
- Checkpoint eligibility is a **shared consensus predicate** across scheduler, cache ownership and backend metadata.
- “Allocated/hashable checkpoint” and “physically written checkpoint” must be distinct states until the backend confirms the write.
- Internal prefill segmentation used to expose checkpoint state is a semantic identity and must be tested independently from the outer full-model forward count.

---

## Boundary status

These sources all predate `2026-09-17 10:33:10 UTC`; they are recovered evidence only.

The subsequent current watch advances the hard boundary independently to its own user-request cutoff.