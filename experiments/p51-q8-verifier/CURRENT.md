# P51 verifier current checkpoint

## Promoted verifier lineage

The complete promoted verifier stack is now:

- P58 FP16 GDN fused verifier prework;
- P61 HEADPAIR HPT2 SDPA;
- P69B3 SG2R4 Q8 M4 shared-weight projection;
- P69B6 DUAL64 verifier MLP fusion;
- P69B11 asymmetric GDN QKV(KP2)+Z(KP1) projection bundle;
- fixed D3 / verifier M4.

The canonical validator must pass all Git, both compiled MLX ABI, and
Homebrew oMLX Python-patch domains before further tuning.

### P69B11 certification

P69B11 bundles the two GDN projections sharing the same FP16 verifier input:

- QKV: M4 K5120 N10240 Q8 GS64, KP2;
- Z: M4 K5120 N6144 Q8 GS64, KP1.

It preserves independent QKV and Z arithmetic/reduction orders and separate
FP16 projection output boundaries. It does not use a homogeneous N16384 QMM.

P69B11-B2 isolated exactness:

- QKV bit-exact: PASS;
- Z bit-exact: PASS;
- frozen Metal source SHA256:
  `e11dd85965c264cdd9b415348d0c2bd9d19ae2cfd20ce1a7ad1654d740bc8508`.

P69B11-B3 2+2 scout:

- mean saving: +2.228494624 ms/cycle;
- TG: +1.4598%;
- pair wins: 2/2.

P69B11-B4 balanced 4+4 certification:

- BASE mean BPC: 147.508870968 ms/cycle;
- CAND mean BPC: 145.100268817 ms/cycle;
- mean saving: +2.408602151 ms/cycle (+1.6329%);
- median saving: +2.750000000 ms/cycle;
- BASE mean TG: 17.888097 tok/s;
- CAND mean TG: 18.157695 tok/s;
- TG improvement: +1.5071%;
- pair wins: 4/4;
- all four CAND actual-weight exactness gates: PASS;
- all eight output hashes: `101ae2aec9793dfe`;
- all eight trajectories: 186 cycles / 325/442 / 155/101/69.

B4 certification summary SHA256:

`0a1153be3f7e4d0643da29abae923a15298fb393fe8fe7b7bcb611f4e934b39d`

Verdict:

**P69B11 CERTIFIED AND PROMOTED.**

### Runtime gate

P69B11 is runtime-gated by:

`OMLX_VERIFY_GDN_QKVZ_DUAL=1`

The permanent validator/restorer track the packaged P69B11 module and exact
embedded Metal source fingerprint.

## Closed work

Do not reopen:

- P69B5 verifier-QMM staging/synchronization;
- P69B6-D residual ADD->RMS fusion;
- P69B8 RMSNormGated fusion;
- P69B9 attention-gate final epilogue;
- P69B10-C recurrent final-state alias.

Do not rerun P69B7 profiling.

## Next work

**P69B12 — choose the next remaining high-leverage verifier seam using the
existing P69B7/P69B10 measurements. Do not rerun profiling.**

Start from the now-promoted P58/P61/P69B3/P69B6/P69B11 stack.

## P69B11 packaging repair

B4 remains certified. A permanent promotion-packaging defect stripped
four runtime state assignments from the packaged module and caused the
dense VLM runtime patch to raise during startup, triggering LLM
fallback.

The durable patch, promoter, restorer, and validator now preserve and
verify the certified runtime state.

Immediate next step: absolute frozen 29,297-token champion measurement.

## Current absolute champion — P69B11

The permanent P58/P61/P69B3/P69B6/P69B11 D3/M4 stack is now the
measured ~30K champion.

Frozen 29,297-token result:

- **19.555088 tok/s**
- **137.827957 ms/cycle**
- 186 cycles
- 325/442 acceptance
- d1/d2/d3 = 155/101/69
- hash `101ae2aec9793dfe`

All promoted components engaged and the post-run canonical validator
passed.

