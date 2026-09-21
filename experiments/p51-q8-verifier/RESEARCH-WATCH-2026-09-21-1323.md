# Project 51 research watch — 2026-09-21 13:23 ET

**Freshness boundary checked:** previous hard boundary **2026-09-21 16:46:31 UTC**. Search ran through the user's cutoff **2026-09-21 17:23:50 UTC**.

## Decision

**No numeric TG/PP, quality-floor, or confidence change.**

This was a quiet 37-minute window. No new exact-window M1/Flash-Next or 27B performance receipt appeared. Two older items surfaced during the pass and are worth recording because they sharpen mechanisms already relevant to P51:

1. vLLM #52244 gives a precise hybrid-GDN/MTP prefix-cache failure mode: cached recurrent state must be published at the actual replay landing position after last-token replay and speculative rewind, not merely at the prompt tail.
2. Splash #88 independently shows that Apple9 Q4/MoE batch-specific kernels can produce very large B2-B4 gains with essentially flat B1, while also retaining explicit cold-vs-cache token-agreement caveats.

Only the first changes a durable correctness rule in STATE. TARGETS remain untouched.

## RECOVERED OLDER EVIDENCE — vLLM #52244 hybrid GDN/MTP replay boundary

Source: vLLM PR #52244, created **2026-08-14**. It was active again at 16:55 UTC in this window, but the measurements and mechanism are older; this is therefore **recovered older evidence**, not a fresh timestamped result.

### Failure mechanism

On Qwen3.5-122B-A10B with MTP, a 1,072-token GDN page and 67-token fine-grained prefix hash unit:

- ordinary replay caps at `prompt_len - 1` because the final prompt token must be recomputed for logits;
- the MTP/EAGLE drafter then rewinds one 67-token hash unit further;
- the producer had published GDN state at the prompt tail boundary instead of where the replay would actually land;
- the full-attention and recurrent groups therefore had no compatible common resume point and their intersection fell to a prior page or to zero.

Examples from the reported live before/after table:

| prompt tokens | before cached | after cached | replay ceiling |
|---:|---:|---:|---:|
| 1,072 | 0 | **938** | 938 |
| 2,000 | 0 | **1,876** | 1,876 |
| 2,144 | 0 | **2,010** | 2,010 |
| 3,000 | 1,072 | **2,881** | 2,881 |
| 3,500 | 2,144 | **3,417** | 3,417 |
| 12,345 | 10,720 | **12,261** | 12,261 |

The patch publishes recurrent state at the actual rewound landing boundary, preserves the full-attention tail positions that future extensions can reach, and avoids advertising prompt-end recurrent states that no lookup can legally resume from.

### Validation

- 132 prompt lengths swept: every patched replay landed exactly at the calculated ceiling.
- Reported Qwen3.5 GPQA/GSM8K checks showed no quality regression.
- Four real prefix-hit text cases at temperature 0 produced byte-identical cold vs replay output, repeated twice.

### P51 consequence

This is directly relevant to `sup`, sleep/restore, rewind and canonical-state publication.

Do not define a committed cache boundary as 'deepest state we have'. Define it as **deepest state every required consumer can actually resume from** after:
- last-token/logit replay;
- speculative rewind;
- target-vs-draft native cache geometry;
- recurrent/GDN checkpoint availability;
- QSA/indexer state availability;
- page/hash alignment.

Hybrid-group intersection should be a first-class invariant in the Actions restore tests.

## RECOVERED OLDER EVIDENCE — Splash #88 Apple9 batch-width kernels

Source: Splash PR #88, created **2026-09-21 08:25 UTC**. Activity occurred again at 16:52 UTC, but the benchmark body predates this pass.

Controlled M3 Max 40-core ABBA against its prior integrated candidate reports incremental aggregate-decode changes:

| model | B1 | B2 | B3 | B4 |
|---|---:|---:|---:|---:|
| Qwen3.8-27B | -0.37% | **+65.9%** | **+74.3%** | **+53.5%** |
| Qwen3.6-35B-A3B | -0.69% | **+29.8%** | **+40.5%** | **+31.2%** |

The implementation extends shape-specific Q4/MoE matrix kernels across batch widths 1-4 and reuses prepared activation/group-sum/split work per tile. This independently agrees with oMLX #3797: **B1 and multi-request inference are different kernel problems**, and total verify rows should drive kernel selection.

Important correctness caveat from the same PR: fixed ABBA decode output hashes and accepted/drafted counts matched the prior candidate, but the author explicitly reports a small number of **cold-vs-cached token disagreements** on both M3/M5 validation. The real client harness was also waived in final combined validation and historical client failures were retained.

### P51 consequence

No B1 forecast effect. For later concurrent-agent serving, preserve separate B1/B2/B4 kernel certification and keep the multi-turn runtime-behavior gate added in the prior watch.

## Exact-window repository sweep

- `antirez/ds4`: no commits in-window; no new target evidence.
- `vllm-project/vllm`: commits were KV-hint plumbing, docs and ROCm shared-expert dispatch. No exact M1/Flash TG receipt. #52244 is recorded only as recovered older evidence; its body predates the window.
- `jundot/omlx`: no commits in-window; only UI/tool-parser activity. No new P51 performance measurement.
- `ddalcu/mlx-serve`: no commits in-window.
- `ggml-org/llama.cpp`: one state-save/load test commit adding logits/NMSE comparison; useful test infrastructure but no model performance evidence.
- `incoai/splash` / `npanj/splash`: no commits in-window. Splash #88 is recovered older evidence, not a new exact-window benchmark.
- `kadirbalalan/qwen38-mac-fast`, visible Kadir llama.cpp fork, `youssofal/MTPLX`, `localai-org/apex-quant`, `ikawrakow/ik_llama.cpp`, Intel AutoRound: no qualifying model/runtime commit in-window.
- Web/community/Hugging Face sweep surfaced the already-known Splash Q8 post and existing ByteShape/Qwen3.8 material; no additional result with a trustworthy evidence timestamp inside this exact window.

## Target / confidence impact

Unchanged:
- Flash-Next production floor: **>=38 AA-class behavior**, preferred 39-40.
- Flash headline: **40 TG @ ~128K**.
- Flash cold PP: **400**.
- Flash confidence ladder unchanged.
- Single-M1 Qwen3.8-27B target: **25 TG**.
- 5070 Ti and DS4 targets unchanged.

Next-work ordering remains:
1. P69B13;
2. cycle / acceptance / dispatch / warm-state instrumentation;
3. P70 Splash-style Apple7 experiments;
4. multi-turn behavioral equivalence gates;
5. explicit cold vs each restored-state tier.

## New hard boundary

**2026-09-21 17:23:50 UTC**
