# Runtime Research Watch — 2026-09-04 01:15 ET

Scope: focused recurring pass after `RESEARCH-WATCH-2026-09-03-2205.md`, using branch checkpoint `ba9277ad14259b8d0e745f8b07da6378010defda` / 2026-09-04 02:09:16 UTC as the hard freshness boundary.

The recurring targets remain narrow:

1. **Qwen3.8-Flash-Next on the planned 2x M1 Max 64 GB / Thunderbolt 4 cluster** — sustained decode, PP2/layer ownership, QSA/PLE, long-context prefill, compiled decode, cache/state lifecycle, MTP/verification, and multi-agent pipeline filling.
2. **DeepSeek-V4-Flash-0731 / DS4 on the same 2x M1 Max 64 GB / TB4 pair** — distributed decode, PP-vs-TP, Metal shard mapping, activation economics, multi-session fill, speculation policy, and portable Apple kernels.
3. **Qwen3.8-27B on one M1 Max 64 GB** — exact/native runtime work plus memory/admission behavior.
4. **Qwen3.8-27B on RTX 5070 Ti 16 GB + 64 GB host** — low-bit residency, native MTP/DFlash, MTP-head quantization, Blackwell verify kernels, context headroom, and coding/tool throughput.

External research still does not modify the certified exact-Q8 verifier state. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **FRESH / MATERIAL CORRECTION — oMLX #3334's reported +79.6% B1 full-model compiled-decode result did not reproduce.** A new M3 Ultra 512 GB reproduction used the production compiled-lane flag and a B1 single stream, with five 256-token rounds per arm and alternating eager/lane restarts. Results:

   | round | condition | eager | compiled lane | result |
   |---|---|---:|---:|---|
   | 1 | sibling instance serving ~35 req/min, TQ off, MTP d5 | 36.4 tok/s (second eager 29.2) | 44.5 | +22% vs first eager, but under external load |
   | 2 | sibling stopped, TQ off, MTP d5 | 46.1 | 45.5 | noise / no win |
   | 3 | sibling stopped, **TurboQuant on, MTP d6** | 46.7 | 43.7 | lane slightly slower |

   The author explicitly states: **the +79.6% B1 result was not reproduced**; both quiet rounds were within <=2.8% of each other. The large delta appeared only while another serving instance was active. The remaining setup differences from the earlier report are 512 GB vs 256 GB and end-to-end stream tok/s vs per-token-latency measurement.

   **Correction to the 22:05 note:** retain the directly controlled #3334 evidence — host dispatch 8.8 -> 2.0 ms (-77%) and in-process B4 step 54.5 -> 44.4 ms (-18%), plus bit-exact controlled-path tests — but **do not treat +79.6% B1 or +21.9% B2 as established serving gains**. Compiled decode remains a promising mechanism/instrument that needs a matched end-to-end M1 A/B, not a mature Hermes baseline.

2. **FRESH / MATERIAL STATUS DOWNGRADE — llama.cpp #28349 closed without merge.** The Qwen4Exp QSA `n_kv_max` wiring still has the physical M5 Max measurements recorded in the prior pass (65K pp 388 -> 702 tok/s; 131K 340 -> 589; three ~33K server prompts 664 -> 760; long-context TG nearly flat), but the PR was closed on 2026-09-04 04:04 UTC. The maintainer's reason was explicit: the path needs measurement on **many more devices** before being enabled.

   This is not evidence that the M5 measurement or sparse-FA mechanism is false. It does mean the formal project must stop describing #28349 as an upstream baseline. The correct status is:

   - merged **Metal sparse-FA backend #28098** remains valid infrastructure/mechanism evidence;
   - #28349's Qwen4Exp wiring is an **experimental patch with one strong M5 dataset**;
   - for dual M1, selected-KV sparse FA should be **A/B-qualified**, not assumed enabled or portable;
   - run output/retrieval exactness plus performance on M1 before promotion.

