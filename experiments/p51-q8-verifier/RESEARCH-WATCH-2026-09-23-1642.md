# Project 51 primary-lane research watch — 2026-09-23 16:42 ET

**Freshness boundary checked:** prior hard boundary **2026-09-23 19:03:50 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-23 20:42:43 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No new exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared, and no new DASLab / GSQ-RCO xhigh behavioral-quality result appeared.

The most important change is a **correction** to the previous watch: the provisional llama.cpp Metal long-context batching cliff was a measurement artifact. That removes negative evidence against generic Metal batching, but it does **not** create exact evidence for P51's M1/TB4 multi-row speculative verifier geometry. The Apple7 B1/B2/B4/B8 verifier-width gate therefore remains useful as an empirical qualification step, but no longer because #29335 demonstrated a catastrophic Metal batching failure.

Other fresh evidence strengthens three existing design directions:

1. sparse PLE/sidecar I/O should use explicit, stable row-lifetime management rather than relying on transient graph-pool tensors or uncontrolled page faults;
2. recurrent/speculative placeholder rows must use rollback-capable state paths rather than being classified as ordinary prefill;
3. target and draft state/configuration are distinct ownership domains across disaggregated or pipelined execution.

## Findings

### UPDATE / CORRECTION — llama.cpp #29335: reported Metal long-context batch collapse was measurement error

Source: https://github.com/ggml-org/llama.cpp/issues/29335

The previous watch correctly treated this report as provisional. The reporter has now rerun on current master `6e60f3560` with `llama-batched-bench` and closed the issue, explicitly stating that the apparent collapse came from the custom measurement script rather than llama.cpp.

At 32K context:

| Model | N=1 | N=2 | N=4 |
|---|---:|---:|---:|
| Qwen3.8-Flash-Next Q8_0 | 29.6 TG | 38.2 TG | 43.8 TG |
| Qwen3.6-35B-A3B Q8_0 | 79.8 TG | 104.1 TG | 120.0 TG |
| Qwen3.5-27B Q8_0 | 19.6 TG | 30.8 TG | 36.1 TG |

For Flash-Next, a corrected `llama-server` measurement restricted to the interval where every slot was generating reported approximately **30.0 / 38.0 / 43.2 TG** for N=1/2/4, within ~2% of batched-bench.

The original script counted time where early-finished prompt slots were decoding while other slots were still prefilling; `predicted_ms` therefore attributed mixed prefill/decode passes to decode and produced the false cliff.

**Qualification:** this is M3-Ultra/current-master transfer evidence and the qwen4exp path remains a moving implementation target. It is not an exact M1-Max/TB4 P51 verifier-width receipt.

**P51 action:** retract #29335 as evidence of a generic Metal batching failure. Keep the Apple7 B1/B2/B4/B8 long-context verifier-width benchmark because P51 still needs exact evidence for shared-prefix speculative verification and PP2 overlap, not because generic Metal batching is known to collapse.

**Target impact:** none. The prior pass never reduced the ~70% >=40-TG planning confidence, so there is no numeric confidence restoration to perform.

### NEW — vLLM #58441: async PLE lookup can consume overwritten graph-pool IDs

Source: https://github.com/vllm-project/vllm/issues/58441

Qwen3.8-Flash-Next on DGX Spark GB10, TP1, CUDA 13.0, MTP n=3, piecewise CUDA graphs exposed a lifetime race in the PLE prefetch flow. `start_prefetch` launches lookup on a side stream and returns while the input `gathered_ids` still resides in graph-pool memory. Later graph segments can reuse that storage before the side stream consumes it.

Measured cold-versus-warm greedy reproducibility:

| lookup path | cold == warm | max |Δlogprob| |
|---|---:|---:|
| side stream, IDs directly from graph pool | 2/8 | 1.41 |
| same + #57785 capture-time sync | 1/8 | 1.41 |
| copy IDs to persistent buffer first | **8/8** | **0** |
| run lookup on current stream | **8/8** | **0** |

A follow-up source review notes that the output side already uses a persistent preallocated buffer; the transient input-ID lifetime is the asymmetry.

**Qualification:** PinnedHost itself could not fit on this 128-GB unified-memory box, so the corruption was reproduced through the checkpoint-mapped backend using the same side-stream flow. The exact allocator mechanism is therefore not fully proven for every PLE backend.

**P51 action:** any asynchronous PLE/QSA/sidecar operation must consume inputs whose storage lifetime explicitly extends through completion. Graph/capture-pool inputs should be copied to stable stage-owned buffers or fenced so reuse cannot occur. Do not treat stream recording alone as proof of lifetime safety across capture-pool reuse without a real-model determinism test.

