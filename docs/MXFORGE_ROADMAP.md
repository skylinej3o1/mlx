# MXFORGE roadmap / research backlog

This document captures the current design ideas so they do not get lost across tuning sessions. Treat measured project numbers as baselines and all forward targets or external results as hypotheses until certified with paired runs on the target hardware.

Companion source index: [`MXFORGE_SOURCE_CATALOG.md`](MXFORGE_SOURCE_CATALOG.md).

## 1. Core MXFORGE thesis

Turn Apple Silicon into a model-specific inference appliance by co-designing:

- quantization / physical weight layout
- Metal kernels
- MTP/speculative drafting and verification
- prompt processing
- long-context attention / KV behavior
- prefix-cache and agent-session behavior
- runtime scheduling
- distributed topology

The goal is not merely to optimize MLX defaults. The model checkpoint, quant recipe, kernels, speculative apparatus, cache policy, prompt layout, and scheduler should be optimized together for the target Mac generation and workload.

For agentic use, optimize **time-to-action / time-to-completed-task**, not only raw decode TPS. That means measuring cold prefill, warm-prefix delta prefill, cache-hit rate, tool latency, effective speculative decode, compaction cost, memory headroom, and correctness together.

## 2. Qwen3.8-27B on M1 Max 64GB

Current working direction:

- preserve the current certified MTP-tuned champion as the reference baseline
- finish/decompose the decode hot path before freezing a custom quant format
- independently optimize prompt processing and long-context paths
- retain high-quality weights (~6.5 bpw class) and Q8 KV where memory permits
- benchmark context bands independently rather than assuming one runtime policy wins everywhere
- keep target-only decode separate from effective emitted TPS with speculation

### Adaptive speculative policy: MTP, DFlash2, DSpark, lookup

Do not turn "MTP vs DFlash2" into a permanent global choice.

Build a hardware/workload-local policy that can choose or tune:

- native MTP draft depth / confidence threshold
- DFlash2 where its acceptance gain pays for a separate drafter and extra memory
- DSpark when it wins on a particular model/quant
- lookup/context-copy drafting for code-edit/refactor workloads that reproduce existing context
- non-drafting rounds when verification economics are unfavorable

Inputs to the policy should include:

- measured drafter latency
- target verification latency for M=2..8
- accepted tokens per verification
- recent acceptance distribution
- context length
- free unified memory
- content class (code/copy-heavy, structured output, reasoning prose, etc.)

Benchmark speculative methods on **identical replayed prompts** and compare within matched acceptance bands. Sequential live agent traffic is too confounded by workload drift.

### Custom MTP head: promoted to first-class workstream

The current Qwen MLX challenge makes the MTP head weights, drafting code, draft schedule, runtime, and Metal kernels all part of the editable surface, and the leading solutions use a custom MTP head. This is enough evidence to treat head optimization as a major unexplored axis rather than assuming the shipped head is fixed.

Research path:

1. Reproduce the challenge harness locally and understand the head contract.
2. Measure the stock head on our exact Qwen3.8 quant and M1 Max.
3. Separate gains from head weights, draft schedule, verifier kernels, and runtime changes.
4. Train/calibrate candidate heads on traffic representative of coding/agent workloads, not generic web text only.
5. Optimize acceptance **and** head cost; a more accurate but slower head can lose.
6. Keep target verification authoritative so speculation remains lossless.

Do not transfer leaderboard TPS directly to M1 Max; use the challenge as proof that the head is an optimizable component.

### Verification hot path

Continue mining oMLX and CUDA implementations conceptually, especially:

- vectorized/block verification attention instead of serial per-row SDPA
- split-KV style attention scheduling for M>1 verification so available cores are actually occupied
- fused GDN verification prework
- fewer dispatches per verification cycle
- specialized M=2..8 quantized matmul kernels
- lower-overhead sampling / top-k / top-p once model compute is no longer dominant
- separate optimization / quantization of LM head and MTP module
- measure collective/sync cost per emitted token when distributed

The optimization target is the **entire verifier execution graph**, not only draft acceptance.

## 3. Prompt processing: accelerate it and avoid it

Prompt processing is now a first-class MXFORGE workstream because agentic coding is input-heavy. There are two independent strategies and both matter.

### A. Make cold prefill faster: heterogeneous execution

oMLX's ANE work demonstrates the architecture we want to test:

- fixed-size prefill chunks
- output-channel partitioning of large projections
- GPU suffix running concurrently with ANE work
- fused merge / activation
- separate handling of MLP and GDN projections
- eventually CPU/AMX + ANE + GPU three-way work sharing
- hardware-local tuning of the fraction assigned to each engine

