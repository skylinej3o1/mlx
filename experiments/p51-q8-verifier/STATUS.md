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

### P65B — Gate structure / depth / cycle-CV

P65B resolved whether the P65A low-margin signal specifically
identifies target-rank-2 misses or primarily identifies ordinary
MTP uncertainty / rejection.

All P63/P65A replay invariants remained exact:

- 442 aligned draft rows
- 186 reconstructed verifier cycles
- depth counts:
  - D1: 186
  - D2: 155
  - D3: 101
- 325 accepted drafts
- 117 rejected drafts
- 44 target-rank-2 rejection frontiers

Global discrimination:

- low margin -> any rejection:
  AUC 0.8132

- low margin -> rank-2 versus all other rows:
  AUC 0.7601

- low margin -> rank-2 versus other rejected rows only:
  AUC 0.4983

The final comparison is decisive.

Once analysis is conditioned on rejection, top-1/top-2 margin
contains essentially no information about whether the target token
is specifically MTP rank 2.

Therefore the P65A 0.7601 AUC was primarily induced by the strong
accepted-versus-rejected confidence separation.

Margin should be interpreted as:

- a useful general MTP uncertainty / rejection signal

not as:

- a detector that the correct token is specifically candidate #2

Depth decomposition:

D1:

- rows: 186
- accepted / rejected: 155 / 31
- rank-2 recoverable: 12
- rank-2 share of rejects: 38.7%
- rejection AUC: 0.7982
- rank-2 vs other-reject AUC: 0.6075
- remaining continuation slots under fixed D3: 2

D2:

- rows: 155
- accepted / rejected: 101 / 54
- rank-2 recoverable: 23
- rank-2 share of rejects: 42.6%
- rejection AUC: 0.8619
- rank-2 vs other-reject AUC: 0.5168
- remaining continuation slots: 1

D3:

- rows: 101
- accepted / rejected: 69 / 32
- rank-2 recoverable: 9
- rank-2 share of rejects: 28.1%
- rejection AUC: 0.7749
- rank-2 vs other-reject AUC: 0.3043
- remaining continuation slots: 0

Early-chain opportunity:

- D1 + D2 rank-2 recoverable:
  35 / 44 = 79.5%

Structural upper bound on possible post-alternate continuation
positions:

- D1:
  12 x 2 = 24 positions

- D2:
  23 x 1 = 23 positions

- total:
  47 continuation positions

This 47-position figure is only a structural ceiling.

It does NOT mean 47 tokens can be recovered and does NOT imply
a cycle reduction.

An alternate top-2 branch only becomes useful if, after inserting
the correct target/top-2 token at the rejection frontier, the MTP
head also predicts subsequent target token(s) correctly.

Cycle-level five-fold CV confirmed that the low-margin rejection
gate itself is stable.

Aggregate CV:

10% target budget:

- actual branch fraction: 10.4%
- rank-2 caught: 9 / 44
- precision: 19.6%
- recall: 20.5%

15% target budget:

- actual branch fraction: 16.1%
- rank-2 caught: 15 / 44
- precision: 21.1%
- recall: 34.1%

20% target budget:

- actual branch fraction: 19.9%
- rank-2 caught: 17 / 44
- precision: 19.3%
- recall: 38.6%

25% target budget:

- actual branch fraction: 25.3%
- rank-2 caught: 23 / 44
- precision: 20.5%
- recall: 52.3%

33% target budget:

- actual branch fraction: 33.5%
- rank-2 caught: 32 / 44
- precision: 21.6%
- recall: 72.7%

P65B conclusion:

- confidence / rejection signal: PASS
- rank-2-specific confidence signal: REJECT
- early D1/D2 branch opportunity: PASS
- live tree speculation: NOT YET JUSTIFIED

The candidate architecture is no longer:

"branch because low margin predicts that candidate #2 is right."

It is instead:

"at selected low-confidence draft positions, retain a small alternate
candidate set because rejection risk is high; alternate candidates only
have economic value if their continued MTP branches verify beyond the
correction token."

Preserved artifact:

p65b-gate-structure.json

SHA256:

06875be716b7e953f97a9888d2f4e7b8f31c386ed97ae4d4b992eb39c4ab1074

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P65C target — observational oracle alternate continuation

P65C should remain observational.

At the 35 D1/D2 rejection frontiers where:

- the ordinary MTP top-1 draft is wrong; and
- the target token equals the MTP top-2 candidate;

construct an alternate MTP chain using the known target/top-2 token.

Measure:

D1 frontier:

- whether alternate-conditioned D2 equals the actual next target token
- if yes, whether alternate-conditioned D3 also equals the following
  target token

D2 frontier:

- whether alternate-conditioned D3 equals the actual next target token

Primary output:

- number of D1 rank-2 corrections with +1 valid continuation
- number of D1 rank-2 corrections with +2 valid continuations
- number of D2 rank-2 corrections with +1 valid continuation
- distribution of total alternate branch lengths
- resulting oracle estimate of verifier-cycle reduction potential

Do not change emitted generation.

Do not promote a tree implementation unless P65C demonstrates
meaningful continuation after the alternate correction.

Before implementing P65C, inspect the exact installed oMLX
0.6.3rc2 chain/cache implementation rather than patching against
newer upstream source.

### P65C result — post-correction continuation

P65C instrumented the exact installed oMLX 0.6.3rc2 runtime and
remained fully observational.

Installed source audited before the experiment:

- oMLX 0.6.3rc2
- MLX 0.32.0
- mlx-lm 0.31.3
- batch_generator.py SHA256:
  2aae3666f861a6b4522af343315a4ebdcbde8f4029d1b46ae046aa23bb98289d
- qwen35_model.py SHA256:
  34e74b36bae0f62701a391bc19cc1d75c288424f075f05fa53bc647787b52d33

The Qwen MTP head has a separate trim-capable KV cache and the
runtime provides _clone_mtp_head_cache for detached speculative
copies.

P65C used a clone of committed-only MTP history after the normal
head trim and rebuilt continuation from:

- verifier/backbone hidden rows for the committed prefix; and
- the known target correction token.

No emitted token, backbone cache, persistent MTP cache, normal draft,
or verifier decision was changed.

Frozen trajectory reproduced exactly:

- prompt: 29297 tokens
- completion: 512 tokens
- cycles: 186
- acceptance: 325 / 442 = 73.5%
- D1: 155 / 186
- D2: 101 / 155
- D3: 69 / 101
- output hash: 101ae2aec9793dfe

Exactly the P65B early rank-2 population was observed:

- D1: 12
- D2: 23
- total: 35
- censored: 0

Post-correction continuation:

D1:

- +1 continuation: 8 / 12 = 66.7%
- +2 continuation: 3 / 12 = 25.0%

D2:

- +1 continuation: 22 / 23 = 95.7%

Combined:

- at least one correct continuation:
  30 / 35 = 85.7%
- correct continuation positions:
  33 / 47 = 70.2%
- match-length histogram:
  - 0: 5
  - 1: 27
  - 2: 3

Preserved artifacts:

p65c-oracle-continuation.json

SHA256:

5b7ef8be1f3a238b4a80a98ca04be025b956bbb278f735170c05d01f9c627abb

p65c-oracle-events.jsonl

SHA256:

995701a134d9cbfdceaf60becfd0ec92bdf12c47c757d96c37eaec64e34a3548

Important semantic qualification:

P65C is a strong positive result, but its disposable continuation
was generated AFTER the target verifier had supplied the correction
token and verifier/backbone hidden representation.

Therefore P65C proves:

- a strong post-rejection / post-correction continuation seam

It does NOT yet prove:

- that a top-2 branch generated speculatively BEFORE target
  verification from the MTP's own hidden state will have the same
  continuation quality.

This distinction matters.

The normal MTP self-chain uses the MTP head's own post-norm hidden
state for deeper speculative positions. P65C instead rebuilt committed
history from target/backbone hidden rows after verification.

Thus two candidate architectures now exist:

1. true pre-verify tree speculation:
   generate a top-2 alternate branch during ordinary MTP drafting,
   then verify it jointly or through another efficient verifier form;

2. post-reject rescue:
   after the target reveals a rank-2 correction, immediately exploit
   the unusually high-quality continuation conditioned on that
   correction rather than waiting for a normal full next cycle.

P65D must distinguish these architectures before live integration.

### P65D target — true pre-verify alternate branch

During ordinary MTP chain construction, before the target verifier
runs:

- at D1, retain the MTP top-2 token and build two additional MTP
  continuation predictions from the same parent MTP hidden/cache;
- at D2, retain the MTP top-2 token and build one additional
  continuation prediction from the same parent MTP hidden/cache.

All alternate work must use detached MTP-cache clones.

After the target verifier runs:

- keep only events where the ordinary top-1 rejected and target
  equals the previously generated top-2 candidate;
- compare the already-generated alternate continuation with the
  subsequent real target token stream.

Expected rank-2 event invariants:

- D1: 12
- D2: 23
- total: 35

Primary comparison:

P65C post-correction continuation
versus
P65D true pre-verification MTP-only continuation.

If P65D remains strong, true tree speculation is justified for an
economics / verifier-layout scout.

If P65D collapses while P65C remains strong, defer tree decoding and
pursue a post-reject rescue micro-cycle instead.

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P65D result — true pre-verify tree signal

P65D tested the key semantic distinction left by P65C.

Unlike P65C, P65D generated every alternate candidate and its
continuation BEFORE target verification.

For each D1/D2 parent:

- the ordinary MTP top-1 chain remained untouched;
- MTP top-2 was extracted from the same parent distribution;
- the MTP cache at that exact parent depth was detached;
- the alternate continuation was generated from the MTP's own
  parent hidden state and cloned speculative cache;
- target verification had not yet occurred.

Only after verification were events retained where:

- ordinary top-1 rejected; and
- target correction equaled the already-generated MTP top-2.

The experiment therefore measures genuine pre-verification
tree-speculative continuation quality.

Frozen trajectory remained exact:

- prompt: 29297
- completion: 512
- cycles: 186
- acceptance: 325 / 442 = 73.5%
- output hash: 101ae2aec9793dfe

Exactly the expected early rank-2 population was reproduced:

- D1: 12
- D2: 23
- total: 35
- censored: 0

True pre-verify alternate continuation:

D1:

- +1 continuation:
  6 / 12 = 50.0%

- +2 continuation:
  3 / 12 = 25.0%

D2:

- +1 continuation:
  16 / 23 = 69.6%

Combined:

- branches with >=1 correct continuation:
  22 / 35 = 62.9%

- correct continuation positions:
  25 / 47 = 53.2%

- match-length histogram:
  - 0: 13
  - 1: 19
  - 2: 3

Comparison with P65C post-correction continuation:

- P65C branches >=1:
  30 / 35

- P65D branches >=1:
  22 / 35

- branch-signal retention:
  73.3%

- P65C correct continuation positions:
  33 / 47

- P65D correct continuation positions:
  25 / 47

- continuation-position retention:
  75.8%

Conclusion:

The pre-verification alternate branch retains substantial predictive
value.

The strong P65C continuation result was therefore not merely an
artifact of target/backbone hidden state becoming available after
verification.

True tree speculation survives the semantic test.

However, P65D does NOT yet establish positive runtime economics.

The diagnostic implementation intentionally explored D1/D2 alternate
branches broadly and forced their outputs to materialize for
measurement.

Observed diagnostic MTP timing:

- P65D MTP-head time:
  5635.2 ms

This number must not be interpreted as optimized tree cost.

The branch implementation included synchronization and observational
instrumentation that a production lazy / batched branch path should
avoid.

More importantly, the benefit ceiling must be expressed in verified
continuation positions rather than rank-2 event count.

On this ruler:

- additional correct pre-verify continuation positions:
  25

Baseline:

- 512 output tokens
- 186 cycles
- 2.7527 output tokens/cycle
- 144.263 ms/backbone-cycle

Therefore 25 perfect additional positions correspond only to roughly:

- 9.08 baseline cycle-equivalents
- about 1.31 seconds of backbone work

before paying for:

- alternate MTP generation
- confidence gating / synchronization
- wider or branched target verification
- cache/tree bookkeeping

Thus the next phase is an economics problem.

Preserved P65D artifacts:

p65d-preverify-tree-continuation.json

SHA256:

e6a47de1edc13674cae0d472e8a497d0cee56c674e04f7bb3782bd87f1319748

p65d-preverify-tree-events.jsonl

SHA256:

d6fbc86a43550902b2447617ee7d315b44beeff9d6a0d54a704bc290b7b4cd7e

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P66A target — tree break-even envelope

Before implementing a tree verifier, join:

- exact P63 MTP confidence margins;
- exact P65D pre-verification branch outcomes.

For several low-margin thresholds measure:

- number of D1/D2 parent positions selected;
- D1 versus D2 selected counts;
- required alternate MTP continuation nodes;
- equivalent extra target tree-query nodes;
- selected rank-2 events;
- selected useful branches;
- selected correct continuation positions;
- recall of the 22 useful branches;
- recall of the 25 useful continuation positions;
- optimistic cycle-equivalent reduction;
- optimistic backbone milliseconds saved;
- maximum combined added cost per branch node that can break even.