### NEW — vLLM #58439: checkpoint-mapped PLE is system-competitive on unified memory when pages are prefetched

Source: https://github.com/vllm-project/vllm/pull/58439

This PR adds a Qwen4Exp PLE backend for integrated/unified-memory GPUs that maps the **47.68-GiB FP8 PLE table directly from safetensors** and has the GPU gather selected rows from those read-only file-backed pages. It avoids a table-sized device allocation, a table-sized pinned anonymous host copy, and a CPU-gather/H2D staging copy.

Exact test system:
- DGX Spark GB10, 128-GB unified memory;
- Qwen3.8-Flash-Next NVFP4 body;
- FP8 PLE table;
- MTP n=3;
- TP1.

A critical systems result is the cold-page behavior: a ~30K-token prefill took **88 s** when the GPU faulted file pages one by one, but approximately **1.6 s** when 64 CPU threads faulted the required rows into page cache first.

Versus the prior #53899 offload-worker reference on the same checkpoint:

| metric | prior worker | checkpoint-mapped |
|---|---:|---:|
| steady-state swap | 50-53 GiB | **5-6 GiB** |
| sum TTFT, 3 prompts of 24-29K | 32.99 / 33.47 s | **31.77 / 31.97 s** |
| sum TTFT, 3 prompts of 7-8K | 9.27 / 9.37 s | **9.01 / 9.02 s** |
| decode, c=16 | 197.6 / 201.1 TG | **199.1 / 198.7 TG** |

Correctness logging covered **2,500 serving steps / 11.36M gathered rows**, including 255 mixed prefill+decode steps. Greedy outputs were 8/8 identical across fresh starts and cold/warm runs with Δlogprob 0.

**Qualification:** validated on GB10 only. Apple Silicon has different page-fault, storage and Metal execution behavior, so do not transfer the percentages.

**P51 action:** this materially strengthens the architecture case for file-backed PLE on a unified-memory machine, but only with explicit row prefetch. P51 should compare SSD-backed explicit row gather/prefetch against mmap-demand behavior on M1; uncontrolled GPU/OS page faults are not an acceptable production path.

### UPDATE — llama.cpp #29030: Qwen4Exp lazy rows move from mmap demand paging to explicit direct reads

Source: https://github.com/ggml-org/llama.cpp/pull/29030  
Fresh commit: https://github.com/ggml-org/llama.cpp/commit/e32c6243d72efec1314d26b73d5b64359678fc76

The fresh commit makes lazy Qwen4Exp/Gemma4 tensor rows use explicit positional reads instead of relying on demand-paged mmap, and auto-enables the lazy-row path for integrated GPUs. The PR's existing Strix Halo measurements show the magnitude possible when sparse-row I/O is the bottleneck:

- pp512: **181.0 -> 400.8** (+121%)
- pp2048: **191.7 -> 421.1** (+120%)
- pp8192: **273.8 -> 451.4** (+65%)

Those benchmark numbers predate this boundary; the **fresh fact** is the implementation shift making direct reads the normal lazy-row mechanism rather than a separate experimental mode.

**P51 action:** explicit sparse row reads are now supported by another implementation path as a strong cross-hardware design choice. Benchmark batched/direct row reads on M1 rather than assuming mmap faulting is optimal. No Apple percentage transfer.

### NEW — vLLM #58434: padded speculative prompt tails can poison recurrent state if classified as prefill

Source: https://github.com/vllm-project/vllm/pull/58434

A one-token prompt tail over an existing recurrent state may be padded with K placeholder draft rows to keep a K+1 speculative shape. For GDN/KDA/Mamba-style recurrent layers, those rows must run the speculative-decode path so rejected placeholders can be rolled back.

The reported regression classified these padded tails as prefill. Prefill kernels then stored recurrent state after all K+1 rows, permanently folding placeholder tokens into the request state.

**Qualification:** correctness mechanism + regression test only; the branch was stale by two commits when CI was requested and no performance result is claimed.

**P51 action:** a padded/placeholder row over existing recurrent state is not ordinary prefill merely because the scheduler labels the request as prefilling. P51 verifier metadata must explicitly distinguish real prompt tokens, proposed tokens and rollback-only padding, and publication must occur only at a semantically committed frontier.

### NEW — SGLang #40953/#40955: target-only prefill does not create valid draft state

Sources:
- https://github.com/sgl-project/sglang/pull/40953
- https://github.com/sgl-project/sglang/pull/40955

For disaggregated EAGLE serving, target-only prefill leaves draft KV/proposal state uninitialized. #40953 therefore transfers the full FP32 draft proposal distribution needed for rejection sampling; top-k candidates alone are insufficient. #40955 adds an experimental correctness fallback that replays the committed prefix through target and draft models on decode, publishes draft state only after successful initialization, and explicitly accounts the replay tokens.

