# Runtime Research Watch — 2026-09-01 Early Evening

Scope: external runtime/model research only. This note does **not** modify the certified P69 verifier state. **P69B13 remains next, using existing profiling data only.**

This is a delta from `RESEARCH-WATCH-2026-09-01-LATE-AFTERNOON.md`.

## Qwen3.8-Flash-Next

### New same-generation calibration: reproducible M1 Max 64 GB context sweep

Source: https://github.com/mihailescu2m/llama.cpp

The custom llama.cpp fork now publishes a reproducible benchmark table specifically for **M1 Max 64 GB (~400 GB/s)** rather than only anecdotal Reddit numbers. The tested Flash-Next checkpoint is `UD-iQ4_K_XXS` at **82.90 GiB**, with a **32 GiB routed-expert cache** and SSD expert streaming.

Target-only `llama-bench` results (`-r 2`, `-r 1` at 128K):

| Context | Prefill | Target-only TG |
|---:|---:|---:|
| 4,096 | 160.64 tok/s | 10.91 tok/s |
| 8,192 | 159.11 | 10.82 |
| 16,384 | 156.00 | 10.67 |
| 32,768 | 150.81 | 10.02 |
| 65,536 | 144.37 | 9.19 |
| 131,072 | 132.79 | 8.03 |

With the native MTP head, the fork reports:

- **17.6 tok/s at 4K**
- **13.0 tok/s at 128K**
- **+51% to +91% decode uplift depending on context**
- MTP costs **5.7–9.2% of prefill** in that sweep

This is the strongest reproducible same-silicon calibration currently available for the dual-M1 project. It is still a **single M1 Max with SSD expert streaming**, not a two-node resident PP result.

### Same author, more aggressive current configuration: ~12.9 -> ~22 tok/s with MTP

Current Reddit post from the same fork author reports a more aggressively optimized custom-Q4 configuration on the same **M1 Max 64 GB**:

- target-only decode: **~12.9 tok/s**
- native MTP decode: **~22 tok/s** (**~+70%**)
- prefill around 4K: roughly **180 tok/s without MTP / ~170 tok/s with MTP**
- prefill at 256K: roughly **150 tok/s**
- Q4_0 MTP is reported to retain acceptance similar to the author's Q8_0 control while using less RAM
- dynamic MTP depth disables speculation when context/acceptance economics turn negative

Treat this as an **updated configuration from the same source**, not an independent second receipt. The README sweep above is the cleaner reproducible baseline; the ~22 tok/s result establishes additional headroom in the fork's tuned configuration.

### Implication for the exact 2x M1 Max / TB4 plan

The exact two-M1 RPC report still has **no published sustained TG/PP number**. It remains a correctness receipt only.

The new single-M1 data changes calibration in two ways:

1. **MTP is demonstrably valuable on M1 Max itself**, including at long context; this is no longer inferred from M3/M5 hardware.
2. **40+ tok/s B1 on two M1 Maxes should remain a stretch target, not a near-certainty.** A single streamed M1 already reaches ~17.6 reproducibly and ~22 in the author's tuned configuration, but PP2 does not automatically double B1 because the stages are serial unless verify spans / microbatches / concurrent work create overlap.

Updated planning confidence for a mature dual-M1 Flash-Next stack (forecast, not measurement):

- **>=30 tok/s B1:** ~90%
- **>=35 tok/s B1:** ~75–80%
- **>=40 tok/s B1:** ~60–65%
- **>=45 tok/s B1:** ~35–40%

This is a deliberate downward calibration from the earlier ~85% confidence on `>=40 tok/s`: the new same-silicon measurement narrows the uncertainty and shows how much of the remaining gain must come from resident two-node execution, better Metal kernels/QSA paths, high MTP acceptance, and deliberate PP overlap rather than simply adding a second 400 GB/s machine.

The **multi-agent aggregate-throughput outlook remains stronger than the B1 outlook** because independent requests can fill PP bubbles even when a single dependent decode chain cannot.

### Bring-up consequence

For the eventual dual-M1 benchmark ladder, record these controls explicitly:

- single M1 target-only and native-MTP at 4K / 32K / 64K / 128K
- dual-M1 PP2 target-only at the same contexts
- dual-M1 PP2 + MTP, with acceptance and committed tokens/cycle
- B2/B4/B6 aggregate throughput and per-agent throughput
- SSD expert streaming on/off where residency permits
- PP stage idle time / overlap percentage

This lets the project separate gains from **removing SSD expert traffic**, **MTP**, and **pipeline utilization** instead of attributing everything to the second Mac.

## DeepSeek V4 Flash 0731

### DS4 #930 — decouple resident sessions from active inference

PR: https://github.com/antirez/ds4/pull/930

DS4 now proposes separate limits for:

- resident KV/session slots (`--batched-session`)
- simultaneously active inference requests (`--max-active-requests`)

Example: keep ten sessions resident while allowing only one active request. This is admission-control work, not a throughput result, and the PR explicitly notes that reuse-aware slot selection is separate.

Implication for the Flash-Next multi-agent server: **memory residency and decode concurrency should be separate scheduler controls.** The two-M1 system may profitably keep more agent sessions warm than it actively decodes at once. That is especially relevant if SSD expert streaming frees model-residency memory for KV/GDN/prefix state.

No new DS4 result in this pass changes the PP2-first topology decision.

## Qwen3.8-27B exact verifier track

Layr challenge: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge

Fresh search still shows:

- frontier **3.7291100105909**
- #1481 newest visible submission
- no #1482+ promoted result

No external evidence changes the frozen exact-Q8 plan. **P69B13 remains next, existing profiling data only.**

## Updated decisions

1. **The same-generation M1 uncertainty is materially lower.** We now have a reproducible M1 Max 64 GB context sweep with target-only and MTP numbers.
2. **MTP-over-M1 is proven useful; MTP-over-TB4 PP is still unmeasured.** Do not conflate the two.
3. **Recalibrate `>=40 tok/s` mature dual-M1 B1 from ~85% to ~60–65%.** The target remains plausible, but now we can see the amount of software/topology gain still required.
4. **Multi-agent aggregate throughput remains the stronger opportunity.** Independent agents can create the pipeline depth that B1 lacks.
5. **Separate resident-agent count from active-decode count.** DS4 #930 provides a clean scheduler analogue.
6. **PP2 remains primary; TP2 remains a falsification benchmark.** Nothing in this pass changes that topology call.
7. **27B certified verifier state remains unchanged.** P69B13 is still next.
