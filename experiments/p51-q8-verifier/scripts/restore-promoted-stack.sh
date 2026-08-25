#!/bin/bash
set -euo pipefail

VENV_ACT="/Users/skylinej17/.venvs/mlx-dspark/bin/activate"
REPO="$HOME/src/mlx-m1-qmv"
BRANCH="project51-q8-verifier"
P58_PATCH="$REPO/experiments/p51-q8-verifier/patches/0011-p58-fp16-gdn-verify-prework.patch"
P69B6_PATCH="$REPO/experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch"
P69B11_PATCH="$REPO/experiments/p51-q8-verifier/patches/0015-p69b11-qkvz-dual.patch"
P69B12_PATCH="$REPO/experiments/p51-q8-verifier/patches/0016-p69b12-ba-piggyback.patch"
VERIFY="$REPO/experiments/p51-q8-verifier/scripts/verify-promoted-stack.sh"

fail() {
    echo "RESTORE_PROMOTED_STACK_FAIL: $*" >&2
    exit 1
}

[[ -f "$VENV_ACT" ]] || fail "missing venv activation"
# shellcheck disable=SC1090
source "$VENV_ACT"
cd "$REPO"

[[ "$(git branch --show-current)" == "$BRANCH" ]] || fail "wrong branch"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || \
    fail "repo must be clean before runtime repair"

git fetch --quiet fork "$BRANCH"
[[ "$(git rev-parse HEAD)" == "$(git rev-parse FETCH_HEAD)" ]] || \
    fail "local/fork mismatch; sync Git before runtime repair"

[[ -f "$P58_PATCH" ]] || fail "missing P58 patch"
[[ -f "$P69B6_PATCH" ]] || fail "missing P69B6 patch"
[[ -f "$P69B11_PATCH" ]] || fail "missing P69B11 patch"
[[ -f "$P69B12_PATCH" ]] || fail "missing P69B12 patch"
[[ -f "$VERIFY" ]] || fail "validator is missing"

OMLX_CMD="$(command -v omlx || true)"
[[ -n "$OMLX_CMD" ]] || fail "omlx command not found"
OMLX_REAL="$(python - "$OMLX_CMD" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
)"
OMLX_PY="$(head -n 1 "$OMLX_REAL")"
OMLX_PY="${OMLX_PY#\#!}"
[[ -x "$OMLX_PY" ]] || fail "oMLX owning Python missing: $OMLX_PY"

OMLX_ROOT="$("$OMLX_PY" - <<'PY'
from pathlib import Path
import importlib.metadata as md
import omlx
if md.version("omlx") != "0.6.3rc2":
    raise SystemExit("wrong oMLX version")
print(Path(omlx.__file__).resolve().parent)
PY
)"

LIVE_P58="$OMLX_ROOT/patches/qwen35_gdn_prework.py"
LIVE_VLMRT="$OMLX_ROOT/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py"
LIVE_DUAL="$OMLX_ROOT/patches/qwen35_dual64_mlp.py"
LIVE_QKVZ="$OMLX_ROOT/patches/qwen35_qkvz_dual.py"

[[ -f "$LIVE_P58" ]] || fail "live P58 target missing"
[[ -f "$LIVE_VLMRT" ]] || fail "live P69B6 wrapper target missing"

TMP="$(mktemp -d /tmp/p51-promoted-restore.XXXXXX)"
STAGE="$TMP/stage"
BACKUP="$TMP/backup"
ROLLBACK=0
DUAL_EXISTED=0
QKVZ_EXISTED=0

cleanup() {
    rc=$?
    if [[ "$ROLLBACK" -eq 1 ]]; then
        echo "===== ROLLBACK HOMEBREW RUNTIME =====" >&2
        cp -p "$BACKUP/qwen35_gdn_prework.py" "$LIVE_P58"
        cp -p "$BACKUP/qwen35_vlm_runtime.py" "$LIVE_VLMRT"
        if [[ "$DUAL_EXISTED" -eq 1 ]]; then
            cp -p "$BACKUP/qwen35_dual64_mlp.py" "$LIVE_DUAL"
        else
            rm -f "$LIVE_DUAL"
        fi
        if [[ "$QKVZ_EXISTED" -eq 1 ]]; then
            cp -p "$BACKUP/qwen35_qkvz_dual.py" "$LIVE_QKVZ"
        else
            rm -f "$LIVE_QKVZ"
        fi
    fi
    rm -rf "$TMP"
    exit "$rc"
}
trap cleanup EXIT

