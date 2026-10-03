# Project 51 research watch — 2026-10-03 07:53 ET

Freshness boundary entering: **2026-10-03 11:00:49 UTC**
Cutoff: **2026-10-03 11:53:50 UTC**

## Decision

**No numeric target movement.**

Primary Windows state remains:
- Strata baseline: **0.1.38**;
- IQ3_S + native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**;
- #481-style automatic containment/no-manual-service-restart: **~85%**;
- native production context: **262,144**, with **204,800** first fallback;
- conversation parking OFF for initial certification;
- explicit `reasoning_budget_tokens` for high/xhigh;
- frozen residency for source/AA qualification.

This short window adds three durable correctness rules:

1. **Reasoning continuations need whole-request accounting, not last-segment cache counters.**
   Strata #615 shows a real continuation can report cached tokens larger than original input tokens and inflate
   client context accounting. Until merged/released, usage telemetry from budget-forced continuations is not a
   trustworthy PP/context-accounting source.

2. **Checkpoint retention is part of admission.**
   TensorFold #302 makes concurrent Flash-Next checkpoint-slot count explicit and charges it to the startup memory
   estimate. Project 51 should do the same: retained resume states are not free background metadata.

3. **Terminal/resume sidecars must not duplicate KV already owned by paged cache.**
   oMLX #4081's new aligned 128K two-worker follow-up removes exactly **8 GiB duplicated KV per snapshot**
   (8.1434 -> 0.1434 GiB sidecar) while preserving the completion-capacity result. This becomes an explicit
   Project-51 snapshot design rule.

No new exact M1-Max DASLab/ByteShape receipt, no exact RX6800 dense-27B PP receipt, no newer Strata release.

## NEW — Strata #615: reasoning-budget continuations can corrupt API usage accounting

PR:
https://github.com/Niko1221/Strata/pull/615

Created **2026-10-03 11:16:43 UTC**, open.

When a request hits `reasoning_budget_tokens`, Strata starts another native generation containing the original
prompt, generated reasoning and wrap-up text. Current accounting can combine:
- the original request's `prompt_tokens`;
- the continuation's cache count.

Observed application example:
- reported input: **181 tokens**;
- reported cached: **244 tokens**;
- client inferred 968 total tokens while API total was 905.

The patch:
- preserves first-segment input/cache counts;
- sums completed segments' generated-token, timing, draft and I/O counters;
- avoids double-counting a preceding segment when a continuation fails before a new DONE.

Validation reports 132 server/lifecycle/accounting tests passing plus eight live OMP checks on full Flash-Next IQ3_S.

Project-51 consequence:
- **do not use continuation-request usage counters as PP/context telemetry on current 0.1.38**;
- certification should compare server-native segment counters against API-level totals under forced reasoning-budget
  continuation;
- this is accounting correctness, not model/runtime throughput, so no TG/PP target move.

## NEW — TensorFold #302: checkpoint-slot count is explicitly part of concurrent Flash-Next admission

PR:
https://github.com/ashhart/TensorFold/pull/302

Created **2026-10-03 11:47:57 UTC**, open/draft.

Flash-Next concurrent decode previously hardcoded 8 kept prompt states. The new
`--checkpoint-slots N`:
- controls retained prompt states for parallel >= 2;
- feeds the same N into startup memory estimation;
- shrinks admitted context as N increases rather than letting retained state exceed budget;
- defaults to 8;
- one-stream mode continues to keep 4 and refuses the flag.

Synthetic fixed-budget admission test:
- N=1: **12,379 tokens**;
- N=8: **12,009**;
- N=16: **11,587**.

No CUDA hardware was run, so this is **architecture/test evidence**, not a physical capacity receipt.

Project-51 consequence:
- resident-agent/checkpoint count must be a first-class admission dimension;
- report `active_context + retained_checkpoint_bytes + cache/snapshot bytes`, not context alone;
- no multi-agent capacity credit from “checkpoint slots” until exact physical tests pass.

## UPDATE — oMLX #4081: aligned 128K completion confirms duplicated-KV sidecars are a major avoidable cost

PR:
https://github.com/jundot/omlx/pull/4081

Older PR, updated in-window.

New aligned follow-up on M3 Ultra 256 GB:
- 2 workers;
- **128,933 input + 2,139 output = 131,072 tokens** per worker;
- stock GA and the candidate both complete 2/2;
- candidate process peak: **172.60 -> 96.53 GiB** in the reported paired run;
- active Metal: **85.53 -> 67.24 GiB**;
- pool max: **85.37 -> 50.21 GiB**;
- elapsed: 205.51 -> 213.28 s, so **no speedup claim**.

The cleanest architectural datum:
- stock fresh terminal sidecar: **8.1434 GiB each**;
- candidate: **0.1434 GiB each**;
- exactly **8 GiB duplicated KV removed per snapshot**.

The broader process-memory drop belongs to a combined patch series, not solely this change, and coding quality remains
unqualified.

Project-51 consequence:
- snapshot/parking format must reference or serialize only state not already durably represented in paged KV;
- do not duplicate attention KV into every terminal sidecar;
- restore qualification still requires fresh-vs-resumed continuation equivalence;
- this directly strengthens the existing resident-agent capacity model but does not move M1 numerical targets.

## UPDATE — TensorFold #273: smaller usage-ranked draft vocabulary may beat a larger static superset

