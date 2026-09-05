# External runtime research watch — 2026-09-05 05:00 ET

Starting freshness boundary:

- project branch head: `755e3e9cac65e7e9970a027b44f76c0e827eaa88`
- cutoff: **2026-09-05 08:03:24 UTC**

This pass rechecked the exact dual-M1 Flash/DS4 lanes first, then single-M1 Qwen3.8-27B,
RTX 5070 Ti Qwen3.8-27B, and transferable QSA/GDN/MTP/runtime work.

## Target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

No new sustained receipt from any of the four target rigs surfaced after the cutoff.

---

# Fresh / material

## vLLM #54521 — correct the SM120/121 GEMM-invariance attribution

A post-cutoff correction at **2026-09-05 08:40:57 UTC** withdraws an earlier blockwise-FP8
M-invariance row from the Qwen3.8-Flash-Next determinism investigation. The test script supplied
row-major scale layouts while the SM120 blockwise kernel infers production M-major/K-major layout
from shapes, so that row was an instrumentation artifact.

What still stands in that report:

- per-channel FP8 dense GEMM was identical across the tested M widths;
- BF16 cuBLAS retained a small **1-ulp, M-dependent** difference;
- fixed-M repeats rule out a simple call-to-call variable in the tested dense FP8 path;
- a production-layout GB10 blockwise-FP8 rerun is still pending.

**Consequence:** do not carry the withdrawn blockwise-FP8 result into the Flash/5070 correctness
model. More generally, numerical-invariance probes must use the runtime's production quant-scale
layout and assert the relevant scale strides before interpreting a kernel result.

This is a correction to mechanism attribution, not throughput evidence and not an Apple result.

## vLLM #55425 — Intel runtime 26.31 stops reproducing the 160K MTP2 Xe crash

A post-cutoff update at **2026-09-05 08:17:30 UTC** reran Qwen3.8-27B GPTQ INT4 + BF16 MTP2 on an
Intel Arc Pro B70 at exactly 160K prompt tokens. Under Intel compute-runtime 26.27 the original run
had passed twice and then produced a CCS timeout / BCS fault / Xe reset on repetition 3.

With compute-runtime **26.31.39395.13**, XPU Graph still enabled and otherwise closely matched
settings, three consecutive 160K + 128-token requests completed successfully:

- request 1: **246.50 s**, PASS;
- request 2: **245.49 s**, PASS;
- request 3: **244.59 s**, PASS.

The reporter correctly stops short of declaring the issue definitively fixed.

**Transfer lesson:** long-context speculative qualification must pin and report the GPU compute
runtime/driver in addition to model/runtime commit. A stability failure can live below the inference
engine and disappear after a low-level runtime update. This strengthens provenance/stability policy
for the RTX 5070 Ti lane but does not alter its target.

## DS4 #929 — Vision-Exp AProjQ4 passes a fully-resident Strix Halo smoke test

A post-cutoff report at **2026-09-05 08:25:22 UTC** exercised the experimental DS4 Vision AProjQ4
artifact on a Ryzen AI Max+ 395 / Radeon 8060S (gfx1151), ROCm 7.1.1, 128 GB unified memory.

Reported configuration/results:

- model: Vision-Exp AProjQ4, **78.62 GiB**;
- fully resident in GPU-visible GTT, no SSD streaming;
- 4K context, temperature 0;
- one kitten image + follow-up question;
- no crash, NaN, loop or BOS-repeat failure;
- object identity/count were correct in this smoke test;
- image-turn processing **95.52 tok/s**;
- follow-up processing **43.94 tok/s**;
- generation **17.69-17.80 tok/s**;
- reported planned memory **79.04 GiB**;
- 100% GPU utilization, no reported throttling.

No matched AProjQ8 control was run, so this is **not** a quality-equivalence or speedup claim.

**Consequence:** AProjQ4 continues to look operationally robust across another backend/memory model,
but this remains cross-hardware support evidence only. Keep AProjQ4 as the primary DS4 candidate and
require an exact dual-M1 AProjQ8/Q4 A/B before moving the DS4 forecast.

