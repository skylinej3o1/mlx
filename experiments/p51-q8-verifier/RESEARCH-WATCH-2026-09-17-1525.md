# External runtime watch — 2026-09-17 15:25 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-17 13:43:30 UTC` through the user-requested cutoff `2026-09-17 19:25:05 UTC`.

Evidence time means the substantive source / measurement timestamp. Merge, rebase, crawler, label, comment, and later-edit times do not make older evidence new. PR summaries, issues, and default-branch commits were all scanned; this is important because several of the strongest receipts in this window live only in PR or issue bodies.

One boundary-edge item is intentionally quarantined: vLLM #57431 was created at `19:03:30 UTC`, but its current PR metadata shows `updated_at=19:25:50 UTC`, 45 seconds after this cutoff. The PR's existence/topic is recorded here, but its quantitative body is not promoted in this watch because the current snapshot cannot prove which description fields existed by the cutoff. Re-evaluate it in the next window. Conversely, vLLM commit `67e5b0acc9988afc50d019db64ad9da0dadaa15e` landed at `19:26:10 UTC`, 65 seconds after cutoff, and is excluded entirely.

## Executive result

**No exact active-topology receipt appeared for any canonical target. No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max 64GB: **25 tok/s TG / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s TG / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max 64GB/TB4: **15 tok/s TG / 180 tok/s cold PP**.

Flash interpretation is unchanged: sustained **40 TG at ~128K active context** is the core success floor; 45–50 is stretch; 50–60 is upside only. Short-context 40 does not satisfy the target. PP means cold prefill.

This window is nevertheless high value. The strongest promoted lessons are:

1. **Long-context speculative attention routing can become the bottleneck by orders of magnitude.** vLLM #57409 moves non-causal multi-row DFlash/DSpark draft attention onto an eligible 3D Triton route. At batch 8 / 131K, one draft attention call fell from 6.07 ms to 0.272 ms in the best measured configuration; Kimi-K3 end-to-end at 150K improved from roughly 430–456 tok/s to 500–508 tok/s at essentially unchanged acceptance. This is non-target AMD transfer evidence, but directly relevant to our 128K speculation ruler.
2. **Asynchronous PP needs decode-cohort balancing, not a blunt global request cap.** vLLM #57433 reports +4.74% at PP2, +12.62% at PP4, and +22.95% on a PP4 trace when established decode cohorts are balanced while prompt-completing work remains uncapped. This is unusually direct transfer evidence for our future dual-M1 PP scheduler.
3. **Physical padded sparse width is not semantic active width.** vLLM #57432 found DSpark non-causal sparse attention normalizing over 256 padded entries when only 133 were valid; fixing active length recovered mean acceptance by ~20–21% without claiming an accuracy gain. Treat sparse valid-count/visibility metadata as correctness identity.
4. **Real long-prompt production traffic can be scheduler-bound while memory is healthy.** vLLM issue #57413 reports 100K–180K prompts on 4x B200 where TTFT p95 rose to 76 s despite KV usage below 40%, zero preemptions, and high GPU utilization. Long-context qualification needs admission/fairness metrics, not just aggregate PP throughput.
5. **Distributed warmup state is consensus state.** vLLM issue #57423 shows a rank-0-only FlashInfer autotune cache hit while other ranks enter synchronized autotuning can deadlock the entire 8-rank launch. A cache hit/miss decision that changes collective participation must be rank-consistent.
6. **Apple expert offload is now backed by a full residency/speed/memory matrix.** oMLX #3720 on M5 Max 128GB shows predictable memory scaling and monotonic decode gains as resident expert fraction rises for DeepSeek-V4-Flash-0731 and GLM-5.3-Flash. This does not transfer as an M1 rate, but it materially strengthens the implementation case for explicit expert-residency controls and exposes a compile-vs-host-managed-state incompatibility.
7. **DS4 now has a fresh Qwen3.8-Flash-Next Strix Halo receipt.** DS4 #1070 reports Q2/Q4 resident decode around 20–22 tok/s at 8K, Q2/Q4 MTP around 22–25 tok/s on coding prompts, 277–297 tok/s fresh 1K PP, and successful 64K prefill + 2K continuation. It is AMD APU / ROCm evidence, not Apple target evidence.
8. **Persistent scratch ownership can dominate admission memory.** vLLM #57421 reduced Humming MoE scratch storage from ~10.1 GiB to ~258 MiB at one 8192-token configuration by sharing compatible sequential scratch across 40 layers. Our allocator ruler must distinguish logically per-layer use from physically concurrent lifetime.
9. **MTP placement/admission can fail before a single draft tensor is created.** llama.cpp issue #29044 reports a Qwen3.8-27B MTP draft failing under automatic device split when reported free memory reaches zero; explicit `-ts 1` loads and then delivers a reported 1.9x decode speedup with 71–82% acceptance. Admission arithmetic must fail closed on zero/NaN geometry.
10. **Long-soak stability remains a separate qualification axis.** vLLM issue #57429 reports repeated GLM-5.3 TP8/MTP5 stalls on MI325X despite low KV usage and no preemption, while a matched MI355X campaign ran 16,026 requests with zero pauses/errors. A fast short benchmark cannot certify a long-running distributed route.

