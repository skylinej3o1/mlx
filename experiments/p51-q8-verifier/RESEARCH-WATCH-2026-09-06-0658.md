# External runtime research watch — 2026-09-06 06:58 ET

Starting branch checkpoint: `4fcc8631aed3bde6e2e757c281d586c1c5a4c200`

Starting hard freshness cutoff: **2026-09-06 06:51:53 UTC**.

## Executive result

This pass is **material for certification and experiment ordering, but does not move any canonical TG/PP target**.

No fresh sustained receipt surfaced on the exact 2x M1 Max 64 GB / TB4 Flash topology, exact 2x M1 Max DS4-0731 topology, exact M1 Max 64 GB Qwen3.8-27B topology, or exact RTX 5070 Ti 16 GB Qwen3.8-27B topology.

The useful changes are:

1. hybrid GDN + MTP can collapse from full-batch scheduling to a much narrower live speculative window even while small-batch acceptance is healthy;
2. the first-repeat prefix-cache failure is now reproduced on unmodified current vLLM main and traced to a mismatch between the EAGLE-adjusted reusable boundary and the recurrent-state retention boundary;
3. a fresh distributed llama.cpp MTP regression shows that acceptance can remain healthy while end-to-end speculative throughput regresses 25–30%, reinforcing whole-round/transport accounting;
4. the current M5 Max Flash prefill report corrected its own early MoE diagnosis: at realistic 65K depth, long-context attention is the largest component and the engine is already around 42% of the measured 4-bit GEMM ceiling; do not chase the initial “19x unsorted MoE” headline;
5. CUDA benchmark provenance must include the backend that actually executed FlashAttention, because unsupported quantized KV can silently schedule FA on CPU while the benchmark still reports `fa=1`;
6. vLLM’s deterministic `persistent_topk` fix remains open; the proposed contract and standalone tests sharpen the QSA correctness gate, but end-to-end validation is still pending.

---

# FRESH / material

## llama.cpp #28484 — draft-MTP over a distributed RPC split regressed while acceptance and plain decode stayed healthy

Issue created **2026-09-06 09:49:46 UTC**.

Physical setup:

- Qwen3.8-27B UD-IQ4_XS, 14.25 GB, embedded MTP;
- Linux RTX A2000 12 GB + Windows RTX 3080 10 GB;
- 2.5 GbE llama.cpp RPC tensor split;
- old good commit `bb4caa7` (2026-08-21) versus bad/current `6a1a922` (2026-09-05);
- 1,209-token prompt / 1,024-token generated benchmark.

Reported comparison:

| configuration | old | new |
|---|---:|---:|
| draft-MTP depth 2 | **27–32 tok/s** | **21.3 tok/s** |
| draft-MTP depth 1, retuned split | — | 22.6–24.4 tok/s |
| no-MTP dense decode | ~17–18 tok/s | **17.5 tok/s** |
| draft acceptance | ~0.68–0.80 | **0.737–0.832** |
| mean accepted length | ~1.7–1.8 | **1.74–1.83** |

A separate 31B dense control remained **17.66 tok/s** before and after on the same RPC split.

The newer build also grew graph/compute reserve enough that a previously loadable 98K-context configuration could OOM until the split or context was retuned.

### Promotion

For distributed/TB4 MTP qualification, **acceptance is not a sufficient performance oracle**. Every speculative receipt should separate:

- plain/no-MTP decode on the same distributed topology;
- speculative TG/E2E wall;
- acceptance and accepted tokens/cycle;
- per-round transport/synchronization count and time;
- graph/compute reserve and peak memory;
- verifier/draft context allocation.

This is strong distributed-mechanism evidence, but RPC over 2.5 GbE is not TB4/Apple evidence and does not imply a dual-M1 rate.

---

# BACKFILL + FRESH UPDATE / material

## vLLM #53504 — first-repeat MTP cache miss now confirmed on unmodified current main

The issue predates this cutoff, but received fresh confirmations after it and now includes an unmodified-current-main reproduction.

Physical report:

- Qwen3.8-27B-FP8 hybrid, 3 recurrent/Mamba cache groups + 1 FullAttention group;
- dual RTX 5090, TP2;
- MTP with 2 speculative tokens;
- auto block/prefix-hash unit **1,600 tokens**;
- repeated ~11.9K-token prompt, requests strictly serialized.

Observed spec-on TTFT pattern:

- production boot: **2.76 / 2.77 / 0.61 s** = cold / full re-prefill / hit;
- separate no-sleep boot: **2.49 / 2.48 / 0.55 / 0.55 s**;
- matched no-spec control: request 2 hits immediately at about **0.27 s**.

On unmodified current main `0.26.1rc1.dev1130+g2ec6f0d71`:

- spec-on: **24.9 / 2.83 / 0.61 s**;
- no-spec: **3.47 / 0.28 / 0.29 s**.

The important mechanism is boundary alignment:

1. MTP/EAGLE semantics reduce the reusable 11,910-token prompt boundary to **9,600**, not 11,200.
2. The first request materializes recurrent state at 9,600 but the default sparse retention mask keeps the unshifted 11,200 replay boundary instead and masks the usable 9,600 state.
3. FullAttention has 9,600, recurrent groups do not, so hybrid reconciliation returns **0** on request 2.
4. Request 2 learns/registers the 9,600 junction and request 3 hits it.

A retention-interval workaround at exactly 1,600 produced **2.52 s cold, then 0.55 s on all four repeats**, including after a 10-second gap. Occupancy/eviction pressure was not measured.

Fresh maintainer comments say the cache-hit drop is known and point at merged PR #53388 (`disable_eagle_block_drop`) as a possible control. Important nuance: #53504’s own analysis accepts the EAGLE one-block drop and proposes retaining the **adjusted** recurrent boundary; simply removing the drop is not yet established as the correct fix for this hybrid case.

### Promotion

Flash cache qualification should use **one canonical reusable-prefix boundary shared by recurrent and attention state**, and explicitly record:

- full prompt length;
- EAGLE/MTP-adjusted reusable boundary;
- recurrent retained boundaries;
- attention retained boundaries;
- first-repeat hit tokens;
- second-repeat hit tokens;
- growing-agent reused/fresh tokens;
- retained-state occupancy/eviction pressure.

A fix that improves first-repeat TTFT but changes target-model greedy output does not pass.

This strengthens, rather than replaces, oMLX #3462 and the previous first-repeat backfill.

## vLLM #55533 — hybrid GDN + MTP can collapse to a ~3-sequence speculative scheduling window

Issue created before this pass’s cutoff but received fresh activity after it.

Physical setup:

- current vLLM main `f4eccda` as of 2026-09-06;
- RTX 4090 D / WSL2;
- Qwen3.8-27B GPTQ INT4 g128;
- 64 layers = **48 GDN + 16 full attention**;
- MTP `k=1`;
- `max_model_len=4608`, `max_num_seqs=25`.

At batch 8, scheduler tracing shows each decode iteration scheduling exactly **3 of 8** sequences with distribution `[2,2,2]` (target + one draft token for each scheduled sequence). The other sequences rotate in only as earlier ones finish.

Measured throughput:

| batch | no spec | MTP k=1 | mean accepted length per seq/iteration |
|---:|---:|---:|---:|
| 1 | 56.4 | **72.0** | 0.86 |
| 3 | 150.6 | **203.7** | 0.84 |
| 4 | **195.4** | 157.8 | **-0.03** |
| 8 | **367.1** | 197.0 | **-0.38** |
| 20 | **649.0** | 210.9 | **-0.73** |

The 24-GDN-layer 9B sibling schedules all sequences up to batch 20. The reported collapse is quant-path/KV-path independent across W4A16/W4FP8, BF16/FP8 KV and multiple GDN kernels. Upstream `874df93` fixed the batch-4 point, but batch >=5 remains affected in the report.

The fresh follow-up is now explicitly investigating how recurrent-state cache budget and `(1 + k)` speculative slots are accounted by the scheduler.

### Promotion

For the planned 3–4 logical-agent appliance, **configured concurrency is not measured concurrency**. Certification must record per iteration:

- active logical requests;
- actually scheduled sequences;
- scheduled-token distribution by sequence;
- MTP target/draft slots resident;
- recurrent-state memory per sequence;
- cache-budget admission/rejection;
- aggregate emitted tokens/iteration and aggregate TG.

Run at least parallel 1/2/3/4, then a stress point above 4. This directly strengthens the current safe-serving rule: use profitable singleton MTP plus plain concurrent work until multi-slot MTP state residency and slot isolation are proven on the target runtime.

This is CUDA transfer evidence, not proof the same scheduler cap exists on M1.

## mlx-serve #366 — correction chain: 65K M5 Flash prefill is attention-heavy, not an obvious MoE defect

The original issue body predates the cutoff and initially attributed low utilization to unsorted expert GEMMs. Fresh measurements after the cutoff **retracted that mechanism twice**. The final current interpretation is the one retained here.

Still-valid direct model-level measurement:

- M5 Max 128 GB, macOS 26.5, mlx-serve 26.9.1 / MLX 0.32.2;
- Qwen3.8-Flash-Next 4-bit, resident 68.4 GB;
- 65K real-source-code prompt, prefix cache disabled;
- measured Flash prefill **1,329 tok/s**;
- dense 27B controls were 604 tok/s in mlx-serve and 651 tok/s in Ollama MLX.