**Next:** P69B12. Use existing profiling/census data; do not reopen
P69B7, P69B8, P69B9, P69B10-C, or P69B11 certification.

## Promoted checkpoint after P69B12 certification

P69B12 is certified and queued for permanent restore on top of P69B11.

Promoted stack after restore:
1. P58 FP16 GDN verifier prework
2. P61 HPT2 HEADPAIR SDPA
3. P69B3 SG2R4 Q8 M4 projection
4. P69B6 DUAL64 verifier MLP
5. P69B11 QKV(KP2)+Z(KP1) bundle
6. P69B12 B/A idle-SIMD piggyback
7. fixed D3 / verifier M4

P69B12 4+4 certification:
- +0.417204301 ms/cycle mean
- +0.401612903 ms/cycle median
- +0.2112% TG
- 3/4 pair wins
- all exactness/hash/trajectory checks PASS

Runtime gates:
OMLX_VERIFY_GDN_QKVZ_DUAL=1
OMLX_VERIFY_GDN_BA_PIGGYBACK=1

Immediate next step:
commit/push this promotion checkpoint, run the updated canonical restorer,
then perform one absolute frozen 29,297-token permanent-stack measurement.

## P69B12 absolute result

Permanent P69B12 absolute ruler:
- 19.551316818 tok/s
- 137.820430108 ms/cycle
- 186 cycles
- 325/442
- depths 155/101/69
- hash 101ae2aec9793dfe

P69B11 prior absolute:
- 19.555088384 tok/s
- 137.827956989 ms/cycle

The two absolute runs are effectively tied:
- P69B12 TG delta: -0.0193%
- P69B12 BPC saving: +0.007527 ms/cycle

P69B12 remains promoted because its balanced 4+4 paired certification is the
stronger causal measurement (+0.417204301 ms/cycle mean, 3/4 wins).

Do not label P69B12 a new raw absolute TG record. P69B11 retains that single
number by 0.003772 tok/s, a noise-scale margin.

Current live/promoted stack remains P58/P61/P69B3/P69B6/P69B11/P69B12 D3/M4.

Next: P69B13 using existing profiling data only.

## External runtime watch — 2026-08-31

A fresh Qwen3.8-27B / Qwen3.8-Flash-Next external sweep is recorded in:

`experiments/p51-q8-verifier/RESEARCH-WATCH-2026-08-31.md`

Key decision-level deltas:

- Layr-Labs 27B MTP frontier remains `3.7291100105909`; no new promotion changes P69B13 selection.
- oMLX direct-QSA long-context MTP, cached-drafter priming, latent-Metal keepwarm, and compiled multi-row decode strengthen the long-agent Flash-Next path.
- A single M1 Max 64 GB field report reaches roughly 22 decode tok/s with MTP and reports roughly 150 prefill tok/s at 256K using SSD-streamed tensors/ngrams/MTP plus custom sparse attention.
- An exact 2x M1 Max 64 GB / point-to-point TB4 llama.cpp RPC deployment now works coherently after RPC buffer-allocation PR #27960; no throughput or completed deep-context result has been posted yet.
- New llama.cpp measurements show host-backed recurrent speculative checkpoints can consume ~73% of a round; keeping rollback checkpoints on-device changes MTP from a severe regression to a real speedup. Distributed design should therefore keep GDN/recurrent rollback state local to each PP stage and send only activation/acceptance metadata across TB4.
- PP2 is now the preferred dual-M1 topology. TP2 remains a controlled benchmark rather than the primary plan because frequent cross-TB4 collectives are a poor fit for Flash-Next's light/stateful per-layer work.
- M1/M2 FP16 activation recast remains a high-priority isolated A/B before distributed-MTP tuning.
- Mixed/per-layer or workload-aware quantization is increasingly favored over a uniform-bit Flash-Next quant.

These external results do **not** modify the certified P69B12 exact-Q8 ruler.

Current verifier next step remains **P69B13 using existing profiling data only**.