mkdir -p "$STAGE/omlx/patches/mlx_vlm_mtp" "$BACKUP"
cp -p "$LIVE_P58" "$STAGE/omlx/patches/qwen35_gdn_prework.py"
cp -p "$LIVE_VLMRT" "$STAGE/omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py"
cp -p "$LIVE_P58" "$BACKUP/qwen35_gdn_prework.py"
cp -p "$LIVE_VLMRT" "$BACKUP/qwen35_vlm_runtime.py"
if [[ -f "$LIVE_DUAL" ]]; then
    DUAL_EXISTED=1
    cp -p "$LIVE_DUAL" "$STAGE/omlx/patches/qwen35_dual64_mlp.py"
    cp -p "$LIVE_DUAL" "$BACKUP/qwen35_dual64_mlp.py"
fi
if [[ -f "$LIVE_QKVZ" ]]; then
    QKVZ_EXISTED=1
    cp -p "$LIVE_QKVZ" "$STAGE/omlx/patches/qwen35_qkvz_dual.py"
    cp -p "$LIVE_QKVZ" "$BACKUP/qwen35_qkvz_dual.py"
fi

echo "===== STAGED RUNTIME CLASSIFICATION ====="

P58_STATE="$("$OMLX_PY" - "$STAGE/omlx/patches/qwen35_gdn_prework.py" <<'PY'
from pathlib import Path
import sys
s = Path(sys.argv[1]).read_text()
post = (
    "OMLX_GDN_VERIFY_PREWORK_FP16" in s
    and "inputs.dtype not in (mx.bfloat16, mx.float16)" in s
    and "conv_state.dtype != inputs.dtype" in s
    and "self.conv1d.weight.dtype != inputs.dtype" in s
)
pre = (
    "OMLX_GDN_VERIFY_PREWORK_FP16" not in s
    and "inputs.dtype != mx.bfloat16" in s
    and "conv_state.dtype != mx.bfloat16" in s
    and "self.conv1d.weight.dtype != mx.bfloat16" in s
)
print("POST" if post else "PRE" if pre else "DIVERGED")
PY
)"
echo "P58_STATE=$P58_STATE"
[[ "$P58_STATE" != "DIVERGED" ]] || fail "P58 source diverged from known pre/post structure"

VLMRT_HAS=0
DUAL_HAS=0
grep -Fq "_apply_p69b6_dual64_mlp" "$STAGE/omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py" && VLMRT_HAS=1 || true
if [[ -f "$STAGE/omlx/patches/qwen35_dual64_mlp.py" ]] && \
   grep -Fq "OMLX_VERIFY_MLP_DUAL64" "$STAGE/omlx/patches/qwen35_dual64_mlp.py"; then
    DUAL_HAS=1
fi

echo "P69B6_WRAPPER_PRESENT=$VLMRT_HAS"
echo "P69B6_MODULE_PRESENT=$DUAL_HAS"

if [[ "$VLMRT_HAS" -ne "$DUAL_HAS" ]]; then
    fail "partial P69B6 runtime state; refusing automatic overwrite"
fi

QKVZ_VLMRT_HAS=0
QKVZ_HAS=0
grep -Fq "_apply_p69b11_qkvz_dual" "$STAGE/omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py" && QKVZ_VLMRT_HAS=1 || true
if [[ -f "$STAGE/omlx/patches/qwen35_qkvz_dual.py" ]] && \
   grep -Fq "OMLX_VERIFY_GDN_QKVZ_DUAL" "$STAGE/omlx/patches/qwen35_qkvz_dual.py" && \
   grep -Fq "_ENABLED" "$STAGE/omlx/patches/qwen35_qkvz_dual.py" && \
   grep -Fq "_KERNEL" "$STAGE/omlx/patches/qwen35_qkvz_dual.py" && \
   grep -Fq "_EXACT_DONE" "$STAGE/omlx/patches/qwen35_qkvz_dual.py" && \
   grep -Fq "_ENGAGE_COUNT" "$STAGE/omlx/patches/qwen35_qkvz_dual.py"; then
    QKVZ_HAS=1
