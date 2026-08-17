import os
import time
import types
import hashlib
import statistics

os.environ["MLX_QMV_FAST_M4"] = "1"
os.environ.pop("MLX_QMV_FAST_M3", None)

os.environ["M1FORGE_COMPILED_VERIFY"] = "1"
os.environ["M1FORGE_VERIFY_M4_ATTN"] = "1"
os.environ["M1FORGE_VERIFY_M4_VARIANT"] = "p36"

os.environ["M1FORGE_MTP_DRAFT_HEAD"] = "q6_g32"
os.environ["M1FORGE_MTP_DRAFT_HEAD_DEBUG"] = "0"
os.environ["M1FORGE_COMPILED_VERIFY_DEBUG"] = "0"

import mlx.core as mx
import mlx_vlm
from mlx_vlm.speculative import load_drafter


TARGET = (
    "/Users/skylinej17/models/"
    "Qwen3.8-27B-MLX-6bit-FP16-Q8HEAD"
)

DRAFT = (
    "/Users/skylinej17/models/"
    "Qwen3.8-27B-MTP-G4-U3-D4-Q6ATTN-FCQ6-27.556"
)

PROMPT = """<|im_start|>user
Implement an LRU cache in Python using a dictionary and doubly linked list. Include type hints and a usage example.<|im_end|>
<|im_start|>assistant
<think>

</think>

"""

EXPECTED_ROUNDS = 138
EXPECTED_TEXT = "e39b478ae4a8"
EXPECTED_TRAJ = "f7801569fbdd"

VOCAB = 248320
N_PAIRS = 10


def text_hash(x):
    return hashlib.sha256(
        x.encode("utf-8")
    ).hexdigest()[:12]


def traj_hash(a, d):
    return hashlib.sha256(
        repr((a, d)).encode("utf-8")
    ).hexdigest()[:12]


print("Loading target ONCE...")
model, processor = mlx_vlm.load(TARGET)

print("Loading canonical MTP drafter ONCE...")
draft, kind = load_drafter(
    DRAFT,
    kind="mtp",
)

mx.eval(model.parameters())
mx.eval(draft.parameters())
mx.synchronize()


# ============================================================
# FORCE CERTIFIED P38E BIND, THEN RECOVER EXACT Q6/G32 TENSORS
# ============================================================

draft.bind(model)

q6_head = draft._lm_head_fn

print()
print("P38E live head:", q6_head)

q6_cells = dict(
    zip(
        q6_head.__code__.co_freevars,
        [
            c.cell_contents
            for c in q6_head.__closure__
        ],
    )
)

for name in sorted(q6_cells):
    x = q6_cells[name]

    if isinstance(x, mx.array):
        print(
            f"  {name:8s}",
            x.shape,
            x.dtype,
        )


Q6_W = q6_cells["q6_w"]
Q6_S = q6_cells["q6_s"]
Q6_B = q6_cells["q6_b"]

assert tuple(Q6_W.shape) == (248320, 960)
assert tuple(Q6_S.shape) == (248320, 160)
assert tuple(Q6_B.shape) == (248320, 160)


# ============================================================
# BUILD Q5/G32 FROM ORIGINAL TARGET Q8/G64 HEAD
# ============================================================

if hasattr(model, "language_model"):
    target_head = model.language_model.lm_head
else:
    target_head = model.lm_head

print()
print(
    "Building Q5/G32 search head from:",
    target_head,
)

assert int(target_head.bits) == 8
assert int(target_head.group_size) == 64

w_fp16 = mx.dequantize(
    target_head.weight,
    target_head.scales,
    target_head.biases,
    group_size=64,
    bits=8,
    mode="affine",
    dtype=mx.float16,
)

mx.eval(w_fp16)
mx.synchronize()

Q5_W, Q5_S, Q5_B = mx.quantize(
    w_fp16,
    group_size=32,
    bits=5,
    mode="affine",
)

mx.eval(
    Q5_W,
    Q5_S,
    Q5_B,
)
mx.synchronize()

del w_fp16
mx.clear_cache()

print(
    "[P41E] Q5 ready:",
    "weight=",
    Q5_W.shape,
    "scales=",
    Q5_S.shape,
)


# ============================================================
# EXACT TWO-STAGE GREEDY TOKEN SELECTOR
# ============================================================

jury_calls = [0]


def q5_logits(h):
    return mx.quantized_matmul(
        h,
        Q5_W,
        Q5_S,
        Q5_B,
        transpose=True,
        group_size=32,
        bits=5,
        mode="affine",
    )