---

# Exact-rig / focused no-change checks

## Dual-M1 Flash-Next

- No post-cutoff exact **2x M1 Max 64 / TB4** sustained TG receipt surfaced.
- No completed long-context exact dual-M1 receipt surfaced.
- llama.cpp #28243 had no post-cutoff comment; the prior Metal `MUL_MAT` verifier-width exactness
  finding remains the current Apple-MTP gate.
- vLLM QSA updates in this window are CUDA/GB10 attribution work, not an Apple rate ruler.

## Dual-M1 DS4-0731

- No post-cutoff sustained generated-token denominator from exact dual-M1 0731 surfaced.
- DS4 #952 had no post-cutoff comment in this window.
- The fresh #929 result is Strix Halo Vision-Exp and does not recalibrate dual-M1 0731.

## Single M1 Max64 Qwen3.8-27B

- No post-cutoff exact M1-Max Qwen3.8-27B serving receipt surfaced.
- Core MLX #4409 remained at its pre-cutoff update (`2026-09-05T03:59:46Z`); no new M1 result.
- P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

## RTX 5070 Ti16 Qwen3.8-27B

- No post-cutoff exact 5070-Ti throughput receipt surfaced.
- Exact-hardware GitHub search produced no new 5070-Ti/Blackwell issue or PR hit in the watched
  llama.cpp lane after the cutoff.
- The Intel #55425 update changes stability provenance policy only; it is not a CUDA speed ruler.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep the 04:00 qualification order, with one instrumentation refinement:

1. pin/certify llama.cpp `v0.4.0` / exact tagged commit on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. PLE residency/page-cache/direct-read A/B;
4. sparse-QSA wide-prefill A/B;
5. QSA neighboring-row selected-block reuse A/B after sparse-QSA passes;
6. pooled QSA-prefix retention / rollback correctness;
7. Metal target-op batch-width invariance across actual quant types and planned verify widths;
8. for quantized-kernel invariance probes, reproduce **production scale layout/strides** explicitly;
9. singleton MTP depth/acceptance with pre-verify snapshot + exact recurrent commit/replay;
10. mismatched-length concurrent pure-prefill state-isolation gate;
11. adversarial parallel-MTP slot isolation, then MTP concurrency >1;
12. compiled-decode B2/B4;
13. exact cache/session reuse and multi-agent stress.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

No topology or forecast change. PP2/layer ownership remains primary; TP2 control; AProjQ4 primary
candidate; request-adaptive speculation; mapping/OS/command-buffer/residency diagnostics; fixed-work
PP measurement; tool-observation, compaction and exact-session gates.

Fresh #929 is another backend smoke-pass for AProjQ4, not the required dual-M1 A/B.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No target change. Preserve the Metal verifier-width exactness gate if batched verification is used,
and require production quant-layout fidelity in any isolated numerical-invariance probe.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Keep:

- fully resident Q3_K_XL + native MTP as the speed lane;
- linked CUDA-runtime provenance;
- driver/runtime version in every certification receipt;
- ubatch/prompt-shape and graph stability matrix;
- draft-cache net-memory A/B;
- DFlash control;
- small-N verification;
- MTP-head quant and GSQ-RCO qualification.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing policy additions from this pass

- **Kernel-invariance tests must mirror production tensor/scale layout.** A mathematically similar
  synthetic layout is not enough for backend dispatch/numerics attribution.
- **GPU driver / compute-runtime version is part of the benchmark identity.** Long-context MTP
  stability can change below the inference-engine layer.
- A successful alternate-backend AProjQ4 smoke test strengthens operational confidence but does not
  substitute for the exact dual-M1 Q8/Q4 comparison.
- Stronger/different hardware mechanisms do not move target-rig TG/PP forecasts by themselves.
- P69 exact verifier work remains isolated from serving/runtime research.

The detailed confidence ladders and target-change rules remain authoritative in
`RESEARCH-TARGETS.md`.
