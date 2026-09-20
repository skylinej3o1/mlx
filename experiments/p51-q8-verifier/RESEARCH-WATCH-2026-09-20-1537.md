# Project 51 external runtime watch — 2026-09-20 15:37 ET

**Hard freshness window:** strictly after **2026-09-20 18:18:49 UTC** through the user's message cutoff **2026-09-20 19:37:24 UTC**.

## Decision

**No numeric TG/PP or quality-floor change.**

- production quality floor remains **>=38 AA-class**, with **39-40 preferred**;
- headline remains **40 TG @ ~128K / 400 genuinely cold PP**;
- no new exact 2x M1 Max 64 GB / TB4 / ~128K / P51 mixed-quant + MTP physical receipt appeared.

This window adds two important correctness rules for a quality-first deployment: compiled tensor layout is part of MoE routing correctness, and target/draft cache groups can have different block geometries. It also narrows—but does not close—the Splash-to-M1 Apple transfer gap.

## NEW — vLLM #57823: padded physical row stride can silently corrupt expert routing

Source: https://github.com/vllm-project/vllm/pull/57823  
Created **2026-09-20 19:03:57 UTC**; implementation commit **19:01:25 UTC**.

Inductor can produce router logits with logical shape such as `[M, 60]` but physical stride `(64, 1)`. The native MoE top-k path addressed each row as `row * num_experts`, implicitly assuming packed rows, so compiled execution read the wrong router logits whenever physical stride differed from the logical expert count.

Observed validation:

- standalone reproducer: minimum **3/33 matching rows** before; **33/33** after in all four padded-stride cases;
- compiled duplicate-prompt pairs: **0/8 -> 8/8**;
- compiled short-cycle outputs: **9 -> 0**;
- eager control: already **8/8** and zero short cycles.

**Project 51 >=38 rule:** physical layout/stride is part of quant/runtime identity. Certification must compare eager/reference vs compiled/fused execution for expert routing, including padded and alignment-expanded row layouts. A quant cannot be judged on output quality until router inputs are proven to read the same logical rows under the production compiler/kernel path.

This joins the existing QSA batch-invariance rule: both **which experts are selected** and **which sparse attention keys are selected** must be topology/layout-stable before any quality conclusion is attributed to quantization.

## NEW — vLLM #57824: MTP draft and target cache groups can have different block geometry

Source: https://github.com/vllm-project/vllm/pull/57824  
Created **2026-09-20 19:28:13 UTC**; implementation commit **19:26:05 UTC**.

A token-sized offload chunk assumes all offloaded KV groups share one tokens-per-block size. Speculative/draft groups can introduce a second block size, making token-to-block conversion ambiguous.

The PR does not pretend mixed sizes are equivalent; it points operators to `blocks_per_chunk`, which expresses offload size in each group's native blocks.

**Project 51 rule:** target, MTP/draft, recurrent/QSA and checkpoint storage geometries are separate state identities. Any sleep/offload/checkpoint layer must either:

- size/restore by each group's native block geometry; or
- normalize to a versioned canonical representation.

Never derive all groups from one target token/block conversion merely because they belong to the same request.

## NEW — Splash #43 admits Apple8 / M2 by capability rather than Apple9 generation name

Source: https://github.com/incoai/splash/pull/43  
Created **2026-09-20 18:34:25 UTC**; commit **18:33:59 UTC**.

Splash previously required Apple GPU family 9. On a tested **M2 Max 64 GB / Apple8**, the required placement-sparse-buffer capabilities and native map/unmap probe passed, so the proposed gate now accepts Apple8/9/10 while retaining capability and memory checks.

Validation on M2 Max:

- CPU and Metal engine suites pass;
- shader validation passes;
- sparse backend stress includes 256 extent-churn repetitions;
- **no real-model quality or throughput result yet**.

**Project 51 implication:** this narrows the generational distance of Splash's design evidence from M3+ to M2, but **does not create M1 evidence**. M1 remains a separate capability/kernel bring-up problem and the P51 confidence ladder does not move.

## NEW — Splash #44: telemetry must not sit on the Metal command-completion critical path

