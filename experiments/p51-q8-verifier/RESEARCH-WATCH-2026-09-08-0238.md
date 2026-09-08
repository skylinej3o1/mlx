# External runtime research watch — 2026-09-08 02:38 ET

Starting freshness boundary: `11996bac754e4818f702b75bd1a060ff010df022` / **2026-09-08 02:04:05 UTC**.

Classification: **material Flash-prefill / speculative-state ownership / distributed-lifecycle / QSA-benchmark update; no performance target movement.**

`RESEARCH-TARGETS.md` is intentionally unchanged. No fresh sustained exact-target receipt surfaced for dual-M1 Flash-Next, dual-M1 DS4-0731, single-M1-Max64 Qwen3.8-27B, RTX 5070 Ti Qwen3.8-27B or RTX 5070 Ti Tiel Coder.

This pass is valuable because it adds one genuinely new Flash-Next Metal prefill A/B and several high-leverage correctness constraints that map directly onto the planned PP2 appliance. The portable lessons are **quant/layout-specific chunk tuning, explicit ownership for every cross-turn speculative buffer, synchronized distributed cancellation/cache transitions, context-qualified QSA selection-width provenance and quant-layout-aware speculative hook qualification**. None is an exact M1/TB4 receipt.

---

# FRESH / material measured A/B

## antirez/ds4 #991 / `a30ed072fc9dc77eeba65a4c4d1a6984cc44be74` — Q4_K routed-expert double buffering and chunk-width sensitivity

Fresh commit: **2026-09-08 06:24:33 UTC**.

Exact source rig / model regime reported by the benchmark note:

- **Apple M5 Max, 137 GB**;
- Metal 4 tensor API enabled;
- Qwen3.8 Flash-Next / qwen4exp;
- Q4 case: `Q4KImatrix-MTP`;
- Q2 case: `IQ2XXSImatrix-Q2KDownPad768-MTP`;
- measurements at a **16,384-token frontier**;
- decode unchanged by construction; this is a prefill-path experiment.

### Mechanism

A new `kernel_mul_mm_id_mpp_dbuf` routed `mm_id` kernel stages the next K-step's Q4_K weights and activations into alternate threadgroup buffers while the current cooperative matmul runs. The stated goal is to pay one barrier per K-step instead of two.

Important boundaries:

- only the Q4_K gate/up and down routed-expert instantiations use the double-buffered path;
- IQ2_XXS / Q2_K / MXFP4 / cached paths retain the original single-buffered path because their dequantization work already hides staging latency or measured neutral-to-negative;
- affected threadgroup allocation rises **8192 -> 12288 bytes**;
- accumulation remains f32 and operand domains are unchanged;
- an explicit kill switch restores the simdgroup path.

### Q4 controlled result

At `--prefill-chunk 4096`, the report's selected warm interleaved-pair analysis gives a headline **~+3.8% mean Q4 prefill improvement** after identifying cold-page/model-switch and heat-soak contamination. An isolation arm using Q4_K MPP with the old single-buffered staging measured about **-0.9%**, supporting the conclusion that **double-buffered staging**, not merely switching to TensorOps, is the active ingredient.

The raw table contains a flagged contaminated pair, so preserve the report's contamination handling rather than simplifying this to an unqualified all-runs-positive claim.

Q2 is unchanged by construction and measured approximately neutral, which is useful negative evidence: the optimization is **quant/dequant-path specific**.

### Chunk-width sweep — higher leverage than the kernel percentage

At the same 16K frontier:

| chunk | Q2 prefill | Q4 prefill |
|---:|---:|---:|
| 1024 | 790, 488 | 466, 445 |
| 4096 | 1025, 995 | 970, 1005 |
| 8192 | 1059, 1069 | 535, 539 |

The report summarizes:

- Q2 fastest at **8192-token chunks**, ~1064 tok/s, about **+35%** over its 1024-token convention;
- Q4 fastest at **4096-token chunks**, ~1000 tok/s, roughly **2.2x** its 1024-token result;
- Q4 **regresses sharply at 8192** (~537 tok/s) and that regression was not yet investigated.

