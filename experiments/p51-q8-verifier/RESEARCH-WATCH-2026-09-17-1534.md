# External runtime watch — 2026-09-17 15:34 ET

## Search window

Complete incremental pass over substantive source activity strictly after `2026-09-17 19:25:05 UTC` through `2026-09-17 19:34:29 UTC`.

Evidence time means substantive source / measurement time, not crawler, merge, rebase, label, or comment time. PR-level activity and default-branch commits were both scanned across DS4, vLLM, oMLX, mlx-serve, and llama.cpp; relevant HF/community surfaces were also checked.

## Executive result

**No exact active-topology receipt appeared for any canonical target. No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s TG at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max 64GB: **25 tok/s TG / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s TG / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max 64GB/TB4: **15 tok/s TG / 180 tok/s cold PP**.

Flash interpretation is unchanged: sustained **40 TG at ~128K active context** is the core success floor; 45–50 is stretch; 50–60 is upside only. Short-context 40 does not satisfy the target. PP means cold prefill.

## Newly promotable evidence — vLLM #57431

The previous watch quarantined the quantitative body of vLLM #57431 because the PR was created at `2026-09-17 19:03:30 UTC` but the current body snapshot was updated at `19:25:50 UTC`, 45 seconds after that watch's cutoff. That body is now inside this window and can be promoted.

PR: **[Model][DCP] Decode context parallelism for Qwen4Exp QSA, without the capacity regression**.

Hardware/topology: 4x B200, TP4, Qwen3.8-Flash-Next-FP8, DCP=2 versus DCP=1. This is exact Qwen4Exp/QSA evidence, but not Apple and not our dual-M1 topology.

### Capacity result

The key bug was not simply missing DCP execution. The replicated QSA selector cache and sharded main KV cache had different block-table widths (335 versus 168), forcing separate cache groups. Because a group pool inherits its widest block size, selector blocks were **93.8% empty** and consumed 335 of the 512 blocks required per request.

Measured capacity:
- DCP=1: **9,758,767 KV tokens**, max concurrency **37.23x**.
- DCP=2 with split groups: **6,845,952 KV tokens**, **26.12x**.
- DCP=2 with aligned/merged groups: **17,603,636 KV tokens**, **67.15x**.

So DCP=2 moved from **0.70x** single-rank capacity to **1.80x** after physical storage spans were aligned with semantic ownership.

### Long-context correctness result

A second defect gated writes to the replicated selector cache using the main-KV DCP-sharded slot mapping. At world size 2, rank 0 could therefore store none of the compressed selector states at the relevant positions.

This failure was invisible to short-context GSM8K and throughput, but catastrophic at long context:
- broken DCP=2 selector write: MRCR **0.0000 in every bucket**;
- corrected DCP=2 MRCR aggregate: **0.8982**, identical to DCP=1 **0.8982**;
- needles 2 / 4 / 8: **0.9960 / 0.9906 / 0.7081** for both DCP=1 and corrected DCP=2;
- GSM8K 400 samples: DCP=1 **0.9800**, DCP=2 **0.9775**, both 0% invalid; PR treats this difference as sampling noise within its published tolerance.

The long-context MRCR samples were 144K–201K tokens. This is unusually relevant transfer evidence for our ~128K qualification discipline even though the hardware is unrelated.

### Serving result

AgentX 256K, 128 users, 900 seconds, cold cache:
- req/s: **1.99 -> 2.24**;
- input tok/s: **151,909 -> 174,354**;
- TTFT: **1,140 ms -> 743 ms**;
- inter-token latency: **33.54 ms -> 27.62 ms**;
- steady-state prefix-cache hit: **80.46% -> 89.40%**.

DCP with MTP is explicitly **not claimed**; buffer-level reuse tests pass, but the PR says no real two-rank metadata-path run has happened.

### Promoted rules for Project 51

1. **Distributed cache geometry is part of capacity identity.** Semantic replication/sharding alone is insufficient; physical block span and group width can turn parallelism into a capacity regression.
2. **Replicated state must use replicated write ownership.** Never gate a replicated auxiliary cache through the shard map of a different state family.
3. **Short-context accuracy plus throughput cannot certify long-context distributed correctness.** The #57431 broken route retained normal GSM8K and throughput while MRCR at 144K–201K went to zero.
4. Add a distributed-state receipt that records, per state family: semantic ownership, physical block span, group identity, write mask, and rank participation.
5. For the dual-M1 ~128K ruler, require a long-context semantic fixture in addition to speed, memory, and token-agreement checks. A healthy short-context run is not sufficient evidence.

Classification: **exact Qwen3.8-Flash-Next/QSA long-context DCP receipt and strong transfer evidence; not an active-topology target receipt.**

## Commit-level delta

vLLM default branch gained commit `67e5b0acc9988afc50d019db64ad9da0dadaa15e` at `19:26:10 UTC` for HiSparse/NIXL full-block import without tail prefill. Its underlying PR/source predates this incremental evidence window, so the merge timestamp does **not** make it new research evidence. Recorded for commit coverage only; no promoted target implication.

No new default-branch commits in-window were found for DS4, oMLX, mlx-serve, or llama.cpp.

## PR / issue / community delta

No new source-time-qualified DS4, oMLX, mlx-serve, or llama.cpp target receipt appeared in this nine-minute window. Recent HF/community surfaces include Qwen3.8 Flash/27B material, but no newly timestamped exact active-topology measurement was found that clears the repository's evidence rules. Crawler timestamps were not treated as evidence timestamps.

## Target decision

**Hold all canonical targets.**

The useful change is to the qualification protocol, not the expected rates: #57431 gives a concrete demonstration that a distributed long-context route can look healthy on short-context accuracy and throughput while being completely wrong at 144K–201K. For our dual-M1 Flash goal, the ~128K success floor therefore needs both sustained TG and an explicit long-context distributed-state correctness receipt.

## Hard freshness boundary

`2026-09-17 19:34:29 UTC`
