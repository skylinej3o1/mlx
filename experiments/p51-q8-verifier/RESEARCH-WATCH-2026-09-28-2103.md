# Project 51 primary-lane research watch — 2026-09-28 21:03 ET

**Freshness boundary entering this pass:** **2026-09-28 22:00:02 UTC**.  
**User cutoff:** **2026-09-29 01:03:02 UTC**.

## Decision

**No target or durable STATE change.**

This strict-window pass found two useful runtime-mechanism updates and one anecdotal deployment signal, but no direct physical evidence strong enough to move the Project-51 planning centers or AA priors.

## Strict-window findings

### NEW — MLX-Serve prompt-lookup speculation widens earlier on repeated spans

Source: https://github.com/ddalcu/mlx-serve/commit/e763f7e5cdc4f5b2dd2f2e45313e48b8b295d333  
Timestamp: **2026-09-28 22:51:11 UTC**.

MLX-Serve changed its prompt-lookup gate so a **16-token exact suffix match** is enough to use the strong lookup cap, drafting up to **14 tokens**, instead of waiting for a 32-token agreement. The implementation keeps the known S=16 cost cliff avoided by capping the actual strong draft at 14; the commit explicitly notes that a 15-draft cap measured slower.

Project-51 interpretation:
- this is useful mechanism evidence for repeated code, quoted tool output and agent-history self-speculation;
- it strengthens the case for a separate cheap prompt/history lookup lane whose width policy is not tied to MTP width;
- it is **not** an M1 physical TG receipt and does not justify changing the single-M1 25-TG or dual-M1 40-TG targets.

### NEW — vLLM sparse-index compaction proves nominal row length is not a validity mask

Source: https://github.com/vllm-project/vllm/commit/75fad5bbef7b2c0264c4b7ce6c4c10e32233d523  
Timestamp: **2026-09-28 23:40:11 UTC**.

The ROCm sparse-MLA path had dense rows whose nominal `lengths` still contained `-1` or out-of-range entries. Downstream consumers indexed the KV pool without checking the sign. The fix first counts valid entries and then compacts only in-range indices into the ragged representation.

Project-51 interpretation:
- cross-runtime corroboration of an already-canonical correctness rule;
- QSA / sparse-attention / verifier proposal rows must carry explicit validity and never treat padded or sentinel slots as real proposals merely because they lie inside a nominal width/length;
- hardware/model path is ROCm sparse MLA, not Qwen Flash on Apple7, so this is correctness evidence only and does not move targets.

### SAME-DAY CURRENT — Strata IQ3_S user deployment / concurrency request

Source: https://github.com/Niko1221/Strata/issues/97  
Created: **2026-09-28 22:48:54 UTC**.

A user on an RTX 3090 Ti with 128 GB RAM reports that Flash-Next IQ3_S works well enough for them to replace their 27B IQ3_S setup and asks for concurrent sessions. There are no TG, PP, context-depth, soak, AA or paired-quality measurements.

Project-51 interpretation:
- useful adoption signal only;
- do **not** use it to move the RTX 5070 Ti IQ3_S ladder or the AA>=40 prior.

## RECOVERED OLDER — third-party dense-27B IQ3_S long-context / agent workload evidence

Source: https://www.gauntletbench.com/models/qwen3.8-27b-gsq-rco-iq3-s-gguf-ista-daslab-ollama-mbp-identical-file-arm-of-m35/

GAUNTLET Bench has an older ISTA-DASLab **Qwen3.8-27B GSQ-RCO IQ3_S** arm with:
- long-context retrieval & synthesis: **120/120**, 6/6 tests, run 2026-09-20;
- MRCR: **44.1/60**, including two 20/20 cells and one 4/20 cell, run 2026-09-17;
- production replay / real-agent workload: **189.6/240**, 12/12 tests, run 2026-09-26.

Its methodology says the long-context suites use a genuinely full context window, but the public page does not provide a token-count denominator for these cells. It is also **dense 27B, not Flash-Next**, third-party judged, mostly n=1, and has no BF16/source-paired arm on those long-context cells.

Project-51 interpretation:
- useful supporting evidence that aggressive GSQ-RCO IQ3_S can behave well on long-context retrieval and real-agent-style workloads;
- **not** the requested Flash-Next IQ3_S 32K/64K/128K/262K source-vs-quant evidence;
- does not move the current **~80% IQ3_S AA>=40 planning prior**.

## Strict-window negative scan

From **2026-09-28 22:00:02 -> 2026-09-29 01:03:02 UTC**:

- **TensorFold:** no post-boundary commit after 0.3.6.2; no new M1 mixed-bit receipt.
- **Strata:** no post-boundary release/commit beyond 0.1.20, no exact RTX 5070 Ti 32K/64K/128K ladder, and no 8h/24h soak receipt.
- **oMLX:** no post-boundary Qwen/Flash commit found.
- **Ishizuki:** no post-boundary commit.
- **llama.cpp:** no post-boundary commit.
- **SGLang:** several post-boundary commits, but no new Project-51 Qwen3.8/Flash state-transfer or target-hardware receipt.
- **vLLM:** the sparse-index validity fix above is relevant as a correctness analogue; no new Flash-Next target-hardware throughput evidence.
- **DASLab / Hugging Face:** no newer official Flash-Next IQ3_S long-context or source-paired result found beyond the already-promoted SWE-bench Verified **82.0 vs 82.8 BF16** result.
- **M1 / M1 Max Flash-Next:** no new provable strict-window physical receipt found.

## Canonical planning state

Unchanged:
- Dual M1 Flash-Next: **40 TG sustained @ genuinely filled ~128K / 400 cold PP / ~70% >=40 TG**.
- Single M1 dense27B: **25 TG / ~110 PP**.
- RTX 5070 Ti dense CUDA-v2 physical ladder unchanged.
- Strata IQ3_XXS / IQ3_S planning ladders unchanged.
- IQ3_XXS AA>=38: **~85%**.
- IQ3_XXS AA>=40: **~65%**.
- IQ3_S AA>=40: **~80%**, still not AA-certified.

## Files intentionally not changed

- `RESEARCH-STATE.md`: no durable conclusion changed.
- `RESEARCH-TARGETS.md`: no direct physical/quality evidence moved the planning distribution.

## New hard boundary

**2026-09-29 01:03:02 UTC**
