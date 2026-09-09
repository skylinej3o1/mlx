# External runtime research watch — 2026-09-09 06:28 ET

Starting freshness boundary: `3692caf919864cc3a74c49da6eb6f0c92b55ac85` / **2026-09-08 22:21:02 UTC**.

Read with `RESEARCH-STATE.md`, `RESEARCH-TARGETS.md`, `RESEARCH-WATCH-LATEST.md`, and the prior dated watches. This note is a delta, not a replacement for the durable state.

## Executive result

No canonical planning target moves in this pass.

The pass adds one new exact-hardware RTX 5070 Ti result, but it is a **different capacity lane** from the canonical fully-resident Q3_K_XL speed lane: a model-specific `UD-IQ4_XS` hot/cold-KV runtime using host RAM as capacity. It materially expands the 5070 Ti long-context design space without contradicting the existing 120 TG / 250 cold-PP working target for the fully-resident speed configuration.

The most important cross-runtime correctness result is a concurrency-only MTP ownership regression: an ownership ticket accidentally shared a counter with capture generation, leaving C=1 unchanged while reducing C=2 decode by about 24%. This strengthens the existing requirement that B2/B3/B4 include interleaved admissions between capture and first propose; B1 equivalence cannot certify concurrent speculative state.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

`RESEARCH-TARGETS.md` remains authoritative. The fresh 5070 Ti result below uses a larger `UD-IQ4_XS` artifact plus a host-backed long-context KV ring; the target file explicitly defines the 120-TG lane around a fully-resident Q3_K_XL/native-MTP configuration and excludes spilling IQ4_XS configurations from defining that speed target.

---

# FRESH — exact RTX 5070 Ti 16 GB Qwen3.8-27B long-context capacity runtime

## BrunoPPassini/llama.cpp `qwen38-blackwell-256k`

Fresh public branch commit `1a63cbf1220714f7a20a6f139a603f0ccada5a59` landed **2026-09-09 00:13:45 UTC**, followed by performance/provenance documentation through `daa7e974f5b702ba65acb06dbf030811b2d9df27` at 00:28:34 UTC.

Measured system:

- GeForce RTX 5070 Ti, 16,303 MiB reported;
- Ryzen 7 9800X3D, 48 GiB DDR5-6400;
- PCIe 5.0 x16;
- CUDA 13.3 / driver 591.86;
- Qwen3.8-27B `UD-IQ4_XS`;
- Q4_0 target and draft KV;
- deterministic native MTP3;
- exact artifact/runtime hashes published.

The runtime exploits the hybrid architecture rather than treating the model as a conventional transformer: 48 recurrent GDN layers carry fixed-size state and only 16 full-attention layers need token-indexed K/V history.

The 256K design uses:

- a logical 262,144-token KV space;
- a 65,536-token GPU-resident hot prefix and page-locked host-memory cold tail;
- CUDA VMM for stable virtual addresses with bounded physical commitment;
- 8,192-token staging tiles;
- copy / Q4 conversion / attention overlap across separate streams;
- online-softmax state across partitions rather than independently normalized tiles;
- shared target/MTP compute arena;
- recurrent transaction-log / phase-arena state so rejected speculative work does not require four full recurrent-state planes.

Measured endpoints:

| Cell | First controlled path | Accepted optimized path | Delta |
|---|---:|---:|---:|
| short / GPU-resident | 1888.63 PP / 42.11 TG | 1745 PP / **82.34 TG** | TG +95.5%, PP -7.6% |
| 87,160 input + 64 output | 1100.65 PP / 23.33 TG | 1104.85 PP / **41.53 TG** | TG +78.0% |
| 256,257 input + 64 output | 654.07 PP / 15.40 TG | 698.84 PP / **23.97 TG** | TG +55.6%, PP +6.8% |

Important qualification: the document explicitly separates the **82.34 TG isolated controlled short path** from a **71.16 TG fully integrated daily reference**. Do not quote 82.34 as a general sustained server rate.

