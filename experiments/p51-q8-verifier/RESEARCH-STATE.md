# Canonical Runtime / Architecture Research State

Last consolidated: 2026-10-02 23:26 ET.

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
7. **Standing shorthand:** if the user says **"search and update"**, perform the search **and** true up GitHub in the same turn. A chat-only summary is incomplete. Write/advance the dated watch and `RESEARCH-WATCH-LATEST.md`; update this file and `RESEARCH-TARGETS.md` when durable conclusions or planning state changed; commit and verify the final branch head.

The protocol exists because older project anchors were previously rediscovered after falling
out of the formal watch-note chain.


## 2026-10-02 23:26 ET consolidation delta — Strata 0.1.38; custom M1 27B verifier lane; RX prefill experiment formalized

### Strata 0.1.38 is the current baseline

The 0.1.38 release commit was created at 2026-10-02 20:54:11 UTC and was missed by the preceding watch pass.
It becomes the exact-box baseline.

The release bundles several known prompt-path improvements (#372/#374/#413/#452), Q5_0 GPU experts, IQ4_XS AVX2
experts, unbuffered Windows loading and peer-device support. No new exact 5070-Ti/IQ3_S/native262K controlled ladder
lands in this pass, so physical-fit/admission/stability/TG/PP planning priors remain unchanged.

Open #510/#525/#537/#572 parser/tool fixes are not credited as shipped merely because they target 0.1.38.

### Single-M1 Qwen3.8-27B is now an explicit custom-engine optimization lane

Recovered MTPLX #506 evidence isolates a concrete pre-M5 long-context bottleneck:
- the packed-GQA q=2..4 verify kernel designed for long dense KV never dispatches in the measured path;
- context-dependent verify traffic scales with MTP draft depth;
- production M3-Max telemetry falls from ~32.9 TG at 4-16K to ~20.2 TG at 64K+;
- the reporter estimates a correct one-sweep verify path could yield ~+30% at 64K and ~+39% at 88K.

Those uplift numbers are estimates on M3, not exact M1 measurements, so the canonical single-M1 25-TG / 110-PP target
does not move.

However this materially changes implementation priority. A Project-51 M1 27B engine should:
- treat multi-row full-attention/GQA verify as a bespoke kernel, not a generic SDPA fallback;
- ensure one long-KV traversal serves the whole accepted/drafted row block;
- benchmark q=2/3/4 and wider DFlash-style blocks;
- log dispatch counts/fallbacks;
- run a 16/32/64/96/128K context ladder with acceptance and total verify-cycle time.

The old MTPLX 2.11.1 semantic-corruption reports (#459/#464) were an M5 NAX kernel accidentally enabled on M1-M4
and were fixed in 2.11.2; do not treat them as evidence that MTP itself is unsafe on M1.

### RX 6800 is promoted to a formal dense-27B prefill-producer experiment

Strata's current RDNA2 documentation now gives a strong gfx1030 anchor:
- RX6900XT-class / 63-GB host / full 131K Flash-Next: 38-42 TG;
- ~330-339 PP with 8K prompt chunks;
- plain hipBLAS, because gfx1030 has no hipBLASLt kernels.

The maintainer additionally reports an exact RX6800 Windows result reaching ~42 TG on 0.1.37 after the current HIP
path improvements.

Separate llama.cpp evidence shows Qwen3.8-27B Q4_K_M on a dual RX6800XT+RX6800 setup at ~230 cold PP for a fresh 15K
prompt. This does not establish single-card PP, but proves dense-27B execution on RDNA2 and provides a scale anchor.

Because DASLab IQ3_S (~11.8 GB) / IQ3_XXS (~10.1 GB) and similar ByteShape packs fit inside one 16-GB RX6800, the
user's Linux RX6800 is now worth testing as a **cold-prefix producer** for a tuned M1 decoder.

No production PP credit yet. Required gates:
1. single-RX6800 local 16/32/64/96/128K cold PP on the exact candidate quant;
2. export of all continuation state, not KV alone;
3. committed-frontier metadata and tokenizer/model identity;
4. import into the M1 engine;
5. Mac-native-vs-imported continuation equivalence;
6. transfer time included in end-to-end TTFT.

### Cross-engine handoff is feasible but HIP->M1 remains unimplemented

TensorFold #77 already established that Qwen3.8-27B CUDA conv/recurrent/KV state maps directly into the corresponding
MLX caches with only batch/axis layout changes. The issue moved implementation to MCDMA rather than rejecting it.

MCDMA has since run a smaller Qwen3-4B Spark-prefill -> Mac-decode request end-to-end, moving ~2.17 GiB in 0.48 s over
RDMA. That is architecture proof, not an RX6800 transport measurement.

Project-51 keeps the existing 32K -> 96/128K bridge qualification sequence and adds HIP/RDNA2 as a producer candidate.
No RX->M1 latency credit is granted until the exact transport and state contract are measured.

**Primary 5070-Ti fit/admission/stability/TG/PP priors, native262K target and hardware-purchase decision remain unchanged.**


## 2026-10-02 20:20 ET consolidation delta — Apple TQ works but does not buy ceiling by arithmetic; hot VRAM release stays out of baseline

### Apple QSA TurboQuant is now measured, but capacity credit requires cold-prefill proof

oMLX #3436 now has live M4 Pro / 64-GB evidence that real QSA TurboQuant works:
- ~84,839-token request;
- measured memory ~55.8 GB at the BF16/full-precision prefill peak;
- ~49.2 GB after 4-bit QSA KV conversion;
- exact needle retrieval at ~64K in the reported test.

The important negative result is stronger than the post-prefill saving: the author also tested quantizing during
prefill and **it did not move the practical context ceiling**. Project-51 therefore does not award context-capacity
credit from KV bytes alone. A compressed-KV lane must prove lower **cold-prefill transient peak** on the actual runtime.

oMLX #3437 independently walks a previous single-64GB Apple ~200K+ projection back to a measured ~121-122K ceiling
for Flash-Next oQ2 with streamed experts on one 64-GB M4 Pro. Chunked-prefill transient memory, not resident expert
weight arithmetic, is the limiting wall.

This does **not** lower the dual-M1/TB4 target: it is a different machine/topology/runtime/quant. It does remove a
bad inference path. The dual-node 200K+ target must be established by a true two-node cold admission ladder rather
than extrapolating from streamed weights or TurboQuant cache size.

### Strata hot expert-cache release is useful but excluded from certification

Strata #563 can unmap the expert-cache VRAM while leaving the model/session loaded and refill it later at the same
virtual addresses. The reported 3090 test gives back 14.5 GiB in ~50 ms and refills in 1.7-2.5 s with byte-identical
slots over three cycles.

However, a refill while another Windows application still occupies the card can trigger WDDM shared-memory spill and
drop decode to ~10-17 TG. Keep the feature OFF for the primary Project-51 baseline. If later enabled for workstation
sharing, admission after refill must verify dedicated/shared VRAM before servicing inference.

### Correct a TensorFold resume interpretation

TensorFold #287 demonstrates that an earlier 32K "resumed turn re-prefills" result was caused by **editing the tail of
the last message**, not by an ordinary append-style multi-turn resume. Ordinary append resumes were already fast on
0.6.2; the PR adds an earlier checkpoint specifically for tail-edit clients.

Do not use that old benchmark as evidence of general Mac resume failure. Separate >100K retention/admission evidence
still justifies the broader Project-51 resume-equivalence gate.

### Restore should validate before becoming serviceable

vLLM #59832 adds a private recovered-output canary before a snapshot-restored engine opens HTTP. Carry this design
principle into future Strata conversation-cache qualification: a restored 200-262K agent state should pass a known
deterministic continuation canary before it is admitted as production state.

**Primary 5070-Ti fit/admission/stability/TG/PP priors, native262K target and hardware-purchase decision remain unchanged.**


## 2026-10-02 19:25 ET consolidation delta — FP8 PLE becomes preferred fidelity candidate; agent/parser and deterministic-residency gates tighten

### PLE precision is now a first-class quality lever

Strata #464 now carries stronger evidence that checkpoint-native PLE precision matters materially:
- stock IQ4_NL vs BF16 first-window KL is reported at 0.156 / 0.0030 / 0.220 on 2K / 16K / 37K prompts, with the
  top token unchanged in each probe;
- an independent 0.1.37 / RTX5090 NVFP4-derived measurement reports answer-level FP8-vs-BF16 median KL ~0.00087,
  on the same scale as BF16-vs-BF16/cache-size noise (~0.00080);
- BF16 prompt cost remains within roughly +/-2.3% of stock IQ4_NL through a 232K-class sweep.

This does **not** prove FP8 PLE equivalence on the exact IQ3_S target. It changes the qualification order:
1. stock IQ4_NL PLE for compatibility/performance;
2. **native FP8 PLE as the preferred production-fidelity candidate**;
3. BF16 PLE as the source-of-record control.

The exact IQ3_S lane must still measure long-agent KL/logit/top-flip/trajectory behavior. The important engineering
point is that PLE fidelity can likely be improved without increasing the 54.8-GB transformer arena or breaking the
native262K physical-fit case.

### Controlled quality runs must keep adaptive residency frozen

Strata #463 now has independent evidence that the nonblocking adaptive-swap timing can fork greedy output.
Strata #550 adds a second race: the expert-residency table itself is uploaded on a legacy stream and can be read from
a non-blocking compute stream before DMA completion after swap/trim/refill.

Therefore the Project-51 AA/source-certification lane explicitly keeps:
- `--adapt-swaps 0`;
- deterministic/fixed expert cache placement;
- `--pcie-frac 0` for the strict arithmetic gate;
- fresh process / prompt cache off where already specified.

Adaptive residency is qualified later as a production-performance mode, not allowed to contaminate the fidelity
baseline.

### Agent parser certification is now a discrete blocker independent of hardware viability

Strata #537 reproduces, on v0.1.37 + IQ3_S, both:
- quoted/self-generated `</think>` text ending or leaking reasoning incorrectly;
- unfinished tool-call structures disappearing behind an empty clean-stop response.

vLLM #59821 independently shows the other side of the parser ambiguity: a quoted `<tool_call>` inside reasoning must
remain reasoning while a genuine implicit-end call must still execute.

The Project-51 agent parser suite must therefore test literal and generated think tags, quoted tool markup, genuine
implicit tool calls, malformed historical calls, unfinished current calls, and ordinary well-formed tool loops.
Do not call the local runtime production-agent-ready until these pass, even if raw model/runtime stability is good.

### sm_120 custom-build sanity becomes mandatory before interpreting PP

Strata #542 shows a CUDA 13-header / CUDA12-runtime ABI mismatch can make shared-memory capacity read as 1 byte,
silently disable IQ MMQ, and cut prefill roughly 4x. The official prebuilt was not the failing path.

Any custom 5070-Ti build must record linked/runtime CUDA, sanity-check GPU properties and reject impossible values
before a PP measurement can enter Project-51 planning.

### Long-context restore remains a separate qualification target

New official-v0.1.37 Windows data in Strata #189 shows correct 57.7K conversation-cache restore on an RTX4070 Laptop /
64GB system, so #528 is not evidence that all parking is broken. But #528's ~100K RTX5090 restored-decode collapse
remains unresolved, and mlx-serve #706 independently reports one corrupted Flash-Next hot-cache restore on M5 Max.

Initial production baseline therefore still leaves conversation parking OFF. Resume equivalence must be proven at the
actual 200-262K agent regime before parking earns production status.

**No physical-fit, admission, zero-stall, TG/PP-center, context-target or hardware-purchase change.**


## 2026-10-02 16:03 ET consolidation delta — 0.1.37 self-healing arrives; parking disabled; xhigh budget made explicit

### Strata 0.1.37 becomes the exact-box baseline

The 0.1.37 release commit was created before the previous hard boundary but was missed by that pass. A new strict-window
maintainer update on #481 confirms that 0.1.37 is the release carrying the server-side safety net.

The implementation ends a request whose engine goes silent for too long, kills the engine, and lets the next request
restart it. The default silence threshold is 300 s, with larger allowances while long prompt chunks are being read.

The underlying #481 server/engine lost-step root cause is still open and there is no real post-release recurrence/soak.
Therefore:
- physical fit stays ~95%;
- Windows full-context admission stays ~90%;
- 8 h zero-stall stays ~75%;
- 24 h zero-stall stays ~55%.

Replace the old ambiguous "<60 s built-in recovery" planning line with two clearer claims:
- **automatic #481-style containment/no-manual-service-restart: ~85% planning confidence**;
- **sub-60 s recovery: not yet qualified and not the shipped default** (default detection is 300 s).

Production qualification should lower `engine_silence_s` only after checking cold/slow-prompt behavior, then measure
stall->error, next-request->READY, prefix restoration/re-read and whether any human action is required.

### Conversation parking is not production-safe yet

Strata #528 reports a severe restored-conversation decode regression on 0.1.36 / Windows / RTX 5090 / IQ3_XXS:
roughly **18-31 TG after parking restore versus ~87-116 TG using ordinary prompt reuse** on the same ~100K
conversation. Fresh ~100K decoding is also fast.

Until the restore path is fixed and qualified:
- set conversation parking/cache **OFF** in the first Project-51 production baseline;
- ordinary prompt/prefix reuse remains allowed;
- restore-vs-reprefill A/B becomes an explicit later gate.

This is an optional-feature performance failure, not evidence against native262K physical fit.

### High/xhigh needs an explicit reasoning budget

Strata #530 reports repeated high/xhigh requests ending at `max_tokens` with empty final content because reasoning
consumed the whole allowance. Older #123 confirms `reasoning_budget_tokens` is supported since 0.1.31 but is off by
default.

Project-51 high/xhigh requests now require an explicit reasoning budget until Strata supplies a safe default/warning.
Record `finish_reason`, reasoning-token count and visible-answer-token count during certification. Do not diagnose an
empty length-terminated response as an IQ3_S quality failure until this configuration error is excluded.

### Agent surface gets one more vision-tool gate

Strata #529 shows that an Anthropic `tool_result` containing an image can lose the image before the vision encoder.
The open patch fixes the Claude-Code `Read` screenshot path. If screenshot-driven QA enters the certification suite,
#529-equivalent behavior must be present.

**No TG/PP center, native262K target, protected-K policy, physical-fit prior or hardware-purchase change.**


## 2026-10-02 15:02 ET consolidation delta — 0.1.36 baseline; #481 still pending; agent-tool parser gate added

### Current exact-box baseline is Strata 0.1.36

Recovered release evidence shows engine 0.1.36 existed before the previous pass's cutoff. The prior watch chain's
"0.1.35 latest" statement was stale.

0.1.36 becomes the current exact-box qualification baseline. Its release commit includes cancelled-prompt accounting,
draft-head failure guidance, update scripts and learned expert-profile persistence. The subsequent 0.1.36 speed merge
adds RTX-50-class decode kernels and optional fused native-IQ prompt experts.

The release commit does **not** include #481's server/engine lost-step recovery, and #481 has no post-boundary
confirmation that 0.1.36 fixes it. Keep:
- IQ3_S/native262K physical fit: ~95%;
- Windows full-context admission: ~90%;
- 8 h zero-stall: ~75%;
- 24 h zero-stall: ~55%;
- current-release built-in <60 s recovery: ~55%.

### RTX-50 decode work is favorable but does not justify an IQ3_S TG-center move yet

The 0.1.36 cluster kernels are bitwise against the prior QSA top-k / greedy argmax paths in their parity harness.
On an RTX 5070, QSA top-k kernel time drops from roughly 200 -> 22 us at 262K and greedy argmax from ~39.6 -> 5.9 us.

This is exactly the right GPU generation for the user's 5070 Ti, but these are subphase numbers.
Do not convert them directly into full-request IQ3_S TG. Measure on the exact box first.

### Keep STRATA_PF_FUSED=1 out of the source-certification baseline

The optional native-IQ fused prompt kernels do not help IQ3_S on the published exact RTX 5070 A/B:
~ -0.2% at 4K and -1.4% at 32K. The fused path is numerically close to the default but not bit-identical; one IQ3_S
greedy comparison diverged after a 31-token common prefix.

Therefore:
- canonical IQ3_S certification uses the default native-IQ prompt path;
- STRATA_PF_FUSED=1 is a separate performance/quality experiment only;
- no PP-center change.

### Add agent tool-call parsing to the production-readiness gate

Strata PR #525 documents a real Qwen3.8-Flash-Next failure mode where a tool call begins before the model emits
`</think>`; the current parser can then emit the complete tool call as reasoning and an agent silently stops because
it sees no executable call.

The open patch treats `<tool_call>` inside reasoning as an implicit think end. This is directly relevant to the
user's long QA/coding-agent workload.

Production-agent certification now explicitly requires:
- #510-equivalent safe handling of malformed/partial historical tool arguments;
- #525-equivalent reasoning->tool boundary handling;
- repeated long tool-loop replay under xhigh/high reasoning.

These are agent-surface gates, not reasons to lower physical-fit or raw runtime-stability priors.

### Apple adjacent runtimes reinforce the retained-context/accounting gate

TensorFold #271 and oMLX #4213 both show that a model's nominal/native context and host memory size do not guarantee a
large **resumable** agent window. TensorFold 0.6.0 can actually report a smaller retained window when the memory budget
is raised because its prefill chunk choice consumes more working memory; oMLX 0.7.0 can reject a ~139K Flash-Next
session through its dynamic guard on a 128-GB M5 Max.

No Windows/Strata target movement. Keep measuring cold admission, retained continuation state, restore, and subsequent
turn behavior separately.

**No hardware-purchase, native262K-context, protected-K, TG/PP-center, or fit-prior change in this consolidation.**


## 2026-10-02 12:59 ET consolidation delta — IQ3_S/full-context fit rises to ~95%; #500 headline de-risked

### Same-memory-shape IQ3_S evidence closes most of the remaining physical-fit gap

Recovered Strata #406 evidence includes a Windows user with **64 GB RAM + 16 GB VRAM + IQ3_S** who manually set
the context to 256K and reports that it works fine with only a slight performance hit. The original Linux/64-GB
IQ3_S reporter ran full native context with >6 GB free. Strata 0.1.33 then changed setup to preserve a user-selected
262,144 context rather than forcibly reducing it to 128K.

This is not the user's exact RTX 5070 Ti, but it is the missing **same OS + same host RAM + same VRAM capacity +
same quant** memory-shape receipt. Combined with:
- exact 5070 Ti / ~63-GB Windows / native262K operation on IQ3_XXS (#31);
- IQ3_S through a real ~250K prompt on 11-GB VRAM (#469);
- exact 5070 Ti 257,466-token cold execution on IQ3_XXS (#200);

the Project-51 **IQ3_S/native262K physical-fit prior rises from ~90% to ~95%**.

Windows 16-GB/64-GB full-context admission planning confidence rises from **~85% to ~90%**.
This is still not exact-box certification: the user's own cold ~250K IQ3_S prompt must survive with measured RAM,
commit, hard faults, WDDM shared memory and late transient peaks.

### #481 now has a planned recovery path, but do not pre-credit an unreleased fix

The maintainer resolved #481's stack to an untimed condition-variable wait where engine and server appear to have
lost step. The next release is intended to restart the engine when a request has no output for too long or a stop is
never acknowledged.

Until that release ships and is soaked, keep:
- 8 h zero-stall: ~75%;
- 24 h zero-stall: ~55%;
- current-release built-in <60 s recovery: ~55%.

Once the release lands, immediately test the exact #481 stress shape: long xhigh thinking, heavy retained prefix,
abort/cancel, immediate next request and repeated tool turns.

### #500 remains a mechanism candidate, not a throughput prior

An independent RX 7900 XTX / IQ3_S measurement of PR #500 reports roughly -2.3% decode and -0.6% 32K prefill.
On that machine the quant segment is too small for the extra pool-phase protocol to pay.

Therefore the original +69-78% result is explicitly **excluded** from Project-51 TG forecasting.
Retain the patch only as an exact-box A/B candidate; the user's Ultra-7/DDR5 host may behave differently.

### Low-bit MTP exactness remains a first-class quality gate

oMLX #4209 reports that a uniform 4-bit Qwen3.8-Flash-Next checkpoint changes greedy output with Lightning MTP on
versus off, while a 5-bit checkpoint is byte-identical on the same four prompts.

Do not transfer this as a Strata defect. Carry the architectural lesson: the production quant must pass exact
plain-vs-MTP continuation checks on the served runtime, especially at low precision.

**No mature TG/PP center, hardware-purchase decision, protected-K policy or native262K production target changes.**


## 2026-10-02 10:24 ET consolidation delta — oMLX gets a real Flash-Next TQ-QSA branch; Strata CPU lever corrected

### oMLX now has a direct Qwen4Exp / Flash-Next TurboQuant-QSA integration branch

oMLX PR #4206 is the first source-visible adjacent-runtime implementation in the watch chain that wires TurboQuant
through Qwen4Exp's QSA path rather than treating it as generic dense-attention KV only. The diff adds
`TurboQuantQSAKVCache`, QSA-aware block/prefix-cache payload reconstruction, and fused TQ-enabled prefill plumbing
for both NAX and simdgroup paths. The PR also adds YaRN handling above the native 262,144 window.

This is **open / unmerged**, has no M1 Max receipt and has no Project-51-grade long-agent quality/KL result.
Its M5-Max 1M/TQ4 claim is outside the production target. Project-51 therefore adds #4206 as the active Apple
TurboQuant-QSA research branch but keeps **native262K first** and requires an exact M1/simdgroup PP/TG + fidelity run
before any dual-M1 target changes.

This does not change the Windows plan: stock Strata INT8/K8V4 first, custom TurboQuant only if measured headroom
requires it.

### Strata's CPU-pool bottleneck is real, but host-thread pinning is not the lever

Strata #494 established that the CPU expert pool can consume about half a fresh verify round on a constrained-GPU
host. PR #501 measured the proposed serve-host pin explicitly and found the thread was already pinned through the
session scratch; same-binary explicit-pin A/B was ~0 performance and the PR was closed unmerged.

Durable correction: do **not** carry "pin the serve host" as a speed target. The remaining CPU-side opportunities
are pool arithmetic, memory bandwidth, expert-cache behavior and serialized work between phases.

PR #500 identifies one such serialized phase: intermediate activation quantization between gate/up and down was
performed serially by the host and the patch parallelizes it through ExpertPool workers. The source mechanism is
credible. Its reported +69-78% end-to-end decode improvement is **not certified** because the performance arms also
change expert-cache hit rate (~80-85% -> ~93-95%) and MTP acceptance (50-60% -> ~61-68%). Those changes violate the
spirit of the fixed-residency A/B needed to isolate one arithmetic barrier.

Before using #500 numerically, rerun with fixed expert residency, adapt-swaps off, pcie-frac 0 for the deterministic
arm, prompt cache off, identical token stream, and direct phase timing.

### Another Windows 16-GB IQ3_S receipt, but no exact-box prior movement

Strata PR #499 runs IQ3_S on a Windows RX 9070 XT 16 GB with 128 GiB host RAM at a 65,536-token window. It reports
45.2 TG median decode, ~370 PP at 4K and ~602 PP at 32K, with a 46.84-GiB host expert arena and ~9.48-GiB GPU expert
cache.

This supports operational maturity of IQ3_S on a 16-GB Windows GPU but is neither a 64-GB-host nor native262K
receipt. The RTX-5070-Ti/64-GB physical-fit prior remains **~90%**.

### Compressed-KV lesson strengthens: native kernels/layout matter as much as bits

vLLM PR #59774 introduces a native RDNA3 3-bit KV backend and reports much faster 380K attention than its TurboQuant
K3/V4 control at roughly similar capacity, plus lower NLL drift for some formats. Those AMD numbers do not transfer to
CUDA/Strata.

The durable mechanism lesson is that a generic compressed representation can lose badly if the runtime pays
dequantization/metadata/synchronization costs. This further supports Project-51's order:
**measure Strata INT8/K8V4 first; only port TurboQuant if the capacity need survives measurement, and fuse it into the
actual QSA prompt/verify paths rather than treating compression alone as the win.**

**No canonical TG/PP center, fit/stability prior, hardware-purchase decision, protected-K policy or native262K
production target changes in this pass.**



## 2026-10-02 08:27 ET consolidation delta — transient/calibration gates tighten; MLX gets a batch-shape exactness gate

### Exact-box fit prior stays at ~90%, but the late-allocation gate gets stronger

Strata #486 is a new native-262K failure report on a very different topology: Linux, 2x modified RTX 2080 Ti 22-GB
cards, IQ3_XXS, vision enabled, layer split, INT8 KV and MTP spec4. A late ~1.43-GiB weight-arena cudaMalloc fails
at 262,144 and the host can become unresponsive; 204,800 is stable.

This does **not** reverse #469 or lower the current ~90% physical-fit prior for the user's single RTX 5070 Ti 16-GB /
64-GB, text-first IQ3_S lane. It does strengthen an existing rule: admission is not proven until a real ~250K cold
prompt survives its transient prefill/indexer/weight-arena peak. Keep the first exact-box run vision OFF and MTP OFF,
then add MTP.

### Do not trust a single automatic PCIe fraction on v0.1.35

Strata #485 measures the same RTX A3000 / PCIe 4.0 x16 host at 18.5, 6.9 and 5.8 GB/s across separate startup probes.
The low readings select pcie_frac around 0.12-0.15, while the host's decode calibration peaks around 0.35
(32.7 TG versus materially lower values around the under-selected region). Open PR #487 primes the link and uses the
median of five bursts.

Until a released baseline contains this fix, exact-box qualification records the startup probe on multiple fresh starts
and runs tools/calibrate.py when it is unstable. One auto pcie_frac value is not treated as hardware truth.

### CPU/DRAM path remains first-order on low-VRAM Flash-Next

Strata #489/#494 profile a 12-GB A3000 + i7-12850HX IQ3_XXS lane. In a fresh-decode window at hit_rate 0.354,
the CPU expert pool consumes 41.6 ms / 53% of a 78.1-ms round while the GPU term is 26.7 ms / 34%.
This supports treating the user's stronger Ultra-7/DDR5 host as a potentially material decode advantage over weak-host
receipts, but it is not an exact-box result and does not move the IQ3_S TG centers.

Open PR #484 also adds conversation-cache counters for prompt reuse, switch restores, parked slots, cache RAM and
evictions. Use them in the retained-prefix harness if/when they reach a stable release.

### Long-agent soak remains mandatory; cross-runtime evidence strengthens the stress shape

Strata #481 still has no identified fix. A second terse "me too" is not enough to move the ~75% / ~55% 8 h / 24 h
zero-stall priors.

vLLM #59768 is separate-runtime evidence: Qwen3.8-Flash-Next with MTP, 80K-185K agent requests, 92-98% GPU KV
pressure and a 74K-141K asynchronous CPU->GPU prefix restore repeatedly hits an illegal-memory-access crash.
Do not transfer this as a Strata failure probability. Add its **restore + high pressure + MTP + immediate decode**
shape to the Project-51 soak matrix.

### MLX certified comparisons gain a batch-shape determinism gate

MLX #4613 reports that 0.32.3 split-K quantized_matmul stores partial sums in the input dtype, so BF16/FP16 rounds
each partition before the final reduction. The split factor depends on M, and the report demonstrates the same row
changing when evaluated alone versus batched.

This is not Flash-Next quality evidence, but it can contaminate Project-51 MLX fidelity A/Bs. Certified MLX
comparisons now:
- pin the MLX revision;
- record batch/row shape;
- compare identical tokens alone versus batched;
- hold batching constant before attributing logit/trajectory differences to quant/KV changes.

### Apple MTP telemetry remains first-class

oMLX #4202 reports a custom-FP16 M2 Ultra lane moving from 0/12 to 9/12 MTP-parking events and roughly -10% median
decode at 32K/64K after a v0.7.0-based rebuild. The report is explicitly confounded and does not move dual-M1 targets.
It reinforces logging MTP engaged/parked state, acceptance and verify-cycle cost under a pinned runtime revision.

mlx-serve #687, updated in this window, further shows that cold PLE/n-gram page residency can dominate TTFT; its
large diagnostic gains were measured with warming disabled and the proper warmed A/B is still pending. Keep cold-table
startup and warmed steady-state measurements separate.

**No TG/PP center, hardware-purchase decision, TurboQuant order, K-precision policy or 262,144 production-context
target changes in this pass.**



## 2026-10-02 05:52 ET consolidation delta — IQ3_S 262K fit strengthens; long-agent stability weakens

### Physical fit moves upward

Strata #469 runs IQ3_S at native262K on an RTX 2080 Ti 11 GB. A real 250K cold prompt runs 466.6 PP / 31.8 TG; the
250,463-token follow-up reuses 249,993 tokens and begins answering in 4.55 s. Engine RSS remains roughly
**52.3-52.9 GiB**, with 3.09 GiB of streamed KV pinned in host RAM.

The host has 128 GB, so this is not an exact 64-GB-host proof. However, the target 5070 Ti has 5 GB more VRAM for
expert residency. Combined with v0.1.35's Windows low-RAM/resident-tier fix, the physical-fit/admission prior for
**5070 Ti 16 GB + 64 GB + IQ3_S + native262K** rises to **~90%**.

### Production stability moves down

Strata #481 reports repeated permanent deadlocks on a 5060 Ti 16 GB / 64 GB / Windows coding-agent box under
34K-85K heavy-prefix prompts and long reasoning streams. The watchdog does not fire and the Python server does not
recover after the engine is killed without a full service restart.

At this cutoff no v0.1.35 fix is identified.

Planning confidence:
- 8 h zero-stall soak: **~75%**;
- 24 h zero-stall soak: **~55%**;
- Windows auto-admission: **~85%**;
- built-in recovery under 60 s: **~55%**.

The exact-box soak must include long xhigh/high reasoning, tool loops, prefix reuse, cancellation and immediate retry.
Use an external supervisor for early production testing.

### BF16 PLE becomes a first-class fidelity control

Strata #464 can stream the checkpoint's original BF16 PLE table. It is 102.4 GB on disk versus 28.8 GB for the
DASLab IQ4_NL PLE, but the reported prompt-speed difference is within about ±2.3% across 9K-237K.

Representation changes are nontrivial: 14.6% of measured routing entries differ and every probed first-window logit
differs (mean absolute delta ~0.22, max 1.69). No accuracy result proves BF16 better.

Add BF16 PLE as a **source-of-record AA/agent control**; keep IQ4_NL production-default unless the control shows a
meaningful end-to-end gain.

### Draft-vocab size becomes an exact-box headroom lever

Strata #474 reports IQ3_S/262K on a 12-GB RTX 3060 failing MTP startup with the default CJK draft head (~348 MiB),
then starting with the English head (~133 MiB). For the user's work/code lane, the English draft vocabulary is the
first emergency VRAM lever if MTP cannot bind. Keep the larger vocabulary for multilingual qualification.

vLLM #59740 independently validates reduced Flash-Next draft vocabulary as a real mechanism, but its measured speed
gain is not transferred to Strata.

### Adaptive-residency exactness remains gated

Strata #462/#463 localize an adaptive expert-copy race that changes CPU-vs-GPU execution and can fork greedy output.
The proposed wait makes the reported test reproducible at under 0.3% cost, but #463 remains open at this cutoff.

Certified P51 comparisons continue to disable adaptive swaps and freeze residency.

### Agentic IQ3_S receives one useful but small receipt

Strata #483 reports a small semver coding-agent task on 2x 5060 Ti 16 GB: IQ3_S medium and xhigh both score 55/55,
while Qwen3.8-27B Q6 xhigh also scores 55/55 but takes about twice as long in that one run. This supports practical
agentic viability but is n=1 on a ceiling task, so no AA/intelligence-prior movement.

### Extreme context remains out of scope

Strata #466 demonstrates IQ3_S at roughly 1.048M real prompt tokens under YaRN x4 on a 5090/122-GB host. Project-51
stays at **native262K**.

**Mature TG/PP centers remain unchanged.**


## 2026-10-02 00:18 ET consolidation delta — Strata 0.1.34, exact 5070-Ti prompt receipts, full-window IQ3_S

### Strata 0.1.34 is now the exact-box baseline

v0.1.33 made the 64-GB setup policy advisory: an explicit native 262,144 context is kept instead of being forced down
to 128K, resident-budget clamping is hardened, and the v0.1.32 Windows vision helper regression is fixed. v0.1.34 adds
the MMQ tile fallback and fast cancellation of disconnected requests while retaining the v0.1.33 answer/speed gate.

Project-51 can therefore request native 262K through setup directly. First qualification remains text-only to maximize
VRAM/expert-cache headroom, but vision is no longer excluded because of the v0.1.32 AVX-512 bug.

Deterministic server A/Bs now freeze all known state-dependent arithmetic:
**fixed expert cache, --prompt-cache 0, --adapt-swaps 0, --pcie-frac 0, STRATA_IQ_MT_MIN=1**, plus fresh process
state when testing persistence itself.

### Exact RTX 5070 Ti 16-GB prompt-path evidence now brackets the weak-host floor

Strata #439/#452/#453 all use an RTX 5070 Ti 16 GB on PCIe 3.0 x16 with a Ryzen 5900XT and DDR4-2133. That host is
materially weaker than the user's DDR5 Ultra-7 box.

On IQ3_XXS:
- grouped native expert gathers move a roughly 30K prompt **1,633 -> 1,702 PP** and are reported bit-identical;
- Q4_0 streamed-KV tensor-core prompt attention moves 8K-30K prompts from roughly **1.58-1.60K** to
  **about 1.88-1.90K PP**, with 15/15 needle passes but non-bitwise continuations;
- batched MTP-draft writes into the streamed KV ring give a repeatable **+4.6-4.7%**, reaching roughly
  **1.73-1.76K PP** in its independent A/B, with reported decode samples around 46-60 TG.

Do not sum these gains: the combined arm was not measured. Do not replace the canonical PP centers: older exact-card
receipts still show about 3.0K around 60K and 2,668 PP at 257K on a faster host. The durable conclusion is that
**host/link bandwidth plus prompt-path implementation can move same-GPU PP by nearly 2x**, so exact-box measurement
remains mandatory.

### IQ3_S now has a real prompt at the edge of the native window

Strata #440 runs DASLab IQ3_S on one RTX 5090 / 96-GB host at max-context 262,144. Needle tests use
**261,669-261,670 actual prompt tokens** and pass 9/9 across 32K/128K/256K and three depths. The same report measures
6,004 PP / 125 TG at its 128K speed point with the larger prefill chunk and 75-76% MTP acceptance.

This materially strengthens IQ3_S/full-native runtime maturity. It does **not** resolve the user's admission question:
the missing proof is still IQ3_S on **16 GB VRAM + 64 GB RAM** with real Windows desktop headroom.

### Long-context peak memory includes transient QSA/indexer scratch

llama.cpp #29825 halves Qwen4Exp indexer-score compute-buffer use: 11.7 -> 5.6 GiB at 262K/ub4096 in its reported
geometry, without a PP/TG change. #29827 shows a separate quantized-KV FA conversion buffer can reclaim hundreds of MiB
when bounded.

Project-51 admission accounting must therefore report:
- steady weights/expert cache;
- resident + host KV;
- MTP/draft state;
- QSA/indexer structural state;
- **peak prompt/indexer/convert scratch** at the chosen chunk size.

A configuration that fits at idle but OOMs during large prompt chunks does not pass the 262K fit gate.

### TurboQuant active plan protects K

The legacy K6/V4 ladder is superseded. TurboQuant's current high-GQA safeguard upgrades symmetric Turbo K to Q8 at
GQA >= 6, and Flash-Next is 12:1. Current Strata also has a strong existing INT8-K/K8V4 path.

Active custom sequence, only if stock controls still need more margin:
1. INT8 K/V fidelity control;
2. K8V4 built-in capacity control;
3. optional Q8/INT8-K + Turbo4-V parity bridge;
4. **Q8/INT8-K + Turbo3-V** capacity candidate;
5. compressed/symmetric K only as a research arm after direct long-context KL/logit/agent evidence.

The old K6/V4 quality prior is retained only as historical research context; it is no longer the production candidate.

### TensorFold stable advances to 0.6.1; Apple idle residency becomes a gate

TensorFold 0.6.1 reports up to about 10% one-stream Flash-Next long-context improvement on an M3 Ultra and adds more
CUDA prefix/fork reuse. This does not move dual-M1 targets.

MLX #4609 shows wired memory can be reclaimed after only a few seconds of GPU idle, making the next compute several
times slower in the reporter's test. Project-51 Apple agent certification now includes idle 2s/10s/60s -> next-turn
TTFT/residency, with a runtime heartbeat A/B when available.

A logical cached state is not a production-warm resident agent if macOS has evicted the backing pages and the next
turn must pay a large residency fault.

### Recovered older exact-GPU decode anchor

Strata #127, created Sep 29, ran three independent RTX 5070 Ti 16-GB IQ3_XXS lanes with 262K configured context.
Each completed a real roughly 141K-145K request at **78.4-80.1 TG**. This strengthens the exact-GPU deep-context
decode anchor but does not prove the user's 64-GB host, since the multi-lane system uses a shared host arena.

**Canonical numerical targets remain unchanged.**


## 2026-10-01 15:49 ET consolidation delta — v0.1.32, native-262K IQ3_S feasibility, and Turbo-K demotion

### The exact-box experiment order changes: stock IQ3_S first, TurboQuant second

Recovered TurboQuant source materially changes the proposed KV-port order. The current TurboQuant branch automatically
upgrades symmetric Turbo K+V requests to Q8 K when GQA >= 6 unless its safeguard is explicitly disabled. Its source
comment cites catastrophic Turbo3-K perplexity on a 7:1 Qwen case. Flash-Next's QSA geometry is 24 query heads / 2 KV
heads = 12:1.

TurboQuant PR #197 independently reports that Q8 K + Turbo4 V reduces mean KLD by ~26% versus symmetric Turbo4 and
describes K as the dominant KLD side. Current Strata prompt/verify code also favors an INT8 K path: K8V4 composes INT8 K
with compressed V and stays eligible for the optimized K path, while q4 K disables important prompt/verify fast paths.

Project-51 planning change:
- first prove **IQ3_S + native 262,144** using stock Strata memory/KV modes on the exact 5070-Ti 16-GB / 64-GB box;
- only if KV/expert-cache pressure remains material, prototype **INT8 K + Turbo3 V**, with MTP/draft KV kept INT8;
- symmetric Turbo3 K+V is a research arm, not the production default.

This changes implementation order, **not canonical numerical targets**.

### Native-262K IQ3_S on 64 GB is more plausible, but exact 16-GB-GPU proof is still missing

Strata issue #406 gives direct 64-GB host evidence: an IQ3_S user with 32 GB VRAM reports setup forcing 256K down to
128K, while a manual run-script edit served full native ~256K with >6 GB RAM still free. The extra context reportedly
cost about 1.8 GB over 128K.

This proves setup's conservative cap is not a physical impossibility result. It does not prove the user's 16-GB GPU,
where less expert mass can stay in VRAM and more must fit in host RAM.

Issue #392 adds real coding-agent IQ3_S evidence on 2x 5060-Ti 16 GB / 128 GB RAM: ~47 TG remained around 75K context
during Forge sessions, with hundreds of tool calls. Useful operational evidence, but not an exact-box quality or speed
receipt.

Qualification priority remains **single 5070 Ti + 64 GB + native 262K**, vision off, before buying another GPU or
writing a custom KV codec.

### Strata v0.1.32 is now the text baseline, with a Windows vision exclusion

v0.1.32 published in the strict window. The release includes multi-GPU prompt-path fixes and reports default Q2/IQ3_S
decode +1.5-3.8% versus 0.1.31 at equal expert slots in maintainer testing.

Immediately afterward, #411/#412/#419 established that the released Windows strata-vision.exe executes an unguarded
AVX-512 instruction on non-AVX512 CPUs. The main text engine falls back correctly and remains usable.

Project-51 therefore advances the **text baseline to 0.1.32** but keeps vision disabled on the user's Ultra 7 265F
until the helper is fixed and requalified.

### Memory admission and A/B methodology get stricter

Strata #380 demonstrates on Windows/RX6800 that using a free-VRAM figure which ignores the desktop can overfill the WDDM
budget, migrate engine allocations to shared system memory and make a larger apparent expert cache much slower. The
budget-aware path measured 41.4 TG versus 30.5 TG in that exact HIP test.

The user's 265F has no display iGPU, so the 5070 Ti's desktop/WDDM consumption is part of admission. Do not maximize
expert slots past the real process budget.

Issue #403 shows --resident-budget-gib can clamp exactly to the RAM safety limit and then fail a second availability
check after a small memory change. Leave explicit margin; do not rely on clamp-at-limit semantics.

Issue #410 shows STRATA_IQ_MT_MIN=1 is insufficient for deterministic server A/Bs. Adaptive expert movement changes
whether CPU or GPU evaluates an expert and therefore changes rounding/tokens. Fidelity comparisons require a fixed
expert cache, --adapt-swaps 0, prompt-cache controls, and preferably fresh process/server state. Residual medium-prompt
variation is still under investigation.

### Elastic KV is a speed/capacity lever, not today's low-RAM solution

Strata #378 maps KV physical memory only as context grows. On an emulated 16-GB budget it increases the expert cache
from 3,396 to 5,719 slots and improves short-chat/prompt numbers, but it explicitly requires every expert in RAM and
does not run in the low-RAM tier.

This reinforces the architecture model: KV savings can buy expert-cache residency and speed, but they are not by
themselves the mechanism that makes the user's 64-GB host fit. Do not assign its measured percentages to the 5070 Ti.

### MTP and cache-state certification remain first-order

Strata #382 finds an AMD MTP prompt hang specifically when streamed KV puts the drafter in ring mode; a per-group
fallback ran 30 rounds without hangs.

llama.cpp #29811 finds a separate Flash-Next MTP startup assert caused by constructing QSA k-pool inputs for an MTP block
that does not consume them.

vLLM #59642 reports 0% Flash-Next MTP acceptance in a disaggregated prefill/decode serving configuration.

These are different runtimes/backends, but together reinforce the Project-51 rule: **MTP correctness must be certified
for the exact state topology**, including prompt processing, rollback, cache/restore and any cross-worker handoff.

### Other mechanism evidence

- TensorFold #191 makes Flash-Next EXL3 routed-expert grouping essentially negligible at 1K-2K rows and reduces measured
  8K/32K prompt time ~8-9% on GB10, bit-identically downstream. Mechanism evidence only.
- Strata #407 reduces expert misses/CPU/PCIe substantially without a measurable primary round-time win. Optimize wall
  time, not cache-hit statistics.
- Strata #413 speeds one DeltaNet recurrence kernel ~1.44x but moves whole-engine PP only ~2% on its 4080-S test.
- oMLX #4175 shows a nominal 4-GB hot prefix cache making reconstruction 18-73x slower under memory pressure on an M4
  Max 36 GB. Apple cache tiers must be measured at lookup and reconstruction separately.
- Strata #409 adds experimental DGX Spark/aarch64 support; useful maturity signal, no purchase-case or P51 target change.

**Canonical numerical targets remain unchanged.**


## 2026-10-01 10:26 ET consolidation delta — mainline Flash MTP, Strata prompt-path work, exact RX 6800 anchor

### Flash-Next MTP is now mainline llama.cpp, but prefill must be benchmarked separately

llama.cpp PR #29761 merged in this window. Its published DGX Spark / Flash-Next IQ4_XS sample moves decode
**28.36 -> 43.88 tok/s (1.55x)** at **0.640 acceptance** across 24 small speed-bench prompts.

A post-merge 3-GPU report at a real ~98K prompt, Q8 target + Q4 MTP draft, 262K configured context, measures only
**~332-333 prompt tok/s** with MTP enabled. The same reporter says a non-MTP setup reached ~850 tok/s, but batching
settings also differed, so this is not a clean A/B and the maintainers are still diagnosing scaling.

Project-51 rule: every speculative configuration must report **MTP-on vs MTP-off cold PP and decode separately** at
the target context. A decode multiplier does not authorize assuming prompt processing is unchanged.

### Deep QSA runtime path remains a first-order variable

llama.cpp #29751 merged concurrently and fixes Qwen4Exp hybrid-indexer attention. On DGX Spark / Flash-Next UD-IQ4_XS,
at 131K prior-token depth it changes PP2048 from **370.71 -> 650.60 tok/s** and TG64 from **14.08 -> 21.20 tok/s**
with ub2048 (similar uplift at ub512).

Do not transfer the numbers to 5070 Ti or Apple. The durable conclusion is that deep-context QSA implementation quality
can dominate both prefill and decode enough to invalidate shallow-context extrapolation.

PR #29805 adds another boundary gate: QSA/k-pool models must be tested at **exact cache fill (`n_tokens == n_ctx`)**
because an off-by-one re-pool bound could build one pool beyond the real cache.

### Strata prompt path has two exactness-preserving optimization directions

PR #372 groups streamed native-expert gathers so an MMQ group uses one launch/wait/release instead of one per expert.
On RTX 5090 / IQ2_XS it reports ~**8.6% lower 32K prompt time** and bit-identical first-token logits under a fixed cache.

PR #374 overlaps the first chunk's PLE row fetch with embedding/layer 0 and raises PLE inflight read depth. On the same
class of box it reports **~2.9% lower 32K** and **~5.3% lower 8K** prompt time with bit-identical first-token logits.

These are mechanism evidence only. Project 51 should mine the synchronization/I/O overlap ideas but retain exact-box
PP targets until they reproduce on 5070 Ti.

### Shared expert cache remains the Strata default

Issue #369 shows `--expert-cache-per-layer` is currently incorrect on native/sized packs because per-layer cursors are
not initialized to their layer ranges and the profile fill can terminate when one layer's quota is exhausted.

The proposed fix restores correctness, but at equal ~10.9-GiB VRAM reserve the report measures shared-cache
**20.7 tok/s** versus per-layer **19.1 tok/s**. Treat the fix as correctness, not a speed path; keep shared cache as the
Project-51 default unless exact target hardware proves otherwise.

### Exact RX 6800 short decode now anchors the secondary lane

Strata PR #376 gives an exact RX 6800 physical receipt: with proper HIP release flags, Windows/HIP SDK 7.2 /
Strata 0.1.30 + the Windows HIP work / expert cache 2048 measures **28.1-28.3 tok/s** decode.

A failed first configure can poison the CMake cache so later GPU kernels compile at `-O0`; the same card then runs only
**0.24-0.27 tok/s**. The configure-cache failure mode is reproduced on Linux as well.

This does not prove long-context speed, model-quality parity, or the user's exact Linux/Ryzen configuration. It does
change one planning statement: the lower edge of the existing **~28-36 tok/s** RX-6800 lane is now physically anchored
on the exact GPU rather than wholly transferred from RX 6900 XT. The **~27-34 tok/s filled-128K** and **~220-300 PP**
figures remain inferred.

AMD qualification must record the actual HIP compile flags and rebuild provenance; a successful binary launch is not
evidence that release kernels were produced.

### Cache ownership/recurrent-state gates strengthen again

oMLX #4157 identifies a prefix-cache dedup race where a block ID could be freed/reused between lookup and refcount
acquisition, silently attaching wrong KV on restore. Atomic `block_id + expected_hash` revalidation closes it.

vLLM #53912 is older evidence updated in this window: hybrid GDN/Mamba prefix caching plus MTP can leave state written
over rejected speculative positions reachable through the prefix cache, producing occasional malformed responses.

Project-51 cache certification therefore includes concurrent store/fetch/reconstruct stress and explicitly proves that
**rejected speculative recurrent state cannot become a reusable prefix**.

### Other current signals

- oMLX #4154 rebases the Splash backend integration onto current main; M1 Max 64-GB integration exists for
  Qwen3.8-27B-Splash, but there is no Flash-Next support or clean performance receipt, so no M1 Flash target movement.
- TensorFold #188 supplies useful mixed-width sensitivity evidence on Qwen3.8-27B (KL 0.057/0.016/0.006 for 4/5/6-bit
  g64), but it is not a DASLab Flash source-fidelity result and does not change AA priors.
- vLLM #59605 shows substantial untuned skinny-GEMM headroom on DGX Spark; this reinforces software-maturity caution
  rather than changing Project-51 hardware-buy economics.
- Strata #366 remains a DFlash2 feasibility/planning PR only.
- DASLab GSQ-RCO main remains `ed59f92`; Strata/oMLX/TensorFold stable releases remain 0.1.31/0.7.0/0.6.0.

**Canonical numerical targets remain unchanged.** The only planning-text change is that exact RX-6800 short decode now
anchors the lower edge of its existing secondary range.

## 2026-10-01 07:01 ET consolidation delta — split-GEMM exactness and depth-aware Apple prefill

### Distributed/head-split GEMMs need reduction-algorithm exactness, not just algebraic equivalence

A strict-window update to Strata issue #204 reports an opt-in two-GPU GDN prompt split on 2x RTX 3090 + NVLink,
IQ3_S. Splitting GDN heads across the helper GPU improves prefill versus the same peer-tier build by:
- 8K: **2,202 -> 2,337 tok/s (+6.2%)**;
- 32K: **2,615 -> 2,809 (+7.4%)**;
- 128K: **2,696 -> 2,913 (+8.0%)**;
- decode remains ~102-104 tok/s.

The durable finding is correctness, not the 3090 speed. cuBLAS GemmEx chooses split-K based on GEMM shape, so computing
a row/output subset can use a different split-K/reduction schedule than the unsplit full projection and therefore
produce different bits. The contributor restores GDN-state identity by selecting a cublasLt algorithm whose split-K
matches the full-shape heuristic; 8K and 21K multi-chunk state hashes then match and the long gate passes.

Project-51 rule: any distributed/head/output-row split of a dense projection must either:
1. pin an arithmetic/reduction schedule equivalent to the reference full-shape path; or
2. explicitly certify the altered arithmetic against source/reference behavior.

"Same mathematical GEMM" is not sufficient for source-equivalence. The numeric 3090 gains do not transfer to M1/TB4.

### Strata PR #363 removes fixed verify-window PCIe launch waste, with small end-to-end gain

New PR #363 (10:59:28 UTC) reduces the grouped-expert launch footprint for the verify window's PCIe arm and fuses
SwiGLU + q8_1 work. On RTX 4080 SUPER / IQ3_S:
- empty PCIe grouped call: **16.51 -> 4.01 us**;
- one-group call: **19.11 -> 10.71 us**;
- VRAM call essentially unchanged;
- GPU PCIe-expert stage drops about **0.67 -> 0.20 ms/window**;
- deterministic end-to-end decode improves about **1.1%**, while ordinary request TG remains within large
  request-to-request scatter.

The PR includes bitwise grouped-kernel parity across the supported quant combinations. This is useful verifier-overhead
mining evidence but does not move the 5070-Ti TG target.

### Apple pipeline memory accounting must count only state-bearing layers

oMLX PR #4147 (open) fixes hybrid-model KV accounting that charged every layer as full attention. On a two-node
M5 Pro 64-GB pipeline running Qwen3.8-27B-oQ4e-mtp:
- 262K planner KV reservation falls from **~49 GB/node to ~17 GB/node**;
- a **245,515-token** needle prompt is admitted and answered **3/3**;
- minimum free memory stays ~31% on both nodes, swap flat.

This is the dense 27B hybrid family, not Flash-Next, so there is no numeric transfer to the dual-M1 Flash target.
The transferable rule is geometric: memory admission must charge KV only to full-attention/KV-bearing layers and
recurrent/QSA state according to their own actual storage geometry.

### Deep Apple prefill needs depth-aware command-buffer sizing

oMLX PR #4149 (open) reports the same two M5 Pro 64-GB / TB5 pipeline:
- fixed 1,024-token prefill chunks pass ~124K but a 245K prompt kills one rank via Metal watchdog ~19 minutes in;
- fixed 512 avoids the deep failure but cuts shallow standalone PP roughly **680 -> 380 tok/s**;
- a depth-aware bound keeps 1,024 through ~150K and drops to 512 deeper; the 245,515-token needle then passes **3/3**
  with no rank death.

No M5->M1 throughput percentage is transferred. Project-51 Apple qualification must measure command-buffer duration
as a function of **chunk size x current KV/QSA depth** and allow chunk size to shrink with depth rather than selecting
one shallow-optimal fixed chunk.

### Saved-state success codes are not resume correctness

New llama.cpp issue #29798 is OpenCL/Adreno-specific: q8_0 KV state restore reports the full token count loaded, but
writes through q8_0 tensor views are silently dropped, so the resumed decode sees an empty cache and produces garbage.
CPU q8_0 and OpenCL f16 restore correctly.

This does not affect the current CUDA/Metal lanes directly. It reinforces the existing Project-51 checkpoint rule:
every save/restore path must prove **resume output/state identity versus fresh prefill**; a successful load return value
or correct token count is not certification.

### Strict-window exclusions / negatives

- llama.cpp PR #29761 adds Flash-Next MTP, but its latest update is **11:01:35 UTC**, 32 seconds after this watch's
  11:01:03 cutoff; that update is deliberately excluded and belongs to the next watch.
- DASLab GSQ-RCO main remains `ed59f92`; no new checkpoint/allocation/benchmark in this window.
- Strata latest release remains 0.1.31.
- oMLX remains 0.7.0; PRs #4147/#4149 are open.
- TensorFold remains 0.6.0.
- no strict-window TurboQuant-MLX, MoEspresso, Ishizuki or mlx-serve release/commit affecting Project 51.

**Canonical and secondary numerical targets remain unchanged.**


## 2026-10-01 06:28 ET consolidation delta — Strata 0.1.31, exact RDNA2 anchor, 1M stretch context, Apple long-context concurrency

### Strata production baseline advances to 0.1.31+

Strata 0.1.31 (commit `9259cad4cfa3543cd3b8decab5962672b968c649`, published 05:13:47 UTC)
supersedes 0.1.30 for new Project-51 runs.

For Project 51, the important changes are:
- the #266 late-finalizer/request-status race is fixed;
- Windows verify-stall watchdog exit now releases GPU-side waits before process termination (#267);
- Linux multi-GPU again pins the full expert arena instead of inheriting the Windows 8-GiB cap (#253);
- Windows gets opt-in `STRATA_ARENA_PIN_GIB=auto`, bounded by the shared-GPU-memory budget (#243);
- tagged checkouts now install their own engine/model revisions/dependencies instead of silently taking newest pieces (#214);
- Windows GGUF expert loading is roughly 2x faster on the maintainer's path;
- the experimental mapped/file-tier architecture can run Unsloth UD-Q4_K_XL, a ~111-GB 4-bit Flash-Next artifact,
  on an RTX 5070 12 GB + 64 GB host at roughly 7-8.5 tok/s with a 40-GiB resident-RAM budget.

Release qualification says fixed-cache outputs remain byte-identical to 0.1.30 on Q2_0/IQ3_XXS/IQ3_S/Coder across
nine rounds, and the 64K server sequence again passes retrieval, prompt reuse, tool call, cancellation and sampled reply.

**0.1.31 is the new qualification baseline, not a completed certification.** The user's exact 5070 Ti + 64-GB box
still needs the >=8 h zero-stall soak, rapid abort/retry concurrency, watchdog recovery and Windows pin-budget admission
tests. The release closes known implementation holes; it does not substitute for exact-box reproduction.

### Exact RDNA2 evidence materially upgrades the RX 6800 secondary lane

Strata PR #311 was created just before the previous hard boundary and updated inside this window, so classify its
performance receipt as **RECOVERED CURRENT / UPDATE**, not NEW.

It adds experimental gfx1030 support and reports on:
- RX 6900 XT 16 GB (gfx1030);
- i7-13700KF, AVX2;
- 63 GB RAM;
- NixOS / ROCm 7.2.3;
- Swift 1.5 IQ3_XXS;
- genuine 131,072-token context, 32K resident KV.

Measured:
- **38-42 tok/s decode with the default 15 CPU-pool workers, even with the 131K context full**;
- 35-37 tok/s with 8 workers; oversubscribing to 24 workers falls to 26-28;
- **246 tok/s prefill at ~2K**;
- **330-339 tok/s** with auto 8,192-token chunks at ~8K/16K;
- decode after the 16K prefill reaches 45.5 tok/s.

This invalidates the previous 8-18 tok/s planning range for the user's RX 6800. The exact card is one tier down from
the 6900 XT (fewer CUs/lower compute, similar memory bus), and the user's Ryzen generation is unspecified, so do not
copy 38-42 directly.

Revised RX 6800 + 64-GB DDR4 planning lane:
- short-to-128K decode: **~28-36 tok/s**, planning center ~32;
- 128K filled-context decode: **~27-34 tok/s**;
- cold prefill: **~220-300 tok/s** order-of-magnitude;
- 64K-128K is now a realistic first-class operating range rather than merely a feasibility experiment.

Confidence is still moderate rather than high because:
1. the PR is open/unmerged;
2. the exact receipt is RX 6900 XT, not RX 6800;
3. it uses Swift 1.5 IQ3_XXS rather than the canonical DASLab base IQ3_XXS;
4. setup's gfx1030 path and quality benchmarks were not validated in the report.

### Exact 5070 Ti reaches 1M context experimentally; native 262K remains the production target

New Strata issue #348 uses the same GPU class as the Project-51 NVIDIA target:
- RTX 5070 Ti 16 GB;
- Ryzen 7 7700;
- 93 GB host RAM;
- IQ3_XXS;
- INT8 streamed KV with 32K resident;
- MTP S=4;
- YaRN x4 to a 1,048,576-token window.

Physical result:
- 1,037,660-token prompt reads from zero in **626 s = 1,657 tok/s**;
- pinned KV is **12.38 GiB at ~1M** versus 3.09 GiB at 262K;
- GPU VRAM stays flat under streaming;
- retrieval is **8/10 at ~1.04M** on the issue's adversarial exact-value test.

Quality caveat is decisive:
- at ~156K, the scaled run scores **6/10** where the prior unscaled run scored **8/10**;
- the reporter therefore keeps production unscaled at 262K.

Project-51 interpretation: 1M is now physically credible as a dedicated long-document **stretch lane** on 16-GB
Blackwell, but it does not promote the headline context. Native unscaled 262K remains the production target because
YaRN changes model behavior even inside the trained range. The 93-GB host also prevents transferring 1M fit to the
user's 64-GB host.

### oMLX long-context batched Lightning-MTP can become net-negative

oMLX issue #4141 measures Qwen3.8-Flash-Next oQ4e on M5 Ultra at a 100K shared prefix + 2K private suffix:
- 1 session: MTP **115.5** vs no-MTP **93.5 tok/s**;
- 2 sessions: **107.1 vs 124.1**;
- 4 sessions: **123.2 vs 161.3**;
- 8 sessions: **150.9 vs 228.3** aggregate.

The dominant mechanism is ragged rollback. At eight ~100K rows, each verify cycle's cache finalization physically rolls
the whole K/V and QSA indexer banks:
- verify attention: ~33.1 ms;
- rollback: **~110.3 ms**.

A temporary "MTP only for singleton" switch restores roughly 122.7 / 155.5 / 223.6 tok/s at 2/4/8 sessions.

This does not move the Project-51 B1 headline, but it adds a hard multi-agent rule: **long-context MTP must demonstrate
aggregate gain at B2/B4/B8 after rollback/state-commit costs; singleton wins do not authorize batched speculation.**
An O(1) logical rotation/offset scheme is the right mechanism class; copying the whole retained bank per cycle is not.

### oMLX PLE-offload warmth can dominate apparent TG on capacity-limited Macs

Issue #4140 on an M3 Ultra 96 GB / oMLX 0.7.0 / Flash-Next oQ4e-mtp reports:
- fresh short requests with PLE offloaded: roughly **62.2-64.6 tok/s** initially;
- byte-identical immediate replays: **80.1-80.8 tok/s**;
- fresh-request slowdown tracks process page-ins very closely in that experiment.

The report does not yet prove every page-in is a PLE decode fault, but it establishes a strong confounder for
Project-51's 64-GB Apple lane: an offloaded model can have materially different **cold-PLE** and **warm-PLE** decode
rates even when prompt shape is tiny.

Apple qualification therefore records:
1. cold/fresh PLE residency state;
2. warmed identical-replay state;
3. page-in/read telemetry where available;
4. B1/B2/B4/B8 separately.

Do not compare an MTP-on warm replay to an MTP-off cold request and call the delta speculative speedup.

### New Strata low-cost and multi-GPU stretch receipts stay outside canonical targets

- Issue #359 reports 3x RTX 3090 + IQ4 at a 1M configured context: >120 tok/s at short context and ~60 tok/s near 1M.
  It is a single community report without a controlled prompt-depth/quality protocol, so it is stretch evidence only.
- The pruned-Q2 8-GB experiment reports further engineering to ~35 tok/s and an estimated 400+ tok/s prefill, and
  speculates 6-GB VRAM may be possible. Quality remains the unresolved question; no AA credit.
- Issue #349 reports RX 9070 16 GB + 64 GB host running Swift IQ3_XXS around 55-70 tok/s at ordinary agent depths,
  reinforcing AMD viability but not transferring numerically to RDNA2.

### Strata-side experimental work worth tracking, but no target credit yet

- PR #353 rebases NVFP4 routed experts onto 0.1.31. On RTX 5090, an 8K prefill reports **4,231 tok/s W4A8** and
  **4,583 W4A4**, same decode, but run-to-run divergence can occur because CPU/GPU NVFP4 expert rows are only
  tolerance-equal and expert-miss ownership is timing-dependent. Fixed expert-cache size is required for identity tests.
- PR #293 adds opt-in Hadamard rotation to INT8 KV. Attention-output error improves in one local microtest, but
  end-to-end first-token KL **improves for NVFP4 and worsens for IQ2_XS**. Keep rotation model/quant-specific and
  quality-gated; lower local tensor error is not sufficient.
- PR #282 raises auto prefill chunks to 16K/32K. On RTX 5090 it reports ~15% faster 32K IQ2_XS prefill and much larger
  gain on an NVFP4 pack, but one-vs-four chunks can change summation order and generated tokens. It therefore needs
  source-equivalence qualification before production credit.
- Issue #347 is only a request to explore DFlash2 support; no implementation or benchmark exists yet.

### Other strict-window mechanisms

- SGLang PR #41175's full optimization series reports B200x4 Qwen3.8-Flash-Next NVFP4 NEXTN TPOT 1.6936 ms vs
  normal decode 4.1270 ms (590 vs 242 tok/s derived), with real AIME-style integration accuracy 95.00% vs 95.42%.
  The performance run uses simulated acceptance 3.3, so this is datacenter mechanism evidence, not consumer transfer.
- vLLM issue #59534, intentionally excluded by eight seconds from the prior watch, reports a FlashAttention
  per-call K/V-view reconstruction regression; caching those views cuts TTFT p50 12-16% in a local 8xH100 patch.
  Low transfer to P51, but another example that host-side bookkeeping can matter for short prefill.
- DASLab Flash-Next GSQ-RCO still points at `ed59f92`; no new checkpoint/allocation/benchmark in this window.
- TensorFold remains 0.6.0, oMLX remains 0.7.0, and no material strict-window TurboQuant-MLX/MoEspresso/Ishizuki
  release changes the canonical targets.

**Canonical 5070-Ti and dual-M1 numerical targets remain unchanged.** The material planning change is the RDNA2
secondary lane and the runtime baseline/gating updates above.


## 2026-09-30 23:57 ET consolidation delta — Victoria/QAD lane, MTP-asset integrity, 64-GB admission reality

### Victoria creates a separate post-compression-recovery lane, not a DASLab-fidelity result

The rmonsurate/Victoria release is now tracked as an explicit **capability-per-byte / post-compression-training**
control alongside the pure post-training-quantization ladder.

Victoria starts from Qwen3.8-Flash-Next, removes 44% of routed experts (512 -> 288 per layer) with REAP, keeps the
same 5.9B active parameters/token, then retrains the compressed model at 4-bit using quantization-aware distillation
on 128M tokens of coding/tool-use data. The published builds are different checkpoints:
- NVFP4: 48.0 GiB of weights including the draft head + 95.4 GiB n-gram lookup table;
- GGUF Q4_K_M: 49.17 GiB resident weights, with a smaller 107.20-GB download using an 8-bit lookup table.

Quality is strong but clearly not source-equivalent:
- NVFP4 Terminal-Bench 2.1: **70.04% avg@3** (75.3 / 68.5 / 66.3), HumanEval **97.0%**;
- GGUF Q4_K_M Terminal-Bench: **75.28% (67/89)** vs original Flash-Next **88.76% (79/89)**,
  i.e. **84.8% of the source Terminal-Bench score**; HumanEval **93.2% avg@5**.

The draft-head speed result must be decomposed correctly. On one B300:
- no draft head: **134.7 tok/s**;
- pruned/unretrained draft head: **269.3 tok/s**, 64.1% acceptance;
- retrained shipped head: **279.6 tok/s**, 67.6% acceptance.

Thus most of the 2.08x gain comes from having MTP at all; retraining the head adds about 3.8% over the unretrained
pruned head. On one M3 Max 128 GB, the GGUF head moves ~26.8-27.8 -> 34.3-38.0 tok/s with 70.4% acceptance.
Those numbers are **not** transferred to M1 Max.

Project-51 interpretation:
- DASLab IQ3_XXS remains the primary **source-fidelity** hypothesis.
- Victoria becomes a secondary **useful-capability-per-byte** arm.
- After the pure PTQ ladder is frozen, run the same AA/agent/retrieval/tool suite on Victoria and report
  source-fidelity and absolute capability separately.
- A future research lane may combine sensitivity-aware pruning/allocation + GSQ/RCO + post-quant QAD + a final-model
  draft-head retrain, but no canonical hardware or AA target is assigned yet.

### Strata #327 adds a mandatory MTP-asset integrity gate

A Windows RTX 5090 Laptop 24-GB report found a silent corruption path in `tools/mtp_fetch.py`: an HF mirror ignored
the HTTP Range header and returned HTTP 200/full-file data, while the downloader saved the first requested-length
bytes. 20 of 31 fetched `mtp.*` blobs therefore contained safetensors header/unrelated shard bytes rather than the
requested tensor ranges.

The failure was deceptive:
- the main model loaded and decoded normally;
- file sizes matched the requested lengths;
- the local manifest hash matched the **wrong downloaded bytes**;
- default logs showed `drafts accepted 0 of 0`, and forced windows showed 0/765 accepted;
- corrupt draft tensors contained NaNs/infs.

After re-fetching the affected ~110 MB:
- forced-window test: **42.7 -> 69.9 tok/s**, acceptance 0 -> 31.8%;
- ordinary serve: Q2_0 **93.5 tok/s** with 44-54% acceptance; IQ3_XXS **77.4 tok/s** with 59-71% acceptance.

Project-51 MTP qualification must therefore validate the **artifact**, not merely runtime code:
1. range fetches must prove HTTP 206 / correct `Content-Range` (or use full-file verified extraction);
2. record authoritative source revision plus expected tensor byte ranges/hashes;
3. sanity-scan draft tensors for finite scales/norms before serving;
4. distinguish **0 offered** from **0 accepted** in telemetry;
5. do not diagnose low acceptance as a verifier/model problem until draft assets pass integrity checks.

This joins draft-vocabulary coverage and width-invariant target arithmetic as a precondition for any MTP speed claim.

### TensorFold 0.6.0 still overpromises Flash-Next fit on one real 64-GB Mac

Issue #95 has a strict-window M5 Pro 64-GB retest on TensorFold 0.6.0. With Flash-Next, PLE on SSD and a 24-GiB
SSD-expert pool, the server advertises a 65,536-token window, but:
- after a 15-token warm request, a 65,380-token prompt is refused with a reported fit around 50,624;
- a 50,618-token prompt can be admitted, prefill for ~4.5 minutes, then be refused with a lower fit estimate;
- as the first request, a 65,383-token prompt can also prefill for ~5.8 minutes and then be refused;
- a 34K turn does resume correctly in ~2.0 s.

The reporter identifies one contributor: sparse-attention indexer memory is profiled per valid token while the cache
allocates in 256-position capacity steps, so a tiny request can inflate the remembered per-token cache cost by ~2.8x.
That alone does not explain the final-chunk refusal.

This is M5 Pro rather than M1 Max, but the bug is memory-accounting logic. Project-51 64-GB Apple certification must
therefore test **window-edge admission as the first request, after a tiny request, after a retained conversation, and
through final prefill completion**. An advertised context window is not capacity evidence until all four agree.

### TensorFold Flash-Next CUDA does not yet share a common agent system prefix across new conversations

Issue #169 on one DGX Spark gives a useful agent-workload control. With a common ~30.7K system+tool block and ~35.7K
total prompts:
- Flash-Next CUDA 0.5.0/0.6.0: new conversation gets **0 cached**, ~23.5 s; next turn of the same conversation resumes,
  ~0.24 s;
- Qwen3.8-27B: new conversation reuses ~30.7K, ~4.2 s; same-conversation next turn ~0.4 s.

Flash-Next currently remembers admitted prompt ends, not message-start/system-prefix states. This directly supports
Project-51's existing rule that a logical common prefix does not earn multi-agent capacity/latency credit unless the
runtime actually checkpoints/shares it. Add an explicit **new-conversation common-system-prefix reuse** test.

### Strata 0.1.30 still has independent multi-session server-state evidence

Issue #328 reproduces `KeyError: 'tail'` on Strata 0.1.30 with multiple OpenAI sessions (RTX A4500, Linux,
IQ3_S/262K). The engine remains healthy; an HTTP streaming handler loses bookkeeping state. This is consistent with
the already-tracked request-finalization/status-ownership family around #266. It reinforces the decision not to
promote 0.1.30 as agent-production-safe before the 0.1.31 request-id fix is released and reproduced.

### New artifact-compatibility issue is third-party specific, canonical DASLab unaffected

Strata #326 shows OrcaRouter IQ3_XXS `--compat-bf16` packs can become unloadable from 0.1.25 onward because the
packer writes `blk.1.ple_key.weight` as BF16 while native loading now treats IQ3_XXS/IQ4_XS PLE keys as native and
skips/rejects that packed row. The official GSQ-RCO files use the canonical native PLE path and are not implicated.
This reinforces the tensor-kind/file-interpretation gate rather than changing the DASLab target.

### Independent IQ2_XS coding run is fast but illustrates why physical speed cannot stand in for capability

Strata #316 reports a reproducible RTX 4090 / 64-GB Linux agent run on original Flash-Next IQ2_XS:
- 37,449 output tokens across 80 responses;
- weighted generation rate **166.36 tok/s** using Strata's predicted decode time, not whole-request wall throughput;
- 84.9% MTP acceptance;
- 12.8-minute harness time.

The generated browser game executed but was rejected for poor physics/game feel. This is one uncontrolled task and
used reasoning off, so it is **not** an IQ2_XS quality score. It is a useful reminder that very high agent-loop
throughput does not establish coding/agent quality.

### Apple/Metal compiler correctness warning is M3-specific, not transferred to M1

MLX issue #4603 reports a deterministic macOS 27.0 / M3 Ultra runtime-Metal-compiler bug where a custom 6-bit
`mx.fast.metal_kernel` using `MathModeSafe` returns entire wrong rows. The same source is exact under Relaxed/Fast,
on M2 Max, and when shader validation perturbs code generation. An MLX-free Metal reproducer points to the OS
compiler rather than MLX.

No M1 failure is demonstrated, so there is no M1 target movement. It does reinforce the Project-51 requirement that
custom Metal kernels be validated **on the exact hardware + OS + compiler mode**, with row-level arithmetic controls;
the name "Safe" is not a correctness proof.

### Low-transfer upstream signals

- vLLM PR #59214 merged at 03:40:55 UTC and adds B200/SM100 Qwen4Exp skinny-BF16 GEMM plans; many M=1-8
  microkernels improve roughly 1.2-2.7x vs cuBLAS. This is useful small-row specialization evidence, not a numerical
  transfer to sm_120 or Apple7.
- SGLang's strict-window commits are not material to the consumer Flash-Next targets.
- A vLLM FlashAttention KV-view-cache issue was created at **03:57:25 UTC**, eight seconds after this watch cutoff,
  and is deliberately excluded from this window.

### Strict-window source state

Strata latest release remains **0.1.30**; 0.1.31 is still not released by the cutoff.

TensorFold latest release remains **0.6.0**.

oMLX latest stable remains **0.7.0**; no strict-window performance/correctness commit relevant to the Flash target.

DASLab Flash-Next GSQ-RCO still has main at `ed59f92`; no new checkpoint/allocation/benchmark landed in the strict
window. TurboQuant-MLX, MoEspresso and Ishizuki likewise have no material strict-window update.

**Canonical numerical Project-51 targets remain unchanged.**


## 2026-09-30 19:19 ET consolidation delta — TensorFold 0.6.0, deep-QSA prefill, artifact-kind validation

### TensorFold 0.6.0 lands as a meaningful experimental-runtime baseline

TensorFold 0.6.0 (commit `c4646171139ee8a3c38103eaa1699dad226ec12b`, release published 21:31:05 UTC)
adds several mechanisms relevant to Project 51, but does not replace oMLX 0.7.0 as the stable Apple comparison baseline.

Relevant release evidence:
- CUDA now includes RTX 40 / sm_89; on one RTX 4090 the 27B runs a 40,182-token DFlash2 window with drafted replies
  equal to serial, fresh/resume equivalence, 2.4-2.6k tok/s prompt fill from 2K-32K, and 64-86 tok/s decode.
- Under `--parallel`, Flash-Next prompts can fill inside live decode rounds rather than globally stopping replies;
  a DGX Spark report gives 2.8-3.1x lower first-token delay, while an M3 Ultra queueing example drops median short-job
  TTFT from 113 s to 9.9 s.
- More engines retain/resume prompt state; an 18.7K Flash-Next resend is reported 8.3 s -> 0.08 s with a fresh run's reply.
- CUDA prompt arithmetic defaults to bf16 rather than FP8; on the 27B the release reports KL 0.0031 vs an fp32
  reference for bf16 prompt rows, versus 0.0624 for FP8.
- On pre-M5 Macs, one-stream copy windows widen and concurrent Flash-Next rounds use matrix units. An M3 Ultra edit
  is reported 190 -> 233 tok/s. This is mechanism evidence only, not an M1 numerical transfer.
- Flash-Next CUDA NVFP4 is reported 4.9-7.1% faster decode and 15-16% faster 2K-16K prompt fill, bit-identical.

0.6.0 therefore strengthens the implementation path around concurrency, resumed state and pre-M5 matrix usage.
It does **not** move the dual-M1 40-TG/400-PP target because there is still no exact dual-M1-Max, filled-128K receipt.

### Deep-context pre-M5 QSA prefill needs its own certification gate

mlx-serve issue #658 gives a same-box M3 Ultra comparison at depth:
- cold 59.7K prefill: mlx-serve ~1,190 tok/s, oMLX ~1,230;
- 60K -> 99K suffix prefill: mlx-serve ~570 tok/s, oMLX ~1,190;
- decode at 99K remains similar, ~56-67 vs ~64 tok/s.

The reporter attributes the collapse to mlx-serve's non-NAX pre-M5 path retaining an 8,192-key gather floor / older
QSA kernel beyond the sparse transition, while oMLX 0.7.0 carries sparse prefill gather and wider native QSA tiles
across Macs. The exact root cause is not yet maintainer-confirmed, so transfer the **test shape**, not the diagnosis.

Project-51 Apple PP qualification must include both:
1. genuinely cold long prefill; and
2. **deep suffix prefill after a retained 60K+ prefix**, e.g. 60K -> 96K/100K.

A runtime that meets the cold PP target but collapses after entering the sparse-QSA regime does not pass the Apple
prefill gate. This is especially relevant to a custom M1 implementation, where M5/NAX-specific fast paths cannot be assumed.

### TensorFold's refused-checkpoint bug is confirmed to persist in 0.6.0

The TensorFold maintainer confirmed issue #155 still applies to 0.6.0: if `allow_checkpoint` refuses a boundary
capture, it is silently skipped and the normal spill path never sees it. The requested upstream fix has three
important properties:
- log one refusal reason per request;
- hand spill writes to a bounded asynchronous writer instead of blocking the engine/decode thread;
- test that a refused boundary capture spills and the next turn resumes from disk with the same token SHA as fresh prefill.

Project-51's resident-agent gate therefore remains strict: capture refusal is a first-class persistence event, not
an eviction detail.

### RTX 4090 gives a strong consumer 24-GB Strata throughput/cache receipt, not a long-context ruler

Strata issue #307/#308 reports native Windows / RTX 4090 24 GB / i9-13900K / 64-GB DDR5 with a 128K-configured
Flash-Next setup:
- IQ2_XS: 106.1 tok/s whole request, ~115 peak, 95.5% expert-cache hit;
- IQ3_XXS: **98.1 tok/s whole request**, ~120 peak, 91.9% expert-cache hit;
- IQ3_XXS generated 11,485 tokens in 118 s on the reported close-reading task.

This is useful evidence that a 24-GB card can keep enough of IQ3_XXS hot to sustain ~100 tok/s-class real requests.
The actual prompt depth is not stated, so **128K configured context must not be read as 128K filled context**. No
5070-Ti TG target moves.

### Pruning buys extreme hardware cost at selective capability loss

Follow-up to Strata issue #298 adds preliminary quality:
- pruned Q2 Flash-Next on RTX 2060 8 GB: HumanEval **92.7%** over 164 problems at ~28.9 tok/s;
- GPQA-Diamond: **25% on only 20 questions** at ~30.9 tok/s;
- the reporter's Qwen3.6-35B-A3B control scores 35% on the same tiny GPQA subset.

The sample is too small for a stable GPQA estimate, but it demonstrates the expected trade: expert pruning can
preserve a narrow capability (coding) while damaging another (hard reasoning). Do not use the pruned-Q2 result as
evidence for unpruned DASLab IQ3_XXS quality.

### New Strata artifact-kind bug does not hit the official DASLab IQ3_XXS artifact, but becomes a loader-certification test

Strata issue #303 reports an Unsloth UD-IQ3_XXS artifact whose `blk.1.ple_conv1d.weight` is F32 while the runtime
passes its raw bits to an F16 convolution kernel, producing coherent-looking execution infrastructure but garbage
model output. Synthetic F16 parity fixtures all pass, illustrating that kernel parity alone cannot validate file-format
interpretation.

The official ISTA-DASLab Flash-Next GSQ-RCO allocation for IQ3_XXS explicitly lists
`blk.1.ple_conv1d.weight: F16` (commit `fb6d866`), so this exact F32/raw-F16 defect **does not apply to our canonical
DASLab IQ3_XXS checkpoint**. The same is true in the published IQ2_XS/Q2_0 allocations.

Even so, Project-51 source-equivalence certification should record and assert the actual GGUF tensor kind/byte count
for critical PLE/GDN/QSA tensors before runtime execution. A green synthetic parity suite is not enough.

### Linux layer-split pinning evidence reinforces platform-specific host-memory policy

Strata issue #306, on an older 0.1.24 2x V100 / 62-GB Linux configuration, reports an unconditional 8-GiB host-pin
cap (introduced for WDDM) reducing 28K prefill from 932 tok/s single-card to 378 tok/s in the split; removing the cap
on Linux and allowing full arena pinning yields 976 tok/s and 35.2 tok/s no-MTP decode. The same report also finds
prompt-borrow sizing inconsistencies.

This is old-release / manually patched / different-hardware evidence, so it does not become a Project-51 speed
number. It reinforces the existing rule: host-registration policy must be OS/topology-specific and Linux memlock
limits must be measured rather than inheriting Windows/WDDM caps.

### oMLX batch-realignment short-stop signal remains unresolved

oMLX issue #4036 receives stronger corpus evidence on 0.7.0rc1-era M1 Max agent traffic: 1,038 generation-row
realignment warnings and 7 of 10 <=10-token long-prompt completions occurring within 5 s of a realign. However, a
40-iteration targeted stress loop produced 203 realigns and zero short stops, and a real agent request with the same
cached-prefix/small-suffix shape also completed normally. Realignment is therefore correlated but not demonstrated
causal.

For Project-51 Apple agent testing, retain a simple invariant: suspiciously short `finish_reason=stop` completions on
large prompts must be preserved with scheduler/cache traces and raw model text; do not silently score them as model
behavior until runtime truncation is excluded.

### Strict-window negative / DASLab state

The official DASLab Flash-Next GSQ-RCO commit history still tops at `ed59f92`; no new checkpoint, allocation,
source-paired long-context result or benchmark landed in this strict window. The official IQ3_XXS PLE dtype check
above is **RECOVERED CURRENT** evidence from the existing `fb6d866` allocation, not a new DASLab release.

No Project-51-relevant strict-window update was found in TurboQuant-MLX, MoEspresso or Ishizuki. MLX core itself had
no relevant new Flash-Next change in the window.

**Canonical numerical targets remain unchanged.**


## 2026-09-30 16:42 ET consolidation delta — Strata 0.1.30, exactness mode, state-retention gates

### Strata production baseline advances to 0.1.30+

Strata 0.1.30 (commit `30ec18ec7094550fcc594fd948220d511d80464e`, release published 17:50:57 UTC)
supersedes 0.1.29 for new Project-51 runs. It keeps fixed-cache output byte-identical to 0.1.29 on the four release
quants while adding several mechanisms directly relevant to the project:

- short 1K-4K prompt streaming uses 1,024-token chunks and is reported +17-28% on the maintainer's RTX 5070;
- layer-split cards keep only their own session state and borrow only their own prompt-cache tail;
- low-RAM mode gains a resident variant that copies the non-GPU expert complement into ordinary RAM;
- bounded multi-conversation caching can park several conversations in RAM and avoid full prompt rereads;
- AMD RDNA4 support lands, and the gfx1100 HIP verify failure reported against 0.1.29 is confirmed fixed on 0.1.30;
- most importantly for certification, `STRATA_IQ_MT_MIN=1` makes native i-quant CPU expert arithmetic width-invariant
  so target outputs no longer depend on the speculative verify width.

The width-invariant mode costs roughly 1-3% decode on IQ3_S/AVX-512 in the maintainer's test; IQ3_XXS was reported
around +3% and other arms were within noise. For Project-51 AA/source-equivalence/MTP certification this mode now
replaces the older broad `STRATA_NO_IQ512/256/IQ4NL` workaround as the preferred exactness control.

The 1K-4K prompt gains do **not** move the 32K/64K/128K/262K cold-PP centers. They are a short-prompt optimization,
not a new long-context ruler.

### Stability gate remains open; the failure taxonomy is now more precise

Issue #251 was closed after the maintainer clarified that its 13.2K hang was in the **batched prompt path**, not the
verify window: the logged verify-window position belonged to the previous request. That prompt path changed in
0.1.30, but the reporter has not yet provided a 0.1.30 retest. Keep repeated cold long-prompt starts in the soak.

Issue #266's abort/immediate-retry race is confirmed: the old request releases the queue lock before its `finally`
cleans shared status, allowing it to clear the next request. The maintainer says 0.1.31 will give each request an id
and ownership-scoped cleanup. Until a released build is verified, rapid abort -> immediate retry remains mandatory.

Issue #267 adds a Windows safety consequence to verify-window stalls: on one RTX 4080 SUPER / 0.1.24 run, the watchdog
killed the process while GPU kernels were still spinning on host-mapped flags and the device remained lost until a
physical power cycle. The maintainer says 0.1.31 will bound the final wait and release all flags before watchdog exit.
Do not treat watchdog recovery as safe until that behavior is reproduced on a released build.

Issue #243's Windows pin-budget failure is also assigned a 0.1.31 fix: cap sliced host registration below the shared
GPU-memory budget and honor `STRATA_ARENA_PIN_GIB`. This remains pending, not a 0.1.30 qualification result.

### AMD HIP gets a useful 0.1.30 recovery receipt

Strata #273 reproduces a 0.1.29 gfx1100 RX 7900 XTX failure in the first verify launch, then confirms the same box and
Coder IQ1_M pack serve successfully on 0.1.30. With a 64K window and INT8 streaming KV, the reporter measured:
- prefill from 98 tok/s at 467 tokens to 856 tok/s at a 49K prompt;
- decode 17.7 tok/s at 467, 46.0 at 6.7K, 60.5 at 26.8K, and 35.4 at 49K;
- 93.3-97.1% expert-cache hit with 17.42 GiB of experts resident in 24-GB VRAM;
- OpenAI and Anthropic endpoints plus a tool-call smoke test working through 49,005 prompt tokens.

This strengthens the AMD runtime case but does not numerically transfer to RDNA2/RX 6800.

### An 8-GB consumer-GPU pruning result pushes the cost floor lower, quality unknown

New issue #298 reports a community-pruned Q2 Flash-Next variant on an RTX 2060 8 GiB at about **30 tok/s decode** and
**150 tok/s prefill**, with roughly **17.6 GiB resident system RAM** and a 128K context. The remaining ~26.8-GiB PLE
can be served from NVMe. The reporter explicitly says coding quality versus Qwen3.6-35B is still under test.

Treat this as a striking cost/capacity proof-of-concept, **not** a frontier-quality receipt and not evidence for the
unpruned DASLab IQ3_XXS AA prior.

### Apple capacity and runtime routing updates

oMLX issue #3917 now has a 0.7.0 receipt on an M4 Max 64-GB machine: the reporter can complete the full 256K context
benchmark for Qwen3.8-27B oQ6e-mtp using the new aggressive memory tier. The balanced tier spends long stretches near
its soft cap and makes little prefill progress. This is a strong 64-GB Apple capacity receipt for the 27B family,
not a Flash-Next 125B or exact-M1-Max throughput result.

oMLX issue #4132 proposes managing Splash/splash-m1 as a per-model backend. The implementation is reported working on
an M1 Max for Qwen3.8-27B/Qwen3.6-35B-A3B. This is interesting for the M1 fleet but does not yet serve Flash-Next, so
it earns no headline target credit.

### Resident-agent correctness gets a concrete negative test

TensorFold issue #155 shows that under memory pressure, a boundary checkpoint capture can be refused and silently
dropped before it ever reaches the configured SSD spill callback. The request completes, but the next turn has zero
resume coverage and cold-prefills the entire conversation; reported 89K-179K conversations then took 231-496 seconds
to rebuild on an M3 Ultra.

Project-51 resident-agent certification must therefore test **checkpoint-capture refusal**, not only eviction:
a refused checkpoint must either spill durably or fail/report loudly. Silent loss followed by a full hidden re-prefill
does not count as retained/resumable agent state.

TensorFold 0.5.0 also resolves the earlier two-Spark TP2 startup hang from issue #107; that is stability evidence for
the Spark lane, not enough to alter the current buy/no-buy economics.

### Other strict-window signals

SGLang issue #41919 publishes a careful B200 TP1 NVFP4 Qwen3.8-Flash-Next benchmark and GSM8K run. It is useful as a
datacenter throughput/reference point but does not transfer to consumer hardware targets.

DASLab's Flash-Next GSQ-RCO model history is unchanged: latest main commit remains `ed59f92`; no strict-window
checkpoint, RCO allocation, source-paired long-context result, or new benchmark landed. TurboQuant-MLX, MoEspresso,
mlx-serve and Ishizuki likewise have no Project-51-relevant strict-window update.

**Canonical numerical targets remain unchanged.** This delta promotes runtime baselines and exactness/state-retention
gates; it does not move 5070-Ti PP centers, dual-M1 40-TG/400-PP goals, AA priors, or the K6/V4 prior.


## 2026-09-30 12:39 ET consolidation delta — corrected AMD long-context MTP result and RX 6800 secondary lane

### vLLM #59448 correction strengthens the long-context MTP mechanism case

A 16:38:43 UTC correction to issue #59054 replaces the earlier short-sample 32K serving number for PR #59448.
On the same gfx1151 / Qwen3.8-27B / MTP-k=3 setup, steady-state measurement over 160 generated tokens with the first
five steps excluded gives:
- stock 2D verify gate: **581 ms/step, 3.2 accepted tokens/step, ~5.5 tok/s**;
- corrected 3D verify + masked-segment guards: **162 ms/step, 3.3 tokens/step, ~20.5 tok/s**;
- no speculative decoding: **92 ms/step, 10.9 tok/s**.

Thus the corrected kernel changes MTP from roughly a 2x loss into a **~1.9x steady-state gain over no-spec at 32K**
on that AMD RDNA3.5 box. The earlier statement that fixed MTP remained slower than no-spec at 32K is retired.
This remains architecture/runtime transfer evidence only; no Project-51 NVIDIA or Apple TG target moves.

### Secondary AMD lane — RX 6800 16 GB + 64 GB DDR4

This is a **low-confidence planning lane**, not a canonical target.

Current upstream Strata HIP documentation supports the RX 7900 XT/XTX gfx1100 Linux path, not RDNA2 gfx1030.
A community RDNA2 gfx1031 RX 6700 XT port has nevertheless served IQ3_XXS short prompts with MTP at **6-10 tok/s**
and high draft acceptance, but its ~1K+ multi-chunk prefill currently hits a routed-id failure. Exact RX 6800/gfx1030
Strata execution is therefore **not currently certified**.

For a fixed/tuned Linux RDNA2 port, the planning range for an RX 6800 16 GB with 64 GB DDR4 is:
- short / <=32K decode: roughly **12-18 tok/s**;
- ~64K decode: roughly **10-15 tok/s**;
- ~128K decode: roughly **8-12 tok/s**;
- cold prefill: order-of-magnitude **~150-350 tok/s**, strongly dependent on HIP dense kernels, CPU/DDR4, SSD residency
  and expert-cache hit rate.

A current minimally tuned/community RDNA2 build should be expected closer to **8-14 tok/s** short-context until the
long-prefill bug and architecture-specific tuning are resolved. The 64-GB upgrade primarily changes *feasibility and
residency* rather than raw GPU speed: it can keep much more of the CPU-expert complement resident and avoid pathological
SSD/page-fault behavior. Full 262K is not a comfortable 64-GB target on this 16-GB card; treat 64K-128K as the practical
first qualification range and 262K as a low-RAM/mmap experiment.

Evidence anchors:
- Strata issue #259: RX 6700 XT gfx1031 community port, IQ3_XXS, 6-10 tok/s short decode; long-prefill routed-id failure.
- Strata AMD_HIP_PERFORMANCE: RX 7900 XTX gfx1100 / 64-GB host, tuned IQ3_XXS path at 55-59 tok/s on 4K-9K fresh requests.
- Strata PR #247: RX 9070 16 GB / gfx1201, ~238 tok/s prefill and ~23 tok/s decode on a 4,445-token prompt.
- Strata PR #256: RX 9060 XT 16 GB / gfx1200, IQ1_M, 27-31 tok/s decode and 540-753 tok/s prefill.
- llama.cpp community RX 6800/6800 XT Qwen3.8 evidence confirms gfx1030 ROCm is viable but does not transfer directly
  to sparse Flash-Next/Strata expert-cache economics.

## 2026-09-30 12:22 ET consolidation delta — Strata 0.1.29, oMLX 0.7.0, and long-context verify gates

### Strata production baseline advances to 0.1.29+, but the stall family remains open

Strata 0.1.29 (commit `d6708a4aae15b4860000d54c8af9e84d684bce09`) is now the production baseline for new
Project-51 Strata runs. The release keeps fixed-cache output byte-identical to 0.1.28 on Q2_0/IQ3_XXS/IQ3_S/Coder
while adding faster QSA verify-window scoring, a software-pipelined prompt GDN recurrence, AVX2 expert-row prefetch,
and a faster sampled-token selector. The sampled selector is explicitly workload-dependent: on an RTX 5070 the
published Q2_0 gain ranges from about +4% at top-k 20 to +38-42% at top-k 64, while greedy decoding is unchanged.
Do not turn those sampling gains into a generic TG multiplier.

0.1.29 does **not** close the stability gate. Issue #251 reproduces a long-prompt stall on 0.1.29 with IQ3_XXS,
CUDA 13.0.2, a 4070 Ti SUPER 16 GB and 128 GB RAM: all 24 expert jobs finish, workers sleep, the GPU reaches layer
48, and the verify window remains stuck until the watchdog fires. Project-51 therefore keeps the exact-box >=8 h
soak, repeated cold long prompts, and watchdog-free completion as promotion requirements.

Issue #266 adds an agent-specific server race: a cancelled/aborted request whose generator finalizes after the next
request starts can clear the new request's status and produce `KeyError: 'tail'` / `RemoteDisconnected`. Add
rapid stream-abort -> immediate retry cycles to the agent soak; cancellation recovery is not certified merely by the
0.1.29 release's ordinary cancelled-prompt test.

### Windows 64-GB host admission now has a concrete host-registration failure mode

Strata issue #243 reports a single-GPU Windows 11 / 63.3-GB-RAM / RTX 4090 IQ3_XXS box where a failed whole-arena
`cudaHostRegister` followed by 28 GiB of sliced registration leaves every later `cudaMalloc` failing despite
roughly 19 GiB free VRAM and substantial free host memory/commit. Capping registered expert-arena memory at 8 GiB
lets the same machine reach READY in 51 s and serve at 40-44 tok/s. This is not an exact 5070-Ti receipt and it is
only a 131K configuration, so the ~90% conditional 262K/64-GB fit prior stays unchanged. It does make Windows host
pinning policy an explicit admission variable for the exact-box qualification.

The opposite OS-specific effect exists on Linux multi-GPU: issue #253 reports the same 8-GiB cap causing a Q2_0
32K prefill collapse from a locally patched 2,109.8 tok/s to 664.9 tok/s because expert-copy waits dominate.
Treat the pin cap as platform/topology-specific, not a universal tuning knob.

### Apple baseline advances to oMLX 0.7.0; M1-M4 mixed-width matrix use becomes a direct test

oMLX 0.7.0 is now the stable Apple baseline. Relevant durable properties include exact single-request Lightning-MTP
verify rows, the served-equivalent fused GDN norm fix, rebuilt memory admission, and an M1-Max native decode-attention
correctness fix. The release is a baseline promotion, not a new dual-M1 128K TG/PP receipt.

TensorFold PR #149 exposes a concrete pre-M5 Flash-Next inefficiency: 5/6/8-bit dense projections in mixed checkpoints
can fall through a row-at-a-time path rather than the matrix-unit backend. Its opt-in matrix path is bit-identical
between a 16-row window and 16 one-row steps in its tests. On M3 Ultra / Qwen3.8-Flash-Next oQ4e, the reported ranges
move from 83-111 -> 89-130 tok/s for one stream and 121-126 -> 140-168 for N=4, with only a small prefill change.
Those M3 Ultra numbers do **not** transfer numerically to M1 Max, but the mechanism is now a high-priority exact-M1
experiment at S=1 and MTP verify widths.

### Long-context MTP correctness remains a separate state-and-reduction problem

vLLM PR #59448 shows that short speculative verify queries can fall onto a path that walks the entire KV history;
on an AMD Strix Halo Qwen3.8-27B test, moving q_len=4 verify to a split-KV path produces large kernel-only gains at
long context, yet greedy continuations sometimes change because the reduction order changes. This is mechanism
evidence only, not a Project-51 speed transfer. Preserve source-equivalence tests when changing verify reductions.

SGLang PR #40001 independently shows that hybrid recurrent state under pipeline-parallel speculative decoding can
silently lose accuracy even while acceptance length looks normal when accepted GDN/KDA/Mamba state is not committed
on every stage or is paired with the wrong in-flight micro-batch. Project-51 continues to treat recurrent/QSA/MTP
state correctness as a first-class certification axis, separate from KV fit and acceptance rate.

### Strict-window negatives

No strict-window commit was found for the DASLab Flash-Next GSQ-RCO checkpoint, TurboQuant-MLX, MoEspresso,
mlx-serve, or Ishizuki. The latest commits observed for those projects remain outside this window
(DASLab `ed59f92`; TurboQuant-MLX 2026-09-19; MoEspresso 2026-09-24; mlx-serve 2026-09-30 00:50 UTC;
Ishizuki 2026-09-26).

**Numerical Project-51 targets do not move in this consolidation.** The new evidence changes baselines and
qualification gates, not the measured 5070-Ti PP centers, dual-M1 TG/PP target, AA priors, or K6/V4 quality prior.


## 2026-09-30 06:55 ET consolidation delta — Strata 0.1.28 and arithmetic-exact verifier gates

### Strata production baseline is now 0.1.28+

Strata 0.1.28 fixes the 0.1.27 draft-head VRAM-accounting regression: the expert cache now subtracts the MTP
draft head before sizing itself, so the configured reserve remains free instead of being consumed later. The old
1,058-1,100 MiB manual reserve is retained as a **0.1.27 diagnostic/control**, not the normal post-0.1.28 setup.

0.1.28 also clears stale cancellation/error state between requests, protects /status with the API key, refuses
explicit empty keys, fixes tool-call truncation when argument values contain literal closing-tag text, persists
installed-model host/API-key options, and reports the engine's actual final error on exit.

For multilingual/source-quality qualification, keep the default CJK-capable draft. The English/code-only draft is
an explicit capacity/performance arm: it saves about 110 MiB and is reported 1-2% faster on English, but
Chinese/Japanese/Korean receive almost no useful drafts.

### The 64-GB-host question has a new partial receipt, not a 262K proof

Strata issue #224 runs the native IQ3_XXS pack on an exact RTX 5070 Ti with a **62-GB Linux host**, INT8 KV and a
32K resident window. The self-built CUDA-12.8 engine faults in batched PLE on long prompts, but disabling the
batched PLE path completes an **11,105-token** prompt. This proves the near-target host class can at least load and
execute IQ3_XXS, but it is **not** a filled-262K receipt and does not move the ~90% conditional 262K/64-GB fit prior.

CUDA 12.8 remains outside the qualified RTX-50 lane. Reproduce #224 on CUDA 13.x before treating it as a current
general Strata defect.

### First-request/prompt stability is still an open qualification gate

Issue #217 was closed with 0.1.28 because its original report had exhausted VRAM and a stale stage label. A later
strict-window report still reproduces a driver-spin stall on **0.1.27** with more than 1.1 GiB free. Because that
later arm has not been rerun on 0.1.28, keep repeated cold-long-prompt starts and cancellation/retry cycles inside
the exact-box soak.

### Apple verifier exactness now includes GDN activation arithmetic

oMLX PR #4122 reproduces on **M1 Max 64 GB** that a fused speculative GDN norm can differ from the served SiLU graph
by one ULP at FP16/BF16 output solely because of a different float32 exponential implementation. A real checkpoint
matched 1,950 decode norm checks after selecting the served-equivalent expression.

Project-51 source-equivalence/MTP certification therefore requires **served-vs-fused GDN arithmetic parity**, not
only close float32 values or matching short text.

oMLX PR #3582 also makes the hardware boundary explicit: Affine4/Affine8 KV is aimed at M5; on M1-M4 the portable
path is a correctness fallback and TurboQuant remains the recommended compressed-KV route. Do not transfer M5
Affine capacity results into the dual-M1 plan.


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

### 2026-09-30 08:40 UTC exact-5070Ti filled-257K / PP recalibration update

- **NEW — first exact RTX 5070 Ti Strata receipt at genuinely filled near-native context:** Strata issue #200 reports **RTX 5070 Ti 16 GB (sm_120), Ryzen 7 7700, 93 GB RAM, Ubuntu 24.04, CUDA 13.2, IQ3_XXS native pack, streamed INT8 KV with 32,768 resident cells, MTP spec4, context 262,144**. A **257,466-token prompt was read from zero in 96.5 s = 2,668 PP**. This is genuine deep-context work, not allocation-only. Output at ~151K–257K was **95–118 TG**, but the reporter explicitly says these were list-style answers with unusually favorable draft acceptance; treat that TG range as an optimistic workload receipt, not a generic 262K center.
- **Host-memory evidence from the same exact-card run:** pinned K/V was **1.55 GiB @128K / 3.09 GiB @262K**; after load, the 93-GB machine reported roughly **44 GB / 43 GB system RAM available** at 128K/262K respectively. That implies the loaded model/runtime footprint itself is nowhere near 93 GB and materially narrows the 64-GB uncertainty. It still does **not** prove a 64-GB machine because transient load/staging and OS headroom may differ.
- **P51 fit recalibration:** exact GPU + native-context feasibility is now physically proven. For the actual Project-51 target — IQ3_XXS + compressed/streamed KV on 5070 Ti 16 GB + 64-GB host — move the conditional physical-fit prior **~85% -> ~90%**. The only major physical-fit unknown is now the smaller host's peak simultaneous allocation/staging, not VRAM or 262K execution correctness.
- **NEW — exact-card PP targets were stale low:** issue #199 on the same RTX 5070 Ti / IQ3_XXS path measures two ~60K prompts read from zero at **2,993 / 3,000 PP** with a safe 1,058-MiB VRAM reserve; issue #200 measures **2,668 PP at 257K from zero**. The old P51 IQ3_XXS PP centers (1,650 / 1,550 / 1,500 at 32/64/128K) are no longer credible for current Strata on this GPU class. New planning centers: **~3,000 PP @32K, ~2,900 @64K, ~2,750 @128K, ~2,500 @262K**. These are production-planning centers with a Windows/64-GB haircut, not claims that every workload or host reaches the Linux measurements.
- **NEW — long-context retrieval quality degrades with length even when KV precision does not explain it:** issue #200's adversarial exact-value retrieval test scores INT8 KV **10/10 @29K, 9/10 @73K, 8/10 @151K, 6/10 @257K**. At 151K, FP16 KV gives the **same 8/10 and the same two wrong answers**; at 257K FP16 is **7/10 vs INT8 6/10**, while costing **18–20% PP** and leaving TG unchanged. P51 consequence: keep INT8 as the source-quality control; do not assume higher KV precision fixes semantic long-context decay. 262K certification needs MRCR/needle/agent continuity and compaction policy, not just cache-precision A/B.
- **NEW — 16-GB VRAM reserve needs to account for the larger CJK MTP draft:** issue #199 measures 0.1.27 + `rt-cjk` + vision + IQ3_XXS on RTX 5070 Ti with only **154–156 MiB free** under setup's old 700-MiB reserve, below Strata's own 256-MiB low-headroom threshold. Raising reserve to **1,058 MiB** leaves **~510 MiB free**, costs only ~**2% PP**, and does not reduce TG in the reported runs. P51 production rule: for vision + CJK draft on 16-GB Blackwell, start around **1.0–1.1 GiB reserve** and record actual post-load free VRAM; do not maximize expert slots into the stall-warning region.
- **NEW — Strata sm_120 Linux toolchain gate:** issue #220 reports engine 0.1.27 built with **CUDA 12.8** on an RTX PRO 5000 Blackwell deterministically crashing in MTP prefill with an illegal memory access; rebuilding the same source with **CUDA 13.0** makes a 17,104-token prompt run at **2,473 PP / 98 TG**. P51 rule: Strata sm_120 builds require CUDA 13.x qualification; record toolkit/runtime with every result. Keep this separate from the existing llama.cpp IQ-compiler rule requiring CUDA 13.2.2+ for the known silent IQ corruption bug.
- **NEW — Strata 0.1.27 still has an unresolved first-request batched-prefill stall on another 16-GB NVIDIA card:** issue #217 reproduces a watchdog stall on RTX 5060 Ti / Swift IQ2_XS before generation, with the GPU ring fired but plan/copy flags still zero. It survives prior generation-stall and stale-error fixes. No exact-5070Ti reproduction yet, so no target-number penalty, but current production promotion still requires the user's own >=8h soak plus repeated cold long-prompt starts.
- **NEW — oMLX Qwen3.8-Flash-Next B8 shows shared MTP can lose to MTP-off:** issue #4111 on M5 Ultra reports **272 TG aggregate with MTP vs 293 TG MTP-off** at eight concurrent requests. A depth-3 shared verify of 8 requests costs **81.5 ms** vs **23.9 ms** for an ordinary 8-row decode step, and even parked MTP adds head-maintenance overhead (**25.1 vs 23.6 ms** per 8-row ordinary step). P51 scheduler rule strengthened: verifier depth/enablement is a **batch-size and context dependent decision**; carry a proven “park MTP” verdict across stable cohorts rather than relearning through many losing cycles.
- **NEW — mlx-serve exposes a >32K-row sorted-gather parity failure on M5 Max:** issue #649 finds the segmented NAX sorted gather differs from stock at **33,010 rows, n=64, k=128, 4-bit/group64** while 81,920-row Flash-shaped large-N/K cases pass. P51 Apple gate: kernel certification must sweep both **row-count boundaries and small-N/K tiles**; passing the long-context production shape does not prove neighboring verifier/prefill tail shapes.
- **NEW — SGLang PD/HiCache restore now clamps to the frontier promised at admission:** commit `51cae5f3` fixes a race where the radix tree grows while an L3->L2 restore is pending, causing a later rematch to return more tokens than prefill had committed to the decode request. P51 transfer/root rule: once a restore/import frontier is promised, later cache growth may not silently advance it; imported state is valid only through the **committed promised frontier**, even if a fresh lookup can match more tokens.
- **NEW — SGLang adds nightly Qwen3.8-Flash-Next-FP8 graph-mode accuracy on AMD:** commit `b87a241a` runs GSM8K + multimodal smoke on MI35x TP1 and MI30x TP2+EP2 with EAGLE speculation and graph decode. Across ROCm 10/7.2.0/7.2.4 the reported GSM8K is **0.968–0.971**. This is useful cross-backend model/runtime correctness evidence, not a P51 NVIDIA/Apple performance transfer.
- **SAME-DAY CURRENT — community Strata adoption on 64-GB hosts continues, but no new exact 64-GB filled-262K IQ3_XXS receipt was found.** A current Reddit report shows RTX 5070 Ti 12-GB-class/64-GB systems running IQ3_XXS at shorter depths and users reporting large Strata speedups; useful adoption signal only.
- **No new exact dual-M1 filled-128K receipt; no new DASLab source-paired 262K semantic-quality certification; no strict-window TurboQuant Flash K6/V4 implementation.**

**Target effect:** IQ3_XXS PP centers move to **3,000 / 2,900 / 2,750 / 2,500** at 32K / 64K / 128K / 262K. Conditional 5070Ti+64GB compressed-streaming 262K physical-fit prior moves **~85% -> ~90%**. TG centers and AA priors remain unchanged pending a controlled workload at 257K.

### 2026-09-30 05:37 UTC QSA-FP8 / long-context batching / snapshot exactness update

- **NEW — SGLang Qwen3.8-Flash-Next compressed-QSA indexer cache can use FP8 e4m3 with strong real-task parity:** merged PR #39614 stores only the **compressed QSA index keys and index query** as plain e4m3; the pending raw-key ring stays BF16, group mean/norm/RoPE compute stays BF16/FP32, and sparse attention's main KV cache is unaffected. On Qwen3.8-Flash-Next-FP8 / B300, BF16-indexer vs FP8-indexer results were: GSM8K **97.80 vs 97.65**, AIME26 xhigh pass@1 **98.33 vs 99.17**, GPQA-D xhigh pass@1 **92.11 vs 91.98**, majority@8 **93.18 vs 92.93**. This is the first strong evidence that one piece of QSA state need not remain BF16 for source-like behavior.
- **QSA-state contract refinement:** keep **logical/structural indexer state exact** — block positions, pending-ring lineage, spare/dead row identity, page/slot mapping, checkpoint frontier. But allow the **compressed normalized index-key rows** themselves to enter a qualified FP8-storage lane. Do not conflate this with quantizing the full-attention K/V payload or with reconstructing indexer state from generic KV.
- **Memory effect is modest but real:** for the Qwen4/Qwen3.8 compressed profile used by SGLang (1 index KV head, 128 dim, compression ratio 4) and 12 QSA/full-attention layers, BF16 compressed-key storage is about **768 B/token** and FP8 about **384 B/token**, so at 262,144 tokens the theoretical reduction is about **96 MiB**. The pending ring remains BF16. This is useful margin, not the primary 64-GB-fit lever. Current SGLang FP8 scoring is gated to SM90/SM100, **not RTX 5070 Ti sm_120**, so Project 51 must separately qualify/implement the Blackwell path before taking the memory credit on the user's box.
- **NEW — SGLang fuses QSA KV preparation / sparse block expansion and Qwen3.8 graph-replay metadata:** strict-window commits #40972/#41173 reduce the number of expansion/packing launches and preserve graph-stable QSA metadata across draft steps. P51 implication: with compressed/selective KV, carry compressed block identities as long as possible and expand/gather only at the final attention boundary; verifier rows must share graph-stable logical->physical metadata rather than rebuild it independently.
- **NEW — vLLM HiSparse proves MTP verification rows need one per-request residency union:** PR #59235 fixes a race where multiple verification rows of the same request independently claimed/evicted shared hot-cache slots. The new kernel unions all rows' selected host pages, resolves the union once, loads a shared page once, then maps each row onto the stable result. Race failed **30/30** on the old kernel and passes on H100/H200/B200; steady H100 residency time improved **155->64 us (1 req), 185->87 us (8), 264->167 us (32), 373->268 us (64)**. P51 rule: any MTP/S>1 sparse state working set — KV, QSA-selected pages, or expert residency — must be planned as the **union across the verification window** before mutation/eviction, not independently per row.
- **NEW — vLLM HiSparse host tier now refuses GPU-only pages:** PR #59036 makes host backing a hard admission invariant; every GPU page must have a host block so it can later be written back/reclaimed. In-flight spill ownership also blocks premature reuse. P51 rule: tiered state counts as evictable only when durable backing is already reserved/owned; never admit a GPU-only page and assume future host capacity will appear.
- **NEW — oMLX split-GDN exact-prefix persistence:** commit `cb157991` persists the exact terminal recurrent state for static/system-tool prefixes in an SSD sidecar. Split-GDN exact-prefix blocks are domain-separated from ordinary partial-prefix matching, and non-recurrent placeholder blocks cannot be reused as generic state. This is directly aligned with P51's persistent canonical root: exact static-root images need a separate identity/domain from ordinary token-prefix cache entries.
- **NEW — oMLX fixes recurrent tail accumulation:** `a28e5a87` applies tail-tip lineage to every layout, not only rotating-attention models. Hybrid GDN/QSA layouts had been retaining one full-state tail per turn indefinitely; now the previous turn remains as edited-turn fallback and the one two turns back is deleted with its GDN sidecar. P51 rule: root/private-suffix persistence needs an explicit **tail-generation retention policy**; “cache every valid state” silently destroys long-running resident capacity.
- **NEW — Strata unified conversation snapshot PR #189 reaches a 119,987-token soak with IQ3_S:** on RTX 4090 / 0.1.27, the shared snapshot core covers main+draft KV, GDN/PLE, indexer state including spare key, retained checkpoints, INT8 streamed/ring and K8V4 identity-layout cases. Thirty A/B/A-style cycles span **2,026 / 39,985 / 119,987-token** contexts with exact baseline output/state parity and stable retained payload. Physical-RAM admission checks Linux/Windows, invalid images fail before writes, and transfer failure is fatal instead of partial continuation. This materially strengthens the persistent-agent-root/state-image design, but is not a throughput or exact-user-hardware receipt.
- **NEW — Strata cancellation bug + exact 5070-Ti recovery receipt:** issue #183 / PR #194 validates on **RTX 5070 Ti 16 GB**, IQ3_XXS native pack, INT8 streamed KV, `--kv-resident 32768`, MTP spec4. Cancelling a 34,719-token prefill previously left stale `err="cancelled"` and killed the next long request; the two-line fix keeps the engine alive, resumes from the **16,384-token checkpoint**, and produces the same 64 token IDs as a fresh read. This is useful exact-box state/cancellation evidence, but not a 262K-filled receipt.
- **SAME-DAY independent deep-context Strata receipt (different hardware):** issue #183's original reporter runs **IQ3_S, context 262144, streamed INT8 KV / 32K resident** on RTX A4500 20 GB with 377 GB host RAM and shows a cancelled request after processing a **204,456-token prompt at 2,841 PP**. This proves Strata's hybrid state/KV streaming path can execute genuinely deep context with IQ3_S, but the large host RAM prevents direct transfer to the user's 64-GB fit question.
- **RECOVERED CURRENT exact 5070-Ti allocation receipt:** an Unsloth/llama.cpp report configures **UD-IQ3_XXS + Q4_0 KV + 262,144 context** on RTX 5070 Ti 16 GB and runs at **20.44 TG / 129.29 PP**, but the measured prompt is only **2,409 tokens**. Treat this as full-window allocation/startup evidence, **not filled-262K throughput or resident-state evidence**.
- **NEW — long-context Apple batching can collapse below solo:** oMLX issue #4110 on **M1 Ultra 128 GB**, Qwen3.8-27B oQ4e + TQ8 KV, reports solo at ~20K context **21.7 TG**, while two concurrent MTP-off requests fall to **~5.4/5.8 TG each (~11.2 aggregate)**. Short-context two-way reaches **28.9 aggregate**, so the failure is context-dependent; effective bandwidth falls from ~390 GB/s solo to ~110 GB/s batched. P51 implication: do not assume B2/B4 improves aggregate throughput at long context merely because weights are shared. Multi-agent Apple targets require explicit 16K/32K/64K/128K batch ladders, not short-context scaling.
- **NEW — TensorFold two-Spark parallelism shows the opposite when the runtime is healthy:** issue #123 reports Flash-Next TP2 on two DGX Sparks: 1 user **111 TG -> 110**, 2 users **91 -> 111 aggregate**, 4 **92 -> 148**, 8 **91 -> 188**, with byte-identical replies vs draft-off in the tested cases. This is encouraging distributed/concurrent mechanism evidence but cannot cancel the M1-Ultra long-context negative; hardware/runtime/context differ.
- **NEW — mlx-serve multirow HC read optimization is not bit-identical for 8-bit HC weights:** commit `933566c4` saves about **1.00 ms/step at 4 streams** but rare BF16 elements differ by a few ULPs; stacked-one-row equality holds for 4-bit HC or when `MLX_SERVE_HC_UV=0`. P51 Apple AA/source-equivalence rule strengthened: multirow performance kernels that alter reduction/projection numerics must be disabled or separately certified on near-tie real-model trajectories.
- **No strict-window Strata 0.1.28/0.1.29 release, no exact 5070-Ti 64-GB filled-262K IQ3_XXS run, no new public exact-M1-Max ~27-TG receipt, and no new DASLab source-paired 262K semantic-quality result.**

**Target effect:** no TG/PP center change and no change to the ~85% conditional 262K physical-fit prior. Add FP8 compressed-QSA keys as an optional post-baseline memory lane; add union-residency and long-context B2/B4 batching gates; strengthen exact-prefix/root/tail-lifetime rules.

### 2026-09-29 23:52 UTC Flash-TurboQuant physical proof / cache-core update

- **RECOVERED OLDER but target-moving — Flash-Next compressed KV already exists in llama.cpp research forks:** the prior statement that the required Flash/QSA compressed-KV path "does not yet exist" was too broad. It is true for **Strata** and **TurboQuant-MLX**, but at least two public Qwen3.8-Flash-Next llama.cpp research trees have implemented real compressed KV while retaining the model's hybrid sparse-attention machinery. This materially lowers implementation risk for P51: we need a Strata/CUDA adaptation, not a first-ever proof that Flash-Next can carry compressed full-attention KV.
- **Strongest recovered physical receipt — 16-GB GPU + IQ3_XXS + native 262K allocation:** `starsder/qwen3.8-flash-next-inference-research` documents Qwen3.8-Flash-Next **UD-IQ3_XXS**, `-c 262144`, on an **RTX A5000 16 GB** / 128-GB host. Only **12/48 layers** are full-attention KV layers (2 KV heads, head_dim 256). At 256K it records: F16 KV **6.0 GiB**, q8_0 **3.19 GiB**, q4_0 **1.69 GiB**, TBQ4 **1.52 GiB**, TBQ3 **1.15 GiB**. In the historical matrix TBQ3 leaves **51 MoE-cache slots** versus 29 for q8_0 and reports peak GPU memory about **14,496 MiB**. This directly proves that **16-GB VRAM is not the blocker for IQ3-class Flash at full native context when KV is compressed**. Host RAM was 128 GB, so it does not by itself prove the user's 64-GB host fit.
- **Recovered TBQ3 quality receipt — useful but not AA certification:** same research tree's controlled short PPL/KLD matrix gives f16 PPL **2.0120**, q8_0 **2.0128 / mean KLD 0.03085**, q4_0 **2.0234 / 0.05689**, and TBQ3 **2.0728 / 0.11640**. TBQ3 is therefore a real capacity format, not quality-neutral on that fixture. TBQ4 was broken/unusable in that branch's tested FA path (single-chunk PPL ~63.7), so do not treat its 1.52-GiB capacity number as a valid quality receipt.
- **Independent second Flash-TurboQuant implementation — `thadreber-web/llama.cpp-qwen38-flash-next`:** Turbo3 K+V on Qwen3.8-Flash-Next measured **40.57 vs 40.02 TG** for q8_0 (n=10; statistically indistinguishable) and saved **341 MiB** in the tested 131K-class serving configuration. A later same-binary quality check reports about **+2.56% PPL vs q8_0**. The implementation explicitly avoids double Hadamard rotation and integrates recurrent-state rollback for MTP. This independently corroborates that Flash-aware TurboQuant KV is implementable and useful for memory even when it gives no speedup.
- **Geometry correction strengthens the fit model:** Qwen3.8-Flash-Next has only **12 full-attention layers**, not 48 KV-bearing layers. This explains why KV is only a few GiB even at 262K and why KV compression buys roughly 1-2 GiB rather than tens of GiB. P51's Strata-specific 3.6-GB INT8 figure remains the direct planning anchor because Strata includes its own block/draft/streaming overhead; the llama.cpp q8_0 **3.19-GiB** figure is a useful lower cross-runtime anchor.
- **262K fit prior moves:** conditional on implementing compressed host KV without a full expanded duplicate, the overall **IQ3_XXS + 262K + 16-GB GPU + 64-GB host physical-fit prior rises from ~75-80% to ~85%**. GPU-side feasibility is now effectively high-confidence; remaining risk is host-RAM admission/staging and Strata integration, not VRAM capacity.
- **K6/V4 remains the preferred custom quality rung:** existing Flash implementations expose roughly 3- and 4-bit TurboQuant-like formats, not P51's proposed 6-bit-K / 4-bit-V mix. The observed TBQ3 PPL/KLD degradation is a reason **not** to jump directly to 3-bit K/V. K6/V4 remains a conservative intermediate whose long-context/source-like quality still needs direct Flash measurements. Do not raise its AA prior merely because TBQ3 fits.
- **Porting strategy update:** mine the existing qwen4exp llama.cpp TBQ plumbing for cache geometry, rotation ownership, CUDA encode/decode, FA integration and QSA separation; do not model the Strata work on TurboQuant-MLX's generic `KVCache` replacement, which intentionally skips Flash's `_AttnCache`.
- **RECOVERED CURRENT — Strata 0.1.27 officially ships the CJK draft-subset fix:** release commit `a7908053` landed at **20:58:59 UTC**, before this pass's hard boundary, so classify RECOVERED CURRENT. Setup now replaces known older draft vocabularies with a subset including Chinese, Japanese and Korean. This promotes our earlier #137 finding from external patch evidence to shipped Strata behavior; domain/output-vocabulary coverage remains a general certification gate.
- **NEW strict-window Strata snapshot-core convergence:** #57 now reports a unified RAM + optional NVMe implementation on the shared snapshot API, with bounded staging, integrity/compatibility checks, atomic disk writes and quotas. Host-level serialization/corruption/restart/eviction/admission tests pass; full GPU/model validation for K8V4, batched draft KV and disk restart parity is still pending. A separate Windows 0.1.27 low-RAM snapshot test on RTX 4070 Laptop / 64 GB reused 3,216 of 3,223 tokens after three unrelated calls and returned in **0.8-1.4 s vs 10.7-11.9 s cold**, but this is only a 3.2K bounded fixture.
- **NEW strict-window TensorFold real-64GB memory-accounting warning:** on M5 Pro 64 GB / Flash-Next SSD experts, 0.4.0 fixed kept-prompt reuse at ~34.4K (**2.18 s resumed vs 195.4 s cold**) but still advertised a **65,536** window while refusing a 65,378-token request at an admission limit of **51,392** on a fresh server. P51 rule reinforced: advertised/resident-context capacity must be derived from the same live accounting used for admission and checkpoint retention; startup fit estimates are not capacity evidence.
- **NEW strict-window SGLang GDN verifier tuning:** SM90 target-verify recurrent GDN now uses a narrow BV=4 launch for N<=64 only after bit-exact tests against the previous BV=32 result across tree/non-tree verification. Cross-hardware only, but it reinforces P69's rule: verifier-specific launch tuning is allowed only behind exact output/state parity.
- **NEW strict-window vLLM hybrid-prefix guard:** a prefix-match unit that a single KV cache group cannot honor is now rejected rather than accepted into an inconsistent hybrid-cache configuration. P51 root/cache rule: prefix granularity is part of the cache-state contract; every participating state group must be able to represent the chosen reusable boundary.
- **NEW strict-window Strata AMD independent run:** issue #178 reports a Radeon AI PRO R9700 32 GB / ROCm 7.14 build running Coder IQ1_M at 128K with ~27 GB mapped host RAM, **62.7 PP / 44.7 TG** and 12/14 MTP acceptance. Useful evidence that Strata's architecture is not CUDA-only theater; no target effect for the user's NVIDIA lane.
- **No strict-window exact 5070-Ti 262K IQ3_XXS run, no new public M1-Max ~27-TG receipt, and no new official DASLab source-paired 262K semantic-quality result.**

**Target effect:** keep all existing TG/PP centers. Raise only the conditional physical-fit prior for **IQ3_XXS + genuine 262K + compressed Flash-aware KV on the user's 16-GB/64-GB box** to **~85%**. The quality and production-readiness gates remain separate.

### 2026-09-29 21:50 UTC compressed-KV / 262K-IQ3_XXS target update

- **PROJECT TARGET PROMOTION — IQ3_XXS + native 262K on RTX 5070 Ti / 64-GB host:** the preferred capacity direction is now to preserve the **3.00-bpw GSQ-RCO IQ3_XXS transformer** and compress/stream KV rather than immediately dropping weights to IQ2_XS. Stock Strata's current cap is conservative admission policy, not proof of a hard physical impossibility: `setup.py` models IQ3_XXS at **60 GB normal RAM / 42.9 GB expert arena**, INT8 streamed KV at ~**13.7 KB/token** (~3.6 GB at 262K), plus a ~1-GB admission margin. That simple sum lands around **64.6 GB**, explaining the forced 128K cap on <90-GB hosts.
- **RECOVERED CURRENT — TurboQuant-MLX Flash-Next audit corrects an important assumption:** although TurboQuant-MLX supports Qwen3.8-Flash-Next weights, **`--kv-bits` currently has no effect on Flash-Next**. Flash uses an `_AttnCache` subclass that carries the QSA sparse-indexer keys; replacing it with the generic TurboQuant cache previously dropped those keys and silently changed decode into effectively dense attention. The runtime now refuses to convert that subclass. Therefore P51's compressed-KV lane requires a **Flash/QSA-aware cache that preserves indexer state separately**, not a command-line toggle on an existing implementation.
- **TurboQuant 6-bit is implemented generically, but physical storage is not ideal 6.0 bpv:** the MLX codec accepts 1-8-bit Lloyd-Max codebooks, including 6 bit. Its generic uint32 packing stores only **5 six-bit indices per word**, so K6 indices consume **6.4 physical bits/value**. With one FP16 scale per 64-value group, K6 is ~**6.65 bpv** and V4 ~**4.25 bpv**; equal-sized K/V therefore make **K6/V4 ~5.45 bpv effective storage**, not 5.0.
- **Revised 262K memory prior:** if a Flash-aware K6/V4 codec replaces Strata's current INT8 QSA KV with comparable geometry, the first-order storage ratio is roughly **5.45 / ~8.25 ~= 0.66**. The current ~3.6-GB 262K INT8 host KV would therefore be roughly **~2.4 GB**, saving about **~1.2 GB**. K6/K6 is closer to ~6.65 bpv / ~2.9 GB and probably buys too little margin; K4/V4 is ~4.25 bpv / ~1.9 GB but has a materially higher quality risk. These are **format-level estimates**, not measured Flash receipts.
- **Quality evidence argues against jumping straight to 3-bit KV:** the broader 2026 TurboQuant ecosystem now treats FP8 as the quality baseline when 2x compression is enough and, in independent long-context evaluations, prefers a 4-bit no-QJL/norm-corrected lane over 3-bit variants; reported 3-bit modes can lose **15-25 benchmark points at >=128K** on some models. A separate 8-model reference study finds optimal K/V bits are architecture-dependent: examples include **K6/V4**, **K6/V3**, and Qwen-family cases requiring **K8/V4**. P51 should therefore test K6/V4 as a research rung, not assume it is source-like.
- **Flash-specific protected state remains non-negotiable:** QSA/indexer selection state, its spare/dead row identity, recurrent/GDN state, MTP/draft state and checkpoint/frontier identity stay outside the lossy KV codec. Compress only the full-attention K/V payload first; do not let a generic cache replacement erase or reconstruct QSA metadata.
- **Compressed streaming is part of the target identity:** a 262K success only counts if compressed KV remains compressed in host storage and across the hot transfer path. Dequantizing the entire 262K history into a persistent/large temporary buffer defeats the RAM target. Preferred implementation: compressed host pages -> gather only selected/resident cells -> dequantize into registers/shared scratch for attention. The resident GPU KV window can remain ~32K initially; any VRAM saved should be reinvested in hot experts or a larger resident window.
- **Feasibility split:** physical-fit feasibility for **IQ3_XXS + 262K + ~5.5-bpv K/V on 64 GB** is now a first-class planning target at roughly **~75-80%** conditional on a correct Flash-aware implementation. Source-like long-horizon quality for K6/V4 is lower-confidence (**~60-70% prior**) until Qwen3.8-Flash-Next 262K AA/retrieval/agent tests exist. End-to-end production readiness is lower still because no current Strata/TurboQuant Flash implementation provides the required compressed-QSA streaming path.
- **RECOVERED CURRENT — TurboQuant-MLX weight result is useful but not KV evidence:** its published Flash-Next 52.0-GiB TQ mixed-weight build runs fully resident on 64-GB Apple hardware, and n-gram SSD offload cuts active memory **52.01 -> 34.13 GiB** bit-identically for that runtime. This supports aggressive memory engineering around Flash but must not be cited as proof of compressed Flash KV.
- **NEW strict-window vLLM Mamba checkpoint fix — `d882bddb`:** sparse checkpoint retention could drop the reusable **prompt-end** recurrent checkpoint because the final partial prompt block looked transient. vLLM now explicitly preserves the computed prompt-end checkpoint and verifies a follower resumes from it. P51 root/cache rule strengthened: sparse retention may discard intermediate boundaries, but the canonical materialized prompt-end frontier must be pinned independently.
- **NEW strict-window SGLang DFlash auxiliary-state sharing — `84523d67`:** multiple decode CUDA-graph sizes now share one preallocated packed auxiliary-hidden-state output for DFlash target->draft transfer rather than each graph pinning its own buffer. The draft consumes the buffer before the next target forward overwrites it. P51 rule: verifier/drafter auxiliary state can be **single-owner, cycle-scoped scratch** when lifetime is proven; do not multiply resident memory by graph/S variants unnecessarily.
- **NEW strict-window mlx-serve NAX canary follow-up — `ff7f359b`:** a per-shape kernel config cache was growing with every prompt row count and canary error handling could consume a prior operation's latched Metal error. Configs are now per-call and canaries drop only errors they raised. P51 lesson: parity/fallback canaries must not hide unrelated forward failures, and shape-keyed runtime caches need bounded lifetime.
- **No strict-window new exact-M1-Max Flash receipt, no new Strata 0.1.26 exact-user-box 262K IQ3 receipt, and no new official DASLab Flash IQ3_S long-context source-paired semantic result.**

**Target effect:** add **IQ3_XXS 3.00-bpw + native 262K + Flash-aware compressed KV** as the preferred 5070-Ti/64-GB maximum-context research lane. Keep INT8 at 128K as the source-quality control, K8V4 as the currently implemented Strata capacity control, and treat K6/V4 as the first custom TurboQuant-style candidate. No existing TG/PP center moves until a physical 262K IQ3_XXS run exists.

### 2026-09-29 20:40 UTC Strata-0.1.26 PP / width-invariance / transfer-region update

- **NEW strict-window Strata 0.1.26 full prompt matrix:** on the same weaker RTX 5070 12 GB / Ryzen 5 7600 / 64-GB Windows calibration box and the same code-agent prompts, IQ3_XXS now measures **1,745 / 1,609 / 1,602 PP** at 32K / 64K / 128K and IQ3_S **1,624 / 1,640 / 1,443 PP**. Versus 0.1.22, the documented prompt gains at 32K-128K are **8-28%** depending on quant/context. These receipts materially clear the existing P51 5070-Ti PP centers and justify another conservative PP true-up.
- **0.1.26 mechanism attribution:** the new matrix combines 0.1.24 tensor-core QSA selection, 0.1.25 mapped grouping tables/fused norms and 0.1.26's batched MTP draft-layer prompt pass. The 0.1.26 engine release commit itself landed at **18:01:05 UTC**, before this pass's strict boundary; classify it **RECOVERED CURRENT**, while the full speed-table publication at **20:09:44 UTC** is NEW for this pass.
- **Output TG is not promoted from the 12-GB matrix:** IQ3_XXS is only **58.5 / 57.2 / 49.0 TG** at 32K / 64K / 128K and IQ3_S **48.3 / 46.3 / 45.5 TG** on this weaker card. The exact-GPU-class RTX 5070 Ti 128K IQ3_XXS receipt at 79.7 TG remains the stronger P51 decode anchor. The new matrix is a **PP target mover only**.
- **UPDATE — verifier width changes native CPU expert arithmetic in current Strata:** issue #152 demonstrates that singleton native i-quant expert groups use ggml `vec_dot` while groups with `nt>=2` use custom AVX paths whose FP32 reduction order differs. Replaying fixed rows produced **9,566 differing cells** between singleton and grouped execution; forcing ggml `vec_dot` at widths 1/2/4 restores bitwise equality, and a fixed 21,999-token greedy prompt then matches plain/MTP target tokens. The maintainer confirmed the bug in this strict window. Temporary width-invariant mode: **`STRATA_NO_IQ512=1 STRATA_NO_IQ256=1 STRATA_NO_IQ4NL=1`** at some CPU-speed cost.
- **P51 exactness consequence:** target-model arithmetic may not depend on speculative/verifier width. All source-equivalence/AA/MTP acceptance certification must use a width-invariant expert path or a fixed upstream engine. Published default-path TG remains a valid physical speed receipt, but it is **not an exact-serial quality certificate** while this bug is present.
- **NEW Strata low-RAM operational lane:** 0.1.26 can mmap `experts.bin` instead of pinning the whole expert corpus in committed RAM when experts + OS headroom do not fit. On the Coder example, committed memory falls roughly **36 -> 13 GB** with the same answers. Large GPUs can remain near normal speed; smaller GPUs fetch more experts from SSD and can slow substantially. For the user's 64-GB host, this is an **admission/stability fallback** for tight IQ3_S configurations, not the canonical performance baseline.
- **Windows memory-accounting clarification:** a same-day Strata maintainer response confirms Task Manager "shared GPU memory" can be the same pinned expert RAM counted again, while Windows also charges VRAM against commit/pagefile accounting. P51 Windows admission should key on **actual physical availability/page activity**, not naïvely sum Task Manager RAM + shared GPU + commit as independent resident bytes.
- **NEW vLLM Mooncake packed hybrid/MLA transfer work — `faacc135`:** transfer metadata now carries layer identity, KV-group/shared-group identity and row offsets for packed hybrid cache views; contiguous compatible slices are coalesced into fewer transfer regions, while heterogeneous-PP peers copy only their shared layer span. Mismatched same-PP layouts fail closed; hetero PP with no common layers is an empty success. P51 handoff rule strengthened: coalescing is an optimization **after** semantic region alignment — never infer transfer identity from physical contiguity alone.
- **Transfer-region contract refinement:** packed/hybrid state transfer keys should include component/layer/group/row-offset identity and block stride. Coalesce only adjacent regions that remain inside the same packed row/group semantics; a producer/consumer PP mismatch may legally omit non-shared layers but must never silently reinterpret row layout.
- **SAME-DAY CURRENT:** Strata has a new planned RTX 3090 / dual-3090 0.1.26 benchmark contribution, but no measurements yet; no target effect.
- **No new public exact-M1-Max ~27-TG fork/settings/context receipt** and no new official DASLab Flash IQ3_S source-paired long-context semantic-quality result in this pass.

**Target effect:** raise Strata cold-PP centers only. Proposed mature centers become IQ3_XXS **1,650 / 1,550 / 1,500 PP** at 32K / 64K / 128K, and IQ3_S **1,550 / 1,550 / 1,350 PP**. Keep every TG center, AA prior and dual-M1 headline unchanged. Add width-invariant native-expert arithmetic as a mandatory AA/speculation certification gate.

### 2026-09-29 19:09 UTC TensorFold-0.4 / Strata-0.1.25 / mixed-bit-state update

- **NEW TensorFold 0.4.0 makes the Apple7 mixed-bit premise concrete:** on **M1-M4**, Flash-Next now loads MLX affine **2/3/4/5/6/8-bit and per-module mixed checkpoints**, with 4-bit group-32 keeping its existing kernels and higher-width modules using row-exact kernels. TensorFold also moves pre-M5 5/6/8-bit linears onto matrix units. On M3 Ultra / dense Qwen3.8-27B, oQ4e 8-row verify falls **40.8 -> 31.9 ms**, lands within **1-5% of 4-bit** across widths, and sampled DFlash2 code is reported **14% faster** (chat +5-7%, greedy code level) while drafted replies remain equal to that runtime's serial reference. This is **cross-chip/runtime mechanism evidence**, not an M1 Flash TG receipt, but it removes a major implementation-risk objection to P51's protected high-precision islands inside a ~3.3-3.6-bpw mixed artifact.
- **TensorFold 0.4.0 Flash-specific pre-M5 work:** Flash-Next is reported **2-7% faster on M1-M4** on M3 Ultra from attention-gate merge fusion, fused PLE/router work and cheaper 4-bit multi-row dots, while preserving the runtime's serial equivalence. Do not transfer the M3 percentage numerically to M1; promote the kernels/format support as Apple7 mining evidence only.
- **TensorFold concurrency/admission evidence:** on a 64-GB Mac, dense 27B now serves **16 streams at 32K** where 0.3.x served 4-9, by charging stream memory as it grows and pricing shared-round workspace across the streams that use it. This supports P51's principle that concurrency capacity must be based on **incremental live-state + shared working-set accounting**, not reserving every stream's maximum reply up front.
- **NEW Strata 0.1.25 prompt fusion:** bit-identical hyper-connection changes remove an FP32 normalized-row copy and fuse a half's write with the next half's norm. The published F-1+F-2 A/B is **+4.0% @32K / +3.3% @128K** on the tested prompt path. This is useful common-path headroom but does not move the IQ3 PP centers without a new same-quant 0.1.25 matrix.
- **NEW Strata K8V4 KV mode becomes the preferred capacity experiment:** keys remain **INT8** so attention-score precision follows the INT8 path; values use Hadamard-rotated Q4_0. Footprint is **816 B/cell vs 1,056 B/cell for INT8 (~23% less)**. On RTX 3090 / Coder IQ1_M at ~198K, docs report **99 TG vs 85 TG INT8**, same needle result and **2-5% slower prefill**; the implementation commit reports 1.39 GB KV @131K vs 1.80 GB INT8 and 25/26 needles at ~198K. This is not enough to make K8V4 the quality default: no long-horizon/AA semantic qualification, no KV streaming support, and the decode uplift may come from freeing expert residency. P51 should test **INT8 K + Q4 V before full Q4 KV** whenever long-context capacity is the goal.
- **UPDATE exact 5070-Ti multilingual MTP fix:** a second Windows RTX 5070 Ti reproduction expands the shipped 40,525-id English-heavy draft subset to **106,285 ids** by adding Han/kana/Hangul/CJK punctuation. Head size rises **52.6 -> 137.9 MiB** but expert-cache slots remain **5,627**, unlike the full 322.1-MiB head which loses 76 slots. On an 8-request English->Chinese translation job, mean decode moves **68.1 -> 99.0 TG (+45.4%)**, acceptance **34-36% -> 70-77%**, and wall time **108.9 -> 78.5 s**; the expanded subset slightly beats the full head (96.4 TG). The correct production rule is therefore **domain-aware compact candidate expansion first, full-head fail-open second**.
- **Draft coverage is output-distribution dependent, not prompt-language dependent:** in that reproduction, English code is essentially unchanged while Chinese-heavy outputs gain the most; a Chinese-instruction coding task gains only in proportion to the Han share of emitted tokens. P51's candidate-space audit should be computed over **actual target-output token occurrences/kinds**, not merely prompt corpus language.
- **UPDATE Strata NVMe delta tier exposes two correctness/performance gaps before promotion:** the #52 branch now appends delta KV chunks rather than rewriting a ~2-GB file every turn, but still synchronously writes an approximately **113-MB mutable State record per turn** and stages the assembled image in RAM (~**2.3 GB at 142K**) on restore. More importantly, its new delta manifest is bound to a weight-set fingerprint + KV quant, while the older v3 fallback used for very long sessions remains **geometry-only / weight-blind**, which could silently restore same-geometry state into different weights. P51 persistent formats must **never permit a legacy/overflow fallback to weaken model/quant/schema identity**; unsupported old state should hard-miss rather than promote.
- **NEW MLX-Serve B2-B4 QSA mechanism:** one fused sparse-QSA split+merge launch now serves **2-4 quantized S=1 decode slots**, bit-identical to the previous per-slot launches. This is directly aligned with the P51 multi-agent aggregate lane, but no end-to-end B2/B4 throughput receipt accompanies the commit, so the aggregate confidence ladder does not move.
- **NEW MLX-Serve Flash prefill mining:** on M5 Ultra/mid48, the occupancy-tuned QSA tensor-unit path makes the QSA stage dramatically cheaper and the commit reports **+22.6% Flash-Next prefill**; the separately ported segmented sorted-MoE gather/row-map/fused-SwiGLU stack reports **+10.5% Flash-Next prefill**. Both use first-use parity/fallback gates. Cross-chip only; they strengthen the 400-PP Apple mining plan, not the M1 target directly.
- **Memory accounting rule reinforced — MLX-Serve `f5acdade`:** make-room eviction must clear the allocator cache before the next model's OS-level memory preflight; bookkeeping that says memory is free is insufficient if the allocator still parks the pages. P51 resident-agent admission should distinguish **logical free**, runtime allocator cache and OS-reclaimable/physical free memory.
- **SAME-DAY CURRENT dense27B warning:** a current Splash discussion reports very high Mac throughput but at least one user finds Splash-tuned 27B behavior behind base on debugging/code analysis. Treat as anecdotal but consistent with P51's rule that runtime/quant throughput claims need artifact-producing and source-paired quality gates.
- **No new public exact-M1-Max ~27-TG fork/settings/context receipt** and no new DASLab Flash IQ3_S source-paired 32K/64K/128K/262K semantic-quality result in this pass.

**Target effect:** no headline TG/PP or AA probability change. Durable planning changes are (1) mixed 2-8-bit row-exact execution on pre-M5 Macs is now a demonstrated runtime capability, (2) **K8V4 replaces full-Q4 KV as the preferred long-context capacity experiment** while INT8 remains the quality baseline, and (3) multilingual/speculative candidate vocabularies should be compactly expanded by output domain before falling back to the full head.

### 2026-09-29 15:03 UTC exact-5070Ti / MTP-vocab / agent-eval update

- **NEW exact-GPU-class Strata 0.1.24 IQ3_XXS receipt — RTX 5070 Ti 16 GB:** issue #137 reports a physical RTX 5070 Ti (PCIe 5 x16) + Ryzen 7 7700 + 96 GB DDR5-5200, engine 0.1.24, IQ3_XXS, INT8 KV, max context 131,072. Against the author's tuned llama.cpp fork on the same box/model class, Strata is reported at **79.7 TG @128K** versus **81.3 TG** for the fork. This directly closes much of the previous 128K extrapolation gap for the P51 5070-Ti lane. Keep the mature IQ3_XXS 128K center at **78 TG** but raise confidence; one domain-specific physical report is not enough to move the center or the 90-TG stretch.
- **NEW MTP draft-vocabulary failure mode — same receipt:** Strata's bundled `draft_vocab.bin` contains **40,525 token ids but only 27 tokens containing a CJK character**, while the full tokenizer vocabulary contains **55,328** CJK-bearing tokens. Chinese-output draft acceptance collapses because the MTP head cannot propose most valid target tokens. Removing the subset vocabulary and using the full native head changes three fixed Chinese/mixed prompts from **76.8 average TG -> 87.7 TG (+14%)**; draft counts rise sharply, with no reported VRAM penalty. P51 rule: **draft candidate-space coverage is part of speculative identity**. Qualification must include output-language/domain coverage and a full-head/fail-open fallback; low acceptance is not automatically a model or verifier-kernel problem.
- **Speculation width interaction from the same exact 5070-Ti box:** with the broken subset head, spec2 ~= spec4 (**76.2 vs 76.8 TG**); with the full head, spec4 is modestly better (**87.7 vs 85.8 TG**). This is a reminder that optimizing verifier width before fixing draft candidate coverage can produce false conclusions about S/acceptance efficiency.
- **Expert-path bottleneck negative result:** the same author locally tried top-8 routed experts instead of top-10 for decode and measured **76.7 vs 76.8 TG** in Strata, despite a +10-18% gain in their llama.cpp fork. P51 interpretation: routed-expert count is runtime-sensitive; do not assume expert-byte reduction maps to decode TG when CPU/GPU handoff, verification or sparse-attention work is dominant.
- **NEW real-agent cache failure evidence — Strata #143:** an OpenClaw + IQ3_S / 262K workload repeatedly re-prefills **150K-168K** prompts (~100+ s each) instead of hitting a long conversation checkpoint. The user suspects early serialization drift and asks for first-mismatch diagnostics. This does not refute #57's snapshot correctness; it proves that exact-prefix caches need observability. P51 cache/root telemetry should expose **candidate checkpoint id, matched token count, first mismatch position/reason, identity-field mismatch and reuse decision** so client rendering drift is distinguishable from state-cache failure.
- **NEW mlx-serve real coding-agent eval harness — `99cfc748`:** larger runtime/quant changes are now tested by having Pi build a real TypeScript/Vite artifact, compiling/rendering it, and grading checkable visual claims over multiple frames. The maintainers explicitly note that packs/samplers/speculation/templates can leave tok/s and MMLU flat while causing loops, early exits or worse artifacts. Minimum recommendation is **>=5 runs/arm**, with build success, turns/source-lines/end-state plus claim-level judge results. P51 AA certification should retain paired source-vs-quant micro/benchmark tests but add at least one **artifact-producing agent task with repeated runs** for changes to quant allocation, sampler, speculative acceptance, template or KV precision.
- **Agent-eval harness caught a methodology bug:** its first version hardcoded a 262K Pi context / 32K output cap, causing 32K/64K servers to return 400s that looked like agent early exits. It now derives context/reserve from the server launch config. P51 rule: agent evaluation must bind the client's compaction/output budget to the server's actual context contract; otherwise runtime-capacity errors contaminate quality labels.
- **RECOVERED CURRENT — M2 Max 96-GB Flash-Next REAP-288 Q4:** a same-day community report measures about **25 TG** for Flash-Next REAP-288 Q4 on M2 Max 96 GB and ~21 TG for dense 27B Q4. Useful Apple-family transfer evidence that Flash can outrun dense 27B under a suitably pruned/quantized artifact, but no filled-128K denominator or M1 result; do not move the dual-M1 target.
- **No strict-window M1-Max ~27-TG fork publication** and no new DASLab Flash IQ3_S source-paired 32K/64K/128K/262K quality result found.

**Target effect:** keep Strata IQ3_XXS **78 TG @128K** but raise its planning confidence from ~65% to **~85%** because the exact GPU class now physically measures 79.7 TG there. Add multilingual/domain draft-vocabulary coverage to the speculative-production gates. All other TG/PP centers and AA priors remain unchanged.

### 2026-09-29 12:57 UTC full Strata PP ladder / parked-state / verifier-semantics update

- **NEW full Strata 0.1.22 prompt matrix on the weaker RTX 5070 12 GB:** IQ3_XXS measures **1,555 / 1,449 / 1,386 PP** at 32K / 64K / 128K; IQ3_S measures **1,499 / 1,285 / 1,245 PP**. These are one-shot code-agent prompts on Windows 10 / Ryzen 5 7600 / 64 GB DDR5-5200, MTP spec4, INT8 KV above 4K and KV streaming from 64K. Every row clears the prior P51 5070-Ti cold-PP center, so the PP targets can be raised conservatively. Output TG is unchanged and remains text/acceptance dependent.
- **NEW Strata 0.1.24 long-prompt QSA selection:** on RTX 5070 / Q2_0, the selection path moves **32K 1,742 -> 1,797 PP** and **128K 1,608 -> 1,843 PP**, TTFT **82.7 -> 72.3 s** at 128K. Register top-k keeps selected ids exact; the block-score GEMM uses 3x-TF32 and is not bitwise. Needles remain 15/15, 16K continuation 32/32 identical, while 32K top-1 remains the same with **KL ~0.03**. P51 rule: exact selection ids do not imply exact model logits when the scoring arithmetic changes; treat this as an approximate prompt-only lane and certify trajectories separately.
- **NEW Strata multi-conversation shared-core physical proof:** the #57 shared-core branch now preserves complete used-page session state including QSA KV/stream maps, indexer state **including the per-sequence spare key `idx_dead`**, GDN/PLE, MTP, checkpoints and compatibility identity. A missing `idx_dead` field was found during audit because equal-opening-token fixtures had masked it; this independently validates P51's rule that every latent/indexer spare row must be fingerprinted and restored explicitly.
- **Tier-1 parked-agent soak now strong:** Linux / RTX 4090 / IQ3_S passed **30 A->B->A returns** across ~2,026 / 39,985 / **119,987 tokens**, including streamed KV, expected secret-word answers, exact baseline output/state parity and stable retained payload. At 51,133 cached tokens, return after B reuses the full prefix and processes 22 new tokens in **1.237 s**; checkpoint return processes seven new tokens in **0.566 s**. This is same-runtime RAM parking, not restart persistence and not Apple timing, but it is direct proof that a ~120K full hybrid conversation can be parked/restored repeatedly without re-prefill.
- **Shared-core admission/failure semantics matured:** Linux and Windows physical-memory admission are now explicit; unknown telemetry declines admission; invalid images are prevalidated before writes; transfer failure is treated as fatal/fail-closed rather than pretending rollback; component fixtures cover zero-QSA, 256/512-expert geometries, FP16/INT8/Q4 and distinct spare keys. Windows admission helper has separate MSVC coverage. P51 root/state import should mirror this distinction between **invalid-before-write** and **failure-during-transfer**.
- **NVMe tier convergence:** Strata #52's whole-session NVMe cache already demonstrated restart promotion (13 fresh tokens after restore in ~350 ms in its earlier simple design) and round-robin ~110K sessions. The author now has the simple NVMe cache working against the #57 shared snapshot API and is replacing full-snapshot-per-turn writes with a **delta-based cache** to reduce NVMe traffic and fork duplication. Treat delta persistence as work-in-progress until its bounded staging / atomic identity / durability tests land.
- **NEW oMLX greedy verifier semantic bug — `26375259`:** serial MLX greedy sampling takes argmax **after** bf16 `logits - logsumexp(logits)`; row-exact Lightning verify had taken argmax of raw logits. Adjacent bf16 logits can collapse to one rounded log-probability, changing the tie winner even with otherwise exact row kernels. Both verify paths now choose from the same log-probabilities as serial decode. P51 exact-verifier rule: **acceptance/token equality must reproduce the serial sampler's numerical pipeline, not merely raw-logit argmax**.
- **oMLX row-exact format rule corrected:** MLX 0.32.2 uses qmv_fast K alignment **512 for 4/5-bit but 256 for 6/8-bit**. A verifier that keyed all widths to K%512 could execute different arithmetic from serial one-row decode. This is latent for current Flash-Next served shapes but directly relevant to heterogeneous P51 mixed-bit verification. Kernel-choice identity is part of exactness.
- **NEW oMLX late-join handoff — `65515c3c`:** a filtered shared-MTP batch could leave a singleton then replay its entire history when a pending request joined. A production ~111K row re-prefilled for ~2 minutes, held both responses to **122 s TTFT**, and raised process memory 88 -> 116 GB. Because the survivor is already at a drained verify frontier, oMLX now hands it off with at most one forward instead of replay. P51 rule strengthened: when a state machine is at a materialized/drained committed frontier, **handoff the live state; do not reconstruct it by history replay**.
- **NEW SGLang peer-snapshot bootstrap series:** a booting router rank subscribes before fetching a peer snapshot, holds incoming delta batches, vets the snapshot before tree mutation, applies it on the single writer, proves watermark continuity, then releases held events. This is strong cross-runtime corroboration for the P51 CUDA->Apple/persistent-state transaction model: subscribe/capture deltas before snapshot, validate whole image, apply atomically on one state owner, prove splice continuity, then expose it.
- **SAME-DAY CURRENT stronger-Apple evidence:** a self-reported M3 Ultra 96-GB Q4 Flash-Next full-262K run reports **55-60 TG decode, ~667 cold PP and ~0.3-0.8 s cached-turn prefill**, with ~90% GPU memory allocation and little desktop headroom. Useful as long-context Apple transfer evidence only; it is M3 Ultra, not exact M1/TB4.
- **RECOVERED CURRENT — TensorFold 0.3.6.3 exact NVFP4 Flash CUDA:** published Flash-Next NVFP4 checkpoints now run on one CUDA GPU with drafted replies equal to serial, resumed prompts equal fresh, and **84/84 concurrent streams equal their solo runs**. On one DGX Spark the NVFP4 path decodes **1.13-1.52x vLLM** on the same checkpoint. Two-rank NVFP4, PLE-on-SSD and images are still refused pending qualification. P51 consequence: useful exact-concurrency and Blackwell-format evidence, but not an exact 5070-Ti ladder.
- **RECOVERED CURRENT — TensorFold decode-share scheduling:** on M3 Ultra, long prompt prefill is chunked so already-running replies receive rounds between chunks. With three incoming ~17K prompts, the running reply's longest pause falls **164 s -> 7 s** while the request-alone time is unchanged. This strongly supports phase-interleaving/fairness as a production-agent target separate from aggregate PP.
- **RECOVERED CURRENT — TensorFold warm long conversations:** under an emulated 64-GB budget on M3 Ultra, one Qwen3.8-27B conversation grows to **143K tokens** and resumed turns remain **38-46 s**, where 0.3.6.2 had fallen back to full re-prefill beyond ~100K. The fix avoids evicting good checkpoints before confirming the new one fits and shrinks DFlash2 prompt-tap state from 114 KB/token to 64 KB/token. Cross-hardware evidence, but it reinforces P51's resident/resumable-capacity distinction.
- **RECOVERED CURRENT — TensorFold M1-M4 prompt-kernel work:** Flash-Next MoE prompt tiles are scheduled per expert and QSA block-score/top-k prompt kernels are specialized for M1-M4, preserving bits; M3 Ultra Flash prompt speed improves only a few percent. This is useful implementation corroboration, not a new M1 Max end-to-end receipt.
- **No new reproducible exact-M1-Max Flash receipt** in this window. The ~27-TG M1-Max comment remains unpublished and does not move the dual-M1 probability ladder.

**Target effect:** raise Strata cold-PP centers based on the full physical 12-GB RTX 5070 matrix; do not move Strata TG, AA priors, or dual-M1 Flash TG/PP. Persistent RAM parked-state confidence is materially stronger, but same-runtime RTX timing is not credited as Apple restore latency.

### 2026-09-29 10:01 UTC Strata-0.1.22 / Swift-Flash / checkpoint update

- **NEW Strata 0.1.22 prompt path (strict window):** the 12-GB RTX 5070 path now has several measured prompt-side gains. Exact intermediate receipts include IQ3_S 32K **1143 -> 1213 PP** from the asynchronous expert issuer, Q2_0 32K **1386 -> 1646 PP** from tensor-core QSA attention, and a Q2_0 128K prompt **1144 -> 1596 PP (+39.5%)** on the combined branch. The 128K run's KV staging was only **1.331 s of 81.3 s (~1.6%)**, so further gains there are not primarily a KV-copy problem. This physically clears the current P51 **IQ3_S 32K >=1200 PP** target on a weaker 12-GB 5070, raising confidence in that target; it does **not** yet justify raising the 64K/128K IQ3_S or IQ3_XXS PP centers without a final same-quant matrix.
- **Prompt attention precision tradeoff is explicit:** Strata's new QSA prompt-attention kernel uses FP16 tensor-core MMA with FP32 accumulation and measures **3.2e-6 relative error vs FP64** (old FP32 kernel 2.5e-6). On Q2_0 32K it reduces attention 5216 -> 1318 ms and prompt 1386 -> 1646 PP. It is intentionally not bitwise; the model amplifies summation-order differences even when kernel error remains tiny. P51 rule: prompt-only approximate/fp32-level paths require full-state/logit/trajectory gates and must stay separate from exact verifier certification.
- **Strata decode regression scare resolved:** a same-box release A/B on RTX 5070 Q2_0 measured 0.1.13 at 73.1/76.2 TG and 0.1.21 at 73.8/74.3 TG. The reported ~50% user regression was not reproduced. This supports treating 0.1.22 as prompt-side progress rather than a decode-target reset.
- **RECOVERED CURRENT — Swift 1.5 Flash-Next becomes a first-class alternate Flash checkpoint:** UkisAI's BF16 xhigh comparison at 262K shows GPQA-D **89.80 -> 89.60** while mean thinking tokens fall **17,683 -> 7,823 (-55.8%)**; LiveCodeBench v6 **88.40 -> 90.39** with **-44.8%** mean thinking tokens; AIME mean tokens **-31.3%**, HMMT **-35.1%**, MMLU-Pro **-57.0%**. Terminal-Bench 2.1 improves **67.64 -> 69.66** but mean total output tokens rise **11.9%**, so the efficiency gain is workload-dependent and not universal.
- **Independent agentic corroboration — Swift Flash Aider:** one paired community run at xhigh reports base Flash **90.7% retry pass, 17,646 tokens/case, 1542 s/case** versus Swift Flash **86.9%, 6,991 tokens/case, 608 s/case**; paired n=107 gives 99 agreements, 2 Swift gains, 6 losses, McNemar p~0.29. Treat this as strong task-seconds evidence, not proof of exact equivalence. It supports an alternate production lane where solved-task wall time and tokens/solve are primary metrics.
- **Swift Flash physical speed per token appears unchanged in Strata:** on the same engine/quant family, Strata documents 4K IQ2_XS at **465 PP / 78.7 TG** for Swift versus **467 / 78.3** for base. This makes Swift's task-time advantage mostly a token-demand effect rather than a faster architecture.
- **Swift Flash compact quant caveat:** current Swift-specific GSQ-RCO releases are IQ3_XXS **75.97 GB**, IQ2_XS **68.15 GB**, Q2_0 **66.55 GB**. Their published refinement/KLD work is mostly 512-token; it explicitly does **not** establish long-context capability parity. Standard GGUFs do publish 32K KLD, but that does not certify the compact GSQ-RCO long-context lane. P51 must separately certify the chosen Swift compact quant at xhigh, 128K+, tools, MTP acceptance and repeated-agent trajectories.
- **NEW vLLM recurrent prefill-checkpoint corroboration — `3e2a7e74`:** GLM-5.3 FlashKDA now exports both convolution and recurrent checkpoint state at aligned prefill offsets, and tests resumed suffixes against uninterrupted prefill with and without speculative rows. This independently reinforces the P51 full-state root rule: recurrent checkpoint state must be materialized at a valid prefix boundary, not reconstructed from KV alone.
- **NEW llama.cpp Metal FWHT optimization — `18bbc46b`:** 512-wide FWHT moved from the one-simdgroup path to the 256-thread threadgroup kernel. No end-to-end Qwen receipt is published, so this is only implementation support for the rotated/Hadamard low-bit search lane, not a target-moving result.
- **RECOVERED newer-Apple Flash fork, not M1 evidence:** a public M5 Pro 64-GB llama.cpp fork reports ~367 PP @4K, **27.6 TG** with depth-3 MTP, **18-18.6 TG** target-only, and **20.6 TG at ~29K real-chat context**. Gathered sparse attention is reported +19% at 62K and +50% at 130K, Metal MoE fusion +5-9%. Useful mechanism evidence, but it is **M5 Pro**, not the previously discussed M1-Max anecdote, so it does not move Apple7 calibration.
- **No reproducible M1-Max 27-TG fork landed in-window.** The prior exact-chip report remains a lead only.

**Target effect:** add a **Swift-Flash effective-task-throughput lane** parallel to base Flash; physical 40-TG/400-PP dual-M1 targets remain unchanged. Raise only the **Strata IQ3_S ~32K PP >=1200 planning confidence** based on the direct weaker-card receipt; long-context Strata PP centers and all TG centers stay unchanged.

### 2026-09-29 06:21 UTC protected-islands / heterogeneous-PP / task-throughput update

- **NEW direct Flash mixed-precision allocation evidence — mlx-serve `65b9c2e0` (M5 Ultra):** a `mid48` repack moves 2.88 GB of non-expert projections from 8-bit to 4-bit while keeping **lm_head, embeddings, hyper-connections, router gate, GDN in_proj_a/b, attention k/v, indexer, PLE and the MTP head at 8-bit**. The pack shrinks 75.30 -> **73.86 GB** and S=1/S=4 forward time improves **11.2% / 4.9%**, while MMLU-Pro-400 is 346 versus 340/338 controls. An all-4-bit non-expert control is faster still at S=1 (-14.7%) but emits **12.8% more tokens** and hits the 8,192-token cap on 7 questions. **P51 quant rule strengthened:** protect hyperconnection/router/recurrent-control/indexer/PLE/MTP islands; compress bulk q/o/GDN-body/shared-expert paths more aggressively only after xhigh agent certification.
- **Verifier-format coupling is now explicit:** mid48's faster target forward produces **no 4-stream decode gain (39.0 vs 38.9-39.1 TG/request)** because the joined verifier supports only 8-bit weights, forcing the new 4-bit projections onto a slower per-request verify path. A 4-bit verifyQMM probe gained ~4.8% at four streams but was not bit-exact and was rejected. P51 must optimize **quant allocation x verifier-kernel support jointly**; a smaller/faster target quant does not count if it de-optimizes or numerically changes verification.
- **NEW heterogeneous layer-PP receipt — Strata 0.1.21 / `f1b1d961`:** on Windows with RTX 5080 x16 + RTX 3090 x4 Gen4, Coder IQ1_M at 32K/int8-KV/spec4 is split by contiguous layers, with each stage owning its session state, verify window and expert cache and only one residual hand-off per verify window. Best K=26 measures **2,039 PP @16K / 2,357 PP @28K** versus 2,045/2,005 on the 0.1.20 5080 control, and **83.8 story / 109.7 code TG** versus 83.2/88.2. Same-GPU split is 10/10 byte-identical; cross-GPU expert execution changes rounding. A slower third 2080 Ti hurts decode. **P51 topology rule:** stage-local residency plus infrequent hand-off can make weak interconnect useful, but stage compute balance dominates once expert residency saturates; never add a slow stage merely for capacity if faster stages already hold the hot set.
- **NEW exact-chip Apple7 lead, not yet a receipt:** a MoEspresso user reports an unpublished fork reaching **~27 TG on an M1 Max 32-core** after a kernel rewrite, up from their earlier ~14 TG tuning. No fork, context depth, MTP/acceptance settings or reproducible command is public yet. Track as a high-priority Apple7 upside lead; **do not move the single-M1 Flash calibration or dual-M1 40-TG confidence until the fork/settings land**. Source: https://www.reddit.com/r/LocalLLaMA/comments/1wrqql8/qwen38flashnext_125b_at_1215_toks_on_a_2021_32gb/
- **NEW high-end Flash concurrency receipt — 4x R9700:** a current TP4 deployment of tcclaviger's MXFP4/FP8 Flash-Next reports **150+ TG single stream, ~100 TG each at 3-5 concurrent streams, and 10K+ PP**, with ~7.8 GB total KV allocation said to support roughly four 262,144-token sessions while each 32-GB card sits near 31.5 GB used. This is valuable evidence that Flash-Next's sparse state can support high aggregate agent throughput; it is **not numerically transferable** to M1/TB4 or a single 5070 Ti. Source: https://www.reddit.com/r/LocalLLaMA/comments/1wsxgbo/first_few_days_of_qwen38flashnext_on_4x_r9700_its/
- **RECOVERED CURRENT Swift task-throughput anchor:** a ~630-task RTX 3090 HyperQwen comparison measures base Qwen at **108.1 s/task, 8,985 output tokens/task, 112.1 TG** versus Swift 1.5 at roughly **68-72 s/task, 5.67-5.75K tokens/task, ~104 TG** depending head quant. Swift is physically slower per token yet finishes the workload roughly one-third sooner because it emits far fewer tokens. This materially strengthens the already-promoted **effective solved-task throughput** lane; physical TG remains separate and base Qwen remains the quality control. Source: https://www.reddit.com/r/LocalLLaMA/comments/1wsqjku/swift_15_hyperqwen_37_less_task_completion_time/
- **NEW phase-specific collective rule — SGLang `c7be3e93`:** on an 8x sm120 switch-free PCIe host, FlashInfer PCIe-IPC all-reduce is dramatically faster than NCCL for decode-size reductions. But sizing the workspace for prefill hurts TTFT **1910 -> 3176 ms** and at 128K/C4 regresses TPOT ~45%; a decode-sized workspace yields **1849-ms TTFT / 13.62-ms TPOT / 48.05 output TG** versus NCCL's 1910/21.14/35.02. P51 rule: communication kernels/workspaces must be selected and budgeted by **phase and verify/decode row shape**, not one maximum prefill geometry.
- **NEW long-context attention corroboration — oMLX `07d88dbd` (MiMo/M5 Ultra, cross-model):** a split-key matrix attention path changes end-to-end decode **108.6 -> 111.7 TG @8K, 73.9 -> 88.4 @64K, 40.2 -> 69.0 @256K** while prefill is unchanged. This reinforces the existing P51 rule that long-context decode/verify attention needs its own execution plan; do not transfer MiMo/M5 percentages to Qwen/Apple7.
- **NEW speculative metadata reuse — vLLM `35d6fb31`:** fused multi-step draft decode can reuse one decode-metadata build while sequence lengths advance in place and block tables remain fixed. Treat speculative metadata as persistent per verify cycle where its invariants permit; do not rebuild it mechanically each draft step.

**Target effect:** none. The new evidence strengthens protected-island quantization, stage-local heterogeneous PP, Swift task-efficiency and long-context/concurrency mechanism confidence, but there is still no reproducible new exact 2x-M1/TB4 Flash receipt or exact-user-5070Ti Strata ladder that warrants moving canonical TG/PP probabilities.

### 2026-09-29 02:19 UTC persistent-root / Swift / exact-state update

- **PERSISTENT CANONICAL AGENT-ROOT IMAGE PROMOTED:** stable system/tool/extension prefixes should be materialized once as complete hybrid state, persisted across process restarts, and restored/cloned for new agent sessions instead of paying cold prefill repeatedly. Treat three mechanisms separately: (1) logical prefix reuse, (2) persistent forkable root images that save compute/TTFT but normally materialize a private copy per agent, and (3) the final physical shared-root/COW design that stores one immutable root while independent private suffixes branch from it. Only (3) earns shared-memory capacity credit.
- **Direct restart-safe evidence is now multi-runtime:** patched llama.cpp Qwen3.8-Flash-Next restored a 5,892-token hybrid checkpoint in ~153 ms and then processed only 4 tokens / ~508 ms versus ~19.1 s cold; stock slot restore silently re-prefilled because recurrent context checkpoints were not persisted. TensorFold independently spills a 35,583-token Qwen3.8-27B conversation (2.2-2.4 GiB) to NVMe in ~0.18-0.19 s, reloads it in ~0.24 s and answers in ~2.3 s versus 26.2 s cold, byte-identical. NInfer independently persists paged target+MTP KV, GDN state, MTP tail hidden, checkpoint ring and prefix identity; a 6.9K session is ~416 MiB, saves in ~0.24 s and restores in ~0.12 s. These are same-runtime checkpoints, not CUDA->MLX portability proof.
- **Pi root-cache pattern is operationally useful:** a user-supplied Pi extension uses llama.cpp slot persistence plus 32 context checkpoints / 4,096-token minimum checkpoint spacing to reuse an invariant Qwen3.8-27B system+tools root across different Pi sessions and restarts. Its fragility to prompt-rendering changes (for example cwd/template changes) confirms that the root identity must hash exact model/quant/tokenizer/template/system/tools/extensions/reasoning/runtime-state schema. Any mismatch is a hard miss.
- **FULL-STATE CONTRACT REAFFIRMED:** target KV alone is insufficient. llama.cpp still has a separate open gap where a slot save/restore can omit live draft-model `ctx_dft` state; P51 persistent roots and CUDA->Apple imports must include target attention KV, recurrent/GDN state, QSA/indexer state where applicable, checkpoint metadata, MTP/draft state, positions/RoPE lineage, sampling/behavioral identity and the materialized committed frontier. Incomplete state must fail closed to replay/re-prefill.
- **SGLang Rust TreeCore corroboration (strict-window NEW, 02:18:57 UTC):** SGLang made its Rust radix-tree core the default and now explicitly pauses internal Mamba/SWA eviction for host backup before tombstoning device state, including SWA relocation/rotation-base handling. P51 rule: eviction/demotion of a shared or persistent root cannot free hybrid internal state until the backup transaction is complete; metadata for physical location may need refresh after allocator compaction.
- **Swift 1.5 becomes a first-class alternate 27B checkpoint lane, not a TG claim:** UkisAI's Qwen3.8-27B derivative keeps the base architecture/MTP lineage while materially reducing reasoning-token demand on xhigh BF16 evaluation; published mean-token reductions vary by workload (~16-54%) rather than being one universal 58.5%. LiveCodeBench improves while using ~24.5% fewer mean tokens, and Terminal-Bench improves with ~16% fewer. P51 should therefore measure solved-task wall time, reasoning tokens and tool trajectory length beside physical TG/PP. Base Qwen3.8-27B remains the control; Swift cannot replace it until the xhigh AA/tool/long-context suite passes.
- **Swift quant lane:** Swift-specific GSQ-RCO IQ3_S+MTP is ~12.12 GB and is an attractive Apple capacity artifact, but its published low-bit distribution tests are short-context. Use the allocation as a prior for a P51 mixed-bit Swift artifact; require the same xhigh, long-context, tool, MTP-acceptance and repeated-agent certification as base.
- **SSD expert streaming is mechanism evidence, not a new long-context speed anchor:** InferredThoughts runs full 176.9B Flash-Next on a 16-GB RTX 5060 Ti by keeping only ~20 GiB model data resident and streaming experts/ngram rows from NVMe. Its own depth table falls from 10.40 TG near 0.2K to 8.35 at ~6K and 6.88 at ~29K; cold PP is ~49.2. Promote GCLOCK-like dynamic expert residency, layer-ahead prefetch and explicit SSD-bytes/token accounting as research seams, but do not transfer the 9-10 TG headline to 128K or to Apple.
- **STRICT-WINDOW DFlash2 quant guard — mlx-serve `cb24806f` (02:07:33 UTC):** DFlash2 selector predecessor/successor codebooks are consumed by dense gather and a generically quantized packed codebook can make every draft invalid. The loader now refuses the shape at startup. P51 allocator rule: keep tiny selector/codebook/control tables in dense BF16/F16 unless the runtime has an explicitly qualified quantized-gather path; fail at load rather than interpreting zero acceptance as model quality.
- **STRICT-WINDOW exact-fusion evidence — oMLX `4626613b` (02:12:26 UTC):** the GLM-5.3 stack demonstrates that exact decode/verify fusion can remove thousands of host/GPU dispatches while retaining bitwise reference arithmetic; on M5 Ultra an earlier fused stage in this stack moved greedy decode from 38.9/38.7/32.7 to 51.7/51.2/49.0 TG at pp200/1024/4096. The combined work also found several attractive fused paths slower in-model despite microbench appeal and leaves them default-off, and uses first-use exactness checks/fallbacks. Cross-model lesson only: fuse the actual dependent chain, certify real-model parity, and keep a per-family fallback; do not transfer M5/GLM percentages to M1/Qwen.
- **RECOVERED 3-bit quant warning/opportunity:** a separate R9700 W3A4 rotated-INT3 Qwen3.8-27B release (~3.1 bpw) keeps 61,440-token needle retrieval at 100% and GSM8K/HumanEval within paired uncertainty versus its MXFP4 control, but loses a statistically significant ~2.9 points on the reported MMLU-Pro subset. This supports continued protected-island / rotation experiments below 4 bits while reinforcing that retrieval parity is not source-like intelligence certification.

**Target effect:** physical TG/PP centers remain unchanged. Durable planning changes are the new persistent-root-image objective and the Swift effective-task-throughput lane. Persistent-root restore latency is a separate metric from honest cold PP; Swift token-efficiency is a separate metric from physical TG.

### 2026-09-22 15:59 UTC warm-prefix / hybrid-draft-state / Apple7 DFlash2 update

- **NEW exact-window merged warm-tail reuse — oMLX #3835 / commit `8288884d9b4f`:** paged prefix caching now preserves a short terminal tail snapshot immediately before the chat template's generation prompt instead of re-prefilling everything after the last full 2K/4K block. On Qwen3.6-35B-A3B at a 13.4K prompt, next-turn re-prefill falls **1,174 -> 37 tokens** and TTFT **0.83 -> 0.42 s**. Ten-turn 100K-164K conversations with Lightning MTP across Qwen3.8-27B, Flash-Next and DeepSeek-V4.1 reused the previous prompt minus the generation marker and recovered correctly after forced partial misses. **P51 rule:** cache identity/publication must include a verified terminal-tail lineage, and generation-prompt boundaries deserve explicit snapshots rather than rounding every reusable prefix down to the full-block grid.
- **NEW exact-window hybrid draft-prefix repair — oMLX #3840/#3842:** SpecPrefill's Qwen3.8 hybrid draft path had two independent defects: it inferred logical position from `cache[0]` even when layer 0 is recurrent and has no offset, and draft stores published no recurrent boundary snapshot. The combination made restored draft-cache state either silently treated as empty or rejected as placeholder state. #3840 derives position from actual attention layers and fails closed on indeterminate state; #3842 captures reusable recurrent state at a reachable boundary. In one 27B-target/0.8B-draft run, draft-cache hits change **0 -> 23 of 27 scorings**, with representative warm scoring reductions from multi-second full-prefill costs to **~0.3-0.8 s** and 38.7 s actual versus 140.4 s baseline-equivalent across that treatment trajectory. **P51 rule:** target prefix reuse and draft/speculative prefix reuse are separate state machines; hybrid draft caches require their own recurrent checkpoint at an actually reachable token boundary.
- **RECOVERED exact M1 DFlash2 precision trap / opportunity — incoai Qwen3.8-27B-DFlash2 discussion #3:** on an M1 Max 32 GB, an older oMLX DFlash2 path automatically cast a quantized draft to **FP16** because BF16 is emulated on M1/M2; the fused DFlash2 forward produced NaNs, acceptance collapsed to **0%**, and speculation became far slower than plain decode. BF16 stayed finite, while forcing quantized weights with **FP32 activations (`w4a32`)** reproduced BF16-like acceptance and the reporter measured roughly **25 TG**, slightly above the plain ~19.6-TG arm in that debugging session. **P51 Apple7 DFlash2 rule:** activation precision is part of drafter identity. Before any throughput result, assert finite hidden/logit tensors and nonzero acceptance; benchmark FP32-activation and BF16-reference drafts before considering FP16. Do not diagnose a zero-acceptance Apple7 run as 'DFlash2 does not work on M1' until this gate passes.
- **DFlash2 + low-bit target remains a legitimate 27B branch:** llama.cpp's merged DFlash2 implementation already verifies blocks against the target and accepts independently quantized draft weights; the official Q4 target study reports **1.77-1.85x AR** on M5 Pro. Public IQ3_S target packages are explicitly paired with external DFlash2 drafts, so DASLab/GSQ-RCO does not need an embedded MTP head to test this topology. There is still **no clean DASLab+DFlash2 M1 Max receipt**, so P51 must measure it rather than transfer CUDA/M5 multipliers.
- **UPDATED PLE-metadata lesson — vLLM #58114:** the Qwen3.8 PLE builder optimization now has end-to-end GB200 data. The microbuilder is ~32-48% faster, but serving is **-1.52% output TG at C1** and **+4.96% at C8** in the reported ABBA. This is a strong warning against converting metadata microbench wins directly into B1 forecasts; PLE/runtime metadata work must be certified at the actual concurrency/verify-width shape.

**Target effect:** none. These results materially improve warm-agent TTFT/speculative-state reuse and make the Apple7 DFlash2 experiment more concrete, but they do not replace the current cold-PP/B1 target receipts. Single-M1 27B remains 25 TG (~65% >=25 planning confidence), and dual-M1 Flash remains 40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence.
### 2026-09-22 10:43 UTC hardware-policy / Blackwell-IQ correctness guard update

- **NEW exact-window 5070-Ti-relevant toolchain guard — llama.cpp #28581 / #28784:** consumer Blackwell `sm_120` can silently produce garbage for `IQ1_S` / `IQ2_S` / `IQ3_S` tensors when llama.cpp is compiled with **nvcc 13.2.51 or 13.2.78 (CUDA 13.2.0/13.2.1)**. Independent reproductions on RTX 5060 Ti and RTX 5080 show both `MUL_MAT` and `MUL_MAT_ID` failing with large numerical error, while sibling `IQ3_XXS`, `IQ4_XS`, XS-family and K-quants remain correct. The same source tree built with **CUDA 13.2.2 (nvcc 13.2.86) or newer 13.3/13.4** passes and restores coherent Qwen3.8-27B generation. PR #28784 implements a `__byte_perm` workaround but was closed unmerged after the compiler fix was established. **P51 5070-Ti rule:** the DASLab/GSQ-RCO `IQ3_S` lane must record CUDA/nvcc identity and run the IQ `MUL_MAT` + `MUL_MAT_ID` correctness gate before any benchmark. Do not interpret garbage/low quality from the broken toolchain as quant degradation.
- **NEW exact-window Apple kernel-policy identity rule — Splash #96:** on an M3 Ultra Apple9 **60-core** GPU, Splash 1.0.2's newer matrix-decode policy gives silent garbage at B1 with **0 draft acceptance** and kills the engine at B>=2, while 1.0/1.0.1 on the same machine/model are correct. The reporter points to a policy validated on smaller Apple9 configurations; this mirrors #95's Apple7 real-model failure despite passing unit kernels. P51 must key kernel-policy certification by at least **Apple GPU family + GPU core count + batch/verify width + model/quant identity**, and preserve an escape/fallback policy. 'Apple9 validated' or 'Apple7 validated' is not sufficient by itself.
- **NEW exact-window Splash scheduler work #97/#98/#99:** current changes only pre-reserve small scheduler/admission containers and propose removing temporary prefill-admission `Request` copies. Focused tests pass, but **no end-to-end speed result exists yet**; the authors explicitly removed a cache-probe optimization that risked turning one deep-state lookup into per-page lookups on long prompts. Track as a CPU-overhead candidate for Apple7, not performance evidence.

**Target effect:** none. No new dual-M1/TB4 Flash receipt, no new exact M1 27B speed receipt beyond #95, and no 5070-Ti throughput result displaced the current frontier.
### 2026-09-22 09:29 UTC Apple7 Splash / dynamic-expert-residency update

- **NEW exact M1 Max 64 GB / Qwen3.8-27B evidence — Splash #95:** on an M1 Max 32-core GPU / 64 GB, the existing Splash Q4 engine runs correctly after lowering the Apple-family gate and selecting an Apple7-specific kernel policy; the report says **no kernel implementation changes were required**, only policy choices. Full Metal engine tests pass. Tuned end-to-end decode across three short prompts improves from **23.2 / 14.0 / 23.7 TG** to **25.7 / 15.4 / 25.8 TG**; the tuned three-prompt mean is ~22.3 TG. A 7,244-token cold prompt improves from **~34 PP (211.6 s TTFT)** to **~49 PP (146.6 s)**. The tuned policy is byte-identical to the untuned Apple7 build on the reporter's greedy single-request and 3-concurrent-request A/B.
- **Apple7 numerical warning — real-model parity outranks kernel unit tests:** enabling the newer `LinearTile::Simdgroup` decode policy on Apple7 passes its 672-case kernel test yet produces obviously wrong real-model greedy text, multi-lane divergence, and only **8.6-9.8 TG**. `tune-kernels` also flags the affected M24 candidates. P51 must therefore require real-model greedy/logit/trajectory parity before promoting any Apple7 tile/fusion even when isolated kernel tests pass.
- **P70 sequencing change:** first reproduce/port the measured Apple7 policy from `paperniuk/splash` commit `8b76480b0e9a` — N128x8 prefill where supported and Split64x8 one-lane decode for eligible projections — before writing a new persistent Q8 verifier kernel. This materially lowers the engineering-risk estimate for bringing Splash-style mechanisms to M1, but does **not** prove full Flash-Next or PP2/TB4 throughput.
- **Single-M1 27B planning update:** exact-hardware evidence now reaches ~25.8 TG on two of three prompts, while one prompt remains acceptance-limited at 15.4 TG. Raise mature **>=22 TG confidence ~80% -> ~90%** and **>=25 TG confidence ~55-60% -> ~65%**. Keep the 25-TG working target, >=28/30 stretch cells, and 110-PP target unchanged.
- **RECOVERED direct Flash expert-residency evidence — llama.cpp #27861:** Qwen3.8-Flash-Next routing over a 54K-record mixed workload shows weak transferable **static** expert skew (top-32 learned on half covers only ~10% of the other half) but strong **temporal locality** (simulated per-layer LRU-64 ~67% hit, LRU-128 ~81%). A GPU-resident cache for host-offloaded experts raises one 2x3090 Flash setup **18.4 -> 24.2 TG (+31%)** with 48 slots/layer (~4.1 GiB VRAM). Community follow-ups show that admission/churn policy, staging/fences, speculative small-batch correctness and physical residency thresholds can dominate the benefit. This is not M1 evidence, but it makes **dynamic expert residency** a legitimate P51 research branch: keep all 512 experts, tier hot experts rather than pruning them permanently, and measure hit rate, bytes promoted, upload/eviction churn, speculative compatibility and agent-quality parity.

**Dual-M1 Flash target effect:** none. The Apple7 result removes a major 'newer-Metal-only' mechanism concern, but the decisive full-model PP2/TB4 measurement remains absent.
### 2026-09-22 06:05 UTC primary-lane Q8-upstream / single-M1-Flash / 5070-Ti update

- **NEW exact-window upstream Q8-27B path — Splash #94:** the previously external `npanj` Q8 work is now proposed directly against `incoai/splash` as PR #94 (created 2026-09-22 02:53 UTC). It adds schema-5 Q8 packages, Q8 decode/prefill/vocabulary/embedding kernels, and importantly `pack_mixed_q8.py` for **chosen-layer Q8 / mixed-precision packages**. On M5 Pro the PR reports ~37 TG average versus ~61 TG Q4 across the author's broader comparison and fresh E2E probes of **58 TG arithmetic / 46 TG code**. This does **not** solve M1: only Apple10/M5 was tested, Apple9 is explicitly untested, and Splash still has no Apple7/M1 backend. P51 consequence: P70 should track the upstreamable #94 kernel/package design rather than the old fork, especially the mixed-Q8 packaging path, but an Apple7 verifier/kernel port is still required.
- **NEW exact-window KV-format evidence — Splash #91:** Splash now has an optional BF16 target-KV path beside default INT8. Across M3 Max and M5 Pro, INT8 default outputs remain bit-identical to main and measured long-attention / short real-model decode deltas stay roughly within ±1%; BF16 doubles target-KV memory and may be slower deep in context. 128K/256K attention coverage passed, although the full 27B native-256K matrix is incomplete. This supports keeping Q8/INT8-class target KV as the P51 default unless our own long-context quality/acceptance A/B shows a reason to spend BF16 memory; KV format remains part of cache/runtime identity.
- **RECOVERED single-M1 Flash experimental control — Litwein REAP320 FP16/MTPLX:** an M1/M2-native FP16 sibling of a REAP-320 Flash-Next build keeps **320/512 routed experts**, uses 3-bit routed experts plus 5/6/8-bit sensitive tensors, streams the 4-bit PLE table, and reports **3.84 bpw / ~37 GiB resident weights** with a measured **39.7 GiB resident floor**. Its MTPLX contract pins depth-2 MTP and a self-distilled 8-bit drafter trained on long-context agent/reasoning traces. The identical BF16 weights on M4 Pro 48 GB report **~31-35 TG**, **33.8 TG at ~85K**, and ~180-196 PP at 46K; the FP16 pack itself has **no M1/M2 timing**. This is a useful single-M1 Flash runtime/acceptance sandbox, not a production candidate: pruning 192 experts plus 3-bit routed experts is explicitly lossy and no task/AA certification is published.
- **RECOVERED date-only same-card 5070-Ti baseline:** a Sep-22 hands-on using PrismML llama.cpp on an RTX 5070 Ti 16 GB runs stock-family `Qwen3.8-27B UD-IQ3_S` fully on GPU at **65,536 context**, Q4_0 KV, one slot, no vision, using **14,388 MiB during generation** and sustaining **45.29 TG over a 26,620-token generation**. The page exposes the date but not a trustworthy publication time, so this is not treated as exact-window freshness evidence. It does not beat the existing P51 same-card ~51.3 TG @128K custom-MTP receipt; it strengthens IQ3_S as a robust baseline arm.
- **NEW exact-window target/draft identity rule — vLLM #58080:** on Qwen3.8-27B with YaRN extension, applying RoPE overrides to the target but not the MTP draft makes acceptance fall from healthy values below 262,144 to effectively **0% above the draft's native context boundary**, while target output remains correct and draft compute becomes pure overhead. P51 currently targets <=~180K/128K, so this does not alter our performance forecast, but target and draft positional/RoPE configuration must be an exact shared identity and mismatch should fail closed.

**Target effect:** none. No new exact 2x-M1/TB4 Flash receipt, no new exact M1 Flash speed receipt, and no same-card 5070-Ti result beats the current frontier. The additions improve the experiment menu and correctness contracts rather than the numeric planning distribution.
### 2026-09-22 00:18 UTC primary-lane cache-geometry / branch-state update

- **NEW exact-window distributed-geometry fix — vLLM #58021:** following the #58020 bug already in state, vLLM now has an explicit repair pattern: resolve hybrid prefix/cache geometry once in the coordinator, stamp the authoritative scheduler/hash block sizes into every `KVCacheConfig` before worker initialization, require late/restarted workers to adopt the published value, and **fail closed** if a consumer reaches the geometry before resolution or sees a conflicting value. This directly strengthens P51's dual-M1 PP2 rule: target KV, recurrent/GDN, QSA and MTP/checkpoint consumers on both stages must use one versioned geometry chosen by the coordinator; per-stage local inference of hash/checkpoint granularity is forbidden.
- **NEW exact-window branch-isolation rule — mlx-serve #492/#493, Qwen3.8-27B 8-bit:** on M4 Max 64 GB, an ~80K-token multi-turn coding-agent session with multiple hot-prefix entries restored ~79K tokens from a sibling branch and then hallucinated a response to the conversation's original `hi`, ignoring the current tool result. The fix treats MTP/DFlash hidden state as **branch-owned**: on any partial/diverging prefix match, speculative hidden state is discarded rather than adopted from the matched sibling branch, and the target restore point is snapped backward to a safe message boundary before replaying the suffix. P51 warm-agent cache identity must therefore include branch lineage and chat-turn boundary, not only token-prefix equality. A partial prefix match may reuse certified target/cache state, but draft/MTP state cannot cross branches unless lineage is exact.
- **PRIMARY-LANE SEARCH RESULT:** no new qualifying performance commit or receipt after 21:48:06 UTC on `mihailescu2m/llama.cpp`, `npanj/llama.cpp`, Kadir's M1 fork, MTPLX, the Harish 5070-Ti project, DASLab GSQ/RCO, APEX, oMLX, or mlx-serve. No new exact 2x M1 Max/TB4 Flash receipt appeared. The 5070-Ti frontier therefore remains the published ~51.3 TG @128K / ~24.6 @261K IQ3_S+MTP setup, and the single-M1/dual-M1 targets remain unchanged.

**Target effect:** none. This pass improves restore/distributed correctness contracts rather than throughput evidence.
### 2026-09-21 21:48 UTC DGPP two-node long-context / distributed-cache-geometry update

- **RECOVERED materially stronger two-node Flash-Next receipt — DGPP:** the model-specific C++/CUDA DGPP engine runs `nvidia/Qwen3.8-Flash-Next-NVFP4` on **2x DGX Spark / GB10** with tensor parallelism over RoCE, FP8 dense projections, mapped n-gram/PLE, BF16 KV and depth-one MTP. Its shipped two-node campaign reports **62.1-74.9 TG at C1** across five prompt classes and **119.0-136.9 aggregate TG at C4**; the same engine on one Spark reports 42.6-50.3 TG. This proves the previously recorded 41-48 TG dual-Spark SGLang receipts were far from the software ceiling.
- **RECOVERED exact-family deep-context mechanism — DGPP QSA radix selector:** commit `1f357dad7f12` (2026-09-21 04:14 UTC, therefore older than this pass's boundary) replaces a serial/underfilled long-context QSA top-k sort with exact radix selection. On the same 2-Spark NVFP4 deployment, decode pass time changes **43.39 -> 29.55 ms at 129,560 tokens**, **59.38 -> 31.36 ms at 260,062**, and **93.52 -> 37.06 ms at 520,742**, with **15/15 response hashes identical**, identical usage/steps, and tokens/pass staying **1.85-1.92**. That implies roughly **63-65 effective TG near 129K**, **59-61 near 260K**, and **50-52 near 520K**. This is direct evidence that exact QSA selection can become a dominant long-context decode tax and that removing it can keep two-node Flash speculative throughput nearly flat far beyond 128K.
- **P51 forecast effect:** this is still not a numeric Apple transfer: DGPP uses GB10 CUDA kernels and a much faster RoCE fabric with TP rather than Project 51's PP2/TB4 topology. But it is materially stronger exact-family, two-node, long-context evidence than the earlier ~41-42 TG receipt and directly demonstrates that model-specific runtime work can move a dual-node Flash deployment from the 40s into the 60s at P51-relevant context. Raise the P51 planning confidence for **>=40 TG @ ~128K from ~65% to ~70%**, **>=45 from ~40% to ~45%**, and **>=50 from ~20% to ~25%**. Keep >=30/>=35 and cold-PP confidence unchanged.
- **NEW distributed cache-geometry rule — vLLM #58020 (created 2026-09-21 21:44 UTC):** EngineCore can resolve a hybrid prefix-match unit from all cache-group geometries (example: attention block 16 + Mamba block 1600 => authoritative unit 16), while a worker that is not given that resolved value can locally derive 1600. The worker then computes recurrent checkpoint positions on the wrong grid, floors the checkpoint to zero and silently drops it. P51 must propagate **resolved cache/checkpoint geometry from the coordinator to every stage/worker as configuration state**; workers must not independently infer a geometry that the scheduler already resolved, and missing authoritative geometry should fail closed.
- **NEW exact-window wide-batch correctness evidence — DGPP #13/#14:** DGPP merged Qwen C16/MTP3 support for up to 64 verify rows on two Sparks and a conservative sparse-batch compaction scheme. Real Qwen NVFP4 two-node validation reached 16 active requests with matching rank operation streams; final sparse-compaction validation reports zero NLL differences and zero top-1 changes over 50,890 positions. The final compaction policy intentionally makes **no performance claim** after unrestricted contraction failed a numerical gate. P51 consequence: wide verify/batch remapping is a correctness identity; never assume shrinking physical rows is numerically safe merely because state addresses are preserved.
- **PREFILL qualification:** a separate PixelML two-Spark TP2/SGLang recipe reports genuinely uncached client-observed prefill **2,960 tok/s at 16K** with zero cached prompt tokens. DGPP's long-context cold prefill on the QSA campaign is about **1.39K tok/s at 129K**, **1.21K at 260K**, and **0.80K at 521K** (derived from prompt tokens / measured cold seconds). These are strong cross-hardware capacity receipts but do not justify raising P51's 400-PP confidence because Spark compute/fabric is not M1/TB4. They also temper the earlier speculative 5-7K cold-B1 Spark ceiling: that remains unproven.
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


### 2026-09-23 07:55 UTC xhigh quant / PP2 / verifier-economics consolidation

- **Production distribution is now xhigh-specific.** P51 no longer spends bandwidth solely to preserve medium reasoning. The production quant objective is the minimum Apple execution cost that remains source-like at xhigh across hard reasoning, coding, tool use, long-context retrieval and multi-turn agent trajectories. Medium/thinking-off remain diagnostic cross-tests for calibration-domain specialization, not production admission requirements.
- **Current quant search hypothesis:** start near ~3.5 average transformer BPW and test approximately 3.0/3.2/3.4/3.6 heterogeneous arms. The current likely source-like xhigh frontier is estimated around **3.3-3.6 average BPW**; this is an engineering hypothesis, not AA certification. Preserve QSA/indexer, recurrent/GDN-sensitive tensors, norms, router/shared experts, output/head and MTP-sensitive paths; compress routed expert mass most aggressively.
- **SiliconSpecies Swift/Splash:** reverse-engineered Splash packaging is operational and exposes a high-leverage norm-storage semantic (most BF16 norms use gamma+1, GDN norm excepted). The saturated 95/95 quality suite is a catastrophic-conversion guard, not source-intelligence certification. Keep real-model greedy/logit/agent parity above isolated kernel tests.
- **EXL3:** current converter/optimizer supports heterogeneous per-tensor recipes, HQ promotion and separate head/MTP/ngram precision. Treat trellis/KLD machinery as an allocation/runtime challenger, not proof that nominal EXL3 BPW maps directly to agent intelligence. PonyExl3 proves Metal execution viability but does not currently replace Apple7 production paths.
- **oMLX #3520 merged gathered-QSA:** removes full-cache transpose/copy from small-row decode/verify gathers. M5 Max reports +18% at ~134K and +28% at ~229K serial decode, +25%/+36% under adaptive MTP. Use stored-layout gather for small verify/decode widths and a width/context-sensitive alternate path for larger prefill widths. Do not transfer percentages to M1.
- **oMLX #3374 verify economics:** measured Flash-Next depth-5 verify cost on M3 Ultra is ~2.3x a target forward: +0.5x GDN sequential recurrence, +0.6x MoE expert union, +0.2x QSA indexer. Proposed MoE union dedup + chunked/TreeWY-style GDN verify target ~1.5x; 2.3x is measured, 1.5x is a hypothesis. This is now the central mechanism behind the ~40-TG thesis.
- **SGLang #39393 PP2:** Qwen4-Exp / Flash-Next PP2 is demonstrated across two physical nodes with temperature-0 correctness and production-like replay. The mHC boundary carries the wide hidden-state representation rather than a normal hidden+residual contract. PP2 feasibility is now high confidence; M1/TB4 throughput remains unmeasured.
- **SGLang #37792 expert residency:** at a 184/512-expert resident floor, ~84.3% routing mass is served locally and remote expert traffic collapses from 26 GB/token to 0.31 GB/token on the reported 24-GB GPU setup. Preserve stage-local dynamic expert residency as an architectural feature; never fetch experts across TB4.
- **flashnext-hybrid:** thin-link hybrid deployment independently shows high draft acceptance can still reduce throughput when speculative widths fragment target batches. Maximize accepted useful tokens per expensive target verification batch, not nominal acceptance. This strengthens multi-row PP2 verify scheduling.
- **oMLX #3771:** current public runtime still contains substantial verify-path regressions/fast-path misses. Instrument target/draft/verify fast-path engagement separately and treat public runtime TG as a moving implementation point, not a ceiling.
- **Qwen4:** Flash-Next remains the public architectural preview. Preserve PP2 stage ownership, external lookup placement, dynamic expert residency and heterogeneous allocation because these abstractions are more likely to transfer than whole-file quant assumptions.

**Planning effect:** retain **~70% confidence for >=40 TG @ ~128K** and the **400 cold-PP** working target. The new evidence improves architectural confidence and implementation specificity more than it changes the numeric forecast.


### 2026-09-23 10:19 UTC transport / PLE-bounds / quantized-DFlash loader update

- **NEW oMLX #3869/#3870 distributed-transport direction:** pipeline edges can be independently moved off the ordinary ring; #3870 additionally piggybacks sampled tokens and adds remote-prefill KV handoff. Current evidence is stand-in/integration correctness only, not ConnectX/vLLM hardware throughput. P51 transferable rule: stage-edge transport is per-edge state, must be preflight-verified, must fail back cleanly, and should carry control/token metadata on already-required activation messages where possible. No numeric forecast credit.
- **NEW vLLM #58325 PLE work-bounds rule:** Qwen4Exp PLE preprocessing must slice persistent workspaces to actual live token count rather than configured `max_num_batched_tokens`. The current PR is designed bit-identical but has no ROCm E2E result yet. Add actual-live-row/token bounds to every PLE/QSA/indexer profile.
- **NEW SGLang #40883 packed target-head evidence:** Qwen3.8-27B W8A16 packed `lm_head` can serve NEXTN and DFlash2 with essentially unchanged acceptance when the target quant method is used rather than requiring a dense `.weight`. Keep output/head protected, but allow an eventual Q8/W8 experimental head arm after xhigh/agent parity.
- **NEW SGLang #40884 draft-loader identity rule:** quantized DFlash2 drafts can preserve BF16-like acceptance only if module names used for quantization match checkpoint tensor names and unsupported tensor/layout mismatches fail closed instead of being silently dropped. Add a tensor-consumption/module-identity audit before finite-state and acceptance checks on Apple7 drafts.
- **RECOVERED exact-chip evidence — oMLX #3853:** on M1 Max 64 GB, automatically routing eligible Qwen3.5/3.6 FP16 B1/T1 GDN decode through the fused prework kernel improves whole-server decode ~5.8-6.2% across mixed 4/5/6-bit conversions with extensive numerical/server validation. This is same-chip / nearby-GDN evidence only; Flash-Next uses a distinct Qwen4 route, so do not transfer the percentage or raise the Flash target.
- **NEW llama.cpp #29305 quant-harness opportunity:** source-model tokens/logits can be cached once and reused to compare later conversion candidates. P51 should freeze a source-logit artifact for the quant allocation sweep, but retain the hierarchy: xhigh/agent behavioral evaluation > hard task behavior > held-out sequence behavior > KLD/logit divergence > PPL.
- **NEW negative cross-family evidence — llama.cpp #29298:** a sparse-FA prefill gate materially improves DeepSeek-V4 long-context PP (+23% at ~65K depth, +42% at ~131K) while the submitted Qwen4Exp benchmark remains ~1.00x. Do not transfer sparse-attention kernel wins across hybrid architectures without direct Qwen4Exp measurement.

**Target effect:** none. No exact dual-M1 Flash receipt and no new DASLab/xhigh quality result appeared. Keep the xhigh ~3.0-3.6 search, ~3.3-3.6 source-like frontier hypothesis, 40 TG @ ~128K / 400 cold PP, and ~70% >=40 planning confidence.


### 2026-09-23 13:53 UTC QSA restore / KV ownership / long-agent speculation update

- **DIRECT exact-family warm-restore rule — SGLang #40916:** Qwen3.8-Flash-Next host restore that reloads KV but leaves QSA compressed index keys stale shows KL ~0.39-0.87 versus a warm reference. Restoring a separately declared QSA compressed-key pool yields KL 2.9e-3/4.3e-3/5.9e-3 with matching argmax; packed-MTP acceptance is exactly 3.317 warm vs 3.317 host. QSA compressed/indexer keys are therefore mandatory durable state, not reconstructible decoration. A target-KV cache hit is invalid if the QSA sidecar is stale/missing.
- **STATE-MANIFEST architecture — SGLang #40913-#40917:** dependent KV/indexer/draft/Mamba/QSA pools should be explicitly declared with geometry/ownership and fail closed if a required pool is absent. P51 warm/sleep checkpoints should use a typed state manifest covering target KV, QSA/indexer state, recurrent/GDN state, PLE/history dependencies, draft/MTP state and PP-stage ownership.
- **KV-PP / LayerSplit transfer evidence — vLLM #58329:** layer-owned KV can materially raise cache capacity and HBM prefix-hit rate in cache-capacity-bound, ~90%-reuse workloads (supporting Ascend data: +46.65% one-node and +45.42% two-node input throughput), but cited non-pooling tests lose 2.30%-12.77%. P51 lesson: ownership bundles include KV+indexer+scales, but per-token remote KV broadcast is not a default decode strategy. Preserve stage-local state over TB4.
- **Flash FP16 path — oMLX #3873:** current draft enables FP16 PLE compute dtype and HC kernels while preserving packed oQ weights; current-main FP16 GDN/L2 verify/MTP acceptance is explicitly unfinished. Historical M2 Ultra dev2 data shows ~+38% PP and ~+13-15% decode at ~31K-62K but regresses ~4K decode; treat as motivation only. Keep M1-FP16 protected-island baseline high priority, with zero forecast credit until current-main real-model acceptance.
- **UPDATE oMLX #3869:** first MCDMA stage-edge transport is now represented in main; broader #3870 all-hop/token/remote-prefill work still lacks real ConnectX/live-vLLM hardware evidence. Message-contract confidence rises, throughput confidence does not.
- **27B long-agent speculation — EXL3 #403:** on RTX 3090 / Qwen3.8-27B EXL3 4.0 bpw at 90K-135K, native MTP holds ~69% median acceptance while a third-party DFlash2 EXL3 draft is ~41%; real-session DFlash2 and MTP decode overlap around the 40s TG with no clear DFlash2 E2E win. Keep native MTP as the 5070-Ti production baseline; DFlash2 must win the actual long prefix-cached agent workload before promotion.
- **SPEC correctness — llama.cpp #29313:** stale graph-allocation plans can alias output tensors and cut EAGLE-3 acceptance from alpha~0.53 / mean accepted length 2.10 to alpha~0.251 / 1.33. Add graph/output-liveness/capture identity to the acceptance-collapse diagnostic tree.
- **SPEC telemetry — vLLM #58340:** proposed draft tokens and actually verified draft tokens are different under adaptive verification. P51 must record proposed, verified, accepted/committed tokens, verify-width distribution and verify wall time separately.
- **Quantized draft loader convergence — vLLM #58343:** selector/head allocation must respect the draft quantization configuration and explicit ownership. GPU/model quality validation is still pending, so this adds no performance evidence beyond the already-promoted draft tensor-consumption gate.

**Target effect:** none. No exact dual-M1 Flash receipt and no new DASLab xhigh quality result appeared. Keep xhigh ~3.0-3.6 search, ~3.3-3.6 source-like frontier hypothesis, 40 TG @ ~128K / 400 cold PP, and ~70% >=40 planning confidence.


### 2026-09-23 16:30 UTC warm-cache boundary / sleep persistence / byte-budget update

- **PREFIX-TAIL checkpoint identity — vLLM #58368:** hybrid Mamba/GDN + MTP prefix reuse can match token hashes yet miss the required recurrent checkpoint boundary. A concrete 1,600-token prompt with 64-token hash blocks should reuse 1,536 tokens; saving state at 1,600 instead of the scheduler-shifted 1,536 boundary collapses reuse to zero. P51 cache identity must include logical matched length, actual resume boundary, recurrent/QSA/draft checkpoint token index, block geometry and runtime/model identity.
- **SLEEP/WAKE cache persistence — llama.cpp #29322:** current prompt-cache state can remain allocated throughout sleep and then be discarded during model reload, converting a pre-sleep 4-token warm hit into ~3.6-4.0K re-prefill after wake in the reported Qwen3.8-27B setup. P51's agent-wake acceptance must test the real post-sleep hit, not RAM residency. If a runtime cannot preserve logical cache state across unload/reload, P51 should own typed state persistence externally.
- **BYTE-BASED cache budget — llama.cpp #29324:** recurrent/hybrid cache entries have large fixed per-entry state; ~1.2K-token Qwen3.8-27B prompts grew private memory by ~640 MiB each in the reported setup, with ~27.5 GiB growth after 44 entries under an unbounded-byte cache. P51 cache eviction/capacity must account target KV, QSA/indexer, recurrent/GDN, checkpoint history, draft/MTP and metadata bytes explicitly; token count alone is not a capacity metric.
- **WATCH ONLY — SGLang #40925/#40929:** DSA-indexer and MTP KV-cache sharding work opened in-window, but both PRs currently have empty descriptions, no accuracy/performance evidence and failing CI. Track them for future state-ownership/sharding evidence; do not infer topology or target gains from titles/diff size alone.
- **Metal BF16 depthwise-conv compatibility — llama.cpp #28741:** missing f32 x bf16 mul_mv variants were merged, fixing BF16 depthwise 1D convolution on native-BF16 Metal devices. This is not M1-Max target evidence because the path is guarded by native BF16 capability. It further supports intentional FP16 protected-island compute on Apple7.
- **SECONDARY MiMo speculation evidence — oMLX #3877:** correct speculative serving requires isolated draft state, predictor-index preservation and full rollback after sliding-window cache rotation. MiMo M3-Ultra Lightning-MTP gains (+11% to +20% at 4K-32K) are non-Flash transfer only; author notes long-context token identity still varies across cache/batch conditions, so no P51 target credit.

**Target effect:** none. No new exact dual-M1 Flash receipt and no new DASLab xhigh quality result appeared. Keep xhigh ~3.0-3.6 search, ~3.3-3.6 source-like frontier hypothesis, 40 TG @ ~128K / 400 cold PP, and ~70% >=40 planning confidence.


### 2026-09-23 19:03 UTC Metal batching / PLE-system-cost / external-state-restore update

- **PROVISIONAL Metal long-context batch-risk — llama.cpp #29335:** an M3-Ultra/Qwen3.8-Flash report shows severe degradation when multiple long sequences share one Metal decode batch, while independent singleton processes scale much better. The exact ratios are not promoted because the maintainer says the custom script reports some effects incorrectly and the model is unsupported in that build. P51 nevertheless adds an explicit Apple7 B1/B2/B4/B8 long-context verifier-width benchmark and singleton-process control before PP2 multi-row overlap receives performance credit.
- **PLE microbench != system bottleneck — SGLang #40947:** a shared-host Flash PLE backend cuts gather time from ~11.2 us to ~2.2-3.6 us and removes one TP4 collective/step, yet whole-server decode is only +0.17% and the prefill-heavy workload is -0.26%. Prioritize verifier GDN/MoE, QSA/indexer geometry and PP2 occupancy ahead of PLE-collective elimination unless P51 profiling shows otherwise.
- **Exact-family external restore — vLLM #58413:** Qwen3.8-27B + MTP3 at 100K moves external adoption 0 -> 99,008 tokens by giving align-mode recurrent groups their own hash-block offload geometry. TTFT drops ~11.7-12.3 s -> 377 ms; restored and cold continuations are byte-identical and MTP acceptance remains 2.601. P51 warm state must support per-group checkpoint/chunk geometry rather than one global cache grid.
- **KV-PP concrete planning — vLLM #58428:** target layers receive explicit physical owners, draft/EAGLE state remains rank-local, logical scheduler blocks are decoupled from rank-local physical tensors, and transfer scratch is budgeted separately. PP4 unit tests report ~3.2x logical block-capacity expansion; runtime transport is not implemented, so no performance credit.
- **Progress-based liveness — vLLM #58422:** a Blackwell Qwen3.8 hybrid/MTP deployment can wedge with active requests and a 200 health endpoint while generation counters stop. P51 long-running service health must include forward/token progress and a validated restart+state-restore path, not HTTP/process health alone.
- **Weak CUDA QSA-prefill evidence — llama.cpp #29326:** enabling radix top-k for the Qwen4Exp indexer reportedly improves prompt processing ~20% through ~148K on CUDA. Keep QSA/indexer top-k as a cold-PP seam; no Apple transfer or target credit.

**Target effect:** none. No exact dual-M1 Flash receipt and no new DASLab xhigh result appeared. Keep 40 TG @ ~128K / 400 cold PP and ~70% >=40 planning confidence.


### 2026-09-23 20:42 UTC batching correction / PLE-lifetime / sparse-row-I/O update

- **CORRECTION — llama.cpp #29335 is not evidence of a generic Metal long-context batching collapse.** The reporter reran on current master with `llama-batched-bench` and closed the issue: Qwen3.8-Flash-Next Q8_0 at 32K rises **29.6 -> 38.2 -> 43.8 aggregate TG** for N=1/2/4, and corrected server-only-generation measurements are ~30.0/38.0/43.2. The prior custom script mixed decode timing with other slots' prefill work. Keep the Apple7 B1/B2/B4/B8 verifier-width qualification because exact M1/TB4 speculative multi-row scaling is still unmeasured, but do not treat #29335 as negative batching evidence.
- **Stable async PLE inputs are mandatory — vLLM #58441.** On Qwen3.8-Flash-Next/GB10, a side-stream PLE lookup reading IDs directly from graph-pool storage was nondeterministic (cold==warm **2/8**, max |Δlogprob| **1.41**); copying IDs to a persistent buffer or doing the lookup on the current stream restores **8/8, Δ=0**. P51 asynchronous PLE/QSA/sidecar work must own stable input storage through completion; transient graph/capture allocations cannot be assumed live merely because work was enqueued.
- **File-backed PLE can be viable if row pages are explicitly prefetched — vLLM #58439.** A 47.68-GiB FP8 PLE table mapped directly from safetensors on DGX Spark cuts the prior worker path's steady swap **50-53 -> 5-6 GiB** while keeping summed TTFT and c=16 decode essentially neutral/slightly better. But a cold ~30K prefill is **88 s** with one-by-one GPU page faults versus **~1.6 s** when 64 CPU threads fault the needed rows first. Treat explicit row prefetch as part of the storage design, not an optional optimization.
- **Explicit direct sparse reads gain another implementation anchor — llama.cpp #29030 / `e32c6243d72e`.** Qwen4Exp/Gemma4 lazy rows now use explicit positional reads rather than mmap demand paging; integrated GPUs auto-select lazy rows. Existing Strix-Halo PR data is 181.0->400.8 PP512, 191.7->421.1 PP2048 and 273.8->451.4 PP8192. This is cross-hardware transfer only, but strengthens the P51 requirement to benchmark explicit SSD/host sparse-row gather against demand paging on M1.
- **Speculative padding must preserve recurrent rollback semantics — vLLM #58434.** A one-token prompt tail padded to K+1 for speculation can be misclassified as prefill, causing placeholder draft tokens to be committed into GDN/KDA/Mamba recurrent state. P51 metadata must distinguish committed prompt tokens, proposed tokens and rollback-only padding; a padded tail over prior recurrent state must use a rollback-capable path.
- **Target and draft state/config are separate ownership domains — SGLang #40953/#40955/#40962.** Target-only prefill does not initialize EAGLE draft KV/proposal state; valid decode must transfer the required proposal/state identity or explicitly replay and account the cost. Adaptive target resources must also be built outside draft TP/MoE/A2A contexts. Carry this rule into PP2/MTP state ownership even though the exact EAGLE mechanism is transfer evidence.
- **Cross-family heterogeneous-precision support — DS4 #1011 fresh `57e0b93bf624`.** A Strix-Halo GLM-5.3 mixed artifact uses Q2 routed experts while retaining Q4 for the rest, including MTP. It is much slower than the all-Q2 arm but improves the reported weighted-NLL results. This supports the structural idea of compressing the routed bank hardest while protecting sensitive/nonexpert/MTP paths; it does **not** certify Flash-Next's 3.x-bpw xhigh frontier.
- **M5 wide-query FA tuning — llama.cpp #28439:** fresh tuning reports 882 selected wide-tile cases without a clear loss and 4,956/4,956 tests passing. This reinforces per-device/per-shape Metal tuning for long-context prefill; no M1 target credit.

**Target effect:** none. No new exact dual-M1 Flash receipt and no new DASLab/GSQ xhigh behavioral result appeared. Keep xhigh ~3.0-3.6 search, ~3.3-3.6 source-like frontier hypothesis, **40 TG @ ~128K / 400 cold PP**, and **~70% planning confidence for >=40 TG**.


### 2026-09-24 00:32 UTC exact-family MTP validation / per-region draft-state geometry update

- **Independent exact-family Flash validation — DS4 #1070:** a second Strix-Halo/ROCm system independently reproduces Qwen3.8-Flash-Next Q4 determinism, recovery, tool use, official continuation scores and throughput. Independent speed is **580.26 PP @8K**, **20.59 TG ordinary decode**, and **29.35 TG on the MTP coding workload** (~1.43x that target-only rate). This materially strengthens cross-hardware mechanism confidence for disk-backed n-grams + recurrent state + native MTP, but it is not an M1/128K multiplier and receives no target credit.
- **Draft transfer geometry is per-region — vLLM #58470/#58471:** an MLA target with a GQA DFlash draft cannot share one model-wide TP mapping. Main can either reject the correct geometry or make every decode rank read draft head 0, leaving final target output plausible while acceptance degrades. A separate draft mapping restores NIXL acceptance length **3.221 vs 3.253 local-prefill ground truth** (~1% difference). P51 PP/disaggregated state identity must encode each region's sharding/replication semantics; final text is insufficient to certify draft-state correctness.
- **Verifier-front sharding is real but not automatically large — SGLang #40820:** fresh real-weight B300 TP8 data shows speculative-front projection sharding from **-0.11% to +3.05%** depending on quant/concurrency. Treat verifier decomposition as a measured A/B problem rather than assigning generic distributed multipliers.
- **Deleting standalone verify launches remains worthwhile — SGLang #40961:** folding target-verify SWA writes into an existing kernel improves an 8K/1K workload **+3.31% C1, +2.55% C4, +0.68% C16**. Continue prioritizing launch/fusion removal on the P51 verifier path.
- **Apple dispatch economics are topology identity — mlx-serve #514:** M5 Ultra reports ~**3.1 us** chained-dispatch price and large HC/MoE/GDN fusion payoffs, but persistent cross-grid barriers that are cheap/correct on M5 Max become unsafe or slower on the Ultra. P51 must benchmark Apple7 directly; do not transfer megakernel/barrier assumptions between Apple topologies.
- **Metal kernel resource certification must include verify width + KV format — llama.cpp #29340:** quantized FlashAttention can exceed 32-KiB threadgroup memory at certain width/head shapes; dequant-to-F16 fallback restores safe occupancy. Promoted P51 kernels must validate real threadgroup-memory use across all verifier widths and cache formats, not only unit numerics.
- **Recurrent sidecars are first-class storage bytes — oMLX #3883:** a real 27B MTP cache had **19.36 GB of GDN sidecars vs ~9.24 GB standard KV files**, and generic offline cache observability/purge omitted them. P51 cache accounting/eviction/purge/sleep tooling must enumerate every state class explicitly.
- **Merged DFlash cross-architecture evidence — SGLang #40794:** Kimi-K3 DFlash on B300 reports **4.99 average accept length / 57% acceptance** with 95.7% GSM8K. Keep external-draft speculation as a legitimate branch; no Apple/Flash target credit.

**Target effect:** none. No exact dual-M1/TB4 Flash throughput receipt and no new DASLab/GSQ xhigh behavioral result appeared. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and the xhigh heterogeneous search around **3.0-3.6 BPW** with a **~3.3-3.6** source-like frontier hypothesis.


### 2026-09-24 02:09 UTC Apple GDN dispatch / semantic checkpoint / merged QSA-MTP update

- **Exact-family Apple GDN fusion — mlx-serve #517:** Flash-Next non-Hadamard decode moves from three dependent GDN dispatches/layer to two, removing **612 ops/forward**. M5-Ultra plain decode improves **~87.5 -> 90.9 TG (~+3.9%)** and 16K decode improves ~78.4 -> ~81.3 TG, with byte-identical greedy output. This directly supports P51's launch/fusion strategy, but it does not touch verify and M5-Ultra economics do not transfer numerically to M1.
- **Application-directed recurrent checkpoints gain fresh production evidence — vLLM #55697/#55876:** Qwen3.5-35B/L40S in a high-reuse 1-to-N workload reports **5.9 -> 13.8 QPS (2.34x)**, TTFT **482 -> 248 ms**, and prefill work ~11.5K -> 5.36K tokens/batch with accuracy parity. The implementation stack is now on hold pending maintainer architectural approval due complexity. Use this as strong warm-prefix/agent-workload evidence, not cold-PP target credit.
- **Merged exact-family QSA/MTP path — SGLang #38876 / commit 8b5d77c2688e:** the ROCm packed sparse-QSA decode path for Qwen3.8-Flash-Next is now merged. Its older 8x-MI355X full-enablement data are **936 -> 1603 output TG** with EAGLE/MTP and **3.16 accept length** (~1.71x), plus correct 18K sparse decode under graph replay. This is a fresh merge-status update, not new benchmark evidence; no Apple numeric transfer.
- **RECOVERED older critical-path lesson — vLLM #58463:** removing ~**1 ms host metadata work/step** from fused MTP proposal leaves ITL essentially unchanged and throughput within noise on 4xGB200, because the host work is not critical-path. P51 must profile before assigning TG credit to CPU metadata deletion; dependent GPU dispatch reduction remains separately valuable on Apple.
- **oMLX #3883 fix merged:** offline recurrent/GDN sidecars now participate in cache maintenance. Keep recurrent sidecars as first-class lifecycle/accounting state.
- **WATCH ONLY — vLLM #58484:** DSpark aggregated-serving PP support is being reverted for unspecified cleanup. Insufficient evidence for a structural speculation+PP penalty; track without changing confidence.

**Target effect:** none. No exact dual-M1/TB4 Flash receipt and no new DASLab/GSQ xhigh behavioral result appeared. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and the xhigh heterogeneous search around **3.0-3.6 BPW** with **~3.3-3.6** as the current source-like hypothesis.


### 2026-09-24 03:31 UTC Apple verify-MoE / speculative rollback / recovered quant-quality update

- **Fresh exact-family Apple verifier evidence — mlx-serve #519:** routing Flash-Next MTP verify rows through an existing fused MoE rows arm cuts whole verify-forward time **~9-13% at S=3/5/7** on M5 Ultra and reports about **+12% llmprobe MTP decode**, with single-run greedy/sampled cells +16-21%. This is directly aligned with the P51 verifier-cost thesis: tiny verify matrices need dedicated dispatch, not sorted/gather chains. No M1 numeric transfer and no target change.
- **Target-only vs verify optimization is now empirically separated — mlx-serve #517 follow-up:** the S=1 GDN fusion moves MTP cells only ~2% within spread and leaves 2K prefill unchanged; #519 is where the MTP-side gain lives. Maintain separate target-only and verifier optimization ledgers.
- **Long-reasoning rollback hazard — vLLM #58454:** fresh discussion plausibly connects speculative kpool ring overwrite to real long GLM-5.3-Flash degeneration reports. The surgical repro shows **106/128 FP8 key bytes wrong** under old sizing and exact equality after enlargement, but production patched A/B remains pending. Add pool-boundary reject/rollback cases to long-xhigh verifier certification.
- **Concrete PLE lifetime implementation — vLLM #58489 (recovered older):** produce PLE prefetch IDs directly into persistent per-layer buffers; no added copy/kernel. Use this as the preferred stable-sidecar pattern.
- **Exact-family verify PLE fusion — SGLang #40041 (recovered older):** ~**2% E2E decode** with unchanged acceptance and AIME26 95%. Another small stacked verifier win.
- **Shared-expert loader integrity — SGLang #40754 merged:** a fused loader silently dropped every shared expert while the server still ran; GSM8K returned to **97.41% vs 97.49% reference** after fixing 1,104 missing mappings. Quant/packing certification must verify protected tensor presence/counts, not just successful load.
- **Quant-fidelity evidence — Agention AP dense-27B (recovered older):** same-size AP encodes improve BF16 KLD materially at several Q3/Q4 tiers; AP IQ3_S 11.21 GiB measures **0.0568/0.0384/0.0528** KLD across held-out/web/wikitext vs GSQ-RCO 11.29 GiB **0.0594/0.0432/0.0665**. This supports deeper 3.x search and tail-KLD screening but is not behavioral/xhigh certification and is not Flash-Next.
- **Behavioral token-efficiency evidence — ThinkingCap dense-27B (recovered older):** xhigh averages **37.2% fewer thinking tokens** for **86.6 -> 85.8 macro accuracy**, while native MTP remains ~**2.6 accepted tokens/step** (53% vs base 54%). Treat as a separate future behavioral-compression branch, not a canonical source-behavior P51 target.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and the xhigh heterogeneous quant search around **3.0-3.6 BPW** with **~3.3-3.6** as the current source-like hypothesis.


### 2026-09-24 04:42 UTC Apple7 headroom / controlled verify-MoE / asymmetric draft-transfer update

- **mlx-serve #519 validation strengthened:** M5-Ultra fused verify-MoE rows now show **+14.3% greedy**, **+14.9% sampled**, and **+10.9% after 32K prompt** in a multi-round served harness. With adaptive depth disabled, acceptance is essentially matched while round time falls **21.1 -> 17.7 ms** (~16%). An M5-Max transfer test gives only 1-5% verify-forward gains and no served win. Dedicated verifier dispatch is real, but policy is hardware-topology specific; qualify Apple7 directly.
- **mlx-serve #517 fresh commit 716c0cd1a7a7:** extends fused GDN prework+recurrence from S=1 into S=2-8 verification while preserving every rollback snapshot. MTP decode improves **~3.6%** and 16K MTP **~4.0%**; S=3/5/7 verify forwards improve ~1.7-2.3%. This directly attacks the sequential GDN verifier component.
- **SGLang #41038/#41040:** asymmetric P/D TP DFlash transfer needs source and destination layout/stride identities separately. TP2->TP4 prototype moved **228/256 -> 256/256 completed transfers**, but exact community-commit GPU/token-equivalence validation is pending. Extend the per-region state-topology rule to explicit source/destination geometry.
- **llama.cpp #28243 fresh exact-family receipt:** Qwen3.8-Flash-Next IQ3_XXS on 2x Arc Pro B70 sees median MTP uplift **+25.5%**, but category range is **+43% file-edit/json to -3.2% reasoning**. Never treat one speculative multiplier as workload-independent; xhigh reasoning must be measured separately.
- **RECOVERED Splash #131 / Apple7 branch:** native M1 Q4 kernels move fixed xhigh five-prompt effective decode **18.9 -> 39.1 TG**, 8K **12.8 -> 26.8**, 32K **12.5 -> 23.8**, and PP **53 -> 142 @2K / 48 -> 110 @32K**. The register-MMA path reaches **7.3-7.4 TFLOPS** on real projections vs 2.4-3.5 for prior MPP. This strongly establishes untapped Apple7-specific kernel headroom, but 39 TG is short-context DFlash-effective throughput, not target-only or 128K Flash evidence.
- **mlx-serve #514 null result:** broad narrow-kernel padding changes forward only **-0.4%** and no decode throughput; targeted critical-chain fusions are the productive unit of optimization.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and **3.0-3.6 BPW** experimental search with **~3.3-3.6** source-like hypothesis. The 27B Apple7+DASLab hybrid lane has higher experimental upside than the canonical 25-TG target, but lacks enough quality + filled-context receipts for formal promotion.


### 2026-09-24 06:15 UTC TurboQuant-KV / packed-projection stacking / state-geometry update

- **NEW DS4 #1115 exact-family Metal TurboQuant KV:** Qwen3.8-Flash-Next now has fused **2-8 bit** packed K/V on Metal while keeping the QSA indexer dense and the last trunk attention + MTP block f16. At 1M context, total state drops from **~33.4 GiB f16** to **22.5 GiB Q8 / 19.7 Q6 / 17.0 Q4 / 15.6 Q3 / 14.2 Q2**. 4-bit is the practical packing/read balance; widths 3/5/6/7 can be slower than 8 because fields straddle u32 words. Durable rule: choose KV width jointly with **pack/unpack geometry**, not byte count alone, and keep selector/recurrent/spec-sensitive state protected.
- **NEW DS4 #1115 renderer/cache identity:** Qwen template Unicode/reasoning/control-token mismatches can shift every downstream token and silently invalidate KV checkpoints. A 167K replay returned to byte-identical rendering; live reuse was **1279/1281**, disk restart **1281/1281**. Exact rendered token stream/template semantics belong in cache identity.
- **UPDATE oMLX #3797 fresh M5 stack:** packed Q4 projections inspired by Splash + speculative overlap raise Qwen3.8-27B oQ4e Lightning-MTP decode **65.7 -> 71.9 TG at B1 (+9.6%)**, **76.7 -> 108.2 at B2 (+41.1%)**, **99.9 -> 145.1 at B4 (+45.2%)**. This is strong evidence that hardware-specific projection kernels and speculation/batching can stack, though only B1 is relevant to single-stream reasoning.
- **NEW oMLX depth-controller rule (95ca02f6):** inherited acceptance estimates may seed the next request, but speculative **timing costs must be remeasured per request/context** before choosing depth. Long-context P51 should treat depth-cost tables as local measurements, not persistent constants.
- **UPDATE SGLang #40204 merge:** dedicated small-M MXFP4 MoE cuts 1-4 token kernel latency **~42-44%**, giving **-12% C1 TPOT** and ~8-11% interactivity gains with real EAGLE MTP. Cross-hardware confirmation that tiny verify matrices deserve their own kernel class.
- **UPDATE SGLang #40337 merge:** mismatched state sizing/addressing geometry caused exact **2x C4 ring allocation**, wasting ~10.5% of each SWA token and up to multiple GiB/rank. State accounting must use the same page/window/ring geometry as actual address translation.
- **UPDATE llama.cpp #29340:** quantized Metal FA overflow cases now have a backend memory-limit assertion even without Metal debug validation.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and **3.0-3.6 BPW** search with **~3.3-3.6** source-like hypothesis. This pass strengthens architecture confidence—especially the "protect sensitive state, compress bulk payload, specialize tiny-row kernels, then stack speculation" synthesis—without providing the exact M1/PP2 receipt needed to move the planning numbers.


### 2026-09-24 08:52 UTC long-context GDN / expert-order verify / sampler-semantics update

- **NEW oMLX #3890 exact-family-community GDN widening:** on M5 Max 128 GB, a Qwen3.8-Flash-Next-family opt8 checkpoint gains **+5.0% @1K, +5.0% @8K, +6.0% @129.8K and +3.6% @255.6K target-only decode** by admitting canonical community affine GDN recipes to the existing fused B1/T1 route. The speedup costs **+1.50 GiB non-evictable resident concat cache** and materially increases memory-pressure events at 64K. P51 rule: evaluate fusion as **TG per resident byte/headroom**, not TG in isolation; on M1 64 GB a few-percent win may be dominated by what those bytes displace.
- **NEW oMLX #3797 commit 485ee0fa verifier-locality mechanism:** a Metal verify kernel orders the same 2-8 row (row, expert) pairs by expert so repeated expert tiles execute back-to-back and can reuse cache, supporting affine 4/5/6/8-bit at group 32/64/128. Outputs are bit-exact versus `gather_qmm`. This concretizes the P51 expert-union/reuse thesis, but no benchmark receipt means **zero TG credit yet**.
- **NEW DS4 #1070 commit e1a9e311 speculative correctness:** Qwen3.8-Flash-Next MTP now applies `ignore_eos` / think-mode stop-token admissibility inside target argmax, draft acceptance and chained-parent generation. P51 verifier certification must inherit the **same admissible-token/stopping policy as target-only sampling**, including EOS suppression, reasoning delimiters and tool termination.
- **UPDATE DS4 #651 distributed field report:** 2x M4 Max 128 GB over a TB5 TCP bridge sustains **22.7 TG TP** versus roughly **19-20 TG server pipeline** on DeepSeek-V4-Flash; no single-node baseline is supplied. A corrected 2x DGX Spark RDMA server run completed **83/83** mixed requests at 131K context/batch2. This supports direct-link distributed feasibility and highlights per-session state admission, but gives no M1/TB4 scaling credit.
- **KNOWN fresh merge:** oMLX #3840/#3842 hybrid draft-cache logical-offset/recurrent-boundary fixes merged in-window; their substantive rules were already durable before this boundary.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and **3.0-3.6 BPW** search with **~3.3-3.6** source-like hypothesis. This pass improves verifier/locality and long-context fusion design confidence without supplying the exact M1/PP2 receipt required to move planning numbers.


### 2026-09-24 10:40 UTC Flash verifier-stack / zero-copy KV / restart-identity update

- **UPDATE oMLX #3797 exact Flash-Next branch-level A/B:** on M5 Max 128 GB, Qwen3.8-Flash-Next oQ4e Lightning-MTP rises **92.8 -> 112.0 TG B1 (+20.7%)**, 112.2 -> 116.2 B2, 118.1 -> 124.6 B4; M3 Ultra B1 rises **96.4 -> 104.8 (+8.7%)**. The branch stacks small-M verify, expert-ordered MoE locality, adaptive depth, runtime overlap and related plumbing. This is strong proof that verifier co-design compounds on Flash-Next itself, but **do not assign the +20.7% to any single mechanism** and do not transfer M5/M3 percentages to M1.
- **NEW oMLX f8f51de verifier zero-copy rule:** ragged verify attention now reads compatible cache backing buffers directly instead of materializing `mx.contiguous` K/V prefix views each cycle. At long context, verifier work must never accidentally include an O(context) KV copy. Profile temporary-copy bytes separately from target weights and actual attention reads.
- **KNOWN/UPDATE oMLX #3853 merged:** the already-recorded M1 Max 64 GB nearby-GDN receipt (~5.8-6.2% decode gain from fused FP16 B1/T1 prework on Qwen3.5/3.6 35B-A3B) is now on main. Still no numeric transfer to Flash-Next/Qwen4.
- **RETRACTED DS4 #1115 restart-cache claim:** the previously reported retention-off restart `0/1033` result was subsequently identified by the PR author as **buggy test logic**, not a confirmed runtime/cache defect. Do not use #1115 as evidence for checkpoint-key failure. The broader cache-identity rule remains supported by other sources.
- **NEW DS4 #1119 cross-family SSD-cache warning:** when prefill's active expert set exceeds the SSD expert-cache capacity, simple LRU can cycle to **0% hits**; a freeze-admission-after-first-batch experiment reports ~110 -> ~400 PP tok/s on GLM-5.3-Flash/RTX Pro 6000. If P51 streams experts/tables, admission must be working-set aware rather than blindly LRU.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and **3.0-3.6 BPW** search with **~3.3-3.6** source-like hypothesis. The exact-family verifier-stack evidence materially strengthens architecture confidence, but the missing receipt remains Apple7/M1 S=2-8 verify cost at long context and dual-M1 PP2 overlap.


### 2026-09-24 17:23 UTC warm-MTP restore / small-M verifier / PLE-fault update

- **NEW oMLX #3895/#3901 warm-agent result:** current main is not slower than dev3 on sustained no-cache Flash-Next in maintainer testing (**103.74 -> 113.36 TG**). The real warm-path bug was target tail-prefix reuse without matching MTP history. #3901 restores exact tail-boundary MTP history and moves a controlled warm request **116.05 -> 133.75 TG**, acceptance **~87 -> ~94%**, with cached tokens and TTFT unchanged. Short warm-burst TG and sustained cold/no-cache TG are distinct performance identities.
- **NEW SGLang #41133/#41134 small-M verifier evidence:** at 72K-200K context on MI355X/Qwen3.5 real MTP, one-launch small-M routing cuts the decode step **~7.5-8.2%** with unchanged acceptance, while small-M FP8 projection/quant fusion cuts another independently measured **~4.4-5.1%**. Cross-hardware only, but strong evidence that S=1-8 verifier overhead is decomposable rather than an immutable matrix/ALU floor.
- **NEW SGLang #41123 exact Flash-Next low-bit acceptance:** MI355X BF16 / FP8 / Quark-MXFP4 mean MTP acceptance is **3.5669 / 3.5690 / 3.5524** on full GSM8K runs, with MXFP4 score 96.65% vs BF16 96.88%. This weakens a blanket low-bit-acceptance-collapse assumption, but is thinking-disabled AMD evidence, not xhigh Apple7 certification.
- **NEW vLLM #54070 fresh PLE fault mitigation:** pageable ~48 GB Flash-Next PLE with 22-39 GB swapped caused ~**17 major faults/token** and a **4.3 ms GPU idle PLE wait**. Batched `MADV_WILLNEED` page prefetch cuts gather **2.94 -> ~1.3 ms**, decode step **19.8 -> 18.0 ms**, major faults ~19 -> ~0; prompt-hint background prefetch cuts 16K prefill **2.06 -> 1.52 s**. P51 must batch/prefetch page intents and measure p99 faults/wait, not rely on mmap alone.
- **NEW DS4 #931 Apple-runtime warning:** M3 Ultra/macOS27 field evidence shows Metal queue-residency configuration can produce minute-scale command submission/completion stalls; disabling only queue residency-set attachment turned a narrow 120-s hang repro into ~5-6-s completions while keeping explicit residency + keepalive. P51 loaded-latency qualification must include idle/resume and memory-pressure residency cases; idle TB4 RTT is not a sufficient jitter model.
- **NEW llama.cpp #29353 GDN chunked-prefill transfer evidence:** Qwen3.8-27B Q8 gains **~11% PP** on RTX PRO 6000/GB10 and **~7% on Strix Halo** from a chunked GDN kernel. Recurrence does not eliminate kernel/chunk optimization headroom, but its non-bit-identical result needs logit/state/chunk-invariance qualification on Apple7.
- **NEW vLLM #58548 retention-geometry rule:** hybrid+EAGLE unset retention can yield **0% prefix hits** when retained checkpoints are unreachable after tail-block drop; defaulting to **6 x block_size** restores practical boundary density. Checkpoint spacing is performance identity, not only capacity.
- **CORRECTION:** prior DS4 #1115 `0/1033` restart-cache failure is retracted; maintainer says the test was buggy.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and the **3.0-3.6 BPW** search with **~3.3-3.6** source-like xhigh hypothesis. This pass strengthens the case that verifier cost and PLE stalls are attackable, while simultaneously making warm-state restoration and Metal residency/jitter explicit qualification gates.


### 2026-09-24 20:14 UTC Flash prefill / prompt-lookup speculation / warm-restart update

- **NEW oMLX #3903 exact Flash-Next prefill:** M5 Max 128 GB / Flash-Next oQ4e-mtp gains **+23.6% @4K, +31.9% @16K, +29.4% @64K** cold prefill (similar with paged cache) by stacking GDN, HC, MoE, QSA, PLE and larger-chunk work. The 8192-token chunk policy costs roughly **+3 GiB peak memory** at 16K/64K. This strongly supports architectural PP headroom but gives no M1 percentage transfer; optimize chunk size against both PP and 64-GB headroom.
- **NEW mlx-serve #523 history/prompt-lookup speculation:** on M5 Ultra Flash-Next, replacing eligible MTP chains with matched earlier prompt/output continuations gives **185.6 -> 216.5 TG (+16.6%)** across 11 agent-style tasks and **+31-48%** on repeat/edit-file workloads, while non-copy work is ~flat. At four streams benefit falls to ~**1.06x** because lookup fires on few grouped rows. Keep this as a workload-selective third arm beside target-only and MTP, using hardware/model-specific measured cost rather than fixed constants.
- **UPDATE oMLX #3901 production warm-state validation:** exact tail-boundary MTP history restore moves warm agent telemetry from **2.34-2.47 -> 3.62-3.92 tokens/cycle** and **71-74% -> 97-100% acceptance**. Restored steady-cycle cost is **26.3 ms vs 26.2 ms natural**, so reconstruction is essentially a one-shot request cost. New gap: after restart, SSD-restored target chains with missing memory-only MTP sidecars can remain permanently suffix-primed; persist sidecars or explicitly draft-replay/rebootstrap once.
- **KNOWN/UPDATE SGLang #40041 merged:** target-verify PLE gate/convolution prep fusion (~2% E2E, unchanged acceptance) is now on main.
- **NEW cross-family Metal llama.cpp #29377:** sparse-FA index movement into threadgroup memory improves DeepSeek-V4-Flash Metal PP **304 -> 348 tok/s (+14.4%) at 65K** while TG is nearly flat. Profile QSA index/metadata traffic separately in Apple7 PP.
- **UPDATE Splash #131 reliability:** one M2 Ultra user reports 32K succeeds but a 64K Splash benchmark enters engine recovery/native transport failure. No root cause yet; Apple-family optimization certification must include filled-context soak/recovery, not just speed.
- **SCREENED DS4 #1120:** M5 shape-specialized microkernels yield only ~1% whole-model benefit despite several larger isolated kernel deltas. Preserve the rule that kernel microbench percentages never add directly to the system TG ledger.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence for >=40 TG**, and **3.0-3.6 BPW** search with **~3.3-3.6** source-like hypothesis. The 400-PP mechanism case gets stronger; the 40-TG generic target remains gated by actual Apple7 verifier economics and xhigh acceptance. Prompt lookup is workload-specific upside, not denominator-changing evidence.


### 2026-09-24 22:20 UTC exact-GDN persistence / speculative-control-plane / M1-Ultra depth update

- **NEW oMLX #3908 exact split-GDN prefix persistence:** Qwen3.8-Flash-Next exact static prefixes now persist the **terminal recurrent/GDN state together with KV** using a dedicated hash domain, rather than incorrectly reusing KV alone. Real oQ5e-mtp smoke test restores **13,526 tokens** and cuts repeated request wall **11.064 -> 3.013 s (-72.8%)**. Exact hybrid prefix publication is a semantic checkpoint, not merely a KV cache entry.
- **NEW SGLang #41166-#41175 speculative overhead series:** Qwen3.8-Flash-Next NEXTN now has concrete optimization work across graph-input copies, batch snapshots, KV-allocation transfers, relay stores, hybrid state commits, greedy verify/argmax, QSA metadata, Mamba tracking and NEXTN prep. Isolated examples: state commit **10.00 -> 5.63 us**, greedy verification **8.38 -> 4.50 us**, CPU snapshot **17.84 -> 6.23 us**. Combined B200 performance with **simulated** acceptance 3.3 is 242 -> 590 TG and is **not** transferable; real-thinking AIME26 acceptance on the combined stack is only **~2.146 including bonus token**, a useful caution against optimistic acceptance assumptions.
- **UPDATE mlx-serve #523 hardware-calibrated prompt lookup:** gate now reads live per-chip/model round-cost measurements. Default-sampled 11-task Flash-Next workload remains **~1.17x overall**, copies **~1.33x**, with lookup draft landing **~93.6-94.1%**; individual copy/edit lookup rounds land roughly **95.5-99.3%** of proposed context continuations. Keep as opportunistic third speculation arm, not generic denominator.
- **UPDATE independent M1 Ultra Splash Apple7 result:** short reasoning-off/code cells reach **43.6-98.3 TG**, selected xhigh math **67 TG**, but ~31.95K depth is only **21.2 TG decode / 161 PP**. This independently reinforces both hidden Apple7 headroom and strong context-depth decay; short TG never substitutes for filled-128K qualification.
- **UPDATE warm-restart contract:** production #3901 follow-up confirms restored MTP state has natural-path cycle cost, but SSD-restored target chains with missing memory-only draft sidecars can remain suffix-primed forever after restart. Persist draft state or explicitly re-bootstrap once.
- **KNOWN close-out:** oMLX #3770/#3771 closed; no new planning impact beyond already preserved regression fixes and fused GDN verification.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence**, and **3.0-3.6 BPW** search with **~3.3-3.6 source-like hypothesis**. This pass strongly reinforces that speculative cost includes attackable control/state overhead, while the real-thinking acceptance ~2.146 cross-hardware datapoint argues against raising the ~2.4 P51 acceptance planning assumption without actual Apple7 xhigh measurements.


### 2026-09-25 00:45 UTC in-place rollback / KV grouping / FP32-logits update

- **NEW oMLX #3909 dense-Qwen Apple rollback evidence:** text-only Qwen3.8-27B batched MTP was deep-copying the entire shared cache on ragged acceptance. On a 64-GB M-series Mac this drove the MLX pool to **30-40 GB**, caused pressure aborts, and made a ~110-ms step contain only ~38 ms of backbone work. In-place vector rollback cuts pool max to **3.6 GB**, removes pressure aborts and reduces batch-2 step **~110 -> ~62 ms**; shared priming also improves batch-8 **225 -> 192 ms**. P51 verifier rollback must be row-aware/in-place; whole-cache copies are forbidden.
- **NEW vLLM #58638 hybrid-drafter grouping:** a one-layer DFlash KV bucket can force **46 cache groups**, repeating expensive GDN metadata builders every step. Byte-aware grouping cuts Qwen3.6+DFlash from 46 -> 17 groups and B300 c1 **460 -> 733 TG**; a packed 5-group layout reaches **746 TG** while preserving capacity. Group count is a runtime cost and must be optimized jointly with padding bytes/state geometry.
- **NEW Splash #141 output-precision evidence:** retaining target/draft logits as FP32 improves 27B teacher-forced top-1 agreement vs llama.cpp from roughly **98.8-98.9% to 99.3-99.4%** on M3/M5, with median KL falling ~3x and essentially no B1/B2 decode cost. Protect runtime **logit storage/selection precision**, not only lm-head weights.
- **NEW oMLX #3910/#3911 offload telemetry/modeling:** Qwen3.8-Flash-Next-4bit at 50% expert residency measured **87.26% cache hit rate** on one M5 Max request. Proposed speed modeling uses route-trace LRU hit curves + misses/token × expert bytes/bandwidth; prior Qwen3 MoE estimates land close to measured values. If P51 must spill routed experts, use measured route locality and overlap—not residency percentage—as the offload model.
- **UPDATE SGLang #40223 draft-state restore:** every MTP depth's KV + recurrent/conv/temporal state may have separate ownership and indexing; synthetic end-to-end eviction/restore produced byte/logprob-identical output after restoring all draft pools. Warm-state identity is per draft head/pool, not one generic MTP blob.
- **LOWER PRIORITY vLLM #58631/#58633:** additional speculative host/padding work removes ~3.5 us/step/rank and ~34 us/step kernel-side respectively; reinforces control-plane optimization but carries no system TG credit.
- **COMMUNITY background only:** the same-day Strata 12-GB RTX 5070 Flash-Next report gives **65.1 TG / 543 PP at 128K** for its lowest-bit path and **44.8 TG / 414 PP** for IQ3_XXS, but the source lacks a precise publication time relative to this strict watch boundary, so it is not classified NEW.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence**, and the **3.0-3.6 BPW / ~3.3-3.6 source-like** quant search. This pass mainly reduces implementation risk: avoid whole-cache rollback, treat cache-group count as a first-class speculative cost, protect FP32 logits, and measure expert locality before considering offload.


### 2026-09-25 07:46 UTC target-only MoE fusion / M4 prompt-lookup / 4-bit-KV capacity update

- **NEW oMLX #3912 exact Flash target-only MoE fusion:** one-token routed experts collapse from five dependent launches to two, yielding **54.9 -> 58.6 TG (+6.1%) @4K** and **53.7 -> 56.8 (+8.2%) @14.6K** on M5 Max with bit-identical output and no meaningful memory tax. With Lightning MTP on, verify rows keep the multi-row path and throughput does **not** measurably improve. Keep S=1 target-only and S=2-8 verifier ledgers separate; target-only kernel wins do not automatically reduce verifier-equivalent cost.
- **UPDATE mlx-serve #523 M4 Max transfer:** Flash-Next prompt/history lookup raises copy/edit workloads from roughly **103-110 TG -> 133-146 TG** while new-code/prose cells stay flat. On Qwen3.8-27B 4-bit, copy/edit is roughly **+50%** with ~98% lookup-draft landing and byte-exact copies. This confirms history speculation across M4/M5 Apple systems but remains workload-specific upside, not generic 40-TG credit.
- **NEW mlx-serve #528 long-agent admission bug:** a 197,945-token Flash-Next request restores **193,961 tokens from SSD** but disk-restored rows are not credited as owned, so admission double-bills the whole prompt, evicts ~9.5 GB of hot cache, then refuses the request. Post-restore ownership/pinning must be authoritative for admission; restored rows are counted exactly once and destructive eviction must wait until final fit is known.
- **NEW vLLM #57057 exact Flash-Next 4-bit KV:** UltraQuant Q4 KV at 262K matches FP8 GPQA-D within sampling noise and is slightly slower at low concurrency (~-2.7%) but avoids the FP8 eviction wall at high concurrency. Treat low-bit KV primarily as **capacity/headroom**, not automatic B1 speed; saved bytes may be more valuable as protected weight precision or state margin on 64-GB M1.
- **NEW unresolved oMLX #3917:** M4 Max 64-GB user reports Qwen3.8-27B max-context regression under simultaneous runtime/macOS/quant changes; current logs fail on prefill transient headroom near 98K processed tokens. No root cause and no Flash/M1 transfer. Final P51 context certification must include steady bytes **and prefill transient workspace** under the exact shipping OS/runtime.
- **KNOWN vLLM #58439:** checkpoint-mapped file-backed PLE still passes 76 tests after the persistent-prefetch-id change; prior file-backed/prefetch conclusion unchanged.
- **PUBLIC background:** DASLab's dense-27B NVFP4 prefiller reinforces a phase-specific representation idea—very-low-bit resident decode plus higher-quality streamed prefill—but its code repo had no in-window commit and the released path is Blackwell-specific. No Flash target effect.

**Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP**, **~70% planning confidence**, and the **3.0-3.6 BPW / ~3.3-3.6 source-like** quant search. This pass mostly improves regime accounting: separate S=1 from verify, treat low-bit KV as capacity, and make warm-state ownership authoritative for long-agent admission.

### 2026-09-25 14:59 UTC LiLiCorr / nearer-Apple Flash update

- **NEW serving-path branch — vLLM LiLiCorr (`73a78e6f1f38e280986b81e0f2a9aa5e1ee6fe47`):** vLLM now supports a `LiLiCorrDraftModel` on top of the DFlash backbone. LiLiCorr keeps top-k candidates at each parallel draft position, scores the candidate lattice with one small correlator pass, and then performs a cheap conditional path walk. The underlying NVIDIA paper reports **+9-19% acceptance length over vanilla DFlash**, about **2.8% correlator latency per drafted block**, and best throughput in **70/72** evaluated benchmark/concurrency settings on H100 with Qwen3-4B/8B. vLLM's new integration supports greedy or probabilistic proposal sampling, quantized draft sublayers with protected floating-point correlator islands, and trained block lengths up to `block_size - 1`; however **compatible LiLiCorr checkpoints are not yet published**, and adaptive verification plus alternate block rejection remain explicitly unvalidated end-to-end.
- **P51 LiLiCorr rule:** track LiLiCorr as an alternative trained-drafter branch for the 27B/CUDA lane and as design evidence for Flash speculative control, but give it **zero Apple or Flash-Next performance credit** until a compatible Qwen3.8 checkpoint exists and the correlator/draft path is ported and measured on the target runtime. If tested, record trained block size, candidate top-k, proposal sampling mode, rejection method, correlator precision islands, acceptance length, draft cost, and target verify cost separately. Do not assume a paper's H100 gain transfers to Apple7 or to hybrid Flash-Next recurrent/QSA state.
- **RECOVERED OLDER nearer-Apple receipt — oMLX M2 Max 96 GB / Flash-Next oQ4e + Lightning MTP:** a 2026-09-24 public benchmark on **M2 Max 38-core / 96 GB** reports **33.2 TG / 292.5 PP at 64K**, with TG **38.4 @1K, 36.6 @4K, 38.6 @8K, 29.5 @16K, 31.6 @32K, 33.2 @64K** and peak memory **79.8 GB** at 64K. This is materially nearer to M1 than M4/M5 evidence and shows a single pre-M3 Apple generation sustaining low-30s Flash MTP at 64K, but it is still **Apple8 rather than Apple7, 38 GPU cores rather than 32, 96 GB rather than 64 GB, Q4e rather than the P51 custom quant, and only 64K rather than the 128K headline denominator**.
- **Target effect:** none. The M2 receipt modestly strengthens architectural plausibility but does not close the 128K Apple7/PP2/TB4 gap. Keep dual-M1 Flash at **40 TG @ ~128K / 400 cold PP / ~70% planning confidence**, with the same ~39-41 center, ~30-32 mature downside and ~24-27 target-only fallback.

### 2026-09-25 18:16 UTC mixed-MTP-quant / speculative-side-state / allocator update

- **NEW exact Qwen3.8-family mixed-draft quant evidence — SGLang `0154f72b48d54e96df7dac69bd7677156c2dc1b6`:** the AMD Quark **Qwen3.8-2.4T-A95B MXFP4** checkpoint keeps the MTP routed experts quantized while excluding the draft attention projections, shared expert, shared-expert gate and FC into BF16. The prior loader saw any `mtp.*` exclusion and incorrectly dequantized the entire draft, causing expert-shard shape mismatch. The fix treats routed-expert exclusions as the signal for an all-BF16 draft and preserves per-layer exclusions independently. **P51 rule:** MTP/draft precision identity is a **per-submodule precision map**, not one draft-wide quant label. Protect sensitive attention/shared/head/control islands while allowing the large routed-expert mass to remain low-bit when checkpoint evidence supports it. Fused-module names must be expanded through the target model's packed-module mapping before matching precision exclusions.
- **NEW speculative side-state lifetime rule — vLLM `2617fe938355594c48d4512a2ef6b470962aac1a`:** GLM-5.3-Flash speculative decoding could corrupt its K-pool tail state when a draft token completed a pool and was then rejected: later draft tokens overwrote ring slots needed to redo the rejected completion. The corrected ring is sized to survive the speculative horizon and chosen to divide the attention block, avoiding both overwrite and a large LCM-driven prefix-cache granularity penalty. **P51 rule:** every recurrent/QSA/side-state scratch ring must retain all source state needed across the maximum rollback horizon; capacity must be derived from base state span + current speculative width, and its geometry must be compatible with prefix/cache block geometry. Never size a rollback ring only for the non-speculative state span.
- **NEW capacity-certification rule — vLLM `6491f481a7c0fb3aa77bbc6649584b545c65c871`:** during startup memory profiling, stepwise-growing workspaces can free multi-GiB allocator blocks that are subsequently split by a small allocation; that small survivor can pin the whole segment past `empty_cache()`, making the profiler report the segment as persistent consumption and silently shrink the KV-cache budget. vLLM now temporarily limits native CUDA/ROCm allocator splitting during the profile run. **P51 rule:** context-fit certification must distinguish true live/resident bytes from allocator-retained/fragmented capacity. Record allocator/pool state and repeat fit measurements after a clean/controlled allocation policy before concluding that a quant or runtime has lost context capacity.
- **Target effect:** none. These are correctness/capacity/quant-identity rules, not new Apple7 or dual-M1 performance receipts. Keep **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence** and the current xhigh quant search.

### 2026-09-25 19:36 UTC independent M1 replication / Splash upstream integration update

- **RECOVERED SAME-DAY independent M1 Max replication — Reddit `1wpza1i`:** a second user benchmarked the M1/M2 Splash fork on a **2021 M1 Max, 24-core GPU, 64 GB**, using the prebuilt `splash-m1 1.0.2-m1`. Qwen3.8-27B results: **32.8 TG** on npanj's five-prompt average, **46.6** math, **61.3** short code, **18.3** short prose, **21.6 @8K** code explanation, **17.1 @32K**, **62.3 aggregate TG at B4**, and **101 PP @8K**. The same post reports 217 extraction/matching/counting/confabulation items plus 50 GSM8K with reasoning off, with Splash essentially tied to the compared stock 4-bit MLX quant. The result is about **0.84x** the original 32-core M1 Max fork numbers, consistent with the smaller GPU. Reddit exposes only day-level timing for the post/comment surface, so this is durable recovered same-day evidence, not a strict-window timestamp claim.
- **RECOVERED SAME-DAY M1 Ultra user runs — comments on Reddit `1woq7cd`:** an M1 Ultra 64-GB user reports a tiny-context Splash chat response around **64 TG**, and on a repeated real image-analysis task reports **36.4 TG** with **13.4 s TTFT** and **48.4 TG** with **5.8 s TTFT** for ~955 input tokens and ~1.0-1.2K output tokens. The same user says total image-analysis wall time was much worse than their regular MLX path, reinforcing that high decode TG can coexist with poor prefill/vision/TTFT. Another M1 Max 32-GB user reports the fork is faster and more consistent than oMLX/MTPLX but gives no numeric run. A promised 32-core M1 Max rerun and M2/M2-Ultra runs had **not** posted numbers at cutoff.
- **P51 Apple7 consequence:** the 24-core replication materially reduces the risk that the original 32-core M1 result was a one-machine anomaly and provides independent evidence that Apple7 custom kernels retain useful B4 aggregate throughput. It also reinforces the central warning that Apple7 **prefill/TTFT remains the weak side**. This strengthens confidence in the existence of Apple7 verifier/kernel headroom but does **not** numerically transfer to Flash-Next PP2/TB4 or the 128K headline target.
- **NEW upstream Splash integration — commits `804bb36b523`, `df5462049fc`, `514e5844062`, `bfc3103e79d`, `06cafcb1e1c`:** upstream merged a batch of runtime work including few-row RMS norms staged in threadgroup memory, preparing DFlash2 drafts directly from their source checkpoints, keeping model weights Metal-resident between requests, stronger scheduler/KV/memory-governor correctness, and explicit GGUF-vs-llama.cpp comparison documentation. The staged norm code reports **1.3-2.6x** kernel-level improvement for dependent <=2048-column, <=64-row norms on M3 Max/M5 Pro; those measurements are stronger-chip transfer only and may predate the merge timestamp.
- **P51 drafter consequence:** checkpoint-native DFlash2 preparation and `--draft-model` make the upstream runtime a cleaner experimental host for separately quantized/custom drafts. Preserve the source checkpoint identity and prepared-draft quantization map as part of the experiment manifest; do not treat a prepared Q4 draft as the same identity as its BF16 source checkpoint.
- **Target effect:** none. Keep dual-M1 Flash at **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence**. The new independent M1 data improves confidence in Apple7 kernel portability, but the decisive unknown remains Flash-Next on two M1 Max nodes with deep-context S=2-8 verification and PP2/TB4 overlap.

### 2026-09-25 22:17 UTC verify-group-width / dual-die Apple policy update

- **NEW exact-window Flash-Next verify-group evidence — mlx-serve #534 (`2a93a011ec1d3ce61372952d3adca198c0cb95fa`):** on **M5 Ultra 256 GB / macOS 27 / Flash-Next mixed-4/8bit / MTP typical 0.2**, nine fused MTP verify kernels help only when the dual-die `applegpu_g17d` runs a grouped verify. Median 400-token code runs report **+4% aggregate TG at 2 streams, +13% at 4, +1% at 8, and unchanged at 1**. Earlier ungated runs showed the same kernels can slow solo sampled decode by **5-7%**. The merged policy therefore enables them on g17d only for `group_rows > 1`; single-die M5 keeps them enabled normally. A solo-opcount check confirms the gated path is byte-identical in per-forward operation counts to base.
- **P51 verifier-policy rule:** kernel selection must be keyed by **GPU family/topology + actual verify-group width**, and possibly model/quant identity; do not promote a fused S>1 path globally from a single-row microbenchmark or a single width. Benchmark S/row groups separately because gains are **non-monotonic** (here 2:+4%, 4:+13%, 8:+1%) and a path that wins grouped verification can regress B1/solo. This is directly relevant to PP2's intended multi-row verifier overlap, but the M5 Ultra concurrency result is still stronger-chip/different-topology transfer evidence rather than an M1 PP2 receipt.
- **RECOVERED SAME-DAY low-value M1 comment:** an r/oMLX commenter with **M1 Max 64 GB** posts an MTPLX screenshot around **29 TG** for an 8-bit Qwen3.8-27B setup described as FP16-adapted for M1. No filled-context, PP, MTP acceptance/depth, output length or exact runtime recipe is exposed in the searchable comment, so this is not used for planning.
- **Target effect:** none. Keep dual-M1 Flash at **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence**. #534 strengthens the mechanism case that grouped verify deserves its own optimized policy, but supplies no Apple7/TB4/128K measurement.

### 2026-09-26 09:37 UTC Apple7 small-row / REAP320 negative-control / adaptive-verification update

- **NEW exact-window Apple7 small-row evidence — mlx-serve #530 (`55d834b0460a83542107a875262daccaa05321b1`):** a generation-specific 2-bit ternary GEMV decodes each packed word once and reuses it across **1-8 activation rows**. On **M1 Ultra 64-core / 128 GB** with Bonsai 2 27B, plain B1 moves **44.5 -> 49.2 TG (+10%)**, B2 **50.8 -> 52.7 (+4%)**, B4 **44.5 -> 57.0 (+28%)**; MTP B1 **47.0 -> 48.9 (+4%)** and MTP B2 **38.6 -> 45.9 (+19%)**. Bonsai 1 27B, previously stock MLX, moves **34.2 -> 45.2 B1 (+32%)**, **34.0 -> 44.8 B2 (+32%)**, **38.1 -> 52.5 B4 (+38%)**. The same code explicitly routes narrow outputs (`N < 2048`, including GDN a/b and attention k/v) back to stock because stock is up to **2x faster** there. The rejected fused gate/up+SwiGLU prototype was ~0% on M1 Ultra. **P51 rule:** small-row kernels need tensor-shape- and row-width-specific dispatch; 'fuse/reuse weights across rows' is a real Apple7 lever, but not all projections benefit and fused-MLP wins on newer Apple cannot be assumed on M1.
- **RECOVERED OLDER exact M1 Flash-Next negative control — oMLX community benchmark dated 2026-09-25:** **M1 Max 32-core / 64 GB** running `Qwen3.8-Flash-Next-REAP320-oQ3e-fp16-DWQ-MTP-Vision-MLX` reports **192.9 PP / 10.0 TG @8K**, another **140.7 / 5.5 @8K**, and **146.6 / 5.7 @16K**. This is the first surfaced exact-M1 Flash-Next timing for that REAP320 MLX package, but it is **not a clean physical Flash floor**: the FP16 oMLX repo is **71.7 GB on disk** on a 64-GB machine and includes the vision/PLE layout, while the sister MTPLX pack explicitly separates the ~32-GB n-gram table for SSD streaming and measures a **39.7-GiB resident floor**. The same family on M4 Pro/MTPLX sustains ~31-35 TG through ~85K. Treat the M1 numbers as a runtime/layout/residency warning until memory residency, PLE offload, vision-engine selection, MTP engagement/acceptance and swap are known.
- **P51 consequence of the REAP320 control:** a low-BPW/pruned checkpoint by itself does not guarantee fast Apple7 decode; the **physical resident set and execution lane** dominate. P51 certification must log mapped/file bytes separately from wired/resident bytes, whether PLE is direct-resident versus SSD streamed, whether vision/VLM mode changes the text engine/MTP path, and actual MTP engagement/acceptance. Do not lower the 24-27 target-only fallback or 40-TG PP2 target from an overcommitted/ambiguous package run.
- **NEW exact-window adaptive-verification infrastructure — vLLM #57263 (`a4eb3f25d6f9b3cad7ecf5390423d853935fcaeb`):** Gemma4 DSpark K=7 now supports variable-length adaptive verification under full decode graphs by exposing each attention backend's maximum graph-safe per-request query length. Mixed prefill/decode batches are explicitly excluded from those varlen decode graphs. Full GSM8K gives **62.77% fixed DSpark vs 62.62% adaptive** (difference statistically non-significant in the PR), while adaptive verification preserves exact graph capture for decode-only steps. **P51 rule:** adaptive S must be constrained by the backend/kernel's graph-safe row-width domain and must not silently route short prefills through a decode-only graph. Keep verification width as an explicit runtime state feeding kernel-policy selection.
- **NEW restore-failure correctness rule — llama.cpp `08618ff8e735141d8e4e5be28e6d6af170e4757b`:** failed state restores can leave partially written K/V, hybrid-attention, MLA/DSA, or recurrent state behind unless every already-applied component is cleared and deferred writes are discarded. P51 warm-prefix / checkpoint restore must be transactional: either all target + recurrent/QSA/MTP state commits, or every touched range is invalidated/zeroed before the request can continue.
- **NEW integrated stronger-chip ceiling — mlx-serve v26.9.6 (`1745ffe89e4670f1e0c6de22c75a9875b27399de`):** the release combines prompt/history lookup, one-dispatch GDN, grouped fused verify and related Flash-Next work. On **M5 Ultra**, mixed-4/8-bit Flash-Next + MTP reports a normal peak around **219 TG B1, 227 aggregate TG B4, 3150 PP @8K**; copy/edit workloads can reach higher because prompt lookup drafts from conversation history. This is an integrated software-ceiling receipt, not an M1 transfer multiplier.
- **Target effect:** none. Keep dual-M1 Flash at **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence**, center ~39-41, mature downside ~30-32, target-only fallback ~24-27. The new evidence increases confidence that Apple7 has removable small-row kernel overhead, while the exact M1 Flash REAP320 run emphasizes that PLE/residency/runtime identity can sink performance if the memory plan is wrong.

### 2026-09-26 13:10 UTC Apple7 attention / disk-checkpoint steady-state update

- **RECOVERED OLDER exact Apple7 long-context attention evidence — Splash-M1 1.0.2-m1.1 / commit `5967821462f2be152bab3feb4174e11dd6f1ada1`:** the M1/M2 fork replaces the remaining Apple MPP attention path with register-matrix kernels using exact-half KV values and FP32 matrix accumulation. On the same **M1 Max 32-core / 64 GB** and Qwen3.8-27B Splash lane, short decode stays ~40 TG, but **51K decode rises 20 -> 25 TG** and a cold **38K TTFT falls 359 -> 312 s**. Per-layer attention is reported **1.85-1.95x faster** for decode/verify and prompt processing from **8K through 176K**; at 176K one 27B decode step's attention component falls from about **215 ms -> 116 ms**. The release was published **2026-09-25 21:02:13 UTC**, before the prior hard boundary, so this is RECOVERED OLDER rather than NEW.
- **RECOVERED SAME-DAY depth curve from the Part-2 agent run:** on that optimized M1 Max lane, Qwen3.8-27B OpenCode medians are about **30 TG at 30-64K, 20 at 64-96K, 20 at 96-128K, and 14 at 128-157K**, with some 150K+ turns exceeding 25 TG depending on draftability. This is dense-27B/DFlash evidence, not Flash-Next/QSA, but it proves Apple7 attention optimization continues to matter far beyond 64K and also shows that full long-context task speed still declines substantially after the attention kernel is improved.
- **Independent same-day confirmation remains shallow-context:** a Part-2 commenter on M1 Max reports **38.9 TG** for a request with **6,929 input tokens / 6,272 cached / 939 output / TTFT 7.1 s**. Useful as an install/repro check, not a deep-context receipt.
- **P51 consequence:** long-context Apple7 attention is no longer an entirely opaque bottleneck. Register-matrix attention can almost halve the per-layer attention component through 176K, which strengthens transfer confidence for an Apple7-optimized QSA/full-attention path. But the dense-27B 128-157K curve also cautions that attention optimization alone does not deliver 40 TG. Keep Flash's sparse-attention architecture, custom quant and PP2 multi-row verify as separate required gains.
- **NEW exact-window SSD checkpoint steady-state evidence — Splash `85e1ba3c380a5ef4f402a19c43e31df68292a65a`:** a disk tier that only consumes free quota stopped accepting rolling checkpoints once cached prefixes filled it, causing every memory suspension to replay the entire prompt. Allowing one rolling checkpoint to replace older LRU disk copies on a **24-GB M6 / Qwen3.8-27B UD-IQ3_XXS / 2-GB disk tier** changes a 60K request from **514 -> 263 s TTFT**, **96,888 -> 39,576 replayed tokens**, and **19 -> 0 failed checkpoints**. The request keeps only one rolling checkpoint and retires the prior checkpoint first, limiting collateral eviction to about one state cell (**187 MiB** in that model).
- **P51 SSD-state rule:** persistent SSD tiers must have an explicit replacement policy for progress checkpoints; 'write only into free quota' fails at normal steady-state occupancy. Rolling checkpoint admission should reserve/reclaim one bounded state-sized unit and prefer replacing stale progress/cached-state copies without destroying active-prefix lineage.
- **NEW exact-window numerical fail-loud rule — Splash `4ab94eb105d27d7f059a98b1852b7e511bce0e71`:** an entirely non-finite logits row could leave the sampling sentinel `0xffffffff`, which previously flowed into token history and could be clamped into the next verify input. Splash now fails only the poisoned lane when output token >= vocabulary size and publishes no cache/output for that lane. **P51 rule:** aggressive quant/kernel experiments must validate post-sampling token range and finite-logit invariants before committing target/draft state; corrupt lanes fail closed without contaminating shared cache or peer lanes.
- **Target effect:** none. Keep dual-M1 Flash at **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence**, center ~39-41, mature downside ~30-32, target-only fallback ~24-27. The recovered Apple7 attention result reduces one specific long-context software uncertainty, but the fresh dense-27B depth curve is not evidence that a single M1 node can sustain 40 at 128K.

### 2026-09-26 15:28 UTC QSA/verify control-path + long-agent compaction update

- **NEW exact-window Flash-Next QSA control-path evidence — mlx-serve #556 (`364b9fd0760bc123b308ec735e5451b67a49d4b6`):** each of Flash-Next's 12 QSA layers maintained the newly pooled index keys with roughly a **10-kernel dependent chain** (`astype -> mean -> astype -> rms_norm -> rope...`). A bit-identical fused kernel reduces that to one dispatch/layer. On **M5 Ultra / Flash-Next mixed-4/8bit / S=4 / kv=16K**, total forward falls **20.63 -> 20.25 ms** and GPU time **18.99-19.20 -> 18.59-18.70 ms**. The implementation deliberately preserves every BF16 rounding point because pooled keys feed top-k block selection; ratios >8 and M-RoPE keep the composed path. Block count is a runtime scalar rather than a template to avoid per-count Metal JIT proliferation. **P51 rule:** QSA index maintenance belongs in the verifier cost model; fuse dependent control/state chains only with selection-bit-identity, and never template a per-call block count.
- **NEW exact-window dense-verify attention evidence — mlx-serve #554 (`080a62e2f2d78359146b8411f9f5de9c89187eb9`):** Flash-Next has GQA=12, so an S=4 dense causal verify exceeded MLX's vector-SDPA `qL*gqa <= 32` envelope and fell into an ~8-dispatch unfused path. Splitting S=4 into two 2-row groups keeps both on the vector kernel. On M5 Ultra at kv=1500, GPU forward improves **17.13 -> 16.71 ms** (~0.42 ms); every split run beat every control run. The path is gated to the measured hd=256 shape and yields to NAX where NAX is already faster. **P51 rule:** verifier attention dispatch must be keyed by `(head_dim, GQA, S, KV regime, fused-kernel availability)`, not merely S.
- **NEW exact-window host/GPU-overlap evidence — mlx-serve #545 (`22749988bdc814bf0a63d45121430b2d0f38c627`):** solo greedy Flash-Next MTP now builds the next draft chain from lazy GPU verify results before the host acceptance read, moving predraft tail work from roughly **1.26 -> 0.53 ms** and improving the fixed-prompt greedy run by about **2.6%** (roughly 185-188 -> 192 TG on M5 Ultra). The next chain is kept or transactionally discarded/truncated after the host verdict; sampled/grouped/lookup/planner-owned paths retain the old flow. **P51 rule:** once verifier kernels approach the target budget, overlap draft-chain construction with the outstanding verdict rather than serializing it behind the host read; speculative prework must have a cheap exact rollback path.
- **SAME-DAY CURRENT long-agent reliability evidence — r/oMLX `1wqkqeu`:** one user reports **Jundot Flash-Next oQ4e-mtp**, latest oMLX, **262K context**, n-gram SSD offload, Pi defaults plus `pi-goal-x + pi-blackhole`, with a personal record of **14 compactions** and repeated unattended overnight runs without runtime failure. They report about **70 TG**, but the comment chain does not unambiguously confirm the hardware, so do not attach that number to M5 Max. This is the strongest surfaced multi-compaction survival receipt, but it is anecdotal.
- **Same thread exposes a crucial failure mode:** another user on **Jundot oQ4e / oMLX 0.7.0-dev4 / MTP / 262K single slot** reports that 2-slot planner/developer caused OOM, while a 100K setup survived **3-4 compactions** but later reverted prior commits because the agent concluded existing work was bad. **P51 certification must split `runtime continuity` from `semantic continuity`:** after every compaction, validate goal/work-note lineage, repo HEAD/diff awareness, accepted decisions, active task, and no destructive regression. A process that stays alive but forgets or reverses correct work has failed.
- **Pi-blackhole/goal-x architecture is directly relevant to the harness layer:** `pi-blackhole` uses deterministic structural compaction plus observational memory that survives compactions; `pi-goal-x` persists the objective/tasks to disk across context churn. Treat durable goal/work-note/transcript-recall state as **out-of-context sidecar state**, analogous to our runtime recurrent/prefix state, rather than relying on repeated free-form LLM summaries alone.
- **Community capacity/speed tradeoff from the same thread:** an M4 Max user reports oQ5e + oMLX 0.7.0-rc1 at about **150K** max context; an M5 Max 128-GB user reports oMLX Flash barely ~40 TG versus MTPLX often 60+, but says oMLX saves **~20-30 GB RAM** through SSD offload. Treat these as anecdotal, not benchmark-grade, but they reinforce the explicit speed/residency tradeoff already in P51.
- **Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence**. The three exact-family M5 changes remove roughly sub-ms control/attention/tail costs in the desired direction, but no Apple7/TB4 receipt exists. The Reddit thread strengthens the long-agent certification design rather than the physical throughput forecast.

### 2026-09-26 17:56 UTC non-NAX speculative decode / PLE synchronization / dense-QSA update

- **NEW exact-window oMLX non-NAX speculative-decode evidence — #3958 (`043f1d9d3cb3bf20f81d8602a8bd9cbc3476b267`):** the patch explicitly widens Qwen3.8 verify optimizations beyond NAX devices and adds fp16 coverage for older Macs. On **M2 Max 38-core / 96 GB / Qwen3.8-27B oQ4e fp16**, DFlash2 improves **20.4 -> 29.5 TG short, 12.8 -> 23.0 @4K, 11.8 -> 16.8 @16K, 7.9 -> 18.1 @64K**; Lightning MTP improves **19.4 -> 26.7 short, 18.7 -> 23.1 @4K, 15.0 -> 26.0 @16K, 10.8 -> 14.2 @64K**. The same patch improves **Flash-Next oQ4e Lightning MTP** on M3 Ultra from **47.6 -> 63.0 TG @64K (+32%)** and on M5 Max from **63.0 -> 66.7 @64K (+6%)**. No exact Flash-Next M1/M2 number is supplied, so this is transfer evidence, not a direct M1 receipt.
- **Mechanism from oMLX #3958:** verify attention moves to a GQA-shared tensor-op kernel; Lightning MTP uses a coarse 3-bit lm_head candidate pass followed by exact rescoring; MTP head KV uses a small tail cache instead of whole-head copies; GDN verify becomes one fused launch/layer with lazy replay for commit; QSA native score/top-k/sparse-GQA thresholds are measured per GPU rather than enabled only by NAX capability; parked MTP keeps head history so re-entry acceptance does not reset. **P51 rule:** capability detection is insufficient—older Apple needs its own measured row-count/verify-path thresholds, fp16 activation semantics and park/re-entry state continuity.
- **NEW exact-window dense-bf16 QSA verify evidence — mlx-serve #555 (`9a54673750087da49d890063e007ea61947d132e`):** default bf16 KV previously missed the fused split-K QSA verify kernel. On **M5 Ultra / Flash-Next mixed4/8 + MTP**, median decode after 32K improves roughly **95.1 -> 106.3 TG**, and after 64K **92.1 -> 103.6 TG** (~12%). The new path serves S=2..15 at every KV past the QSA indexer budget and handles unaligned views in-kernel rather than trusting host-visible strides. **P51 rule:** default KV format must be on the optimized sparse-verify path; scheduler memory billing must follow the actual O(budget) keys read rather than raw KV length.
- **NEW exact-window PLE placement/synchronization evidence — mlx-serve #539 (`e541ec86641349d5187cb120d1f405eba1068302`):** moving PLE n-gram hash/gather/dequant onto the GPU and wrapping the **29.8-GB** mmapped table as one no-copy Metal buffer removes a host draft-ID read between draft chain and verify. On the M5 Ultra context ladder, at ~104K effective prompt tokens decode moves **93.06 -> 107.14 TG (+15.1%)** and prefill **3377 -> 3432 PP**; the fixed 8K harness reports **3153 -> 3361 PP**. Raw PLE work was only ~0.3 ms, but the CPU path also forced ~0.2 ms synchronization per round and serialized the chain. **Correction to prior P51 rule:** raw PLE gather cost can be ~1% while PLE *placement* still has double-digit decode impact because of dependency-induced host synchronization. Measure `PLE compute + forced barrier`, not gather time alone.
- **P51 PLE memory implication:** do **not** infer that each 64-GB M1 should resident-map a ~30-GB PLE table. #539's M5 Ultra has ample memory and explicitly gates the GPU arm on working set. For P51's SSD-backed PLE design, the goal is to eliminate the mid-round host dependency—via asynchronous/prefetched GPU-visible lookup, staged hot working set, or another no-host-read design—while keeping PLE residency within the real 128K memory budget. Re-run the memory model before promoting a fully resident PLE arm.
- **NEW scheduler/agent QoS evidence — mlx-serve #568 (`3f7f0d9eb119240e5649e878342a167d9beea5d2`):** a long prefill can freeze existing decoding streams because chunk boundaries previously hosted only a few decode ticks. A configurable decode share trades the new request's TTFT for live-agent responsiveness and caps active prefill chunks while decoders exist. **P51 multi-agent rule:** benchmark throughput and interactive starvation separately; PP maximization must not make an existing agent unresponsive during another slot's long prefill.
- **Target effect:** none. Keep **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence**, center ~39-41, downside ~30-32, target-only fallback ~24-27. The non-NAX oMLX work strengthens transfer plausibility to older Apple, while #539/#555 reveal additional exact-family long-context seams; neither supplies the missing exact Flash-Next + M1 + ~128K + PP2/TB4 receipt.

### 2026-09-27 02:24 UTC M1 offload-MTP / QSA workspace / Ishizuki audit update

- **NEW exact-window M1 Flash-Next + expert-offload MTP receipt — oMLX #3935 (`a6d0b8046c8911f2e6e45efd4e6b650665dceb2c`):** on **M1 Max 64 GB / Jundot Qwen3.8-Flash-Next-oQ4e-mtp / PLE SSD / 60% experts resident / 500-token coding prompt**, expert offload with MTP off is **14.3-14.6 TG**; keeping the native MTP head resident and using adaptive MTP reaches **16.3-16.4 TG** in the final branch, with earlier runs **17.0-17.3 TG, 1.87 committed tokens/cycle, 69.5% acceptance**. Fixed depth 2 reached ~17.0 while depth 3 fell to ~15.0 because longer verify windows route to more distinct experts and increase misses. **P51 rule:** if any backbone component is streamed/offloaded, keep the draft/MTP head resident and make verify-width control account for *bytes fetched / distinct experts touched*, not acceptance alone. This is exact M1 + exact Flash-family evidence, but its short prompt and expert-offloaded topology are not a 128K PP2 receipt.
- **NEW QSA allocator-fragmentation evidence — vLLM #57105 (`7a877ae34dcf4a7d46de08eb16db4699e1e0047c`):** a variable QSA-indexer logits workspace accumulated allocator segments as context grew. In a GB10 direct-kernel walk to **166.4K**, stock reserved memory reached **13,556 MiB / 55 segments**, while reserving one worst-case workspace held it at **534 MiB / 3 segments**. **P51 rule:** QSA score/index workspaces should be stable/reused reservations sized from an explicit ceiling, not per-length growth allocations; memory certification must separate logical live bytes from allocator fragmentation/reserved-pool bytes.
- **NEW long-context memory-admission evidence — oMLX #3933 (`86ddbff225242c09fecd13c16f7ad2fb1c4e5217`):** MLX-counter-based usage, one-time full-prompt KV capacity reservation and consistent admission/headroom rules eliminate mid-prefill aborts. On M5 Max the Qwen3.8-27B 44-GB context bench goes **143,360 -> 262,144** first-attempt; Flash-Next 99-GB resident-ngram under aggressive/context reaches **262,144** instead of model eviction, while safe mode moves n-gram to SSD and avoids swap. **P51 rule:** budget separately for steady state, prefill transient workspace, allocator pool/fragmentation and guard margin; reserve long-lived KV/state geometry early enough that repeated growth cannot strand whole old copies in the allocator pool.
- **NEW prefill-QSA tile evidence — oMLX #3934 (`2a3d08935fe40ab11451ed3dbd3db04d2c1fb914`):** on M3 Ultra, wider native QSA query tiles reduce the sparse-QSA pipeline by **11-17%** at 8K-32K K/M shapes and produce ~**+2.6-3.0%** end-to-end 24K/32K prefill while keeping the FP32 score sheet under an explicit memory ceiling. **P51 rule:** prefill query-tile width is a `(KV length, score-sheet budget, GPU)` policy, not one fixed chunk width.
- **NEW portability reminder — mlx-serve #558 (`3dc1dab54e7bb12e90ad62de1f4766dd7114c8c7`):** folding GDN verify recurrence + norm/gate + rollback-concat saves only **~0.046 ms / 0.3%** on M5 Ultra and requires a 1024-thread threadgroup; a CI GPU exposes an **896-thread** pipeline limit and must decline to the old path. **P51 rule:** probe actual per-pipeline threadgroup limits and fail back cleanly; never infer launch support from Apple generation alone.
- **ISHIZUKI AUDIT — strong Apple7 mechanism evidence, not an exact Flash-128K receipt:** current `struffl/ishizuki` has custom few-row affine/GGUF verify kernels, DFlash partial-accept replay for recurrent GDN state, KV quantization, SSD expert streaming, persistent prefix caches and extensive local tests. On **M1 Max**, its 2-bit dense-Qwen DFlash runs code/math around **44 TG vs ~22 TG plain** at ~5.9 accepted/verify; the custom 8-row verify cuts a representative MLX 8-row forward from ~279 ms to ~134 ms. This independently supports the P51 Apple7 small-row verifier thesis, but Ishizuki publishes no planning-grade full-model Flash-Next 64K/128K depth curve.
- **ISHIZUKI rules worth mining:** custom-kernel cache identity must include **activation dtype** (Ishizuki found fp16/fp32 same-shape kernels could share the wrong MLX build, causing page faults/wrong outputs); warm each shape/dtype at model load; keep changing row count as a runtime argument rather than a shader-template identity; use shape/byte-specific row crossover thresholds; clamp padded/dead verify rows rather than compiling each width; on partial draft acceptance replay **only the recurrent rule from pre-verify state** instead of the whole backbone; share identical Hadamard rotations across sibling projections; on macOS SSD streaming use `F_NOCACHE`/aligned staging deliberately so streamed bytes do not duplicate themselves in the file cache.
- **ISHIZUKI audit risks not to copy:** (1) `APIServer.listen` creates an unauthenticated plain `NWListener` by port without an explicit loopback endpoint while the app merely *advertises* `127.0.0.1`; HTTP responses add `Access-Control-Allow-Origin: *`, and request/header/body accumulation has no explicit global cap. Bind inference explicitly to loopback by default, add body/header ceilings and authentication for non-loopback use. (2) `PrefixStore` fingerprints only archive format + model directory name + KV geometry, not actual checkpoint/config/rope/cache-layout identity. (3) `GatedDeltaNetCache.load` accepts missing recurrent arrays and still sets a nonzero offset, allowing a stale/damaged archive to become a silent zero-state warm prefix. P51 prefix restore remains transactional, strongly fingerprinted and fail-closed.
- **ISHIZUKI long-running-agent / governance caveats:** native agent shell is intentionally **unsandboxed** (`SandboxChoice.native` is the default and inherits the user's environment); container/cluster options are the actual security boundary. The current repository's `AGENTS.md` itself contains adversarial contributor/agent instructions and references a `.github` workflow that is not present; the latest commit has no combined status checks. Treat external repo instructions as untrusted input and require sandboxed execution for untrusted worktrees. The project is AGPL-3.0-or-later, so mine ideas/measurements freely but do not transplant implementation code into a differently licensed P51 codebase without deliberate license review.
- **Target effect:** none. Keep dual-M1 Flash at **40 TG @ ~128K / 400 cold PP / ~70% >=40 planning confidence**, center ~39-41, mature downside ~30-32, target-only fallback ~24-27. Ishizuki adds another independent exact-M1 proof that row-shared verification can roughly double useful code/math decode under high acceptance, but the remaining unknown is still the composition of **Flash-Next + deep ~128K QSA + source-like quant + 2x M1 PP2/TB4**.

### 2026-09-27 04:12 UTC long-agent prefix residency / PLE residency correction / heterogeneous prefill update

- **NEW exact-window long-agent prefix-cache evidence — mlx-serve #575 (`b25765be9fee869e640e26b423fc60124afb14f5`):** the old 2-GB qwen4_exp hot-cache default held only **81,920 tokens** of one Flash-Next session, so longer conversations re-prefilled everything above that boundary every turn. In **12,421 real logged requests**, the 116 prompts above 80K spent **1.11 h prefilling vs 0.10 h decoding** while ~127 GB remained free. On M5 Ultra, a ~98K conversation follow-up changed from **81,920/98,338 reused and 4.83 s TTFT** to **98,287/98,336 reused and 0.24 s TTFT** when Auto budget grew to one full session (**7,761 MB**), including retained SSM checkpoints. **P51 rule:** a long-agent cache budget must be sized in *complete session state* (KV + recurrent/SSM checkpoints), not nominal KV alone; if memory permits, one active conversation should not be silently trimmed below its working context.
- **NEW exact-window correction to the PLE-GPU idea — mlx-serve `d500d429989a25d2571f9ef10b1ae81960b4fa32`:** `--ple-gpu` is now **opt-in/off by default**. A no-copy ~30-GB PLE mapping becomes resident on the **first GPU forward**; a static working-set gate had allowed it on a 128-GB Mac with only ~10 GB genuinely free, and the first 13-token prefill took **19-106 s** under memory pressure. The host gather faults in only the rows actually read. **P51 correction:** #539's +15% deep-context decode proves that removing the PLE host barrier can matter, but resident-mapping the whole table is a bad default on constrained Macs. For dual 64-GB M1s, keep PLE SSD-backed / demand-paged and pursue a no-host-barrier hot/staged subset rather than full residency.
- **NEW strict-window recurrent-prefill mechanism evidence — mlx-serve #574 (`0ae3f66b57df43d07383d9a1c736bedb0d423fdc`):** on M5 Max / Nemotron-H, changing a Mamba2 prefill from ~12 dispatches per token/layer + periodic host evals to one kernel that walks the whole chunk in 16-row passes raises 4K prefill from roughly **407-444 PP to 3,571-3,987 PP (~9x)** while keeping the recurrent state in registers. This is not Qwen GDN and gets no numeric P51 credit, but it strongly reinforces the hypothesis that recurrent prefill can be **launch/control bound** and that whole-chunk sequential-state kernels are worth a dedicated Apple7 experiment.
- **RECOVERED OLDER exact hybrid PD evidence — SGLang #36651 (merged 2026-09-12):** Qwen3.8-Flash-Next PD disaggregation transfers the model's state beyond ordinary KV: **PLE short-convolution + n-gram history, QSA pending raw-key/RoPE ring, compressed QSA keys, normal attention KV, and global attention/QSA metadata**. Matching TP4->TP4 aggregate-vs-PD production validation passed all **12 cases / 84 requests / 2,730 generated tokens with zero output-token-sequence mismatches**. Heterogeneous Mooncake TP1<->TP4 variants also achieved exact output-token parity.
- **RECOVERED OLDER prefill-PP + MTP composition — SGLang #40501 (merged 2026-09-22):** Flash-Next PD **prefill TP2xPP2 + native MTP -> decode TP4 + MTP** scores **0.980 GSM8K-200 with accept length 3.16**, matching the TP4 aggregate reference (0.980 / 3.16). It also transfers the MTP draft's QSA pending/RoPE/compressed-key state. **P51 implication:** hybrid-model prefill/decode separation is already demonstrated as a correctness-preserving architecture; the new 5070-Ti-prefill -> M1-decode lane is primarily a **cross-runtime canonical-state serialization** problem, not a question of whether Qwen hybrid state can cross the boundary.
- **27B heterogeneous P/D experiment lane:** prototype **32K CUDA prefill -> canonical state export -> MLX import -> next-token/logit parity**, then extend to 96K and bidirectional multi-turn mirroring only after parity. Wire identity should include a strong model/quant/config fingerprint + token lineage + positions/RoPE + each attention KV layer + each recurrent/GDN conv/temporal state + draft/MTP state if warmed. No performance target credit until CUDA->MLX numerical continuity is demonstrated.
- **NEW minor transport robustness — vLLM `fff03267dae61d03615225c2f48a06082d842e2d`:** NIXL now drops dead-peer state immediately instead of waiting for TTL. For any P51 remote-prefill prototype, peer/session state must be explicitly invalidated on disconnect so stale remote cache handles cannot survive a failed prefiller.
- **Target effect:** none. Keep dual-M1 Flash **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence** and single-M1 27B **25 TG** canonical. This pass strengthens the case that long-agent UX is currently dominated by *state reuse and prefill architecture* more than by another few TG of decode.

### 2026-09-27 10:23 UTC live-state accounting / transferred-state readiness update

- **NEW exact-window live-state accounting — mlx-serve `4e00f2af7a64fd846d31cfaa90247586cf853ca2`:** `/props` now counts **live requests' KV plus recurrent/QSA state**, including a slot while it is still mid-prefill, separately from activations. Restored shared views are skipped so the donor hot-cache entry is not double-billed. **P51 rule:** memory admission/telemetry must distinguish weights, persistent/shared prefix state, request-owned live KV+recurrent state, and transient activations/workspace; shared restored state has exactly one owner for residency accounting.
- **NEW exact-window transfer-readiness correctness — SGLang `38d865489af5ce7b1885577aa834b0d34dd99438`:** low-ratio sparse index-K access now explicitly waits for that layer's HiCache transfer to complete before dequantized or FP4 index rows can be read. **P51 heterogeneous-prefill rule:** a state object being logically registered or its metadata arriving is not enough; every CUDA->MLX imported layer/component needs an explicit completion/visibility state before any QSA/index/recurrent consumer may read it.
- **NEW exact-window prefix ownership rule — SGLang `d27efca3536e3fe084fe654a68d494d95af030a9`:** a prefix matched from the shared radix tree remains tree-owned when a request finishes; the request frees only its private suffix and **unpins** the protected prefix rather than freeing it. **P51 rule:** mirrored/persistent prefix state needs explicit ownership separate from request lifetime. Request completion releases references/pins, not shared state storage, preventing both double-free and needless re-prefill.
- **NEW exact-window transport-efficiency note — llama.cpp `d7fb90e8e2494b2908934d956a3202fd60152ee0`:** Linux RDMA RPC now spins briefly under load then sleeps on a completion channel when idle; the Apple Thunderbolt RDMA path is explicitly left with a TODO for equivalent non-spinning completion behavior. **P51 implication:** a CUDA-prefill or dual-M1 state link should use event/completion-driven idle waits rather than permanent polling; transport CPU burn is part of system efficiency even if it does not change raw TG.
- **KNOWN MERGE, not new evidence — SGLang `aa7a976807ea71320027713a8b90cf91cc1503c4`:** the previously recorded Qwen3.8 small CUDA-graph copy fusion (#41166) merged in this window. Its ~11 us -> ~1.4 us copy result and control-overhead lesson were already in canonical state, so no duplicate target credit.
- **Community/Ishizuki result:** no new planning-grade independent M1/M2 64K-128K receipt, no new Ishizuki commit, and no new MTPLX/Splash measurement after the prior boundary.
- **Target effect:** none. Keep dual-M1 Flash **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence** and single-M1 27B **25 TG** canonical. This pass mainly hardens the state-transfer/cache-lifetime model needed for the 5070 Ti prefill -> M1 decode experiment.

### 2026-09-27 11:03 UTC Strata/DASLab/TensorFold secondary-lane consolidation

- **STRICT WINDOW:** no qualifying primary-lane performance/correctness commit landed between **2026-09-27 10:23:44 UTC and 11:03:54 UTC**. One SGLang diffusion commit was unrelated. The items below are **RECOVERED CURRENT / SECONDARY-LANE** evidence intentionally added because they materially affect the RTX 5070 Ti and M1 27B plans.
- **RECOVERED CURRENT — Strata makes low-VRAM Flash-Next a serious local serving lane:** `Niko1221/Strata` on **RTX 5070 12 GB + Ryzen 7600 + 64 GB DDR5** reports at **128K context**: Q2_0 **65.1 TG / 543 PP**, IQ2_XS **52.0 / 472**, IQ3_XXS **44.8 / 414**, IQ3_S **42.2 / 378**. At short context the same rows are ~95/78/66/54 TG. This is a complete Flash-Next runtime, not merely a prefiller.
- **Strata architecture relevant to P51:** GPU holds always-used attention/GDN/router/shared-expert/output/MTP work plus a hot expert cache; RAM holds all routed experts and CPU computes misses concurrently; the 28.8-GB PLE/ngram shard remains SSD-backed; MTP drafts up to 3 tokens; prompt lookup drafts up to 5 only when measured surplus is positive. At >=64K, KV streaming keeps only the heavily read part resident in VRAM, freeing space for experts.
- **Strata long-context memory result:** Q2_0 at 262K improves **50.9 -> 62.6 TG** when KV streaming increases GPU-resident experts from **1,589 -> 3,872**. This is strong evidence that moving *cold* KV out of scarce VRAM can improve decode when the reclaimed VRAM buys more hot MoE experts. The lesson is model/topology-specific; do not transfer the exact gain to dense 27B.
- **Strata prompt-lookup receipt:** current engine reports code edits **6-11% faster**, with unrelated text unchanged, using measured acceptance/cost gating. This independently supports a coding-agent 'lookup/copy only when surplus > 0' lane rather than globally enabling prompt-copy speculation.
- **Strata KV-quality rule:** optional Q4_0 KV with Hadamard rotation is about **4% faster at 128K** and halves KV memory, but the project reports **+8-12% perplexity on long documents** even though needle tests still pass. For the P51/AA~40 quality lane, Q4 KV is therefore a throughput experiment, **not** a default; retain higher-precision KV until our long-context reasoning/tool/agent certification clears it.
- **RECOVERED CURRENT — DASLab Flash quant quality:** ISTA-DASLab's official Flash-Next GSQ-RCO **IQ3_XXS is 3.00 transformer BPW** and reports task average **92.57 vs BF16 93.12 (99.4%)**, AIME25 **100.00 vs 100.00**, GPQA-D **91.41 vs 91.92**, LiveCodeBench v6 **86.29 vs 87.43**. This makes 3.0 BPW a legitimate **AA~40 candidate arm**, not a certified source-like quant.
- **Important Flash quality caveat:** an independent Hugging Face user reports qualitative degradation on some real workflow/voxel-modeling tests for the official Flash GSQ-RCO IQ3_XXS; DASLab replied that the degradation was unexpected and needed investigation. **P51 rule remains unchanged:** benchmark parity is insufficient for AA~40 certification; require xhigh reasoning/coding/tools/long-context/semantic-continuity tests before promotion.
- **RECOVERED CURRENT — DASLab dense 27B GSQ-RCO strengthens the 3.5-BPW quality thesis:** official **IQ3_S = 3.50 BPW / 11.8 GB**, described as task-lossless: AIME25 **100.00 = BF16**, LiveCodeBench v6 **85.71 = BF16**, GPQA-D **89.39 vs 89.90**, task average **91.70 vs 91.87 (99.8%)**. IQ3_XXS 3.00 BPW is already close, but IQ3_S is the cleaner quality-reference arm for the M1 27B lane.
- **5070 Ti Flash-Next implication:** the weaker RTX 5070 12-GB card already demonstrates **42-45 TG + 378-414 PP at 128K** in Strata's highest-quality currently exposed IQ3 tiers. A 5070 Ti 16-GB should be treated as a **first-class complete Flash runtime candidate**, not merely a prefiller. Any 5070-Ti projection above the measured 5070 table remains an estimate until benchmarked on the user's machine.
- **RECOVERED CURRENT — TensorFold Apple-Silicon reference:** TensorFold publicly reports **Qwen3.8-27B 120-124 TG on M5 Max 128 GB with DFlash2**, versus **27 TG without drafts** for the stated workload. This is stronger-chip evidence only; there is no current planning-grade M1 Max TensorFold receipt, so it receives **zero direct M1 target credit**.
- **TensorFold/DFlash2 mechanism implication:** current DFlash guidance for Apple Silicon says quantized Qwen3.8-27B targets/drafts should use **verify block size <=5** under stock MLX because larger-row quantized matmul becomes inefficient. That aligns with Ishizuki/Splash/oMLX evidence that verifier row width must be tensor/GPU-specific and strengthens the priority of custom Apple7 few-row kernels rather than simply widening speculative blocks.
- **Planning consequence:** do not raise the canonical dual-M1 Flash 40/400 target or single-M1 27B 25-TG target. Add two concrete secondary lanes: (1) **5070 Ti + Strata + DASLab IQ3_S/IQ3_XXS** for practical Flash-Next serving and AA~40 certification; (2) **M1 27B TensorFold/DFlash2-inspired verifier + lookup-copy + whole-chunk recurrent prefill** for research and agent-effective throughput.

### 2026-09-27 12:54 UTC sync-free upper-bound planning / device-clamp update

- **NEW exact-window — vLLM #58684 (`c8d7a7dd13e2b40c013fb6d46be800937e4335fb`):** sparse-attention metadata planning under async scheduling previously did a **blocking D2H copy every metadata build**, including every MTP draft step, because exact per-row `kv_len` lived on device. The fix plans on CPU from a **sync-free upper bound + 32-token slack**, then clamps each work item's exact `kv_end` on GPU from device-resident sequence/layout state. The padded plan is reused across nearby decode/draft steps until the bound no longer fits.
- **Measured transfer evidence (H100 / GLM-5.3-Flash / fp8 KV / MTP-5):** async mean TPOT **11.09 -> 6.86 ms at c=1 (-38%)**, **21.87 -> 17.36 ms at c=8 (-21%)**, **45.04 -> 37.04 ms at c=32 (-18%)**. TTFT also improves; MTP mean acceptance stays ~4.2 and GSM8K is unchanged within run noise. This is stronger-chip/different-architecture evidence only, not direct Apple target credit.
- **P51 rule:** when dynamic exact metadata/state is on GPU, prefer **host-side conservative bounds + GPU-side exact clamp/validation** over a per-step device-to-host synchronization. Make bounded slack a runtime scalar/state, reuse the plan across nearby speculative/decode steps, and fail closed if actual state escapes the certified bound. This directly applies to QSA/index planning, speculative row-count/length metadata, and potentially recurrent/prefix-state admission on Apple.
- **Strict-window scan:** no new qualifying oMLX, mlx-serve, Splash, MTPLX, Ishizuki, Strata, DFlash, DS4, llama.cpp-Apple, DASLab/GSQ, ModelOpt or SGLang primary-lane receipt after the prior boundary. Reddit/community searches surfaced only already-recorded Splash/Strata/Flash threads and no new planning-grade M1/M2 measurement.
- **Target effect:** none. Keep dual-M1 Flash **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence**, single-M1 27B **25 TG**, and the existing 5070 Ti secondary-lane plan unchanged.

- **Boundary extension checked through 2026-09-27 13:12:54 UTC:** no additional qualifying primary-lane receipt appeared after the 12:54 consolidation. A same-day Ishizuki Reddit comment says Splash was ported into its kernel, but with no new commit/benchmark in this interval it remains watch-only.

### 2026-09-27 17:04 UTC Flash control-path / QSA batching / VRAM-reserve update

- **NEW exact-window — mlx-serve #584 (`42b34e2c7d2d4f6a41e6c0fbf731abb00e7dd31d`):** Qwen3.8-Flash-Next batched decode now launches an async-eval ladder every fourth layer, but only after a deferred **host-filled PLE leaf** has been materialized; evaluating earlier consumed the zero-filled placeholder and changed all 128 tested logits. On M5 Max 128 GB / mixed4-8bit / CPU PLE / MTP off, per-stream decode improved **43.6 -> 46.2 TG** for prose x2, **31.2 -> 32.1** for prose x4, and **41.0 -> 43.4** on an ~8.5K x2 case; serial decode stayed unchanged. **P51 rule:** lazy/asynchronous evaluation is a real several-percent lever, but every host-produced leaf/state has a materialization barrier that must be explicit before an early GPU eval may consume it.
- **NEW exact-window — mlx-serve #580 (`185bfe2cf7352c85c905c17bc0c5d53c7e8c0ee1`):** for **batched** long-context Flash decode, S=1 QSA rows now use the fused split-K sparse-attention kernel instead of a chain of gather/dequant/masked-SDPA kernels. On M5 Max with Q8 KV: four streams at ~11.9K improved **37.3 -> 34.9 ms/step**; around 47.6K the fused arm saved ~**3.0-3.1 ms/step** for four streams and **0.8-1.4 ms** for two; around 95.5K it saved **3.1-3.6 ms** for four streams. A lone stream was neutral/slightly worse, so the floor is lowered only for n>=2. **P51 rule:** QSA dispatch policy must include concurrency/batch topology, not only S and KV length; kernel-chain launch overhead can dominate even when each request contributes only one decode row.
- **NEW exact-window — Strata v0.1.9 (`0680ab633f69deb23ac6c4691737386d459a9843`):** sizing the adaptive expert cache before loading the native output head left only **30 MiB free** for IQ3_S at 128K; the CUDA driver paged GPU memory and the request stalled indefinitely at the first verify window despite GPU showing 100% utilization at low power. Loading the head first and then sizing the cache leaves **480-626 MiB free** with everything loaded; the expert cache is ~8% smaller but decode is not slower (Q2_0 32K measured **78-79 TG median vs 71.7** on v0.1.8 greedy prompts). Startup now warns below **256 MiB** free. **P51/5070-Ti rule:** never size hot expert/KV caches to nominal free VRAM. Reserve post-load headroom for output head, graphs, first-use workspaces, desktop/driver and verification buffers; paging/thrashing can look like 'GPU busy' while forward progress collapses.
- **QUALITY EXCLUSION — Strata experimental speed projection (`9e599c076e2f74a83b8576c5e171f7e99e635062`):** optional control-vector/refusal-direction projection is off by default, costs only 0.2-0.4% per token but reports mean KL **0.063** over 2,557 teacher-forced tokens. This is a behavior-changing intervention, not an inference optimization; keep it **off** for AA~40/source-like certification and performance baselines.
- **Reddit 'silent bottleneck' thread:** direct Reddit retrieval was unavailable at scan time, so no exact quote/number from the post is promoted. Its broad thesis is independently supported by current code: blocking D2H planning sync (#58684), host-filled lazy-state barriers (#584), multi-kernel QSA launch chains (#580), and VRAM paging from insufficient reserve (Strata v0.1.9) all create large losses without changing model FLOPs. Treat the thread as community framing, not evidence.
- **Target effect:** none. Keep dual-M1 Flash **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence**, single-M1 27B **25 TG**, and the 5070-Ti Strata lane experimental pending exact-hardware/AA~40 certification. This pass lowers confidence that any one roofline metric (bandwidth, FLOPs, nominal VRAM occupancy) is sufficient to predict realized throughput.


### 2026-09-27 17:22 UTC quant-sensitivity / row-invariant verify / hybrid-rollback update

- **RECOVERED CURRENT + UPDATE — mlx-serve #594 tensor-sensitivity map:** M5 Ultra Flash-Next experiments keep head/embed, hyper-connections, router, GDN a/b, attention k/v, indexer, PLE and MTP at 8-bit while lowering GDN qkv/z/out, attention q/o and shared expert to 4-bit. This **mid48** arm cuts S=1 forward GPU time by about **11.2%** and S=4 verify by **4.9%**; its 400-question MMLU-Pro/output-length behavior stays near repeat-run variability, while an all4 arm shows materially larger output-length/runaway changes. **P51 quant rule:** treat GDN qkv/z/out + attention q/o + shared expert as a candidate lower-precision tier, but continue protecting HC/router/GDN-state/indexer/PLE/MTP/head paths. This is a search prior, not AA~40 certification or M1 speed credit.
- **RECOVERED CURRENT — oMLX #4012–#4018 Flash roadmap gives a useful component ruler:** on M5 Ultra/oQ5e at 24K, reported prefill is **3,978 PP with MTP / 4,100 without**, with time split roughly **MoE 39% / GDN 24% / QSA 20% / HC 11%**. The same roadmap calls out MLX command-buffer byte caps, PLE/small-op fusion, hidden gathers/copies and MoE/GDN kernel gaps. **P51 Apple rule:** profile PP by MoE/GDN/QSA/HC/PLE plus command-buffer/host-gap terms before choosing kernels; stronger-chip absolute rates get zero direct M1 credit.
- **RECOVERED CURRENT — row-invariant verification is a correctness requirement, not an aesthetic one:** oMLX #4014 reports Lightning-MTP greedy output diverging from MTP-off on **3/4** realistic prompts at near ties because batched verify arithmetic depends on row count, while a TensorFold row-invariant path is byte-identical to serial on **4/4** of those prompts. P51 verifier certification must compare serial S=1 with S=2–5 verify at logit/token level and keep greedy versus sampled rulers separate.
- **RECOVERED CURRENT — speculation economics are sampling/workload dependent:** oMLX #4021 reports a newer MTP path at roughly **-9.2%** for fixed-depth greedy and **-3%** for adaptive greedy on its M5 Flash workload, while sampled/top-k and one code workload improve. Draft depth/window selection must be conditioned on sampling mode + workload + measured surplus, not promoted globally.
- **RECOVERED OLDER — DFlash #172 hybrid rollback bug:** the HF DFlash loop's normal cache crop can remove rejected attention KV/conv rows while leaving GDN **recurrent state mutated by rejected drafts**. The reporter measures **12–41/384** target-argmax differences under alternate rejection patterns; restoring recurrent state then replaying accepted rows removes the effect. **P51 hard gate:** hybrid rollback must restore every recurrent/conv/temporal component to the committed boundary; attention-KV crop alone is not lossless. Add adversarial partial-acceptance patterns and recurrent-block-boundary cases.
- **RECOVERED CURRENT — vLLM #58894 prefix-hit/DFlash failure independently reinforces the same state-identity rule:** on hybrid GDN, acceptance can collapse permanently to 0% immediately after a prefix-cache hit when recurrent/block geometry is wrong. Prefix state, recurrent checkpoint, draft state and token lineage must share one authoritative geometry, and first-hit transitions must be tested explicitly.
- **UPDATE — Strata #29 long-generation liveness:** an RTX 4090/IQ3_S/262K report sustains ~75 -> high-50s TG before a hard no-progress stall; a newer v0.1.11 attempt is reported to stall again at a different generated-token count. Root cause is open and hardware differs from the user's 5070 Ti, so there is no speed-target credit. **P51/5070-Ti production gate:** add a long-output soak with progress, GPU power/utilization, CPU activity and post-load VRAM/residency telemetry; short 256-token matrices do not establish runtime liveness.
- **Target effect:** none. Keep dual-M1 Flash **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence**, single-M1 dense 27B **25 TG**, and the 5070-Ti Strata lane experimental until exact-hardware + AA~40 + long-run liveness validation.


### 2026-09-27 18:28 UTC Apple7 command-duration / exact-5070-Ti liveness update

- **NEW exact-window — Splash-M1 1.1 weight-residency correction (c5f93c964e58d3ba45c4e7e617b2e60ccae99b7c):** on **M1 Max 64 GB / Qwen3.8-27B**, removing file-backed weights from the Metal residency set made host-available memory swing by roughly the entire weight footprint while a command ran; on smaller Macs this could push the governor below its 1-GB headroom and deny GDN snapshots, yielding cached 0. Restoring weight residency keeps cache reuse alive; the branch reports ~8K prefill in **61 s**, ~30K in **243 s**, growing-chat cache reuse and a 54/54 smoke eval. This is direct physical evidence in the **~120–130 PP class** and materially strengthens the plausibility of the existing single-M1 **110 PP** target, but the branch/quant is not the frozen P69/AA ruler, so TARGETS is not raised.
- **RECOVERED CURRENT — bounded Apple7 prefill command duration (4083ec6ad33167fe7f0d454b6449ea91f8f2000a):** a full 2,048-row prefill command can take ~12 s around 8K and ~1 minute around 170K on M1, and macOS aborted a long command as ImpactingInteractivity. Dynamically halving isolated work to keep a command around <=5 s is TTFT-neutral in ABBA at 8K (**60.8/60.9 s**) and 30K (**269.0/269.1 s**) and allowed a **7-hour / 229K-context** agent session where the prior build failed at 176K. **P51 Apple rule:** qualify PP with max single-command duration/watchdog health in addition to aggregate tok/s; whole-chunk recurrent work may require an outer command-time bound.
- **RECOVERED CURRENT — Apple7 generic GGUF execution (15abab5b1d2660ef8dc872d5ce57deac14022eaf):** custom simdgroup-MMA GGUF kernels run UD-Q4_K_M Qwen3.8-27B at **31.6 TG** on M1 Max 64 GB with 8K cold TTFT **65.9 s**, close to the fork's Splash Q4 package at ~38 TG / 62.8 s. Treat this as evidence that much of the stock-format gap is kernel/runtime quality rather than an intrinsic GGUF ceiling; no deep-context or AA target credit.
- **NEW exact-window — Strata #31 exact RTX 5070 Ti liveness failure:** Windows / **RTX 5070 Ti 16 GB** / Swift-Qwen3.8-Flash-Next GSQ-RCO IQ3_XXS / Q4 KV / 32K resident KV / spec4 / 5,059 expert slots / ~707 MiB free VRAM hard-wedged **4 times in ~2.5 h**. Generated count froze while GPU stayed 100% at ~69 W and the process remained alive; failures occurred at 13, 130, 218 and 91,058 generated tokens, and cancellation did not recover the single server slot. This is the user's exact GPU class and makes a multi-hour liveness/cancellation matrix a **blocking promotion gate** for the 5070-Ti Strata lane. Raw speed potential is not revised downward; runtime-readiness confidence is.
- **UPDATE — Strata #29:** the same wedge reproduces with Q4_0 after an INT8 run, so do not attribute the failure to INT8 KV. The maintainer stated a cause was known, but no public root-cause/fix had landed by the 18:28:19 cutoff.
- **NEW transfer-mechanism evidence — SGLang HiCache #39726 / e581520c67a921feda4433bc4e4d41f3514a9d06:** page-unified host KV can load back one layer at a time directly from pinned mapping. On B200/PCIe5, quota-16 reaches **39.7–47.8 GB/s** versus a **53.8 GB/s** contiguous-copy ceiling; shipped quota-2 stays ~15–18 GB/s to reduce interference with forward compute. **P51 heterogeneous-state rule:** transfer concurrency is an end-to-end scheduler knob, and imported layers become consumable only after per-layer completion/visibility.
- **SAME-DAY CURRENT — MoEspresso 3 low-memory Flash-Next:** M1 Max 24-core / 32 GB reports **12–15 TG** with BF16 PLE SSD-backed, aggressive IQ2/IQ3 routed experts, K4/V4 old-cache body and a Cache-Prior policy that protects the top two original routes but biases remaining selections toward resident experts. The package retains all experts and demonstrates extreme-capacity streaming, but routing/KV are intentionally behavior-changing and the local 48-question score is below the hosted source row. Keep this as an optional locality/capacity experiment with **zero AA~40 or canonical TG credit**.
- **Target effect:** dual-M1 Flash remains **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence**; single-M1 dense remains **25 TG / ~110 cold PP**. The Apple7 evidence improves confidence in the existing PP goal; the exact-5070-Ti wedge blocks Strata production promotion until fixed.

### 2026-09-27 23:23 UTC exact-DFlash / TensorFold-0.3.5 / residual-Strata-liveness update

- **NEW exact-verifier convergence — mlx-serve #590 / eca42620018566d4dd0acc3eab9565685b46dd5b:** mlx-serve ports TensorFold's row-exact 4/6/8-bit matvecs, fixed-order multi-row qmm, fixed-split row attention, absolute-position keyed sampling and draft-tree construction. Exact DFlash uses arithmetic whose row result does not depend on sibling-row count; ordinary MTP/serial remain on the faster stock path because forcing exact-row arithmetic costs MTP roughly 30%. **P51 consequence:** P69B13 begins with a cross-diff of TensorFold + mlx-serve + Ishizuki + frozen P69B12 before inventing another shader. No new M1 numeric receipt, so no target credit.
- **NEW TensorFold 0.3.5 architecture:** current-window commits add shared exact verification rounds across concurrent requests, a Flash-Next long-prompt prefill path, message-boundary exact resume and wider quantized lane support. M1-M4 dense Qwen3.8 continues to use row-exact 4-bit/group-64 simd_qmm windows up to 16 rows; M5 lane kernels now cover affine 2/3/4/5/6/8-bit projections. Fresh and resumed prompts share the same tokenizer-derived chunk plan. **P51 rule:** cache identity includes chat-template/tokenizer/chunk-plan identity and fresh/resumed boundaries must match exactly.
- **NEW Strata v0.1.12 root cause + mitigation, but not closure:** the original wedge was traced to a CPU expert-pool sleep/wake race where a late worker could claim next-batch work before publication completed and corrupt completion accounting. v0.1.12 ties jobs to batch epochs and adds a 120-s no-progress watchdog that terminates/restarts the engine. The exact **RTX 5070 Ti 16 GB** reporter nevertheless caught a watchdog event on v0.1.12 after ~45 min, localized to **verify window: the CPU experts of layer 9**; recovery worked automatically. **P51 status:** operationally recoverable, residual liveness failure still present; keep production promotion blocked until a multi-hour zero-watchdog soak passes.
- **NEW LiLiCorr mechanism — SGLang #37462 / 78eee88113510d6b0d70f6978739d0845e2fff0f:** a learned lattice reranker improves joint coherence of DFlash draft slots while leaving target verification untouched. On Qwen3-8B/H100, matched greedy tests report **+9.1% to +14.6% output throughput** vs head-free DFlash and **+7.6% to +21.7% acceptance**. A per-block CPU seq-len mirror costs ~8% and forcing the head outside the captured graph costs ~8.4%, while torch.compile itself is essentially neutral. **P51 implication:** after verifier-cost work, increasing accepted useful tokens per fixed target window is a serious alternative to widening S; host sync and graph placement belong in the acceptance-economics model.
- **UPDATE hybrid speculative metadata cost — vLLM #58638:** Qwen3.6-35B-A3B + DFlash can expand from 4 to 46 cache groups, each rebuilding metadata. Revised grouping 46 -> 17 reports **460 -> 733 TG at c=1 (~+54%)**, +36% at c=32 on B300. No Apple numeric transfer; make **cache-group count / metadata-builder count** an explicit P51 cost term beside verifier forward time.
- **RECOVERED CURRENT draft-vocabulary optimization — vLLM #58578:** on Arc Pro B70, Qwen3.8-27B's MTP drafter repeatedly reads the target's ~2.54-GB / 248,320-row full lm_head. Restricting the **draft-only** head to a 50,521-token list reduces 3-draft step cost **50.7 -> 40.2 ms** and raises **59.5 -> 74.6 TG** at approximately unchanged acceptance; Qwen3.6-35B-A3B reports **147.4 -> 189.8 TG**. The target still verifies/emits over the full vocabulary, so missing draft tokens cost acceptance rather than target expressivity. Add a P51 arm: **reduced-vocab draft head + full protected target head**, independently before combining with draft-head quantization.
- **Boundary discipline:** oMLX #4040 opened before this cutoff but its visible body was edited after **23:23:40 UTC**; defer it to the next scan rather than importing post-cutoff text.
- **Target effect:** none. Keep dual-M1 Flash **40 TG @ genuinely filled ~128K / 400 cold PP / ~70% >=40 confidence** and single-M1 dense **25 TG / ~110 cold PP**.

### 2026-09-28 08:53 UTC Apple7 exact-verifier / Strata-0.1.13 / hybrid-state update

- **NEW direct M1 Max dense27B receipt:** TensorFold issue #48 comment at 00:23:31 UTC reports M1 Max 32-core/64GB, Qwen3.8-27B 4-bit/g64, one stream greedy/thinking-off. Reducing physical simdgroups 16->8 while leaving logical split/reduction order intact lets the exact-row path run. Short generation **16.96 TG serial -> 33.64 TG DFlash2**; 8/8 paired responses have matching token_sha; three Ruby tasks **101.50 -> 68.78 s**; peak footprint 18.57->20.57 GiB, no new swap. The ~6,566-token cold prompt reportedly spent ~61 s in prompt processing, implying about **108 PP**. One paired run and short-context only: strengthens the ~30-TG engineering / ~110-PP single-M1 plan, does not raise the 25-TG canonical ruler or credit dual-M1 Flash.
- **NEW Apple7 physical-vs-logical verifier rule:** TensorFold 0.3.5.1 (beddbb7) and mlx-serve 2496d independently fix M1/M2 failures caused by per-compiled-kernel threadgroup limits (notably ~448 threads for the relevant M1/M2 specialization). Both reduce **physical simdgroups** while preserving the logical arithmetic split and reduction order. P69B13 should explicitly separate these dimensions and fail closed by chip+compiled kernel+shape.
- **NEW oMLX exact Qwen verifier merge:** #4023 / d403e460 makes Qwen3.8 Flash-Next Lightning MTP verify rows reproduce serial one-row arithmetic across quantized projections/lm_head, GDN normalization, dense attention and gathered QSA. Real-model R1..4 checks show max |Δlogit| 0 and MTP-on == MTP-off byte-for-byte. A follow-up found 13/47 2-row windows near the 1,024-key SDPA plan boundary differed before boundary-aware routing (max |Δlogit| 1.29), proving exactness must be certified at runtime kernel-plan transitions.
- **NEW fused exact verify — oMLX #4041 / e15e5b5:** exact MoE/GDN/QSA verify fusion recovers **~+10% MTP decode** on M5 Ultra oQ5e while preserving row equality and rollback state. However a separate oQ6e report shows global per-row exact routing destroys c=4/c=8 throughput (c8 ~199 -> ~105-108); gating exactness to single-stream/small-S restores it. **P51 rule:** dispatch exact verify by chip x quant x shape x S x concurrency, never globally.
- **UPDATE cross-generation exactness:** M3 Ultra exposed a one-ulp GDN beta mismatch (fast bf16 exp vs mx.sigmoid), fixed by 8cc7812. #4050 adds per-device qmv/SDPA/GDN/HC/MoE/QSA/PLE exact diagnostics and finds a sampler-level mismatch: serial greedy picks bf16 log-prob argmax while verify used raw-logit argmax. **P51:** certify emitted-token semantics and near ties on M1 itself; include 1K/4K/8K/16K/64K attention boundaries.
- **UPDATE M1 idle TTFT:** oMLX #4040 on M1 Ultra64GB / 41.8GB model measures first forward **~862–1012 ms after >=2 s idle** vs 20–27 ms repeated. Keep-warm alone does not solve the default-unwired case; bounded wiring + 0.5-s trivial GPU keepalive brings the next forward to ~40–49 ms. Add 0.5/1/2/5+s idle-gap TTFT ruler and separate GPU wake from weight-page residency.
- **NEW Strata 0.1.13 PP:** on RTX5070 12GB + R5 7600 +64GB, 32K PP Q2_0 **572->1290**, IQ3_S **383->1208** through adaptive <=8192 chunks, whole-chunk PLE, llama.cpp MMQ experts and overlapped expert streaming. Some MMQ/chunk changes are not bit-identical (32K teacher-forced same-top1 85.9%, KL0.38 for MMQ vs 89.8%, KL0.33 alternate-chunk yardstick), so this is not AA~40 certification. Two new prompt-path NaN/expert-corruption defects were fixed before the v0.1.13 release creation point.
- **UPDATE Strata exact-5070Ti liveness:** two v0.1.13 stalls at ~46 min and ~21 min show every CPU expert job done and all workers parked while the host waits on the GPU-side layer handshake even though the GPU ring advanced. Free RAM differed ~1.9 vs 8.5GiB, weakening memory pressure as common cause. Watchdog recovery works but one cold restart reportedly took ~15 min. Production gate remains blocked; suspected locus moves from CPU pool toward CUDA/host protocol/synchronization.
- **NEW SGLang real-model hybrid PD parity:** #41378 validates Kimi-Linear PD split across page/DCP/chunk and cached-prefix boundaries with exact tokens + <=1e-3 logprob delta where a valid monolithic oracle exists; heterogeneous-TP exactness is deliberately not asserted. Use the same boundary-oriented, topology-aware oracle design for 5070Ti-prefill -> MLX-import.
- **NEW vLLM recurrent metadata reuse:** #58762 reuses Mamba/GDN batch-level metadata across KV groups and only changes state/block mappings; on B200 Qwen3.6+DFlash 46-group setup, c1 step -40%, output +57%, CUDA API calls 1032->424, acceptance unchanged. P51 scheduler should reuse equivalent recurrent metadata rather than rebuild per logical group.
- **Target effect:** dual-M1 **unchanged** at 40 TG genuinely filled ~128K / 400 cold PP / ~70% >=40. Single-M1 25 TG / ~110 PP canonical stays unchanged, but confidence in the ~30-TG engineering band and ~110 PP ruler materially improves.

### 2026-09-28 10:51 UTC TensorFold-0.3.6 / Strata-0.1.14 / recurrent-cache update

- **NEW TensorFold 0.3.6 capacity lane:** `--ple-on-ssd` leaves Flash-Next PLE on SSD and, on an emulated 128-GB M3-Ultra budget, peaks at **85.6 GiB** while decoding **0.91–1.03x** resident. `--ssd-experts GIB` streams routed experts into a GPU pool; Flash-Next fits an emulated **64-GB** budget at **39.5 GiB peak** with tokens identical to resident, but only **0.31–0.39x resident decode**. Treat as source-identical capacity/fallback evidence, **zero canonical 40-TG credit** until M1 physical results exist.
- **NEW TensorFold M1–M4 PP exactness caveat:** release notes state the 27B prompt-attention path around **8,192 keys** is not bit-identical to one stock MLX call when a chunk splits with a short tail; drafted==serial and resumed==fresh still hold. Adaptive chunk size can also make long-prompt replies differ across machines with different memory budgets. **P51 rule:** freeze/record chunk plan in AA/PP and exported-state lineage; self-consistency is not the same as stock/source-path identity.
- **NEW agent protocol failure:** TensorFold #60 on M3 Ultra / Flash-Next reports complete tool-call markup emitted inside an unclosed think block being swallowed into `reasoning_content`, yielding an empty API turn; **2/128** real agent-trace replays. Add unclosed-think/tool-call recovery and streamed/non-streamed parser cases to AA tool certification.
- **NEW Strata 0.1.14 root cause/fix:** 0.1.13 thread dumps show the residual IQ-model wedge with the host blocked in **cudaMemcpyAsync** on an NVIDIA-driver lock inside `Verifier::fetch_dma`; native IQ packs issued host CUDA DMA/callback calls inside a verify window while the GPU waited on their flags. 0.1.14 makes the GPU copy kernel the default for every pack, avoiding host CUDA calls in-window; IQ3_S measured **45.3 -> 44.8 TG (~1% cost)**. This is a concrete landed fix, but no exact-5070-Ti post-fix clean soak existed by the cutoff. Keep the production gate until the old HumanEval-47/long-degenerate repro passes for hours without watchdogs.
- **RECOVERED CURRENT oMLX #4051:** M3 Ultra Flash-Next rc1 report shows `boundary_snapshot_unavailable ... available_boundaries=0` on multi-turn cache stores and cold reprocessing of repeated 27K prefixes. Whether or not same-session partial-block reuse helps, a durable GDN prefix needs a committed recurrent snapshot at the cache boundary. **P51:** exported/imported state is incomplete without recurrent boundary checkpoint + lineage; fail closed to re-prefill otherwise.
- **NEW SGLang #41165 state-spec design:** predicate-registered linear-attention models can receive Mamba radix-cache extra-buffer leaves from the model spec rather than hard-coded architecture allowlists. P51 state transfer/cache capabilities should likewise be spec-driven.
- **Boundary discipline:** Strata #53 opened at 10:51:11 UTC but its visible body was edited after this pass's 10:51:31 cutoff; defer its sampler-parity claims to the next scan. mlx-serve #605 currently lacks enough isolation/evidence to promote.
- **Target effect:** none. Keep dual-M1 Flash **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence**, single-M1 dense **25 TG / ~110 PP**.

### 2026-09-28 11:34 UTC 5070-Ti target true-up / Strata sampler / cache-boundary update

- **RECOVERED CURRENT exact RTX 5070 Ti CUDA-v2 receipt — feveromo f2495156 (2026-09-27 20:16 UTC):** exact GB203 16-GB card, Qwen3.8-27B abliterated GSQ-RCO IQ3_S + embedded MTP, Q4_0 target/draft KV, xhigh-capable llama.cpp custom patch. Direct ladder: short **130–131.6 TG**, 15.7K **104.7 TG / 2030 PP** (sampled 111.7 TG), 62.5K **98 TG / 1814 PP** (sampled 96), 92.9K **94.8 TG / 1696 PP**, 128.8K **91.3 TG / 1576 PP**. VRAM peak at 128K ~14.93 GiB server /15.07 GiB whole card. Mechanisms include 2–4-column qmv reuse, reduced-vocab draft head, fused MTP catch-up, distribution-exact Gumbel-coupled sampling, small-query Q4 attention, INT8 prompt QK, glue fusion and faster GDN prompt kernels. **Target effect:** the old 5070-Ti **250 PP** mature target is superseded; TARGETS now uses a context-aware TG/PP ladder. Checkpoint is abliterated IQ3_S and is not AA~40-certified.
- **NEW Strata 0.1.14 measured matrix on weaker RTX5070 12GB:** at 128K, Q2_0 **1208 PP/67.2 TG**, IQ2_XS **1071/59.8**, IQ3_XXS **1015/45.8**, IQ3_S **931/40.5**; 32K PP 1070–1308. Confirms consumer-Blackwell Flash prefill comfortably exceeds the dual-M1 400-PP objective; for 5070Ti-prefill -> M1-decode the bottleneck is state export/transfer, not CUDA prefill compute.
- **RECOVERED CURRENT Strata CUDA eager-module admission — 6609960; NEW 0.1.15 code de19166:** lazy first-use MMQ kernel loading could OOM at 64K/128K after expert cache filled VRAM. Set CUDA_MODULE_LOADING=EAGER before context creation; code costs ~30 MB / ~20–23 expert slots and is accounted before cache sizing. The v0.1.15 release publication itself occurred 9 s after this pass cutoff and is not counted. **Rule:** reserve code/module memory before expert/KV admission.
- **UPDATE Strata sampler semantics #53:** source confirms sampled candidates are penalized before top-k and then `scaled()` applies repetition/frequency/presence penalties a second time after temperature. Greedy applies once. Internal host parity duplicates the same behavior. Add an independently derived canonical sampler oracle; neutral-penalty benchmark rows are unaffected.
- **NEW vLLM #58957 HC fusion:** Qwen4Exp BF16 HC down+SiLU fusion wins on GB300 for M=1–48 (1.1–1.77x micro), loses at M=64, and improves E2E TPOT ~2–4% at c1–16. No Apple/5070 numeric credit; reinforces shape/concurrency-specific fusion dispatch.
- **UPDATE vLLM #52244 hybrid GDN prefix-cache + MTP:** producer snapshots must be written at positions the replay/rewind lookup can actually land on. Prompt-tail-only recurrent snapshots can intersect attention hits down to a previous page or zero. P51 cache/export checkpoint placement must derive from consumer replay semantics, not only producer chunk boundaries.
- **UPDATE vLLM #58815 PLE file gather:** Flash-Next 47.7-GiB PLE access measured ~17.6 rows/step and ~1.6 MiB working set over 800 steps. Dedup + fadvise + preadv staging is ~0.4% of c1 ITL and ~7% at c16 on DGX Spark, with cold 30K TTFT ~2 s over warm. Supports bounded file-backed/staged PLE rather than full residency.
- **Target effect:** 5070-Ti dense lane recalibrated; dual-M1 Flash remains **40 TG@128K / 400 PP / ~70%**, single-M1 dense remains **25 TG / 110 PP**.


### 2026-09-28 13:58 UTC pruned-Coder / agent-protocol / state-mapping update

- **NEW Strata 0.1.16 + DASLab pruned Coder lane:** Qwen3.8-Flash-Next Coder keeps 256/512 experts/layer, still top10 active, retained weights 3.5 bpw, 29.6GB resident transformer shard. DASLab xhigh quality: LiveCodeBench v6 **87.43->86.28 (98.7%)**, SWE-bench Verified **82.8->75.6 (91.3%)**. Therefore specialized code/agent/vision compression, **not source-like AA~40 primary lane**. Strata RTX5070-12GB matrix: 32K **1298 PP/53.3 TG**, 128K **1266/44.0**, 262K **1034/42.8**; a 3090 agent session reached 192K over ~3.5h with zero engine errors. Keep as capability/capacity fallback and pruning research lane only.
- **NEW Strata 0.1.17 closes sampler/protocol defects:** sampler now applies penalties once and uses llama.cpp ordering (penalties -> top_k -> top_p -> min_p -> temperature); greedy unchanged. Anthropic `/v1/messages?beta=true` and late system/developer messages now work, enabling a reported real Claude-Code edit/test flow with KV reuse. Add endpoint/envelope normalization to agent-runtime certification.
- **NEW Strata admission risk #60:** Windows 10, 16GB VRAM +64GB RAM, Swift IQ2_XS/64K: whole-arena cudaHostRegister fails, ~29GiB slices pin, auto sees 9.96GiB free and sizes a 9.28GiB expert cache, then cudaMalloc fails OOM. No diagnosis by cutoff. Add exact-5070Ti Windows admission/fragmentation margin tests; separate from the mid-generation stall fix.
- **UPDATE Strata liveness:** no post-0.1.14/0.1.15 exact-5070Ti clean soak appeared in #31/#29 during this window. Production gate remains.
- **NEW SGLang #41144 recurrent-state mapping bug:** unified-memory short-conv checkpoints used virtual mamba_track_indices as physical slots; cold runs were correct but prefix hits restored stale/foreign state (max |Δlogprob| 0.086/0.120 and greedy-token flips). Translation to physical slots restores bit-exact hits. **P51 rule:** state lineage includes logical->physical slot mapping; never write virtual ids directly to physical recurrent storage.
- **NEW llama.cpp d77dd08 Metal shape-stability lesson:** excluding zero-element tensors from fusion matching made no-output decode graphs pack differently from reserved graphs and triggered allocator re-reserve. Zero-element tensors now preserve structural packing and dispatch zero threadgroups. Add S=0/no-output/partial-accept graph cases to Apple verifier tests. Same commit broadens recurrent rollback/split-replay tests across generated model architectures.
- **UPDATE vLLM #58114 PLE metadata:** builder work -32% to -48% in microbench, but Qwen3.8 Flash E2E c1 is -1.5% while c8 is +5%. Treat metadata optimization primarily as B2-B4/multi-agent work unless B1 wall-clock proves value.
- **NEW EXPERIMENTAL TensorFold #68:** disk-spilled exact conversation checkpoint: 35.6K-turn resume **2.3s vs 26.2s cold**, 35.4K tokens reused, byte-identical output; ~2.2-2.4GiB spill in 0.18-0.19s and 0.24s read on M5 Ultra. Preserve as multi-agent SSD cache-tier experiment, no M1 timing transfer.
- **UPDATE mlx-serve #604/#606:** compact GDN initial-state + accepted-path replay and up-to-16-row DFlash tree substantially improves M5 Max code TG but is checkpoint/workload dependent and not uniformly better than TensorFold. Runtime replay length replaces per-length template specialization. Supports compact replay architecture; no M1 numeric credit.
- **WATCH oMLX #4054:** M5 Ultra oQ5e served MoE is ~2.60ms/step R1 and 5.69ms R4 against byte floors ~1.81/4.17ms, leaving ~0.79/1.52ms theoretical gaps. Profile/roadmap only; measure M1 bytes/bandwidth before transfer.
- **Target effect:** none. Dual-M1 Flash **40 TG@128K /400 PP /~70%**, single-M1 dense **25/110**, RTX5070Ti dense context ladder unchanged.

### 2026-09-28 15:56 UTC exact-5070Ti Strata stability validation + target ladder

- **NEW exact-card post-fix stability receipt:** original RTX5070Ti16GB/Ryzen9800X3D failure box ran Strata 0.1.14 for ~3.5h / three 164-task HE+ sweeps across q4_0 and int8 KV with **zero stalls and zero watchdog trips**; the pre-fix workload had frozen every ~20-45 min. HE+ score reported **153/164 (93.3%)** on both q4_0 and int8. This materially raises liveness confidence.
- **CORROBORATION:** separate RTX5060Ti16GB/64GB host reports a few sustained hours on 0.1.14 with zero stalls/watchdogs. Its PCIe4 x8 H2D (~13.7GB/s) favors lower pcie_frac than x16, reinforcing PCIe-aware expert-streaming policy.
- **UPDATE Strata 0.1.18:** no P51 speed change; update/setup polish plus zero-length penalty-window sampler guard.
- **OPEN admission risk:** issue #60 now has a second similar 16GB/64GB report; no root cause by cutoff. Keep Windows auto expert-cache admission as a separate gate from generation liveness.
- **TARGETS:** added a dedicated Strata/RTX5070Ti Flash-Next section. IQ3_XXS balanced targets: <=8K **100 TG (~75%)**; 32K **95 TG /1300 PP (~75%/~85%)**; 64K **90/1250 (~80%/~80%)**; 128K **78/1150 (~65%/~75%)**. Stretch 128K **90 TG (~35-40%)**. IQ3_S quality lane: <=8K **85 TG (~65%)**; 32K **78/1200 (~65%/~80%)**; 64K **70/1150 (~60%/~75%)**; 128K **60/1050 (~55%/~70%)**.
- **Strata stability targets:** 8h zero stalls/watchdogs **~90% planning confidence**; 24h **~75%**; Windows 16GB/64GB auto admission first-try success **~70%** until #60 resolves.
- **AA planning priors:** IQ3_XXS AA>=38 **~85%**, AA>=40 **~65%**; IQ3_S AA>=40 **~75%**. These are not measured custom-AA scores.
- **Dual-M1 / single-M1 target effect:** none.

### 2026-09-28 17:54 UTC mixed-bit lanes / resident-agent / Strata 0.1.19 update

- **NEW Strata 0.1.19 penalty semantics:** 0.1.17 fixed double-penalty/order, but speculative batches still gave only the first checked token the true history. 0.1.19 gives every checked token serial-equivalent history; non-neutral penalties cost **~1-11% TG** from lower acceptance, neutral requests unchanged. Strata target tables remain neutral/no-penalty rulers; production penalty configs get a temporary 1-11% discount until exact-5070Ti 0.1.19+ data exists.
- **NEW Strata Windows admission root cause:** issue #60 is system **commit/page-file** exhaustion, not the 32-GB shared-GPU-memory figure. 0.1.19 retries a smaller expert cache and warns below 4-GB pagefile; exact host should use System-managed page file before benchmarking. Admission risk downgraded from unknown fragmentation to known host configuration dependency.
- **NEW Strata calibration:** `--calibrate` measures PCIe share, draft depth and CPU threads, retaining only >3% wins; +7.6% on Coder/RTX5070 test PC. Use exact-host calibration, no target credit yet.
- **NEW Strata state-schema correction:** first #57 multi-conversation snapshot omitted indexer per-sequence spare key `idx_dead`. Revised shared core preserves it and passes 30 returns at 2K/40K/120K with exact baseline state/output. At 51,133 cached tokens A->B->A resumes in 1.237s. Canonical P51 state image must include the indexer spare/dead-row state, whole-image fingerprint, pre-write validation and fail-closed transfer failure.
- **NEW TensorFold 0.3.6.2 mixed-bit exact lanes:** dense Qwen MLX affine 2/3/4/5/6/8-bit, groups32/64/128 and per-module mappings now run through exact lane verification; M1-M4 use packed row decoder. M3 Ultra oQ4 mixed 27B: **114-120 code /59-61 chat TG vs mlx_lm34-36**. Strong dynamic-quant mechanism evidence; **no M1 numeric credit** until Apple7 measurement.
- **NEW TensorFold M1-M4 chunk exactness:** split prompts now bit-match one-piece attention at tested lengths; prior two 8192-key short-tail mismatches fixed. Add 8192-key boundaries to P69B13 certification.
- **NEW resident-agent capacity rule from TF #71:** physical M5 Pro64GB + 27B4bit+DFlash2 fits 140,288 one-shot tokens but can retain only ~96-100K conversation checkpoints (~6.1-6.3GiB). Above that, next turns re-prefill for 574-644s. One-shot window != resumable agent window. TARGETS updated so a resident 128K agent counts only when complete continuation state remains resumable.
- **NEW concurrent-prefill starvation from TF #72:** four independent ~16K cold prefills on one M5 Pro serialize and freeze earlier decode streams to ~1.0/1.5/2.8TG; last stream returns ~22.4TG. Strong evidence for 5070Ti cold-prefill -> Apple resident-decode division of labor or mandatory chunk interleaving.
- **UPDATE TensorFold SSD spill ships:** 35K evicted conversation restores in 0.27s vs75s on M5 Max/48GB budget, same reply. Parked-state tier only; active long-context KV residency target unchanged.
- **WATCH oMLX:** HC path is latency-bound with no retained bit-exact win (#4056); prefill transient predictor can overestimate large chunks 10-25x and shed ANE banks (#4057); tiny weight size does not guarantee context capacity (#4058).
- **Target effect:** no dual-M1/Strata numeric speed change. Strata penalty convention + resident-agent definition added to TARGETS.

### 2026-09-28 20:02 UTC Strata 0.1.20 / MoEspresso M1 / handoff frontier update

- **NEW Strata 0.1.20 shared-root checkpoint:** PR #62 pins the deepest common checkpoint and rotates later checkpoints LRU. RTX4070/IQ3_XXS new-chat test with 16,747-token system prefix: **14.898s -> 1.176s (12.7x)**; repeat 1.181s; answers token-identical. It is still one KV arena/one branch, so this is prefix reuse, **not physical simultaneous prefix sharing**. TARGETS now requires actual refcounted shared attention+recurrent+QSA state before common-prefix bytes count once across N resident agents.
- **NEW Strata PCIe-aware default:** PR #44 measures pinned H2D bandwidth and scales `pcie_frac`; RTX5060Ti PCIe4x8 measured **14.1GB/s** and default 0.55->0.30. Keep actual link bandwidth in scheduling provenance; no E2E target credit.
- **NEW Strata hit-rate telemetry:** PR #69 adds per-request decode expert hit rate. Record it with future 5070Ti TG receipts.
- **UPDATE Strata #57 Windows shared-core admission:** 23 MSVC admission tests pass on rebased shared-core helper; impossible allocations denied. Full Windows restore/agent validation still pending.
- **RECOVERED OLDER MoEspresso 3 physical M1 Flash receipt:** 2021 M1 Max 24-core/32GB, Flash-Next 128K, all 512 experts retained in package, 223 resident/layer, mostly IQ2_K routed experts with six IQ3_K groups, higher-precision dense tensors, BF16 PLE selected rows from SSD, KVarN K4/V4 attention state, no MTP sidecar. Physical grid **12.96-15.85 TG**, release cell **15.46 TG**. Cache-Prior 2/2 changes decode routing; small 48-question local score 84.3% vs hosted Qwen 90.7 under different effort/protocol. Strong Apple7 feasibility floor, **zero AA40 or dual-scaling numeric credit**.
- **NEW oMLX #4061:** on M5 Ultra fused Flash attention, rank-one masked QSA remains **3-8% faster with MTP** and **5-6% faster without MTP** at long context than the gathered path selected from 32K by an older M5-Max crossover; masked is also bit-exact. Make QSA plan threshold chip/kernel/context/S-specific. No M1 numeric credit.
- **NEW SGLang #41404 transfer ownership:** any transfer failure that may leave a writer in flight must defer decode KV/page release until all writers drain/ack or timeout. P51 destination import pages stay transaction-owned on failure; failure is not free permission.
- **NEW vLLM #58259 safe continuation frontier:** async resumable turns must resume from **computed - output_placeholders**, not optimistic computed frontier; old in-flight outputs are marked stale and drained. P51 exports/imports only materialized committed state and fences stale old-turn work.
- **NEW SGLang #41235 replay metadata:** replayed committed boundary token keeps original logprob and sampling-mask row; recomputation metadata is not substituted. Include token-decision metadata in continuation lineage where semantics depend on original sampling.
- **RECOVERED CURRENT vLLM #59054:** long-context speculative verify q_len>1 forced onto a low-parallelism 2D attention kernel caused 7-20x per-call slowdown; at 67K, spec serving 16.5TG vs 56.1 non-spec, small-q 3D path 33.7TG. Reinforces context×verify-width attention-plan certification; no Apple target credit.
- **Target effect:** no 40/400 or Strata numeric speed change. TARGETS changed only to distinguish logical prefix reuse from physical multi-agent state sharing.

### 2026-09-28 21:39 UTC CUDA->MLX bridge receipt / acceptance-semantics update

- **NEW TensorFold #77 direct heterogeneous-state receipt:** Qwen3.8-27B CUDA `conv`/fp32 recurrent `rec`/bf16 attention `kv` state maps 1:1 into MLX caches after batch/layout reshaping. ~64KiB/token +150MiB fixed (~1.9GiB @28K). At 28,227 tokens: CUDA FP8 fast prefill **1593 PP /40-of-64 continuation tokens equal**, K/V cosine min .850; CUDA BF16 **469 PP /55-of-64**, K/V .964, recurrent .997; Mac native **400 PP** and different chunk plans agree only 33/64. At 8,925 tokens FP8 import matches all 64 Mac-native tokens. **Bridge layout is feasible; long-prompt fast-prefill numerical drift is the main blocker.** Qualify 32K then96K/128K, within Mac chunk-control envelope, needles+agent replay, committed frontier only. Flash adds QSA/indexer/PLE/MTP state.
- **NEW mlx-serve #614 acceptance semantics:** prompt-lookup/copy drafts under typical acceptance caused agent loops because a point-mass proposal was treated like an MTP distribution. Controlled 12-sample typical-lookup arm had 2 loop-stops and distinct8 .653; exact lookup acceptance removed loop-stops while copy-heavy speed stayed ~240->239TG. P51 rule: acceptance is proposal-distribution-specific; prompt lookup, ngram, MTP, tree etc need valid independent acceptance semantics.
- **NEW vLLM #58784:** padded/unproposed draft rows were verified as token0 after PD resume, giving 71/80 NUL-prefixed sampled responses; explicit rejection fixes to0/80. Every P51 verify row needs validity/proposal mask; padding must be unaccept-able.
- **NEW vLLM #57107:** incidental scalar specialization made acceptance estimator compile 14/3/3 variants; no-specialize collapses each to1. Keep Apple verifier specialization small/frozen and shape-keyed; avoid runtime compile churn.
- **NEW TensorFold #76 M1 agent-loop watch:** no-thinking M1Max/27B+DFlash agent repeated successful repro probes; similar pattern appeared on MTPLX. Thinking-enabled follow-up solved task in13 model turns, 4/4 verifier checks pass. No TensorFold defect proven. Agent AA suite must cover thinking/sampling modes + no-progress guard.
- **NEW Strata #90:** Hermes requests 65,536 output tokens with 70,527-token prompt under131,072 context, correctly gets400 because prompt+reservation exceeds window. Orchestrator must use dynamic remaining-context output caps/compaction; no context-corruption evidence.
- **RECOVERED CURRENT DASLab IQ3_S SWE:** unpruned GSQ-RCO IQ3_S **82.0 SWE Verified vs82.8 BF16 (~99%)**. TARGETS quality prior IQ3_S AA>=40 rises **~75%->~80%**, still not AA certification. IQ3_XXS prior unchanged.
- **Speed target effect:** none. Dual-M1 Flash remains **40TG@128K /400PP /~70%**.
