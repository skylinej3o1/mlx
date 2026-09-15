# External runtime watch — 2026-09-15 06:01 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-15 03:44:23 UTC` through the user-request cutoff `2026-09-15 10:01:18 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, comment-only activity, or a later merge of already-known measurements.

**New hard source-freshness boundary for the next complete external search: `2026-09-15 10:01:18 UTC`.**

---

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured internal GDN/projection/downstream-tail evidence.**

---

# Fresh evidence

## mlx-serve #433 — sampled MTP must stay on the exact reranked shortlist

Source PR #433 created `2026-09-15 04:15:30 UTC`, merged `2026-09-15 05:39:57 UTC` as `a758a93b9ee67b19c0f7e9f2e24cff5040697d01`.

**FRESH DIRECT APPLE / QWEN3.8-FLASH-NEXT SAMPLED-MTP MECHANISM EVIDENCE.**

The shipped sampled-proposal path requested target probabilities and therefore abandoned the cheap coarse/reranked proposal head path. Every draft step paid a full 8-bit ~675 MB lm-head readout plus full-row probability work. On the measured stack this changed approximately:

- correction path `corr`: ~0.53 -> 2.6 ms;
- predraft: ~1.75 -> 2.9 ms;
- grouped N=4 sampled chain: ~3.82 -> 9.07 ms/round;
- target trunk eval itself did not move.

The fix exposes the 32 exact reranked candidate ids/logits before argmax and samples only from that exact shortlist. The resulting q has zero mass off the shortlist, but Leviathan correction remains exact because residual `max(p-q,0)` reaches the rest of the vocabulary. Batched sampled rows keep one `[K,32]` proposal block instead of falling back to row-wise full-vocabulary work.

Per-request policy remains important: temperature <= 0.5 or `top_k == 1` stays greedy; sampled proposal is used above that measured crossover. For Flash-Next, using the target's own temperature for the draft beat a fixed 0.6 draft temperature on four of six cells, mean per-draft acceptance 53.4% vs 51.1%.

M5 Max 128 GB, Flash-Next mixed-4/8-bit, forced D3, temp=1.0 / top_p=.95, medians of three, short context:

| Cell | Greedy-proposal tok/s | Shortlist-sampled tok/s | Greedy per-draft | Sampled per-draft |
|---|---:|---:|---:|---:|
| code / xhigh | 84.4 | **104.7** | 49.8% | **68.3%** |
| code / medium | 98.3 | **103.1** | 62.2% | 65.1% |
| prose / xhigh | 70.1 | **75.4** | 34.8% | 38.6% |
| prose / medium | 71.6 | **85.8** | 37.0% | **48.7%** |

The expensive sampled arm disappeared: new `corr` ~0.47–0.49 ms and `predraft` ~1.81–1.93 ms versus old ~2.57–2.64 / ~2.84–2.92 ms.

Two concurrent creative chats under auto depth:

- MTP token share: **19% -> 98%**;
- per-draft acceptance: ~33.3–48.2% -> **66.5–68.6%**;
- group decode: 74.8 -> **82.2 tok/s**;
- greedy control ~87 tok/s;
- creative-to-greedy gap: ~14.6% -> ~5.7%.

At N=4 throughput stayed effectively flat because the planner speculated on only ~17% of tokens in both arms; that is a separate policy bottleneck.

An 8K `llmprobe` creative run reported xhigh 82.1 -> 86.6 tok/s and medium 86.9 -> 101.3 tok/s, with tokens/decode-step increasing 2.45 -> 3.08 and 2.87 -> 3.56 respectively.

Qualifications: cross-boot drift was stated as 5–12%; n=3; almost all diagnostic cells were below 2K KV and the llmprobe rung was 8K; no 128K result; sampled outputs are distribution-equivalent rather than byte-comparable. Temp-0 exact-equivalence suite remained 11/11.

