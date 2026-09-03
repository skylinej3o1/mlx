# Runtime Research Watch — 2026-09-03 19:50 ET

Scope: focused recurring pass after `RESEARCH-WATCH-2026-09-03-1725.md`, using branch checkpoint `c079ac2a69315526fde9d90e507ad65caa917ea0` / 2026-09-03 21:31:01 UTC as the hard freshness boundary.

The recurring targets remain intentionally narrow:

1. **Qwen3.8-Flash-Next on the exact planned 2x M1 Max 64 GB / Thunderbolt 4 cluster** — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, cache/state lifecycle, long-context prefill, and multi-agent pipeline filling.
2. **DeepSeek-V4-Flash-0731 / DS4 on the same 2x M1 Max 64 GB / TB4 cluster** — distributed decode, PP-vs-TP, Metal shard mapping, sparse-attention/activation economics, speculation policy, and multi-session bubble fill.
3. **Qwen3.8-27B on one M1 Max 64 GB** — exact/native verifier/runtime/kernel work and serving-memory behavior.
4. **Qwen3.8-27B on the RTX 5070 Ti 16 GB + 64 GB host rig** — low-bit fit, native MTP/DFlash, Blackwell verify kernels, and coding/tool throughput.

Other hardware is included only when it exposes a mechanism likely to transfer into one of those lanes. External research does not modify the certified exact-Q8 verifier state: P69B12 remains frozen/promoted and **P69B13 remains next using existing local profiling only**.

## Executive delta

1. **FRESH AND MATERIAL — llama.cpp #28349 finally wires Qwen3.8-Flash-Next QSA into the merged sparse Flash-Attention gather path.** `build_attn_qsa` now passes the indexer top-k width as `n_kv_max`; Metal/CUDA backends that support sparse FA can gather only the selected K/V rows instead of applying a sparse mask over the full cache. The path falls back to dense below 4096 KV. On an M5 Max with Flash-Next IQ4_XS, q8_0 KV, `-ub 2048 -b 2048`, the PR reports:

   | Test | Master | #28349 | Change |
   |---|---:|---:|---:|
   | pp2048 @ 65,536 | 388.1 | 702.2 tok/s | **+80.9%** |
   | pp2048 @ 131,072 | 340.0 | 588.7 tok/s | **+73.1%** |
   | tg32 @ 16,384 | 35.0 | 39.4 tok/s | noisy short-context uplift |
   | tg32 @ 32,768 | 34.5 | 35.1 tok/s | ~+1.7% |
   | tg32 @ 65,536 | 28.3 | 28.7 tok/s | ~+1.4% |
   | tg32 @ 131,072 | 20.6 | 20.7 tok/s | ~+0.5% |

   A more serving-like cold-prefill gate across three ~33K prompts improved **664 -> 760 tok/s (~+14.5%)**, and greedy output over a 36K prompt matched master. The test tree also contained #27836 MTP, but the author states MTP does not touch this path. This is the strongest fresh upstream evidence in this pass because it converts the already-known selected-KV architectural recommendation into an actual Qwen3.8-Flash-Next Metal code path with physical measurements.

2. **RECOVERED OLDER EVIDENCE — merged Metal sparse-FA backend #28098 is the dependency behind #28349 and also has strong DSv4 long-context measurements.** It merged earlier on 2026-09-03 but was absent from `RESEARCH-STATE.md` and the recent 13:30/15:30/latest chain checked in this pass. On an M2 Ultra running DeepSeek-v4 through llama.cpp, sparse FA left short-context behavior near parity but transformed long-context prefill:

   - 8K prefill: 323.58 -> 373.49 tok/s;
   - 16K: 248.67 -> 362.21;
   - 32K: 170.35 -> 347.85;
   - 65K: **107.08 -> 323.54 tok/s (~3.0x)**.

   Decode moved much less but improved at long context: 65K **20.36 -> 23.84 tok/s (~+17%)**. This is a llama.cpp/M2-Ultra DSv4 mechanism receipt, **not** an antirez/ds4 result and not an M1-Max forecast. It reinforces the same structural conclusion as #28349: sparse selected-KV attention is primarily a long-context prefill/scaling fix, with decode benefit depending on model/runtime shape.

