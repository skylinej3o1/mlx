# Runtime Research Watch — 2026-09-02 13:50 ET

Scope: fresh external delta after `RESEARCH-WATCH-2026-09-02-0945.md`, following the canonical-state-first protocol. Targets remain Qwen3.8-Flash-Next, Qwen3.8-27B exact/verifier work, DeepSeek-V4/DS4 distributed serving, and especially the planned 2x M1 Max 64 GB / TB4 Hermes agent system.

This pass does **not** change the certified exact-Q8 verifier checkpoint. P69B12 remains frozen/promoted and **P69B13 remains next using existing profiling only**.

## Executive delta

1. **RECOVERED OLDER EVIDENCE + FRESH UPDATE — oMLX #3330 exact-resident/prompt-tail cache is highly relevant to Hermes.** The PR predates this pass and therefore is not classified as new. Physical M3 Ultra / Flash-Next Fusion integration reports an 18,174-token rewritten transcript dropping from 4.17 s visible TTFT to 0.62 s with exact output parity, ordinary matching terminals around 0.47 s, and structured tool follow-up around 0.51 s. A fresh 2026-09-02 update also fixes Qwen3.8-27B Lightning-MTP exact-terminal ownership: MTP-on TTFT fell from 4.831 s before the fix to 0.197 s after, versus 0.208 s with MTP off.
2. **RECOVERED OLDER EVIDENCE — oMLX #3328 provides a direct ~100K warm-prefix Flash-Next receipt.** On M3 Ultra, 98,304 prompt tokens were restored from target prefix cache, only 1,689 exact suffix tokens were primed into the MTP head, draft acceptance was 98.3%, committed work 5.38 tokens/target-cycle, and 500-token decode ran at 65.25 tok/s with the exact target output hash. This existed before the current pass and was missed by the formal watch chain; record it as recovered, not new.
3. **NEW — oMLX #3382 measures Flash-Next MTP verify economics.** M3 Ultra / oQ4e reports a ~2.3x verify-forward multiplier at B1/depth-5, decomposed approximately as base 1.0x + GDN sequential recurrence 0.5x + MoE expert-union work 0.6x + QSA indexer 0.2x. Measured workload acceptance translates to roughly 2.4 tok/cycle prose (~1.04x net vs the 2.3x verify wall) and 3.1 tok/cycle tool-call workloads (~1.35x net). Proposed expert-union dedup and TreeWY/chunked-scan gains are **estimates**, not measurements.
4. **CORRECTION / UPDATE — #28213 follow-up retracts the claim that QSA top-k selection is the demonstrated next long-context bottleneck.** On one unusual 8-GPU system, reducing top-k input width and gathered attention width did not improve ~60K decode. The only additional measured win was merged llama.cpp #28040, changing `get_prev_tokens` cache lookup from O(N) to O(log n): 19.6 -> 21.6 tok/s in that system (+10%). #28040's own RTX PRO 6000 measurements were 74.5 -> 77.6 tok/s @55K and 52.0 -> 56.7 @132K. Keep QSA/indexer acceleration as a valid seam, but do not call it the proven dominant residual bottleneck.
5. **NEW MEMORY CAUTION — llama.cpp QSA dense-mask transient can dwarf simple KV arithmetic.** A #27941 follow-up identifies about **9 GB** reserved for the QSA mask at 128K context with 4K ubatch prompt processing; later graph reallocation was ~7 GB smaller in the reported testcase. This is llama.cpp-specific and does not transfer to oMLX's gathered-QSA path, but it means the Hermes memory budget must include runtime/transient/indexer/cache-snapshot allocations rather than only K/V tensor geometry.
6. **UPDATE — DS4 #861 now validates four concurrent sessions but aggregate remains flat.** Four clients on `--batched-session 4` all matched the serial baseline bit-for-bit, with aggregate ~13.2 tok/s and clean queuing of a fifth client. The current step batches shared span transport plus QKV/shared-FFN, while attention and routed-MoE remain per-session. A proposed 1.5-1.8x ceiling from wider row batching is an estimate, not a result.
7. **UPDATE — DS4 #621 AProjQ4 remains a strong lossy/capacity track, but its CUDA prefill advantage was requalified.** Metal currently shows ~15.5% median decode advantage across 32/32 frontiers and ~2.14 GiB footprint saving. A new order-balanced GB10 long-context series supersedes earlier fixed-order prefill claims: Q4 is +0.33% at 8K and about -0.22% to -0.34% at 16K-64K versus Q8, effectively parity at depth. This does not affect exact-Q8 P69.
8. **NO CHANGE — exact dual-M1 receipts.** llama.cpp #27993 has no new comments; DS4 #922 has no new comments. There is still no sustained 2x M1 Max Flash-Next TG measurement and no sustained dual-M1 0731 TG measurement.
9. **NO CHANGE — Layr exact frontier and mlx-dspark.** Layr still shows #1481 as the newest submission and best score `3.7291100105909`; #1481 was cancelled by its submitter. `ARahim3/mlx-dspark` still has no code push after 2026-09-01 10:54 UTC.

