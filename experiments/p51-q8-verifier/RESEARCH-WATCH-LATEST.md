# Project 51 primary-lane research watch — 2026-09-26 11:28 ET

**Freshness boundary checked:** prior hard boundary **2026-09-26 13:10:08 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-26 15:28:27 UTC**, plus an explicit mining pass over the user-supplied r/oMLX long-running-agent thread. Reddit comment timestamps are only relative/hour-level, so those are classified as SAME-DAY CURRENT rather than forced into the strict timestamp window.

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

The strict window adds three exact-Flash-family optimizations that attack QSA bookkeeping, dense verify attention and host-read serialization. The supplied Reddit thread adds something orthogonal and valuable: a credible 14-compaction overnight survival receipt and a counterexample where the runtime survived compaction but the agent semantically regressed.

## Findings

### NEW — mlx-serve #556 collapses QSA index-key upkeep from ~10 dependent kernels/layer to one

Source: https://github.com/ddalcu/mlx-serve/pull/556  
Merged **2026-09-26 14:02:18 UTC**.

Flash-Next's 12 QSA layers re-pooled each finished index-key block through approximately:
`astype -> mean -> astype -> rms_norm -> ropeApplyCosSin` (~10 dependent kernels/layer).

The new fused kernel reproduces the chain's rounding points exactly because the resulting pooled keys feed top-k block selection. It deliberately declines block ratios >8, where MLX's mean reduction order changes, and M-RoPE image turns.

M5 Ultra / Flash-Next mixed-4/8bit / S=4 / kv=16K:
- forward **20.63 -> 20.25 ms**
- GPU range **18.99-19.20 -> 18.59-18.70 ms**
- output bit-identical in the covered path.

A review caught a particularly important implementation trap: the changing block count `NB` was initially a Metal template argument, which would JIT a new pipeline for block counts 1,2,...512 during real sessions. The final version moves block count to a scalar runtime input so decode, verify and prefill share one compiled pipeline.

**P51 consequence:** QSA index maintenance is part of the verifier budget, not background bookkeeping. Fusions that affect selection state require selection-bit-identity, and per-call dimensions must not become shader-template identities.

### NEW — mlx-serve #554 keeps Flash S=4 dense causal verify inside the vector SDPA envelope

Source: https://github.com/ddalcu/mlx-serve/pull/554  
Merged **2026-09-26 13:57:15 UTC**.

Flash-Next has Hq/Hkv = 24/2, **GQA=12**. At S=4, one causal SDPA call gives `4*12=48`, exceeding MLX's vector-SDPA wall (`qL*gqa <= 32`) and falling to an unfused ~8-dispatch path. Splitting into two 2-row groups yields 24 each and stays on the vector kernel.

M5 Ultra at kv=1500, QSA off:
- GPU forward **17.13 -> 16.71 ms** (~0.42 ms)
- all measured split runs beat all base runs.

The final path is intentionally restricted to the measured **hd=256** envelope and yields to NAX where the fused NAX path is preferred.

**P51 consequence:** verifier attention policy key should include **head_dim × GQA × S × KV regime × available fused kernel**. A generic S=4 policy is not sufficient.

### NEW — mlx-serve #545 overlaps next-draft construction with the outstanding host verdict

Source: https://github.com/ddalcu/mlx-serve/pull/545  
Merged **2026-09-26 13:50:19 UTC**.

Before: verify dispatch -> host read -> commit -> build next chain.  
After: verify dispatch -> build the next chain from lazy GPU mismatch/argmax/hidden arrays -> host read -> keep or discard.

On M5 Ultra / Flash-Next mixed-4/8bit / greedy MTP:
- predraft tail **~1.26 -> ~0.53 ms**
- fixed-prompt greedy decode roughly **184.6-188.1 -> 192.1-192.6 TG**, about **+2.6%**.

The speculative chain is discarded and the MTP head truncated if the host verdict changes the path (budget/EOS/done/spec-off/lookup choice); sampled, grouped and planner-owned paths remain eager.

**P51 consequence:** the desired verifier-cost reduction is not only GEMM/kernel work. Once GPU work is short enough, host-verdict serialization becomes visible. Prebuild reversible next-round state while the host read is outstanding.

## User-supplied Reddit thread: what is actually worth mining

Thread: https://www.reddit.com/r/oMLX/comments/1wqkqeu/qwen38_flash_next_with_omlx_pi_for_longrunning/

### SAME-DAY CURRENT — strongest positive receipt: 14 compactions + overnight autonomous work

`corruptbytes` reports:
- Flash-Next **oQ4e**, direct reply confirms the OP's proposed **Jundot oQ4e-mtp** setup;
- current/latest oMLX;
- **262K context**;
- **n-gram SSD offload**;
- Pi default compaction settings;
- `pi-goal-x + pi-blackhole`, plus `pi-autoresearch`/`pi-loop` experimentation;
- personal record of **14 compactions**;
- repeated non-stop overnight runs with no reported runtime issue.

The same commenter says roughly **70 TG**, but the parent asks both speed and whether the machine is an M5 Max and the reply only says 'like 70'; hardware is therefore **not confirmed** and the speed is not attached to an M5 in P51.

**Why this matters:** this is not a short-chat benchmark. It is the first surfaced anecdotal end-to-end receipt that Flash-Next + oMLX + external durable-goal/memory tooling can continue through many compaction cycles and unattended hours.

### SAME-DAY CURRENT — negative receipt: process survival can hide semantic failure

Another commenter reports:
- `Jundot/Qwen3.8-Flash-Next-oQ4e`
- **oMLX 0.7.0-dev4**
- **MTP on**
- experimenting at **262K** single-slot;
- default Pi compaction; manual compaction around **100K**;
- the previous 2-slot planner/developer configuration repeatedly OOMed;
- at 100K it survived **3-4 compactions**, but eventually **reverted earlier commits**, deciding prior implementation was bad.

**P51/harness consequence:** define two separate certification dimensions:
1. **Runtime continuity** — server stays alive, cache/state restores, no OOM/crash/loop.
2. **Semantic continuity** — after N compactions, agent still knows the accepted goal, current task, repository HEAD/diff, completed/rejected approaches and does not undo correct prior work.

A multi-compaction test should checkpoint repo state and ask the agent to restate/verify goal, work note, accepted decisions and current diff after every compaction before allowing destructive actions.

### Why pi-blackhole + pi-goal-x are structurally interesting

`pi-blackhole` replaces free-form LLM compaction with a deterministic structural summary and observational memory that survives compactions; `pi-goal-x` persists the objective/tasks/progress on disk across context churn. This is exactly the kind of **out-of-context durable sidecar state** we should prefer for long-horizon agents rather than repeatedly compressing all load-bearing state back into prose.

### Other thread signals

- M4 Max user: oQ5e + oMLX 0.7.0-rc1, roughly **150K** practical context.
- M5 Ultra 256-GB user: original FP8 weights work for long agentic runs; their main complaint is overthinking rather than runtime instability.
- M5 Max 128-GB user: oMLX Flash 'barely' around **40 TG** while MTPLX often exceeds 60, but oMLX saves roughly **20-30 GB RAM** from SSD offload. Anecdotal but directionally consistent with the known throughput-vs-residency trade.

## LOWER PRIORITY strict-window activity

- mlx-serve also landed a large Nemotron-H hybrid/recurrent optimization chain. It independently reinforces dtype-narrowing, no-per-layer-host-sync, single-token recurrent fusion and MTP-state rollback rules, but it is not exact Flash and does not move P51 targets.
- oMLX fixed an M5 packed-projection A8-prefill regression; M5-specific and no new P51 Apple7 receipt.
- vLLM/llama.cpp/SGLang strict-window changes were CI/frontend/load-time or unrelated to the primary Apple Flash lane.
- no qualifying new DS4, MTPLX-core, APEX/GSQ, IST-DASLab, Model-Optimizer or M1-Splash performance result appeared inside the strict interval.

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

`RESEARCH-STATE.md` is updated with the exact-family QSA/SDPA/lazy-predraft rules and the long-agent runtime-vs-semantic continuity certification split. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-26 15:28:27 UTC**
