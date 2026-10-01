# Project 51 research watch — 2026-09-30 23:57 ET

Freshness boundary entering: **2026-09-30 23:19:38 UTC**  
Cutoff: **2026-10-01 03:57:17 UTC**

## Decision

Durable STATE and TARGETS changes; **no canonical numerical target movement**.

New consequences:
- add **Victoria** as a separate post-compression-recovery / capability-per-byte control after the frozen DASLab
  fidelity ladder;
- add a mandatory **MTP draft-asset integrity** gate before interpreting acceptance or TG;
- strengthen 64-GB Apple admission testing and common-system-prefix reuse tests;
- keep Strata at **0.1.30** pending a released/reproduced 0.1.31.

## RECOVERED CURRENT — Victoria adds a post-compression-training control

Model card: https://huggingface.co/rmonsurate/Victoria

The release surfaced in this conversation inside the current watch window. No reliable repository publish timestamp was
available from the retrieved model page, so classify the artifact as **RECOVERED CURRENT**, not as a timestamp-proven
new strict-window HF commit.

Victoria:
- prunes 44% of Flash-Next experts, 512 -> 288/layer, while keeping 5.9B active parameters/token;
- retrains the compressed model at 4-bit with QAD over 128M coding/tool-use tokens;
- NVFP4: 48.0 GiB weights + 95.4 GiB lookup table;
- GGUF Q4_K_M: 49.17 GiB resident weights.

Published quality:
- NVFP4 Terminal-Bench 2.1: **70.04% avg@3** (67/89, 61/89, 59/89), HumanEval 97.0%;
- GGUF: **75.28% (67/89)** Terminal-Bench vs original Flash-Next **88.76% (79/89)**; 84.8% retained on that
  benchmark; HumanEval 93.2% avg@5.

Draft-head decomposition on one B300:
- off: **134.7 tok/s**;
- pruned, unretrained head: **269.3**, 64.1% acceptance;
- retrained head: **279.6**, 67.6%.

On M3 Max 128 GB, GGUF MTP is reported ~26.8-27.8 -> 34.3-38.0 tok/s at 70.4% acceptance.

Classification: **RECOVERED CURRENT / new Project-51 experimental lane**. This is not evidence for DASLab IQ3_XXS
source fidelity. Add it only after the frozen PTQ ladder and score source fidelity separately from absolute capability.

## NEW — Strata #327: silent MTP-range-download corruption

Issue created 01:51:26 UTC:
https://github.com/Niko1221/Strata/issues/327

An HF mirror ignored HTTP Range and returned full-file HTTP 200 content; `mtp_fetch.py` kept the first requested-size
bytes. 20/31 `mtp.*` files therefore held safetensors headers/unrelated shard data rather than their tensors.

Why existing checks failed:
- output file lengths were correct;
- manifest hashes were generated from the already-wrong downloaded bytes;
- the main model decoded normally;
- MTP alone silently collapsed.

Observed:
- corrupt: `0 of 0` drafts on defaults; forced windows 0/765 accepted, NaN draft probabilities;
- after re-fetch: forced-window **42.7 -> 69.9 tok/s**, acceptance 31.8%;
- normal serving: Q2_0 93.5 tok/s at 44-54% acceptance; IQ3_XXS 77.4 tok/s at 59-71%.

Classification: **NEW MTP certification gate**. Require authoritative ranged-byte validation / HTTP 206, source
revision and byte-range hashes, finite tensor sanity and separate offered-vs-accepted telemetry before interpreting MTP.

## UPDATE — real 64-GB TensorFold 0.6.0 Flash-Next admission still inconsistent

Issue #95 comment at 01:55:26 UTC:
https://github.com/ashhart/TensorFold/issues/95#issuecomment-5923160330

M5 Pro 64 GB, TensorFold 0.6.0, Flash-Next + PLE-on-SSD + 24-GiB SSD experts:
- advertised context: 65,536;
- after a tiny request, 65,380+64 refused, "fits up to" ~50,624;
- even 50,618+64 can prefill ~4.5 min and then be refused;
- as the first request, 65,383+64 can prefill ~5.8 min and then be refused;
- a 34K conversation resumes correctly with ~34,432 cached in ~2.0 s.

One diagnosed contributor is 256-position indexer-capacity allocation being profiled per valid token, allowing a tiny
request to inflate remembered per-token cache cost. It does not explain the full last-chunk failure.

Classification: **UPDATE / 64-GB capacity gate**. Advertised window is not accepted capacity until first-request,
post-tiny-request, post-retained-turn and final-chunk paths agree. No M1 numerical transfer.

## NEW — TensorFold #169: Flash-Next lacks message-start/common-system-prefix reuse on CUDA

Created 03:08:04 UTC:
https://github.com/ashhart/TensorFold/issues/169

One DGX Spark agent workload shares ~30.7K system+tool tokens across new conversations:
- Flash-Next 0.5/0.6: new conversation 0 cached, ~23.5 s; same-conversation next turn ~35.7K cached, 0.24 s;
- Qwen3.8-27B: new conversation ~30.7K cached, ~4.2 s; next turn ~35.7K cached, 0.4 s.

Classification: **NEW multi-agent prefix-reuse mechanism evidence**. Add a new-conversation/common-system-prefix
checkpoint test; do not count logical shared prefixes as capacity/TTFT savings until the runtime materializes them.

## NEW — Strata #328 independently reproduces the 0.1.30 multi-session `tail` failure

Created 01:53:22 UTC:
https://github.com/Niko1221/Strata/issues/328

RTX A4500 / Linux / IQ3_S / 262K with multiple OpenAI sessions can raise `KeyError: 'tail'` in the HTTP streaming
bookkeeping while the engine stays healthy.

Classification: **NEW independent reproduction / KNOWN failure family**. Consistent with #266 request-state ownership.
Keep 0.1.30 out of agent-production certification until the 0.1.31 request-id fix exists and passes concurrency/abort tests.

## NEW / target-unaffected — Strata #326 third-party PLE-key format mismatch

Created 01:35:20 UTC:
https://github.com/Niko1221/Strata/issues/326

OrcaRouter IQ3_XXS `--compat-bf16` packs can be rejected by the native loader from 0.1.25 onward because the packer
stores the PLE key as BF16 while the loader now recognizes IQ3_XXS/IQ4_XS GGUF keys as native.

Classification: **NEW third-party artifact compatibility bug**. Canonical DASLab GSQ-RCO uses the native path and is
not implicated; reinforces the existing tensor-kind/file-interpretation gate.

## NEW — independent fast IQ2_XS agent coding run, quality unsuccessful

Strata #316 created 23:51:16 UTC:
https://github.com/Niko1221/Strata/issues/316

RTX 4090 / 64-GB Linux / IQ2_XS / 65K:
- 80 responses / 37,449 output tokens;
- reported weighted generation **166.36 tok/s**, calculated from predicted decode milliseconds rather than wall time;
- 84.9% MTP acceptance;
- 12.8-min agent harness.

The generated browser game executed but the reporter rejected its physics/game feel. Reasoning was off, there is no
higher-quant/runtime control, and the speed metric is not whole-request throughput.

Classification: **NEW qualitative caution**, not a quality score or TG ruler.

## NEW / low-transfer — MLX M3 Ultra/macOS 27 MathModeSafe compiler defect

Issue #4603 created 01:51:59 UTC:
https://github.com/ml-explore/mlx/issues/4603

A custom 6-bit Metal kernel returns whole wrong rows on M3 Ultra/macOS 27.0 under `MathModeSafe`; identical source
is exact under Relaxed/Fast, on M2 Max, and when shader validation perturbs code generation. A Metal-cpp reproducer
points at the OS runtime compiler.

Classification: **NEW exact-hardware/compiler warning, no M1 transfer**. Keep exact hardware+OS+compiler-mode parity
tests for custom Project-51 Metal kernels.

## NEW / low-transfer — vLLM Qwen4Exp SM100 skinny GEMMs

PR #59214 merged 03:40:55 UTC:
https://github.com/vllm-project/vllm/pull/59214

B200 Qwen4Exp BF16 low-latency GEMM plans reduce many M=1-8 projection microkernels from ~5-8 us to ~2-6 us
(roughly 1.2-2.7x depending on shape). This is evidence that small-row specialization still has material headroom on
the right architecture, but it does not transfer numerically to RTX 5070 Ti sm_120 or Apple7.

## Strict-window negatives / exclusions

- Strata latest release remains **0.1.30**; no 0.1.31 release/commit by the cutoff.
- TensorFold latest release remains **0.6.0**.
- oMLX remains **0.7.0** with no relevant strict-window Flash-Next commit.
- DASLab Flash-Next GSQ-RCO main remains **ed59f92**; no new checkpoint/allocation/benchmark.
- no material TurboQuant-MLX, MoEspresso or Ishizuki update.
- vLLM issue #59534 was created at **03:57:25 UTC**, eight seconds *after* the 03:57:17 cutoff and is deliberately
  excluded from this watch.

## Canonical target state

Unchanged:
- RTX 5070 Ti IQ3_XXS cold PP: **3,000 / 2,900 / 2,750 / 2,500** at 32K/64K/128K/262K;
- conditional 262K/64-GB fit prior: **~90%**;
- IQ3_XXS AA>=38 **~85%**;
- IQ3_XXS AA>=40 **~65%**;
- IQ3_S AA>=40 **~80%**;
- K6/V4 long-horizon quality **~60-70%**;
- dual-M1 Flash target: **~40 TG @128K / ~400 PP**.

## New hard boundary

**2026-10-01 03:57:17 UTC**
