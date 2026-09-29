# Project 51 primary-lane research watch — 2026-09-29 11:03 ET

**Freshness boundary entering this pass:** **2026-09-29 12:57:59 UTC**.  
**User cutoff:** **2026-09-29 15:03:35 UTC**.

## Decision

**Durable STATE + TARGETS update.**

One planning probability moves:
- Strata / RTX 5070 Ti / IQ3_XXS / ~128K mature TG target stays **78 TG**;
- planning confidence rises **~65% -> ~85%** after a direct physical RTX 5070 Ti / IQ3_XXS / Strata 0.1.24 report at **79.7 TG @128K**.

No TG center, PP center, AA prior or dual-M1 headline target moves.

A new production qualification gate is added:
- **draft-vocabulary / candidate-space coverage by language/domain** must be healthy before verifier-width or MTP-acceptance tuning is interpreted.

## Strict-window findings

### NEW — exact RTX 5070 Ti / IQ3_XXS / 128K Strata receipt

Source:
https://github.com/Niko1221/Strata/issues/137  
Created: **2026-09-29 13:36:55 UTC**.

Physical box:
- RTX 5070 Ti 16 GB, PCIe 5.0 x16;
- Ryzen 7 7700;
- 96 GB DDR5-5200;
- Ubuntu 24.04;
- CUDA 13.2;
- Strata **0.1.24**;
- ISTA-DASLab GSQ-RCO **IQ3_XXS**;
- MTP packed Q2_0;
- INT8 KV;
- `--max-context 131072`;
- `--kv-resident 32768`.

The author reports against a tuned llama.cpp fork on the same box/model class:
- Strata prefill: **2,590-2,830 PP** versus llama.cpp **660-750**;
- at **128K**, Strata decode: **79.7 TG** versus llama.cpp **81.3 TG**.

The 128K denominator is the key P51 result. It directly supports the existing **78-TG** IQ3_XXS center on the correct GPU class.

Why the center does not move:
- single external machine/run family;
- CPU/RAM differ from the user's exact Windows box;
- speculative acceptance is strongly text/language dependent;
- no frozen 32K/64K/128K exact-box matrix yet.

Why confidence does move:
- the previous 128K TG row was explicitly partly extrapolated;
- a physical 5070 Ti now clears the target at the named context.

Target effect:
- **78 TG stays**;
- confidence **~65% -> ~85%**.

### NEW — MTP draft vocabulary silently excludes CJK

Same Strata issue #137.

The shipped `draft_vocab.bin`:
- contains **40,525 token ids**;
- only **27** contain a CJK character.

The model's full vocabulary:
- contains **55,328 CJK-bearing tokens**.

Therefore the subset draft head can almost never propose the target model's Chinese token.

Controlled fixed-prompt result:

| Workload | bundled subset | full native head |
|---|---:|---:|
| Chinese 6K-table description | 65-67 TG | **78 TG** |
| Chinese concept explanation | 70-73 TG | **84-87 TG** |
| Python + Chinese notes | 90-95 TG | **99-100 TG** |
| Average | **76.8 TG** | **87.7 TG (+14%)** |

Draft acceptance/counts rise materially when the full head is used. The author reports no VRAM penalty in the observed run.

P51 rule:
- draft candidate-space coverage is part of the speculative configuration identity;
- acceptance must be measured by output language/domain;
- code/JSON/tool-call symbols and multilingual outputs need explicit coverage;
- use a full-head/fail-open path when the subset cannot represent the target distribution;
- do not blame verifier width, MTP quality or kernel cost until candidate coverage is known healthy.

### NEW — verifier-width conclusions can be false when candidate coverage is broken

Same exact box:
- broken subset: spec2 **76.2 TG**, spec4 **76.8 TG**;
- full head: spec2 **85.8 TG**, spec4 **87.7 TG**.

Interpretation:
- with an unhealthy drafter vocabulary, changing S barely matters because proposals already fail at the candidate-space level;
- S/occupancy experiments should start only after candidate coverage passes.

### NEW — expert-count reduction is not universally a decode win

Same author locally changed routed experts per token from 10 -> 8 for decode:
- **76.8 -> 76.7 TG** in Strata — effectively no gain;
- the author says their llama.cpp fork sees +10-18% from the same idea.

P51 interpretation:
- expert-byte reduction only helps if routed-expert execution is actually on the critical path;
- runtime scheduling/PCIe/CPU/verify/QSA costs can dominate;
- never transfer expert-count speed percentages across runtimes.

### NEW — real agent exact-prefix cache misses at 150K-168K

Source:
https://github.com/Niko1221/Strata/issues/143  
Created: **2026-09-29 14:47:46 UTC**.

OpenClaw + Strata 0.1.24 + IQ3_S / 262K / INT8 KV repeatedly reads essentially the full prompt:
- ~152K -> ~99 s prompt processing;
- later turns grow through **154K / 156K / ... / 168K**;
- ~168K still costs roughly **112 s** before generation.

The report does not establish whether Strata cache state is wrong. Exact-prefix reuse can be defeated when the client rerenders or mutates early prompt content.

P51 consequence:
cache/root systems need diagnostic observability, not only hit/miss:
- candidate checkpoint/root id;
- matched-prefix token count;
- first mismatch token position;
- mismatch class: token/template/image/steering/runtime identity;
- selected resume frontier;
- reuse rejection reason.

This lets client serialization drift be distinguished from snapshot corruption/state loss.

### NEW — mlx-serve adds artifact-producing coding-agent evaluation

Source:
https://github.com/ddalcu/mlx-serve/commit/99cfc74894a023670195010e1daa4403fb5c665c  
Timestamp: **2026-09-29 14:16:22 UTC**.

