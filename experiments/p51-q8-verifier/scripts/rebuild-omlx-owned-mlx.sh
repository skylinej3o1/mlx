#!/bin/bash
set -euo pipefail

VENV_ACT="/Users/skylinej17/.venvs/mlx-dspark/bin/activate"
REPO="$HOME/src/mlx-m1-qmv"
BRANCH="project51-q8-verifier"
VERIFY="$REPO/experiments/p51-q8-verifier/scripts/verify-promoted-stack.sh"
OMLX_CMD="/opt/homebrew/bin/omlx"
TMPDIR="${TMPDIR:-/tmp}"

fail() {
    echo "REBUILD_OMLX_OWNED_MLX_FAIL: $*" >&2
    exit 1
}

[[ -f "$VENV_ACT" ]] || fail "missing venv activation: $VENV_ACT"
# shellcheck disable=SC1090
source "$VENV_ACT"
cd "$REPO"

[[ "$(git branch --show-current)" == "$BRANCH" ]] || fail "wrong branch"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || \
    fail "repo must be clean before oMLX-owned MLX rebuild"

git fetch --quiet fork "$BRANCH"
[[ "$(git rev-parse HEAD)" == "$(git rev-parse FETCH_HEAD)" ]] || \
    fail "local/fork mismatch; sync Git first"

[[ -x "$OMLX_CMD" ]] || fail "missing oMLX command: $OMLX_CMD"
OMLX_REAL="$(python - "$OMLX_CMD" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
)"
SHEBANG="$(head -n 1 "$OMLX_REAL")"
OMLX_PY="${SHEBANG#\#!}"
[[ -x "$OMLX_PY" ]] || fail "missing oMLX owning Python: $OMLX_PY"
OMLX_BIN_DIR="$(dirname "$OMLX_PY")"
BUILD_PATH="$OMLX_BIN_DIR:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"

for marker in \
    "mlx/backend/metal/quantized.cpp:MLX_P69B2_Q8_M4_SHARED" \
    "mlx/backend/metal/kernels/quantized.h:affine_qmv_fast_m4_q8_shared_sg2r4" \
    "mlx/backend/metal/scaled_dot_product_attention.cpp:MLX_SDPA_GQA6_M4_HPT2_HEADPAIR" \
    "mlx/backend/metal/kernels/sdpa_vector.h:sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair"
do
    file="${marker%%:*}"
    token="${marker#*:}"
    grep -Fq "$token" "$file" || fail "promoted source marker missing: $token"
done

command -v cmake >/dev/null 2>&1 || fail "cmake not found"

"$OMLX_PY" - <<'PY'
import sys
import setuptools
print("build_python=" + sys.executable)
print("setuptools=" + setuptools.__version__)
PY

echo "===== OMLX-OWNED MLX NATIVE REBUILD ====="
echo "HEAD=$(git rev-parse HEAD)"
echo "omlx_real=$OMLX_REAL"
echo "omlx_python=$OMLX_PY"
echo "build_path=$BUILD_PATH"
"$OMLX_PY" --version

OMLX_MLX_INFO="$TMPDIR/p51-omlx-mlx-info.$$"
(
    cd /tmp
    env -u PYTHONPATH -u VIRTUAL_ENV "$OMLX_PY" - <<'PY'
from pathlib import Path
import mlx.core as mx
root = Path(mx.__file__).resolve().parent
print(root)
print(Path(mx.__file__).resolve())
PY
) > "$OMLX_MLX_INFO"

OMLX_MLX_ROOT="$(sed -n '1p' "$OMLX_MLX_INFO")"
OMLX_CORE="$(sed -n '2p' "$OMLX_MLX_INFO")"
rm -f "$OMLX_MLX_INFO"

[[ -d "$OMLX_MLX_ROOT" ]] || fail "oMLX-owned MLX root missing: $OMLX_MLX_ROOT"
[[ -f "$OMLX_CORE" ]] || fail "oMLX-owned core missing: $OMLX_CORE"

OMLX_LIB="$OMLX_MLX_ROOT/lib"
for path in \
    "$OMLX_LIB/libmlx.dylib" \
    "$OMLX_LIB/libjaccl.dylib" \
    "$OMLX_LIB/mlx.metallib"
