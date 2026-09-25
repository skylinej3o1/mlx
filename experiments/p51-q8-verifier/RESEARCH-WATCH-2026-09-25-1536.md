# Project 51 primary-lane research watch — 2026-09-25 15:36 ET

**Freshness boundary checked:** prior hard boundary **2026-09-25 18:16:37 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-25 19:36:59 UTC**, plus an explicit re-check of M1-related Reddit threads/comments for newly surfaced run data.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

The important change is evidentiary rather than numeric: a second independent M1 Max configuration now reproduces large Splash-M1 gains, and M1 Ultra comments finally contain real run data. The strict GitHub window also contains a large upstream Splash integration batch, but no exact dual-M1 Flash-Next receipt.

## Findings

### RECOVERED SAME-DAY — independent 24-core M1 Max reproduces Splash-M1 gains

Reddit: https://www.reddit.com/r/LocalLLM/comments/1wpza1i/a_breakthrough_for_m1_and_m2_macs/

Independent hardware:
- 2021 MacBook Pro
- **M1 Max, 24-core GPU, 64 GB**
- prebuilt `splash-m1 1.0.2-m1`
- Qwen3.8-27B Splash package.

Reported Qwen3.8-27B results:
- npanj five-prompt average: stock 4-bit MLX **16.0 TG** vs Splash-M1 **32.8**
- math: **46.6 TG**
- short code, reasoning off: **61.3**
- short prose: **18.3**
- code explanation @8K: **21.6**
- code explanation @32K: **17.1**
- four parallel requests: **62.3 aggregate TG**
- prefill @8K: **101 PP**.

The author says this is about **0.84x** the original 32-core M1 Max results, close to the expected hardware gap. Their reasoning-off quality suite (217 extraction/matching/counting/confabulation items + 50 GSM8K) was essentially tied with the comparison 4-bit MLX quant.

**Classification:** RECOVERED SAME-DAY independent exact-generation Apple7 evidence. Reddit exposes only calendar-day timing here, so it is not claimed as strictly post-18:16:37 evidence.

**P51 consequence:** substantially reduces one-machine/one-author risk around the M1 Splash result and is useful evidence that Apple7 small-row/multi-request kernels can sustain high aggregate throughput. It does not prove Flash-Next S=2-8 verification or PP2/TB4.

### RECOVERED SAME-DAY — M1 Ultra comments finally contain run data

Reddit: https://www.reddit.com/r/LocalLLM/comments/1woq7cd/you_can_now_run_qwen3827b_on_a_2021_m1_max_at_39/

An M1 Ultra 64-GB user reports:
- tiny-context `hi` response around **64 TG**;
- real image-analysis run: **955 input / 1,207 output**, **13.4 s TTFT**, **36.4 TG**;
- another run: **955 input / 1,047 output**, **5.8 s TTFT**, **48.4 TG**.

The same commenter says the overall image-analysis task took roughly four times as long as their regular MLX setup despite the high decode TG, which is a useful reminder that TTFT/prefill/vision-path cost can dominate end-to-end agent work.

Another M1 Max 32-GB user says the fork is faster and more consistent than oMLX and MTPLX and runs cool, but supplies no numeric benchmark. A commenter with a 64-GB 32-core M1 Max says they will report results, but no numbers were visible at cutoff. M2/M2-Ultra commenters were also still asking rather than reporting.

**Classification:** RECOVERED SAME-DAY community run evidence; exact comment times are unavailable from the public search surface.

**P51 consequence:** strengthens Apple7 portability/reproducibility and reinforces the split between strong decode and weak prompt/TTFT behavior. No numeric target transfer.

### NEW MERGED INFRASTRUCTURE — Splash upstream integrates several P51-relevant seams

Strict-window upstream Splash merges include:
- `804bb36b523`: stage <=2048-column, <=64-row RMS norms in threadgroup memory; source comments report **1.3-2.6x** dependent-norm kernel gains on M3 Max/M5 Pro;
- `df5462049fc`: prepare DFlash2 draft weights directly from the source checkpoint instead of relying only on prepacked package assets; exposes cleaner `--draft-model` experimentation;
- `514e5844062`: keep model-weight buffers Metal-resident between requests, unwiring only after a long idle period;
- `bfc3103e79d`: scheduler/KV release/memory-governor hardening and stronger atomic rollback/accounting;
- `06cafcb1e1c`: publish GGUF-vs-llama.cpp quality/speed comparisons and supported GGUF target rules.

Because the merge timestamps are in-window but some attached benchmark measurements may have been produced earlier, the performance numbers are **not** promoted as strict-window physical evidence. The implementation capabilities themselves are newly merged upstream.

**P51 consequence:** upstream Splash is becoming a better experimental host for independent draft-checkpoint/quant work and for mining few-row Apple kernels. For any custom drafter experiment, record source-checkpoint SHA, prepared-draft format/precision map, and preparation code SHA separately.

### NON-QUALIFYING strict-window work

- vLLM changes were CI coverage only.
- llama.cpp's in-window change was filesystem/path handling.
- the M1/M2 Splash fork itself only added an explicit unofficial-fork documentation marker in this strict interval.
- no qualifying performance update appeared on DS4, oMLX, mlx-serve, MTPLX, APEX/GSQ, ISTA-DASLab, SGLang, or NVIDIA Model-Optimizer.

## Canonical planning state after this pass

Unchanged:
- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target.
- RTX 5070 Ti 27B: **120 TG** mature target.

`RESEARCH-STATE.md` is updated with the independent M1 replication, M1 Ultra comment runs, and upstream Splash integration consequences. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-25 19:36:59 UTC**
