# Canonical Runtime / Architecture Research State

Last consolidated: 2026-09-02 05:30 ET.

Purpose: durable baseline for every future Qwen3.8-Flash-Next, Qwen3.8-27B, and
DeepSeek-V4-Flash/DS4 external research pass. Dated `RESEARCH-WATCH-*` files are deltas;
this file carries forward the facts and decisions that must not be rediscovered or silently
dropped.

## Required research-pass protocol

Before any new search:

1. Read this file first.
2. Read `RESEARCH-WATCH-LATEST.md`.
3. Read every dated watch newer than this file's consolidation point.
4. Classify each hit as **KNOWN**, **UPDATE**, **NEW**, or **RECOVERED OLDER EVIDENCE**.
5. Never call an old source new merely because it was absent from a later note.
6. After a useful pass, update the dated delta, this state when a durable conclusion changes,
   and `RESEARCH-WATCH-LATEST.md`.

The protocol exists because older project anchors were previously rediscovered after falling
out of the formal watch-note chain.

## Certified exact 27B verifier state — external research cannot modify this

Current promoted stack:

- P58 FP16 GDN verifier prework
- P61 HPT2 HEADPAIR SDPA
- P69B3 SG2R4 Q8 M4 projection
- P69B6 DUAL64 verifier MLP
- P69B11 QKV(KP2)+Z(KP1) projection bundle
- P69B12 B/A idle-SIMD piggyback
- fixed D3 / verifier M4

P69B11/P69B12 remain effectively tied near 19.55 tok/s on the frozen 29,297-token ruler;
P69B12 remains promoted because its paired certification is stronger causal evidence.

**Next exact-verifier work is P69B13 using existing profiling only.** Do not rerun P69B7
profiling or reopen closed P69B5/P69B6-D/P69B8/P69B9/P69B10-C/P69B11/P69B12 work.

## Durable exact-hardware anchors — 2x M1 Max 64 GB / Thunderbolt 4

### KNOWN since 2026-08-01 — DS4 #607, pre-0731

Source: https://github.com/antirez/ds4/issues/607

- 2x MacBook Pro M1 Max 64 GB
- direct TB4
- serial layer/pipeline split 0:23 / 24:output
- fully resident q2-q4-imatrix, ctx 65,536, 32-bit distributed activations
- long-document decode: 10.03 / 10.07 tok/s
- code decode: 11.00-12.95 tok/s
- long-prompt prefill: 153.7-162.7 tok/s

This predates 0731. It is a topology/economics anchor, not a 0731 result. Plain serial layer
PP on exact M1-Max/TB4 hardware is a low-teens dependent-chain decode system, not a near-2x
multiplier.

### KNOWN — DS4 #922, exact 0731 long-context receipt

Source: https://github.com/antirez/ds4/issues/922

- 2x M1 Max 64 GB / TB4
- DeepSeek-V4-Flash-0731 Quality128, 95.76 GiB
- layers 0:22 / 23:output
- 8-bit distributed activations
- ctx allocation 262,144
- 34,384-token distributed prefill: ~152 tok/s, ~225 s
- 51K CLI prompt succeeds
- external USB SSD mmap caused post-prefill SIGBUS; internal NVMe removed the failure
- TSO=0 and removal of a ~46 GB background memory consumer also mattered to stability

Still no completion-token count or sustained decode TG. Never infer TG from the reported
257-second successful end-to-end completion.

### KNOWN — exact dual-M1 Flash-Next RPC correctness

Source: https://github.com/ggml-org/llama.cpp/issues/27993

Exact 2x M1 Max 64 GB / point-to-point TB4 with Qwen3.8-Flash-Next UD-IQ4_XS. PR #27960
fixed deterministic all-zero output beyond roughly 2K prompt length. 2.5K/4K and q8 KV runs
then became coherent. A 115K/256K needle was started, but no result or sustained TG has been
published.

Distributed recurrent/QSA correctness remains a mandatory bring-up gate before throughput.

## Durable single-M1 Flash-Next calibration

Reproducible M1 Max 64 GB custom llama.cpp work anchors the hardware class:

- target-only ~10.9 tok/s @4K, ~10.0 @32K, ~9.2 @64K, ~8.0 @128K
- native MTP ~17.6 tok/s @4K and ~13 tok/s @128K in the reproducible sweep
- later tuned same-author configuration around 12.9 target-only / ~22 MTP
- prefill roughly 150-180+ tok/s depending on context/configuration

Flash-Next's sparse PLE/n-gram table is a much better SSD-offload candidate than routed
experts: tiny indexed reads can be cheap while expert streaming repeatedly touches much
larger weight volumes.

## Established Flash-Next optimization seams

Future passes should seek status/performance updates rather than rediscover these:

- exact/direct QSA scoring and deterministic selection
- gathered/selected-KV sparse attention instead of full-context masked attention
- QSA/indexer top-k acceleration
- resident PLE / GDN / hyperconnection projections
- batched SSD-backed PLE gather without host synchronization
- MTP prompt-history sidecar / warm-prefix restoration
- recurrent speculative checkpoints kept on-device
- context-adaptive verify width/depth
- compiled multi-row decode and reduced host dispatch
- n-gram-history self-speculation for repeated code/agent workloads
- exact resident prefix/cache reuse
- per-projection mixed quantization as a separate lossy capacity track
- stage-local recurrent state under PP; avoid chatty TB4 collectives
- continuous-batching QSA/cache state must be explicitly ragged-row safe
- MTP economics must be qualified separately for greedy and real sampling settings

### 2026-09-21 18:51 UTC distributed Flash / recurrent-cache retention additions

- **RECOVERED direct two-node Flash-Next evidence — 2x DGX Spark:** a production-verified SGLang recipe dated 2026-08-27 runs `Qwen3.8-Flash-Next-NVFP4` across **2x DGX Spark / GB10 128 GB** with **TP=2 over a direct 200G RoCEv2 link**, native **262,144-token** context and NEXTN MTP. A 30-minute soak reports **~41-42 TG single-stream**, **153 TG aggregate at 8 streams**, and sustained speculative accept length **~2.3**. This is the first recovered exact-family two-node receipt in the P51 state that actually clears the 40-TG headline at native context. It is a **distributed-architecture analogue, not a numeric M1 transfer**: the interconnect is roughly an order of magnitude faster than TB4, the parallelism is TP rather than P51's planned PP2, and CUDA/SGLang kernels differ materially. It strengthens the proposition that full Flash-Next + speculation can sustain ~40 in a two-node deployment, while leaving the Apple7/TB4/PP2 execution question unresolved.
- **RECOVERED exact-family recurrent-cache retention evidence — vLLM #57253:** on `Qwen3.8-Flash-Next-FP8`, 4xB200, 256K AgentX replay at concurrency 128, retiring the Mamba/GDN state that had been registered as a prefix-cache boundary dropped steady-state prefix hits to **49.81%**. Protecting the registered boundary while continuing to retire unhashed intermediate states raises hit rate to **77.48%**, request throughput **1.16 -> 1.89/s (+63%)**, mean TTFT **2,986 -> 1,335 ms**, and mean ITL **63.51 -> 36.32 ms** at equal KV capacity. P51 warm-session state retention must distinguish 'not needed by this request's next forward' from 'not needed by any future prefix consumer'; cache-published recurrent/QSA boundaries stay pinned until the cache ownership/retention policy releases them.
- **RECOVERED distributed-layout design prior — vLLM #51548:** node-local pipeline placement explicitly supports deployments where pipeline stages define node boundaries so **only pipeline activations cross nodes**, while expert/data-parallel communication stays node-local. No performance results are provided, so this is not evidence for P51 TG; it independently validates the architectural reason to prefer PP2 over chatty cross-node TP on a slow TB4 fabric.

**Target effect:** no numeric change. The dual-Spark receipt is materially relevant distributed evidence, but different silicon, TP semantics and 200G fabric prevent a justified change to the current 40-TG @ ~128K confidence ladder. It strengthens the mechanism case, not the target denominator.
### 2026-09-21 17:23 UTC recovered hybrid-prefix replay-boundary rule

- **RECOVERED OLDER EVIDENCE — vLLM #52244:** hybrid full-attention + GDN prefix caching under MTP can have useful state in both cache groups yet still intersect down to an older full page or **zero** if recurrent state is published at the prompt tail rather than at the actual replay landing position after the mandatory last-token cap and MTP/EAGLE rewind. On Qwen3.5-122B-A10B with a 1,072-token GDN page and 67-token fine-grained hash unit, page-boundary replays such as 1,072 and 2,144 tokens went **0 -> 938** and **0 -> 2,010** cached tokens after publishing the rewound GDN state and a reachable full-attention partial tail. A 132-length sweep then landed exactly on the replay ceiling, and temperature-0 outputs on real cache hits were byte-identical in the reported quality check.
- **P51 rule:** prefix/checkpoint publication must be keyed to the **deepest position the consumer can actually resume from**, including last-token replay, speculative rewind, per-group page/hash geometry and recurrent-state availability. Target KV, QSA/recurrent state and draft/MTP state must advertise compatible committed boundaries before the coordinator intersects them. Do not publish a semantically unreachable prompt-tail state merely because it exists physically.

**Target effect:** none. This strengthens the warm-session restore/canonical-state correctness model already in force; it does not move TG/PP or quality confidence.
### 2026-09-21 16:46 UTC Splash-Q8 / warm-MTP / runtime-behavior update

- **RECOVERED stronger-Apple Q8-27B mechanism evidence — Splash-HQ:** a Sep-21 community report on M5 Pro 64 GB uses a model-specific C++/Metal Splash fork with native group-64 Q8 tiled kernels and a 27 GB Qwen3.8-27B target. Across five short task prompts it reports **36.9 TG average**, including **54.8 TG** on the math prompt, versus **26.5 TG** for MTPLX on the same 8-bit base weights; a compressed-Q8 Splash arm reports 36.5 TG. Live context telemetry reaches 190,016 tokens, with deep-context samples mostly in the low-20s to low-30s TG plus cache-hit spikes. Treat this as a **mechanism blueprint, not M1 proof**: the current Splash runtime hard-requires Apple GPU family 9 / M3-or-newer and its Q8 path uses newer Metal tensor/matmul machinery. Project 51's single-M1 27B target remains 25 TG; after P69B13, add a P70 Splash-mechanism campaign that first measures cycle time, dispatch/materialization gaps and accepted tokens/cycle, then tests an Apple7-specific persistent/small-M Q8 kernel only if profiling justifies it.
- **NEW runtime-behavior gate — Splash #90:** on identical Qwen3.6-35B-A3B weights and one fixed Claude Code task, LM Studio completed in **60 turns / 4m38s**, while three Splash runs took **110 turns / 34m09s**, **113 turns / 40m timeout**, and **207+ turns before manual stop**, despite Splash reporting **232 TG**, ~3,400 PP and a 91.8% prefix-cache hit rate. The reporter ruled out different weights, obvious template differences, retries, memory pressure and engine failures; the proposed speculative-distribution explanation is still unproven. Project 51 must therefore certify **end-to-end multi-turn agent trajectories** for runtime/speculative optimizations. Same weights, strong token-level speed and short greedy checks are insufficient to prove behavioral equivalence.
- **NEW warm-path MTP state evidence — oMLX #3770 comments:** on M3 Ultra Flash-Next oQ4e-mtp, current main with the known fixes is faster than dev3 with caching disabled (~119 vs ~110 TG), but a repeated-prompt prefix-cache-hit arm reports **dev3 ~168 TG vs current main ~115 TG**. The evidence indicates a lost warm-path MTP-state acceleration rather than a target decode regression. Project 51 must benchmark **cold/no-cache and repeated identical warm turns separately** and treat restored draft/MTP/recurrent state as part of performance identity; a cache restore that fixes TTFT but fails to restore speculative decode acceleration is incomplete.
- **NEW batch verify evidence — oMLX #3797:** a new M3 Ultra batched-DFlash path adds small-M 4/5-bit verify kernels for 7..24 rows. Qwen3.8-27B aggregate B=4 rises from **83.7 TG** on the old single-stream DFlash engine to **160.7 TG** on batched DFlash2; the Lightning-MTP kernel arm rises **112.0 -> 166.3 TG** at B=4 while B=1 is essentially flat. This is not a Project 51 B1 target change, but it strengthens the rule that multi-request serving needs row-count-specific verify kernels and shared weight traversal rather than one independent verifier pass per request.
- **NEW/confirmed M1 numerical-portability warning — DS4 #1039:** current DS4 main now passes the previously failing M1 Ultra router numerical test after replacing the unstable small-logit softplus evaluation with a log1p-style accurate path. The original pre-M5 discrepancy was large enough to shift one router probability by about 0.5%. Any Apple7-specific Project 51 kernel work must use stable elementary-function formulations and certify against an accurate host/reference oracle; arithmetic that happens to agree on M3/M5 is not automatically portable to M1.
- **MINOR direct model evidence — llama.cpp f4e276a:** vectorizing contiguous conversion on gfx1151 improves Qwen3.8-Flash-Next IQ3_XXS **PP by ~1.26% but TG by only ~0.14%**. This reinforces that prefill-copy work and decode bottlenecks must be optimized separately; it does not transfer numerically to M1.

**Target effect:** no numeric TG/PP or quality-confidence change. The fresh evidence changes the **test plan and certification rules**, not the canonical 40 TG @ ~128K / 400 cold-PP Flash targets or the 25-TG single-M1 27B target.
### 2026-09-21 12:18 UTC DASLab Flash-Next GSQ/RCO qualification update

