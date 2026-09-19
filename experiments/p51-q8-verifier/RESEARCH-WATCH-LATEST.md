# External runtime watch — 2026-09-19 11:55 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-19 11:04:27 UTC` through `2026-09-19 15:55:17 UTC`.

PRs, issues, comments/reviews, and default-branch commits were screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. The currently relevant Splash, MTPLX, Kadir benchmark/fork repos, plus fresh Qwen3.8-Flash-Next Hugging Face/community/web surfaces, were also checked. Evidence time means the substantive source/measurement timestamp, not crawler, merge, rebase, label, or bot timestamps.

## Executive result

**No exact dual-M1-Max/TB4 custom-quant Flash-Next receipt appeared. Canonical numeric targets do not change.**

Current Flash-Next plan after the recovered Splash confidence update:
- **40 TG sustained @ ~128K: ~65%**
- **400 cold PP: ~70%**
- deployment design: **custom ~4.6-4.9 hot-trunk BPW**
- oQ5e: quality/certification comparator
- oQ4e: aggressive speed comparator
- PLE/ngram and MTP precision tracked separately.

The strongest strict-window finding is an exact diagnosis of the oMLX Flash decode regression from the prior watch. It was a **lost fast-path eligibility bug plus hot-loop environment lookups**, not a new hardware/runtime ceiling. A second important Metal finding shows that fusion can reduce performance by destroying graph concurrency even when fusion counts are unchanged.

No TG/PP confidence move is warranted: these findings mostly remove software regressions or strengthen qualification rules rather than provide a new target-topology speed receipt.

## NEW — oMLX #3760 restores the Qwen3.8-Flash-Next decode regression

Created **2026-09-19 13:50:36 UTC**.

Model / hardware:
- Qwen3.8-Flash-Next-oQ4e-mtp
- M3 Ultra
- MTP OFF
- same prompts / serving path as #3755.

### Root cause

A mlx-vlm upgrade caused quantized projections to be reclassed as `_VLMQuantizedPrefillLinear`.

The Qwen4 fused B1/T1 GDN decode gate used exact type identity:

`type(linear) is nn.QuantizedLinear`

so subclasses no longer qualified.

Result:
- all **36 GDN layers** fell off the fused decode-prework/norm-gate path;
- the server stopped logging that the fused path was engaged;
- the wrapper also read four environment variables per projection call, producing roughly **470 getenv-style reads per generated token** across ~230 projection calls.

The PR:
1. accepts `nn.QuantizedLinear` subclasses for fused-decode eligibility;
2. hoists routing thresholds/environment values out of the projection hot loop.

### Exact measured recovery

Flash-Next oQ4e, MTP off:

| Prompt | dev4 main | #3760 | older dev2 |
|---|---:|---:|---:|
| 4K | 45.8 / 48.1 TG | **51.8 / 51.7** | 51.9 / 52.4 |
| 16K | 42.6 / 45.0 | **48.2 / 48.5** | 49.1 / 49.3 |

The fix therefore essentially restores the prior performance.

A matched Qwen3.6-35B-A3B-oQ6 test also recovers smaller losses:
- 4K: 87.6/87.7 -> 88.9/89.7
- 16K: 79.6/79.5 -> 81.0/81.5.

Classification: **NEW exact Apple / exact Flash-family runtime diagnosis; stronger Apple hardware and short/medium context, not target M1/TB4 evidence.**

### Project 51 rule

Fast-path identity must be observed, not inferred from source intent.

Every performance receipt should record:
- resolved wrapper/projection class;
- fast-path engagement counters;
- selected kernel/plan family;
- hot-loop configuration/environment reads when relevant.

A wrapper/reclass/library upgrade can silently turn off optimized execution while preserving numerics and nominal backend labels.

Target effect: **none**. This restores lost software performance rather than raising the known ceiling.

## NEW — llama.cpp #29134: fusion packing can destroy Metal concurrency

Created **2026-09-19 14:02:43 UTC**.

Hardware/model:
- M2 Ultra 128 GB
- Gemma-4-26B-A4B Q4_K_M
- Metal.

A prior fusion-table refactor changed decode from roughly:

- last good: **85.17 TG**
- first bad: **79.35 TG**
- current affected build: ~79.1 TG

while prompt processing was not harmed.

The important diagnosis is that **the same fused kernel patterns still matched**. Fusion counts were unchanged.

What changed was structural packing:
- old path packed one fused-kernel pattern at a time;
- new path chained adjacent patterns into one structural pack;
- independent dense/MLP and MoE branches became glued together;
- concurrent nodes per decode graph fell **720 -> 662**.

