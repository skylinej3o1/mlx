# External runtime watch — 2026-09-04 09:15 ET

Freshness boundary: `9f24f1eabadfcad661174bc4b4bd8c126386858d` / 2026-09-04 10:43:57 UTC.

Scope remains narrow: exact planned 2x M1 Max 64 GB / TB4 Flash-Next and DS4-0731,
single-M1-Max-64 Qwen3.8-27B, and the RTX 5070 Ti 16 GB Qwen3.8-27B lane. Direct physical
evidence is required to move the canonical TG/PP probabilities in `RESEARCH-TARGETS.md`.
Older material discovered in this pass is explicitly labeled backfill rather than fresh.

## Executive result

**No canonical TG/PP target or confidence moves.** No new sustained exact 2x-M1 Flash-Next TG,
exact 2x-M1 DS4-0731 TG, exact single-M1 27B ruler, or direct single-5070-Ti speed result appeared
after the cutoff.

The pass is still material for productization and serving safety:

1. llama.cpp's 0.4.0 version bump merged after the cutoff and packages a much more coherent
   upstream Flash-Next baseline;
2. a missed qwen4exp `draft-mtp + --parallel > 1` cross-slot contamination report makes parallel
   MTP a correctness gate, not merely an economics choice;
3. SSD expert-streaming work provides a useful one-Mac/fallback lane and exposes an Apple
   host-mediated exact-demand latency floor that reinforces resident stage ownership for the
   primary dual-M1 design;
4. MTP-head imatrix results turn head quantization into a concrete exact-5070 A/B candidate.

## FRESH / MATERIAL OPERABILITY — llama.cpp 0.4.0 version bump merged

Source: https://github.com/ggml-org/llama.cpp/pull/28386

PR #28386 was created at 2026-09-04 12:21 UTC and merged at 12:22 UTC, after this pass's
10:43:57 UTC freshness boundary. The version-bump notes explicitly collect the following into the
0.4.0-era baseline:

- initial Qwen3.8-Flash-Next (`qwen4exp`) architecture support;
- lazy/on-demand tensor reading and `--lazy-mode`;
- sparse flash-attention infrastructure for DeepSeek-V4/GLM/qwen4exp;
- Qwen4Exp recurrent rollback;
- Qwen4Exp indexer-head reduction and graph-split reductions;
- Apple RDMA as an RPC transport;
- RPC event/async backend APIs;
- KV-cell token tracking and state/session version changes;
- n-gram history lookup;
- DFlash2 support;
- per-slot server context limits;
- ggml 0.23.0 sparse-attention / async scheduling / allocation-dependency work.

The release note is also explicit that Qwen3.8-Flash-Next optimization work is still pending.
Therefore this is **not** a throughput promotion event.

At check time the version-bump PR was merged, but the GitHub API did not yet expose a stable
`v0.4.0` release/tag; the visible binary release line was still the normal rolling build stream.
For the turnkey recipe, qualify one pinned 0.4.0-era commit/release on the physical dual-M1 pair
before calling it the blessed baseline. Do not mix ad-hoc cherry-picks into the community recipe
once that baseline is selected unless a measured gate requires one.

Productization consequence: much more of the stack we need is becoming ordinary upstream surface
instead of a pile of unrelated experimental branches. This strengthens the starter-kit story, but
it does not change the 40 TG / 400 PP planning center.

## NEW-TO-REPO BACKFILL / MATERIAL CORRECTNESS — parallel MTP can contaminate slots

Source: https://github.com/ggml-org/llama.cpp/issues/28286

Issue #28286 predates this pass's freshness boundary, so this is backfill, not a fresh event.
It is nevertheless important enough to change the safe serving policy.

Reported environment:

- qwen4exp / Qwen3.8-Flash-Next UD-Q3_K_XL;
- Q8 MTP sidecar;
- AMD Strix Halo / ROCm downstream build rebased to upstream 2026-09-01;
- `--spec-type draft-mtp --spec-draft-n-max 4 --parallel 4`.

Observed failure:

- concurrent requests with semantically distinct prompts sometimes produced plausible text from
  another slot's prompt/completion;
- examples included a quicksort completion drifting into Roman-history prose and a CAP-theorem
  request acquiring quicksort code;
- output stayed valid and plausible rather than obviously corrupted, making casual smoke tests
  insufficient;
- disabling GPU graphs did not remove the behavior;
- `--parallel 1` did not reproduce it;
- trivial repetitive prompts could also pass, so a low-entropy smoke test can miss the bug.

This report is not an M1 measurement and was not run on the final 0.4.0 baseline. It therefore does
**not** prove current master is still affected. It does prove that parallel qwen4exp MTP must pass a
real isolation gate before it is allowed into a turnkey default.

### Safe policy until requalified