3. **FRESH SUPPORTING CONFIRMATION — llama.cpp #27210 adaptive MTP received another mixed-workload datapost after the cutoff.** At the current PR head on Strix Halo / Qwen3.8-27B UD-Q4_K_XL, 16K, q4_0 KV, temp 0.2, adaptive [3..12] measured **18.61 tok/s code / 14.88 prose** at 61.7% / 41.9% acceptance, versus fixed n=4 at 17.65 / 13.98 and fixed n=12 at 17.72 / 11.79. These values are consistent with the adaptive-MTP evidence already recorded in the 15:30 pass, so this is confirmation rather than a new policy conclusion. Keep request/workload-adaptive speculation; do not transfer these absolute rates to the 5070 Ti.

4. **FRESH BUT GLM-ONLY — DS4 #964 added stronger quantized GLM-5.3-Flash Metal results, still with no DeepSeek-V4 gain.** New ABBA measurements on GLM-5.3-Flash-Q2 show roughly **+35-37% decode** from 2K-16K with flat prefill. A separate Q4 file with KDA/head BF16->Q8 also shows ~+35-37% decode, but quality was not yet tested. The PR continues to explicitly report DeepSeek V4 within ~0.5% of main. Treat this as exact-kernel/model-layout mining only; **do not import the GLM percentage into DS4-0731**.

5. **NO CHANGE — exact two-M1 Flash-Next ruler.** #27993 is still unchanged since 2026-08-30. The exact 2x M1 Max 64 GB / TB4 pair remains correctness-proven after #27960, but there is still no sustained physical Flash-Next TG and no published 115K follow-up.

6. **NO CHANGE — exact two-M1 DS4-0731 ruler and PP shard-map gate.** #922 remains unchanged since 2026-09-01: ~152 tok/s at 34K distributed prefill and successful 51K CLI generation, but no generated-token denominator / sustained TG. #957 remains unchanged with no physical post-coalescing Apple `--layers` throughput receipt. Therefore PP2 remains primary, but a fragmented-vs-coalesced shard-map gate remains mandatory before accepting any throughput number.

7. **NO CHANGE — 5070-Ti direct ruler and exact Apple 27B frontier.** `aipruner/qwen3.8-3bit-test-in-16GB-GPU` still has no push after 2026-08-20, so its Q3 + native-MTP ~97.2 tok/s mixed 8K mean / ~111-115 tok/s 24K tool-call result remains the direct GPU ruler. llama.cpp #28196 has no post-cutoff update beyond the already-recorded Blackwell wide-verify trace. `ARahim3/mlx-dspark` still has no code push after 2026-09-01 10:54 UTC, and Layr has no PR updated after this pass's cutoff.

8. **NO NEW single-M1 27B performance receipt.** oMLX #3334 was touched after the cutoff, but its measured state is unchanged: compiled B4 Flash-Next decode removes 77% of host dispatch / 18% of pure-step time on M3 Ultra while repeated HTTP A/B remains within 0.93-1.02x noise. No new M1-Max-64 physical rate appeared.

9. **BROADER WEB / COMMUNITY CHECK — no independent exact dual-M1 result surfaced.** Recent Reddit/Hugging Face/GitHub search returned single-Mac Flash-Next tuning, DGX/other-GPU results, and already-known M1/27B material, but no newer sustained 2x M1 Max Flash-Next or DS4-0731 decode receipt and no new exact 5070-Ti 27B result.

## Dual-M1 Flash-Next consequence — sparse QSA FA is now a mandatory baseline

This pass changes the **bring-up/test-plan priority**, not the decode forecast.

Before accepting any long-context or multi-agent dual-M1 Flash-Next measurement, qualify the #28349-equivalent path (or its merged successor):

