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
    experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch \
    experiments/p51-q8-verifier/patches/0015-p69b11-qkvz-dual.patch
do
    [[ -f "$patch" ]] || fail "missing promoted patch: $patch"
done

echo "GIT_DOMAIN_PASS"

echo
echo "===== REPO MLX SOURCE DOMAIN ====="
grep -Fq "P69B2B_Q8_M4_SHARED_WEIGHT" \
    mlx/backend/metal/kernels/quantized.h || fail "P69B3 source marker missing"
grep -Fq "affine_qmv_fast_m4_q8_shared_sg2r4" \
    mlx/backend/metal/kernels/quantized.h || fail "P69B3 kernel marker missing"
grep -Fq "MLX_P69B2_Q8_M4_SHARED" \
    mlx/backend/metal/quantized.cpp || fail "P69B3 host gate missing"
grep -Fq "sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair" \
    mlx/backend/metal/kernels/sdpa_vector.h || fail "P61 kernel source marker missing"
grep -Fq "MLX_SDPA_GQA6_M4_HPT2_HEADPAIR" \
    mlx/backend/metal/scaled_dot_product_attention.cpp || fail "P61 host gate missing"
echo "REPO_MLX_SOURCE_PASS"

echo
echo "===== VENV IMPORTED / COMPILED MLX DOMAIN ====="
python - <<'PY'
from pathlib import Path
import importlib.metadata as md
import mlx
import mlx.core as mx

root = Path(mx.__file__).resolve().parent
lib = root / "lib" / "libmlx.dylib"
metallib = root / "lib" / "mlx.metallib"

print("mlx_version=" + md.version("mlx"))
print("mlx_file=" + str(getattr(mlx, "__file__", None)))
print("mlx_core_file=" + str(Path(mx.__file__).resolve()))
print("mlx_path=" + repr(list(getattr(mlx, "__path__", []))))
print("venv_libmlx=" + str(lib))
print("venv_metallib=" + str(metallib))

checks = [
    (lib, b"MLX_P69B2_Q8_M4_SHARED", "P69B3_host"),
    (lib, b"MLX_SDPA_GQA6_M4_HPT2_HEADPAIR", "P61_host"),
    (metallib, b"affine_qmv_fast_m4_q8_shared_sg2r4", "P69B3_metallib"),
    (metallib, b"sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair", "P61_metallib"),
]
for path, needle, label in checks:
    if not path.is_file():
        raise SystemExit(f"PROMOTED_STACK_FAIL: venv native file missing: {path}")
    hit = needle in path.read_bytes()
    print(f"{label}={'PASS' if hit else 'MISSING'}")
    if not hit:
        raise SystemExit(f"PROMOTED_STACK_FAIL: {label} absent from venv compiled MLX runtime")

print("VENV_COMPILED_MLX_RUNTIME_PASS")
PY

echo
echo "===== OMLX EXECUTABLE OWNERSHIP ====="
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

echo
echo "===== OMLX-OWNED COMPILED MLX DOMAIN ====="
(
    cd /tmp
    env -u PYTHONPATH "$OMLX_PY" - <<'PY'
from pathlib import Path
import hashlib
import importlib.metadata as md
import mlx
import mlx.core as mx

root = Path(mx.__file__).resolve().parent
core = Path(mx.__file__).resolve()
lib = root / "lib" / "libmlx.dylib"
metallib = root / "lib" / "mlx.metallib"

print("omlx_owned_mlx_metadata_version=" + md.version("mlx"))
print("omlx_owned_mlx_file=" + str(getattr(mlx, "__file__", None)))
print("omlx_owned_core=" + str(core))
print("omlx_owned_mlx_path=" + repr(list(getattr(mlx, "__path__", []))))
print("omlx_owned_libmlx=" + str(lib))
print("omlx_owned_metallib=" + str(metallib))

for path in (core, lib, metallib):
    if not path.is_file():
        raise SystemExit(f"PROMOTED_STACK_FAIL: oMLX-owned native file missing: {path}")
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    print(path.name + "_sha256=" + h)

checks = [
    (lib, b"MLX_P69B2_Q8_M4_SHARED", "P69B3_host"),
    (lib, b"MLX_SDPA_GQA6_M4_HPT2_HEADPAIR", "P61_host"),
    (metallib, b"affine_qmv_fast_m4_q8_shared_sg2r4", "P69B3_metallib"),
    (metallib, b"sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair", "P61_metallib"),
]
for path, needle, label in checks:
    hit = needle in path.read_bytes()
    print(f"omlx_owned_{label}={'PASS' if hit else 'MISSING'}")
    if not hit:
        raise SystemExit(
            f"PROMOTED_STACK_FAIL: {label} absent from actual oMLX-owned compiled MLX runtime"
        )

# Native load smoke test.
a = mx.array([1.0, 2.0], dtype=mx.float32)
b = a + 1.0
mx.eval(b)
print("OMLX_OWNED_COMPILED_MLX_RUNTIME_PASS")
PY
)