- **DIRECT Flash allocation evidence strengthened:** ISTA-DASLab's official Flash-Next GSQ/RCO release searches 352 groups; ~95% of searchable weight mass is in routed experts. Its 3.00-bpw IQ3_XXS allocation keeps HC projections/injections and QSA indexer projections at BF16, HC/recurrent/indexer norms/state at F32/BF16, full-attention mostly Q4-Q6 class, shared experts above most routed experts, and routed gate/up expert mass around ~2-bit classes. This strongly validates P51's protected-island / aggressive-routed-expert strategy.
- **QUALITY CAVEAT PROMOTED:** the official 99.4%-of-BF16 AIME25/GPQA-D/LCB-v6 result is primarily **xhigh-reasoning** evidence. DASLab explicitly says calibration used xhigh traces and acknowledges that medium reasoning effort can degrade substantially more; multiple community tests observed this. P51 quant certification must therefore include medium/xhigh/thinking-off rows and agentic token-budget behavior. The 3.00-bpw release is an allocation prior, not >=38 AA certification.
- **FORMAT-COST EVIDENCE:** DASLab's own 55-prompt panel reports Q2_0 2.40 bpw at 367.49 PP / 93.79 TG versus IQ2_XS 2.50 bpw at 108.19 / 70.30, despite only 1.6 GB size difference. Their explanation is quant-format lookup cost. P51's allocator must optimize **actual M1 us/token and hot bytes**, not nominal BPW.
- **MTP remains uncertified for official Flash GSQ/RCO:** unlike DASLab 27B, the Flash release has no official MTP-integrated build/result at this cutoff. Target quality does not imply target/draft agreement; MTP precision and acceptance remain separate optimization identities.
- **PLE remains separate:** DASLab holds the 51.2B n-gram table at fixed IQ4_NL in all evaluated Flash builds. This is useful capacity evidence but does not supersede P51's deep-context Q8-vs-lower-bit PLE acceptance matrix.
- **SEARCH SPACE EXPANDED, production start unchanged:** keep ~4.6-4.9 hot-trunk / MTPLX-Optimized-class as the quality-first production starting region, but add RCO-style ~4.3/~4.0/~3.5/~3.0 experimental allocations where MLX/M1 kernels are efficient. Promote only after >=38 behavioral + long-context + MTP/state certification.

### 2026-09-21 12:03 UTC sparse-canonicalization / failure-cleanup / profile-parity additions

- **NEW canonical-state debt rule — oMLX #3793:** sparse prefill can answer the foreground turn while leaving no independently restorable canonical prefix. P51 should track canonicalization debt separately from request completion and may repay it with bounded, cancellable, machine-idle dense rereads. Advance committed prefix only after the normal cache can read the published block back successfully, and publish hybrid KV + recurrent/GDN/QSA state only at versioned committed boundaries. Background recovery budget must be process-global across engines; execution slice size bounds collision severity.
- **NEW shared-mutation cleanup rule — oMLX #3792:** OOM requeue cleared SpecPrefill ownership without removing the shared RoPE offset wrapper, allowing stale numerical state to leak into later requests. Any request-scoped model/runtime mutation must be reverted while ownership is still provable, before requeue/preemption/cancel/error clears the owner token.
- **NEW profile-before-cache rule — vLLM #57926:** memory profiling that omits serving/warmup sampler work can over-allocate KV and OOM only after cache allocation. P51 admission profiling must exercise actual sampling/logit processing, MTP verify/rollback, QSA/indexer, grammar/tool, recurrent and PP2 workspace paths before assigning remaining memory to long-context state.
- **NEW incremental-prefix planner rule — vLLM #57930:** rescanning already-durable prefix pages and repeating shared materialization once per cache group can dominate scheduler CPU. P51 restore/recovery bookkeeping should use monotonic durable/import cursors and deduplicate shared operations while preserving each target/draft group's native geometry.
- **NEW restored-replay optimization hypothesis — vLLM #57939:** a certified one-token landing replay after a complete imported prefix may be physically decode-shaped even though logically part of prefill. Permit compiled decode treatment only after exact state-identity and numerical-parity certification; partial/failed/preempted/speculative replay must fail closed.

### 2026-09-21 10:36 UTC MTP-recovery / direct-RCO-Flash / recurrent-transfer additions

- **NEW current Apple Flash MTP — oMLX #3791:** Qwen3.8-Flash-Next-oQ4e-mtp on M3 Ultra recovered from 94.34 TG to **116.42-117.13 TG** by eliminating short-block gate/up materialization, reusing verifier fused paths and restoring fused router top-k; MTP acceptance stayed ~90-92%. Audit verify/history-fold copies and fused-path engagement separately from target-only decode. Router fusion changes arithmetic/order and therefore requires behavior + acceptance recertification.
- **NEW quality-first KV mechanism — mlx-serve f66634e:** optimized KV8 attention on M4 Max Qwen3.8-27B improved MTP decode **45->55 @16K** and **37->51 @32K**, beating BF16 KV at 32K on that path. Keep Q8 KV as the default quality baseline until lower precision proves necessary; first optimize dequant/attention kernels.
- **NEW speculative cache-integrity rule — vLLM #56734:** dummy draft steps can write through stale block-table rows and poison cached drafter KV, producing request-local 0% MTP acceptance until cache reset. Padding/warmup/dummy/cancelled rows must be write-inert unless they own a live slot.
- **NEW recurrent-transfer evidence — vLLM #51052:** cross-node/pipeline restore must transfer recurrent conv/SSM state alongside attention KV and define an exact replay landing boundary; KV hit alone is not a valid hybrid-model checkpoint.
- **NEW Apple-family kernel evidence — Splash #88:** Apple9 Q4/MoE decode gains can be very large, but split-K was withdrawn after prompt-specific speculative-acceptance regressions. Arithmetic-changing M1 kernels need rollback toggles and MTP/behavior gates.
- **RECOVERED direct Flash quant evidence — ISTA-DASLab GSQ/RCO:** exact Qwen3.8-Flash-Next **3.00-bpw transformer** allocation retains **99.4% of BF16** on AIME25/GPQA-D/LCB-v6 task average. Public allocation strongly protects HC/recurrent/indexer/control tensors while driving routed expert mass toward ~2-bit classes. Add GSQ/RCO as a first-class sensitivity/allocation prior beside APEX. This is not AA certification and has no MTP-head result.
- **USER-SUPPLIED M3 Ultra cross-runtime receipt:** mlx-serve mixed-4/8 Flash MTP reports **113.1 TG think-off / ~70 TG xhigh**, ~960 PP cold @64K and ~892 PP on a 258K request with 64K cached. Together with oMLX #3791 it strengthens the upside tail, not exact dual-M1 confidence.

### 2026-09-20 19:37 UTC routing-layout / cache-geometry / PLE-quality additions

- **NEW MoE routing correctness — vLLM #57823:** compiled router logits can have padded physical row strides; assuming packed `row * num_experts` silently changed expert selection. P51 >=38 certification must prove eager/reference vs compiled/fused router-selection parity under padded/aligned layouts before attributing any behavior change to quantization.
- **NEW mixed cache geometry — vLLM #57824:** speculative/draft and target cache groups may have different tokens-per-block. Sleep/offload/checkpoint state must use per-group native block geometry or an explicitly versioned canonical form; one target-derived token/block conversion is not safe.
- **NEW nearer-Apple transfer — Splash #43:** capability-gated Splash backend now validates on M2 Max / Apple8, but has no real-model throughput/quality receipt and still provides no M1 proof. Confidence unchanged.
- **NEW Metal observability rule — Splash #44:** command completion/watchdog disarm must precede memory telemetry. Diagnostics cannot sit on the GPU-completion critical path.
- **RECOVERED PLE quality warning:** provenance-verified Strix Halo Flash-Next runs report a 128K MTP reversal between Q8 PLE and IQ4_NL PLE (26.9 vs 18.6 tok/s in one run; mechanism/ratio explicitly unverified, n=1). PLE/ngram precision remains separately accounted from hot-trunk BPW but must be qualified as a **long-context MTP/quality dimension**, not treated as capacity-only.

### 2026-09-20 18:18 UTC quality-floor / batch-invariance / resume-retention additions

- **USER QUALITY TARGET PROMOTED:** production Flash quant must preserve **>=38 AA-class behavior**, with **39-40 preferred**. Current source Flash-Next remains AA Intelligence Index **40**. Quant optimization is now lexicographic: pass the quality floor first, then maximize M1 TG. Candidates below 38 remain experimental speed quants even if faster.
- **NEW in-flight retention — vLLM #57813:** unfinished requests can preferentially pin CPU-offloaded chunks they will resume from, with pressure fallback. P51 sleep/rewind tiers should use request lifetime as an eviction signal so active coding-agent checkpoints outlive completed/background sessions without becoming unevictable.
- **NEW quality/determinism gate — vLLM #57815:** sparse-indexer backend/algorithm selection can vary with batch rows, padded width and concurrency, silently changing selected attention keys even at greedy temperature. P51 >=38 certification must compare B1/B2/B4 + mixed-length batches at QSA-selection/logit/recurrent/MTP levels or pin a genuinely batch-invariant path.
- **NEW PP2 constraint — vLLM #57817:** generic GPU n-gram speculative state is not automatically PP-safe; sampled/draft-token state must be transported/owned explicitly. This is distinct from Flash-Next's PLE/n-gram embedding sidecar, but any P51 n-gram self-speculation under PP2 needs an explicit state-transport design.
- **UPDATE SSD checkpoint viability — Splash #3:** bounded SSD caching now covers KV plus recurrent state with shared-prefix restores, cancellation/failure handling and 128K real-model validation. This strengthens the P51 sleep-idle tier without changing TG/PP targets.

### 2026-09-20 15:28 UTC sleep-preserved prefix tier addition

- **NEW agent sleep/wake rule — vLLM #57810:** accelerator pause/sleep can release device KV and working memory while preserving the external CPU/SSD prefix tier. P51 should distinguish **hot idle**, **sleep idle** and **cold**; `sup` can wake from sleep idle by restoring certified prefix/checkpoint material instead of cold-prefilling. Retained state must be namespaced by model/weights, quant, tokenizer/template, stable-prefix hash, runtime schema and PP2/recurrent-QSA format, and explicitly invalidated when any identity changes. Sleep itself must not imply cache invalidation.

### 2026-09-20 14:50 UTC verify-fusion / warmup-lifetime additions

- **NEW direct Flash verify-fusion fix — oMLX #3776:** Qwen4Exp's post-upgrade verifier uses L2 normalization, so the old RMS-compatible fused GDN prework gate silently failed. A bit-exact L2 fused variant restores T=4 Apple-Silicon verify backbone from **38.9-43.2 -> 33.7-36.1 ms/cycle**, back near the 33.5-34 ms pre-upgrade band, with ~70-77% acceptance unchanged. P51 fast paths must match the active numerical contract rather than simply relax compatibility gates, and must expose engagement/rejection diagnostics.
- **NEW warmup pointer-lifetime bug — vLLM #57807:** dummy graph warmup can initialize a shared hybrid-state context against temporary block-table/cache pointers that later survive into serving. P51 `sup` prewarm must separate compile/warmup artifacts from live state bindings and tear down/rebind every temporary cache/QSA/recurrent pointer before admitting a real request.
- **UPDATE sparse scoring — vLLM #54335/#56984:** selected-token prefill scoring can avoid generic full-row/full-vocab logprob cost, but prefix/session reuse complicates row ownership; skipped rows must never be returned as fabricated scores. Keep classifier candidate domains small and tensorized because nested Python per-row metadata can dominate serialization/copy time.

### 2026-09-20 13:58 UTC rewindable-agent / Apple-runtime additions

- **NEW DS4 #1089:** M5 Max / Metal / ~21K tool chat rewinds a live V4.1 session to the safe shared prefix instead of replaying full client-rendered history. Batched turn 2 re-read **21,357 tokens / 197.6 s -> 95 / 7.4 s**; turn 3 **21,445 / 196.3 s -> 89 / 6.9 s**. P51 `sup` should preserve a rewindable active-session checkpoint and >=2 live slots when auxiliary calls could evict it.
- **NEW exact Qwen3.8 cache rule — vLLM #57128:** after MTP rejection, skip the newest matched recurrent checkpoint if it can contain rejected draft state; do not blindly subtract a token/hash margin because real checkpoints are sparse. Live ~24K shared-prefix case reused **15,440/~18,528** available tokens and cut ~77 s cold to 30-32 s warm on 2x5060Ti.
- **NEW Apple admission/MTP evidence — mlx-serve 06d53afb:** re-bill requests against live wired memory immediately before prefill; stale concurrent admission of four 64K prompts could kernel-panic macOS. M4 Max MTP row-batching reports **109->119 aggregate tok/s** at N=4 and a four-stream policy **64->122 tok/s**. Directional only for M1.
- **NEW Apple prefill tuning method — Splash #36:** M4 Max Apple9 Q4 prefill measured N128/4-simdgroup ahead of N256/8; cold 128K GPU prefill **-2.3%**, 2K-50K ~**-3.6 to -3.7%**, bit-identical. M1 must tune actual contention/continuation row sizes rather than inherit M4 constants.
- **UPDATE:** vLLM #56810 merged cache-class separation; #43310 merged per-request speculative metrics; #56742 explicitly places Qwen4Exp MTP buffers and warms its target kernels; #56698 reinforces that profiled KV maximum is only an upper bound under activation/allocator/concurrency pressure.
- **NEW agent preparation:** Splash #32/#33/#34/#35 add bounded tokenization reuse, phase latency histograms, contention-aware prefill and single-flight grammar compilation. Extend `sup` prewarm beyond model state to stable tokenizer/grammar/tool-schema artifacts.

### 2026-09-20 10:43 UTC cache-integrity / workspace / score-only additions

