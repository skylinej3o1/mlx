import os
import gc
import json
import hashlib
from collections import Counter

# ------------------------------------------------------------
# Long-context robustness test:
# deliberately disable P36 fixed-cap verifier machinery.
# We're testing Q5->Q6 shortlist robustness, not verifier TPS.
# ------------------------------------------------------------

for k in (
    "M1FORGE_COMPILED_VERIFY",
    "M1FORGE_VERIFY_M4_ATTN",
    "M1FORGE_VERIFY_M4_VARIANT",
    "MLX_QMV_FAST_M4",
    "MLX_QMV_FAST_M3",
):
    os.environ.pop(k, None)

# Keep certified P38E draft head as generation/reference path.
os.environ["M1FORGE_MTP_DRAFT_HEAD"] = "q6_g32"
os.environ["M1FORGE_MTP_DRAFT_HEAD_DEBUG"] = "0"

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

VOCAB = 248320
GEN_TOKENS = 128

CONTEXT_TARGETS = [64, 256, 1024, 4096, 8192, 16384]

PROMPT_KINDS = [
    "code",
    "reasoning",
    "prose",
    "structured",
    "dialogue",
]


def short_hash(s):
    return hashlib.sha256(
        s.encode("utf-8")
    ).hexdigest()[:12]


print("Loading target...")
model, processor = mlx_vlm.load(TARGET)

print("Loading MTP drafter...")
draft, kind = load_drafter(
    DRAFT,
    kind="mtp",
)

mx.eval(model.parameters())
mx.eval(draft.parameters())
mx.synchronize()


# ============================================================
# TOKENIZER HELPERS
# ============================================================

tokenizer = getattr(
    processor,
    "tokenizer",
    processor,
)


def encode(s):
    try:
        return tokenizer.encode(
            s,
            add_special_tokens=False,
        )
    except TypeError:
        return tokenizer.encode(s)


def decode(ids):
    try:
        return tokenizer.decode(
            ids,
            skip_special_tokens=False,
        )
    except TypeError:
        return tokenizer.decode(ids)


# ============================================================
# PROMPT CORPUS
# ============================================================

PREFIX = "<|im_start|>user\n"

SUFFIX = (
    "\n<|im_end|>\n"
    "<|im_start|>assistant\n"
    "<think>\n\n</think>\n\n"
)


def filler_unit(kind, i):
    if kind == "code":
        return (
            f"\n# module section {i}\n"
            f"def transform_{i}(records, limit={17 + (i % 23)}):\n"
            f"    \"\"\"Normalize batch {i} while preserving stable ordering.\"\"\"\n"
            f"    result = []\n"
            f"    for index, item in enumerate(records):\n"
            f"        if index % {2 + (i % 5)} == 0:\n"
            f"            result.append((index, item))\n"
            f"    return result[:limit]\n"
        )

    if kind == "reasoning":
        return (
            f"\nConstraint set {i}: "
            f"worker A{i%11} starts before B{i%13}; "
            f"B{i%13} cannot share a slot with C{i%17}; "
            f"machine M{i%7} has capacity {20 + (i % 31)}; "
            f"job J{i%19} consumes {2 + (i % 9)} units; "
            f"if condition X{i%5} holds, J{i%19} must precede "
            f"J{(i+3)%19}. Record this without resolving it yet.\n"
        )

    if kind == "prose":
        return (
            f"\nSection {i}. "
            f"The survey team returned to station {i%29} after sunrise. "
            f"Measurements from channel {i%13} differed slightly from the "
            f"previous observation, while the surrounding terrain remained "
            f"stable. The researchers logged temperature series {1000+i}, "
            f"checked the instruments, compared notes, and continued along "
            f"the ridge before documenting the next sample.\n"
        )

    if kind == "structured":
        return (
            f'\n{{"event_id": {100000+i}, '
            f'"service": "svc-{i%23}", '
            f'"region": "zone-{i%9}", '
            f'"latency_ms": {11 + (i*7)%311}, '
            f'"attempt": {1+i%4}, '
            f'"status": "{["ok","retry","queued","ok"][i%4]}", '
            f'"tags": ["batch-{i%17}", "node-{i%31}"]}}\n'
        )

    if kind == "dialogue":
        return (
            f"\nSpeaker A: For item {i}, did you keep the original ordering?\n"
            f"Speaker B: Yes, except record {i%37} was deferred until the "
            f"dependency completed.\n"
            f"Speaker A: And the reason code?\n"
            f"Speaker B: R-{100 + i%53}; the underlying value was "
            f"{7000 + i*3}.\n"
        )

    raise ValueError(kind)


