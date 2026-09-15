# External runtime watch — 2026-09-15 07:34 ET

## Search window

Complete pass over substantive source activity strictly after `2026-09-15 10:01:18 UTC` through the user-request cutoff `2026-09-15 11:34:26 UTC`.

Evidence timestamp remains the substantive source / measurement timestamp, not crawler time, rebase time, comment-only activity, or a later merge of already-known measurements.

## Executive result

No exact active-topology receipt appeared for any canonical target. No target moves.

Promoted fresh mechanisms in this window:

1. vLLM #56995 — generic MTP local argmax reduction: replace full `[batch,vocab]` cross-rank logits materialization with tiny `(value,index)` candidate exchange; exact token agreement, large-batch micro-step wins, but a small-batch crossover means it must be adaptive / gated.
2. llama.cpp #28943 — Qwen3.8-27B at 98,304 context on RX 7900 XTX: skip fully masked KV tiles in shared/unified-cache Flash Attention prefill; ~25% request-time reduction / ~35% prefill throughput gain for the repeated-slot workload.
3. vLLM #56996 — attention execution geometry must come from the physical KV-cache group, not model-global metadata; correcting the group-local KV-head/head-dim geometry changes kernel selection and yields 23–60% kernel-level gains on the affected heterogeneous-attention regime while reducing scratch.

Fresh oMLX #3680/#3681 and frontend/CI-only changes were inspected but not promoted to the performance stack. A fresh Hugging Face Qwen3.8-27B DFlash2 result was rediscovered, but its substantive source timestamp is not exposed reliably enough to advance this hard window and it remains external context only.

## Promoted — vLLM #56995: local argmax reduction for generic MTP

Source created: `2026-09-15 10:26:35 UTC`.

The generic DeepSeek-style MTP path could not use `use_local_argmax_reduction`; enabling it raised at startup because `get_top_tokens()` was missing. The patch wires the generic MTP drafter into the existing reduction where each TP rank computes its local top candidate and only tiny `(value,index)` records cross ranks rather than a full vocabulary tensor.

Correctness evidence:
- TP2, batch 1..1024: token agreement = 1.0000 in all 20 measured cases.
- Cross-rank tie handling included.
- A deliberately wrong variant that skipped the family-specific `shared_head` normalization dropped agreement as low as 0%, so the semantic placement is load-bearing.

GLM-5.2-shape TP2 micro-step:

| batch | full-logits path | local reduction | delta |
|---:|---:|---:|---:|
| 1 | 207.9 us | 240.1 us | -15.5% |
| 16 | 290.1 us | 296.3 us | -2.2% |
| 32 | 354.7 us | 292.7 us | +17.5% |
| 128 | 716.1 us | 319.7 us | +55.4% |
| 512 | 2169.8 us | 537.3 us | +75.2% |
| 1024 | 4151.6 us | 881.6 us | +78.8% |

DeepSeek-V3 shapes show the same crossover; reported +49.3% at batch128 and +75.2% at batch1024.

Communication example:
- GLM-5.2, TP2, batch512: default ~151.2 MiB vs reduction ~8.0 KiB per draft step.
- GLM-5.2, TP8, batch1024: default ~302.5 MiB vs reduction ~64.0 KiB.

No trustworthy E2E throughput claim was made because same-arm run drift was ~8.5%.

### Transfer to our distributed Lightning MTP

Promote as a topology/economics rule, not an active-target receipt:

- Never ship or gather a full vocabulary tensor across TB4 when the authoritative downstream decision only needs a top candidate / tiny shortlist.
- Candidate selection semantics are family-specific: the exact normalization/head boundary must match the normal logits path before reducing.
- The optimization has a real crossover: at tiny batch the fixed reduction overhead can lose. Our PP2 Lightning implementation should select local-reduction vs ordinary local head work from measured row count / payload, not hard-wire one path.
- Extend the distributed ruler with `bytes_cross_link_per_draft_step`, `rows_per_head_projection`, and `candidate_payload_bytes`.

This composes directly with the previous "collapse semantic state before transport" rule.

## Promoted — llama.cpp #28943: skip fully masked KV tiles in shared-cache prefill

Source created: `2026-09-15 10:41:28 UTC`.

Direct model: `Qwen3.8-27B-UD-Q4_K_M`.
Hardware/runtime: RX 7900 XTX, ROCm 7.2.1, full offload, Flash Attention.
Context: 98,304.
Workload: two unified-cache slots, 40,960 input tokens + 64 output, slot order 0/1/0, prompt reuse disabled.

The AMD WMMA attention path still loaded K/V and executed matrix work for interior tiles that were completely masked for the current sequence. The change checks a full tile cooperatively and skips it only when every relevant mask value is exactly `-INFINITY`.

Third-request means over three independent restarts per arm:

| KV | stock request | patched request | time reduction | prefill throughput gain |
|---|---:|---:|---:|---:|
| F16 | 77.414 s | 57.833 s | 25.29% | 35.17% |
| Q8_0 | 79.793 s | 59.488 s | 25.45% | 35.85% |

All 36 compared generated token-id positions matched; Wikitext-2 perplexity also matched the stock result at the printed precision.

### Transfer to our 27B and Flash long-context rulers

Backend is AMD WMMA, so this is mechanism transfer only. Promote these checks:

- In any shared/ring/unified KV layout, distinguish logical cache span from tiles actually visible to the current query/sequence.
- A long-context attention kernel can waste bandwidth and matrix work on *known-dead* masked tiles even when its arithmetic kernel is otherwise efficient.
- Add `masked_tiles_total`, `masked_tiles_skipped`, and `bytes_read_from_dead_tiles` to long-context prefill profiling where the backend permits it.
- For our QSA/indexer path, apply the same principle after selection: work must remain bounded to selected/live physical spans all the way through K/V gather and attention, not merely at the selector.

