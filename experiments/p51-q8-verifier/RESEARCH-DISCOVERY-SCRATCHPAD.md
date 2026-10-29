# Project 51 — Seeded Discovery Scratchpad (ranked next actions)

Last reconciled **2026-10-29T08:36:12Z** request, immutable evidence: [RESEARCH-WATCH-2026-10-29-0436.md](./RESEARCH-WATCH-2026-10-29-0436.md). Latest hard cutoff only in [RESEARCH-WATCH-LATEST.md](./RESEARCH-WATCH-LATEST.md). Lead scoring: **3F+2N+3E+2A+I** where owner Fit, Novelty, Evidence, Actionability, Independence each 0–3 (0–33 heuristic, not probability). Security correctness overrides score.

## Fixed objective and scope

Original **ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO IQ3_S** xhigh coding quality, oQ5e/BF16 oracle, oQ4e speed comparator; separately PLE/ngram/MTP precision, 128K+262K actually occupied cold PP/TG, two **independent M1Max 32GPU/64GiB** native Metal; 3–5 independent durable correct agents, possible 5070Ti CUDA→Metal Relay. Owner NVIDIA RTX5070Ti16+CoreUltra7265F64GB DDR5 Linux and AMD **RX6800 nonXT gfx1030 16GB VRAM + ONLY16GB host DDR4**; GTX1080 8GB Pascal no assumed current supported route. No hardware tests or unattended workflows without HIGH authorization.

## Active ranked queue — maximum 12

