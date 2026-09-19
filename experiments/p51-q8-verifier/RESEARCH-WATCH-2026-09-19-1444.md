# External runtime watch — 2026-09-19 14:44 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-19 17:24:44 UTC` through the user-message cutoff `2026-09-19 18:44:41 UTC`.

The repository had already advanced beyond the boundary quoted in the request: the prior LATEST covered `2026-09-19 15:55:17 UTC -> 17:24:44 UTC`. Per the Project 51 README, this pass therefore starts from the repository's actual hard boundary and does not double-count the earlier window.

PRs, issues, comments/reviews, and default-branch commits were screened across DS4, vLLM, oMLX, mlx-serve, llama.cpp, Splash, Kadir's benchmark/fork, and current Qwen3.8-Flash-Next quant/community surfaces. Evidence time means the substantive source/measurement timestamp, not crawler, merge, rebase, label, or bot activity.

## Executive result

**No exact dual-M1-Max/TB4 custom-quant Flash-Next TG or PP receipt appeared. Numeric targets and confidence remain unchanged.**

Current Flash-Next plan remains:
- >=35 TG @ ~128K: **~85%**
- **>=40 TG @ ~128K: ~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20%**
- **400 cold PP: ~70%**
- deployment design: **custom ~4.6-4.9 hot-trunk BPW**
- oQ5e: quality/certification comparator
- oQ4e: aggressive speed comparator
- PLE/ngram and MTP precision tracked separately.

The most useful new evidence is an exact **M1 Max 64 GB** rerun on DS4 #1056. It shows that Qwen4Exp/Flash decode-side work can produce repeatable low-to-mid-teens percentage gains on M1 while simultaneously exposing a context-sensitive MTP weakness: the deepest tested prompt lost the earlier acceptance gain even though ordinary target decode remained materially faster. That is exactly the sort of verifier/predictor interaction Project 51 must qualify before assigning PP2/MTP credit at ~128K.

A fresh llama.cpp issue also reports a Qwen3.8-Flash-Next MTP load regression after a runtime upgrade. It has no Apple measurement or diagnosed root cause yet, so it changes qualification rules, not targets.

## NEW — exact M1 Max 64 GB DS4 #1056 rerun: decode gains survive, deep MTP acceptance does not

Source: https://github.com/antirez/ds4/pull/1056#issuecomment-5744306216  
Substantive timestamp: **2026-09-19 18:21:45 UTC**.

Hardware/workload:
- Apple **M1 Max 64 GB**
- Qwen3.8-Flash-Next Q2 GGUF
- resident path for the main A/B
- base `antirez/main@8db1d1d`
- optimized `#1056@11811b9`
- separate worktrees/binaries
- `--temp 0 --nothink`
- effective prefill chunk explicitly pinned in both arms through both the CLI and `DS4_QWEN4_PREFILL_CHUNK`
- ABBA/BAAB; four observations per normal cell, two for deep/streaming/chunk-128 cells; medians.

### Resident performance

| Workload | MTP | PP base -> PR | TG base -> PR | Acceptance |
|---|---|---:|---:|---:|
| 575-token prompt | off | 232.1 -> 246.3 (**+6.1%**) | 26.04 -> 30.00 (**+15.2%**) | — |
| 575-token prompt | on | 232.0 -> 231.4 (-0.2%) | 26.20 -> 30.25 (**+15.5%**) | 16/33 -> 18/32 |
| 5,760-token prompt | off | 274.8 -> 289.2 (**+5.2%**) | 24.48 -> 27.94 (**+14.1%**) | — |
| 5,760-token prompt | on | 274.8 -> 269.3 (-2.0%) | 28.12 -> 32.51 (**+15.6%**) | 52/72 -> **56/67** |
| 5,760, chunk 128 | off | 128.5 -> 137.3 (**+6.9%**) | 24.55 -> 27.92 (**+13.7%**) | — |
| 17,408 / ctx 32,768 | off | 273.9 -> 287.4 (**+4.9%**) | 23.93 -> 27.16 (**+13.5%**) | — |
| 17,408 / ctx 32,768 | on | 273.6 -> 267.6 (-2.2%) | 25.09 -> 27.02 (**+7.7%**) | 47/79 -> 46/78 |

The reported decode ranges do not overlap in any cell.

This is **exact target-generation hardware and model-family evidence**, but it is not the Project 51 deployment quant, not ~128K, not dual-M1/TB4, and not a PP2 measurement. The Q2 lane is materially more aggressive than the intended ~4.6-4.9 hot-trunk deployment design.

