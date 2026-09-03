# Runtime Research Watch — 2026-09-03 15:30 ET

Scope: **narrow focused pass** after `RESEARCH-WATCH-2026-09-03-1330.md`, using branch checkpoint `a11fbb354a8643007a2b203b31f5411e8e7e1065` / 2026-09-03 17:35:38 UTC as the hard freshness boundary.

The watch target is now explicitly constrained to:

1. **Qwen3.8-Flash-Next on the exact planned 2x M1 Max 64 GB / Thunderbolt 4 cluster** — sustained decode, PP2/layer ownership, MTP/verification, QSA/PLE placement, cache/state lifecycle, multi-agent pipeline filling, and any Apple/Metal mechanism that plausibly transfers to this topology.
2. **DeepSeek-V4-Flash-0731 / DS4 on the same 2x M1 Max 64 GB / TB4 cluster** — especially physical distributed decode, PP-vs-TP, Metal layer mapping, activation transport, multi-session bubble fill, and portable pre-M5 Metal kernels.
3. **Qwen3.8-27B on one M1 Max 64 GB** — exact/native verifier/runtime/kernel work and operational memory behavior.
4. **Qwen3.8-27B on the RTX 5070 Ti 16 GB + 64 GB host rig** — practical low-bit fit, native MTP/DFlash, verify economics, CUDA/Blackwell kernel behavior, and coding/tool throughput.

Other hardware is included only when it exposes a mechanism likely to transfer into one of those four lanes. The certified exact-Q8 verifier project remains separate: P69B12 stays frozen/promoted and **P69B13 remains next using existing local profiling only**.

## Executive delta

1. **NEW — Blackwell Qwen3.8-27B MTP tracing identifies a concrete verify-kernel target relevant to the RTX 5070 Ti.** A fresh llama.cpp #28196 native-Linux run on an RTX PRO 6000 Blackwell Server Edition (sm_120) used the exact Qwen3.8-27B-0814 Q4_K_M blob and upstream `draft-mtp` depth 4. Median serving throughput moved **67.7 -> 119.8 tok/s (1.77x)** with 0.47 accepted/drafted overall. Code prompts gained **2.18-2.38x** at 0.68-0.75 acceptance, while prose gained 1.30-1.41x at 0.29-0.34 acceptance. The important new part is the trace: five-column target verification runs the large quantized matvecs at only **66-71% of the bandwidth bound versus ~84% for the single-column draft path**; this contributes about 5 ms of penalty per MTP step, with another ~2.8 ms spent on four single-column LM-head draft passes. GDN itself was only ~1.5% of kernel time in that trace. Absolute PRO-6000 rates do not transfer to the 5070 Ti, but the **small-N wide-verify `mmvq` path and repeated LM-head passes are now concrete Blackwell optimization targets** rather than a vague acceptance problem.

2. **NEW — oMLX #3330 removes a pathological full-history MTP-terminal replay that is especially important for a 64-GB M1 serving lane.** A fresh signed update found that when the live terminal cache proof missed, a completed Qwen3.8-27B request could replay its entire 10K/30K prompt solely to manufacture a cache candidate, producing **159-236 GB transient attention graphs** and apparent stream freezes. The new path writes completed 4K blocks through the existing hot/SSD cache during normal prefill, never replays the completed request, and lets idle target-only keepwarm reconstruct only a bounded suffix under an explicit proof. Physical validation is M3 Ultra, not M1 Max: a 33,282-token image follow-up reused 28,672 tokens, generated 96 tokens at 68.8% acceptance, settled at 23.9 GB, then reconstructed an 801-token tail in 3.09 s and served the following text turn in 0.39 s model / 0.71 s visible TTFT. This is **capacity/lifecycle mechanism evidence**, not an M1 Max TG result, but it directly attacks a transient allocation shape that would be disastrous on 64 GB.

3. **NEW SUPPORTING EVIDENCE — adaptive MTP continues to beat one fixed depth across mixed Qwen3.8-27B workloads.** Fresh llama.cpp #27210 testing on other hardware shows the same workload split seen in the Blackwell trace: adaptive depth preserves prose while climbing on code/high-acceptance runs. One Strix Halo run measured adaptive [3..12] at 18.61 tok/s code / 14.88 prose versus fixed depth 4 at 17.65 / 13.98 and fixed depth 12 at 17.72 / 11.79; a separate R9700 user reports roughly 72 tok/s code / 34 prose with adaptive versus 53 / 34 using static depth 3. These are not 5070-Ti measurements, so do not use the absolute numbers as a rig forecast. They strengthen the policy already suggested by the exact 5070-Ti receipt: **MTP depth should be workload/acceptance adaptive, with deep drafts reserved for code/tool lanes that actually accept them.**