Net: **do not move the B1 or B2-B4 dual-M1 forecast bands.** The strongest positive change is confidence in the *software shape* needed by Hermes: exact-resident cache ownership, suffix-local MTP reconstruction, and prompt-tail keepwarm are now backed by physical Flash-Next measurements. The strongest caution is memory accounting: do not derive 3-4-agent context limits from raw Q8 K/V bytes alone.

## RECOVERED / UPDATE — oMLX #3330 exact-resident agent-turn cache

Source: https://github.com/jundot/omlx/pull/3330

This PR predates the 09:45 pass, so its older body evidence is classified **RECOVERED OLDER EVIDENCE**, not new. Fresh comments after the pass provide an additional Qwen3.8-27B MTP-terminal fix.

The architecture has three opt-in layers:

- asynchronous Metal readiness after idle periods;
- bounded `ExactResident` L0 ownership transfer for validated live prefixes;
- cancellable idle prompt-tail materialization that reconstructs only a bounded uncached suffix and atomically publishes an exact fallback.

The motivating agent/tool problem is important: clients frequently re-render prior assistant/tool transcripts differently from the raw token terminal. A terminal cache can therefore miss even when the preceding input prompt remains an exact prefix. The implementation retains multiple exact candidates under one byte ceiling and selects the longest exact match.

### Physical Flash-Next Fusion evidence — M3 Ultra 256 GB

Qwen3.8-Flash-Next oQ4e MTP:

- 18,174-token transcript-divergence control: 16,384 cached, 3.80 s model / 4.17 s visible TTFT;
- same turn with the integrated cache path: 18,152 cached, 0.23 s model / **0.62 s visible TTFT**;
- visible TTFT improvement: **6.7x**;
- ordinary matching terminal: ~0.47 s visible TTFT;
- structured tool follow-up: 18,445 / 18,487 cached, **0.51 s total**, valid tool-call/result flow;
- cold 9,994 uncached tokens: 907.7 tok/s prefill;
- 500-token cold decode: 74.36 tok/s with 98.2% MTP acceptance;
- a low-acceptance case parked/retried after 128 native tokens and recovered to 95.7% acceptance, finishing at 50.11 tok/s with the identical output SHA;
- B2/B4/B6 smoke completed with unique exact markers and zero errors;
- idle resident-L0 soak reported 1.60 GB resident L0 with flat RSS and unchanged SSD manifest.

Important qualification: the speculative-Qwen rows use a separate Fusion target-terminal/cached-suffix transaction. Standalone #3330 is still designed to fail closed for unsupported speculative Qwen until dependencies land. Treat these as physical integration evidence, not merged-main behavior.

### Fresh Qwen3.8-27B MTP exact-terminal update

Source: https://github.com/jundot/omlx/pull/3330#issuecomment-5512383106

Physical M3 Ultra / Qwen3.8-27B-4bit / MTP depth 5:

| Path | Exact prefix / suffix | TTFT |
|---|---:|---:|
| MTP off | 1,243 / 1 | 0.208 s |
| MTP on before fix | 1,243 / 1 | 4.831 s |
| MTP on after fix | 1,244 / 1 | **0.197 s** |

