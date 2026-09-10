# External runtime research watch — 2026-09-10 09:11 ET

## Scope and starting checkpoint

This pass continues the external-runtime watch from the prior hard source boundary:

- branch: `project51-q8-verifier`
- starting head: `f2985b65dc68f7de9ff068b11a02cfe49fc27d70`
- starting hard source-freshness boundary: **2026-09-10 10:07:43 UTC**
- canonical target blob at start: `e91ed103bd85ff1db36d1d61675d02b1b3d3fb`

Search discipline remains evidence-time-first. Repository update time is not a substitute for source freshness. This pass searched strictly after the prior source boundary and ended at **2026-09-10 13:23:11 UTC**.

No P69 experiment files are part of this watch. P69B12 remains frozen/promoted; P69B13 remains next only from the already-measured high-leverage GDN/projection/downstream-tail structure.

---

# Executive result

This is a **material mechanism / qualification update, not a target-moving pass**.

The strongest changes are:

1. **UPDATE / oMLX #3553:** the Flash-Next optimization branch now contains a completed end-to-end decomposition that separates true cycle-time savings from MTP acceptance / continuation luck and isolates a bit-exact safe core.
2. **FRESH / vLLM #56228:** DeepSeek V4.1 Flash support landed with first-class conditional n-gram / Engram memory and a substantially changed compressed-state path. This is a future architecture lane, not DS4-0731 rate evidence.
3. **FRESH / vLLM #54574:** separate and quantized MTP LM heads are now explicitly supported and measured; MTP-head precision should be an independent Blazer design variable.
4. **FRESH / llama.cpp #28696:** V4.1 conversion work proves that family-name inheritance is unsafe for quant metadata and that giant Engram tables require streamed / disk-backed conversion rather than whole-table dequantization.
5. Exact-rig searches produced **no new post-cutoff target receipt** for dual-M1 Flash, dual-M1 DS4-0731, single-M1-Max64 Qwen3.8-27B, or the RTX5070Ti16 fully-resident Q3_K_XL/native-MTP speed lane.

**No canonical TG / PP row moves.**

---

# UPDATE — oMLX #3553: separate kernel speed from speculative continuation luck

Source: https://github.com/jundot/omlx/pull/3553

PR state observed this pass:

- created: 2026-09-10 09:47:50 UTC
- materially updated: **2026-09-10 12:42:42 UTC**
- branch head reported by the PR: `a04d2408183c130d24a968ed74732260eb55d0be`
- base: `d7c63c278075e25aa916458bdefff6d3e9e4df50`

This is an **UPDATE**, not a newly discovered fresh PR: the prior 06:01 watch already incorporated the initial execution-shape findings. What changed after the previous source cutoff is the completed benchmark decomposition and explicit bit-exact-versus-tolerance accounting.

Environment remains transfer evidence only:

- M5 Max 128 GB
- `Qwen3.8-Flash-Next-oQ4e-mtp`
- SSD PLE
- 512 generated tokens
- greedy unless noted
- independent kill switches and mirrored/interleaved A/B-style runs.

## Pinned depth-3 cycle decomposition

`main -> branch`:

| Context | Backbone ms/cycle | Draft-head ms/cycle | Wall ms/cycle | Tokens/cycle | Accept | Client TG |
|---|---:|---:|---:|---:|---:|---:|
| 16K | 34.41 -> 34.46 | 3.37 -> 2.89 | 37.87 -> 37.43 **(-1.2%)** | 2.78 -> 2.68 | 74.9 -> 74.2% | 70.7 -> 68.9 |
| 65K | 34.92 -> 33.29 | 5.67 -> 3.80 | 40.70 -> 37.18 **(-8.6%)** | 2.61 -> 2.88 | 71.7 -> 78.3% | 61.7 -> 74.0 |
| 136K | 36.75 -> 35.01 | 9.57 -> 5.39 | 46.43 -> 40.50 **(-12.8%)** | 2.68 -> 3.03 | 74.2 -> 81.7% | 55.8 -> 71.9 |
| 210K | 37.55 -> 35.44 | 11.22 -> 5.41 | 48.89 -> 40.96 **(-16.2%)** | 2.43 -> 2.53 | 66.5 -> 70.0% | 48.0 -> 59.5 |

