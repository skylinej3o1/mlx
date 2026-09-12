# External runtime research delta — 2026-09-12 17:35 ET

Search window: substantive sources strictly after `2026-09-12 16:57:49 UTC` through `2026-09-12 21:35:07 UTC`.

Active lanes remain:

- Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4
- Qwen3.8-27B — one M1 Max 64 GB
- Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM
- DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4
- Blazer / custom ~5.x-BPW work where mechanisms transfer cleanly

No canonical target moves in this pass. P69 remains isolated: P69B12 stays frozen/promoted; P69B13 remains next from the existing measured GDN/projection/downstream-tail profile only.

---

## 1. vLLM #56628 — bound sparse decode-mask work by live context, not configured max context

**FRESH NEW / STRONG LONG-CONTEXT MECHANISM TRANSFER. Not Apple and not an exact active-lane receipt.**

DeepSeek-V4.1 ROCm allocated the DSA candidate-logit workspace at `(batch_size * next_n, max_model_len)` and then sanitized the whole width, even though downstream top-k consumed only each row's live `[0, end)` span. With `max_model_len=1,048,576`, the old mask launched 1,024 programs per row even when roughly 128 had useful work.

The replacement keeps a graph-capture-safe static grid but has those programs stride only to the device-resident live end. That preserves replay shape while making actual work depend on live context rather than padded workspace width.

MI355X / gfx950 / TP4 / DeepSeek-V4.1-Flash / DSpark-5 evidence:

- 131K standalone mask, concurrency 16 / 96 rows: `0.1236 -> 0.0201 ms` (**6.16x**);
- 96-row sweep: 32K `0.1249 -> 0.0125 ms` (~9.9x), 131K `0.1249 -> 0.0197` (~6.3x), 524K `0.1464 -> 0.0786` (~1.9x);
- in-situ decode, four mask calls/step, concurrency 16: `0.464 -> 0.077 ms/step` (~6.0x);
- indexer chain: `2.95 -> 2.58 ms/step` (11.4% -> 10.0% of the decode step);
- GSM8K stayed within noise.

Low-concurrency end-to-end step wall time could not resolve the kernel-sized win because TP rank-arrival skew in `cross_device_reduce` moved by >2 ms/step, so do not promote an end-to-end TG percentage.

**Promote:** for Flash-Next QSA/indexer and any long-context sparse metadata/kernel path, distinguish:

`configured maximum span -> allocated physical workspace -> live consumer-visible span -> actual kernel iteration/work span`.

A graph-captured fixed launch geometry may still use device-resident bounds internally. Static capture shape does **not** require doing work across the full padded/max-context workspace.

---

## 2. vLLM #56638 — fuse prefill top-k + SWA index preparation and remove host-synchronizing fallback

**FRESH NEW / PREFILL MECHANISM TRANSFER. Later DeepSeek/ROCm only.**

DeepSeek-V4.1 on gfx950 had fallen back from an unsafe inherited Triton path to ordinary Torch indexing for `combine_topk_swa_indices`. That fallback became the largest pure-copy source on the measured prefill path: `direct_copy + bfloat16_copy = 55.2 ms`, about 4.4% of the busiest stream's kernel time. Its `repeat_interleave` also synchronized to the host, keeping the operation out of graph capture.

The new one-program-per-row Triton path fixes three correctness hazards (row-bound mismatch, negative unclamped lengths, `compress_ratio==0`) and avoids the host-synchronizing Torch construction.

4x MI355X / TP4 / DeepSeek-V4.1-Flash A/B:

- ISL 8,192 TTFT: roughly `600/588 ms -> 526/532 ms`, about **-11.0%**;
- ISL 32,768 TTFT: roughly `1517/1513 ms -> 1394/1399 ms`, about **-7.8%**;
- 22 correctness/edge cases matched the Torch reference;
- GSM8K `0.902 -> 0.905`, explicitly inside the harness's ~1.7 pp same-build spread;
- prefill-only; decode unchanged.

**Promote:** metadata/index preparation is part of PP architecture, not bookkeeping. For Flash-Next/DS4 prefill, profile and eliminate host-syncing `repeat_interleave`/index-copy/copy chains where a fused device path can preserve exact bounds. Record whether metadata preparation is graph-capturable and whether an apparent model-kernel improvement merely moves time into host synchronization.

Do not transfer the 8-11% TTFT percentage to M1.

---

## 3. vLLM #56627 — draft metadata builders must use the draft model's own config

**FRESH NEW / SPECULATIVE CORRECTNESS + EXECUTION-IDENTITY TRANSFER.**

The speculative proposer built draft attention metadata using the **target** `vllm_config`, even when the draft model had different attention geometry. The fix creates/caches `draft_vllm_config` and uses it consistently for draft-model construction and draft metadata builders.

This is directly relevant to our Lightning-MTP/DFlash2 work because target and drafter may intentionally differ in precision, expert geometry, vocabulary/head shape, block size or backend.

**Promote speculative identity:**

`target config/geometry/precision/backend` and `draft config/geometry/precision/backend` are independent planes. Draft metadata, cache layout, attention-group construction and kernel block geometry must derive from the **draft** configuration unless an equivalence is explicitly proven.

No throughput claim; unit/regression tests only.

---

## 4. oMLX #3619 — Qwen3.8-Flash-Next cluster/text-only PLE prefill hard failure

**FRESH NEW / DIRECT FLASH-NEXT APPLE BRING-UP CORRECTNESS.**

The flat `mlx-lm` `qwen4_exp` implementation calls bare `bisect_right` for PLE n-gram shard lookup while importing only `bisect`. The vendored mlx-vlm copy imports the symbol correctly, but a cluster rank serving the flat/text-only model never traverses that VLM compatibility path. Result: every n-gram prefill reaching this code can raise `NameError`.

