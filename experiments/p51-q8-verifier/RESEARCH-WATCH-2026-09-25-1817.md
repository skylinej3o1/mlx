# Project 51 primary-lane research watch — 2026-09-25 18:17 ET

**Freshness boundary checked:** prior hard boundary **2026-09-25 19:36:59 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-25 22:17:26 UTC**, plus a community/Reddit re-check for M1/M2 run data.

## Decision

**No canonical TG/PP, quant-quality, or planning-confidence change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

The main fresh result is directly relevant to verifier policy: on dual-die M5 Ultra, a fused MTP verify path helps grouped verification but can hurt solo decode, and the gain varies sharply by group width. No exact M1/PP2/TB4 Flash receipt appeared.

## Findings

### NEW — mlx-serve #534: fused MTP verify kernels must be gated by verify-group width on dual-die Apple

Source: https://github.com/ddalcu/mlx-serve/pull/534  
Merge commit: `2a93a011ec1d3ce61372952d3adca198c0cb95fa`, merged **2026-09-25 21:45:17 UTC**.

Test setup from the PR:
- **M5 Ultra 256 GB**
- macOS 27.0
- Qwen3.8-Flash-Next mixed-4/8bit
- MTP enabled, `--mtp-typical 0.2`
- 400-token code answers, greedy for the grouped sweep
- lookup on
- three alternating rounds, median by point.

Median aggregate-generation effect of the fused verify kernels with the new group-aware gate:
- **1 stream: unchanged**
- **2 streams: +4%**
- **4 streams: +13%**
- **8 streams: +1%**.

Earlier ungated A/Bs explain why the gate is needed. A 4-stream run moved roughly **195/194/191 -> 206/210/215 TG**, while one solo sampled run moved roughly **213/211/212 -> 196/196/206**, a **~5-7% regression**. The merged policy therefore enables the nine fused verify kernels on dual-die `applegpu_g17d` only when `group_rows > 1`. Single-die M5 remains enabled. A follow-up opcount check on a solo greedy request found the gated PR and base **byte-identical for every forward/opcount column**, confirming the residual solo timing difference was noise.

Greedy decode, 8K prefill, decode-after-32K, and GSM8K/MMLU-Pro quality were reported flat across arms.

**Classification:** NEW exact-window stronger-Apple / exact-Flash-family grouped-verifier evidence.

**P51 consequence:** verifier dispatch policy must include **chip topology and actual S/row-group width**. Do not assume a fusion that wins at S=4 wins at S=1 or S=8. The observed curve is explicitly non-monotonic. This is very relevant to P51's multi-row PP2 verifier design, but it does not provide a direct Apple7 or TB4 speed multiplier.

### REDDIT / M1-M2 re-check

No new clean **32-core M1 Max** 32K/64K/128K table and no new M2 Splash depth curve was visible by cutoff. The previously recorded 24-core M1 Max replication and M1 Ultra image-analysis runs remain the strongest independent same-day community receipts.

A same-day r/oMLX comment adds one lower-value datum: an **M1 Max 64 GB** screenshot around **29 TG** for an 8-bit Qwen3.8-27B MTPLX setup described as FP16-adapted to M1. The searchable comment exposes no context length, PP/TTFT, output length, MTP acceptance/depth or complete recipe, so it is **not planning-grade** and does not modify the Apple7 curve.

Broader current search also resurfaced known older exact M1 oMLX depth data (**18.9 TG @1K -> 10.3 @128K** on the stock 4-bit lane) and older M2 receipts. These are pre-boundary and remain background, not NEW evidence.

### NON-QUALIFYING strict-window activity

- vLLM's in-window commits were frontend/CI/API/ROCm maintenance without a P51-relevant Qwen3.8 inference receipt.
- Splash upstream's in-window commits were HTTP/chat-chain fixes rather than kernel/runtime throughput changes.
- SGLang activity was cache/LoRA/frontend infrastructure, with no new relevant Flash/MTP receipt.
- no qualifying post-boundary performance change appeared on DS4, oMLX, MTPLX, APEX/GSQ, IST-DASLab, llama.cpp, the M1 Splash fork, or NVIDIA Model-Optimizer.

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

`RESEARCH-STATE.md` is updated with the verify-group-width policy evidence. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-25 22:17:26 UTC**