4. **NEW APPLE-METAL METHOD LEAD, BUT NOT A DS4 SPEED RESULT — DS4 #964 gets +30% GLM-5.3-Flash decode on M3 Ultra while explicitly leaving DeepSeek V4 unchanged.** The new PR stages indexed-attention rows for all heads, pipelines weighted sums, and adds several exact producer/epilogue fusions. GLM-5.3-Flash decode rises about **30-32%** from 2K through 16K context with byte-identical greedy output and flat prefill. However, the PR explicitly reports **DeepSeek V4 Flash within 0.5% of main** on prefill/decode. Therefore this is only a Metal optimization-methodology lead: it demonstrates that exact indexed-attention staging and dispatch fusion can still uncover large Apple decode wins, but **none of the measured gain transfers to DS4-0731 today**.

5. **NO CHANGE — exact dual-M1 Flash-Next calibration.** llama.cpp #27993 remains closed with its last update on 2026-08-30. The exact 2x M1 Max 64 GB / TB4 configuration is still known to execute Flash-Next correctly after #27960, including Q8 KV, but there is still **no sustained physical decode TG receipt** and no completed published 115K needle follow-up. #28330's unused-indexer-V-cache removal has no new post-boundary measurement; #28243 Flash-Next MTP likewise has no fresh post-boundary Apple result.

6. **NO CHANGE — exact dual-M1 DS4-0731 calibration.** DS4 #922 remains unchanged since 2026-09-01: exact two-M1 34,384-token distributed prefill is still ~152 tok/s and 51K CLI generation works, but no generated-token count / sustained 0731 TG has been posted. DS4 #957 remains open with no physical post-fix Apple `--layers` throughput receipt. DS4 #861 had no update after this pass's boundary. Therefore the preferred topology remains **PP2/layer ownership first, TP2 as a control**, with a mandatory coalesced Metal shard-map gate before interpreting PP performance.

7. **NO CHANGE — exact 5070-Ti direct receipt and exact Apple verifier frontier.** `aipruner/qwen3.8-3bit-test-in-16GB-GPU` has not been pushed since 2026-08-20, so the existing exact-GPU receipt remains the current direct ruler: Q3_K_XL + native MTP at 24K, ~97.2 tok/s four-workload mean at 8K and ~111-115 tok/s tool-call generation at 24K, with the tested IQ4_XS spilling catastrophically. `ARahim3/mlx-dspark` still has no code push after 2026-09-01 10:54 UTC, and the Layr Qwen3.8 MTP challenge has no PR updated after the freshness boundary.

8. **BROADER WEB CHECK — no new exact two-M1 receipt surfaced.** Fresh web/Reddit/Hugging Face search did not produce a newer physical 2x M1 Max Flash-Next or DS4-0731 sustained-decode result. Single-Mac 27B posts and other-GPU model cards continue to appear, but none replace the exact cluster calibration gap.

## RTX 5070 Ti consequence — the verify path is now a more specific tuning target

The user's direct 5070-Ti Q3 + native-MTP result remains the primary machine-specific ruler. The fresh sm_120 trace adds a useful *mechanistic* target because the RTX 5070 Ti is also Blackwell-class:

- qualify `draft-mtp` with shallow/adaptive depths rather than a globally deep fixed N;
- record acceptance by workload class, not only one aggregate number;
- profile the target verify pass at widths roughly 3-5, especially quantized `mul_mat_vec_q` / `mmvq` occupancy and bandwidth efficiency;
- separate verify-width cost from repeated LM-head draft cost;
- treat code/tool traffic as the most likely high-payoff lane because the fresh trace physically showed 0.68-0.75 acceptance and >2x speedup there;
- do not assume an optimization that raises acceptance alone will improve wall time if the small-N verify kernel remains inefficient;
- keep the current 3-bit target fit advantage first-order on 16 GB VRAM: a faster verify kernel is irrelevant if a larger target spills.

