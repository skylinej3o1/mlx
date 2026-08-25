# P51 verifier current checkpoint

This file is the compact current-state handoff for `project51-q8-verifier`.
Read it together with `STATUS.md`, `TERMINAL-BOOTSTRAP.md`, and
`RUNTIME-STATE.md`.

## Git/runtime checkpoint before P69B11-B4

Canonical runtime hardening is complete. The strengthened validator checks:

1. local/fork Git state;
2. promoted MLX source markers;
3. Python-3.14 venv compiled MLX host + metallib markers;
4. Python-3.11 oMLX-owned compiled MLX host + metallib markers;
5. Homebrew oMLX Python-side P58/P69B6 patches.

The actual oMLX-owned Python-3.11 MLX runtime was rebuilt from the current
promoted source and verified to contain P61 and P69B3 host + metallib markers.
The full validator ends in `PROMOTED_STACK_PASS`.

Promoted stack remains:

- P58 FP16 GDN fused verifier prework;
- P61 HEADPAIR HPT2 SDPA;
- P69B3 SG2R4 Q8 M4 shared-weight projection;
- P69B6 packaged DUAL64 verifier MLP fusion;
- fixed D3 / verifier M4.

Closed work that must not be reopened:

- P69B8 RMSNormGated fusion;
- P69B9 attention-gate final epilogue;
- P69B10-C recurrent final-state alias;
- P69B5 verifier-QMM staging/synchronization;
- P69B6-D residual ADD->RMS fusion;
- do not rerun P69B7 profiling.

## P69B11-B2 — isolated asymmetric QKV+Z bundle

Candidate bundles the two GDN projections sharing the same FP16 hidden-state
input while preserving their independent arithmetic:

- QKV: M4 K5120 N10240 Q8 GS64, verifier KP2;
- Z: M4 K5120 N6144 Q8 GS64, verifier KP1;
- separate FP16 QKV and Z output boundaries;
- no homogeneous N16384 concatenated QMM.

The candidate uses one Metal dispatch. QKV retains exact KP2 reduction. Z
retains exact KP1 arithmetic inside the first 1536 QKV tile threadgroups.

Exactness:

- QKV bit-exact: PASS;
- Z bit-exact: PASS;
- max absolute error both: 0.

Balanced 15-round isolated result:

- stock median pair: 0.551042 ms;
- candidate median pair: 0.543125 ms;
- median saving: +0.007917 ms/pair (+1.437%);
- pair wins: 9/15;
- projected x48 saving: +0.380016 ms/cycle.

Frozen B2 Metal source SHA256:

`e11dd85965c264cdd9b415348d0c2bd9d19ae2cfd20ce1a7ad1654d740bc8508`

B2 microbenchmark artifact SHA256:

`a8d87db4ff5d2229f542866e40b3616f9daa9c4044fa16684c01031a4bd9efe1`

## P69B11-B3 — controlled integrated 2+2 scout

Order:

- BASE-1
- CAND-1
- CAND-2
- BASE-2

Identical packaged source was installed in both arms; only
`OMLX_VERIFY_GDN_QKVZ_DUAL=0/1` differed. CAND warmup compared candidate vs
stock using the actual loaded model weights before measured frozen runs.

All four frozen runs preserved:

- output hash `101ae2aec9793dfe`;
- 186 verifier cycles;
- acceptance 325/442;
- d1/d2/d3 = 155/101/69.

Actual-weight exactness:

- QKV: PASS;
- Z: PASS.

Integrated BPC:

- BASE-1: 147.222580645 ms/cycle;
- CAND-1: 144.981182796 ms/cycle;
- CAND-2: 145.164516129 ms/cycle;
- BASE-2: 147.380107527 ms/cycle.

Aggregate:

- BASE mean BPC: 147.301344086 ms/cycle;
- CAND mean BPC: 145.072849462 ms/cycle;
- mean saving: +2.228494624 ms/cycle;
- median saving: +2.228494624 ms/cycle;
- BASE mean TG: 17.917944 tok/s;
- CAND mean TG: 18.179509 tok/s;
- TG improvement: +1.4598%.

Sandwich pairs:

- BASE-1 - CAND-1: +2.241397849 ms/cycle;
- BASE-2 - CAND-2: +2.215591398 ms/cycle;
- pair wins: 2/2.

Relative to B2's +0.380016 ms/cycle isolated projection, B3 measured
+586.42% translation. This unusually large translation is accepted only as a
strong scout result because both sandwich pairs agree closely and the
candidate removes real graph/device dispatch work. It still requires 4+4
certification before promotion.

B3 summary SHA256:

`00464bfc698b82adabc2f620ef871c7b0deb8ec8600a0e9499781a2e08018ff4`

After B3, the temporary candidate module and hook were removed, model settings
were restored, and the complete canonical validator returned
`PROMOTED_STACK_PASS`.

## Next experiment

**P69B11-B4 — balanced 4+4 integrated certification of the exact B2/B3
QKV(KP2)+Z(KP1) asymmetric bundle.**

Do not rerun B2 or B3 unless later evidence invalidates their controls.
P69B11 is not promoted yet.
