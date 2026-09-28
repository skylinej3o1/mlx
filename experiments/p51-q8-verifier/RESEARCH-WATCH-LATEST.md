# Project 51 primary-lane research watch — 2026-09-28 09:58 ET

**Freshness boundary entering this pass:** **2026-09-28 11:34:46 UTC**.  
**User cutoff:** **2026-09-28 13:58:58 UTC**.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash-Next: **40 TG @ genuinely filled ~128K / 400 cold PP / ~70% >=40 confidence**
- single-M1 dense27B: **25 TG / ~110 PP**
- RTX 5070 Ti dense27B: context-aware ladder from the prior pass
- unpruned/source-like Flash-Next as the AA~40 production-quality baseline

## NEW — Strata 0.1.16 supports DASLab's 256-of-512-expert Flash-Next Coder

PR #54 merged in-window; v0.1.16 published **2026-09-28 12:44:05 UTC**.

The DASLab Coder keeps **256/512 routed experts per layer**, still top-10 active/token. Retained weights are 3.5 bpw; resident transformer shard is 29.6 GB and the PLE/ngram shard may stay off resident memory.

DASLab xhigh quality:
- LiveCodeBench v6: **87.43 BF16 -> 86.28 Coder (98.7% retained)**
- SWE-bench Verified: **82.80 -> 75.60 (91.3% retained)**

Therefore this is **not source-like enough for the AA~40 primary lane**. It is a capability-targeted coding/agent/vision compression lane.

Strata RTX 5070 12 GB / R5 7600 / 64 GB matrix:
- 1K: **599 PP / 53.3 TG**
- 4K: **1,152 / 50.6**
- 32K: **1,298 / 53.3**
- 64K: **1,350 / 50.8**
- 128K: **1,266 / 44.0**
- 262K: **1,034 / 42.8**

A separate RTX3090 PR test ran ~3.5 hours to **192K context**, one compaction, zero engine errors, 27–42 TG and 65–85% draft acceptance.

**P51 consequence:** keep Coder as a specialized capacity/coding fallback and expert-pruning research lane. Do not credit its speed/memory savings to the unpruned dual-M1 target.

## NEW — Strata 0.1.17 ships sampler semantics + Claude Code fixes

Sampler commit 3e936701c877b57c2ff49040e0a674bd0bd981c7; engine commit 236d5f214a9917b7f3f320fbc09b828d0dae5401; release published **13:40:19 UTC**.

Sampling order is now:
1. penalties once
2. top_k
3. top_p
4. min_p
5. temperature

The prior double-penalty defect is closed; greedy/default-temperature-zero is unchanged.

0.1.17 also fixes:
- Anthropic `/v1/messages?beta=true` query-string handling
- mid-conversation system/developer messages that previously crashed the Qwen chat template

A reporter verified a real Claude Code edit-and-test task with ~17K–25K prompts and KV reuse.

**P51 consequence:** protocol/envelope compatibility belongs in agent-runtime certification.

## NEW RISK WATCH — Strata #60: 16-GB VRAM / 64-GB RAM Windows admission failure

Opened **2026-09-28 13:51:03 UTC**. Windows 10, 16 GB VRAM + 64 GB RAM, Swift1.5 IQ2_XS, 64K context.

Log:
- 33.02 GiB expert arena loaded
- whole-arena cudaHostRegister fails; ~29 GiB pins in slices
- engine reports ~9.96 GiB free VRAM and chooses a 9.28-GiB expert cache
- cudaMalloc(9.28 GiB) then fails OOM

No maintainer diagnosis by cutoff.

**P51 consequence:** exact 5070-Ti Windows admission tests must reserve fragmentation/driver/module/vision/MTP headroom before auto-sizing expert cache and observe free VRAM before/after host registration.

This is separate from the fixed mid-generation DMA/driver-lock stall.

## UPDATE — no exact-5070-Ti post-fix clean soak yet

No new #31/#29 stall-thread receipt appeared in this window. Keep the production liveness gate.

## NEW — SGLang virtual->physical recurrent checkpoint corruption fix

Commit da3eb6db32a1d2de6e8bb0d4b3984a33c1d3f7ef merged **12:19:19 UTC**.

Unified-memory Inkling wrote virtual `mamba_track_indices` as physical slots. Cold recompute was correct, but prefix hits restored stale/foreign conv state:
- max |Δlogprob| **0.086 / 0.120**
- greedy first-token flips

Translating track ids through the virtual->physical mapping restores bit-exact tested hits.

**P51 rule:** state lineage includes logical->physical slot mapping; never write virtual ids directly into physical recurrent storage.

## NEW — llama.cpp Metal graph packing must remain shape-stable for zero-row branches

