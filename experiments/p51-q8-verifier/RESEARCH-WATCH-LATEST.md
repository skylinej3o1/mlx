# Latest external runtime watch

## Active scope

Research remains centered on:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**
- **Qwen3.8-27B — one M1 Max 64 GB**
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**
- **Blazer / custom ~5.x-BPW execution work** where evidence transfers cleanly

Stronger-Apple, newer-model, CUDA and ROCm results remain transfer/mechanism evidence unless they reproduce an active topology. Do not create a dedicated future M5/M5-Ultra lane unless explicitly reopened.

---

## Read order for the next research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-14-0743.md` — newest complete delta: single-stream exact Flash verifier reuse, transient-priced 8192 prefill chunks, Metal decode queue/wait removal, fresh Engram-read revalidation, sparse top-k allocator transient.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-14-0007.md` — 64-GB iQ Flash pack, fused 3-bit/mixed expert decode, MTP cold-JIT calibration, MTP-specific expert geometry, partial checkpoint ownership, sparse tie determinism, bounded replay, SM120 warning.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-2115-ADDENDUM.md` — targeted mlx-serve Apple Flash backfill: compact QSA gather/select/history, adaptive MTP/proposal head, M5 1M community receipt, grouped MTP, distributed-MTP PP2 hypothesis.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-2057.md` — generated-prefix MTP history, SDPA transient capacity, distributed-MTP constraint, coherent multi-slot cache, live-length gather geometry, dummy-draft KV poisoning, M1 long-context correctness.
7. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1533.md` — TB routable discovery, executed PP ownership, live memory admission, lazy-send ordering, internal checkpoints, DCP interleave.
8. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1237.md` — live-context sparse work, DFlash2 causality, candidate-pruned proposal head, retained-history offload, parallel JIT, multimodal pre-prefill TTFT.
9. Older 2026-09-13 / 09-12 / 09-11 / 09-10 / 09-09 watches and mining notes remain retained for QSA/MTP, PP/TP, recurrent rollback, cache/state, transport, ABI, precision and soak methodology.

`RESEARCH-STATE.md` predates several later dated deltas, so this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest **complete** pass covers substantive sources strictly after `2026-09-14 04:07:40 UTC` through `2026-09-14 11:43:49 UTC`.

**Hard source-freshness boundary for the next complete external search: `2026-09-14 11:43:49 UTC`.**

Evidence timestamp = substantive source/measurement timestamp, not crawler, rediscovery, rebase, comment-only activity or merge-only churn.

Important cutoff edge: **vLLM #56822 was created at 11:43:58 UTC, nine seconds after the cutoff.** It was intentionally excluded and should be checked first next pass.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling. Do not reopen P69B8/B9/B10-C from external evidence.**

Apple Flash evidence continues to shift confidence rather than the target: **40 tok/s @ ~128K is a credible success floor for a fully tuned implementation; 50+ is a plausible stretch until exact dual-M1 evidence exists.**

---

# Newest high-value evidence

## mlx-serve #422 — exact single-stream verifier reuse

Created `2026-09-14 04:20:33 UTC`.

Flash-Next single-stream MTP now reuses the exact verifier kernels developed for grouped verification instead of paying the stock gather-heavy chain. Physical savings include route packing, indexed gate/up inputs, adjacent-expert down reuse, fused weighted reduction and prepared-HC graph reuse.

M5 Max 128 GB, mixed-4/8, KV8 target/head, warm prefix, one stream:

- 4K: **+6.6%** median;
- 16K: **+6.2%**;
- 64K: **+4.8%**;
- 128K: **+7.9%**.

The branch qualifies logits, hidden outputs, recurrent state, PLE, QSA and speculative captures across eligible widths.

**Transfer:** closest external Apple confirmation yet of the P69 thesis that verifier-cycle execution itself still has several-percent headroom after MTP already works. Do not transfer the percentage to M1. Put indexed expert inputs, route packing, expert-pair down reuse, fused weighted reduction and HC graph reuse in the Flash verifier experiment queue.

## mlx-serve #423 — transient-priced 8192 prefill chunks

Created `2026-09-14 07:49:10 UTC`, substantive update through `11:39:31 UTC`.

Flash-Next previously capped MoE prefill at 4096 before live admission could price 8192. The new chooser makes 8192 a candidate and takes it only when exact request geometry plus a conservative transient margin fits.

M5 Max mixed-4/8, KV8, MTP on, cold prefill:

- forced 8192 vs 4096 at 128K: **1644 -> 1724 tok/s (+4.9%)**;
- auto-chooser A/B is noisy; order-cancelled estimate at 128K is **~+7.9%**;
- author frames the honest overall effect as roughly **+8%**, with a broad +5..15% bracket.

