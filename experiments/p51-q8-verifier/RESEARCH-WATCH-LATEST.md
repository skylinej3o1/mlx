# External runtime watch — 2026-09-17 19:18 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-17 20:33:27 UTC` through `2026-09-17 23:18:58 UTC`.

PRs, issues, and default-branch commits were screened across DS4, vLLM, oMLX, mlx-serve/related MLX serving surfaces, and llama.cpp; relevant oMLX benchmark and Hugging Face model surfaces were also checked. Evidence time means substantive source/measurement time, not crawler, merge, rebase, label, or comment time.

The user also supplied a same-day oMLX M5 Max benchmark and a DragonScale quality receipt for explicit evaluation. Those are evaluated below even where their substantive timestamp is not inside the incremental window.

## Executive result

**No exact active-topology receipt appeared for any canonical target. Numeric targets do not move.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max 64GB: **25 tok/s TG / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s TG / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max 64GB/TB4: **15 tok/s TG / 180 tok/s cold PP**.

However, the new user-supplied M5 Max/oMLX receipt materially strengthens the architecture-level plausibility of the Flash-Next target: the same model family/runtime path sustains **64.6 tok/s at 128K** and **59.9 tok/s near 200K** while prefill remains **1,279 / 1,239 tok/s**. This is not M1/TB4 proof, but it is strong evidence that the model/runtime no longer inherently collapses at long context.

## Evaluated receipt — oMLX community benchmark dalhnt9f

Public benchmark page: Qwen3.8-Flash-Next-oQ4e-mtp on **M5 Max 40-core GPU / 128 GB**, oMLX **0.7.0.dev2**, macOS 26.5.2, Code (Mixed), TurboQuant KV 4-bit, Lightning MTP, thinking enabled.

The public page confirms:
- 1K: **960.8 PP / 65.4 TG**, peak listed 71.3 GB;
- 8K: **1,453 PP / 42.7 TG**, 72.3 GB;
- 16K: **1,405 PP / 67.7 TG**, 72.6 GB;
- 32K: **1,343 PP / 53.0 TG**, 73.1 GB;
- 64K: **1,293 PP / 63.5 TG**, 74.7 GB;
- 128K: **1,279 PP / 64.6 TG**, 79.0 GB;
- ~195K: **1,239 PP / 59.9 TG**, 80.8 GB;
- batching: B1 **65.4 TG**, B2 **93.3 TG**, **1.43x** aggregate speedup.

Resource telemetry for the 1K result reports peak footprint **86.04 GB**, MLX active peak **70.84 GB**, MLX cache peak **1.71 GB**, system used peak **96.68 GB**, GPU average **83.5%**, GPU max **100%**, thermal state nominal.

The public recipe confirms MTP enabled, TurboQuant KV4 enabled, speculative prefill disabled, DFlash disabled, and Qwen ANE prefill disabled. This matters: the high long-context PP/TG is not an ANE-prefill artifact and does not require DFlash.

Classification: **exact same-model-family oMLX/M5 performance receipt; strong architecture/runtime transfer evidence, not active-topology evidence.**

### Interpretation for dual M1 Max target

This is the strongest same-runtime evidence in the watch chain that **40 TG at ~128K is not blocked by Qwen3.8-Flash-Next's long-context algorithmic shape**. At 128K, M5 Max produces 64.6 TG, 61% above the Project 51 40-TG floor, while PP is >3x the 400-PP target.

But the receipt cannot be scaled by core count or memory bandwidth directly to dual M1 Max. M5 has newer GPU/Metal behavior; Project 51 adds TB4 distributed execution; the benchmark uses oQ4e rather than the preferred higher-quality lane; and its 79 GB listed peak / 86 GB footprint cannot fit unchanged on one 64 GB M1. The relevant question is now less “can Flash-Next remain fast at 128K?” and more “can we preserve enough of this efficient local execution after repartitioning across two M1 Max nodes and a quality-preserving quant lane?”

**Confidence direction:** upward for the architecture-level 40@128K target, but not enough to move the numeric target or promote the 45–50 stretch band.

### User-reported 390K session

The user supplied a report of medium-effort operation to ~390K session context with PLE SSD offload, ~1,200 tok/s prefill near the end and ~44 tok/s decode, versus prior long-context collapse. This is highly interesting long-session evidence, but those exact 390K numbers were not independently visible on the public benchmark page checked in this pass. Keep them as **user-supplied external receipt pending source-level verification**, not a canonical measured anchor yet.

If verified, the key implication is not merely speed: it would show that the gathered-QSA / SSD-PLE / cache stack can preserve useful throughput far beyond the 128K Project 51 qualification point.

## Quality receipt — DragonScale 98.75 / 100

The user supplied DragonScale run `run-QWEN38NF-JundotoQ4-001`, timestamped `2026-09-17T17:08:08.234467Z`, seed 42, model `UNOBTANIUM/Qwen3.8-Flash-Next-oQ4e-mtp`.

Reported deterministic score: **98.75/100**, no gate failures. Components included hidden suite 25/25, passability 12/12, replay 8/8, own tests 5/5, contract 8/8, git 5/5, human-play 30/30, packaging 2/2, and mutation 3.75/5. Visible tests: **13 passed / 0 failed / 0 errors**. Mutation panel killed 3/4 applicable mutants; `rng_seed_mix` survived. Human-play smoke completed successfully, including level progression, idle-time progression, quit handling, Ctrl+C responsiveness, and small-terminal overflow checks.

Classification: **strong task-level quality evidence for an oQ4-derived Flash-Next lane, but not a general model-quality proof and not an exact receipt for Jundot's artifact unless model identity/checksum equivalence is established.** The run's substantive timestamp predates the previous hard boundary, so it is evaluated here because the user explicitly supplied it, not counted as newly timestamped window evidence.

### Project 51 quality implication

This materially reduces concern that an oQ4e-style lane is automatically “too lossy to be useful” for agentic coding. It does **not** justify replacing the preferred Q6/Q8 quality lane or claiming broad benchmark parity. Add the oQ4e lane as a serious capacity/performance comparator in qualification, with checksum/provenance, deterministic replay, coding/eval suites, and long-context semantic checks. A 98.75 task-harness score can justify testing the lane; it cannot by itself certify general intelligence retention.

## Incremental source delta

No new oMLX, DS4, or llama.cpp default-branch commit in the strict window produced a new active-topology performance receipt.

vLLM had several default-branch merges in-window. The most architecture-adjacent was `db7a24c230a4db6ae3a568ed01b01f3f7172069d`, merge of #55960, adding fused DFlash2 grouped convolution. Its substantive PR work predates this window, so the merge timestamp does not make its measurements new evidence. Other in-window vLLM merges covered KV-cache release APIs, metadata/event plumbing, ROCm/GLM sparse-MLA boot correctness, CI/frontend, and MoE layout handling; none changes the Project 51 target distributions.

A same-day oMLX issue #3723 (created before the prior boundary) is an important caution for interpreting fresh-process benchmark numbers: on M3 Ultra 256 GB / oMLX 0.7.0.dev2 / Qwen3.8-Flash-Next oQ4e-MTP, a reporter measured pooled-median decode **20.48 tok/s after ~10h uptime** versus **66.45 tok/s after restart** on the same MLX 0.32.0 stack; MLX 0.32.2 fresh was 70.83 and custom kernels 73.85. The reporter attributes the decay to the backbone, while MTP remained ~90.8% acceptance / 3.20 tok per cycle. Cause is not isolated. This is older than the strict window and therefore not new evidence, but it reinforces that Project 51 must qualify sustained uptime, not only fresh-process peaks.

## New/strengthened qualification rules

1. **Long-context speed is now a two-part gate:** fresh-process 128K throughput plus sustained-session/uptime retention. A spectacular fresh M5 receipt does not supersede long-session stability.
2. **Quant lane is part of topology identity.** oQ4e performance can raise architecture confidence without directly certifying a Q6/Q8 target.
3. **Public benchmark recipe provenance matters.** Record MTP, KV quant, PLE offload, DFlash/spec-prefill, ANE state, thinking/sampling state, context, and memory telemetry with every receipt.
4. **Quality promotion requires artifact identity.** If a quality run names a repack/alias, establish checksum or tensor provenance before transferring the score to another named quant.
5. Add an **oQ4e comparator lane** to Flash-Next qualification because the current performance/quality evidence makes it a credible practical fallback, while retaining Q6/Q8 as the preferred quality-preserving target lane.

## Target decision

**Hold all canonical numeric targets.**

The M5 Max/oMLX receipt is a meaningful positive update. It moves the Flash-Next 40@128K target from being constrained by uncertainty about long-context runtime collapse toward being constrained mainly by **M1-generation silicon, dual-node/TB4 partition economics, memory fit, and quant-quality choice**. That is exactly the direction we wanted external evidence to move.

Do not extrapolate 64.6 M5 TG into a predicted dual-M1 number. The next decisive receipt remains exact dual-M1 Max 64GB/TB4 at ~128K with the intended distributed topology and quality lane.

## Hard freshness boundary

`2026-09-17 23:18:58 UTC`
