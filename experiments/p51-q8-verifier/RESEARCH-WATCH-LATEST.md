# Latest external runtime watch

## Active scope

Research remains centered on:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**
- **Qwen3.8-27B — one M1 Max 64 GB**
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**
- **Blazer / custom ~5.x-BPW execution work** where evidence transfers cleanly

Do not maintain a dedicated future M5/M5-Ultra lane unless explicitly reopened. Stronger-Apple evidence remains transfer/mechanism evidence unless it reproduces an active topology.

---

## Read order for the next research pass

1. `experiments/p51-q8-verifier/RESEARCH-STATE.md`
2. `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`
3. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-14-0007.md` — newest complete delta: Flash iQ 3.3-bpw capacity/quality, direct Apple 3-bit/mixed-expert fused decode, grouped-MTP scheduling, cold-MTP JIT calibration, MTP-specific expert geometry, partial speculative checkpoint ownership, Qwen4Exp route/warmup provenance, exact top-k specialization/determinism, bounded replay, and fresh SM120 Qwen3.8 regression.
4. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-2115-ADDENDUM.md` — targeted mlx-serve Flash-Next backfill: direct Apple QSA gather/select/history receipts, adaptive MTP/coarse-head rerank, M5 1M community receipt, grouped-MTP evidence, and distributed-MTP PP2 implementation hypothesis.
5. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-2057.md` — generated-prefix MTP history, route-specific SDPA transient capacity, distributed-MTP constraint, coherent prompt cache, live-length gather geometry, sampler support, dummy-draft KV poisoning, M1 long-context correctness.
6. `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-13-1533.md` — TB routable-address discovery, executed PP ownership, live memory admission, lazy-send/collective ordering, recurrent checkpoints, DCP interleave mapping, EPLB warmup isolation.
7. Older 2026-09-13 / 2026-09-12 / 2026-09-11 / 2026-09-10 / 2026-09-09 notes remain retained for QSA/MTP, offload, PP/TP, recurrent rollback, cache/state, transport, ABI, precision and soak methodology.

Because `RESEARCH-STATE.md` predates later dated deltas, this watch chain remains part of canonical working context.

---

# Freshness discipline

The latest complete pass covers substantive sources strictly after `2026-09-14 00:57:57 UTC` through `2026-09-14 04:07:40 UTC`.

**Hard source-freshness boundary for the next complete external search: `2026-09-14 04:07:40 UTC`.**

Evidence timestamp = substantive source timestamp, not crawl, rediscovery, rebase, comment-only activity or merge-only churn.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 remains frozen/promoted; P69B13 remains next only from existing measured GDN/projection/downstream-tail profiling.**

Recent Apple evidence changes confidence, not calibration: **40 tok/s @ ~128K remains a credible success floor for a fully tuned dual-M1 implementation; 50+ remains a plausible stretch until exact dual-M1 evidence exists.**

---

# Newest directly relevant evidence — 2026-09-14 00:07 ET

## mlx-serve — 3.3-bpw Flash pack + fused expert execution

The new iQ-MLX Flash-Next pack is **52 GB resident**, with **85.6% held-out top-1 agreement vs BF16** versus **89.1%** for the mixed-4/8 pack. This is a real single-64GB capacity fallback, not a reason to demote the higher-quality dual-M1 primary plan.

More important for the primary plan, mlx-serve now admits 3-bit experts into its fused MoE decode path and improves the common expert down/reduce kernel. M4 Max, four alternated boots, MTP off: **52.1 -> 56.5 tok/s** on the 3.3-bpw pack and **54.3 -> 56.3** on mixed 4/8. The mixed-pack gain proves the lane/reduction mechanism is not merely a 3-bit workaround.

**Promote:** physical expert width/packing and actual fused-kernel admission are execution identity. Configured quantization alone proves nothing.

## mlx-serve grouped-MTP scheduling + cold-MTP calibration

`#420` dispatches grouped draft graphs before verify-graph construction so GPU draft work overlaps CPU graph building; PLE wait falls about **7 ms -> <1 ms/round**. Four-stream @128K paired boots show small positive gains; one stream is unchanged.

`#421` finds a more fundamental controller problem: the first live speculative width can pay **139–148 ms** of Metal compile inside the planner's cost sample versus **25–31 ms steady**, poisoning the learned width price. The proposed fix warms all relevant verify widths/group row totals/head projections with throw-away state and revalidates wider cells after a trustworthy narrower cell matures. First-round cost becomes ~**25 ms**; load adds ~1.1–1.4 s.

**Promote:** planner cost tables must distinguish compile state from steady execution and be keyed to the actual engine/build/kernel route. Long-context-only QSA arms still need live-bucket qualification because load-time warmup cannot manufacture their real KV shapes cheaply.

## oMLX #3659 — MTP-specific expert geometry

Qwen4-Exp target and MTP head can carry different expert counts/top-k. The patch adds proposal-specific expert geometry rather than inheriting target values.

**Promote:** record target and MTP expert count/top-k independently; wrong inheritance can corrupt loading, routing, quant dispatch, memory planning and acceptance.