Source: https://github.com/incoai/splash/pull/44  
Created **2026-09-20 19:31:15 UTC**; commit **19:30:16 UTC**.

Splash found that GPU completion callbacks queried memory telemetry before publishing completion and stopping the watchdog. A delayed telemetry call could therefore turn already-completed GPU work into an engine timeout.

The change moves memory sampling to host-side ticket retirement before the next submission.

**Project 51 reliability rule:** profiling/telemetry may observe the serving path but must not delay the event that declares a Metal command complete. Completion, watchdog disarm and resource ownership transitions come first; memory/metrics sampling follows on a host-side path.

This matters for a premium always-on agent experience because diagnostic instrumentation must never create apparent GPU stalls.

## RECOVERED OLDER COMMUNITY EVIDENCE — PLE/n-gram precision may affect deep-context MTP acceptance

Source: https://huggingface.co/julianmb/Qwen3.8-Flash-Next-IQ4_XS-GGUF

This evidence predates the strict window and is deliberately classified as **RECOVERED OLDER EVIDENCE**.

The artifact compares an IQ4_XS trunk with:

- a **Q8_0 PLE/n-gram table** (~116 GiB total); and
- an **IQ4_NL PLE/n-gram table** (~91 GiB total).

On the same Strix Halo Vulkan lineage runtime, q8 KV and temp 0:

- <=32K, low-bit PLE can be competitive or faster;
- at **128K**, one reported run measured MTP **26.9 tok/s with Q8 PLE vs 18.6 with IQ4_NL PLE**;
- the model card explicitly labels the proposed mechanism—lower draft acceptance from accumulated PLE quantization noise—as **plausible but unverified, n=1**.

The same card later reports additional runs/variants with material spread, reinforcing that this is a qualification warning rather than a transferable speed ratio.

**Project 51 quant-strategy correction:** PLE/ngram remains separately accounted from the hot trunk because sparse lookup economics are different, but **PLE precision is not a capacity-only decision**. Qualify Q4/Q6/Q8-or-source PLE precision at 8K/32K/64K/128K using:

- target-only TG;
- MTP TG;
- acceptance by depth;
- tokens/cycle;
- draft/target disagreement;
- long-context coding/retrieval fixtures;
- the >=38 quality proxy suite.

Do not spend PLE bits merely because the table is mostly SSD-backed if those bits materially preserve long-context MTP or behavior.

## RECOVERED QUANT-QUALITY CONTEXT — held-out heterogeneous Flash quants

Source: https://huggingface.co/agentionai/Qwen3.8-Flash-Next-AP-GGUF

This older model card reports a held-out quant ladder with heterogeneous per-tensor allocation. Examples:

- AP-Q5_K_XL: effective **5.46 BPW**, KL **0.0839**, top-1 **86.63%**;
- AP-Q4_K_XL: **4.57 BPW**, KL **0.0992**, top-1 **85.71%**;
- AP-Q4_K_M: **4.27 BPW**, KL **0.1243**, top-1 **84.22%**.

These are **not AA scores** and cannot certify >=38. They do reinforce the current search plan: quality degradation is gradual across heterogeneous 4-5-bit allocations, so the production knee must be found behaviorally rather than inferred from a nominal BPW label.

## Screened / no target-changing evidence

- **vLLM #55875/#55876:** useful application-directed recurrent prefix/checkpoint grouping, including a reported 7.58x kernel microbenchmark, but substantive commits are September 9 / earlier than this window; not relabeled new.
- **DS4:** no strict-window substantive implementation commit.
- **oMLX:** no strict-window Flash implementation commit.
- **mlx-serve:** no strict-window P51 implementation commit.
- **llama.cpp:** new CUDA shared-expert/MMVQ work is not M1/Metal evidence.
- **Splash:** #43/#44 recorded above; no M1 real-model receipt.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no activity.
- **MTPLX:** no post-boundary commit.
- **APEX:** no post-boundary commit.
- Current Hugging Face scan found no newly timestamped exact M1/TB4 Flash quality/throughput receipt.

## Target impact

**No numeric change.**

The production decision remains: preserve **>=38 AA-class behavior first**, ideally **39-40**, then maximize throughput.

**New hard boundary: 2026-09-20 19:37:24 UTC.**