- **NEW prefix-cache integrity failure — vLLM #57477:** a padded-stride bug in GLM-5.3-Flash tail seeding silently overwrote long-lived cached indexer pages while prefix-cache hit metrics remained healthy. Under allocator churn a cached 14.5K system prompt degraded from 7/7 to **1/7** final lookups; fixed branch stayed **7/7**, and a fresh cache-salt copy was also 7/7. P51 `sup` prewarm must validate **semantic state integrity under churn**, not merely cache hits: long-lived-prefix stress, fresh-namespace control, stage stride/layout identity and behavioral probes are mandatory.
- **NEW tiny-metadata fusion with bounded E2E transfer — vLLM #57534:** 12 kpool slot-mapping launches became 1, removing roughly **0.44 ms CPU enqueue/step with MTP k=1**, but most E2E points remained within noise. Continue profiling/fusing QSA/MTP/rollback/stage-handoff metadata, but promote only E2E TG.
- **NEW persistent-workspace lifetime result — vLLM #57421:** sharing compatible Humming MoE scratch across 40 sequential layers cut scratch storage **10,330.684 -> 258.267 MiB (-97.5%)** and live allocation by **9.836 GiB** at 8192 max batched tokens. Audit Flash PP-stage scratch by lifetime rather than layer ownership; isolate concurrent lanes/ubatches/spec slots.
- **NEW topology-sensitive precision result — vLLM #54894:** replacing BF16 `wo_a` with native FP8 produced materially larger gains under **TP1/PP8 (~6% prefill class)** than TP8/PP1 (~1-2%), with matched full GSM8K on the older checkpoint. P51 quant allocation should include **PP2-stage-local timing** as an objective; single-node B1 timing alone can miss pipeline value.
- **NEW score-only agent primitive — Splash #12:** resident model can score 2-255 answer tokens on the final prefill chunk with **zero output tokens**, while retaining prefix reuse/scheduling/cancellation. This is a strong architecture candidate for tool/skill routing, failure classification, guardrails and compact/retrieve/continue decisions over a warm `sup` prefix. It is not Jev quality parity; calibrate separately.
- **UPDATED exactness caution — vLLM #57756:** an initially promising fused sparse-decode path had to restore baseline split boundaries/reduction order for exactness; corrected fast path is now **shape-gated** and prior service/eval tables are being rerun. Do not retain pre-fix 3.5% service numbers as evidence.
- **UPDATED compile-state caution — vLLM #57451:** request-dependent row/rotation state read inside unsafe compiled code can freeze at trace time; the parent V4.1 failure reportedly lost **0.087 GSM8K** while remaining fluent. Compiled P51 paths must not freeze decode/verify rows, spec width, QSA active rows, rollback state or cache ownership.

### 2026-09-20 08:31 UTC quant-frontier / wake-prewarm additions

- **Quant identity correction:** MTPLX Bare is explicitly **flat 4-bit** for all MoE experts/dense matrices (64-weight groups) with 16-bit GDN/recurrent/norm/QSA-indexer/MTP islands; MTPLX Optimized is explicitly **dynamic 4-bit with Q8 QSA attention**, not a uniform Q5. Treat Bare and Optimized as concrete MLX lower/upper protection endpoints.
- **M1 BF16->FP16 first experiment:** older MLX PR #4216 measured M1 Max INT4/group-32 QMM at **30.6 ms stock BF16 vs 17.2 ms stock FP16 vs 17.32 ms BF16-I/O + FP16 tiles/FP32 accumulate**. First P51 artifact experiment should preserve quantized tensors and make the remaining 16-bit path M1-FP16-native where behavior remains certified.
- **APEX methodology promoted:** mine `localai-org/apex-quant` for perturbation/sensitivity tooling, not preset GGUF recipes. Qwen3.8-27B measurements show a **15.3x** per-byte sensitivity spread and **2.63x** edge-vs-middle FFN sensitivity, but also prove sensitivity is convex and that clever redistribution can lose at a mild Q4 band. P51 should optimize **behavioral quality + MTP acceptance per M1 hot-byte/us saved**, using local perturbations around Bare Q4.
- **Flash APEX tensor prior:** Myric MIDDLE maps 51.2B PLE and 40.265B down experts to Q4_0, 80.531B gate/up experts across IQ4_XS/IQ3_XXS, tiny dense/shared/attention paths to Q6/Q8/F32, and QSA indexer projections to BF16. Row widths **640 (down)** and **160 (PLE)** block many 256-element quant formats while gate/up rows at 2560 remain flexible. Its MTP head is absent, so it is a tensor-role prior, not a P51 quality/speed certificate.
- **Search-band refinement:** keep **4.6-4.9 hot-trunk BPW** as the initial deployment search band, but explicitly test APEX-inspired **~4.3-4.6** experimental arms if M1 kernels make lower-bit gate/up formats faster. Whole-file BPW is not the objective; PLE precision/placement and MTP precision remain separate identities.
- **Agent wake/prewarm protocol:** a trivial Slack/Telegram/iMessage opener such as **"sup"** can trigger stable system/tool/skill/repo-prefix materialization before the real task arrives. Restore/recompute recurrent + QSA/indexer state at a certified boundary, warm verifier/stage buffers, then append the real task when received. Measure wake->ready, restored vs recomputed tokens, physical PP rows, real-task->TTFT, false-wake cost and invalidation rate. Keep this separate from the honest **400 cold-PP** target.
- **NEW exact-family long-context mechanism — llama.cpp #28770:** sparse FA for Qwen4Exp merged 08:08 UTC; on DGX Spark it changed qwen4exp TG **12.00 -> 14.19 at 100K (+18%)** and a PP-shaped 100K test **252.81 -> 318.28 (+26%)**. Different hardware/quant, but it confirms full-cache rescoring becomes a material long-context tax.
- **NEW speculative serial-cost evidence — vLLM #57770:** split-vocabulary greedy draft argmax reduced one full-vocab selection from **43.424 -> 4.352 us at M=1** and **44.415 -> 7.968 us at M=32**. Small draft-selection costs multiply by speculative depth and belong in the verifier profile after larger costs are removed.
- **Splash #16/#18 are now merged:** live-producer prefix reuse and work-budgeted prefill admission are no longer just PR concepts. Splash #22 additionally defers full-history preparation until needed, supporting P51's split policy: prewarm invariant context early, expand mutable history lazily.

### 2026-09-20 05:46 UTC Flash MTP transaction / verify fast-path additions

- **NEW exact Apple Flash regression — oMLX #3770:** M5 Max 128 GB / Flash-Next-oQ4e-mtp dropped **92.6 -> 68.2 TG on code** and **59.1 -> 51.2 on prose** after a runtime integration began opening `SpeculativeCacheTransaction` on every hidden-state forward, including one-token decode and draft calls where rollback cannot occur. That enabled GDN history recording and forced target-verify paths on non-verify work, causing the depth controller to park MTP after 21 cycles. Moving transaction creation to real multi-token verify only recovered **79.8 / 54.6 TG**, **2.4-2.8 tokens/cycle**, **91-95% acceptance** and sustained MTP. Durable rule: **transaction/rollback scope is benchmark identity**; target, draft and verify forwards plus transaction starts/aborts/park cycles must be counted separately.
- **NEW exact Apple Flash verify fast-path regression — oMLX #3771:** with #3770 fixed, dev4 still failed to engage fused GDN verify prework on all 36 GDN layers because eligibility used exact method identity and Qwen4Exp overrides the normalization method. On M5 Max code/prose, dev4 + lazy transaction measured **77.4/57.7 TG**; removing the false gate restored fused verify prework and **81.1/58.8 TG**, versus **96.4/66.6** on the pre-#3719 build. This extends the #3760 lesson from exact-type B1 gates to exact-method verify gates: **fast-path eligibility should be semantic/capability based, and decode vs verify kernel engagement must be instrumented independently**.
- **NEW speculative numerical-exactness warning — llama.cpp #29168:** on CUDA Gemma4 MoE, a target-side weighted-expert reduction fusion changed the numerical path used under speculation: acceptance **0.823 -> 0.481**, MTP **46.35 -> 35.36-36.73 TG**, and drafted greedy output stopped matching plain greedy, while no-draft speed stayed ~37-38 TG. Durable rule: every fusion that differs between plain target and verify target must pass greedy/logit parity plus acceptance/tokens-per-cycle checks; an acceptance collapse can be a **target-path mismatch**, not weak drafting.
- **NEW concurrent-prefix / admission architecture — Splash #16/#18:** waiting requests can attach to a live producer's certified prefix recovery points instead of duplicating cold prefill, and long-prefill admission is budgeted by remaining work/rows rather than merely consuming every state cell. Project 51 should measure **physical prefill rows**, producer/waiter TTFT, cancellation fallback and decode responsiveness; state slots, resident bytes and PP work are distinct scheduler resources.
- **NEW sparse metadata reuse with explicit negative E2E transfer — vLLM #57434:** DeepSeek-V4.1 reduced ragged top-k metadata builds from **38 consumer layers to 8 source results**, cutting launches **380 -> 80 per 10 steps** and removing **250.2 us/step** of GPU work, yet paired E2E step time did not resolve the gain because the loop was partly host-bound. Durable rule: memoize query-independent metadata at source lifetime, but **never promote kernel-time savings to TG without E2E proof**.
- **NEW cross-backend quality reminder — DS4 #1073 strict-window comment:** the current draft Metal-optimization branch on DGX Spark tied main on CUDA speed but produced prompt-length-dependent greedy logit/output divergence. Project 51's frozen quality gate must cover every backend/topology whose semantics we claim to preserve, even when the optimization targets another backend.

### 2026-09-20 01:18 UTC multi-sequence QSA / memory-pressure additions

- **NEW exact-model-family QSA concurrency bug — llama.cpp #29166:** Qwen4Exp `set_input_qsa` per-block bias indexed per-sequence bid arrays by block number. With multiple live sequences in a unified cache, block and bid identities diverge, so a block can inherit another sequence's visibility. A two-live-sequence concurrent repro was **2/4 correct before -> 4/4 after** an inverse block->owning-bid map. Durable rule: **QSA block visibility is keyed by sequence identity + block identity**, and Project 51 multi-row qualification must include independent sequences occupying overlapping position ranges.
- **RECOVERED older long-context optimization + NEW concurrency correction — llama.cpp #28699:** incremental pooled QSA block-summary caching avoids recomputing summaries over the whole context every token/layer. The older 8-GPU Flash-Next/Q8-KV/MTP-n_max2 A/B measured **22.25 -> 24.33 TG at 63K (+9.3%)** and **25.41 -> 27.80 at 114K (+9.4%)**, with bit-identical greedy output; do not transfer the percentage to M1. The implementation also found a single cross-device pooled-indexer buffer could cost roughly **2x decode** on a split setup, supporting **stage-local QSA summary/indexer buffers under PP2**. A strict-window follow-up found pooled rows also need per-sequence ownership; its concurrent shape improved **2/4 wrong -> 4/4 correct** after per-sequence row windows/own-block fill.
- **NEW Apple-runtime memory-pressure evidence — Splash #13/#15:** under advisory host pressure, preserve the newest ordinary recurrent-state resume publication ahead of disposable speculative checkpoints; otherwise hybrid follow-ups can replay the whole prompt. M5 Pro 48 GiB / 27B testing changed an 8K cached follow-up from **22.2/21.2 s with no hit -> 3.03/3.02 s with 8,160 tokens resumed**. Separate two-request testing showed work-aware prefill suspension finishing two 48,022-token prompts in **279 s / exactly 96,044 physical prefill rows**, versus the old path still running at 360 s after **129,942 rows**. Durable rule: reclaim semantic value and record **physical prefill rows vs logical prompt tokens**.
- **NEW speculative-state sizing evidence — vLLM #57721 + Apple confirmation from llama.cpp #28433:** hybrid recurrent page planning that omitted speculative widening fit n_spec=1 but failed n_spec=2 (**819,200 B planned vs 819,712 B required** in the reported case). Separately, an M3 Pro/Metal comment confirms draft-MTP can reserve the target model's total `n_ctx` rather than a bounded/per-sequence draft window. Durable rule: fit/admission is qualified at the **maximum speculative width/depth actually enabled**, while target and draft/verifier context reserves remain separate identities.
- **NEW cold-baseline/cache lifecycle evidence — vLLM #57727 + llama.cpp #29163:** vLLM's prefix-cache reset can clear the GPU tier while a CPU offload tier still serves **1,008/1,024** tokens; a fresh cache salt produced the truly cold path. llama.cpp separately reports HTTP cancellation causing full conversation re-prefill on the next continuation. Durable rules: **cold PP proves every reusable tier cold (or uses a fresh namespace with zero-hit telemetry)**, and agent qualification includes cancellation/interruption followed by immediate continuation.
- **RECOVERED current heterogeneous-quant precedent:** `Vontra/Qwen3.8-Flash-Next-MLX-oQ4` uses a 4-bit affine base with **228 sensitivity-protected modules at 5/8-bit**. Its evidence predates this watch and is not a Project 51 quality/performance ruler, but it supports the feasibility of an APEX/I-Balanced-style Flash-Next MLX artifact. Keep Project 51's stronger identity: ~4.6-4.9 **hot-trunk** BPW with PLE/ngram placement, MTP precision and QSA/indexer precision accounted separately.

### 2026-09-19 22:24 UTC extreme-context packed-KV / multi-row MTP additions