def q5_top2_q6_token(h):
    jury_calls[0] += 1

    # --------------------------------------------------------
    # Stage 1: fast Q5 search over complete vocabulary.
    # --------------------------------------------------------

    logits5 = q5_logits(h)

    part = mx.argpartition(
        logits5,
        VOCAB - 2,
        axis=-1,
    )

    ids = part[..., -2:]

    # --------------------------------------------------------
    # Stage 2: evaluate ONLY those two rows with certified Q6.
    # --------------------------------------------------------

    flat_ids = ids.reshape(-1)

    wk = Q6_W[flat_ids]
    sk = Q6_S[flat_ids]
    bk = Q6_B[flat_ids]

    scores6 = mx.quantized_matmul(
        h,
        wk,
        sk,
        bk,
        transpose=True,
        group_size=32,
        bits=6,
        mode="affine",
    )

    local = mx.argmax(
        scores6,
        axis=-1,
    )

    chosen = mx.take_along_axis(
        ids,
        local[..., None],
        axis=-1,
    )[..., 0]

    return chosen


# ============================================================
# MONKEYPATCH ONLY THE TWO GREEDY HEAD DECISION SITES
#
# Stock mode:
#   unchanged certified P38E Q6/G32
#
# Jury mode:
#   Q5 full vocab -> top2 -> exact Q6 rerank
#
# All model forwards / KV / target verify remain identical.
# ============================================================

mode = ["stock"]

orig_set_seed = draft._set_seed_from_hidden
orig_draft_block = draft.draft_block


def selectable_set_seed(
    self,
    hidden,
    sampler,
    greedy,
):
    if mode[0] != "jury" or not greedy:
        return orig_set_seed(
            hidden,
            sampler,
            greedy,
        )

    self._seed_token = q5_top2_q6_token(
        hidden
    )

    self._seed_hidden = hidden


def selectable_draft_block(
    self,
    last_bonus,
    hidden,
    cache,
    block_size,
    sampler,
    token_dtype=mx.int32,
    greedy=False,
):
    if mode[0] != "jury" or not greedy:
        return orig_draft_block(
            last_bonus,
            hidden,
            cache,
            block_size,
            sampler,
            token_dtype,
            greedy,
        )

    del cache

    if (
        self._input_embed is None
        or self._lm_head_fn is None
    ):
        raise RuntimeError(
            "bind(target_model) must be called before "
            "draft_block()"
        )

    if isinstance(last_bonus, int):
        tok = mx.array(
            [[last_bonus]],
            dtype=token_dtype,
        )
    else:
        tok = last_bonus[:, None].astype(
            token_dtype
        )

    h_prev = hidden
    tokens = []

    self._round_appended = 0

    if (
        self._seed_token is not None
        and self._seed_hidden is not None
    ):
        tok = self._seed_token.astype(
            token_dtype
        )

        h_prev = self._seed_hidden

        tokens.append(tok)

        self._seed_token = None
        self._seed_hidden = None

    while len(tokens) < block_size - 1:
        h_prev = self._forward_token(
            tok,
            h_prev,
            token_dtype,
        )

        self._round_appended += 1

        tok = q5_top2_q6_token(
            h_prev
        )

        tokens.append(tok)

    self._draft_round += 1

    return mx.concatenate(
        tokens,
        axis=1,
    )


draft._set_seed_from_hidden = types.MethodType(
    selectable_set_seed,
    draft,
)

draft.draft_block = types.MethodType(
    selectable_draft_block,
    draft,
)


# ============================================================
# RUNNER
# ============================================================

def run(which, label):
    mode[0] = which

    before_jury = jury_calls[0]

    mx.synchronize()

    result = mlx_vlm.generate(
        model,
        processor,
        PROMPT,
        max_tokens=512,
        temperature=0,
        draft_model=draft,
        draft_kind=kind,
        draft_block_size=4,
        verbose=False,
    )

    mx.synchronize()

    accepts = list(
        draft.accept_lens
    )

    drafts = list(
        draft.draft_lens
    )

    rec = {
        "tps": result.generation_tps,
        "rounds": len(accepts),
        "text": text_hash(result.text),
        "traj": traj_hash(
            accepts,
            drafts,
        ),
        "accepts": accepts,
        "drafts": drafts,
        "jury_calls": (
            jury_calls[0]
            - before_jury
        ),
    }

    print(
        f"{which:8s} "
        f"{str(label):>5s}: "
        f"{rec['tps']:7.3f} tok/s | "
        f"rounds={rec['rounds']:3d} | "
        f"text={rec['text']} | "
        f"traj={rec['traj']} | "
        f"jury={rec['jury_calls']}"
    )

    return rec