do
    [[ -f "$path" ]] || fail "oMLX-owned native file missing: $path"
done

echo "omlx_mlx_root=$OMLX_MLX_ROOT"
echo "omlx_core=$OMLX_CORE"

TMP="$(mktemp -d /tmp/p51-omlx-mlx-rebuild.XXXXXX)"
REPO_BACKUP="$TMP/repo-native"
OMLX_BACKUP="$TMP/omlx-native"
REPO_MANIFEST="$TMP/repo-manifest.txt"
mkdir -p "$REPO_BACKUP" "$OMLX_BACKUP"

find python/mlx -type f \
    \( -name '*.so' -o -name '*.dylib' -o -name '*.metallib' \) \
    -print > "$REPO_MANIFEST"

while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    mkdir -p "$REPO_BACKUP/$(dirname "$path")"
    cp -p "$path" "$REPO_BACKUP/$path"
done < "$REPO_MANIFEST"

cp -p "$OMLX_CORE" "$OMLX_BACKUP/core.so"
cp -p "$OMLX_LIB/libmlx.dylib" "$OMLX_BACKUP/libmlx.dylib"
cp -p "$OMLX_LIB/libjaccl.dylib" "$OMLX_BACKUP/libjaccl.dylib"
cp -p "$OMLX_LIB/mlx.metallib" "$OMLX_BACKUP/mlx.metallib"

ROLLBACK=1
cleanup() {
    rc=$?
    if [[ "$ROLLBACK" -eq 1 ]]; then
        echo "===== ROLLBACK OMLX-OWNED MLX =====" >&2

        while IFS= read -r path; do
            [[ -n "$path" ]] || continue
            if [[ -f "$REPO_BACKUP/$path" ]]; then
                mkdir -p "$(dirname "$path")"
                cp -p "$REPO_BACKUP/$path" "$path"
            else
                rm -f "$path"
            fi
        done < "$REPO_MANIFEST"

        find python/mlx -maxdepth 1 -type f -name 'core.cpython-311-*.so' -delete
        while IFS= read -r path; do
            [[ -n "$path" ]] || continue
            if [[ -f "$REPO_BACKUP/$path" ]]; then
                cp -p "$REPO_BACKUP/$path" "$path"
            fi
        done < "$REPO_MANIFEST"

        cp -p "$OMLX_BACKUP/core.so" "$OMLX_CORE"
        cp -p "$OMLX_BACKUP/libmlx.dylib" "$OMLX_LIB/libmlx.dylib"
        cp -p "$OMLX_BACKUP/libjaccl.dylib" "$OMLX_LIB/libjaccl.dylib"
        cp -p "$OMLX_BACKUP/mlx.metallib" "$OMLX_LIB/mlx.metallib"
    fi
    rm -rf "$TMP"
    exit "$rc"
}
trap cleanup EXIT

echo
echo "===== BUILD CURRENT MLX SOURCE FOR PYTHON 3.11 ====="
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-10}"
echo "CMAKE_BUILD_PARALLEL_LEVEL=$CMAKE_BUILD_PARALLEL_LEVEL"

env \
    -u PYTHONPATH \
    -u VIRTUAL_ENV \
    PATH="$BUILD_PATH" \
    "$OMLX_PY" setup.py build_ext --inplace

shopt -s nullglob
CORE11=(python/mlx/core.cpython-311-*.so)
shopt -u nullglob
[[ "${#CORE11[@]}" -eq 1 ]] || \
    fail "expected exactly one repo-local CPython 3.11 core, found ${#CORE11[@]}"
REPO_CORE11="${CORE11[0]}"

for path in \
    "$REPO_CORE11" \
    python/mlx/lib/libmlx.dylib \
    python/mlx/lib/libjaccl.dylib \
    python/mlx/lib/mlx.metallib
do
    [[ -f "$path" ]] || fail "rebuilt repo-native file missing: $path"
done

