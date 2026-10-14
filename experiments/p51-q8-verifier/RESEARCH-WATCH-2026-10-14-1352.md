# Project 51 research watch — 2026-10-14 13:52 EDT

**Previous strict cutoff:** 2026-10-14 15:26:39 UTC.
**New strict cutoff:** 2026-10-14 17:52:46 UTC (user's latest message timestamp).
**Sources:** GitHub connector search PR/issues created in window, recent default-branch commits, original merged PR descriptions and selected source-diff validation, plus public topic searches. Classify **UPDATE (previously opened, merged now)** separately from **NEW (created in window)**. Prior two Oct14 watches already commit Strata v0.1.44.1, oMLX batched DFlash and SSD requeue merged, and older recovered PLE/WSL diagnostic evidence; do not double-count.

## Executive verdict

**No direct on-owner M1 Max64GB IQ3_S or RTX5070Ti16GB/Core Ultra7/64GB Swift IQ3_S long-262K xhigh test; no full dual-M1 PP2/TB4 numerical result; no hardware/quant/certification target movement.** Merged *cross-system KV-transfer correctness*, *descriptor geometry*, *SYCL IQ3 acceleration*, and *cache identity* are useful Relay research, but do not constitute turnkey CUDA->Metal handoff. No source code or verifier changes; GitHub documentation only.

## UPDATE (merged in window): vLLM producer retains transfer pins until NIXL terminal, PR #59790

**Merged at 2026-10-14 ~15:31 UTC**, created Oct2.
https://github.com/vllm-project/vllm/pull/59790
https://github.com/vllm-project/vllm/commit/e2aabc8b1521

**Root cause:** On UCX/NIXL, `release_xfer_handle`, `cancel(mode="wait")`, or `remove_remote_peer` were mistakenly treated as proof that a running remote WRITE stopped. An RMA PUT may continue, so producer's early abort acknowledgment/host block unpin lets a later requester reuse memory still being read/written by an old transfer, silently contaminating KV.

**Transport-qualified evidence, not model benchmark:** Real NIXL 1.4.1 UCX-over-TCP CPU DRAM: old 512MiB `cancel(mode="wait")` returned empty (declared cancelled) in **5/5**, all bytes arrived later; corrected method kept transfer inflight in **5/5** until 512MiB arrived. `remove_remote_peer` similarly did not stop post-close writes in 5/5; 1GiB paused process resumed after immediate cancellation still received all 64 blocks; stalled live peer may never finish; SIGKILL triggers NIXL disconnect. Focused tests 486 pass/1 skip on one head, 484 pass/1 skip on another. **No RDMA/InfiniBand, GPU memory, serving load, Flash/GDN correctness qualification.**

**Fix semantics:** Producer stores remain pinned, no `AbortAck` until all writes reach terminal state (or verified peer gone); controlled 100ms retry pacing and no unsafe forced cancel after 10s; a living hung peer can therefore retain pins indefinitely. **Remaining gap:** consumer-side `_ABORT_ACK_TIMEOUT_S` currently frees its slots after timeout, referenced open #61532, so neither service nor our Relay is fully safe purely by importing producer logic.

**P51 action:** copy *proof obligations*, not code: immutable memory ownership epochs, exact model and layout fingerprints, write/read completion fences, remote peer failure state, no authoritative cache publish or buffer reclaim until all writers/readers terminal; test SIGSTOP/SIGKILL, delayed RDMA write, cancellation, retry, peer loss, and two-agent private nonce. Never count aborted transfer as stopped without transport guarantee.

## UPDATE (merged in window): vLLM NIXL1.5 strided KV descriptors #61032

**Merged 2026-10-14 ~16:07 UTC** (commit `eaf25f675a4e`), PR created Oct10.
https://github.com/vllm-project/vllm/pull/61032

**Mechanism:** instead of emitting millions of per-KV-block `(addr,len,dev)` records, NIXL v1.5 supports `(addr,len,dev,stride,count)` for uniform block regions. One row per region; preserve flat-index mapping. Mixed VRAM/DRAM and PP split regions handled separately; decline NIXL <1.5. Stated benefit is *metadata setup and first handshake*, **not runtime transfer bandwidth or warm decode TG**.

**Author GB300 Qwen3-8B P/D evidence, median ~3 interleaved rounds:** TP1 local registration 52ms→0.2ms, handshake 156→109ms, cold first request 307→259ms; TP2→TP1 first handshake **2255→118ms**, cold request **2656→425ms**, warm latency ~76–89 vs 77–99ms (no real improvement). Pool ~1.48M KV tokens/3.3M original per-block descriptors. No TB4 CUDA→Metal compatibility and not the owner's 262K xhigh test.

**P51 action:** Relay KV/state export should be region-oriented and typed, with compact descriptor registration and monotonic token/block indexing. Avoid O(context x layers x ranks) Python descriptor construction and don't promote setup improvement to long decode rate.

## UPDATE (merged in window): llama.cpp Intel SYCL IQ3_S reorder #29107

**Merged 2026-10-14 ~16:41 UTC**, originally opened Sep18.
https://github.com/ggml-org/llama.cpp/pull/29107
https://github.com/ggml-org/llama.cpp/commit/529ac893e754

Persistent reordering IQ3_S and IQ3_XXS once at load lets Intel SYCL Arc compute dense dot products more efficiently; dequantization honors reordered layout. Author Intel Arc Pro B70 / Qwen3.8-27B-GSQ-RCO-IQ3_S: tg256 at ~9K **12.30→21.59 TG**, 64K **9.76→14.92**, 126K **7.88→10.93**; prefill about unchanged. Commit text lists 0-context 12.92→23.54 TG. **Does not apply as-is to M1 Metal or 5070Ti CUDA**, no custom Swift layout or 262K proof. Potential abstract design inspiration for a Metal QMM prepack (requires memory/time/quant exactness accounting), not a project performance target update.

## UPDATE (merged in window): SGLang LoRA-aware prefix cache identity #42818

**Merged 2026-10-14 ~16:50 UTC**, PR created Oct6.
https://github.com/sgl-project/sglang/pull/42818
https://github.com/sgl-project/sglang/commit/c964d9ba207d

Worker-local external KV block IDs are not sufficient prefix lookup keys across different LoRA adapters/loads. Computes canonical namespace-specific lookup identity from token sequence, adapter name and cache salt; tracks per-worker/rank external IDs and independent owners across storage tiers. 1,531 Rust router/indexer tests pass. GPU serving E2E/Hicache not run on this revision, and reusing the same public adapter name for different weights still requires versioning. **P51 analogue:** different model revision, quant layout, adapter or agent isolation namespace cannot inherit another's prefix state; storage-block identity and logical cache key are distinct.

## NEW default branch commits with low relevance

- llama.cpp `685f70894b66` Oct14 16:36 UTC keeps CPU F16C FP16→FP32 lookup table; no exact Mac/CUDA model performance proof.
- llama.cpp `5cdadfc32616` Oct14 15:31 UTC CPU row-buffer allocation safety; no 262K TG estimate.
- vLLM also merges exact-shape `vllm bench forward` #61339 at 17:52:26 UTC; separates model-forward latency from end-to-end serving and supports modeled KV/token geometry, but is CUDA-centric and **not a measured speed result for our fleet**. https://github.com/vllm-project/vllm/commit/9d3dfa2886ae
- Other vLLM/SGLang commits in the window target GPT-OSS, AITER/ROCm, Granite, LoRA router or unrelated backends, not direct dual-M1/5070Ti validated rates.

## Research scope and negative checks

- Queried Oct14-created GitHub issues/PRs in Strata, oMLX, Basalt, Strata-for-Mac, Sushi, llama.cpp, vLLM, SGLang, mlx-serve, TencentDB Agent Memory, DS4, pi-vcc and adaptive-KV fork. **No newly created PR/issues in the narrow (15:26:39,17:52:46] UTC interval** for those index queries; do not confuse an older PR merge with a newly created PR.
- Checked latest default-branch commits; Strata newest source commit Oct13 23:51 UTC, oMLX Oct14 10:59, Basalt Oct14 14:09, Sushi Oct14 01:29, Mac Strata Oct11, mlx-serve Oct14 05:34, TencentDB Oct14 07:29, pi-vcc Oct12, adaptive KV fork Oct11 and DS4 Oct7. **None in interval.** llama.cpp/vLLM/SGLang relevant merges described above.
- Existing Oct14 Strata v0.1.44.1 release and oMLX main DFlash batching+SSD requeue changes **are already recorded** by the prior watches; rechecking doesn't confer a new performance receipt.
- Web searches produced background/stale forum records but no new verified **ISTA-DASLABS IQ3_S Swift1.5 actual-filled 262K xhigh** on owner 5070Ti/64GB or single M1Max64GB, and no verified physical dual-host PP2. Do not conflate Sushi 3bpw, oMLX oQ4e, and original/SwiFT DASLABS IQ3_S.

## Next execution-gated actions

1. **RTX5070Ti**: Strata 0.1.42 control vs 0.1.44.1 candidate vs Basalt Linux, exact GGUF/model/quant, actual filled 16/64/128/192/near262K, cold PP+TG/TPOT, MTP, source-like coding quality, pinned CPU experts, hot ngram PLE I/O, 64GB host/VRAM margin, two-agent isolation.
2. **M1 Max x2**: M1 #4496 oMLX 27B baseline and main batched DFlash + SSD requeue first; separate Strata-for-Mac DASLABS IQ3_S at real memory fit, 128K/256K. No exact M1Max64GB IQ3_S 262K benchmark, no metal Swift adaptation proven.
3. **Relay**: implement only after typed complete checkpoint export including QSA indexer, GDN/decay, KV, vision/MTP state, transport commit epoch, ack-after-drain; use strided descriptors and owner namespaces. Test aborted transfer while 3–5 concurrent Pi agents stream and retry.
4. **Quant quality**: keep ~3.3–3.6bpw custom xhigh Flash plan with oQ5e comparator and frozen agent-task pass rates; do not move confidence solely on Reddit speed reports.

**TARGETS / CERTIFIED VERIFIER: unchanged.** No hardware recommendation. No experimental code patch or owner's equipment runtime test this research pass.

**NEW STRICT HARD RESEARCH BOUNDARY: 2026-10-14 17:52:46 UTC.**
