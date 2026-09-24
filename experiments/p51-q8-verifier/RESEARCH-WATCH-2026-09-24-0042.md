# Project 51 primary-lane research watch — 2026-09-24 00:42 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 03:31:38 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 04:42:49 UTC**. The Splash M1/Apple7 kernel work is included as **RECOVERED OLDER EVIDENCE** because it predates the boundary but materially changes the Apple7 headroom picture.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared, and no new DASLab / GSQ-RCO xhigh behavioral-quality result appeared.

The strongest fresh result is a higher-quality validation of the Apple Flash-Next verifier optimization already seen in #519: the result now survives a multi-round served harness, a 32K-context cell, and a pinned-controller acceptance comparison. The speedup is no longer plausibly explainable by lower acceptance. At the same time, an M5 Max transfer test shows the same kernel choice gives only 1-5% verify-forward gains and no served advantage, reinforcing hardware-topology-specific dispatch.

The recovered M1/Splash work also materially strengthens the premise that Apple7-specific kernel policy can uncover large performance headroom even when a modern runtime is already model-specialized.

## Findings

### UPDATE — mlx-serve #519: verify-MoE gain survives controlled acceptance and 32K context; Max transfer is weak

Source: https://github.com/ddalcu/mlx-serve/pull/519

The previous watch recorded the initial M5 Ultra result for routing Flash-Next MTP verify rows through the fused MoE rows arm instead of the sorted/gather/QMV chain. The PR now includes stronger validation.

M5 Ultra 256 GB, Flash-Next mixed 4/8-bit, bf16 KV:

| served cell | fused rows | old sorted chain | change |
|---|---:|---:|---:|
| 512-token greedy MTP decode | **190.0 TG** | 166.2 | **+14.3%** |
| sampled MTP decode | **217.0 TG** | 188.9 | **+14.9%** |
| decode after 32K prompt | **93.6 TG** | 84.4 | **+10.9%** |
| 1-stream aggregate | 142.4 | 140.3 | +1.5% |
| 4-stream aggregate | 189.3 | 190.0 | flat |

The concurrency result makes sense: batched decode already takes the rows arm, so the new path primarily helps single-slot speculative verify.

Most importantly, acceptance was isolated with the adaptive controller disabled and depth pinned:
- exact-accept greedy rows: **0.90 accepted/round**, round **17.7 ms**;
- old chain: **0.93 accepted/round**, round **21.1 ms**;
- mean decode **144.5 vs 129.1 TG**.

Under sampled served settings:
- rows: **1.33 accepted/round**, **18.7 ms**;
- old chain: **1.21**, **21.5 ms**;
- mean decode **156.0 vs 134.0 TG**.

Thus the earlier tokens/step anomaly was sampling/controller variance; with the controller pinned, acceptance is essentially matched while each round is about **16% cheaper**.

Transfer test on M5 Max 128 GB:
- S=3 verify: ~23.5 vs ~24.1 ms;
- S=5: ~29.4 vs ~30.5 ms;
- S=7: noisy ~38-43 vs ~40.4 ms;
- served decode: **52.9 vs 56.8 TG**.

The path therefore stays Ultra-only by default.

**Classification:** UPDATE / stronger exact-family Apple verifier evidence.

**P51 consequence:** dedicated verify-width MoE dispatch is now substantially better supported as a real verifier-cost lever. But the M5 Max result is equally important: **do not transfer an Ultra-optimal verify kernel policy to M1/Max without direct Apple7 qualification**. P51 should autotune or explicitly qualify S=2-8 policies on the actual M1 Max.

**Target impact:** none.

### NEW — mlx-serve #517 extends the fused GDN path into MTP verification

Source: https://github.com/ddalcu/mlx-serve/pull/517  
Fresh commit: **716c0cd1a7a7** at 2026-09-24 04:02:22 UTC.

The earlier version only fused the non-Hadamard GDN S=1 path. The fresh commit adds a sequence form for S=2-8 verification while preserving the per-step state snapshots required for partial-accept rollback.

Flash-Next / M5 Ultra:
- MTP decode: **131.0 / 129.3 TG** vs **125.9 / 125.0**, about **+3.6%**;
- MTP decode at 16K: **121.7 / 127.5** vs **118.5 / 120.4**, about **+4.0%**;
- S=3 verify forward: **19.26 vs 19.71 ms (-2.3%)**;
- S=5: **22.90 vs 23.39 (-2.1%)**;
- S=7: **27.86 vs 28.33 (-1.7%)**;
- 2K prefill unchanged.

Correctness:
- 2,639 tests passed;
- sequence parity checks cover y, convolution state, final recurrent state and **every captured rollback row**;
- with adaptive depth disabled and depth pinned to 3, MTP greedy text is byte-identical to the old chain on four prompts.

**Classification:** NEW exact-family Apple verifier evidence.

**P51 consequence:** GDN dispatch fusion and rollback-safe multi-row verification are compatible. This is directly relevant to the P51 goal of reducing the sequential GDN component of the ~2.3x verifier cost. It is a few-percent system win, not a full verifier breakthrough.

### NEW — SGLang #41038/#41040: asymmetric P/D TP requires destination-aware DFlash KV relayout

Sources:
- https://github.com/sgl-project/sglang/issues/41038
- https://github.com/sgl-project/sglang/pull/41040

GLM-5.3-Flash + DFlash2, Mooncake disaggregation:
- prefill TP2;
- decode TP4;
- B300;
- 256 requests, concurrency 64, ~4096 input / 1536 output.

Target MLA KV has compatible per-rank layout, but the DFlash draft KV is head-sharded. A TP2 source draft page has twice the per-rank bytes of a TP4 destination page. Reusing source item lengths as destination strides addresses the wrong destination locations.

Observed:
- before local prototype: **228/256** completed, 28 transfer failures;
- prototype with target KV unchanged and draft slices repacked to owning destination ranks: **256/256** completed.

The community PR packs source draft pages into registered staging storage, separately supplies destination item lengths, and scopes the relayout to unequal-P/D-TP DFlash transfers.

Caveat: the 256/256 result was from the earlier internal prototype, not this exact rebased community commit; full token-equivalence and current-main GPU rerun remain pending.

**Classification:** NEW draft-state transport correctness evidence.

**P51 consequence:** reinforces the per-region state-topology rule from vLLM #58470/#58471. Draft state transfer identity needs **source geometry and destination geometry separately**, including item lengths/strides, ownership and replication. PP/disaggregated state transfer cannot assume symmetric stage layouts.

### NEW / exact-family cross-hardware — llama.cpp #28243: MTP uplift is highly workload-dependent and can be negative on reasoning

Source: https://github.com/ggml-org/llama.cpp/pull/28243  
Fresh validation comment: 2026-09-24 03:55:41 UTC.

Qwen3.8-Flash-Next UD-IQ3_XXS on 2x Arc Pro B70, layer split with some FFN on CPU/DDR5, standalone Q8 MTP draft, greedy/fixed seed, BetterBench 0.6.0:

| category | MTP off | MTP on | delta |
|---|---:|---:|---:|
| file_edit | 29.0 | 41.5 | **+43.3%** |
| json | 29.0 | 41.2 | **+42.1%** |
| math | 29.2 | 38.9 | +33.0% |
| summarization | 29.3 | 36.8 | +25.6% |
| code | 28.8 | 36.1 | +25.4% |
| chat | 28.7 | 32.0 | +11.7% |
| prose | 28.4 | 29.5 | +3.8% |
| reasoning | 28.8 | 27.9 | **-3.2%** |
| median | 28.7 | 36.3 | **+25.5%** |

**Classification:** NEW exact-family cross-hardware speculative evidence.

**P51 consequence:** reinforces that a single average speculative multiplier is unsafe. Acceptance/value must be reported by workload class, especially xhigh reasoning. P51's source-like certification should include both effective TG and acceptance/correction behavior on long reasoning, coding, tools and prose separately.

### RECOVERED OLDER EVIDENCE — Splash #131 / paperniuk Apple7 branch: native M1 kernels expose large hidden headroom

Sources:
- https://github.com/incoai/splash/issues/131
- https://github.com/paperniuk/splash/tree/apple7-m1-kernels

This work predates the 03:31 boundary but was audited after the previous watch and materially changes the Apple7 evidence base.

M1 Max 32-GPU-core / 64 GB / macOS 26.7, Qwen3.8-27B Splash Q4 + DFlash, ABBA:
- five fixed xhigh prompts: **18.9 -> 39.1 effective TG**;
- reasoning-off technical/python/TS cells roughly double;
- 8K decode: **12.8 -> 26.8 TG**;
- 32K decode: **12.5 -> 23.8 TG**;
- four parallel requests: **18.0 -> 65.2 aggregate TG**;
- prefill 2,048 tokens: **53 -> 142 tok/s**;
- prefill 32,029 tokens: **48 -> 110 tok/s**.

Real opencode agent session, context growing 30K-89K:
- median decode by range: **19.5-36.5 TG**;
- new-token prefill: 96 tok/s at 16-32K and 54 tok/s at 64-96K;
- ~95% prompt tokens served from prefix cache.

Kernel mechanism:
- M1 has no hardware BF16 arithmetic, so Apple7/8 gets exact-half weights + FP32 activations/accumulation;
- the new register-only Mma64 prefill tile reaches **7.3-7.4 TFLOPS** on actual model projections vs **2.4-3.5 TFLOPS** for the prior MPP path;
- microbench peaks 8.6 TFLOPS FP32xFP32 and 9.9 halfxFP32;
- batch-wide decode reuses each unpacked Q4 weight fragment across lanes.

Numerics:
- 2,528 shared positions;
- **99.92% top-1 agreement** vs the prior M1 Q4 kernel;
- mean KL **1.3e-4 nats**;
- 168 engine tests + vision/runtime oracle pass.

Important limitations:
- 39.1 TG is **short-prompt speculative effective decode**, not target-only and not a 128K receipt;
- parity is new-Q4-kernel vs old-Q4-kernel, not Q4 vs BF16 source;
- no filled-128K decode measurement.

**Classification:** RECOVERED OLDER EVIDENCE / strong Apple7 kernel-headroom evidence.

**P51 consequence:** the distinction between "modern Apple-tuned" and **actually M1-specific** is now first-class. Apple7 can leave 2x-class projection performance untapped under an inappropriate arithmetic/kernel policy. This materially strengthens the rationale for custom M1 kernel qualification and for testing low-bit formats around exact Apple7 arithmetic rather than assuming newer-Apple policies transfer.

It does **not** justify multiplying the existing Flash-Next 128K anchor by 2. Dense 27B Q4 + DFlash has different arithmetic, memory traffic and speculative behavior.

### UPDATE — mlx-serve #514: broad kernel padding is a null result; targeted fusion wins are the right granularity

Source: https://github.com/ddalcu/mlx-serve/issues/514

Fresh follow-up reports:
- #517: +3.9% plain, +3.6% MTP;
- #519: +14% greedy / +15% sampled MTP on Ultra;
- padding narrow decode kernels to 16+ threadgroups moved forward **13.12 -> 13.06 ms (-0.4%)** and decode **87.2 vs 87.4 TG**, effectively null.

**P51 consequence:** don't generalize from a low-level dispatch probe into broad kernel-padding policy. Profile and fuse the actual critical chains. This supports a targeted min-maxing approach rather than blanket "more occupancy" changes.

## Community / quant search

- **IST-DASLab/GSQ:** no issue, PR or commit activity in-window.
- Fresh web/Reddit search surfaced the already-known RTX 4080 Flash-Next ~131K report and the M1 Splash post, but search metadata did not expose a new precisely post-boundary controlled source-vs-quant xhigh result.
- No new ByteShape behavioral receipt materially changed the current quant frontier during this exact window.

## Canonical planning state after this pass

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**, conditional on at least modest speculation benefit.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target; the Apple7/DASLab-style hybrid lane now has clearly higher experimental upside but is not yet promoted to a canonical target.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 04:42:49 UTC**
