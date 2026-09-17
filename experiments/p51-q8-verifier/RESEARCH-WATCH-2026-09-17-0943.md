# External runtime watch — 2026-09-17 09:43 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-17 10:33:10 UTC` through the user-request cutoff `2026-09-17 13:43:30 UTC`.

Evidence time is the substantive source / measurement timestamp, not crawler time, merge time, a later PR edit, or a rebase. A separate addendum backfills four high-value vLLM items discovered during this pass that were actually created before the prior boundary; those do **not** move this watch's freshness boundary.

## Executive result

No exact active-topology receipt appeared for any canonical target. **No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max64: **25 tok/s TG / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s TG / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max64/TB4: **15 tok/s TG / 180 tok/s cold PP**.

The window is nonetheless unusually useful for implementation:

1. **vLLM #57352** removes a per-step GPU→CPU `seq_lens` synchronization from eligible FlashInfer attention planning by carrying provable CPU bounds instead. On MTP workloads the measured effect reaches **+16.6% output tok/s** at C32. Pipeline parallelism is explicitly still on the exact-copy path, so this is a warning and a design target for our PP2 scheduler rather than a direct speed transfer.
2. **mlx-serve #449 / `47c428b3`** is a substantial Apple Qwen3.8-Flash-Next expert-streaming implementation. It serves the original 335GB bf16 checkpoint on an M5 Max 128GB by keeping the trunk resident and streaming routed experts from SSD, with detailed I/O, cache-hit, synchronization and quality receipts. It also provides a useful quant-quality ladder against a streamed bf16 teacher.
3. **vLLM #57355** shows a graph-capture-table hole at the maximum legal batch can cause a distributed throughput cliff rather than a small boundary penalty: batch 97–100 fell to PIECEWISE execution when FULL capture stopped at 96, and the measured max-load cell recovered from **1523 to 3876.85 tok/s** after adding the missing full-graph shape.
4. **vLLM #57356** catches a speculative correctness bug where draft token IDs were updated but the semantic `is_token_ids` side mask was not. Verification then consumed stale prompt embeddings. Correctness identity therefore includes semantic sidecars attached to a token row, not merely the token-ID buffer.
5. **llama.cpp #29027** gives a direct Qwen3.8-27B 60K-context measurement of marginal CPU-offload cost per MiB. Whole-layer `-ngl` is materially more expensive than selectively offloading FFN/output/MTP tensors, and MTP changes the cost of offloading the output tensor because it is reused for each draft.
6. **oMLX #3713/#3715/#3717** strengthen the physical-artifact rules for expert offload: checkpoint quant metadata and structural tensor layout are stronger evidence than a family-name allowlist, but structural eligibility still does not prove that the runtime expert module was actually wrapped and offloaded.
7. **vLLM #57351** is the first current-window item, created only 23 seconds after the prior cutoff. Qwen3.8-Flash-Next NVFP4 TP sharding can leave gate/up rows physically unaligned even though the logical model dimension is valid. Physical padded geometry belongs in execution identity.
8. **vLLM #57358** shows that even observability/reporting code must respect sparse physical cache topology: reconstructing a dense event sequence from a sparse hybrid hit table can crash an otherwise correct cache path.

Fresh external/community screening did not provide a new source-time-qualified measurement on the exact active dual-M1/TB4 quality-quant topology. Nothing external qualifies to move the target distribution.

---

## Promoted scheduling evidence — vLLM #57352: eliminate host synchronization only when CPU bounds prove the planner contract

Source PR created: `2026-09-17 10:35:47 UTC`.

FlashInfer's metadata builder was copying `seq_lens` from GPU to CPU on every build. That tiny-looking read is a full dependency edge: it waits for queued GPU work, then prevents the host from preparing the next step until the device has produced the lengths.

The proposed path carries CPU-side lower/upper bounds for the sequence length. A backend that only needs a safe planning extent can use the upper bound and skip the device read entirely. Backends or modes that require the exact length retain the copy.

Measured output-throughput deltas on RTX 6000 Ada, FP8 KV:
- Qwen3.5-0.8B, MTP3: **+3.0% C1 / +5.0% C8 / +16.6% C32**;
- Qwen3.5-9B, MTP3: **+4.7% / +3.0% / +0.8%**;
- Qwen3-8B, no speculation: **+1.4% / +1.1% / +0.8%**.

RTX 4090 reproduced the same qualitative pattern: the 0.8B MTP3 path gained **+4.7% / +5.6% / +16.1%**, while the non-spec 8B path stayed around one percent.

The implementation logged 102,800 debug builds without a lower/upper-bound violation.

### Important non-transfer

