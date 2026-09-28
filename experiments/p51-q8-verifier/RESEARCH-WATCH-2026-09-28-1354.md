# Project 51 primary-lane research watch — 2026-09-28 13:54 ET

**Freshness boundary entering this pass:** **2026-09-28 15:56:26 UTC**.  
**User cutoff:** **2026-09-28 17:54:51 UTC**.

## Decision

**No canonical 40-TG / 400-PP target change.**

Two planning definitions do change:
1. Strata TG targets are now explicitly neutral/no-penalty unless stated otherwise; 0.1.19-correct penalties cost ~1-11% when enabled.
2. A long-context agent counts as resident only if its full continuation state can remain resumable without a full re-prefill. One-shot context fit is not sufficient.

---

## NEW — Strata 0.1.19 fixes speculative penalty history, not just the earlier double-penalty bug

Release published **2026-09-28 17:13:49 UTC**.

0.1.17 fixed double application/order of penalties, but 0.1.19 found a second defect: in a speculative verify batch, only the first checked token had the request's real penalty history. Later candidates were judged against an unfilled history buffer.

Consequences before 0.1.19:
- repetition/presence/frequency penalties were mostly ineffective when ~3 tokens/step were accepted;
- large `penalty_last_n` could crash;
- benchmark/self-reference checks could miss the semantics error.

0.1.19 gives every checked token the serial-equivalent history. Strata reports **1-11% lower TG on requests with non-neutral penalties** because more draft guesses are correctly rejected. Requests without penalties keep the same answers/speed.

### P51 consequence

- Keep the existing Strata IQ3_XXS/IQ3_S TG ladders as **neutral/no-penalty rulers**.
- For production agent configurations with presence/repetition penalties, budget a temporary **1-11% decode discount** until an exact 5070-Ti 0.1.19+ ladder exists.
- Sampler certification must compare speculative vs independently derived serial semantics token-by-token, including history after each accepted draft.

---

## NEW — Strata #60 root cause: Windows commit limit, not VRAM or shared-GPU-memory limit

The 16-GB VRAM / 64-GB RAM admission failure is now explained.

On Windows, GPU allocations also consume system commit (RAM + page file). The failing box had a ~64.5-GB commit limit with ~63.7 GB RAM, implying a tiny/off page file. After loading the ~33-GB expert arena, the 9.3-GB expert cache could not be committed even though VRAM was nominally free.

0.1.19 now:
- retries with a smaller expert cache instead of stopping;
- prints remaining commit;
- warns if the page file is under 4 GB.

Recommended host fix: Windows page file **System managed**.

### P51 consequence

The prior 16GB/64GB admission risk is substantially downgraded from unknown fragmentation to a known Windows-commit dependency. Exact-card production setup should include page-file/commit validation before benchmarking.

---

## NEW — Strata `--calibrate` makes machine-specific expert/draft tuning first-class

0.1.19 adds `START-HERE.bat --calibrate`, measuring:
- PCIe share;
- speculative draft depth;
- CPU worker count.

It keeps a new setting only if it is >3% faster and stores the result per PC/model. On Strata's RTX 5070 test PC it made the Coder **7.6% faster**.

### P51 consequence

Do not hard-code a universal `pcie_frac`, draft depth or pool-worker count for the user's 5070 Ti. Promotion should include calibration on the exact host. No numeric target credit yet because the published +7.6% is Coder/RTX5070, not the user's exact IQ3 lane.

---

## NEW — Strata multi-conversation snapshot audit finds a missing indexer state field

Strata #57's first conversation-cache prototype omitted the indexer's per-sequence spare key, `idx_dead`, from both snapshot payload and fingerprint. Similar opening tokens could mask the omission.

The revised shared-core branch now preserves that state and reconstructs the spare row on rewind. Validation includes:
- Linux/RTX4090/IQ3_S;
- 30 returns across **2,026 / 39,985 / 119,987-token** contexts;
- exact baseline output/state parity;
- KV streaming;
- steering/image identity isolation;
- memory-denial fail-safe;
- host fault injection + ASan/UBSan.

At **51,133 cached tokens**, A→B→A returned with the full prefix reused and only 22 new tokens processed in **1.237 s**; a checkpoint return processed 7 new tokens in **0.566 s**.

The maintainer asked for a unified PR rebased to 0.1.19; an NVMe spill tier is planned on top of the shared snapshot format.

### P51 consequence

Add to the canonical CUDA→Apple / resident-agent state schema:
- indexer spare-key / dead-row state (`idx_dead` equivalent);
- whole-image fingerprinting;
- explicit invalid-image rejection before writes;
- fail-closed semantics for transfer failure rather than pretending rollback succeeded.

This is direct evidence that even a state image that already includes KV + recurrent + indexer state can still omit a small but correctness-critical per-sequence field.

---

## NEW — TensorFold 0.3.6.2 makes mixed/dynamic MLX quants first-class exact lane inputs

Release published **2026-09-28 16:21:04 UTC**.

For dense Qwen3.8/3.5, TensorFold now reads MLX affine **2/3/4/5/6/8-bit** weights, groups 32/64/128, including per-module mixed precision. M1-M4 use packed row decoders; M5 uses native lane kernels when the checkpoint format is supported and falls back to the packed reader otherwise.

Every draft still verifies through the lane engine; incompatible fused stacks are split rather than silently converted. The checkpoint is not expanded to dense weights.

Physical receipt on **M3 Ultra** for an oQ4-style mixed 27B checkpoint:
- code: **114-120 TG**;
- chat: **59-61 TG**;
- mlx_lm reference: **34-36 TG**.

### P51 consequence

This is strong mechanism evidence for our dynamic-quant thesis: protected 5/6/8-bit tensors plus lower-bit bulk weights can participate in exact multi-row speculative verification without requiring a uniform 4-bit artifact.

**No M1 numeric credit yet.** General mixed-bit row readers can be materially slower than specialized 4-bit routes, so P69B13 should benchmark the actual proposed hot-trunk BPW layout on Apple7 rather than assume the M3 Ultra speed transfers.

---

## NEW — TensorFold fixes M1-M4 split-prompt exactness at the 8,192-key boundary

0.3.6 had two M1-M4 cases around 8,192 keys where a prompt split into chunks did not bit-match one stock MLX attention call. 0.3.6.2 reports that split prompts now attend exactly as one-piece prompts at every tested length.

### P51 consequence

Promote 8,192-key short-tail cases into the mandatory Apple7 exactness suite. Chunk boundaries remain part of execution identity even when drafted==serial and resumed==fresh already pass.

---

## NEW — one-shot context fit and resumable-agent capacity diverge sharply

TensorFold #71 on physical **M5 Pro 64 GB**, Qwen3.8-27B 4-bit + DFlash2:
- one-shot fitted context: **140,288 tokens**;
- largest retained conversation checkpoint: roughly **96-100K tokens / 6.1-6.3 GiB**;
- at 102K the checkpoint store falls to zero;
- subsequent turns re-prefill almost everything;
- 131K and 140K continuations take roughly **574-644 s** instead of sub-second resume.

Without the drafter, a **152K** prompt retained a **9.44-GiB** checkpoint and resumed in **0.59 s**.

### P51 consequence

Project 51 must track two separate capacities:
1. maximum one-shot context;
2. **resident/resumable agent context**.

A 128K agent does not count toward the resident-agent target if its next turn must rebuild state. TARGETS now states this explicitly.

---

## NEW — cold long prefill can starve concurrent Apple decode

TensorFold #72, physical M5 Pro 64 GB / 27B + DFlash2: four independent ~16.4K prompts submitted together each need ~40 s of prefill. Because each new prefill monopolizes the MLX execution path, previously admitted streams effectively freeze:
- first stream decode: **1.0 TG**;
- second: **1.5 TG**;
- third: **2.8 TG**;
- fourth, after no later prefill: **22.4 TG**.

Shared-prefix requests with only tiny suffix prefills scale normally.

### P51 consequence

This materially strengthens the heterogeneous architecture:
- **5070 Ti / CUDA = cold long-prefill engine**;
- **dual M1 = resident long-context decode/verification engine**.

Until Apple prefill/decode scheduling can interleave at chunk boundaries, admitting a fresh 100K+ prefill onto the same Mac server can destroy latency for resident agents.

---

## UPDATE — TensorFold exact SSD conversation spill ships

0.3.6.2 ships `--spill-gib`. Release receipt on M5 Max / 48-GB budget: a 35K-token evicted conversation returned in **0.27 s instead of 75 s**, same reply.

This is a parked-state tier, not a substitute for the user's requirement that active long-context KV stay resident. It remains useful for inactive agents.

---

## WATCH — oMLX Flash-Next performance limits

- #4056 concluded the hyper-connection path is latency-bound; its attempted bit-exact kernel reorganization did not produce a promotable win.
- #4057 shows a prefill transient estimator can over-predict large-chunk memory by **10-25x** after observing tiny chunks and permanently shed ANE banks. This is an admission/control-path warning, not a P51 target mover.
- #4058 shows a 2-bit Ternary Bonsai model can have *less* usable context than a larger 3-bit model because transient/architecture memory dominates. Weight bytes alone are not a context-capacity ruler.

---

## Strict-window scan summary

From **15:56:26 -> 17:54:51 UTC**:
- **Strata:** 0.1.19 penalty-history fix, Windows commit/page-file diagnosis, `--calibrate`, multi-conversation shared-state audit; promoted.
- **TensorFold:** 0.3.6.2 mixed-bit exact lane support, M1-M4 chunk exactness fix, resident-window and concurrent-prefill findings; promoted.
- **oMLX:** HC no-win result + prefill-memory estimator risk; watch.
- **mlx-serve:** no new strict-window commit; prior Flash trunk mixed-precision result remains known.
- **Ishizuki / MTPLX / DFlash / Splash:** no strict-window primary-lane performance receipt.
- **vLLM / SGLang:** no new strict-window Flash-Next result that moves P51 targets; existing multi-component state-transfer hazards remain part of the handoff test plan.

---

## Canonical planning effect

**No speed-target changes.**

Keep:
- dual-M1 Flash-Next: **40 TG @ genuinely filled ~128K / 400 cold PP / ~70% >=40**;
- single-M1 dense27B: **25 TG / ~110 PP**;
- dense RTX5070Ti CUDA-v2 ladder unchanged;
- Strata Flash-Next TG ladders unchanged as neutral/no-penalty targets, with a new **1-11% production discount note when penalties are enabled**.

The major change is architectural confidence: current evidence increasingly supports a **fast-CUDA-prefill → state handoff → Apple resident-long-context** topology, and resident-agent capacity must be measured by retained/resumable state, not one-shot context fit.

## New hard boundary

**2026-09-28 17:54:51 UTC**