### Deep MTP caveat

The same 17,408-token MTP workload had previously measured:
- base: **47/79 accepted (59.5%), 25.09 TG**
- earlier PR `04c0867`: **51/72 (70.8%), 28.41 TG**
- current `11811b9`: **46/78 (59.0%), 27.02 TG**.

So the deepest MTP-on gain fell from about **+14.8% to +7.7%**, and acceptance returned to roughly the base level. Meanwhile the 5,760-token acceptance improved to **56/67 = 83.6%**.

Interpretation: verify/predictor quality is **context- and boundary-sensitive**. A target-path optimization can remain a real speed win while changing draft/target agreement enough to erase speculative gains at another context length.

### Project 51 action

Strengthen the MTP/verify qualification matrix:
1. report **target-only TG, MTP TG, accepted/attempted proposals, tokens/cycle, verify width/depth and rollback count** together;
2. run at multiple prompt depths, including a deep-context cell, before crediting an MTP-side change;
3. for PP2, record per-stage proposal/verify occupancy and bubble time so a single-node acceptance change is not mistaken for a pipeline gain;
4. keep QSA/sparse-boundary arithmetic changes coupled to MTP acceptance checks.

Target effect: **no numeric change**. This is favorable exact-M1 mechanism evidence, but the deep-MTP regression offsets any case for raising confidence before ~128K dual-node data exists.

## NEW — chunked prefill can be made bit-identical to the unchunked M1 reference

The same DS4 #1056 rerun closes an important correctness ambiguity.

For a 5,760-token prompt, with one-pass chunk 8192 as the reference:
- base @8192: max abs logit delta **0**
- base @2048: **0.594551**
- base @128: **1.132671**
- PR `11811b9` @8192: **0.000000**
- PR @2048: **0.000000**
- PR @128: **0.000000**.

At 17,408 tokens the PR is internally invariant across chunk 8192/4096/2048/128 (**spread 0.000000**) while base spans **1.099256**, but an absolute one-pass reference at that length could not be obtained because both base and PR hit a 64-GB Metal command-buffer OOM when the whole prompt was forced into one chunk. SSD streaming also produced identical output at chunk 2048 and 8192.

Project 51 rule:
- when feasible, qualify chunked prefill against an **unchunked reference**, not merely against another chunk size;
- when an unchunked reference cannot fit, cross-chunk invariance is useful evidence but **not absolute parity proof**;
- effective resolved chunk size remains benchmark identity.

This matters to the 400-PP program because PP gains must not come from a numerically different chunk-boundary path.

## NEW — llama.cpp #29148 reports a fresh Flash-Next MTP load regression

Source: https://github.com/ggml-org/llama.cpp/issues/29148  
Created: **2026-09-19 17:35:06 UTC**.

Reported environment:
- llama.cpp build 11046 / commit `60081bb2b`
- Linux x86_64 / Vulkan
- AMD Strix Halo 128 GB
- Qwen3.8-Flash-Next Q4_K_XL
- upgrade from server-vulkan-b10975 to b11046
- reporter identifies **b10991** as the first bad build.

The model no longer loads with MTP. The issue currently contains only a context-overflow warning and no diagnosed root cause, patch, or performance result.

Classification: **NEW runtime-regression evidence; non-Apple, unresolved.**

Project 51 action:
- keep a minimal Flash + MTP **load/graph-build smoke test** pinned to every candidate runtime SHA before throughput work;
- do not treat MTP support as preserved merely because target-only Flash still loads;
- continue the existing MTP ABI/schema-parity gate across trunk changes.

No target effect.

## NEW transfer-only — async overlap must be verified from the actual timeline, not inferred from enqueue order

Source: https://github.com/ggml-org/llama.cpp/pull/28414#issuecomment-5743936762  
Substantive timestamp: **2026-09-19 17:30:37 UTC**.

A ROCm follow-up to expert-weight lookahead prefetch reports:
- mmap/pageable host path, 27K / 64K prefill: **1014 / 1079 PP stock -> 1319 / 1292 PP with 3 slots**
- pinned host memory: **1459-1532 / 1484 PP**
- decode unchanged.

GPU timestamps showed an event wait that logically targeted an earlier copy could still be delayed behind a later pageable async copy when the wait was issued after the later enqueue. Pinned memory avoided the behavior.

Classification: **NEW non-Apple transfer evidence.**

