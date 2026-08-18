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
# P42C — HIERARCHICAL METAL TOP-2, G=256
# ============================================================

P42_GROUPS = 256
P42_TG = 256
P42_TOTAL_THREADS = 65536
P42_NCAND = 512

P42_HEADER = r"""
struct P42Top2 {
    float v1;
    uint i1;
    float v2;
    uint i2;
};

inline bool p42_better(
    float av,
    uint ai,
    float bv,
    uint bi
) {
    return (
        (av > bv) ||
        ((av == bv) && (ai < bi))
    );
}

inline void p42_insert(
    thread P42Top2& t,
    float v,
    uint i
) {
    if (i == t.i1)
        return;

    if (p42_better(v, i, t.v1, t.i1)) {
        t.v2 = t.v1;
        t.i2 = t.i1;
        t.v1 = v;
        t.i1 = i;
        return;
    }

    if (
        i != t.i1 &&
        p42_better(v, i, t.v2, t.i2)
    ) {
        t.v2 = v;
        t.i2 = i;
    }
}
"""

P42_STAGE1 = r"""
constexpr uint N = 248320;
constexpr uint TG = 256;
constexpr uint TOTAL_THREADS = 65536;

uint tid = thread_position_in_threadgroup.x;
uint gid = thread_position_in_grid.x;
uint grp = gid / TG;

P42Top2 local;
local.v1 = -3.402823466e+38f;
local.i1 = 0xffffffffu;
local.v2 = -3.402823466e+38f;
local.i2 = 0xffffffffu;

for (
    uint i = gid;
    i < N;
    i += TOTAL_THREADS
) {
    p42_insert(
        local,
        float(logits[i]),
        i
    );
}

threadgroup P42Top2 scratch[TG];
scratch[tid] = local;

threadgroup_barrier(
    mem_flags::mem_threadgroup
);

for (
    uint stride = TG >> 1;
    stride > 0;
    stride >>= 1
) {
    if (tid < stride) {
        P42Top2 cur = scratch[tid];
        P42Top2 rhs = scratch[tid + stride];

        p42_insert(cur, rhs.v1, rhs.i1);
        p42_insert(cur, rhs.v2, rhs.i2);

        scratch[tid] = cur;
    }

    threadgroup_barrier(
        mem_flags::mem_threadgroup
    );
}

if (tid == 0) {
    uint base = grp * 2;

    part_vals[base] = scratch[0].v1;
    part_ids[base] = int(scratch[0].i1);

    part_vals[base + 1] = scratch[0].v2;
    part_ids[base + 1] = int(scratch[0].i2);
}
"""

P42_STAGE2 = r"""
constexpr uint TG = 256;
constexpr uint NCAND = 512;

uint tid = thread_position_in_threadgroup.x;

P42Top2 local;
local.v1 = -3.402823466e+38f;
local.i1 = 0xffffffffu;
local.v2 = -3.402823466e+38f;
local.i2 = 0xffffffffu;

for (
    uint i = tid;
    i < NCAND;
    i += TG
) {
    p42_insert(
        local,
        part_vals[i],
        uint(part_ids[i])
    );
}

threadgroup P42Top2 scratch[TG];
scratch[tid] = local;

threadgroup_barrier(
    mem_flags::mem_threadgroup
);

for (
    uint stride = TG >> 1;
    stride > 0;
    stride >>= 1
) {
    if (tid < stride) {
        P42Top2 cur = scratch[tid];
        P42Top2 rhs = scratch[tid + stride];

        p42_insert(cur, rhs.v1, rhs.i1);
        p42_insert(cur, rhs.v2, rhs.i2);

        scratch[tid] = cur;
    }

    threadgroup_barrier(
        mem_flags::mem_threadgroup
    );
}

if (tid == 0) {
    out_ids[0] = int(scratch[0].i1);
    out_ids[1] = int(scratch[0].i2);
}
"""

p42_stage1_kernel = mx.fast.metal_kernel(
    name="m1forge_p42c_stage1_g256",
    input_names=["logits"],
    output_names=[
        "part_vals",
        "part_ids",
    ],
    header=P42_HEADER,
    source=P42_STAGE1,
)

p42_stage2_kernel = mx.fast.metal_kernel(
    name="m1forge_p42c_stage2_g256",
    input_names=[
        "part_vals",
        "part_ids",
    ],
    output_names=["out_ids"],
    header=P42_HEADER,
    source=P42_STAGE2,
)


