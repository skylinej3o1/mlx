# External runtime watch — 2026-09-19 13:24 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-19 15:55:17 UTC` through `2026-09-19 17:24:44 UTC`.

PRs, issues, comments/reviews, and default-branch commits were screened across DS4, vLLM, oMLX, mlx-serve, llama.cpp, Splash, Kadir's benchmark/fork, and relevant Unsloth surfaces. Fresh Qwen3.8-Flash-Next community/web and oMLX benchmark surfaces were also checked. Evidence time means substantive source/measurement time, not crawler, merge, rebase, label, or bot timestamps.

## Executive result

**No exact dual-M1-Max/TB4 custom-quant Flash-Next receipt appeared. Numeric targets and confidence remain unchanged.**

Current Flash-Next plan:
- >=35 TG @ ~128K: **~85%**
- **>=40 TG @ ~128K: ~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20%**
- **400 cold PP: ~70%**
- deployment design: **custom ~4.6-4.9 hot-trunk BPW**
- oQ5e: quality/certification comparator
- oQ4e: aggressive speed comparator
- PLE/ngram and MTP precision tracked separately.

Two conclusions matter most in this window:

1. **Splash transfer strength is lower than previously implied at the kernel level.** The current Splash README requires **M3 or newer**, and a new issue explicitly requests an M2 Ultra / Apple GPU family 8 backend. Splash remains excellent architecture/methodology evidence, but not direct M1 kernel evidence.
2. A newly published vLLM duplicate PR gives a particularly clean articulation of the multi-row verify optimization Project 51 wants: keep K candidate queries together so the shared committed prefix is read/amortized once, or split verification into **common-prefix stage A + tiny causal candidate-tail stage B**.

These pull in opposite forecast directions and do not warrant a numeric move. Exact M1 confidence continues to rest most heavily on Project 51's own M1 27B verifier gains plus exact M1 Flash receipts.

## NEW — Splash current hardware floor is M3+, not M1/M2

Strict-window Splash issue #9 was created at **2026-09-19 16:04:24 UTC** requesting:

> Apple GPU family 8 / M2 Ultra backend.

The current public Splash README states:
- **Apple M3 or newer**
- macOS 26.4+
- 36 GB unified memory minimum.

The source also contains Apple9/Apple10-specific Q4 linear policies and tuning branches.

Classification: **NEW transfer-qualification evidence.**

### Project 51 impact

Previous Project 51 wording that treated Splash as generic Apple-Silicon execution evidence was too broad.

Correct interpretation:
- Splash strongly validates the **architecture** of model-specialized speculative execution:
  - fixed small verify blocks
  - model-shaped kernels
  - target-pass amortization
  - quantized KV reuse
  - bounded draft context
  - representative-shape autotuning
  - whole-cycle scheduling.
- Splash's **exact kernels/presets do not establish M1 portability or M1 speedup**.
- The exact M1 basis for verify-side optimism remains Project 51's own 27B campaigns and exact M1 Flash evidence.

Target effect: **no change**. The earlier +5-point confidence expansion is retained because it was not based on Splash alone, but future references must qualify Splash as **M3+ architectural corroboration**.

## STRICT-WINDOW / DUPLICATE — vLLM #57703 articulates common-prefix verify amortization

PR #57703 was created at **2026-09-19 17:08:13 UTC** and closed at 17:17 as a duplicate of older #56861 and #57085.

It describes two multi-token verification routes under decode context parallelism:

### Existing segmented path
K-token verification becomes:
- K separate single-query rows
- each row rereads almost the same committed KV prefix
- causality is represented with per-row lengths.

### Native block path
The K-query verify block stays together:
- common committed prefix is traversed/amortized across queries
- causal boundaries come from global positions in-kernel.

### Experimental two-stage path
- **stage A:** common committed prefix, no causal mask inside the candidate block
- **stage B:** small dense causal draft/candidate window
- merge output + natural-log LSE afterward.

This is extremely close to the Project 51 “verify wave” concept.

### Directional measurements in #57703

MI355X / ROCm:
- c1 fixed 8K-context probe: **15.23 -> 19.15 TG (+25.7%)**
- c8: **136.95 -> 265.38 aggregate TG**
- c32: **216.81 -> 374.38 aggregate TG**.

The author explicitly says the fixed-probe old/new arms were **not perfectly isolated**: one archived segmented run used dummy weights / a PD route while the native run used real colocated weights.

A separate real Kimi-K3 1P1D TP8/DCP8 MoRIIO deployment at c48 over 1,200 s reported:
- DSpark K4 native block verify: **623.58 output TG**
- no-spec: **487.44 output TG**
- acceptance length ~3.37.

The implementation was already represented by older PRs, so this is not a new mechanism despite the strict-window write-up.

Classification: **strict-window duplicate write-up / recovered confirmatory mechanism evidence.**

### Project 51 rule

For Flash verification, wherever semantics permit:
- separate shared committed-history work from the small candidate-tail work;
- batch candidate rows so common metadata/KV traversal is not replayed serially;
- cache/reuse QSA block-key/indexer state across the wave.

Caveat: QSA selection remains **query-dependent**. We must not assume candidate rows have identical selected blocks or identical attention results. The optimization target is common-data traversal/staging and batched scoring, not invalid row sharing.

No numeric target effect.

## NEW — compact draft vocabulary as an MTP-side optimization

llama.cpp PR #29143 / issue #29145 were created around **2026-09-19 17:02-17:06 UTC**.

Qwen3.5 MTP sidecars can carry a trimmed draft vocabulary:
- example draft vocab: **32,768**
- target vocab: **152,064**
- mapping tensor: `d2t`.

The patch:
1. sizes the draft LM head to the compact vocab;
2. prevents full-vocab embedding fallback from clobbering that head;
3. scatters compact draft logits into a full-vocab `-inf` canvas before target-side sampling/verification.

Reported hardware result:
- dual RTX PRO 6000-class GPUs
- autoregressive dense baseline: ~**44.5 TG**
- FastMTP compact-vocab setup: **102.2-113.9 TG**
- draft acceptance up to **82.89%**.

Important limitation:
this is **not an isolated compact-vocab vs full-vocab MTP A/B**. The 2.3-2.5x headline includes speculative decoding itself, so no percentage credit is assigned to vocabulary trimming.

Classification: **NEW mechanism opportunity, non-Flash/non-Apple performance evidence.**

Project 51 action:
consider compact draft vocabulary as a separate MTP-side experiment if our draft/head projection becomes material.

Required qualification:
- d2t mapping parity
- unsupported/rare-token behavior
- acceptance impact
- compact-head projection time
- scatter/remap cost
- quality on code/tool vocabulary tails.

No target effect.

## RECOVERED OLDER EVIDENCE — Unsloth Flash MTP “2x hotfix” was mainly restoration of a broken carry

Fresh search surfaced Unsloth's v0.1.811-beta marketing language: “Qwen3.8-Flash-Next MTP hotfix (2x faster).”

The underlying exact fork evidence is older than this window:
- Unsloth llama.cpp PR #220
- merged **2026-09-18 10:18:27 UTC**.

Root cause:
- upstream Qwen4Exp changed HC gamma layout;
- the fork-only MTP head retained a stale gamma shape;
- MTP builds then aborted during graph construction/load.
- separately, the fit estimator opened a borrowing/shared MTP head without the target embedding tensor and incorrectly budgeted essentially nothing for the draft, causing real load OOM near capacity.

Measured B200/Q4 Flash:
- broken carry: aborts
- fixed MTP head: **61.2-63.6 TG**
- older working prebuilt: **60.7 TG with MTP**
- same older prebuilt without MTP: **43.8 TG**.

Thus the release's “2x” wording should not be treated as a new 2x algorithmic improvement. It primarily restored a broken MTP integration/carry.

Classification: **RECOVERED OLDER correctness/runtime evidence.**

Project 51 rules:
- every trunk architecture/schema change needs MTP-side tensor-shape/ABI parity tests;
- fit/admission must budget borrowed/shared draft tensors even if the draft artifact does not own a duplicate copy;
- release-level “MTP speedup” claims need decomposition into actual algorithmic gain vs restoration of a disabled/broken fast path.

## CURRENT-DAY, timestamp-not-qualified — M2 Ultra Flash MTP batching receipt

The oMLX benchmark site currently exposes a **2026-09-19** session but does not expose a precise source timestamp suitable for strict-window classification.

Hardware/runtime:
- M2 Ultra, 76 GPU cores
- 192 GB RAM
- oMLX dev4
- Qwen3.8-Flash-Next-oQ4e-fp16-mtp
- Lightning MTP
- no DFlash
- max context configured 131,072.

Measured:
- 1K: **362.4 PP / 20.5 TG**
- 4K: **360.5 / 22.3**
- 16K: **621.8 / 23.9**
- peak memory at 16K: **84.7 GB**.

Batching panel:
- B1: **20.5 TG**
- B2: **39.8 aggregate TG (1.94x)**
- B4: **42.7 aggregate TG (2.08x)**.

Classification: **current-day Apple8 supporting evidence; not strict-window NEW because source time is insufficiently precise.**

Interpretation:
- useful evidence that Lightning MTP + batching can scale almost linearly from B1 to B2 on Apple8;
- saturation appears rapidly by B4 in this runtime;
- not M1, not TB4, not ~128K measured context.

No B1 or B2-B4 target move.

## STRICT-WINDOW anecdote rejected for forecasting

A Reddit post appearing during this window reports Qwen3.8-Flash-Next going from roughly 20-50 TG to **>70 TG** after updating Unsloth v0.1.811-beta and redownloading the MTP file.

By cutoff:
- hardware unspecified
- quant unspecified
- context unspecified
- output length unspecified
- no controlled before/after recipe.

A commenter reports ~30 TG on Strix Halo after the update.

Classification: **weak ecosystem smoke only.**

No numeric credit.

## Other checked surfaces / negatives

- No exact 2x M1 Max / TB4 Flash TG or PP receipt.
- No new qualifying single-M1 Max Flash receipt.
- No strict-window commit in Splash, Kadir qwen38-mac-fast, Kadir llama.cpp, oMLX, DS4, or mlx-serve that changes the target.
- llama.cpp strict-window default-branch commits were Hexagon backend changes, irrelevant to the Apple Flash lane.
- vLLM #57704 context-parallel fp8 indexer was scaffolding with core scoring/top-k bodies still TODO and benchmark cells TBD; no performance evidence.
- oMLX #3762 adds per-request SpecPrefill controls to the Anthropic endpoint only; no performance mechanism change.
- Splash issue #10 contains an M3 Max user's 190-TG Qwen3.6-35B anecdote but is unrelated to the Flash target and not used.
- Fresh HF/community search did not surface a qualified dual-M1/custom-quant Flash result.

## Target / confidence decision

**No change.**

Flash-Next dual-M1:
- >=35 TG @ ~128K: **~85%**
- **>=40 TG @ ~128K: ~65%**
- >=45 TG: **~40%**
- >=50 TG: **~20%**
- **400 cold PP: ~70%**.

Reason:
- Splash's exact kernel transfer to M1 is weaker than previously implied.
- The common-prefix multi-row verification mechanism received additional independent support.
- Exact M1 verifier experience remains favorable.
- No new target-topology receipt closes the PP2/TB4/QSA/MTP interaction uncertainty.

## New/strengthened qualification rules

1. **Generation-specific transfer labels:** M3+/Apple9 kernel evidence must not be presented as M1 kernel evidence.
2. **Verify common-prefix amortization:** candidate rows should reuse committed-history traversal/staging wherever semantics permit.
3. **Query-dependent sparse selection remains row-local:** reuse infrastructure/state, not incorrect attention outputs.
4. **Compact draft-vocab is a separate optimization axis:** do not credit its performance without full-vocab-MTP A/B.
5. **MTP ABI/schema parity:** trunk HC/GDN/QSA tensor-shape changes need explicit draft-side compatibility tests.
6. **Draft fit accounting includes borrowed/shared tensors.**
7. Existing exact fast-path engagement, fusion concurrency, state provenance, distributed geometry, long-context parity, and component-wise quant gates remain.

## Hard freshness boundary

`2026-09-19 17:24:44 UTC`
