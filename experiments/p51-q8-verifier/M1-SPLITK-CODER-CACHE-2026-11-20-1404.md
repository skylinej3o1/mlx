# Project 51 — November 20 M1 Split-K, pruned Coder, cache and agent fidelity

[Strict research watch](./RESEARCH-WATCH-2026-11-20-1404.md) · new cutoff **2026-11-20T19:04:42Z** · previous **2026-11-19T23:44:00Z**.

## 1. Direct Apple7/8 potential and disconfirmations

[Paperniuk/splash #73](https://github.com/paperniuk/splash/pull/73) created Nov20 03:06Z targets **M1/M2 narrow-grid prefill Split-K**. Existing Apple7/8 MMA no K split leads to too few group tiles for e.g. QFN HC down Q8_0 320×10240; K splitting parallelizes. **Actual evidence other M2 Max38GPU, QFN Q2_0**: 64K history prefill append128 rows fused step430.82→370.06ms (-14.1%), 384 rows926.64→890.04(-4%), 2048 rows4100.6→4071(-0.7%). Warm server append162 tokens544.3→504.8ms (+7.4% PP), 416+3.1%,1035+0.8%. **NON-EXACT numerics**: changed addition order, teacher logit KL0.0053, top1 97.2% vs base Q2_0. Dense27B MLX4 low-row gain M2 also measured, but that is not owner format. [Paperniuk #72](https://github.com/paperniuk/splash/pull/72) same contributor new IQ2 routed expert tile M2 UD-IQ1_S B1 decode+6.5%; deliberately does **NOT** include IQ3XXS/IQ3S because no whole-layer benefit / M1 slowdown. Both OPEN, no merged original owner benchmark. M1Max32GPU physical128K/259K outcomes and exact CPU/Metal transcript remain **UNKNOWN**.

## 2. Authentication and meaning of DASLab Coder benchmark (rediscovered older Oct checkpoint)

[Original provider model card](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF); Oct revision [bba88856f8c3c0c9e40e45f82d05e228b814ac43](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF/commit/bba88856f8c3c0c9e40e45f82d05e228b814ac43). Pruned half the experts 512→256, retained expert weight precision~3.5 bits, transformer29.6GB resident plus unchanged streamable28.8GB lookup table =58.4GB artifact. "IQ1_M" overall effective bits after pruning is **NOT** an actual 1-bit quant of surviving weights. First-party latest xhigh SWEbench BF16 **82.8** vs Coder **79.2**, LiveCodeBench v6 BF16/Coder both **87.43**. Old v1 Coder SWEbench75.6, LCB86.28 now SUPERSEDED. These tests are not independent, not measured on original pristine GSQ IQ3_XXS, not owner M1 long context and not completed multi-agent coding tasks. [Splash #789](https://github.com/incoai/splash/pull/789) added this model to install/catalog on Nov20, and optional three-lane warm prefill scheduling for >=128GB Mac; does not prove a 64GB original memory/TG/tokens restored. Keep Coder candidate, never silently replace IQ3XXS quality floor.

## 3. Agent cache economics / correctness

| Primary source | Status Nov20 | Actual data from non-owner hardware | What matters for 2 M1Max64 |
|---|---|---|---|
| [Splash #789](https://github.com/incoai/splash/pull/789) | OPEN NEW | M5Studio128, 94/146K cold + 6 warm followups: p95 warm TTFT108.99→11.34s; overall output throughput13.935→13.985, heldback10/12 both | Fairness/latency, not raw completed tasks/hour or M1 source gain |
| [oMLX #5321](https://github.com/jundot/omlx/pull/5321) | MERGED12:43Z | M5Pro64 native dense27B, two126K sessions S=4.3GB KV, batch join peak +2.06S→+.13S; join wall time worse | Need transient RAM admission and no silent task changes |
| [oMLX #5253](https://github.com/jundot/omlx/pull/5253) | MERGED12:44Z | M5Pro64, two64K quantized cache rollback: +4.4GB→+.38GB, ~203→106ms | Critical for several long resident agents; no original GGUF proof |
| [Strata #6288](https://github.com/Niko1221/Strata/pull/6288) | OPEN UPDATED | 2x CMP50HX Swift IQ3S SSD durable stage snapshots, 165.6K cold66.1→8.4s restored | Check exact QSA/GDN/PLE identities/SSD after restarts |
| [Basalt #382](https://github.com/jesdga95/basalt/pull/382) | OPEN UPDATED | QFN cache SSD stream restores from files without ~2GB whole-image temporary RAM for120K | Strong 64GB RAM-pressure idea; not shipped |
| [oMLX #5454](https://github.com/jundot/omlx/issues/5454) | NEW / FIX MERGED | M3Max64 native QFN oQ4e SSD writer held Metal buffer-clear lock; engine evictions after long prefill | Preserve pool reclamation and SSD-worker lock fairness |
| [Splash #790](https://github.com/incoai/splash/issues/790) | OPEN NEW | M5Ultra256 Unsloth QFN Q8, reasoning OFF + json_schema 15/1486 failures in1.7, prior0/5106 | Schema-stream correctness matters more than TG |

## 4. NVIDIA release quality/correctness and control

[Strata v0.2.17](https://github.com/Niko1221/Strata/releases/tag/v0.2.17) fresh Nov20 engine0.1.63: rank7 expert tail-skipping now OFF default after quality complaints; 94.5tok/s vs73.4 on different RTX5090 but source output differs. 5070Ti-class new `STRATA_ADAPT_FETCH=2` default ON for single ≤16GB RTX50; 5060Ti other model+draft test +2–23% TG, only9/48 exact output sequences, not acceptable to call quality-neutral or transfer to owner original GSQ frozen no-draft. 64GB model RAM budget change limited to Unsloth UDQ4KXL/IQ4XS, not original source IQ3S. Updated other topology [#6423](https://github.com/Niko1221/Strata/issues/6423) and [#6431](https://github.com/Niko1221/Strata/issues/6431) show regressions from new per-GPU defaults. [Basalt #430](https://github.com/jesdga95/basalt/issues/430) reporter Nov20 same RTX5080/96 host UDQ4KXL complete successful retest after clearer logged placement 12.5GPU/65.0RAM, desktop clean, mean62.6 TG vs v0.4.1; the earlier open-correctness caveat now **verified resolved for that other rig**, not universal. Basalt tool-parser [#429](https://github.com/jesdga95/basalt/issues/429) still open. First owner Basalt run frozen original GSQ IQ3S v2 one5070Ti16, host64 DDR5-4800, physical32K INT8 KV one slot spec1 NO DRAFT, no owner run authorization.

## 5. What hasn't changed

No official Qwen4 Flash/27B open weights/size/PLE/MTP manifest from [Alibaba Chinese changelog](https://platform.qianwenai.com/docs/changelog/models) or [Qwen HF](https://huggingface.co/Qwen), so competing large and small rumors remain unsupported. No full CUDA RTX5070Ti→external Metal Splash original-GSQ QFN GDN/QSA/PLE/MTP exact Relay; native oMLX helper remains separate. No same-hardware 2x separate M1Max64 distributed benchmark, no RX6800 **non-XT** with **ONLY16GB system RAM** source model fit proof. Prior M1 orig GSQXXS128K PP278/TG34.2;259K PP258/TG31.7 unchanged. May2027 TG forecasts not achieved. No quant floor downgrade.

## 6. Exact proposed future quality gate (DO NOT EXECUTE without HIGH)

Use equal original checkpoint + chat template, exact original GSQ XXS vs pruned Coder, and full coding-agent tasks at *physical*128K/259K with repeated context truncation, tool-like text containing closing-delimiter literals, first answer after restart, strict schemas and file-content SHA256. Count correct finished tasks per hour and per GB, not just tok/s. For split-K #73 validate per-projection logit KL/routing and entire agent task, reject quality regression even if low-row PP improves. For 3–5 agents test transient peak memory during batch join/rollback, compaction, SSD and fairness with two genuinely separate64GB domains.

Documentation only; no owner model, code, CI or hardware action was authorized by this research continuation.
