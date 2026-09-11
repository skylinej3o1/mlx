# Runtime Research Watch — 2026-09-11 00:26 ET

Scope: fresh external-runtime pass after `RESEARCH-WATCH-2026-09-10-1928.md`, plus verification that the repository-only target-definition correction is already canonical.

Starting branch head: `42ffba783a5f958005e0fea9ab8aaaafaa0d190c`.

Starting hard source-freshness boundary: **2026-09-10 23:28:08 UTC**.

End-of-search boundary for this pass: **2026-09-11 04:26:56 UTC**.

The external research lanes remain:

1. Qwen3.8-Flash-Next on the planned **2x M1 Max 64 GB / TB4** cluster — PP2/layer ownership primary, TP2 control, QSA/PLE/GDN/MTP/cache/state ownership, long-context agent use and eventual Q5-class / custom ~5.x-BPW Blazer work.
2. Qwen3.8-27B on **one M1 Max 64 GB** — exact/native serving and portable kernel evidence only; P69 remains isolated.
3. Qwen3.8-27B on **RTX 5070 Ti 16 GB + 64 GB host** — fully-resident speed lane and separate capacity lane.
4. DeepSeek-V4-Flash-0731 / DS4 on **2x M1 Max 64 GB / TB4** — distributed control/architecture lane.

Evidence discipline remains unchanged: measured target receipt, transfer/mechanism evidence, user receipt, A/B and planning target are separate facts. Source execution/publication timestamp controls freshness; repository write time does not.

---

# Canonical Flash target — verified, not changed by this pass

`RESEARCH-TARGETS.md` already contains the 2026-09-10 target-definition correction:

> **Qwen3.8-Flash-Next, quality-preserving Q5-class / eventual ~5.x-BPW weights, PP2 on 2x M1 Max 64 GB over TB4, ~128K active context: ~40 tok/s sustained TG, with ~400 tok/s realistic cold PP.**

The September 4 short/medium 30/35/40/45/50 ladder is secondary bring-up calibration only. The old ~128K 20/25/30/35 probability ladder is historical evidence calibration, not the project target.

This pass does **not** move the headline target or assign a new exact confidence to 40 @ ~128K. There is still no sustained physical receipt on the exact dual-M1-Max64/TB4 topology.

---

# Executive delta

## 1. FRESH / MATERIAL UPDATE — oMLX #3553 adds strong long-context Flash optimization evidence and new machine-exclusive Apple A/Bs

Source: https://github.com/jundot/omlx/pull/3553

PR head: `a04d2408183c130d24a968ed74732260eb55d0be` (`Rascal/omlx`, open).

The PR itself predates the freshness boundary, so its M5 Max body is an **UPDATE / stronger incorporated mechanism record**, not newly executed target-lane evidence. Two comments are genuinely post-cutoff:

- M3 Ultra 512 GB machine-exclusive A/B comment: **2026-09-11 02:46:46 UTC**.
- Three-content-shape follow-up: **2026-09-11 03:39:11 UTC**.

### M5 Max 128 GB long-context cycle decomposition — UPDATE / transfer, not M1 numeric transfer

Model: `Qwen3.8-Flash-Next-oQ4e-mtp`, SSD PLE, 512 generated tokens, greedy unless noted. The branch combines six independent levers: indexed selected-K/V attention, NAX indexer scores, fused GDN MTP verify rows, grouped quantized verify projections, parked-head priming and narrow gathered-QSA windows.

At pinned MTP depth 3, the body reports:

| Context | main client TG | branch client TG | main cycle ms | branch cycle ms |
|---:|---:|---:|---:|---:|
| 16K | 70.7 | 68.9 | 37.87 | 37.43 |
| 65K | 61.7 | 74.0 | 40.70 | 37.18 |
| 136K | 55.8 | 71.9 | 46.43 | 40.50 |
| 210K | 48.0 | 59.5 | 48.89 | 40.96 |

The headline TG deltas are **not clean kernel-speed multipliers** because tolerance-level QSA/indexer kernels can flip near-tie selections, fork the continuation and change acceptance. The PR explicitly separates this from cycle cost.

The more portable equal-acceptance / bit-exact decomposition is:

| Context | main ms/cycle | bit-exact subset | all six | equal-acceptance throughput: bit-exact | tolerance on top |
|---:|---:|---:|---:|---:|---:|
| 16K | 37.54 | 37.11 (-1.1%) | 37.11 (-1.1%) | +1.2% | +0.0% |
| 65K | 40.88 | 38.58 (-5.6%) | 36.84 (-9.9%) | +6.0% | +4.7% |
| 136K | 46.26 | 42.05 (-9.1%) | 40.76 (-11.9%) | +10.0% | +3.2% |
| 210K | 48.74 | 42.73 (-12.3%) | 40.76 (-16.4%) | +14.1% | +4.8% |

