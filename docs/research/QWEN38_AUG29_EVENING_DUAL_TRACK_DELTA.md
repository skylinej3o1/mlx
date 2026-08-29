# Qwen3.8 Aug-29 evening dual-track delta

Status: **fresh field evidence / implementation guidance**

Updated: 2026-08-29 evening ET.

This note records the Aug-29 sweep across both active tracks:

1. Qwen3.8-Flash-Next on Apple / oMLX;
2. Qwen3.8-27B exact verifier/MTP tuning and the Layr challenge.

The most important net change is asymmetric: Flash-Next gained several strong practical Apple runtime results, while the 27B challenge supplied useful negative controls that strengthen rather than loosen the current P69 experimental discipline.

---

## 1. Flash-Next: M1/M2 FP16 leaf recast is a real generation-specific lever

Source:
- https://github.com/jundot/omlx/pull/3277

M1/M2 Apple GPUs do not have the same native BF16 execution support as newer generations. PR #3277 therefore recasts only BF16 leaves after model load to FP16 while leaving quantized U32 weight payloads unchanged.

Reported Flash-Next model conversion:

- 2,725 BF16 tensors / 15.41 GB recast;
- 1,020 quantized U32 tensors / 90.88 GB left untouched;
- same 16-bit storage width, so no material model-memory growth;
- load conversion cost about 0.6 s in the reported run.

Reported M1 Ultra 128GB measurements on `Qwen3.8-Flash-Next-oQ4e-mtp`:

- rewrite decode: 28.29 -> 32.26 tok/s, about +14.0%;
- novel decode: 22.89 -> 24.07 tok/s, about +5.2%;
- prefill: 313.2 -> 500.2 tok/s, about +59.7%;
- per-cycle cost fell about 9%; MTP acceptance was roughly flat.

Correctness caveat: FP16 and BF16 round differently, so this is not a bit-identical trajectory path. It is a production/quality optimization lane, not an exact-numerics ruler.

### MXFORGE implication

This is directly relevant to the user's two M1 Max machines. It means earlier M1-generation Flash-Next PP and decode results using BF16 leaves may have understated the practical hardware ceiling. It materially raises confidence in strong PP on the M1 pair, but it does **not** solve distributed MTP / Thunderbolt verification economics.

---

## 2. Flash-Next: concurrent `pread()` makes SSD PLE much less punitive

Source:
- https://github.com/jundot/omlx/pull/3287

The prior mmap/fancy-index PLE gather path can serialize random page faults. PR #3287 uses a thread pool of `os.pread()` calls; `pread` releases the Python GIL and can expose internal-NVMe queue parallelism.

Reported M4 Max internal-NVMe microbenchmark, 500 random 4KB reads:

- serial: ~9,063 IOPS / ~110 us per read;
- 32 workers: ~98,771 IOPS;
- 64 workers: ~99,626 IOPS;
- roughly 11x random-read IOPS at saturation.

Reported full Flash-Next result using `jedisct1/Qwen3.8-Flash-Next-oQ4e-MTP-128k`, 40K cold prompt:

- cold TTFT: 216.85 s -> 6.54 s, about 33x;
- warm TTFT: 12.63 s -> 6.02 s, about 2.1x;
- generation: 43.70 -> 59.92 tok/s.

A second 4-bit PLE checkpoint reportedly moved isolated row reads from ~9,166 to ~109,636 rows/s, with steady-state TTFT around 6-7.5 s.

Rows remained byte-identical in the reported deterministic checks. Resident-PLE mode is unaffected; this targets SSD/mmap PLE.

### MXFORGE implication

This is the strongest evidence yet that SSD-backed PLE should be treated as an optimizable memory tier rather than an unavoidable large decode tax. Actual M1 internal-SSD IOPS still need local measurement, but the mechanism is generic and should combine naturally with request dedupe/coalescing and page-aware prefetch.

---

## 3. Flash-Next: the ~43K wall on a 64GB Mac was largely a software pathology

Source:
- https://github.com/jundot/omlx/pull/3283

PR #3283 fixes two major long-context memory blowups for Qwen4-Exp / Flash-Next:

1. QSA boolean array masks were routed to stock MLX's unfused O(L*T) fallback, materializing large `[heads, L, T]` score slabs.
2. `QSAKVCache` / `QSAQuantizedKVCache` were omitted from the sliceable-cache registry, so boundary/prompt-cache snapshots copied the full K/V + index prefix rather than an incremental slice. The report cites roughly 1.1 GB per snapshot around 40K and quadratic growth.

After both fixes, on M4 Pro 64GB, the author reports clean unique-prompt prefill at:

- 43K;
- 58K;
- 77K;
- 96K;

with a clean guard rejection rather than a crash at roughly 125K. Needle retrieval remained correct at 6K, 10K, and 41,529 tokens.

Full 262K on a 64GB host still requires a real QSA KV-quantization path; a naive conversion currently breaks batch insertion / MTP verify assumptions.

### MXFORGE implication

A significant fraction of the perceived 64GB Flash-Next context ceiling was runtime pathology, not fundamental state size. This raises confidence that each 64GB M1 node can support useful 100K-class working contexts once the corresponding fixes/paths are ported and qualified.

---

## 4. Flash-Next: PLE residency policy can silently create a 2.5x decode regression

Source:
- https://github.com/jundot/omlx/pull/3299

A model swap could sample `vm_stat` in the short interval after the outgoing model released arrays but before macOS returned pages. That temporarily depressed the dynamic admission ceiling and silently forced an incoming Flash-Next PLE table to SSD despite persisted settings still showing resident mode.

Reported M1 Ultra 128GB behavior:

- clean resident load: ~35.3 tok/s;
- after affected model swap: ~14.1 tok/s, with PLE silently forced to SSD;
- after the residency-ceiling fix, clean and post-swap novel-prompt distributions overlapped (~30.5 vs ~29.0 mean in the reported runs).

### MXFORGE implication

For a long-running multi-model / multi-agent service, residency decisions must be observable and based on stable capacity, not momentary allocator/VM-state artifacts. Otherwise a runtime can appear to have enormous unexplained performance variance.

---

## 5. Flash-Next correction: oMLX DFlash support is currently not real for `qwen4_exp`

Source:
- https://github.com/jundot/omlx/pull/3302

The prior compatibility gate accepted any model type containing `qwen`, including `qwen4_exp`. The actual mlx_lm DFlash loader has no resolved path for `qwen4_exp`, so enabling DFlash could fail internally and fall back to the standard engine while the UI/settings suggested it was enabled.

PR #3302 replaces the substring test with the actual supported model-type list and marks `qwen4_exp` incompatible.

### Planning correction

Do not currently count DFlash/DFlash2 as an oMLX Flash-Next speculation lane. For Flash-Next, the live speculation work remains native MTP, context/ngram-derived drafting, and future architecture-specific methods. Dense Qwen3.8-27B can still evaluate DFlash2 separately.

---

# Qwen3.8-27B / Layr challenge: fresh negative controls

Current public challenge frontier found in the latest sweep remains approximately **3.7291100105909x serial-relative** on the organizer's Q4/MTP ruler. This number is not directly comparable to the user's Q8 M1 tok/s ruler.

The important new information is mechanism-level.

## 6. Narrow attention K/V direct-nibble QMV extension lost despite parity

Sources:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1478

Candidate:
- extend the promoted wide direct-nibble QMV specialization into the 1024-4096-output narrow branch, especially attention K/V projections.

Official result:

- candidate: 3.635322445967237;
- frontier: 3.7291100105909;
- parity: passed.

This is roughly a 2.5% score regression despite correct outputs.

### P69 implication

Do **not** mechanically port a wide-projection QMV geometry win into narrow K/V shapes. Occupancy and fixed overhead dominate differently. The current geometry-specific / shape-specific P69 discipline is strongly validated.

---

## 7. Full-attention `o_proj` xsums producer fusion lost badly despite parity

Sources:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1476

Candidate:
- replace the existing compiled flat-grid attention output gate with a custom threadgroup-per-row kernel that computes the gate and emits the downstream QMV xsums table, eliminating 16 standalone fill dispatches.

Official result:

- candidate: 3.649027959612079;
- frontier: 3.7291100105909;
- parity: passed.

About a 2.1% regression.

### P69 implication

