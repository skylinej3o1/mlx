# Tiel / Ornith-1.5 trained-MTP coding-quant note

Status: **CORE / Apple coding-agent lead**

Updated: 2026-08-26

Primary model:

- https://huggingface.co/peculiar-ragdoll/Tiel-Coder-35B-A3B-GGUF-MTP

Base model:

- https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B

## What Tiel is

Tiel is not a newly trained 35B backbone. The model card describes it as:

- Ornith-1.5-35B-A3B weights;
- dynamically requantized using a coding-heavy importance matrix;
- Sharp chat template embedded in the GGUF;
- optional upstream Ornith MTP / `nextn` block retained in the MTP repository.

That distinction matters because MXFORGE can treat Tiel as an **execution/quant/template branch of Ornith**, not as an unrelated model family.

## Important upstream change: Ornith MTP head was replaced

The Tiel author reports that the first Ornith-1.5 MTP block was effectively untrained/random and therefore stripped from the original Tiel quant ladder.

On **2026-08-23**, Ornith re-uploaded the affected shard with a trained `nextn` head. The Tiel MTP repository was then built around that replacement.

The author reports checking the replacement weight statistics rather than trusting only the announcement: the new tensors show strongly non-random heavy-tailed structure, unlike the old near-Gaussian initialization.

MXFORGE implication:

> Old Ornith MTP benchmark conclusions made with the broken/random head are stale. Re-test Ornith speculation only with the corrected post-2026-08-23 head.

## Shipped MTP quant ladder

Current Tiel MTP files include approximately:

| Tier | File size |
|---|---:|
| UD-Q2_K_XL | 13.2 GB |
| UD-IQ3_XXS | 14.1 GB |
| UD-Q3_K_XL | 17.7 GB |
| UD-IQ4_XS | 18.6 GB |
| UD-Q4_K_S | 21.8 GB |
| UD-Q4_K_XL | 23.3 GB |
| UD-Q5_K_XL | 27.5 GB |
| UD-Q6_K_XL | 32.7 GB |
| UD-Q8_K_XL | 39.4 GB |

The MTP repository says each tier carries roughly **0.9 GB of MTP-head weights**, pinned at the same precision instead of following the target tier's bit width.

This is a useful quant-design precedent: treat the speculative head as an independent precision component.

## Coding-focused quant calibration

The non-MTP Tiel card explains that its importance matrix was built from about 49M characters, roughly:

- ~75% code-oriented calibration;
- ~25% mixed data covering math, tools and non-English text.

The matrix was measured across about 1.5M tokens and deliberately large enough to exercise Ornith's 256-expert MoE rather than leaving rare experts under-calibrated.

MXFORGE lesson:

> For large sparse MoE quantization, calibration-corpus coverage must be judged at the **expert population** level, not merely by total token count.

## Reported capability / task-time evidence

Tiel's model card reports a 25-problem SWE-bench-Live slice with one attempt per problem:

| Model | Solved | Median attempt time |
|---|---:|---:|
| Qwen3.8-27B | 16 / 25 | 50.2 min |
| Dirk 27B | 15 / 25 | 20.1 min |
| Tiel | 12 / 25 | 8.6 min |
| stock Ornith comparator | 8 / 25 | 5.5 min |

The same card reports Tiel at 67.2 on its Claw-Eval multi-turn score, versus 65.3 for Ornith and 60.5 for Nail, while Tiel is weaker on MMLU-Pro.

Treat all of these as **project-authored model-card measurements**, not MXFORGE-certified capability.

The high-value signal is the shape of the trade-off:

- Qwen3.8 solves more of the small SWE slice;
- Tiel/Ornith attempts are dramatically faster;
- completed engineering work per hour may therefore favor a waterfall rather than one universal local model.

## MTP tuning lesson

The Tiel MTP card explicitly warns that speculation knobs depend on hardware and should be swept locally rather than assuming larger draft depth is better.

This is directly aligned with P51-P69 verifier work: target verification cost, acceptance, and row geometry jointly determine useful tokens/ms.

## M1 Max experiment priority

The existing `M1_MAX_27B_ORNITH_QUANT_REFRESH.md` established that Ornith-1.5-35B-A3B is already extremely fast on an M1 Max because only ~3B parameters are active per token.

The corrected MTP head changes the recommended next experiment from "Ornith AR only until speculation proves itself" to:

1. keep plain AR as the control;
2. use the corrected post-2026-08-23 MTP head;
3. sweep draft depth / verifier width on the actual M1 Max;
4. benchmark Tiel-style Q4/Q5/Q6 target quantizations;
5. preserve ordinary/high-quality KV first;
6. measure complete coding-agent wall time, not only tok/s.

Suggested matrix:

```text
Target quant:
  Tiel Q4_K_XL
  Tiel Q5_K_XL
  Tiel Q6_K_XL
  clean Ornith oQ4e/oQ6e controls

Speculation:
  off
  MTP depth 1
  MTP depth 2
  MTP depth 3+

Context:
  4K
  16K
  ~29-32K
  64K

Workloads:
  code generation
  repo edit/tool loop
  debugging
  prose/reasoning control
```

Record:

- target-only tok/s;
- MTP tok/s;
- accepted tokens / cycle;
- acceptance by depth;
- verifier time;
- memory footprint;
- tool-call validity;
- task success;
- complete wall-clock task time.

## Likely deployment role if reproduced

Potential local waterfall:

```text
Tiel / Ornith Q5-Q6 + corrected MTP
  -> routine coding, repo exploration, tool work, cheap iterations

Qwen3.8-27B MXFORGE Q8 + DFlash/native MTP
  -> hard debugging, architecture, difficult reasoning, final review
```

This is a hypothesis until paired M1 agent runs show that Tiel's lower per-attempt capability is offset by enough additional attempts / lower task time.

## Promotion rule

Do not promote Tiel as a Qwen replacement based on the 25-problem model-card slice.

Promote only if a matched local agent harness shows superior **completed correct tasks per hour or per joule/dollar** for the intended worker tier while maintaining acceptable tool reliability.