- permit **one active MTP lane at a time**;
- fill concurrency with plain target batching / PP pipeline work / queued independent requests;
- do not expose `parallel > 1` MTP as a default merely because aggregate throughput looks good.

### Mandatory parallel-MTP isolation gate

Before promoting parallel MTP on the real dual-M1 system:

1. run parallel 2 and 4;
2. use clearly distinct high-entropy prompts (multiple code domains plus unrelated prose/reasoning);
3. test temperature 0 and the intended agent sampling settings;
4. generate long enough outputs for contamination to surface;
5. repeat multiple rounds with randomized prompt assignment to slots;
6. fail on any cross-slot semantic attribution, state/hash mismatch, or recurrent/cache leakage;
7. repeat after joins/leaves, cancellation, cache restore and long-prefix reuse.

This converts the existing singleton-MTP-lane idea from an economics preference into the default
**correctness posture** until the gate passes.

## BACKFILL / MECHANISM CLARIFICATION — Qwen4Exp recurrent rollback is upstream, multi-slot safety is separate

Source: https://github.com/ggml-org/llama.cpp/pull/28123

PR #28123 merged on 2026-09-01 and is now named in the 0.4.0 version notes. It adds qwen4exp
recurrent rollback coverage for the delta-net QKV convolution and PLE convolution snapshot planes.
The motivating single-slot RTX PRO 6000 measurement was:

- no draft: 108 tok/s;
- before rollback fix: 123 tok/s code / 83 tok/s prose;
- after: 183 tok/s code / 144 tok/s prose.

Those absolute rates do not transfer to M1. The portable point is that host serialization of
recurrent state can erase speculative gains and that snapshotting the qwen4exp recurrent planes is
a real mechanism.

