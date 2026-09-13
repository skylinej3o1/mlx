# External runtime watch — 2026-09-13 12:37 ET

## Scope and freshness

Active lanes remain:

- Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4
- Qwen3.8-27B — one M1 Max 64 GB
- Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM
- DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4
- Blazer / custom ~5.x-BPW execution work where evidence transfers cleanly

This pass covers substantive source activity strictly after `2026-09-13 07:43:32 UTC` through `2026-09-13 16:37:16 UTC`.

Evidence timestamp means substantive source timestamp, not crawl time, rediscovery, rebase, comment-only churn or merge-only churn.

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Flash-Next — 2x M1 Max64 / TB4 | 40 tok/s @ ~128K active context | 400 tok/s | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | 25 tok/s | 110 tok/s native/exact-runtime | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | 120 tok/s | 250 tok/s | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | 15 tok/s | 180 tok/s | unchanged |

P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail evidence. External findings below do not reopen P69B8/B9/B10-C.

---

## 1. vLLM #56686 — live-context-bounded sparse candidate work + compile-shape bucketing

**FRESH NEW / HIGH-VALUE LONG-CONTEXT MECHANISM TRANSFER. Not active Apple-topology evidence.**

DeepSeek-V4.1-Flash on one 8x B200 TP8 node exposed a major graph-capture pathology: sparse-attention candidate work was sized by the model's 1,048,576-token context limit instead of the batch's live sequence lengths. At ~830 requests, candidate-block work accounted for roughly 5.8 ms of a 35 ms decode step, while a transient `[rows, 1M]` fp32 indexer buffer reached ~3.5 GB and could push the caching allocator into expensive `cudaFree` events.

The experimental branch:

- bounds decode-side logits by live `max_seq_len` rather than `max_model_len` where graph semantics permit it;
- uses a fixed graph-compatible grid whose inner work loops only over each row's live range;
- replaces full-width `torch.topk` + invalid-pick cleanup with an exact row-bounded candidate selector;
- buckets/pads eager prefill output-projection token counts and prewarms the resulting DeepGEMM shapes so first-seen shapes do not JIT-compile inside serving.

Controlled 1000-request ShareGPT workload, same model/work, warmup excluded:

- baseline: **24.6 s / 18,040 total tok/s**;
- optimized: **22.9 s / 19,390 total tok/s (+7.4%)**;
- large-decode-step median: **25.6 -> 22.2 ms**;
- single-request step: **6.2 -> 5.4 ms**;
- candidate buffer transient: roughly **3.5 GB -> ~4 MB** for the cited large batch.

The PR also documents a 3–3.6 s first-seen DeepGEMM compile stall for arbitrary eager prefill token counts; bucketing + explicit warmup moved that cost to startup.

**Promote:** under graph capture, fixed graph shape must not imply work proportional to maximum configured context. Distinguish static launch geometry from dynamic live-work span. For Flash-Next/QSA/DSA experiments, record `max_context`, live span, physical workspace extent, touched span, per-row candidate count and whether full-width reductions/top-k remain. Also record eager-shape JIT key cardinality and first-seen compile stalls.

---

## 2. vLLM #56692 — DFlash/DFlash2 full-attention causality config bug

**FRESH NEW / DIRECT DFLASH2 CONFIG-CORRECTNESS EVIDENCE.**

Speculators-format DFlash checkpoints with `sliding_window_non_causal=False` were mapped to a global causal flag, incorrectly making full-attention draft layers causal even though the training contract keeps full attention bidirectional within the draft block. The fix restores per-layer semantics: causal SWA can remain causal while full-attention layers stay non-causal. The same converter is shared by DFlash2.

Regression suite:

- unpatched: **6 failed / 31 passed** in the newly covered full/mixed/unspecified-layer cases;
- patched: **46 passed**.

Model-level B300 diagnostic using identical DFlash weights and corrected draft RoPE:

- short prompts: acceptance length **3.026 -> 3.147**, throughput **2715.7 -> 2748.9 tok/s**;
- 16K prefix: acceptance length **2.916 -> 3.078**, throughput **383.9 -> 393.7 tok/s**.

This is not Apple performance evidence, but it is directly relevant to our Q6/Q8 DFlash2 challenger work.

**Promote:** draft attention causality is part of execution identity at **per-layer granularity**. Record full-vs-SWA layer type, local/global causal override, converter path and actual backend requirement. A low-acceptance DFlash result is invalid as architecture evidence until masking semantics match the training contract.

---

## 3. vLLM #56694 — candidate-pruned DSpark Markov projection

**FRESH NEW / SPECULATIVE-DRAFT MECHANISM TRANSFER.**

DSpark's Markov bias normally projects rank-space state through a full-vocabulary W2. The PR restricts that projection to a candidate union drawn from top base logits and top Markov-bias candidates, then lets target verification/sampling preserve the final target distribution.

The submitted Hopper sweeps over top-k values 1/8/16/32/64/128 on GSM8K and C-Eval report roughly **5–8% output-throughput gains** with little accepted-length loss across tested settings.

This is not evidence for our Lightning-MTP champion itself, but the principle is useful: **draft-side full-vocab work can be pruned independently of target verification when candidate coverage is certified.**

**Promote as experiment idea only:** inspect whether any of our draft/proposal paths perform full-vocab projection or scoring that can be reduced to a verifier-safe candidate set. Do not infer the reported percentage onto M1 or onto Lightning MTP.

---

## 4. vLLM #56709 — MTP retained-history / SWA offload reachability

**FRESH NEW / LONG-CONTEXT STATE-CORRECTNESS EVIDENCE.**

Native KV offload could admit a cache hit based on ordinary SWA coverage while MTP's extra retained tokens required an older block that lookup never checked and the producer might never have stored. The result could be an assertion after the hit had already been admitted.

The fix extends lookup coverage, in-flight checks and producer store reachability to `extra_retained_tokens` while preserving the normal lower bound. Focused regressions were **102 passed** patched versus **14 failed / 88 passed** with the production fix reverted. GPU smoke tests exercised two MTP modules, four speculative tokens, SWA window 32 and three retained tokens, including rejected-draft re-prefill, with identical cold/warm outputs.

**Promote:** speculative state identity includes *retained history beyond the nominal attention window*. Cache lookup, storage reachability, transfer ownership, restore coverage and rejection/re-prefill must all agree on that retained span. This is directly applicable to long-context MTP/PP2 correctness gates even though the implementation is CUDA-side.

---

## 5. vLLM #56683 — parallel JIT warmup for independent variants

**FRESH NEW / COMPILE-LIFECYCLE MECHANISM.**

Nine cold-cache DSV4.1 mHC pre-norm variants on GB200 compiled in:

- sequential: **95.03 s**;
- four compiler workers: **43.39 s**;
- isolated compile-stage speedup: **2.19x**.

A later real-weight TP4 startup compiled four remaining variants in parallel in ~14 s and completed a greedy smoke. This is not an end-to-end startup speedup claim.

**Promote:** after controlling warmup-key cardinality, independent kernel variants may be compiled concurrently. Our benchmark identity should distinguish key enumeration, serial elaboration, compile scheduling, compiler-worker count, cache state and final startup wall time.

---

## 6. oMLX #3634 — multimodal long-agent TTFT can be dominated before prefill

**FRESH MERGED / APPLE AGENT-RUNTIME EVIDENCE. Text-only lanes unaffected.**

A repeated-screenshot agent loop was re-decoding every historical image on every turn before prefill. A DeepSeek-V4.1 multimodal session around 200K context observed roughly **22 s** of image decode before cached-block restore/prefill became visible.

