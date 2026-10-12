# Project 51 research watch — 2026-10-12 12:49 ET

Prior hard boundary: **2026-10-12 13:07:45 UTC**.
Cutoff: **2026-10-12 16:49:11 UTC** (user message timestamp).
Scope: fresh upstream PRs, issues, code commits and model artifacts relevant to Project 51, 5070 Ti Swift/Flash, two M1 Max PP2, Relay, Pi and agent orchestration. Sources created strictly after prior boundary are NEW; rebase/merge of older work is an UPDATE, not new measurement.
Model-repository listings examined during this window may recover earlier-existing artifacts; do not attribute their upload time to the crawler.

## Overall decision

**No numeric TG, cold PP, xhigh-quality, fit, 8h/24h stability, or hardware target promotion.** No change to certified P58/P61/P69B3/P69B6/P69B11/P69B12 verifier code, M1 Max architecture, or accepted benchmark outputs. `RESEARCH-TARGETS.md`, `CURRENT.md`, and `RUNTIME-STATE.md` remain unchanged.

Durable qualification update: include expert-slot provenance race, strict request reasoning-budget compatibility, FP32 GDN state/decay correctness, and producer/consumer checkpoint leases. Separate all model/quant/context/hardware cohorts.

## NEW: Strata optional Foresight swaps may serve *wrong expert bytes* (#2134)
Created 2026-10-12 15:59:47 UTC.
https://github.com/Niko1221/Strata/issues/2134

Cause: an asynchronous Foresight RAM->GPU slot fill reads an address that an adaptive `commit_exchanges/commit_copies/commit_flip` moves while the fill is in flight. Slot identity remains expert X while bytes belong to expert Y. Clean Strata 0.1.43/7695859, RTX PRO 6000, Flash IQ3_XXS, `STRATA_FS_SLOTS=4 STRATA_FS_VERIFY=1`, one HumanEval-50 sequence: **19 BAD / 425,973 verified OK**. Contributor's 37-line local invalidation fix: **0 BAD / 763,665 OK, 263,727 exchange invalidations**. Median per-request decode 71.8 TG in both arms; whole-run 75.3 vs 74.7 is noise. **Not merged.** Default Foresight off unaffected.

P51: keep `STRATA_FS_SLOTS=0`; no Foresight speed credit until read-after-write ownership canary and identity checks pass sampled, long-context, batch and adversarial swap tests. General Relay ownership lesson: invalidate/in-flight fence correctly across expert-state relocation. Silent numerical contamination is more dangerous than an obvious crash.

## NEW: Strata ignores a llama.cpp client's reasoning budget (#2141 / PR #2140)
Issue created 2026-10-12 16:24:35 UTC; PR created 16:18:18 UTC (source provenance overlaps, despite PR number).
https://github.com/Niko1221/Strata/issues/2141
https://github.com/Niko1221/Strata/pull/2140

Pi `pi-llama-cpp` sends `thinking_budget_tokens` (medium=8192) while Strata reads only `reasoning_budget_tokens`. On 2x CMP 50HX + Flash IQ3_XXS, a 109,013-token automatic compaction generated 26,214 thinking tokens per retry and repeated five times (~250 seconds each; ~21 min), never producing a summary. Proposed alias fix reads either name with `reasoning_budget_tokens` taking precedence. No merged release yet.

P51: explicitly send recognized `reasoning_budget_tokens` or validate adapter mapping, assert the budget in e2e replies/logs, bound retries and cap compaction completion; compare Pi default compaction vs manual pi-vcc separately. This can dominate agent wall time despite high decode TG.

## NEW: same 64GB host capacity benchmark of Swift-1.5 IQ3_S, but **not long context** (#2133)
Created 2026-10-12 15:54:05 UTC.
https://github.com/Niko1221/Strata/issues/2133

