# Project 51 design/source true-up — 2026-10-04 03:53 ET

**Targeted source audit, not a comprehensive strict-window search.**
The formal research hard boundary remains **2026-10-04 00:51:42 UTC**.

## Swift 1.5 Flash-Next conclusion

Swift 1.5 is now a **serious Project-51 model-level challenger**, because it attacks the user's actual bottleneck:
**time-to-correct-agent-result**, not merely raw decoder TG.

However, the current compact GSQ-RCO bucket is **not** promoted over DASLab IQ3_S.

Reason:
- Swift 1.5 BF16 has strong xhigh/coding/agent evidence;
- the compact Swift GSQ-RCO release currently provides **IQ3_XXS, IQ2_XS and Q2_0**, but **no IQ3_S**;
- its quant evaluation is short-context distribution/KLD work, not long-agent task evaluation;
- therefore Swift BF16 benchmark gains must not be silently attributed to the Swift IQ3_XXS quant.

Plain DASLab IQ3_S remains the canonical production artifact until the Swift compact build passes Project 51's
long-agent/xhigh suite.

## Source — Swift 1.5 BF16

Model:
https://huggingface.co/ukisai/Swift1.5-Qwen3.8-Flash-Next

Swift 1.5 is post-trained specifically for shorter reasoning and coding/agentic/long-horizon use.

Reported xhigh BF16 results versus Qwen3.8-Flash-Next BF16:

| Benchmark | Base | Swift 1.5 | Efficiency note |
| --- | ---: | ---: | --- |
| GPQA-Diamond | 89.80 | 89.60 | mean thinking 17,683 -> 7,823 (-55.8%); median -63.4% |
| MMLU-Pro | 87.75 | 87.20 | mean thinking -57.0% |
| C-Eval | 93.27 | 93.60 | mean thinking -44.1% |
| IFBench | 73.20 | 70.13 | mean thinking -46.9%; quality regression |
| AIME 2026 | 98.67 | 96.67 | mean thinking -31.3% |
| HMMT Nov 2025 | 98.00 | 97.33 | mean thinking -35.1% |
| LiveCodeBench v6 | 88.40 | **90.39** | mean thinking 17,833 -> 9,849 (-44.8%) |
| Terminal-Bench 2.1 | 67.64 | **69.66** | long-horizon agent score improves; total output-token behavior is mixed |

UkisAI summarizes the model as using **63.4% fewer median thinking tokens** with roughly **1.8x task-speedup** while
keeping xhigh accuracy loss below 1% in its aggregate framing.

Important nuance:
- this is not blanket benchmark parity;
- IFBench loses ~3 points;
- AIME loses 2 points;
- medium/low GPQA lose ~2.4-2.6 points;
- Project 51 is xhigh-only, so the xhigh behavior is the relevant production regime.

The model card's Terminal-Bench setup uses a real 89-task terminal-agent dataset with up to 131K server context and
long per-task limits. That makes it meaningful evidence for the user's agentic coding workload, though it remains
author-reported.

## Source — Swift 1.5 GSQ-RCO compact bucket

Bucket:
https://huggingface.co/buckets/adamm-hf/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF-bucket

The release reuses ISTA-DASLab per-tensor allocation profiles and applies Swift-specific GSQ refinement:
- joint attention/expert refinement;
- second expert-refinement pass;
- all 1,224 tensors checked and packaged reproducibly.

Available compact tiers:

| Tier | Combined GGUF | Development KLD vs Swift BF16 |
| --- | ---: | ---: |
| **IQ3_XXS** | **75.97 GB** | **0.240139** |
| IQ2_XS | 68.15 GB | 0.341275 |
| Q2_0 experimental | 66.55 GB | 0.424350 |

IQ3_XXS reporting KLD:
- English prose 0.1161;
- CodeParrot 0.1187;
- GSM8K-text 0.0868;
- German 0.1091;
- French 0.1336;
- Spanish 0.0737;
- Chinese 0.1741.

The release reports IQ3_XXS improves on its Swift starting quant in 6/7 measured domains by ~3-16%.
Relative to ISTA's corresponding IQ3_XXS, Swift's version is better on math-text and Chinese and within roughly
1-4% on the other reporting domains.

Critical limitations stated by the release itself:
- KLD comparisons are against each model's **own BF16 reference**;
- they are not direct capability rankings;
- measurements are at only **512-token context**;
- IQ3_XXS lacks the preregistered fresh-English holdout used for the smaller tiers;
- the tests **do not establish long-context quality**.

