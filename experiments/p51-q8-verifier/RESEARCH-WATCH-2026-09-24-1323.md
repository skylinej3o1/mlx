# Project 51 primary-lane research watch — 2026-09-24 13:23 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 10:40:14 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 17:23:35 UTC**.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

No exact dual-M1/TB4 Flash-Next S=2-8 verifier receipt appeared, no direct Apple7 PP2 overlap measurement appeared, and no new source-vs-quant xhigh behavioral certification from DASLab/ByteShape appeared.

However, this pass materially improves three parts of the implementation model:
1. **warm-prefix MTP state is now proven to be performance-critical**, not just a correctness sidecar;
2. **small-M verifier specialization gained another set of real server-level wins at 72K-200K context** while preserving acceptance;
3. **cold PLE/page-fault stalls now have a concrete measured mitigation pattern** rather than remaining a generic warning.

It also adds one negative Apple-runtime warning: Metal queue-residency configuration can produce multi-minute submission stalls under some large-model workloads, so transport/compute jitter must be qualified under realistic idle/resume and memory-pressure conditions.

## Findings

### NEW / CORRECTED — oMLX #3895/#3901: warm target-prefix reuse without matching MTP history can make cached decode slower

Sources:
- https://github.com/jundot/omlx/issues/3895
- https://github.com/jundot/omlx/pull/3901
- merged commit **92483d9b967d** at **2026-09-24 16:52:26 UTC**

A user reported an apparent Flash-Next Lightning-MTP regression from dev3 to current main. The first report mixed two different workload identities:
- dev3's ~167 TG was a **~46-token warm-prefix burst** after cache restoration;
- maintainer comparison used a **1,024-token sustained no-cache** decode.

Maintainer same-machine M3 Ultra 512 GB no-cache A/B:
- dev3: **103.74 TG**
- before #3797: **110.75**
- current main: **113.36**

Thus there is **no demonstrated base verifier regression** on that sustained no-cache workload; current main is faster there.

The useful bug was in the warm-tail path. #3901 shows that a non-aligned tail-cache hit restored the target/backbone prefix but Lightning MTP history was retained only at full-block boundaries.

Controlled M3 Ultra / Flash-Next oQ4e-mtp result:

| Metric | main | #3901 |
|---|---:|---:|
| cached prompt tokens | 685 | 685 |
| MTP primed tokens | **7** | **692** |
| draft acceptance | 87.0-87.2% | **93.7-94.0%** |
| decode throughput | 116.05 TG | **133.75 TG** |
| TTFT | 0.149 s | 0.150 s |
| request wall | 8.967 s | **7.797 s** |

The fix captures MTP history at the retained tail boundary, keys the bounded in-memory sidecar by the matching backbone chain hash including the terminal partial block, and requires an exact live boundary before restore.

The sidecar remains memory-only; it is not restored across process restart.