- **NEW stronger-Apple 1M-context Flash receipt — oMLX #3594 / commit `2b8bd0783d37` (2026-09-19 21:50:56 UTC):** Qwen3.8-Flash-Next on **M5 Max 128 GB** serves a **1,004,168-token** prefill with 4-bit TurboQuant QSA K/V, dense QSA indexer sidecar, PLE SSD offload and optional Lightning MTP. The commit reports roughly **950-1250 PP tok/s**, about **14 GB packed KV residency versus 28+ GB dense fp16**, zero memory-guard rejections, and successful needle recall for markers written under an ~870K packed window. A 900K agentic suite completed 41 warm turns; forced cache invalidations re-prefilled ~888K tokens at roughly **1020 PP**, while the warm control reused **99.9%** of tokens with **59x lower TTFT**. This is strong architecture/capacity evidence, not M1/TB4 or deployment-quant proof. Durable rule: **for extreme context, keep QSA selection/indexer state dense while quantizing only the gathered K/V payload**, and bound MTP prompt priming independently (the tested setting uses `mtp_prime_window=65536`). Only the 4-bit TurboQuant path is qualified by this receipt; B>1 packed batching is still serialized.
- **RECOVERED OLDER multi-request Flash MTP evidence — oMLX #3695:** M3 Ultra 512 GB / Qwen3.8-Flash-Next-oQ4e-mtp measured whole-response aggregate throughput **54.12 -> 82.98 TG at B1, 71.74 -> 96.32 at B2, 95.51 -> 107.45 at B3, and 111.14 -> 116.47 at B4** with multi-request Lightning MTP. The marginal MTP benefit falls sharply with concurrency (**+53.3% B1, +34.3% B2, +12.5% B3, +4.8% B4**). This strengthens the existing scheduler rule: **MTP and ordinary batching are competing occupancy policies, not additive multipliers**; benchmark per-concurrency crossover and allow dynamic disable/parking.
- **NEW ragged-cache correctness evidence:** oMLX #3533 received a 2026-09-19 19:31 UTC design correction stating that fused multi-row MTP must validate ragged rollback support **before** mutating the cache and must compute per-row stop/length emission counts **before** constructing the rollback vector. oMLX #3767 separately reports a reproducible M5 Max Qwen3.8-27B multi-request Lightning-MTP crash where TurboQuant `trim()` treats a per-row offset vector as a scalar; Flash-Next qwen4_exp was a 4/4-success control in that report. Durable rule: every batched speculative cache API—trim, rollback, finalize, late join, stop handling—must be explicitly vector/ragged-row safe; never silently degrade a per-row rewind to one uniform scalar trim.
- **NEW PP2 speculative-corruption warning — vLLM #57716:** a B200 **TP8xPP2** Kimi-K3 + DSpark report reproduces all-NaN target rows under concurrent verify load and traces them to poisoned latent-KV page bytes; masked invalid columns are not safe because the P·V path can still propagate **0 × NaN = NaN**. This is different hardware/model and not a Flash speed receipt, but Project 51 PP2 qualification should sanitize newly allocated/reused KV pages, assert finiteness at stage boundaries, and test mixed prefill+decode/spec rows under concurrency before accepting occupancy results.
- **RECOVERED sparse-indexer ragged rule — vLLM #52500, merged 2026-09-19 20:14 UTC:** ragged decode batches can reach the sparse indexer with token count not divisible by batch width even when metadata says padding is unnecessary. The fix forces the padded path when `num_decode_tokens % batch != 0`. Evidence predates this strict window, so the merge is not reclassified as NEW; it strengthens Project 51's existing requirement that QSA/indexer kernels must not infer uniform row geometry from one metadata flag.
- **CORRECTION — llama.cpp #29092 upstream GDN leak attribution narrowed:** strict-window follow-up tests show stock llama.cpp builds are clean on gfx1151 under both system ROCm 7.1 and Ollama's bundled ROCm 7.2, while the Ollama 0.34.1 bundled `llama-server/libggml-hip` still leaks prior-request GDN state. Treat the reported cross-request leak as **Ollama-build-specific until contrary evidence appears**, not a current upstream llama.cpp/GDN source defect.

### 2026-09-19 18:44 UTC exact-M1 MTP-depth / chunk-parity additions

- **NEW exact-M1 Qwen4Exp optimization evidence — DS4 #1056:** a 2026-09-19 18:21:45 UTC M1 Max 64 GB rerun of `11811b9` versus `antirez/main@8db1d1d`, with effective chunk size pinned in both arms, reports resident target-only decode gains of **+15.2% @575 tokens, +14.1% @5,760, +13.5% @17,408/ctx32K** and MTP-on gains of **+15.5%, +15.6%, +7.7%** respectively. The deepest MTP acceptance moved from an earlier optimized **70.8% (51/72)** back to **59.0% (46/78)**, approximately the base **59.5% (47/79)**, while the 5,760-token cell improved to **83.6% (56/67)**. This is exact target-generation hardware/model-family evidence but Q2, single-node and <=32K, not the Project 51 ~4.6-4.9 hot-trunk / ~128K / dual-M1 topology. Durable rule: **MTP/verify improvements must be qualified at multiple prompt depths with target-only TG, MTP TG, acceptance/tokens-per-cycle and rollback/verify counters together; medium-context acceptance does not transfer to deep context.** No target-confidence change until the ~128K/PP2 interaction is measured.
- **Chunked-prefill parity can be an explicit correctness gate:** the same #1056 rerun shows `11811b9` at 5,760 tokens is **bit-identical to an unchunked reference** at chunks 8192/2048/128, while main differs by up to **0.594551 / 1.132671 logits** at 2048/128. At 17,408 tokens the PR is cross-chunk invariant (spread **0.000000**) but an absolute one-pass reference does not fit on 64 GB. Durable rule: compare performance-oriented chunked PP to an unchunked reference when feasible; when it does not fit, label cross-chunk invariance as weaker than absolute parity.
- **PP2/MTP instrumentation implication:** Project 51 distributed speculative experiments must log per-stage proposal/verify occupancy and bubble time in addition to acceptance. A faster target stage with lower deep-context acceptance can reduce or erase the expected PP2 win even when single-node target decode improves.
- **Fresh llama.cpp MTP regression — #29148:** build b10991+ is reported to stop loading Qwen3.8-Flash-Next Q4_K_XL with MTP on Strix Halo/Vulkan. Root cause is unresolved and it is non-Apple, so it does not move targets, but it reinforces the existing rule that every candidate runtime SHA needs a Flash+MTP load/graph-build smoke test before throughput qualification.

### 2026-09-19 17:24 UTC verify-wave transfer qualification / compact-draft additions

- **Splash transfer qualification correction:** the current public Splash README requires **Apple M3 or newer**, and strict-window issue #9 (created 2026-09-19 16:04 UTC) explicitly requests an **Apple GPU family 8 / M2 Ultra backend**. Therefore Splash's exact Metal kernels/presets are **not directly portable evidence for M1 Max**. Its Project 51 value is architectural/methodological: dedicated verify-row kernels, bounded draft context, speculative-wave scheduling, quantized-KV reuse, and representative-shape autotuning. The direct M1 evidence for verify-side headroom remains Project 51's own 27B campaigns; Splash is corroboration, not the M1 ruler. This correction does **not** reverse the current ~65% 40-TG confidence because that confidence also rests on exact M1 verifier gains and independent multi-row evidence, but future references must not call Splash an M1-generation result.
- **STRICT-WINDOW / duplicate-writeup mechanism evidence — vLLM #57703:** a new ROCm PR (created 17:08 UTC, closed as duplicate of older #56861/#57085) documents the same multi-token verification problem Project 51 is targeting: expanding K verify tokens into K single-query rows repeatedly reads nearly the same committed KV prefix. The native block path keeps the K-query verify group together and amortizes the prefix read; an experimental two-stage form separates **stage A = common committed prefix** from **stage B = small causal draft window**, then merges output/LSE. Directional MI355X measurements report c1 **15.23 -> 19.15 TG (+25.7%)** and much larger aggregate gains, but the author explicitly notes the fixed-probe arms were not perfectly isolated. A real 1P1D TP8/DCP8 Kimi-K3 deployment with DSpark K4 reported **623.58 output tok/s vs 487.44 no-spec** at c48 over 1200 s with acceptance length ~3.37. Because #57703 is a duplicate and its measurements were collected on an earlier integration base, treat this as **recovered/confirmatory mechanism evidence, not a new target-speed receipt**.
- **Project 51 verify-wave rule strengthened:** for multi-row verification, separate the **shared committed-history work** from the **tiny candidate-tail causal work** wherever semantics permit. For Flash/QSA this does not mean attention output is identical across candidate rows; query-dependent QSA selection still matters. It means block-key/indexer reads, selected-page staging, common-prefix metadata and KV traversal should be designed to reuse work across the verify block rather than serially replaying the whole prefix for each row.
- **NEW compact-draft-vocabulary opportunity — llama.cpp #29143/#29145:** Qwen3.5 MTP sidecars can use a trimmed draft vocabulary (example **32,768 vs 152,064** target vocab) with a `d2t` mapping. The PR sizes the draft LM head to the compact vocabulary and scatters draft logits into a full-vocabulary -inf canvas before target sampling. It reports **102.2-113.9 TG vs ~44.5 TG autoregressive** on dual RTX PRO 6000-class GPUs with up to **82.89% acceptance**, but that comparison does **not isolate vocabulary trimming from MTP itself**, so no speed percentage transfers. Project 51 should nevertheless consider draft-vocab pruning as a separate MTP-side optimization because the draft LM-head projection is paid every proposal cycle. Qualification must check d2t mapping, unsupported-token behavior, acceptance, and scatter cost.
- **RECOVERED OLDER EVIDENCE — Unsloth Flash MTP carry failure/fix:** Unsloth llama.cpp PR #220 (merged 2026-09-18 10:18 UTC) explains that an upstream Qwen4Exp HC gamma schema change left the fork-only MTP head with a stale shape, causing MTP model-load aborts. A second bug made the fit estimator omit memory for a borrowing/shared draft head. Repinning to the fixed head restored B200 Q4 Flash MTP to **61.2-63.6 TG**; an older working prebuilt measured **60.7 TG with MTP vs 43.8 without**. The later Unsloth release's “2x faster MTP hotfix” language should therefore be read primarily as **restoring a broken MTP carry**, not evidence of a fresh 2x algorithmic optimization. Durable rule: trunk architecture/schema changes require explicit MTP-side ABI/shape parity tests, and fit/admission must budget borrowed/shared draft tensors even when the draft artifact does not own a duplicate tensor.
- **CURRENT-DAY, timestamp-not-qualified Apple8 receipt:** oMLX's public benchmark site currently shows a 2026-09-19 **M2 Ultra 76c / 192 GB** Qwen3.8-Flash-Next-oQ4e-fp16-mtp session on dev4: **20.5 TG @1K, 22.3 @4K, 23.9 @16K**, with **621.8 PP @16K**. Its batching panel reports **20.5 B1 -> 39.8 B2 (1.94x) -> 42.7 B4 (2.08x)**. The public page exposes the date but not a source timestamp precise enough to place the measurement inside this strict window, so it is not counted as strict-window NEW. It is useful Apple8 evidence that MTP/batching can nearly double from B1 to B2 and then saturate rapidly; it is not M1/TB4 or ~128K evidence and does not move the B1/B2-B4 ladders.
- **STRICT-WINDOW anecdote rejected for forecasting:** a new Reddit post reports >70 TG after Unsloth v0.1.811-beta where the same user previously saw 20-50 TG, but no hardware, quant, context, output length or controlled A/B was supplied by cutoff. A Strix Halo commenter reports ~30 TG. Keep as ecosystem smoke only; no Project 51 numeric credit.

### 2026-09-19 15:55 UTC runtime-path eligibility / fusion-concurrency additions

