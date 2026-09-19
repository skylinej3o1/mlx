# External runtime watch — 2026-09-19 03:51 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-18 21:34:45 UTC` through `2026-09-19 07:51:54 UTC`.

PRs, issues, comments/reviews, and default-branch commits were screened across DS4, vLLM, oMLX, mlx-serve, and llama.cpp. Fresh Qwen3.8-Flash-Next Hugging Face/community/web surfaces were also searched. Evidence time means the substantive source/measurement time, not crawler, merge, label, bot or rebase timestamps.

## Executive result

**No exact dual-M1-Max/TB4 Q5/custom-quant receipt appeared. Canonical physical targets and current planning confidence remain unchanged.**

Flash-Next:
- target topology: **2x M1 Max 64 GB / TB4**
- headline target: **40 TG sustained at ~128K**
- cold PP target: **400 PP**
- current planning confidence: **~60% for 40 TG**, **~70% for 400 PP**.

The major durable change is quant identity:
- **oQ5e = quality/certification comparator**
- **oQ4e = aggressive performance comparator**
- **deployment design = custom mixed quant around ~4.6-4.9 hot-trunk BPW**
- **PLE/ngram BPW and MTP BPW are reported separately**.

Whole-file BPW is no longer acceptable as the primary Flash quant label because the giant PLE table can consume many bits while sitting on an SSD/offload path rather than the hot decode-weight path.

## QUANT STRATEGY UPDATE — hot-trunk BPW, not whole-file BPW

AtomicChat's published “4.27 bpw” build is the clearest example of why the old shorthand is misleading.

Its giant ~51.2B-parameter PLE/ngram table is stored at roughly 6-bit-class precision. Using 177B total parameters, a simple arithmetic back-out:

`(4.27*177 - 6*51.2) / (177 - 51.2) ~= 3.57 bpw`

for the non-PLE remainder.

That is an **engineering estimate**, not a model-card-reported hot-trunk figure, and file-format overhead is ignored. But it is enough to show that “4.27 overall” is not comparable to a true ~4.6-4.9 compute-trunk design.

Project 51 quant receipts must now report:
1. hot compute-trunk BPW
2. PLE/ngram BPW and placement
3. MTP BPW
4. protected high-precision tensor groups
5. resident vs streamed/offloaded byte footprint.

## NEW — nitinpanj Flash-Next V3: role-aware quant allocation buys large quality for small speed cost

Newly published fork/checkpoint during this window:
- model: Qwen3.8-Flash-Next
- checkpoint size: **95.5 GiB**
- intended machine: 64-GB Apple Silicon
- base quant: bartowski Q4_0
- `output.weight`: Q8_0
- five resident groups spliced from UD-IQ4_XS:
  - attention
  - hyperconnection
  - token embeddings
  - SSM output
  - shared experts.

Paired 40-chunk comparison versus the unspliced checkpoint:
- perplexity: **5.2777 -> 4.3148 (-17.8%)**
- wins: **40/40 chunks**
- MTP draft acceptance: **0.751 -> 0.817**
- decode-speed cost: **-2.7%**
- disk cost: **+1.69 GiB**.

The author also reports that keeping only attention/hyperconnection/token-embedding protection gives the same perplexity score but makes decode **14% slower**; adding SSM-output/shared-expert tensors restores about 11 points of decode despite not moving that perplexity test.

Classification: **strong fresh quant-allocation evidence; M5-Pro/streamed topology, not target hardware.**

Project 51 implication:
precision assignment must jointly consider **quality sensitivity + runtime traffic/residency**. A tensor can be worth higher precision because it enables a faster kernel/resident path even if the sampled perplexity metric barely moves.

## NEW — 64-GB Apple streaming Flash receipt with MTP

Same V3 fork, M5 Pro 64 GB:
- target-only decode: **18.0-18.6 TG**
- MTP decode: **~27.6 TG**
- 4K prompt processing: **~367 PP**
- real chat at ~29K: **~20.6 TG**
- MTP depth 3 reported optimal; depth 4 slower
- 36-GiB expert cache, internal SSD streaming.

