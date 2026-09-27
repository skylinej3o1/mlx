# Project 51 primary-lane research watch — 2026-09-27 09:12 ET

**Freshness chain:** previous canonical boundary was **2026-09-27 11:03:54 UTC**. A concurrent sub-pass covered through **12:54:04 UTC**; this reconciled pass verifies the full interval through the user cutoff **2026-09-27 13:12:54 UTC**.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- central TG region **~39-41**, mature downside **~30-32**, target-only fallback **~24-27**
- single-M1 27B: **25 TG canonical target**
- RTX 5070 Ti dense-27B: **120 TG mature target / 250 cold PP baseline target**
- 5070 Ti + Strata Flash lane: experimental pending exact-hardware TG/PP + AA~40 certification.

## NEW — vLLM #58684: eliminate sparse-attention D2H planning sync

Source: https://github.com/vllm-project/vllm/pull/58684  
Merged **2026-09-27 11:06:23 UTC**, commit `c8d7a7dd13e2b40c013fb6d46be800937e4335fb`.

Under async scheduling, FlashInfer sparse MLA was performing a **blocking device-to-host copy on every metadata build** to recover exact per-row sequence/KV lengths. With MTP this happened on every draft step as well.

On GLM-5.3-Flash / H100 / TP8 / fp8 KV / MTP-5:
- baseline async c=1 TPOT: **11.09 ms**
- baseline no-async c=1: **7.70 ms**.

So async scheduling was actually slower because sparse-plan construction synchronized with the GPU.

### Fix

1. Build the host plan from the already-available CPU **upper bound + 32 tokens of bounded slack**.
2. Compute exact valid counts on GPU and clamp each work item's `kv_end` before the sparse kernel consumes it.
3. Reuse the padded plan across later decode/spec steps while the growing context stays within the certified bound.
4. Fall back to an exact/syncing path only when no safe host bound exists.

Patched async mean TPOT:
- c=1: **6.86 ms (-38%)**
- c=8: **17.36 ms (-21%)**
- c=32: **37.04 ms (-18%)**.

The profiler reports the previous path incurred **13 blocking syncs over roughly five draft steps, ~79 ms total**. MTP mean acceptance remains ~4.2 and GSM8K is unchanged within normal run variation.

**Classification:** stronger-chip/different sparse-attention implementation. No numeric M1 credit.

**P51 design rule:** when exact dynamic sparse/QSA metadata resides on device, prefer:

**host conservative geometry + bounded slack -> GPU exact clamp/validation -> plan reuse**

rather than forcing a per-step D2H read. This should be tested for Apple7 QSA/index planning and speculative row/length metadata.

## Strict-window scan

No additional qualifying primary-lane performance or correctness receipt appeared through **13:12:54 UTC** in:
- oMLX
- mlx-serve
- Splash / M1 Splash
- MTPLX
- Ishizuki
- Strata
- DFlash2
- DS4
- llama.cpp Apple path
- ISTA-DASLab / GSQ
- NVIDIA ModelOpt
- SGLang primary inference work.

vLLM's only other relevant-window commit reorganized speculative-decoding CI. llama.cpp's commits were unrelated PLaMo/Jinja/CI changes.

## Community watch

Fresh web searches surfaced only already-recorded M1 Splash, Strata 5070, older Mac Flash and DASLab threads.

A same-day comment in the Ishizuki Reddit post says **Splash has been ported into the Ishizuki kernel**. There is **no new Ishizuki commit or benchmark in this strict interval**, so classify this as **WATCH ONLY**: potentially interesting convergence of the Splash and Ishizuki Apple7 work, but zero target credit until code + exact-hardware measurements appear.

## Canonical planning effect

**None.** This pass strengthens one control-flow pattern: eliminate host synchronization by planning from safe upper bounds and enforcing exactness on device.

`RESEARCH-STATE.md` is reconciled to one durable vLLM planning entry plus the boundary extension. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 13:12:54 UTC**