The reporter then corrected the component profile to use the **real attention depth**. For a representative 4,096-token chunk around 32K average key length in the 65K run:

| component | measured time | share of 3,060 ms actual chunk |
|---|---:|---:|
| SDPA, ~32K key length | **1,112 ms** | **36%** |
| MoE gather_qmm x3 | 665 ms | 22% |
| MoE scaffolding | 271 ms | 9% |
| GDN projections | 232 ms | 8% |
| conv1d | 89 ms | 3% |
| attention projections | 64 ms | 2% |
| accounted | 2,433 ms | 80% |

Across the full 65K work estimate:

- attention FLOPs: **633 TFLOP**;
- weight FLOPs: **393 TFLOP**;
- total: **1,026 TFLOP in 49.3 s = 20.8 TFLOP/s**;
- about **42%** of the reporter’s measured ~50 TFLOP/s 4-bit GEMM ceiling.

Individual SDPA and MoE kernels were reported in the roughly **27–38 TFLOP/s** range. The earlier “16% utilization” and “95.7% MoE” claims were measurement artifacts from profiling a shallow key length.

The reporter also corrected two tempting optimization hypotheses:

- prefill already sorts routed expert work;
- actually doubling runtime chunk 4,096 -> 8,192 measured **0–1%** change (1,320/1,348 vs 1,337/1,345 tok/s in two interleaved rounds).

Final conclusion from the reporter: no obvious 3x MoE defect remains; a prefill profiler and the unattributed ~20% may be worth studying, but the engine is in a plausible efficiency regime for this mixed long-context workload.

### Promotion

Use this as **Apple mechanism-transfer anatomy**, not as an M1 target ruler.

For Flash long-context PP experiments:

- profile at the actual key/context depth, not only a shallow 4K chunk;
- separate QSA/SDPA, MoE, GDN and host/launch overhead;
- do not infer chunk effectiveness from a requested flag without tracing the effective runtime chunk;
- do not prioritize a routed-MoE rewrite merely from the initial issue headline;
- keep long-context attention/QSA optimization high in the order because attention becomes first-order as reused context grows.

The measured 1,329 PP is on M5 Max and does **not** move the dual-M1 400 PP target.

## vLLM #54521 / PR #55122 — deterministic QSA selection fix is defined, but end-to-end proof is still pending

Fresh comments after the cutoff point at open PR #55122, which proposes a deterministic `persistent_topk` contract:

- selected output sorted in ascending index order;
- no atomic arrival-order slot assignment;
- exact handling of threshold ties;
- candidate buffers that caused set truncation are removed on the relevant paths.

Standalone sm121 testing reported **177/177** deterministic/reference-equal cases; the same unmodified kernel reproduced its own exact output in **0/177** on those inputs.

Reported kernel cost on GB10 is roughly **1.3–3x per top-k call** depending shape. The PR estimates about +1.5% per model decode step at 32K context and +2% TTFT at 8K, but the end-to-end A/B was still pending in the inspected state. Those are estimates, not promoted model rates.

A fresh follow-up also scopes Qwen3.8-Flash-Next’s MoE router: for this model vLLM selects `FusedTopKRouter` / CUDA `topk_softmax`, not the `grouped_topk` Python fallback. Therefore the separate #55514 grouped-router fix should not be conflated with the sm121 Flash QSA issue.

### Promotion

Keep the QSA gate from the 02:43 pass, and add a **position-resolved behavioral layer** between kernel tests and final completion hashes:

- teacher-forced per-position logprob spread across identical repeats;
- top-1 agreement;
- top-k set overlap;
- first divergent prompt position;
- serial repeats and a concurrent batch;
- cells below, around and above the QSA selection boundary.

A deterministic kernel fix is not promoted until end-to-end logits/output pass on the intended serving path.

---

# BACKFILL / known serving-provenance trap

## llama.cpp #28455 — `-fa on` does not prove FlashAttention ran on GPU for all quantized KV types

The issue predates the cutoff but was freshly closed by a maintainer as a **known issue**.

Reported CUDA behavior with the default `GGML_CUDA_FA_ALL_QUANTS=OFF`:

- q4_1/q5_0/q5_1 KV types can cause `GGML_OP_FLASH_ATTN_EXT` to be rejected by CUDA and silently scheduled on CPU;
- `llama-bench` can still print `fa=1` for that row.

RTX 4080, Qwen3.8/3.5-family 27B report:

| KV / build | prompt eval | decode |
|---|---:|---:|
| q5_1 default | **38.4 tok/s** | **6.5 tok/s** |
| q8_0 default | 1,348 tok/s | 30.1 tok/s |
| q5_1 with `GGML_CUDA_FA_ALL_QUANTS=ON` | **1,162 tok/s** | **38.5 tok/s** |

