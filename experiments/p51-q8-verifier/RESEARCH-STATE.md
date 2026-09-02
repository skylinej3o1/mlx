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
