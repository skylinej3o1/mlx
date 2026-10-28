# Project 51 — Research Discovery Scratchpad (ranked, compact)

Protocol: [Seeded Discovery v1.0](./RESEARCH-DISCOVERY-METHOD.md). Last maintained **2026-10-28T17:34:00Z**, paired [strict watch](./RESEARCH-WATCH-2026-10-28-1334.md); hard cutoff verified in [LATEST](./RESEARCH-WATCH-LATEST.md). Notes are DISCOVERY queue, not certification or authorized hardware changes.

## Objective and scoring

Primary owner goal: original ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO **IQ3_S**, separate PLE/MTP, **TWO independent M1 Max32GPU/64GB** native Metal source-like 128K/262K cold prefill and sustained decode, correct 3–5 long-lived xhigh agents, Relay/KVarN. Distinct RTX5070Ti16/CoreUltra7 265F/64GB DDR5 Linux Basalt and RX6800 nonXT16GB VRAM/**ONLY16GB host**. Never confuse model files with working RAM or similar GPU/model with owner evidence. Scores are researcher triage heuristic 3F+2N+3E+2A+I, each component 0–3; not success probabilities. Only original sources' raw measurements can support conclusions; HIGH human approval needed to run tests.

## Ranked active leads (max 12; security overrides score)

| Lead / priority | Score F,N,E,A,I → total | Seed | What actually falsifies/improves the hypothesis |
|---|---|---|---|
| **RS-04 CRITICAL privacy** | 1,3,1,3,0 → **18** | [Strata #4451 cross-client SSE frames](https://github.com/Niko1221/Strata/issues/4451) | Find concrete routing isolation patch/repro with overlap, cancellation and stream IDs. Do not claim owner native M1 vulnerable on different server. |
| **RS-11 HIGH persistent fit** | 2,3,2,3,0 → **24** | [Strata source IQ3S #4518](https://github.com/Niko1221/Strata/issues/4518) | Joint RAM budget full PLE26.8GiB vs 8GiB cached sessions, experts, QSA/GDN/MTP/KV, OS. Two agent parking/revisit TTFT and full job wall A/B; reject isolated 2% PP gain if caching dies. |
| **RS-10 HIGH owner M1 baseline** | 2,2,3,3,0 → **25** | [Strata M1Max64 Q2_0 #4457](https://github.com/Niko1221/Strata/pull/4457) | HIGH-gated physically original IQ3S true128K/262K cold PP/decode/completed >512-token xhigh tool tasks; same chip Q2 4/16K n3 is not source-quality or long-context certification. |
| **RS-01 HIGH complete state** | 2,3,2,3,0 → **24** | [TensorFold source QFN CUDA disk layout](https://github.com/ashhart/TensorFold/commit/4dddda8557f94bdeb057b0089bd703d9515fd7ab) | Per-worker source state inventory, GDN conv/recurrent, QSA K/V+indexer+pooled rows, PLE/ngram and optional MTP, cross-machine hash/version and replay equality AND real agent correctness; M1 port not proven. |
| **RS-12 HIGH checkpoint writer** | 1,3,2,3,0 → **21** | [TensorFold #1538](https://github.com/ashhart/TensorFold/issues/1538) / [#1548](https://github.com/ashhart/TensorFold/pull/1548) | Reproduce latest-state save under queue pressure; assert promised block checksum, atomic publication and invalid-state purge; GLM CUDA 2.6→0.96s TTFT is not QFN Metal. |
| **RS-02 HIGH Basalt deep PP/TG** | 2,2,2,3,0 → **22** | [Basalt open #114](https://github.com/jesdga95/basalt/pull/114) / old [#108](https://github.com/jesdga95/basalt/pull/108) | 139K original IQ3S current-main vs +#114 matched owner-class A/B with SSD/host/RAM profile. Prior ~−2.67% regression NOT shown recovered; fork result neutral only on different base. |
| **RS-15 NEW HIGH memory correctness** | 1,2,2,3,1 → **20** | [antirez/ds4 #1279](https://github.com/antirez/ds4/pull/1279) → [#1282](https://github.com/antirez/ds4/pull/1282) | Can any QFN cache layer be packed **losslessly from an already-low-bit representation**, and survive subnormal-scale, sign, sparse-index, A41–A43-like checkpoint cross-format? **V4.1/DeepSeek not QFN**. Author M5Max pre-window tests: 5→2.5→0.8GiB at1M, 0.0 logits diff; outside contributor corroboration reported but source comment timestamp unknown. |
| **RS-09 HIGH GPU headroom** | 2,2,2,3,0 → **22** | [Strata IQ3S UC #4516](https://github.com/Niko1221/Strata/issues/4516) + [#4474](https://github.com/Niko1221/Strata/issues/4474) | Linux 5070Ti actual free VRAM, expert cache overshoot, first-touch PP and actual repeated agent completion; WDDM 843→1289 PP on different GPU is not owner Linux. |
| **RS-03 MED Metal MTP memory** | 2,2,2,3,0 → **22** | [oMLX #4916](https://github.com/jundot/omlx/pull/4916) | Original source IQ3S on M1 with separate precision/KV/MTP verified; M3Ultra oQ4e 8×81K not owner. |
| **RS-16 NEW MED adaptive draft** | 1,2,2,3,0 → **19** | [TensorFold stacked EXL3 #1446](https://github.com/ashhart/TensorFold/pull/1446) | 2x5060Ti CUDA QFN EXL3 author report code cold decode34.24→103.10 TG but TTFT worsens10.88→11.66; short draft worse, 2 streams ~22% slower, rebased cold restart anomalous. Test per-session total coding wall, not MTP superficial gain. Older Oct27 evidence, not fresh. |
| **RS-13 MED thinking budget** | 1,3,2,2,0 → **19** | [oMLX open #4926](https://github.com/jundot/omlx/pull/4926) | Verify GPU synchronization skipped only when QFN native source budget cannot trigger; parity for thinking control tokens, xhigh output and tool calls. M3 Ultra Qwen27+11% is analogy. |
| **RS-07 LOW discovery quant map** | 2,2,0,3,0 → **16** | [ByteShape / ShapeLearn](https://byteshape.com/blogs/Qwen3.8-27B/) | Exact QFN transformer per-tensor quant sensitivity, PLE/MTP exceptions and independent task quality; nothing confirmed newly published within 17:16–17:34Z window. |

## Next bounded deep dives (maximum three)

1. **RS-11 + RS-10 (owner):** issue/PR evidence for source IQ3S physical M1 MAX64 at true128/262K; compare performance against 2+ parked agents, budget full PLE and resumption. Seek contradiction to shallow Q2 extrapolation.
2. **RS-01 + RS-12 + RS-15 (state/precision):** cross-runtime GDN/QSA/indexer/PLE/optional MTP serialization and latest save correctness. Explore exact low-bit *representation packing* separately from lossy new KV quantization and test subnormal block/selected-index masks.
3. **RS-02 + RS-16 (runtime):** monitor deep Basalt #114 regression countercheck or reliable adaptive MTP source-family result, whichever produces a physically controlled latest experiment; if neither, return to exact HF ShapeLearn artifacts. Verify whether [vLLM #64123](https://github.com/vllm-project/vllm/pull/64123) is now source-dated after the cutoff, since its body changed 17:34:47Z AFTER this watch and cannot be retroactively counted.

## Discovery outcomes and closed/deprioritized

- **REDISCOVERED older but useful:** DS4 V4.1 Metal packed-KV **bit-exact representation** with subnormal-scale recovery (#1282; original Oct25), EXL3 adaptive MTP can lose prefill/concurrency (#1446; Oct27). Neither transfers speed or correctness to owner FlashNext Metal IQ3S.
- **FRESH but not actionable:** Strata Windows mixed9070XT+3070Ti engine-selection issue #4520 created17:16:57Z; vLLM ROCm CI lockfile commit17:26:28Z. No source target measurements.
- **Timestamp discipline:** GitHub updated_at on #1279/#1282 at17:24Z and TensorFold #1446 at17:22Z does not prove a benchmark was run then. The independent commenter date on #1282 was not exposed by connector; conservatively treat as undated corroboration. No promotion.
- **False analogy rejected:** another-family V4.1 storage exactness is NOT a QFN KVarN IQ3S KV4 quality certificate, not even if both use 4-bit; 1M stored cache per-session saving on M5Max does NOT quantify M1 128/262K fit.
- **AREX-2/ShapeLearn:** no new direct source per-tensor optimized map found; keep as discovery debt, not claim of nonexistence.
- **Source M1 XHIGH and durable Relay:** still no exact 128/262K IQ3S physical source, no 3–5 resumed independently correct agents, no end-to-end two-M1 cache; keep all targets and approved-stage policy.
- **AMD worker/GTX1080:** no new owner gfx1030 with 16GB host memory or meaningful Pascal supported inference proof; do not buy/allocate based on neighbors.
- **Do not reactivate** 1-minute autonomous heartbeat or any pre-approved auto tuning; research-only GitHub changes.

## Primary source map growth and discovery debt

Useful new source entries: [V4.1 packed cache primary](https://github.com/antirez/ds4/pull/1282), [adaptive offload MTP primary](https://github.com/ashhart/TensorFold/pull/1446); original source [ISTA publisher](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) remains central. New future postcutoff verification candidate [vLLM QFN ROCm MXFP4](https://github.com/vllm-project/vllm/pull/64123). Missing: QFN IQ3S M1 correct full-context source/kv/working-memory proof, exact QSA selected-index lossless packing opportunity, MTP tensor presence, PLE Q8 quality and I/O, producer storage atomicity, real cold prefill/SSD pages, quantitative semantic coding success vs oQ5e/BF16, 5070Ti Linux own Basalt, RX6800 16GB host trial, cross-client sentinels.

**All experiments stay PROPOSED until explicit human HIGH approval.**
