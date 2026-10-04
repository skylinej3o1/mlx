# Project 51 research watch — 2026-10-04 08:27 ET

Freshness boundary entering: **2026-10-04 11:00:23 UTC**
Cutoff: **2026-10-04 12:27:27 UTC**

## Decision

One narrow planning prior moves:

- **Strata IQ3_S/native262K physical-fit prior on the 16-GB-GPU / 64-GB-host memory class: ~95% -> ~97%.**

Everything else stays put:
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**;
- automatic containment: **~85%**;
- dual-M1 production target: **IQ3_S/native262144/>=35 TG/>=400 cold PP**;
- dual-M1 performance target: **~128K/>=40 TG/>=425 cold PP**;
- native262K stretch: **>=40 TG**.

The strict hard boundary advances to **2026-10-04 12:27:27 UTC**.

## NEW — Strata #755: gfx1100 ROCm-nightly hipBLASLt table becomes an engine-tree artifact

PR:
https://github.com/Niko1221/Strata/pull/755

Created **2026-10-04 11:17:16 UTC**, open.

This is the engine-tree companion to the already-known #745 benchmark:
- RX7900XTX / gfx1100;
- ROCm nightly hipBLASLt 1.5.0 / version 100500;
- exact-version tuning table;
- 131071-token IQ3_S prefill reported at **1687 vs 926 tok/s (1.82x)** with the table vs plain hipBLAS;
- decode unchanged.

Classification: **NEW implementation artifact; underlying benchmark mechanism was KNOWN from the previous pass.**

Project-51 impact:
- RX6800 qualification must record exact ROCm + hipBLASLt version and whether a matching gfx1030 table is active;
- no numeric transfer from gfx1100 to gfx1030.

## NEW — Strata #757: exact 16-GB GPU / 64-GB host IQ3_S native262K fit receipt

PR:
https://github.com/Niko1221/Strata/pull/757

Created **2026-10-04 11:30:42 UTC**, open/results-only.

Hardware / runtime:
- RTX 4090 Laptop GPU, **16 GB**;
- host **64 GB / 61.28 GiB usable**;
- Linux;
- Strata 0.1.38 lineage;
- original DASLab **IQ3_S**;
- INT8 KV;
- context caps 131072 and **262144**.

At the 262144 cap:
- 250000-token prompt: **2116 PP / 40.3 TG**;
- 128000-token prompt: **2292 PP / 39.7 TG**;
- 15/15 recall needles across the tested ladder;
- VRAM peak ~15.7/16.0 GB;
- MemAvailable never below **6.17 GiB**;
- swap did not grow.

Important configuration result:
- with KV streaming off, the 262K cap shrank the expert cache from 3865 to 2856 slots;
- decode was ~13-17% lower than the 131K-cap arm even at shorter prompt lengths;
- prompt throughput stayed within ~4%.

Project-51 decision:
- this is the strongest same-memory-class exact IQ3_S/native262K capacity receipt now in the record;
- raise **physical fit ~95% -> ~97%**;
- do **not** raise Windows admission because this is Linux and Windows commit/page-lock behavior remains separately risky;
- do **not** transfer the 4090-Laptop TG/PP numbers to the 5070 Ti;
- retain streamed INT8 KV (~32K resident first) on the 16-GB 5070-Ti production baseline specifically to avoid sacrificing expert-cache residency to a fully resident long KV allocation.

## NEW — Strata #758: MI50 experimental receipt

PR:
https://github.com/Niko1221/Strata/pull/758

Created **2026-10-04 11:49:39 UTC**.

MI50 32 GB / gfx906 / 64-GB host / IQ2_XS:
- ~330 PP at 4K/24K;
- ~35-36 TG;
- 6/6 recall;
- ~8.1 GiB swap peak.

Classification: **NEW**, but outside Project-51 hardware/quant targets. No planning movement.

## NEW — Strata #759: native Responses API reaches real Codex + subagent workflow

PR:
https://github.com/Niko1221/Strata/pull/759

Created **2026-10-04 11:51:24 UTC**, open.

Adds POST /v1/responses with:
- streaming/non-streaming text;
- reasoning effort;
- function/custom tools and namespaces;
- full-history tool-call/result replay;
- auth/cancellation/monitoring integration.

Reported real validation:
- Windows + Codex CLI 0.160.0 + Qwen3.8 Flash-Next;
- a streaming exec_command round trip completed;
- initial prompt contained **92,672 tokens** from tools/skills;
- a separate coding profile completed native **spawn_agent / wait_agent / close_agent** with the child returning the expected marker.