The fork warns that over-growing expert cache can collapse performance: on its 64-GB machine, 38 GiB cache drove generation from roughly 24 TG to ~3.7 TG as macOS began swapping.

Classification: **fresh stronger-chip/different-topology transfer evidence.**

This does not change the M1 target. It does reinforce:
- MTP can provide a large effective-generation gain when acceptance is healthy;
- memory pressure is sharply non-monotonic;
- streamed-expert cache size must be tuned under real swap telemetry.

## NEW — PLE direct-read prefill evidence

The same publication attributes major prompt-processing gains to replacing mmap/page-fault PLE gathers with direct file reads for the ~26.8-GiB per-layer embedding table. Public measurements report approximately:
- 512-token PP: **181 -> 401**
- 8K PP: **274 -> 451**.

Classification: **community/fork A/B; useful but not Project-51-controlled.**

This is consistent with prior PLE findings. PLE precision/storage policy and PLE I/O policy must be optimized independently from hot-trunk quantization.

## NEW — oMLX #3755: dev4 loses deep-context Flash decode while prefill improves

Exact Apple/same-model-family report:
- M3 Ultra 96 GB
- Qwen3.8-Flash-Next-oQ4e-mtp
- MTP OFF
- SSD n-gram offload ON
- matched serving settings.

Decode medians, older tested build -> dev4:
- 4K cold: roughly neutral
- 16K cold: **49.2 -> 45.6 TG (-7.4%)**
- 64K cold: ~46.7 -> ~46.0
- ~128K cold: **41.3 -> 37.6 (-9.0%)**
- ~128K warm: **~41.0 -> 36.5 (-10.9%)**.

Prefill is **~3-7% faster** on dev4 and peak MLX residency is flat around 68 GB.

Classification: **new exact Apple / same-model-family runtime-regression evidence; stronger chip and oQ4e, not target topology.**

Action:
- exact oMLX/MLX dependency SHA stays benchmark identity;
- runtime promotion needs deep-context TG and PP separately;
- a release can improve PP while regressing the metric we care about most.

No target-confidence move: this is a software regression, not hardware evidence.

## NEW — llama.cpp #29110: Apple small-row MTP verify kernels can remove large overhead

M3 Ultra Metal, Q4_0/Q8_0, verify-row width 2..8.

Op-level small-row matvec speedups are commonly **~1.3-1.9x**.

Qwen3.8-27B Q8_0 at 131K, MTP:
- depth 1: essentially control
- depth 2: **32.5 -> 44.5 TG (+37%)**
- acceptance: **0.836**
- output: byte-identical.

At a real 89,575-token code prompt, depth 2:
- **17.06 -> 20.28 TG (+19%)**
- acceptance unchanged at **0.678**
- prefill unchanged.

Classification: **new exact Apple MTP/verify evidence; different Qwen model and M3 Ultra.**

Project 51 implication:
small-row verification is not necessarily an irreducible cost. A substantial part of MTP economics can live in memory-traffic/dispatch inefficiency, which strengthens the technical plausibility of the multi-row PP2 thesis without changing the numerical target.

## NEW — recurrent rollback must track state provenance

llama.cpp #29117 identifies stale recurrent/hybrid restores after a multi-token snapshot is followed by one or more single-token decode steps.

Proposed mechanism:
- record the last snapshot epoch/end/plane count;
- restore by exact index shift;
- refuse rollback when the requested prior state no longer exists, forcing re-prefill.

External matrix:
- fixed path: **9/9 exact**
- vanilla: only **3/9 exact at m=0**, plus stale restores/refusals.

PR was closed administratively due contributor PR-count rules, not because the mechanism was disproven.

Classification: **new recurrent-state correctness evidence.**

Project 51 action:
speculative rejection/edit-turn rollback must carry state provenance and must fail closed to re-prefill when exact state is unavailable.

## NEW — distributed hybrid-state transfer identity needs geometry

