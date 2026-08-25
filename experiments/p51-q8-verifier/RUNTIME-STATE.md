# P51 verifier promoted runtime state

This document is the durable bridge between Git history and the live runtime
used by the `project51-q8-verifier` experiments.

`STATUS.md` records experimental decisions. This file records the additional
runtime invariants that must be true before those decisions are assumed to be
live.

## Why this exists

The project has two independent state domains:

1. the Git checkout / fork, including MLX source changes and recorded patches;
2. installed runtime state, especially the Homebrew `omlx` package and the
   imported/compiled MLX package used by the benchmark environment.

A clean Git checkout does not prove that the Homebrew package still contains
promoted Python-side patches. A package reinstall, refresh, or experimental
source restoration can overwrite installed files without changing Git.

Therefore every new terminal and every new chat must validate both domains.

## Canonical runtime ownership

### Shell / project environment

```text
venv: /Users/skylinej17/.venvs/mlx-dspark
repo: ~/src/mlx-m1-qmv
branch: project51-q8-verifier
```

### Homebrew oMLX

```text
command: /opt/homebrew/bin/omlx
version: 0.6.3rc2
owning Python: /opt/homebrew/Cellar/omlx/0.6.3rc2/libexec/bin/python3.11
mlx-vlm in oMLX runtime: 0.6.3
mlx in oMLX runtime: 0.32.0
```

Do not assume the activated `mlx-dspark` Python owns `omlx`.

## Current promoted verifier stack

The post-P69B10 champion stack keeps:

- **P58** FP16 GDN fused verifier prework;
- **P61** HEADPAIR HPT2 SDPA;
- **P69B3** SG2R4 Q8 M4 shared-weight projection;
- **P69B6** packaged DUAL64 verifier MLP fusion.

Closed work that must not be silently reintroduced:

- P69B8 RMSNormGated fusion;
- P69B9 attention-gate final epilogue;
- P69B10-C recurrent final-state alias.

## Component ownership and validation

### P58 — Homebrew oMLX Python source

Recorded patch:

```text
experiments/p51-q8-verifier/patches/0011-p58-fp16-gdn-verify-prework.patch
```

Live file:

```text
.../site-packages/omlx/patches/qwen35_gdn_prework.py
```

Required structural signatures include:

```text
OMLX_GDN_VERIFY_PREWORK_FP16
inputs.dtype not in (mx.bfloat16, mx.float16)
conv_state.dtype != inputs.dtype
self.conv1d.weight.dtype != inputs.dtype
dtype=inputs.dtype
```

### P61 — MLX source and compiled/imported MLX runtime

Recorded patch:

```text
experiments/p51-q8-verifier/patches/0013-p61-headpair-hpt2-sdpa.patch
```

Required source/runtime signatures include:

```text
MLX_SDPA_GQA6_M4_HPT2_HEADPAIR
sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair
```

The validator checks both the repository source and the imported MLX package
for the compiled gate string.

### P69B3 — MLX source and compiled/imported MLX runtime

Recorded patch:

```text
experiments/p51-q8-verifier/patches/0012-p69b-q8-m4-shared-weight-sg2r4.patch
```

Required source/runtime signatures include:

```text
MLX_P69B2_Q8_M4_SHARED
P69B2B_Q8_M4_SHARED_WEIGHT
```

The promoted runtime value is `sg2r4`.

### P69B6 — Homebrew oMLX Python source

Recorded patch:

```text
experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch
```

Required runtime signatures include:

```text
OMLX_VERIFY_MLP_DUAL64
P69B6_E4_DUAL64
omlx_p69b6_dual64_q8_gs64_m4_k5120_n17408
_apply_p69b6_dual64_mlp
```

## 2026-08-25 runtime-drift incident

While beginning P69B11-A, Git was clean and synchronized, but the live
Homebrew file `qwen35_gdn_prework.py` was discovered to be pre-P58.

Observed pre-P58 SHA256:

```text
af5e949e9d0dad8b14d87717db773d5366926dee9efef1efe822297c46bf5ed5
```

Recorded P58 patch SHA256:

```text
f3e3a99a8caf363821570db10b7d73d00aed0cdca4af8628a299fa5c3eb95c02
```

The live source had:

- zero `OMLX_GDN_VERIFY_PREWORK_FP16` occurrences;
- zero `mx.float16` occurrences;
- the old BF16-only eligibility checks.

This proves Git cleanliness alone is insufficient for this project. The cause
of the overwrite was not established and must not be guessed.

## Current experiment handoff

P69B11-A selected the next candidate from the remaining measured high-leverage
structure:

**asymmetric GDN QKV + Z input-projection bundle**.

The exact installed Qwen3.5 source confirmed both projections consume the same
GDN input through `_target_verify_linears`.

Measured frozen verifier populations remain:

- QKV: M4 K5120 N10240 Q8 GS64 KP2, 48 calls/cycle;
- Z: M4 K5120 N6144 Q8 GS64 KP1, 48 calls/cycle.

The verifier-QMM router and K-parts machinery were also confirmed in the exact
Homebrew oMLX runtime.

P69B11-B must preserve:

- QKV KP2 reduction/arithmetic order;
- Z KP1 reduction/arithmetic order;
- independent FP16 projection output boundaries.

Do **not** implement a naive homogeneous N16384 concatenated QMM.

P69B11-B is paused until the canonical promoted-stack validator passes. After
that pass, the next experiment is:

**P69B11-B — asymmetric KP2-QKV + KP1-Z bundled projection isolated exactness
and balanced microbenchmark.**

Do not rerun P69B7 profiling and do not reopen P69B8, P69B9, or P69B10-C.

## Canonical commands

Validate:

```bash
bash experiments/p51-q8-verifier/scripts/verify-promoted-stack.sh
```

Repair Homebrew Python-side drift, then revalidate:

```bash
bash experiments/p51-q8-verifier/scripts/restore-promoted-stack.sh
```

The restore script intentionally refuses to repair Git/source or compiled MLX
runtime drift. Those failures indicate the wrong build/checkpoint and require
a controlled rebuild or checkout, not an installed-Python patch.

## Checkpoint discipline

During active tuning, prefer local changes followed by a deliberate commit and
push at an explicit checkpoint. If a coordination/documentation commit is made
directly on the fork, immediately fast-forward the local branch before doing
more experimental work.
