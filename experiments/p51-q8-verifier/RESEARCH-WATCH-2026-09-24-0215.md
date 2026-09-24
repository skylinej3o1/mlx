# Project 51 primary-lane research watch — 2026-09-24 02:15 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 04:42:49 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 06:15:43 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared, and no new post-boundary DASLab / GSQ-RCO source-vs-quant xhigh behavioral certification appeared.

This pass is nevertheless useful in three ways:

1. DS4 landed a fresh exact-family Metal implementation of **2-8 bit TurboQuant KV** that preserves dense QSA selection and protected recurrent/speculative state while materially reducing long-context memory.
2. oMLX added **Splash-inspired packed Q4 projections + speculative overlap** on M5 dense Qwen3.8-27B and measured an additional B1/B2/B4 uplift on top of its existing MTP path, directly demonstrating that hardware-specific kernels and speculation can stack.
3. Fresh SGLang merges reinforce two recurring P51 rules: **tiny-M MoE deserves its own kernel**, and state capacity/accounting must use the exact geometry by which state is addressed.

## Findings

### NEW — DS4 #1115: 2-8 bit TurboQuant KV for Qwen3.8-Flash-Next on Metal

Source: https://github.com/antirez/ds4/pull/1115  
Created: **2026-09-24 05:08:40 UTC**.  
Primary commit: **485902a7f46e**.

DS4 adds `DS4_QWEN4_KV_BITS=<2..8>` for Qwen3.8-Flash-Next attention K/V on Metal using TurboQuant rows:
- randomized-Hadamard rotation;
- fixed data-oblivious Lloyd codebook;
- exact f16 row norms;
- width-specific fused encode/decode/prefill paths;
- no 1-bit mode because two centroids carry insufficient KV signal.

Crucially, the design **does not quantize the whole state machine**:
- the QSA indexer remains dense f32/f16;
- the last trunk attention layer remains f16;
- the MTP/nextn block remains f16;
- only 11 of 13 production attention layers use packed KV.

Therefore sparse block selection remains bit-identical to the f16 run; quantization perturbs gathered K/V values rather than changing which blocks are selected.

For a 1M-token session, DS4 documents:

| KV width | K+V cache | total context state |
|---|---:|---:|
| f16 | 26.0 GiB | ~33.4 GiB |
| 8-bit | 15.1 GiB | ~22.5 GiB |
| 6-bit | 12.3 GiB | ~19.7 GiB |
| 4-bit | 9.6 GiB | ~17.0 GiB |
| 3-bit | 8.2 GiB | ~15.6 GiB |
| 2-bit | 6.8 GiB | ~14.2 GiB |

The remaining ~7.4 GiB is dominated by fixed dense indexer/recurrent/block-key state, which is why savings flatten below ~4 bits.

Golden-row round-trip cosine:
- 8-bit: **0.99995**
- 6-bit: **0.99960**
- 4-bit: **0.99640**
- 3-bit: **0.98429**
- 2-bit: **0.94796**

DS4 states 6/8-bit are within the noise band of f16 on its official continuation suite; 4-bit is the production balance point inherited from the oMLX design. This is not a full xhigh behavioral certification of the 2/3/4-bit modes.

Performance characteristics:
- fused chunked prefill at 1024-token chunks: **1141 tok/s packed vs 1146 f16**, effectively neutral in that aggregate cell;
- isolated 16-query x 32768-key attention read: **5.9 ms f16**, **7.2 ms 2-bit**, **7.3 ms 4-bit**, **7.7 ms 8-bit**, with 3/5/6/7 slower because packed fields straddle words;
- encoding overhead is roughly +0.011 to +0.014 us per K/V row.

Thus lower byte width is not automatically faster: unpack arithmetic can dominate. Widths dividing 32 cleanly (2/4/8) have a materially better unpack path than 3/5/6/7.

Session checkpoints encode the KV width and reject cross-width restore.

**Classification:** NEW exact-family Metal long-context-state evidence.

**P51 consequence:** strong independent confirmation of the existing P51 extreme-context rule: **compress bulk attention K/V while protecting selection/indexer, recurrent and speculative-sensitive state**. It also adds a new kernel-design rule: bit width must be chosen jointly with pack/unpack geometry; 6-bit can be slower than 8-bit despite moving fewer bytes.