**Promotion:** whenever an optimization can change selector scores, top-k sets or continuation text, compare **per-cycle cost at equal acceptance / same execution work** separately from client TG. Client TG on a different continuation is still useful production evidence, but it is not a pure kernel multiplier.

### Bit-exact portable levers to mine

1. **Fused GDN verify rows (1..8 rows).** Fuses conv, SiLU, q/k RMS norm/scales, `g`, `beta`, next conv state and gated RMS norm for the small-M MTP verify shape.
2. **Grouped quantized verify projections (2..8 rows).** Group by identical `(bits, group_size)` signature. Single-row grouping was measured negative, so do not generalize a verify-row win to ordinary B1 decode.
3. **Narrow gathered QSA windows.** The MTP head's committed fold uses 2..8 rows; once the prefix is long, those narrow windows should take the gathered sparse path rather than masked-dense attention.
4. **Parked MTP head priming.** When adaptive speculation parks, retain/fold the draft-head state during plain decode so the next probe does not re-enter cold at long context.

### Recurrent exactness lesson — precise math semantics are part of kernel identity

The fused-GDN work found that prebuilt `mx.sigmoid` uses a precise exponential while JIT/Metal compiled paths could use a fast exponential. One BF16 gate input (`b=-6.84375`) was enough to shift recurrent state by an FP32 ulp on rare cycles and eventually fork greedy output roughly 160 tokens later. The fix uses precise `exp` for `beta` and verifies all finite BF16 gate inputs over real weights.

**Promotion:** for GDN/recurrent kernels, `same formula` is not sufficient provenance. Record the actual math implementation / compiler path for nonlinearities, and certify recurrent state plus long greedy continuation, not only immediate output tolerance.

### Measured-negative work should suppress duplicate exploration

On this M5 lane the PR reports:

- prompt-lookup n-gram drafts: **-10% to -20%**;
- block-sparse row-group prefill kernel: **3.6x slower**;
- MMA rewrite of GDN prefill recurrence: low leverage because recurrence is only about 6.5% of a prefill chunk.

These are transfer-only negatives, not universal M1 bans, but they lower priority unless the M1 profile shows a different bottleneck.

### FRESH physical M3 Ultra 512 GB A/B — machine residency as benchmark identity

Comment at **2026-09-11 02:46:46 UTC**:

- full machine-exclusive; all sibling engines stopped;
- greedy streaming;
- each arm physically tree-switched and engine-restarted;
- 5 rounds, 3 iterations per context tier, **120 requests** total;
- round-to-round variance <1%;
- baseline already includes #3520 + #3534.

Reported decode medians:

| Context | main | #3553 | delta |
|---:|---:|---:|---:|
| 1K | 164.1 | 164.5 | +0.2% |
| 16K | 86.5 | 86.9 | +0.5% |
| 32K | 82.2 | 82.8 | +0.7% |
| 64K | 80.6 | 81.5 | +1.1% |

The 64K arms do not overlap across rounds. This is **strong Apple transfer evidence**, not a dual-M1 rate receipt. It also reinforces the prior rule that **resident sibling engines / keepwarm state are benchmark provenance**.

### FRESH content-shape follow-up — one context length is not one workload

Comment at **2026-09-11 03:39:11 UTC** repeats the machine-exclusive tree-switched A/B across English prose, Rust code and CJK text.

Material observations:

- at the reported long-context comparison, branch absolute decode differs materially by content shape: prose **81.4 tok/s**, code **79.7**, CJK **66.4**;
- the one negative optimization delta across the 18 cells is 16K code: **83.9 -> 80.1 tok/s (-4.5%)**, non-overlapping across all three rounds;
- prose 64K remains positive at about **+1.4%** in the follow-up.

Do **not** promote the commenter's causal explanation for the CJK difference without a controlled mechanism test. Promote the empirical fact: token count alone does not fully identify a production workload because content shape can change routing, MTP acceptance and kernel economics.

**Qualification addition:** long-context Flash certification should include at least code, prose and a multilingual/CJK-shaped workload, recording acceptance/depth/controller state alongside TG.

### Consequence for the 40 @ ~128K thesis

This evidence **strengthens mechanism plausibility** for preserving high TG as context grows: the equal-acceptance benefit of the bit-exact subset rises from ~1% at 16K to ~10% at 136K and ~14% at 210K on the M5 test lane. It does **not** numerically transfer to M1 Max or prove the dual-M1 target. No target movement this pass.

---

## 2. FRESH / rMLX #558 — population counts can stay plausible while a scanner loses the actual round loop

Commit: `3ded8892c5f07918dd8a43aa09972fb744766cc4`
Timestamp: **2026-09-11 01:27:34 UTC**
Source: https://github.com/Pushkinist/rMLX/commit/3ded8892c5f07918dd8a43aa09972fb744766cc4

A bodiless trait `fn` declaration was treated as if it were waiting for the next `{`, so the scanner could consume the following function's body. One round loop was therefore lost from the sampling population, while the newly added entry filled its numerical slot; a plain count remained plausible.

The fix:

- terminates a bodiless declaration at its own semicolon, including multiline signatures/`where` clauses;
- shares that predicate across the signature scanners;
- requires an entry that forwards a `RoundCfg` to have a forwarded loop to enter;
- treats an entry-with-no-loop as a lost-population invariant violation;
- covers trait/impl methods as functions;
- keeps stated parser boundaries explicit and fails closed where ownership becomes ambiguous.

**Promotion:** provenance/correctness gates need **relational invariants between populations**, not only census totals. `lost X + gained Y = same count` is a real failure mode. For our PP2/MTP qualification, cross-check configured entries -> materialized loops/routes -> executed route rather than accepting matching counts alone.

---

## 3. FRESH / vLLM #56033 — heterogeneous PP completion must count no-op consumers before releasing shared state

Commit: `ce08bb5b3463fd423be90d5f22c2b41142834bf6`
Timestamp: **2026-09-11 02:57:19 UTC**
Source: https://github.com/vllm-project/vllm/commit/ce08bb5b3463fd423be90d5f22c2b41142834bf6

For heterogeneous producer/consumer PP sizes, a producer stage can have no overlapping layers with one consumer stage. That no-op pull still participates in completion. The fix:

- records remote PP size in transfer metadata;
- allows partial layer-region alignment for heterogeneous PP;
- multiplies completion accounting by the consumer PP fanout;
- retains source KV until **every consumer PP stage**, including a no-op stage, has completed.

The added P4/D2 test explicitly requires producer KV to survive until both D stages finish even though only one stage performs a physical transfer.

**Promotion:** PP completion is a topology/lifetime fact, not `bytes transferred > 0`. Stage ownership, no-op participation and release/retirement counts must be certified explicitly. For dual-M1 PP2, a stage that consumes no tensor in one transition can still own a completion dependency.

---

## 4. FRESH / vLLM #55239 — speculative verify rows belong to the ragged sparse-attention route when the kernel indexes per query token

Commit: `828f4f19b4d8ea6a97a047409a90b563d166002f`
Timestamp: **2026-09-11 01:13:14 UTC**
Source: https://github.com/vllm-project/vllm/commit/828f4f19b4d8ea6a97a047409a90b563d166002f

The GLM-5.3-Flash ROCm route had classified its sparse Triton path as plain-decode only. The kernel actually indexes metadata per query token, so multi-token MTP verification rows have the same route capability. Tests now cover 2-row and 6-row speculative verification as well as ordinary decode/prefill.

**Promotion:** sparse-attention eligibility should be derived from the actual kernel's per-query-row semantics, not a broad `decode vs verify` label. Our QSA route matrix must explicitly test MTP verify widths through the intended gathered/ragged sparse path rather than allowing verify to fall back merely because `max_query_len > 1`.

This is mechanism transfer only; no Apple numeric transfer.

---

## 5. FRESH / vLLM #49675 — deferred frees cannot be used as immediate preemption capacity

Commit: `84030bbe3d74d99bad477a3d2e37a973ccd8865c`
Timestamp: **2026-09-11 00:40:10 UTC**
Source: https://github.com/vllm-project/vllm/commit/84030bbe3d74d99bad477a3d2e37a973ccd8865c

Under overlapping batches / PP, KV blocks may be fenced behind in-flight output. Preempting such a request does not immediately free capacity. Repeatedly choosing victims whose blocks cannot yet be freed caused zero-progress preemption cascades.

The fix checks whether a victim's blocks **can actually be returned now** before using that preemption to satisfy allocation, and stops/retries after the fence when they cannot.

**Promotion:** admission/backpressure decisions must distinguish logical retirement from physically reusable memory/state. Under PP2 concurrency, `request preempted` or `state scheduled for free` is not equivalent to `capacity available now`.

---

## 6. FRESH / oMLX #3565 — cluster pairing recovery is durable-state correctness, not throughput

Commit: `48951154c06c5db408ee40ad6533c3a65ab061e7`
Timestamp: **2026-09-11 03:27:20 UTC**
Source: https://github.com/jundot/omlx/commit/48951154c06c5db408ee40ad6533c3a65ab061e7

Cluster v2 pairing now persists the join proof/session, survives a joining-server restart, distinguishes local cancellation from remote cleanup completion, retries retired requests and prevents delayed responses from resurrecting a cancelled join.

**Promotion:** useful operational hardening for eventual two-Mac serving, but no rate implication. Keep cluster control-plane generation/revision identity separate from model execution generation identity.

---

# SCREENED / no exact target-rate movement

- **llama.cpp main:** no commit after the 2026-09-10 23:28:08 UTC cutoff in the inspected history.
- **antirez/ds4 main:** no post-cutoff main commit; newest visible main activity remained September 8.
- **oMLX main:** the only post-cutoff mainline commit found is #3565 pairing recovery; no post-cutoff exact dual-M1 rate receipt.
- **rMLX:** #558 is correctness/provenance-gate work, not a production rate result.
- **vLLM:** fresh items are route/lifetime/scheduler transfer evidence; no exact Apple target rate.
- Broad exact-rig searches surfaced older/undated receipts or crawl-time rediscovery, not timestamp-qualified new target evidence.
- No new exact **2x M1 Max64/TB4 Flash-Next** sustained TG/PP receipt.
- No new exact **one M1 Max64 Qwen3.8-27B** canonical production receipt after the cutoff.
- No new exact **RTX 5070 Ti16 fully-resident Q3_K_XL/native-MTP** canonical speed-lane receipt after the cutoff.
- No new exact **2x M1 Max64/TB4 DS4-0731** sustained decode receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as concrete control.

Add/strengthen:

1. headline qualification stays **~40 TG at ~128K active context**, not short-context 40;
2. selected-K/V gathered QSA must cover ordinary B1 decode, target verify rows and MTP-head narrow committed folds where legal;
3. certify GDN fused verify rows at the actual MTP row widths and require reference-math semantics for recurrent nonlinearities;
4. grouped quantized projections are a verify-row candidate, not automatically a B1 decode candidate;
5. preserve MTP head state during parked periods and measure re-entry coldness/probe success;
6. separate cycle/kernel gain at equal acceptance from client TG when selector tolerances can fork continuation;
7. include code/prose/multilingual-CJK content shapes in the long-context matrix;
8. no-op PP stages still participate in completion/lifetime accounting;
9. logical preemption/deferred release does not equal immediately reusable state/memory;
10. keep machine-residency/sibling-engine state in benchmark provenance;
11. suppress low-priority duplicate work when a transfer lane has a strong measured negative unless M1 profiling shows a different bottleneck.

Safe serving remains **profitable singleton MTP + plain concurrent work** until the existing simultaneous B2/B3/B4 state/workspace/ownership gates are certified.

## Future Blazer / ~5.x BPW

#3553 strengthens several design rules:

- optimize the real **verify-row shapes**, not only single-row QMV;
- group projections only across identical quant signatures when the grouped route is independently profitable;
- keep sparse selected-row attention and quant packing compatible with narrow MTP folds;
- treat math-library/compiler semantics as part of the recurrent kernel format;
- judge tolerance-level sparse/index kernels by **task quality + acceptance + equal-work cycle cost + TG**, not TG alone.

## Single M1 Max64 Qwen3.8-27B

No target movement. P69 is untouched.

**P69B12 remains frozen/promoted; P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.**

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully resident Q3_K_XL/native-MTP remains the canonical speed lane; host-backed IQ4_XS long-context work remains a separate capacity lane.

## Dual-M1 DS4-0731

No target movement. No new exact dual-M1 rate receipt.

---

# Standing decisions strengthened this pass

- **40 TG @ ~128K** remains the actual Flash headline objective; this pass strengthens plausibility but does not prove it.
- Long-context optimizations can be nearly irrelevant at 16K yet material at 136K-210K; qualification must preserve context as part of cell identity.
- If an optimization changes continuation/acceptance, client TG and kernel/cycle gain are separate measurements.
- Recurrent exactness can depend on precise-vs-fast math-library semantics even when formulas look identical.
- Sparse attention must qualify the actual verify-row/narrow-window shapes, not only one-token decode.
- Content shape belongs in the workload descriptor; same token count can produce materially different serving economics.
- PP completion counts no-op participants if they own a lifetime dependency.
- Deferred release is not reusable capacity until the fence has completed.
- Cross-population provenance gates need relational invariants, not only matching counts.
- Machine-residency/sibling-engine state remains part of benchmark identity.
- Cross-runtime/cross-hardware mechanisms do not move exact-target rates without exact target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**