Project-51 impact:
- Responses/Codex becomes a high-priority Strata qualification lane once the PR is merged/rebased into the selected production build;
- add the user's long tools/skills prefix and subagent workflow to the agent test suite;
- no quality credit merely because the protocol works.

## NEW — Strata #760: 524K Blackwell field data exposes 16-GB staging/residency coupling

Issue:
https://github.com/Niko1221/Strata/issues/760

Created **2026-10-04 11:52:59 UTC**.

On 4x 5060 Ti 16 GB at 524K YaRN:
- the histogram QSA fallback works end-to-end;
- long context consumes enough KV VRAM to collapse main-card expert residency;
- large 24576 prefill staging can then fail admission;
- 4096 chunks boot;
- the reported chunk clamp costs ~18% PP in a controlled arm.

Project-51 impact:
- no move beyond native262K;
- reinforces that max-context configuration, KV residency and prefill-chunk staging must be qualified jointly on 16-GB cards;
- our 262K streamed-KV baseline is the right first arm.

## NEW — Strata #761: multi-stage prefill pipeline fixes a downstream-wait serialization bug

PR:
https://github.com/Niko1221/Strata/pull/761

Created **2026-10-04 12:05:23 UTC**, open.

4-way mixed 3060/5060 layer split, IQ3_S:
- old pipeline: ~1090 PP;
- new pipeline: **2211-2228 PP (~2.04x)**;
- cards busy three-or-more-at-once: 0% -> 54%;
- stage-0 downstream wait: 6253 -> 131 ms;
- residual dumps byte-identical.

Mechanism:
- each stage keeps a deque of downstream futures;
- reaps one-for-one before the next handoff;
- outer stage joins at completion;
- only one chunk per stage remains in flight because buffers are shared.

Project-51 transfer:
- strong mechanism evidence that pipeline PP can be lost to host-side stage synchronization rather than compute;
- for dual-M1 Flash bring-up, make asynchronous stage handoff / one-in-flight ownership explicit in the balanced-pipeline implementation;
- **no 2.04x numeric transfer to M1/TB4** and no change to the >=400 PP prior.

## NEW — Strata #762/#763: parser recovery helps clients, but synthetic tool intent is disallowed in quality certification

#762:
https://github.com/Niko1221/Strata/pull/762
Created **2026-10-04 12:06:37 UTC**.

It extracts balanced JSON from prose/code fences before validating structured output.

#763:
https://github.com/Niko1221/Strata/pull/763
Created **2026-10-04 12:07:00 UTC**.

It:
- honors required/function-specific tool_choice;
- retries once with an explicit directive;
- if the model still does not call a tool, can **synthesize a minimal valid tool call from the selected schema**;
- allows response_format with tools and validates the final answer.

Project-51 rule:
- parser recovery may be evaluated as a separate server-recovery metric;
- **a server-synthesized tool call must never count as a native model/quant success** in AA/xhigh/agent certification;
- record native model call, recovered JSON, retry, and synthesized action separately;
- production use of synthesized actions requires an explicit application policy, not a hidden benchmark assist.

This is important for comparing DASLab IQ3_S vs Swift: protocol repair must not erase a real model-level difference.

## NEW — Strata #764: delayed adaptive swaps seek determinism without paying every-window synchronization

PR:
https://github.com/Niko1221/Strata/pull/764

Created **2026-10-04 12:12:40 UTC**, open.

Instead of synchronizing every verify window on the immediately previous adaptive expert swaps, swaps become eligible
after a fixed number of windows (STRATA_ADAPT_LAG, default 2), by which time their copies should normally have landed.

Project-51 impact:
- useful exactness/performance design candidate for adaptive expert placement;
- no production credit until independent exact-IQ3_S 16-GB soak and trajectory gates.

## NEW — Splash #295: prefill-only decision scoring becomes a possible eval/routing primitive

PR:
https://github.com/incoai/splash/pull/295

Created **2026-10-04 11:02:59 UTC**, open.

Adds /v1/score and /v1/decisions:
- fixed-label probabilities from one prefill, no generation;
- shared-prefix batching;
- explicit batch-invariance work because alternate K-split order changed logits/expert routing;
- production-fork evidence reports deterministic packed/cold/warm scoring.

Project-51 impact:
- useful future eval/routing/jury primitive;
- also reinforces a standing rule: execution-plan changes can flip near-tie routing even when arithmetic precision is unchanged;
- not part of the production TG target.

