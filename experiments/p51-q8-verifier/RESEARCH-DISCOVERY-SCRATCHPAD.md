# Project 51 — Research Discovery Scratchpad (ranked, replace rather than append)

Purpose: high-information, evidence-first exploration queue for future **user-requested** strict watches; companion [RESEARCH-DISCOVERY-METHOD.md](./RESEARCH-DISCOVERY-METHOD.md). Compact working memory, NOT an accepted finding list, target register, scheduler, executable plan or benchmark result.
Initialized in research-method adoption requested **2026-10-28T17:11:57Z**. **Last verified strict watch cutoff stays 2026-10-28T14:12:42Z**, per [RESEARCH-WATCH-LATEST.md](./RESEARCH-WATCH-LATEST.md). Initial entries are PRIOR-WATCH seeds and current unanswered questions, not a new freshness scan. New session must inspect source updates after that cutoff before calling anything FRESH.

## Objective and invariants

Discover low-circulation, high-information, **verifiable** source model/quant/runtime/agent evidence that improves actual owner performance or correctness: two independent M1 Max32GPU/64GiB source QFN original GSQ IQ3S Metal KVarN+Relay and RTX5070Ti16/Ultra7265F64GiB Linux Basalt; Q8 PLE/MLX mixed compression/quant quality and 3–5 correct persistent xhigh agents. Quality reference oQ5e/BF16 and speed baseline oQ4e; genuine 128/262K occupancy, cold prefill, end-to-end agent tool correctness. A separate broad "new models/quants" lane can compare AREX2 and similar candidates but does not silently redefine the QFN source owner target.

Scores are preliminary triage only: F owner fit (0–3), N novelty (0–3), E evidence (0–3), A actionability (0–3), I independent verification (0–3). Total 3F+2N+3E+2A+I; evidence is NOT certification. Risk/correctness incidents override scores.

## Ranked active leads — maximum 12, replace stale items

| ID / priority | Score | Seed (existing evidence, not newly scanned) | Specific question / next bespoke action |
| --- | ---: | --- | --- |
| RS-04 HIGH correctness override | 18 (F1 N3 E1 A3 I0) | [Strata cross-client SSE reasoning leak #4451](https://github.com/Niko1221/Strata/issues/4451), old watch Oct28 11:50Z | Trace stream/request ID routing and isolation fixes and reproducible two-client overlap/cancel/long-context test; find whether this architecture exists in our Relay path. Counterpass: non-owner server bug must not be asserted as a Mac defect without code evidence. |
| RS-01 HIGH | 24 (F2 N3 E2 A3 I0) | [TensorFold QFN CUDA complete state](https://github.com/ashhart/TensorFold/commit/4dddda8557f94bdeb057b0089bd703d9515fd7ab), last watch evidence 2026-10-28 03:38Z | Reverse engineer exact FlashNext GDN/QSA indexer/PLE/ngram/MTP serialized fields and owner native Metal mapping; find independent save→restart→resume correctness checks and **what CUDA state cannot restore on M1**. Counterpass: only single-rank, may exclude GPU-independent state. |
| RS-02 HIGH | 22 (F2 N2 E2 A3 I0) | [Basalt elastic-KV expert homes #114](https://github.com/jesdga95/basalt/pull/114), opened13:48Z | Inspect material new tests after cutoff; see whether #108 regression 8d94e805 is actually retested on source current main at ~139K, including SSD reads and pressure; separate reduced resident RAM from throughput and multi-slot fit. Counterpass: on-admission DMA and conditional RAM-home retention worsen PP or pressure. |
| RS-03 HIGH | 22 (F2 N2 E2 A3 I0) | [oMLX MTP multi-stream memory #4916](https://github.com/jundot/omlx/pull/4916), old watch Oct28 10:08Z | Follow state restoration/correctness receipts and true resident buffers across QFN models, Q4e vs original IQ3S; explore whether recurrent-state in-place MTP strategy ports to native M1 without peak memory spikes. Counterpass: M3Ultra 248→161GiB at 8 streams does NOT fit or certify 64GiB M1. |
| RS-05 MED/HIGH | 20 (F2 N2 E2 A2 I0) | [TensorFold M3Ultra QFN Metal sampled two-pass topK](https://github.com/ashhart/TensorFold/commit/fd058f579d631b10691e618964c8a4288b1c887), old watch09:52Z | Inspect actual kernel implementation and RNG parity tests; ask if source M1/older Metal supports subgroup design and whether topK overhead is big enough. Counterpass: 698→29µs kernel-only and ~+5% served different M3 Ultra, not 24× owner runtime. |
| RS-09 MED | 20 (F2 N1 E2 A3 I0) | [Strata #4474](https://github.com/Niko1221/Strata/issues/4474), created14:12:03Z, 16GB source IQ3S VRAM reserve problem | Find code-level auto expert-cache sizing regression cause, corrected test and fixed release; require repeated cold boot post-load accounting MTP/indexer/cache/PLE. Counterpass: different WSL2 RTX5080/engine0.1.53 may not reproduce on owner Linux5070Ti. |
| RS-06 MED | 16 (F1 N3 E1 A2 I0) | [BAAI AREX-2](https://huggingface.co/BAAI/AREX-2) + [NapYang 3.80bpw candidate](https://huggingface.co/NapYang/AREX2-27B-3.80bpw-fp16), model discussion earlier this session, not strict watch | Verify source architecture dense vs claimed MoE, actual tensor index and per-layer quant recipe, whether calibration/sensitivity-mapped, true context, missing MTP and eval fidelity. Search DASLab/ByteShape for exact AREX2 optimized artifacts with primary file tree—not mere model-card copy. Counterpass: unvalidated ~13.7GB does not imply source-like coding quality. |
| RS-07 MED | 16 (F2 N2 E0 A3 I0) | [ByteShape Qwen3.8-27B report](https://byteshape.com/blogs/Qwen3.8-27B/) and ISTA source family, no verified original QFN ShapeLearn quant | Follow quantization authors, calibration recipe, per-tensor sensitivity and linked repos/HF commits; look for original QFN model PLE/MTP hybrid precisions and owner-compatible conversion backend. **Negative until artifact verified:** absence in our watch is not proof nobody is working on it. |
| RS-08 MED | 16 (F2 N2 E0 A3 I0) | Source QFN PLE precision Q8_0 vs IQ4NL is a project hypothesis, NOT published test | Seek independent PLE/ngram quality-ablation and compression evidence, inspect actual tensor precision and lookup handling; define smallest blinded xhigh coding/repair eval. Counterpass: better headroom may worsen bandwidth and task time; cannot assert quality improvement without controlled comparison. |

RS-04 is a critical correctness override and should not be buried behind higher weighted speed candidates.

## Next requested-watch deep dives (select 1–3 only)

1. RS-02: Basalt current-main plus #114 exact original IQ3S deep-context regression mitigation: look for fresh comments/commits with **paired actual139K** and synchronized SSD/host transfer, and a versioned owner testable flag.
2. RS-01: complete CUDA QFN state serialization with QSA indexer/PLE/ngram and what a native Mac Relay implementation needs for lossless 128K+ agent resume; include counterexamples (not-restored MTP/per-shard state).
3. RS-06 or RS-07: whichever newly adds primary provenance for an actual optimized AREX2 or original QFN ShapeLearn pack, prioritize HF file tree/tensor index against social claims. If no fresh sources, deprioritize and avoid repeating the same negative search.

Mandatory broad source lane A continues regardless of the above choices.

## Deprioritized or blocked, with reopening gates

- Claims that M3 Ultra source-family 8-stream 81K throughput prove **3–5 simultaneous** M1 Max64 agents: blocked; reopen only on actual 64GB owner peak-memory/live-agent logs.
- Project 51 owner RTX5070Ti16 short TG 100–115 optimistic projection: not a measurement; reopen with physical original source quant benchmark, correct topology, context, and workload.
- Pure “smallest BPW wins” quant ranking: blocked; reopen with frozen output/logit/task-quality cross-check against oQ5e/BF16 and per-tensor map.
- Strata mixed 5080+4060Ti IQ1_M reported ~10× PP vs tuned fork: not directly portable; reopen with one-variable, exact owner source quant and runtime profile.
- Automatic self-rewriting minute-heartbeat researcher: not enabled; reopen ONLY on explicit user request with budget, stop condition and approval separation.

## Missing discovery areas and seed-map extensions

- Original-source QFN calibration/ShapeLearn code/data, native source PLE Q8 impact, explicit tensor index/metadata for model variants.
- M1 Max GPU-family native metal-QSA K4V3, padded scratch and true 262K per-worker retained state.
- Non-English specialized GPU quant/kernel source notes only when primary provenance and dated receipts are obtainable.
- Comparison of per-request full-job agent completion quality and cache traffic vs attractive single-kernel benchmarks.
- Source-matched independent reproductions and contradictory/negative tests.

Maintenance protocol: each completed full strict search-and-update rewrites the active queue, closes dead leads, adds at most the highest-signal sources, and records a new scratchpad maintenance date separately from the hard watch cutoff. This adoption creates **no new time-window evidence** and leaves previous cutoff intact. Any performance, fit or correctness claim here is a lead to test, not promoted canonical target truth.
