# Project 51 primary-lane research watch — 2026-09-24 18:20 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 20:14:25 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 22:20:34 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

No exact dual-M1/TB4 Flash-Next S=2-8 verifier receipt appeared, no direct Apple7 PP2 overlap measurement appeared, and no new precisely timestamped DASLab/ByteShape source-vs-quant xhigh behavioral certification appeared.

This pass materially strengthens three architecture rules:
1. **hybrid recurrent state must be persisted at the exact cache boundary, not reconstructed approximately;**
2. **speculative overhead includes a large control/state-preparation layer outside the model forward that can be fused independently;**
3. **history/prompt lookup should be costed from live chip/model measurements, not hard-coded constants.**

## Findings

### NEW — oMLX #3908: exact split-GDN prefix state can be persisted correctly and cuts repeated static-prefix wall time by 72.8%

Source: https://github.com/jundot/omlx/pull/3908  
Created **2026-09-24 21:45:53 UTC**.

Qwen3.8-Flash-Next hybrid ArraysCache previously refused to persist exact split-GDN prefixes because the terminal recurrent state had no sidecar commit path. Reusing only KV blocks would be incorrect: the exact prefix also needs the terminal recurrent/GDN state.

#3908 adds:
- an exact-prefix checkpoint writer backed by the boundary snapshot SSD store;
- terminal recurrent-state extraction and commit under the terminal block hash;
- a dedicated hash domain for the entire split-GDN exact-prefix chain so intermediate placeholders cannot leak into ordinary partial-prefix matching;
- fail-closed behavior when no sidecar writer exists.

Real Qwen3.8-Flash-Next-oQ5e-mtp smoke test:
- cold request: **11.064 s**
- repeat: **3.013 s**
- restored static prefix: **13,526 tokens**
- wall-time reduction: **72.77%**

Validation reports **536 tests passed**.

**Classification:** NEW exact-family hybrid-state persistence evidence.

**P51 consequence:** persistent prefix identity must publish **target KV + terminal recurrent/GDN state as one semantic checkpoint**. Never treat ordinary KV reuse as sufficient for a hybrid model. Exact-prefix chains and partial-prefix chains should have separate identity domains when the intermediate recurrent frontier is not independently valid.

This is also strong evidence that correct recurrent-state persistence can make long static system/tool prefixes cheap in real agent loops without changing model math.

### NEW — SGLang #41166-#41175: exact Flash-Next speculative control/state overhead is decomposable into many independently optimizable pieces

Sources:
- https://github.com/sgl-project/sglang/pull/41166
- through https://github.com/sgl-project/sglang/pull/41175
- plus QSA preparation #40972

Created as a coordinated series beginning **2026-09-24 20:43 UTC**.

The series targets work surrounding Qwen3.8-Flash-Next NEXTN verification rather than the large model matmuls themselves:
- fuse small CUDA-graph input copies;
- reuse speculative-overlap batch snapshots;
- skip KV-allocation transfers when no pages are needed;
- fuse simulated-acceptance tensor preparation;
- fuse relay payload stores and remove single-request gathers;
- fuse GDN/convolution/PLE state commits across hybrid state pools;
- fuse greedy verification with argmax finalization;
- fuse QSA graph-replay metadata across draft steps;
- fuse Mamba tracking-index lookup;
- fuse NEXTN verify/draft graph input preparation.

Useful isolated microbenchmarks:
- small input-copy GPU work: **~11.0 -> 1.4 us** (but host eligibility/alias checks can grow ~7.7 -> 57.3 us, so no automatic E2E credit);
- CPU schedule-batch snapshot: **17.84 -> 6.23 us**;
- hybrid state commit at B1: **10.00 -> 5.63 us** without tracking, **10.88 -> 7.75 us** with tracking;
- greedy chain verification: **8.38 -> 4.50 us**.

Combined B200 x4 / TP4 / Qwen3.8-Flash-Next-NVFP4 integration benchmark:
- normal decode: **4.127 ms TPOT = 242.3 TG**
- NEXTN with 4 drafts and **simulated acceptance 3.3**: **1.694 ms TPOT = 590.4 TG**

That large E2E number **must not** be interpreted as a real observed speculative multiplier because the performance run uses simulated acceptance.

More relevant to P51 acceptance planning: on the combined real-thinking AIME26 validation with no acceptance simulation, weighted real MTP acceptance length was only about **2.146 including the bonus token**.

Accuracy:
- normal: **229/240 = 95.42%**
- NEXTN: **228/240 = 95.00%**
- thinking enabled; max 131,072 tokens.

**Classification:** NEW exact-family cross-hardware verifier/control-plane evidence.

**P51 consequence:** the measured verifier multiplier is not just “GPU ALU cost.” Host snapshots, state scatters, metadata construction, allocation transfers, graph-input preparation, relay gathers, argmax and QSA bookkeeping are individually attackable. This strengthens the P51 goal of measuring **target-forward-equivalent work plus non-forward control/state cost separately**.

But the **2.146 real-thinking acceptance** is also a caution: it is below the current ~2.4 conservative P51 useful-commit planning figure on this very different B200/AIME workload. Do not raise MTP assumptions from simulated 3.3 or from easy copy/coding workloads.

### UPDATE — mlx-serve #523: prompt lookup now uses measured per-chip/model round cost and survives default sampling

