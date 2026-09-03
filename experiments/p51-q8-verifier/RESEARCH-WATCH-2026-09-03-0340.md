# Runtime Research Watch — 2026-09-03 03:40 ET

Scope: fresh external delta after `RESEARCH-WATCH-2026-09-02-2320.md`, following the canonical-state-first protocol. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DS4 distributed serving, and the planned 2x M1 Max 64 GB / TB4 Hermes system.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **NEW — llama.cpp #28302 gives an Apple/M1 receipt for hybrid-agent rewind checkpoint retention.** The draft PR fixes short-prompt checkpoint spacing from deleting the recent recurrent-state checkpoint needed when a conversation rewinds, branches, retries, compacts, or reopens at an earlier point. On an M1 Pro 32 GB, editing an earlier turn after advancing the conversation changed from **704 tokens / 3355 ms** of prompt work on master to **26 tokens / 264 ms** on the PR; a master-again ordering control reproduced **704 / 3323 ms**. On an M5 coding-agent replay using a hybrid GDN MoE model, warm reprocessed tokens fell **2436 -> 1776** and wall time **18.25 -> 17.12 s (-6.2%)**. The cost is retained checkpoint memory: the agent replay observed 8 live checkpoints / ~596 MiB and the default count bound is 32. This is directly relevant to Hermes because retries, edits, branch exploration and compaction are normal agent operations. Keep rewind-capable recurrent checkpoints, but add a byte budget rather than relying only on checkpoint count.

2. **UPDATE — llama.cpp #28243 adds a negative Apple MTP/identity result on the current Flash-Next head.** M5 Pro 64 GB / Metal / `Qwen3.8-Flash-Next-UD-IQ3_XXS` with the official shared Q8 MTP draft measured, across interleaved medians: no-spec **26.8 tok/s**; draft depth 2 **26.3 tok/s (-2%)** with the same greedy token stream; draft depth 5 **22.1 tok/s (-18%)** and a different greedy token stream in 3/3 runs. The reporter also reproduced depth>=3 divergence on older heads. This is llama.cpp-specific and must **not** be transferred to oMLX's separately qualified exact Lightning-MTP stack, but it strengthens the system rule: before enabling speculative depth on Apple, gate both wall-clock gain and token/output identity. Do not assume a model-page recommended depth is safe on lower-bandwidth Apple hardware.

3. **RECOVERED OLDER EVIDENCE — DS4 #765 is unusually direct Hermes/subagent cache-routing evidence.** This PR dates to August and is not fresh, so it must not be called a new result. It fixes `--batched-session N` slot selection so an arriving subagent does not evict a long main session merely because they share a long system-prefix. Physical M3 Ultra / Metal validation with two slots changed the main agent's next continuation from a full 2,881-token reprefill / **5.06 s TTFB** to a 12-token suffix / **0.27 s TTFB**, with no engine-path throughput regression in a 2K-16K sweep. The PR's real-world note reports ~120K cold prefill at ~306 s on that machine, illustrating how catastrophic a wrong eviction can become. The evolved victim policy prefers empty slots, then stale (>~1h) checkpoints, then short recently-active checkpoints. Durable Hermes implication: cache slots need session-aware exact reuse plus staleness-aware eviction; long-lived main-agent state should not be sacrificed to short subagent waves when free/cheap slots exist.

4. **RECOVERED + UPDATE — oMLX #2628/#2630 harden SSD-cache memory pressure and teardown.** These are older PR lines, now rebased/currently updated, not new architecture discoveries. #2628 addresses a long-prefill case where paged-cache boundary snapshots themselves pushed a DeepSeek-V4-Flash 350K run from **113.3 GB without cache (completed)** to **116.5 GB with cache (hard abort)**. Admission now prices the largest future non-sliceable boundary snapshot before the chunk runs; the Qwen4 profile charges measured fixed GDN state while excluding block-sliceable QSA state. #2630 bounds SSD persistence teardown after a memory-pressure eviction so a saturated writer queue cannot run beyond the engine teardown budget and take every loaded model down with one evicted model. For Hermes this reinforces a separate cache-memory budget and bounded/cancellable persistence during unload/pressure events.

