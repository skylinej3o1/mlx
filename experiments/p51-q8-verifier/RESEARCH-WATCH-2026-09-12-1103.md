# Research watch — 2026-09-12 11:03 ET

## Scope and freshness

This pass starts from the prior hard boundary `2026-09-12 07:13:21 UTC` and includes substantive source activity through the user's request cutoff:

**`2026-09-12 15:03:42 UTC`**.

Evidence timestamp means the underlying source/measurement/update time, not crawler time, search rediscovery, fork pushes or rebases.

Active lanes remain:

- Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4;
- Qwen3.8-27B — one M1 Max 64 GB;
- Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM;
- DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4;
- Blazer / custom ~5.x-BPW execution work where mechanisms are portable.

No canonical target moves in this pass. P69 remains isolated: **P69B12 stays frozen/promoted; P69B13 remains next from the existing measured high-leverage GDN/projection/downstream-tail structure.** Do not reopen P69B8/B9/B10-C.

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s** | planning / calibration target |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | planning / calibration target |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | planning / calibration target |

---

# Fresh new evidence

## 1. oMLX #3607 — DeepSeek V4.1 CED prefill with bounded SWA replay

**FRESH NEW / APPLE PREFILL-ARCHITECTURE TRANSFER. Not an exact DS4-0731 result and not an active dual-M1 receipt.**

PR #3607 was created and merged inside this search window. The implementation makes DeepSeek V4.1 prefill asymmetric across the encoder/decoder split:

- decoder-half layers 21–39 run attention + MoE only over the trailing sliding-window tokens;
- global decoder KV is obtained by projecting the full encoder-final hidden state through the midpoint CSA2 layer;
- chunked prefill uses an absolute gate and clears/rebuilds the stale decoder window so final cache state is determined by the trailing window;
- decode and DSpark verify blocks remain outside the CED path;
- layout capability is validated explicitly and unsupported layouts auto-disable;
- follow-up commits in the same window preserve CED state across reload/cache planning and add the per-model feature toggle.

Reported Apple measurement from the PR:

- Mac Studio **M3 Ultra 512 GB**;
- `DeepSeek-V4.1-Flash-oQ4e-mtp`;
- cold prefill, ~21.4K-token prompt;
- CED off: **50.19 s / ~430 tok/s**;
- CED on: **30.55 s / ~700 tok/s**;
- approximately **+63% prefill throughput**;
- DSpark acceptance stayed in the same stated range (~71–73%); decode/speculative path itself was not changed.

Correctness coverage includes CED-off regression, layout validation, encoder + midpoint global-KV parity, deterministic behavior, inactive-within-window full-compute parity, chunked-vs-single CED equality plus decode seam, and DSpark ring-gap replacement.

### Durable project promotion

For any split-phase or bounded-window prefill optimization, execution identity must now include:

1. encoder/decoder phase ownership;
2. full-context state/KV source;
3. trailing-window forward scope;
4. replay/reconstruction window size;
5. chunk-boundary stale-state invalidation;
6. replay source and state boundary;
7. chunked-vs-single/unchunked parity;
8. decode/speculative exclusion or inclusion explicitly;
9. reload/cache-planner persistence of the feature state;
10. actual executed path, not merely configured eligibility.

This is also a useful architectural pattern for Flash-Next research: if a later phase can derive required global state from a full-context boundary while only forwarding a bounded local tail, compute can potentially be removed without weakening the global-state source. That is a **mechanism hypothesis only** until demonstrated on Qwen3.8-Flash-Next.

No DS4 target move: V4.1 is a materially different model/runtime lineage and the measurement is on M3 Ultra 512 GB.

---

## 2. antirez/ds4 `bd66c402` — DeepSeek V4.1 Flash Metal support

**FRESH NEW / APPLE MODEL-LINEAGE IMPLEMENTATION TRANSFER. Not an exact DS4-0731 performance receipt.**

Commit `bd66c402070042bf0a79ad6ece8242de4c93680c` landed at `2026-09-12 09:47:54 UTC` with DeepSeek V4.1 Flash support for Metal.

The change is substantial rather than a metadata-only declaration: it adds V4.1-specific graph/test coverage, Engram support, Metal execution tests, prefill tests, CLI/model plumbing, GGUF support, and additional TP/command-memory tests.

Current project documentation at that commit states:

- V4.1 text and vision are Metal-supported;
- V4.1 uses its own GGUF/tokenizer/inference graph and is **not interchangeable** with V4 Flash 0731 weights or DSpark support files;
- Q2 artifact: 341 GiB total file / ~152 GiB main weights, including 189 GiB Engram tables read from disk on demand;
- one 128 GB Mac uses SSD streaming;
- two 128 GB Macs can run resident TP/RDMA at about 81 GiB main weights per rank;
- full residency was tested on an M3 Ultra 512 GB;
- Q4 requires substantially more memory and does not fit resident across two 128 GB Macs;
- DSpark is not currently implemented for V4.1 in this ds4 path.

### Project consequence

This is valuable source-level Apple transfer for:

- Engram-on-disk ownership and lookup;
- resident vs SSD-streamed expert capacity;
- two-Mac ownership-aware TP/RDMA;
- V4.1 graph differences and model-family separation;
- command-memory and cancellation testing;
- prefill batching under resident/streamed modes.

But it **does not move DS4-0731 targets**. Our active dual-M1 64 GB lane has a different checkpoint/topology, and the new V4.1 artifact itself is far outside resident capacity for two 64 GB machines.