The exact issue report was closed partly for repository AI-post policy, so treat its detailed rate table as user-reported evidence; the maintainer explicitly called the underlying behavior known.

### Promotion

For 5070/Tiel/Qwen experiments, benchmark provenance includes **actual operator/backend placement**. Do not infer treatment from `-fa on`, the KV-type label, or the benchmark summary alone.

If using q4_1/q5 KV, explicitly verify FA kernel support/build flags and GPU execution before comparing PP/TG.

---

# Focused follow-up status

- **oMLX #3462:** no post-cutoff comments/fix surfaced; real-agent cache-capture gate remains active.
- **oMLX #3464:** no post-cutoff comments/fix surfaced; explicit TG provenance/denominator gate remains active.
- **jundot/omlx main:** no material post-cutoff update surfaced in the checked window.
- **rMLX main:** no post-cutoff commits surfaced; whole-round MTP decomposition from the 02:43 pass remains current.
- **antirez/ds4 main:** no post-cutoff commits surfaced.
- **MLX #4409:** no post-cutoff comment/result surfaced.
- **llama.cpp #28425/#28433/#28448/#25187:** no fresher material result displaced the current gates in this pass.
- **Tiel Coder:** no fresh targeted result surfaced.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG receipt or completed new exact-rig cold-PP result.
- **Dual-M1 DS4-0731:** no fresh sustained generated-token denominator on 2x M1 Max64/TB4.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact-card TG/PP receipt.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max serving receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

---

# Current consequences by lane

## Dual-M1 Flash-Next

No target change. Refine qualification order:

1. exact PP2/layer-owned baseline; TP2 control;
2. ordinary no-spec recurrent rollback / growing-session correctness;
3. real-agent cache capture plus **canonical recurrent/attention reusable-boundary** check;
4. first-repeat, second-repeat and growing-session hit/frontier metrics with MTP on/off;
5. QSA selected-set/order determinism plus position-resolved logprob/top-k behavioral regression;
6. long-context PP profiler at realistic key depth: QSA/attention vs MoE vs GDN vs host/launch;
7. PLE residency/page-cache/direct-read and QSA known-horizon/residency work;
8. MTP recurrent commit/replay plus per-slot draft-context sizing;
9. **scheduled-sequence occupancy** at parallel 1/2/3/4 and stress above 4;
10. concurrent pure-prefill and adversarial MTP slot-isolation gates;
11. whole-round MTP replay/verify/head/sync/transport accounting;
12. activation-FP16 approximate lane only after exact freeze;
13. compiled multi-agent / long-prefill-while-decode combinations.

Canonical center remains **40 TG / 400 cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B / Tiel control lane

No target change to the Qwen row and no Tiel rate claim.

Keep:

1. Qwen exact known resident baseline;
2. Tiel Q4/Q5 partial-expert-offload practical A/B, not 3-bit by default;
3. actual backend/operator placement stamped into every row;
4. if testing quantized KV, assert FlashAttention support and GPU execution;
5. MTP whole-round metrics, including scheduled-sequence occupancy at multi-request batch;
6. full-head quantization before aggressive FR-Spec trimming;
7. quality/useful-work-per-hour plus TG/PP/VRAM/context headroom.

Canonical Qwen center remains **120 TG / 250 cold PP**.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**. None of this external serving work changes that sequence.

Canonical center remains **25 TG / 110 native cold PP**.

## Dual-M1 DS4-0731

No fresh exact-rig result. Existing Metal/TB transport, scratch/temp, rollback and session-state transfer candidates remain in force.

Canonical center remains **15 TG / 180 cold PP**.

---

# Standing decisions strengthened this pass

- **Configured concurrency is not measured concurrency.** Record the sequences the scheduler actually admits each iteration.
- MTP multi-agent promotion requires target + draft recurrent-state budget accounting, not only acceptance and aggregate TG.
- **Acceptance can stay healthy while speculative throughput regresses materially.** Always retain a same-topology no-spec control and round/transport accounting.
- Hybrid cache reuse needs one canonical reusable boundary across recurrent and attention state; certify the first repeat explicitly.
- Do not “fix” EAGLE/MTP cache boundaries by changing semantics unless verifier-only greedy equivalence remains intact.
- Long-context performance attribution must use realistic key depth. Shallow component profiles can invert the apparent bottleneck.
- Requested/runtime flags are not treatment proof: stamp effective chunk sizes, actual backends and operator placement.
- QSA promotion requires kernel determinism **and** position-resolved/end-to-end behavioral equivalence.
- Existing gates remain active: ordinary recurrent rollback, first-repeat cache efficacy, persistent runtime identity, checkpoint/tensor completeness, per-slot draft context, concurrent state isolation, whole-round MTP economics and explicit TG generated-token provenance.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.
