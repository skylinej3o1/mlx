# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence. Do not reconstruct targets from watch-note prose.**

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-09-0628.md`

   **The 06:28 note is authoritative for the fresh exact-RTX5070Ti IQ4_XS 256K hot/cold-KV capacity runtime, Atlas concurrency-only MTP ownership/counter regression, rMLX single-source speculative round/acceptance invariants, the M3-Ultra #3520 reproduction and dense-vs-gathered non-equivalence, oMLX recurrent-boundary materialization failure, and vLLM mixed-concurrency/tail-ring/long-soak fault attribution. It moves no canonical performance target.**

4. Retain the immediately previous deltas:

   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1813.md` — corrected extension-built oMLX #3520 long-context QSA matrix and width-dependent routing, independent indexed split-K numerical/performance evidence, Affine4 long-context capacity evidence and DSv4/DSpark drafter-head/native-depth provenance;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1438.md` — gathered-QSA mechanism promotion, short-prompt MTP paged-boundary admission fix and device-upload happens-before correction. **Its #3520 percentages are superseded by the 18:13 correction; the mechanism findings stand.**
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-1048.md` — Apple IQ3 small-width SIMD-utilization A/B, recurrent checkpoint retention / warm-rewind fix, DFlash2 cumulative-OOB attribution correction and recovered M1-Max Qwen3.8-27B baseline;
   - `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-08-0843.md` — landed oMLX distributed lifecycle work, rMLX bounded speculative capture / commit-scoped conditioning, mixed-phase recurrent+MTP ordering bug, QSA TopK monitor, backend-context placement and MTP-depth backfill;
   - retain the remaining 2026-09-08, 2026-09-07, 2026-09-06 and 2026-09-05 deltas for GDN/projection structure, recurrent rollback/state geometry, scheduler occupancy, whole-round speculative economics, cache lifecycle, sampler ownership, request-row ownership and benchmark-provenance gates.

5. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain the dated deltas newer than that point when reconstructing the evidence chain.

6. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 06:28 pass moves no row.** The new RTX 5070 Ti measurement is exact hardware but a different quantization/residency/workload lane: `UD-IQ4_XS` with a host-backed long-context KV ring. The canonical 120-TG speed target remains defined around a fully-resident Q3_K_XL/native-MTP configuration.

---

# Current newest evidence delta — 2026-09-09 06:28 ET

Starting freshness boundary: `3692caf919864cc3a74c49da6eb6f0c92b55ac85` / **2026-09-08 22:21:02 UTC**.

## FRESH / exact RTX 5070 Ti long-context capacity lane

Public `BrunoPPassini/llama.cpp` branch `qwen38-blackwell-256k` landed after the cutoff, beginning with `1a63cbf1220714f7a20a6f139a603f0ccada5a59`.

Exact hardware: RTX 5070 Ti 16 GB, PCIe 5 x16, Ryzen 9800X3D / 48 GiB DDR5-6400, Qwen3.8-27B `UD-IQ4_XS`, Q4 target/draft KV, deterministic native MTP3.

Measured optimized endpoints:

- short/GPU-resident controlled path: **82.34 TG**, but the report explicitly separates a **71.16 TG integrated daily reference**;
- 87,160 input + 64 output: **1104.85 PP / 41.53 TG**;
- 256,257 input + 64 output: **698.84 PP / 23.97 TG**.

The design keeps 65,536 tokens hot in VRAM and uses pinned host RAM as cold KV capacity, staging 8,192-token tiles over PCIe with copy/convert/attention overlap. It also compresses recurrent-state lifetime via transaction-log / phase-arena ownership rather than duplicating full speculative state planes.

**Promotion:** add a separate 5070 Ti IQ4_XS long-context capacity lane with explicit hot/cold boundary, VMM content epoch, PCIe/link/staging provenance, output-hash/MTP-counter qualification, and integrated-vs-isolated rate separation. Do not merge these rates into the fully-resident Q3_K_XL 120-TG speed target.

## FRESH / Atlas #968 — C1-clean, C2-broken speculative ownership

Atlas `fdc912b108ccf7f83dc5283e75b44148f87e15a5` hardens cross-turn MTP carry/session and hidden-interval ownership.

A new ownership ticket was initially drawn from the existing capture-generation counter. Interleaved admissions then advanced that counter between another sequence's capture and first propose, silently disabling drafter prefill.

Measured:

- C1: **18.5 -> 18.5**;
- C2: **30.8 -> 23.7**, repeat **23.4** (~24% regression);
- C2 TPOT: roughly **62 -> 79 ms**.

The fixed design uses a separate ticket dispenser and passes its concurrency gates. Accuracy stayed unchanged, which is expected for a lossless speculative acceptance/performance defect.

**Promotion:** semantic ownership epochs get distinct counters; B2 includes `A capture -> admit B -> A first propose`; C1 identity cannot certify concurrent speculative state; configured/armed/executed are separate provenance states. Host ownership stamps still do not prove device happens-before.

## FRESH / rMLX #549 + #550 — one speculative arithmetic/accounting contract

`9567876605f14cd2b2090689d80000c469c7499e` centralizes round-block sizing and rollback targets, adds a round-stream oracle and pins phase-charge attribution so rollback and reported phase accounting cannot silently diverge.

`28dc628426acb65f2b56c2ee742faca873e00179` unifies DFlash/EAGLE-3 acceptance and refuses malformed verified blocks unless:

`target rows = proposed rows + 1 correction/bonus row`.

Verifier codec/context ceiling/cache-stack construction also has one producer.

**Promotion:** assert proposal/bonus shape and `accepted <= proposed`; keep one authoritative round-width/rollback/phase-charge interpretation; answer equivalence is insufficient to certify work attribution.

## UPDATE / oMLX #3520 M3-Ultra reproduction

Fresh owner testing on M3 Ultra 512 GiB, Flash-Next-oQ4e-mtp, temperature 0, adaptive Lightning MTP depth <=3, caching disabled:

- 128K main **753.8 PP / 49.6 TG** -> updated PR **757.1 / 59.2**;
- 200K main **723.1 / 46.4** -> updated PR **722.3 / 50.1**.

The updated dispatch recovers the previous prefill regression while retaining long-context decode benefit.

Quality tests showed no clear aggregate regression, but exact equivalence is false: repeated gathered runs were deterministic while dense and gathered greedy outputs diverged at token 225, reproduced from cloned KV caches.

**Promotion:** route-local determinism and quality are separate from dense-equivalence; a custom sparse path must name the exact baseline it claims to match.

## FRESH / oMLX #3539 — boundary state not materialized despite crossing blocks

M3 Max 128 GB / Qwen3.8-27B-oQ4e-mtp, block size 4096. A 9,890-token prompt crosses two expected block boundaries but reports `available_boundaries=0` / `boundary_snapshot_unavailable`; persistent boundary snapshots remain absent while other cache artifacts exist.

MTP itself is healthy in the request (one reported depth-3 cell accepts 177/193 drafts), proving that speculative execution does not imply reusable recurrent boundary state exists.

**Promotion:** certify the actual materialized boundary IDs/count and `store -> restart -> prefix reuse`, not just prompt length or cache-enabled configuration. Preserve fail-closed behavior rather than storing non-sliceable live recurrent state.

## FRESH / vLLM #56037 — separate mixed-MTP, tail-seed and long-soak fault shapes

Fresh ROCm GLM-5.3-Flash evidence separates:

- mixed long+short MTP decode failure — scheduler shape measured, exact kernel inferred;
- chunked-prefill tail-seed failure — `_kpool_tail_seed_kernel` measured and missing local tail-ring bounds;
- equal-short B2 MTP failure after **46.38 h** — scheduler shape measured, exact asynchronous kernel still unproven.

**Promotion:** mixed long+short B3, non-aligned chunked-prefill tail, equal-short B2 first-token MTP and long serving soak are distinct robustness cells. Scheduler dumps are not asynchronous kernel identity; mark measured vs inferred producer explicitly.

## SCREENED / no-change

- oMLX main: no post-cutoff main commit.
- antirez/ds4: no post-cutoff main commit.
- NInfer, vllm-mlx and TurboQuant-MLX: no post-cutoff commits.
- Rapid-MLX changes are product/share-compute/model work, not target evidence.
- llama.cpp upstream changes screened were unrelated to target mechanisms.
- vLLM main commits did not add a stronger exact target-lane rate.
- no fresh exact 2x M1 Max64/TB4 Flash or DS4 receipt;
- no fresh exact M1 Max64 mature Qwen3.8-27B receipt;
- no fresh exact fully-resident Q3_K_XL RTX 5070 Ti receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary and TP2 as control**.

Current qualification additions/strengthening:

1. exact PP2 model/recurrent/QSA identity + distributed lifecycle;
2. cold PP with real chunking, stage balance and TB4 traffic/bubbles;
3. mixed-phase first speculative decode joining continuing chunked prefill;
4. speculative ownership / rollback / replay with one authoritative committed frontier;
5. one authoritative round-width / rollback-target / phase-charge contract;
6. verifier acceptance shape = proposals + one bonus/correction row;
7. verifier capture bounded to drafter-readable horizon;
8. admission-time paged-boundary alignment;
9. actual boundary materialization + restart reuse;
10. recurrent checkpoint retention across branch/edit/retry/compaction/reopen;
11. rendered-history cacheability and stream/nonstream parity;
12. native/default MTP whole-round baseline;
13. explicit drafter-head binding + native MTP/NextN count + requested/resolved depth;
14. distinct counter/ticket namespace per state ownership meaning;
15. B2 `A capture -> admit B -> A first propose` interleaving;
16. configured / armed / executed feature provenance;
17. workload-separated deeper-depth A/Bs + segmented long-generation TG/acceptance;
18. realized QSA route for draft, target decode and target verify;
19. extension/build/admission + row/verify-width x context route matrix;
20. selected-KV traffic/work accounting with no accidental dense TB4 materialization;
21. dense-vs-gathered quality separate from exact equivalence;
22. custom split-K only after exact-build real-checkpoint transaction checks;
23. mixed long+short B3, equal-short B2 and non-aligned prefill-tail stress;
24. long soak after short semantic qualification;
25. stage-local GDN/routed-MoE/projection/sync + SIMD profiling;
26. quant/kernel chunk-width sweep;
27. combine passing mechanisms and rerun cluster cold PP, ~128K TG, append/live-prefix, branch/retry and coding-agent wall.

For PP2, selected K/V plus recurrent/QSA state stay stage-local. Sparse attention that becomes dense TB4 traffic fails the intended economics.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

> B2/B3/B4 means physically simultaneously scheduled independent requests with correct persistent state. Configured/admitted/batched/queued slots do not count; admission interleavings and staggered mixed prefill/decode are part of the definition.

## Single M1 Max64 Qwen3.8-27B

No target movement.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.** Do not reopen P69B8, P69B9 or P69B10-C.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel Coder

Keep the canonical fully-resident Q3_K_XL speed target unchanged.

Add a separate IQ4_XS **long-context capacity lane** based on the exact-hardware 256K study. Report hot/cold boundary, PCIe/link state, pinned-host memory, VMM content epoch, tile width, copy/convert/attention overlap, recurrent-state memory, output hash and integrated-vs-isolated rate.

## Dual-M1 DS4-0731

No target movement. The fresh ROCm failure shapes strengthen concurrency/tail-ring/soak certification only.

---

# Standing decisions strengthened this pass

- Exact hardware does not automatically move a target if quantization/residency/workload differs from the target lane.
- Keep RTX 5070 Ti fully-resident speed and host-backed long-context capacity separate.
- C1 identity can hide severe concurrent speculative regressions.
- Distinct state ownership meanings use distinct counters/ticket namespaces.
- Configured, armed and executed are separate benchmark provenance.
- Host ownership metadata does not prove device completion/order.
- Acceptance refuses verified blocks not equal to proposals + one bonus/correction row.
- Per-round work attribution is an auditable correctness dimension.
- Boundary reuse is certified by actual materialization and restart recovery.
- Healthy MTP does not prove reusable recurrent snapshots exist.
- Dense and gathered attention may both be deterministic without being equivalent.
- Aggregate quality similarity is not bit/token equivalence.
- Scheduler evidence is not asynchronous kernel identity.
- Mixed-long/short, equal-short, non-aligned-prefill-tail and long-soak are separate robustness cells.
- Acceptance is diagnostic; useful emitted tokens per wall-second is the objective.
- Cross-runtime/other-hardware gains remain mechanism evidence until exact target-lane reproduction.
- No canonical target movement without exact target-lane evidence or exceptional explicit justification.
- P69 remains isolated.