The exact-copy path is still retained for context parallelism, cascade attention, sinks, adaptive verification, **and pipeline parallelism**. Therefore the numbers are not evidence that our PP2 route gets the same gain by deleting a read.

### Promoted rules

- Treat every small device→host scalar/vector read as a possible **global scheduling barrier**, not as negligible metadata traffic.
- If the host already owns an authoritative bound/state, prefer proving the planner contract from that state rather than reading back device state.
- For PP2, maintain explicit ownership of exact sequence/frontier state. If both ranks already know the committed frontier, do not create an avoidable TB4/device-host round trip merely to rediscover it.
- A bound-based route is valid only for consumers whose semantics require a bound. Any consumer requiring an exact value stays on the exact state path.

---

## Promoted Apple Flash-Next evidence — mlx-serve #449 / `47c428b3`: SSD expert streaming is a whole-forward synchronization problem

Implementation commit author time: `2026-09-17 13:31:25 UTC`; committer time `13:38:29 UTC`, both before cutoff. The PR itself was edited after the cutoff, so this watch relies on the qualifying implementation commit and the measurement material contained in that commit.

The implementation serves the original bf16 `Qwen/Qwen3.8-Flash-Next` checkpoint, roughly **335 GB**, on an **M5 Max 128GB** by keeping the trunk resident and streaming routed experts from SSD.

The physical design is useful to our memory/streaming work:
- byte-span expert store over fused HF or split MLX expert banks;
- per-layer group-exact LRU where all route hits are protected before new admissions;
- prefill union workspace for misses;
- F_NOCACHE positioned reads, file-descriptor identity validation and 64MiB coalescing;
- page-aligned slabs with epoch leases;
- zero-copy `mlx_array_new_data_managed_payload` import validated by pointer identity;
- one MLX barrier per MoE layer;
- resident-budget ledger against the wired-memory limit;
- quantized streamed packs execute the resident fused quant kernels against the imported slab;
- speculative MTP is deliberately refused on the streamed route.

### Physical I/O receipt

On the measured M5 Max the storage path reached a **14.0 GB/s physical ceiling**; four workers saturated it. Direct pread helped about 13% only at one worker, and a 64MiB sequential run was no faster than a 9.8MB random span in the reported test.

At `--ssd-budget-gb 60` on bf16:
- short-prompt decode: **6.4 tok/s cold / 8.6 warm**;
- 4K prefill: **160 tok/s**;
- 4K decode: **5.1 tok/s**;
- ten-prompt warm-loop median: **6.5 tok/s**;
- decode expert-cache hit rate: **92%**;
- fills: about **0.374 GB per decode row**;
- reported host sync: **47 ms per forward**;
- RSS: **64.4 GiB**;
- observed SSD rates: ~7.3 GB/s during prefill and ~5.9 GB/s during decode.

A warm decode forward was decomposed to roughly **150 ms = 68 ms route/compute + 78 ms fill + 2 ms build**. A fully hit forward was about 47 ms. The replay model put the I/O-only ceiling at 16.3 tok/s for that cache budget.

The more revealing result is the quantized 4/8-bit pack. At an SSD budget of 50GB it ran a warm loop at **24 tok/s versus 66 resident**, and 4K prefill at **507 versus 2110 tok/s**. The measured warm forward was route 49ms + fill 30ms: the per-layer synchronization/barrier route cost was larger than the actual fills.

### Quality ladder against the streamed bf16 teacher

The commit records teacher-forced quality across 7,186 scored positions. Selected rows:
- experts 8-bit g64 + original bf16 n-gram: **KLD 0.0353, top-1 0.943**;
- experts 6-bit g128 / dense 8-bit: **0.0443 / 0.936**;
- experts 5-bit g64 + bf16 n-gram: **0.0445 / 0.937**;
- experts 5-bit g64 / dense8: **0.0501 / 0.932**;
- 4/8-bit + bf16 n-gram: **0.0749 / 0.920**;
- 4/8-bit ordinary pack: **0.0814 / 0.913**;
- 4/8-bit with KV8: **0.0818 / 0.914**;
- experts 3-bit g128 / dense8: **0.1628 / 0.877**;
- iQ 3.3bpw: **0.1990 / 0.865**.

This supports a useful separation: the expert quant width and the n-gram/PLE table precision contribute separately to quality. KV8 in this particular comparison had effectively no measurable quality cost.

The quantized streamed pack also reproduced the resident pack's greedy bytes/top-20 logprobs at equal prefill chunk width, providing a strong execution-identity bar for the streaming transform itself.

### Important lifecycle finding

An MLX array created from an imported host slab can release its payload **after** `mlx_array_free` returns. The slab therefore cannot be unmapped/reused merely because the array handle is freed; the payload deleter / lease completion is part of the physical ownership state machine.

### Promoted rules

