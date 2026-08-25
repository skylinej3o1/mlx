#!/bin/bash
set -euo pipefail

VENV_ACT="/Users/skylinej17/.venvs/mlx-dspark/bin/activate"
REPO="$HOME/src/mlx-m1-qmv"
BRANCH="project51-q8-verifier"

fail() {
    echo "PROMOTED_STACK_FAIL: $*" >&2
    exit 1
}

[[ -f "$VENV_ACT" ]] || fail "missing venv activation: $VENV_ACT"

# shellcheck disable=SC1090
source "$VENV_ACT"
cd "$REPO"

echo "===== P51 PROMOTED STACK VALIDATOR ====="
echo "VIRTUAL_ENV=${VIRTUAL_ENV:-NONE}"
echo "shell_python=$(command -v python)"
python --version

echo
echo "===== GIT DOMAIN ====="

[[ "$(git branch --show-current)" == "$BRANCH" ]] || \
    fail "wrong branch: $(git branch --show-current)"

DIRTY="$(git status --porcelain=v1 --untracked-files=all)"
[[ -z "$DIRTY" ]] || {
    printf '%s\n' "$DIRTY" >&2
    fail "local worktree is dirty"
}

FORK_REMOTE=""
while read -r remote; do
    url="$(git remote get-url "$remote" 2>/dev/null || true)"
    case "$url" in
        *skylinej3o1/mlx.git|*skylinej3o1/mlx)
            FORK_REMOTE="$remote"
            break
            ;;
    esac
done < <(git remote)

[[ -n "$FORK_REMOTE" ]] || fail "skylinej3o1/mlx fork remote not found"

git fetch --quiet "$FORK_REMOTE" "$BRANCH"
LOCAL_SHA="$(git rev-parse HEAD)"
FORK_SHA="$(git rev-parse FETCH_HEAD)"

echo "branch=$BRANCH"
echo "local_sha=$LOCAL_SHA"
echo "fork_remote=$FORK_REMOTE"
echo "fork_sha=$FORK_SHA"

[[ "$LOCAL_SHA" == "$FORK_SHA" ]] || fail "local/fork checkpoint mismatch"

for patch in \
    experiments/p51-q8-verifier/patches/0011-p58-fp16-gdn-verify-prework.patch \
    experiments/p51-q8-verifier/patches/0012-p69b-q8-m4-shared-weight-sg2r4.patch \
    experiments/p51-q8-verifier/patches/0013-p61-headpair-hpt2-sdpa.patch \
    experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch
 do
    [[ -f "$patch" ]] || fail "missing promoted patch: $patch"
 done

echo "GIT_DOMAIN_PASS"

echo
echo "===== REPO MLX SOURCE DOMAIN ====="

grep -Fq "P69B2B_Q8_M4_SHARED_WEIGHT" \
    mlx/backend/metal/kernels/quantized.h || \
    fail "P69B3 source marker missing"

grep -Fq "MLX_P69B2_Q8_M4_SHARED" \
    mlx/backend/metal/quantized.cpp || \
    fail "P69B3 host gate missing"

grep -Fq "sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair" \
    mlx/backend/metal/kernels/sdpa_vector.h || \
    fail "P61 kernel source marker missing"

grep -Fq "MLX_SDPA_GQA6_M4_HPT2_HEADPAIR" \
    mlx/backend/metal/scaled_dot_product_attention.cpp || \
    fail "P61 host gate missing"

echo "REPO_MLX_SOURCE_PASS"

echo
echo "===== IMPORTED / COMPILED MLX DOMAIN ====="

python - <<'PY'
from pathlib import Path
import mlx
import mlx.core as mx

needles = {
    b"MLX_P69B2_Q8_M4_SHARED": "P69B3",
    b"MLX_SDPA_GQA6_M4_HPT2_HEADPAIR": "P61",
}

roots = []
for mod in (mlx, mx):
    p = Path(mod.__file__).resolve()
    root = p if p.is_dir() else p.parent
    if root not in roots:
        roots.append(root)

print("mlx_file=" + str(Path(mlx.__file__).resolve()))
print("mlx_core_file=" + str(Path(mx.__file__).resolve()))
for root in roots:
    print("runtime_search_root=" + str(root))

found = {needle: None for needle in needles}


def contains(path: Path, needle: bytes) -> bool:
    overlap = max(0, len(needle) - 1)
    tail = b""
    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    return False
                data = tail + chunk
                if needle in data:
                    return True
                tail = data[-overlap:] if overlap else b""
    except (OSError, PermissionError):
        return False

seen = set()
for root in roots:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rp = path.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        for needle in needles:
            if found[needle] is None and contains(rp, needle):
                found[needle] = rp

for needle, label in needles.items():
    hit = found[needle]
    print(f"{label}_compiled_marker={hit or 'MISSING'}")
    if hit is None:
        raise SystemExit(
            f"PROMOTED_STACK_FAIL: {label} marker absent from imported MLX runtime"
        )

print("COMPILED_MLX_RUNTIME_PASS")
PY

echo
echo "===== HOMEBREW OMLX DOMAIN ====="

OMLX_CMD="$(command -v omlx || true)"
[[ -n "$OMLX_CMD" ]] || fail "omlx command not found"

OMLX_REAL="$(python - "$OMLX_CMD" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
)"

SHEBANG="$(head -n 1 "$OMLX_REAL")"
OMLX_PY="${SHEBANG#\#!}"

[[ -x "$OMLX_PY" ]] || fail "oMLX owning interpreter missing: $OMLX_PY"

echo "omlx_cmd=$OMLX_CMD"
echo "omlx_real=$OMLX_REAL"
echo "omlx_python=$OMLX_PY"

"$OMLX_PY" - <<'PY'
from pathlib import Path
import importlib.metadata as md
import omlx

expected = {
    "omlx": "0.6.3rc2",
    "mlx": "0.32.0",
    "mlx-vlm": "0.6.3",
}
for package, want in expected.items():
    got = md.version(package)
    print(f"{package}_version={got}")
    if got != want:
        raise SystemExit(
            f"PROMOTED_STACK_FAIL: {package} version {got} != {want}"
        )

root = Path(omlx.__file__).resolve().parent
p58 = root / "patches" / "qwen35_gdn_prework.py"
dual = root / "patches" / "qwen35_dual64_mlp.py"
vlmrt = root / "patches" / "mlx_vlm_mtp" / "qwen35_vlm_runtime.py"

for path in (p58, vlmrt):
    if not path.is_file():
        raise SystemExit(f"PROMOTED_STACK_FAIL: missing runtime file {path}")

p58s = p58.read_text()
p58_required = [
    "OMLX_GDN_VERIFY_PREWORK_FP16",
    "inputs.dtype not in (mx.bfloat16, mx.float16)",
    "conv_state.dtype != inputs.dtype",
    "self.conv1d.weight.dtype != inputs.dtype",
    "dtype=inputs.dtype",
]
p58_forbidden = [
    "inputs.dtype != mx.bfloat16",
    "conv_state.dtype != mx.bfloat16",
    "self.conv1d.weight.dtype != mx.bfloat16",
]
for token in p58_required:
    if token not in p58s:
        raise SystemExit(f"PROMOTED_STACK_FAIL: P58 token missing: {token}")
for token in p58_forbidden:
    if token in p58s:
        raise SystemExit(f"PROMOTED_STACK_FAIL: pre-P58 token still live: {token}")
print("P58_RUNTIME_PASS")

if not dual.is_file():
    raise SystemExit(f"PROMOTED_STACK_FAIL: P69B6 module missing: {dual}")

duals = dual.read_text()
vlmrts = vlmrt.read_text()
for token in (
    "OMLX_VERIFY_MLP_DUAL64",
    "P69B6_E4_DUAL64",
    "omlx_p69b6_dual64_q8_gs64_m4_k5120_n17408",
):
    if token not in duals:
        raise SystemExit(f"PROMOTED_STACK_FAIL: P69B6 token missing: {token}")
for token in ("qwen35_dual64_mlp", "_apply_p69b6_dual64_mlp"):
    if token not in vlmrts:
        raise SystemExit(f"PROMOTED_STACK_FAIL: P69B6 wrapper token missing: {token}")
print("P69B6_RUNTIME_PASS")
print("HOMEBREW_OMLX_RUNTIME_PASS")
PY

echo
echo "===== FINAL ====="
echo "PROMOTED_STACK_PASS"