This must precede target-tree implementation.

If useful continuation is too diffuse, close tree speculation.

If a confidence gate preserves a large share of the 25 positions with
a small node budget, proceed to P66B and measure actual async/batched
branch-generation cost plus target verifier-layout cost.

### P66A result — tree break-even envelope

P66A joined the exact P63 confidence margins with the exact P65D
true pre-verification branch outcomes.

Baseline economics:

- 512 output tokens
- 186 verifier cycles
- 2.752688 output tokens/cycle
- 144.263 ms/backbone-cycle
- 26832.918 ms baseline backbone work
- each additional verified output position is worth approximately
  52.408 ms of baseline backbone work

P65D zero-overhead upper bound:

- 25 correct continuation positions
- 9.082 baseline cycle-equivalents
- 1310.201 ms optimistic backbone value

The forced-sync P65D diagnostic path implied approximately:

- 10.201 ms / alternate branch node

This is NOT production branch cost.

It includes forced materialization and diagnostic synchronization and
is used only as a warning/reference.

Confidence-gated envelope:

~10% gate:

- margin <= 0.53125
- 40 candidate parents
- 59 alternate continuation nodes
- 10 rank-2 events selected
- 5 useful branches
- 6 / 25 useful positions preserved = 24%
- optimistic backbone value: 314.4 ms
- combined break-even budget: 5.330 ms/node

~15% gate:

- margin <= 0.78125
- 54 candidate parents
- 82 nodes
- 13 rank-2 events
- 8 useful branches
- 10 / 25 useful positions = 40%
- optimistic value: 524.1 ms
- combined break-even budget: 6.391 ms/node

~20% gate:

- margin <= 1.046875
- 67 candidate parents
- 100 nodes
- 16 rank-2 events
- 9 useful branches
- 11 / 25 useful positions = 44%
- optimistic value: 576.5 ms
- combined break-even budget: 5.765 ms/node

~25% gate:

- margin <= 1.375
- 84 candidate parents
- 127 nodes
- 20 rank-2 events
- 13 useful branches
- 15 / 25 useful positions = 60%
- optimistic value: 786.1 ms
- combined break-even budget: 6.190 ms/node

~33% gate:

- margin <= 1.859375
- 114 candidate parents
- 172 nodes
- 29 rank-2 events
- 19 useful branches
- 22 / 25 useful positions = 88%
- optimistic value: 1153.0 ms
- combined break-even budget: 6.703 ms/node

Ungated:

- 341 candidate parents
- 527 nodes
- all 25 useful positions
- optimistic value: 1310.2 ms
- combined break-even budget: only 2.486 ms/node

P66A signal:

ASYNC_OR_BATCH_REQUIRED

The forced-sync P65D branch implementation is therefore not
economically viable.

A tree can remain viable only if alternate MTP work is made
substantially cheaper and target-tree verification also fits inside
the residual budget.

P66A's automatic rule selected the ~25% gate because it was the
smallest gate preserving at least 60% of useful positions.

A separate marginal-economics observation favors also testing ~33%:

- moving 25% -> 33% adds 45 branch nodes
- optimistic value rises by approximately 366.9 ms
- marginal value is approximately 8.15 ms per additional node

Therefore if branch cost is approximately linear and the tree is
viable at all, the 33% policy may produce more absolute net benefit
than the 25% policy.

A static D2-only policy is also important.

P65D D2 continuation:

- 16 / 23 rank-2 D2 events carried the one available continuation
- therefore 16 useful positions are structurally available at D2

Branching every D2 parent would require:

- 155 candidate parents
- 155 alternate nodes

Its optimistic benefit is approximately:

- 838.5 ms
- 5.41 ms/node break-even

D2-only requires no dynamic confidence-gate control flow and therefore
provides a useful simple-policy reference.

Preserved P66A artifact:

p66a-tree-break-even-envelope.json

SHA256:

0e659ffc2b5a84979be50634f64ef64053f308e453d3332cf784381fde986479

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P66B target — lazy branch-generation cost

P66B should NOT implement target-tree verification yet.

It should isolate alternate MTP generation cost under:

- ~25% frozen-ruler gate
- ~33% frozen-ruler gate
- static D2-only branching

For the margin policies, use the exact frozen P63 selected
cycle/depth positions as a precomputed schedule.

This intentionally removes online gate/control-flow cost from the
measurement and therefore establishes a LOWER BOUND on production
branch-generation cost.

The branch implementation must:

- use detached MTP-cache clones;
- preserve the true pre-verification semantics established by P65D;
- avoid any new host synchronization;
- keep top-2 and continuation IDs as lazy device arrays;
- dispatch alternate branch work asynchronously;
- resolve branch outputs only inside the verifier's already-existing
  single host synchronization;
- leave normal drafts, target verification, output, caches and
  acceptance untouched.

Benchmark against interleaved CONTROL rulers on the same server.

Primary measurements:

- integrated decode-window delta
- internal telemetry delta
- incremental ms per alternate node
- residual target-tree-verifier budget per node

If branch generation alone consumes the full P66A break-even budget,
close the current tree implementation path.

If substantial budget remains, proceed to a target-tree verifier
layout/cost scout.

Important caveat:

The precomputed 25%/33% schedules bypass the production problem of
making a margin-dependent branch decision without host synchronization.

A future live dynamic gate will require a device-side conditional /
compaction mechanism or an equivalent strategy.

The D2-only result provides a useful zero-dynamic-gate alternative.

### P66B result — lazy branch generation exceeds budget

P66B measured the lower-bound cost of true pre-verification
alternate MTP generation after removing the additional host
synchronization used by P65D.

Controls:

- exact frozen 29297-token prompt
- 512 generated tokens
- P61 HEADPAIR HPT2
- P58 FP16 GDN
- fixed D3 MTP
- output hash 101ae2aec9793dfe
- 186 cycles
- 325 / 442 ordinary drafts accepted

G25 / G33 used precomputed frozen-ruler cycle/depth schedules.

Therefore their measurements intentionally exclude the unresolved
production cost of making a dynamic low-margin branch decision.

Alternate branch arrays remained lazy on device and were resolved
inside the verifier cycle's already-existing host synchronization.

Interleaved CONTROL median:

- decode window:
  27.341537 s
- TG:
  18.726 tok/s
- internal measured time:
  27264.950 ms

G25:

- 84 selected parents
- 127 alternate continuation nodes
- median TG:
  18.125 tok/s
- decode-window delta:
  +907.3 ms
- integrated added cost:
  7.144 ms/node
- internal-time delta:
  +888.8 ms
- internal delta:
  6.999 ms/node
- P66A total break-even:
  6.190 ms/node
- residual target-tree budget:
  -0.955 ms/node

G33:

- 114 selected parents
- 172 nodes
- median TG:
  17.918 tok/s
- decode-window delta:
  +1232.8 ms
- integrated added cost:
  7.167 ms/node
- internal-time delta:
  +1207.5 ms
- internal delta:
  7.020 ms/node
- P66A total break-even:
  6.703 ms/node
- residual target-tree budget:
  -0.464 ms/node

D2ALL:

- 155 selected parents
- 155 nodes
- median TG:
  17.963 tok/s
- decode-window delta:
  +1161.3 ms
- integrated added cost:
  7.492 ms/node
- internal-time delta:
  +1143.4 ms
- internal delta:
  7.377 ms/node
- P66A break-even:
  approximately 5.410 ms/node
- residual target-tree budget:
  -2.082 ms/node

P66B signal:

BRANCH_GENERATION_CONSUMES_TREE_BUDGET

Conclusion:

The current pre-verification tree implementation is economically
non-viable.

Alternate MTP generation alone consumes more than the complete
break-even budget before paying for:

- target-tree verification
- tree attention layout
- dynamic confidence gating
- target cache bookkeeping

Do NOT proceed directly to a widened target-tree verifier using this
alternate-continuation implementation.

This closes the current implementation path, but does not yet close
the semantic tree opportunity.

The branch-generation implementation still pays to predict every
alternate descendant with an additional MTP forward.

A potentially cheaper architecture exists:

the ordinary linear MTP chain has already generated tokens at D2/D3
beyond the branch point.

Speculative candidates need not themselves have been generated under
the alternate parent; correctness is established by target
verification.

Therefore a top-2 branch may be able to reuse the already-existing
main-chain descendant token IDs with zero extra continuation MTP
forwards.

P66C must measure this before tree speculation is abandoned.

Preserved P66B artifact:

p66b-lazy-branch-cost.json

SHA256:

d38ad8adbd233772adee4877702a500e3b3374c4282c78b9d4eff14691c20167

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P66C target — free descendant reuse

P66C is observational and must perform NO alternate MTP forward.

At the exact 35 true rank-2 D1/D2 rejection frontiers established
by P65D, retain the ordinary already-generated draft token IDs that
occur after the rejected position.

For a D1 rejection:

ordinary chain already contains:

- original D2 token
- original D3 token

Treat those token IDs as descendants of the alternate top-2 D1
correction and compare them against the subsequent real target token
stream.

For a D2 rejection:

ordinary chain already contains:

- original D3 token

Treat that token as the descendant of the alternate top-2 D2
correction.

Measure sequential speculative usefulness:

- D1 reused +1
- D1 reused +2
- D2 reused +1
- branches with at least one reusable descendant
- total reusable continuation positions out of structural maximum 47

Important:

For D1, if the reused D2 token is wrong, the reused D3 token is not
counted even if its ID happens to match later, because speculative
acceptance terminates at the first mismatch.

This experiment requires:

- no MTP cache clone
- no alternate MTP decoder invocation
- no alternate LM-head projection
- no new host synchronization

It reads only draft IDs that already exist in the ordinary verifier
sync result.

If a substantial fraction of P65D's 25 useful continuation positions
can be recovered this way, the economic tree problem changes
dramatically:

- alternate continuation MTP cost becomes zero
- remaining costs are top-2 extraction / selection and target-tree
  verification

If free descendant reuse is weak, the current tree direction should
be deprioritized unless a fundamentally cheaper alternate-head
implementation is found.

### P66C result — free top-1 descendant reuse is weak

P66C tested whether ordinary D2/D3 draft token IDs that were already
generated by the normal linear MTP chain could be reused as descendants
of the correct top-2 branch.

This formulation performed:

- zero alternate MTP forwards
- zero alternate LM-head projections
- zero MTP-cache clones
- no target-tree verification
- no changes to emitted generation

Frozen trajectory remained exact:

- prompt: 29297
- completion: 512
- cycles: 186
- acceptance: 325 / 442
- hash: 101ae2aec9793dfe

Exactly the expected P65D rank-2 population was observed:

- D1: 12
- D2: 23
- total: 35
- censored: 0

Free top-1 descendant reuse:

D1:

- reused +1:
  2 / 12 = 16.7%

- reused +2:
  1 / 12 = 8.3%

D2:

- reused +1:
  3 / 23 = 13.0%

Combined:

- branches with >=1 reusable descendant:
  5 / 35 = 14.3%

- reusable continuation positions:
  6 / 47 = 12.8%

- match-length histogram:
  - 0: 30
  - 1: 4
  - 2: 1

Compared with P65D separately-generated true pre-verify branches:

- P65D useful branches:
  22 / 35

- P65D useful positions:
  25 / 47

- P66C branch usefulness versus P65D:
  22.7%

- P66C position usefulness versus P65D:
  24.0%

Zero-extra-MTP optimistic backbone value:

- approximately 314.4 ms

Conclusion:

The ordinary descendant argmax transfers poorly across the corrected
top-2 parent.

Therefore simple free top-1 descendant reuse is rejected.

Preserved artifacts:

p66c-free-descendant-reuse.json

SHA256:

c6edda4914c974296c8953f3c02b5212ce3b8ac39a76f5bfb200f7e48002e339

p66c-free-descendant-reuse-events.jsonl

SHA256:

a6b1b17b9ad7de0c139ee45eef970958f06b7a3dc1ea637db9739ffb53fa5198

One final zero-alternate-MTP formulation remains logically distinct.

The ordinary chain has already computed the complete vocabulary
distribution at each descendant position, not merely its top-1 token.

P66D should retain a small top-K candidate set from those existing
descendant distributions.

No additional MTP forward is required.

For D1 rank-2 corrections:

- inspect the already-computed ordinary D2 distribution
- inspect the already-computed ordinary D3 distribution

For D2 rank-2 corrections:

- inspect the already-computed ordinary D3 distribution

Measure target inclusion at K:

- 1
- 2
- 4
- 8
- 16

For D1 sequential usefulness:

- +1 requires the next true target token to be in D2 top-K
- +2 additionally requires the following target token to be in
  D3 top-K

This is an observational candidate-set experiment only.

If small K recovers substantial continuation, a target-only tree may
remain viable without alternate MTP generation.

If small K is weak, close the P65/P66 tree family and move to a
learned MTP-head / representation-correction workstream.

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P66D result — close current tree family

P66D tested the final zero-alternate-MTP formulation in the P65/P66
tree-speculation workstream.

Instead of reusing only the ordinary descendant argmax as in P66C,
P66D captured top-K candidate sets from the complete descendant MTP
distributions that the ordinary linear chain had already computed.

