# External runtime watch — 2026-09-14 15:17 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-14 11:43:49 UTC` through the user-request cutoff `2026-09-14 19:17:07 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, comment-only activity or a merge timestamp for measurements that already existed before the boundary.

**New hard source-freshness boundary for the next complete external search: `2026-09-14 19:17:07 UTC`.**

---

## Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP | Status |
|---|---:|---:|---|
| Qwen3.8-Flash-Next — 2x M1 Max64 / TB4 | **40 tok/s @ ~128K active context** | **400 tok/s** | planning objective; no exact receipt |
| Qwen3.8-27B — M1 Max64 | **25 tok/s** | **110 tok/s native/exact-runtime** | unchanged |
| Qwen3.8-27B — RTX5070Ti16 | **120 tok/s** | **250 tok/s** | unchanged |
| DS4-0731 — 2x M1 Max64 / TB4 | **15 tok/s** | **180 tok/s** | unchanged |

**No canonical target moved. P69 remains isolated. P69B12 stays frozen/promoted; P69B13 remains next only from existing measured internal GDN/projection/downstream-tail evidence.**

---

# Fresh evidence

## vLLM #56822 — bill hidden-state extraction at its own physical KV-group width

Source created `2026-09-14 11:43:58 UTC`, nine seconds after the previous cutoff.

**FRESH NEW / ADMISSION-ACCOUNTING TRANSFER.**

Hybrid Mamba/MLA hidden-state extraction could create a one-layer extraction group but charge its memory using the widest peer cache-group width. A roughly 5.4-GiB extraction allocation could therefore be billed as roughly 130 GiB and reject startup even though the physical allocation fit.

The fix splits the relevant cache group down to one layer when hidden-state extraction is present, so the accounting width matches the physical extraction page width. Targeted tests cover the extraction case while ordinary layouts remain unchanged.

**Project consequence:** logical membership and physical billing width are distinct identities. Any Flash/MTP auxiliary state, hidden snapshot, draft handoff or cache sidecar must be admitted using the allocation geometry it actually owns, not the maximum width of a neighboring group.

## ds4 #1042 — fuse single-box V4.1 Metal decode glue at exact rounding boundaries

Source created `2026-09-14 11:58:12 UTC`.

**FRESH NEW / STRONG APPLE-METAL FUSION TRANSFER.**

The single-token V4.1 graph paid dozens of tiny dispatches per layer for hyper-connection glue, router selection, shared-expert glue and attention post-processing. #1042 fuses those sequences while deliberately preserving the standalone reduction trees and BF16 rounding points.

Representative dispatch collapses:

- HC glue: **19 -> 6**;
- router: **11 -> 2**, and ->1 on M5 where the single-dispatch visibility rule is valid;
- shared expert: **12 -> 3**;
- multiple attention round/norm/RoPE/FP8/window-copy sequences collapse into fused tails.

M3 Ultra 512 GB, resident DeepSeek-V4.1-Flash-Q4, on top of queued decode #1041 + parallel Engram reads #1035:

- all fusions: **29.80 / 29.88 tok/s**;
- everything off: **25.34 tok/s**;
- delta: **+18–20%**, byte-identical greedy output;
- GPU busy/token: **36.9 -> 31.2 ms**.

Prefill is unchanged and TP remains unfused.

**Transfer:** do not transfer the percentage to Flash-Next or DS4-0731. Promote the engineering rule: fuse chains only after enumerating the exact physical reduction order and quantization/rounding boundaries. Small dispatch glue can still be a first-order decode cost even after command-buffer scheduling is fixed.

## vLLM #56831 — adaptive speculative decisions require rank consensus

Source created `2026-09-14 12:57:49 UTC`.

**FRESH NEW / DISTRIBUTED SPECULATIVE-CORRECTNESS TRANSFER.**