The important interpretation is the author's own separation:

- **wall-ms/cycle is the kernel/work saving**;
- the NAX indexer is only tolerance-level (~2e-5 relative) and can flip near-tie block selections;
- once the continuation changes, acceptance and tokens/cycle can move because the branch is now verifying different text;
- disabling NAX restores the base tokens/cycle on the reported control.

Therefore raw MTP TG is not a clean kernel-speed metric whenever the route can change the continuation.

## Bit-exact safe core versus all six changes

Pinned depth 3, Python code:

| Context | Main ms/cycle | Bit-exact/control-flow core | All six | Bit-exact share of cycle saving | Equal-acceptance throughput: exact core / tolerance on top |
|---|---:|---:|---:|---:|---:|
| 16K | 37.54 | 37.11 (-1.1%) | 37.11 (-1.1%) | 100% | +1.2% / +0.0% |
| 65K | 40.88 | 38.58 (-5.6%) | 36.84 (-9.9%) | 57% | +6.0% / +4.7% |
| 136K | 46.26 | 42.05 (-9.1%) | 40.76 (-11.9%) | 77% | +10.0% / +3.2% |
| 210K | 48.74 | 42.73 (-12.3%) | 40.76 (-16.4%) | 75% | +14.1% / +4.8% |

The safe core is commits 3/4/6 plus commit 5 control flow when applicable:

- fused GDN verification rows with reference-compatible precise `exp`;
- grouped verify-row quantized projections;
- narrow 2..15-row gathered QSA at long context;
- parked-head priming control flow does not engage in the pinned-depth comparison.

**Promotion for our engine:**

1. record **wall-ms / verify cycle at equal acceptance** alongside user-visible TG;
2. benchmark a strict **bit-exact lane** separately from a **tolerance-level lane**;
3. never credit acceptance/continuation changes as kernel speed;
4. for tolerance-level QSA/indexer changes, add teacher-forced NLL/logit/top-k/route drift plus task/behavior certification;
5. for recurrent/GDN changes, retain long-output greedy parity because an apparently tiny local numerical difference can propagate hundreds of tokens later;
6. preserve separate execution cells for n=1 decode, 2..8 verify rows, 2..15 narrow committed-head folds, and large-M prefill.

## Adaptive MTP and serial controls

Across the PR's 15 adaptive-MTP cells the reported raw mean improvement is +8.3% and 14/15 cells are positive, but those raw TG values are explicitly confounded whenever tolerance-level kernels fork the continuation.

A useful control is the formerly negative 65K Python-code cell: with both tolerance-level kernels disabled, the branch reproduces main's text byte-for-byte and reports **+6.5%** on that prompt.

Serial MTP-off decode is only about +1 to +3% and cold prefill roughly 1 to 3% shorter beyond the first 4K warm-up-sensitive cell. This reinforces that the large long-context MTP gains arise from exact speculative execution shape and narrow gathered state, not a universal dense-decode speedup.

**Classification:** direct exact-model Apple transfer evidence; stronger M5 hardware; **not** a dual-M1 numeric receipt.

---

# FRESH — vLLM #56228: DeepSeek V4.1 Flash is a distinct future architecture lane

Source: https://github.com/vllm-project/vllm/pull/56228

- merged: **2026-09-10 12:16:26 UTC**
- adds `DeepseekV41ForCausalLM` support.

The important point for this project is not a rate number. The implementation makes architecture changes that line up with our long-term sparse/offload thesis while also proving V4.1 must not be silently folded into the current DS4-0731 lane.

Relevant implementation properties:

- first-class conditional **Engram / n-gram memory**;
- Engram lookup can be CPU/UVA-backed rather than demanding ordinary accelerator residency;
- compressed-state machinery changes relative to the older V4 path, including new ratio-1/2 state handling rather than assuming the older compressor geometry;
- the runtime therefore needs architecture-specific state accounting rather than a family-label shortcut.

