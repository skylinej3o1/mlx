# Project 51 primary-lane research watch — 2026-09-28 16:02 ET

**Freshness boundary entering this pass:** **2026-09-28 17:54:51 UTC**.  
**User cutoff:** **2026-09-28 20:02:08 UTC**.

## Decision

**No canonical speed-target change.**

Keep:
- dual-M1 Flash-Next: **40 TG @ genuinely filled ~128K / 400 cold PP / ~70% >=40**;
- single-M1 dense27B: **25 TG / ~110 PP**;
- dense RTX5070Ti CUDA-v2 ladder unchanged;
- Strata Flash-Next target ladders unchanged.

One target-definition refinement landed: **prefix reuse is not automatically physical prefix sharing.** A common prefix earns multi-agent memory-capacity credit only when several resident agents actually reference one shared immutable state image while holding independent private suffixes.

---

## NEW — Strata 0.1.20 pins the shared system/tool prefix for new chats

Release published **2026-09-28 17:59:33 UTC**.

PR #62 changes the existing single-branch conversation cache from FIFO to a pinned-root + LRU-leaf policy. The deepest checkpoint shared by the retained conversation chain stays resident while later checkpoints rotate.

Measured IQ3_XXS / RTX4070 example:
- 16,747-token shared system prompt;
- old new-chat path: **14,898 ms** prompt read;
- pinned-root path: **1,176 ms**;
- repeat: **1,181 ms**;
- `--prompt-cache 1` fallback: **14,948 ms**.

That is **12.7x lower first-message prompt-read time** in the measured new-chat case. The PR estimates a 30K shared prefix saves roughly 25–30 s at ~1,100 PP. All ten A/B answers were token-identical; decode throughput was unchanged.

Important limitation: Strata still has **one live KV arena / one branch of history at a time**. This is checkpoint reuse, not true simultaneous physical sharing of one prefix across multiple resident agent suffixes.

### P51 consequence

- Promote a **pinned immutable system/tools/repo root** as the first shared-prefix optimization.
- Do not count its bytes once across N resident agents until Project 51 implements refcounted read-only attention KV + recurrent/GDN + QSA/indexer state with independent suffix ownership/rollback.
- TARGETS now states this explicitly.

---

## NEW — Strata 0.1.20 makes the default PCIe policy topology-aware

PR #44 measures pinned-host -> device bandwidth once at startup using four 256-MiB DMA reads, then scales the default `pcie_frac` down on links slower than the PCIe4 x16 reference.

Example physical x8 receipt:
- RTX5060Ti 16 GB / PCIe4 x8;
- measured H2D: **14.1 GB/s**;
- default `pcie_frac`: **0.55 -> 0.30**.

x16-class links retain the existing default. Explicit `--pcie-frac` and `--calibrate` still override the automatic guess. No credible E2E speed number was claimed for this PR.

### P51 consequence

Keep PCIe/TB bandwidth as a measured scheduler input. This independently reinforces our rule that expert/state movement policy must derive from actual link throughput, not card identity.

---

## NEW — Strata monitor exposes per-request decode expert-cache hit rate

PR #69 records decode-only expert-cache hits/lookups, excluding prompt-prefill lookups, and surfaces the hit rate in the request monitor.

### P51 consequence

For every Strata 5070-Ti TG receipt, record **decode expert hit rate** alongside TG, acceptance, PCIe bandwidth and cache slots. A speed number without hit-rate provenance is no longer enough to compare expert-residency configurations.

---

## UPDATE — Strata multi-conversation shared core passes first Windows admission tests

#57 update at **19:57:42 UTC**: rebased shared-core work has its Windows physical-memory admission helper passing **23/23 MSVC tests**; a live `GlobalMemoryStatusEx` probe returns usable physical-memory data and impossible allocations are denied.

Full Windows restore/agent acceptance is still pending.

### P51 consequence

Keep the shared snapshot work as a mechanism reference, not a production-ready source yet.

---

## RECOVERED OLDER — direct physical M1 Max 32-GB Flash-Next @128K via MoEspresso 3

MoEspresso 3 was committed **2026-09-24** and surfaced in the community on Sep 27; it was missed by prior watches, so this is **RECOVERED OLDER**, not NEW.

Physical configuration:
- **2021 M1 Max, 24-core GPU, 32 GB unified memory**;
- Qwen3.8-Flash-Next, all 512 routed experts retained in package;
- default served context **131,072**;
- measured physical grid **12.96–15.85 TG**;
- release Cache-Prior 2/2 cell **15.46 TG**;
- planner ceiling 24 GB, 43-token prompt, 32 greedy generated tokens, disk KV disabled.

Memory/quant design:
- 223/512 routed experts resident per layer on measured 32-GB configuration;
- most routed projections **IQ2_K**; six early projection groups **IQ3_K**;
- dense/non-routed tensors use higher Q6/Q8/BF16-class precision by role;
- the original **102.4-GB BF16 PLE** remains file-backed on SSD and selected rows are read on demand;
- attention state uses KVarN K4/V4 with exact BF16 sink/recent suffix;
- no separate MTP sidecar in this package.

Decode uses Cache-Prior 2/2 when bounded: resident experts get a ranking preference while the two strongest original routes are protected. Prefill is unbiased. This can change the selected expert set and therefore model output.

Quality receipt is a reproducible but small 48-question mixed-category suite: local bounded path **84.3%** at medium reasoning vs hosted Qwen3.8 Flash **90.7%** at xhigh under a different provider protocol.

### P51 consequence

