# External runtime research watch — 2026-09-07 19:19 ET

Starting freshness boundary: `611b8bdf7c2ead7e67b66491debe7d9884c09464` / **2026-09-07 22:03:12 UTC**.

Classification: **material Flash-Next prefill optimization / experiment-order update; no target movement.**

Evidence classes are kept separate throughout this note:

- the new result is a **measured experimental A/B on one M3 Ultra 512 GB system**;
- for the planned 2x M1 Max 64 GB / TB4 appliance it is **transfer/mechanism evidence only**;
- it is not a sustained exact-target TG or cold-PP receipt;
- `RESEARCH-TARGETS.md` is intentionally unchanged.

No fresh sustained exact-target receipt surfaced for dual-M1 Flash, dual-M1 DS4-0731, single-M1-Max Qwen3.8-27B, RTX 5070 Ti Qwen3.8-27B, or RTX 5070 Ti Tiel Coder.

---

## FRESH / material experimental A/B

### antirez/ds4 #991 / `b85a6174da6d0ea3139b48194a2ca108097657b1` — block-parallel GDN convolution plus reusable prefill work gives a repeatable ~2.8–2.9% 8K gain over the already-enabled Q8-unpack baseline

Post-boundary commit authored **2026-09-07 22:05:55 UTC**, committed **22:06:23 UTC**.

The PR is the ds4 Qwen3.8-Flash-Next Metal branch. The fresh commit is narrower than the PR as a whole: it does **not** newly establish Flash-Next support, MTP support, or the older Q8-unpack baseline. Those predate this boundary. The fresh delta adds structural prefill reuse on top of that baseline.

Tested configuration:

- Apple **M3 Ultra, 512 GiB unified memory**;
- Qwen3.8-Flash-Next IQ2_XXS / padded-Q2_K-down experimental GGUF plus external Q4_1 PLE sidecar;
- resident weights;
- **MTP off**;
- single loaded engine;
- 1K and 8K chunk/prefix cases, including an independent code prompt and an 8K append after an 8K live prefix;
- explicit control `DS4_QWEN4_PREFILL_REUSE=0` versus candidate `=1`, while the pre-existing Q8-unpack path is enabled in both arms;
- alternating ABBA/BAAB, eight measured runs per arm per final scenario;
- throughput includes input staging and GPU preprocessing;
- every measured final vocabulary vector compared bit-for-bit.

The retained structural changes are:

1. **block-history GDN convolution** — snapshot each 64-token block's incoming history so blocks can run independently while preserving the old per-channel tap order, FP32 accumulation, SiLU and raw-input history semantics; only the final block commits final history;
2. **wider Q2_K routed-down tiles** at sufficiently large batches — reuse each decoded down-weight tile across more token columns while preserving K traversal and accumulation semantics;
3. bounded reusable scratch accounting rather than hidden transient memory.

Final full-model results over the already-enabled Q8-unpack control:

- 1K prose: **1173.5053 -> 1194.9359 tok/s (+1.8262%)**;
- 8K prose: **1300.4796 -> 1338.8000 tok/s (+2.9466%)**;
- independent 8K code: **1303.8942 -> 1340.0871 tok/s (+2.7758%)**;
- append 8K after an 8K prose prefix: **1284.8197 -> 1321.0206 tok/s (+2.8176%)**.

All 64 measured final vocabulary rows / **15,892,480 floats** matched bit-for-bit. A final integrated-main 8K ABBA/BAAB also measured **1301.9296 -> 1338.8552 tok/s (+2.8362%)** with exact compared vocabulary rows.

The fresh commit explicitly reports that its requested **5% target was not reached**. Keep the smaller measured result; do not inflate it by stacking percentages from separately measured baselines.

### Useful negative-result mining from the same controlled experiment

The experiment also tested higher-complexity candidates and retained the failures rather than censoring them:

- unpack IQ2 gate/up once into FP16: **-6.95% at 8K**;
- pack routed inputs once into FP16 tiles: **-19.70% at 8K**;
- 64-token gate/up + down tiles: only **+0.74%**; gate/up alone **-0.09%**, down alone **+0.74%**;
- fully parallel convolution with a full raw-input snapshot: **+1.53%**;
- smaller block-history snapshot superseded it at **+2.10%** in screening.

The pre-existing Q8-unpack baseline itself is pre-boundary evidence: on this M3 Ultra configuration it had measured roughly **+1.4–1.8% at 8K** by decoding eligible Q8 projections once into reusable FP16 scratch. That older result is **BACKFILL/KNOWN context**, not a fresh gain from this pass.

### Evidence boundary

This is strong evidence for **candidate ordering and mechanism**, not a transferable M1 rate:

- M3 Ultra 512 GB is not M1 Max 64 GB;
- it is single-node, not PP2/TB4;
- it is no-MTP prefill, not decode or speculative economics;
- it uses a specific experimental quant/layout;
- final-vocabulary bit identity is strong but does not prove all intermediate states or general model accuracy.

Therefore it does **not** move the dual-M1 Flash cold-PP target or confidence ladder.

---

## Promotion for the dual-M1 Flash-Next prefill plan

After the exact semantic/layout baseline and PP2 stage ownership are frozen, add a **stage-local prefill-structure A/B** rather than immediately pursuing more invasive weight/input repacking.

For each PP stage separately:

1. profile GDN convolution preparation/execution and routed-MoE down/gate/up attribution at realistic chunk sizes;
2. if the stage shows the same repeated-work shape, test block-history convolution with exact incoming/final recurrent-state identity;
3. test reusable per-invocation quantized-weight decode/unpack only where the chosen M1 quant/layout actually repeats decode work across token tiles;
4. test wider routed-down tiles independently from gate/up widening;
5. record additional steady scratch, transient growth overlap, wired residency and actual stage-local memory headroom;
6. retain an explicit kill switch/control for every candidate;
7. certify unequal chunk tails, append after a live prefix and PP2 cross-stage frontier/state identity;
8. only then combine passing mechanisms and measure **cold cluster PP including TB4 bubbles/traffic**.

Candidate priority from the external evidence is now:

- **higher priority:** block-history GDN convolution / equivalent stage-local recurrence parallelization;
- **conditional:** one-time Q8/quantized projection unpack when profiling proves repeated decode work and scratch fits;
- **conditional:** wider routed-down tiles at large chunks;
- **lower priority unless M1 profiling overturns it:** broad gate/up unpack or routed-input prepacking, which were materially negative on the measured M3 Ultra experiment.

Do not copy the M3 percentages into the M1 forecast. The portable result is the **shape of repeated work and the negative-candidate ordering**.

---

## Screened post-boundary items that do not promote

### oMLX #3469 — KNOWN, no substantive post-boundary delta

The PR's substantial M5 Max host-dispatch / fused-hyperconnection measurements predate this boundary. Its post-boundary update was a non-technical user comment. Do not relabel the older benchmark as fresh.

### Rapid-MLX #3156 — BACKFILL/KNOWN; post-boundary closure is procedural

The underlying M2 Max Qwen3.8-27B observation predates this boundary: one Rapid-MLX MTP path measured **18.1 tok/s versus 20.9 tok/s plain**, while a different MTPLX path on the same architecture showed usable draft acceptance and a large positive MTP result. The only post-boundary event is a Mergify bot closure with no explanatory comment or linked resolution.

Treat the old numbers as mechanism/backfill evidence that **acceptance alone does not determine MTP profitability on Apple**. They do not alter P69, and the closure itself is not an UPDATE.

### NInfer #188 — post-boundary comments are not an exact 5070-Ti receipt

The high Qwen3.8-27B DFlash2/NVFP4 numbers in the issue body and substantive NVIDIA-user measurements predate this boundary. Fresh comments concern artifact size / cross-model draft-weight compatibility and do not establish an exact RTX 5070 Ti production lane. No target movement.

### rMLX / llama.cpp / vLLM targeted scans

No post-boundary item established a new exact dual-M1 Flash TG/PP receipt, exact M1-Max64 27B receipt, exact RTX5070Ti16 27B receipt, or exact dual-M1 DS4-0731 sustained TG receipt.

---

# Exact-rig no-change confirmation

Canonical planning centers remain:

| Lane | TG | Cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64/TB4 | **40** | **400** |
| Qwen3.8-27B — M1 Max64 | **25** | **110 native/exact-runtime** |
| Qwen3.8-27B — RTX5070Ti16 | **120** | **250** |
| DS4-0731 — 2x M1 Max64/TB4 | **15** | **180** |

These remain **planning targets, not measurements**.

`RESEARCH-TARGETS.md` stays untouched.

---

# Current project consequences

## Dual-M1 Flash-Next

PP2/layer ownership remains the primary architecture; TP2 remains a control. The 15:10 + 17:53 correctness/certification order is unchanged except for one prefill optimization refinement:

- once the exact PP2 semantic baseline, recurrent state ownership, QSA oracle and cold-PP measurement harness are trustworthy, profile and A/B **stage-local block-history GDN convolution / repeated quantized-weight work** before attempting broad repacking;
- preserve exact stage-local recurrent state and PP frontier identity;
- evaluate the optimization at realistic cold chunks and in append/live-prefix shapes;
- cluster promotion requires measured end-to-end cold PP with actual TB4 traffic, not summed single-stage kernel gains.

MTP ordering is unchanged: replay semantics first, actual-resolved depth provenance, then deeper-depth A/Bs, with tape/refold orthogonal and after the replay baseline.

Safe serving remains **profitable singleton MTP + plain concurrent work** until multi-slot state isolation, physical recurrent capacity and PP+MTP distributed ownership are certified.

## Single M1 Max64 Qwen3.8-27B

No change. **P69B12 remains frozen/promoted; P69B13 remains next from existing profiling only.** Do not import external M2/M3 serving A/Bs into the frozen verifier campaign.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target or experiment-order change from this pass.

## Dual-M1 DS4-0731

No target movement. PR #991 is useful Flash-Next Metal mining evidence, not a DS4-0731 throughput receipt.

---

# Standing decisions strengthened this pass

- Controlled negative experiments are first-class mining evidence; do not retry broad repacking simply because it sounds theoretically attractive.
- Repeated-work elimination is promoted only when profiling proves the repetition exists in the exact quant/layout/backend.
- Scratch used to save decode/unpack work is part of admission and residency accounting.
- Prefill optimizations must preserve recurrent history/frontier semantics in append as well as cold-prefix cases.
- Single-node prefill gains do not become PP2 cluster gains until TB4 bubbles/traffic and stage balance are measured.
- Cross-generation Apple percentages remain transfer evidence, never exact M1 target measurements.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