def p42_top2_ids(logits):
    part_vals, part_ids = p42_stage1_kernel(
        inputs=[logits],
        grid=(65536, 1, 1),
        threadgroup=(256, 1, 1),
        output_shapes=[
            (512,),
            (512,),
        ],
        output_dtypes=[
            mx.float32,
            mx.int32,
        ],
    )

    return p42_stage2_kernel(
        inputs=[
            part_vals,
            part_ids,
        ],
        grid=(256, 1, 1),
        threadgroup=(256, 1, 1),
        output_shapes=[(2,)],
        output_dtypes=[mx.int32],
    )[0]


# ============================================================
# P42R5 ROBUST TOP-4 REDUCER
# ============================================================

P42R5_HEADER = r"""
struct P42Top4 {
    float v0;
    uint  i0;
    float v1;
    uint  i1;
    float v2;
    uint  i2;
    float v3;
    uint  i3;
};

inline bool p42_better(
    float av,
    uint ai,
    float bv,
    uint bi
) {
    return (
        (av > bv) ||
        ((av == bv) && (ai < bi))
    );
}

inline void p42_insert(
    thread P42Top4& t,
    float v,
    uint i
) {
    if (
        i == t.i0 ||
        i == t.i1 ||
        i == t.i2 ||
        i == t.i3
    ) {
        return;
    }

    if (p42_better(v, i, t.v0, t.i0)) {
        t.v3 = t.v2;
        t.i3 = t.i2;

        t.v2 = t.v1;
        t.i2 = t.i1;

        t.v1 = t.v0;
        t.i1 = t.i0;

        t.v0 = v;
        t.i0 = i;
        return;
    }

    if (p42_better(v, i, t.v1, t.i1)) {
        t.v3 = t.v2;
        t.i3 = t.i2;

        t.v2 = t.v1;
        t.i2 = t.i1;

        t.v1 = v;
        t.i1 = i;
        return;
    }

    if (p42_better(v, i, t.v2, t.i2)) {
        t.v3 = t.v2;
        t.i3 = t.i2;

        t.v2 = v;
        t.i2 = i;
        return;
    }

    if (p42_better(v, i, t.v3, t.i3)) {
        t.v3 = v;
        t.i3 = i;
    }
}
"""


P42R5_STAGE1 = r"""
constexpr uint N = 248320;
constexpr uint TG = 256;
constexpr uint TOTAL_THREADS = 65536;

uint tid = thread_position_in_threadgroup.x;
uint gid = thread_position_in_grid.x;
uint grp = gid / TG;

P42Top4 local;

local.v0 = -3.402823466e+38f;
local.i0 = 0xffffffffu;

local.v1 = -3.402823466e+38f;
local.i1 = 0xffffffffu;

local.v2 = -3.402823466e+38f;
local.i2 = 0xffffffffu;

local.v3 = -3.402823466e+38f;
local.i3 = 0xffffffffu;


for (
    uint i = gid;
    i < N;
    i += TOTAL_THREADS
) {
    p42_insert(
        local,
        float(logits[i]),
        i
    );
}


threadgroup P42Top4 scratch[TG];

scratch[tid] = local;

threadgroup_barrier(
    mem_flags::mem_threadgroup
);


for (
    uint stride = TG >> 1;
    stride > 0;
    stride >>= 1
) {
    if (tid < stride) {
        P42Top4 cur = scratch[tid];
        P42Top4 rhs = scratch[tid + stride];

        p42_insert(cur, rhs.v0, rhs.i0);
        p42_insert(cur, rhs.v1, rhs.i1);
        p42_insert(cur, rhs.v2, rhs.i2);
        p42_insert(cur, rhs.v3, rhs.i3);

        scratch[tid] = cur;
    }

    threadgroup_barrier(
        mem_flags::mem_threadgroup
    );
}


if (tid == 0) {
    uint base = grp * 4;

    part_vals[base + 0] = scratch[0].v0;
    part_ids [base + 0] = int(scratch[0].i0);

    part_vals[base + 1] = scratch[0].v1;
    part_ids [base + 1] = int(scratch[0].i1);

    part_vals[base + 2] = scratch[0].v2;
    part_ids [base + 2] = int(scratch[0].i2);

    part_vals[base + 3] = scratch[0].v3;
    part_ids [base + 3] = int(scratch[0].i3);
}
"""