---

## Promoted long-context speculative evidence — vLLM #57409

Source PR created: `2026-09-17 16:23:55 UTC`.

DFlash/DSpark sends `1+k` **non-causal query rows** per request. The Triton unified-attention router previously admitted only single-token rows to its segmented 3D launch, so draft rows always used the 2D path even when their geometry was ideal for 3D. Cost grows badly with context: the PR measured one B8 / q_len=4 / 131K draft attention call at **6069.7 µs** on the old path.

The proposed route allows non-causal multi-token rows onto 3D only when the scratch can hold every query token. Sliding windows, sinks, image-prefix masks, quantized KV, or insufficient scratch retain the 2D path. Scratch is sized from the **drafter KV spec**, not the target model's head geometry.

Measured on 8x MI325X:
- draft q_len4, B8, 8K: **317.4 µs -> 36.0 / 30.9 µs** (16 / 128 segments);
- draft q_len4, B8, 131K: **6069.7 -> 509.0 / 272.4 µs**;
- B1, 8K: **244.2 -> 14.7 µs**;
- B16, 8K: **316.6 -> 47.8 µs**.

Kimi-K3 TP8 + DSpark at ~150K:
- AITER drafter attention: 429.9 / 456.1 / 433.2 tok/s, acceptance 2.99 / 2.99 / 3.04, ~54.7 ms/step;
- new Triton route: 499.8 / 508.0 / 501.4 tok/s, acceptance 3.03 / 3.01 / 3.04, ~48.1 ms/step.

With DCP the PR reports 8K ~45.7 ms/step versus 50.8, and 131K **51.1 versus 71.2 ms/step** against the AITER drafter path.

### Promoted rules

- Speculative drafter attention gets its own route crossover; do not inherit target-attention routing merely because both use attention.
- Route identity includes `causal/non-causal`, q_len, B, context, scratch rows, drafter head geometry, KV dtype, masks/windows/sinks, and segment count.
- At ~128K, certify **per-draft attention cost** explicitly. Good acceptance can coexist with a terrible speculative cycle if the drafter attention route scales with context.
- Scratch should be sized from the actual module consuming it. Target model geometry is not a safe proxy for drafter geometry.

These numbers are ROCm/Kimi-K3 transfer evidence, not Apple rates and not a direct Qwen3.8-Flash-Next receipt.

---

## Promoted PP scheduling evidence — vLLM #57433

Source PR created: `2026-09-17 19:08:09 UTC`.

Model Runner V2 asynchronous PP makes a request eligible again only after `pipeline_parallel_size` scheduler steps. Prompt-completion timing can therefore create persistent uneven cadence cohorts such as Q7/Q13/Q2/Q10.

The proposal caps **established decode** selected per step at:

`ceil(max_num_seqs / pipeline_parallel_size)`

while leaving prefill, chunked prefill, and prompt-completing mixed work uncapped. This is important: an earlier global cap (#50410) reportedly reduced throughput because it constrained prompt work that requires token-aware scheduling rather than sequence-count balancing.

Matched Kimi-K3 + DSpark on B200:
- TP8/PP2, C64 fixed 64K/400: Q19/Q13 -> Q16/Q16, **+4.74% output tok/s**;
- TP8/PP4: Q7/Q13/Q2/Q10 -> Q8/Q8/Q8/Q8, **+12.62%**;
- Mooncake trace C64 TP8/PP4: decode cap 8, **+22.95% versus natural scheduling**;
- the PR states the global-cap approach was -8.21% versus natural on the matched trace, making the decode-only policy +33.95% versus that approach.

### Transfer to dual M1 PP2

- Measure stage cadence/cohort balance, not only mean stage utilization.
- Decode balancing and prefill admission are distinct policy problems. Do not use one global sequence cap as a substitute for both.
- Our PP2 ruler should record per-step cohort width, stage idle gaps, prompt-completion transitions, and output tok/s before/after a decode-only balancing policy.
- If our one-user B1 path is the main target, this mechanism may not move B1 directly; it becomes more important for dynamic joins, concurrent local agent traffic, or batched MTP verification.

This is strong scheduler transfer evidence, not an M1 performance receipt.

---

## Promoted speculative-correctness evidence — vLLM #57432

Source PR created: `2026-09-17 19:04:40 UTC`; last update before cutoff at `19:14:10 UTC`.

DSpark draft length 5 had **133 valid sparse keys** but the FlashInfer integration padded the index list to 256 and passed 256 as the active sparse length. Padding therefore participated in softmax normalization. A constant-value reference that should return 1 returned **0.51953125 = 133/256**. Short contexts also inherited causal visibility from per-request query positions despite the draft window being non-causal.

The fix separates valid SWA length from the minimum physical width FlashInfer requires and presents every draft query with the full non-causal sequence length.

4x GB200, DeepSeek-V4.1-Flash + DSpark5:
- DEP4 mean acceptance including bonus: **3.1823 -> 3.8248 (+20.2%)**;
- TP4: **3.2075 -> 3.8879 (+21.2%)**;
- GSM8K remained near the prior level; the PR explicitly says the runs establish acceptance recovery, **not an accuracy improvement or bit-exact greedy equivalence**.

### Promoted rules

- Physical padded sparse width, active valid count, and semantic visibility are three separate quantities.
- Padding rows/indices must be numerically inert, including in normalization denominators and position/visibility logic.
- Acceptance collapse can be a metadata/geometry bug even when target quality looks healthy.
- Add valid-count and visibility sentinels to our speculative correctness receipts, not only accepted-token totals.

---

## Promoted Apple expert-offload evidence — oMLX #3720

Source PR created: `2026-09-17 16:38:29 UTC`.

The PR extends expert offload to `deepseek_v4` and `glm5_next`, whose routed experts use the same custom `SwitchGLU` module. Parameters are swapped into resident slot tensors while keeping the module/kernels, with host LRU + positional `pread` for misses.

Live testing found a critical execution-mode incompatibility: the vendored GLM5 decoder compiled its FFN decode block, but an offloaded block performs host-managed LRU lookup and disk reads. The first real request failed because those host actions cannot be traced/evaluated inside the compiled transformation. The fix disables FFN compilation for offloaded layers while retaining native gather kernels.

M5 Max 128GB, DeepSeek-V4-Flash-0731-2.4bit-mixed (~86GB):
- 25% residency: peak ~25.6–27.7GB; TG ~12.7–16.1 across 1K–16K prefill cells;
- 50%: peak ~43.8–46.1GB; TG ~15.1–18.5;
- 75%: peak ~62.0–64.0GB; TG ~18.2–20.9.

GLM-5.3-Flash-oQ2e-mtp (~99GB):
- 25% residency: peak ~38.9–42.4GB; TG ~6.8–9.2;
- 50%: peak ~61.0–64.6GB; TG ~8.2–11.6;
- 75% measured at pp1024: peak 83.12GB, TG 14.4; longer cells were refused by the existing predicted-peak safety guard.

The PR reports resident-model greedy outputs matching at full residency and coherent generation across the matrix, but MTP remains mutually exclusive with offload.

### Promoted rules

- Expert offload needs an explicit `resident_fraction -> physical memory -> miss rate -> TG/PP` ruler. Treat residency as a tunable capacity variable, not a Boolean.
- Host-managed state transitions (LRU, pread, slot replacement) must not be hidden inside a compiled device graph unless explicitly supported.
- Admission should reject predicted unsafe cells before running; refusal is not evidence that the model fundamentally cannot fit.
- Separate memory savings from throughput gain and from quality/correctness. Offload is a capacity route first.

M5 Max != M1 Max, and neither model/quant/topology is the dual-M1 Flash target. No target movement.

---

## Promoted DS4 cross-platform Flash receipt — #1070

Source PR created: `2026-09-17 16:56:09 UTC`.

Strix Halo 128GB, ROCm 10, Qwen3.8-Flash-Next, resident weights + disk-backed n-grams. Native `ds4-bench`, 8192-token prefill chunks, 128 generated tokens:

- Q2: fresh 1K PP **277 tok/s**; append 7K to 8K **462 tok/s**; decode at 8K **21.4 tok/s**.
- Q4: fresh 1K PP **297 tok/s**; append 7K **364 tok/s**; decode **20.0 tok/s**.
- coding prompts: Q2 ordinary 21.5–21.8, MTP 23.9–24.9; Q4 ordinary 20.2–20.4, MTP 22.4–23.1.
- all eight ordinary/MTP coding pairs reportedly produced identical answers and passed executable-code checks.
- both quants completed **64K prefill + 2K continuation + subsequent decode** in the validation panel.

Quality fixtures show Q4 consistently higher API top-1 than Q2; the PR also reports 72 coding/tool task runs passing 376 checks, checkpoint/rewind/failure recovery, vision, cancellation, session reuse and disk restore.

Limitations matter: no Qwen TP/PP, no SSD expert streaming, no native multi-session ROCm decode batching, and server MTP is disabled by `--batched-session` even when set to 1.

### Classification

Exact AMD-APU/ROCm Flash receipt + quality evidence. It helps bound what this model architecture can do on a 128GB unified-memory consumer-class system, but it is **not** an M1 transfer factor and does not satisfy the ~128K active-context target.

---

## Promoted Apple runtime-integration evidence — oMLX #3719

Source PR created: `2026-09-17 15:54:25 UTC`; merged `16:06:32 UTC`.

oMLX upgraded mlx-vlm and adapted nested cache classes, batching/restoration, Lightning MTP, VLM assistant MTP, image-prefix boundary caching, and DFlash completion snapshots. Two execution-thread rules are especially relevant:

- Qwen MoE projections are materialized on the **loading thread** to avoid cross-thread MLX stream errors.
- DFlash completion snapshots are saved on the **MLX execution thread**.

Validation included singleton/B2 cold prefill, partial/full hits, memory reuse, SSD restoration, cancellation/retry, and additional 12K checks on Qwen3.8-27B, Qwen3.8-Flash-Next and DeepSeek V4.

### Promoted rule

Thread/stream ownership is state identity. A numerically valid operation performed on the wrong MLX execution stream/thread can still be an invalid lifecycle transition. Include execution-thread provenance in cache/snapshot/materialization qualification.

---

## Promoted sparse-prefill component evidence — vLLM #57420

Source PR created: `2026-09-17 17:40:37 UTC`.

MiniMax-M3 query-tiled sparse prefill groups adjacent queries, unions selected KV blocks, loads each union block once, and gates membership/causality per query.

H200 component measurements with high overlap:
- BF16 median best representative speedup **4.49x**;
- FP8 **5.37x**;
- representative B32/q256 BF16: **1.0259 ms -> 0.2252 ms (4.56x)**.

End-to-end, MiniMax-M3 MXFP8 TP8, C32, 64K input with 57.6K shared prefix:
- output tok/s/GPU 105.8 -> 109.6 (**+3.7%**);
- p50 TTFT 3.51 -> 2.84 s;
- p50 user tok/s slightly decreased 38.5 -> 37.6.

### Promoted rule

Sparse block reuse across adjacent queries can produce large kernel gains while only modestly moving end-to-end throughput. Preserve the standing component-vs-E2E distinction and instrument selected-block overlap before deciding whether a tiled union route is worthwhile for QSA prefill.

---

## Promoted persistent-workspace evidence — vLLM #57421

Source PR created: `2026-09-17 17:40:55 UTC`.

Humming grouped MoE retained permutation scratch in every layer even though sequential layers do not need all those buffers concurrently. A shared `WorkspaceManager` owner reuses compatible persistent scratch while isolating ubatches, lanes and concurrent streams.

B300, Qwen3.6-35B-A3B-NVFP4, 40 MoE layers:
- max batched tokens 2048: live GPU allocation **33.412 -> 30.953 GiB**, saving 2.459 GiB;
- 8192: **41.352 -> 31.516 GiB**, saving **9.836 GiB**;
- scratch objects: 40 -> 1;
- scratch storage at 8192: **10330.684 MiB -> 258.267 MiB (97.5% less)**.

No latency improvement is claimed.

### Promoted rule

Physical memory billing follows **simultaneous lifetime**, not module count. When sequential layers share a compatible scratch contract, per-layer persistent allocation can be a pure admission tax. For our Flash memory accounting, explicitly classify scratch as per-layer logical ownership versus concurrently required physical instances.

---

## Promoted production long-context scheduling receipt — vLLM #57413

Issue created: `2026-09-17 16:42:16 UTC`.

A production GLM-5.3-Flash deployment on 4x B200, TP4, MTP5, chunked prefill, FP8 KV reports median prompts around **100K–180K tokens** and generation generally <1K.

During saturation:
- TTFT p50: ~0.5–0.9 s healthy -> up to **18 s**;
- TTFT p95: ~2–4 s -> **76 s**;
- queue-time p50: ~0.2 s -> **12 s**;
- ITL p50: ~20–40 ms -> **247 ms**;
- KV cache remained <40%; preemptions stayed zero;
- GPU util remained 96–99%, but reported tensor-pipe active only 10–20%; waiting reason was capacity.

Doubling max batched tokens from 8192 to 16384 did not eliminate the high tail. The reporter attributes the behavior to lack of a concurrent-partial-prefill admission control; that causal interpretation is user-supplied evidence, not independently proven by the issue.

### Transfer

Our cold-PP target is necessary but not sufficient for useful long-context serving. Record TTFT distribution, prompt scheduling fairness, queue time, active partial-prefill count, and decode interference under at least one multi-request long-prompt stress cell.

---

## Promoted distributed warmup-consensus failure — vLLM #57423

Issue created: `2026-09-17 17:57:55 UTC`.

On 8x H100, a FlashInfer autotune config cache was reportedly loaded only on rank 0. Rank 0 took a cache-hit route while the other ranks entered autotuning that performs synchronized collectives. The engine then hung indefinitely.

### Promoted rule

Any warmup/autotune/compile cache decision that changes collective participation is **distributed consensus state**. Cache keys, hits, fallbacks and invalidation must be rank-consistent, or all ranks must enter an explicit consensus handshake before choosing the route.

For our dual-M1 runner, persist and compare warmup/JIT route identity on both machines before a distributed benchmark is considered valid.

---

## Promoted long-soak stability receipt — vLLM #57429

Issue created: `2026-09-17 18:46:29 UTC`.

8x MI325X, GLM-5.3 FP8, TP8, MTP5. Under 50–60 concurrent long-prompt requests, the reporter observed:
- 4 fatal engine deaths in 6 days;
- at least 6 recoverable freezes lasting 75 s to 12.8 min;
- 29 ~10-second pauses during one 5.4-hour soak;
- KV cache ~21–27%, no preemptions;
- during a freeze some ranks show 100% GPU use while others show 0%;
- matched gfx950 / MI355X run: **16,026 requests, zero errors, zero pauses**.

The last logged AITER fused-MoE width is correlated with some stalls, but the issue explicitly says causality is unproven and AITER-off has not yet been tested.

### Promoted rule

Long-run liveness is independent of short-run correctness and throughput. A production qualification campaign should include time-to-stall/forward-progress telemetry, per-rank activity divergence, and a fail-fast watchdog that distinguishes a dead distributed step from a slow one.

---

## Promoted Qwen3.8-27B speculative admission receipt — llama.cpp #29044

Issue created: `2026-09-17 19:23:42 UTC`, inside the cutoff by 83 seconds.

RTX 3080 Laptop 16GB / WSL2, Qwen3.8-27B main + MTP Q4_0 draft. With the main already filling the GPU, automatic tensor split fails during draft-model device/layer assignment with an out-of-range vector access. Explicit `-ts 1` loads successfully and the reporter then sees **1.9x decode with 71–82% acceptance**.

The proposed root cause is plausible but not debugger-confirmed: free-memory reporting can return `free=0,total>0`, making normalized automatic split geometry divide by zero and become NaN; `upper_bound` then returns an out-of-range device index.

### Promoted rule

Admission/placement arithmetic must validate finite/nonzero denominators and resulting device indices before tensor creation. A runtime can have enough physical capacity for a working explicit placement while its auto-placement heuristic fails because measurement geometry is invalid.

This is exact non-target RTX3080/WSL evidence, not evidence for the RTX5070Ti 120 tok/s target.

---

## Fresh benchmark-provenance fix — mlx-serve `ef5e667d`

Source commit timestamp: `2026-09-17 15:48:11 UTC`.

The benchmark path was changed so it explicitly loads the selected model and reports only settings that the executed engine actually supports. Notably, ds4/llama.cpp runs no longer inherit MLX-only KV/attention/drafter flags, and quantized packs are no longer mislabeled as lossy merely from high-level metadata.

### Promoted rule

A benchmark receipt must record **executed engine capabilities**, not configuration knobs inferred from a model card/UI. The benchmark harness should load the exact selected artifact and serialize the effective physical route before timing begins.

---

## Boundary-edge quarantine — vLLM #57431

PR created `2026-09-17 19:03:30 UTC`, but current metadata shows `updated_at=2026-09-17 19:25:50 UTC`, after the `19:25:05` cutoff.

Topic is highly relevant: decode context parallelism for Qwen4Exp/Qwen3.8-Flash-Next QSA, selector-cache ownership and cache-group geometry. Because the snapshot visible during this search is post-cutoff, **do not promote the current quantitative body into this watch**. Re-open it first in the next pass, where the 19:25:50 update belongs naturally.

This quarantine is deliberate evidence-timestamp discipline, not a judgment about the PR's quality.

---

## Screened but not target-moving

Additional fresh material included ROCm/GLM startup dispatch fixes, MiniMax sparse-cache work, generic spec-decode synchronization removal, Apple/VLM cache-API adaptation, Vulkan bounds issues, and other backend correctness changes. They either reinforce already-promoted rules or lack sufficiently direct transfer to justify expanding the canonical target distribution.

Broader web/HF/community screening found recently crawled Qwen3.8 benchmark pages and M5 Max projects, but no **source-time-qualified new measurement inside this exact 13:43:30–19:25:05 UTC window** on the active dual-M1/TB4 Flash target, single-M1 27B quality lane, RTX5070Ti target, or dual-M1 DS4-0731. Older measurements and crawler freshness were not promoted.

---

## New qualification rules promoted in this window

1. **Drafter attention has its own long-context route identity.** Measure it separately at 128K+.
2. **Async PP decode cohort balance is scheduler state.** Balance established decode without blindly capping prompt work.
3. **Sparse padded width != active valid count != visibility.** All three must be carried explicitly.
4. **Expert residency is a capacity dial.** Record resident fraction, physical memory, miss rate and throughput together.
5. **Host-managed offload state cannot silently enter compiled device graphs.** Compile eligibility is lifecycle-dependent.
6. **Execution thread/stream is state provenance** for MLX materialization, snapshots and cache transitions.
7. **Sequential logical owners can share physical scratch** only when concurrency/shape/dtype/stream contracts prove lifetime compatibility.
8. **Long-context serving needs admission/fairness receipts**, not only cold PP and decode throughput.
9. **Autotune/JIT cache route is consensus state** when collectives differ across hit/miss paths.
10. **Long-soak liveness is a first-class certification axis.** Track forward progress and per-rank divergence.
11. **Auto-placement arithmetic must fail closed on zero/NaN geometry.** Explicit placement success does not validate the heuristic.
12. **Benchmark provenance records the executed engine route**, not inferred/UI settings.

These augment, not replace, the prior standing rules on route provenance, state commit boundaries, memory provenance, speculation economics, PP ownership, QSA selection, padding/sentinel behavior, and lifecycle correctness.

---

## Target status after this pass

### Qwen3.8-Flash-Next — dual M1 Max 64GB/TB4

Planning target remains **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.

This window increases confidence in the *optimization map* more than in the numeric target itself. The most actionable additions are long-context drafter-attention routing, PP decode-cohort balancing, sparse valid-count discipline, explicit scratch lifetime sharing, and distributed warmup consensus. DS4 #1070 is useful cross-platform evidence that Flash-Next remains healthy through 64K on another consumer unified-memory platform, but it does not provide a 128K M1/TB4 rate.

### Qwen3.8-27B — one M1 Max 64GB

Target remains **25 TG / 110 cold PP**. llama.cpp #29044 strengthens the case for treating MTP placement/admission as a separate correctness gate, not a throughput change.

### Qwen3.8-27B — RTX 5070 Ti 16GB + host RAM

Target remains **120 TG / 250 cold PP**. No fresh exact 5070 Ti receipt.

### DS4-0731 — dual M1 Max 64GB/TB4

Target remains **15 TG / 180 cold PP**. oMLX #3720 provides strong non-target Apple evidence about the memory/speed tradeoff of expert residency for DSv4-0731, but it is one M5 Max, a different runtime, and no TB4 PP.

---

## Next implementation priorities for the dual-M1 harness

When the hardware loop comes online, ensure the ruler captures:

- exact SHA on both Macs and result metadata;
- target and drafter per-stage route identity;
- TG at real ~128K active context, not just configured max context;
- cold PP separately from warm/prefix reuse;
- MTP accepted tokens, BPC/round cost, **drafter attention time**, verifier time and policy depth;
- PP per-stage compute, TB4 bytes, wait/idle time and decode cohort width;
- QSA valid count, padded width, selected-block overlap and selector ownership;
- physical memory: settled resident, scratch, profile/warmup, recurrent state, QSA history and transient verifier/indexer work;
- warmup/JIT/autotune identity on both ranks;
- long-soak forward-progress watchdog and rank divergence;
- admission/placement geometry with explicit finite-value checks;
- effective executed-engine settings serialized into every receipt.

## Hard freshness boundary

The new hard source-freshness boundary is **`2026-09-17 19:25:05 UTC`**.

Next search starts strictly after that timestamp. First re-open vLLM #57431 because its current snapshot records a post-cutoff update at `19:25:50 UTC`; its quantitative content was deliberately quarantined here.