# ============================================================
# WARM STOCK REFERENCE
# ============================================================

print()
print("=" * 72)
print("WARM CERTIFIED P38E Q6/G32")
print("=" * 72)

ref = run(
    "stock",
    "WARM",
)

assert ref["rounds"] == EXPECTED_ROUNDS
assert ref["text"] == EXPECTED_TEXT
assert ref["traj"] == EXPECTED_TRAJ


# ============================================================
# LIVE JURY HARD GATE
# ============================================================

print()
print("=" * 72)
print("WARM P41E Q5-TOP2 -> Q6-JURY")
print("=" * 72)

cand = run(
    "jury",
    "WARM",
)

exact = (
    cand["rounds"] == ref["rounds"]
    and cand["text"] == ref["text"]
    and cand["traj"] == ref["traj"]
    and cand["accepts"] == ref["accepts"]
    and cand["drafts"] == ref["drafts"]
)

print()
print("P41E LIVE EXACT:", exact)
print(
    "jury calls:",
    cand["jury_calls"],
)

if not exact:
    print()
    print("P41E HARD GATE: FAIL")
    raise SystemExit(0)

if cand["jury_calls"] != 414:
    print()
    print(
        "WARNING: expected exactly 414 jury calls"
    )


# Second warm jury pass.
trace = run(
    "jury",
    "TRACE",
)

assert trace["rounds"] == EXPECTED_ROUNDS
assert trace["text"] == EXPECTED_TEXT
assert trace["traj"] == EXPECTED_TRAJ
assert trace["accepts"] == ref["accepts"]
assert trace["drafts"] == ref["drafts"]


# ============================================================
# 3-PAIR PERFORMANCE SCOUT
# ============================================================

print()
print("=" * 72)
print("P41E — 3 PAIRED RUNS")
print("=" * 72)

stock_tps = []
jury_tps = []
ratios = []
deltas = []


for pair in range(1, N_PAIRS + 1):

    if pair % 2:
        order = (
            "stock",
            "jury",
        )
    else:
        order = (
            "jury",
            "stock",
        )

    print()
    print(
        f"--------------- PAIR {pair:02d} "
        f"{order[0]} -> {order[1]} ---------------"
    )

    recs = {}

    for which in order:
        rec = run(
            which,
            pair,
        )

        # HARD behavioral certification on EVERY run.
        assert rec["rounds"] == EXPECTED_ROUNDS
        assert rec["text"] == EXPECTED_TEXT
        assert rec["traj"] == EXPECTED_TRAJ
        assert rec["accepts"] == ref["accepts"]
        assert rec["drafts"] == ref["drafts"]

        if which == "jury":
            assert rec["jury_calls"] == 414

        recs[which] = rec

        time.sleep(5)

    a = recs["stock"]["tps"]
    b = recs["jury"]["tps"]

    stock_tps.append(a)
    jury_tps.append(b)

    delta = b - a
    ratio = b / a

    deltas.append(delta)
    ratios.append(ratio)

    print(
        f"PAIR {pair:02d}: "
        f"Q6={a:.3f} | "
        f"JURY={b:.3f} | "
        f"delta={delta:+.3f} tok/s | "
        f"{(ratio-1)*100:+.3f}%"
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 72)
print("SUMMARY")
print("=" * 72)

print(
    "Q6:   ",
    " ".join(
        f"{x:.3f}"
        for x in stock_tps
    ),
)

print(
    "JURY: ",
    " ".join(
        f"{x:.3f}"
        for x in jury_tps
    ),
)

print()

print(
    "Q6 mean:  ",
    f"{statistics.mean(stock_tps):.6f}",
)

print(
    "jury mean:",
    f"{statistics.mean(jury_tps):.6f}",
)

print()

print(
    "paired deltas:",
    " ".join(
        f"{x:+.3f}"
        for x in deltas
    ),
)

print(
    "paired %:    ",
    " ".join(
        f"{(x-1)*100:+.3f}%"
        for x in ratios
    ),
)

print()

print(
    "mean paired speedup:   ",
    f"{(statistics.mean(ratios)-1)*100:+.4f}%",
)

print(
    "median paired speedup: ",
    f"{(statistics.median(ratios)-1)*100:+.4f}%",
)

print(
    "jury pair wins:        ",
    f"{sum(x > 1 for x in ratios)}/{N_PAIRS}",
)

print()
print("BEHAVIORAL CERTIFICATION: PASS")
print()
print("P41E DONE")
