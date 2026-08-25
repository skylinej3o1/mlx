#!/bin/bash
set -euo pipefail

VENV_ACT="/Users/skylinej17/.venvs/mlx-dspark/bin/activate"
REPO="$HOME/src/mlx-m1-qmv"
BRANCH="project51-q8-verifier"

PATCH_DIR="$REPO/experiments/p51-q8-verifier/patches"
P69B11_PATCH="$PATCH_DIR/0015-p69b11-qkvz-dual.patch"

VERIFY="$REPO/experiments/p51-q8-verifier/scripts/verify-promoted-stack.sh"
RESTORE="$REPO/experiments/p51-q8-verifier/scripts/restore-promoted-stack.sh"

B2_SOURCE="$HOME/src/mlx-m1-qmv-artifacts/p69/p69b11b2-asym-qkv-z.metal"
B4_SCRIPT="/tmp/p69b11b4-certification.sh"
B4_SUMMARY="$HOME/src/mlx-m1-qmv-artifacts/p69/p69b11b4/p69b11b4-integrated-4plus4-summary.txt"

EXPECTED_B2_SHA="e11dd85965c264cdd9b415348d0c2bd9d19ae2cfd20ce1a7ad1654d740bc8508"
EXPECTED_B4_SUMMARY_SHA="0a1153be3f7e4d0643da29abae923a15298fb393fe8fe7b7bcb611f4e934b39d"
EXPECTED_QMM_SHA="9375a8f380f14803075605c971533fa34a5ad08ff5b6c2e8bf2c029db4fbc2f8"

fail() {
    echo "PROMOTE_P69B11_FAIL: $*" >&2
    exit 1
}

sha256() {
    shasum -a 256 "$1" | awk '{print $1}'
}

[[ -f "$VENV_ACT" ]] || fail "missing venv activation"
# shellcheck disable=SC1090
source "$VENV_ACT"
cd "$REPO"

echo "===== P69B11 PROMOTION PREFLIGHT ====="

[[ "$(git branch --show-current)" == "$BRANCH" ]] || fail "wrong branch"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || \
    fail "repo must be clean"

git fetch --quiet fork "$BRANCH"
[[ "$(git rev-parse HEAD)" == "$(git rev-parse FETCH_HEAD)" ]] || \
    fail "local/fork mismatch"

[[ -f "$VERIFY" ]] || fail "validator missing"
[[ -f "$RESTORE" ]] || fail "restorer missing"
[[ -f "$B2_SOURCE" ]] || fail "frozen B2 Metal source missing"
[[ -f "$B4_SCRIPT" ]] || fail "B4 certification script missing"
[[ -f "$B4_SUMMARY" ]] || fail "B4 certification summary missing"
[[ ! -e "$P69B11_PATCH" ]] || fail "P69B11 patch already exists"

[[ "$(sha256 "$B2_SOURCE")" == "$EXPECTED_B2_SHA" ]] || \
    fail "B2 Metal source SHA mismatch"

[[ "$(sha256 "$B4_SUMMARY")" == "$EXPECTED_B4_SUMMARY_SHA" ]] || \
    fail "B4 summary SHA mismatch"

grep -Fq "verdict=CERTIFIED_PROMOTE_P69B11" "$B4_SUMMARY" || \
    fail "B4 certification verdict missing"
grep -Fq "pair_wins=4/4" "$B4_SUMMARY" || \
    fail "B4 4/4 pair-win evidence missing"
grep -Fq "mean_save_ms_cycle=+2.408602151" "$B4_SUMMARY" || \
    fail "B4 mean saving evidence mismatch"

bash "$VERIFY"

echo "PASS: certified evidence + current promoted stack"

OMLX_CMD="$(command -v omlx || true)"
[[ -n "$OMLX_CMD" ]] || fail "omlx command missing"
OMLX_REAL="$(python - "$OMLX_CMD" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
)"
OMLX_PY="$(head -n 1 "$OMLX_REAL")"
OMLX_PY="${OMLX_PY#\#!}"
[[ -x "$OMLX_PY" ]] || fail "oMLX owning Python missing"

OMLX_ROOT="$("$OMLX_PY" - <<'PY'
from pathlib import Path
import importlib.metadata as md
import omlx

if md.version("omlx") != "0.6.3rc2":
    raise SystemExit("wrong oMLX version")

