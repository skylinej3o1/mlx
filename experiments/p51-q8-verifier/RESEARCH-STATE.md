# Canonical Runtime / Architecture Research State

Last consolidated: 2026-09-02 00:08 ET.

Purpose: durable baseline for every future Qwen3.8-Flash-Next, Qwen3.8-27B, and
DeepSeek-V4-Flash/DS4 external research pass. Dated `RESEARCH-WATCH-*` files are deltas;
this file carries forward the facts and decisions that must not be rediscovered or
silently dropped.

## Required research-pass protocol

Before any new search:

1. Read this file first.
2. Read `RESEARCH-WATCH-LATEST.md`.
3. Read every dated watch newer than this file's consolidation point.
4. Classify each hit as **KNOWN**, **UPDATE**, **NEW**, or **RECOVERED OLDER EVIDENCE**.
5. Never call an old source new merely because it was absent from a later note.
6. After a useful pass, update the dated delta, this state when a durable conclusion
   changes, and `RESEARCH-WATCH-LATEST.md`.

This protocol was added after DS4 issue #607 was rediscovered on 2026-09-01 even though
it had already been found and used in the project on 2026-08-01.

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

This predates the 0731 checkpoint. It is a topology/economics anchor, not a 0731 result.
Plain serial layer PP on the exact M1-Max/TB4 hardware class is a low-teens dependent-chain
decode system, not a near-2x multiplier.

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
fixed deterministic all-zero output beyond roughly 2K prompt length. 2.5K/4K and q8 KV
runs then became coherent. No sustained TG has been published.

Distributed recurrent/QSA correctness is a mandatory bring-up gate before throughput.

## Durable single-M1 Flash-Next calibration

Reproducible M1 Max 64 GB custom llama.cpp work currently anchors the hardware class:

- target-only ~10.9 tok/s @4K, ~10.0 @32K, ~9.2 @64K, ~8.0 @128K
- native MTP ~17.6 tok/s @4K and ~13 tok/s @128K in the reproducible sweep
- later tuned same-author configuration around 12.9 target-only / ~22 MTP
- prefill roughly 150-180+ tok/s depending on context/configuration

Flash-Next's sparse PLE/n-gram table is a much better SSD-offload candidate than routed
experts: tiny indexed reads can be cheap while expert streaming repeatedly touches much
larger weight volumes.

## Established Flash-Next optimization seams

Future passes should look for status/performance updates rather than rediscover these:

- exact/direct QSA scoring and deterministic selection
- gathered/selected-KV sparse attention instead of full-context masked attention
- QSA/indexer top-k acceleration
- resident PLE / GDN / hyperconnection projections
- MTP prompt-history sidecar / warm-prefix restoration
- recurrent speculative checkpoints kept on-device
- context-adaptive verify width/depth
- compiled multi-row decode and reduced host dispatch
- n-gram-history self-speculation for repeated code/agent workloads
- exact resident prefix/cache reuse
- per-projection mixed quantization as a separate lossy capacity track
- stage-local recurrent state under PP; avoid chatty TB4 collectives
- continuous-batching QSA state must be explicitly per-row

## Long-context QSA evidence

### llama.cpp #28213 — gathered selected-K/V decode

Source: https://github.com/ggml-org/llama.cpp/pull/28213

Dual A6000, IQ4_XS, q8 KV, temp 0:

- 31K: 36.5 -> 38.5 tok/s (+6%)
- 62K: 26.5 -> 31.6 tok/s (+19%)
- 130K: 15.7 -> 23.6 tok/s (+50%)

At 130K it also removes roughly 17 MB of attention-mask upload per token. Not Apple
evidence, but strong architecture evidence that selected-KV gather is the correct
long-context shape.

### oMLX #3320 — direct-QSA wide-MTP evidence is under requalification

Source: https://github.com/jundot/omlx/pull/3320

A later low-margin workload exposed a parity failure in the prior fast wide-verifier
evidence. The PR remains draft until the exact 10K-220K output-hash/cache-state/selector/
prefill/decode gates are refreshed. Preserve the architecture signal, but do not overweight
its most aggressive throughput numbers until requalified.

## Flash-Next continuous batching — current state

### NEW #3368 — per-row QSA indexer past length

Source: https://github.com/jundot/omlx/pull/3368

At B>1 `BatchQSAKVCache.offset` is per-row, but the QSA indexer treated it as a scalar,
causing wrong axis broadcasting and batch-formation crashes. The fix builds true
`[batch, seq_len]` per-row state and preserves B1 numerics; 14 tests verify selected-mask
contents.

Practical implication: current upstream Qwen4-exp continuous batching was not generally
safe merely by setting `max_concurrent_requests >= 2`. This fix is foundational, not yet a
throughput receipt.

### NEW #3369 — BatchQSAKVCache join rank/length correctness

Source: https://github.com/jundot/omlx/pull/3369

Follow-up fixes make rank-2 text and rank-3 MRoPE/image position joins promote to the
widest rank and stop conflating KV offset with indexer length. This removes both crash and
silent-mis-slice classes in B>1 joins. Again: correctness foundation, no throughput claim.

### RECOVERED #3265 — batched depth-1 MTP is silicon/economics sensitive

Source: https://github.com/jundot/omlx/pull/3265

Opt-in depth-1 always-advance MTP across a multi-row batch reports on M3 Ultra:

- batched acceptance ~56% vs ~61% single-stream
- four concurrent requests roughly +70-90% aggregate vs plain batching in the reported
  setup

But an independent **M1 Ultra** run is directly relevant to our M1-generation plan:

- 8 concurrent
- 580 cycles
- acceptance 52.4%, zero fallbacks
- batched MTP 38.50 / 36.03 tok/s
- plain-batched baseline 57.09 tok/s
- draft-head work ~12,226 ms vs verifier ~10,196 ms

The draft head cost approximately as much as verification, so MTP was net-negative despite
reasonable acceptance. Do not make MTP mandatory under concurrency on M1 Max.

## Distributed concurrency evidence

### oMLX Cluster v2 #3118 — stronger-hardware architecture calibration

Source: https://github.com/jundot/omlx/pull/3118

Physical pair is **M3 Ultra 256 GB + M5 Max 128 GB / TB5 JACCL-RDMA**, measured around
6.1-6.5 GB/s and 27-31 us. Absolute numbers must not be transferred to M1 Max/TB4.

DeepSeek-V4 TP2 evidence:

- cold prefill ~732.49 tok/s @30K, ~684.66 @100K
- non-MTP B1 decode ~29-31 tok/s
- non-MTP aggregate B1/B2/B4 ~31.22 / 47.35 / 75.22 tok/s
- fixed-depth-5 high-acceptance MTP ~79.8-80.6 tok/s raw

The most transferable result is the final concurrency policy. Until true N x M speculative
verification exists, the implementation caps the MTP lane to one and queues/arbitrates
concurrent work around it. Cached physical aggregate wall rates are approximately:

- B1 75.1 tok/s
- B2 75.2 tok/s
- B4 73.1 tok/s

The PR explicitly calls this **serialized throughput arbitration, not simultaneous batched
MTP scaling**.

Qwen3.8-27B Phase-split evidence in the same branch:

- 9,410-token cold prefill compute ~991.36 tok/s
- decode ~29.59 tok/s
- cache handoff 7.34 GB/s
- exact-prefix wall 12.31 s -> 1.40 s
- B4 queued throughput ~1.29x sequential stage time

Single-node donor-head Lightning MTP works, but Qwen TP2 MTP physically stalled at the
first `return_hidden`/rollback graph and was reverted/fail-closed. Distributed target
execution and distributed speculative lifecycle are separate qualification problems.

### DS4 #861 — distributed batched-serving L0

Source: https://github.com/antirez/ds4/pull/861

Known Strix-Halo topology result remains: layer-split pipeline ~222 tok/s average prefill /
260 peak and 13.6 tok/s decode, while TP is link/RTT-heavy. Current update adds a shared
worker registry for `--batched-session N` and multiplexed session/request IDs, but decode
remains serialized and coalescing/mixed-prefill are disabled until row-batched spans land.

Correct multi-session distributed serving is advancing; true distributed batched throughput
is still a separate milestone.

## M1 Max 27B ordinary-batching feasibility anchors

Recovered existing oMLX benchmark records show that M1 Max itself can expose useful
aggregate target-batching headroom, but results are highly configuration-sensitive.
Observed B1/B2/B4 rows include examples around:

- 18.9 / 22.0 / 44.9 tok/s
- 18.1 / 31.0 / 63.8 tok/s
- 16.2 / 26.4 / 45.1 tok/s
- 15.5 / 31.9 / 61.7 tok/s

Another M1 Max 64 GB record showed only ~19.0 / 22.3 / 23.7. Durable conclusion:
plain multi-row execution can scale significantly on M1 Max, but the multiplier is runtime,
model, and configuration sensitive. These 27B records are not direct Flash-Next proof.

## Qwen3.8-27B external exact frontier

Layr challenge remains unchanged as of this consolidation:

- best score `3.7291100105909`
- #1481 newest visible submission
- no newer promoted exact result

No external result changes P69B13 selection.

## Current dual-M1 Flash-Next planning ladder

These are engineering planning probabilities, not statistical confidence intervals.
Assumptions: mature 2x M1 Max 64 GB / TB4, short-to-medium B1 coding/agent workload,
best single-node kernels first, recurrent state kept local, and PP overlap used where it
actually pays.

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

### Mature B2-B4 aggregate — trimmed after concurrency evidence

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

Reason for trim: previous aggregate forecasts blended plain batching, speculative batching,
and singleton-lane speculative arbitration. #3368/#3369 show Flash-Next B>1 correctness is
only now being repaired, #3265 shows batched MTP can lose badly on M1-generation silicon,
and #3118 shows a mature distributed system may intentionally serialize the profitable
MTP lane instead of speculating every concurrent row.

The outlook remains favorable because ordinary M1 Max batching can scale and independent
requests can fill otherwise idle pipeline work. The adjustment means **concurrency is a
scheduler/topology optimization, not an automatic MTP multiplier**.

## Current topology / serving decision

- **PP2 remains primary** for the dual-M1 Flash-Next experiment.
- **TP2 remains a falsification/control benchmark.**
- First prove single-M1 and PP2 target-only correctness/performance.
- Then benchmark B2/B4 plain target batching separately from MTP.
- Under load, prefer the best measured policy among:
  1. plain multi-row target batching;
  2. singleton profitable MTP lane plus queued/arbitrated independent work;
  3. batched depth-1 MTP;
  4. context/acceptance-driven dynamic MTP disable.

Do not assume "MTP everywhere" is optimal on M1 Max.

## Bring-up invariants / highest-value missing measurements

- internal NVMe for long-lived model/vocab mappings
- explicit TB4 TSO check
- background-memory audit
- deep-context needle/correctness before speed
- single-M1 target-only + MTP baselines first
- PP2 target-only before PP2+MTP
- B1/B2/B4/B6 ladder
- stage-local recurrent/GDN rollback state
- separate resident-session count from active decode
- record acceptance, committed tokens/cycle, stage idle %, and actual TB4 bytes/round

Highest-value missing measurements now are:

1. exact Flash-Next 2x M1 Max/TB4 target-only B1 TG;
2. exact Flash-Next 2x M1 Max/TB4 MTP B1 TG;
3. single-M1 Flash-Next B2/B4 plain batching after #3368/#3369;
4. M1 Max plain batching vs singleton-MTP-lane vs batched-depth-1 MTP;
5. PP2 B2/B4 aggregate with stage-idle % and actual TB4 traffic.