Adaptive DSpark derived verifier budget from rank-local confidence. Small numerical differences across TP ranks could therefore choose different total draft budgets or per-request boundaries, yielding divergent execution layouts and possible collective hangs.

The patch makes rank 0 authoritative for both the selected draft budget and partial-allocation capacities before request boundaries are built.

Validation:

- deliberately injected rank drift: original path produced **20 consensus mismatches** at TP2 and TP4; patched path produced **0**;
- 120 compiled allocation cases plus graph-boundary replays per run;
- natural adaptive execution remained active: **568** partial-budget steps TP2, **559** TP4, with exact cross-rank boundary agreement;
- TP2 and TP4 each completed **2304/2304** requests at observed concurrency 128 without failure or hang;
- GSM8K changes were within the measured run-to-run noise band.

**Project consequence:** speculative policy is not rank-local once it changes tensor shape, verifier width, request boundaries or collective geometry. For distributed Flash, the authoritative budget/boundary source and broadcast point belong in execution identity.

## ds4 #1047 — selective SSD expert staging for Qwen3.8 Flash-Next on a 32-GB M1 Max

Source created `2026-09-14 15:00:44 UTC`; substantive updates continued through the current window.

**FRESH NEW / DIRECT APPLE FLASH CAPACITY + EXPERT-I/O MECHANISM RECEIPT.**

Flash-Next previously rejected `--ssd-streaming`; its Q2 pack needed about 41.73 GiB resident even though the n-gram table already stayed on disk. #1047 keeps dense/shared/GDN/attention/HC weights mapped and streams only routed experts through the explicit-pread cache, extended for 512 IDs and top-10 routing. The Q2 model then runs on a **32-GiB M1 Max**.

Important implementation details:

- compact staging buffers contain only distinct selected experts;
- expert IDs remain original IDs through private address tables;
- cache sizing reserves static weights, context, recurrent state, MTP snapshots, prefill workspace, two staging windows and runtime headroom before expert capacity is assigned;
- read failures propagate rather than silently falling back to whole-layer rereads;
- staging buffers remain alive through GPU completion, including unretained command-buffer mode.

M1 Max 32 GiB, Qwen3.8-Flash-Next-Q2, short 29-token prompt / 50-token generation / MTP:

- initial whole-layer streaming: **4.55 tok/s**;
- selective expert staging: **7.86 tok/s**;
- delta: **+72.7%**;
- expert bytes returned by `pread`: **48.40 -> 12.02 GiB (-75.2%)**;
- output identical; 27 verifier cycles, 21 accepted drafts.

This is a deliberately short, Q2, over-capacity workload. It is **not** evidence for our Q6/Q8 resident dual-M1 target and the percentage must not transfer.

**Project consequence:** if we ever need an emergency over-capacity lane, route demand rather than layer size should determine the I/O unit. Whole-layer streaming is the wrong baseline for sparse experts. Keep this outside the primary resident 40@128K Flash plan unless capacity forces it.

## mlx-serve #425 — QSA prefix trim must bill transferred pooled history

Source created `2026-09-14 15:51:46 UTC`, merged `17:54:06 UTC`.

**FRESH NEW / DIRECT APPLE LONG-CONTEXT CACHE-ACCOUNTING CORRECTNESS.**

When an oversized QSA prefix-cache entry was trimmed, the chooser omitted pooled QSA history transferred onto the retained checkpoint. It could therefore select a nominally fitting prefix that still exceeded the byte cap and then evict the entire conversation.

A real M5 Max 128-GB log showed a 496,263-token entry with an 11,734.92-MB budget being trimmed to 491,520 tokens while the actual retained entry was still roughly **11,936.29 MB** after checkpoint shedding.

The fix includes transferred history in both trim policies. Regression tests cover new entries, replacements, budget compliance, later reuse and agreement between estimated checkpoint bytes and materialized pooled history.

