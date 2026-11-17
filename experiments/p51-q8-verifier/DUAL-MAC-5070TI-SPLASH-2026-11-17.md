# Project 51 focused evidence — November 17 2026

**Strict interval:** 2026-11-16T15:58:46Z to 2026-11-17T11:51:16Z. [Full watch](./RESEARCH-WATCH-2026-11-17-0651.md). All measurements below are other people's source-reported results, not owner's hardware results.

## Direct 5070 Ti Basalt figure and exact comparator limits

Basalt community #394/#401 patches to docs/community/benchmarks.json: hexhamallstar same Windows RTX5070Ti16 300W PCIe4×16, Ryzen5700X3D, **96GB** RAM; preset community-1, context66661, INT8 KV, code d3b7574. NVFP4 prefill16K3348.1/64K3859.6, decode overall78.4, conv60.4, struct85.5, prose64. IQ3_XXS prefill16K3259.5/64K3664.7, decode overall100.4, conv72.7, struct112.9, prose75.3. Both have draft acceptance >60%; no full agent correctness equivalence or source SHA proof for ISTA original pack. Do not compare weighted drafted TG against owner planned no-draft first baseline. Freeze RTX5070Ti16/CoreUltra7 265F/64GB host first Basalt **original ISTA GSQ-RCO IQ3_S v2 .basalt actual32K slot1 INT8KV spec1 no draft**, CPU double and tool check. No benchmarks run by assistant.

## Split prefill with replicated decode — paired-Mac novel path

[TensorFold #3688](https://github.com/ashhart/TensorFold/pull/3688) created11:51:03Z exactly 13 seconds before cutoff, OPEN. On dual M5 Ultra each256GB and Thunderbolt5, Flash-Next MLX6bit: existing pair exchanges 48 expert-stage and36 GDN partials per step (about0.4ms hop vs0.2ms layer local). New code reproduces complete rank0+rank1 decode on both Macs, one ACK per step, yet retains TP partitioning for prompt. 49 requests drafted median pair51.1→115.3 tok/s, plain26.3→87.1, one Mac126.4 drafted/99.6 plain. 16.4K prompt time to first token2.36s pair/5.17s single, long requests finish faster92s pair/166s single, short requests44.7s vs40.3s (cross-over). 49/49 reply hash equality with and without cache, 147 continuous hashes equal; peer-kill detection now10–12s vs2s. Wired169–179GB EACH node. Cannot fit MLX6bit 170GiB on owner's M1Max64. Concept can inform physical128K QFN GSQXXS 2-M1 plan only after model/state residency, concurrency and TB4 proof; not evidence that CUDA PC can transfer GDN/QSA/PLE/MTP to M1.

## M1 and upstream Splash

Paperniuk/splash#63 new Nov16 and17 comments: M2Max64 60K full-day replays stable52–59TG even with recurring growth-paused logs, but worst queued wait336s; original M1Max64 after2 days normal 29.7–35TG, idle first request16.9 then recovers, severe prior16.8 sustained only after heavy150–220K SSD-spilled KV agent sessions. m1.1 start fixed, no proven long-agent stability. Paperniuk DS4/Splash no new main commits. Keep historical pristine GSQXXS M1Max64 physically128K PP278/TG34.2 physically259K PP258/TG31.7 near57GiB unchanged.

[Upstream Splash #780](https://github.com/incoai/splash/pull/780) OPEN stacked onto1.6.2 #769 OPEN. M5Pro64 reported QFN2K decode1.14× solo/1.28× 4 lanes, dense27B GGUF1.22×; 62 pi/Codex 27B full requests median1.23× and decode1.46×. Draft tree verifies up to16 rows, copy prior prompt up to15 tokens, price-driven adaptive steps. GDN cached state dense27B152.6MiB→46.9 via INT8 in32/BF16 scale; exact opt-in available; default auto-verify rows not identical run-to-run, all-verify repeatable. Four agent overall first tokens accumulated worsened218→259s even as median request improved. NOT M1 port or physical128K pristine QFN match; do not quietly take INT8 state in fidelity-first setup. 1.6.2 #769 repairs quoted user special control tokens injection (previous forged tool turn obeyed8/20 vs after0/20) and endless JSON whitespace, showing tool correctness risk.

## Quant and other agent evidence

[oMLX #5317](https://github.com/jundot/omlx/pull/5317) author KL at same file bytes for dense27B: Q3 12.2GiB FLORES stock0.066 refined0.059 oQh0.040, code0.052/0.052/0.037; Q4 15.2GiB FLORES0.016/0.014/0.011, code0.013/0.012/0.011. No completed real coding-agent battery. Flash-Next oQh min oQ2 70.8GiB (oQ3 84.9, oQ4 98.9) exceeds single M1Max64; Splash/ANE/helper refuse new format. QFN original GSQXXS floor and old independent sady GPTQ 27B quality track are not displaced.

[Kapitsa #1302](https://github.com/nace-ai/kapitsa/pull/1302) merged one-buffer cache growth copy accounting, OTHER dense27B near 24GB cap increases maximum served agent prompt from9,475 to13,274, not throughput. [Strata #6136](https://github.com/Niko1221/Strata/issues/6136) on OTHER RTX4080+64GB host, engine0.1.60 equal chunk prefill after 66,968 prompt+9 tail rereads16,754 rows, 6.4× slower than0.1.54 despite faster initial prompt. This is essential for long-context multi-turn agent test design; not a Basalt user problem.

[Basalt #391](https://github.com/jesdga95/basalt/issues/391) grammar mask copy from legacy CUDA stream racing sampling nonblocking stream caused masked draws being refused and disabling strict JSON schema. Fix main commits same-stream asynchronous copy, author 35/35 schema-valid on RTX5090 dense27B. [Basalt #400](https://github.com/jesdga95/basalt/pull/400) cancellation resources OPEN. [Strata #6138](https://github.com/Niko1221/Strata/pull/6138) indented bare function tool call stream parser fix OPEN; [oMLX #5345](https://github.com/jundot/omlx/pull/5345) JSON-string fragment tool array parse fix OPEN. HaikuSwarm should verify tools actually executed and history causal groups, not merely token speeds.

[vLLM #65186](https://github.com/vllm-project/vllm/pull/65186) merged internal GDN checkpoints at64 rows with conv context on CUDA, fake one-layer tests only. It is a Relay component design reference, NOT a complete QFN source transfer or end-to-end TTFT proof. [Qwen Code#17527](https://github.com/QwenLM/qwen-code/pull/17527) merged stateless Harness idle-session design with durable journal and irreversible teardown; Molt continuation idempotence useful.

## Qwen4 official status

QwenCloud changelog Nov16 qwen4-max API and Nov11 preview only; Alibaba promised future smaller open-weight Qwen4 with unspecified parameters, sizes, licenses, release date. No new official Qwen4-Flash/27B/35B-A3B checkpoint by strict cutoff. Chinese social recirculates Qwen4-Max and pre-existing dense27B Intel-kernel inference; no new verified numeric Flash or 35B rumor. Never use flagship2.4T/71B as Flash spec.

**Boundary:** no user hardware/weights/runtime/CI action. All updates are docs only. Next strict cutoff 2026-11-17T11:51:16Z.
