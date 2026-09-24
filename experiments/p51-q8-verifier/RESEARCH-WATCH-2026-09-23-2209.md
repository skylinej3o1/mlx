# Project 51 primary-lane research watch — 2026-09-23 22:09 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 00:32:47 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 02:09:05 UTC**. One materially useful older source missed by the previous delta is separately marked **RECOVERED OLDER EVIDENCE** rather than misclassified as new.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No new exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared. No new DASLab / GSQ-RCO xhigh behavioral-quality result appeared.

The strongest fresh evidence is:
1. an exact-family Apple runtime win that removes one dependent GDN dispatch per layer from Flash-Next plain decode and improves M5-Ultra decode by about 3.9%;
2. fresh production evidence that application-directed recurrent checkpoints can more than double throughput on a high-reuse hybrid workload, while the upstream PR is now explicitly held pending architectural consensus;
3. a newly merged Qwen3.8-Flash-Next ROCm QSA sparse-decode path whose existing full-stack data show 936 -> 1603 output tok/s with MTP/EAGLE and 3.16 average acceptance;
4. confirmation that deleting host metadata work can be correctness-clean yet throughput-neutral when it is not on the critical path.

These sharpen implementation priorities but do not justify changing 40/400 or the ~70% planning confidence.

## Findings

### NEW — mlx-serve #517: one fewer dependent GDN dispatch per layer gives ~3.9% Flash-Next plain-decode gain on M5 Ultra

Source: https://github.com/ddalcu/mlx-serve/pull/517  
Created: 2026-09-24 02:08:02 UTC.

Flash-Next and 27B non-Hadamard packs were still paying three dependent GDN dispatches per layer: prework, recurrence, and norm-gate. The new path combines prework + recurrence, reducing the chain to two dispatches per layer.

For Flash-Next this removes **612 ops per forward**.

M5 Ultra 256 GB, macOS 27.0, Flash-Next mixed 4/8-bit, MTP off:
- plain decode A-B-B-A: **90.9 / 90.9 tok/s** vs **87.7 / 87.3 tok/s** with the new path disabled, about **+3.9%**;
- 16K context: **81.2 / 81.4 tok/s** vs **78.5 / 78.2 tok/s**, roughly +3.7-4.0%;
- forward microbench: **12.57 ms** vs **13.03 ms**;
- 300 greedy output tokens: byte-identical.

On 27B 4-bit / M5 Max the same change removes 816 ops/forward and preserves greedy output, but the PR does not provide a decode-rate A/B for that machine.

The PR explicitly says this does **not** touch the verify path, so MTP cells do not move.

**Classification:** NEW exact-model-family Apple transfer evidence, stronger-generation hardware.

**P51 consequence:** directly validates the project strategy of eliminating dependent GDN dispatches one stage at a time. It is encouraging for Apple-hosted Flash, but M5 Ultra dispatch economics differ from Apple7/M1 and this optimization affects target-only decode, not verifier cost. No direct 128K/M1 multiplier transfer.

### UPDATE — vLLM #55697 / #55876: application-directed recurrent checkpoints show large production benefit, but the implementation is on hold for complexity

Sources:
- https://github.com/vllm-project/vllm/issues/55697
- https://github.com/vllm-project/vllm/pull/55876

Fresh RFC comment at 2026-09-24 01:12 UTC adds production-scale results for Qwen3.5-35B on L40S / MRv2 in a high-reuse 1-to-N workload with an application-marked semantic checkpoint boundary.

Reported production result:
- serving throughput: **5.9 -> 13.8 QPS** (**2.34x**, +133.9%);
- TTFT: **482 -> 248 ms** (-48.6%);
- prefill compute: ~**11,500 -> 5,358 tokens/batch**;
- GSM8K 5-shot exact match: **0.8522 vs 0.8522**;
- 3,428 production request pairs: **0.9991 Pearson**, **99.94% prediction consistency**, **0.00% significant difference >=0.1**.

The workload has a shared ~624-token multimodal premise and divergent 350-650-token suffixes. The application marks the scarce recurrent checkpoint at the semantic boundary rather than asking the runtime to infer it.

Important governance update: a maintainer put #55876 on hold and asked for architectural RFC approval first, citing implementation complexity. The author agreed to pause the PR stack.

**Classification:** UPDATE / fresh production evidence on an older hybrid-checkpoint design.

**P51 consequence:** strongly supports explicit semantic checkpoint placement for warm agent/repeated-prefix workloads where recurrent state is too large to checkpoint densely. It does **not** improve cold PP and should not be folded into the 400-PP target. The upstream maintainability concern is also relevant: P51 should keep checkpoint identity/restore machinery small and architecture-local rather than spreading special cases across the scheduler.

### UPDATE / newly merged older evidence — SGLang #38876: packed QSA sparse decode for Qwen3.8-Flash-Next on ROCm

Source: https://github.com/sgl-project/sglang/pull/38876  
Merged commit: 8b5d77c2688e at 2026-09-24 01:59:17 UTC.

