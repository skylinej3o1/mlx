# External runtime watch — 2026-09-17 06:33 ET

## Search window

Complete source-time pass over substantive activity strictly after `2026-09-16 16:46:32 UTC` through the user-request cutoff `2026-09-17 10:33:10 UTC`.

Evidence time is the substantive source / measurement time, not crawl time, merge time, rebase time, or a later merge of an older result. I screened PR-level summaries as well as commits, specifically to avoid repeating the DS4 #1062 miss from the previous cycle.

The boundary is hard: vLLM #57351 was created at `2026-09-17 10:33:33 UTC`, 23 seconds after the requested cutoff, so it is explicitly excluded from this watch and belongs to the next window.

## Executive result

No exact active-topology receipt appeared for any canonical target. **No target moves.**

Canonical planning targets remain:
- Qwen3.8-Flash-Next, dual M1 Max 64GB/TB4: **40 tok/s at ~128K active context / 400 tok/s cold PP**.
- Qwen3.8-27B, one M1 Max64: **25 tok/s / 110 tok/s native cold PP**.
- Qwen3.8-27B, RTX 5070 Ti 16GB + host RAM: **120 tok/s / 250 tok/s cold PP**.
- DS4-0731, dual M1 Max64/TB4: **15 tok/s / 180 tok/s cold PP**.

The headline is nevertheless unusually relevant: **DS4 #1068 supplies the first exact M1 Max 64GB Qwen3.8-Flash-Next receipt in this watch chain.** On Q2, one M1 Max sustains about 24.4 tok/s through 16K with roughly 275 tok/s prefill; a real 32,113-token prompt still produces 22.76 tok/s with 271.94 tok/s prefill. MTP raises short-context prose generation to 28.91 tok/s. A 131072 context configuration loads at 48.44 GiB planned, but there is **no 128K generation-rate receipt** in the PR.

That strengthens the feasibility prior for the dual-M1 project, especially the memory/admission side, but it does not justify extrapolating two Macs to 40 tok/s at 128K: the measurement is Q2 rather than the preferred quality-preserving lane, uses DS4 rather than the eventual distributed MLX path, contains no TB4 transport, and does not measure 128K decode.

Other promoted evidence materially sharpens implementation/certification:

1. **DS4 #1067** reports a 45% V4.1 Metal decode improvement on pre-M5 Apple silicon by collapsing command-buffer waits, overlapping Engram reads and reducing encode overhead: 17.94 -> 26.07 tok/s on M3 Ultra 512, with identical output. This is strong Apple scheduling-transfer evidence, not a Flash-Next rate transfer.
2. **llama.cpp #29019** shows batch reorder can silently feed DFlash another token's hidden state even when KV streams are separate. Restoring original row identity improved Qwen3.8-27B + DFlash2 Q4_K_M C16 mean acceptance length 3.3531 -> 3.9211 (+16.94%).
3. **mlx-serve `a7e22dcb`** proves replay segmentation itself is numerical identity on Flash Next: warm restore split a 31-token tail as 30+1 while cold ran 31, changed BF16 tiling and flipped a near-tied greedy token. Restoring the tail as one span makes warm/cold logprobs exact.
4. **mlx-serve `4e9bdf79`** fixes dense Qwen3.8-27B grouped sampled MTP when rows have unequal draft lengths: the verify tensor is padded to the group's widest draft, so an acceptance graph must slice the row's live `1+m` positions before reshape.
5. **oMLX #3702 fresh commits `0c779662` / `64204dbe`** make failed MTP handoff fail closed or rebuild committed cache before resuming, and prevent prefill-interrupted intervals from polluting the adaptive batch-cost model.
6. **vLLM #57261 / #57270 / #57262** strengthen physical admission accounting: speculative recurrent scratch should be billed by simultaneously running requests, profiling must actually exercise reachable MoE routes, and distributed receive workspace needs an explicit worst-case routing bound rather than whatever skew a dummy profile happened to generate.
7. **vLLM #57317 / #57260 / #57280** sharpen recurrent-state identity: fixed-tail ring buffers need their own slot mapping, context-parallel address localization is per cache-group rather than a global process property, and batch-invariant GDN includes row-tiling/reduction topology.
8. **vLLM #57329** demonstrates that recurrent checkpoint creation need not force a second model forward: one full prompt forward can export intermediate recurrent state at the logical checkpoint boundary. On the reported Nemotron setup this cut TTFT by roughly 13–18% without materially changing prompt tok/s.
9. **vLLM #57318** shows a narrow BF16 GDN projection can dominate a decode hot path at speculative M=2–4. On RTX 5090 Qwen3.8-27B, a bounded FlashInfer split-K path cut that projection from 27.2 us to 3.40 us/call and total decode 1494.3 -> 1397.7 ms (-6.5%). This is NVIDIA transfer evidence for our GDN routing work, not an Apple throughput receipt.
10. **vLLM #57273** provides new Qwen QSA component tuning evidence, but its BF16 end-to-end serving numbers remain inside roughly 1–3% drift. This is a useful negative reminder that selector microbench wins do not automatically move model throughput.