The 87K final path matched the accepted output hash and MTP counters; the 256K before/after cell used the same 64-token output protocol and matched output hashes. Below 65,536 effective tokens the hot/cold route declines and stock GPU KV remains active; a 42,109-token dual-path control measured only about -0.18% PP / -0.24% TG overhead.

A precision control found Q8 KV could reproduce the same 1,024 output token IDs in the tested long runs but around 100K cost roughly 23% decode and 14.8% PP versus Q4, so the published profile remains Q4.

### Promotion

Create a separate **5070 Ti long-context capacity lane** rather than changing the fully-resident speed target:

- host RAM is capacity; VRAM is a working set;
- benchmark bulk asynchronous H2D staging against direct mapped-host reads rather than assuming zero-copy is better;
- recurrent-state lifetime is a first-class memory lever, separate from KV precision;
- VMM remap needs a content epoch because a stable virtual address does not imply stable data;
- record hot/cold boundary, tile width, transfer bandwidth, copy/convert/attention overlap and PCIe link state;
- exact long-context qualification includes output hash, MTP counters and route admission/fallback;
- report isolated controlled peaks separately from integrated daily serving rates.

**No target movement:** this is exact hardware, but not the canonical fully-resident Q3_K_XL target configuration.

---

# FRESH — Atlas #968: concurrency-only MTP ownership regression and corrected carry provenance

## `fdc912b108ccf7f83dc5283e75b44148f87e15a5`

Atlas hardened a model-global cross-turn MTP carry that had been using common-prefix agreement as if it were request/session identity. The carry now stamps the existing session identity and refuses foreign or zero-identity adoption.

The shared `mtp_prefill_hidden` interval also had row coverage but no writer identity. A later request could replace or merge into the interval and another request could pair its own tokens with foreign hidden rows. The interval now carries an unconditional allocation-time owner ticket; a foreign write takes ownership instead of extending the previous interval, and a foreign read is refused.

Configured and armed state were also separated. The carry could print `ON` from configuration while the actual runtime disabled it whenever `mtp_max_seqs > 1`; the default cap is 32. The report now reflects the actual armed predicate. This is another concrete example that **configured != armed != executed**.

### Regression found while implementing the ownership stamp

The first store-ticket implementation drew tickets from the same counter used for `mtp_prefill_capture_gen`. Every new sequence allocation advanced that shared counter, so an admission between another sequence's capture and first propose silently invalidated that earlier sequence's drafter prefill.

Measured concurrency sweep:

| concurrency | parent | coupled-counter bug |
|---:|---:|---:|
| C=1 | 18.5 | 18.5 |
| C=2 | **30.8** | **23.7**, repeat **23.4** |
| C=4 | 45.4 | 51.1 |
| C=8 | 63.0 | 63.3 |
| C=16 | 90.1 | 90.4 |
| C=32 | 105.3 | 105.1 |

C=2 TPOT moved roughly 62 -> 79 ms. The defect therefore cost about **24% of C=2 decode while C=1 was identical**. Accuracy did not move, as expected for a speculative-path acceptance/performance defect.

The corrected implementation uses a distinct ticket dispenser. Its certification reports C2 27.8 against a 24.1 floor and DFlash2 C2 48.0 against a 35.4 floor, with the broader 11-gate campaign passing.

### Promotion

- Distinct ownership meanings get distinct counters / ticket namespaces. A separate field sourced from a shared counter can recreate the original coupling.
- Add an explicit **admit-B between A-capture and A-first-propose** cell to B2/B3/B4.
- B1 identity is not evidence that a state feature is concurrency-safe; identical C1 can be the fingerprint of an interleaving-only bug.
- Throughput/acceptance gates are required in addition to answer-quality gates for lossless speculation.
- Record configured / armed / actually executed separately for cross-turn carry and other conditional accelerators.
- The new host ownership stamp still does not prove capture-copy -> catch-up-read device happens-before; the earlier device-ordering gate remains required.

---

# FRESH — rMLX speculative round invariants become single-source and auditable

## #549 / `9567876605f14cd2b2090689d80000c469c7499e`

