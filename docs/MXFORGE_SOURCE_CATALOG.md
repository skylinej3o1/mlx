# MXFORGE research source catalog

Last updated: 2026-08-21

This catalog turns external notes into a deduplicated research index. It is not an endorsement of every benchmark claim. Results from Reddit posts and project-authored benchmarks are treated as leads until reproduced on the target hardware. The roadmap promotes only the ideas that appear technically relevant to MXFORGE.

Status legend:

- **CORE / promoted** — directly relevant and promoted into the MXFORGE roadmap.
- **CORE / already tracked** — already represented in the roadmap; source adds implementation detail or evidence.
- **ADJACENT / port ideas** — different hardware/runtime, but contains techniques worth translating.
- **FIELD REPORT / lead** — useful empirical datapoint, but not a controlled MXFORGE measurement; preserve exact configuration caveats.
- **AGENT LAYER** — affects effective capability, context reuse, or orchestration rather than inference kernels.
- **UNRESOLVED** — source could not be inspected reliably; retain as a pointer only.

## Source inventory

| # | Source | Area | Status | What to keep / MXFORGE action |
|---|---|---|---|---|
| 1 | https://www.reddit.com/r/LocalLLM/comments/1vsuf77/dflash2_speeds_qwen_38_27b_up_to_4_times/ | Qwen3.8 speculation | CORE / promoted | DFlash2 can beat native MTP on favorable short tasks, but real ~100K agent traffic in the same discussion shows the gap can collapse to a tie and memory overhead can reduce usable context. Benchmark MTP, DFlash2, DSpark/lookup on replayed workloads and compare at matched acceptance length, not sequential live traffic. |
| 2 | https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2 | Qwen3.8 DFlash2 drafter | CORE / promoted | Primary model card: block-diffusion drafter, coherent path selector, dynamic convs, lossless target verification. Treat as an alternate drafting engine, not a universal replacement for native MTP. |
| 3 | https://github.com/tarruda/llama.cpp/tree/dsv4-metal-optimizations | DeepSeek V4 Metal | CORE / already tracked | Mine sparse selected-KV packing/gather, compressor/mask fusion, Q8 KV fixes, wide-head FA scheduling, and small recurrent/norm fusions for the two-Mac DS4 path. |
| 4 | https://www.reddit.com/r/LocalLLaMA/comments/1vs7ft2/how_i_made_deepseek_v4_flash_12x_faster_on_an_m3/ | DS4 prefill + prefix cache | CORE / promoted | Two separate lessons: optimized long-context indexer kernels improve cold prefill, but exact prefix-cache reuse dwarfs that win in chat/agent use. Preserve sampled replies/tool calls byte-for-byte, expose cached-token telemetry, support session prewarming, and measure cache-hit rate. |
| 5 | https://github.com/julianmb/q38rocm | Hardware-aligned quant + MTP + reporting | ADJACENT / port ideas | Strix Halo project demonstrates hardware-aligned block quant, high-precision critical/MTP tensors, asymmetric KV, and workload-specific speculation. Also use its clear cumulative-stage/context/workload tables as inspiration for MXFORGE benchmark reporting. Do not port ROCmFP4 literally; port the co-design and reporting method to M1/Metal. |
| 6 | https://huggingface.co/peculiar-ragdoll/Qwen-Sharp-Chat-Templates | Prompt/template stability | AGENT LAYER / promoted | The important infrastructure idea is thinking retention / stable serialization so subsequent turns can hit the prefix cache instead of invalidating it by deleting prior thinking blocks. Benchmark exact prompt-template stability separately from the template's quality claims. |
| 7 | https://www.yukon.org/mlxfast | Apple Qwen3.8 MTP challenge | CORE / promoted | Major signal: the leaderboard moved from roughly serial-level decode to a much higher regime, and the current leaders use a custom MTP head plus runtime/kernel work. Do not transfer leaderboard TPS directly to M1; do promote **custom MTP-head optimization/training** to a first-class workstream. |
| 8 | https://github.com/Layr-Labs/qwen-3.8-mtp-challenge | Qwen3.8 MTP harness | CORE / promoted | Primary harness behind the challenge. The editable surface explicitly includes MTP head weights, draft schedule 0..8, runtime, and Metal kernels. Useful model for a reproducible MXFORGE MTP-head laboratory. |
| 9 | https://www.reddit.com/r/oMLX/comments/1vrnxru/new_omlx_with_npu_released_qwen_38_27b_mtp_on_m5/ | ANE prefill | CORE / already tracked | Community evidence that ANE-assisted Qwen3.8 prefill and Lightning MTP can coexist across long contexts. Hardware is M5 Max, so use only as evidence for architecture, not M1 performance prediction. |
| 10 | https://github.com/ARahim3/mlx-dspark | DFlash/DSpark on MLX | CORE / promoted | Especially valuable: runtime measures each machine's drafter/verify cost curves and derives a local draft cap; speculative speedup is non-monotone in quant precision. Borrow the hardware-local autotuning philosophy and benchmark DFlash2 vs native MTP on M1. |
| 11 | https://www.reddit.com/r/LocalLLM/comments/1vsk8sb/prefilloptimized_qwen38_27b_nvfp4_quant/ | Blackwell-native quant | ADJACENT / promoted | Shows a quant format can be chosen for **prefill execution efficiency**, not just size/quality. Follow primary model below. |
| 12 | https://huggingface.co/akopytko/Qwen3.8-27B-NVFP4-GGUF | Blackwell-native N4_0 | ADJACENT / promoted | Primary model card reports materially faster Blackwell prefill at similar 4-bit footprint, with an embedded quantized MTP head. Important 5070 Ti candidate and conceptual precedent for M1 hardware-native quant/layout design. Quality is below strong Q4/Q6 references, so speed must be weighed against fidelity. |
| 13 | https://www.reddit.com/r/OpenSourceAI/comments/1vs0p2v/deepseek_v4_flash_went_from_6742_to_8202_with_one/ | Coding-agent orchestration | AGENT LAYER | Points to Autoprompt: plan/build/test/review/repair orchestration can raise task success substantially at the cost of more time/tokens. Keep separate from inference benchmarks. |
| 14 | https://github.com/Spielewoy/autoprompt-skill | Coding-agent orchestration | AGENT LAYER | Primary project reports 60/89 -> 73/89 on its OpenCode Terminal-Bench 2.1 comparison; project itself notes estimated ~3x time / ~2x tokens were not retained measurements. Candidate appliance/harness experiment, not an inference optimization. |
| 15 | https://www.reddit.com/r/LocalLLM/comments/1vsyf0k/nearly_3_longer_context_on_a_single_rtx_5090/ | Runtime memory structures | CORE / already tracked for CUDA | FlashRT-style optimized kernel/weight structures reclaim memory that can be spent on KV/context. Do not multiply our 5070 Ti context target by the headline factor; measure reclaimed VRAM under our no-MTP stack. |
| 16 | https://github.com/flashrt-project/FlashRT | Static graphs + CUDA kernels | CORE / already tracked for CUDA | Mine static whole-forward graphs, fused kernels, direct packed-cache paths, hardware dispatch, and memory-residency discipline for the 5070 Ti comparison stack. |
| 17 | https://anbeeld.com/articles/kv-cache-quantization-benchmarks-for-long-context | KV precision | CORE / promoted | Strong reason to test asymmetric K/V precision and tail-sensitive metrics. For the 5070 Ti, K5/V4-ish is the current capacity-balanced target, K5/V5 quality-balanced, and Q4/Q4 a capacity mode rather than automatic default. Exact codecs differ by runtime, so certify locally. |
| 18 | https://github.com/jundot/omlx/pull/2756 | Heterogeneous Apple prefill | CORE / promoted | Dual-ANE + GPU prompt processing validates a separate PP execution architecture. Follow-ups extend Qwen3.8 and CPU+ANE+GPU work sharing. This is a major MXFORGE PP branch; decode/MTP verification should remain independently optimized. |
| 19 | https://www.reddit.com/r/LocalLLaMA/comments/1vt0g7a/someone_apparently_cracked_dual_anegpu_prefill_on/ | ANE prefill on older Apple Silicon | CORE / promoted as evidence | Anecdotal but useful: reports a gain on M1 Pro/9B, suggesting the architecture is not M3/M5-only. Memory overhead is large. Measure M1 Max topology, optimum fraction, and resident-memory cost directly. |
| 20 | https://anbeeld.com/articles/kv-cache-quantization-standard-vs-qat-gemma-4-31b | KV-aware QAT | CORE / long-term | Important research direction: a QAT checkpoint can be much more tolerant of low-bit KV. Not Qwen evidence, but suggests future MXFORGE training could co-optimize **weights for the intended cache codec**, potentially moving the Q4/Q5/Q6 frontier. Lower priority than post-training/runtime wins. |
| 21 | https://www.reddit.com/r/LocalLLaMA/comments/1vrw4sz/i_pushed_qwen3827b_to_124_tps_on_a_single_request/ | Qwen3.8 verifier/speculation hot path | ADJACENT / promoted | Very high-value idea mine: draft vocabulary measured from the model's own outputs; separate calibrated quant of lm_head + MTP module; split-KV attention for multi-row verification; lower-overhead sampling; optional KVarN cache. Port the *principles* to Metal rather than the CUDA/Triton code. |
| 22 | https://github.com/syv-ai/qwen38-27b-rtx3090 | Primary implementation for #21 | ADJACENT / promoted | Primary repo confirms the single-user stack and, importantly, documents failed experiments too. Treat lm_head/MTP module/verify attention as independent hot components and benchmark them separately. Fine-tuning its MTP head reportedly did not help there, so custom-head training needs its own Apple/Qwen challenge evidence rather than assumption. |
| 23 | https://huggingface.co/turboderp/Qwen3.8-27B-exl3 | 5070 Ti EXL3 control | CORE / already tracked for CUDA | 2.0-6.0 bpw branches exist. Keep 4.00 bpw as a high-performance ExLlama/CUDA **control**, but no longer assume it is the primary 5070 Ti fit after the smaller Dynamic 3.0 UD-IQ4_XS appeared. Measure actual loaded VRAM residency with CPU input embeddings rather than infer it from checkpoint file size. |
| 24 | https://x.com/0x0SojalSec/status/2089418544312381462 | Unknown | UNRESOLVED | X page did not expose retrievable content during cataloging. Keep the pointer; do not infer a claim from it. |
| 25 | https://github.com/Tiger3807861189/J-Space-Cognition-Suite-V3.6/blob/main/README.md | Agent state / cognition protocol | AGENT LAYER | Interesting for selective workspace loading, durable external task state, verification/recovery, and avoiding context pressure. Benchmark claims are project-reported and should not be conflated with base-model capability. Potential complement to prefix-cache/context-discipline work. |
| 26 | https://github.com/antirez/ds4/issues/607 | Two-M1-Max DS4 field report | CORE / promoted | Directly relevant 2×M1 Max 64GB Thunderbolt PP measurements (~10–13 tok/s decode), coordinator ownership bug, and transient long-prefill memory regression. Important correction: its reported ~51.3 GiB Metal working-set ceiling was a configured/runtime ceiling, not proof of the machine's physical fit limit. Use for certification and PP comparison, not as evidence that DSpark cannot fit. See `docs/research/DS4_ISSUE_607.md`. |
| 27 | https://github.com/antirez/ds4/pull/835 | Distributed DSpark/MTP PP speculation | CORE / promoted as idea mine | Adds prefix commits, fused speculative spans, whole-block verify and small-batch kernels to two-node PP. Its own measurements show PP+DSpark only ~13.4 tok/s on code and report TP speculation was abandoned on that hardware because multi-row TP verify communication was too expensive. Mine the protocol ideas while keeping TP as our primary topology. |
| 28 | https://huggingface.co/unsloth/Qwen3.8-27B-GGUF | Dynamic 3.0 Qwen3.8 quants | CORE / promoted for CUDA | Current model card lists **UD-IQ4_XS at 14.3 GB** and a separate MTP Q4_0 sidecar at 1.37 GB. Unsloth reports Dynamic 3.0 >10% better top-1%-tail accuracy at matched size versus its comparison set; treat that as vendor-reported until independently reproduced. Make UD-IQ4_XS the primary 5070 Ti fit/quality candidate, with EXL3 4.00 as the speed control. |
| 29 | https://docs.vllm.ai/en/stable/features/disagg_prefill/ | Disaggregated prefill / scheduling | ADJACENT / reference architecture | vLLM can place prefill and decode in different instances and use different parallel strategies such as TP and PP while transferring KV. Mine scheduler, cache, telemetry, prefix/chunked-prefill and serving ideas; do not replace the specialized Metal core with vLLM. |
| 30 | https://nvidia.github.io/TensorRT-LLM/features/disagg-serving.html | KV mobility + topology transformation | ADJACENT / reference architecture | TensorRT-LLM documents KV cache transfer and **cache-layout transformation across different parallel strategies**, including a TP2 prefill -> PP2 generation example. Strong architectural precedent for MXFORGE TP<->PP KV migration without full re-prefill; port the concept, not CUDA/TensorRT. |
| 31 | https://arxiv.org/html/2605.06241v2 | Reasoning post-training / ReasonMaxxer | CORE / promoted research | Strong evidence that, on the paper's verifiable math tasks, much RLVR benefit can be recovered by sparse steering of high-entropy branch decisions with a small LoRA rather than full online RL. Do not generalize the title to all capability learning. MXFORGE should test frozen Qwen3.8 + rank-16/32 QLoRA on automatically verified coding trajectories, comparing positive SFT, success/failure contrastive tuning, and entropy-targeted ReasonMaxxer-style updates. See `docs/research/REASONMAXXER_QLORA_REASONING.md`. |
| 32 | https://github.com/geodesia-ai/geodesia-kv | Adaptive mixed-precision KV | CORE / promoted research | Strong architectural lead: per-64-token-block variable precision with a monotonic `{16,8,4,2,centroid}` ladder, attention-mass/distortion allocation, and fused mixed-bit attention. Port the idea to Metal rather than the CUDA implementation. Interpret “no information loss” as no token-position eviction, not numerical losslessness. Current validation is not Qwen3.8 GDN or DeepSeek MLA and does not establish a tok/s win on our hardware. See `docs/research/GEODESIA_KV.md`. |
| 33 | https://www.reddit.com/r/LocalLLaMA/comments/1vunqoz/llamacpp_dspark_pc_tree_fork_up_to_3295_faster/ | DSpark Parent-Conditioned Drafting Tree fork | CORE / promoted as idea mine | First-shot llama.cpp PCTree implementation. RTX 5090 result is more important for its shape than its headline: k3/N16 beat linear DSpark n3 by only ~2.16% overall while k4/N22 had still higher acceptance but lower throughput, proving verifier cost can dominate acceptance. Qwen3.8-27B Q4 was reported worse with k2-k4; DeepSeek Flash was not yet tested. MXFORGE action: tiny hardware-cost-aware **Micro-PCTree**, k=2 first, N=3..8, equal target-row budgets. See `docs/research/DS4_MICRO_PCTREE.md`. |
| 34 | https://arxiv.org/abs/2608.02123 | PCTree paper | CORE / promoted research | Primary PCTree paper: reuses DSpark's learned conditional structure to score multiple parent-consistent continuations without retraining or extra backbone passes. Reported matched-DSpark gains vary 3.1%-29.5% on Qwen3 4B/8B/14B; at B=16 on Qwen3-4B, acceptance length rose 9.41->11.16 and AR speedup 6.14x->6.60x. For TB4 TP, port the principle, not the large verification tree. |
| 35 | https://www.reddit.com/r/LocalLLM/comments/1vupm6p/qwen3827b_6bit_macbook_m4_pro_259_toks/ | Qwen3.8-27B 6-bit Apple field report | FIELD REPORT / lead | Fresh M4 Pro report claims **25.9 tok/s** with a tuned 6-bit Qwen3.8-27B setup. Public text confirms the author experimented with settings for a speed/quality balance, but the screenshot/config is not yet sufficient for a controlled comparison. Preserve as a Q6 Apple reference point; do not transfer it to M1 without matching quant, runtime, MTP, context and KV settings. |
| 36 | https://www.reddit.com/r/LocalLLM/comments/1vuptie/qwen3827b_6bit_on_a_macbook_m4_pro_48_gb_vision/ | Qwen3.8-27B 6-bit Apple vision field report | UNRESOLVED | User-supplied fresh report title states **M4 Pro 48GB, 6-bit, vision enabled, 21.6 tok/s**. The page could not yet be retrieved reliably for exact runtime/MTP/KV/context details. Keep it as a pointer and do **not** infer that the 25.9->21.6 difference is a pure vision penalty until the configurations are matched. |

