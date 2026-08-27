# Qwen3.8-Flash-Next day-two runtime delta

Status: **FRESH FIELD EVIDENCE / high relevance to 2x M1 Max MXFORGE target**

Updated: 2026-08-27 afternoon.

## Executive delta

Several important results appeared after the first day-one scans:

1. A dedicated Apple `mlx-serve` implementation with the 51.2B PLE removed from resident MLX weights now reports roughly **60 tok/s serial decode, 78 tok/s on code with native MTP, and ~730 tok/s prefill** on an M4 Max 128GB. The model uses 4-bit routed experts, 8-bit sensitive non-expert paths, BF16 controls, and a 4-bit SSD/mmapped PLE sidecar. Resident memory is ~75GB. This is the closest public architecture match yet to the planned MXFORGE hierarchy.
2. The same implementation reports that MTP is highly workload-dependent: about **+41% on code**, but slightly slower on prose and on one 8.5K prompt. Therefore native MTP should be adaptive, not blindly always-on.
3. A separate M5 Max 128GB llama.cpp user rearranged the Unsloth GGUF so PLE tensors can remain mmap/SSD-backed instead of Metal-wired. Wired memory fell from ~123GB to ~97GB while decode remained **36 tok/s without MTP**. This is direct Apple evidence that moving the PLE to SSD can be effectively throughput-neutral in a real full-model run.
4. PipeNetwork published a strong quant-sensitivity study. Uniform 4-bit is badly degraded on WikiText-2 (ppl 5.3914 vs 4.4708 BF16), while 4-bit routed experts + 8-bit sensitive non-expert weights gives ppl 4.5286, only +1.3%. Uniform 6-bit and 8-bit are statistically indistinguishable from BF16 on that corpus. The ~4B non-expert/control weights are roughly 20x more quantization-sensitive per parameter than the 121B routed-expert pool.
5. The Baekpica/ds4 SSD-PLE project has now crossed from isolated correctness into integrated serving. Its Q5 variant (77.55 GiB resident compute + BF16 PLE sidecar) runs full 48-layer prefill/decode on a DGX Spark with a 262K-configured server; at 5.38K prompts it measures 154.6 tok/s prefill / 34.9s TTFT / 18.7 tok/s decode, and at 21.0K prompts 149.1 tok/s prefill / 141.3s TTFT / 18.8 tok/s decode. Increasing the bounded PLE cache from 512 MiB to 2 GiB produced only ~0.6% prefill improvement on the tested workload.
6. No controlled direct 2x M1 Max Flash-Next benchmark has surfaced yet. The key remaining uncertainty for the user's 2x64GB M1 Max setup is distributed execution efficiency, not model viability or SSD-PLE feasibility.

## Apple runtime result closest to MXFORGE

Source: `ddalcu/Qwen3.8-Flash-Next-MLX-Serve-mixed-4-8bit`.

Reported M4 Max 128GB configuration:

- routed experts: 4-bit group 64;
- attention / GDN / hyper-connections / indexer / shared experts: 8-bit group 64;
- lm_head: 8-bit;
- embed_tokens: 4-bit;
- routers, inject gates, norms, convs, SSM state: BF16;
- native MTP head uses the same mixed policy as the trunk;
- 51.2B PLE: one **32.0GB 4-bit `ngram_table.bin`**, mmap-backed rather than loaded into MLX weights;
- per token, CPU dequantizes only the 16 selected rows and transfers the resulting 2560-vector;
- total resident footprint: roughly 75GB plus KV/state.

Current measured claims on M4 Max 128GB, mlx-serve 26.8.11:

- serial decode: ~60 tok/s;
- code with MTP: ~78 tok/s, about +41%;
- prose with MTP: about 4% slower than serial;
- one 8.5K-prompt MTP case: about 4% slower;
- prefill: ~730 tok/s;
- sparse-attention needle at ~24.8K recovered;
- prefix cache enabled.

This result replaced an earlier first-port figure of ~29-34 tok/s decode / ~400 tok/s prefill, demonstrating how immature and tunable the runtime still is.

### Relevance to 2x M1 Max

Official Apple bandwidth:

- M1 Max 32-core GPU: 400 GB/s;
- top M4 Max 40-core GPU: 546 GB/s.

A single M4 Max at 60 tok/s does **not** imply 2x M1 Max will exceed 60 tok/s. The M1 pair cannot be treated as one 800 GB/s memory pool because inter-node communication and PP/TP bubbles matter. The later M1 Ultra measurements in the resolution update below are now the better same-generation anchor.

