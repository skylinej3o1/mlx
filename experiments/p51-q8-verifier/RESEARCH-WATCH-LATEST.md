# External runtime watch — 2026-09-17 22:28 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-17 23:18:58 UTC` through `2026-09-18 02:28:04 UTC`.

PRs, issues, and default-branch commits were explicitly screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Relevant Hugging Face / oMLX community benchmark surfaces were also checked. Evidence time means substantive source/measurement time, not crawler, merge, rebase, label, or comment time.

This pass also performs a required continuity correction: the canonical target file already specified **Flash-Next Q5-class / eventual ~5.x-BPW**. The prior watch's Q6/Q8 language was stale and wrong for Flash. Q5 is now pinned in the read-first README and canonical state so future sessions cannot inherit that regression.

## Executive result

**No exact active-topology receipt appeared for any canonical target, so no numeric target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, **Q5-class / eventual ~5.x BPW**, dual M1 Max 64GB/TB4: **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max 64GB: **25 tok/s TG / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s TG / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max 64GB/TB4: **15 tok/s TG / 180 tok/s cold PP**.

Two things do materially improve the research picture:

1. **RECOVERED OLDER EVIDENCE:** a previously missed oMLX M5 Max session is on the exact intended **Q5-class Flash lane**, not Q4. It sustains **47.3 TG at 128K** and **47.4 TG at 200K** with MTP disabled.
2. **NEW:** oMLX fixed a process-lifetime performance failure mode and a separate shared-MTP cache-corruption path during this window. Those changes make long-session qualification substantially more concrete.

## RECOVERED OLDER EVIDENCE — exact Q5-class Flash long-context receipt

A 2026-09-15 oMLX community benchmark was missed in earlier passes:

- model: `Qwen3.8-Flash-Next-Uncensored-oQ5e-mtp`
- hardware: M5 Max, 40 GPU cores, 128 GB
- runtime: oMLX 0.7.0.dev2, macOS 27.0
- quant: 5-bit / oQ5e target class
- benchmark context: Code (Mixed)
- public recipe: **MTP off, DFlash off, speculative prefill off, ANE prefill off, TurboQuant KV off**

Measured session:
- 32K: **1,296 PP / 41.6 TG**, 87.0 GB listed peak
- 64K: **1,251 PP / 34.5 TG**, 88.2 GB
- 128K: **1,203 PP / 47.3 TG**, 91.4 GB
- 200K: **1,236 PP / 47.4 TG**, 97.4 GB

At 128K, detailed telemetry reports about **99.99 GB peak footprint**, **91.36 GB MLX active**, **5.03 GB MLX cache**, **97.4% average GPU utilization**, and thermal state nominal-to-heavy.

Classification: **exact same-model-family, exact target-quant-class stronger-Apple receipt; strong transfer evidence, not active dual-M1 evidence.**

### Why this is more important than the prior Q4 receipt

This directly closes the quant-identity mistake. The Project 51 Flash target is not asking a Q6/Q8 build to reach 40@128K; it is asking a **Q5-class / ~5.x-BPW** build to do it.

The recovered M5 receipt shows that the intended quant class itself can sustain **47.3 tok/s at 128K without Lightning MTP**. That removes two uncertainties at once:
- long-context Qwen4/QSA execution need not collapse below 40;
- Q5 itself need not be traded away to Q4 merely to stay above 40 on a newer Apple GPU.

Do not scale 47.3 M5 directly to M1. Dual-M1 adds older silicon, TB4, partition bubbles, per-node fit and distributed state correctness. But architecture confidence in the 40@128K thesis moves **up materially**.

The 64K 34.5 TG point is non-monotonic relative to the 128K/200K results, so do not fit a smooth context-decay curve from this session. Treat each context cell as measured and preserve runtime/thermal state.

## RECOVERED OLDER EVIDENCE — why Q5, not Q6, is the canonical capacity lane

The same public oQ5e artifact reports:
- **5.72 bpw effective**
- **128.54 GB decimal / 119.72 GiB on disk**
- routed experts primarily 5-bit; sensitivity-selected 5/6/8-bit non-expert tensors
- MTP head 6-bit; embeddings/lm_head 8-bit
- on 128 GB Apple Silicon, PLE/n-gram table is SSD-offloaded and about **84 GiB remains resident**