---

## Direct active-hardware evidence — DS4 #1068: M1 Max 64GB Qwen3.8 Flash Next

PR created: `2026-09-17 06:16:53 UTC`.

Machine and route:
- MacBookPro18,2, Apple M1 Max, 64 GB;
- Metal backend, DS4 built at `8db1d1d`;
- `qwen38-q2`;
- model 137.10 GiB on disk, **41.72 GiB resident**, n-grams disk-only.

Committed sweep:

| context | prefill tok/s | steady generation tok/s |
| ---: | ---: | ---: |
| 2,048 | 288.41 | 24.15 |
| 4,096 | 274.97 | 24.41 |
| 8,192 | 274.78 | 24.45 |
| 12,288 | 275.57 | 24.46 |
| 16,384 | 273.95 | 24.26 |

A second identical run reportedly agreed within about 1% at every frontier.

The most useful 64GB detail is not merely the rate; it is the memory route. Default `--prefill-chunk 8192` planned 49.74 GiB (`7.49 GiB buffers + 41.72 GiB resident model`) and pushed the machine into swap, with first-generation latency rising to 280–460 ms and TG scattering from 20.70 to 24.72. `--prefill-chunk 2048` planned 44.36 GiB, stayed resident and restored stable decode. Chunk 1024 worked but cost about 10% prefill versus 2048.

Ordinary inference beyond the benchmark harness:
- real 32,113-token prompt: **271.94 tok/s PP / 22.76 tok/s TG**;
- `--ctx 131072`: **loads at 48.44 GiB planned**, but no 128K decode receipt is provided;
- MTP reference: **33.19 tok/s** on highly predictable output and **28.91 tok/s** on prose, at about 3% prefill cost.

### Interpretation for our dual-M1 target

This is the strongest new evidence because the CPU/GPU family and memory size now match one of our actual boxes. It says a single M1 Max is not inherently stuck in an ~18–20 tok/s Flash-Next regime on an aggressively compressed route, and it confirms substantial resident headroom with the right prefill chunk.

It still does **not** certify 40@128K on two M1s. Missing dimensions are exactly the important ones: 128K active decode, preferred ~5.x-BPW/Q6-ish quality lane, PP2 execution, TB4 bytes/round, distributed Lightning MTP and the final MLX kernel stack.

### Promoted rule

**Prefill chunk is admission identity on memory-tight Apple systems.** Qualification must record chunk size, planned memory, settled resident memory, swap pressure and post-prefill TG. A run that enters swap because of an oversized transient is not a clean decode measurement.

---

## Apple Metal scheduling transfer — DS4 #1067

PR created: `2026-09-17 04:54:43 UTC`.

