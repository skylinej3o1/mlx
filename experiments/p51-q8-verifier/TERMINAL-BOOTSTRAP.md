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

## oMLX installed runtime

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

The `mlx-dspark` venv currently uses Python 3.14.6 and does **not** own the
`omlx` package. Therefore source/runtime inspection of installed oMLX must
invoke the Homebrew-owned Python 3.11 explicitly rather than assuming
`python` from the activated venv can import `omlx`.

## Canonical health check

Before continuing tuning after a new terminal, new chat, package refresh, or
broken experimental command, run:

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

If the verifier reports drift in the Homebrew oMLX Python runtime, use the
checked-in idempotent repair script:

```bash
bash experiments/p51-q8-verifier/scripts/restore-promoted-stack.sh
```

The repair script only repairs the Homebrew Python-side promoted pieces. It
refuses to paper over a wrong/dirty/diverged Git checkout or a stale compiled
MLX runtime.

## New-chat handoff rule

A new chat should read, in this order:

1. `experiments/p51-q8-verifier/STATUS.md`
2. `experiments/p51-q8-verifier/TERMINAL-BOOTSTRAP.md`
3. `experiments/p51-q8-verifier/RUNTIME-STATE.md`

Then require a fresh `verify-promoted-stack.sh` result before issuing the next
benchmark or source-modifying experiment block.

Do not infer live runtime state from `STATUS.md` alone. Git state and installed
Homebrew/oMLX state are separate state domains.

## Rule for future experiment blocks

- Reactivate `mlx-dspark` at the top of every fresh-terminal block.
- Use the venv for the project tooling and MLX runtime it owns.
- Use the explicit Homebrew oMLX Python 3.11 for installed oMLX / `mlx_vlm`
  source inspection and runtime imports.
- Do not search unrelated Python installations first when the oMLX executable
  already reveals its owning interpreter.
- Do not benchmark unless the promoted-stack validator passes.
- Prefer local repo edits plus a deliberate checkpoint push over ad-hoc direct
  GitHub writes during an active tuning session.
