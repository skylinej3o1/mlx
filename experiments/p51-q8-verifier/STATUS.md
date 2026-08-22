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