Source: https://github.com/ddalcu/mlx-serve/pull/523  
Fresh update at **2026-09-24 20:41:42 UTC**.

The prompt/history lookup gate no longer relies primarily on hard-coded M5-Ultra cost constants:
- MTP side reads the existing measured `round_cost.roundMs` for the current width;
- lookup rounds build their own runtime cost row;
- first lookup at a new draft count is excluded because it includes kernel compilation;
- persisted cost-table format remains unchanged.

On M5 Ultra / Flash-Next, the measured lookup-cost row closely matches the prior fit:
- k7 **31.1 ms measured vs 29.6 fit**
- k14 **49.7 vs 47.9**

Fresh server-default sampled A/B over the same 11 tasks:
- plain MTP lookup on: **~209-210 TG**
- off: **~179 TG**
- about **1.17x overall**
- copy tasks: **~261-266 vs ~197-198 = ~1.33x**
- with typical-0.2: **226.1 vs 184.3 = 1.23x overall**, copy **1.35x**
- lookup draft landing rate **~93.6-94.1%**

Example copy task:
- lookup: **72 rounds / 978 drafted / 971 landed**
- roughly **13.6 drafts per lookup round, 99.3% landing**

Example edit task:
- **70 / 871 / 832**
- roughly **12.4 drafts/round, 95.5% landing**

**Classification:** UPDATE / stronger exact-family Apple workload-selective speculative evidence.

**P51 consequence:** controller decisions should be based on **measured landed tokens per measured current cost** for each mechanism: target-only, MTP, and history/prompt lookup. Hardware/model/context-specific cost tables are preferable to fixed constants. History lookup remains opportunistic upside, not part of the generic 40-TG denominator.

### UPDATE — independent M1 Ultra Apple7 Splash run: strong short-context headroom, clear 32K depth decay

Source: https://github.com/incoai/splash/issues/131#issuecomment-5822722639

Independent setup:
- **M1 Ultra, 48 GPU cores, 128 GB**
- Apple7 branch `d2f902e`
- Qwen3.8-27B Splash
- 32K max context.

Short decode:
- technical: **50.0 TG**
- Python: **64.7**
- TypeScript: **43.6**
- repeat: **98.3**
- reasoning effort low/medium/xhigh on the selected math prompt: **63.8 / 65.5 / 67.0**

Depth:
- ~2K: **202 PP / 31.6 TG**
- ~8K: **197 PP / 33.2 TG**
- ~31.95K: **161 PP / 21.2 TG**
- cached 31.95K prefix TTFT: **0.46 s**

Parallel aggregate:
- B1 **48.2**
- B2 **65.7**
- B4 **73.5 TG**

Output remained coherent in the report.

**Classification:** UPDATE / independent Apple7 scaling evidence.

**P51 consequence:** reinforces both sides of the Apple7 story:
- short-context custom-kernel headroom is very real;
- deep-context decode can fall sharply even when short xhigh looks spectacular.

Therefore never use short Apple7 TG as a proxy for filled-128K P51 throughput. Context-depth curves remain mandatory.

### UPDATE — oMLX #3901 production follow-up: warm MTP restoration is fast, but restart chains need explicit bootstrap

Source: fresh #3895 comment at **2026-09-24 18:41:18 UTC**.

Already recorded core result is independently production-confirmed:
- before full sidecar restore: **2.34-2.47 tok/cycle, 71-74% acceptance**
- after: **3.62-3.92, 97-100%**
- warm restored backbone cost **26.3 ms/cycle**
- natural path **26.2 ms/cycle**
- one-shot reconstruction **12-50 ms/request**

Newly isolated restart issue:
- MTP sidecar is memory-only;
- after restart, target SSD prefix restores without MTP history;
- the warm suffix-only path never satisfies the current capture condition;
- repeated future warm hits can remain degraded indefinitely.

**P51 consequence:** if draft/MTP history is not persisted, the runtime must explicitly **re-bootstrap it once after target-state restore**, then publish a new compatible frontier. Warm caches must self-heal after process restart.

### KNOWN / CLOSE-OUT — oMLX #3770/#3771

Both older regression issues were closed in-window:
- #3770 base no-cache decode regression is resolved by the previously recorded fix stack;
- #3771 fused GDN verify prework now engages on current Flash-Next builds at S=3 with l2 normalization.

No new P51 planning conclusion beyond already durable state.

### LOWER PRIORITY — vLLM #58485 confirms sampler semantics remain a speculative-decoding correctness axis

Fresh discussion shows the V2 runner correctly handles multi-token reasoning-end sequences across a speculative window; the older V1 path can still be reached by some fallback speculative methods.

**P51 consequence:** already covered by the target-sampler/admissibility rule. No state change required.

## Quant / community search

- **ISTA-DASLab/GSQ:** no in-window GitHub activity.
- **ByteShape:** no precisely timestamped new Flash-Next source-vs-quant behavioral receipt inside this strict interval.
- The same-day 12-GB CUDA custom-engine post reports very high 128K numbers on low-bit GSQ/RCO-family quants, but the public search surface exposes only "today" rather than a precise publication timestamp. It remains outside this strict delta.
- No new exact dual-M1/TB4 receipt was found.

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
- single-M1 27B: **25 TG** canonical target; Apple7 + heterogeneous quant + verifier co-design remains an experimental upside lane.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 22:20:34 UTC**