RTX5090 32GiB VRAM + Threadripper9960X +63.4GiB installed RAM, Windows 11, Strata0.1.43, Swift1.5 IQ3_S native GGUF/MTP: median short-chat **185.6 TG**, fresh 16K **6639.4 PP**, agent followup **184.7 TG** with actual agent prompts only ~14.4K. **131,072-token configured window is not an actually filled 131K performance test**; thinking off, greedy, no coding correctness evaluation. Demonstrates artifact/host class admission, not 5070Ti transfer or deep xhigh quality.

RECOVERED EXISTING MODEL ARTIFACT (upload date NOT established in this research window): https://huggingface.co/tomngdev/Swift1.5-Qwen3.8-Flash-Next-GGUF has an independent **IQ3_S** GGUF of Swift1.5 with modified ISTA-DASLab-style recipe, MTP included Q4_K_M, embedding Q6_K, shared projections Q8_0 and disk PLE BF16. Don't equate its weights/layout to original ISTA-DASLab or proposed P51 xhigh mixed quant; source revision, files, license, tensor fingerprint and external PLE footprint must be confirmed before testing. This corrects the October 4 artifact watch's broader implication that no public Swift Flash IQ3_S existed, **but does not establish a fresh upload since 13:07 UTC**.

## NEW: Strata disk-parking alternative PR #2119
Created 2026-10-12 14:07:35 UTC.
https://github.com/Niko1221/Strata/pull/2119

Opt-in `--conversation-cache-storage disk`, native session snapshot per parked conversation, atomic write and LRU eviction. Compared with the more complete #2098 page-granular version-tagged disk tier; #2119 deliberately omits blob sharing, GC and version tag gating. RTX5090 Laptop 24GiB, IQ3_XXS 14.4K conversation, ~435MiB snapshot: park RAM 105ms versus disk 411ms; restore RAM 32ms versus disk **42.5ms page-cache hot**; disk park decreases engine RSS ~26MiB vs RAM park +308MiB; identical 14087/14188 reused tokens; decode RAM 30.3 versus disk 27.7 TG. After engine restart disk restore 152ms. Source author says alternating conversations on RAM-constrained box ~2–4 seconds versus full cold re-prefill. **Draft/unmerged**.

P51: architecture reference for bounded durable spill, but prefer version-tagged/validated #2098 path; require cold-cache, restart, disk exhaustion, concurrent evictions, crash atomicity and exact resumed state. No M1 numerical transfer.

## NEW: Strata QA / high-context community receipts
- #2138 created 2026-10-12 16:11:43 UTC: two independent RTX3090 replicas with batch2, 2×EPYC virtualization, same immutable v0.1.43, warm aggregate **153.60 TG overlap off vs 121.53 TG on** (~-20.9%), v0.1.42 155.67 control. Solo mode neutral. **Not a layer split**; confirms `STRATA_ADAPT_OVERLAP=0` test requirement for B2 as well as B1. https://github.com/Niko1221/Strata/issues/2138
- #2139 created 16:15:05 UTC: RTX3060 12GiB + i7-12700 +64GB, three original Flash quant types Q2_0, IQ2_XS, IQ3_XXS, Windows 0.1.43. Fresh inputs through **260,000** tokens; xhigh sampled MTP; 90/90 speed requests and 21/21 synthetic recall; one-hour IQ2_XS 128K soak. Expert placements/cache differ, uncontrolled OS cache, not quality/Swift/5070 comparative causal evidence. https://github.com/Niko1221/Strata/pull/2139
- #2117 created 13:52:41 UTC: RTX4080 16GiB +128GB, Flash IQ3_S, configured 262K but benchmark actual <=32K, 66.0 short TG / 1996.3 fresh 16K PP; supplemental personal ~225K agent-session observations must remain distinct from standardized suite and RAM is larger than ours. https://github.com/Niko1221/Strata/issues/2117
- #2131 created 15:44:01 UTC: under `--prefill auto`, prompt cache loan can be too small for a short request's legacy ring on IQ3_XXS, causing engine exit. Proposed fix sizes for max selected/legacy chunk; L4 24GiB reproduction and 3/3 failure->0/3 for affected expert-cache sizes. Test small fresh prompts *after* long prompt initialization, and on varying expert-cache capacities. https://github.com/Niko1221/Strata/pull/2131
- #2135 created 16:03:00 UTC: benchmark utility warning for `--expert-profile-save` overwriting live routing profile; do NOT run quality/perf test suites with profile-save to production artifact. https://github.com/Niko1221/Strata/pull/2135

