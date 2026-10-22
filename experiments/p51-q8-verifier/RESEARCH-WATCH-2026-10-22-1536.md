# Project 51 / Relay — research watch 2026-10-22 15:36 EDT

**Strict new/updated interval:** (2026-10-22 17:12:40 UTC, **2026-10-22 19:36:43 UTC**]. Prior canonical HEAD `bb0f70a786350c754c7905e761e1ef14aeec4d88`; prior report `RESEARCH-WATCH-2026-10-22-1312.md`. No owner hardware was operated or inference code changed in this pass. Every numerical claim below is a third-party physical report or author benchmark, not a measured Project51 target. All PRs are unmerged unless explicitly noted. NEW means PR created in interval, UPDATE means older PR changed in interval, RECOVERED means new to our watch but published before cutoff.

## Ranked findings

### 1. NEW physical M1 Max 64GB independent-agent state: Strata #3757 (DRAFT)

https://github.com/Niko1221/Strata/pull/3757 — created **2026-10-22 18:06:03 UTC**. **Physical M1 Max/32 GPU cores/64GB**, macOS26.5.2, Qwen3.8-Flash-Next GSQ-RCO **Q2_0** (NOT target IQ3_S); `--spec 2 --mtp` for solo, batched slots disable MTP; tested **32K window and short extra prompts**, not 128/262K genuinely occupied.

Metal slots maintain separate GDN recurrent and conv, PLE, QSA KV/scales/indexer/pooled keys, n-gram and turn checkpoint state. Two 64-token slots match solo token-for-token; 3-slot interleave and resumed turns passed; later HTTP request in middle of 220-token reply had **1.1s TTFT** while first continued. **Two-slot aggregate 15.8–17.1 decode tok/s vs single speculative ~22 tok/s**, so this improves responsiveness/concurrency, **NOT total throughput**. Extra per-slot copied state **~0.55GiB 32K, ~1GiB 64K, ~1.9GiB 128K, ~3.6GiB 256K**; these longer figures are allocation estimates, NOT physical long-agent speed. Two 256K slots **did not fit** on the M1Max64 test. No >32K batch, sampled, image, pause-mid-prefill, B3-B5 occupied128K or AA xhigh proof. Important opportunity: compare **independently resumable speculative parked streams** versus concurrently time-sliced no-MTP slots. No production IQ3_S win.

### 2. NEW Metal source-changing control vector — Strata #3756

https://github.com/Niko1221/Strata/pull/3756 — created **18:02:42Z**, OPEN, physical **M1Max64 QFN Q2_0**, 256K *configured* but speed tests only ~8.5K prefill and 300 output tokens. Opt-in steering changes generated target distribution/output; OFF matches stock (9 prompts); ON intentionally changes ordinary answers and refusal behavior. 300-token story decode ON **31.9/32.5**, OFF **33.3/33.2 tok/s** (~3% cost), PP variable **251–345 vs285–345**. Not eligible for **source-equivalent** IQ3_S xhigh verifier claims, despite native Metal feature feasibility. Do not label this a GSQ IQ3_S 256K result.

### 3. UPDATED old TB4 connection discovery but NOT merged, oMLX #3205

https://github.com/jundot/omlx/pull/3205 — originally created **2026-08-27**, closed **2026-10-22 19:02Z without merge**. Real dual-Mac direct cable, macOS self-assigned `169.254.x.x` on `bridge0`, previously filtered by oMLX transport discovery; proposed fix allows link-local candidate only after actual route and ping/TCP. **Physical ping0.4ms, identified TB4 nominal40Gb/s**, 47 unit tests on M1Max64. Neither payload transfer throughput, merged engine, source-equivalent cross-M1 GDN/QSA/PLE/MTP state, true TB4 distributed cluster decode nor CUDA-to-Metal Relay proven. Gate: actual link enumeration and bytes/second + model-continuation parity, not network candidate discovery.

### 4. NEW Strata #3760: deeper stage pipeline modest gain and rollback gates

https://github.com/Niko1221/Strata/pull/3760 — created **18:59:21Z**, OPEN. **Four GP100/Pascal dies, one host, all experts resident, Swift1.5 IQ3_S**, no M1/5070Ti/RX6800/remote transfer. Third in-flight speculative pipeline window plus stage rollback grew decode **54.22→56.12 tok/s (+3.5%)**, all replies matched, two runs per arm; with generic slower drafter +0.15%. More pipeline slots/memory and accurate rollback, but no automatic multiplicative Relay gain or cold PP speed. Treat as alternative scheduling algorithm only after actual bridge.

### 5. UPDATED older split negative control Strata #3636, Oct21 results refreshed Oct22 19:35Z

https://github.com/Niko1221/Strata/pull/3636 . Physical **Radeon AI PRO R9700 32GB + Ryzen AI MAX+395/124GB unified Strix Halo host RAM, OCuLink PCIe4x4 Radeon 8060S**, QFN IQ3_S, Strata0.2.2 Linux ROCm. **R9700 solo streaming experts from host RAM was faster than split using integrated 8060S**: genuinely 64K prefill **1,627→2,530 PP**, 200K TTFT **141→87s**, decode depth **46–49→71–74 tok/s**, B4 aggregate **82→136–140 tok/s**. Distinct hardware, not user RX6800 gfx1030+32GB and not TB4. Default `ulimit -n 1024` breaks HIP `--kv-grow` (many VMM chunks); after 85 minutes/45 requests default batch VRAM reserve ~430MiB stalled and restarted. No evidence that adding slow devices helps; require full request latency, transfer and long soak, plus RAM/VRAM margin.

