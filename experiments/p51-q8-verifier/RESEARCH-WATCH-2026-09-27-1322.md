# Project 51 primary-lane research watch — 2026-09-27 13:22 ET

**Freshness boundary:** canonical boundary entering this pass was **2026-09-27 17:04:18 UTC**. Strict-window evidence is limited to material published or materially updated after that time through the user cutoff **2026-09-27 17:22:18 UTC**. Same-day/older items that the immediately preceding watches missed are explicitly labeled **RECOVERED CURRENT** or **RECOVERED OLDER** rather than being reclassified as NEW.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- single-M1 dense 27B: **25 TG canonical**
- Flash quant search: **~3.0–3.6 transformer BPW**, with source-like production preference still around **~3.3–3.6** until AA~40 certification says otherwise
- 5070 Ti + Strata: first-class experimental Flash serving lane, but still requires exact-hardware and AA~40 certification.

The main change is **experiment priority and correctness gating**, not the forecasts.

## RECOVERED CURRENT + UPDATE — mlx-serve #594 sharpens the Flash quant sensitivity map

Source: https://github.com/ddalcu/mlx-serve/issues/594  
Created **2026-09-27 17:00:32 UTC**, four minutes before the prior watch cutoff; materially updated through **17:11:11 UTC**, so it is recovered rather than called a strict-window NEW item.

On M5 Ultra 256 GB / Flash-Next mixed-4/8, the experiment keeps these tensors at 8-bit:
- lm_head / embeddings
- hyper-connections
- router gate
- GDN a/b
- attention k/v
- indexer
- PLE
- MTP head

It requantizes these to 4-bit in the **mid48** arm:
- GDN qkv/z/out
- attention q/o
- shared expert (~2.88 GB)

Measured same-boot forward microbench:
- S=1 forward: **~11.2% lower GPU ms**
- S=4 verify: **~4.9% lower GPU ms**

Quality/behavior probe:
- MMLU-Pro 400 questions: mixed run1 **340**, mixed run2 **338**, mid48 **346**, all4 **342**
- output tokens vs mixed run1: repeated mixed run **+2.9%**, mid48 **+4.7%**, all4 **+12.8%**
- 8,192-token-cap hits: **3 / 4 / 3 / 7**
- four-stream decode: mid48 **39.0 t/s/request**, mixed **39.1 / 38.9**, all4 **37.5**

Interpretation:
- **mid48 is a valuable tensor-sensitivity prior**, not AA~40 certification.
- The all4 arm is the more important negative: pushing hyper-connections/router/GDN-sensitive paths down too appears to alter length/runaway behavior beyond the repeat-run baseline.
- This independently supports Project 51's policy of protecting state/routing/indexing/MTP-sensitive tensors while compressing less-sensitive trunk/expert mass first.
- It also suggests a concrete candidate arm where **GDN qkv/z/out + attention q/o + shared expert** can be tested lower than the protected tier.
- M5 Ultra evidence receives **zero direct M1 speed credit** and the 400-question MMLU/coding probes are not a substitute for our xhigh/coding/tools/long-context/semantic-continuity suite.

## RECOVERED CURRENT — oMLX #4012–#4018 is unusually useful mechanism evidence

Sources:
- https://github.com/jundot/omlx/issues/4012
- https://github.com/jundot/omlx/issues/4014
- https://github.com/jundot/omlx/issues/4015
- https://github.com/jundot/omlx/issues/4016
- https://github.com/jundot/omlx/issues/4017
- https://github.com/jundot/omlx/issues/4018

These were created earlier on Sep 27 and missed by the immediately preceding watch. They are **RECOVERED CURRENT**, not strict-window NEW.

M5 Ultra / oQ5e Flash-Next roadmap baseline:
- 24K prefill: **3,978 PP with MTP on / 4,100 MTP off**
- decode: **181 TG** on the canonical Lightning-MTP workload
- realistic coding prompts: **142–169 TG**
- MTP off: **78 TG**
- 24K prefill time breakdown: **MoE 39% / GDN 24% / QSA 20% / hyper-connections 11%**

The mechanism details matter more than the absolute M5 numbers:

1. **#4012 — Metal command-buffer caps.** TensorFold observed that binding ~420 MB expert stacks can terminate command buffers under MLX's default byte cap. An empty kernel binding them was reported at **28 us vs 12 us** after raising the cap. oMLX also sees the same unchanged runtime at **77.5 TG from CLI vs 73.0 TG from the menu-bar launcher**, root cause not yet established. This is direct support for measuring command-buffer boundaries/launcher environment rather than assuming a kernel roofline.

2. **#4014 — row-exact MTP verification.** On four realistic greedy prompts, oMLX Lightning MTP diverged from MTP-off on **3/4** at near-tie tokens because batched verify arithmetic changes with row count. TensorFold's row-invariant verify path was byte-identical to serial on **4/4** of the same prompts. This is a high-priority P51 verifier rule: performance certification needs **row-count invariance / serial-vs-verify logit tests**, not merely "the full target verified the draft."

3. **#4015 — byte-exact decode fusions.** Candidate savings include passing routing picks/renormalized weights from gate/up to down rather than recomputing top-10, fusing the PLE lookup currently represented by many small ops, and eliminating hidden gathers/copies. This aligns with our Apple7 dispatch-control thesis.

4. **#4016 — hyper-connection prefill is ~11% of 24K PP**, represented by ~97 small memory-bound modules per forward. This is a concrete fusion target, not a reason to lower HC precision.

5. **#4017 — MoE + GDN remain the big PP terms.** Routed-expert matmuls are reported around **53 TFLOPS vs ~98 TFLOPS** for a dense Q5 matmul of the same size; simple weight reuse explains only part of the gap. GDN is **~24% of prefill** even with an existing native kernel. Profile before rewriting.

6. TensorFold on the same M5 machine is reported as **~36% faster in decode but 8.8x slower in default 24K prefill**, with **~9% higher prose perplexity** for its 4-bit checkpoint. That is exactly why P51 should mine mechanisms, not copy a runtime or transfer M5 headline TG.

**P51 consequence:** our M1 PP program should explicitly profile **MoE / GDN / QSA / HC** separately, and the verifier program should add row-invariance + command-buffer accounting. No M1 forecast moves.

## RECOVERED CURRENT — oMLX #4021 confirms speculation policy is workload/sampling dependent

Source: https://github.com/jundot/omlx/issues/4021

On M5 Ultra / Flash-Next oQ4e, one newer Lightning-MTP path is reported to:
- hurt **greedy fixed-depth** decode by about **9.2%**
- hurt default adaptive greedy by about **3%**
- be near neutral or positive under sampled top-k
- improve one 2K code prompt by **~9–30%**

This is stronger evidence for Project 51's existing rule: verifier/draft policy is not a single global depth. Route by **sampling mode + workload + measured acceptance/cost surplus**, and freeze greedy and sampled rulers separately.

## RECOVERED OLDER — DFlash #172 proves recurrent rollback can make "lossless" speculation lossy

Source: https://github.com/z-lab/dflash/issues/172  
Opened **2026-09-23**; missed by prior P51 consolidation.

The Hugging Face DFlash reference loop verifies a block, then calls cache crop on rejection. For hybrid GDN targets, the reported Transformers cache crop trims convolution state but **does not restore the recurrent state mutated by rejected draft rows**. After the first partial acceptance, target logits therefore depend on tokens that were never committed.

Reported evidence:
- greedy HF generate and DFlash output diverged on identical prompts
- with a fixed text and alternate rejection patterns, one pattern had **0/384** target-argmax differences while another produced **12–41/384**
- first divergent margins were **0.6–2.4**, too large to dismiss as ordinary rounding
- snapshotting/restoring GDN recurrent state and replaying only accepted rows removed the effect
- a perfect drafter, with no rejected rows, was unaffected

Scope: this issue is for the HF reference implementation; it does not establish that SGLang/oMLX/Strata share the bug.

**P51 correctness gate:** for hybrid speculation, rollback means **restore recurrent/conv/temporal state to the committed boundary and replay only accepted rows as required**. A normal attention-KV crop is insufficient. Add adversarial partial-acceptance patterns to the exact-verifier suite.

## RECOVERED CURRENT — vLLM #58894 independently shows prefix reuse can poison DFlash acceptance

Source: https://github.com/vllm-project/vllm/issues/58894  
Opened earlier on Sep 27, before this strict boundary.

On Qwen3.8-family hybrid GDN + DFlash2 + prefix caching, vLLM 0.30.0 reports normal variable acceptance until the first positive prefix-cache hit, then **acceptance pins to 0% for the rest of the process** while the drafter continues proposing. A second report on RTX 6000 Ada sees a related failure as an illegal memory access on a long hit; a referenced fix restoring the correct recurrent-state/block-size geometry lets the same hit complete with acceptance remaining **~33–46%**.

This is not direct P51 performance evidence. It is independent support for a strict cache-state identity gate:
- recurrent checkpoint position must match token lineage
- prefix-hit state and speculative/draft state must share authoritative geometry
- test first-hit transitions, not only cold requests
- fail closed rather than silently accepting a prefix state whose recurrent boundary is ambiguous

## UPDATE — Strata #29 means the CUDA lane needs a long-generation liveness soak

Source: https://github.com/Niko1221/Strata/issues/29  
The issue was updated at **2026-09-27 17:04:30 UTC**, 12 seconds after the prior boundary.

RTX 4090 + 192 GB RAM / IQ3_S / 262K context:
- generation starts around **75 TG**
- decays into the high-50s during a very long output
- one run hard-stalled at generated token **58,303** with GPU still at 100% and CPU no longer progressing
- the reporter says a newer v0.1.11 attempt still reproduced a stall, this time much earlier (~7.7K generated tokens)

No root cause is established, and this is not the user's 5070 Ti. It gets **zero throughput-target credit**.

But it changes the 5070-Ti acceptance test: a 256-token benchmark is insufficient to call Strata production-ready. Add a **long-generation liveness/soak arm**, tracking forward progress, GPU power/utilization, CPU activity, free VRAM and expert/KV residency over time.

## STRICT-WINDOW scan after 17:04:18 UTC

- **mlx-serve:** no additional qualifying performance commit after #580/#584; a docs/benchmark-chart commit at **17:22:43 UTC** is after the user cutoff and excluded.
- **oMLX:** no post-boundary commit; the #4012–#4018 material above is recovered same-day evidence.
- **Ishizuki:** no new commit or new planning-grade M1 receipt after the boundary. Keep the existing audited M1 verifier mechanisms; do not invent freshness.
- **TensorFold/DFlash2:** no new M1 Max physical receipt. DFlash's current public guidance still recommends **verify block <=5** for quantized Qwen3.8 under stock MLX; this remains mechanism evidence, not M1 target credit.
- **Strata:** no post-boundary performance commit; #29 is the relevant liveness update.
- **DASLab/GSQ-RCO:** no new strict-window quality receipt. Existing 3.0/3.5-BPW evidence stands.
- **SGLang / llama.cpp / vLLM:** post-boundary commits were unrelated to P51 performance except issue-level state/correctness material already classified above; no new exact M1/5070-Ti receipt.
- **Reddit "silent bottleneck":** no additional planning-grade receipt beyond the prior watch. The useful part remains the systems hypothesis already promoted: synchronization, launch topology, state materialization and residency can dominate realized speed.

## Project 51 actions promoted by this pass

1. Add a **mid48-style quant arm** to the Flash quant matrix:
   - high precision: HC, router, GDN a/b, attention k/v, indexer/QSA, PLE, MTP, norms/head/embed
   - candidate lower tier: GDN qkv/z/out, attention q/o, shared expert
   - routed expert bank remains the primary compression budget
   - certify on AA~40 behavioral suite before any promotion.

2. Add **row-count invariance** to verifier certification:
   - serial S=1 vs S=2–5 verify logits
   - exact/near-tie token agreement
   - separate greedy and sampled rulers.

3. Add **hybrid rollback/cache-hit adversaries**:
   - partial acceptance at recurrent-block boundaries
   - repeated shared-prefix hits
   - cold -> first-hit -> later independent request transitions
   - recurrent-state snapshot/restore parity
   - multi-request isolation.

4. Add **per-component PP timing** on Apple:
   - MoE / GDN / QSA / hyper-connection / PLE
   - command-buffer count/bytes and host gaps
   - whole-chunk GDN experiment remains high priority.

5. Add **Strata long-output soak** on the actual 5070 Ti before declaring it a daily-driver server.

## Canonical planning effect

**Targets unchanged.**

The new evidence strengthens the *implementation* case, especially the tensor-sensitivity map and exact recurrent rollback requirements, but does not supply a new physical 2x-M1/TB4 receipt or an exact 5070-Ti measurement that justifies moving forecasts.

## New hard boundary

**2026-09-27 17:22:18 UTC**