No alternate MTP continuation forward was performed.

Frozen trajectory remained exact:

- prompt: 29297
- completion: 512
- cycles: 186
- acceptance: 325 / 442 = 73.5%
- output hash: 101ae2aec9793dfe

Exactly the expected oracle rank-2 population was observed:

- D1: 12
- D2: 23
- total: 35
- structural descendant positions: 47

Free candidate-set results:

K=1:

- D1 +1: 2 / 12
- D1 +2: 1 / 12
- D2 +1: 3 / 23
- shallow positions: 5
- deep positions: 6 / 47
- shallow oracle target nodes: 70
- deep oracle target nodes: 82
- shallow break-even: 3.743 ms/node
- deep break-even: 3.835 ms/node

K=2:

- D1 +1: 3 / 12
- D1 +2: 2 / 12
- D2 +1: 4 / 23
- shallow positions: 7
- deep positions: 9 / 47
- shallow oracle target nodes: 105
- deep oracle target nodes: 153
- shallow break-even: 3.494 ms/node
- deep break-even: 3.083 ms/node

K=4:

- D1 +1: 3 / 12
- D1 +2: 2 / 12
- D2 +1: 7 / 23
- shallow positions: 10
- deep positions: 12 / 47
- shallow oracle target nodes: 175
- deep oracle target nodes: 367
- shallow break-even: 2.995 ms/node
- deep break-even: 1.714 ms/node

K=8:

- D1 +1: 5 / 12
- D1 +2: 3 / 12
- D2 +1: 7 / 23
- deep positions: 15 / 47
- deep oracle target nodes: 1083
- deep break-even: 0.726 ms/node

K=16:

- D1 +1: 6 / 12
- D1 +2: 4 / 12
- D2 +1: 7 / 23
- deep positions: 17 / 47
- deep oracle target nodes: 3667
- deep break-even: 0.243 ms/node

Target-rank census across all 47 already-computed descendant
distributions:

- rank <= 1:
  6 / 47 = 12.8%
- rank <= 2:
  9 / 47 = 19.1%
- rank <= 4:
  12 / 47 = 25.5%
- rank <= 8:
  15 / 47 = 31.9%
- rank <= 16:
  17 / 47 = 36.2%
- rank > 16:
  30 / 47 = 63.8%

P65D separately generated alternate continuations had:

- 25 / 47 correct continuation positions

Therefore the poor P66C reuse result is not merely an argmax problem.
Most post-correction target tokens are not even near the top of the
ordinary wrong-parent descendant distribution.

P66D verdict:

CLOSE_CURRENT_TREE_FAMILY

This decision is stronger than the raw oracle node budgets imply.

All P66D economics condition on already knowing the exact 35
target-rank-2 rejection events.

A production confidence gate does not know this and P65B established
that margin is primarily a general rejection signal rather than a
rank-2-specific signal.

Production tree width would therefore include many false-positive
branches and have strictly worse economics than these oracle figures.

Combined P65/P66 conclusion:

- rank-2 near-miss population:
  real
- true pre-verify alternate continuation quality:
  real
- separately generated branch semantics:
  valid
- separately generated branch runtime cost:
  too high
- free top-1 descendant reuse:
  weak
- free small-top-K descendant reuse:
  economically weak
- confidence margin as rank-2 detector:
  rejected
- current tree-speculation family:
  CLOSED

Do not reopen this branch without a fundamentally different
branch-generation or target-verification primitive.

Preserved P66D artifacts:

p66d-free-topk-descendants.json

SHA256:

9cbd4e050ea7bb37a5ce9c406f4a293ce783b95f868ed688fc521a01a724c057

p66d-free-topk-descendants-events.jsonl

SHA256:

64adfdbbf01876ca1c6b0516f1f55a0c36adf669fc9ebd9dd85c8bec4e20a531

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P67A target — state-dependent residual predictability

Return to MTP-head acceptance improvement while keeping fixed:

- D3 / M4
- P58 FP16 GDN
- native 256-block attention topology
- P61 HPT2 HEADPAIR
- exact shared Q8 / GS64 LM head
- frozen P61 speculative trajectory for diagnostics

P64A rejected a constant global/depth mean residual correction.

P64A did NOT test whether the target residual is conditionally
predictable from the MTP hidden state.

P67A should remain completely offline.

Using the exact P63E aligned artifact:

- X = MTP hidden
- Y = target hidden
- residual R = Y - X

Use whole verifier cycles as the splitting unit so D1/D2/D3 rows from
one cycle can never cross train / validation / test boundaries.

Canonical split:

- deterministic cycle shuffle
- 60% train
- 20% validation
- 20% untouched test

Train a diagnostic kernel-ridge residual predictor from MTP hidden
state.

Use depth-specific residual means as the intercept so the model tests
STATE-DEPENDENT structure beyond the P64 mean seam.

Evaluate both:

- compact residual output ranks:
  8 / 16 / 32 / 64
- higher-capacity upper bounds:
  128 / full

Select:

- lambda
- output rank
- correction scale

using validation only.

Then refit on train + validation and evaluate the selected model once
on the untouched test set.

Primary metrics:

- residual-energy R2 versus no correction
- incremental R2 versus depth-mean-only correction
- corrected-hidden cosine to target
- relative-L2 reduction
- predicted-residual cosine to true residual
- per-depth test behavior

Also evaluate the validation-selected best compact rank <=64
independently from the best-any-capacity model.

Interpretation:

If a compact held-out predictor materially beats the depth-mean
baseline, proceed to exact shared-LM-head replay in P67B.

If only a high-capacity/full predictor generalizes, treat that as
evidence of state-dependent structure but not yet of a practical
adapter.

If neither beats depth-mean correction on untouched test cycles, close
this residual-prediction route and move to a different MTP-head
training objective.

P67A is a predictability experiment, not a production model.

### P67A result — compact state-dependent residual signal

P67A tested whether target-hidden residual structure is predictable
from the current MTP hidden state beyond the constant depth-mean seam
rejected by P64A.

Artifact:

- exact P63E aligned capture
- 442 x 5120 MTP hidden
- paired 442 x 5120 target hidden
- 186 verifier cycles
- D1 / D2 / D3:
  186 / 155 / 101
- 325 accepted drafts

Split unit:

- whole verifier cycle

No D1/D2/D3 rows from a single cycle could cross dataset splits.

Deterministic split seed:

- 6701

Split:

- train:
  112 cycles / 273 rows
- validation:
  37 cycles / 79 rows
- untouched test:
  37 cycles / 90 rows

Training / model-selection policy:

- depth-specific MTP-hidden centering
- depth-specific residual-mean intercept
- linear kernel ridge predictor
- residual output ranks:
  8 / 16 / 32 / 64 / 128 / full
- lambda:
  0.1 / 1.0 / 10.0
- correction alpha:
  0.25 / 0.50 / 0.75 / 1.00
- all hyperparameter selection:
  validation only
- final test:
  one untouched evaluation after refitting train + validation

Validation depth-mean-only baseline:

- selected alpha:
  0.75
- validation residual R2:
  +0.104242

Best validation any-capacity predictor:

- full output rank
- lambda 0.1
- alpha 0.75
- validation R2:
  +0.272958

Best validation compact predictor:

- output rank 64
- lambda 0.1
- alpha 0.75
- validation R2:
  +0.218577

Untouched test depth-mean baseline:

- R2:
  +0.111548
- corrected hidden / target cosine delta:
  +0.045322
- relative-L2 delta:
  -0.070381

Untouched test compact rank-64 predictor:

- R2:
  +0.251010
- incremental R2 over depth-mean-only:
  +0.139462
- corrected hidden / target cosine delta:
  +0.084655
- predicted residual / true residual cosine:
  +0.506417
- relative-L2 delta:
  -0.163426

Compact test behavior remained positive at every depth:

D1:

- 37 rows
- R2:
  +0.248242
- cosine delta:
  +0.073593
- relative L2:
  1.034734 -> 0.885613

D2:

- 31 rows
- R2:
  +0.241772
- cosine delta:
  +0.079380
- relative L2:
  1.164035 -> 1.002286

D3:

- 22 rows
- R2:
  +0.264733
- cosine delta:
  +0.110693
- relative L2:
  1.288095 -> 1.098245

Untouched test full-capacity upper bound:

- R2:
  +0.317773
- incremental R2 over depth mean:
  +0.206225
- corrected hidden / target cosine delta:
  +0.103359
- predicted residual cosine:
  +0.567831
- relative-L2 delta:
  -0.210908

P67A signal:

COMPACT_STATE_DEPENDENT_RESIDUAL_SIGNAL

Conclusion:

The P63 MTP -> target representation error contains a substantial
state-dependent component that generalizes across held-out verifier
cycles.

This is qualitatively different from P64A.

P64A tested only:

- global mean residual
- depth-specific mean residual

and found no held-out token-decision justification for those constant
corrections.

P67A shows that the residual is conditionally predictable from the
MTP hidden state itself.

The rank-64 result is especially important:

- it captures substantial held-out residual structure;
- it remains positive across D1 / D2 / D3;
- it captures a large fraction of the full-capacity predictor's
  held-out signal.

However, P67A is still hidden-space evidence only.

A better approximation to target hidden does not automatically imply
better shared-LM-head token decisions.

Therefore no live correction is justified yet.

Preserved P67A artifact:

p67a-supervised-residual-predictability.json

SHA256:

fbfcbcfde2bd6162dc39a6e5c28263cb903e7d7672319a939e3eb146974e4620

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P67B target — exact Q8 shared-LM-head replay

P67B must remain offline.

Use exactly the untouched P67A test cycles.

Refit on P67A train + validation rows and reproduce:

1. baseline MTP hidden
2. validation-selected depth-mean correction
3. validation-selected compact rank-64 predictor
4. validation-selected full-capacity predictor as an upper bound

Project each hidden representation through the exact shared target
LM head:

- vocabulary:
  248320
- Q8
- group size 64
- exact model quantized weight/scales/biases

Before interpreting corrections, baseline replay must reproduce:

- exact draft top-1 IDs on all test rows
- exact captured target ranks on all test rows

Primary decision metrics:

- total target top-1 count
- recovered baseline rejections
- broken baseline accepts
- net top-1 change
- per-depth recovered / broken / net
- target-rank movement on baseline rejection rows
- target rank <=2 / <=4 / <=8 / <=16
- target-logit deficit versus top-1

Interpretation:

A hidden-space gain is useful only if the compact predictor produces a
positive held-out token-decision trade:

- recover incorrect drafts
- without breaking a comparable number of correct drafts

Do not translate corrected-row count directly into verifier-cycle
savings.

The captured hidden states come from the original speculative
trajectory; changing an earlier token decision changes later MTP
states.

If compact exact-head replay is positive, the next phase must be
multi-prompt validation before any live decoding integration.

### P67B result — hidden gain does not transfer ungated

P67B replayed the exact shared Q8 / GS64 LM head on the untouched
P67A test split.

Test set:

- 37 verifier cycles
- 90 draft rows
- 67 baseline accepts
- 23 baseline rejections

The P67A predictors reproduced exactly before LM-head evaluation:

- depth-mean R2:
  +0.111547968
- compact rank-64 R2:
  +0.251009810
- full-capacity R2:
  +0.317772533

Exact shared head:

- vocab:
  248320
- Q8
- group size:
  64
- shard:
  model-00006-of-00007.safetensors

Baseline replay invariants:

- draft top-1 mismatches:
  0
- captured target-rank mismatches:
  0
- baseline acceptance mask:
  exact

Exact token-decision result:

BASE:

- correct:
  67 / 90
- rejection target rank <=2:
  8 / 23
- <=4:
  15 / 23
- <=8:
  17 / 23
- <=16:
  20 / 23
- mean rejection target-logit deficit:
  3.1505

DEPTH_MEAN:

- correct:
  68 / 90
- recovered rejections:
  1
- broken accepts:
  0
- net:
  +1

COMPACT64:

- correct:
  67 / 90
- recovered rejections:
  4
- broken accepts:
  4
- net:
  0
- rejection target rank <=2:
  10 / 23
- <=4:
  16 / 23
- <=8:
  18 / 23
- <=16:
  20 / 23
- mean rejection target-logit deficit:
  3.0346

FULL:

- correct:
  61 / 90
- recovered rejections:
  3
- broken accepts:
  9
- net:
  -6

Compact rank-64 by depth:

D1:

- 37 rows
- baseline correct:
  31
- corrected:
  29
- recover:
  1
- break:
  3
- net:
  -2

D2:

- 31 rows
- baseline correct:
  22
- corrected:
  24
- recover:
  3
- break:
  1
- net:
  +2

D3:

- 22 rows
- baseline correct:
  14
- corrected:
  14
- recover:
  0
- break:
  0
- net:
  0

The eight compact decision transitions were:

- four recovered baseline rejects
- four broken baseline accepts

P67B signal:

HIDDEN_GAIN_DOES_NOT_TRANSFER_TO_TOP1

Conclusion:

The P67A state-dependent representation signal is real, but direct
Euclidean residual regression is not sufficiently aligned with the
shared-LM-head decision boundary when applied unconditionally.