vLLM #57661, DeepSeek-V4.1-Flash P/D disaggregation:
- silent garbled/empty output
- root cause: transfer-region aliases shared a base address but had different block lengths
- example: 32,768-byte compressor state vs 19,008-byte SWA view
- deduplication by base address truncated/misaligned transferred state
- deduplication by **(base_addr, block_len)** fixes the cluster reproduction.

After fix:
- 0% garble over reported 200-token generations
- clean output across 6 concurrent streams.

Classification: **new non-Apple distributed hybrid-state correctness evidence.**

Project 51 rule:
distributed state identity includes base/offset/stride/block length/owner; shared backing storage alone is not semantic identity.

## NEW — dynamic speculative width must feed admission

vLLM #57658 fixes Hybrid Mamba scheduling that chose a smaller step-local speculative K but still reserved memory using maximum K.

Qwen3.5-4B DFlash:
- concurrency 16: **414.8 -> 752.6 tok/s**
- concurrency 32: **392.2 -> 950.2 tok/s**.

The gain is from admitting more requests, not a faster model kernel.

Classification: **new scheduler transfer evidence; not Flash B1 evidence.**

Project 51 B2-B4 rule:
admission must use the **actual step-local verify width**, while retaining a safe hard-cap guard. Static max-K reservation can destroy aggregate utilization.

## TRANSFER — DS4 #1090 shows large Apple hybrid-MoE fusion headroom on other models

Archived M3 Ultra campaigns:
- GLM-5.3-Flash Q4 decode: **+28.5-29.6%**
- DeepSeek-V4.1-Flash Q4: about **+36-37% decode**
- techniques include HC/KDA/projection fusion, tiled sparse attention, router/shared-expert fusion and avoiding unused expert-tile work.

Classification: **historical/different-model Apple transfer evidence.**

Do not add these percentages to Kadir or the Project 51 forecast. They only show that mature-looking Apple hybrid-MoE paths can still hide substantial model-specific execution losses.

## Quant/community search

Fresh search did **not** surface an exact dual-M1-Max/TB4 custom-Q5 receipt.

Useful current quant observations:
- PipeNetwork's existing MLX ablation remains important: uniform 4-bit is +20.6% perplexity vs BF16, while 4-bit routed experts + 8-bit non-expert sensitive weights is only +1.3% for ~2.4 GB more.
- Current community discussion explicitly distinguishes non-PLE BPW from whole-model BPW; this reinforces the new Project 51 accounting rule but is not used as target evidence.
- A current M1 Max 64-GB REAP 4-bit artifact is reported to load with native MTP and ~40.3 GB short-test peak, but no qualified long-context throughput receipt is published.

## Target / confidence decision

**No numeric target or confidence change.**

Current Flash-Next dual-M1 plan:
- **40 TG @ ~128K: ~60%**
- **400 cold PP: ~70%**.

Quant strategy changes, not physical forecast:
- custom deployment design: **~4.6-4.9 hot-trunk BPW**
- oQ5e: quality/certification reference
- oQ4e: speed comparator
- PLE and MTP precision reported separately.

A future custom-quant performance stretch above 40/400 is not promoted until a physical target-topology receipt exists.

## New/strengthened qualification rules

1. **Quant identity is component-wise:** hot trunk / PLE / MTP / protected tensor groups.
2. **Quality + traffic co-design:** high precision may be justified by runtime placement/kernel economics even when perplexity is flat.
3. **Deep-context runtime promotion gate:** version upgrades need matched TG and PP at ~128K.
4. **MTP verify-row profiling:** benchmark small-row matvec/verify separately from target decode.
5. **Exact recurrent rollback provenance:** refuse unavailable state rather than restoring stale snapshots.
6. **Distributed geometry identity:** base pointer alone never defines state-transfer equivalence.
7. **Effective dynamic K in admission:** reserve what this step will actually verify, subject to hard safety bounds.
8. Existing effective-setting, chunk-parity, state-isolation, PLE-staging, memory-staircase and autotune-stability gates remain.

## Hard freshness boundary

`2026-09-19 07:51:54 UTC`