Its model card reports a real **250,073-token** request on M5 Max:
- **1,165 PP**
- about **30 TG**
- Lightning MTP depth 3
- **88.9% MTP acceptance**
- TurboQuant KV4
- full 262,144-token native context fits.

The sibling oQ6e build is listed at **150.5 GB on disk / ~101 GiB resident with MTP off** and does **not** preserve the full 262K context on a 128 GB machine; its stated limit is around 131K.

Classification: **recovered target-definition evidence.**

Durable conclusion: **Q5-class remains the canonical Flash quality/capacity lane.** oQ4e is the fallback/comparator. Q6 is a higher-quality comparison that loses the capacity geometry we selected Q5 to preserve.

## NEW — oMLX commit 9052b395: transient Qwen4 failure could permanently disable a fast path

Commit `9052b3952d1af3258fe85939b4fefbcc6c6c3e28`, 2026-09-18 01:46:34 UTC, fixes a Qwen4 hyper-connection failure mode linked to issue #3723.

Before the fix, a single exception in the optional fused hyper-connection path set a process-global failure flag. From that point onward, **every later Qwen4 model/call in the process stayed on the canonical fallback path**, including MTP verification. The process still worked, so this could look like mysterious uptime-related throughput decay rather than a crash.

The fix:
- removes the process-lifetime `_RUNTIME_FAILED` latch;
- falls back only for the failed call;
- leaves the optimized path eligible for later calls;
- adds a regression test that injects a transient failure and verifies both the failed model and another model recover to the optimized path.

At 2026-09-18 01:49:26 UTC, jundot confirmed reproducing the sticky slowdown with a one-time prefill error, but explicitly said it was **not yet confirmed to explain the full 3.2x 20.48 -> 66.45 tok/s uptime report**.

Classification: **new exact mechanism fix; no new post-fix full-workload A/B yet.**

### Project 51 action

Long-session qualification now needs explicit **optimization-state observability**:
- record whether fused/compiled fast paths are eligible or have fallen back;
- fault-inject one transient failure and verify subsequent calls recover;
- do not attribute a long-uptime slowdown to allocator/cache aging until sticky fail-closed state is ruled out.

This partially softens the prior “server uptime itself may decay performance” interpretation: at least one concrete, fixable sticky-state mechanism exists.

## NEW — oMLX #3724: shared MTP verify corrupted all rows at paged boundaries

PR #3724 was created 2026-09-18 00:18:52 UTC and merged at 01:05:44 UTC as `9e70587477f60ad0995a6dc8da1fb2a20c621d3c`.

Failure:
- multi-row Lightning MTP
- prefix cache enabled
- row commit lands on a **4096-token paged boundary**
- the one-token boundary materialization for one row was executed against the **whole batch cache**
- one KV key was therefore broadcast into every row's tail
- GDN state collapsed to a single row
- all rows in the batch could derail together.

There was a second identity bug: ragged `finalize()` mutated `left_padding` in place, while Qwen cached padding metadata by array identity, so later single-token steps could use stale row-padding metadata.

Validation:
- Qwen3.8-27B
- **5 sessions x 3 turns**
- prompts **12K–17K**
- before: **3–8 corrupted turns per run** across five runs
- after: **0 / 15 corrupted turns** in two runs
- a batch-size detector fired on main with the exact bad stack and stayed silent after the fix.

Classification: **new exact Qwen-family batch/state correctness receipt; strong transfer evidence for Flash distributed/batched state discipline.**

### Project 51 action

Boundary, rollback, replay and materialization operations that are semantically row-local must use **private extracted row state plus explicit merge-back** unless batch safety is proven. Array/object identity can also be part of cache metadata identity when downstream code memoizes derived state by identity.

This strengthens the existing long-session/state rule rather than changing TG expectations.

## NEW — DS4 #1072: ordinary V4.1 decode was serializing tiny Engram reads

PR #1072, created 2026-09-18 00:28:39 UTC, routes ordinary single-token V4.1 Engram reads through the existing concurrent batch reader.

M3 Ultra 80-GPU-core / 256 GB, DeepSeek-V4.1-Flash-Q2, resident, context allocation 131K, temperature 0, 200 generated tokens:
- main: **19.16 tok/s** median
- patch: **21.06 tok/s** median
- **+9.9%**, about **4.7 ms/token**
- output byte-identical.

