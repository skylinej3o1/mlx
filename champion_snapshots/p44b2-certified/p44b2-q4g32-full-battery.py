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
# BUILD Q4/G32 SEARCH HEAD
# ============================================================

if hasattr(model, "language_model"):
    target_head = model.language_model.lm_head
else:
    target_head = model.lm_head

print()
print("Building Q4/G32 search head...")

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
        group_size=32,
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


def p42_jury_from_logits(
    h,
    logits5,
):
    ids = p42_top4_ids(
        logits5
    )

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
    "top8": 0,
    "p42_exact": 0,
}

case_results = []
worst_records = []


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
        "top8": 0,
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

        mx.eval(
            rank,
            margin,
            jury,
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

        stats["calls"] += 1
        stats["top1"] += r <= 1
        stats["top2"] += r <= 2
        stats["top4"] += r <= 4
        stats["top8"] += r <= 8
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
        overall["top8"] += r <= 8
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
            f"top8={stats['top8']}/{calls}"
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
    "top8",
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
}

OUTFILE = (
    "/tmp/p44b2-q4g32-robustness-results.json"
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