**Promotion:** create a future V4.1 / post-DS4 architecture lane only when a runnable quant/offload artifact exists. Until then:

- do not move DS4-0731 TG or PP targets;
- preserve Engram/conditional-memory offload as a durable design seam;
- inventory active compute, recurrent/compressed state, conditional-memory residency and host/interconnect traffic independently;
- keep the thesis phrased as architecture transfer, not hardware performance proof.

This strengthens the strategic direction: very large total parameter or conditional-memory footprints can coexist with much smaller active work, but actual fit and speed on 64-GB M1 nodes still require a concrete quantized artifact and measured execution path.

---

# FRESH — vLLM #54574: MTP-head precision is an independent quantization variable

Source: https://github.com/vllm-project/vllm/pull/54574

- merged: **2026-09-10 12:26:32 UTC**
- adds support for separate external MTP LM heads, including quantized heads.

The reported cross-model / accelerator validation compares an external-MTP shared-head control with a separate **W4A16** MTP LM head:

- shared/native-style control mean acceptance length: about **4.31565**;
- separate W4A16-head mean acceptance length: about **4.28227**.

That is only a small acceptance reduction in this specific test, while native/shared-head baseline behavior remains intact.

**Promotion for Blazer / custom 5.x-bit work:**

- MTP head precision is an independent search dimension; do not force it to the backbone's precision recipe;
- sensitivity-map and certify the MTP head separately;
- record draft-head config/quant identity in requested -> configured -> compiled -> armed/admitted -> executed provenance;
- evaluate head quantization on acceptance-by-depth, task completion, long-output stability, memory and TG, not weight error alone.

**Classification:** transfer/mechanism only. Different model, runtime and accelerator; no Apple numeric transfer and no target movement.

---

# FRESH — llama.cpp #28696: V4.1 quant metadata and giant Engram conversion must be explicit

Source: https://github.com/ggml-org/llama.cpp/pull/28696

- created: **2026-09-10 10:23:42 UTC**
- updated through at least **2026-09-10 12:56:28 UTC** during this pass
- draft conversion-only PR, head `cd628010bc3fc0a787d156c969d52a0789451c96`.

Important findings:

1. **FP8 block geometry differs from V4.** V4.1 uses `[32,32]` where the inherited V4 converter had hard-coded `[128,128]`. Reusing the old family value can silently rescale every dequantized weight without throwing an error.
2. The two Engram tables are each reported as **384,006,168 x 256**. Whole-table float32 dequantization would require roughly **393 GB scratch for one table**.
3. The converter therefore reads rows in blocks, quantizes per block and accumulates into a disk-backed memmap.
4. End-to-end conversion of `deepseek-ai/DeepSeek-V4.1-Flash` on a machine with **121 GiB RAM** produced 1046 tensors and a **507.9 GB Q8_0** artifact with MXFP4 experts, with peak host memory reported under 8 GB above baseline; all eight Engram tensors were present.
5. This is still **conversion only**. The converted file does not yet load in the inherited DeepSeek4 runtime because V4.1 omits runtime tensors the existing graph expects.

**Promotion:**

- architecture/family inheritance never substitutes for reading exact quantization metadata;
- block/group geometry is part of compiled/executed benchmark identity;
- a model that loads or emits fluent text is not sufficient evidence of correct dequantization;
- very large conditional-memory tables require streamed/chunked conversion and offload-first tooling;
- quantify scratch peak separately from resident inference memory;
- do not infer M1 viability from the successful low-RAM conversion: the current Q8 artifact is enormous and the runtime is incomplete.

This is particularly relevant to the eventual Blazer methodology: the quantizer must consume exact per-artifact format metadata and should be able to process giant sparse/conditional components without materializing full-precision copies.

---

# SCREENED — exact target lanes and recurring runtimes

## Exact target receipt sweep

