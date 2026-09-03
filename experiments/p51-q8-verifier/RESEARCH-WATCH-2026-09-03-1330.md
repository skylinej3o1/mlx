# Runtime Research Watch — 2026-09-03 13:30 ET

Scope: fresh external runtime/model scan after `RESEARCH-WATCH-2026-09-03-1030.md`, plus a deliberate backfill pass for direct receipts on the user's machine classes that were missing from the formal research chain.

Targets remain:

- Qwen3.8-Flash-Next;
- Qwen3.8-27B;
- DeepSeek-V4-Flash-0731 / DS4;
- especially M1 Max 64 GB, M1 Max 32 GB, RTX 5070 Ti 16 GB + 64 GB host RAM, RX 6800 16 GB + 32 GB host RAM, and the exact 2x M1 Max 64 GB / TB4 topology.

Dedupe policy for this pass:

- `RESEARCH-STATE.md` plus every formal delta after the 2026-09-02 05:30 consolidation were treated as canonical current state;
- the older formal Aug-31 / Sep-1 watch chain was also checked before classifying recovered hardware receipts;
- an older external source absent from that chain is labeled **NEW-TO-REPO BACKFILL**, not "new today";
- only activity after the prior 10:30 ET pass is labeled **FRESH POST-CUTOFF**.

This pass does **not** modify the certified exact-Q8 verifier state. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling data only**.

## Executive delta

1. **NEW-TO-REPO BACKFILL — direct M1 Max 64 GB Qwen3.8-27B serving measurements exist in the oMLX benchmark corpus.** A 32-GPU-core M1 Max / 64 GB 4-bit profile without MTP or DFlash measured roughly 18.9 tok/s at 1K, 17.9 at 8K, 15.1 at 32K, 13.3 at 64K, and 10.3 at 128K; short-context B4 aggregate reached 44.9 tok/s. A separate 8-bit M1 Max profile measured 10.9 tok/s B1 and 38.4 tok/s B4 at the short-context point. These are serving baselines, not P69 exact-verifier measurements.
2. **NEW-TO-REPO BACKFILL — RTX 5070 Ti 16 GB has a strong direct 27B 3-bit + MTP receipt.** On `UD-Q3_K_XL`, native MTP fits a 24K Q8-KV window; a controlled 8K cache-busted four-workload test averaged 97.2 tok/s, while tool-call generation in the 24K agent run was 111-115 tok/s. The same operator reports the tested IQ4_XS 4-bit file spilling to ~0.4 tok/s, making VRAM fit/quant choice first-order on this card.
3. **NEW-TO-REPO BACKFILL — RX 6800 16 GB has a direct Qwen3.8-27B Vulkan receipt.** In one real tool-chain task at 32K context, Q3_K_M produced ~12.7 tok/s with ~129-130 tok/s prompt processing; UD-Q2_K_XL produced 29.3 tok/s with 156 tok/s prompt processing and 10.68 GB VRAM use. This is a one-task community result, so treat the Q2 quality conclusion as provisional rather than a general quality guarantee.
4. **NEW-TO-REPO BACKFILL — RTX 5070 Ti 16 GB now has direct Flash-Next numbers.** A Windows / 64 GB DDR4 / RTX 5070 Ti 16 GB operator reports ~17-18 tok/s real chat generation at 128K using llama.cpp b10718, IQ4_XS, Q4_0 KV, Flash Attention, Auto-Fit, mmap/lazy mode, and one GPU. A separate Q8_0 artifact reports 11.3 tok/s single-stream decode on the same GPU class. The spread reinforces that quantization/residency policy is part of the performance result, not incidental metadata.
5. **NEW-TO-REPO BACKFILL — single M1 Max 64 GB has a direct DS4-0731 decode receipt.** A patched llama.cpp / IQ3-XXS (~104 GB) / 64K-context report progressed from ~8 tok/s decode and ~30 tok/s prefill to **90+ tok/s prefill and 7+ tok/s decode** after tuning. A second same-thread M1 Max 64 GB operator reports an IQ2XXS DS4/SSD-streaming point around 8-10 tok/s prefill and 10 tok/s decode. These are single-node community receipts; they do not supply the still-missing exact two-M1 0731 TG.
6. **FRESH POST-CUTOFF — llama.cpp #28330 removes an unused Flash-Next indexer V-cache allocation.** Qwen4Exp's indexer memory only needs cached indexer keys, but the generic KV object also allocated V storage. The PR removes that waste. No end-to-end memory saving or TG number is posted yet, so this is capacity-headroom mechanism evidence, especially relevant to constrained machines, not a fit guarantee.
7. **FRESH POST-CUTOFF — DS4 distributed/current-agent work moved.** PR #861's refreshed two-Radeon-8060S/TB5 layer-pipeline numbers are 250 tok/s prefill at ~6K, 274 tok/s at ~23K, 15.5 tok/s short decode, and ~14.3-14.4 tok/s over a 6,144-token thinking run. Its two-client batched-session path reports +3% to +14% aggregate versus serial. PR #963 separately reproduces and fixes DeepSeek text-tool observations failing as false context overflows on M5 Max. These are topology/correctness updates, not M1 performance receipts.
8. **FRESH POST-CUTOFF — oMLX #3405 fixes an MLX 0.32.2 Qwen3.8-27B VLM compatibility regression.** A scalar temporal-repeat argument is normalized before `mx.repeat`; validation includes a real 3,116-image-token Qwen3.8-27B screenshot and Flash-Next image/tool checks. No raw-speed claim.
9. **NO CHANGE — exact dual-M1 and exact Layr frontier.** No sustained 2x M1 Max Flash-Next TG or 0731 TG appeared after the prior pass, and the Layr exact challenge has no post-cutoff submission update.