## UPDATE (MERGED during window): mlx-serve Flash GDN dtype correctness #815/#814
Git commit `9c511c4710` 2026-10-12 15:25:30 UTC; **underlying issue/PR created Oct 11 and numeric evidence is older, not a new Oct 12 measurement**.
https://github.com/ddalcu/mlx-serve/pull/815
https://github.com/ddalcu/mlx-serve/issues/814

`qwen4_exp` GDN recurrent state and decay factor had bf16 instead of declared FP32; 206/1728 heads rounded decay to g=1, effectively failing to forget. Reported M5 Max 128GB over a 16,384-token chat, teacher-forced perplexity decode **56.95 bf16 -> 39.76 f32**, chunked prefill **48.16 -> 42.35**; fp32 state/decay introduces higher memory and checkpoint dtype change, SSD namespace split. This demonstrates a general *state-precision* correctness gate, **not evidence existing oMLX/P51 P58 patch has this bug**. Verify oMLX/M1 state and decay dtype against model/reference, and native short/long recurrence correctness before accepting cross-backend state transfers or quantized islands.

## NEW: oMLX Apple Silicon PLE and cluster research
- #4464 created 13:39:56 UTC: removes redundant extra mmap copy. Synthetic selected-row microtest 0.1164 -> 0.1059ms (8K rows), but **real M5 Max Flash-Next oQ5e end-to-end 8K cold PP 2036->1957, decode 99.9->100.0, TTFT 3.947->4.104s**; micro win is NOT a serving win. No M1 target change. https://github.com/jundot/omlx/pull/4464
- #4467 created 14:16:12 UTC, **rebase of old #3063** (older since September). Distributed prompt-cache slots tiered by per-rank headroom on two 48GB Thunderbolt Macs; 121 tests, old deployment reports zero incidents. Different Mac RAM, TP2 topology and old measurement; useful cache-pressure policy, not new PP2 throughput. https://github.com/jundot/omlx/pull/4467
- #4472 created 16:27:28 UTC: bounded SSD PLE prefetch workers; 2,048-page synthetic 16.0877 -> 11.6100 ms on M5 Max, no model TG proven. #4473 created 16:28:20 UTC: cached immutable shard layouts, 64-row synthetic planning 0.0426 -> 0.0101 ms, no E2E improvement. Both open. Avoid mistaking synthetic lookup micro gains for dual-M1 B1/B4 rates. https://github.com/jundot/omlx/pull/4472 https://github.com/jundot/omlx/pull/4473
- #4470 created 16:04 UTC: optional Decision 3.0 auxiliary decision-model serving. No effect on Flash verifier; M3 Ultra 3 text questions 0.35s is unrelated. https://github.com/jundot/omlx/pull/4470

## NEW: vLLM QSA context-parallelism capacity/throughput tradeoff
#61242 created 2026-10-12 16:13:26 UTC, draft.
https://github.com/vllm-project/vllm/pull/61242

8×A100 40GiB, Flash FP8, TP8/EP, DCP=4 splits two KV heads' tokens across GPUs instead of 4x replication: **GPU KV capacity 2.18M -> 7.70M tokens** (3.53x FP8), but 3x60min MLPerf agentic 20-session run **aggregate TG 915->805**, TPOT p50 13.2->16.4–16.8ms; strict SLO goodput ~2.0->1.52–1.69 req/s. A100 kernel merge fallback + 4 collectives per QSA layer. Useful capacity-only research, *not* dual M1 TB4 PP2 speed evidence. Preserve topology-by-execution-mode rule.

