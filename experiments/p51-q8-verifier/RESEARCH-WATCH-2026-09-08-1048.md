# External runtime research watch — 2026-09-08 10:48 ET

Starting branch checkpoint: `fa13bcae0ba0d285dd8611543a7993fb6ff641f2`

Starting hard freshness cutoff: **2026-09-08 12:53:53 UTC**.

This pass searched the recurring Qwen3.8 / Flash-Next / DS4 lanes, Apple runtime/kernel work, speculative decoding correctness, hybrid/recurrent checkpointing, and exact-rig/community receipts. Findings are classified against the hard cutoff above; evidence that predates the cutoff but was newly recovered is explicitly BACKFILL rather than FRESH.

---

# Executive result

No performance target moves.

Fresh material is concentrated in two landed llama.cpp fixes:

1. a real Apple Metal `IQ3_XXS` small-width utilization fix with both kernel and coding-agent wall evidence;
2. a recurrent/hybrid context-checkpoint eviction fix with large warm-rewind prompt-processing savings on M1 Pro/M5 and a measured coding-agent replay wall win.

A fresh vLLM DFlash2 issue update also materially **weakens** an earlier attribution: clean upstream runs did not execute the community split-KV kernel used by the failing system, and a CMP-unlocker driver memory-map confound is now plausible. Treat that issue as unresolved environment/path provenance, not as an upstream DFlash2 root-cause receipt.

A same-day M1 Max 32 GB Qwen3.8-27B benchmark was recovered after the cutoff. It is useful direct single-M1 baseline evidence but predates this pass's freshness boundary and therefore is BACKFILL.

Canonical targets remain:

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

---

# FRESH / landed Apple Metal small-width utilization

## llama.cpp #28086 / merge `88ada91c18cd026388be742838d9f27fc12673bc`

Merged **2026-09-08 12:54:42 UTC**, 49 seconds after the previous research cutoff.

### Mechanism

For `IQ3_XXS` matrix-vector work with `ne00 < 1024`, the existing Metal mapping could leave part of a SIMD group idle. The measured case is `ne00 = 512`, so there are only 16 32-element chunks (`nb32 = 16`) for 32 threads. Half of the threads therefore did no useful chunk work.

The merged path:

- detects `nb32 < 32` when `nb32` divides 32;
- assigns multiple threads to a chunk;
- partitions output rows between those threads;
- uses a separate split pipeline specialization;
- raises the split path's row capacity to 8 while retaining the old path elsewhere.

The same idle-thread assignment pattern is called out in `iq2_xxs`, `iq2_xs`, `iq3_s`, `iq2_s`, `iq1_s`, and `iq1_m`, but those were **not** changed without a measured model hitting the same small-width regime.

### Measured evidence

Rig / model:

- 14-inch MacBook Pro M5, 24 GB;
- Tiel-Coder-35B-A3B MTP, `UD-IQ3_XXS`;
- fixed multi-turn coding-agent replay;
- ~5.6K-token system prompt;
- warm prefix cache;
- MTP + ngram speculative decoding;
- 13 generations;
- mean of 3 warm repetitions.

End-to-end report:

- wall: **24.66 -> 22.59 s/rep** (**-8.4%**);
- decode: **65.6 -> 73.9 tok/s**;
- perplexity unchanged at **3.3969**.

Kernel table at `ne00 = 512` reports roughly **-28.8% to -36.7%** latency versus master across verify heights `n=2..24`.

The author also used rotating expert IDs between timed batches because the stock backend-op benchmark otherwise repeatedly hits the same selected experts and can overstate a hot-weight path.

### Evidence class

**FRESH / measured Apple mechanism + production-style wall A/B.**

It is M5, Tiel-Coder and IQ3 rather than M1 Flash-Next Q4/Q2. The percentages do not transfer numerically to our target lanes.

### Promotion into our plan

- Add **small inner-width SIMD utilization** to the stage-local routed-MoE/projection profiling checklist.
- A quant kernel is not disqualified merely because the arithmetic count is fixed; prove active-lane utilization at the exact `ne00`, verify height and expert geometry.
- When benchmarking routed experts, rotate or otherwise vary expert IDs so hot-weight reuse does not define the cell accidentally.
- Preserve the narrow promotion rule: only port row/chunk splitting to another quant path when the exact target profile proves the same idle-lane shape.
- Pair kernel microbench with coding-agent wall/TG and equivalence, as #28086 did.
- Do not infer a Flash Q4/Q2 gain from IQ3_XXS.

