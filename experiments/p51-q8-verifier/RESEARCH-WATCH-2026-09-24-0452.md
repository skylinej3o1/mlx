# Project 51 primary-lane research watch — 2026-09-24 04:52 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 06:15:43 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 08:52:30 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared, and no new post-boundary DASLab / GSQ-RCO / ByteShape source-vs-quant xhigh behavioral certification appeared.

This pass is nevertheless mechanism-positive:

- a fresh oMLX Qwen4/Flash-family GDN route shows a controlled **~3.6-6.0% target-only decode gain out to 255,598 tokens** on M5 Max, but at **+1.5 GiB resident memory**;
- oMLX added a verifier-specific expert-ordering kernel that groups repeated expert accesses to improve cache reuse while preserving per-pair arithmetic bit-exactly;
- DS4 fixed a subtle exact-family speculative correctness hole where MTP verification did not inherit the target sampler's `ignore_eos` token-admissibility rule;
- a fresh DS4 distributed field update gives another homogeneous two-Mac direct-link data point, but remains TB5/M4 transfer evidence rather than M1/TB4 proof.

## Findings

### NEW — oMLX #3890: widening fused GDN decode gives ~3.6-6% long-context gain, with a measured memory tax

Source: https://github.com/jundot/omlx/pull/3890  
Created: **2026-09-24 07:22:01 UTC**; merged/closed in-window.

The existing fused Qwen4 B1/T1 GDN decode path was gated to the exact affine quant recipes emitted by the oMLX converter. Community Qwen3.8-family checkpoints using other canonical affine bit/group allocations silently fell back to the unfused chain even though the fused kernel consumes the same bf16 projection outputs.

The opt-in `OMLX_QWEN4_GDN_DECODE_WIDE_PROJ=1` widens admission to canonical affine allocations while retaining shape/dtype/group checks.

Measured on:
- MacBook Pro **M5 Max 128 GB**;
- Qwen3.8-Flash-Next-family community checkpoint `Qwen3.8-Flash-Next-Uncensored-Mixed-opt8`;
- 8-bit/g64 GDN + attention, 4-bit/g64 routed experts;
- no draft model / target-only decode in the paired harness.

Paired same-process decode A/B:

| context | old route | fused route | gain |
|---:|---:|---:|---:|
| 1,011 | 47.25 TG | 49.83 | **+5.03%** |
| 8,120 | 42.30 | 44.40 | **+4.98%** |
| 129,835 | 33.69 | 35.28 | **+6.04%** |
| 255,598 | 38.52 | 39.90 | **+3.58%** |

The route counter reports 0 fused calls in flag-off segments and 4,608 in each flag-on segment (36 GDN layers x 128 decode steps).

An independent HTTP A/B supports the sign at 1K/8K:
- 1,024: 47.64 upstream / 48.03 flag-off / **49.02 flag-on**;
- 8,192: 43.61 / 43.77 / **45.85**.

The HTTP method becomes unreliable at larger contexts on this 128 GB machine because run order, page-cache state and memory-pressure/reclamation dominate the ~5% effect. The long-context evidence therefore rests on the paired in-process decode harness rather than the noisy served A/B.

The speedup has a concrete memory cost: the fused route caches concatenated packed GDN projection weights, about **42.78 MiB per GDN layer x 36 = +1.50 GiB resident**. At 64K, the flagged arm also reaches the engine's memory caution/reclaim path far more often than the control.

Projection concatenation is bit-identical to four separate quantized projections; the fused-vs-unfused layer output is not bit-identical because the already-existing fused path uses bf16 scaling in q/k normalization (max layer-level delta reported ~2.4e-3). The PR changes which checkpoints enter that already-existing route, not the fused math itself.

**Classification:** NEW exact-family-community / stronger-Apple target-decode evidence.

**P51 consequence:** GDN fusion remains a real long-context lever even after QSA is budget-bounded, but **fusion cache residency belongs in the optimization objective**. On 64 GB M1s, a 3-6% decode win that permanently consumes ~1.5 GiB may or may not be worth taking if those bytes could instead protect quant-sensitive tensors, keep experts resident, or increase state headroom. P51 should optimize **TG per resident byte**, not TG alone.

**Target impact:** none. M5 Max, non-canonical community weights, and target-only decode do not provide M1/TB4 numeric transfer.

### NEW — oMLX #3797 commit 485ee0fa: order verify (row,expert) pairs by expert to reuse weight cache

Source: https://github.com/jundot/omlx/commit/485ee0fa099017e2c89a6498c2e24b9c9f268bd8  
Fresh commit: **2026-09-24 07:00:11 UTC**.

Lightning-MTP verification emits multiple (row, expert) pairs. The prior gather path executes pairs in routing order; consecutive proposal rows often select the same experts, causing repeated weight reads.

The new Metal path:
- supports 2-8 verify rows;
- supports affine 4/5/6/8-bit, group sizes 32/64/128;
- orders the same pairs by expert so repeated expert tiles execute back-to-back and can hit cache;
- preserves each pair's output **bit-for-bit** versus `mx.gather_qmm`;
- preserves the verifier's logical row ordering in the returned output.

Tests cover 2 and 8 rows, qmv-fast and tail paths, and all supported bit widths.

No end-to-end or microbenchmark receipt was attached to this commit by the cutoff.

**Classification:** NEW verifier-mechanism evidence, **no performance credit yet**.

**P51 consequence:** this is almost exactly the proposed **expert-union / repeated-expert reuse** direction in concrete form. It confirms that verifier routing can be reordered physically for locality while preserving logical per-row results. P51 should benchmark expert-sorted traversal, true expert-union fusion, and ordinary routing separately at the actual M1 verify widths; do not award TG credit until the profiler shows reduced target-forward-equivalent cost.

### NEW — DS4 #1070 commit e1a9e311: MTP verification must inherit the target sampler's stop-token admissibility

Source: https://github.com/antirez/ds4/commit/e1a9e31146e0a50cfe5ea0817251f34dd70e1037  
Fresh commit: **2026-09-24 07:32:15 UTC**.

Qwen3.8-Flash-Next MTP verification previously compared drafts against the raw target argmax even when the caller requested `ignore_eos` / think-mode-specific stop suppression.

The fix:
- computes target argmax after excluding stop tokens when `ignore_eos` is active;
- refuses to accept a draft token that is itself disallowed by that stop policy;
- applies the same filtered parent token to chained MTP drafting;
- threads the sampling constraint through both first- and second-draft verification.

**Classification:** NEW exact-family speculative-correctness evidence.

**P51 consequence:** speculative acceptance is not merely `draft == target argmax`. The verifier must inherit the **same admissible-token mask / stopping semantics / thinking-mode policy** as the target sampler. Certification should explicitly test EOS suppression, reasoning delimiters, tool-call termination and max-token boundaries under both target-only and MTP paths.

No performance implication is assigned.

### UPDATE — DS4 #651: two-Mac direct-link field report supports distributed feasibility but not M1 scaling

Source: https://github.com/antirez/ds4/issues/651  
Fresh issue activity in-window: **2026-09-24 06:24:25 UTC**.

Field report:
- **2x MacBook Pro M4 Max 128 GB**;
- Thunderbolt 5 bridge using **TCP**, not RDMA;
- DeepSeek-V4-Flash quant;
- DS4 CLI tensor parallel: **22.7 TG sustained** over a 550-token generation;
- server pipelined distribution: roughly **19-20 TG**.

The reporter notes TP synchronization did not appear to be the bottleneck at these sizes. There is no controlled single-Mac baseline in the report, so this cannot be converted into a TP scaling factor.

The same issue also contains a corrected two-DGX-Spark RDMA server report: current DS4 can serve network TP correctly, and a 30-minute mixed soak completed **83/83 requests** at `--ctx 131072 --batched-session 2`. The earlier apparent unsharded-memory failure was actually an 8-session memory-admission mistake.

**Classification:** UPDATE / cross-hardware distributed evidence.

**P51 consequence:** another data point that direct-link inter-node synchronization can be practical for interactive inference, even over TCP on TB5, and that **per-session state memory can dominate distributed admission before link bandwidth does**. It does not establish M1/TB4 PP2 throughput or justify changing the 40-TG target.

### KNOWN / fresh merge — oMLX #3840/#3842 hybrid draft-cache fixes

Both PRs merged in-window at 08:28 UTC. Their substantive evidence was already preserved in canonical state before this boundary:
- derive logical draft-cache position from actual attention layers rather than recurrent layer 0;
- publish recurrent draft-state snapshots at reachable block boundaries;
- warm draft scoring becomes suffix-only rather than silently re-prefilling the whole prompt.

**Classification:** KNOWN/UPDATE (merge only).  
**State effect:** none; already durable.

### KNOWN — SGLang #40947 shared-host PLE

Fresh review activity occurred in-window, but the substantive TP1/TP4/TP8 measurements were already preserved in state: removing one PLE all-reduce per step cuts the gather microkernel strongly while moving whole-server throughput only ~0-1%. No new P51 conclusion.

### Cross-hardware / lower-priority items screened

- **oMLX #3891:** GLM-5.3-Flash oQ8 experts can use already-compiled native affine block kernels; bit-exact versus stock gather, layer microbench +9%, whole admin-prefill cell at 8K +1.6%. Useful implementation detail for high-bit expert support, but no Flash/M1 target credit.
- **SGLang #41048:** fixes a small unbudgeted ratio-2 recurrent pair-state pool. Correctness/accounting rule is already covered by the existing "enumerate all state classes using actual addressing geometry" contract; numeric impact in the tested configuration is only ~0.007-0.04% token capacity.
- **SGLang #40118:** experimental "preserve speculative decoding during prefill across DP ranks" merged, but the PR contains no performance/accuracy description sufficient for P51 evidence promotion.
- **llama.cpp #29340:** no new performance result; existing threadgroup-memory guard remains as previously recorded.
- **vLLM Qwen4Exp PP/PLE work:** active but no new GPU-validated exact-family result in this freshness window sufficient to change state.

## Quant / community search

- **IST-DASLab/GSQ:** no issue, PR or commit activity in-window.
- No new precisely timestamped DASLab/RCO or ByteShape source-vs-quant xhigh behavioral receipt was found.
- Same-day Reddit/Hugging Face searches surfaced older Flash-Next benchmark posts and previously known low-bit/long-context reports, but no result with a verifiable publication timestamp strictly inside **06:15:44-08:52:30 UTC** that warranted promotion.
- Therefore no quant-frontier movement is recorded.

## Canonical planning state after this pass

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**, conditional on at least modest speculation benefit.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target; the Apple7 + heterogeneous-quant + verifier co-design lane remains an experimental upside branch.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 08:52:30 UTC**
