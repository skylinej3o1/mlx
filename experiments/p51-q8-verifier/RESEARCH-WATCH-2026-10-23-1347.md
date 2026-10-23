# Project 51 / Relay — supplemental research watch, 2026-10-23 13:47 EDT

**Predecessor:** [RESEARCH-WATCH-2026-10-23-1345.md](./RESEARCH-WATCH-2026-10-23-1345.md), strict cutoff **2026-10-23 17:45:00 UTC**, commit `4251f8007cf9f87721161e58b44e80037f84e970`, committed during this research response by another writer. This supplement advances the official **strict UTC cutoff to 2026-10-23 17:47:07 UTC**, exactly the user's request time. The GitHub branch moved after an initial expected-head check: orphan commit `415feaf989e12b87a1b1e9b1484cf8fe0f449408` was intentionally **NOT attached**. The concurrent 13:45 report retains the complete main window (11:19:46–17:45Z) and its state update; do NOT duplicate those findings as newly discovered after 17:45Z. There were **no additional high-confidence owner-hardware target measurements in the final 127 seconds**. The items below are *supplementary evidence omitted from the already-committed watch*, dated earlier in the parent window unless explicitly otherwise. No owner hardware was operated, inference code was changed, or target/probability was promoted.

## Additional independently traced supporting evidence, originally UPDATED/MERGED before 17:45Z

### A. Older TensorFold #1080 updated 13:11Z: dense27B CUDA 5090 5.4× long-prefill, NOT source-exact

https://github.com/ashhart/TensorFold/pull/1080 . Physical **one RTX5090** with dense **Qwen3.8-27B MLX4bit + DFlash2** and FP8 KV, actual **75,616 input tokens**: cold TTFT **144.5→26.9 s**, using tensor-core attention, 4096-row prefill chunks, optimized GDN/delta-rule chain and 2×2-warps. This is **5.37×** faster end-to-end *on the RTX5090 and this dense checkpoint*. Numerics differ because attention/chunk summation changes: only **10 of 24** tested greedy replies byte-identical to baseline. No source-equivalent long-task xhigh proof; no direct transfer to owner's RTX5070Ti16 (fewer SMs and different memory) or the original general Flash-Next GSQ architecture. Owner inference coldPP confidence unchanged.

### B. NEW TensorFold #1217 (created 12:50:58Z) on a GB10: bitwise-exact GDN fusion, small full-request win

https://github.com/ashhart/TensorFold/pull/1217 . Physical **GB10**, Flash-Next FP4-Local, CUDA GDN front/chain/norm fused per value head, **4096-row block5.008→4.078ms** but served **38K cold TTFT~30.98→29.93s**; hashes equal for **136/136 tokens** in described seeded/cold/warm tests. No change to dense27B path, Metal or user5070Ti. Distinguish large isolated-kernel gains from 2–3% total request and preserve fidelity. Open/unmerged at watch.

### C. MERGED Basalt #23 at16:15:50Z and updated cached-state PRs

https://github.com/jesdga95/basalt/pull/23 : serving prefix match bulk-int32 rather than one-token-at-a-time, same returned ids, CPU tests39/39 and reference greedy text. No measured user coding-agent speed.
Stacked OPEN #24 https://github.com/jesdga95/basalt/pull/24 and #25 https://github.com/jesdga95/basalt/pull/25 : private/RAII GDN checkpoint slot ownership and whole-page BIGRAM-keyed draft KV with invalidation of unpublished tail across every KV mode, preventing stale bytes from another conversation after restore. Physical RTX5090 #24's pool of 2 ×112MiB did **not** speed realistic cache restores; measured +26ms park/+8ms restore under PDL. These primarily support **source-continuation correctness and session isolation**, not M1 memory reclamation. #26 aligns stop/context-fit, #27 draft suffix length; no actual owner result.

### D. MERGED llama.cpp #30804 at16:26:17Z and NEW #31037/#31040

https://github.com/ggml-org/llama.cpp/pull/30804 : chunk CUDA graph launches, generic developer **1–2% TG**, no target/source/hardware qualification.
https://github.com/ggml-org/llama.cpp/pull/31037 (created11:24:30Z) : trimmed 98,304-token MTP draft vocabulary on **SYCL Intel GPU** Swift1.5 Q3_K_S, short sampled greedy 300-token request **93.3→100.2 TG (+7.4%)**, **same 687/789 accepted tokens** and same text. SYCL CUDA graphs crashed in BOTH baseline and patch. A draft-head compression idea, not M1/RTX5070Ti measured.
https://github.com/ggml-org/llama.cpp/pull/31040 (created11:58:15Z) : required/optional tagged tool-argument parser accepts any order exactly once instead of rigid order/unbounded repeats; important coding-agent tool validity *test case*, no physical agent success receipt.

### E. Public date-only M1 Max Flash-Next benchmark, strict time indeterminate

https://omlx.ai/benchmarks/performance/3xz7c2u3 lists **M1 Max 32 GPU cores /64GB**, **Qwen3.8-Flash-Next-oQ4e-fp16-mtp** on **oMLX0.7.2**, macOS27.0.1, nominal context65,536 and benchmark 64K row **PP233.6, TG8.0**, reported process peak**49.5GB**. It also shows 1K72.7PP/9.6TG and 4K195.1PP/9.4TG. The page is dated **2026-10-23 without precise submitted UTC**, and does not fully expose prompt actual occupancy, cache coldness, quality or methods; **DO NOT assert it was created during 11:19–17:47Z**, nor that it is the ISTA-DASLab original general GSQ IQ3S on paperniuk DS4. Useful counterexample for why a nominal64K FlashNext model may perform much worse than short dense27B / newer Apple measurements; further corroborate before adjusting confidence.

## Strict final-window check and gate

The prior [13:45 watch](./RESEARCH-WATCH-2026-10-23-1345.md) already covers Strata #3869 dual RTX3090 DFlash2 -1.8% vs MTP, oMLX #4785 missing QFN DFlash2 rollback, remote CUDA stages #1887, Hipfire #945 session swap, Strata #3060 RAM expert staging, and M1Ultra (not M1Max) oMLX #4496 evidence. A Strata #3875 PLE-only shard change was created17:42:53Z and already covered there. The known llama.cpp #30657 PR later updated at **17:47:41Z** lies **after** request time and does not enter this watch. Research should next begin **STRICTLY AFTER 2026-10-23 17:47:07 UTC**; avoid duplicated status claims or moving the cutoff beyond the request.

**FROZEN target/hardware:** 2 independent M1Max64/32GPU, original-general Qwen3.8-Flash-Next ISTA-DASLab GSQ IQ3S, truly occupied128K **>=40 B1 TG /425 genuinely cold PP**, occupied native262K **>=35 TG/400 coldPP**, source-like xhigh AA-like>=38, 3–5 independent genuinely restorable coding agents. Owner one RTX5070Ti16 +64 DDR5 Linux and separate RX6800 nonXT gfx1030 16GB+32DDR4. No third M1, no new xhigh coding-agent quality, no real full native262K K4V3 on M1, no exact physical CUDA→Metal QSA/GDN/indexer/PLE/MTP state-equivalent Relay. Leave numerical targets and prior confidence unchanged. Prioritize actual M1 native memory map, after-restore evidence of *real* reused tokens, independent tool/end-task quality, M1 dense27B/Flint/Sage quant A/B and correct owner's CUDA/AMD physical measurements.
