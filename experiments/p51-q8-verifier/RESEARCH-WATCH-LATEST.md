# Project 51 research watch — November 15, 2026, ~10:49 EST

**Previous verified strict cutoff:** 2026-11-15T14:32:00Z (minute-resolution). **New request cutoff:** 2026-11-15T15:49:00Z (minute-resolution, not independently established to a second). **Starting branch HEAD:** `98a756778c6505c2da93124d7c7f9c89d105e724`.

**Method:** checked GitHub commit history and recent issue/PR updates for Paperniuk DS4 `m1-flash-next`, Paperniuk Splash, antirez DS4, Splash, oMLX, Kapitsa, Basalt, Strata, TensorFold, Qwen Code, vLLM and llama.cpp; checked official Qwen Hugging Face organization and QwenCloud changelog; researched Qwen4 Chinese/English/Japanese coverage and discovered older quantization research. Only underlying events with dated evidence in the strict window are FRESH. A new comment on an old PR is UPDATED OLD; older techniques discovered now are REDISCOVERED, not fresh releases.

## A. Ranked executive findings (evidence-weighted, not claimed owner gains)

1. **FRESH M1-generation 6/8-bit verification GEMV:** [oMLX #5304](https://github.com/jundot/omlx/pull/5304), created **14:39:22Z**, OPEN. Extends `m1_verify_qmv` eligibility to 6- and 8-bit, 2–4 rows. On a **busy M1 Ultra**, 6-bit per-projection kernels improve 0–61% by shape; end-to-end Qwen3-4B-Instruct-2507 **6-bit**, 256-token requests, 2–4 concurrent decodes, best-of-8 rounds, gains 27–42% total throughput with prerequisite #5276 on both arms. Not measured: M1 Max 32-core, QFN original GSQ XXS/S, 27B/MTP/DFlash, physically 128K/259K, agent correctness, idle median. Not bit-exact vs stock qmv (fp16 max per-projection delta ~4e-3). **Promising for future 27B higher-bit resident workloads, not a new QFN performance claim.**
2. **UPDATED OLD M1-generation verify attention correctness caveat:** [oMLX #5300](https://github.com/jundot/omlx/pull/5300), opened before cutoff, new **14:42:50Z** CI correction comment [source](https://github.com/jundot/omlx/pull/5300#issuecomment-6896277908). M1 Ultra head-width128, plain KV, 3–8 armed verify rows; 4096 keys, four rows attention alone 6.58→3.04ms and 16384 keys 25.85→9.67ms, but whole-forward Qwen3-4B gains smaller (4096/T4 ratio 0.94; 8192/T8 0.84), **no end-to-end MTP tok/s** and greedy can diverge due to reduction order. The fresh item is *CI test hook reset*, not a new performance measurement.
3. **FRESH 27B cached-turn improvement on different hardware:** [Kapitsa #1276](https://github.com/nace-ai/kapitsa/pull/1276), created **14:58:09Z**, OPEN. M5 Pro 48GB **plain 27B MLX4** (not 27B KQuant, not M1): move tensor-tile GEMM threshold 64→17 rows. New cached 26–63-row turn prefills 208–301→150–173ms (~27–43% faster); cold random-token 4K prefill essentially flat ~5076 vs 5082ms; 192 logit records 0 top-1 flips, mean KL 3–6.5e-7 in chunk48 check, but 4,129-token actual text not tested. M5 matrix units **do not transfer to M1**. Decode ~17.6–17.9 tok/s unchanged.
4. **UPDATED OLD dense 27B agent risk:** [Kapitsa #1231](https://github.com/nace-ai/kapitsa/issues/1231) opened Nov12; **14:48:19Z** maintainer asks for high/low effort `chat:` log on report of Pi v1.5.2 looping with `27b:kquant` on **M4 Pro 48GB**. No reproduced cause or fix; note as agent quality/correctness gate, not proof that KQuant is intrinsically defective.
5. **UPDATED OLD Splash persistent cache adoption:** [Splash #772](https://github.com/incoai/splash/pull/772), opened before cutoff; **15:36:14Z** comment reports new-head CI: 221 desktop tests passing, native sanitizer and Python compatibility green, READY FOR REVIEW but still **OPEN**, optional model release gate skipped. Fix retries bounded EINTR mkdir/open for persistent-cache directory; no changed inference benchmark and no deployment. Useful to persistent agents and restart stability, not decode speed.
6. **UPDATED OLD Strata tool calls:** [Strata #6032](https://github.com/Niko1221/Strata/pull/6032) already open before cutoff; **15:00:14Z** CI note states a Linux keepawake test is flaky/failed (1 of 1716), macOS/Windows passed. The proposed parser recovers damaged openers, JSON arguments and type coercion, but **no live model session test**. Full correct tool execution remains unproven.
7. **FRESH Qwen Code verification isolation:** [Qwen Code #17185](https://github.com/QwenLM/qwen-code/pull/17185), merged **15:28:58Z**. Machine-enforced verifier boundary declaration (credential-free container or explicit waiver), atomic deduplicated watch state, event-driven wait discipline. Relevant as a **HaikuSwarm/Molt orchestration design analogue**, not an inference kernel.
8. **FRESH but dissimilar inference:** [Basalt #362](https://github.com/jesdga95/basalt/pull/362) merged **15:20:14Z**; **dual RTX5090**, Ryzen5950X/61GiB host, **Unsloth UD-IQ1_M** + peer access, 655.9 tok/s aggregate decode and 11,555.6 PP at64K. Does **NOT** predict a single RTX5070Ti16+64GiB original ISTA GSQ IQ3_S at physically32K and no draft. [Basalt #370](https://github.com/jesdga95/basalt/pull/370) build/testing gate merged15:37Z, not model performance.
9. **FRESH different-model Metal launch reduction:** [TensorFold #3442](https://github.com/ashhart/TensorFold/pull/3442), created **15:43:17Z**, OPEN, GLM5.3 Flash on **M5 Ultra**, 127 fewer launches/window, no-draft 71.8→74.6 tok/s (+3.9%) 48/48 token-equal replies; kernel-level bitwise tests. Shows optimization technique, **not M1 QFN owner result**.
10. **REDISCOVERED prospective quant quality-per-byte mechanism:** [llama.cpp #15550](https://github.com/ggml-org/llama.cpp/pull/15550), created **Aug2025**, still **OPEN**, targets chosen file size/bpw via imatrix-weighted per-tensor quantization error, Pareto set and Lagrangian bit allocation. Authors report matched/better KLD in 93% of 238 evaluations over 34 models, **not original GSQ QFN** and KLD proxy does not certify agent-task quality. Fresh window comment is banter, *not an algorithm update*. Worth source-specific trial design, separate approval for repacking.

## B. Qwen4 / Qwen4.5 (strict result and model sizing)

- OFFICIAL [QwenCloud model releases](https://docs.qwencloud.com/changelog/models) still list Nov11 **`qwen4-max-preview` API** as newest Qwen4 launch, not a Qwen4-Flash/27B open-weight announcement. [Qwen official HF organization](https://huggingface.co/Qwen) top visible recent model list is Qwen3.8 series; no visible official Qwen4-Flash/27B files in checked listing. Negative search evidence is **not proof of nonexistence anywhere**.
- PREVIOUSLY SOURCED October conference reporting named **Max / Plus / Flash / 27B** tiers; no verified Qwen4-Flash parameter count, 27B dense-vs-MoE architecture or official Flash-Next successor checkpoint in this 77-minute window.
- The **Qwen4-35B-A3B** hypothesis remains extremely weak (secondhand test of an A3B model without total size); independent [Whittle 35B-A3B](https://huggingface.co/whittleOrg/Whittle-Qwen-3.8-35B-A3B) shows architecture feasibility **NOT Qwen's roadmap**. The Nov11 flagship does not establish a Flash release schedule.
- The official [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) precursor **125B backbone (~6B active)+51B lookup+~4B MTP** cannot be imputed to Qwen4-Flash. No supported evidence settles **new pretraining vs post-training continuation**. `qwen4_exp` code name, Qwen Code client aliases and empty third-party HF repos are not weights.
- HOLD memory feasibility: QFN original GSQ XXS on M1 Max64 has historical ~57GiB residency near physically259K; larger equally quantized future Flash would tighten one-machine margin. If an actual 35B-A3B arrives, Q4/Q5 could be far more practical **subject to proven coding quality**; 27B would offer more quant headroom.

## C. M1 Max, Paperniuk, DS4/DFlash2

- Direct commit-history scan of Paperniuk `ds4:m1-flash-next`, Paperniuk Splash, antirez DS4, upstream Splash and oMLX main found **no commits dated 14:32–15:49Z** on checked branches; issue activity elsewhere does not imply those branches advanced.
- HOLD **original ISTA GSQ-RCO IQ3_XXS** measured on **2021 M1 Max 32GPU/64GB** in Paperniuk DS4: *physically occupied* 128K **PP278 / TG34.2**, 259K **PP258 / TG31.7**, near57GiB long context. Do not replace with configured-context figures, M1 Ultra or model swaps.
- DFlash2 integration previously measured code 37.3→41.8 and edit33.0→34.5 within changed kernel path; **not a controlled DFlash2 vs native MTP long-context comparison**. Draft acceptance, rewind and quant verification remain gates. Six-month 128K 40–48 / 259K 36–44 tok/s remain speculative ranges, **not achieved**. New #5304 suggests architectural headroom for certain models, not reason to revise these QFN ranges.

## D. Dense27B / smaller MoE / quant

- [Kapitsa #1276](https://github.com/nace-ai/kapitsa/pull/1276) M5-only cache-turn optimization is a good *experiment design*, not M1 evidence. Existing [Kapitsa #1194](https://github.com/nace-ai/kapitsa/issues/1194) M1 Max32 NE-assisted Qwen27B prefill improvements carried greedy drift; quality gate remains absent.
- Existing KQuant 27B Q4 quality KLD ~0.035 vs comparator~0.054, Q5 candidate and [MACaQ](https://github.com) IQ4_XS **cannot be equated** across unmatched evaluations; no new original GSQXXS-equivalent at smaller bytes proven.
- [Strata #6025](https://github.com/Niko1221/Strata/pull/6025) PRE-EXISTING/REDISCOVERED Gyro-L TQP5/6/7 Metal expert kernel path, open PR updated15:27Z: parity and one coding probe on Apple Silicon128GB, **not M1 64 or matched BF16-reference task quality**. Possible future trellis-quant research seed, not immediate substitution.
- Tencent dense27B DSpine approximately2B draft, native MTP and DFlash2 still need like-for-like agent-task A/B and exact output/tool correctness. No fresh matched trial.

## E. Relay and disaggregated inference

- HOLD [oMLX #5163](https://github.com/jundot/omlx/pull/5163) Nov11 merged CUDA helper: other M3 Ultra512GiB + two RTX A6000 48GiB, prefill QFN 1388→3574 PP and dense27B405→2079 at32K. **Not RTX5070Ti16→2021M1Max64**, not physically128/262K or exact source GSQ. No new oMLX main commit in window materially proves owner Relay.
- Critical correctness state for QFN: QSA KV and selective indexer, GDN/recurrent, PLE access, MTP/draft state, tokenizer/prefix parity and all numerical continuation, not a naked KV copy. Transfer time and actual TTFT are unknown. Two Macs are independent memory domains; 3–5 correct persistent agents not yet measured.

## F. NVIDIA/AMD and tool reliability

- Keep frozen first PC: **single RTX5070Ti16 / 64GiB host, pristine ISTA GSQ IQ3_S historical v2 `.basalt`, actual consumed32K, one slot, INT8 KV, `spec=1` NO DRAFT, original source/PLE SHA, CPU-double and executed tool-call parity**. Dual5090 UD-IQ1_M numbers do not move the target.
- No validated new 5070Ti originalGSQ32K result. RX6800 non-XT16VRAM + **only16GiB host**, so no implicit multi-64GB machine assumption.
- Strata parser PR and Pi looping reports are reminders that agent throughput requires **completed correct tasks, faithful tool JSON, no hangs, session restart safety, cache isolation**, not merely decode throughput.

## G. Exploratory discovery and skepticism

- Main fresh Qwen-family commit traffic in window was Qwen Code agent/verification work, not released weights. Qwen HF listing is stronger evidence than `qwen4_exp` package labels.
- [llama.cpp #15550](https://github.com/ggml-org/llama.cpp/pull/15550) **older rediscovery** has potential to optimize BF16 quality-per-byte under a hard 57GiB ceiling. Need actual QFN tensor support, PLE and MTP separately; no proof of equal IQ3_S quality in XXS bytes.
- oMLX M1 qmv and TensorFold GLM Metal both show kernel headroom on Apple generations, but model, bitwidth, GPU, verify mode and occupied context differ. Do not collapse independent speedups into a multiplicative owner forecast.

## H. Ranked next experiments (NOT EXECUTED; separate HIGH approval)

1. **Qwen4 artifact gate**: official Qwen/ModelScope/HF tensor index, actual config and weight files; verify total/active/body/PLE/MTP, license and release chronology. Watch, no model download.
2. **Same-source QFN DS4 comparison**: original GSQXXS, physical128K/259K, native MTP vs DFlash2 same prompts, task-completion+tool-call validity, memory/TTFT. Requires HIGH for execution.
3. **M1 Max higher-bit kernel fit**: investigate port of #5304 on resident 27B Q5/Q6 with matched logits and 1/2/4 agent slots, not 4B throughput extrapolation; HIGH to run.
4. **27B vs QFN agent suite**: fixed coding tasks, 27B KQuant Q4/Q5/MACaQ controlled provenance, Pi/OpenCode hang and tool-call recovery, long-context stability, BF16 KL/top1; HIGH to run.
5. **Relay feasibility proof**: first 5070Ti CUDA-helper layer budget and GDN/QSA/PLE state round trip on smaller prompt; then true32K–128K TTFT and full completed task; HIGH for owner execution.
6. **Quant exploratory**: theoretically budget-aware error allocation (#15550), source BF16 controlled calibration and PLE preservation; HIGH to repack.

## I. Repository accounting / strict next cutoff

Research documentation only. This watch is an immutable record of checked sources at **2026-11-15T15:49:00Z minute-resolution**. New changes to research README/state/targets/quant radar/scratchpad and technical note are tracked in the final committing change. **NO model downloads, installs, benchmarks, source-code mutations, CI or configuration changes.** Next query starts from this strict cutoff, regardless of commit wall-clock time.