fi

echo "P69B11_WRAPPER_PRESENT=$QKVZ_VLMRT_HAS"
echo "P69B11_MODULE_PRESENT=$QKVZ_HAS"

if [[ "$QKVZ_VLMRT_HAS" -ne "$QKVZ_HAS" ]]; then
    fail "partial P69B11 runtime state; refusing automatic overwrite"
fi

P69B12_HAS=0

if [[ "$QKVZ_HAS" -eq 1 ]] && \
   grep -Fq "OMLX_VERIFY_GDN_BA_PIGGYBACK" \
       "$STAGE/omlx/patches/qwen35_qkvz_dual.py" && \
   grep -Fq "P69B12_B3_PATCH" \
       "$STAGE/omlx/patches/qwen35_qkvz_dual.py" && \
   grep -Fq "_PIGGY_SOURCE" \
       "$STAGE/omlx/patches/qwen35_qkvz_dual.py"; then
    P69B12_HAS=1
fi

echo "P69B12_MODULE_PRESENT=$P69B12_HAS"

if [[ "$P58_STATE" == "PRE" ]]; then
    echo "===== STAGE P58 RESTORE ====="
    (
        cd "$STAGE"
        patch --batch --forward -p1 < "$P58_PATCH"
    )
else
    echo "P58 already present; no staged change"
fi

if [[ "$VLMRT_HAS" -eq 0 ]]; then
    echo "===== STAGE P69B6 RESTORE ====="
    (
        cd "$STAGE"
        patch --batch --forward -p1 < "$P69B6_PATCH"
    )
else
    echo "P69B6 already present; no staged change"
fi

if [[ "$QKVZ_VLMRT_HAS" -eq 0 ]]; then
    echo "===== STAGE P69B11 RESTORE ====="
    (
        cd "$STAGE"
        patch --batch --forward -p1 < "$P69B11_PATCH"
    )
else
    echo "P69B11 already present; no staged change"
fi

if [[ "$P69B12_HAS" -eq 0 ]]; then
    echo "===== STAGE P69B12 RESTORE ====="
    (
        cd "$STAGE"
        patch --batch --forward -p1 < "$P69B12_PATCH"
    )
else
    echo "P69B12 already present; no staged change"
fi

echo "===== VERIFY STAGED PYTHON SOURCES ====="

"$OMLX_PY" - "$STAGE" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1]) / "omlx" / "patches"
p58 = root / "qwen35_gdn_prework.py"
dual = root / "qwen35_dual64_mlp.py"
qkvz = root / "qwen35_qkvz_dual.py"
vlmrt = root / "mlx_vlm_mtp" / "qwen35_vlm_runtime.py"
for p in (p58, dual, qkvz, vlmrt):
    if not p.is_file():
        raise SystemExit(f"missing staged file: {p}")
    compile(p.read_text(), str(p), "exec")
p58s = p58.read_text()
for token in (
    "OMLX_GDN_VERIFY_PREWORK_FP16",
    "inputs.dtype not in (mx.bfloat16, mx.float16)",
    "conv_state.dtype != inputs.dtype",
    "self.conv1d.weight.dtype != inputs.dtype",
    "dtype=inputs.dtype",
):
    if token not in p58s:
        raise SystemExit(f"staged P58 token missing: {token}")
duals = dual.read_text()
vlmrts = vlmrt.read_text()
for token in (
    "OMLX_VERIFY_MLP_DUAL64",
    "P69B6_E4_DUAL64",
    "omlx_p69b6_dual64_",
    "q8_gs64_m4_k5120_n17408",
):
    if token not in duals:
        raise SystemExit(f"staged P69B6 token missing: {token}")
