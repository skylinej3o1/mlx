# Project 51 research watch — 2026-10-02 19:25 ET

Freshness boundary entering: **2026-10-02 20:03:27 UTC**
Cutoff: **2026-10-02 23:25:36 UTC**

## Decision

**No numeric physical-fit, Windows-admission, zero-stall, TG/PP-center, context-target, or hardware-purchase change.**

Current exact-box planning state stays:
- Strata baseline: **0.1.37**;
- IQ3_S + native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h zero-stall: **~75%**;
- 24 h zero-stall: **~55%**;
- #481-style automatic containment/no-manual-service-restart: **~85%**;
- conversation parking remains **OFF** for the initial production baseline pending #528;
- high/xhigh still requires explicit `reasoning_budget_tokens`.

This pass changes **quality and agent-certification priority**, not hardware viability:

1. **PLE precision becomes a first-class quality lever.**
   Strata #464 now has much stronger evidence that checkpoint-native FP8 PLE is extremely close to BF16 while the
   stock IQ4_NL PLE can move logits materially. BF16 remains the source-of-record control; **FP8 PLE becomes the
   preferred production-fidelity candidate** once the path is qualified on the exact IQ3_S configuration.

2. **Agent parser certification expands.**
   Strata #537 shows literal/self-generated `</think>` text can terminate or leak reasoning, and an unfinished tool
   call can disappear behind a clean `finish_reason: stop`. vLLM #59821 independently demonstrates the complementary
   parser requirement: quoted tool markup inside reasoning must remain reasoning while a real implicit-end tool call
   must still execute.

3. **Deterministic certification must keep adaptive residency frozen.**
   Strata #550 finds an engine-side residency-table upload race after swaps/trim/refill. #463 separately shows the
   existing nonblocking adaptive-swap race can fork greedy output. The existing Project-51 frozen-residency AA rule is
   therefore strengthened, not relaxed.

4. **A local-build sm_120 ABI trap can fake terrible PP.**
   Strata #542 shows a mismatched CUDA header/runtime build can silently disable MMQ and cut prefill ~4x. The official
   prebuilt path is not implicated, but any custom 5070-Ti build must sanity-check CUDA runtime/header compatibility
   and the startup GPU-property values before interpreting PP.

No reason to buy more hardware. No reason to retreat from native 262,144.

## UPDATE — Strata #464: FP8 PLE looks like the practical source-fidelity lane

PR:
https://github.com/Niko1221/Strata/pull/464

This PR existed before the boundary; the **new measurements and interpretation are UPDATE evidence**.

The stock ISTA second shard presents the PLE table to Strata as **IQ4_NL**. The checkpoint itself also contains:
- F8_E4M3 + scale;
- BF16 source-of-record values.

The PR's packer now copies checkpoint-native FP8 or BF16 bytes rather than re-quantizing.

### New independent FP8-vs-BF16 result

The PR incorporates an independent 0.1.37 / RTX 5090 measurement on an NVFP4/Orca-derived lane:
- answer-level median KL, FP8 vs BF16: **~0.00087**;
- another BF16-table/cache-size run: **~0.00080**, i.e. same scale;
- FP8 table: ~51 GB;
- BF16 table: ~102 GB.

That is not yet an exact IQ3_S source-equivalence receipt, but it is strong evidence that the native FP8 table can be
a near-BF16 production choice.

### Stock IQ4_NL vs BF16 is much farther apart

With the same engine/prompt and fixed expert cache, first-window KL:
- 2K: **0.156**;
- 16K: **0.0030**;
- 37K: **0.220**.

Top token stayed the same in each reported probe, so this is **not** evidence of immediate greedy-answer failure.
It is evidence that the PLE table can materially alter the logit distribution and routing trajectory.

### Cost

BF16-vs-IQ4_NL prompt sweep through ~232-237K:
- deltas stay within roughly **-2.3% to +1.0%**;
- no clear performance penalty survives noise.

The table is streamed from disk rather than held resident, so the main BF16/FP8 cost is disk capacity, not an extra
50-100 GB of process RAM.

### Project-51 decision

Quality ladder now becomes:
1. stock IQ3_S + stock IQ4_NL PLE — compatibility/performance baseline;
2. **checkpoint-native FP8 PLE — preferred production-fidelity candidate**;
3. **BF16 PLE — source-of-record control**.

Do not claim FP8 equivalence from the 5090/NVFP4 result alone. Exact IQ3_S qualification still needs:
- answer-level KL / logit deltas;
- near-tie flips;
- long agent trajectories;
- Playwright/debugging tasks;
- 32/64/128/192/250K retrieval and state tracking.

This is encouraging because it offers a plausible fidelity improvement without touching the 54.8-GB IQ3_S transformer
arena or the native262K memory-fit case.

## UPDATE — Strata #463: adaptive-swap timing really can fork deterministic greedy output

PR:
https://github.com/Niko1221/Strata/pull/463

Independent 0.1.37 / RTX 5090 / NVFP4 reproduction now reports:
- same prompt, fixed expert cache, 400 tokens;
- default nonblocking adaptation: **2 different outputs** over 3 runs;
- `STRATA_ADAPT_WAIT=1`: **3/3 identical**.

On that busy tier, waiting for swaps costs roughly:
- **18.38 -> 19.32 ms/round (~5%)**.

The original lighter tier showed <0.3% cost.

Project-51 consequence:
- source/AA certification continues with **adaptive swaps disabled/frozen residency**;
- production adaptive residency is a separate performance mode;
- if production requires deterministic greedy behavior, test `STRATA_ADAPT_WAIT=1` on the exact box rather than
  assuming it is free.

## NEW — Strata #550: residency-table upload race after swaps/trim/refill

PR:
https://github.com/Niko1221/Strata/pull/550

Created **2026-10-02 22:14:18 UTC**.

Engine-side issue:
- expert residency table uploads use pageable host->device `cudaMemcpy` on the legacy stream;
- consumers run on `cudaStreamNonBlocking`;
- the next verify window can therefore read a table before the upload DMA has landed.

Failure shape:
- expert can be computed by both GPU and CPU, or by neither;
- table is only ~100 KB, so the race should be rare.

Proposed fix synchronizes the legacy stream after the residency-table copy.
RTX 5090 IQ2_XS A/B:
- first-token logits identical at 2K/32K;
- decode cost about **+0.7%**, within noise.

This is not a reason to lower physical-fit confidence. It is another reason the controlled quality lane must keep
residency static until the fix is merged/qualified.

## NEW — Strata #537: quoted/self-generated </think> can break answer-channel semantics

Issue:
https://github.com/Niko1221/Strata/issues/537

Created **2026-10-02 21:17:05 UTC** on official v0.1.37 / IQ3_S / RTX 5090 / native262K.

Two direct failures:
1. user asks the model to quote literal `</think>`:
   - HTTP 200;
   - `finish_reason: stop`;
   - no final answer content;
   - reproduced 3/3 JSON and 3/3 SSE.
2. user sends only escaped text `&lt;/think&gt;` and asks what it means:
   - model itself generates literal `</think>` inside reasoning;
   - parser switches channel early;
   - reasoning leaks into visible content and later the true close marker can also appear visibly;
   - reproduced 3/3 JSON and 3/3 SSE.

A follow-up also identifies another agent failure mode:
- generation ends while mid-tool-call;
- `finish()` silently discards the unfinished call;
- client receives empty content, no tool call, clean `finish_reason: stop`.

