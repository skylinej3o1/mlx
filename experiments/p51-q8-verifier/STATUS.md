# P51 Q8 Verifier Tuning

## Target

Qwen3.8-27B-oQ8e-fp16-mtp on M1 Max 32-core GPU / 64 GB.

Frozen real coding ruler:

- prompt: 29,297 tokens
- generation: 512 tokens
- temperature: 0
- seed: 1
- thinking: disabled

## Baseline

Target-only M=1:

- decode: 10.536 tok/s

Stock Lightning MTP:

- decode: ~15.59 tok/s
- cycles: 211
- tok/cycle: 2.43
- acceptance: 78.1%
- backbone/cycle: ~151.23 ms

## Fixed-depth sweep

### Fixed D1 / verify M=2

- decode: ~15.082 tok/s
- tok/cycle: 1.82
- backbone/cycle: ~120.06 ms

### Fixed D2 / verify M=3 — current Q8 champion

Run 1:

- decode: 15.687 tok/s
- backbone: 32350.8 ms

Run 2:

- decode: 15.550 tok/s
- backbone: 32499.0 ms

Mean:

- decode: 15.619 tok/s
- cycles: 217
- tok/cycle: 2.36
- acceptance: 293/392 = 74.7%
- depth: d1=175/217, d2=118/175
- backbone/cycle: ~149.42 ms

### Fixed D3 / verify M=4

- decode mean: 15.006 tok/s
- cycles: 187
- tok/cycle: 2.74
- acceptance: 325/442 = 73.5%
- backbone/cycle: ~180.82 ms

### Fixed D4 / verify M=5

- decode mean: 12.794 tok/s
- cycles: 180
- tok/cycle: 2.84
- acceptance: 334/474 = 70.5%
- backbone/cycle: ~213.59 ms

## P51A — true M=3 huge-N MSG template

Change:

    m = 4 if M <= 4 else 6

to:

    m = 3 if M == 3 else (4 if M <= 4 else 6)

This removes M=3 -> M=4 padding for the huge-N MSG path, primarily lm_head.

Fixed-D2 results:

- run 1: 15.727 tok/s
- run 2: 15.572 tok/s
- mean: 15.650 tok/s
- output hash both runs: f42ac9dd2bdf9d5a
- cycles: 217
- tok/cycle: 2.36
- acceptance: 293/392 = 74.7%
- backbone run 1: 32422.2 ms
- backbone run 2: 32491.1 ms
- backbone/cycle mean: ~149.57 ms

Interpretation:

P51A is approximately neutral on end-to-end throughput (+~0.2%) and slightly
worse on measured backbone/cycle versus the fixed-D2 baseline. Do not certify
as a keeper yet. Preserve for later paired testing / kernel geometry work.

## Current experimental runtime state

oMLX: 0.6.3rc2

Model setting:

- mtp_enabled = true
- mtp_num_draft_tokens = 2

Server launch uses:

    OMLX_MTP_FIXED_DEPTH=1

The fixed-depth profiler is an experimental local oMLX patch captured in:

    patches/0001-fixed-mtp-depth-profiler.patch

P51A is captured in:

    patches/0002-p51a-true-m3-msg.patch

## Current conclusion

Fixed D2 / verifier M=3 is the optimization target.

The main bottleneck is target verifier/backbone latency, not MTP-head cost.
Next work should characterize and optimize the M=3 verifier projection paths.

## P51B-P51F routing discoveries

### P51B route attribution

Fixed D2 at ~29.3K:

- stock verifier QMM routes off: 13.429 tok/s
- lm_head route only: 13.747 tok/s
- projection routes only: 14.999 tok/s
- all custom routes: 15.608 / 15.798 tok/s bookends

Custom verifier QMM routing saves roughly 24 ms/backbone-cycle versus stock.
Most of the gain comes from ordinary projection routing.

### P51C global split-K sweep

K_PARTS 1/4/8 did not beat K_PARTS=2.
The sweep also exposed transient system-performance drift.
Keep K_PARTS=2.

### P51D shape census

At verifier M=3, the default N >= 16384 floor routes only:

- K=5120 -> N=17408
- K=5120 -> N=248320 (lm_head)

Important excluded families include N=12288, 10240, 6144, and 5120.

### P51E extra-N scout

Stable baseline mean:

- 15.800 tok/s
- ~148.51 ms backbone/cycle

Results:

- N=12288: 15.949 tok/s
- N=10240: 16.186 tok/s
- N=6144: 16.033 tok/s
- N=5120: 16.308 tok/s

### P51F exact N=5120 decomposition

Stable baseline mean:

- 15.7695 tok/s
- ~148.71 ms backbone/cycle

K=17408 -> N=5120:

- 16.455 tok/s
- ~141.22 ms backbone/cycle
- ~7.49 ms/cycle saved
- +4.35% TG versus bookend baseline
- KEEP

K=6144 -> N=5120:

- 16.355 tok/s alone
- changed trajectory to 214 cycles / 2.39 tok/cycle

Both N=5120 shapes:

- 16.288 tok/s
- ~142.25 ms backbone/cycle

Broad N=5120 control:

- 16.295 tok/s
- ~142.23 ms backbone/cycle

The exact-two-shape route and broad N=5120 control match closely,
validating the exact-shape routing gate.

Adding K=6144 -> N=5120 on top of K=17408 -> N=5120 makes the
same f462 trajectory slower by about 1 ms/backbone-cycle.

Current routing champion:

- fixed D2 / verifier M=3
- default routes
- plus exact K=17408 -> N=5120
- 16.455 tok/s observed at real 29.3K context

## P51J — Warmed routing certification

Warmed paired certification at the frozen 29,297-token ruler:

- default routing:
  - mean TG 15.539 tok/s
  - mean backbone 149.984 ms/cycle
- ALL-MEDIUM:
  - mean TG 16.898 tok/s
  - mean backbone 137.409 ms/cycle

Certified routing delta:

- +8.74% TG
- -8.38% backbone/cycle

ALL-MEDIUM exact routes:

- 17408x5120
- 5120x10240
- 5120x6144
- 5120x12288

P51I subtractive ablation showed all three added medium routes
contribute, with 5120x10240 the largest contributor.

P51J is the current warmed steady-state Q8 routing champion.

## P52A-C — lm_head MSG reconnaissance

P52A re-isolated the huge lm_head custom MSG path under
ALL-MEDIUM routing.

Observed means:

- custom lm_head ON: 17.676 tok/s, 131.894 ms/cycle
- projection-only: 17.215 tok/s, 135.245 ms/cycle

Mean observed lm_head benefit:

- +2.67% TG
- -3.351 ms/cycle

The paired deltas were noisy, so the exact lm_head benefit is not
yet certified.

P52B varied MSG simdgroups per threadgroup.

NSG8 bookend mean:

- 17.666 tok/s
- 132.037 ms/cycle

Results:

- NSG1: 17.051 / 136.397 ms
- NSG2: 17.733 / 131.541 ms
- NSG4: 17.692 / 131.717 ms
- NSG8: 17.666 / 132.037 ms bookend mean
- NSG16: 17.459 / 133.192 ms

Conclusion:

- NSG1 and NSG16 are clearly worse.
- NSG2/4/8 form a relatively flat optimum region.
- NSG2 is an interesting scout but not a certified winner.

P52C explicitly hoisted invariant Q8 scale/bias loads outside the
two-half wsel loop.

Results:

- OFF: 16.925 tok/s, 137.239 ms/cycle
- ON:  16.936 tok/s, 137.095 ms/cycle
- delta: +0.06% TG, -0.145 ms/cycle

Pairwise signs were mixed.

Conclusion:

P52C is rejected as noise-level. Metal appears to already optimize
the invariant qparam loads effectively.

## P52D — MSG output tile width

Q8 lm_head MSG output tile width was parameterized and tested
at fixed NSG=8.

BN4 bookend mean:

- 17.059 tok/s
- 136.240 ms/cycle

Alternatives:

- BN2: 16.888 tok/s, 137.437 ms/cycle
- BN8: 16.817 tok/s, 138.088 ms/cycle

Relative to BN4 mean:

- BN2: -1.00% TG, +1.197 ms/cycle
- BN8: -1.42% TG, +1.848 ms/cycle

Both BN2 and BN8 were slower than both BN4 bookends.

Conclusion:

BN4 is retained. P52D is a strong negative result for alternate
lm_head output tile widths.

## P52E — Q8 float4 lm_head scout

The BN4 Q8 MSG kernel was rewritten with float4 accumulators
across the four output columns.

Three warmed balanced runs each:

Scalar:
- 17.380 / 134.023 ms/cycle
- 17.868 / 130.829 ms/cycle
- 17.757 / 131.451 ms/cycle
- mean 17.668 / 132.101 ms/cycle