Deleting a downstream dispatch is not sufficient justification for replacing an already-efficient compiler-generated producer. Barrier-heavy row/threadgroup geometry can cost much more than the saved fill.

---

## 8. GDN postnorm -> `out_proj` xsums producer fusion also lost despite parity

Sources:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1477

Candidate:
- analogous custom GDN postnorm/gate producer that emits the `out_proj` xsums table.

Official result:

- candidate: 3.6468715281441595;
- frontier: 3.7291100105909;
- parity: passed.

About a 2.2% regression.

### Refined producer-fusion rule

The strongest current rule is now:

> Favor sidecar/epilogue work when it can ride an already-required custom producer **without materially changing its launch geometry**.

Avoid:

> replacing a good compiled flat elementwise producer with a new barrier-heavy threadgroup kernel merely to delete a following auxiliary dispatch.

That distinction should be explicit in P69B13 candidate selection.

---

## 9. Corrections on two previously discussed challenge candidates

### PR #1470 trained/hybrid MTP head

Source:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1470

Local M3 Max measurements reported large acceptance improvements, including code acceptance around 0.730 vs 0.527 for the incumbent and local serial-relative gains.

**However, the official benchmark did not produce a score. It timed out after three hours and was cancelled.**

Therefore the trained hybrid head is **unqualified**, not an officially measured regression or win.

### PR #1472 single-pass M=6/7/8 QMV

Source:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1472

The proposed mechanism attempted to halve repeated weight streaming on deep verify widths by moving M=6/7/8 to one input group and reducing rows-per-SIMD to control register pressure.

**The official workflow failed during bench-workspace preparation and produced no performance score.**

Therefore this mechanism is also **unqualified**, not a measured negative result.

These corrections matter because future planning should distinguish:

- scored rejection;
- correctness failure;
- infrastructure failure / timeout;
- unmeasured local-only claim.

---

## 10. PR #1481 broad compiled-shapeless elementwise fusion is also not performance evidence

Source:
- https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1481

The submission proposed broad `compile(shapeless: true)` fusion for attention gating, precise gated RMSNorm, and SwiGLU.

The validation was **cancelled by the submitter** before a score was produced. Treat it as an idea to inspect, not a positive or negative benchmark receipt.

---

# Updated planning implications

## Flash-Next / two M1 Max machines

The M1/M2 FP16-leaf result and concurrent-SSD-PLE result both move the practical forecast upward in confidence, while the distributed-MTP problem remains unsolved.

Provisional mature forecast remains deliberately broad:

- target-only decode: roughly 28-35 tok/s;
- competent distributed MTP: roughly 42-52 tok/s;
- excellent verifier / favorable coding workload: 50-60+ remains possible;
- 20-30K PP: roughly 400-550 tok/s is now a more credible central band than before, with ~500 tok/s no longer an exotic single-box number on M1-generation hardware once BF16 leaf emulation is removed.

These are forecasts for the two-M1 project, **not measured two-node results**.

A reasonable confidence update for eventual daily-driver MTP throughput is approximately:

- >=30 tok/s: 93-95%;
- >=35: ~82%;
- >=40: ~65-70%;
- >=45: ~50%;
- >=50: ~30-35%.

The confidence increase comes from M1-specific compute-path and PLE-I/O improvements, not from solving Thunderbolt verifier communication.

## Qwen3.8-27B exact Q8 P69

Do **not** raise the finished-P69 target from this sweep.

Keep the prior central expectation around:

- ~20.0-20.3 tok/s finished-P69;
- >=20.0 around 65-70% confidence;
- >=20.5 around 40-45%;
- >=21 around 20-25%.

The new evidence improves candidate-selection discipline rather than revealing a new guaranteed speed lever.

P69B13 should prefer:

1. a remaining measured GDN/projection/downstream-tail seam;
2. producer-side sidecar work only if it can reuse an already-good producer geometry;
3. no blind transfer of wide QMV geometry into narrow attention projections;
4. no reopening of previously closed/profiled lanes merely because a challenge submission mentions a similar mechanism.

Post-P69 MTP-head / scheduling work remains attractive, but the strongest new trained-head candidate is still officially unqualified because its ranked run timed out.
