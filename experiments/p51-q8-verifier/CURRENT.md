# P51 verifier current checkpoint

## Promoted champion after P69B11

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