**Project consequence:** for sampled Lightning MTP, proposal precision and verifier exactness do not require a full-vocabulary proposal distribution. Carry the exact reranked shortlist as the proposal support, build q there, and reserve the target full-vocabulary distribution for correction/bonus work that actually requires it. Record proposal-support width, full-head reads/round, proposal ms, acceptance-by-depth and spec-share. Keep this path separate from the canonical greedy ruler.

## mlx-serve #434 — group sampled verification should share one filter/eval graph

Source PR #434 created `2026-09-15 06:47:10 UTC`.

**FRESH DIRECT APPLE / GROUPED-MTP SCHEDULING + CORRECTNESS EVIDENCE.**

Follow-up audit to #433 found three grouped-path issues:

1. sampled rows each built/waited their own full-position probabilities even though the group target forward had already projected one joined `[rows,...,V]` verify block;
2. top-k and bounded top-p independently selected/masked the same full row;
3. greedy speculative argmax did not apply the reserved-id suppress mask used by the serial sampler.

The first fix publishes the group's joined verify logits, filters them once, and attaches all sampled-row acceptance graphs to the same async evaluation. On M5 Max, forced D2:

- N=4 creative per-row `gap` after the first row fell from roughly **2.07 / 1.39 / 0.72 ms** to **0.31 / 0.22 / 0.14 ms**, matching greedy-control gaps;
- N=2 sampled-row excess gap ~0.57 ms fell to essentially zero;
- headline N=4 round time improved only ~1.5%, so this is a confirmed scheduling-lap removal, not a large end-to-end throughput receipt.

Combining top-k + bounded top-p into one selection removed another ~0.42–0.44 ms of sampled penalty per group while greedy controls stayed flat. Greedy reserved-id masking was cost-neutral within measurement noise and restored the sampler's correctness contract.

**Project consequence:** grouped MTP execution identity includes graph/eval sharing. If multiple requests already consume slices of one joined verifier projection, filter/accept them from one joined block and one device evaluation rather than building row-wise wait staircases. Also require the speculative greedy correction path to obey the same reserved-id/suppression contract as the serial sampler.

## mlx-serve #436 — best-effort speculative sidecars must not poison global runtime state

Source PR #436 created `2026-09-15 07:33:57 UTC`.

**FRESH DIRECT MLX / PREFIX-CACHE FAILURE-CONTAINMENT EVIDENCE.**

A pooled-only speculative head snapshot could be mistaken for a restorable head even after its raw QSA-history tensor was gone. The writer then inserted an empty `mlx_array`, MLX latched a process-wide error, and the next unrelated decode tick consumed that latch and returned HTTP 500.

Pre-fix production log: **366 MLX raises and 136 failed requests out of 3,204**. The fix refuses to persist the head half unless raw history exists and explicitly clears errors produced by a best-effort sidecar write while preserving any pre-existing error.

The KV half can still round-trip; the head is correctly declined on restore. The core contract is that a failed optional speculative-state persistence operation may cost that cache entry its speculative acceleration, but may not poison later requests.

**Project consequence:** cache/spec-sidecar persistence must be transactional with respect to runtime error state. QSA/PLE/MTP snapshots need dependency-complete admission (`pooled` cannot imply restorable without raw history), and best-effort writes need scoped error ownership so a failed persistence task cannot invalidate an unrelated request.

## oMLX #3672 — SSD expert streaming makes MTP a measured loss when verify multiplies cold expert I/O

Source PR #3672 created `2026-09-15 04:10:09 UTC`.

**FRESH DIRECT APPLE / FLASH-NEXT CAPACITY-EMERGENCY + NEGATIVE-MTP EVIDENCE.**

This PR streams routed MoE experts from SSD into a dynamically sized resident arena for models larger than unified memory. Dynamic budgets respond to free-RAM watermarks plus decode stalls; expert banks use lock-free `preadv` span reads; model reload identity remains keyed to requested settings so transient pressure cannot cause reload oscillation.

MacBook Pro M4 Pro 48 GB, NVMe over USB4, 2K prompt / 128 decode, Q4 emergency-capacity lane:

| Model | Arm | TTFT | Decode | tok/s | Peak RAM |
|---|---|---:|---:|---:|---:|
| Qwen3.8-Flash-Next-oQ4e-mtp, 99 GB checkpoint | base | 26.3 s | 42.1 s | **3.04** | 26.1 GiB |
| same | MTP | 26.1 s | 46.3 s | **2.77** | 27.1 GiB |
| DeepSeek-V4.1-Flash-oQ4e-mtp, 402 GB | base | 122.6 s | 147.0 s | **0.87** | 31.5 GiB |
| same, DSpark | MTP | 125.8 s | 170.8 s | **0.75** | 39.7 GiB |

For Qwen, MTP was about **-9%**; for V4.1 about **-14%** despite 62.9% acceptance because verifier draft positions multiplied routed expert I/O per emitted token. The auto gate therefore parks MTP when bounded SSD expert streaming is live. A prior mechanism ablation on the same core found contiguous `preadv` span reads about 7–8x faster than mmap gather at expert-row sizes.

This is Q4, short-context, M4 Pro, and an emergency over-capacity path. It is not a normal resident-runtime target receipt.

**Project consequence:** speculative decoding economics must include storage bytes per emitted token, not only accepted tokens per verifier cycle. In any selective SSD-expert fallback on 64GB Macs, disable or re-evaluate MTP if verifier depth increases cold expert demand faster than acceptance repays it. The I/O unit remains routed expert demand, and span/coalesced reads remain preferred over scattered mmap gathers.

## oMLX #3676 — residency fit must run the same physical admission arithmetic as load

Source PR #3676 created `2026-09-15 06:07:58 UTC`.

**FRESH DIRECT APPLE / PHYSICAL-ADMISSION TRANSFER.**

Rather than letting users choose coarse 12.5/25/50/75% residency blindly, the runtime now enumerates whole-expert capacities and chooses the largest fraction whose *same admission estimator used by load* fits the byte ceiling. Table placement is included, so an auxiliary PLE/Engram table that no longer fits is forced to SSD exactly as real admission would do.

Header-only sizing on M5 Max 128 GB:

- Qwen3.8-Flash-Next-4bit checkpoint size **109.1 GiB**;
- 107 GiB budget: fit **1.0**, with PLE forced to SSD, resident estimate **77.8 GiB**;
- 64 GiB budget: **416/512 experts = 0.8125**, resident estimate **63.9 GiB**.

The 100% case is intentionally non-monotone versus 75% because moving PLE out of RAM can make a larger expert-residency fraction physically cheaper.

**Project consequence:** "resident fraction" is not a sufficient memory model. Capacity fitting must run actual placement/admission arithmetic across experts, PLE/Engram, speculative weights, cache state and route-specific transients. Search the discrete physical placement space; do not assume more resident experts always means monotonically more total RAM.

## vLLM #56956 — speculative drafting on a PP2 target is a proven topology

Source PR #56956 created `2026-09-15 06:07:25 UTC`.

**FRESH DISTRIBUTED-SPECULATIVE / PIPELINE-PARALLEL TOPOLOGY TRANSFER.**

DeepSeek-V4-Flash (0731) DSpark now runs against an IFB **PP2 x TP2** target. The drafter lives wholly on the last PP stage.

The required topology/correctness details are directly relevant to our dual-M1 Lightning design:

- last stage broadcasts fresh draft tokens to earlier PP stages before the next verifier step;
- the no-op second call site must not double-post that broadcast, or PP receive FIFOs become misaligned and hang;
- deferred PP post-update kernels must be compiled during warmup, because a first-use compile during serving can deadlock against an in-flight collective;
- the drafter needs its own embedding copy when target embeddings exist only on PP stage 0;
- CUDA-graph padding rows must have ids/positions/state explicitly cleared rather than being allowed to carry uninitialized speculative state.

Validation: **1,744 tests passed**. DeepSeek-V4-Flash (0731), DSpark K=5, IFB PP2xTP2, GSM8K strict match **0.9545**, stated to match target-only within noise.

No dual-M1, TB4, Lightning or throughput receipt is provided.