## Direct Apple SSD-PLE evidence

A separate M5 Max 128GB user modified the Unsloth UD-Q4_K_XL GGUF layout so PLE tensors are no longer interleaved with Metal-wired tensors. With default mmap behavior:

- wired memory before layout fix: ~123GB including OS;
- after fix: ~97GB;
- roughly 26GB of wired footprint removed;
- decode stayed ~36 tok/s without MTP.

This is direct evidence that the Apple SSD/mmap PLE tier can be effectively throughput-neutral for decode when the tensor layout permits the OS to page the table independently.

It also confirms the packaging rule already identified by MXFORGE: PLE should be a first-class sidecar / independently pageable region, not mixed into accelerator-resident shards.

## Quant sensitivity: important correction to generic Q4/Q5 thinking

PipeNetwork tested BF16, 8-bit, 6-bit, uniform 4-bit, and a mixed 4/8-bit MLX build over 296,815 WikiText-2 tokens / 145 windows.

| Build | PPL | Delta vs BF16 |
|---|---:|---:|
| BF16 | 4.4708 | baseline |
| 8-bit | 4.4749 | statistically indistinguishable |
| 6-bit | 4.4767 | statistically indistinguishable |
| mixed 4/8 | 4.5286 | +1.3% |
| uniform 4-bit | 5.3914 | +20.6% |

The mixed 4/8 recipe uses:

- 121B routed experts at 4-bit;
- sensitive non-expert weights (attention, DeltaNet, hyper-connections, shared experts, embeddings, lm_head) at 8-bit;
- tiny router/control set at BF16;
- PLE at 4-bit group 32.

Ablations show that no single sensitive group explains the loss; hyper-connection gates and attention/DeltaNet paths each account for a large fraction. The conclusion for MXFORGE is strong:

> Do not define the production quant by one global bit-width. Spend precision on the ~4B sensitive always-active/control path and compress the 121B routed expert reservoir more aggressively.

## Baekpica Q5 SSD-PLE integrated serving

The dedicated ds4 implementation now has a Q5 variant with:

- resident compute payload: 77.5456 GiB;
- BF16 PLE sidecar: 95.3682 GiB;
- Q4_K / Q5_K / Q5_0 routed expert tiers;
- bounded PLE cache and O_DIRECT sidecars;
- full 48-layer prefill/decode serving on one DGX Spark.

Measured under a 262,144-token configured server and no prefix-cache reuse:

| Prompt | Prefill | TTFT | Decode |
|---|---:|---:|---:|
| ~5.38K | 154.6 tok/s | 34.91 s | 18.7 tok/s |
| 21,037 | 149.1 tok/s | 141.28 s | 18.8 tok/s |

A 512 MiB vs 2 GiB PLE cache A/B at 21K changed prefill only ~0.6%, suggesting very large explicit PLE caches may not be necessary for at least this workload.

Caveats: MTP, full 262K prompt characterization, full-model quant quality, multi-sequence batching and SSD latency percentiles remain pending.

## Updated MXFORGE implications — initial afternoon view

### Quant target

Initial direction before the later same-day quant data:

```text
routed expert bulk        Q5 first serious quality target
                          Q4 as speed baseline
attention/GDN/QSA/HC      Q8 or protected mixed precision
shared experts            Q8-ish
lm_head                   Q8
routers/control/norms     BF16 where cheap
MTP                       Q8-ish / separately tuned
PLE cold                  Q8 production target initially
PLE reference             BF16 SSD for exactness certification
PLE hot                   dequantized FP16/BF16 or OS page cache
```

The late-day resolution update below supersedes the Q8-PLE/default-Q5 assumptions with better evidence.

### Performance forecast — initial afternoon view

The earlier M4-driven forecast was intentionally optimistic and is superseded by the late-day resolution update below. It is preserved here to show how the estimate changed as M1-generation evidence arrived.

## Late-day resolution update — M1 Ultra, oMLX 0.6.3, AtomicChat quant audit

The evidence available later on Aug 27 materially improves resolution and changes several planning assumptions.

### 1. M1-generation target-only anchor: optimized QSA is already present

`tarruda/llama.cpp` branch `metal-qwen4exp-split-ngram` now provides the most relevant same-generation public anchor: Qwen3.8-Flash-Next on **M1 Ultra** with an IQ4_NL compute body and a split PLE sidecar.

At 30K depth with resident PLE it reports approximately:

- prefill: **411.27 tok/s**
- decode: **27.17 tok/s**

With its direct disk-read PLE mode:

- prefill: **207.64 tok/s**
- decode: **26.06 tok/s**

Crucially, these results should **not** be dismissed as a dense-attention fallback. The branch contains a real Flash-Next QSA path and a sequence of measured optimizations:

- cached normalized/rotated QSA block keys;
- partial top-k block selection;
- batched indexed Flash Attention on Metal;
- indexed QSA prefill;
- cached QSA cell mappings;
- narrow-matrix Metal kernels;
- parallel routed-expert token mapping.

One commit reports that caching QSA cell mappings alone improved 30K decode from about **24.68 -> 29.07 tok/s** on its IQ1_S test while preserving exact QSA layout and token-by-token/chunked logits.

Therefore the M1 Ultra result is a legitimate M1-generation software anchor. It is still not a direct prediction for two separate M1 Max machines: UltraFusion is much better than Thunderbolt and the quant/runtime differ.

### 2. The current direct SSD-read path is intentionally naive enough to leave headroom

Code inspection of `llama_qwen4_ngram_data::set_input()` shows the nonresident mode loops over selected PLE row IDs and, for each row, performs a file `seek` followed by `read_raw`, then dequantizes into staging memory. It does **not** implement the whole-prompt planner MXFORGE has been considering:

```text
all prompt n-gram row IDs
    -> deduplicate
    -> sort/group by SSD page
    -> coalesce reads
    -> asynchronous double-buffered prefetch
    -> overlap with GPU prefill
```

This is strong evidence that the observed ~411 -> ~208 tok/s resident-vs-disk prefill drop is **not an optimized-SSD ceiling**. Decode is already almost insensitive to SSD because only a tiny sparse payload is required per generated token.

### 3. AtomicChat: architecture-aware 4.27 bpw may make the compute body much smaller than assumed

AtomicChat published a paired BF16-logit/KLD/PPL comparison using one reference, corpus and machine:

| Build | Resident | SSD | Total | Mean KLD | Same top-1 | PPL ratio |
|---|---:|---:|---:|---:|---:|---:|
| AD-3.84bpw-IQ4_XS-M64 | 45.8 GB | 39.1 GB | 84.9 GB | 0.2277 | 82.68% | 1.102 |
| **AD-4.27bpw-Q4_K_M-M64** | **54.5 GB** | **38.4 GB** | **92.9 GB** | **0.0842** | **89.49%** | **1.026** |
| AD-5.00bpw-Q5_K_M-M64 | 56.1 GB | 54.4 GB | 110.5 GB | 0.0837 | 89.55% | 1.026 |

On this ruler, the 4.27-bpw build is effectively tied with the 5.00-bpw build while being 17.6 GB smaller overall. This is **not proof of equal SWE-bench/agent quality**; MXFORGE must certify the recipe on the frozen coding ruler and broader coding tasks before promotion.

The recipe is architecture-aware rather than globally Q4:

- PLE: `Q5_1` (~6-bit class), ~38.4 GB SSD;
- expert gate/up: `IQ2_S`, raised to `IQ3_S` in sensitive layer bands;
- expert down: `IQ4_NL`;
- everything else: `Q8_0`;
- higher-bit layer bands are asymmetric: blocks 0-3 and 40-47.

Important tensor-geometry finding: expert intermediate width is 640, which makes several ordinary K/I quant formats fall back on expert-down weights. AtomicChat reports `IQ4_NL` as the practical low-bit floor for that group in its current GGUF tooling.

If coding quality survives, a ~54.5 GB resident compute payload means a balanced two-node layer split would average only ~27 GB of model weights per M1 Max, radically increasing headroom versus the earlier ~78-91 GB compute-body assumption.

### 4. PLE Q8 is no longer the obvious production target

AtomicChat compared approximately 6-bit versus 8.5-bit PLE precision on otherwise identical builds and reports mean KLD moving by only **~0.0005**, around its measurement error. The PLE is a GET_ROWS tensor and does not receive normal imatrix statistics, but this paired test is still the best direct precision evidence available so far.

Updated MXFORGE PLE ladder:

1. **BF16 SSD** — correctness ruler / offload exactness.
2. **Q5_1 / ~6-bit SSD** — first serious production candidate.
3. **Q8 SSD** — quality control if Q5_1 fails coding certification.
4. Lower precision only after explicit coding/agent quality testing.

A ~38 GB PLE also reduces cold-read traffic versus the earlier ~48 GB Q8 assumption.

### 5. oMLX 0.6.3: native Flash-Next MTP can be much larger than the launch-day +25% result