Standalone I/O on 48 random 264-byte rows:
- serial: **5.177 ms/batch**, 107.9 us/row
- parallel: **0.614 ms/batch**, 12.8 us/row.

On a faster optimization branch the same change reportedly moved **26.8 -> 30.5 tok/s**, Engram wall time **5.55 -> 1.12 ms/token**.

Classification: **new exact non-target Apple/DS4 V4.1 receipt; strong sparse-table I/O transfer evidence.**

### Project 51 action

For SSD/mmap sparse-table paths, measure **latency per indexed row and overlap/concurrency**, not bandwidth alone. A few dozen tiny random reads can stall the entire token even when aggregate storage bandwidth is trivial.

This mechanism maps conceptually onto Flash PLE offload, but the exact percentage must not transfer from M3 Ultra/V4.1 to M1/Qwen.

## NEW — DS4 #1073: V4.1 Metal optimization branch roughly doubles plain decode

PR #1073, created 2026-09-18 00:40:19 UTC, reports a larger DeepSeek-V4.1 Metal optimization/DSpark branch. The author states a two-Mac-Studio M3 Ultra 512-GB test setup; the reported tables include local/plain and TP server lanes. This is **V4.1 on M3 Ultra**, not the canonical V4-0731 dual-M1 target.

Standard MXFP4 sweep:
- 2K: **19.2 -> 34.7 TG**, PP 329 -> 368
- 16K: **19.0 -> 33.7**
- 32K: **18.6 -> 32.9**
- 64K: **18.2 -> 31.3**

Q4 similarly moves:
- 2K: **16.9 -> 33.2**
- 64K: **16.2 -> 30.4**

Server sweep, 256 output tokens:
- 128K Q4: **15.6 -> 28.4 TG**, branch MXFP4 **29.3**
- 256K Q4: **14.8 -> 24.6**, branch MXFP4 **26.3**
- branch TP columns at 128K are about **29.5–30.0 TG** and at 256K about **26.0–26.4 TG**.

DSpark is strongly workload/context dependent. On an XNU code corpus:
- 4K plain 34.5 vs DSpark **54.1**
- 16K 33.8 vs **47.5**
- 32K 33.0 vs **39.8**
- 64K 31.7 vs **29.2**
- 128K 26.6 vs **27.3**
- 256K 23.9 vs **20.6**

On prose, DSpark becomes net-negative earlier.

Classification: **new strong Apple/DeepSeek architecture evidence; not 0731/M1 active-topology evidence.**

### Project 51 action

This sharply reinforces our existing policy: speculative decode must be **context- and workload-adaptive**, not globally enabled. Code can justify speculation at short/medium context while prose or deep context can reverse the economics.

The large plain-decode gain is also valuable mining evidence for DS4 Metal scheduling/Engram work, but it does not move the 0731 15-TG target because model generation, silicon and topology differ.

## NEW — vLLM #57456: RTX 50 / sm_120 batch-invariant matmul was badly under-tuned

Open PR #57456 was created 2026-09-18 00:22:16 UTC. vLLM had no tuned persistent-matmul table for compute capability 12.x, so RTX PRO 6000 / RTX 50-series GPUs used a generic configuration under `VLLM_BATCH_INVARIANT=1`.

RTX PRO 6000 Blackwell, TP1, Qwen3 1.7B/4B/8B:

Decode-heavy end-to-end latency under batch-invariant mode:
- 1.7B: 1.5916 -> **1.4301 s** (**-10.1%**)
- 4B: 2.9861 -> **2.3562 s** (**-21.1%**)
- 8B: 4.1242 -> **3.4510 s** (**-16.3%**)

Prefill-heavy:
- **-7.0% / -14.9% / -11.1%** respectively.

Kernel-level small-M gains are much larger for some projections, but those are not E2E multipliers. The PR also notes that selecting the M bucket from runtime M under breakable CUDA graphs can remove most of the remaining batch-invariant tax on the tested PRO 6000 path.

Classification: **new exact sm_120 hardware-family kernel evidence; experimental/open, different GPU/model/runtime from the 5070 Ti 27B lane.**

### Project 51 action

