# External runtime watch — 2026-09-18 09:32 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-18 09:21:44 UTC` through `2026-09-18 13:32:09 UTC`.

PRs, issues, comments/reviews, and default-branch commits were explicitly screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Current Qwen3.8-Flash-Next Hugging Face/community and oMLX benchmark surfaces were also searched. Evidence time means substantive measurement/investigation time, not crawler, merge, rebase, label, or generic bot activity.

## Executive result

**No exact active-topology dual-M1-Max/TB4 Q5 receipt appeared. Canonical numeric targets do not move.**

Flash-Next remains:
- canonical quant lane: **Q5-class / eventual ~5.x BPW**
- target topology: **2x M1 Max 64 GB / TB4**
- headline target: **40 tok/s sustained TG at ~128K active context**
- cold PP target: **400 tok/s**

Current planning confidence changes slightly:
- **40 TG @ ~128K: ~50%** (down from ~55%)
- **400 cold PP: ~65-70%** (unchanged)

The TG confidence reduction is driven by a **recovered older M1 Ultra Q5 receipt**: same M1 generation and target quant class, but an older llama.cpp runtime and a fused on-package Ultra topology rather than dual Max/TB4. It is strong enough to constrain the thesis, not strong enough to redefine the target.

The strongest strict-window additions are:
1. **DS4 #1056:** phase-correct prefill dispatch collapses chunk-size-dependent logit drift from order-1 values to ~1e-6 after prefill and <1e-3 through the checked decode steps.
2. **mlx-serve #438/#460:** HC+GDN fusions give +8.7% to +13.6% measured prefill on M5 Max, with the fused path holding roughly 1.86k PP through ~131K; additional combined prefill paths show more unisolated headroom.
3. **vLLM #57562:** async scheduling can incorrectly emit sampled tokens during incomplete chunked prefill under concurrency, corrupting output even with speculation and prefix-cache effects removed.
4. **oMLX #3732:** memory emergency logic must distinguish reclaimable Metal buffers from a true physical-cap breach.
5. **DS4 #1083:** overlapping cached expert compute with SSD miss reads yields ~7-8% repeatable CUDA decode gains, but a Metal-derived threshold is measurably wrong on CUDA.

## RECOVERED OLDER EVIDENCE — M1 Ultra Q5 target-quant anchor

Source:
- https://huggingface.co/apetersson/Qwen3.8-Flash-Next-GGUF
- historical context record dated **2026-09-07**

Configuration:
- **Apple M1 Ultra, 128 GiB unified memory**
- Qwen3.8-Flash-Next **Q5_K_M**
- Metal / llama.cpp
- MTP depth 2
- one slot
- batch 512 / ubatch 128
- temperature 0, seed 1234
- prompt cache off
- native 262,144 context with F16 KV
- BF16 n-gram table kept out of the Q5 trunk / lazy storage path.

Measured:
- 2,048 input / 256 output: **176.4 PP / 27.7 TG**
- 8,192 / 256: **175.8 PP / 31.8 TG**
- 261,888 / 23: **100.7 PP / 12.3 TG**
- a later card also preserves a 1,048,320-input historical row at **53.68 PP / 4.05 TG** under extended-context settings.

Native-context correctness/memory:
- all 261,888 input tokens processed
- **3/3 checkpoint codes recovered**
- no truncation/context shifting
- about **95.5 GiB peak system wired memory**
- swap did not grow.

Classification: **recovered exact M1-generation / target-Q5 physical receipt, but non-target topology and older runtime. Strong transfer evidence and an important counterweight.**

### Project 51 interpretation

This receipt matters because it attacks a different uncertainty from the low-bit M1 data. Q2/IQ1 showed that modern M1 Flash can remain useful at deep context; this Q5 receipt shows what the **actual target precision class** looked like on an M1-generation dual-die Apple system before the modern gathered-QSA / fused-GDN / newer MTP work.

It does **not** imply that dual M1 Max must reproduce 12.3 TG:
- the deep cell is ~262K, not 128K;
- the runtime is older;
- modern selected/gathered QSA removes substantial long-context work;
- the M1 Ultra's on-package fabric is not equivalent to PP2 over TB4;
- conversely, an Ultra can expose both dies to a single layer more efficiently than B1 pipeline stages across TB4.

The durable conclusion is therefore narrower: **40 TG @128K cannot be justified by aggregate M1 bandwidth alone.** It requires meaningful runtime uplift plus enough MTP/multi-row pipeline overlap to keep the two Maxes productively overlapped.

