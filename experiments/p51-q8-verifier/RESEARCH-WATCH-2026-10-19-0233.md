# Project 51 / Relay — 27B host-KV recovery, 2026-10-19 02:33 EDT

**PREVIOUS STRICT CUTOFF:** 2026-10-19 06:17:35 UTC.
**NEW STRICT CUTOFF:** 2026-10-19 06:33:02 UTC.
**Classification:** All experiments below are **RECOVERED OLDER EVIDENCE** from September/early October 2026, not newly published within this 15-minute watch. User asked for the successful Qwen3.8-27B RAM-backed / streaming KV test. Source reports and independent reproduction distinguished; no physical owner test, model/engine modifications or target changes.

## Three distinct successes (and where they do *not* transfer)

**1. Adaptive KV Streaming V2 — direct RTX 5070 Ti chip match, full-history attention**

- https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming — Qwen3.8-27B Unsloth UD-IQ4_XS, Q8_0 K/Q4_0 V. Complete native attention K/V stays in **pinned CPU RAM**; bounded GPU resident pages and reusable ring transfer K/V at each needed full-attention layer. Unlike KVMem, model attends to the entire required history; exactness relative to same-format native path has numerical qualification but is not universal token identity. One serial CUDA request, not ROCm and not CUDA→Metal.
- On contributor **RTX 5070 Ti 16 GB**, matching article corpus at 128Ki: stock UVM-only llama.cpp 2.48 decode TG /837.1 PP, V2 target-only 26.15 TG /934.6 PP. This is an *unmanaged UVM vs deliberate streaming* comparison, not GPU-resident vs streaming. V2 MTP3 ~59.7 TG @128Ki (separate controlled run); near256Ki V2 Q8K/Q4V target 9.60TG, MTP3 22.27TG, DFlash7 21.80TG. With Q5_1/Q5_1, DFlash7 27.71TG at256Ki. Corpus sweep outputs only256 tokens and **does not demonstrate solved 262K coding-agent tasks**. Runtime/quant/compiler/effort other than exact card may differ from owner's headless Linux.
- Independent earlier-version RTX5060Ti16+32GB Ubuntu replication https://github.com/arczhi/5060ti-qwen3.8-27b/blob/main/references/adaptive-kv-192k-experiment.md: physically admitted and generated at 196608, real DeliverableBench task99.5/100 in760s. Prefill/decode long sweep including8.15TG@180K was originally timed on an **invalid-output sm120-only build**; corrected build functionality checked separately. No MTP in that reproduction; do not conflate with V2.

**2. KVMem — query-selected GPU KV window, full history stored in RAM and optionally SSD**

- https://arxiv.org/abs/2609.04852 ; https://github.com/kvmem/kvmem (canonical, old kvmem-llama.cpp URL redirects); original https://github.com/ggml-org/llama.cpp/discussions/28894 (2026-09-14).
- RTX5060Ti16 +32GB host (WSL2 ~19.5GB visible) source Sep14: Qwen3.8-27B ISTA IQ3_S Q8 KV with 36K history/16K output GPU window, or Unsloth IQ4_XS Q5 KV with32K history/12K output window. A 33-request simulated tool-history span reached **262058 /262144 tokens**, overall decode30/33TG (IQ3/IQ4), final 29/35; GPU15.5/15.6GB and host RAM13.1/11GB. Author LongMemEval-S selected32K85.6% vs full256K86.6%, AgentLongBench60.9% vs59.5%; **selective retrieval is not exact full history**.
- Independent arczhi https://github.com/arczhi/5060ti-qwen3.8-27b/blob/main/references/kvmem-256k-experiment.md: single 261699-token prompt needle, 56.8TG in 256 repetitive tokens **with 100% MTP acceptance**; separate real agent100/100, 69 tests green,482s, median50.3TG **at <=54K agent context**, NOT long262K task. KVMem paper 1M *addressable workspace* never one native 1M model invocation.
- KVMem NInfer 0.18 stable release **Oct13** Windows RTX30/40/50 source https://github.com/kvmem/kvmem/releases/tag/v0.18.0: GSQ-RCO IQ3_S vision/MTP 5060Ti16 and simulated33 tool-turn memory at261522 prompt, 53.24TG overall, final44.87 TG, 33/33 replies, **no protected code completeness/retrieval pass**, free host memory reached only8.78MiB. ROCm Beta2 exists for earlier llama.cpp branch but no exact RX6800 27B runtime or full 0.18 feature parity receipt.

**3. TierKV — host KV selective page staging plus disk snapshots**

- https://github.com/arczhi/llama-tierkv same RTX5060Ti16/32GB host, Unsloth IQ4_XS + requantized MTP head.
- *Actual* DeliverableBench ocr-dual-channel protected agent **100/100 in398s**,72/72 tests, decode median62.1TG, with selected 49152 GPU window and **65536 logical context**, MTP5. On same task/machine plain llama.cpp MTP5 433s/65.8 median vs KVMem 482s/50.3 median. **Full 262K is separately tested without speculation**: 680PP and22.70TG, host Q4 KV ~4.6GB, VRAM15.5GB. Never attach the 62.1TG agent result to the 262K run. SSD is an idle snapshot tier, not per-token substitute for all KV.

## Project-specific engineering decision

- **RTX 5070 Ti16 +64GB native headless Linux:** put Adaptive KV V2 first for source-checkpoint-preserving 128/200/262K experiments (retains whole historical attention); KVMem and TierKV for RAM/VRAM efficiency and agents whose quality tolerates selective retrieval. Compare with Swift1.5, ByteShape dense27B only if correct quant+MTP+cache support; rerun agent task success, resumption state and solved tasks/hour. All published V2 tests use one request and IQ4_XS, not owner's own source quant.
- **RX6800 16GB+32GB DDR4 separate Linux PC:** weight+host RAM arithmetic promising, but Adaptive V2 full-streamed CUDA kernels lack end-to-end HIP; KVMem earlier ROCm Beta2 not proof of gfx1030 reliability. No borrowed NVIDIA TG.
- **2×M1 Max64:** Apple UMA doesn't use a 16GB discrete VRAM↔host PCIe split; mechanisms inform memory governance and long-agent selective recall but are not Metal implementations. Existing exact M1 dense27B oMLX #4496 40.4/33.7/24.2TG@17/67/133K remains independent.
- **Relay:** none moves complete Qwen recurrent GDN/KV/draft context from CUDA on PC into exact Apple Metal model or supports streamed remote KV on Macs. PC RAM KV is not automatically Mac GPU memory; don't treat memory paging as cross-host Relay. Keep numerical targets, code, frozen verifier and buying plan unchanged.

**NEXT STRICT WATCH:** after 2026-10-19 06:33:02 UTC.