On V4.1 / M3 Ultra 512 the PR reports **17.94 -> 26.07 tok/s (+45%) with identical output**. The major steps were:
- flush groups of layers but wait once at logits rather than repeatedly synchronizing the command queue: roughly 17.7 -> 22.8 tok/s;
- read both Engram tables on worker threads and join before first commit: roughly 23.0 -> 25.8 tok/s;
- allocation-free pipeline lookup: throughput-neutral but encode bookkeeping fell 4.0 -> 0.7 ms/token;
- small aligned copies moved from blit to compute: throughput-neutral, zero blit passes/token;
- same queue treatment for batched graph step: **239 -> 187 ms/step at 8 sessions**.

The path is gated to pre-M5 Apple silicon, which makes it directly interesting for our M1-class scheduling design. It does not establish Flash-Next throughput because model/runtime/topology differ.

Promoted rule: separate **encode/submit overhead**, **command-buffer commit frequency**, **GPU completion waits** and **host I/O joins**. A Metal optimization can be mostly synchronization removal rather than arithmetic reduction.

---

## Speculative row identity — llama.cpp #29019

PR created: `2026-09-17 09:34:15 UTC`.

Concurrent batch splitting can reorder tokens. Separate KV streams preserved cache identity, but DFlash auxiliary hidden-state rows still arrived in the reordered layout while the drafter interpreted them in original request/token order.

SPEED-Bench, Qwen3.8-27B target + DFlash2 drafter, both Q4_K_M, concurrency 16:
- mean acceptance length **3.3531 -> 3.9211 (+16.94%)**;
- coding +16.15%; math +16.94%; multilingual +18.46%; RAG +20.17%; summarization +27.24%; every reported category improved.

This is unusually clean evidence that a low-acceptance speculative path can be an **identity-routing bug**, not a weak drafter.

Promoted rule: every auxiliary tensor used by speculation needs explicit `(request, token-original-position)` provenance through split/reorder/merge. KV ownership alone is insufficient proof that hidden states, logits or draft inputs are aligned.

---

## Cache restore segmentation is numerical identity — mlx-serve `a7e22dcb`

Commit author timestamp: `2026-09-17 01:35:40 UTC`; committer timestamp `03:37:01 UTC`.

On Flash Next, an always-on SSM snapshot left a 31-token tail. Warm restore split the tail 30+1 while the cold route forwarded all 31 together. The different BF16 kernel tilings changed logits enough to flip a near-tied greedy token. The fix forwards a restored tail inside the backoff window as the cold run's single span; the project reports warm == cold logprobs exactly afterward.

Promoted rule: cache equivalence must include **replay segmentation / row geometry**, not only token IDs and restored state. For exact greedy certification compare cold vs warm logits and tokens under identical forward partitioning wherever practical.

This also explains why a semantically correct cache reconstruction can still fail a strict deterministic ruler.

---

## Unequal draft widths under grouped sampling — mlx-serve `4e9bdf79`

Source timestamp: `2026-09-17 04:27:24 UTC`.

Dense Qwen3.8-27B grouped MTP right-pads verify rows to the group's widest draft. A shorter sampled request then reshaped the entire padded block using only its local `m`, producing the `Cannot reshape array of size N` failure and taking down every sampled request in the group.

The fix slices the live `1+m` positions before reshape/filtering and treats a short verify block as an explicit error. Greedy escaped because it did not use the sampled accept graph; a fallback correction path also escaped because it already sliced per position.

Promoted rule: **physical group width != live row width**. Every verifier/acceptance kernel must consume an explicitly bounded live span and must not infer its input geometry from the local accepted/draft count when the producer emitted group-padded storage.

---

## oMLX #3702 follow-through — failed handoffs and contaminated cost learning

Fresh commits:
- `0c7796622f334578d32b8ccf3596d0d17ee8b005` — `2026-09-16 23:47:17 UTC`;
- `64204dbee77b26b6b3788a3778c48e981dd67066` — `2026-09-17 02:13:30 UTC`.

The first closes an unsafe fallback: if MTP-to-standard reconciliation or one-token frontier handoff mutates cache and then fails, decoding no longer simply drops MTP state and continues. It retries by rebuilding committed history; if that cannot be proven safe, it raises and stops. The emitted token is recorded before a handoff that may need history reconstruction.

