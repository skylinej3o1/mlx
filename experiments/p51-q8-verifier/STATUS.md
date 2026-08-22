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

## P53D — NSG stack on UP-KP4

P53D retested lm_head MSG NSG geometry with the P53C
5120x17408 K_PARTS=4 winner enabled.

All runs retained exactly:

- 214 cycles
- accept 297/392
- hash 101ae2aec9793dfe

Therefore this sweep provides a clean kernel-cost comparison
without speculative-trajectory differences.

Results:

NSG8-A:
- 18.325 tok/s
- 129.466 ms/cycle

NSG2:
- 17.848 tok/s
- 132.465 ms/cycle

NSG4:
- 18.309 tok/s
- 129.503 ms/cycle

NSG8-B:
- 18.403 tok/s
- 128.978 ms/cycle

NSG8 bookend mean:
- 18.364 tok/s
- 129.222 ms/cycle

Relative:

- NSG2: -2.81% TG, +3.243 ms/cycle
- NSG4: -0.30% TG, +0.281 ms/cycle

Conclusion:

NSG8 remains the lm_head winner when stacked with UP-KP4.
NSG2 is decisively rejected. NSG4 is slightly slower than NSG8.

New observed real-29.3K peak:
- 18.403 tok/s

P53C remains the formal performance-certification set because
P53D contains only two NSG8 bookends.

## P53E — Remaining per-shape K-parts

P53E completed the D2/M3 exact-shape K_PARTS map while keeping
the P53C winner 5120x17408:4 enabled.

Baseline configuration:

- 5120x17408: K_PARTS=4
- all other regular verifier projections: default K_PARTS=2
- lm_head: NSG8 / BN4

BASE bookends:

- 18.366 tok/s / 129.230 ms/cycle
- 18.251 tok/s / 129.900 ms/cycle
- mean 18.309 tok/s / 129.565 ms/cycle
- always 214 cycles
- always accept 297/392
- always hash 101ae2aec9793dfe

Additional shape tests:

5120x6144 K_PARTS=1:
- 18.034 tok/s
- 129.724 ms/cycle
- -1.50% realized TG
- +0.158 ms/cycle
- reverted to 217-cycle / f462 trajectory

5120x6144 K_PARTS=4:
- 18.056 tok/s
- 129.526 ms/cycle
- -1.38% realized TG
- -0.039 ms/cycle
- reverted to 217-cycle / f462 trajectory

5120x12288 K_PARTS=1:
- 18.069 tok/s
- 129.432 ms/cycle
- -1.31% realized TG
- -0.133 ms/cycle
- reverted to 217-cycle / f462 trajectory

5120x12288 K_PARTS=4:
- 18.327 tok/s
- 129.422 ms/cycle
- +0.10% realized TG
- -0.143 ms/cycle
- retained 214-cycle / 101ae trajectory

Conclusion:

No additional shape-specific K_PARTS override is promoted.

The final D2/M3 verifier K_PARTS policy remains:

- 5120x17408 -> K_PARTS=4
- all other regular projections -> K_PARTS=2

P53E closes the current D2/M3 per-shape K_PARTS search.

Current D2/M3 performance state:

- P53C certified mean: 18.309 tok/s at 29,297 prompt tokens
- P53C SD: 0.064 tok/s
- deterministic trajectory: 214 cycles, accept 297/392
- observed peak to date: 18.403 tok/s
- lm_head geometry retained: NSG8 / BN4

Next phase:

Reopen D3/M4 using the verifier routing and per-shape lessons
learned from the D2/M3 optimization campaign.

## P54A — D3/M4 verifier-routing transfer

P54A reopened fixed D3 / verifier M=4 using the routing
lessons learned during the D2/M3 campaign.

Configuration:

- fixed speculative depth D3
- verifier M=4
- global regular-projection K_PARTS=2
- no shape-specific K_PARTS overrides
- lm_head NSG8 / BN4
- frozen 29,297-token ruler

M4 shape census confirmed the same important regular
projection families seen at M3:

- 17408x5120
- 5120x10240
- 5120x6144
- 5120x12288
- 5120x17408

The default route threshold only admitted:

- 5120x17408
- 5120x248320 lm_head

ALL-MEDIUM additionally routed:

- 17408x5120
- 5120x10240
- 5120x6144
- 5120x12288

DEFAULT:

- 14.084 tok/s / 187.606 ms/cycle
- 14.067 tok/s / 187.715 ms/cycle
- mean 14.075 tok/s
- mean 187.661 ms/cycle
- always 187 cycles
- always accept 325/442
- always hash f42ac9dd2bdf9d5a

ALL-MEDIUM:

- 16.028 tok/s / 155.118 ms/cycle
- 16.707 tok/s / 151.007 ms/cycle
- mean 16.367 tok/s
- mean 153.062 ms/cycle
- always 197 cycles
- always accept 315/452
- always hash f46220cfe4923fc1

Realized delta:

- +16.28% TG
- -34.599 ms/backbone-cycle

Interpretation:

The D2 routing strategy transfers extremely strongly to M4.

ALL-MEDIUM changes the deterministic numerical/speculative
trajectory from 187 cycles to 197 cycles and reduces acceptance,
yet the verifier-backbone latency reduction is large enough to
overwhelm the additional speculative cycles and increase
end-to-end throughput by more than 16%.

Therefore the historical untuned D3/M4 result is no longer a
useful estimate of optimized D3 performance.

P54A establishes ALL-MEDIUM as the M4 routing baseline for the
next phase.

Next:

Perform M4 subtractive per-shape routing attribution before
reintroducing shape-specific split-K tuning.

## P54B — M4 subtractive routing attribution

P54B performed local-sandwich subtractive attribution on
the P54A ALL-MEDIUM D3/M4 routing baseline.

Configuration:

- fixed D3 / verifier M=4
- all regular routed projections at K_PARTS=2
- lm_head NSG8 / BN4
- frozen 29,297-token ruler

Five interleaved ALL-MEDIUM controls were exceptionally stable:

- TG range: 17.561 to 17.575 tok/s
- backbone range: 146.382 to 146.468 ms/cycle
- always 197 cycles
- always accept 315/452
- always hash f46220cfe4923fc1

Subtractive attribution:

17408x5120 removed:

- 16.466 tok/s
- 165.841 ms/cycle
- -6.30% TG versus local ALL-MEDIUM control
- +19.416 ms/cycle
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

5120x10240 removed:

- 17.523 tok/s
- 154.657 ms/cycle
- -0.29% TG
- +8.240 ms/cycle
- 187 cycles
- accept 325/442
- hash f42ac9dd2bdf9d5a

5120x6144 removed:

- 17.985 tok/s
- 150.501 ms/cycle
- +2.37% TG
- +4.076 ms/cycle
- 187 cycles
- accept 325/442
- hash f42ac9dd2bdf9d5a

5120x12288 removed:

- 17.227 tok/s
- 149.393 ms/cycle
- -1.94% TG
- +2.957 ms/cycle
- retained 197 cycles
- accept 315/452
- hash f46220cfe4923fc1

Interpretation:

All four additional routes reduce raw M4 verifier cost.

17408x5120 is the dominant route and is indispensable.

5120x12288 is also a clean keeper: removing it worsens kernel
cost without changing the speculative trajectory.

5120x10240 and 5120x6144 show a numerical-path interaction.
Removing either returns the same 187-cycle / f42a trajectory,
while full ALL-MEDIUM uses the 197-cycle / f462 trajectory.

Therefore 5120x6144 should not yet simply be removed from the
optimized policy. Its custom route saves approximately
4.1 ms/cycle, but the current K_PARTS=2 reduction ordering
participates in a trajectory change large enough to make the
route net-negative end to end.

Likewise 5120x10240 saves approximately 8.2 ms/cycle, but its
realized TG benefit is mostly cancelled by the same trajectory
interaction.

Next:

Test per-shape K_PARTS alternatives on 5120x6144 and
5120x10240 while retaining the full ALL-MEDIUM routing set,
looking for a reduction ordering that preserves the kernel
savings while recovering a lower-cycle speculative trajectory.

## P54C — M4 K-parts trajectory rescue

P54C tested shape-specific split-K alternatives on the two
M4 routes implicated in the P54B numerical-path interaction.

Configuration:

- fixed D3 / verifier M=4
- full ALL-MEDIUM routing
- lm_head NSG8 / BN4
- untouched regular projections default to K_PARTS=2
- frozen 29,297-token ruler

All KP2 controls retained:

- 197 cycles
- accept 315/452
- hash f46220cfe4923fc1

The control session showed substantial system-performance drift,
so conclusions use local sandwich comparisons rather than
cross-session absolute throughput.

5120x6144 K_PARTS=1:

- 17.512 tok/s
- 151.435 ms/cycle
- +7.65% TG versus local control
- -2.206 ms/cycle
- 187 cycles
- accept 325/442
- hash f42ac9dd2bdf9d5a

5120x6144 K_PARTS=4:

- 15.978 tok/s
- 155.528 ms/cycle
- -1.71% TG
- +1.869 ms/cycle
- retained 197-cycle / f462 trajectory

5120x10240 K_PARTS=1:

- 16.916 tok/s
- 154.933 ms/cycle
- +4.25% realized TG
- +1.291 ms/cycle
- 187 cycles
- accept 325/442
- hash f42ac9dd2bdf9d5a

5120x10240 K_PARTS=4:

- 16.886 tok/s
- 155.072 ms/cycle
- +2.87% realized TG
- +2.615 ms/cycle
- 187 cycles
- accept 325/442
- hash f42ac9dd2bdf9d5a

Interpretation:

5120x6144 K_PARTS=1 is the strongest trajectory-rescue
candidate.

It simultaneously restores the lower-cycle 187 / f42a
speculative trajectory and improves raw verifier cost versus
the surrounding full-ALL-MEDIUM KP2 controls.