Disabling concurrency makes both builds essentially equal:
- ~71.24 vs 71.16 TG.

Packing exactly one pattern per structural pack restores:
- **85.02 TG**
- concurrent nodes back to **720**
- later PP improvements retained.

### Direct Flash negative control

On Qwen3.8-Flash-Next UD-Q3_K_XL, the proposed packing fix is essentially neutral:
- TG: **36.46 -> 36.77**
- PP: **654 -> 656**
- fusion counts, including GDN+CPY, unchanged.

Classification: **NEW exact Metal concurrency/fusion evidence; direct Flash negative control but different Apple hardware/quant/context.**

### Project 51 rule

“More fusion” is not automatically faster.

Every fusion A/B should record:
- fusion count/pattern identity;
- structural pack boundaries;
- number of nodes/commands eligible for concurrency;
- GPU overlap/busy fraction where available.

A fusion can save launches yet lose end-to-end TG by shrinking scheduler/reorder freedom.

This is particularly relevant after the newly merged qwen4exp fusion work: evaluate the final graph schedule, not just individual fused-kernel microbenchmarks.

Target effect: **none**. The direct Flash control is neutral.

## NEW — vLLM #57701: sparse-indexer scratch must be sized to effective pooled length

Created **2026-09-19 15:24:42 UTC**.

GLM5.3 sparse indexer / KeyPool uses:
`max_pool_len = max_model_len // index_kpool`

with `index_kpool=4`.

The old path sized decode-logit workspace to raw `max_model_len`, despite the actual sparse indexer operating on the compressed pool.

Measured workspace effect:
- 16,384: no change, 512 MiB floor dominates
- 65,536: no change, 512 MiB floor
- 262,144: **1024 -> 512 MiB**, saves 512 MiB
- 1,048,576: **4096 -> 1024 MiB**, saves **3072 MiB**

Kernel latency is essentially unchanged and the compared output slice is bit-identical.

Classification: **NEW non-Apple sparse-indexer memory evidence; transfer mechanism is strong, performance transfer is not.**

Project 51 action:
audit QSA/indexer workspace dimensions against:
- selected/pooled sequence length;
- active top-k budget;
- actual verify width;
- physical page count;

rather than allocating from nominal maximum context whenever the kernel never observes that full dimension.

This could be useful capacity headroom for our custom quant/MTP buffers, but no M1 byte saving is assumed until the actual QSA implementation is profiled.

## NEW — DS4 #1092 / #1093: visible tool-turn checkpoints prevent huge repeated prefill

Created **2026-09-19 12:29-12:30 UTC**.

Model/hardware:
- GLM-5.3-Flash Q2
- M4 Max
- ctx 393,216
- MTP ON
- long agent/tool session.

Problem:
after a tool call, the client replays the assistant/tool surface without the generated reasoning block. The server cleared the live checkpoint, and compressed sparse/recurrent state could not be safely rolled back by ordinary token truncation.

One controlled mechanism probe:
- before patch: follow-up from older disk block, **765 tokens re-prefilled / 4.2 s**
- after visible checkpoint: **84 tokens / 1.2 s**.

The production symptom was much larger:
- live frontier ~50,747
- fallback block ~20,536
- ~30K tokens re-prefilled
- roughly **100 s** repeated work.

Caveat: the one before/after arm generated different amounts of reasoning, so the exact factor is not treated as a controlled throughput result.

Classification: **NEW agent-cache/state-lifecycle evidence; different model/hardware.**

Project 51 action:
for tool-using clients, checkpoint identity must match the **visible replay surface**, not only raw generated token history.

Qualification must include clients that:
- omit private reasoning;
- replay only visible tool-call text;
- edit/compact reasoning;
- resume from a live prefix after tool execution.

This belongs alongside recurrent-state provenance and prefix-cache correctness gates.

## NEW — oMLX #3761: ANE prefill acceleration can regress generation and total latency

Created **2026-09-19 13:56:37 UTC**, detailed measurements posted **15:30 UTC**.

Hardware/model:
- M5 Pro 64 GB
- Qwen3.8-27B-4bit
- DFlash2
- three alternating pairs
- 128 generated tokens.

Means:

| Prompt | ANE | PP | TG | Total |
|---|---|---:|---:|---:|
| 4K | off | 513.9 | 35.9 | 11.568 s |
| 4K | on | 454.1 | 36.3 | 12.669 s |
| 8K | off | 493.7 | 39.6 | 19.845 s |
| 8K | on | 536.5 | 35.1 | 18.934 s |

