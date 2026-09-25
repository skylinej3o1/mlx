# Project 51 primary-lane research watch — 2026-09-25 10:59 ET

**Freshness boundary checked:** prior hard boundary **2026-09-25 10:37:58 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-25 14:59:30 UTC**.

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

The fresh window adds one meaningful speculative-decoding implementation branch, LiLiCorr, but no exact dual-M1/TB4 Flash-Next receipt, no Apple7 PP2 overlap measurement, and no new source-vs-quant xhigh behavioral certification.

## Findings

### NEW — vLLM merges LiLiCorr speculative drafting

Source: https://github.com/vllm-project/vllm/commit/73a78e6f1f38e280986b81e0f2a9aa5e1ee6fe47
Committed **2026-09-25 14:08:28 UTC**.

vLLM now implements `LiLiCorrDraftModel` on top of the DFlash parallel-draft backbone. LiLiCorr does not autoregressively re-run a correction network for every draft position. Instead it:
- keeps the top-k candidate tokens from each DFlash position;
- processes the candidate lattice with one lightweight learned correlator;
- emits pairwise compatibility factors;
- then walks the precomputed scores to choose a coherent draft path.

The merged runtime supports:
- trained block sizes such as 16, with `num_speculative_tokens=block_size-1` recommended;
- shorter draft prefixes from the same checkpoint;
- greedy or probabilistic proposal sampling;
- target LM-head reuse or an owned quantized draft head;
- quantized draft convolution/correlator-support projections while keeping specific LiLiCorr QKV/factor/head tensors in floating-point model dtype.

Important limitations in the newly merged docs:
- **compatible LiLiCorr checkpoints are not published yet**;
- adaptive verification with LiLiCorr is not validated end-to-end;
- the alternate block rejection method is not LiLiCorr-validated for correctness/performance;
- draft lengths outside the trained geometry can reduce acceptance unpredictably.

Underlying NVIDIA LiLiCorr results are older than this strict window but are relevant provenance:
- **+9-19% acceptance length** over vanilla DFlash on every reported benchmark;
- correlator scoring head about **2.8% of per-block latency**;
- highest throughput in **70 of 72** evaluated settings across benchmarks and concurrency sweeps;
- H100 / Qwen3-4B and Qwen3-8B study, not Qwen3.8 Flash-Next or Apple.

Paper/project: https://research.nvidia.com/labs/nemotron/lilicorr/  
arXiv: https://arxiv.org/abs/2608.20530

**Classification:** NEW serving/runtime support plus RECOVERED OLDER algorithmic performance evidence.

**P51 consequence:** LiLiCorr becomes a legitimate future comparator to MTP/DFlash2/history lookup, especially for the CUDA 27B lane. It also reinforces the broader P51 thesis that raising accepted tokens can be worth a small learned control network if the control network is truly parallel and cheap. But give it **zero numerical credit** toward 40 TG until a Qwen3.8-compatible checkpoint and target-runtime implementation exist. Apple7 also lacks an implementation receipt.

### RECOVERED OLDER EVIDENCE — M2 Max Flash-Next oQ4e + Lightning MTP reaches 33.2 TG at 64K

Source: https://omlx.ai/benchmarks/performance/x9lkrbbx  
Benchmark date **2026-09-24**, therefore older than this pass's hard boundary.

Hardware/runtime:
- **M2 Max, 38 GPU cores, 96 GB**;
- Qwen3.8-Flash-Next-oQ4e-mtp;
- oMLX 0.7.0.dev4;
- macOS 26.6.2;
- Lightning MTP;
- code/Python benchmark context.

Depth curve:
- 1K: **244.7 PP / 38.4 TG**
- 4K: **309.1 / 36.6**
- 8K: **318.8 / 38.6**
- 16K: **309.2 / 29.5**
- 32K: **302.4 / 31.6**
- 64K: **292.5 / 33.2**, peak memory **79.8 GB**

**Classification:** RECOVERED OLDER nearer-Apple transfer evidence.

**P51 consequence:** this is more transferable to M1 than M4/M5 receipts and shows a pre-M3 Apple generation sustaining low-30s Flash MTP at meaningful context. It still cannot be mapped directly to the target because it is Apple8, 38 cores, 96 GB, oQ4e and 64K rather than Apple7/32-core/64-GB/custom-quant/128K. It modestly strengthens plausibility but does not warrant a confidence move.

### NON-QUALIFYING in-window work

- vLLM also merged model-runner cleanup and a ROCm CI fix; neither changes P51 inference economics.
- llama.cpp in-window changes were OpenCL/Vulkan/tokenizer work, not Apple/Flash/Blackwell Qwen3.8 performance evidence.
- no qualifying post-boundary issue/PR/commit appeared on DS4, oMLX, mlx-serve, Splash, the M1 Splash fork, MTPLX, APEX/GSQ, SGLang, or NVIDIA Model-Optimizer.

## Community / Hugging Face scan

Fresh web/community searches did not expose a precisely timestamped post-boundary M1/dual-M1 Flash-Next receipt or new DASLab/ByteShape/MTPLX source-vs-quant xhigh certification. Search surfaces continued to return the already-known M1 Splash work, MTPLX 2.12.0 material, and existing DFlash/GSQ/RCO artifacts; these are not reclassified as new.

## Canonical planning state after this pass

Unchanged:
- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target.
- RTX 5070 Ti 27B: **120 TG** mature target.

`RESEARCH-STATE.md` is updated with the durable LiLiCorr branch and recovered M2 receipt. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-25 14:59:30 UTC**