The second excludes scheduler intervals interrupted by prefill from MTP-vs-standard batch cost learning. Prefill may consume wall time and pending decode work, so treating that interval as a normal decode sample biases the adaptive speculative policy.

Promoted rules:
- a failed speculative handoff after state mutation must **recover a committed frontier or fail closed**;
- adaptive speculation telemetry has an execution-class identity: prefill-interrupted, warmup, depth-transition and ordinary steady cycles are not interchangeable samples.

---

## Physical memory/admission rules — vLLM #57261, #57270, #57262

### #57261 — speculative scratch belongs to running concurrency

GLM5.3 Flash TP4 MTP3 used 45 blocks per resident request, 9 of them speculative scratch. The old formula multiplied scratch by theoretical KV-cache concurrency even though scratch exists only for running requests. Reserving scratch once for `max_num_seqs` increased reported GPU KV capacity **635,699 -> 729,088 tokens (+14.7%)** on the test system, with unchanged GSM8K and no meaningful TTFT/decode change.

Rule: ephemeral speculation scratch is billed by the maximum simultaneous active users of that scratch, not by all theoretical resident KV slots.

### #57270 — a dummy profile must exercise reachable dynamic allocation

Padding-only profile tokens could be skipped by MoE routing, so profiling omitted expert workspace and later runtime/warmup could OOM. The patched route intentionally sends dummy profile tokens through expert work. One simple Qwen3-30B setup exposed about 0.9 GiB/rank of previously missed workspace; larger EP topology could miss several GiB.

Rule: profile/warmup correctness requires **reachable work**, not syntactically valid but inert inputs.

### #57262 — distributed receive workspace needs an explicit skew bound

Expert-parallel receive size depends on routing skew; whatever route a profile happens to sample is not a worst-case proof. The new design allows a configurable bound over reachable receive tokens and frees warmup scratch before graph capture.

Rule: distributed admission needs `reachable worst-case fan-in`, not average/profile-observed fan-in.

---

## Recurrent-state address and arithmetic identity — vLLM #57317, #57260, #57280, #57329

### #57317 — fixed tail/ring state needs its own addressing contract

A GLM-5.3-Flash Kpool fixed per-request tail buffer inherited a generic slot-mapping path that treated positions as unbounded cache addresses. It survived shorter prompts and failed at about 500K. The correct mapping is ring-local (`position % kpool`).

Rule: cache inheritance/classification does not prove address semantics. Ring/tail/recurrent side buffers declare their physical address transform explicitly and get long-context wraparound tests.

### #57260 — parallelism ownership is per cache group

Global context-parallel slot localization was applied to replicated Mamba/GDN/sliding/Kpool groups. In the reported CP=4 example, 48/64 tokens became PAD and the remaining mapping was wrong. The fix derives localization eligibility from each cache spec.

Rule: distributed ownership/addressing is **per state group**, not implied by the process-wide parallel mode. Attention can be sharded while recurrent/tail state remains replicated.

### #57280 — batch invariance includes tiling

A GDN occupancy heuristic chose different row tilings for ordinary decode and speculative verification, changing reduction order/inverse-std. Batch-invariant mode now forces one-row-per-program; the synthetic validation moved differing elements/invstd from 4/1044 to 0/0.

Rule: exact batch invariance constrains launch/tiling/reduction topology, not merely the written mathematical expression.

### #57329 — checkpoint export need not split the whole forward

Instead of ending a model forward at every cacheable recurrent boundary, one full prompt forward can export intermediate recurrent state from the scan at the logical checkpoint location. On the reported Nemotron setup TTFT improved approximately 13–18% at C1/C4/C16 while prompt throughput barely moved.

Rule: checkpoint granularity and model-forward granularity are separate knobs when the recurrent primitive can expose intermediate state safely.

---

## Kernel/component evidence — useful, not target-moving

### vLLM #57318 — narrow GDN projection

For Qwen3.8-27B on RTX 5090, GDN `in_proj_ba` has geometry `[tokens,5120] x [5120,96]` BF16. At speculative M=2–4, cuBLAS was a poor fit. A bounded FlashInfer split-K route reports **27.2 -> 3.40 us/call**, total 112.4 -> 14.0 ms over the run, and end-to-end decode **1494.3 -> 1397.7 ms (-6.5%)**.