The new harness:
1. drives Pi against an mlx-serve arm;
2. asks it to build a real TypeScript/Vite artifact;
3. compiles and serves the result;
4. captures multiple rendered frames;
5. judges checkable task claims;
6. reports claim score, build status, turns, source lines, empty/timeout endings.

The repository recommends **>=5 runs per arm** for larger changes such as:
- quant packs;
- sampler changes;
- speculative acceptance;
- templates;
- KV quantization.

The stated rationale is highly relevant to P51: tok/s and MMLU can remain flat while an agent loops, quits early or builds a worse artifact.

P51 consequence:
- AA certification should retain paired low-level/source-vs-quant tests;
- add at least one repeated artifact-producing agent task when quant allocation, sampler, speculation, template or KV representation changes.

### NEW — agent-eval context-budget bug caught by the harness itself

The first harness revision hardcoded:
- 262,144 context;
- 32,768 output cap;
- a separate fixed compaction reserve.

On 32K/64K servers this caused HTTP 400s that looked like model/agent early exits.

The harness now derives Pi context and reserve from the server's advertised launch configuration.

P51 rule:
- client compaction/output budgets are part of the evaluation fixture;
- bind them to the server's actual context contract;
- do not score context-capacity errors as model-quality failures.

### NEW — mlx-serve qmm_int8 macOS 27 compile fix

Source:
https://github.com/ddalcu/mlx-serve/commit/0a6007fd79b748b1e57edf7ddf3bbc05a02fcc36  
Timestamp: **2026-09-29 14:16:55 UTC**.

The int8 QMM kernel now strips the right operand's address-space qualifier so MetalPerformancePrimitives cooperative-tensor code builds on macOS 27.

P51 interpretation:
- implementation compatibility only;
- no physical speed/quality target effect.

## RECOVERED CURRENT — M2 Max 96-GB Flash-Next Q4 receipt

Source:
https://www.reddit.com/r/LocalLLM/comments/1wsj8u0/qwen_38_27b_q4q6q8_vs_qwen_38_flashnext_on_a_96gb/

Reported MLX results:
- dense Qwen3.8-27B Q4: ~**21 TG**;
- Flash-Next REAP-288 Q4: ~**25 TG**;
- Flash peak RAM ~42.5 GB.

Useful as stronger-Apple family evidence that a pruned/quantized Flash artifact can outrun dense 27B on the same machine.

Limitations:
- M2 Max, not M1 Max;
- no genuine filled-128K denominator attached to the headline rate;
- no source-paired P51 quality qualification.

No target movement.

## KNOWN / checked again — MoEspresso exact M1 Max

The public MoEspresso thread/repo remains at the reproducible physical:
- 2021 M1 Max 32 GB;
- Flash-Next;
- roughly **12-15 TG** for the published V3 configuration.

The previously discussed separate comment claiming ~27 TG still has no published fork/settings/context denominator discoverable in this pass.

No dual-M1 target movement.

## Strict-window negative scan

From **2026-09-29 12:57:59 -> 15:03:35 UTC**:

- **TensorFold:** no strict-window commit after 0.3.6.3.
- **Strata:** no new strict-window engine commit after 0.1.24; issue #137 provides the important exact-card physical evidence.
- **oMLX:** only Qwen3-VL embedding/position work in-window; no new Flash TG receipt.
- **Ishizuki:** no commit.
- **llama.cpp:** no P51-relevant strict-window commit.
- **SGLang:** no strict-window performance/state commit after the already-promoted bootstrap series.
- **vLLM:** frontend/multimodal fixes only; no P51 target-hardware receipt.
- **mlx-serve:** agent-eval harness and qmm_int8 build fix; no new Flash physical benchmark.
- **DASLab / Hugging Face:** no new official Flash IQ3_S source-paired 32K/64K/128K/262K quality result found.
- **Exact dual M1 Max / TB4:** no new sustained filled-128K receipt.
- **M1 Max ~27 TG lead:** still not reproducible/public.

## Durable target change

### Strata IQ3_XXS ~128K TG confidence

Target remains:
- **78 TG @ ~128K**

Planning confidence:
- **~65% -> ~85%**

Reason:
- physical **79.7 TG @128K** on RTX 5070 Ti 16 GB / IQ3_XXS / Strata 0.1.24.

Stretch remains:
- **90 TG @128K**
- confidence unchanged at **~35-40%**.

### New speculative-production gate

Require:
- draft-vocabulary coverage for expected natural languages;
- coverage for code / JSON / tool-call token distributions;
- acceptance by workload/domain;
- full-head/fail-open fallback when subset coverage is inadequate.

Only tune verifier width after this gate passes.

## Canonical planning state after this pass

- Dual-M1 Flash-Next: **40 TG sustained @ genuine ~128K / 400 cold PP / ~70% >=40 TG**.
- Single-M1 dense27B: **25 TG / ~110 PP**.
- Strata IQ3_XXS 128K: **78 TG / ~85% confidence**.
- Strata IQ3_XXS PP: **1,500 / 1,400 / 1,300** at 32K / 64K / 128K.
- Strata IQ3_S PP: **1,450 / 1,250 / 1,200**.
- Remaining Strata TG rows unchanged.
- IQ3_XXS AA>=38: **~85%**.
- IQ3_XXS AA>=40: **~65%**.
- IQ3_S AA>=40: **~80%**.
- Swift lanes remain effective-task-throughput lanes, not physical TG multipliers.
- Persistent root / parked-agent targets unchanged.

## New hard boundary

**2026-09-29 15:03:35 UTC**