print(Path(omlx.__file__).resolve().parent)
PY
)"

LIVE_VLMRT="$OMLX_ROOT/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py"
LIVE_QKVZ="$OMLX_ROOT/patches/qwen35_qkvz_dual.py"

[[ -f "$LIVE_VLMRT" ]] || fail "live Qwen3.5 wrapper missing"
[[ ! -e "$LIVE_QKVZ" ]] || fail "P69B11 live module unexpectedly already present"

TMP="$(mktemp -d /tmp/p69b11-promote.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

echo
echo "===== EXTRACT EXACT CERTIFIED PYTHON MODULE ====="

"$OMLX_PY" - \
    "$B4_SCRIPT" \
    "$B2_SOURCE" \
    "$TMP/qwen35_qkvz_dual.py" \
    "$EXPECTED_B2_SHA" \
    "$EXPECTED_QMM_SHA" <<'PY'
from __future__ import annotations

import ast
import hashlib
import os
import subprocess
import sys
from pathlib import Path

b4_path = Path(sys.argv[1])
metal_path = Path(sys.argv[2])
out_path = Path(sys.argv[3])
expected_metal_sha = sys.argv[4]
expected_qmm_sha = sys.argv[5]

b4 = b4_path.read_text()
metal = metal_path.read_text()

if hashlib.sha256(metal.encode()).hexdigest() != expected_metal_sha:
    raise SystemExit("frozen Metal source text SHA mismatch")

module_marker = 'cat >"$TMP/qwen35_qkvz_dual.py" <<\'PY\'\n'
replace_marker = '"$OMLX_PY" - "$TMP/qwen35_qkvz_dual.py" <<\'PY\'\n'
end_marker = "\nPY\n"

if b4.count(module_marker) != 1:
    raise SystemExit("certified module heredoc marker not unique")
if b4.count(replace_marker) != 1:
    raise SystemExit("certified module completion marker not unique")

m0 = b4.index(module_marker) + len(module_marker)
m1 = b4.index(end_marker, m0)
module_text = b4[m0:m1]

r0 = b4.index(replace_marker, m1) + len(replace_marker)
r1 = b4.index(end_marker, r0)
replace_script = b4[r0:r1]

# Re-run the exact certified B4 shell fragment that originally
# constructed and completed qwen35_qkvz_dual.py.
#
# This is deliberately safer than emulating the old placeholder
# mutation: the B4 fragment already succeeded in every certified
# CAND process.
build_start = b4.index(module_marker)
build_end = r1 + len(end_marker)

builder = b4[
    build_start:build_end
]

env = os.environ.copy()
env["TMP"] = str(
    out_path.parent
)
env["OMLX_PY"] = sys.executable

subprocess.run(
    [
        "/bin/bash",
        "-c",
        builder,
    ],
    env=env,
    check=True,
)

if not out_path.is_file():
    raise SystemExit(
        "certified B4 module builder did not create output"
    )

s = out_path.read_text()

required = (
    "P69B11_B3_QKVZ_DUAL",
    "OMLX_VERIFY_GDN_QKVZ_DUAL",
    "P69B11_B3_EXACT_PASS",
    "P69B11_B3_ENGAGED",
    "_SOURCE = _load_source()",
)
for token in required:
    if token not in s:
        raise SystemExit(f"certified module token missing: {token}")

start = s.index("SOURCE_PATH = Path.home()")
end_token = "_SOURCE = _load_source()\n"
end = s.index(end_token, start) + len(end_token)

state_names = (
    "_ENABLED",
    "_KERNEL",
    "_EXACT_DONE",
    "_ENGAGE_COUNT",
)

cert_tree = ast.parse(s)
state_parts = {}

for node in cert_tree.body:
    if not isinstance(
        node,
        (ast.Assign, ast.AnnAssign),
    ):
        continue

    names = []

    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.append(target.id)
    else:
        if isinstance(node.target, ast.Name):
            names.append(node.target.id)

    for name in names:
        if name in state_names:
            segment = ast.get_source_segment(
                s,
                node,
            )

            if not segment:
                raise SystemExit(
                    f"cannot preserve state {name}"
                )

            state_parts[name] = segment

missing_state = [
    name
    for name in state_names
    if name not in state_parts
]