The merged content-hash decoded-image cache converts cumulative re-decode from quadratic in turn count to one decode per unique image. Real-server Mac Studio A/B over six cumulative-image turns reported TTFT reductions of roughly **21–35%** and eliminated **86%** of PNG decode-chunk work in that run.

**Promote for agent benchmarking:** TTFT decomposition starts before model prefill. Track request parsing/media decode, feature lookup/encode, KV restore, actual prefill, compile and first decode separately. Do not attribute pre-prefill host work to PP or model kernels.

---

# Fresh-screen negatives / non-promoted artifacts

- No fresh exact dual-M1 Flash-Next TG/PP receipt appeared in the source window.
- No fresh exact M1 Max64 Qwen3.8-27B receipt appeared.
- No fresh exact RTX5070Ti16 Qwen3.8-27B throughput receipt appeared.
- No fresh exact dual-M1 DS4-0731 receipt appeared.
- `antirez/ds4` had no in-window commits.
- `llama.cpp` in-window activity screened as SYCL/CI/Vulkan/general maintenance; no new relevant Metal/Qwen active-lane receipt was promoted.
- Fresh web/HF screening surfaced current Qwen3.8-Flash-Next oQ6/oQ8 artifacts and DFlash2 model/community pages, including stronger-hardware results, but crawl/update visibility was insufficient to prove a new post-boundary exact active-topology receipt. Keep as backfill/transfer context only.
- oMLX #3635 improves evaluation worker scheduling; useful harness work, but it does not change model/runtime throughput and is not promoted as a target-performance result.
- vLLM #56682 and related startup work reinforce initialization accounting but do not provide an isolated active-lane throughput result.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary; TP2 remains control. Add to the certification/optimization queue:

1. graph-compatible **live-span-bounded** candidate/QSA/DSA work rather than max-context-width work;
2. workspace/touched-span accounting separate from graph launch shape;
3. first-seen shape/JIT compile detection and bucketing where exact;
4. MTP retained-history coverage across store/lookup/restore/rejection;
5. pre-model TTFT decomposition for multimodal/agent workloads;
6. existing TB/RDMA interface, watchdog, failure/reload, helper ABI, PLE, verifier peak, pointer/state and long-context gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement and no P69 ordering change. DFlash2 experimentation gets one important new gate: certify **per-layer draft masking semantics** before reading acceptance/speed as architecture evidence. DSpark candidate pruning is an external draft-side experiment idea only. P69B12 remains frozen/promoted; P69B13 remains next.

## RTX5070Ti16

No target movement. Previous SM120 physical-stride gate remains. This pass adds no exact 5070-Ti speed receipt. The JIT-shape/warmup and draft-config lessons transfer to CUDA methodology but do not alter the 120/250 objectives.

## DS4-0731 dual M1

No target movement. #56686 is later-V4.1/B200 evidence but strongly reinforces live-context-bounded sparse work and first-seen compile accounting. #3634 is later-V4.1 Apple multimodal runtime evidence; use it only for host-side TTFT methodology.

---

# Standing rules added/reinforced

- Static graph geometry does not justify work over configured maximum context; certify dynamic live-work span and touched workspace.
- Draft masking/casuality is per-layer execution identity, not a single model-wide boolean unless the training/config contract proves it.
- Draft-side full-vocabulary work may be candidate-pruned only with verifier-safe coverage and acceptance/correctness certification.
- MTP retained-history span is part of cache/store/restore identity even when it lies outside the nominal SWA window.
- Warmup-key cardinality and compiler scheduling are separate; parallel compilation is an optimization surface after key discipline.
- TTFT includes host work before prefill; model PP cannot explain media decode / request preprocessing stalls.
- Merge/crawl time does not refresh older evidence.
- Requested/configured route remains distinct from built/available/admitted/executed route.
- Final-output correctness does not certify speculative correctness; acceptance/task quality remain separate.
- Component/kernel gains do not move canonical targets without exact active-topology reproduction or exceptionally strong transfer evidence.
- **P69 remains isolated.**