echo
echo "===== VERIFY STAGED PYTHON 3.11 BUILD ====="
(
    cd /tmp
    env -u VIRTUAL_ENV PYTHONPATH="$REPO/python" "$OMLX_PY" - <<'PY'
from pathlib import Path
import mlx.core as mx

root = Path(mx.__file__).resolve().parent
lib = root / "lib" / "libmlx.dylib"
metallib = root / "lib" / "mlx.metallib"

print("staged_core=" + str(Path(mx.__file__).resolve()))
print("staged_libmlx=" + str(lib))
print("staged_metallib=" + str(metallib))

checks = [
    (lib, b"MLX_P69B2_Q8_M4_SHARED", "P69B3 host gate"),
    (lib, b"MLX_SDPA_GQA6_M4_HPT2_HEADPAIR", "P61 host gate"),
    (metallib, b"affine_qmv_fast_m4_q8_shared_sg2r4", "P69B3 metallib kernel"),
    (metallib, b"sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair", "P61 metallib kernel"),
]

for path, needle, label in checks:
    data = path.read_bytes()
    hit = needle in data
    print(f"{label}={'PASS' if hit else 'MISSING'}")
    if not hit:
        raise SystemExit("REBUILD_OMLX_OWNED_MLX_FAIL: staged " + label + " missing")

a = mx.array([1.0, 2.0], dtype=mx.float32)
b = a + 1.0
mx.eval(b)
print("STAGED_OMLX_MLX_RUNTIME_PASS")
PY
)

echo
echo "===== INSTALL PYTHON 3.11 BUILD INTO OMLX RUNTIME ====="
cp -p "$REPO_CORE11" "$OMLX_CORE"
cp -p python/mlx/lib/libmlx.dylib "$OMLX_LIB/libmlx.dylib"
cp -p python/mlx/lib/libjaccl.dylib "$OMLX_LIB/libjaccl.dylib"
cp -p python/mlx/lib/mlx.metallib "$OMLX_LIB/mlx.metallib"

echo "core_sha256=$(shasum -a 256 "$OMLX_CORE" | awk '{print $1}')"
echo "libmlx_sha256=$(shasum -a 256 "$OMLX_LIB/libmlx.dylib" | awk '{print $1}')"
echo "metallib_sha256=$(shasum -a 256 "$OMLX_LIB/mlx.metallib" | awk '{print $1}')"

echo
echo "===== VERIFY ACTUAL OMLX-OWNED MLX RUNTIME ====="
(
    cd /tmp
    env -u PYTHONPATH -u VIRTUAL_ENV "$OMLX_PY" - <<'PY'
from pathlib import Path
import mlx.core as mx

root = Path(mx.__file__).resolve().parent
lib = root / "lib" / "libmlx.dylib"
metallib = root / "lib" / "mlx.metallib"

print("live_core=" + str(Path(mx.__file__).resolve()))
print("live_libmlx=" + str(lib))
print("live_metallib=" + str(metallib))

checks = [
    (lib, b"MLX_P69B2_Q8_M4_SHARED", "P69B3 host gate"),
    (lib, b"MLX_SDPA_GQA6_M4_HPT2_HEADPAIR", "P61 host gate"),
    (metallib, b"affine_qmv_fast_m4_q8_shared_sg2r4", "P69B3 metallib kernel"),
    (metallib, b"sdpa_vector_2pass_1_gqa6_m4_hpt2_headpair", "P61 metallib kernel"),
]

for path, needle, label in checks:
    data = path.read_bytes()
    hit = needle in data
    print(f"{label}={'PASS' if hit else 'MISSING'}")
    if not hit:
        raise SystemExit("REBUILD_OMLX_OWNED_MLX_FAIL: live " + label + " missing")

a = mx.array([1.0, 2.0], dtype=mx.float32)
b = a + 1.0
mx.eval(b)
print("OMLX_OWNED_COMPILED_MLX_RUNTIME_PASS")
PY
)

ROLLBACK=0

echo
echo "===== REPO CLEANLINESS ====="
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || {
    git status --short
    fail "build generated unexpected tracked/unignored repo state"
}
echo "REPO_CLEAN_PASS"

echo
echo "===== FULL PROMOTED STACK VALIDATION ====="
bash "$VERIFY"

echo
echo "===== FINAL ====="
echo "REBUILD_OMLX_OWNED_MLX_PASS"
