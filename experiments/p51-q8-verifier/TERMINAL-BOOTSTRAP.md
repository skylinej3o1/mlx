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

Example:

```bash
OMLX_PY=/opt/homebrew/Cellar/omlx/0.6.3rc2/libexec/bin/python3.11
"$OMLX_PY" -c 'import omlx; print(omlx.__file__)'
```

## Rule for future experiment blocks

- Reactivate `mlx-dspark` at the top of every fresh-terminal block.
- Use the venv for the project tooling it owns.
- Use the explicit Homebrew oMLX Python 3.11 for installed oMLX / `mlx_vlm`
  source inspection and runtime imports.
- Do not search unrelated Python installations first when the oMLX executable
  already reveals its owning interpreter.