Commit d77dd0806dc26fc418273ef99f88da11239ca41b at **13:36:38 UTC**.

Zero-element tensors were excluded from fusion matching, so no-output decode graphs packed differently from the reserved graph and triggered allocator re-reserve. They now preserve structural packing and dispatch zero threadgroups.

The same commit broadens recurrent-state rollback/split-replay testing across generated model architectures.

**P51 consequence:** include S=0/no-output and partial-accept branches in Apple graph-allocation/state tests.

## UPDATE — vLLM PLE metadata: mostly a concurrency win

Commit 20b52e9f5b5793d56586b91df9b93cbe30a24040 merged **12:46:22 UTC**.

Metadata-builder microbench: **~32–48% less wall time**.

Qwen3.8 Flash TP4+MTP3 E2E:
- c=1 output **244.3 -> 240.6 TG (-1.5%)**
- c=8 **490.0 -> 514.3 TG (+5.0%)**
- c=8 TPOT ~-4.7%, TTFT ~-4.5%

**P51 consequence:** metadata/control optimization is mainly a B2-B4/multi-agent lane unless B1 wall-clock proves otherwise.

## NEW EXPERIMENTAL — TensorFold exact conversation checkpoints spilled to SSD

PR #68 opened **12:41:59 UTC**, not merged by cutoff.

M5 Ultra / Qwen3.8-27B 4-bit + DFlash2:
- evicted 35,583-token conversation restored in **2.3 s**
- cold fresh server: **26.2 s**
- 35,396 cached tokens reused
- output SHA byte-identical
- 2.2–2.4 GiB spill in **0.18–0.19 s**, read-back ~0.24 s

**P51 consequence:** strong mechanism for multi-agent exact SSD cache tier; no M1 SSD timing transfer.

## UPDATE — MLX-Serve DFlash tree approaches TensorFold on M5 Max, not uniformly

PR #604 updated through cutoff; #606 adds follow-ups.

Experimental path: compact GDN initial-state replay, up to 16 verify rows, native uint4 NAX kernels, earlier GPU submission.

M5 Max examples:
- Vontra 4-bit code T=1: control **132.8**, candidate **181.4**, TensorFold **201.1 TG**
- ddalcu 4-bit code T=1: candidate **~202–212**, TensorFold **~200–201**

Chat/checkpoint results are less consistent. #606 makes replay length a runtime input rather than a per-length template specialization.

**P51 consequence:** compact initial-state + accepted-path replay is viable; S up to 16 remains workload/checkpoint/hardware dependent. No M1 numeric credit.

## WATCH — oMLX quantifies remaining Flash MoE bandwidth headroom

Issue #4054, M5 Ultra/oQ5e:
- R=1: **54.2 us/layer = 2.60 ms/step**, ~1.81 ms byte floor
- R=4: **118.6 us/layer = 5.69 ms/step**, ~4.17 ms byte floor

Potential gap ~0.79 ms/step R1 and ~1.52 ms/R4 verify window if fully closed. Roadmap/profile only.

**P51 consequence:** MoE remains a plausible lossless optimization target after verifier correctness; measure M1 bytes/read and achieved bandwidth before transfer.

## SAME-DAY CURRENT — exact 5070 Ti Strata code-generation corroboration

A same-day Reddit update in the existing Strata thread reports **~91 TG on RTX 5070 Ti at 64K while generating code** with IQ3_XXS. Exact comment timestamp is unavailable, so this is corroboration, not strict-window evidence. It does not change the liveness gate.

## Strict-window scan summary

From **11:34:46 -> 13:58:58 UTC**:
- **Strata:** Coder support/release, 0.1.17 sampler+Claude-Code fixes, 16GB/64GB Windows admission issue; promoted.
- **SGLang:** recurrent-slot translation corruption fix; promoted.
- **llama.cpp:** Metal zero-element graph-packing + broader rollback tests; promoted.
- **vLLM:** PLE metadata optimization; promoted with B1-vs-concurrency caveat.
- **TensorFold:** exact disk-spill checkpoint PR; experimental promotion.
- **mlx-serve:** DFlash tree comparison/followups; mechanism promotion.
- **oMLX:** MoE bandwidth roadmap; watch.
- **Ishizuki / MTPLX / Splash / upstream DFlash:** no strict-window primary-lane commit.

## Canonical planning effect

**No target changes.**

Coder fails the source-like agentic quality bar strongly enough to remain secondary. Strata's liveness fix still lacks exact-card clean soak validation. Apple findings refine graph/state/cache engineering but do not provide a new physical dual-M1/TB4 Flash-Next receipt.

## New hard boundary

**2026-09-28 13:58:58 UTC**