The 5120x10240 KP1 and KP4 alternatives also recover the
187-cycle trajectory, but both increase raw verifier
latency, making them inferior rescue candidates.

5120x6144 K_PARTS=4 is rejected.

Before promoting 5120x6144:1, directly compare it against
leaving 5120x6144 unrouted. Both configurations are expected
to share the same 187-cycle / f42a trajectory, allowing a
clean kernel-cost certification without speculative-path
confounding.

## P54D — 5120x6144 KP1 route certification

P54D directly certified the P54C trajectory-rescue candidate
against leaving 5120x6144 on stock qmm.

Common configuration:

- fixed D3 / verifier M=4
- 17408x5120 custom routed
- 5120x10240 custom routed
- 5120x12288 custom routed
- 5120x17408 custom routed at default KP2
- lm_head NSG8 / BN4
- frozen 29,297-token ruler

STOCK left 5120x6144 unrouted.

RESCUE custom routed 5120x6144 with K_PARTS=1.

Four balanced runs per configuration:

STOCK:

- 17.976 tok/s / 150.611 ms/cycle
- 18.017 tok/s / 150.474 ms/cycle
- 18.034 tok/s / 150.358 ms/cycle
- 17.971 tok/s / 150.578 ms/cycle

Mean:

- 17.999 tok/s
- SD 0.031 tok/s
- 150.505 ms/cycle
- SD 0.114 ms/cycle

RESCUE:

- 18.469 tok/s / 146.688 ms/cycle
- 18.489 tok/s / 146.656 ms/cycle
- 18.455 tok/s / 146.841 ms/cycle
- 18.447 tok/s / 146.890 ms/cycle

Mean:

- 18.465 tok/s
- SD 0.018 tok/s
- 146.769 ms/cycle
- SD 0.114 ms/cycle

Delta:

- +2.59% realized TG
- -3.736 ms/backbone-cycle

All eight certification runs had the identical deterministic
trajectory:

- 187 cycles
- accept 325/442
- hash f42ac9dd2bdf9d5a

Interpretation:

5120x6144 K_PARTS=1 is a clean kernel-performance win.

Unlike several earlier split-K experiments, the realized
throughput improvement is not caused by a numerical-path
change. STOCK and RESCUE have identical cycle counts,
acceptance statistics, and final output hashes.

Therefore 5120x6144:1 is promoted into the D3/M4 verifier
policy.

Current D3/M4 champion:

- mean 18.465 tok/s
- SD 0.018 tok/s
- mean 146.769 ms/backbone-cycle
- 187 cycles
- 325/442 accepts
- hash f42ac9dd2bdf9d5a
- observed peak 18.489 tok/s

This exceeds the previous P53C D2/M3 certified mean of
18.309 tok/s on the same frozen real ruler.

Next:

Transfer the remaining high-value D2 per-shape K_PARTS
lessons onto the certified D3/M4 rescue baseline, beginning
with 5120x17408 and 17408x5120.

## P54E — D2 K-parts transfer to rescued M4

P54E tested selected D2 per-shape split-K lessons on top of
the P54D certified D3/M4 rescue configuration.

Baseline:

- fixed D3 / verifier M=4
- full ALL-MEDIUM routing
- 5120x6144: K_PARTS=1
- remaining regular routed shapes: default K_PARTS=2
- lm_head NSG8 / BN4
- frozen 29,297-token ruler

Baseline controls were stable:

- TG range 18.422 to 18.471 tok/s
- BPC range 146.690 to 146.915 ms/cycle
- always 187 cycles
- always accept 325/442
- always hash f42ac9dd2bdf9d5a

17408x5120 K_PARTS=1:

- 17.476 tok/s
- 147.766 ms/cycle
- -5.24% TG
- +0.917 ms/cycle
- 196 cycles
- accept 316/450
- hash f46220cfe4923fc1

Rejected.

5120x17408 K_PARTS=1:

- 18.540 tok/s
- 146.972 ms/cycle
- +0.50% TG
- +0.152 ms/cycle versus local baseline
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

This candidate is trajectory-driven rather than kernel-driven.
It slightly increases raw backbone cost per cycle but removes
one speculative cycle, producing a small realized TG gain.

5120x17408 K_PARTS=4:

- 17.630 tok/s
- 146.495 ms/cycle
- -4.45% TG
- -0.277 ms/cycle
- 196 cycles
- accept 316/450
- hash f46220cfe4923fc1

Rejected.

The D2 5120x17408 KP4 winner therefore does not transfer to M4.

Next:

Formally certify 5120x17408 K_PARTS=1 against the P54D M4
champion using balanced repeated runs. Promotion requires a
stable 186-cycle trajectory and a reproducible realized TG gain.

## P54F — M4 5120x17408 KP1 certification

P54F formally certified the P54E 5120x17408 K_PARTS=1
candidate on top of the P54D rescued D3/M4 baseline.

BASE policy:

- fixed D3 / verifier M=4
- full ALL-MEDIUM routing
- 5120x6144: K_PARTS=1
- 5120x17408: default K_PARTS=2
- other routed regular projections: K_PARTS=2
- lm_head NSG8 / BN4
- frozen 29,297-token ruler

TEST policy additionally used:

- 5120x17408: K_PARTS=1

Four balanced runs per configuration.

BASE:

- mean 18.453 tok/s
- SD 0.015 tok/s
- mean 146.754 ms/cycle
- SD 0.121 ms/cycle
- always 187 cycles
- always accept 325/442
- always hash f42ac9dd2bdf9d5a

KP1:

- mean 18.504 tok/s
- SD 0.028 tok/s
- mean 147.128 ms/cycle
- SD 0.141 ms/cycle
- always 186 cycles
- always accept 325/442
- always hash 101ae2aec9793dfe

Delta:

- +0.28% realized TG
- +0.374 ms/backbone-cycle

Interpretation:

5120x17408 K_PARTS=1 is a small but reproducible
trajectory-driven win.

The alternate reduction ordering slightly increases the cost
of each backbone cycle, but deterministically removes one
speculative cycle.

Approximate aggregate backbone cost:

- BASE: 187 * 146.754 ms = 27.443 s
- KP1: 186 * 147.128 ms = 27.366 s

The approximately 77 ms aggregate saving is consistent with
the observed end-to-end throughput improvement.

Therefore 5120x17408:1 is promoted into the D3/M4 policy.

Current certified D3/M4 champion:

- mean 18.504 tok/s
- SD 0.028 tok/s
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

Current shape policy:

- 17408x5120 -> K_PARTS=2
- 5120x10240 -> K_PARTS=2
- 5120x6144 -> K_PARTS=1
- 5120x12288 -> K_PARTS=2
- 5120x17408 -> K_PARTS=1
- lm_head -> NSG8 / BN4

This exceeds the P53C D2/M3 certified mean of
18.309 tok/s by approximately 1.07%.

Observed real-ruler peak remains 18.540 tok/s.

Next:

Retune lm_head geometry specifically for true verifier M=4
rather than continuing to assume the D2/M3 NSG8 / BN4
geometry transfers unchanged.

## P55A — True-M4 lm_head NSG sweep

P55A retuned the huge-N lm_head MSG geometry specifically
for the current certified D3/M4 verifier configuration.

Frozen regular-projection policy:

- 17408x5120 -> K_PARTS=2
- 5120x10240 -> K_PARTS=2
- 5120x6144 -> K_PARTS=1
- 5120x12288 -> K_PARTS=2
- 5120x17408 -> K_PARTS=1

lm_head BN remained fixed at BN4.

All runs retained the identical deterministic trajectory:

- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

NSG8 controls:

- 18.499 tok/s / 147.194 ms/cycle
- 18.533 tok/s / 147.049 ms/cycle
- 18.484 tok/s / 147.248 ms/cycle
- 18.476 tok/s / 147.285 ms/cycle

NSG2:

- 18.472 tok/s
- 147.407 ms/cycle
- -0.24% TG versus local NSG8 controls
- +0.286 ms/cycle

Rejected.

NSG4:

- 18.556 tok/s
- 146.910 ms/cycle
- +0.26% TG versus local NSG8 controls
- -0.239 ms/cycle

Best candidate.

NSG16:

- 18.507 tok/s
- 147.118 ms/cycle
- +0.15% TG
- -0.149 ms/cycle

Positive but smaller than NSG4.

Interpretation:

Because all configurations preserve the identical cycle count,
acceptance statistics, and output hash, the NSG4 result is a
clean lm_head kernel-geometry improvement rather than a
speculative-trajectory effect.

NSG4 is the P55A winner but the approximately +0.26% effect
is small enough to require balanced repeated certification
before promotion.

New observed real-ruler peak:

- 18.556 tok/s at 29,297 prompt tokens

Next:

Certify NSG4 versus NSG8 with balanced repeated runs while
holding BN4 and the complete D3/M4 projection policy fixed.

## P55B — True-M4 NSG4 certification

P55B formally tested the P55A NSG4 lm_head candidate against
the retained NSG8 geometry using balanced 4+4 runs.

Common configuration:

- fixed D3 / verifier M=4
- current certified regular-projection routing policy
- 5120x6144 -> K_PARTS=1
- 5120x17408 -> K_PARTS=1
- lm_head BN4
- frozen 29,297-token ruler

All eight runs retained the identical deterministic trajectory:

- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

NSG8:

- mean 18.499 tok/s
- SD 0.032 tok/s
- mean 147.202 ms/cycle
- SD 0.092 ms/cycle

NSG4:

- mean 18.460 tok/s
- SD 0.086 tok/s
- mean 147.328 ms/cycle
- SD 0.326 ms/cycle

Delta:

- -0.21% realized TG
- +0.126 ms/backbone-cycle

Conclusion:

The P55A NSG4 scout win did not reproduce under balanced
certification.

Because trajectory, acceptance, and output hash were identical,
this is a clean kernel-geometry rejection.

NSG4 is rejected.

NSG8 remains the true-M4 lm_head NSG policy.

