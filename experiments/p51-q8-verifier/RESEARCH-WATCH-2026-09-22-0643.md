# Project 51 primary-lane research watch — 2026-09-22 06:43 ET

**Freshness boundary checked:** previous hard boundary **2026-09-22 09:29:14 UTC**. Search ran through the user's cutoff **2026-09-22 10:43:09 UTC**.

## Decision

**No numeric target or confidence change.**

This 74-minute window produced no new dual-M1/TB4 Flash receipt, no new M1 27B speed record, and no same-card 5070-Ti throughput record. The useful additions are two hardware-policy correctness guards that directly affect our M1 and 5070-Ti experiment lanes.

## NEW — consumer Blackwell IQ3_S toolchain trap

Sources: llama.cpp issue #28581 and closed PR #28784.

The issue was updated inside this window with independent reproductions that pin the failure to a narrow NVIDIA compiler window, not to Qwen3.8 or IQ3_S quality itself.

Observed on consumer Blackwell `sm_120` (RTX 5060 Ti and RTX 5080):

| nvcc / CUDA | IQ1_S/IQ2_S/IQ3_S op tests | real Qwen3.8 generation |
|---|---|---|
| 13.2.51 / 13.2.0 | **FAIL** | garbage |
| 13.2.78 / 13.2.1 | **FAIL** | garbage |
| 13.2.86 / 13.2.2 | **PASS** | coherent |
| 13.3.73 / 13.3 | **PASS** | coherent |
| 13.4.92 / 13.4 | **PASS** | coherent |

Mechanism: nvcc 13.2.0/13.2.1 miscompiles byte extraction from packed 32-bit IQ quant words on `sm_120`. Both MMQ and vector/cuBLAS-adjacent paths are affected, so forcing cuBLAS does not solve it. `IQ3_XXS`, `IQ4_XS`, XS-family sibling types and K-quants are unaffected in the reported matrix.

PR #28784 replaces the problematic byte indexing with `__byte_perm` and passes the affected op tests even on the broken compiler, but it was **closed without merge** once multiple testers established that NVIDIA fixed the compiler starting in CUDA 13.2.2.

### P51 consequence for the RTX 5070 Ti

Our 5070 Ti is the same consumer-Blackwell `sm_120` class, and our interesting 27B lane explicitly includes DASLab/GSQ-RCO `IQ3_S` tensors.

Therefore every 5070-Ti IQ3_S experiment must record:
- driver;
- CUDA toolkit;
- exact **nvcc patch version**;
- llama.cpp commit;
- `test-backend-ops` IQ1/2/3_S `MUL_MAT` and `MUL_MAT_ID` result before performance testing.

Prefer CUDA **>=13.2.2** (or a tree carrying the #28784 workaround). If an affected compiler produces garbage, that is a runtime/toolchain defect, **not evidence that the quant lost intelligence**.

No target change: our existing same-card performance receipts necessarily came from functioning paths; this is a reproducibility/version gate.

## NEW — Splash #96: GPU family alone is not a sufficient kernel-policy identity

Source: incoai/splash issue #96, created **2026-09-22 10:30:36 UTC**.

On M3 Ultra / Apple9 / **60 GPU cores**, Splash 1.0.2 + `Qwen3.8-27B-Splash` shows:
- B1 returns HTTP 200 but emits token soup;
- **833 drafted / 0 accepted** in one reproduction;
- B>=2 triggers `target policy selected an invalid next anchor` and leaves the engine unavailable;
- Splash 1.0 and 1.0.1 on the same machine/model remain correct with ~0.30-0.31 draft acceptance and routine B1-B4 use.

The reporter suspects the newer Apple9 matrix-decode path, whose release validation covered other Apple9 configurations but not this 60-core M3 Ultra. This is the same class of warning as yesterday's exact-M1 #95 result: isolated kernels/family-level gating can look valid while a real model is semantically wrong.

### P51 consequence

Kernel-policy identity should include at least:
`GPU family + GPU core count + model/quant + B/verify width + runtime revision`.

Our Actions runner should capture `system_profiler SPHardwareDataType` and the selected kernel-policy key into every result artifact. Promotion requires real-model greedy/logit/agent parity at B1 and the B2/B4 widths we intend to use.

This does **not** weaken the M1 #95 result: #95 is itself measured on the exact M1 Max 32-core configuration. It tells us not to generalize that policy blindly to a different M1/M2 core count if one appears.

## NEW — Splash scheduler CPU-overhead work, no receipt yet

Sources: Splash #97, #98, #99, created around **10:33-10:42 UTC**.

The current low-risk patch only reserves capacity for B<=4 scheduler batches and queued prefill-admission pointers. Focused scheduler/cache tests pass. No end-to-end throughput result is claimed yet.

One proposed allocation-free cache probe was deliberately removed because on long prompts it could replace a single deepest-state lookup with a lookup for every matched page. This is a useful design warning for our long-context warm-cache work: fewer allocations are not automatically lower wall time if they multiply cache/state probes.

Track these issues because Apple7 may be relatively CPU/dispatch-sensitive, but do not credit any TG/PP gain until ABBA results exist.

## Other exact-window checks

- vLLM had only unrelated merged commits in-window. Active Qwen/GDN/PLE work did not publish an M1/5070-Ti end-to-end receipt.
- vLLM #55313 documents an intermittent Qwen3.8 + DSpark K7 + streaming strict-JSON failure returning HTTP 200 with a huge whitespace tail. It strengthens the existing speculative-runtime behavioral gate, but is an older issue updated in-window and does not alter our hardware targets.
- llama.cpp had no new merged runtime commit relevant to the primary lanes during the window.
- Kadir, MTPLX, APEX, AutoRound, Harish 5070-Ti, mlx-serve and the M1-focused forks produced no qualifying new performance receipt.
- Targeted web/community search surfaced the already-known MTPLX, Splash Apple7/Q8 and expert-cache results; nothing newer displaced the current physical frontiers.

## Target / confidence impact

Unchanged:
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**, >=38 AA-class, ~70% planning confidence for >=40 TG;
- single-M1 27B: **25 TG**, ~65% confidence for >=25 after #95;
- RTX 5070-Ti 27B: **120 TG mature optimized target**; add CUDA/nvcc correctness gate, no probability change.

## New hard boundary

**2026-09-22 10:43:09 UTC**