- Expert streaming viability is `route + fill + synchronization + compute`, not SSD bandwidth alone.
- Every streaming benchmark receipt must include at least cache hit rate and fill bytes per committed row. Cross-run SSD bandwidth is otherwise confounded by residency and hit behavior.
- A speculative path can increase expert bytes per committed token and multiply state ownership. **Do not bolt MTP onto streaming** until whole-cycle expert traffic and rollback/commit state are priced.
- Imported host-buffer lifetime ends on the runtime's ownership-release event, not necessarily at host-handle free.
- When a faster kernel changes reduction order, use an appropriate numerical/quality bar rather than demanding byte identity where the reference itself changes rounding.

### Target status

This is valuable Apple/Flash mechanism and quality evidence, but it is **M5 Max, one SoC, SSD-streamed, MTP-disabled**, not our dual-M1/TB4 quality-quant 128K topology. It does not move 40/400.

---

## Promoted distributed runtime evidence — vLLM #57355: graph ladders must include the actual maximum live shape

Source PR created: `2026-09-17 11:10:57 UTC`.

A Mistral-Small-4-119B TP4 deployment used FULL CUDA graphs only through batch 96 even though `max_num_seqs=100`. Requests 97–100 therefore fell onto PIECEWISE execution at the exact maximum-load region.

At batch 97 the reported throughput moved from **1523 tok/s to 3876.85 tok/s (+154.6%)** after adding an explicit FULL capture at 100. Total test duration fell **129.72s -> 52.41s**.

Nsight showed the failure was not merely four rows of launch overhead. The PIECEWISE path accumulated rank skew: graph gaps grew from ~0.69ms toward 5.5ms and all-reduce waits from tens of microseconds to multiple milliseconds.

### Promoted rules

- Capture tables are part of the executed topology. Qualify **exact maximum live batch**, not merely powers-of-two or a nearby ladder rung.
- Test capture thresholds at `threshold-1 / threshold / threshold+1`, plus the actual configured maximum.
- In distributed execution a local graph miss can amplify into cross-rank arrival skew and collective waiting. Measure both local gap and rank-aligned collective timeline.
- The planned graph mode is not evidence of execution; record which shape actually captured/executed.

---

## Promoted speculative correctness — vLLM #57356: token identity includes semantic side masks

Source PR created: `2026-09-17 11:16:22 UTC`.

When prompt embeddings were enabled together with speculative decoding, draft token IDs were scattered into the input-ID buffer, but the corresponding `is_token_ids` positions were not updated. Target verification therefore interpreted those rows as external prompt embeddings and reused stale embedding values.

The final result can still look plausible because the target path continues executing, while acceptance quietly degrades. A Qwen3-8B DFlash test reported mean acceptance improving **2.79 -> 2.95** after the fix.

### Promoted rule

For every speculative row, execution identity is the tuple of:

`token/value payload + semantic kind mask + position + ownership/state metadata`.

Any scatter/copy/reorder of the token row must update all semantic sidecars atomically. A buffer-level equality test that ignores the kind mask is insufficient.

---

## Promoted packed-geometry correctness — vLLM #57351

Source PR created: `2026-09-17 10:33:33 UTC`, only 23 seconds after the previous boundary.

For Qwen3.8-Flash-Next NVFP4, TP=4 leaves the logical intermediate dimension 640 sharded into geometry that is not aligned for FlashInfer/CUTLASS `swizzle_blockscale`. The route needs an additional pad of 64 for the affected gate/up projections.

The fix pads each projection before swizzle using the backend's 64/128 rule and records the physical padded intermediate size. Five targeted tests pass.

### Promoted rule

Quant execution identity includes **physical packed/padded dimensions after TP partitioning**. A valid logical model dimension and a recognized quantization mode do not prove that a backend's block-scale layout is valid.

---

## Promoted offload evidence — oMLX #3713/#3715/#3717 and llama.cpp #29027

### oMLX #3713 — checkpoint-declared affine quantization is the source of truth

Created `2026-09-17 12:12:47 UTC`.

Third-party MLX DeepSeek V4.1 affine checkpoints declare quantization through checkpoint metadata and can mix packed and dense projections. The old source loader assumed official/oMLX layouts and failed before model construction.

A real M5 Max 128GB check on a 222.4GiB 2-bit affine V4.1 checkpoint, with 12.5% expert residency and MTP off, reported 27.61GiB resident / 23.75GiB Metal active, 2.20 tok/s cold and 4.43–5.18 warm.

More important than that non-target speed: the real checkpoint exposed **66 packed projections with a dense bias**. A generic packed projection had nowhere to preserve that bias, so those projections required a forced-dense path.

