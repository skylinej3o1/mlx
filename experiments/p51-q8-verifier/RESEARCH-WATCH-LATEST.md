# Project 51 primary-lane research watch — 2026-09-27 08:54 ET

**Freshness boundary checked:** prior hard boundary **2026-09-27 11:03:54 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-27 12:54:04 UTC**.

## Decision

**No canonical TG/PP, quant-quality, or planning-confidence change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- central TG **~39-41**, mature downside **~30-32**, target-only fallback **~24-27**
- single-M1 27B: **25 TG canonical target**
- RTX 5070 Ti dense-27B: **120 TG mature target / 250 cold PP baseline target**
- practical Flash secondary lane: **5070 Ti + Strata + DASLab IQ3_S/IQ3_XXS**, pending exact-machine quality/speed certification.

## NEW — vLLM removes per-step D2H synchronization from sparse-attention planning

Source: https://github.com/vllm-project/vllm/pull/58684  
Merged as `c8d7a7dd13e2b40c013fb6d46be800937e4335fb` at **2026-09-27 11:06:23 UTC**.

### Problem

`FLASHINFER_MLA_SPARSE_SM90` needed exact per-row KV lengths to build its host-side plan. Under async scheduling/speculative decode, the available host value was only an optimistic upper bound, so the backend performed a **blocking device-to-host copy** of exact sequence/position state every metadata build. MTP paid this on every draft step.

On the benchmark workload this made async scheduling slower than synchronous scheduling.

### Fix

1. Plan from the already-available **CPU upper bound + 32 tokens of slack**.
2. Cap the planned bound at the architecture's maximum valid sparse count.
3. On GPU, compute the exact per-row valid count from device sequence/layout state.
4. Clamp every planned work item's `kv_end` to that exact value before attention runs.
5. Reuse the padded plan across subsequent decode/draft steps while the live context remains inside the bound.

This removes the D2H synchronization and avoids repeated host replanning while retaining exact bounds at the point the kernel consumes them.

### Measured result

Setup: **GLM-5.3-Flash, TP8 H100, fp8 KV, MTP-5, max context 32K**, random 1024-in/128-out serving benchmark.

| concurrency | main async TPOT | patched async TPOT | change |
|---|---:|---:|---:|
| 1 | 11.09 ms | **6.86 ms** | **-38%** |
| 8 | 21.87 ms | **17.36 ms** | **-21%** |
| 32 | 45.04 ms | **37.04 ms** | **-18%** |

At c=1 TTFT also drops **136.6 -> 128.1 ms**. The patched async path becomes faster than the no-async path at every tested concurrency. MTP mean acceptance remains about **4.2**. GSM8K does not regress.

Classification: **stronger-chip / different sparse-attention architecture transfer evidence**. Zero direct M1/Flash target credit.

### P51 consequence

This is a clean general systems rule for our Apple/QSA/speculative work:

> **If exact dynamic metadata lives on-device, do not synchronize it to the host just to make a plan. Plan conservatively from a bounded host view, then clamp/validate exactly on the device immediately before use.**

Potential Project 51 applications:
- QSA/indexer scheduled lengths and sparse ranges;
- variable speculative row count / accepted-prefix geometry;
- per-step MTP/verifier work descriptors;
- recurrent/prefix-state ranges where a host-side upper bound exists;
- any Apple Metal path where host inspection would force command-buffer completion.

Important guardrails:
- slack/bounds must be explicit and capped;
- the consuming GPU path must perform the exact clamp/check;
- plan reuse must invalidate when the live state can escape its certified range;
- correctness tests should compare conservative-plan+clamp against exact-plan outputs around boundary cases.

## Other strict-window activity

- vLLM also split H200 speculative-decoding CI jobs; testing infrastructure only.
- llama.cpp changes were PLaMo-3 conversion, Jinja and CI updates; no P51 impact.
- no qualifying new commit in oMLX, mlx-serve, DS4, Splash, MTPLX, Ishizuki, Strata, DFlash, DASLab/GSQ, ModelOpt or SGLang's primary inference lane.

## Community scan

Current Reddit searches resurfaced the already-recorded M1 Splash replication, Splash-M1 release, Strata 5070 thread, and earlier Flash-Next/offload posts. No new independent **M1 Max 64K/96K/128K** measurement or new Strata 5070 Ti receipt appeared inside this strict interval.

## Canonical planning state after this pass

Unchanged. The useful delta is another strong independent example that **host synchronization around speculative/sparse metadata can dominate the benefit of otherwise-good GPU work**, and that conservative-plan + device-clamp is a practical way around it.

`RESEARCH-STATE.md` is updated with the durable planning rule. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 12:54:04 UTC**