Increasing capacity makes the token trade worse rather than better:

- rank-64:
  net 0
- full:
  net -6

Therefore this is not primarily an under-capacity problem.

The compact correction does, however:

- recover four real held-out rejections;
- improve target-rank statistics on baseline rejects;
- slightly reduce mean rejection target-logit deficit.

The failure mode is protection of already-correct drafts.

This motivates a selective correction architecture rather than
discarding the state-dependent signal immediately.

P65 independently established that baseline top1-top2 margin is a
strong general rejection / uncertainty signal.

Therefore P67C should test whether applying the fixed P67A compact
correction only to low-confidence baseline rows preserves recovered
rejections while suppressing broken accepts.

Important methodological rule:

The observed P67B D1/D2 test-depth behavior is hypothesis-generating
only.

Do not choose a D2-only policy from this spent test result.

P67C gating must be selected without using P67B test outcomes.

Preserved P67B artifact:

p67b-exact-q8-lm-head-replay.json

SHA256:

000dbfb3167815311269112cdb6eea0a4dfcd623ed707b3a7c9b5b32a191dc40

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P67C target — confidence-gated compact correction

Keep the P67A compact predictor fixed:

- output rank:
  64
- lambda:
  0.1
- correction alpha:
  0.75

Do not retune those parameters using P67B test rows.

Use P67A train + validation cycles only to select a baseline
top1-minus-top2 margin threshold.

Use cycle-disjoint cross-fitting across those 149 development cycles:

- each development row receives a correction prediction from a model
  that did not train on its cycle;
- exact shared Q8/GS64 LM-head replay supplies baseline margin and
  corrected token decision;
- pool the out-of-fold decisions;
- select one margin threshold using only those out-of-fold development
  decisions.

Selection objective:

1. maximize net top-1 gain;
2. then minimize broken baseline accepts;
3. then maximize recovered rejections;
4. then prefer fewer gated rows.

Include a NONE policy.

Then:

- refit the fixed rank-64 predictor on all P67A train + validation rows;
- apply the frozen margin gate to the 90-row P67B test split;
- compare against ungated COMPACT64.

The P67B test has already been exposed once and must not be described
as a newly untouched test.

It remains useful as a secondary fixed-policy confirmation because
the P67C threshold itself is selected without those outcomes.

Runtime architecture note:

A positive margin-gated result can potentially avoid a second full
Q8 LM-head pass.

The normal baseline LM-head pass already supplies:

- baseline logits
- baseline top1 / top2
- confidence margin

Because the learned correction is constrained to a rank-64 residual
basis, a future implementation can pre-project that basis through the
LM head and express the correction as a lower-dimensional logit delta.

This should be measured only if P67C demonstrates a positive
recover-versus-break trade.

### P67C result — confidence gate does not rescue

P67C tested whether baseline MTP confidence could protect
already-correct drafts from the P67A rank-64 state-dependent
residual correction.

The compact correction was frozen exactly from P67A:

- output rank:
  64
- lambda:
  0.1
- correction alpha:
  0.75

No compact-model parameter was retuned.

Gate threshold selection used only the original P67A
train + validation development population:

- 149 verifier cycles
- 352 rows

Five cycle-disjoint cross-fit folds were used.

Every development correction prediction came from a model
that did not train on that verifier cycle.

Baseline top1-minus-top2 margin thresholds tested:

- NONE
- 0.25
- 0.50
- 0.75
- 1.00
- 1.25
- 1.50
- 1.75
- 2.00
- 2.50
- 3.00
- 4.00
- 6.00
- ALL

Cross-fitted development results:

NONE:

- gated:
  0
- recovered:
  0
- broken:
  0
- net:
  0

0.25:

- gated:
  25
- baseline rejects:
  13
- baseline accepts:
  12
- recovered:
  2
- broken:
  6
- net:
  -4

0.50:

- gated:
  37
- recovered:
  2
- broken:
  7
- net:
  -5

0.75:

- gated:
  56
- recovered:
  2
- broken:
  10
- net:
  -8

1.00:

- gated:
  74
- recovered:
  4
- broken:
  11
- net:
  -7

1.50:

- gated:
  105
- recovered:
  5
- broken:
  13
- net:
  -8

2.00:

- gated:
  121
- recovered:
  5
- broken:
  14
- net:
  -9

3.00:

- gated:
  174
- recovered:
  5
- broken:
  14
- net:
  -9

ALL:

- gated:
  352
- baseline rejects:
  94
- baseline accepts:
  258
- recovered:
  5
- broken:
  14
- net:
  -9

Every nonzero confidence-gated policy was negative.

The development-selection objective therefore correctly chose:

- threshold:
  NONE
- gated rows:
  0
- net:
  0

The already-exposed P67B test split then necessarily remained
unchanged:

- gated:
  0 / 90
- recovered:
  0
- broken:
  0
- net:
  0

For reference, P67B ungated compact was reproduced exactly:

- recovered:
  4
- broken:
  4
- net:
  0

P67C signal:

CONFIDENCE_GATE_DOES_NOT_RESCUE

Conclusion:

Baseline confidence is a real rejection signal, as established
earlier in P65, but it is not sufficient to distinguish rows where
the P67A Euclidean residual correction will help from rows where it
will destroy an already-correct decision.

Therefore close the current formulation:

- Euclidean target-hidden residual regression
- followed by baseline-margin gating

Do not tune another threshold or depth-specific gate on the same
spent ruler.

The P67 sequence nevertheless established two important positive facts:

1. MTP hidden state contains substantial held-out information about
   target representation error.

2. A compact rank-64 correction can recover real LM-head mistakes.

The primary failure is objective alignment:

- P67A minimizes representation-space residual error;
- production utility depends on target-vs-competitor LM-head margins;
- increasing Euclidean predictor capacity made token behavior worse,
  not better.

Therefore the next learned experiment should train directly toward
LM-head decision geometry and explicitly protect already-correct rows.

Preserved P67C artifact:

p67c-confidence-gated-compact-replay.json

SHA256:

36accd2fc402f37acc59c961b4ef10ceeb558f5c1d84de76e50d19d21999cb8a

Champion remains unchanged:

- P61 HEADPAIR HPT2
- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- 325 / 442 drafts accepted
- hash 101ae2aec9793dfe

### P68A target — decision-aware low-rank margin correction

P68A should remain offline.

Do NOT optimize Euclidean distance to target hidden.

Instead construct a fixed rank-64 hidden correction subspace from
training-only MTP->target residuals and train the state-dependent
predictor toward LM-head decision margins.

For each training fold:

- fit a rank-64 residual basis using training cycles only;
- replay the exact shared Q8 / GS64 LM head;
- for an already-correct row:
  - desired correction coefficient target = zero;
- for a rejected row:
  - identify the current baseline top-1 competitor;
  - project target-vs-competitor LM-head sensitivity into the
    rank-64 basis;
  - construct the minimum-L2 coefficient vector that would raise
    target above that competitor by a small positive margin;
  - clip the coefficient norm conservatively.

Then train a state-only kernel-ridge predictor:

MTP hidden -> 64 decision-aware correction coefficients

The inference predictor must not consume target id, acceptance,
target hidden, or target logits.

Use cycle-disjoint cross-fitting on the original 149 development
cycles.

Select only on cross-fitted development behavior.

The already-exposed P67B 90-row split may be used only as secondary
fixed-policy confirmation.

Primary exact metrics:

- recovered baseline rejections
- broken baseline accepts
- net top-1 change
- per-depth behavior
- correction norm
- exact Q8/GS64 full-vocabulary replay

The selected development policy must be verified with a full exact
LM-head replay, because pairwise target-vs-baseline-competitor
optimization can still cause a third token to become top-1.

If P68A is positive:

- stop tuning on this single prompt;
- freeze the objective and architecture;
- capture genuinely new prompts for validation.

If P68A is not positive:

- close low-rank hidden-correction adapters from this ruler;
- return to structural verifier/runtime work or collect a larger
  multi-prompt training corpus before further learned tuning.

### P68A result — no decision-aware low-rank gain

P68A tested the final same-ruler learned hidden-correction formulation.

Unlike P67A, P68A did NOT optimize Euclidean distance to target hidden.

It trained a compact rank-64 state-dependent correction directly
against shared-LM-head decision geometry.

Training-label construction:

- correction subspace:
  rank 64
- basis:
  training-only MTP -> target residual PCA
- already-correct training rows:
  explicit zero-correction target
- rejected training rows:
  minimum-L2 rank-64 coefficient vector required to raise the
  true target above the current baseline top-1 competitor
- exact shared head:
  Q8 / GS64 / vocabulary 248320

Inference predictor remained state-only:

- MTP hidden -> rank-64 correction coefficients

No target id, target hidden, target logit, or acceptance flag was
available to the inference predictor.

Development population:

- original P67A train + validation cycles
- 149 verifier cycles
- 352 rows
- 258 accepted
- 94 rejected

Selection used five cycle-disjoint cross-fit folds.

Search space:

target margin:

- 0.00
- 0.25
- 0.50

label coefficient clip norm:

- 8
- 16
- 32

kernel-ridge lambda:

- 0.1
- 1.0

rejection-row training weight:

- 1
- 4

output scale:

- 0.50
- 1.00

A NONE policy was included.

Baseline exact shared-LM-head replay reproduced all 442 rows.

Cross-fitted pairwise development result:

The selector preferred:

NONE

with:

- recovered:
  0
- broken:
  0
- net:
  0

No active configuration achieved positive net development gain.

Representative strongest active configurations:

target-margin 0.00 / clip32 / lambda0.1 /
reject-weight4 / scale1.0:

- recovered:
  3
- broken:
  3
- net:
  0

target-margin 0.25 / clip32 / lambda0.1 /
reject-weight4 / scale1.0:

- recovered:
  3
- broken:
  3
- net:
  0

target-margin 0.50 / clip32 / lambda0.1 /
reject-weight4 / scale1.0:

- recovered:
  3
- broken:
  3
- net:
  0

More conservative configurations generally changed no decisions or
became net negative.

Because NONE won development selection, exact full-vocabulary OOF
verification remained baseline:

- rows:
  352
- baseline correct:
  258
- corrected:
  258
- recovered:
  0
- broken:
  0
- net:
  0

Secondary already-exposed P67B test likewise remained baseline:

- rows:
  90
- baseline correct:
  67
- corrected:
  67
- recovered:
  0
- broken:
  0
- net:
  0

P68A signal:

NO_DECISION_AWARE_LOW_RANK_GAIN

Conclusion:

The single frozen 29.3K ruler does contain real state-dependent
MTP -> target information, as demonstrated by P67A.

However, none of the compact low-rank correction formulations tested
on this ruler converts that information into a reproducibly positive
top-1 trade.

Closed same-ruler learned formulations now include:

1. constant global residual correction
2. constant depth-specific residual correction
3. state-dependent Euclidean residual regression
4. state-dependent residual regression plus baseline-margin gating
5. rank-64 direct target-vs-competitor decision-margin supervision

Do not continue hyperparameter tuning of this adapter family on the
same prompt.

A future learned-correction effort requires a substantially larger
multi-prompt training corpus rather than another same-ruler variant.

Preserved artifact:

p68a-decision-aware-margin-adapter.json

SHA256:

95460bade39ca2ff9607be6bf00638c9485f82523078f6b121a16b3f84aada17

### Search-family closure after P68A

The following major branches are now intentionally closed for the
current 29.3K operating point unless a fundamentally new primitive or
new multi-prompt evidence appears.

Speculative-depth routing:

- D2/M3 lost to D3/M4 across P57 sampled real workloads
- D4/M5 lost even on acceptance-rich challenges
- fixed D3/M4 remains preferred

Verifier attention geometry:

- native 256-block topology retained for numerical stability
- HPT2 HEADPAIR is certified
- HPT3 is catastrophically slower
- do not test HPT4 on this kernel geometry

Tree speculation:

- real rank-2 near-miss population exists
- true pre-verify alternate continuation exists
- separately generated branch cost exceeds its economic envelope
- free top-1 and small-top-K descendant reuse are too weak
- P65/P66 tree family closed

Same-ruler learned hidden correction:

- hidden-state predictability exists
- direct top-1 utility does not generalize positively
- P67/P68 same-ruler correction family closed

Champion remains unchanged:

P61 HEADPAIR HPT2

- 18.731 tok/s
- 144.263 ms/backbone-cycle
- 186 cycles
- acceptance:
  325 / 442
- hash:
  101ae2aec9793dfe

Preferred structural stack remains:

- fixed D3 / verifier M4
- P54F verifier QMM routing
- lm_head NSG8 / BN4
- P58 FP16 GDN fused verifier prework
- native 256-block SDPA reduction topology
- P61 HPT2 HEADPAIR K/V reuse
- exact frozen speculative trajectory

### P69A target — structural verifier remainder audit

Return to structural runtime optimization.

Do NOT begin with another speculative-policy or learned-correction
experiment.

P69A should first measure where the remaining P61 verifier-backbone
time is spent.

The purpose is to identify the largest remaining optimizable component
after the already-certified structural work.