if missing_state:
    raise SystemExit(
        "certified state assignment(s) missing: "
        + ", ".join(missing_state)
    )

state_block = "\n\n".join(
    state_parts[name]
    for name in state_names
)

replacement = (
    state_block
    + "\n\n"
    + "_SOURCE = " + repr(metal) + "\n\n"
    "if hashlib.sha256(Path(vq.__file__).resolve().read_bytes()).hexdigest() != EXPECTED_QMM_SHA:\n"
    "    raise RuntimeError(\n"
    "        \"P69B11 verifier-QMM SHA mismatch\"\n"
    "    )\n\n"
    "if hashlib.sha256(_SOURCE.encode()).hexdigest() != EXPECTED_SOURCE_SHA:\n"
    "    raise RuntimeError(\n"
    "        \"P69B11 embedded Metal source SHA mismatch\"\n"
    "    )\n"
)

packaged = s[:start] + replacement + s[end:]

packaged = packaged.replace(
    "P69B11-B3 gated integrated QKV+Z verifier projection bundle.",
    "P69B11 certified QKV+Z verifier projection bundle.",
    1,
)

packaged = packaged.replace(
    "# P69B11-B3 — gated QKV(KP2)+Z(KP1) bundle.",
    "# P69B11 — certified QKV(KP2)+Z(KP1) bundle.",
)

if "SOURCE_PATH" in packaged or "_load_source" in packaged:
    raise SystemExit("artifact-path dependency remains in packaged module")

compile(packaged, str(out_path), "exec")
out_path.write_text(packaged)

tree = ast.parse(packaged)

assigned_state = set()

for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                assigned_state.add(target.id)
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            assigned_state.add(node.target.id)

missing_state = [
    name
    for name in state_names
    if name not in assigned_state
]

if missing_state:
    raise SystemExit(
        "packaged state assignment(s) missing: "
        + ", ".join(missing_state)
    )

source_value = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        if any(
            isinstance(t, ast.Name) and t.id == "_SOURCE"
            for t in node.targets
        ):
            source_value = ast.literal_eval(node.value)
            break

if source_value is None:
    raise SystemExit("embedded _SOURCE assignment missing")

source_sha = hashlib.sha256(source_value.encode()).hexdigest()
if source_sha != expected_metal_sha:
    raise SystemExit(
        f"embedded Metal SHA {source_sha} != {expected_metal_sha}"
    )

qmm_value = None

for node in tree.body:
    if isinstance(node, ast.Assign):
        if any(
            isinstance(t, ast.Name)
            and t.id == "EXPECTED_QMM_SHA"
            for t in node.targets
        ):
            qmm_value = ast.literal_eval(
                node.value
            )
            break

if qmm_value is None:
    raise SystemExit(
        "embedded EXPECTED_QMM_SHA assignment missing"
    )

if qmm_value != expected_qmm_sha:
    raise SystemExit(
        "embedded verifier-QMM SHA mismatch: "
        f"{qmm_value} != {expected_qmm_sha}"
    )

print(
    "embedded_qmm_sha256="
    + qmm_value
)

print("packaged_module=" + str(out_path))
print("embedded_metal_sha256=" + source_sha)
print("PACKAGED_MODULE_PASS")
PY

echo
echo "===== BUILD PROMOTED WRAPPER + PATCH ====="

cp -p "$LIVE_VLMRT" "$TMP/qwen35_vlm_runtime.pre.py"

"$OMLX_PY" - \
    "$TMP/qwen35_vlm_runtime.pre.py" \
    "$TMP/qwen35_vlm_runtime.post.py" <<'PY'
from pathlib import Path
import sys

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

s = src.read_text()

anchor = """    from ..qwen35_dual64_mlp import apply as _apply_p69b6_dual64_mlp

    _apply_p69b6_dual64_mlp(q35_lang)
"""

insert = anchor + """
    # P69B11 — certified asymmetric QKV(KP2)+Z(KP1) bundle.
    # The wrapper is always installed; runtime behavior is gated by
    # OMLX_VERIFY_GDN_QKVZ_DUAL.
    from ..qwen35_qkvz_dual import apply as _apply_p69b11_qkvz_dual

    _apply_p69b11_qkvz_dual(q35_lang)
"""

if s.count(anchor) != 1:
    raise SystemExit("P69B6 wrapper anchor is not unique")

