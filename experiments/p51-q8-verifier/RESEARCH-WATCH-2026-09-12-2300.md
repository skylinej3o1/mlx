# External runtime research watch — 2026-09-12 23:00 ET

## Scope and freshness

This pass covers substantive sources strictly after `2026-09-12 21:35:07 UTC` through the user-request cutoff `2026-09-13 03:00:39 UTC`.

Active lanes remain:

- **Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4**
- **Qwen3.8-27B — one M1 Max 64 GB**
- **Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM**
- **DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4**
- **Blazer / custom ~5.x-BPW** where evidence transfers cleanly

Evidence timestamp means substantive source timestamp, not crawl/rediscovery time. PRs or measurements outside the window remain older evidence even if rediscovered now.

**Hard source-freshness boundary for the next complete pass: `2026-09-13 03:00:39 UTC`.**

---

# Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| **Flash-Next — 2x M1 Max64 / TB4** | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| **Qwen3.8-27B — M1 Max64** | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| **Qwen3.8-27B — RTX5070Ti16** | **120 tok/s** | **250 tok/s** | unchanged |
| **DS4-0731 — 2x M1 Max64 / TB4** | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moves in this pass. P69 remains isolated. P69B12 remains frozen/promoted and P69B13 remains next only from the existing measured GDN/projection/downstream-tail profiling. External research does not reopen P69B8/B9/B10-C or redefine P69B13.**

---

# New evidence

## oMLX #3626 — fused RMS/GDN verification recurrence with exact rollback

**FRESH NEW / DIRECTLY RELEVANT VERIFIER-MECHANISM CANDIDATE. Not an exact active-lane receipt.**

A new default-off Qwen4 verification path fuses:

- RMS/scaling prework;
- the full GDN recurrence;
- gated normalization;
- recurrent rollback snapshot production;

into one dispatch. Admission is intentionally narrow: B1, speculative width S3-4, BF16 projections, FP32 recurrent state, qualified cache ABI, supported geometry, and no mask/padding/sharding. The path preserves the deployed RMS/scaling order rather than substituting a mathematically similar normalization.

The PR reports a separately qualified composed source with **18/18 exact fixed-length cells** and median RMS-off -> on decode:

- 16K: **77.20 -> 78.09 tok/s** (~+1.15%);
- 32K: **79.13 -> 81.00** (~+2.36%);
- 64K: **75.70 -> 76.97** (~+1.68%).

Only the 16K bracket passed the stated thermal gate; 32K/64K are diagnostics. Semantic checks reported 8/8 exact multi-turn pairs and 100/100 exact domain pairs. The isolated PR head itself has CPU contract validation only, and the PR body does not establish an exact hardware/model identity for those composed-source throughput numbers.

**Promote the mechanism, not the percentage:** verifier work can fuse normalization + full recurrent update + rollback-state materialization in one ownership boundary, provided cache advance and every rollback snapshot stay exact.

For Flash-Next, this becomes a concrete transfer experiment after shape/ABI matching. For 27B, it is conceptually aligned with our GDN/verifier work but **does not alter P69 or P69B13**.

Required A/B dimensions if ported:

`generic verify prework/recurrence/rollback -> fused recurrence ownership -> exact cache advance -> every rollback snapshot -> acceptance trajectory -> TG -> thermal bracket`.

## oMLX #3628 — positional preads transform expert-offload I/O economics

**FRESH NEW / STRONGER-APPLE V4.1 CAPACITY + I/O MECHANISM TRANSFER. Not DS4-0731 target evidence.**

DeepSeek V4.1 expert offload was using an Engram-style scattered-row mmap path for a physically opposite workload: each expert is a ~14.8 MiB contiguous slab at the tested oQ3e geometry. Replacing that path with positional `preadv`, a dedicated reader pool, bounded in-flight payload, deterministic serial installation, and expert-boundary prefill chunking changed cold synthetic expert fetch on M5 Max from:

- one-token / MoE-layer read cost: **362 ms -> 9.1 ms**;
- cold fetch throughput: **0.23 -> 9.3 GB/s**;
- sorted 256-token prefill: **33 -> 568 token-layers/s**.

Real `Jundot/DeepSeek-V4.1-Flash-oQ3e-mtp` receipt on a 128 GB M5 Max, Engram on SSD, 433-token prefill + 64 greedy tokens:

| residency | Metal active | peak footprint | prefill | decode | decode hit rate |
|---:|---:|---:|---:|---:|---:|
| 12.5% | 38.0 GiB | 49.6 GiB | 28 tok/s | **5.6 tok/s** | 0.69 |
| 25% | 65.7 GiB | 77.4 GiB | 25 tok/s | **4.2 tok/s** | 0.78 |

