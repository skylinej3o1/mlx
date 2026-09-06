# External runtime research watch — 2026-09-06 12:45 ET

Starting branch checkpoint: `04aeef52051d6fdda7ac49d4a507be2aadc2a566`

Starting hard freshness cutoff: **2026-09-06 14:14:07 UTC**.

## Executive result

This pass is **material for correctness certification and experiment ordering, but does not move any canonical TG/PP target**.

No fresh sustained receipt surfaced on the exact 2x M1 Max 64 GB / TB4 Flash topology, the exact 2x M1 Max DS4-0731 topology, the exact M1 Max 64 GB Qwen3.8-27B serving lane, the exact single RTX 5070 Ti Qwen3.8-27B lane, or RTX 5070 Ti Tiel Coder.

The useful changes are:

1. Qwen4-exp QSA nondeterminism is now reproduced independently in llama.cpp and is sharper than an ordering bug: tied expanded cells can change the **selected set** itself across calls and devices;
2. fresh vLLM work separates four independent correctness axes — QSA selection, MoE finalize determinism, external/async PLE lifecycle, and batch-shape/concurrency — and traces one graph-era PLE path to every forward consuming the **previous step's PLE output**;
3. an exact M1 Max 64 GB oMLX report shows byte-identical greedy requests can change completion and length solely because they share a batch, including a non-MTP control, making batch-composition invariance a native Apple gate rather than CUDA-only transfer evidence;
4. rMLX found five speculative sidecar loops silently decoded greedily for any `temperature > 0`; production sampler correctness therefore needs a distribution-level oracle, not only greedy/verifier-only equivalence;
5. fresh M1 Ultra oMLX measurements show decode/MTP small-N MoE dispatch needs a different threshold from wide prefill — the block kernels were 2–2.7x slower over much of the small route-count range, while a routing fix improved a measured server workload materially;
6. llama.cpp #28495 shows warm multi-slot state can cut repeated long-prompt PP by roughly half even when requests are sequential, so request-1 PP is not a sufficient serving ruler;
7. llama.cpp #28506 provides fresh 2x RTX 5070 Ti fit evidence showing requested tensor split ratios can drift at tensor-granularity and OOM despite nominal aggregate headroom; this is allocation/provenance evidence, not a new speed receipt.

`RESEARCH-TARGETS.md` remains untouched.

---

# FRESH / material

## llama.cpp #28497 — QSA tied-cell top-k can change the selected set, not merely output order

Issue created **2026-09-06 14:50:51 UTC**.

Physical reproductions include:

- RTX 3090 / sm86;
- RTX 4060 Ti / sm89;
- RTX 5060 Ti / sm120.

The Qwen4-exp QSA path scores compressed blocks, expands each block score to its constituent cells, then asks `ggml_top_k` for `indexer_top_k + compress_ratio - 1` cells. The cutoff can land inside a group of cells with exactly equal scores. CUDA 13 / CCCL CUB `DeviceTopK::MaxPairs` does not define deterministic tie membership, so repeated calls can choose different cells from the tied boundary block.

Twenty-call kernel samples reported selected-set changes at multiple sizes, including:

- 4,098 cells: 4 set changes on sm89;
- 131,074 cells: 3 on sm120;
- 196,610 cells: 13 on sm89 and 8 on sm120;
- 262,146 cells: 3 on sm120 and 10 on sm86.

Output order changed on every call at every tested size. Exactly one block was partially selected at the tie boundary, and separate processes could choose different cell IDs from that block.

Real-model reproduction used Qwen3.8-Flash-Next UD-Q4_K_XL, q8 KV, parallel 1, no draft, temperature 0 / top-k 1 and prompt cache disabled. Shorter prompts remained stable, while ~2.4K and ~9.1K prompts produced four different streams across four runs, with divergence beginning within tens of generated tokens. Disabling CUB top-k and falling back to stable radix-sort selection restored repeatability.

### Promotion

The Flash QSA correctness oracle must distinguish:

- compressed-block selected set;
- expanded-cell selected set;
- tie-boundary membership;
- selected order;
- first divergent prompt/generation position;
- serial and concurrent repeats around the selection boundary.

A candidate that only stabilizes order but changes which tied block/cell survives does not pass. Consider block-level selection before expansion as a reference/candidate where practical.