3. **FRESH / MATERIAL CAPACITY FINDING — oMLX #3425 isolates 7.06 GB of resident ANE-prefill memory that normal accounting cannot see.** The draft PR finds that ANE compiled prefill banks are charged to the neural-engine ledger and excluded from `phys_footprint`; RSS, `vmmap`, and MLX accounting therefore miss them and today's admission guard effectively charges zero. For Qwen3.8-27B at the default ANE fraction, the isolated resident bank total is **7.06 GB**:

   - 64 MLP programs at about 90 MB each;
   - 48 GDN programs at about 30 MB each.

   The compiled-program file size matched driver `wiredMemory` across tested geometries, making pre-load pricing possible. A simple formula gets >99% of the compiled size, though the PR currently uses the private ANE compiler for exact pricing and is draft because the maintainer trade-off is unresolved.

   This is highly relevant to a 64 GB M1 serving box even though the PR's failure example is a 32 GB machine: **ANE prefill consumes resident headroom that ordinary process/MLX telemetry can systematically hide.** It also explains why a model can look admissible by RSS and then evict/abort once ANE banks are live.

   Keep the prior exact-M1 field report separate: an M1 Max 64 GB operator measured ANE-on peak-memory increases of about **+9.54 to +9.64 GB** while gaining roughly 18-32% prefill. The new 7.06 GB figure is the isolated resident compiled-bank component, not the total observed ANE-on peak, so the two numbers are compatible rather than contradictory.

4. **FRESH SUPPORTING, STILL GLM-ONLY — DS4 #964 extended its exact Metal benchmark to 262K context.** On M3 Ultra / GLM-5.3-Flash-Q4_K, an 8-run drift-balanced interleave now reports:

   - decode +31.6% @2K, +30.4% @4K, +30.1% @32K, +29.5% @65K, +28.6% @131K, +27.3% @262K;
   - prefill effectively flat across the range;
   - first-token latency about 19-22% lower.

   The PR still explicitly reports **DeepSeek V4 Flash within 0.5% of main**. Therefore this remains a kernel-mining / measurement-method result and **does not move DS4-0731 performance expectations**.

5. **NO CHANGE — exact dual-M1 Flash-Next ruler.** llama.cpp #27993 is still unchanged since 2026-08-30. The exact 2x M1 Max 64 GB / TB4 pair remains correctness-proven after the earlier RPC fix, but there is still no sustained physical TG or published 115K completion/result.

6. **NO CHANGE — exact dual-M1 DS4-0731 ruler.** antirez/ds4 #922 is still unchanged since 2026-09-01: 34,384-token distributed prefill ~152 tok/s and successful long CLI generation, but no generated-token denominator / sustained TG. #957 remains open without a physical Apple post-coalescing `--layers` throughput result.

7. **NO CHANGE — direct RTX 5070 Ti speed ruler.** No newer exact 5070 Ti result appeared after the cutoff. `aipruner` Q3_K_XL + native-MTP remains the direct speed ruler (~97.2 tok/s mixed at 8K and ~111-115 tok/s tool-call generation at 24K). The GSQ-RCO lane from the 22:05 note remains the context/quality alternative, not a replacement speed ruler. llama.cpp #28196 has no post-cutoff update.

8. **NO CHANGE — MTP-head imatrix / exact verifier frontier.** llama.cpp #28351 remains draft/open with no post-cutoff measurement. It is still a future MTP-head quantization seam, not a current speed or quality result. P69 remains untouched.

9. **BROADER WEB / COMMUNITY CHECK — no new exact dual-M1 receipt.** Fresh search did not surface a sustained 2x M1 Max Flash-Next or DS4-0731 decode measurement. The strongest machine-specific Apple item remains the already-known M1 Max ANE field report; fresh public discussion around Qwen3.8-27B mainly concerns reasoning-token volume and newer-Mac serving rather than a new exact M1/TB4 performance ruler.

## Dual-M1 Flash-Next consequence — correct the promotion level

The previous note over-promoted two mechanisms. The corrected bring-up order is:

1. **Baseline first:** establish exact dual-M1 PP2/layer-owned correctness and sustained B1/B2/B4 without experimental sparse-FA wiring or compiled decode.
2. **Sparse-QSA experimental A/B:** apply the #28349-equivalent top-k->`n_kv_max` wiring only as a controlled patch. Validate 4K/32K/64K/~128K retrieval/output plus prefill/TG. Do not assume the M5 benefit transfers to M1.
3. **Compiled-decode experimental A/B:** run #3334-equivalent explicit-tensor-state compilation only after baseline is stable. Measure actual end-to-end B1/B2 and churn, not microstep/dispatch alone.
4. **Then combine:** only if each isolated mechanism passes, test sparse-QSA + compiled lane together and verify no state/cache interaction.

The architectural ideas remain good. What changes is **evidentiary status**: neither is now a mandatory upstream/mature baseline.

## Single M1 Max 64 GB 27B consequence — ANE admission must include hidden resident banks

For any ANE-enabled 27B run, record both visible and hidden capacity terms:

- process/system peak;
- MLX active peak;
- ANE compiled-bank estimate/measurement;
- total memory high-water under long prefill;
- whether the model is evicted/reloaded after ANE bank creation;
- context/headroom remaining after bank residency;
- ANE-off matched control.

For planning, do **not** treat `phys_footprint` or MLX-active memory as the complete resident cost. The fresh 7.06 GB bank figure should be treated as a first-order admission term until exact M1 measurements show a different compiled-bank geometry. The existing M1 field +9.5 GB total-peak delta remains the stronger machine-specific safety calibration.

## RTX 5070 Ti consequence

No change to the two-lane campaign:

- **speed lane:** Q3_K_XL + native MTP;
- **context/quality lane:** official GSQ-RCO IQ3_XXS-mtp first, IQ2_S-mtp and IQ3_S-mtp controls.

Keep #26705-equivalent small-N verify work and #28351 MTP-head imatrix work as separate future axes. No new exact 5070-Ti speed number justifies changing the ruler.

## DS4 consequence

No topology or forecast change:

- PP2/layer ownership primary;
- TP2 control;
- AProjQ4 primary serving candidate with AProjQ8 same-checkpoint control;
- coalesced Metal `--layers` mapping prerequisite;
- workload/request-adaptive speculation;
- GLM #964 techniques are only mining candidates until DeepSeek-V4 itself moves under physical testing.

## Forecast consequence

**No numerical change.** In fact, this pass increases caution around two previously promoted Flash implementation paths while adding useful capacity accounting for 27B ANE serving.

Keep the mature dual-M1 Flash-Next confidence bands unchanged:

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

The mature-system target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, but sparse-QSA wiring and compiled low-occupancy decode must now be treated as experimental A/B lanes until they reproduce on M1-generation hardware and under real serving metrics.

## Sources

- oMLX #3334 — compiled Qwen4Exp decode and fresh B1 non-reproduction: https://github.com/jundot/omlx/pull/3334
- llama.cpp #28349 — Qwen4Exp sparse-FA wiring, now closed without merge: https://github.com/ggml-org/llama.cpp/pull/28349
- llama.cpp #28098 — merged Metal sparse Flash Attention backend: https://github.com/ggml-org/llama.cpp/pull/28098
- oMLX #3425 — ANE prefill-bank admission pricing / hidden resident memory: https://github.com/jundot/omlx/pull/3425
- M1 Max 64 GB ANE field report: https://www.reddit.com/r/oMLX/comments/1vumbhw/experience_with_ane_on_m1_max_64gb/
- DS4 #964 — GLM-5.3-Flash exact Metal tuning: https://github.com/antirez/ds4/pull/964
- llama.cpp #27993 — exact 2x M1 Max Flash-Next RPC correctness: https://github.com/ggml-org/llama.cpp/issues/27993
- DS4 #922 — exact 2x M1 Max DS4-0731 long-context distributed thread: https://github.com/antirez/ds4/issues/922
- DS4 #957 — Metal `--layers` map-span coalescing: https://github.com/antirez/ds4/pull/957
- llama.cpp #28196 — Blackwell Qwen3.8-27B MTP/verify trace: https://github.com/ggml-org/llama.cpp/issues/28196
- llama.cpp #28351 — MTP-aware imatrix collection: https://github.com/ggml-org/llama.cpp/pull/28351