Project-51 parser gate now must include all of:
- quoted literal `</think>` in user text;
- model quoting `</think>` inside reasoning;
- quoted `<tool_call>` markup inside reasoning stays reasoning;
- a real implicit-end tool call still becomes a tool call;
- malformed/incomplete tool-call history does not crash the next request (#510);
- unfinished current tool call is surfaced as content/error/stall, not silently discarded;
- #525's ordinary reasoning->tool transition case.

For an autonomous QA agent, these are correctness gates, not cosmetic frontend issues.

## NEW — vLLM #59821 independently clarifies the right quoted-tool semantics

PR:
https://github.com/vllm-project/vllm/pull/59821

Created **2026-10-02 20:06:27 UTC**.

vLLM observed that a `<tool_call>` block quoted as an example inside Qwen3 reasoning could be executed as a real tool.
Their proposed parser:
- holds a tool opener while reasoning is still open;
- if `</think>` arrives, returns the held span as reasoning;
- if stream ends without an explicit close, replays it through the existing implicit-end-tool path.

Validation claims:
- quoted tool markup remains reasoning;
- genuine implicit-end tool calls keep working;
- thousands of parser tests plus focused new cases.

This is directly relevant to reviewing Strata #525: Project 51 should test both sides of the ambiguity, not merely
"tool opener inside reasoning => end reasoning."

## NEW — Strata #542: custom sm_120 builds can silently lose ~4x PP from CUDA ABI mismatch

Issue:
https://github.com/Niko1221/Strata/issues/542

Created **2026-10-02 21:36:06 UTC**.

On an RTX 5090 local build:
- 0.1.31 32K PP: **3,285**;
- broken 0.1.36 build: **1,083**;
- same 0.1.36 after fixing the link: **3,281**.

Root cause:
- CUDA 13.x headers compiled the host code;
- binary linked an older CUDA 12.4 `libcudart`;
- `cudaGetDeviceProperties` struct layout mismatch made shared-memory-per-block read as **1 byte**;
- MMQ `fits()` therefore rejected every IQ kernel and silently fell back to slow dequant-FP16 prompt work.

The official Windows prebuilt is not the reported failing path.

Project-51 exact-box gate for any local/custom build:
- verify the runtime/header CUDA major match;
- sanity-check startup GPU properties;
- a value such as **1 byte shared memory/block is an invalid build**, not a slow GPU;
- do not accept a sudden ~4x PP loss as a hardware result.

## NEW — Strata #547: prompt carve currently over-reserves VRAM

PR:
https://github.com/Niko1221/Strata/pull/547

Created **2026-10-02 21:52:40 UTC**.

`Prefill::bytes_needed()` does not exactly match what `carve()` allocates.

Default path over-count:
- **~0.31 GiB at an 8K chunk**;
- **~1.25 GiB at a 32K chunk**.

Those bytes are borrowed from the expert cache but never used, which is especially relevant to 12-16 GB cards.

RTX 5090/IQ2_XS measurement:
- borrowed slots at 32K chunk: 3,340 -> 3,108;
- first-token logits byte-identical;
- one-run prompt time 6,460 -> 6,241 ms.

Mechanism is favorable to the 5070-Ti 16-GB lane and may reduce transient/cache pressure, but there is no exact-card
IQ3_S receipt. **Do not raise the fit prior yet.**

## NEW — Strata #559: real multi-conversation batching arrives as an opt-in PR

PR:
https://github.com/Niko1221/Strata/pull/559

Created **2026-10-02 23:05:49 UTC**.

Adds:
- verifier batch windows for 2-8 independent conversations;
- pipelined layer-split groups;
- per-stage dense-weight trimming;
- concurrent server slots.

Correctness gate:
- 8 conversations x 150 greedy tokens;
- identical to solo runs under fixed deterministic controls (`STRATA_IQ_MT_MIN=1`, `--pcie-frac 0`).

Measured on **4 x 16-GB GPUs / PCIe Gen3 / IQ3_S**:
- 1 request: 123 tok/s solo;
- 2: 57 each / 113 total;
- 4: 51 each / 205 total;
- 8: 45 each / **360 total**.

Not yet:
- no MTP in batched windows;
- penalties not applied in batch windows;
- batching/pipeline not wired into setup.

Interesting future multi-agent mechanism; **no single-5070-Ti target or hardware-purchase change**.

## UPDATE — conversation caching is not universally broken, but #528 keeps it out of the initial baseline

Strata #189 has a new official-v0.1.37 Windows data point:
- RTX 4070 Laptop 8 GB;
- 64 GB RAM;
- Swift IQ3_XXS;
- high reasoning;
- 64K configured context;
- 2-slot / 2-GiB conversation cache.

57,750-token cold request:
- mapped mode: 188.93 s;
- resident mode: 107.17 s.

Return after unrelated request:
- mapped: 4.44 s;
- resident: 2.57 s;
- **57,745 tokens reused** in both;
- correct answer, image history and tool/code checks passed.

So #528's ~100K RTX5090 restore slowdown is likely **regime/config/path-specific**, not proof that snapshot restore is
conceptually broken. Nevertheless, because #528 remains unresolved at the target long-agent scale, the first
Project-51 baseline still keeps conversation parking OFF.

## NEW — Strata #535: 0-MiB-free configuration can collapse to ~0.6 TG mid-agent session

Issue:
https://github.com/Niko1221/Strata/issues/535

RTX 3070 Ti / 64-GB Windows / IQ3_S / 0.1.36:
- startup explicitly reports **0 MiB VRAM free** and warns to add reserve;
- after tool-call traffic, a later turn reads only 452 new tokens at 6.8 PP and generates 555 tokens at **0.6 TG**;
- only one CPU core appears busy; restart is reported as the only recovery.

This reinforces, rather than changes, the existing admission rule:
**0 MiB free is a failed configuration.**
The 5070-Ti production gate keeps a real VRAM reserve and rejects WDDM/shared-memory spill.

## NEW — Strata #560 matters to the secondary RX 6800 Linux box

Issue:
https://github.com/Niko1221/Strata/issues/560

AMD/Linux desktop, 64 GB RAM, 32-GB R9700, IQ3_XXS:
- default 700-MiB reserve left ~624 MiB actually free;
- starting desktop apps triggered ~24.5 GB of GTT/system-RAM eviction;
- OOM killed desktop processes;
- `--vram-reserve-mib 3072` stopped the behavior.

The user's RX6800/Linux secondary host should therefore use a **multi-GiB reserve if that GPU drives a desktop**,
rather than copying the primary NVIDIA reserve blindly.

No primary 5070-Ti target change.

## NEW — oMLX #4214 / #4215: greedy MTP can be nondeterministic on the Apple dense lane

Issue/PR:
https://github.com/jundot/omlx/issues/4214
https://github.com/jundot/omlx/pull/4215

Qwen3.8-27B-oQ4e-mtp / M4 Max 64 GB:
- same temp-0 prompts over 20 runs produced 1 and 4 distinct outputs with MTP;
- MTP off: 20/20 identical;
- bisected to width-dependent verify kernels.

Proposed fix makes greedy singleton verify width-stable:
- 53.3 -> 51.1 TG in one short-prompt measurement (~4% cost);
- 20-run distinct outputs become 1 and 1;
- with SpecPrefill off, a 22K prompt matched MTP-off exactly;
- **SpecPrefill-on nondeterminism remains**.

This is a dense-Apple runtime issue, not Strata/Flash fit evidence.
It strengthens the exact requirement that Apple certification compare serial, MTP and SpecPrefill separately.

## NEW — TensorFold #278 / #280: M1-M4 dense lane has a real row-window cliff and quant-dependent draft acceptance

On a 48-GB M4 Pro / Qwen3.8-27B:
- row decoder cost is nearly flat from 2-8 rows, roughly doubles by 16, and jumps again at 17;
- 4-bit target: ~43.4 TG, 7.8 rows/round, 47/109 drafts accepted;
- oQ2: ~19.7 TG, 2.9 rows/round, 31/60 accepted.

This is **not Flash-Next** and does not move the dual-M1 Flash target.
For the single-M1/27B fallback lane, it reinforces:
- do not assume lower target BPW automatically raises end-to-end speed;
- draft acceptance must be calibrated against the actual target quant;
- 4-bit currently looks like the safer pre-M5 operating point.

## NEW — TensorFold #284: mixed-width oQ3.5e can run on pre-M5 after FP16->BF16 normalization

M4 Max 64 GB / Qwen3.8-27B-oQ3.5e:
- before: row-decoder Metal compile failure;
- patch casts checkpoint FP16 floating tensors to BF16;
- after: loads, drafts, and reports ~70-76 TG on longer replies vs ~25.6 serial;
- exact drafted/serial/resend text/token SHA passed the reported short validation.

Promising 27B fallback work, not dual-M1 Flash target evidence.

## NEW — mlx-serve #706: another runtime finds corrupted hot-cache restore

Issue:
https://github.com/ddalcu/mlx-serve/issues/706

M5 Max 128 GB / Flash-Next mixed 4-8bit / long agent session:
- a fresh German request hit a hot-cache entry and was interpreted as unrelated Chinese;
- identical retries hit the same bad cache state;
- restart fixed it;
- observed once so far.

Different runtime and not yet reliably reproduced, but it reinforces the universal Project-51 rule:
**restored prefix/state must be proven equivalent to cold prefill, not trusted because the token prefix matches.**

## NEW — vLLM #59826: hybrid recurrent + attention prefix caching remains subtle under speculation

Open PR fixes several hybrid Mamba/full-attention prefix-cache boundary errors under EAGLE/speculation:
- cached recurrent state and attention proof can land at different boundaries;
- exact prompt resend can collapse from a substantial reusable prefix to zero;
- external tail saves can miss the proof margin required by speculation.

Agentic benchmark shows improved hit rate/throughput at high concurrency, but this is a separate runtime/model family.

Project-51 implication:
- prefix reuse qualification must run **with MTP/speculation enabled**;
- cache correctness needs recurrent/GDN + QSA/attention + draft state at the same committed frontier.

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- DASLab / Hugging Face;
- TurboQuant;
- mlx-serve;
- Ishizuki.

No newer Strata engine release than **0.1.37** found in the repository during this pass.
No TurboQuant repository change.
No Ishizuki change.
No target-moving MLX-core item.
No new DASLab long-agent/xhigh IQ3_S quality table. The live model card remains:
- IQ3_S transformer average **3.50 bpw**;
- 54.8-GB transformer shard;
- 28.8-GB n-gram shard;
- AIME25 100.00;
- GPQA-D 92.93;
- LCBv6 86.86.

## Target state after this pass

1. Current exact-box Strata baseline: **0.1.37**.
2. IQ3_S/native262K physical-fit prior: **~95%**.
3. Windows 16-GB/64-GB full-context admission prior: **~90%**.
4. 8 h zero-stall: **~75%**.
5. 24 h zero-stall: **~55%**.
6. #481-style automatic containment/no-manual-service-restart: **~85%**.
7. Conversation parking: **OFF for initial production baseline** pending #528 exact-regime resolution.
8. High/xhigh: explicit `reasoning_budget_tokens`.
9. Controlled quality runs: **adaptive residency OFF / frozen**.
10. PLE ladder: stock IQ4_NL baseline -> **FP8 production-fidelity candidate** -> BF16 source control.
11. Agent parser gate expands to quoted think/tool markup and unfinished-call behavior (#537 + vLLM #59821).
12. Any custom sm_120 build must pass CUDA-runtime/header and sane-GPU-property checks (#542).
13. IQ3_S TG/PP centers: **unchanged**.
14. Native production context target remains **262,144**.
15. No hardware purchase change.

## New hard boundary

**2026-10-02 23:25:36 UTC**
