# MXFORGE roadmap / research backlog

This document captures the current design ideas so they do not get lost across tuning sessions. Treat measured numbers as baselines and all forward targets as hypotheses until certified with paired runs.

## 1. Core MXFORGE thesis

Turn Apple Silicon into a model-specific inference appliance by co-designing:

- quantization / physical weight layout
- Metal kernels
- MTP/speculative verification
- prompt processing
- long-context attention/KV behavior
- runtime scheduling
- distributed topology

The goal is not merely to optimize MLX defaults. The model checkpoint, quant recipe, kernels, and scheduler should be optimized together for the target Mac generation and workload.

## 2. Qwen3.8-27B on M1 Max 64GB

Current working direction:

- preserve the current MTP-tuned champion as the reference baseline
- finish decode tuning before freezing the quant format
- independently optimize prompt processing and long-context paths
- retain high-quality weights (~6.5 bpw class) and Q8 KV where memory permits
- benchmark context bands independently rather than assuming one runtime policy wins everywhere

### Adaptive MTP/runtime policy

Investigate runtime switching by context / verification economics:

- aggressive draft depth at short context
- moderate depth at medium context
- shallow/no-MTP when long-context verification becomes too expensive
- allow different architectures for decode vs prompt processing

Track expected time per accepted/emitted token rather than acceptance rate alone.

### Verification hot path

Mine the current oMLX/Qwen Lightning-MTP work conceptually, especially:

- vectorized/block verification attention instead of serial per-row SDPA
- fused GDN verification prework
- fewer dispatches per verification cycle
- larger PP chunks where memory allows
- measure collective/sync cost per emitted token when distributed

The key optimization target is the verifier execution graph, not only draft acceptance.

## 3. M1-specific custom quant / kernel co-design

After the decode/MTP hot path stabilizes, build a hardware-in-the-loop quant search for M1 Max.

### Search dimensions

Per tensor / tensor class:

- bits: 2/3/4/5/6/8 where supported
- group size: 32/64/128
- scale/bias representation
- physical packing / alignment
- precision of LM head, embeddings, attention projections, GDN, MTP module
- separate treatment for decode-hot vs MTP-verification-hot matrices

### Objective

Do **not** optimize only perplexity vs bpw.

Optimize a Pareto frontier over:

- quality loss
- M1 M=1 latency
- M1 M=2..5 verification latency
- memory footprint
- prompt-processing latency
- long-context behavior

Use measured nanoseconds on the target M1 rather than abstract storage cost as the hardware objective.

### Quant workflow

1. Build sensitivity map once.
2. Generate many cheap mixed-precision candidates.
3. Benchmark real M1 matrix shapes / context bands.
4. Eliminate dominated recipes.
5. Apply AWQ/GPTQ/DWQ only to finalists.
6. Re-tune MTP policy after quant changes because verification economics may shift.
7. Only then specialize Metal packing/kernels to the winning representation.

## 4. Benchmark/certification protocol

Every claimed win should include:

- exact model + quant hash
- exact commit
- hardware / macOS / MLX version
- fixed prompts and output lengths
- context lengths spanning short -> long
- target-only decode and MTP-effective decode reported separately
- MTP draft depth / acceptance / accepted tokens per verification
- PP/TTFT separately from decode
- peak memory
- 10 paired runs for certification where practical
- mean / median / stdev
- wall-clock validation independent of internal reporter

Avoid adding percentage wins that overlap; certify whole-stack deltas from a fixed champion.

## 5. DeepSeek V4 Flash distributed path

Keep the current two-M1-Max tensor-parallel path as the working distributed baseline rather than replacing it with generic layer/RPC split.

Relevant concepts to mine/port from current llama.cpp DeepSeek V4 Metal work:

- sparse selected-KV packing/gather
- fused compressor/mask paths
- Q8 KV-specific decode fixes
- wide-head FA scheduling
- fused hyper-connection RMSNorm

Profile the two-node system explicitly for:

- local compute time
- collective/network time
- idle/bubble time
- indexer latency
- GPU busy percentage

A kernel win does not double merely because TP has two nodes; super-additive gains are only expected when the change also reduces communication/synchronization bubbles.

## 6. Future 100B+ Qwen MoE on 2 x M1 Max 64GB (speculative until release)

If Qwen releases a ~100-150B sparse midsize model, investigate a high-quality ~Q6-class distributed build.

Prefer a hybrid topology over blind TP:

- expert parallelism for routed experts
- TP only for shared/attention pieces where it pays
- stable expert placement per Mac
- small activation/routing transfers rather than splitting every expert matrix
- MTP verification designed to amortize cross-node synchronization

Target is interactive inference of a much larger-capacity model across 128GB aggregate unified memory without treating it like a dense 100B+ model.

## 7. Ornith 1.5 35B-A3B fast-worker path

Ornith 1.5 makes the 35B/A3B class worth revisiting as a high-throughput coding/repo worker.

Research goals:

- verify architecture compatibility with existing Qwen MoE kernels
- measure plain MLX vs oMLX/MTPLX paths on M1 Max
- test MTP graft/native compatibility
- optimize expert routing / gate-up fusion
- compare against Qwen3.8-27B on repo, terminal, and long-horizon coding tasks

Intended role if quality holds: extremely fast coding/agent worker while Qwen3.8-27B remains the stronger general local brain.

## 8. Long-context policy on M1 Max 64GB

The 64GB M1 Max should be treated as a capacity-rich target, not forced into low-bit KV compromises.

Goals:

- Q8 KV as the quality reference/default where practical
- independent PP and long-context kernel tuning
- context-dependent attention scheduling
- measure the entire curve (2K/8K/32K/64K/128K/max practical) instead of only short-context decode
- compact agent state before pathological context accumulation rather than always running at the physical maximum

## 9. Adjacent CUDA/5070 Ti research (not core MXFORGE, but useful cross-pollination)

Qwen3.8-27B on RTX 5070 Ti 16GB is a useful comparison platform and source of ideas.

Potential stack:

- ~4-bpw quality-class weights
- keep giant input embeddings in system RAM
- no vision tower for text/coding worker
- keep LM head GPU-resident
- compressed/rotated Q4 KV for ~128K-class context if quality validates
- reserve ~1.2-1.3GB VRAM for desktop/VS Code workload
- no MTP initially for simpler long-context residency
- mine FlashRT-style fused/static-graph/memory-layout work
- direct packed-KV attention rather than materializing dequantized cache

Research question: can Blackwell-specific runtime/weight-layout work turn 16GB into a stable 27B ~4bpw + ~128K appliance without sacrificing weight quality?

## 10. KV compression ideas worth tracking

Do not assume uniform cache precision is the endpoint.

Track/experiment with:

- TurboQuant/Hadamard-rotated low-bit KV
- asymmetric K vs V precision
- token-wise adaptive bit allocation
- protected anchors/recent tokens at higher precision
- low-salience history at lower precision
- selective pruning / semantic cache compression
- variable-rate / low-rank cache representations

For any sub-Q8 cache, validate specifically on long-code editing, multi-needle retrieval, instruction retention, multi-turn agent state, and reasoning at 32K/64K/96K/128K.

## 11. Productization / portability

Long-term MXFORGE should not be an M1-only bag of patches.

Potential user-facing flow:

1. detect Apple Silicon generation / memory
2. benchmark primitive matrix and attention shapes
3. select quant/layout recipe
4. select MTP/context policy
5. select PP/decode/long-context kernels
6. emit a hardware profile + reproducible benchmark report

Eventually support M1 -> M2 -> M3 -> M4 -> M5 with per-machine empirical tuning rather than hard-coded assumptions.

## 12. Immediate ordering

1. Finish/certify Qwen3.8-27B decode/MTP champion.
2. Profile and optimize prompt processing separately.
3. Profile long-context degradation and choose adaptive thresholds.
4. Port the most valuable verifier-fusion ideas.
5. Freeze hot-path shapes and begin M1-specific quant search.
6. Re-tune after custom quant changes.
7. Revisit two-node DeepSeek V4 and future large-MoE distribution with the same methodology.

---

This is intentionally a living research map. Split individual experiments into focused issues/PRs as they become concrete.