The final oMLX 0.6.3 release includes first-class Flash-Next support, SSD-mapped PLE, prefix-state preservation and Lightning MTP.

On an M3 Ultra 512 GB with `Qwen3.8-Flash-Next-oQ4e-mtp`, fresh process, SSD-mapped PLE, no prefix reuse, same Python-code prompt and seed, 128 generated tokens, temperature 1.0/top-p 1.0, adaptive maximum MTP depth 3:

| Context | MTP off TG | MTP on TG | Speedup | Acceptance | PP on |
|---:|---:|---:|---:|---:|---:|
| 4K | 22.2 | 58.1 | 2.62x | 96.8% | 1035.9 |
| 16K | 21.9 | 53.7 | 2.45x | 97.9% | 934.1 |
| **32K** | **21.0** | **49.0** | **2.33x** | **97.8%** | **809.4** |

The PP cost of enabling MTP was only ~2.5-3.7%, with ~1.6-1.8 GiB added MLX peak memory.

This is exceptionally encouraging for coding, but it must **not** be transferred numerically to the two-M1 cluster:

- M3 Ultra is newer hardware;
- acceptance is extraordinarily high on this code prompt;
- the test uses stochastic sampling rather than the existing MXFORGE greedy certification ruler;
- distributed Thunderbolt verification can make M>1 economics much worse;
- prose/other workloads may have lower acceptance.

The correct implication is that Flash-Next MTP should be treated as a major performance workstream, not a routine 20-25% add-on. MXFORGE should sweep adaptive D1/D2/D3 separately for code and prose and optimize milliseconds per committed token.

### 6. oMLX now supplies a useful PP implementation reference

Current oMLX distributed serving uses contiguous pipeline stages, per-rank KV, Thunderbolt/Ring/JACCL support, measured per-rank compute/collective calibration and performance-aware layer rebalancing. It preserves an OpenAI-compatible API and exposes end-to-end TTFT/prefill/decode/pipeline-utilization telemetry.

That makes oMLX itself a strong implementation/control path for the first Flash-Next two-Mac PP experiment. It also reinforces the planned order:

1. PP correctness/capacity baseline first;
2. TP performance branch immediately after;
3. adaptive topology by context/workload if the measured crossover warrants it.

Our older DeepSeek V4 Flash result remains relevant: the custom two-M1 TP path reached ~17.5 tok/s while documented layer-split PP was ~13.0-13.4 tok/s, so TP cannot be dismissed. Conversely, PP is much friendlier to whole-span MTP verification because a verifier block crosses one stage boundary rather than inducing per-layer collectives.

### 7. Updated 2x M1 Max forecast

These are **forecasts, not measured Flash-Next cluster numbers**.

Assuming:

- a coding-quality-certified architecture-aware compute body roughly in the **55-70 GB resident** range total;
- Q5_1/~6-bit SSD PLE around ~38 GB, or Q8 if quality requires it;
- optimized QSA/GDN/MoE Metal paths;
- direct Thunderbolt/JACCL-class link;
- adaptive MTP that remains at least moderately profitable on coding traffic;
- PP and TP both tested rather than committing to one topology in advance;

current mature ~30K coding-context confidence is approximately:

| Sustained generation | Confidence |
|---|---:|
| **>=25 tok/s** | ~98% |
| **>=30 tok/s** | **~92-95%** |
| **>=35 tok/s** | **~75-80%** |
| **>=40 tok/s** | **~55-65%** |
| **>=45 tok/s** | ~35-45% |
| **>=50 tok/s** | ~20-25% |
| **>=55 tok/s** | ~10% |

Current center for a mature coding configuration: roughly **39-43 tok/s**.

Important downside branch: if Thunderbolt verifier economics are poor and MTP acceptance falls sharply, a mature target-only/shallow-MTP system may still land closer to **30-36 tok/s**. That is why >=30 is much higher confidence than >=40.

Important upside branch: if PP whole-span verification preserves even a meaningful fraction of the oMLX code-MTP economics, or if TP target-only repeats the topology advantage seen in the DeepSeek work while verifier communication is successfully amortized, **45-50 tok/s becomes credible rather than fantasy**.

### 8. Updated cold-prefill view

Do not use M3/M4/M5 PP numbers directly as M1-cluster predictions. The M1 Ultra 30K resident-PLE result (~411 tok/s) is now the cleaner same-generation ceiling-like anchor, while its row-by-row direct-disk mode (~208 tok/s) is a useful naive SSD floor.