The deployed 4096->8192 rung costs roughly **3.64 GiB** more estimated transient and uses a 22% safety margin before widening.

**Transfer:** prefill width is a live admission variable, not a model-family constant. Sweep 4096/8192 under exact dual-M1 PP2 ownership and actual transient/reserved memory. This directly supports the 400-PP workstream but is not a dual-M1 calibration.

## ds4 #1041 — Metal command queue vs per-layer waits

Created `2026-09-14 11:18:27 UTC`.

Single-box V4.1 waited for GPU after each of 40 layers. Queuing layers and draining only at true dependency boundaries changed M3 Ultra 512GB fully-resident Q4 decode roughly from **16.7–17.1 tok/s to ~21.4–21.7**, and commit-without-wait reached **23.08–23.09** in the measured 2K/256 cell.

GPU timing:

- waits: **37.3 ms GPU busy / 46.9 ms span**;
- queued: **36.9 ms busy / 37.7 ms span**.

The kernel work barely changed; ~9 ms/token of host scheduling gap disappeared. Combined with #1035 parallel Engram reads: **24.86 tok/s** on that box.

**Transfer only:** later V4.1 / M3 Ultra, not DS4-0731 or dual M1. Add explicit encode/commit/GPU-busy/wait telemetry to Metal qualification and remove per-layer waits unless a real dependency requires completion.

## ds4 #1035 — fresh current-upstream revalidation

Substantive 2026-09-14 revalidation, updated `11:12:35 UTC`.

M2 Ultra 192GB, V4.1 IQ2_XXS/Q2_K, isolated macOS Engram read change:

- **10.205 -> 10.740 tok/s (+5.2%)** over 512-token decode;
- outputs match.

Two observations per arm only. Promote the I/O-shape lesson: tiny scattered Engram reads and large expert slabs deserve separate concurrency policies.

## llama.cpp #28889 — top-k scratch invisible to admission

Created `2026-09-14 08:32:42 UTC`.

Logical argsort input chunk ~64 MB could reserve **300–450 MB** once destination indices, duplicate index storage, key copies and CUB scratch were included. This transient appears at graph execution and was invisible to context admission. Reducing chunk target to 16 MB bounded the transient near **100 MB** and allowed a 55K sparse-indexer prefill on V100-16GB to complete without measurable PP change.

**Transfer:** QSA/indexer workspace admission must use actual execution-time allocator transient, not logical input-size estimates.

---

# Recovered older evidence surfaced this pass

## oMLX #3654 — expert-major offload prefill

Created `2026-09-13 20:46:46 UTC`, so not fresh despite merging now.

For over-capacity expert offload, expert-major chunking avoids repeatedly fetching/evicting the same experts. M5 Max Gemma4-A4B:

- 50% residency warm TTFT **2.38 -> 0.69 s**;
- 25% **8.87 -> 0.85 s**;
- 12.5% **16.60 -> 0.97 s**.

Retain as offload/capacity transfer only.

Merge-only: oMLX #3659, mlx-serve #421 and llama.cpp #28670 are not re-dated.

---

# Critical retained Flash-Next evidence

## Direct Apple QSA

mlx-serve direct Apple work shows sparse selection must stay sparse through actual K/V access:

- decode compact K/V gather at 128K: **23.5 -> 46.1 tok/s**;
- at 256K: **14.6 -> 40.9**;
- prefill block-gather at 128K: **395 -> 654 tok/s**;
- at 256K: **267 -> 551**.

Exact top-k splitting / fused score-sheet work further improves long-context selection. QSA history should be a short raw-key ring + pooled authoritative history, not raw full-history clones in each SSM checkpoint.

## Apple MTP / proposal economics

Retain:

- grouped Qwen4 drafting + row-axis verify while every request owns independent KV/recurrent/rollback state;
- dispatch lazy draft graphs before verify-build to overlap GPU work with CPU graph construction;
- coarse proposal head + exact shortlist rerank;
- consumed-row-only proposal projection;
- adaptive speculation from measured accepted-token economics;
- first-use JIT must not poison learned MTP width costs.

## 1M community calibration

M5 Max 128GB, mixed dense8/expert4, KV8, MTP community receipt remains useful transfer evidence:

- ~80+ tok/s <=256K;
- ~60 around 500K;
- ~40 at 1M original prose result, ~75 coding;
- later current-main claim ~67 at 1M, exact whole-delta commit not isolated.

Do not transfer M5 percentages to dual M1.

