# External Qwen runtime watch — 2026-08-31

This note records external runtime/quantization evidence relevant to the P51/P69 exact-Q8 verifier work and the separate Qwen3.8-Flash-Next dual-Mac research plan.

These are upstream PR descriptions and community field reports, not measurements produced by this repository. Do not turn them into local performance claims without reproduction.

## Executive delta

- Qwen3.8-27B Layr-Labs MTP challenge frontier remains `3.7291100105909`; no new promoted result changes the P69 direction.
- Qwen3.8-Flash-Next runtime evidence improved materially again, especially for long-context MTP, warm agent turns, M1-class hardware, and recurrent-state handling.
- The strongest new M1-specific field report shows a single M1 Max 64 GB running Flash-Next with SSD-streamed tensors/ngrams/MTP, custom sparse attention, and dynamic MTP at roughly 22 decode tok/s with MTP, while reporting roughly 150 prefill tok/s at 256K context.
- A separate exact-topology report now proves that 2x M1 Max 64 GB systems can run Flash-Next split over a point-to-point Thunderbolt 4 RPC link after a llama.cpp transient-buffer allocation bug was fixed. Throughput is still unreported.
- Fresh llama.cpp MTP measurements show that recurrent speculative rollback must stay device-resident: host-serializing the full recurrent checkpoint can dominate the round and turn high-acceptance MTP into a severe regression.
- This strengthens the case that the eventual dual-M1 Flash-Next bottleneck is implementation/distribution quality rather than an obvious single-node compute wall. Distributed MTP is still unmeasured on the exact two-M1 topology and remains the major uncertainty.

## Flash-Next: exact long-context MTP verification

Upstream oMLX PR #3320 (`perf(qwen4): flatten exact long-context MTP decode`) routes batch-one Qwen4 Lightning-MTP verify windows through bounded direct selected-block QSA above a measured crossover while preserving exact target verification.

Reported M3 Ultra 256 GB fixed-depth-5 results:

| Context | Decode-only |
|---:|---:|
| 10K | 85.6 tok/s |
| 50K | 74.4 tok/s |
| 100K | 71.8 tok/s |
| 150K | 70.9 tok/s |

The prior 150K path was about 59.4 tok/s, making the reported 150K improvement +19.3%. The direct-QSA verify path itself stayed near 71–73 tok/s from 20K through 150K, which is the important architectural result: verifier cost need not grow badly with context when the selected-block path is bounded correctly.

The same PR reports adaptive MTP at 220K around 53.15 tok/s with ~99% draft acceptance versus 26.37 tok/s MTP-off, with deterministic output-hash parity in its stated check.

Source: https://github.com/jundot/omlx/pull/3320

## Flash-Next: cached-drafter priming

Upstream oMLX PR #3328 (`perf(qwen4): prime verified MTP drafter from cached suffix`) addresses a warm-agent seam: the target backbone can restore a huge prefix while the memory-only MTP drafter lacks history.

Reported deterministic 100K restart case:

- 98,304 target prompt tokens restored from prefix cache;
- 1,668 exact suffix tokens used to prime the drafter;
- 97.6% draft acceptance;
- 5.32 committed tokens/target cycle;
- 60.35 tok/s decode;
- exact output hash matched the unmodified target result.

This is directly relevant to persistent-agent/Tameru-style compaction and restoration: large target-prefix reuse does not have to imply a long MTP cold-start penalty.

Source: https://github.com/jundot/omlx/pull/3328

## Flash-Next: latent Metal keepwarm for agent-turn gaps

Upstream oMLX PR #3330 (`perf(runtime): add opt-in latent Metal keepwarm`) adds a default-off bounded GPU pulse between cached turns. It does not mutate model weights, KV state, prompt state, sampling state, or SSD cache state.

Reported M3 Ultra 256 GB / Flash-Next oQ4e-MTP 220K agent-tool conversation results include:

- keepwarm OFF model TTFT after 5/15/60-second gaps: about 1.84 / 1.76 / 1.76 s;
- keepwarm ON repeated-turn model TTFT median: about 1.45 s;
- keepwarm ON after a 60-second gap: about 0.85 s model TTFT (visible-stream TTFT remained higher at 1.83 s in that run);
- B1 repeated decode median: 55.56 -> 58.79 tok/s;
- cold 4K prefill: 887.01 OFF vs 885.31 ON tok/s, effectively neutral;
- no cache repopulation after explicit hot/L0 clear in the stated validation.

This is not a throughput-transforming kernel change, but it is highly relevant to interactive coding-agent latency once cache restore and MTP priming are already good.