## Qwen3.8-27B — M1 Max 64 GB direct serving baseline

Primary no-MTP/no-DFlash 4-bit source:

https://omlx.ai/benchmarks/performance/xtobxdbz

Hardware/runtime:

- M1 Max, 32 GPU cores;
- 64 GB unified memory;
- Qwen3.8-27B 4-bit;
- oMLX v0.5.7;
- code/Python benchmark context;
- MTP off;
- DFlash off.

Reported curve:

| Context | PP tok/s | B1 TG tok/s |
|---:|---:|---:|
| 1K | 91.0 | 18.9 |
| 4K | 90.9 | 18.3 |
| 8K | 90.1 | 17.9 |
| 16K | 88.3 | 16.3 |
| 32K | 84.8 | 15.1 |
| 64K | 76.8 | 13.3 |
| 128K | 60.0 | 10.3 |

Short-context batching on the same profile:

- B1: 18.9 tok/s;
- B2: 22.0 tok/s aggregate;
- B4: **44.9 tok/s aggregate**.

The 8K page reports roughly 17.8 GB active-MLX peak but ~39.9 GB system-used peak / ~48.8 GB process-footprint peak. Therefore **do not infer that the same profile fits a 32 GB M1 Max merely from the MLX-active number**. No exact M1-Max-32 receipt was found in this pass.

### Separate 8-bit profile

Source:

https://omlx.ai/benchmarks/performance/hh0i6n6t

M1 Max 32c / 64 GB / oMLX v0.6.2, no MTP/DFlash:

- B1: 10.9 tok/s;
- B2: 21.2 tok/s aggregate;
- B4: 38.4 tok/s aggregate;
- 1K active-MLX peak: ~28.3 GB;
- system-used peak: ~48.2 GB.

A related 8-bit context profile on the same hardware/runtime family reports roughly 10.9 / 10.7 / 10.6 / 10.2 tok/s at 1K / 4K / 8K / 16K.

Source:

https://omlx.ai/benchmarks/performance/b4905hk1

The useful conclusion is not that 4-bit universally beats 8-bit by a fixed factor. The benchmark corpus contains materially different oMLX builds, acceleration settings, and workloads. Preserve each profile as a profile. Still, the direct same-generation result is valuable: a 64 GB M1 Max can serve 27B at high-teens B1 in a favorable 4-bit baseline and can reach materially higher aggregate throughput with batching.

### Separate accelerated 4-bit signal

Source:

https://omlx.ai/benchmarks/performance/s4s92tx7

A different M1 Max 32c / 64 GB / oMLX v0.6.3rc2 profile with DFlash enabled reports **23.5 tok/s at 32K**. Keep this separate from the no-DFlash curve above. It is evidence that serving-side speculation can materially move 27B on M1-generation hardware, not evidence for the frozen native exact-verifier ruler.