TASKS = {
    "code": (
        "\nUsing the preceding material as context, write a concise Python "
        "implementation of an LRU cache with a dictionary and doubly linked "
        "list. Include type hints and explain two edge cases."
    ),

    "reasoning": (
        "\nNow solve the following carefully: identify a consistent ordering "
        "strategy for the constraints above, explain how you would detect a "
        "cycle, and state what information remains insufficient."
    ),

    "prose": (
        "\nSummarize the important recurring observations above and explain "
        "which conclusions are directly supported versus speculative."
    ),

    "structured": (
        "\nAnalyze the records above. Describe likely retry patterns, give a "
        "robust aggregation strategy, and sketch Python code that would find "
        "the highest-latency services."
    ),

    "dialogue": (
        "\nSummarize the operational issues in the transcript, separating "
        "confirmed facts from assumptions, and propose a short follow-up plan."
    ),
}


def build_prompt(kind, target_tokens):
    # Produce more filler than the largest context needs.
    chunks = []

    for i in range(3000):
        chunks.append(
            filler_unit(kind, i)
        )

    filler_ids = encode(
        "".join(chunks)
    )

    prefix_ids = encode(PREFIX)
    suffix_ids = encode(SUFFIX)
    task_ids = encode(TASKS[kind])

    budget = (
        target_tokens
        - len(prefix_ids)
        - len(suffix_ids)
        - len(task_ids)
    )

    if budget < 0:
        budget = 0

    chosen_filler = decode(
        filler_ids[:budget]
    )

    prompt = (
        PREFIX
        + chosen_filler
        + TASKS[kind]
        + SUFFIX
    )

    actual = len(
        encode(prompt)
    )

    return prompt, actual


# ============================================================
# FORCE/CAPTURE CERTIFIED Q6/G32 HEAD
# ============================================================

draft.bind(model)

q6_head = draft._lm_head_fn

cells = dict(
    zip(
        q6_head.__code__.co_freevars,
        [
            c.cell_contents
            for c in q6_head.__closure__
        ],
    )
)

Q6_W = cells["q6_w"]
Q6_S = cells["q6_s"]
Q6_B = cells["q6_b"]

print()
print("Certified Q6/G32:")
print("  W:", Q6_W.shape)
print("  S:", Q6_S.shape)
print("  B:", Q6_B.shape)


def q6_logits(h):
    return mx.quantized_matmul(
        h,
        Q6_W,
        Q6_S,
        Q6_B,
        transpose=True,
        group_size=32,
        bits=6,
        mode="affine",
    )


# ============================================================
# BUILD Q4/G64 SEARCH HEAD
# ============================================================

if hasattr(model, "language_model"):
    target_head = model.language_model.lm_head
else:
    target_head = model.lm_head

print()
print("Building Q4/G64 search head...")

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
    group_size=64,
    bits=4,
    mode="affine",
)

mx.eval(
    Q5_W,
    Q5_S,
    Q5_B,
)
mx.synchronize()

del w_fp16

print(
    "Q4 ready:",
    Q5_W.shape,
    Q5_S.shape,
)


def q5_logits(h):
    return mx.quantized_matmul(
        h,
        Q5_W,
        Q5_S,
        Q5_B,
        transpose=True,
        group_size=64,
        bits=4,
        mode="affine",
    )


VOCAB_IDS = mx.arange(
    VOCAB,
    dtype=mx.int32,
)

mx.eval(VOCAB_IDS)


# ============================================================
# ACTUAL CERTIFIED P42C HIERARCHICAL TOP-2
# ============================================================

P42_HEADER = r"""
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


P42_STAGE1 = r"""
constexpr uint N = 248320;
constexpr uint TG = 256;
constexpr uint TOTAL_THREADS = 16384;

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


P42_STAGE2 = r"""
constexpr uint TG = 256;
constexpr uint NCAND = 256;

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


stage1 = mx.fast.metal_kernel(
    name="m1forge_p43c_top4_stage1_g64",
    input_names=["logits"],
    output_names=[
        "part_vals",
        "part_ids",
    ],
    header=P42_HEADER,
    source=P42_STAGE1,
)

stage2 = mx.fast.metal_kernel(
    name="m1forge_p43c_top4_stage2_g64",
    input_names=[
        "part_vals",
        "part_ids",
    ],
    output_names=["out_ids"],
    header=P42_HEADER,
    source=P42_STAGE2,
)


def p42_top4_ids(logits):
    vals, ids = stage1(
        inputs=[logits],
        grid=(16384, 1, 1),
        threadgroup=(256, 1, 1),
        output_shapes=[
            (256,),
            (256,),
        ],
        output_dtypes=[
            mx.float32,
            mx.int32,
        ],
    )

    return stage2(
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
# P44B4R5 — DETERMINISTIC G64 METAL TOP5
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

P44B4R5_HEADER = r"""
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


