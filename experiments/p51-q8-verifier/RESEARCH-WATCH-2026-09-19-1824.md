# External runtime watch — 2026-09-19 18:24 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-19 18:44:41 UTC` through the user-message cutoff `2026-09-19 22:24:30 UTC`.

PRs, issues, comments/reviews, commits, releases and current community/benchmark surfaces were screened across DS4, vLLM, oMLX, mlx-serve, llama.cpp, Splash, Kadir's qwen38-mac-fast/fork, and current Qwen3.8-Flash-Next quant/community work. Evidence timestamp means the substantive source/measurement timestamp, not crawler, merge, rebase, label, or bot time.

## Executive result

**No exact dual-M1-Max/TB4 custom-quant Flash-Next TG or PP receipt appeared. Numeric targets and confidence remain unchanged.**

Current Flash-Next plan remains:
- >=35 TG @ ~128K: **~85%**
- **>=40 TG @ ~128K: ~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20%**
- **400 cold PP: ~70%**
- deployment design: **custom ~4.6-4.9 hot-trunk BPW**
- oQ5e: quality/certification comparator
- oQ4e: aggressive speed comparator
- PLE/ngram, MTP and KV precision tracked separately.

The strongest strict-window result is oMLX #3594's new **1M-context Qwen3.8-Flash-Next** packed-KV implementation on M5 Max 128 GB. It is valuable because it separates the QSA indexer's selection state from compressed K/V payloads, preserves sparse selection semantics, and demonstrates that long-context MTP priming must be bounded as its own memory transient. It does **not** establish M1 kernel portability or dual-M1 throughput.

The most important scheduler result is recovered oMLX #3695 multi-request Flash MTP: MTP materially helps at B1/B2 but its incremental benefit collapses by B4. That supports the existing Project 51 plan to treat ordinary batching, singleton MTP and batched MTP as dynamically competing policies.

## NEW — oMLX #3594 / 2b8bd078: 1,004,168-token Flash on M5 Max 128 GB

Source: https://github.com/jundot/omlx/pull/3594  
Strict-window commit: https://github.com/jundot/omlx/commit/2b8bd0783d3759490b932c42aab4a78366485507  
Commit timestamp: **2026-09-19 21:50:56 UTC**.

The commit is a squash of a TurboQuant/QSA campaign for Qwen3.8-Flash-Next and reports:

- hardware: **M5 Max 128 GB**
- prompt: **1,004,168 tokens**
- prefill: roughly **950-1250 tok/s**
- packed K/V residency: about **14 GB**
- dense fp16 K/V comparison: **28+ GB**
- memory-guard rejections: **0**
- needle ladder: 300K/500K single-needle and 750K/1M three-needle all PASS
- packed-window recall: markers written under an approximately **870K-token packed window** recalled successfully.

The design keeps:
- **K/V payload packed at 4-bit TurboQuant**
- **QSA indexer sidecar dense**: raw keys, positions and pooled block bank remain unquantized
- block selection therefore does not read quantized state
- gathered prefill/decode/MTP verify arms read packed selected rows directly rather than dequantizing the whole context.

The commit explicitly says **only 4-bit TurboQuant is functional/qualified** for this path.

### Agentic / cache evidence

A 900K agentic suite reports:
- **41 warm turns**
- per-turn TTFT roughly **17-35 s**
- MTP prompt priming bounded to roughly **20-24K folded tokens per turn**
- system-prompt or early-summary invalidation forced a full cold refill of about **888K tokens at ~1020 tok/s**
- all markers recalled
- warm control resumed at **99.9% cached tokens**
- warm control TTFT was **59x lower** than the cold invalidated case.

The tested production setting includes:
- `max_context_window=1010000`
- TurboQuant KV 4-bit
- `turboquant_skip_last=true`
- optional MTP
- **`mtp_prime_window=65536`**
- PLE SSD offload.

### Important limitation for Project 51

B>1 packed batching is **not solved** by this commit. The commit says concurrent requests serialize at admission; a dense-merge fallback remains behind an opt-in path with known MTP late-join issues.

Classification: **NEW stronger-Apple architecture/capacity evidence; not exact M1/TB4 evidence.**

### Project 51 action