- **NEW exact Apple Flash regression diagnosis — oMLX #3760:** the previously measured Qwen3.8-Flash-Next dev4 decode regression was traced to a runtime-wrapper interaction, not a fundamental mlx-vlm slowdown. Reclassing quantized projections to `_VLMQuantizedPrefillLinear` made a fast-path gate using exact type identity (`type(linear) is nn.QuantizedLinear`) fail, so all **36 GDN layers** stopped using the fused B1/T1 GDN decode prework/norm-gate path. The wrapper also performed about **470 environment lookups per generated token** across ~230 projection calls. Fixing the gate to accept subclasses and hoisting environment reads restores M3 Ultra Flash-Next oQ4e MTP-off decode from **45.8/48.1 -> 51.8/51.7 TG @4K** and **42.6/45.0 -> 48.2/48.5 @16K**, essentially back to dev2. Durable rule: **resolved fast-path eligibility and hot-loop configuration lookup counts are benchmark identity**; wrapper/reclass changes must have explicit kernel-engagement counters.
- **NEW Metal fusion-concurrency regression lesson — llama.cpp #29134:** a generic Metal fusion-table refactor reduced Gemma-4-26B-A4B decode from about **85.2 -> 79.4 TG (-6.8%)** even though the same fused kernels still matched. Root cause was packing multiple adjacent fusion patterns into one structural pack, reducing reorder/concurrency freedom (**720 -> 662 concurrent nodes/decode graph**). Packing one fused-kernel pattern per structural pack restores **85.0 TG** while retaining later PP gains. The same patch is neutral on Qwen3.8-Flash-Next UD-Q3_K_XL (**36.46 -> 36.77 TG; 654 -> 656 PP**), so this is not a hidden Flash speedup. Durable rule: **more fusion is not automatically faster**; Project 51 fusion A/Bs must record graph concurrency/overlap, not only fusion counts.
- **NEW sparse-indexer workspace sizing evidence — vLLM #57701:** GLM5.3's sparse indexer had decode workspace sized to raw max model length even though the actual KeyPool is compressed by `index_kpool=4`. Sizing to pooled length is bit-identical and reduces the profiled decode workspace by **512 MiB at 262K** and **3072 MiB at 1,048,576**, with essentially unchanged kernel latency. This is not Qwen4Exp evidence, but Project 51 should audit every QSA/indexer scratch allocation against **effective selected/pooled length**, not nominal context length.
- **NEW agent live-prefix checkpoint evidence — DS4 #1093/#1092:** GLM tool turns were clearing the live checkpoint when the client omitted generated reasoning from the replayed assistant message. On M4 Max / GLM-5.3-Flash Q2 / MTP, preserving a visible tool-turn checkpoint reduced one follow-up from **765 re-prefilled tokens / 4.2 s** to **84 tokens / 1.2 s**; the production symptom had fallen from a ~50.7K live frontier to a 20.5K disk block, causing ~30K tokens / ~100 s of repeated prefill. Project 51 agent cache qualification must treat the **visible client-replay surface** as a first-class checkpoint key and test reasoning-omitting tool clients explicitly.
- **NEW 27B ANE+DFlash mixed result — oMLX #3761:** M5 Pro 64 GB, Qwen3.8-27B-4bit + DFlash2, three alternating pairs. ANE prefill at 8K improves **493.7 -> 536.5 PP (+8.7%)** but generation falls **39.6 -> 35.1 TG (-11.4%)**, for **4.6% lower total request time**; at 4K prefill falls **513.9 -> 454.1 (-11.6%)** and total time worsens **9.5%**. ANE adds ~**3.83 GB** peak memory. No target change: phase-local acceleration can lose end-to-end because of memory/dispatch interaction; require total-request and generation checks beside PP.
- **RECOVERED OLDER EVIDENCE — long-context sparse-QSA CUDA real workload:** a Reddit post timestamped **2026-09-19 05:05:20 UTC** (therefore older than the prior hard boundary and not strict-window NEW) reports Qwen3.8-Flash-Next UD-Q3_K_XL with MTP off on RTX PRO 4500 32 GB + 64 GB RAM sustaining **27.9 TG token-weighted** over 35 agent requests as context grows **116K -> 148K** (27.7 / 28.5 / 27.5 by context bucket). It attributes flat long-context decode to sparse QSA + persistent block-key caching; warm PLE disk traffic was only ~5 GB/52 min. On that CUDA setup F16 KV beat Q8_0 **38.1 vs 33.4 TG** at ~49K prompt/65K context while costing ~808 MiB more. The sparse-QSA patch is explicitly experimental and long-context parity was not certified, so this is mechanism support only: benchmark KV precision as a speed/fit trade, and never assume Q8 KV is free.

### 2026-09-19 recovered Splash evidence — speculative-cycle architecture

- **RECOVERED OLDER EVIDENCE, not strict-window evidence:** `incoai/splash` was published before the current 11:04 UTC freshness boundary, but its public runtime/source was only fully audited afterward. It is therefore recorded as recovered evidence and does not advance the external-search boundary.
- Splash's Qwen3.8-27B path is a highly model-specialized Apple runtime rather than a generic backend. Its decode path makes speculation mandatory and hard-codes **8 target verify rows / 7 proposal tokens**, with separate Q4 decode/verify kernels, Q8 paged target KV read directly by verify attention, bounded draft attention state, one-cycle state commit, and model/hardware-specific offline kernel selection.
- The key Project 51 transfer is **mechanism validation, not the 144-TG number**. Splash demonstrates that on Apple Silicon a mature runtime can get most of its effective-generation gain from reducing the cost of a multi-row target verification pass and increasing useful accepted tokens per target pass, even when ordinary target B1 bandwidth remains the fundamental floor.
- This independently matches two existing Project 51 signals: (1) our own two Qwen3.8-27B tuning campaigns produced their meaningful gains primarily on the MTP/verify side; and (2) llama.cpp #29110 moves Qwen3.8-27B at 131K from **32.5 -> 44.5 TG (+37%)** at MTP depth 2 while the n_max=1 path barely changes (**34.2 -> 35.4**). The three lines of evidence converge on verify-side specialization as a real Apple optimization surface.
- Splash's public source also validates several concrete future Project 51 tactics: treat the speculative **wave** as the scheduling unit; tune verify kernels separately by row width and history bucket; reuse quantized KV/history across all rows of a verify wave; keep draft-context cost bounded independently of target context; tune on actual representative model weights/layers rather than one synthetic shape; and qualify candidates using paired alternating A/B timing plus exact-output checks.
- **Forecast effect:** this does not justify transferring Splash's 144-TG M5-Max headline or raising the headline target above 40 TG. It does justify a modest confidence expansion because the exact mechanism required by the dual-M1 thesis is now independently demonstrated in a mature Apple runtime. Project 51 40-TG planning confidence moves **~60% -> ~65%**, >=35 moves **~80% -> ~85%**, >=45 **~35% -> ~40%**, and >=50 to **~20%**. Cold-PP confidence is unchanged.

### 2026-09-19 11:04 UTC upstream Qwen4Exp Metal additions

- **NEW upstream post-Kadir Metal fusion work is now directly applicable to qwen4exp graphs.** llama.cpp commit `5b59b83f4e2101ea173d4f853a0522d9971f48c6` / PR #28948 merged at **2026-09-19 10:14:44 UTC** and adds Metal top-k MoE routing fusion, MoE weighted-reduction fusion, RMS_NORM+SCALE fusion, and SSM_CONV+SiLU fusion plus safer fusion/reorder infrastructure. The merged Metal fusion baseline explicitly contains `qwen4exp` patterns for **MUL+ADD, RMS_NORM+SCALE, SOFT_MAX+ARGSORT+GET_ROWS+SUM_ROWS+CLAMP+DIV, and SSM_CONV+UNARY**, so this is not merely transfer from unrelated architectures.
- #28948 publishes no direct Qwen3.8-Flash-Next benchmark. Related Apple measurements show the same generic patch gives **+12-16% TG** on Qwen3.5-MoE 35B on M2 Ultra/M5 Max, about **+3-5%** on dense Qwen3.5 27B, and smaller gains on DeepSeek4/Gemma depending shape. Do **not** transfer these percentages to Flash or add them to Kadir. The correct interpretation is narrower: there is now verifiable **post-2026-09-08 upstream optimization headroom in graph patterns Flash-Next actually uses**, supporting the upper end of the existing ~5-15% single-node target-only headroom estimate until a physical Flash A/B exists.
- **NEW qwen4exp HC backend support:** llama.cpp commit `59fc5a1ca3842241dd53617ae2ae030c1a015061` / PR #29000 merged at **2026-09-19 08:27:31 UTC** and adds Metal support for the qwen4exp gated `hc_pre` variant (sigmoid gate + scale) and identity `hc_post` variant. No performance numbers were posted. This improves upstream architectural coverage but is not itself speed evidence.
- **Kadir overlap remains uncertain rather than zero.** His frozen September 8 fork already carried custom qwen4exp HC/QSA/Metal work, so some conceptual overlap with today's upstream fusion campaign is possible. However, today's generic fusion infrastructure and qwen4exp fusion-baseline coverage post-date his runtime. Project 51 should benchmark **Kadir frozen -> current upstream/fusion backport** as a controlled A/B instead of assuming either full additivity or full duplication.
- **NEW runtime-regression methodology evidence:** vLLM #57680 reports Qwen3.6-35B-A3B-FP8 on one H100 dropping from **148.3 -> 41.4 TG at c=1** and **1295 -> 362 TG at c=12** between vLLM 0.26 and 0.29 despite nominally identical attention/MoE/cudagraph backends. CPU-side `aten::copy_` call count falls while mean wait per call rises **109.5 -> 563.1 us**, indicating GPU completion latency rather than extra copies. 0.29 also alternates between ~41 and ~61 TG request-by-request. This reinforces two Project 51 rules already in force: exact dependency/runtime SHA is benchmark identity, and repeated runs must preserve/report multimodal or bimodal distributions rather than hiding them behind one median.
- **Agent-history hygiene transfer:** oMLX #3758 shows a long-agent DeepSeek-V4.1 session where one stochastic reasoning loop is replayed back through `reasoning_content`, creating a self-reinforcing few-shot attractor; a 40,583-token loop ran at **99.4% MTP acceptance / 5.80 tokens per cycle** because the target itself wanted the repeated text. This is not Flash performance evidence, but Project 51 agent evaluation should cap/strip historical private reasoning and distinguish high MTP acceptance from semantic health: speculation can accelerate a pathological target trajectory perfectly.

### 2026-09-19 07:51 UTC Flash quant / Metal-MTP additions

- **Flash quant identity is now component-wise, not one whole-file BPW number.** Project 51 will record **hot compute-trunk BPW**, **PLE/ngram BPW + placement**, and **MTP BPW** separately. Whole-file BPW can be misleading because Flash carries roughly 51.2B PLE/ngram parameters that can live on SSD/offload paths. oQ5e remains the quality/certification comparator; oQ4e remains the aggressive performance comparator; the intended deployment lane is a **custom mixed quant around ~4.6-4.9 hot-trunk BPW**, with sensitive QSA/GDN/HC/router/head/MTP tensors allowed more precision.
- **AtomicChat 4.27 should not be read as a 4.27-bpw hot trunk.** Its published recipe spends roughly 6-bit-class precision on the giant PLE table and much lower precision on much of the expert trunk. Using 177B total parameters and 51.2B PLE parameters, a simple arithmetic back-out places the non-PLE remainder around the mid-3-bit range (~3.6 bpw before file-format nuances). This is an engineering estimate, not artifact-reported hot-trunk BPW.
- **Fresh custom-quant allocation evidence — nitinpanj Flash-Next V3:** a 95.5-GiB checkpoint for 64-GB Apple Silicon starts from Q4_0, upgrades output.weight to Q8_0, and splices UD-IQ4_XS into resident **attn, hc, token_embd, ssm_out, shexp** groups. Paired 40-chunk perplexity improves **5.2777 -> 4.3148 (-17.8%)**, better on **40/40** chunks, while draft acceptance improves **0.751 -> 0.817** for only **-2.7% decode speed** and +1.69 GiB disk. This strongly supports role-aware custom quantization rather than uniform bit allocation.
- On **M5 Pro 64 GB**, the same fork reports about **18.0-18.6 target-only TG**, **~27.6 TG with MTP**, **~367 PP at 4K**, and **~20.6 TG at 29K real chat context** with internal-SSD expert streaming. MTP depth 3 is reported optimal; depth 4 was slower. This is stronger-chip / different-topology transfer evidence, not an M1 target receipt.
- **NEW exact Apple Flash runtime regression:** oMLX #3755, M3 Ultra 96 GB / Flash-Next-oQ4e-mtp / MTP off / SSD n-gram offload, reports ~128K cold decode **41.3 -> 37.6 TG (-9.0%)** and warm **~41.0 -> 36.5 (-10.9%)** on dev4 versus the earlier tested build; 16K cold is **49.2 -> 45.6 (-7.4%)**. Prefill is **+3-7% faster** and model residency remains ~68 GB. Keep exact oMLX/MLX version pinning and deep-context decode A/Bs mandatory.
- **NEW Metal MTP-verify kernel evidence:** llama.cpp #29110 adds multi-column Q4_0/Q8_0 mat-vec kernels for verify rows 2..8 on M3 Ultra. On Qwen3.8-27B Q8_0 at 131K, MTP depth 2 improves **32.5 -> 44.5 TG (+37%)** with acceptance **0.836** and byte-identical output; on an 89,575-token code prompt it improves **17.06 -> 20.28 TG (+19%)** with acceptance unchanged at 0.678. It is not Flash-Next, but it is direct Apple evidence that small-row verify memory traffic can be a large removable bottleneck.
- **NEW recurrent rollback correctness evidence:** llama.cpp #29117 shows hybrid/recurrent partial rollback can silently restore the wrong snapshot after intervening single-token decode steps. Its provenance/index-shift approach makes **9/9** external rollback cells exact on lfm2moe/qwen35 where the previous path produced stale/refused states. Project 51 speculative rejection/edit-turn rollback must carry explicit state provenance and fail closed to re-prefill when the exact prior state no longer exists.
- **NEW distributed hybrid-state geometry evidence:** vLLM #57661 reports DeepSeek-V4.1-Flash NIXL P/D output corruption because transfer regions sharing a base address had different block lengths. Deduplicating by **(base_addr, block_len)** fixes the physical reproduction. Project 51 distributed state identity must include offset/stride/block length and not infer semantic identity from shared backing storage alone.
- **NEW dynamic-speculation admission evidence:** vLLM #57658 makes Hybrid Mamba admission use the scheduler's actual step-local speculative K instead of max K. Its Qwen3.5 DFlash throughput rises **414.8 -> 752.6 tok/s** at concurrency 16 and **392.2 -> 950.2** at 32 by admitting more work. Do not transfer the percentages to Flash B1; do carry the rule that B2-B4 admission must budget the **effective per-step verify width**, not a static worst-case K.
- **Metal fusion headroom remains plausible after Kadir:** DS4 #1090 archives M3 Ultra campaigns with GLM-5.3-Flash Q4 decode **+28.5-29.6%** and DeepSeek-V4.1-Flash Q4 about **+36-37%** from HC/KDA/projection fusion, sparse attention and router/shared-expert work. These are different models and historical baselines, so they do not move Project 51 targets or imply Kadir has 30% easy headroom.


### 2026-09-18 23:56 UTC interpretation correction — qwen38-mac-fast tuning depth