The important transfer is shape-specific routing: only choose the special kernel inside its measured narrow-N/small-M crossover; decline for incompatible quant/bias/LoRA/batch-invariant modes. Dynamic shape selection must also stay runtime-sensitive under compilation rather than freezing the trace-time geometry.

### vLLM #57273 — QSA tuning table

Fresh Qwen QSA SM90 configuration tuning substantially improves several sparse-selector microbench cells, especially FP8 larger row counts, but BF16 serving results remain inside approximately 1–3% run-to-run drift. This does not support moving any whole-model target.

Rule: preserve component receipts, then rerun whole-model decode after the bottleneck shifts. Do not add component percentages.

### vLLM #57343 — transfer crossover follows submitted fragment geometry

A KV-offload path selected DMA from logical page size even though each actual submitted fragment was smaller. Switching based on fragment size reduced the reported host submission/copy path dramatically while preserving bytes exactly.

Transfer to TB4 work: transport backend/copy strategy is chosen from the **actual physical fragment submitted**, not the logical object/page that contains it.

---

## Non-promotions and boundary discipline

- **vLLM #57351** is relevant to Qwen3.8-Flash-Next NVFP4 TP padding, but was created at `10:33:33 UTC`, 23 seconds after this watch cutoff. It is deliberately left for the next pass.
- vLLM #55867 merged in this window but its underlying PR/evidence predates the window; merge time does not make it fresh.
- oMLX #3703 merged after the previous boundary but the PR itself was already captured in the prior watch; no duplicate promotion.
- QSA, GDN, sparse-MLA and offload numbers from NVIDIA/AMD remain mechanism/transfer evidence unless they reproduce on the active Apple topology.
- DS4 #1067 is pre-M5 Apple scheduling evidence, but V4.1 on M3 Ultra is not Qwen3.8 Flash Next on M1 Max.
- DS4 #1068 is exact M1 Max hardware evidence, but Q2 short/32K and `ctx=131072 loads` are not a 128K quality-lane TG receipt.
- No new result measures dual M1 Max/TB4 PP2 + distributed Lightning MTP at ~128K active context.

## New rules to carry into implementation/certification

1. **Prefill chunk is memory-admission identity**: record planned/settled memory, swap and post-prefill TG.
2. **Replay segmentation is numerical identity** when BF16 tiling/reduction changes; cold/warm state equality alone is insufficient.
3. Preserve `(request, original-token-row)` identity for every speculative auxiliary tensor across batch split/reorder/merge.
4. Distinguish group-padded physical verifier width from a row's live `1+m` span.
5. Failed speculative handoff after mutation must restore a committed frontier or fail closed.
6. Adaptive cost models must reject prefill-interrupted/warmup/transition samples from steady decode economics.
7. Bill speculative scratch by active concurrency, not theoretical cache residency.
8. Profile inputs must exercise reachable dynamic work; route-skew workspace gets an explicit worst-case bound.
9. Parallel addressing/ownership is per cache/state group; process-wide CP/PP mode is not sufficient.
10. Ring/tail buffers own their slot transform and require long-context wraparound tests.
11. Batch-invariant arithmetic includes launch tiling and reduction topology.
12. Separate recurrent checkpoint-export boundaries from whole-model forward boundaries where the backend permits.
13. Select copy/transport paths using actual submitted fragment geometry.
14. Keep component microbench wins separate from model-level target evidence.

## Target status

**UNCHANGED.**

The new M1 Max receipt makes the 40 tok/s @ ~128K dual-M1 goal more credible as an engineering objective, but not enough to change its numerical target or stretch bands. The cleanest next evidence remains an exact-quality-lane single-M1 long-context ruler followed by PP2/TB4 receipts with stage timing, bytes/round, memory residency and distributed-MTP acceptance.

## New hard source-freshness boundary

`2026-09-17 10:33:10 UTC`