## NEW — TensorFold #368: batch SSD n-gram gathers across concurrent requests

Issue:
https://github.com/ashhart/TensorFold/issues/368

Created **2026-10-04 11:46:39 UTC**.

Single DGX Spark / 16 concurrent Flash requests:
- combined SSD n-gram gathers reduce reported decode GPU idle;
- aggregate decode 190.0 -> 212.4 tok/s (+11.7%);
- all 144 paired outputs reportedly matched.

Project-51 impact:
- multi-agent n-gram I/O should batch/coalesce across active agents where possible;
- no single-request M1 TG credit.

## NEW — TensorFold #379/#380: Flash distributed execution expands to four ranks / Volta

#379:
https://github.com/ashhart/TensorFold/pull/379
Created **2026-10-04 12:15:32 UTC**.

#380:
https://github.com/ashhart/TensorFold/pull/380
Created **2026-10-04 12:15:37 UTC**.

#379 adds four-rank Flash machinery but has no standalone >=sm80 four-GPU physical receipt.
#380 physically exercises a stacked four-rank NVFP4 Flash path on 4x V100 32 GB:
- drafted/serial exactness checks;
- reported ~82-100 TG depending prompt in upstream-tool cells;
- ~1.2K PP in the older branch measurements.

Project-51:
- distributed Flash mechanics continue to mature cross-runtime;
- no V100/CUDA numeric transfer to M1/TB4;
- useful implementation patterns only.

## RECOVERED OLDER + IN-WINDOW UPDATE — Strata #390 per-stage weight carve / helper tier

PR:
https://github.com/Niko1221/Strata/pull/390

Originally created **2026-10-01**, updated again **2026-10-04 12:19:02 UTC**.

Do **not** classify its core mechanism as new.

Current PR documents:
- a layer-split stage loads only its own dense/native layer weights rather than the whole model;
- reclaimed VRAM grows stage expert caches;
- leftover per-card VRAM can become a global helper-expert tier;
- on one 4-way IQ3_S rig, expert slots rise 9269 -> 14172 and auto prefill chunk 2048 -> 4096.

Project-51 engineering inference:
- balanced/asymmetric dual-M1 bring-up should price and load stage-owned weights only;
- do not accidentally duplicate the full dense/nonexpert body on both Macs;
- helper-tier ideas are later optimizations, not part of initial correctness bring-up.

No numeric target movement.

## RECOVERED OLDER — oMLX #4240 SSD expert-streaming improvements

PR:
https://github.com/jundot/omlx/pull/4240

Created **2026-10-04 08:24:50 UTC**, before this strict boundary.

Classification: **RECOVERED OLDER**, never NEW.

On an emulated 24-GB Mac with Qwen3.8 Flash oQ4e and only ~10% experts resident:
- prefill 112-130 -> 220-320 tok/s;
- decode +16-25%;
- mechanisms include least-used expert eviction, larger prompt chunks, prompt borrowing of expert-cache memory and next-chunk expert read-ahead.

This reinforces the already-adopted shallow-expert-spill architecture, but does not change its M1 target probabilities.

## RECOVERED OLDER — oMLX #4241 tool-marker parser content loss

Issue:
https://github.com/jundot/omlx/issues/4241

Created **2026-10-04 09:13:51 UTC**, before this strict boundary.

Classification: **RECOVERED OLDER**.

Literal tool markers inside normal prose can open a streaming envelope; if never closed, recoverable text is withheld and
the request fails. This is consistent with the parser gate already added from Strata/oMLX/MTPLX evidence. No new state movement.

## KNOWN / NO CHANGE

- No public **Swift 1.5 Flash-Next GSQ-RCO IQ3_S** release was found by the cutoff.
- Swift Flash IQ3_S remains the highest-priority artifact to build/qualify, not an assumed published artifact.
- DASLab IQ3_S remains the production baseline.
- No paperniuk/ds4 commit newer than the prior strict boundary was found; its latest relevant work remains SAME-DAY/KNOWN.
- No npanj/slipstream commit newer than the prior strict boundary was found.
- Strata release baseline remains **0.1.38**.
- #646 remains excluded from 5070-Ti production credit pending independent sm_120/16-GB IQ3-family retest.
- 5070-Ti first long-context arm remains streamed INT8 KV with ~32K resident cells and fine adaptive prefill chunking.
- RX6800 producer remains exact gfx1030, target-only/speculation-OFF first.
- M1 implementation starts from paperniuk/ds4; do not rebuild the Flash engine from scratch.