Source: https://github.com/jundot/omlx/pull/3330

## Flash-Next: M1 Max 64 GB field result

A fresh LocalLLaMA field report is unusually relevant because it is on the exact Apple generation/memory class of interest: M1 Max 64 GB.

Reported configuration:

- llama.cpp fork;
- SSD streaming for model tensors;
- SSD streaming for n-gram/PLE data;
- SSD streaming for MTP;
- custom Q4 quant assembled by tensor-level performance/quality selection;
- custom Metal sparse attention with near-linear context degradation;
- Q4_0 MTP reported to retain the same acceptance as the tested Q8_0 MTP at half the RAM;
- dynamic MTP draft sizing, including disabling speculation when context makes it negative.

Reported performance:

- ~180 tok/s 4K prefill without MTP;
- ~170 tok/s 4K prefill with MTP in the original note, with a later edit reporting ~185–190 tok/s after another optimization;
- ~150 tok/s prefill at 256K context;
- decode rising from ~12.9 to ~22 tok/s with MTP (~70% gain).

This is a community field report, not a controlled reproduction. Still, it is strong direct evidence that one M1 Max can run Flash-Next at useful full-context rates despite only 64 GB RAM by combining selective residency, SSD streaming, sparse attention, and MTP.

Source: https://www.reddit.com/r/LocalLLaMA/comments/1w296bx/qwen38flashnext_optimised_for_macs/
Fork: https://github.com/mihailescu2m/llama.cpp

## Flash-Next: exact 2x M1 Max / Thunderbolt RPC receipt

llama.cpp issue #27993 is the first public report matching the intended physical topology closely enough to retire a major feasibility question:

- 2x MacBook Pro M1 Max 64 GB;
- point-to-point Thunderbolt 4 bridge with static IPs;
- reported ~0.8 ms RTT;
- Flash-Next UD-IQ4_XS, 93.7 GiB;
- layer split through llama.cpp RPC using `-ts 1,1`;
- full model cannot fit on either 64 GB node alone.

The initial deployment deterministically collapsed to zero-token output above roughly 2K prompt tokens. That failure was not a recurrent-model or Thunderbolt limitation. llama.cpp PR #27960 fixed RPC transient-buffer under-allocation for operations including CUMSUM/ARGSORT/TOP_K. After rebuilding both machines, the reporter confirmed coherent 2.5K and 4K needle prompts and also confirmed that the earlier Q8-KV threshold disappeared.

The reporter then started a 115K-token needle at 256K context, but as of this checkpoint has not posted its result or any PP/TG throughput numbers.

Decision-level implication:

- distributed target execution on the exact hardware/network class is now functionally demonstrated;
- the receipt does **not** establish scaling efficiency or a two-node tok/s number;
- PP/layer ownership remains the preferred first topology because it minimizes cross-TB4 synchronization frequency;
- TP remains worth one controlled benchmark, but it is no longer the primary engineering plan.

Sources:
- https://github.com/ggml-org/llama.cpp/issues/27993
- https://github.com/ggml-org/llama.cpp/pull/27960

## Flash-Next: recurrent MTP rollback must stay on device

Two new llama.cpp PRs (#28104 and the isolated #28118) expose a decisive speculative-decoding systems cost for recurrent hybrids.

For Qwen3.8-Flash-Next, a speculative round may require a full recurrent-state checkpoint and rollback. The default server path serialized the recurrent state to host memory every round, including GDN conv/state rows, the four-stream residual state, and PLE history. On Strix Halo this cost was reported at roughly 600 ms of an ~825 ms round (~73%), overwhelming the benefit of high draft acceptance.

PR #28118 reports, on Strix Halo / Vulkan / Q4_K_M target with Q8 KV:

| Configuration | Decode | Acceptance |
|---|---:|---:|
| no draft | 32.4 tok/s | — |
| speculative, host checkpoint | 6.2 tok/s | 0.54 |
| speculative, device checkpoint, n-max 3 | 41.5 tok/s | 0.79 |
| speculative, device checkpoint, code, n-max 6 | 56.6 tok/s | 0.91 |

PR #28104 independently reports the same root cause in a fuller NextN/MTP port: host-backed checkpointing reduced short-context MTP to ~4.77 tok/s; requesting the existing on-device state path restored ~25.83 tok/s short-context and ~16.08 tok/s at 70K, versus target-only ~10.69 tok/s at 70K.

A maintainer follow-up suggests an even cleaner future design: provision multiple recurrent sequence-state slots (`n_rs_seq > 1`) so rollback can select an already-resident state rather than checkpointing the full recurrent state each round.

This has a direct dual-M1 design consequence: **each PP stage should own, checkpoint, and roll back its recurrent state locally**. Thunderbolt should carry activation rows and small draft/accept/commit metadata, not serialized recurrent snapshots. Treat any design that sends GDN state over TB4 or stages it through host memory every round as architecturally wrong until measurements prove otherwise.

Sources:
- https://github.com/ggml-org/llama.cpp/pull/28104
- https://github.com/ggml-org/llama.cpp/pull/28118

## Flash-Next: compiled multi-row decode / agent concurrency

oMLX PR #3334 (`feat(qwen4_exp): mx.compile batched decode for multi-row inference`) attacks the continuous-batching path rather than singleton MTP. It turns the changing cache offsets, rope positions, GDN recurrent state, and QSA cache/indexer state into explicit tensor leaves so an entire `(B,1)` Flash-Next forward can be captured with `mx.compile`.

Reported M3 Ultra / oQ4e / B=4, 2K context:

- host dispatch: 8.8 -> 2.0 ms (-77%);
- total step: 54.5 -> 44.4 ms (-18%);
- bit-exact against the eager path in the stated 2K/16K checks.

The HTTP A/B remained within run-to-run noise, so this should not be counted as an end-to-end gain yet. The important architectural result is that **multi-row Flash-Next decode can be compiled despite mutable recurrent/QSA state**.

For the dual-M1 plan, this reinforces continuous batching as a first-class optimization: several simultaneous coding-agent streams can fill PP bubbles while each node still owns its local layer/recurrent state. It also makes “3–5 agents” qualitatively different from one B1 stream; pipeline utilization can improve without introducing TP-style all-reduces inside every layer.

Source: https://github.com/jundot/omlx/pull/3334

## Flash-Next: avoid dead long-agent snapshot work

oMLX PR #3335 shows another recurrent-state tax that matters for persistent agent sessions. On reasoning-model requests, decode-time boundary snapshots beyond the cacheable prompt boundary could never be reused, yet the scheduler still extracted the full non-sliceable state and wrote an fp32 GDN sidecar (~111 MiB per event on Flash-Next) before discarding it.

Reported deterministic 9-turn agent session (~32K -> 47K context):

- 14 captures on stock;
- 7 decode-time captures were guaranteed dead;
- ~770 MiB of wasted GDN sidecar writes per session;
- patched path suppresses exactly those 7 while preserving the same cached-token sequence.

This is not a decode-throughput breakthrough, but it reinforces the cache policy rule: recurrent snapshots are expensive enough that capture/store decisions must be reuse-aware, not merely boundary-driven.

Source: https://github.com/jundot/omlx/pull/3335

## Flash-Next: GDN snapshot compression matters for hot-cache capacity

oMLX PR #3336 extends the GDN state codec to embedded/hot-cache block payloads. The PR estimates Flash-Next recurrent state at ~3.15 MB fp32 per GDN layer per 2048-token boundary, or ~113 MB of fp32 GDN state embedded per hot block across 36 GDN layers.

Reported hot-cache storage density:

| mode | hot bytes/token |
|---|---:|
| split / GDN sidecars on SSD | 27.9 KB |
| hot-only / embedded fp32 | ~85 KB |
| hot-only / embedded RHT-int16 | ~57 KB |

Reduced precision is explicitly not bit-exact and remains an opt-in quality/capacity tradeoff. For exact verifier work, keep fp32. For a practical long-running Flash-Next agent server, however, recurrent snapshot precision/placement is now clearly part of the memory-tier design rather than a minor cache detail.

Source: https://github.com/jundot/omlx/pull/3336

## Flash-Next: deep-context QSA and MTP throttling

MTPLX PR #413 reports three complementary long-context mechanisms on M5 Max 128 GB:

- multi-threadgroup QSA indexer scoring for S=1 decode;
- quantized pooled-key mirrors (q8/q4), reducing the stated pooled-key traffic from ~805 MB/step to ~200 MB/step in the q4 configuration;
- automatic MTP history-window cap at 16,384 tokens when context exceeds 262K, keeping speculative verification rounds bounded below ~5 ms.

Reported decode remains 43.55 tok/s at ~220K prompt tokens (262K rung) and 36.63 tok/s at the ~458K-token 546K rung, with 100% NIAH recall in the reported sweep. These are M5 numbers and do not transfer to M1, but the policy lesson is useful: **deep-context speculation should be context-adaptive, and QSA pooled-key bandwidth can be quantized separately from the model trunk**.

Source: https://github.com/youssofal/MTPLX/pull/413

## Flash-Next: quantization should be architecture/workload aware

Two independent lines now point the same way.

1. oMLX HOBBIT work (#3325) reports workload-profiled hot/cold expert precision allocation. The published PR data show meaningful decode gains for small perplexity penalties and also show that expert hotness changes substantially by workload/domain. That argues against a uniform-bit quant for an agent-specialized build.

2. Community Flash-Next quant work is converging on per-layer/tensor assignment rather than blanket bpw. A recent AP-GGUF release explicitly uses per-layer tailored quantization and reports 20–30 GB savings versus common Q4 builds at a similar perplexity band.

For our eventual build, the design implication is to preserve precision preferentially in architecture-sensitive regions and coding-agent-hot experts rather than spending bits uniformly. This is a research direction, not yet a local checkpoint.

Sources:
- https://github.com/jundot/omlx/pull/3325
- https://www.reddit.com/r/LocalLLaMA/comments/1w1ou8x/qwen38_flash_quants/

## Flash-Next: M1/M2 BF16 activation recast remains high priority

Upstream oMLX PR #3277 reports that M1/M2 hardware benefits from recasting BF16 non-quantized activation-side tensors to FP16 because BF16 arithmetic is emulated there.

Reported M1 Ultra / Flash-Next oQ4e-MTP results:

- rewrite decode: 28.29 -> 32.26 tok/s (+14.0%);
- novel decode: 22.89 -> 24.07 tok/s (+5.2%);
- prefill: 313.2 -> 500.2 tok/s (+59.7%).

This is particularly relevant to M1 Max reproduction. It should be isolated as its own A/B before combining it with distributed inference or new quantization.

Source: https://github.com/jundot/omlx/pull/3277

## Qwen3.8-27B external state

The Layr-Labs `qwen-3.8-mtp-challenge` frontier remains:

`3.7291100105909`

The newest visible candidate (#1481) is an unmeasured compiled-elementwise-fusion proposal without an Apple-Silicon local timing receipt. There is no newly promoted external result that should change the P69B13 selection or reopen closed verifier seams.

Source: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1481

A separate quantization development is worth cataloging but does not alter the exact-Q8 verifier campaign: GSQ+RCO 2.5–3.0 bpw GGUFs use learned scalar grids plus per-tensor constrained precision assignment. The architecture-level lesson again supports non-uniform bit allocation for future compact deployments.

Source: https://www.reddit.com/r/LocalLLaMA/comments/1w13vse/release_sota_ggufs_for_qwen3827b_gsqrco_at_25_to/

## Decision impact

### P69 / 27B exact-Q8 verifier

No change.

- Keep the P69B12 promoted stack and exact-Q8 ruler intact.
- Continue to P69B13 from existing profiling/census data.
- Do not reopen the explicitly closed P69B8/P69B9/P69B10-C seams on the basis of external challenge submissions.

### Flash-Next dual-M1 research

The preferred topology is now **PP2 first**, with TP2 retained only as a measured control unless it produces a surprising result.

Evidence priority now looks like:

1. reproduce the single-M1 Max 64 GB baseline with MTP + selective SSD residency;
2. isolate the M1/M2 FP16-activation recast;
3. reproduce the exact 2x M1 Max / TB4 target-only RPC path and record PP/TG/RTT under the same quant;
4. keep recurrent checkpoints/rollback device-local on each stage; do not serialize GDN state across TB4;
5. establish PP target-only scaling and state ownership before adding native distributed MTP;
6. bring up PP + context/ngram wide verification as the lower-risk speculative path;
7. add native MTP with coarse-grained stage handoff and acceptance/rollback metadata only;
8. port/bound direct-QSA verify so long-context speculation does not inherit general-mask scaling;
9. test continuous-batching / multi-agent PP utilization once single-stream correctness is stable;
10. profile coding-agent expert/tensor hotness before choosing a final mixed-precision quant;
11. add cached-drafter priming and optional GPU keepwarm only after cache/distributed correctness is stable.

The new dual-M1 receipt retires “can Flash-Next execute across two M1 Max machines over TB4?” as a primary feasibility risk. The remaining question is **performance scaling**, especially whether distributed MTP can turn PP's otherwise sequential B1 stages into a useful overlapped verification pipeline.

The on-device checkpoint findings sharpen that further: TB4 bandwidth is not the obvious MTP blocker if state ownership is designed correctly. The likely failure mode is excessive synchronization or host/state movement, not the activation payload itself.

None of the current external evidence establishes a two-node 40+ tok/s result. That remains a target, not a measured claim.