---

# Distributed Lightning-MTP — current interpretation

Stock oMLX still rejects distributed MTP. Treat this as an **engineering/certification blocker, not a known architectural impossibility**.

Working PP2 hypothesis:

1. backbone / QSA / GDN / PLE state stays stage-local;
2. one authoritative sampling / verification-control rank;
3. one PP traversal for the whole verifier row block, **not one traversal per drafted token**;
4. authority rank determines accepted-prefix length / sampled continuation;
5. tiny commit/control sync back to the other stage;
6. both stages commit/rollback KV + recurrent + QSA/indexer + PLE + MTP history to the same boundary;
7. prefix-cache sidecars persist the same committed-boundary identity;
8. cancellation/error synchronizes the same boundary before releasing state.

Target and proposal MoE geometry are separate identities; MTP expert count/top-k may differ from the trunk.

Prove distributed-MTP correctness relatively early because its transport/state topology determines which P69/QSA paths are actually hot.

---

# Current Flash-Next optimization stack

Treat as mostly orthogonal / stackable:

1. **QSA/indexer:** compact selected-K/V decode + prefill, live-span geometry, exact/deterministic top-k, fused score path, short raw ring + pooled history, owner-local state, real workspace transient.
2. **MTP/P69 economics:** distributed-MTP correctness, one verifier traversal/round, #422 exact verifier routes, coarse proposal + exact rerank, consumed-row projection, GDN verifier fusion/prework, PLE defer, adaptive depth/speculation, clean JIT calibration.
3. **PP2/MoE/runtime:** actual layer ownership/balance, transient-aware chunk width, TB4 transport/collective order, command commit-vs-wait scheduling, minimal recurrent tails, prefix-cache correctness/recovery.

---

# Current lane consequences

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control.

Priority gates / experiments:

1. distributed-Lightning-MTP correctness/topology proof;
2. compact QSA selected-K/V execution on decode and prefill;
3. port/audit #422 verifier primitives against actual Flash/P69 shapes;
4. sweep 4096/8192 cold-prefill width under exact PP2 transient headroom;
5. command encode/commit/wait telemetry; remove unnecessary per-layer waits;
6. exact top-k/score-sheet/live-shape census and workspace transient;
7. minimal authoritative QSA history + recurrent checkpoint ownership;
8. full prefix-cache boundary identity across backbone/QSA/GDN/PLE/MTP;
9. repeated 64K/~96K/~128K semantic correctness;
10. TB4 routability, actual stage ownership, live admission ceiling, collective ordering and failure/reload certification.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement. **P69B12 frozen/promoted; P69B13 next.**

External #422 strengthens the engineering thesis but does not alter internal sequence. Fresh exact-shape/route evidence may inform B13 implementation only where the shape census matches.

## RTX5070Ti16

No target movement. Keep SM120 physical-stride, device-kernel admission and concurrent-long-prompt soak gates. No exact fresh 5070-Ti receipt.

## DS4-0731 dual M1

No target movement. #1041/#1035 transfer scheduling/I/O methodology only; later-V4.1 percentages do not calibrate the 0731 target.

---

# Standing evidence rules

- Exact target receipt vs transfer/mechanism vs experimental A/B vs planning target must remain separate.
- Actual benchmark cell = **executed physical route**, not requested flags.
- Context is part of target identity.
- Requested/configured precision != physical/executed precision.
- Route provenance: requested -> configured -> built/registered -> device-compatible/admitted -> armed -> executed.
- Memory provenance: load/materialization transient, live tensors, allocator-reserved, speculative derived weights, verifier temporaries, sparse/indexer scratch.
- Prefill chunk width is a physical/admission choice; price exact geometry + measured safety margin.
- Command-buffer commit and wait are separate controls; no host wait without a dependency justification.
- Shared append-only QSA history and checkpoint-local recurrent leftovers are separate ownership classes.
- Recurrent tails must not retain whole prefill chunks through views.
- Prefix-cache correctness is multi-state committed-boundary correctness, not backbone-KV correctness alone.
- Dummy/warmup/padding speculative work must be write-side-effect-free.
- First-use JIT cannot silently become steady-state learned cost.
- Sparse top-k tie ordering must be deterministic under batch/row reshaping.
- A no-forward step can still carry cache/state/transport effects; complete before metadata retirement.
- Distributed cancellation is a coordinated state transition.
- Final output correctness != speculative correctness; acceptance + task quality remain separate.
- Component/kernel gains do not move canonical targets without exact topology evidence.
- Merge/crawl time never refreshes older evidence.
- **P69 remains isolated.**
