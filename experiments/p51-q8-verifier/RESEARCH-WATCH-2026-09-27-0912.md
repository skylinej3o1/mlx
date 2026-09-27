# Project 51 primary-lane research watch — 2026-09-27 09:12 ET

**Strict freshness boundary:** prior hard boundary **2026-09-27 11:03:54 UTC**. This pass covers substantive evidence strictly after that boundary through **2026-09-27 13:12:54 UTC**.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- central TG region **~39-41**, mature downside **~30-32**, target-only fallback **~24-27**
- single-M1 27B: **25 TG canonical target**
- RTX 5070 Ti dense-27B: **120 TG mature target / 250 cold PP baseline target**
- 5070 Ti + Strata Flash lane: experimental until exact-hardware TG/PP and AA~40 certification.

## NEW — vLLM removes per-step sparse-attention D2H synchronization

Source: https://github.com/vllm-project/vllm/pull/58684  
Merged **2026-09-27 11:06:23 UTC**, commit `c8d7a7dd13e2b40c013fb6d46be800937e4335fb`.

Problem: `FLASHINFER_MLA_SPARSE_SM90` needed exact per-row KV lengths to build its host-side sparse plan. Under async scheduling/spec decode, the available CPU-side lengths were only optimistic upper bounds, so every metadata build copied GPU `positions` / `seq_lens` back to CPU. With MTP this synchronization happened on every draft step.

On GLM-5.3-Flash / H100 / TP8 / fp8 KV / MTP-5:
- baseline async c=1 TPOT: **11.09 ms**
- baseline no-async c=1: **7.70 ms**

So the supposedly asynchronous scheduler was slower because metadata planning forced repeated D2H synchronization.

### Fix pattern

1. Build the host sparse plan from the existing CPU **upper bound + 32-token slack**, capped at legal maximum.
2. On GPU, compute the exact valid count and clamp each work item's `kv_end` before the sparse kernel reads it.
3. Reuse the same plan on subsequent steps while the growing context still fits inside its slack.
4. Fall back to the exact/syncing path only when no safe host bound exists.

Patched async TPOT:
- c=1: **6.86 ms** (**-38%**)
- c=8: **17.36 ms** (**-21%**)
- c=32: **37.04 ms** (**-18%**).

Profiler validation reports no blocking sync left in draft-step metadata build; before, there were **13 blocking syncs per ~5 draft steps, ~79 ms total**. MTP mean acceptance remains ~4.2; GSM8K is effectively unchanged.

### P51 implication

This is a stronger, concrete version of our existing rule that a host read inside a sparse/spec loop is a GPU barrier.

For Apple7 QSA / speculative verification, investigate the same shape:

**host conservative geometry + bounded slack -> GPU exact clamp/mask -> plan reuse across several decode/draft steps**

instead of reading exact QSA lengths/selection metadata back to CPU every step.

The useful lesson is the control-flow pattern, not the Hopper performance magnitude; no numeric transfer to M1 is allowed.

## Strict-window negative scan

No qualifying new primary-lane performance/correctness receipt appeared in:
- oMLX
- mlx-serve
- Splash (both repos)
- MTPLX
- Ishizuki
- Strata
- DFlash2
- DS4
- llama.cpp Apple path
- ISTA-DASLab/GSQ
- NVIDIA ModelOpt.

llama.cpp's strict-window commits were unrelated PLaMo/Jinja/CI work. vLLM's other strict-window commit only reorganized speculative-decoding CI.

Community/web searches returned the already-recorded M1 Splash 39-TG post, Strata 5070 128K results, older Mac Flash streaming results, and existing DASLab quality discussions; none is new evidence after the hard boundary.

## Canonical planning effect

**None.** The pass strengthens QSA/spec metadata scheduling design but does not change throughput or quality forecasts.

`RESEARCH-STATE.md` is updated with the conservative-host-plan + GPU-clamp + plan-reuse rule. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 13:12:54 UTC**