For the current ~128K target this is primarily a memory-headroom lever, not a demonstrated TG lever. It could free memory for higher-quality weights, more resident experts, or safer state headroom, but no M1/PP2 throughput credit is assigned.

### NEW — DS4 #1115 tokenizer/template fixes: rendered prompt bytes are cache identity

Source: same PR, commit **f5e419dc1b0e**.

The second half of #1115 fixes three Qwen prompt-rendering mismatches:
- reasoning blocks;
- JSON/tool-schema Unicode escaping;
- control tokens embedded in client text.

Because the prompt is tokenized rather than parsed after rendering, a seemingly cosmetic escaping difference shifts every subsequent token and can silently invalidate existing KV checkpoints.

On a real 167K replay request, the corrected renderer matched the previously captured canonical render byte-for-byte:
- **572,480 rendered bytes**;
- 608 raw em dashes;
- zero escaped replacements.

The live retention regression measured:
- prompt size **2053 -> 1216 tokens** through the retention window;
- **1279/1281** tokens reused from the live session;
- **1281/1281** reused from disk after restart.

**P51 consequence:** rendered-template/tokenizer semantics are part of persistent-cache identity. Cache/state certification must include the exact rendered token stream, not only conversation objects or hashes of user-visible text. Template upgrades can invalidate state even when visible turns appear unchanged.

### UPDATE — oMLX #3797: hardware-specific packed projections stack with Lightning MTP

Source: https://github.com/jundot/omlx/pull/3797  
Fresh commit: **52e4de5ac547** at **2026-09-24 04:46:07 UTC**.

The prior state already recorded #3797's batched-DFlash / small-M verify work on M3 Ultra. The fresh commit adds an M5 path for dense Qwen:
- Q4 projections repacked for the tensor unit at load, explicitly using Splash's M5 packed-projection work as a reference;
- DFlash2 drafter projections packed as well;
- the next draft block is queued before the host synchronization;
- command-buffer caps are raised only during speculative-decode steps;
- adaptive Lightning MTP depth defaults to 4 on dense Qwen on NAX/M5.

M5 Max, Qwen3.8-27B oQ4e, Lightning MTP, same coding prompts:

| concurrency | main | PR | change |
|---|---:|---:|---:|
| B=1 | 65.7 TG | **71.9 TG** | **+9.6%** |
| B=2 | 76.7 | **108.2** | **+41.1%** |
| B=4 | 99.9 | **145.1** | **+45.2%** |

**Classification:** UPDATE / fresh exact-27B stronger-Apple evidence.

**P51 consequence:** this is direct evidence that **hardware-specific packed projection work and speculative/batched runtime work stack rather than merely substituting for each other**. The huge B2/B4 gains are mostly a concurrency result and must not be transferred to B1 P51, but the B1 +9.6% is still meaningful mechanism evidence.

It also validates the broader co-design direction discussed for the 27B experimental lane: quant format, packed kernel, verify geometry and drafting policy should be optimized together.

### NEW — oMLX #3797 commit 95ca02f: speculative-depth costs must be revalidated per request

Fresh commit: **95ca02f6bc3a** at **2026-09-24 06:07:36 UTC**.

The Lightning MTP depth controller previously inherited timing estimates from the preceding request and could skip remeasuring depths already seen. The fix:
- retains prior acceptance estimates as a seed;
- marks inherited timing costs stale;
- performs a fresh warmup sweep for the new request;
- refuses to consume invalid/non-timing samples as the new cost.

**P51 consequence:** **MTP timing cost is request/context dependent enough that cross-request reuse is only a prior, not truth**. Reuse acceptance priors if useful, but revalidate actual verify-cycle cost for the current context/hardware state before selecting depth. This is particularly important for long-context P51 where the cost curve changes as QSA/KV work grows.

### UPDATE / fresh merge of older evidence — SGLang #40204: tiny-M MoE specialization yields system-level gains

Source: https://github.com/sgl-project/sglang/pull/40204  
Merged commit: **32290dda2cea** at **2026-09-24 05:45:33 UTC**.

This Qwen3.5 MXFP4 / MI355X PR is cross-family and cross-hardware, but it independently targets the same tiny-M MoE regime as mlx-serve #519.

Dedicated small-M kernel vs generic AITER fused-MoE:
- 1 token: **50-60 -> 29-33 us**, ~42% faster;
- 4 tokens: **57 -> 32 us**, -44%;
- 16: **88 -> 66 us**, -25%;
- 32: **117 -> 104 us**, -11%;
- 48: parity.

With real EAGLE MTP:
- concurrency-1 TPOT p50: **3.66 -> 3.22 ms (-12.0%)**;
- completed requests in one hour: **559 -> 594 (+6.3%)**;
- normalized interactivity p50/p90: **+8.4% / +11%**;
- concurrency-8 normalized interactivity: about **+10%**.

Accuracy remained within run variance on GSM8K/GPQA.

**Classification:** UPDATE / fresh merge of older performance evidence.

**P51 consequence:** strengthens the general rule that **verify/decode matrices in the 1-40-row regime are a distinct kernel class**, not a degenerate case of throughput-oriented MoE GEMMs. This is supportive cross-hardware evidence for Apple7 verify-first kernels; no numeric transfer.

### UPDATE / fresh merge of older evidence — SGLang #40337: state sizing and state addressing must use the same geometry

Source: https://github.com/sgl-project/sglang/pull/40337  
Merged commit: **90663ccb418a** at **2026-09-24 05:05:32 UTC**.

A DSV4 C4 compressed-state pool used one quantity named `swa_page_size` for sizing and a different quantity for addressing:
- sizing used window size 128;
- addressing used scheduler page size 256.

The result was exact **2x over-allocation** of the C4 ring.

For published V4 checkpoints this represented:
- ~**10.5% phantom share of every SWA token**;
- fixing it buys roughly **+11.7-11.8% SWA token capacity** at the same memory;
- absolute waste from **0.90 GiB/rank** on V4-Flash 262K to **5.16 GiB/rank** on V4-Pro 1M.

Post-fix allocation/addressability probes show only deliberate small padding headroom. A 5,276-request GSM8K A/B found no stable accuracy regression.

**Classification:** UPDATE / fresh merge of older evidence.

**P51 consequence:** extends the state-byte rule from “count every state class” to **“size each state class with the exact geometry used to address it.”** Page size, window size, ring size and speculative tail geometry must not share ambiguous names or inferred equivalence.

### UPDATE — llama.cpp #29340 adds an always-on threadgroup-memory guard

Source: https://github.com/ggml-org/llama.cpp/pull/29340  
Fresh comment: **2026-09-24 05:27:34 UTC**.

The previously recorded quantized-FA overflow fix now adds a backend memory-limit assertion, so the failing Metal shapes are caught even without Metal validation environment variables.

**P51 consequence:** no planning change; strengthens the kernel-certification rule that verify width + KV type + tensor shape must be rejected before dispatch when threadgroup-memory occupancy is invalid.

## Checked surfaces / negative results

- **IST-DASLab/GSQ:** no post-boundary issue, PR or commit activity.
- **mlx-serve:** no post-boundary repository activity in this window; #517/#519 therefore remain as recorded in the previous watch.
- **Splash / paperniuk Apple7 branch / splash-plus:** no post-boundary code activity. The M1 Q4 result remains recovered evidence, not a new delta.
- **llama.cpp:** no new Flash-Next MTP performance receipt after the boundary; #29340 only gained the guard above.
- **oMLX:** #3797 is the substantive exact-27B update; other fresh PRs were not P51-relevant.
- **vLLM:** no new exact-family Apple/Flash performance receipt. The previously recorded #58463 critical-path null remains unchanged.
- **Community/Hugging Face:** current searches surfaced a same-day M5 Ultra Flash-Next benchmark post, but the search surface did not expose a precise publication timestamp sufficient to prove it was after the prior hard boundary, so it is **not promoted into this delta**. No new precisely timestamped ByteShape or DASLab behavioral-quality receipt was found.
- Fresh searches also surfaced older low-bit-KV/MTP negative evidence on a vLLM/5090 path; the underlying repositories had no commits in this freshness window, so it remains background rather than NEW evidence.

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
- single-M1 27B: **25 TG** canonical target; the Apple7 + heterogeneous-quant + verifier co-design lane remains an experimental upside branch rather than a promoted target.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 06:15:43 UTC**