**Project consequence:** distributed speculative PP is now stronger than a conceptual feasibility argument. The concrete control topology matches our working design: stage-local model state, drafter/control authority on one end of the pipeline, verifier traversal, tiny authoritative draft/commit broadcasts, synchronized state updates, warmup before collective-bearing paths, and explicit padding-row hygiene. This increases confidence that our blocker is implementation/certification rather than PP architecture itself.

## vLLM #56971 — hybrid prefix cache must save decode-phase recurrent boundary states

Source PR #56971 created `2026-09-15 07:56:53 UTC`.

**FRESH HYBRID GDN/MAMBA PREFIX-CACHE TRANSFER.**

Hybrid Mamba/GDN external prefix caching previously saved recurrent boundary states only through prompt end. Attention cache groups kept decode blocks, but recurrent groups did not; lookup intersects all groups, so cache hits stopped exactly at the original prompt boundary.

The fix saves every retained decode boundary and finish-time partial tails when decode-cache saving is enabled. It also fingerprints the cache key with the physical settings that define block bytes: KV dtype, model dtype, quantization, recurrent-cache dtypes, block sizes, cache-group specs and parallel layout.

8x H20 over TCP, Qwen3.5 GDN hybrids:

- Qwen3.5-2B: external hit **1,088 -> 2,176 tokens**, TTFT **0.202 -> 0.186 s**, cold ~0.236 s;
- Qwen3.5-4B: hit **2,112**, TTFT **0.316 s** vs cold **0.411 s**;
- TP2, CUDA graph and ngram speculative modes all retained the extended hit;
- eight concurrent requests each hit 2,176 tokens;
- 32-token greedy continuations were token-for-token identical to cold recompute;
- consumers with mismatched recurrent cache dtype/model dtype received a different key digest and loaded nothing.

**Project consequence:** our Flash prefix-cache contract must extend recurrent/QSA state through decode, not merely snapshot prompt-end state. Cache identity must fingerprint physical block representation and distributed layout; model path + token prefix is insufficient. Retention interval must guarantee a recurrent boundary exists at every advertised reusable block.

## vLLM #56974 — recurrent kernel launch geometry is device admission state

Source PR #56974 created `2026-09-15 08:06:32 UTC`.

**FRESH RECURRENT-KERNEL ADMISSION TRANSFER.**

A GLM-5.3-Flash fused recurrent KDA/GDN kernel used `(batch * value_heads)` in CUDA `gridDim.z`. At batch 1024 x 64 heads this became 65,536 programs, one beyond CUDA's 65,535 z-grid limit, so DP4 could not start. Moving that dimension to grid x restored launch validity while preserving bitwise outputs where the old route ran.

Patched DP4+EP starts, captures graphs and serves an 8K-in/1K-out concurrency sweep. TP4 throughput stayed effectively identical: 169.6 vs 169.1 tok/s at c=1 and 1898.6 vs 1897.4 at c=32.

**Project consequence:** reinforces the fresh oMLX Metal finding: launch-grid/threadgroup/residency constraints are part of physical route admission. M1-specific QSA/GDN kernels must certify device-generation limits at maximum *physical padded* batch/head geometry, not merely compile successfully or pass small-shape tests.

## vLLM #56982 — padding can rescue a catastrophic backend-routing cliff

Source PR #56982 created `2026-09-15 09:08:57 UTC`.

**FRESH QWEN3.8-27B / PHYSICAL-DISPATCH TRANSFER FOR THE RTX LANE.**

While comparing Qwen3.8-27B and Qwen3.8-27B-FP8 on B300, block-FP8 was about 3x slower because unaligned M failed the desired FlashInfer/DeepGEMM route and fell to a CUTLASS small-M swapAB kernel. Padding large M to the backend's alignment before quantization changes physical route selection.

B300 synthetic kernel results:

- M=129–131: ~2.27–2.29x;
- M=257: ~2.35x;
- M=8193–8195: **~7.88–8.08x**.

This is SM100 block FP8 on B300, not our 5070 Ti Q6/Q8 lane, and there is no target-model E2E throughput receipt.