The substantially higher run-to-run variance observed under
NSG4 explains the favorable single P55A scout result.

NSG16 remains unpromoted. Its P55A signal was smaller than the
NSG4 scout signal and does not currently justify separate
certification.

Current certified D3/M4 policy remains:

- 17408x5120 -> K_PARTS=2
- 5120x10240 -> K_PARTS=2
- 5120x6144 -> K_PARTS=1
- 5120x12288 -> K_PARTS=2
- 5120x17408 -> K_PARTS=1
- lm_head -> NSG8 / BN4

Certified champion remains:

- 18.504 tok/s
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

Next:

Retune lm_head BN specifically for true verifier M=4 with
NSG8 fixed.

## P55C — True-M4 lm_head BN sweep

P55C completed true-M4 lm_head geometry retuning with
NSG8 fixed and the certified D3/M4 regular-projection policy
unchanged.

All configurations retained the identical deterministic
trajectory:

- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

BN4 controls:

- 18.458 tok/s / 147.353 ms/cycle
- 18.411 tok/s / 147.600 ms/cycle
- 18.531 tok/s / 147.028 ms/cycle

BN2:

- 18.347 tok/s
- 148.522 ms/cycle
- -0.47% TG versus local BN4 controls
- +1.045 ms/cycle

Rejected.

BN8:

- 18.392 tok/s
- 148.197 ms/cycle
- -0.43% TG versus local BN4 controls
- +0.883 ms/cycle

Rejected.

Conclusion:

BN4 remains the true-M4 lm_head tile-width policy.

Together with P55B, the current M4 lm_head geometry remains:

- NSG8
- BN4

No additional lm_head geometry change is promoted.

Current certified D3/M4 champion remains:

- 18.504 tok/s mean
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

Current regular projection policy:

- 17408x5120 -> K_PARTS=2
- 5120x10240 -> K_PARTS=2
- 5120x6144 -> K_PARTS=1
- 5120x12288 -> K_PARTS=2
- 5120x17408 -> K_PARTS=1

P55 closes the inherited lm_head parameter-retuning search.

Next:

Reopen D4/M5 and measure routing transfer before attempting
new M5-specific kernel specialization.

## P56A — D4/M5 verifier-routing transfer

P56A reopened fixed D4 / verifier M=5 and measured the
transfer of the ALL-MEDIUM verifier-routing policy.

Configuration:

- fixed speculative depth D4
- verifier M=5
- global regular-projection K_PARTS=2
- no shape-specific K_PARTS overrides
- lm_head NSG8 / BN4
- frozen 29,297-token ruler

M5 shape census confirmed the expected verifier families.

DEFAULT:

- 12.016 tok/s / 223.809 ms/cycle
- 11.824 tok/s / 226.564 ms/cycle
- mean 11.920 tok/s
- mean 225.187 ms/cycle
- always 180 cycles
- accept 334/474
- hash f42ac9dd2bdf9d5a

ALL-MEDIUM:

- 14.630 tok/s / 174.422 ms/cycle
- 14.520 tok/s / 174.568 ms/cycle
- mean 14.575 tok/s
- mean 174.495 ms/cycle
- always 188 cycles
- accept 324/476
- hash f46220cfe4923fc1

Delta:

- +22.27% realized TG
- -50.692 ms/backbone-cycle

Interpretation:

Verifier routing transfers extremely strongly to M5.

However, even after removing more than 50 ms/backbone-cycle,
D4/M5 remains substantially behind the certified D3/M4
champion at the frozen ~29.3K ruler.

The deeper speculative configuration currently provides no
round-efficiency advantage over D3/M4:

- D4/M5 ALL-MEDIUM: 188 cycles / 2.72 tok per cycle
- D3/M4 champion: 186 cycles / approximately 2.75 tok per cycle

D4/M5 also shows materially higher MTP-side runtime.

Therefore a broad M5 per-shape tuning campaign is not yet
justified.

One remaining structural M5-specific opportunity should be
tested first:

The huge-N lm_head path currently maps verifier M=5 onto an
M6 MSG template. Test a true-M5 MSG template while holding
all other P56A parameters fixed.

If true-M5 does not produce a large structural reduction,
close D4/M5 for the ~30K operating point and return to the
D3/M4 champion.

## P56B — True-M5 lm_head structural scout

P56B tested a true verifier-M5 huge-N MSG template against
the existing behavior, which pads verifier M=5 to an M6
lm_head template.

Common configuration:

- fixed D4 / verifier M=5
- ALL-MEDIUM routing
- global regular-projection K_PARTS=2
- no shape-specific K_PARTS overrides
- lm_head NSG8 / BN4
- frozen 29,297-token ruler

PAD6:

- 15.870 tok/s / 163.986 ms/cycle
- 15.585 tok/s / 165.573 ms/cycle
- mean 15.727 tok/s
- mean 164.780 ms/cycle

TRUE5:

- 15.901 tok/s / 163.579 ms/cycle
- 15.871 tok/s / 163.751 ms/cycle
- mean 15.886 tok/s
- mean 163.665 ms/cycle

Delta:

- +1.01% realized TG
- -1.114 ms/backbone-cycle

All four runs retained the identical deterministic trajectory:

- 188 cycles
- accept 324/476
- hash f46220cfe4923fc1

Interpretation:

The true-M5 MSG template is a genuine kernel-side
improvement. Removing the unused sixth lm_head row saves
approximately 1.1 ms per backbone cycle without changing
speculative behavior.

However, the effect is far too small to make D4/M5
competitive with the certified D3/M4 configuration at the
~29.3K operating point.

The P56B session also ran in a materially faster system state
than P56A, so cross-session absolute throughput is not used
for attribution.

Approximately:

- 1.114 ms/cycle * 188 cycles = 209 ms aggregate backbone saving

This is much smaller than the remaining D4/M5 deficit.

Conclusion:

Close D4/M5 as a candidate for the ~30K operating point.

Retain the true-M5 implementation as an experimental patch
for future shorter-context or depth-routing work, but do not
promote D4 as the current runtime policy.

Restore active runtime to fixed D3 / verifier M=4.

Current ~30K champion remains the P54F D3/M4 policy:

- 18.504 tok/s certified mean
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

Next:

Measure speculative-depth crossover versus context length.
Determine where D2/M3, D3/M4, and potentially D4/M5 should
be selected by an adaptive runtime policy.

## P57A — Real-context D2/M3 versus D3/M4 map

P57A compared the certified D2/M3 and D3/M4 policies across
nested real-context suffixes derived from the existing
29,297-token real request.

Actual server-reported prompt sizes:

- 2,358 tokens
- 4,329 tokens
- 8,585 tokens
- 17,259 tokens
- 29,297 tokens

D3/M4 beat D2/M3 at every sampled operating point.

Results:

2358 tokens:

- D2: 23.671 tok/s, 189 cycles, 112.784 ms/cycle
- D3: 24.847 tok/s, 166 cycles, 121.852 ms/cycle
- D3 advantage: +4.97%

4329 tokens:

- D2: 21.019 tok/s, 210 cycles, 114.198 ms/cycle
- D3: 24.497 tok/s, 166 cycles, 123.638 ms/cycle
- D3 advantage: +16.55%

8585 tokens:

- D2: 22.151 tok/s, 192 cycles, 118.476 ms/cycle
- D3: 22.380 tok/s, 174 cycles, 128.726 ms/cycle
- D3 advantage: +1.03%

17259 tokens:

- D2: 19.930 tok/s, 201 cycles, 125.448 ms/cycle
- D3: 23.374 tok/s, 150 cycles, 135.790 ms/cycle
- D3 advantage: +17.28%

29297 tokens:

- D2: 17.457 tok/s, 214 cycles, 134.398 ms/cycle
- D3: 18.386 tok/s, 186 cycles, 147.609 ms/cycle
- D3 advantage: +5.32%

Interpretation:

No D2/D3 context-length crossover was observed.

D3/M4 is the winner at every sampled real-context point and
should remain the default speculative-depth policy.

The experiment also demonstrates that context length alone
does not determine realized speculative throughput.

For example:

- 8585-token D3: 174 cycles, 22.380 tok/s
- 17259-token D3: 150 cycles, 23.374 tok/s

Despite the much larger context and higher cycle cost at
17259 tokens, much stronger speculative acceptance reduces
the number of cycles sufficiently to make it faster.

Therefore speculative trajectory / acceptance quality can
dominate the raw context-length cost.

The nested-context experiment changes both context length and
conversation content, so these results should be interpreted
as real-workload operating points rather than a causal
context-length-only curve.

Output equivalence:

- 2358: D2 and D3 hashes matched
- 4329: D2 and D3 hashes matched
- 8585: D2 and D3 hashes differed
- 17259: D2 and D3 hashes matched
- 29297: D2 and D3 hashes matched

The 8585-token point therefore remains useful as realized
operational throughput but is not an exact-output-equivalent
speed comparison.

Next:

Test D4/M5 selectively on the real-context workloads showing
the strongest deep-D3 acceptance, particularly 4329 and
17259 tokens.

This tests whether D4 should be selected according to
speculative acceptance regime rather than context length.

## P57B — Acceptance-rich D4/M5 challenge

P57B tested D4/M5 specifically on the two P57A real-context
workloads that had shown unusually favorable deep-D3
speculative acceptance.

Configurations:

D3:

- fixed D3 / verifier M=4
- certified M4 routing policy
- 5120x6144 -> K_PARTS=1
- 5120x17408 -> K_PARTS=1
- remaining routed regular projections -> K_PARTS=2
- lm_head NSG8 / BN4

D4:

- fixed D4 / verifier M=5
- ALL-MEDIUM routing
- global regular-projection K_PARTS=2
- true-M5 lm_head experimental template
- lm_head NSG8 / BN4

4329-token workload:

D3:

- mean 21.254 tok/s
- 181 cycles
- mean 128.376 ms/cycle
- accept 330/433
- hash 695669b3bf3ea831