A separate user bisect identified two apparent regressions (#3835 tail matching and #3854 first-chunk release), but the maintainer could not reproduce a first-chunk throughput penalty and kept that behavior. #3901 is the accepted/merged fix.

**Classification:** NEW exact-family warm-agent performance evidence + correction of initial regression interpretation.

**P51 consequence:** warm-state identity must distinguish:
- target prefix/cache state,
- recurrent state,
- QSA/indexer state,
- **MTP/draft history at the exact terminal tail boundary**.

A cache hit that restores target state but not compatible MTP state can improve TTFT while **reducing speculative decode acceleration**. Benchmark cold sustained TG, warm long-output TG and short agent-burst TG separately.

### NEW — SGLang #41133: one-launch small-M MoE router cuts real verify-step time 7.5-8.2% at 72K-200K

Source: https://github.com/sgl-project/sglang/pull/41133

Qwen3.5-397B MoE on MI355X, real EAGLE/MTP. The existing verify route for M=1-8 performs:
1. gate GEMM,
2. router softmax/top-k,
3. shared-expert append.

The PR collapses them into one launch for M<=8.

Real server decode-step A/B at concurrency 1:
- **72K:** 8.79 -> **8.07 ms (-8.2%)**
- **200K:** 9.06 -> **8.38 ms (-7.5%)**

MTP acceptance:
- baseline **3.612**
- new **3.613**

Microkernel routing:
- M1: 12.39 -> 8.54 us (**1.45x**)
- M2: 12.82 -> 8.80 (**1.46x**)
- M4: 12.90 -> 9.05 (**1.42x**)
- M8: 13.26 -> 11.66 (**1.14x**)

The optimized path intentionally stops at M=8; it is slower than the existing path at M>=9.

**Classification:** NEW cross-hardware verifier evidence.

**P51 consequence:** another strong independent confirmation that **S=1-8 is a separate kernel regime**. Fixed launch/router overhead can remain a meaningful fraction of a verify step even at 200K context, and the correct optimization can remove ~8% of whole-step latency without changing acceptance. No percentage transfers to Apple7.

### NEW — SGLang #41134: small-M projection specialization removes another 4.4-5.1% of long-context decode step

Source: https://github.com/sgl-project/sglang/pull/41134

Same broad MI355X/Qwen3.5 MTP regime, targeting small-M FP8 attention/GDN projections and fusing output-side activation quantization.

Real server step:
- c1, **72K:** 8.65 -> **8.21 ms (-5.1%)**
- c1, **200K:** 9.11 -> **8.71 ms (-4.4%)**
- c4, 72K: 11.50 -> **11.02 ms (-4.2%)**

MTP acceptance:
- baseline **3.603**
- new **3.616**

The fused producers remove **60 per-token quant launches per verify step**.

**Classification:** NEW cross-hardware verifier evidence.

**P51 consequence:** strengthens the same conclusion from a different component: small-row verifier cost is not a single unavoidable ALU floor. Projection launch/packing/quant overhead is separately attackable. The P51 Apple7 profiler should decompose S=2-8 verify into GDN, routing, expert projections, QSA, head, host dispatch and temporary copies before accepting a 2.1-2.4x “hardware floor.”

### NEW — SGLang #41123: exact Flash-Next MXFP4 preserves MTP acceptance on one controlled low-bit correctness workload

Source: https://github.com/sgl-project/sglang/pull/41123

Qwen3.8-Flash-Next, TP8+EP8, full target/draft decode graphs, EAGLE/MTP 3/1/4.

Five-shot GSM8K:
- MI355X BF16: **96.8798%**, mean MTP acceptance **3.5669**
- MI355X FP8: **96.8037%**, acceptance **3.5690**
- MI355X Quark MXFP4: **96.6514%**, acceptance **3.5524**

All 1,314 scored responses completed with zero request errors.

**Classification:** NEW exact-family low-bit acceptance evidence, cross-hardware and non-xhigh.

**P51 consequence:** materially weakens the blanket claim that low-bit target weights must cause severe MTP acceptance collapse. On this workload, MXFP4 acceptance is within ~0.4% of BF16 in absolute accepted-length terms. But this is **thinking-disabled GSM8K on AMD**, not xhigh agent work; it does not validate the P51 ~2.4 xhigh committed-token assumption or the ~3.3-3.6 BPW source-like frontier.

### NEW — vLLM #54070 fresh field report: page-fault-driven PLE stalls can be parallel-prefetched

Source: https://github.com/vllm-project/vllm/pull/54070#issuecomment-5812965047  
Fresh comment: **2026-09-24 11:13:13 UTC**.

RTX PRO 6000 / Qwen3.8-Flash-Next offload worker, ~48 GB FP8 PLE table in pageable host memory with 22-39 GB swapped to NVMe.

Observed failure mode:
- decode-sized gather uses effectively serial fault handling;
- about **17 major faults/token**;
- cold row ~100-150 us;
- one PLE wait creates ~**4.3 ms GPU idle gap per decode step**.

Prefetch mitigation:
- collect unique pages for requested rows;
- issue batched `process_madvise(..., MADV_WILLNEED)`;
- let kernel start page-ins concurrently before gather.

Measured:
- PLE gather **2.94 -> ~1.3 ms**
- decode step **19.8 -> 18.0 ms (-9%)**
- major faults/gather **~19 -> ~0**
- 16K prefill **2.06 -> 1.68 s**
- plus background prompt-hint prefetch: **2.06 -> 1.52 s (-26%)**

The author explicitly had **not** tested a file-backed mapping.

**Classification:** NEW exact-family cross-hardware PLE-stall evidence.

**P51 consequence:** this directly answers the PLE page-fault concern with a measurable design pattern: **batch page intents before gather and overlap future-row residency with earlier compute**. P51 must report major-fault count, PLE wait p50/p95/p99 and GPU-idle time; average SSD bandwidth is insufficient. This is mechanism evidence only, not M1 NVMe latency proof.

### NEW / caution — DS4 #931: Metal queue-residency configuration can cause minute-scale submit stalls

Source: https://github.com/antirez/ds4/issues/931  
Fresh same-day field report in-window.

On M3 Ultra / macOS 27 / large DeepSeek Flash workloads, a contributor captured stalls with:
- worker waiting in `waitUntilCompleted`;
- Metal submission thread blocked in `IOGPUCommandQueueSubmitCommandBuffers`;
- GPU utilization near zero during the stall.

In a narrow reproducible request, changing only:
`DS4_METAL_DISABLE_QUEUE_RESIDENCY_SET=1`
turned repeated **120 s hangs** into ~**5-6 s** completions, including after idle. This skips `queue.addResidencySet` while retaining explicit residency requests and queue keepalive.

Caveats:
- M3 Ultra, macOS 27, DeepSeek rather than M1/Flash-Next;
- short bounded repro does not establish reliability at 272K;
- root driver defect is not proven.

**Classification:** NEW Apple-runtime negative evidence.

**P51 consequence:** loaded cross-node/Metal timing qualification must include **idle->resume, memory-pressure and residency-policy** cases. A 0.3-ms idle transport RTT is not enough; record submission-to-GPU-start and completion p99/p999 under real agent idle gaps. Keepalive/residency policy is part of runtime identity.

### NEW — llama.cpp #29353: chunked GDN recurrence materially improves prefill across three GPU families

Source: https://github.com/ggml-org/llama.cpp/pull/29353

New CUDA/HIP chunked GDN kernel. Qwen3.8-27B Q8:
- RTX PRO 6000: 2048 PP **3977 -> 4449 (+11.9%)**, 4096 **3997 -> 4437 (+11.0%)**
- GB10: 2048 **858 -> 955 (+11.3%)**, 4096 **852 -> 951 (+11.6%)**
- Strix Halo: 2048 **331 -> 354 (+6.8%)**, 4096 **327 -> 350 (+7.0%)**

Qwen3.5-35B gains ~12-19% depending hardware.

Correctness screen reports small KL/perplexity differences and ~98.8% top-token agreement, not bit-identical behavior.

**Classification:** NEW cross-hardware prefill mechanism evidence.

**P51 consequence:** GDN's sequential recurrence does not imply there is no chunk-level kernel headroom. It reinforces the case for a purpose-built Apple7 chunked recurrence path, but the non-bit-identical numerics require source/logit/chunk-invariance qualification before P51 adopts a similar transformation.

### CORRECTION / RETRACTION — DS4 #1115 restart-cache “real FAIL” from the prior watch was a buggy test

Source: https://github.com/antirez/ds4/pull/1115#issuecomment-5814784999  
Fresh maintainer comment: **2026-09-24 13:11:43 UTC**.

The previous watch promoted an independent report's retention-off restart result (0/1033 cached tokens) as a genuine checkpoint-identity failure. The PR author subsequently states:

> "Turned out to be buggy tests"

Therefore that specific failure **must not remain durable evidence of a DS4 cache-key defect**.

The broader P51 rule that rendered/tokenized prompt semantics and state-affecting configuration belong in cache identity remains supported by other independent evidence, but **#1115 no longer supports that claim**.

### UPDATE — vLLM #58548: hybrid+EAGLE retention interval can determine whether prefix reuse is 0%

Source: https://github.com/vllm-project/vllm/pull/58548

For hybrid models with EAGLE, an unset retention interval fell through to sparse `0`, leaving only a replay-boundary checkpoint that tail-block dropping made unreachable. Result: **0% prefix-cache hits**.

The fix defaults hybrid+EAGLE to **6 x scheduler block_size**, based on earlier measurements, while preserving explicit user choices.

**Classification:** NEW/UPDATE state-retention evidence.

**P51 consequence:** persistent checkpoint *density* is part of performance identity. A semantically correct checkpoint can be practically useless if the scheduler's tail/drop geometry makes every retained boundary unreachable. Retention interval should be tuned jointly with block size, speculative depth and common agent-turn tail lengths.

### KNOWN / merge updates

- oMLX #3797 merged at **2026-09-24 11:18:29 UTC**. Its substantive Flash-Next +20.7% M5 B1 branch-level result was already recorded before this boundary.
- mlx-serve #517 and #519 merged to main at ~13:38 UTC. Their GDN-verify and fused-MoE results were already durable.
- oMLX #3853 generalized fused Qwen GDN decode on main; M1 Max ~5.8-6.2% nearby-GDN evidence was already durable.

## Quant / community search

- **ISTA-DASLab/GSQ:** no new GitHub issue/PR/commit in this exact window. The official Flash-Next GSQ-RCO release remains current; no fresh xhigh behavioral certification was found.
- **ByteShape:** no precisely timestamped new source-vs-quant Flash-Next behavioral result was found inside the boundary.
- A same-day UkisAI Swift Flash-Next/GSQ-RCO community release claims large thinking-token reductions at near-base xhigh scores. Its public surface did not expose a publication timestamp precise enough to prove that it falls inside this strict watch interval, and it changes behavior/token policy by design. It is therefore **not promoted into the canonical source-like P51 lane**.
- Same-day LocalLLaMA/LocalLLM searches otherwise surfaced already-known M1 Splash and older Flash-Next Mac results, not a new exact dual-M1/TB4 receipt.

## Canonical planning state after this pass

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**, conditional on at least modest speculation benefit.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target; Apple7 + heterogeneous quant + verifier co-design remains an experimental upside lane.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 17:23:35 UTC**