for token in ("qwen35_dual64_mlp", "_apply_p69b6_dual64_mlp"):
    if token not in vlmrts:
        raise SystemExit(f"staged wrapper token missing: {token}")

qkvzs = qkvz.read_text()
for token in (
    "OMLX_VERIFY_GDN_QKVZ_DUAL",
    "OMLX_VERIFY_GDN_BA_PIGGYBACK",
    "P69B11_B3_QKVZ_DUAL",
    "P69B11_B3_EXACT_PASS",
    "P69B11_B3_ENGAGED",
    "P69B12_B3_PATCH",
    "P69B12_B3_EXACT_PASS",
    "P69B12_B3_ENGAGED",
):
    if token not in qkvzs:
        raise SystemExit(f"staged P69B11 token missing: {token}")
for token in ("qwen35_qkvz_dual", "_apply_p69b11_qkvz_dual"):
    if token not in vlmrts:
        raise SystemExit(f"staged P69B11 wrapper token missing: {token}")

import ast
import hashlib

tree = ast.parse(qkvzs)

assigned_state = set()

for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                assigned_state.add(target.id)
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            assigned_state.add(node.target.id)

for name in (
    "_ENABLED",
    "_PIGGY_ENABLED",
    "_KERNEL",
    "_BASE_KERNEL",
    "_EXACT_DONE",
    "_ENGAGE_COUNT",
):
    if name not in assigned_state:
        raise SystemExit(
            f"staged P69B11 state assignment missing: {name}"
        )

source = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        if any(
            isinstance(t, ast.Name) and t.id == "_SOURCE"
            for t in node.targets
        ):
            source = ast.literal_eval(node.value)
            break

if source is None:
    raise SystemExit("staged P69B11 embedded _SOURCE missing")

source_sha = hashlib.sha256(source.encode()).hexdigest()
if source_sha != "e11dd85965c264cdd9b415348d0c2bd9d19ae2cfd20ce1a7ad1654d740bc8508":
    raise SystemExit("staged P69B11 embedded Metal SHA mismatch")

piggy_source = None

for node in tree.body:
    if isinstance(node, ast.Assign):
        if any(
            isinstance(t, ast.Name)
            and t.id == "_PIGGY_SOURCE"
            for t in node.targets
        ):
            piggy_source = ast.literal_eval(node.value)
            break

if piggy_source is None:
    raise SystemExit(
        "staged P69B12 embedded _PIGGY_SOURCE missing"
    )

piggy_source_sha = hashlib.sha256(
    piggy_source.encode()
).hexdigest()

if piggy_source_sha != (
    "dc30e64adbbd82eac7fc423137ca8b15"
    "a6727d3cecab662d1eb28033eb36142a"
):
    raise SystemExit(
        "staged P69B12 embedded Metal SHA mismatch"
    )

print(
    "staged_p69b12_piggy_sha256="
    + piggy_source_sha
)

print("STAGED_RUNTIME_PASS")
PY

echo "===== INSTALL STAGED HOMEBREW RUNTIME ====="
ROLLBACK=1
cp -p "$STAGE/omlx/patches/qwen35_gdn_prework.py" "$LIVE_P58"
cp -p "$STAGE/omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py" "$LIVE_VLMRT"
cp -p "$STAGE/omlx/patches/qwen35_dual64_mlp.py" "$LIVE_DUAL"
cp -p "$STAGE/omlx/patches/qwen35_qkvz_dual.py" "$LIVE_QKVZ"

echo "p58_sha256=$(shasum -a 256 "$LIVE_P58" | awk '{print $1}')"
echo "p69b6_wrapper_sha256=$(shasum -a 256 "$LIVE_VLMRT" | awk '{print $1}')"
echo "p69b6_module_sha256=$(shasum -a 256 "$LIVE_DUAL" | awk '{print $1}')"
echo "p69b11_module_sha256=$(shasum -a 256 "$LIVE_QKVZ" | awk '{print $1}')"

echo "===== FULL PROMOTED-STACK REVALIDATION ====="
bash "$VERIFY"

ROLLBACK=0

echo "===== FINAL ====="
echo "PROMOTED_STACK_RESTORE_PASS"