- Re-review of `kadirbalalan/llama.cpp` shows the recovered 23.31 TG @117,764 receipt is already a **substantially tuned single-M1 stack**, not a near-stock baseline. Its lineage includes a large Qwen4Exp Metal optimization patch, indexed sparse attention, QSA block scoring, Qwen hyperconnection kernels, direct PLE staging/reader support, and a dedicated Q8 selected-row gather/dequant path. The final runtime was explicitly frozen as an indexed-Q8 Metal fast path.
- Therefore the receipt remains strong evidence for the **single-M1 physical floor**, but should not be used to assume another large easy target-only speedup on the same Mac. Realistic remaining single-node target-only headroom is more plausibly incremental (~5-15% typical, larger only if a currently unknown bottleneck is found), while larger effective-TG gains depend on MTP acceptance/verify cost and the second Mac's ability to stay occupied through multi-row pipeline overlap.
- Numeric targets stay **40 TG @~128K / 400 cold PP**. Planning confidence is recalibrated to about **60% for 40 TG** and **70% for 400 PP**. This is an interpretation correction using already-known evidence; the external-search freshness boundary does not change.

### 2026-09-18 21:34 UTC Flash / recurrent-state additions

- **2026-09-18 post-audit qualification correction for the Kadir M1 receipt:** the frozen benchmark branch is substantially more tuned than a stock llama.cpp run. It inherits Tarruda's large Qwen4Exp Metal optimization patch (model-specific QSA block scoring, indexed sparse FA, HC reduce/combine and related graph work), includes QSA/PLE graph-input reuse, direct PLE staging, direct-reader support, a Q8 selected-row gather/dequant Metal kernel, Q8 KV, single-slot/cache-RAM-zero serving, and the packed/cached QSA path. Therefore **23.3 TG @117.8K should not be treated as a lightly tuned baseline with 20-30% obvious target-only headroom**. A reasonable remaining target-only M1 optimization allowance is closer to **~5-15% likely, ~20% stretch** on the same 4.27-bpw lane before fundamentally new speculative/distributed machinery.
- **Correctness caveat on that receipt:** the final runtime commit `535e1f69d...` has parent `43cb304d...`, whose commit message explicitly says **"WIP: packed QSA indexer V cache experiment — deterministic parity is not yet proven. Do not merge into stable."** The final Q8-fast-path commit does not remove that experiment, and the frozen `qwen4exp.cpp` automatically takes the cached-QSA path under sparse-QSA conditions. No later parity-certification commit exists in the frozen branch history. Thus the 23.3-TG result remains a real physical throughput receipt, but **not a Project-51-quality-certified semantic ruler** until the packed-QSA/cached-indexer path passes deterministic/logit parity tests.
- **The main unharvested headroom is not ordinary target decode.** Published profile explicitly keeps **MTP OFF** and n-gram speculation OFF. Although the fork contains Qwen4Exp MTP support, its MTP graph states a v1 simplification: the draft block **attends densely** and has a TODO to wire QSA for long-context draft fidelity. At ~128K this makes the shipped MTP path unsuitable as evidence for easy speculative gain. Modern sparse/draft-aware MTP, adaptive verify width/depth, final-token-aware PLE staging, and PP2 multi-row overlap are separate engineering work, not toggles the author simply forgot to enable.
- **RECOVERED OLDER EVIDENCE — strongest modern single-M1 long-context Flash receipt:** `kadirbalalan/qwen38-mac-fast`, commit `feeb3d57bf340f027f55eb56760c736cd80c4326` dated **2026-09-08**, publishes raw controlled JSON for Qwen3.8-Flash-Next on **one M1 Max 64 GB** using AtomicChat **AD-4.27bpw-Q4_K_M-M64**, Q8_0 K/V, Flash Attention, one slot, Metal indexed QSA with Q8 selected-row gather/dequant, direct PLE `--lazy-mode on-direct`, batch/ubatch 512/256, **MTP OFF**, runtime commit `535e1f69d4bdf9c9aa51619636595d155ff02ccf`. Controlled 384-token generations measure **23.80 TG / 208.84 PP at 84,984 prompt tokens**, **23.79 / 206.87 at 93,212**, **23.47 / 205.27 at 101,396**, **23.28 / 202.46 at 109,580**, and **23.31 / 203.18 at 117,764** using on-direct PLE. A 148,476-token stress run measures **20.51 TG / 152.03 PP**. This is exact target-generation hardware, exact model family, near-target quant precision and long context, with checked-in raw receipts; it is the most relevant single-M1 physical anchor currently known. It is **not** exact Q5, not dual-M1/TB4, and the machine reports ~11 GB system swap during the controlled long-context runs, so do not double the result or transfer it directly.
- The same recovered receipt shows Q8 KV is nearly free in speed at ~77K: F16 KV **24.01 TG / 209.78 PP**, Q8 KV **23.92 / 211.00**, while system-wide wired memory drops about **1.0 GiB**. This supports Q8 KV as the default long-context M1 capacity lane unless a target-topology A/B says otherwise.
- **Flash planning confidence rises, target does not:** the direct single-M1 4.27-bpw receipt removes much of the previous uncertainty about whether modern indexed-QSA/direct-PLE execution can sustain low-20s TG and ~200 PP near 128K on M1. The remaining gap is specifically Q4.27->Q5-class bandwidth/quality economics plus PP2/TB4/state/MTP overlap. After the post-audit parity caveat, durable planning confidence is moderated to about **60% for 40 TG @~128K** and **~70-75% for 400 cold PP**. The physical throughput is real, but Project 51 should not grant it full semantic-certification weight until packed-QSA parity is proven.
- **Plain MTP must not inherit EAGLE draft-KV assumptions.** vLLM #57616, on Qwen3.8-Flash-Next NVFP4 / GB10 / MTP k=3 / 262K, shows plain MTP shares target KV and has no separate draft KV group. A conservative “no draft group identified => all groups are EAGLE” fallback caused **zero prefix-cache insertions/hits**. The fix restores **6400/12778 = 50.1%** cache hits and repeat-prompt TTFT **3.6 -> 1.6 s** with MTP acceptance unchanged at 44.5%. Project 51 cache logic must model native MTP as target-state speculation unless an actual separate draft state exists; EAGLE/DFlash fallbacks cannot be applied generically to every speculative method.
- **PLE staging for verify must occur after the draft tokens are known.** vLLM #57608 uses Qwen3.8-Flash-Next NVFP4 on GB10 with disk-backed PLE and MTP k=3. Staging PLE rows in `prepare_inputs` before draft proposal omits the draft-token tail from verify inputs and drops acceptance **44.5% -> 34.6%** with visible quality regression. Computing rows at the true verify frontier inside piecewise eager segments is correct but costs about **7% decode throughput** versus FULL_DECODE_ONLY graphs. Project 51 must stage any token-indexed PLE/QSA side data from the **final verify token sequence**, not from pre-draft target inputs; draft->verify becomes an explicit host/preparation boundary when side data depends on proposed token IDs.
- **Lookahead allocation is part of recurrent-state correctness.** vLLM #57605 shows Mamba/GDN align-mode lookahead crossing a page-aligned main-model boundary can either write into a recycled stale block or displace the worker's running-state column with a null slot. On a 4-node Thor GLM-5.3-Flash cluster this caused deterministic **0% spec acceptance** after boundary-ending chunks. After next-page materialization + padding from main-model length, the full prompt-size ladder and a **22-turn / 360K-prompt-token** conversation remain coherent with mean acceptance length ~3. Project 51 recurrent-state qualification must include page-aligned chunk endings with lookahead/speculation and verify physical block-table ownership of the next state page.
- **Cross-request recurrent-state reset is a privacy/correctness gate, not merely a speed test.** llama.cpp #29092 reports Qwen3.6-35B-A3B and **Qwen3.8-27B** on HIP/gfx1151 with fused Gated DeltaNet carrying previous-request recurrent state into a reused server slot. At temperature 0, later requests can emit earlier prompts' text verbatim even after full `memory_seq_rm [0,end)`; disabling the fused GDN path clears the three-request repro on the older build. Across 29 unrelated documents the contamination accumulates into degraded output. Although this is HIP rather than Metal and not Flash-Next, the mechanism is directly relevant: Project 51 must run multi-user slot-reuse probes with disjoint synthetic vocabularies and assert zero cross-request state leakage after cache reset, checkpoint restore, cancellation and slot reuse.
- **oMLX dev4 has a separate MTP state/correctness regression beyond raw verify cost.** #3742 bisects Qwen3.6-35B-A3B Lightning MTP acceptance from **72.5% -> 34.7%**, tokens/cycle **2.48 -> 1.44**, and mean TG **116.7 -> 70.0** to the mlx-vlm upgrade in commit `a1663771`, while backbone/cycle stays **18.16 -> 18.47 ms** and prefill is unchanged. This signature points to draft/verify state or rollback divergence, reinforcing that acceptance is a correctness-sensitive state metric, not just a performance metric.
- **oMLX dev4 Flash loader compatibility is currently unstable.** #3748 reports `pipenetwork/Qwen3.8-Flash-Next-MLX-mixed-4_8bit` loading/running at ~20 TG on dev2 but failing to load on dev4 because mlx-vlm's generic custom-model loader expects `ModelConfig` that the qwen4_exp module does not define. This is a version-specific loader regression, not a Flash fit/performance conclusion; keep runtime-version pinning mandatory.
- **Distributed autotune cache identity is role-aware, not necessarily byte-identical.** vLLM #57635 refines the prior cache-sync rule: FlashInfer MoE cache keys include TP/EP rank, so broadcasting rank 0's identical cache file to every rank can itself deadlock because peers need rank-specific entries. In an 8xH100 field report, **19 consecutive restarts failed** until the cache directory was removed; then all ranks retuned in ~1 s and the engine became ready in ~20 s. Project 51 should require a complete, topology-stamped **per-rank/per-stage tuning-cache manifest**, with all ranks agreeing on cache epoch/schema/completeness; do **not** require byte-identical cache payloads when the tuning key legitimately includes rank or stage identity.
- **27B side lane — ternary/Hadamard remains worth watching:** mlx-serve commit `bbf652a589d8b7dc2d7e8299581003c14a1bf229` reports Prism Ternary-Bonsai-2-27B on M4 Max with exact 2-bit verify GEMV and MTP depth 2 reaching **73.5 TG** vs 67.9 on the earlier bf16 build, with **271 PP vs 255** on the 512/1K/2K probe set. This is M4/2-bit/short-context transfer evidence, not an M1 27B target receipt, but it strengthens the case for a separate extreme-compression verifier lane.

### 2026-09-18 16:27 UTC runtime / distributed-state additions

- **Shape-aware kernel tuning must execute against runtime shape, not a trace-time dummy shape.** vLLM #57586 shows batch-invariant persistent matmul configs keyed by an M bucket being frozen during `torch.compile` tracing at the dummy compile-time M. On RTX PRO 6000 / SM120, this made the supposedly tuned path **3-6x slower per GEMM** at small decode M. Switching batch-invariant mode to breakable CUDA graphs lets config selection happen at capture time with the real M and reduces decode-heavy latency from **1.4305 -> 0.5211 s (Qwen3-1.7B)**, **2.3578 -> 0.9797 s (4B)**, and **3.4567 -> 1.5818 s (8B)**, leaving only ~4-7% batch-invariance overhead versus BI=0 for the larger two decode cases. This is Blackwell/Qwen3 transfer evidence, not Flash/M1 evidence. Durable rule: any auto-tuned or shape-bucketed kernel path must prove the dispatch decision is made from the **runtime-effective M/N/K**, not frozen during tracing/compilation.
- **Distributed autotune state must be synchronized before any collective-dependent tuning path.** vLLM #57579 documents FlashInfer multi-rank hangs when rank 0 has an autotune cache hit while peers miss and enter tuning collectives. The proposed fix forces all ranks to load the same persisted payload (accepting both FlashInfer/vLLM filenames) or all miss together after clearing rank-local hits. No physical multi-GPU validation was posted by cutoff, so this is a mechanism/correctness rule rather than performance evidence. Project 51 dual-Mac tuning must persist a topology-stamped tuning-cache manifest before a distributed run; rank-local warm caches may not silently select different branches. Cache **schema/epoch/completeness** must agree across ranks, while payload hashes may legitimately differ when keys are rank/stage-specific.
- **A preempted recurrent-state producer must not publish an uncomputed checkpoint.** vLLM #57580 reproduces a Mamba align-mode scheduler case where priority preemption withdraws a request after only **32 computed tokens**, yet a later consumer acquires a **48-token checkpoint** because eager hash registration survives the same-step withdrawal. FCFS control computes the full 48 tokens and is valid. This is CPU scheduler metadata evidence, not model-output corruption proof, but it directly reinforces Project 51's recurrent/GDN state rule: publication/visibility of a recurrent checkpoint must be fenced to confirmed execution completion, and successful refcount/allocation is not proof that state was computed.
- **Compute-buffer reserve and speculative/draft reserve are separate memory identities.** llama.cpp #29086 (closed draft) reports a context-reserve knob freeing about **6.5 GiB** with only ~**1.5% throughput** improvement on its development model by reserving compute buffers below full context and growing later. Critically, applying the same reduced reserve to the speculative-draft context cut decode from **26.8 -> 11.9 TG**; the PR therefore deliberately kept the draft context fully reserved. Project 51 fit tuning must price target and verifier/draft reserve independently: reclaiming apparently idle reserve from the speculative side can destroy decode even when target-only execution looks neutral.

### 2026-09-18 15:03 UTC Flash/runtime additions