1. Treat **QSA indexer precision and selected-K/V precision as separate quantization domains**.
2. For long-context capacity experiments, test 4-bit KV while keeping block-selection/indexer state at higher precision.
3. Track MTP prompt priming as an independent memory transient and cap it separately from target context.
4. Do not extrapolate the 950-1250 PP figure to M1; M5 Max compute/bandwidth and the 1M path are different.
5. Packed-KV B>1 must pass the same ragged-row cache gates before receiving any PP2/aggregate credit.

Target effect: **no numeric change**.

## RECOVERED OLDER EVIDENCE — oMLX #3695 multi-request Lightning MTP on Flash

Source: https://github.com/jundot/omlx/pull/3695  
Merged 2026-09-16; surfaced in the current pass via dev4/release and multi-row follow-up work. This is **older evidence**, not strict-window NEW.

Hardware/runtime:
- Apple **M3 Ultra 512 GB**
- MLX 0.32.2
- oQ4e model bodies
- fresh caches
- auto MTP depth
- long Python prompts
- temperature 1 / top_p 0.95 / top_k 20
- whole-response aggregate medians, including prefill, calibration, parking and smaller-batch tails.

Qwen3.8-Flash-Next-oQ4e-mtp:

| concurrency | non-MTP aggregate | MTP aggregate | MTP change |
|---:|---:|---:|---:|
| B1 | 54.12 | **82.98** | **+53.3%** |
| B2 | 71.74 | **96.32** | **+34.3%** |
| B3 | 95.51 | **107.45** | **+12.5%** |
| B4 | 111.14 | **116.47** | **+4.8%** |

This is strong evidence that multi-row MTP can coexist with ordinary batching on Apple Silicon, but also that the marginal benefit of speculation can collapse rapidly as plain batching fills the machine.

Classification: **RECOVERED stronger-Apple scheduler evidence.**

### Project 51 rule

For Hermes/multi-agent load, measure and choose among:
- plain target batching
- singleton MTP with queued independent work
- fused/batched MTP
- dynamic MTP parking/disable.

Do not assume MTP is additive with B2-B4 occupancy.

No M1 B2-B4 target move because this is M3 Ultra, not M1/TB4.

## NEW design correction — oMLX #3533 ragged rollback must decide before mutation

Source comment: https://github.com/jundot/omlx/pull/3533#issuecomment-5744722985  
Timestamp: **2026-09-19 19:31:37 UTC**.

The fresh comment identifies two ordering hazards in fused multi-row MTP:

1. test whether every cache supports ragged rollback **before** target verification mutates shared state;
2. determine each row's actual emitted length, including stop/length truncation, **before** constructing the per-row rollback vector.

The proposal avoids:
- a fallback after the cache has already advanced;
- extracting cache rows that contain candidate tokens never emitted;
- a BAIL/retry loop that can become slower than plain batching.

The commenter explicitly says they **have not run this branch**, so this is a design proposal, not a measured speed result.

Classification: **NEW planning/correctness mechanism, unmeasured.**

Project 51 rule: speculative fallback eligibility must be resolved before shared-state mutation; rollback length is the emitted length, not merely the verifier's accepted length.

## NEW — oMLX #3767 exposes scalar-trim failure under batched speculative rollback

Source: https://github.com/jundot/omlx/issues/3767  
Created **2026-09-19 20:07:04 UTC**.

M5 Max 128 GB / oMLX dev4 / Qwen3.8-27B-oQ4e-fp16-mtp:
- TurboQuant 4-bit + multi-request Lightning MTP
- 3 concurrent: **0/3 succeed**
- 4 concurrent: **0/4 succeed**
- TurboQuant disabled: **3/3 and 4/4 succeed**.

The failure occurs because `TurboQuantKVCache.trim()` treats a per-row offset array as a scalar during speculative rollback.

Important control:
- **Qwen3.8-Flash-Next-oQ4e-mtp with TurboQuant 4-bit + MTP handled 4 concurrent requests 4/4** in the same report.

This is not a Flash failure, but it is a concrete illustration of the cache contract Project 51's multi-row path must enforce.

Durable rule:
- trim/rollback/finalize must accept row vectors when the batch is ragged;
- late-join mask/key lengths must be checked before rollback;
- do not silently call a scalar cache primitive on a multi-row speculative state.

No target effect.

## NEW — vLLM #57716: PP2 speculative verify can propagate poisoned cache bytes through masked attention