**Project consequence:** extend execution provenance with shape-alignment -> backend-selection mapping. A logically equivalent padded dimension can be a large win if it changes kernel admission. On 5070 Ti, explicitly census verifier/projection/pre-fill M/N/K alignments and record whether each shape lands on the intended SM120 kernel or a fallback before blaming the arithmetic itself.

## vLLM #56983 — DFlash2 can beat MTP materially, but draft KV region costs context capacity

Source PR #56983 created `2026-09-15 09:11:35 UTC`.

**FRESH STRONG DFLASH2 ECONOMICS / LONG-CONTEXT-CAPACITY TRANSFER; NOT QWEN/APPLE EVIDENCE.**

GLM-5.3-Flash + a five-layer DFlash2 draft model was made runnable on 8x H100, TP8+EP, max-model-len 131,072. The draft uses separate sliding-window KV geometry rather than aliasing target MLA slots.

Throughput sweep, 16 fixed code/prose prompts, greedy, 512 output:

| Config | Single stream | C8 | C32 | C64 |
|---|---:|---:|---:|---:|
| DFlash2 k=6, FA, maxseq96 | **223–225.5** | **1074** | **2851–2924** | **4269** |
| MTP k=5, maxseq96 | 160.7 | 853.7 | 2377.0 | 3721.3 |

DFlash2 k=6 therefore beat MTP by roughly **+40% single stream, +26% C8, +23% C32, +15% C64** on this stack.

Acceptance economics:

- k=4: mean accept length 3.00, draft acceptance 49.9%;
- k=6: 3.31, 38.5%;
- k=8: 3.33, 29.1%;
- k=16: 3.63, 16.5%.

Acceptance decays near zero beyond the drafter's block size; k=16 pays a 17-token verifier step for essentially the same accepted length, so k≈4–6 is the measured sweet spot.

Critical capacity cost at 131,072 target context:

- MTP k=5: 23.61 GiB KV memory, **1,802,673-token** capacity;
- DFlash2 k=6: 23.49 GiB KV memory, **1,358,649-token** capacity;
- separate draft KV region therefore costs about **24.6% capacity**.

GSM8K target-only accuracy 0.931 vs DFlash2 0.939; output speed 101.6 vs 203.8 tok/s under the evaluation harness, with differences described as within the nondeterministic FP8-MoE run spread.

Known limitation: mixed long prefill + speculative verify still hits a pre-existing FlashInfer sparse-MLA crash on this stack, reproduced with both DFlash2 and MTP.

**Project consequence:** DFlash2 remains interesting, but this is exactly why it does not displace Lightning MTP in our current dual-M1 plan. Measure speculative speedup and context-capacity tax together. On 64GB unified memory a separate draft-KV region can erase the headroom required for 128K even when decode is faster. Any DFlash experiment must report accepted length, verifier width, draft-state residency and remaining max-context capacity as one receipt.

## llama.cpp #28931 — Qwen3.8-27B decode still pays materially for dispatch count

Source PR #28931 created `2026-09-15 06:23:51 UTC`.

**FRESH QWEN3.8-27B DECODE-MECHANISM TRANSFER.**

Arc Pro B70 SYCL profiling of Qwen3.8-27B UD-Q4_K_XL found roughly **1,860 kernel launches/token** at ~5 us fixed Level-Zero dispatch, estimated ~25% of the ~41 ms token time. Mixed-quant GLU, rms_norm+scale and ssm_conv+silu fusions remove ~330 launches/token (~18% of the launch pool).

Measured A/B:

- tg256 p512: **23.90 -> 24.25 tok/s (+1.47%)**;
- tg128 p8192: **23.80 -> 24.22 (+1.76%)**;
- pp512/pp8192: within noise.

**Project consequence:** dispatch reduction is real but modest after larger bottlenecks are fixed. For our M1 27B/P69 path, keep command-buffer/kernel-count census and fuse cheap adjacent elementwise/recurrent glue only after preserving quant/reduction semantics. Do not infer a large target movement from launch count alone.

