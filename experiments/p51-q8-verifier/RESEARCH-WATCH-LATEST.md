# Project 51 primary-lane research watch — 2026-09-26 05:37 ET

**Freshness boundary checked:** prior hard boundary **2026-09-25 22:17:26 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-26 09:37:04 UTC**, plus newly surfaced older M1/community evidence classified separately.

## Decision

**No canonical TG/PP, xhigh-quality, or planning-confidence change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

This pass adds strong exact-Apple7 evidence for row-reuse/small-row kernels, one exact-M1 Flash-Next negative control whose memory/runtime configuration is heavily confounded, and new adaptive-verification / failed-restore correctness rules. Nothing closes the exact two-M1/TB4/128K receipt gap.

## Findings

### NEW — mlx-serve #530: decode-once multi-row kernels produce large M1 Ultra 27B gains, but only on the right tensor shapes

Source: https://github.com/ddalcu/mlx-serve/pull/530  
Merged **2026-09-25 22:30:36 UTC**.

The kernel decodes one packed 2-bit ternary word and reuses it across **1-8 activation rows**, with a different dispatch plan per Apple GPU generation. M1 Ultra is exact **Apple7/g13** evidence.

Selected **M1 Ultra 64-core / 128-GB** results:
- Bonsai 2 27B plain B1: **44.5 -> 49.2 TG (+10%)**
- B2: **50.8 -> 52.7 (+4%)**
- B4: **44.5 -> 57.0 (+28%)**
- Bonsai 2 27B MTP B1: **47.0 -> 48.9 (+4%)**
- Bonsai 2 27B MTP B2: **38.6 -> 45.9 (+19%)**
- Bonsai 1 27B B1: **34.2 -> 45.2 (+32%)**
- B2: **34.0 -> 44.8 (+32%)**
- B4: **38.1 -> 52.5 (+38%)**.

The important negative results are just as useful:
- outputs narrower than **2048 rows** (GDN a/b, attention k/v) route back to stock MLX because stock was **up to 2x faster**;
- a fused gate/up+SwiGLU prototype was effectively **~0% gain on M1 Ultra** even though it helped newer Apple chips;
- unmeasured Apple generations retain the old path rather than inheriting another chip's tuning.

**Classification:** NEW exact Apple7 small-row/multi-row kernel evidence; different model/2-bit quant.

**P51 consequence:** strongly reinforces the existing width-specific verifier policy. Weight reuse across S=2-8 can be a large Apple7 lever, but dispatch must be keyed by **tensor shape + row width + GPU generation**, not globally enabled. This supports the possibility of reducing verifier cost without implying a specific multiplier for Flash-Next.

### RECOVERED OLDER — exact M1 Max Flash-Next REAP320 runs are very slow, but materially confounded

oMLX community benchmark, dated **2026-09-25**:  
https://omlx.ai/benchmarks/performance?chip=M1

**M1 Max 32-core / 64 GB**, `Qwen3.8-Flash-Next-REAP320-oQ3e-fp16-DWQ-MTP-Vision-MLX`:
- **8K: 192.9 PP / 10.0 TG**
- another **8K: 140.7 / 5.5**
- **16K: 146.6 / 5.7**.

This is important because it is exact Apple7 + Flash-Next, but it should **not** be treated as a physical floor for Project 51:
- the FP16 MLX package is **71.7 GB on disk** on a 64-GB machine;
- it contains the multimodal/PLE layout and the public benchmark exposes no resident/wired/swap breakdown;
- the sister MTPLX pack explicitly streams its ~32-GB n-gram table from SSD and reports a **39.7-GiB resident floor**;
- that same weight family on M4 Pro/MTPLX reports **~31-35 TG from short prompt through ~85K**, showing that the checkpoint itself does not intrinsically run at 5-10 TG.

Also missing from the oMLX benchmark rows: MTP engagement/depth/acceptance, vision-engine lane, output length and swap state.

**Classification:** RECOVERED OLDER exact-M1 negative control with major runtime/residency confounds.