post = s.replace(anchor, insert, 1)
compile(post, str(dst), "exec")
dst.write_text(post)

print("PROMOTED_WRAPPER_PASS")
PY

"$OMLX_PY" - \
    "$TMP/qwen35_vlm_runtime.pre.py" \
    "$TMP/qwen35_vlm_runtime.post.py" \
    "$TMP/qwen35_qkvz_dual.py" \
    "$P69B11_PATCH" <<'PY'
from __future__ import annotations

import difflib
import sys
from pathlib import Path

pre_path = Path(sys.argv[1])
post_path = Path(sys.argv[2])
module_path = Path(sys.argv[3])
patch_path = Path(sys.argv[4])

pre = pre_path.read_text().splitlines(True)
post = post_path.read_text().splitlines(True)
module = module_path.read_text().splitlines(True)

wrapper_rel = "omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py"
module_rel = "omlx/patches/qwen35_qkvz_dual.py"

parts = []

parts.append(
    f"diff --git a/{wrapper_rel} b/{wrapper_rel}\n"
)
parts.extend(
    difflib.unified_diff(
        pre,
        post,
        fromfile=f"a/{wrapper_rel}",
        tofile=f"b/{wrapper_rel}",
        n=3,
    )
)

parts.append(
    f"diff --git a/{module_rel} b/{module_rel}\n"
)
parts.append("new file mode 100644\n")
parts.extend(
    difflib.unified_diff(
        [],
        module,
        fromfile="/dev/null",
        tofile=f"b/{module_rel}",
        n=3,
    )
)

patch_path.write_text("".join(parts))

print("patch=" + str(patch_path))
print("PROMOTED_PATCH_BUILT")
PY

echo "patch_sha256=$(sha256 "$P69B11_PATCH")"

echo
echo "===== DRY-RUN PROMOTED PATCH ====="

mkdir -p "$TMP/stage/omlx/patches/mlx_vlm_mtp"
cp -p \
    "$TMP/qwen35_vlm_runtime.pre.py" \
    "$TMP/stage/omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py"

(
    cd "$TMP/stage"
    patch --batch --forward -p1 < "$P69B11_PATCH"
)

"$OMLX_PY" - \
    "$TMP/stage" \
    "$EXPECTED_B2_SHA" <<'PY'
from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1]) / "omlx" / "patches"
expected = sys.argv[2]

module = root / "qwen35_qkvz_dual.py"
wrapper = root / "mlx_vlm_mtp" / "qwen35_vlm_runtime.py"

for path in (module, wrapper):
    if not path.is_file():
        raise SystemExit(f"missing staged file: {path}")
    compile(path.read_text(), str(path), "exec")

ms = module.read_text()
ws = wrapper.read_text()

for token in (
    "OMLX_VERIFY_GDN_QKVZ_DUAL",
    "P69B11_B3_QKVZ_DUAL",
    "P69B11_B3_EXACT_PASS",
    "P69B11_B3_ENGAGED",
):
    if token not in ms:
        raise SystemExit(f"staged P69B11 token missing: {token}")

for token in (
    "qwen35_qkvz_dual",
    "_apply_p69b11_qkvz_dual",
):
    if token not in ws:
        raise SystemExit(f"staged P69B11 wrapper token missing: {token}")

tree = ast.parse(ms)
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
    raise SystemExit("staged embedded _SOURCE missing")

got = hashlib.sha256(source.encode()).hexdigest()
print("staged_embedded_metal_sha256=" + got)

if got != expected:
    raise SystemExit("staged embedded Metal source SHA mismatch")

print("STAGED_P69B11_PATCH_PASS")
PY

echo
echo "===== EXTEND VALIDATOR / RESTORER / DOCS ====="

python - \
    "$VERIFY" \
    "$RESTORE" \
    "experiments/p51-q8-verifier/CURRENT.md" \
    "experiments/p51-q8-verifier/STATUS.md" \
    "experiments/p51-q8-verifier/RUNTIME-STATE.md" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path

verify = Path(sys.argv[1])
restore = Path(sys.argv[2])
current = Path(sys.argv[3])
status = Path(sys.argv[4])
runtime = Path(sys.argv[5])


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor, found {count}"
        )
    return text.replace(old, new, 1)