PR:
https://github.com/ashhart/TensorFold/pull/273

The PR itself enlarges Flash-Next's shipped draft subset from 79,591 to 80,014 ids and raises held-out code-shaped
coverage from ~99.30-99.60% to ~99.81-99.92%, with measured decode effectively neutral.

An in-window independent comment reports a different approach on GB10 / Flash-Next EXL3 4.05:
- frequency-ranked **40,960-id** draft list;
- preserves **98.8% of correct drafts**;
- MTP head lm_head: **1.54 -> 1.27 ms**;
- 15-case interleaved A/B: **+1.8% geometric mean**;
- household +2.4%, reasoning +4.3%, **code -1.8%**;
- 60/60 drafted replies equal serial.
- a 48K hybrid list preserving the shipped code tail is proposed as a better code-oriented compromise.

Project-51 consequence:
- do not blindly minimize draft vocabulary for the QA/coding lane;
- when we tune draft vocab, optimize **workload-weighted accepted-token/time**, with a protected code/tool token tail;
- existing `--draft-vocab en` idea remains experimental, not baseline.

## NEW — Strata #617 independently reinforces explicit reasoning budgets

Issue:
https://github.com/Niko1221/Strata/issues/617

Created **2026-10-03 11:51:09 UTC**.

V100-32GB / Strata 0.1.38 / Flash-Next IQ3_XXS field report:
- hard prompts with max_tokens=5K and 15K could consume the entire allowance in reasoning and return empty content;
- `reasoning_budget_tokens: 4000` forced the same spiraling seed to stop reasoning and produce an answer;
- on three hard problems, capped Flash and a 27B comparison under ~4K thinking caps had the same coarse correctness
  pattern in that small battery.

This is not a user-hardware performance transfer and the small capability battery is not a quality ranking.

Project-51 consequence:
- our existing rule stands: **high/xhigh always gets an explicit reasoning budget**;
- add “non-empty final answer after budget rollover” to agent soak tests.

## NEW — Strata #616: AVX2 i-quant codebook gather is real but only ~1% end-to-end

Issue:
https://github.com/Niko1221/Strata/issues/616

RTX A3000 + i7-12850HX / IQ3_XXS:
- AVX2 gather improves isolated IQ3_XXS/IQ3_S gate-up kernels ~**1.32-1.34x**;
- five interleaved end-to-end pairs: ~**+1.0%** mean;
- kept opt-in as `STRATA_IQ256_GATHER`.

Interpretation:
- confirms codebook lookup is a real single-core cost;
- pool concurrency/other stages absorb most of the local win;
- lower-byte pack format or GPU placement remains the larger lever.

No Project-51 target transfer.

## UPDATED / KNOWN items with no strategy change

- Strata #567 incremental prompt tokenization was updated in-window; the 100.9K synthetic result remains
  ~235 ms full encode vs ~1.5 ms incremental. Useful server overhead reduction, not model PP.
- Strata #525 unclosed-thinking tool-call rescue was updated; remains open and still belongs to the parser gate.
- TensorFold #144 ROCm GGUF branch updated; no new exact RX6800/gfx1030 receipt appeared.
- TensorFold #268 long-context 27B grouped tree-attention work was updated/closed unmerged; its existing GB10
  result remains ~5% faster drafted rounds at 90K and ~9-10% at 242K.
- TensorFold #252 EXL3 PLE read-ahead updated; cold-page behavior remains a file/page-residency result, not a
  Windows/M1 target transfer.
- oMLX #4081 still has an unqualified shared-activation patch path; do not promote the full series as a quality-safe
  production patch.

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- MTPLX;
- Splash;
- Ishizuki;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- TurboQuant;
- mlx-serve;
- DASLab/Hugging Face;
- ByteShape/public sources.

No Strata release newer than **0.1.38**.
No strict-window TurboQuant repository change.
No strict-window MLX-core PR/issue.
No strict-window MTPLX/Splash/Ishizuki change.
No new exact M1 Max 64-GB DASLab/ByteShape benchmark.
No new single-RX6800 dense-Qwen3.8-27B benchmark.
No evidence requiring a hardware purchase or target change.

## Target state after this pass

1. Primary Windows baseline: **Strata 0.1.38**.
2. IQ3_S/native262K physical fit: **~95%**.
3. Windows 16GB/64GB admission: **~90%**.
4. 8 h / 24 h zero-stall: **~75% / ~55%**.
5. #481 automatic containment: **~85%**.
6. Native context 262144; 204800 first fallback.
7. High/xhigh: explicit reasoning budget; validate final-answer rollover and API usage accounting.
8. PLE ladder unchanged: IQ4_NL -> FP8 production candidate -> BF16 exact control.
9. Single-M1 27B remains **25 TG / 110 cold PP**.
10. Primary dense artifact remains **DASLab IQ3_S-MTP**.
11. Custom M1 engine remains based on current MLX plus bespoke long-context multi-row verify/state lifecycle.
12. RX6800 remains an uncredited prefill-producer experiment pending exact PP + HIP->M1 bridge.
13. Resident-agent admission must explicitly include retained checkpoint count/bytes.
14. Snapshot/parking sidecars must **not duplicate paged KV**.
15. Draft-vocab tuning is workload-weighted; protect code/tool-tail coverage rather than minimizing vocab blindly.
16. No hardware purchase change.

## New hard boundary

**2026-10-03 11:53:50 UTC**