The authors emphasize that this fallback is **not a throughput optimization**: GPU transport, real-runner performance and stochastic sampling quality remain unvalidated.

**P51 action:** target state and draft/speculative state are separate ownership domains. If a PP/disaggregated stage does not construct draft state, downstream code must not infer/synthesize it silently. Either transfer the required state/probability identity or perform an explicit replay whose cost is separately accounted.

### NEW / WATCH — SGLang #40962: target graph resources can inherit draft runtime context accidentally

Source: https://github.com/sgl-project/sglang/pull/40962

Adaptive initialization built target resources while draft TP/MoE/A2A contexts were still active. In one TP16 deployment, this caused a target runner to inherit draft configuration and eventually hit a DeepEP hybrid-dispatch barrier timeout. The fix scopes draft context only around draft-resource construction and builds target resources after it exits.

**P51 action:** runtime/capture identity includes whether a resource is target-side or draft-side. Build/capture target kernels, communication plans and graph runners under target configuration; draft context must not leak into target resource construction.

### NEW — DS4 #1011 mixed Q2/Q4 GLM-5.3 receipt supports heterogeneous precision structurally

Source: https://github.com/antirez/ds4/pull/1011  
Fresh commit: `57e0b93bf624` at 2026-09-23 19:55:27 UTC.

A new Strix Halo / ROCm 10 mixed GLM-5.3-Flash artifact puts the routed gate/up/down experts in blocks 3-28 on the Q2 recipe while retaining Q4_K for all other tensors, including the complete embedded MTP block.

Measured resident mixed artifact:

- 4K prefill: **106.95 / 108.83 PP**
- 16K prefill: **103.08 PP**
- decode after 4K: **7.06 TG**
- decode after 16K: **6.85 TG**
- Short100 weighted NLL: **0.403247680**, first-token match 86/100
- Long8 weighted NLL: **0.643285013**, first-token match 6/8
- 512-token MTP timing: 236 accepted drafts / 37 rejections

The same PR's all-Q2 optimized arm is materially faster (~203 PP at 4K, ~184 PP at 16K; ~11.9/11.2 TG decode) but has worse reported weighted NLL (~0.459 Short100, ~0.657 Long8).

**Qualification:** GLM-5.3, ROCm/gfx1151, different quant recipes and no source-behavior certification. This is cross-family transfer only.

**P51 interpretation:** it is another real implementation where aggressively compressing the routed expert bank while protecting the rest, including MTP, moves the quality/speed frontier. It supports the *shape* of P51's heterogeneous allocation strategy but gives no numerical evidence for Flash-Next's 3.x-bpw source-like frontier.

### UPDATE / WATCH — llama.cpp #28439 M5 wide-query FlashAttention tuning

Source: https://github.com/ggml-org/llama.cpp/pull/28439

A fresh M5 tuning comment reports 882 wide-tile selections across 13 DK/DV pairs, six KV buckets, two tile counts and GQA 1/2/4/8/16/32 with **no clear losses**; the lowest selected-config ratio versus Q8 was 1.0115. For 192/192 at 64K KV and 1024 tiles, the reported gain is **1.276x at GQA8** and **1.228x at GQA32**. Tests pass 4,956/4,956 plus perplexity parity on the sampled models.

**P51 interpretation:** reinforces device/shape-specific Metal tuning and the value of larger query tiles in long-context prefill. M5 rows are explicitly not inherited by M4, and there is no M1 result, so no direct P51 target credit.

## Checked surfaces with no qualifying durable change

- **oMLX:** no P51-relevant new PR/commit in-window; only unrelated model/API work surfaced.
- **mlx-serve:** no PR/issue/commit activity in the exact window.
- **IST-DASLab/GSQ:** no issue/PR/commit activity in-window.
- **vLLM:** other in-window activity was reviewed; generic allocator/frontend/ROCm/CI changes did not alter P51 state. #58413 received only bot review activity; its prior external-state-restore result remains unchanged.
- **llama.cpp:** the only merged in-window commit was a backend-selection testing option; not performance evidence. #29030's fresh branch commit is captured above.
- **SGLang:** #40961 proposes fusing a DSV4 verify-side SWA scatter into an existing QK-norm/RoPE kernel but supplies no speed data; track, no target credit.
- **Hugging Face / Reddit / community search:** same-day Flash-Next quant/KV discussion exists, but no new controlled post-boundary xhigh/source-vs-quant behavioral receipt with a sufficiently precise timestamp was found. Do not promote anecdotes into the durable quality frontier.

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

**2026-09-23 20:42:43 UTC**