Therefore no direct inference is allowed from:
“Swift BF16 beats/equals base on coding/agent tasks”
to:
“Swift GSQ-RCO IQ3_XXS preserves those gains.”

That requires a real task suite.

## Project-51 rank after this audit

### Production baseline
**DASLab Flash-Next IQ3_S**

Why it stays first:
- stronger known quant-level task preservation;
- long-horizon SWE-bench evidence previously recovered;
- native262K retrieval/runtime evidence;
- ~3.5-bpw economics;
- paperniuk/ds4 has direct M1 IQ3_S kernel support.

### Challenger A
**Swift 1.5 GSQ-RCO IQ3_XXS**

Why it is compelling:
- underlying BF16 model is much more reasoning-token efficient;
- BF16 LiveCodeBench and Terminal-Bench improve versus base;
- the compact quant is still a GSQ-RCO refined allocation, not a naive low-bit build;
- if it preserves Swift's model-level behavior, actual agent task wall-clock may beat plain IQ3_S even at similar or
  slightly lower raw TG.

Why it is not promoted:
- lower precision than IQ3_S;
- no quant-level Terminal-Bench/SWE-bench/LCB rerun published here;
- no deep-context quant-quality validation;
- no exact M1-Max performance receipt yet.

### Challenger B
Swift IQ2_XS

This is interesting only after IQ3_XXS is qualified. The bucket calls IQ2_XS the standout of its smaller tiers,
including 5-11% lower KLD than ISTA's corresponding IQ2_XS on 7/8 reporting sets, but Project 51 does not need to
sacrifice this much precision before testing the stronger Swift IQ3_XXS arm.

## New metric: task-normalized agent throughput

Raw TG is insufficient when one model may think ~40-60% fewer tokens.

Add a separate Project-51 KPI:

**time-to-correct-result / useful task completion wall-clock**

For each source/quant:
- wall time to correct completion;
- total generated reasoning tokens;
- visible answer/tool tokens;
- number of tool calls;
- correction/retry count;
- raw TG/PP;
- final task success.

A 32-TG model generating half the reasoning tokens may be operationally much faster than a 40-TG model that
overthinks.

Do not replace raw TG/PP with this metric; report both.

## Required Swift qualification ladder

Before Swift can replace DASLab IQ3_S:

1. **Quant identity / runtime**
   - confirm paperniuk/ds4 can load the Swift GSQ-RCO IQ3_XXS formats without semantic conversion;
   - confirm MTP-head compatibility/presence and tokenizer/template identity;
   - exact serial-vs-MTP source gates.

2. **Quality**
   - LiveCodeBench v6 or frozen coding equivalent;
   - Terminal-Bench / Project-51 terminal-agent subset;
   - SWE-bench-style repo repair;
   - Playwright brownfield diagnosis/repair;
   - adversarial retrieval at 32/64/128/200/250K;
   - near ties / multilingual / parser-tool loops;
   - repeated xhigh trajectories.

3. **Efficiency**
   - reasoning-token distribution vs base IQ3_S;
   - task wall time, not only decoder TG;
   - MTP acceptance after Swift post-training.

4. **Memory/performance**
   - single M1 Max 64-GB 128/262K admission;
   - TG/PP ladder under the paperniuk engine;
   - if memory-limited, compare shallow spill vs dual-M1 split using the same architecture bakeoff as IQ3_S.

## License note

Swift adds an additional license layer. Its model card says individual/research/educational use is allowed, and
commercial use is free only for organizations up to US$1M gross annual revenue; above that, a separate Swift
Enterprise License is required.

That does not affect personal Project-51 research, but it may matter for future corporate deployment and should be
checked before workplace/commercial use.

## Canonical decision

- **DASLab IQ3_S remains production baseline.**
- **Swift 1.5 GSQ-RCO IQ3_XXS becomes the highest-priority model-level challenger.**
- Do not lower the native262K **35 TG / 400 PP** production target because of Swift.
- Add **task-normalized agent wall-clock** as a first-class KPI.
- If Swift IQ3_XXS preserves its BF16 coding/agent gains under quantization, it may win the actual user experience
  even without matching IQ3_S on every raw-quality proxy.

Strict search hard boundary remains **2026-10-04 00:51:42 UTC**.
