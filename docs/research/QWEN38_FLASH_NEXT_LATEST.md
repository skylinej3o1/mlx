# Qwen3.8 MXFORGE research index

Status: **LATEST POINTER**

Updated: 2026-08-29 morning ET.

## Flash-Next resume order

Read these in order when resuming Flash-Next work:

1. `QWEN38_FLASH_NEXT_CONDITIONAL_MEMORY.md` — released architecture, PLE/QSA/GDN memory hierarchy and original SSD-tier thesis.
2. `QWEN38_FLASH_NEXT_DAY1_APPLE_QUANTS.md` — release-day Apple quant/runtime field evidence.
3. `QWEN38_FLASH_NEXT_LATE_DAY1_RERUN.md` — late day-one corrections and rerun evidence.
4. `QWEN38_FLASH_NEXT_DAY2_RUNTIME_DELTA.md` — M1 Ultra/tarruda anchor, AtomicChat quant audit, oMLX 0.6.3 MTP, revised 2x-M1 forecast.
5. `QWEN38_FLASH_NEXT_AUG28_FIELD_DELTA.md` — exact direct Metal QSA, cold SSD-PLE batching, llama.cpp native MTP, PLE rollback correctness, mixed-length batching, `ngram-mod`, distributed-MTP warning, and adjacent 5070 Ti adaptive-KV evidence.
6. **`QWEN38_FLASH_NEXT_AUG28_LATE_DELTA.md` — CURRENT FLASH-NEXT ADDENDUM.** Batched depth-1 MTP under concurrency, layer-streamed Flash-Next imatrix calibration at ~21 GB active memory, stricter SSD-PLE cold rerun, and exact no-thinking/prefix-cache API reconstruction.

## Qwen3.8-27B tuning resume

For the active Q8 verifier project, read:

1. **`QWEN38_27B_AUG28_TUNING_REFRESH.md`** — fresh ecosystem scan mapped onto the post-P69B12 project state: Layr Labs' native-MTP Apple challenge, upstream MLX GQA K/V reuse, native-MTP + `ngram-mod`, DFlash2, Cider W8A8, and the P69B13/future-work split.
2. **`QWEN38_27B_LAYR_MTP_CHALLENGE_MINING_AUG28.md`** — mechanism-level mining of the challenge frontier. Most important receipt: officially promoted producer-side QMV xsums fusion (#1197); equally important negative receipt: rejected SwiGLU -> `mlp.down` xsums extension (#1474). Includes a concrete P69B13 pre-implementation checklist.
3. **`QWEN38_27B_5070TI_MEMORY_HIERARCHY_AUG29.md`** — RTX 5070 Ti serving architecture update: jrell asymmetric IQ4/IQ3 neural quant, BeeLlama KVarN + precision tail + native MTP, adaptive host-RAM KV as the deep-context tier, and Tameru/RAG/web as semantic-memory layers. Includes the current non-drop-in integration caveat and a certification matrix.

The authoritative local experiment state remains:

- `experiments/p51-q8-verifier/STATUS.md` on branch `project51-q8-verifier`.

At the Aug-28 evening scan, GitHub `project51-q8-verifier` is at commit `5d6325f8747f8634061d1ea2e9bedf57a1010588`, P69B12 is complete/promoted, and P69B13 is next. Always re-read STATUS and re-check the branch head before resuming experiments.

## Current highest-leverage takeaways

Flash-Next:

- direct exact QSA on Apple has much more headroom than the earlier M1-generation branch alone implied;
- SSD PLE can be made dramatically cheaper in cold prefill by batching/deduplicating page requests rather than serial row faults;
- layer-streamed imatrix/sensitivity calibration makes a custom architecture-aware quant practical without full-model residency;
- native MTP is a major coding-speed lever, but workload-adaptive policy is required;
- PLE history + short-convolution state must participate in speculative rollback, not only QSA/GDN state;
- context-derived `ngram-mod` is a separate high-value speculation lane for copy/edit/transform-heavy agent work;
- mixed-length continuous batching and batched MTP are first-class agent-server problems;
- exact prompt-template/API reconstruction is part of prefix-cache correctness;
- **distributed Qwen Flash-Next MTP remains unqualified / fail-closed in current evidence**, so single-Ultra MTP gains must not be copied into the 2x-M1 forecast;
- architecture-aware quant + Q5_1/~6-bit SSD PLE remains the preferred quality-oriented starting point until coding certification says otherwise.

Qwen3.8-27B:

- keep P69B13 disciplined around the already-measured GDN/projection/downstream-tail remainder;
- mine the Layr challenge for same-geometry Apple kernel/verifier ideas, but separate official promotions from local-only/rejected probes;
- the strongest fresh structural pattern is producer-side exact auxiliary-data fusion that deletes a standalone downstream dispatch while preserving producer launch geometry;
- Layr #1197 is positive evidence for that class; rejected #1474 warns against rewriting a cheap compiler-generated producer into a barrier-heavy custom kernel just to save the next dispatch;
- P60/P61 HEADPAIR K/V reuse is independently validated by upstream MLX #4076/#4077 and should remain closed unless upstream exposes a genuinely new trick;
- after the structural P69 series, measure native MTP + `ngram-mod` on both novel-code and copy/edit agent rulers;
- treat batched native MTP as a high-value later 3-5-agent serving workstream;
- DFlash2 is worth a separate later A/B, not a reason to interrupt P69;
- Cider W8A8 is a promising non-exact prefill lane, not a candidate for the current exact Q8 verifier contract;
- on the RTX 5070 Ti, the preferred normal-agent starting point is now the jrell asymmetric quant + Bee KVarN/precision-tail + native-MTP stack, with adaptive host-KV retained as the 100-262K exception tier rather than the default daily-driver path;
- a future Bee + adaptive-residency integration is architecturally attractive because compressed KV should reduce both VRAM per resident page and host<->GPU transfer payload, but current branches are not drop-in composable and must be integrated/certified deliberately;
- Tameru-style compaction should remain policy above the runtime hierarchy: compact based on semantic redundancy, use RAG/web/repo retrieval for recoverable knowledge, and retain raw long history only when its exact form still matters.

Current research branch: `mxforge-research-20260826`.

When resuming from another chat, read this index first, then the relevant current delta before updating forecasts or selecting implementation work.