If the coding-certified resident compute body really lands around 55-70 GB rather than 78-91 GB, weight traffic and memory headroom improve enough to raise the optimized-SSD target modestly:

- naive/direct SSD implementation: **~180-225 tok/s** at ~30K;
- optimized whole-prompt SSD PLE planner: **~275-350 tok/s** target band;
- hypothetical RAM-speed PLE backend: **~325-400 tok/s** target band.

For a safer/higher-precision 70-80+ GB compute body, keep the previous **~250-325 tok/s** optimized-SSD expectation.

The difference between optimized SSD and DRAM remains a reasonable price for capacity. Prefix reuse further reduces its real agent-session importance because only novel suffixes should be re-prefilled.

## Revised engineering priorities

1. **Do not build “Q5 everything.”** Start with architecture-aware tensor classes and use the AtomicChat 4.27-bpw allocation as an experimental point, not as an automatic production quant.
2. Build a BF16 PLE SSD correctness ruler, then test **Q5_1/~6-bit PLE immediately** against Q8 on the frozen coding ruler.
3. Implement the PLE sidecar as an explicit backend with a whole-prompt planner; avoid row-by-row synchronous reads during prefill.
4. Port/measure the QSA wins already demonstrated in the tarruda branch: cached block keys/cell mappings, indexed FA, partial top-k and routed-expert-map specialization.
5. Bring up **PP first**, preferably using oMLX/JACCL as a reference/control, because it simplifies layer ownership, PLE placement and whole-span MTP verification.
6. Bring up **TP immediately after** because the prior two-M1 DeepSeek result showed a real ~30%+ topology advantage for target-only decode.
7. Sweep MTP D1/D2/D3 and report local compute, wire/collective time, accepted tokens/span and milliseconds per committed token. Code and prose need separate policies.
8. Preserve exact prefix/state caches and later add SpecPrefill only to novel uncached material.
9. Quality promotion must include the frozen ~29.3K coding ruler plus broader coding/agent tests; KLD/PPL is a screening metric, not the final certificate.

## Evidence status after late-day update

- M1 Ultra ~411 tok/s PP / ~27 tok/s TG @30K with resident PLE: **direct community measurement on M1-generation silicon, optimized QSA-aware llama.cpp branch**.
- M1 Ultra direct-disk PLE ~208 PP / ~26 TG @30K: **direct measurement; code inspection shows synchronous row-by-row reads, so not an optimized-SSD ceiling**.
- oMLX M3 Ultra 32K SSD-PLE 21 -> 49 tok/s with MTP at 97.8% acceptance: **controlled release benchmark, highly encouraging but workload/hardware-specific**.
- AtomicChat 4.27-bpw 54.5GB resident / 38.4GB SSD with KLD/PPL matching its 5.00-bpw build: **paired quant-quality measurement, not yet coding-agent certification**.
- AtomicChat ~6-bit versus ~8.5-bit PLE KLD delta ~0.0005: **paired publisher measurement; makes ~6-bit PLE a serious production candidate**.
- M5 Max 64GB 85GB quant ~517.9 pp512 / 36 tg128: **direct publisher measurement but aggressive quant and short/fresh PP; useful feasibility evidence, not quality target**.
- direct **2x M1 Max Flash-Next** performance: **still forecast only**.

## Sources

- https://huggingface.co/ddalcu/Qwen3.8-Flash-Next-MLX-Serve-mixed-4-8bit
- https://huggingface.co/pipenetwork/Qwen3.8-Flash-Next-MLX-mixed-4_8bit
- https://www.reddit.com/r/LocalLLM/comments/1vz927j/got_qwen38nextflash_ngram_ssd_offload_working_in/
- https://huggingface.co/Baekpica/Qwen3.8-Flash-Next-Mixed-Quant-SSD-PLE-GGUF/commit/f77e47a8db4781db7d51e7d0e9a29ecf595a57e2
- https://www.reddit.com/r/LocalLLaMA/comments/1w08zar/custom_llamacpp_branch_with_faster_metal/
- https://github.com/tarruda/llama.cpp/tree/metal-qwen4exp-split-ngram
- https://huggingface.co/AtomicChat/Qwen3.8-Flash-Next-GGUF
- https://huggingface.co/datasets/AtomicChat/Qwen3.8-Flash-Next-GGUF-metrics
- https://github.com/jundot/omlx/releases/tag/v0.6.3
- https://github.com/jundot/omlx/blob/main/docs/distributed-cluster.md
- https://support.apple.com/en-us/111901
- https://support.apple.com/en-us/121553