**Project consequence:** a retained checkpoint is not just its checkpoint tensor. Any history/state reparented onto it is part of the physical retained byte bill. Our long-context cache ruler should charge post-trim state after ownership transfer, then verify the materialized resident total before admitting reuse.

## ds4 #1049 — gathered-KV reuse is stack-dependent, not automatically valuable

Source created `2026-09-14 16:14:31 UTC`.

**FRESH NEW / NEGATIVE-THEN-COMPOSITE METAL MICRO-OPT EVIDENCE.**

V4.1 scalar decode repeatedly gathered the same compressed KV rows across reuse layers. Reusing the gathered buffer gave:

- standalone exact PR: **16.62/16.63 vs 16.64/16.62 tok/s — flat**;
- integration stack with #1041 + #1035 + #1042 + #1043: **30.96/31.13 -> 31.45/31.42 tok/s**, about **+1.26%**;
- all outputs byte-identical.

**Project consequence:** an apparently redundant gather may be hidden under another bottleneck until scheduling/fusion is repaired. Do not prioritize micro-reuse from static operation counts alone; rerun it after major bottleneck-removal steps before discarding or promoting it.

## mlx-serve #427 — sampled MTP policies + paired routed gate/up on M5 Max

Source created `2026-09-14 16:39:24 UTC`.

**FRESH NEW / DIRECT APPLE FLASH SPECULATIVE-MECHANISM EVIDENCE WITH IMPORTANT CONFOUNDERS.**

The PR adds opt-in Typical-0.2 and TokenV3-0.95 sampled acceptance plus a paired physical-S=4 routed gate/up kernel for the validated mixed-4/8 Qwen3.8 pack. Exact acceptance remains default.

M5 Max low-context three-arm sweep, KV8, sampled D3, temp1/top-p.95/top-k20, same timed prompts:

| Input tokens | unchanged control | Typical + kernel | TokenV3 + kernel |
|---:|---:|---:|---:|
| 1,035 | 98.5 | 114.5 | 116.4 |
| 2,048 | 101.5 | 111.3 | 111.1 |
| 4,088 | 101.1 | 107.8 | 109.3 |
| 8,258 | 88.7 | 103.4 | 104.0 |
| 16,295 | 94.3 | 102.4 | 104.2 |
| 32,885 | 90.9 | 108.1 | 111.9 |
| 65,446 | 100.6 | 109.6 | 109.2 |

But the unchanged control predates the PR's seeded sampled-draft/correction fix, so this table measures the whole PR configuration and **cannot isolate either acceptance policy or kernel**.

The same-binary exact-acceptance kernel isolation is much smaller and cleaner:

- **70.377 -> 70.914 decode tok/s (+0.76%)** at a 16K / 1024-cap serving cell;
- wall **109.077 -> 108.675 s**;
- paired lengths and answer/reasoning digests matched.

Fresh JS quality screen: 79/100 control, 78/100 Typical, 77/100 TokenV3; HumanEval-JS 45/50 all arms; MBPP-JS 34/50, 33/50, 32/50. 128K–1M still require finite GDN-state/reference qualification and a larger memory gate.

**Project consequence:** keep sampled verifier-policy experiments separate from kernel experiments. The paired gate/up kernel alone is a sub-1% result in the clean cell; the large low-context deltas are configuration-level evidence only. Do not use them to move 40@128K.

## vLLM #56869 — align distributed ranks before sharded DFlash graph capture

Source created `2026-09-14 16:57:04 UTC`.

**FRESH NEW / DISTRIBUTED GRAPH-CAPTURE CORRECTNESS TRANSFER.**

Once a DFlash/DSpark draft is DCP-sharded, its captured graph contains a context-parallel collective. Capture is unsafe if ranks enter while peers are still completing earlier work. The observed fault disappeared under serialized kernel launch, identifying a race rather than an ordinary bounds error.

The fix, only when draft DCP > 1, does:

1. accelerator synchronization;
2. CPU-group DCP barrier;
3. graph capture.