- **DS4 M1 throughput correction supersedes the earlier chunk-size regression claim.** A new #1056 M1 Max 64 GB re-run against current branch `04c0867` found that upstream `ds4_engine_generate_argmax` ignored the CLI `--prefill-chunk 128` for Qwen4 unless `DS4_QWEN4_PREFILL_CHUNK` was also set; the previous base-vs-PR comparison was therefore actually **8192 vs 128**, not equal-chunk A/B. With both arms explicitly pinned to the same effective chunk, chunk128 prefill is **127.5 -> 136.6 PP (+7%)**, not a ~52% regression. Durable rule: benchmark receipts must record the **effective runtime-resolved setting**, not merely the CLI argument requested.
- **Corrected exact M1 Max 64 GB Q2 resident A/B:** base `8db1d1d` -> PR `04c0867`, context 16K, chunk2048, 4-observation ABBA/BAAB cells. At 5,760 tokens ordinary prefill/decode is **274.4 -> 288.0 PP (+5%) / 24.96 -> 28.57 TG (+14%)**; MTP decode **27.24 -> 31.75 TG (+17%)** while MTP prefill is **273.5 -> 259.0 (-5.3%)**. At 17,408 tokens ordinary **271.4 -> 285.0 PP (+5%) / 23.39 -> 26.80 TG (+15%)**; MTP decode **24.76 -> 28.41 (+15%)** with MTP prefill **272.6 -> 265.9 (-2.5%)**. Decode ranges did not overlap in these cells. This materially strengthens the modern M1 low-bit runtime anchor but remains Q2 / medium-context transfer evidence, not Q5 @128K proof.
- **Chunk arithmetic remains a correctness issue even though the throughput regression was measurement error.** In the corrected #1056 study, unchunked PR and main agree bit-for-bit, but chunked prefill still differs from the unchunked reference. At 5,760 tokens the PR's chunk128 and chunk2048 results are identical to each other and each sits **0.424518 max-logit** from the unchunked reference; main differs **0.594551 at chunk2048** and **1.132671 at chunk128**. Thus the phase-dispatch fix makes chunked execution self-consistent and closer to unchunked, but a residual chunk-boundary numerical discrepancy remains open.
- **Current oMLX dev4 Flash memory regression needs version pinning.** oMLX #3738 reports M4 Max 64 GB / 0.7.0.dev4 with Qwen3.8-Flash-Next-oQ4e, 25% resident experts, MoE SSD offload and n-gram SSD offload exceeding the process guard during only a 4,096-token prefill inside a 16K context benchmark: **53.9 GB usage vs 53.2 GB hard watermark**, with model eviction. The reporter says the same behavior occurs with a GBP-DE oQ5e artifact and did not occur in dev2 (dev2 was slow). No root cause or fix exists at cutoff. Treat this as a **runtime-version regression**, not evidence that Q5/64GB is intrinsically unfit.
- **oMLX dev4 also has a 27B MTP regression report.** #3737 on M4 Max 64 GB / Qwen3.8-27B-4bit reports VLM MTP TG at 1K/4K/16K changing from **44.2/41.2/42.9 on dev1 -> 35.4/32.4/25.4 on dev4**, while acceptance/tokens-per-round remain essentially unchanged. At 16K, ANE prefill banks were released, PP fell **302 -> 239**, and one unload left ~16.45 GB active until restart. This is exact runtime-regression evidence, not a hardware target change; pin runtime SHA/version in every 27B receipt and record fast-path/bank residency.
- **Auto-calibration itself needs stability qualification.** vLLM #57569's opt-in DMA/Triton KV-load calibration produced unstable crossover picks on GB10: repeated identical 16/32/64 KiB tests selected widely different `min_n` values (e.g. 16 KiB selecting 16 through 256) because Triton medians varied by up to ~6x while DMA stayed within ~2%. Project 51 auto-tuning should require a margin/hysteresis or repeated-consensus decision and persist raw measurement spread; a one-shot threshold learner can make the system less deterministic.
- **Sparse-prefill workspace must be included before cache sizing.** vLLM #57575 identifies GLM sparse-prefill temporaries allocated after startup attention profiling: roughly **288 MiB padded query + 256 MiB output + 128 MiB compact output** for a 4096-token case. The draft fix reserves them before KV sizing but had no GPU validation by cutoff. This strengthens the existing rule that fit certification includes representative sparse-prefill transient/workspace geometry, not only model/KV residency.

### 2026-09-18 13:32 UTC Flash/runtime additions

- **RECOVERED target-quant / same-generation Apple capacity anchor:** a September 7 llama.cpp receipt for Qwen3.8-Flash-Next **Q5_K_M** on an **M1 Ultra 128 GiB** (Metal, MTP depth 2, F16 KV at native 262K, one slot, batch 512 / ubatch 128, temp 0, prompt cache off) measured **176.4 PP / 27.7 TG at 2K**, **175.8 / 31.8 at 8K**, and **100.7 / 12.3 at 261,888 input tokens**. The full-context run recovered 3/3 checkpoint codes, reported 95.5 GiB peak system wired memory, and no swap growth. The source itself labels these figures **historical Q5 performance**. Treat this primarily as a **fit/correctness/capacity receipt**, not a tuned performance anchor: the benchmark used an older llama.cpp path, shallow MTP depth 2, F16 KV, one slot, batch 512 / ubatch 128, no prompt cache, vision loaded, and the deep-context run used an external SSD with only 23 generated tokens. It does not document the modern gathered-QSA / HC-GDN / adaptive-MTP / tuned prefill stack we are targeting.
- **Do not use the historical M1 Ultra Q5 receipt as a tuned-speed counterweight.** It still proves that the target quant fits and functions at native context on M1-generation Apple silicon, but its runtime/recipe is too baseline-oriented to lower the modern dual-M1 forecast by itself. The 40@128K thesis must still be justified from modern gathered/selected QSA, GDN/HC kernels, MTP verification economics, stage-local state and PP2 overlap—not from aggregate bandwidth arithmetic alone.
- **NEW chunk-invariance correctness evidence:** DS4 #1056 commit/comment `2d6a207` separates prefill projection policy from decode/batch policy. On M1 Max 32 GiB Q2 SSD-streaming, prior optimized paths produced max logit drift versus the reference of up to **0.4873 after prefill and 1.3767 during decode**. After phase-correct dispatch, measured prefill max error is about **1-2e-6** and worst 16-step decode error **3.2e-4 to 8.3e-4** across five fixtures; **85 frontiers / 21,107,200 logit pairs** were checked. For the 5,760-token fixture, chunk 128 and chunk 2048 become bit-identical across all 17 measured frontiers. Project 51 must test chunk-size invariance at logit/state level, not final text only.
- **NEW M5 prefill-fusion receipt:** mlx-serve #438 post-merge measurements on M5 Max 128 GB / Flash-Next mixed-4/8, MTP/PLD off, prefix cache off, prefill chunk 8192: HC+GDN fusions measure **1488 -> 1618 PP (+8.7%) at ~16.4K** and **1628 -> 1850 (+13.6%) at ~32.8K**. Fusion-ON stays at **1873 PP around 65.5K** and **1858 PP around 131K**; decode remains 51-55 TG in both arms. #460 records a further combined, non-isolated 64,947-token prefill change **2163.9 -> 2323.4 PP** for several still-unseparated paths. This strengthens long-context prefill architecture headroom but is stronger-chip/non-Q5 transfer evidence.
- **NEW async chunked-prefill correctness gate:** vLLM #57562 shows a Qwen3.6 hybrid GDN model with async scheduling returning sampled tokens while a request is still mid-prefill under concurrent multi-chunk traffic. In a 12-request load there were **44 placeholder underflows**; ~143K prompts produced ~14 occurrences, ~42K produced 4-5, ~9K produced 1, and single-chunk prompts produced 0. Prefix-cache disable does not fix it; disabling async scheduling completes **24/24** with no underflow and reported throughput cost below the test's noise floor. Project 51 must assert that incomplete prefill rows cannot emit/commit decode tokens under mixed-length concurrency, even with speculation disabled.
- **NEW memory-guard distinction:** oMLX #3732 fixes a path where a moving dynamic memory ceiling could abort concurrent long prefills while several GiB of MLX Metal buffers were still reclaimable. Emergency abort uses the stable physical/Metal cap; dynamic ceiling remains an admission/pressure signal, and soft pressure requests pooled-buffer reclamation first. No live large-model A/B exists yet, so this is a correctness/lifecycle rule rather than performance evidence.
- **Backend-specific overlap thresholds remain hardware identity.** DS4 #1083 on DGX Spark/DeepSeek V4.1 Q2 SSD streaming overlaps resident expert compute with miss reads and reports repeated **~6.9-8.0% decode gains vs current base** (older comparisons 6.5-12.3%), byte-identical output. A Metal-inspired threshold reduced the CUDA gain to ~4%, demonstrating that overlap admission thresholds must be backend-measured rather than copied across Metal/CUDA. This is transfer evidence only for Flash's offload scheduler.

### 2026-09-18 09:21 UTC Flash/runtime additions

- **Exact M1 Max 64 GB DS4 Q2 calibration strengthened.** DS4 #1068 records `Qwen3.8-Flash-Next-Q2.gguf` on an M1 Max 64 GB, Metal, 41.72 GiB resident with n-grams disk-only. Main at `8db1d1d` measures roughly **24.15-24.46 TG** from 2K through 16K and **~275 PP**, with an ordinary 32,113-token prompt at **271.94 PP / 22.76 TG**. Built-in MTP reaches **33.19 TG** on highly predictable output and **28.91 TG** on prose. This remains Q2, not the canonical Q5 lane.
- A later corrected #1056/#1068 M1 Max 64 GB resident A/B supersedes the first comment: with the effective prefill chunk pinned identically, 5,760-token ordinary decode is **24.96 -> 28.57 TG** and MTP **27.24 -> 31.75 TG**; at 17,408 ordinary **23.39 -> 26.80** and MTP **24.76 -> 28.41**. Ordinary prefill improves about **+5%** at both real-prompt cells. This strengthens M1-generation headroom but remains Q2/medium-context transfer evidence.
- **SUPERSEDED measurement:** the earlier apparent resident-prefill regression at chunk128 (**282 -> 136 PP**) was later traced to a benchmark configuration mismatch: base ignored the CLI chunk flag and actually used 8192 while the PR used 128. With effective chunk128 pinned in both arms, the PR is faster (**127.5 -> 136.6 PP**). Chunk width still matters to absolute throughput and numerical state, so it remains benchmark identity, but this specific regression claim is retracted.
- **PLE offload should use split-phase async start/finalize when possible.** vLLM #57497 on one MI300X with Qwen3.8-Flash-Next-FP8 keeps the ~51 GiB PLE table in pinned host memory, reports bit-identical top-8 logprobs versus device-resident PLE, exact needles at 105K and 209K, and cuts 16K TTFT from **3.5 s synchronous -> 1.9 s async** while decode remains ~**77-84 TG**. This is non-Apple evidence, but strongly supports launching the next PLE gather early and joining only at consumption.
- **Sparse-table offload can be capacity-positive without a decode tax when prefetch fully hides it.** vLLM #57491 moves DeepSeek-V4.1 Engram tables off MI355X VRAM. TP4 KV capacity rises **4.325M -> 6.195M tokens (+43.2%)** while 4096-in/512-out C8 serving stays statistically flat at ~**620.6 output tok/s** and mean TPOT ~**11.35 ms**. This is DeepSeek/ROCm transfer evidence, not a Flash target receipt.
- **Scheduler admission latency is separate from model PP.** oMLX #3726 fixed a case where an already-cache-hit classifier request with only 1,161 tokens left to prefill waited about 50 s behind decode/chunked-prefill debt. In a Qwen3.5 9B controlled test, first-token latency changed **8.86 -> 0.73 s** with Lightning MTP off and **7.28 -> 1.16 s** with it. Project 51 interactive qualification must record queue/admission-to-first-prefill delay separately from PP and TTFT.
- **Cross-request determinism must be tested even with prefix caching disabled.** vLLM #57493 shows ROCm paged attention on gfx1151 returning four distinct decode-step logprobs and two greedy completions for the same probe after varying filler requests, with max_num_seqs=1, eager mode and prefix cache off; Triton attention is 20/20 identical. Project 51 must run fixed greedy/logprob probes after variable filler traffic and after allocator/cache churn to detect stale scratch or hidden kernel state, not only explicit prefix-cache corruption.

### 2026-09-18 recovered exact M1 long-context Flash anchor

- **Single M1 Max 64 GB / llama.cpp Metal / Flash-Next low-bit physical receipt:** a community PLE-last GGUF repack of the full model reports Q2_K_XL at about **21 tok/s decode and ~200 tok/s prefill**, with **128K context at the same ~21 tok/s decode rate**; a separate MTP sidecar reaches about **24 tok/s on code**. The ~27 GiB PLE/n-gram table stays mmap/SSD-backed and wired use is reported around **44-48 GB**. This is exact M1-generation hardware and exact model family, but **not the canonical Q5 target lane**: Q2/IQ1 weight precision materially changes bandwidth/quality economics. Treat it as a silicon/runtime/offload anchor, not a direct Q5 forecast.
- The same source's small quality checks (GSM8K 40 items, HumanEval 20 items, perplexity) are useful smoke evidence only and do not promote Q2/IQ1 into the production quality lane.
- **Nominal quant label is insufficient topology identity.** Public M5 Max oQ5e artifacts span materially different long-context outcomes (for example ~25.8 TG at 131K on one oQ5e card versus the previously recorded 47.3 TG at 128K on another). Record artifact/revision, sensitivity/imatrix provenance, oMLX/runtime version, MTP state, KV quant, PLE/offload policy, sampling/thinking state, and fast-path eligibility before comparing “Q5” numbers.
- **Sparse-cache physical stride is semantic state.** vLLM #57477 showed a GLM sparse-indexer tail seed writing with a dense stride into a padded shared pool, silently corrupting unrelated prefix-cached indexer pages. Project 51 cache qualification must assert logical block id -> physical stride/offset mapping and verify that unrelated requests cannot mutate hot cached-prefix pages.