Vec4:
- 17.103 / 135.987 ms/cycle
- 17.723 / 131.646 ms/cycle
- 17.872 / 130.765 ms/cycle
- mean 17.566 / 132.799 ms/cycle

Delta:
- -0.58% TG
- +0.698 ms/cycle

All runs used the same 217-cycle speculative trajectory and
f46220cfe4923fc1 output hash.

Conclusion:

P52E rejected. Native float4 accumulator restructuring does not
improve this M1 Max/Q8/M3 lm_head kernel.

## P52F — GS64 qparam broadcast

P52F specialized the Q8 / GS64 / M3 / BN4 lm_head kernel so
each eight-lane cohort loaded shared scale/bias parameters once
and distributed them with simd_shuffle.

Balanced warmed results:

BASE:
- 17.956 tok/s / 130.251 ms/cycle
- 17.890 tok/s / 130.710 ms/cycle
- 17.934 tok/s / 130.376 ms/cycle
- mean 17.927 tok/s / 130.445 ms/cycle

BCAST:
- 17.876 tok/s / 130.869 ms/cycle
- 17.529 tok/s / 133.126 ms/cycle
- 17.866 tok/s / 130.937 ms/cycle
- mean 17.757 tok/s / 131.644 ms/cycle

Delta:
- -0.95% TG
- +1.198 ms/cycle

BCAST lost all three paired comparisons.

All runs retained the same 217-cycle trajectory and
f46220cfe4923fc1 output hash.

Conclusion:

P52F rejected. Cached qparam loads are cheaper than the added
lane-selection and simd_shuffle machinery on this M1 Max.

The BASE trio at 17.927 tok/s is the strongest tight local
control cluster observed so far, but it is not promoted over
the existing cross-session certification without additional
certification.

## P53A — Exact lm_head specialization

The Q8 M3 lm_head kernel was specialized to the exact hot shape:

- M=3
- K=5120
- N=248320
- Q8
- GS64
- BN4

Balanced warmed results:

GEN:
- 17.853 / 130.933 ms/cycle
- 18.040 / 129.708 ms/cycle
- 17.974 / 130.170 ms/cycle
- mean 17.956 / 130.270 ms/cycle

EXACT:
- 17.906 / 130.568 ms/cycle
- 18.029 / 129.841 ms/cycle
- 17.950 / 130.295 ms/cycle
- mean 17.962 / 130.235 ms/cycle

Delta:
- +0.03% TG
- -0.035 ms/cycle

All runs retained 217 cycles and
f46220cfe4923fc1 output hash.

Conclusion:

P53A is noise-level and rejected. Exact K/N compile-time
specialization does not materially improve the current lm_head
kernel.

Observed full-ruler 18 tok/s crossings:
- GEN2 18.040 tok/s
- EXACT2 18.029 tok/s

These are observed peaks, not a new cross-session certification.

## P53B/C — Shape-specific K-parts

P53B introduced exact-shape K_PARTS routing for the regular
split-K verifier kernel.

Scout result of interest:

5120x17408 with K_PARTS=4:
- 18.337 tok/s
- 129.371 ms/cycle
- 214 cycles
- accept 297/392
- hash 101ae2aec9793dfe

Baseline bookend:
- 17.943 tok/s
- 130.356 ms/cycle
- 217 cycles
- accept 294/392
- hash f46220cfe4923fc1

P53C then ran a balanced 4+4 certification.

BASE:
- mean 18.029 tok/s
- SD 0.063
- mean 129.842 ms/cycle
- SD 0.406
- always 217 cycles
- always accept 294/392
- always hash f46220cfe4923fc1

UP-KP4:
- mean 18.309 tok/s
- SD 0.064
- mean 129.516 ms/cycle
- SD 0.435
- always 214 cycles
- always accept 297/392
- always hash 101ae2aec9793dfe

Delta:
- +1.55% realized TG
- -0.325 ms/cycle

Observed peak:
- 18.360 tok/s at 29,297 prompt tokens

Interpretation:

The realized throughput gain is highly reproducible.

Most of the gain comes from the deterministic numerical-path
change reducing speculative cycles from 217 to 214. Raw kernel
cost improves modestly by 0.325 ms/cycle.

Status:
- performance certification: PASS
- deterministic trajectory: PASS
- quality/equivalence certification: pending

Do not interpret the extra accepts as proof of higher model
quality. Different split-reduction ordering perturbs floating
point results and can change close greedy decisions.