This is direct CUDA/model evidence and strong architecture-mechanism evidence, not an Apple rate ruler.

---

## vLLM #54521 + #53899 — correctness decomposes into QSA, MoE finalize, PLE epoch ownership and concurrency

Fresh post-cutoff updates sharpen the earlier QSA nondeterminism story.

### Position-resolved Qwen3.8-Flash-Next regression

Reported environment:

- GB10 / sm121;
- current vLLM main dev401;
- no speculative decoding;
- prefix cache disabled;
- batch token budget 16,384;
- temperature 0;
- `prompt_logprobs=5`;
- eight sequential and eight concurrent identical requests;
- prompt lengths around 1,460 / 1,999 / 5,960 tokens, straddling `indexer_budget=2048`.

Stock behavior diverged from **position 1**, with thousands of top-1 flips and 7–8 distinct completions out of eight in affected cells.

Disabling fused MoE finalize removed one source of variability. Combining deterministic MoE finalize with deterministic `persistent_topk` removed additional above-budget divergence attributable to the QSA path.

With both of those changes **and CUDA graphs disabled**, sequential requests became bit-exact across all three lengths: zero top-1 flips, zero spread and one completion class.

Graphs enabled still left a deterministic split between the cold first request and later warm requests. That remaining axis traced to a separate PLE CPU-offload semaphore defect.

### #53899 — every graphed forward could consume the previous step's PLE output

The reported failure sequence is especially important for stateful/external PLE designs:

1. graph capture signals a dummy PLE result;
2. a real request submits real offload work;
3. the first wait consumes the stale dummy signal;
4. the request releases/resets the semaphore;
5. the real worker finishes later and signals readiness for the **next** forward;
6. the pipeline remains one PLE result behind for the server lifetime.

Direct PLE-buffer row counts showed the stale-step relationship: the first real step consumed zero rows; subsequent steps consumed the previous request/step's row count.

A small semaphore reset on the model stream before the real request restored own-step ownership. With that fix, sequential output matched the graph-disabled path and position-resolved sequential tests at 1,460 / 1,999 / 5,960 tokens reported zero flips and one completion class.

But concurrent requests still showed position flips at the larger two shapes even with graphs disabled. Thus concurrency/batch composition remains a **separate** axis after QSA, MoE finalize and PLE epoch bugs are removed.

### Promotion

Flash exact-runtime certification now treats these as four independent gates:

1. **QSA selection semantics** — set, order and tie membership;
2. **MoE finalize determinism** — especially routed expert accumulation/reduction;
3. **async/external PLE lifecycle** — request/step epoch ownership, cold-first request and graph/capture state;
4. **batch-shape/concurrency invariance** — identical and mixed prompt batches.

Use position-resolved teacher-forced logprobs/top-1 plus final completion hashes. Test cold-first versus warm, graphs/compiled path off/on where applicable, and sequential versus concurrent.

The critical general rule is: **same-prompt-twice after warmup is not a sufficient correctness oracle**. A stale one-step pipeline can look perfectly repeatable after the first request.

---

## oMLX #3476 — exact M1 Max 64 GB batch-composition divergence, independent of MTP

This issue predates the hard cutoff but received a fresh update after it and is newly surfaced in this pass.

Physical environment:

- macOS;
- **M1 Max 64 GB / 32 GPU cores**;
- oMLX 0.6.4;
- cache disabled;
- Qwen3.6-35B-A3B-oQ6-fp16-mtp plus a small Qwen3.5-0.8B control.

Byte-identical greedy requests (`temperature=0`, same seed/body) were stable serially but diverged when overlapped.

Small non-MTP model:

- 4 serial requests: one identical hash class;
- 4 parallel requests: one request kept the serial hash, while three batched rows shared a different hash;
- measured wall time confirmed actual overlap.

Qwen3.6-35B-A3B:

- serial: 3/3 identical 67-token completion;
- parallel: the same prompt produced recurring completion classes of **67, 72 and 102 tokens**.

Setting `max_concurrent_requests=1` and restarting restored identical results; parallel callers then formed the expected queue staircase.

The reporter separately A/B tested MTP off/on in serial mode and found identical output. The small model does not carry MTP, so this failure is not explained by speculative decoding.

### Promotion

Batch-composition invariance becomes an explicit **Apple-native** gate:

- concurrency 1 / 2 / 3 / 4;
- identical prompts and mixed prompt lengths/content;
- no-MTP first, then MTP;
- output hash plus position-resolved logits/logprobs where practical;
- record which rows actually shared a batch and the effective batch width at each decode step.

For the turnkey appliance, reproducibility cannot be certified from isolated B1 runs and then assumed under multi-agent serving.

This is direct M1 Max hardware evidence, but on adjacent Qwen models rather than Flash-Next, so it changes the test plan rather than Flash performance targets.

---

## rMLX `79f01a37268335781f0395216dfc52c3e1f7c326` — speculative sidecars silently ignored production temperature

Fresh commit timestamp: **2026-09-06 16:42:06 UTC**.

The prior implementation allowed any `temperature > 0` request to reach one of five sidecar speculative loops, but those loops still decoded greedily. The sampling configuration never reached the speculative sidecar path, while logs could imply stochastic acceptance was active.

This matters because normal checkpoint defaults commonly use nonzero temperature; greedy-only regression tests therefore could pass while the production serving law was wrong.

The corrected design keeps a sidecar proposal as an argmax point mass if desired, while the verifier draws from its own requested post-sampling distribution at every verified position. The proposal controls the speculative walk depth, not the output distribution.

A `VerifierDraw` now owns per-request sampler configuration and RNG state for the seed token and each speculative round.

Important remaining limitation: penalties and logit bias are still not propagated to every speculative arm. The fresh work makes that limitation visible rather than silently pretending full support. The sampled sidecar path also pays host softmax per verified position, so there is not yet a throughput promotion from this change.

### Promotion

MTP certification splits **greedy semantic equivalence** from **production sampling-law equivalence**.

For nonzero-temperature serving, record/verify:

- resolved temperature / top-p / top-k;
- seed and RNG ownership per request;
- verifier distribution at each accepted/rejected position;
- rollback positions inside a speculative round;
- distribution-level surprise/logprob against a plain-verifier control;
- unsupported penalties / logit bias must fail closed or be prominently declared.

Token equality on a few greedy prompts is not sufficient to certify speculative sampling.

---

## oMLX `8327920452bd4180407f8fd8c4100f0a4dafca67` — small-N decode/MTP MoE needs a different dispatch regime from wide prefill

Fresh merged commit at **2026-09-06 14:18:11 UTC** combines a QSA decode-side sync removal with restoration of a more appropriate MXFP4 dispatch policy.

### M1 Ultra direct measurement — GLM-5.3-Flash expert routing

On M1 Ultra with real GLM-5.3-Flash expert weights, 2-bit group64:

- sorting becomes worthwhile around ~32 routed rows;
- affine block kernels do not beat plain `mx.gather_qmm` until roughly ~1,024 routed rows;
- over much of the 64–900 row region, the block kernels were **2–2.7x slower**;
- wide prefill chunks at >=512 tokens / >=4096 routes still correctly favor block kernels.

A server B=8 / 300-token-per-request measurement moved step time **278.5 -> 173.5 ms** and aggregate generation **28.7 -> 46.1 tok/s** after the route policy was corrected.

This is an adjacent GLM/M1-Ultra physical result, not a Flash M1-Max rate ruler. The portable mechanism is the important part: **decode and multi-position verify are small-N workloads, while prefill is wide-N**. One dispatch threshold should not be assumed optimal for both.

### QSA row-width crossover

The same fresh oMLX change also incorporates prior Qwen3.8-Flash-Next M5 measurements showing the official masked QSA path can win for tiny 1–4-row decode/MTP work, while gathered selected-K/V wins as row width grows. Pooled index-prefix retention also reduces repeated repooling work at long context.

### Promotion

After exact baseline freeze, benchmark Flash target operations by effective row/route count:

- B1 decode;
- MTP verify widths 2/3/4+;
- B2/B4 concurrent decode;
- small incremental prefill;
- wide cold prefill.

Record the **actual selected kernel route** and route-count distribution. Do not promote a wide-prefill winner into decode merely because it has the same operator name.

---

## oMLX `2aab2ce3ce2f4254abd0c99a5ff64efb98215d3a` — resource/headroom state must be engine-worker local

Fresh commit at **2026-09-06 14:15:35 UTC** scopes SDPA headroom providers to the actual engine worker instead of a shared/global registration that multiple schedulers could overwrite or clear.

