# Project 51 primary-lane research watch — 2026-09-26 09:10 ET

**Freshness boundary checked:** prior hard boundary **2026-09-26 09:37:04 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-26 13:10:08 UTC**, plus newly surfaced older/same-day M1 evidence classified separately.

## Decision

**No canonical TG/PP, xhigh-quality, or planning-confidence change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

The biggest newly surfaced evidence is the second M1-Splash kernel pass: attention itself is now nearly 2x faster on Apple7 through 176K context. It materially narrows one software uncertainty but still leaves dense-27B decode at ~14 TG in the 128-157K band, so it is not a reason to inflate the Flash-Next/PP2 forecast.

## Findings

### RECOVERED OLDER — Splash-M1 Part 2 nearly halves Apple7 long-context attention cost

Release: https://github.com/paperniuk/splash/releases/tag/1.0.2-m1.1  
Release published **2026-09-25 21:02:13 UTC**, before the previous hard boundary; therefore **RECOVERED OLDER**, not NEW.

Same **M1 Max 32-core / 64 GB** as the original Part-1 work. The new Apple7/8 register-matrix path replaces the remaining MPP attention implementation (and separately the Qwen3.6-35B expert path). For Qwen3.8-27B:
- short decode remains around **~40 TG**;
- **51K-context decode: 20 -> 25 TG**;
- cold **38K TTFT: 359 -> 312 s**;
- attention per layer: **1.85-1.95x faster** for decode/verify and prompt processing from **8K to 176K**;
- at **176K**, per-step 27B attention falls from roughly **215 ms -> 116 ms**.

Quality receipt from the release:
- 27B next-token top-1 agreement with upstream kernels: **99.84%**;
- 54/54 physics/arithmetic word problems before and after;
- mismatches inspected were near-ties.

**P51 consequence:** direct proof that an Apple7-specific attention path can remove roughly half of the long-context attention component at 176K. That is particularly relevant to our QSA/full-attention Apple7 work, but it is dense-27B Splash/DFlash rather than Flash-Next/QSA and gives no direct PP2 multiplier.

### RECOVERED SAME-DAY — optimized M1 Max depth curve now reaches 157K

Part-2 community report: https://www.reddit.com/r/LocalLLM/comments/1wqngu9/splash_on_m1_part_2_35ba3b_at_144_toks_on_a_2021/

Real OpenCode session, Qwen3.8-27B, medians by context:
- **30-64K: ~30 TG**
- **64-96K: ~20 TG**
- **96-128K: ~20 TG**
- **128-157K: ~14 TG**.

The author notes text/draftability matters; some 150K+ turns still exceeded 25 TG. This is the first surfaced deep Apple7 curve after their attention rewrite.

One commenter independently reports an M1 Max run with **6,929 input / 6,272 cached / 939 output, TTFT 7.1 s, 38.9 TG**. It confirms the build runs well but is not deep enough to change the long-context model.

**P51 consequence:** two-sided evidence. Apple7 long-context kernels clearly have significant software headroom, but even after the attention rewrite a dense 27B node does not remain near 40 TG at ~128K. Flash's sparse QSA, lower active compute, quant plan and multi-row PP2 verification remain necessary rather than optional.

### NEW — Splash rolling checkpoints need replacement rights on a full SSD tier

Source: https://github.com/incoai/splash/commit/85e1ba3c380a5ef4f402a19c43e31df68292a65a  
Committed **2026-09-26 12:05:31 UTC**.

Previously, rolling checkpoints consumed only free disk-tier quota. Once the tier reached its normal steady state full of cached prefixes, checkpoint writes failed. If the active request then suspended for memory, it replayed its prompt from the beginning rather than resuming progress.

Measured on **24-GB M6 / Qwen3.8-27B UD-IQ3_XXS / 2-GB disk tier / 60K request**:
- first token: **514 -> 263 s**
- replayed tokens: **96,888 -> 39,576**
- failed rolling checkpoints: **19 -> 0**.

The request holds only one rolling checkpoint and retires the old one before writing the new one, so at most one state-sized cached object is displaced; the commit reports **187 MiB** for this model.

**P51 consequence:** SSD progress/checkpoint storage must be designed for steady-state full occupancy, not an empty-tier benchmark. Reserve or reclaim a bounded checkpoint slot and make checkpoint replacement lineage-aware.

### NEW — Splash fails closed on invalid sampled tokens after non-finite logits

Source: https://github.com/incoai/splash/commit/4ab94eb105d27d7f059a98b1852b7e511bce0e71  
Committed **2026-09-26 10:05:13 UTC**.

An all-nonfinite logit row can leave the sampling sentinel `0xffffffff`. Previously the sentinel could enter exact token history and be clamped to the last vocabulary id on the next verify input. The engine now rejects output tokens >= vocabulary size, fails only that lane with `model_result_invalid`, and publishes neither cache nor output for the poisoned lane while peers continue.

**P51 consequence:** every aggressive quant/kernel arm needs explicit finite-logit / valid-token fail-loud checks before committing target, draft or cache state. Lane-local numerical failure must not poison shared state.

### LOWER PRIORITY strict-window activity

- Splash also merged SSD KV/state tier infrastructure and 24-GB low-bit GGUF support; the rolling-checkpoint result above is the planning-relevant measurement.
- vLLM in-window commits were Elastic-EP accounting/security/CI changes with no relevant Qwen3.8 receipt.
- SGLang's in-window commits were mostly DP/overlap refactors and router CI, with no new P51-transferable throughput measurement.
- no qualifying new DS4, oMLX, mlx-serve, llama.cpp, MTPLX, APEX/GSQ, IST-DASLab or NVIDIA Model-Optimizer performance commit appeared inside the strict interval.

## Community / Reddit / HF scan

Fresh searches did not surface a new M2/M2-Ultra Splash depth curve or a new independent 32-core-M1 64K/128K benchmark. The new Part-2 M1 writeup is the major community update. Search also surfaced the already-recorded M2 Max 38-core oMLX Flash receipt (**33.2 TG / 292.5 PP @64K**) and older M1/oMLX/MTPLX material; these are not reclassified as NEW.

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

`RESEARCH-STATE.md` is updated with the Apple7 attention receipt, SSD checkpoint replacement rule and fail-loud numerical invariant. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-26 13:10:08 UTC**
