# Canonical Runtime / Architecture Research State

Last consolidated: 2026-09-01 20:30 ET.

Purpose: this file is the durable baseline for all future external research passes.
Dated `RESEARCH-WATCH-*` files are deltas; this file carries forward the facts that
must not be rediscovered or accidentally reclassified as new.

## Required research-pass protocol

Before any new Qwen3.8-27B / Qwen3.8-Flash-Next / DeepSeek-V4-Flash search:

1. Read this file first.
2. Read `RESEARCH-WATCH-LATEST.md`.
3. Read every dated `RESEARCH-WATCH-*` delta newer than this file's last consolidation.
4. Classify each external hit as one of:
   - **KNOWN** — already in the canonical state or an earlier project discussion;
   - **UPDATE** — same source/idea, but materially newer data or status;
   - **NEW** — genuinely new source/architecture/result.
5. Never call an old source "new" merely because it was missing from a later dated note.
6. After a useful pass, update the dated delta, this canonical state when a durable
   decision changes, and `RESEARCH-WATCH-LATEST.md`.

This protocol exists because the 2026-09-01 Night pass rediscovered DS4 issue #607,
which had already been found and used as an empirical anchor in the project on
2026-08-01, but had not been carried into the later formal `RESEARCH-WATCH-*` files.
`RESEARCH-WATCH-LATEST.md` was also stale and pointed only through Early Evening.

## Certified 27B verifier state — separate from external research

External research does **not** change the exact-Q8 P69 certification state.

Current promoted verifier stack:

- P58 FP16 GDN verifier prework
- P61 HPT2 HEADPAIR SDPA
- P69B3 SG2R4 Q8 M4 projection
- P69B6 DUAL64 verifier MLP
- P69B11 QKV(KP2)+Z(KP1) bundle
- P69B12 B/A idle-SIMD piggyback
- fixed D3 / verifier M4

Current absolute ruler remains effectively the P69B11/P69B12 tie near 19.55 tok/s
at the frozen 29,297-token ruler.

**Next exact-verifier work remains P69B13 using existing profiling data only.**
Do not rerun P69B7 profiling or reopen closed P69B8/P69B9/P69B10-C/P69B12 work.

## Durable exact-hardware anchors — 2x M1 Max 64 GB / Thunderbolt 4

### KNOWN since 2026-08-01 — DS4 issue #607, pre-0731

Source: https://github.com/antirez/ds4/issues/607

This was one of the project's earliest direct dual-M1 calibration points. It is
**historical known context, not a 2026-09-01 discovery**.

Hardware/topology:

- 2x MacBook Pro M1 Max 64 GB
- direct Thunderbolt 4
- layer/pipeline split 0:23 / 24:output
- fully resident `q2-q4-imatrix`
- context 65,536
- 32-bit distributed activations

Measured:

- long-document decode: 10.03 / 10.07 tok/s
- code decode: 11.00-12.95 tok/s
- long-prompt prefill: 153.7-162.7 tok/s

Interpretation:

- this predates the 0731 checkpoint and must not be quoted as 0731 performance;
- it is the strongest direct historical anchor for **plain serial layer-split
  economics** on the exact M1-Max/TB4 hardware class;
- plain PP/layer splitting by itself does not produce a near-2x dependent B1 decode
  multiplier.

### KNOWN — DS4 issue #922, exact 0731 long-context receipt

Source: https://github.com/antirez/ds4/issues/922

Hardware/topology:

- 2x M1 Max 64 GB / TB4
- DeepSeek-V4-Flash-0731 DS4-Quality128, 95.76 GiB
- layers 0:22 / 23:output
- 8-bit distributed activations
- ctx allocation 262,144

Measured/confirmed:

- 34,384-token distributed prefill: ~152 tok/s, ~225 s
- 51K CLI prompt works
- after moving the model mmap from external USB SSD to internal NVMe,
  34K prefill + generation completed successfully
- TSO=0 and removal of a large background-memory consumer mattered to stability

Still missing:

- generated-token count
- sustained decode TG

The 257-second end-to-end completion after the storage fix cannot be converted into
TG. Rechecked 2026-09-01 20:30 ET: no newer comment supplies it.

### KNOWN — exact dual-M1 Flash-Next RPC correctness

Source: https://github.com/ggml-org/llama.cpp/issues/27993

Exact 2x M1 Max 64 GB / point-to-point TB4 with Qwen3.8-Flash-Next UD-IQ4_XS.
PR #27960 fixed an RPC allocation/state bug that caused deterministic all-zero output
past ~2K prompt length. 2.5K/4K and q8 KV tests then passed; a 115K/256K needle run
was started. No sustained TG has been published in that issue.

Interpretation: distributed recurrent/QSA correctness is a mandatory bring-up gate
before throughput claims.

## Durable single-M1 Flash-Next anchors

### Reproducible M1 Max 64 GB custom llama.cpp sweep

Known current calibration:

- target-only ~10.9 tok/s at 4K, ~10.0 at 32K, ~9.2 at 64K, ~8.0 at 128K
- native MTP ~17.6 tok/s at 4K and ~13 tok/s at 128K in the reproducible sweep
- later tuned configuration from the same author reaches roughly 12.9 target-only
  and ~22 tok/s with MTP
- prefill roughly 150-180+ tok/s depending on context/configuration

This is the most relevant direct single-node calibration for a 400-GB/s M1 Max.

### Storage asymmetry

Flash-Next's sparse n-gram/PLE table is a much better SSD-offload candidate than
routed experts: tiny indexed PLE reads can be serviced efficiently while expert
streaming touches much larger recurring weight volumes. PLE direct-read/concurrent
pread work in llama.cpp/oMLX reinforces this distinction.

