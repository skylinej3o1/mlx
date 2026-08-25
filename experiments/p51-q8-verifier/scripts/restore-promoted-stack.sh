#!/bin/bash
set -euo pipefail

VENV_ACT="/Users/skylinej17/.venvs/mlx-dspark/bin/activate"
REPO="$HOME/src/mlx-m1-qmv"
BRANCH="project51-q8-verifier"
P58_PATCH="$REPO/experiments/p51-q8-verifier/patches/0011-p58-fp16-gdn-verify-prework.patch"
P69B6_PATCH="$REPO/experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch"
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
[[ -x "$VERIFY" ]] || fail "validator is missing or not executable"

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

[[ -f "$LIVE_P58" ]] || fail "live P58 target missing"
[[ -f "$LIVE_VLMRT" ]] || fail "live P69B6 wrapper target missing"

TMP="$(mktemp -d /tmp/p51-promoted-restore.XXXXXX)"
STAGE="$TMP/stage"
BACKUP="$TMP/backup"
ROLLBACK=0
DUAL_EXISTED=0

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

echo "===== VERIFY STAGED PYTHON SOURCES ====="

"$OMLX_PY" - "$STAGE" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1]) / "omlx" / "patches"
p58 = root / "qwen35_gdn_prework.py"
dual = root / "qwen35_dual64_mlp.py"
vlmrt = root / "mlx_vlm_mtp" / "qwen35_vlm_runtime.py"
for p in (p58, dual, vlmrt):
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
    "omlx_p69b6_dual64_q8_gs64_m4_k5120_n17408",
):
    if token not in duals:
        raise SystemExit(f"staged P69B6 token missing: {token}")
for token in ("qwen35_dual64_mlp", "_apply_p69b6_dual64_mlp"):
    if token not in vlmrts:
        raise SystemExit(f"staged wrapper token missing: {token}")
print("STAGED_RUNTIME_PASS")
PY

echo "===== INSTALL STAGED HOMEBREW RUNTIME ====="
ROLLBACK=1
cp -p "$STAGE/omlx/patches/qwen35_gdn_prework.py" "$LIVE_P58"
cp -p "$STAGE/omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py" "$LIVE_VLMRT"
cp -p "$STAGE/omlx/patches/qwen35_dual64_mlp.py" "$LIVE_DUAL"

echo "p58_sha256=$(shasum -a 256 "$LIVE_P58" | awk '{print $1}')"
echo "p69b6_wrapper_sha256=$(shasum -a 256 "$LIVE_VLMRT" | awk '{print $1}')"
echo "p69b6_module_sha256=$(shasum -a 256 "$LIVE_DUAL" | awk '{print $1}')"

echo "===== FULL PROMOTED-STACK REVALIDATION ====="
bash "$VERIFY"

ROLLBACK=0

echo "===== FINAL ====="
echo "PROMOTED_STACK_RESTORE_PASS"