### 2026-09-18 durable Flash lane / runtime corrections

- **Canonical Flash quant identity is Q5-class / eventual ~5.x BPW.** Do not describe Q6/Q8 as the preferred Flash-Next lane. oQ4e is a speed/quality comparator; Q6/Q8 remains relevant only where separately named (for example smaller 27B lanes/verifier work).
- Recovered exact stronger-Apple target-lane receipt: M5 Max 128 GB / oMLX 0.7.0.dev2 / Qwen3.8-Flash-Next-Uncensored-oQ5e, MTP/DFlash/spec-prefill/ANE/TurboQuant disabled, measured **47.3 TG / 1,203 PP at 128K** and **47.4 TG / 1,236 PP at 200K**. This raises architecture confidence but is not dual-M1/TB4 evidence.
- A transient optimized-path exception must not become a silent process-lifetime performance mode. oMLX commit `9052b3952d1af3258fe85939b4fefbcc6c6c3e28` fixed a Qwen4 hyper-connection path where one exception permanently disabled fused optimization for every later Qwen4 call in the process. Long-session qualification must record optimization eligibility/fallback state and verify recovery after a one-shot injected failure.
- Shared MTP verify must keep row-local boundary work row-local. oMLX #3724 showed that a one-row paged-boundary forward on the whole batch cache could broadcast a KV write across rows and collapse GDN state. Boundary emits/rollback/replay that are semantically per-row must use extracted private row state and explicit merge-back; cache padding identity must be refreshed after ragged finalize when the model caches metadata by array identity.

## Long-context QSA evidence

### llama.cpp #28213 — gathered selected-K/V decode

Source: https://github.com/ggml-org/llama.cpp/pull/28213

Dual A6000, IQ4_XS, q8 KV, temp 0:

- 31K: 36.5 -> 38.5 tok/s (+6%)
- 62K: 26.5 -> 31.6 tok/s (+19%)
- 130K: 15.7 -> 23.6 tok/s (+50%)

At 130K it also removes roughly 17 MB of attention-mask upload per token. Not Apple
evidence, but strong architecture evidence that selected-KV gather is the correct long-context
shape.

### oMLX #3320 — direct-QSA wide-MTP evidence is under requalification

Source: https://github.com/jundot/omlx/pull/3320

A later low-margin workload exposed a parity failure in the prior fast wide-verifier evidence.
The PR remains draft until exact 10K-220K output-hash/cache-state/selector/prefill/decode gates
are refreshed. Preserve the architecture signal, but do not overweight its most aggressive
throughput numbers until requalified.

### oMLX #3355 + #3351 — merged long-context gathered-prefill serving stack

Sources:
- https://github.com/jundot/omlx/pull/3355
- https://github.com/jundot/omlx/pull/3351

#3355 preserves gathered text prefill through mRoPE rebinds. Physical M3 Ultra evidence:

- 19,992 uncached tokens: 892.56 tok/s
- 219,994 uncached tokens: 885.27 tok/s overall
- pure-model windows: 944.69 tok/s at 0-8K -> 851.68 at 213-220K
- exact cached repeat: 19,991/19,992 tokens reused, 0.15 s model TTFT, identical output hash

#3351 fixes gathered-QSA memory admission. A real 233,472-token cached prefix + 5,244-token
continuation had been falsely rejected because a stale dense transient predicted 90.45 GB.
Representative Q=4096 / KV=233,472 gathered static pricing is ~4.04 GB versus 46.41 GB dense,
while image paths remain dense and recurrent fixed state is still charged.

Durable conclusion: long-agent continuation/prefill robustness has improved materially, but
this does not directly raise M1 decode forecasts.

## Flash-Next continuous batching — corrected current state

### MERGED foundation #3246 — mixed-length continuous batching works

Source: https://github.com/jundot/omlx/pull/3246

Merged 2026-08-29. It fixed the actual qwen4_exp continuous-batching join chain:

- honor model-owned `to_batch()` for warm QSA singleton joins;
- aligned scalar `past_len` for ragged QSA batches;
- skip singleton MTP fold on mid-cycle joins;
- slice BatchQSAKVCache indexer arrays during trim.

Physical M3 Ultra validation ran a 14K request decoding 500 tokens while four short requests
joined mid-flight and completed. Residual corruption/recovery events were eliminated, with
reported join latency dropping from up to ~13 s to ~2 s.

### CORRECTION — #3368 was superseded, not a new prerequisite

Source: https://github.com/jundot/omlx/pull/3368

The maintainer closed it without merge because #3246 already handled the production ragged
QSA offset/indexer path. The proposed tests passed unchanged on main because they exercised a
local mask copy rather than the production method. Do not cite #3368 as evidence that current
main lacked fundamental per-row QSA safety.

### MERGED #3369 — remaining BatchQSAKVCache join hardening

Source: https://github.com/jundot/omlx/pull/3369

Merged 2026-09-02 as `2246290a1000ef50317151868b20537dd7e0e4c2`. It promotes mixed text/MRoPE
position ranks correctly and separates actual indexer length from KV offset during joins.

### OPEN #3334 — compiled multi-row decode reduces host dispatch, not yet E2E

Source: https://github.com/jundot/omlx/pull/3334

M3 Ultra / Qwen3.8-Flash-Next oQ4e, B4:

- host dispatch 8.8 -> 2.0 ms (-77%)
- pure decode step 54.5 -> 44.4 ms (-18%)
- bit-exact controlled path at 2K and 16K

Repeated HTTP B1/B2/B4/B8 A/Bs were only 0.93-1.02x versus control, so the PR explicitly
makes no E2E speedup claim. Compiled batching remains a credible host-overhead seam, not a
forecasted multiplier.

### RECOVERED #3265 — batched depth-1 MTP is silicon/economics sensitive

Source: https://github.com/jundot/omlx/pull/3265

M3 Ultra report:

- batched acceptance ~56% vs ~61% single-stream
- four concurrent requests roughly +70-90% aggregate vs plain batching in the reported setup

Independent M1 Ultra result, directly relevant to M1-generation economics:

- B8, 580 cycles
- acceptance 52.4%, zero fallbacks
- batched MTP 38.50 / 36.03 tok/s
- plain-batched baseline 57.09 tok/s
- draft-head work ~12,226 ms vs verifier ~10,196 ms

The draft head cost approximately as much as verification, so MTP was net-negative despite
reasonable acceptance. Do not make MTP mandatory under concurrency on M1 Max.

### NEW CAUTION #3370 — temp>0 may collapse current Lightning-MTP acceptance

Source: https://github.com/jundot/omlx/issues/3370

Unconfirmed user report on M3 Ultra / Qwen3.8-Flash-Next-oQ8-MTP:

- temp=0: 295/295 accepted, 3.88 tok/cycle, ~70.7 tok/s
- temp=0.3: 0/387 accepted, 1.01 tok/cycle, ~21 tok/s
- temp=0.7: 0/311 accepted, 1.01 tok/cycle, ~21 tok/s

The reporter suspects exact-match/greedy-only acceptance rather than proper stochastic
rejection sampling, but there is no maintainer confirmation. Treat as a benchmark requirement:
measure temp=0 and the actual agent sampling configuration separately.

## SSD-backed PLE evidence

### NEW #3372 — batch sharded PLE embedding gather

Source: https://github.com/jundot/omlx/pull/3372

The old SSD-backed PLE path called `.tolist()` on IDs and then performed per-ID shard scans,
forcing a GPU/host synchronization and serializing many tiny mmap faults. The new path buckets
IDs by shard, warms them with threaded pread, dequantizes once, and keeps a bounded hot-row LRU.

M5 Max 128 GB, 92K warm prefix, 600 generated tokens, paired/interleaved:

- 35.42 -> 37.32 tok/s
- +1.90 tok/s / +5.4%
- reported 95% CI [+0.13, +3.78] tok/s

Do not transfer the M5 percentage directly to M1. The portable lesson is that if M1 requires
SSD-backed PLE, host readback + row-at-a-time shard faults should be removed before distributed
tuning.

## Distributed concurrency evidence

### oMLX Cluster v2 #3118 — stronger-hardware architecture calibration

Source: https://github.com/jundot/omlx/pull/3118

Physical pair: M3 Ultra 256 GB + M5 Max 128 GB / TB5 JACCL-RDMA, ~6.1-6.5 GB/s and
27-31 us. Absolute numbers are not transferrable to M1/TB4.

DeepSeek-V4 TP2 evidence:

- cold prefill ~732.49 tok/s @30K, ~684.66 @100K
- non-MTP B1 decode ~29-31 tok/s
- non-MTP aggregate B1/B2/B4 ~31.22 / 47.35 / 75.22 tok/s
- fixed-depth-5 high-acceptance MTP ~79.8-80.6 tok/s raw

Most transferable result: until true N x M speculative verification exists, the final policy
caps the MTP lane to one and arbitrates concurrent work around it. Cached B1/B2/B4 aggregate
wall rates are ~75.1 / 75.2 / 73.1 tok/s. The PR explicitly calls this serialized throughput
arbitration, not simultaneous batched-MTP scaling.

Qwen3.8-27B Phase-split evidence in the same branch:

- 9,410-token cold prefill compute ~991.36 tok/s
- decode ~29.59 tok/s
- cache handoff 7.34 GB/s
- exact-prefix wall 12.31 s -> 1.40 s
- B4 queued throughput ~1.29x sequential stage time

Single-node donor-head Lightning MTP works, but Qwen TP2 MTP physically stalled at the first
`return_hidden`/rollback graph and was reverted/fail-closed. Distributed target execution and
distributed speculative lifecycle are separate qualification problems.

### DS4 #861 — distributed batched-serving L0

Source: https://github.com/antirez/ds4/pull/861

Known Strix-Halo topology: layer-split pipeline ~222 tok/s average prefill / 260 peak and
13.6 tok/s decode, while TP is link/RTT-heavy. Current distributed multi-session serving
shares a worker registry and multiplexes session/request IDs, but decode remains serialized and
coalescing/mixed-prefill are disabled until row-batched spans land.

## M1 Max 27B ordinary-batching feasibility anchors

Recovered oMLX benchmark records show useful but configuration-sensitive M1 Max target-batch
headroom. Example B1/B2/B4 rows:

- 18.9 / 22.0 / 44.9 tok/s
- 18.1 / 31.0 / 63.8 tok/s
- 16.2 / 26.4 / 45.1 tok/s
- 15.5 / 31.9 / 61.7 tok/s

Another M1 Max 64 GB record showed only ~19.0 / 22.3 / 23.7. Durable conclusion: ordinary
multi-row execution can scale significantly on M1 Max, but the multiplier is runtime/model/
configuration sensitive. These 27B records are not direct Flash-Next proof.

## Qwen3.8-27B external exact frontier

Layr challenge remains unchanged as of this consolidation:

- best score `3.7291100105909`
- #1481 newest visible submission
- no newer promoted exact result

No external result changes P69B13 selection.

## Current dual-M1 Flash-Next planning ladder

These are engineering planning probabilities, not statistical confidence intervals. Assumptions:
mature 2x M1 Max 64 GB / TB4, short-to-medium B1 coding/agent workload, best single-node
kernels first, recurrent state kept local, and PP overlap used where it actually pays.

### B1 short/medium context — unchanged

| Mature B1 target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

### B1 around 128K — unchanged

| Mature B1 target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate — unchanged from midnight trim

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

**Rationale correction:** plain Flash-Next continuous-batching correctness is stronger than the
midnight note stated because #3246 had already landed and #3369 has now merged. We retain the
aggregate trim because the direct M1-generation batched-MTP result remains negative, #3334 has
no E2E gain yet, and there is still no direct M1-Max Flash-Next B2/B4 throughput receipt.

Concurrency remains a scheduler/topology optimization, not an automatic MTP multiplier.

## Current topology / serving decision

- **PP2 remains primary** for the dual-M1 Flash-Next experiment.
- **TP2 remains a falsification/control benchmark.**
- Prove single-M1 and PP2 target-only correctness/performance first.
- Benchmark B2/B4 plain target batching separately from MTP.
- Under load, choose the best measured policy among:
  1. plain multi-row target batching;
  2. singleton profitable MTP lane plus queued/arbitrated independent work;
  3. batched depth-1 MTP;
  4. context/acceptance/sampling-driven dynamic MTP disable.

Do not assume "MTP everywhere" is optimal on M1 Max.

## Bring-up invariants / highest-value missing measurements

- internal NVMe for long-lived model/vocab mappings
- explicit TB4 TSO check
- background-memory audit
- deep-context needle/correctness before speed
- single-M1 target-only + MTP baselines first
- MTP at temp=0 **and** intended agent sampling
- current-main single-M1 B2/B4 plain batching
- SSD-PLE gather A/B if PLE is offloaded
- PP2 target-only before PP2+MTP
- B1/B2/B4/B6 ladder
- stage-local recurrent/GDN rollback state
- separate resident-session count from active decode
- record acceptance, committed tokens/cycle, stage idle %, and actual TB4 bytes/round

Highest-value missing measurements:

1. exact Flash-Next 2x M1 Max/TB4 target-only B1 TG;
2. exact Flash-Next 2x M1 Max/TB4 MTP B1 TG;
3. single-M1 Flash-Next B2/B4 plain batching on current main after #3246/#3369/#3355;
4. M1 Max plain batching vs singleton-MTP-lane vs batched-depth-1 MTP;
5. M1 Max MTP temp=0 vs realistic agent sampling acceptance/economics;
6. PP2 B2/B4 aggregate with stage-idle % and actual TB4 traffic.