echo
echo "===== HOMEBREW OMLX PYTHON PATCH DOMAIN ====="
(
    cd /tmp
    env -u PYTHONPATH "$OMLX_PY" - <<'PY'
from pathlib import Path
import ast
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
        raise SystemExit(f"PROMOTED_STACK_FAIL: {package} version {got} != {want}")

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
    "omlx_p69b6_dual64_",
    "q8_gs64_m4_k5120_n17408",
):
    if token not in duals:
        raise SystemExit(f"PROMOTED_STACK_FAIL: P69B6 token missing: {token}")
for token in ("qwen35_dual64_mlp", "_apply_p69b6_dual64_mlp"):
    if token not in vlmrts:
        raise SystemExit(f"PROMOTED_STACK_FAIL: P69B6 wrapper token missing: {token}")
print("P69B6_RUNTIME_PASS")

qkvz = root / "patches" / "qwen35_qkvz_dual.py"
if not qkvz.is_file():
    raise SystemExit(
        f"PROMOTED_STACK_FAIL: P69B11 module missing: {qkvz}"
    )

qkvzs = qkvz.read_text()

qkvz_tree = ast.parse(qkvzs)
qkvz_assigned = set()

for node in qkvz_tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                qkvz_assigned.add(target.id)
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            qkvz_assigned.add(node.target.id)

for name in (
    "_ENABLED",
    "_KERNEL",
    "_EXACT_DONE",
    "_ENGAGE_COUNT",
):
    if name not in qkvz_assigned:
        raise SystemExit(
            f"PROMOTED_STACK_FAIL: "
            f"P69B11 state assignment missing: {name}"
        )

for token in (
    "OMLX_VERIFY_GDN_QKVZ_DUAL",
    "P69B11_B3_QKVZ_DUAL",
    "P69B11_B3_EXACT_PASS",
    "P69B11_B3_ENGAGED",
):
    if token not in qkvzs:
        raise SystemExit(
            f"PROMOTED_STACK_FAIL: P69B11 token missing: {token}"
        )

for token in (
    "qwen35_qkvz_dual",
    "_apply_p69b11_qkvz_dual",
):
    if token not in vlmrts:
        raise SystemExit(
            f"PROMOTED_STACK_FAIL: P69B11 wrapper token missing: {token}"
        )

import hashlib
from omlx.patches import qwen35_qkvz_dual as qkvz_mod

source_sha = hashlib.sha256(
    qkvz_mod._SOURCE.encode()
).hexdigest()

print("p69b11_embedded_metal_sha256=" + source_sha)

if source_sha != (
    "e11dd85965c264cdd9b415348d0c2bd9"
    "d19ae2cfd20ce1a7ad1654d740bc8508"
):
    raise SystemExit(
        "PROMOTED_STACK_FAIL: P69B11 embedded Metal source SHA mismatch"
    )

from omlx.patches.mlx_vlm_mtp import (
    qwen35_vlm_runtime as q35_dense_runtime,
)

if not q35_dense_runtime.apply():
    raise SystemExit(
        "PROMOTED_STACK_FAIL: "
        "dense Qwen3.5 runtime hook did not apply"
    )

from mlx_vlm.models.qwen3_5 import (
    language as q35_lang,
)

if not getattr(
    q35_lang,
    "_p69b11_b3_qkvz_dual",
    False,
):
    raise SystemExit(
        "PROMOTED_STACK_FAIL: "
        "P69B11 dense hook not installed"
    )

print("P69B11_DENSE_HOOK_PASS")
print("P69B11_RUNTIME_PASS")
print("HOMEBREW_OMLX_RUNTIME_PASS")
PY
)

echo
echo "===== FINAL ====="
echo "PROMOTED_STACK_PASS"