Do not infer from this single-slot result that parallel MTP is safe. Issue #28286 and the older
multi-sequence rollback investigation (#28019) are enough reason to requalify per-slot state on the
current 0.4.0-era code. Treat recurrent rollback as a baseline mechanism to test on M1, not as a
parallel-MTP correctness certificate or a forecast multiplier.

## NEW-TO-REPO BACKFILL / PORTABLE APPLE MECHANISM — exact SSD expert streaming

Sources:
- https://github.com/jundot/omlx/pull/3359
- independent review comments on the same PR

oMLX #3359 is an experimental exact-routing SSD expert-streaming runtime. It keeps a bounded expert
bank resident, streams exact routed rows from storage, supports route-frequency/LRU caching, uses a
prompt scratch bank, can directly publish exact-format rows into proven-idle Metal buffers, and
keeps Flash-Next's large PLE on mmap/SSD when streaming is enabled.

The branch author's development trajectory is intentionally non-portable: Qwen3.8-Flash-Next
Q2-MTP with a 320/512-row decode bank and fixed MTP depth 3 reached about 40.36 TG / 362 PP on a
short forced trajectory with 100% MTP acceptance. Do not import those numbers into the dual-M1
forecast.

The more useful independent physical receipt is an **M5 Pro 64 GB** reviewer run after correctness
fixes:

- Flash-Next oQ2 MTP resident footprint about 32.7 GB;
- warm TG about 25-28 tok/s at MTP depth 3;
- native-demand `mx.synchronize()` could deadlock because the completion path needed the GIL;
- an all-resident fast path could use a stale slot map and diverge nondeterministically;
- resolving every route through the callback restored exactness at the same throughput;
- parallel PLE prefaulting reduced a bimodal 1024-token prefill from roughly 3.6-10 s to about
  3.6-3.9 s across the reported runs;
- measured native-demand route turnaround was roughly 150 us/layer (about 47 us GPU->CPU and
  106 us CPU->GPU), implying about a **7 ms/step host-mediated floor across 48 layers** even with
  every expert already resident.

Portable conclusion for the 2x M1 Max plan:

- direct Metal I/O and PLE prefaulting are useful mechanisms to mine;
- exact host-mediated on-demand expert routing is a strong **one-Mac / fallback / capacity** lane;
- it should not displace resident stage-owned experts as the primary dual-M1 architecture when the
  aggregate 128 GB system can avoid that per-layer host round trip.

For a future community kit, this may become a useful "single 64 GB Mac / starter-lite" profile,
but only after its exactness, shutdown and admission accounting are independently certified.

## BACKFILL / 5070 CANDIDATE — MTP-head imatrix now has concrete quality numbers

Source: https://github.com/ggml-org/llama.cpp/pull/28351

PR #28351 was updated before this pass's cutoff, so it is not fresh. It does sharpen the existing
"MTP-aware imatrix" watch item into a concrete 5070-Ti capacity experiment.

Reported head-only agreement table includes:

- Q4_0, 240 MB: 0.7183 without imatrix / 0.7200 with imatrix;
- Q4_K, 240 MB: 0.7203 without / **0.7216 with imatrix**;
- Q6_K, 350 MB: 0.7233;
- BF16, 850 MB: 0.7239.

The PR's own recommendation is Q4_K + imatrix when memory is tight and Q6_K when it is not. There
is no direct 5070-Ti end-to-end acceptance/TG/quality result in this evidence.

Add an exact-card A/B after the existing Blackwell stability gate:

1. BF16 head control;
2. Q6_K head;
3. Q4_K + imatrix head;
4. same target quant and prompt set;
5. sampled acceptance by workload, TG, VRAM, maximum healthy context and agent-quality checks.

Only promote a smaller head if the released VRAM actually buys context/headroom without enough
acceptance or quality loss to erase the wall-time benefit.

## NO CHANGE — exact physical rulers

### Flash-Next / exact 2x M1 Max 64 GB / TB4

- llama.cpp #27993 remains the topology/correctness anchor;
- no sustained exact dual-M1 generation rate surfaced;
- no completed published 115K-class follow-up surfaced.

### DS4-0731 / exact 2x M1 Max 64 GB / TB4

- #922 remains the exact 0731 receipt: ~152 tok/s for a 34,384-token distributed prefill and a
  successful long CLI generation, but still no generated-token denominator / sustained TG;
- #957 remains open with no physical post-coalescing exact-M1 throughput result;
- prior #845 command-buffer/OS diagnostics remain the current caution.

### Qwen3.8-27B / RTX 5070 Ti

- `aipruner/qwen3.8-3bit-test-in-16GB-GPU` still has `pushed_at=2026-08-20T19:16:50Z`;
- the direct Q3_K_XL + native-MTP ruler remains primary;
- no new exact single-card result superseded the current speed/context lanes.

### Qwen3.8-27B / Apple external frontier

- `ARahim3/mlx-dspark` still has `pushed_at=2026-09-01T10:54:45Z`;
- `Layr-Labs/qwen-3.8-mtp-challenge` still has `pushed_at=2026-08-29T07:05:19Z`;
- no external result changes the exact verifier work.

## Updated qualification order

### Dual-M1 Flash-Next

1. pin and certify one 0.4.0-era baseline on both Macs;
2. plain exact PP2/layer-owned B1/B2/B4 + cold/long prefill baseline;
3. PLE residency/page-cache/direct-read/quantized placement A/B;
4. sparse-QSA experimental A/B;
5. recurrent rollback + singleton MTP A/B at temp 0 and real agent sampling;
6. **parallel-MTP slot-isolation gate before any `parallel > 1` MTP serving**;
7. compiled-decode B2/B4 E2E A/B;
8. short-turn cache granularity / exact replay A/B;
9. SSD-expert-streaming/direct-I/O as a secondary capacity/control lane, not the default topology;
10. combine only mechanisms that pass individually, then run the long-prefill-arrives-during-active-
    decode multi-agent stress test.

Serving default until the isolation gate passes: **singleton MTP lane + plain concurrent work**.
PP2/layer ownership remains primary; TP2 remains the falsification/control topology.

### Dual-M1 DS4-0731

No topology or target change. Continue the existing gate:

1. sane/coalesced Metal mappings;
2. OS build / command-buffer completion behavior;
3. GPU-busy fraction and wired residency;
4. same-host control;
5. then PP bubbles, interconnect and multi-session filling.

### RTX 5070 Ti 27B

Keep the existing order:

1. ubatch 256/512 + prompt-shape stability matrix;
2. Q3_K_XL + native MTP speed lane;
3. small-N Blackwell verify A/B;
4. add BF16/Q6_K/Q4_K-imatrix **MTP-head** A/B for context headroom;
5. retain GSQ-RCO as the separate context/quality lane.

### Single M1 Max 64 GB 27B

No performance-target change. Retain ANE hidden-bank admission accounting, cache-block granularity,
resource-release checks and the exact P69 boundary.

## Target / verifier consequence

**Targets remain unchanged:**

| Model / hardware | Working TG | Confidence | Working PP | Confidence |
|---|---:|---:|---:|---:|
| Flash-Next — 2x M1 Max 64 / TB4 | 40 tok/s | ~55-60% | 400 tok/s | ~55-60% |
| Qwen3.8-27B — M1 Max 64 | 25 tok/s | ~55-60% | 110 tok/s native | ~60% |
| Qwen3.8-27B — RTX 5070 Ti 16 GB | 120 tok/s | ~60-65% | 250 tok/s | ~55-60% |
| DS4-0731 — 2x M1 Max 64 / TB4 | 15 tok/s | ~60-65% | 180 tok/s | ~60% |

No direct exact physical receipt justifies moving a row.

P69 is unchanged. **P69B12 remains frozen/promoted and P69B13 remains next using existing profiling
only.** External runtime evidence must not reopen closed verifier experiments.