rMLX now drives speculative round width and rollback targets through one producer across the round loops and adds a per-round stream/oracle for equivalence checks.

A new phase-charge CI gate requires each round loop to name one charge decision and use the same decision for rollback accounting and `RoundPhases` / `RoundStats`. This closes a provenance hole where tokens and answers could remain identical while work was silently attributed to the wrong phase.

The adaptive schedule now narrows through the same shared round-block logic rather than computing a parallel interpretation of remaining budget.

## #550 / `28dc628426acb65f2b56c2ee742faca873e00179`

DFlash and EAGLE-3 now share one acceptance walk. The shared path refuses a malformed verifier block unless its shape is exactly:

`verified target rows = proposed draft rows + 1 correction/bonus row`.

Previously a swapped/malformed call could report more proposals accepted than were actually proposed.

The verifier codec, context ceiling and per-layer cache-stack construction also move to one producer; the two-model drafter cache stack uses the same builder instead of carrying another local copy.

### Promotion

- Before acceptance accounting, assert `target_rows == draft_rows + 1` and `accepted <= proposed`.
- Keep one authoritative round-width / rollback-target producer.
- Phase-charge/accounting identity belongs in the round event stream; answer equivalence cannot detect accounting drift.
- Verifier cache codec/ceiling/geometry should come from one authoritative builder rather than per-loop copies.

No throughput target moves from these refactors.

---

# UPDATE — oMLX #3520 M3 Ultra reproduction strengthens the long-context QSA mechanism, not equivalence

Fresh owner testing on an **M3 Ultra 512 GiB** used Qwen3.8-Flash-Next-oQ4e-mtp, Code(Python) contexts, temperature 0, adaptive Lightning MTP through depth 3, caching disabled.

Single sequential cells, each shown as PP / TG:

| version | 16K | 128K | 200K |
|---|---:|---:|---:|
| main `94530d8d` | 829.0 / 61.0 | 753.8 / **49.6** | 723.1 / **46.4** |
| updated #3520 `9e19561b` | 835.7 / 62.1 | 757.1 / **59.2** | 722.3 / **50.1** |

The updated dispatch recovered the earlier prefill slowdown while retaining the long-context decode gain. A local split that forced the original gather on ordinary prefill reduced isolated prefill time but gave no clear server-level advantage over the updated dispatch; at 200K it saved only ~0.32 s TTFT in the reported run.

Quality/equivalence evidence is deliberately bounded:

- dense versus gathered with fixed MTP depth 3 and a shared 32K code background measured MMLU 877/1000 vs 880/1000 and HumanEval 159/164 vs 158/164;
- neither score difference was significant in the report;
- **greedy dense and gathered outputs are nevertheless not equivalent**: repeated gathered runs were deterministic, but dense/gathered diverged at token 225, and replay against cloned KV caches reproduced the argmax difference.

### Promotion

- The M3 Ultra reproduction strengthens the gathered-QSA long-context mechanism case and the updated prefill dispatch.
- Do not call gathered attention bit-equivalent to dense attention.
- Maintain route-local determinism plus quality gates separately from exact-equivalence gates.
- Any custom split-K path that claims equivalence should state **equivalent to which baseline**: gathered or dense.

No numeric transfer from M3 Ultra to M1 Max PP2.

---

# FRESH — oMLX #3539: sufficient prompt length but zero recurrent boundary snapshots

Fresh issue created **2026-09-09 10:03:43 UTC** on M3 Max 128 GB / oMLX 0.6.4 / MLX 0.32.2 / Qwen3.8-27B-oQ4e-mtp.

With `block_size=4096`, a 9,890-token prompt should cross 4,096 and 8,192, but the scheduler reports:

- `reason=boundary_snapshot_unavailable`;
- `tokens=9890`;
- `available_boundaries=0`.

The boundary-snapshot directory remains empty while the GDN sidecar and ordinary hot cache contain data. Persistent SSD reuse after restart therefore does not engage.

