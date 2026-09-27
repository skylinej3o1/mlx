# Project 51 primary-lane research watch — 2026-09-27 06:23 ET

**Freshness boundary checked:** prior hard boundary **2026-09-27 04:12:29 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-27 10:23:44 UTC**.

## Decision

**No canonical TG/PP, quant-quality, or planning-confidence change.**

Keep:
- dual-M1 Flash: **40 TG @ genuinely filled ~128K**
- dual-M1 Flash: **400 realistic cold PP**
- **~70%** planning confidence for >=40 TG
- central TG region **~39-41**, mature downside **~30-32**, target-only fallback **~24-27**
- single-M1 27B: **25 TG canonical target**
- RTX 5070 Ti 27B: **120 TG mature target / 250 cold PP baseline target**
- Flash quant search **3.0-3.6 BPW**, source-like hypothesis **~3.3-3.6**.

This is a systems/correctness pass rather than a new speed pass. It adds durable rules for ownership, physical residency accounting and transfer completion that matter directly to the newly promoted heterogeneous-prefill lane.

## Findings

### NEW — mlx-serve now accounts live request KV + recurrent state instead of hiding it inside 'working'

Source: https://github.com/ddalcu/mlx-serve/commit/4e00f2af7a64fd846d31cfaa90247586cf853ca2  
Committed **2026-09-27 06:08:53 UTC**.

`/props kv_cache_bytes` now includes:
- hot prefix-cache residency;
- request-owned live attention KV;
- recurrent/SSM state including QSA raw-key state;
- the active slot while it is still mid-prefill.

Restored/shared KV views are deliberately excluded from the live-request bill because the hot-cache donor owns their backing buffers. The memory breakdown takes measured KV first, then fits the weight estimate into what remains; 'working' is left for activations/transients.

**P51 consequence:** use explicit physical ownership. A canonical accounting table should separate:
1. model weights;
2. shared/persistent prefix state;
3. private live-request KV + recurrent/QSA state;
4. transient activations/workspaces/allocator reserve.

Imported or restored shared state must be billed once, not once per consumer.

### NEW — SGLang fixes a sparse-index transfer race by waiting at the read boundary

Source: https://github.com/sgl-project/sglang/commit/38d865489af5ce7b1885577aa834b0d34dd99438  
Committed **2026-09-27 05:04:03 UTC**.

DeepSeek V4.1 HiCache could read low-ratio index-K payload/dequantized rows before the corresponding layer transfer had completed. The fix inserts `wait_layer_transfer(layer_id)` directly in both low-ratio index-K read paths.

**P51 consequence:** this is directly transferable to CUDA-prefill -> MLX-decode state import. Metadata/handle availability is not proof that bytes are visible. Each imported layer/component needs a completion state/fence before QSA/index/recurrent consumers can read it. Put the wait at the consumer/read API as a fail-safe, even if the scheduler also tracks transfer completion.

### NEW — SGLang clarifies shared-prefix ownership: request release unlocks, it does not free

Source: https://github.com/sgl-project/sglang/commit/d27efca3536e3fe084fe654a68d494d95af030a9  
Committed **2026-09-27 05:00:02 UTC**.

A prefix matched from the radix tree is tree-owned. On request finish the request now frees only its private suffix and unpins the protected prefix rather than freeing the matched prefix itself.

**P51 consequence:** cache/prefix ownership must be independent from request lifetime. This is especially important for mirrored M1<->CUDA state: finishing one decoding request should release its reference/pin while leaving reusable shared conversation state intact. It prevents both double-free and accidental re-prefill.

### NEW — llama.cpp RDMA RPC stops burning a CPU core while idle; Apple/TB4 still lacks the equivalent

Source: https://github.com/ggml-org/llama.cpp/commit/d7fb90e8e2494b2908934d956a3202fd60152ee0  
Committed **2026-09-27 09:28:32 UTC**.

The regular RDMA path now spins briefly while active, then arms an RDMA completion channel and sleeps until a completion or peer close. The Apple RDMA/Thunderbolt implementation is explicitly annotated with a TODO for the same behavior.

**P51 consequence:** not a throughput receipt, but relevant to both dual-M1 TB4 and remote-prefill designs. Use completion/event-driven transport when idle; avoid a permanent polling core and define peer-close invalidation explicitly.

### KNOWN MERGE — SGLang #41166 small-copy fusion

SGLang commit `aa7a976807ea71320027713a8b90cf91cc1503c4` merged in this interval. This is the already-recorded Qwen3.8 CUDA graph small-buffer-copy work (~11 us -> ~1.4 us in the prior evidence set). It is classified **KNOWN MERGE**, not new evidence, and receives no additional target credit.

## Community / Ishizuki / M1-M2 scan

No new planning-grade independent **32-core M1 Max 64K/96K/128K** measurement appeared after the prior boundary. Current searches continue to return the already-recorded M1 Splash Part 1/Part 2, 24-core replication, MTPLX and oMLX threads. `struffl/ishizuki`, MTPLX, both Splash repos and oMLX had no new qualifying commit in this strict interval.

## Lower-priority strict-window activity

- llama.cpp added SYCL wide FWHT and unrelated CUDA/HIP/OpenCL work; no Apple P51 target impact.
- vLLM changes were CPU attention and DSv4.1 SM100 fusion, not applicable to the primary lane.
- SGLang added unrelated memory-cache/control-plane and diffusion work.
- mlx-serve's other current work is UI/telemetry; no new Flash throughput receipt.

## Canonical planning state after this pass

Unchanged. Priority remains **prefix/state reuse, recurrent-prefill work, and heterogeneous prefill correctness** rather than raising TG forecasts.

`RESEARCH-STATE.md` is updated with live-state ownership/accounting, transferred-state readiness and shared-prefix lifetime rules. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 10:23:44 UTC**
