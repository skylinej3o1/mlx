# Project 51 primary-lane research watch — 2026-09-24 06:40 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 08:52:30 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 10:40:14 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared, and no new post-boundary DASLab / GSQ-RCO / ByteShape source-vs-quant xhigh behavioral certification appeared.

The strongest fresh result is nevertheless highly relevant to the verifier thesis: oMLX #3797 now reports **actual Qwen3.8-Flash-Next MTP A/Bs** after stacking several verifier/runtime optimizations. M5 Max B1 improves **92.8 -> 112.0 TG (+20.7%)** and M3 Ultra B1 **96.4 -> 104.8 (+8.7%)**. This is stronger-Apple exact-family evidence that small-row verifier specialization, expert locality, adaptive depth and runtime plumbing can compound. It is not M1 evidence and does not isolate any one optimization.

## Findings

### UPDATE — oMLX #3797 now has exact Flash-Next branch-level MTP A/Bs

Source: https://github.com/jundot/omlx/pull/3797  
PR updated through **2026-09-24 10:35:06 UTC**.

The branch now combines:
- batched DFlash drafting;
- small-M verify kernels;
- M5 packed Q4 projections;
- speculative draft/verify overlap;
- adaptive MTP depth;
- expert-ordered MoE verification;
- fresh zero-copy verify-KV access where cache geometry permits.

Fresh branch-level Flash-Next results:

**M5 Max 128 GB, Qwen3.8-Flash-Next oQ4e, Lightning MTP, coding prompts, temperature 1.0**
- B1: **92.8 -> 112.0 TG (+20.7%)**
- B2: **112.2 -> 116.2 (+3.6%)**
- B4: **118.1 -> 124.6 (+5.5%)**

**M3 Ultra 512 GB, same Flash-Next family**
- B1: **96.4 -> 104.8 TG (+8.7%)**
- B2: **130.9 -> 138.6 (+5.9%)**
- B4: **154.5 -> 170.1 (+10.1%)**

The same branch continues to show large dense-27B concurrency gains, but those are already recorded and are not P51 B1 evidence.

**Classification:** UPDATE / strong exact-family stronger-Apple verifier-system evidence.

**P51 consequence:** this is the clearest current evidence that **verifier-specific optimizations stack at whole-system level on Flash-Next itself**, rather than merely on dense 27B. The B1 M5 result is particularly relevant because it is not a multi-request aggregate illusion.

**Important limitation:** the PR does not provide a factorial ablation isolating small-M kernels vs expert ordering vs adaptive depth vs zero-copy KV vs other branch changes. Treat **+20.7% / +8.7% as branch-level gains only**. No individual mechanism inherits that percentage.

**Target impact:** none. M5/M3 are not Apple7, and the current P51 target is specifically dual M1 at filled ~128K.

### NEW — oMLX #3797 commit f8f51de: verify attention can read cache backing buffers directly instead of copying context-length KV every cycle

Source: https://github.com/jundot/omlx/commit/f8f51de80790798066a957b62b436f3c11352fb5  
Fresh commit: **2026-09-24 10:35:03 UTC**.

The ragged verify-attention path previously called `mx.contiguous(keys/values)` on prefix views returned from step-grown KV cache buffers. That can allocate/copy the **current context length on every verify cycle**, and the MLX buffer pool cannot efficiently reuse continuously growing allocation sizes.

The fresh path:
- detects when fetched K/V are a prefix view of a known cache backing buffer;
- passes the backing buffers directly;
- threads the physical KV stride separately from logical K size;
- falls back to contiguous copies for unsupported cache contracts;
- adds a parity test confirming backing-buffer reads are bit-identical to the copied-prefix path.

**Classification:** NEW verifier-memory-traffic mechanism evidence; no isolated benchmark.

**P51 consequence:** add a hard verifier invariant: **no O(context) materialization/copy on an S=2-8 verification step unless profiling proves unavoidable**. At 128K context, even a logically small verify block can accidentally become context-bandwidth dominated if cache views are materialized. P51's verifier profiler should separately count target-weight bytes, QSA/KV bytes, and temporary-copy bytes.