Rules: stored tensor metadata beats family assumptions; offload accounting bills scale/bias side metadata; and packed eligibility must include all arithmetic attached to the projection.

### oMLX #3715/#3717 — structural layout eligibility versus executed module coverage

#3715, created `13:01:54 UTC`, reuses the same SwitchGLU offload adapter for Qwen3.6 MoE. On M5 Max 128GB a 24.2GiB Q5 model at 25% expert residency loaded at 8.62GiB resident / 9.55GiB Metal and warmed from 4.57 to **24.89 tok/s** on a repeated request.

#3717, created `13:18:00 UTC`, proposes admitting offload by complete checkpoint structural validation instead of a hardcoded model-family list.

The caveat in #3717 is exactly the useful rule for us: a checkpoint can have a compatible expert tensor layout while the runtime uses a custom expert module that the generic adapter never wraps. Therefore maintain separate states for:

`artifact structurally compatible -> runtime module recognized -> adapter attached -> offloaded route armed -> offloaded route executed`.

### llama.cpp #29027 — offload by marginal penalty per byte, not whole layer

Created `2026-09-17 12:46:52 UTC`.

On Qwen3.8-27B UD3-Q4_K_M at 60K context, the PR measures generation-time penalty per MiB moved to CPU:
- K-quant FFN tensors: ~**12 us/token/MiB**;
- smallest IQ3/Q3 FFNs: **16.5**;
- rest of a layer after its FFN: **13.5–15**;
- output tensor: **12 without MTP, 13.5–23 with MTP**;
- MTP-layer FFN: **15–20**;
- reducing `-ngl` / moving whole layers: **25–33**, and the cost scales with context.

Moving FFNs before the rest of a layer was reported **4–9% faster** than layer-by-layer placement.

Rules for the RTX+host lane:
- optimize placement by `decode penalty / bytes freed`, not by layer index;
- rerun placement economics when MTP is enabled because shared output/head work is multiplied by draft activity;
- context is part of the placement target because whole-layer CPU attention/state traffic gets more expensive with context.

Hardware was a single unspecified GPU, so these are placement-cost relationships, not a 5070Ti target receipt.

---

## Promoted sparse-cache observability correctness — vLLM #57358

Source PR created: `2026-09-17 11:24:47 UTC`.

After hybrid cache-hit reconciliation, a sparse cache group may contain null placeholders and a shared hit can end between that group's physical block boundaries. The full event-report path discarded the actual hit table and reconstructed events as if `len(group_blocks)` described a dense sequence, eventually indexing past the hash view.

The fix reports from the actual per-group hit blocks and reconciled token count, skips null placeholders, and preserves each real block's exact hash/parent/token span. Scheduling and cache contents are unchanged.

Rule: observability must consume the real sparse physical representation. Reporting code is not exempt from cache topology invariants merely because it does not choose the model output.

---

## Non-promotions / screening notes

- No new M1 Max Flash-Next **128K measured TG** receipt appeared in this interval. The fresh M1 Max DS4 Q2 result from the prior watch remains the strongest direct M1 evidence, but its measured TG stops at the real ~32K prompt and its 128K evidence is admission/load only.
- The M5 Max SSD-streaming result is important physical evidence but intentionally refuses MTP and does not involve TB4 PP.
- The vLLM host-sync and graph-capture gains are CUDA/distributed transfer evidence, not Apple rate claims.
- oMLX offload receipts are single-M5 expert-residency observations, not evidence for the dual-M1 target.
- Component/kernel wins remain component evidence unless the PR supplies an end-to-end cell. The recovered #57319 addendum is a particularly clean negative example: a 2.46–3.50x final sampler reduction did not improve serving throughput.

## Updated implementation implications

The new evidence sharpens the dual-M1 qualification plan without changing its goals:

1. Make committed sequence/frontier ownership explicit on both PP stages. Identify every device→host or cross-stage metadata read and prove which can be replaced by authoritative host/consensus state.
2. Include the exact maximum verifier/batch width in graph/JIT qualification; exercise boundary±1 and max, and record rank arrival skew.
3. Treat speculative row state as a typed record: token id/value, semantic mask, position, target/draft ownership, rollback epoch and cache frontier move together.
4. Record physical packed dimensions after quantization and partitioning, not only logical layer dimensions.
5. For any SSD/host-memory expert experiment, log cache hits, bytes filled per committed token, synchronization time and storage throughput. Raw bandwidth alone is not a performance explanation.
6. Preserve runtime-route provenance separately from checkpoint-layout compatibility.
7. Keep 40@128K / 400 PP frozen until the real dual-M1/TB4 quality-quant ruler produces a receipt.

## New hard boundary

**`2026-09-17 13:43:30 UTC`**.

Future searches continue strictly after this timestamp.