# ------------------------------------------------------------
# Validator
# ------------------------------------------------------------

s = verify.read_text()

s = replace_once(
    s,
    """    experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch
do
""",
    """    experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch \\
    experiments/p51-q8-verifier/patches/0015-p69b11-qkvz-dual.patch
do
""",
    "validator patch inventory",
)

s = replace_once(
    s,
    """print("P69B6_RUNTIME_PASS")
print("HOMEBREW_OMLX_RUNTIME_PASS")
""",
    """print("P69B6_RUNTIME_PASS")

qkvz = root / "patches" / "qwen35_qkvz_dual.py"
if not qkvz.is_file():
    raise SystemExit(
        f"PROMOTED_STACK_FAIL: P69B11 module missing: {qkvz}"
    )

qkvzs = qkvz.read_text()

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

print("P69B11_RUNTIME_PASS")
print("HOMEBREW_OMLX_RUNTIME_PASS")
""",
    "validator P69B11 runtime check",
)

verify.write_text(s)


# ------------------------------------------------------------
# Restorer
# ------------------------------------------------------------

s = restore.read_text()

s = replace_once(
    s,
    'P69B6_PATCH="$REPO/experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch"\n',
    'P69B6_PATCH="$REPO/experiments/p51-q8-verifier/patches/0014-p69b6-dual64-q8-mlp.patch"\n'
    'P69B11_PATCH="$REPO/experiments/p51-q8-verifier/patches/0015-p69b11-qkvz-dual.patch"\n',
    "restorer patch variable",
)

s = replace_once(
    s,
    '[[ -f "$P69B6_PATCH" ]] || fail "missing P69B6 patch"\n',
    '[[ -f "$P69B6_PATCH" ]] || fail "missing P69B6 patch"\n'
    '[[ -f "$P69B11_PATCH" ]] || fail "missing P69B11 patch"\n',
    "restorer patch requirement",
)

s = replace_once(
    s,
    'LIVE_DUAL="$OMLX_ROOT/patches/qwen35_dual64_mlp.py"\n',
    'LIVE_DUAL="$OMLX_ROOT/patches/qwen35_dual64_mlp.py"\n'
    'LIVE_QKVZ="$OMLX_ROOT/patches/qwen35_qkvz_dual.py"\n',
    "restorer live path",
)

s = replace_once(
    s,
    'DUAL_EXISTED=0\n',
    'DUAL_EXISTED=0\nQKVZ_EXISTED=0\n',
    "restorer existence flag",
)

s = replace_once(
    s,
    """        if [[ "$DUAL_EXISTED" -eq 1 ]]; then
            cp -p "$BACKUP/qwen35_dual64_mlp.py" "$LIVE_DUAL"
        else
            rm -f "$LIVE_DUAL"
        fi
""",
    """        if [[ "$DUAL_EXISTED" -eq 1 ]]; then
            cp -p "$BACKUP/qwen35_dual64_mlp.py" "$LIVE_DUAL"
        else
            rm -f "$LIVE_DUAL"
        fi
        if [[ "$QKVZ_EXISTED" -eq 1 ]]; then
            cp -p "$BACKUP/qwen35_qkvz_dual.py" "$LIVE_QKVZ"
        else
            rm -f "$LIVE_QKVZ"
        fi
""",
    "restorer rollback",
)

s = replace_once(
    s,
    """if [[ -f "$LIVE_DUAL" ]]; then
    DUAL_EXISTED=1
    cp -p "$LIVE_DUAL" "$STAGE/omlx/patches/qwen35_dual64_mlp.py"
    cp -p "$LIVE_DUAL" "$BACKUP/qwen35_dual64_mlp.py"
fi
""",
    """if [[ -f "$LIVE_DUAL" ]]; then
    DUAL_EXISTED=1
    cp -p "$LIVE_DUAL" "$STAGE/omlx/patches/qwen35_dual64_mlp.py"
    cp -p "$LIVE_DUAL" "$BACKUP/qwen35_dual64_mlp.py"
fi
if [[ -f "$LIVE_QKVZ" ]]; then
    QKVZ_EXISTED=1
    cp -p "$LIVE_QKVZ" "$STAGE/omlx/patches/qwen35_qkvz_dual.py"
    cp -p "$LIVE_QKVZ" "$BACKUP/qwen35_qkvz_dual.py"
fi
""",
    "restorer backup stage",
)