The same request still shows healthy MTP activity — e.g. one 256-token request completed at 17.4 TG with MTP depth-3 acceptance 177/193 (91.7%) — so speculative decode activity alone is not evidence that reusable boundary state is materialized.

Root cause is **not established** by the issue and should remain open rather than inferred from the reporter's suggestions.

### Promotion

- A cacheability cell must verify the actual list/count of materialized boundary IDs, not merely prompt length and cache configuration.
- Add `>=2 block boundaries -> store -> restart -> exact prefix reuse` to warm-cache certification.
- `available_boundaries=0` after sufficient executed tokens is a hard failure even if GDN sidecars or ordinary KV files exist.
- Preserve the current fail-closed behavior: skipping the store is preferable to serializing live non-sliceable recurrent state and poisoning future hits.

---

# FRESH — vLLM #56037 strengthens mixed-concurrency / tail-ring / long-soak fault attribution

A fresh ROCm GLM-5.3-Flash report separates three memory-fault shapes that had previously risked being collapsed into one explanation.

### Crash C — mixed-length MTP decode

One long ~130K request was joined by two short MTP requests. The scheduler dump is measured; the exact dying kernel is inferred, not HIP-captured. A local per-request split overlay replayed the shape without a fault, but this does **not** prove the inferred kernel identity.

### Crash D — chunked prefill tail seed

This path was measured with `HIP_LAUNCH_BLOCKING`: `_kpool_tail_seed_kernel` could use a main-KV-scale block id against a much smaller per-request tail ring without checking `blk < tail.shape[0]`. A `NUM_TAIL_BLOCKS` guard fixes the direct probe and replay.

### Crash E — equal-length short B2 MTP after long soak

The patched image still faulted after **46.38 hours**. The dying scheduler dump had two equal short requests with computed lengths `[20, 20]`, each scheduling MTP tokens. The exact faulting kernel remains unmeasured because launches were asynchronous; the author explicitly declines to promote the equal-length fused-kernel hypothesis without a captured shader name.

### Promotion

Add distinct robustness cells rather than one generic concurrency stress:

1. B3 mixed long+short MTP join after the long request has accumulated substantial state;
2. chunked prefill whose tail is not aligned to the kpool factor;
3. equal-length short B2 first-token MTP;
4. prolonged serving soak after all short semantic tests pass.

Keep local tail-ring IDs/ranges distinct from main-KV physical IDs, and treat a scheduler dump as scheduler evidence rather than proof of the asynchronous kernel that faulted.

This is ROCm/GLM evidence only; it changes qualification structure, not Apple or RTX target rates.

---

# SCREENED / no target movement

- jundot/oMLX main: no post-cutoff main commit; the material items are fresh issue/comment evidence above.
- antirez/ds4: no post-cutoff main commit.
- llama.cpp upstream post-cutoff commits screened were unrelated to our target mechanisms.
- vLLM main post-cutoff commits did not provide a new exact target-lane rate; the material item is #56037 fault attribution.
- Rapid-MLX post-cutoff work is model/share-compute product work, not target evidence.
- NInfer: no post-cutoff commit.
- vllm-mlx: no post-cutoff commit.
- TurboQuant-MLX: no post-cutoff commit.
- no fresh exact **2x M1 Max64/TB4** Flash or DS4 sustained TG/cold-PP receipt surfaced;
- no fresh exact **M1 Max64** mature Qwen3.8-27B target-configuration receipt surfaced;
- no fresh exact **RTX 5070 Ti fully-resident Q3_K_XL** target-lane receipt surfaced. The new 5070 result is the separate IQ4_XS hot/cold capacity lane.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Add or strengthen these cells in the current qualification order:

1. exact PP2 model/recurrent/QSA identity + distributed lifecycle;
2. cold PP with real chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase first speculative decode joining continuing chunked prefill;
4. speculative ownership / rollback / replay with one authoritative committed frontier;
5. one authoritative round-width / rollback-target / phase-charge interpretation;
6. verifier acceptance-shape invariant: proposals plus exactly one correction/bonus row;
7. bound verifier capture to the drafter-readable horizon;
8. admission-time paged-boundary alignment, including short-prompt first-boundary-during-decode;
9. **actual boundary materialization + restart reuse**, not merely cache-enabled configuration;
10. recurrent checkpoint retention across branch/edit/retry/compaction/reopen;
11. rendered-history cacheability for reasoning/tool calls, stream/nonstream parity;
12. native/default MTP whole-round baseline;
13. explicit drafter-head binding + trained MTP/NextN count + requested/resolved depth;
14. distinct owner tickets/counters for capture, hidden-store interval and other state epochs;
15. **B2 admission-interleaving cell: A capture -> admit B -> A first propose**;
16. workload-separated deeper-depth A/Bs + segmented long-generation acceptance/TG;
17. configured / armed / executed provenance for conditional accelerators;
18. realized QSA route for draft, target decode and target verify;
19. extension/build/admission receipt + row/verify-width x context route matrix;
20. selected-KV traffic/work accounting; no accidental dense materialization or TB4 movement;
21. dense-vs-gathered quality is separate from exact-equivalence certification;
22. custom split-K only after exact-build real-checkpoint transaction checks;
23. mixed long+short B3, equal-short B2 and non-aligned prefill-tail robustness cells;
24. long soak after short correctness passes;
25. stage-local GDN/routed-MoE/projection/sync profiling + SIMD occupancy;
26. quant/kernel chunk-width sweep;
27. combine only passing mechanisms, then rerun cluster cold PP, ~128K TG, append/live-prefix, branch/retry and coding-agent wall cells.

For PP2, selected K/V, recurrent state and QSA metadata stay stage-local. A sparse route that turns into dense TB4 traffic fails the intended economics.

Safe serving remains **profitable singleton MTP + plain concurrent work** until per-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

> B2/B3/B4 means physically simultaneously scheduled independent requests with correct persistent state. Configured/admitted/batched/queued slots do not count. Admission interleavings and staggered mixed prefill/decode are explicitly part of the definition.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

Keep the canonical fully-resident Q3_K_XL speed target unchanged.

Add a separate **IQ4_XS long-context capacity lane** based on the fresh exact-hardware study. Its qualification records hot/cold boundary, PCIe link, host pinning, tile width, VMM content epoch, transfer/convert/attention overlap, recurrent-state memory, output hash and integrated-vs-isolated rate.

Do not merge a host-backed 256K capacity rate into the 120-TG fully-resident short/medium planning target.

## Dual-M1 DS4-0731

No target movement. The vLLM ROCm failure shapes strengthen mixed-concurrency and tail-ring stress design but do not transfer rates.

---

# Standing decisions strengthened this pass

- Exact hardware alone is not enough to move a target when the model quantization / residency / workload lane differs from the target definition.
- Keep 5070 Ti fully-resident speed and host-backed long-context capacity as separate planning lanes.
- B1 identity can hide a severe concurrency-only speculative regression.
- Each semantic ownership epoch gets its own counter/ticket namespace.
- Configured, armed and executed are separate benchmark-provenance states.
- Host ownership metadata still does not prove device happens-before.
- Acceptance accounting refuses verifier blocks that are not proposals + one bonus/correction row.
- Phase/work attribution belongs in an auditable per-round stream.
- Boundary-cache qualification observes real materialized boundaries and restart reuse.
- Healthy MTP activity does not imply reusable recurrent snapshots exist.
- Gathered and dense attention can both be deterministic while producing different greedy outputs.
- Similar benchmark quality is not exact equivalence.
- Scheduler state is not asynchronous kernel identity; fault attribution states what was measured versus inferred.
- Mixed long+short, equal-short, non-aligned prefill-tail and long-soak cells are distinct robustness dimensions.
- Useful emitted tokens per wall-second remains the objective; acceptance is diagnostic.
- Cross-runtime/other-hardware gains remain mechanism evidence until exact target reproduction.
- No canonical target movement without evidence from the exact target lane or exceptional explicit justification.
- P69 remains isolated.