## llama.cpp #28873 — partial speculative checkpoint ownership

Full-attention draft KV was serialized/restored even under `PARTIAL_ONLY`, despite rollback already reconstructing it with `seq_rm`. At 200K the redundant state is cited as **400–900 MB**; Qwen3.8-Flash-Next on a 4-GPU box reports new-turn TTFT **3.5 s -> <1 s** after omitting it.

**Promote:** logical checkpoint completeness does not require physically duplicating deterministic/reconstructible state.

## vLLM #56742 — Qwen4Exp execution provenance

Fresh bring-up fixes cover explicit MTP hidden-buffer device placement, normalization of serialized `qwen_sparse_attention` back to the execution spelling used for QSA classification, and Qwen4Exp inclusion in Qwen Triton warmup.

**Promote:** config spelling -> layer classification -> physical allocation -> warmup -> executed kernel is one provenance chain.

## vLLM #56743 / #56749 — exact sparse top-k execution and determinism

- #56743: DSV4.1 K=512 missed its fast gfx950 path; shape-specific tuning produces large kernel wins across 10K–1M but no clear E2E serving gain. Transfer the exact-K/live-shape dispatch rule, not the percentage.
- #56749: tied prefill indexer scores can change selected sparse context when row batching changes. Stable value-desc/index-asc selection is proposed. Transfer tie-order determinism as a correctness gate.

## vLLM #56752 — decoder-side bounded replay

Layers whose real dependency is only a 128-token SWA window can replay just that window rather than the full prompt, with explicit guards for incompatible PP/CP/adaptive-verification/Engram/drafter geometries. This extends the existing bounded-replay principle: full-history forwarding is unnecessary when a smaller authoritative dependency is proven, but stage ownership and metadata lifetime are part of the proof.

## llama.cpp #28877 — fresh SM120 Qwen3.8 regression

RTX 5090 Laptop (SM120) + Qwen3.8-27B reproduces a CUDA misaligned-address fault in unary sigmoid/PDL under two concurrent long-prompt slots on a recent build. This is not an RTX5070Ti receipt, but it is directly relevant 50-series/SM120 architecture-family evidence.

**Promote for RTX5070Ti:** qualify the exact current binary/driver with concurrent long-prompt soak and record the unary/PDL route. “SM120 supported” is not enough.

---

# Fresh negatives / non-promoted results

- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No exact RTX5070Ti16 Qwen3.8-27B throughput receipt.
- No exact new dual-M1 DS4-0731 receipt.
- External HF/Reddit search produced no source-time-qualified new active-topology receipt.
- `antirez/ds4` V4.1 CUDA work predates this boundary; do not refresh it.
- Merge-only activity does not refresh older evidence.
- No P69 target/order change.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control. Highest-priority gates now include:

1. distributed-Lightning-MTP correctness/topology proof;
2. target-vs-MTP expert geometry provenance;
3. compact QSA selected-K/V decode and prefill, exact/deterministic top-k;
4. physical quant packing -> fused-kernel admission -> executed route;
5. speculative cost tables after correct width/shape JIT warmup, with stale-cell invalidation;
6. long-context buckets qualified separately from boot warmup;
7. logically complete but non-duplicative checkpoint/state ownership;
8. minimal recurrent/QSA history ownership and bounded replay only where stage/metadata geometry proves it safe;
9. prefix-cache committed-boundary identity across backbone/QSA/GDN/PLE/MTP;
10. existing TB4 transport, actual stage ownership, transient admission, lazy collective ordering, cancellation/failure/reload and 64K/~96K/~128K semantic gates.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement or sequencing change. **P69B12 frozen/promoted; P69B13 next.** Fresh evidence reinforces exact-shape dispatch, executed-kernel provenance and warm-JIT measurement discipline only.

## RTX5070Ti16

No target movement. Add a **current-build SM120 concurrent-long-prompt soak gate** from #28877, with exact driver/commit and unary-sigmoid/PDL route recorded, alongside existing stride/executed-route checks.

## DS4-0731 dual M1

No target movement. K=512 sparse-top-k and bounded-replay results are later-model/other-hardware mechanism transfer only.

---

# Standing rules added/reinforced

- MTP proposal-head expert geometry may differ from target MoE geometry; record both.
- First-use JIT must not silently become the learned steady-state price of a speculative width.
- Warmup identity includes width, row total, projection mode and physical kernel route; long-context-only routes need separate live qualification.
- Configured quantization is not execution evidence; record physical packing and whether the fused path actually admits it.
- Logical checkpoint completeness does not imply duplication of reconstructible full KV.
- Sparse top-k correctness includes deterministic tie order under batch reshaping.
- Architecture-family support does not certify a current build under concurrent long prompts.
- Kernel/component gains do not move canonical targets without exact active-topology E2E evidence.
- Merge/crawl time does not refresh older evidence.
- Requested/configured/planned remains distinct from built/available/admitted/executed.
- **P69 remains isolated.**
