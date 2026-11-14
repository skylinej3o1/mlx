# Project 51 research watch — November 14, 2026, 17:11 EST

Previous cutoff 2026-11-14T17:33:51Z; new cutoff 2026-11-14T22:11:31Z. Targeted connected GitHub scan, issues updated in window; not every issue was created in window. Research-only.

## New drafter watch: Tencent DSpine (NEW)
[Basalt #360](https://github.com/jesdga95/basalt/issues/360), updated Nov14 18:09Z; [Tencent DSpine](https://github.com/Tencent/DSpine); [checkpoint](https://huggingface.co/tencent/Qwen3.8-27B-DSpine-b16). Dense Qwen3.8-27B five-layer 16-token block 8192 sliding window. Request for converter/runtime, not implemented in Basalt. RTX5090 DFlash2 baseline on dense27B 53-59K agent prompts 44-53% draft acceptance, 2.38-2.90 output tokens/verification; no DSpine benchmark in Basalt. Do not extrapolate to QFN M1.

## Long-context practical MoE: Flint (UPDATED)
[Kapitsa #1257](https://github.com/nace-ai/kapitsa/issues/1257), updated Nov14 20:08Z. M4Max32GPU36GB, Flint40B-A2.5B int4 22.57GB, Kapitsa0.2.17, three weeks opencode coding-agent use, single slot headless. 38-token prompt short decode ~163-164 internal, 19.3K cold PP1257. Actual coding agent decode 12-22K 115-141, 60-83K 80-94, 134-154K 57-62, 178-179K 51.6-52.1 tok/s; prefix cached TTFT 0.3-1.4 sec. Model and M4 hardware differ from M1 QFN; quant quality user considers limit.

## Tool correctness regression (NEW)
[Strata #5979](https://github.com/Niko1221/Strata/issues/5979), updated Nov14 21:12Z: OpenAI tool JSON boolean emitted as string "True"/"False" for QFN across tested releases 0.2.7/0.2.9/0.2.11; current main code read not run. Schema-validity eval required, especially HaikuSwarm.

## Multi-request fused-kernel opportunities (NEW)
[oMLX #5273](https://github.com/jundot/omlx/issues/5273), updated Nov14 20:19Z. M5Ultra256 GLM5.3Flash 4bit, not M1/QFN. Batched B>1 fallback; experimental fold reuses B1 fused kernels. No spec aggregate 2 requests 55.1→78 (+42%), 4 requests 85.6→109.6 (+28%); adaptive DFlash 2 requests 69.1→81.2 (+18%), 4 requests 91.5→106.3 (+16%). Greedy divergence remains, no validated merged patch.

## Paperniuk status
[DS4 M1 fork](https://github.com/paperniuk/ds4/tree/m1-flash-next) last visible commit 9da1288 Nov12; [Splash M1 fork](https://github.com/paperniuk/splash) last d61103e Nov12. No new benchmark M1Max64 128K DFlash2 vs MTP confirmed in this scan. Existing concerns: speculative acceptance, batched parity, long-context overhead, memory budget.

## Priority decisions
Maintain original GSQ IQ3XXS minimum IQ3S preferred, QFN 128K/262K on two M1Max64 32GPU. PC 5070Ti16+64GB, RX6800 16+16GB host. Frozen first Basalt original GSQ IQ3S 32K INT8KV one slot spec1 no draft. No downloads, code edits, tests or CI authorized. Relay CUDA→Metal handoff unproven; oMLX SSD cache hash/rescan proposals from prior watch still relevant. Future tests: native MTP vs DFlash2 on same QFN quant at 32K/128K/262K, accepted tokens, TTFT, wall TG, memory, greedy parity, tool JSON schema, concurrency.

NEXT CUTOFF 2026-11-14T22:11:31Z.