## Qwen3.8-27B — RTX 5070 Ti 16 GB direct receipt

Source:

https://github.com/aipruner/qwen3.8-3bit-test-in-16GB-GPU

Setup:

- RTX 5070 Ti 16 GB, CUDA / WSL2;
- `Qwen3.8-27B-UD-Q3_K_XL.gguf`, 12.51 GiB;
- native MTP daily-driver profile at 24,576 context;
- Q8_0 K/V cache;
- MTP max depth 4.

Measured 24K agent-run generation by output type:

- tool calls: **111-115 tok/s**;
- Chinese prose: ~80 tok/s.

Controlled cache-busted 600-token A/B at 8K on the same PR image:

| Workload | native MTP | DFlash2 |
|---|---:|---:|
| Python | 110.0 | 114.4 |
| HTML | 121.6 | 110.4 |
| English prose | 76.7 | 81.3 |
| Chinese prose | 80.7 | 62.7 |
| Mean | **97.2** | 92.2 |

The important fit warning is equally valuable: the tested IQ4_XS 4-bit target at 8K fell to about **0.4 tok/s because it spilled**. On this exact 16-GB card, the operator's 3-bit target plus native-MTP head is the working high-throughput lane; adding the DFlash2 model consumed enough VRAM to reduce the usable context window and was not a net agent win on this target.

Host-RAM capacity is not identified in the repo's primary setup table, so classify this as an **exact GPU-class receipt**, not an exact match to the user's 64-GB host-RAM desktop.

## Qwen3.8-27B — RX 6800 16 GB direct receipt

Source:

https://zenn.dev/omohikane/articles/qwen38-test-my-rx6800

Setup:

- RX 6800 16 GB;
- llama.cpp Vulkan;
- LiteLLM/OpenCode-style tool task;
- fresh session;
- 32,768 context for the successful Qwen3.8 runs.

Measured on the author's one configuration-inspection agent task:

| Quant | Prompt | TG | VRAM / note |
|---|---:|---:|---|
| Q3_K_M | ~129-130 tok/s | ~12.7 tok/s | slower but detailed/stable |
| UD-Q2_K_XL | **156 tok/s** | **29.3 tok/s** | ~10.68 GB VRAM |

The author judged the Q2 answer roughly comparable on this one task, but the sample is too small to treat that as a general quality guarantee. The robust machine-level result is that **27B can run usefully on RX 6800 16 GB and the chosen low-bit quant dramatically changes speed/headroom**.

The article does not establish the host-RAM capacity in the measurement section, so this is an exact GPU-class receipt, not an exact RX6800-16 + 32-GB-host match.

## Qwen3.8-Flash-Next — RTX 5070 Ti 16 GB direct receipts

### IQ4_XS / 128K / 64-GB-host operational report

Source:

https://jdssl.top/index.php/2026/09/01/5070ti16g-run-qwen-3-8-flash-next-iq4x-gguf/

Hardware/runtime:

- RTX 5070 Ti 16 GB;
- 64 GB DDR4 host RAM;
- Windows;
- llama.cpp b10718;
- IQ4_XS GGUF (~90.8 GiB in the operator's model);
- 128K context;
- Q4_0 K/V;
- Flash Attention;
- single GPU;
- Auto-Fit + mmap + Lazy Mode;
- Hermes Agent.

Reported real chat generation: **~17-18 tok/s**, described as stable after warm-up.

This is unusually useful because it matches both the user's GPU VRAM and host-RAM class. It also demonstrates that Flash-Next does not need the entire ~90-GiB file resident in VRAM; the result depends on selective GPU residency plus host/mmap/lazy behavior.

### Independent Q8_0 same-GPU-class receipt

Source:

https://huggingface.co/sigmanih/Qwen-Qwen3.8-Flash-Next-GGUF-Q8_0

Measured on RTX 5070 Ti 15.9 GB:

- single-stream decode: **11.3 tok/s**;
- prompt processing: **5 tok/s**.

Do not compare 11.3 and 17-18 as if they differed only by quant bit count: the artifacts, residency/offload policy, context, and runtime configuration differ. The pair is still useful evidence that **quant/residency choices can move this 16-GB Flash-Next deployment by a large amount**.

No direct RX 6800 Flash-Next receipt was found in this pass.

## DeepSeek-V4-Flash-0731 — single M1 Max 64 GB backfill

Source:

https://www.reddit.com/r/LocalLLaMA/comments/1vncerl/deepseekv4flash0731_on_64gb_macs/

Primary operator:

- M1 Max 64 GB MacBook;
- patched llama.cpp;
- IQ3-XXS quant, ~104 GB;
- context limited to 64K;
- initial report around 8 tok/s decode / 30 tok/s prefill;
- later tuned update: **90+ tok/s prefill / 7+ tok/s decode**.

The same operator notes that using DSpark to push decode higher would consume about 8 GB more memory and displace expert cache, hurting prefill; that is a proposed tradeoff, not a clean measured DSpark A/B.

A second M1 Max 64 GB operator in the thread reports DS4 + SSD streaming / IQ2XXS around **8-10 tok/s prefill and 10 tok/s decode**.

### Interpretation beside existing exact dual-M1 evidence

Keep the already-canonical two-node facts separate:

- pre-0731 DS4 #607 exact 2x M1 Max 64 GB / TB4: ~10-13 tok/s decode, ~150-163 tok/s long prefill;
- 0731 DS4 #922 exact 2x M1 Max 64 GB / TB4: ~152 tok/s at 34K prefill + successful generation, but **no generated-token count / sustained TG**.

The new-to-repo single-node 0731 receipt improves the fallback/single-Mac calibration, but it does not justify synthesizing an exact dual-M1 0731 TG number.

No direct DS4-0731 desktop RTX 5070 Ti 16 GB or RX 6800 16 GB receipt strong enough for the machine table was found in this pass.

## Fresh post-10:30 upstream activity

### llama.cpp #28330 — stop allocating unused Qwen4Exp indexer V cache

Source:

https://github.com/ggml-org/llama.cpp/pull/28330

Created after the previous pass. `llama_memory_hybrid_idx` uses a KV-cache object for QSA/indexer keys, but its V plane is not used. The proposal suppresses that V allocation.

Implication:

- directionally helpful for constrained-memory Flash-Next deployments;
- particularly interesting for the 32-GB M1 and 16-GB discrete-GPU lanes;
- **no posted bytes-saved or end-to-end throughput number yet**, so do not turn it into a fit claim.

### DS4 #861 — refreshed NHI/layer-pipeline numbers

Source:

https://github.com/antirez/ds4/pull/861

Current two-Radeon-8060S / TB5 / MXFP4 layer-pipeline head now reports:

- 6K prefill: **250 tok/s**;
- 23K prefill: **274 tok/s**;
- short decode: **15.5 tok/s**;
- 6,144-token thinking run: **14.3-14.4 tok/s**;
- 2-client batched-session aggregate: **+3% short to +14% long** versus serial.

TP-over-NHI remains slower for prefill in the posted chunk ladder (best 137.5 tok/s at chunk 512), and the PR describes TP decode as gate-RTT-bound. The new multi-session result reinforces the existing dual-M1 planning rule: **coarse pipeline ownership plus independent requests can recover otherwise-idle stage time; fine-grained TP over a latency-heavy link is not automatically better.**

These are Strix/TB5 numbers, not M1/TB4 numbers.

### DS4 #963 — text-tool observation regression fix

Source:

https://github.com/antirez/ds4/pull/963

Created after the previous pass. On M5 Max 128 GB / DS4-0731 IQ2_XXS, DeepSeek text-only tool observations could be routed through a multimodal-only guard, fail to build, and then be misreported as context overflow. The patch restores the text path and adds a regression test; an 11-tool interactive session passed.

This is directly relevant to persistent coding-agent qualification, but it is correctness rather than raw performance.

### oMLX #3405 — MLX 0.32.2 VLM compatibility

Source:

https://github.com/jundot/omlx/pull/3405

Created after the prior pass. A Qwen3.5-family temporal repeat count is scalarized before `mx.repeat`, repairing fresh-install MLX 0.32.2 vision requests while leaving model math unchanged.

Validation includes:

- Qwen3.8-27B real screenshot, 3,116 image tokens, HTTP 200;
- Flash-Next image, required-tool, and three-turn TTFT checks.

No speed result, but preserve this because a future local 27B/Flash VLM bring-up on a fresh MLX install could otherwise misdiagnose a compatibility failure as model/runtime instability.

### Layr exact challenge

No PR in `Layr-Labs/qwen-3.8-mtp-challenge` was updated after the prior 10:30 ET cutoff. The last canonical exact frontier therefore remains unchanged.

## Machine matrix after this pass

| User machine class | Flash-Next direct evidence | 27B direct evidence | DS4-0731 direct evidence |
|---|---|---|---|
| M1 Max 64 GB | already canonical: target-only/MTP single-M1 Flash sweep | **NEW-TO-REPO:** oMLX 4-bit/8-bit context + batching profiles | **NEW-TO-REPO:** single-M1 ~7-10 decode community receipts; exact dual-M1 still TG-missing |
| M1 Max 32 GB | no exact new receipt | no exact 32-GB receipt; 64-GB process/system memory figures forbid a fit assumption | no exact new receipt |
| RTX 5070 Ti 16 GB + 64 GB host | **NEW-TO-REPO:** ~17-18 tok/s IQ4_XS @128K on exact RAM/GPU class; Q8 side receipt 11.3 | **NEW-TO-REPO:** exact GPU 3-bit+MTP receipt; host RAM unspecified | no strong exact desktop receipt found |
| RX 6800 16 GB + 32 GB host | no direct receipt found | **NEW-TO-REPO:** exact GPU Q3/Q2 Vulkan receipt; host RAM unspecified | no direct receipt found |
| 2x M1 Max 64 GB / TB4 | correctness only; sustained Flash TG still missing | not the P69 deployment target | 0731 ~152 tok/s prefill known; sustained TG still missing |

## Planning consequence

### Flash-Next

Do **not** change the canonical dual-M1 B1/B2-B4 probability bands from this pass. The strongest new machine-specific datapoint is the RTX 5070 Ti 16 GB / 64 GB-host ~17-18 tok/s 128K receipt, but the missing quantity remains exactly the same: sustained Flash-Next TG on the real 2x M1 Max/TB4 topology.

The new llama.cpp indexer-cache patch is a capacity lead, not a forecast input.

### Qwen3.8-27B

Add machine-specific serving priors separate from P69:

- M1 Max 64 GB, favorable 4-bit oMLX baseline: high-teens B1 short-context and ~10 tok/s at 128K, with ~45 tok/s short-context B4 aggregate observed;
- RTX 5070 Ti 16 GB: the measured working high-throughput lane is low-bit target + native MTP; the tested 4-bit file can spill catastrophically;
- RX 6800 16 GB: low-bit 27B is practical, with a one-task Q2 point at ~29 tok/s, but quality must be requalified on the user's own coding workload.

These serving results do not modify the frozen exact-Q8 verifier campaign or promote any lossy quant into P69.

### DS4-0731

The single-M1 backfill makes the machine hierarchy more concrete: a 64-GB M1 can deliver high-single-digit/around-10 tok/s 0731 decode with aggressive quant/streaming, while the exact two-M1 0731 setup is already known to deliver ~152 tok/s long prefill. The **two-node 0731 decode TG is still unmeasured**, so retain the existing topology lesson and do not manufacture scaling from single-node data.

## Decision

1. Preserve the five direct machine-family backfills as **NEW-TO-REPO**, not newly published Sep-3 results.
2. Add the M1-Max-64 27B oMLX curves to the hardware calibration set; they materially improve the user's direct 27B priors.
3. Treat RTX-5070-Ti quant/residency selection as first-order for both 27B and Flash-Next.
4. Treat RX6800 Q2/Q3 27B as a useful bring-up lead requiring quality reproduction before choosing a daily-driver quant.
5. Preserve single-M1 DS4-0731 as a fallback calibration only; exact dual-M1 0731 TG remains a top missing receipt.
6. Track llama.cpp #28330 because removal of wasted indexer V-cache storage may matter disproportionately on the 32-GB M1 and 16-GB GPU lanes.
7. Track DS4 #861 multi-session PP because it strengthens the multi-agent pipeline-utilization thesis without changing the M1 forecast.
8. Exact verifier state is unchanged: **P69B13 remains next using existing profiling data only**.