D4:

- mean 19.102 tok/s
- 170 cycles
- mean 145.065 ms/cycle
- accept 343/467
- hash 695669b3bf3ea831

Delta:

- D4 -10.13% realized TG
- D4 removes 11 verifier cycles
- D4 adds 16.689 ms/backbone-cycle

17259-token workload:

D3:

- mean 20.625 tok/s
- 165 cycles
- mean 143.470 ms/cycle
- accept 346/421
- hash 331af8ab91273718

D4:

- mean 20.081 tok/s
- 149 cycles
- mean 159.143 ms/cycle
- accept 364/457
- hash 331af8ab91273718

Delta:

- D4 -2.64% realized TG
- D4 removes 16 verifier cycles
- D4 adds 15.673 ms/backbone-cycle

Interpretation:

D4/M5 loses even on the two real workloads chosen to give
deeper speculation its strongest plausible opportunity.

At 17259 tokens D4 successfully reduces verifier rounds from
165 to 149, but the higher M5 verifier cost and substantially
larger MTP-side cost outweigh the speculative-round savings.

Both comparisons retain exact final-output equivalence between
D3 and D4.

Therefore no adaptive D3/D4 runtime policy is justified with
the current verifier implementation.

Combined P57 conclusion:

- D2/M3 lost to D3/M4 at every sampled P57A operating point.
- D4/M5 lost at ~30K in P56.
- D4/M5 also lost its favorable 4329- and 17259-token P57B
  challenges.
- D3/M4 remains the default production speculative depth.

P57B also showed that speculative trajectory itself is not
fully stable across separate benchmark sessions.

For the same request and D3 policy:

- 4329-token P57A: 166 cycles
- 4329-token P57B: 181 cycles
- 17259-token P57A: 150 cycles
- 17259-token P57B: 165 cycles

The final output hashes remained the same.

Therefore previously observed prompt-specific acceptance
should not currently be treated as a sufficiently stable
routing signal.

Operational note:

Because P57B was pasted into an interactive shell, its EXIT
trap did not execute when the benchmark block completed.
The experimental true-M5 patch therefore remained installed
until it was explicitly reverse-applied afterward.

Active runtime was restored to fixed D3 / verifier M=4.

Next:

Keep D3/M4 fixed and return to structural performance work.
Profile the remaining D3/M4 backbone cost by operation and
context length to identify the next high-leverage kernel or
runtime target instead of further speculative-depth tuning.

## P58 — FP16 fused GDN verifier prework

P58 returned to structural D3/M4 backbone profiling after
P57 closed adaptive speculative-depth routing.

P58A-P58C established the active Qwen3.5 verifier structure:

- 64 transformer layers total
- 48 linear / Gated DeltaNet layers
- 16 full-attention layers
- full attention every fourth layer
- hidden size 5120
- 24 query heads
- 4 KV heads
- head_dim 256
- fixed D3 / verifier M=4

The existing qwen35 verify-SDPA split patch was confirmed
active at M=4:

- q_len=4
- GQA factor=6
- vector row budget=32
- row limit=5

Therefore the full M=4 verifier block already fits in one
vector-SDPA dispatch per full-attention layer.

P58D-P58F then found that the existing fused GDN verify
prework patch was installed successfully but never engaged
on this model.

The exact rejection was dtype only.

Observed verifier shape:

- S=4
- input shape (1, 4, 5120)
- input dtype FP16
- conv state dtype FP16
- conv weight dtype FP16
- gdn_sink present
- mask None

The existing patch required BF16 for all three tensors.

All other eligibility conditions passed.

P58G audited the fused Metal kernel.

The kernel itself is dtype-generic:

- scalar type T is templated from qkv.dtype
- outputs use qkv.dtype
- convolution accumulation uses FP32
- RMS sum/reduction uses FP32
- output conversion returns through T

The BF16-only restriction therefore lived primarily in the
Python eligibility checks and BF16 scale construction rather
than in a BF16-specific Metal implementation.

P58H added a temporary env-gated FP16 route:

OMLX_GDN_VERIFY_PREWORK_FP16=1

The FP16 route:

- permits FP16 input/state/conv-weight tensors
- requires state and weight dtype to equal input dtype
- constructs q/k scales in inputs.dtype
- otherwise leaves the fused kernel unchanged

P58H 2+2 scout at the 29297-token real workload:

BASE mean:

- 18.090 tok/s
- 148.987 ms/cycle

FUSED mean:

- 18.335 tok/s
- 147.508 ms/cycle

Delta:

- +1.35% realized TG
- -1.478 ms/cycle

Every run retained:

- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

P58I then ran a balanced 4+4 certification:

Order:

- BASE-1
- FUSED-1
- FUSED-2
- BASE-2
- FUSED-3
- BASE-3
- BASE-4
- FUSED-4

BASE:

- mean TG 17.960 tok/s
- TG SD 0.063
- mean BPC 149.563 ms
- BPC SD 0.392

FUSED:

- mean TG 18.386 tok/s
- TG SD 0.147
- mean BPC 147.103 ms
- BPC SD 0.717

Certified paired delta:

- +2.37% realized TG
- -2.460 ms/backbone-cycle
- approximately 457.6 ms target-backbone time removed across
  186 verifier cycles

All eight certification runs retained exactly:

- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

The fused arm engaged cleanly on every FUSED run and never
fell back.

P58I therefore establishes a clean kernel-side speed win,
not a speculative-trajectory effect.

Absolute-session note:

The P58I BASE session was slower than the historical P54F
certification environment.

Therefore 18.386 tok/s is not promoted as a new absolute
global champion measurement.

P58 certifies the paired FP16 GDN kernel delta itself:

- +2.37% TG
- -2.460 ms/cycle

P58J directly compared the internal fused FP16 prework output
against the stock composed FP16 path.

Coverage:

- 96 GDN layer calls
- two complete 48-GDN-layer verifier passes

Direct tensor comparison result:

- q differing elements: 0
- q max absolute error: 0
- k differing elements: 0
- k max absolute error: 0
- v differing elements: 0
- v max absolute error: 0
- next conv-state differing elements: 0
- next conv-state max absolute error: 0

Therefore the tested FP16 fused prework is bit-exact against
the stock FP16 composed path for all directly compared
q/k/v/conv-state tensors.

The P58J synchronized comparator intentionally perturbed
runtime timing and must not be used as a performance result.

P58 conclusion:

The existing Qwen3.5 fused GDN target-verify prework kernel
was unnecessarily unavailable to the FP16 27B model because
of BF16-only Python gating.

Extending the route to FP16 is both:

- performance-certified at 30K:
  +2.37% paired TG / -2.460 ms per cycle

and

- directly numerically certified over the tested 96-call
  coverage:
  bit-exact q/k/v/next-conv-state tensors

The certified implementation is preserved as:

experiments/p51-q8-verifier/patches/
0011-p58-fp16-gdn-verify-prework.patch

The preserved patch remains environment gated:

OMLX_GDN_VERIFY_PREWORK_FP16=1

Current installed oMLX source is restored to the unmodified
package version after experimentation.

Next:

Integrate the certified FP16 GDN route with the existing
P54F D3/M4 policy and measure a fresh absolute 30K champion
under a stable session.

After that, resume structural context-length work on the
remaining 16 full-attention KV scans rather than reopening
speculative-depth routing.

## Current handoff — post-P58

Current checkpoint:

- branch: project51-q8-verifier
- commit: 52c1efd
- P58 FP16 fused GDN verifier prework certified
- preserved patch:
  experiments/p51-q8-verifier/patches/
  0011-p58-fp16-gdn-verify-prework.patch

Immediate next phase: P59.

P59 goal:

Integrate the certified P58 FP16 GDN route with the exact
P54F D3/M4 verifier policy and establish a fresh absolute
29,297-token / 512-output champion.

Enable:

OMLX_GDN_VERIFY_PREWORK_FP16=1

Keep the existing P54F routing unchanged.

Historical P54F 30K reference:

- 18.504 tok/s mean
- 147.128 ms/backbone-cycle
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

P58I certified paired kernel delta:

- +2.37% realized decode throughput
- -2.460 ms/backbone-cycle

A simple projection puts P59 near 18.9 tok/s, but P59 must
measure the absolute result rather than assume the paired
delta transfers arithmetically.

Current 30K target ladder:

- P59 integrated P58:
  ~18.9 tok/s center
- next structural attention phase:
  ~20 tok/s 50% target
- mature verifier stack:
  ~21-22 tok/s
- broader mature MXFORGE:
  ~22.5-24 tok/s 50% region
- ~25+ requires another major architectural win

All of these targets refer to the real ~29.3K-context
benchmark.

Do not compare them directly with the historical ~27.6-29
tok/s Q6-ish champions, which were short/low-context runs.

### P60 priority after P59

The leading next structural target is specialized long-KV
verifier attention for the exact Qwen3.8 geometry:

- verifier M=4 / q_len=4
- GQA=6
- head_dim=256
- 16 full-attention layers
- long KV history

The existing qwen35_verify_sdpa_split path already fits all
four M4 verifier rows into one vector-SDPA dispatch per
full-attention layer.

Therefore do NOT revisit the already-solved idea of merely
combining four row-wise SDPA calls.

Instead investigate:

- reuse K/V loads across GQA query heads;
- reuse KV work across M4 verifier rows where practical;
- split long sequence/KV work to improve M1 GPU occupancy;
- specialize around GQA6 + hd256 + M4;
- reduce memory traffic from the 16 growing KV-history scans.

Recent upstream MLX work titled:

"Read each K/V byte once in gqa-8 decode attention"

is a high-value architecture lead. It is not directly
applicable because it targets GQA8 / single-token decode,
but its K/V-reuse strategy should be mined for a
GQA6/M4 verifier-specific Metal implementation.

A recent upstream force_fused SDPA option may also be useful
as a diagnostic/assertion tool. Confirm installed MLX support
before relying on it.