## Dedupe / relationship map

### Qwen3.8 speculative decoding

Sources 1, 2, 7, 8, 10, 21, 22, 33, and 34 all point at the same deeper conclusion: the winning question is not "MTP or DFlash?" in the abstract. The runtime should choose among draft mechanisms, depths, and now small parent-conditioned branch shapes using measured target-verification cost, drafter cost, acceptance/rejection-depth distribution, memory headroom, context length, and workload type. Custom MTP-head weights are explicitly in scope. PCTree strengthens the rule that **higher acceptance is not automatically higher throughput**.

### Apple prompt processing

Sources 4, 6, 9, 18, and 19 split the problem into two independent levers:

1. **Make cold prefill faster** with specialized GPU kernels and heterogeneous ANE/GPU/CPU execution.
2. **Make cold prefill rare** with stable prompt serialization, exact prefix reuse, session affinity, prewarming, and cache-hit telemetry.

For agentic coding, the second lever can dominate the user experience.

### Hardware-aware quantization

Sources 5, 11, 12, 21, 22, 23, 28, 35, and 36 support quantization as an execution-layout problem, not only a bpw/quality problem. Critical tensors (LM head, embeddings, recurrent state, MTP module, attention projections) can deserve different treatment from bulk weights. Dynamic 3.0 is another external example of spending bits non-uniformly to improve the quality/size frontier; MXFORGE adds measured target-hardware latency and verifier shape to that objective. The M4 Pro Q6 reports are field observations only and must be normalized for runtime, vision projector, MTP, context and KV before drawing architectural conclusions.