Counterintuitively, 12.5% residency decoded faster despite a lower cache hit rate because the released RAM became filesystem page cache. Repeated misses were then served at ~6.5 GB/s effective versus ~3.4 GB/s from SSD.

The speculative result is especially important: a 5-token verification block touched about **4.6x** as many experts as one-token decode under these low-residency conditions. The PR estimates that a 1.6-2x token/step speculative gain would net only roughly **0.4x throughput** while expert-read latency dominates.

**Promote:** speculative decoding profitability is bottleneck-conditional. If each verify block multiplies nonresident expert working-set touches, higher accepted tokens/step can make wall-clock throughput worse. Always record `experts touched / verifier step`, miss count, fetched bytes, hit rate, page-cache state and resident fraction alongside acceptance.

Also promote storage-class separation: scattered small-row Engram access and contiguous expert-slab access require different I/O primitives and queue ownership.

## oMLX #3620/#3621/#3625 — direct Thunderbolt/RDMA cluster bring-up and serving reliability

**FRESH NEW / EXACTLY RELEVANT TOPOLOGY MECHANISM EVIDENCE. No TG/PP receipt.**

Three post-boundary PRs expose concrete failure modes for the dual-Mac lane:

### #3620 — system-Python sidecar environment contamination

Packaged oMLX rank workers can inherit app-bundle `PYTHONHOME/PYTHONPATH`. JACCL/system-socket helpers intentionally invoke Apple's `/usr/bin/python3`; inheriting the app's Python 3.11 environment into system Python 3.9 can crash before RDMA communicator bootstrap. The proposed fix strips those variables from sidecar environments.

**Promote:** communicator/control-sidecar process environment is part of distributed execution identity. A healthy main rank does not prove helper-process ABI/runtime compatibility.

### #3621 — native 169.254/16 Thunderbolt link-local addresses

Direct Mac-to-Mac Thunderbolt commonly self-assigns IPv4 link-local addresses. oMLX previously rejected all `169.254.*` addresses as unroutable, causing an active Thunderbolt/RDMA link to be ignored and Wi-Fi selected instead. The proposed route admits link-local only when attached to an active Thunderbolt/RDMA hardware interface.

**Promote:** transport certification must record selected interface/address and physical transport, not merely that two ranks connected. For our topology, link-local TB/RDMA is a valid production transport.

### #3625 — watchdog false positives during heavy TB/RDMA prompt ingestion

During high-throughput parallel prompt ingestion/context compaction, remote SSH health probes can exceed 5 seconds while ranks are busy in collectives. The existing 3 s serving interval + two-failure tolerance could declare healthy workers dead after ~6 seconds. The PR raises/configures probe timeout, failure tolerance and abort grace; default failure patience becomes ~30 seconds.

**Promote:** liveness-plane timing must be decoupled from dataplane stalls. Long-prefill/TB collective load is not proof of peer death. Cluster qualification should include heavy-prefill watchdog survival, not only idle health checks.

These are highly relevant to our PP2/TB4 bring-up but do not move throughput targets.

## vLLM #56629 — one physical HiSparse host pool for replicated TP state

**FRESH MERGE / MEMORY-OWNERSHIP MECHANISM TRANSFER. Not Metal evidence.**

Merged in-window. On single-node multiprocess TP, HiSparse MLA source KV is replicated across ranks. The change maps all TP workers onto one mmap-backed pinned-host pool, with rank 0 as writer and peers synchronized through IPC events, rather than allocating one physical host pool per TP rank.

Validation covers shared inode/visibility, creator-only population, cleanup after SIGKILL, exact round trips and host-registration cleanup, but **no production-sized end-to-end model or performance run was done**.

**Promote:** distinguish logical per-rank ownership from physical replicated storage. If state is semantically identical across ranks, a single physical backing with explicit producer/event ownership can reduce capacity pressure. For our Flash-Next experiments this is a transfer idea for any replicated host-side QSA/PLE/cache plane; PP2 remains primary and this does not imply TP2 is preferred.

## vLLM #56323 -> #56649/#56654 — explicit DFlash/MTP JIT warmup caused compile-cardinality blowup

**FRESH INTEGRATION CHURN / COMPILE-LIFECYCLE WARNING. Not a throughput result.**

`#56323` merged in-window and migrated sampling/DFlash/MTP Triton kernels into explicit MRV2 warmup. A fresh follow-up reports roughly **120 sampler warmup keys per engine**, with multi-engine CI lanes accumulating **~700-1,400 seconds** of warmup compilation and timing out while tests themselves continued normally. A second fresh PR, #56654, proposes reverting the MRV2-specific sampler/DFlash/MTP warmup migration while keeping shared model/attention warmup infrastructure.

The rollback's targeted tests pass, but it explicitly has **no end-to-end serving, startup-latency or first-request compilation benchmark** yet.