For the RTX 5070 Ti lane, treat Blackwell consumer/workstation **small-M persistent matmul configuration as a real tuning seam**, especially if determinism/batch-invariance is enabled. Do not add 10–20% to the 120-TG forecast: the receipt is RTX PRO 6000 and small Qwen3 dense models, not 5070 Ti/Qwen3.8-27B.

## NEW — vLLM #57469: host shared-memory ownership can be the binding fit constraint

Issue #57469, created 2026-09-18 01:55:49 UTC:
- DeepSeek-V4.1-Flash
- 4x H20 96 GB = 384 GB GPU
- node RAM ~587 GiB
- each TP worker shows about **143 GB shmem-rss**, ~3 GB anon RSS
- workers are MEMCG-OOM-killed during model loading, before KV allocation
- lowering CPU offload 200 -> 50 GB does not change the failure
- lazy safetensors fixes an earlier page-cache OOM but not this shared-memory wall.

Classification: **new non-target fit/allocator receipt.**

It reinforces, rather than changes, our current rule: record host shared-memory/memfd ownership and per-worker replication separately from GPU residency and aggregate “free RAM.”

## NEW / low-impact correctness delta

vLLM #57465 (created 01:01 UTC) fixes DeepSeek-V4 fused-MoE expert placement using TP size/rank where EP group size/rank should own expert distribution. No performance receipt is attached. This reinforces the existing Project 51 rule that **group identity and semantic ownership are execution-state identity**.

vLLM #57454 merged in-window but was created before the previous hard boundary, so its DeepSeek-V4.1 NaN candidate-index correctness receipt is not relabeled as new evidence merely because of merge time.

oMLX #3290 also merged in-window, but its principal M5/GLM measurements predate this window. Its final integration reinforces safe per-member CacheList persistence and warns that a supposedly memory-saving snapshot transform can silently truncate restored KV if store and restore semantics disagree. It is continuity/supporting evidence, not newly timestamped target performance.

llama.cpp's newly created issues/PRs in the strict window (including Prism ternary-format support and Edge0-style SSD expert-offload feature requests) contain no qualifying Qwen3.8-Flash/27B or DS4 target receipt. mlx-serve had no new strict-window PR/commit that changes the target distributions.

## Target / confidence decision

### Flash-Next dual M1 target

**Keep 40 TG @ ~128K / 400 cold PP. Canonical quant is Q5-class.**

Confidence moves **up qualitatively** because we now have a target-quant-class stronger-Apple receipt at 47.3 TG / 1,203 PP at 128K with MTP off. The remaining uncertainty is increasingly concentrated in:
- M1-generation GPU throughput;
- the cost/benefit of PP2 partitioning;
- TB4 stage traffic and bubbles;
- per-node fit with PLE/offload placement;
- distributed recurrent/QSA/MTP correctness.

Do not promote 45–50 until exact dual-M1/TB4 evidence exists.

### Qwen3.8-27B RTX 5070 Ti target

**Keep 120 TG / 250 PP.**

The sm_120 tuned-matmul PR is encouraging hardware-family evidence but too remote in model size/runtime/GPU class to move the target.

### DS4-0731 dual M1 target

**Keep 15 TG / 180 PP.**

V4.1 M3-Ultra work shows large current Metal headroom and highly useful mechanisms, but it is not a 0731/M1 receipt. Mine the branch; do not numerically transfer it.

## New/strengthened qualification rules

1. **Flash quant identity:** Q5-class / eventual ~5.x BPW is the headline lane; oQ4e is comparator/fallback, Q6 is higher-quality comparison with worse capacity geometry.
2. **Sticky-fast-path gate:** after a deliberately injected transient optimized-path failure, later requests must return to the optimized path; record fast-path eligibility in long-session receipts.
3. **Row-local state gate:** one-row boundary emits/rollback/replay cannot touch whole-batch cache state unless proven semantically batch-safe.
4. **Sparse-table I/O gate:** measure indexed-read latency/concurrency/overlap, not only SSD bandwidth.
5. **Speculation policy gate:** code/prose and short/deep context must be separate cells; speculation may reverse from positive to negative as context/workload changes.
6. **Blackwell small-M gate:** RTX 50 qualification should record persistent-matmul config family and graph/bucket mode when batch-invariant/deterministic kernels are active.

## Hard freshness boundary

`2026-09-18 02:28:04 UTC`
