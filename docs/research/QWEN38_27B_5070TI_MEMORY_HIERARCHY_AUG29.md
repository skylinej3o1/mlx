# Qwen3.8-27B on RTX 5070 Ti 16GB: hybrid quant + KVarN + adaptive KV + compaction

Status: **field-derived architecture note / not yet locally certified**

Updated: 2026-08-29 ET.

## Why this note exists

A new LocalLLaMA result materially changes the preferred 5070 Ti serving plan for Qwen3.8-27B.

The earlier extreme-context path used RaymondHuang210129's adaptive-KV-streaming llama.cpp fork with a UD-Q3_K_XL-class neural quant, authoritative KV in pinned host RAM, and a bounded GPU-resident/prefetch ring. That remains the most interesting path when raw context must approach 200-262K.

A newer 16GB-GPU result instead demonstrates a much faster **fully GPU-resident ~100K-class profile** using:

- `jrell/Qwen3.8-27B-i1-IQ4_XS-GGUF-Smaller`;
- BeeLlama.cpp;
- native MTP depth 2;
- KVarN compressed KV, reported as KVarN5 K / KVarN4 V;
- a recent high-precision KV tail;
- ~100K context;
- roughly high-40s to ~50 tok/s on the reported RTX 4070 Ti SUPER 16GB setup.

Primary field post:
- https://www.reddit.com/r/LocalLLaMA/comments/1w1lq7u/qwen_38_27b_at_50_toks_with_100k_context_on_a/

Relevant implementations / quant:
- https://huggingface.co/jrell/Qwen3.8-27B-i1-IQ4_XS-GGUF-Smaller
- https://github.com/Anbeeld/beellama.cpp
- https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming

The user's RTX 5070 Ti 16GB has more memory bandwidth than the reported 4070 Ti SUPER, but the practical Windows/display VRAM budget is only about 14.9 GiB. Therefore the exact reported ~15.9GB configuration should **not** be copied blindly.

## Quantization takeaway

The jrell quant is interesting because it is intentionally asymmetric rather than a uniform low-bit squeeze:

- important attention / non-FFN tensors retain roughly IQ4_XS-class precision;
- large FFN gate/up/down reservoirs are pushed lower, around IQ3_S-class precision;
- the result is around the mid-13GB class rather than a conventional ~14.5GB+ IQ4 build.

This is attractive for an agent system where closed-book general knowledge is not the primary objective. RAG, repository retrieval, tools, and web search can compensate for some lost parametric recall.

However, FFN quantization does **not** selectively remove only trivia. It can also affect reasoning, coding, instruction following, and use of retrieved evidence. The quant therefore still requires coding/agent-task certification rather than being assumed safe from perplexity alone.

## Preferred three-profile 5070 Ti plan

### 1. FAST / daily-driver agent profile

Target:

- jrell asymmetric neural quant;
- Bee KVarN history;
- recent high-precision KV tail;
- native MTP;
- roughly 32-64K active context initially;
- remain fully GPU-resident.

Purpose: maximize normal coding-agent latency and throughput.

### 2. AGENT / extended working-set profile

Target:

- same neural quant;
- KVarN historical KV + recent precision tail;
- approximately 64-100K active context;
- Tameru-style compaction before raw context expands merely because capacity exists.

Purpose: persistent agent sessions with a dense, useful working set rather than unbounded transcript accumulation.

### 3. DEEP / raw-history retention profile

Target:

- adaptive host-RAM KV tiering when exact raw context is genuinely valuable;
- approximately 100-262K physical context as an exception mode;
- accept lower decode speed in exchange for preserving raw history.

Purpose: avoid forced semantic loss when a task genuinely needs the original long history.

## The combined architecture

The long-term preferred design is to combine the mechanisms rather than choose between them:

```text
Qwen3.8-27B
  |
  +-- asymmetric neural quant
  |     attention/core protected more strongly
  |     large FFN reservoir compressed more aggressively
  |
  +-- native MTP / optional context-derived drafting
  |
  +-- KV hierarchy
        recent tail: high precision
        older history: KVarN compressed
              |
              +-- GPU hot/resident pages
              +-- pinned-host authoritative overflow
                    |
                    +-- adaptive prefetch / residency planner
```

This composition should be beneficial in principle because compressed KVarN history can reduce both:

1. VRAM required per resident KV page; and
2. PCIe payload when pages move between host RAM and the GPU.

That could partly offset the jrell neural quant being larger than UD-Q3_K_XL while preserving a better neural precision allocation.

## Important implementation caveat

This is **not a drop-in configuration today**.

The adaptive-KV fork is currently validated around its own KV representation / tested model configuration, while BeeLlama owns a separate KVarN-aware CUDA attention path, precision-tail handling, and MTP integration.

The likely engineering direction is therefore:

> port the adaptive residency/prefetch planner into BeeLlama's fast path,

rather than trying to bolt Bee's entire KVarN/MTP stack onto the adaptive fork.

This should be treated as a future integration project after first reproducing the standalone Bee result on the 5070 Ti.

## Why compaction remains central

Physical context capacity and semantic context quality are different problems.

The agent should not run at 200K continuously merely because adaptive KV makes that possible. Coding sessions accumulate:

- stale tool output;
- superseded plans;
- prior file versions;
- duplicate source;
- dead hypotheses;
- repeated system/tool metadata.

Tameru-style compaction should keep the active context dense with high-value state. Adaptive KV then acts as insurance:

> memory pressure no longer forces compaction; semantic value decides whether compaction is appropriate.

The preferred hierarchy is:

1. active context in the fastest GPU-resident profile;
2. compact durable state / summaries when material has become redundant;
3. RAG/repository retrieval/web search for recoverable external knowledge;
4. adaptive raw-history retention only when exact old context remains valuable.

## Local certification matrix

Do not certify KVarN from generic perplexity alone. Compare at minimum:

- high-precision or Q8 KV reference;
- KVarN6/6;
- KVarN5/5;
- KVarN5/4;
- KVarN4/4;
- with the same recent precision-tail policy.

Rulers should include:

- exact code copying;
- minified JS or similarly punctuation-sensitive source;
- JSON/tool payloads;
- patch/diff generation;
- literal symbol/file retrieval;
- long-context needle retrieval;
- Playwright/repository coding tasks;
- 30K, 60K, 90K-ish depths.

A prior Bee issue reported reproducible code corruption under compressed KV on a related Qwen dense model, so exact-source/code-copy tasks are mandatory qualification cases even if median-KLD looks excellent.

## First local experiment order

1. Reproduce the jrell + Bee profile at ~32K-64K with generous VRAM margin.
2. Freeze prompt, sampling, template, MTP depth, and generated-token count.
3. Sweep KV formats / tail policy while measuring task correctness, TG, PP, and VRAM.
4. Walk context upward: 64K -> 72K -> 80K -> 88K -> 96K -> 100K only while fully resident and stable.
5. Test official/default chat template first; treat reduced-thinking / Sharp-style prompting as a separate wall-time experiment.
6. Only after the Bee path is certified, prototype Bee + adaptive host-KV tiering.
7. Evaluate Tameru compaction as a policy layer above both profiles rather than as a substitute for runtime memory management.

## Current planning conclusion

For the 5070 Ti, the preferred order is now:

1. **jrell asymmetric quant + Bee KVarN + native MTP** for normal 32-100K agent use;
2. **adaptive KV streaming** for 100-262K raw-history exception mode;
3. investigate a **combined Bee + adaptive residency** implementation if the first two profiles independently validate.

The optimization target is complete agent-task success / wall time, not closed-book trivia retention or maximum nominal context alone.