### DeepSeek V4 distributed adaptive runtime

Sources 3, 4, 26, 27, 29, 30, 33, and 34 support a broader design than one fixed TP/PP choice. Tune TP, PP, small-MTP, linear DSpark, **Micro-PCTree**, and target-only paths independently, then construct a context/workload phase diagram. Same-topology drafter swaps can be cheap; TP<->PP transitions require explicit KV migration/repartition economics. Datacenter disaggregated-serving systems validate phase-specific parallel strategies and movable KV state even though the Metal implementation will be custom.

### RTX 5070 Ti Qwen3.8

Sources 12, 15-17, 23, and 28 define the current bakeoff. **UD-IQ4_XS Dynamic 3.0 is now the primary fit/quality candidate**, EXL3 4.00 is the optimized CUDA speed control, and N4_0/NVFP4 is the Blackwell prefill-speed experiment. Keep MTP optional initially so context capacity can be measured cleanly.

### Long-context KV

Sources 15-17, 20-23, 28-30, and 32 suggest a ladder rather than one universal cache mode: ordinary high-quality asymmetric K/V at normal long context; more aggressive codecs only when capacity requires them; **heterogeneous block precision that preserves recent/salient history at higher precision while monotonically demoting colder blocks**; topology-aware cache mobility for distributed transitions; and eventually KV-aware training if the quality frontier is worth moving. Geodesia-KV is an architecture lead here, not direct evidence for Qwen3.8/Metal or DS4/MLA.