### KNOWN/UPDATE — oMLX #3853 merged: same-chip M1 GDN fusion evidence is now on main

Source: https://github.com/jundot/omlx/pull/3853  
Merged commit: **abdebd4b81a6** at **2026-09-24 10:39:39 UTC**.

The substantive evidence was already recovered into canonical state before this boundary:
- Apple **M1 Max 64 GB**;
- Qwen3.5/3.6 35B-A3B FP16 decode;
- mixed 4/5/6-bit conversions;
- fused eligible B1/T1 GDN prework;
- whole-server decode gain **~5.8-6.2%**;
- complete-response time down **~4.8-5.9%**;
- extensive numerical/server validation.

**Classification:** KNOWN/UPDATE (merge only).

**P51 consequence:** no new conclusion, but this same-chip evidence is now less provisional operationally. It remains nearby-GDN evidence, not Flash-Next/Qwen4 percentage transfer.

### NEW — DS4 #1115 real-hardware validation exposes a restart-cache identity hole

Source: https://github.com/antirez/ds4/pull/1115#issuecomment-5811161906  
Fresh comment: **2026-09-24 09:04:29 UTC**.

Independent M5 Max 128 GB testing with real Qwen3.8-Flash-Next-Q2 weights reports:
- TurboQuant KV kernel tests pass;
- chat/tool use coherent at 8-bit and 4-bit KV;
- TurboQuant engages in server logs;
- reasoning-retention harness: 9 PASS, 5 INCONCLUSIVE, **1 real FAIL**.

The failure:
- retention-off history after server restart restores **0/1033 cached tokens** instead of reusing the disk checkpoint.

The harness itself interprets this as evidence that the checkpoint/cache key must follow the retention/prompt-preservation switch.

**Classification:** NEW exact-family cache-identity correctness evidence.

**P51 consequence:** any runtime switch that changes **rendered reasoning/history semantics** must participate in checkpoint identity or force a cold path. Persistent state cannot be keyed only on visible message content/model/context geometry. Add reasoning-retention/prompt-preservation policy to warm-state identity and restart tests.

### NEW — DS4 #1119: LRU expert-cache thrash can collapse prefill when the active set exceeds cache capacity

Source: https://github.com/antirez/ds4/issues/1119  
Created **2026-09-24 10:10:59 UTC**.

On GLM-5.3-Flash Q2 / RTX Pro 6000 SSD streaming, the reporter observed:
- active expert set per prefill batch larger than cache;
- ordinary LRU reaches **0% hit rate**, because experts are evicted before reuse;
- freezing new cache admissions after the first prefill batch while still serving hits avoids cycling;
- reported prefill improvement **~110 -> ~400 tok/s**.

This is a field report, not a merged controlled upstream benchmark, and it is GLM/CUDA rather than Qwen/Apple.

**Classification:** NEW cross-family offload-policy evidence.

**P51 consequence:** if expert or sparse-table SSD streaming enters the shipping design, cache admission policy must be **working-set aware**. When batch active-set size exceeds cache capacity, ordinary LRU can be pathologically worse than a frozen/segmented admission policy. No numeric PP transfer.

### LOWER-PRIORITY / no state change

- vLLM #57039 only gained a merge-conflict/rebase comment in-window; no fresh GDN performance evidence.
- vLLM #58413 discussion confirms the Qwen3.8-27B + MTP + offload use case remains active, but no new measurement was posted.
- SGLang #40947 had no substantive fresh measurement in the exact window.
- Splash had no new M1/Apple7 code activity. A same-day M3/M5 community benchmark thread had follow-up discussion, but it is non-M1 and does not alter the canonical M1 target.
- IST-DASLab/GSQ GitHub had no in-window code/issue/PR activity. The official Flash-Next GSQ-RCO Hugging Face collection remains an older release rather than a fresh quality receipt.
- No precisely timestamped new ByteShape source-vs-quant behavioral result was found inside this boundary.

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

**2026-09-24 10:40:14 UTC**