Source: https://github.com/vllm-project/vllm/issues/57716  
Created **2026-09-19 21:09:02 UTC**.

Reported environment:
- 2x B200 systems / **TP8 x PP2**
- Kimi-K3
- DSpark, 7 speculative tokens, block rejection
- hybrid recurrent + MLA architecture
- fp8 latent KV
- concurrent long generations.

The reporter says the failure reproduced on three detached engine runs under 1-3 concurrent long sequences. Target verify occasionally produces all-NaN rows; subsequent proposal state remains poisoned.

A poison-injection harness reports:
- clean q_len=8: finite / reference-matching
- q_len=8 with NaN bytes only beyond valid sequence rows in the last page: **NaN output**
- q_len=1 with the same poisoned tail: finite
- extra table entries pointing to poisoned rows: **NaN output**.

Mechanism: causal masking can zero attention probability for invalid positions, but the P·V multiply can still propagate **0 × NaN = NaN**.

This is **not Qwen3.8-Flash, not Apple and not a performance measurement**. The issue is still a report, not an upstream-confirmed root cause.

Project 51 PP2 action:
- zero/sanitize newly allocated or recycled KV pages;
- assert finite cache writes and stage-boundary tensors in debug qualification;
- test mixed prefill+decode/spec batches, page crossings and concurrent row lifecycles;
- never treat masked garbage as safe payload.

No numeric target effect.

## RECOVERED / MERGED — ragged sparse-indexer geometry cannot assume uniform decode rows

vLLM PR #52500 merged in this window as commit `133b71e0beec` at **20:14:29 UTC**, but its substantive evidence predates this hard boundary, so it is not classified as strict-window NEW.

The bug:
- metadata could say padding was unnecessary;
- a ragged decode batch could still contain, for example, 8 decode tokens across 6 requests;
- the fast path then performed a uniform reshape and crashed.

The fix also uses the padded path whenever:
`num_decode_tokens % number_of_rows != 0`.

Project 51 implication:
QSA/indexer verify kernels must derive row geometry from actual per-row lengths, not a single uniformity flag.

## CORRECTION — llama.cpp #29092 now points to the Ollama build, not upstream source/runtime

Fresh follow-up:
- stock llama.cpp on gfx1151 / system ROCm 7.1: **no cross-request GDN leak**
- same stock build with **Ollama's bundled ROCm 7.2 runtime**: **no leak**
- Ollama 0.34.1 bundled llama-server + bundled libggml-hip under the same ROCm 7.2 runtime: **leak reproduces**.

Holding ROCm 7.2 constant exonerates the runtime itself and the tested upstream llama.cpp source. Remaining differences are the Ollama ggml-hip build/patches/flags or fused-op resolver path.

Classification: **NEW attribution correction.**

Project 51 impact:
do not carry this as a current upstream llama.cpp GDN-state defect. The broader rule—recurrent state must be reset and row-local—remains valid independently.

## NEW non-target regression — llama.cpp #29149 Flash-Next HIP load livelock

Source: https://github.com/ggml-org/llama.cpp/issues/29149  
Created **2026-09-19 19:11:38 UTC**.

Qwen3.8-Flash-Next UD-IQ3_XXS and UD-Q4_K_XL on ROCm/HIP can livelock during load when enough of the model is placed on the GPU; the same command/model loads under Vulkan. Reported state while hung is ~one CPU core busy, GPU 0-3%, disk idle and frozen VRAM.

This is a backend load-path issue, not Apple/M1 evidence. It reinforces the runtime-SHA/backend smoke gate but gives no target credit.

## DS4 side evidence — attention Q4 without imatrix

DS4 #952 received a 2026-09-19 19:50 UTC ROCm quality comparison of AProjQ4 with and without the measured imatrix:
- fixture: 100 official continuations / 2,313 target tokens / ctx4096
- Q8 avg_nll: **0.40599**
- Q4 imatrix: **0.40522**
- Q4 synthetic weight-energy fallback: **0.40114**
- top1 rate: 0.8582 / 0.8599 / 0.8573
- top-n recall: 0.7592 / 0.7554 / 0.7504.

The author correctly labels the sub-1% differences below the fixture's discrimination threshold: **no measurable regression**, not proof that no-imatrix is better.

Classification: **NEW DS4 quantization-side evidence, non-Flash target.**