The failure class is relevant to the planned multi-agent appliance even though this exact code is oMLX-specific: one engine's construction/teardown could change another engine's memory/headroom behavior if provider state is global rather than worker-local.

### Promotion

Any resource/correctness state used for admission, PLE residency, recurrent state, draft slots or cache restoration should have explicit ownership:

- request-local where request semantics differ;
- slot-local for persistent serving slots;
- engine-worker-local for backend/device state;
- process-global only when the object is genuinely immutable/shared by contract.

Include engine teardown/reload while another request remains active in the multi-engine stress suite where relevant.

---

## llama.cpp #28495 — warm multi-slot state can collapse long-prompt PP even for sequential requests

Issue created **2026-09-06 14:26:50 UTC**.

Physical primary report:

- Radeon AI PRO R9700 32 GB;
- Qwen3.8-27B UD-Q5_K_XL;
- `-np 2`, `--kv-unified`;
- requests issued sequentially, not concurrently;
- ~100,607-token prompt;
- `cache_prompt=false`.

Stock master reported:

- `-np 2` PP: **335.7 -> 151.4 -> 154.5 tok/s** from request 1 to later requests;
- `-np 1`: **323.5 -> 322.3 -> 321.9 tok/s**;
- `-np 2` TTFT: roughly **299.7 s -> 664.6 -> 651.1 s**;
- memory was reported flat with no spill;
- generation throughput was unaffected;
- disabling speculative decoding did not remove the collapse.

A separate Strix Halo user comment reports a similar warm-state PP degradation and points at unified KV as a suspect, but that follow-up remains user-reported and not a confirmed cross-backend root cause.

### Promotion

Cold/fresh-process PP is not enough for the appliance. Add a warm-slot matrix:

- slot count / `np`: 1 / 2 / 3 / 4;
- request 1, request 2, request 3+;
- sequential first, then concurrent;
- cache reuse deliberately disabled for the cold-PP cells;
- record persistent KV/recurrent metadata, slot ownership, effective backend route and PP/TTFT.

A production cold-PP claim should explicitly say whether it is first-request/fresh-slot or repeated-request/warm-slot.

This is ROCm transfer evidence; it does not move Apple PP targets.

---

## llama.cpp #28506 — 2x RTX 5070 Ti tensor-split fit can drift from the requested ratio

Issue created **2026-09-06 16:49:53 UTC** during this live pass.

Physical setup:

- Linux;
- llama.cpp 0.4.0-dev build 10825 / `9e0e22059`;
- **2x RTX 5070 Ti 16 GB**;
- Qwen3.8-27B Q5_K_M;
- 190K context;
- q8 KV;
- draft-MTP depth 3;
- tensor-split mode.

The reporter finds the realized split can drift materially from requested `-ts` because each tensor's split point is floored to fixed granularity. The bias accumulates over the model and can OOM a configuration that appears to fit from the requested aggregate ratio.

`-ts 0.5,0.5` reportedly loads without the vision encoder at about **14,642 MiB of 16,303 MiB** on each device. Small asymmetric changes intended to reserve room for the vision encoder can instead OOM.

### Promotion

This is **fit/provenance evidence, not a TG/PP receipt**.

If the 5070 lane ever expands to multi-GPU or asymmetric placement, record:

- requested tensor split;
- realized bytes/tensors per device;
- split granularity/rounding policy;
- graph/draft/KV allocations after model load;
- peak headroom under the real context.

For the current single-5070 Qwen/Tiel shootout, the standing rule remains simpler: compare actual residency/offload and real coding-agent wall time, not nominal model size.

---

# Focused follow-up status