The fast path is admitted only when every readable target cache has one uniform offset equal to the visible token ledger and rollback/draft/undo state is empty. The author reports no change to logits, sampling, verification, accepted tokens, or output bytes. The branch was then rebased onto upstream main and reported 541/541 focused post-merge tests passing.

### Implication for Hermes

This is strong evidence for the software policy already preferred for the planned local agent system:

- keep logical agents/session histories persistent;
- transfer exact live cache ownership instead of serializing/reconstructing when possible;
- retain durable SSD/paged fallback boundaries;
- rebuild only the suffix that actually changed;
- let new user/agent work cancel hidden keepwarm work immediately;
- fail closed when speculative/recurrent state cannot be proven exact.

This improves confidence in **warm-agent latency**, not in dual-M1 raw TG.

## RECOVERED — oMLX #3328 ~100K cached-prefix MTP reconstruction

Source: https://github.com/jundot/omlx/pull/3328

This PR also predates the pass and should have been carried into the formal research chain earlier.

Physical Apple M3 Ultra / Qwen3.8-Flash-Next-oQ4e-MTP, deterministic ~100K restart restore:

- **98,304 prompt tokens** restored from target prefix cache;
- **1,689 exact local suffix tokens** primed into the MTP drafter;
- draft acceptance: **98.3%**;
- **5.38 tokens/target cycle**;
- decode: **65.25 tok/s** for 500 generated tokens;
- exact output hash matched the unmodified target result;
- cold 99,993-token control: 867.11 tok/s prefill and no accidental priming tax.

This is the cleanest physical evidence currently in the watch chain that a very long Flash-Next agent history can be restored without replaying the entire reusable prefix into the MTP head.

It does **not** establish the memory cost on M1 Max or the final 2x-M1 cache-sharing mechanism.

## NEW — oMLX #3382 Flash-Next verify-cost decomposition

Source: https://github.com/jundot/omlx/issues/3382
Supporting write-up: https://github.com/moc375/qwen4-speculative-decoding

Environment in the write-up: M3 Ultra 512 GB, oMLX 0.6.4, Qwen3.8-Flash-Next oQ4e.

Measured B1/depth-5 verify-forward multiplier:

```text
base forward             1.0x
GDN sequential recurrence ~0.5x
MoE expert union          ~0.6x
QSA indexer               ~0.2x
--------------------------------
total verify              ~2.3x
```

The author reports current workload-level speculative economics of:

- prose acceptance ~2.4 tok/cycle -> ~**1.04x** effective relative to a 2.3x verify wall;
- tool-call acceptance ~3.1 tok/cycle -> ~**1.35x** effective;
- temp>0 acceptance currently near zero in the separate #3370 report.

The important measured result is the **2.3x cost decomposition and workload-dependent acceptance**. The proposed future improvements are analytical/engineering estimates:

- MoE expert-union dedup: author estimates verify ~2.0x;
- TreeWY/chunked-scan GDN verification: author estimates combined verify ~1.5x;
- prose at 1.5x would mathematically be ~1.6x, but this is **not measured hardware performance**.

### Implication

This strengthens the case for **dynamic speculation policy** in Hermes:

- deterministic/tool-call/code continuation can be favorable;
- ordinary prose may sit near break-even depending acceptance;
- concurrent traffic should not blindly force MTP;
- temp>0 remains an explicit qualification gate;
- the server/gateway should select MTP lane policy from measured economics rather than model capability alone.

This also gives a portable future-kernel lead for the 27B verifier project: GDN multi-position recurrence and expert-union reuse are structurally important. However, this is cross-model/runtime evidence and **does not supersede P69B13 selection from the existing exact local P69 measurements**.

## CORRECTION / UPDATE — #28213 residual bottleneck is not settled

Sources:
- https://github.com/ggml-org/llama.cpp/pull/28213
- https://github.com/ggml-org/llama.cpp/pull/28040

The 09:45 note said the independent #28213 tester identified full-context QSA top-k/indexer selection as the next context-scaling bottleneck. That interpretation is now too strong.

