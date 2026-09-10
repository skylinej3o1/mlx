# Runtime research watch — 2026-09-10 00:16 ET

## Scope / evidence class

This is a **BACKFILL / SOURCE-CORRECTION** pass over the full user-supplied capture of the r/oMLX thread:

- `Qwen3.8-Flash-Next-oQ4e-mtp with oMLX 0.6.4 is an absolute wonder !`
- https://www.reddit.com/r/oMLX/comments/1wa34po/

The earlier research passes captured overlapping Flash-Next mechanisms but did **not** exhaust this thread. The receipts below are therefore newly incorporated into the project evidence chain, but they are **not fresh post-cutoff discoveries**.

Starting canonical head: `23c9940ef62f7a50f90bd61d00e0cd99ac9c0a11`.

**Hard source-freshness boundary remains 2026-09-10 00:38:49 UTC.** Do not advance it to this backfill commit time; the interval after 00:38:49 UTC has not yet been searched.

Evidence discipline used here:

- **BACKFILL / USER RECEIPT** = self-reported real-hardware result with useful workload/config detail, but not independently standardized or reproduced by us.
- **BACKFILL / TRANSFER** = useful runtime/hardware mechanism evidence from a non-target lane.
- **SCREENED** = interesting discussion that is too underspecified to promote.

No row in `RESEARCH-TARGETS.md` moves from this pass.

---

## BACKFILL / USER RECEIPT — M4 Max 128 GB, oMLX Flash-Next at usable long context

The thread OP reports:

- M4 Max 128 GB;
- `Jundot/Qwen3.8-Flash-Next-oQ4e-mtp`;
- oMLX 0.6.4;
- `max_context_window = 120000`;
- Lightning/native MTP enabled;
- SSD N-gram offload in the described daily setup;
- Pi as the harness;
- `reasoning_effort = low`;
- TurboQuant KV off, dFlash off, SpecPrefill off;
- **stable 30+ tok/s generation** in use.

The OP later clarifies that the practical workload is Kubernetes/cluster plumbing rather than a broad modern application-coding benchmark. Preserve that workload provenance when citing the receipt.

**Interpretation:** this is substantially more useful than a short `tg128`/`pp512` style number because it is a real harness at a configured 120K context ceiling. It is still stronger-hardware transfer evidence, not a dual-M1 receipt.

---

## BACKFILL / USER RECEIPT — second M4 Max 128 GB warm-session report

A separate M4 Max 128 GB user reports switching from Qwen3.6-35B-A3B BF16 to Jundot Flash-Next oQ4e-MTP and seeing, after the context is KV-cached and important/frequent PLE rows are warm:

- approximately **500 tok/s prefill**;
- approximately **40 tok/s generation**;
- MTP enabled;
- reasoning set to medium with an 8192-token thinking budget.

The comment does **not** provide a standardized active-context denominator for the ~40 TG number, so do not relabel it as an exact 120K or 128K receipt.

**Interpretation:** reinforces that Flash-Next can reach a ~40-TG-class interactive experience on newer Apple silicon when the cache/PLE path is healthy, but does not numerically transfer to M1 PP2.

---

## BACKFILL / USER RECEIPT — M5 Max daily-driver long-context behavior

A M5 Max user running the same Jundot oQ4e-MTP model with Pi reports:

- **>30 tok/s generation up to ~150K context**;
- no loops, breaks or tool-call errors in their oMLX daily-driver experience;
- memory pressure appearing near ~200K context, sometimes requiring autocompaction;
- big-repo analysis/design use;
- they had largely stopped using DS4 and Qwen3.8-27B for that workload.

This is anecdotal behavioral evidence, not a controlled benchmark, but it is directly useful for the **usable-context** lane.

**Promotion:** long-context qualification should report not only raw TG but also tool-call integrity, loop/runaway incidence, compaction threshold and session-memory pressure.

---

## BACKFILL / USER RECEIPT — MTPLX is a high-value speed control, not yet a trusted correctness baseline

The thread contains multiple reports of very large MTPLX throughput gains:

- one M5 Max user: **~50-100% higher TG** than oMLX on Flash-Next;
- another M5 Max 128 GB user: approximately **70-75 tok/s** on a dynamic-4 MTPLX setup;
- an M2 Ultra 128 GB user: oMLX around **17-20 tok/s at high context** versus MTPLX around **30 tok/s**.

However, the M2 Ultra user reports **loops and hallucinations** on MTPLX and stayed with slower oMLX; another user says they saw similar reliability problems on earlier MTPLX Qwen 3.6/3.8-27B and regarded Jundot/oMLX quants as more reliable.

**Promotion:** MTPLX should be treated as a **frontier speed/control implementation** whose fast paths are worth mining. Do not adopt its TG as a production target receipt without output-quality, tool-call, loop/runaway, MTP-acceptance and state-lifecycle certification.

Desired future comparison:

`same weights / same prompt / same sampling / same context / same MTP depth -> oMLX vs MTPLX -> TG + PP + accepted/cycle + output hash/semantic task result + tool-call/state correctness`.

---

## BACKFILL / USER RECEIPT — 64 GB viability exists, but exact M1 attribution is unresolved

One commenter states that the Flash-Next setup **runs on their 64 GB Max at 12-20 tok/s**.

The exact Max generation is not supplied in that comment. Another commenter specifically says they still cannot get it to run on an **M1 Max**.

**Classification:** useful 64-GB-class viability evidence only.

**Do not promote to the exact M1 Max target lane.** Hardware generation, quant/runtime config, context, memory policy and execution path are unresolved.

---

## BACKFILL / USER RECEIPT — oQ5e memory premium and hard-prompt robustness

A M5 Max 128 GB user built and published `GBP-DE/Qwen3.8-Flash-Next-oQ5e-mtp` and reports under broadly similar SSD-N-gram-offload conditions:

- oQ4e: approximately **93 GB total system memory**;
- oQ5e: approximately **102-103 GB total system memory**.

These are whole-system numbers including macOS and other applications, not model-only residency.

The same user reports that normal/simple prompts are often indistinguishable between Q4 and Q5, but harder/stability-tail tasks separate them:

- in an 8-person / 24-constraint logic puzzle, oQ5e completed the puzzle correctly while oQ4e produced duplicate assignments and constraint violations;
- in a longer multi-stage task, oQ5e completed in about 520 s while oQ4e was still reasoning/outputting around 772 s and did not finish the required answer;
- the user had observed severe generation/reasoning loops occasionally on oQ4e but not yet on their oQ5e testing;
- they explicitly stop short of claiming universal superiority and note cases where both are equally correct and one difficult case where Q4 was faster.

**Interpretation:** supporting evidence for a Q5-class **robustness/headroom** advantage in difficult tails, not standardized proof that Q5 is universally smarter.

**Blazer consequence:** the optimization objective should emphasize hard-constraint stability, long-task completion, loop/runaway rate and task wall-clock in addition to perplexity/logit drift. The desired custom 5.x-bit recipe is not simply “more bits everywhere”; it should spend precision where it removes difficult-tail failure modes.

---

## BACKFILL / USER RECEIPT — PLE / N-gram SSD offload should be a policy, not a permanent assumption

A M5 Max 128 GB user reports that with Jundot oQ4e-MTP they can disable SSD N-gram offload, gain speed, and still reach approximately **128K context**.

This does not transfer directly to two 64-GB M1 nodes, but it invalidates a simplistic design assumption that Flash-Next PLE/N-gram must always be SSD-backed.

**Promotion:** qualify at least these PLE modes on the target topology:

1. fully resident when memory permits;
2. SSD-backed sparse gather;
3. hot-row resident + SSD cold rows;
4. PP-stage-local placement/ownership where applicable.

Record TG, cold PP, warm PP, page-fault/I/O traffic, memory headroom, context ceiling and TB4 traffic. The winning policy may change with quant, context and MTP buffers.

---

## BACKFILL / USER RECEIPT — runtime implementation can dominate nominal model/quant choice

A user reports moving the same Flash-Next model/hardware from GGUF `UD_Q4_K_XL` to oMLX oQ4 and seeing roughly:

- GGUF: **10-32 tok/s**;
- oMLX: **35-70 tok/s sustained**, with higher intermittent bursts.

The report is not controlled enough for target calibration, but the magnitude is a useful warning against treating checkpoint BPW as the main performance variable.

**Promotion:** runtime route, graph shape, kernel selection, cache policy and MTP implementation are first-class benchmark identity.

---

## BACKFILL / TRANSFER — mlx-serve PR370 / newer M5 fast-path ceiling

A M5 Max 128 GB user reports a Q4-Q8 mixed Flash-Next build on `mlx-serve` PR370, attributing the fast prefill to a M5-specific NAX optimization, with:

- approximately **52 tok/s sustained decode** over runs totaling about 50K output tokens;
- approximately **1200 tok/s prefill**;
- real Xcode/Claude-Code-style app-building loops including tests, screenshots and bug fixing.

This is a newer-silicon/runtime ceiling receipt, not an M1 numeric transfer.

**Use:** architecture/kernel ceiling evidence only; preserve the long-run output-token denominator because it is much more useful than a short burst.

---

## BACKFILL / USER RECEIPT — M5 Max full-context GGUF comparison versus 27B

A M5 Max 128 GB user reports:

- Qwen3.8-Flash-Next `UD_Q4_K_XL` at full context: approximately **38+ tok/s**;
- Qwen3.8-27B `UD_Q6_K_XL`: approximately **38-40 tok/s**;
- Flash produced the preferred UI/UX and harness result;
- 27B was preferred for their chat-interface use.

The exact active-token denominator and full config are missing, so this stays USER RECEIPT / transfer evidence.

**Promotion:** model evaluation must keep **harness/agent task quality** separate from generic chat preference; same TG does not imply same utility.

---

## BACKFILL / USER RECEIPT — context headroom is part of quant utility

An M2 Studio Ultra 192 GB user reports choosing oQ4e despite available higher precision because it leaves enough memory headroom to run about `2^18` (~262K) context and values that capacity increasingly.

**Promotion:** final quant utility is multi-objective: quality-tail robustness + TG + PP + MTP acceptance + memory + usable context + allocator stability. Do not rank quants on quality or BPW alone.

---

## BACKFILL / USER RECEIPT — tokens-to-solution can reverse a TG ranking

A commenter reports preferring a 2-4-bit mixed DeepSeek-V4-Flash-Vision-Exp build for coding/non-coding tasks even though it was roughly **50% slower** in raw generation than Flash-Next, because Flash-Next used many more tokens to reach similar conclusions and total task time was worse.

This is subjective and not a controlled cross-model benchmark, but the metric lesson is durable.

**Promotion:** add **tokens-to-solution / task wall-clock** to agent evaluation. A faster decoder can lose the real task if it reasons longer, loops, emits more repair turns or needs more tool iterations.

---

# Consequences for the dual-M1 Flash-Next plan

No target movement. Keep PP2/layer ownership primary and TP2 as control.

Add/strengthen these qualification requirements:

1. report **usable-context TG** at 32K / 64K / ~128K / capacity edge, not only short-context decode;
2. report cold versus warm KV/PLE state explicitly;
3. make PLE residency/offload policy an A/B dimension rather than an assumption;
4. retain oQ4e as speed/control and promote oQ5e-class weights as the main quality-shape candidate for tuning;
5. use MTPLX as a speed/frontier control and mine its fast paths, but require behavioral parity before promotion;
6. measure loop/runaway rate, tool-call integrity, long-task completion and tokens-to-solution;
7. keep context headroom and allocator stability in the quant objective;
8. preserve runtime/kernel provenance because same model/nominal quant can differ dramatically across engines;
9. exact 64-GB-class anecdotes do **not** substitute for exact M1 Max 64 / TB4 PP2 receipts.

### Important target interpretation

The canonical target file remains authoritative:

- Flash-Next dual-M1 working target = **40 tok/s B1 short/medium**;
- around 128K, the current ladder remains **20 / 25 / 30 / 35 tok/s at the recorded confidence levels**;
- cold PP working target remains **400 tok/s**.

The thread strengthens the plausibility of good long-context interactive performance on Apple silicon, but it does **not** justify silently redefining the dual-M1 40-TG target as an already-supported 128K rate.

---

# Other lanes

## Single M1 Max64 Qwen3.8-27B

No target movement. P69B12 remains frozen/promoted; P69B13 remains next from the existing measured GDN/projection/downstream-tail profiling only.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement.

## Dual-M1 DS4-0731

No target movement. The thread's subjective DS4-vs-Flash task-efficiency comparison is evaluation-method evidence only.

---

# Standing decisions strengthened by this backfill

- Real agent usability must be measured at realistic active context, not inferred from tiny benchmark cells.
- Warm KV/PLE state is benchmark provenance.
- PLE residency policy is hardware/memory/context dependent.
- Q5's likely value is difficult-tail robustness/headroom more than obvious normal-chat gains.
- MTPLX is a valuable speed-control implementation but requires correctness/quality certification before adoption.
- Runtime implementation can dominate nominal BPW/model choice.
- Tokens-to-solution and task wall-clock belong beside TG/PP.
- The future custom 5.x-bit / Blazer objective remains: **task quality + tail robustness + TG + PP + MTP acceptance + memory + usable context + PP balance**.
- Cross-hardware user receipts do not move exact dual-M1 targets without exact target-topology reproduction.
- **No canonical target movement.**
- **P69 remains isolated.**