- **antirez/ds4 PR #991:** still open at the same inspected head; no post-cutoff update surfaced.
- **antirez/ds4 main:** no post-cutoff commit surfaced.
- **oMLX #3462:** no post-cutoff comment surfaced; real-agent capture/store-efficacy gate remains active.
- **oMLX #3464:** no post-cutoff comment surfaced; explicit generated-token/TG provenance remains active.
- **vLLM #53504:** no post-cutoff comment surfaced; canonical recurrent/attention reusable-boundary gate remains active.
- **vLLM #55533:** no post-cutoff comment surfaced; actual scheduled-sequence occupancy remains active.
- **MLX #4409:** no post-cutoff result surfaced.
- **llama.cpp #28425 / #28433 / #28448 / #25187:** no post-cutoff comments surfaced; their standing rollback, per-slot context, allocator-identity and MTP-head quant gates remain active.
- **llama.cpp #28484:** no newer result; retain its downgraded/not-currently-reproducible status.
- **Tiel Coder:** no fresh exact RTX 5070 Ti receipt surfaced.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 generated-token throughput or new exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max serving TG/PP receipt. oMLX #3476 is direct M1-Max correctness evidence on adjacent Qwen models, not a rate ruler for this lane.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact **single-card** TG/PP receipt. #28506 is two-card fit/provenance evidence only.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

Therefore **no row in `RESEARCH-TARGETS.md` moves**.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control. Revised experiment/certification order:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent rollback / growing-session correctness;
3. cache-layout/handler round-trip + model/tokenizer/runtime identity;
4. **cold-first request / request-step epoch ownership for any async or external PLE/state path**, with compiled/graph-like route off/on where applicable;
5. **QSA block/cell selected-set, tie-membership and order oracle** around the selection boundary;
6. **batch-composition invariance** at concurrency 1/2/3/4 using identical and mixed prompts, no-MTP first;
7. real-agent cache capture with canonical recurrent/attention reusable boundary;
8. immediate-follow-up async-store race + forced eviction/pause progress oracle;
9. **warm-slot PP: request 1 vs request 2+ at slot counts 1/2/3/4**;
10. realistic-depth QSA/attention vs MoE/GDN/host profiler;
11. QSA known-horizon reservation + capacity/physical-footprint accounting;
12. PLE residency/page-cache/direct-read;
13. **small-N versus wide-N kernel-route matrix** for MoE/QSA decode, verify and prefill;
14. MTP reconcile using ordinary prefill chunk geometry;
15. MTP pre-verify snapshot / commit / replay + per-slot draft context;
16. **production sampler-law certification** for temperature/top-p/top-k, RNG and rollback positions;
17. actual scheduled-sequence occupancy at parallel 1/2/3/4 plus stress;
18. concurrent pure-prefill state isolation;
19. adversarial parallel-MTP slot isolation;
20. M1/M2 activation-FP16 approximate lane after exact freeze;
21. compiled B2/B4, combine passing mechanisms, then long prefill while other sessions decode.

Safe serving policy remains: profitable singleton MTP plus plain concurrent work until multi-slot state isolation, batch-composition invariance and occupancy are certified.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement.

Keep Qwen3.8-27B as the known resident practical baseline and test Tiel at Q4/Q5-class partial expert offload using the 64 GB host RAM rather than defaulting to 3-bit.

Qualification now explicitly records:

- actual CUDA operator/backend placement;
- resident vs CPU-offloaded bytes by tensor/expert class;
- whole-round speculative economics, not acceptance alone;
- full-head MTP quantization before aggressive vocab trim;
- peak VRAM/context headroom;
- deterministic/race-clean routed-MoE path;
- real coding-agent wall time and quality;
- if multi-GPU is ever used, requested versus realized tensor split.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

Do not import oMLX #3476's concurrency behavior into P69 certification unless the same serving/batch path is intentionally under test. It is a production-runtime correctness gate, not evidence against the frozen exact verifier.

## Dual-M1 DS4-0731

No exact-rig target update. Continue using DS4 as topology/mechanism control until a sustained exact 0731 generated-token denominator exists.

---

# Standing decisions strengthened this pass

- QSA correctness means selected **set + tie membership + order**, not merely stable ordering.
- A warm repeated request can hide stale async state; **cold-first request** belongs in correctness qualification.
- External/async PLE and recurrent state require explicit request/step epoch ownership.
- Batch composition is an independent semantic axis, now supported by direct M1 Max evidence.
- Greedy equivalence does not certify production stochastic speculative decoding.
- Warm multi-slot PP can differ radically from first-request PP even without concurrent requests.
- Decode/MTP small-N and prefill wide-N need separate kernel-route qualification.
- Resource/headroom providers should be scoped to the worker/request/slot that owns them, not mutable process globals.
- Requested device/tensor split is not allocation provenance; record realized placement and bytes.
- Cross-runtime and stronger-hardware gains remain mechanism candidates until target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.