- QSA top-k must be communicated to the backend as a real `n_kv_max` sparse bound;
- Metal must gather selected K/V rows rather than scanning/masking the full cache;
- verify output identity/correctness at 4K, 32K, 64K, and ~128K before throughput;
- run single-host M1-Max stage-local A/B first if possible, then the PP2 cluster;
- record cold prefill, cached continuation, B1 TG, and B2-B4 aggregate separately;
- include one long-prefill-arriving-while-other-agents-decode test, because faster sparse prefill may matter operationally by reducing the time a new agent monopolizes a stage even if steady TG barely moves;
- confirm each PP stage performs its selected-KV gather locally and TB4 still carries activations/compact metadata rather than dense cache material.

The physical M5 result makes the *mechanism* much more credible, but M5 bandwidth/compute and llama.cpp single-node scheduling do not calibrate M1-Max/TB4 numerically.

## Dual-M1 DS4 consequence

No forecast change. Keep the 17:25 plan:

- PP2/layer ownership primary, TP2 control;
- current-head AProjQ4 primary serving candidate with AProjQ8 control;
- qualify #957-style coalesced Metal mapping before throughput;
- classify speculation by prose/reasoning/code and keep a sticky low-lifetime-acceptance bypass;
- mine #28098/#964 for sparse-attention and exact-dispatch ideas, but require antirez/ds4 physical validation before crediting any speedup.

#28098 is particularly useful as cross-runtime evidence that dense full-cache attention can become a catastrophic long-context prefill shape on Apple, while sparse selected-KV execution largely removes that scaling penalty. It does not prove the same magnitude remains available in DS4, whose current kernels and data structures differ.

## RTX 5070 Ti 27B consequence

No new exact-rig rate. Preserve the current plan:

- 3-bit fit/residency remains first-order;
- native MTP is the direct working baseline;
- profile shallow/adaptive draft depths by workload;
- A/B the #26705-equivalent branchless Q4_K/Q5_K small-N verify path where the quant mix reaches it;
- separate target verify-width cost from repeated LM-head draft cost;
- keep code/tool lanes as the likely deep-speculation winner;
- do not infer 5070-Ti rates from PRO 6000 / R9700 / Strix Halo results.

## Single M1 Max 64 GB 27B consequence

No new physical M1 result and no P69 consequence. Continue to require bounded MTP/session state construction, no full-history replay merely to manufacture cache state, and process/system/transient memory telemetry in addition to MLX-active memory.

## Forecast consequence

**No Flash decode-band change.** #28349 materially improves long-context prefill architecture but does not materially move the long-context TG rows in its own M5 bench, so it would be incorrect to raise the current B1 or ~128K B1 confidence bands from this evidence.

Keep the current mature dual-M1 Flash-Next confidence bands:

### B1 short/medium

| Target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

### ~128K active-context B1

| Target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**. #28349 strengthens confidence that selected-KV sparse attention is the correct route to that prefill target on Apple, but the target remains unmeasured on the real dual-M1 topology.

## Sources

- llama.cpp #28349 — Qwen4Exp QSA sparse-FA wiring: https://github.com/ggml-org/llama.cpp/pull/28349
- llama.cpp #28098 — merged Metal sparse Flash Attention: https://github.com/ggml-org/llama.cpp/pull/28098
- llama.cpp #27210 — adaptive MTP: https://github.com/ggml-org/llama.cpp/pull/27210
- DS4 #964 — GLM-5.3-Flash exact Metal tuning: https://github.com/antirez/ds4/pull/964
- llama.cpp #27993 — exact 2x M1 Max Flash-Next correctness: https://github.com/ggml-org/llama.cpp/issues/27993
- DS4 #922 — exact 2x M1 Max DS4-0731 long-context thread: https://github.com/antirez/ds4/issues/922
- DS4 #957 — Metal layer-map span coalescing: https://github.com/antirez/ds4/pull/957
- exact 5070-Ti Qwen3.8-27B test repo: https://github.com/aipruner/qwen3.8-3bit-test-in-16GB-GPU
- Apple speculative-decoding reference: https://github.com/ARahim3/mlx-dspark
- Layr Qwen3.8 MTP challenge: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge
