# Project 51 primary-lane research watch — 2026-09-26 13:56 ET

**Freshness boundary checked:** prior hard boundary **2026-09-26 15:28:27 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-26 17:56:46 UTC**, plus Reddit/HF/community freshness checks.

## Decision

**No canonical TG/PP, xhigh-quality, or planning-confidence change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

This pass is unusually useful despite no target move: oMLX landed a broad speculative-decode patch explicitly covering non-NAX/fp16 Macs, while mlx-serve demonstrated two exact-Flash long-context bottlenecks that were materially larger than their component microbenchmarks suggested.

## Findings

### NEW — oMLX #3958: speculative decode gets a large non-NAX/fp16 path

Source: https://github.com/jundot/omlx/pull/3958  
Merged **2026-09-26 17:45:44 UTC**.

The patch explicitly targets Qwen3.8 speculative decode on both NAX and non-NAX devices, with fp16 support for older Apple generations.

**M2 Max 38-core / 96 GB / Qwen3.8-27B oQ4e fp16:**
- DFlash2: **20.4 -> 29.5 TG short (+45%)**
- **12.8 -> 23.0 @4K (+80%)**
- **11.8 -> 16.8 @16K (+42%)**
- **7.9 -> 18.1 @64K (+129%)**
- Lightning MTP: **19.4 -> 26.7 short (+38%)**
- **18.7 -> 23.1 @4K (+24%)**
- **15.0 -> 26.0 @16K (+73%)**
- **10.8 -> 14.2 @64K (+31%)**.

**Exact Flash-Next oQ4e Lightning MTP:**
- M3 Ultra: **105.4 -> 110.6 short; 73.6 -> 81.7 @8K; 69.5 -> 73.3 @16K; 47.6 -> 63.0 @64K (+32%)**
- M5 Max: **79.3 -> 91.1 short; 64.2 -> 77.9 @8K; 67.2 -> 75.3 @16K; 63.0 -> 66.7 @64K (+6%)**.

Important mechanisms:
- GQA-shared tensor-op verify attention;
- small tail cache for MTP-head KV rather than copying the whole head cache;
- fused single-launch GDN verify with lazy replay on commit;
- 3-bit lm_head candidate proposal + exact rescore;
- GPU-specific measured QSA score/top-k/sparse-GQA row thresholds rather than NAX=yes/no dispatch;
- MTP park/re-entry preserves head history.

Validation notes explicitly discuss **M1/M2** fp16 softplus rounding differences, but the performance table contains M2 Max 27B and M3/M5 Flash rather than exact M1/M2 Flash. Therefore this is strong **transfer evidence**, not the missing Apple7 Flash receipt.

**P51 consequence:** older Apple speculative performance can be dominated by dispatch/precision policy rather than raw silicon. Per-GPU measured thresholds, fp16 activation identity and state-preserving park/re-entry belong in the M1 implementation plan.

### NEW — mlx-serve #555: default bf16 KV was missing the fast QSA verify path

Source: https://github.com/ddalcu/mlx-serve/pull/555  
Merged **2026-09-26 15:49:52 UTC**.

Default bf16 KV at MTP widths S=2..15 previously built masks / ran repeated SDPA or union-gathered blocks instead of using the fused split-K QSA kernel.

On M5 Ultra / Flash-Next mixed4/8 + MTP:
- after 32K: median-ish control **~95.1 TG** vs fused dense arm **~106.3**
- after 64K: **~92.1 -> 103.6 TG**, about **+12%**
- GSM8K + MMLU-Pro unchanged at **113/130**.

The scheduler now bills the key budget actually read by the fused sparse kernel rather than raw KV length. Unaligned dense views are handled safely inside the kernel.

**P51 consequence:** ensure the *default* KV representation—not only experimental KV4/8—hits the optimized verifier path. Memory/admission accounting must follow physical reads, not logical context length.

### NEW — mlx-serve #539: PLE cost was mostly the synchronization it induced, not the gather itself

Source: https://github.com/ddalcu/mlx-serve/pull/539  
Merged **2026-09-26 15:35:11 UTC**.

The CPU PLE path required reading draft IDs back to the host between the draft chain and verify dispatch. The new arm no-copy wraps the entire mmapped n-gram table as a Metal-visible buffer and performs hash/EOS/gather/dequant/RNE on the GPU.

Raw-data ladder on M5 Ultra / Flash-Next mixed4/8 + MTP:
- effective ~104K-token prompt / nominal 131072 rung:
  - CPU PLE: **3377 PP / 93.06 TG**
  - GPU PLE: **3432 PP / 107.14 TG**
  - decode **+15.1%**
- fixed 8K harness: **3153 -> ~3361 PP (+6.6%)**
- trace removes roughly **0.29-0.34 ms PLE + 0.19-0.20 ms PLE sync** per round.

This corrects an earlier interpretation in P51. The raw gather looked ~1% of an MTP round, but it created a host dependency that had a much larger end-to-end cost as context grew.

**P51 consequence:** measure PLE as **compute + dependency/barrier cost**. The result does *not* mean 'resident-map 30 GB on every M1': the table is **29.8 GB** and this M5 Ultra has 256 GB. For dual 64-GB M1s, preserve the SSD-backed capacity advantage while finding a no-mid-round-host-read design (prefetched/hot GPU-visible working set, asynchronous staging, or another equivalent).

### NEW — mlx-serve #568: prefill throughput and interactive decode QoS are separate objectives

Source: https://github.com/ddalcu/mlx-serve/pull/568  
Merged **2026-09-26 15:33:19 UTC**.

A long new prefill could leave an existing decoding stream only ~3% of wall time between multi-second chunks. A configurable `prefill-decode-share` narrows chunks while decoders are live and explicitly trades newcomer TTFT for incumbent decode responsiveness.

**P51 consequence:** multi-agent certification should report both maximum PP and worst inter-token stall of an already-running agent while another request prefills. A 400-PP system that freezes an incumbent agent for seconds is not equivalent to an interactive 400-PP system.

## Community / Reddit / HF scan

No new independent **32-core M1 Max 64K/128K** result or M2 Flash-Next Splash depth curve surfaced after the prior boundary. Current search continues to return the already-recorded 24-core M1 replication, M1-Splash Part 1/Part 2, the r/oMLX long-running-agent thread and older oMLX M1/M2 discussions.

The user-supplied long-agent thread remains unchanged in its planning-grade takeaways: 14-compaction runtime survival is encouraging, but another user's 3-4-compaction semantic regression requires runtime and semantic continuity to be certified separately.

## Lower-priority strict-window activity

- SGLang reports a 6x MXFP4 MoE decode kernel win on RTX 4090 by pinning Triton `num_warps`; useful CUDA lane evidence, no Apple transfer.
- vLLM strict-window work was sparse-indexer backend correctness / host-sync cleanup / security and CI.
- paperniuk/Splash only had funding metadata changes.
- no qualifying new DS4, MTPLX, APEX/GSQ, IST-DASLab or NVIDIA Model-Optimizer result appeared.

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

`RESEARCH-STATE.md` is updated with the non-NAX/fp16 speculative-decode evidence, dense-bf16 QSA path rule, corrected PLE synchronization rule and interactive prefill/decode QoS rule. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-26 17:56:46 UTC**