Project 51 relevance is methodological, not numerical:
- PP2/TB4/SSD overlap claims require actual command-buffer/event timelines;
- record whether waits fence the intended operation or an evolving queue tail;
- do not infer useful overlap from “asynchronous” API use alone.

No Flash target credit.

## NEW side lane — DS4 has a live Bonsai-2 PQ2_0 prototype, not Flash-Next evidence

Source: https://github.com/antirez/ds4/issues/1075#issuecomment-5744427436  
Timestamp: **2026-09-19 18:40:48 UTC**.

The author points to a `ternary-bonsai-2-support` branch and says only the small **Ternary-Bonsai-2-27B-PQ2_0.gguf** model is currently supported.

This is relevant to the separate 27B extreme-compression/ternary lane, not to the Flash-Next deployment quant or dual-M1 target. No target change.

## Checked surfaces / negative results

- **vLLM:** no new qualifying verify/QSA measurement after the prior boundary. #57704 remains scaffolding: its shard-scoring and top-k helpers are still placeholders and its accuracy/throughput tables remain TBD. #57703 received no new substantive post-boundary evidence; later activity was duplicate/merge bookkeeping.
- **oMLX:** no strict-window Flash performance commit/PR/issue. Updates in the interval were unrelated cluster model classification, keepalive, and admin UI work.
- **mlx-serve:** no strict-window Flash performance change; activity was MiniCPM-V 4.6 support and docs.
- **llama.cpp default branch:** no qualifying Flash/Metal commit in the interval. #29094 reports a **+3.0% M5 Pro** FWHT butterfly micro-change, but it is M5-only and not Flash TG/PP evidence; #29095 adds wider FWHT shapes without a strict-window performance receipt.
- **Splash:** no commit/issue/PR activity in the window. The prior M3+ hardware-floor correction stands; no older-Apple/M1 backend or M1 benchmark appeared.
- **Kadir qwen38-mac-fast + llama.cpp fork:** no commit/issue/PR activity in the window. The 23.31 TG @117.8K M1 receipt remains the relevant frozen single-M1 anchor.
- **current Flash quant/community sweep:** current oQ6e/oQ8e MTP model cards and same-day community posts were visible, but no source with a precise substantive timestamp after 17:24:44 UTC produced a controlled dual-M1/custom-quant receipt. Older/current-day material was therefore not reclassified as strict-window NEW.
- **Unsloth:** no post-boundary mechanism beyond the already-recorded v0.1.811-beta MTP restoration story.
- No new exact ~128K M1 MTP acceptance receipt.
- No direct PP2 occupancy or TB4 verify-wave receipt.
- No new multi-row verification A/B on Apple M1.

## Target / confidence decision

**No change.**

Flash-Next dual-M1:
- >=35 TG @ ~128K: **~85%**
- **>=40 TG @ ~128K: ~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20%**
- **400 cold PP: ~70%**.

Why:
- DS4 #1056 adds strong exact-M1 evidence that model-specific Qwen4Exp work can produce real ~13-16% target-decode gains in several cells.
- The same exact-M1 run shows deep MTP acceptance can move backward enough to reduce the speculative gain materially.
- There is still no direct ~128K MTP receipt on the target quant and no dual-M1 PP2 occupancy measurement.
- Splash remains M3+ methodology evidence, not an M1 kernel ruler.
- No result in this interval changes the fit/capacity assumptions of the custom ~4.6-4.9 hot-trunk design.

## New / strengthened qualification rules

1. **MTP must be depth-qualified:** medium-context acceptance is not enough; include a deep-context cell.
2. **MTP counters travel with TG:** accepted/attempted proposals, tokens/cycle, verify width/depth and rollback count are part of benchmark identity.
3. **Chunked PP needs parity:** compare to an unchunked reference when feasible; otherwise label cross-chunk invariance separately from absolute correctness.
4. **PP2 occupancy must be explicit:** measure per-stage proposal/verify occupancy and bubbles before assigning distributed speculative credit.
5. **Async overlap requires timeline proof:** command-buffer/event ordering must show that intended work actually overlaps.
6. **MTP load smoke before perf:** target-only load success does not certify the draft/verify side after a runtime update.
7. Existing QSA/KV common-prefix reuse, row-local sparse selection, fast-path engagement, fusion-concurrency, MTP ABI/schema parity, draft-fit accounting, exact runtime SHA, and long-context parity rules remain.

## Hard freshness boundary

`2026-09-19 18:44:41 UTC`