The same tester performed follow-up A/B work on the unusual 8-GPU PCIe-Gen1 host at ~60K context:

- no selected-K/V gather: 15.5 tok/s;
- gather: 19.6 tok/s;
- gather + merged #28040: **21.6 tok/s**;
- ~2K baseline: ~40 tok/s.

The tester then reduced the top-k input to a width-sized trim and separately shrank gathered-attention width from 2304 to 256. Neither moved the ~60K result. CPU profiling showed no host hotspot and the process waiting around CUDA event handling, so some other GPU work still scales with depth on this configuration.

Merged #28040 changes `get_prev_tokens` from scanning used KV cells O(N) to indexed O(log n). Its own RTX PRO 6000 measurements:

- 55K: **74.5 -> 77.6 tok/s**;
- 132K: **52.0 -> 56.7 tok/s**;
- fixed-seed multi-sequence greedy output byte-identical.

### Revised interpretation

- selected-K/V gather remains strongly supported;
- QSA/indexer top-k optimization remains a plausible seam;
- **do not call top-k the proven dominant next bottleneck**;
- per-token cache bookkeeping / sequence-position lookup is a demonstrated context-scaling seam in llama.cpp;
- Metal/oMLX must be profiled independently rather than importing the CUDA residual-bottleneck ordering.

## NEW MEMORY CAUTION — dense QSA mask/transient reserve

Source: https://github.com/ggml-org/llama.cpp/pull/27941#issuecomment-5512601466

A llama.cpp contributor traced a memory swing on Flash-Next to the QSA mask compute buffer:

- ~**9 GB** reserved for the QSA mask at 128K context with 4K ubatch prompt processing in the reported setup;
- later prompt/decode graph reallocation was around **7 GB smaller** because allocation reflected current KV usage;
- a deeper later prefill could require the larger allocation again.

This is **not an oMLX/M1 memory measurement**. llama.cpp's dense-mask implementation is precisely the kind of shape that gathered-QSA work avoids; oMLX #3351 separately demonstrated much lower gathered-QSA memory pricing than a dense equivalent at long context.

Nevertheless, this corrects an overly simple capacity inference from raw Q8 K/V geometry alone. For the future Hermes server, per-agent context budgeting must include:

- QSA K/V tensors;
- indexer/raw-key/position state;
- GDN/recurrent state;
- speculative rollback/checkpoint state;
- paged/exact-resident cache copies;
- gathered/dense transient workspaces;
- batch-join and prompt-processing peak allocations.

Therefore **4 agents x 128K advertised context remains a design target, not a proven comfortable resident-memory configuration on 2x M1 Max**. Measure real peak residency before fixing the default limit.

## UPDATE — DS4 #861 four-client partial row batching

Source: https://github.com/antirez/ds4/pull/861#issuecomment-5511669070

Known hardware/model context remains the DS4 distributed Strix-Halo work, not M1 Max.

Fresh validation on `a93cdd9`:

- 4 clients with `--batched-session 4`, temp 0, 48 generated tokens each;
- all completions bit-identical to serial baseline and one another;
- 42 batch spans at B4, then B3/B2 tail spans;
- total batch wall: 14.1-14.9 s;
- aggregate: **~13.2 tok/s**;
- 5 clients on a 4-slot server: fifth queued cleanly; all five completed with no errors/crashes.

Aggregate remained essentially flat from B2 through B4 because the current implementation batches shared span transport plus QKV/shared-FFN while attention and routed MoE remain per-session.

The contributor estimates a future 1.5-1.8x ceiling after routed-MoE row batching, batched attention with per-row KV planes, and shared-down batching. **That ceiling is an estimate, not measured throughput.**

### Implication for our multi-agent forecast

This is a caution against assuming that merely exposing multiple sessions automatically creates aggregate scaling. The runtime must batch the expensive row-wise regions, not only shared transport/projections. It does not directly lower the oMLX/PP2 forecast because the hardware/runtime topology differs, but it reinforces the need to record stage idle %, row-batching coverage, and actual aggregate wall throughput on the M1 pair.