### Reasoning adapters / cheap post-training

Source 31 adds a new orthogonal axis: improve **behavioral branch selection** while keeping the foundation model frozen. The first MXFORGE experiment should use automatically verified coding outcomes and small QLoRA adapters, then require held-out pass@1 gains and broad-regression checks before promotion. Keep reasoning-effort prompting, adapter effects, and inference/speculation changes independently measurable because each can alter output distributions and speculative acceptance.

### Agent-system layer

Sources 6, 13, 14, and 25 are not inference-engine optimizations. They may still materially change cost per completed engineering task through better state continuity, selective loading, review/repair loops, and cache-friendly prompt structure. They should be benchmarked separately from tok/s.

## Research hygiene

For every imported idea:

- reproduce on the actual target hardware before promoting a performance number;
- distinguish short synthetic prompts from long agent traffic;
- replay identical prompts when comparing speculative modes;
- log accepted tokens / verification, draft cost, context length, cache-hit rate, peak memory, and wall-clock time;
- separate cold-prefill, warm-prefix delta-prefill, target-only decode, and effective speculative decode;
- preserve failed experiments in notes so the project does not rediscover them later;
- record transition costs for adaptive runtimes, including weight reload, KV migration/repartition, and break-even future work;
- for reasoning-adapter experiments, keep a frozen held-out suite and report pass@1/pass@k, tool validity, token/time cost, general-task regressions, and KL/drift diagnostics;
- treat project-authored quality/agent benchmark claims as hypotheses until independently reproduced;
- for user-supplied field reports, preserve the original URL and exact claimed configuration, and explicitly mark missing variables rather than silently normalizing unlike runs.