5. **UPDATE — reasoning-effort discovery is becoming machine-readable, but `none/off` semantics are still being resolved.** oMLX #2746/#3395 expose the actual reasoning vocabulary from model/chat-template metadata; Qwen3.8 is detected as `xhigh / medium / low` with `xhigh` default, while DeepSeek-V4's patched template can advertise `low / high / max`. A fresh discussion notes that mapping `none` to low thinking is undesirable for agent harnesses that expect `none` to mean thinking disabled. This is useful for future Hermes task routing, but do not rely on `none` as a stable cross-provider off switch until the oMLX contract settles.

6. **NO CHANGE — exact dual-M1 calibration.** llama.cpp #27993 has no new comments/results after the prior pass; DS4 #922 likewise has no new sustained 2x M1 Max 0731/Flash-Next TG result. DS4 #957 still has no post-fix throughput receipt for the coalesced Metal `--layers` mapping. Layr has no newer visible submission, and `ARahim3/mlx-dspark` still reports `pushed_at = 2026-09-01T10:54:45Z` despite repository metadata activity.

## Hermes consequence

This pass materially sharpens **state ownership**, not raw decode speed.

The preferred server policy should now explicitly include:

- 3-4 logical persistent agents, normally 2-3 active compute slots;
- exact session-aware slot ownership/reuse rather than longest-common-prefix-only routing;
- empty-slot first placement for short subagents when available;
- staleness-aware victim selection so old finished conversations do not become immortal cache squatters;
- protect expensive long main-agent state from short subagent waves when alternatives exist;
- preserve rewind/branch checkpoints for hybrid recurrent state, with a **byte budget** in addition to a checkpoint-count bound;
- durable SSD exact-terminal/paged fallback for cold/unloaded agents;
- bounded/cancellable SSD persistence during memory pressure and unload;
- speculative depth enabled only after both **identity** and **wall-clock** qualification on the exact runtime/hardware/quant/workload.

This fits the planned heterogeneous Hermes topology especially well: Flash-Next Lead/Builder/Reviewer retain expensive persistent histories, while bounded Qwen27B/Codex/Claude/Antigravity workers should receive isolated task packages and should not be allowed to evict the Lead's hot state merely because they share the same system/tool prefix.

## Forecast consequence

Short/medium B1, ~128K B1, and mature B2-B4 aggregate probability bands remain **unchanged**. There is still no physical sustained 2x M1 Max Flash-Next decode receipt.

The new M1 Pro checkpoint result improves confidence in practical long-lived agent workflows, not the compute ceiling. The new llama.cpp MTP result is cautionary rather than a reason to lower the oMLX-based forecast, because it exercises a different speculative implementation and explicitly shows a correctness divergence not present in the separately qualified oMLX exact stack.

The mature target remains roughly **400+ tok/s cold prefill plus excellent exact prefix/session reuse**, 3-4 logical agents, 2-3 active slots, asymmetric resident PP2, and a fourth Flash-Next identity available elastically rather than permanently compute-hot.

External evidence does **not** modify the certified P69 checkpoint; **P69B13 remains next using existing profiling data only**.

## Sources

- llama.cpp #28302 hybrid/recurrent checkpoint rewind retention: https://github.com/ggml-org/llama.cpp/pull/28302
- llama.cpp #28243 Flash-Next MTP Apple result: https://github.com/ggml-org/llama.cpp/pull/28243
- DS4 #765 session-aware batched-slot routing: https://github.com/antirez/ds4/pull/765
- oMLX #2628 boundary-snapshot memory admission: https://github.com/jundot/omlx/pull/2628
- oMLX #2630 bounded SSD persistence teardown: https://github.com/jundot/omlx/pull/2630
- oMLX #2746 / #3395 reasoning-effort discovery: https://github.com/jundot/omlx/pull/2746 and https://github.com/jundot/omlx/pull/3395
- llama.cpp #27993 exact dual-M1 Flash-Next correctness thread: https://github.com/ggml-org/llama.cpp/issues/27993
- DS4 #922 exact dual-M1 0731 long-context thread: https://github.com/antirez/ds4/issues/922
- DS4 #957 Metal `--layers` mapping coalescing: https://github.com/antirez/ds4/pull/957