For the user's Tiel-Coder interest this is useful Apple-side evidence, but it does not modify the RTX 5070 Ti lane.

---

# FRESH / recurrent checkpoint retention and warm rewind economics

## llama.cpp #28302 / merge `5d806aa2575e01e126651fd69ab1ab6cefff861d`

Merged **2026-09-08 13:01:03 UTC**.

### Root cause

`create_checkpoint()` applied `checkpoint_min_step` spacing eviction before the checkpoint list was full. The default spacing is 8192 tokens.

On prompts shorter than that spacing, the oldest checkpoint could dominate and later checkpoints were repeatedly deleted, including the useful near-frontier checkpoint created around `n_tokens - 4`.

That is particularly harmful for hybrid/recurrent models because recurrent state cannot be reconstructed by simply trimming a KV cache. A later edit, branch, retry, compaction or reopen-at-an-earlier-point then has to re-prefill substantially more history.

The landed repair:

- applies spacing eviction only when the checkpoint list is at its capacity boundary;
- replaces an existing checkpoint at the same token position instead of appending a duplicate.

### Measured Qwen-family evidence

Stock Qwen3.5-9B Q4_K_M, M5, six short turns after a ~390-token system prompt:

- edit turn 4 after turn 6: **702 -> 26 processed tokens**;
- prompt wall: **1459 -> 229 ms**;
- total 9 warm requests: **1753 -> 1077 processed prompt tokens**, **4647 -> 3407 ms**;
- greedy output unchanged.

Same scenario on M1 Pro 32 GB with master -> PR -> master ordering control:

- edit rewind: **704 tok / 3355 ms -> 26 tok / 264 ms**;
- second master reproduced **704 tok / 3323 ms**;
- `erasing context checkpoint too close` log lines: **23 -> 0 -> 23**.

### Measured coding-agent / recurrent MoE evidence

Tiel-Coder-35B-A3B-MTP `UD-IQ3_XXS` on M5, fixed 3-session coding-agent replay:

- opener reprocessing per session dropped from **260/254/272** to **40/34/52** tokens;
- total warm reprocessed tokens per repetition: **2436 -> 1776**;
- warm wall: **18.25 -> 17.12 s** (**-6.2%**);
- edit-turn replay: **715 -> 26** reprocessed tokens.

### Memory tradeoff

Keeping the recent useful checkpoints can increase retained checkpoint memory. The PR reports:

- ~74 MiB/checkpoint on Tiel;
- ~50 MiB/checkpoint on Qwen3.5-9B;
- highest observed agent replay: 8 live checkpoints / ~596 MiB;
- default hard count limit remains 32.

A byte budget is explicitly left as possible follow-up.

### Qwen3.8 relevance

An independent PR comment predating this pass reports Qwen3.8-27B under Ollama repeatedly reprocessing full sub-8K conversational prompts with the same checkpoint-invalidated symptom. That comment is supporting transfer evidence, not a fresh controlled Qwen3.8 A/B.

### Evidence class

**FRESH / landed, measured Apple recurrent-state lifecycle evidence.**

This is warm rewind/session economics, not cold PP throughput.

### Promotion into our plan

- Recurrent checkpoint **retention policy is part of cache correctness/economics**, not just memory housekeeping.
- Add branch/edit/retry/compaction/reopen-at-earlier-frontier cells to recurrent session qualification.
- Record both `prompt_n` and prompt wall time on warm rewinds; a session-cache "hit" is not sufficient if the useful recurrent frontier was evicted.
- Prefer a recent mathematically useful recurrent checkpoint over a purely age/spacing-driven survivor.
- Capacity must be explicit in both count and observed bytes; do not trade correctness/rewind work for unbounded checkpoint growth.
- Duplicate frontier positions must supersede rather than accumulate.
- PP2 prompt/session reuse must prove each rank retains or reconstructs the **same recurrent frontier identity**, not merely the same token prefix.
- This does **not** move the 110 tok/s cold-PP target for M1 Max 27B or the 400 tok/s Flash cold-PP target.