For M1 Max specifically:

1. Probe actual ANE topology / usable instances rather than assuming M3/M5 behavior.
2. Establish GPU-only PP baselines by chunk size (1K/2K/4K/8K where practical).
3. Port or reproduce the eligible Qwen3.8 ANE path.
4. Sweep ANE/GPU fractions independently for MLP and GDN.
5. Test CPU/AMX participation only after ANE/GPU is stable.
6. Record steady-state and peak unified memory; heterogeneous PP can duplicate weight representations.
7. Keep decode and MTP verification on their separately optimized GPU path unless measurement proves otherwise.

A community M1 Pro result suggests the ANE/GPU concept can help first-generation Apple Silicon, but this must be measured directly on the 64GB M1 Max.

### B. Make cold prefill rare: prefix-cache discipline

For persistent agents, this may matter more than another 20-40% of raw PP throughput.

Add explicit runtime goals for:

- session affinity to a resident KV/prefix cache
- exact byte/token replay of assistant replies and tool calls
- stable system prompt, tool schema, and chat-template serialization
- retaining prior thinking blocks when removing them would invalidate the prefix
- prewarming a session without sampling an extra token where the serving API permits it
- cache eviction visibility and rewarm support
- cached-token / uncached-token telemetry on every request
- compaction that deliberately creates a smaller new stable prefix and then grows incrementally again

Measure:

- prefix-cache hit rate
- cached tokens vs newly prefetched tokens per turn
- warm TTFT vs cold TTFT
- number and cost of >32K / >50K cold prefills during a real coding-agent session

A large logical context should not imply re-prefilling that entire context every turn.

## 4. M1-specific custom quant / kernel co-design

After the decode/MTP hot path stabilizes, build a hardware-in-the-loop quant search for M1 Max.

### Search dimensions

Per tensor / tensor class:

- bits: 2/3/4/5/6/8 where supported
- group size: 32/64/128
- scale/bias representation
- physical packing / alignment / block geometry
- precision of LM head, embeddings, attention projections, GDN/recurrent state, and MTP module
- separate treatment for decode-hot vs MTP-verification-hot matrices
- layouts that map cleanly to the exact SIMD/threadgroup behavior of the M1 GPU
- possible secondary representations for ANE/CPU PP only when the memory trade is justified

Cross-hardware work on ROCm and Blackwell reinforces the principle: a quant format is an **execution format**, not just a storage format. Hardware-aligned blocks and selectively higher precision for critical tensors can outperform generic mixed quants even at similar bpw.

### Objective

Do **not** optimize only perplexity vs bpw.

Optimize a Pareto frontier over:

- downstream quality loss / KLD / task accuracy
- M1 M=1 latency
- M1 M=2..8 verification latency
- acceptance with the chosen MTP head
- memory footprint
- prompt-processing latency
- long-context behavior

Use measured nanoseconds on the target M1 rather than abstract storage cost as the hardware objective.

### Quant workflow

1. Build sensitivity maps once, including LM head/MTP-specific calibration on model hidden states.
2. Generate many cheap mixed-precision candidates.
3. Benchmark real M1 matrix shapes at M=1 and the actual verification widths.
4. Eliminate dominated recipes.
5. Apply AWQ/GPTQ/DWQ or other calibration only to finalists.
6. Re-tune MTP policy after quant changes because verification economics and acceptance can shift.
7. Only then specialize Metal packing/kernels to the winning representation.

## 5. Benchmark / certification protocol

Every claimed win should include:

- exact model + quant hash
- exact commit
- hardware / macOS / MLX version
- fixed prompts and output lengths
- context lengths spanning short -> long
- target-only decode and speculative effective decode reported separately
- PP/TTFT reported separately from decode
- cold PP vs warm-prefix delta PP separately
- prefix cached tokens / new tokens / cache-hit rate for agent tests
- speculative mode, draft depth, acceptance, accepted tokens per verification, and drafter cost
- peak and steady-state memory
- 10 paired runs for certification where practical
- mean / median / stdev
- wall-clock validation independent of internal reporter

For speculative A/Bs:

- replay identical prompts rather than compare different live-agent windows
- log acceptance distribution, not only average TPS
- compare equal-context and equal-memory configurations
- include code-copy/refactor, tool-calling, structured output, reasoning prose, and long-context coding traffic

Avoid adding percentage wins that overlap; certify whole-stack deltas from a fixed champion.

## 6. DeepSeek V4 Flash distributed path

Keep the current two-M1-Max tensor-parallel path as the working distributed baseline rather than replacing it with generic layer/RPC split.

Relevant concepts to mine/port from current llama.cpp / DS4 Metal work:

- sparse selected-KV packing/gather
- fused compressor/mask paths
- optimized lightning-indexer scoring and streaming top-K for cold long-context PP
- Q8 KV-specific decode fixes
- wide-head FA scheduling
- fused hyper-connection RMSNorm

Profile the two-node system explicitly for:

- local compute time
- collective/network time
- idle/bubble time
- indexer latency
- GPU busy percentage
- prefix-cache hit / miss behavior in the actual API harness

A kernel win does not double merely because TP has two nodes; super-additive gains are only expected when the change also reduces communication/synchronization bubbles.

Also treat exact prefix reuse as part of DS4 performance. A fast long-context indexer helps cold PP; avoiding unnecessary cold PP is an independent and potentially much larger win.

## 7. Future 100B+ Qwen MoE on 2 x M1 Max 64GB (speculative until release)

If Qwen releases a ~100-150B sparse midsize model, investigate a high-quality ~Q6-class distributed build.

Prefer a hybrid topology over blind TP:

- expert parallelism for routed experts
- TP only for shared/attention pieces where it pays
- stable expert placement per Mac
- small activation/routing transfers rather than splitting every expert matrix
- MTP verification designed to amortize cross-node synchronization
- hardware-local speculation policy rather than fixed draft depth

Target is interactive inference of a much larger-capacity model across 128GB aggregate unified memory without treating it like a dense 100B+ model.

## 8. Ornith 1.5 35B-A3B fast-worker path

Ornith 1.5 makes the 35B/A3B class worth revisiting as a high-throughput coding/repo worker.

Research goals:

- verify architecture compatibility with existing Qwen MoE kernels
- measure plain MLX vs oMLX/MTPLX paths on M1 Max
- test MTP graft/native compatibility
- optimize expert routing / gate-up fusion
- test DFlash/DSpark only if a compatible drafter exists and wins locally
- compare against Qwen3.8-27B on repo, terminal, and long-horizon coding tasks

Intended role if quality holds: extremely fast coding/agent worker while Qwen3.8-27B remains the stronger general local brain.

## 9. Long-context policy on M1 Max 64GB

The 64GB M1 Max should be treated as a capacity-rich target, not forced into low-bit KV compromises.

Goals:

- Q8 KV as the quality reference/default where practical
- independent PP and long-context kernel tuning
- context-dependent attention scheduling
- measure the entire curve (2K/8K/32K/64K/128K/max practical) instead of only short-context decode
- compact agent state before pathological context accumulation rather than always running at the physical maximum
- preserve prefix-cache continuity through normal agent turns

### Longer-term: KV-aware training

The Gemma QAT cache experiments suggest a checkpoint can be trained to tolerate lower-bit KV materially better than a non-QAT checkpoint. This is **not yet evidence for Qwen3.8**, but it is a valuable future direction:

- train/fine-tune with the intended KV codec in the loop
- compare Q4/Q5/Q6/Q8 cache sensitivity against the unmodified checkpoint
- optimize for long-code/tool/agent quality, not only perplexity
- test whether a wider low-bit body beats schemes that spend similar memory on a high-precision recent-token tail

Keep this below the post-training/runtime work in priority because it is much more expensive to execute and validate.

## 10. Adjacent CUDA / RTX 5070 Ti research

Qwen3.8-27B on RTX 5070 Ti 16GB is a useful comparison platform and source of ideas.

### Weight format baseline

First serious baseline:

- EXL3 4.00 bpw
- CPU-resident input embeddings where supported
- no vision tower for text/coding
- LM head GPU-resident
- measure actual loaded VRAM rather than infer residency from checkpoint file size
- reserve ~1.2-1.3GB VRAM for desktop/VS Code workload

Also benchmark Blackwell-native NVFP4/N4_0 as a **prefill-speed** alternative. Current external results show materially better PP than conventional Q4 at similar footprint, but its published fidelity trails strong Q4/Q6 variants. It is therefore a speed/quality trade, not an automatic replacement for EXL3.

### KV ladder for ~100-128K

Current test order based on long-context KLD evidence:

1. **K5 / V4-ish** — capacity-balanced daily target, roughly aligned with ~110K-class use if runtime residency permits.
2. **K5 / V5** — quality-balanced mode if the context ceiling remains sufficient.
3. **Q4 / Q4** — maximum-capacity mode when ~128K matters more than tail fidelity.
4. More aggressive adaptive/KVarN/Turbo/TCQ modes only if needed to cross a hard memory boundary.

Exact codec names differ between ExLlama, llama.cpp, and other runtimes; benchmark the actual implementation rather than assume a nominal bit width transfers quality.

### Runtime / memory-layout work

