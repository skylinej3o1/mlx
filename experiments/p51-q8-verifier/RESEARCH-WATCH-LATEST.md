# Project 51 — Strict Six-Minute Delta and Reconciliation — 2026-10-30 07:28 EDT

**PRIOR hard cutoff**: **2026-10-30T11:22:56Z**, from committed byte-identical [2026-10-30 07:22 watch](./RESEARCH-WATCH-2026-10-30-0722.md) and previous LATEST. **NEW current user request end**: **2026-10-30T11:28:36Z**; interval is **strictly AFTER 11:22:56Z through 11:28:36Z** (5min40sec). **NEW HARD FRESHNESS BOUNDARY = 2026-10-30T11:28:36Z**. Do not treat earlier research from [07:22 report](./RESEARCH-WATCH-2026-10-30-0722.md) as discovered within the tiny delta. This dated file is an **addendum**, not a copy of the 20K-character 07:22 research watch; together the immutable pair records both periods.

## Why this watch is short

The user issued a second "search and update" while the previous comprehensive run was still being reconciled. Actual GitHub branch readback at start confirmed [RESEARCH-WATCH-2026-10-30-0722.md](./RESEARCH-WATCH-2026-10-30-0722.md) and `RESEARCH-WATCH-LATEST.md` were **identical blob SHA 77ee91213503af3b8cb66d12d3286a780766922d** with cutoff11:22:56Z, **but** `RESEARCH-DISCOVERY-SCRATCHPAD.md`, `RESEARCH-STATE.md`, `RESEARCH-TARGETS.md`, `AUTONOMOUS-METAL-OPTIMIZATION-PLAN.md` still described Oct29 21:15:12Z and had not been updated with the substantive 07:22 evidence. This run **reconciled all four files** and verified each write. New 07:28 LATEST must be identical to THIS dated addendum; 07:22 dated research report retains prior detailed numeric evidence.

## Lane A: short-window ten-repository direct-source commit/issue/PR delta