P42R5_STAGE2 = r"""
constexpr uint TG = 256;
constexpr uint NCAND = 1024;

uint tid = thread_position_in_threadgroup.x;

P42Top4 local;

local.v0 = -3.402823466e+38f;
local.i0 = 0xffffffffu;

local.v1 = -3.402823466e+38f;
local.i1 = 0xffffffffu;

local.v2 = -3.402823466e+38f;
local.i2 = 0xffffffffu;

local.v3 = -3.402823466e+38f;
local.i3 = 0xffffffffu;


for (
    uint i = tid;
    i < NCAND;
    i += TG
) {
    p42_insert(
        local,
        part_vals[i],
        uint(part_ids[i])
    );
}


threadgroup P42Top4 scratch[TG];

scratch[tid] = local;

threadgroup_barrier(
    mem_flags::mem_threadgroup
);


for (
    uint stride = TG >> 1;
    stride > 0;
    stride >>= 1
) {
    if (tid < stride) {
        P42Top4 cur = scratch[tid];
        P42Top4 rhs = scratch[tid + stride];

        p42_insert(cur, rhs.v0, rhs.i0);
        p42_insert(cur, rhs.v1, rhs.i1);
        p42_insert(cur, rhs.v2, rhs.i2);
        p42_insert(cur, rhs.v3, rhs.i3);

        scratch[tid] = cur;
    }

    threadgroup_barrier(
        mem_flags::mem_threadgroup
    );
}


if (tid == 0) {
    out_ids[0] = int(scratch[0].i0);
    out_ids[1] = int(scratch[0].i1);
    out_ids[2] = int(scratch[0].i2);
    out_ids[3] = int(scratch[0].i3);
}
"""


p42r5_stage1_kernel = mx.fast.metal_kernel(
    name="m1forge_p42r5_top4_stage1",
    input_names=["logits"],
    output_names=[
        "part_vals",
        "part_ids",
    ],
    header=P42R5_HEADER,
    source=P42R5_STAGE1,
)

p42r5_stage2_kernel = mx.fast.metal_kernel(
    name="m1forge_p42r5_top4_stage2",
    input_names=[
        "part_vals",
        "part_ids",
    ],
    output_names=["out_ids"],
    header=P42R5_HEADER,
    source=P42R5_STAGE2,
)


def p42_top4_ids(logits):
    vals, ids = p42r5_stage1_kernel(
        inputs=[logits],
        grid=(65536, 1, 1),
        threadgroup=(256, 1, 1),
        output_shapes=[
            (1024,),
            (1024,),
        ],
        output_dtypes=[
            mx.float32,
            mx.int32,
        ],
    )

    return p42r5_stage2_kernel(
        inputs=[
            vals,
            ids,
        ],
        grid=(256, 1, 1),
        threadgroup=(256, 1, 1),
        output_shapes=[
            (4,),
        ],
        output_dtypes=[
            mx.int32,
        ],
    )[0]




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
    # Q5/G32 full-vocab search.
    #
    # p42b:
    #   original certified P42C top2 behavior.
    #
    # p42r5:
    #   robust deterministic Metal top4.
    # --------------------------------------------------------

    logits5 = q5_logits(h)

    if mode[0] == "p42r5":
        ids = p42_top4_ids(
            logits5
        ).reshape(1, 1, 4)

    elif mode[0] == "p42b":
        ids = p42_top2_ids(
            logits5
        ).reshape(1, 1, 2)

    else:
        part = mx.argpartition(
            logits5,
            VOCAB - 2,
            axis=-1,
        )

        ids = part[..., -2:]

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

    # --------------------------------------------------------
    # Robust P42R5 tie semantics:
    #
    # full-vocab mx.argmax picks the lowest vocabulary ID
    # when multiple tokens have exactly equal max scores.
    # --------------------------------------------------------

    if mode[0] == "p42r5":

        max_score = mx.max(
            scores6,
            axis=-1,
            keepdims=True,
        )

        sentinel = mx.array(
            VOCAB,
            dtype=mx.int32,
        )

        tied_ids = mx.where(
            scores6 == max_score,
            ids,
            sentinel,
        )

        chosen = mx.min(
            tied_ids,
            axis=-1,
        )

        return chosen

    # Original P42C / P41E behavior stays untouched.
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
    if mode[0] not in ("jury", "p42b", "p42r5") or not greedy:
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
    if mode[0] not in ("jury", "p42b", "p42r5") or not greedy:
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
# WARM P38E CANONICAL REFERENCE
# ============================================================

