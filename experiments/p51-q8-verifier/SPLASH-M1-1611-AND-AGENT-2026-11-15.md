# Splash 1.6.1-m1.1 and persistent agent reliability — Nov 15, 12:52 EST

**Document-only evidence receipt.** Strict interval 2026-11-15T15:49:00Z to 2026-11-15T17:52:37Z. [Full watch](./RESEARCH-WATCH-2026-11-15-1252.md).

## Shipped release and regression fix

[Paperniuk 1.6.1-m1.1](https://github.com/paperniuk/splash/releases/tag/1.6.1-m1.1), published16:35:17Z, built at 9921abc8cf34621a05b6d35ff97d21fb4b708f41, unofficial M1/M2 fork. [#65](https://github.com/paperniuk/splash/pull/65) merged15:55:54Z. Source fork Metal Break erroneously committed buffers before SSD expert load host step finished; GPU read uninitialized experts, prefill nonfinite, model_result_invalid. Fix routes through commitEncoded to obey host-step order. M1Max64 original GSQ-RCO IQ3_XXS with --expert-memory16G gets Ready and short correct streamed reply; no physically128K/259K task suite. This does not imply same performance as resident original ISTA source model. [#63](https://github.com/paperniuk/splash/issues/63) 24h 'growth paused' oscillation/31–39→16.8TG slowdown still open. Do not recommend always-on default until measured long-term.

## Paired ANE/GPU prefill on dense27B, quant and task limits

[#64](https://github.com/paperniuk/splash/pull/64) merged15:55:54Z and is in release. On **M1Max64**, dense Qwen3.8-27B **MLX 4bit**, calibrated ANE share0.50 versus opt-in pair share0.735, min rows512, prefills tok/s: 560 175→166 (−5%),1.1K202→221 (+10%),2.1K215→254 (+18%),7K215→255 (+18%),16.7K203→241 (+19%). Earlier 32GiB M1Max numbers comparable but not final revision and should not supersede final 64GB data. One/two-lane MLX4 decode57.6/63.2 unchanged; other 27B UD-Q5KM49.9/57.9 unchanged. Mechanism overlaps GPU attention/mixer of one half with Neural Engine FFN of other; explicit --ane-ffn-share required, normal calibrated path bit-equal to previous.

Quality 4 texts (docs/Python/README/quant guide), 1/2/4K 129 positions each, compared with GPU same **4bit** source: calibrated KL0.00050, top1 99.1%; paired KL0.00057, top1 99.2%; differences in chunk order or share can alter greedy outputs. This is not BF16 KL, not Q4 vs Q5 comparative quality, not QFN GDN/QSA/PLE and not real code-agent correctness. User hardware test requires HIGH permission.

## Molt and agent correctness implications

[Qwen Code#15959](https://github.com/QwenLM/qwen-code/pull/15959) MERGED16:09Z: hosted interruption restores user prompt with paired committed assistant/tool history, unlike cancellation/error groups, covered by 905 mocked tests; physical SIGKILL test not performed. Molt handoff should preserve causal instruction, ordered acknowledged tool calls + exact results, settlement reason, idempotent retry handle, prefix-cache identity and checkpoint provenance; never rehydrate orphan tool messages.

[Strata#6044](https://github.com/Niko1221/Strata/pull/6044) OPEN adaptive idle slot memory, tested other RTX2080Ti22 QFN UD-Q3KXL true256K; idle restored expert cache 3164→6223 slots, four concurrently served with VRAM grow1.8–2.3s, HIP and DFlash2 slot drafts explicitly excluded. Useful independent-agent resource scheduling design, no owner result.

[Kapitsa#1277/1279](https://github.com/nace-ai/kapitsa/issues/1277) on other Qwen3.6-35B UD-IQ2XXS omitted literal opener in raw tokens, partial fallback OPEN; [llama.cpp#32348](https://github.com/ggml-org/llama.cpp/issues/32348) required tool call can be delayed forever with cached prompt on other 9B. Agent correctness means *completed tool-using tasks, not tok/s*, including cache on/off and mixed long sessions.

## Qwen and other model discovery

No Qwen4 official Flash/27B downloadable weights in checked sources; max-preview API only. [ConceptCountry edited 27B](https://concept.country/research/weight-space-programming) Nov8 author paper claims LiveCodeBench+13pp after nine rank-one down-projection edits and matched random control. [Model card](https://huggingface.co/ConceptCountry/qwen-concept-27b) explicitly says Q4_K_M is not quality-tested; experimental BF16/Q8 result only, no independent agent long-context reproduction. Candidate for desk audit, not automatic model swap or download.

## Tests proposed, not executed

Same source/quant physically128K/259K QFN DS4 native MTP vs DFlash2, Splash GSQ streamed 24h soak, high-quality dense27B Q5 ANE pair vs calibrated, agent tools/cancel/retry; Relay exact checkpoint CUDA5070Ti to M1 decode with full QSA/GDN/PLE state and true TTFT. ALL require separate HIGH. No owner machine, CI, model or code changes.
