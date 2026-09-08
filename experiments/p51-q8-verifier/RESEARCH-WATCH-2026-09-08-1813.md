# External runtime research watch — 2026-09-08 18:13 ET

Starting freshness boundary: `5452dffc758ba3230ed627e514d06beaeec87d71` / **2026-09-08 18:47:28 UTC**.

This pass preserves the project evidence discipline: measured exact-topology evidence, mechanism-transfer evidence, benchmark corrections and planning targets remain separate. No exact target-topology receipt surfaced that justifies moving a target.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

`RESEARCH-TARGETS.md` remains authoritative. This pass moves no row.

---

# UPDATE / CORRECTION — oMLX #3520 long-context gathered QSA

PR: https://github.com/jundot/omlx/pull/3520

The 14:38 watch correctly promoted the mechanism but its then-current server matrix has now been superseded. The PR was revised after the cutoff and explicitly withdraws an earlier benchmark chain because that chain did **not** have the native sparse-attention extension built. The fallback route therefore made the branch look up to roughly **20 percentage points better at 229K** than the production extension-built comparison.

The current comparison is:

- **M5 Max 128 GB**, High Power;
- Qwen3.8-Flash-Next-oQ4e-mtp;
- `main` `b908f563` versus branch `9e19561b`;
- both arms with native kernel extensions built;
- fresh server per arm, interleaved B/A/A/B chain, two passes per prompt, mean of four;
- 512-token completions.

## Corrected end-to-end matrix

### Serial decode, MTP off, greedy

| Context | main | branch | Delta |
|---:|---:|---:|---:|
| 3.9K | 62.7 | 62.5 | -0.4% |
| 7.7K | 61.3 | 61.2 | -0.1% |
| 16K | 59.4 | 59.5 | +0.1% |
| 32K | 57.5 | 57.3 | -0.3% |
| 63K | 53.7 | 57.7 | **+7.5%** |
| 134K | 47.3 | 55.7 | **+17.7%** |
| 229K | 40.9 | 52.4 | **+28.1%** |

### Adaptive Lightning MTP, max depth 3, temperature 1 / top-p .95 / top-k 20

| Context | main | branch | Delta |
|---:|---:|---:|---:|
| 3.9K | 62.1 | 64.8 | +4.4% |
| 7.7K | 62.7 | 62.6 | -0.1% |
| 16K | 63.6 | 64.5 | +1.5% |
| 32K | 62.1 | 58.7 | -5.4% noisy cell |
| 63K | 53.2 | 57.7 | **+8.5%** |
| 134K | 45.3 | 56.8 | **+25.4%** |
| 229K | 39.2 | 53.4 | **+36.1%** |

### Adaptive Lightning MTP, max depth 3, greedy

| Context | main | branch | Delta |
|---:|---:|---:|---:|
| 3.9K | 70.2 | 69.5 | -0.9% |
| 7.7K | 74.3 | 76.3 | +2.6% |
| 16K | 67.8 | 66.1 | -2.5% |
| 32K | 63.8 | 64.6 | +1.2% |
| 63K | 58.0 | 66.4 | **+14.6%** |
| 134K | 48.6 | 62.6 | **+28.7%** |
| 229K | 44.1 | 58.5 | **+32.4%** |

**Supersession:** these extension-built numbers replace the #3520 figures recorded in the 14:38 watch. The mechanism conclusion survives; the withdrawn matrix does not remain quantitative evidence.

## Row-count and context-dependent route selection

The revised PR adds an important qualification: one sparse route is not globally optimal.

### Selected-row gather itself

For decode / a few verify rows, gathering directly from stored `(B,H,N,D)` layout stays approximately flat with context. But a 64-query-row prefill subchunk can make a one-time token-major copy cheaper because direct take rereads selected rows per query.

Per QSA layer, 64 query rows / 2,051 selected rows:

| Context | token-major copy + flat gather | stored-layout take |
|---:|---:|---:|
| 16K | 0.58 ms | 1.55 ms |
| 65K | 0.90 ms | 1.02 ms |
| 131K | 1.19 ms | 1.04 ms |
| 206K | 1.49 ms | 1.05 ms |

Current branch policy: with **>=32 query rows and cache <128K**, use token-major copy; otherwise use stored-layout take. Both forms are tested against the old helper.

### QSA indexer score route on M5 / NAX

At ~134K context:

| Query rows | native score kernel | MLX expression |
|---:|---:|---:|
| 1 | 0.77 ms | 0.27 ms |
| 4 | 0.36 | 0.26 |
| 16 | 0.36 | 0.30 |
| 32 | 0.39 | 0.39 |
| 64 | 0.40 | 0.54 |
| 2048 | 5.1 | 11.8 |