---

# UPDATE / attribution correction for cumulative DFlash2 OOB report

## vLLM #55279

The issue remains useful as a stress-test pattern, but the fresh update materially changes attribution.

### What the fresh qualification found

Current-upstream A100 runs reached **21,296** and **22,084** speculative verification steps without a CUDA error. Older near-merge upstream runs also passed **7,284** and **7,103** steps.

However, those are only **negative controls**: the failing deployment used a community `spec-decode-attn.patch` split-KV Triton path that is **not** the upstream path exercised by those clean runs.

The investigator also identified a plausible environment confound for the reporter's CMP 170HX 64 GB setup: older `cmpunlocker` driver behavior could register a WPR2/GSP reserved framebuffer region into PMA and itself produce Xid 31 faults. The driver-side fix exists separately and must be ruled in/out before assigning the fault to vLLM.

No vLLM root cause or code fix is claimed yet.

### Evidence class

**UPDATE / attribution correction.**

The previous "fixed cumulative verify-step OOB" symptom remains real for the reporter's configured system, but it is not currently a clean upstream-DFlash2 receipt.

### Promotion

- A crash/corruption cell is defined by the **actual engaged kernel/source tree**, not the product/version label.
- Hash community patches and the exact installed files that implement speculative verify.
- Record device ID, driver build/source and relevant reserved-memory mapping when low-level GPU faults are involved.
- Upstream-clean does not clear a patched path; patched-path failure does not indict upstream.
- Keep long-running cumulative-step stress tests after semantic qualification because lifecycle bugs can require thousands of rounds to surface.
- Do not promote #55279 into our Apple/5070 correctness model until the failing producer is isolated.

This strengthens the standing rule: benchmark and failure provenance must describe what **actually executed**.

---

# BACKFILL / recovered same-day M1 Max Qwen3.8-27B baseline

## r/oMLX — M1 Max 32 GB, 24-core GPU

The post was already several hours old when this pass began, so it predates the **12:53:53 UTC** cutoff and is BACKFILL despite being posted today.

Reported setup:

- M1 Max Mac Studio;
- 24-core GPU;
- 32 GB unified memory;
- Qwen3.8-27B;
- 512 prompt tokens / 700 generated tokens;
- 3 runs.

MLX arm:

- `mlx-community/Qwen3.8-27B-4bit`;
- ~16.1 GB model footprint;
- prompt **81.76 tok/s**;
- generation **15.81 tok/s**;
- peak memory **16.39 GB**.

llama.cpp arm:

- Unsloth `UD-Q4_K_M`;
- full Metal offload;
- Flash Attention on;
- prompt **99.61 ± 0.44 tok/s**;
- generation **9.69 ± 0.34 tok/s**.

Comments include an anecdotal claim of roughly **18-25 tok/s around 50K context** with a tuned MTPLX route on another M1 Max 32 GB machine. Treat that as anecdote only: no full controlled cell, denominator or exact runtime state is supplied.

### Evidence class

**BACKFILL / direct single-M1 chip-family baseline.**

It is not the exact M1 Max 64 GB target configuration, GPU-core bin is explicit at 24 cores, and the benchmark is a small 3-run user test rather than our mature-runtime ruler.

### Consequence

- It strengthens the direct single-M1 non-MTP baseline range: ordinary 4-bit MLX can reach mid-teens TG on this chip family.
- It is consistent with, rather than stronger than, the existing mature 25 tok/s planning target once MTP/runtime optimization is included.
- No target or confidence movement.

---

# SCREENED / no material change

- **oMLX:** no main commit after the cutoff.
- **antirez/ds4:** no main commit after the cutoff.
- **rMLX:** post-cutoff `#547` is CI/debt-report process work; no runtime performance/correctness promotion.
- **vllm-mlx:** no post-cutoff commit.
- **Avarok Atlas:** no post-cutoff commit.
- **llama.cpp:** later post-cutoff commits screened here are unrelated build/HIP/MSVC work; no new Flash/Qwen exact-rig receipt.
- Broad same-day exact-rig searches found no fresh sustained **2x M1 Max64/TB4 Flash TG/cold-PP** receipt.
- No fresh sustained **2x M1 Max64/TB4 DS4-0731 TG** receipt.
- No fresh exact **M1 Max64 Qwen3.8-27B** mature-runtime receipt after the cutoff.
- No fresh exact **RTX 5070 Ti 16 GB Qwen3.8-27B** receipt after the cutoff; currently surfaced benchmark pages are older observations already outside this pass.
- No fresh exact RTX 5070 Ti Tiel-Coder Q4/Q5 partial-offload receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary, TP2 control**.