## NEW: distributed checkpoint safety
- vLLM #61229 issue created 14:42:21 UTC: NIXL producer expires KV lease during stalled consumer READ; reused physical pages silently poison decode. Controlled Qwen2.5-0.5B test **5/5 wrong request outputs** at both 30-second and 1-second lease settings. Must tie remote block ownership to in-flight consumers, transfer completion and content epoch, and never reclaim until safe. https://github.com/vllm-project/vllm/issues/61229
- vLLM #61238 PR created 15:50 UTC: marks stalled-read engine invalid after ~480s timeout; test later requests fail fast rather than pin blocks. Simulated blocks pinned **470->55** and followup hangs **5->1**. The first in-flight request remains pinned until it finishes; no premature free. This does not itself solve #61229's producer expiry. https://github.com/vllm-project/vllm/pull/61238
- vLLM #61248 created 16:36 UTC: drain asynchronous HF3FS save writers and validate complete writes before release/confirm; CPU 22 focused tests passed. Matches Relay's durable-write-before-reclamation requirement. https://github.com/vllm-project/vllm/pull/61248
- SGLang #43868 created 16:03 UTC: HiCache block-group page hits, caller-owned destination pages, and allocation-target FULL eviction policy. Supports explicit owner/layout metadata; no exact-target measurement. https://github.com/sgl-project/sglang/pull/43868
- SGLang commit #40896 merged by 16:03 UTC: fail a request whose external linker load fails rather than crash global scheduler. https://github.com/sgl-project/sglang/commit/f92199b569

## NEW: llama.cpp image+MTP interface
PR #30397 created 15:19:10 UTC: Qwen3.8-Flash-Next image embeddings pass to MTP. Contributor's image/text/image-repeat HTTP smoke no longer fails after patch; **open**, limited correctness suite and no quality/speed improvement claimed. https://github.com/ggml-org/llama.cpp/pull/30397

## Checked, no target movement / boundary exclusions
- antirez/ds4 latest direct commit Oct 7; no fresh Oct 12 PR/issue in query. This is a negative current-window check, not a new performance conclusion.
- Adaptive KV Streaming V2 and pi-vcc have no new created PRs/issues or default-branch commits later than previous checkpoint. Previous Oct 12 audit stands.
- SGLang #43820 proposed exact-affine GDN CP but was created at 09:41 UTC *before* our 13:07 boundary; do not label new here. Similarly oMLX #4460/#4461/#4456 predates the boundary; ignore crawl/update time.
- Exact user's 2×M1 Max/TB4 PP2 decode and 5070Ti/Core Ultra7/64GB Swift IQ3_S 128K–262K xhigh performance still unmeasured. No confirmed official Qwen successor model refresh established.

## New qualification actions (no benchmark/target promotion)
1. Strata Foresight opt-out until expert-slot identity is proved; same-build overlap A/B for B1/B2; guard benchmark profile files.
2. Pi/Strata request compatibility matrix including `thinking_budget_tokens` and `reasoning_budget_tokens`, maximum output and failure/retry boundaries.
3. Typed recurrent/GDN state and decay-gate numerical parity with model declaration, PP/chunk/verify/restore/rewind and 16K+ accumulative drift; fail cross-backend import when precision differs.
4. Remote state epochs/lease references: producer cannot reclaim blocks until all readers finish or are conclusively revoked; image/schema digest, committed frontier and writer drain before publish/reuse.
5. Long-context performance ledger preserves actual prompts and supported hardware/quant, never configured length. Experimental cache/PLE micro speed is not production TG/PP.
6. Research priorities remain Project 51 PP2/cross-runtime state correctness, single-Mac quality-grounded Swift dense 27B service, and 5070Ti Flash Swift IQ3_S fit/quality.

**New strict hard boundary: 2026-10-12 16:49:11 UTC.**