s = replace_once(
    s,
    """if [[ "$VLMRT_HAS" -ne "$DUAL_HAS" ]]; then
    fail "partial P69B6 runtime state; refusing automatic overwrite"
fi
""",
    """if [[ "$VLMRT_HAS" -ne "$DUAL_HAS" ]]; then
    fail "partial P69B6 runtime state; refusing automatic overwrite"
fi

QKVZ_VLMRT_HAS=0
QKVZ_HAS=0
grep -Fq "_apply_p69b11_qkvz_dual" "$STAGE/omlx/patches/mlx_vlm_mtp/qwen35_vlm_runtime.py" && QKVZ_VLMRT_HAS=1 || true
if [[ -f "$STAGE/omlx/patches/qwen35_qkvz_dual.py" ]] && \\
   grep -Fq "OMLX_VERIFY_GDN_QKVZ_DUAL" "$STAGE/omlx/patches/qwen35_qkvz_dual.py"; then
    QKVZ_HAS=1
fi

echo "P69B11_WRAPPER_PRESENT=$QKVZ_VLMRT_HAS"
echo "P69B11_MODULE_PRESENT=$QKVZ_HAS"

if [[ "$QKVZ_VLMRT_HAS" -ne "$QKVZ_HAS" ]]; then
    fail "partial P69B11 runtime state; refusing automatic overwrite"
fi
""",
    "restorer P69B11 classification",
)

s = replace_once(
    s,
    """if [[ "$VLMRT_HAS" -eq 0 ]]; then
    echo "===== STAGE P69B6 RESTORE ====="
    (
        cd "$STAGE"
        patch --batch --forward -p1 < "$P69B6_PATCH"
    )
else
    echo "P69B6 already present; no staged change"
fi
""",
    """if [[ "$VLMRT_HAS" -eq 0 ]]; then
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
""",
    "restorer apply P69B11",
)

s = replace_once(
    s,
    """dual = root / "qwen35_dual64_mlp.py"
vlmrt = root / "mlx_vlm_mtp" / "qwen35_vlm_runtime.py"
for p in (p58, dual, vlmrt):
""",
    """dual = root / "qwen35_dual64_mlp.py"
qkvz = root / "qwen35_qkvz_dual.py"
vlmrt = root / "mlx_vlm_mtp" / "qwen35_vlm_runtime.py"
for p in (p58, dual, qkvz, vlmrt):
""",
    "restorer staged file inventory",
)

s = replace_once(
    s,
    """for token in ("qwen35_dual64_mlp", "_apply_p69b6_dual64_mlp"):
    if token not in vlmrts:
        raise SystemExit(f"staged wrapper token missing: {token}")
print("STAGED_RUNTIME_PASS")
""",
    """for token in ("qwen35_dual64_mlp", "_apply_p69b6_dual64_mlp"):
    if token not in vlmrts:
        raise SystemExit(f"staged wrapper token missing: {token}")

qkvzs = qkvz.read_text()
for token in (
    "OMLX_VERIFY_GDN_QKVZ_DUAL",
    "P69B11_B3_QKVZ_DUAL",
    "P69B11_B3_EXACT_PASS",
    "P69B11_B3_ENGAGED",
):
    if token not in qkvzs:
        raise SystemExit(f"staged P69B11 token missing: {token}")
for token in ("qwen35_qkvz_dual", "_apply_p69b11_qkvz_dual"):
    if token not in vlmrts:
        raise SystemExit(f"staged P69B11 wrapper token missing: {token}")

import ast
import hashlib

tree = ast.parse(qkvzs)
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

print("STAGED_RUNTIME_PASS")
""",
    "restorer staged P69B11 verification",
)

s = replace_once(
    s,
    """cp -p "$STAGE/omlx/patches/qwen35_dual64_mlp.py" "$LIVE_DUAL"

echo "p58_sha256=$(shasum -a 256 "$LIVE_P58" | awk '{print $1}')"
""",
    """cp -p "$STAGE/omlx/patches/qwen35_dual64_mlp.py" "$LIVE_DUAL"
cp -p "$STAGE/omlx/patches/qwen35_qkvz_dual.py" "$LIVE_QKVZ"

echo "p58_sha256=$(shasum -a 256 "$LIVE_P58" | awk '{print $1}')"
""",
    "restorer install P69B11",
)

