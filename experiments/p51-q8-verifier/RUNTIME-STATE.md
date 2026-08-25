# P51 verifier promoted runtime state

This document is the durable bridge between Git history and the live runtime
used by the `project51-q8-verifier` experiments.

`STATUS.md` records experimental decisions. This file records the additional
runtime invariants that must be true before those decisions are assumed to be
live.

## Why this exists

This project has four independently drifting state domains:

1. Git checkout / fork and recorded source patches;
2. the Python-3.14 `mlx-dspark` compiled MLX runtime;
3. the Python-3.11 MLX runtime actually owned by `/opt/homebrew/bin/omlx`;
4. Homebrew oMLX Python-side runtime patches.

A clean Git checkout does not prove any compiled or installed runtime still
matches the promoted source. Package refreshes, source restoration, or source
changes without a native rebuild can make live runtime state diverge from Git
without dirtying the worktree.

Therefore every new terminal and every new chat must run the canonical
promoted-stack validator before benchmarking.

## Canonical runtime ownership

### Shell / project environment

```text
venv: /Users/skylinej17/.venvs/mlx-dspark
repo: ~/src/mlx-m1-qmv
branch: project51-q8-verifier
venv Python: 3.14.x
```

The venv imports repo-local MLX native outputs under:

```text
~/src/mlx-m1-qmv/python/mlx/
```

### Homebrew oMLX

```text
command: /opt/homebrew/bin/omlx
version: 0.6.3rc2
owning Python: /opt/homebrew/Cellar/omlx/0.6.3rc2/libexec/bin/python3.11
mlx-vlm metadata in oMLX runtime: 0.6.3
mlx metadata in oMLX runtime: 0.32.0
```

The actual oMLX process owns a separate CPython-3.11 MLX extension and native
library set under its `libexec` site-packages. It does **not** automatically use
the Python-3.14 repo-local `core.so` merely because the shell venv was
activated.

Never copy a CPython-3.14 extension into the Python-3.11 runtime. Both ABIs must
be built separately from the same promoted source.

## Current promoted verifier stack

The post-P69B10 champion stack keeps:

- **P58** FP16 GDN fused verifier prework;
- **P61** HEADPAIR HPT2 SDPA;
- **P69B3** SG2R4 Q8 M4 shared-weight projection;
- **P69B6** packaged DUAL64 verifier MLP fusion.
- **P69B11** asymmetric GDN QKV+Z projection bundle;

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

Required live signatures include:

```text
OMLX_GDN_VERIFY_PREWORK_FP16
inputs.dtype not in (mx.bfloat16, mx.float16)
conv_state.dtype != inputs.dtype
self.conv1d.weight.dtype != inputs.dtype
dtype=inputs.dtype
```

### P61 — MLX source plus both compiled MLX ABIs

Recorded patch:

```text
experiments/p51-q8-verifier/patches/0013-p61-headpair-hpt2-sdpa.patch
```

Required host / Metal signatures:

```text
MLX_SDPA_GQA6_M4_HPT2_HEADPAIR
sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair
```

These must exist in both:

- the Python-3.14 venv `libmlx.dylib` / `mlx.metallib`;
- the Python-3.11 oMLX-owned `libmlx.dylib` / `mlx.metallib`.

### P69B3 — MLX source plus both compiled MLX ABIs

Recorded patch:

```text
experiments/p51-q8-verifier/patches/0012-p69b-q8-m4-shared-weight-sg2r4.patch
```

Required host / Metal signatures:

```text
MLX_P69B2_Q8_M4_SHARED
affine_qmv_fast_m4_q8_shared_sg2r4
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
"omlx_p69b6_dual64_"
"q8_gs64_m4_k5120_n17408"
_apply_p69b6_dual64_mlp
```

The Metal kernel name is represented as two adjacent Python string literals;
do not validate the source by requiring the concatenated runtime name as one
contiguous source token.

## 2026-08-25 runtime-drift incidents

### Incident 1 — P58 Homebrew source drift

While beginning P69B11-A, Git was clean and synchronized, but live
`qwen35_gdn_prework.py` was pre-P58.

Observed pre-P58 SHA256:

```text
af5e949e9d0dad8b14d87717db773d5366926dee9efef1efe822297c46bf5ed5
```

Recorded P58 patch SHA256:

```text
f3e3a99a8caf363821570db10b7d73d00aed0cdca4af8628a299fa5c3eb95c02
```

P58 was restored successfully. Current restored live SHA256:

```text
2706ed6443c748026acd813c266c8c18eef9157adb5950036b5cba0c0cbda6b5
```

### Incident 2 — Python-3.14 compiled MLX drift

Repository MLX source contained P61/P69B3 while the venv-imported native
`libmlx.dylib` had been built before those changes. The repo source was clean,
but the compiled runtime lacked both promoted host markers.

The current source was rebuilt in place under Python 3.14. The rebuilt venv
runtime then exposed both promoted markers and passed the original compiled
runtime gate.

### Incident 3 — actual oMLX executable owned a second stale MLX build

P69B11-B1 provenance capture revealed that `/opt/homebrew/bin/omlx` does not
use the Python-3.14 extension. Its shebang launches:

```text
/opt/homebrew/Cellar/omlx/0.6.3rc2/libexec/bin/python3.11
```

That interpreter imported:

```text
.../site-packages/mlx/core.cpython-311-darwin.so
```

B1 observed:

```text
homebrew_P69B3_compiled_hits=[]
homebrew_P61_compiled_hits=[]
```

Therefore the earlier validator's `PROMOTED_STACK_PASS` was insufficient: it
proved the venv compiled MLX runtime, P58, and P69B6, but not the compiled MLX
runtime actually used by the oMLX executable.

This is now treated as a distinct ABI/state domain.

## P69B11-B1 exact source capture

B1 successfully captured the exact Homebrew verifier-QMM implementation:

```text
omlx/patches/qwen35_verify_qmm.py
SHA256: 9375a8f380f14803075605c971533fa34a5ad08ff5b6c2e8bf2c029db4fbc2f8
```

Verified verifier shapes / routing contract:

```text
QKV: M4 K5120 N10240 Q8 GS64 KP2
Z:   M4 K5120 N6144  Q8 GS64 KP1
```

The stock split-K kernel performs:

- independent per-projection Q8 traversal;
- FP32 accumulation;
- `simd_sum` within each K part;
- threadgroup partial storage;
- ordered reduction `p=0..K_PARTS-1`;
- FP16 output store.

P69B11-B must preserve independently:

- QKV KP2 traversal/reduction order;
- Z KP1 traversal/reduction order;
- separate FP16 projection output boundaries.

Do **not** implement a homogeneous N16384 concatenated QMM.

B1 artifact:

```text
~/src/mlx-m1-qmv-artifacts/p69/p69b11b1-exact-qmm-source.txt
SHA256: 0fb8ea5251d4433475d23fc127708c759bf8b6fe0e1eeed91f7f39edc56d1a82
```

## Current experiment handoff

**P69B11-B2 is paused until the actual oMLX-owned Python-3.11 MLX runtime
contains P61 and P69B3 and the strengthened validator returns
`PROMOTED_STACK_PASS`.**

After that pass, continue directly to:

**P69B11-B2 — single-dispatch asymmetric KP2-QKV + KP1-Z isolated exactness
and balanced microbenchmark.**

Do not rerun P69B7 profiling and do not reopen P69B8, P69B9, or P69B10-C.

## Canonical commands

Validate all state domains:

```bash
bash experiments/p51-q8-verifier/scripts/verify-promoted-stack.sh
```

Repair Python-3.14 repo-local compiled MLX drift:

```bash
bash experiments/p51-q8-verifier/scripts/rebuild-promoted-mlx.sh
```

Repair the actual oMLX-owned Python-3.11 compiled MLX runtime:

```bash
bash experiments/p51-q8-verifier/scripts/rebuild-omlx-owned-mlx.sh
```

Repair Homebrew Python-side P58/P69B6 drift:

```bash
bash experiments/p51-q8-verifier/scripts/restore-promoted-stack.sh
```

## Checkpoint discipline

During active tuning, prefer local changes followed by a deliberate commit and
push at an explicit checkpoint. If a coordination/documentation commit is made
directly on the fork, immediately fast-forward the local branch before doing
more experimental work.

## P69B11 certified runtime

P69B11 is a Homebrew oMLX Python-side promoted component.

Patch artifact:

```text
experiments/p51-q8-verifier/patches/0015-p69b11-qkvz-dual.patch
```

Live module:

```text
.../site-packages/omlx/patches/qwen35_qkvz_dual.py
```

Wrapper hook:

```text
qwen35_qkvz_dual
_apply_p69b11_qkvz_dual
```

Runtime gate:

```text
OMLX_VERIFY_GDN_QKVZ_DUAL=1
```

The packaged module embeds the exact certified B2 Metal source. Required
embedded Metal SHA256:

```text
e11dd85965c264cdd9b415348d0c2bd9d19ae2cfd20ce1a7ad1654d740bc8508
```

B4 certification:

```text
mean saving = +2.408602151 ms/cycle
TG gain     = +1.5071%
pair wins   = 4/4
```

All certification output hashes and verifier trajectories remained frozen.

The canonical restorer repairs P69B11 together with P58/P69B6 when necessary,
and the canonical validator requires the P69B11 module, wrapper hook, and exact
embedded Metal source fingerprint.

## P69B11 absolute champion validation

Permanent live runtime validated at:

- TG: 19.5550883835 tok/s
- BPC: 137.827956989 ms/cycle
- frozen hash: 101ae2aec9793dfe
- cycles: 186
- acceptance: 325/442
- depths: 155/101/69

Live engagement confirmed for P58, P69B6, and P69B11.

The canonical promoted-stack validator passed both before and after the
measurement.

Current promoted verifier stack:

1. P58 FP16 GDN verifier prework
2. P61 HPT2 HEADPAIR attention
3. P69B3 SG2R4 Q8 M4 shared projection
4. P69B6 DUAL64 verifier MLP
5. P69B11 asymmetric QKV(KP2)+Z(KP1) verifier projection bundle
6. fixed D3/M4 speculative decoding

Next optimization series: P69B12.