P44B4R5_STAGE1 = r"""
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


P44B4R5_STAGE2 = r"""
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
    header=P44B4R5_HEADER,
    source=P44B4R5_STAGE1,
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
    header=P44B4R5_HEADER,
    source=P44B4R5_STAGE2,
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


def p42_jury_from_logits(
    h,
    logits5,
):
    ids = p42_top4_ids(
        logits5
    ).reshape(-1)

    wk = Q6_W[ids]
    sk = Q6_S[ids]
    bk = Q6_B[ids]

    scores = mx.quantized_matmul(
        h,
        wk,
        sk,
        bk,
        transpose=True,
        group_size=32,
        bits=6,
        mode="affine",
    )

    # Match full-vocabulary mx.argmax behavior:
    # highest Q6 score, then lowest vocab ID on exact ties.
    max_score = mx.max(
        scores,
        axis=-1,
        keepdims=True,
    )

    id_grid = ids.reshape(
        1,
        1,
        -1,
    )

    sentinel = mx.array(
        VOCAB,
        dtype=mx.int32,
    )

    tied_ids = mx.where(
        scores == max_score,
        id_grid,
        sentinel,
    )

    chosen = mx.min(
        tied_ids,
        axis=-1,
    )

    return chosen.reshape(
        1,
        1,
    )



# ============================================================
# P45B2A — SPECIALIZED Q6/G32 x4 METAL JURY
#
# Parity-only. No confidence bypass yet.
#
# Specialization of MLX small-N affine Q6/G32 qmv:
#   K                  = 5120
#   values/thread      = 4
#   SIMD lanes         = 32
#   block size         = 128
#   blocks             = 40
#   packed row bytes   = 3840
#   groups/row         = 160
# ============================================================

P45_Q6X4_HEADER = r"""
inline float p45_qdot_q6_4(
    const device uchar* w,
    const thread float* x_thread,
    float scale,
    float bias,
    float sum
) {
    float accum = 0.0f;

    accum +=
        (w[0] & 0x3f) *
        x_thread[0];

    accum +=
        (w[0] & 0xc0) *
        x_thread[1];

    accum +=
        (w[1] & 0x0f) *
        (x_thread[1] * 256.0f);

    accum +=
        (w[1] & 0xf0) *
        x_thread[2];

    accum +=
        (w[2] & 0x03) *
        (x_thread[2] * 256.0f);

    accum +=
        (w[2] & 0xfc) *
        x_thread[3];

    return (
        scale * accum
        + sum * bias
    );
}
"""

P45_Q6X4_SOURCE = r"""
constexpr uint K = 5120;
constexpr uint NUM_BLOCKS = 40;
constexpr uint BLOCK_SIZE = 128;

constexpr uint ROW_W_BYTES = 3840;
constexpr uint GROUPS_PER_ROW = 160;

constexpr uint BYTES_PER_BLOCK = 96;
constexpr uint BYTES_PER_LANE = 3;

constexpr uint GROUPS_PER_BLOCK = 4;
constexpr uint LANES_PER_GROUP = 8;

uint lane =
    thread_position_in_threadgroup.x;

const device uchar* wb =
    (const device uchar*)q6_w;

uint id0 = uint(ids[0]);
uint id1 = uint(ids[1]);
uint id2 = uint(ids[2]);
uint id3 = uint(ids[3]);

float r0 = 0.0f;
float r1 = 0.0f;
float r2 = 0.0f;
float r3 = 0.0f;

for (
    uint block = 0;
    block < NUM_BLOCKS;
    ++block
) {
    uint kbase =
        block * BLOCK_SIZE
        + lane * 4;

    float x_thread[4];

    half x0 = h[kbase + 0];
    half x1 = h[kbase + 1];
    half x2 = h[kbase + 2];
    half x3 = h[kbase + 3];

    float sum = 0.0f;

    sum +=
        x0 + x1 + x2 + x3;

    x_thread[0] = x0;
    x_thread[1] = x1 / 64.0f;
    x_thread[2] = x2 / 16.0f;
    x_thread[3] = x3 / 4.0f;

    uint byte_offset =
        block * BYTES_PER_BLOCK
        + lane * BYTES_PER_LANE;

    uint group_offset =
        block * GROUPS_PER_BLOCK
        + lane / LANES_PER_GROUP;

    const device uchar* w0 =
        wb
        + id0 * ROW_W_BYTES
        + byte_offset;

    const device uchar* w1 =
        wb
        + id1 * ROW_W_BYTES
        + byte_offset;

    const device uchar* w2 =
        wb
        + id2 * ROW_W_BYTES
        + byte_offset;

    const device uchar* w3 =
        wb
        + id3 * ROW_W_BYTES
        + byte_offset;

    float s0 = float(
        q6_s[
            id0 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    float s1 = float(
        q6_s[
            id1 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    float s2 = float(
        q6_s[
            id2 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    float s3 = float(
        q6_s[
            id3 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    float b0 = float(
        q6_b[
            id0 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    float b1 = float(
        q6_b[
            id1 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    float b2 = float(
        q6_b[
            id2 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    float b3 = float(
        q6_b[
            id3 * GROUPS_PER_ROW
            + group_offset
        ]
    );

    r0 += p45_qdot_q6_4(
        w0,
        x_thread,
        s0,
        b0,
        sum
    );

    r1 += p45_qdot_q6_4(
        w1,
        x_thread,
        s1,
        b1,
        sum
    );

    r2 += p45_qdot_q6_4(
        w2,
        x_thread,
        s2,
        b2,
        sum
    );

    r3 += p45_qdot_q6_4(
        w3,
        x_thread,
        s3,
        b3,
        sum
    );
}

r0 = simd_sum(r0);
r1 = simd_sum(r1);
r2 = simd_sum(r2);
r3 = simd_sum(r3);

if (lane == 0) {
    scores[0] = half(r0);
    scores[1] = half(r1);
    scores[2] = half(r2);
    scores[3] = half(r3);
}
"""

