# External runtime watch — 2026-09-17 16:33 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-17 19:34:29 UTC` through `2026-09-17 20:33:27 UTC`.

Evidence time means substantive source / measurement time, not crawler, merge, rebase, label, or comment time. PRs, issues, and default-branch commits were screened across the standing runtime set, with relevant community/model surfaces checked under the same timestamp rule.

## Executive result

**No exact active-topology receipt appeared for any canonical target. No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max 64GB: **25 tok/s TG / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s TG / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max 64GB/TB4: **15 tok/s TG / 180 tok/s cold PP**.

## New evidence — vLLM #57440: allocator ownership can hide real device headroom

Issue #57440 was created at `2026-09-17 19:51:36 UTC`. It reports vLLM 0.28.0 on 2–4 nodes of 8x B200, Kimi-K3 MXFP4, fastsafetensors, FP8 KV, TP/DP/EP, with DeepEP v2/NCCL and a speculative Kimi-K3-DSpark configuration.

The exact measured receipt is startup-memory behavior, not throughput:
- before Kimi-K3 load: driver free **46.338 GiB**;
- immediately after load, PyTorch `reserved - allocated` **40.626 GiB**, driver free **5.537 GiB**;
- after MXFP4 repack, stranded cache **45.611 GiB**, driver free only **0.494 GiB**;
- explicit GC + empty-cache at the lifecycle boundaries returned **45.483 GiB** total and restored driver free to **45.865 GiB**.

Operationally, the reporter says the unpatched 2-node DeepEP-v2 setup had to clamp `max_num_seqs / max_num_batched_tokens` from 256/8192 to 32/512 to start, while the cleanup patch allowed 256/8192 again. The same startup pressure was reproduced with the speculative draft model.

Classification: **exact non-target startup-memory receipt; strong transfer evidence for fit/admission instrumentation.** The proposed causal explanation involving raw driver allocations is still partly hypothesis and is not promoted as independently proven mechanism.

### Project 51 rule

Record memory by allocator/owner and lifecycle boundary, not only aggregate free/used memory. A fit receipt should distinguish model-live bytes, framework-reserved-but-unallocated bytes, driver-visible free memory, communication/workspace reservations, and temporary load/repack staging. A model can be semantically unloaded from a temporary path while its bytes remain unavailable to another allocator.

## New evidence — llama.cpp #29045: cache families can disagree on sequence frontier

Issue #29045 was created at `2026-09-17 19:59:05 UTC` and reports a Mac/iSWA cache failure. After partial sequence removal below the sliding window, the sliding cache can report `seq_pos_max = -1` while the base cache still owns earlier positions. A position-implicit batch then derives position zero, writes over the logical prefix, and silently accumulates duplicate base-cache cells.

Measured on Gemma 4 E2B, excess stored cells grew **+277 -> +699 -> +1,099 -> +1,542 -> +1,954 -> +2,808 -> +3,559**, then both caches filled and decode failed with `failed to find a memory slot`. The reporter also notes that llama-server's explicit-position path does not rely on this derived-position behavior; the downstream wrapper was using a helper the public header says to avoid.

Classification: **exact Mac cache-correctness/failure receipt, different model/runtime path; strong state-identity transfer evidence.**

### Project 51 rule

For every cache/state family, sequence frontier is part of state identity. Never derive a global next position from a narrower sliding/auxiliary cache unless its frontier is guaranteed to represent the superset. After truncate/rollback/replay operations, assert frontier agreement or explicitly choose the authoritative family. Add repeated partial-truncate/reappend to long-session qualification because silent duplicate cells can masquerade as a memory leak until late failure.

## Commit-level delta

vLLM default branch commits inside the window included `ac2f0ea82c0d3005eb1de081cda715f0ee524c16`, `9a5bd373cfe59e236f2b32c30530f4dbbf24120d`, `2b02c6c29b72147de18905ba4e7dc8f284655b40`, `acc2ed2a5f1fbe79575a220fc743a80c2d068ce8`, and `9612f77077e09acbae9cc1d1b2ddf14a23e91597`.

The last is the merge of vLLM #56902, FlashMLA stale-workspace-view release. The PR's substantive measurement predates this incremental window, so merge time does not make it new evidence. For continuity, its measured deployed-version receipt was 5,904 MiB stale FlashMLA storage retained beside a new 6,144 MiB MoE workspace on 18/64 ranks; the fix recovered **103.78125 GiB** aggregate and raised minimum per-rank KV capacity **490,816 -> 603,904 tokens**. This reinforces the allocator/lifetime rule above but is not counted as newly timestamped evidence.

Other in-window vLLM merges were screened as commit coverage and do not move the active topology targets.

## PR / issue delta

vLLM #57441 added video support to the Transformers backend with L4 measurements, unrelated to the target model/topologies. No newly timestamped exact active-topology target receipt was found in the standing DS4/oMLX/mlx-serve/llama.cpp surfaces beyond the llama.cpp cache-correctness receipt above.

## Target decision

**Hold all canonical targets.**

This window changes qualification more than expected speed. Two independent receipts reinforce the same architectural point: apparent free capacity depends on ownership and authoritative state. For Project 51, both memory ownership across allocators and sequence-frontier ownership across cache families need explicit receipts before a long-context run is considered healthy.

## Hard freshness boundary

`2026-09-17 20:33:27 UTC`