Already optimized / heavily searched components include:

- regular verifier QMM routing and split-K policy:
  P51-P55
- huge-N lm_head geometry:
  P52-P55
- GDN verifier prework:
  P58
- full-attention long-KV K/V reuse:
  P60-P62

P69A should profile the certified P61 stack while preserving:

- exact D3/M4 policy
- exact 186-cycle trajectory
- exact 325/442 acceptance
- exact output hash
- P58 FP16 GDN
- P61 HPT2 HEADPAIR
- native 256-block attention topology

Profile the remaining backbone by operation family.

At minimum separate:

- regular quantized projections / QMM
- lm_head
- full-attention SDPA
- Gated DeltaNet / recurrent work
- normalization
- residual / elementwise work
- embeddings / indexing where applicable
- cache / state update work
- unclassified framework / dispatch remainder

Where possible also split by:

- 48 GDN layers
- 16 full-attention layers
- verifier M=4 hot shapes

P69A is an attribution experiment.

Do not alter arithmetic, kernel geometry, speculative policy, or
trajectory during the initial profile.

The next optimization after P69A must target the largest measured
unclosed structural remainder rather than guessing from historical
kernel intuition.


## P69A — structural verifier remainder audit

P69A returned to the certified P61 structural stack and measured the
remaining verifier-backbone cost before designing another optimization.

The frozen ruler remained:

- prompt: 29,297 tokens
- generation: 512 tokens
- fixed D3 / verifier M4
- 186 cycles
- acceptance: 325/442 = 73.5%
- depth: d1=155/186, d2=101/155, d3=69/101
- output hash: 101ae2aec9793dfe

### P69A profiler capability audit

The initial Metal System Trace exposed a rich compiled-shader dictionary
and command-buffer timing data, but no usable per-shader execution timing
on this M1 Max.

Shader Timeline / shader-profiler counters were unavailable:

- profiler table remained empty
- Metal reported that the selected counter profile was unsupported

Direct `MTLCommandBuffer` GPU timestamps were then validated using:

- `GPUStartTime()`
- `GPUEndTime()`

The direct timestamp smoke passed on this M1 Max.

An attempted family-boundary profiler that committed command buffers from
inside pipeline selection was rejected after Metal aborted with a command-
buffer lifecycle assertion.

A second experiment split compute encoders on operation-family transitions
without forcing command-buffer commits. The mechanism successfully joined
encoder labels to real GPU durations on a synthetic workload, but the full
ruler changed dramatically:

- 130 cycles instead of 186
- acceptance 382/385 instead of 325/442
- output became degenerate repeated punctuation

Therefore even encoder-boundary changes are numerically / scheduling
intrusive on this verifier path and cannot be used for P69 attribution.

### P69A passive natural-command-buffer profiler

P69A-7D instead added metadata only while preserving MLX's existing
encoder and command-buffer boundaries exactly.

For each naturally occurring command buffer it recorded:

- normal command-buffer GPU duration
- exact compiled kernel IDs dispatched inside the buffer
- dispatch counts per kernel

It did not add:

- `end_encoding()`
- `commit()`
- synchronization
- arithmetic changes
- kernel-geometry changes
- speculative-policy changes

This passive instrumentation preserved the frozen trajectory exactly:

- hash: 101ae2aec9793dfe
- cycles: 186
- acceptance: 325/442
- exact depth ladder retained

P69A-7D telemetry:

- backbone: 26,811.4 ms
- MTP: 347.3 ms
- sampling: 6.3 ms
- cache: 73.3 ms

The natural command-buffer decode slice contained:

- 29,626 command buffers
- 25,211.102 ms measured GPU time
- 135.544 ms mean measured GPU time/cycle
- 1.816 ms cycle-to-cycle SD
- 129.802 ms minimum cycle
- 151.214 ms maximum cycle

Measured natural GPU time therefore covered approximately:

- 94.03% of logged backbone time
- 92.56% of total logged decode work

Kernel `custom_kernel_omlx_vk_m4_q8_bn4_nsg8_gs64_fp16`
appeared exactly 186 times and provided a natural cycle terminator for
offline segmentation.

### Dominant natural buffer archetypes

The largest directly measured recurrent natural command-buffer archetype
was a verifier projection / QMV buffer:

- 8,550 occurrences
- 45.968 buffers/cycle
- median 0.77550 ms/buffer
- 35.648 ms/cycle direct measured contribution

Its recurring composition includes:

- RMS normalization
- stock `affine_qmv_fast` Q8 projection
- custom verifier split-K QMM
- gather / activation / add operations

The second-largest recurring archetype was the certified P61 long-context
attention buffer:

- 2,944 occurrences
- 15.828 buffers/cycle
- median 1.52675 ms/buffer
- 24.165 ms/cycle direct measured contribution

Therefore the largest measured unclosed structural remainder is no longer
the already-optimized P61 attention path. It is the recurrent verifier
projection / QMV bundle.

### Kernel-level attribution limit

A coarse family NNLS model was weak:

- R² = 0.136750

An exact-kernel NNLS model improved fit but remained insufficient for
kernel-level promotion:

- R² = 0.430393

The model suggested a large role for stock Q8 `affine_qmv_fast`, but this
estimate is NOT promoted as a measured standalone kernel cost because the
natural scheduler strongly collinearizes the hot verifier kernels.

Matched natural-buffer contrasts were then attempted.

The important hot kernels, including:

- stock `affine_qmv_fast`
- verifier KP1 / KP2 QMM
- P61 HEADPAIR SDPA
- M4 lm_head verifier QMM
- GDN verifier kernels

did not obtain clean exact matched contrasts because they travel together
in the natural execution graph.

Therefore P69A does NOT claim that any single kernel owns the full
35.648 ms/cycle projection-buffer cost.

### Final hardware counter gate

The Apple M1 Max reports:

- stage-boundary counter sampling: YES
- dispatch-boundary counter sampling: NO
- timestamp counter set: present
- timestamp sample-buffer creation: supported

Because dispatch-boundary counter sampling is unsupported, true
non-perturbative per-dispatch timestamping inside the existing compute
encoder is not available on this hardware.

This closes the remaining clean kernel-timestamp route.

### P69A conclusion

P69A is complete.

The strongest defensible structural result is:

**the dominant remaining unclosed verifier cost is the recurrent
projection / QMV command-buffer bundle, measured directly at approximately
35.648 ms/cycle on the frozen 30K P61 ruler.**

The already-certified P61 attention archetype is approximately
24.165 ms/cycle and is no longer the first optimization target.

Do not interpret the weak regression as proof that stock
`affine_qmv_fast` alone costs ~74 ms/cycle.

### Next phase — P69B

P69B should optimize the measured projection / QMV bundle.

Begin with exact-shape isolation and microbenchmarking of the hot projection
path, especially the stock Q8 `affine_qmv_fast` component and its interaction
with the existing verifier KP1/KP2 routes.

The objective is to determine which component of the directly measured
35.648 ms/cycle archetype can be reduced while preserving the exact P61
arithmetic / speculative trajectory.

Do NOT reopen:

- D2/D4 speculative-depth routing
- P65/P66 tree speculation
- HPT3/HPT4 attention geometry
- P67/P68 learned hidden correction
- further P61 attention tuning without new measured evidence

P69B must remain driven by the measured projection/QMV remainder rather
than by historical kernel intuition.


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

As of the P68A checkpoint, same-ruler learned hidden correction is
closed.

P68A's cycle-cross-fitted decision-aware rank-64 search selected NONE.

The next phase is:

**P69B — verifier projection / QMV bundle optimization**

Return to the certified P61 structural stack.

Do not reopen:

- D2/D4 speculative-depth routing
- P65/P66 tree speculation
- HPT3/HPT4 attention geometry
- P67/P68 same-ruler learned hidden correction

P69A completed the structural remainder audit while preserving the exact
frozen P61 trajectory.

The largest directly measured unclosed remainder is now the recurrent
verifier projection / QMV natural command-buffer bundle at approximately
35.648 ms/cycle.

P69B should isolate and optimize that measured projection path, beginning
with exact-shape microbenchmarking rather than assuming any single kernel
owns the entire buffer cost.

---

## P69B1 / P69B2-A — QMV shape census and wide screen

Date: 2026-08-23

### P69B1 — exact M4 affine-Q8 / GS64 runtime census

P69B1 instrumented `QuantizedMatmul::eval_gpu` in an isolated
P61 worktree and ran the frozen 29,297-token / 512-token D3/M4
ruler.

The run preserved the exact certified P61 trajectory:

- prompt tokens: 29,297
- completion tokens: 512
- output hash: `101ae2aec9793dfe`
- cycles: 186
- acceptance: 325/442 = 73.5%
- depth:
  - d1 = 155/186
  - d2 = 101/155
  - d3 = 69/101
- decode observation during the census run: 18.738 tok/s

The earlier salvage warning was only a parser-index bug:
the completion telemetry was emitted as `MTP[0]`, not `MTP[1]`.

Exact stock M4 affine-Q8 / GS64 runtime population:

- N=48, K=5120:
  - 17,856 calls
  - 96.000 calls/cycle
- N=5120, K=6144:
  - 11,973 calls
  - 64.371 calls/cycle
- N=1024, K=5120:
  - 6,090 calls
  - 32.742 calls/cycle
- N=17408, K=5120:
  - 138 calls
- N=5120, K=17408:
  - 69 calls
- N=12288, K=5120:
  - 69 calls

Total:

- 36,195 stock `dispatch_qmv` calls
- 194.597 calls/cycle
- zero M4 QMM/split-K fallbacks

The three dominant shapes account for:

- 35,919 / 36,195 calls
- 99.2375% of the measured stock M4 Q8 population

P69B1 report SHA256:

`5a101cba46f0cce020677ac59ba01ea10c454fd4670e698a28f3ae0069af4291`

### P69B2-A — forced affine `qmv_wide` screen

P69B2-A tested the existing MLX `qmv_wide` implementation against
stock `qmv_fast` on the three runtime-dominant shapes.

Results:

1. N=48, K=5120
   - stock median: 0.014065 ms/call
   - wide median: 0.018775 ms/call
   - wide: +33.49% slower
   - bit-exact parity: yes

2. N=5120, K=6144
   - stock median: 0.205920 ms/call
   - wide median: 0.395310 ms/call
   - wide: +91.97% slower
   - bit-exact parity: no
   - max abs diff: 0.0078125

3. N=1024, K=5120
   - stock median: 0.040210 ms/call
   - wide median: 0.071863 ms/call
   - wide: +78.72% slower
   - bit-exact parity: no
   - max abs diff: 0.03125

Top-three screening totals:

- stock: 15.922 ms/cycle
- forced wide: 29.602 ms/cycle
- forced wide penalty: 13.680 ms/cycle
- weighted stock/wide ratio: 0.5379x
- wide wins: 0/3

These weighted cycle values are microbenchmark screening estimates,
not promoted end-to-end ruler attribution.

Conclusion:

- close generic affine `qmv_wide` on M1 for this verifier workload
- do not promote any forced-wide route
- the existing MLX pre-gen15 affine-wide exclusion is strongly
  supported by the exact verifier workload
- next target is a dedicated M4 Q8 shared-weight kernel
- begin with K=6144 -> N=5120 because it dominates the stock
  microbenchmark opportunity at approximately 13.255 screened
  ms/cycle

P69B2-A report SHA256:

`809e1e9d4a9c5515850f6db991bb9c8b42c212d83c7241e6486cfdf95e9d0940`

### Next experiment

**P69B2-B — exact M4 Q8 shared-weight kernel**

First isolate only:

- M=4
- affine Q8
- group size 64
- FP16 input/output
- K=6144
- N=5120
- B=1

Preserve the stock Q8 arithmetic and per-vector accumulation order,
but load each Q8 weight field once and apply it to all four verifier
vectors.

Screen at least two output geometries before any frozen-ruler
promotion:

- SG2 x 4 output rows
- SG4 x 2 output rows

Require bit-exact microbenchmark parity before promotion.

---

## P69B2-B / P69B2-C — exact Q8 M4 shared-weight kernel

Date: 2026-08-23

### P69B2-B — dominant 6144 -> 5120 projection

A dedicated M=4 affine-Q8 / GS64 FP16 shared-weight kernel was
implemented in an isolated P61 worktree.

The kernel preserves stock Q8 arithmetic and each verifier vector's
FP32 accumulation order, but reads each group of Q8 weights once and
applies it to all four M vectors.

Two output geometries were screened:

- SG2 x 4 output rows
- SG4 x 2 output rows

Both were bit-exact over all eight parity probes.

Dominant K=6144 -> N=5120 result:

Stock:
- median: 0.206999 ms/call
- screened cost: 13.325 ms/cycle

SG2 x R4:
- median: 0.122041 ms/call
- speedup: 1.6961x
- reduction: 41.04%
- screened cost: 7.856 ms/cycle
- screened saving: 5.469 ms/cycle
- parity: exact, 0/163840 mismatches

SG4 x R2:
- median: 0.136397 ms/call
- speedup: 1.5176x
- reduction: 34.11%
- screened saving: 4.545 ms/cycle
- parity: exact