| Rank | ID and triage F,N,E,A,I / score | Seed | Next falsifier / action |
|---|---|---|---|
| SAFETY OVERRIDE | **RS-04** 1,3,1,3,0 /18 | [Strata cross-client SSE #4451](https://github.com/Niko1221/Strata/issues/4451); [oMLX silent tools fix #4941](https://github.com/jundot/omlx/pull/4941) | Run only after HIGH: overlapping agent/tool/sse ID isolation and declared-tool parser/stream output exactness. Do not infer all backends leak. |
| HIGH | **RS-17** 2,3,3,3,0 /27 | [Physical M1Max64 concurrency #4935](https://github.com/jundot/omlx/issues/4935) | On actual source IQ3S, queue vs adaptive vs fixed DFlash/MTP, 1/2/4 agents full work and peak memory; Qwen3.6 oQ4e M1 fixed DFlash c4 ~56–59 vs no-spec123–124 aggregate does NOT transfer model/quant. |
| HIGH | **RS-18** 2,3,3,3,0 /27 | [oMLX merged batch-KV join #4936](https://github.com/jundot/omlx/pull/4936) | Which source M1 Metal bank/attention layouts reallocate on return? M3Ultra QFN oQ4e returning agent +18.8→+5.1GiB pool: reproduce with protected peak+semantic oracle and M1 64GB cold/reuse. |
| HIGH | **RS-11** 2,3,2,3,0 /24 | [IQ3S PLE pin evicts parked state #4518](https://github.com/Niko1221/Strata/issues/4518) | Joint 26.8GiB PLE, 8GiB park, experts, GPU KV, OS budget on distinct Macs; two resumed full coding agents and real revisit wall; do not optimize 2% PP blindly. |
| HIGH | **RS-19** 2,3,2,3,0 /24 | [Basalt IQ3S deep KV pinned host #117](https://github.com/jesdga95/basalt/pull/117) stacked on [#114](https://github.com/jesdga95/basalt/pull/114) | Current main+114 vs +117 real131K/262K owner5070Ti, c1 continuation, content diverse, RAM admission, SSD, cold vs reuse, ABBA/CIs, task quality. Non-owner5080 131K decode-window +4.7% with fresh-read -3.8%; only 1 stream, RAM pin1.74GiB. |
| HIGH | **RS-01/12** 2,3,2,3,0 /24 | [QFN CUDA full snapshot](https://github.com/ashhart/TensorFold/commit/4dddda8557f94bdeb057b0089bd703d9515fd7ab), [rows-store writer #1548](https://github.com/ashhart/TensorFold/pull/1548), [Metal idle memory #1572](https://github.com/ashhart/TensorFold/issues/1572) | Latest committed GDN/QSA/indexer/PLE/ngram/MTP bytes and complete state, checkpoint retries, idle footprint/spills; code cleanup is not proof newest state persisted, nor that M1 agent can resume. |
| HIGH | **RS-20** 2,3,2,3,0 /24 | [oMLX calibration correction #4930](https://github.com/jundot/omlx/pull/4930) | Frozen source QFN calibration correct forward positional/masks, sensitivity map & tensor index, matched TOTAL bits/bytes vs previous, xhigh coding long tools. Model QFN change reported only out_proj; dense27B oQ3e Chat KL -.027 is NOT source certification. |
| HIGH | **RS-21** 2,3,2,2,0 /22 | [Original-family MXFP4 QSA #64123](https://github.com/vllm-project/vllm/pull/64123), [MI355 fast #64405](https://github.com/vllm-project/vllm/pull/64405), [FP8 merged #61529](https://github.com/vllm-project/vllm/pull/61529) | Quant main KV vs indexer separately, 272B record vs FP8 512B; MI355 capacity +51%, c1 neutral, c256 +47% only capacity queue. Need GSM8K/GPQA/RULER true gate and exact gfx1030/Metal operators; no transplanted performance. |
| MED/HIGH | **RS-10** 2,2,3,3,0 /25 | [M1Max64 Q2 standard #4457](https://github.com/Niko1221/Strata/pull/4457) | Original IQ3_S physically at actual128/262K; Q2_0 4K/16K ~373/369PP,37.84/36.01TG capped512 not proof. |
| MED | **RS-22** 2,2,2,3,0 /22 | [oMLX source-family DFlash2 partial rollback #4865](https://github.com/jundot/omlx/pull/4865) | Recover GDN rollback on *partially accepted* MTP verify, correct HC layer mean, source M1 long real context. M5Max uncensored 103GB DFlash math90/code70TG; c4 swapping invalid; no owner projection. |
| MED | **RS-23** 1,2,2,3,0 /19 | [Basalt empty --dump-logits #119](https://github.com/jesdga95/basalt/issues/119) | Validate file byte-count/header/rows/hash before any KLD quality acceptance; ensure current owner Basalt report not silently missing data. No actual test executed. |
| MED | **RS-09** 2,2,2,3,0 /22 | [Strata VRAM reserve #4516](https://github.com/Niko1221/Strata/issues/4516) | Owner 5070Ti Linux actual live free VRAM and cache overshoot under long agent turns; other WDDM843→1289 PP not owner. |

Research rank = physical relevance and correctness urgency, not score-only sort. RS-15 exact quant packing on DeepSeek V4.1, RS-16 adaptive draft on dual5060Ti EXL3, RS-03 QFN MTP multi-stream oMLX #4916 remain supporting seeds rather than duplicate active rows.

## Next seeded deep-dive selection — 1–3 only

1. **RS-17 + RS-18 + RS-11**, source M1 64GB: trace oMLX bank joins/returns and DFlash adaptive scheduler across same M1 Qwen3.6 benchmark → source QFN oQ4e join → original IQ3S Paperniuk backend, with memory pressure countercontrols and true parked agent tasks.
2. **RS-19 + RS-23**, original source IQ3S on NVIDIA: Basalt current-main+#114+#117 exact deep context and valid reference logit dump. Seek independent same-card/CPU long test and reproducible RAM/VRAM/SSD statistics.
3. **RS-20 + RS-21 + RS-22**, source fidelity: corrected oQ sensitivity/HC/GDN vs mixed precision QSA KV and MTP rollback, source tensor maps and actual scored xhigh tool/coding quality; compare alternative false causes (extra bpw, batching, page-size budget).

## Fresh primary-source map added

- [M1 physical adaptive/fixed speculation concurrency #4935](https://github.com/jundot/omlx/issues/4935) — same GPU, DIFFERENT dense MoE/quant.
- [oMLX returned agent KV bank spike fix #4936](https://github.com/jundot/omlx/pull/4936) — QFN oQ4e M3Ultra (different M1).
- [Basalt original IQ3S host KV #117](https://github.com/jesdga95/basalt/pull/117) — RTX5080 matched specific stack, open.
- [oQ correct calibration forward #4930](https://github.com/jundot/omlx/pull/4930) — merged, no exact QFN IQ3S eval.
- [AMD QSA MXFP4 capacity #64123](https://github.com/vllm-project/vllm/pull/64123), [kernel fast path #64405](https://github.com/vllm-project/vllm/pull/64405), [Mamba-align scheduler #64161](https://github.com/vllm-project/vllm/pull/64161); MI355 only.
- [Basalt dump logit bug #119](https://github.com/jesdga95/basalt/issues/119) — quality instrumentation concern.
- [TensorFold idle-footprint/re-prefill #1572](https://github.com/ashhart/TensorFold/issues/1572), different M5Ultra/GLM.

## Negative/deprioritized and discovery debt

1. **No newly verified native IQ3S original M1 fully occupied128K/262K paired cold PP and continuous agent tasks**, no true CUDA5070Ti→MetalM1 production Relay, no multi-Mac shared KV correctness/cold restore; numeric targets HOLD.
2. **No exact new ISTA/ByteShape ShapeLearn original QFN optimized artifact** in targeted HF/source searches. Derived heretic/abliterated packs, reuploaded quants and model-list modified dates are NOT original source quality evidence. AREX-2 remains distinct dense27B model; no optimized source QFN AREX quant found.
3. **No original QFN oQ3e quantitative before/after score** in #4930: author says only out_proj bit width changes. Different dense27B + extra bits improves KL; do not call quality improvement free.
4. **No native AMD gfx1030 RX6800 16GBVRAM/16GBhost source-matching optimized QSA MXFP4/FP8**; MI355 support cannot transfer from CDNA to RDNA2. Physical RX7600 gfx1102 results not owner.
5. **No full correctness certification** from greedy matches or kernel passing; check dataset task success, tool outputs, SSE isolation and latest checkpoint.
6. **Basalt #114 main deep regression not proven resolved**, and #117 stacked, single-GPU only; zero-byte logits report needs verified fix.
7. Cross-family V4.1 packed-KV losslessness does not apply to freshly compressing BF16 QFN KV, and very large MXFP4 high concurrency capacity benefits do not imply single-client speed.
8. One-minute self-editing heartbeat remains disabled; no experiment or CODE deployment approved. HIGH control lifecycle unchanged.

**Discovery debt:** actual source M1 original IQ3S model/PLE/MTP tensor map; first-token trace and peak wired Metal; exact oQ5e/BF16 vs candidate xhigh AA-like≥38; state-format roundtrip and PLE Q8_0 file I/O; source long-context distinct code material; owner RX6800 host affordability, RTX5070Ti Basalt physical, Pascal real backend, longer completed multiagent tasks.
