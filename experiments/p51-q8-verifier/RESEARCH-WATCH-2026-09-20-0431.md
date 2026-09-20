# Project 51 external runtime watch — 2026-09-20 04:31 ET

**Hard freshness window:** strictly after **2026-09-20 05:46:36 UTC** through **2026-09-20 08:31:59 UTC**.

This pass also consolidates several older/recovered sources intentionally surfaced during the user's quant-design discussion: MTPLX Bare/Optimized, Myric Flash-Next APEX, the APEX quantization repo, and the M1 BF16->FP16 MLX kernel experiment. Those are clearly marked as recovered/current design evidence rather than falsely labeled NEW.

## Decision

**No numeric TG/PP probability change.** The headline target remains **40 TG @ ~128K active context / 400 cold PP** on 2x M1 Max 64 GB / TB4.

The important change is **quant identity and experiment design**:

- stop describing MTPLX Optimized Speed as "basically Q5";
- use **MTPLX Bare = flat 4-bit** and **MTPLX Optimized = dynamic 4-bit with Q8 QSA attention** as concrete MLX endpoints;
- treat ~4.6-4.9 hot-trunk BPW as the **initial search band**, not a sacred scalar target;
- mine APEX for per-role/per-layer sensitivity methodology and optimize **quality loss per M1 hot-byte / microsecond saved**, not whole-file BPW;
- establish an M1-native **BF16->FP16 protected-tensor baseline** before custom reallocation;
- add an agentic **wake/prewarm protocol**: a trivial Slack/Telegram/iMessage message can trigger invariant-prefix prefill and certified state preparation before the real task arrives.

## RECOVERED CURRENT REFERENCE — MTPLX Bare Speed is the flat-Q4 lower endpoint

Source: https://huggingface.co/Youssofal/Qwen3.8-Flash-Next-MTPLX-Bare-Speed

The model card calls this **"Flat 4-bit quantization"**.

- every MoE expert and dense matrix: **4-bit, 64-weight groups**;
- GDN convolution/recurrent-state parameters, every norm, QSA indexer and MTP head: **16-bit**;
- n-gram table: separate ~32 GB SSD-streamed sidecar;
- resident weights with n-gram on SSD: **~74 GB + working set**;
- adaptive MTP, ceiling depth 3.

M5 Max product measurements:

- coding task MTP: **75.9 TG**;
- same task plain autoregressive: **47.0 TG**;
- MTP multiplier: **~1.6x**.

This is older than the strict watch window, so it is **RECOVERED/CURRENT REFERENCE**, not NEW.

**Project 51 role:** first flat-Q4 MLX baseline, and a likely lower-precision endpoint for the custom quant search.

## RECOVERED CURRENT REFERENCE — MTPLX Optimized Speed is dynamic Q4, not Q5

Source: https://huggingface.co/Youssofal/Qwen3.8-Flash-Next-MTPLX-Optimized-Speed

The author labels this **"Dynamic 4-bit quant with 8-bit attention."**

- bulk MoE/dense matrices remain Q4;
- Qwen Sparse Attention projections are promoted to **8-bit**;
- sensitive GDN/norm/indexer/MTP islands remain 16-bit;
- n-gram table remains SSD-streamed;
- resident body is larger than Bare because the QSA pathway is protected.

The card reports on M5 Max:

- **79.3 TG** on a ~9K code prompt;
- **61.8 TG** on a ~109K OpenCode turn;
- **50.3 TG** on a warm ~200K OpenCode turn;
- a cache-heavy OpenCode request at **125.8 TG**, with 18,364 of 18,539 prompt tokens served from cache;
- a **96,760-token** conversation restored from session cache in **8 ms**.

**Correction:** do not call this a uniform or literal Q5 quant. Its useful identity is **Q4 trunk + Q8 QSA + 16-bit sensitive islands**.

**Project 51 role:** higher-quality dynamic-Q4 comparator. The interesting search is which QSA/layer/tensor subsets truly need promotion above Bare.

## RECOVERED M1-SPECIFIC MECHANISM — BF16 storage/I-O with FP16 compute can recover the M1 fast path

Source: mlx PR #4216, "Optimize BF16 quantized matmul with FP16 tiles" (older experiment).

Exact M1 Max affine INT4/group-32 QMM, M=512/K=6656/N=19968:

| Path | Time |
|---|---:|
| stock BF16 | **30.6 ms** |
| stock FP16 | **17.2 ms** |
| BF16 I/O + FP16 tiles / FP32 accumulate | **17.32 ms** |

The mixed path essentially matched pure FP16 while preserving BF16 I/O.

**Project 51 first artifact experiment:** take MTPLX Bare/Optimized and convert or execute the remaining 16-bit BF16-sensitive path through M1-friendly FP16 where semantically safe, while keeping all quantized tensors bit-identical. Benchmark target TG, PP, MTP acceptance/tokens-per-cycle, long recurrent stability, logit/greedy parity and wired memory.

This does **not** mean FP16 is universally "higher quality" than BF16. Recurrent state needs explicit range/stability validation.

## RECOVERED APEX METHODOLOGY — turn quantization into a measured allocation problem

Source: https://github.com/localai-org/apex-quant

The useful asset is not a preset. It is the machinery:

- `generate_sensitivity_configs.py`: hold a baseline precision, drop one tensor group at a time, measure quality damage;
- `generate_opt_config.py`: allocate bits by measured marginal damage per byte saved;
- explicit edge / near / middle layer bands;
- diverse imatrix calibration spanning chat, code, reasoning and tool-calling.

On Qwen3.8-27B, APEX measured a **15.3x spread** in sensitivity across tensor groups.

Notable measured results:

- `output` was **15.3x more expensive per saved byte** than `token_embd` despite identical shape;
- FFN edge layers were **2.63x more expensive per saved byte** than middle layers;
- gate/up/down and linear-attention subroles were not interchangeable;
- sensitivity is **convex**: a cheap Q6->Q3 move does not imply the last Q4->Q3 bit is cheap;
- at the relatively gentle Q4 band, measured reallocation could be worse than a flat role-aware control because there was little quality damage left to redistribute;
- at more aggressive Mini/Nano bands, measured allocation recovered roughly **22-25%** KL advantage at matched-ish size.

**Project 51 adaptation:** replace APEX's sole objective "Delta quality per GB saved" with a multi-objective ruler:

- behavioral quality loss;
- long-context/QSA retrieval loss;
- tool/state correctness;
- MTP acceptance/tokens-per-cycle loss;
- **M1 microseconds/token saved**;
- hot bytes/token saved;
- PP impact;
- kernel-format availability/efficiency.

Use the sensitivity sweep to rank local moves around the actual Q4/Bare operating point. Do not extrapolate one giant perturbation.

## RECOVERED FLASH-SPECIFIC APEX MAP — Myric Flash-Next APEX is a useful tensor-role prior, not a final recipe

Source: https://huggingface.co/Myric/Qwen3.8-Flash-Next-APEX-GGUF

Published MIDDLE:

- 91.7 GB / **4.144 whole-file BPW**;
- 176.944B included parameters;
- 51.200B `per_layer_token_embd`: Q4_0;
- 40.265B `ffn_down_exps`: Q4_0;
- 80.531B gate/up experts: mixture of **IQ4_XS and IQ3_XXS**;
- attention, dense FFN, shared experts, `ssm_out`, `attn_gate`: **Q6_K / Q8_0 / F32**;
- token embedding/output: Q6_K;
- QSA indexer q/k projections: **BF16**;
- quantized using an importance matrix with **926 entries over 4,000 calibration chunks**.

Two shape constraints matter:

- `ffn_down_exps` rows are only **640** wide;
- `per_layer_token_embd` rows are only **160** wide.

Neither is divisible by 256, preventing 256-block K/I formats and forcing 32-block-style fallbacks for **91.5B params / 51.7% of the file**. Gate/up rows are 2560 wide and remain much more flexible.

The 51.2B n-gram table is sparse lookup: only a few rows are touched per token. Therefore its file BPW is not equivalent to hot decode bandwidth.

The artifact omits the **2.607B MTP head**, so its quality/speed does not certify our MTP lane.

**Project 51 implication:** the likely high-leverage search surface is gate/up expert precision and selective sensitive-path protection, while down-expert / PLE format choices are constrained by row shape and actual M1 kernel support.

## QUANT DESIGN CHANGE — optimize hot-path economics, not a whole-file BPW label

The current preferred experimental ladder becomes:

1. **MTPLX Bare-FP16/M1 path** — flat Q4 trunk, sensitive 16-bit path adapted to M1 FP16 execution.
2. **MTPLX Optimized-FP16/M1 path** — dynamic Q4 + all QSA Q8.
3. **P51 measured mixed quant** — start from Bare and add/remove precision only where Flash-specific sensitivity + M1 timing justify it.
4. APEX-inspired aggressive arms below flat Q4 on selected gate/up middle layers, but only if M1 dequant/GEMV kernels actually make those formats faster.
5. oQ5e/BF16 remains a quality/certification comparator; oQ4e remains an aggressive runtime comparator.

The canonical deployment search still starts around **4.6-4.9 effective BPW on the hot compute trunk**, but APEX makes **~4.3-4.6 experimental arms worth testing**. No lower band is promoted until exact M1 behavioral quality and MTP evidence support it.

## AGENTIC ARCHITECTURE — precompute the context tax before the real task exists

User-supplied discussion:
https://www.reddit.com/r/LocalLLaMA/comments/1wlazxc/precaching_context_overhead_system_prompt_tools/

The exact Reddit page was not retrievable by the current web tool, so no unverified comment text is imported. The architecture idea itself is independently consistent with established prefix-cache behavior and Splash #16's producer/waiter reuse.

Agent harnesses repeatedly carry invariant or slowly-changing prefix material:

- system prompt;
- tool schemas;
- skills;
- repo instructions / AGENTS.md;
- stable policy/runtime metadata;
- optionally a repo/session checkpoint.

### User-proposed wake/prewarm protocol

A trivial first message such as **"sup"** arriving through Telegram, Slack or iMessage can be treated as a **wake signal**, not the actual task.

Immediately on wake:

1. identify agent/repo/profile;
2. materialize or restore the stable system/tools/skills prefix;
3. prefill any missing invariant prefix;
4. restore/rebuild recurrent state + QSA/indexer summary state at a certified boundary;
5. warm the likely MTP/verifier graphs and stage-local buffers;
6. optionally pre-load a likely skill bundle without mutating the stable prefix identity;
7. wait for the real task;
8. append the real user request onto the certified warm prefix.

This can hide seconds of cold context work behind the human typing interval.

**Important:** this is a separate latency objective from **400 cold PP**. Cold PP must remain honestly measured with reuse disabled. Wake/prewarm gets its own metrics:

- wake -> prefix-ready latency;
- physical prefill rows executed;
- prefix tokens restored vs recomputed;
- cache/state bytes;
- real-task arrival -> first-model-work latency;
- TTFT with 0/1/3/10/30-second human think delays after wake;
- false wake / abandoned wake cost;
- prefix invalidation rate when tools/skills/repo state change;
- cancellation and concurrent wake behavior.

Security/correctness gate: the real request must bind only to the correct user/session/repo prefix; no cross-session recurrent/QSA state leakage.

## NEW MERGE — llama.cpp #28770 enables sparse FA for Qwen4/Qwen4Exp long context

Source: https://github.com/ggml-org/llama.cpp/pull/28770  
Merged **2026-09-20 08:08:11 UTC**.

The branch avoids rescoring the entire KV cache for sparse Qwen4 attention once the selected union is sufficiently sparse.

DGX Spark qwen4exp A3B IQ1_S results:

- TG @10K: 22.98 -> 23.56 (+3%);
- TG @20K: 20.76 -> 23.58 (+14%);
- TG @50K: 15.88 -> 18.72 (+18%);
- TG @100K: **12.00 -> 14.19 (+18%)**;
- PP-shaped test @100K: **252.81 -> 318.28 (+26%)**.

Different hardware/quant; do not transfer percentages to M1.

**Project 51 implication:** long-context QSA work must score/gather only the selected sparse set. Full-cache rescoring becomes increasingly dominant with context and can erase the gains of a lighter quant.

## NEW — vLLM #57770: speculative draft token selection itself can be a measurable serial cost

Source: https://github.com/vllm-project/vllm/pull/57770  
Created **2026-09-20 08:26:07 UTC**.

For DSpark greedy drafting, five dependency-chained full-vocabulary argmax operations run per decode step at n_spec=5. A split-vocabulary Triton reduction reduced the isolated argmax from:

- M=1: **43.424 -> 4.352 us (~10x)**;
- M=32: **44.415 -> 7.968 us (~5.6x)**;
- M=128: **45.344 -> 16.928 us (~2.7x)**.

End-to-end gains were smaller but measurable at high concurrency; acceptance/verification counts were unchanged.

**Project 51 implication:** after the big verifier/backbone costs are fixed, profile draft sampling/head selection as a serial per-depth tax. Small per-draft costs multiply by verify width/depth.

## NEW MERGES — Splash #16/#18 promote prefix-sharing/work-budget ideas to main

Merged **2026-09-20 07:25 UTC**.

Previously recorded as NEW PR evidence; now merged.

- #16: concurrent requests can wait on a live producer's certified shared-prefix recovery points instead of duplicating cold prefill.
- #18: prefill admission uses priority/remaining work/row budget rather than merely occupying state cells.

This directly strengthens the wake/prewarm architecture: a warm-prefix producer can feed later task requests without requiring each consumer to replay invariant context.

## NEW MERGE — Splash #22 defers history expansion and releases completed inputs

Merged **2026-09-20 07:26:01 UTC**.

Stored-response lookups no longer deserialize full conversation history when only the result is needed; queued continuations expand history only inside the preparation gate; `store:false` avoids retaining history it will never save.

Project 51 implication: **prompt/state preparation should be demand-driven**. Prewarm invariant material early, but defer mutable/full-history expansion until a request actually needs it. This prevents the wake path from eagerly inflating memory just because it has time.

## Screened / no target-changing evidence

- DS4 #1090 was updated in-window, but its headline M3 Ultra speed measurements are archived/historical and do not create a new exact M1 receipt.
- vLLM #57312 (MTP draft weight-cache daemon) updated in-window but reports no new target-topology throughput result.
- oMLX: no new default-branch commit in-window; the #3770/#3771 diagnoses remain the current relevant Flash regression evidence.
- mlx-serve: no post-boundary default-branch commit.
- Kadir repos: no activity.
- MTPLX repo: no strict-window commit; the Bare/Optimized cards are deliberately recovered design references.
- APEX repo: no strict-window commit; its sensitivity machinery is deliberately recovered methodology.
- No new exact **2x M1 Max 64 / TB4 / ~128K / custom mixed quant + MTP** throughput receipt appeared.

## Target impact

**No numeric target or confidence change.**

The quant plan is better specified, and wake/prewarm can materially reduce perceived agent latency, but neither is a physical exact-target throughput receipt.

**New hard boundary: 2026-09-20 08:31:59 UTC.**
