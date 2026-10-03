# Project 51 research watch — 2026-10-03 07:00 ET

Freshness boundary entering: **2026-10-03 03:26:54 UTC**
Cutoff: **2026-10-03 11:00:49 UTC**

## Decision

**No numeric primary-Windows fit/admission/stability/TG/PP target movement.**

Current primary state remains:
- Strata baseline: **0.1.38**;
- IQ3_S + native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**;
- #481-style automatic containment/no-manual-service-restart: **~85%**;
- conversation parking OFF for the initial production baseline;
- explicit `reasoning_budget_tokens` for high/xhigh;
- frozen expert residency for source/AA qualification.

This pass makes four durable strategy refinements:

1. **PLE fidelity language is corrected.**
   New direct Strata #586 teacher-forced evidence shows **BF16 and FP8 are behaviorally distinct** on Flash-Next.
   FP8 remains the practical production candidate; BF16 remains the exact source-value control. Do not call FP8
   “near-BF16 equivalent” without a task-quality qualification.

2. **Our custom M1 27B engine should start from current upstream MLX, not an old fork baseline.**
   MLX #4596 merged a substantial generic long-context SDPA improvement on M1 Pro; #4598 adds Q4/Q5/Q6/Q8
   medium-alignment gather-QMV wins. Those changes attack exactly the decode shapes we were considering writing
   ourselves. Bespoke Project-51 work should focus on the still-missing Qwen3.8-specific multi-row verifier,
   state/cache lifecycle and quant mapping rather than reimplementing already-improving generic primitives.

3. **The RX6800 dense-27B prefill experiment gets a materially stronger implementation basis.**
   TensorFold #100 already runs Qwen3.8-27B + DFlash2 on ROCm with very high PP on an R9700; #144 adds a ROCm
   GGUF path using Gufo kernels. Neither is an RX6800 receipt, but this means our experiment can mine an existing
   ROCm 27B engine rather than building the producer from zero.

4. **DASLab's MTP-integrated IQ3_S is the correct first artifact for the M1/RX experiment.**
   Recovered older Hugging Face evidence confirms the `*-mtp.gguf` builds embed the MTP head. The IQ3_S-MTP file
   is ~12.1 GB versus ~11.8 GB without the head. Use the integrated MTP artifact when measuring the production-like
   lane; keep the non-MTP build only as a target-only control.

No hardware purchase change. Native Windows context remains 262,144.

## NEW — Strata #586: direct BF16/FP8/IQ4_NL PLE comparison changes the fidelity interpretation

PR:
https://github.com/Niko1221/Strata/pull/586

Created **2026-10-03 05:44:18 UTC**, open.

The checkpoint carries:
- FP8/F8_E4M3 PLE source: ~51 GB packed, ~2.66% row error;
- BF16 PLE source-of-record: ~102 GB;
- current stock IQ4_NL PLE: ~28.8 GB.

Controlled 8-prompt sweep (585 to 37K prompt tokens), fixed residency:
- FP8 vs FP8 control: median/p95 KL **0 / 0** over 1701 windows;
- BF16 vs FP8: median **0.01105**, p95 **0.16647**;
- IQ4_NL vs FP8: median **0.02280**, p95 **0.36905**.

Greedy trajectories:
- BF16 vs FP8: mean **3.8 verify windows** before first disagreement; **0/8** full runs identical;
- IQ4_NL vs FP8: mean **6.6 windows**; **0/8** full runs identical;
- control: 212.6 windows average; 7/8 complete runs identical.

Interpretation:
- **FP8 and BF16 are not interchangeable**; the table choice changes generated text quickly;
- IQ4_NL is roughly twice as far from FP8 as BF16 is in the reported KL statistics;
- this does **not** establish which table produces better task answers.

Performance cost of BF16 vs IQ4_NL through ~232-237K is within roughly **-2.3% to +1.0%**, i.e. noise-level in this
streamed-expert configuration. The cost is disk capacity, not resident RAM.

Project-51 PLE ladder is therefore refined to:
1. stock IQ4_NL — compatibility/capacity baseline;
2. **FP8 — practical production-fidelity candidate**;
3. **BF16 — exact source-value control and quality ceiling arm**.

Promotion requires labeled task/agent evaluation; KL alone cannot choose the production winner.

This supersedes the overly strong prior wording that treated FP8 as essentially BF16-equivalent.

## NEW — MLX #4596 merged: generic long-context SDPA gets a real M1-family speedup

PR:
https://github.com/ml-explore/mlx/pull/4596

Merged in-window at **2026-10-03 10:48 UTC**.

The generic `sdpa_vector_2pass_1` path now unrolls four independent K/V loads per inner iteration to expose more
memory-level parallelism.

M1 Pro measurements:
- 32Q/32KV, 4K: **667.5 -> 474.5 us (1.41x)**;
- 32Q/32KV, 32K: **5964 -> 3597 us (1.66x)**;
- GQA4, 32K: **697.8 -> 469.6 us (1.49x)**;
- smaller GQA2 cases: ~1.04-1.06x.

Qwen3.8-27B's exact GQA6/head-dim-256 shape was **not measured**, and the specialized GQA kernel is unchanged.
Nevertheless, Qwen3.8's pre-M5 geometry has historically missed MLX's specialized GQA route, so this is directly
relevant upstream headroom.

Project-51 consequence:
- rebase any custom M1 engine on a revision containing #4596;
- measure the exact 24Q/4KV/head256 16/32/64/96/128K single-row decode shape before writing a replacement;
- no 25-TG target move without exact M1 Max/model evidence.

## UPDATE — MLX #4598: Q4/Q5/Q6/Q8 medium-alignment gather-QMV improves on M1

PR:
https://github.com/ml-explore/mlx/pull/4598

Older PR, updated in-window, still open.

Adds a one-pack fast path for affine gather-QMV shapes aligned to K%256 but not K%512.

M1 Pro results:
- Q4 K=768,N=2048: **92.2 -> 83.6 us (+10%)**;
- Q5 K=768,N=1024: **76.4 -> 63.3 us (+21%)**;
- Q6 K=384,N=1024: **61.4 -> 52.9 us (+16%)**;
- Q8 K=384,N=1024: **56.4 -> 50.5 us (+12%)**.

Controls move only ~1-2%.

This directly informs the user's Q4/Q5/Q6/Q8 M1 tuning question:
- higher-bit controls are getting cheaper upstream;
- our engine should benchmark current MLX affine paths before implementing custom GEMV for those controls;
- DASLab/ByteShape GGUF allocations still need either efficient native GGUF kernels or a faithful conversion/mapping
  to MLX-friendly per-tensor formats.

No numeric single-M1 TG target change.

## RECOVERED OLDER EVIDENCE + UPDATE — TensorFold ROCm Qwen3.8-27B materially strengthens the RX-prefill experiment

PR #100:
https://github.com/ashhart/TensorFold/pull/100

Older branch, updated in-window; closed/unmerged.

On one Radeon AI PRO R9700 32 GB / 640 GB/s:
- Qwen3.8-27B MLX 4-bit + DFlash2;
- cold PP: **1834 @2K, 2121 @8K, 2069 @16K**;
- longer prompt overall: ~2049 @4K, 1992 @16.7K, 1890 @30.9K;
- DFlash2 decode around **96-126+ TG** on the short public fixtures, strongly acceptance-dependent;
- long-context 12-row verify measurements extend experimentally through **120K**;
- ROCm implementation includes WMMA prompt/tree attention, FP8 prompt GEMMs, packed drafter estimate and optional
  FP8 KV.

This card is substantially stronger than the RX6800 and has twice the VRAM, so **do not transfer the numbers**.
The important result is implementation feasibility: the dense-27B CUDA engine already has a real ROCm port with
drafted-vs-serial and chunk/resume correctness tests.

PR #144:
https://github.com/ashhart/TensorFold/pull/144

Older branch, updated in-window, open. It adds a ROCm **GGUF** path on Strix Halo using Gufo kernels:
- fast GGUF prefill quantizes activations to Q8_1 and uses W8A8 WMMA;
- one-row decode uses Gufo GEMV;
- exact verify is kept separate;
- measured UD-Q4_K_XL prefill ~**193 PP** on an 8651-token prompt vs 77 PP exact;
- fast vs exact prompt arithmetic changed 6/16 tested replies, so it is not a fidelity-preserving substitution.

Project-51 RX6800 plan:
- use TensorFold #100/#144 as implementation mines, not production branches;
- first adapt/validate the **DASLab IQ3_S-MTP GGUF** on gfx1030;
- preserve an exact-prefill control because fast W8A8 prompt arithmetic can change trajectories;
- still require exact single-RX6800 16/32/64/96/128K PP before assigning bridge credit.

## RECOVERED OLDER EVIDENCE — DASLab publishes integrated-MTP 27B artifacts

Hugging Face:
https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF

The `*-mtp.gguf` files are integrated builds, not separate draft files. For the first Project-51 quality lane:
- IQ3_S target-only: ~**11.8 GB**;
- IQ3_S-MTP integrated: ~**12.1 GB**;
- IQ3_XXS-MTP integrated: ~**10.4 GB**.

DASLab's own discussion confirms `--spec-type draft-mtp` uses the included head directly.

This is older evidence, recovered because the user explicitly reopened the single-M1/RX producer lane.

Project-51 artifact identity:
- **primary quality experiment = IQ3_S-MTP integrated**;
- target-only IQ3_S = serial/control arm;
- IQ3_XXS-MTP = capacity/speed arm;
- ByteShape quality/speed siblings remain comparison arms.

## NEW — Strata #608: 204800 becomes an explicit native-context fallback, but the setup estimator remains conservative on 64 GB

PR:
https://github.com/Niko1221/Strata/pull/608

Created **2026-10-03 08:44:38 UTC**, open.

Adds **204800** between 131072 and 262144; no RoPE scaling is needed.

RTX 4080 16 GB + 62 GB usable host, IQ3_XXS, int8 KV:
- 128K shallow decode: 94.1 TG;
- 200K shallow: **85.1 TG**;
- a **203,259-token** prompt: **3093 PP / 68.6 TG**.

Important for our exact IQ3_S lane:
- setup estimates IQ3_S at 204800 as **77.1 GB RAM** and therefore still recommends only 128K on a nominal 64-GB
  PC;
- this is the conservative setup estimator, not a new physical failure receipt;
- prior same-memory-shape manual IQ3_S 256K evidence remains stronger for actual admission.

Project-51 interpretation:
- **200K remains the first fallback if native262K fails qualification**;
- do not lower the ~95% native262K fit prior because setup's heuristic estimate is conservative by design.

## NEW — Strata #603: large-context top-k prefill gets much faster on pre-Hopper CUDA, not the 5070-Ti cluster path

PR:
https://github.com/Niko1221/Strata/pull/603

Created **2026-10-03 07:31:13 UTC**, open.

RTX 3060 / IQ3_XXS / max-context262K:
- 61K PP +8.7%;
- 123K +9.5%;
- 153K +14.1%;
- 186K +16.5%;
- 243K **743 -> 934 PP (+25.6%)**.

The new wide top-k kernel replaces the old fallback when the register kernel no longer fits.

But the PR explicitly leaves the **sm_90+ cluster path unchanged**. The user's RTX5070Ti already uses that newer
cluster path, so these percentages do **not** transfer to Project-51's primary GPU.

No target move.

## NEW — Strata #614: optional near-tail checkpoint can make branched agent edits much cheaper

PR:
https://github.com/Niko1221/Strata/pull/614

Created **2026-10-03 10:36:23 UTC**, open.

Optional `--prompt-cache-tail` adds one checkpoint near the prompt end on an existing chunk boundary.

One 33.8K branch fixture:
- reusable prefix: **18,432 -> 30,720 tokens**;
- branch TTFT median: **17.05 -> 4.47 s (-73.8%)**;
- fresh prompt: +0.9%;
- local logits/teacher-forced controls reported bitwise/KL-equal under the frozen configuration.

This is not conversation parking and does not change the initial “parking OFF” rule.
It is a promising later optimization for the user's branch/edit-heavy coding-agent workload.

## NEW — Strata #577: 0.1.38 unbuffered file tier can regress mapped UD-Q4 prompts; native IQ packs are not implicated

Issue:
https://github.com/Niko1221/Strata/issues/577

On RTX5090/96GB/Windows, hand-made UD-Q4_K_XL GGUF-in-place:
- 0.1.38 unbuffered file tier is ~15-40% slower than 0.1.34;
- `STRATA_UNBUFFERED_LOAD=0` restores/slightly beats prior PP.

The reporter explicitly notes Swift IQ3_XXS/IQ3_S native packs on the same machine improved **~11-20%** at 14.7K/28.9K.

Therefore:
- no Project-51 IQ3_S primary regression;
- if we later test mapped/UD-Q4 controls, record buffered vs unbuffered file-tier behavior.

## NEW — Strata #606: persistent repeated-token degeneration has a plausible non-finite-activation lead, but no general Strata conclusion yet

Issue:
https://github.com/Niko1221/Strata/issues/606

One 0.1.35 / RTX5090D / IQ3_S / ~155K long agent session eventually entered a persistent state where subsequent
requests emitted one repeated token until engine restart.

Follow-up source inspection notes Q8_1 activation quantizers store a raw 32-value sum into fp16; sufficiently large
outliers can overflow that sum to inf. That is a plausible deterministic NaN source, but:
- the exact failure was not reduced to a minimal reproducer;
- the GPU was running a significant memory overclock, itself a co-suspect;
- the report predates 0.1.38.

Project-51 action:
- add a cheap repeated-token/non-finite degeneration canary to the 8h/24h soak;
- do **not** lower zero-stall/stability priors from this single confounded report.

## NEW — oMLX #4225: SpecPrefill + TurboQuant currently destroys prefix reuse

Issue:
https://github.com/jundot/omlx/issues/4225

M1 Ultra 64 GB / Qwen3.8 hybrid model:
- SpecPrefill creates plain `KVCache`;
- next turn expects `TurboQuantKVCache`;
- cache type mismatch truncates the prefix to zero every turn.

Observed 32.5K -> 52.3K session:
- without SpecPrefill, TTFT 2.5-7.2 s with prefix reuse;
- with SpecPrefill, TTFT **76 -> 97 s**, `cached 0` every turn;
- decode/MTP acceptance improve, but repeated prefill dominates latency.

Project-51 custom-engine rule:
- speculative prefill, KV compression and saved-prefix state must share an **identical cache-state type/provenance**;
- a speed feature that changes cache representation without migration invalidates resident-agent reuse.

## UPDATE — TensorFold #247: INT8 KV remains a strong dense-27B long-context control

Older PR updated/closed in-window.

One DGX Spark, Qwen3.8-27B:
- int8 KV halves attention-cache bytes;
- drafted-round time vs BF16 improves ~7% @90K, ~10% @180K, **~13% @242K**;
- serial token attention gains grow to ~20% at 242K;
- prompt fill stays within ~2%;
- startup estimate at native262K drops ~37.4 -> 30.4 GiB for the MLX 4-bit lane.

Quality sample changes in both directions and needles pass; it is not proof of bit-equivalence to BF16.

For our custom M1/RX 27B lane:
- use **INT8/Q8 KV as the first compressed long-context control**;
- only pursue more aggressive KV after exact continuation/agent quality tests.

## OTHER strict-window checks

Searched:
- Strata;
- oMLX;
- TensorFold;
- MTPLX;
- Splash;
- Ishizuki;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- TurboQuant;
- mlx-serve;
- DASLab/Hugging Face;
- ByteShape/public sources.

No newer Strata engine release than **0.1.38** found.
No strict-window TurboQuant repository change.
No strict-window Ishizuki or Splash change.
No new strict-window DASLab/ByteShape benchmark table.

Adjacent items with no target transfer:
- llama.cpp #29901 speeds Qwen3.8-Flash-Next's 4-head Lightning indexer prefill on CUDA, not M1;
- vLLM #56148 reinforces the same multi-row long-context verifier principle on CUDA split-K;
- SGLang #42372 adds Qwen3.8-27B SSD weight streaming on a 6-GB CUDA laptop, useful architecture evidence but
  far below the performance class of our RX producer;
- vLLM #59764 shows hybrid-GDN batch non-determinism can be large when several sequences share a step, reinforcing
  the rule that deterministic source/AA tests run B1/frozen before concurrency qualification.

## Target state after this pass

1. Primary Windows baseline: **Strata 0.1.38**.
2. IQ3_S/native262K fit: **~95%**.
3. Windows 16GB/64GB admission: **~90%**.
4. 8h / 24h zero-stall: **~75% / ~55%**.
5. #481-style automatic containment: **~85%**.
6. 200K/204800 remains the first fallback if native262K fails.
7. PLE ladder: stock IQ4_NL baseline -> **FP8 practical production candidate** -> **BF16 exact source control**;
   FP8 is **not** treated as source-equivalent.
8. Single-M1 27B target remains **25 TG / 110 cold PP**.
9. Custom M1 engine base: current upstream MLX including #4596; benchmark #4598 if merged/cherry-picked before
   writing replacement Q4/Q5/Q6/Q8 GEMV.
10. Custom M1 27B bespoke priority remains the long-context multi-row GQA verifier and state/cache lifecycle.
11. Primary 27B artifact: **DASLab IQ3_S-MTP integrated (~12.1 GB)**; IQ3_S serial and IQ3_XXS-MTP controls.
12. RX6800 prefill producer: TensorFold ROCm/GGUF branches are implementation mines; no numeric PP credit yet.
13. Dense-27B compressed-KV first control: **INT8/Q8**, not an immediately more aggressive format.
14. Native Windows production target remains **262,144**.
15. No hardware purchase change.

## New hard boundary

**2026-10-03 11:00:49 UTC**