The PRO-6000 absolute number must **not** be converted into a 5070-Ti forecast. The direct 5070-Ti result remains ~97 tok/s mixed / ~111-115 tool-call TG in the currently measured lane.

## Single M1 Max 64 GB 27B consequence — memory lifecycle matters as much as nominal model fit

The fresh oMLX cache fix strengthens one operational rule for the M1 Max 64 GB lane: **never manufacture reusable MTP/session state by replaying a completed long prompt when equivalent block state already passed through the engine.** A 159-236 GB transient graph shape is acceptable on neither a 64-GB workstation nor a multi-agent server.

For future M1 Max qualification, record:

- process/system peak in addition to MLX-active memory;
- transient peak during MTP terminal publication and cache reconstruction;
- whether the path replays full history or reconstructs only a bounded suffix;
- hot-cache and SSD write-through cost;
- TTFT after a rewritten/extended tool turn;
- whether MTP remains active after the cache handoff without re-priming the entire history.

This serving-side work remains **separate from P69**. External cache/MTP lifecycle fixes do not select the next exact verifier kernel candidate.

## Dual-M1 Hermes consequence

No topology change.

The preferred cluster plan remains:

- asymmetric resident **PP2 / layer ownership** as the primary execution topology;
- TP2 only as a falsification/control benchmark unless a new physical result overturns the communication argument;
- keep GDN/recurrent, QSA/indexer and PLE state stage-local where possible;
- move activations and compact metadata over TB4, not recurrent snapshots every token;
- 3-4 logical persistent Flash-Next agents, normally 2-3 compute-active slots;
- use independent requests to fill pipeline bubbles rather than expecting naive layer splitting to double B1;
- exact hot-session ownership, suffix-local reconstruction, rewind/cancellation checkpoints and durable SSD cold state;
- workload-gated speculation only after exactness + wall-clock qualification on the real dual-node implementation;
- reject fragmented Metal `--layers` mappings before any distributed benchmark is accepted.

DS4 #964 is interesting mainly as a reminder that a large exact Apple decode win can still hide in a model-specific indexed-attention/dispatch implementation. Because DeepSeek V4 itself was unchanged in that PR, it does **not** justify importing a +30% expectation into DS4 or Flash-Next.

## Forecast consequence

**No change.** The missing evidence is still exactly the same physical ruler: sustained Qwen3.8-Flash-Next decode on the real 2x M1 Max 64 GB / TB4 pair, plus a sustained DS4-0731 decode measurement on that pair.

Keep the current Flash-Next confidence bands unchanged:

### Mature dual-M1 Flash-Next B1

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

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, with multi-agent pipeline filling doing much of the practical throughput work. That remains a target, not a dual-M1 measurement.

## Sources

- llama.cpp #28196 — Qwen3.8-27B Blackwell MTP/verify analysis: https://github.com/ggml-org/llama.cpp/issues/28196
- llama.cpp #27210 — adaptive MTP: https://github.com/ggml-org/llama.cpp/pull/27210
- oMLX #3330 — exact prompt-tail / MTP terminal persistence: https://github.com/jundot/omlx/pull/3330
- DS4 #964 — exact GLM-5.3-Flash Metal decode tuning (DeepSeek V4 control unchanged): https://github.com/antirez/ds4/pull/964
- llama.cpp #27993 — exact 2x M1 Max Flash-Next correctness: https://github.com/ggml-org/llama.cpp/issues/27993
- llama.cpp #28330 — unused Qwen4Exp indexer V-cache allocation: https://github.com/ggml-org/llama.cpp/pull/28330
- llama.cpp #28243 — Flash-Next MTP: https://github.com/ggml-org/llama.cpp/pull/28243
- DS4 #922 — exact 2x M1 Max 0731 long-context distributed thread: https://github.com/antirez/ds4/issues/922
- DS4 #957 — Metal `--layers` map-span coalescing: https://github.com/antirez/ds4/pull/957
- DS4 #861 — distributed PP/TP/batching work: https://github.com/antirez/ds4/pull/861
- Exact 5070-Ti direct 27B test repo: https://github.com/aipruner/qwen3.8-3bit-test-in-16GB-GPU
- Apple speculative-decoding reference: https://github.com/ARahim3/mlx-dspark
- Layr Qwen3.8 MTP challenge: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge
