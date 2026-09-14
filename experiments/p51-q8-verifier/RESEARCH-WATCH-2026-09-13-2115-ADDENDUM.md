# External runtime watch addendum — 2026-09-13 21:15 ET

## Scope / freshness

This is a **targeted addendum/backfill**, not a new complete external search.

It records Qwen3.8-Flash-Next / mlx-serve evidence surfaced after the complete `20:57 ET` watch was written, plus a planning interpretation of the distributed-Lightning-MTP blocker.

**Do not advance the hard source-freshness boundary. It remains `2026-09-14 00:57:57 UTC`.**

Most mlx-serve implementation evidence below predates that boundary and is explicitly retained at its original source timestamp. One important mlx-serve commit (#412 / `6d3cb6d...`) is actually inside the prior complete-search window but was missed because mlx-serve was not yet part of the regular sweep; classify it as **fresh missed-window evidence** rather than date-refreshed backfill.

Canonical targets remain unchanged. P69 remains isolated.

---

# Fresh missed-window evidence

## mlx-serve #412 / commit `6d3cb6d2863e0ee1aa113bfd0f1f48df45c1ea02` — grouped Flash-Next MTP draft + verify

**FRESH MISSED-WINDOW / HIGH-VALUE FLASH-MTP EXECUTION EVIDENCE.**

Source timestamp: `2026-09-13T22:11:47Z`, inside the previous `19:33:05 -> 00:57:57 UTC` window.

Flash-Next requests can now speculate together: one group planner chooses a draft width per request from measured round cost, one MTP graph drafts all active rows, and one row-axis target verify forward serves the group while each request keeps independent KV, recurrent state and rollback offsets.

Reported paired-boot gains over legacy per-request MTP:

- 4 concurrent streams: **+30.1% @ 4K**, **+26.8% @ 16K**, **+18.9% @ 64K**.
- 2 streams against actively speculating legacy MTP: about **+27%** at all three contexts.
- Single-stream output is byte-identical to the legacy arm with grouping disabled.
- Unit suite: 2503 passed; live two-stream EOS/cancellation parity gate passed.

**Transfer for our PP2 work:** speculative execution does not require one monolithic mutable global state. Independent KV/recurrent/rollback ownership can coexist with a shared draft/verify computation. This strengthens the design hypothesis that our distributed verifier should keep stage/request state local while centralizing only the minimum proposal/accept decision path.

Do **not** transfer the concurrency percentages to dual-M1 PP2.

---

# Recovered mlx-serve Flash-Next implementation evidence — original timestamps retained

## QSA decode gather — commit `96578478da83d10e5d398b605d77ef8537a1b7c0`

**DIRECT APPLE / VERY HIGH-VALUE 128K MECHANISM.**

Old decode built a full-context dense mask and ran full-KV SDPA after QSA had already selected ~2K rows. The replacement gathers selected K/V rows from quantized or dense KV and runs attention only on the compact set.

Locked serial Qwen3.8-Flash-Next, KV8, no speculation:

- 32K: **40.8 -> 51.3 tok/s**
- 64K: **32.9 -> 48.7 tok/s**
- 128K: **23.5 -> 46.1 tok/s**
- 256K: **14.6 -> 40.9 tok/s**

Subset-SDPA vs masked-full parity was exact for the tested quant+dense cases; take-then-dequant was bit-exact.

**Promote:** this is direct Apple confirmation of the same mechanism inferred from llama.cpp #28213. Our Flash QSA audit must prove that selected blocks remain selected all the way through K/V read + attention; a sparse selector followed by dense/full-context execution is a major 128K performance bug.

## QSA prefill gather by block index — commit `7d0120363c98e7daa9b9894b6fb71cc8d7e84c5e`

Older but highly relevant Apple prefill evidence. Replacing dense full-cache masked QSA prefill with direct gathered block attention reported:

- 32K: **589 -> 699 tok/s**
- 128K: **395 -> 654 tok/s**
- 256K: **267 -> 551 tok/s**

N-gram table boot warming also removed a first-prompt penalty in the reported 38K case (**174 s -> 55 s**).

**Promote:** QSA compact gather matters on both decode and prefill. First-request PLE/n-gram warm state must be separated from steady-state PP.

## QSA select + fused score sheet — commit `680e5a56d2ca6926785b404efed06d1d85b563f3`

On M5 Max, the exact sparse top-k block select split across threadgroups and the indexer score sheet was fused into a Metal kernel. Reported live cells:

- 162K: serial **50.3 -> 52.8 tok/s**, MTP **54.8 -> 60.3**, prefill **1393 -> 1413**.
- 361K: serial **47.7 -> 49.6**, MTP **57.7 -> 59.0**, prefill **1115 -> 1168**.
- 805K: serial **39.5 -> 46.6 (+18%)**, MTP **53.5 -> 57.8**, prefill **930 -> 960**.
- The split top-k kernel itself moved ~0.72 -> 0.26 ms/layer at ~215K blocks before a second optimization reduced marginal select cost further.

Greedy answers were byte-identical between arms at 42K/162K/361K/805K; block IDs matched on the tested prompt.

**Promote:** exact top-k, score-sheet fusion and row-count/threadgroup specialization are real Apple long-context hotspots. This strongly reinforces the current Flash QSA/indexer workstream.

## QSA history representation — commit `e0a4264064b86f7aba73e5553a25a6f8b879bab3`

Raw QSA indexer keys were retained for the whole context even though only a short tail was needed to close/reopen partial blocks. mlx-serve changed live raw history to a 32-row ring while the pooled bank becomes the authoritative history.

Reported:

- Removes about **3.2 GB** of raw-key memory at 1M and about **80%** of the prior history-file payload.
- 256K history file: **960 MB -> 192 MB**.
- MTP forced-depth acceptance stayed equal to control across tested warm restore rungs.
- Warm-append ladder 4K -> 1M completed; **1M decode 37.7 tok/s**, peak MLX active **108.8 GB**.

**Promote:** long-context indexer state should store the minimal authoritative history representation, not mechanically snapshot every intermediate/raw row. Rollback reach must be an explicit bound; a rollback older than the retained raw ring should be a named miss/error, not silent truncation.

## QSA/SSM checkpoint ownership — commit `290b84c37483d10e5d398b605d77ef8537a1b7c0`

An earlier design cloned growing QSA history into each SSM checkpoint; 32 copies of a ~273K-row history could add roughly **30 GB** and kill long prefills. The fix stores QSA history once and lets checkpoints own only recurrent/partial-block state.

M5 Max 128GB / mixed 4-8bit / KV8 validation reported:

- 600K needle recovered.
- 1M prefill **509 tok/s**.
- after cool-down: **56 tok/s @ 32K**, **49 tok/s @ 128K** (n=80).

**Promote:** our prefix-cache bundle should separate shared append-only QSA history from checkpoint-local recurrent leftovers. Do not duplicate long-history tensors into every recurrent checkpoint.

## Long-context bundle / adaptive speculation — commit `862bddff472fe7a60a5e2d84b4bfaeaf09b320c5`

mlx-serve's long-context Flash path combines:

- split-K QSA at verify widths with quantized KV;
- exact radix-select block picks;
- per-forward tables / one indexer-history copy;
- per-request + per-chunk prefill width;
- SSD-first prefix cache;
- recurrent checkpoint thinning;
- adaptive MTP using measured serial/spec round prices, with `--max-mtp-ctx` as a hard ceiling;
- QSA-half persistence with the MTP head;
- admission based on reclaimable memory rather than nominal free RAM.

**Promote:** adaptive speculation is not optional polish at extreme context. The controller should compare measured verifier-cycle cost against realized accepted tokens and disable/re-enable MTP when economics cross over.

## Cheaper MTP round / coarse-head exact rerank — commit `58fcfbdf4e8c3763a305943c4b89a4fc6b24f072`

The Flash MTP head was paying the entire ~248K-vocab target projection at every greedy draft step. mlx-serve builds a coarse quantized copy of the target head, selects a small candidate set, then exact-rescores those rows through the real target head.

The commit's internal measurements attribute roughly **8-9%** code/prose improvement to the rerank change in the tested setup, while preserving the target verifier as the source of final bytes.

It also contains two P69-like lessons:

- defer the PLE gather so MTP verify graph construction does not block on lazy draft IDs;
- project only the MTP rows actually consumed (`last_row` / `none`) rather than projecting a whole block and slicing later.

**Promote:** this is direct independent confirmation of proposal precision / target precision separation and full-vocab-work elimination. Audit our Flash proposal head before assuming the P69 verifier itself is the only large-head hotspot.

## GDN prefill state ownership — commit `fa76a4b50b3f54af7e9cd927279f5ba2870f02c6`

The GDN conv-state tail was a view into the whole 4096-token prefill chunk, pinning about **3 GB** across the linear-attention layers. Copying the required three-row tail cut peak by **~2.5 GB** with unchanged prefill speed and changed admission billing from about **8495 MB -> 5184 MB** for the reported 4096-token chunk.

Also adds optional MTP-head KV quantization, reporting acceptance within noise of dense from 4K-128K and saving **960 B/token** with MTP on.

**Promote:** recurrent tails must own only the minimal rows needed after the chunk; views into large prefill tensors can silently pin enormous transients. This belongs in our load/prefill memory provenance ruler.

## Batched/per-request Flash MTP head state — commit `fd9c0c38c8e6dcbf6a33c008f0dd4957447d54af`

Recovered recent evidence from `2026-09-12T19:25:30Z`: Flash-Next MTP head state was made per-request, removing exclusive MTP slots and allowing batched slots to gather selected QSA blocks while preserving independent state.

**Transfer:** another concrete example that independent speculative state + shared verify compute is feasible. Useful architecture evidence for our distributed design, not an exact PP2 result.

---

# mlx-serve 26.9.2 release evidence — source timestamp retained

Release `v26.9.2` (published 2026-09-09) reports for Qwen3.8-Flash-Next:

- M4 Max benchmark table: **83 -> 93 tok/s** between 26.9.1 and 26.9.2 at the release's benchmark cell.
- release note: ~**+50% short-prompt** and ~**+30% at 64K/128K** from the bundle of cheaper speculative rounds, shortlist drafting and long-prompt improvements.
- adaptive speculation now turns itself off when the speculative step costs more than it saves and can turn back on when profitable.
- long Flash sessions can push prefix-cache state to SSD rather than retaining every conversation in memory.
- long-prompt width is chosen per request instead of pinning the narrowest width for a 1M-capable server.

**Classification:** stronger-Apple runtime evidence / implementation transfer. Not active dual-M1 evidence and not a reason by itself to change the canonical 40 target.

---

# Community 1M receipt — Reddit source date retained

Reddit thread: `r/LocalLLaMA/comments/1wb7p70` (published 2026-09-09), authored by a mlx-serve Flash-Next co-creator.

Reported configuration:

- **M5 Max 128 GB**
- Qwen3.8-Flash-Next mixed quant: **dense layers 8-bit / expert layers 4-bit**
- **KV8**
- MTP enabled
- 1 concurrency
- `ctx-size=1048576`
- ~**117 GB peak memory** at full 1M

Reported sampled workloads (temperature 1.0, not only greedy microbench):

- prefill about **1700-1800 tok/s** initially, staying near **~1000 tok/s** toward 1M;
- base generation **100+ tok/s <=16K**, **80+ <=256K**, about **60 @ 500K**, about **40 @ 1M**;
- coding workload about **75 tok/s at 1M** in the original post.

A follow-up comment on 2026-09-10 states the 1M tail was subsequently raised from about **40 -> 67 tok/s (+67%)** and was already in `main` but not yet in the release by 2026-09-11. The exact commit responsible for the entire 40->67 delta has not been isolated here, so retain this as a **community receipt / current-main claim**, not an exact implementation A/B.

**Interpretation for our target:** this materially raises confidence that 40 tok/s @ ~128K is achievable in a well-tuned Apple Flash engine, but the single-M5 topology avoids our TB4/PP2 synchronization cost. Keep the canonical target at 40 until exact dual-M1 evidence exists; treat 50+ as an increasingly plausible stretch rather than a target move.

---

# Distributed Lightning-MTP feasibility assessment — planning, not external fact

The fresh oMLX #3653 constraint remains real: stock distributed serving still rejects distributed MTP. However, current evidence increasingly suggests an **engineering/certification blocker rather than an architectural impossibility**.

Reasons:

1. oMLX already carries pipeline-aware MTP-compatible model paths with recv/send/all-gather mechanics for ordinary PP serving.
2. mlx-serve demonstrates that Flash MTP can keep independent per-request KV/recurrent/rollback state while sharing draft/verify compute.
3. oMLX already has explicit MTP rollback/history/prefix-sidecar machinery; the distributed problem is to make commit ownership and collectives agree across ranks.

Working implementation hypothesis for dual-M1 PP2:

1. keep backbone/recurrent/QSA/PLE state stage-local;
2. designate one authoritative sampling/verification-control rank;
3. run one normal PP traversal for the target verifier over the whole speculative row block, not one traversal per draft token;
4. authoritative rank determines accepted prefix length / sampled continuation;
5. send a tiny commit/control message back to the other stage;
6. both ranks commit/rollback KV + GDN + QSA/indexer + PLE + MTP head history to the same token boundary;
7. prefix-cache sidecars persist the same committed boundary identity;
8. cancellation/error paths synchronize the same decision before releasing state.

Current planning judgment: **do not rethink the dual-M1 project because of the stock MTP rejection.** Prove distributed MTP correctness relatively early, because its communication/state topology determines which verifier paths are actually hot and therefore which P69/QSA optimizations should be ported first.

Do not encode the confidence percentages from conversational planning as measured evidence.

---

# Updated Flash-Next optimization stack

Treat the major workstreams as largely orthogonal and potentially stackable:

1. **QSA/indexer long-context path**
   - gathered selected-K/V decode;
   - gathered block prefill;
   - live-span/launch geometry;
   - exact/deterministic top-k;
   - fused score-sheet path;
   - minimal raw-key ring + pooled authoritative history;
   - owner-local state.
2. **MTP / P69-style verifier economics**
   - distributed MTP correctness first;
   - one verifier traversal per round;
   - coarse proposal head + exact shortlist rescoring;
   - project only consumed rows;
   - GDN fused verifier prework/recurrence;
   - PLE defer / graph-build overlap;
   - adaptive depth/speculation based on measured round economics.
3. **PP2 / MoE / runtime**
   - actual stage ownership and balance;
   - TB4 transport and collective ordering;
   - live capacity/transient admission;
   - minimal recurrent-tail ownership;
   - allocator/pool lifecycle;
   - prefix-cache + SSD tier correctness and failure recovery.

The canonical 40 tok/s @ ~128K target remains unchanged, but recent mlx-serve evidence shifts the **confidence calibration**: 40 should be treated as a credible success floor for a fully tuned implementation, not an assumed ceiling. Do not move the target until exact dual-M1 measurement exists.

---

# No target / P69 changes

- Flash-Next dual M1: **40 tok/s @ ~128K**, **400 tok/s cold PP** — unchanged.
- 27B M1 / 5070 Ti / DS4 targets — unchanged.
- P69B12 remains frozen/promoted.
- P69B13 remains next only from existing internal measured evidence.
- No external mlx-serve result is allowed to reorder P69.
