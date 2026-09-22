# Project 51 primary-lane research watch — 2026-09-22 02:05 ET

**Freshness boundary checked:** previous hard boundary **2026-09-22 00:18:59 UTC**. Search ran through the user's cutoff **2026-09-22 06:05:53 UTC**.

## Scope

Priority stayed narrow:
1. Flash-Next on **2x M1 Max 64 GB / TB4**;
2. Flash-Next on **one M1 Max 64 GB** as an experimental/calibration lane;
3. Qwen3.8-27B on **one M1 Max 64 GB**;
4. Qwen3.8-27B on **RTX 5070 Ti 16 GB**.

## Decision

**No numeric target or confidence change.**

The best exact-window development is that the Splash Q8-27B work is no longer only an external fork: it is now an upstream PR with reusable mixed-Q8 packaging. That lowers the engineering friction for our P70 study, but it does not add M1/Apple7 support. A recovered M1/M2-specific pruned Flash pack gives us an interesting single-M1 experimental control, and a same-day 5070-Ti long-run corroborates the IQ3_S baseline without moving the frontier.

## NEW — Splash #94 upstreams native Q8 Qwen3.8-27B

Source: https://github.com/incoai/splash/pull/94
Created: **2026-09-22 02:53:17 UTC**.

PR #94 proposes the Q8 branch directly against upstream Splash:
- schema 5 / `splash-packed-q8` package format;
- native Q8 linear kernels for decode and prefill across the existing tile families;
- Q8 vocabulary projection and embedding;
- `Qwen3_8Q8Layout` / `Qwen3_8Q8Weights` runtime integration;
- `pack_q8.py` for full Q8;
- **`pack_mixed_q8.py` for Q8 only on selected layers**.

The package/draft/tokenizer layout remains compatible with the Q4 family. When the planner selects a Q4-only tile, Q8 falls back to the Splash 1.0 decode policy.

Fresh PR-level validation:
- M5 Pro / Apple10 only;
- build + CPU/Metal tests pass;
- Q8 package serves end-to-end;
- **58 TG** on a short arithmetic prompt;
- **46 TG** on a code prompt;
- PR summary retains the broader result of about **37 TG average Q8 vs ~61 TG Q4**.

### P51 meaning

This is useful for the **27B M1 tuning program** even though it cannot run there yet:
- upstream source is now cleaner than maintaining our mental model from the fork;
- the mixed-Q8 packer is almost exactly the mechanism we want for sensitivity-driven Q4/Q8 allocation;
- target/draft/package integration is explicit and auditable.

But the hardware limitation is unchanged. The PR explicitly says Apple9 was not tested, and Splash's runtime still targets newer GPU families. There is still no Apple7/M1 backend. **P70 remains a port/adaptation problem, not a checkout-and-run problem.**

No single-M1 27B target movement.

## NEW — Splash #91 BF16 vs INT8 target KV

Source: https://github.com/incoai/splash/pull/91
Created: **2026-09-22 01:33:29 UTC**.

Splash adds an opt-in BF16 target-KV cache while leaving INT8 as default.

Validation includes M3 Max and M5 Pro, both 27B/35B models, 128K/256K attention tests and B1-B4 decode coverage. The PR reports:
- default INT8 outputs bit-identical to main;
- long-context attention elapsed-time changes around **-0.41% to +0.57%**;
- short real-model B1-B4 decode-cycle changes around **-0.71% to +0.81%**;
- BF16 uses roughly 2x target-KV memory and can be slower at long context;
- native 35B reached 256K in both formats; the complete native 27B 256K matrix remains unfinished.

One focused 27B BF16 numerical case has a lower whole-network state cosine than an older oracle threshold, but independent checks show matching top-1 and very small KL on that sample. The author explicitly does not claim general task-quality equivalence from that focused check.

### P51 meaning

Nothing here argues for spending BF16-KV memory by default. Keep our Q8-class KV lane and A/B source/Q8/Q6/Q4 where acceptance and long-context quality matter. Treat KV dtype as part of cache identity and certification.

## RECOVERED — a useful single-M1 Flash sandbox exists

Source: https://huggingface.co/Litwein/Qwen3.8-Flash-Next-REAP320-oQ3e-fp16-DWQ-MTP-Vision-MTPLX

This was not boundary-new, but it had not been in P51 state and directly fits the user's renewed interest in **Flash on one M1 Max 64 GB**.

The M1/M2 FP16 pack:
- REAP prunes routed experts **512 -> 320**;
- routed experts remain 3-bit; sensitive GDN/attention tensors are 5/6-bit; shared experts/lm_head/MTP are 8-bit;
- PLE is 4-bit g32 and streamed from SSD;
- in-RAM precision is reported as **3.84 bpw**, about **37 GiB**;
- MTPLX measures a **39.7 GiB resident floor**;
- recommended 64-GB-Mac setup exposes a **163,840-token** window;
- native FP16 is used for M1/M2 instead of BF16 upcast.

The MTP sidecar is unusually relevant to P51: it was self-distilled from the target's own long-context agent/reasoning traces and optimized for **depth-2 acceptance under production sampling**. On the BF16/M4-Pro arm, replacing the old sidecar improves production tokens/verify-cycle **2.445 -> 2.488** with unchanged cycle cost.

Measured family performance is **not M1 evidence**. On an M4 Pro 48 GB the identical BF16 weights report:
- ~32-35 TG short;
- 31.5-34.4 TG at 46K;
- **33.8 TG at ~85K**;
- ~180-196 PP at 46K.

The uploader explicitly has no M1/M2 timing.

### How to use it

This is **not** a candidate for the production >=38-quality lane until proven otherwise. It prunes 192 experts and uses 3-bit routed experts; the card itself says pruning/quantization are lossy and publishes no task/AA benchmark.

It *is* a very interesting experimental control for the second M1:
> What can M1/Apple7 + native FP16 + a ~40-GiB hot working set + trained depth-2 MTP actually do when full-model capacity pressure is removed?

That can help separate **M1 kernel/runtime ceiling** from **full 512-expert model capacity/streaming cost**.

## RECOVERED / timestamp-unqualified — RTX 5070 Ti 65K real workload

Source: https://mikkoge.com/2026/09/22/bonsai2-qwen38-27b-rtx5070ti/

The page is dated Sep 22 but does not expose a trustworthy publication time, so it is not counted as exact-window freshness evidence.

Hardware/runtime:
- RTX 5070 Ti 16 GB;
- Windows 11;
- PrismML llama.cpp CUDA;
- `Qwen3.8-27B UD-IQ3_S`;
- context **65,536**;
- one slot;
- Q4_0 KV;
- all layers on GPU;
- vision off.

Measured:
- startup VRAM **14,370 MiB**;
- generation VRAM **14,388 MiB**;
- **45.29 TG**;
- one actual run produced **26,620 output tokens** before natural completion.

This does not beat our existing same-card frontier (~51.3 TG @128K with custom MTP/KVarN-style setup), but it is a strong stock-ish baseline and confirms that IQ3_S can remain fully resident with useful 65K context and a long generation.

## NEW — vLLM #58080 target/draft RoPE mismatch can silently kill MTP

Source: https://github.com/vllm-project/vllm/issues/58080
Created: **2026-09-22 05:26:43 UTC**.

Qwen3.8-27B, 2x H20, MTP K2, target extended from native 262,144 toward 1M with YaRN:
- target receives the YaRN override;
- MTP draft does not;
- below 262K acceptance is healthy;
- at 279K/312K acceptance collapses to essentially **0%**;
- target output remains correct;
- draft work continues, turning speculation into pure overhead.

After baking the same RoPE extension into the draft config, reported acceptance returns to ~2.3-2.7 mean accepted length and 2x312K aggregate throughput rises from ~60-90 TG to ~153 TG.

P51's current 128K/180K working contexts stay below the native 262K boundary, so this does not change our targets. Durable rule: **target and draft positional/RoPE configuration must be identical runtime identity; mismatch should fail closed.**

## Primary-lane sweep result

### 2x M1 Max / TB4 Flash-Next
- No new exact dual-M1/TB4 receipt.
- No new Apple PP2 implementation/measurement.
- Splash still does not support Flash-Next (#39 remains a request) and still has no Apple7 backend.
- DGPP/two-Spark remains the strongest distributed analogue already captured.

### Single M1 Max 64 GB Flash-Next
- No new full-512-expert M1 performance receipt.
- Recovered Litwein REAP320 FP16 pack is now a worthwhile **experimental control**, not a quality-certified replacement.
- Kadir, `mihailescu2m`, `npanj/llama.cpp`, MTPLX repo: no qualifying fresh commit in-window.

### Qwen3.8-27B on M1 Max
- No new exact M1 speed receipt.
- Splash #94 lowers the software distance to a mixed-Q8 experiment but still requires Apple7 porting.
- oMLX had no new Qwen3.8 performance commit in-window.

### Qwen3.8-27B on RTX 5070 Ti
- Harish same-card project: no commits/issues in-window.
- no new DASLab GSQ/RCO update in-window.
- Sep-22 65K / 45.29-TG real-workload result is useful corroboration but does not displace the ~51.3 TG @128K custom frontier.

## Target / confidence impact

Unchanged:
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**, >=38 AA-class production floor;
- >=40 TG @128K planning confidence: **~70%**;
- single-M1 27B working target: **25 TG**;
- 5070-Ti 27B working target: **120 TG mature optimized lane**.

## New hard boundary

**2026-09-22 06:05:53 UTC**