## Flash-Next architecture seams already established

These are known directions; future search passes should look for status/performance
updates rather than rediscovering the ideas.

- exact/direct QSA scoring and deterministic block selection
- gather/selected-KV sparse attention rather than full-context masked attention
- QSA/indexer top-k acceleration
- resident PLE / GDN / hyperconnection projections
- MTP head/history warm-prefix restoration
- recurrent speculative checkpoints kept on-device
- context-adaptive verify width/depth
- compiled multi-row decode / host-dispatch reduction
- n-gram history speculation for repeated agent/code workloads
- exact resident prefix/cache reuse for agent turns
- per-projection / workload-aware mixed quantization as a separate lossy capacity track
- stage-local recurrent state for distributed PP; avoid chatty cross-TB4 collectives

## Freshly consolidated 2026-09-01 late-evening deltas

### UPDATE — llama.cpp PR #28213: gather-based QSA decode

Source: https://github.com/ggml-org/llama.cpp/pull/28213

A newer qwen4exp implementation gathers only indexer-selected K/V instead of applying
a sparse mask over the full KV history.

Dual RTX A6000, IQ4_XS, q8 KV, temp 0:

- 31K: 36.5 -> 38.5 tok/s (+6%)
- 62K: 26.5 -> 31.6 tok/s (+19%)
- 130K: 15.7 -> 23.6 tok/s (+50%)

At 130K it also avoids roughly 17 MB of attention-mask upload per token.
This is not an Apple result, but it strongly confirms that **selected-KV gather** is
one of the highest-leverage long-context Flash-Next seams.

### UPDATE / caution — oMLX PR #3320 requalification

Source: https://github.com/jundot/omlx/pull/3320

The long-context direct-QSA MTP PR now explicitly remains draft for a technical
requalification gate because a later low-margin workload exposed a parity failure in
the prior fast wide-verifier evidence. The unqualified experimental path is not being
promoted until exact 10K-220K output-hash/cache-state/selector/prefill/decode gates
pass again.

The reported high-acceptance M3 Ultra results remain valuable architectural evidence,
but aggressive throughput extrapolations should carry less weight until requalified.

### UPDATE — oMLX PRs #3364/#3365: 27B ANE long-prefill admission repair

Qwen3.8-27B oQ4e-mtp could reject long prefill because ANE-bank transient reserve and
retry escalation were stale/misclassified. The repaired source path completes a
65,536-token context benchmark at roughly 397 tok/s where the captured v0.6.4 path
rejected at 4,096 tokens.

This is a serving/memory-admission improvement, not an exact-P69 decode result.

### UPDATE — Layr exact 27B frontier unchanged

Rechecked 2026-09-01 20:30 ET:

- best score: 3.7291100105909
- #1481 newest visible submission
- no #1482+ promoted result

## Current dual-M1 Flash-Next target ladder

These are **engineering planning probabilities**, not statistical confidence intervals.
They assume a mature 2x M1 Max 64 GB / TB4 stack, batch-one coding/agent workload,
roughly short-to-medium active context (about 4K-32K), best available single-node
Flash-Next kernels first, MTP enabled, recurrent state kept local, and PP overlap used
where it actually pays.

| Mature B1 target | Current confidence | Interpretation |
|---|---:|---|
| >=30 tok/s | ~90% | base success target |
| >=35 tok/s | ~75-80% | strong target |
| >=40 tok/s | ~55-60% | stretch, still plausible |
| >=45 tok/s | ~30-35% | aggressive |
| >=50 tok/s | ~15% | upside case, not planning baseline |

Change from the Early-Evening ladder: the >=40 and >=45 bands are trimmed slightly.
The new QSA-gather evidence is positive, but oMLX #3320's requalification warning means
we should not overweight the most aggressive long-context MTP numbers until they pass
again. The exact dual-M1 Flash-Next TG is still missing, so no large forecast move is
justified.

### Long-context B1 planning band (~128K active context)

| Mature B1 target | Current confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

The direct-QSA gather results support meaningful long-context upside, but the exact M1
calibration still falls from ~17.6 at 4K toward ~13 at 128K on one streamed node.

### Multi-agent aggregate throughput

Independent requests can fill otherwise idle PP stages, so aggregate throughput has a
stronger outlook than a single dependent decode chain. For a mature B2-B4 server:

| Aggregate target | Current confidence |
|---|---:|
| >=50 tok/s | ~90% |
| >=60 tok/s | ~80% |
| >=70 tok/s | ~65% |
| >=80 tok/s | ~45% |
| >=90 tok/s | ~25% |

The key validation ladder remains B1 -> B2 -> B4 -> B6 with per-agent throughput,
aggregate throughput, stage idle time, MTP acceptance/tokens-per-cycle, and TB4 traffic
recorded separately.

## Current topology decision

- **PP2 remains primary** for the dual-M1 Flash-Next project.
- **TP2 remains a falsification/control benchmark**, not the default plan.
- Plain layer PP should be expected to resemble the old DS4 low-teens dependent-chain
  behavior unless MTP/overlap creates useful pipeline work.
- Multi-agent service is the strongest opportunity because independent requests create
  pipeline depth that B1 inherently lacks.

## Bring-up invariants

For the eventual two-M1 benchmark:

- internal NVMe for long-lived mapped model/vocab files
- explicit TB4 TSO check
- quiet/background-memory audit
- deep-context needle/correctness test before speed testing
- single-M1 target-only + MTP baselines first
- PP2 target-only before PP2+MTP
- B1/B2/B4/B6 ladder
- per-stage recurrent/GDN rollback state remains local
- separate resident-session count from active-decode concurrency
- record acceptance, committed tokens/cycle, stage idle %, and actual TB4 bytes/round
