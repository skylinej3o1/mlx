# Project 51 external runtime watch — 2026-09-20 11:28 ET

**Hard freshness window:** strictly after **2026-09-20 14:50:36 UTC** through the user's message cutoff **2026-09-20 15:28:44 UTC**.

## Decision

**No numeric target/confidence change.** Keep **40 TG @ ~128K / 400 genuinely cold PP** on 2x M1 Max 64 GB / TB4.

This short window produced one durable architecture change for the agent lifecycle: preserve the slower reusable prefix tier while releasing accelerator memory during idle/sleep, rather than forcing every wake to become a cold prefill.

## NEW — vLLM #57810: preserve offloaded KV across pause/sleep

Source: https://github.com/vllm-project/vllm/pull/57810  
Created **2026-09-20 15:07:00 UTC**; implementation commit **15:05:52 UTC**.

vLLM's pause/sleep cascade releases GPU memory, but it also reset the external CPU/SSD KV connector. That destroys the exact cache tier that could make a later wake cheap.

The proposed change keeps the external/offloaded prefix tier across:

- `pause_generation(clear_cache=True)`;
- `sleep(level>=1)`;
- GPU KV-memory release.

GPU prefix cache, multimodal cache and encoder cache are still cleared and device KV memory is still returned. The slower connector tier survives until an explicit `reset_prefix_cache(reset_connector=True)`.

The motivating case is RL time-sharing: sleep the inference GPU, train, then wake and restore hundreds of thousands of prompt tokens from CPU rather than re-prefilling.

### Project 51 consequence

Introduce three explicit agent-idle states:

1. **hot idle** — model + live PP2/QSA/recurrent state remain resident;
2. **sleep idle** — release accelerator/wired working state but retain certified CPU/SSD prefix/checkpoint material;
3. **cold** — invalidate all reusable state and rebuild.

A trivial Slack/Telegram/iMessage `sup` can wake from state 2 by restoring the retained prefix tier and rebuilding only the stage-local live state.

The retained tier must be namespaced by at least:

- exact model/weight identity;
- quant identity;
- tokenizer/template identity;
- stable system/tools/skills prefix hash;
- runtime/cache schema version;
- PP2 stage partition / recurrent-QSA state format.

If weights, quantization, model topology or state schema change, the harness must explicitly invalidate the retained external tier. Sleep itself must **not** imply invalidation.

Measure separately:

- sleep -> GPU memory returned;
- `sup` -> prefix restored;
- restored tokens / physical recomputed rows;
- `sup` -> real-task-ready;
- real-task -> TTFT;
- stale-tier rejection/invalidation count.

This extends the existing wake/prewarm design without changing the honest 400 cold-PP ruler.

## STATUS UPDATE — vLLM #56685 Humming integration merged

Source: https://github.com/vllm-project/vllm/pull/56685  
Merged **2026-09-20 15:11:01 UTC**.

Humming adds fused activation/Hadamard/input-quant processing and expanded low-bit kernels on newer NVIDIA hardware. The substantive implementation predates this window and is not Apple/M1 evidence, so it is **not** promoted into Project 51 state or target assumptions.

Useful general reminder only: quant format efficiency depends on whether input transform/activation/quantization work is fused with the GEMM path, not merely nominal BPW.

## RECOVERED OLDER EVIDENCE — llama.cpp #29181 grouped-expert top-k fusion

Source: https://github.com/ggml-org/llama.cpp/pull/29181

The PR was created inside this window, but its substantive fusion commit was **2026-09-20 14:06:17 UTC** and its test commit **14:47:58 UTC**, both before this watch boundary. Per Project 51 evidence-timestamp rules it is therefore **RECOVERED OLDER EVIDENCE**, not NEW.

On CUDA BailingMoE2 16B-A1B Q8_0, grouped-expert top-k fusion recovered roughly **15-16% TG** versus the grouped-expert baseline.

No numeric transfer to Flash/M1 is valid. The general implication is already compatible with P51's expert-path work: grouping/fusing expert execution is only useful if route/top-k preparation does not become a new serial tax.

## Screened / no new substantive evidence

- **vLLM #53978 DFlash2 warmup:** PR metadata updated in-window, but both substantive commits are from August; do not relabel as new.
- **vLLM #52244:** no new substantive commit; prior recurrent-prefix evidence remains current.
- **vLLM #57811:** newly opened HY4 CUDA-graph event fix has no test/performance evidence yet and is not P51-specific enough to promote.
- **oMLX:** no post-boundary Flash performance commit; #3776 remains the latest relevant Apple Flash evidence.
- **mlx-serve:** no new strict-window commit; recently touched older PRs retain their original evidence timestamps.
- **llama.cpp #29169:** merged at 14:52 UTC, but the Metal HC implementation itself predates this window; merge status only.
- **Splash:** no new strict-window commit.
- **DS4:** no new strict-window substantive commit.
- **Kadir qwen38-mac-fast / Kadir llama.cpp:** no activity.
- **MTPLX:** no post-boundary commit.
- **APEX:** no post-boundary commit.
- **npanj/llama.cpp:** no post-boundary commit.
- **Current web/Hugging Face/Reddit scan:** no cutoff-qualified new exact M1/TB4 Flash receipt or new quant artifact measurement in this 38-minute window.
- No new exact **2x M1 Max 64 GB / TB4 / ~128K / P51 mixed quant + MTP** physical throughput receipt appeared.

## Target impact

**No change.**

The new result affects **agent availability/TTFT architecture**, not raw model TG or genuinely cold PP. It makes a low-resource sleeping state practical without throwing away the expensive reusable prefix tier.

**New hard boundary: 2026-09-20 15:28:44 UTC.**
