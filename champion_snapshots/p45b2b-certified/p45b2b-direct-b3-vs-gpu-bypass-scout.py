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
N_PAIRS = 3


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
# BUILD P44B3 Q4/G64 + P45B2B GPU BYPASS SEARCH HEADS
# ============================================================

if hasattr(model, "language_model"):
    target_head = model.language_model.lm_head
else:
    target_head = model.lm_head

print()
print(
    "Building P44B3 Q4/G64 + P45B2B GPU BYPASS from:",
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


Q4G64_W, Q4G64_S, Q4G64_B = mx.quantize(
    w_fp16,
    group_size=64,
    bits=4,
    mode="affine",
)

Q4G128_W, Q4G128_S, Q4G128_B = mx.quantize(
    w_fp16,
    group_size=128,
    bits=4,
    mode="affine",
)

mx.eval(
    Q4G64_W,
    Q4G64_S,
    Q4G64_B,
    Q4G128_W,
    Q4G128_S,
    Q4G128_B,
)
mx.synchronize()

del w_fp16
mx.clear_cache()


assert tuple(Q4G64_W.shape) == (248320, 640)
assert tuple(Q4G64_S.shape) == (248320, 80)
assert tuple(Q4G64_B.shape) == (248320, 80)

assert tuple(Q4G128_W.shape) == (248320, 640)
assert tuple(Q4G128_S.shape) == (248320, 40)
assert tuple(Q4G128_B.shape) == (248320, 40)


print(
    "[P44B3] Q4/G64:",
    "weight=", Q4G64_W.shape,
    "scales=", Q4G64_S.shape,
)

print(
    "[P45B2B] GPU BYPASS:",
    "weight=", Q4G128_W.shape,
    "scales=", Q4G128_S.shape,
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
# P43C — G64 TOP4 GEOMETRY
#
# P42R5:
#   groups        = 256
#   TG            = 256
#   TOTAL_THREADS = 65536
#   NCAND         = 1024
#
# P43C:
#   groups        = 64
#   TG            = 256
#   TOTAL_THREADS = 16384
#   NCAND         = 256
#
# Comparator / deterministic top4 semantics unchanged.
# ============================================================

import re as _p43c_re


P43C_TOTAL_THREADS = 16384
P43C_NCAND = 256
P43C_TG = 256


_p43c_total_pat = _p43c_re.compile(
    r"constexpr\s+uint\s+TOTAL_THREADS\s*=\s*\d+\s*;"
)

_p43c_ncand_pat = _p43c_re.compile(
    r"constexpr\s+uint\s+NCAND\s*=\s*\d+\s*;"
)


if not _p43c_total_pat.search(
    P42R5_STAGE1
):
    raise RuntimeError(
        "P43C: TOTAL_THREADS constant not found"
    )


if not _p43c_ncand_pat.search(
    P42R5_STAGE2
):
    raise RuntimeError(
        "P43C: NCAND constant not found"
    )


P43C_STAGE1 = _p43c_total_pat.sub(
    "constexpr uint TOTAL_THREADS = 16384;",
    P42R5_STAGE1,
    count=1,
)


P43C_STAGE2 = _p43c_ncand_pat.sub(
    "constexpr uint NCAND = 256;",
    P42R5_STAGE2,
    count=1,
)


p43c_stage1_kernel = mx.fast.metal_kernel(
    name="m1forge_p43c_top4_stage1_g64",
    input_names=[
        "logits",
    ],
    output_names=[
        "part_vals",
        "part_ids",
    ],
    header=P42R5_HEADER,
    source=P43C_STAGE1,
)


p43c_stage2_kernel = mx.fast.metal_kernel(
    name="m1forge_p43c_top4_stage2_g64",
    input_names=[
        "part_vals",
        "part_ids",
    ],
    output_names=[
        "out_ids",
    ],
    header=P42R5_HEADER,
    source=P43C_STAGE2,
)


def p43c_top4_ids(logits):

    part_vals, part_ids = p43c_stage1_kernel(
        inputs=[
            logits,
        ],
        grid=(
            P43C_TOTAL_THREADS,
            1,
            1,
        ),
        threadgroup=(
            P43C_TG,
            1,
            1,
        ),
        output_shapes=[
            (P43C_NCAND,),
            (P43C_NCAND,),
        ],
        output_dtypes=[
            mx.float32,
            mx.int32,
        ],
    )

    return p43c_stage2_kernel(
        inputs=[
            part_vals,
            part_ids,
        ],
        grid=(
            P43C_TG,
            1,
            1,
        ),
        threadgroup=(
            P43C_TG,
            1,
            1,
        ),
        output_shapes=[
            (4,),
        ],
        output_dtypes=[
            mx.int32,
        ],
    )[0]




# ============================================================
# P45B2B — DETERMINISTIC G64 METAL TOP5
#
# Same geometry as certified P43C:
#   groups        = 64
#   TG            = 256
#   TOTAL_THREADS = 16384
#
# Top8:
#   stage1 = 64 * 8 = 512 candidates
#   stage2 = 512 -> 8
#
# Ordering:
#   higher approximate logit first
#   lower vocabulary ID on exact ties
# ============================================================

P45B2B_HEADER = r"""
struct P44Top5 {
    float v[5];
    uint i[5];
};

inline bool p44_better(
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

inline void p44_insert(
    thread P44Top5& t,
    float v,
    uint i
) {
    for (uint k = 0; k < 5; ++k) {
        if (i == t.i[k]) {
            return;
        }
    }

    for (uint k = 0; k < 5; ++k) {
        if (p44_better(v, i, t.v[k], t.i[k])) {
            for (uint j = 4; j > k; --j) {
                t.v[j] = t.v[j - 1];
                t.i[j] = t.i[j - 1];
            }

            t.v[k] = v;
            t.i[k] = i;
            return;
        }
    }
}
"""


P45B2B_STAGE1 = r"""
constexpr uint N = 248320;
constexpr uint TG = 256;
constexpr uint TOTAL_THREADS = 16384;

uint tid = thread_position_in_threadgroup.x;
uint gid = thread_position_in_grid.x;
uint grp = gid / TG;

P44Top5 local;

for (uint k = 0; k < 5; ++k) {
    local.v[k] = -3.402823466e+38f;
    local.i[k] = 0xffffffffu;
}

for (
    uint i = gid;
    i < N;
    i += TOTAL_THREADS
) {
    p44_insert(
        local,
        float(logits[i]),
        i
    );
}

threadgroup P44Top5 scratch[TG];

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
        P44Top5 cur = scratch[tid];
        P44Top5 rhs = scratch[tid + stride];

        for (uint k = 0; k < 5; ++k) {
            p44_insert(
                cur,
                rhs.v[k],
                rhs.i[k]
            );
        }

        scratch[tid] = cur;
    }

    threadgroup_barrier(
        mem_flags::mem_threadgroup
    );
}

if (tid == 0) {
    uint base = grp * 5;

    for (uint k = 0; k < 5; ++k) {
        part_vals[base + k] = scratch[0].v[k];
        part_ids[base + k] = int(scratch[0].i[k]);
    }
}
"""


P45B2B_STAGE2 = r"""
constexpr uint TG = 256;
constexpr uint NCAND = 320;

uint tid = thread_position_in_threadgroup.x;

P44Top5 local;

for (uint k = 0; k < 5; ++k) {
    local.v[k] = -3.402823466e+38f;
    local.i[k] = 0xffffffffu;
}

for (
    uint i = tid;
    i < NCAND;
    i += TG
) {
    p44_insert(
        local,
        part_vals[i],
        uint(part_ids[i])
    );
}

threadgroup P44Top5 scratch[TG];

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
        P44Top5 cur = scratch[tid];
        P44Top5 rhs = scratch[tid + stride];

        for (uint k = 0; k < 5; ++k) {
            p44_insert(
                cur,
                rhs.v[k],
                rhs.i[k]
            );
        }

        scratch[tid] = cur;
    }

    threadgroup_barrier(
        mem_flags::mem_threadgroup
    );
}

if (tid == 0) {
    for (uint k = 0; k < 5; ++k) {
        out_ids[k] = int(scratch[0].i[k]);
    }
}
"""


p44b4r5_stage1_kernel = mx.fast.metal_kernel(
    name="m1forge_p44b4r5_top5_stage1_g64",
    input_names=[
        "logits",
    ],
    output_names=[
        "part_vals",
        "part_ids",
    ],
    header=P45B2B_HEADER,
    source=P45B2B_STAGE1,
)


p44b4r5_stage2_kernel = mx.fast.metal_kernel(
    name="m1forge_p44b4r5_top5_stage2_g64",
    input_names=[
        "part_vals",
        "part_ids",
    ],
    output_names=[
        "out_ids",
    ],
    header=P45B2B_HEADER,
    source=P45B2B_STAGE2,
)


def p44b4r5_top5_ids(logits):

    part_vals, part_ids = p44b4r5_stage1_kernel(
        inputs=[
            logits,
        ],
        grid=(
            16384,
            1,
            1,
        ),
        threadgroup=(
            256,
            1,
            1,
        ),
        output_shapes=[
            (320,),
            (320,),
        ],
        output_dtypes=[
            mx.float32,
            mx.int32,
        ],
    )

    return p44b4r5_stage2_kernel(
        inputs=[
            part_vals,
            part_ids,
        ],
        grid=(
            256,
            1,
            1,
        ),
        threadgroup=(
            256,
            1,
            1,
        ),
        output_shapes=[
            (5,),
        ],
        output_dtypes=[
            mx.int32,
        ],
    )[0]



# ============================================================
# EXACT TWO-STAGE GREEDY TOKEN SELECTOR
# ============================================================

jury_calls = [0]

# ============================================================
# P45B2B — GPU-RESIDENT CONFIDENCE BYPASS
# ============================================================

_P45_STAGE2_OLD = """if (tid == 0) {
    out_ids[0] = int(scratch[0].i0);
    out_ids[1] = int(scratch[0].i1);
    out_ids[2] = int(scratch[0].i2);
    out_ids[3] = int(scratch[0].i3);
}"""

_P45_STAGE2_NEW = """if (tid == 0) {
    out_ids[0] = int(scratch[0].i0);
    out_ids[1] = int(scratch[0].i1);
    out_ids[2] = int(scratch[0].i2);
    out_ids[3] = int(scratch[0].i3);

    out_vals[0] = scratch[0].v0;
    out_vals[1] = scratch[0].v1;
    out_vals[2] = scratch[0].v2;
    out_vals[3] = scratch[0].v3;
}"""

if P43C_STAGE2.count(
    _P45_STAGE2_OLD
) != 1:
    raise RuntimeError(
        "P45B2B stage2 tail mismatch"
    )

P45B2B_STAGE2 = (
    P43C_STAGE2.replace(
        _P45_STAGE2_OLD,
        _P45_STAGE2_NEW,
        1,
    )
)

p45b2b_stage2_kernel = (
    mx.fast.metal_kernel(
        name=(
            "m1forge_p45b2b_"
            "top4_ids_vals_g64"
        ),
        input_names=[
            "part_vals",
            "part_ids",
        ],
        output_names=[
            "out_ids",
            "out_vals",
        ],
        header=P42R5_HEADER,
        source=P45B2B_STAGE2,
    )
)

def p45b2b_top4_ids_vals(
    logits,
):
    part_vals, part_ids = (
        p43c_stage1_kernel(
            inputs=[
                logits,
            ],
            grid=(
                P43C_TOTAL_THREADS,
                1,
                1,
            ),
            threadgroup=(
                P43C_TG,
                1,
                1,
            ),
            output_shapes=[
                (P43C_NCAND,),
                (P43C_NCAND,),
            ],
            output_dtypes=[
                mx.float32,
                mx.int32,
            ],
        )
    )

    out_ids, out_vals = (
        p45b2b_stage2_kernel(
            inputs=[
                part_vals,
                part_ids,
            ],
            grid=(
                P43C_TG,
                1,
                1,
            ),
            threadgroup=(
                P43C_TG,
                1,
                1,
            ),
            output_shapes=[
                (4,),
                (4,),
            ],
            output_dtypes=[
                mx.int32,
                mx.float32,
            ],
        )
    )

    return (
        out_ids,
        out_vals,
    )

P45B2B_Q6_HEADER = '\ninline float p45_qdot_q6_4(\n    const device uchar* w,\n    const thread float* x_thread,\n    float scale,\n    float bias,\n    float sum\n) {\n    float accum = 0.0f;\n\n    accum +=\n        (w[0] & 0x3f) *\n        x_thread[0];\n\n    accum +=\n        (w[0] & 0xc0) *\n        x_thread[1];\n\n    accum +=\n        (w[1] & 0x0f) *\n        (x_thread[1] * 256.0f);\n\n    accum +=\n        (w[1] & 0xf0) *\n        x_thread[2];\n\n    accum +=\n        (w[2] & 0x03) *\n        (x_thread[2] * 256.0f);\n\n    accum +=\n        (w[2] & 0xfc) *\n        x_thread[3];\n\n    return (\n        scale * accum\n        + sum * bias\n    );\n}\n'

P45B2B_Q6_SOURCE = '\nconstexpr uint K = 5120;\nconstexpr uint NUM_BLOCKS = 40;\nconstexpr uint BLOCK_SIZE = 128;\n\nconstexpr uint ROW_W_BYTES = 3840;\nconstexpr uint GROUPS_PER_ROW = 160;\n\nconstexpr uint BYTES_PER_BLOCK = 96;\nconstexpr uint BYTES_PER_LANE = 3;\n\nconstexpr uint GROUPS_PER_BLOCK = 4;\nconstexpr uint LANES_PER_GROUP = 8;\n\nuint lane =\n    thread_position_in_threadgroup.x;\n\nhalf p45_gap =\n    half(q4_vals[0])\n    - half(q4_vals[1]);\n\nif (\n    p45_gap\n    > half(0.671875f)\n) {\n    if (lane == 0) {\n        chosen[0] = ids[0];\n    }\n\n    return;\n}\n\nconst device uchar* wb =\n    (const device uchar*)q6_w;\n\nuint id0 = uint(ids[0]);\nuint id1 = uint(ids[1]);\nuint id2 = uint(ids[2]);\nuint id3 = uint(ids[3]);\n\nfloat r0 = 0.0f;\nfloat r1 = 0.0f;\nfloat r2 = 0.0f;\nfloat r3 = 0.0f;\n\nfor (\n    uint block = 0;\n    block < NUM_BLOCKS;\n    ++block\n) {\n    uint kbase =\n        block * BLOCK_SIZE\n        + lane * 4;\n\n    float x_thread[4];\n\n    half x0 = h[kbase + 0];\n    half x1 = h[kbase + 1];\n    half x2 = h[kbase + 2];\n    half x3 = h[kbase + 3];\n\n    float sum = 0.0f;\n\n    sum +=\n        x0 + x1 + x2 + x3;\n\n    x_thread[0] = x0;\n    x_thread[1] = x1 / 64.0f;\n    x_thread[2] = x2 / 16.0f;\n    x_thread[3] = x3 / 4.0f;\n\n    uint byte_offset =\n        block * BYTES_PER_BLOCK\n        + lane * BYTES_PER_LANE;\n\n    uint group_offset =\n        block * GROUPS_PER_BLOCK\n        + lane / LANES_PER_GROUP;\n\n    const device uchar* w0 =\n        wb\n        + id0 * ROW_W_BYTES\n        + byte_offset;\n\n    const device uchar* w1 =\n        wb\n        + id1 * ROW_W_BYTES\n        + byte_offset;\n\n    const device uchar* w2 =\n        wb\n        + id2 * ROW_W_BYTES\n        + byte_offset;\n\n    const device uchar* w3 =\n        wb\n        + id3 * ROW_W_BYTES\n        + byte_offset;\n\n    float s0 = float(\n        q6_s[\n            id0 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    float s1 = float(\n        q6_s[\n            id1 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    float s2 = float(\n        q6_s[\n            id2 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    float s3 = float(\n        q6_s[\n            id3 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    float b0 = float(\n        q6_b[\n            id0 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    float b1 = float(\n        q6_b[\n            id1 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    float b2 = float(\n        q6_b[\n            id2 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    float b3 = float(\n        q6_b[\n            id3 * GROUPS_PER_ROW\n            + group_offset\n        ]\n    );\n\n    r0 += p45_qdot_q6_4(\n        w0,\n        x_thread,\n        s0,\n        b0,\n        sum\n    );\n\n    r1 += p45_qdot_q6_4(\n        w1,\n        x_thread,\n        s1,\n        b1,\n        sum\n    );\n\n    r2 += p45_qdot_q6_4(\n        w2,\n        x_thread,\n        s2,\n        b2,\n        sum\n    );\n\n    r3 += p45_qdot_q6_4(\n        w3,\n        x_thread,\n        s3,\n        b3,\n        sum\n    );\n}\n\nr0 = simd_sum(r0);\nr1 = simd_sum(r1);\nr2 = simd_sum(r2);\nr3 = simd_sum(r3);\n\nif (lane == 0) {\n    half s0 = half(r0);\n    half s1 = half(r1);\n    half s2 = half(r2);\n    half s3 = half(r3);\n\n    half best_score = s0;\n    int best_id = ids[0];\n\n    if (\n        (s1 > best_score)\n        || (\n            s1 == best_score\n            && ids[1] < best_id\n        )\n    ) {\n        best_score = s1;\n        best_id = ids[1];\n    }\n\n    if (\n        (s2 > best_score)\n        || (\n            s2 == best_score\n            && ids[2] < best_id\n        )\n    ) {\n        best_score = s2;\n        best_id = ids[2];\n    }\n\n    if (\n        (s3 > best_score)\n        || (\n            s3 == best_score\n            && ids[3] < best_id\n        )\n    ) {\n        best_score = s3;\n        best_id = ids[3];\n    }\n\n    chosen[0] = best_id;\n}\n'

p45b2b_conditional_kernel = (
    mx.fast.metal_kernel(
        name=(
            "m1forge_p45b2b_"
            "conditional_q6g32_x4"
        ),
        input_names=[
            "h",
            "q6_w",
            "q6_s",
            "q6_b",
            "ids",
            "q4_vals",
        ],
        output_names=[
            "chosen",
        ],
        header=P45B2B_Q6_HEADER,
        source=P45B2B_Q6_SOURCE,
    )
)

def p45b2b_gpu_jury(
    h,
    logits5,
):
    ids, vals = (
        p45b2b_top4_ids_vals(
            logits5
        )
    )

    chosen = (
        p45b2b_conditional_kernel(
            inputs=[
                h,
                Q6_W,
                Q6_S,
                Q6_B,
                ids,
                vals,
            ],
            grid=(
                32,
                1,
                1,
            ),
            threadgroup=(
                32,
                1,
                1,
            ),
            output_shapes=[
                (1,),
            ],
            output_dtypes=[
                mx.int32,
            ],
        )[0]
    )

    return chosen.reshape(
        1,
        1,
    )


p45_bypass_calls = [0]
p45_q6_calls = [0]


def q5_logits(h):
    if mode[0] == "p44b3_q4g64":
        w = Q4G64_W
        scales = Q4G64_S
        biases = Q4G64_B
        group_size = 64

    elif mode[0] == "p45b2b_gpu":
        w = Q4G64_W
        scales = Q4G64_S
        biases = Q4G64_B
        group_size = 64

    else:
        raise RuntimeError(
            f"search head called in unsupported mode: {mode[0]}"
        )

    return mx.quantized_matmul(
        h,
        w,
        scales,
        biases,
        transpose=True,
        group_size=group_size,
        bits=4,
        mode="affine",
    )


def q5_top2_q6_token(h):
    jury_calls[0] += 1

    logits5 = q5_logits(h)

    if mode[0] == "p45b2b_gpu":
        return p45b2b_gpu_jury(
            h,
            logits5,
        )

    if mode[0] != "p44b3_q4g64":
        raise RuntimeError(
            "unexpected jury mode: "
            f"{mode[0]}"
        )

    ids = p43c_top4_ids(
        logits5
    ).reshape(
        1,
        1,
        4,
    )

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

    return mx.min(
        tied_ids,
        axis=-1,
    ).reshape(
        1,
        1,
    )




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
    if mode[0] not in ("jury", "p42b", "p42r5", "p43c", "p44b3_q4g64", "p45b2b_gpu") or not greedy:
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
    if mode[0] not in ("jury", "p42b", "p42r5", "p43c", "p44b3_q4g64", "p45b2b_gpu") or not greedy:
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
# P45B2B — DIRECT P44B3 Q4/G64 vs P45B2B GPU BYPASS
# ============================================================

print()
print("=" * 72)
print("WARM CANONICAL STOCK REFERENCE")
print("=" * 72)

ref = run("stock", "WARM")

assert ref["rounds"] == EXPECTED_ROUNDS
assert ref["text"] == EXPECTED_TEXT
assert ref["traj"] == EXPECTED_TRAJ


def assert_exact(rec):
    assert rec["rounds"] == EXPECTED_ROUNDS
    assert rec["text"] == EXPECTED_TEXT
    assert rec["traj"] == EXPECTED_TRAJ
    assert rec["accepts"] == ref["accepts"]
    assert rec["drafts"] == ref["drafts"]
    assert rec["jury_calls"] == 414


print()
print("=" * 72)
print("WARM P44B3 — Q4/G64")
print("=" * 72)

b2_warm = run(
    "p44b3_q4g64",
    "WARM",
)
assert_exact(b2_warm)


print()
print("=" * 72)
print("WARM P45B2B — GPU BYPASS")
print("=" * 72)

b3_warm = run(
    "p45b2b_gpu",
    "WARM",
)
assert_exact(b3_warm)


print()
print("=" * 72)
print("TRACE / POST-JIT")
print("=" * 72)

b2_trace = run(
    "p44b3_q4g64",
    "TRACE",
)
assert_exact(b2_trace)

b3_trace = run(
    "p45b2b_gpu",
    "TRACE",
)
assert_exact(b3_trace)


print()
print("=" * 72)
print("P45B2B — 3 PAIRED RUNS: Q4/G64 vs GPU BYPASS")
print("=" * 72)

b2_tps = []
b3_tps = []

ratios = []
deltas = []


for pair in range(1, N_PAIRS + 1):

    if pair % 2:
        order = (
            "p44b3_q4g64",
            "p45b2b_gpu",
        )
    else:
        order = (
            "p45b2b_gpu",
            "p44b3_q4g64",
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

        assert_exact(rec)

        recs[which] = rec

        time.sleep(5)

    a = recs["p44b3_q4g64"]["tps"]
    b = recs["p45b2b_gpu"]["tps"]

    b2_tps.append(a)
    b3_tps.append(b)

    delta = b - a
    ratio = b / a

    deltas.append(delta)
    ratios.append(ratio)

    print(
        f"PAIR {pair:02d}: "
        f"P44B3={a:.3f} | "
        f"P45B2B={b:.3f} | "
        f"delta={delta:+.3f} tok/s | "
        f"{(ratio - 1) * 100:+.3f}%"
    )


print()
print("=" * 72)
print("P45B2B SUMMARY")
print("=" * 72)

print(
    "P44B3 Q4/G64:",
    " ".join(f"{x:.3f}" for x in b2_tps),
)

print(
    "P45B2B GPU BYPASS:",
    " ".join(f"{x:.3f}" for x in b3_tps),
)

print()

b2_mean = statistics.mean(b2_tps)
b3_mean = statistics.mean(b3_tps)

mean_pct = (
    statistics.mean(ratios) - 1
) * 100

median_pct = (
    statistics.median(ratios) - 1
) * 100

wins = sum(
    x > 1
    for x in ratios
)

print("P44B3 mean:", f"{b2_mean:.6f}")
print("P45B2B mean:", f"{b3_mean:.6f}")

print()

print(
    "paired deltas:",
    " ".join(f"{x:+.3f}" for x in deltas),
)

print(
    "paired %:",
    " ".join(
        f"{(x - 1) * 100:+.3f}%"
        for x in ratios
    ),
)

print()

print(
    "mean paired speedup:",
    f"{mean_pct:+.4f}%",
)

print(
    "median paired speedup:",
    f"{median_pct:+.4f}%",
)

print(
    "P45B2B pair wins:",
    f"{wins}/{N_PAIRS}",
)

print()
print("BEHAVIORAL CERTIFICATION: PASS")

promotion = (
    mean_pct > 0.03
    and median_pct > 0.0
    and wins >= 6
)

print(
    "PROMOTION SPEED GATE:",
    "PASS" if promotion else "FAIL",
)

print()
print(
    "P45B2B GPU policy: "
    "no host-synchronized counters"
)
print("P45B2B DONE")

