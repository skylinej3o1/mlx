# Project 51 — agent cache economics, correct state, and new Nov19 18:44 evidence

[Strict watch](./RESEARCH-WATCH-2026-11-19-1844.md) · source cutoff 2026-11-19T23:44Z, previous 2026-11-19T17:47:41Z.

## Most actionable correction

[Strata #6248](https://github.com/Niko1221/Strata/issues/6248) is **closed and the uptime cause is retracted**. A benchmark harness polluted boot configuration with `pcie_frac: 0.15`; do not propagate previous "uptime-dependent" root cause. Per-request override ineffectiveness on that reporter's rig should be investigated but is not universal proof. The independent SM80 control with 328 stable requests further narrows the problem.

## Cache economics for 3–5 agents

| Event | Source/hardware | Author-reported end-to-end effect | Limit |
|---|---|---|---|
| Underbudget 340K conversation snapshot | [Strata #6327](https://github.com/Niko1221/Strata/issues/6327), other PC | 331–342K reread ×5 at 19.5–20.1min; budgeted ~282K prefix reuse 99.86%, 3.8s prefill | Exact cache byte size, tools/chunk anchor and model runtime differ |
| Claude Code classifier prefix | [Strata #6214](https://github.com/Niko1221/Strata/issues/6214), RTX3090; new 2-Spark repro | 11.4K reread/5.85s → 287/1.37s; 2-Spark 21.31s cold →0.84/0.86s warm | Not M1; permission checks must retain correct deny/allow |
| Release weights but retain KV RAM | [Splash #787](https://github.com/incoai/splash/pull/787), M5 Max dense27B | 3.1→0.1GB cache RAM; 2.8GB SSD, next turn 4.7s incl weights | OPEN and no M1 GSQ long-session parity |
| First question after 128K doc | [oMLX #5430](https://github.com/jundot/omlx/pull/5430), M5Pro dense27B | ~8.4–9.7s→~2.7–3.1s | Some cold answers differ; native MLX not GGUF Splash |
| Native batch quant cache rollback | [oMLX #5253](https://github.com/jundot/omlx/pull/5253), other Mac | Before: 41→55GB during 2×128K batched verify and requests aborted | OPEN fix; independent quality unverified |

**Design implications:** cache budget must cover actual retained GDN+KV states, not only model weights; retain prefix identity and tokenizer/chat-template; after compaction the tool block must match or be deliberately re-rendered safely; SSD state must survive memory pressure and restart; a crash-first-answer must replay correctly; admission/decode scheduling must account for transient duplication.

## Fidelity before throughput

[Splash #788](https://github.com/incoai/splash/issues/788): different M4Max Qwen3.6 GGUF, greedy identical prompt, 3/9 fabricated write_file / 6/9 no completed reply while llama.cpp asked for missing info3/3. This is a severe **single-source report**, not a confirmed M1 QFN bug. [Strata #6316](https://github.com/Niko1221/Strata/issues/6316): in two of four other setups first reply after process restart omitted earlier nonce even though whole history was sent; second correct. [Basalt #429](https://github.com/jesdga95/basalt/issues/429) remains OPEN for literal tool closer truncation. [Strata #6315](https://github.com/Niko1221/Strata/pull/6315) OPEN schema repair. [TensorFold #3706](https://github.com/ashhart/TensorFold/pull/3706) MERGED Nov19 23:40Z, 18 cache miss reason codes and bounded metrics, diagnostic only.

## New runtime release, not a new owner model recommendation

[Basalt v0.5.0](https://github.com/jesdga95/basalt/releases/tag/v0.5.0) NEW 19:10Z adds Tencent Hy4-flash with DFly2; official [Tencent repo](https://github.com/Tencent-Hunyuan/Hy4-flash) has older-than-cutoff open weights and explains index/KV sharing. Basalt's pack is **158.7GB**, far above a single64GB M1 or 5070Ti16+host64; no same-source GSQ QFN crossover established. [Basalt loader #430](https://github.com/jesdga95/basalt/issues/430) now CLOSED, maintainer 21:52 says GPU-first main patch available, needs retest and desktop-stall still unresolved.

## Preserved physical constraints

- 2 separate 2021 M1Max32GPU64; original pristine ISTA QFN GSQ IQ3_XXS is minimum, IQ3_S preferred if practical; true physical128K PP278/TG34.2, 259K PP258/TG31.7 historic, no new actual benchmark.
- PC first test frozen: original ISTA IQ3_S historical .basalt v2, one 5070Ti16, CoreUltra7 265F, host64 DDR5-4800, physical32K, INT8 KV, 1 slot, spec1 NO DRAFT, CPU-double and full task/tool gates; no user hardware execution authorized.
- RX6800 non-XT VRAM16/host16; no results from other RDNA GPUs imply full model fit.
- No fresh Paperniuk old-M1 commits, no independently verified original GGUF oMLX partial CUDA helper or full CUDA→Metal QFN Relay.
- Qwen4-Flash size/config/weights remain unconfirmed in [Chinese Qianwen changelog](https://platform.qianwenai.com/docs/changelog/models) and [Qwen official HF](https://huggingface.co/Qwen).

## Recommended future research gates

1. Create exact agent side-effect fixtures + completed coding task pass/fail around prefill, cache hit, restored GDN, tool schema, first post-crash answer, and SSD pressure.
2. Budget two resident 128K–259K agents with measured model+KV+GDN+PLE+MTP and transient memory headroom; do not infer from just nominal64GB.
3. Before experimenting with new M1 cache work, require source GSQ IQ3_XXS 128K and259K functional and numerical parity, not M5 dense27B analogues.
4. Compare independent two-M1 agent service with any distributed proposal on completed correct work/hour; Full Relay still research only.