### Evidence class

**Measured M5-Max experimental A/B / mechanism-transfer evidence only.** It is neither M1 Max nor PP2/TB4, and none of the numeric gains transfer to the target cluster.

### Promotion for dual-M1 Flash prefill

This materially changes the experiment order:

1. **Chunk width becomes an explicit per-quant/per-kernel sweep**, not one global serving constant.
2. Sweep chunk width before judging a routed-expert kernel: a bad chunk can dwarf a percent-level kernel gain.
3. For PP2, choose chunk width jointly with **stage balance and TB4 bubble/traffic behavior**, not from one stage in isolation.
4. Record quant format, routed-expert implementation, RHS dtype, threadgroup scratch and realized chunk width as benchmark provenance.
5. Double-buffered staging is promoted only if M1 profiling shows the same barrier/staging bottleneck and scratch does not reduce occupancy or admission headroom.
6. Keep negative controls: TensorOps alone, old staging, and quant formats where dequantization already hides load latency.
7. A local-stage prefill win promotes only after exact recurrent/frontier identity and cluster cold-PP A/B.

This complements rather than replaces the 19:19 block-history GDN / repeated-work candidate. The two mechanisms attack different parts of prefill.

---

# FRESH / material speculative-state correctness

## Avarok-Cybersecurity/atlas #968 — cross-turn MTP carry was model-global without sufficient request ownership

Fresh PR created **2026-09-08 04:47:10 UTC**.

This is unusually relevant transfer evidence because it independently rediscovers the same class of ownership failure our 15:10 / 23:33 chain is designed to exclude.

### D1 — one model-level carry slot had no enforced request identity

The implementation had one `mtp_carry` slot for the whole engine. Whichever sequence finished last deposited the carry; whichever proposed next could adopt it. Comments described the state as same-session-only, but the actual admission check was only a short common-prefix condition.

The patch adds an explicit session stamp and refuses unstamped/foreign sessions rather than relying on prose or common-template prefixes.

Important nuance: the reported `session_hash` is a hash of the first <=1024 prompt tokens, not a client identity. Requests sharing that full prefix can still match. The author argues this is semantically sound for retained rows bounded by the common prefix because the hidden row is a pure function of that prefix. We should preserve that distinction instead of treating "session hash" as a universal request ID.

### D2 — the shared hidden-row interval proved coverage, not provenance

A model-level `mtp_prefill_hidden` buffer plus an integer row interval could say that rows `[a,b)` existed without saying **which request/generation wrote them**. A foreign write could therefore extend/take over the interval, and a later append plan could pair this request's tokens with another request's hidden rows.

The patch stamps the interval with a generation/owner ticket. A foreign write takes ownership instead of merging ranges; a foreign read sees no usable interval.

The negative-control tests are important because either half of the bug in isolation looks harmless. The failure appears in the composed write-then-read order.

### D3 — configured state was reported as armed when runtime gates made it inert

The startup line reported carry `ON` from environment/configuration even though the actual runtime gate disables carry whenever multi-sequence mode is active; that cap reportedly defaults to 32. The feature could therefore be logged as enabled while being unreachable.

The patch introduces one shared `carry_armed` predicate for both dispatch and reporting.

### Verification / remaining boundary

The PR reports red/green tests for foreign session adoption, unstamped requests, shared-template-prefix non-identity, inert-vs-armed reporting, foreign interval takeover and append-plan rejection; `spark-model` library tests report **671 passed** with clippy/check clean.

Crucially, the author explicitly says the fix **does not prove device ordering**: a host-side ownership stamp does not establish the happens-before relation between device capture/copy and later catch-up reads. That remains a separate synchronization contract.

### Evidence class / promotion

This is **cross-runtime correctness/mechanism evidence**, not Apple target performance evidence.

Promote these standing requirements:

- every persistent or cross-turn speculative buffer has an explicit **owner identity plus generation/epoch**, not merely a valid index range;
- coverage and provenance are separate predicates;
- a single model-global carry slot is never assumed request-safe because concurrency is currently low;
- common prompt/template prefixes are not request identity unless the reused state is mathematically proven to depend only on that exact prefix;
- configured/enabled and **actually armed/executed** states are reported separately;
- host ownership metadata and device happens-before are separate certification surfaces;
- composed cross-request write/read negative controls are mandatory because unit tests of each half can miss the bug.

For our B2/B3/B4 gate, this strengthens the existing rule: every concurrently scheduled request owns its persistent recurrent/draft/carry state, and the ownership stamp must survive slot reuse/cancellation/restart without aliasing.

---

# FRESH / material distributed lifecycle integration

## oMLX #3258 — distributed request safety review found missing cancellation, cache-maintenance and cache-agreement wiring

Fresh restack/review/repair sequence after the cutoff:

- restacked status: **2026-09-08 05:11:12 UTC**;
- maintainer consolidated review: **05:16:22 UTC**;
- integration restoration report: **06:08:59 UTC**, commit `fd547df8` referenced by the contributor.

The key value is not that a distributed PR exists; it is that a maintainer review found several lifecycle pieces missing from a split that otherwise looked substantially complete.

### Missing surfaces reproduced / called out by review

- cancellation state initialization and vote completion;
- batch drain/arm methods and control-channel operations;
- watchdog `scope=all` cancellation entering the synchronized generation path instead of mutating rank-zero state from a heartbeat thread;
- terminal completion signals for cancelled request response queues;
- plan-scoped cancellation acknowledgements and stale-cancel handling;
- a reproduced stale `scope=all` marker contaminating a later targeted cancel;
- registration/clearing of live prompt caches and SSD stores;
- unloaded local/remote cache clearing using **each peer's own paths**, not coordinator filesystem paths;
- request-ID propagation through `/v1/completions`;
- prompt-cache agreement after lookup plus authenticated control operations.

### Reported restoration ordering

The follow-up says cancellation now:

1. initializes/validates the cancel-vote epoch;
2. completes shared votes across control/fallback paths;
3. drains Metal work;
4. performs an authenticated rank barrier;
5. arms the exact epoch/UID set;
6. only then permits batch removal.

It also scopes cancel files/acks by plan and worker lifetime, treats startup files as watermarks, and prevents acknowledged/stale all-request markers from being merged into a later targeted request cancellation.

Prompt-cache agreement is invoked after memory/SSD lookup using an authenticated owned-bytes broadcast; live and cold cache cleanup are wired across local/remote peers.

Focused validation after restoration reports **335 passed, 3 skipped**. The contributor reports no original two-Mac hardware rerun; therefore this is **integration correctness evidence, not a distributed performance or exact-topology receipt**.

### Promotion for PP2

Distributed cancellation/cache maintenance are state-machine transitions, not admin side effects:

- cancellation has a request/plan identity, epoch and explicit rank agreement;
- no rank may unilaterally remove distributed request state before the synchronization frontier is complete;
- Metal/device work is drained or fenced before ownership is released/reused;
- cancelled streams receive an explicit terminal event so client lifecycle cannot hang;
- stale cancel markers are worker-lifetime scoped and cannot poison future requests;
- cache maintenance resolves peer-local paths/config on the peer;
- prompt-cache hits are accepted only after **cross-stage agreement on the owned bytes/boundary**;
- transport request IDs propagate through both streaming and non-streaming distributed paths.

Add cancellation-during-prefill, cancellation-during-decode, slot reuse after cancellation, cache clear while loaded/unloaded, peer restart and stale-control-file negative cells to PP2 certification.

---

# FRESH / material benchmark-methodology evidence

## llama.cpp #28591 — QSA/indexer `top_k` is a depth-sensitive benchmark dimension

Fresh draft PR created **2026-09-08 04:11:30 UTC**.

The code change itself is small: add model-metadata overrides to `llama-bench`. The reason is directly relevant to Flash-Next. `qwen4exp.attention.indexer.top_k` was otherwise awkward to sweep in the normal pp/tg benchmark harness even though it materially affects prefill.

The PR reports that, on **Vulkan**, changing Qwen3.8-Flash-Next indexer `top_k` from 2048 to 1024 changes prefill cost increasingly with depth:

- about **8% at ~29K prompt tokens**;
- about **25% at ~120K prompt tokens**.

A branch smoke on **Strix Halo gfx1151 / RADV**, Qwen3.8-Flash-Next UD-Q4_K_XL, verifies the override is actually applied; the short `pp64` / `tg16` smoke is only a wiring check, not a target throughput ruler.

### Evidence class / promotion

This is **cross-hardware benchmark-methodology / mechanism evidence**.

QSA selection width is not merely a runtime knob:

- it changes compute with context depth;
- it can change the selected set / approximation, so performance and semantic quality must be certified together;
- short-context pp results cannot establish long-context economics.

Promotion:

1. record actual QSA/indexer `top_k` / budget as benchmark provenance;
2. sweep it at realistic depth points, including the ~128K target ladder rather than only short pp;
3. pair every speed arm with deterministic selected-set/tie handling and quality/retrieval checks;
4. do not compare engines/runs whose hidden model-metadata overrides differ;
5. prefer harnesses that print the **realized metadata value**, not just requested CLI state.

This strengthens the existing rule that a benchmark cell is defined by what actually executed.

---

# FRESH / bounded Apple correctness evidence

## oMLX #3515 — Qwen3.8-27B ParoQuant DFlash2 requires quant-layout-aware target ops / rollback hooks

Fresh PR created **2026-09-08 06:34:41 UTC**; head `165f423faa8e77ed14541006e0a43e5e79d812a9`.

Scope is deliberately narrow: dense Qwen3.8-27B ParoQuant, 64 layers, hidden size 5120, vocab 248320, 4-bit/group-128/krot-8. The generic MLX loader cannot interpret this checkpoint's packed weights/rotations, so the target must route through its ParoQuant-aware loader and the existing Qwen hybrid-attention speculative adapter.

### High-value ablation

The useful mechanism result is not a speed claim. On a small fixture with real nonzero ParoQuant rotations, **suppressing all speculative-hook installation changed the next-token argmax after partial rejection**, with reported max logit error 0.65346. Explicit hook installation and the normal cache-created installation path preserved argmax, with a rerun reporting max logit difference ~8.34e-7.

This shows that "the model loads" and "target/draft dimensions match" are insufficient. The realized quantized module classes must participate in the hidden-capture / recurrent-attention rollback protocol.

### Reported bounded validation

- 310 related tests passed on the final PR branch;
- earlier full-model work on **M3 Max** reported no missing/extra/mismatched sanitized text tensors and forward-logit agreement;
- nine 64-token greedy comparisons matched exactly at DFlash block sizes 3, 5 and 8;
- 16 forced-rejection cases preserved next-token argmax;
- actual engine checks covered cold/warm 4K, 16K and 32K requests, complete prefix reuse, seeded sampling, cancellation recovery and unload/reload.

The PR explicitly makes **no controlled serving-performance claim**; the full-model checks were performed before the final upstream refresh. Treat this as bounded correctness/integration evidence only.

### Promotion

- target/draft compatibility includes quantization layout and **real module-class behavior**, not just hidden/vocab/layer dimensions;
- benchmark provenance records whether speculative hooks/rewrite paths were actually installed and which modules they covered;
- unsupported quantized module types fail closed rather than silently using a partial speculative path;
- forced-rejection rollback is part of quantized-target qualification;
- unload/reload must re-arm any class/runtime hooks without leaking prior model state.

For P69, this is external mechanism evidence only: **P69B12 stays frozen/promoted and P69B13 remains next from existing profiling only.**

---

# UPDATE / screened non-promotions

## vLLM #55557 — Qwen4Exp QSA main-KV fp8 work continues, but no fresh target-rig claim

The PR's headline measurements — larger KV pool, long-context needle checks and bf16-vs-fp8 prompt-logprob comparisons — were already present before this pass's starting boundary and are therefore **KNOWN/BACKFILL**, not newly promoted evidence.

Fresh post-cutoff review commits include:

- `2bff9a56c7f9cd8c065954b7a2cba8047455a163` at 04:49 UTC, correcting how fp8 V scaling is combined with the split-K normalizer;
- `7150f470c0de8b646142f7a408455980f8bce3f3` at 06:22 UTC, removing an unnecessary giant fp32 test temporary that tripped allocator assertions in large fp8 cases.

Useful consequence: low-precision QSA cache work still needs exact reference/normalizer semantics and realistic-memory test construction. No Apple or RTX5070 target movement follows.

## oMLX #3508 — cache key identity warning from a VLM feature-cache failure

Fresh Gemma-4 issue, not a target-lane receipt. Per-image vision features were keyed by image hash even though their soft-token geometry could differ with aspect ratio/request composition; combining individually cached entries with incompatible sequence lengths caused a 500 before the downstream validity check could run.

Portable lesson only: **content identity is not sufficient cache identity when the materialized representation depends on transformation regime/shape.** Any reusable cache key must bind the representation-shaping metadata needed to prove compatibility before concatenation/consumption.

This does not change the current Flash text-first bring-up order, but it belongs in later multimodal cache qualification.

## Other screened lanes

- `Pushkinist/rMLX`: no post-cutoff PR update surfaced.
- Rapid-MLX: no post-cutoff Qwen3.8 update surfaced.
- NInfer: no post-cutoff Qwen3.8 issue update surfaced.
- TurboQuant-MLX: no commit after the starting cutoff; same-day web-indexed 27B results are not fresh to this pass.
- llama.cpp #28243 Flash-Next MTP: PR activity surfaced, but no post-cutoff commit in its commit list; do not relabel its existing MTP claims fresh.
- vllm-mlx post-cutoff activity was documentation / Anthropic-image adapter work rather than a new Flash/27B performance receipt.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash-Next:** no fresh sustained exact 2x M1 Max 64 GB / TB4 TG or exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max 64 GB / TB4.
- **Single M1 Max64 Qwen3.8-27B:** no fresh exact target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt.

Therefore the canonical planning centers remain:

| Lane | TG | Cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64/TB4 | **40** | **400** |
| Qwen3.8-27B — M1 Max64 | **25** | **110** |
| Qwen3.8-27B — RTX5070Ti16 | **120** | **250** |
| DS4-0731 — 2x M1 Max64/TB4 | **15** | **180** |

These remain **planning targets, not measurements**.

---

# Incremental dual-M1 Flash bring-up consequences

Keep **PP2/layer ownership primary and TP2 as control**. Preserve the 15:10 + 17:53 + 19:19 + 21:57 chain, with these additions.

## Prefill tuning order

After exact PP2 semantics / recurrent ownership / cold-PP harness are frozen:

1. profile stage-local GDN, routed MoE, projection and synchronization attribution at realistic chunk widths;
2. perform a **chunk-width sweep per quant/kernel path** before judging kernels;
3. carry forward the 19:19 block-history GDN / repeated-work candidate;
4. test Q4-like double-buffered routed-expert staging only if M1 profiling shows barrier/load latency remains exposed;
5. include threadgroup scratch/occupancy and per-stage admission headroom;
6. select the cluster chunk jointly from stage balance + TB4 bubble/traffic data, not the fastest isolated stage;
7. combine only passing mechanisms, then measure exact cluster cold PP and append/live-prefix behavior.

## Persistent/speculative state ownership

Every reusable surface now has both **coverage and provenance**:

- request/session identity appropriate to the mathematical dependency;
- generation/epoch/slot owner;
- valid row/token range;
- explicit device happens-before before a later consumer is allowed to trust the host stamp;
- correct reset on cancellation, slot reuse, unload/reload and peer restart.

No model-global carry or hidden buffer may be treated as request-safe merely because today's default concurrency happens to suppress its use.

## Distributed lifecycle / PP2 state machine

Add explicit cells for:

- targeted cancellation during prefill and decode;
- all-request/watchdog cancellation;
- stale cancel marker / future epoch / worker restart;
- rank barrier before state removal/reuse;
- terminal response signaling after cancellation;
- local + remote cache clear loaded/unloaded;
- peer-local path resolution;
- prompt-cache agreement after memory/SSD lookup;
- transport request-ID continuity through streaming and non-streaming paths.

## QSA long-context provenance

Record and certify:

- actual indexer `top_k` / selection budget;
- context depth;
- selected-set/tie semantics;
- realized low-precision cache/indexer path;
- any metadata override used by the harness.

Do not infer ~128K economics from short-context PP with a different selection width.

## MTP / structured agent serving

Retain 21:57 requirements for grammar-state snapshot/rewind, actual MTP engagement, sampler ownership/fallback and fairness. Add quant-layout-aware target-op/hook realization and forced-rejection rollback before declaring a new quantized target compatible.

For MTP depth: actual-resolved block/depth remains mandatory provenance. Default depth is certified first; deeper depths are separate correctness + whole-round A/B cells. Tape/refold remains orthogonal and post-replay-baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot recurrent/spec state isolation, physical recurrent capacity, PP+MTP distributed ownership and concurrent-state semantics are certified.

The appliance concurrency claim remains strict:

> B2/B3/B4 means that many independent requests are simultaneously physically scheduled with their own correct persistent state. Configured, admitted, batched or queued slots do not count.

---

# Other lanes

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. No fresh exact-card receipt surfaced. The fresh QSA/Vulkan and distributed lifecycle results are mechanism evidence only. Preserve realized placement/backend, VRAM/context headroom, sampler path and real coding-agent wall-time provenance.

## Single M1 Max64 Qwen3.8-27B

No target movement. The M3-Max ParoQuant/DFlash2 result strengthens compatibility and rollback requirements but is not an M1 receipt.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## Dual-M1 DS4-0731

No target movement and no fresh exact sustained current-head dual-M1 generated-token receipt. ds4 #991 remains Flash-Next kernel mining, not DS4-0731 throughput evidence.

---

# Standing decisions strengthened this pass

- Chunk width is a quant/kernel/topology-specific tuning dimension, not a universal serving constant.
- Kernel A/Bs are invalid if the control/candidate use materially different cold paging or heat-soak regimes without explicit handling.
- Double buffering is promoted only when exact profiling shows exposed staging/barrier latency and scratch/occupancy remains acceptable.
- Coverage and provenance are separate state predicates.
- Every cross-turn/cross-request speculative buffer carries owner identity plus generation/epoch.
- Common prompt prefixes are not generic request identity; any prefix-based reuse must be justified by the exact mathematical dependency of the reused state.
- Configured/enabled and actually armed/executed are separate benchmark fields.
- Host ownership stamps do not establish device happens-before.
- Distributed cancellation is a synchronized state transition, not rank-zero bookkeeping.
- Cancellation acknowledgements are plan/epoch/worker scoped so stale all-request state cannot poison later targeted requests.
- Prompt-cache reuse in PP2 requires cross-stage boundary/owned-byte agreement after lookup.
- QSA/indexer selection width is long-context benchmark provenance and must be paired with semantic selected-set/quality certification.
- Cache keys bind representation-shaping metadata, not only source-content identity.
- Quantized target/draft compatibility includes realized module classes and speculative hook coverage, not dimensions alone.
- Forced-rejection rollback and unload/reload re-arming are part of speculative compatibility.
- Structured-output grammar state remains speculative state and is checkpointed/rewound with the emitted frontier.
- Distributed sampling lives where complete logits exist or uses an explicitly supported reduction path.
- Silent sampler fallback remains a failed optimized cell even if correctness survives.
- Prefill/decode fairness remains a serving correctness property, not merely a throughput knob.
- Isolated component microbench speedups do not become PP gains without production-style wall A/B.
- Controlled negative experiments remain first-class mining evidence.
- A benchmark cell is defined by what the engine actually executed, not merely what the CLI requested.
- The 15:10 oMLX #3494 attribution correction remains authoritative.
- Tape/refold remains a post-baseline optimization candidate, not a replacement for replay correctness.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
