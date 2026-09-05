# External runtime research watch — 2026-09-05 15:12 ET

Starting freshness boundary: `10523b862796ac4d53a034305e1d307075fd45b8` / 2026-09-05 16:04:52 UTC.

This pass is **material but does not move any canonical TG / PP target or confidence**. The strongest fresh evidence is about real agent-turn prefix-cache effectiveness, Qwen3.8-27B MTP-head/vocabulary tradeoffs, and an exact CUDA decode-allocation optimization in ds4. A newly reported ggml allocator identity failure is worth monitoring as a correctness seam, but it is not yet a Qwen3.8-Flash-Next / Apple reproduction.

Canonical planning centers remain:

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

`RESEARCH-TARGETS.md` remains unchanged and authoritative. Numbers below from other hardware are evidence for mechanisms/test ordering only unless explicitly described as an exact-rig receipt.

---

## Fresh / material

### oMLX #3462 — Flash agent sessions can have a cache that is enabled but operationally almost useless

Created 2026-09-05 17:16:37 UTC. Physical report: M3 Ultra 512 GB, oMLX 0.6.4, Qwen3.8-Flash-Next 180B 5.5-bpw oQ5, GatedDeltaNet / ArraysCache, MTP enabled.

The report isolates a bad interaction between the 2,048-token ArraysCache boundary and coding-agent turns with huge prompts plus short completions. Boundary state is captured only when the running token count lands exactly on a multiple of 2,048.

Measured over one long-running agent session:

- 540 requests;
- 1,000 cache-store skips versus 461 successful stores: **68% skip rate**;
- all skips reported `boundary_snapshot_unavailable`;
- 661/1,000 skips had zero available boundaries and 325/1,000 had one;
- median skipped sequence was 123,961 tokens;
- average prompt/completion was 99,246 / 535 tokens;
- prompts grew about 94K -> 148K while reusable prefix stayed pinned at **12,288 tokens**;
- the consequence was about **80K tokens re-prefilled per turn**, reported around 187 s at the measured 474 tok/s prefill rate.

MTP makes exact-boundary landing still less likely because one scheduler step can advance by more than one token. The report measured median 2.25 tokens/step across 2,356 generations. A tiny n=2-per-arm 5K-output control observed 2/2 captured boundaries without MTP versus 1/2 then 2/2 with MTP while decode was 18.3 versus 39.8 tok/s. Treat that boundary-count A/B as suggestive only; MTP clearly should not be disabled merely to improve capture probability.

The 2,048-token prefill step is described as part of the recurrent-state correctness invariant, so simply lowering it is not a safe tuning recommendation.

**Promotion for the appliance:** `prefix cache enabled` is no longer an adequate qualification result. Add an **agent-turn cache-capture efficacy gate** that records, over a growing real session:

- eligible store attempts / successful stores / skips and reason;
- reusable-prefix frontier after every turn;
- reused tokens and fresh prefill tokens per request;
- warm-turn PP / TTFT / wall time;
- completion length and MTP tokens-per-step;
- whether the reuse frontier advances under repeated short generations.

Any crossed-boundary or end-of-generation snapshot fix must pass recurrent exactness / state-replay controls before promotion.

Source: https://github.com/jundot/omlx/issues/3462

### llama.cpp #25187 update — independent Qwen3.8-27B run weakens the case for aggressive 32K FR-Spec as the default

The research issue predates this cutoff, but a fresh independent Qwen3.8-27B follow-up was posted after it. Setup: custom FR-Spec build 10752 / `044b56f77`, cross-file MTP draft, Qwen3.8-27B NVFP4 target, 192K context, q8 KV, n-max=4, nine generic code/prose/QA prompts plus a real ~70K-token technical document, temperature 1.0 / seed 42.

Reported long-context results:

| Draft head | Acceptance | TG |
|---|---:|---:|
| target internal IQ4_XS full 248K head | 68.1% | 109.7 tok/s |
| 32K FR-Spec agentic map | 60.8% | 105.6 tok/s |
| 32K FR-Spec prose map | 60.6% | 104.5 tok/s |
| cross-file full Q5_K head | **70.9%** | **112.6 tok/s** |
| cross-file full NVFP4 head | 70.9% | 109.6 tok/s |
| cross-file full BF16 head | 70.9% | 110.3 tok/s |

On the shorter prompts, the 32K agentic map did produce roughly a 5% best-case wall-time improvement, but acceptance fell about 5 percentage points; on the long technical case the loss was about 10 points. Re-ranking the 32K vocabulary with prose data barely changed the result, suggesting the aggressive ~13%-of-vocabulary cut itself was the main problem on this workload.

The author reports identical output tokens versus the target's internal MTP at the same seed, consistent with target verification preserving the sampled result. The full Q5_K head was about 1.9 GiB and, in this experiment, was the best speed/acceptance compromise.

**RTX 5070 Ti consequence:** test **full-head MTP quantization before aggressive vocabulary trimming**. FR-Spec remains valuable as a memory/headroom or workload-specific lane, but a small draft-head kernel is not sufficient if acceptance falls enough to increase target verification work. Certification should include short coding turns and long technical context at the intended sampling settings, with acceptance, accepted tokens/cycle, TG, E2E wall and memory all recorded.

This is not RTX 5070 Ti hardware and therefore does not move the 120/250 center.

Source: https://github.com/ggml-org/llama.cpp/issues/25187

### ds4 main — reusable aligned-Q8 CUDA scratch gives an exact +6.4% to +7.5% Flash-0731 decode win on DGX Spark

Fresh ds4 commits `b42682f12ff1e71746c698125ee4b182dca1e5ae` and `9ab705347c1775e7599ede7eb81a6255ec7dccb5` remove repeated pool allocation from aligned Q8 dense/paired decode kernels by reusing device-checked scratch, retaining safe missing/undersized fallbacks.

Physical September 5 DGX Spark / GB10 result, fully resident DeepSeek V4 Flash-0731 Q2, **no speculative decoding**, three interleaved medians after warmup, 128 teacher-forced decode tokens:

| Context | Previous TG | Scratch-reuse TG | Gain | PP before / after |
|---|---:|---:|---:|---:|
| 2,048 | 17.90 | 19.25 | **+7.5%** | 823.06 / 823.49 |
| 4,096 | 15.23 | 16.22 | **+6.5%** | 898.69 / 899.89 |
| 8,192 | 15.01 | 15.97 | **+6.4%** | 931.53 / 931.17 |

Full prefill and post-decode logits matched exactly at all three frontiers. The 100-case Flash-0731 continuation score was unchanged. The added scratch test covers 24 shapes, missing/undersized fallback and CUDA graph replay with changed inputs; Compute Sanitizer reportedly found zero errors.

**Transfer:** inspect the Apple/Metal projection/QMV hot path for equivalent per-step scratch/pool allocation or repeated temporary construction. If it exists, preallocated stage-local scratch deserves a controlled exact A/B. This is a CUDA/GB10 result, not a Metal or M1 rate ruler, and it does not move the DS4 15-TG target.

Sources:
- https://github.com/antirez/ds4/commit/b42682f12ff1e71746c698125ee4b182dca1e5ae
- https://github.com/antirez/ds4/commit/9ab705347c1775e7599ede7eb81a6255ec7dccb5

### llama.cpp #28448 — dynamic-topology allocator identity is a new silent-corruption seam to monitor

Created 2026-09-05 17:34:42 UTC. The report argues `ggml_gallocr_needs_realloc()` validates reusable allocation plans primarily by graph position and size, not logical tensor identity. With a dynamic sparse-MoE graph, a different tensor can therefore occupy a compatible same-size graph position and inherit a stale allocation offset.

The author reports two physical sparse-MoE reproductions, including Gemma 4 reproduced with CPU-only execution and a Qwen3-MoE case. The application symptom was grammatically shaped but semantically corrupted output with no crash or default warning. Follow-up git archaeology found prior narrow gallocr fixes where a changed graph required plan invalidation/reallocation, strengthening the general mechanism without proving this exact bug on Qwen3.8-Flash-Next.

**Policy:** keep this as a monitored correctness seam, not a current Flash blocker. If the llama.cpp Qwen4Exp/Flash path dynamically changes decode topology/expert graph identity, add a repeated-route-change oracle that compares full logits/output against a forced-reallocation/reference path. Do not infer Apple impact until reproduced on the relevant graph/backend.

Source: https://github.com/ggml-org/llama.cpp/issues/28448

### oMLX #3464 — benchmark log provenance can hide TG even when the benchmark computed it

Created 2026-09-05 18:59:22 UTC. oMLX's `[benchmark-pp-result]` log line records processing TPS, TTFT, E2E and cached tokens but currently omits the already-computed `gen_tps` field that is shown elsewhere.

**Policy:** a missing TG in this log line is not evidence that TG was unmeasured or zero, and the research collector must not manufacture a TG denominator from E2E timing. For promotion receipts, capture the structured result / explicit generation TPS and generated-token count directly.

Source: https://github.com/jundot/omlx/issues/3464

---

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG receipt or completed 115K/256K exact result surfaced after the boundary.
- **Dual-M1 DS4-0731:** fresh ds4 main work is CUDA/ROCm/other hardware; no new exact sustained generated-token denominator on 2x M1 Max64/TB4 surfaced.
- **RTX 5070 Ti Qwen3.8-27B:** no new exact-card TG/PP receipt surfaced. The FR-Spec follow-up is different hardware and changes test ordering, not the card ruler.
- **M1 Max64 Qwen3.8-27B:** no new exact single-M1-Max serving receipt surfaced.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep the 12:00 qualification order and add one new high-priority serving gate immediately after ordinary recurrent rollback correctness:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent partial-rollback correctness;
3. **growing coding-agent cache-capture efficacy:** short generations, long reused prefixes, MTP on/off diagnostic controls, require advancing reuse frontier and bounded fresh-prefill work;
4. PLE residency/page-cache/direct-read A/B;
5. sparse-QSA wide-prefill and neighboring-row reuse;
6. long-context indexer reservation and recurrent-checkpoint budgeting;
7. MTP per-slot context/state and slot-isolation gates;
8. compiled/multi-agent stress.

A cache hit percentage alone is insufficient; record actual reusable tokens and fresh work.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

No target movement. AProjQ4 remains the primary projection candidate, with cold/full PP separated from incremental-turn PP as established in the 12:00 pass.

The fresh DGX Spark scratch result creates a new low-cost profiling question: does the Metal QMV/projection path allocate or rebuild scratch every decode step? Only promote a Metal scratch reuse change after exact logits and repeated/graph-style replay pass.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No exact-target movement. Preserve P69 separation: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

FR-Spec/full-head evidence is architecture-level MTP evidence, not an M1 receipt. If the serving lane later adopts an external/cross-file MTP head, test head quantization and acceptance before considering aggressive vocabulary trimming.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Keep full residency first-order.

Updated speculative order:

1. known-good native/full-head MTP baseline;
2. full-head quantization A/B that preserves useful acceptance while fitting the context target;
3. small-N verifier / Blackwell stability gates;
4. only then 32K FR-Spec or other draft-vocab trim as a memory/workload-specific alternative;
5. compare acceptance, accepted tokens/cycle, true drafting share, TG, E2E wall and peak memory rather than draft-kernel time alone.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing architecture / certification decisions added or strengthened this pass

- **Cache enabled != cache effective.** Real-agent qualification must measure cache-store success and reusable-prefix frontier advancement.
- **Short-output recurrent agents are an adversarial cache workload.** Boundary snapshot policy must be tested with the actual completion-length distribution, especially under MTP stride >1.
- **Draft-head compute savings are not the objective function.** Full E2E speculative performance depends on acceptance/verification work; on the fresh Qwen3.8-27B comparison, a better-quantized full head beat the 32K trim at long context.
- **Prefer full-head quantization before aggressive vocabulary trimming** on the 5070 Ti unless memory pressure forces the latter.
- **Per-step allocation/scratch lifecycle can be a first-order decode lever.** The fresh ds4 CUDA result is exact and physically measured, but Metal transfer requires its own profile and A/B.
- **Dynamic graph allocation identity is now a correctness watch item.** Do not promote it to a Flash-Next blocker without a relevant Qwen4Exp/backend reproduction.
- **Benchmark receipts must contain an explicit TG source and denominator.** Missing log fields must not be reverse-engineered into measured rates.

---

# Search classification

**Fresh / material:** oMLX #3462, oMLX #3464, llama.cpp #25187 fresh independent Qwen3.8-27B follow-up, llama.cpp #28448, ds4 `b42682f` / `9ab7053`.

**Fresh but not target-moving:** all of the above. They change serving certification, profiling priority or speculative-decoding experiment order.

**No fresh exact-rig receipt:** 2x M1 Max64/TB4 Flash sustained TG, 2x M1 Max64/TB4 DS4-0731 sustained TG, M1 Max64 Qwen3.8-27B serving, RTX 5070 Ti Qwen3.8-27B.

Next search boundary is this note's eventual project51 commit, not the upstream issue timestamps.