# Project 51 primary-lane research watch — 2026-09-25 14:16 ET

**Freshness boundary checked:** prior hard boundary **2026-09-25 14:59:30 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-25 18:16:37 UTC**.

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

No exact dual-M1/TB4 Flash-Next S=2-8 verifier receipt appeared, no direct Apple7 PP2 overlap measurement appeared, and no new precisely timestamped source-vs-quant xhigh behavioral certification appeared.

## Findings

### NEW — SGLang preserves mixed quantization inside a Qwen3.8 MTP draft

Source: https://github.com/sgl-project/sglang/commit/0154f72b48d54e96df7dac69bd7677156c2dc1b6  
Committed **2026-09-25 17:31:29 UTC**.

The fix is filed under Qwen3.5 MTP infrastructure, but its regression fixture explicitly uses the AMD **Qwen3.8-2.4T-A95B-Quark-MXFP4** checkpoint. That checkpoint is not uniformly quantized inside the draft:
- MTP routed experts remain **MXFP4**;
- draft attention projections remain excluded / BF16;
- shared expert, shared-expert gate and FC remain excluded / BF16.

The previous logic saw any `mtp.*` exclusion and disabled quantization for the entire MTP module. That made the loader allocate BF16 routed experts even though the checkpoint contained MXFP4 expert shards. The new logic disables draft quantization only when the routed experts themselves are excluded, while honoring the finer per-layer exclusions for sensitive modules. It also reuses the target model's packed-module mapping so fused `qkv_proj` names correctly inherit q/k/v exclusion policy.

**Classification:** NEW exact-Qwen3.8-family quant-identity/correctness evidence, cross-hardware.

**P51 consequence:** this strongly supports treating MTP precision as a **heterogeneous submodule allocation**, not a single MTP bit-width. For our Flash search, the draft expert mass can be tested at aggressive precision while attention/shared/control/head islands remain protected. Every artifact must report that map explicitly; a label like `MTP Q4` is insufficient.

There is no Flash-Next/M1 performance result in this commit, so no TG credit.

### NEW — vLLM GLM-5.3-Flash: rejected speculative drafts can corrupt a too-short side-state ring

Source: https://github.com/vllm-project/vllm/commit/2617fe938355594c48d4512a2ef6b470962aac1a  
Committed **2026-09-25 16:51:34 UTC**.

In the K-pool tail path, a speculative token can complete a pool and later be rejected. With only a one-pool tail ring, subsequent drafts overwrite earlier ring entries that are still needed when the rejected completion is redone. The fix expands the ring so it survives the speculative horizon and chooses ring sizes compatible with the main attention block. The added tests explicitly demonstrate the one-ring corruption and the two-ring safe case.

A second geometry issue is important: an awkward ring size can force cache matching onto the LCM of tail-ring and attention-block sizes, coarsening prefix reuse. The new sizing chooses a ring that both covers `KPOOL + num_speculative_tokens` and divides the attention block.

**Classification:** NEW cross-model speculative-state correctness evidence.

**P51 consequence:** stage-local recurrent/GDN/QSA/MTP scratch state needs a retention horizon derived from **rollback span + speculative width**, not merely the normal decode state size. Ring/checkpoint geometry must also compose cleanly with prefix-cache block geometry. This strengthens the existing exact-state-provenance rule.

### NEW — vLLM startup allocator fragmentation can silently shrink inferred KV capacity

Source: https://github.com/vllm-project/vllm/commit/6491f481a7c0fb3aa77bbc6649584b545c65c871  
Committed **2026-09-25 16:16:27 UTC**.

During the startup profile run, large workspaces such as MoE buffers can grow in steps, freeing earlier multi-GiB allocations. A later small allocation may be carved out of one of those freed blocks and keep the entire segment pinned beyond `empty_cache()`. The memory profiler then counts that allocator-retained segment as consumed and reduces the KV-cache allocation even though the model did not truly gain equivalent persistent memory.

vLLM now scopes a native CUDA/ROCm `max_split_size_mb=20` policy around the profile pass and restores the user's allocator settings afterward.

**Classification:** NEW cross-runtime capacity-certification evidence.

**P51 consequence:** when a context limit unexpectedly regresses, distinguish **steady live bytes, true workspace/transient bytes, memory-guard policy, and allocator-retained fragmentation**. A single startup memory-profile result is not a physical fit proof. This complements the recent oMLX context-capacity/admission warning.

### LOWER PRIORITY / no planning change

- vLLM added an AMD/PyTorch reference test for DeepSeek-V4 MoE routing. Useful CI hardening, but no new DS4 performance receipt.
- vLLM optimized low-concurrency speculative KDA for Kimi-K3 and added more uniform/ragged speculative-shape correctness coverage. It is adjacent evidence that speculative recurrent kernels should dispatch by actual row geometry, but no transferable Qwen3.8/Apple end-to-end number was attached.
- remaining in-window vLLM work was unrelated kernel/CI/frontend/runtime maintenance; llama.cpp's only in-window merge was an LFM2-audio preprocessor fix.

## Required-surface / community scan

No qualifying post-boundary performance or quality update was found on:
- **antirez/ds4**
- **jundot/omlx**
- **ddalcu/mlx-serve**
- **incoai/splash**
- **paperniuk/splash**
- **youssofal/MTPLX**
- **localai-org/apex-quant**
- **IST-DASLab/GSQ**
- **NVIDIA/Model-Optimizer**.

Current web/Hugging Face/Reddit search surfaced known recent Apple receipts, including the already-recorded M2-Max result and older M3/M5 oMLX/Splash/MTPLX work, but no precisely timestamped new M1/dual-M1 Flash receipt inside this strict window. Search/crawl freshness was not treated as evidence time.

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

`RESEARCH-STATE.md` is updated with the durable mixed-MTP-quant, speculative-state-lifetime, and allocator-capacity rules. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-25 18:16:37 UTC**