#3619 adds the patch on the shared flat-model load path rather than behind `for_vlm`.

**Promote for dual-M1 Flash bring-up:** certify PLE/n-gram prefill independently on every physical rank/model-loading surface:

- flat `mlx-lm` text rank;
- VLM compatibility rank/path if present;
- PP stage-local model loader;
- cold prefill and continued prefill.

Passing a VLM/local-single-process path does not prove a flat cluster rank executes the same patched implementation.

No speed target impact.

---

## 5. oMLX #3614 — fresh 64-GB single-node capacity accounting, not a performance receipt

**FRESH NEW / CAPACITY OBSERVATION ONLY.**

A user-requested `oQ3e-mtp` Flash-Next quant documents safetensors-header accounting for current single-node checkpoints:

- Jundot `oQ4e-mtp`: 106.3 GB total, ~74.3 GB non-PLE resident, ~32.0 GB PLE;
- third-party oQ3-MTP: 92.5 GB total, 63.1 GB non-PLE, 24.0 GB PLE, 1.64 GB MTP.

The author argues that a ~52 GB non-PLE target is needed to keep transformer+MTP+embeddings resident under a ~57.5 GB wired cap while serving PLE from SSD, because MoE expert offload and Lightning MTP are mutually exclusive in the current oMLX path.

This is useful single-64GB capacity bookkeeping, but it does **not** apply numerically to our PP2 two-M1 ownership plan and contains no new speed measurement. Keep it as a constraint/quant-design signal only.

---

## 6. oMLX #3610 — recovered older Flash-Next 64-GB evidence, not fresh

**RECOVERED OLDER EVIDENCE. Created before the prior hard boundary (`2026-09-12 15:33:30 UTC`); do not relabel as fresh.**

A REAP-288 Qwen3.8-Flash-Next 4-bit trunk on an M2 Ultra 64 GB is reported at ~39 GB resident with PLE on SSD. Without MTP, the issue reports:

- ~36 tok/s @ 4K;
- ~22 tok/s @ 100K.

The published full-width MTP head keeps 512 experts while the REAP trunk has 288, so oMLX currently instantiates incompatible MTP geometry and fails strict weight loading. The issue says the head author measured ~1.5-2.2x MTP gain on the same pruned trunk in another runtime; treat that multiplier as second-hand transfer, not an oMLX receipt.

This supports two durable points only:

1. long-context Flash decode degradation remains substantial even on stronger Apple hardware;
2. a speculative head may legitimately retain different expert geometry from a pruned target trunk, reinforcing the draft-vs-target config separation in #56627.

Do not use the M2 Ultra rates to move the dual-M1 target.

---

# Screened non-promotions

- `jundot/omlx` main in-window commit activity was documentation/security only; #3619 is still an open PR at cutoff.
- `antirez/ds4`: no in-window commits; no new exact 0731 dual-M1 receipt.
- `llama.cpp`: in-window commits screened were schema/Jinja/general maintenance; no new Metal/Qwen3.8/DS4 active-lane result.
- vLLM had routine CI/DSpark/watermarking work besides the items above; no exact M1/5070Ti topology receipt.
- web/HF/Reddit searches resurfaced older Apple Qwen3.8/DFlash/Flash-Next posts but no source-time post-boundary exact active-lane result.
- no new exact M1 Max64 Qwen3.8-27B receipt;
- no new exact RTX 5070 Ti 16 GB receipt;
- no new exact dual-M1 Flash-Next TG/PP receipt;
- no new exact dual-M1 DS4-0731 receipt.

---

# Consequences by active lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary, TP2 control. Add these explicit certification dimensions:

1. sparse/indexer kernel work must be accounted against **live context**, not only allocated/max context;
2. fixed graph launch geometry must record whether inner work is bounded by device-resident live spans;
3. prefill metadata/index building must be profiled for host synchronization and graph-capture eligibility;
4. target and draft configs/geometries are separate execution identities;
5. each PP/cluster rank's actual `qwen4_exp` model-loading surface must pass PLE/n-gram prefill independently;
6. a pruned target trunk may require a full-width draft/MTP head; donor compatibility cannot be inferred from target `num_experts` alone.

P69-derived verifier/kernel methods remain transfer candidates, but P69 itself is unchanged.

## Qwen3.8-27B M1 / P69

No target movement. #56627 strengthens the requirement to record target-vs-draft config/geometry in all DFlash2/Lightning-MTP experiments. No fresh 27B receipt.

## RTX 5070 Ti 16 GB

No target movement. #56628/#56638 are stronger-GPU mechanism evidence only. Continue separating allocated max workspace from live work and configured from executed route.

## DS4-0731 dual M1

No target movement. The V4.1 ROCm results reinforce long-context sparse-work bounding and device-only metadata fusion, but remain later-lineage transfer evidence.

---

# Standing additions from this pass

- `max_model_len` / maximum workspace width is **not** a valid proxy for useful per-step work; record live consumer-visible span.
- CUDA/Metal graph capture does not require full-workspace work if the launch shape is static and device-side bounds control the inner loop safely.
- Prefill/indexer metadata kernels deserve first-class profiling; host-synchronizing convenience ops can dominate TTFT.
- Speculative draft metadata/cache/backend construction must derive from draft configuration, not silently inherit target configuration.
- Cluster correctness must be certified per actual model-loading surface/rank; a compatibility path exercised on one rank does not prove another rank executes it.

**Next hard source-freshness boundary: `2026-09-12 21:35:07 UTC`.**