**P51 consequence:** physical memory plan is part of the model identity. Log **file/mapped bytes vs resident/wired bytes**, PLE placement, vision/text engine path, MTP engagement and swap before using an Apple benchmark in the performance model. These runs do **not** lower the current 24-27 target-only fallback.

### NEW — vLLM #57263 makes adaptive speculative verification explicitly width/graph-domain aware

Source: https://github.com/vllm-project/vllm/pull/57263  
Merged **2026-09-26 09:01:17 UTC**.

Gemma4 DSpark K=7 now supports adaptive verification with variable-length FULL decode graphs. Each backend advertises the largest graph-safe per-request query length; mixed prefill/decode batches are prevented from replaying a decode-only varlen graph.

Quality/correctness receipt in the PR:
- no speculation GSM8K: **62.32%**
- fixed DSpark K=7: **62.77%**
- adaptive: **62.62%**
- adaptive-vs-fixed difference: **-0.15 pp**, paired McNemar **p=0.868**.

**P51 consequence:** dynamic S is viable only inside the active backend/kernel's verified row-width domain. `S` must therefore feed graph/kernel dispatch as a first-class runtime variable; short prefills cannot be mistaken for verification rows merely because their token count is small.

### NEW — llama.cpp failed state restore is now transactional

Source: https://github.com/ggml-org/llama.cpp/commit/08618ff8e735141d8e4e5be28e6d6af170e4757b  
Committed **2026-09-26 07:23:03 UTC**.

The fix explicitly clears already-written K/V cells, recurrent state, hybrid attention state and MLA/DSA state when a later restore component fails, and discards deferred tensor writes.

**P51 consequence:** warm-prefix/checkpoint restore must be **all-or-nothing**. A partial restore failure may not leave stale physical tensors addressable by a later request. This extends the existing lineage/provenance rule from logical validity to physical cleanup.

### NEW integrated stronger-chip ceiling — mlx-serve v26.9.6

Release commit `1745ffe89e4670f1e0c6de22c75a9875b27399de`, **2026-09-26 04:37:51 UTC**.

The release combines the recently tracked prompt/history lookup, one-dispatch GDN and grouped fused-verifier work. Its M5 Ultra mixed-4/8-bit Flash-Next + MTP headline includes about **219 TG decode, 227 aggregate TG across 4 streams, and 3150 PP on an 8K prompt**. Copy/edit workloads can go higher because lookup drafts directly from conversation history.

**P51 consequence:** useful integrated exact-family software ceiling; no Apple7 numeric transfer.

### REDDIT / community re-check

No new planning-grade **32-core M1 Max** 64K/128K run and no new numeric M2 Splash depth curve were visible by cutoff. The original Splash thread still shows the useful author depth curve (**36.5 TG at 16-32K, 19.5 at 32-64K, 23.4 at 64-96K**) and the previously recorded independent 24-core-M1 replication, but no newer deep-context replication.

## Lower-priority strict-window items

- SGLang's Mamba2 `selective_state_update` changes launch geometry and reports up to **2x kernel speed / +7.5% serving** on B200 Nemotron-3-Super. This supports shape-specific recurrent-kernel tuning but is too remote from Apple7 to alter P51 planning.
- mlx-serve #533 turns prompt lookup on by default; its performance evidence is the already-recorded #523/#533 lookup study.
- llama.cpp's tiled CPU K-quant matmul is 3-6x for large CPU matmuls but regresses GEMV, reinforcing shape-specific dispatch; no Apple impact.
- no qualifying new DS4, oMLX-core, MTPLX-core, APEX/GSQ, IST-DASLab or M1-fork performance commit appeared after the boundary.

## Canonical planning state after this pass

Unchanged:
- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target.
- RTX 5070 Ti 27B: **120 TG** mature target.

`RESEARCH-STATE.md` is updated with the Apple7 small-row evidence, M1 Flash negative-control interpretation, adaptive-verification rule and transactional-restore rule. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-26 09:37:04 UTC**