GitHub connected account scans executed again, each using updated issues+PRs and recent main commits, for all **10 mandatory** repos:
- **jesdga95/basalt**: no in-window main commit or PR with new source experiment. GitHub search surfaced new [issue #161](https://github.com/jesdga95/basalt/issues/161) RTX5060 sm120 CUDA illegal-instruction prefill — direct issue.created_at **2026-10-30T11:29:08Z**, exactly **32 seconds AFTER** user-request cutoff. **EXCLUDED, queue for NEXT watch**; do not count as fresh safety finding here.
- **Niko1221/Strata**: no in-window qualifying PR, issue or main commit.
- **ashhart/TensorFold**: older [issue #1510](https://github.com/ashhart/TensorFold/issues/1510), created **2026-10-27T23:10:32Z** and updated **2026-10-30T11:27:44Z**, has a different-model three-GB10 GLM CUDA large-window cache-starvation example, but no separately dated new physical experiment identifiable from body. **UPDATED OLD / content useful, not a new benchmark.** PRs #1631/#1632 are Nemotron speech, not QFN. Old #1549 last update at 11:28:46Z **after cutoff**, irrelevant.
- **jundot/omlx**: no new qualifying issue, PR or main commit within the 5min40 interval.
- **ddalcu/mlx-serve**: no new qualifying issue, PR or main commit within interval.
- **paperniuk/ds4**: no new qualifying issue, PR or main commit within interval.
- **antirez/ds4**: no new qualifying issue, PR or main commit within interval.
- **Anbeeld/beellama.cpp**: no new qualifying issue, PR or main commit within interval.
- **ggml-org/llama.cpp**: no new qualifying issue, PR or main commit within interval.
- **vllm-project/vllm**: several old PRs updated, no independently dated substantive new QFN performance result within the 5min40 window. [LeapQuant #64725](https://github.com/vllm-project/vllm/issues/64725) originally created **11:20:50Z** and last edited **11:22:56Z**: fully accounted in 07:22 prior watch, **NOT new after cutoff**; do not double-count.

Supplementary source crosscheck: [ISTA original source quant README](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/blob/main/README.md) still describes original IQ3_S **54.8GB transformer +28.8GB separate n-gram**, not a newly verified optimised source pack during these minutes; separate [ISTA Coder Oct17 update](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF) is older, pruned distinct architecture and explicitly NOT substitute for base source. Targeted external searches found no new source-original QFN mixed-quant ShapeLearn/ByteShape artifact or AREX2 QFN same-source derivative confirmed in interval. No automated source was silently considered latest on crawl date alone.

**Lane A result:** **zero newly source-dated, material owner-target performance benchmarks, source model/quant releases or main merges** inside strict six minutes. This is a **bounded negative finding**, not proof nothing exists anywhere. Do not invent late-source freshness from a search's modified index.

## Lane B: deep countercheck — oversized reserved KV can defeat conversation resume

**UPDATED OLD, not FRESH**: [TensorFold #1510](https://github.com/ashhart/TensorFold/issues/1510) concerns **GLM CUDA** TP3 on **three GB10**, not QFN original source or M1. In the original older report, `--parallel 4 --context 1048576` reserves **6,147 KV pages =38.27GiB**, leaving only **497MiB** available for prompt cache; a real64K second chat turn rereads in ~36s and 128K in~75s, despite free/idle pool pages. Configuring262144 instead reserves12.77GiB and leaves16GiB prompt cache; same-category repeat64K/128K chat turns resume at **0.386s /0.725s**. `--prompt-cache-gib 8` cannot fix admission because initial pool reserved before cache. Separate subtle countercheck: author notes raw token completion benchmark does not mark `history_len`/`user_end` and therefore does not trigger same cache reuse as **chat**; comparing one to other can falsely diagnose actual runtime failure or speed.
- Affected model, hardware, context configuration and measurements are **from Oct27 opened issue; exact update11:27:44Z does not establish new run**. Prior 07:22 and earlier oMLX long-agent dynamic KV findings stay distinct and non-transferable.
- Owner falsifier under HIGH approval: M1 original GSQ IQ3S cache budget actual vs configured 128K/262K, active vs parked agents, true chat/tool turns and raw completions as independent cohorts, page residency, free/swap and exact reused tokens. Avoid enabling extreme configured context if it makes cache admission impossible; this does not imply reducing required true occupied context below goal.

## Prior 07:22 material RECONCILED, not newly published in this six-minute watch

The interrupted prior [full 07:22 primary watch](./RESEARCH-WATCH-2026-10-30-0722.md) had already established: **MERGED [oMLX #4971](https://github.com/jundot/omlx/pull/4971)** M3Ultra QFN oQ4e eight long sessions KV-bank peak185.3→153.0GiB MTPoff and177.0→158.2GiB MTPon; **OPEN [#4970](https://github.com/jundot/omlx/pull/4970)** GDN sidecar write-amplification controls; **OPEN [vLLM #64725](https://github.com/vllm-project/vllm/issues/64725)** QFN MI355 recurrent INT8 LeapQuant state57.9→25.7MB but whole decode only1.08–1.13× at high concurrency, QFN GPQA91.6→90.4 and no MTP; **FRESH [TensorFold #1661](https://github.com/ashhart/TensorFold/issues/1661)** gfx1151 192GB QFN MLX4-inexact true261061 PP1489/serialTG34.20/MTP71.28, not source M1/6800; **UPDATED OLD [two-M4 Pro dense27B TensorFold #1432–1437](https://github.com/ashhart/TensorFold/pull/1437)** limited 1 greedy stream/no draft/no prompt cache; **OPEN [Basalt #149](https://github.com/jesdga95/basalt/pull/149)** IQ3S100K streaming disk snapshot helps only when RAM capture would have failed, not generic 17×; **OPEN [#155](https://github.com/jesdga95/basalt/pull/155)** verify width T1–8 invariant on5080 but overall spec4/spec8 still differs, **OPEN [#157](https://github.com/jesdga95/basalt/pull/157)** FP16 fixed GEMM; owner RTX5070Ti Linux actual IQ3S parity remains unmeasured; gfx1031 Win HIP different IQ3XXS +F16 prefill, RX6800 owner only16GB host. **These are older than THIS mini-window.** Exact detailed metrics and source limitations remain in the 07:22 watch, no duplication into FRESH section.

## GitHub reconciliation and next research boundary

This second update:
1. Rewrote `RESEARCH-DISCOVERY-SCRATCHPAD.md` with 12 ranked evidence-led leads (safety, M1 transient memory, SSD GDN, GDN recurrent quant, true high-context HIP, two-Mac limitations, owner RX6800 memory feasibility).
2. Prepended material findings to `RESEARCH-STATE.md` and `RESEARCH-TARGETS.md` including correct timestamp separation and **NO NUMERICAL TARGET CHANGE**.
3. Appended design-only, HIGH-gated acceptance protocols to `AUTONOMOUS-METAL-OPTIMIZATION-PLAN.md`.
4. Created this immutable dated addendum, then replaced `RESEARCH-WATCH-LATEST.md` with byte-identical content and verified HEAD/blob.

**Targets HOLD**: two independent M1Max64 original source IQ3S physically occupied128K coldPP>=425 TG>=40 and occupied262K coldPP>=400 TG>=35, 3–5 correct resumable xhigh coding/tool agents, source AA-like>=38; oQ5e/BF16 quality oracle, oQ4e fast comparator, proposed mixed transformer3.0/3.2/3.4/3.6bpw and distinct PLE/MTP. RTX5070Ti16/CoreUltra7265F64GiB DDR5 Linux, RX6800nonXT16VRAM **ONLY16GB host**, GTX1080 unchanged. No machine trial, tuning, production deployment, CI changes, remote additions, purchases or scheduled monitoring. Lifecycle **PROPOSED → HIGH-APPROVED → RUNNING → RESULTS → AWAITING-HIGH-REVIEW**.

**NEXT HARD FRESHNESS BOUNDARY: 2026-10-30T11:28:36Z.**
