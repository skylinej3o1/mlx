# External runtime watch — 2026-09-17 13:40 ET — independent rerun

## Search window

Independent completion pass over substantive source activity strictly after `2026-09-17 10:33:10 UTC` through the user-requested cutoff `2026-09-17 13:43:30 UTC`.

Evidence time means the substantive source / measurement timestamp. Merge, rebase, crawler, later edit, and comment times do not make older evidence new.

This rerun was required because the handoff stated that the prior pass had been interrupted. On inspection, branch HEAD unexpectedly already contained `RESEARCH-WATCH-2026-09-17-0943.md` in commit `a3bbe114da64b069989de98dfd238121ab0b9835`. I therefore treated that watch as an untrusted candidate and independently rescanned PRs, issues, and commits rather than accepting its claimed boundary.

## Executive result

**No exact active-topology receipt appeared for any canonical target. No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max 64GB: **25 tok/s TG / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s TG / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max 64GB/TB4: **15 tok/s TG / 180 tok/s cold PP**.

Flash interpretation is unchanged: sustained **40 TG at ~128K active context** is the core success floor; 45–50 is stretch; 50–60 is upside only. Short-context 40 does not satisfy the target. PP means cold prefill.

The earlier `09:43` candidate watch correctly captured the major PR/commit-level mechanism evidence, including the source-time-qualified original mlx-serve expert-streaming commit. However, it missed several useful in-window **issue-level** receipts. This watch supersedes `RESEARCH-WATCH-LATEST.md` and records the corrected complete pass.

---

## Coverage audit

### DS4

PR-level, issue-level, and default-branch commit scans found **no substantive source item created in the window**. No target evidence.

### vLLM

The full PR window was rescanned in split ranges to avoid result truncation. The important current-window items in the earlier candidate were independently reproduced: #57351, #57352, #57355, #57356, and #57358. Additional in-window PRs were screened and were not active-topology target receipts.

Default-branch commits were also scanned. Merge timestamps were not used as evidence time. Example: llama.cpp-style merge-time ambiguity was checked explicitly below; the same rule was applied to vLLM merges.

The issue-level scan found one important failure receipt and one planning-only RFC that the candidate watch omitted:

- **vLLM #57354**, created `2026-09-17 11:10:11 UTC`: DeepSeek-V4-Flash-0731 intermittently segfaulted during sparse-MLA mixed warmup on 4x MI355X / ROCm 7.2 / TP4 + expert parallel. One pinned nightly reportedly failed 4/5 identical startup attempts, without speculative decoding or client traffic. This is an **exact failure receipt on a non-target topology**, not performance evidence.
- **vLLM #57383**, created `2026-09-17 13:12:07 UTC`: RFC for asymmetric DeepSeek-V4.1 prefill/decode placement, with P handling `[0,N-128)` and D executing the final 128-token window through the full model. The author explicitly states there is **no prototype or benchmark**. This is **speculation/planning only** and cannot move a target.

### oMLX

PR-level scan reproduced #3713, #3715, and #3717. No default-branch commits landed with qualifying source timestamps in the window.

The issue-level scan found an important omitted durability receipt:

- **oMLX #3711**, created `2026-09-17 10:40:58 UTC`: M4 Pro 64GB, oMLX 0.6.4, Qwen3.8-27B oQ4e-MTP, TurboQuant KV4, Lightning MTP. Short tasks worked, but a longer coding-analysis workload reportedly ran about 15 minutes and then hit `OMLX stream timed out` after two attempts. The reporter saw the same failure with the 8-bit quant, repeated it on a clean session, and reported free memory never below 17GB. The model then would not reload even though the UI remained alive. This is an **exact failure/stability receipt**, not a throughput receipt and not proof of OOM.

### mlx-serve

PR-level scan found #449. The original implementation commit remains retrievable as `47c428b3e61d364ecc064518c31f373a57e42692`, author time `2026-09-17 13:31:25 UTC`, committer time `13:38:29 UTC`, both before cutoff. A later rebase produced a different commit with a post-cutoff committer time; that rebase does **not** create the evidence.

The original commit itself contains the benchmark and quality material, so the earlier candidate's use of #449 is validated under the standing timestamp rule.

### llama.cpp

PR-level scan reproduced #29027 and screened the rest of the in-window PR set. Default-branch commits were also scanned.

A merge-time trap was checked explicitly: #29014 merged at `11:53:55 UTC`, but its PR was created at `07:31:47 UTC`, before the previous hard boundary. It therefore remains older evidence and is **not** promoted into this window merely because it merged here.

The issue-level scan found an omitted backend-compatibility receipt:

- **llama.cpp #29028**, created `2026-09-17 12:47:20 UTC`: on Ryzen AI Max+ 395 / Radeon 8060S gfx1151 / 128GB UMA, Qwen3.8-Flash-Next UD-Q4_K_XL and DeepSeek-V4-Flash MXFP4 failed at first decode on Vulkan/RADV. Full offload hit a tensor-read OOB; a partial DeepSeek placement lost the Vulkan device. On the same GPU, the Qwen Flash checkpoint reportedly loaded and produced an 8-token completion at roughly **19 tok/s on ROCm**. That 19 tok/s is only a **very short sanity receipt on a different architecture/backend/quant topology**, not target evidence.

### HF / broader community screening

Fresh screening produced no source-time-qualified measurement in this exact window on dual-M1/TB4 Flash at ~128K, single-M1 Qwen3.8-27B in the quality lane, RTX 5070 Ti + host-RAM Qwen3.8-27B, or dual-M1/TB4 DS4-0731. Crawler freshness was ignored where the underlying source was older.

---

## Validated evidence from the earlier `09:43` candidate

The following major items were independently reproduced and remain valid. Their detailed measurements are preserved in `RESEARCH-WATCH-2026-09-17-0943.md`; this section records their status without reclassifying them.

- **vLLM #57351** — Qwen3.8-Flash-Next NVFP4 TP4 physical padding/alignment. **Correctness / packed-geometry transfer evidence.** Physical post-shard geometry is part of execution identity.
- **vLLM #57352** — removes eligible per-step GPU->CPU `seq_lens` synchronization using CPU-owned bounds; up to +16.6% output throughput in a measured MTP cell. Pipeline parallelism explicitly remains on the exact-copy path. **Experimental A/B / scheduling transfer evidence, not PP2 target evidence.**
- **vLLM #57355** — missing FULL graph capture at the maximum legal batch caused a large distributed throughput cliff; adding the max shape recovered 1523 -> 3876.85 tok/s at batch 97 in the reported topology. **Experimental A/B / graph-boundary transfer evidence.**
- **vLLM #57356** — speculative token IDs were updated without their semantic `is_token_ids` side mask; fixing the stale sidecar improved reported mean acceptance 2.79 -> 2.95. **Correctness evidence.** Token identity includes semantic sidecars, not only IDs.
- **vLLM #57358** — observability reconstructed dense cache events from sparse hybrid topology and could crash the cache path. **Correctness/observability transfer evidence.**
- **oMLX #3713** — checkpoint metadata and actual tensor structure beat model-family assumptions for quant/offload eligibility; a real V4.1 affine checkpoint exposed packed projections with dense bias. **Exact non-target receipt + loader/offload transfer evidence.**
- **oMLX #3715/#3717** — structural checkpoint eligibility is distinct from proof that the runtime expert module was actually wrapped/offloaded. **Exact non-target receipt + planning/implementation evidence.**
- **llama.cpp #29027** — Qwen3.8-27B 60K selective CPU-offload measurements show whole-layer `-ngl` can cost materially more per MiB than selected FFN/output/MTP placement, and MTP changes output-tensor cost. **Exact non-target relationship evidence.**
- **mlx-serve #449 / original `47c428b3`** — M5 Max 128GB Qwen3.8-Flash-Next SSD expert streaming. The committed receipt includes a 14.0 GB/s physical SSD ceiling, bf16 streaming measurements, a 4/8-bit streamed-vs-resident comparison, synchronization decomposition, cache-hit/fill accounting, and a quant-quality ladder against a streamed bf16 teacher. It is **exact non-target Apple/Flash mechanism + quality evidence**, not evidence for dual M1/TB4 40@128K/400.

---

## Evidence classification for target movement

### Exact active-topology receipts

**None.** No canonical target moves.

### Exact receipts on non-target topologies

Includes mlx-serve #449, oMLX #3711/#3713/#3715, llama.cpp #29027/#29028, and vLLM #57354. These can change implementation priorities or qualification tests, but not the canonical rate targets.

### Experimental A/B / transfer evidence

Includes vLLM #57352/#57355/#57356 and related runtime mechanisms. Useful for implementation hypotheses; percentages are not portable rate multipliers.

### Speculation / planning only

vLLM #57383 is explicitly unimplemented and unbenchmarked. It contributes an architecture idea only.

---

## Newly promoted qualification rules

1. **Long-session stability is a separate benchmark cell.** A model that passes short speed tests can still fail after sustained agent/coding use. Record sustained duration, committed-token progress, memory trajectory, watchdog/stream state, and whether reload succeeds after failure.
2. **Do not diagnose timeout as OOM without evidence.** Free-memory observations, runtime progress, server state, and failure logs must remain separate facts until a causal mechanism is demonstrated.
3. **Warmup/setup paths are runtime correctness surfaces.** A failure before serving traffic can invalidate an otherwise fast kernel/backend combination. Qualification includes mixed warmup shapes, not only steady-state decode.
4. **Backend identity is part of topology.** “Same GPU works” is insufficient when Vulkan and ROCm execute different graph/kernels. Record architecture + backend + placement + quant + speculative state.
5. **Planning RFCs do not move performance distributions.** No prototype/measurement means no target update, even when the architecture is plausible.
6. **Merge/rebase time never refreshes evidence.** Preserve the timestamp and identity of the original substantive source/measurement. The mlx-serve #449 original commit and llama.cpp #29014 merge-time check are concrete examples.

---

## Target status

Unchanged:

| Target | Canonical planning target | Status after rerun |
|---|---:|---|
| Flash-Next dual M1 Max 64GB/TB4 | 40 TG @ ~128K / 400 cold PP | unchanged; no exact receipt |
| Qwen3.8-27B single M1 Max 64GB | 25 TG / 110 native cold PP | unchanged; no exact receipt |
| Qwen3.8-27B RTX 5070 Ti + host RAM | 120 TG / 250 cold PP | unchanged; no exact receipt |
| DS4-0731 dual M1 Max 64GB/TB4 | 15 TG / 180 cold PP | unchanged; no exact receipt |

## Hard research freshness boundary

This independent rerun completes the previously interrupted interval.

**Hard source-freshness boundary: `2026-09-17 13:43:30 UTC`.**

Do not infer coverage beyond that timestamp from later merge, rebase, crawler, edit, or comment activity.