This strengthens the existing rule that static graph/cache geometry does not justify max-span work.

## Promoted — vLLM #56996: physical KV-group geometry controls kernel route

Source created: `2026-09-15 10:26:54 UTC`.

A Triton attention metadata builder used model-global KV-head count and head dimension even though builders are created per KV-cache group. On heterogeneous attention this meant one path sized the actual kernel grid using the physical group's KV tensor while the route-selection threshold and scratch sizing used different, global geometry.

Gemma-4 example:
- sliding groups: physical `kv=8, head=256`; builder previously used head=512.
- full-attention group: physical `kv=2, head=512`; builder previously used kv=8.

On MI355X at ctx4096, fixing the full-attention group changed the 2D/3D route at intermediate batch sizes:

| batch | before | after | gain |
|---:|---:|---:|---:|
| 24 | 325.7 us | 129.6 us | +60.2% |
| 32 | 329.4 us | 161.9 us | +50.9% |
| 48 | 335.7 us | 215.8 us | +35.7% |
| 64 | 336.3 us | 258.6 us | +23.1% |

Outside the affected route-selection range results were flat. Aggregate softmax scratch fell 48.2 -> 44.2 MiB and KV capacity was unchanged.

### Transfer

Promote as execution-identity rule:

- Kernel/admission metadata must be derived from the *physical cache/execution group* that the kernel consumes, not a model-global architectural default.
- Route thresholds, scratch dimensions, launch geometry and physical tensor geometry must share one provenance.
- Add an explicit consistency check in our QSA/attention ruler: `physical_heads`, `physical_head_dim`, selected kernel, launch grid, scratch shape, and allocator bill must all describe the same group.

This joins prior physical packing, sentinel, workspace-view and route-provenance rules.

## Fresh but not promoted

### oMLX #3680 — hidden AppleDouble safetensor sidecars
Created `2026-09-15 10:33:49 UTC`.
Fixes checkpoint shard discovery on exFAT/NTFS/SMB by excluding dot-prefixed AppleDouble/resource-fork files before header parsing. Useful robustness, but no inference-target mechanism.

### oMLX #3681 — Anthropic stream prefill-guard error propagation
Created `2026-09-15 10:33:52 UTC`.
A finished error output could stop the Anthropic generator before the next pull raised the typed prefill rejection, fabricating a successful empty `end_turn`. Correctness/observability issue, not a throughput target mechanism. It does reinforce that admission rejection must survive every API/streaming wrapper, but no target change.

### vLLM #56994 — GLM-5.3 reasoning parser semantics
Created `2026-09-15 10:24:02 UTC`.
Frontend/parser correctness only; no runtime optimization promoted.

### vLLM #56997/#56998/#56999
Created 11:06:38 / 11:09:35 / 11:19:51 UTC.
Backend preference, Rust reasoning normalization and XPU weight-cache changes respectively; no active-lane mechanism strong enough to promote in this watch.

### llama.cpp #28944/#28945
Created 10:58:10 / 11:26:51 UTC. CI/docs only.

## External HF/Reddit screen

A Hugging Face Qwen3.8-27B DFlash2 card currently reports on one H200 that DFlash2 beats MTP and DSpark across several tasks, with DFlash2 acceptance length around 4.10-5.46 depending on task and C1 output throughput around 184-236 tok/s versus MTP around 135-179 tok/s. A separate RTX5090 NVFP4 discussion reports DFlash2 121.52 tok/s vs MTP 106.19 vs AR 64.74 in a single-stream ShareGPT run.

These are **not promoted in this hard-window watch** because the web-visible card/discussion did not expose a reliable substantive source timestamp inside `10:01:18Z -> 11:34:26Z`; crawler freshness is not evidence freshness. They remain background evidence for the already-known DFlash2-vs-MTP trade study.

## Main-branch merge activity

vLLM merged #56962 (DeepSeek-V4.1 Mega-mHC) at `11:01:07 UTC`, but the PR was created at `06:44:50 UTC`, before this watch window. Per standing methodology, merge time does not refresh the underlying measurements, so this watch does not treat it as new evidence.

mlx-serve main: no commits in the window.
oMLX main: no commits in the window.

## Cutoff edge

vLLM #57000 was created at `2026-09-15 11:34:37 UTC`, **11 seconds after the user cutoff**. It was deliberately excluded.

Its subject is Mamba-align admission overcount after external-KV resume; it should be the **first vLLM item checked next pass**.

## Target status

Canonical targets remain unchanged:

- Qwen3.8-Flash-Next dual M1 Max64/TB4: **40 tok/s @ ~128K active context**, **400 tok/s cold PP**.
- Qwen3.8-27B one M1 Max64: **25 tok/s**, **110 tok/s native/exact-runtime cold PP**.
- Qwen3.8-27B RTX5070Ti16 + host RAM: **120 tok/s**, **250 tok/s cold PP**.
- DS4-0731 dual M1 Max64/TB4: **15 tok/s**, **180 tok/s cold PP**.

No fresh exact dual-M1 Flash receipt, M1Max64 27B receipt, controlled 5070Ti target receipt, or dual-M1 DS4-0731 receipt appeared.

## Planning impact

No P69 reorder/reopen.

For distributed Lightning MTP, add local top-candidate/shortlist reduction to the TB4 design ruler, but gate it by measured row count because the fresh vLLM evidence shows a real low-batch crossover.

For long-context attention/QSA, add two explicit audit rows:
1. dead/masked physical tiles actually read or multiplied;
2. group-local physical geometry vs route-threshold/scratch geometry.

The fresh evidence improves confidence in the optimization stack, not the canonical target calibration.

## New hard freshness boundary

`2026-09-15 11:34:26 UTC`