s = replace_once(
    s,
    """echo "p69b6_module_sha256=$(shasum -a 256 "$LIVE_DUAL" | awk '{print $1}')"

echo "===== FULL PROMOTED-STACK REVALIDATION ====="
""",
    """echo "p69b6_module_sha256=$(shasum -a 256 "$LIVE_DUAL" | awk '{print $1}')"
echo "p69b11_module_sha256=$(shasum -a 256 "$LIVE_QKVZ" | awk '{print $1}')"

echo "===== FULL PROMOTED-STACK REVALIDATION ====="
""",
    "restorer P69B11 fingerprint",
)

restore.write_text(s)


# ------------------------------------------------------------
# CURRENT.md
# ------------------------------------------------------------

current.write_text("""# P51 verifier current checkpoint

## Promoted champion after P69B11

The complete promoted verifier stack is now:

- P58 FP16 GDN fused verifier prework;
- P61 HEADPAIR HPT2 SDPA;
- P69B3 SG2R4 Q8 M4 shared-weight projection;
- P69B6 DUAL64 verifier MLP fusion;
- P69B11 asymmetric GDN QKV(KP2)+Z(KP1) projection bundle;
- fixed D3 / verifier M4.

The canonical validator must pass all Git, both compiled MLX ABI, and
Homebrew oMLX Python-patch domains before further tuning.

### P69B11 certification

P69B11 bundles the two GDN projections sharing the same FP16 verifier input:

- QKV: M4 K5120 N10240 Q8 GS64, KP2;
- Z: M4 K5120 N6144 Q8 GS64, KP1.

It preserves independent QKV and Z arithmetic/reduction orders and separate
FP16 projection output boundaries. It does not use a homogeneous N16384 QMM.

P69B11-B2 isolated exactness:

- QKV bit-exact: PASS;
- Z bit-exact: PASS;
- frozen Metal source SHA256:
  `e11dd85965c264cdd9b415348d0c2bd9d19ae2cfd20ce1a7ad1654d740bc8508`.

P69B11-B3 2+2 scout:

- mean saving: +2.228494624 ms/cycle;
- TG: +1.4598%;
- pair wins: 2/2.

P69B11-B4 balanced 4+4 certification:

- BASE mean BPC: 147.508870968 ms/cycle;
- CAND mean BPC: 145.100268817 ms/cycle;
- mean saving: +2.408602151 ms/cycle (+1.6329%);
- median saving: +2.750000000 ms/cycle;
- BASE mean TG: 17.888097 tok/s;
- CAND mean TG: 18.157695 tok/s;
- TG improvement: +1.5071%;
- pair wins: 4/4;
- all four CAND actual-weight exactness gates: PASS;
- all eight output hashes: `101ae2aec9793dfe`;
- all eight trajectories: 186 cycles / 325/442 / 155/101/69.

B4 certification summary SHA256:

`0a1153be3f7e4d0643da29abae923a15298fb393fe8fe7b7bcb611f4e934b39d`

Verdict:

**P69B11 CERTIFIED AND PROMOTED.**

### Runtime gate

P69B11 is runtime-gated by:

`OMLX_VERIFY_GDN_QKVZ_DUAL=1`

The permanent validator/restorer track the packaged P69B11 module and exact
embedded Metal source fingerprint.

## Closed work

Do not reopen:

- P69B5 verifier-QMM staging/synchronization;
- P69B6-D residual ADD->RMS fusion;
- P69B8 RMSNormGated fusion;
- P69B9 attention-gate final epilogue;
- P69B10-C recurrent final-state alias.

Do not rerun P69B7 profiling.

## Next work

**P69B12 — choose the next remaining high-leverage verifier seam using the
existing P69B7/P69B10 measurements. Do not rerun profiling.**

Start from the now-promoted P58/P61/P69B3/P69B6/P69B11 stack.
""")


# ------------------------------------------------------------
# STATUS.md append
# ------------------------------------------------------------

st = status.read_text()
marker = "## P69B11-B4 — certified asymmetric QKV+Z projection bundle"