Project 51 impact:
do not assume every projection family needs measured imatrix guidance, but require our own oQ5e/BF16 certification battery before simplifying Flash hot-trunk sensitivity data. No quant-target change.

## CURRENT-DAY, timestamp-not-qualified community/benchmark observations

These were visible during the pass but do not expose a precise substantive timestamp after the hard boundary, so they are not strict-window NEW.

### M5 Max oQ4e Lightning MTP community session

oMLX benchmark page, M5 Max 40c / 128 GB / oMLX dev2 / Qwen3.8-Flash-Next-oQ4e-mtp:
- 1K: **882.1 PP / 54.1 TG**
- 4K: **1369 PP / 65.0 TG**
- 8K: **1527 PP / 60.3 TG**
- batching panel at the 1K session: **54.1 B1 -> 89.3 B2 -> 140.8 B4**.

Useful stronger-Apple evidence that high aggregate Flash throughput is physically achievable; not M1, not ~128K, and timestamp-not-qualified.

### 64-GB M5 Pro streamed-expert community report

A same-day Reddit post reports a 95.5-GiB Qwen3.8-Flash-Next artifact on an M5 Pro 64 GB using SSD-streamed routed experts:
- draft/MTP on: about **27.6 TG**
- draft off: **18-18.6 TG**
- real chat around 29K context: about **20.6 TG**
- direct PLE file reads substantially improved prefill in the author's fork.

Hardware is not M1 and the post does not provide a precise UTC source timestamp for this strict window, so it is ecosystem support only.

## Checked surfaces / negatives

- **No exact 2x M1 Max / TB4 Flash TG, PP, PP2-occupancy or ~128K MTP receipt.**
- **No new Kadir qwen38-mac-fast or Kadir llama.cpp activity.**
- **Splash:** strict-window activity is score-only/API work, not model kernels or older-Apple support. No M1 backend or benchmark appeared.
- **mlx-serve:** the Linux/Vulkan port merged; no Apple Flash performance change.
- **vLLM #57701** sparse-indexer workspace reduction merged in this window, but its substantive 512 MiB/3,072 MiB savings were already recorded before the prior hard boundary; merge time does not make the evidence new.
- **vLLM #57129** fused score+top-k remains older evidence: H200 operator gains up to 5.40x but only ~0.7-0.9% E2E TG; its strict-window update was merge-conflict bookkeeping.
- **oMLX #3594 B>1 packed TurboQuant batching remains unresolved/serialized.**
- No strict-window evidence warrants changing the custom hot-trunk BPW target.
- No strict-window source shows oQ5e quality equivalence for a new lower-BPW Flash trunk.

## Target / confidence decision

**No change.**

Flash-Next dual-M1:
- >=35 TG @ ~128K: **~85%**
- **>=40 TG @ ~128K: ~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20%**
- **400 cold PP: ~70%**.

Why no move:
- oMLX #3594 strongly improves confidence that sparse-QSA + compressed selected-K/V can scale far beyond 128K, but it is M5 Max, not M1.
- recovered #3695 shows batched MTP works on Apple but also shows speculation's incremental benefit shrinking rapidly with concurrency.
- the fresh ragged-cache and PP2 corruption reports increase the amount of correctness qualification required before crediting distributed/multi-row gains.
- exact M1 long-context target-only evidence remains favorable, but the decisive ~128K MTP + PP2/TB4 receipt is still missing.

## New / strengthened qualification rules

1. **Separate QSA indexer precision from selected-K/V precision.**
2. **At extreme context, bound MTP prompt priming independently from target context.**
3. **Resolve speculative fallback eligibility before mutating shared cache state.**
4. **Rollback/trim/finalize are vector operations for ragged batches; scalar fallback is not valid.**
5. **MTP vs ordinary batching is a measured concurrency policy, not an additive multiplier.**
6. **PP2 debug qualification must include page sanitation/finiteness checks and mixed prefill+decode/spec concurrency.**
7. **Sparse-indexer row geometry comes from actual row lengths, not a single uniformity flag.**
8. Existing exact runtime SHA, fast-path engagement, fusion concurrency, MTP ABI parity, deep-context acceptance, QSA/KV common-prefix reuse, chunk-parity and stage-occupancy rules remain.

## Hard freshness boundary

`2026-09-19 22:24:30 UTC`