8x MI355X, Kimi-K3 + DSpark TP8/DCP8: every boot previously died during speculator capture; with the alignment barrier the server reached startup in **280 s** with no steady-state serialization penalty and a 9/9 concurrency sweep completed rc=0.

**Project consequence:** collective-bearing graph capture has a rank-alignment precondition. For any future dual-node captured speculative path, capture identity includes effective draft parallelism, pre-capture device quiescence and group-consensus boundary.

## oMLX #3666 — model discovery should follow executable weight structure, not metadata alone

Source created `2026-09-14 18:22:58 UTC`.

**FRESH NEW / 27B DISTRIBUTED ROUTE-DISCOVERY CORRECTNESS.**

Published Qwen3.8-27B text quants can retain a populated `vision_config` and even vision tensors while stock loading sanitizes them away. The cluster fallback classifier therefore rejected real text-capable 27B checkpoints as VLMs unless users edited config or supplied an override.

The patch classifies the family using the actual `language_model.` weight root in `model.safetensors.index.json`. It was verified against Qwen3.8-27B-oQ4e on a real **2x M4 Max TP2** cluster; 201 discovery tests pass.

No throughput is reported and Q4 is not our preferred target quant.

**Project consequence:** requested/config metadata is not execution identity. Model-family admission should follow the weight structure and sanitize/load route that will actually execute, especially before rejecting distributed topology support.

---

# Newly landed / older measurement evidence — do not refresh benchmark timestamps

## vLLM #55309 — Qwen3.8-Flash-Next PLE residual + QSA output-gate fusion

Merged in this window at `2026-09-14 12:16:25 UTC`, but the PR and measurements predate the freshness boundary.

**NEWLY LANDED / RECOVERED OLDER MECHANISM EVIDENCE.**

It fuses the outer PLE residual add into short convolution and the optional QSA output gate into sparse-attention epilogues while explicitly preserving the original BF16/FP16 rounding boundaries.

Older B200 microbench evidence:

- PLE single-row decode **6.464 -> 4.480 us (1.443x)**;
- PLE prefill speedup **1.15–1.29x** across measured 16–8192-token sizes;
- QSA output-gate single-row **12.832 -> 11.616 us (1.105x)**, converging toward ~1% at large row count.

This is useful confirmation of the same fusion rule surfaced by fresh ds4 #1042, but it is not a fresh performance receipt and not Apple evidence.

## vLLM #56633 — V4.1 mHC post/pre folding landed with older tuning evidence

Merged in this window at `2026-09-14 18:57:37 UTC`; substantive tuning work predates the boundary.

**NEWLY LANDED / RECOVERED OLDER FUSION-HEURISTIC EVIDENCE.**

The fused TileLang seam wins roughly **1.3x at tiny decode widths**, ~1.17x at 16 tokens and reaches break-even around 32 against a corrected/tuned unfused baseline. The important methodological lesson is that an inherited split-K heuristic was itself 5–19% off on unfused seams, and an apparently good fusion cutoff would have been wrong if compared only against that slow baseline.

**Promote methodology only:** every fusion should be compared against a separately tuned unfused control; otherwise a bad baseline can exaggerate both the gain and the valid shape range.

---

# External HF / Reddit screen

The fresh web screen surfaced several September-14 model-card updates, including Qwen3.8 Flash-Next MTP/runtime measurements on DGX Spark and newly crawled M3-Ultra model cards. They are useful context but **not promoted as fresh active-topology receipts** because exact source times relative to this 11:43:49–19:17:07 UTC window are unavailable and the hardware/topology differs from the canonical lanes.

Notable context only:

- a Q5 DGX-Spark card reports a same-artifact MTP runtime optimization around **+3.34% decode at cold 8K** with exact frontier-logit/generated-ID parity;
- community M3-Ultra Flash-Next cards continue to show that native MTP can range from negative to materially positive depending on quant/runtime/acceptance, reinforcing that acceptance alone is not a speed claim;
- the older M1-Max-32 27B MLX-vs-llama.cpp community cell remains unchanged and is not refreshed.