if marker not in st:
    st = st.rstrip() + """

## P69B11-B4 — certified asymmetric QKV+Z projection bundle

P69B11 bundles GDN `in_proj_qkv` and `in_proj_z` into one Metal dispatch while
preserving their independent verifier arithmetic:

- QKV: M4 K5120 N10240 Q8 GS64, KP2;
- Z: M4 K5120 N6144 Q8 GS64, KP1;
- separate FP16 output boundaries preserved;
- no homogeneous N16384 concatenated QMM.

B2 synthetic exactness was bit-exact for both outputs. B3 then passed a 2+2
integrated scout at +2.228494624 ms/cycle and +1.4598% TG with 2/2 pair wins.

B4 balanced 4+4 certification:

- BASE mean BPC: 147.508870968 ms/cycle;
- CAND mean BPC: 145.100268817 ms/cycle;
- mean saving: +2.408602151 ms/cycle (+1.6329%);
- median saving: +2.750000000 ms/cycle;
- TG improvement: +1.5071%;
- pair wins: 4/4;
- all four CAND actual-weight exactness checks: PASS;
- all eight frozen hashes: `101ae2aec9793dfe`;
- all eight trajectories: 186 cycles / 325/442 / 155/101/69.

Certification summary SHA256:

`0a1153be3f7e4d0643da29abae923a15298fb393fe8fe7b7bcb611f4e934b39d`

Verdict: **CERTIFIED / PROMOTE P69B11.**

Runtime gate:

`OMLX_VERIFY_GDN_QKVZ_DUAL=1`

Next work is P69B12: select the next remaining verifier seam from existing
P69B7/P69B10 measurements without rerunning profiling.
""" + "\n"

status.write_text(st)


# ------------------------------------------------------------
# RUNTIME-STATE.md
# ------------------------------------------------------------

rt = runtime.read_text()

if "- **P69B11** asymmetric GDN QKV+Z projection bundle;" not in rt:
    anchor = "- **P69B6** packaged DUAL64 verifier MLP fusion."
    if anchor not in rt:
        raise SystemExit("RUNTIME-STATE promoted-stack anchor missing")
    rt = rt.replace(
        anchor,
        anchor + "\n- **P69B11** asymmetric GDN QKV+Z projection bundle;",
        1,
    )

runtime_marker = "## P69B11 certified runtime"

if runtime_marker not in rt:
    rt = rt.rstrip() + """

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
""" + "\n"

runtime.write_text(rt)

print("PROMOTION_METADATA_EDIT_PASS")
PY

echo
echo "===== STATIC VALIDATION ====="

bash -n "$VERIFY"
bash -n "$RESTORE"
git diff --check

grep -Fq \
    "0015-p69b11-qkvz-dual.patch" \
    "$VERIFY"

grep -Fq \
    "P69B11_RUNTIME_PASS" \
    "$VERIFY"

grep -Fq \
    "STAGE P69B11 RESTORE" \
    "$RESTORE"

grep -Fq \
    "P69B11 CERTIFIED AND PROMOTED" \
    experiments/p51-q8-verifier/CURRENT.md

echo "STATIC_PROMOTION_PASS"

echo
echo "===== PROMOTION DIFF SUMMARY ====="

git status --short
git diff --stat

echo
echo "===== COMMIT + PUSH PROMOTION ====="

git add \
    "$P69B11_PATCH" \
    "$VERIFY" \
    "$RESTORE" \
    experiments/p51-q8-verifier/CURRENT.md \
    experiments/p51-q8-verifier/STATUS.md \
    experiments/p51-q8-verifier/RUNTIME-STATE.md

git commit -m "Promote P69B11 QKVZ verifier bundle"
git push fork "$BRANCH"

git fetch --quiet fork "$BRANCH"
[[ "$(git rev-parse HEAD)" == "$(git rev-parse FETCH_HEAD)" ]] || \
    fail "post-push local/fork mismatch"
[[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || \
    fail "repo dirty after promotion commit"

echo
echo "PROMOTION_HEAD=$(git rev-parse HEAD)"

echo
echo "===== INSTALL CERTIFIED P69B11 INTO LIVE OMLX ====="

bash "$RESTORE"

echo
echo "===== FINAL CANONICAL VALIDATION ====="

bash "$VERIFY"

echo
echo "===== FINAL ====="
git status -sb
echo "P69B11_PROMOTION_PASS"
echo "P69B11_NEXT=P69B12"