The implementation itself and its benchmark data predate this freshness window, so this is **not new performance evidence**. The fresh event is merge into SGLang.

The patch gives ROCm a graph-safe packed sparse-QSA decode path for Qwen3.8-Flash-Next. It avoids a host sync during HIP graph capture by using a fixed decode query length of one after selected K/V rows have already been compacted into contiguous request segments.

Existing full-enablement data on 8x MI355X / released BF16 Flash-Next:
- BF16 baseline output throughput: **936 tok/s**;
- BF16 + EAGLE MTP: **1603 tok/s**;
- average accept length: **3.16**;
- GSM8K 200-example score: **0.980 baseline vs 0.975 MTP**.

That is roughly **1.71x output throughput** on the reported serving configuration. The same PR verifies an 18K-token prompt beyond indexer_budget=2048, HIP graph replay, and image+text sparse decode.

**Classification:** UPDATE / merge-status change with older exact-family cross-hardware benchmark evidence.

**P51 consequence:** exact-family evidence continues to support meaningful speculative uplift when QSA sparse decode and MTP are implemented cleanly. Because this is MI355X, multi-GPU, short-benchmark throughput with older data, it receives no Apple/128K numerical credit. The newly merged graph-safe packed-QSA design is a useful implementation reference for keeping the sparse-decode path capture-safe.

### RECOVERED OLDER EVIDENCE — vLLM #58463: removing ~1 ms of MTP host metadata work produces essentially zero throughput gain

Source: https://github.com/vllm-project/vllm/pull/58463

This PR was created before the prior hard boundary; its only activity inside the current window was CI retry, so it is **not new**. It was not preserved in the previous durable state and is useful enough to recover explicitly.

DeepSeek-V4-Flash + MTP3 on 4x GB200 removes the first eager draft-attention metadata rebuild before fused multi-step drafting, eliminating about **1 ms of host work per decode step**.

End-to-end:
- C1 ITL: 8.97 -> 8.97 ms; output 290.3 -> 288.3 tok/s;
- C16 ITL: 19.13 -> 19.15 ms; output 1806.7 -> 1819.4 tok/s;
- C64 ITL: 22.96 -> 22.96 ms; output 4415.5 -> 4380.6 tok/s.

The authors conclude the removed millisecond is not on the critical path at TP4; observed throughput differences track tiny acceptance variation/noise.

**P51 consequence:** host-work deletion only deserves TG credit after critical-path profiling. On Apple, dependent dispatch can still matter greatly (#514/#517), but generic CPU metadata time should not be assumed to translate one-for-one into token latency.

### UPDATE / operational — oMLX #3883 fix merged

Source: https://github.com/jundot/omlx/issues/3883  
Merged commit: 15941566dec0 at 2026-09-24 01:23:42 UTC.

The prior watch recorded that offline cache accounting/purge omitted GDN sidecars, which could dominate persistent bytes. That fix is now merged.

**P51 consequence:** no target change; reinforces that recurrent sidecars must participate in ordinary observability, purge and lifecycle management rather than living as hidden auxiliary storage.

### WATCH ONLY — vLLM #58484 reverts DSpark PP target support pending cleanup

Source: https://github.com/vllm-project/vllm/pull/58484

An in-window PR proposes reverting aggregated-serving pipeline-parallel target support for DSpark, saying the earlier change "needs some more cleanup." No reproducer, performance data or structural root cause is provided.

**P51 consequence:** track as a reminder that speculation + PP integration remains implementation-fragile, but there is not enough evidence here to infer a fundamental PP2 limitation or change target confidence.

## Community / quant search

A same-day Reddit result surfaced a Qwen3.8-Flash-Next Q4/MTP report claiming roughly **16.5 TG and 350 PP at ~131K** on an RTX 4080 / host-memory setup, but the search surface does not expose a sufficiently precise publication timestamp to prove it falls after the **00:32:47 UTC** hard boundary. It is therefore **not promoted** into this delta or canonical planning state.

No fresh controlled post-boundary source-vs-quant xhigh behavioral certification was found. No new DASLab/GSQ repository activity appeared.

## Checked surfaces / negative results

- **antirez/ds4:** no issue, PR or commit activity in-window.
- **IST-DASLab/GSQ:** no issue, PR or commit activity in-window.
- **oMLX:** relevant fresh activity is operational/cache and converter fixes; no new Flash-Next/M1 throughput receipt.
- **mlx-serve:** #517 is the material exact-family Apple item; #516 only adds decode-graph observability.
- **llama.cpp:** no new exact M1/TB4 Flash throughput receipt. #29340 received only a test-coverage discussion in-window.
- **vLLM:** #55697/#55876 production-checkpoint update is material; #58463 is recovered older evidence; #58484 is watch-only.
- **SGLang:** #38876 merge is the material exact-family event; the benchmark itself predates this window.

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
- single-M1 27B: **25 TG**.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 02:09:05 UTC**
