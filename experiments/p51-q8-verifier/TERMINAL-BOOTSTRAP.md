# P51 verifier terminal bootstrap

This file records the mandatory shell/runtime bootstrap for the
`project51-q8-verifier` tuning work.

## Every new-terminal paste-ready block

Start every shell block that may be pasted into a fresh terminal with:

```bash
source /Users/skylinej17/.venvs/mlx-dspark/bin/activate
cd ~/src/mlx-m1-qmv
setopt interactivecomments
```

Do not assume the venv survived a broken command or a newly opened terminal.
A fresh terminal commonly starts outside `mlx-dspark`.

## Two compiled MLX ABI targets

This project has **two distinct compiled MLX runtimes** that must both contain
promoted MLX changes.

### Development / tuning venv

```text
venv: /Users/skylinej17/.venvs/mlx-dspark
Python: 3.14.x
repo-local core: ~/src/mlx-m1-qmv/python/mlx/core.cpython-314-darwin.so
```

P61 and P69B3 must be present in the repo-local `libmlx.dylib` and
`mlx.metallib` used by this interpreter.

### Actual Homebrew oMLX executable

The Homebrew oMLX command is:

```text
/opt/homebrew/bin/omlx
```

For oMLX `0.6.3rc2`, it resolves to:

```text
/opt/homebrew/Cellar/omlx/0.6.3rc2/libexec/bin/omlx
```

Its owning interpreter is:

```text
/opt/homebrew/Cellar/omlx/0.6.3rc2/libexec/bin/python3.11
```

That interpreter owns a separate CPython-3.11 MLX extension under the oMLX
`libexec` site-packages. The actual `/opt/homebrew/bin/omlx` process uses this
runtime unless explicitly redirected. Therefore a correct Python-3.14 build
does **not** prove P61/P69B3 are active in oMLX.

Never copy a `core.cpython-314-*.so` into the Python-3.11 runtime. The two
Python extension ABIs must be built separately from the same promoted source.

## Canonical health check

Before continuing tuning after a new terminal, new chat, package refresh,
compiled rebuild, or broken experimental command, run:

```bash
source /Users/skylinej17/.venvs/mlx-dspark/bin/activate
cd ~/src/mlx-m1-qmv
setopt interactivecomments
bash experiments/p51-q8-verifier/scripts/verify-promoted-stack.sh
```

Do not start a new performance experiment unless the final line is:

```text
PROMOTED_STACK_PASS
```

The validator checks all of these independently:

1. local/fork Git state;
2. promoted MLX source markers;
3. Python-3.14 venv compiled MLX host + metallib markers;
4. Python-3.11 oMLX-owned compiled MLX host + metallib markers;
5. Homebrew oMLX Python-side P58/P69B6 runtime patches.

## Canonical repair commands

If the Python-3.14 repo-local compiled MLX runtime is stale:

```bash
bash experiments/p51-q8-verifier/scripts/rebuild-promoted-mlx.sh
```

If the actual oMLX-owned Python-3.11 compiled MLX runtime is stale:

```bash
bash experiments/p51-q8-verifier/scripts/rebuild-omlx-owned-mlx.sh
```

The Python-3.11 helper rebuilds the current Git source for the exact oMLX
interpreter, stages and verifies it, then installs `core.so`, `libmlx.dylib`,
`libjaccl.dylib`, and `mlx.metallib` into the oMLX-owned MLX package with
backup + rollback protection.

If the Homebrew oMLX Python-side P58/P69B6 patches drift:

```bash
bash experiments/p51-q8-verifier/scripts/restore-promoted-stack.sh
```

Do not use a Python-side patch restorer to conceal compiled MLX drift.

## New-chat handoff rule

A new chat should read, in this order:

1. `experiments/p51-q8-verifier/CURRENT.md`
2. `experiments/p51-q8-verifier/STATUS.md`
3. `experiments/p51-q8-verifier/TERMINAL-BOOTSTRAP.md`
4. `experiments/p51-q8-verifier/RUNTIME-STATE.md`

`CURRENT.md` is the compact latest handoff and names the exact next experiment.
`STATUS.md` remains the longer experimental history.

Then require a fresh `verify-promoted-stack.sh` result before issuing the next
benchmark or source-modifying experiment block.

Do not infer live runtime state from `STATUS.md` alone. Git state, the
Python-3.14 compiled MLX runtime, the Python-3.11 oMLX-owned compiled MLX
runtime, and installed oMLX Python patches are separate state domains.

## Rule for future experiment blocks

- Reactivate `mlx-dspark` at the top of every fresh-terminal block.
- Use the explicit Homebrew oMLX Python 3.11 for installed oMLX / `mlx_vlm`
  source inspection and oMLX-process provenance checks.
- Validate both compiled MLX ABIs before benchmarking.
- Do not benchmark unless the promoted-stack validator passes.
- Prefer local repo edits plus a deliberate checkpoint push over ad-hoc direct
  GitHub writes during an active tuning session.