### 6. NEW Splash #557 and Mirai pre-M5 status

- https://github.com/incoai/splash/pull/557 **NEW created19:35:08Z OPEN**. **M5 Max 40-core/128GB**, released dense27B and 35B models **MLX4 + DFlash2**, backend-benchmark: dense27B **190 solo decode / 594 B4 aggregate**, cold14K **909 PP**; Qwen3.6-35B-A3B **476 solo /1297 B4 aggregate**, cold14K **6069 PP**. **Advertised262K != filled262K**, no Apple M1 or source-like xhigh; no Claude CLI agent benchmark. Not an M1 target-ruler.
- https://github.com/trymirai/uzu/pull/1005 **NEW 17:22:16Z OPEN**: cancellation/explicit stream closure, fragmented Hanashi tool-call tags and exact token ID buffers for cached-prefix consistency. Good correctness mechanism, not a measured throughput change.
- https://github.com/trymirai/uzu/pull/999 + /pull/1000 + /pull/1001 UPDATED older **Qwen3.5-35B-A3B-M** Metal MoE kernels/loader, M5Pro **77.5TG /705.5PP 1357 input**, prototype/greedy test; no M1, Qwen3.6/Sage or FlashNext IQ3_S proof. uzu 0.6.13 release commit **15:41Z BEFORE cutoff**, not NEW in interval; no pre-M5 Mirai trellis native TG.
- https://github.com/Niko1221/Strata/pull/3761 **NEW DRAFT19:24:29Z** SYCL Arc Pro B70 32GB+61GiB host pinned mirror under cache pressure: drop GGUF page cache BEFORE 25.7GiB mirror alloc, restart TG **~37.5–41.4→42.4–44.5**, +1s model mirror loading. Not Metal, CUDA or HIP performance credit.
- TensorFold #1201 NEW docs-only about 3+ rank receipts not attested; older CUDA GLM5.3 paged #1163 updated but NOT QFN. No new paperniuk DS4 M1 branch commits (latest reported Oct13), owner native KVarN K4V3 full262K or exact heterogeneous state handoff.

## RECOVERED, published BEFORE this interval: user-raised MemT-1.0-Nano

https://huggingface.co/MemTensor/MemT-1.0-Nano ; https://github.com/MemTensor/MemT-1.0 ; https://github.com/MemTensor/MemT-1.0/blob/main/inference/README.md ; https://arxiv.org/abs/2610.26825 . Repository release first commit **2026-10-20 05:27Z**, last08:42Z; recovered, not new today. **Qwen3.6-35B-A3B backbone, ~36B/3B active, 451M memory-training parameters and ~10M-element FP32 (~38MiB) fixed learned dynamic memory.** Local memory + gated hyper-memory is **lossy**, independent versioned native safetensors snapshots, not an exact FlashNext KV codec. Publisher persistent storage66x smaller vs full-context KV@128K and 1.86x end-to-end speedup on MemT architecture: not occupied128K owner QQFN measurements. Official SGLang0.5.16 server **Linux NVIDIA CUDA BF16 only, quantization and chunked prefill and radix caching/CUDA graphs disabled**, example Nano TP2, no verified MLX/Metal/GGUF/Strata backend, full BF16 checkpoint ~70GB. Software **PolyForm Noncommercial1.0**, HF weights Apache2.0. Native session transaction/publish/abort/lease/snapshot API and independent branches are a strong idea; not on owner hardware today. Author SWE-bench Verified with retrieved past coding procedures: vanilla66.07%, textual experience69.13%, native MemT69.73% average success, incremental **+0.60pt** over text, no independently proven AA-like xhigh >=38. First compare MemT procedural retention vs compact Markdown+RAG with exact code lines, contradictory design revisions, rollback, 100 turns, solved task/hour. Distinct from Sage-A1.5 trained checkpoint.

## Frozen conclusions and highest-value owner experiments

**No changes to numeric targets or confidence:** two **M1Max64 32GPU** native general GSQ IQ3_S FlashNext 128K occupied **>=40 decode TG + >=425 genuinely cold PP**, 262K occupied **>=35TG+>=400 coldPP**, **AA-like xhigh>=38** and 3–5 independently resumed agents. 5070Ti16+64GB DDR5 Linux, separate RX6800 gfx1030 16GB+32GB DDR4; no third Mac.

1. Physical one-M1 **DS4 memory map** with 32/65/131K actual occupancy, QSA indexer/KV/GDN/PLE/draft/scratch/OS margin; then Q8 control vs KVarN K4V3 actual262K.
2. On same M1 evaluate **speculative solo+park/restart vs Metal time-sliced slots** at 32/64/128K IQ3_S, independent code-agent tool/rollback state, 3–5 persisted agents, memory/TTFT/solved tasks per hour. Source fidelity more important than first-response TTFT alone.
3. Sage-A1.5 pinned Q4/oQ4e-MTP **on actual M1** with 16/64/128K and AA-like agent eval; separate MemT native memory architecture benchmark before port.
4. RTX5070Ti16+64 Linux general DASLab/Swift vs Gyro-L/Basalt/Mirai-S and full long-context quality/VRAM/SSD, RX6800 sourcebuild/fit lower-quant smoke.
5. Actual link+source-equivalent CUDA→Metal committed safe-frontier QSA K/V/indexer, GDN, PLE, MTP/n-gram, sampler with transfer budget. TB4 route ping not state equivalence.

**Next strict cutoff > 2026-10-22 19:36:43 UTC**. No code changes, full long-context owner benchmark, quant promotion or hardware purchase.