### Later Qwen workstreams

After the attention path:

1. LM-head / MTP-module specialization
   - reduced draft vocabulary from measured output usage
   - specialized quant/layout
   - lower-overhead sampling

2. Custom MTP head
   - P57 closed adaptive depth, not head optimization
   - retain D3/M4 and try to improve acceptance / reduce
     verifier cycle count

3. Prefix-cache/session discipline
   - stable serialization
   - exact prefix reuse
   - session affinity
   - cached/new-token telemetry

4. Heterogeneous ANE/GPU prompt processing

5. Adaptive mixed-precision KV / Geodesia-inspired work
   only after the core attention/verifier path stabilizes

6. M1-specific hardware-aware quant/layout search

Recent DS4, 5070-sidecar, adaptive-waterfall, Geodesia-KV,
and ReasonMaxxer research notes remain separate future
workstreams under docs/research and should be treated as
architecture sources rather than mixed into P59.

### Experiment safety

When temporarily modifying installed oMLX Python source,
create and execute a /tmp/*.sh script with cleanup traps in
the bash subprocess.

Do not rely on EXIT traps pasted directly into interactive
zsh.

Next action:

Run P59 integrated absolute 30K certification.

## P59 — Integrated FP16 GDN absolute 30K certification

P59 integrated the certified P58 FP16 fused GDN verifier
prework with the exact P54F D3/M4 routing policy.

Policy:

- fixed D3 / verifier M=4
- ALL-MEDIUM verifier routing
- 5120x6144: K_PARTS=1
- 5120x17408: K_PARTS=1
- remaining regular routed projections: default K_PARTS=2
- lm_head NSG8 / BN4
- OMLX_GDN_VERIFY_PREWORK_FP16=1
- frozen 29,297-token / 512-output ruler

P59 absolute four-run result:

- run 1:
  - 17.069 tok/s
  - 153.597 ms/backbone-cycle
- run 2:
  - 16.952 tok/s
  - 154.801 ms/backbone-cycle
- run 3:
  - 17.019 tok/s
  - 154.244 ms/backbone-cycle
- run 4:
  - 17.001 tok/s
  - 154.230 ms/backbone-cycle

Mean:

- 17.010 tok/s
- TG SD 0.048
- 154.218 ms/backbone-cycle
- BPC SD 0.492
- best observed TG 17.069 tok/s

Every run retained exactly:

- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe
- fused FP16 GDN engagement

This did not beat the historical P54F absolute certification:

- P54F mean: 18.504 tok/s
- P54F BPC: 147.128 ms/cycle

However, the P59 session was clearly slower globally and could
not distinguish integration performance from system/session drift.

### P59B — same-session drift control

P59B therefore repeated the exact P54F stack in a balanced
same-session FP16 GDN OFF/ON comparison.

Order:

- BASE-1
- FUSED-1
- FUSED-2
- BASE-2

BASE:

- 17.940 tok/s / 149.673 ms/cycle
- 18.054 tok/s / 149.756 ms/cycle
- mean 17.997 tok/s
- mean 149.715 ms/cycle

FUSED:

- 18.229 tok/s / 147.892 ms/cycle
- 18.486 tok/s / 146.472 ms/cycle
- mean 18.358 tok/s
- mean 147.182 ms/cycle

Same-session fused delta:

- +2.00% realized TG
- -2.532 ms/backbone-cycle

For comparison, P58I certified:

- +2.37% realized TG
- -2.460 ms/backbone-cycle

Therefore P59B reproduces the P58 kernel-side result extremely
closely.

All four P59B runs retained exactly:

- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

Fused GDN engaged only in the FUSED arm.

P59 conclusion:

- P58 FP16 GDN integration: PASS
- deterministic trajectory: PASS
- same-session performance transfer: PASS
- new absolute 30K champion: NOT ESTABLISHED

The failed absolute P59 result is dominated by session/system
performance drift rather than by an integration regression.

The historical absolute 30K certification remains:

- P54F: 18.504 tok/s mean

The preferred structural verifier stack now includes the
certified P58 FP16 GDN fusion.

Do not spend additional tuning cycles chasing an absolute P59
number in a drifting machine session.

Proceed to P60 structural long-KV verifier attention work using
paired or same-session controls.

## P60 — Long-KV verifier attention

P60 targets the remaining 16 full-attention layers.

Exact verifier geometry established before P60:

- verifier M=4 / q_len=4
- 24 query heads
- 4 KV heads
- GQA factor=6
- head_dim=256
- 16 full-attention layers
- long growing KV history

The existing qwen35 verifier SDPA split path already fits all
four verifier rows into one vector-SDPA dispatch per full-attention
layer.

Therefore P60 must not revisit merely combining four row-wise
attention calls.

P60A first audits:

- exact installed qwen35 verifier-SDPA wrapper
- installed MLX version and SDPA API
- whether force_fused is available
- whether the local MLX source contains the newly merged
  GQA K/V-reuse kernel
- exact current vector-SDPA dispatch constraints for
  q_len=4 / GQA6 / head_dim=256

Only after that audit should P60B alter or benchmark attention
kernel structure.

## P60B-D — SDPA block geometry and trajectory search

P60A established the exact full-attention verifier path:

- q_len=4
- 24 query heads
- 4 KV heads
- GQA=6
- head_dim=256
- 16 full-attention layers
- ~29.3K KV at the frozen ruler

The installed qwen35_verify_sdpa_split patch sends the full
M4 verify block through MLX vector SDPA because:

q_len * GQA = 4 * 6 = 24 <= 32

At long KV length this selects sdpa_vector_2pass.

The local MLX tree does not contain the newer upstream
sdpa_vector_2pass_1_gqa K/V-reuse kernel.

### P60B — attention-only block-count scout

Exact synthetic geometry:

- B=1
- QH=24
- KVH=4
- q_len=4
- kv_len=29297
- D=256
- FP16

AUTO bookend median:

- 2.0844 ms

Explicit block medians:

- B16:  2.6150 ms
- B32:  2.2077 ms
- B64:  1.9927 ms
- B128: 2.0087 ms
- B256: 2.0939 ms
- B512: 2.1293 ms

B64 therefore showed:

- +4.60% attention-kernel speed
- estimated -1.468 ms/backbone-cycle across 16 layers

AUTO output was bit-identical to B256, confirming that the
M1 Max / ~29K / M4 geometry automatically selects 256 blocks.

### P60C — B64 integrated certification

Balanced 4+4 results:

AUTO:

- mean 18.043 tok/s
- mean 149.536 ms/backbone-cycle
- always 186 cycles
- always accept 325/442
- hash 101ae2aec9793dfe

B64:

- mean 17.230 tok/s
- mean 147.892 ms/backbone-cycle
- always 197 cycles
- always accept 315/452
- hash f46220cfe4923fc1

Raw kernel/backbone result:

- -1.644 ms/cycle

Realized throughput:

- -4.50%

Therefore the P60B kernel saving transferred almost exactly,
but changing the SDPA block reduction tree perturbed floating
point decisions enough to degrade speculative acceptance and
add 11 verifier cycles.

B64 is rejected.

### P60D — trajectory-safe block hunt

Results:

AUTO-A:
- 18.092 tok/s
- 149.236 ms/cycle
- 186 cycles
- 325/442
- hash 101ae2aec9793dfe

B128:
- 18.093 tok/s
- 148.278 ms/cycle
- 187 cycles
- 325/442
- hash f42ac9dd2bdf9d5a

B192:
- 18.063 tok/s
- 148.554 ms/cycle
- 187 cycles
- 325/442
- hash f42ac9dd2bdf9d5a

B160:
- 17.250 tok/s
- 148.551 ms/cycle
- 196 cycles
- 316/450
- hash f46220cfe4923fc1

B224:
- 17.205 tok/s
- 148.885 ms/cycle
- 196 cycles
- 316/450
- hash f46220cfe4923fc1

B96:
- 18.099 tok/s
- 149.072 ms/cycle
- 186 cycles
- 325/442
- hash 101ae2aec9793dfe

AUTO-B:
- 18.057 tok/s
- 149.463 ms/cycle
- 186 cycles
- 325/442
- hash 101ae2aec9793dfe

AUTO bookend mean:

- 18.074 tok/s
- 149.350 ms/cycle

Only B96 retained the exact historical trajectory.

B96 delta:

- +0.14% TG
- -0.278 ms/cycle

Conclusion:

The block-count search is closed.

There is real attention headroom, but the large wins from
reducing pass-1 blocks change the floating-point reduction
tree and destabilize speculative acceptance.

Do not promote a global MLX_SDPA_BLOCKS override.

The next kernel must instead preserve the native 256-block
partial-reduction topology while reducing redundant K/V reads.

### P60E target

Build an exact verifier specialization for:

- FP16
- q_len=4
- GQA=6
- head_dim=256
- causal
- no sinks
- no array mask
- long KV

First scout: HPT2.

Each SIMD group computes two query-head/row combinations from
one K/V load, while each query accumulator still processes:

block_idx,
block_idx + blocks,
block_idx + 2*blocks,
...

in the exact existing order.

The second-pass aggregation and 256-block topology stay
unchanged.

Goal:

reduce redundant K/V traffic without changing the frozen
186-cycle / 325-of-442 / 101ae2aec9793dfe trajectory.

## P60E-G — HPT2 verifier attention certification

P60B-D demonstrated that reducing the native 256-block
two-pass SDPA reduction topology can expose meaningful
attention speed, but also changes floating-point reductions
enough to perturb speculative acceptance.

The custom-kernel work therefore retained:

- native 256 pass-1 blocks
- existing second-pass aggregation
- the same per-output token visitation order

while reducing redundant K/V reads.

### P60E — HPT2 attention-only kernel

An isolated MLX worktree was built at:

/tmp/p60e-mlx-hpt2

The specialized route targets the exact verifier geometry:

- FP16 certified workload
- batch 1
- q_len=4
- 24 query heads
- 4 KV heads
- GQA=6
- head_dim=256
- causal
- no sinks
- no array mask
- long KV

The route is environment gated:

MLX_SDPA_GQA6_M4_HPT2=1

and was tested with the native:

MLX_SDPA_BLOCKS=256

HPT2 keeps two query/row accumulators in registers and
reuses each K/V load across both while preserving each
individual accumulator's original token-processing order.

Exact 29,297-KV microbenchmark:

BASE mean-of-bookend medians:

- 2.0653 ms

HPT2 mean-of-bookend medians:

- 1.8274 ms

Kernel speedup:

- +13.01%

Estimated 16-layer effect:

- approximately -3.805 ms/backbone-cycle

All BASE and HPT2 outputs had exactly the same hash:

c37c1d739e0a90b0

Therefore the tested exact attention call was bit-exact.

A later preflight reproduced:

- BASE 2.0721 ms
- HPT2 1.8418 ms
- identical c37c1d739e0a90b0 hash

### P60F — integrated 2+2 scout

Both arms used the same isolated rebuilt MLX and explicitly
used 256 SDPA blocks.

Only:

MLX_SDPA_GQA6_M4_HPT2

changed between arms.

BASE:

- 18.060 tok/s / 149.428 ms/cycle
- 18.095 tok/s / 149.195 ms/cycle
- mean 18.078 tok/s
- mean 149.312 ms/cycle

HPT2:

- 18.650 tok/s / 144.856 ms/cycle
- 18.684 tok/s / 144.652 ms/cycle
- mean 18.667 tok/s
- mean 144.754 ms/cycle

Paired result:

- +3.26% TG
- -4.558 ms/backbone-cycle

Every run retained exactly:

- 186 cycles
- accept 325/442
- 73.5% acceptance
- hash 101ae2aec9793dfe

### P60G — balanced 4+4 certification

Order:

- BASE-1
- HPT2-1
- HPT2-2
- BASE-2
- HPT2-3
- BASE-3
- BASE-4
- HPT2-4

BASE runs:

- 18.093 tok/s / 149.149 ms/cycle
- 18.076 tok/s / 149.309 ms/cycle
- 18.066 tok/s / 149.395 ms/cycle
- 18.053 tok/s / 149.485 ms/cycle

BASE mean:

- 18.072 tok/s
- TG SD 0.017
- 149.335 ms/backbone-cycle
- BPC SD 0.143

HPT2 runs:

- 18.677 tok/s / 144.734 ms/cycle
- 18.687 tok/s / 144.632 ms/cycle
- 18.669 tok/s / 144.754 ms/cycle
- 18.658 tok/s / 144.770 ms/cycle

HPT2 mean:

- 18.672 tok/s
- TG SD 0.012
- 144.722 ms/backbone-cycle
- BPC SD 0.062

Certified paired delta:

- +3.32% realized TG
- -4.612 ms/backbone-cycle
- approximately 857.8 ms target-backbone time removed
  across 186 verifier cycles

All eight P60G runs retained exactly:

- 186 cycles
- accept 325/442
- 73.5% acceptance
- hash 101ae2aec9793dfe

This establishes a bit-stable structural verifier-attention
win rather than a speculative-trajectory effect.

### Absolute champion

Historical P54F absolute certification:

- 18.504 tok/s mean
- 147.128 ms/backbone-cycle

P60G HPT2:

- 18.672 tok/s mean
- 144.722 ms/backbone-cycle

Therefore P60G establishes a new measured 30K champion mean:

- +0.91% TG versus historical P54F
- -2.406 ms/cycle versus historical P54F

This is especially notable because the same-session P60G
BASE mean was only 18.072 tok/s, confirming that the HPT2
structural delta survives a globally slower session.

### P60 conclusion

The long-KV verifier attention path had substantial redundant
K/V traffic even after consolidating M4 into one vector-SDPA
dispatch.

A specialized HPT2 pass-1 kernel removes enough redundant
K/V loading to produce:

- +13.01% exact attention-call speed
- +3.32% certified end-to-end TG
- -4.612 ms/backbone-cycle

while preserving both:

- exact tested attention output
- exact frozen speculative trajectory

The implementation is preserved as:

experiments/p51-q8-verifier/patches/
0012-p60-hpt2-m4-gqa6-sdpa.patch

and is promoted into the project branch source.

Current preferred 30K verifier stack:

- fixed D3
- verifier M=4
- P54F QMM routing
- lm_head NSG8 / BN4
- P58 FP16 fused GDN verifier prework
- native 256-block vector SDPA topology
- P60 HPT2 M4/GQA6/hd256 K/V-reuse attention kernel

Current measured 30K champion:

- 18.672 tok/s mean
- 144.722 ms/backbone-cycle
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

Next attention optimization should retain the same numerical
discipline. Candidate geometry work should preserve each
accumulator's arithmetic order and compare alternative HPT2
pairings before increasing register pressure substantially.

## P61 — head-paired HPT2 refinement

P60 established that HPT2 K/V reuse is a major,
bit-stable verifier-attention optimization.

P61 tested whether the same HPT2 register pressure could
be used more efficiently by changing only the pairing
topology.

### Mapping

P60 ROWPAIR pairs two M4 rows belonging to the same
query head.

P61 HEADPAIR instead pairs two GQA query heads at the same
M4 row.

Both mappings retain:

- HPT=2
- 12 SIMD groups instead of the native 24
- native 256 pass-1 blocks
- unchanged pass-2 aggregation
- unchanged per-accumulator token visitation order

HEADPAIR additionally gives each paired accumulator the
same causal cutoff.

The experimental gate is:

MLX_SDPA_GQA6_M4_HPT2_HEADPAIR=1

ROWPAIR remains available through:

MLX_SDPA_GQA6_M4_HPT2=1

HEADPAIR takes precedence when both are requested.

### P61A — exact attention microbenchmark

Exact verifier geometry:

- batch 1
- q_len=4
- 24 query heads
- 4 KV heads
- GQA=6
- KV length 29,297
- head_dim=256
- FP16
- causal
- 256 pass-1 blocks

Balanced results:

BASE:

- 2.0815 ms mean-of-bookend medians

ROWPAIR:

- 1.8439 ms
- +12.88% versus BASE

HEADPAIR:

- 1.8189 ms
- +14.43% versus BASE
- +1.37% versus ROWPAIR

Projected additional HEADPAIR saving versus ROWPAIR:

- approximately 0.400 ms/backbone-cycle

All outputs retained the exact attention hash:

c37c1d739e0a90b0

Therefore HEADPAIR remained bit-exact.

### P61B — integrated 2+2 scout

ROWPAIR:

- 18.693 tok/s / 144.548 ms/cycle
- 18.690 tok/s / 144.620 ms/cycle
- mean 18.691 tok/s
- mean 144.584 ms/cycle

HEADPAIR:

- 18.728 tok/s / 144.278 ms/cycle
- 18.735 tok/s / 144.272 ms/cycle
- mean 18.731 tok/s
- mean 144.275 ms/cycle

Paired delta:

- +0.21% TG
- -0.309 ms/backbone-cycle

Every run retained exactly:

- 186 cycles
- accept 325/442
- 73.5% acceptance
- hash 101ae2aec9793dfe

### P61C — balanced 4+4 certification

ROWPAIR runs:

- 18.700 tok/s / 144.575 ms/cycle
- 18.696 tok/s / 144.566 ms/cycle
- 18.669 tok/s / 144.685 ms/cycle
- 18.681 tok/s / 144.579 ms/cycle

ROWPAIR mean:

- 18.686 tok/s
- TG SD 0.014
- 144.601 ms/backbone-cycle
- BPC SD 0.056

HEADPAIR runs:

- 18.717 tok/s / 144.401 ms/cycle
- 18.741 tok/s / 144.188 ms/cycle
- 18.727 tok/s / 144.331 ms/cycle
- 18.739 tok/s / 144.134 ms/cycle

HEADPAIR mean:

- 18.731 tok/s
- TG SD 0.011
- 144.263 ms/backbone-cycle
- BPC SD 0.124

Certified HEADPAIR delta versus same-session ROWPAIR:

- +0.24% TG
- -0.338 ms/backbone-cycle

Across 186 cycles this removes approximately:

- 62.9 ms additional target-backbone time

All eight runs retained exactly:

- 186 cycles
- accept 325/442
- 73.5% acceptance
- hash 101ae2aec9793dfe

### Champion update

Previous certified P60 ROWPAIR champion:

- 18.672 tok/s mean
- 144.722 ms/backbone-cycle

P61C HEADPAIR:

- 18.731 tok/s mean
- 144.263 ms/backbone-cycle

P61 therefore establishes a new measured 30K champion mean:

- 18.731 tok/s

and replaces ROWPAIR as the preferred HPT2 mapping.

### P61 conclusion

The large P60 gain came primarily from reducing redundant
K/V reads through HPT2.

P61 shows that pairing query heads at the same M4 row is
slightly more efficient than pairing adjacent M4 rows,
without increasing HPT or register pressure.

Current preferred verifier attention route:

- q_len=4
- GQA=6
- head_dim=256
- native 256-block two-pass topology
- HPT2
- same-row adjacent-query-head K/V reuse

Implementation delta preserved as:

experiments/p51-q8-verifier/patches/
0013-p61-headpair-hpt2-sdpa.patch

Current preferred 30K verifier stack:

- fixed D3
- verifier M=4
- P54F QMM routing
- lm_head NSG8 / BN4
- P58 FP16 fused GDN verifier prework
- native 256-block vector SDPA topology
- P61 HEADPAIR HPT2 M4/GQA6/hd256 attention

Current measured 30K champion:

- 18.731 tok/s mean
- 144.263 ms/backbone-cycle
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

The next attention experiment may increase HPT, but should
continue to preserve the native 256-block reduction topology
and exact per-accumulator arithmetic order.

## P62 — HPT3 reuse frontier

P62 tested whether verifier-attention K/V reuse could be
extended beyond the certified P61 HPT2 same-row head-pair
mapping.

The experimental kernel used:

- batch 1
- q_len=4
- 24 query heads
- 4 KV heads
- GQA=6
- head_dim=256
- FP16
- causal
- KV length 29,297
- native 256 pass-1 blocks
- unchanged pass-2 aggregation
- unchanged per-accumulator arithmetic order

P62 HPT3 grouped three GQA query heads at the same M4 row.

This reduced logical SIMD groups from:

- native: 24
- HPT2: 12
- HPT3: 8

but increased live per-SIMD accumulator state from two query
outputs to three.

### P62A exact attention microbenchmark

Balanced results:

BASE-A:

- median 2.0905 ms
- hash c37c1d739e0a90b0

HPT2-A:

- median 1.8175 ms
- hash c37c1d739e0a90b0

HPT3-A:

- median 3.9791 ms
- hash c37c1d739e0a90b0

HPT3-B:

- median 3.9769 ms
- hash c37c1d739e0a90b0

HPT2-B:

- median 1.8260 ms
- hash c37c1d739e0a90b0

BASE-B:

- median 2.0838 ms
- hash c37c1d739e0a90b0

Mean of balanced medians:

- BASE: 2.0872 ms
- HPT2 HEADPAIR: 1.8217 ms
- HPT3: 3.9780 ms

Relative performance:

- HPT2 versus BASE: +14.57%
- HPT3 versus BASE: -47.53%
- HPT3 versus HPT2: -54.21%

All six outputs retained exactly:

c37c1d739e0a90b0

Therefore HPT3 is numerically bit-exact, but its performance
is catastrophically worse.

16-layer projection:

- HPT2 saving versus BASE:
  approximately 4.247 ms/backbone-cycle

- HPT3 versus BASE:
  approximately -30.254 ms/backbone-cycle

- HPT3 incremental versus HPT2:
  approximately -34.501 ms/backbone-cycle

### P62 conclusion

At head_dim=256 on the M1 Max vector-SDPA kernel, HPT3
crosses the useful K/V-reuse versus register-pressure /
occupancy frontier.

The exactness result proves that the regression is not due
to changed arithmetic or speculative behavior.

HPT2 HEADPAIR remains the preferred verifier-attention
geometry.

Do not test HPT4 on this kernel geometry.

Attention HPT search is closed at:

- HPT=2
- same M4 row
- two adjacent GQA query heads
- native 256-block reduction topology

No P62 source changes are promoted.

Canonical champion remains P61:

- 18.731 tok/s mean
- 144.263 ms/backbone-cycle
- 186 cycles
- accept 325/442
- hash 101ae2aec9793dfe

Next workstream:

Audit the MTP module and lm-head path for the next
structural verifier/decode optimization.

## P63 — MTP acceptance diagnosis

P63 shifted optimization focus from raw MTP latency to speculative
acceptance / cycle reduction.

### P63A/B — architecture and budget audit

Representative fixed-D3 P61 budget at ~30K context:

- backbone: 144.328 ms/cycle
- MTP: 1.828 ms/cycle
- sampling: 0.032 ms/cycle
- cache: 0.430 ms/cycle
- backbone / MTP ratio: ~78.95x

Frozen trajectory:

- 512 emitted tokens
- 186 verify cycles
- 325 / 442 drafts accepted = 73.5%
- 2.753 emitted tokens/cycle
- D1: 155 / 186 = 83.33%
- D2: 101 / 155 = 65.16%
- D3: 69 / 101 = 68.32%

Conclusion: shaving MTP compute has limited leverage. Avoiding even a
small number of ~144 ms backbone verify cycles can be more valuable.

Qwen3.5 MTP architecture audit established:

- one full-attention MTP transformer layer
- hidden size 5120
- MTP hidden ultimately feeds the same target LM head
- vocabulary size 248320
- greedy verifier contains both target ids and the exact MTP draft
  distributions needed for observational recoverability telemetry

### P63C — greedy recoverability telemetry

Exact frozen generation was preserved:

- cycles: 186
- accept: 325 / 442
- hash: `101ae2aec9793dfe`

All 117 true rejection frontiers were measured.

Target rank under the MTP distribution at rejection:

- rank <= 2: 44 / 117 = 37.6%
- rank <= 4: 70 / 117 = 59.8%
- rank <= 8: 81 / 117 = 69.2%
- rank <= 16: 98 / 117 = 83.8%

This is a strong near-miss signal: the MTP head is often near the
target token even when top-1 is wrong.

### P63D — confusion structure

The near misses are contextual rather than a reusable vocabulary
confusion table:

- 117 rejection frontiers
- 116 unique draft -> target pairs
- only one pair repeated
- all 44 rank-2 draft -> target pairs were unique

Conclusion:

- reject fixed token-bias / confusion-table correction
- investigate representation / chain-state quality instead

### P63E-v3c — complete aligned hidden-state capture

After correcting diagnostic instrumentation, P63E captured every
conditional draft position:

- artifact shape: 442 x 5120 MTP hidden
- paired target hidden: 442 x 5120
- skipped cycles: 0
- exact depth counts: D1=186, D2=155, D3=101
- exact rejection count: 117
- exact P63C rank totals reproduced
- exact frozen output hash: `101ae2aec9793dfe`

Diagnostic artifact SHA256:

`aab731da83b7bdd21a1c92d87290303d03b15cd1a1d3219050167b2d7e28d9b2`

P63E diagnostic TPS is NOT a performance result because hidden capture
adds synchronization and host copies.

Accepted-row MTP/target cosine by chain depth:

- D1: 0.597302
- D2: 0.526064
- D3: 0.459056
- D3 - D1: -0.138247

This is a strong depth-drift signal.

However, the aggregate accept/reject hidden-distance comparison was
depth-confounded and must not be interpreted as a direct acceptance
classifier.

### P63F — depth-deconfounded hidden geometry

Within-depth accept/reject discrimination:

- mean cosine AUC: 0.463879
- mean relative-L2 AUC: 0.417010

Per depth:

- D1 cosine AUC: 0.4458
- D2 cosine AUC: 0.5319
- D3 cosine AUC: 0.4139

Therefore generic MTP -> target hidden closeness does NOT reliably
predict acceptance once chain depth is controlled.

Among rejected rows, representation error still has a moderate
relationship with confidence error:

- depth-demeaned gap vs 1-cos: +0.287112
- depth-demeaned rank vs 1-cos: +0.224417
- depth-demeaned gap vs relative-L2: +0.2528

Residual structure is not strongly low-rank.

Depth-specific centered PCA top-8 variance:

- D1: 19.23%
- D2: 19.20%
- D3: 23.30%

This rejects the current hypothesis that a tiny rank-8 residual adapter
captures most MTP hidden error.

There IS a substantial shared mean residual component.

Mean residual direction strength:

- D1: 0.395953
- D2: 0.349624
- D3: 0.353347

Equivalent mean-residual share of uncentered residual energy:

- D1: ~15.68%
- D2: ~12.22%
- D3: ~12.49%

Mean residual direction cosine:

- D1 / D2: +0.885495
- D1 / D3: +0.769328
- D2 / D3: +0.935171

This is a plausible global-bias correction seam.

The strongest self-chain evidence comes from centroid drift.

Draft centroid cross-depth cosine:

- D1 / D2: +0.939025
- D1 / D3: +0.856822
- D2 / D3: +0.950443

Target centroid cross-depth cosine:

- D1 / D2: +0.986943
- D1 / D3: +0.973139
- D2 / D3: +0.981485

The target representation remains highly stable across depth while the
MTP draft representation drifts substantially more, especially D1->D3.

### P63 conclusion

P63 establishes:

1. Acceptance/cycle reduction is materially higher-leverage than raw
   MTP latency optimization for this workload.
2. Most rejected target tokens are already relatively near the top of
   the MTP distribution.
3. Misses are contextual, not a small repeated vocabulary-confusion
   table.
4. MTP representation changes strongly with self-chain depth while the
   target representation is comparatively stable.
5. Generic hidden distance is not a direct accept/reject classifier.
6. Residual variation is too distributed to justify a rank-8 adapter
   from this single ruler.
7. A substantial and similarly oriented mean residual component exists
   across D1/D2/D3.

Preferred next experiment:

**P64A — offline shared-LM-head residual replay**

Using the frozen P63E hidden artifact, replay the shared LM head after
adding scaled residual corrections and measure target-rank / top-1
recovery without changing runtime generation.

Compare at minimum:

- no correction
- one global mean residual direction
- depth-specific mean residual directions
- conservative scale sweep around zero

Do not train a learned adapter yet.

Any correction must first demonstrate held-out / multi-prompt
generalization before an integrated speculative-decoding experiment.

### Champion remains unchanged

P61 HEADPAIR HPT2 remains the certified absolute champion:

- TG: 18.731 tok/s
- BPC: 144.263 ms/cycle
- cycles: 186
- acceptance: 325 / 442
- hash: `101ae2aec9793dfe`

Preferred structural stack remains:

- P58 FP16 GDN
- fixed P54F D3 / M4 verifier policy
- native 256 SDPA blocks
- P61 HEADPAIR HPT2 attention reuse
- exact frozen speculative trajectory

## P64 — Offline shared-LM-head residual replay

P64A tested the shared mean-residual seam identified by P63
without altering runtime generation.

The frozen P63E artifact was first validated exactly:

- artifact shape: 442 x 5120
- D1 / D2 / D3 rows: 186 / 155 / 101
- exact artifact SHA256:
  aab731da83b7bdd21a1c92d87290303d03b15cd1a1d3219050167b2d7e28d9b2

The exact Q8 / GS64 shared target LM head was replayed from:

- vocabulary: 248320
- packed weight shape: 248320 x 1280
- Q8
- group size 64

Before testing any correction, P64A reproduced every important
P63 invariant:

- baseline top-1: 325 / 442
- rejection count: 117
- replay acceptance mask exactly matched the captured mask
- replay draft tokens exactly matched captured draft IDs
- rejection target-rank census exactly reproduced:
  - rank <= 2: 44
  - rank <= 4: 70
  - rank <= 8: 81
  - rank <= 16: 98

This establishes the offline shared-LM-head replay as faithful
to the captured MTP distributions.

Mean residual L2 norms:

- global: 47.8147
- D1: 49.8812
- D2: 48.9386
- D3: 52.3359

P64A swept additive corrections using:

- one global mean residual
- depth-specific mean residuals
- alpha:
  - -0.50
  - -0.25
  - 0
  - 0.125
  - 0.25
  - 0.50
  - 0.75
  - 1.00

Both full-data replay and stratified 5-fold held-out replay
were measured.

Best full-data result:

- global alpha=0.25
- top-1: 326 / 442
- recovered rejections: 2
- broken accepts: 1
- net: +1

This tiny in-sample gain did not survive held-out replay.

Best CV5 result:

- alpha=0
- top-1: 325 / 442
- net: 0

Representative nonzero CV5 results:

- global alpha=0.25:
  - top-1 325 / 442
  - recovered 1
  - broken 1
  - net 0

- depth alpha=0.50:
  - top-1 325 / 442
  - recovered 3
  - broken 3
  - net 0

Larger positive corrections increasingly damaged already-correct
drafts.

At alpha=1.0:

- global CV5: 317 / 442, net -8
- depth CV5: 317 / 442, net -8

Conclusion:

The shared mean residual observed in P63 is real geometric
structure, but a simple additive mean correction is not a useful
MTP decision correction.

P64A is therefore rejected.

Do not integrate either:

- global mean-residual correction
- depth-specific mean-residual correction

into live speculative generation.

The failure also removes the rationale for collecting additional
prompts merely to validate this specific additive-mean hypothesis.

Preserved P64 artifacts:

- p64a-residual-replay.json
  SHA256:
  453082b4c61077b94482448ad89330e275d860073f11b0eab340ae7263e3a508

- p64a-mean-residuals.npz
  SHA256:
  aec5fae15dba7e5443ff9638abdf01177fd980d61cce8bbfe3d4ecfa48d37538

Champion remains P61 HEADPAIR HPT2:

- TG: 18.731 tok/s
- BPC: 144.263 ms/cycle
- cycles: 186
- acceptance: 325 / 442
- hash: 101ae2aec9793dfe

The high-value P63 near-miss observation remains:

- 44 / 117 rejection frontiers have target rank <= 2
- 70 / 117 have target rank <= 4

Therefore the next experiment moves from global hidden correction
to selective candidate branching.

### P65A target

Measure whether rank-2-recoverable rejection frontiers are
concentrated among low-confidence MTP predictions.

Replay the exact shared LM head and capture:

- top-1 token
- top-2 token
- top-1 minus top-2 logit margin

Then evaluate selective top-2 branching at increasing branch
budgets.

The key question is whether a small low-margin subset captures
a large fraction of the 44 rank-2 rejection frontiers.

If so, selective top-2 / tree speculative decoding may be
higher leverage than modifying the MTP representation itself.

Do not implement live tree speculation until this offline
branchability scout establishes a useful confidence gate.

## P65 — Selective top-2 branchability

P65A tested whether the strong P63 rank-2 near-miss population
can be selected using MTP confidence rather than modifying the
MTP hidden representation.

The exact P63E artifact and exact Q8 / GS64 shared LM head were
replayed.

Invariants reproduced:

- all 442 MTP top-1 draft IDs exactly matched
- all 44 P63 rank-2 rejection rows were exactly:
  target token == replayed MTP top-2 token

Margin definition:

- MTP top-1 logit minus top-2 logit
- smaller margin = lower MTP confidence

Margin distributions:

Accepted rows:

- n=325
- p10=0.89062
- p25=2.23438
- median=4.31250
- p75=8.53125
- p90=12.02813
- mean=5.75430

All rejected rows:

- n=117
- p10=0.17188
- p25=0.62500
- median=1.21875
- p75=2.23438
- p90=3.67500
- mean=1.68864

Rank-2 recoverable rejects:

- n=44
- p10=0.20937
- p25=0.67188
- median=1.29688
- p75=1.89062
- p90=3.41641
- mean=1.61310

Other rejected rows:

- n=73
- p10=0.17500
- p25=0.60938
- median=1.21875
- p75=2.23438
- p90=3.85625
- mean=1.73416

Observed discrimination:

- low margin -> rank-2 recoverable:
  AUC 0.7601

- low margin -> any rejection:
  AUC 0.8132

Selective low-margin branching results:

5% budget:

- branch 22 / 442 rows
- catch 5 / 44 rank-2 opportunities
- recall 11.4%
- branch precision 22.7%

10% budget:

- branch 44 rows
- catch 9 / 44
- recall 20.5%
- precision 20.5%

20% budget:

- branch 88 rows
- catch 18 / 44
- recall 40.9%
- precision 20.5%

25% budget:

- branch 110 rows
- catch 22 / 44
- recall 50.0%
- precision 20.0%

33% budget:

- branch 146 rows
- catch 32 / 44
- recall 72.7%
- precision 21.9%

50% budget:

- branch 221 rows
- catch 38 / 44
- recall 86.4%
- precision 17.2%

Best same-ruler F1 threshold:

- branch 148 / 442 rows = 33.5%
- catch 33 / 44
- precision 22.3%
- recall 75.0%
- F1 0.3437
- margin threshold 1.859375

Interpretation:

P65A establishes a real confidence signal.

However, the rank-2-recoverable and other-rejection margin
distributions are very similar, while accepted and rejected
rows are strongly separated.

Therefore the observed rank-2 AUC may be driven primarily by
MTP rejection prediction rather than by a margin signal that
specifically identifies target-rank-2 events.

This distinction must be measured directly before implementing
live tree speculation.

Important economic correction:

Simply including the MTP top-2 token at a rejection frontier does
not itself save a verifier cycle.

The ordinary greedy verifier already emits the target correction
token when the top-1 draft mismatches.

To improve throughput, an alternate top-2 branch must additionally
provide useful continuation tokens after the corrected token.

Therefore the P65A optimistic cycle-floor numbers are only loose
upper bounds and must not be interpreted as predicted throughput.

The depth location of rank-2 opportunities is important:

- D1 alternate branches can potentially carry D2/D3 continuation
- D2 alternate branches can potentially carry D3 continuation
- D3 alternates have no remaining continuation slot under the
  current fixed-D3 draft depth unless the tree itself extends deeper

Preserved P65A artifact:

p65a-top2-branchability.json

SHA256:

676ec6fa9d9fcfb4dbfabcef55e15e292776c38cce70b35acc9012f1eecf1509

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P65B target

Before any live tree implementation:

1. measure low-margin discrimination for rank-2 recovery
   specifically against other rejected rows;
2. decompose rank-2 opportunities by D1 / D2 / D3;
3. validate low-margin branch budgets using cycle-level
   cross-validation;
4. determine whether enough recoverable opportunity exists at
   D1/D2 to justify an oracle alternate-continuation experiment.

## Project handoff / new-chat protocol

This repository, specifically this STATUS file, is the canonical
persistent handoff for this tuning project.

### Canonical-memory rule

All technical context needed to continue the project MUST be recorded
in this STATUS file at meaningful checkpoints, including as applicable:

- current canonical commit / branch
- certified champion and performance numbers
- fixed experimental policy and environment
- relevant source architecture
- experiment rationale
- exact controls and invariants
- successful and failed experiments
- measured results
- hashes / trajectory identifiers
- accepted and rejected hypotheses
- local artifact locations and SHA256 values when important
- current preferred structural stack
- explicit next experiment
- important cautions / closed search branches

Do not depend on a large chat handoff prompt to carry project state.

If an important fact is needed to resume work in a fresh chat, it
belongs here.

### New-chat rule

New-chat bootstrap prompts should be intentionally minimal.

Normal bootstrap prompt:

`Continue the MLX/oMLX verifier tuning project. Read experiments/p51-q8-verifier/STATUS.md first, verify the current repo checkpoint, and continue from the recorded next experiment.`

That is normally sufficient.

Do NOT reproduce the full project history, benchmark tables, environment
details, or previous experiment summaries in the new-chat prompt.
Those belong in STATUS.md.

### Resume rule for the assistant

At the beginning of a fresh project chat:

1. Read `experiments/p51-q8-verifier/STATUS.md` before designing or
   recommending the next experiment.
2. Treat the STATUS file at the current canonical HEAD as the primary
   project handoff.
3. Verify the repo branch / HEAD / cleanliness before modifying project
   state.
4. Resume from the explicit next experiment recorded in STATUS rather
   than reconstructing project history from chat memory.
5. Preserve the project's existing control, reproducibility, trajectory,
   and experimental-isolation discipline.

If chat context and the canonical STATUS file disagree about an older
project fact, inspect the repo/history and prefer the intentionally
checkpointed repository record unless newer verified evidence exists.

### Checkpoint rule

Before recommending a fresh chat after a meaningful project phase:

1. update STATUS with all information required to resume;
2. preserve important non-Git artifacts and hashes when needed;
3. commit the checkpoint;
4. push it to the fork;
5. verify local HEAD == fork HEAD and the working tree is clean;
6. only then declare it a safe new-chat checkpoint.

The goal is that a fresh chat requires only the minimal bootstrap prompt
above.

### Current resume point

As of the P65A checkpoint, the next phase is:

**P65B — gate-structure / depth / cycle-CV diagnosis**

P65A established a strong MTP confidence signal but did not yet
show that margin specifically distinguishes target-rank-2 misses
from other rejection types.

P65B should resolve that ambiguity and quantify how many rank-2
opportunities occur early enough in the D1/D2 chain to support
useful alternate continuation.