## llama.cpp #28923 — exact RTX5070Ti hardware shows a partial-tile PP lever

Source PR #28923 created `2026-09-15 04:45:55 UTC`.

**FRESH EXACT-HARDWARE / DIFFERENT-MODEL VULKAN TRANSFER FOR RTX5070TI16.**

On an RTX 5070 Ti 16 GB with locked clocks and fully resident MoE models, Vulkan `MUL_MAT_ID` always used a full BN=64 final N tile even when the tail fit in 32. Enabling BN/2 specifically for the tail preserved 921/921 backend-op tests.

PP512 average gains:

- DeepSeek-V2-Lite Q5_K_M: +4.30%;
- Qwen3-16B-A3B Q6_K: **+3.89%**;
- Moonlight-16B-A3B Q6_K: +4.79%.

B=1..8 uses a vector path and is unaffected.

This is exact 5070Ti16 hardware but different models/runtime and not Qwen3.8-27B, so it is transfer evidence only.

**Project consequence:** the RTX lane should include tail-tile occupancy in PP shape census. For Q6/Q8 MoE/projection kernels, a half-width final tile can matter even when dispatch count is unchanged. Check SM120-native equivalents before accepting full-width padded-tail cost.

---

# Screened but not target-promoted

## External M1 / community benchmark screen

A newly crawled M1 Max 64 GB Qwen3.8-27B article reports Ollama/Q4_K_M around 10–12.2 tok/s with a 65,536 configured context and very large prompt TTFT at ~6.9K tokens. It explicitly does **not** test MLX, and the retrieved source does not provide a trustworthy substantive publication timestamp inside this search window. It therefore does not advance the hard freshness boundary and is not used to recalibrate our 25 tok/s MLX target.

A current aggregate benchmark index also exposes RTX5070Ti and Apple Qwen3.8 rows, but the aggregator does not give enough source-level timing/provenance for the individual cells to qualify under the hard source-time rule. Retain only as discovery leads.

## vLLM #56969

Created `2026-09-15 07:39:15 UTC`; targets out-of-bounds access in FlashInfer SM90 sparse-MLA mixed batches. It is relevant to the speculative mixed-prefill crash family, but the PR description available in this pass does not provide a sufficiently controlled before/after performance/correctness receipt to supersede the stronger explicit crash evidence in #56983. Track as an implementation fix, not a target mechanism gain.

## Other fresh conceptual/runtime PRs

Fresh work also appeared around sparse top-k reuse, reused prefill KV gathers, packed FP8 Engram exchange and additional distributed/configuration cleanup. Several are still TODO/test-light or do not contain a measured A/B. They are not promoted ahead of the measured items above.

---

# Fresh-screen negatives

- No exact fresh **dual-M1 Flash-Next** TG/PP receipt.
- No exact fresh **M1 Max64 Qwen3.8-27B MLX** receipt with controlled native runtime.
- No controlled exact fresh **RTX5070Ti16 Qwen3.8-27B** receipt strong enough to move 120/250.
- No exact fresh **dual-M1 DS4-0731** receipt.
- No evidence justifies moving any canonical target.
- No evidence justifies reopening/reordering P69.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 control.

New/reinforced work items:

1. **Distributed Lightning topology:** prototype last/control-stage authority + one verifier PP traversal + tiny authoritative draft/commit broadcasts. Warm every collective-bearing/state-update path before serving. Guard against duplicate PP posts and clear padded speculative rows.
2. **Sampled MTP:** carry an exact reranked shortlist as q support; do not force proposal drafting through a full target lm-head distribution. Group rows onto one verifier projection/filter/eval graph where homogeneous.
3. **Cache through decode:** save recurrent/QSA boundary state beyond prompt end. Cache key fingerprints physical dtype/quant/block/distributed layout. Advertised hits require all state groups to be reusable at the same committed boundary.
4. **Optional-state persistence:** sidecar/snapshot writes are transactional with respect to global MLX error state. Dependency-incomplete speculative snapshots are declined rather than half-restored.
5. **Physical admission:** enumerate actual expert/table/state placements. A larger expert fraction can be cheaper if it forces a large PLE table out of RAM; do not fit memory with a monotone fraction heuristic.
6. **Launch validity:** qualify QSA/GDN/SDPA kernels against M1 threadgroup/grid/residency limits at maximum physical padded shapes.
7. **Speculation under I/O fallback:** if experts spill to SSD, price expert bytes/emitted token. MTP can become negative when verifier depth multiplies cold routed reads.
8. **DFlash control only after memory receipt:** any DFlash2 arm reports throughput and context-capacity tax together. A ~25% draft-KV capacity penalty would be unacceptable if it pushes 128K outside the 64GB envelope.

The new PP2 DSpark evidence increases confidence in distributed speculative feasibility; #433 strengthens the Apple-side MTP economics. Neither is an exact dual-M1/128K receipt.

## Qwen3.8-27B M1 / P69

No target movement and no P69 sequence change. **P69B12 remains frozen/promoted; P69B13 remains next.**

#28931 reinforces that launch/dispatch cleanup is a legitimate final-stage gain but only ~1.5–1.8% on its SYCL receipt. Keep fusion exactness and reduction-order gates; do not reopen frozen stages from external evidence.

## RTX5070Ti16

No target movement.

Fresh useful transfer:

- exact 5070Ti Vulkan PP shows ~3.9% Q6 MoE gain from narrower final N tiles;
- B300 Qwen3.8-27B shows shape alignment can alter backend selection catastrophically.

Add explicit SM120 route census for M/N/K alignment, tail tile, kernel-image selection, quant layout and fallback. Still require an exact Qwen3.8-27B controlled 5070Ti receipt before moving **120/250**.

## DS4-0731 dual M1

No target movement. #56956 is same-family DeepSeek-V4-Flash PP speculative-topology transfer; oMLX SSD streaming is an emergency-capacity negative MTP result. Neither is dual-M1 DS4-0731 throughput evidence.

---

# Standing rules added / reinforced

- **Proposal support can be sparse while verification remains exact:** for stochastic MTP, an exact reranked shortlist can define q; full-vocab proposal logits are not automatically required.
- **Group graph sharing is execution identity:** joined verifier logits should normally lead to one filter/eval graph, not row-wise build/wait staircases.
- **Speculative and serial sampler masks must agree:** reserved/suppressed ids cannot re-enter through greedy correction/argmax paths.
- **Optional persistence errors are scoped:** best-effort cache/spec writes may drop acceleration state, never poison process-global runtime error state.
- **Restorable state is dependency-complete:** pooled/indexed summaries do not imply a usable checkpoint if required raw history is absent.
- **Speculative economics include I/O bytes per emitted token:** acceptance alone can mislead under SSD expert streaming.
- **Residency fitting uses physical placement arithmetic:** expert fraction is not monotonically equivalent to total resident bytes when auxiliary tables can change tiers.
- **PP speculative control is a distributed protocol:** authoritative draft broadcast, exactly-once collective ordering, warmup, padding hygiene and stage-local ownership are correctness state.
- **Decode-phase recurrent states belong in prefix cache:** prompt-end-only snapshots are incomplete for hybrid models.
- **Cache keys fingerprint physical representation and parallel layout, not just model path/token prefix.**
- **Launch-grid/threadgroup limits are route admission state:** compile success is not execution validity.
- **Alignment can select the backend:** padding may improve performance by changing physical kernel admission, not arithmetic count.
- **Draft speedup and draft-KV capacity tax are one receipt:** speculative methods cannot be ranked on tok/s alone at long context.
- **Dispatch-count cleanup is usually a late-stack gain:** record launch count and fixed per-launch cost, but validate E2E contribution rather than extrapolating from removed calls.
- **Tail-tile geometry matters separately from dispatch count:** a narrower last tile can improve PP without changing the number of launches.
- Exact target receipts remain distinct from mechanism transfer, experimental A/Bs and planning targets.