Native score kernel now engages at **32 rows** on NAX hardware.

### Top-k and sparse-GQA attention route

Native top-k ties/loses at one to four rows and wins from about eight; branch gate = **8 rows**.

Native sparse-GQA attention at ~134K:

| Query rows | native sparse attention | gathered SDPA |
|---:|---:|---:|
| 4 | 1.56 ms | 0.70 ms |
| 8 | 1.58 | 0.87 |
| 16 | 1.65 | 1.36 |
| 24 | 1.67 | 1.83 |
| 64 | 1.74 | 3.93 |

Branch gate = **24 rows** on NAX. Four-to-eight-row calls are exactly ordinary MTP verify widths, so blindly selecting the native kernel was reportedly adding about **10 ms per verify cycle across 12 QSA layers**.

### Promotion

For Flash certification, record separately:

- extension/build identity and whether each native kernel was actually available;
- actual selected gather implementation;
- query-row count / verify width;
- context depth;
- native score / top-k / sparse-attention route;
- fallback reason and fallback implementation.

A native custom kernel is not automatically the fast path. The route boundary is a function of hardware, row count, context and workload phase.

No M5 percentage numerically transfers to M1 Max/TB4.

---

# FRESH — independent indexed split-K sparse-attention evidence

Fresh comment on oMLX #3520 at **2026-09-08 21:03:36 UTC**:
https://github.com/jundot/omlx/pull/3520#issuecomment-5591835675

Independent M5-Max work on B=1, self-MTP k=2, same Flash-Next / 4-bit-A3B profile replaced gather+SDPA with an indexed split-K kernel that reads selected K/V by block index directly from stored layout and performs its reduction in-kernel.

Reported performance versus the gather path:

- isolated attention, M=3: ~**2.8x at 16K** rising to ~**11x at 128K**;
- M=1 crossover between ~32K and 64K; ~1.1x at 64K, ~1.5x at 128K;
- end-to-end decode: **+11% at 16K, +21% at 32K, +42% at 64K**, digest-identical to the gather baseline.

The higher-value result is the numerical/correctness qualification. A mathematically cleaner reduction using contiguous chunks, precise exp, FP32 partials and a sequential merge looked exact on small cases but shifted a chosen-token logprob by about **0.06 at 16K**, enough to flip a real verify transaction. Digest equality required reproducing the deployed native `sdpa_vector_2pass` arithmetic closely: interleaved streams, pre-scaled q, fast-exp behavior, BF16 partial boundaries and matching second-pass merge structure.

Operational caveats are equally important:

- the custom kernel is build-pinned behind an MLX allowlist plus SDPA-header hash;
- a serving venv with a different MLX build silently declined the kernel and fell back to slow gather until a receipt exposed it;
- M>1 verify widths remain separately gated because changing verify width can alter the verify token stream;
- equality is to the gathered baseline; versus dense masked attention the reporter still sees near-tie differences around ~1/256 positions.

### Promotion

- Kernel admission/build hash/fallback reason are benchmark provenance.
- A custom sparse-attention kernel needs real-checkpoint transaction-level digest/equivalence, not only small tensor parity.
- Verify width `M` is a semantic and performance dimension.
- A hybrid default is attractive: portable stored-layout gather for ordinary widths, build-pinned split-K only where reduction cost dominates.
- If exactness depends on matching an existing numerical path, arithmetic-path identity belongs in the certification contract.

---

# UPDATE / capacity lane — oMLX #3499 Affine4 KV

PR: https://github.com/jundot/omlx/pull/3499

This is not an exact target receipt and remains opt-in/lossy, but it adds useful Apple long-context capacity evidence.

On **M5 Pro 48 GiB**, Qwen3.8-27B oQ4e with Affine4:

- 150K cold prompt: **291.9 PP / 12.3 TG**, peak active 20.71 GiB;
- 200K cold prompt: **250.0 PP / 11.8 TG**, peak active 21.81 GiB, sampled physical 26.13 GiB;
- logical attention KV at 200K: **12.21 GiB native -> 3.71 GiB Affine4 (-69.6%)**; cache objects including recurrent state ~3.86 GiB.

Short 8K Qwen3.8 comparison is nearly neutral in decode:

- native BF16: 381.6 PP / 13.4 TG;
- TurboQuant4: 373.1 / 13.0;
- Affine4: 365.0 / 13.5.

Separate MTP compatibility probe on Qwen3.8 Affine4 measured **16.9 TG without Lightning MTP -> 36.1 TG with MTP**, with 84/97 considered drafts accepted. A thinking-enabled run completed 28,903 generated tokens with MTP active.

A fresh third-party comment after this pass's cutoff says a cherry-pick fit **256K context on Qwen3.8-27B oQ4e** and observed high MTP acceptance, but supplies no controlled rate/quality receipt. Treat that as supportive capacity anecdote only.

The repeated strongest format comparison is on Qwen3.6-35B-A3B at 200K, where Affine4 measured 46.9 TG versus 22.5 TQ4 and 29.4 native BF16, but that is another checkpoint and remains transfer evidence.

### Caveat / promotion

Affine4 is lossy and the PR explicitly states that incremental compression changes prefill hidden states and chunk size can affect outputs. Therefore:

- retain it as an **optional long-context capacity lane**, not a default target assumption;
- qualify quality/equivalence at realistic long context and chunk widths;
- record cache format, retained native layers, physical and active memory separately;
- certify MTP + prefix restore + restart on the exact checkpoint before promotion.

No headline target movement.

---

# FRESH — DSv4 / DSpark loader and native-depth provenance

Fresh vLLM #50576 comment at **2026-09-08 22:12:19 UTC**:
https://github.com/vllm-project/vllm/issues/50576#issuecomment-5592568869

On 4x CMP 170HX / SM80, TP4+EP, fp8 KV, 32K configuration, a DeepSeek-V4 Vision-Exp port reports DSpark `num_speculative_tokens=6`:

| | no spec | DSpark n=6 |
|---|---:|---:|
| single-stream decode | ~45 | **~86 tok/s** |
| decode at 6K context | ~42 | **~66** |
| aggregate peak | ~138 | **~229** |

Mixed-benchmark draft acceptance was ~29%, short-chat ~48%. Image inference, tool calling and reasoning split were also exercised.

Two loader/model-structure findings are portable:

1. The VL draft loader looked for `lm_head` on the outer `DeepseekV4ForConditionalGeneration` wrapper, got `None`, and the draft head silently remained randomly initialized. Spec decode executed but acceptance was near zero with no hard error. The valid head lives on the inner language model.
2. Vision-Exp reports `num_nextn_predict_layers=3` versus one on the 0731 text checkpoint; requested speculative depth must be compatible with that native structure (reporter uses 3/6/9 rather than the text-oriented 5).

### Promotion

- Explicitly hash/bind the actual draft head weights; `spec enabled` is not proof the drafter is loaded correctly.
- Record wrapper/inner-model ownership of lm_head and other draft-only weights.
- Record native trained NextN/MTP layer count plus requested and resolved proposal depth.
- Validate depth divisibility/formation rules from the exact checkpoint, not another member of the family.

The reported rate is CUDA Vision-Exp transfer evidence, not Apple DS4-0731 target evidence.

---

# BACKFILL / multi-session cache-group economics

vLLM RFC #54661 is older than this cutoff but relevant enough to preserve as a planning input:
https://github.com/vllm-project/vllm/issues/54661

In a GLM-5.3-Flash / 2x DGX Spark / DFlash2-k7 deployment, a sliding-window draft group reportedly consumed ~87% of the shared prefix-cache block pool because every retained target boundary protected many draft-window block IDs even though that group did not determine the useful target hit length. Per-group retention plus a carefully constrained hit-min exemption restored roughly 4x conversation capacity in the fork; a separate 120K alternating-conversation receipt reported 119,936 / 119,995 tokens cached on each return.

This is not upstream behavior and the proposed exemption has strict semantic predicates. A fresh tester notes that a 2,048-token draft window with 1,648-token cache blocks/alignment falls outside those proposed conditions.

### Promotion

For multi-session certification, report cache occupancy **by semantic cache group**. A global retention scalar can be pathological when target, recurrent and draft groups have very different reusable horizons. Any draft-group hit exemption must prove fresh-window recomputation and no stale acceptance state; this is not a generic optimization.

---

# SCREENED / no-change

- oMLX main: no post-cutoff main commit.
- rMLX: no post-cutoff commit.
- antirez/ds4: no post-cutoff commit.
- llama.cpp: no post-cutoff commit.
- Avarok Atlas: no post-cutoff commit.
- NInfer: no post-cutoff commit.
- vllm-mlx: no post-cutoff commit.
- TurboQuant-MLX: no post-cutoff commit.
- Rapid-MLX post-cutoff changes are service/provider/audit work, not inference target receipts.
- oMLX #3372 was closed as **superseded by #3287**; do not promote its title-level `+18% long-context prefill` claim as fresh E2E evidence.
- vLLM main has post-cutoff CI/dependency/distributed-test activity, but no stronger exact target receipt was identified in this pass.
- A same-day M1 Max64 user comment claiming ~30 tok/s with MTPLX lacks quant/context/runtime/measurement provenance and remains anecdotal only.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head exact 2x M1 Max64/TB4 generated-token receipt.
- **M1 Max64 Qwen3.8-27B:** no fresh controlled exact-runtime receipt strong enough to move the planning distribution.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane receipt after the cutoff.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card Q4/Q5 partial-offload receipt after the cutoff.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Current qualification / optimization order:

1. exact PP2 model/recurrent/QSA identity + distributed request lifecycle;
2. cold-PP harness with actual chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase first speculative decode joining another request's continuing chunked prefill;
4. speculative ownership / rollback / replay with one authoritative committed frontier;
5. bound verifier capture to the exact drafter-readable horizon;
6. admission-time paged-boundary alignment, including short-prompt/long-output first-boundary crossing;
7. recurrent checkpoint retention across branch/edit/retry/compaction/reopen with exact frontier/count/bytes;
8. rendered-history cacheability for preserved reasoning/tool calls, with stream/nonstream parity;
9. native/default MTP depth whole-round baseline;
10. explicit **drafter-head binding identity** + native trained MTP/NextN layer count + requested/resolved depth;
11. workload-separated deeper-depth A/Bs + segmented long-generation acceptance/TG;
12. realized QSA route proof for draft, backbone decode and target verify;
13. **extension/build/admission receipt before timing any custom route**;
14. QSA route matrix across query widths / verify widths (at least 1/2/4/8/16/24/32/64) and context depths;
15. selected-KV gather bytes/work must scale with the realized selected set unless a deliberate amortized-copy route is chosen;
16. custom split-K only after real-checkpoint digest/equivalence at the exact verify width and deployed MLX build;
17. serial / sampled-MTP / greedy-deeper threshold sweep with short-context negative controls;
18. stage-local GDN/routed-MoE/projection/sync profiling at realistic chunks, including SIMD occupancy;
19. per-quant/per-kernel chunk-width sweep before promotion;
20. optional Affine4/other compressed-KV long-context lane only after quality, chunk-sensitivity, MTP and restore certification;
21. multi-session cache occupancy by target/recurrent/draft group; per-group retention only with semantic proof;
22. block-history/repeated-work first; double-buffer, row split or custom kernels only where exact M1 profiling proves the matching bottleneck;
23. combine passing mechanisms and rerun cluster cold PP, ~128K TG, append/live-prefix, branch/retry and real coding-agent wall cells.

For PP2, selected K/V plus recurrent/QSA state remain stage-local. Sparse attention that materializes dense cross-stage/TB4 traffic fails the intended topology economics.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

> B2/B3/B4 means physically simultaneously scheduled independent requests with their own correct persistent state. Configured/admitted/batched/queued slots do not count; staggered mixed prefill/decode must remain correct.

## Single M1 Max64 Qwen3.8-27B

No target movement. Affine4 is a separate optional long-context capacity route, not a replacement for the canonical native/exact-runtime cold-PP target.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt. Retain actual source/kernel path, build hash where relevant, target/drafter placement, sampler path, driver/runtime identity and peak VRAM/context headroom. Route-specific fallbacks must be visible in receipts.

## Dual-M1 DS4-0731

No target movement. Add explicit draft-head binding and native MTP/NextN-depth provenance to DS4 qualification. CUDA Vision-Exp numbers do not numerically transfer to the Apple text-0731 lane.

---

# Standing decisions strengthened this pass

- Superseded benchmark chains are explicitly withdrawn; corrected production-route receipts replace them.
- Extension/build availability is benchmark provenance.
- Silent custom-kernel fallback is a failed receipt unless fallback identity is recorded.
- Sparse/QSA route selection is a function of hardware + phase + query/verify rows + context.
- A native custom kernel is not presumed faster at decode/verify widths.
- Selected-row gather and prefill-wide gather may have different optimal memory-access forms.
- Custom sparse-attention exactness may require matching the deployed arithmetic path, not merely the mathematical formula.
- Verify width is both a numerical/correctness and throughput dimension.
- Small tensor parity cannot replace transaction-level token/digest equivalence on a real checkpoint.
- Draft-head weights are explicitly bound and hashed; nonzero speculative execution is not proof of a valid drafter.
- Native trained MTP/NextN head/layer count plus requested/resolved depth are mandatory provenance.
- Optional lossy KV compression is a separate capacity lane and requires long-context quality/chunk-sensitivity certification.
- Cache capacity is measured by semantic cache group under multi-session load.
- Draft-group retention/hit exemptions require proof of fresh state and cannot be inferred from target verification.
- Existing request ownership, device happens-before, mixed-phase recurrent ordering, grammar rollback, sampler ownership/fallback, fairness, cancellation/reuse/restart, quantized-hook, QSA selected-set/order and tape/refold gates remain active.
- Acceptance length/rate is diagnostic; useful emitted tokens per wall-second remains the objective.
- Cross-runtime/other-hardware gains remain mechanism evidence until exact target reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
