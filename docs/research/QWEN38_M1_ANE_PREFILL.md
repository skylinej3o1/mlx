# Qwen3.8-27B on M1 Max 64GB — ANE-assisted prefill

Status: **CORE / promoted field evidence**

This note records fresh direct evidence that ANE-assisted prompt processing is useful on the exact first-generation Apple Silicon class MXFORGE targets: **M1 Max 64GB**.

Primary field report:

- canonical thread: https://www.reddit.com/r/oMLX/comments/1vumbhw/experience_with_ane_on_m1_max_64gb/
- user-supplied Reddit share link: https://www.reddit.com/r/oMLX/s/JR5dbVaMfI

The opaque share token did not resolve reliably through normal web access, so the canonical post was recovered by enumerating fresh `r/oMLX` posts and matching subreddit, timing, hardware, and topic. Treat the canonical mapping as **high-confidence but not cryptographically proven** until Reddit's shortlink resolver is available again.

## Reported setup

Field-report configuration:

- hardware: M1 Max 64GB
- model family: Qwen3.8-27B
- quant/runtime path: `oQ4e-fp16-mtp`
- custom-kernel HEAD build
- full Xcode / Metal toolchain
- group size: 64
- prompt block: 1024
- `Use both ANE`: disabled
- attempts with prompt block 2048 and/or GS128 reportedly produced tuning failures

These are community-reported settings, not MXFORGE-certified settings.

## Reported results

| M1 Max 64GB / Qwen3.8-27B | GPU-only / no ANE | ANE-assisted | Delta |
|---|---:|---:|---:|
| PP at ~1K | 134.5 tok/s | **198.0 tok/s** | **+47.2%** |
| TTFT at ~1K | 7.62 s | **5.18 s** | **-32.1%** |
| end-to-end at ~1K | 14.60 s | **12.21 s** | **-16.4%** |
| PP at ~4K | 139.7 tok/s | **171.1 tok/s** | **+22.5%** |
| TTFT at ~4K | 29.34 s | **23.95 s** | **-18.4%** |
| end-to-end at ~4K | 37.93 s | **31.29 s** | **-17.5%** |
| decode at ~1K | 18.4 tok/s | 18.3 tok/s | essentially unchanged |
| decode at ~4K | 15.0 tok/s | 17.5 tok/s | do not attribute to ANE without controlled replay |
| peak-memory cost | baseline | roughly **+9.5–9.6 GB** | significant residency tradeoff |

The strongest transferable observation is **prompt-processing / TTFT improvement**, not decode acceleration. The ~1K decode result is effectively unchanged, which is consistent with ANE being used primarily as a heterogeneous prefill engine.

Do not promote the 4K decode difference as an ANE decode win without matched repeated runs; workload state, MTP acceptance, runtime variation, or measurement noise may explain it.

## Why this changes MXFORGE priority

Before this field report, the M1 ANE branch was supported mainly by:

- oMLX heterogeneous ANE/GPU implementation work;
- newer-Apple demonstrations;
- indirect M1 Pro community evidence.

This report adds direct evidence on **M1 Max 64GB + Qwen3.8-27B + MTP**, making heterogeneous prefill a near-term experiment rather than a speculative portability question.

The working hypothesis is now:

> ANE-assisted prefill can materially reduce cold TTFT on M1 Max, but costs enough unified memory that it should be a **context/memory-dependent runtime mode**, not an always-on default.

## MXFORGE experiment plan

Do not multiply the current MXFORGE decode champion by the field-report PP percentage. Reproduce the prefill path independently on our exact model/quant/runtime.

### Stage 0 — frozen controls

Use identical serialized prompts and output budgets. Record:

- exact model + quant hash
- runtime / commit
- prompt block
- ANE mode
- group size
- context length
- PP tok/s
- TTFT
- decode tok/s
- end-to-end wall time
- steady + peak memory
- cached vs newly processed tokens

### Stage 1 — GPU-only baseline

Measure at least:

- 1K
- 4K
- 8K
- 16K
- 32K

and, where memory permits, larger cold-prefill points.

### Stage 2 — ANE + GPU

Reproduce the field-report-friendly starting point:

- GS64
- prompt block 1024
- single-ANE / conservative mode first

Then sweep:

- ANE fraction / work split
- prompt block size
- one vs both ANE engines if supported/stable
- MLP and GDN fractions independently

### Stage 3 — memory crossover

Because the field report observed roughly +9.5–9.6GB peak memory, explicitly find the context point where ANE residency/workspace stops being worth its TTFT gain.

Potential policy shape:

```text
short / medium cold prompt
    -> ANE + GPU prefill
    -> release transient ANE buffers
    -> optimized Metal/MTP decode

high memory pressure / very long context
    -> GPU-only prefill
    -> preserve unified memory for KV, prefix cache, verifier workspace, output reserve
```

Do not assume the crossover is a fixed context threshold; include free/wired memory and expected remaining session work.

## Agentic-use interpretation

ANE prefill and prefix caching solve different problems and should stack:

1. **avoid cold prefill whenever possible** through exact prefix reuse;
2. when cold or delta prefill is unavoidable, **make it faster** through heterogeneous ANE/GPU execution.

For persistent coding agents, prefix-cache hit rate may still dominate total wall time. The ANE branch is most valuable for:

- first request / cold session startup
- compaction/rebase events
- large tool-schema or repository-prefix changes
- cache misses
- explicit long-context imports

## Certification rule

This source is **field evidence**, not a project benchmark. Promotion to a measured MXFORGE result requires paired replay on our M1 Max 64GB with a fixed quant/runtime and independent wall-clock validation.

The target metric is not merely PP tok/s:

> **end-to-end time-to-first-useful-token at a defined memory reserve**, with decode quality and long-context capacity preserved.