Interpretation:
- 8K PP **+8.7%**, TG **-11.4%**, total request time **-4.6%**
- 4K PP **-11.6%**, total request time **+9.5%**
- ANE adds ~**3.83 GB** peak memory.

The author explicitly says the divergent 4K/8K behavior needs independent verification.

Classification: **NEW exact Apple 27B transfer evidence, not Flash target evidence.**

Project 51 action:
phase-local accelerators must be judged on:
- PP
- subsequent TG
- peak memory
- end-to-end request time

because extra banks/residency or dispatch changes can improve one phase and hurt another.

No 27B target change.

## RECOVERED OLDER EVIDENCE — sparse-QSA keeps Flash decode flat at 116K-148K on CUDA

Fresh community search recovered a Reddit post with source timestamp **2026-09-19 05:05:20 UTC**, which is **older than the prior 11:04:27 UTC hard boundary**. It is therefore not strict-window NEW.

Setup:
- RTX PRO 4500 Blackwell 32 GB
- 64 GB system RAM
- Qwen3.8-Flash-Next UD-Q3_K_XL (~90 GB)
- MTP OFF
- 16 routed-expert layers GPU / 32 CPU
- PLE disk-backed mmap
- experimental block-sparse QSA with persistent block-key cache.

Real agent workload:
- 35 requests
- ~23K generated tokens
- context **116K -> 148K**
- token-weighted decode **27.9 TG**
- context buckets:
  - 115-125K: 27.7
  - 125-135K: 28.5
  - 135-148K: 27.5.

Prompt chunks were ~150 PP, peak 201; prefix cache hit rate ~99%.

The author attributes the flat long-context TG to sparse QSA and persistent block-key caching.

Additional A/B at ~49K prompt / 65K context:
- F16 KV: **38.1 TG**
- Q8_0 KV: **33.4 TG**
- PP essentially tied: 496 vs 499
- Q8 saves ~808 MiB.

The author explicitly notes:
- sparse-QSA patch is experimental/unreviewed;
- long-context correctness vs dense reference has not been fully certified;
- workload is warm-cache and not a controlled benchmark.

Classification: **RECOVERED mechanism evidence only, non-Apple and aggressive quant.**

Project 51 implications:
- sparse selected-QSA can structurally flatten context-depth cost;
- KV quantization is not automatically “free” even when PP is unchanged;
- Q8 vs higher-precision KV should be an empirical speed/fit/quality choice for our final custom quant.

No numeric target effect.

## STRICT-WINDOW negatives / checked surfaces

- No exact 2x M1 Max / TB4 Qwen3.8-Flash-Next TG or PP receipt.
- No new qualifying M1 Max Flash receipt.
- No new substantive commit in oMLX, DS4, mlx-serve, Splash, MTPLX, Kadir's qwen38-mac-fast repo, or Kadir's llama.cpp fork during the strict window.
- llama.cpp #29110 (small-row Metal MTP verify kernel) received no new M1 measurement before cutoff.
- The vLLM sm_120 persistent-matmul PR merged during the window, but its substantive measurements were already captured in an earlier Project 51 pass; merge time is not new evidence.
- Fresh Hugging Face/community searching did not surface a new exact dual-M1/custom-quant receipt.
- MTPLX/Splash headline Apple numbers remain prior evidence; no new source commit in this strict window changes their qualification.

## Target / confidence decision

**No change.**

Flash-Next dual-M1:
- >=35 TG @ ~128K: **~85%**
- **>=40 TG @ ~128K: ~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20%**
- **400 cold PP: ~70%**.

The strict-window findings improve our ability to avoid false regressions and wasted memory, but they do not add a new physical target-topology throughput receipt.

## New/strengthened qualification rules

1. **Resolved fast-path engagement is benchmark identity.** Record selected kernel/plan counters after wrapper/runtime changes.
2. **No configuration lookup in hot projection loops.** Resolve environment/config values once unless dynamic behavior is intentionally required.
3. **Fusion qualification includes concurrency.** Kernel fusion counts without graph overlap/concurrency metrics are insufficient.
4. **Sparse scratch uses effective dimensions.** Size QSA/indexer workspace from selected/pooled/active geometry, not raw context ceiling.
5. **Agent checkpoint keys follow visible replay semantics.** Test reasoning-omitting tool clients.
6. **Phase-local speedups require end-to-end checks.** PP improvements can regress TG or total latency through memory/residency effects.
7. Existing component-wise quant, exact-state provenance, distributed geometry, MTP acceptance, long-context parity and state-isolation gates remain.

## Hard freshness boundary

`2026-09-19 15:55:17 UTC`
