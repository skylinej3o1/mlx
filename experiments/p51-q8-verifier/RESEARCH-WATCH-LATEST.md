# Project 51 primary-lane research watch — 2026-09-27 00:12 ET

**Freshness boundary checked:** prior hard boundary **2026-09-27 02:24:13 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-27 04:12:29 UTC**, plus newly relevant older evidence for the proposed 5070 Ti prefill -> M1 decode lane.

## Decision

**No canonical TG/PP, quant-quality, or planning-confidence change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- central TG region **~39-41**, mature downside **~30-32**, target-only fallback **~24-27**
- single-M1 27B: **25 TG canonical target**
- RTX 5070 Ti 27B: **120 TG mature target / 250 cold PP baseline target**
- Flash quant search **3.0-3.6 BPW**, source-like hypothesis **~3.3-3.6**.

The useful change is architectural rather than a target move: production Flash traces show long-agent time dominated by repeated prefill when the hot cache silently trims the active session, while SGLang already proves that Qwen3.8 hybrid recurrent/QSA state can be transferred correctly across a prefill/decode boundary.

## Strict-window findings

### NEW — mlx-serve #575: an undersized prefix cache made real 80K+ agent traffic spend 11x more wall time prefilling than decoding

Source: https://github.com/ddalcu/mlx-serve/pull/575  
Merged **2026-09-27 02:58:58 UTC**.

The old qwen4_exp default was a fixed 2-GB hot cache. With 12 attention layers and the server's actual KV geometry it retained **81,920 tokens**, so an active 100K-160K conversation reused only the first 81,920 and re-prefilled the rest each turn.

Real traffic:
- **12,421 logged requests** total
- **116 prompts >80K**
- those 116 spent **1.11 hours in prefill** versus **0.10 hours decoding**
- logs repeatedly showed reuse such as `81920/111997` and `81920/164228` despite ~127 GB free.

Controlled M5 Ultra / Flash-Next mixed4/8 + MTP follow-up, ~98K prompt:
- fixed 2 GB: **81,920 / 98,338 reused**, turn-2 **TTFT 4.83 s**
- Auto one-session budget: **98,287 / 98,336 reused**, **TTFT 0.24 s**
- computed hot-cache budget **7,761 MB**.

The budget explicitly includes the retained recurrent/SSM checkpoints that the cache entry will bill.

**P51 consequence:** cache capacity must be expressed as a full active-session state bill, not 'N GB of KV'. For a long-running coding agent, trimming the active conversation a few tens of thousands of tokens below its working depth can dominate the whole runtime even when decode is excellent.

### NEW — full PLE GPU residency is now opt-in because the first forward can turn the 30-GB mmap into catastrophic memory pressure

Source: https://github.com/ddalcu/mlx-serve/commit/d500d429989a25d2571f9ef10b1ae81960b4fa32  
Committed **2026-09-27 03:43:09 UTC**.

The previously measured GPU PLE arm no-copy wraps the **~29.8-GB** n-gram table. Important newly documented behavior: the mapping may be cheap at load, but the **first GPU forward makes the whole table resident**. The static working-set check passed on a 128-GB Mac with roughly **10 GB free**, and a first **13-token prefill took 19-106 seconds** under pressure. The host gather, by contrast, faults in only rows actually read.

The server therefore now leaves PLE GPU gather **off unless `--ple-gpu` is explicitly requested**.

**P51 consequence / correction:** retain #539's lesson that PLE-induced host synchronization can cost double-digit decode at deep context, but do not solve that by resident-mapping ~30 GB on a 64-GB M1. Our desired arm is **SSD/demand-paged capacity + no mid-round host barrier**, probably via bounded hot GPU-visible rows or asynchronous staging.

### NEW — recurrent prefill can be overwhelmingly launch-bound when the sequential rule is expressed per token

Source: https://github.com/ddalcu/mlx-serve/pull/574  
Merged **2026-09-27 02:49:43 UTC**.

Different model but useful mechanism: Nemotron-H Mamba2 previously used a fused step only for <=16 rows; a normal prompt chunk fell back to ~12 dispatches/token/layer plus a host eval every 32 steps. The new kernel walks the entire chunk in internal 16-row passes while retaining recurrent state in registers.

M5 Max 64 GB, 4K prompt:
- before: **407 / 435 / 444 PP**
- after: **3,571 / 3,958 / 3,987 PP**
- decode stays essentially unchanged.

**Classification:** exact-window stronger-chip / different-recurrence mechanism evidence only.

**P51 consequence:** dedicate an Apple7 experiment to a whole-chunk GDN recurrence kernel before assuming M1 27B/Flash prefill is fundamentally bandwidth-limited. No 9x transfer estimate is permitted; the useful evidence is that recurrent prefill can hide an enormous dispatch/host-control tax.

## Newly relevant older evidence — 5070 Ti prefill -> M1 decode

### RECOVERED OLDER — SGLang #36651 already transfers full Qwen3.8-Flash-Next hybrid state across PD

Source: https://github.com/sgl-project/sglang/pull/36651  
Merged **2026-09-12**.

This is much stronger support for the proposed heterogeneous prefiller than generic KV-disaggregation documentation. Flash-Next explicitly requires and transfers:
- ordinary full-attention KV
- **PLE short-convolution state**
- **PLE n-gram history**
- **QSA pending raw-key/RoPE ring state**
- **compressed QSA keys**
- request/global attention/QSA metadata needed to map state across layouts.

Matching TP4 -> TP4 aggregate vs 1P1D Mooncake PD passed **12/12 matrix cases, 84 requests, 2,730 generated tokens, zero output-token-sequence mismatches**. Heterogeneous TP1->TP4 and TP4->TP1 Mooncake variants also achieved exact output-token parity.

This directly answers the architectural question: **Qwen3.8 hybrid state is transferable across the prefill/decode boundary without recomputing the model.**

### RECOVERED OLDER — SGLang #40501 composes PP prefill + native MTP on Flash-Next

Source: https://github.com/sgl-project/sglang/pull/40501  
Merged **2026-09-22**.

GB300 Qwen3.8-Flash-Next:
- reference TP4 aggregate + MTP: **GSM8K 0.980, accept length 3.16**
- **PD prefill TP2xPP2 + MTP -> decode TP4 + MTP:** **0.980, 3.16**.

The implementation transfers the draft MTP QSA pending keys, RoPE state and compressed keys as well. This demonstrates that prefill-side parallelism and a warm native speculative state can coexist with PD.

**P51 consequence:** the proposed 5070-Ti-prefill/M1-decode experiment is no longer speculative at the model-architecture level. The open research problem is the **canonical CUDA<->MLX state representation and numerical identity**, not whether a hybrid Qwen can be disaggregated.

### Proposed first experiment

Do not start with networking or 96K. First certify:

**32K CUDA prefill -> export canonical state -> MLX import -> compare next logits/tokens against native-MLX prefill.**

Only after parity:
1. extend 32K -> 96K;
2. measure export/import bytes and latency;
3. add bidirectional state mirroring so CUDA receives M1-generated-token state rather than re-prefilling history;
4. then benchmark end-to-end TTFT against native M1 PP.

State identity must carry a strong model/quant/config fingerprint, token lineage, position/RoPE identity, per-layer KV, recurrent/GDN state, and any warmed draft/MTP state.

## Community / Reddit / Ishizuki freshness check

No new planning-grade independent **32-core M1 Max 64K/96K/128K** result appeared after the prior boundary. Searches continue to surface the already-recorded Splash M1 depth curves and older M1 MLX-vs-llama PP comparisons. Ishizuki had no new commit inside this strict window.

## Lower-priority strict-window activity

- vLLM NIXL now tears down a dead peer's state immediately rather than waiting for TTL; useful hygiene for a future remote prefiller but no performance receipt.
- mlx-serve's remaining commits in the window are app/agent UI and registry changes.
- SGLang's strict-window changes are unrelated ROCm/router work.
- no qualifying new DS4, oMLX, Splash/MTPLX, llama.cpp Apple, APEX/GSQ, IST-DASLab or Model-Optimizer performance result appeared.

## Canonical planning state after this pass

Unchanged. The new evidence shifts priority toward **prefix/state reuse and heterogeneous prefill**, not a higher TG forecast.

`RESEARCH-STATE.md` is updated with the prefix residency rule, corrected PLE residency interpretation, recurrent-prefill mechanism evidence and the 27B heterogeneous P/D experiment lane. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 04:12:29 UTC**
