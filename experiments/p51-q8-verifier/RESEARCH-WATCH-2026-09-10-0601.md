# External Runtime Research Watch — 2026-09-10 06:01 ET

Starting canonical head: `1c302969e7f344b56549df94e4f44fe746838880`.

Starting hard source-freshness boundary: **2026-09-10 00:38:49 UTC**.

This is the first genuinely fresh search after the 00:16 ET Reddit source-correction/backfill. The backfill remains retained evidence but did not advance the prior cutoff.

## Verdict

**Material mechanism / qualification update. No canonical target movement.**

No post-cutoff search result provided a new exact rate receipt for:

- Qwen3.8-Flash-Next on 2x M1 Max 64 GB / direct TB4;
- Qwen3.8-27B on one M1 Max 64 GB;
- the fully-resident Q3_K_XL/native-MTP RTX 5070 Ti 16 GB speed lane; or
- DeepSeek-V4-Flash-0731 on 2x M1 Max 64 GB / direct TB4.

The strongest new evidence materially improves the Flash-Next PP mechanism case, the Apple-cluster bring-up gates, and the exact execution-shape/correctness plan.

---

## FRESH / oMLX #3534 — Flash-Next prefill removes PLE + hyperconnection critical-path work

Source: https://github.com/jundot/omlx/pull/3534

Merged as `9e71c6e0d959ac3ad6bfa5b6903b4fafbe06af82` at **2026-09-10 03:22:30 UTC**.

Physical configuration:

- Apple **M5 Max 128 GB**;
- `Qwen3.8-Flash-Next-oQ4e-mtp`;
- SSD-backed PLE enabled;
- native extensions built;
- code prompts;
- **MTP OFF** for the prefill comparison;
- interleaved A/B chain with a fresh server per arm.

The changes attack three concrete costs:

1. fuse/compile hyperconnection norm/projection/stream-mean work;
2. assemble SSD-backed PLE rows on host so each family/chunk gets one compact upload instead of touching all 129 shards;
3. gather the next chunk's PLE while the current chunk's GPU work is executing.

Representative per-2048-token chunk attribution:

- total: **1,817 -> 1,536 ms (-15.5%)**;
- hyperconnections: **250 -> 144 ms**;
- PLE: **248 -> 35 ms**.

Nested-prefix prefill receipts:

| rung | tokens actually prefilled | before | after | gain |
|---|---:|---:|---:|---:|
| ~16K | 16,010 | 1,170 tok/s | **1,556 tok/s** | **+33%** |
| ~63K | 49,127 | 1,191 | **1,402** | **+18%** |
| ~134K | 72,110 | 1,194 | **1,353** | **+13%** |
| ~229K | 95,454 | 1,159 | **1,301** | **+12%** |

The separate app-admin cold exact-N benchmark with unique prefixes / `skip_cache_store`, 128 generated tokens and MTP off reports:

- 16K: **1,165 -> 1,554 tok/s**, TTFT 14.1 -> 10.5 s;
- 64K: **1,219 -> 1,433**, TTFT 53.8 -> 45.7 s;
- 128K: **1,243 -> 1,390**, TTFT 105.4 -> 94.3 s.

Generation remains effectively unchanged in that comparison, around **51 TG at 64K and 46.5 TG at 128K**.

### Promotion

This is **direct Apple / exact-model transfer evidence**, not a numeric M1-Max transfer.

It strengthens the mechanism case behind the 400 tok/s dual-M1 cold-PP target because:

- Flash-Next PP still has substantial removable graph/PLE orchestration cost;
- SSD PLE is not intrinsically a large serial stall if selected rows are compacted and overlapped correctly;
- the useful optimization is chunk-pipelined producer/consumer work, not simply making the PLE resident;
- benchmark provenance must state PLE placement, warm/cold state, MTP state, exact prefilled denominator and cache-store policy.

Do **not** convert the M5 absolute rates to an M1 prediction.

---

## FRESH / oMLX cluster — MLX fast CPU/GPU synchronization can deadlock two-Mac inference

Source commit: `5df528e50f8164137c29baf06240b3ddb119b98d` at **2026-09-10 07:49:37 UTC**.

A two-Mac TCP Ring run of `DeepSeek-V4-Flash-0731-oQ2.5e-mtp` stalled twice during 64K prefill with MLX Metal fast synchronization enabled. Remote samples showed fence waits. Changing only `MLX_METAL_FAST_SYNCH` to `0` completed the same **65,536-token prompt + 128-token decode**.

The commit restores `MLX_METAL_FAST_SYNCH=0` as the cluster-rank default because the fast CPU/GPU synchronization path is documented as unreliable for this use.

### Promotion

This is direct **two-Mac distributed correctness evidence**, but the commit does not establish the Mac generation, so it is not an exact dual-M1 rate receipt.

For our cluster qualification:

1. default the initial PP2 bring-up to the reliable synchronization path;
2. record `MLX_METAL_FAST_SYNCH` in benchmark provenance;
3. make 64K+ prefill / decode completion a hard stability gate before measuring rates;
4. only A/B the fast-sync path after correctness, with fence-wait/deadlock detection and long-context repetitions;
5. a faster synchronization mode that intermittently stalls does not qualify as a throughput optimization.

---

## FRESH / oMLX #3553 — Flash-Next decode work is strongly execution-shape specific

Source: https://github.com/jundot/omlx/pull/3553

Draft head `a04d2408183c130d24a968ed74732260eb55d0be` at **2026-09-10 09:44:55 UTC**. Measurements are on M5 Max 128 GB, `Qwen3.8-Flash-Next-oQ4e-mtp`, SSD PLE, 512 generated tokens, mostly greedy, with interleaved A/B runs and kill-switchable exact/bit-exact paths.

The six-lever bundle is especially useful because it measures the awkward Flash-Next/MTP shapes directly rather than inferring them from dense GEMM intuition:

### Gathered indexed-KV QSA decode

A two-pass kernel consumes selected K/V through an int32 index list without materializing the gather or walking the whole masked prefix.

Reported MTP gains at ~16K / 63K / 134K / 229K: **+0.3 / +4.8 / +6.8 / +1.0%**; serial gains **+0 / +1.6 / +1.7 / +2.3%**. Prefill is flat.

### Verify-row GDN fusion

Flash-Next's 36 GDN layers see **2..8 rows** in the MTP verify path. A fused verify arm covers conv, SiLU, q/k norm/scales, gate/beta and state updates. A rare precise-exp mismatch was found to shift recurrent state and fork greedy output roughly 160 tokens later, demonstrating that local kernel closeness is insufficient for recurrent correctness.

Pinned depth-1 / 5K gains about **+3.4%**; adaptive code/prose gains are smaller, generally ~0.1-1.9% in the reported 5K/40K examples.

### Grouped mixed-quant verify projections

Verify-row projection grouping is checked across mixed signatures including **4/64, 5/128, 6/64, 8/32 and 8/128**. The same grouping applied to single-row decode was **-1.6 to -2.4%**, so it is deliberately restricted to verify rows.

This is highly relevant to Blazer: a packing/grouping win can be phase-specific even within the same model and tensor family.

### Parked-MTP head priming

Keeping a parked draft head incrementally primed lets long-context MTP re-entry start from the committed head state instead of cold. In the cited 68K production-sampling example, a controller parked after 154 tokens, re-entered with the head primed at 68,600 and stayed on MTP for the remaining 742 tokens.

### Narrow gathered QSA windows

The MTP head's 2..8-row committed folds previously missed both the one-row decode arm and >=16-row prefill arm, falling into dense masked attention. Allowing 2..15-row text windows to take gathered QSA beyond 16K gives **+4.6% at 82K code** and cuts head time/cycle there from **3.4 -> 1.8 ms**; shorter/other prompt classes are smaller or neutral/slightly negative.

### Measured negatives

- prompt-lookup n-gram drafting: **-10 to -20%**;
- proposed block-sparse prefill kernel: **3.6x slower**;
- MMA GDN prefill recurrence rewrite: low leverage because recurrence is only ~6.5% of a prefill chunk.

### Promotion

Keep candidate selection **phase × row-count × context × quant-signature specific**.

Our Flash qualification should explicitly include:

- serial n=1 decode;
- MTP verify rows 2..8;
- narrow 2..15-row committed-head folds;
- large-M/chunked prefill;
- context rungs where gathered-QSA crossover changes;
- exact recurrent-state/output parity after hundreds of generated tokens, not only local tensor tolerances.

The PR is draft and M5-specific. It does not move the dual-M1 rate target.

---

## FRESH / llama.cpp #28330 — sparse indexer state is K-only; do not budget a fake V cache

Source commit: `311d4211bf1611ff7ca6b67035a4a07c79766efc` at **2026-09-10 08:55:46 UTC**.

llama.cpp removes allocation of a V cache for the sparse indexer because it is not consumed.

### Promotion

Flash/QSA cache-memory accounting must follow the **semantic state actually read**, not mechanically allocate a K+V pair because an API resembles attention KV.

For dual-64GB planning, inventory indexer/cache memory by actual tensor role and ownership. Any context/headroom gain must be measured from the resulting allocation; this commit does not provide an M1 byte/rate receipt.

---

## FRESH / vLLM #56237 — same graph-token count does not imply same captured sparse-indexer layout

Source: https://github.com/vllm-project/vllm/pull/56237

Created **2026-09-10 08:37:17 UTC**, updated 09:27:34 UTC.

Flattened speculative decode can produce two different request layouts with the same total graph-token count, e.g. `[2,2]` followed by `[1,1,1,1]`. The old condition allowed the compressed sparse-indexer sequence-length result to switch allocations between those shapes. CUDA graph replay retained the address from capture and could therefore consume uncompressed context lengths.

MI355X reproducer:

- stock: buffer address changed; expected `[100,125,150,175]`, replay saw `[401,501,601,701]`;
- one-line ownership fix: stable address and correct replay.

The accompanying adaptive DeepSeek-V4 GSM8K run reportedly moves from **0.3723 flexible / 0.2767 strict** to **0.9507 / 0.9507**, while fixed-K/no-spec controls are 0.9477-0.9553.

### Promotion

For captured/compiled Flash QSA + MTP paths:

- `total_tokens` is not sufficient graph identity;
- request row partition, per-row query width, compression state and backing-buffer identity belong to capture provenance;
- every capture/replay test must include equal-total-token / different-row-layout transitions;
- stable host-side metadata is not enough: the exact buffer address/ownership consumed by the captured device graph must remain valid.

This is correctness-transfer evidence, not Apple throughput evidence.

---

## FRESH / vLLM #54713 — retain both exact-replay boundaries for aligned MTP/EAGLE prompts

Merged as `b28c3e1568bfae930f61d4b24940e47528c85d4a` at **2026-09-10 02:54:00 UTC**.

For block-aligned prompts under hybrid speculative decode, an identical resend and a longer sibling can legitimately land on different useful replay boundaries. Retaining only the higher boundary can make the identical resend fall back to zero cache hit.

### Promotion

Our rendered-history / prompt-cache qualification should retain and test all semantically valid replay boundaries needed by:

- exact resend;
- longer sibling/append;
- block-aligned boundary cases;
- MTP/recurrent sidecar restoration.

A cache implementation that performs well only on append but loses exact resend is not certified.

---

## FRESH / rMLX #554 — benchmark rate cross-checks need enough wall-clock window to survive host jitter

Commit `467c600a274aae7ac7851502ade3538588a0ff4f` at **2026-09-10 00:40:54 UTC**.

Three loaded-host failures traced to a client-vs-engine decode-rate cross-check over too short a wall-clock window. rMLX keeps the **10% agreement band** and instead widens the plain-arm streamed decode window from six to ten chunks, giving a 360 ms measurement window. The change adds tests that attribute the failure to the cross-check rather than relaxing provenance requirements.

### Promotion

When our harness cross-checks engine-reported and client-observed TG:

- do not loosen the agreement band merely because the host is busy;
- use a long-enough output window that fixed scheduler jitter is a small fraction of the measurement;
- retain host-load/thermal provenance and refuse rows whose rate identity is genuinely inconsistent.

This is harness methodology only.

---

# SCREENED / no target move

- `mihailescu2m/llama.cpp`: no post-cutoff commit; the M1-Max Flash research log remains valuable retained evidence, not new evidence this pass.
- Rapid-MLX: search surfaced existing August Flash/27B material, no post-cutoff exact target-lane receipt.
- NInfer: current public work remains primarily NVIDIA/sm120-class and did not produce a post-cutoff RTX5070Ti16 canonical speed-lane receipt.
- Atlas: current Flash material remains single-Spark/specification or older transfer evidence.
- MTPLX: search surfaced older M2/M3/M5 Flash reports and known depth/quality/correctness concerns, but no source-time-qualified post-cutoff exact dual-M1 receipt.
- web/Reddit exact-rig search surfaced previously known RTX5070Ti long-context work and older M1/DS4 receipts; nothing post-cutoff justifies a target change.
- a current M1 Max 32GB 27B discussion remains a smaller-memory/plain-AR comparison and is not the canonical 64GB lane.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary; TP2 control**.

Add/strengthen:

1. reliable Metal sync (`MLX_METAL_FAST_SYNCH=0`) as initial cluster baseline and provenance field;
2. repeated 64K+ prefill/decode completion before any distributed rate promotion;
3. PLE selected-row compaction + next-chunk asynchronous overlap as a first-class PP seam;
4. profile hyperconnection work separately from PLE and attention during PP;
5. serial n=1, verify 2..8, narrow-fold 2..15 and large-M prefill as separate kernel cells;
6. QSA capture identity includes row partition/layout and backing-buffer identity, not total graph tokens alone;
7. indexer memory accounting is semantic/K-only where appropriate;
8. retain multiple valid replay boundaries for exact resend and sibling append;
9. recurrent fused-kernel qualification must extend far enough to catch ulp-scale state drift that forks later output;
10. all prior residency, ownership, rollback, compiled-route, concurrency, quant-shape, long-soak and task-quality gates remain.

The M5 PP receipts strengthen confidence in the **mechanism** behind 400 cold PP, but there is still no exact dual-M1 rate receipt and no target movement.

## Single M1 Max64 Qwen3.8-27B

No target movement. **P69B12 remains frozen/promoted; P69B13 remains next from existing measured high-leverage GDN/projection/downstream-tail profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B

No target movement. Fully-resident Q3_K_XL/native-MTP remains the canonical speed lane. Host-backed / streamed long-context configurations remain a separate capacity lane.

## Dual-M1 DS4-0731

No target movement. The two-Mac fast-sync failure/fix is a new distributed correctness gate, not a rate receipt.

---

# Standing decisions strengthened this pass

- Cold PP can improve materially by removing orchestration/graph work even when PLE remains SSD-backed.
- PLE I/O should be compacted, sorted/coalesced where appropriate and overlapped with current-chunk GPU work rather than treated as an unavoidable serial penalty.
- Distributed synchronization mode is part of benchmark identity and must be qualified for long-context progress, not just short smoke tests.
- Flash kernel selection is phase/shape specific: n=1, 2..8 verify, 2..15 folds and large-M prefill are not interchangeable.
- Same total graph-token count does not imply same captured metadata layout or address identity.
- Sparse indexer memory should model what is actually consumed; do not manufacture V-cache cost for K-only state.
- Cache certification includes exact resend and sibling append replay boundaries.
- Recurrent numerical parity must be judged on downstream state/output stability, not merely local tolerance.
- Engine/client rate provenance should be preserved by sufficiently long measurement windows rather than widened disagreement bands.
- Cross-runtime/cross-hardware mechanism evidence does not move exact-target rates without target-topology reproduction.
- **No canonical target movement this pass.**
- **P69 remains isolated.**