Mine FlashRT-style ideas:

- static whole-forward CUDA graphs
- fused norm/residual/activation/quant paths
- hardware-native FP4/NVFP4 kernels
- optimized weight structures that reclaim VRAM for KV
- direct packed-KV attention rather than materializing dequantized cache
- chunked prefill and context-dependent attention kernels

No MTP is required for the first long-context residency target. Once the no-MTP baseline is stable, test native MTP only if its extra workspace/draft state does not destroy the context target.

Research question: can Blackwell-specific runtime/weight-layout work turn 16GB into a stable Qwen3.8-27B ~4bpw + ~110K daily / ~128K capacity appliance without sacrificing the desired quality floor?

## 11. KV compression ideas worth tracking

Do not assume uniform cache precision is the endpoint.

Track/experiment with:

- ordinary rotated q4/q5/q6 baselines first
- asymmetric K vs V precision, generally spending more bits on K
- TurboQuant / TCQ where they actually beat ordinary rotated codecs
- token-wise adaptive bit allocation
- protected anchors/recent tokens at higher precision
- low-salience history at lower precision
- selective pruning / semantic cache compression
- variable-rate / low-rank cache representations
- KV-aware QAT as a future model-training lever

For any sub-Q8 cache, validate specifically on long-code editing, multi-needle retrieval, instruction retention, multi-turn agent state, tool calls, and reasoning at 32K/64K/96K/128K. Include tail-sensitive distribution metrics; perplexity alone can hide rare but operationally important failures.

## 12. Agent/runtime layer: effective intelligence and context economics

Keep this distinct from inference-engine benchmarks, but track it because an appliance is a complete system.

### Cache-friendly prompt/session design

- stable Qwen chat template
- exact assistant/tool replay
- thinking retention when stripping it would invalidate a large prefix
- selective context loading instead of dumping the repo repeatedly
- durable external task state that can survive compaction/restart

### Autoprompt-style orchestration

Multi-agent planning / build / test / independent review / repair loops may increase coding success substantially, but cost more tokens and wall time. Benchmark task completion, total tokens, wall clock, and local inference occupancy; do not call an agent-harness score an inference-model improvement.

### J-Space-style state discipline

Selective workspace loading, a durable external ledger, checkpoints, explicit open questions, and recovery could reduce context pressure and improve long-horizon consistency. Evaluate as an optional agent protocol, not as a modification to model weights or MXFORGE kernels.

An eventual appliance can expose multiple modes: lightweight single-agent, durable-state single-agent, and more expensive multi-agent verification loops.

## 13. Productization / portability

Long-term MXFORGE should not be an M1-only bag of patches.

Potential user-facing flow:

1. detect Apple Silicon generation / memory
2. benchmark primitive matrix, attention, verifier, and PP shapes
3. probe ANE/CPU/GPU capabilities
4. select quant/layout recipe
5. select speculative engine/depth policy
6. select PP/decode/long-context kernels
7. configure prefix-cache/session policy
8. emit a hardware profile + reproducible benchmark report

Eventually support M1 -> M2 -> M3 -> M4 -> M5 with per-machine empirical tuning rather than hard-coded assumptions.

## 14. Immediate ordering

1. Finish/certify the current Qwen3.8-27B decode/MTP champion as the fixed whole-stack reference.
2. Reproduce the Qwen MLX challenge locally and isolate what custom MTP-head weights can buy on our hardware.
3. Add agent prefix-cache observability and a cache-stable prompt/session path; measure real cache-hit rate before chasing giant cold-PP numbers.
4. Profile/port Qwen3.8 heterogeneous PP on M1 Max: GPU -> ANE+GPU -> CPU+ANE+GPU only if the memory/performance trade works.
5. Attack verifier execution: split-KV/block verification attention, GDN prework fusion, dispatch count, LM-head/MTP-module hot tensors.
6. Benchmark native MTP vs DFlash2/DSpark/lookup on replayed short and long coding traffic and build a hardware-local speculation policy.
7. Freeze hot-path shapes and begin M1-specific hardware-aware quant search, including critical-tensor precision/layout.
8. Profile long-context degradation and choose adaptive thresholds / compaction policy.
9. On the 5070 Ti, establish EXL3 4.00 + K5/V4-ish no-MTP residency first, then compare N4_0/FlashRT-style alternatives.
10. Revisit two-node DeepSeek V4 and future large-MoE distribution with the same measurement methodology.
11. Keep KV-aware QAT and agent-orchestration experiments as separate later branches once the core runtime is stable.

---

This is intentionally a living research map. Promote individual experiments into focused branches/PRs as they become concrete, and add every external lead to the source catalog before it disappears into chat history.