This is valuable **physical Apple7 feasibility evidence**:
- full Flash-Next architecture can serve 128K interactively on a severely memory-constrained M1 Max;
- dynamic precision + bounded expert residency + file-backed PLE + compressed attention state is practical on 2021 silicon.

But it receives **no AA40/source-like numeric credit** because the routed experts are mostly IQ2_K and Cache-Prior deliberately changes routing. It also receives no direct dual-node scaling credit and does not move the 40-TG target.

---

## NEW — oMLX finds the long-context QSA crossover moved after fused attention rows

Issue #4061 opened **2026-09-28 19:24:11 UTC**, M5 Ultra / Flash-Next oQ5e.

oMLX currently switches text-only decode at 32,768 cached tokens from rank-one masked QSA to gathered QSA arms, based on an older M5 Max crossover.

With newer fused attention rows on M5 Ultra, the **masked path is faster at every tested context from 16K to 128K**:
- MTP off: **~5–6% faster** at 48K–128K;
- MTP on: **~3–8% faster** at 48K–96K.

The masked path is also bit-identical to the unfused MLX reference; the gathered path is not. Attention's share of one decode token grows from **19% at 16K to 26% at 64K**.

### P51 consequence

- QSA execution-plan thresholds must be keyed by chip + kernel generation + context + verify width, not inherited globally from another Apple generation.
- Long-context AA baseline should prefer the bit-exact masked path whenever it is not slower.
- No M1 numeric credit yet, but this identifies another plausible 128K TG lever for Apple-specific tuning.

---

## NEW — SGLang closes another PD transfer ownership hole

PR #41404 merged **18:19:51 UTC**.

Before the fix, decode-side KV pages were deferred only when decode itself initiated an abort. A prefill fault, transport error or cache-restore failure could immediately release those destination pages while another rank still had a write in flight. The allocator could hand the pages to another request and the late transfer would corrupt the new owner.

The fix:
- notifies every prefill rank on any deferrable transfer failure;
- arms drain-ack accounting before the abort notification;
- retains destination ownership until all settled writers ack drain, or timeout;
- releases immediately only when metadata was never published and therefore no remote writer can know the destination.

### P51 handoff rule

**Destination state pages remain owned by the transfer transaction until every possible writer has crossed a completion/drain fence. Failure is not permission to free them.**

This applies directly to CUDA->Apple import staging and any future TB4 state mover.

---

## NEW — vLLM resumable-request fix defines the correct continuation frontier under async execution

PR #58259 merged **19:26:57 UTC**.

With async scheduling, `num_computed_tokens` can be an optimistic frontier that includes old-turn dispatches still in flight. Reusing that value when a turn ends lets stale outputs land in the next turn.

The fix resumes from:

**safe_frontier = computed_tokens - output_placeholders**

then marks the remaining in-flight outputs stale and drains/discards them before new-turn output is accepted.

### P51 handoff rule

State export/import and resident-agent continuation must snapshot the **materialized committed frontier**, never the optimistic scheduled frontier. Any old-turn GPU work still in flight must be fenced or explicitly marked stale before ownership advances to the successor turn.

---

## NEW — SGLang replay fix: token metadata belongs to the committed token, not the recomputation

PR #41235 merged **19:02:27 UTC**.

During PD rebootstrap, SGLang can replay a previously emitted boundary token after prefill recomputes the prefix. It already kept the original behavior logprob but incorrectly appended the new prefill worker's sampling-mask row, producing one extra/misaligned mask row.

The fix keeps both the original logprob **and original sampling mask** for the replayed token.

### P51 consequence

Continuation lineage must include token-associated metadata whose semantics came from the original committed decision. Recomputing the same boundary token does not authorize silently replacing its behavior/sampling metadata.

---

## RECOVERED CURRENT — long-context multi-row attention can make speculation slower if the verify path is wrong

vLLM #59054 was opened before this pass boundary (**15:04:50 UTC**) and is therefore **RECOVERED CURRENT**.

On the Triton attention backend, any speculative verify `q_len > 1` was forced onto a low-parallelism 2D varlen kernel. At 67K KV length, measured per-call attention was **~7–20x slower** than a small-q 3D split-KV path; serving with k=2 speculation fell to **16.5 TG** versus **56.1 TG** non-spec, while the proposed 3D verify path recovered **33.7 TG**.

### P51 consequence

Another independent confirmation that **multi-row verification needs its own long-context attention plan**. Never assume the B1 attention kernel is appropriate merely because q_len is small; benchmark verify widths and context jointly.

No Apple/CUDA target credit from these SM80 numbers.

---

## STRICT-WINDOW non-events

- **Ishizuki:** no new commit.
- **TensorFold:** no new post-0.3.6.2 commit in-window.
- **mlx-serve:** no new commit in-window.
- **MTPLX / DFlash:** no new commit in-window.
- **Splash:** Hermes profile isolation/benchmark-harness maintenance only; no model-performance receipt.
- **Strata:** no new exact-5070-Ti TG/PP ladder or longer exact-card soak in this window.

---

## Canonical planning effect

**No numeric speed-target changes.**

The strongest change is architectural confidence:
- shared immutable prefixes are worth pinning immediately;
- but actual multi-agent memory credit requires physical state sharing, not merely cache reuse;
- state handoff must use a committed safe frontier and transaction-owned destination pages until every writer drains;
- direct M1 Max 32-GB evidence further confirms that Flash-Next's 128K execution is physically viable on Apple7 even under severe memory pressure, while remaining too lossy/routing-biased to certify the AA40 production lane.

## New hard boundary

**2026-09-28 20:02:08 UTC**