This is why 40@128K engineering confidence moves from ~55% to **~50%**, while the 40 target itself stays fixed.

## NEW — DS4 #1056: phase-correct dispatch restores chunk/logit invariance

Substantive comment at **2026-09-18 12:18:40 UTC**, commit `2d6a207`.

Problem:
- short prefill chunks/tails could select projection kernels intended for decode/batch work;
- F16/Q8 tile choices and split-K FP32 reductions changed prefill arithmetic;
- therefore changing prefill chunk size could alter state/logits carried into decode.

Setup:
- Apple M1 Max 32 GiB
- Qwen3.8-Flash-Next Q2
- Metal SSD streaming
- 1,024 cached experts
- context 8,192
- MTP disabled
- comparison against the earlier reference branch.

Before correction, maximum raw-logit differences versus reference included:
- 575-token fixture: **0.4221 prefill / 1.3767 decode**
- 5,760-token fixture chunk128: **0.4873 / 1.0015**
- same fixture chunk2048: **0.1793 / 0.4338**.

After phase-correct dispatch:
- prefill max error roughly **1.4e-6 to 1.9e-6**
- worst checked decode error roughly **3.2e-4 to 8.3e-4**
- **85 frontiers / 21,107,200 logit pairs** checked.

Most important for our qualification design:
- the 5,760-token fixture at chunk128 and chunk2048 produced **bit-identical logits at all 17 measured frontiers**, including subsequent decode after the correction;
- before correction, the two chunk widths differed by as much as **0.45611 after prefill** and **1.07523 during decode**.

The corrected dispatch retained decode/batch optimized kernels and restored reference arithmetic for contiguous prefill/tails.

Performance check for the correction itself:
- 575/chunk128: prefill 34.931 -> 34.682 PP (-0.7%), decode 5.402 -> 5.487 (+1.6%)
- 5,760/chunk2048: prefill 141.779 -> 145.376 (+2.5%), decode 5.013 -> 5.420 (+8.1%), but the author explicitly treats the decode increase as preliminary whole-model behavior, not a kernel-speed claim.

Classification: **new exact M1 correctness evidence; Q2/SSD-streaming rather than target Q5/resident topology.**

### Project 51 action

Chunk-size qualification now has **two independent gates**:
1. throughput/memory sweep across chunk widths;
2. state/logit invariance across those chunk widths.

Final-text equality is insufficient. Near-ties can hide large numerical drift until a later token flips.

Also record the execution phase explicitly in any compiled/kernel dispatch cache key. A prefill tail is still prefill; it must not inherit a decode-optimized arithmetic contract merely because M is small.

## NEW — mlx-serve #438 / #460: long-context prefill fusion headroom

At **2026-09-18 13:03:59 UTC**, #438 received post-merge full-model measurements.

Setup:
- M5 Max 128 GB
- macOS 26.5
- Flash-Next mixed-4/8
- prefix cache off
- MTP/PLD off
- KV quant off
- prefill chunk 8192
- three runs per rung
- one arm per boot.

HC+GDN fusions ON vs OFF:
- ~16.4K (17,085 tokens): **1488 -> 1618 PP (+8.7%)**
- ~32.8K: **1628 -> 1850 PP (+13.6%)**
- fusion-ON at ~65.5K: **1873 PP**
- fusion-ON at ~131K: **1858 PP**.

The OFF arm stopped serving during the 64K rung, so no controlled 64K/131K percentage is claimed. Fusion-ON drift was reported as -2.1%. Decode sat at **51-55 TG** in both arms with speculation disabled.

Issue #460, created **13:03:44 UTC**, records remaining unisolated prefill candidates:
- QSA-pair
- PLE-ahead
- PLE-packed
- grouped MoE prefill
- HC upmix.

As a **combination**, on top of a core config already containing QSA-pair/HC/GDN, one 64,947-token uncached HTTP timing reads:
- **2163.9 -> 2323.4 PP** (~+7.4%).

That single screen read does not assign causal credit to any path and is not promotion evidence. The issue explicitly calls for isolated A/Bs and quality/parity bars.

Classification: **new exact stronger-Apple / exact-model-family PP evidence; mixed-4/8 and M5, not target Q5/M1.**

### Project 51 implication

This supports keeping the **400 PP target and 65-70% confidence unchanged**. Modern Flash prefill has substantial architecture-level headroom even at ~131K, and HC/GDN fusion improvements are demonstrably long-context-stable on stronger Apple silicon.

Do not transfer 1.8k PP to M1. The value is that the model's prefill graph is still optimizable at large context rather than inherently saturated.

## NEW — vLLM #57562: incomplete prefill must never emit decode tokens

Issue created **2026-09-18 12:26:51 UTC**.

Setup:
- Qwen3.6-35B-A3B-FP8 hybrid GDN/attention MoE
- H100 NVL
- vLLM 0.29.0
- async scheduling on
- chunked prefill
- max-num-batched-tokens 8192
- max model length 262,144
- concurrency
- **no speculative decoding**
- prefix caching reproduced both on and off.

Observed:
- scheduler reserves no output placeholder for an incomplete prefill chunk;
- model runner nevertheless returns a sampled token for some such steps;
- placeholder count underflows and the assertion kills EngineCore;
- clamping the assertion exposes that the token would otherwise be appended, i.e. this is output corruption rather than bookkeeping only.

Controlled results:
- prompts <= batch-token limit / single chunk: **0 underflows across 18 requests**
- mixed multi-chunk prompts up to ~143K, 12 requests: **44 underflows**
- one ~143K request alone: **0**
- ~143K prompts: ~14 occurrences each
- ~42K: 4-5
- ~9K: 1
- prefix caching disabled: still fails
- async scheduling disabled: **24/24 complete, 0 underflows**
- reported throughput cost of disabling async scheduling was below that benchmark's noise floor.

Classification: **new hybrid-GDN scheduler correctness evidence; wrong model/hardware, strongly transferable to Flash continuous batching.**

### Project 51 action

Add a mixed-length concurrent chunked-prefill test with speculation **off**:
- an incomplete prefill row may not produce/commit an output token;
- output-placeholder/token counts must remain exact;
- compare async and synchronous scheduler modes;
- verify final output and internal sequence frontier, not only absence of crashes.

This is separate from MTP/ragged verify correctness; it can fail without speculation.

## NEW — oMLX #3732: reclaimable Metal buffers are not a physical OOM

PR created **2026-09-18 09:39:52 UTC**.

Mechanism:
- concurrent long prefills can temporarily lower the dynamic memory ceiling below process footprint;
- several GiB of unused MLX Metal buffers may still be reclaimable;
- old background enforcement could treat that dynamic ceiling crossing as an emergency and abort all requests before the scheduler reclaimed the pool.

Change:
- emergency abort uses stable physical cap / Metal cap;
- dynamic ceiling remains for admission and soft/hard pressure;
- first soft-pressure tick asks scheduler to return pooled Metal buffers.

Validation:
- 208 memory-enforcer/prefill-guard tests pass;
- no live large-model replay at cutoff.

Classification: **new Apple runtime memory-lifecycle fix; tests only, no performance receipt.**

Project 51 rule:
Fit/pressure telemetry must distinguish:
- live model/state
- reclaimable MLX cache/pool
- admission ceiling
- true physical/Metal hard cap.

Soft pressure should attempt deterministic reclamation before declaring a physical-fit failure.

## NEW transfer evidence — DS4 #1083: overlap thresholds are backend specific

PR created **2026-09-18 11:34:35 UTC**.

DGX Spark GB10 / DeepSeek-V4.1-Flash Q2 / CUDA SSD expert streaming:
- run cached expert hits while SSD misses read in parallel;
- gate/up for all misses are queued before down reads;
- down partials are summed in slot order;
- output/logprob hashes reported byte-identical.

Against current base `8db1d1d`:
- round D: **10.70 vs 9.83 TG (+8.0%)**, 3/3 repeats
- round E: **10.57 vs 9.62 (+6.9%)**, 3/3.

An older set reported +6.5 to +12.3%.

Important negative:
- porting the Metal split threshold to CUDA produced only **+3.98%** versus the branch's **+6.89%** in the same round;
- on this backend, one expert read is ~321-411 us while a CUDA kernel launch is single-digit us, so splitting at one/two misses remains worthwhile.

Classification: **new non-target offload overlap evidence.**

Project 51 implication:
Never import an overlap/admission threshold from CUDA, Metal, or another Apple generation just because the mechanism is the same. Measure backend-local launch cost, read latency, hit rate and batch shape.

## NEW transfer evidence — vLLM #57555: offload copy thresholds are device specific

Issue created **2026-09-18 11:27:27 UTC**.

A30 measurements show the DMA-vs-Triton KV-offload crossover changes materially with both copy size and batch count, contradicting one H100-tuned global threshold. Examples:
- 8 KiB: crossover near N~32-64
- 1 KiB: closer to N~128
- 28-32 KiB: Triton can win from ~N=128 on A30 even though the H100-derived rule always selects DMA there.

Classification: **new non-target copy-path evidence.**

Project 51 implication:
PLE/KV/offload copy path selection should be a small measured surface by transfer size and concurrency, not one static threshold copied from another device.

## Strict-window items not promoted to target evidence

- vLLM #57548 routes Qwen4Exp QSA indexer top-k through a shared dispatcher but contains **no benchmark or correctness receipt** at the cutoff.
- vLLM #57560 adds an opt-in ROCm FlyDSL GDN prefill backend and has 8 unit tests passing, but its serving A/B and accuracy A/B are explicitly **pending**.
- vLLM #57318 has useful small-M GDN projection evidence on RTX 5090/GB10: Flash-Next's 96x2560 projection is roughly 3.0-3.5x faster at M=2-4 with the alternate kernel, while the same path can lose at M=1 and has no gain on B200/B300. This reinforces token-count/hardware-specific dispatch, but is not Apple evidence and does not move targets.
- oMLX #3672 received a large refactor/hardening update with 14,180 non-slow/non-integration tests passing, but no new physical Qwen Flash speed receipt in the strict window.
- oMLX #3735 is a startup/network-settings migration fix, not inference evidence.
- llama.cpp strict-window commits contain no new Flash-Next Apple target receipt.
- Hugging Face/oMLX community search found **no new exact dual-M1-Max/TB4 Q5 measurement** through the cutoff.

## Target / confidence decision

### Flash-Next dual M1 Max

**Hold the numeric target: 40 TG @ ~128K / 400 cold PP. Hold Q5-class as canonical quant.**

Updated ~128K TG planning ladder:
- >=30 TG: **~85%**
- >=35 TG: **~70%**
- >=40 TG: **~50%**
- >=45 TG: **~30%**
- >=50 TG: **~15%**.

Cold PP remains:
- >=250: **~97%**
- >=300: **~90%**
- >=350: **~80%**
- >=400: **~65-70%**
- >=450: **~45-50%**
- >=500: **~30-35%**
- >=600: **~12-15%**
- >=700: **~5%**.

Why TG confidence moves down modestly:
- the newly recovered M1 Ultra Q5 physical receipt shows only 27.7-31.8 TG at short context and 12.3 TG at ~262K on the older path;
- that is much closer in silicon generation and quant class than M5/Q2 transfer evidence;
- dual M1 Max over TB4 has a harder interconnect/state problem than an Ultra's fused package.

Why it only moves to ~50%, not lower:
- the old receipt predates much of the current gathered-QSA, GDN/HC and MTP work;
- it has no 128K cell;
- modern low-bit M1 results are materially faster;
- modern stronger-Apple prefill/decode receipts show substantial runtime headroom;
- PP2 plus multi-row/MTP overlap can change utilization geometry versus the old single-device path.

Why PP confidence stays:
- exact M1 low-bit PP around ~272-275 already exists;
- long-context M5 fusion-on PP remains ~1.86k through ~131K;
- PP2 can pipeline chunks much more naturally than B1 decode;
- current uncertainties are stage balance/chunking/TB4 and scheduler behavior, not evidence of an intrinsic Flash prefill wall near 400.

## New/strengthened qualification rules

1. **Phase is kernel identity:** short prefill tails cannot silently reuse decode/batch arithmetic.
2. **Chunk invariance is numerical:** compare logits/cache state across chunk widths, not text only.
3. **Incomplete-prefill output prohibition:** under concurrency, a row with prompt tokens remaining may not emit or commit a decode token.
4. **Reclaim before abort:** distinguish reclaimable Metal buffers from true physical-cap breach.
5. **Backend-local overlap thresholds:** measure transfer/read latency and launch overhead before setting hit/miss split rules.
6. Existing gates remain: admission latency decomposition, async PLE start/finalize, cross-request hidden-state probes, distributed progress telemetry, and mirrored/A-B-A noise-floor measurements.

## Hard freshness boundary

`2026-09-18 13:32:09 UTC`
