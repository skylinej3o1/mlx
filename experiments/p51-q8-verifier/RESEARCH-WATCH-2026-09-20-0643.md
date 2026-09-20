# Project 51 external runtime watch — 2026-09-20 06:43 ET

**Hard freshness window:** strictly after **2026-09-20 08:31:59 UTC** through the user message cutoff **2026-09-20 10:43:46 UTC**.

## Decision

**No numeric TG/PP target or confidence change.** The headline remains **40 TG @ ~128K active context / 400 cold PP** on 2x M1 Max 64 GB / TB4.

This window did not produce a new exact dual-M1 Flash-Next receipt. It did produce several durable scheduler/cache/kernel lessons that strengthen qualification of the recently added wake/prewarm and low-row/MTP plans.

## NEW MERGE — vLLM #57477: a prefix cache can be hot, hit, and silently corrupted

Source: https://github.com/vllm-project/vllm/pull/57477  
Merged **2026-09-20 10:15:04 UTC**.

GLM-5.3-Flash's NVIDIA kpool tail-seed kernel assumed a dense tail-block stride even though the tail is a padded strided view sharing the indexer allocation.

Consequences:

- every prefill left its own tail block unseeded;
- the misplaced 2,048-byte write landed in another indexer block;
- low block IDs belonging to a long-lived cached system prompt were preferentially damaged as the allocator cycled;
- prefix-cache metrics continued to report hits while sparse top-k state became progressively wrong;
- MLA KV itself remained intact, making the failure look like a semantic/cache-quality problem rather than an obvious crash.

End-to-end stress:

- cached 14.5K system prompt, 420 vault/code records;
- after 50 filler requests: **16/38 cached pages modified / 18.4 KB**;
- after 400 fillers: **30/38 / 64.1 KB**, lookups often wrong/no code;
- final hot cached prompt: **1/7 correct** on main;
- fixed branch: **0 pages modified / 7/7 correct**;
- request-level run: fresh prompt 7/7, cache hit before fillers 7/7, then **0/7 after every 100-600 filler pass**;
- the same prompt with a fresh `cache_salt`: **7/7**, and its subsequent cache hit: **7/7**.

The fix uses the actual tail view strides and adds cross-platform regression coverage.

### Project 51 consequence

This is directly relevant to the new **`sup` wake/prewarm protocol**. A prefix cache hit is **not proof of semantic state integrity**.

Wake/prewarm qualification must include:

1. repeated wake/restore under allocator churn;
2. sentinel/hash or semantic probe of certified recurrent/QSA/indexer state;
3. long-lived stable prefix + hundreds of unrelated sessions;
4. fresh-namespace/cache-salt control;
5. per-stage stride/layout identity after PP2 restore;
6. cached-prefix behavioral probes, not merely cache-hit counters.

Never allow a prewarmed system/tools/skills prefix to become a long-lived corruption amplifier.

## NEW MERGE — vLLM #57534: fuse tiny per-step metadata work, but do not overclaim E2E gains

Source: https://github.com/vllm-project/vllm/pull/57534  
Merged **2026-09-20 10:20:55 UTC**.

GLM-5.3-Flash kpool tail metadata previously used a chain of 12 tiny torch kernels every decode step; with MTP k=1 the builder runs twice per step.

The replacement uses one Triton kernel.

Micro results on GB300:

- decode bs=1 / 2 tokens: CPU enqueue **157 -> 38 us**, GPU **18.2 -> 1.5 us**, launches **12 -> 1**;
- bs=256 / 512 tokens: CPU **254 -> 33 us**, GPU **22.1 -> 2.0 us**;
- prefill 1x8192: CPU **251 -> 33 us**, GPU **22.9 -> 12.2 us**.

Reported removed CPU work is roughly **0.44 ms/step with MTP** because the builder runs twice.

E2E 8K-in/1K-out:

- c=1 output throughput mean improved about **+5.1%**, but only two runs/build and near the noise boundary;
- c=16 **+2.4%** inside larger run-to-run noise;
- c=64 **-1.4%**;
- c=256 **+0.4%**;
- median TPOT deltas were within noise overall.

### Project 51 consequence

This reinforces the existing rule from #57434: **launch/enqueue reductions are valuable but do not become TG until E2E proves them.**

For M1/Metal, explicitly profile tiny per-token host work in:

- QSA top-k metadata;
- MTP draft selection;
- rollback bookkeeping;
- PP2 stage handoff metadata;
- prefix-state lookup/restore.

Fuse/cache them only when their lifetime/identity is correct.

## NEW MERGE — vLLM #57421: sequential layers should share compatible persistent scratch

Source: https://github.com/vllm-project/vllm/pull/57421  
Merged **2026-09-20 09:28:34 UTC**.

Humming grouped MoE kept persistent permutation scratch separately in every layer. A shared `WorkspaceManager` now reuses compatible scratch across sequential layers while isolating concurrent execution slots/streams.

Qwen3.6-35B-A3B-NVFP4, B300, 40 MoE layers:

- max batched tokens 2048: live PyTorch allocation **33.412 -> 30.953 GiB**, saving **2.459 GiB**;
- 8192: **41.352 -> 31.516 GiB**, saving **9.836 GiB**;
- scratch objects: **40 -> 1**;
- scratch storage at 8192: **10,330.684 -> 258.267 MiB**, **97.5% less**.

No latency improvement was established.

### Project 51 consequence

Audit M1 Flash scratch/workspaces by **lifetime**, not layer ownership. Sequential PP-stage layers may share compatible:

- expert permutation/dequant scratch;
- QSA gather/top-k temporary storage;
- verify/prework scratch;
- prefill staging buffers.

But each concurrently active lane/ubatch/speculative slot still needs isolation. Memory saved here becomes useful headroom for Q8 KV, larger context, wider verify, or safer Metal residency; do not count it as TG by itself.

## NEW MERGE — vLLM #54894: lower-precision output projection can be a real PP/PP-topology lever

Source: https://github.com/vllm-project/vllm/pull/54894  
Merged **2026-09-20 09:13:56 UTC**.

On ROCm DeepSeek-V4, the native FP8 `wo_a` output projection replaces a BF16 grouped einsum.

0813 checkpoint, 8x MI355X:

- TP1/PP8, 100K prefill: median TTFT **2459.0 -> 2278.4 ms (-7.35%)**, input throughput **40,667 -> 43,891 tok/s (+7.93%)**;
- TP1/PP8 8K prefill concurrency: roughly **+3.7% to +6.7%**;
- TP8/PP1: mostly **+0.8% to +1.9%**.

Older checkpoint remeasurement:

- TP1/PP8 mean prefill gain **+6.09%**;
- TP8/PP1 mean **+1.29%**;
- decode TP8/PP1 output throughput **+1.9% to +3.2%**;
- full GSM8K matched **1250/1319** in both arms.

### Project 51 consequence

Different hardware/format, so percentages do not transfer. The topology pattern is useful: **a precision/kernel change can pay much more under pipeline partitioning than tensor parallelism**. Our APEX/MTPLX sensitivity optimizer should therefore record both quality and **PP2-stage-local kernel timing**, not infer dual-M1 benefit from a single-node B1 microbench.

## NEW MERGE — Splash #12: score-only decisions can reuse prefix state without decode

Source: https://github.com/incoai/splash/pull/12  
Merged **2026-09-20 10:29:07 UTC**.

Splash added score-only requests that:

- accept 2-255 vocabulary-validated option token IDs;
- run the target head on the final prefill chunk;
- read only requested logits;
- emit **zero output tokens**;
- preserve scheduler, chunked prefill, memory admission, prefix reuse and cancellation;
- publish no cache state if the score result is non-finite.

Real-model validation included:

- score logits agreeing with greedy next token;
- score-only work advancing **zero decode counters**;
- scored-prefix cache reuse of **9,632 / 9,661 tokens**;
- concurrent scoring + chat;
- cancellation recovery;
- 255-choice request at **6,485 input / 0 output tokens**.

The PR explicitly says this is API compatibility, **not Jev numerical/model parity**.

### Project 51 consequence

This is a strong architecture match for the user's separate Jev/failure-classifier work:

- binary/multi-choice agent routing;
- "which tool/skill?" decisions;
- failure classification;
- guardrail decisions;
- "continue / compact / retrieve / ask user" routing.

When the decision space can be encoded as stable answer tokens, **do not autoregress JSON just to make a classification**. Score the choices directly against the already-warm prefix. This also composes naturally with `sup` prewarm: wake the prefix once, then make cheap score-only routing decisions before expensive generation.

Do not assume Splash's decision quality equals Jev; Project 51 would need its own calibration/behavioral gate.

## UPDATE / caution — vLLM #57756 exactness repair after an apparently successful fusion campaign

Source: https://github.com/vllm-project/vllm/pull/57756  
Updated **2026-09-20 10:40:19 UTC**; still draft.

Earlier measurements showed ~3.5% C1 TPOT improvement from fused sparse-decode metadata + final HC/RMSNorm, but the PR now records an exactness correction: the direct top-k path must retain the parallel length kernel to preserve sparse-attention split boundaries and reduction order.

After correction, direct mode is shape-gated:

- rows 5-32: exact direct path;
- <=4: fully fused ragged builder;
- >32: parallel ragged path.

Corrected local path saves only **~2.6-3.3 us** for rows 5-32; rows 4 and 64 are deliberately not admitted because the direct path regresses.

The prior serving/GSM8K tables were collected before this exactness fix and are explicitly being rerun.

### Project 51 consequence

This reinforces two existing rules:

1. **shape-dependent fast-path admission** beats one universal "optimized" path;
2. preserve split/reduction semantics where tiny numerical changes can alter sparse selection/MTP acceptance.

Do not promote the earlier 3.5% service number after the exactness patch until rerun.

## UPDATE — vLLM #57451 demonstrates why compiled dynamic state must not be frozen at trace time

Source: https://github.com/vllm-project/vllm/pull/57451  
Updated **2026-09-20 10:42:13 UTC**; draft, no V4 E2E eval yet.

The proposed DeepSeek-V4 inverse-RoPE fusion has to track which rows still require rotation. Reading that dynamic value from inside a compiled path using unsafe skipped guards can freeze its trace-time value.

The parent V4.1 experience reportedly caused an **0.087 GSM8K loss against a 0.902 baseline** while output remained fluent and no runtime error occurred.

### Project 51 consequence

For compiled M1/Metal paths, never capture request-dependent values such as:

- actual decode/verify row count;
- speculative width;
- active QSA rows;
- rollback/transaction state;
- cache/prefix ownership;

as compile-time constants unless they are truly invariant. A fluent output smoke is insufficient.

## Screened / no target-changing evidence

- **DS4:** no post-boundary default-branch commit. Updated PRs do not add a new exact M1/TB4 receipt.
- **oMLX:** no new default-branch commit; no new Flash-specific post-boundary measurement superseding #3770/#3771.
- **mlx-serve:** no post-boundary default-branch commit.
- **llama.cpp:** no post-boundary default-branch commit relevant to Project 51.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no activity.
- **MTPLX:** no post-boundary commit.
- **APEX:** no post-boundary commit.
- No new exact **2x M1 Max 64 GB / TB4 / ~128K / custom mixed quant + MTP** physical throughput receipt.

## Target impact

**No change.**

The window materially strengthens cache-integrity, workspace-lifetime, shape-gated fast-path and score-only routing design, but it does not change the physical throughput distribution for the target hardware.

**New hard boundary: 2026-09-20 10:43:46 UTC.**