print()
print("=" * 72)
print("WARM P38E CANONICAL REFERENCE")
print("=" * 72)

ref = run(
    "stock",
    "WARM",
)

assert ref["rounds"] == EXPECTED_ROUNDS
assert ref["text"] == EXPECTED_TEXT
assert ref["traj"] == EXPECTED_TRAJ


# ============================================================
# WARM P42C GENERIC JURY
# ============================================================

print()
print("=" * 72)
print("WARM P42C GENERIC JURY")
print("=" * 72)

p41_warm = run(
    "p42b",
    "WARM",
)

assert p41_warm["rounds"] == EXPECTED_ROUNDS
assert p41_warm["text"] == EXPECTED_TEXT
assert p41_warm["traj"] == EXPECTED_TRAJ
assert p41_warm["accepts"] == ref["accepts"]
assert p41_warm["drafts"] == ref["drafts"]
assert p41_warm["jury_calls"] == 414


# ============================================================
# WARM P42R5 / P42C METAL JURY
# ============================================================

print()
print("=" * 72)
print("WARM P42R5 HIERARCHICAL METAL JURY")
print("=" * 72)

p42_warm = run(
    "p42r5",
    "WARM",
)

exact = (
    p42_warm["rounds"] == ref["rounds"]
    and p42_warm["text"] == ref["text"]
    and p42_warm["traj"] == ref["traj"]
    and p42_warm["accepts"] == ref["accepts"]
    and p42_warm["drafts"] == ref["drafts"]
)

print()
print("P42R5 LIVE EXACT:", exact)
print("jury calls:", p42_warm["jury_calls"])

if not exact:
    print()
    print("P42C HARD GATE: FAIL")
    raise SystemExit(0)

assert p42_warm["jury_calls"] == 414


# Second pass after Metal JIT.
p42_trace = run(
    "p42r5",
    "TRACE",
)

assert p42_trace["rounds"] == EXPECTED_ROUNDS
assert p42_trace["text"] == EXPECTED_TEXT
assert p42_trace["traj"] == EXPECTED_TRAJ
assert p42_trace["accepts"] == ref["accepts"]
assert p42_trace["drafts"] == ref["drafts"]
assert p42_trace["jury_calls"] == 414


# ============================================================
# 3-PAIR P42C vs P42R5
# ============================================================

print()
print("=" * 72)
print("P42R5 — 10 PAIRED RUNS: P42C vs P42R5")
print("=" * 72)

p41_tps = []
p42_tps = []

ratios = []
deltas = []


for pair in range(1, N_PAIRS + 1):

    if pair % 2:
        order = (
            "p42b",
            "p42r5",
        )
    else:
        order = (
            "p42r5",
            "p42b",
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

        assert rec["rounds"] == EXPECTED_ROUNDS
        assert rec["text"] == EXPECTED_TEXT
        assert rec["traj"] == EXPECTED_TRAJ
        assert rec["accepts"] == ref["accepts"]
        assert rec["drafts"] == ref["drafts"]
        assert rec["jury_calls"] == 414

        recs[which] = rec

        time.sleep(5)

    a = recs["p42b"]["tps"]
    b = recs["p42r5"]["tps"]

    p41_tps.append(a)
    p42_tps.append(b)

    delta = b - a
    ratio = b / a

    deltas.append(delta)
    ratios.append(ratio)

    print(
        f"PAIR {pair:02d}: "
        f"P42C={a:.3f} | "
        f"P42R5={b:.3f} | "
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
    "P42C:",
    " ".join(
        f"{x:.3f}"
        for x in p41_tps
    ),
)

print(
    "P42R5:",
    " ".join(
        f"{x:.3f}"
        for x in p42_tps
    ),
)

print()

print(
    "P42C mean:",
    f"{statistics.mean(p41_tps):.6f}",
)

print(
    "P42R5 mean:",
    f"{statistics.mean(p42_tps):.6f}",
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
    "paired %:",
    " ".join(
        f"{(x-1)*100:+.3f}%"
        for x in ratios
    ),
)

print()

print(
    "mean paired speedup:",
    f"{(statistics.mean(ratios)-1)*100:+.4f}%",
)

print(
    "median paired speedup:",
    f"{(statistics.median(ratios)-1)*100:+.4f}%",
)

print(
    "P42R5 pair wins:",
    f"{sum(x > 1 for x in ratios)}/{N_PAIRS}",
)

print()
print("BEHAVIORAL CERTIFICATION: PASS")
print()
print("P42R5 DONE")