## UPDATE — DS4 #621 AProjQ4 requalification

Source: https://github.com/antirez/ds4/pull/621

Still a **lossy/mixed-quant future track**, not exact-Q8 P69 evidence.

Current consolidated Metal evidence:

- footprint: 80.76 -> 78.62 GiB, saving **2.14 GiB**;
- M5 Max steady 2K decode: 45.69 -> 53.35 tok/s (+16.8%);
- 32-frontier 2K-65K sweep: Q4 wins 32/32;
- paired median decode advantage: **+15.5%**;
- strongest published resident Metal prefill comparison is effectively tied.

Fresh GB10 order-balanced long-context prefill series corrects earlier fixed-order claims:

- 8K: +0.33% Q4 vs Q8;
- 16K: -0.34%;
- 32K: -0.22%;
- 65K: -0.29%.

The tester found a ~0.4-0.5 percentage-point positional/order bias that exceeded several effects under study. The earlier +2.39% 8K prefill comparison used a different prompt/benchmark shape and should not be treated as the long-context steady-state result.

Durable lesson: AProjQ4's **decode and capacity advantage is real on the measured platforms; prefill should be described as near-parity and benchmark-order sensitive** until final-head matched certification.

## External no-change checks

### Exact dual-M1 Flash-Next — llama.cpp #27993

No comments after the 09:45 pass. Still no sustained TG measurement and no posted 115K/256K correctness completion.

### Exact dual-M1 0731 — DS4 #922

No comments after the 09:45 pass. Still no generated-token count or sustained TG.

### Layr Qwen3.8-27B exact challenge

Direct GitHub check:

- total PRs: 1480;
- #1481 remains newest;
- #1481 validation was cancelled by the submitter;
- current best remains `3.7291100105909`;
- no submission created after the current pass boundary.

### mlx-dspark / DFlash2

Repository metadata still reports last code push `2026-09-01T10:54:45Z`; no fresh issue activity in this pass window.

## Forecast consequence

### Mature dual-M1 Flash-Next B1 — short/medium context

**Unchanged:**

| Target | Confidence |
|---|---:|
| >=30 tok/s | ~90% |
| >=35 tok/s | ~75-80% |
| >=40 tok/s | ~55-60% |
| >=45 tok/s | ~30-35% |
| >=50 tok/s | ~15% |

### ~128K active-context B1

**Unchanged:**

| Target | Confidence |
|---|---:|
| >=20 tok/s | ~85% |
| >=25 tok/s | ~65% |
| >=30 tok/s | ~40% |
| >=35 tok/s | ~20% |

### Mature B2-B4 aggregate

**Unchanged:**

| Aggregate target | Confidence |
|---|---:|
| >=50 tok/s | ~85% |
| >=60 tok/s | ~70-75% |
| >=70 tok/s | ~50-55% |
| >=80 tok/s | ~30-35% |
| >=90 tok/s | ~15% |

No exact M1-Max Flash-Next B2/B4 receipt or dual-M1 TG appeared, so a probability move would be unjustified.

## Hermes design consequence

The desired mature system target remains:

- 3-4 logical persistent agents;
- 2-3 active compute slots chosen dynamically;
- strong exact prefix/cache ownership and suffix-only reconstruction;
- ~400+ tok/s mature cold prefill target;
- PP2 primary / TP2 falsification control;
- resident hot execution path first, selective SSD backing second;
- dynamic MTP enablement by workload/acceptance/economics.

But revise the context-capacity wording:

> **128K advertised per agent is still a reasonable product/API target; 4 x 128K simultaneously hot/resident on 2x M1 Max is not yet proven.**

The eventual memory qualification must measure actual B1/B2/B4 cache residency and peak prompt-processing/transient memory at 32K/64K/96K/128K per live session before choosing the default Hermes context cap.

## P69 exact-verifier consequence

None. External Flash-Next/DS4 evidence may suggest future seams, but P69B13 remains selected only from the already-measured local high-leverage GDN/projection/downstream-tail structure. Do not reopen closed P69 experiments or rerun P69B7 profiling.