**Promote:** compile coverage cardinality is a first-class cost. A kernel-prewarm design that improves first-use predictability can be net-negative if it eagerly materializes a large cross-product of shapes/configs. Our benchmark lifecycle should continue separating:

1. fresh process / zero cache;
2. explicit compile/prewarm total wall time and key count;
3. first real request;
4. first new shape;
5. warm steady state;
6. realistic shape churn.

Do not interpret “all kernels prewarmed” as a free optimization.

## vLLM #56641 — preserve declared DSpark architecture across Qwen MTP config rewrites

**FRESH NEW / SPECULATIVE CONFIG-PROVENANCE CORRECTNESS.**

A Qwen-family DSpark checkpoint can carry an MTP-like `model_type` while explicitly declaring a DSpark architecture. The current config override rewrote that architecture to Qwen MTP based on `model_type` alone; dispatch then failed to recognize DSpark and could fall through to a DeepSeek DSpark implementation with incompatible config fields.

The proposed fix preserves an explicitly declared DSpark architecture. The PR validates dispatch/config behavior but does **not** yet claim end-to-end Qwen DSpark execution.

**Promote:** draft architecture declaration is authoritative unless a conversion explicitly proves otherwise. `model_type`, MTP-like fields and target-family resemblance are insufficient to rewrite the draft execution class. This reinforces the existing target-vs-draft config separation rule for DFlash2/DSpark/Lightning experiments.

---

# Screened / not promoted

- `jundot/omlx` main itself had no post-boundary commits; the important Apple evidence above is in fresh open PRs.
- `antirez/ds4` had no commits in-window and no new exact dual-M1 0731 receipt.
- `llama.cpp` in-window commits were structured logging and Qwen3-Coder chat-schema parsing; no active-lane Metal throughput/correctness receipt.
- vLLM's MHC/DSv4 warmup migrations were screened; no active-lane numeric target evidence was promoted.
- Web/HF/Reddit searches surfaced stronger-Apple/M5 and community Flash/27B results, but no source-time-qualified post-boundary exact M1 Max64 / dual-M1 / RTX5070Ti receipt strong enough to promote. Crawl time is not evidence time.
- No new exact dual-M1 Flash-Next TG/PP receipt.
- No new exact M1 Max64 Qwen3.8-27B receipt.
- No new canonical RTX5070Ti16 receipt.
- No exact new dual-M1 DS4-0731 receipt.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 as control.

Add/retain these certification gates:

- JACCL/control-sidecar environment identity and helper ABI;
- selected network interface/address/transport, including valid 169.254 Thunderbolt link-local;
- heavy-prefill watchdog survival and liveness/dataplane decoupling;
- verifier fusion as an exact ownership boundary: normalization + recurrent update + rollback snapshots;
- compile/prewarm key count and total startup compilation wall time;
- logical per-rank vs physical replicated host-state ownership;
- existing live-context work bounds, QSA workspace lifetime, proposal precision, draft config, spec-verifier peak shape, rank-local PLE loader path and PP/MTP state gates.

No target move.

## Qwen3.8-27B M1 / P69

No target move and no external modification to certified work.

#3626 is conceptually aligned with our GDN verifier campaign, but it **does not become P69B13 evidence** and does not reopen closed branches. It is a separate external mechanism candidate to revisit only after the existing P69 plan is complete or if independently reproduced under our frozen ruler.

DFlash2/DSpark config identity rules strengthen further from #56641; target and draft architecture/config remain separate.

## RTX5070Ti16

No target movement. JIT warmup compile-cardinality evidence is relevant to CUDA startup/benchmark methodology. #56629/#56641 are transfer/correctness evidence only, not 5070 Ti performance receipts.

## DS4-0731 dual M1

No target movement. #3628 is later-V4.1/M5 capacity evidence only, but it materially strengthens the rule that SSD/expert-offload speculation should be disabled when verifier blocks multiply expert misses. #3620/#3621/#3625 are directly useful dual-Mac transport/reliability lessons.

---

# Standing rules added/reinforced

- Fused recurrent verification must certify cache advance **and every rollback snapshot**, not only final output.
- Speculation economics must include nonresident expert touches/misses/fetched bytes per verify step; accepted tokens/step alone can be misleading.
- Storage primitives must match physical access shape: scattered row gather and contiguous slab reads are distinct lanes.
- Distributed execution identity includes helper-process environment/ABI, selected physical interface/address and liveness policy.
- Logical replicated state and physical backing are separate; deduplicate physical copies only with explicit producer/consumer synchronization.
- JIT warmup cardinality and total compile wall time belong in benchmark identity.
- Explicit draft architecture beats family/model-type heuristics unless a conversion explicitly proves equivalence.
- Component/kernel gains still do not move TG/PP targets without exact target-topology evidence or exceptionally strong transfer evidence.
- **P69 remains isolated.**
