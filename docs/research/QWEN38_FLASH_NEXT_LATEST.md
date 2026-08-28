# Qwen3.8-Flash-Next MXFORGE research index

Status: **LATEST POINTER**

Updated: 2026-08-28.

Read these in order when resuming Flash-Next work:

1. `QWEN38_FLASH_NEXT_CONDITIONAL_MEMORY.md` — released architecture, PLE/QSA/GDN memory hierarchy and original SSD-tier thesis.
2. `QWEN38_FLASH_NEXT_DAY1_APPLE_QUANTS.md` — release-day Apple quant/runtime field evidence.
3. `QWEN38_FLASH_NEXT_LATE_DAY1_RERUN.md` — late day-one corrections and rerun evidence.
4. `QWEN38_FLASH_NEXT_DAY2_RUNTIME_DELTA.md` — M1 Ultra/tarruda anchor, AtomicChat quant audit, oMLX 0.6.3 MTP, revised 2x-M1 forecast.
5. **`QWEN38_FLASH_NEXT_AUG28_FIELD_DELTA.md` — CURRENT HIGH-SIGNAL DELTA.** Exact direct Metal QSA, cold SSD-PLE batching, llama.cpp native MTP, PLE rollback correctness, mixed-length batching, `ngram-mod`, distributed-MTP warning, and adjacent 5070 Ti adaptive-KV evidence.

Current highest-leverage takeaways as of Aug 28:

- direct exact QSA on Apple has much more headroom than the earlier M1-generation branch alone implied;
- SSD PLE can be made dramatically cheaper in cold prefill by batching/deduplicating page requests rather than serial row faults;
- native MTP is a major coding-speed lever, but workload-adaptive policy is required;
- PLE history + short-convolution state must participate in speculative rollback, not only QSA/GDN state;
- context-derived `ngram-mod` is a separate high-value speculation lane for copy/edit/transform-heavy agent work;
- mixed-length continuous batching is a first-class agent-server correctness problem;
- **distributed Qwen Flash-Next MTP remains unqualified / fail-closed in current oMLX Cluster v2 evidence**, so single-Ultra MTP gains must not be copied into the 2x-M1 forecast;
- architecture-aware quant + Q5_1/~6-bit SSD PLE remains the preferred quality-oriented starting point until coding certification says otherwise;
- first action on return should be another ecosystem rescan before custom implementation because upstream is moving daily.

Current research branch: `mxforge-research-20260826`.

When resuming from another chat, read this index first, then the current high-signal delta before updating forecasts or selecting implementation work.