The ordering is now:

1. exact PP2 model/recurrent/QSA identity + landed distributed lifecycle;
2. cold-PP harness with real stage balance, chunking and TB4 traffic/bubbles;
3. mixed-phase first-decode/continuing-prefill correctness;
4. speculative owner/epoch/range + rollback/replay + one authoritative committed frontier;
5. bound verifier capture to the mathematical drafter horizon;
6. certify recurrent checkpoint retention across branch/edit/retry/compaction/reopen and measure warm `prompt_n` + wall;
7. default/native MTP depth whole-round baseline;
8. workload-separated deeper-depth A/Bs with long-generation segmented acceptance/TG;
9. profile stage-local GDN/routed-MoE/projection/sync at realistic chunks, including active SIMD-lane utilization at actual matrix widths;
10. per-quant/per-kernel chunk-width sweep before promotion;
11. block-history/repeated-work first; double buffering and small-width row/chunk splitting only where exact M1 profiling proves the matching bottleneck;
12. combine passing mechanisms, then cluster cold PP + append/live-prefix + branch/retry + real agent wall.

New explicit harness fields from this pass:

- recurrent checkpoint position / frontier identity;
- live checkpoint count and bytes;
- reprocessed prompt tokens on rewind;
- small-width kernel active-lane geometry;
- expert-ID variation policy for routed kernel A/Bs;
- exact source/kernel hashes for non-stock speculative paths.

## Single M1 Max64 Qwen3.8-27B

No target movement. The recovered 24-core/32GB user benchmark is useful baseline calibration only.

P69 remains isolated:

- **P69B12 frozen/promoted**;
- **P69B13 next from existing profiling only**;
- do not reopen P69B8, P69B9 or P69B10-C.

External checkpoint/kernel evidence can inform later runtime work but does not rewrite the frozen verifier stack.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

No target movement and no fresh exact-card receipt.

The main incremental consequence is provenance: community speculative patches, actual target/drafter kernels, driver state and GPU memory-map/runtime must be pinned before a stability result is used. The M5 Tiel IQ3 result is Apple kernel transfer evidence only.

## Dual-M1 DS4-0731

No target movement and no fresh exact sustained current-head generated-token denominator.

The checkpoint-retention lesson transfers to any recurrent session/reuse path, but it is not DS4-0731 throughput evidence.

---

# Standing decisions strengthened this pass

- Warm recurrent reuse is certified by the exact retained/restored frontier, not a generic cache-hit flag.
- Branch/edit/retry/compaction/reopen are first-class recurrent-cache cells.
- Reprocessed prompt tokens and warm prompt wall are mandatory session-reuse metrics.
- Recurrent checkpoint retention needs explicit count **and byte** accounting.
- Duplicate checkpoint frontiers should supersede rather than accumulate.
- Small matrix width can make SIMD occupancy a larger lever than arithmetic-count changes.
- Routed-kernel A/Bs vary expert IDs when fixed IDs would create unrealistic hot-weight reuse.
- Kernel gains still require production-style wall/TG and equivalence before promotion.
- Cross-quant small-width fixes transfer only after exact shape/profile confirmation.
- Community-patched speculative paths are separate execution identities from upstream.
- Exact installed source/kernel hashes and driver/runtime state are failure provenance.
- Clean upstream negative controls do not clear a community patch; patched-path failures do not prove an upstream bug.
- Long cumulative-round stress remains necessary after short correctness tests.
- Acceptance length remains diagnostic; useful emitted tokens per wall-second remains the speculative objective.
- First-decode-during-continuing-prefill remains an explicit concurrency cell.
- Capture horizon, target/drafter backends, scheduler requirements, owner/epoch/range and device happens-before remain mandatory provenance.
- QSA selected-set/order determinism and actual `top_k` remain mandatory.
- A benchmark cell is defined by what the engine actually executed, not what was requested.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