SG2 x R4 is the promoted geometry.

P69B2-B report SHA256:

`fd57b34ff2b7d4376430cc14bb00b5ee86b4c12242eb289eae3d706c03f20a17`

P69B2-B source patch SHA256:

`0c77b2e2db28f583b6ad6eeb2aba1d34eee8c0f4388a2024902aa5c6fe058221`

### P69B2-C — all three runtime-hot shapes

The same SG2 x R4 Metal arithmetic was retained unchanged.
Only the host gate was widened to the complete runtime-hot set:

- K=6144 -> N=5120
- K=5120 -> N=1024
- K=5120 -> N=48

All three shapes remained bit-exact across eight independent parity
probes per shape.

Results:

1. K=6144 -> N=5120
   - stock: 0.206655 ms/call
   - SG2R4: 0.121717 ms/call
   - speedup: 1.6978x
   - reduction: 41.10%
   - screened saving: 5.468 ms/cycle
   - exact: yes

2. K=5120 -> N=1024
   - stock: 0.036842 ms/call
   - SG2R4: 0.023017 ms/call
   - speedup: 1.6007x
   - reduction: 37.53%
   - screened saving: 0.453 ms/cycle
   - exact: yes

3. K=5120 -> N=48
   - stock: 0.004807 ms/call
   - SG2R4: 0.004681 ms/call
   - speedup: 1.0268x
   - reduction: 2.61%
   - screened saving: 0.012 ms/cycle
   - exact: yes

The three shapes cover:

- 35,919 / 36,195 stock M4-Q8 calls
- 99.2375% of the measured population

Aggregate microbenchmark screen:

- all-stock: 14.970 ms/cycle
- all-SG2R4: 9.038 ms/cycle
- screened saving: 5.932 ms/cycle
- screened reduction: 39.63%

These values remain screening estimates, not end-to-end attribution.

P69B2-C report SHA256:

`d39e79b7df41b51ccfa348f15f4818e1b63fded064da0ef5d66db37b5740eade`

P69B2-C source patch SHA256:

`3eaab0d7e92db7b0d5d496c76e1fa9d3c348506e6a9803a40842986347a4a9bb`

### Next experiment

**P69B3-A — frozen 3+3 integrated A/B**

Reconstruct the exact P61 runtime plus the P69B2-C patch and compare:

- BASE: P61 stack, SG2R4 route disabled
- CAND: identical stack with
  `MLX_P69B2_Q8_M4_SHARED=sg2r4`

Balanced run order:

- BASE-1
- CAND-1
- CAND-2
- BASE-2
- BASE-3
- CAND-3

Every run must retain:

- output hash `101ae2aec9793dfe`
- 512 completion tokens
- 186 cycles
- acceptance 325/442
- depth d1=155/186, d2=101/155, d3=69/101

Primary integrated metric:

- backbone milliseconds per cycle

Secondary metric:

- measured decode tokens/sec

---

## P69B3 — SG2R4 integrated certification and champion promotion

Date: 2026-08-23

P69B2 produced an exact M4 affine-Q8 / GS64 FP16 shared-weight
kernel using SG2 x 4 output rows.

The promoted route applies only to the three P69B1 runtime-hot
stock-QMV shapes:

- M=4, K=6144, N=5120
- M=4, K=5120, N=1024
- M=4, K=5120, N=48

The kernel retains stock Q8 arithmetic and per-vector FP32
accumulation order while sharing each Q8 weight load across all
four verifier vectors.

### P69B3-A — initial frozen 3+3

Balanced order:

- BASE
- CAND
- CAND
- BASE
- BASE
- CAND

All six runs retained the exact frozen trajectory:

- output hash: `101ae2aec9793dfe`
- prompt: 29,297 tokens
- completion: 512 tokens
- cycles: 186
- acceptance: 325/442 = 73.5%
- depth:
  - d1 = 155/186
  - d2 = 101/155
  - d3 = 69/101

P69B3-A result:

- BASE mean BPC: 141.1898 ms
- CAND mean BPC: 140.4226 ms
- mean BPC improvement: 0.543%
- mean BPC saving: 0.7672 ms/cycle
- paired BPC wins: 2/3

The first two pairs were positive:

- +2.374% BPC
- +1.729% BPC

The final candidate run suffered a broad simultaneous disturbance
across backbone, MTP, and cache and produced the negative third pair.

P69B3-A therefore remained positive but required controlled repeat.

P69B3-A summary SHA256:

`59a7098cdc896e33826d9daed9bc66fe449a859d6624a51f89d7aa00ec17ece7`

### P69B3-B — controlled 4+4 certification

A controlled repeat used:

- four adjacent matched BASE/CAND pairs
- mirrored pair order:
  - BASE -> CAND
  - CAND -> BASE
  - CAND -> BASE
  - BASE -> CAND
- 12-second idle cooldown between every frozen run
- no exclusion of disturbed runs from the statistics

All eight runs again retained the exact frozen hash and speculative
trajectory.

Controlled result:

BASE:

- mean TG: 18.6855 tok/s
- median TG: 18.6870 tok/s
- mean BPC: 144.8065 ms
- median BPC: 144.7836 ms
- BPC stdev: 0.0867 ms

SG2R4 candidate:

- mean TG: 19.0746 tok/s
- median TG: 19.0741 tok/s
- mean BPC: 141.8324 ms
- median BPC: 141.8309 ms
- BPC stdev: 0.0422 ms

Integrated deltas:

- mean TG: +2.083%
- mean BPC: +2.054% faster
- median BPC: +2.039% faster
- mean BPC saving: 2.9741 ms/cycle
- median BPC saving: 2.9527 ms/cycle

Adjacent paired BPC results:

1. +2.033% / +2.9430 ms/cycle
2. +2.042% / +2.9565 ms/cycle
3. +2.016% / +2.9194 ms/cycle
4. +2.123% / +3.0774 ms/cycle

Certification:

- BPC pair wins: 4/4
- median paired BPC improvement: +2.038%
- pooled 7+7 mean BPC improvement: +1.416%
- pooled 7+7 median BPC improvement: +2.017%
- microbenchmark screened saving: 5.9322 ms/cycle
- controlled integrated saving: 2.9741 ms/cycle
- microbenchmark -> integrated translation: 50.13%

Verdict:

**CERTIFIED CONTROLLED INTEGRATED WIN**

The P69 SG2R4 Q8 M4 shared-weight path is promoted as the new
project51 verifier-projection champion.

P69B3-B summary SHA256:

`e465d0d0cace9f6cd412e635263b52568bcf47eaa8391a6fdaaeabf1d6c286e3`

Certified source patch SHA256:

`3eaab0d7e92db7b0d5d496c76e1fa9d3c348506e6a9803a40842986347a4a9bb`

Canonical patch:

`experiments/p51-q8-verifier/patches/0012-p69b-q8-m4-shared-weight-sg2r4.patch`

### Promoted runtime switch

The exact certified route is enabled with:

`MLX_P69B2_Q8_M4_SHARED=sg2r4`

The environment gate is deliberately retained in the promoted source
so the committed code remains byte-identical to the source used in
P69B3-A/B certification.

### Current preferred stack

The preferred stack is now:

- fixed D3 / verifier M4
- P54F verifier QMM routing
- lm_head NSG8 / BN4
- P58 FP16 GDN fused verifier prework
- native 256-block SDPA reduction topology
- P61 HPT2 HEADPAIR K/V reuse
- P69 SG2R4 Q8 M4 shared-weight projection path
- exact frozen speculative trajectory

### Next experiment

**P69B4 — post-champion residual projection-bundle profile**

Do not immediately optimize another assumed kernel.

First repeat the passive natural command-buffer profiler with the
certified SG2R4 route enabled and the exact frozen ruler.

Goals:

1. measure the residual projection/QMV natural-CB archetype after the
   certified ~2.97 ms/cycle integrated reduction;
2. determine whether the next largest residual component is:
   - remaining stock QMV tail,
   - verifier custom QMM,
   - RMS/gather/activation/add,
   - or a different command-buffer archetype;
3. choose the next optimization from post-P69 evidence rather than
   the pre-P69 profile.

Do not reopen closed D2/D4, tree speculation, HPT3/HPT4, learned
hidden correction, or P61-attention geometry without new evidence.

---

## P69B4 — post-champion residual natural-command-buffer profile

Date: 2026-08-23

P69B4 repeated the passive natural command-buffer profiler on the
canonical P69 SG2R4 champion.

The profiling worktree was created directly from canonical champion
commit:

`c55992a62e2844dd22b28b39f29fdeba61a30bb8`

No historical P61 or P69 performance patch was replayed.

Only the proven metadata-only natural command-buffer instrumentation
was added.

The frozen request retained the exact trajectory:

- output hash: `101ae2aec9793dfe`
- prompt: 29,297 tokens
- completion: 512
- cycles: 186
- acceptance: 325/442 = 73.5%
- d1 = 155/186
- d2 = 101/155
- d3 = 69/101

Observed profiler telemetry:

- backbone: 26,333.4 ms
- MTP: 327.5 ms
- sampling: 5.1 ms
- cache: 73.2 ms

The natural dataset contained:

- 29,626 decode command buffers
- 31,860 total recorded natural command buffers
- 93 registered exact kernels

### Pre-P69 vs post-P69 natural GPU cycle

Pre-P69:

- 135.544 ms/cycle

Post-P69:

- 133.323 ms/cycle

Difference:

- -2.221 ms/cycle
- 1.64% reduction

This is observational profiler evidence only.
P69B3-B remains the authoritative performance certification.

### QMV population transition

Pre-P69 stock QMV dispatches:

- 40,155

Post-P69 stock QMV dispatches:

- 4,236

Promoted SG2R4 dispatches:

- 35,919

Therefore P69 moved essentially the complete previously identified
runtime-hot M4-Q8 stock-QMV population onto SG2R4 while leaving the
small stock-QMV tail.

### Post-P69 direct natural-buffer archetypes

Largest directly measured archetypes:

1. projection / verifier bundle
   - 33.114 ms/cycle
   - 8,550 occurrences
   - 45.968 buffers/cycle
   - median 0.72037 ms
   - includes SG2R4, KP1 verifier QMM, RMS, gather/add/activation

2. P61 attention bundle
   - 24.183 ms/cycle
   - 2,944 occurrences
   - 15.828 buffers/cycle
   - median 1.52788 ms

3. projection + GDN bundle
   - 18.959 ms/cycle
   - 5,330 occurrences
   - 28.656 buffers/cycle

4. residual stock-QMV bundle
   - 12.656 ms/cycle
   - 556 occurrences
   - 2.989 buffers/cycle
   - contains three stock `affine_qmv_fast` dispatches

Additional recurring projection bundles:

- 11.435 ms/cycle
- 11.198 ms/cycle
- 9.600 ms/cycle

The projection path therefore remains the largest directly measured
residual target after P69.

### Exact verifier-QMM dispatch census from P69B4

The post-P69 frozen trajectory contains:

KP1 verifier QMM:

- kernel id 78
- 32,736 dispatches
- exactly 176 dispatches/cycle

KP2 verifier QMM:

- kernel id 75
- 23,808 dispatches
- exactly 128 dispatches/cycle

lm_head verifier QMM:

- kernel id 83
- 186 dispatches
- exactly 1 dispatch/cycle

SG2R4 M4-Q8:

- kernel id 76
- 35,919 dispatches

This makes the recurring KP1/KP2 verifier QMM path the next
projection component requiring exact source/shape analysis.

### Regression caution

Coarse family NNLS:

- R² = 0.148068

Exact-kernel NNLS:

- R² = 0.683619

The exact-kernel model is improved relative to pre-P69 but remains
too weak for isolated attribution.

In particular it assigns zero modeled cost to the heavily exercised
SG2R4 kernel, demonstrating that individual NNLS coefficients must
not be treated as kernel timings.

Direct natural-buffer archetypes and controlled A/B remain the
promotion standard.

### P69B4 artifacts

Natural profile SHA256:

`cefecaa856549f45d4b3e3f035d06c8d78aea8c1a4d7463874725f5b3f90cc50`

Offline solve SHA256:

`f2485a427b6038eb027a30980777cf3f71c95d618f6689eb9c460ba86f1e9d8e`

Matched-signature audit SHA256:

`9933f0d7dad47646290595042cd571db88b053652b54e4543816915cba23bef8`

Pre/post comparison SHA256:

`13d5da2c9c46f3de83bb74a1fabfdde8b07f5bbd124b255efe7e16b56219dd33`

### Next experiment

**P69B5-A — verifier KP1/KP2 source and shape-routing audit**

Before changing verifier QMM arithmetic or geometry:

1. locate the exact oMLX implementation that creates the
   `omlx_vk_ks_m4_q8_kp1` and `kp2` kernels;
2. inspect the existing `OMLX_VERIFY_TRACE_SHAPES` implementation;
3. determine whether it reports every dispatch or only unique route
   decisions;
4. identify the exact `(K,N,K_PARTS)` population feeding KP1 and KP2;
5. only then build shape-specific bit-exact microbenchmarks.

Do not optimize the P61 attention bundle merely because it remains
large; that workstream remains closed absent new evidence.