p45_q6x4_kernel = mx.fast.metal_kernel(
    name="m1forge_p45_q6g32_x4_half_sum",
    input_names=[
        "h",
        "q6_w",
        "q6_s",
        "q6_b",
        "ids",
    ],
    output_names=[
        "scores",
    ],
    header=P45_Q6X4_HEADER,
    source=P45_Q6X4_SOURCE,
)


def p45_q6x4_scores(
    h,
    ids,
):
    ids = ids.reshape(-1)

    return p45_q6x4_kernel(
        inputs=[
            h,
            Q6_W,
            Q6_S,
            Q6_B,
            ids,
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
            (1, 1, 4),
        ],
        output_dtypes=[
            mx.float16,
        ],
    )[0]


def p45_ref_q6x4_scores(
    h,
    ids,
):
    ids = ids.reshape(-1)

    return mx.quantized_matmul(
        h,
        Q6_W[ids],
        Q6_S[ids],
        Q6_B[ids],
        transpose=True,
        group_size=32,
        bits=6,
        mode="affine",
    )


def p45_choose_from_scores(
    ids,
    scores,
):
    ids = ids.reshape(
        1,
        1,
        4,
    )

    max_score = mx.max(
        scores,
        axis=-1,
        keepdims=True,
    )

    sentinel = mx.array(
        VOCAB,
        dtype=mx.int32,
    )

    tied_ids = mx.where(
        scores == max_score,
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


p45_stats = {
    "calls": 0,
    "token_matches": 0,
    "fp16_exact_calls": 0,
    "max_abs_score_error": 0.0,
}

p45_mismatches = []


# ============================================================
# P45B2B — SELF-CONTAINED P43C IDS+VALS REDUCER
# ============================================================

P45B2B_TOP4_HEADER = '\nstruct P42Top4 {\n    float v0;\n    uint  i0;\n    float v1;\n    uint  i1;\n    float v2;\n    uint  i2;\n    float v3;\n    uint  i3;\n};\n\ninline bool p42_better(\n    float av,\n    uint ai,\n    float bv,\n    uint bi\n) {\n    return (\n        (av > bv) ||\n        ((av == bv) && (ai < bi))\n    );\n}\n\ninline void p42_insert(\n    thread P42Top4& t,\n    float v,\n    uint i\n) {\n    if (\n        i == t.i0 ||\n        i == t.i1 ||\n        i == t.i2 ||\n        i == t.i3\n    ) {\n        return;\n    }\n\n    if (p42_better(v, i, t.v0, t.i0)) {\n        t.v3 = t.v2;\n        t.i3 = t.i2;\n\n        t.v2 = t.v1;\n        t.i2 = t.i1;\n\n        t.v1 = t.v0;\n        t.i1 = t.i0;\n\n        t.v0 = v;\n        t.i0 = i;\n        return;\n    }\n\n    if (p42_better(v, i, t.v1, t.i1)) {\n        t.v3 = t.v2;\n        t.i3 = t.i2;\n\n        t.v2 = t.v1;\n        t.i2 = t.i1;\n\n        t.v1 = v;\n        t.i1 = i;\n        return;\n    }\n\n    if (p42_better(v, i, t.v2, t.i2)) {\n        t.v3 = t.v2;\n        t.i3 = t.i2;\n\n        t.v2 = v;\n        t.i2 = i;\n        return;\n    }\n\n    if (p42_better(v, i, t.v3, t.i3)) {\n        t.v3 = v;\n        t.i3 = i;\n    }\n}\n'

P45B2B_STAGE1 = '\nconstexpr uint N = 248320;\nconstexpr uint TG = 256;\nconstexpr uint TOTAL_THREADS = 16384;\n\nuint tid = thread_position_in_threadgroup.x;\nuint gid = thread_position_in_grid.x;\nuint grp = gid / TG;\n\nP42Top4 local;\n\nlocal.v0 = -3.402823466e+38f;\nlocal.i0 = 0xffffffffu;\n\nlocal.v1 = -3.402823466e+38f;\nlocal.i1 = 0xffffffffu;\n\nlocal.v2 = -3.402823466e+38f;\nlocal.i2 = 0xffffffffu;\n\nlocal.v3 = -3.402823466e+38f;\nlocal.i3 = 0xffffffffu;\n\n\nfor (\n    uint i = gid;\n    i < N;\n    i += TOTAL_THREADS\n) {\n    p42_insert(\n        local,\n        float(logits[i]),\n        i\n    );\n}\n\n\nthreadgroup P42Top4 scratch[TG];\n\nscratch[tid] = local;\n\nthreadgroup_barrier(\n    mem_flags::mem_threadgroup\n);\n\n\nfor (\n    uint stride = TG >> 1;\n    stride > 0;\n    stride >>= 1\n) {\n    if (tid < stride) {\n        P42Top4 cur = scratch[tid];\n        P42Top4 rhs = scratch[tid + stride];\n\n        p42_insert(cur, rhs.v0, rhs.i0);\n        p42_insert(cur, rhs.v1, rhs.i1);\n        p42_insert(cur, rhs.v2, rhs.i2);\n        p42_insert(cur, rhs.v3, rhs.i3);\n\n        scratch[tid] = cur;\n    }\n\n    threadgroup_barrier(\n        mem_flags::mem_threadgroup\n    );\n}\n\n\nif (tid == 0) {\n    uint base = grp * 4;\n\n    part_vals[base + 0] = scratch[0].v0;\n    part_ids [base + 0] = int(scratch[0].i0);\n\n    part_vals[base + 1] = scratch[0].v1;\n    part_ids [base + 1] = int(scratch[0].i1);\n\n    part_vals[base + 2] = scratch[0].v2;\n    part_ids [base + 2] = int(scratch[0].i2);\n\n    part_vals[base + 3] = scratch[0].v3;\n    part_ids [base + 3] = int(scratch[0].i3);\n}\n'

P45B2B_STAGE2 = '\nconstexpr uint TG = 256;\nconstexpr uint NCAND = 256;\n\nuint tid = thread_position_in_threadgroup.x;\n\nP42Top4 local;\n\nlocal.v0 = -3.402823466e+38f;\nlocal.i0 = 0xffffffffu;\n\nlocal.v1 = -3.402823466e+38f;\nlocal.i1 = 0xffffffffu;\n\nlocal.v2 = -3.402823466e+38f;\nlocal.i2 = 0xffffffffu;\n\nlocal.v3 = -3.402823466e+38f;\nlocal.i3 = 0xffffffffu;\n\n\nfor (\n    uint i = tid;\n    i < NCAND;\n    i += TG\n) {\n    p42_insert(\n        local,\n        part_vals[i],\n        uint(part_ids[i])\n    );\n}\n\n\nthreadgroup P42Top4 scratch[TG];\n\nscratch[tid] = local;\n\nthreadgroup_barrier(\n    mem_flags::mem_threadgroup\n);\n\n\nfor (\n    uint stride = TG >> 1;\n    stride > 0;\n    stride >>= 1\n) {\n    if (tid < stride) {\n        P42Top4 cur = scratch[tid];\n        P42Top4 rhs = scratch[tid + stride];\n\n        p42_insert(cur, rhs.v0, rhs.i0);\n        p42_insert(cur, rhs.v1, rhs.i1);\n        p42_insert(cur, rhs.v2, rhs.i2);\n        p42_insert(cur, rhs.v3, rhs.i3);\n\n        scratch[tid] = cur;\n    }\n\n    threadgroup_barrier(\n        mem_flags::mem_threadgroup\n    );\n}\n\n\nif (tid == 0) {\n    out_ids[0] = int(scratch[0].i0);\n    out_ids[1] = int(scratch[0].i1);\n    out_ids[2] = int(scratch[0].i2);\n    out_ids[3] = int(scratch[0].i3);\n\n    out_vals[0] = scratch[0].v0;\n    out_vals[1] = scratch[0].v1;\n    out_vals[2] = scratch[0].v2;\n    out_vals[3] = scratch[0].v3;\n}\n'


p45b2b_stage1_kernel = mx.fast.metal_kernel(
    name=(
        "m1forge_p45b2b_"
        "stage1_g64_robust"
    ),
    input_names=[
        "logits",
    ],
    output_names=[
        "part_vals",
        "part_ids",
    ],
    header=P45B2B_TOP4_HEADER,
    source=P45B2B_STAGE1,
)


p45b2b_stage2_kernel = mx.fast.metal_kernel(
    name=(
        "m1forge_p45b2b_"
        "stage2_ids_vals_g64_robust"
    ),
    input_names=[
        "part_vals",
        "part_ids",
    ],
    output_names=[
        "out_ids",
        "out_vals",
    ],
    header=P45B2B_TOP4_HEADER,
    source=P45B2B_STAGE2,
)


def p45b2b_top4_ids_vals(
    logits,
):
    part_vals, part_ids = (
        p45b2b_stage1_kernel(
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
                (256,),
                (256,),
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




p45b2b_policy_stats = {
    "calls": 0,
    "matches": 0,
}

p45b2b_policy_mismatches = []


# JIT once.
dummy = mx.zeros(
    (1, 1, VOCAB),
    dtype=mx.float16,
)

jit_ids = p42_top4_ids(dummy)
mx.eval(jit_ids)
mx.synchronize()

del dummy


# ============================================================
# CAPTURE REAL HEAD INPUTS WHILE GENERATING WITH EXACT Q6
# ============================================================

captured = []

orig_bind = draft.bind


def capture_bind(target_model):
    out = orig_bind(target_model)

    live_head = draft._lm_head_fn

    def wrapped(h):
        captured.append(h)
        return live_head(h)

    draft._lm_head_fn = wrapped

    return out


draft.bind = capture_bind


# ============================================================
# ANALYSIS
# ============================================================

overall_rank_hist = Counter()

overall = {
    "calls": 0,
    "top1": 0,
    "top2": 0,
    "top4": 0,
    "top5": 0,
    "p42_exact": 0,
}

case_results = []
worst_records = []
all_gap_records = []


def analyze_case(
    case_name,
    prompt_tokens,
):
    rank_hist = Counter()

    stats = {
        "calls": 0,
        "top1": 0,
        "top2": 0,
        "top4": 0,
        "top5": 0,
        "p42_exact": 0,
        "max_rank": 0,
    }

    failures = []

    for call_i, h in enumerate(captured):
        l6 = q6_logits(h)
        l5 = q5_logits(h)

        q6_tok = mx.argmax(
            l6,
            axis=-1,
        )

        mx.eval(
            l5,
            q6_tok,
        )

        t6 = int(
            q6_tok.item()
        )

        target_score = l5[
            ...,
            t6
        ]

        # Deterministic rank matching our Metal tie-break:
        #   higher score first;
        #   on exact tie, smaller token ID first.
        rank = (
            mx.sum(
                l5 > target_score
            )
            + mx.sum(
                (l5 == target_score)
                & (VOCAB_IDS < t6)
            )
            + 1
        )

        # Useful ambiguity diagnostic.
        top2_values = mx.topk(
            l5,
            k=2,
            axis=-1,
        )

        margin = (
            mx.max(top2_values)
            - mx.min(top2_values)
        )

        jury = p42_jury_from_logits(
            h,
            l5,
        )

        ids4 = p42_top4_ids(
            l5
        ).reshape(-1)

        ref_scores = p45_ref_q6x4_scores(
            h,
            ids4,
        )

        metal_scores = p45_q6x4_scores(
            h,
            ids4,
        )

        ref_token = p45_choose_from_scores(
            ids4,
            ref_scores,
        )

        metal_token = p45_choose_from_scores(
            ids4,
            metal_scores,
        )

        policy_token = p45b2b_gpu_jury(
            h,
            l5,
        )

        mx.eval(
            rank,
            margin,
            jury,
            ref_scores,
            metal_scores,
            ref_token,
            metal_token,
            policy_token,
        )

        r = int(
            rank.item()
        )

        j = int(
            jury.item()
        )

        m = float(
            margin.item()
        )

        exact = (
            j == t6
        )

        policy_t = int(
            policy_token.item()
        )

        p45b2b_policy_stats[
            "calls"
        ] += 1

        p45b2b_policy_stats[
            "matches"
        ] += (
            policy_t == t6
        )

        if policy_t != t6:
            p45b2b_policy_mismatches.append(
                {
                    "case": case_name,
                    "call": call_i,
                    "q6_token": t6,
                    "policy_token": policy_t,
                    "rank": r,
                }
            )

        ref_t = int(
            ref_token.item()
        )

        metal_t = int(
            metal_token.item()
        )

        score_equal = bool(
            mx.all(
                ref_scores == metal_scores
            ).item()
        )

        score_err = float(
            mx.max(
                mx.abs(
                    ref_scores.astype(
                        mx.float32
                    )
                    - metal_scores.astype(
                        mx.float32
                    )
                )
            ).item()
        )

        p45_stats["calls"] += 1

        p45_stats["token_matches"] += (
            ref_t == metal_t
        )

        p45_stats["fp16_exact_calls"] += (
            score_equal
        )

        p45_stats[
            "max_abs_score_error"
        ] = max(
            p45_stats[
                "max_abs_score_error"
            ],
            score_err,
        )

        if ref_t != metal_t:
            p45_mismatches.append(
                {
                    "case": case_name,
                    "call": call_i,
                    "ref_token": ref_t,
                    "metal_token": metal_t,
                    "q6_token": t6,
                    "rank": r,
                    "score_err": score_err,
                }
            )

        all_gap_records.append(
            {
                "case": case_name,
                "prompt_tokens": prompt_tokens,
                "call": call_i,
                "q6_token": t6,
                "rank": r,
                "q4_gap12": m,
                "top1_exact": r == 1,
                "p42_token": j,
                "p42_exact": exact,
            }
        )

        stats["calls"] += 1
        stats["top1"] += r <= 1
        stats["top2"] += r <= 2
        stats["top4"] += r <= 4
        stats["top5"] += r <= 8
        stats["p42_exact"] += exact
        stats["max_rank"] = max(
            stats["max_rank"],
            r,
        )

        rank_hist[r] += 1
        overall_rank_hist[r] += 1

        overall["calls"] += 1
        overall["top1"] += r <= 1
        overall["top2"] += r <= 2
        overall["top4"] += r <= 4
        overall["top5"] += r <= 8
        overall["p42_exact"] += exact

        if (
            r > 1
            or not exact
        ):
            rec = {
                "case": case_name,
                "prompt_tokens": prompt_tokens,
                "call": call_i,
                "q6_token": t6,
                "rank": r,
                "margin": m,
                "p42_token": j,
                "p42_exact": exact,
            }

            worst_records.append(
                rec
            )

            if not exact:
                failures.append(
                    rec
                )

    return (
        stats,
        rank_hist,
        failures,
    )


# ============================================================
# RUN BATTERY
# ============================================================

print()
print("=" * 86)
print("P42R1 — DISTRIBUTIONAL ROBUSTNESS BATTERY")
print("=" * 86)

case_no = 0

for target_ctx in CONTEXT_TARGETS:
    for prompt_kind in PROMPT_KINDS:
        case_no += 1

        prompt, actual_ctx = build_prompt(
            prompt_kind,
            target_ctx,
        )

        case_name = (
            f"{prompt_kind}-ctx{target_ctx}"
        )

        captured.clear()

        print()
        print("-" * 86)
        print(
            f"CASE {case_no:02d}/"
            f"{len(CONTEXT_TARGETS)*len(PROMPT_KINDS)} "
            f"{case_name}"
        )

        print(
            f"target ctx={target_ctx} "
            f"actual ctx={actual_ctx}"
        )

        result = mlx_vlm.generate(
            model,
            processor,
            prompt,
            max_tokens=GEN_TOKENS,
            temperature=0,
            draft_model=draft,
            draft_kind=kind,
            draft_block_size=4,
            verbose=False,
        )

        mx.eval(*captured)
        mx.synchronize()

        rounds = len(
            draft.accept_lens
        )

        print(
            f"generation: "
            f"{result.generation_tps:.3f} tok/s | "
            f"rounds={rounds} | "
            f"head_calls={len(captured)} | "
            f"text={short_hash(result.text)}"
        )

        stats, hist, failures = analyze_case(
            case_name,
            actual_ctx,
        )

        calls = stats["calls"]

        print(
            "rank recall: "
            f"top1={stats['top1']}/{calls} "
            f"top2={stats['top2']}/{calls} "
            f"top4={stats['top4']}/{calls} "
            f"top5={stats['top5']}/{calls}"
        )

        print(
            f"max rank={stats['max_rank']} | "
            f"P42C exact="
            f"{stats['p42_exact']}/{calls}"
        )

        if stats["max_rank"] > 1:
            interesting = {
                k: v
                for k, v in sorted(
                    hist.items()
                )
                if k > 1
            }

            print(
                "non-rank1 histogram:",
                interesting,
            )

        if failures:
            print(
                "*** P42C FAILURES:",
                failures[:5],
            )

        case_results.append(
            {
                "case": case_name,
                "kind": prompt_kind,
                "target_context": target_ctx,
                "actual_context": actual_ctx,
                "rounds": rounds,
                "head_calls": calls,
                "generation_tps": result.generation_tps,
                "text_hash": short_hash(
                    result.text
                ),
                **stats,
            }
        )

        captured.clear()
        gc.collect()


# ============================================================
# GRAND SUMMARY
# ============================================================

N = overall["calls"]

print()
print("=" * 86)
print("P42R1 GRAND SUMMARY")
print("=" * 86)

print(
    "cases:",
    len(case_results),
)

print(
    "total real MTP head decisions:",
    N,
)

print()

for k in (
    "top1",
    "top2",
    "top4",
    "top5",
    "p42_exact",
):
    n = overall[k]

    print(
        f"{k:12s}: "
        f"{n}/{N} "
        f"({n/N*100:.6f}%)"
    )

print()
print(
    "global rank histogram:",
    dict(
        sorted(
            overall_rank_hist.items()
        )
    ),
)

max_rank = max(
    overall_rank_hist
) if overall_rank_hist else 0

print(
    "global max Q6-winner rank under Q5:",
    max_rank,
)

jury_failures = (
    N
    - overall["p42_exact"]
)

print(
    "actual P42C jury failures:",
    jury_failures,
)


# Show the most concerning states first.
worst_sorted = sorted(
    worst_records,
    key=lambda x: (
        -x["rank"],
        x["margin"],
    ),
)

print()
print("WORST / AMBIGUOUS STATES:")

for rec in worst_sorted[:30]:
    print(
        f"  {rec['case']:24s} "
        f"call={rec['call']:4d} "
        f"rank={rec['rank']:3d} "
        f"margin={rec['margin']:.8f} "
        f"Q6={rec['q6_token']:6d} "
        f"P42={rec['p42_token']:6d} "
        f"exact={rec['p42_exact']}"
    )


# ============================================================
# SAVE MACHINE-READABLE RESULT
# ============================================================

out = {
    "settings": {
        "generation_tokens": GEN_TOKENS,
        "context_targets": CONTEXT_TARGETS,
        "prompt_kinds": PROMPT_KINDS,
    },
    "overall": overall,
    "rank_histogram": dict(
        sorted(
            overall_rank_hist.items()
        )
    ),
    "max_rank": max_rank,
    "jury_failures": jury_failures,
    "cases": case_results,
    "interesting_states": worst_sorted,
    "gap_records": all_gap_records,
    "p45b2b_policy": {
        "calls": p45b2b_policy_stats[
            "calls"
        ],
        "matches": p45b2b_policy_stats[
            "matches"
        ],
        "mismatches": (
            p45b2b_policy_mismatches
        ),
    },
    "p45b2a": {
        "calls": p45_stats["calls"],
        "token_matches": p45_stats["token_matches"],
        "fp16_exact_calls": p45_stats["fp16_exact_calls"],
        "max_abs_score_error": p45_stats[
            "max_abs_score_error"
        ],
        "mismatches": p45_mismatches,
    },
}

OUTFILE = (
    "/tmp/p45b2b-gpu-policy-robustness-results.json"
)

with open(
    OUTFILE,
    "w",
) as f:
    json.dump(
        out,
        f,
        indent=2,
    )

print()
print(
    "saved:",
    OUTFILE,
)


print()
print("=" * 86)

if jury_failures:
    print(
        "P42R1 VERDICT: FAIL — "
        "P42C diverged from certified Q6 on "
        f"{jury_failures}/{N} real decisions."
    )

elif max_rank <= 2:
    print(
        "P42R1 VERDICT: STRONG PASS — "
        "Q6 winner stayed inside deterministic Q5 top-2 "
        "for every captured state, and actual P42C jury "
        "matched every decision."
    )

elif max_rank <= 4:
    print(
        "P42R1 VERDICT: TOP-2 NOT ROBUST ENOUGH, "
        "BUT TOP-4 COVERS ALL OBSERVED STATES."
    )

else:
    print(
        "P42R1 VERDICT: INVESTIGATE — "
        f"observed Q6 winner rank as high as {max_rank}."
    )

print("=" * 86)

print()
print("P42R1 DONE")