---

## 3. vLLM #56562 merge — device-resident DSV4.1 metadata preparation

**POST-BOUNDARY MERGE / MECHANISM TRANSFER. The PR itself predates the prior boundary, so its benchmark numbers are not reclassified as fresh measurements.**

PR #56562 merged at `2026-09-12 14:20:04 UTC`. It replaces chains of per-step PyTorch metadata operations with Triton kernels that write directly into existing buffers for DSV4.1 token-to-request and flattened indexer metadata.

The key correctness lesson is more important to this project than the CUDA-specific implementation:

- DSpark adaptive verification can make CPU-side request boundaries stale;
- metadata therefore has to be derived from the **device-side authoritative boundaries**;
- graph replay was explicitly tested with changed device boundaries and stale CPU boundaries;
- all metadata-builder baseline tensors matched exactly in the focused validation.

The PR reports large metadata-only microbenchmark reductions and lower batch-1 TPOT, but those numbers are GB200/CUDA transfer evidence and are not promoted as active-lane speed receipts.

### Durable project promotion

For speculative/distributed Flash work, metadata provenance should explicitly include:

`logical request state -> authoritative device boundary -> derived token/request/indexer metadata -> graph-captured metadata route -> executed verifier/draft route`.

A host-side boundary being logically recent is not sufficient if adaptive speculative execution can advance device state independently.

This fits our existing logical-vs-physical execution-shape and pointer-freshness rules and should be checked when Flash PP2/MTP metadata crosses stages.

---

# Fresh-screen results / non-promotions

## vLLM

- No newly created post-boundary Qwen3.8-Flash-Next or Qwen3.8-27B receipt on our active M1/5070Ti topologies was found.
- #56562 merged during the window and is retained as current-runtime metadata/provenance evidence, not a newly fresh benchmark.
- Previously recorded #56577 FP8 proposal-head A/B, #56572 speculative-verifier peak profiling, #56568 shared-expert padding/fusion, #56550 SM120 physical NVFP4-KV identity, and earlier QSA/DFlash correctness items remain prior-pass evidence; they were not made fresh by search resurfacing.
- Fresh unrelated CUDA/XPU/serving commits were screened and not promoted.

## oMLX

- #3607 is the substantive new Apple inference change in this window.
- No new exact M1 Max 64 GB Qwen3.8-27B or dual-M1 Flash-Next performance receipt was found after the prior boundary.
- Older M1/M2 DFlash2 benchmarks remain retained evidence only; search/crawl time does not reset their evidence timestamp.

## antirez/ds4

- Unlike the previous pass, there is genuine new activity: `bd66c402` adds V4.1 Flash Metal support.
- It is retained as V4.1/Apple lineage transfer, not DS4-0731 target evidence.

## llama.cpp

- Post-boundary commits were screened through the request cutoff.
- No new Metal/Qwen3.8/DS4 active-lane throughput or correctness receipt was found; surfaced commits were primarily UI/server/other-platform work.

## Community / Hugging Face / Reddit

- Searches resurfaced older M1/M2 DFlash2 and Flash-Next material but no source-time post-boundary exact active-lane receipt strong enough to promote.
- Crawled-today pages are not treated as newly measured evidence.

---

# Consequences by active lane

## Dual-M1 Flash-Next

No target move. Keep PP2/layer ownership primary and TP2 as control.

Add two explicit research questions to the existing Flash certification plan:

1. **Can any Flash phase use a CED-like split:** retain a full-context authoritative state/KV source while forwarding only a bounded trailing portion through later expensive work?
2. **Is speculative/indexer metadata derived from authoritative device/stage state**, or can host/stage boundaries become stale under MTP/adaptive execution?

P69-derived verifier work remains a promising source of techniques, but **P69 itself is unchanged by this research pass**.

## Qwen3.8-27B M1 Max64

No target move. DFlash2 remains a challenger to the tuned Lightning-MTP/P69 incumbent, not an assumed successor. Existing FP16 and W4/A32 draft experiments remain valid candidates, but no fresh post-boundary receipt changes their expected ranking.

## RTX5070Ti16

No target move. Keep physical KV-format provenance and target/draft/proposal/verifier precision planes separate.

## DS4-0731 dual M1 Max64/TB4

No target move. The two fresh V4.1 developments are useful implementation/mechanism transfer only:

- oMLX CED supplies a concrete bounded-replay prefill pattern;
- ds4 now supplies fresh V4.1 Metal/Engram/streaming/TP source material.

Neither reproduces 0731 on two 64 GB M1 Max machines.

---

# Standing rules reinforced by this pass

- Exact-target receipt, transfer/mechanism evidence, experimental A/B and planning target stay separate.
- Evidence timestamp is the substantive source timestamp, not rediscovery or merge/rebase noise.
- Requested/configured state does not prove executed state.
- For split-phase prefill, record the authoritative full-context state source and the bounded local-forward/replay scope separately.
- For speculative metadata, record whether host or device state is authoritative and prove graph replay sees fresh boundaries.
- Chunked-vs-single/unchunked parity is mandatory when a bounded-replay optimization changes state construction.
- Model-lineage similarity is not topology equivalence: V4.1 evidence does not move DS4-0731 targets without direct reproduction.
- **P69 remains isolated: P69B12 frozen/promoted; P69B13 next from existing measured structure only.**

## Next hard freshness boundary

**`2026-09-12 15:03:42 UTC`**