---

## P69B5 — verifier-QMM residual investigation

Date: 2026-08-23

P69B5 investigated whether the custom verifier QMM kernels inside the
largest post-P69 projection bundle contained another actionable
optimization.

### P69B5-B1 — verifier router audit

The exact verifier routing implementation is in:

`omlx/patches/qwen35_verify_qmm.py`

For non-lm_head verifier shapes, `vk_qmm()` selects K_PARTS using:

1. global `OMLX_VERIFY_KPARTS`, if set;
2. shape-specific `OMLX_VERIFY_KPARTS_SHAPES`, if present;
3. otherwise K_PARTS=2 for N >= 4096 and K_PARTS=4 below that.

The certified shape overrides remain:

- 5120x6144 -> KP1
- 5120x17408 -> KP1

The existing `OMLX_VERIFY_TRACE_SHAPES` mechanism records unique
signatures only and is not a dispatch census.

### P69B5-B2 — exact runtime census

One exact frozen run reproduced all 56,730 verifier-routed calls:

KP1:

- 32,736 calls
- exactly 176/cycle

KP2:

- 23,808 calls
- exactly 128/cycle

lm_head MSG:

- 186 calls
- exactly 1/cycle

Exact shape population:

- M4 K5120 N17408 Q8 GS64 KP1: 128/cycle
- M4 K17408 N5120 Q8 GS64 KP2: 64/cycle
- M4 K5120 N6144 Q8 GS64 KP1: 48/cycle
- M4 K5120 N10240 Q8 GS64 KP2: 48/cycle
- M4 K5120 N12288 Q8 GS64 KP2: 16/cycle
- M4 K5120 N248320 Q8 GS64 MSG: 1/cycle

### P69B5-C1 — KP1 no-barrier scout

Candidate:

- preserve Q8 unpack/FMA traversal;
- preserve FP32 accumulation;
- preserve `simd_sum`;
- remove the redundant K_PARTS=1 threadgroup
  partial-store/barrier/reload sequence;
- directly write the already-reduced SIMD accumulator.

Both exact KP1 shapes were bit-exact.

Results:

K5120 N17408:

- +0.2832% median microbench reduction
- projected +0.188935 ms/cycle

K5120 N6144:

- -1.7501% median microbench reduction
- projected -0.275900 ms/cycle

Combined:

- projected -0.086966 ms/cycle
- -0.1054%

Verdict:

**CLOSED — KP1 no-barrier specialization does not pay.**

### P69B5-C2 — KP2 parallel partial-store scout

Candidate changed only partial staging after `simd_sum`:

Stock:

- lane 0 serially writes all 16 reduced accumulators.

Candidate:

- lanes 0..15 each write one accumulator.

The barrier and two-part reduction order were unchanged.

All three exact KP2 shapes were bit-exact.

Microbench:

- K17408 N5120: +0.3878%
- K5120 N10240: +1.8020%
- K5120 N12288: +0.2579%

Weighted isolated projection:

- +0.524599 ms/cycle
- +0.8399%

This justified an integrated scout but was not itself promotion
evidence.

### P69B5-D1 — controlled integrated 4+4

Balanced order:

- BASE / CAND
- CAND / BASE
- CAND / BASE
- BASE / CAND

Every measured run retained:

- output hash `101ae2aec9793dfe`
- 186 cycles
- acceptance 325/442 = 73.5%
- d1=155/186
- d2=101/155
- d3=69/101

Results:

BASE mean BPC:

- 141.743817 ms

CAND mean BPC:

- 141.913575 ms

Mean candidate change:

- -0.169758 ms/cycle
- -0.1198%

BASE median BPC:

- 141.709946 ms

CAND median BPC:

- 141.886022 ms

Median candidate change:

- -0.176075 ms/cycle
- -0.1243%

Mean TG change:

- -0.1058%

Adjacent pair wins:

- 1/4

Median pair change:

- -0.1242%

Verdict:

**NO CONTROLLED INTEGRATED WIN.**

The isolated C2 microbenchmark improvement did not translate into the
real natural execution stack.

### P69B5 conclusion

Close verifier-QMM synchronization/staging work.

Do not integrate:

- KP1 no-barrier specialization;
- KP2 parallel partial-store specialization.

The custom verifier QMM kernels remain part of the projection bundle,
but current evidence does not support further synchronization-level
tuning.

Return to the largest post-P69 natural-buffer archetype and map the
remaining non-QMM components:

- RMS
- fused sigmoid/multiply activation
- gather
- add
- associated copy/indexing kernels

P61 attention remains closed absent new evidence.

### P69B5 artifact hashes

B1 router audit:

`f8b5adeb8d75918ec3294eab42f2a26f3308d6882b6667837dcc7c76df73446b`

B2 runtime census:

`6410456ba36cca82275ede3060e22cf06c120c507f32e948d15d8f44341c4e7c`

C1 KP1 microbench:

`b8a01c886e72d4a9e1b405847c7387b7bdda6eb280dff9e77d8558506c2e22d2`

C2 KP2 microbench:

`784b015622bc2a9d2130f54584eb7538f0e9bcafb2bd8c9cadf6fcca8fc36234`

D1 integrated 4+4 summary:

`500f3c1692dea9c0fdef04da2f0d4dd2d69c3c69698f0106bb50af79704943ec`

### Next experiment

**P69B6-A — dominant projection-bundle source and operation map**

Goal:

Map the exact non-QMM kernel identities in the 33.114 ms/cycle
natural command-buffer archetype back to MLX/oMLX/model operations
before selecting another performance candidate.

## P69B6 — structural projection-bundle and MLP fusion

P69B6 followed the post-P69B4 residual profile after
P69B5 closed further verifier-QMM synchronization tuning.

The dominant natural command-buffer archetype was:

- approximately 33.114 ms/backbone-cycle
- approximately 45.968 occurrences/cycle
- mixed RMS / elementwise / gather / QMM work

Static model/source mapping established:

- 64 decoder layers
- 48 Gated DeltaNet layers
- 16 full-attention layers
- hidden size 5120

The approximately 45.968/cycle dominant archetype therefore
tracks the 48-layer GDN path very closely.

### P69B6-D — residual ADD -> RMS fusion

The first structural candidate fused:

    h = x + residual
    n = post_attention_RMS(h)

into a two-output Metal kernel returning both:

    h
    n

The kernel copied the canonical MLX `rms_loopedfloat16`
reduction topology and explicitly rounded the residual result
to FP16 before RMS accumulation.

P69B6-D2 exact M=4 / D=5120 microbenchmark:

- exact cases: 8/8
- stock median: 0.235274 ms
- fused median: 0.226806 ms
- isolated reduction: +3.60%
- round wins: 10/11
- projected saving: +0.541947 ms/backbone-cycle

P69B6-D3 then tested the candidate in the frozen integrated
29,297-token workload.

The isolated gain did not translate.

Controlled result:

- pair wins: 1/4
- mean saving: approximately +0.020 ms/cycle
- median result: regression
- microbenchmark translation: approximately 3.7%

Conclusion:

Close the residual ADD -> RMS fusion candidate.

This reinforces the rule established by P69B5:

small isolated kernel wins are not sufficient when natural
execution does not remove enough meaningful graph work.

D3 evidence SHA256:

    c915d2a6fddfc12213defb2e194ef7d3ec2c9be562daa86635ba5a3be00649da

### P69B6-E1 — exact MLP attribution

P69B6-E1 identified the remaining large elementwise population.

Natural kernel counts:

- id26: 8,928 total = exactly 48/cycle
- id28: 12,460 total = 66.989/cycle

id26 therefore belongs to the 48-layer GDN path.

The target-verifier MLP projection census was exact:

- K5120 -> N17408: 23,808 calls
  = 128/cycle
  = gate_proj + up_proj across 64 decoder layers
- K17408 -> N5120: 11,904 calls
  = 64/cycle
  = one down_proj per decoder layer

The active MLP formula is:

    gate, up = target_verify_linears(
        gate_proj,
        up_proj,
        x,
    )

    y = swiglu(gate, up)

    out = target_verify_linear(
        down_proj,
        y,
    )

The id28 population contains one target MLP activation call
per decoder layer plus a small approximately 2.989/cycle
side/MTP population.

E1 evidence SHA256:

    3cbfb8a71c522f359c9f7ed38b9e266fcef723f87c498390dba35b06fe829390

### P69B6-E2 — dual Q8 gate/up QMM + SWIGLU

A down-projection input-fusion design was rejected before
implementation because down_proj is tiled over output
columns and would recompute SWIGLU values across many output
tiles.

Instead P69B6-E2 fused the two independent gate/up Q8
projections with the immediately following SWIGLU.

The candidate preserves:

- M=4
- K=5120
- N=17408
- Q8 affine
- group size 64
- K_PARTS=1
- original per-projection packed-weight traversal
- original FP32 accumulation order
- original `simd_sum`
- FP16 projection-output rounding before SWIGLU
- exact MLX sigmoid / SiLU arithmetic

It writes only the final 4x17408 SWIGLU tensor, eliminating:

- gate device materialization
- up device materialization
- the standalone SWIGLU dispatch

Two geometries were tested.

DUAL32:

- one SIMD group
- gate and up accumulators live together
- input x loads reused
- exact
- 11/11 timing wins
- +1.03% isolated
- projected +0.544378 ms/cycle

DUAL64:

- two SIMD groups
- one projection per SIMD group
- lower register pressure
- exact
- 11/11 timing wins
- stock median: 0.827652 ms
- DUAL64 median: 0.773999 ms
- isolated reduction: +6.48%
- projected +3.433822 ms/cycle

DUAL64 decisively beat DUAL32 and advanced.

E2 evidence SHA256:

    8371ceab179d7b775d27f76cff7b5ffdf15381b48e54ac9c2919b05867dc9676

### P69B6-E3 — DUAL64 controlled integrated certification scout

Balanced order:

- BASE-1
- CAND-1
- CAND-2
- BASE-2
- CAND-3
- BASE-3
- BASE-4
- CAND-4

Every valid run retained exactly:

- output hash: 101ae2aec9793dfe
- 512 generated tokens
- 186 verifier cycles
- acceptance: 325/442 = 73.5%
- depth:
  - d1=155/186
  - d2=101/155
  - d3=69/101

Every candidate run additionally self-reported that the
DUAL64 MLP path was actually engaged.

BASE mean:

- backbone/cycle: 141.821371 ms
- TG: 19.054934 tok/s

DUAL64 mean:

- backbone/cycle: 140.473387 ms
- TG: 19.210250 tok/s

Controlled mean delta:

- -1.347984 ms/backbone-cycle
- +0.9505% backbone efficiency
- +0.8151% realized TG

Median delta:

- -1.536828 ms/backbone-cycle
- +1.0838%

Adjacent pairs:

- pair 1: +0.4151%
- pair 2: +1.1581%
- pair 3: +1.2019%
- pair 4: +1.0266%
- pair wins: 4/4
- median pair improvement: +1.0923%

Microbenchmark -> integrated translation:

- E2 projected: +3.433822 ms/cycle
- E3 controlled: +1.347984 ms/cycle
- translation: 39.26%

Verdict:

P69B6-E3 is a controlled integrated win.

The important structural lesson is that meaningful graph-level
work elimination can translate where small local kernel
optimizations did not.

DUAL64 removes two large 4x17408 intermediate writes plus the
standalone SWIGLU dispatch while preserving the down_proj
verifier path unchanged.

E3 summary SHA256:

    2339cddba8da68dcd18d45b203386f845997d780edddac4788ce2f4ba056bddf

### P69B6 promotion state

DUAL64 is now a certified promotion candidate.

However, the E3 implementation was injected temporarily via
an isolated `sitecustomize.py` hook.

Therefore it is not yet considered part of the permanent
runtime stack.

Next:

Package the exact DUAL64 implementation into the normal
oMLX verifier patch path, guarded to:

- target verify only
- batch 1
- M=4
- K=5120
- N=17408
- Q8 affine
- GS64
- FP16

Leave the existing certified down_proj QMM path untouched.

Then re-run a controlled packaged-form certification.

Only after the packaged implementation reproduces the E3
win should DUAL64 receive a permanent runtime patch/tag and
be added to the preferred stack.

### P69B6-E4 — packaged DUAL64 certification and promotion

P69B6-E4 moved the E3-winning DUAL64 implementation out of
the temporary `sitecustomize.py` experiment and into the
normal oMLX patch mechanism.

The packaged change consists of two source changes:

- a new `omlx/patches/qwen35_dual64_mlp.py` implementation
- an installer hook in
  `omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py`

The runtime gate is:

    OMLX_VERIFY_MLP_DUAL64=1

The wrapper is installed in both BASE and CAND processes.
Only the runtime gate differs between arms.

Eligibility remains deliberately narrow:

- target verify only
- batch 1
- verifier M=4
- K=5120
- N=17408
- Q8 affine
- group size 64
- FP16 input / scales / biases
- exact packed Q8 geometry
- existing down_proj verifier path unchanged

The packaged implementation preserves the E2/E3 arithmetic
discipline:

- original gate projection Q8 traversal
- original up projection Q8 traversal
- independent FP32 accumulators
- original `simd_sum` reduction order
- FP16 rounding at each projection-output boundary
- exact MLX sigmoid / SiLU arithmetic
- only the final 4x17408 SWIGLU tensor is materialized

Therefore it removes:

- the 4x17408 gate device tensor
- the 4x17408 up device tensor
- the standalone SWIGLU dispatch

without changing the downstream K17408 -> N5120 down_proj.

#### E4 packaged controlled 4+4

Balanced order:

- BASE-1
- CAND-1
- CAND-2
- BASE-2
- CAND-3
- BASE-3
- BASE-4
- CAND-4

All eight valid runs retained exactly:

- output hash: 101ae2aec9793dfe
- generation: 512 tokens
- verifier cycles: 186
- acceptance: 325/442 = 73.5%
- depth:
  - d1=155/186
  - d2=101/155
  - d3=69/101

Every BASE run self-reported that the packaged wrapper was
installed with DUAL64 disabled.

Every CAND run self-reported:

- packaged wrapper installed
- DUAL64 enabled
- DUAL64 actually engaged on the exact M=4 / Q8 / GS64 path

BASE:

- mean backbone/cycle: 141.780914 ms
- median backbone/cycle: 141.768548 ms
- mean TG: 19.063826 tok/s

DUAL64:

- mean backbone/cycle: 140.266801 ms
- median backbone/cycle: 140.270699 ms
- mean TG: 19.249275 tok/s

Controlled packaged delta:

- mean saving: 1.514113 ms/backbone-cycle
- median saving: 1.497849 ms/backbone-cycle
- mean backbone improvement: +1.0679%
- median backbone improvement: +1.0565%
- mean realized TG improvement: +0.9728%

Adjacent paired improvements:

- pair 1: +0.9028%
- pair 2: +1.1217%
- pair 3: +1.0388%
- pair 4: +1.2080%
- pair wins: 4/4
- median pair improvement: +1.0802%

Microbenchmark translation:

- E2 projected saving: 3.433822 ms/cycle
- E4 packaged saving: 1.514113 ms/cycle
- translation: 44.09%

E3-to-E4 reproduction:

- E3 temporary-hook mean saving: 1.347984 ms/cycle
- E4 packaged mean saving: 1.514113 ms/cycle
- packaged reproduction: 112.32%

This is stronger than the promotion threshold and reproduces
the E3 result with the actual durable package architecture.

Verdict:

P69B6 DUAL64 is certified and promoted.

The exact promoted patch artifact is:

    experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch

Patch SHA256:

    1f959d680a98af32ad70b909ede3375eb198b8e76dc439ef300a31fed80662d0

E4 controlled-summary SHA256:

    2bab5354a3fb0bde4a7810fc9e3693bf51e18831e0c328d6056d8b6f2c19dcec

E4 promotion-manifest SHA256:

    7b9779f06a7dae4ab56e5d6fa873d9689e257392fc12a7a0edaad8c5a5cbab20

#### Preferred verifier stack after P69B6

The preferred ~29.3K fixed-D3 / verifier-M4 stack is now the
previous P69B3-certified stack plus:

    OMLX_VERIFY_MLP_DUAL64=1

when the promoted `0014-p69b6-dual64-q8-mlp.patch` oMLX patch is applied.

The packaged E4 candidate establishes a new measured mean in
this certification session:

- 19.249275 tok/s
- 140.266801 ms/backbone-cycle
- 186 cycles
- acceptance 325/442
- output hash 101ae2aec9793dfe

The paired delta, rather than the cross-session absolute
number, remains the primary certification evidence.

P69B6 is complete.

Next:

Re-profile natural command-buffer execution with the complete
P69B6 stack enabled.

Do not use the old pre-DUAL64 MLP activation / command-buffer
ranking as the next optimization priority without measuring
the new residual profile first.

### P69B7 — post-DUAL64 natural residual profile

P69B7 re-profiled the complete promoted verifier stack after
P69B6 DUAL64.

P69B7-A passive natural-CB dataset:

- raw profiler command-buffer rows: 31,860
- registered kernels: 94
- natural decode buffers in the measured window: 29,626
- verifier cycles: 186
- acceptance: 325/442
- depth: d1=155/186, d2=101/155, d3=69/101
- output hash: 101ae2aec9793dfe
- DUAL64 engagement observed
- P61 HEADPAIR observed
- SG2R4 observed

P69B7-A server-log SHA256:

    7e51c443565200c61158c7008053d1046c25e45f47bcece0fe932826acbfbd49

P69B7-B natural-CB solve SHA256:

    289a8dbe7ed06dfde6f8106f6f9d72b33cc8aa1c8c40ff62959d93175d217bbc

P69B7-C matched-signature report SHA256:

    aed43c499ad199e2b2118590e2ffd0b95a7d55e00db441d0842d14a183ca23ff

P69B7-D B4->B7 residual comparison SHA256:

    635e5f5d8a8f3b9f8ce2087f71a9af812139f43d9d7a87f2d67fce333b72f902

P69B7-E GDN source-seam audit SHA256:

    184891b6437f3950c89a8b37bc877e22f909349b5cd52fbd6b2b43426a8f09ba

Observational B4 -> B7 transition:

- natural GPU:
  - B4: 133.323 ms/cycle
  - B7: 132.659 ms/cycle
  - delta: -0.664 ms/cycle
  - improvement: +0.498%

- telemetry backbone:
  - B4: 141.577419 ms/cycle
  - B7: 139.641398 ms/cycle
  - delta: -1.936022 ms/cycle
  - improvement: +1.3675%

These are cross-session passive-profile numbers. The controlled
P69B6-E4 result remains the authoritative DUAL64 performance
certification.

The structural graph accounting is exact:

- standalone target-MLP SWIGLU:
  - 12,460 -> 556
  - delta = -11,904
  - exactly -64/cycle

- DUAL64:
  - 0 -> 11,904
  - exactly +64/cycle

- verifier QMM:
  - 56,730 -> 32,922
  - delta = -23,808
  - exactly -128/cycle

Therefore the promoted fusion removed exactly the intended two
gate/up verifier-QMM dispatches plus the standalone target-MLP
SWIGLU population for all 64 decoder layers.

The direct post-DUAL64 natural-buffer archetypes are now led by:

1. 46.978/cycle, 33.742 ms/cycle
   - approximately the 48 GDN-layer frequency

2. 15.828/cycle, 24.168 ms/cycle
   - approximately the 16 full-attention-layer frequency
   - includes P61 HEADPAIR SDPA

3. 29.306/cycle, 19.206 ms/cycle
   - mixed GDN / projection bundle

5. 15.984/cycle, 11.410 ms/cycle
   - approximately the 16 full-attention-layer frequency
   - includes attention-side gating/postprocessing plus the MLP

P69B7 closes the pre-DUAL64 residual profile. Future candidate
selection must use the post-DUAL64 B7 topology.


### P69B8-A — exact GDN RMSNormGated fusion microbench

Source seam:

    out = self.norm(out, z)

where Qwen3_5RMSNormGated performs:

    x = mx.fast.rms_norm(hidden_states, self.weight, self.eps)
    return _precise_swiglu(hidden_states, gate, x)

A custom 32-thread Metal kernel reproduced the exact MLX
128-wide RMS reduction:

- one SIMD group
- four values/lane
- FP32 squared accumulation
- simd_sum reduction
- metal::precise::rsqrt
- stock FP16 weighted-RMS rounding boundary
- existing FP32 precise SiLU/gating arithmetic

Real model norm weight was used:

- shape: 128
- dtype: FP16
- observed range: 0.78515625 .. 0.9296875

Exactness:

- 8/8 dynamic-range sweeps bit-exact
- zero-hidden adversarial case exact
- constant-row adversarial case exact
- alternating-sign adversarial case exact

Timing over 11 balanced rounds / 128 batched invocations:

- stock median: 0.006983070 ms/layer
- fused median: 0.005086258 ms/layer
- local saving: +0.001896813 ms/layer
- local reduction: +27.1630%
- wins: 10/11
- projected 48-layer saving: +0.091047 ms/cycle

Report SHA256:

    adf089f1407cfffea86f5553d19e015d04299c541fd904dba61556835ca20cc9

Decision:

P69B8 RMSNormGated fusion is CLOSED WITHOUT integrated
certification.

Reason:

The local kernel optimization is real and bit-exact, but its
absolute leverage is too small.

At the P69B7 telemetry backbone of ~139.64 ms/cycle, the
microbench projection is only ~0.065% of a cycle even assuming
an impossible 100% translation.

For comparison, the closed P69B6-D ADD_RMS experiment projected
roughly 0.542 ms/cycle yet translated to only ~0.020 ms/cycle
integrated.

A 4+4 certification for a 0.091 ms/cycle theoretical ceiling is
not a good use of the frozen ruler.

No runtime change is promoted from P69B8.

Next:

P69B9 should inspect the 16-layer full-attention residual
topology.

The first structural seam to audit is not a standalone
sigmoid/multiply fusion and not sigmoid-on-load inside o_proj.

Instead inspect whether the already-promoted P61 HEADPAIR SDPA
kernel can apply the attention gate as an exact output epilogue:

    output * mx.sigmoid(gate)

before the existing o_proj.

This could remove the standalone gate postprocessing and the
ungated attention-output materialization without recomputing
the Q8 output projection.

### P69B9-A — full-attention gated SDPA seam audit

P69B9-A audited the post-DUAL64 16-layer full-attention
residual topology.

Report SHA256:

    5789f103ff8b02a6a81fef6b7b629a8be8177af7400d94670be1da1eefaff46c

Model geometry:

- hidden size: 5120
- decoder layers: 64
- full-attention interval: 4
- therefore full-attention layers: 16
- attention heads: 24
- KV heads: 4
- head dimension: 256

Active attention source ends with:

    output = output.transpose(0, 2, 1, 3).reshape(B, L, -1)

    return _target_verify_linear(
        self.o_proj,
        output * mx.sigmoid(gate),
        target_verify,
    )

Post-DUAL64 direct natural-buffer evidence includes two strong
approximately-16-layer-frequency bundles:

- rank 2:
  - 15.828/cycle
  - 24.168 ms/cycle
  - includes P61 HEADPAIR SDPA

- rank 5:
  - 15.984/cycle
  - 11.410 ms/cycle
  - includes the attention-side sigmoid/multiply/postprocessing
    and output projection context

P61 HEADPAIR population:

- 2,976 launches in 186 verifier cycles
- exactly 16.000/cycle

P61 patch SHA256:

    1875a72869f8e21d30cb4c4ded19e647d434faa4f8e4287a2263f1559fa1ec06

Important source refinement:

The first P69B9 hypothesis was to put the gate directly into
P61 HEADPAIR.

Do NOT do this.

P61 HEADPAIR is the specialized SDPA two-pass PASS-1 kernel:

    sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair

It computes per-block partial attention outputs and stores:

    op[x] = static_cast<T>(o[j][x])

along with per-block sums and maxima.

Those partials are subsequently consumed by:

    sdpa_vector_2pass_2

which performs the final cross-block max/sum/partial reduction.

Therefore applying the attention gate in HEADPAIR pass-1 would
gate partial values before the final SDPA aggregation and would
not preserve the stock computation graph.

Correct structural seam:

    sdpa_vector_2pass_2

The stock pass-2 kernel performs the final aggregation and ends
with:

    out[i] = static_cast<T>(o[i]);

This is the correct place to investigate an exact attention-gate
epilogue.

Candidate P69B9-B:

Extend/specialize the verifier-M4 SDPA pass-2 final-output path
so that after the normal SDPA accumulator has been finalized it:

1. preserves the existing SDPA FP16 rounding boundary;

2. reads the corresponding FP16 attention gate element;

3. reproduces the stock FP16 sigmoid semantics exactly;

4. reproduces the stock FP16 multiply boundary exactly;

5. writes the final gated FP16 attention activation;

6. leaves the existing K6144 -> N5120 o_proj verifier route
   completely unchanged.

Target verifier geometry:

- B=1
- L/M=4
- H=24
- D=256
- output width=6144
- 16 full-attention layers/cycle

Gate-layout caution:

The SDPA pass-2 output is logically head-major during the kernel
([B,H,L,D]), while the Python gate is logically
[B,L,H,D] / [B,L,6144].

A P69B9-B implementation must map:

    (batch, head, q_row, d)

to the corresponding gate element:

    (batch, q_row, head, d)

exactly once per final attention output element.

Do not change SDPA accumulation order.

Do not change P61 HEADPAIR geometry.

Do not compute the gate inside o_proj output tiles; that would
repeat the gate work across projection tiles.

P69B9-B should begin with exactness + isolated microbenchmark,
not an integrated 4+4.

Promotion rule:

Advance to controlled integrated testing only if the fused
pass-2 epilogue is bit-exact and its measured absolute
ms/cycle projection is large enough to justify the frozen-ruler
cost.

P69B8 remains closed.

P69B6 DUAL64 remains the latest promoted optimization.

Next experiment:

    P69B9-B — gated SDPA pass-2 final-output epilogue
    exactness and microbenchmark.