No new post-cutoff exact receipt was found for:

- Flash-Next on **2x M1 Max 64 GB / TB4**;
- DS4-0731 on **2x M1 Max 64 GB / TB4**;
- Qwen3.8-27B on **one M1 Max 64 GB**;
- Qwen3.8-27B on **RTX 5070 Ti 16 GB**, fully resident Q3_K_XL/native-MTP speed lane.

Searches resurfaced older known M1-Max64, M1-Max32, MTPLX and RTX5070Ti receipts plus the already-incorporated 256K RTX capacity branch. These remain KNOWN / prior evidence, not fresh target evidence.

## Main branches

- `jundot/omlx`: no post-cutoff main commit; material fresh work remains in #3553.
- `Pushkinist/rMLX`: no post-cutoff main commit after the prior #554 item.
- `antirez/ds4`: no post-cutoff main commit.
- NInfer screened: latest relevant main activity was pre-cutoff.
- llama.cpp post-cutoff main commits were primarily unrelated portability/tests; no target-lane Apple/RTX rate receipt.

## Capacity/config-only sightings

A fresh mixed-GPU configuration report puts Qwen3.8-27B Q6_K_M at 180K across a 3090 + 5070 Ti split, but supplies no TG/PP measurement and is not the user's RTX-only speed lane. **SCREENED / capacity configuration only.**

Global GitHub search was also polluted by unrelated SEO/spam repositories containing model keywords; those were discarded rather than treated as evidence.

---

# Consequences by current lane

## Dual-M1 Flash-Next

Targets unchanged.

Add to the qualification/optimization protocol:

1. wall-ms / speculative verify cycle at equal acceptance;
2. strict bit-exact kernel lane versus separately certified tolerance lane;
3. continuation/acceptance changes never counted as kernel speed;
4. teacher-forced distribution/route drift for tolerance QSA/indexer kernels;
5. long-output recurrent parity after fused GDN work;
6. preserve n=1, verify 2..8, narrow 2..15 and large-M prefill as separate kernel cells;
7. retain all prior PP2 ownership, TB4 traffic, reliable Metal sync, PLE-residency, cache-boundary, graph-layout, concurrency and soak gates.

PP2/layer ownership remains primary; TP2 remains control.

## Single M1 Max64 Qwen3.8-27B

No target movement and no P69 change.

P69B12 remains frozen/promoted. P69B13 remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the canonical speed lane. Host-backed and mixed-GPU long-context configurations stay separate capacity lanes.

## DS4-0731 dual-M1

No target movement. V4.1 is a new architecture/future lane, not a replacement benchmark cell for DS4-0731.

## Future custom 5.x-bit / Blazer

Strengthen the design plan with:

- independently quantized MTP head;
- exact format/block/group metadata ingestion;
- component-specific precision policies for backbone / routed experts / conditional memory / draft head;
- streamed conversion for giant tables;
- acceptance-by-depth and task-wall-clock in the quant objective;
- bit-exact and tolerance certification lanes instead of one aggregate quality gate.

---

# Standing decisions strengthened

- **Kernel speed and speculative acceptance are separate observables.**
- Equal-acceptance cycle cost is a first-class performance metric for speculative optimization.
- Bit-exact improvements should be promoted independently of tolerance-level improvements.
- Tiny recurrent/indexer numerical differences can fork long continuations even when local error is small.
- MTP-head precision is not required to equal backbone precision.
- Exact quant block/group metadata is part of model identity; family defaults can be silently wrong.
- Huge Engram/conditional-memory components should be streamed/offloaded rather than expanded whole.
- DeepSeek V4.1 Flash is a future architecture lane; it does not alter the current DS4-0731 target row.
- Cross-runtime/cross-hardware evidence remains transfer evidence until exact target topology reproduces it.
- **No canonical target movement.**
- **P69 remains isolated.**

---

# Next hard source-freshness boundary

**2026-09-10 13:23:11 UTC**

The next search must search strictly after this timestamp. A later repository commit timestamp must not replace this source boundary.