No crawler timestamp is treated as evidence time.

---

# Fresh-screen negatives

- No exact fresh **dual-M1 Flash-Next** 40@128K or 400-PP receipt.
- No exact fresh **M1 Max64 Qwen3.8-27B** Q6/Q8 receipt.
- No exact fresh **RTX5070Ti16 Qwen3.8-27B** canonical-lane receipt.
- No exact fresh **dual-M1 DS4-0731** receipt.
- No target movement.
- No P69 reorder/reopen.

---

# Consequences by lane

## Dual-M1 Flash-Next

Keep **PP2/layer ownership primary**, TP2 control.

Add these concrete checks/experiments:

1. preserve exact rounding/reduction boundaries when fusing PLE/QSA/HC/MoE glue; record fused-vs-tuned-unfused, not fused-vs-default-only;
2. rank-authoritative speculative budget and request-boundary consensus before any shape-changing distributed verification step;
3. rank alignment before graph capture if the captured draft contains collectives;
4. post-trim QSA cache admission must include history/state transferred to the retained checkpoint;
5. if capacity/offload is ever needed, stage **selected experts**, not whole sparse layers; keep this emergency lane separate from the resident Q6/Q8 target;
6. sampled-verifier policy and verifier-kernel changes require separate A/B cells; do not attribute whole-configuration gains to a kernel;
7. retain the previous pass's verifier route-pack/indexed-gather/down-reuse work, 4096/8192 transient-aware prefill sweep and Metal commit-vs-wait instrumentation.

No target movement.

## Qwen3.8-27B M1 / P69

No target movement. **P69B12 frozen/promoted; P69B13 next.**

Fresh evidence reinforces two existing principles without changing P69 order:

- remove major scheduling/fusion bottlenecks before judging small reuse ideas (#1049);
- model/distributed-route identity should follow executable weight structure rather than metadata flags (#3666).

The clean #427 paired gate/up isolation at +0.76% is a useful warning against treating a large whole-stack speculative delta as proof that one small verifier kernel is high leverage.

## RTX5070Ti16

No target movement. No exact post-boundary 5070-Ti receipt appeared. Existing SM120 route/stride and long-prompt concurrency gates remain.

## DS4-0731 dual M1

No target movement. #1042/#1049 are V4.1/M3-Ultra evidence and #1047 is Qwen Flash/Q2/M1-Max capacity evidence, not DS4-0731 receipts. Promote the exact-boundary fusion methodology and stack-aware microbenchmark sequencing, not their percentages.

---

# Standing rules added / reinforced

- **Physical billing width** belongs to execution identity; never charge a singleton auxiliary allocation at a neighboring group's maximum width.
- **Fusion exactness** means preserving reduction trees and intended rounding/quantization boundaries, not merely matching a loose final-output tolerance.
- Compare every fused candidate against a **separately tuned unfused baseline**; inherited heuristics can make fake headroom.
- Speculative choices that alter shape, budget, request boundaries or collective geometry require an **authoritative rank and consensus point**.
- Collective-bearing graph capture requires **rank alignment and device quiescence before capture**.
- Cache trim admission must price state **after ownership transfer/reparenting**, then verify materialized resident bytes.
- Sparse over-capacity I/O should be demand-shaped by selected experts; full-layer streaming is not an acceptable sparse baseline when selective staging is possible.
- A micro-optimization that is flat before major bottleneck removal may become measurable after the bottleneck is removed; keep stack-aware retest points.
- Requested model metadata is weaker than the physical weight/load/sanitize route that actually executes.
- Context remains part of target identity. A low-context speculative win does not satisfy 40 tok/s at ~128K.
- No external result silently changes P69 or any canonical target.
