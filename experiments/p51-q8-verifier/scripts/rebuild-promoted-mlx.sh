#!/bin/bash
set -euo pipefail

VENV_ACT="/Users/skylinej17/.venvs/mlx-dspark/bin/activate"
REPO="$HOME/src/mlx-m1-qmv"
BRANCH="project51-q8-verifier"
VERIFY="$REPO/experiments/p51-q8-verifier/scripts/verify-promoted-stack.sh"

fail() {
    echo "REBUILD_PROMOTED_MLX_FAIL: $*" >&2
    exit 1
}

[[ -f "$VENV_ACT" ]] || fail "missing venv activation: $VENV_ACT"
# shellcheck disable=SC1090
source "$VENV_ACT"
cd "$REPO"

[[ "$(git branch --show-current)" == "$BRANCH" ]] || fail "wrong branch"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || \
    fail "repo must be clean before native MLX rebuild"

git fetch --quiet fork "$BRANCH"
[[ "$(git rev-parse HEAD)" == "$(git rev-parse FETCH_HEAD)" ]] || \
    fail "local/fork mismatch; sync Git before native MLX rebuild"

for marker in \
    "mlx/backend/metal/quantized.cpp:MLX_P69B2_Q8_M4_SHARED" \
    "mlx/backend/metal/scaled_dot_product_attention.cpp:MLX_SDPA_GQA6_M4_HPT2_HEADPAIR"
do
    file="${marker%%:*}"
    token="${marker#*:}"
    grep -Fq "$token" "$file" || fail "promoted source marker missing: $token"
done

echo "===== PROMOTED MLX NATIVE REBUILD ====="
echo "VIRTUAL_ENV=${VIRTUAL_ENV:-NONE}"
echo "python=$(command -v python)"
python --version
echo "HEAD=$(git rev-parse HEAD)"

echo
echo "===== PRE-BUILD IMPORTED RUNTIME ====="
python - <<'PY'
from pathlib import Path
import importlib.metadata as md
import mlx
import mlx.core as mx
print("mlx_version=" + md.version("mlx"))
print("mlx_file=" + str(getattr(mlx, "__file__", None)))
print("mlx_core_file=" + str(Path(mx.__file__).resolve()))
PY

TMP="$(mktemp -d /tmp/p51-mlx-rebuild.XXXXXX)"
BACKUP="$TMP/native-backup"
MANIFEST="$TMP/native-manifest.txt"
mkdir -p "$BACKUP"

# Snapshot the repo-local native runtime files before rebuilding. These are
# generated/ignored build outputs, not Git-tracked source files.
find python/mlx -type f \
    \( -name '*.so' -o -name '*.dylib' -o -name '*.metallib' \) \
    -print > "$MANIFEST"

while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    mkdir -p "$BACKUP/$(dirname "$path")"
    cp -p "$path" "$BACKUP/$path"
done < "$MANIFEST"

ROLLBACK=1
cleanup() {
    rc=$?
    if [[ "$ROLLBACK" -eq 1 ]]; then
        echo "===== ROLLBACK NATIVE MLX RUNTIME =====" >&2
        while IFS= read -r path; do
            [[ -n "$path" ]] || continue
            if [[ -f "$BACKUP/$path" ]]; then
                mkdir -p "$(dirname "$path")"
                cp -p "$BACKUP/$path" "$path"
            fi
        done < "$MANIFEST"
    fi
    rm -rf "$TMP"
    exit "$rc"
}
trap cleanup EXIT

echo
echo "===== BUILD EXTENSION IN PLACE ====="
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-10}"
echo "CMAKE_BUILD_PARALLEL_LEVEL=$CMAKE_BUILD_PARALLEL_LEVEL"

python setup.py build_ext --inplace

echo
echo "===== POST-BUILD COMPILED MARKER CHECK ====="
python - <<'PY'
from pathlib import Path
import importlib.metadata as md
import mlx
import mlx.core as mx

needles = {
    b"MLX_P69B2_Q8_M4_SHARED": "P69B3",
    b"MLX_SDPA_GQA6_M4_HPT2_HEADPAIR": "P61",
}

candidates = []
for path in [Path(mx.__file__).resolve()]:
    if path.is_file() and path not in candidates:
        candidates.append(path)

for root_text in list(getattr(mlx, "__path__", [])) + list(getattr(mx, "__path__", [])):
    root = Path(root_text).resolve()
    if not root.exists():
        continue
    for pattern in ("*.so", "*.dylib", "*.a"):
        for path in root.rglob(pattern):
            path = path.resolve()
            if path.is_file() and path not in candidates:
                candidates.append(path)

print("mlx_version=" + md.version("mlx"))
print("mlx_core_file=" + str(Path(mx.__file__).resolve()))
print("native_runtime_file_count=" + str(len(candidates)))
for path in candidates:
    print("native_runtime_file=" + str(path))

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
    except OSError:
        return False

for path in candidates:
    for needle in needles:
        if found[needle] is None and contains(path, needle):
            found[needle] = path

for needle, label in needles.items():
    hit = found[needle]
    print(f"{label}_compiled_marker={hit or 'MISSING'}")
    if hit is None:
        raise SystemExit(
            f"REBUILD_PROMOTED_MLX_FAIL: {label} marker still absent after rebuild"
        )

print("PROMOTED_MLX_COMPILED_PASS")
PY

# The rebuild itself is now proven. Do not roll it back merely because another
# independent domain (Homebrew oMLX) might still need repair.
ROLLBACK=0

echo
echo "===== REPO CLEANLINESS AFTER GENERATED BUILD ====="
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || {
    git status --short
    fail "native rebuild unexpectedly changed tracked/unignored repo state"
}

echo "REPO_CLEAN_PASS"

echo
echo "===== FULL PROMOTED STACK VALIDATION ====="
# This may identify an independent Homebrew oMLX drift. If so, keep the now-
# validated MLX rebuild and repair the Homebrew domain separately.
bash "$VERIFY"

echo
echo "===== FINAL ====="
echo "REBUILD_PROMOTED_MLX_PASS"
